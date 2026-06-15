#!/usr/bin/env python3
"""inbox-watch 评测 harness（纯标准库）。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = SKILL_ROOT / "evals.json"
MODULE_PATH_RE = re.compile(
    r"((?:references|data|scripts)/[\w./-]+(?:\.md|\.json|\.py)?)"
)
REQUIRED = ("name", "input", "expected_mode", "expected", "must_have", "loads_module")


def main() -> int:
    errors: list[str] = []
    if not EVALS_PATH.is_file():
        print(f"[FAIL] 缺少 {EVALS_PATH}")
        return 1
    spec = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    evals = spec.get("evals", [])
    print(f"评测用例 v{spec.get('version', '?')}：{len(evals)} 条\n")
    print(f"{'#':>2}  {'模式':<4} {'用例':<22} {'引用':<32} OK")
    print("-" * 72)
    for i, ev in enumerate(evals, 1):
        for f in REQUIRED:
            if f not in ev:
                errors.append(f"#{i} 缺 {f}")
        loads = str(ev.get("loads_module", ""))
        m = MODULE_PATH_RE.search(loads)
        ok = "—"
        if m:
            rel = m.group(1)
            exists = (SKILL_ROOT / rel).is_file()
            ok = "✅" if exists else "❌"
            if not exists:
                errors.append(f"#{i} 缺文件 {rel}")
        print(f"{i:>2}  {ev.get('expected_mode','?'):<4} {ev.get('name','')[:20]:<22} {loads[:30]:<32} {ok}")
    print("-" * 72)
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[OK] 全部 {len(evals)} 条合法")
    return 0


if __name__ == "__main__":
    sys.exit(main())
