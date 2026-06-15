---
name: huazhirong-inbox-watch
version: 0.1.0
description: 通用 IMAP 收件箱值守——工作日每3小时 cron 扫描 UNSEEN 未读、关注人分级处理、归档 output/scans/、推送微信。阿里企业邮开箱默认。单 Agent 闭环，setup 引导配置。Use when 未读邮件、收件箱扫描、inbox watch、mail cron、IMAP、微信推送、openclaw、hermes、setup。
metadata: {"openclaw":{"requires":{"bins":["python3"]},"skillKey":"huazhirong-inbox-watch","emoji":"📬"},"hermes":{"tags":["email","imap","cron","inbox","weixin"],"category":"productivity","requires_toolsets":["terminal"]}}
user-invocable: true
license: Apache-2.0
---

# 收件箱值守 inbox-watch v0.1.0

> **单 Agent 闭环**：terminal 扫未读 → 关注人处理 → emoji 摘要 → 归档 → 微信推送  
> **slash**：`/inbox-watch`

---

## 零、开箱即用

```bash
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py setup status
python3 huazhirong-inbox-watch/scripts/run_acceptance.py
```

- 注册：`references/openclaw-hermes-registration.md`
- 引导：`references/onboarding-flow.md`
- Cron：`references/cron-setup.md` + `references/agent-cron-prompt.md`
- bundle：`bundles/inbox-watch.hermes.yaml`

---

## 一、铁律

1. **单 Agent** — 禁止 `delegate_task`、禁止加载其他 skill
2. **只读 IMAP** — 禁止发信/删信/改已读
3. **无未读不可静默** — 必须回复「**没有新邮件**」并仍可 `--deliver`
4. **IMAP 搜索** — 仅用 `UNSEEN`/`ALL`/`SINCE`；过滤在 Python 侧（见 `references/imap-traps.md`）
5. **terminal 执行脚本** — 禁止在 execute_code 沙箱跑 imaplib
6. **Emoji 输出** — `references/emoji-output-guide.md`

---

## 二、场景路由

| 模式 | 触发 | 动作 |
|------|------|------|
| **C** | cron、每3小时、扫描未读 | `check_unseen.py` → 关注人策略 → `run_scan.py --deliver` |
| **M** | 手动查信、/inbox-watch | 同上或 `mail_tool.py list` |
| **R** | 读全文、读 UID | `mail_tool.py read --uid` |
| **A** | 下载附件 | `mail_tool.py attachments_match` |
| **S** | 配置邮箱、setup | `inbox_watch_cli.py setup` |

---

## 三、核心脚本

| 脚本 | 用途 |
|------|------|
| `check_unseen.py` | UNSEEN 扫描，输出 `TOTAL_UNSEEN` / `---EMAIL---` |
| `mail_tool.py` | `list` / `read` / `read_match` / `attachments_match` / `unseen` |
| `run_scan.py` | 生成 emoji Markdown → `output/scans/` → 可选 `--deliver` |
| `inbox_watch_cli.py` | `setup` / `doctor` / `scan` |
| `deliver_weixin.py` | 微信 bridge 推送 |

```bash
# 扫描（Agent cron 第一步）
python3 scripts/check_unseen.py

# 归档 + 推送
python3 scripts/run_scan.py --deliver

# 读关注人全文
python3 scripts/mail_tool.py read --uid 12345
```

---

## 四、配置（`scripts/inbox_watch_config.py`）

| 变量 | 默认 | 含义 |
|------|------|------|
| `INBOX_WATCH_OWNER` | 老板 | 汇报对象 |
| `INBOX_WATCH_IMAP_HOST` | imap.qiye.aliyun.com | 通用 IMAP 主机 |
| `INBOX_WATCH_IMAP_USER` | — | 邮箱（必填） |
| `INBOX_WATCH_IMAP_PASSWORD` | — | 授权码（必填） |
| `INBOX_WATCH_ARCHIVE_DIR` | `<skill>/output` | 归档根目录 |
| `WEIXIN_TO` | — | 微信推送对象 |

关注人：`data/watchlist.json`（可编辑）  
系统发件人过滤：`data/system-sender-patterns.json`

---

## 五、Cron（Hermes）

| 项 | 值 |
|----|-----|
| 调度 | `0 7-22/3 * * 1-5`（工作日 6 次/天） |
| toolsets | `terminal`（+ `skills` 加载本 skill） |
| Prompt | `references/agent-cron-prompt.md` |

---

## 六、关注人处理（默认）

| 联系人 | 策略 |
|--------|------|
| Fernando Alonso | `read_full` |
| Fernando Geraldeli | `read_full` |
| Linda（尼尔森） | `read_attachments` |
| Victor | `report_promptly` |

---

## 七、输出格式（check_unseen）

```
TOTAL_UNSEEN:3
PERSONAL_UNSEEN:1
---EMAIL---
UID:123
SENDER:Name <a@b.com>
SENDER_RAW:a@b.com
DATE:2026-06-15 10:00
SUBJECT:Subject
IS_SYSTEM:False
IS_KNOWN:True
WATCH_ACTION:read_full
WATCH_NAME:Fernando Alonso
ATTACHMENTS:file.xlsx
BODY_PREVIEW:...
```

---

## 八、与周报技能

本技能 **不自动委派** 周报处理。陈徐伟 xlsx 周报请用户另行 `/weekly-report`。

---

## 九、文件结构

```
huazhirong-inbox-watch/
├── SKILL.md
├── data/watchlist.json
├── data/system-sender-patterns.json
├── references/（cron、imap、emoji、onboarding）
├── scripts/（check_unseen、mail_tool、run_scan、cli）
├── agents/ / bundles/
└── output/scans/（gitignore）
```
