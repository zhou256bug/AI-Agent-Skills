# Changelog

本文件记录 `huazhirong-inbox-watch` 技能变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

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
