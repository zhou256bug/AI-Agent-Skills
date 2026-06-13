# 审计报告 · Opus 4.8 修复后复验

**修复时间**：2026-06-09  
**验收结果**：**48/48 通过**（含 TC31–45 状态机与边界用例）

## 已修复项

| ID | 问题 | 修复 |
|----|------|------|
| B1 | IMAP 异常 Gate 崩溃 | 全链路 try/except + `timeout=30` + main 兜底始终输出 `GATE:` |
| B2 | 验收未覆盖状态机 | TC31–39 mock 测试 RETRY/FAIL/RUN/ALREADY_* |
| M1 | 无 xlsx 新邮件遮蔽旧邮件 | `_pick_best_candidate` 优先含 xlsx |
| M2 | 80 封 RFC822 全量拉取 | 先 `BODY.PEEK[HEADER]` 再按需 RFC822 |
| M3 | 凭据/IMAP 误报「未收到邮件」 | `FAIL_MESSAGES` 按 reason 分流 |
| M4 | next_run_at 非周一 | 修正为 2026-06-15（下周一） |
| M5 | 仅 terminal 工具集 | 四轮 cron 增加 `file` |
| m1 | 去重仅 mtime | 支持按 `week_num` 精确去重 |
| m2 | FAIL 重复通知 | `GATE:ALREADY_FAILED` + `failed_notified` 幂等 |
| m3 | 超大内容多页 | `page_height_pt` 24000 + weekly-report 多页 exit 3 |
| m4 | validator 缺口 | 禁止段变体、段序、meta 字段、节1/节5 条数 |
| m5 | 表格 `\|` 分列 | `_parse_table_row` 支持 `\|` 转义 |

## 运行验收

```bash
HERMES_HOME=~/.hermes-huazhirong python3 \
  skills/business/huazhirong-management-weekly-report/scripts/run_acceptance.py
```

## 结论：**PASS**（可上线）

Gateway 已需 reload 以加载 jobs.json 变更。
