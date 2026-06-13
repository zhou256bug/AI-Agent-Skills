# Capitec Bank 端到端客户管线案例（2026-06-05）

## 背景

菜头说"南非的capitac是我们大客户，请帮我建立客户档案"——仅从一个模糊的客户名开始。

## 管线步骤

### 阶段一：发现与确认

1. **内部名录核实** → 搜索 `newpos/销售/客户列表.csv` → 确认第51行 `Capitec Bank,非洲一区,许文强`
2. **Obsidian核实** → `客户信息总表.md` 第255行确认
3. **名别称确认** → web_search → "Capitac" 实为 "Capitec Bank"（南非最大零售银行）
4. **代理发现** → web_search → LinkedIn → 代理是 **SCOTCH. Software**，老板 **Tian van Zyl**（Founder & CEO）

### 阶段二：联系人归档

5. **名片接收** → 菜头发来 Francois Dempers（Product Head: Merchant Solutions）名片照片
6. **名片处理**（2026-06-07 路径已迁移；以下为 2026-06-05 历史快照）：
   - 大为 OCR + 存图 → 委派艾玛建档（现行见 `emma-customer-maintenance`）
   - ~~名片笔记 → `客户维护/客户信息/名片/…`~~ → 现行 `客户维护/客户名片/中东非洲/南非-Capitec-Francois Dempers.md`
   - 联系人信息 → patch Capitec 档案 `### 四、关键联系人`

### 阶段三：会议纪要（飞书妙记 → Obsidian）

7. **找妙记** → `feishu_minutes.py list 3` → 找到 "New Store Product Discussion"（6月5日 13:32）
8. **取转录** → `feishu_minutes.py url <link>` → 得到2564行全文
9. **整理纪要** → `hermes -p emma chat -q "…" -Q -s emma-customer-maintenance` 委派艾玛整理 → 输出结构化会议纪要（6议题+9决策+13行动项+时间线）
10. **归档** → 存 `客户维护/Meetings/南非Capitec Bank meeting 2026-06-05.md`
11. **双链** → 在 Capitec 客户档案中追加 `[[南非Capitec Bank meeting 2026-06-05]]`

### 阶段四：客户档案更新

12. 补充已供型号（9310/9830/9220）
13. 补充联系人（Tian van Zyl + Francois Dempers）
14. 添加重要会议双链

## 关键教训

| 步骤 | 做对了什么 | 可改进 |
|------|-----------|--------|
| CSV 核查 | 第一时间从内部名录确认客户存在 | 应该在档案中直接记录订单数量 |
| LinkedIn 搜索 | 找到了代理的正确公司名（SCOTCH. Software 而非 Scotch International） | 无 |
| 名片处理 | 原图+独立md+更新档案，格式正确 | 无 |
| 飞书转录取内容 | url 命令成功获取全文 | API GET 方式第一次失败后切换到了 url 方式 |
| 纪要委派 | delegate_task 一次性完成分析，效率高 | 无 |

## 产出文件清单

| 文件 | 路径 |
|------|------|
| Capitec 客户档案 | `客户维护/客户信息/南非/Capitec Bank.md` |
| SCOTCH. Software 代理档案 | `客户维护/客户信息/南非/SCOTCH. Software.md` |
| Francois 名片笔记 | ~~`客户维护/客户信息/名片/…`~~ → `客户维护/客户名片/中东非洲/南非-Capitec-Francois Dempers.md` |
| 名片原图 | `附件/普通附件/Francois Dempers - Capitec.jpg` |
| 会议纪要 | `客户维护/Meetings/南非Capitec Bank meeting 2026-06-05.md` |
| 客户总表更新 | `客户维护/客户信息总表.md` — Capitec行补了联系人 |
