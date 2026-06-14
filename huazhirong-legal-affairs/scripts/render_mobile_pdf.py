#!/usr/bin/env python3
"""Render mobile-friendly single-column Chinese PDF.

Presets:
  mobile-default (default) — 跨文化手机竖版 PDF (~284pt)
  weekly-report   — 总裁办周报 W22 完整版 (~160mm, 六段结构)
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

WEASYPRINT = shutil.which("weasyprint") or "/opt/homebrew/bin/weasyprint"
GS = shutil.which("gs") or "/opt/homebrew/bin/gs"

NOTO_REGULAR = Path.home() / ".local/share/fonts/NotoSansSC.ttf"
NOTO_BOLD_CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/NotoSansSC-Bold.otf"),
    Path.home() / ".local/share/fonts/NotoSansSC-Bold.ttf",
]

CALLOUT_CLASSES = frozenset({"meta", "info", "highlight", "urgent", "callout"})


@dataclass(frozen=True)
class LayoutPreset:
    name: str
    width_pt: float
    page_height_pt: float
    page_margin_pt: str
    body_pt: float
    title_pt: float
    h2_pt: float
    h3_pt: float
    table_pt: float
    footer_pt: float
    pad_x: float
    pad_top: float
    pad_bottom: float
    brand_color: str
    title_color: str
    css_template: str
    default_footer: str


def _noto_bold_path() -> Path | None:
    for p in NOTO_BOLD_CANDIDATES:
        if p.is_file():
            return p
    return None


def _font_face_css() -> str:
    if NOTO_REGULAR.is_file():
        reg = NOTO_REGULAR.as_uri()
        bold = _noto_bold_path()
        lines = [
            f"@font-face {{ font-family: 'NotoSC'; src: url('{reg}'); font-weight: 400; }}",
        ]
        if bold:
            lines.append(
                f"@font-face {{ font-family: 'NotoSC'; src: url('{bold.as_uri()}'); font-weight: 700; }}"
            )
        return "\n".join(lines)
    return ""


MOBILE_CSS = """
%(font_face)s
@page { size: %(width_pt)spt %(height_pt)spt; margin: 0; }
* { box-sizing: border-box; }
html, body {
  width: %(width_pt)spt;
  max-width: %(width_pt)spt;
  margin: 0;
  padding: %(pad_top)spt %(pad_x)spt %(pad_bottom)spt %(pad_x)spt;
  background: #ffffff;
  color: #222222;
  font-family: "NotoSC", "PingFang SC", "STHeiti", "Microsoft YaHei", sans-serif;
  font-size: %(body_pt)spt;
  line-height: 1.65;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
h1 {
  font-size: %(title_pt)spt;
  font-weight: 700;
  margin: 0 0 0.45em 0;
  color: %(title_color)s;
  border-bottom: 2px solid %(brand_color)s;
  padding-bottom: 0.25em;
  line-height: 1.35;
}
h2 {
  font-size: %(h2_pt)spt;
  font-weight: 700;
  margin: 1.05em 0 0.35em 0;
  color: %(brand_color)s;
  line-height: 1.4;
}
h3 {
  font-size: %(h3_pt)spt;
  font-weight: 700;
  margin: 0.85em 0 0.25em 0;
  background: #f0f4f8;
  padding: 0.3em 0.45em;
  line-height: 1.4;
}
p, li { margin: 0.35em 0; padding: 0; }
ul, ol { margin: 0.35em 0; padding-left: 1.15em; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 0.7em 0; }
strong { font-weight: 700; }
blockquote {
  margin: 0.5em 0;
  padding: 0.45em 0.55em;
  border-left: 3px solid %(brand_color)s;
  background: #f8f9fa;
  color: #333;
}
.meta {
  font-size: %(table_pt)spt;
  color: #555;
  background: #f5f5f5;
  padding: 0.45em 0.55em;
  border-radius: 4px;
  margin: 0 0 0.8em 0;
  line-height: 1.5;
}
.info {
  background: #e3f2fd;
  border-left: 4px solid #1976d2;
  padding: 0.5em 0.6em;
  margin: 0.5em 0;
  font-size: %(body_pt)spt;
}
.highlight {
  background: #fff8e1;
  border-left: 4px solid #f9a825;
  padding: 0.5em 0.6em;
  margin: 0.5em 0;
}
.urgent {
  background: #ffebee;
  border-left: 4px solid #c62828;
  padding: 0.5em 0.6em;
  margin: 0.5em 0;
}
.callout {
  background: #f0f4f8;
  border-left: 4px solid %(brand_color)s;
  padding: 0.5em 0.6em;
  margin: 0.5em 0;
}
table {
  width: 100%%;
  border-collapse: collapse;
  margin: 0.45em 0;
  font-size: %(table_pt)spt;
  line-height: 1.45;
}
th, td {
  border: 1px solid #ddd;
  padding: 3px 5px;
  text-align: left;
  vertical-align: top;
  word-break: break-word;
}
th { background: #f0f4f8; font-weight: 700; }
.footer {
  margin-top: 1.2em;
  padding-top: 0.5em;
  border-top: 1px solid #ddd;
  font-size: %(footer_pt)spt;
  color: #666;
}
"""

# W22 周报_W22_20260601_手机长条_完整版.pdf / 总结.html
WEEKLY_CSS = """
%(font_face)s
@page { size: %(width_pt)spt %(height_pt)spt; margin: %(page_margin_pt)s; }
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: %(pad_top)spt %(pad_x)spt %(pad_bottom)spt %(pad_x)spt;
  background: #ffffff;
  color: #333333;
  font-family: "NotoSC", "Noto Sans SC", "PingFang SC", "Apple Color Emoji", "Segoe UI Emoji", sans-serif;
  font-size: %(body_pt)spt;
  line-height: 1.4;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
h1 {
  font-size: %(title_pt)spt;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: %(title_color)s;
  border-bottom: 2.5px solid %(brand_color)s;
  padding-bottom: 5px;
}
h2 {
  font-size: %(h2_pt)spt;
  font-weight: 700;
  margin: 10px 0 4px 0;
  color: #2c3e50;
  border-left: 3.5px solid %(brand_color)s;
  padding-left: 7px;
  line-height: 1.35;
}
h3 {
  font-size: %(h3_pt)spt;
  font-weight: 700;
  margin: 8px 0 3px 0;
  color: #34495e;
  background: none;
  padding: 0;
  line-height: 1.35;
}
p { margin: 1px 0; font-size: %(body_pt)spt; }
li { margin: 0; font-size: %(body_pt)spt; }
ul, ol { margin: 2px 0; padding-left: 15px; }
strong { font-weight: 700; }
.section { margin-bottom: 6px; }
.meta {
  color: #7f8c8d;
  font-size: %(table_pt)spt;
  margin: 0 0 8px 0;
  line-height: 1.45;
  background: none;
  padding: 0;
  border-radius: 0;
}
.meta p { margin: 0 0 3px 0; font-size: %(table_pt)spt; }
.info {
  background: #d1ecf1;
  border-left: 3.5px solid #17a2b8;
  padding: 3px 6px;
  margin: 3px 0;
  border-radius: 2px;
}
.info h3 { margin-top: 4px; }
.highlight {
  background: #fff3cd;
  border-left: 3.5px solid #ffc107;
  padding: 3px 6px;
  margin: 4px 0;
  border-radius: 2px;
  font-size: %(body_pt)spt;
}
.urgent {
  background: #f8d7da;
  border-left: 3.5px solid #dc3545;
  padding: 3px 6px;
  margin: 4px 0;
  border-radius: 2px;
  font-size: %(body_pt)spt;
}
table {
  width: 100%%;
  border-collapse: collapse;
  margin: 3px 0;
  font-size: %(table_pt)spt;
}
th {
  background: %(brand_color)s;
  color: white;
  padding: 2px 4px;
  text-align: left;
  font-size: %(table_pt)spt;
  font-weight: 700;
  border: none;
}
td {
  padding: 1px 4px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: top;
  word-break: break-word;
}
tr:nth-child(even) { background: #f8f9fa; }
td.status-cell {
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
  width: 1.6em;
  padding: 2px 5px;
}
.status-icon {
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
  font-size: 11pt;
  line-height: 1;
  display: inline-block;
}
.footer {
  margin-top: 1em;
  padding-top: 0.4em;
  border-top: 1px solid #ddd;
  font-size: %(footer_pt)spt;
  color: #666;
}
"""

PRESETS: dict[str, LayoutPreset] = {
    "mobile-default": LayoutPreset(
        name="mobile-default",
        width_pt=284,
        page_height_pt=24000,
        page_margin_pt="0",
        body_pt=10,
        title_pt=12,
        h2_pt=8.5,
        h3_pt=8,
        table_pt=7,
        footer_pt=6.5,
        pad_x=12,
        pad_top=15,
        pad_bottom=30,
        brand_color="#006341",
        title_color="#006341",
        css_template=MOBILE_CSS,
        default_footer="手机竖版 284pt · NotoSC",
    ),
    "weekly-report": LayoutPreset(
        name="weekly-report",
        width_pt=284,  # 100mm — 手机阅读标准宽（内容极多时可 --width-mm 110~120）
        page_height_pt=24000,
        page_margin_pt="0",
        body_pt=9,
        title_pt=12,
        h2_pt=9.5,
        h3_pt=8.5,
        table_pt=7,
        footer_pt=6.5,
        pad_x=10,
        pad_top=12,
        pad_bottom=24,
        brand_color="#2980b9",
        title_color="#1a5276",
        css_template=WEEKLY_CSS,
        default_footer="",
    ),
}


def _mm_to_pt(mm: float) -> float:
    return mm / 25.4 * 72.0


def _preset_with_width(preset: LayoutPreset, width_mm: float | None) -> LayoutPreset:
    if width_mm is None:
        return preset
    clamped = max(100.0, min(120.0, width_mm))
    return replace(preset, width_pt=_mm_to_pt(clamped))


def _parse_table_row(line: str) -> list[str]:
    row = line.strip().strip("|")
    cells: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(row):
        if row[i] == "\\" and i + 1 < len(row) and row[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if row[i] == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(row[i])
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line))


_STATUS_INLINE_RE = re.compile(r"([⏳✅🆕⚠🔵🟡🔴🟢]\uFE0F?)")
_STATUS_CELL_RE = re.compile(r"^[⏳✅🆕⚠🔵🟡🔴🟢\uFE0F\s]+$")


def _wrap_status_icons(text: str) -> str:
    return _STATUS_INLINE_RE.sub(r'<span class="status-icon">\1</span>', text)


def _inline_md(text: str) -> str:
    escaped = html.escape(text)
    escaped = _wrap_status_icons(escaped)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def _md_to_html_body(text: str, *, in_callout: bool = False) -> str:
    """Markdown → HTML: headings, lists, tables, nested callout fences."""
    lines = text.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False
    i = 0

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i].rstrip()

        m_callout = re.match(r"^:::(\w+)\s*$", line.strip())
        if m_callout and not in_callout:
            cls = m_callout.group(1).lower()
            if cls in CALLOUT_CLASSES:
                close_lists()
                buf: list[str] = []
                i += 1
                while i < len(lines) and lines[i].strip() != ":::":
                    buf.append(lines[i])
                    i += 1
                inner = _md_to_html_body("\n".join(buf), in_callout=True)
                out.append(f'<div class="{cls}">{inner}</div>')
                if i < len(lines) and lines[i].strip() == ":::":
                    i += 1
                continue

        if not line.strip():
            close_lists()
            i += 1
            continue
        if line.strip() == "---":
            close_lists()
            out.append("<hr>")
            i += 1
            continue
        if "|" in line and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            close_lists()
            headers = _parse_table_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(_parse_table_row(lines[i]))
                i += 1
            out.append("<table><thead><tr>")
            for h in headers:
                out.append(f"<th>{_inline_md(h)}</th>")
            out.append("</tr></thead><tbody>")
            for row in rows:
                out.append("<tr>")
                for cell in row:
                    cls = ' class="status-cell"' if _STATUS_CELL_RE.match(cell.strip()) else ""
                    out.append(f"<td{cls}>{_inline_md(cell)}</td>")
                out.append("</tr>")
            out.append("</tbody></table>")
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{html.escape(m.group(2))}</h{level}>")
            i += 1
            continue
        m = re.match(r"^>\s?(.*)$", line)
        if m:
            close_lists()
            out.append(f"<blockquote>{_inline_md(m.group(1))}</blockquote>")
            i += 1
            continue
        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline_md(m.group(1))}</li>")
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{_inline_md(m.group(2))}</li>")
            i += 1
            continue
        close_lists()
        out.append(f"<p>{_inline_md(line)}</p>")
        i += 1
    close_lists()
    return "\n".join(out)


def _css_for_preset(preset: LayoutPreset, brand_color: str | None) -> str:
    brand = brand_color or preset.brand_color
    title = preset.title_color if brand_color is None else brand
    return preset.css_template % {
        "font_face": _font_face_css(),
        "width_pt": preset.width_pt,
        "height_pt": preset.page_height_pt,
        "page_margin_pt": preset.page_margin_pt,
        "pad_x": preset.pad_x,
        "pad_top": preset.pad_top,
        "pad_bottom": preset.pad_bottom,
        "body_pt": preset.body_pt,
        "title_pt": preset.title_pt,
        "h2_pt": preset.h2_pt,
        "h3_pt": preset.h3_pt,
        "table_pt": preset.table_pt,
        "footer_pt": preset.footer_pt,
        "brand_color": brand,
        "title_color": title,
    }


def build_html(
    *,
    title: str,
    body_html: str,
    preset: LayoutPreset,
    brand_color: str | None,
    footer: str,
) -> str:
    css = _css_for_preset(preset, brand_color)
    footer_block = ""
    if footer:
        footer_block = f'<div class="footer">{html.escape(footer)}</div>'
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
{body_html}
{footer_block}
</body>
</html>
"""


def _weasyprint_env() -> dict[str, str]:
    env = os.environ.copy()
    brew_lib = "/opt/homebrew/lib"
    if Path(brew_lib).is_dir():
        prev = env.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        env["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{brew_lib}:{prev}" if prev else brew_lib
        )
    return env


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    if not Path(WEASYPRINT).is_file():
        raise RuntimeError(f"weasyprint not found at {WEASYPRINT}")
    result = subprocess.run(
        [WEASYPRINT, str(html_path), str(pdf_path)],
        capture_output=True,
        text=True,
        timeout=120,
        env=_weasyprint_env(),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"weasyprint failed ({result.returncode}): {result.stderr[:800]}"
        )
    if not pdf_path.is_file() or pdf_path.stat().st_size < 500:
        raise RuntimeError(f"PDF missing or too small: {pdf_path}")


def crop_pdf_whitespace(pdf_path: Path, *, padding_pt: float = 8.0) -> None:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF (fitz) required for crop") from exc

    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        doc.close()
        return
    page = doc[0]
    blocks = [b for b in page.get_text("blocks") if b[6] == 0]
    if not blocks:
        doc.close()
        return
    min_y = min(b[1] for b in blocks)
    max_y = max(b[3] for b in blocks)
    rect = fitz.Rect(
        0,
        max(0, min_y - padding_pt),
        page.rect.width,
        min(page.rect.height, max_y + padding_pt),
    )
    page.set_cropbox(rect)
    tmp = pdf_path.with_suffix(".crop.pdf")
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    tmp.replace(pdf_path)


def maybe_gs_optimize(pdf_path: Path) -> None:
    if not Path(GS).is_file():
        return
    tmp = pdf_path.with_suffix(".gs.pdf")
    result = subprocess.run(
        [
            GS,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={tmp}",
            str(pdf_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0 and tmp.is_file() and tmp.stat().st_size > 500:
        tmp.replace(pdf_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mobile Chinese PDF (presets: mobile-default, weekly-report)"
    )
    parser.add_argument("--title", required=True, help="Report title (Chinese)")
    parser.add_argument("--output", required=True, type=Path, help="Output .pdf path")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--body-md", type=Path, help="Markdown body file (Chinese)")
    src.add_argument("--body-html", type=Path, help="Pre-built HTML body fragment")
    src.add_argument("--html", type=Path, help="Full HTML file (weasyprint direct)")
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default="mobile-default",
        help="Layout preset (weekly-report = 总裁办周报 W22 格式)",
    )
    parser.add_argument(
        "--width-mm",
        type=float,
        default=None,
        help="Override page width in mm (weekly-report: 100 default, max 120)",
    )
    parser.add_argument(
        "--brand-color",
        default="",
        help="Override accent color (weekly default #2980b9)",
    )
    parser.add_argument("--footer", default=None, help="Footer line (weekly: omit)")
    parser.add_argument("--no-crop", action="store_true")
    parser.add_argument("--no-gs", action="store_true")
    args = parser.parse_args()

    preset = _preset_with_width(PRESETS[args.preset], args.width_mm)
    brand = args.brand_color or None
    footer = args.footer if args.footer is not None else preset.default_footer

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.html:
        render_pdf(args.html, args.output)
    else:
        if args.body_html:
            body_html = args.body_html.read_text(encoding="utf-8")
        else:
            body_html = _md_to_html_body(args.body_md.read_text(encoding="utf-8"))

        doc = build_html(
            title=args.title,
            body_html=body_html,
            preset=preset,
            brand_color=brand,
            footer=footer,
        )
        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(doc)
            tmp_path = Path(tmp.name)
        try:
            render_pdf(tmp_path, args.output)
        finally:
            tmp_path.unlink(missing_ok=True)

    if not args.no_crop:
        crop_pdf_whitespace(args.output)
    if not args.no_gs:
        maybe_gs_optimize(args.output)

    if args.preset == "weekly-report":
        try:
            import fitz

            if fitz.open(args.output).page_count > 1:
                print(
                    "ERROR: weekly-report exceeded single page after crop",
                    file=sys.stderr,
                )
                return 3
        except ImportError:
            pass

    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
