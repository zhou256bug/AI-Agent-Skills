# 管理团队周报 · 内容格式（四段）

**版式金标准**：100mm 宽 · `W22-2026年06月01日.pdf`

## 命名（铁律）

| 项 | 规则 |
|---|---|
| 期号 N | 邮件主题 `总裁办及各部门经理周报（N）` 括号内数字 |
| 文件名 | `W{N}-YYYY年MM月DD日.pdf` / 同名 `.md` |
| 禁止 | ISO 日历周（第24周）、`周报_W24_YYYYMMDD_手机长条_完整版` 旧格式 |

```bash
# 路径 helper
python3 scripts/weekly_report_paths.py  # 或 import weekly_report_paths.report_paths(N)
```

## 渲染（vendored，可选依赖）

```bash
python3 scripts/render_mobile_pdf.py \
  --preset weekly-report \
  --title "{SUBJECT_KEY} · 第N期" \
  --body-md "<ARCHIVE_DIR>/W{N}-YYYY年MM月DD日.md" \
  --output "<ARCHIVE_DIR>/W{N}-YYYY年MM月DD日.pdf"
```

> 渲染器已 vendored 进本 skill `scripts/`,无需 `$HERMES_HOME`。需可选依赖 weasyprint/ghostscript/PyMuPDF。

## 结构（四段，无单独「{OWNER}重点」）

{OWNER} 行程/来访并入 **二、海外市场** 或 **三、业务线**，**不设第一节**。

### meta

```markdown
:::meta
第23期 | 汇总日期：2026-06-08 | 来源：{SENDER_NAME}

涵盖部门：总裁办(…)、硬件结构部、…
:::
```

### 一、重点项目进展

每个大项目 `### NEW9830`，下一行注明来源：

```markdown
### NEW9830
*周报来源：**肖锦填**、**卢艳娟***
```

表格三列；**状态列保留 emoji**（⏳ ✅ 🆕 ⚠️ 🔵 🟡 🔴），渲染器会放大并选用彩色 emoji 字体以保证清晰。

### 二、海外市场要闻

分区域 `:::info`；每条末尾 `**姓名**`。

### 三、业务线重点关注

五子板块 `###`；每条末尾署名。

### 四、需{OWNER}关注的事项

`:::urgent` 编号 6–10 条，末尾署名。

## 投递（多通道，见 delivery-channels.md）

完成后用 `scripts/deliver.py` 投递。微信通道要求最终回复**含单独一行** `MEDIA:<绝对路径>`(否则微信只收到文字、不附 PDF):

```bash
python3 scripts/deliver.py --channel wechat-media --file <ARCHIVE_DIR>/W23-2026年06月08日.pdf
# 企业微信 / 飞书：--channel wecom / feishu（需配置 webhook）
```
