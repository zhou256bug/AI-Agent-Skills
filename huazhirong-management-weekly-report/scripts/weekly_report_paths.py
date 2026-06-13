#!/usr/bin/env python3
"""Canonical paths and naming for management weekly reports.

Naming: W{期号}-YYYY年MM月DD日.pdf  (期号 = 邮件主题「周报（N）」)
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 确保同目录的 weekly_report_config 可被导入（脚本/被 import 两种方式都成立）
sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_report_config as cfg  # noqa: E402

TZ_CN = timezone(timedelta(hours=8))


def report_dir() -> Path:
    """归档目录（可配置，默认技能本地 output/）。"""
    return cfg.archive_dir()


def format_report_basename(period: int, dt: datetime | None = None) -> str:
    dt = (dt or datetime.now(TZ_CN)).astimezone(TZ_CN)
    return f"W{period}-{dt.year}年{dt.month:02d}月{dt.day:02d}日"


def report_paths(period: int, dt: datetime | None = None) -> dict[str, Path]:
    base = report_dir() / format_report_basename(period, dt)
    return {"md": base.with_suffix(".md"), "pdf": base.with_suffix(".pdf")}


def parse_period_from_subject(subject: str) -> int | None:
    m = re.search(r"周报[（(](\d+)[)）]", subject)
    return int(m.group(1)) if m else None


def find_latest_pdf(period: int) -> Path | None:
    d = report_dir()
    if not d.exists():
        return None
    matches = sorted(d.glob(f"W{period}-*.pdf"), reverse=True)
    return matches[0] if matches else None


def pdf_exists_for_period(period: int) -> bool:
    return find_latest_pdf(period) is not None
