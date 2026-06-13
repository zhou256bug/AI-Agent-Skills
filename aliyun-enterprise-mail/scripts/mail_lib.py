"""阿里企业邮箱 IMAP 读信共享库（仅标准库）。"""

from __future__ import annotations

import email
import imaplib
import json
import os
import re
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


DEFAULT_IMAP_HOST = "imap.qiye.aliyun.com"
DEFAULT_IMAP_PORT = 993

# 凭据相关环境变量（跨 Agent 统一契约）
CREDENTIAL_ENV_KEYS = (
    "ALIYUN_MAIL_USER",
    "ALIYUN_MAIL_PASSWORD",
    "ALIYUN_MAIL_IMAP_HOST",
    "ALIYUN_MAIL_IMAP_PORT",
    "ALIYUN_MAIL_ENV_FILE",
)

# 常见企业邮箱 IMAP 主机备选（由 ALIYUN_MAIL_IMAP_HOST 覆盖）
KNOWN_IMAP_HOSTS = {
    "cn": "imap.qiye.aliyun.com",
    "hk": "imaphk.qiye.aliyun.com",
    "legacy": "imap.mxhichina.com",
}

DEFAULT_USER_CREDENTIALS_PATH = (
    Path.home() / ".config" / "aliyun-enterprise-mail" / "credentials.env"
)

# skill 目录（scripts/ 的上级），用于 clone 后本地凭据落盘
SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_LOCAL_CREDENTIALS_PATH = SKILL_DIR / "local" / "credentials.env"

# Agent 引导配置时需向用户收集的字段（结构化，供 setup status 输出）
SETUP_FIELDS: list[dict[str, Any]] = [
    {
        "key": "ALIYUN_MAIL_USER",
        "label": "完整邮箱地址",
        "required": True,
        "secret": False,
        "example": "your.name@company.com",
        "agentPrompt": "请提供你的阿里企业邮箱完整地址（例如 name@company.com）。",
    },
    {
        "key": "ALIYUN_MAIL_PASSWORD",
        "label": "客户端授权密码",
        "required": True,
        "secret": True,
        "example": "在网页邮箱「设置 → 账户与安全」中生成",
        "agentPrompt": "请提供客户端授权密码（推荐，而非网页登录密码）。若尚未开启三方客户端，需联系管理员。",
    },
    {
        "key": "ALIYUN_MAIL_IMAP_HOST",
        "label": "IMAP 主机",
        "required": False,
        "secret": False,
        "default": DEFAULT_IMAP_HOST,
        "choices": list(KNOWN_IMAP_HOSTS.values()),
        "agentPrompt": "IMAP 主机默认 imap.qiye.aliyun.com；香港节点用 imaphk.qiye.aliyun.com；不确定可直接跳过。",
    },
    {
        "key": "ALIYUN_MAIL_IMAP_PORT",
        "label": "IMAP 端口",
        "required": False,
        "secret": False,
        "default": str(DEFAULT_IMAP_PORT),
        "agentPrompt": "IMAP 端口默认 993，一般无需修改。",
    },
]

SETUP_TARGETS = ("auto", "skill", "repo", "user", "path")


class MailConfigError(ValueError):
    """邮箱连接配置缺失或无效。"""


class MailConnectionError(RuntimeError):
    """IMAP 连接或认证失败。"""


@dataclass
class MailConfig:
    host: str
    port: int
    user: str
    password: str

    @classmethod
    def from_env(cls) -> MailConfig:
        user = os.environ.get("ALIYUN_MAIL_USER", "").strip()
        password = os.environ.get("ALIYUN_MAIL_PASSWORD", "").strip()
        if not user:
            raise MailConfigError(
                "缺少环境变量 ALIYUN_MAIL_USER（完整邮箱地址，例如 user@company.com）。"
            )
        if not password:
            raise MailConfigError(
                "缺少环境变量 ALIYUN_MAIL_PASSWORD（登录密码或客户端授权密码）。"
            )
        host = os.environ.get("ALIYUN_MAIL_IMAP_HOST", DEFAULT_IMAP_HOST).strip()
        port_raw = os.environ.get("ALIYUN_MAIL_IMAP_PORT", str(DEFAULT_IMAP_PORT)).strip()
        try:
            port = int(port_raw)
        except ValueError as exc:
            raise MailConfigError(
                f"ALIYUN_MAIL_IMAP_PORT 必须是整数，当前值: {port_raw!r}"
            ) from exc
        return cls(host=host, port=port, user=user, password=password)


def parse_env_line(line: str) -> tuple[str, str] | None:
    """解析单行 KEY=VALUE（支持 export 前缀与引号）。"""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()
    if "=" not in stripped:
        return None
    key, _, raw_value = stripped.partition("=")
    key = key.strip()
    if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
        return None
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return key, value


def read_env_file(path: Path) -> dict[str, str]:
    """读取 env 文件为字典，不写入 os.environ。"""
    values: dict[str, str] = {}
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        parsed = parse_env_line(line)
        if parsed is None:
            continue
        key, value = parsed
        values[key] = value
    return values


def apply_env_values(values: dict[str, str], *, override: bool = False) -> list[str]:
    """将键值写入 os.environ；默认不覆盖已存在的非空变量。"""
    applied: list[str] = []
    for key, value in values.items():
        if not override and os.environ.get(key, "").strip():
            continue
        os.environ[key] = value
        applied.append(key)
    return applied


def default_env_file_candidates() -> list[Path]:
    return [
        Path.cwd() / ".aliyun-mail.env",
        SKILL_LOCAL_CREDENTIALS_PATH,
        DEFAULT_USER_CREDENTIALS_PATH,
        Path.home() / ".aliyun-mail.env",
    ]


def bootstrap_env(*, explicit_env_file: str | None = None) -> dict[str, Any]:
    """
    按优先级加载凭据文件（不覆盖进程已有非空环境变量）：
    1. --env-file 显式路径
    2. ALIYUN_MAIL_ENV_FILE
    3. ./.aliyun-mail.env
    4. <skill>/local/credentials.env
    5. ~/.config/aliyun-enterprise-mail/credentials.env
    6. ~/.aliyun-mail.env
    """
    candidates: list[Path] = []
    if explicit_env_file:
        candidates.append(Path(explicit_env_file).expanduser())
    env_file_var = os.environ.get("ALIYUN_MAIL_ENV_FILE", "").strip()
    if env_file_var:
        candidates.append(Path(env_file_var).expanduser())
    candidates.extend(default_env_file_candidates())

    loaded_from: list[dict[str, Any]] = []
    skipped_paths: list[str] = []
    seen: set[str] = set()

    for path in candidates:
        resolved = str(path.expanduser().resolve()) if path.expanduser().exists() else str(path.expanduser())
        if resolved in seen:
            continue
        seen.add(resolved)

        expanded = path.expanduser()
        if not expanded.is_file():
            skipped_paths.append(resolved)
            continue

        applied = apply_env_values(read_env_file(expanded), override=False)
        if applied:
            loaded_from.append({"path": resolved, "keys": applied})

    preset_keys = [
        key for key in CREDENTIAL_ENV_KEYS if os.environ.get(key, "").strip()
    ]
    return {
        "loadedFrom": loaded_from,
        "checkedPaths": [str(p.expanduser()) for p in candidates],
        "missingPaths": skipped_paths,
        "presetEnvKeys": preset_keys,
    }


def mask_user_email(user: str) -> str:
    if "@" not in user:
        return "***"
    local, domain = user.split("@", 1)
    if len(local) <= 1:
        masked_local = "*"
    else:
        masked_local = f"{local[0]}***"
    return f"{masked_local}@{domain}"


def config_snapshot() -> dict[str, Any]:
    user = os.environ.get("ALIYUN_MAIL_USER", "").strip()
    password = os.environ.get("ALIYUN_MAIL_PASSWORD", "").strip()
    host = os.environ.get("ALIYUN_MAIL_IMAP_HOST", DEFAULT_IMAP_HOST).strip()
    port_raw = os.environ.get("ALIYUN_MAIL_IMAP_PORT", str(DEFAULT_IMAP_PORT)).strip()
    return {
        "user": mask_user_email(user) if user else None,
        "passwordSet": bool(password),
        "host": host or DEFAULT_IMAP_HOST,
        "port": port_raw or str(DEFAULT_IMAP_PORT),
        "envFile": os.environ.get("ALIYUN_MAIL_ENV_FILE") or None,
    }


def run_doctor(*, explicit_env_file: str | None = None) -> dict[str, Any]:
    bootstrap = bootstrap_env(explicit_env_file=explicit_env_file)
    snapshot = config_snapshot()
    result: dict[str, Any] = {
        "status": "ok",
        "bootstrap": bootstrap,
        "config": snapshot,
        "checks": [],
    }

    try:
        cfg = MailConfig.from_env()
    except MailConfigError as exc:
        result["status"] = "config_error"
        result["checks"].append({"name": "config", "ok": False, "detail": str(exc)})
        result["hint"] = (
            "运行 setup status 查看需向用户收集的字段；"
            "收集完成后用 setup apply 写入凭据，再运行 doctor 验证。"
            "详见 references/onboarding-flow.md。"
        )
        result["nextAction"] = "setup status"
        return result

    result["checks"].append({"name": "config", "ok": True, "detail": "凭据字段齐全"})

    try:
        mail = connect(cfg)
        try:
            folders = list_folders(mail)
            inbox_info = None
            try:
                inbox_info = select_folder(mail, "INBOX")
            except MailConnectionError:
                inbox_info = None
            result["checks"].append(
                {
                    "name": "imap_login",
                    "ok": True,
                    "detail": f"已连接 {cfg.host}:{cfg.port}",
                }
            )
            result["checks"].append(
                {
                    "name": "list_folders",
                    "ok": True,
                    "detail": f"可见文件夹 {len(folders)} 个",
                }
            )
            if inbox_info:
                result["inbox"] = inbox_info
        finally:
            try:
                mail.logout()
            except imaplib.IMAP4.error:
                pass
    except MailConnectionError as exc:
        result["status"] = "connection_error"
        result["checks"].append({"name": "imap_login", "ok": False, "detail": str(exc)})

    return result


def escape_env_value(value: str) -> str:
    if re.match(r"^[A-Za-z0-9._@/-]+$", value):
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_credentials_file(values: dict[str, str]) -> str:
    lines = [
        "# 阿里企业邮箱凭据（由 aliyun-enterprise-mail setup 生成）",
        "# 此文件含敏感信息，禁止提交到 Git",
        "",
    ]
    order = (
        "ALIYUN_MAIL_USER",
        "ALIYUN_MAIL_PASSWORD",
        "ALIYUN_MAIL_IMAP_HOST",
        "ALIYUN_MAIL_IMAP_PORT",
    )
    for key in order:
        if key in values and values[key].strip():
            lines.append(f"{key}={escape_env_value(values[key].strip())}")
    lines.append("")
    return "\n".join(lines)


def resolve_setup_target(
    target: str = "auto",
    *,
    explicit_path: str | None = None,
) -> Path:
    if target not in SETUP_TARGETS:
        raise MailConfigError(
            f"未知 target {target!r}，可选: {', '.join(SETUP_TARGETS)}"
        )
    if target == "path":
        if not explicit_path:
            raise MailConfigError("target=path 时必须提供 --path。")
        return Path(explicit_path).expanduser()

    if target == "skill":
        return SKILL_LOCAL_CREDENTIALS_PATH
    if target == "repo":
        return Path.cwd() / ".aliyun-mail.env"
    if target == "user":
        return DEFAULT_USER_CREDENTIALS_PATH

    # auto：clone skill 时优先 skill/local，否则 repo 根，最后 user 级
    if (SKILL_DIR / "SKILL.md").is_file():
        return SKILL_LOCAL_CREDENTIALS_PATH
    if (Path.cwd() / ".git").exists():
        return Path.cwd() / ".aliyun-mail.env"
    return DEFAULT_USER_CREDENTIALS_PATH


def find_existing_credential_files() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in default_env_file_candidates():
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
                "user": mask_user_email(values.get("ALIYUN_MAIL_USER", ""))
                if values.get("ALIYUN_MAIL_USER")
                else None,
                "passwordSet": bool(values.get("ALIYUN_MAIL_PASSWORD", "").strip()),
                "host": values.get("ALIYUN_MAIL_IMAP_HOST", DEFAULT_IMAP_HOST),
            }
        )
    return found


def get_setup_status() -> dict[str, Any]:
    bootstrap = bootstrap_env()
    snapshot = config_snapshot()
    existing_files = find_existing_credential_files()
    recommended = resolve_setup_target("auto")
    configured = bool(os.environ.get("ALIYUN_MAIL_USER", "").strip()) and bool(
        os.environ.get("ALIYUN_MAIL_PASSWORD", "").strip()
    )

    missing_fields = []
    for field in SETUP_FIELDS:
        key = field["key"]
        if not field.get("required"):
            continue
        if key == "ALIYUN_MAIL_USER" and not os.environ.get(key, "").strip():
            missing_fields.append(field)
        elif key == "ALIYUN_MAIL_PASSWORD" and not os.environ.get(key, "").strip():
            missing_fields.append(field)

    return {
        "configured": configured,
        "configSnapshot": snapshot,
        "bootstrap": bootstrap,
        "existingCredentialFiles": existing_files,
        "recommendedWritePath": str(recommended.expanduser()),
        "recommendedTarget": "auto",
        "fieldsToCollect": SETUP_FIELDS,
        "missingRequiredFields": missing_fields,
        "needsSetup": not configured,
        "agentProtocol": {
            "reference": "references/onboarding-flow.md",
            "steps": [
                "运行 setup status，确认 needsSetup 为 true",
                "按 fieldsToCollect 向用户逐项提问（secret 字段勿写入日志/代码/提交）",
                "用户给齐信息后运行 setup apply 写入 recommendedWritePath",
                "运行 doctor --env-file <写入路径> 验证连通",
                "验证通过后执行 list/read 等读信命令",
            ],
        },
    }


def write_credentials_file(path: Path, values: dict[str, str]) -> dict[str, Any]:
    user = values.get("ALIYUN_MAIL_USER", "").strip()
    password = values.get("ALIYUN_MAIL_PASSWORD", "").strip()
    if not user:
        raise MailConfigError("setup apply 缺少 ALIYUN_MAIL_USER。")
    if not password:
        raise MailConfigError("setup apply 缺少 ALIYUN_MAIL_PASSWORD。")

    payload = {
        "ALIYUN_MAIL_USER": user,
        "ALIYUN_MAIL_PASSWORD": password,
        "ALIYUN_MAIL_IMAP_HOST": values.get("ALIYUN_MAIL_IMAP_HOST", DEFAULT_IMAP_HOST).strip()
        or DEFAULT_IMAP_HOST,
        "ALIYUN_MAIL_IMAP_PORT": values.get("ALIYUN_MAIL_IMAP_PORT", str(DEFAULT_IMAP_PORT)).strip()
        or str(DEFAULT_IMAP_PORT),
    }

    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_credentials_file(payload), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

    return {
        "writtenPath": str(path.resolve()),
        "user": mask_user_email(user),
        "host": payload["ALIYUN_MAIL_IMAP_HOST"],
        "port": payload["ALIYUN_MAIL_IMAP_PORT"],
        "permissions": oct(path.stat().st_mode & 0o777),
    }


def run_setup_apply(
    *,
    user: str,
    password: str,
    host: str | None = None,
    port: str | None = None,
    target: str = "auto",
    explicit_path: str | None = None,
    verify: bool = False,
) -> dict[str, Any]:
    write_path = resolve_setup_target(target, explicit_path=explicit_path)
    write_result = write_credentials_file(
        write_path,
        {
            "ALIYUN_MAIL_USER": user,
            "ALIYUN_MAIL_PASSWORD": password,
            "ALIYUN_MAIL_IMAP_HOST": host or DEFAULT_IMAP_HOST,
            "ALIYUN_MAIL_IMAP_PORT": port or str(DEFAULT_IMAP_PORT),
        },
    )

    result: dict[str, Any] = {
        "status": "written",
        "target": target,
        "write": write_result,
        "nextSteps": [
            f"python read_mail.py doctor --env-file {write_result['writtenPath']}",
            f"python read_mail.py list --env-file {write_result['writtenPath']} --folder INBOX --limit 10",
        ],
    }

    if verify:
        # 清空相关 env，强制从刚写入的文件验证
        for key in ("ALIYUN_MAIL_USER", "ALIYUN_MAIL_PASSWORD", "ALIYUN_MAIL_IMAP_HOST", "ALIYUN_MAIL_IMAP_PORT"):
            os.environ.pop(key, None)
        doctor = run_doctor(explicit_env_file=write_result["writtenPath"])
        result["verify"] = doctor
        result["status"] = "verified" if doctor["status"] == "ok" else "verify_failed"

    return result
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (email.errors.HeaderParseError, UnicodeError):
        return value


def format_imap_date(dt: datetime) -> str:
    """将 datetime 转为 IMAP SEARCH 可用的 DD-Mon-YYYY。"""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return f"{dt.day:02d}-{months[dt.month - 1]}-{dt.year}"


def parse_message_date(msg: Message) -> str | None:
    date_header = msg.get("Date")
    if not date_header:
        return None
    try:
        parsed = parsedate_to_datetime(date_header)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, IndexError):
        return date_header


def extract_body(msg: Message) -> dict[str, str | None]:
    plain_parts: list[str] = []
    html_parts: list[str] = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disposition:
                continue
            content_type = part.get_content_type()
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError, TypeError):
                continue
            if content_type == "text/plain":
                plain_parts.append(text)
            elif content_type == "text/html":
                html_parts.append(text)
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload is not None:
                charset = msg.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    html_parts.append(text)
                else:
                    plain_parts.append(text)
        except (LookupError, UnicodeDecodeError, TypeError):
            pass

    return {
        "text": "\n".join(plain_parts).strip() or None,
        "html": "\n".join(html_parts).strip() or None,
    }


def extract_attachments(msg: Message) -> list[dict[str, Any]]:
    attachments: list[dict[str, Any]] = []
    for part in msg.walk():
        disposition = (part.get("Content-Disposition") or "").lower()
        filename = part.get_filename()
        if "attachment" not in disposition and not filename:
            continue
        name = decode_mime_words(filename) if filename else "unnamed"
        payload = part.get_payload(decode=True) or b""
        attachments.append(
            {
                "filename": name,
                "contentType": part.get_content_type(),
                "size": len(payload),
            }
        )
    return attachments


def message_to_summary(
    uid: str,
    raw_bytes: bytes,
    flags: list[str] | None = None,
) -> dict[str, Any]:
    msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
    subject = decode_mime_words(msg.get("Subject"))
    from_addr = decode_mime_words(msg.get("From"))
    to_addrs = decode_mime_words(msg.get("To"))
    cc_addrs = decode_mime_words(msg.get("Cc"))
    return {
        "uid": uid,
        "messageId": msg.get("Message-ID"),
        "subject": subject,
        "from": from_addr,
        "to": to_addrs,
        "cc": cc_addrs or None,
        "date": parse_message_date(msg),
        "flags": flags or [],
        "seen": "\\Seen" in (flags or []),
        "attachmentCount": len(extract_attachments(msg)),
    }


def message_to_detail(
    uid: str,
    raw_bytes: bytes,
    flags: list[str] | None = None,
    include_body: bool = True,
) -> dict[str, Any]:
    msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
    detail = message_to_summary(uid, raw_bytes, flags)
    detail["replyTo"] = decode_mime_words(msg.get("Reply-To")) or None
    detail["attachments"] = extract_attachments(msg)
    if include_body:
        detail["body"] = extract_body(msg)
    return detail


def select_folder(mail: imaplib.IMAP4_SSL, folder: str) -> dict[str, Any]:
    status, data = mail.select(f'"{folder}"' if " " in folder else folder, readonly=True)
    if status != "OK":
        raise MailConnectionError(f"无法打开文件夹 {folder!r}: {status} {data!r}")
    count = int(data[0]) if data and data[0] else 0
    return {"folder": folder, "messageCount": count}


def list_folders(mail: imaplib.IMAP4_SSL) -> list[dict[str, Any]]:
    status, data = mail.list()
    if status != "OK" or not data:
        raise MailConnectionError(f"LIST 失败: {status} {data!r}")

    folders: list[dict[str, Any]] = []
    pattern = re.compile(
        r'\((?P<flags>[^)]*)\)\s+"?(?P<delimiter>[^"]*)"?\s+(?P<name>.+)$'
    )
    for raw in data:
        line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
        match = pattern.match(line)
        if not match:
            folders.append({"raw": line})
            continue
        name = match.group("name").strip().strip('"')
        folders.append(
            {
                "name": name,
                "flags": match.group("flags").split(),
                "delimiter": match.group("delimiter"),
            }
        )
    return folders


def search_uids(
    mail: imaplib.IMAP4_SSL,
    *,
    unread_only: bool = False,
    since: datetime | None = None,
    before: datetime | None = None,
    subject_contains: str | None = None,
    from_contains: str | None = None,
    custom_criteria: str | None = None,
) -> list[str]:
    criteria: list[str] = []
    if custom_criteria:
        criteria.append(custom_criteria)
    else:
        criteria.append("ALL")
        if unread_only:
            criteria.append("UNSEEN")
        if since is not None:
            criteria.append(f"SINCE {format_imap_date(since)}")
        if before is not None:
            criteria.append(f"BEFORE {format_imap_date(before)}")
        if subject_contains:
            criteria.append(f'SUBJECT "{subject_contains}"')
        if from_contains:
            criteria.append(f'FROM "{from_contains}"')

    query = " ".join(criteria) if len(criteria) > 1 else criteria[0]
    status, data = mail.uid("search", None, query)
    if status != "OK":
        raise MailConnectionError(f"SEARCH 失败: {status} {data!r}")
    if not data or not data[0]:
        return []
    return [uid.decode("ascii") for uid in data[0].split()]


def fetch_messages(
    mail: imaplib.IMAP4_SSL,
    uids: list[str],
    *,
    include_body: bool = False,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for uid in uids:
        status, fetched = mail.uid(
            "fetch",
            uid,
            "(FLAGS BODY.PEEK[])" if include_body else "(FLAGS BODY.PEEK[HEADER])",
        )
        if status != "OK" or not fetched or fetched[0] is None:
            continue
        raw_item = fetched[0]
        if not isinstance(raw_item, tuple) or len(raw_item) < 2:
            continue
        meta = raw_item[0].decode("utf-8", errors="replace")
        raw_bytes = raw_item[1]
        flags_match = re.search(r"FLAGS \(([^)]*)\)", meta)
        flags = flags_match.group(1).split() if flags_match else []
        if include_body:
            results.append(message_to_detail(uid, raw_bytes, flags, include_body=True))
        else:
            results.append(message_to_summary(uid, raw_bytes, flags))
    return results


def connect(config: MailConfig | None = None) -> imaplib.IMAP4_SSL:
    cfg = config or MailConfig.from_env()
    context = ssl.create_default_context()
    try:
        mail = imaplib.IMAP4_SSL(cfg.host, cfg.port, ssl_context=context)
        mail.login(cfg.user, cfg.password)
    except imaplib.IMAP4.error as exc:
        raise MailConnectionError(
            "IMAP 登录失败。请确认：1) 管理员已允许三方客户端；"
            "2) 使用完整邮箱地址；3) 密码或客户端授权密码正确。"
            f" 原始错误: {exc}"
        ) from exc
    except OSError as exc:
        raise MailConnectionError(
            f"无法连接 {cfg.host}:{cfg.port}。请检查网络与 IMAP 主机配置。"
            f" 原始错误: {exc}"
        ) from exc
    return mail


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
