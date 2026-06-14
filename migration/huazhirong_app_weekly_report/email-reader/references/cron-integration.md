# Cron 定时邮件汇报集成指南

## 概述

本文档介绍如何使用 Hermes cron 系统实现定时邮件汇报，自动读取邮件并推送到微信等平台。

## 架构设计

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Cron Scheduler │ ──→ │ email-report.sh  │ ──→ │   微信推送      │
│  (每天 8:00)     │     │ 编排脚本          │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
       ┌──────────┐   ┌──────────────┐  ┌──────────┐
       │ email-   │   │ email-       │  │ 格式化   │
       │ reader   │──→│ summarizer   │──→│ mobile   │
       └──────────┘   └──────────────┘  └──────────┘
```

## 配置步骤

### 1. 环境变量配置

在 `~/.hermes/.env` 中添加：

```bash
# 阿里企业邮箱 IMAP 配置
EMAIL_IMAP_HOST=imap.qiye.aliyun.com
EMAIL_IMAP_PORT=993
EMAIL_IMAP_USER=your_email@company.com
EMAIL_IMAP_PASSWORD=你的授权码

# 可选：自定义汇报参数
EMAIL_REPORT_SINCE=24 hours ago
EMAIL_REPORT_LIMIT=100
```

### 2. 创建 Cron 任务

```bash
hermes cron create "0 8 * * *" \
  "读取过去 24 小时的未读邮件并生成汇报" \
  --name "邮件定时汇报" \
  --deliver "weixin:your_wechat_id" \
  --script "custom/scripts/email-report.sh" \
  --no-agent
```

### 3. 验证任务

```bash
# 查看任务列表
hermes cron list

# 手动触发测试
hermes cron run <job_id>

# 查看任务状态
hermes cron status
```

## 编排脚本说明

脚本位置：`~/.hermes/skills/custom/scripts/email-report.sh`

### 脚本功能

1. 从环境变量读取邮箱配置
2. 调用 `email-reader` 读取邮件
3. 调用 `email-summarizer` 生成汇报
4. 无邮件时静默（不推送）
5. 自动清理临时文件

### 脚本参数

可通过环境变量自定义：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `EMAIL_REPORT_SINCE` | 读取时间范围 | `24 hours ago` |
| `EMAIL_REPORT_LIMIT` | 最大邮件数 | `100` |

### 示例用法

```bash
# 基本用法（使用环境变量）
./email-report.sh

# 自定义时间范围
EMAIL_REPORT_SINCE="12 hours ago" ./email-report.sh

# 限制邮件数量
EMAIL_REPORT_LIMIT=50 ./email-report.sh
```

## Cron 调度配置

### 推荐时间表

| 场景 | Cron 表达式 | 说明 |
|------|------------|------|
| 每日早报 | `0 8 * * *` | 每天上午 8 点（推荐） |
| 每日晚报 | `0 18 * * *` | 每天下午 6 点 |
| 每小时 | `0 * * * *` | 整点执行 |
| 每 30 分钟 | `*/30 * * * *` | 适合高频邮件 |
| 工作日 | `0 8 * * 1-5` | 工作日早上 8 点 |

### Cron 表达式参考

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ 星期 (0-7, 0 和 7 都是周日)
│ │ │ └─── 月份 (1-12)
│ │ └───── 日期 (1-31)
│ └─────── 小时 (0-23)
└───────── 分钟 (0-59)
```

示例：
- `0 8 * * *` - 每天 8:00
- `0 8 * * 1-5` - 工作日 8:00
- `*/30 * * * *` - 每 30 分钟
- `0 9 * * *` - 每天 9:00

## 交付目标配置

### 微信推送

```bash
--deliver "weixin:o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat"
```

需要配置：
- `WEIXIN_ALLOWED_USERS` 包含用户 ID
- `WEIXIN_HOME_CHANNEL` 设置默认频道

### 其他平台

```bash
# Telegram
--deliver "telegram:chat_id"

# 本地文件（调试用）
--deliver "local"

# 所有平台
--deliver "all"
```

## 执行模式对比

### no-agent 模式（推荐）

```bash
hermes cron create "0 8 * * *" \
  --script "custom/scripts/email-report.sh" \
  --no-agent
```

**优点：**
- ✅ 直接运行脚本，无 LLM 调用
- ✅ 执行快速，成本低
- ✅ 输出确定，无随机性
- ✅ 适合固定流程任务

**缺点：**
- ❌ 无法动态调整逻辑
- ❌ 需要预先编写脚本

### agent 模式

```bash
hermes cron create "0 8 * * *" \
  "使用 email-reader 读取邮件并生成汇报"
```

**优点：**
- ✅ 灵活，可动态调整
- ✅ 自然语言描述即可

**缺点：**
- ❌ 每次执行调用 LLM
- ❌ 成本较高
- ❌ 输出可能有变化

## 监控与调试

### 查看执行历史

```bash
hermes cron list
```

输出示例：
```
3518f5e5d2f6 [active]
  Name:      邮件定时汇报
  Schedule:  0 8 * * *
  Next run:  2026-06-13T08:00:00+08:00
  Script:    custom/scripts/email-report.sh
  Mode:      no-agent
```

### 查看输出文件

```bash
# 查看最近的汇报
ls -lt ~/.hermes/cron/output/

# 查看特定任务的输出
ls -lt ~/.hermes/cron/output/<job_id>/
```

### 查看日志

```bash
# Gateway 日志（包含 cron 执行记录）
tail -100 ~/.hermes/logs/gateway.log

# 搜索 cron 相关日志
grep "cron" ~/.hermes/logs/gateway.log | tail -50
```

### 常见问题排查

**问题 1：任务未执行**
- 检查 Gateway 是否运行：`hermes gateway status`
- 检查任务是否启用：`hermes cron list`
- 查看错误日志：`tail -50 ~/.hermes/logs/gateway.log`

**问题 2：推送失败**
- 检查平台配置：确认 `WEIXIN_ALLOWED_USERS` 已配置
- 检查网络连接：`ping ilinkai.weixin.qq.com`
- 查看推送日志：`grep "weixin" ~/.hermes/logs/gateway.log`

**问题 3：无邮件时仍推送**
- 确认脚本使用 `--silent-if-empty` 参数
- 检查脚本是否正确输出 `[SILENT]`

**问题 4：授权码错误**
- 重新生成客户端专用密码
- 更新 `.env` 中的 `EMAIL_IMAP_PASSWORD`
- 测试连接：`./fetch_emails.py --test-connection`

## 最佳实践

### 1. 时间选择

- **早报**：8:00-9:00（上班后查看）
- **晚报**：17:00-18:00（下班前总结）
- **避免**：深夜、周末（除非必要）

### 2. 频率控制

- **高频邮件**：每 30 分钟 -1 小时
- **正常邮件**：每天 1-2 次
- **低频邮件**：每天 1 次或隔天

### 3. 数量限制

- 建议 `--max-emails 20-50`
- 避免单次汇报过长
- 截断时提示"还有 X 封未显示"

### 4. 静默模式

- 务必使用 `--silent-if-empty`
- 无邮件时不打扰用户
- 节省推送资源

### 5. 测试流程

```bash
# 1. 手动测试脚本
./email-report.sh

# 2. 创建测试任务（1 分钟后执行）
hermes cron create "$(date -v+1M +%H:%M)" \
  --script "custom/scripts/email-report.sh" \
  --no-agent \
  --name "测试邮件汇报"

# 3. 验证推送
# 等待 1 分钟后检查微信

# 4. 删除测试任务
hermes cron remove <test_job_id>

# 5. 创建正式任务
hermes cron create "0 8 * * *" \
  --script "custom/scripts/email-report.sh" \
  --no-agent \
  --name "邮件定时汇报"
```

## 安全建议

### 1. 凭证保护

```bash
# 设置 .env 文件权限
chmod 600 ~/.hermes/.env

# 验证权限
ls -la ~/.hermes/.env
# 应显示：-rw------- 1 user staff ...
```

### 2. 只读访问

- `email-reader` 技能仅为只读权限
- 禁止删除、移动、修改邮件
- 确保邮箱数据安全

### 3. 推送控制

- 配置 `WEIXIN_ALLOWED_USERS` 白名单
- 避免向未授权用户推送
- 定期审查推送记录

## 扩展场景

### 多邮箱聚合

```bash
# 创建多个读取任务，汇总到一个汇报
hermes cron create "0 8 * * *" \
  --script "custom/scripts/email-report-multi.sh" \
  --no-agent
```

### 条件推送

```bash
# 仅在有紧急邮件时推送
EMAIL_SUMMARIZER_KEYWORDS="紧急，ASAP" ./email-report.sh
```

### 分类推送

```bash
# 工作邮件推送到微信
# 系统邮件推送到邮件
# 告警邮件推送到短信
```

## 相关文档

- `email-reader` 技能 - 邮件读取配置
- `email-summarizer` 技能 - 汇报格式配置
- `references/mobile-format.md` - 移动端格式规范
