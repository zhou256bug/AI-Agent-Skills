# 原子技能设计指引

> 宪法全文：[`../SKILL-DESIGN-STANDARDS.md`](../SKILL-DESIGN-STANDARDS.md)

OpenClaw / Hermes / Cursor 的 Skill 机制本质是 **渐进式加载**：Agent 按触发词挂载**小文件、小能力**。  
本仓库 **默认只建原子 skill**；多步业务由 **Agent + bundle + cron prompt** 组合。

---

## 1. 判断是否够「原子」

回答三问，任一否 → 继续拆：

| 问题 | 期望 |
|------|------|
| 能否用**一句话**说清能力？ | 「读 IMAP 未读并输出结构化文本」✅ |
| 去掉其他 skill，能否单独 demo？ | 是 ✅ |
| `Use when` 是否只有**一类**触发？ | 「读邮件、IMAP、收件箱」✅ / 「读邮件并推送微信 cron」❌ |

---

## 2. 四种类型怎么选

| 类型 | 何时选 | 例子 |
|------|--------|------|
| **B 原子工具** | 协议/CLI/单一 IO | 读信、发微信、渲 PDF、watchlist CRUD |
| **A 领域知识** | 单领域 Playbook，多 mode 仍属同一领域 | 合同审核、跨文化顾问 |
| **D 数据/校验** | 纯 JSON + validator | 法域索引、输出校验器 |
| **E 编排例外** | 必须有状态机/断点续跑，且 PR 获批 | weekly-report |

**不要**因为「用户想要一键 cron」就建 E 类 monolith；cron 是 **prompt**，不是 skill。

---

## 3. 组合模式

### 3.1 用户对话

```
用户：扫描未读并推微信
Agent：
  1. 加载 aliyun-enterprise-mail → check_unseen
  2. （可选）format 脚本或 A 类模板 skill
  3. 加载 mobile-pdf skill → render
  4. 加载 weixin-deliver → POST /send
```

### 3.2 Hermes bundle

`bundles/inbox-scan.hermes.yaml` 列出多个 `skills:` + 短 `instruction`，**不**新建 `inbox-watch-monolith`。

### 3.3 Cron prompt

放在 `docs/cron-prompts/<name>.md`，逐步写 terminal 命令，引用原子 skill 路径。

---

## 4. skill 内可选文件

`references/composes-with.md` 示例：

```markdown
# 可组合技能（不自动执行）

| 场景 | 组合 |
|------|------|
| 扫描推送 | 本 skill → mobile-pdf-render → weixin-deliver |
| 周报 | 用户切换 `/weekly-report` |
```

---

## 5. 反例（勿建）

- `huazhirong-inbox-watch` 式：IMAP + watchlist + cron 文档 + PDF + 微信 + emoji 全包  
- migration 总入口 `business-support` 委派链  
- description 写：`Use when email cron scan push pdf weixin setup ...`

---

## 6. 新建原子 skill 最小步骤

1. 定类型 B/A/D  
2. 复制 [`CHECKLIST.md`](CHECKLIST.md)  
3. 只实现**一件事**的 CLI + `run_acceptance.py`  
4. 需组合时写 composes-with / 提 bundle PR，**不扩 SKILL  scope**
