# 合同分类路由总表

> 收到任何合同时**第一步**：填下表 → 加载对应 Playbook → 确认我方是甲方还是乙方

## 快速分类

| 合同场景 | 我方角色 | Playbook | 归档目录 |
|----------|----------|----------|----------|
| 海外经销商/代理（卖 POS） | **乙方** Vendor | `negotiation-playbook.md` | `output/合同/审核记录/` |
| 供应商供货（买料/代工/服务） | **甲方** Buyer | `procurement-playbook.md` | `output/合同/采购/审核记录/` |
| 中国境内员工劳动合同 | 用人单位 | `labor-cn-playbook.md` | `output/合同/人事/审核记录/` |
| 境外当地雇员（巴欧墨马印迪拜等） | 用人单位 | `data/jurisdiction-index.json` + 升级当地律师 | `output/合同/人事/审核记录/` |
| 商业客户 NDA | 视角色 | 经销→商务；采购→采购 Playbook | 按类型 |
| 顾问/服务解约终止 | 视合同角色 | `termination-strategies.md` | `output/合同/审核记录/` |
| 续签多版本对比 | — | + `distribution-review-workflow.md` | 同上 |

## 立场对照（防混）

| | 海外经销 | 采购供货 | 用工 |
|--|---------|---------|------|
| 华智融 | 卖方乙方 | **买方甲方** | 雇主 |
| 付款偏好 | 预收/短账期 | 验收后付/控预付 | 依法发薪 |
| 终止 | 乙方保留退出权 | **甲方**便利终止 | 法定程序 |
| 管辖 | 中国法/香港法 | 中国法/香港法 | 劳动仲裁/当地劳工机关 |
| IP | 许可给客户有限范围 | **定制归华智融** | 职务成果归单位 |

## 辅助参考

- 拉美经销保护法：`latam-distributor-law.md`（经销专用，非采购）
- POS 合规：`pos-contract-clauses.md`、`pos-payment-compliance.md`
- 输出模板：`review-output-template.md`
