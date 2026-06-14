# Management Weekly Report Skill

> **版本**: 1.0.0
> **适用对象**: 管理团队周报汇编——收件箱取信 → 四段 Markdown → 手机长条 PDF → 多通道投递
> **开箱即用**: OpenClaw / Hermes / Cursor clone 后配置 IMAP 凭据即可跑；脚本纯标准库，PDF 为可选依赖（注册见 `references/openclaw-hermes-registration.md`）

---

## 这个 skill 解决什么

| 阶段 | 你的需求 | skill 给你 |
|------|---------|-----------|
| **fetch** | 从收件箱抓源周报邮件 + xlsx | `fetch_mail.py`（通用 IMAP，自动） |
| **compose** | 把 xlsx 汇编成老板可读的四段总结 | Agent 写 Markdown（格式见 `references/content-format.md`） |
| **render** | 手机一列到底的长条 PDF | `render_mobile_pdf.py --preset weekly-report`（可选依赖） |
| **deliver** | 推送给老板（微信/企微/飞书） | `deliver.py` 多通道，默认 `wechat-bridge`（有回执） |

一条命令 `run_weekly.py` 编排全程，**失败可断点续跑**（取信成功跳取信、限流只补推送）。

---

## 配置（全部可参数化）

业务默认值面向华智融实例，**均可环境变量或 `local/credentials.env` 覆盖**（见 `scripts/weekly_report_config.py`）：

| 配置 | 环境变量 | 默认 |
|------|----------|------|
| 收件人（老板） | `WEEKLY_REPORT_OWNER` | 老板 |
| 源发件人 | `WEEKLY_REPORT_SENDER_EMAIL` | evyn.chen@newpostech.com |
| 主题关键词 | `WEEKLY_REPORT_SUBJECT_KEY` | 总裁办及各部门经理周报 |
| 公司名 | `WEEKLY_REPORT_COMPANY` | 华智融 |
| 归档目录 | `WEEKLY_REPORT_ARCHIVE_DIR` | `<skill>/output` |
| 取信 IMAP | `WEEKLY_REPORT_IMAP_*` | **必备** |
| 微信投递 | `WEIXIN_BRIDGE_URL` / `WEIXIN_TO` | localhost:9100 / — |

```bash
cp credentials.env.example local/credentials.env   # 填 IMAP + WEIXIN_TO
python3 scripts/weekly_report_config.py             # 打印生效配置（密码脱敏）
```

---

## 本地归档（`output/`）

默认落在技能目录 `output/`（`.gitignore`，不入库）：

```
output/
├── input/W{N}.xlsx                 # 取信下载的 xlsx
├── W{N}-YYYY年MM月DD日.md / .pdf    # 汇编产物
└── .state/W{N}.json                # 断点续跑状态
```

---

## 一条命令（推荐）

```bash
python3 scripts/run_weekly.py                      # 自动识别期号
python3 scripts/run_weekly.py --period 23          # 指定期号
python3 scripts/run_weekly.py --force-stage deliver  # 仅补推送（限流后）
```

终态 `STATE:<X>`：`DELIVERED` / `NEED_COMPOSE` / `FETCH_WAIT` / `DELIVER_RETRY` / `FAIL_NOTIFY`（详见 `SKILL.md` §二）。

---

## 目录结构

```
huazhirong-management-weekly-report/
├── SKILL.md                         # 主规则 + 编排说明
├── README.md / CHANGELOG.md / .gitignore
├── credentials.env.example
├── local/                           # 本地凭据（gitignore）
├── agents/ / bundles/
├── references/
│   ├── content-format.md            # 四段 Markdown 格式
│   ├── email-and-xlsx.md            # 取信规则
│   ├── delivery-channels.md         # 投递通道与微信发文件机制
│   ├── cron-retry.md                # 可选定时节奏
│   └── openclaw-hermes-registration.md
└── scripts/
    ├── run_weekly.py                # 编排器（fetch→compose→render→deliver）
    ├── fetch_mail.py                # 取信（必备，纯标准库）
    ├── state.py                     # 断点续跑状态
    ├── weekly_report_config.py      # 配置中心
    ├── validate_weekly_report_md.py
    ├── transform_report_md.py       # 旧五段→四段
    ├── render_mobile_pdf.py         # 手机 PDF（可选 weasyprint/gs/PyMuPDF）
    ├── deliver.py                   # 多通道投递
    └── run_acceptance.py            # 验收套件（44 项）
```

---

## 可选依赖

| 能力 | 依赖 | 缺失时 |
|------|------|--------|
| 手机 PDF | weasyprint、ghostscript、PyMuPDF、Noto Sans SC | 止于 Markdown，编排器 `FAIL_NOTIFY` |
| 微信自动化投递 | hermes-weixin bridge + `WEIXIN_TO` | 改 `wechat-media`（无回执）或 wecom/feishu |
| 取信 | 任意 IMAP 收件箱凭据 | `FETCH_WAIT` / `FAIL_NOTIFY` |

---

## 安装与自检

```bash
git clone https://github.com/zhou256bug/AI-Agent-Skills.git ~/Projects/AI-Agent-Skills
cd huazhirong-management-weekly-report
cp credentials.env.example local/credentials.env   # 按需填写

python3 scripts/run_acceptance.py                # 44 项，无需凭据
```

---

## 四段结构速查

1. **重点项目进展**（每项目 `> 周报来源：**姓名**`）
2. **海外市场要闻**（老板行程/来访并入此处，不单设第一节）
3. **业务线重点关注**
4. **需{老板}关注的事项**

禁止：ISO 日历周编号、单独「老板本周重点」段（校验器会拦截）。

---

## 注意事项

- **compose 需 Agent**：xlsx→四段 Markdown 不能全自动；编排器返回 `NEED_COMPOSE` 时由 Agent 写完 MD 再重跑
- `transform_report_md.py` 的 `PROJECT_SOURCES` 为华智融默认项目映射，换公司需改脚本（P2 计划外置）
- 不绑定 iCloud/Obsidian/`$HERMES_HOME` 路径
