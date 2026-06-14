# 移动端邮件汇报格式规范

## 设计原则

1. **单屏优先**：关键信息在第一屏显示，减少滚动
2. **紧凑布局**：减少空行，使用短分隔线
3. **视觉层次**：使用 emoji 图标快速识别优先级
4. **智能截断**：长主题/摘要自动截断，保持可读性

## 格式示例

```
📧 邮件汇报 · 06-12 17:04

📊 共 5 封 | 🟡1 | 📎2
━━━━━━━━━━━━━━━━━━━━

🟡 重要 (1)
───────────────
• [06-10] Re: 回复：NEWSTORE 客户端体系提测
  #待办 #回复 #系统

📩 普通 (4)
───────────────
• [06-10] 关于对王艺超先生的任命决定 @华智融
  #会议 #人事

• [16:40] [系统提醒邮件] 华智融文件管理系统 文件发行通知！ @oa
  #回复 #系统 #人事

━━━━━━━━━━━━━━━━━━━━
✅ 已全部显示
```

## 格式规范

### 1. 标题行

格式：`📧 邮件汇报 · MM-DD HH:MM`

- 日期时间格式：`月 - 日 时：分`
- 紧凑显示，无多余空格

### 2. 概览行

格式：`📊 共 X 封 | 🔴X | 🟡X | 📎X`

- 总数必显
- 紧急邮件（🔴）>0 时显示
- 重要邮件（🟡）>0 时显示
- 含附件（📎）>0 时显示
- 超过显示上限时用 `…还有 X 封`

### 3. 分组标题

格式：
```
🔴 紧急 (X)
───────────────
```

- 优先级图标：🔴紧急 > 🟡重要 > 📩普通
- 分隔线：15 个 `─` 字符
- 显示该组邮件数量

### 4. 邮件行

格式：`• [时间] 主题 @发件人`

- 时间：今天显示 `HH:MM`，其他显示 `MM-DD`
- 主题：最多 40 字符，超长截断加 `…`
- 发件人：≤6 字符时显示，简化显示（如 `@oa`、`@华智融`）

### 5. 标签行

格式：`  #标签 1 #标签 2 #标签 3`

- 缩进 2 空格
- 最多显示 3 个标签
- `#` 前缀，无空格

### 6. 附件提示

格式：`  📎 X 个附件`

- 缩进 2 空格
- 仅在 `--include-attachments` 时显示

### 7. 底部分隔

格式：
```
━━━━━━━━━━━━━━━━━━━━
✅ 已全部显示
```

或（有截断时）：
```
━━━━━━━━━━━━━━━━━━━━
💡 还有 X 封邮件未显示，请登录邮箱查看完整列表
```

## 推荐参数

```bash
python summarize.py \
  --format mobile \
  --compact \
  --max-emails 20 \
  --max-subject-length 40 \
  --max-summary-length 100 \
  --group-by priority \
  --silent-if-empty
```

## 微信推送优化

### 字符限制

- 微信消息无严格字符限制，但建议控制在 2000 字符内
- 超过 2000 字符可能被折叠或分多条发送

### 显示优化

- 使用通用 emoji（微信支持良好）
- 避免特殊 Unicode 字符（可能显示为方框）
- 分隔线使用中文破折号 `━` 和 `─`（兼容性好）

### 推送时机

- 推荐工作时间推送（如 8:00、18:00）
- 避免深夜推送打扰
- 无邮件时静默（`--silent-if-empty`）

## 发件人简化规则

| 原始发件人 | 简化显示 |
|-----------|---------|
| `华智融 <newpostech@newpostech.com>` | `华智融` |
| `oa@newpostech.com` | `oa` |
| `"seven.lin@newpostech.com" <seven.lin@newpostech.com>` | `seven.lin` |
| `周强 <qiang.zhou@newpostech.com>` | `周强` |
| `newpostech@newpostech.com` | `newpostech` |

## 优先级关键词

### 🔴 紧急
- 中文：`紧急`、`立刻`、`马上`、`急`
- 英文：`urgent`、`ASAP`、`immediately`

### 🟡 重要
- 中文：`重要`、`优先`、`请处理`
- 英文：`important`、`priority`、`critical`

## 标签关键词

| 标签 | 关键词 |
|------|--------|
| #会议 | 会议、meeting、参会、会议室 |
| #待办 | 待办、todo、请处理、需要 |
| #回复 | 回复、reply、请确认、请反馈 |
| #批准 | 批准、审批、approve、审核 |
| #项目 | 项目、project、进度、开发 |
| #告警 | 告警、alert、警告、warning |
| #系统 | 系统、system、备份、通知 |
| #人事 | 人事、任命、招聘、hr、入职 |
| #财务 | 财务、付款、发票、报销 |

## 自定义配置

通过环境变量自定义：

```bash
# 自定义高亮关键词
export EMAIL_SUMMARIZER_KEYWORDS="老板，审批，合同，付款"

# 自定义最大邮件数
export EMAIL_REPORT_LIMIT=50

# 自定义时间范围
export EMAIL_REPORT_SINCE="24 hours ago"
```

## 测试命令

```bash
# 测试移动端格式
cat emails.json | python summarize.py --format mobile --compact

# 测试静默模式
cat empty_emails.json | python summarize.py --silent-if-empty
# 应输出：[SILENT]

# 测试自定义关键词
cat emails.json | python summarize.py \
  --highlight-keywords "老板，审批，合同" \
  --format mobile
```
