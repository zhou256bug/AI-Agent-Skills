# 收件箱值守 inbox-watch

通用 IMAP 收件箱 cron 扫描 — 工作日每 3 小时查 UNSEEN、关注人分级、归档、推送微信。

**版本**：0.1.0 | **slash**：`/inbox-watch`

## 能力

- 通用 IMAP（默认阿里企业邮 `imap.qiye.aliyun.com`）
- `check_unseen.py` 全量 UNSEEN（最多 50 封）
- 系统邮件过滤 + 关注人标注
- `mail_tool.py` 读信/匹配/附件
- 无未读仍汇报「没有新邮件」
- 归档 `output/scans/` + 微信 bridge 推送

## 快速开始

```bash
cp local/credentials.env.example local/credentials.env   # 填 IMAP + WEIXIN_TO
python3 scripts/inbox_watch_cli.py setup apply --verify
python3 scripts/check_unseen.py
python3 scripts/run_scan.py --deliver --dry-run
python3 scripts/run_acceptance.py
```

### Hermes cron

见 `references/cron-setup.md`。

```bash
hermes chat --toolsets terminal,skills -q "/inbox-watch 扫描未读邮件"
```

## 设计原则

- 单 Agent 闭环，无委派
- 七大宪法原则对齐（见仓库 `docs/SKILL-DESIGN-STANDARDS.md`）
- 纯标准库脚本；IMAP 需网络时由 terminal 执行
