# A 模式 — 海外经销/代理合同

> 触发：海外经销、独家代理、POS 终端销售、Law 173、7-Labs、续签对比  
> 我方角色：**乙方（Vendor）**

## 加载清单

1. `references/negotiation-playbook.md` — Tier 1/2/3 标准立场
2. `references/latam-distributor-law.md` — 拉美保护法（如适用）
3. `references/distribution-review-workflow.md` — 续签对比与市场验证
4. `references/pos-contract-clauses.md` — POS 产品条款（如涉及硬件/SDK）
5. `frameworks/legal-reasoning.md` — 推理框架

## 执行步骤

### 1. 确认分类

填 `contract-routing.md` → 确认「海外经销 / 我方乙方」。

### 2. 提取与对比

- 提取合同全文
- **续签**：立即做新旧差异表（不先问要不要对比）
- 重点标记：新增本土保护法条款（Law 173 等）

### 3. Tier 评估

按 `negotiation-playbook.md` 逐条评估：

**Tier 1 必查**：
- Law 173 / 登记条款 + just cause 终止条件
- 管辖法与仲裁
- IP 许可范围
- 独家与最低采购量（15% 法则）
- 关键附件完整性

**Tier 2 重点**：
- MFN 区域限制
- 付款条件
- 终止与库存
- 赔偿上限

### 4. 可选市场验证

老板要求时，估算区域 POS 需求量并与最低采购量对比。

### 5. 输出

按 `review-output-template.md` A 模式输出，归档 `output/合同/审核记录/`。

## 案例锚点

**7-Labs SRL（多米尼加）**：
- 2018 旧约无 Law 173
- 2026 V2 新增 Law 173 + 登记授权 → 典型 🔴
- 最终策略：保留 Law 173 + 写入 6 项 just cause + 管辖法不受影响

## 升级条件

- 对方拒改 Tier 1 → 建议暂停签署，升级老板
- 制裁/主体异常 → 建议外部律师
- 新国别法律不确定 → 标注「建议外部律师确认」
