---
name: fanglv-skills-audit-report
description: 方律技能体系审计报告与修正记录。
instance_ownership: dawei
version: 2026-06-06
---

# 方律技能体系审计报告（2026-06-06）

## 审计范围

- Playbook 五件套 + routing
- `contract-review-anthropic`、`tabular-review-lawvable`
- `fanglv/SOUL.md`、`huazhirong-business-support/SKILL.md`
- `overseas-contract-review-detail.md`

## 发现的问题与修正

| # | 问题 | 严重度 | 修正 |
|---|------|--------|------|
| 1 | `contract-review-anthropic` 正文仍写「仅海外经销、我方乙方」，与采购/用工路由矛盾 | 🔴 | 重写适用边界；用工明确不走商事框架 |
| 2 | Redline「依据」硬编码 `hzr-negotiation-playbook` | 🟡 | 改为「所加载 Playbook 章节」 |
| 3 | 谈判 Tier 1 仅列经销条款，采购甲方无对应 | 🟡 | 分经销/采购两套 Tier 1 |
| 4 | `overseas-contract-review-detail` Step 3 重复标题、条目 1 断裂 | 🟡 | 合并为连续编号 |
| 5 | 劳动 Playbook 写「甲方=用人单位」易与采购甲方混淆 | 🟡 | 改为「用人单位/雇主」 |
| 6 | `fanglv/SOUL` 技能路径 `references/...` 不完整 | 🟡 | 统一为 `business/huazhirong-business-support/references/...` |
| 7 | `fanglv/SOUL` §6 留痕仅写经销目录 | 🟡 | 分经销/采购/人事三路归档 |
| 8 | 风险等级表仅覆盖经销场景 | 🟡 | 增加采购、用工示例行 |
| 9 | `hzr-procurement-playbook` 正文用 RED 与 🟢🟡🔴 混用 | 🟢 | 输出格式已统一 emoji；正文保留 RED 作内部标签可接受 |
| 10 | `hzr-contract-routing` 未写 Hermes 完整路径 | 🟢 | 补充路径前缀说明 |
| 11 | `fanglv/SOUL`、根 `SOUL` 写 `hermes profile run`，CLI 无此子命令 | 🔴 | 方律改为 `delegate_task` / `hermes -p fanglv chat -q`；与 business-support §委派 对齐 |
| 12 | 用工合同误走 Anthropic 商事赔偿/indemnity 框架 | 🟡 | `contract-review-anthropic` 增加「劳动不适用」边界 |
| 13 | `tabular-review` 采购矩阵列缺失 | 🟢 | 补充采购默认列 |

## 未改项（已知限制）

- 多国用工速查为初审清单，不构成法律意见；复杂案件仍须当地律师。
- Playbook 中采购/经销数字底线（预付比例、违约金比例）为建议值，待采购/菜头确认后可写入模板库。
- `tabular-review-lawvable` 仍含 AGPL-3.0 许可证；仅内部使用，未再分发。

## 优先级链（审计确认）

```
hzr-contract-routing（分类）
  → 专用 Playbook（经销 / 采购 / 用工）
    → contract-review-anthropic（仅商事；劳动跳过）
      → tabular-review-lawvable（续签矩阵）
```

**禁止**：无 Playbook 时按 Anthropic/欧美 SaaS 默认标准出结论。

## 委派命令（审计确认有效）

| 场景 | 命令 |
|------|------|
| Gateway 大为 | `delegate_task(goal=方律审核…, context=路由+Playbook+合同路径)` |
| CLI 一次性 | `hermes -p fanglv chat -q "先读 hzr-contract-routing…"` |
| ❌ 无效 | `hermes profile run fanglv`（`hermes profile --help` 无 `run`） |

**2026-06-06 续**：三团队（大为/高阳/大喵）全部 SOUL + 下属 profile + Obsidian 架构文档已统一委派语法。见 Obsidian `三团队委派语法统一说明.md`。
