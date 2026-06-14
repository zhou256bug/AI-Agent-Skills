# 华智融法务技能

华智融合同审核 Agent Skill — 海外经销、采购供货、境内用工、顾问解约、POS 合规、股权激励、合资增资。

**版本**：0.2.0 | **slash**：`/legal-affairs` | **凭据**：无（setup 配置业务偏好）

## 能力范围

| 模式 | 场景 | 我方角色 |
|------|------|----------|
| A | 海外经销/代理（POS） | 乙方 Vendor |
| B | 采购供货 | 甲方 Buyer |
| C | 中国境内用工 | 用人单位 |
| D | 境外用工（简引） | 升级当地律师 |
| E | 解约/终止 | 视合同 |
| F | 股权激励/期权/ESOP | 授予方 |
| G | 合资/JV/股东协议/增资 | 股东/投资方 |
| H | POS 合规（PCI/SDK/认证） | 速查 |
| J | 意图澄清 | — |
| S | setup 引导配置 | — |

## 设计原则

- **单 Agent 闭环** — 禁止委派
- **先分类再立场** — 不可混用 Playbook
- **续签必对比** — 7-Labs / Law 173 案例结构
- **归档 `output/`** — setup 可配置路径
- **引导配置** — `setup status` / `setup apply`（无密码）

## 快速开始

```bash
# 验收（推荐）
python3 huazhirong-legal-affairs/scripts/run_acceptance.py

# 引导配置
python3 huazhirong-legal-affairs/scripts/legal_affairs_cli.py setup status
python3 huazhirong-legal-affairs/scripts/legal_affairs_cli.py setup apply --verify

# 评测
python3 huazhirong-legal-affairs/evaluation/run_evals.py
```

### Hermes

```bash
hermes chat --toolsets terminal,skills -q "/legal-affairs 墨西哥子公司增资，股东借款还是增资好"
```

## 配置

| 环境变量 | 默认 | 含义 |
|----------|------|------|
| `LEGAL_AFFAIRS_DECISION_MAKER` | 老板 | 决策者称呼 |
| `LEGAL_AFFAIRS_COMPANY` | 华智融 | 公司名 |
| `LEGAL_AFFAIRS_ARCHIVE_DIR` | `<skill>/output` | 归档根目录 |
| `LEGAL_AFFAIRS_ENTITY_CN` | 深圳华智融科技股份有限公司 | 境内签约主体 |
| `LEGAL_AFFAIRS_ENTITY_HK` | NEW POS GLOBAL HOLDING (HONG KONG) LIMITED | 境外签约主体 |

详见 `references/onboarding-flow.md`。

## 免责声明

本 skill 输出为**内部合同初审意见**，不构成正式法律意见。
