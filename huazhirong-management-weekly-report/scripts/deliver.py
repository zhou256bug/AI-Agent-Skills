#!/usr/bin/env python3
"""多通道投递层（纯标准库，可扩展，带回执判定）。

通道：
- wechat-bridge : 直连 hermes-weixin bridge `POST /send`，读 HTTP 200/500 →**真实成功/失败**
                  （限流/网络/鉴权失败都会表现为非 200，可重试）。自动化默认。
- wechat-media  : 仅输出 `MEDIA:<绝对路径>` 行，交给 Hermes 回复→网关代发（**无回执**，交互兜底）。
- wecom         : 企业微信群机器人 webhook（WECOM_WEBHOOK_URL），文本通知。
- feishu        : 飞书自定义机器人 webhook（FEISHU_WEBHOOK_URL），文本通知。

统一返回 dict：{"ok": bool, "retryable": bool, "channel": str, "detail": str}
退出码：ok→0；可重试失败→3；配置错误→2。

参考 hermes-weixin 官方插件：POST /send 体 {to, content, media_path, account_id}，
成功 200、失败 500（src/bot.ts）；底层任何非 2xx 抛错（src/api/api.ts）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_report_config as cfg  # noqa: E402


def _post_json(url: str, payload: dict, *, dry_run: bool, timeout: int = 30) -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if dry_run:
        return 200, f"[dry-run] POST {url} {data.decode('utf-8')}"
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def deliver_wechat_bridge(file: Path, title: str, text: str, dry_run: bool) -> dict:
    if not cfg.WEIXIN_TO:
        return {"ok": False, "retryable": False, "channel": "wechat-bridge",
                "detail": "缺少 WEIXIN_TO（收件人 user_id）"}
    payload = {"to": cfg.WEIXIN_TO, "content": text or title, "media_path": str(file.resolve())}
    if cfg.WEIXIN_ACCOUNT_ID:
        payload["account_id"] = cfg.WEIXIN_ACCOUNT_ID
    url = cfg.WEIXIN_BRIDGE_URL.rstrip("/") + "/send"
    try:
        status, body = _post_json(url, payload, dry_run=dry_run)
    except (urllib.error.URLError, OSError) as e:
        # 连接失败/超时 → 可重试（含网关未起、限流断连等）
        return {"ok": False, "retryable": True, "channel": "wechat-bridge", "detail": f"连接异常：{e}"}
    if status == 200:
        return {"ok": True, "retryable": False, "channel": "wechat-bridge", "detail": body[:160]}
    # 500/限流/其它非 200 → 可重试
    return {"ok": False, "retryable": True, "channel": "wechat-bridge",
            "detail": f"HTTP {status}: {body[:160]}"}


def deliver_wechat_media(file: Path, title: str, text: str, dry_run: bool) -> dict:
    # 发后不管：输出 MEDIA: 行，由 Hermes 回复→网关代发，无回执
    print(f"MEDIA:{file.resolve()}")
    if text:
        print(text)
    return {"ok": True, "retryable": False, "channel": "wechat-media", "detail": "emitted MEDIA line (no ack)"}


def _deliver_webhook(channel: str, env_var: str, payload_builder, file: Path, title: str, text: str, dry_run: bool) -> dict:
    url = os.environ.get(env_var)
    if not url:
        return {"ok": False, "retryable": False, "channel": channel, "detail": f"缺少 {env_var}"}
    content = text or f"{title}\n文件：{file.resolve()}"
    try:
        status, body = _post_json(url, payload_builder(content), dry_run=dry_run)
    except (urllib.error.URLError, OSError) as e:
        return {"ok": False, "retryable": True, "channel": channel, "detail": f"连接异常：{e}"}
    ok = status == 200
    return {"ok": ok, "retryable": not ok, "channel": channel, "detail": f"HTTP {status}: {body[:120]}"}


def deliver_wecom(file: Path, title: str, text: str, dry_run: bool) -> dict:
    return _deliver_webhook("wecom", "WECOM_WEBHOOK_URL",
                            lambda c: {"msgtype": "text", "text": {"content": c}},
                            file, title, text, dry_run)


def deliver_feishu(file: Path, title: str, text: str, dry_run: bool) -> dict:
    return _deliver_webhook("feishu", "FEISHU_WEBHOOK_URL",
                            lambda c: {"msg_type": "text", "content": {"text": c}},
                            file, title, text, dry_run)


# 新增通道：在此注册即可
CHANNELS = {
    "wechat-bridge": deliver_wechat_bridge,
    "wechat-media": deliver_wechat_media,
    "wecom": deliver_wecom,
    "feishu": deliver_feishu,
}


def deliver(channel: str, file: Path, title: str = "管理团队周报", text: str = "", dry_run: bool = False) -> dict:
    """供编排器调用的统一入口。"""
    if channel not in CHANNELS:
        return {"ok": False, "retryable": False, "channel": channel, "detail": "未知通道"}
    return CHANNELS[channel](file, title, text, dry_run)


def main() -> int:
    ap = argparse.ArgumentParser(description="多通道投递周报 PDF")
    ap.add_argument("--channel", required=True, choices=sorted(CHANNELS))
    ap.add_argument("--file", required=True, type=Path)
    ap.add_argument("--title", default="管理团队周报")
    ap.add_argument("--text", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.file.exists() and args.channel != "wechat-media" and not args.dry_run:
        print(f"文件不存在：{args.file}", file=sys.stderr)
        return 2

    res = deliver(args.channel, args.file, args.title, args.text, args.dry_run)
    print(json.dumps(res, ensure_ascii=False))
    if res["ok"]:
        return 0
    return 3 if res["retryable"] else 2


if __name__ == "__main__":
    sys.exit(main())
