# 源周报 · 邮件与 xlsx

> 发件人/主题均**可配置**(见 `scripts/weekly_report_config.py`:`SENDER_EMAIL` / `SUBJECT_KEY`),下表为华智融默认值。

## 邮件

| 项 | 值（默认，可配置） |
|---|---|
| 发件人 | `${SENDER_EMAIL}` = evyn.chen@newpostech.com（陈徐伟） |
| 主题 | `${SUBJECT_KEY}（N）` = 总裁办及各部门经理周报（N） |
| 附件 | `${SUBJECT_KEY}（N）.xlsx` |
| 到达 | 通常 **周一下午**（17:00 前后） |

## IMAP 注意

- ❌ `email_tool.py search` 中文关键词 → UnicodeEncodeError
- ❌ 英文 SUBJECT SEARCH → BAD
- ✅ `SINCE` 日期 + 遍历 + Python 过滤 `evyn.chen` + 主题含 `总裁办及各部门经理周报`
- ✅ `check_unseen.py` 或内联 imaplib（终端，非 execute_code 沙箱）

## 附件

- 约 1.4MB，`fetch(RFC822)` 可能超时，注意 timeout
- 中文文件名：`email.header.decode_header(part.get_filename())`
- 嵌套结构：`multipart/mixed` → 递归 `walk()` 找 .xlsx

## xlsx sheet

**保留（按人名）**：蔡伟旭、杨晓东、赵国栋、王青虹、肖启新、林华新、…（24–27 人）

**跳过的 sheet**（历史档案，不属于当周汇报内容，不提取）：

- `周报汇总链接`
- `错误档案` — ⚠️ 这是公司历史错误记录库，不是当周工作汇报。里面的条目是跨年份累积的旧事件（包括比利时9220U发错型号等），与本周实际工作无关。**必须完全跳过，不得提取其中任何内容到周报PDF中。**
- `Sheet1`

## 去重

按 **周数 NN** 匹配归档目录是否已有 `周报_WNN_*_手机长条_完整版.pdf`，不依赖 SEEN。
