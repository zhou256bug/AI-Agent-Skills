#!/usr/bin/env python3
"""阿里企业邮箱 IMAP 读信 CLI。"""

from __future__ import annotations

import argparse
import imaplib
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mail_lib import (  # noqa: E402
    MailConfigError,
    MailConnectionError,
    bootstrap_env,
    connect,
    dump_json,
    fetch_messages,
    get_setup_status,
    list_folders,
    run_doctor,
    run_setup_apply,
    search_uids,
    select_folder,
)


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"日期格式应为 YYYY-MM-DD，收到: {value!r}"
        ) from exc


def add_env_file_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--env-file",
        help="凭据文件路径（KEY=VALUE）；不覆盖进程已有非空环境变量",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="通过 IMAP 读取阿里企业邮箱邮件。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
凭据加载优先级（高 → 低，且不覆盖已有非空环境变量）:
  1. 进程环境变量（Agent / CI / Secrets 注入）
  2. --env-file
  3. ALIYUN_MAIL_ENV_FILE
  4. ./.aliyun-mail.env
  5. <skill>/local/credentials.env
  6. ~/.config/aliyun-enterprise-mail/credentials.env
  7. ~/.aliyun-mail.env

环境变量:
  ALIYUN_MAIL_USER          完整邮箱地址（必填）
  ALIYUN_MAIL_PASSWORD      登录密码或客户端授权密码（必填）
  ALIYUN_MAIL_IMAP_HOST     IMAP 主机（默认 imap.qiye.aliyun.com）
  ALIYUN_MAIL_IMAP_PORT     IMAP 端口（默认 993）
  ALIYUN_MAIL_ENV_FILE      指向凭据文件

示例:
  python read_mail.py setup status
  python read_mail.py setup apply --user you@co.com --password *** --verify
  python read_mail.py doctor
  python read_mail.py list --folder INBOX --limit 10
        """.strip(),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="检查凭据与 IMAP 连通性")
    add_env_file_arg(doctor_parser)

    folders_parser = sub.add_parser("folders", help="列出邮箱文件夹")
    add_env_file_arg(folders_parser)

    list_parser = sub.add_parser("list", help="列出邮件摘要")
    add_env_file_arg(list_parser)
    list_parser.add_argument("--folder", default="INBOX", help="文件夹名称（默认 INBOX）")
    list_parser.add_argument("--limit", type=int, default=20, help="最多返回条数（默认 20）")
    list_parser.add_argument("--unread-only", action="store_true", help="仅未读")
    list_parser.add_argument("--since", type=parse_date, help="起始日期 YYYY-MM-DD（含）")
    list_parser.add_argument("--before", type=parse_date, help="截止日期 YYYY-MM-DD（不含）")
    list_parser.add_argument(
        "--subject-contains",
        help="主题包含关键字（IMAP SUBJECT 搜索）",
    )
    list_parser.add_argument(
        "--from-contains",
        help="发件人包含关键字（IMAP FROM 搜索）",
    )

    read_parser = sub.add_parser("read", help="读取单封邮件详情（含正文）")
    add_env_file_arg(read_parser)
    read_parser.add_argument("--folder", default="INBOX", help="文件夹名称")
    read_parser.add_argument("--uid", required=True, help="邮件 UID")

    search_parser = sub.add_parser("search", help="按 IMAP 条件搜索并返回摘要")
    add_env_file_arg(search_parser)
    search_parser.add_argument("--folder", default="INBOX", help="文件夹名称")
    search_parser.add_argument("--limit", type=int, default=50, help="最多返回条数")
    search_parser.add_argument("--unread-only", action="store_true")
    search_parser.add_argument("--since", type=parse_date)
    search_parser.add_argument("--before", type=parse_date)
    search_parser.add_argument("--subject-contains")
    search_parser.add_argument("--from-contains")
    search_parser.add_argument(
        "--criteria",
        help='自定义 IMAP 搜索条件，例如 UNSEEN SUBJECT "发票"',
    )

    setup_parser = sub.add_parser(
        "setup",
        help="Agent 引导式凭据配置（status 查看 / apply 写入）",
    )
    setup_sub = setup_parser.add_subparsers(dest="setup_command", required=True)

    setup_sub.add_parser(
        "status",
        help="输出需向用户收集的字段与推荐写入路径（Agent 首选）",
    )

    apply_parser = setup_sub.add_parser(
        "apply",
        help="写入凭据文件（由 Agent 在用户对话中收集参数后调用）",
    )
    apply_parser.add_argument("--user", required=True, help="完整邮箱地址")
    apply_parser.add_argument("--password", required=True, help="客户端授权密码")
    apply_parser.add_argument("--host", help=f"IMAP 主机（默认 imap.qiye.aliyun.com）")
    apply_parser.add_argument("--port", help="IMAP 端口（默认 993）")
    apply_parser.add_argument(
        "--target",
        default="auto",
        choices=["auto", "skill", "repo", "user", "path"],
        help="凭据落盘位置：auto/skill/repo/user/path",
    )
    apply_parser.add_argument(
        "--path",
        help="target=path 时的显式文件路径",
    )
    apply_parser.add_argument(
        "--verify",
        action="store_true",
        help="写入后立即运行 doctor 验证",
    )

    return parser


def prepare_env(args: argparse.Namespace) -> None:
    bootstrap_env(explicit_env_file=getattr(args, "env_file", None))


def newest_first(uids: list[str], limit: int) -> list[str]:
    if limit <= 0:
        return []
    return list(reversed(uids))[:limit]


def cmd_folders() -> dict:
    mail = connect()
    try:
        folders = list_folders(mail)
        return {"folders": folders}
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def cmd_list(args: argparse.Namespace) -> dict:
    mail = connect()
    try:
        folder_info = select_folder(mail, args.folder)
        uids = search_uids(
            mail,
            unread_only=args.unread_only,
            since=args.since,
            before=args.before,
            subject_contains=args.subject_contains,
            from_contains=args.from_contains,
        )
        selected = newest_first(uids, args.limit)
        messages = fetch_messages(mail, selected, include_body=False)
        return {
            "folder": folder_info,
            "query": {
                "unreadOnly": args.unread_only,
                "since": args.since.strftime("%Y-%m-%d") if args.since else None,
                "before": args.before.strftime("%Y-%m-%d") if args.before else None,
                "subjectContains": args.subject_contains,
                "fromContains": args.from_contains,
            },
            "totalMatched": len(uids),
            "returned": len(messages),
            "messages": messages,
        }
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def cmd_read(args: argparse.Namespace) -> dict:
    mail = connect()
    try:
        folder_info = select_folder(mail, args.folder)
        messages = fetch_messages(mail, [args.uid], include_body=True)
        if not messages:
            raise MailConnectionError(f"未找到 UID={args.uid} 的邮件。")
        return {"folder": folder_info, "message": messages[0]}
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def cmd_search(args: argparse.Namespace) -> dict:
    mail = connect()
    try:
        folder_info = select_folder(mail, args.folder)
        uids = search_uids(
            mail,
            unread_only=args.unread_only,
            since=args.since,
            before=args.before,
            subject_contains=args.subject_contains,
            from_contains=args.from_contains,
            custom_criteria=args.criteria,
        )
        selected = newest_first(uids, args.limit)
        messages = fetch_messages(mail, selected, include_body=False)
        return {
            "folder": folder_info,
            "totalMatched": len(uids),
            "returned": len(messages),
            "messages": messages,
        }
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "doctor":
        result = run_doctor(explicit_env_file=args.env_file)
        print(dump_json(result))
        if result["status"] == "ok":
            return 0
        if result["status"] == "config_error":
            return 2
        return 1

    if args.command == "setup":
        try:
            if args.setup_command == "status":
                result = get_setup_status()
            elif args.setup_command == "apply":
                result = run_setup_apply(
                    user=args.user,
                    password=args.password,
                    host=args.host,
                    port=args.port,
                    target=args.target,
                    explicit_path=args.path,
                    verify=args.verify,
                )
            else:
                parser.error(f"未知 setup 子命令: {args.setup_command}")
                return 2
            print(dump_json(result))
            if args.setup_command == "status":
                return 0
            if result.get("status") == "verified":
                return 0
            if result.get("status") == "verify_failed":
                return 1
            return 0
        except MailConfigError as exc:
            print(f"配置错误: {exc}", file=sys.stderr)
            return 2

    prepare_env(args)
    try:
        if args.command == "folders":
            result = cmd_folders()
        elif args.command == "list":
            result = cmd_list(args)
        elif args.command == "read":
            result = cmd_read(args)
        elif args.command == "search":
            result = cmd_search(args)
        else:
            parser.error(f"未知命令: {args.command}")
            return 2
        print(dump_json(result))
        return 0
    except MailConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        print(
            "提示: 运行 python read_mail.py setup status 进入引导配置；"
            "详见 references/onboarding-flow.md",
            file=sys.stderr,
        )
        return 2
    except MailConnectionError as exc:
        print(f"连接错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
