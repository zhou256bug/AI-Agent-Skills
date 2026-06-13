# Changelog

All notable changes to the `huazhirong-management-weekly-report` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

首个规范化(平台解耦、可独立跑通)版本,目标 1.0.0。

### Added

- `scripts/weekly_report_config.py`:集中可配置项(OWNER/SENDER_NAME/SENDER_EMAIL/SUBJECT_KEY/COMPANY/ARCHIVE_DIR),全部支持环境变量覆盖
- vendored `scripts/render_mobile_pdf.py`(含 `weekly-report` 预设),技能自带渲染器,不再依赖 `$HERMES_HOME` 或其它技能
- `scripts/deliver.py`:多通道投递层(`wechat-media` / `wecom` / `feishu`,可扩展)
- 平台脚手架:`agents/{openclaw,hermes,openai}.yaml`、`bundles/weekly-report.hermes.yaml`、`references/openclaw-hermes-registration.md`、`references/delivery-channels.md`、`.gitignore`、`CHANGELOG.md`

### Changed

- `scripts/run_acceptance.py` 重写为**平台无关、可独立跑通**的验收套件:覆盖 validator/transform/paths/config;render 用例在缺 weasyprint/PyMuPDF 时自动 SKIP;移除对 `$HERMES_HOME`、cron gate、iCloud 金标准的依赖
- `validate_weekly_report_md.py` / `transform_report_md.py` / `weekly_report_paths.py` 参数化:段标题/署名/发件人/归档路径改为读取配置(默认值不变,兼容历史「菜头」字样)
- `SKILL.md` 规范化:补 `metadata.{openclaw,hermes}` + `user-invocable`;cron/门禁降为可选运维层;推送改为多通道投递层;归档路径改为可配置 `output/`
- 归档默认目录由 iCloud `newpos/笔记/周报` 改为技能本地 `output/`(可配置)

### Removed

- 对仓库外 `$HERMES_HOME/scripts/weekly_evyn_cron_gate.py` 的硬依赖(降为可选运维文档 `references/cron-retry.md`)
- frontmatter `instance_ownership=dawei` 与指向仓库内不存在 skill 的 `related_skills`

### Notes

- `transform_report_md.py` 的 `PROJECT_SOURCES`(项目→周报负责人)为华智融默认业务数据,可按需替换
- 旧版 45 项验收(依赖 gate/iCloud)记录保留在 `references/acceptance-test-cases.md`、`references/AUDIT-REPORT.md` 作历史参考
