# Changelog

All notable changes to the `cross-cultural-consultant` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned (P2, deferred)

> 通用化文档抛光；**不影响技能触发与交付主路径**，合并后可择机处理。

- `README.md`：适用对象由「华智融高管」改为「中国管理者 / B2B 出海高管」；PagBank 等触发示例泛化
- `templates/A4-report-template.html`：页脚去掉 Hermes 平台字样，改为平台无关 Skill 名
- `evals.json`：补 C 来访 / E 经营 / B6 话术结构用例；将 `C-战略-沙特建团队` 更名为 `A+战略-沙特建团队`（当前路由实为 A+战略）
- `scripts/render_mobile_pdf.py`：`weekly-report` preset 标注为跨技能残留或迁出（跨文化主路径仅用 `mobile-default`）
- `SKILL.md` §十三：「老板要手机 PDF」可改为「用户要求」（可选口吻抛光）

## [0.8.1] - 2026-06-13

### Changed

- `render_mobile_pdf.py` 默认 preset `cielo` 更名为 `mobile-default`（版式不变）；SKILL §十三 文案同步
- 删除已合并的占位文件 `references/F-mode-brazil-cielo-2026-06-04.md`

## [0.8.0] - 2026-06-14

### Added

- 平台注册脚手架：`agents/openclaw.yaml`、`agents/hermes.yaml`、`agents/openai.yaml`
- `references/openclaw-hermes-registration.md`：OpenClaw / Hermes 复制即用注册文档
- `bundles/cross-cultural-consultant.hermes.yaml`：Hermes `/cross-cultural-consultant` bundle
- `evaluation/run_evals.py`：纯标准库的静态评测 / 自检 harness（校验 evals.json 结构与 module 引用）
- `scripts/run_integration_test.py`：端到端集成测试（路由、Delta、PDF）
- `CHANGELOG.md`、`.gitignore`
- SKILL.md「零、开箱即用与注册」与「十四、C 模式会后 CRM」
- C 模式 CRM：`references/crm-workflow.md`、`crm-card-note-template.md`、`crm-meeting-note-template.md`
- `scripts/ocr_card.py`（名片 OCR，可选 tesseract）

### Changed

- **定版 0.8.0**：平台解耦、单 Agent 闭环、`output/` 本地归档规范
- C 模式会后改为单 Agent 闭环：移除大为/emma/Hermes 委派；Agent 直接写 `output/crm/`
- 移除 `ericstudio` Mac 本机路径与全部 `newpos/` 引用；`pdf-trip-report-workflow.md` 与 §十三 对齐
- 去语境化（人名）：`菜头` → `老板`（`SKILL.md` 与相关 `references/`）
- 手机 PDF 统一走 `scripts/render_mobile_pdf.py`，移除 `$HERMES_HOME/tools/...` 依赖
- 归档路径统一为技能内 `output/`（出差报告 / 来访战备 / 市场 / crm）
- `SKILL.md` §九 / §十二：`v0.3.0-backup` 引用改为 `migration/cross-cultural-consultant/.v0.3.0-backup/`
- `A-mode-japan-25th-anniversary.md`、`F-mode-brazil-fernando-termination.md`：PDF 流程改为 `render_mobile_pdf.py`
- `README.md` 更新：C/E/B6、`output/` 树、`ocr_card.py`、可选依赖与自检命令

### Removed

- `references/hofstede-dimensions.json`（无效占位）——以 `data/hofstede-dimensions.json` 为唯一数据源
- 提升到仓库根的副本不含 `.v0.3.0-backup/`（历史备份在 `migration/cross-cultural-consultant/`）

### Notes

- `references/` 中华智融、9010、PagBank 等案例为高管场景设计，**有意保留**

## [0.7.1] - 2026-06-09

### Added

- A 模式参考「孟加拉 + 手机分期项目评估」：金融/分期场景须追加行业适配建议（风控结构、分期周期、推广路径、催收机制）

## [0.7.0]

### Added

- B6 话术撰写模式：为非流利英语的中国管理者设计英文话术（语用规则、篇幅控制、交付格式，见 `references/b6-speechcraft.md`），新增触发词路由

## [0.6.1]

### Added

- C 模式参考文件补全全流程环节（会前→会中→会后）、产出物清单、晚宴台卡与名片归类

### Changed

- C 模式描述更新为包含会后三环节

### Removed

- 合并重复的 F-mode-cielo 参考文件

## [0.6.0]

### Added

- C 模式（来访接待 Reverse A）与 Cielo 案例参考

## [0.5.1]

### Added

- 「解约谈判」场景路由与处理规则；巴西 Fernando 解约谈判参考案例

## [0.5.0]

### Added

- E 模式（经营分析）：诊断已投入重金的现有客户关系；巴西 PagBank 参考示例

## [0.4.0]

### Changed

- 文件结构由单 SKILL.md（~38KB）重构为主路由 + `modules/` + `frameworks/` 分层（渐进式加载）
- 出国中场景由 1 个通用 B 模式细分为 5 个子场景（B1-B5）

### Added

- D 模式（回国后复盘，两阶段：先引导提问 → 再分析）

## [0.3.0]

### Added

- 初始版本：单 SKILL.md，含 Hofstede 数据、教授 12 框架、A/B 模式（完整副本保留于 `migration/cross-cultural-consultant/.v0.3.0-backup/`）
