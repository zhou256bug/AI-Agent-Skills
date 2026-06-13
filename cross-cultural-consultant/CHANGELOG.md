# Changelog

All notable changes to the `cross-cultural-consultant` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 平台注册脚手架：`agents/openclaw.yaml`、`agents/hermes.yaml`、`agents/openai.yaml`
- `references/openclaw-hermes-registration.md`：OpenClaw / Hermes 复制即用注册文档
- `bundles/cross-cultural-consultant.hermes.yaml`：Hermes `/cross-cultural-consultant` bundle
- `evaluation/run_evals.py`：纯标准库的静态评测 / 自检 harness（校验 evals.json 结构与 module 引用）
- `CHANGELOG.md`、`.gitignore`
- SKILL.md 新增「零、开箱即用与注册」段落

### Changed

- 平台解耦：手机 PDF（SKILL.md §十三）统一走 skill 内 `scripts/render_mobile_pdf.py`，移除 `$HERMES_HOME/tools/...` 路径依赖
- 归档输出路径由 `newpos/...` 改为可配置的 `output/...`（operative 段落；历史案例参考文件保持原样）
- 版本号对齐为 0.7.1（frontmatter / 正文标题 / 输出脚注 / README / evals.json 一致）

### Removed

- `references/hofstede-dimensions.json`（无效占位符，非合法 JSON，含本机绝对路径）——以 `data/hofstede-dimensions.json` 为唯一数据源
- 提升到仓库根的副本不含 `.v0.3.0-backup/`（历史备份仍保留在 `migration/cross-cultural-consultant/`）

### Notes（待后续讨论，本轮未改）

- 部分参考案例文件仍含特定同事/公司语境（菜头、emma/大为 委派、newpos/Obsidian 路径），按约定留待单独讨论后再处理

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
