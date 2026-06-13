#!/usr/bin/env python3
"""管理团队周报技能的可配置项（平台无关，全部支持环境变量覆盖）。

设计目标：clone 后开箱即用——所有"特定公司/特定人/特定路径/凭据"都集中在这里，
支持两种来源（环境变量优先，其次本地凭据文件）：

1. 进程环境变量（最高优先级）
2. `<skill>/local/credentials.env`（KEY=VALUE，已 gitignore，不入库）

业务/路径配置：

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| OWNER         | WEEKLY_REPORT_OWNER         | 老板                       | PDF 收件人；段标题「需{OWNER}关注的事项」与禁止段 |
| SENDER_NAME   | WEEKLY_REPORT_SENDER_NAME   | 陈徐伟                     | 源周报邮件发件人姓名（meta「来源」） |
| SENDER_EMAIL  | WEEKLY_REPORT_SENDER_EMAIL  | evyn.chen@newpostech.com   | 需查询的源周报邮件发件人邮箱 |
| SUBJECT_KEY   | WEEKLY_REPORT_SUBJECT_KEY   | 总裁办及各部门经理周报      | 源邮件主题关键词 |
| COMPANY       | WEEKLY_REPORT_COMPANY       | 华智融                     | 公司名 |
| ARCHIVE_DIR   | WEEKLY_REPORT_ARCHIVE_DIR   | <skill>/output            | MD/PDF/xlsx/状态 归档根目录 |

取信（IMAP，必备能力的凭据）：

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| IMAP_HOST     | WEEKLY_REPORT_IMAP_HOST     | (空)   | 收件箱 IMAP 主机，如 imap.qiye.aliyun.com |
| IMAP_PORT     | WEEKLY_REPORT_IMAP_PORT     | 993    | IMAP SSL 端口 |
| IMAP_USER     | WEEKLY_REPORT_IMAP_USER     | (空)   | 收件箱账号 |
| IMAP_PASSWORD | WEEKLY_REPORT_IMAP_PASSWORD | (空)   | 收件箱密码/客户端授权码（勿入库） |
| SINCE_DAYS    | WEEKLY_REPORT_SINCE_DAYS    | 10     | IMAP SINCE 回溯天数 |

投递（微信 bridge / 群机器人）：

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| WEIXIN_BRIDGE_URL  | WEIXIN_BRIDGE_URL  | http://localhost:9100 | hermes-weixin bridge 地址（POST /send 有 200/500 回执） |
| WEIXIN_TO          | WEIXIN_TO          | (空)   | 收件人 WeChat user_id（老板） |
| WEIXIN_ACCOUNT_ID  | WEIXIN_ACCOUNT_ID  | (空)   | 可选，多账号时指定 |
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
_LOCAL_ENV = SKILL_ROOT / "local" / "credentials.env"


def _load_local_env() -> None:
    """把 local/credentials.env 的 KEY=VALUE 注入 os.environ（不覆盖已有环境变量）。"""
    if not _LOCAL_ENV.is_file():
        return
    for raw in _LOCAL_ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


_load_local_env()


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# ── 业务/路径 ──
OWNER: str = _get("WEEKLY_REPORT_OWNER", "老板")
SENDER_NAME: str = _get("WEEKLY_REPORT_SENDER_NAME", "陈徐伟")
SENDER_EMAIL: str = _get("WEEKLY_REPORT_SENDER_EMAIL", "evyn.chen@newpostech.com")
SUBJECT_KEY: str = _get("WEEKLY_REPORT_SUBJECT_KEY", "总裁办及各部门经理周报")
COMPANY: str = _get("WEEKLY_REPORT_COMPANY", "华智融")

# ── 取信 IMAP ──
IMAP_HOST: str = _get("WEEKLY_REPORT_IMAP_HOST")
IMAP_PORT: int = int(_get("WEEKLY_REPORT_IMAP_PORT", "993") or "993")
IMAP_USER: str = _get("WEEKLY_REPORT_IMAP_USER")
IMAP_PASSWORD: str = _get("WEEKLY_REPORT_IMAP_PASSWORD")
SINCE_DAYS: int = int(_get("WEEKLY_REPORT_SINCE_DAYS", "10") or "10")

# ── 投递（微信 bridge）──
WEIXIN_BRIDGE_URL: str = _get("WEIXIN_BRIDGE_URL", "http://localhost:9100")
WEIXIN_TO: str = _get("WEIXIN_TO")
WEIXIN_ACCOUNT_ID: str = _get("WEIXIN_ACCOUNT_ID")


def archive_dir() -> Path:
    """归档根目录：环境变量优先，否则技能本地 output/（已 gitignore）。"""
    env = os.environ.get("WEEKLY_REPORT_ARCHIVE_DIR")
    return Path(env).expanduser() if env else (SKILL_ROOT / "output")


def imap_ready() -> bool:
    return bool(IMAP_HOST and IMAP_USER and IMAP_PASSWORD)


if __name__ == "__main__":
    print(f"OWNER         = {OWNER}")
    print(f"SENDER_NAME   = {SENDER_NAME}")
    print(f"SENDER_EMAIL  = {SENDER_EMAIL}")
    print(f"SUBJECT_KEY   = {SUBJECT_KEY}")
    print(f"COMPANY       = {COMPANY}")
    print(f"ARCHIVE_DIR   = {archive_dir()}")
    print(f"IMAP_HOST     = {IMAP_HOST or '(未配置)'}")
    print(f"IMAP_USER     = {IMAP_USER or '(未配置)'}")
    print(f"IMAP_PASSWORD = {'***' if IMAP_PASSWORD else '(未配置)'}")
    print(f"IMAP ready    = {imap_ready()}")
    print(f"WEIXIN_BRIDGE_URL = {WEIXIN_BRIDGE_URL}")
    print(f"WEIXIN_TO     = {WEIXIN_TO or '(未配置)'}")
