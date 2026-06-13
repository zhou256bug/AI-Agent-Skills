# 多 Agent 凭据配置指南

本文说明 **Cursor / Codex / OpenClaw / Hermes** 等 Agent 如何共用凭据契约。

> **OpenClaw / Hermes 用户**：注册配置见 `openclaw-hermes-registration.md`；对话引导见 `onboarding-flow.md`。

## 两种配置模式

| 模式 | 适用 | 入口 |
|------|------|------|
| **Agent 引导（推荐）** | OpenClaw、Hermes、对话式 Agent | `setup status` → 对话 → `setup apply --verify` |
| **手动/Secrets** | Cursor Cloud、运维脚本 | 环境变量或手建 credentials.env |

## Agent 引导模式（clone 开箱即用）

```bash
python aliyun-enterprise-mail/scripts/read_mail.py setup status
# needsSetup: true → 按 fieldsToCollect 向用户提问

python aliyun-enterprise-mail/scripts/read_mail.py setup apply \
  --user "name@company.com" \
  --password "CLIENT_AUTH_PASSWORD" \
  --target skill \
  --verify
```

默认写入 `aliyun-enterprise-mail/local/credentials.env`（gitignore，不提交）。

详见 **`references/onboarding-flow.md`**。

## 统一契约

所有 Agent 最终都应让 Python 进程可见以下环境变量（**名称固定，不要各平台自创别名**）：

| 变量 | 必填 | 说明 |
|------|------|------|
| `ALIYUN_MAIL_USER` | ✅ | 完整邮箱地址 |
| `ALIYUN_MAIL_PASSWORD` | ✅ | 客户端授权密码（推荐）或登录密码 |
| `ALIYUN_MAIL_IMAP_HOST` | 否 | 默认 `imap.qiye.aliyun.com` |
| `ALIYUN_MAIL_IMAP_PORT` | 否 | 默认 `993` |
| `ALIYUN_MAIL_ENV_FILE` | 否 | 指向凭据文件路径 |

## 推荐：用户级配置文件（配一次，多 Agent 共用）

```bash
mkdir -p ~/.config/aliyun-enterprise-mail
cp aliyun-enterprise-mail/credentials.env.example \
   ~/.config/aliyun-enterprise-mail/credentials.env
chmod 600 ~/.config/aliyun-enterprise-mail/credentials.env
# 编辑 credentials.env，填入真实账号
```

验证：

```bash
python aliyun-enterprise-mail/scripts/read_mail.py doctor
```

`doctor` 会报告：从哪些路径加载了凭据、配置是否齐全、IMAP 是否登录成功。**不会输出密码明文**。

## 凭据加载优先级

`read_mail.py` 启动时按以下顺序尝试（**不覆盖进程里已有的非空环境变量**）：

1. **进程环境变量** — Agent Secrets、CI、`export` 注入（最高优先级）
2. **`--env-file`** — CLI 显式指定
3. **`ALIYUN_MAIL_ENV_FILE`** — 环境变量指向的文件
4. **`./.aliyun-mail.env`** — 当前工作目录（项目级）
5. **`~/.config/aliyun-enterprise-mail/credentials.env`** — 用户级（推荐默认）
6. **`~/.aliyun-mail.env`** — 用户级简写路径

因此：

- **Cloud Agent** 可在 Secrets 里直接配 4 个变量，无需落盘
- **本机 Agent** 可只维护 `~/.config/.../credentials.env`，不必配系统变量
- **项目专用邮箱** 可在项目根放 `.aliyun-mail.env`（务必 gitignore）

## 各 Agent 接入方式

### Cursor（本地 + Cloud Agent）

| 场景 | 做法 |
|------|------|
| Cloud Agent | 在 Cursor **Secrets / 环境变量** 中配置 `ALIYUN_MAIL_USER`、`ALIYUN_MAIL_PASSWORD` |
| 本地 Agent | 使用 `~/.config/aliyun-enterprise-mail/credentials.env`，skill 自动加载 |
| 项目专用 | 项目根 `.aliyun-mail.env` + `.gitignore` |

Agent 工作流建议固定为：

```bash
python aliyun-enterprise-mail/scripts/read_mail.py doctor
python aliyun-enterprise-mail/scripts/read_mail.py list --folder INBOX --limit 10
python aliyun-enterprise-mail/scripts/read_mail.py read --uid <UID>
```

### Codex / CLI 类 Agent

**方式 A**：启动前加载同一文件

```bash
set -a
# shellcheck source=/dev/null
. "$HOME/.config/aliyun-enterprise-mail/credentials.env"
set +a
python aliyun-enterprise-mail/scripts/read_mail.py doctor
```

**方式 B**：在 Agent 配置的 `env:` 段写入 4 个标准变量名。

**方式 C**：只配一行

```bash
export ALIYUN_MAIL_ENV_FILE="$HOME/.config/aliyun-enterprise-mail/credentials.env"
```

### OpenClaw / Hermes 等

若支持用户级 config + 环境变量段，任选其一：

```yaml
env:
  ALIYUN_MAIL_USER: "your.name@company.com"
  ALIYUN_MAIL_PASSWORD: "${SECRET}"   # 若平台支持密钥引用
```

或：

```yaml
env:
  ALIYUN_MAIL_ENV_FILE: "~/.config/aliyun-enterprise-mail/credentials.env"
```

若 Agent 从 shell 启动，也可在 `~/.bashrc` / `~/.zshrc` 中一次性 `source` 凭据文件（见上文 Codex 方式 A）。**不继承 shell 的 GUI Agent** 仍依赖 skill 自动读 `~/.config/.../credentials.env`。

## 项目级 `.aliyun-mail.env`

适用于某仓库使用独立邮箱账号：

```bash
# 项目根目录
echo ".aliyun-mail.env" >> .gitignore
cp aliyun-enterprise-mail/credentials.env.example .aliyun-mail.env
chmod 600 .aliyun-mail.env
```

在项目目录运行 CLI 时会自动加载；其它项目不受影响。

## 安全红线

- ❌ 禁止把 `credentials.env`、`.aliyun-mail.env` 提交到 Git
- ❌ 禁止在 SKILL、prompt、日志中写入密码
- ❌ 不建议把密码配成「系统（全用户）环境变量」
- ✅ 凭据文件权限建议 `chmod 600`
- ✅ 优先使用**客户端授权密码**，而非网页登录密码

## 排错

| `doctor` 结果 | 处理 |
|---------------|------|
| `config_error` / 缺少变量 | 检查 credentials.env 或 Agent Secrets |
| `connection_error` / LOGIN failed | 管理员开启三方客户端；确认授权密码 |
| `loadedFrom` 为空 | 文件路径不对或文件不存在 |
| 本机有配置但 Cloud Agent 失败 | Cloud 环境读不到本机 `~/.config`，需在 Cursor Secrets 再配一份 |

更多 IMAP 服务器与管理员开关见 `imap-setup.md`。
