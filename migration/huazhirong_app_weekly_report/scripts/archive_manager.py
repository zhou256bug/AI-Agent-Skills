#!/usr/bin/env python3
"""
周报归档目录管理

目录结构：
~/Documents/weekly-reports/
├── 2026/
│   ├── week-22/
│   │   ├── week-22.md
│   │   ├── week-22.html
│   │   └── week-22.pdf
│   ├── week-23/
│   │   └── ...
│   └── week-24/
└── 2027/
    └── ...
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def get_archive_dir(week_num, year=None):
    """获取归档目录路径"""
    if year is None:
        year = datetime.now().year
    
    base_dir = Path.home() / "Documents" / "weekly-reports" / str(year)
    week_dir = base_dir / f"week-{week_num}"
    
    return week_dir


def create_archive_dir(week_num, year=None):
    """创建归档目录"""
    week_dir = get_archive_dir(week_num, year)
    week_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建归档目录：{week_dir}")
    return week_dir


def save_report(content, week_num, filename="report", year=None):
    """保存汇报文件"""
    week_dir = get_archive_dir(week_num, year)
    week_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    # 保存 Markdown
    md_path = week_dir / f"{filename}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    saved_files.append(str(md_path))
    
    # 保存 HTML（如果 content 是 HTML 格式）
    if content.strip().startswith('<!DOCTYPE'):
        html_path = week_dir / f"{filename}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        saved_files.append(str(html_path))
    
    return saved_files


def list_archives(year=None):
    """列出所有归档"""
    if year is None:
        year = datetime.now().year
    
    base_dir = Path.home() / "Documents" / "weekly-reports" / str(year)
    
    if not base_dir.exists():
        print(f"📁 {year} 年暂无归档")
        return []
    
    weeks = sorted([d.name for d in base_dir.iterdir() if d.is_dir()])
    
    print(f"📋 {year} 年周报归档 ({len(weeks)} 期):")
    for week in weeks:
        week_dir = base_dir / week
        files = list(week_dir.glob("*"))
        print(f"  {week}: {len(files)} 个文件")
        for f in files[:3]:
            size = f.stat().st_size
            size_str = f"{size/1024:.1f}K" if size < 1024*1024 else f"{size/1024/1024:.1f}M"
            print(f"    - {f.name} ({size_str})")
    
    return weeks


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='周报归档目录管理')
    parser.add_argument('--action', choices=['create', 'list', 'path'], default='list')
    parser.add_argument('--week', type=int, help='周报期号')
    parser.add_argument('--year', type=int, help='年份')
    args = parser.parse_args()
    
    if args.action == 'create':
        if not args.week:
            print("❌ 错误：需要指定 --week")
            sys.exit(1)
        create_archive_dir(args.week, args.year)
    
    elif args.action == 'list':
        list_archives(args.year)
    
    elif args.action == 'path':
        if not args.week:
            print("❌ 错误：需要指定 --week")
            sys.exit(1)
        week_dir = get_archive_dir(args.week, args.year)
        print(f"📁 {week_dir}")
