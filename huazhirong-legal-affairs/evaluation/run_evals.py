#!/usr/bin/env python3
"""华智融法务 skill 的评测 / 自检 harness（纯标准库）。

1. 校验 evals.json 结构
2. 校验引用的 module / references 文件存在
3. 校验 data/jurisdiction-index.json 可加载
4. 打印用例汇总表

用法：
    python3 evaluation/run_evals.py
    python3 huazhirong-legal-affairs/evaluation/run_evals.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = SKILL_ROOT / "evals.json"
DATA_PATH = SKILL_ROOT / "data" / "jurisdiction-index.json"

MODULE_PATH_RE = re.compile(
    r"((?:modules|references|frameworks|data)/[\w./-]+(?:\.md|\.json)?)"
)

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

    if not DATA_PATH.exists():
        errors.append(f"缺少数据文件 data/jurisdiction-index.json（{DATA_PATH}）")
    else:
        try:
            data = load_json(DATA_PATH)
            j_count = len(data.get("jurisdictions", {}))
            print(f"数据文件 OK：{j_count} 个法域（v{data.get('version', '?')}）")
        except json.JSONDecodeError as exc:
            errors.append(f"jurisdiction-index.json 不是合法 JSON：{exc}")

    evals = spec.get("evals", [])
    if not evals:
        errors.append("evals.json 中没有任何 evals 用例")

    print(f"\n评测用例（evals.json v{spec.get('version', '?')}）：{len(evals)} 条\n")
    print(f"{'#':>2}  {'模式':<6} {'用例名':<28} {'引用':<36} 存在")
    print("-" * 90)

    for idx, ev in enumerate(evals, 1):
        for field in REQUIRED_FIELDS:
            if field not in ev:
                errors.append(f"用例 #{idx} 缺字段：{field}")

        name = str(ev.get("name", "<无名>"))
        mode = str(ev.get("expected_mode", "?"))
        loads = str(ev.get("loads_module", ""))

        must_have = ev.get("must_have", [])
        if not isinstance(must_have, list) or not must_have:
            errors.append(f"用例 #{idx}（{name}）的 must_have 应为非空数组")

        m = MODULE_PATH_RE.search(loads)
        if m:
            rel = m.group(1)
            exists = (SKILL_ROOT / rel).exists()
            status = "✅" if exists else "❌ 缺失"
            if not exists:
                errors.append(f"用例 #{idx}（{name}）引用的文件不存在：{rel}")
        else:
            status = "—（描述性）"

        print(f"{idx:>2}  {mode:<6} {name:<28} {loads[:34]:<36} {status}")

    print("-" * 90)
    if errors:
        print(f"\n[FAIL] 发现 {len(errors)} 个问题：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"\n[OK] 全部 {len(evals)} 条用例结构合法，引用齐全。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
