# 投递通道（多通道，可扩展）

投递是**可选的平台胶水层**,与周报核心(取邮件→四段→PDF)解耦。统一入口 `scripts/deliver.py`。

| 通道 | `--channel` | 机制 | 依赖 |
|------|-------------|------|------|
| 微信(Hermes 桥接) | `wechat-media` | 输出单独一行 `MEDIA:<绝对路径>`,Hermes→微信桥据此附带 PDF | 无 |
| 企业微信 | `wecom` | 群机器人 webhook 发文本通知 | 环境变量 `WECOM_WEBHOOK_URL` |
| 飞书 | `feishu` | 自定义机器人 webhook 发文本通知 | 环境变量 `FEISHU_WEBHOOK_URL` |

```bash
# 微信（默认）：最终回复必须含 MEDIA: 行，否则微信只收到文字、不附 PDF
python3 scripts/deliver.py --channel wechat-media --file output/W23-2026年06月08日.pdf

# 企业微信 / 飞书：先配 webhook，再发（--dry-run 可预览不联网）
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
python3 scripts/deliver.py --channel wecom --file output/W23-....pdf --title "第23期周报" --dry-run
```

## 扩展新通道

在 `scripts/deliver.py` 的 `CHANNELS` 字典注册一个 `deliver_xxx(file, title, text, dry_run)` 函数即可,核心流程无需改动。

## 关于"直接上传 PDF 文件"

`wecom`/`feishu` 的 webhook 仅支持**文本/卡片通知**;要把 PDF 作为文件消息直接推送,需各平台的「上传素材 + 应用凭据(app id/secret 或 media upload key)」API——属于需要 Secret 的部署项,不在本脚本范围。当前实现发送含标题与文件路径的通知,文件本身经各自的文件分享/网盘链接或微信 `MEDIA:` 桥接送达。
