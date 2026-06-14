#!/usr/bin/env python3
"""华智融法务技能 · 独立验收套件（平台无关，纯标准库）。

用法：
    python3 scripts/run_acceptance.py
退出码：有 FAIL → 1；否则 0。
"""

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


def main() -> int:
    # ---- 文件结构 ----
    required = [
        "SKILL.md", "evals.json", "README.md", "CHANGELOG.md",
        "modules/contract-distribution.md", "modules/contract-procurement.md",
        "modules/labor-domestic.md", "modules/contract-termination.md",
        "modules/equity-incentive.md", "modules/corporate-jv.md",
        "references/negotiation-playbook.md", "references/equity-incentive-playbook.md",
        "references/corporate-jv-playbook.md", "references/onboarding-flow.md",
        "references/emoji-output-guide.md", "references/pdf-review-workflow.md",
        "scripts/legal_affairs_cli.py", "scripts/legal_affairs_lib.py",
        "scripts/render_mobile_pdf.py", "scripts/render_review_pdf.py",
        "evaluation/run_evals.py",
    ]
    for rel in required:
        record(f"FS-{rel[:20]}", f"存在 {rel}", (SKILL / rel).is_file())

    # ---- 禁止迁移残留 ----
    forbidden = ["方律", "大为", "delegate_task", "newpos/", "fanglv", "dawei"]
    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for word in forbidden:
        record(f"CL-{word[:8]}", f"SKILL.md 不含 {word}", word not in skill_md)

    # ---- 版本号 ----
    record("VER01", "SKILL.md version 0.3.0", "version: 0.3.0" in skill_md)

    # ---- config 默认值 ----
    import legal_affairs_config as cfg  # noqa: E402

    record("CFG01", "默认决策者=老板", cfg.DECISION_MAKER == "老板")
    record("CFG02", "默认公司=华智融", cfg.COMPANY == "华智融")
    record("CFG03", "境内主体已配置", "华智融" in cfg.ENTITY_CN)
    record("CFG04", "境外主体已配置", "HONG KONG" in cfg.ENTITY_HK)
    record("CFG05", "股权归档路径", str(cfg.ARCHIVE_EQUITY).endswith("股权/审核记录"))

    # ---- setup status ----
    lib = _load("la_lib", "legal_affairs_lib.py")
    status = lib.get_setup_status()
    record("SET01", "setup status 含 needsSetup", "needsSetup" in status)
    record("SET02", "setup status 含 fieldsToCollect", len(status.get("fieldsToCollect", [])) >= 5)
    record("SET03", "setup configured=true", status.get("configured") is True)

    # ---- setup apply + doctor（临时目录）----
    with tempfile.TemporaryDirectory() as td:
        env_path = Path(td) / "credentials.env"
        os.environ.pop("LEGAL_AFFAIRS_DECISION_MAKER", None)
        apply_res = lib.run_setup_apply(
            target="path",
            explicit_path=str(env_path),
            values={
                "LEGAL_AFFAIRS_DECISION_MAKER": "测试决策者",
                "LEGAL_AFFAIRS_COMPANY": "测试公司",
                "LEGAL_AFFAIRS_ARCHIVE_DIR": td,
            },
            verify=False,
        )
        record("SET04", "setup apply 写入文件", env_path.is_file())
        record("SET05", "apply 含 writtenPath", "writtenPath" in apply_res.get("apply", {}))

        lib.bootstrap_env(str(env_path))
        snap = lib.config_snapshot()
        record("SET06", "apply 后决策者生效", snap.get("decisionMaker") == "测试决策者")

        # doctor 使用临时归档目录
        os.environ["LEGAL_AFFAIRS_ARCHIVE_DIR"] = td
        doc = lib.run_doctor()
        record("DOC01", "doctor ok", doc.get("ok") is True, "; ".join(doc.get("errors", [])))

    # ---- CLI 子进程 ----
    cli = SCRIPTS / "legal_affairs_cli.py"
    r_status = subprocess.run(
        [sys.executable, str(cli), "setup", "status"],
        capture_output=True, text=True, timeout=30,
    )
    record("CLI01", "cli setup status 退出码 0", r_status.returncode == 0, r_status.stderr[:120])
    if r_status.returncode == 0:
        try:
            parsed = json.loads(r_status.stdout)
            record("CLI02", "cli status JSON 可解析", isinstance(parsed, dict))
        except json.JSONDecodeError:
            record("CLI02", "cli status JSON 可解析", False)

    r_doc = subprocess.run(
        [sys.executable, str(cli), "doctor"],
        capture_output=True, text=True, timeout=30,
    )
    record("CLI03", "cli doctor 退出码 0", r_doc.returncode == 0, r_doc.stderr[:120])

    record("EMO01", "emoji-output-guide 存在", (SKILL / "references/emoji-output-guide.md").is_file())
    emoji_guide = (SKILL / "references/emoji-output-guide.md").read_text(encoding="utf-8")
    record("EMO02", "emoji 指南含 📌", "📌" in emoji_guide)
    record("EMO03", "pdf-review-workflow 存在", (SKILL / "references/pdf-review-workflow.md").is_file())

    render_py = SCRIPTS / "render_mobile_pdf.py"
    render_review = SCRIPTS / "render_review_pdf.py"
    record("PDF00", "render_mobile_pdf.py 存在", render_py.is_file())
    record("PDF01", "render_review_pdf.py 存在", render_review.is_file())

    import shutil
    have_weasy = shutil.which("weasyprint") is not None
    try:
        import fitz  # noqa: F401
        have_fitz = True
    except Exception:
        have_fitz = False

    if have_weasy and have_fitz and render_review.is_file():
        with tempfile.TemporaryDirectory() as td:
            body = Path(td) / "review.md"
            body.write_text(
                "## ⚖️ 测试\n\n**📌 结论**：测试\n\n### 🔴 必须改\n- x\n\n> ⚗️ **免责声明**：测试\n",
                encoding="utf-8",
            )
            outpdf = Path(td) / "t.pdf"
            r = subprocess.run(
                [sys.executable, str(render_review), "--title", "验收测试",
                 "--body-md", str(body), "--output", str(outpdf), "--mode", "A"],
                capture_output=True, text=True, timeout=120,
            )
            record("PDF02", "render_review_pdf 退出码 0", r.returncode == 0, r.stderr[:120])
            if outpdf.is_file():
                import fitz
                w_mm = fitz.open(str(outpdf))[0].cropbox.width / 72 * 25.4
                record("PDF03", "PDF 宽约 100mm", 96 <= w_mm <= 104, f"{w_mm:.1f}mm")
            else:
                record("PDF03", "PDF 输出存在", False)
    else:
        skip("PDF02", "render_review_pdf 渲染", f"weasyprint={have_weasy} PyMuPDF={have_fitz}")
        skip("PDF03", "PDF 宽度校验", "render 依赖缺失")

    # ---- evals harness ----
    r_evals = subprocess.run(
        [sys.executable, str(SKILL / "evaluation" / "run_evals.py")],
        capture_output=True, text=True, timeout=30,
        cwd=str(SKILL),
    )
    record("EVL01", "run_evals 退出码 0", r_evals.returncode == 0, r_evals.stdout[-200:])

    evals = json.loads((SKILL / "evals.json").read_text(encoding="utf-8"))
    record("EVL02", "evals >= 21 条", len(evals.get("evals", [])) >= 21)
    modes = {e.get("expected_mode") for e in evals.get("evals", [])}
    record("EVL03", "含 F/G 模式", "F" in modes and "G" in modes)
    record("EVL04", "含 S/setup 模式", "S" in modes)

    # ---- validate_review_output ----
    val = _load("la_val", "validate_review_output.py")
    for flag, mode in [("--sample", "A"), ("--sample-f", "F"), ("--sample-g", "G")]:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_review_output.py"), flag],
            capture_output=True, text=True, timeout=15,
        )
        record(f"VAL-{mode}", f"validate {mode} 样例通过", r.returncode == 0, r.stderr[:80])

    # ---- 路由表含 F/G ----
    routing = (SKILL / "references" / "contract-routing.md").read_text(encoding="utf-8")
    record("RTE01", "路由表含股权激励", "股权激励" in routing)
    record("RTE02", "路由表含合资/JV", "合资" in routing or "JV" in routing)

    # ---- 汇总 ----
    print(f"\n{'ID':<12} {'OK':<6} 用例")
    print("-" * 72)
    for r in RESULTS:
        if r["ok"] is None:
            mark = "⏭️ SKIP"
        else:
            mark = "✅" if r["ok"] else "❌"
        print(f"{r['id']:<12} {mark:<6} {r['name']}" + (f"  [{r['detail']}]" if r["detail"] else ""))
    print("-" * 72)
    print(f"PASS={PASS}  FAIL={FAIL}  SKIP={SKIP}  (DECISION_MAKER={cfg.DECISION_MAKER}, COMPANY={cfg.COMPANY})")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
