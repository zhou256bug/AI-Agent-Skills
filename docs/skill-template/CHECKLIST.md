# 新技能上线 Checklist

> 完整说明见 [`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md)

## 技能信息

- 技能名：`________________`
- 类型：□ A 知识/审核  □ B 凭据工具  □ C 编排自动化  □ D 纯数据/校验
- slash 命令：`________________`

## 硬性项（全部技能）

- [ ] `SKILL.md`（frontmatter + 路由 + 版本）
- [ ] `README.md`
- [ ] `CHANGELOG.md`
- [ ] `.gitignore`（`output/`、`local/credentials.env`）
- [ ] `agents/{openclaw,hermes,openai}.yaml`
- [ ] `references/openclaw-hermes-registration.md`
- [ ] `scripts/*_config.py` 或文档说明无需配置
- [ ] 单 Agent 闭环（无委派）
- [ ] `run_acceptance.py` 或 `evals.json` + `run_evals.py`
- [ ] `python3 scripts/validate_skill_scaffold.py` 通过
- [ ] 根 `README.md` 技能表已更新
- [ ] 根 `CHANGELOG.md` [Unreleased] 已追加

## 按类型追加

### 有凭据或个性化（B/C 或 A 可选）

- [ ] `setup status` / `setup apply` / `doctor`
- [ ] `references/onboarding-flow.md`
- [ ] `local/credentials.env.example`

### 有用户报告输出（A/C）

- [ ] `references/emoji-output-guide.md`
- [ ] 输出模板含 `📌` `🔴🟡🟢` `👉`

### 有长报告 / 手机阅读（A/C）

- [ ] `scripts/render_mobile_pdf.py`（可 vendored）
- [ ] `scripts/render_*_pdf.py` 封装（推荐）
- [ ] `references/pdf-*-workflow.md`
- [ ] `SKILL.md` PDF 专节 + 可选依赖声明

## PR 合并前命令

```bash
python3 scripts/validate_skill_scaffold.py
python3 <skill>/scripts/run_acceptance.py
# 或
python3 <skill>/evaluation/run_evals.py
```
