#!/usr/bin/env python3
"""下载并解析第 23 期周报 Excel 附件"""

import imaplib
import email
from email import policy
import ssl
import json
import pandas as pd
from io import BytesIO

# 配置
IMAP_HOST = 'imap.qiye.aliyun.com'
IMAP_PORT = 993
IMAP_USER = 'qiang.zhou@newpostech.com'
IMAP_PASS = 'UIkm6I2cigBGA2Nl'
WEEK23_EMAIL_ID = '6219'  # 第 23 期周报邮件 ID

print("📋 开始解析第 23 期周报...\n")

# 连接邮箱
ssl_context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=ssl_context)

try:
    mail.login(IMAP_USER, IMAP_PASS)
    mail.select('INBOX')
    
    # 获取邮件
    status, msg_data = mail.fetch(WEEK23_EMAIL_ID, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email, policy=policy.default)
    
    print(f"✅ 邮件：{msg.get('Subject', '')}")
    print(f"   日期：{msg.get('Date', '')}")
    
    # 查找并解析 Excel 附件
    print("\n🔍 查找 Excel 附件...")
    
    for part in msg.walk():
        content_disposition = str(part.get_content_disposition())
        
        if 'attachment' in content_disposition:
            filename = part.get_filename()
            if filename and ('23 期' in filename or '.xls' in filename.lower()):
                print(f"✅ 找到：{filename}")
                
                payload = part.get_payload(decode=True)
                if payload:
                    print(f"📊 大小：{len(payload)} bytes")
                    
                    try:
                        # 使用 pandas 读取 Excel
                        excel_file = BytesIO(payload)
                        
                        # 尝试读取所有 sheet
                        xl = pd.ExcelFile(excel_file)
                        sheet_names = xl.sheet_names
                        
                        print(f"\n📄 Excel 包含 {len(sheet_names)} 个工作表:")
                        for i, sheet in enumerate(sheet_names[:5], 1):
                            print(f"   {i}. {sheet}")
                        
                        # 读取第一个工作表
                        df = pd.read_excel(excel_file, sheet_name=0)
                        
                        print(f"\n📊 数据维度：{df.shape[0]} 行 × {df.shape[1]} 列")
                        print(f"\n列名：{', '.join(df.columns[:10])}")
                        
                        # 显示前几行
                        print("\n=== 数据预览 ===")
                        print(df.head(10).to_string())
                        
                        # 尝试识别人名和工作内容列
                        print("\n=== 尝试识别人员周报 ===")
                        
                        # 常见的人名列
                        name_cols = ['姓名', '人员', '员工', 'Name', 'name']
                        work_cols = ['工作内容', '工作', '本周工作', '总结', '计划']
                        
                        name_col = None
                        work_col = None
                        
                        for col in df.columns:
                            col_str = str(col)
                            if any(n in col_str for n in name_cols):
                                name_col = col
                            if any(w in col_str for w in work_cols):
                                work_col = col
                        
                        if name_col and work_col:
                            print(f"✅ 识别到人员列：{name_col}")
                            print(f"✅ 识别到工作列：{work_col}")
                            
                            # 提取人员周报
                            employees = []
                            for idx, row in df.iterrows():
                                name = str(row[name_col]) if pd.notna(row[name_col]) else ''
                                work = str(row[work_col]) if pd.notna(row[work_col]) else ''
                                
                                if name and len(name) > 1 and name not in ['nan', 'None']:
                                    employees.append({
                                        'name': name,
                                        'work': work[:500]  # 限制长度
                                    })
                            
                            print(f"\n👤 共提取 {len(employees)} 人的周报")
                            
                            # 保存结果
                            result = {
                                'week_num': '23',
                                'email_subject': msg.get('Subject', ''),
                                'date': msg.get('Date', ''),
                                'employee_count': len(employees),
                                'employees': employees
                            }
                            
                            with open('/tmp/week23_parsed.json', 'w', encoding='utf-8') as f:
                                json.dump(result, f, ensure_ascii=False, indent=2)
                            
                            print("✅ 解析结果已保存到 /tmp/week23_parsed.json")
                            
                            # 生成移动端汇报
                            print("\n" + "=" * 40)
                            print("📋 工作周报 · 第 23 期")
                            print("📧 发件人：林珊雯")
                            print(f"👤 共{len(employees)}人")
                            print("━" * 40)
                            
                            for emp in employees[:10]:  # 显示前 10 人
                                print(f"\n👤 {emp['name']}")
                                print("─" * 15)
                                work_preview = emp['work'][:100]
                                if len(emp['work']) > 100:
                                    work_preview += '…'
                                print(work_preview)
                            
                            if len(employees) > 10:
                                print(f"\n… 还有 {len(employees) - 10} 人")
                            
                            print("\n" + "━" * 40)
                            print("✅ 周报整理完成")
                            
                        else:
                            print("⚠️  未能自动识别人员列和工作列")
                            print(f"   可用列：{', '.join(map(str, df.columns))}")
                        
                    except Exception as e:
                        print(f"❌ 解析 Excel 失败：{e}")
                        import traceback
                        traceback.print_exc()
                break
    
    mail.logout()
    
except Exception as e:
    print(f"❌ 错误：{e}")
    try:
        mail.logout()
    except:
        pass
