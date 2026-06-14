#!/usr/bin/env python3
"""
周报解析技能 v2.0 - 支持关注列表配置

功能：
1. 读取指定发件人的周报邮件
2. 下载并解析 Excel 附件
3. 根据关注列表生成个性化汇报
4. 支持人和项目两种关注类型
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 配置路径
SKILLS_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILLS_DIR / "config" / "focus_list.json"


def load_config():
    """加载关注列表配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "focus_people": [],
        "focus_projects": [],
        "show_others": True,
        "others_format": "compact"
    }


def save_config(config):
    """保存关注列表配置"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def parse_weekly_report(excel_path):
    """解析 Excel 周报（支持两种格式：表格格式和文本格式）"""
    import xlrd
    
    with open(excel_path, 'rb') as f:
        payload = f.read()
    
    wb = xlrd.open_workbook(file_contents=payload)
    
    employees = []
    
    # 遍历所有工作表（跳过目录）
    for sheet_idx in range(1, wb.nsheets):
        ws = wb.sheet_by_index(sheet_idx)
        person_name = ws.name
        
        work_items = []
        
        # 检测格式：如果只有一列，则是文本格式
        if ws.ncols == 1:
            # 文本格式：遍历所有行，提取项目和工作内容
            current_project = ""
            for row in range(ws.nrows):
                cell = str(ws.cell_value(row, 0)).strip()
                if cell.startswith('项目:'):
                    current_project = cell.replace('项目:', '').strip()
                elif cell.startswith('工作摘要:'):
                    # 提取工作摘要
                    summary = cell.replace('工作摘要:', '').strip()
                    if current_project:
                        work_items.append(f"{current_project}: {summary}")
                    else:
                        work_items.append(summary)
        else:
            # 表格格式：列 1=项目名，列 2=工作内容
            for row in range(1, ws.nrows):
                project = str(ws.cell_value(row, 1)).strip() if ws.ncols > 1 else ""
                work = str(ws.cell_value(row, 2)).strip() if ws.ncols > 2 else ""
                
                if project and work:
                    work_items.append(f"{project}: {work}")
                elif work:
                    work_items.append(work)
        
        work_text = '\n'.join(work_items[:10])  # 最多 10 条
        
        if person_name and person_name not in ['目录', 'Sheet1']:
            employees.append({
                'name': person_name,
                'work': work_text[:1000]
            })
    
    return employees


def extract_projects(work_text):
    """从工作内容中提取项目名"""
    projects = []
    # 常见项目关键词
    project_keywords = ['项目', 'APP', '系统', '平台', 'POS', 'NewStore', 'RKI', 'SoftPos']
    
    lines = work_text.split('\n')
    for line in lines[:10]:
        for kw in project_keywords:
            if kw in line:
                # 提取项目名
                if ':' in line:
                    proj = line.split(':')[0].strip()
                    if proj and len(proj) > 2:
                        projects.append(proj)
                break
    
    return list(set(projects))[:3]  # 最多 3 个项目


def generate_report_b(employees, config, week_num, period, department):
    """生成方案 B：关键成果版汇报"""
    
    focus_people = config.get('focus_people', [])
    focus_projects = config.get('focus_projects', [])
    
    lines = []
    
    # 标题
    lines.append(f"📋 工作周报 · 第{week_num}期")
    lines.append(f"🏢 {department}")
    lines.append(f"📅 {period}")
    lines.append("━" * 40)
    lines.append("")
    
    # 您的关注
    lines.append("⭐ 您的关注")
    lines.append("━" * 40)
    
    if not focus_people and not focus_projects:
        lines.append("")
        lines.append("💡 暂无关注配置")
        lines.append("")
        lines.append("📝 如何添加关注：")
        lines.append("直接告诉强仔：")
        lines.append("  • 关注某人：'关注周强'")
        lines.append("  • 关注项目：'关注 NEWSTORE 项目'")
        lines.append("  • 移除关注：'移除关注 XXX'")
        lines.append("")
    else:
        lines.append("")
        
        # 关注的人员
        for person in focus_people:
            emp_data = next((e for e in employees if person in e['name']), None)
            if emp_data:
                lines.append(f"👤 {emp_data['name']}")
                # 提取关键成果
                work_lines = emp_data['work'].split('\n')[:5]
                for wl in work_lines:
                    if wl and len(wl) > 5:
                        lines.append(f"  • {wl[:60]}")
                lines.append("")
        
        # 关注的项目
        if focus_projects:
            lines.append("📁 关注的项目")
            for proj in focus_projects:
                # 找到相关人员和成果
                related = []
                for emp in employees:
                    if proj in emp['work']:
                        related.append(emp['name'])
                if related:
                    lines.append(f"  • {proj}: {', '.join(related[:3])}")
            lines.append("")
    
    lines.append("━" * 40)
    lines.append("")
    
    # 本周概览
    lines.append("📊 本周概览")
    lines.append("━" * 40)
    lines.append(f"• 总人数：{len(employees)} 人")
    
    # 统计项目
    all_projects = []
    for emp in employees:
        projects = extract_projects(emp['work'])
        all_projects.extend(projects)
    
    project_count = {}
    for p in all_projects:
        project_count[p] = project_count.get(p, 0) + 1
    
    top_projects = sorted(project_count.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_projects:
        lines.append(f"• 热门项目：{', '.join([p[0] for p in top_projects])}")
    
    lines.append("")
    lines.append("━" * 40)
    lines.append("")
    
    # 重点成果
    lines.append("🔴 重点成果（Top 5）")
    lines.append("━" * 40)
    lines.append("")
    
    # 简单按工作内容长度排序（越长越重要）
    sorted_employees = sorted(employees, key=lambda x: len(x['work']), reverse=True)
    
    for i, emp in enumerate(sorted_employees[:5], 1):
        lines.append(f"{i}️⃣ {emp['name']}")
        work_preview = emp['work'].split('\n')[0][:80]
        lines.append(f"   {work_preview}")
        lines.append("")
    
    lines.append("━" * 40)
    lines.append("")
    lines.append("✅ 周报整理完成")
    
    return '\n'.join(lines)


def update_focus(focus_type, name, action='add'):
    """更新关注列表"""
    config = load_config()
    
    if focus_type == 'person':
        key = 'focus_people'
    elif focus_type == 'project':
        key = 'focus_projects'
    else:
        return False, "不支持的关注类型"
    
    if action == 'add':
        if name not in config[key]:
            config[key].append(name)
            save_config(config)
            return True, f"已添加关注：{name}"
        else:
            return False, f"{name} 已在关注列表中"
    
    elif action == 'remove':
        if name in config[key]:
            config[key].remove(name)
            save_config(config)
            return True, f"已移除关注：{name}"
        else:
            return False, f"{name} 不在关注列表中"
    
    return False, "未知操作"


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='周报解析技能 v2.0')
    parser.add_argument('--action', choices=['parse', 'add_focus', 'remove_focus', 'list_focus'],
                        default='parse', help='操作类型')
    parser.add_argument('--type', choices=['person', 'project'],
                        help='关注类型')
    parser.add_argument('--name', help='人员或项目名称')
    parser.add_argument('--week', default='23', help='周报期号')
    parser.add_argument('--excel', help='Excel 文件路径')
    args = parser.parse_args()
    
    if args.action == 'add_focus':
        if not args.type or not args.name:
            print("❌ 错误：需要指定 --type 和 --name")
            return 1
        success, msg = update_focus(args.type, args.name, 'add')
        print(f"{'✅' if success else '⚠️'}  {msg}")
        return 0 if success else 1
    
    elif args.action == 'remove_focus':
        if not args.type or not args.name:
            print("❌ 错误：需要指定 --type 和 --name")
            return 1
        success, msg = update_focus(args.type, args.name, 'remove')
        print(f"{'✅' if success else '⚠️'}  {msg}")
        return 0 if success else 1
    
    elif args.action == 'list_focus':
        config = load_config()
        print("📋 当前关注列表")
        print("━" * 40)
        print(f"关注的人员：{', '.join(config.get('focus_people', ['无'])) or '无'}")
        print(f"关注的项目：{', '.join(config.get('focus_projects', ['无'])) or '无'}")
        return 0
    
    elif args.action == 'parse':
        if not args.excel:
            print("❌ 错误：需要指定 --excel 文件路径", file=sys.stderr)
            return 1
        
        employees = parse_weekly_report(args.excel)
        config = load_config()
        
        report = generate_report_b(
            employees,
            config,
            week_num=args.week,
            period="2026.06.01-06.07",
            department="海外应用开发部"
        )
        
        print(report)
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
