# 周报解析指南

## 概述

本指南说明如何解析部门周报邮件，特别是 Excel 附件格式的周报。

## 周报结构模式

### 模式 1：多工作表（每人一个工作表）

**特征：**
- Excel 包含多个工作表
- 第一个工作表通常是"目录"或"汇总"
- 后续每个工作表以员工姓名命名
- 每个工作表包含该员工的周报内容

**示例：**
```
工作表列表:
1. 目录
2. 林旭伟
3. 代鑫
4. 丁璞
...
```

**解析策略：**
1. 跳过目录工作表
2. 遍历所有以人名命名的工作表
3. 提取每个工作表的全部内容
4. 合并为该员工的周报

**解析脚本：** `scripts/parse_week23_all_sheets.py`

### 模式 2：单工作表（多行多列）

**特征：**
- Excel 只有一个工作表
- 第一行是表头
- 每行是一个员工
- 列包含：姓名、工作内容、计划等

**示例表头：**
```
姓名 | 本周工作 | 下周计划 | 备注
```

**解析策略：**
1. 识别姓名列和工作列
2. 遍历所有行
3. 提取姓名和对应工作内容

**解析脚本：** `scripts/parse_week23_xlrd.py`

### 模式 3：纯文本邮件

**特征：**
- 无附件
- 周报内容直接在邮件正文中
- 通常格式为"姓名：工作内容"

**解析策略：**
1. 使用正则表达式识别"姓名："模式
2. 提取每个人员的周报内容

**解析脚本：** `scripts/weekly_report_parser.py`

## Excel 格式处理

### .xls vs .xlsx

| 格式 | 解析库 | 说明 |
|------|--------|------|
| `.xls` | `xlrd` | 旧版 Excel 二进制格式 |
| `.xlsx` | `openpyxl` | 新版 Excel XML 格式 |

**依赖安装：**
```bash
pip install xlrd openpyxl
```

### 解析注意事项

1. **编码问题** - Excel 可能包含中文字符，确保正确解码
2. **合并单元格** - 合并单元格只在一个单元格有值
3. **空值处理** - 使用 `pd.notna()` 或检查 `None`
4. **数字格式** - 日期/数字可能以特殊格式存储

## 周报整理输出格式

### 移动端优化格式

```
📋 工作周报 · 第 23 期
📧 发件人：林珊雯 (seven.lin@newpostech.com)
🏢 部门：海外应用开发部
📅 周期：2026.06.01-2026.06.07
👤 共 15 人
━━━━━━━━━━━━━━━━━━━━

👤 林旭伟
───────────────
23.0 项目名称：华智融亚太分公司
本周完成内容：
1. Airwallex 项目：与销售沟通了项目进度...
2. 推进跨机型 UI 适配...

👤 代鑫
───────────────
项目：日本 BMT-CCT
本周工作记录:
1. 梳理二期的交易流程...

...

━━━━━━━━━━━━━━━━━━━━
✅ 周报整理完成
```

### 输出文件

- `/tmp/week23_parsed.json` - 结构化数据
- `/tmp/week23_report.txt` - 文本汇报

## 常用命令

### 立即解析周报

```bash
python3 ~/.hermes/skills/custom/scripts/parse_week23_all_sheets.py
```

### 创建定时任务（每周一 8 点）

```bash
hermes cron create "0 8 * * 1" \
  "读取林珊雯发送的周报并整理" \
  --name "部门周报整理" \
  --deliver "weixin:o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat" \
  --script "custom/scripts/parse_week23_all_sheets.py" \
  --no-agent
```

## 故障排查

### 问题 1：找不到周报邮件

**检查：**
```bash
# 搜索包含"周报"的邮件
python3 -c "
import json
with open('/tmp/recent_emails.json') as f:
    data = json.load(f)
for email in data['emails']:
    if '周报' in email.get('subject', ''):
        print(email.get('subject'))
"
```

### 问题 2：Excel 解析失败

**可能原因：**
- 格式不支持（.xls 用了 openpyxl）
- 文件损坏
- 加密的 Excel 文件

**解决：**
```bash
# 确认文件格式
file weekly_report.xls

# 使用正确的库
# .xls → xlrd
# .xlsx → openpyxl
```

### 问题 3：无法识别人员列

**可能原因：**
- 表头名称不标准
- 多语言混合

**解决：**
- 扩展关键词列表
- 手动指定列索引

## 相关脚本

- `scripts/parse_week23_all_sheets.py` - 多工作表解析
- `scripts/parse_week23_xlrd.py` - xlrd 解析（.xls）
- `scripts/parse_week23_excel.py` - openpyxl 解析（.xlsx）
- `scripts/weekly_report_parser.py` - 纯文本解析
- `scripts/weekly_report_skill.py` - 通用周报技能

## 相关文件

- `email-summarizer/SKILL.md` - 邮件整理技能
- `email-reader/SKILL.md` - 邮件读取技能
- `references/mobile-format-guide.md` - 移动端格式指南
