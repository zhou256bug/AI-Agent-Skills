#!/usr/bin/env python3
"""Validate management weekly-report Markdown (四段结构、署名、禁止段)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_H2 = [
    "一、重点项目进展",
    "二、海外市场要闻",
    "三、业务线重点关注",
    "四、需菜头关注的事项",
]

FORBIDDEN_LITERAL = [
    "菜头周报原文",
    "一、菜头（蔡伟旭）本周重点",
]

FORBIDDEN_RE = re.compile(r"菜头.{0,8}原文|第\d+周（", re.MULTILINE)

META_FIELDS = ("第", "汇总日期", "来源")  # 第N期

ATTRIBUTION_RE = re.compile(r"\*\*[^*]+\*\*\s*$")


def _section_slice(text: str, start_h2: str, end_h2: str | None) -> str:
    start = text.find(f"## {start_h2}")
    if start < 0:
        return ""
    if end_h2:
        end = text.find(f"## {end_h2}", start + 1)
        return text[start:end] if end >= 0 else text[start:]
    return text[start:]


def validate(text: str) -> list[dict]:
    issues: list[dict] = []

    for bad in FORBIDDEN_LITERAL:
        if bad in text:
            issues.append({"code": "FORBIDDEN_SECTION", "detail": bad})

    if FORBIDDEN_RE.search(text):
        issues.append({"code": "FORBIDDEN_SECTION", "detail": "禁止段或ISO周表述"})

    for h2 in REQUIRED_H2:
        if h2 not in text:
            issues.append({"code": "MISSING_H2", "detail": h2})

    positions = [text.find(f"## {h}") for h in REQUIRED_H2 if f"## {h}" in text]
    if len(positions) == len(REQUIRED_H2) and positions != sorted(positions):
        issues.append({"code": "SECTION_ORDER", "detail": "四段标题顺序错误"})

    if ":::meta" not in text:
        issues.append({"code": "MISSING_META", "detail": ":::meta"})
    else:
        meta_text = text.split(":::", 2)[1] if len(text.split(":::")) > 1 else ""
        for field in META_FIELDS:
            if field not in meta_text:
                issues.append({"code": "MISSING_META_FIELD", "detail": field})

    if ":::urgent" not in text:
        issues.append({"code": "MISSING_URGENT", "detail": ":::urgent"})

    sec1 = _section_slice(text, REQUIRED_H2[0], REQUIRED_H2[1])
    if sec1 and "| --- |" not in sec1 and "|---|" not in sec1.replace(" ", ""):
        issues.append({"code": "MISSING_TABLE", "detail": "section 1 projects"})

    if "周报来源" not in sec1:
        issues.append({"code": "MISSING_PROJECT_SOURCE", "detail": "section 1 缺周报来源"})

    urgent_m = re.search(r":::urgent\n(.*?):::", text, re.DOTALL)
    if urgent_m:
        numbered = [
            ln for ln in urgent_m.group(1).splitlines() if re.match(r"^\d+\.\s", ln.strip())
        ]
        if numbered and not (6 <= len(numbered) <= 10):
            issues.append(
                {"code": "URGENT_ITEM_COUNT", "detail": f"expected 6-10, got {len(numbered)}"}
            )

    in_sec = None
    for line in text.splitlines():
        if line.startswith("## 一、"):
            in_sec = 1
        elif line.startswith("## 二、"):
            in_sec = 2
        elif line.startswith("## 三、"):
            in_sec = 3
        elif line.startswith("## 四、"):
            in_sec = 4
        if in_sec in (2, 3) and line.startswith("- "):
            if not ATTRIBUTION_RE.search(line) and "**" not in line[-24:]:
                issues.append(
                    {"code": "MISSING_ATTRIBUTION", "detail": line[:60], "section": in_sec}
                )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("md_path", type=Path)
    args = parser.parse_args()
    text = args.md_path.read_text(encoding="utf-8")
    issues = validate(text)
    for i in issues:
        print(json.dumps(i, ensure_ascii=False))
    if issues:
        return 1
    print(json.dumps({"status": "ok"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
