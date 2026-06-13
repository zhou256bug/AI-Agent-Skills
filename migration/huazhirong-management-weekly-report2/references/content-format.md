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

## 渲染

```bash
python3 "$HERMES_HOME/tools/render_mobile_pdf.py" \
  --preset weekly-report \
  --title "总裁办及各部门经理周报 · 第N期" \
  --body-md "…/W{N}-YYYY年MM月DD日.md" \
  --output "…/W{N}-YYYY年MM月DD日.pdf"
```

## 结构（四段，无单独「菜头重点」）

菜头行程/来访并入 **二、海外市场** 或 **三、业务线**，**不设第一节**。

### meta

```markdown
:::meta
第23期 | 汇总日期：2026-06-08 | 来源：陈徐伟

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

### 四、需菜头关注的事项

`:::urgent` 编号 6–10 条，末尾署名。

## 推送（必做）

Cron/人工完成后，最终回复**必须含单独一行**：

```
MEDIA:/绝对路径/W23-2026年06月08日.pdf
```

否则微信只收到文字、**不会附 PDF**。
