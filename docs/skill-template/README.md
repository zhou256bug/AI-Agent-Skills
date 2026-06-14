# 技能模板目录

新建技能时：

1. 阅读 [`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md)
2. 复制 [`CHECKLIST.md`](CHECKLIST.md) 到 PR 描述逐项勾选
3. 参考已有技能目录结构：
   - `cross-cultural-consultant/` — 知识类 + PDF
   - `aliyun-enterprise-mail/` — 凭据 + setup
   - `huazhirong-management-weekly-report/` — 编排 + acceptance
   - `huazhirong-legal-affairs/` — 审核 + emoji + PDF + setup

仓库级脚手架校验：

```bash
python3 scripts/validate_skill_scaffold.py
```
