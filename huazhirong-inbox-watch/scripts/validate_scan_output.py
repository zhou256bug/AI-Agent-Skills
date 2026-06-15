#!/usr/bin/env python3
"""校验扫描摘要 Markdown 是否含关键 emoji 标记。"""

from __future__ import annotations

import argparse
import re
import sys


REQUIRED_MARKERS = ("📌", "👉")
EMPTY_PHRASE = "没有新邮件"


def validate(text: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if "📌" not in text and EMPTY_PHRASE not in text:
        errors.append("缺少 📌 结论或无邮件固定话术")
    if "👉" not in text and EMPTY_PHRASE not in text:
        errors.append("缺少 👉 下一步")
    if EMPTY_PHRASE in text:
        return len(errors) == 0, errors
    if "🔴" not in text and "🟡" not in text and "📧" not in text:
        errors.append("有邮件时应含 🔴/🟡/📧 分级标记")
    return len(errors) == 0, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=argparse.FileType("r", encoding="utf-8"))
    ap.add_argument("--sample", choices=["empty", "has_mail"], help="内置样例")
    args = ap.parse_args()

    if args.sample == "empty":
        text = "## 📌 结论\n\n没有新邮件。\n\n👉 下次继续。\n"
    elif args.sample == "has_mail":
        text = "## 📌 结论\n\n未读 1 封。\n\n## 🔴 真人未读\n\n- ⭐ **A** <a@b.com>\n\n## 👉 下一步\n\n- 读全文\n"
    elif args.file:
        text = args.file.read()
    else:
        print("请提供 --file 或 --sample", file=sys.stderr)
        return 2

    ok, errors = validate(text)
    if ok:
        print("OK")
        return 0
    for err in errors:
        print(f"FAIL: {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
