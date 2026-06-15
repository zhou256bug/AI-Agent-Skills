"""关注人列表读写（data/watchlist.json）。"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import inbox_watch_config as cfg

VALID_ACTIONS = ("read_full", "read_attachments", "report_promptly")
VALID_PRIORITIES = ("high", "medium", "low")


def watchlist_path() -> Path:
    override = os.environ.get("INBOX_WATCH_WATCHLIST_FILE", "").strip()
    if override:
        return Path(override).expanduser()
    return cfg.WATCHLIST_PATH


def load_watchlist() -> dict[str, Any]:
    path = watchlist_path()
    if not path.is_file():
        return {"version": "1.0.0", "description": "", "contacts": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_watchlist(data: dict[str, Any]) -> Path:
    path = watchlist_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def slugify(name: str, email: str) -> str:
    local = email.split("@", 1)[0].lower()
    safe = re.sub(r"[^a-z0-9]+", "-", local).strip("-")
    return safe or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "contact"


def list_contacts() -> list[dict[str, Any]]:
    return load_watchlist().get("contacts", [])


def find_by_id_or_email(target: str) -> dict[str, Any] | None:
    target_l = target.lower()
    for c in list_contacts():
        if c.get("id", "").lower() == target_l:
            return c
        for pat in c.get("email_patterns", []):
            if target_l in pat.lower() or pat.lower() in target_l:
                return c
    return None


def add_contact(
    *,
    name: str,
    email: str,
    role: str = "关注联系人",
    action: str = "report_promptly",
    priority: str = "medium",
    note: str = "",
    contact_id: str | None = None,
) -> dict[str, Any]:
    if action not in VALID_ACTIONS:
        raise ValueError(f"action 必须是 {VALID_ACTIONS} 之一")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"priority 必须是 {VALID_PRIORITIES} 之一")
    if "@" not in email:
        raise ValueError("email 须为完整邮箱地址")

    data = load_watchlist()
    contacts = data.setdefault("contacts", [])
    cid = contact_id or slugify(name, email)

    for existing in contacts:
        if existing.get("id") == cid:
            raise ValueError(f"已存在 id={cid}，请用 remove 后重加或换 id")
        for pat in existing.get("email_patterns", []):
            if email.lower() == pat.lower():
                raise ValueError(f"邮箱已在关注列表：{existing.get('name')}")

    entry = {
        "id": cid,
        "name": name,
        "email_patterns": [email.lower()],
        "role": role,
        "action": action,
        "priority": priority,
        "note": note or "用户通过 Agent 添加",
    }
    contacts.append(entry)
    save_watchlist(data)
    return entry


def remove_contact(target: str) -> dict[str, Any]:
    data = load_watchlist()
    contacts = data.get("contacts", [])
    removed: dict[str, Any] | None = None
    remaining: list[dict[str, Any]] = []
    target_l = target.lower()
    for c in contacts:
        match = (
            c.get("id", "").lower() == target_l
            or c.get("name", "").lower() == target_l
            or any(target_l in p.lower() or p.lower() in target_l for p in c.get("email_patterns", []))
        )
        if match and removed is None:
            removed = c
        else:
            remaining.append(c)
    if removed is None:
        raise ValueError(f"未找到关注人：{target}")
    data["contacts"] = remaining
    save_watchlist(data)
    return removed
