#!/usr/bin/env python3
"""仓库级技能脚手架校验（纯标准库）。

对照 docs/SKILL-DESIGN-STANDARDS.md v1.1.0（原子技能优先 + 八大原则）。

用法：
    python3 scripts/validate_skill_scaffold.py
    python3 scripts/validate_skill_scaffold.py --skill huazhirong-legal-affairs

退出码：全部通过 0；存在缺失 1。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STANDARDS_DOC = REPO_ROOT / "docs" / "SKILL-DESIGN-STANDARDS.md"
EXCLUDE_DIRS = {"migration", "docs", "scripts", ".git", ".cursor", "node_modules"}

# 所有已规范化技能必须具备
REQUIRED_ALL = [
    "SKILL.md",
    "CHANGELOG.md",
    ".gitignore",
    "agents/openclaw.yaml",
    "agents/hermes.yaml",
    "agents/openai.yaml",
    "references/openclaw-hermes-registration.md",
]

RECOMMENDED_ALL = [
    "README.md",
]

# 至少一种验收能力
ACCEPTANCE_ANY = [
    ("scripts/run_acceptance.py", None),
    ("evaluation/run_evals.py", "evals.json"),
]

# 有用户报告输出的技能（当前根目录四类）建议具备
RECOMMENDED_OUTPUT = [
    "references/emoji-output-guide.md",
]

# 长报告类技能建议具备 PDF 工作流
RECOMMENDED_PDF = [
    "scripts/render_mobile_pdf.py",
]

SKILLS_WITH_PDF = {
    "cross-cultural-consultant",
    "huazhirong-management-weekly-report",
    "huazhirong-legal-affairs",
}

SKILLS_WITH_EMOJI = {
    "cross-cultural-consultant",
    "huazhirong-legal-affairs",
    "huazhirong-management-weekly-report",
}

SKILLS_WITH_SETUP = {
    "aliyun-enterprise-mail",
    "huazhirong-legal-affairs",
    "huazhirong-management-weekly-report",
}

SETUP_FILES = [
    "references/onboarding-flow.md",
]

FORBIDDEN_PATTERNS = [
    ("delegate_task(", "delegate_task 调用"),
    ("$HERMES_HOME", "平台专有路径"),
]
FORBIDDEN_LITERALS = ["newpos/"]


def _skill_md_violations(text: str) -> list[str]:
    violations: list[str] = []
    for line in text.splitlines():
        if "禁止" in line or "勿" in line or "不得" in line:
            continue
        for pat, label in FORBIDDEN_PATTERNS:
            if pat in line:
                violations.append(f"SKILL.md 含禁止项：{label}")
        for lit in FORBIDDEN_LITERALS:
            if lit in line:
                violations.append(f"SKILL.md 含禁止项：{lit}")
    return violations


def discover_skills() -> list[Path]:
    skills: list[Path] = []
    for child in sorted(REPO_ROOT.iterdir()):
        if not child.is_dir() or child.name in EXCLUDE_DIRS or child.name.startswith("."):
            continue
        if (child / "SKILL.md").is_file():
            skills.append(child)
    return skills


def check_skill(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    name = skill_dir.name

    for rel in REQUIRED_ALL:
        if not (skill_dir / rel).is_file():
            errors.append(f"缺少必需文件：{rel}")

    for rel in RECOMMENDED_ALL:
        if not (skill_dir / rel).is_file():
            warnings.append(f"建议补充：{rel}")

    has_acceptance = False
    for script_rel, extra in ACCEPTANCE_ANY:
        script_path = skill_dir / script_rel
        if script_path.is_file():
            if extra is None or (skill_dir / extra).is_file():
                has_acceptance = True
                break
    if not has_acceptance:
        warnings.append("建议补充：run_acceptance.py 或 run_evals.py + evals.json")

    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        text = skill_md.read_text(encoding="utf-8")
        if "Use when" not in text and "use when" not in text.lower():
            warnings.append("SKILL.md description 建议含 Use when 触发词")
        for v in _skill_md_violations(text):
            errors.append(v)

    if name in SKILLS_WITH_EMOJI:
        if not any((skill_dir / p).is_file() for p in RECOMMENDED_OUTPUT):
            warnings.append("建议补充 references/emoji-output-guide.md")

    if name in SKILLS_WITH_PDF:
        for rel in RECOMMENDED_PDF:
            if not (skill_dir / rel).is_file():
                warnings.append(f"建议补充 {rel}")

    if name in SKILLS_WITH_SETUP:
        for rel in SETUP_FILES:
            if not (skill_dir / rel).is_file():
                warnings.append(f"建议补充 {rel}（setup 技能）")

    config_candidates = list((skill_dir / "scripts").glob("*_config.py")) if (skill_dir / "scripts").is_dir() else []
    if not config_candidates and name != "cross-cultural-consultant":
        warnings.append("建议 scripts/*_config.py 参数化配置（cross-cultural 历史豁免）")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验技能目录脚手架")
    parser.add_argument("--skill", help="只检查指定技能目录名")
    parser.add_argument("--strict", action="store_true", help="建议项缺失也视为失败（新技能上线推荐）")
    args = parser.parse_args()

    if not STANDARDS_DOC.is_file():
        print(f"[FAIL] 缺少标准文档：{STANDARDS_DOC}")
        return 1

    skills = discover_skills()
    if args.skill:
        skills = [REPO_ROOT / args.skill]
        if not (skills[0] / "SKILL.md").is_file():
            print(f"[FAIL] 找不到技能：{args.skill}")
            return 1

    if not skills:
        print("[FAIL] 未发现任何技能目录")
        return 1

    total_errors = 0
    total_warnings = 0
    print(f"技能脚手架校验（标准：docs/SKILL-DESIGN-STANDARDS.md）\n")
    print(f"{'技能':<36} {'必需':<8} {'建议'}")
    print("-" * 72)

    for skill_dir in skills:
        errors, warnings = check_skill(skill_dir)
        status = "✅" if not errors else "❌"
        warn_str = f"{len(warnings)} 条" if warnings else "—"
        print(f"{skill_dir.name:<36} {status:<8} {warn_str}")
        for e in errors:
            print(f"  ❌ {e}")
        for w in warnings:
            print(f"  🟡 {w}")
        total_errors += len(errors)
        total_warnings += len(warnings)
        if args.strict:
            total_errors += len(warnings)

    print("-" * 72)
    if total_errors:
        print(f"[FAIL] {total_errors} 个问题（含 --strict 建议项），{total_warnings} 条建议")
        return 1
    print(f"[OK] {len(skills)} 个技能脚手架必需项齐全（{total_warnings} 条建议性提示）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
