#!/usr/bin/env python3
"""多通道投递层（纯标准库，可扩展）。

支持通道：
- wechat-media : 输出 Hermes→微信桥接约定的 `MEDIA:<绝对路径>` 行（最终回复带它，微信才附 PDF）。
- wecom        : 企业微信群机器人 webhook 发送文本通知（环境变量 WECOM_WEBHOOK_URL）。
- feishu       : 飞书自定义机器人 webhook 发送文本通知（环境变量 FEISHU_WEBHOOK_URL）。

设计：核心技能与"投递"解耦——投递是可选的平台胶水层。新增通道只需在 CHANNELS 注册一个函数。
说明：wecom/feishu 的 webhook 仅能发"文本/卡片通知"；要直接上传 PDF 文件，需各平台的
      "上传素材 + 应用凭据" API（需要 secret，超出本脚本范围），此处发送含标题与文件路径的通知。

用法：
    python3 scripts/deliver.py --channel wechat-media --file output/W23-....pdf
    python3 scripts/deliver.py --channel wecom  --file output/W23-....pdf --title "第23期周报" [--dry-run]
    python3 scripts/deliver.py --channel feishu --file output/W23-....pdf --title "第23期周报" [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def _post_json(url: str, payload: dict, *, dry_run: bool) -> int:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if dry_run:
        print(f"[dry-run] POST {url}\n{data.decode('utf-8')}")
        return 0
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 (url 来自用户配置)
        body = resp.read().decode("utf-8", "replace")
        print(f"HTTP {resp.status}: {body[:200]}")
        return 0 if resp.status == 200 else 1


def deliver_wechat_media(file: Path, title: str, text: str, dry_run: bool) -> int:
    # Hermes→微信桥接：最终回复中包含单独一行 MEDIA:<绝对路径>，微信才会附带该 PDF
    print(f"MEDIA:{file.resolve()}")
    if text:
        print(text)
    return 0


def deliver_wecom(file: Path, title: str, text: str, dry_run: bool) -> int:
    url = os.environ.get("WECOM_WEBHOOK_URL")
    if not url:
        print("缺少环境变量 WECOM_WEBHOOK_URL（企业微信群机器人 webhook）", file=sys.stderr)
        return 2
    content = text or f"{title}\n文件：{file.resolve()}"
    return _post_json(url, {"msgtype": "text", "text": {"content": content}}, dry_run=dry_run)


def deliver_feishu(file: Path, title: str, text: str, dry_run: bool) -> int:
    url = os.environ.get("FEISHU_WEBHOOK_URL")
    if not url:
        print("缺少环境变量 FEISHU_WEBHOOK_URL（飞书自定义机器人 webhook）", file=sys.stderr)
        return 2
    content = text or f"{title}\n文件：{file.resolve()}"
    return _post_json(url, {"msg_type": "text", "content": {"text": content}}, dry_run=dry_run)


# 新增通道：在此注册即可（保持核心解耦、可扩展）
CHANNELS = {
    "wechat-media": deliver_wechat_media,
    "wecom": deliver_wecom,
    "feishu": deliver_feishu,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="多通道投递周报 PDF")
    ap.add_argument("--channel", required=True, choices=sorted(CHANNELS))
    ap.add_argument("--file", required=True, type=Path, help="待投递文件（PDF）")
    ap.add_argument("--title", default="管理团队周报", help="通知标题")
    ap.add_argument("--text", default="", help="自定义通知正文（覆盖默认）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将要发送的内容，不联网")
    args = ap.parse_args()

    if not args.file.exists() and args.channel != "wechat-media":
        # wechat-media 仅产出路径行，允许文件尚未生成时预览；其余通道要求文件存在
        print(f"文件不存在：{args.file}", file=sys.stderr)
        return 2

    return CHANNELS[args.channel](args.file, args.title, args.text, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
