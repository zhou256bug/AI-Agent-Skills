# IMAP 搜索参数故障排查

## 问题：SEARCH command error

### 症状

```json
{"success": false, "error": "处理失败：SEARCH command error: BAD [b'invalid command or parameters']"}
```

### 根本原因

IMAP 搜索命令的参数组合不正确，某些参数不能同时使用。

### 已知的参数冲突

#### 冲突 1：`--from` + `--since`

**错误示例：**
```bash
python fetch_emails.py \
  --from "seven.lin@newpostech.com" \
  --since "1 hour ago"
# ❌ SEARCH command error
```

**原因：** IMAP 协议的 `FROM` 和 `SINCE` 组合在某些服务器上不被支持。

**解决方案：**
```bash
# 方案 1：只用 --from，手动过滤时间
python fetch_emails.py --from "seven.lin@newpostech.com" --limit 50

# 方案 2：只用 --since，手动过滤发件人
python fetch_emails.py --since "2026-06-01" --limit 50

# 方案 3：不使用搜索参数，获取后在代码中过滤
python fetch_emails.py --limit 50 --output /tmp/emails.json
# 然后用 Python 脚本过滤
```

#### 冲突 2：`--subject` + 其他参数

**错误示例：**
```bash
python fetch_emails.py \
  --subject "周报" \
  --unread \
  --since "2026-06-01"
# ❌ 可能失败
```

**解决方案：** 减少参数组合，分步获取。

### 推荐的搜索策略

#### 策略 1：宽泛搜索 + 代码过滤（推荐）

```bash
# 获取最近的邮件
python fetch_emails.py \
  --since "2026-06-01" \
  --limit 50 \
  --output /tmp/emails.json

# 用 Python 过滤
python3 << 'EOF'
import json
with open('/tmp/emails.json') as f:
    data = json.load(f)

# 过滤特定发件人
for email in data['emails']:
    if 'seven.lin' in email.get('from', '').lower():
        print(email.get('subject'))
EOF
```

#### 策略 2：单一参数搜索

```bash
# 只按发件人搜索
python fetch_emails.py --from "seven.lin@newpostech.com" --limit 10

# 只按时间搜索
python fetch_emails.py --since "2026-06-01" --limit 50

# 只按未读状态搜索
python fetch_emails.py --unread --limit 20
```

#### 策略 3：使用邮件 ID 直接获取

如果已知邮件 ID：

```bash
# 需要修改脚本支持 --email-id 参数
# 或直接用 IMAP 命令
```

### 阿里企业邮箱的特殊限制

根据实际测试，阿里企业邮箱（`imap.qiye.aliyun.com`）有以下限制：

| 参数组合 | 状态 | 说明 |
|---------|------|------|
| `--from` alone | ✅ 正常 | |
| `--since` alone | ✅ 正常 | |
| `--unread` alone | ✅ 正常 | |
| `--from` + `--since` | ❌ 失败 | 不支持组合 |
| `--from` + `--subject` | ❌ 失败 | 不支持组合 |
| `--unread` + `--since` | ✅ 正常 | 可以组合 |

### 调试步骤

1. **测试基本连接**
   ```bash
   python fetch_emails.py --test-connection
   ```

2. **测试单一参数**
   ```bash
   python fetch_emails.py --limit 5 --pretty
   ```

3. **逐步添加参数**
   ```bash
   # 先测试 --since
   python fetch_emails.py --since "2026-06-01" --limit 5
   
   # 再测试 --from
   python fetch_emails.py --from "test@example.com" --limit 5
   
   # 如果都正常，尝试组合
   python fetch_emails.py --since "2026-06-01" --limit 5
   ```

4. **查看 IMAP 日志**
   ```bash
   # 在脚本中添加调试输出
   python fetch_emails.py --debug
   ```

### 替代方案

#### 方案 1：使用 himalaya CLI

```bash
# himalaya 是终端邮件客户端
himalaya list --folder INBOX --limit 50

# 过滤特定发件人
himalaya list --from "seven.lin@newpostech.com"
```

#### 方案 2：使用 Python imaplib 直接操作

```python
import imaplib

mail = imaplib.IMAP4_SSL('imap.qiye.aliyun.com', 993)
mail.login('user@company.com', 'password')
mail.select('INBOX')

# 简单搜索
status, messages = mail.search(None, 'FROM "seven.lin@newpostech.com"')
# 或
status, messages = mail.search(None, '(SINCE "01-Jun-2026")')
```

### 相关文件

- `email-reader/scripts/fetch_emails.py` - 邮件读取脚本
- `email-reader/SKILL.md` - 邮件读取技能
- `references/qiye-aliyun-imap.md` - 阿里企业邮箱配置

## 最佳实践总结

1. **避免复杂搜索参数组合** - 尤其是 `--from` + `--since`
2. **宽泛获取 + 代码过滤** - 更灵活，更可靠
3. **测试单一参数** - 确认基本功能正常
4. **使用 --debug 参数** - 查看详细错误信息
5. **考虑服务器差异** - 不同邮箱服务商支持不同的搜索语法
