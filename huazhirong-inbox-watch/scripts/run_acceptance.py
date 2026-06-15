#!/usr/bin/env python3
"""inbox-watch 独立验收（纯标准库，无 live IMAP）。"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

PASS = FAIL = SKIP = 0
RESULTS: list[dict] = []


def record(cid: str, name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    PASS += int(ok)
    FAIL += int(not ok)
    RESULTS.append({"id": cid, "ok": ok, "name": name, "detail": detail[:120]})


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    required = [
        "SKILL.md", "evals.json", "README.md", "CHANGELOG.md",
        "data/watchlist.json", "data/system-sender-patterns.json",
        "references/cron-setup.md", "references/agent-cron-prompt.md",
        "references/imap-traps.md", "references/emoji-output-guide.md",
        "references/onboarding-flow.md",
        "scripts/check_unseen.py", "scripts/mail_tool.py",
        "scripts/run_scan.py", "scripts/inbox_watch_cli.py",
        "scripts/inbox_watch_config.py", "scripts/imap_lib.py",
        "references/watchlist-management.md",
        "scripts/watchlist_cli.py", "scripts/deliver_weixin.py",
        "evaluation/run_evals.py",
        "agents/hermes.yaml", "bundles/inbox-watch.hermes.yaml",
    ]
    for rel in required:
        record(f"FS-{rel[:12]}", f"存在 {rel}", (SKILL / rel).is_file())

    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for word in ("delegate_task", "菜头", "大为", "/Users/"):
        hit = any(word in ln for ln in skill_md.splitlines() if "禁止" not in ln)
        record(f"CL-{word[:6]}", f"SKILL 不含 {word}", not hit)

    record("VER01", "version 0.1.1", "version: 0.1.1" in skill_md)
    record("RTE01", "路由含 cron C", "cron" in skill_md.lower() and "check_unseen" in skill_md)
    record("RTE02", "slash inbox-watch", "/inbox-watch" in skill_md or "inbox-watch" in skill_md)
    record("RULE01", "无邮件不可静默", "没有新邮件" in skill_md)

    import inbox_watch_config as cfg  # noqa: E402

    record("CFG01", "默认 OWNER=老板", cfg.OWNER == "老板")
    record("CFG02", "默认 IMAP 阿里", "qiye.aliyun" in cfg.IMAP_HOST)
    record("CFG03", "UNSEEN_LIMIT=50", cfg.UNSEEN_LIMIT == 50)

    imap = _load("imap", "imap_lib.py")
    patterns = imap.load_system_patterns()
    record("DAT01", "系统过滤模式>=20", len(patterns) >= 20)
    contacts = imap.load_watchlist()
    record("DAT02", "关注人>=8", len(contacts) >= 8)

    record("DAT03", "Fernando Alonso 在 watchlist", any("alonso" in str(c).lower() for c in contacts))

    emails = [
        {
            "uid": "1",
            "sender": "Fernando Alonso <f@x.com>",
            "sender_raw": "f@x.com",
            "date": "2026-06-15",
            "subject": "Plan",
            "is_system": False,
            "is_known": True,
            "watch_contact": {"action": "read_full", "name": "Fernando Alonso"},
            "attachments": ["a.xlsx"],
            "body_preview": "Hello",
        }
    ]
    text = imap.format_check_unseen_output(emails, total_unseen=1)
    record("FMT01", "TOTAL_UNSEEN 行", text.startswith("TOTAL_UNSEEN:1"))
    record("FMT02", "---EMAIL--- 块", "---EMAIL---" in text)
    record("FMT03", "WATCH_ACTION", "WATCH_ACTION:read_full" in text)

    record("SYS01", "noreply 判系统", imap.is_system_sender("x", "noreply@co.com", patterns))
    record("SYS02", "真人非系统", not imap.is_system_sender("Fernando", "f@x.com", patterns))

    from run_scan import build_summary_markdown  # noqa: E402

    empty_md = build_summary_markdown({"total_unseen": 0, "personal_unseen": 0, "emails": []})
    record("OUT01", "空邮箱含没有新邮件", "没有新邮件" in empty_md)
    record("OUT02", "空邮箱含 📌", "📌" in empty_md)

    val = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_scan_output.py"), "--sample", "empty"],
        capture_output=True,
        text=True,
    )
    record("VAL01", "validate empty", val.returncode == 0)

    val2 = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_scan_output.py"), "--sample", "has_mail"],
        capture_output=True,
        text=True,
    )
    record("VAL02", "validate has_mail", val2.returncode == 0)

    cli = subprocess.run(
        [sys.executable, str(SCRIPTS / "inbox_watch_cli.py"), "setup", "status"],
        capture_output=True,
        text=True,
        cwd=str(SKILL),
    )
    record("CLI01", "setup status 退出码0", cli.returncode == 0)
    if cli.returncode == 0:
        st = json.loads(cli.stdout)
        record("CLI02", "needsSetup 字段", "needsSetup" in st)
        record("CLI03", "fieldsToCollect", len(st.get("fieldsToCollect", [])) >= 4)

    with tempfile.TemporaryDirectory() as td:
        env = Path(td) / "c.env"
        apply = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "inbox_watch_cli.py"),
                "setup",
                "apply",
                "--imap-user",
                "test@example.com",
                "--imap-password",
                "secret",
                "--owner",
                "测试老板",
                "--target",
                "path",
                "--path",
                str(env),
            ],
            capture_output=True,
            text=True,
            cwd=str(SKILL),
        )
        record("SET01", "setup apply 写文件", env.is_file() and apply.returncode == 0)

    record("DAT04", "charlene 在列表", any("charlene.cheng" in str(c).lower() for c in contacts))

    wl_list = subprocess.run(
        [sys.executable, str(SCRIPTS / "watchlist_cli.py"), "list"],
        capture_output=True,
        text=True,
        cwd=str(SKILL),
    )
    record("WL01", "watchlist list", wl_list.returncode == 0 and "charlene" in wl_list.stdout.lower())

    with tempfile.TemporaryDirectory() as td:
        tmp_wl = Path(td) / "watchlist.json"
        import shutil

        shutil.copy(SKILL / "data" / "watchlist.json", tmp_wl)
        env = {**os.environ, "INBOX_WATCH_WATCHLIST_FILE": str(tmp_wl)}
        add = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "watchlist_cli.py"),
                "add",
                "--name",
                "测试人",
                "--email",
                "test-add@example.com",
            ],
            capture_output=True,
            text=True,
            cwd=str(SKILL),
            env=env,
        )
        record("WL02", "watchlist add", add.returncode == 0)
        rm = subprocess.run(
            [sys.executable, str(SCRIPTS / "watchlist_cli.py"), "remove", "test-add@example.com"],
            capture_output=True,
            text=True,
            cwd=str(SKILL),
            env=env,
        )
        record("WL03", "watchlist remove", rm.returncode == 0)

    evl = subprocess.run(
        [sys.executable, str(SKILL / "evaluation" / "run_evals.py")],
        capture_output=True,
        text=True,
        cwd=str(SKILL),
    )
    record("EVL01", "run_evals OK", evl.returncode == 0, evl.stdout[-80:] if evl.stdout else evl.stderr)

    dry = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_scan.py"), "--no-archive"],
        capture_output=True,
        text=True,
        cwd=str(SKILL),
        env={k: v for k, v in os.environ.items() if not k.startswith("INBOX_WATCH_IMAP")},
    )
    record("SCN01", "run_scan 无凭据返回2", dry.returncode == 2)

    print(f"\n{'ID':<12} {'OK':<5} 用例")
    print("-" * 60)
    for r in RESULTS:
        mark = "✅" if r["ok"] else "❌"
        print(f"{r['id']:<12} {mark:<5} {r['name']}")
    print("-" * 60)
    print(f"PASS={PASS}  FAIL={FAIL}  SKIP={SKIP}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
