#!/usr/bin/env python3
"""关注人列表 CLI：list / add / remove（供 Agent 执行用户口述的增删）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from watchlist_lib import add_contact, list_contacts, remove_contact  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="关注人列表管理")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出全部关注人")

    add = sub.add_parser("add", help="新增关注人")
    add.add_argument("--name", required=True, help="显示名，如 程晓艳 (Charlene)")
    add.add_argument("--email", required=True, help="完整邮箱")
    add.add_argument("--role", default="关注联系人")
    add.add_argument(
        "--action",
        default="report_promptly",
        choices=["read_full", "read_attachments", "report_promptly"],
    )
    add.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    add.add_argument("--note", default="")
    add.add_argument("--id", help="可选自定义 id")

    rm = sub.add_parser("remove", help="删除关注人（id / 邮箱 / 姓名 任一匹配）")
    rm.add_argument("target", help="id、邮箱或姓名")

    args = ap.parse_args()
    try:
        if args.command == "list":
            print(json.dumps(list_contacts(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "add":
            entry = add_contact(
                name=args.name,
                email=args.email,
                role=args.role,
                action=args.action,
                priority=args.priority,
                note=args.note,
                contact_id=args.id,
            )
            print(json.dumps({"status": "added", "contact": entry}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "remove":
            removed = remove_contact(args.target)
            print(json.dumps({"status": "removed", "contact": removed}, ensure_ascii=False, indent=2))
            return 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
