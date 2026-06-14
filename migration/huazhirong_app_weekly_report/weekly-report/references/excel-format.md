# 周报 Excel 格式规范与解析要点

## 概述

海外应用开发部周报使用 Excel 格式，由林珊雯 (seven.lin@newpostech.com) 每周发送。附件为 `.xls` 格式，包含多个工作表。

## 文件结构

```
周报附件.xls
├── 目录 (Sheet 0)     - 包含部门名称、期号、员工列表
├── 员工 1 姓名 (Sheet 1)  - 员工 1 的工作记录
├── 员工 2 姓名 (Sheet 2)  - 员工 2 的工作记录
└── ...
```

## 两种 Excel 格式

### 格式 A：表格格式（多列）

**特征：** `ws.ncols > 1`（通常 3-4 列）

**结构示例：**
```
| 行号 | 列 0      | 列 1          | 列 2                              |
|------|----------|---------------|-----------------------------------|
| 0    | (序号)    | 项目名称       | 工作内容                           |
| 1    |          | 巴西分公司     | 出差巴西，沟通巴西目前各项目...     |
| 2    |          | 迪拜中东分公司  | 1.SmartOne 应用内存泄漏问题跟进...  |
| 3    |          | 华智融亚太分公司 | 跟进泰国 E-Merchant 项目...        |
```

**解析逻辑：**
```python
for row in range(1, ws.nrows):  # 跳过标题行
    project = str(ws.cell_value(row, 1)).strip()
    work = str(ws.cell_value(row, 2)).strip()
    if project and work:
        work_items.append(f"{project}: {work}")
```

### 格式 B：文本格式（单列）

**特征：** `ws.ncols == 1`（仅 1 列）

**结构示例：**
```
| 行号 | 列 0                                          |
|------|----------------------------------------------|
| 0    | 代鑫                                          |
| 1    | 工作记录                                       |
| 2    | 项目：日本 BMT-CCT                              |
| 3    | 本周工作记录：                                   |
| 4    | 工作摘要：代鑫 [2026/05/06] 日本 BMT-CCT         |
| 5    | 工作摘要：代鑫 [2026/05/07] 日本 BMT-CCT         |
```

**解析逻辑：**
```python
current_project = ""
for row in range(ws.nrows):
    cell = str(ws.cell_value(row, 0)).strip()
    if cell.startswith('项目:'):
        current_project = cell.replace('项目:', '').strip()
    elif cell.startswith('工作摘要:'):
        summary = cell.replace('工作摘要:', '').strip()
        if current_project:
            work_items.append(f"{current_project}: {summary}")
        else:
            work_items.append(summary)
```

## 解析脚本

主脚本：`~/.hermes/skills/custom/scripts/weekly_report_v2.py`

**关键函数：** `parse_weekly_report(excel_path)`

**自动格式检测：**
```python
if ws.ncols == 1:
    # 文本格式解析
else:
    # 表格格式解析
```

## 常见陷阱

### 1. 使用错误的库
- ❌ `openpyxl` 仅支持 `.xlsx` 格式
- ✅ 使用 `xlrd` 支持 `.xls` 格式

### 2. 跳过标题行
- 表格格式的第 0 行是标题行（列名）
- 从第 1 行开始读取数据

### 3. 空工作表处理
- 某些员工的工作表可能为空或只有标题
- 检查 `work_items` 是否为空再添加到结果

### 4. 项目名称缺失
- 文本格式中，`工作摘要:` 可能出现在 `项目:` 之前
- 需要处理 `current_project` 为空的情况

## 测试验证

```bash
# 解析测试
python ~/.hermes/skills/custom/scripts/weekly_report_v2.py \
  --action parse --week 19 --excel /tmp/week19_report.xls

# 预期输出：
# - 15 名员工
# - 每人有项目名称和工作内容
# - 无空字符串或仅姓名的条目
```

## 更新历史

- **2026-06-13 (第 19 期)**: 发现并修复格式兼容问题
  - 原逻辑：遍历所有单元格收集非空值（导致收集到姓名碎片）
  - 新逻辑：检测列数，分别处理表格格式和文本格式
  - 修复文件：`scripts/weekly_report_v2.py` 的 `parse_weekly_report()` 函数
