# 阿里企业邮箱 IMAP 配置指南

## 服务器信息

### IMAP 设置（收件）

| 配置项 | 值 |
|--------|-----|
| 服务器 | `imap.qiye.aliyun.com` |
| 端口 | `993` |
| 加密 | SSL/TLS |
| 用户名 | 完整邮箱地址（如 `user@yourcompany.com`） |
| 密码 | 邮箱密码或客户端专用密码 |

### SMTP 设置（发件）

| 配置项 | 值 |
|--------|-----|
| 服务器 | `smtp.qiye.aliyun.com` |
| 端口 | `465` (SSL) 或 `587` (TLS) |
| 加密 | SSL/TLS |
| 用户名 | 完整邮箱地址 |
| 密码 | 邮箱密码或客户端专用密码 |

---

## 启用 IMAP/SMTP 服务

### 步骤 1：登录网页版

访问：https://qiye.aliyun.com

使用你的企业邮箱账号登录。

### 步骤 2：进入设置

1. 点击右上角 **设置** 图标（齿轮）
2. 选择 **客户端设置**

### 步骤 3：开启服务

在 **客户端设置** 页面：

1. 找到 **IMAP/SMTP 服务** 选项
2. 点击 **开启**
3. 阅读并同意服务协议

### 步骤 4：生成客户端专用密码（推荐）

为了安全，建议使用客户端专用密码而非主密码：

1. 在 **客户端设置** 页面找到 **客户端专用密码**
2. 点击 **生成新密码**
3. 输入密码名称（如 "Hermes Agent"）
4. 点击 **确定**
5. **复制并保存** 生成的密码（只会显示一次）

### 步骤 5：配置环境变量

将生成的密码保存到 Hermes 配置：

```bash
# 编辑 .env 文件
nano ~/.hermes/.env

# 添加以下内容
EMAIL_IMAP_HOST=imap.qiye.aliyun.com
EMAIL_IMAP_PORT=993
EMAIL_IMAP_USER=your_email@yourcompany.com
EMAIL_IMAP_PASSWORD=你的客户端专用密码
```

---

## 测试连接

使用 email-reader 技能测试连接：

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --test-connection
```

成功输出示例：

```json
{
  "success": true,
  "message": "IMAP 连接成功",
  "host": "imap.qiye.aliyun.com",
  "port": 993,
  "user": "your_email@yourcompany.com",
  "timestamp": "2026-06-12T14:30:00+08:00"
}
```

---

## 常见问题排查

### 问题 1：认证失败 (AUTHENTICATIONFAILED)

**可能原因：**
- 使用了主密码而非客户端专用密码
- IMAP/SMTP 服务未开启
- 密码已过期

**解决方案：**
1. 确认已开启 IMAP/SMTP 服务
2. 生成新的客户端专用密码
3. 更新 `.env` 文件中的密码

### 问题 2：连接超时

**可能原因：**
- 防火墙阻止 993 端口
- 公司网络限制
- 服务器地址错误

**解决方案：**
1. 检查防火墙设置：`telnet imap.qiye.aliyun.com 993`
2. 联系 IT 部门确认网络策略
3. 确认服务器地址正确

### 问题 3：SSL 证书错误

**可能原因：**
- 系统证书过期
- 使用了错误的端口

**解决方案：**
1. 确认使用 993 端口（SSL）
2. 更新系统证书：`sudo security find-certificate -a`
3. 如仍不行，可临时禁用证书验证（不推荐）

### 问题 4：找不到邮件

**可能原因：**
- 文件夹名称错误
- 搜索条件过于严格

**解决方案：**
1. 确认文件夹名称（默认 `INBOX`）
2. 尝试不使用搜索条件：去掉 `--unread`、`--since` 等参数
3. 使用 `--debug` 查看详细日志

---

## 安全建议

### 1. 使用客户端专用密码

- 不要使用主密码
- 定期更换（建议 90 天）
- 为不同应用生成不同密码

### 2. 保护 .env 文件

```bash
# 设置文件权限（仅所有者可读写）
chmod 600 ~/.hermes/.env

# 验证权限
ls -la ~/.hermes/.env
# 应显示：-rw------- 1 user staff ...
```

### 3. 监控登录活动

定期登录网页版邮箱，检查 **登录日志**，查看是否有异常登录。

### 4. 限制 IP 访问（企业版功能）

如果企业邮箱支持，可以配置 IP 白名单，只允许公司网络访问。

---

## 其他配置示例

### 读取未读邮件

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread \
  --since "1 hour ago" \
  --limit 20
```

### 读取特定发件人

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --from "boss@company.com" \
  --limit 10
```

### 读取特定主题

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --subject "会议" \
  --unread
```

### 保存结果到文件

```bash
python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --unread \
  --output /tmp/emails.json \
  --pretty
```

---

## 相关资源

- [阿里企业邮箱官方文档](https://help.aliyun.com/product/44966.html)
- [IMAP 协议规范](https://tools.ietf.org/html/rfc3501)
- [Python imaplib 文档](https://docs.python.org/3/library/imaplib.html)
