#!/usr/bin/env bash
# 邮件定时汇报 - 编排脚本
# 用法：./email-report.sh

set -e

# 从环境变量读取配置（优先）或默认值
EMAIL_USER="${EMAIL_IMAP_USER:-qiang.zhou@newpostech.com}"
EMAIL_PASS="${EMAIL_IMAP_PASSWORD}"
SINCE="${EMAIL_REPORT_SINCE:-24 hours ago}"
LIMIT="${EMAIL_REPORT_LIMIT:-100}"

# 验证必要配置
if [ -z "$EMAIL_PASS" ]; then
  echo "错误：EMAIL_IMAP_PASSWORD 环境变量未设置" >&2
  exit 1
fi

# 临时文件
TEMP_EMAILS="/tmp/emails_$(date +%s).json"
TEMP_REPORT="/tmp/report_$(date +%s).md"

# 清理临时文件
trap "rm -f $TEMP_EMAILS $TEMP_REPORT" EXIT

# 读取邮件
echo "正在读取过去 1 小时的未读邮件..." >&2
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/custom/email-reader/scripts/fetch_emails.py \
  --user "$EMAIL_USER" \
  --password "$EMAIL_PASS" \
  --unread \
  --since "$SINCE" \
  --limit $LIMIT \
  --output "$TEMP_EMAILS"

# 检查是否有邮件
EMAIL_COUNT=$(cat "$TEMP_EMAILS" | ~/.hermes/hermes-agent/venv/bin/python -c "import sys,json; print(json.load(sys.stdin).get('count',0))")

if [ "$EMAIL_COUNT" -eq 0 ]; then
  echo "[SILENT]" 
  exit 0
fi

# 生成汇报（移动端优化格式）
echo "正在生成汇报..." >&2
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/custom/email-summarizer/scripts/summarize.py \
  --input "$TEMP_EMAILS" \
  --output "$TEMP_REPORT" \
  --format mobile \
  --compact \
  --silent-if-empty

# 输出汇报
cat "$TEMP_REPORT"

echo "汇报生成完成，共 $EMAIL_COUNT 封邮件" >&2
