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
| [`huazhirong-legal-affairs`](huazhirong-legal-affairs/) | 华智融法务合同审核:海外经销/采购供货/境内用工/解约终止/POS合规;单 Agent 闭环,Playbook 自包含 | 无 | 无 | ✅ 可用 |
| `migration/huazhirong-business-support` | 华智融商务支持总入口原始迁移素材 | — | — | 🚧 待规范化(强耦合,后续讨论) |

> `migration/` 保留尚未规范化的原始技能素材,**不建议直接注册使用**;规范化后的技能会提升到仓库根目录。

---

## 仓库结构

```
AI-Agent-Skills/
├── README.md                 # 本文件
├── CHANGELOG.md              # 仓库级变更(Keep a Changelog + SemVer)
├── LICENSE                   # Apache-2.0
├── aliyun-enterprise-mail/   # 技能:阿里企业邮箱读信
├── cross-cultural-consultant/# 技能:跨文化管理顾问
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

新增或规范化一个技能时,对齐以下约定:

1. **入口 `SKILL.md`**:YAML frontmatter 至少含 `name`、`description`(写清 *Use when* 触发词)、`metadata.{openclaw,hermes}`;正文只做路由,细节拆到子文件按需加载。
2. **自包含**:运行所需的数据 / 知识 / 脚本放进技能目录,**不依赖特定主机的绝对路径或平台专有脚本路径**(如 `$HERMES_HOME/...`)。
3. **平台脚手架**:提供 `agents/{openclaw,hermes,openai}.yaml` 与 `references/openclaw-hermes-registration.md`,确保 clone 即可注册。
4. **变更记录**:技能目录内维护 `CHANGELOG.md`,仓库级变更同时记入根 `CHANGELOG.md`;均遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/)。
5. **可选依赖显式声明**:非核心能力(如 PDF 渲染)所需的第三方依赖在 `SKILL.md` 与注册文档中标注为"可选",缺失时核心流程不受影响。
6. **自检脚本**:尽量提供纯标准库的校验/自检脚本(如 `scripts/validate-data.py`、`evaluation/run_evals.py`),便于 clone 后快速验证。

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
