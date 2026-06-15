# Changelog

本文件记录 `huazhirong-inbox-watch` 技能变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

## [0.1.2] - 2026-06-15

### Added

- vendored `scripts/render_mobile_pdf.py` + `scripts/render_scan_pdf.py`
- `references/pdf-scan-workflow.md`（手机竖版 284pt，`mobile-default`）
- `run_scan.py` 归档后自动渲 PDF；`--deliver` 微信优先推送 PDF

### Changed

- 版本升至 **0.1.2**；SKILL 铁律补手机 PDF（C 类编排合规）

## [0.1.1] - 2026-06-15

### Added

- 关注人：程晓艳、林旭伟、蔡伟旭(Eric)、万丽霞
- `watchlist_cli.py`（list/add/remove）+ `references/watchlist-management.md`
- 环境变量 `INBOX_WATCH_WATCHLIST_FILE` 可指向自定义列表路径

### Changed

- 版本升至 **0.1.1**；SKILL 路由新增 **W** 关注人管理模式

## [0.1.0] - 2026-06-15

### Added

- 独立技能 `huazhirong-inbox-watch`（slash `/inbox-watch`）
- 通用 IMAP：`check_unseen.py`、`mail_tool.py`（list/read/read_match/attachments_match）
- `run_scan.py` emoji 摘要归档 + `deliver_weixin.py` 微信推送
- `inbox_watch_cli.py` setup/doctor/scan
- `data/watchlist.json`、`data/system-sender-patterns.json`
- Cron 文档与 Agent prompt（`0 7-22/3 * * 1-5`）
- `run_acceptance.py`、`evaluation/run_evals.py`
- 平台脚手架 `agents/*.yaml`、`bundles/inbox-watch.hermes.yaml`

### Changed

- 无

### Fixed

- 无
