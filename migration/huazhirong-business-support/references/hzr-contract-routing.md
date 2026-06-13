---
name: hzr-contract-routing
description: 方律合同分类路由总表。先分类再加载 Playbook。
instance_ownership: dawei
version: 2026-06-06
---

# 方律合同路由总表

> 收到任何合同时**第一步**：填下表 → 加载对应 Playbook → 确认我方是甲方还是乙方  
> **Hermes 路径前缀**：`business/huazhirong-business-support/references/`

## 快速分类

| 合同场景 | 我方角色 | Playbook | 归档目录 |
|----------|----------|----------|----------|
| 海外经销商/代理（卖 POS） | **乙方** Vendor | `hzr-negotiation-playbook.md` | `newpos/合同/审核记录/` |
| 供应商供货（买料/代工/服务） | **甲方** Buyer | `hzr-procurement-playbook.md` | `newpos/合同/采购/审核记录/` |
| 中国境内员工劳动合同 | 用人单位 | `hzr-labor-contract-playbook.md` | `newpos/合同/人事/审核记录/` |
| 境外当地雇员（巴欧墨马印迪拜等） | 用人单位 | `hzr-labor-law-jurisdictions.md` §国别 | `newpos/合同/人事/审核记录/` |
| 商业客户 NDA | 视角色 | 经销→商务；采购→采购 Playbook | 按类型 |
| 续签多版本对比 | — | + `tabular-review-lawvable` | 同上 |

## 立场对照（防混）

| | 海外经销 | 采购供货 | 用工 |
|--|---------|---------|------|
| 华智融 | 卖方乙方 | **买方甲方** | 雇主 |
| 付款偏好 | 预收/短账期 | 验收后付/控预付 | 依法发薪 |
| 终止 | 乙方保留退出权 | **甲方**便利终止 | 法定程序 |
| 管辖 | 中国法/香港法 | 中国法/香港法 | 劳动仲裁/当地劳工机关 |
| IP | 许可给客户有限范围 | **定制归华智融** | 职务成果归单位 |

## 辅助技能

- 条款骨架：`contract-review-anthropic`（须以 Playbook 为准）
- 矩阵对比：`tabular-review-lawvable`
- 拉美经销保护法：`latam-distributor-law-cheatsheet.md`（经销专用，非采购）
