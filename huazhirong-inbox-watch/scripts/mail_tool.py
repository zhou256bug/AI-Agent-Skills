#!/usr/bin/env python3
"""邮件工具 CLI：list / read / read_match / attachments_match。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from imap_lib import (  # noqa: E402
    ImapConfigError,
    ImapConnectionError,
    attachments_match,
    bootstrap_env,
    read_by_uid,
    read_match,
    scan_unseen,
    search_all_uids,
    connect,
    select_inbox,
    summarize_email,
    fetch_raw,
)


def cmd_list(args: argparse.Namespace) -> int:
    mail = connect()
    try:
        select_inbox(mail, args.folder)
        uids = search_all_uids(mail, limit=args.limit)
        items = []
        for uid in reversed(uids):
            raw = fetch_raw(mail, uid, peek_body=False)
            msg_summary = summarize_email(uid, raw, preview_chars=200)
            items.append({k: v for k, v in msg_summary.items() if k != "body_full"})
        print(json.dumps(items, ensure_ascii=False, indent=2))
    finally:
        try:
            mail.logout()
        except Exception:
            pass
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    detail = read_by_uid(args.uid, folder=args.folder)
    print(json.dumps(detail, ensure_ascii=False, indent=2))
    return 0


def cmd_read_match(args: argparse.Namespace) -> int:
    matched = read_match(
        sender_contains=args.sender,
        subject_contains=args.subject,
        folder=args.folder,
        limit=args.limit,
        unseen_only=args.unseen_only,
    )
    print(json.dumps(matched, ensure_ascii=False, indent=2))
    return 0


def cmd_attachments_match(args: argparse.Namespace) -> int:
    dest = Path(args.dest).expanduser() if args.dest else None
    results = attachments_match(
        sender_contains=args.sender,
        subject_contains=args.subject,
        folder=args.folder,
        limit=args.limit,
        dest_dir=dest,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def cmd_unseen(args: argparse.Namespace) -> int:
    result = scan_unseen(folder=args.folder, limit=args.limit)
    if args.format == "text":
        print(result["text"], end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="通用 IMAP 邮件工具")
    ap.add_argument("--env-file")
    sub = ap.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="列出最近邮件摘要")
    p_list.add_argument("--folder", default="INBOX")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_read = sub.add_parser("read", help="按 UID 读全文")
    p_read.add_argument("--uid", required=True)
    p_read.add_argument("--folder", default="INBOX")
    p_read.set_defaults(func=cmd_read)

    p_rm = sub.add_parser("read_match", help="遍历后 Python 过滤匹配")
    p_rm.add_argument("--sender")
    p_rm.add_argument("--subject")
    p_rm.add_argument("--folder", default="INBOX")
    p_rm.add_argument("--limit", type=int, default=20)
    p_rm.add_argument("--unseen-only", action="store_true")
    p_rm.set_defaults(func=cmd_read_match)

    p_am = sub.add_parser("attachments_match", help="匹配并下载附件")
    p_am.add_argument("--sender")
    p_am.add_argument("--subject")
    p_am.add_argument("--folder", default="INBOX")
    p_am.add_argument("--limit", type=int, default=10)
    p_am.add_argument("--dest")
    p_am.set_defaults(func=cmd_attachments_match)

    p_unseen = sub.add_parser("unseen", help="扫描 UNSEEN（同 check_unseen.py）")
    p_unseen.add_argument("--folder", default="INBOX")
    p_unseen.add_argument("--limit", type=int)
    p_unseen.add_argument("--format", choices=["text", "json"], default="text")
    p_unseen.set_defaults(func=cmd_unseen)

    args = ap.parse_args()
    bootstrap_env(explicit_env_file=args.env_file)
    try:
        return args.func(args)
    except ImapConfigError as exc:
        print(f"CONFIG_ERROR: {exc}", file=sys.stderr)
        return 2
    except ImapConnectionError as exc:
        print(f"IMAP_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
