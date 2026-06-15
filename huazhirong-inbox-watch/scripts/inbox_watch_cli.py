#!/usr/bin/env python3
"""收件箱值守 CLI：setup status/apply、doctor、scan。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import inbox_watch_config as cfg  # noqa: E402
from imap_lib import ImapConfigError, bootstrap_env, connect, select_inbox  # noqa: E402


def dumps(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def resolve_write_path(target: str, explicit: str | None) -> Path:
    if target == "path":
        if not explicit:
            raise ImapConfigError("target=path 需要 --path")
        return Path(explicit).expanduser()
    if target == "skill":
        return cfg.SKILL_ROOT / "local" / "credentials.env"
    if target == "repo":
        return Path.cwd() / ".inbox-watch.env"
    return cfg.SKILL_ROOT / "local" / "credentials.env"


def escape_val(value: str) -> str:
    if re.match(r"^[A-Za-z0-9._@/-]+$", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_credentials(path: Path, values: dict[str, str]) -> dict:
    lines = [
        "# inbox-watch 凭据（禁止提交 Git）",
        "",
    ]
    order = [
        "INBOX_WATCH_IMAP_USER",
        "INBOX_WATCH_IMAP_PASSWORD",
        "INBOX_WATCH_IMAP_HOST",
        "INBOX_WATCH_IMAP_PORT",
        "INBOX_WATCH_OWNER",
        "INBOX_WATCH_COMPANY",
        "INBOX_WATCH_ARCHIVE_DIR",
        "WEIXIN_TO",
        "WEIXIN_BRIDGE_URL",
    ]
    for key in order:
        if values.get(key, "").strip():
            lines.append(f"{key}={escape_val(values[key].strip())}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return {"writtenPath": str(path.resolve())}


def get_setup_status() -> dict:
    bootstrap_env()
    configured = cfg.imap_ready()
    return {
        "configured": configured,
        "needsSetup": not configured,
        "configSnapshot": cfg.config_snapshot(),
        "fieldsToCollect": cfg.SETUP_FIELDS,
        "recommendedWritePath": str(resolve_write_path("skill", None)),
        "recommendedTarget": "skill",
        "note": "通用 IMAP；阿里企业邮默认 imap.qiye.aliyun.com。微信推送需 WEIXIN_TO。",
        "agentProtocol": {
            "reference": "references/onboarding-flow.md",
            "steps": [
                "setup status",
                "按 fieldsToCollect 收集 IMAP 凭据与 WEIXIN_TO",
                "setup apply --verify",
                "doctor",
                "cron 时运行 check_unseen.py 或 run_scan.py --deliver",
            ],
        },
    }


def run_doctor() -> dict:
    bootstrap_env()
    errors: list[str] = []
    warnings: list[str] = []
    if not cfg.imap_ready():
        errors.append("IMAP 凭据未配置")
    if not cfg.WEIXIN_TO:
        warnings.append("WEIXIN_TO 未配置，--deliver 将失败")
    for sub in (cfg.scan_archive_dir(), cfg.attachment_archive_dir()):
        try:
            sub.mkdir(parents=True, exist_ok=True)
            test = sub / ".write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink()
        except OSError as exc:
            errors.append(f"目录不可写: {sub} ({exc})")
    imap_ok = False
    if cfg.imap_ready():
        try:
            mail = connect()
            try:
                count = select_inbox(mail)
                imap_ok = True
                inbox_count = count
            finally:
                try:
                    mail.logout()
                except Exception:
                    pass
        except Exception as exc:
            errors.append(f"IMAP 连接失败: {exc}")
            inbox_count = None
    else:
        inbox_count = None
    return {
        "ok": not errors,
        "imapOk": imap_ok,
        "inboxCount": inbox_count,
        "configSnapshot": cfg.config_snapshot(),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="inbox-watch CLI")
    ap.add_argument("--env-file")
    sub = ap.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup")
    setup_sub = setup.add_subparsers(dest="setup_cmd", required=True)
    setup_sub.add_parser("status")
    apply = setup_sub.add_parser("apply")
    apply.add_argument("--imap-user")
    apply.add_argument("--imap-password")
    apply.add_argument("--imap-host")
    apply.add_argument("--imap-port")
    apply.add_argument("--owner")
    apply.add_argument("--company")
    apply.add_argument("--archive-dir")
    apply.add_argument("--weixin-to")
    apply.add_argument("--weixin-bridge-url")
    apply.add_argument("--target", default="skill", choices=["skill", "repo", "path"])
    apply.add_argument("--path")
    apply.add_argument("--verify", action="store_true")

    sub.add_parser("doctor")
    scan = sub.add_parser("scan")
    scan.add_argument("--deliver", action="store_true")
    scan.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()
    bootstrap_env(explicit_env_file=args.env_file)

    if args.command == "setup":
        if args.setup_cmd == "status":
            print(dumps(get_setup_status()))
            return 0
        if args.setup_cmd == "apply":
            if not args.imap_user or not args.imap_password:
                print("apply 需要 --imap-user 与 --imap-password", file=sys.stderr)
                return 2
            values = {
                "INBOX_WATCH_IMAP_USER": args.imap_user,
                "INBOX_WATCH_IMAP_PASSWORD": args.imap_password,
                "INBOX_WATCH_IMAP_HOST": args.imap_host or cfg.IMAP_HOST,
                "INBOX_WATCH_IMAP_PORT": str(args.imap_port or cfg.IMAP_PORT),
                "INBOX_WATCH_OWNER": args.owner or cfg.OWNER,
                "INBOX_WATCH_COMPANY": args.company or cfg.COMPANY,
                "INBOX_WATCH_ARCHIVE_DIR": args.archive_dir or str(cfg.archive_dir()),
                "WEIXIN_TO": args.weixin_to or "",
                "WEIXIN_BRIDGE_URL": args.weixin_bridge_url or cfg.WEIXIN_BRIDGE_URL,
            }
            path = resolve_write_path(args.target, args.path)
            write_result = write_credentials(path, values)
            result = {"status": "written", "write": write_result}
            if args.verify:
                for k in list(os.environ):
                    if k.startswith("INBOX_WATCH_") or k in ("WEIXIN_TO", "WEIXIN_BRIDGE_URL"):
                        os.environ.pop(k, None)
                bootstrap_env(explicit_env_file=str(path))
                doc = run_doctor()
                result["doctor"] = doc
                result["status"] = "verified" if doc["ok"] else "verify_failed"
            print(dumps(result))
            return 0 if result.get("status") != "verify_failed" else 1

    if args.command == "doctor":
        doc = run_doctor()
        print(dumps(doc))
        return 0 if doc["ok"] else 1

    if args.command == "scan":
        from run_scan import main as scan_main

        sys.argv = ["run_scan.py"]
        if args.deliver:
            sys.argv.append("--deliver")
        if args.dry_run:
            sys.argv.append("--dry-run")
        if args.env_file:
            sys.argv.extend(["--env-file", args.env_file])
        return scan_main()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
