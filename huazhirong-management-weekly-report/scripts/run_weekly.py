#!/usr/bin/env python3
"""周报编排器：一次触发跑全程，失败可断点续跑（纯标准库 + 子进程调渲染器）。

阶段（按期号 N 幂等，断点依据见 state.py）：
  fetch    取信下载 xlsx           （自动）
  compose  据 xlsx 写四段 Markdown （**Agent 任务**：编排器输出 NEED_COMPOSE 让 Agent 写）
  render   校验 MD → 渲染手机 PDF   （自动，PDF 为可选依赖）
  deliver  投递（默认 wechat-bridge，读 200/500 回执）（自动）

每次触发：已完成阶段（产物在）跳过，失败即停，留待下次续跑。终态打印 `STATE:<X>`。

状态 → 退出码：
  DELIVERED / ALREADY_DONE → 0
  FETCH_WAIT / DELIVER_RETRY / NEED_COMPOSE → 3（非致命，下次/Agent 续）
  FAIL_NOTIFY → 2（需通知：凭据错/取信连接异常/渲染失败/投递配置错）

用法：
  python3 scripts/run_weekly.py [--period N] [--channel wechat-bridge] [--force-stage deliver] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import weekly_report_config as cfg  # noqa: E402
import state as st_mod  # noqa: E402
import fetch_mail  # noqa: E402
import deliver as deliver_mod  # noqa: E402


def _emit(state_name: str, **detail) -> int:
    print(f"STATE:{state_name}")
    if detail:
        print(json.dumps(detail, ensure_ascii=False))
    return {"DELIVERED": 0, "ALREADY_DONE": 0,
            "FETCH_WAIT": 3, "DELIVER_RETRY": 3, "NEED_COMPOSE": 3,
            "FAIL_NOTIFY": 2}.get(state_name, 1)


def _highest_in_progress() -> int | None:
    """状态目录里仍未 done 的最大期号（用于无 --period 时续跑）。"""
    sd = cfg.archive_dir() / ".state"
    if not sd.is_dir():
        return None
    periods = []
    for f in sd.glob("W*.json"):
        try:
            n = int(f.stem[1:])
        except ValueError:
            continue
        if st_mod.decide_next(n) != "done":
            periods.append(n)
    return max(periods) if periods else None


def _default_render(period: int) -> tuple[bool, str]:
    md = st_mod.md_path(period)
    if md is None:
        return False, "MD 缺失"
    # 校验
    import importlib.util
    spec = importlib.util.spec_from_file_location("wr_validate", SCRIPTS / "validate_weekly_report_md.py")
    val = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(val)
    issues = val.validate(md.read_text(encoding="utf-8"))
    if issues:
        return False, f"校验未过：{issues[:2]}"
    # 渲染
    pdf = md.with_suffix(".pdf")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "render_mobile_pdf.py"), "--preset", "weekly-report",
         "--title", f"{cfg.SUBJECT_KEY} · 第{period}期", "--body-md", str(md), "--output", str(pdf)],
        capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0 or not pdf.is_file():
        return False, f"渲染失败：{r.stderr[:160]}"
    return True, str(pdf)


def run(period: int | None = None, *, channel: str = "wechat-bridge", force_stage: str | None = None,
        dry_run: bool = False, fetcher=None, renderer=None, deliverer=None) -> int:
    fetcher = fetcher or fetch_mail.find_and_download
    renderer = renderer or _default_render
    deliverer = deliverer or deliver_mod.deliver

    # ── 解析期号（含取信发现） ──
    pending_fetch = None
    if period is None:
        period = _highest_in_progress()
    if period is None:
        pending_fetch = fetcher(None)
        if pending_fetch.get("status") != "ok":
            s = pending_fetch.get("status")
            if s in ("not_found", "no_xlsx"):
                return _emit("FETCH_WAIT", **pending_fetch)
            return _emit("FAIL_NOTIFY", **pending_fetch)
        period = pending_fetch["period"]

    st = st_mod.load_state(period)

    # ── 强制某阶段（如限流后只补推送） ──
    if force_stage:
        st_mod.mark(st, force_stage, "pending")
        st_mod.save_state(period, st)

    title = f"{cfg.SUBJECT_KEY} · 第{period}期"

    # ── 驱动阶段 ──
    guard = 0
    while True:
        guard += 1
        if guard > 8:
            return _emit("FAIL_NOTIFY", period=period, detail="状态机异常循环")
        nxt = st_mod.decide_next(period, st)

        if nxt == "done":
            return _emit("ALREADY_DONE", period=period)

        if nxt == "fetch":
            res = pending_fetch or fetcher(period)
            pending_fetch = None
            if res.get("status") == "ok":
                st_mod.mark(st, "fetch", "done", xlsx=res.get("xlsx_path"))
                st_mod.save_state(period, st)
                continue
            st_mod.mark(st, "fetch", "failed", error=res.get("detail"))
            st_mod.save_state(period, st)
            if res.get("status") in ("not_found", "no_xlsx"):
                return _emit("FETCH_WAIT", period=period, **res)
            return _emit("FAIL_NOTIFY", period=period, **res)

        if nxt == "compose":
            # Agent 任务：据 xlsx 写四段 Markdown 到 <ARCHIVE_DIR>/W{N}-YYYY年MM月DD日.md
            return _emit("NEED_COMPOSE", period=period,
                         xlsx=str(st_mod.xlsx_path(period)),
                         hint="据 xlsx 写四段 Markdown（重点项目进展/海外市场要闻/业务线重点关注/需"
                              f"{cfg.OWNER}关注的事项），存为 W{period}-日期.md 后重跑")

        if nxt == "render":
            ok, detail = renderer(period)
            if ok:
                st_mod.mark(st, "render", "done", pdf=detail)
                st_mod.save_state(period, st)
                continue
            st_mod.mark(st, "render", "failed", error=detail)
            st_mod.save_state(period, st)
            return _emit("FAIL_NOTIFY", period=period, detail=detail)

        if nxt == "deliver":
            pdf = st_mod.pdf_path(period)
            res = deliverer(channel, pdf, title, "", dry_run)
            if res.get("ok"):
                st_mod.mark(st, "deliver", "done", channel=channel)
                st_mod.save_state(period, st)
                return _emit("DELIVERED", period=period, channel=channel)
            st_mod.mark(st, "deliver", "failed", error=res.get("detail"), channel=channel)
            st_mod.save_state(period, st)
            if res.get("retryable"):
                return _emit("DELIVER_RETRY", period=period, **res)
            return _emit("FAIL_NOTIFY", period=period, **res)


def main() -> int:
    ap = argparse.ArgumentParser(description="周报编排器（断点续跑）")
    ap.add_argument("--period", type=int, default=None)
    ap.add_argument("--channel", default="wechat-bridge", choices=sorted(deliver_mod.CHANNELS))
    ap.add_argument("--force-stage", default=None, choices=list(st_mod.STAGES))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(args.period, channel=args.channel, force_stage=args.force_stage, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
