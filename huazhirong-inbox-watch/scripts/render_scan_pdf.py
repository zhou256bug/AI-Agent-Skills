#!/usr/bin/env python3
"""收件箱扫描摘要 → 手机竖版 PDF 便捷入口。

封装 render_mobile_pdf.py（mobile-default，284pt 竖版）。

用法：
    python3 scripts/render_scan_pdf.py \\
      --body-md output/scans/2026-06-15_10-00_inbox_scan.md

    python3 scripts/render_scan_pdf.py \\
      --title "收件箱扫描" --body-md /tmp/scan.md --output out.pdf
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inbox_watch_config as cfg  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = SKILL_ROOT / "scripts" / "render_mobile_pdf.py"
DEFAULT_BRAND = "#1565c0"


def default_output(body_md: Path) -> Path:
    if body_md.suffix.lower() == ".md":
        return body_md.with_suffix(".pdf")
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return cfg.scan_archive_dir() / f"{stamp}_inbox_scan.pdf"


def render_pdf(
    *,
    body_md: Path,
    title: str | None = None,
    output: Path | None = None,
    brand_color: str = DEFAULT_BRAND,
) -> tuple[Path | None, int, str]:
    """渲染 PDF；返回 (路径, 退出码, stderr/stdout 片段)。"""
    if not body_md.is_file():
        return None, 1, f"body-md 不存在：{body_md}"
    if not RENDER_SCRIPT.is_file():
        return None, 1, f"缺少渲染器：{RENDER_SCRIPT}"

    out = output or default_output(body_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf_title = title or "收件箱扫描"
    if not pdf_title.startswith("📬"):
        pdf_title = f"📬 {pdf_title}"

    cmd = [
        sys.executable,
        str(RENDER_SCRIPT),
        "--preset",
        "mobile-default",
        "--title",
        pdf_title,
        "--body-md",
        str(body_md.resolve()),
        "--output",
        str(out.resolve()),
        "--brand-color",
        brand_color,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    detail = (result.stderr or result.stdout or "")[:300]
    if result.returncode != 0:
        return None, result.returncode, detail
    if not out.is_file() or out.stat().st_size == 0:
        return None, 1, "PDF 未生成或为空"
    return out, 0, detail


def main() -> int:
    ap = argparse.ArgumentParser(description="收件箱扫描摘要手机 PDF")
    ap.add_argument("--title", help="PDF 标题")
    ap.add_argument("--body-md", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--brand-color", default=DEFAULT_BRAND)
    args = ap.parse_args()

    path, code, detail = render_pdf(
        body_md=args.body_md,
        title=args.title,
        output=args.output,
        brand_color=args.brand_color,
    )
    if code != 0 or path is None:
        print(detail, file=sys.stderr)
        return code or 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
