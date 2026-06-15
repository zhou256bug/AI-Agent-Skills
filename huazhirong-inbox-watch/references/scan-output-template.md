# 扫描摘要输出模板

```markdown
# 📬 收件箱扫描 · {时间}

**{公司}** · 汇报给 **{老板}**

## 📌 结论

未读 **{N}** 封，过滤系统邮件后真人邮件 **{M}** 封。

## 🔴 真人未读（需关注）

- ⭐ **{发件人}** · {日期}
  - 主题：{主题} · 策略：**read_full**
  - 📎 附件：{文件名}
  - 预览：{前200字}…

## 🟡 系统/营销未读（已过滤统计）

共 {K} 封，默认不展开。

## 👉 下一步

- 关注人：mail_tool.py read --uid {UID}
- 附件：mail_tool.py attachments_match --sender ...
```

校验：`python3 scripts/validate_scan_output.py --file <摘要.md>`
