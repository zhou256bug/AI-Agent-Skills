# 阿里企业邮箱 IMAP 配置参考

## 服务器地址

| 区域/版本 | IMAP 主机 | 端口（SSL） |
|-----------|-----------|-------------|
| 中国大陆企业邮箱（默认） | `imap.qiye.aliyun.com` | 993 |
| 香港 | `imaphk.qiye.aliyun.com` | 993 |
| 万网/旧版域名邮箱 | `imap.mxhichina.com` | 993 |

官方文档：[IMAP/POP/SMTP 服务器地址及端口配置](https://help.aliyun.com/zh/document_detail/36576.html)

## 管理员前置条件

阿里企业邮箱**默认可能禁止第三方客户端**。若登录失败，请让邮箱管理员在管理后台：

1. 确认账号未被单独限制三方客户端登录
2. 按官方指引开启「允许使用第三方客户端」

参考：[如何允许/关闭使用三方客户端功能？](https://help.aliyun.com/zh/document_detail/606337.html)

## 凭据

| 方式 | 说明 |
|------|------|
| 登录密码 | 部分租户可直接使用网页登录密码 |
| 客户端授权密码 | 更安全；在网页邮箱「设置 → 账户与安全」中生成专用密码 |

**禁止**把密码写入代码、提交到 Git 或写进 skill 文档。统一使用环境变量。

## 环境变量

在业务工程或 Agent 运行环境配置（详见 `references/agent-setup.md`）：

**推荐用户级文件**（本机多 Agent 共用）：

```bash
~/.config/aliyun-enterprise-mail/credentials.env   # chmod 600
```

或通过环境变量 / Agent Secrets：

```bash
export ALIYUN_MAIL_USER="your.name@company.com"
export ALIYUN_MAIL_PASSWORD="your-client-auth-password"
# 可选
export ALIYUN_MAIL_IMAP_HOST="imap.qiye.aliyun.com"
export ALIYUN_MAIL_IMAP_PORT="993"
export ALIYUN_MAIL_ENV_FILE="/path/to/credentials.env"
```

验证：`python aliyun-enterprise-mail/scripts/read_mail.py doctor`

## 常见错误

| 现象 | 可能原因 |
|------|----------|
| `LOGIN failed` | 密码错误、未开三方客户端、账号被限制 |
| `connection refused` / 超时 | 主机名错误、公司防火墙拦截 993 端口 |
| 文件夹为空但网页有信 | 选错文件夹；部分系统文件夹名需用 `INBOX` |
| 中文主题/发件人乱码 | 本 skill 已用 MIME 解码；若仍异常请提供原始样本 |

## 与本 skill 的关系

- 读信走 **IMAP + SSL**，只读模式打开文件夹（`readonly=True`），不会自动删信或改已读状态（使用 `BODY.PEEK`）。
- 发信、移动、删除等写操作**尚未实现**；后续可扩展 SMTP 与 IMAP STORE。
