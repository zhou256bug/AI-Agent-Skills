# OA看板数据管线

## 总流程

每日7:00自动执行：
1. 拉取近3天OA邮件 → `fetch_oa_quick.py`
2. 生成看板数据 → `gen_dashboard_data.py`（自动去重）

## 拉取规则

- **脚本位置**: `/Users/ericstudio/.hermes-huazhirong/tools/fetch_oa_quick.py`
- **搜索范围**: 最近3天（自"3天前"起搜），脚本无重复下载
- **搜索条件**: SINCE 日期搜索全部邮件，本地按主题过滤"每日发货明细统计"和"海外销售欠款提醒"
- **OA每天都有邮件**，不分工作日和周末

## 看板生成 — 发货去重规则

- **脚本位置**: `/Users/ericstudio/.hermes-huazhirong/tools/gen_dashboard_data.py`
- **发货数据**: OA每天发的是增量数据（单日明细），不是全量快照。需要累加所有文件
- **去重规则（已修复 2026-06-01）**:
  1. 排除文件名含"每日"或"每日发货明细统计"前缀的文件（同一份数据有两个副本：`发货_记录_日期.xls` 和 `每日_记录_日期.xls`，内容完全相同）
  2. **按MD5 hash去重** — 某些日期下载时产生了`_1`、`_1_2`等重复副本（如 `20260504_发货_xxx_1.xls`），必须全部排除
  3. 去重后只剩唯一文件列表，再逐文件累加
- **欠款数据**: 合并所有欠款xls文件，按订单号 order_no 去重保留最后出现记录

## 产出

- `data.json`: `/Users/ericstudio/Library/Mobile Documents/com~apple~CloudDocs/newpos/销售/OA数据/dashboard/data.json`
- 看板服务: `python3 -m http.server 8080` 从该目录启动

## Cron

- job_id: `511cfc79b875`（每日更新）
- job_id: `814e0b2df5b2`（邮件监控，每3小时）
