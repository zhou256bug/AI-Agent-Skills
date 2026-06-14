# 微信发送故障排查指南

## 常见故障

### 1. iLink 频率限制 ⚠️

**现象：**
```
iLink sendmessage rate limited; cooldown active for 30.0s
```

**原因：**
- 短时间内发送消息过多
- iLink API 触发限流保护（30 秒冷却）

**解决：**
1. 等待 30 秒后重试
2. 定时任务间隔 ≥ 60 分钟
3. 避免短时间内多次发送

**日志示例：**
```log
2026-06-13 07:19:29,032 ERROR gateway.platforms.weixin: 
  [Weixin] send failed to=o9cq80x3: 
  iLink sendmessage rate limited; cooldown active for 30.0s
```

### 2. 网络连接不稳定

**现象：**
```
[Weixin] poll error: Server disconnected
[Weixin] poll error: Cannot connect to host ilinkai.weixin.qq.com
```

**原因：**
- iLink 服务器连接不稳定
- 网络波动

**解决：**
1. 重启 Gateway：`hermes gateway restart`
2. 检查网络连接
3. 等待网络恢复

### 3. 用户未授权

**现象：**
```
Unauthorized user: o9cq80x3-X2_...
```

**原因：**
- 用户不在 `WEIXIN_ALLOWED_USERS` 列表中

**解决：**
```bash
# 编辑 .env 文件
nano ~/.hermes/.env

# 添加用户
WEIXIN_ALLOWED_USERS=o9cq80x3
```

### 4. 配置丢失

**现象：**
```
Weixin startup failed: WEIXIN_TOKEN is required
```

**原因：**
- 微信配置被清除
- 需要重新配对

**解决：**
1. 运行 `hermes gateway setup`
2. 选择 "Weixin / WeChat"
3. 扫描二维码重新配对

## 发送方式对比

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| `hermes chat -q` | CLI 终端对话 | 本地查看，**不发送到微信** |
| `send_message` | 发送到指定平台 | 需要知道 chat_id |
| 文件路径通知 | 发送文件路径文本 | 微信限流时的备选方案 |
| HTML 文件 | 发送 HTML 格式 | 微信可直接预览 |

## 最佳实践

### 定时任务配置

```bash
# ✅ 推荐：每小时整点执行
hermes cron create "0 * * * *" "整点报时" \
  --deliver "weixin:o9cq80x3-..."

# ✅ 推荐：每天固定时间（9:00, 12:00, 18:00）
hermes cron create "0 9,12,18 * * *" "时间播报"

# ❌ 避免：间隔太短（如每 20 分钟）
hermes cron create "every 20m" "时间播报"
```

### 周报发送模板

```bash
# 1. 生成汇报
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action parse --week 23 --excel /tmp/week23.xls

# 2. 归档保存
mkdir -p ~/Documents/weekly-reports/2026/week-23
mv /tmp/week23.* ~/Documents/weekly-reports/2026/week-23/

# 3. 发送微信通知（文件路径 + 摘要）
hermes chat -q "
📋 工作周报 · 第 23 期已生成

🏢 海外应用开发部
📅 2026.06.01-06.07
👤 共 15 人

⭐ 重点成果（Top 5）：
1️⃣ 林旭伟 - Airwallex 项目 UI 适配完成
2️⃣ 丁璞 - Winfopay 9220U 识别问题解决
3️⃣ 胡陈琛 - 欧洲装机程序开发
4️⃣ 李家俊 - OMA 5320 固件交付
5️⃣ 李响 - 土耳其税控模块跟进

📄 完整报告：
~/Documents/weekly-reports/2026/week-23/week-23.pdf

✅ 周报整理完成
"
```

## 故障排查命令

```bash
# 检查 Gateway 状态
hermes gateway status

# 查看微信配置
grep "WEIXIN" ~/.hermes/.env

# 查看最近日志
tail -50 ~/.hermes/logs/gateway.log | grep -i "weixin\|send\|error"

# 检查定时任务
hermes cron list

# 重启 Gateway
hermes gateway restart
```

## 相关资源

- [Hermes 微信配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
- iLink Bot API: https://ilinkai.weixin.qq.com
- 日志路径：`~/.hermes/logs/gateway.log`
