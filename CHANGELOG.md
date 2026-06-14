# Changelog

本仓库(`AI-Agent-Skills`)所有值得记录的变更都记在此文件。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

> 说明:各 skill 另有自己的 `CHANGELOG.md`(如 `cross-cultural-consultant/CHANGELOG.md`、`aliyun-enterprise-mail/CHANGELOG.md`),记录该 skill 的细粒度变更;本文件记录仓库级(新增/规范化/移除 skill 等)变更。

## [Unreleased]

### Added

- 仓库根专业 `README.md`(技能一览 / 注册快速开始 / 技能开发规范 / 安全与凭据)
- `cross-cultural-consultant` C 模式会后 CRM：`references/crm-workflow.md`、`crm-card-note-template.md`、`crm-meeting-note-template.md`、`scripts/ocr_card.py`（单 Agent 写 `output/crm/`，不委派外部 profile/skill）
- `cross-cultural-consultant` `scripts/run_integration_test.py`（端到端集成测试 36 项）
- 根级 `CHANGELOG.md`
- 规范化技能 `cross-cultural-consultant`(提升至仓库根,与 `aliyun-enterprise-mail` 同级):
  - 平台注册脚手架 `agents/{openclaw,hermes,openai}.yaml`、`bundles/cross-cultural-consultant.hermes.yaml`、`references/openclaw-hermes-registration.md`
  - `.gitignore`、技能级 `CHANGELOG.md`、`evaluation/run_evals.py`(纯标准库自检 harness)
- 规范化技能 `huazhirong-management-weekly-report`(提升至仓库根,独立完整):
  - vendored `scripts/render_mobile_pdf.py`(技能自带渲染器,独立可跑)、`scripts/weekly_report_config.py`(发件人/老板/公司/归档/IMAP/WEIXIN 可配置,环境变量覆盖)
  - **内置取信** `scripts/fetch_mail.py`(必备,通用 IMAP,纯标准库),不再依赖 aliyun/平台工具
  - **断点续跑编排** `scripts/run_weekly.py` + `scripts/state.py`:一条命令 fetch→compose→render→deliver,失败按期号续跑(取信成功跳取信、限流仅补推送、幂等)
  - `scripts/deliver.py` 多通道投递,新增 `wechat-bridge`(直连 hermes-weixin `POST /send` 读 200/500 真实回执,默认),另有 `wechat-media`/`wecom`/`feishu`
  - 凭据 `credentials.env.example` + `local/`(gitignore);平台脚手架 `agents/{openclaw,hermes,openai}.yaml`、`bundles/weekly-report.hermes.yaml`、`references/{openclaw-hermes-registration,delivery-channels}.md`、`.gitignore`、技能级 `CHANGELOG.md`

### Changed

- `huazhirong-management-weekly-report` **v1.0.0 定版**：补技能级 `README.md`、CHANGELOG 收口；验收 44/44
- `cross-cultural-consultant` **v0.8.1**：PDF preset `mobile-default`、删除 F-mode 占位；含 v0.8.0 定版（单 Agent CRM、`output/` 归档、平台解耦）
- `cross-cultural-consultant` C 模式会后改为单 Agent 闭环（移除大为/emma 委派；`output/crm/` + `ocr_card.py`）
- `cross-cultural-consultant` 去语境化（人名）：全技能 `菜头` → `老板`（`SKILL.md` 与 9 个 `references/` 文档，共 22 处）
- `cross-cultural-consultant` 平台解耦,实现 OpenClaw / Hermes clone 后开箱即用:
  - 手机 PDF 统一走 skill 内 `scripts/render_mobile_pdf.py`(移除 `$HERMES_HOME/tools/...` 依赖),PDF 标注为可选依赖
  - 归档输出路径由 `newpos/...` 改为可配置的 `output/...`(operative 段落)
  - 版本号对齐为 0.7.1
- `huazhirong-management-weekly-report` 平台解耦并参数化:
  - `run_acceptance.py` 重写为平台无关、可独立跑通(25 用例;render 在缺可选依赖时自动 SKIP),移除对 `$HERMES_HOME`/cron gate/iCloud 金标准的依赖
  - validator/transform/paths 参数化(老板/发件人/归档默认值不变,兼容历史「菜头」字样)
  - cron/门禁降为可选运维层(`references/cron-retry.md`);推送改为多通道投递层;归档默认 `output/`

### Fixed

- `aliyun-enterprise-mail` 注册文档与 `agents/*.yaml` 仓库名 `AI-Skills` → `AI-Agent-Skills`

### Removed

- `cross-cultural-consultant` 提升副本移除无效占位 `references/hofstede-dimensions.json` 与 `.v0.3.0-backup/`(原件仍保留于 `migration/cross-cultural-consultant/`)
- 重复目录 `migration/huazhirong-management-weekly-report2`(与 `migration/huazhirong-management-weekly-report` 逐字节相同)

### Notes

- `migration/` 保留原始迁移素材;`huazhirong-business-support` 因强耦合,待单独讨论后再规范化
- `cross-cultural-consultant` 中涉及特定同事/公司语境(菜头、emma/大为 委派、newpos/Obsidian)的案例参考文件本轮未改,留待后续讨论
- `cross-cultural-consultant` **P2 文档抛光**（README 适用对象、A4 模板 Hermes 字样、evals C/E/B6 等）已记入技能 `CHANGELOG.md` Planned 段,合并后择机处理,不阻塞发版
- `huazhirong-management-weekly-report` **P2**（`PROJECT_SOURCES` 外置、evals.json 等）已记入技能 `CHANGELOG.md` Planned 段
- `huazhirong-management-weekly-report` 的 `PROJECT_SOURCES`(项目→周报负责人)为华智融默认业务数据,可按需替换

## [0.0.0]

### Added

- 初始仓库:`LICENSE`、`README.md`
- 技能 `aliyun-enterprise-mail`(阿里企业邮箱 IMAP 读信,含对话式引导配置)
- `migration/` 导入原始技能素材(`cross-cultural-consultant`、`huazhirong-business-support`、`huazhirong-management-weekly-report`)
