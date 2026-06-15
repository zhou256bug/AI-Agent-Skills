# IMAP 已知陷阱（阿里企业邮等）

## 禁止

- ❌ 多条件 `SEARCH`（如 `UNSEEN SUBJECT "中文"`）— 阿里企业邮 **BAD**
- ❌ `email_tool.py search` 带中文关键词 — 可能 `UnicodeEncodeError`
- ❌ 在 `execute_code` 沙箱内跑 imaplib — 网络受限

## 推荐

- ✅ 仅 `UNSEEN` 或 `ALL` 或单条件 `SINCE`
- ✅ 取回后在 **Python 侧** 过滤发件人/主题
- ✅ 用 **terminal** 跑 `check_unseen.py` / `mail_tool.py`
- ✅ 按 UID `read` / `attachments_match`

## 关注人处理（默认 data/watchlist.json）

| 策略 | 含义 |
|------|------|
| `read_full` | Agent 用 `mail_tool.py read --uid` 读全文 |
| `read_attachments` | `attachments_match` 下载到 `output/attachments/` |
| `report_promptly` | 摘要中标注，由 Agent 判断是否读全文 |

## 与周报技能

本技能 **不委派** `huazhirong-management-weekly-report`。  
陈徐伟周报 xlsx 处理由用户另行触发 `/weekly-report` 或手动跑周报脚本。
