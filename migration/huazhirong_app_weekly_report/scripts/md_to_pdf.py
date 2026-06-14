#!/usr/bin/env python3
"""
将 Markdown 汇报转换为 PDF 并保存
使用纯 Python 实现，无需外部依赖
"""

import sys
import os
from datetime import datetime

def markdown_to_pdf_simple(markdown_text, output_path):
    """
    简单的 Markdown 转 PDF
    使用 reportlab 如果可用，否则生成 HTML 供转换
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_LEFT
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        story = []
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.2*inch))
            elif line.startswith('# '):
                story.append(Paragraph(line[2:], title_style))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
                story.append(Spacer(1, 0.05*inch))
            elif line.startswith('• ') or line.startswith('- '):
                story.append(Paragraph(f"• {line[2:]}", styles['Normal']))
            elif line.startswith('━'):
                story.append(Paragraph("─" * 50, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            else:
                # 普通文本
                if line:
                    story.append(Paragraph(line, styles['Normal']))
        
        doc.build(story)
        return True, "reportlab"
        
    except ImportError:
        # reportlab 不可用，生成 HTML 文件
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(markdown_to_html(markdown_text))
        return False, f"html (saved to {html_path})"


def markdown_to_html(md_text):
    """简单的 Markdown 转 HTML"""
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; line-height: 1.6; }
h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
h2 { color: #555; margin-top: 20px; }
h3 { color: #666; }
hr { border: none; border-top: 1px solid #ccc; margin: 20px 0; }
</style>
</head>
<body>
"""
    
    lines = md_text.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            html += '<br>\n'
        elif line_stripped.startswith('# '):
            html += f'<h1>{line_stripped[2:]}</h1>\n'
        elif line_stripped.startswith('## '):
            html += f'<h2>{line_stripped[3:]}</h2>\n'
        elif line_stripped.startswith('### '):
            html += f'<h3>{line_stripped[4:]}</h3>\n'
        elif line_stripped.startswith('• ') or line_stripped.startswith('- '):
            html += f'<li>{line_stripped[2:]}</li>\n'
        elif line_stripped.startswith('━'):
            html += '<hr>\n'
        else:
            if line_stripped:
                html += f'<p>{line_stripped}</p>\n'
    
    html += '</body></html>'
    return html


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法：python md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    success, format_used = markdown_to_pdf_simple(md_content, output_path)
    
    if success:
        print(f"✅ PDF 已生成：{output_path} (使用 {format_used})")
    else:
        print(f"⚠️  {format_used}")
    
    sys.exit(0 if success else 1)
