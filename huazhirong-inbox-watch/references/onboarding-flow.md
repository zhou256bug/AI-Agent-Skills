# Agent 引导配置

## 何时触发

1. 首次 `/inbox-watch` 或 cron 报 IMAP 凭据缺失
2. 用户更换邮箱 / 微信收件人

## CLI

```bash
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py setup status
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py setup apply \
  --imap-user "name@company.com" \
  --imap-password "..." \
  --weixin-to "your_id" \
  --target skill \
  --verify
python3 huazhirong-inbox-watch/scripts/inbox_watch_cli.py doctor
```

## 对话话术

> 收件箱值守需要 IMAP 邮箱与（可选）微信推送对象。
> 1. 邮箱地址与客户端授权密码
> 2. IMAP 主机（阿里企业邮默认 `imap.qiye.aliyun.com`）
> 3. 微信 `WEIXIN_TO`（推送给谁）

密码禁止写入日志、代码或 commit。
