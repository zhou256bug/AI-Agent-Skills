# 首次研发例会实战案例（2026-06-08）

## 背景

菜头发飞书妙记链接 + 发Excel《研发技术专题会议_项目进展报告（两周一次）》，要求首次创建研发例会纪要。

## 关键数据

- 会议时间：2026-06-08 17:57-19:00（63分钟）
- 飞书妙记转录：`/tmp/meeting_rd.txt`（779行，48189 bytes）
- Excel sheet：「工作重点」（15个项目）、「在研项目」（详细进度）、「认证更新项目」
- 纪要路径：`NEWPOS/管理会议/公司研发例会2026-06-08.md`

## 核心观察

### Excel 解析注意

WPS生成的xlsx有非标准fill样式，openpyxl报 `Fill() takes no arguments` 错误。解决：用 `pandas + calamine engine`。

```
pip3 install --break-system-packages python-calamine
sheets = pd.ExcelFile(file, engine="calamine").sheet_names
df = pd.read_excel(file, sheet_name="工作重点", engine="calamine", header=None)
```

### 转录覆盖陷阱

`feishu_minutes.py url` 每次保存到 `/Users/ericstudio/download.txt`。本会话中先后调用了两次 `url`，第一次的研发会议转录被第二次的AI平台会议转录覆盖，丢失了第一次数据。修复方法：每次 `url` 调用后立即 `cp /Users/ericstudio/download.txt /tmp/meeting_rd.txt`，再调第二个。

### 纪要结构

首次研发例会的结构被菜头认可：

1. 公司战略决策（首条放陈总宣布的未来一年停新项目）
2. 项目进度汇报（15项逐条，对照Excel工作重点）
3. 平台与技术进展（NewStore、AI平台、认证）
4. 重要决议（4条）
5. 跟进事项（18项TODO表格）

## 下次会议的链接方式

后续研发例会纪要需要在开头新增「与上次对照」段落，列出各项目从本次到下次之间的进展。TODO责任人需从录音中识别各项目负责人姓名补全。
