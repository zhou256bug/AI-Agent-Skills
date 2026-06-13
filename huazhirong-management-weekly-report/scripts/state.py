#!/usr/bin/env python3
"""按期号 N 的断点续跑状态 + 产物探测（纯标准库）。

真值以"产物 + 状态文件"双重判定：
- fetch_done   ⇔ <ARCHIVE_DIR>/input/W{N}.xlsx 存在
- compose_done ⇔ <ARCHIVE_DIR>/W{N}-*.md 存在（Agent 据 xlsx 写出的四段 Markdown）
- render_done  ⇔ W{N}-*.pdf 存在 且 对应 md 通过 validator
- deliver_done ⇔ 状态文件 stages.deliver.status == "done"（投递无本地产物，靠回执记录）

状态文件：<ARCHIVE_DIR>/.state/W{N}.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_report_config as cfg  # noqa: E402

STAGES = ("fetch", "compose", "render", "deliver")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_dir() -> Path:
    d = cfg.archive_dir() / ".state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def state_path(period: int) -> Path:
    return state_dir() / f"W{period}.json"


def load_state(period: int) -> dict:
    p = state_path(period)
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"period": period, "stages": {s: {"status": "pending", "attempts": 0} for s in STAGES}}


def save_state(period: int, st: dict) -> None:
    st["updated_at"] = _now()
    state_path(period).write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def mark(st: dict, stage: str, status: str, **extra) -> dict:
    s = st["stages"].setdefault(stage, {"status": "pending", "attempts": 0})
    s["status"] = status
    s["ts"] = _now()
    if status in ("failed", "done"):
        s["attempts"] = s.get("attempts", 0) + (1 if status == "failed" else 0)
    s.update(extra)
    return st


# ── 产物探测 ──

def xlsx_path(period: int) -> Path:
    return cfg.archive_dir() / "input" / f"W{period}.xlsx"


def md_path(period: int) -> Path | None:
    matches = sorted(cfg.archive_dir().glob(f"W{period}-*.md"), reverse=True)
    return matches[0] if matches else None


def pdf_path(period: int) -> Path | None:
    matches = sorted(cfg.archive_dir().glob(f"W{period}-*.pdf"), reverse=True)
    return matches[0] if matches else None


def fetch_done(period: int) -> bool:
    return xlsx_path(period).is_file()


def compose_done(period: int) -> bool:
    return md_path(period) is not None


def render_done(period: int) -> bool:
    md, pdf = md_path(period), pdf_path(period)
    if not (md and pdf):
        return False
    # 用 validator 确认 md 合法（导入避免循环依赖问题，惰性）
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wr_validate", Path(__file__).resolve().parent / "validate_weekly_report_md.py"
    )
    val = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(val)
    return not val.validate(md.read_text(encoding="utf-8"))


def deliver_done(period: int, st: dict | None = None) -> bool:
    st = st or load_state(period)
    return st["stages"].get("deliver", {}).get("status") == "done"


def decide_next(period: int, st: dict | None = None) -> str:
    """返回下一个要执行的阶段，或终态 'done'。"""
    if not fetch_done(period):
        return "fetch"
    if not compose_done(period):
        return "compose"
    if not render_done(period):
        return "render"
    if not deliver_done(period, st):
        return "deliver"
    return "done"
