#!/usr/bin/env python3
"""下载并解析第 23 期周报 Excel 附件 - 遍历所有工作表"""

import imaplib
import email
from email import policy
import ssl
import json
import xlrd
from io import BytesIO
from datetime import datetime

# 配置
IMAP_HOST = 'imap.qiye.aliyun.com'
IMAP_PORT = 993
IMAP_USER = 'qiang.zhou@newpostech.com'
IMAP_PASS = 'UIkm6I2cigBGA2Nl'
WEEK23_EMAIL_ID = '6219'

print("📋 开始解析第 23 期周报...\n")

ssl_context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=ssl_context)

try:
    mail.login(IMAP_USER, IMAP_PASS)
    mail.select('INBOX')
    
    status, msg_data = mail.fetch(WEEK23_EMAIL_ID, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email, policy=policy.default)
    
    print(f"✅ 邮件：{msg.get('Subject', '')}")
    
    # 查找 Excel 附件
    for part in msg.walk():
        content_disposition = str(part.get_content_disposition())
        
        if 'attachment' in content_disposition:
            filename = part.get_filename()
            if filename and ('23 期' in filename or '.xls' in filename.lower()):
                print(f"✅ 找到：{filename}")
                
                payload = part.get_payload(decode=True)
                if payload:
                    print(f"📊 大小：{len(payload)} bytes")
                    
                    # 使用 xlrd 读取.xls 格式
                    excel_file = BytesIO(payload)
                    wb = xlrd.open_workbook(file_contents=excel_file.read())
                    
                    print(f"\n📄 Excel 包含 {wb.nsheets} 个工作表")
                    
                    # 遍历所有工作表（跳过目录）
                    employees = []
                    
                    for sheet_idx in range(1, wb.nsheets):  # 从第 2 个工作表开始（跳过目录）
                        ws = wb.sheet_by_index(sheet_idx)
                        person_name = ws.name
                        
                        # 提取该员工的工作内容
                        work_items = []
                        
                        for row in range(ws.nrows):
                            for col in range(ws.ncols):
                                cell_value = str(ws.cell_value(row, col)).strip()
                                if cell_value and len(cell_value) > 1:
                                    work_items.append(cell_value)
                        
                        # 合并工作内容
                        work_text = '\n'.join(work_items[:20])  # 最多 20 条
                        
                        if person_name and person_name not in ['目录', 'Sheet1']:
                            employees.append({
                                'name': person_name,
                                'work': work_text[:800]  # 限制长度
                            })
                    
                    print(f"👤 共提取 {len(employees)} 人的周报")
                    
                    # 保存结果
                    result = {
                        'week_num': '23',
                        'email_subject': msg.get('Subject', ''),
                        'date': msg.get('Date', ''),
                        'period': '2026.06.01-2026.06.07',
                        'department': '海外应用开发部',
                        'employee_count': len(employees),
                        'employees': employees
                    }
                    
                    with open('/tmp/week23_parsed.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    print("✅ 解析结果已保存到 /tmp/week23_parsed.json")
                    
                    # 生成移动端汇报
                    print("\n" + "=" * 40)
                    print("📋 工作周报 · 第 23 期")
                    print("📧 发件人：林珊雯 (seven.lin@newpostech.com)")
                    print("🏢 部门：海外应用开发部")
                    print("📅 周期：2026.06.01-2026.06.07")
                    print(f"👤 共{len(employees)}人")
                    print("━" * 40)
                    
                    for emp in employees:
                        print(f"\n👤 {emp['name']}")
                        print("─" * 15)
                        work_preview = emp['work'][:150]
                        if len(emp['work']) > 150:
                            work_preview += '…'
                        print(work_preview)
                    
                    print("\n" + "━" * 40)
                    print("✅ 周报整理完成")
                    
                    # 保存完整汇报到文件
                    with open('/tmp/week23_report.txt', 'w', encoding='utf-8') as f:
                        f.write("📋 工作周报 · 第 23 期\n")
                        f.write("🏢 海外应用开发部\n")
                        f.write("📅 2026.06.01-2026.06.07\n")
                        f.write("━" * 40 + "\n\n")
                        
                        for emp in employees:
                            f.write(f"👤 {emp['name']}\n")
                            f.write("─" * 15 + "\n")
                            f.write(emp['work'] + "\n\n")
                    
                    print("📄 完整汇报已保存到 /tmp/week23_report.txt")
                break
    
    mail.logout()
    
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    try:
        mail.logout()
    except:
        pass
