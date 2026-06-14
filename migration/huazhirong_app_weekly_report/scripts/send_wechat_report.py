#!/usr/bin/env python3
"""
周报微信发送脚本 - 优化格式和顺序

发送顺序：
1. Markdown 文本汇报
2. PDF 文件附件
"""

import subprocess
import sys
from pathlib import Path

def send_wechat_report(week_num, recipient, pdf_path, markdown_path=None):
    """发送周报到微信"""
    
    # 读取 Markdown 内容
    if markdown_path and Path(markdown_path).exists():
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    else:
        md_content = generate_default_report(week_num)
    
    # 优化格式
    optimized_content = optimize_for_wechat(md_content, week_num, pdf_path)
    
    # 发送消息
    send_cmd = [
        'hermes', 'chat', '-q',
        f'发送以下消息到微信 {recipient}：\n\n{optimized_content}'
    ]
    
    result = subprocess.run(send_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 消息已发送到 {recipient}")
        
        # 等待 2 秒后发送 PDF 文件
        import time
        time.sleep(2)
        
        # 发送 PDF 文件
        send_file_cmd = [
            'hermes', 'chat', '-q',
            f'发送文件 {pdf_path} 到微信 {recipient}，并说明"📄 完整报告如上"'
        ]
        
        result2 = subprocess.run(send_file_cmd, capture_output=True, text=True)
        
        if result2.returncode == 0:
            print(f"✅ PDF 文件已发送到 {recipient}")
        else:
            print(f"⚠️  文件发送失败：{result2.stderr}")
    else:
        print(f"❌ 发送失败：{result.stderr}")
    
    return result.returncode == 0


def optimize_for_wechat(content, week_num, pdf_path):
    """优化格式以适应微信显示"""
    
    # 简化 PDF 路径显示
    pdf_filename = Path(pdf_path).name
    short_path = f"~/weekly-reports/week-{week_num}/{pdf_filename}"
    
    # 替换分隔符（避免微信换行问题）
    content = content.replace('━' * 40, '─' * 30)
    content = content.replace('━━━━━━━━━━━━━━━━━━━━', '─' * 30)
    
    # 替换 PDF 路径
    content = content.replace(
        '~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf',
        short_path
    )
    
    return content


def generate_default_report(week_num):
    """生成默认汇报内容"""
    return f"""📋 工作周报 · 第{week_num}期
🏢 海外应用开发部
📅 2026.06.01-06.07
{'─' * 30}

⭐ 您的关注
{'─' * 30}

💡 暂无关注配置

📝 如何添加关注：
直接告诉强仔：
  • 关注某人："关注周强"
  • 关注项目："关注 NEWSTORE 项目"

{'─' * 30}

📊 本周概览
{'─' * 30}
• 总人数：15 人
• 周期：2026.06.01-06.07

{'─' * 30}

🔴 重点成果（Top 5）
{'─' * 30}

1️⃣ 林旭伟 - Airwallex 项目 UI 适配完成
2️⃣ 丁璞 - Winfopay 9220U 识别问题解决
3️⃣ 胡陈琛 - 欧洲装机程序开发
4️⃣ 李家俊 - OMA 5320 固件交付
5️⃣ 李响 - 土耳其税控模块跟进

{'─' * 30}

📄 完整报告：~/weekly-reports/week-{week_num}/week-{week_num}.pdf
✅ 周报整理完成
"""


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='周报微信发送')
    parser.add_argument('--week', type=str, default='23', help='周报期号')
    parser.add_argument('--recipient', type=str, default='o9cq809nVomNJ57JU7rlAbWnk290@im.wechat', help='微信用户 ID')
    parser.add_argument('--pdf', type=str, required=True, help='PDF 文件路径')
    parser.add_argument('--markdown', type=str, help='Markdown 文件路径')
    args = parser.parse_args()
    
    success = send_wechat_report(args.week, args.recipient, args.pdf, args.markdown)
    sys.exit(0 if success else 1)
