#!/usr/bin/env python3
"""名片图片 OCR（可选依赖 tesseract）。

供 C 模式会后「名片收网」使用。Agent 在本 skill 内直接调用，不委派外部 profile。

退出码：
  0 — OCR 成功（文本输出到 stdout 或 --json）
  1 — 输入文件无效
  2 — 未安装 tesseract（Agent 应改用识图或请用户粘贴文字）
  3 — OCR 结果为空
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TESSERACT = shutil.which("tesseract")


def _validate_image(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"图片不存在：{path}")
    if path.stat().st_size == 0:
        raise ValueError(f"图片为空：{path}")
    # 可选：用 Pillow 校验是否为可读图片
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        return
    with Image.open(path) as im:
        im.verify()


def _run_tesseract(image: Path, lang: str, timeout: int) -> str:
    if not TESSERACT:
        return ""
    cmd = [TESSERACT, str(image), "stdout", "-l", lang, "--psm", "6"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"tesseract 失败：{err}")
    return proc.stdout.strip()


def _copy_attachment(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image  # noqa: PLC0415

        with Image.open(src) as im:
            rgb = im.convert("RGB")
            rgb.save(dest, format="JPEG", quality=90)
    except ImportError:
        import shutil as sh

        sh.copy2(src, dest)
    return dest.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="名片 OCR（tesseract 可选；未安装时退出码 2）"
    )
    parser.add_argument("--image", required=True, help="名片图片路径")
    parser.add_argument(
        "--lang", default="chi_sim+eng", help="tesseract 语言，默认 chi_sim+eng"
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument(
        "--save-attachment",
        metavar="PATH",
        help="复制/转换图片到 output/crm/附件/…（目录不存在则创建）",
    )
    parser.add_argument("--timeout", type=int, default=60, help="tesseract 超时秒数")
    args = parser.parse_args()

    image = Path(args.image).expanduser().resolve()
    try:
        _validate_image(image)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    saved: str | None = None
    if args.save_attachment:
        dest = Path(args.save_attachment)
        if not dest.is_absolute():
            skill_root = Path(__file__).resolve().parent.parent
            dest = (skill_root / dest).resolve()
        saved = str(_copy_attachment(image, dest))

    if not TESSERACT:
        msg = (
            "未找到 tesseract。请安装系统包 tesseract-ocr 及 chi_sim/eng 语言包，"
            "或由 Agent 使用识图读取名片。"
        )
        print(msg, file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {"ok": False, "error": "tesseract_missing", "attachment": saved},
                    ensure_ascii=False,
                )
            )
        return 2

    try:
        text = _run_tesseract(image, args.lang, args.timeout)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 3

    if not text:
        print("OCR 结果为空，请检查图片清晰度或改用 Agent 识图。", file=sys.stderr)
        if args.json:
            print(
                json.dumps(
                    {"ok": False, "error": "empty_ocr", "attachment": saved},
                    ensure_ascii=False,
                )
            )
        return 3

    if args.json:
        print(
            json.dumps(
                {"ok": True, "text": text, "attachment": saved, "lang": args.lang},
                ensure_ascii=False,
            )
        )
    else:
        print(text)
        if saved:
            print(f"\n[attachment] {saved}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
