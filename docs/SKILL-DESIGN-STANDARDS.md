# Agent Skill 设计标准（硬性规则 / 宪法）

本文件是 `AI-Agent-Skills` monorepo 的**技能设计宪法**。  
新增或规范化技能时，**必须先读本文**；PR 合并前完成 [Checklist](#十三上线-checklist)。

> **平台哲学（OpenClaw / Hermes / Cursor）**：Skill 是 **渐进式加载的原子能力**，不是「小应用」。  
> **编排发生在 Agent 会话或 Cron Prompt**，不在单个 Skill 内堆叠整条流水线。

**参考技能**：

| 技能 | 类型 | 擅长示范 |
|------|------|----------|
| `aliyun-enterprise-mail` | **B 原子工具** | IMAP 读信 + setup（一件事） |
| `cross-cultural-consultant` | **A 领域知识** | 单领域多模式 + 渐进加载 + PDF |
| `huazhirong-legal-affairs` | **A 领域知识** | 合同审核 Playbook + emoji + PDF |
| `huazhirong-management-weekly-report` | **E 编排例外** | 状态机 + 断点续跑（历史包袱，新需求勿模仿） |

原子技能设计指引：[`docs/skill-template/ATOMIC-SKILL-GUIDE.md`](skill-template/ATOMIC-SKILL-GUIDE.md)

---

## 零、原子技能 vs 编排（先读）

### 什么是原子技能

**一个 Skill = 一个可独立注册、独立验收、单一职责的能力单元。**

| 维度 | 原子 Skill ✅ | 编排型 Monolith ❌ |
|------|---------------|-------------------|
| `description` / slash | 窄触发词（如「读 IMAP 未读」） | 宽触发词（如「邮件 cron 全流程」） |
| SKILL.md 体量 | 短；路由 ≤ 少量模式 | 长；含 cron + 投递 + 多工具 |
| 脚本 | 1～3 个核心 CLI | fetch→transform→render→deliver 全包 |
| 复用 | 被多个场景组合 | 与别的 skill 能力重复 |
| 验收 | 只测**这一件事** | 测整条业务链 |

**示例（邮件 cron）应拆为**：

```
aliyun-enterprise-mail (或 imap-read)  →  UNSEEN / read / attachments
watchlist (可选)                         →  关注人 list/add/match
scan-summary-format (可选)               →  emoji Markdown 模板
mobile-pdf-render (共享)                 →  md → 284pt PDF
weixin-deliver (共享)                    →  bridge 推送
────────────────────────────────────────────────────────────
Hermes cron prompt / bundle              →  显式组合上述步骤（平台层）
```

### 组合在哪里做

| 层级 | 职责 | 示例 |
|------|------|------|
| **原子 Skill** | 一件事 + 脚本 + 文档 | `check_unseen.py` 只在 mail skill 内 |
| **Hermes bundle** | 列出多个 skills + 简短 instruction | `bundles/inbox-scan.hermes.yaml` |
| **Cron prompt** | 逐步调用脚本 / 切换 skill | `docs/cron-prompts/inbox-scan.md` |
| **用户对话** | 用户 slash 不同 skill | `/mail-read` → `/mobile-pdf` |

### 与「单 Agent」的关系（重要）

| 禁止 ❌ | 允许 ✅ |
|---------|---------|
| `delegate_task` 派给另一个 Agent/profile | 同一 Agent 会话内按步骤使用多个原子 skill |
| Skill 内写「自动加载 weekly-report」 | Cron prompt 写「先 A 再 B」 |
| Skill 内隐式调用其他 skill 的 runtime | 用户显式切换 slash 或 Agent 读 prompt 组合 |

**单 Agent 闭环** = 一个 Agent 会话内完成用户目标；**不等于**一个 Skill 包办一切。

---

## 一、八大原则（硬性）

### 1. 原子技能（优先）

**定义**：新建 skill **默认必须是原子技能**；多步流水线通过平台组合，不得新建 monolith skill。

| 必须 | 禁止 |
|------|------|
| `description` 只描述**单一能力** | 一个 skill 覆盖读信+摘要+PDF+推送+cron |
| `SKILL.md` 有效规则建议 **< 150 行**（领域 A 类可至 300） | 把 cron 运维手册塞进 skill |
| 验收只覆盖本 skill 的原子能力 | 验收假设其他 skill 已加载 |
| 需组合时写 `references/composes-with.md` 或 bundle | 在 skill 内写死「联动某某 skill」自动执行 |

**编排例外（E 类）**：见 [§八 技能分级](#八技能分级)；须 PR 说明理由（状态机、幂等、断点续跑等）。

### 2. 通用化

**定义**：技能不绑定特定平台路径、特定主机、特定人名或旧项目目录。

| 必须 | 禁止 |
|------|------|
| 脚本与文档使用 skill 内相对路径 | `$HERMES_HOME/...`、`/Users/...` 等等人绝对路径 |
| 平台无关的描述与 CLI | `delegate_task`、委派其他 Agent/profile |
| 人名/旧代号可配置或中性化（如「老板」） | 硬编码 `菜头`、`方律`、`大为`、`newpos/` |
| `metadata.{openclaw,hermes}` 声明依赖 | 隐式依赖仓库外工具链 |

> **注意**：Skill 内禁止**自动**加载其他 skill；文档中说明「可与 X 组合」是允许的。

### 3. 独立跑通

**定义**：单个**原子** skill 目录 clone 后即可注册、自检、完成**其唯一核心能力**，不依赖 monorepo 内其他 skill。

| 必须交付 |
|----------|
| `scripts/run_acceptance.py` **或** `evaluation/run_evals.py` + `evals.json` |
| 验收脚本 **纯标准库**可运行（可选依赖缺失时 SKIP，不算 FAIL） |
| 验收**不要求**跑通跨 skill 业务流水线 |

### 4. 开箱即用

**定义**：clone → 注册 `extra_dirs` → 加载 `SKILL.md` 即可用；默认值合理。

| 必须交付 |
|----------|
| `SKILL.md` §零（或 §一）写明开箱路径与注册链接 |
| 知识/数据在 `references/`、`data/`、`modules/` 内自包含 |
| 无凭据技能：零配置可跑核心流程 |
| 有凭据技能：缺凭据时 `setup status` 引导，而非直接报错退出 |

### 5. 参数化

**定义**：公司、人名、路径、主体等可变项集中配置，支持环境变量覆盖。

| 必须交付 |
|----------|
| `scripts/<skill>_config.py`（或等价单一配置模块） |
| 配置表：环境变量名、默认值、含义 |
| 禁止在多个脚本中散落硬编码业务常量 |

### 6. 引导配置化

**定义**：需要凭据或个性化时，提供 Agent 可执行的配置流程。

| 有凭据/个性化时必须有 |
|----------------------|
| `setup status` — 输出 `needsSetup`、`fieldsToCollect` |
| `setup apply` — 写入 `local/credentials.env`（gitignore） |
| `doctor` 或 `--verify` — 验证配置与目录可写 |
| `references/onboarding-flow.md` |
| `local/credentials.env.example` |

### 7. Emoji 化（提升阅读体验）

**定义**：面向用户的长文本输出，使用统一 emoji 标记结构，便于手机扫读。

| 必须交付（有用户报告输出的技能） |
|--------------------------------|
| `references/emoji-output-guide.md` 或在输出模板中嵌入等价规范 |
| 至少包含：`📌` 结论、`🔴🟡🟢` 分级、`👉` 下一步 |
| `scripts/validate_*_output.py` 可校验关键标记（推荐） |

**B 原子工具类**可豁免，须在 `SKILL.md` 注明。

### 8. 手机体验化（内容输出）

**定义**：长报告类输出支持手机竖版 PDF，与跨文化技能同款体验。

| 必须交付（有 PDF 场景的 skill） |
|-------------------------------|
| 优先复用仓库共享 `render_mobile_pdf.py`（见 [§九 共享能力](#九共享能力模块)） |
| 或 skill 内 vendored + `render_*_pdf.py` 封装 |
| `references/pdf-*-workflow.md`；禁止 Agent 手写 HTML |
| 缺依赖时降级 Markdown，原子能力不中断 |

**B 原子工具类**可豁免 PDF。

---

## 二、基础架构规则（所有技能）

### 渐进式加载

- `SKILL.md`：frontmatter + **窄路由** + 全局铁律
- 场景细节：`modules/`、`references/`、`frameworks/`
- 按触发词**只加载当前模式**所需文件
- Agent 不应为读信而加载整包 cron+推送规则

### 归档与产物

- 本地产物写入 `output/`（可配置），**不入库**
- `.gitignore`：`output/`、`*.pdf`、`local/credentials.env`、`__pycache__/`

### 平台脚手架（必须）

```
<skill>/
├── agents/openclaw.yaml
├── agents/hermes.yaml
├── agents/openai.yaml
├── bundles/<slash>.hermes.yaml        # 可选：组合多个原子 skill
└── references/openclaw-hermes-registration.md
```

### 变更与版本

- 技能级 `CHANGELOG.md`（Keep a Changelog + SemVer）
- 根 `CHANGELOG.md` 记录仓库级变更
- `SKILL.md` frontmatter `version` 与技能 `CHANGELOG.md` 一致

### 安全

- 凭据、token、密码**永不入库**
- 文档与错误信息用 `${ENV_VAR}` 占位
- `local/credentials.env` 权限 `600`（setup apply 时）

---

## 三、标准目录结构（原子 skill）

```
<skill>/
├── SKILL.md                 # 短；单一职责
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── evals.json
├── agents/
├── bundles/                 # 可选
├── data/                    # 按需
├── references/
│   ├── openclaw-hermes-registration.md
│   ├── onboarding-flow.md   # 有 setup 时
│   ├── composes-with.md     # 推荐：写可与哪些 skill 组合
│   └── ...
├── scripts/
│   ├── <skill>_config.py
│   ├── <skill>_cli.py
│   └── run_acceptance.py
└── local/
    └── credentials.env.example
```

---

## 四、SKILL.md frontmatter 最低要求

```yaml
---
name: <skill-name>
version: x.y.z
description: <单一能力一句话>。Use when <窄触发词>。
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

`description` 必须含英文 `Use when ...`。**禁止**在 description 中堆砌多种 unrelated 能力（读信+推送+cron）。

可选 frontmatter 字段（推荐）：

```yaml
skill_type: B          # A/B/D/E，见 §八
atomic: true           # 默认 true；E 类编排例外标 false
```

---

## 五、验收标准

### 最低验收（merge 前必过）

```bash
python3 scripts/validate_skill_scaffold.py
python3 scripts/validate_skill_scaffold.py --strict --skill <new-skill>   # 新技能推荐
python3 <skill>/scripts/run_acceptance.py    # 或 evaluation/run_evals.py
```

### 原子技能验收必须回答

1. 本 skill **唯一核心能力**是什么？（一句话）  
2. 去掉其他 skill，能否单独 demo？  
3. 是否存在应迁到 cron/bundle 的编排步骤？

---

## 六、反模式（禁止）

| 反模式 | 正确做法 |
|--------|----------|
| **Monolith 编排 skill**（IMAP+watch+cron+PDF+微信一包） | 拆原子 skill + cron prompt / bundle |
| migration 总入口 SKILL 委派链 | 拆成多个原子 skill |
| Skill 内「自动调用 weekly-report」 | cron prompt 或用户切换 slash |
| `newpos/` 归档路径 | `output/` + 可配置 |
| 现场手写 HTML 出 PDF | `render_mobile_pdf.py` |
| 真实密钥写入 example | 仅占位符 |
| 一个 slash 触发 5 种 unrelated 工具 | 拆 slash 或拆 skill |

---

## 七、组合模式（平台层）

### Hermes bundle（推荐）

```yaml
name: inbox-scan
skills:
  - aliyun-enterprise-mail
  - mobile-pdf-render      # 未来共享 skill
instruction: |
  组合原子技能完成收件箱扫描：mail unread → format → pdf → deliver。
  步骤见 docs/cron-prompts/inbox-scan.md
```

### Cron prompt（推荐）

存放在 `docs/cron-prompts/`，**不是** skill 目录内 monolith 文档。

### composes-with.md（skill 内可选）

说明本 skill 常与哪些 skill 组合，**但不自动执行**。

---

## 八、技能分级

新建 skill **必须先定类型**。默认选 **B 或 A**，不要轻易选 E。

| 类型 | 含义 | 示例 | setup | Emoji | PDF |
|------|------|------|-------|-------|-----|
| **B 原子工具** | 单一工具/协议 | `aliyun-enterprise-mail` | 有凭据则必须 | 豁免 | 豁免 |
| **A 领域知识** | 单领域 Playbook（可多 mode） | legal-affairs, cross-cultural | 可选 | 必须 | 推荐 |
| **D 数据/校验** | 纯数据、validator | watchlist-only（未来） | 视情况 | 豁免 | 豁免 |
| **E 编排例外** | 多阶段状态机；**须 PR 批准** | weekly-report | 必须 | 必须 | 必须 |

**E 类准入条件**（须 PR 正文说明）：

- 存在**跨阶段状态持久化**（如 `.state/W{N}.json`）  
- 或**强幂等/断点续跑**需求，拆原子后反而更易错  
- 有**迁移/拆分计划**或维护者承诺  

**不再默认新建 C 类「编排自动化」monolith skill。**

---

## 九、共享能力模块（规划中）

以下能力应逐步从业务 skill **抽出**为原子 skill 或 `packages/`，避免重复 vendored：

| 共享能力 | 现状 | 目标 |
|----------|------|------|
| `render_mobile_pdf.py` | 多 skill 各 vendored 一份 | 单一 `mobile-pdf-render` skill 或 packages |
| 微信 bridge 投递 | weekly-report `deliver.py` | `weixin-deliver` 原子 skill |
| IMAP 读信 | aliyun-enterprise-mail | 通用 `imap-read` 或扩展 aliyun |

在新共享 skill 落地前，**允许**在单个原子 skill 内 vendored，但**禁止**为同一能力再建第三个 monolith。

---

## 十、migration 规范化流程

1. 从 `migration/` 提取**原子** Playbook/脚本（按职责拆块）  
2. 删除：委派链、monolith 入口、平台耦合、旧路径  
3. **每个原子能力**一个 `<skill>/` 目录  
4. 组合逻辑 → `docs/cron-prompts/` 或 bundle，不进入 skill  
5. 跑验收 + 根 README/CHANGELOG 更新  
6. `migration/` 保留素材，**不注册**

---

## 十一、Emoji / PDF 速查

见原规范：`emoji-output-guide.md`、`render_mobile_pdf.py --preset mobile-default`（284pt）。

---

## 十二、与 Cursor / Cloud Agent 的配合

- 仓库规则：`.cursor/rules/skill-design-standards.mdc`（`alwaysApply: true`）  
- 新建 skill：本文 + [`ATOMIC-SKILL-GUIDE.md`](skill-template/ATOMIC-SKILL-GUIDE.md) + [`CHECKLIST.md`](skill-template/CHECKLIST.md)

---

## 十三、上线 Checklist

```
[ ] 已确认：本 skill 是原子 skill（B/A/D），或已获批 E 类编排例外
[ ] 一句话核心能力已写在 PR 描述
[ ] description / slash 触发词足够窄
[ ] 无 monolith 编排（或 E 类已说明理由）
[ ] SKILL.md + README + CHANGELOG + agents/ + registration
[ ] 参数化 config；setup（有凭据时）
[ ] 无 delegate_task；无 skill 内自动加载其他 skill
[ ] composes-with.md 或 bundle/cron 说明组合方式（若需组合）
[ ] run_acceptance / run_evals 通过
[ ] validate_skill_scaffold 通过
[ ] 根 README + CHANGELOG 已更新
[ ] 无真实凭据/绝对路径
```

---

## 十四、修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.0 | 2026-06-15 | **原子技能优先**：八大原则、组合/platform 分层、E 类编排例外、反 monolith |
| 1.0.0 | 2026-06-14 | 首版：七大原则 + 脚手架 + Checklist |
