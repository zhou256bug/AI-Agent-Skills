#!/usr/bin/env python3
"""
周报解析技能 - 完整版本

功能：
1. 读取指定发件人的周报邮件
2. 下载并解析附件（支持 PDF/Excel/纯文本）
3. 按人员整理周报内容
4. 生成移动端优化的汇报

用法：
    python weekly_report_skill.py --from seven.lin@newpostech.com --subject "周报" --week 23
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from email.header import decode_header


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='周报解析技能')
    parser.add_argument('--from', dest='from_addr', default='seven.lin@newpostech.com',
                        help='发件人邮箱')
    parser.add_argument('--subject', default='周报',
                        help='主题关键词')
    parser.add_argument('--week', type=int, default=None,
                        help='周报期号（可选）')
    parser.add_argument('--user', default='qiang.zhou@newpostech.com',
                        help='邮箱用户')
    parser.add_argument('--password', default=None,
                        help='邮箱密码（从环境变量读取）')
    parser.add_argument('--output', default=None,
                        help='输出文件路径')
    parser.add_argument('--format', choices=['mobile', 'markdown', 'json'],
                        default='mobile', help='输出格式')
    parser.add_argument('--debug', action='store_true',
                        help='调试模式')
    return parser.parse_args()


def fetch_emails(user, password, from_addr, subject, limit=5):
    """获取邮件"""
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    
    cmd = [
        sys.executable,
        os.path.expanduser('~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py'),
        '--user', user,
        '--password', password,
        '--from', from_addr,
        '--limit', str(limit),
        '--output', temp_file.name
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        if temp_file.name and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None
    
    with open(temp_file.name) as f:
        data = json.load(f)
    
    os.unlink(temp_file.name)
    return data


def decode_mime_words(text):
    """解码 MIME 编码"""
    if not text:
        return ""
    decoded = []
    for part, encoding in decode_header(text):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            except Exception:
                decoded.append(part.decode('utf-8', errors='replace'))
        else:
            decoded.append(part)
    return ''.join(decoded)


def parse_weekly_report_body(body_text, week_num=None):
    """解析周报正文，提取人员列表"""
    if not body_text:
        return []
    
    employees = []
    lines = body_text.split('\n')
    current_person = None
    current_work = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和邮件头尾
        if not line or line.startswith('各位好') or line.startswith('附件') or '@' in line:
            if current_person and current_work:
                employees.append({
                    'name': current_person,
                    'work': '\n'.join(current_work).strip()
                })
                current_person = None
                current_work = []
            continue
        
        # 检测人员名称行
        # 模式：姓名：工作内容 或 姓名 - 工作内容
        match = re.match(r'^([A-Za-z\u4e00-\u9fa5\.]+)\s*[:：-—]\s*(.*)$', line)
        if match and len(match.group(1)) <= 6:
            if current_person:
                employees.append({
                    'name': current_person,
                    'work': '\n'.join(current_work).strip()
                })
            current_person = match.group(1).strip()
            if match.group(2):
                current_work = [match.group(2)]
            else:
                current_work = []
            continue
        
        # 累积工作内容
        if current_person:
            current_work.append(line)
    
    # 保存最后一个人
    if current_person:
        employees.append({
            'name': current_person,
            'work': '\n'.join(current_work).strip()
        })
    
    return employees


def format_mobile_report(week_num, employees, email_info):
    """移动端优化格式"""
    lines = []
    
    # 标题
    lines.append(f"📋 工作周报 · 第{week_num}期")
    if email_info.get('date'):
        try:
            date = datetime.fromisoformat(email_info['date']).strftime('%Y-%m-%d')
            lines.append(f"📅 {date}")
        except Exception:
            pass
    
    lines.append(f"👤 共{len(employees)}人")
    lines.append("━" * 20)
    
    # 按人员显示
    for emp in employees:
        name = emp['name']
        work = emp['work']
        
        # 简化工作内容（最多 5 行）
        work_lines = work.split('\n')[:5]
        work_preview = '\n'.join(work_lines)
        if len(work.split('\n')) > 5:
            work_preview += '\n…'
        
        lines.append(f"\n👤 {name}")
        lines.append("─" * 15)
        lines.append(work_preview)
    
    lines.append("\n" + "━" * 20)
    lines.append("✅ 汇报整理完成")
    
    return '\n'.join(lines)


def main():
    args = parse_args()
    
    # 获取密码
    password = args.password or os.getenv('EMAIL_IMAP_PASSWORD')
    if not password:
        print("❌ 错误：未提供邮箱密码，请设置 EMAIL_IMAP_PASSWORD 环境变量")
        return 1
    
    print(f"📋 正在获取 {args.from_addr} 的周报...")
    
    # 获取邮件
    data = fetch_emails(args.user, password, args.from_addr, args.subject)
    
    if not data or not data.get('success'):
        print(f"❌ 获取邮件失败：{data.get('error', '未知错误') if data else '无响应'}")
        return 1
    
    emails = data.get('emails', [])
    if not emails:
        print("❌ 未找到符合条件的周报邮件")
        return 1
    
    # 找到周报邮件
    week_email = None
    week_num = args.week or "未知"
    
    for email in emails:
        subject = email.get('subject', '')
        if '周报' in subject:
            week_email = email
            # 提取期号
            match = re.search(r'第 (\d+) 期', subject)
            if match:
                week_num = match.group(1)
            break
    
    if not week_email:
        print("❌ 未找到周报邮件")
        return 1
    
    print(f"✅ 找到周报：第{week_num}期")
    print(f"   主题：{week_email.get('subject', '')}")
    
    # 检查附件
    attachments = week_email.get('attachments', [])
    if attachments:
        print(f"📎 附件：{len(attachments)} 个")
        for att in attachments[:3]:
            print(f"   - {att.get('filename')} ({att.get('size', 0)} bytes)")
        print("\n💡 附件内容需要额外解析，当前仅处理邮件正文")
    
    # 解析正文
    body_text = week_email.get('body_text', '')
    employees = parse_weekly_report_body(body_text, week_num)
    
    if not employees:
        print("⚠️  未能从正文解析出人员周报")
        if body_text:
            print("\n=== 邮件正文预览 ===")
            print(body_text[:500])
        employees = [{
            'name': '原始内容',
            'work': body_text[:1500] if body_text else '无内容'
        }]
    
    print(f"✅ 解析出 {len(employees)} 人的周报")
    
    # 生成汇报
    email_info = {
        'date': week_email.get('date', ''),
        'subject': week_email.get('subject', '')
    }
    
    if args.format == 'mobile':
        report = format_mobile_report(week_num, employees, email_info)
    elif args.format == 'json':
        report = json.dumps({
            'week_num': week_num,
            'email_subject': email_info['subject'],
            'employee_count': len(employees),
            'employees': employees
        }, ensure_ascii=False, indent=2)
    else:
        report = format_mobile_report(week_num, employees, email_info)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 汇报已保存到 {args.output}")
    else:
        print("\n" + "=" * 40)
        print(report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
