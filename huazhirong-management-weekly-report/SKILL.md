---
name: huazhirong-management-weekly-report
version: 1.0.0
description: 管理团队周报汇编——把各部门经理周报邮件(含 xlsx 附件)汇编为老板手机可读的四段长条 PDF。四段结构、W{N}-日期命名、可配置发件人/归档/通道。OpenClaw/Hermes clone 后开箱即用(脚本纯标准库,PDF 为可选依赖)。Use when 管理团队周报、各部门经理周报、周报总结、周报 PDF、weekly report、openclaw、hermes。
metadata: {"openclaw":{"requires":{"bins":["python3"]},"skillKey":"huazhirong-management-weekly-report","emoji":"🗂️"},"hermes":{"tags":["weekly-report","email","xlsx","pdf","management"],"category":"productivity","requires_toolsets":["terminal"]}}
user-invocable: true
license: Apache-2.0
---

# 管理团队周报汇编

把 **{发件人}** 发来的「各部门经理周报」邮件(含 xlsx 附件),汇编为 **{老板}** 手机可读的 **四段长条 PDF**,并归档/投递。

> 默认面向华智融实例,但所有"特定人/公司/路径"均**可配置**(见下「零、配置」),clone 后可直接跑或替换为自己的值。脚本为**纯标准库**;手机 PDF 为**可选依赖**。

## 零、配置(可配置项,环境变量覆盖)

集中在 `scripts/weekly_report_config.py`,均可用环境变量覆盖:

| 配置 | 环境变量 | 默认 | 含义 |
|------|----------|------|------|
| OWNER | `WEEKLY_REPORT_OWNER` | 老板 | PDF 收件人(CEO/老板);用于段标题「需{OWNER}关注的事项」与禁止段 |
| SENDER_NAME | `WEEKLY_REPORT_SENDER_NAME` | 陈徐伟 | 源邮件发件人姓名(meta「来源」) |
| SENDER_EMAIL | `WEEKLY_REPORT_SENDER_EMAIL` | evyn.chen@newpostech.com | 需查询的源邮件发件人邮箱 |
| SUBJECT_KEY | `WEEKLY_REPORT_SUBJECT_KEY` | 总裁办及各部门经理周报 | 主题关键词(IMAP 过滤 + 期号解析) |
| COMPANY | `WEEKLY_REPORT_COMPANY` | 华智融 | 公司名 |
| ARCHIVE_DIR | `WEEKLY_REPORT_ARCHIVE_DIR` | `<skill>/output` | MD/PDF 归档根目录 |

```bash
python3 scripts/weekly_report_config.py   # 打印当前生效配置
```

## 一、开箱即用与注册(OpenClaw / Hermes)

- 平台注册(复制即用):见 `references/openclaw-hermes-registration.md`
- 配置源文件:`agents/{openclaw,hermes,openai}.yaml`;bundle:`bundles/weekly-report.hermes.yaml`
- 自检:`python3 scripts/run_acceptance.py`(纯标准库,绿即可用)

## 二、何时执行

| 触发 | 说明 |
|------|------|
| 人工 | {老板}说「做周报总结」「{SUBJECT_KEY} PDF」 |
| 定时(可选) | 周一下午邮件到达后运行;调度与门禁是**可选运维层**,见 `references/cron-retry.md`(平台相关,非核心) |

## 三、流程

### 1. 取邮件(IMAP)

见 `references/email-and-xlsx.md`。要点:`SINCE` 日期 + 遍历 + Python 过滤(发件人含 `SENDER_EMAIL`、主题含 `SUBJECT_KEY`),递归 `walk()` 找 `.xlsx`。

### 2. 解析 xlsx

保留各经理 sheet;**跳过** `周报汇总链接`、`错误档案`(历史错误库,与本周无关)、`Sheet1`。

### 3. 去重

归档目录已有 `W{N}-*.pdf`(N=邮件期号,取自主题括号,**禁止 ISO 周**)→ 静默跳过。
```bash
python3 -c "import sys;sys.path.insert(0,'scripts');import weekly_report_paths as p;print(p.pdf_exists_for_period(23))"
```

### 4. 写 Markdown(四段)

见 `references/content-format.md`:
1. **重点项目进展** — 每项目 `> 周报来源：**姓名**`;状态用 emoji(⏳✅🆕⚠️🔵🟡🔴)
2. **海外市场要闻** — {老板}行程/来访并入此处,**不单设第一节**
3. **业务线重点关注**
4. **需{老板}关注的事项**

> 若源数据是旧版「五段」(含单独的「{老板}本周重点」),用 `scripts/transform_report_md.py` 转成四段:
> `python3 scripts/transform_report_md.py in.md out.md 23 2026-06-08`

### 5. 校验

```bash
python3 scripts/validate_weekly_report_md.py output/W23-2026年06月08日.md
```

### 6. 渲染(可选依赖)

> 需 `weasyprint`、`ghostscript`、`PyMuPDF`(`fitz`)+ Noto Sans SC 字体。未装则交付 Markdown 即可。

```bash
python3 scripts/render_mobile_pdf.py --preset weekly-report \
  --title "{SUBJECT_KEY} · 第23期" \
  --body-md output/W23-2026年06月08日.md \
  --output output/W23-2026年06月08日.pdf
```

### 7. 投递(多通道,可选)

见 `references/delivery-channels.md` 与 `scripts/deliver.py`,支持 `wechat-media`(默认)/`wecom`(企业微信)/`feishu`(飞书),后续可扩展:

```bash
python3 scripts/deliver.py --channel wechat-media --file output/W23-2026年06月08日.pdf
```

## 四、命名与归档

```
<ARCHIVE_DIR>/
├── W{N}-YYYY年MM月DD日.md
└── W{N}-YYYY年MM月DD日.pdf
```

## 五、禁止

- ISO 日历周编号、旧文件名 `周报_W24_…_完整版`
- 单独「{老板}本周重点」段(校验器会拦截)
- (微信通道)投递缺 `MEDIA:` 行 → 微信收不到 PDF(见 delivery-channels.md)

## 六、文件索引

| 路径 | 用途 |
|------|------|
| `scripts/weekly_report_config.py` | 配置(发件人/老板/公司/归档,环境变量覆盖) |
| `scripts/weekly_report_paths.py` | 命名 `W{N}-日期` 与归档路径 |
| `scripts/validate_weekly_report_md.py` | 四段结构/署名/禁止段校验 |
| `scripts/transform_report_md.py` | 旧五段 → 四段转换 |
| `scripts/render_mobile_pdf.py` | 手机长条 PDF(vendored,可选依赖) |
| `scripts/deliver.py` | 多通道投递(wechat-media/wecom/feishu) |
| `scripts/run_acceptance.py` | 独立验收套件(纯标准库) |
| `references/` | 邮件/格式/通道/可选 cron 门禁/注册文档 |
