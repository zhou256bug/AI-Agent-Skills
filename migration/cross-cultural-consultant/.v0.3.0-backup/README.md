# Cross-Cultural Consultant Skill

> **版本**：v0.3.0
> **数据快照**：2026-05-30
> **适用对象**：面向中国管理者的跨国商务/海外团队管理场景

面向跨国商务场景的跨文化顾问技能，基于：
- **Hofstede 六维数据**（119 国家，The Culture Factor）
- **港大 EMBA6611（张轶文教授）12 条决策框架**
- **Kluckhohn 六维价值取向理论**
- **Hall 高/低语境沟通理论**

---

## 目录结构

```
cross-cultural-consultant/
├── SKILL.md                 # 技能主文件（必读）
├── README.md                # 本文件，安装与使用说明
├── LICENSE                  # MIT 许可证
├── evals.json               # 回归测试用例（6 个）
├── data/
│   └── hofstede-dimensions.json   # 119 国六维数据（391KB）
├── evaluation/
│   └── run_evals.py                # 自动评测脚本
└── examples/
    ├── A-mode-japan.md             # A 模式示例：日本画像
    ├── B-mode-germany.md           # B 模式示例：德国谈判
    ├── C-mode-saudi.md             # C 模式示例：沙特建团队
    └── null-dimensions.md          # 数据缺失国家清单与处理示范
```

---

## 安装方式

### 方式一：Claude Code (CLI)
```bash
cp -r cross-cultural-consultant ~/.claude/skills/
```

### 方式二：Claude Desktop / Claude.ai
将整个文件夹压缩为 `cross-cultural-consultant.zip`，在 Project 中上传。

### 方式三：Hermes Agent
将目录放到 Hermes 的 `external_skills_dirs` 配置指向的路径下。

---

## 触发关键词

- "下周去日本见客户，先给我完整画像"
- "和德国客户谈条款，怎么回应更稳"
- "在沙特建团队，外派和本地雇佣怎么组合"
- "对比墨西哥和法国，我作为中国管理者最容易踩的坑"
- "我要去越南出差，文化上要注意什么"

---

## 输出模式

| 模式 | 触发场景 | 输出形式 |
|------|---------|---------|
| **A** | 出发前国家画像 | 完整 5 板块报告 |
| **B** | 即时场景顾问 | 3-5 句直接建议 |
| **C** | 战略决策参考 | A 模式 + 战略管理警示 |
| **对比** | 多国并列 | 多国表格（含中国列） |
| **澄清** | 信息不足 | 先问 4 个最小问题再回答 |
| **兜底** | 数据缺失 | 明确告知 + 定性建议 |

---

## 注意事项

- 数据为**国家层面统计倾向**，不代表个体
- 涉及法律、合规、宗教与身份冲突时，优先给风险提示
- 若数据文件缺失或损坏，skill 会降级为定性分析模式

---

## 反馈与升级

- 本 skill 每半年随 Hofstede 数据更新一次
- 课堂洞察来自 2026 年 5 月港大 EMBA6611 课程
- 如发现数据冲突、框架引用错误、或有新的国家实战洞察，欢迎反馈

---

## 致谢

- **张轶文教授**（港大 EMBA6611）— 12 条决策认知框架
- **Hofstede Insights / The Culture Factor** — 六维度国家数据
- **Edward T. Hall** — 高/低语境沟通理论
- **Florence Kluckhohn & Fred Strodtbeck** — 价值取向理论
- **EMBA6611 学员** — 德国/法国/墨西哥实战分享
