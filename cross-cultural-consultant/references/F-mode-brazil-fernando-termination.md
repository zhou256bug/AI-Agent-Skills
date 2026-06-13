# F 模式参考示例：巴西 Fernando 解约谈判

> 场景：需解约海外顾问/经销商合同时的谈判策略生成流程
> 数据来源：2026-06-02 菜头 × Fernando Geraldeli（巴西）解约咨询

## 合同分析要点

收到海外合同 PDF 后，提取以下核心条款：

| 条款 | 说明 |
|:--|:--|
| 合同性质 | 顾问/经销/代理？确认是个人还是公司合同 |
| 签约方 | 谁签的？母子公司结构 |
| 期限 | 何时到期、自动续约条件 |
| 月费/佣金 | 固定费用+业绩奖金结构 |
| **通知期** | 提前多少天通知、通知期内薪酬是否照付 |
| **锁定条款** | 是否有不得解约的锁定期（Anexo / Schedule） |
| 管辖法律 | 哪国法律、仲裁地 |
| 终止后义务 | 保密、赔偿、保险的持续期限 |

## 跨文化谈判策略生成流程

### 第一步：锁定条款分析

检查是否有"A公司不得在某日期前解约"的条款（锁定条款）。锁定条款禁止的是"解除行为本身"而非"通知行为"：

- **合规做法**：在锁定期内发送通知，约定终止日在锁定期之后
- **违规做法**：在锁定期内发送通知约定终止日在锁定期内

### 第二步：对方画像

用 Hofstede 数据（特别是 UA 和 LTO）校准菜头对人的判断：

| 菜头说 | Hofstede 验证 | 谈判影响 |
|:--|:--|:--|
| 谨小慎微 | UA=76（高不确定性规避）| 需要精确、书面、合规，模糊=焦虑 |
| 正直 | 符合集体主义注重规范 | 真诚比话术管用 |
| 守规矩 | UA=76 | 先让他自己确认合同条款 |
| 不够灵活 | LTO=28（短期导向）| 不接受"先做再调"，要短期确定结果 |

### 第三步：推荐话术结构

1. **开场**：一起翻合同，让对方自己确认条款
2. **提方案**：我方的建议方案（精确日期、费用照付）
3. **回应质疑**：准备好几个对方可能问的问题的回答
4. **过渡方案**：已发货/未交付订单、客户交接、售后支持

### 第四步：生成会前 PDF

用 pdfprint 生成 A4 PDF，包含：
- 合同核心条款速查表
- 时间线
- Hofstede 跨文化对照表
- 推荐话术（英文，可直接念）
- 会后待办清单
- ⚠️ 不要做的事

存档路径：`newpos/{地区}/{人物}_解约谈判备忘录_日期.pdf`

## 巴西解约话术（参考）

**开场（让对方确认条款）**：
> "Fernando, let's look at Anexo II — it says we cannot terminate before September 8, 2026. My reading is: if I give notice now, the effective date should be no earlier than September 8. Is that how you interpret it?"

**提方案**：
> "I give formal notice today, we set the termination date as September 10, 2026. This respects the lock-in period and gives you 90+ days to prepare. Your monthly fee continues through the notice period as per Clause 2.2."

**回应"为什么解约"**（不用业绩说事）：
> "This is about strategic alignment, not performance. The Brazilian entity will continue. Your consulting role has reached a natural conclusion point."

## ⚠️ 不要做的事

- 不用业绩不好当理由谈解约（高UA的人会用合规杠回来）
- 不绕开通知期费用（写死的条款）
- 不在会议上编数字（不知道的说"I'll confirm"）
- 不用微信/中文谈正式解约（全部走Email书面确认）
- 不在锁定条款期内发"终止日为锁定期之前"的通知

## 输出 PDF 检查清单

- [ ] 合同条款表（含锁定条款原文）
- [ ] 时间线（含关键节点：发票、付款、锁定期止、终止日）
- [ ] Hofstede 对照表（中国vs目标国，标Delta>30）
- [ ] 可直接念的英文话术
- [ ] 会后待办清单
- [ ] ⚠️ 不要做的事
- [ ] 文件存 newpos/{地区}/
