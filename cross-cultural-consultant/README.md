# Cross-Cultural Consultant Skill

> **版本**:v0.8.1
> **数据快照**:2026-05-30
> **适用对象**:华智融高管跨文化出国伴侣——出国前 / 出国中 / 回国后 + 来访接待(C)
> **开箱即用**:OpenClaw / Hermes / Cursor clone 后即可用,知识与数据自包含,**无凭据依赖**(注册见 `references/openclaw-hermes-registration.md`)

---

## 这个 skill 解决什么

| 阶段 / 模式 | 你的需求 | skill 给你 |
|-------------|---------|-----------|
| **出国前(A)** | 文化画像 + 踩坑清单 | 完整报告 + 中国 Delta + checklist |
| **出国中(B1–B6)** | 餐桌 / 谈判 / 送礼 / 会议 / 突发 / 英文话术 | 场景化短答 + 框架依据 |
| **回国后(D)** | 复盘 | 先引导提问 → 再文化归因 |
| **来访接待(C)** | 外宾来华 | 战备手册 + 会后 CRM（单 Agent 写 `output/crm/`） |
| **经营分析(E)** | 已投重金的客户为什么拖 | 时间线 + Hofstede 节奏归因 |
| **多国对比** | 对比两国以上 | 含中国列的表格 + 3 件事 |

---

## 本地输出规范（`output/`）

所有本地产物落在技能目录 `output/`（已在 `.gitignore`，不入库）:

```
output/
├── 出差报告/          # A 模式等文化画像 PDF
├── 来访战备/          # C 模式战备手册 PDF
├── 市场/              # E 模式经营分析 PDF
└── crm/               # C 模式会后 CRM
    ├── 附件/          # 名片原图
    ├── 客户名片/      # 名片笔记
    ├── 客户信息/      # 客户主档案
    └── Meetings/      # 会议纪要
```

手机 PDF 统一走 `scripts/render_mobile_pdf.py`（SKILL.md §十三）。C 模式名片 OCR 走 `scripts/ocr_card.py`（§十四）。

---

## 知识基础

- **Hofstede 六维度数据库**(119 国,The Culture Factor)
- **港大 EMBA6611(张轶文教授)12 条决策框架** + 学员国家实战分享
- **Kluckhohn 六维价值取向理论**
- **Hall 高/低语境沟通理论**
- **华智融实战案例**（Cielo 来访、PagBank 经营分析、Fernando 解约等,见 `references/`）

---

## 目录结构

```
cross-cultural-consultant/
├── SKILL.md                  # 主路由 + 全局规则(渐进式加载)
├── CHANGELOG.md
├── README.md / LICENSE / .gitignore / evals.json
├── data/hofstede-dimensions.json
├── frameworks/               # 12 框架 + Kluckhohn + Hall
├── modules/                  # 7 个场景模板
├── examples/
├── references/               # 实战案例、CRM 模板、注册文档
│   ├── openclaw-hermes-registration.md
│   ├── crm-workflow.md
│   ├── crm-card-note-template.md
│   └── crm-meeting-note-template.md
├── templates/
├── agents/ / bundles/
├── evaluation/run_evals.py
└── scripts/
    ├── validate-data.py
    ├── render_mobile_pdf.py   # 手机竖版 PDF（可选 weasyprint/gs/PyMuPDF）
    ├── ocr_card.py            # 名片 OCR（可选 tesseract）
    └── run_integration_test.py
```

> v0.3.0 完整备份保留在 `migration/cross-cultural-consultant/.v0.3.0-backup/`。

---

## 可选依赖

| 能力 | 依赖 | 缺失时 |
|------|------|--------|
| 手机 PDF | weasyprint、ghostscript、PyMuPDF、中文字体 | 仍交付 Markdown |
| 名片 OCR | 系统 `tesseract` + `chi_sim`/`eng` 语言包 | Agent 识图兜底（`ocr_card.py` 退出码 2） |

---

## 安装与自检

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
# OpenClaw / Hermes: extraDirs 指向仓库根（见 references/openclaw-hermes-registration.md）

python3 cross-cultural-consultant/scripts/validate-data.py
python3 cross-cultural-consultant/evaluation/run_evals.py
python3 cross-cultural-consultant/scripts/run_integration_test.py   # 可选，含 PDF 链路
```

---

## 触发关键词速查

### 出国前(A)
- "下周去日本" / "给我日本完整画像"

### 出国中(B1–B6)
- **B1** 餐桌 / **B2** 谈判·解约 / **B3** 送礼 / **B4** 会议实时 / **B5** 突发
- **B6** "帮我写英文话术" / "英文演讲稿"

### 回国后(D)
- "刚从日本回来" / "为什么没谈成" / "复盘"

### 来访接待(C)
- "巴西客户团来中国" / "接待外宾" + 名单

### 经营分析(E)
- "PagBank 为什么这么拖" / "分析某国业务节奏"

---

## 输出特点

- ✅ Hofstede 数据 + 中国 Delta 对照
- ✅ 教授框架背书 + 行动导向
- ✅ 证据标签 `[D]`/`[F]`/`[C]`
- ✅ C 模式会后 CRM 单 Agent 闭环（不委派外部 profile/skill）
- ✅ 华智融真实案例保留（高管场景设计）

---

## 注意事项

- 数据为国家层面统计倾向,不代表个体
- `output/` 为本地归档,请定期备份或同步到你自己的笔记库（不绑定 iCloud/Obsidian 路径）

---

## 致谢

张轶文教授(港大 EMBA6611)、Hofstede / The Culture Factor、Hall、Kluckhohn、EMBA6611 学员实战分享
