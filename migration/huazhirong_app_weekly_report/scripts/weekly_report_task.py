#!/usr/bin/env python3
"""周报技能 - 读取指定邮件并整理周报"""

import os
import sys
import json
import subprocess
from datetime import datetime

def fetch_weekly_report(user, password, from_addr, subject_keyword, output_json):
    """获取周报邮件"""
    cmd = [
        sys.executable,
        os.path.expanduser('~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py'),
        '--user', user,
        '--password', password,
        '--from', from_addr,
        '--limit', '5',
        '--output', output_json
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def extract_attachments(email_json):
    """提取附件信息"""
    with open(email_json) as f:
        data = json.load(f)
    
    for email in data.get('emails', []):
        attachments = email.get('attachments', [])
        if attachments:
            print(f"找到 {len(attachments)} 个附件:")
            for att in attachments:
                print(f"  - {att.get('filename')} ({att.get('size')} bytes)")
            return email, attachments
    
    print("未找到附件")
    return None, []

def main():
    # 配置
    USER = 'qiang.zhou@newpostech.com'
    PASSWORD = os.getenv('EMAIL_IMAP_PASSWORD', 'UIkm6I2cigBGA2Nl')
    FROM_ADDR = 'seven.lin@newpostech.com'
    SUBJECT_KEYWORD = '周报'
    
    TEMP_EMAIL = '/tmp/weekly_report_email.json'
    
    print("📋 正在获取周报邮件...")
    if not fetch_weekly_report(USER, PASSWORD, FROM_ADDR, SUBJECT_KEYWORD, TEMP_EMAIL):
        print("❌ 获取邮件失败")
        return 1
    
    print("✅ 邮件获取成功")
    
    email_data, attachments = extract_attachments(TEMP_EMAIL)
    
    if not attachments:
        print("\n💡 周报邮件没有附件，可能是纯文本格式")
        body = email_data.get('body_text', '')
        if body:
            print("\n=== 邮件正文 ===")
            print(body[:2000])
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
