#!/usr/bin/env python3
"""收件箱值守技能可配置项（通用 IMAP，支持阿里企业邮等）。

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| OWNER | INBOX_WATCH_OWNER | 老板 | 汇报对象称呼 |
| COMPANY | INBOX_WATCH_COMPANY | 华智融 | 公司名 |
| ARCHIVE_DIR | INBOX_WATCH_ARCHIVE_DIR | <skill>/output | 扫描摘要归档根目录 |
| IMAP_HOST | INBOX_WATCH_IMAP_HOST | imap.qiye.aliyun.com | IMAP 主机 |
| IMAP_PORT | INBOX_WATCH_IMAP_PORT | 993 | IMAP SSL 端口 |
| IMAP_USER | INBOX_WATCH_IMAP_USER | (空) | 邮箱账号 |
| IMAP_PASSWORD | INBOX_WATCH_IMAP_PASSWORD | (空) | 密码/授权码 |
| UNSEEN_LIMIT | INBOX_WATCH_UNSEEN_LIMIT | 50 | 单次 UNSEEN 上限 |
| BODY_PREVIEW_CHARS | INBOX_WATCH_BODY_PREVIEW_CHARS | 500 | 正文预览字数 |
| WEIXIN_BRIDGE_URL | WEIXIN_BRIDGE_URL | http://localhost:9100 | 微信 bridge |
| WEIXIN_TO | WEIXIN_TO | (空) | 微信收件人 user_id |
| WEIXIN_ACCOUNT_ID | WEIXIN_ACCOUNT_ID | (空) | 多账号时可选 |
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
_LOCAL_ENV = SKILL_ROOT / "local" / "credentials.env"
_REPO_ENV = Path.cwd() / ".inbox-watch.env"

KNOWN_IMAP_HOSTS = {
    "aliyun_cn": "imap.qiye.aliyun.com",
    "aliyun_hk": "imaphk.qiye.aliyun.com",
    "aliyun_legacy": "imap.mxhichina.com",
}

SETUP_FIELDS: list[dict] = [
    {
        "key": "INBOX_WATCH_IMAP_USER",
        "label": "邮箱账号",
        "description": "完整邮箱地址",
        "required": True,
        "secret": False,
        "example": "name@company.com",
    },
    {
        "key": "INBOX_WATCH_IMAP_PASSWORD",
        "label": "客户端授权密码",
        "description": "IMAP 登录密码或客户端专用授权码",
        "required": True,
        "secret": True,
        "example": "在邮箱设置中生成",
    },
    {
        "key": "INBOX_WATCH_IMAP_HOST",
        "label": "IMAP 主机",
        "description": "阿里企业邮默认 imap.qiye.aliyun.com；其它邮箱填对应主机",
        "required": False,
        "default": "imap.qiye.aliyun.com",
    },
    {
        "key": "INBOX_WATCH_IMAP_PORT",
        "label": "IMAP 端口",
        "required": False,
        "default": "993",
    },
    {
        "key": "INBOX_WATCH_OWNER",
        "label": "汇报对象",
        "required": False,
        "default": "老板",
    },
    {
        "key": "WEIXIN_TO",
        "label": "微信收件人",
        "description": "hermes-weixin bridge 的 user_id",
        "required": False,
        "example": "your_wechat_id",
    },
]


def _load_local_env() -> None:
    for env_path in (_LOCAL_ENV, _REPO_ENV):
        if not env_path.is_file():
            continue
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
        break


_load_local_env()


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


OWNER: str = _get("INBOX_WATCH_OWNER", "老板")
COMPANY: str = _get("INBOX_WATCH_COMPANY", "华智融")
IMAP_HOST: str = _get("INBOX_WATCH_IMAP_HOST", KNOWN_IMAP_HOSTS["aliyun_cn"])
IMAP_PORT: int = int(_get("INBOX_WATCH_IMAP_PORT", "993") or "993")
IMAP_USER: str = _get("INBOX_WATCH_IMAP_USER")
IMAP_PASSWORD: str = _get("INBOX_WATCH_IMAP_PASSWORD")
UNSEEN_LIMIT: int = int(_get("INBOX_WATCH_UNSEEN_LIMIT", "50") or "50")
BODY_PREVIEW_CHARS: int = int(_get("INBOX_WATCH_BODY_PREVIEW_CHARS", "500") or "500")
WEIXIN_BRIDGE_URL: str = _get("WEIXIN_BRIDGE_URL", "http://localhost:9100")
WEIXIN_TO: str = _get("WEIXIN_TO")
WEIXIN_ACCOUNT_ID: str = _get("WEIXIN_ACCOUNT_ID")

WATCHLIST_PATH = SKILL_ROOT / "data" / "watchlist.json"
SYSTEM_PATTERNS_PATH = SKILL_ROOT / "data" / "system-sender-patterns.json"


def archive_dir() -> Path:
    env = _get("INBOX_WATCH_ARCHIVE_DIR")
    if env:
        p = Path(env).expanduser()
        return p if p.is_absolute() else SKILL_ROOT / p
    return SKILL_ROOT / "output"


def scan_archive_dir() -> Path:
    return archive_dir() / "scans"


def attachment_archive_dir() -> Path:
    return archive_dir() / "attachments"


def imap_ready() -> bool:
    return bool(IMAP_USER and IMAP_PASSWORD and IMAP_HOST)


def config_snapshot() -> dict:
    user = IMAP_USER
    masked = "***"
    if user and "@" in user:
        local, domain = user.split("@", 1)
        masked = f"{local[0]}***@{domain}" if local else f"***@{domain}"
    return {
        "owner": OWNER,
        "company": COMPANY,
        "archiveDir": str(archive_dir()),
        "imapHost": IMAP_HOST,
        "imapPort": IMAP_PORT,
        "imapUser": masked if user else None,
        "imapPasswordSet": bool(IMAP_PASSWORD),
        "unseenLimit": UNSEEN_LIMIT,
        "weixinTo": WEIXIN_TO or None,
        "weixinBridgeUrl": WEIXIN_BRIDGE_URL,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(config_snapshot(), ensure_ascii=False, indent=2))
