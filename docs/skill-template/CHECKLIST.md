# 新技能上线 Checklist

> 宪法：[`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md)  
> 原子指引：[`ATOMIC-SKILL-GUIDE.md`](ATOMIC-SKILL-GUIDE.md)

## 技能信息

- 技能名：`________________`
- **类型**：□ **B 原子工具**（默认） □ A 领域知识 □ D 数据/校验 □ **E 编排例外（须 PR 理由）**
- **一句话核心能力**：`________________`
- slash 命令：`________________`（触发词须窄）

## 原子性（必答）

- [ ] 本 skill **不是** monolith（未打包读信+推送+cron+PDF 等多职责）
- [ ] 验收**只测**本 skill 核心能力，不测跨 skill 流水线
- [ ] 若需多步组合：已规划 **bundle / cron prompt / composes-with.md**（而非扩大 skill）
- [ ] E 类例外：PR 已说明状态机/断点续跑/拆分计划

## 硬性项（全部技能）

- [ ] `SKILL.md`（frontmatter + 窄路由 + 版本；建议 B 类 <150 行有效规则）
- [ ] `README.md`
- [ ] `CHANGELOG.md`
- [ ] `.gitignore`（`output/`、`local/credentials.env`）
- [ ] `agents/{openclaw,hermes,openai}.yaml`
- [ ] `references/openclaw-hermes-registration.md`
- [ ] `scripts/*_config.py` 或文档说明无需配置
- [ ] 无 `delegate_task`；skill 内不自动加载其他 skill
- [ ] `run_acceptance.py` 或 `evals.json` + `run_evals.py`
- [ ] `python3 scripts/validate_skill_scaffold.py` 通过
- [ ] 根 `README.md` 技能表已更新
- [ ] 根 `CHANGELOG.md` [Unreleased] 已追加

## 按类型追加

### B 原子工具 / 有 IMAP 等凭据

- [ ] `setup status` / `setup apply` / `doctor`
- [ ] `references/onboarding-flow.md`
- [ ] `local/credentials.env.example`
- [ ] `SKILL.md` 注明 Emoji/PDF **豁免**（若适用）

### A 领域知识 / 有用户报告

- [ ] `references/emoji-output-guide.md`
- [ ] 输出模板含 `📌` `🔴🟡🟢` `👉`
- [ ] PDF：共享或 vendored `render_mobile_pdf` + `pdf-*-workflow.md`

### E 编排例外（ rare ）

- [ ] PR 批准 E 类理由 documented
- [ ] 状态/幂等/断点续跑文档
- [ ] Emoji + PDF 全套

## PR 合并前命令

```bash
python3 scripts/validate_skill_scaffold.py
python3 scripts/validate_skill_scaffold.py --strict --skill <new-skill>
python3 <skill>/scripts/run_acceptance.py
```
