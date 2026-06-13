---
name: aliyun-enterprise-mail
description: 阿里企业邮箱 IMAP 读信技能，支持 Agent 对话式引导配置（setup status/apply）。OpenClaw/Hermes/Codex/Cursor clone 后开箱即用：Agent 向用户收集邮箱与授权密码并写入 local/credentials.env，再 list/read 读信。Use when 读邮件、配置邮箱、setup 邮箱、查收件箱、阿里企业邮箱、企业邮、IMAP、openclaw、hermes、首次配置、引导配置。
metadata: {"openclaw":{"requires":{"bins":["python3"]},"skillKey":"aliyun-enterprise-mail","emoji":"📧"},"hermes":{"tags":["email","imap","aliyun","enterprise-mail"],"category":"productivity","requires_toolsets":["terminal"]}}
user-invocable: true
---

# Aliyun Enterprise Mail（阿里企业邮箱读信）

## Overview

通过 **IMAP over SSL** 读取阿里企业邮箱邮件。面向 **OpenClaw / Hermes** 等 Agent：**clone 仓库 → 加载 skill → 对话收集凭据 → 自动配置 → 读信**。

实现为 Python 标准库（`imaplib`、`email`），**无第三方 pip 依赖**。

**OpenClaw / Hermes 注册**：见 `references/openclaw-hermes-registration.md`（含 `openclaw.json` / `config.yaml` 复制块）。

## Agent 首次加载协议（必读）

**任何读信操作前**，Agent 必须执行：

```bash
python aliyun-enterprise-mail/scripts/read_mail.py setup status
```

| `needsSetup` | Agent 行为 |
|--------------|------------|
| `true` | 按 `fieldsToCollect` 向用户提问 → `setup apply --verify` → 再读信 |
| `false` | `doctor` → `list` / `read` |

**完整对话流程**：见 `references/onboarding-flow.md`（含话术模板、Git 边界、排错）。

**红线**：

- ❌ 禁止把密码写入代码 / commit / 日志 / 回复复述
- ❌ 禁止提交 `local/credentials.env` 或 `.aliyun-mail.env`
- ✅ clone 场景默认写入 `<skill>/local/credentials.env`（已在 `.gitignore`）

## 对话式配置示例

用户：「帮我看看收件箱有什么邮件」

Agent 内部流程：

```bash
# 1. 检测
python aliyun-enterprise-mail/scripts/read_mail.py setup status
# → needsSetup: true

# 2. 对话收集邮箱 + 客户端授权密码后写入
python aliyun-enterprise-mail/scripts/read_mail.py setup apply \
  --user "name@company.com" \
  --password "..." \
  --target auto \
  --verify

# 3. 读信
python aliyun-enterprise-mail/scripts/read_mail.py list --folder INBOX --limit 10
```

## 凭据落盘位置（`setup apply --target`）

| target | 路径 | 适用 |
|--------|------|------|
| `auto`（默认） | skill/local → repo根 → user级 | 通用 |
| `skill` | `aliyun-enterprise-mail/local/credentials.env` | **clone 开箱即用（推荐）** |
| `repo` | `./.aliyun-mail.env` | 当前 git 项目专用 |
| `user` | `~/.config/aliyun-enterprise-mail/credentials.env` | 本机多项目共用 |

加载优先级（高 → 低，不覆盖已有非空环境变量）：

1. 进程环境变量
2. `--env-file` / `ALIYUN_MAIL_ENV_FILE`
3. `./.aliyun-mail.env`
4. `<skill>/local/credentials.env`
5. `~/.config/aliyun-enterprise-mail/credentials.env`
6. `~/.aliyun-mail.env`

## Quick Start

```bash
# Agent：检查是否需要引导配置
python aliyun-enterprise-mail/scripts/read_mail.py setup status

# Agent：用户给齐信息后写入并验证
python aliyun-enterprise-mail/scripts/read_mail.py setup apply \
  --user "you@company.com" --password "..." --verify

# 读信
python aliyun-enterprise-mail/scripts/read_mail.py list --folder INBOX --limit 10
python aliyun-enterprise-mail/scripts/read_mail.py read --uid <UID>
```

## CLI 命令

| 命令 | 作用 |
|------|------|
| `setup status` | 输出 `needsSetup`、`fieldsToCollect`、推荐写入路径 |
| `setup apply` | 写入凭据（`--user` `--password` `--target` `--verify`） |
| `doctor` | 检查连通性 |
| `folders` / `list` / `read` / `search` | 读信 |

## 默认 IMAP 端点

| 场景 | 主机 |
|------|------|
| 大陆企业邮（默认） | `imap.qiye.aliyun.com:993` |
| 香港 | `imaphk.qiye.aliyun.com:993` |
| 万网旧域 | `imap.mxhichina.com:993` |

## Git 仓库边界

| 提交到 Git | 不提交 |
|------------|--------|
| `SKILL.md`、`scripts/`、`credentials.env.example` | `local/credentials.env` |
| `local/credentials.env.example`、`local/.gitkeep` | `.aliyun-mail.env` |
| `references/onboarding-flow.md` | 任何含真实密码的文件 |

他人 clone 后：**代码共享，凭据每人本地配置一次**（由 Agent 引导）。

## 安全与合规

- 使用只读选文件夹 + `BODY.PEEK`，避免误标已读
- 附件默认只返回元数据
- 管理员需开启「允许第三方客户端」

## References

- `references/openclaw-hermes-registration.md`：**OpenClaw / Hermes 注册配置（复制即用）**
- `references/onboarding-flow.md`：Agent 对话引导主协议
- `references/agent-setup.md`：多 Agent 环境变量与平台差异
- `references/imap-setup.md`：IMAP 服务器与管理员开关
- `agents/openclaw.yaml`、`agents/hermes.yaml`：平台配置片段源文件
- `bundles/mail-assistant.hermes.yaml`：Hermes `/mail-assistant` bundle

## 常见错误

| 现象 | 处理 |
|------|------|
| 用户要读信但未配置 | 跑 `setup status`，进入对话引导，不要直接失败 |
| `LOGIN failed` | 引导换客户端授权密码；确认三方客户端已开 |
| clone 后别人用不了 | 正常：每人需 `setup apply` 配自己的凭据 |

## 后续扩展（未实现）

- SMTP 发信、附件落盘、标记已读/移动/删除
