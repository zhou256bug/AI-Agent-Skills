"""通用 IMAP 读信库（仅标准库）。阿里企业邮等仅支持 UNSEEN/ALL/SINCE 单条件搜索。"""

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
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Any

import inbox_watch_config as cfg


class ImapConfigError(ValueError):
    pass


class ImapConnectionError(RuntimeError):
    pass


@dataclass
class ImapConfig:
    host: str
    port: int
    user: str
    password: str

    @classmethod
    def from_env(cls) -> ImapConfig:
        if not cfg.IMAP_USER:
            raise ImapConfigError("缺少 INBOX_WATCH_IMAP_USER（完整邮箱地址）。")
        if not cfg.IMAP_PASSWORD:
            raise ImapConfigError("缺少 INBOX_WATCH_IMAP_PASSWORD（密码或授权码）。")
        return cls(
            host=cfg.IMAP_HOST,
            port=cfg.IMAP_PORT,
            user=cfg.IMAP_USER,
            password=cfg.IMAP_PASSWORD,
        )


def decode_mime_words(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (email.errors.HeaderParseError, UnicodeError):
        return value


def parse_env_line(line: str) -> tuple[str, str] | None:
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
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(line)
        if parsed:
            values[parsed[0]] = parsed[1]
    return values


def apply_env_values(values: dict[str, str], *, override: bool = False) -> list[str]:
    applied: list[str] = []
    for key, value in values.items():
        if not override and os.environ.get(key, "").strip():
            continue
        os.environ[key] = value
        applied.append(key)
    return applied


def env_file_candidates() -> list[Path]:
    return [
        Path.cwd() / ".inbox-watch.env",
        cfg.SKILL_ROOT / "local" / "credentials.env",
        Path.home() / ".config" / "inbox-watch" / "credentials.env",
    ]


def bootstrap_env(*, explicit_env_file: str | None = None) -> dict[str, Any]:
    candidates: list[Path] = []
    if explicit_env_file:
        candidates.append(Path(explicit_env_file).expanduser())
    candidates.extend(env_file_candidates())
    loaded: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path.expanduser())
        if key in seen:
            continue
        seen.add(key)
        expanded = path.expanduser()
        if not expanded.is_file():
            continue
        applied = apply_env_values(read_env_file(expanded), override=False)
        if applied:
            loaded.append({"path": str(expanded.resolve()), "keys": applied})
    return {"loadedFrom": loaded, "checkedPaths": [str(p.expanduser()) for p in candidates]}


def connect(config: ImapConfig | None = None) -> imaplib.IMAP4_SSL:
    c = config or ImapConfig.from_env()
    context = ssl.create_default_context()
    try:
        mail = imaplib.IMAP4_SSL(c.host, c.port, ssl_context=context)
        mail.login(c.user, c.password)
    except imaplib.IMAP4.error as exc:
        raise ImapConnectionError(
            f"IMAP 登录失败：请确认账号、授权码与三方客户端已开启。原始错误: {exc}"
        ) from exc
    except OSError as exc:
        raise ImapConnectionError(f"无法连接 {c.host}:{c.port}：{exc}") from exc
    return mail


def select_inbox(mail: imaplib.IMAP4_SSL, folder: str = "INBOX") -> int:
    status, data = mail.select(f'"{folder}"' if " " in folder else folder, readonly=True)
    if status != "OK":
        raise ImapConnectionError(f"无法打开文件夹 {folder!r}: {status}")
    return int(data[0]) if data and data[0] else 0


def search_unseen_uids(mail: imaplib.IMAP4_SSL, *, limit: int | None = None) -> list[str]:
    """仅 UNSEEN 搜索（阿里企业邮不支持多条件组合 SEARCH）。"""
    status, data = mail.uid("search", None, "UNSEEN")
    if status != "OK":
        raise ImapConnectionError(f"UNSEEN SEARCH 失败: {status} {data!r}")
    if not data or not data[0]:
        return []
    uids = [u.decode("ascii") for u in data[0].split()]
    cap = limit or cfg.UNSEEN_LIMIT
    return uids[-cap:] if len(uids) > cap else uids


def search_all_uids(mail: imaplib.IMAP4_SSL, *, limit: int = 50) -> list[str]:
    status, data = mail.uid("search", None, "ALL")
    if status != "OK":
        raise ImapConnectionError(f"ALL SEARCH 失败: {status}")
    if not data or not data[0]:
        return []
    uids = [u.decode("ascii") for u in data[0].split()]
    return uids[-limit:] if len(uids) > limit else uids


def fetch_raw(mail: imaplib.IMAP4_SSL, uid: str, *, peek_body: bool = True) -> bytes:
    item = "(BODY.PEEK[])" if peek_body else "(BODY[])"
    status, fetched = mail.uid("fetch", uid, item)
    if status != "OK" or not fetched or fetched[0] is None:
        raise ImapConnectionError(f"FETCH uid={uid} 失败")
    raw_item = fetched[0]
    if not isinstance(raw_item, tuple) or len(raw_item) < 2:
        raise ImapConnectionError(f"FETCH uid={uid} 响应异常")
    return raw_item[1]


def parse_sender_parts(from_header: str) -> tuple[str, str]:
    name, addr = parseaddr(from_header)
    display = decode_mime_words(name) if name else addr
    if display and addr and display != addr:
        sender = f"{display} <{addr}>"
    else:
        sender = addr or display or ""
    return sender, (addr or "").lower()


def parse_message_date(msg: Message) -> str:
    date_header = msg.get("Date")
    if not date_header:
        return ""
    try:
        parsed = parsedate_to_datetime(date_header)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        local = parsed.astimezone()
        return local.strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, IndexError):
        return decode_mime_words(date_header)


def extract_body_text(msg: Message) -> str:
    plain: list[str] = []
    html: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disposition:
                continue
            ctype = part.get_content_type()
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError, TypeError):
                continue
            if ctype == "text/plain":
                plain.append(text)
            elif ctype == "text/html":
                html.append(text)
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload is not None:
                charset = msg.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    html.append(text)
                else:
                    plain.append(text)
        except (LookupError, UnicodeDecodeError, TypeError):
            pass
    body = "\n".join(plain).strip() or "\n".join(html).strip()
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def extract_attachment_names(msg: Message) -> list[str]:
    names: list[str] = []
    for part in msg.walk():
        disposition = (part.get("Content-Disposition") or "").lower()
        filename = part.get_filename()
        if "attachment" in disposition or filename:
            names.append(decode_mime_words(filename) if filename else "unnamed")
    return names


def save_attachments(msg: Message, dest_dir: Path, *, uid: str) -> list[str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for part in msg.walk():
        disposition = (part.get("Content-Disposition") or "").lower()
        filename = part.get_filename()
        if "attachment" not in disposition and not filename:
            continue
        name = decode_mime_words(filename) if filename else f"attachment_{uid}"
        safe = re.sub(r'[\\/:*?"<>|]+', "_", name)
        path = dest_dir / safe
        payload = part.get_payload(decode=True) or b""
        path.write_bytes(payload)
        saved.append(str(path))
    return saved


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_system_patterns() -> list[str]:
    data = load_json(cfg.SYSTEM_PATTERNS_PATH)
    return [p.lower() for p in data.get("patterns", [])]


def load_watchlist() -> list[dict[str, Any]]:
    data = load_json(cfg.WATCHLIST_PATH)
    return data.get("contacts", [])


def is_system_sender(sender: str, sender_raw: str, patterns: list[str]) -> bool:
    hay = f"{sender} {sender_raw}".lower()
    return any(p in hay for p in patterns)


def match_watchlist(sender: str, sender_raw: str, contacts: list[dict[str, Any]]) -> dict[str, Any] | None:
    hay = f"{sender} {sender_raw}".lower()
    for contact in contacts:
        for pattern in contact.get("email_patterns", []):
            if pattern.lower() in hay:
                return contact
    return None


def summarize_email(uid: str, raw: bytes, *, preview_chars: int | None = None) -> dict[str, Any]:
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    from_hdr = decode_mime_words(msg.get("From"))
    sender, sender_raw = parse_sender_parts(from_hdr)
    subject = decode_mime_words(msg.get("Subject")) or "(无主题)"
    patterns = load_system_patterns()
    contacts = load_watchlist()
    is_system = is_system_sender(sender, sender_raw, patterns)
    known = match_watchlist(sender, sender_raw, contacts)
    body = extract_body_text(msg)
    limit = preview_chars or cfg.BODY_PREVIEW_CHARS
    preview = body[:limit] if body else ""
    attachments = extract_attachment_names(msg)
    return {
        "uid": uid,
        "sender": sender,
        "sender_raw": sender_raw,
        "date": parse_message_date(msg),
        "subject": subject,
        "is_system": is_system,
        "is_known": known is not None,
        "watch_contact": known,
        "attachments": attachments,
        "body_preview": preview,
        "body_full": body,
        "message_id": msg.get("Message-ID"),
    }


def format_check_unseen_line(key: str, value: str | int | bool) -> str:
    if isinstance(value, bool):
        return f"{key}:{str(value)}"
    return f"{key}:{value}"


def format_check_unseen_output(emails: list[dict[str, Any]], *, total_unseen: int) -> str:
    personal = [e for e in emails if not e["is_system"]]
    lines = [
        f"TOTAL_UNSEEN:{total_unseen}",
        f"PERSONAL_UNSEEN:{len(personal)}",
    ]
    for e in emails:
        lines.append("---EMAIL---")
        lines.append(format_check_unseen_line("UID", e["uid"]))
        lines.append(format_check_unseen_line("SENDER", e["sender"]))
        lines.append(format_check_unseen_line("SENDER_RAW", e["sender_raw"]))
        lines.append(format_check_unseen_line("DATE", e["date"]))
        lines.append(format_check_unseen_line("SUBJECT", e["subject"]))
        lines.append(format_check_unseen_line("IS_SYSTEM", e["is_system"]))
        lines.append(format_check_unseen_line("IS_KNOWN", e["is_known"]))
        if e.get("watch_contact"):
            wc = e["watch_contact"]
            lines.append(format_check_unseen_line("WATCH_ACTION", wc.get("action", "")))
            lines.append(format_check_unseen_line("WATCH_NAME", wc.get("name", "")))
        att = ",".join(e["attachments"]) if e["attachments"] else ""
        lines.append(format_check_unseen_line("ATTACHMENTS", att))
        lines.append(format_check_unseen_line("BODY_PREVIEW", e["body_preview"]))
    return "\n".join(lines) + "\n"


def scan_unseen(*, folder: str = "INBOX", limit: int | None = None) -> dict[str, Any]:
    mail = connect()
    try:
        select_inbox(mail, folder)
        uids = search_unseen_uids(mail, limit=limit)
        total = len(uids)
        emails: list[dict[str, Any]] = []
        for uid in uids:
            raw = fetch_raw(mail, uid)
            emails.append(summarize_email(uid, raw))
        personal = [e for e in emails if not e["is_system"]]
        return {
            "total_unseen": total,
            "personal_unseen": len(personal),
            "emails": emails,
            "text": format_check_unseen_output(emails, total_unseen=total),
        }
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def read_by_uid(uid: str, *, folder: str = "INBOX") -> dict[str, Any]:
    mail = connect()
    try:
        select_inbox(mail, folder)
        raw = fetch_raw(mail, uid)
        detail = summarize_email(uid, raw, preview_chars=100000)
        return detail
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def read_match(
    *,
    sender_contains: str | None = None,
    subject_contains: str | None = None,
    folder: str = "INBOX",
    limit: int = 20,
    unseen_only: bool = False,
) -> list[dict[str, Any]]:
    """Python 侧过滤（避免 IMAP 中文/多条件 SEARCH 陷阱）。"""
    mail = connect()
    try:
        select_inbox(mail, folder)
        uids = search_unseen_uids(mail, limit=limit) if unseen_only else search_all_uids(mail, limit=limit)
        matched: list[dict[str, Any]] = []
        for uid in reversed(uids):
            raw = fetch_raw(mail, uid)
            item = summarize_email(uid, raw, preview_chars=100000)
            hay_sender = f"{item['sender']} {item['sender_raw']}".lower()
            hay_subject = item["subject"].lower()
            if sender_contains and sender_contains.lower() not in hay_sender:
                continue
            if subject_contains and subject_contains.lower() not in hay_subject:
                continue
            matched.append(item)
        return matched
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def attachments_match(
    *,
    sender_contains: str | None = None,
    subject_contains: str | None = None,
    folder: str = "INBOX",
    limit: int = 10,
    dest_dir: Path | None = None,
) -> list[dict[str, Any]]:
    mail = connect()
    dest = dest_dir or cfg.attachment_archive_dir()
    results: list[dict[str, Any]] = []
    try:
        select_inbox(mail, folder)
        uids = search_unseen_uids(mail, limit=limit)
        for uid in reversed(uids):
            raw = fetch_raw(mail, uid)
            msg = email.message_from_bytes(raw, policy=email.policy.default)
            from_hdr = decode_mime_words(msg.get("From"))
            sender, sender_raw = parse_sender_parts(from_hdr)
            subject = decode_mime_words(msg.get("Subject")) or ""
            hay_sender = f"{sender} {sender_raw}".lower()
            if sender_contains and sender_contains.lower() not in hay_sender:
                continue
            if subject_contains and subject_contains.lower() not in subject:
                continue
            subdir = dest / f"{uid}_{re.sub(r'[\\\\/:*?\"<>|]+', '_', subject)[:40]}"
            saved = save_attachments(msg, subdir, uid=uid)
            results.append(
                {
                    "uid": uid,
                    "sender": sender,
                    "subject": subject,
                    "saved_paths": saved,
                }
            )
        return results
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass
