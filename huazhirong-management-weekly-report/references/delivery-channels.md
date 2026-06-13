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

## 微信发文件机制与部署要求（重点）

`wechat-bridge` 通道**真正把 PDF 作为微信"文件消息"发送**(收件人可在微信下载该文件)。完整链路(源自官方插件 [hermes-weixin](https://github.com/hypergraphdev/hermes-weixin)):

```
deliver.py → POST {WEIXIN_BRIDGE_URL}/send  body={to, content, media_path:<abs pdf>}
  → bot.ts /send：校验 to+content 非空 → 有 media_path → sendWeixinMediaFile
    → 按 MIME 路由(mime.ts)：application/pdf → 文件附件分支 uploadFileAttachmentToWeixin
      → upload.ts：读文件 → md5 + AES-ECB 补齐 → getUploadUrl(no_need_thumb)
        → cdn-upload.ts：AES-ECB 加密 → POST CDN(octet-stream)，最多重试 3 次
      → send.ts sendFileMessageWeixin：FILE 消息(file_item{media,file_name,len}) → iLink sendmessage
  ← 200 成功 / 500 任何失败 / 400 缺 to|content
```

**支持的文件类型(mime.ts)**:pdf/doc(x)/xls(x)/ppt(x)/txt/csv/zip/tar/gz → **文件消息**;png/jpg/gif/webp/bmp → 图片;mp4/mov/webm/mkv/avi → 视频;未知后缀 → `application/octet-stream` 文件附件。

**部署硬性要求**:

1. **文件须在 bridge 进程的文件系统上**:`/send` 用 `path.resolve(media_path)` 以 **bridge 自身 CWD** 解析。本技能发送的是**绝对路径**;若 bridge 与技能不在同机/同容器,需把 `WEEKLY_REPORT_ARCHIVE_DIR` 指向 bridge 也能读的**共享卷**。
2. **微信账号已登录**(QR 登录 + token 配好),否则 `/send` 返回「Account not configured」。
3. **`content` 必须非空**:本技能用 `text or title`(title 恒非空),已规避 400。
4. **大小**:bridge 将整文件读入内存;周报 PDF(~数十 KB)无压力;超大文件受 iLink/微信侧限制,会以 500 形式返回(本技能记为可重试)。
5. **回执**:`getuploadurl`/CDN/`sendmessage` 任一非 2xx → `/send` 返回 500 → 本技能 `DELIVER_RETRY`(限流即属此类)。

> 验证(无需真实微信):`scripts/run_acceptance.py` 的 `WX01–WX06` 用本地 mock bridge 断言我们确实按 `{to, content(非空), media_path(绝对路径)}` 发送,并正确处理 200→成功 / 500→可重试 / 文件缺失→硬错误。

## 扩展新通道

在 `scripts/deliver.py` 的 `CHANNELS` 字典注册一个 `deliver_xxx(file, title, text, dry_run)` 函数即可,核心流程无需改动。

## 关于"直接上传 PDF 文件"

`wecom`/`feishu` 的 webhook 仅支持**文本/卡片通知**;要把 PDF 作为文件消息直接推送,需各平台的「上传素材 + 应用凭据(app id/secret 或 media upload key)」API——属于需要 Secret 的部署项,不在本脚本范围。当前实现发送含标题与文件路径的通知,文件本身经各自的文件分享/网盘链接或微信 `MEDIA:` 桥接送达。
