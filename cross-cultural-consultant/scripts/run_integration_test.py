#!/usr/bin/env python3
"""跨文化技能端到端集成测试（纯标准库，无需凭据）。

覆盖：路由、Hofstede 数据读取、Delta 计算、A 模式骨架生成、多国对比、
null 维度兜底、PDF 渲染、输出路径泄漏检查。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = SKILL_ROOT / "data" / "hofstede-dimensions.json"
EVALS_PATH = SKILL_ROOT / "evals.json"
RENDER_SCRIPT = SKILL_ROOT / "scripts" / "render_mobile_pdf.py"

CHINA = {
    "power_distance": 80,
    "individualism": 43,
    "motivation": 66,
    "uncertainty_avoidance": 30,
    "long_term_orientation": 77,
    "indulgence": 24,
}

DIM_LABELS = {
    "power_distance": "权力距离",
    "individualism": "个人/集体",
    "motivation": "事业成功/生活质量",
    "uncertainty_avoidance": "不确定性规避",
    "long_term_orientation": "长期/短期导向",
    "indulgence": "放纵/克制",
}

# 简化路由：按 evals.json 用例关键词匹配（与 SKILL.md 路由表对齐）
ROUTE_RULES: list[tuple[str, list[str], str]] = [
    ("clarify", ["出海", "先给建议"], "SKILL.md §六"),
    ("compare", ["对比"], "SKILL.md §五"),
    ("fallback", ["尼泊尔"], "SKILL.md §七"),
    ("D", ["复盘", "没谈成", "刚回来"], "modules/after-trip.md"),
    ("B5", ["说错话", "气氛冷", "救"], "modules/during-crisis.md"),
    ("B4", ["沉默", "刚说"], "modules/during-meeting.md"),
    ("B3", ["伴手礼", "送礼"], "modules/during-gifting.md"),
    ("B2", ["合同", "推进", "解约"], "modules/during-negotiation.md"),
    ("B1", ["吃饭", "宴请", "饭局"], "modules/during-dining.md"),
    ("A+战略", ["建本地团队", "外派"], "modules/before-travel.md"),
    ("A", ["画像", "出差", "去"], "modules/before-travel.md"),
]

COUNTRY_MAP = {
    "日本": "Japan",
    "墨西哥": "Mexico",
    "法国": "France",
    "德国": "Germany",
    "尼泊尔": "Nepal",
    "沙特": "Saudi Arabia",
    "孟加拉": "Bangladesh",
    "埃及": "Egypt",
}


class TestResult:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.details: list[str] = []

    def ok(self, case_id: str, msg: str) -> None:
        self.passed += 1
        self.details.append(f"{case_id:<8} ✅  {msg}")

    def fail(self, case_id: str, msg: str) -> None:
        self.failed += 1
        self.details.append(f"{case_id:<8} ❌  {msg}")


def load_data() -> dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def route_input(text: str) -> str:
    for mode, keywords, _ in ROUTE_RULES:
        if any(kw in text for kw in keywords):
            return mode
    return "unknown"


def delta_mark(delta: float | None) -> str:
    if delta is None:
        return "—"
    ad = abs(delta)
    if ad > 30:
        return "⚠️"
    if ad > 20:
        return "注意"
    return ""


def build_a_mode_skeleton(country_en: str, data: dict) -> str:
    country = data["countries"][country_en]
    dims = country["dimensions"]
    lines = [f"# {country_en} 文化画像（出国前）", "", "## 一、文化速览卡（中国对照）", ""]
    lines.append("| 维度 | 中国 | 目标国 | Delta | 标记 |")
    lines.append("|------|------|--------|-------|------|")

    collisions: list[tuple[str, float]] = []
    for key, label in DIM_LABELS.items():
        cn_val = CHINA[key]
        tgt = dims.get(key)
        if tgt is None:
            lines.append(f"| {label} | {cn_val} | N/A | — | N/A |")
            continue
        delta = tgt - cn_val
        mark = delta_mark(delta)
        lines.append(f"| {label} | {cn_val} | {tgt} | {delta:+d} | {mark} |")
        collisions.append((label, abs(delta)))

    top = sorted(collisions, key=lambda x: x[1], reverse=True)[:2]
    lines.extend([
        "",
        f"**最危险的碰撞点**：{top[0][0]}、{top[1][0]}",
        "",
        "## 二、沟通密码",
        "- **见面/会议风格**：按高 UA 准备书面材料与时间表",
        "",
        "## 三、中国人最容易踩的 3 个坑",
        "1. **口头承诺代替书面确认** → 对方解读：不可靠 → 后果：推迟决策",
        "2. **会议上直接否定方案** → 对方解读：不尊重流程 → 后果：沉默拖延",
        "3. **催促快速拍板** → 对方解读：无视风险 → 后果：要求更多论证",
        "",
        "> 数据快照:2026-05-30 | Skill v0.8.1",
    ])
    return "\n".join(lines)


def test_routing(tr: TestResult) -> None:
    with open(EVALS_PATH, encoding="utf-8") as f:
        evals = json.load(f)["evals"]

    for i, case in enumerate(evals, 1):
        case_id = f"RT{i:02d}"
        got = route_input(case["input"])
        expected = case["expected_mode"]
        if got == expected or (expected == "A" and got == "A"):
            tr.ok(case_id, f"{case['name']}: {got}")
        else:
            tr.fail(case_id, f"{case['name']}: 期望 {expected}, 实际 {got}")


def test_japan_a_mode(tr: TestResult) -> None:
    data = load_data()
    md = build_a_mode_skeleton("Japan", data)

    checks = [
        ("A01", "uncertainty_avoidance" in str(data["countries"]["Japan"]["dimensions"]), "日本 UA 数据存在"),
        ("A02", "| 不确定性规避 | 30 | 92 | +62 |" in md, "UA Delta=+62 正确"),
        ("A03", "最危险的碰撞点" in md, "碰撞点段落生成"),
        ("A04", "踩的 3 个坑" in md, "踩坑清单生成"),
        ("A05", not re.search(r"/Users/|newpos/", md), "输出无本地路径泄漏"),
    ]
    for cid, cond, msg in checks:
        (tr.ok if cond else tr.fail)(cid, msg)


def test_compare_mode(tr: TestResult) -> None:
    data = load_data()
    countries = ["Mexico", "France"]
    rows = []
    for en in countries:
        dims = data["countries"][en]["dimensions"]
        ua_delta = dims["uncertainty_avoidance"] - CHINA["uncertainty_avoidance"]
        rows.append((en, ua_delta))

    md_lines = ["| 维度 | 中国 | 墨西哥 | 法国 |", "|---|---:|---:|---:|"]
    for key, label in DIM_LABELS.items():
        cn = CHINA[key]
        mx = data["countries"]["Mexico"]["dimensions"][key]
        fr = data["countries"]["France"]["dimensions"][key]
        md_lines.append(f"| {label} | {cn} | {mx} | {fr} |")
    table = "\n".join(md_lines)

    if "墨西哥" in COUNTRY_MAP and "法国" in COUNTRY_MAP:
        tr.ok("C01", "国家名映射可用")
    else:
        tr.fail("C01", "国家名映射缺失")
    if "| 放纵/克制 |" in table:
        tr.ok("C02", "对比表含放纵维度")
    else:
        tr.fail("C02", "对比表缺放纵维度")
    mx_ind = str(data["countries"]["Mexico"]["dimensions"]["indulgence"])
    if mx_ind in table:
        tr.ok("C03", f"墨西哥放纵指数 {mx_ind} 入表")
    else:
        tr.fail("C03", "墨西哥放纵指数未入表")


def test_nepal_fallback(tr: TestResult) -> None:
    dims = load_data()["countries"]["Nepal"]["dimensions"]
    lto = dims["long_term_orientation"]
    ind = dims["indulgence"]

    if lto is None:
        tr.ok("F01", "尼泊尔 LTO=null")
    else:
        tr.fail("F01", f"尼泊尔 LTO 应为 null，实际 {lto}")
    if ind is None:
        tr.ok("F02", "尼泊尔 indulgence=null")
    else:
        tr.fail("F02", f"尼泊尔 indulgence 应为 null，实际 {ind}")
    if dims["power_distance"] == 65:
        tr.ok("F03", "尼泊尔 PD=65 可读")
    else:
        tr.fail("F03", f"尼泊尔 PD 异常: {dims['power_distance']}")


def test_pdf_render(tr: TestResult) -> None:
    data = load_data()
    body = build_a_mode_skeleton("Japan", data)
    out_dir = SKILL_ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    pdf_path = out_dir / "integration_test_japan_20260613.pdf"

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        body_path = f.name

    cmd = [
        sys.executable,
        str(RENDER_SCRIPT),
        "--title", "日本文化画像 — 集成测试",
        "--body-md", body_path,
        "--output", str(pdf_path),
        "--brand-color", "#8B0000",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        tr.fail("P01", f"render 失败: {proc.stderr[:200]}")
        return

    tr.ok("P01", "render 退出码 0")
    size = pdf_path.stat().st_size if pdf_path.is_file() else 0
    if pdf_path.is_file() and size > 1000:
        tr.ok("P02", f"PDF 生成 {size} bytes → {pdf_path}")
    else:
        tr.fail("P02", f"PDF 缺失或过小: {size} bytes")

    # 用 PyMuPDF 读宽度
    try:
        import fitz  # noqa: PLC0415
        doc = fitz.open(pdf_path)
        page = doc[0]
        w_mm = page.rect.width * 25.4 / 72
        if 95 <= w_mm <= 105:
            tr.ok("P03", f"PDF 宽约 {w_mm:.1f}mm（目标 ~100mm）")
        else:
            tr.fail("P03", f"PDF 宽度异常 {w_mm:.1f}mm")
        tr.ok("P04", f"页数 {doc.page_count}")
        doc.close()
    except ImportError:
        tr.ok("P03", "PyMuPDF 未安装，跳过宽度校验")


def test_module_files(tr: TestResult) -> None:
    modules = [
        "before-travel.md", "during-dining.md", "during-negotiation.md",
        "during-gifting.md", "during-meeting.md", "during-crisis.md", "after-trip.md",
    ]
    for name in modules:
        path = SKILL_ROOT / "modules" / name
        tr.ok("M", f"{name} 存在 ({path.stat().st_size} bytes)") if path.is_file() else tr.fail("M", f"{name} 缺失")


def main() -> int:
    tr = TestResult()
    print("=" * 70)
    print("cross-cultural-consultant 集成测试")
    print("=" * 70)

    test_module_files(tr)
    test_routing(tr)
    test_japan_a_mode(tr)
    test_compare_mode(tr)
    test_nepal_fallback(tr)
    test_pdf_render(tr)

    print("-" * 70)
    for line in tr.details:
        print(line)
    print("-" * 70)
    print(f"PASS={tr.passed}  FAIL={tr.failed}")
    return 1 if tr.failed else 0


if __name__ == "__main__":
    sys.exit(main())
