# Changelog

本文件记录 `huazhirong-legal-affairs` 技能的版本变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

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

[0.1.0]: https://github.com/zhou256bug/AI-Agent-Skills/compare/main...cursor/huazhirong-legal-affairs-3368
