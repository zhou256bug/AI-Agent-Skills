#!/usr/bin/env python3
"""
改进版 Markdown 转 PDF - 支持中文和更好看的格式
"""

import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def create_pdf(markdown_path, pdf_path):
    """创建格式更好的 PDF"""
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    story = []
    
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 0.15*cm))
            continue
        
        # 标题处理
        if line.startswith('📋') or line.startswith('# '):
            title = line.replace('📋', '').replace('# ', '').strip()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.5*cm))
        
        elif line.startswith('🏢') or line.startswith('## '):
            heading = line.replace('🏢', '').replace('## ', '').strip()
            story.append(Paragraph(heading, heading_style))
            story.append(Spacer(1, 0.3*cm))
        
        elif line.startswith('📅') or line.startswith('### '):
            subheading = line.replace('📅', '').replace('### ', '').strip()
            story.append(Paragraph(subheading, subheading_style))
            story.append(Spacer(1, 0.2*cm))
        
        elif line.startswith('━'):
            story.append(Paragraph("─" * 50, normal_style))
            story.append(Spacer(1, 0.3*cm))
        
        elif line.startswith('• ') or line.startswith('- '):
            text = line[2:].strip()
            story.append(Paragraph(f"• {text}", normal_style))
        
        elif line.startswith('👤'):
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(line, subheading_style))
        
        elif line.startswith('⭐') or line.startswith('📊') or line.startswith('🔴'):
            story.append(Spacer(1, 0.4*cm))
            story.append(Paragraph(line, heading_style))
            story.append(Spacer(1, 0.2*cm))
        
        elif line.startswith('1️⃣') or line.startswith('2️⃣') or line.startswith('3️⃣'):
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(line, normal_style))
        
        elif line.startswith('   •'):
            text = line.strip().replace('•', '  •')
            story.append(Paragraph(text, normal_style))
        
        elif line.startswith('📄') or line.startswith('✅'):
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(line, normal_style))
        
        else:
            if line and len(line) > 2:
                story.append(Paragraph(line, normal_style))
    
    doc.build(story)
    return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法：python md_to_pdf_v2.py <input.md> <output.pdf>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        create_pdf(input_path, output_path)
        print(f"✅ PDF 已生成：{output_path}")
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        sys.exit(1)
