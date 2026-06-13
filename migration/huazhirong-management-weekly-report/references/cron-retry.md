# 周一 Cron · 四轮重试

陈徐伟周报邮件通常在 **周一下午** 到达。专项任务 **仅周一** 运行：

| Slot | 时间 | cron |
|------|------|------|
| 1 | 17:10 | `10 17 * * 1` |
| 2 | 18:10 | `10 18 * * 1` |
| 3 | 19:10 | `10 19 * * 1` |
| 4 | 20:10 | `10 20 * * 1`（最终） |

## Gate 脚本（必须先跑）

```bash
python3 "$HERMES_HOME/scripts/weekly_evyn_cron_gate.py" --slot N
```

| 首行输出 | Agent 行为 |
|----------|------------|
| `GATE:ALREADY_DONE` | `[SILENT]` — 本周 PDF 已存在 |
| `GATE:ALREADY_FAILED` | `[SILENT]` — 本周已通知失败，不重复打扰 |
| `GATE:RETRY_SILENT` | `[SILENT]` — 未收到邮件，下一小时再试（不打扰菜头） |
| `GATE:FAIL_NOTIFY` | **必须推送** — 读取 stdout `message=` 行原样告知（未收到邮件 / 凭据缺失 / 连接异常 / 无 xlsx 等） |
| `GATE:RUN` | 执行完整 xlsx→五段 Markdown→PDF→推送 |

状态文件：`$HERMES_HOME/cron/state/weekly-evyn-YYYY-Www.json`

## 验收（生成后）

```bash
python3 skills/business/huazhirong-management-weekly-report/scripts/validate_weekly_report_md.py /path/to/body.md
python3 skills/business/huazhirong-management-weekly-report/scripts/run_acceptance.py
```

## 已取消

- ~~周二 09:10 补跑~~ — 由周一 17:10–20:10 四轮覆盖
