# Cross-Cultural Consultant Skill

> **版本**:v0.4.0
> **数据快照**:2026-05-30
> **适用对象**:中国管理者出国全程伴侣——出国前/出国中/回国后三段式

---

## 这个 skill 解决什么

针对中国管理者真实出国流程的三段需求:

| 阶段 | 你的需求 | skill 给你 |
|------|---------|-----------|
| **出国前** | 文化画像 + 踩坑清单 | A 模式:完整报告 + 中国人最易踩的 3 个坑 + checklist |
| **出国中** | 场景化问答 | B1 餐桌 / B2 谈判 / B3 送礼 / B4 实时解读 / B5 突发救场 |
| **回国后** | 复盘 + 下次改进 | D 模式:先引导提问 → 再分析 → 给具体改进 |

---

## 知识基础

- **Hofstede 六维度数据库**(119 国,The Culture Factor)
- **港大 EMBA6611(张轶文教授)12 条决策框架** + 学员国家实战分享
- **Kluckhohn 六维价值取向理论**
- **Hall 高/低语境沟通理论**

---

## 目录结构

```
cross-cultural-consultant/
├── SKILL.md                  # 主路由(精简,~240 行)
├── data/
│   └── hofstede-dimensions.json   # 119 国六维数据
├── frameworks/               # 知识库(按需引用)
│   ├── 12-frameworks.md           # 教授 12 框架(按 4 组分)
│   ├── kluckhohn.md               # Kluckhohn 六维
│   └── hall-context.md            # Hall 高/低语境
├── modules/                  # 场景模板(按触发词加载)
│   ├── before-travel.md           # 出国前画像
│   ├── during-dining.md           # 餐桌
│   ├── during-negotiation.md      # 谈判/合同
│   ├── during-gifting.md          # 送礼
│   ├── during-meeting.md          # 会议实时解读
│   ├── during-crisis.md           # 突发救场
│   └── after-trip.md              # 复盘
├── examples/                 # 输出示范
│   ├── A-mode-japan.md            # A 模式:日本画像
│   ├── B-mode-germany.md          # B 模式:德国谈判(v0.3 通用版,保留)
│   ├── B1-dining-japan.md         # B1 餐桌:日本饭局
│   ├── B2-negotiation-after-dinner.md  # B2 谈判:饭桌后推进
│   ├── C-mode-saudi.md            # C 模式:沙特建团队
│   ├── D-debrief-japan.md         # D 复盘:日本谈崩
│   └── null-dimensions.md         # 数据缺失兜底
├── evaluation/
│   └── run_evals.py               # 自动评测脚本
├── .v0.3.0-backup/           # v0.3.0 完整备份(可回退)
├── README.md / LICENSE / evals.json
```

---

## 设计原则:渐进式加载

主 SKILL.md 只放路由(~240 行),**不在每次对话都读 38KB 全部内容**。模型按触发词只加载相关 module 文件。frameworks/ 只在被 module 引用时加载。

这是 Claude Skill 推荐的 progressive disclosure 模式,显著降低上下文消耗。

---

## 安装方式

### 方式一:Claude Code (CLI)
```bash
cp -r cross-cultural-consultant ~/.claude/skills/
```

### 方式二:Claude Desktop / Claude.ai
将整个文件夹压缩为 `cross-cultural-consultant.zip`,在 Project 中上传,系统提示词写一句"涉及跨国商务/海外团队管理时使用此 skill"。

### 方式三:Hermes Agent
将目录放到 Hermes 的 `external_skills_dirs` 配置路径下。

### 方式四:自定义 Agent / SDK
- `SKILL.md` 作为 system prompt 加载
- `data/hofstede-dimensions.json` 作为可读文件挂载
- `modules/` 和 `frameworks/` 作为知识库目录挂载

---

## 触发关键词速查

### 出国前(A 模式)
- "下周去日本"
- "给我日本完整画像"
- "日本怎么样"

### 出国中(B1-B5)
- **B1 餐桌**:"今晚请日本客户吃饭" / "和德国客户喝什么酒" / "敬酒"
- **B2 谈判**:"和德国客户谈合同" / "下一步怎么走" / "怎么接话"
- **B3 送礼**:"送日本客户什么礼物" / "伴手礼" / "价位"
- **B4 实时**:"客户刚说'我们考虑一下'" / "对方沉默 30 秒"
- **B5 突发**:"对方生气" / "冷场" / "聊到敏感话题"

### 回国后(D 模式)
- "刚从日本回来"
- "为什么没谈成"
- "复盘一下"

---

## 输出特点

- ✅ **数据先行**:必先查 Hofstede,有中国对照 Delta
- ✅ **框架支撑**:每条建议至少 1 条教授框架背书
- ✅ **行动导向**:落到"所以你应该怎么做",不是抽象原则
- ✅ **证据标签**:`[D]`数据 / `[F]`框架 / `[C]`课堂案例
- ✅ **接力问句**:出国中场景末尾追问"还有其他场景问题吗?"——但不强行推下一步
- ✅ **数据透明**:19 国部分维度 null,明确标 N/A 不编造

---

## v0.3.0 → v0.4.0 关键变化

| 维度 | v0.3.0 | v0.4.0 |
|------|--------|--------|
| 文件结构 | 单 SKILL.md (~38KB) | 主路由 + modules/ + frameworks/ 分层 |
| 出国中场景 | 1 个通用 B 模式 | 5 个细分子场景 |
| 回国复盘 | ❌ 无 | ✅ D 模式(两阶段:先引导问 → 再分析) |
| 加载方式 | 每次读全部 | 按触发词只读相关 module |
| 用户痛点 | "知道理论,不知道现在做什么" | 出国中连续问场景,像聊天一样 |

v0.3.0 完整副本保留在 `.v0.3.0-backup/`,随时可对照或回退。

---

## 注意事项

- 数据为**国家层面统计倾向**,不代表个体
- 涉及法律、合规、宗教与身份冲突时,优先给风险提示
- 若数据文件缺失或损坏,降级为定性分析模式
- 课堂案例(尤其历史/争议事件)使用"课堂援引/可能/建议核验"等不确定性表述

---

## 反馈与升级

- 数据每半年随 Hofstede 重抓
- 课堂洞察来自 2026 年 5 月港大 EMBA6611
- 如发现数据冲突 / 框架引用错误 / 新的国家实战洞察,欢迎反馈

---

## 致谢

- **张轶文教授**(港大 EMBA6611)— 12 条决策认知框架 + 课堂实战案例
- **Hofstede Insights / The Culture Factor** — 六维度国家数据
- **Edward T. Hall** — 高/低语境沟通理论
- **Florence Kluckhohn & Fred Strodtbeck** — 价值取向理论
- **EMBA6611 学员** — 德/法/墨/越/沙特等国实战分享
