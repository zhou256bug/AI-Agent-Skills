# Hermes Cron 定时扫描

## 调度

| 项 | 值 |
|----|-----|
| 表达式 | `0 7-22/3 * * 1-5` |
| 含义 | 工作日 07/10/13/16/19/22 整点 |
| 模式 | **LLM-driven**（Hermes agent + terminal） |
| toolsets | `terminal`（仅跑脚本，不联网不读库） |

## 创建任务（示例）

```bash
hermes cron create "0 7-22/3 * * 1-5" \
  "收件箱未读扫描：运行 inbox-watch 技能，归档并推送微信" \
  --name "inbox-watch-weekday" \
  --toolsets terminal,skills
```

内联 prompt 见 `references/agent-cron-prompt.md`。

## Agent 每轮步骤

1. `python3 huazhirong-inbox-watch/scripts/check_unseen.py`
2. 解析 `TOTAL_UNSEEN` / `PERSONAL_UNSEEN` / `---EMAIL---` 块
3. 无未读 → 回复 **「没有新邮件」** 并 `run_scan.py --deliver`（不可静默）
4. 有关注人 → 按 `WATCH_ACTION` 读全文或下载附件
5. `run_scan.py --deliver` 归档 Markdown + 推送微信
6. 向用户输出 emoji 摘要

## 手动测试

```bash
python3 huazhirong-inbox-watch/scripts/run_scan.py --dry-run
python3 huazhirong-inbox-watch/scripts/run_scan.py --deliver --dry-run
hermes cron run <job_id>
```

## 运维

- `hermes cron list` / `hermes cron status`
- 归档：`output/scans/YYYY-MM-DD_HH-MM_inbox_scan.md`
- 节假日仅 22:00：**v2**（需单独 cron 或日历门控）
