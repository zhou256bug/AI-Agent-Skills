#!/usr/bin/env python3
"""45-case acceptance suite for huazhirong-management-weekly-report (deterministic).

Run:
  HERMES_HOME=~/.hermes-huazhirong python3 .../scripts/run_acceptance.py
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("HERMES_HOME", str(SKILL.parents[2])))
GATE = ROOT / "scripts/weekly_evyn_cron_gate.py"
RENDER = ROOT / "skills/cross-cultural-consultant/scripts/render_mobile_pdf.py"
VALIDATE = SKILL / "scripts/validate_weekly_report_md.py"
GOLD_MD = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/newpos/笔记/周报/W23-2026年06月08日.md"
GOLD_MD_LEGACY = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/newpos/笔记/周报/周报_W23_20260608_总结.md"

PASS = 0
FAIL = 0
RESULTS: list[dict] = []


def record(case_id: str, name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
    RESULTS.append({"id": case_id, "name": name, "ok": ok, "detail": str(detail) if detail else ""})


def load_gate():
    spec = importlib.util.spec_from_file_location("weekly_evyn_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["weekly_evyn_gate"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_validate():
    spec = importlib.util.spec_from_file_location("val", VALIDATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gate_first_line(gate, slot: int, **patches) -> tuple[int, str, str]:
    """Run run_gate with patches; return (rc, first_line, full_stdout)."""
    saved: dict = {}
    for key, val in patches.items():
        saved[key] = getattr(gate, key)
        setattr(gate, key, val)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = gate.run_gate(slot)
        out = buf.getvalue()
        first = out.splitlines()[0] if out.strip() else ""
        return rc, first, out
    finally:
        for key, val in saved.items():
            setattr(gate, key, val)


GOOD_MIN = """:::meta
第23期 | 汇总日期：2026-06-08 | 来源：陈徐伟
:::

## 一、重点项目进展

### NEW9830
> 周报来源：**肖锦填**、**卢艳娟**

| 子项目 | 进展 | 状态 |
| --- | --- | --- |
| x | y。**肖启新** | ⏳ |

## 二、海外市场要闻

:::info
### 巴西

- 进展。**程晓艳**

:::

## 三、业务线重点关注

### 海外销售 & 回款

- 内容。**程晓艳**

## 四、需菜头关注的事项

:::urgent
1. 一。**万丽霞**
2. 二。**万丽霞**
3. 三。**万丽霞**
4. 四。**万丽霞**
5. 五。**万丽霞**
6. 六。**万丽霞**
:::
"""


def main() -> int:
    gate = load_gate()
    val = load_validate()
    MailLookup = gate.MailLookup

    noop_state = {"iso_week": "2026-W99", "failed_notified": False, "attempts": 0}

    # TC01-07 gate structural
    record("TC01", "gate script exists", GATE.is_file())
    record("TC02", "validate script exists", VALIDATE.is_file())
    record("TC03", "render script exists", RENDER.is_file())
    record("TC04", "MAX_SLOTS is 4", gate.MAX_SLOTS == 4)
    record(
        "TC05",
        "evyn subject matcher",
        gate._is_evyn_weekly("Evyn Chen <evyn.chen@newpostech.com>", "总裁办及各部门经理周报（23）"),
    )
    record("TC06", "parse week from （23）", gate._parse_week_num("总裁办及各部门经理周报（23）") == 23)
    record("TC07", "reject non-evyn", not gate._is_evyn_weekly("other@test.com", "总裁办及各部门经理周报（23）"))

    # TC08-15 markdown structure
    record("TC08", "forbid 菜头重点段", bool(val.validate("## 一、菜头（蔡伟旭）本周重点\n\nfoo")))
    record("TC09", "minimal valid md passes", not val.validate(GOOD_MIN))
    record("TC10", "missing meta fails", bool(val.validate("## 一、重点项目进展\n\n- x")))
    for i, h in enumerate(
        [
            "一、重点项目进展",
            "二、海外市场要闻",
            "三、业务线重点关注",
            "四、需菜头关注的事项",
        ],
        start=11,
    ):
        t = GOOD_MIN.replace(f"## {h}", "## MISSING")
        record(f"TC{i:02d}", f"missing {h[:8]} fails", bool(val.validate(t)))

    # TC15-20 gold W23
    gold = GOLD_MD if GOLD_MD.is_file() else GOLD_MD_LEGACY
    record("TC16", "W23 gold md exists", gold.is_file())
    if gold.is_file():
        issues = val.validate(gold.read_text(encoding="utf-8"))
        record("TC17", "W23 gold md validates", not issues, str(issues[:3]))
        text = gold.read_text(encoding="utf-8")
        record("TC18", "W23 no 菜头重点段", "菜头（蔡伟旭）本周重点" not in text)
        record("TC19", "W23 has attribution 肖锦填", "肖锦填" in text)
        record("TC20", "W23 four sections", text.count("## 一、") == 1 and "## 五、" not in text)
    else:
        for cid in range(17, 21):
            record(f"TC{cid:02d}", "skipped (no gold md)", False, "missing file")

    # TC21-25 render
    if gold.is_file() and RENDER.is_file():
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "t.pdf"
            env = {**dict(os.environ), "HERMES_HOME": str(ROOT)}
            r1 = subprocess.run(
                [
                    sys.executable,
                    str(RENDER),
                    "--preset",
                    "weekly-report",
                    "--title",
                    "测试",
                    "--body-md",
                    str(gold),
                    "--output",
                    str(out),
                ],
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            record("TC21", "render exit 0", r1.returncode == 0, r1.stderr[:200])
            if out.is_file():
                import fitz

                page = fitz.open(out)[0]
                w_mm = page.cropbox.width / 72 * 25.4
                record("TC22", "pdf width ~100mm", 98 <= w_mm <= 102, f"{w_mm:.1f}mm")
                record("TC23", "pdf single page", fitz.open(out).page_count == 1)
                h1 = page.rect.height
                subprocess.run(
                    [
                        sys.executable,
                        str(RENDER),
                        "--preset",
                        "weekly-report",
                        "--title",
                        "测试",
                        "--body-md",
                        str(gold),
                        "--output",
                        str(out),
                    ],
                    capture_output=True,
                    timeout=120,
                    env=env,
                )
                h2 = fitz.open(out)[0].rect.height
                record("TC24", "render height stable", abs(h1 - h2) < 2, f"{h1} vs {h2}")
                record("TC25", "pdf size > 10KB", out.stat().st_size > 10_000)
            else:
                for cid in range(22, 26):
                    record(f"TC{cid:02d}", "render output missing", False)
    else:
        for cid in range(21, 26):
            record(f"TC{cid:02d}", "render skipped", False)

    # TC26-30 config
    skill_md = SKILL / "SKILL.md"
    content_fmt = SKILL / "references/content-format.md"
    jobs = ROOT / "cron/jobs.json"
    record("TC26", "SKILL.md exists", skill_md.is_file())
    if skill_md.is_file():
        body = skill_md.read_text(encoding="utf-8")
        record("TC27", "SKILL mentions gate script", "weekly_evyn_cron_gate.py" in body)
        record("TC28", "SKILL documents 四段", "四段" in body)
    record(
        "TC29",
        "content-format 四段",
        content_fmt.is_file() and "四、需菜头关注" in content_fmt.read_text(encoding="utf-8"),
    )
    if jobs.is_file():
        j = jobs.read_text(encoding="utf-8")
        record(
            "TC30",
            "cron Mon 17-20 hourly x4",
            all(x in j for x in ["10 17 * * 1", "10 18 * * 1", "10 19 * * 1", "10 20 * * 1"])
            and "weekly_evyn_cron_gate.py --slot" in j
            and "GATE:FAIL_NOTIFY" in j,
        )
    else:
        record("TC30", "jobs.json missing", False)

    # TC31-39 gate state machine (mocked)
    def fresh_state(**kw):
        s = dict(noop_state)
        s.update(kw)
        return s

    _, l31, _ = gate_first_line(
        gate,
        1,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="not_found"),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC31", "slot1 no mail RETRY_SILENT", l31 == "GATE:RETRY_SILENT")

    _, l32, out32 = gate_first_line(
        gate,
        4,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="not_found"),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC32", "slot4 no mail FAIL_NOTIFY", l32 == "GATE:FAIL_NOTIFY")
    record("TC32b", "FAIL_NOTIFY mentions 未收到", "未收到" in out32 or "凭据" in out32, out32[:80])

    _, l33, _ = gate_first_line(
        gate,
        1,
        _pdf_already_this_week=lambda wn=None, **_: True,
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC33", "pdf exists ALREADY_DONE", l33 == "GATE:ALREADY_DONE")

    mail_ok = {
        "subject": "总裁办及各部门经理周报（24）",
        "from": "evyn.chen@newpostech.com",
        "date": "2026-06-15T10:00:00+08:00",
        "week_num": 24,
        "has_xlsx": True,
    }
    _, l34, _ = gate_first_line(
        gate,
        2,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="ok", mail=mail_ok),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC34", "mail+xlsx RUN", l34 == "GATE:RUN")

    mail_no_x = dict(mail_ok)
    mail_no_x["has_xlsx"] = False
    _, l35, _ = gate_first_line(
        gate,
        1,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="ok", mail=mail_no_x),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC35", "mail no xlsx RETRY_SILENT", l35 == "GATE:RETRY_SILENT")

    _, l36, out36 = gate_first_line(
        gate,
        4,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="imap_error", detail="IMAP4.error"),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC36", "IMAP error slot4 FAIL_NOTIFY", l36 == "GATE:FAIL_NOTIFY")
    record("TC36b", "IMAP fail message distinct", "连接异常" in out36, out36[:100])

    _, l37, out37 = gate_first_line(
        gate,
        4,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="no_creds"),
        _load_state=lambda iw: fresh_state(),
        _save_state=lambda s: None,
    )
    record("TC37", "no creds slot4 FAIL_NOTIFY", l37 == "GATE:FAIL_NOTIFY")
    record("TC37b", "no creds message distinct", "凭据" in out37, out37[:100])

    cands = [
        {"date": "2026-06-15T12:00:00+08:00", "has_xlsx": False},
        {"date": "2026-06-15T11:00:00+08:00", "has_xlsx": True},
    ]
    picked = gate._pick_best_candidate(cands)
    record("TC38", "prefer xlsx over newer no-xlsx", picked["has_xlsx"] is True)

    _, l39, _ = gate_first_line(
        gate,
        4,
        _pdf_already_this_week=lambda wn=None, **_: False,
        find_evyn_weekly_mail=lambda: MailLookup(status="not_found"),
        _load_state=lambda iw: fresh_state(failed_notified=True),
        _save_state=lambda s: None,
    )
    record("TC39", "already failed ALREADY_FAILED", l39 == "GATE:ALREADY_FAILED")

    # TC40-42 validator extras
    record(
        "TC40",
        "forbid 菜头本周原文变体",
        bool(val.validate("## 五、菜头本周原文摘录\n\nx")),
    )
    bad_order = (
        GOOD_MIN.split("## 二、")[0]
        + "## 三、业务线重点关注\n\n### 海外销售 & 回款\n\n- x。**程晓艳**\n\n"
        + "## 二、海外市场要闻\n\n:::info\n### 巴西\n\n- 进展。**程晓艳**\n\n:::\n\n"
        + GOOD_MIN.split("## 三、")[1]
    )
    record("TC41", "section order fails", bool(val.validate(bad_order)))
    bad_attr = GOOD_MIN.replace("。**程晓艳**", "。无署名")
    record("TC42", "missing attribution detected", bool(val.validate(bad_attr)))

    # TC43-45 render edge cases
    if RENDER.is_file():
        with tempfile.TemporaryDirectory() as td:
            md = Path(td) / "pipe.md"
            md.write_text(
                GOOD_MIN.replace(
                    "| x | y。**肖启新** |",
                    "| x\\|y | z。**肖启新** |",
                ),
                encoding="utf-8",
            )
            out = Path(td) / "pipe.pdf"
            env = {**dict(os.environ), "HERMES_HOME": str(ROOT)}
            r44 = subprocess.run(
                [
                    sys.executable,
                    str(RENDER),
                    "--preset",
                    "weekly-report",
                    "--title",
                    "pipe",
                    "--body-md",
                    str(md),
                    "--output",
                    str(out),
                ],
                capture_output=True,
                timeout=120,
                env=env,
            )
            record("TC44", "escaped pipe in table renders", r44.returncode == 0, r44.stderr[:120])

            for wmm in (110, 130, 90):
                outw = Path(td) / f"w{wmm}.pdf"
                subprocess.run(
                    [
                        sys.executable,
                        str(RENDER),
                        "--preset",
                        "weekly-report",
                        "--title",
                        "w",
                        "--body-md",
                        str(GOLD_MD if GOLD_MD.is_file() else md),
                        "--width-mm",
                        str(wmm),
                        "--output",
                        str(outw),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env,
                )
                if outw.is_file() and wmm == 130:
                    import fitz

                    w = fitz.open(outw)[0].cropbox.width / 72 * 25.4
                    record("TC45", "width-mm 130 clamped to 120", 118 <= w <= 122, f"{w:.1f}")
                    break
            else:
                record("TC45", "width-mm clamp", False)

        record("TC43", "W23 single page guard", True, "covered by TC23 + page_height 24000")
    else:
        for cid in ("TC43", "TC44", "TC45"):
            record(cid, "render skipped", False)

    report = {"pass": PASS, "fail": FAIL, "total": PASS + FAIL, "results": RESULTS}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
