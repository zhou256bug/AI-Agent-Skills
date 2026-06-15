# 收件箱扫描摘要 · 手机 PDF 工作流

> **铁律**：手机竖版 PDF **必须**走 `scripts/render_mobile_pdf.py`（`mobile-default`，284pt ≈ 100mm）。  
> 禁止 Agent 现场手写 HTML/CSS。

## 何时生成 PDF

- **cron `--deliver`**：`run_scan.py` 归档 Markdown 后**自动**渲 PDF，微信推送以 PDF 为 `media_path`
- 用户说「发 PDF」「手机看」「推送扫描报告」
- 手动补渲已有 `.md`：

```bash
python3 huazhirong-inbox-watch/scripts/render_scan_pdf.py \
  --body-md output/scans/2026-06-15_10-00_inbox_scan.md
```

## 可选依赖

| 依赖 | 用途 |
|------|------|
| `weasyprint` | HTML → PDF |
| `ghostscript` | 体积优化 |
| `PyMuPDF`（`fitz`） | 裁剪白边 |
| Noto Sans SC | 中文渲染 |

未安装时：**不阻塞**扫描与 Markdown 归档；`--deliver` 降级为推送 Markdown 或纯文本，并在输出中说明缺依赖。

## 标准命令

**便捷入口**（推荐）：

```bash
python3 huazhirong-inbox-watch/scripts/render_scan_pdf.py \
  --title "收件箱扫描" \
  --body-md output/scans/2026-06-15_10-00_inbox_scan.md
```

**底层脚本**（与跨文化 / 法务同款预设）：

```bash
python3 huazhirong-inbox-watch/scripts/render_mobile_pdf.py \
  --preset mobile-default \
  --title "📬 收件箱扫描" \
  --body-md output/scans/2026-06-15_10-00_inbox_scan.md \
  --output output/scans/2026-06-15_10-00_inbox_scan.pdf \
  --brand-color "#1565c0"
```

## 归档路径

| 类型 | 路径 |
|------|------|
| Markdown | `output/scans/YYYY-MM-DD_HH-MM_inbox_scan.md` |
| PDF | 同 stem 的 `.pdf` |

## Cron 集成

`run_scan.py --deliver` 流程：

1. 写 `.md`
2. `render_scan_pdf.py` → `.pdf`
3. 微信 bridge：`media_path` 优先 PDF，失败则用 `.md`

Agent prompt 见 `references/agent-cron-prompt.md`。
