# 投递通道（多通道，可扩展）

统一入口 `scripts/deliver.py`,返回结构化结果 `{ok, retryable, channel, detail}`,供编排器判定续跑。

| 通道 | `--channel` | 机制 | 回执 | 依赖 |
|------|-------------|------|------|------|
| **微信 bridge(自动化默认)** | `wechat-bridge` | 直连 hermes-weixin `POST /send` | **有**:HTTP 200=成功 / 500/超时=可重试(含限流) | `WEIXIN_BRIDGE_URL`(默认 `http://localhost:9100`)+ `WEIXIN_TO` |
| 微信(回复桥接,交互兜底) | `wechat-media` | 输出 `MEDIA:<绝对路径>` 行,Agent 回复→网关代发 | **无** | 无 |
| 企业微信 | `wecom` | 群机器人 webhook 文本通知 | HTTP 200/非200 | `WECOM_WEBHOOK_URL` |
| 飞书 | `feishu` | 自定义机器人 webhook 文本通知 | HTTP 200/非200 | `FEISHU_WEBHOOK_URL` |

> **为何默认 `wechat-bridge`**:据官方插件源码(`src/bot.ts` /send 返回 200/500、`src/api/api.ts` 非 2xx 抛错),直连 bridge 能拿到**真实成功/失败**,限流表现为可重试失败 → 编排器据此 `DELIVER_RETRY` 续跑。`wechat-media` 走 Agent 回复代发,**拿不到回执**,仅适合人对话兜底。

```bash
# 微信 bridge（默认，有回执）
python3 scripts/deliver.py --channel wechat-bridge --file output/W23-2026年06月08日.pdf   # 需 WEIXIN_TO

# 交互兜底：输出 MEDIA: 行（无回执）
python3 scripts/deliver.py --channel wechat-media --file output/W23-2026年06月08日.pdf

# 企业微信 / 飞书：先配 webhook，再发（--dry-run 可预览不联网）
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
python3 scripts/deliver.py --channel wecom --file output/W23-....pdf --title "第23期周报" --dry-run
```

## 扩展新通道

在 `scripts/deliver.py` 的 `CHANNELS` 字典注册一个 `deliver_xxx(file, title, text, dry_run)` 函数即可,核心流程无需改动。

## 关于"直接上传 PDF 文件"

`wecom`/`feishu` 的 webhook 仅支持**文本/卡片通知**;要把 PDF 作为文件消息直接推送,需各平台的「上传素材 + 应用凭据(app id/secret 或 media upload key)」API——属于需要 Secret 的部署项,不在本脚本范围。当前实现发送含标题与文件路径的通知,文件本身经各自的文件分享/网盘链接或微信 `MEDIA:` 桥接送达。
