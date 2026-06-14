# AI-Agent-Skills

面向 **OpenClaw / Hermes / Cursor** 等 Agent 平台的 **Agent Skills 技能库**(monorepo)。

每个子目录是一个**自包含技能**:以 `SKILL.md` 为入口(路由 + 全局规则),配套 `scripts/`、`data/`、`references/` 等。技能遵循 **渐进式加载**(Progressive Disclosure)——`SKILL.md` 只做路由,按触发词按需加载子文件,降低上下文消耗。目标是 **clone 仓库 → 注册目录 → 开箱即用**。

---

## 技能一览

| Skill | 说明 | 凭据 | 可选依赖 | 状态 |
|-------|------|------|----------|------|
| [`aliyun-enterprise-mail`](aliyun-enterprise-mail/) | 阿里企业邮箱 IMAP 读信,支持 Agent 对话式引导配置(`setup status` / `apply`) | 需(邮箱 + 客户端授权密码,本地配置) | 无(纯标准库) | ✅ 可用 |
| [`cross-cultural-consultant`](cross-cultural-consultant/) | 跨文化管理顾问:出国前画像 / 出国中场景问答 / 回国后复盘 / 来访接待,基于 Hofstede 六维(119 国)+ 港大 EMBA6611 框架 | 无 | PDF 输出需 weasyprint/ghostscript/PyMuPDF | ✅ 可用 |
| [`huazhirong-management-weekly-report`](huazhirong-management-weekly-report/) | 管理团队周报汇编(独立完整):内置取信→汇编四段→长条 PDF→多通道投递,一条命令编排且失败可断点续跑 | 需(收件箱 IMAP,本地配置) | PDF 需 weasyprint/ghostscript/PyMuPDF;企业微信/飞书投递需 webhook | ✅ 可用 |
| [`huazhirong-legal-affairs`](huazhirong-legal-affairs/) | 华智融法务合同审核:海外经销/采购/境内用工/解约/POS合规/股权;emoji+手机PDF;单 Agent 闭环 | 无 | PDF 需 weasyprint/ghostscript/PyMuPDF | ✅ 可用 |
| `migration/huazhirong-business-support` | 华智融商务支持总入口原始迁移素材 | — | — | 🚧 待规范化(强耦合,后续讨论) |

> `migration/` 保留尚未规范化的原始技能素材,**不建议直接注册使用**;规范化后的技能会提升到仓库根目录。

---

## 仓库结构

```
AI-Agent-Skills/
├── README.md                 # 本文件
├── CHANGELOG.md              # 仓库级变更(Keep a Changelog + SemVer)
├── docs/
│   ├── SKILL-DESIGN-STANDARDS.md   # 技能设计宪法（硬性规则）
│   └── skill-template/             # 新技能 Checklist 与指引
├── scripts/
│   └── validate_skill_scaffold.py  # 仓库级技能脚手架校验
├── LICENSE                   # Apache-2.0
├── aliyun-enterprise-mail/   # 技能:阿里企业邮箱读信
├── cross-cultural-consultant/# 技能:跨文化管理顾问
├── huazhirong-legal-affairs/ # 技能:华智融法务
├── huazhirong-management-weekly-report/
└── migration/                # 原始迁移素材(待规范化)
```

每个已规范化技能的标准结构(以 `aliyun-enterprise-mail` / `cross-cultural-consultant` 为基准):

```
<skill>/
├── SKILL.md                  # 入口:frontmatter(name/description/metadata)+ 路由
├── CHANGELOG.md              # 该技能的细粒度变更
├── .gitignore                # 忽略本地产物 / 凭据 / 缓存
├── agents/                   # 平台注册片段:openclaw.yaml / hermes.yaml / openai.yaml
├── bundles/                  # Hermes bundle(可选 slash 命令)
├── references/               # 配套文档(含 openclaw-hermes-registration.md)
└── scripts/ | data/ | ...    # 该技能的脚本与资源
```

---

## 快速开始(注册到 OpenClaw / Hermes)

以 monorepo 方式注册——让平台扫描仓库下所有 `*/SKILL.md`:

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
```

**OpenClaw** — 编辑 `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    load: {
      extraDirs: ["~/Projects/AI-Agent-Skills"],
      watch: true,
    },
  },
}
```

**Hermes** — 编辑 `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/Projects/AI-Agent-Skills
```

每个技能的完整注册片段、bundle、CLI 模板见各自的 `agents/*.yaml` 与 `references/openclaw-hermes-registration.md`。

---

## 技能开发规范

> **硬性规则全文**：[docs/SKILL-DESIGN-STANDARDS.md](docs/SKILL-DESIGN-STANDARDS.md)  
> **新技能 Checklist**：[docs/skill-template/CHECKLIST.md](docs/skill-template/CHECKLIST.md)  
> **Agent 自动遵守**：`.cursor/rules/skill-design-standards.mdc`

### 七大原则（摘要）

| 原则 | 要点 |
|------|------|
| **通用化** | 无平台专有路径、无委派链、无 `newpos/` |
| **独立跑通** | 单 skill 可注册自检；`run_acceptance.py` 或 `run_evals.py` |
| **开箱即用** | 默认值可跑；知识/data 自包含 |
| **参数化** | `scripts/*_config.py` + 环境变量 |
| **引导配置化** | 有凭据时 `setup status` / `setup apply` |
| **Emoji 化** | 报告输出类：`emoji-output-guide.md`，`📌🔴🟡🟢👉` |
| **手机体验化** | 长报告类：`render_mobile_pdf.py` + PDF 工作流 |

### 基础约定

1. **入口 `SKILL.md`**：frontmatter 含 `name`、`description`（*Use when* 触发词）、`metadata.{openclaw,hermes}`；正文只做路由。
2. **自包含**：不依赖 `$HERMES_HOME/...` 或本机绝对路径。
3. **单 Agent 闭环**：禁止 `delegate_task` 与跨 skill 委派。
4. **平台脚手架**：`agents/{openclaw,hermes,openai}.yaml` + `openclaw-hermes-registration.md`。
5. **变更记录**：技能级 + 根级 `CHANGELOG.md`（Keep a Changelog + SemVer）。
6. **可选依赖显式声明**：PDF 等缺失时核心流程仍可用。
7. **合并前校验**：

```bash
python3 scripts/validate_skill_scaffold.py
python3 <skill>/scripts/run_acceptance.py   # 或 evaluation/run_evals.py
```

**参考技能**：`cross-cultural-consultant` · `aliyun-enterprise-mail` · `huazhirong-management-weekly-report` · `huazhirong-legal-affairs`

---

## 安全与凭据

- **凭据绝不入库**:邮箱密码、API key 等只写本地凭据文件(已在各技能 `.gitignore`),由 Agent 引导配置;仓库只提供 `*.example` 模板。
- 代码 / 注释 / 文档 / 日志中不出现任何真实密钥、密码、生产连接串或个人隐私信息,统一用占位符或环境变量引用。

---

## 版本与变更

- 仓库级变更见根 [`CHANGELOG.md`](CHANGELOG.md);各技能另有独立 `CHANGELOG.md`。
- 遵循语义化版本(SemVer):破坏性变更升 major,新增能力升 minor,修复升 patch。

---

## License

[Apache-2.0](LICENSE) © zhou256bug
