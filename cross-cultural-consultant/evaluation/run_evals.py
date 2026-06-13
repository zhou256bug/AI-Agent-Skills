#!/usr/bin/env python3
"""跨文化顾问 skill 的评测 / 自检 harness（纯标准库，无第三方依赖）。

本脚本不调用任何 LLM，做的是**静态校验**，用于 clone 后确认 skill 自洽、可开箱即用：

1. 校验 evals.json 结构（每条用例含必需字段）。
2. 校验每条用例引用的 module 文件（loads_module 中形如 ``modules/xxx.md`` 的路径）真实存在。
3. 校验 data/hofstede-dimensions.json 可加载且用例 must_have 字段非空。
4. 打印用例汇总表。

退出码：全部通过 0；存在结构性问题 1。
用法：
    python3 evaluation/run_evals.py            # 从 skill 根目录
    python3 cross-cultural-consultant/evaluation/run_evals.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# skill 根目录 = 本文件父目录（evaluation/）的上一级
SKILL_ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = SKILL_ROOT / "evals.json"
DATA_PATH = SKILL_ROOT / "data" / "hofstede-dimensions.json"

# loads_module 字段里形如 "modules/xxx.md" 或 "references/xxx.md" 的才当作文件路径校验；
# 形如 "直接走 SKILL.md 第五节" 的描述性文本不校验存在性。
MODULE_PATH_RE = re.compile(r"((?:modules|references|frameworks|examples)/[\w./-]+\.md)")

REQUIRED_FIELDS = ("name", "input", "expected_mode", "expected", "must_have", "loads_module")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors: list[str] = []

    if not EVALS_PATH.exists():
        print(f"[FAIL] 找不到 evals.json：{EVALS_PATH}")
        return 1
    spec = load_json(EVALS_PATH)

    # 1. 数据文件可加载
    if not DATA_PATH.exists():
        errors.append(f"缺少数据文件 data/hofstede-dimensions.json（{DATA_PATH}）")
    else:
        try:
            data = load_json(DATA_PATH)
            country_count = len(data.get("countries", {}))
            print(f"数据文件 OK：{country_count} 国（snapshot={data.get('scraped_at', 'unknown')}）")
        except json.JSONDecodeError as exc:
            errors.append(f"data/hofstede-dimensions.json 不是合法 JSON：{exc}")

    evals = spec.get("evals", [])
    if not evals:
        errors.append("evals.json 中没有任何 evals 用例")

    print(f"\n评测用例（evals.json v{spec.get('version', '?')}）：{len(evals)} 条\n")
    print(f"{'#':>2}  {'模式':<10} {'用例名':<24} {'引用 module':<32} module 存在")
    print("-" * 86)

    for idx, ev in enumerate(evals, 1):
        # 2. 必需字段
        for field in REQUIRED_FIELDS:
            if field not in ev:
                errors.append(f"用例 #{idx} 缺字段：{field}")

        name = str(ev.get("name", "<无名>"))
        mode = str(ev.get("expected_mode", "?"))
        loads = str(ev.get("loads_module", ""))

        # 3. must_have 非空
        must_have = ev.get("must_have", [])
        if not isinstance(must_have, list) or not must_have:
            errors.append(f"用例 #{idx}（{name}）的 must_have 应为非空数组")

        # 4. 引用的 module 文件存在性
        m = MODULE_PATH_RE.search(loads)
        if m:
            rel = m.group(1)
            exists = (SKILL_ROOT / rel).exists()
            status = "✅" if exists else "❌ 缺失"
            if not exists:
                errors.append(f"用例 #{idx}（{name}）引用的文件不存在：{rel}")
        else:
            # 描述性路由（如“直接走 SKILL.md 第五节”），不校验文件
            status = "—（描述性）"

        print(f"{idx:>2}  {mode:<10} {name:<24} {loads[:30]:<32} {status}")

    print("-" * 86)
    if errors:
        print(f"\n[FAIL] 发现 {len(errors)} 个问题：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\n[OK] 全部 {len(evals)} 条用例结构合法，module 引用齐全。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
