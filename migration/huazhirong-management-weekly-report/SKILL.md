---
name: huazhirong-management-weekly-report
description: 陈徐伟「总裁办及各部门经理周报」→ 手机长条 PDF。四段结构，W{N}-日期命名，推送必含 MEDIA。instance_ownership=dawei
triggers:
  - 陈徐伟周报
  - 总裁办及各部门经理周报
  - 管理团队周报总结
  - evyn.chen 周报
related_skills:
  - productivity/data-pdf-dashboard: render_mobile_pdf.py（--preset weekly-report）
  - productivity/cron-email-scan: 邮箱 IMAP 规则（本技能专项 cron 执行，邮件扫描不重复生成）
---

# 华智融管理团队周报总结

大为从 **evyn.chen@newpostech.com** 邮件附件 xlsx 提取各部门周报，综合为菜头手机阅读的 **四段 PDF**。

## 何时执行

| 触发 | 说明 |
|------|------|
| **专项 cron（主）** | 周一 **17:10–20:10** 四轮（见 `references/cron-retry.md`） |
| **人工** | 菜头说「做周报总结」「陈徐伟周报 PDF」 |

### Cron 前置 Gate

```bash
python3 "$HERMES_HOME/scripts/weekly_evyn_cron_gate.py" --slot N
```

## 流程

### 1. 去重

- 已有 `W{N}-YYYY年MM月DD日.pdf`（N = 邮件期号）→ **`[SILENT]`**

### 2. 邮件与 xlsx

见 `references/email-and-xlsx.md`。期号 **N** 取自主题括号，**禁止用 ISO 周**。

### 3. 写 Markdown（四段）

见 `references/content-format.md`：

1. **重点项目进展** — 每项目 `> 周报来源：**姓名**`；状态用 emoji（⏳✅🆕⚠️🔵🟡🔴）
2. **海外市场要闻** — 菜头来访等内容编在此处，不单设「菜头重点」
3. **业务线重点关注**
4. **需菜头关注的事项**

蔡伟旭 sheet 内容并入上述各段，**不设独立第一节**。

### 4. 命名与路径

```python
# scripts/weekly_report_paths.py
W{N}-YYYY年MM月DD日.md / .pdf
```

### 5. 校验 → 渲染 → 推送

```bash
validate_weekly_report_md.py …/W23-2026年06月08日.md
render_mobile_pdf.py --preset weekly-report --title "…第23期" …
```

**推送铁律** — 最终回复必须含**单独一行**（否则微信无 PDF）：

```
MEDIA:/Users/ericstudio/Library/Mobile Documents/com~apple~CloudDocs/newpos/笔记/周报/W23-2026年06月08日.pdf
```

另附 3 条关注摘要（第四节）。

## 归档

```
newpos/笔记/周报/
├── 总裁办及各部门经理周报（N）.xlsx
├── W{N}-YYYY年MM月DD日.md
└── W{N}-YYYY年MM月DD日.pdf
```

## 禁止

- ISO 日历周编号、旧文件名 `周报_W24_…_完整版`
- 单独「菜头本周重点」段
- 推送不含 `MEDIA:` 行
