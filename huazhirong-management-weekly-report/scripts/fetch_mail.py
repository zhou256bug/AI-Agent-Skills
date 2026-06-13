#!/usr/bin/env python3
"""取信（必备能力）：从收件箱抓取源周报邮件的 xlsx 附件。纯标准库（imaplib + email），通用 IMAP。

规则（见 references/email-and-xlsx.md）：
- 不用中文 SUBJECT SEARCH（会 UnicodeEncodeError）；用 `SINCE 日期` 拉回，再在 Python 侧过滤
  发件人含 SENDER_EMAIL、主题含 SUBJECT_KEY。
- 期号 N 取自主题括号；多封候选时优先"含 xlsx"且最新的一封。
- 下载 xlsx 到 <ARCHIVE_DIR>/input/W{N}.xlsx。

输出 JSON：{"status": ok|not_found|no_xlsx|no_creds|imap_error, "period": N, "xlsx_path": "...", "detail": "..."}
退出码：ok→0；not_found/no_xlsx→3（可重试）；no_creds/imap_error→2（需处理）。

用法：
    python3 scripts/fetch_mail.py [--period N] [--json]
"""

from __future__ import annotations

import argparse
import email
import imaplib
import json
import sys
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from email.message import Message
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_report_config as cfg  # noqa: E402
import weekly_report_paths as wp  # noqa: E402

TZ_CN = timezone(timedelta(hours=8))


# ───────── 纯函数（可单测） ─────────

def decode_mime(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", "replace"))
        else:
            out.append(text)
    return "".join(out)


def is_weekly_mail(from_addr: str, subject: str, sender_email: str, subject_key: str) -> bool:
    """发件人含 sender_email 且主题含 subject_key。"""
    return sender_email.lower() in (from_addr or "").lower() and subject_key in (subject or "")


def parse_week_num(subject: str) -> int | None:
    return wp.parse_period_from_subject(subject or "")


def extract_xlsx(msg: Message) -> tuple[str, bytes] | None:
    """递归 walk 找第一个 .xlsx 附件，返回 (文件名, 字节)。"""
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fname = decode_mime(part.get_filename())
        if fname and fname.lower().endswith(".xlsx"):
            payload = part.get_payload(decode=True)
            if payload:
                return fname, payload
    return None


def pick_best_candidate(cands: list[dict]) -> dict | None:
    """优先含 xlsx，其次按 date 最新。cands 元素含 has_xlsx(bool)、date(str ISO)、period(int)。"""
    if not cands:
        return None
    return sorted(
        cands,
        key=lambda c: (1 if c.get("has_xlsx") else 0, c.get("date") or ""),
        reverse=True,
    )[0]


# ───────── IMAP（真实网络，run_weekly 测试时被 mock 替换） ─────────

def _imap_search_since(host: str, port: int, user: str, password: str, since_days: int):
    """连接 IMAP/SSL，返回 (conn, [uid...]) ——SINCE 回溯过滤。调用方负责 logout。"""
    conn = imaplib.IMAP4_SSL(host, port)
    conn.login(user, password)
    conn.select("INBOX", readonly=True)
    since = (datetime.now(TZ_CN) - timedelta(days=since_days)).strftime("%d-%b-%Y")
    typ, data = conn.search(None, "SINCE", since)
    if typ != "OK":
        raise imaplib.IMAP4.error(f"search failed: {typ}")
    uids = data[0].split() if data and data[0] else []
    return conn, uids


def find_and_download(period: int | None = None, *, searcher=None) -> dict:
    """主流程。searcher 可注入（测试用）；默认用真实 IMAP。返回状态 dict。"""
    if not cfg.imap_ready():
        return {"status": "no_creds", "detail": "缺少 IMAP_HOST/USER/PASSWORD（见 local/credentials.env）"}

    try:
        if searcher is None:
            conn, uids = _imap_search_since(
                cfg.IMAP_HOST, cfg.IMAP_PORT, cfg.IMAP_USER, cfg.IMAP_PASSWORD, cfg.SINCE_DAYS
            )

            def _fetch_raw(uid: bytes) -> bytes:
                typ, d = conn.fetch(uid, "(RFC822)")
                return d[0][1] if typ == "OK" and d and d[0] else b""

            raws = [_fetch_raw(u) for u in uids]
            try:
                conn.close()
                conn.logout()
            except Exception:
                pass
        else:
            raws = searcher()  # 测试注入：返回 [raw_bytes,...]
    except (imaplib.IMAP4.error, OSError) as exc:
        return {"status": "imap_error", "detail": f"连接异常：{exc}"}

    # 过滤 + 收集候选
    cands: list[dict] = []
    for raw in raws:
        if not raw:
            continue
        msg = email.message_from_bytes(raw)
        frm = decode_mime(msg.get("From"))
        subj = decode_mime(msg.get("Subject"))
        if not is_weekly_mail(frm, subj, cfg.SENDER_EMAIL, cfg.SUBJECT_KEY):
            continue
        n = parse_week_num(subj)
        if n is None:
            continue
        if period is not None and n != period:
            continue
        xlsx = extract_xlsx(msg)
        cands.append({
            "period": n, "date": msg.get("Date") or "", "has_xlsx": xlsx is not None,
            "_xlsx": xlsx, "subject": subj,
        })

    if not cands:
        return {"status": "not_found", "detail": "未匹配到周报邮件", "period": period}

    best = pick_best_candidate(cands)
    if not best.get("has_xlsx"):
        return {"status": "no_xlsx", "detail": "匹配到邮件但无 xlsx 附件", "period": best["period"]}

    n = best["period"]
    fname, data = best["_xlsx"]
    dest_dir = cfg.archive_dir() / "input"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"W{n}.xlsx"
    dest.write_bytes(data)
    return {"status": "ok", "period": n, "xlsx_path": str(dest), "orig_name": fname}


def main() -> int:
    ap = argparse.ArgumentParser(description="取信：抓取源周报邮件 xlsx")
    ap.add_argument("--period", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = find_and_download(args.period)
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"[fetch] {res.get('status')} period={res.get('period')} {res.get('detail','')} {res.get('xlsx_path','')}")
    return {"ok": 0, "not_found": 3, "no_xlsx": 3, "no_creds": 2, "imap_error": 2}.get(res["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
