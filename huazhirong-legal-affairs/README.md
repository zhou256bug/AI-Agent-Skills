# 华智融法务技能

华智融合同审核 Agent Skill — 海外经销、采购供货、境内用工、顾问解约、POS 合规速查。

**版本**：0.1.0 | **slash**：`/legal-affairs` | **凭据**：无

## 能力范围（P0）

| 模式 | 场景 | 我方角色 |
|------|------|----------|
| A | 海外经销/代理（POS） | 乙方 Vendor |
| B | 采购供货 | 甲方 Buyer |
| C | 中国境内用工 | 用人单位 |
| D | 境外用工（简引） | 升级当地律师 |
| E | 解约/终止 | 视合同 |
| H | POS 合规（PCI/SDK/认证） | 速查 |
| J | 意图澄清 | — |

**P2 延后**：股权/JV、setup 引导配置

## 设计原则

- **单 Agent 闭环** — 禁止委派外部 Agent 或其他 skill
- **先分类再立场** — 经销乙方 ≠ 采购甲方 ≠ 用人单位
- **续签必对比** — 7-Labs / Law 173 案例结构
- **归档 `output/`** — 可配置 `LEGAL_AFFAIRS_ARCHIVE_DIR`
- **真实案例** — 华智融主体、15% 法则、老板决策

## 快速开始

```bash
# 自检
python3 huazhirong-legal-affairs/evaluation/run_evals.py
python3 huazhirong-legal-affairs/scripts/validate_review_output.py --sample
```

### Hermes

```bash
hermes chat --toolsets terminal,skills -q "/legal-affairs 7-Labs 续签新增了 Law 173，帮我审核"
```

注册见 `references/openclaw-hermes-registration.md`。

## 目录结构

```
huazhirong-legal-affairs/
├── SKILL.md              # 路由 + 全局规则
├── modules/              # A/B/C/E 场景模板
├── references/           # Playbook + 案例
├── frameworks/           # 推理框架
├── data/                 # 法域索引（D 模式）
├── scripts/              # 配置 + 输出校验
└── evaluation/           # 静态自检 harness
```

## 配置

| 环境变量 | 默认 | 含义 |
|----------|------|------|
| `LEGAL_AFFAIRS_DECISION_MAKER` | 老板 | 决策者称呼 |
| `LEGAL_AFFAIRS_COMPANY` | 华智融 | 公司名 |
| `LEGAL_AFFAIRS_ARCHIVE_DIR` | `<skill>/output` | 归档根目录 |

## 免责声明

本 skill 输出为**内部合同初审意见**，不构成正式法律意见。涉诉或跨境争议须由持证律师确认。
