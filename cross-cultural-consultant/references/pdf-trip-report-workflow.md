# PDF 出差报告生成工作流（跨文化顾问配套）

**场景**：跨文化画像输出后，菜头（中国管理者）要求输出可打印的 PDF 带出国

**用户偏好**：
- **手机滑读**（菜头最新偏好）：手机竖版长条形 PDF，宽度 160mm/390px，一列到底不分页。用 `@page { size: 160mm 3000mm; margin: 0; }` 避免分页。直接调 weasyprint + GhostScript（见下方 PDF 生成工作流 选项B）
- **可打印**（备选）：A4 版式 HTML → pdfprint 转 PDF。**不要用 Python PIL/reportlab 逐像素绘制**。

## 工作流（选项A：A4 可打印版）

## 工作流（选项B：手机长条形版 — 菜头当前偏好）

**2026-06-07 起：必须走 `scripts/render_mobile_pdf.py`，禁止 agent 手写 CSS。**

当菜头说"手机看"、"一列到底"、"不要分页"、"长条图"时：

```bash
python3 scripts/render_mobile_pdf.py \
  --title "国家文化画像 — 意大利" \
  --body-md /tmp/report-body.md \
  --output newpos/出差报告/意大利文化画像_YYYYMMDD.pdf \
  --brand-color "#009739"
```

脚本锁定：284pt 宽、10pt 正文、NotoSC、weasyprint 直出 + PyMuPDF 裁剪，无 pdfprint。

旧流程（手写 HTML）仅作参考：

1. **编写 HTML 模板**（内联 CSS，宽度固定 390px/160mm）
   - 页面尺寸：`@page { size: 160mm 3000mm; margin: 0; }`（超大高度避免分页）
   - 样式全部内联在 `<style>` 中
   - 字体：`@font-face { font-family:'NotoSC'; src:url('file:///Users/ericstudio/.local/share/fonts/NotoSansSC.ttf'); }`
   - 正文 12pt，标题 15-16pt
   - 卡片式布局（flexbox），不用密集表格

2. **生成 PDF**（⚠️ 不要走 pdfprint，它会对完整 HTML 做二次包装导致中文乱码）
   ```python
   import subprocess, os
   # weasyprint
   r1 = subprocess.run(['/opt/homebrew/bin/weasyprint', 'input.html', '/tmp/temp.pdf'], capture_output=True, timeout=60)
   # GhostScript 优化
   r2 = subprocess.run(['/opt/homebrew/bin/gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.7',
       '-dPDFSETTINGS=/prepress', '-dNOPAUSE', '-dQUIET', '-dBATCH',
       '-sOutputFile=output.pdf', '/tmp/temp.pdf'], capture_output=True, timeout=60)
   os.unlink('/tmp/temp.pdf')
   ```

3. **归档**（同上）

## ⚠️ pdfprint 完整 HTML 陷阱（2026-06-04 血泪教训）

pdfprint 对以 `<!DOCTYPE` 或 `<html` 开头的输入，会检测为 HTML 模式，然后**把完整 HTML 再包一层到自己的 FONT_CSS 模板中**，导致：
- HTML 双重嵌套
- 你自己的 font-family 声明被覆盖
- 中文渲染为乱码

**规则**：给 pdfprint 只传 Markdown 内容（走 md2h 路径）。完整 HTML 内容一律直接调 weasyprint。

1. **编写 HTML 模板**（内联 CSS，纯 A4 尺寸）
   - 页面尺寸：`@page { size: A4; margin: 1cm 1.5cm; }`
   - 品牌色：根据目标国确定（日本 #8B0000 深红、墨西哥 #006341 绿、埃及 #C8102E 红等）
   - 表格用 `<table>` + `<style>`，字段名用粗体
   - 关键数据用 `<span class="highlight">` 高亮标记（如 |Δ|>20 的维度）
   - 底部加注脚：`数据快照:YYYY-MM-DD | Skill v0.4.0`

2. **生成 PDF**
   ```
   python3 /Users/ericstudio/.local/bin/pdfprint report.html -o report.pdf
   ```

3. **归档**
   - 存 `newpos/出差报告/国家名文化画像报告_v版本_日期.pdf`
   - 微信或飞书发给菜头确认

## HTML 模板骨架

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<style>
@page { size: A4; margin: 1cm 1.5cm; }
body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 11pt; color: #333; line-height: 1.6; }
h1 { font-size: 18pt; color: #BRAND_COLOR; border-bottom: 2px solid #CCC; padding-bottom: 4px; }
h2 { font-size: 14pt; color: #BRAND_COLOR; margin-top: 1.2em; }
table { width: 100%; border-collapse: collapse; margin: 0.8em 0; }
th, td { border: 1px solid #CCC; padding: 6px 10px; text-align: center; }
th { background: #BRAND_COLOR; color: white; }
.highlight { background: #FFF3CD; font-weight: bold; }
.warning { color: #CC0000; }
.footer { margin-top: 2em; font-size: 9pt; color: #999; border-top: 1px solid #DDD; padding-top: 0.5em; }
</style>
</head>
<body>
<!-- content here -->
<div class="footer">数据快照:YYYY-MM-DD | Skill v0.4.0</div>
</body>
</html>
```

## 注意事项

- pdfprint（weasyprint 封装）支持所有标准 CSS，包括 flexbox/grid
- 表格中的长文本自动换行，不用固定列宽
- 中文需指定 `PingFang SC` 等系统字体，macOS 自带
- 输出前检查 HTML 构建是否正确（直接浏览器预览）
- 典型页数：2-4 页 A4（内含数据表 + 场景建议 + 工具箱）
