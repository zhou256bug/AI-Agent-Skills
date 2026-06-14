---
name: email-reader
description: Use when you need to read emails from IMAP servers (Gmail, 163, QQ, enterprise mailboxes). Fetches, parses, and returns structured email data.
version: 1.0.0
author: 大老板团队
license: MIT
metadata:
  hermes:
    tags: [email, imap, reader, business, custom]
    related_skills: [email-summarizer, himalaya]
---

# Email Reader 技能

## Overview

`email-reader` 是一个用于从 IMAP 邮件服务器**只读**读取邮件的技能。支持所有标准 IMAP 协议邮箱，包括 Gmail、163、QQ、阿里企业邮箱等。

**重要：本技能仅为只读权限，不支持任何写入操作！**

核心功能：
- IMAP 连接与认证
- 收件箱查询（支持多种过滤条件）
- 邮件内容解析（主题、发件人、正文、附件）
- 输出结构化 JSON 数据

**安全限制（明确禁止的操作）：**
- ❌ **禁止删除邮件**
- ❌ **禁止移动邮件**
- ❌ **禁止标记已读/未读**
- ❌ **禁止发送邮件**
- ❌ **禁止回复邮件**
- ❌ **禁止修改邮件内容**
- ❌ **禁止管理文件夹**

所有操作仅限于读取和解析，确保邮箱数据安全。

## When to Use

**使用场景：**
- 需要读取收件箱邮件进行自动化处理
- 定时邮件汇报任务
- 邮件内容分析与整理
- 邮件归档或备份

**不使用场景：**
- 需要发送邮件（使用其他工具）
- 需要管理邮件文件夹（移动、删除等）
- 只需要简单邮件通知

**安全限制（明确禁止的操作）：**
- ❌ **禁止删除邮件**
- ❌ **禁止移动邮件**
- ❌ **禁止标记已读/未读**
- ❌ **禁止发送邮件**
- ❌ **禁止回复邮件**
- ❌ **禁止修改邮件内容**
- ❌ **禁止管理文件夹**

所有操作仅限于读取和解析，确保邮箱数据安全。

## 阿里企业邮箱配置

### IMAP 服务器信息

| 配置项 | 值 |
|--------|-----|
| IMAP 服务器 | `imap.qiye.aliyun.com` |
| 端口 | `993` (SSL) |
| 用户名 | 完整邮箱地址（如 `user@yourcompany.com`） |
| 密码 | 邮箱密码或**授权码/客户端专用密码** |

### 启用 IMAP/SMTP 服务

1. 登录阿里企业邮箱网页版：https://qiye.aliyun.com
2. 进入 **设置** → **客户端设置**
3. 开启 **IMAP/SMTP 服务**
4. 如需客户端专用密码，在此生成

### 环境变量配置

在 `~/.hermes/.env` 中添加：

```bash
# 阿里企业邮箱 IMAP 配置
EMAIL_IMAP_HOST=imap.qiye.aliyun.com
EMAIL_IMAP_PORT=993
EMAIL_IMAP_USER=your_email@yourcompany.com
EMAIL_IMAP_PASSWORD=your_password_or_app_token
EMAIL_IMAP_USE_SSL=true
```

## 使用方法

### 基本用法

```bash
# 通过 cron 任务调用
hermes cron create "every 1h" "使用 email-reader 技能读取过去 1 小时的未读邮件" --name "邮件检查"

# 或在对话中加载技能
/skill email-reader
```

### Python 脚本调用

技能包含 `scripts/fetch_emails.py` 脚本，可直接调用：

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --host imap.qiye.aliyun.com \
  --port 993 \
  --user your_email@company.com \
  --password your_password \
  --folder INBOX \
  --unread \
  --since "1 hour ago"
```

### 输出格式

脚本输出 JSON 格式的邮件列表：

```json
{
  "success": true,
  "count": 3,
  "emails": [
    {
      "id": "12345",
      "from": "sender@example.com",
      "from_name": "张三",
      "to": "you@company.com",
      "subject": "会议通知",
      "date": "2026-06-12T10:30:00+08:00",
      "body_text": "邮件正文内容...",
      "body_html": "<html>...</html>",
      "attachments": [],
      "flags": ["\\Seen"],
      "folder": "INBOX"
    }
  ]
}
```

## 脚本参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | IMAP 服务器地址 | 从环境变量读取 |
| `--port` | IMAP 端口 | 993 |
| `--user` | 邮箱用户名 | 从环境变量读取 |
| `--password` | 邮箱密码 | 从环境变量读取 |
| `--folder` | 邮箱文件夹 | `INBOX` |
| `--unread` | 只读取未读邮件 | `false` |
| `--since` | 读取此时间之后的邮件（如 "1 hour ago", "2026-06-12"） | 无限制 |
| `--limit` | 最多读取的邮件数量 | 50 |
| `--output` | 输出文件路径 | 标准输出 |

## 常见邮箱 IMAP 配置参考

| 邮箱服务商 | IMAP 服务器 | 端口 | 说明 |
|-----------|------------|------|------|
| 阿里企业邮箱 | `imap.qiye.aliyun.com` | 993 | 需开启 IMAP 服务 |
| Gmail | `imap.gmail.com` | 993 | 需 App Password |
| 163 邮箱 | `imap.163.com` | 993 | 需客户端授权码 |
| QQ 邮箱 | `imap.qq.com` | 993 | 需客户端授权码 |
| Outlook | `outlook.office365.com` | 993 | 企业邮箱 |
| 腾讯企业邮 | `imap.exmail.qq.com` | 993 | 需开启 IMAP |

详细配置见 `references/` 目录。

**故障排查：**
- `references/imap-search-troubleshooting.md` - IMAP 搜索参数问题和解决方案
- `references/qiye-aliyun-imap.md` - 阿里企业邮箱配置指南

## Common Pitfalls

1. **环境变量未加载导致认证失败**
   - 问题：运行脚本时报错"缺少邮箱用户名/密码"，但 `.env` 文件已正确配置
   - 原因：脚本不会自动加载 `~/.hermes/.env` 文件
   - 解决：使用显式参数测试，而非依赖环境变量
   ```bash
   # ❌ 可能失败（环境变量未加载）
   python fetch_emails.py --test-connection
   
   # ✅ 推荐方式（显式传递参数）
   python fetch_emails.py --user your@email.com --password your_pass --test-connection
   ```
   - 调试技巧：先用 `--debug` 参数查看实际使用的配置

2. **IMAP 搜索参数冲突（重要！）**
   - 问题：`SEARCH command error: BAD [b'invalid command or parameters']`
   - 原因：某些搜索参数组合不被 IMAP 服务器支持
   - 已知冲突：
     - `--from` + `--since` 不能同时使用
     - `--from` + `--subject` 可能失败
   - 解决：
     - 使用单一参数搜索
     - 或宽泛获取后在代码中过滤（推荐）
     - 示例：先 `--limit 30` 获取最近邮件，再用 Python 过滤发件人
   - 参考：`references/imap-search-troubleshooting.md`

3. **密码错误**
   - 问题：认证失败，提示 `AUTHENTICATIONFAILED`
   - 解决：检查是否使用了客户端专用密码（授权码），而非登录密码
   - 阿里企业邮箱：在网页版设置中生成客户端专用密码

4. **IMAP 服务未开启**
   - 问题：连接被拒绝
   - 解决：登录网页版邮箱，在设置中开启 IMAP/SMTP 服务

5. **防火墙阻止连接**
   - 问题：连接超时
   - 解决：检查本地防火墙或公司网络是否允许 993 端口出站

6. **SSL 证书验证失败**
   - 问题：`CERTIFICATE_VERIFY_FAILED`
   - 解决：确保使用正确的端口（993=SSL），或检查系统证书

7. **中文乱码**
   - 问题：邮件主题或正文显示乱码
   - 解决：脚本会自动检测编码，如仍有问题检查 `charset` 参数

8. **大附件导致内存溢出**
   - 问题：读取带大附件的邮件时崩溃
   - 解决：使用 `--skip-attachments` 跳过附件，或增加 `--limit` 限制数量

## Verification Checklist

- [ ] 已在 `~/.hermes/.env` 中配置 IMAP 环境变量
- [ ] 已在邮箱网页版开启 IMAP/SMTP 服务
- [ ] 已测试 IMAP 连接（使用脚本的 `--test-connection` 参数）
- [ ] 已验证能读取未读邮件
- [ ] 已验证邮件内容编码正确（特别是中文）
- [ ] 已配置防火墙允许 993 端口出站

## One-Shot Recipes

### 场景 1：快速测试连接

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --test-connection
```

### 场景 2：读取最近 1 小时的未读邮件

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread \
  --since "1 hour ago" \
  --limit 20
```

### 场景 3：读取特定发件人的邮件

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --from "boss@company.com" \
  --limit 10
```

### 场景 4：配合 email-summarizer 生成汇报

```bash
# 读取邮件
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread --since "1 hour ago" > /tmp/emails.json

# 生成汇报
python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --input /tmp/emails.json \
  --output /tmp/report.md

# 查看汇报
cat /tmp/report.md
```

## 与其他技能配合

- **email-summarizer**: 读取邮件后自动整理生成汇报
- **weekly-report**: 周报解析与归档（支持 Excel 附件解析）
- **himalaya**: 作为备选邮件工具（终端邮件客户端）
- **cronjob**: 定时执行邮件检查任务

**移动端汇报格式：** 见 `email-summarizer` 技能的 `references/mobile-format.md` - 微信推送格式优化指南。

**周报解析：** 见 `weekly-report` 技能 - 支持从 Excel 附件提取周报内容。

**Cron 集成文档：** 见 `references/cron-integration.md` - 定时汇报集成指南。

**微信故障排查：** 见 `references/weixin-troubleshooting.md` - 微信连接和发送问题排查。

**集成文档：**
- `references/cron-integration.md` - Cron 定时汇报集成指南
- `references/weixin-troubleshooting.md` - 微信连接故障排查指南

## 安全建议

1. **使用客户端专用密码**：不要在 `.env` 中使用主密码
2. **限制 `.env` 文件权限**：`chmod 600 ~/.hermes/.env`
3. **定期轮换密码**：建议每 90 天更换一次
4. **监控异常登录**：定期检查邮箱登录记录
