# Changelog

All notable changes to the `huazhirong-management-weekly-report` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned (P2, deferred)

> 通用化抛光；**不影响当前 1.0.0 主路径**，合并后择机处理。

- `transform_report_md.py`：`PROJECT_SOURCES` 外置为 `data/project-sources.json` 或可配置路径
- 补 `evals.json` + 结构评测 harness（对标 `cross-cultural-consultant`）
- README 适用对象表述进一步泛化（默认值仍可为华智融实例）
- 目录/skill 名去公司前缀（如 `management-weekly-report`）——架构级，需单独确认

## [1.0.0] - 2026-06-13

首个规范化定版：平台解耦、可独立跑通、一条命令编排 + 断点续跑。

### Added

- `scripts/weekly_report_config.py`：集中可配置项（OWNER/SENDER/COMPANY/ARCHIVE/IMAP/WEIXIN），环境变量 + `local/credentials.env` 覆盖
- vendored `scripts/render_mobile_pdf.py`（含 `weekly-report` 预设），技能自带渲染器
- `scripts/deliver.py`：多通道投递（`wechat-bridge` / `wechat-media` / `wecom` / `feishu`）
- `scripts/fetch_mail.py`：**必备**取信（通用 IMAP，纯标准库）
- `scripts/run_weekly.py` + `scripts/state.py`：fetch→compose→render→deliver 编排 + 断点续跑
- `deliver.py` `wechat-bridge` 通道：直连 hermes-weixin `POST /send`，读 200/500 真实回执
- 凭据 `credentials.env.example` + `local/`（gitignore）
- `scripts/run_acceptance.py`：平台无关验收套件（44 项，含取信纯函数、状态机续跑、微信发文件契约 WX01–WX06）
- 平台脚手架：`agents/{openclaw,hermes,openai}.yaml`、`bundles/weekly-report.hermes.yaml`
- `references/{openclaw-hermes-registration,delivery-channels,cron-retry,content-format,email-and-xlsx}.md`
- `README.md`、`.gitignore`、`CHANGELOG.md`

### Changed

- `validate_weekly_report_md.py` / `transform_report_md.py` / `weekly_report_paths.py` 参数化（段标题/署名/发件人/归档读配置）
- `SKILL.md` 规范化：补 `metadata.{openclaw,hermes}` + `user-invocable`；cron 降为可选运维层
- 归档默认由 iCloud `newpos/笔记/周报` 改为技能本地 `output/`（可配置）

### Removed

- 对 `$HERMES_HOME/scripts/weekly_evyn_cron_gate.py` 的硬依赖（降为 `references/cron-retry.md`）
- frontmatter `instance_ownership=dawei` 与无效 `related_skills`

### Notes

- `transform_report_md.py` 的 `PROJECT_SOURCES` 为华智融默认业务数据，可按需替换（P2 计划外置）
- 旧版 45 项验收（依赖 gate/iCloud）保留在 `references/acceptance-test-cases.md`、`references/AUDIT-REPORT.md` 作历史参考
- 取信不再依赖 `aliyun-enterprise-mail`；微信默认走 bridge 以获取回执
