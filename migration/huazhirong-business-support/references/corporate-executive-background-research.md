# 公司高管背景调研指南

## 适用场景

需要查找某公司特定高管的职业背景、教育经历、履历时使用。常见于：
- 客户高管背景摸底
- 合作伙伴关键人物尽职调查
- 竞品公司核心团队分析

## 核心方法论

### 第一步：确定信息获取渠道

| 优先级 | 渠道 | 适用情况 | 
|--------|------|----------|
| 🥇 公司IR（投资者关系）官网 | 上市公司法定高管 | 最权威，有法定披露义务 |
| 🥈 LinkedIn公开资料 | 所有高管/员工 | 信息最全，个人主动更新 |
| 🥉 新闻报道/行业媒体 | 特殊情况 | 重大任命/离职/奖项 |

### 第二步：区分高管层级（关键认知）

不同层级的高管在信息披露上差异巨大：

| 层级 | 典型头衔 | 公开披露情况 |
|------|---------|-------------|
| **法定高管** | CEO, CFO, C-level, EVP, 副总裁（VP级） | ✅ 上市公司IR官网有法定简历披露（姓名、年龄、教育、履历） |
| **运营管理层** | Executive Superintendent, Senior Director, General Manager | ❌ 通常不在法定披露中，需LinkedIn或新闻报道 |
| **中层管理** | Manager, Supervisor | ❌ 无公开披露 |

> ⚠️ 关键陷阱：如果IR官网只披露了8-10人的执行董事会（Diretoria Estatutária），而你要查的人头衔是"Executive Superintendent"或类似级别，属于法定高管之下的运营管理层。IR官网不会列出这些人。必须转向LinkedIn或行业新闻。

### 第三步：搜索IR官网的步骤

> ⚠️ 以下步骤在 web_search 不可用时作为替代方案使用。优先使用 web_search。

#### 1. 找到公司IR网站

常见URL模式：
- `ri.{公司}.com.br`（巴西公司模式：RI = Relações com Investidores）
- `investors.{公司}.com`（英语市场模式）
- `ir.{公司}.com`（通用模式）
- `{公司}.com/investors`（子路径模式）

#### 2. 查找管理层/高管页面

导航菜单关键词（葡萄牙语/英语/西班牙语）：
- Diretoria / Board of Directors / Management
- Governança Corporativa / Corporate Governance
- Conselho, Diretoria, Comitês e Fóruns / Board, Management, Committees and Forums
- Executive Team / Leadership Team
- Equipe Executiva / Time de Liderança

#### 3. 用提取简历

```bash
# 获取页面内容并打印指定XPath区域
curl -sL --max-time 15 "https://ri.cielo.com.br/sobre-a-cielo/conselho-diretoria-comites-e-foruns/"

# 提取执行董事会(Executive Board)区域
curl -sL --max-time 15 "URL" | sed -n '/Diretoria Executiva/,/Regimento Interno/p'
```

#### 4. 从HTML表格中提取结构化数据

巴西/拉美公司通常在页面上用HTML `<table>` 呈现高管名单，结构为：

| 字段 | 示例 |
|------|------|
| 姓名 | Filipe Augusto dos Santos Oliveira |
| 年龄 | 39 |
| 职位 | Diretor Vice-Presidente e DRI |
| 任命日期 | 29/05/2024 |
| 任期结束 | 1º RCA após a AGO 2026 |
| 简历 | 教育+工作经历的段落文本 |

每个 `<tr class="curriculo">` 行包含该高管的详细简历文本。

### 第四步：搜索阈值

如果IR官网没有（如所查人员低于法定高管级别），应当：
1. 通知用户该人员不在IR公开披露范围内
2. 建议转向LinkedIn搜索（通常可公开访问）
3. 如有行业新闻提及，一并提供

### 第五步：搜索引擎不可用时的备选方案

当 web_search（Brave Search）和所有搜索引擎同时不可用时，按以下优先顺序尝试：

| # | 方案 | 方法 | 局限性 |
|---|------|------|--------|
| 1 | **IR官网直接浏览** | browser_navigate → 查找"Liderança/Diretoria/Governança"页面 | 只覆盖法定高管（C-level/EVP），不覆盖运营管理层（Superintendent级别） |
| 2 | **Cielo主站"Conheça a Cielo"** | https://www.cielo.com.br/ → 页脚"Conheça a Cielo" | 实测找不到高管页面，未知原因 |
| 3 | **LinkedIn公开搜索** | browser_navigate → linkedin.com/search/results/people/?keywords=... | 需要登录才可查看详细简历 |
| 4 | **Bing非无障碍版** | 尝试不同URL参数绕过无障碍模式 | 实测受限（返回空搜索结果页） |
| 5 | **curl直连搜索引擎** | 用Python requests模拟浏览器 | Bing/Google均触发反爬/SSL错误 |
| 6 | **DuckDuckGo API** | api.duckduckgo.com/?q=...&format=json | 返回结果极有限，不适合人物搜索 |
| 7 | **python duckduckgo_search库** | pip install duckduckgo_search | 实测连接Bing代理被限 |
| 8 | **公司新闻稿/投资者页面** | 新闻公告可能含管理层变动信息 | 需逐个扫描，效率低 |
| 9 | **CVM/证监会文件** | 巴西CVM（Comissão de Valores Mobiliários）公开备案 | 文件批量大，需精准定位 |

**关键经验（2026-06-04 实测）**：
- 当所有搜索引擎同时不可用时，对于**上市公司运营管理层**（非法定高管），**没有可靠的公开替代渠道**
- Cielo IR官网 (ri.cielo.com.br) 的/lideranca/和/executive-board/页面均返回404
- Cielo主站产品页 (cielo.com.br) 不包含管理团队信息
- 应该直接告知用户搜索基础设施当前不可用，建议稍后重试
- 如果有LinkedIn账号，登录后搜索是唯一可靠途径

### 第六步：信息整理格式

用中文概括输出，包含以下要素：

```
**姓名 — 职位**
年龄：XX岁
教育：毕业院校+专业
工作经历（按时间倒序）：
- 现任（公司+职位+入职时间）
- 过往经历要点
行业背景：整体从业年限+专长领域总结
```

## Pitfalls

- ⚠️ 切勿混淆"执行董事会成员"与"运营管理层"——两种在披露深度上有本质差异
- ⚠️ 巴西/拉美公司IR网站经常有 .br 域名，但HTTP请求可能被阻——尝试HTTP/HTTPS两种协议、PT和EN两种语言版本
- ⚠️ IR网站有时是WordPress+JS渲染——先用 `curl` 尝试能否拿到HTML，纯JS渲染的页面要改用browser工具
- ⚠️ 高管年龄注意区分：巴西格式 `dd/mm/yyyy`，不是 `mm/dd/yyyy`
- ⚠️ 中文翻译职位时保持一致性：Presidente=总裁/CEO, Diretor=总监/董事, Vice-Presidente=副总裁, Superintendente=总监/执行总监
- ⚠️ DRI = Diretor de Relações com Investidores = 投资者关系总监
- ⚠️ **搜索引擎全面不可用时**：不花时间逐个尝试所有搜索引擎。做3次 web_search 尝试都失败后，直接切换到IR官网浏览+告知用户当前搜索不可用。持续重试同一工具到10+次是浪费token。
- ⚠️ **运营管理层vs法定高管的信息鸿沟**：Superintendent/Director级别没有法定披露义务，IR官网不会有。如果搜索引擎不可用且没有LinkedIn登录权限，这个层级的信息无法获得——直接告知用户，不要猜测。
