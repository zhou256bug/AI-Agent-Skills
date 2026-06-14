# Changelog

本文件记录 `huazhirong-legal-affairs` 技能的版本变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

## [0.2.0] - 2026-06-13

### Added

- **P2 F/G 模式**：股权激励/期权（F）、合资/JV/股东协议/增资（G）
  - `modules/equity-incentive.md`、`modules/corporate-jv.md`
  - `references/equity-incentive-playbook.md`、`references/corporate-jv-playbook.md`
  - 墨西哥子公司增资案例锚点（股东借款 vs 增资）
- **引导配置**：`setup status` / `setup apply` / `doctor`
  - `scripts/legal_affairs_cli.py`、`scripts/legal_affairs_lib.py`
  - `references/onboarding-flow.md`、`local/credentials.env.example`
- **验收套件**：`scripts/run_acceptance.py`（结构/setup/evals/输出校验）
- evals 扩充至 **20 条**（含 F/G/S）；`validate_review_output` 增加 F/G 样例

### Changed

- 版本升至 **0.2.0**；`legal_affairs_config.py` 增加 `ENTITY_CN`/`ENTITY_HK`/`ARCHIVE_EQUITY`
- agents/bundle 增加 setup 引导说明

## [0.1.0] - 2026-06-13

### Added

- P0 首发：海外经销（A）、采购供货（B）、境内用工（C）、境外用工简引（D）、解约终止（E）、POS 合规（H）、澄清（J）
- 从 migration Playbook 改写：`negotiation-playbook`、`procurement-playbook`、`labor-cn-playbook`、`latam-distributor-law`
- 新增：`pos-contract-clauses`、`pos-payment-compliance`、`termination-strategies`、`review-output-template`、`distribution-review-workflow`
- 真实案例结构：7-Labs / Law 173、巴西顾问解约
- 单 Agent 闭环；归档 `output/合同/`；决策者「老板」可配置
- `scripts/legal_affairs_config.py`、`scripts/validate_review_output.py`
- `evaluation/run_evals.py` + `evals.json`（14 条静态用例）
- 平台脚手架：`agents/{openclaw,hermes,openai}.yaml`、`bundles/legal-affairs.hermes.yaml`
- `data/jurisdiction-index.json`（7 法域轻量索引）

### Removed

- migration 中的委派链（方律/大为/delegate_task）、`newpos/` 路径、`contract-review-anthropic`、`tabular-review-lawvable`

[0.2.0]: https://github.com/zhou256bug/AI-Agent-Skills/compare/huazhirong-legal-affairs-0.1.0...cursor/huazhirong-legal-affairs-3368
[0.1.0]: https://github.com/zhou256bug/AI-Agent-Skills/compare/main...cursor/huazhirong-legal-affairs-3368
