---
name: huazhirong-management-weekly-report
version: 1.0.0
description: 管理团队周报汇编——独立完整技能：从收件箱取信(xlsx)→汇编四段 Markdown→渲染老板手机长条 PDF→多通道投递，一条命令编排且失败可断点续跑。可配置发件人/老板/归档/通道。OpenClaw/Hermes clone 后开箱即用(脚本纯标准库；PDF 为可选依赖)。Use when 管理团队周报、各部门经理周报、周报总结、周报 PDF、weekly report、openclaw、hermes。
metadata: {"openclaw":{"requires":{"bins":["python3"]},"skillKey":"huazhirong-management-weekly-report","emoji":"🗂️"},"hermes":{"tags":["weekly-report","email","xlsx","pdf","management"],"category":"productivity","requires_toolsets":["terminal"]}}
user-invocable: true
license: Apache-2.0
---

# 管理团队周报汇编（独立完整技能）

把 **{发件人}** 发来的「各部门经理周报」邮件(含 xlsx 附件),汇编为 **{老板}** 手机可读的 **四段长条 PDF**,并归档/投递。**取信内置为必备能力**,不依赖其它技能。

> 默认面向华智融实例,所有"特定人/公司/路径/凭据"均**可配置**(见「零、配置」),clone 后填邮箱凭据即可跑。脚本为**纯标准库**;手机 PDF 为**可选依赖**。

## 零、配置与凭据

业务/路径配置集中在 `scripts/weekly_report_config.py`(环境变量覆盖);**凭据**写 `local/credentials.env`(由 `credentials.env.example` 复制,**已 gitignore**)。

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| OWNER | `WEEKLY_REPORT_OWNER` | 老板 | PDF 收件人;段标题「需{OWNER}关注的事项」与禁止段 |
| SENDER_NAME | `WEEKLY_REPORT_SENDER_NAME` | 陈徐伟 | 源邮件发件人姓名(meta「来源」) |
| SENDER_EMAIL | `WEEKLY_REPORT_SENDER_EMAIL` | evyn.chen@newpostech.com | 需查询的源邮件发件人邮箱 |
| SUBJECT_KEY | `WEEKLY_REPORT_SUBJECT_KEY` | 总裁办及各部门经理周报 | 主题关键词(IMAP 过滤 + 期号解析) |
| COMPANY | `WEEKLY_REPORT_COMPANY` | 华智融 | 公司名 |
| ARCHIVE_DIR | `WEEKLY_REPORT_ARCHIVE_DIR` | `<skill>/output` | MD/PDF/xlsx/状态 归档根目录 |
| **取信 IMAP** | `WEEKLY_REPORT_IMAP_HOST/PORT/USER/PASSWORD` | — | **必备**:接收周报的收件箱(任意 IMAP) |
| 微信 bridge | `WEIXIN_BRIDGE_URL` / `WEIXIN_TO` | `http://localhost:9100` / — | hermes-weixin 投递 |

```bash
cp credentials.env.example local/credentials.env   # 填 IMAP + WEIXIN_TO
python3 scripts/weekly_report_config.py             # 打印当前生效配置（密码脱敏）
```

## 一、开箱即用与注册(OpenClaw / Hermes)

- 平台注册(复制即用):`references/openclaw-hermes-registration.md`;配置源 `agents/*.yaml`;bundle `bundles/weekly-report.hermes.yaml`
- 自检:`python3 scripts/run_acceptance.py`(纯标准库,绿即可用;render 用例缺依赖时自动 SKIP)

## 二、一条命令编排（推荐）+ 断点续跑

```bash
python3 scripts/run_weekly.py            # 自动识别最新期号，跑全程
python3 scripts/run_weekly.py --period 23            # 指定期号
python3 scripts/run_weekly.py --force-stage deliver  # 仅补推送（如微信限流后）
```

编排器按 **fetch → compose → render → deliver** 四阶段推进,**已完成阶段(产物在)自动跳过,失败即停,下次触发续跑**(状态 `<ARCHIVE_DIR>/.state/W{N}.json`)。终态打印 `STATE:<X>`:

| STATE | 含义 | 退出码 | 下次触发 |
|-------|------|--------|----------|
| `DELIVERED` / `ALREADY_DONE` | 完成 / 已交付幂等 | 0 | — |
| `NEED_COMPOSE` | 已取信,**需 Agent 据 xlsx 写四段 Markdown**(见 §三) | 3 | Agent 写完 MD 后重跑 |
| `FETCH_WAIT` | 邮件未到/无 xlsx | 3 | 静默,下一轮再试 |
| `DELIVER_RETRY` | 已出 PDF,推送失败(限流等) | 3 | 仅补推送 |
| `FAIL_NOTIFY` | 硬错误(凭据错/取信连接异常/渲染失败) | 2 | 通知一次 |

> 续跑示例:某次"取信成功但推送被限流"→ 下次触发自动跳过取信+处理,**只补推送**;"取信成功但还没写 MD"→ 返回 `NEED_COMPOSE`,Agent 写完 MD 再触发即从渲染继续。

## 三、各阶段说明

1. **fetch(自动)** — `scripts/fetch_mail.py`:IMAP `SINCE` 回溯 + Python 过滤(发件人含 `SENDER_EMAIL`、主题含 `SUBJECT_KEY`),递归找 `.xlsx` 下载到 `<ARCHIVE_DIR>/input/W{N}.xlsx`。期号 N 取自主题括号(**禁止 ISO 周**)。
2. **compose(Agent 任务)** — 据 xlsx 写四段 Markdown 存为 `<ARCHIVE_DIR>/W{N}-YYYY年MM月DD日.md`(格式见 `references/content-format.md`):
   1. 重点项目进展(每项目 `> 周报来源：**姓名**`;状态 emoji ⏳✅🆕⚠️🔵🟡🔴)
   2. 海外市场要闻({老板}行程/来访并入此处,**不单设第一节**)
   3. 业务线重点关注
   4. 需{老板}关注的事项
   - 解析 xlsx 时**跳过** `周报汇总链接`、`错误档案`(历史错误库)、`Sheet1`。
   - 旧版「五段」可用 `scripts/transform_report_md.py in.md out.md 23 2026-06-08` 转四段。
3. **render(自动,可选依赖)** — 校验 MD 后 `scripts/render_mobile_pdf.py --preset weekly-report` 出手机长条 PDF。需 `weasyprint`+`ghostscript`+`PyMuPDF`+Noto Sans SC;未装则止于 Markdown。
4. **deliver(自动)** — `scripts/deliver.py`,默认 `wechat-bridge`(直连 hermes-weixin `POST /send`,**读 200/500 真实回执**,限流=可重试失败);另支持 `wechat-media`/`wecom`/`feishu`(见 `references/delivery-channels.md`)。

## 四、命名与归档

```
<ARCHIVE_DIR>/
├── input/W{N}.xlsx              # 取信下载
├── W{N}-YYYY年MM月DD日.md / .pdf  # 汇编产物
└── .state/W{N}.json            # 断点续跑状态
```

## 五、禁止

- ISO 日历周编号、旧文件名 `周报_W24_…_完整版`
- 单独「{老板}本周重点」段(校验器会拦截)

## 六、定时(可选运维层)

调度是平台自己的事(Hermes jobs / 系统 cron):**只需按节奏反复调 `run_weekly.py`**,幂等与续跑由技能内部保证。参考节奏(周一 17:10–20:10 四轮 + 推送限流延迟重试)见 `references/cron-retry.md`。

## 七、文件索引

| 路径 | 用途 |
|------|------|
| `scripts/run_weekly.py` | **编排器**:fetch→compose→render→deliver + 断点续跑 |
| `scripts/fetch_mail.py` | 取信(必备,通用 IMAP) |
| `scripts/state.py` | 期号状态 + 产物探测 |
| `scripts/weekly_report_config.py` | 配置 + 凭据加载(环境变量覆盖) |
| `scripts/weekly_report_paths.py` | 命名 `W{N}-日期` 与归档路径 |
| `scripts/validate_weekly_report_md.py` | 四段结构/署名/禁止段校验 |
| `scripts/transform_report_md.py` | 旧五段 → 四段转换 |
| `scripts/render_mobile_pdf.py` | 手机长条 PDF(vendored,可选依赖) |
| `scripts/deliver.py` | 多通道投递(wechat-bridge/wechat-media/wecom/feishu) |
| `scripts/run_acceptance.py` | 独立验收套件(纯标准库,含续跑场景) |
| `credentials.env.example` / `local/` | 凭据模板 / 本地凭据(gitignore) |
| `references/` | 邮件/格式/通道/可选 cron/注册文档 |
