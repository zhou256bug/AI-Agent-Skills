#!/usr/bin/env python3
"""生成 emoji 扫描摘要 Markdown、归档、可选推送微信。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import inbox_watch_config as cfg  # noqa: E402
from deliver_weixin import post_send  # noqa: E402
from imap_lib import ImapConfigError, ImapConnectionError, bootstrap_env, scan_unseen  # noqa: E402


def build_summary_markdown(result: dict) -> str:
    total = result["total_unseen"]
    personal = result["personal_unseen"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = [
        f"# 📬 收件箱扫描 · {now}",
        "",
        f"**{cfg.COMPANY}** · 汇报给 **{cfg.OWNER}**",
        "",
    ]
    if total == 0:
        lines.extend([
            "## 📌 结论",
            "",
            "没有新邮件。",
            "",
            "👉 下次 cron 继续扫描。",
        ])
        return "\n".join(lines) + "\n"

    lines.extend([
        "## 📌 结论",
        "",
        f"未读 **{total}** 封，过滤系统邮件后真人邮件 **{personal}** 封。",
        "",
    ])

    personal_emails = [e for e in result["emails"] if not e["is_system"]]
    system_emails = [e for e in result["emails"] if e["is_system"]]

    if personal_emails:
        lines.append("## 🔴 真人未读（需关注）")
        lines.append("")
        for e in personal_emails:
            flag = "⭐" if e.get("is_known") else "📧"
            action = ""
            if wc := e.get("watch_contact"):
                action = f" · 策略：**{wc.get('action', '')}**"
            lines.append(f"- {flag} **{e['sender']}** · {e['date']}")
            lines.append(f"  - 主题：{e['subject']}{action}")
            if e.get("attachments"):
                lines.append(f"  - 📎 附件：{', '.join(e['attachments'])}")
            if e.get("body_preview"):
                preview = e["body_preview"].replace("\n", " ")[:200]
                lines.append(f"  - 预览：{preview}…")
        lines.append("")

    if system_emails:
        lines.append("## 🟡 系统/营销未读（已过滤统计）")
        lines.append("")
        lines.append(f"共 {len(system_emails)} 封，默认不展开。")
        lines.append("")

    lines.extend([
        "## 👉 下一步",
        "",
        "- 关注人邮件：用 `mail_tool.py read --uid <UID>` 读全文",
        "- 需附件：用 `mail_tool.py attachments_match --sender ...`",
        "- 无真人邮件时仍须告知「没有新邮件」（不可静默）",
        "",
    ])
    return "\n".join(lines) + "\n"


def build_weixin_text(result: dict) -> str:
    total = result["total_unseen"]
    personal = result["personal_unseen"]
    if total == 0:
        return f"📬 收件箱扫描\n\n没有新邮件。"
    lines = [f"📬 未读 {total} 封 · 真人 {personal} 封"]
    for e in result["emails"]:
        if e["is_system"]:
            continue
        star = "⭐" if e.get("is_known") else "•"
        lines.append(f"{star} {e['sender']}: {e['subject']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="扫描未读 → 摘要 → 归档 → 可选微信推送")
    ap.add_argument("--env-file")
    ap.add_argument("--folder", default="INBOX")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--deliver", action="store_true", help="推送微信（需 WEIXIN_TO）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-archive", action="store_true")
    args = ap.parse_args()

    bootstrap_env(explicit_env_file=args.env_file)
    try:
        result = scan_unseen(folder=args.folder, limit=args.limit)
    except (ImapConfigError, ImapConnectionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    md = build_summary_markdown(result)
    archive_path: Path | None = None
    if not args.no_archive:
        out_dir = cfg.scan_archive_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        archive_path = out_dir / f"{stamp}_inbox_scan.md"
        archive_path.write_text(md, encoding="utf-8")

    payload = {
        "total_unseen": result["total_unseen"],
        "personal_unseen": result["personal_unseen"],
        "archive_path": str(archive_path) if archive_path else None,
        "empty": result["total_unseen"] == 0,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("---MARKDOWN---")
    print(md, end="")

    if args.deliver:
        wx = post_send(build_weixin_text(result), media_path=archive_path, dry_run=args.dry_run)
        print("---DELIVER---")
        print(json.dumps(wx, ensure_ascii=False, indent=2))
        if not wx.get("ok"):
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
