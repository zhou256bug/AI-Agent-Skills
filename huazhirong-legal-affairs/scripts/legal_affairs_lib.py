#!/usr/bin/env python3
"""华智融法务技能配置库（setup status/apply、doctor）。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
LOCAL_CREDENTIALS = SKILL_ROOT / "local" / "credentials.env"
REPO_ENV = Path.cwd() / ".legal-affairs.env"

DEFAULT_DECISION_MAKER = "老板"
DEFAULT_COMPANY = "华智融"
DEFAULT_ARCHIVE_DIR = str(SKILL_ROOT / "output")
DEFAULT_ENTITY_CN = "深圳华智融科技股份有限公司"
DEFAULT_ENTITY_HK = "NEW POS GLOBAL HOLDING (HONG KONG) LIMITED"

SETUP_FIELDS: list[dict[str, Any]] = [
    {
        "key": "LEGAL_AFFAIRS_DECISION_MAKER",
        "label": "决策者称呼",
        "description": "审核意见中的最终商业决策者（如「老板」）",
        "required": False,
        "default": DEFAULT_DECISION_MAKER,
        "example": "老板",
    },
    {
        "key": "LEGAL_AFFAIRS_COMPANY",
        "label": "公司名称",
        "description": "审核意见中的公司主体简称",
        "required": False,
        "default": DEFAULT_COMPANY,
        "example": "华智融",
    },
    {
        "key": "LEGAL_AFFAIRS_ARCHIVE_DIR",
        "label": "归档根目录",
        "description": "合同审核 Markdown 归档路径（绝对或相对 skill 根）",
        "required": False,
        "default": DEFAULT_ARCHIVE_DIR,
        "example": "~/Documents/legal-affairs-output",
    },
    {
        "key": "LEGAL_AFFAIRS_ENTITY_CN",
        "label": "境内签约主体",
        "description": "中国境内常用合同主体全称",
        "required": False,
        "default": DEFAULT_ENTITY_CN,
        "example": "深圳华智融科技股份有限公司",
    },
    {
        "key": "LEGAL_AFFAIRS_ENTITY_HK",
        "label": "境外签约主体",
        "description": "香港/境外常用合同主体全称",
        "required": False,
        "default": DEFAULT_ENTITY_HK,
        "example": "NEW POS GLOBAL HOLDING (HONG KONG) LIMITED",
    },
]


class LegalAffairsConfigError(Exception):
    """配置错误。"""


def read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def format_credentials_file(values: dict[str, str]) -> str:
    lines = [
        "# 华智融法务技能本地配置（由 setup apply 生成，勿提交 Git）",
        "",
    ]
    for field in SETUP_FIELDS:
        key = field["key"]
        if key in values and values[key].strip():
            lines.append(f"{key}={values[key].strip()}")
    lines.append("")
    return "\n".join(lines)


def resolve_setup_target(target: str, explicit_path: str | None = None) -> Path:
    if target == "path":
        if not explicit_path:
            raise LegalAffairsConfigError("target=path 时必须提供 --path")
        return Path(explicit_path).expanduser()
    if target == "skill":
        return LOCAL_CREDENTIALS
    if target == "repo":
        return REPO_ENV
    # auto
    if (SKILL_ROOT / "SKILL.md").is_file():
        return LOCAL_CREDENTIALS
    if (Path.cwd() / ".git").exists():
        return REPO_ENV
    return LOCAL_CREDENTIALS


def find_existing_config_files() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in (LOCAL_CREDENTIALS, REPO_ENV):
        expanded = path.expanduser()
        resolved = str(expanded.resolve()) if expanded.exists() else str(expanded)
        if resolved in seen:
            continue
        seen.add(resolved)
        if not expanded.is_file():
            continue
        values = read_env_file(expanded)
        found.append(
            {
                "path": resolved,
                "decisionMaker": values.get("LEGAL_AFFAIRS_DECISION_MAKER"),
                "company": values.get("LEGAL_AFFAIRS_COMPANY"),
                "archiveDir": values.get("LEGAL_AFFAIRS_ARCHIVE_DIR"),
            }
        )
    return found


def bootstrap_env(explicit_env_file: str | None = None) -> dict[str, Any]:
    """加载本地配置到 os.environ（不覆盖已有环境变量）。"""
    loaded: list[str] = []
    candidates: list[Path] = []
    if explicit_env_file:
        candidates.append(Path(explicit_env_file).expanduser())
    candidates.extend([LOCAL_CREDENTIALS, REPO_ENV])
    for path in candidates:
        if not path.is_file():
            continue
        for key, val in read_env_file(path).items():
            if key and key not in os.environ:
                os.environ[key] = val
        loaded.append(str(path.resolve()))
        break
    return {"loadedFiles": loaded}


def config_snapshot() -> dict[str, str]:
    archive = os.environ.get("LEGAL_AFFAIRS_ARCHIVE_DIR", DEFAULT_ARCHIVE_DIR)
    if not Path(archive).is_absolute():
        archive = str((SKILL_ROOT / archive).resolve())
    return {
        "decisionMaker": os.environ.get("LEGAL_AFFAIRS_DECISION_MAKER", DEFAULT_DECISION_MAKER),
        "company": os.environ.get("LEGAL_AFFAIRS_COMPANY", DEFAULT_COMPANY),
        "archiveDir": archive,
        "entityCn": os.environ.get("LEGAL_AFFAIRS_ENTITY_CN", DEFAULT_ENTITY_CN),
        "entityHk": os.environ.get("LEGAL_AFFAIRS_ENTITY_HK", DEFAULT_ENTITY_HK),
    }


def get_setup_status() -> dict[str, Any]:
    bootstrap_env()
    snapshot = config_snapshot()
    existing = find_existing_config_files()
    recommended = resolve_setup_target("auto")
    has_local = LOCAL_CREDENTIALS.is_file() or REPO_ENV.is_file()

    return {
        "configured": True,
        "hasLocalOverrides": has_local,
        "needsSetup": not has_local,
        "configSnapshot": snapshot,
        "existingConfigFiles": existing,
        "recommendedWritePath": str(recommended.expanduser()),
        "recommendedTarget": "auto",
        "fieldsToCollect": SETUP_FIELDS,
        "note": "本技能无密码凭据；setup 用于个性化决策者/公司/归档路径/签约主体。默认值即可开箱使用。",
        "agentProtocol": {
            "reference": "references/onboarding-flow.md",
            "steps": [
                "首次使用或用户要求个性化时运行 setup status",
                "若 needsSetup 为 true，按 fieldsToCollect 向用户确认是否覆盖默认值",
                "用户确认后运行 setup apply --target skill",
                "运行 doctor 验证配置与目录可写",
                "继续合同审核流程",
            ],
        },
    }


def write_config_file(path: Path, values: dict[str, str]) -> dict[str, Any]:
    payload: dict[str, str] = {}
    for field in SETUP_FIELDS:
        key = field["key"]
        val = values.get(key, field.get("default", "")).strip()
        if val:
            payload[key] = val

    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_credentials_file(payload), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

    return {
        "writtenPath": str(path.resolve()),
        "values": {k: payload[k] for k in payload},
        "permissions": oct(path.stat().st_mode & 0o777),
    }


def run_setup_apply(
    *,
    target: str = "auto",
    explicit_path: str | None = None,
    values: dict[str, str] | None = None,
    verify: bool = False,
) -> dict[str, Any]:
    write_path = resolve_setup_target(target, explicit_path=explicit_path)
    merged = {f["key"]: f.get("default", "") for f in SETUP_FIELDS}
    if values:
        merged.update({k: v for k, v in values.items() if v is not None})
    written = write_config_file(write_path, merged)
    result: dict[str, Any] = {"apply": written}
    if verify:
        bootstrap_env(str(write_path))
        result["doctor"] = run_doctor()
    return result


def run_doctor() -> dict[str, Any]:
    bootstrap_env()
    snap = config_snapshot()
    errors: list[str] = []
    warnings: list[str] = []

    archive = Path(snap["archiveDir"])
    for sub in (
        archive / "合同" / "审核记录",
        archive / "合同" / "采购" / "审核记录",
        archive / "合同" / "人事" / "审核记录",
        archive / "合同" / "股权" / "审核记录",
    ):
        try:
            sub.mkdir(parents=True, exist_ok=True)
            probe = sub / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        except OSError as exc:
            errors.append(f"归档目录不可写：{sub}（{exc}）")

    required_files = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "evals.json",
        SKILL_ROOT / "evaluation" / "run_evals.py",
        SKILL_ROOT / "scripts" / "validate_review_output.py",
        SKILL_ROOT / "modules" / "contract-distribution.md",
        SKILL_ROOT / "modules" / "equity-incentive.md",
        SKILL_ROOT / "modules" / "corporate-jv.md",
        SKILL_ROOT / "references" / "emoji-output-guide.md",
        SKILL_ROOT / "references" / "pdf-review-workflow.md",
        SKILL_ROOT / "scripts" / "render_mobile_pdf.py",
        SKILL_ROOT / "scripts" / "render_review_pdf.py",
    ]
    for f in required_files:
        if not f.is_file():
            errors.append(f"缺少必需文件：{f.relative_to(SKILL_ROOT)}")

    if not snap["decisionMaker"]:
        warnings.append("决策者称呼为空，将使用默认「老板」")
    if not snap["company"]:
        warnings.append("公司名称为空，将使用默认「华智融」")

    return {
        "ok": len(errors) == 0,
        "configSnapshot": snap,
        "errors": errors,
        "warnings": warnings,
    }


def dumps_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
