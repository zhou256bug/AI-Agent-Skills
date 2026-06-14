#!/usr/bin/env python3
"""校验合同审核输出结构（纯标准库）。

用法：
    python3 scripts/validate_review_output.py --sample     # A 模式样例
    python3 scripts/validate_review_output.py --sample-f   # F 模式样例
    python3 scripts/validate_review_output.py --sample-g   # G 模式样例
    python3 scripts/validate_review_output.py <file.md>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

COMMON_REQUIRED = ["结论", "免责声明"]

MODE_MARKERS: dict[str, list[str]] = {
    "A": ["我方立场", "🔴", "🟡", "🟢", "建议下一步"],
    "B": ["我方立场", "🔴", "🟡", "🟢"],
    "C": ["🔴", "🟡", "🟢"],
    "E": ["方案", "🔴"],
    "F": ["🔴", "外部律师"],
    "G": ["出资", "🔴"],
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

SAMPLE_F = """\
## 股权激励审核 — 核心研发 / 期权授予 / 新签

**结论**：行权价无评估依据且未约定离职回购，为最大风险。

### 🔴 必须改
1. 行权定价 — 无公允价值评估报告

### 🟡 建议改
1. 加速归属条件未与并购场景挂钩

### 🟢 可接受
1. 激励对象限定为核心技术人员

### 建议外部律师确认项
- 期权池稀释对控制权的影响
- 税务递延纳税资格

### 建议下一步
暂停签署，补充评估报告后升级老板。

> **免责声明**：本意见为内部合同初审，不构成正式法律意见。
"""

SAMPLE_G = """\
## 股东/合资协议审核 — 墨西哥子公司 / 增资 / 新签

**结论**：出资方式未在协议中明确借款 vs 增资路径，为最大风险。

### 出资结构对比
| 方式 | 税务 | 治理 | 建议 |
| 股东借款 | 利润还本 | 债权 | 短期过桥 |
| 增资 | 分红预提税 | 股权 | 长期资本 |

### 🔴 必须改
1. 治理条款 — 我方无重大事项否决权

### 🟡 注意
1. 退出估值方法未约定

### 🟢 可接受
1. 争议解决为中国法 + CIETAC

### 建议董事会/老板下一步
股东会前明确出资形式与金额区间。

> **免责声明**：本意见为内部合同初审，不构成正式法律意见。
"""


def detect_mode(text: str) -> str:
    if "股权激励审核" in text:
        return "F"
    if "股东/合资协议审核" in text or "股东" in text and "增资" in text:
        return "G"
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
    errors: list[str] = []
    mode = detect_mode(text)

    for marker in COMMON_REQUIRED:
        if marker not in text:
            errors.append(f"缺少通用标记：{marker}")

    for marker in MODE_MARKERS.get(mode, []):
        if marker not in text:
            errors.append(f"缺少 {mode} 模式标记：{marker}")

    if re.search(r"/Users/\w+", text):
        errors.append("输出含本地绝对路径 /Users/...")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验合同审核输出结构")
    parser.add_argument("file", nargs="?", help="待校验的 Markdown 文件")
    parser.add_argument("--sample", action="store_true", help="校验内置 A 模式样例")
    parser.add_argument("--sample-f", action="store_true", help="校验内置 F 模式样例")
    parser.add_argument("--sample-g", action="store_true", help="校验内置 G 模式样例")
    args = parser.parse_args()

    if args.sample:
        text, label = SAMPLE_A, "内置 A 模式样例"
    elif args.sample_f:
        text, label = SAMPLE_F, "内置 F 模式样例"
    elif args.sample_g:
        text, label = SAMPLE_G, "内置 G 模式样例"
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
