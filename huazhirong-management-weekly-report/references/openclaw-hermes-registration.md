# OpenClaw / Hermes 注册配置（复制即用）

加载 `huazhirong-management-weekly-report` 的可粘贴配置。技能脚本**纯标准库**,clone 即可注册自检;**邮件读取/PDF/投递**按需配置(邮箱凭据、可选依赖、webhook)。

源文件:`../agents/openclaw.yaml`、`../agents/hermes.yaml`、`../agents/openai.yaml`、`../bundles/weekly-report.hermes.yaml`。

## 0. 克隆仓库

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
```

## 1. OpenClaw

编辑 `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    load: { extraDirs: ["~/Projects/AI-Agent-Skills"], watch: true },
    entries: { "huazhirong-management-weekly-report": { enabled: true } },
  },
}
```

## 2. Hermes

编辑 `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/Projects/AI-Agent-Skills
```

bundle(可选 slash 命令):

```bash
mkdir -p ~/.hermes/skill-bundles
cp ~/Projects/AI-Agent-Skills/huazhirong-management-weekly-report/bundles/weekly-report.hermes.yaml \
   ~/.hermes/skill-bundles/weekly-report.yaml
# 使用： /weekly-report 做第23期周报总结
```

## 3. 配置(可选，环境变量覆盖默认)

```bash
export WEEKLY_REPORT_OWNER=老板
export WEEKLY_REPORT_SENDER_EMAIL=evyn.chen@newpostech.com
export WEEKLY_REPORT_SUBJECT_KEY=总裁办及各部门经理周报
export WEEKLY_REPORT_ARCHIVE_DIR=~/reports/weekly
python3 ~/Projects/AI-Agent-Skills/huazhirong-management-weekly-report/scripts/weekly_report_config.py
```

## 4. 自检

```bash
SKILL_DIR=~/Projects/AI-Agent-Skills/huazhirong-management-weekly-report
python3 "$SKILL_DIR/scripts/run_acceptance.py"   # 纯标准库；render 用例在无 weasyprint 时自动 SKIP
```

## 5. 可选依赖

- **手机 PDF**:`weasyprint`、`ghostscript`、`PyMuPDF`(`fitz`)+ Noto Sans SC 字体。
- **投递**:企业微信/飞书需对应 `*_WEBHOOK_URL`(见 `delivery-channels.md`);微信走 `MEDIA:` 桥接无需额外依赖。

## 6. Git 边界

| 提交 | 不提交 |
|------|--------|
| `SKILL.md`、`scripts/`、`agents/`、`bundles/`、`references/` | `output/`(MD/PDF 产物) |
| `CHANGELOG.md`、`.gitignore` | `__pycache__/`、`*.pyc`、`.DS_Store` |
| | 任何邮箱密码 / webhook 密钥 |
