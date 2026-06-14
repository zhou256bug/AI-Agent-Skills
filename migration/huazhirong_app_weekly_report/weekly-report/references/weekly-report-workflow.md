# 周报技能完整工作流

## 完整执行流程（第 23 期实测）

### 步骤 1：读取周报邮件

```bash
~/.hermes/hermes-agent/venv/bin/python \
  ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --user qiang.zhou@newpostech.com \
  --password UIkm6I2cigBGA2Nl \
  --limit 30 \
  --output /tmp/week23_emails.json
```

**预期输出：**
- 找到周报邮件
- 主题：海外应用开发部―2026 年华智融第 23 期工作周报
- 发件人：seven.lin@newpostech.com
- 附件：.xls 格式 Excel 文件

### 步骤 2：解析 Excel 附件

```bash
python3 << 'EOF'
import imaplib, email, xlrd, ssl, json
from io import BytesIO

# 连接邮箱并下载附件
ssl_context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL('imap.qiye.aliyun.com', 993, ssl_context=ssl_context)
mail.login('qiang.zhou@newpostech.com', 'UIkm6I2cigBGA2Nl')
mail.select('INBOX')

# 获取邮件（使用邮件 ID 或搜索）
status, msg_data = mail.fetch('6219', '(RFC822)')
raw_email = msg_data[0][1]
msg = email.message_from_bytes(raw_email)

# 提取附件
for part in msg.walk():
    if 'attachment' in str(part.get_content_disposition()):
        filename = part.get_filename()
        if '23 期' in filename:
            payload = part.get_payload(decode=True)
            with open('/tmp/week23_report.xls', 'wb') as f:
                f.write(payload)
            print(f"✅ 附件已保存：{filename}")

# 解析 Excel
wb = xlrd.open_workbook('/tmp/week23_report.xls')
employees = []

for sheet_idx in range(1, wb.nsheets):  # 跳过目录
    ws = wb.sheet_by_index(sheet_idx)
    person_name = ws.name
    
    work_items = []
    for row in range(ws.nrows):
        for col in range(ws.ncols):
            cell_value = str(ws.cell_value(row, col)).strip()
            if cell_value and len(cell_value) > 1:
                work_items.append(cell_value)
    
    employees.append({
        'name': person_name,
        'work': '\n'.join(work_items[:20])[:800]
    })

# 保存解析结果
with open('/tmp/week23_parsed.json', 'w', encoding='utf-8') as f:
    json.dump({
        'week_num': '23',
        'department': '海外应用开发部',
        'period': '2026.06.01-06.07',
        'employees': employees
    }, f, ensure_ascii=False, indent=2)

print(f"✅ 解析完成：{len(employees)} 人")
EOF
```

### 步骤 3：生成汇报文档

```bash
python3 ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action parse \
  --week 23 \
  --excel /tmp/week23_report.xls
```

**输出格式：方案 B（用户首选）**
- ⭐ 您的关注（空配置时显示添加指南）
- 📊 本周概览（总人数、周期）
- 🔴 重点成果（Top 5）
- ✅ 移除"项目分布"（数据可能不准确）

### 步骤 4：归档保存

```bash
# 创建归档目录
mkdir -p ~/Documents/weekly-reports

# 保存 Markdown
cp /tmp/week23_report.txt ~/Documents/weekly-reports/week-23.md

# 转换为 PDF/HTML
python3 ~/.hermes/skills/custom/scripts/md_to_pdf.py \
  ~/Documents/weekly-reports/week-23.md \
  ~/Documents/weekly-reports/week-23.pdf

# 检查输出
ls -lh ~/Documents/weekly-reports/week-23.*
```

**预期输出：**
```
-rw-r--r--  1 greg  staff  22K week-23.md   # Markdown 原文档
-rw-r--r--  1 greg  staff  25K week-23.html # HTML 格式（备选）
-rw-r--r--  1 greg  staff  12K week-23.pdf  # PDF 格式（9 页，正式归档）
```

### 步骤 5：发送微信通知

```bash
hermes chat -q "
📋 周报已生成：第 23 期

📄 归档文件：
   ~/Documents/weekly-reports/week-23.pdf
   ~/Documents/weekly-reports/week-23.html

👤 共 15 人
🔴 重点成果 Top 5：林旭伟、丁璞、胡陈琛、李家俊、李响
"
```

---

## 关键配置

### 关注列表配置

`~/.hermes/skills/custom/config/focus_list.json`

```json
{
  "focus_people": [],
  "focus_projects": [],
  "show_others": true,
  "others_format": "compact",
  "department": "海外应用开发部",
  "default_sender": "seven.lin@newpostech.com"
}
```

**空配置时行为：**
- 显示"💡 暂无关注配置"
- 显示添加指南（口述命令）
- 示例："关注周强"、"关注 NEWSTORE 项目"

### 归档目录结构

```
~/Documents/weekly-reports/
├── week-22.md
├── week-22.html
├── week-22.pdf
├── week-23.md
├── week-23.html
└── week-23.pdf
```

---

## 依赖安装

### reportlab（PDF 生成）

```bash
pip3 install reportlab --user
```

**安装验证：**
```bash
python3 -c "from reportlab.lib.pagesizes import letter; print('✅ reportlab 可用')"
```

### xlrd（Excel .xls 解析）

```bash
pip3 install xlrd --user
```

**注意：** openpyxl 仅支持 `.xlsx` 格式，周报使用 `.xls` 格式需要 xlrd。

---

## 常见问题

### 1. 网络超时导致安装失败

**现象：** `pip install` 或 `brew install` 超时

**解决：**
- 使用 `--user` 参数安装到用户目录
- 使用 `uv pip install --system` 尝试不同包管理器
- 降级为 HTML 格式（无需额外依赖）

### 2. Excel 格式解析失败

**现象：** `BadZipFile: File is not a zip file`

**原因：** `.xls` 是二进制格式（OLE），不是 ZIP

**解决：**
- 使用 `xlrd` 库（支持 `.xls`）
- 不要用 `openpyxl`（仅支持 `.xlsx`）

### 3. 微信 iLink 频率限制

**现象：** `iLink sendmessage rate limited`

**解决：**
- 定时任务间隔 ≥ 60 分钟
- 整点报时改为 `0 * * * *`（每小时）
- 避免短时间内多次发送

---

## 实测数据（第 23 期）

- **邮件数：** 1 封周报邮件
- **附件：** 1 个 Excel 文件（212KB）
- **工作表：** 16 个（1 个目录 + 15 个员工）
- **解析人数：** 15 人
- **PDF 页数：** 9 页
- **PDF 大小：** 12KB
- **HTML 大小：** 25KB
- **处理时间：** ~2 分钟（含网络请求）

---

## 用户偏好记录

1. **默认格式：** 方案 B（关键成果版）
2. **关注栏目：** 必须包含，空配置时显示添加指南
3. **移除栏目：** "项目分布"（数据可能不准确）
4. **归档路径：** `~/Documents/weekly-reports/`
5. **PDF 优先：** 有 reportlab 时生成 PDF，否则降级 HTML
6. **口述配置：** 支持"关注 XXX"自然语言命令
