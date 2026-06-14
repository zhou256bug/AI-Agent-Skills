# 微信连接故障排查指南

## 常见问题

### 问题 1：微信用户未授权

**症状：**
```
WARNING gateway.run: Unauthorized user: o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat
```

**原因：** `WEIXIN_ALLOWED_USERS` 未配置或用户 ID 不在列表中

**解决：**
```bash
# 1. 检查当前配置
grep "WEIXIN_ALLOWED_USERS" ~/.hermes/.env

# 2. 编辑 .env 文件
nano ~/.hermes/.env

# 3. 添加用户 ID（从日志中获取）
WEIXIN_ALLOWED_USERS=o9cq80x3

# 4. 重启 Gateway
hermes gateway restart

# 5. 验证连接
tail -20 ~/.hermes/logs/gateway.log | grep "weixin"
```

**获取用户 ID：**
- 查看 Gateway 日志：`tail -50 ~/.hermes/logs/gateway.log | grep "from="`
- 格式：`o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat`
- 只需前半部分：`o9cq80x3`

---

### 问题 2：微信 iLink API 网络连接失败

**症状：**
```
ERROR gateway.platforms.weixin: [Weixin] poll error (1/3): 
Cannot connect to host ilinkai.weixin.qq.com:443 ssl:default 
[nodename nor servname provided, or not known]
```

**原因：**
- DNS 解析失败
- 网络中断
- 防火墙阻止

**解决：**
```bash
# 1. 测试网络连接
ping ilinkai.weixin.qq.com

# 2. 如网络已恢复，重启 Gateway
hermes gateway restart

# 3. 验证连接
tail -20 ~/.hermes/logs/gateway.log | grep "Connected"
```

**时间线示例：**
```
10:08 - 微信连接成功 ✓
12:32 - 网络开始报错 🔴
13:45 - 网络恢复 ✓
14:19 - Gateway 重启，微信重连成功 ✓
```

---

### 问题 3：定时任务执行了但没收到推送

**症状：** Cron 任务显示 `ok`，但微信没有收到消息

**检查清单：**

```bash
# 1. 检查 deliver 配置
hermes cron list
# 确认 Deliver: weixin:<chat_id> 而非 local

# 2. 检查微信用户授权
grep "WEIXIN_ALLOWED_USERS" ~/.hermes/.env
# 确认已添加你的用户 ID

# 3. 检查任务输出
ls -la ~/.hermes/cron/output/<job_id>/
cat ~/.hermes/cron/output/<job_id>/<timestamp>.md
# 确认有输出内容

# 4. 检查 Gateway 日志
tail -50 ~/.hermes/logs/gateway.log | grep -E "cron|weixin"
# 查找 "Sending response" 或错误信息
```

**常见原因：**
| 原因 | 症状 | 解决 |
|------|------|------|
| deliver=local | 输出只保存到本地文件 | 重新创建任务，指定 `--deliver "weixin:<chat_id>"` |
| 用户未授权 | 日志显示 `Unauthorized user` | 添加 `WEIXIN_ALLOWED_USERS` |
| 网络中断 | 日志显示 `poll error` | 等待网络恢复，重启 Gateway |
| 微信未连接 | 日志显示 `weixin disconnected` | 重启 Gateway |

---

### 问题 4：斜杠命令未识别

**症状：**
```
WARNING gateway.run: Unrecognized slash command /cron from weixin
```

**原因：** 微信平台的工具集未包含 `cronjob`

**解决：**
```bash
# 1. 检查平台工具集配置
cat ~/.hermes/config.yaml | grep -A 5 "platform_toolsets:"

# 2. 添加 cronjob 到微信工具集
hermes config set platform_toolsets.weixin '["hermes-weixin", "cronjob"]'

# 3. 重启 Gateway
hermes gateway restart
```

---

### 问题 5：Cron 任务丢失（重启后）

**症状：** `hermes cron list` 显示 `No scheduled jobs`

**原因：** 任务未持久化，或 `jobs.json` 被清空

**解决：**
```bash
# 重新创建任务
hermes cron create "every 30m" \
  "使用 email-reader 读取过去 30 分钟的未读邮件，使用 email-summarizer 生成汇报" \
  --name "邮件定时汇报" \
  --deliver "weixin:o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat"

# 验证
hermes cron list
```

**预防：**
- 避免直接编辑 `~/.hermes/cron/jobs.json`
- 使用 `hermes cron create/remove` 命令管理任务

---

## 完整排查流程

```bash
# 步骤 1：检查 Gateway 状态
hermes gateway status
# 应显示：✓ Gateway service is loaded

# 步骤 2：检查微信连接
tail -20 ~/.hermes/logs/gateway.log | grep "weixin"
# 应显示：[Weixin] Connected

# 步骤 3：检查 Cron 任务
hermes cron list
# 应显示活跃任务

# 步骤 4：检查用户授权
grep "WEIXIN_ALLOWED_USERS" ~/.hermes/.env
# 应显示：WEIXIN_ALLOWED_USERS=<your_id>

# 步骤 5：检查网络
ping ilinkai.weixin.qq.com
# 应能解析并 ping 通

# 步骤 6：查看最近推送日志
tail -100 ~/.hermes/logs/gateway.log | grep "Sending response"
# 应显示推送成功记录
```

---

## 日志关键信息

### 成功连接
```
INFO gateway.platforms.weixin: [Weixin] Connected account=86421b9c
INFO gateway.run: ✓ weixin connected
```

### 成功推送
```
INFO gateway.platforms.base: [Weixin] Sending response (137 chars) to o9cq80x3-...
INFO gateway.run: response ready: platform=weixin chat=o9cq80x3-... time=9.3s
```

### 用户未授权
```
WARNING gateway.run: Unauthorized user: o9cq80x3-X2_ZwHwboFg4Z7Wo-qc@im.wechat
```

### 网络故障
```
ERROR gateway.platforms.weixin: [Weixin] poll error (1/3): 
Cannot connect to host ilinkai.weixin.qq.com:443
```

### 命令未识别
```
WARNING gateway.run: Unrecognized slash command /cron from weixin
```

---

## 快速修复命令

```bash
# 重启 Gateway（解决大部分问题）
hermes gateway restart

# 验证微信连接
tail -5 ~/.hermes/logs/gateway.log | grep "Connected"

# 查看 Cron 状态
hermes cron status

# 测试邮件读取
~/.hermes/hermes-agent/venv/bin/python \
  ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --test-connection
```

---

## 相关文档

- `qiye-aliyun-imap.md` - 阿里企业邮箱 IMAP 配置
- `cron-integration.md` - Cron 定时汇报集成指南
- `email-reader` SKILL.md - 邮件读取技能
- `email-summarizer` SKILL.md - 邮件整理技能
