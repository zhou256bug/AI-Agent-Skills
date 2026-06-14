#!/usr/bin/env python3
"""
周报整理器 - 从部门周报邮件中提取并按人员整理汇报

用法:
    python weekly_report_parser.py --input week23.json
"""

import json
import argparse
import re
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description='周报整理器')
    parser.add_argument('--input', required=True, help='输入邮件 JSON 文件')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--format', choices=['mobile', 'markdown', 'json'], default='mobile')
    return parser.parse_args()


def parse_weekly_report(body_text):
    """解析周报内容，提取人员周报"""
    if not body_text:
        return []
    
    # 按人员分割周报（假设格式：姓名 + 工作内容）
    # 常见格式：
    # 1. "姓名：工作内容"
    # 2. "姓名 - 工作内容"
    # 3. "【姓名】工作内容"
    # 4. "姓名：\n 工作内容"
    
    employees = []
    
    # 尝试多种分割模式
    lines = body_text.split('\n')
    current_person = None
    current_work = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测是否是人员名称行
        # 模式 1: 姓名：
        match = re.match(r'^([A-Za-z\u4e00-\u9fa5]+)[:：]\s*(.*)$', line)
        if match:
            # 保存前一个人
            if current_person:
                employees.append({
                    'name': current_person,
                    'work': '\n'.join(current_work).strip()
                })
            # 开始新的人员
            current_person = match.group(1)
            if match.group(2):
                current_work = [match.group(2)]
            else:
                current_work = []
            continue
        
        # 模式 2: 【姓名】
        match = re.match(r'^[【\[]([A-Za-z\u4e00-\u9fa5]+)[】\]]\s*(.*)$', line)
        if match:
            if current_person:
                employees.append({
                    'name': current_person,
                    'work': '\n'.join(current_work).strip()
                })
            current_person = match.group(1)
            current_work = [match.group(2)] if match.group(2) else []
            continue
        
        # 模式 3: 姓名 - 工作内容
        match = re.match(r'^([A-Za-z\u4e00-\u9fa5]+)\s*[-—]\s*(.*)$', line)
        if match and len(match.group(1)) <= 4:  # 姓名一般不超过 4 个字
            if current_person:
                employees.append({
                    'name': current_person,
                    'work': '\n'.join(current_work).strip()
                })
            current_person = match.group(1)
            current_work = [match.group(2)] if match.group(2) else []
            continue
        
        # 其他行作为当前人员的工作内容
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
    lines.append(f"📅 {email_info.get('date', '')[:10]}")
    lines.append(f"👤 共{len(employees)}人")
    lines.append("━" * 20)
    
    # 按人员显示
    for emp in employees:
        name = emp['name']
        work = emp['work']
        
        # 简化工作内容（最多 3 行）
        work_lines = work.split('\n')[:3]
        work_preview = '\n'.join(work_lines)
        if len(work.split('\n')) > 3:
            work_preview += '\n…'
        
        lines.append(f"\n👤 {name}")
        lines.append("─" * 15)
        lines.append(work_preview)
    
    lines.append("\n" + "━" * 20)
    lines.append("✅ 汇报整理完成")
    
    return '\n'.join(lines)


def main():
    args = parse_args()
    
    # 读取邮件
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    emails = data.get('emails', [])
    if not emails:
        print("未找到邮件")
        return 1
    
    # 找到周报邮件
    week_email = None
    week_num = "未知"
    for email in emails:
        subject = email.get('subject', '')
        if '周报' in subject:
            week_email = email
            # 提取期号
            match = re.search(r'第 (\d+) 期', subject)
            if match:
                week_num = match.group(1)
            else:
                match = re.search(r'(\d+) 期', subject)
                if match:
                    week_num = match.group(1)
            break
    
    if not week_email:
        print("未找到周报邮件")
        return 1
    
    # 解析周报内容
    body_text = week_email.get('body_text', '')
    employees = parse_weekly_report(body_text)
    
    if not employees:
        print("未能解析出人员周报，尝试其他格式...")
        # 如果解析失败，返回原始内容
        employees = [{
            'name': '原始内容',
            'work': body_text[:2000]
        }]
    
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
        print(f"汇报已保存到 {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
