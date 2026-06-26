# 技能模板目录

新建技能时：

1. 阅读 [`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md)（**原子技能优先**）
2. 阅读 [`ATOMIC-SKILL-GUIDE.md`](ATOMIC-SKILL-GUIDE.md)
3. 复制 [`CHECKLIST.md`](CHECKLIST.md) 到 PR 描述逐项勾选

## 参考（按类型）

| 类型 | 参考 skill |
|------|------------|
| **B 原子工具** | `aliyun-enterprise-mail/` — IMAP + setup |
| **A 领域知识** | `cross-cultural-consultant/`、`huazhirong-legal-affairs/` |
| **E 编排例外** | `huazhirong-management-weekly-report/`（新需求勿模仿） |

组合逻辑放 **Hermes bundle** 或 **`docs/cron-prompts/`**，不要建 monolith skill。

```bash
python3 scripts/validate_skill_scaffold.py
```
