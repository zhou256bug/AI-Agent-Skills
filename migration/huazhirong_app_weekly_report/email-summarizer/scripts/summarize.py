#!/usr/bin/env python3
"""
Email Summarizer - 整理和汇总邮件生成汇报（移动端优化版）

用法:
    cat emails.json | python summarize.py --mobile-friendly [选项]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description='整理和汇总邮件生成汇报（移动端优化）')
    
    # 输入输出
    parser.add_argument('--input', default=None,
                        help='输入文件路径（JSON），默认从 stdin 读取')
    parser.add_argument('--output', default=None,
                        help='输出文件路径，默认输出到 stdout')
    parser.add_argument('--format', choices=['markdown', 'text', 'json', 'mobile'],
                        default='mobile', help='输出格式（默认 mobile 优化）')
    
    # 整理选项
    parser.add_argument('--group-by', choices=['sender', 'subject', 'priority', 'none'],
                        default='priority', help='分组方式（默认按优先级）')
    parser.add_argument('--highlight-keywords', default='紧急，urgent,ASAP，立刻，马上，重要，important，优先，priority',
                        help='高亮关键词（逗号分隔）')
    parser.add_argument('--max-subject-length', type=int, default=40,
                        help='主题最大长度（字符）')
    parser.add_argument('--max-summary-length', type=int, default=100,
                        help='摘要最大长度（字符）')
    parser.add_argument('--max-emails', type=int, default=20,
                        help='最多显示的邮件数量（避免过长）')
    
    # 输出控制
    parser.add_argument('--silent-if-empty', action='store_true',
                        help='无邮件时静默输出 [SILENT]')
    parser.add_argument('--include-attachments', action='store_true',
                        help='包含附件信息')
    parser.add_argument('--compact', action='store_true',
                        help='紧凑模式（减少空行）')
    
    # 调试
    parser.add_argument('--debug', action='store_true',
                        help='启用调试模式')
    
    return parser.parse_args()


def detect_priority(subject, body, keywords):
    """检测邮件优先级"""
    text = (subject + ' ' + body).lower()
    
    # 紧急关键词
    urgent_keywords = ['紧急', 'urgent', ' asap ', '立刻', '马上', 'immediately', '急']
    for kw in urgent_keywords:
        if kw.lower() in text:
            return 'urgent'
    
    # 重要关键词
    important_keywords = ['重要', 'important', '优先', 'priority', 'critical', '请处理']
    for kw in important_keywords:
        if kw.lower() in text:
            return 'important'
    
    return 'normal'


def detect_tags(subject, body):
    """检测邮件标签"""
    text = (subject + ' ' + body).lower()
    tags = []
    
    tag_keywords = {
        '会议': ['会议', 'meeting', '参会', '会议室', 'conference'],
        '待办': ['待办', 'todo', '请处理', '需要', 'action'],
        '回复': ['回复', 'reply', '请确认', '请反馈', 'confirm'],
        '批准': ['批准', '审批', 'approve', '审核', 'approval'],
        '项目': ['项目', 'project', '进度', '开发', 'sprint'],
        '告警': ['告警', 'alert', '警告', 'warning', 'alarm'],
        '系统': ['系统', 'system', '备份', 'backup', '通知', 'notification'],
        '财务': ['财务', '付款', '发票', '报销', 'budget'],
        '人事': ['人事', '任命', '招聘', 'hr', '入职'],
    }
    
    for tag, keywords in tag_keywords.items():
        for kw in keywords:
            if kw.lower() in text:
                tags.append(tag)
                break
    
    return tags


def truncate_text(text, max_length):
    """截断文本，保持可读性"""
    if not text:
        return ""
    
    # 清理 HTML 标签
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 中英文混合处理
    if len(text) > max_length:
        # 尝试在句子边界截断
        for sep in ['。', '！', '？', '.', '!', '?', '…']:
            pos = text[:max_length].rfind(sep)
            if pos > max_length // 2:
                return text[:pos + 1] + '…'
        return text[:max_length - 2] + '…'
    
    return text


def simplify_sender(sender):
    """简化发件人显示"""
    if not sender:
        return "未知"
    
    # 提取名称部分
    if '<' in sender:
        name = sender.split('<')[0].strip().strip('"').strip()
        if name:
            return name
    
    # 提取邮箱前缀
    if '@' in sender:
        prefix = sender.split('@')[0]
        # 去除引号和特殊字符
        prefix = prefix.strip('"').strip()
        # 尝试转换为中文显示
        if '.' in prefix:
            # 可能是 name.surname 格式
            parts = prefix.split('.')
            if len(parts) == 2:
                return f"{parts[0]}{parts[1][0]}."
        return prefix
    
    return sender[:20]


def group_emails(emails, group_by):
    """按指定方式分组邮件"""
    if group_by == 'none' or not emails:
        return {'other': emails}
    
    groups = defaultdict(list)
    
    for email in emails:
        if group_by == 'sender':
            key = simplify_sender(email.get('from', 'unknown'))
            groups[key].append(email)
        
        elif group_by == 'subject':
            subject = email.get('subject', '(无主题)')
            subject = subject.replace('Re:', '').replace('Fwd:', '').strip()
            key = subject[:30] if len(subject) > 30 else subject
            groups[key].append(email)
        
        elif group_by == 'priority':
            priority = email.get('_priority', 'normal')
            priority_map = {
                'urgent': '🔴 紧急',
                'important': '🟡 重要',
                'normal': '📩 普通'
            }
            key = priority_map.get(priority, '📩 普通')
            groups[key].append(email)
    
    return dict(groups)


def format_mobile_report(data, args):
    """生成移动端优化的汇报格式"""
    emails = data.get('emails', [])
    
    # 无邮件时的处理
    if not emails:
        if args.silent_if_empty:
            return '[SILENT]'
        else:
            return "📧 邮件汇报\n\n暂无新邮件\n"
    
    # 限制邮件数量
    if len(emails) > args.max_emails:
        emails = emails[:args.max_emails]
        truncated = True
        truncated_count = len(data.get('emails', [])) - args.max_emails
    else:
        truncated = False
        truncated_count = 0
    
    # 统计信息
    total_count = len(emails)
    urgent_count = sum(1 for e in emails if e.get('_priority') == 'urgent')
    important_count = sum(1 for e in emails if e.get('_priority') == 'important')
    attachment_count = sum(1 for e in emails if e.get('attachments'))
    
    # 生成时间
    generated_at = datetime.now().strftime('%m-%d %H:%M')
    
    # 构建汇报
    lines = []
    
    # 标题栏（紧凑）
    lines.append(f"📧 邮件汇报 · {generated_at}")
    if not args.compact:
        lines.append("")
    
    # 概览（单行显示）
    overview = f"📊 共{total_count}封"
    if urgent_count > 0:
        overview += f" | 🔴{urgent_count}"
    if important_count > 0:
        overview += f" | 🟡{important_count}"
    if attachment_count > 0:
        overview += f" | 📎{attachment_count}"
    if truncated:
        overview += f" | …还有{truncated_count}封"
    
    lines.append(overview)
    lines.append("━" * 20)
    
    # 分组显示
    groups = group_emails(emails, args.group_by)
    
    # 优先级排序：紧急 → 重要 → 普通
    priority_order = {'🔴 紧急': 0, '🟡 重要': 1, '📩 普通': 2}
    sorted_groups = sorted(groups.items(), key=lambda x: priority_order.get(x[0], 99))
    
    for group_name, group_list in sorted_groups:
        # 分组标题
        lines.append(f"\n{group_name} ({len(group_list)})")
        lines.append("─" * 15)
        
        for email in group_list[:10]:  # 每组最多显示 10 封
            subject = email.get('subject', '(无主题)')
            subject = truncate_text(subject, args.max_subject_length)
            
            # 发件人（简化）
            sender = simplify_sender(email.get('from', ''))
            
            # 时间
            date = email.get('date', '')
            if date:
                try:
                    dt = datetime.fromisoformat(date)
                    # 今天显示时间，其他显示日期
                    if dt.date() == datetime.now().date():
                        date_str = dt.strftime('%H:%M')
                    else:
                        date_str = dt.strftime('%m-%d')
                except Exception:
                    date_str = ''
            else:
                date_str = ''
            
            # 邮件行：[时间] 主题 @发件人
            line = f"• [{date_str}] {subject}"
            if len(sender) <= 6:  # 短名称才显示
                line += f" @{sender}"
            lines.append(line)
            
            # 标签（紧凑显示）
            tags = email.get('_tags', [])
            if tags:
                tag_str = ' '.join([f'#{tag}' for tag in tags[:3]])  # 最多 3 个标签
                lines.append(f"  {tag_str}")
            
            # 附件提示
            if args.include_attachments and email.get('attachments'):
                att_count = len(email['attachments'])
                lines.append(f"  📎 {att_count}个附件")
            
            # 紧凑模式下减少空行
            if not args.compact:
                lines.append("")
    
    # 底部提示
    lines.append("━" * 20)
    if truncated:
        lines.append(f"💡 还有{truncated_count}封邮件未显示，请登录邮箱查看完整列表")
    else:
        lines.append("✅ 已全部显示")
    
    return '\n'.join(lines)


def format_markdown_report(data, args):
    """生成标准 Markdown 格式汇报（备用）"""
    # 简单实现，使用 mobile 格式作为基础
    return format_mobile_report(data, args)


def format_text_report(data, args):
    """生成纯文本格式汇报"""
    return format_mobile_report(data, args)


def main():
    args = parse_args()
    
    # 读取输入
    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({
            'success': False,
            'error': f'JSON 解析失败：{e}'
        }, ensure_ascii=False), file=sys.stderr)
        return 1
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'读取输入失败：{e}'
        }, ensure_ascii=False), file=sys.stderr)
        return 1
    
    # 验证输入格式
    if not data.get('success'):
        print(json.dumps({
            'success': False,
            'error': '输入数据格式错误，缺少 success=true 字段'
        }, ensure_ascii=False), file=sys.stderr)
        return 1
    
    emails = data.get('emails', [])
    
    if args.debug:
        print(f"读取到 {len(emails)} 封邮件", file=sys.stderr)
    
    # 处理每封邮件
    highlight_keywords = [kw.strip().lower() for kw in args.highlight_keywords.split(',')]
    
    for email in emails:
        subject = email.get('subject', '')
        body = email.get('body_text', '') or email.get('body_html', '')
        
        # 检测优先级
        email['_priority'] = detect_priority(subject, body, highlight_keywords)
        
        # 检测标签
        email['_tags'] = detect_tags(subject, body)
    
    # 生成汇报
    if args.format == 'mobile':
        report = format_mobile_report(data, args)
    elif args.format == 'markdown':
        report = format_markdown_report(data, args)
    elif args.format == 'text':
        report = format_text_report(data, args)
    elif args.format == 'json':
        report = json.dumps({
            'success': True,
            'count': len(emails),
            'emails': emails,
            'generated_at': datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    else:
        report = format_mobile_report(data, args)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        if args.debug:
            print(f"汇报已保存到 {args.output}", file=sys.stderr)
    else:
        print(report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
