# 法务审核意见 · 手机 PDF 工作流

> **铁律**：手机竖版 PDF **必须**走 `scripts/render_mobile_pdf.py`（与跨文化技能同款引擎）。  
> 禁止 Agent 现场手写 HTML/CSS。

## 何时生成 PDF

用户说以下任一意图时，在 Markdown 审核意见完成后生成 PDF：

- 「发 PDF」「手机看」「手机可读」
- 「发给我」「推送报告」
- 微信/邮件附带审核意见

未要求 PDF 时，交付 Markdown 即可（`output/合同/.../*.md`）。

## 可选依赖

| 依赖 | 用途 |
|------|------|
| `weasyprint` | HTML → PDF |
| `ghostscript` | 体积优化 |
| `PyMuPDF`（`fitz`） | 裁剪白边 |
| Noto Sans SC | 中文渲染 |

未安装时：**不影响**文本审核；告知用户缺依赖，交付 Markdown。

## 标准命令（推荐）

**便捷入口**（自动归档路径 + 法务配色）：

```bash
python3 huazhirong-legal-affairs/scripts/render_review_pdf.py \
  --title "7-Labs 经销合同审核" \
  --body-md output/合同/审核记录/2026-06-14_7-Labs_合同审核.md \
  --party "7-Labs" \
  --mode A
```

**底层脚本**（与跨文化 `mobile-default` 预设一致，284pt 宽 / 10pt 正文）：

```bash
python3 huazhirong-legal-affairs/scripts/render_mobile_pdf.py \
  --preset mobile-default \
  --title "⚖️ 7-Labs 合同审核" \
  --body-md output/合同/审核记录/2026-06-14_7-Labs_合同审核.md \
  --output output/合同/审核记录/2026-06-14_7-Labs_合同审核.pdf \
  --brand-color "#1a365d"
```

## 归档路径

| 模式 | PDF 路径 |
|------|----------|
| A / E | `output/合同/审核记录/YYYY-MM-DD_对方名_合同审核.pdf` |
| B | `output/合同/采购/审核记录/YYYY-MM-DD_供方名_合同审核.pdf` |
| C | `output/合同/人事/审核记录/YYYY-MM-DD_岗位_合同审核.pdf` |
| F / G | `output/合同/股权/审核记录/YYYY-MM-DD_交易方_协议审核.pdf` |

根目录可通过 `LEGAL_AFFAIRS_ARCHIVE_DIR` 或 `setup apply` 配置。

## Agent 流程

1. 按 `review-output-template.md` + `emoji-output-guide.md` 写 Markdown（含 emoji）
2. 保存 `.md` 到归档目录
3. 用户要 PDF → 调用 `render_review_pdf.py` 或 `render_mobile_pdf.py`
4. **推送 PDF 文件**并告知相对路径（不写 `/Users/...` 绝对路径）
5. 文末保留 ⚗️ 免责声明

## 正文要求

- 纯中文 Markdown，保留 emoji 与 🔴🟡🟢 分级
- 结论段用 `📌 结论` 开头
- 宽度/字号由脚本锁定，Agent 不要内联 CSS

## 与跨文化技能的关系

`render_mobile_pdf.py` 自 cross-cultural-consultant vendored，预设 `mobile-default` 版式相同。  
法务默认品牌色 `#1a365d`（深蓝），跨文化常用 `#006341`（绿）——仅视觉区分，版式一致。
