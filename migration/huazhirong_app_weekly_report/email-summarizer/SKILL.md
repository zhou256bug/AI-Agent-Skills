---
name: email-summarizer
description: Use when you need to summarize and organize emails into structured reports. Transforms raw email data into formatted summaries with categorization and key insights.
version: 1.0.0
author: 大老板团队
license: MIT
metadata:
  hermes:
    tags: [email, summarizer, report, business, custom]
    related_skills: [email-reader]
---

# Email Summarizer 技能

## Overview

`email-summarizer` 是一个用于整理和汇总邮件的技能。它接收 `email-reader` 输出的结构化邮件数据，进行分析、分类、提取关键信息，并生成格式化的汇报文档。

**用户偏好：**
- ✅ 默认使用 `mobile` 格式（移动端优化）
- ✅ 紧凑布局（`--compact` 参数）
- ✅ 按优先级分组（紧急→重要→普通）
- ✅ 限制显示数量（最多 20 封，避免过长）
- ✅ 无邮件时静默输出 `[SILENT]`

核心功能：
- 邮件分类汇总（按发件人、主题、优先级）
- 关键信息提取
- 优先级标记（紧急、待办、会议等）
- 生成格式化汇报（Markdown）
- 支持静默模式（无邮件时不输出）

## When to Use

**使用场景：**
- 定时邮件汇报（配合 cron 任务）
- 收件箱整理与归档
- 邮件内容分析与洞察
- 团队邮件汇总

**不使用场景：**
- 只需要原始邮件数据（使用 `email-reader`）
- 需要实时邮件通知（使用其他工具）
- 只需要简单邮件计数

## 工作流程

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  email-reader   │ ──→ │ email-summarizer  │ ──→ │   汇报输出      │
│  读取邮件       │     │  整理分析        │     │  (Markdown)     │
│  输出 JSON      │     │  生成汇报        │     │  微信/文件      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 使用方法

### 基本用法

```bash
# 从 stdin 读取邮件数据，输出汇报
cat emails.json | python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py
```

### 移动端优化格式（推荐用于微信推送）

```bash
cat emails.json | python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --format mobile \
  --compact \
  --max-emails 20
```

### 配合 email-reader 使用

```bash
# 方式 1：管道传递
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "1 hour ago" | \
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py

# 方式 2：文件传递
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "1 hour ago" --output /tmp/emails.json

python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --input /tmp/emails.json --output /tmp/report.md
```

### 配合 Cron 任务

```bash
# 创建定时汇报任务（每 30 分钟）
hermes cron create "every 30m" \
  "使用 email-reader 读取过去 30 分钟的未读邮件，使用 email-summarizer 生成汇报，推送到微信" \
  --name "邮件定时汇报" \
  --deliver "weixin:o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat"
```

## 脚本参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入文件路径（JSON） | stdin |
| `--output` | 输出文件路径 | stdout |
| `--format` | 输出格式（markdown/text/json） | `markdown` |
| `--group-by` | 分组方式（sender/subject/priority/none） | `sender` |
| `--highlight-keywords` | 高亮关键词（逗号分隔） | `紧急，待办，会议，回复，批准` |
| `--max-body-length` | 正文最大长度（字符） | 500 |
| `--silent-if-empty` | 无邮件时静默输出 `[SILENT]` | `false` |
| `--include-attachments` | 包含附件信息 | `false` |
| `--timezone` | 时区 | `Asia/Shanghai` |

## 输出格式示例

### Markdown 格式（默认）

```markdown
# 📧 邮件汇报

**生成时间：** 2026-06-12 14:30:00  
**统计期间：** 过去 1 小时  
**邮件总数：** 5 封

---

## 📊 概览

| 分类 | 数量 |
|------|------|
| 未读邮件 | 5 |
| 紧急邮件 | 1 |
| 含附件 | 2 |

---

## 📬 邮件详情

### 张三 <zhangsan@company.com> (2 封)

#### [紧急] 项目进度汇报 - 2026-06-12 14:15
**摘要：** 本周项目进度正常，已完成模块 A 的开发...
**附件：** 项目进度.xlsx
**标签：** #紧急 #项目

#### 会议纪要 - 产品评审会 - 2026-06-12 13:30
**摘要：** 今天下午 3 点在会议室 A 召开产品评审会...
**标签：** #会议

---

### 李四 <lisi@partner.com> (1 封)

#### 合作方案确认
**摘要：** 关于上次讨论的合作方案，我们内部已经...
**标签：** #合作

---

### 系统通知 <noreply@service.com> (2 封)

#### 服务器监控告警
**摘要：** 检测到服务器 CPU 使用率超过 90%...
**标签：** #告警 #紧急

#### 每日备份完成
**摘要：** 今日备份任务已成功完成...
**标签：** #系统
```

### 静默模式（无邮件时）

```
[SILENT]
```

---

## 优先级规则

脚本自动识别以下关键词标记优先级：

| 优先级 | 关键词 |
|--------|--------|
| 🔴 紧急 | `紧急`, `urgent`, ` ASAP`, `立刻`, `马上` |
| 🟡 重要 | `重要`, `important`, `优先`, `priority` |
| 🟢 普通 | 其他邮件 |

### 主题标签自动识别

| 标签 | 关键词 |
|------|--------|
| #会议 | `会议`, `meeting`, `参会`, `会议室` |
| #待办 | `待办`, `todo`, `请处理`, `需要` |
| #回复 | `回复`, `reply`, `请确认`, `请反馈` |
| #批准 | `批准`, `审批`, `approve`, `审核` |
| #项目 | `项目`, `project`, `进度`, `开发` |
| #告警 | `告警`, `alert`, `警告`, `warning` |
| #系统 | `系统`, `system`, `备份`, `通知` |

---

## 模板自定义

可以创建自定义汇报模板，见 `templates/` 目录。

### 参考文档

- **移动端格式规范**：`references/mobile-format-guide.md` - 微信等移动端推送的格式优化指南
- **周报解析**：`references/weekly-report-parsing.md` - 部门周报邮件的提取和整理指南
- **Python 陷阱**：`references/python-pitfalls.md` - 变量作用域冲突等常见 Python 问题

### 使用自定义模板

```bash
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --input emails.json \
  --template ~/.hermes/skills/custom/email-summarizer/templates/simple.md
```

### 模板变量

模板中可用的变量：

| 变量 | 说明 |
|------|------|
| `{{generated_at}}` | 汇报生成时间 |
| `{{period}}` | 统计期间描述 |
| `{{total_count}}` | 邮件总数 |
| `{{summary_table}}` | 概览表格 |
| `{{email_groups}}` | 分组邮件详情 |
| `{{urgent_count}}` | 紧急邮件数 |
| `{{attachment_count}}` | 含附件邮件数 |

---

## Common Pitfalls

1. **JSON 格式错误**
   - 问题：输入 JSON 解析失败
   - 解决：确认 `email-reader` 输出正确，使用 `--pretty` 参数调试

2. **中文乱码**
   - 问题：输出中文显示乱码
   - 解决：确保终端/文件使用 UTF-8 编码

3. **无邮件时仍输出**
   - 问题：无邮件时仍生成空汇报
   - 解决：使用 `--silent-if-empty` 参数

4. **分组过多**
   - 问题：邮件分散到太多组
   - 解决：使用 `--group-by none` 禁用分组，或增加 `--limit`

5. **关键词匹配过度**
   - 问题：普通邮件被标记为紧急
   - 解决：自定义 `--highlight-keywords` 列表

6. **移动端输出过长**
   - 问题：微信消息超过显示限制
   - 解决：使用 `--format mobile --compact --max-emails 20`
   - 参考：`references/mobile-format-guide.md`

7. **⚠️ Python 变量作用域冲突（重要！）**
   - 问题：`UnboundLocalError: cannot access local variable 'group_emails'`
   - 根本原因：循环变量名与函数名冲突，例如 `for group_name, group_emails in groups.items()` 会覆盖 `group_emails()` 函数
   - 解决：循环变量使用不同名称，如 `group_list`、`mail_group`、`email_batch`
   - 预防：在函数内部使用局部变量时，避免与已定义函数同名
   - 示例：
     ```python
     # ❌ 错误：变量名覆盖函数
     for group_name, group_emails in groups.items():
         for email in group_emails:  # 这里 group_emails 是列表，不是函数
     
     # ✅ 正确：使用不同变量名
     for group_name, group_list in groups.items():
         for email in group_list:  # 清晰，不冲突
     ```
   - 参考：`references/python-pitfalls.md`

8. **⚠️ 微信推送频率限制**
   - 问题：`Weixin send failed: iLink sendmessage rate limited; cooldown active for 30.0s`
   - 原因：iLink API 对同一用户有发送频率限制（约 30 秒冷却时间）
   - 触发场景：
     - 定时任务间隔过短（如每 20 分钟）
     - 短时间内多次发送（失败重试累积）
     - iLink 策略调整
   - 解决方案：
     1. **增加间隔时间**：从 20 分钟改为 60 分钟
        ```bash
        hermes cron create "0 * * * *" "整点报时" --deliver "weixin:..."
        ```
     2. **固定时间点**：每天固定时间推送（如 9:00、12:00、18:00）
        ```bash
        hermes cron create "0 9,12,18 * * *" "定时汇报" --deliver "weixin:..."
        ```
     3. **接受部分限流**：任务继续执行，日志记录失败（适合非关键推送）
   - 监控：`hermes cron list` 查看 `Delivery failed` 警告
   - 参考：`references/mobile-format-guide.md` - 微信推送优化章节

---

## 周报解析（Excel 附件）

**重要：** 如果周报邮件包含 Excel 附件（.xls 或.xlsx 格式），请使用专用技能：

```bash
# 使用 weekly-report-parsing 技能
python ~/.hermes/skills/weekly-report-parsing/scripts/parse_weekly_report.py \
  --email-json /tmp/week_emails.json \
  --format mobile
```

**功能：**
- 解析 Excel 多工作表结构（每人一个工作表）
- 提取人员工作内容
- 支持"您的关注"配置（人员/项目）
- 生成移动端优化汇报（方案 B）

**配置关注列表：**
```bash
# 添加关注
python ~/.hermes/skills/weekly-report-parsing/scripts/parse_weekly_report.py \
  --action add_focus --type person --name "周强"

# 查看关注
python ~/.hermes/skills/weekly-report-parsing/scripts/parse_weekly_report.py \
  --action list_focus
```

**参考：** `weekly-report-parsing` 技能完整文档

---

## 模板自定义

- [ ] 能正确读取 `email-reader` 的 JSON 输出
- [ ] 能正确分类和标记优先级
- [ ] Markdown 格式输出正确
- [ ] 静默模式正常工作
- [ ] 自定义模板能加载
- [ ] 中文编码正确

---

## One-Shot Recipes

### 场景 1：快速查看最近邮件汇报

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "2 hours ago" --limit 10 | \
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py
```

### 场景 2：生成文件并推送

```bash
# 读取并整理
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "1 hour ago" --output /tmp/emails.json

python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --input /tmp/emails.json --output /tmp/report.md

# 查看汇报
cat /tmp/report.md
```

### 场景 3：静默模式（适合 cron）

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "30m ago" | \
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --silent-if-empty
```

### 场景 4：自定义关键词

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "1 hour ago" | \
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --highlight-keywords "老板，审批，合同，付款" \
  --group-by subject
```

---

## 与其他技能配合

- **email-reader**: 提供邮件数据输入
- **cronjob**: 定时执行汇报任务
- **messaging**: 推送汇报到微信/Telegram 等平台

**集成文档：** 见 `email-reader` 技能的 `references/cron-integration.md` - Cron 定时汇报集成指南。

## 扩展建议

### 可能的未来功能

1. **AI 摘要**：使用 LLM 生成更智能的邮件摘要
2. **情感分析**：识别邮件情绪（积极/消极/中性）
3. **自动分类**：基于历史邮件自动学习分类规则
4. **多邮箱聚合**：同时处理多个邮箱的邮件
5. **图表生成**：生成邮件统计图表

### 贡献代码

欢迎提交 PR 增加新功能！

---

## 安全建议

1. **汇报文件权限**：生成的汇报可能包含敏感信息，注意文件权限
2. **推送渠道安全**：确保微信等推送渠道的访问控制
3. **定期清理**：定期清理临时文件和历史汇报
