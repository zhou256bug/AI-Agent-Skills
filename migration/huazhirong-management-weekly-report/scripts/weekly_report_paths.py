#!/usr/bin/env python3
"""Canonical paths and naming for management weekly reports.

Naming: W{期号}-YYYY年MM月DD日.pdf  (期号 = 邮件主题「周报（N）」)
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CN = timezone(timedelta(hours=8))
REPORT_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/newpos/笔记/周报"


def format_report_basename(period: int, dt: datetime | None = None) -> str:
    dt = (dt or datetime.now(TZ_CN)).astimezone(TZ_CN)
    return f"W{period}-{dt.year}年{dt.month:02d}月{dt.day:02d}日"


def report_paths(period: int, dt: datetime | None = None) -> dict[str, Path]:
    base = REPORT_DIR / format_report_basename(period, dt)
    return {"md": base.with_suffix(".md"), "pdf": base.with_suffix(".pdf")}


def parse_period_from_subject(subject: str) -> int | None:
    m = re.search(r"周报[（(](\d+)[)）]", subject)
    return int(m.group(1)) if m else None


def find_latest_pdf(period: int) -> Path | None:
    matches = sorted(REPORT_DIR.glob(f"W{period}-*.pdf"), reverse=True)
    return matches[0] if matches else None


def pdf_exists_for_period(period: int) -> bool:
    return find_latest_pdf(period) is not None
