#!/usr/bin/env python3
"""华智融法务技能的可配置项（平台无关，全部支持环境变量覆盖）。

优先通过 legal_affairs_cli.py setup apply 写入 local/credentials.env。
也可直接设置环境变量（优先级更高）。

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| DECISION_MAKER | LEGAL_AFFAIRS_DECISION_MAKER | 老板 | 最终商业决策者称呼 |
| COMPANY        | LEGAL_AFFAIRS_COMPANY        | 华智融 | 公司名 |
| ARCHIVE_DIR    | LEGAL_AFFAIRS_ARCHIVE_DIR    | <skill>/output | 合同审核归档根目录 |
| ENTITY_CN      | LEGAL_AFFAIRS_ENTITY_CN      | 深圳华智融科技股份有限公司 | 境内签约主体 |
| ENTITY_HK      | LEGAL_AFFAIRS_ENTITY_HK      | NEW POS GLOBAL HOLDING (HONG KONG) LIMITED | 境外签约主体 |
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
_LOCAL_ENV = SKILL_ROOT / "local" / "credentials.env"
_REPO_ENV = Path.cwd() / ".legal-affairs.env"


def _load_local_env() -> None:
    """把本地配置文件的 KEY=VALUE 注入 os.environ（不覆盖已有环境变量）。"""
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


# ── 业务/路径 ──
DECISION_MAKER: str = _get("LEGAL_AFFAIRS_DECISION_MAKER", "老板")
COMPANY: str = _get("LEGAL_AFFAIRS_COMPANY", "华智融")
ENTITY_CN: str = _get("LEGAL_AFFAIRS_ENTITY_CN", "深圳华智融科技股份有限公司")
ENTITY_HK: str = _get("LEGAL_AFFAIRS_ENTITY_HK", "NEW POS GLOBAL HOLDING (HONG KONG) LIMITED")

_archive_raw = _get("LEGAL_AFFAIRS_ARCHIVE_DIR", str(SKILL_ROOT / "output"))
ARCHIVE_DIR: Path = Path(_archive_raw) if Path(_archive_raw).is_absolute() else SKILL_ROOT / _archive_raw

# 归档子目录
ARCHIVE_REVIEW = ARCHIVE_DIR / "合同" / "审核记录"
ARCHIVE_PROCUREMENT = ARCHIVE_DIR / "合同" / "采购" / "审核记录"
ARCHIVE_LABOR = ARCHIVE_DIR / "合同" / "人事" / "审核记录"
ARCHIVE_EQUITY = ARCHIVE_DIR / "合同" / "股权" / "审核记录"
