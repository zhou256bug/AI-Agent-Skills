#!/usr/bin/env python3
"""管理团队周报技能 · 独立验收套件（平台无关，纯标准库可跑）。

设计原则（按"必须独立跑通"要求）：
- 不依赖 `$HERMES_HOME`、cron gate、iCloud 归档或外部渲染器；
- 渲染相关用例仅在本机装了 weasyprint + PyMuPDF 时执行，否则记为 SKIP（不算失败）；
- 用例围绕本技能的确定性核心：validator / transform / paths / config。

用法：
    python3 scripts/run_acceptance.py
退出码：有 FAIL → 1；否则 0（SKIP 不影响退出码）。
"""

from __future__ import annotations

import email
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from email.message import EmailMessage
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import weekly_report_config as cfg  # noqa: E402

PASS = 0
FAIL = 0
SKIP = 0
RESULTS: list[dict] = []


def record(case_id: str, name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
    RESULTS.append({"id": case_id, "name": name, "ok": ok, "detail": str(detail)[:160]})


def skip(case_id: str, name: str, detail: str = "") -> None:
    global SKIP
    SKIP += 1
    RESULTS.append({"id": case_id, "name": name, "ok": None, "detail": str(detail)[:160]})


def _load(mod_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


val = _load("wr_validate", "validate_weekly_report_md.py")
tr = _load("wr_transform", "transform_report_md.py")
paths = _load("wr_paths", "weekly_report_paths.py")

OWNER = cfg.OWNER

GOOD_MIN = f""":::meta
第23期 | 汇总日期：2026-06-08 | 来源：{cfg.SENDER_NAME}
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

## 四、需{OWNER}关注的事项

:::urgent
1. 一。**万丽霞**
2. 二。**万丽霞**
3. 三。**万丽霞**
4. 四。**万丽霞**
5. 五。**万丽霞**
6. 六。**万丽霞**
:::
"""

LEGACY_5SEC = f""":::meta
汇报周期：2026-06-01 ~ 06-07
:::

## 一、{OWNER}（蔡伟旭）本周重点

- 这段应被 transform 删除

## 二、重点项目进展

### NEW9830

| 子项目 | 进展 | 状态 |
| --- | --- | --- |
| x | y。**肖启新** | ⏳ |

## 三、海外市场要闻

:::info
### 巴西

- 进展。**程晓艳**

:::

## 四、{OWNER}业务线重点关注

### 海外销售 & 回款

- 内容。**程晓艳**

## 五、需{OWNER}关注的事项

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
    # ---- 配置 ----
    record("CFG01", "config OWNER 非空", bool(cfg.OWNER))
    record("CFG02", "config SENDER_EMAIL 含 @", "@" in cfg.SENDER_EMAIL)
    record("CFG03", "archive_dir 可解析", isinstance(cfg.archive_dir(), Path))

    # ---- validator ----
    record("VAL01", "最小合法 md 通过", not val.validate(GOOD_MIN))
    record("VAL02", f"禁止「{OWNER}本周重点」段", bool(val.validate(f"## 一、{OWNER}本周重点\n\nfoo")))
    record("VAL03", "兼容禁止历史「菜头（蔡伟旭）本周重点」", bool(val.validate("## 一、菜头（蔡伟旭）本周重点\n\nfoo")))
    record("VAL04", "缺 meta 失败", bool(val.validate("## 一、重点项目进展\n\n- x")))
    for i, h in enumerate(val.REQUIRED_H2, start=5):
        t = GOOD_MIN.replace(f"## {h}", "## MISSING")
        record(f"VAL{i:02d}", f"缺「{h[:8]}」失败", bool(val.validate(t)))
    bad_order = (
        GOOD_MIN.split("## 二、")[0]
        + "## 三、业务线重点关注\n\n### 海外销售 & 回款\n\n- x。**程晓艳**\n\n"
        + "## 二、海外市场要闻\n\n:::info\n### 巴西\n\n- 进展。**程晓艳**\n\n:::\n\n"
        + GOOD_MIN.split("## 三、")[1]
    )
    record("VAL09", "段落顺序错误被发现", bool(val.validate(bad_order)))
    record("VAL10", "缺署名被发现", bool(val.validate(GOOD_MIN.replace("。**程晓艳**", "。无署名"))))

    # ---- transform（legacy 5 段 → 4 段）----
    out = tr.transform(LEGACY_5SEC, period=23, summary_date="2026-06-08")
    record("TR01", "transform 后无第五节", "## 五、" not in out)
    record("TR02", "transform 后含四段标题", f"## 四、需{OWNER}关注的事项" in out)
    record("TR03", "transform meta 来源=配置发件人", f"来源：{cfg.SENDER_NAME}" in out)
    record("TR04", "transform 注入项目周报来源", "周报来源" in out)
    record("TR05", "transform 产物通过 validator", not val.validate(out), str(val.validate(out)[:2]))

    # ---- paths ----
    record("PATH01", "期号解析（23）", paths.parse_period_from_subject(f"{cfg.SUBJECT_KEY}（23）") == 23)
    record("PATH02", "命名 W{N}-…格式", paths.format_report_basename(23).startswith("W23-"))
    pp = paths.report_paths(23)
    record("PATH03", "report_paths 落在归档目录下", str(pp["pdf"]).startswith(str(cfg.archive_dir())))

    # ---- fetch 纯函数 ----
    fetch_mail = _load("wr_fetch", "fetch_mail.py")
    record("FET01", "发件人+主题匹配命中",
           fetch_mail.is_weekly_mail("Evyn Chen <evyn.chen@newpostech.com>",
                                     f"{cfg.SUBJECT_KEY}（23）", cfg.SENDER_EMAIL, cfg.SUBJECT_KEY))
    record("FET02", "非发件人被拒",
           not fetch_mail.is_weekly_mail("other@x.com", f"{cfg.SUBJECT_KEY}（23）",
                                         cfg.SENDER_EMAIL, cfg.SUBJECT_KEY))
    record("FET03", "期号解析（23）", fetch_mail.parse_week_num(f"{cfg.SUBJECT_KEY}（23）") == 23)
    record("FET04", "候选优先含 xlsx",
           fetch_mail.pick_best_candidate(
               [{"has_xlsx": False, "date": "z"}, {"has_xlsx": True, "date": "a"}])["has_xlsx"])
    _m = EmailMessage()
    _m["From"] = "Evyn Chen <evyn.chen@newpostech.com>"
    _m["Subject"] = f"{cfg.SUBJECT_KEY}（24）"
    _m.set_content("body")
    _m.add_attachment(b"PK\x03\x04fake", maintype="application",
                      subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                      filename="周报（24）.xlsx")
    _x = fetch_mail.extract_xlsx(email.message_from_bytes(_m.as_bytes()))
    record("FET05", "提取 xlsx 附件", _x is not None and _x[0].endswith(".xlsx"))

    # ---- 状态机 / 断点续跑（隔离到临时归档目录）----
    state = _load("wr_state", "state.py")
    runw = _load("wr_runweekly", "run_weekly.py")

    def _capture(fn, *a, **k):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = fn(*a, **k)
        stt = ""
        for ln in buf.getvalue().splitlines():
            if ln.startswith("STATE:"):
                stt = ln[len("STATE:"):].strip()
        return rc, stt

    _saved_env = os.environ.get("WEEKLY_REPORT_ARCHIVE_DIR")
    with tempfile.TemporaryDirectory() as td:
        os.environ["WEEKLY_REPORT_ARCHIVE_DIR"] = td
        adir = Path(td)

        def _seed(period, *, xlsx=False, md=False, pdf=False, delivered=False):
            if xlsx:
                (adir / "input").mkdir(parents=True, exist_ok=True)
                (adir / "input" / f"W{period}.xlsx").write_bytes(b"x")
            if md:
                (adir / f"W{period}-2026年06月08日.md").write_text(GOOD_MIN, encoding="utf-8")
            if pdf:
                (adir / f"W{period}-2026年06月08日.pdf").write_bytes(b"%PDF-1.4 test")
            if delivered:
                stt = state.load_state(period)
                state.mark(stt, "deliver", "done")
                state.save_state(period, stt)

        def mock_deliver_ok(channel, file, title="", text="", dry_run=False):
            return {"ok": True, "retryable": False, "channel": channel, "detail": "ok"}

        def mock_deliver_limit(channel, file, title="", text="", dry_run=False):
            return {"ok": False, "retryable": True, "channel": channel, "detail": "HTTP 500: rate limited"}

        # 场景A：取信已完成 → 下次直接做后面（不再取信）
        fetch_calls = {"n": 0}

        def spy_fetch(period=None):
            fetch_calls["n"] += 1
            return {"status": "ok", "period": 23}

        def mock_render_make_pdf(period):
            md = state.md_path(period)
            pdf = md.with_suffix(".pdf")
            pdf.write_bytes(b"%PDF-1.4 test")
            return True, str(pdf)

        _seed(23, xlsx=True, md=True)  # 取信+撰写已完成，缺 PDF
        rc, stt = _capture(runw.run, 23, fetcher=spy_fetch,
                           renderer=mock_render_make_pdf, deliverer=mock_deliver_ok)
        record("SM01", "取信已完成→跳过取信", fetch_calls["n"] == 0)
        record("SM02", "续跑直达 DELIVERED", stt == "DELIVERED", stt)

        # 场景B：处理完成、推送被限流 → 下次只补推送（不重渲染）
        render_calls = {"n": 0}

        def spy_render(period):
            render_calls["n"] += 1
            return True, "should-not-be-called"

        _seed(24, xlsx=True, md=True, pdf=True)  # 全部产物就绪，待投递
        rc, stt = _capture(runw.run, 24, fetcher=spy_fetch,
                           renderer=spy_render, deliverer=mock_deliver_limit)
        record("SM03", "限流→DELIVER_RETRY", stt == "DELIVER_RETRY", stt)
        record("SM04", "补推送时不重渲染", render_calls["n"] == 0)
        rc, stt = _capture(runw.run, 24, fetcher=spy_fetch,
                           renderer=spy_render, deliverer=mock_deliver_ok)
        record("SM05", "再次触发→DELIVERED", stt == "DELIVERED", stt)

        # 场景C：邮件未到 → FETCH_WAIT（静默重试）
        rc, stt = _capture(runw.run, 25,
                           fetcher=lambda period=None: {"status": "not_found"},
                           renderer=spy_render, deliverer=mock_deliver_ok)
        record("SM06", "邮件未到→FETCH_WAIT", stt == "FETCH_WAIT", stt)

        # 场景D：全部完成 → ALREADY_DONE（幂等）
        _seed(26, xlsx=True, md=True, pdf=True, delivered=True)
        rc, stt = _capture(runw.run, 26, fetcher=spy_fetch,
                           renderer=spy_render, deliverer=mock_deliver_ok)
        record("SM07", "已交付→ALREADY_DONE 幂等", stt == "ALREADY_DONE", stt)

        # 场景E：仅取信、未撰写 → NEED_COMPOSE（交给 Agent 写四段）
        _seed(27, xlsx=True)
        rc, stt = _capture(runw.run, 27, fetcher=spy_fetch,
                           renderer=spy_render, deliverer=mock_deliver_ok)
        record("SM08", "缺 Markdown→NEED_COMPOSE", stt == "NEED_COMPOSE", stt)

    if _saved_env is None:
        os.environ.pop("WEEKLY_REPORT_ARCHIVE_DIR", None)
    else:
        os.environ["WEEKLY_REPORT_ARCHIVE_DIR"] = _saved_env

    # ---- render（可选依赖，缺失则 SKIP）----
    have_weasy = shutil.which("weasyprint") is not None
    try:
        import fitz  # noqa: F401

        have_fitz = True
    except Exception:
        have_fitz = False

    render_py = SCRIPTS / "render_mobile_pdf.py"
    record("REN00", "vendored render_mobile_pdf.py 存在", render_py.is_file())

    if have_weasy and have_fitz and render_py.is_file():
        with tempfile.TemporaryDirectory() as td:
            body = Path(td) / "body.md"
            body.write_text(GOOD_MIN, encoding="utf-8")
            outpdf = Path(td) / "t.pdf"
            r = subprocess.run(
                [sys.executable, str(render_py), "--preset", "weekly-report",
                 "--title", "测试", "--body-md", str(body), "--output", str(outpdf)],
                capture_output=True, text=True, timeout=120,
            )
            record("REN01", "render 退出码 0", r.returncode == 0, r.stderr[:160])
            if outpdf.is_file():
                import fitz
                page = fitz.open(str(outpdf))[0]
                w_mm = page.cropbox.width / 72 * 25.4
                record("REN02", "PDF 宽约 100mm", 96 <= w_mm <= 104, f"{w_mm:.1f}mm")
                record("REN03", "PDF 单页", fitz.open(str(outpdf)).page_count == 1)
            else:
                record("REN02", "render 无输出", False)
    else:
        skip("REN01", "render 退出码 0", f"weasyprint={have_weasy} PyMuPDF={have_fitz}")
        skip("REN02", "PDF 宽约 100mm", "render 依赖缺失")
        skip("REN03", "PDF 单页", "render 依赖缺失")

    # ---- 汇总 ----
    print(f"\n{'ID':<8} {'OK':<6} 用例")
    print("-" * 70)
    for r in RESULTS:
        mark = "✅" if r["ok"] is True else ("⏭️ SKIP" if r["ok"] is None else "❌")
        print(f"{r['id']:<8} {mark:<6} {r['name']}" + (f"  [{r['detail']}]" if r["detail"] else ""))
    print("-" * 70)
    print(f"PASS={PASS}  FAIL={FAIL}  SKIP={SKIP}  (OWNER={cfg.OWNER}, COMPANY={cfg.COMPANY})")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
