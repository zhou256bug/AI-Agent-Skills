# Changelog

All notable changes to the `aliyun-enterprise-mail` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- 修正注册文档与 `agents/*.yaml` 中的仓库名：`AI-Skills` → `AI-Agent-Skills`（与实际仓库 `zhou256bug/AI-Agent-Skills` 一致）

### Added

- 初始 skill：`SKILL.md` 工作流与 `references/imap-setup.md` 配置说明
- IMAP 读信 CLI：`scripts/read_mail.py`（`folders` / `list` / `read` / `search`）
- 共享库 `scripts/mail_lib.py`（标准库 `imaplib` + `email`，无第三方依赖）
- Cursor agent 入口 `agents/openai.yaml`
- 多 Agent 凭据加载：`bootstrap_env()`、默认 `~/.config/aliyun-enterprise-mail/credentials.env`
- `doctor` 子命令：检查凭据与 IMAP 连通性
- `credentials.env.example` 与 `references/agent-setup.md`（Cursor / Codex / OpenClaw / Hermes）
- 各子命令支持 `--env-file`
- Agent 引导式配置：`setup status` / `setup apply`（对话收集后写入凭据）
- `local/credentials.env` 作为 clone 后默认落盘路径（gitignore）
- `references/onboarding-flow.md`：OpenClaw/Hermes 对话式配置协议
- `references/openclaw-hermes-registration.md`：OpenClaw/Hermes 注册 snippet 与 bundle
- `agents/openclaw.yaml`、`agents/hermes.yaml`、`bundles/mail-assistant.hermes.yaml`
