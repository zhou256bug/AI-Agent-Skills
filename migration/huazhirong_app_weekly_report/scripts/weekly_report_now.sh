#!/usr/bin/env bash
# 周报汇报 - 立即执行

set -e

echo "📋 正在获取林珊雯的周报..."

# 读取最近邮件
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --user qiang.zhou@newpostech.com \
  --password UIkm6I2cigBGA2Nl \
  --limit 30 \
  --output /tmp/weekly_emails.json

# 过滤并解析周报
~/.hermes/hermes-agent/venv/bin/python << 'PYTHON_SCRIPT'
import json
import re
from datetime import datetime

with open('/tmp/weekly_emails.json') as f:
    data = json.load(f)

emails = data.get('emails', [])

# 找到林珊雯的周报
week_email = None
week_num = "未知"

for email in emails:
    subject = email.get('subject', '')
    sender = email.get('from', '')
    
    if 'seven.lin' in sender.lower() and '周报' in subject:
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
    print("❌ 未找到林珊雯的周报邮件")
    exit(1)

print(f"✅ 找到周报：第{week_num}期")
print(f"   主题：{week_email.get('subject', '')}")
print(f"   日期：{week_email.get('date', '')}")

# 解析正文中的人员名单
body = week_email.get('body_text', '')
attachments = week_email.get('attachments', [])

print(f"\n📎 附件：{len(attachments)} 个")
for att in attachments[:3]:
    print(f"   - {att.get('filename')}")

# 简单的人员提取（从文件名或正文）
employees = []

# 尝试从正文提取
if body:
    lines = body.split('\n')
    for line in lines:
        # 查找类似 "张三：工作内容" 的模式
        match = re.match(r'^([A-Za-z\u4e00-\u9fa5\.]+)\s*[:：]\s*', line.strip())
        if match and len(match.group(1)) <= 6 and match.group(1) not in ['各位好', '附件', '谢谢']:
            employees.append(match.group(1))

# 如果有附件，从附件名提取人员信息
if attachments:
    for att in attachments:
        filename = att.get('filename', '')
        # 尝试从文件名提取期号等信息
        if '周报' in filename or 'week' in filename.lower():
            print(f"\n📄 周报附件：{filename}")

print(f"\n👤 从正文识别到 {len(employees)} 人")
if employees:
    print("   人员：" + ", ".join(employees[:10]))

# 生成简单汇报
print("\n" + "=" * 40)
print(f"📋 工作周报 · 第{week_num}期")
print(f"📧 发件人：林珊雯 (seven.lin@newpostech.com)")
if week_email.get('date'):
    try:
        date = datetime.fromisoformat(week_email['date']).strftime('%Y-%m-%d')
        print(f"📅 日期：{date}")
    except:
        pass
print(f"📎 附件：{len(attachments)} 个")
print("━" * 40)

if attachments:
    print("\n📄 附件列表:")
    for i, att in enumerate(attachments[:5], 1):
        filename = att.get('filename', '未知文件')
        size = att.get('size', 0)
        size_kb = round(size / 1024, 1)
        print(f"  {i}. {filename} ({size_kb} KB)")

if employees:
    print(f"\n👤 识别到人员：{', '.join(employees[:10])}")

print("\n" + "━" * 40)
print("💡 周报内容在附件中，需要下载解析")
print("   请手动打开附件查看完整周报内容")
PYTHON_SCRIPT
