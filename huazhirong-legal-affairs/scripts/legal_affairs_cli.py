#!/usr/bin/env python3
"""华智融法务技能 CLI：setup status/apply、doctor。

用法：
    python3 scripts/legal_affairs_cli.py setup status
    python3 scripts/legal_affairs_cli.py setup apply --decision-maker 老板 --company 华智融 --verify
    python3 scripts/legal_affairs_cli.py doctor
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from legal_affairs_lib import (  # noqa: E402
    LegalAffairsConfigError,
    bootstrap_env,
    dumps_json,
    get_setup_status,
    run_doctor,
    run_setup_apply,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="华智融法务技能 CLI")
    parser.add_argument("--env-file", help="显式指定 local/credentials.env 路径")
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="引导式配置")
    setup_sub = setup.add_subparsers(dest="setup_command", required=True)
    setup_sub.add_parser("status", help="查看配置状态与待收集字段")

    apply = setup_sub.add_parser("apply", help="写入本地配置")
    apply.add_argument("--decision-maker", dest="decision_maker")
    apply.add_argument("--company")
    apply.add_argument("--archive-dir", dest="archive_dir")
    apply.add_argument("--entity-cn", dest="entity_cn")
    apply.add_argument("--entity-hk", dest="entity_hk")
    apply.add_argument(
        "--target",
        default="auto",
        choices=["auto", "skill", "repo", "path"],
    )
    apply.add_argument("--path", help="target=path 时的文件路径")
    apply.add_argument("--verify", action="store_true", help="写入后运行 doctor")

    sub.add_parser("doctor", help="验证配置与目录可写、必需文件齐全")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.env_file:
        bootstrap_env(args.env_file)

    try:
        if args.command == "setup":
            if args.setup_command == "status":
                print(dumps_json(get_setup_status()))
                return 0
            if args.setup_command == "apply":
                values = {
                    "LEGAL_AFFAIRS_DECISION_MAKER": args.decision_maker or "",
                    "LEGAL_AFFAIRS_COMPANY": args.company or "",
                    "LEGAL_AFFAIRS_ARCHIVE_DIR": args.archive_dir or "",
                    "LEGAL_AFFAIRS_ENTITY_CN": args.entity_cn or "",
                    "LEGAL_AFFAIRS_ENTITY_HK": args.entity_hk or "",
                }
                result = run_setup_apply(
                    target=args.target,
                    explicit_path=args.path,
                    values=values,
                    verify=args.verify,
                )
                print(dumps_json(result))
                if args.verify and not result.get("doctor", {}).get("ok"):
                    return 1
                return 0
            parser.error(f"未知 setup 子命令: {args.setup_command}")

        if args.command == "doctor":
            result = run_doctor()
            print(dumps_json(result))
            return 0 if result.get("ok") else 1

        parser.error(f"未知命令: {args.command}")
    except LegalAffairsConfigError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
