#!/usr/bin/env python3
"""微信 bridge 投递（纯标准库）。"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import inbox_watch_config as cfg  # noqa: E402


def post_send(content: str, *, media_path: Path | None = None, dry_run: bool = False) -> dict:
    if not cfg.WEIXIN_TO:
        return {"ok": False, "retryable": False, "detail": "缺少 WEIXIN_TO"}
    payload: dict = {"to": cfg.WEIXIN_TO, "content": content}
    if media_path and media_path.is_file():
        payload["media_path"] = str(media_path.resolve())
    if cfg.WEIXIN_ACCOUNT_ID:
        payload["account_id"] = cfg.WEIXIN_ACCOUNT_ID
    url = cfg.WEIXIN_BRIDGE_URL.rstrip("/") + "/send"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if dry_run:
        return {"ok": True, "retryable": False, "detail": f"[dry-run] POST {url}"}
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            body = resp.read().decode("utf-8", "replace")
            return {"ok": resp.status == 200, "retryable": resp.status != 200, "detail": body[:200]}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return {"ok": False, "retryable": True, "detail": f"HTTP {e.code}: {body[:200]}"}
    except (urllib.error.URLError, OSError) as e:
        return {"ok": False, "retryable": True, "detail": f"连接异常: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser(description="通过微信 bridge 发送扫描摘要")
    ap.add_argument("--text", required=True, help="推送正文")
    ap.add_argument("--media", type=Path, help="可选附件路径")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    result = post_send(args.text, media_path=args.media, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
