# PDF 出差报告生成工作流（跨文化顾问配套）

> **现行铁律（2026-06-07 起）**：手机竖版 PDF **必须**走 `scripts/render_mobile_pdf.py`（见 SKILL.md §十三）。  
> 本文档选项 A / 旧版手写 HTML / pdfprint 仅作**历史参考**；**禁止**在输出或命令中写入 `/Users/...` 等本机绝对路径。

**场景**：跨文化画像输出后，老板（中国管理者）要求输出可打印或手机可读的 PDF。

**用户偏好**：
- **手机滑读**（推荐）：手机竖版长条形 PDF，一列到底。走 `render_mobile_pdf.py`（284pt / 10pt NotoSC）。
- **可打印**（备选）：A4 HTML → weasyprint；**不要**用 Python PIL/reportlab 逐像素绘制。

---

## 工作流（现行 · 手机长条形版）

当老板说「手机看」「一列到底」「不要分页」「长条图」时：

```bash
python3 scripts/render_mobile_pdf.py \
  --title "国家文化画像 — 意大利" \
  --body-md /tmp/report-body.md \
  --output output/出差报告/意大利文化画像_YYYYMMDD.pdf \
  --brand-color "#009739"
```

脚本锁定：284pt 宽、10pt 正文、NotoSC、weasyprint 直出 + PyMuPDF 裁剪。

归档默认在技能目录下 `output/`（可配置；已在 `.gitignore`）。生成后推送 PDF 并告知相对路径。

---

## 工作流（备选 · A4 可打印版）

1. 使用 `templates/A4-report-template.html` 或等价内联 CSS HTML
2. 页面：`@page { size: A4; margin: 1cm 1.5cm; }`
3. 字体：使用系统自带中文字体（如 PingFang SC、Microsoft YaHei、Noto Sans SC），**不要**写死 `file:///Users/...` 字体路径
4. 生成：

```bash
weasyprint report.html output/出差报告/国家名文化画像报告_YYYYMMDD.pdf
```

5. 可选 GhostScript 压缩（`gs` 在 PATH 中即可，路径因系统而异）

---

## ⚠️ pdfprint 完整 HTML 陷阱（历史教训）

pdfprint 对完整 HTML 会做二次包装，易导致中文乱码。**新流程不要用 pdfprint 包完整 HTML**。

若必须用 pdfprint，只传 Markdown（走 md2h），且 `pdfprint` / `weasyprint` 均使用 PATH 中的命令，例如：

```bash
weasyprint report.html /tmp/report.pdf
```

---

## HTML 模板骨架（A4 参考）

见 `templates/A4-report-template.html`，或：

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<style>
@page { size: A4; margin: 1cm 1.5cm; }
body { font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; font-size: 11pt; color: #333; line-height: 1.6; }
h1 { font-size: 18pt; color: #BRAND_COLOR; border-bottom: 2px solid #CCC; padding-bottom: 4px; }
/* … 见 templates/A4-report-template.html … */
</style>
</head>
<body>
<div class="footer">数据快照:YYYY-MM-DD | Skill v0.8.1</div>
</body>
</html>
```

## 注意事项

- 中文 PDF 需本机有中文字体；`render_mobile_pdf.py` 用 `Path.home()` 与系统字体，不绑定特定用户名目录
- 典型页数：手机版 1 页长条；A4 版 2–4 页
