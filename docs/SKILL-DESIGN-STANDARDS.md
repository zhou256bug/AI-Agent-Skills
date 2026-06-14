# Agent Skill 设计标准（硬性规则）

本文件是 `AI-Agent-Skills` monorepo 的**技能设计宪法**。  
新增或规范化技能时，必须对照本文；PR 合并前完成 [Checklist](#十二上线-checklist)。

**参考技能**（已对齐或基本对齐）：

| 技能 | 擅长示范 |
|------|----------|
| `cross-cultural-consultant` | 通用化、渐进式加载、手机 PDF、无凭据开箱即用 |
| `aliyun-enterprise-mail` | 引导配置 `setup status/apply`、凭据隔离 |
| `huazhirong-management-weekly-report` | 独立跑通、`run_acceptance.py`、参数化、断点续跑 |
| `huazhirong-legal-affairs` | Emoji 输出、法务 PDF、`setup`、单 Agent 闭环 |

---

## 一、七大原则（硬性）

### 1. 通用化

**定义**：技能不绑定特定平台路径、特定主机、特定人名或旧项目目录。

| 必须 | 禁止 |
|------|------|
| 脚本与文档使用 skill 内相对路径 | `$HERMES_HOME/...`、`/Users/...` 等等人绝对路径 |
| 平台无关的描述与 CLI | `delegate_task`、委派其他 Agent/profile/skill |
| 人名/旧代号可配置或中性化（如「老板」） | 硬编码 `菜头`、`方律`、`大为`、`newpos/` |
| `metadata.{openclaw,hermes}` 声明依赖 | 隐式依赖仓库外工具链 |

### 2. 独立跑通

**定义**：单个技能目录 clone 后即可注册、自检、完成核心流程，不依赖 monorepo 内其他技能。

| 必须交付 |
|----------|
| `scripts/run_acceptance.py` **或** `evaluation/run_evals.py` + `evals.json` |
| 验收脚本 **纯标准库**可运行（可选依赖缺失时 SKIP，不算 FAIL） |
| 核心能力不依赖其他 skill 的运行时加载 |

### 3. 开箱即用

**定义**：clone → 注册 `extra_dirs` → 加载 `SKILL.md` 即可用；默认值合理。

| 必须交付 |
|----------|
| `SKILL.md` §零（或 §一）写明开箱路径与注册链接 |
| 知识/数据在 `references/`、`data/`、`modules/` 内自包含 |
| 无凭据技能：零配置可跑核心流程 |
| 有凭据技能：缺凭据时 `setup status` 引导，而非直接报错退出 |

### 4. 参数化

**定义**：公司、人名、路径、主体等可变项集中配置，支持环境变量覆盖。

| 必须交付 |
|----------|
| `scripts/<skill>_config.py`（或等价单一配置模块） |
| 配置表：环境变量名、默认值、含义 |
| 禁止在多个脚本中散落硬编码业务常量 |

### 5. 引导配置化

**定义**：需要凭据或个性化时，提供 Agent 可执行的配置流程。

| 有凭据/个性化时必须有 |
|----------------------|
| `setup status` — 输出 `needsSetup`、`fieldsToCollect` |
| `setup apply` — 写入 `local/credentials.env`（gitignore） |
| `doctor` 或 `--verify` — 验证配置与目录可写 |
| `references/onboarding-flow.md` |
| `local/credentials.env.example` |

无凭据且默认值足够的技能：在 `setup status` 中说明 `needsSetup: false`，仍可提供可选个性化（如法务技能）。

### 6. Emoji 化（提升阅读体验）

**定义**：面向用户的长文本输出，使用统一 emoji 标记结构，便于手机扫读。

| 必须交付（有用户报告输出的技能） |
|--------------------------------|
| `references/emoji-output-guide.md` 或在输出模板中嵌入等价规范 |
| 至少包含：`📌` 结论、`🔴🟡🟢` 分级、`👉` 下一步 |
| 涉合规/免责： `⚗️` 免责声明 |
| `scripts/validate_*_output.py` 可校验关键标记（推荐） |

纯工具型技能（如仅 `list/read` 邮件）可豁免，但须在 `SKILL.md` 注明。

### 7. 手机体验化（内容输出）

**定义**：长报告类输出支持手机竖版 PDF，与跨文化技能同款体验。

| 必须交付（有 PDF 场景的 skill） |
|-------------------------------|
| vendored 或自有 `scripts/render_mobile_pdf.py`（预设 `mobile-default`） |
| 便捷封装：`scripts/render_*_pdf.py`（推荐） |
| `references/pdf-*-workflow.md` |
| `SKILL.md` 专节：禁止 Agent 手写 HTML；可选依赖声明 |
| 可选依赖：`weasyprint`、`ghostscript`、`PyMuPDF`、Noto Sans SC |
| 未安装依赖时：降级交付 Markdown，核心流程不受影响 |

---

## 二、基础架构规则（所有技能）

### 单 Agent 闭环

- 一个 skill = 一个 Agent 工作流闭环
- 禁止委派外部 Agent、profile、其他 skill
- 跨技能协作须在文档中标注「用户自行切换 skill」，不得在 skill 内自动委派

### 渐进式加载

- `SKILL.md`：frontmatter + 路由表 + 全局铁律（建议 < 300 行有效规则）
- 场景细节：`modules/`、`references/`、`frameworks/`
- 按触发词只加载当前模式所需文件

### 归档与产物

- 本地产物写入 `output/`（可配置），**不入库**
- `.gitignore`：`output/`、`*.pdf`、`local/credentials.env`、`__pycache__/`

### 平台脚手架（必须）

```
<skill>/
├── agents/openclaw.yaml
├── agents/hermes.yaml
├── agents/openai.yaml
├── bundles/<slash>.hermes.yaml        # 有 slash 命令时
└── references/openclaw-hermes-registration.md
```

### 变更与版本

- 技能级 `CHANGELOG.md`（Keep a Changelog + SemVer）
- 根 `CHANGELOG.md` 记录仓库级「新增/规范化技能」
- `SKILL.md` frontmatter `version` 与技能 `CHANGELOG.md` 一致

### 安全

- 凭据、token、密码**永不入库**
- 文档与错误信息用 `${ENV_VAR}` 占位
- `local/credentials.env` 权限 `600`（setup apply 时）

---

## 三、标准目录结构

```
<skill>/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── evals.json                          # 推荐
├── agents/
├── bundles/
├── data/                               # 按需
├── frameworks/                         # 按需
├── modules/                            # 按需
├── references/
│   ├── openclaw-hermes-registration.md
│   ├── onboarding-flow.md              # 有 setup 时
│   ├── emoji-output-guide.md           # 有报告输出时
│   └── pdf-*-workflow.md               # 有 PDF 时
├── scripts/
│   ├── <skill>_config.py
│   ├── <skill>_cli.py                  # 有 setup 时
│   ├── run_acceptance.py               # 推荐
│   ├── render_mobile_pdf.py            # 有 PDF 时（可 vendored）
│   └── render_*_pdf.py                 # 可选封装
├── evaluation/
│   └── run_evals.py
└── local/
    ├── .gitkeep
    └── credentials.env.example
```

---

## 四、SKILL.md frontmatter 最低要求

```yaml
---
name: <skill-name>
version: x.y.z
description: <一句话能力>。Use when <触发词列表>。
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    skillKey: <skill-name>
  hermes:
    tags: [...]
    category: productivity
    requires_toolsets: ["terminal"]
user-invocable: true
license: MIT
---
```

`description` 必须含英文触发词 `Use when ...`，供 Agent 发现。

---

## 五、验收标准

### 最低验收（merge 前必过）

```bash
# 仓库级脚手架检查（对所有根目录技能）
python3 scripts/validate_skill_scaffold.py

# 新技能上线推荐加 --strict（建议项也视为失败）
python3 scripts/validate_skill_scaffold.py --strict --skill <new-skill>

# 技能级验收（在对应技能目录）
python3 <skill>/scripts/run_acceptance.py    # 若有
python3 <skill>/evaluation/run_evals.py      # 若有
```

### 验收脚本约定

| 约定 | 说明 |
|------|------|
| 退出码 0 | 全部 PASS；SKIP 不计入 FAIL |
| 禁止调用 LLM | 静态结构/配置/文件校验 |
| 覆盖 | 文件存在、禁止词、config 默认值、setup、evals 引用 |

---

## 六、反模式（禁止）

| 反模式 | 正确做法 |
|--------|----------|
| migration 总入口 SKILL 委派链 | 拆成独立 skill，单 Agent 闭环 |
| `newpos/` 归档路径 | `output/` + 可配置 |
| 现场手写 HTML 出 PDF | `render_mobile_pdf.py` |
| 续签不对比直接评条款 | 先 `🔍` 差异表 |
| 混用 Playbook 立场 | 先路由表确认甲方/乙方/雇主 |
| 真实密钥写入 example | 仅占位符 |

---

## 七、技能分级（决定哪些规则适用）

| 类型 | 示例 | 引导 setup | Emoji | 手机 PDF |
|------|------|------------|-------|----------|
| A 知识/审核类 | legal-affairs, cross-cultural | 可选个性化 | 必须 | 推荐 |
| B 凭据工具类 | aliyun-enterprise-mail | 必须 | 豁免 | 豁免 |
| C 编排自动化类 | weekly-report | 必须 | 必须 | 必须 |
| D 纯数据/校验类 | （未来） | 视情况 | 豁免 | 豁免 |

新建技能时先定类型，再查表确定必选项。

---

## 八、与 Cursor / Cloud Agent 的配合

- 仓库规则：`.cursor/rules/skill-design-standards.mdc`（`alwaysApply: true`）
- 开发新技能前：阅读本文 + 复制 `docs/skill-template/`
- PR 描述：粘贴 [Checklist](#十二上线-checklist) 完成项

---

## 九、migration 规范化流程

1. 从 `migration/<name>/` 提取**有用** Playbook/脚本
2. 删除：委派链、平台耦合、旧路径、过时人名
3. 在仓库根创建 `<skill>/`，按本文档建脚手架
4. 跑 `validate_skill_scaffold.py` + 技能验收
5. 根 `README.md` 技能表新增一行
6. 根 `CHANGELOG.md` `[Unreleased]` 追加
7. `migration/` 原目录保留素材即可，**不注册使用**

---

## 十、Emoji 速查（输出类技能默认）

| Emoji | 含义 |
|-------|------|
| ⚖️ | 标题/法务立场 |
| 📌 | 结论 |
| 🚨 | 极高危 |
| 🔴🟡🟢 | Tier 1/2/3 |
| 🔍 | 对比/差异 |
| 📎 | 缺失项 |
| 👉 | 建议下一步 |
| 👤 | 升级老板/决策者 |
| ⚗️ | 免责声明/外部律师 |
| 💰🌍🔐💳 | 付款/管辖/IP/支付 |

完整规范见各技能 `references/emoji-output-guide.md`。

---

## 十一、手机 PDF 速查

```bash
python3 <skill>/scripts/render_review_pdf.py \
  --title "报告标题" \
  --body-md output/.../report.md \
  --party "对方名" --mode A
```

底层统一 `render_mobile_pdf.py --preset mobile-default`（284pt 宽 / 10pt 正文）。

---

## 十二、上线 Checklist

复制到 PR 描述，逐项勾选：

```
[ ] 技能类型已确定（A/B/C/D）
[ ] SKILL.md frontmatter + 路由表 + 版本号
[ ] README.md + CHANGELOG.md（技能级）
[ ] agents/{openclaw,hermes,openai}.yaml + openclaw-hermes-registration.md
[ ] 参数化 config 模块（或文档说明无需）
[ ] setup status/apply/doctor（有凭据或个性化时）
[ ] 单 Agent 闭环（无 delegate_task / 无委派）
[ ] output/ 归档 + .gitignore
[ ] emoji-output-guide（输出类技能）
[ ] pdf-workflow + render_*_pdf（长报告类技能）
[ ] run_acceptance.py 或 run_evals.py 通过
[ ] python3 scripts/validate_skill_scaffold.py 通过
[ ] 根 README.md 技能表已更新
[ ] 根 CHANGELOG.md [Unreleased] 已追加
[ ] 无真实凭据/密钥/绝对路径
```

---

## 十三、修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-06-14 | 首版：七大原则 + 脚手架 + Checklist |
