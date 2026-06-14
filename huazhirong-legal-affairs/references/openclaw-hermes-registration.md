# OpenClaw / Hermes 注册配置（复制即用）

本文提供 **OpenClaw** 与 **Hermes Agent** 加载 `huazhirong-legal-affairs` 的可粘贴配置。

本 skill **Playbook 自包含、无任何凭据**：clone 仓库 → 注册目录 → 直接用。

相关源文件：

- OpenClaw 片段：`../agents/openclaw.yaml`
- Hermes 片段：`../agents/hermes.yaml`
- Cursor 类 Agent 入口：`../agents/openai.yaml`
- Hermes bundle：`../bundles/legal-affairs.hermes.yaml`

---

## 0. 克隆仓库

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
```

Skill 路径：`~/Projects/AI-Agent-Skills/huazhirong-legal-affairs/`

---

## 1. OpenClaw

编辑 `~/.openclaw/openclaw.json`：

```json5
{
  skills: {
    load: {
      extraDirs: ["~/Projects/AI-Agent-Skills"],
      watch: true,
    },
    entries: {
      "huazhirong-legal-affairs": {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      skills: ["huazhirong-legal-affairs"],
    },
  },
}
```

---

## 2. Hermes

编辑 `~/.hermes/config.yaml`：

```yaml
skills:
  external_dirs:
    - ~/Projects/AI-Agent-Skills
```

### slash 命令（推荐）

复制 `bundles/legal-affairs.hermes.yaml` 到 Hermes bundles 目录，或在对话中使用：

```bash
hermes chat --toolsets terminal,skills -q "/legal-affairs 帮我审核这份采购合同"
```

### 本地软链（可选）

```bash
mkdir -p ~/.hermes/skills
ln -sf ~/Projects/AI-Agent-Skills/huazhirong-legal-affairs \
  ~/.hermes/skills/huazhirong-legal-affairs
```

---

## 3. 自检

```bash
python3 ~/Projects/AI-Agent-Skills/huazhirong-legal-affairs/evaluation/run_evals.py
python3 ~/Projects/AI-Agent-Skills/huazhirong-legal-affairs/scripts/validate_review_output.py --sample
```

---

## 4. 使用提示

1. **先分类**：收到合同后确认我方是甲方/乙方/用人单位
2. **续签必对比**：老客户续签立即做新旧差异表
3. **结论先行**：🔴/🟡/🟢 分级输出
4. **归档**：审核意见写入 `output/合同/`（可通过 `LEGAL_AFFAIRS_ARCHIVE_DIR` 覆盖）
5. **单 Agent**：本 skill 不委派其他 Agent 或 skill

---

## 5. 配置（可选）

| 环境变量 | 默认 | 含义 |
|----------|------|------|
| `LEGAL_AFFAIRS_DECISION_MAKER` | 老板 | 决策者称呼 |
| `LEGAL_AFFAIRS_COMPANY` | 华智融 | 公司名 |
| `LEGAL_AFFAIRS_ARCHIVE_DIR` | `<skill>/output` | 归档根目录 |

也可写入 `<skill>/local/credentials.env`（已 gitignore）。
