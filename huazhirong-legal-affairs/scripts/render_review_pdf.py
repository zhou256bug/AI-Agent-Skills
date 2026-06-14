#!/usr/bin/env python3
"""法务审核意见 → 手机竖版 PDF 便捷入口。

封装 render_mobile_pdf.py，自动解析归档路径与法务默认配色。

用法：
    python3 scripts/render_review_pdf.py \\
      --title "7-Labs 经销合同审核" \\
      --body-md output/合同/审核记录/2026-06-14_7-Labs_合同审核.md \\
      --party "7-Labs" --mode A

    python3 scripts/render_review_pdf.py \\
      --title "采购合同审核" --body-md /tmp/review.md \\
      --output output/合同/采购/审核记录/custom.pdf
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legal_affairs_config as cfg  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = SKILL_ROOT / "scripts" / "render_mobile_pdf.py"

MODE_SUBDIR: dict[str, Path] = {
    "A": cfg.ARCHIVE_REVIEW,
    "E": cfg.ARCHIVE_REVIEW,
    "B": cfg.ARCHIVE_PROCUREMENT,
    "C": cfg.ARCHIVE_LABOR,
    "D": cfg.ARCHIVE_LABOR,
    "F": cfg.ARCHIVE_EQUITY,
    "G": cfg.ARCHIVE_EQUITY,
    "H": cfg.ARCHIVE_REVIEW,
}

DEFAULT_BRAND = "#1a365d"


def _safe_filename(name: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]', "_", name.strip())
    return s[:80] if s else "合同审核"


def default_output(party: str, mode: str) -> Path:
    sub = MODE_SUBDIR.get(mode.upper(), cfg.ARCHIVE_REVIEW)
    today = date.today().isoformat()
    stem = f"{today}_{_safe_filename(party)}_合同审核"
    return sub / f"{stem}.pdf"


def main() -> int:
    parser = argparse.ArgumentParser(description="法务审核意见手机 PDF")
    parser.add_argument("--title", required=True, help="PDF 标题（可含 emoji）")
    parser.add_argument("--body-md", required=True, type=Path, help="审核意见 Markdown")
    parser.add_argument("--output", type=Path, help="输出 PDF 路径（默认按 mode+party 推断）")
    parser.add_argument("--party", default="合同审核", help="对方名/供方名，用于默认文件名")
    parser.add_argument("--mode", default="A", choices=list(MODE_SUBDIR.keys()) + ["J", "S"],
                        help="审核模式，决定默认归档子目录")
    parser.add_argument("--brand-color", default=DEFAULT_BRAND)
    parser.add_argument("--preset", default="mobile-default")
    args = parser.parse_args()

    if not args.body_md.is_file():
        print(f"[FAIL] body-md 不存在：{args.body_md}", file=sys.stderr)
        return 1
    if not RENDER_SCRIPT.is_file():
        print(f"[FAIL] 缺少渲染器：{RENDER_SCRIPT}", file=sys.stderr)
        return 1

    out = args.output or default_output(args.party, args.mode)
    out.parent.mkdir(parents=True, exist_ok=True)

    title = args.title if args.title.startswith("⚖️") else f"⚖️ {args.title}"

    cmd = [
        sys.executable,
        str(RENDER_SCRIPT),
        "--preset", args.preset,
        "--title", title,
        "--body-md", str(args.body_md.resolve()),
        "--output", str(out.resolve()),
        "--brand-color", args.brand_color,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return result.returncode

    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
