# 关注人列表管理

用户可直接告诉 Agent「把 xxx 加入/移出关注人」，Agent **用 terminal 执行 CLI**，勿手改 JSON（除非用户明确要求编辑文件）。

## CLI

```bash
# 列出
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py list

# 新增
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py add \
  --name "程晓艳 (Charlene)" \
  --email charlene.cheng@newpostech.com \
  --action report_promptly \
  --priority medium

# 删除（id / 邮箱 / 姓名 任一）
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py remove charlene.cheng@newpostech.com
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py remove fernando-alonso
```

## action 策略

| action | 含义 |
|--------|------|
| `read_full` | cron 时必读全文 |
| `read_attachments` | 读全文 + 下载附件 |
| `report_promptly` | 摘要标 ⭐，由 Agent 判断是否读全文 |

## Agent 对话示例

**用户**：「把 jay.lin@newpostech.com 加入关注，重要邮件读全文」

**Agent**：
```bash
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py add \
  --name "林旭伟 (Jay)" \
  --email jay.lin@newpostech.com \
  --action read_full \
  --priority high
```

**用户**：「Victor 不用关注了，删掉」

**Agent**：
```bash
python3 huazhirong-inbox-watch/scripts/watchlist_cli.py remove victor
```

## 数据文件

- 路径：`data/watchlist.json`（技能内，可 commit 团队默认；个人实例也可只改本地）
- `check_unseen.py` 每次扫描自动加载最新列表

## 注意

- 邮箱用完整地址，避免误匹配
- 删除前可先 `list` 确认 id
- 内部同事默认 `report_promptly`；海外 GM / 尼尔森等见仓库默认配置
