# Changelog

本仓库(`AI-Agent-Skills`)所有值得记录的变更都记在此文件。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

> 说明:各 skill 另有自己的 `CHANGELOG.md`(如 `cross-cultural-consultant/CHANGELOG.md`、`aliyun-enterprise-mail/CHANGELOG.md`),记录该 skill 的细粒度变更;本文件记录仓库级(新增/规范化/移除 skill 等)变更。

## [Unreleased]

### Added

- 仓库根专业 `README.md`(技能一览 / 注册快速开始 / 技能开发规范 / 安全与凭据)
- 根级 `CHANGELOG.md`
- 规范化技能 `cross-cultural-consultant`(提升至仓库根,与 `aliyun-enterprise-mail` 同级):
  - 平台注册脚手架 `agents/{openclaw,hermes,openai}.yaml`、`bundles/cross-cultural-consultant.hermes.yaml`、`references/openclaw-hermes-registration.md`
  - `.gitignore`、技能级 `CHANGELOG.md`、`evaluation/run_evals.py`(纯标准库自检 harness)

### Changed

- `cross-cultural-consultant` 平台解耦,实现 OpenClaw / Hermes clone 后开箱即用:
  - 手机 PDF 统一走 skill 内 `scripts/render_mobile_pdf.py`(移除 `$HERMES_HOME/tools/...` 依赖),PDF 标注为可选依赖
  - 归档输出路径由 `newpos/...` 改为可配置的 `output/...`(operative 段落)
  - 版本号对齐为 0.7.1

### Fixed

- `aliyun-enterprise-mail` 注册文档与 `agents/*.yaml` 仓库名 `AI-Skills` → `AI-Agent-Skills`

### Removed

- `cross-cultural-consultant` 提升副本移除无效占位 `references/hofstede-dimensions.json` 与 `.v0.3.0-backup/`(原件仍保留于 `migration/cross-cultural-consultant/`)
- 重复目录 `migration/huazhirong-management-weekly-report2`(与 `migration/huazhirong-management-weekly-report` 逐字节相同)

### Notes

- `migration/` 保留原始迁移素材;`huazhirong-business-support` 与 `huazhirong-management-weekly-report` 因强耦合,待单独讨论后再规范化
- `cross-cultural-consultant` 中涉及特定同事/公司语境(菜头、emma/大为 委派、newpos/Obsidian)的案例参考文件本轮未改,留待后续讨论

## [0.0.0]

### Added

- 初始仓库:`LICENSE`、`README.md`
- 技能 `aliyun-enterprise-mail`(阿里企业邮箱 IMAP 读信,含对话式引导配置)
- `migration/` 导入原始技能素材(`cross-cultural-consultant`、`huazhirong-business-support`、`huazhirong-management-weekly-report`)
