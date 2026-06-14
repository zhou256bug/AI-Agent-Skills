# C 模式会后 CRM 工作流（单 Agent 闭环）

> **铁律**：名片录入、档案更新、会议纪要 **均由运行本 skill 的 Agent 自行完成**（文件工具写 `output/crm/`）。  
> **禁止**：`delegate_task`、`hermes -p …`、调用其他 skill/profile、写入仓库外绝对路径。

## 何时加载

用户触发 **C 来访接待**，且进入会后阶段（名片、纪要、档案、跟进）时，与 `references/C-mode-cielo-*` 一并按需加载。

## 流程（T+0 ~ T+3）

### 1. 名片收网

1. 用户提供名片照片路径或附件。
2. **OCR（推荐稳定路径）**：

```bash
python3 scripts/ocr_card.py --image /path/to/card.jpg --lang chi_sim+eng
```

可选：将原图复制到 CRM 附件目录：

```bash
python3 scripts/ocr_card.py --image /path/to/card.jpg \
  --save-attachment "output/crm/附件/{姓名}_{公司}.jpg"
```

3. 若 `ocr_card.py` 退出码 2（未安装 tesseract），Agent 用**识图**读取名片，或请用户粘贴文字。
4. Agent 按 `references/crm-card-note-template.md` 写入名片笔记。
5. 更新 `output/crm/客户信息/{国家}-{客户}.md` 联系人表。

### 2. 会议纪要

按 `references/crm-meeting-note-template.md` 写入 `output/crm/Meetings/…`，并与客户主档案、相关名片笔记双向链接（相对路径或 `[[wikilink]]` 风格即可）。

### 3. 跟进执行

- 生成英文跟进邮件/消息草稿（跨文化技能核心产出）。
- 强调书面时间表、已确认行动项（适配高 UA 来访国别）。

## 可选系统依赖

| 组件 | 用途 | 缺失时 |
|------|------|--------|
| `tesseract` + 语言包 `chi_sim`/`eng` | `ocr_card.py` 稳定 OCR | 退出码 2；改 Agent 识图 |
| Python 3 | 脚本 | 必备 |

无需其他 skill、凭据或 Obsidian 插件。
