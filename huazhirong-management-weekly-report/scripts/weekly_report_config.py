#!/usr/bin/env python3
"""管理团队周报技能的可配置项（平台无关，全部支持环境变量覆盖）。

设计目标：clone 后开箱即用——所有"特定公司/特定人/特定路径"的值都在这里集中、
可被环境变量覆盖，默认值为华智融实例的真实值（便于原环境直接跑，也便于他人替换）。

| 配置 | 环境变量 | 默认值 | 含义 |
|------|----------|--------|------|
| OWNER         | WEEKLY_REPORT_OWNER         | 老板                       | 最终 PDF 的收件人（CEO/老板），用于段标题「需{OWNER}关注的事项」与禁止段判定 |
| SENDER_NAME   | WEEKLY_REPORT_SENDER_NAME   | 陈徐伟                     | 源周报邮件的发件人姓名（meta「来源」） |
| SENDER_EMAIL  | WEEKLY_REPORT_SENDER_EMAIL  | evyn.chen@newpostech.com   | 需查询的源周报邮件发件人邮箱 |
| SUBJECT_KEY   | WEEKLY_REPORT_SUBJECT_KEY   | 总裁办及各部门经理周报      | 源邮件主题关键词（用于 IMAP 过滤与期号解析） |
| COMPANY       | WEEKLY_REPORT_COMPANY       | 华智融                     | 公司名 |
| ARCHIVE_DIR   | WEEKLY_REPORT_ARCHIVE_DIR   | <skill>/output            | MD/PDF 归档根目录 |
"""

from __future__ import annotations

import os
from pathlib import Path

# skill 根目录 = 本文件父目录（scripts/）的上一级
SKILL_ROOT = Path(__file__).resolve().parent.parent

OWNER: str = os.environ.get("WEEKLY_REPORT_OWNER", "老板")
SENDER_NAME: str = os.environ.get("WEEKLY_REPORT_SENDER_NAME", "陈徐伟")
SENDER_EMAIL: str = os.environ.get("WEEKLY_REPORT_SENDER_EMAIL", "evyn.chen@newpostech.com")
SUBJECT_KEY: str = os.environ.get("WEEKLY_REPORT_SUBJECT_KEY", "总裁办及各部门经理周报")
COMPANY: str = os.environ.get("WEEKLY_REPORT_COMPANY", "华智融")


def archive_dir() -> Path:
    """归档根目录：环境变量优先，否则技能本地 output/（已 gitignore）。"""
    env = os.environ.get("WEEKLY_REPORT_ARCHIVE_DIR")
    return Path(env).expanduser() if env else (SKILL_ROOT / "output")


if __name__ == "__main__":
    # 便于排查：打印当前生效配置
    print(f"OWNER        = {OWNER}")
    print(f"SENDER_NAME  = {SENDER_NAME}")
    print(f"SENDER_EMAIL = {SENDER_EMAIL}")
    print(f"SUBJECT_KEY  = {SUBJECT_KEY}")
    print(f"COMPANY      = {COMPANY}")
    print(f"ARCHIVE_DIR  = {archive_dir()}")
