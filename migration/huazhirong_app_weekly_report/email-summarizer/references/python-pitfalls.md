# Python 变量作用域陷阱

## 问题：循环变量覆盖函数名

### 症状

```
UnboundLocalError: cannot access local variable 'group_emails' 
where it is not associated with a value
```

### 根本原因

在函数内部使用循环时，**循环变量名与已定义的函数名冲突**，导致函数名被覆盖。

### 错误示例

```python
def format_report(data, args):
    emails = data.get('emails', [])
    
    # 定义了一个函数
    def group_emails(emails, group_by):
        # ... 分组逻辑
        return groups
    
    # ❌ 错误：循环变量名与函数名相同
    for group_name, group_emails in groups.items():
        # 这里 group_emails 已经被重新绑定为列表值
        # 不再是上面的函数！
        
        # 如果后续代码尝试调用 group_emails(...)
        # 会触发 UnboundLocalError
        for email in group_emails[:10]:  # 这里可以正常使用
            pass
        
        # 但如果尝试：
        result = group_emails(other_emails, 'sender')  
        # ❌ UnboundLocalError!
```

### 正确示例

```python
def format_report(data, args):
    emails = data.get('emails', [])
    
    def group_emails(emails, group_by):
        # ... 分组逻辑
        return groups
    
    # ✅ 正确：使用不同的变量名
    for group_name, group_list in groups.items():
        # group_list 不会覆盖任何函数
        for email in group_list[:10]:
            pass
        
        # 函数仍然可用
        result = group_emails(other_emails, 'sender')  # ✅ 正常工作
```

### 常见冲突模式

| 函数名 | 冲突的循环变量 | 建议的变量名 |
|--------|---------------|-------------|
| `group_emails` | `group_emails` | `group_list`, `mail_group`, `email_batch` |
| `parse_email` | `parse_email` | `parsed`, `email_data`, `result` |
| `format_report` | `format_report` | `report`, `output`, `formatted` |
| `extract_data` | `extract_data` | `data`, `extracted`, `item` |

### 预防措施

1. **命名约定**
   - 函数名：使用动词开头（`parse_*`, `format_*`, `extract_*`）
   - 循环变量：使用名词（`item`, `data`, `list`, `group`）

2. **代码审查检查点**
   - 检查 `for X, Y in ...` 中的变量名
   - 确认不与已定义函数同名
   - 特别关注嵌套函数

3. **使用 Linter**
   ```bash
   # Pyright 会检测这类问题
   pyright script.py
   
   # 在 VSCode 中启用 Python 语言服务器
   ```

### 调试技巧

当遇到 `UnboundLocalError` 时：

```python
# 1. 打印变量类型
print(type(group_emails))  # 如果是 list，说明被覆盖了

# 2. 检查作用域
import inspect
print(inspect.currentframe().f_locals)  # 查看局部变量

# 3. 查找冲突
# 搜索代码中所有 group_emails 的出现
# grep -n "group_emails" script.py
```

### 相关案例

本技能中的实际案例：
- 文件：`scripts/summarize.py`
- 问题：`for group_name, group_emails in groups.items()`
- 修复：改为 `for group_name, group_list in groups.items()`
- 提交：`fix: 修复 summarize.py 变量作用域冲突`

## 其他作用域陷阱

### 1. 嵌套函数的变量捕获

```python
def outer():
    x = 10
    def inner():
        print(x)  # ✅ 可以访问外部变量
    inner()

def outer2():
    x = 10
    def inner2():
        x = 20  # ❌ 创建了新的局部变量 x
        print(x)  # 输出 20
    inner2()
    print(x)  # 输出 10 (不是 20)
```

### 2. 闭包中的延迟绑定

```python
# ❌ 错误：所有函数都引用同一个 i
funcs = []
for i in range(5):
    funcs.append(lambda: i)

print([f() for f in funcs])  # [4, 4, 4, 4, 4]

# ✅ 正确：使用默认参数捕获当前值
funcs = []
for i in range(5):
    funcs.append(lambda x=i: x)

print([f() for f in funcs])  # [0, 1, 2, 3, 4]
```

## 相关文件

- `email-summarizer/scripts/summarize.py` - 修复后的脚本
- `email-summarizer/SKILL.md` - 包含此陷阱的说明
