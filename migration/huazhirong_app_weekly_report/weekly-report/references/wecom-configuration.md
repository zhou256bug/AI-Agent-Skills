# 企业微信（WeCom）配置指南

## 优势对比

| 功能 | 个人微信 | 企业微信 |
|------|----------|----------|
| **限流** | ❌ 30 秒冷却 | ✅ 不限流 |
| **群聊** | ❌ 不支持 | ✅ 支持 |
| **稳定性** | ⚠️ 经常断开 | ✅ 稳定 |
| **文件发送** | ⚠️ 有限制 | ✅ 支持 |
| **消息长度** | ⚠️ 有限制 | ✅ 更长 |
| **配置难度** | ⭐ 简单（扫码） | ⭐⭐ 中等（需创建应用） |

**推荐：** 如有企业微信，优先使用企业微信（更稳定、不限流）

---

## 配置步骤

### 步骤 1：创建企业微信自建应用

1. 登录 **企业微信管理后台**：https://work.weixin.qq.com
2. 进入 **应用管理** → **应用** → **自建**
3. 点击 **创建应用**
   - 名称：`Hermes Agent` 或 `周报助手`
   - 上传 Logo（可选）
   - 可见范围：选择自己或部门
4. 创建后记录以下信息：
   - **CorpId**（企业 ID）
   - **AgentId**（应用 ID）
   - **Secret**（应用密钥）

### 步骤 2：配置 Hermes

编辑 `~/.hermes/.env` 文件，添加：

```bash
# 企业微信配置
WECOM_BOT_ID=<你的 Bot ID>
WECOM_SECRET=<你的 Secret>
WECOM_DM_POLICY=pairing
WECOM_ALLOWED_USERS=<你的企业微信用户 ID>
WECOM_HOME_CHANNEL=<你的企业微信用户 ID>
```

**获取用户 ID：**
- 查看 Gateway 日志：`tail -20 ~/.hermes/logs/gateway.log | grep "inbound from="`
- 或从企业微信后台查看

### 步骤 3：重启 Gateway

```bash
hermes gateway restart
```

### 步骤 4：测试连接

在企业微信给 Hermes 发送消息：
- "测试"
- "在吗"

如果收到回复，说明配置成功！

---

## 常见问题

### 问题 1：用户未授权

**日志：**
```
WARNING gateway.run: Unauthorized user: wolB10EAAAFcdETbLL3wHglQZRxWFIkw on wecom
```

**解决：**
```bash
# 添加用户到允许列表
echo "WECOM_ALLOWED_USERS=wolB10EAAAFcdETbLL3wHglQZRxWFIkw" >> ~/.hermes/.env
echo "WECOM_HOME_CHANNEL=wolB10EAAAFcdETbLL3wHglQZRxWFIkw" >> ~/.hermes/.env
hermes gateway restart
```

### 问题 2：连接失败

**日志：**
```
ERROR gateway.platforms.wecom: Failed to connect to wss://openws.work.weixin.qq.com
```

**解决：**
- 检查网络是否可访问 `openws.work.weixin.qq.com`
- 确认 CorpId 和 Secret 配置正确
- 重启 Gateway

### 问题 3：收不到消息

**可能原因：**
- 应用可见范围未包含自己
- 用户未授权

**解决：**
- 在企业微信后台检查应用可见范围
- 确认用户 ID 已添加到 `WECOM_ALLOWED_USERS`

---

## 配置示例

```bash
# ~/.hermes/.env 文件示例

# 个人微信配置（备用）
WEIXIN_ACCOUNT_ID=86421b9c079a@im.bot
WEIXIN_TOKEN=86421b...a03e
WEIXIN_ALLOWED_USERS=o9cq809n
WEIXIN_HOME_CHANNEL=o9cq809nVomNJ57JU7rlAbWnk290@im.wechat

# 企业微信配置（推荐）
WECOM_BOT_ID=aibZgdr_maGOn2hpoiDCR2n2n09hmbuHxry
WECOM_SECRET=pufiDQ...szIv
WECOM_DM_POLICY=pairing
WECOM_ALLOWED_USERS=wolB10EAAAFcdETbLL3wHglQZRxWFIkw
WECOM_HOME_CHANNEL=wolB10EAAAFcdETbLL3wHglQZRxWFIkw
```

---

## 发送消息

### 方式 1：使用 send_message 工具

```bash
hermes chat -q "发送以下消息到企业微信：

📋 工作周报 · 第 23 期
🏢 海外应用开发部
📅 2026.06.01-06.07
──────────────────────────────
🔴 重点成果：林旭伟、丁璞等
📄 完整报告：~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf
✅ 周报整理完成
"
```

### 方式 2：使用专用脚本

```bash
python ~/.hermes/skills/custom/scripts/send_wechat_report.py \
  --week 23 \
  --recipient "wolB10EAAAFcdETbLL3wHglQZRxWFIkw" \
  --pdf "~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf"
```

---

## 相关资源

- [企业微信官方文档](https://work.weixin.qq.com/api/doc)
- [Hermes Gateway 配置](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
- [周报技能文档](../SKILL.md)
