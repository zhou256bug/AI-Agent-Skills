# C 模式示例：Cielo 高管团来访接待（2026-06-04）

## 场景背景

Cielo（巴西最大收单机构）13人全高管层随咨询公司访学中国，由供应商赞助。我方（华智融）获得展示机会。核心目标：将 1000 台 9010 推入 Cielo 巴西体系。

## 来访团队构成（决策影响力排序）

| 姓名 | 职位 | 决策角色 | 关注点 |
|------|------|----------|--------|
| Carlos Eduardo D. Alves | EVP/CTO | 技术认证签字 | 9010 技术架构、PIX 兼容、认证路线 |
| Adriana P. Garbim | EVP/CSO | 推量决策 | 销售模型、渠道策略、商户适配 |
| Filipe A. S. Oliveira | EVP/CFO | 定价付款条件 | Unit economics、账期、ROI |
| Louangela B. C. Colquhoun | EVP/CLO | 合同把关 | 合规、监管适配 |
| Patricia C. C. Passos | CRO | 风控审批 | 欺诈预防、PCI 合规 |
| Bruno Lino | 技术执行总监 | 技术对接 | 平台集成 |
| Diego Munoz | 业务发展总监 | 信息收集 | 市场对标 |
| Elissandra Rodrigues | 销售执行总监 | 一线反馈 | 产品卖点 |
| Luis H. P. Loureiro | 销售执行总监 | 一线反馈 | 产品卖点 |
| Marcelo Veiga | 反欺诈总监 | 风控信息 | 安全标准 |
| Victor Zakime | FP&A 总监 | 财务分析 | 成本测算 |
| Vitor Madureira | 客服总监 | 产品体验 | 终端体验 |

## 核心跨文化碰撞

| 维度 | 中国 | 巴西 | Delta | 商业含义 |
|------|------|------|-------|---------|
| 权力距离 | 80 | 69 | -11 | 层级接受但不过度，可对话 |
| 不确定规避 | 30 | 76 | ⚠️ +46 | 需要书面承诺、认证路线图、时间表 |
| 长期导向 | 77 | 28 | ⚠️ -49 | 要快——90天内能做什么比三年蓝图重要 |
| 放纵/克制 | 24 | 59 | ⚠️ +35 | 情感外露、喜欢轻松氛围 |

## 全流程环节（会前 → 会中 → 会后）

### 会前（T-1 周）
1. **Excel 名单分析** — 识别决策者（CTO/CSO/CFO 三维影响力）、信息收集者、陪同者
2. **LinkedIn 背景查询** — 公开简历+IR页面法定高管信息
3. **文化画像** — Hofstede（中国对照）、Kluckhohn、Hall
4. **PDF 战备手册** — 8页含：来宾画像、文化分析、中国趋势、我方实力、话术、路线图、Q&A
5. **团队分工 briefing** — 谁开场、谁主沟通、谁补位

### 会中（D-Day）
6. **75 分钟议程执行** — 开场（中方 3 分钟英文）→ 我方展示 → 对方提问 → 收网（书面时间表承诺）
7. **晚宴准备** — 打印中英文台卡（全员姓名+职位），注意巴西人餐桌习惯和酒类偏好

### 会后（T+0 ~ T+3）

> 本节由**本 Agent**执行，见 `references/crm-workflow.md`。**禁止**委派外部 Agent 或调用其他 skill。

8. **名片收网** — 名片照片 → `scripts/ocr_card.py --image …`（或 Agent 识图）→ 按 `crm-card-note-template.md` 写入 `output/crm/客户名片/{大洲}/{国家}/{国家}-{公司}-{姓名}.md`，并更新 `output/crm/客户信息/{国家}-{客户}.md`
9. **客户档案更新** — 联系人表追加一行，链到名片笔记与会议纪要
10. **会议纪要** — 按 `crm-meeting-note-template.md` 写入 `output/crm/Meetings/{国家}-{客户}-meeting-{YYYY-MM-DD}.md`
11. **跟进执行** — 发送英文纪要、书面路线图、POC 对接安排（48 小时内，适配高 UA 来访国别）

## 产出物清单

- 战备手册 → `output/来访战备/{客户}_战备手册_{语言}_{YYYYMMDD}.pdf`（`scripts/render_mobile_pdf.py`）
- 客户档案 → `output/crm/客户信息/{国家}-{客户}.md`
- 会议纪要 → `output/crm/Meetings/{国家}-{客户}-meeting-{YYYY-MM-DD}.md`
- 名片 → `output/crm/附件/{姓名}_{公司}.jpg` + `output/crm/客户名片/...md`（本 Agent + `ocr_card.py` 或识图）

## 关键教训

- A 模式（出国前画像）的文化分析框架完全适用于来访场景，但输出需要额外包含"给对方看的中国内容"和"话术"
- Excel 名单 → PDF 战备手册是全流程可复制的模式
- 决策影响力地图是老板最看重的部分——三个核心人物精确标注
- 晚宴台卡是巴西高 UA 文化的细节——全员中英文名字+职位，让对方感觉被认真对待
- 名片宜当晚会后录入（`ocr_card.py` 或 Agent 识图），48 小时内书面跟进；高 UA 文化依赖时间表与英文纪要
