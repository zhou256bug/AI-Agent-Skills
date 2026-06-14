#!/usr/bin/env python3
"""校验合同审核输出结构（纯标准库）。

检查审核意见 Markdown 是否包含必需段落标记。
可用于 Agent 输出后的本地自检。

用法：
    python3 scripts/validate_review_output.py --sample   # 校验内置样例
    python3 scripts/validate_review_output.py <file.md>  # 校验指定文件
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

# 所有模式通用的必需标记
COMMON_REQUIRED = ["结论", "免责声明"]

# 各模式额外必需标记
MODE_MARKERS: dict[str, list[str]] = {
    "A": ["我方立场", "🔴", "🟡", "🟢", "建议下一步"],
    "B": ["我方立场", "🔴", "🟡", "🟢"],
    "C": ["🔴", "🟡", "🟢"],
    "E": ["方案", "🔴"],
    "H": ["🔴"],
}

SAMPLE_A = """\
## 合同风险分析 — 7-Labs SRL / 多米尼加 / 续签

**我方立场**：乙方（Vendor）
**结论**：新版新增 Law 173 登记条款且无 just cause 终止条件，为最大风险。

### 🔴 必须改
1. Law 173 登记条款 — 旧约无新约有 → 须绑定 6 项 just cause 终止触发条件

### 🟡 注意
1. MFN 条款未限缩为区域内

### 🟢 可接受
1. 管辖法为中国法 + CIETAC

### 建议下一步
提交老板确认 Law 173 保留 + just cause 的谈判策略。

> **免责声明**：本意见为内部合同初审，不构成正式法律意见。
"""


def detect_mode(text: str) -> str:
    """根据标题行推断模式。"""
    if "采购合同审核" in text:
        return "B"
    if "人事合同审核" in text:
        return "C"
    if "解约" in text or "终止分析" in text:
        return "E"
    if "POS 合规" in text:
        return "H"
    if "合同风险分析" in text:
        return "A"
    return "A"


def validate(text: str) -> list[str]:
    """返回缺失标记列表；空列表表示通过。"""
    errors: list[str] = []
    mode = detect_mode(text)

    for marker in COMMON_REQUIRED:
        if marker not in text:
            errors.append(f"缺少通用标记：{marker}")

    for marker in MODE_MARKERS.get(mode, []):
        if marker not in text:
            errors.append(f"缺少 {mode} 模式标记：{marker}")

    # 禁止本地绝对路径
    if re.search(r"/Users/\w+", text):
        errors.append("输出含本地绝对路径 /Users/...")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验合同审核输出结构")
    parser.add_argument("file", nargs="?", help="待校验的 Markdown 文件")
    parser.add_argument("--sample", action="store_true", help="校验内置 A 模式样例")
    args = parser.parse_args()

    if args.sample:
        text = SAMPLE_A
        label = "内置 A 模式样例"
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"[FAIL] 文件不存在：{path}")
            return 1
        text = path.read_text(encoding="utf-8")
        label = str(path)
    else:
        parser.print_help()
        return 1

    errors = validate(text)
    mode = detect_mode(text)
    print(f"校验对象：{label}")
    print(f"检测模式：{mode}")

    if errors:
        print(f"[FAIL] 发现 {len(errors)} 个问题：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("[OK] 输出结构校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
