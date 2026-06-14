# B 模式 — 采购供货合同

> 触发：采购、供货、供应商、OEM/ODM、元器件、委外加工、我方买方  
> 我方角色：**甲方（Buyer）**

## 加载清单

1. `references/procurement-playbook.md` — Tier 1/2/3 买方立场
2. `references/pos-contract-clauses.md` — POS 元器件/整机采购（如适用）
3. `frameworks/legal-reasoning.md`

## 执行步骤

### 1. 确认分类

填 `contract-routing.md` → 确认「采购供货 / 我方甲方」。

⚠️ **防混**：不可套用经销 Playbook（乙方立场相反）。

### 2. 识别采购类型

| 类型 | 额外关注 |
|------|----------|
| 元器件/芯片 | 真伪、ECCN、长单 cancel |
| OEM/ODM 整机 | 认证责任、不良率、返修 |
| 结构件/包材 | 模具权属 |
| 软件/SaaS | 许可、SLA、DPA、退出迁移 |

### 3. Tier 评估

**Tier 1 必查**：
- 标的规格与验收程序
- 交付与 Incoterms
- 质保（≥ 12 个月）
- 定制 IP 归华智融
- 付款（控预付）
- 华智融便利终止权
- 模具/专用物料归属

### 4. 输出

按 `review-output-template.md` B 模式输出，归档 `output/合同/采购/审核记录/`。

## 升级条件

- 100% 预付无担保 → 🔴，升级老板
- 定制 IP 归供方 → 🔴，暂停签署
- 出口管制/制裁风险 → 建议合规确认
