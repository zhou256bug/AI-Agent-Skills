# Changelog

All notable changes to the `huazhirong-management-weekly-report` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added（独立完整化：内置取信 + 断点续跑编排）

- `scripts/fetch_mail.py`:**必备**取信(通用 IMAP,纯标准库),`SINCE` + 发件人/主题过滤 + 递归取 xlsx
- `scripts/run_weekly.py`:一条命令编排 fetch→compose→render→deliver,**失败断点续跑**(状态 `STATE:DELIVERED/ALREADY_DONE/NEED_COMPOSE/FETCH_WAIT/DELIVER_RETRY/FAIL_NOTIFY`)
- `scripts/state.py`:按期号 N 的状态文件 + 产物探测(fetch/compose/render/deliver)
- `deliver.py` 新增 `wechat-bridge` 通道:直连 hermes-weixin `POST /send`,**读 200/500 真实回执**(限流=可重试),自动化默认
- 凭据 `credentials.env.example` + `local/`(gitignore):IMAP + WEIXIN 配置
- `weekly_report_config.py` 扩展 IMAP/WEIXIN 配置 + `local/credentials.env` 加载器
- `run_acceptance.py` 增取信纯函数 + 状态机/续跑用例(取信续跑、限流仅补推送、幂等、NEED_COMPOSE)
- `run_acceptance.py` 增**微信发文件契约**用例(WX01–WX06):本地 mock bridge 断言 `{to, content非空, media_path绝对路径}` + 200→成功/500→可重试/文件缺失→硬错误
- `deliver.py` wechat-bridge **发送前校验文件存在且非空**(bridge 以自身文件系统解析 media_path)
- `references/delivery-channels.md` 增「微信发文件机制与部署要求」(完整链路 + 支持类型 + 同机/共享卷要求 + 回执)

### Notes（取信设计）

- 取信不再依赖 `aliyun-enterprise-mail` 或平台工具,技能自给自足(任意 IMAP)
- 微信投递默认走 bridge 直连以获取回执;`wechat-media`(MEDIA 行,无回执)仅作交互兜底

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
