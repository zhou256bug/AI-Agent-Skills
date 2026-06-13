# 验收测试用例（历史记录）

> **历史文档**:以下用例对应旧版"依赖 `$HERMES_HOME` cron gate + iCloud 金标准"的 45 项套件。
> 规范化后,`scripts/run_acceptance.py` 已改为**平台无关、可独立跑通**的套件(validator/transform/paths/config,render 在无可选依赖时自动 SKIP),不再依赖外部 gate。本文保留作历史参考。

自动化入口：`scripts/run_acceptance.py`（全部 deterministic，不依赖 LLM）。

## A. Gate 逻辑（TC01–TC07）

| ID | 角度 | 预期 |
|----|------|------|
| TC01 | 脚本存在性 | `weekly_evyn_cron_gate.py` 可读 |
| TC02 | 校验器存在 | `validate_weekly_report_md.py` 可读 |
| TC03 | 渲染器存在 | `render_mobile_pdf.py` 可读 |
| TC04 | 重试次数 | `MAX_SLOTS == 4`（17:10–20:10） |
| TC05 | 发件人匹配 | evyn.chen + 总裁办周报主题 → True |
| TC06 | 周数解析 | 「周报（23）」→ week_num=23 |
| TC07 | 负例过滤 | 非 Evyn 发件人 → False |

## B. Markdown 结构（TC08–TC15）

| ID | 角度 | 预期 |
|----|------|------|
| TC08 | 禁止段 | 含「菜头周报原文」→ 校验失败 |
| TC09 | 最小合法样例 | 五段 + meta + urgent → 通过 |
| TC10 | meta 必填 | 无 `:::meta` → 失败 |
| TC11 | 第一节 | 缺「一、菜头…」→ 失败 |
| TC12 | 第二节 | 缺「二、重点项目…」→ 失败 |
| TC13 | 第三节 | 缺「三、海外…」→ 失败 |
| TC14 | 第四节 | 缺「四、业务线…」→ 失败 |
| TC15 | 第五节 | 缺「五、需关注…」→ 失败 |

## C. 金样 W23（TC16–TC20）

| ID | 角度 | 预期 |
|----|------|------|
| TC16 | 文件存在 | `周报_W23_20260608_总结.md` |
| TC17 | 校验通过 | validate 零 issue |
| TC18 | 无禁止段 | 不含「菜头周报原文」 |
| TC19 | 署名规范 | 含 `**肖启新**` 等末尾署名 |
| TC20 | 段数 | 仅五段，无「## 六、」 |

## D. PDF 渲染稳定性（TC21–TC25）

| ID | 角度 | 预期 |
|----|------|------|
| TC21 | 渲染成功 | exit code 0 |
| TC22 | 页宽 | cropbox ≈ 100mm（98–102） |
| TC23 | 单页 | page_count == 1 |
| TC24 | 高度稳定 | 连续两次渲染高度差 < 2pt |
| TC25 | 体积 | PDF > 10KB（非空壳） |

## E. 技能与 Cron 配置（TC26–TC30）

| ID | 角度 | 预期 |
|----|------|------|
| TC26 | SKILL 存在 | `SKILL.md` |
| TC27 | Gate 文档 | SKILL 提及 `weekly_evyn_cron_gate.py` |
| TC28 | 禁止原文 | SKILL 明确禁止「菜头周报原文」 |
| TC29 | 格式参考 | `content-format.md` 含第五节 |
| TC30 | Cron 四轮 | jobs.json 含 Mon 17/18/19/20 + gate + FAIL_NOTIFY |

## Gate 行为矩阵（人工/集成）

| Slot | 时间 | 无邮件 | 有邮件+xlsx | 已有 PDF |
|------|------|--------|-------------|----------|
| 1 | 17:10 | RETRY_SILENT | RUN | ALREADY_DONE |
| 2 | 18:10 | RETRY_SILENT | RUN | ALREADY_DONE |
| 3 | 19:10 | RETRY_SILENT | RUN | ALREADY_DONE |
| 4 | 20:10 | **FAIL_NOTIFY** | RUN | ALREADY_DONE |
