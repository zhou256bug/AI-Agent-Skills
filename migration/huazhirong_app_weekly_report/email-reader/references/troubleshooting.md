# 邮件技能故障排查指南

## 会话记录：2026-06-12 邮件技能调试

### 问题 1：环境变量未加载

**现象：**
```bash
python fetch_emails.py --test-connection
# 输出：{"success": false, "error": "缺少邮箱用户名，请设置 --user 或 EMAIL_IMAP_USER 环境变量"}
```

**原因：**
- 脚本不会自动加载 `~/.hermes/.env` 文件
- 环境变量需要通过 shell 导出或显式传递参数

**解决方案：**

方式 1 - 显式传递参数（推荐）：
```bash
python fetch_emails.py \
  --user qiang.zhou@newpostech.com \
  --password YourAuthCode \
  --test-connection
```

方式 2 - 导出环境变量：
```bash
export EMAIL_IMAP_HOST=imap.qiye.aliyun.com
export EMAIL_IMAP_PORT=993
export EMAIL_IMAP_USER=qiang.zhou@newpostech.com
export EMAIL_IMAP_PASSWORD=YourAuthCode
python fetch_emails.py --test-connection
```

方式 3 - 使用 Hermes 终端工具（会自动加载 .env）：
```bash
# 在 Hermes 对话中使用 terminal 工具
terminal(command="python fetch_emails.py --test-connection")
```

---

### 问题 2：认证失败 (LOGIN failed)

**现象：**
```json
{"success": false, "error": "处理失败：b'LOGIN failed.'"}
```

**排查步骤：**

1. **确认 IMAP 服务已开启**
   - 登录网页版邮箱
   - 设置 → 客户端设置
   - 确认 IMAP/SMTP 服务已开启

2. **确认使用授权码而非登录密码**
   - 阿里企业邮箱：客户端专用密码
   - QQ 邮箱：授权码
   - 163 邮箱：客户端授权码
   - Gmail：App Password

3. **测试连接（使用显式参数）**
   ```bash
   python fetch_emails.py \
     --user your@email.com \
     --password YourAuthCode \
     --debug \
     --test-connection
   ```

4. **检查授权码是否有隐藏字符**
   ```bash
   # 查看 .env 文件中的密码是否有换行或空格
   grep "EMAIL_IMAP_PASSWORD" ~/.hermes/.env | od -c
   ```

5. **企业微信能登录但脚本失败？**
   - 企业微信可能使用不同的认证方式（OAuth）
   - 脚本使用标准 IMAP 协议，需要 IMAP 专用授权码
   - 在网页版重新生成客户端专用密码

---

### 问题 3：Python 变量作用域冲突

**现象：**
```python
UnboundLocalError: cannot access local variable 'group_emails' where it is not associated with a value
```

**原因：**
- 函数内部循环变量名与函数名冲突
- 例如：`for group_name, group_emails in groups.items()` 覆盖了 `group_emails()` 函数

**解决方案：**
- 重命名循环变量，避免与函数名冲突
- 例如：`for group_name, group_mails in groups.items()`

**预防措施：**
- 循环变量使用复数名词（`mails`, `items`, `records`）
- 函数名使用动词或动词短语（`fetch_emails`, `load_data`）
- 代码审查时注意变量遮蔽问题

---

### 问题 4：管道命令执行失败

**现象：**
```bash
python fetch_emails.py | python summarize.py
# 输出：Security scan — Pipe to interpreter denied
```

**原因：**
- Hermes 安全策略禁止管道直接传递到解释器
- 防止下载的内容未经检查直接执行

**解决方案：**
使用中间文件：
```bash
# 步骤 1：读取邮件保存到文件
python fetch_emails.py --output /tmp/emails.json

# 步骤 2：从文件读取并生成汇报
python summarize.py --input /tmp/emails.json
```

---

## 调试命令速查

```bash
# 测试 IMAP 连接
python fetch_emails.py --user user@email.com --password pass --test-connection --debug

# 读取最近邮件
python fetch_emails.py --user user@email.com --password pass --limit 5 --pretty

# 读取未读邮件
python fetch_emails.py --user user@email.com --password pass --unread --since "1 hour ago"

# 生成汇报（使用文件）
python fetch_emails.py --output /tmp/emails.json
python summarize.py --input /tmp/emails.json

# 检查环境变量配置
grep "EMAIL_IMAP" ~/.hermes/.env

# 查看授权码是否有隐藏字符
grep "EMAIL_IMAP_PASSWORD" ~/.hermes/.env | od -c
```

---

## 阿里企业邮箱特殊问题

### 授权码永不过期但仍失败

**可能原因：**
1. IMAP 服务未开启（最常见）
2. 授权码复制时多了空格或换行
3. 用户名格式错误（应使用完整邮箱地址）
4. 公司网络防火墙阻止 993 端口

**排查顺序：**
1. 确认网页版能登录
2. 确认 IMAP/SMTP 服务已开启
3. 重新生成授权码（删除旧的）
4. 使用显式参数测试（避免环境变量问题）
5. 检查网络连接：`telnet imap.qiye.aliyun.com 993`

### 企业微信能登录但 IMAP 失败

**原因：**
- 企业微信使用 OAuth 或其他认证方式
- IMAP 需要专用的客户端授权码

**解决：**
1. 登录网页版（不是企业微信）
2. 设置 → 客户端设置
3. 生成客户端专用密码
4. 使用该密码配置 IMAP

---

## 联系支持

如以上方法均无效，请收集以下信息：

1. 完整的错误输出
2. `--debug` 模式的输出
3. 邮箱服务商和配置
4. 网络环境（公司网络/家庭网络/VPN）

然后联系 Hermes Agent 支持或检查技能文档更新。
