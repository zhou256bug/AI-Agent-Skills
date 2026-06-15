#!/usr/bin/env python3
"""扫描 UNSEEN 未读邮件，输出结构化文本（供 Agent cron 解析）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from imap_lib import ImapConfigError, ImapConnectionError, bootstrap_env, scan_unseen  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="扫描收件箱 UNSEEN 未读邮件")
    ap.add_argument("--env-file", help="凭据文件路径")
    ap.add_argument("--folder", default="INBOX")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非文本格式")
    args = ap.parse_args()

    bootstrap_env(explicit_env_file=args.env_file)
    try:
        result = scan_unseen(folder=args.folder, limit=args.limit)
    except ImapConfigError as exc:
        print(f"CONFIG_ERROR: {exc}", file=sys.stderr)
        return 2
    except ImapConnectionError as exc:
        print(f"IMAP_ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        # 不输出 body_full 到默认 JSON（过大）；文本格式不含全文
        payload = {
            "total_unseen": result["total_unseen"],
            "personal_unseen": result["personal_unseen"],
            "emails": [
                {k: v for k, v in e.items() if k != "body_full"}
                for e in result["emails"]
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(result["text"], end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
