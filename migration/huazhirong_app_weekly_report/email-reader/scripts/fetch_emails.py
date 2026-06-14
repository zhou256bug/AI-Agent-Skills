#!/usr/bin/env python3
"""
Email Reader - 从 IMAP 服务器读取邮件

用法:
    python fetch_emails.py [选项]

示例:
    python fetch_emails.py --unread --since "1 hour ago" --limit 20
"""

import os
import sys
import json
import imaplib
import email
from email import policy
from email.header import decode_header
from datetime import datetime, timedelta
import argparse
import ssl


def parse_args():
    parser = argparse.ArgumentParser(description='从 IMAP 服务器读取邮件')
    
    # 连接参数
    parser.add_argument('--host', default=os.getenv('EMAIL_IMAP_HOST', 'imap.qiye.aliyun.com'),
                        help='IMAP 服务器地址')
    parser.add_argument('--port', type=int, default=int(os.getenv('EMAIL_IMAP_PORT', '993')),
                        help='IMAP 端口')
    parser.add_argument('--user', default=os.getenv('EMAIL_IMAP_USER'),
                        help='邮箱用户名')
    parser.add_argument('--password', default=os.getenv('EMAIL_IMAP_PASSWORD'),
                        help='邮箱密码')
    
    # 查询参数
    parser.add_argument('--folder', default='INBOX',
                        help='邮箱文件夹')
    parser.add_argument('--unread', action='store_true',
                        help='只读取未读邮件')
    parser.add_argument('--since', default=None,
                        help='读取此时间之后的邮件 (如 "1 hour ago", "2026-06-12")')
    parser.add_argument('--from', dest='from_addr', default=None,
                        help='只读取特定发件人的邮件')
    parser.add_argument('--subject', default=None,
                        help='只读取主题包含关键词的邮件')
    parser.add_argument('--limit', type=int, default=50,
                        help='最多读取的邮件数量')
    
    # 输出参数
    parser.add_argument('--output', default=None,
                        help='输出文件路径 (默认输出到 stdout)')
    parser.add_argument('--skip-attachments', action='store_true',
                        help='跳过附件内容')
    parser.add_argument('--pretty', action='store_true',
                        help='美化 JSON 输出')
    
    # 测试模式
    parser.add_argument('--test-connection', action='store_true',
                        help='只测试连接，不读取邮件')
    
    # 调试模式
    parser.add_argument('--debug', action='store_true',
                        help='启用调试模式')
    
    return parser.parse_args()


def decode_mime_words(text):
    """解码 MIME 编码的文本（支持中文等）"""
    if not text:
        return ""
    
    decoded = []
    for part, encoding in decode_header(text):
        if isinstance(part, bytes):
            try:
                if encoding:
                    decoded.append(part.decode(encoding, errors='replace'))
                else:
                    decoded.append(part.decode('utf-8', errors='replace'))
            except Exception:
                decoded.append(part.decode('utf-8', errors='replace'))
        else:
            decoded.append(part)
    
    return ''.join(decoded)


def get_email_body(msg):
    """提取邮件正文（优先纯文本，其次 HTML）"""
    body_text = ""
    body_html = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get_content_disposition())
            
            # 跳过附件
            if 'attachment' in content_disposition:
                continue
            
            if content_type == 'text/plain' and not body_text:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body_text = payload.decode(charset, errors='replace')
                except Exception as e:
                    body_text = f"[无法解析纯文本：{e}]"
            
            elif content_type == 'text/html' and not body_html:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body_html = payload.decode(charset, errors='replace')
                except Exception as e:
                    body_html = f"[无法解析 HTML: {e}]"
    else:
        # 非多部分邮件
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                content = payload.decode(charset, errors='replace')
                if msg.get_content_type() == 'text/html':
                    body_html = content
                else:
                    body_text = content
        except Exception as e:
            body_text = f"[无法解析邮件正文：{e}]"
    
    return body_text, body_html


def get_attachments(msg):
    """提取附件信息"""
    attachments = []
    
    for part in msg.walk():
        content_disposition = str(part.get_content_disposition())
        if 'attachment' in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_mime_words(filename)
                attachments.append({
                    'filename': filename,
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload(decode=True) or b'0')
                })
    
    return attachments


def parse_date(date_str):
    """解析 IMAP 日期字符串"""
    try:
        # IMAP 日期格式：'12-Jun-2026 10:30:00 +0800'
        return email.utils.parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now()


def fetch_emails(args):
    """主函数：获取邮件"""
    
    # 验证必要参数
    if not args.user:
        print(json.dumps({
            'success': False,
            'error': '缺少邮箱用户名，请设置 --user 或 EMAIL_IMAP_USER 环境变量'
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        return 1
    
    if not args.password:
        print(json.dumps({
            'success': False,
            'error': '缺少邮箱密码，请设置 --password 或 EMAIL_IMAP_PASSWORD 环境变量'
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        return 1
    
    if args.debug:
        print(f"连接到 {args.host}:{args.port} 用户：{args.user}", file=sys.stderr)
    
    try:
        # 创建 SSL 连接
        ssl_context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(args.host, args.port, ssl_context=ssl_context)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'连接失败：{e}'
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        return 1
    
    try:
        # 登录
        mail.login(args.user, args.password)
        
        if args.debug:
            print("登录成功", file=sys.stderr)
        
        # 测试连接模式
        if args.test_connection:
            print(json.dumps({
                'success': True,
                'message': 'IMAP 连接成功',
                'host': args.host,
                'port': args.port,
                'user': args.user,
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False, indent=2 if args.pretty else None))
            mail.logout()
            return 0
        
        # 选择文件夹
        mail.select(args.folder)
        
        if args.debug:
            print(f"已选择文件夹：{args.folder}", file=sys.stderr)
        
        # 构建搜索条件
        search_criteria = []
        
        if args.unread:
            search_criteria.append('UNSEEN')
        
        if args.since:
            # 解析时间
            try:
                if 'ago' in args.since:
                    # 相对时间： "1 hour ago", "2 days ago"
                    parts = args.since.split()
                    if len(parts) >= 3 and parts[-1] == 'ago':
                        value = int(parts[0])
                        unit = parts[1].lower()
                        
                        if 'hour' in unit:
                            since_date = datetime.now() - timedelta(hours=value)
                        elif 'day' in unit:
                            since_date = datetime.now() - timedelta(days=value)
                        elif 'week' in unit:
                            since_date = datetime.now() - timedelta(weeks=value)
                        elif 'min' in unit:
                            since_date = datetime.now() - timedelta(minutes=value)
                        else:
                            since_date = datetime.now() - timedelta(days=1)
                    else:
                        since_date = datetime.now() - timedelta(days=1)
                else:
                    # 绝对时间： "2026-06-12"
                    since_date = datetime.strptime(args.since, '%Y-%m-%d')
                
                # IMAP 日期格式：12-Jun-2026
                imap_date = since_date.strftime('%d-%b-%Y').upper()
                search_criteria.append(f'(SINCE "{imap_date}")')
                
            except Exception as e:
                if args.debug:
                    print(f"解析 --since 参数失败：{e}", file=sys.stderr)
        
        if args.from_addr:
            search_criteria.append(f'(FROM "{args.from_addr}")')
        
        # 合并搜索条件
        if search_criteria:
            search_query = ' '.join(search_criteria)
        else:
            search_query = 'ALL'
        
        if args.debug:
            print(f"搜索条件：{search_query}", file=sys.stderr)
        
        # 搜索邮件
        status, messages = mail.search(None, search_query)
        
        if status != 'OK':
            print(json.dumps({
                'success': False,
                'error': f'搜索失败：{status}'
            }, ensure_ascii=False, indent=2 if args.pretty else None))
            return 1
        
        # 获取邮件 ID 列表
        email_ids = messages[0].split()
        
        if not email_ids:
            print(json.dumps({
                'success': True,
                'count': 0,
                'emails': [],
                'message': '没有符合条件的邮件'
            }, ensure_ascii=False, indent=2 if args.pretty else None))
            mail.logout()
            return 0
        
        # 限制数量
        if len(email_ids) > args.limit:
            email_ids = email_ids[-args.limit:]  # 取最新的 N 封
        
        if args.debug:
            print(f"找到 {len(email_ids)} 封邮件", file=sys.stderr)
        
        # 获取每封邮件
        emails = []
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    if args.debug:
                        print(f"获取邮件 {email_id} 失败：{status}", file=sys.stderr)
                    continue
                
                # 解析邮件
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email, policy=policy.default)
                
                # 提取信息
                email_data = {
                    'id': email_id.decode() if isinstance(email_id, bytes) else str(email_id),
                    'from': decode_mime_words(msg.get('From', '')),
                    'from_name': decode_mime_words(msg.get('From', '').split('<')[0].strip()) if '<' in msg.get('From', '') else decode_mime_words(msg.get('From', '')),
                    'to': decode_mime_words(msg.get('To', '')),
                    'subject': decode_mime_words(msg.get('Subject', '(无主题)')),
                    'date': parse_date(msg.get('Date', '')).isoformat(),
                    'folder': args.folder,
                }
                
                # 获取正文
                body_text, body_html = get_email_body(msg)
                email_data['body_text'] = body_text[:5000] if body_text else ""  # 限制长度
                email_data['body_html'] = body_html[:5000] if body_html else ""
                
                # 获取附件
                if not args.skip_attachments:
                    email_data['attachments'] = get_attachments(msg)
                else:
                    email_data['attachments'] = []
                
                # 获取标志
                status, flags = mail.fetch(email_id, '(FLAGS)')
                if status == 'OK':
                    flags_str = flags[0].decode()
                    email_data['flags'] = []
                    if '\\Seen' in flags_str:
                        email_data['flags'].append('\\Seen')
                    if '\\Answered' in flags_str:
                        email_data['flags'].append('\\Answered')
                    if '\\Flagged' in flags_str:
                        email_data['flags'].append('\\Flagged')
                
                emails.append(email_data)
                
            except Exception as e:
                if args.debug:
                    print(f"处理邮件 {email_id} 出错：{e}", file=sys.stderr)
                continue
        
        # 输出结果
        result = {
            'success': True,
            'count': len(emails),
            'limit': args.limit,
            'folder': args.folder,
            'emails': emails
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2 if args.pretty else None)
            print(f"已保存 {len(emails)} 封邮件到 {args.output}", file=sys.stderr)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        
        # 登出
        mail.logout()
        return 0
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'处理失败：{e}'
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        try:
            mail.logout()
        except Exception:
            pass
        return 1


if __name__ == '__main__':
    args = parse_args()
    sys.exit(fetch_emails(args))
