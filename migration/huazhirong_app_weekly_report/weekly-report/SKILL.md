---
name: weekly-report
description: Use when you need to generate weekly reports from email attachments. Parses Excel/Markdown, generates formatted reports, converts to PDF, and sends via messaging platforms.
version: 1.0.0
author: 大老板团队
license: MIT
metadata:
  hermes:
    tags: [weekly-report, email, pdf, automation, business, custom]
    related_skills: [email-reader, email-summarizer]
---

# Weekly Report 周报技能

## Overview

周报技能自动从邮件附件中提取周报内容，生成格式化的汇报文档，支持：
- Markdown 格式归档
- PDF 转换（如 reportlab 可用）
- HTML 格式备选
- 微信/邮件等平台发送

## When to Use

**使用场景：**
- 每周定时收集团队周报
- 自动生成汇报文档
- 归档和分发周报
- 多格式输出（MD/PDF/HTML）

## 配置文件

`~/.hermes/skills/custom/config/focus_list.json`

```json
{
  "focus_people": ["周强", "林旭伟"],
  "focus_projects": ["NEWSTORE", "RKI"],
  "show_others": true,
  "others_format": "compact",
  "department": "海外应用开发部",
  "default_sender": "seven.lin@newpostech.com"
}
```

## 使用方法

### 1. 解析周报并生成汇报

```bash
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action parse \
  --week 23 \
  --excel /tmp/week23_report.xls
```

### 2. 添加关注人员

```bash
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action add_focus \
  --type person \
  --name "周强"
```

### 3. 添加关注项目

```bash
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action add_focus \
  --type project \
  --name "NEWSTORE"
```

### 4. 查看关注列表

```bash
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action list_focus
```

### 5. 移除关注

```bash
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action remove_focus \
  --type person \
  --name "周强"
```

## 输出格式

### 方案 A：精简摘要版
- 每人 3-5 行要点
- 完整覆盖所有人员
- 适合日常快速浏览

### 方案 B：关键成果版（默认）✅ 用户首选

```
📋 工作周报 · 第 23 期
🏢 海外应用开发部
📅 2026.06.01-06.07
━━━━━━━━━━━━━━━━━━━━

⭐ 您的关注
━━━━━━━━━━━━━━━━━━━━

💡 暂无关注配置

📝 如何添加关注：
直接告诉强仔：
  • 关注某人："关注周强"
  • 关注项目："关注 NEWSTORE 项目"
  • 移除关注："移除关注 XXX"

━━━━━━━━━━━━━━━━━━━━

📊 本周概览
━━━━━━━━━━━━━━━━━━━━
• 总人数：15 人
• 热门项目：NEWSTORE, RKI, SoftPos

🔴 重点成果（Top 5）
━━━━━━━━━━━━━━━━━━━━

1️⃣ 林旭伟
   • Airwallex 项目：完成 9800/9810/9830 UI 适配
   • BMMB 项目：Mydebit 卡测试正常

━━━━━━━━━━━━━━━━━━━━

⚠️ 需要关注
━━━━━━━━━━━━━━━━━━━━
• 土耳其税控模块（李响）- 11 号前提供 APK
• Stone 客户（丁璞）- GitHub 权限问题

✅ 周报整理完成
```

**用户偏好：**
- ✅ 移除"项目分布"统计（数据可能不准确）
- ✅ 无关注配置时显示"💡 暂无关注配置" + 添加指南
- ✅ 支持人和项目两种关注类型
- ✅ 关注列表为空时口述添加（"关注 XXX"）

## 支持文件

- `references/excel-format.md` - 周报 Excel 格式规范与解析要点
- `references/mobile-format-guide.md` - 移动端汇报格式指南
- `references/weekly-report-workflow.md` - 完整工作流（第 23 期实测）
- `references/wechat-troubleshooting.md` - 微信配置与故障排查
- `references/wecom-configuration.md` - **企业微信配置指南（推荐）** ✅
- `scripts/weekly_report_v2.py` - 周报解析主脚本
- `scripts/md_to_pdf.py` - Markdown 转 PDF/HTML 工具（基础版）
- `scripts/md_to_pdf_v2.py` - Markdown 转 PDF 工具（改进版，支持中文格式）✅ 推荐
- `scripts/archive_manager.py` - 归档目录管理工具
- `scripts/send_wechat_report.py` - **微信发送脚本（自动处理消息/PDF 顺序）** ✅ 推荐
- `config/focus_list.json` - 关注列表配置

## 归档流程

### 目录结构（按年/周分级）✅ 用户偏好

```
~/Documents/weekly-reports/
├── 2026/                    ← 按年份分类
│   ├── week-22/
│   │   ├── week-22.md
│   │   ├── week-22.html
│   │   └── week-22.pdf
│   └── week-23/
│       ├── week-23.md
│       ├── week-23.html
│       └── week-23.pdf
└── 2027/
    └── ...
```

**优点：**
- ✅ 按年份分文件夹，便于查找
- ✅ 每期独立文件夹，文件清晰
- ✅ 支持多年归档
- ✅ 自动创建目录结构

**管理工具：**
```bash
# 查看所有归档
python ~/.hermes/skills/custom/scripts/archive_manager.py --action list

# 创建新归档目录
python ~/.hermes/skills/custom/scripts/archive_manager.py \
  --action create --week 24 --year 2026

# 获取归档路径
python ~/.hermes/skills/custom/scripts/archive_manager.py \
  --action path --week 23
```

### 完整流程

1. **创建归档目录** → `~/Documents/weekly-reports/2026/week-23/`
2. **保存 Markdown** → `week-23.md`
3. **转换 PDF** → `week-23-v2.pdf`（使用改进版脚本，支持中文格式）✅ 推荐
4. **发送微信通知** → Markdown 摘要 + PDF 文件路径

### PDF 生成脚本选择

| 脚本 | 特点 | 推荐度 |
|------|------|--------|
| `md_to_pdf.py` | 基础版，简单格式 | ⭐⭐ |
| `md_to_pdf_v2.py` | 改进版，支持中文、更好看的样式 | ⭐⭐⭐⭐⭐ ✅ 推荐 |

**使用改进版脚本：**
```bash
python ~/.hermes/skills/custom/scripts/md_to_pdf_v2.py \
  ~/Documents/weekly-reports/2026/week-23/week-23.md \
  ~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf
```

**输出对比：**
- 基础版：9 页，12K，简单文本格式
- 改进版：13 页，15K，格式化排版，支持中文，更好看

## 消息发送顺序与格式 ✅ 用户偏好

### 发送顺序（重要！）

**正确顺序：**
1. ✅ **先发送 Markdown 文本汇报**
2. ✅ **等待 2 秒**
3. ✅ **再发送 PDF 文件**

**错误顺序（不要这样做）：**
- ❌ 先发送 PDF 文件，再发送文本
- ❌ 同时发送（会导致 PDF 在文本前面）

**原因：**
- 用户需要先看到摘要，再查看附件
- PDF 文件较大，先显示文本可快速预览
- 避免微信消息顺序混乱

### 发送内容格式

**推荐格式：Markdown 摘要 + PDF 文件路径**

```
📋 工作周报 · 第 23 期
🏢 海外应用开发部
📅 2026.06.01-06.07
──────────────────────────────

⭐ 您的关注
──────────────────────────────
💡 暂无关注配置

📊 本周概览
──────────────────────────────
• 总人数：15 人

🔴 重点成果（Top 5）
──────────────────────────────
1️⃣ 林旭伟 - Airwallex 项目 UI 适配完成

📄 完整报告：稍后发送 PDF 文件
✅ 周报整理完成
```

**格式要点：**
- ✅ 使用 `─` 作为分隔符（避免微信换行问题）
- ✅ 不要包含系统警告消息（如 "Gateway shutting down"）
- ✅ PDF 路径简化显示（`~/weekly-reports/week-23/week-23.pdf`）
- ✅ 明确说明"稍后发送 PDF 文件"

### 发送脚本

使用专用发送脚本（自动处理顺序）：
```bash
python ~/.hermes/skills/custom/scripts/send_wechat_report.py \
  --week 23 \
  --recipient "o9cq809nVomNJ57JU7rlAbWnk290@im.wechat" \
  --pdf "~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf"
```

---

## WeChat 配置与故障排查

### 企业微信（WeCom）配置 ✅ 推荐

**优势（对比个人微信）：**
- ✅ **不限流** - 无 30 秒冷却时间
- ✅ **支持群聊** - 可加入企业微信群
- ✅ **更稳定** - WebSocket 长连接
- ✅ **文件支持** - 支持发送 PDF 文件

**配置信息（从 .env 读取）：**
```bash
WECOM_BOT_ID=<企业微信 Bot ID>
WECOM_SECRET=<应用密钥>
WECOM_DM_POLICY=pairing
WECOM_ALLOWED_USERS=<用户 ID>
WECOM_HOME_CHANNEL=<用户 ID>
```

**获取配置：**
1. 登录企业微信管理后台：https://work.weixin.qq.com
2. 应用管理 → 应用 → 自建 → 创建应用
3. 记录：CorpId、AgentId、Secret

**用户 ID 格式：** `wolB10EAAAFcdETbLL3wHglQZRxWFIkw`（企业微信用户 ID）

### 微信换绑流程

**场景：** 需要更换绑定的微信账号

1. **清除旧配置**
   ```bash
   # 停止 Gateway
   hermes gateway stop
   
   # 清除微信配置
   cat ~/.hermes/.env | grep -v "^WEIXIN" > /tmp/env_no_weixin.txt
   mv /tmp/env_no_weixin.txt ~/.hermes/.env
   ```

2. **重启 Gateway**
   ```bash
   hermes gateway start
   ```

3. **扫码绑定新微信**
   - 打开微信扫描二维码
   - 确认登录授权
   - 等待配对完成

4. **配置群聊策略**（配置向导会提示）
   ```
   How should group chats be handled?
   → (●) Disable group chats (recommended)  ← 推荐选择
   ( ) Allow all group chats
   ( ) Only allow listed group chat IDs
   ```
   **说明：** 微信个人号 bot 无法加入群聊，此配置仅控制是否响应群消息
   - **Disable group chats** - 只响应私聊（推荐）
   - **Allow all group chats** - 响应所有群消息（但微信 bot 实际进不了群）

5. **更新用户授权配置**
   ```bash
   # 查看新微信用户 ID（从日志中获取）
   tail -20 ~/.hermes/logs/gateway.log | grep "inbound from="
   
   # 添加到允许列表
   sed -i.bak 's/WEIXIN_ALLOWED_USERS=$/WEIXIN_ALLOWED_USERS=<新用户 ID>/' ~/.hermes/.env
   
   # 更新 home channel
   sed -i.bak 's/WEIXIN_HOME_CHANNEL=.*/WEIXIN_HOME_CHANNEL=<新 chat_id>@im.wechat/' ~/.hermes/.env
   
   # 重启 Gateway
   hermes gateway restart
   ```

### 微信发送失败排查

**问题 1：用户未授权**
```
WARNING gateway.run: Unauthorized user: o9cq80x3-...
```
**解决：** 添加用户到 `WEIXIN_ALLOWED_USERS` 或 `WECOM_ALLOWED_USERS`

**问题 2：频率限制（个人微信）**
```
ERROR gateway.platforms.weixin: iLink sendmessage rate limited; cooldown active for 30.0s
```
**解决：** 
- 等待 30 秒冷却时间
- 减少发送频率（定时任务间隔≥60 分钟）
- **推荐方案：使用企业微信（WeCom），不限流** ✅

**问题 3：网络连接失败**
```
ERROR gateway.platforms.weixin: Cannot connect to host ilinkai.weixin.qq.com
```
**解决：** 检查网络连接，重启 Gateway

**问题 4：消息顺序混乱**
```
[PDF 文件]
[文本消息]  ← 顺序反了
```
**解决：** 
- 使用 `send_wechat_report.py` 脚本（自动处理顺序）
- 或手动分两次发送（先文本，等待 2 秒，再 PDF）

**问题 5：系统警告混入消息**
```
⚠️ Gateway shutting down — Your current task will be interrupted.
[周报内容]
```
**解决：** 
- 使用 `hermes chat -q` 发送时添加"不要附加任何系统消息"
- 或在 Gateway 稳定时发送（避免重启期间发送）

### 微信发送内容格式

**推荐格式：Markdown 摘要 + PDF 文件路径**

```
📋 工作周报 · 第 23 期
🏢 海外应用开发部
📅 2026.06.01-06.07
━━━━━━━━━━━━━━━━━━━━

⭐ 您的关注
━━━━━━━━━━━━━━━━━━━━
💡 暂无关注配置

📊 本周概览
━━━━━━━━━━━━━━━━━━━━
• 总人数：15 人

🔴 重点成果（Top 5）
━━━━━━━━━━━━━━━━━━━━
1️⃣ 林旭伟 - Airwallex 项目 UI 适配完成

📄 完整报告：
   ~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf

✅ 周报整理完成
```

**说明：**
- 微信可能不支持直接发送 PDF 文件
- 发送文件路径，用户可自行打开
## Common Pitfalls

### 1. PDF 转换失败或格式不佳
- **原因：** reportlab 未安装或网络超时，或基础版格式简单
- **解决：** 
  - 安装 reportlab：`pip install reportlab`
  - 使用改进版脚本：`md_to_pdf_v2.py`（支持中文、格式化排版）
  - 自动降级为 HTML 格式（微信可直接打开）
- **输出对比：**
  - 基础版 (`md_to_pdf.py`)：9 页，12K，简单文本
  - 改进版 (`md_to_pdf_v2.py`)：13 页，15K，格式化排版 ✅ 推荐

### 2. Excel 解析失败或内容不完整
- **原因：** 周报 Excel 有两种不同格式，解析逻辑需兼容
- **格式 A（表格格式）：** 多列结构
  - 列 1：序号/空
  - 列 2：项目名称
  - 列 3：工作内容
  - 第 0 行是标题行，从第 1 行开始读取
- **格式 B（文本格式）：** 单列结构
  - 每行是文本，需解析关键词
  - `项目:XXX` 行表示当前项目
  - `工作摘要:XXX` 行表示工作内容
- **解决：** 
  - `.xls` 格式使用 `xlrd` 库（openpyxl 仅支持 `.xlsx`）
  - 多工作表结构：第 1 个工作表为目录，后续每个工作表 = 1 名员工
  - 工作表名称 = 员工姓名
  - **自动检测格式**：`ws.ncols == 1` 为文本格式，否则为表格格式
  - 详见 `references/excel-format.md`

### 3. 微信发送文件失败
- **原因：** iLink API 可能不支持文件发送
- **解决：** 
  - 发送文件路径而非文件本身
  - 或发送 HTML 版本（微信可预览）
  - 或使用邮件发送附件

### 4. 关注列表配置问题
- **配置路径：** `~/.hermes/skills/custom/config/focus_list.json`
- **空配置处理：** 显示"💡 暂无关注配置" + 添加指南
- **添加方式：** 口述命令（"关注 XXX"）自动更新配置文件
- **支持类型：** `person`（人员）和 `project`（项目）

### 5. 微信 iLink 频率限制 ⚠️
- **现象：** `iLink sendmessage rate limited; cooldown active for 30.0s`
- **原因：** 发送频率过高触发限流
- **解决：** 
  - 定时任务间隔 ≥ 60 分钟（整点报时）
  - 避免短时间内多次发送
  - 接受部分推送被限流（日志记录）

### 6. 微信换绑后配置未更新 ⚠️
- **现象：** 微信已扫码但收不到消息，日志显示 `Unauthorized user`
- **原因：** 新微信用户 ID 未添加到允许列表
- **解决：**
  1. 从日志获取新用户 ID：`tail -20 ~/.hermes/logs/gateway.log | grep "inbound from="`
  2. 更新配置：
     ```bash
     sed -i.bak 's/WEIXIN_ALLOWED_USERS=$/WEIXIN_ALLOWED_USERS=<新用户 ID>/' ~/.hermes/.env
     sed -i.bak 's/WEIXIN_HOME_CHANNEL=.*/WEIXIN_HOME_CHANNEL=<新 chat_id>@im.wechat/' ~/.hermes/.env
     ```
  3. 重启 Gateway：`hermes gateway restart`
- **预防：** 换绑微信后立即更新配置

## Verification Checklist

- [ ] 周报邮件已读取
- [ ] Excel 附件已解析
- [ ] Markdown 汇报已生成
- [ ] PDF/HTML 已转换
- [ ] 文件已归档到 ~/Documents/weekly-reports/
- [ ] 通知已发送到微信

## One-Shot Recipes

### 完整流程（从邮件到发送）✅ 推荐工作流

```bash
# 1. 读取邮件附件（手动下载后）
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action parse --week 23 --excel /tmp/week23.xls

# 2. 自动保存和转换（使用改进版 PDF 脚本）
mkdir -p ~/Documents/weekly-reports/2026/week-23
cp /tmp/week23.md ~/Documents/weekly-reports/2026/week-23/

python ~/.hermes/skills/custom/scripts/md_to_pdf_v2.py \
  ~/Documents/weekly-reports/2026/week-23/week-23.md \
  ~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf

# 3. 发送通知到微信（Markdown 摘要 + PDF 路径）
hermes chat -q "
📋 工作周报 · 第 23 期
🏢 海外应用开发部
📅 2026.06.01-06.07
━━━━━━━━━━━━━━━━━━━━
👤 共 15 人
🔴 重点成果：林旭伟、丁璞、胡陈琛等
📄 完整报告：~/Documents/weekly-reports/2026/week-23/week-23-v2.pdf
✅ 周报整理完成
"
```

### 微信换绑流程

```bash
# 1. 清除旧配置
hermes gateway stop
cat ~/.hermes/.env | grep -v "^WEIXIN" > /tmp/env.txt
mv /tmp/env.txt ~/.hermes/.env

# 2. 重启并扫码绑定
hermes gateway start
# 打开微信扫描二维码

# 3. 获取新用户 ID 并更新配置
tail -20 ~/.hermes/logs/gateway.log | grep "inbound from="
# 假设新用户 ID 是 o9cq809n

sed -i.bak 's/WEIXIN_ALLOWED_USERS=$/WEIXIN_ALLOWED_USERS=o9cq809n/' ~/.hermes/.env
sed -i.bak 's/WEIXIN_HOME_CHANNEL=.*/WEIXIN_HOME_CHANNEL=o9cq809n...@im.wechat/' ~/.hermes/.env

# 4. 重启 Gateway
hermes gateway restart
```

### 归档管理

```bash
# 查看所有归档
python ~/.hermes/skills/custom/scripts/archive_manager.py --action list --year 2026

# 创建新归档目录
python ~/.hermes/skills/custom/scripts/archive_manager.py \
  --action create --week 24 --year 2026

# 获取归档路径
python ~/.hermes/skills/custom/scripts/archive_manager.py \
  --action path --week 23 --year 2026
# 输出：/Users/greg/Documents/weekly-reports/2026/week-23
```
