# OpenClaw / Hermes 注册配置（复制即用）

加载 `huazhirong-management-weekly-report` 的可粘贴配置。技能脚本**纯标准库**,clone 即可注册自检。**取信为必备能力**,需配收件箱 IMAP 凭据;PDF/投递为可选增强。

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

## 3. 凭据（必备）与配置

复制凭据模板并填写**收件箱 IMAP**(取信必备)与 `WEIXIN_TO`(微信投递):

```bash
SKILL_DIR=~/Projects/AI-Agent-Skills/huazhirong-management-weekly-report
cp "$SKILL_DIR/credentials.env.example" "$SKILL_DIR/local/credentials.env"
# 编辑 local/credentials.env：WEEKLY_REPORT_IMAP_HOST/USER/PASSWORD、WEIXIN_TO（local/ 已 gitignore）
python3 "$SKILL_DIR/scripts/weekly_report_config.py"   # 查看生效配置（密码脱敏）
```

业务默认值(老板/发件人/公司/主题)已是华智融真实值,要改用环境变量或在 `local/credentials.env` 覆盖。

## 4. 运行与自检

```bash
SKILL_DIR=~/Projects/AI-Agent-Skills/huazhirong-management-weekly-report
python3 "$SKILL_DIR/scripts/run_acceptance.py"   # 纯标准库自检；render 用例无 weasyprint 时自动 SKIP
python3 "$SKILL_DIR/scripts/run_weekly.py"        # 一条命令编排（取信→撰写→渲染→投递），失败可断点续跑
```

编排器对 `NEED_COMPOSE` 状态会停下,提示 Agent 据 xlsx 写四段 Markdown 后重跑(详见 SKILL.md §二/§三)。

## 5. 可选依赖

- **手机 PDF**:`weasyprint`、`ghostscript`、`PyMuPDF`(`fitz`)+ Noto Sans SC 字体。
- **投递**:企业微信/飞书需对应 `*_WEBHOOK_URL`(见 `delivery-channels.md`);微信走 `MEDIA:` 桥接无需额外依赖。

## 6. Git 边界

| 提交 | 不提交 |
|------|--------|
| `SKILL.md`、`scripts/`、`agents/`、`bundles/`、`references/` | `output/`(MD/PDF/xlsx/状态产物) |
| `CHANGELOG.md`、`.gitignore`、`credentials.env.example`、`local/.gitkeep` | `local/credentials.env`(IMAP/WEIXIN 凭据) |
| | `__pycache__/`、`*.pyc`、`.DS_Store` |
