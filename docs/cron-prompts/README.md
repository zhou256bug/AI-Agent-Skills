# Cron Prompt 模板目录

本目录存放 **Hermes / OpenClaw cron 任务的内联 prompt**，属于**平台编排层**，**不是** Skill。

## 原则

- 多步流水线（读信 → 摘要 → PDF → 推送）写在这里或 Hermes bundle，**不要**建 monolith skill
- Prompt 内引用**原子 skill** 的脚本路径
- 见 [`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md) §零、§七

## 待补充示例

| 文件 | 场景 |
|------|------|
| `inbox-scan-weekday.md` | 工作日每 3 小时 UNSEEN 扫描 + 推送 |

迁移 `huazhirong-inbox-watch/references/agent-cron-prompt.md` 内容时，应**拆步骤**并引用 `aliyun-enterprise-mail` 等原子 skill，而非 monolith skill。
