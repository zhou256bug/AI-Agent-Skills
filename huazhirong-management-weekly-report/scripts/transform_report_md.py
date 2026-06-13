#!/usr/bin/env python3
"""Transform legacy 5-section report → 4-section + project sources (keep emoji status)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 确保同目录的 weekly_report_config 可被导入
sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekly_report_config as cfg  # noqa: E402

# Project block → primary weekly-report owner(s)
# 注：这是公司专属的"项目→周报负责人"映射（华智融默认数据），可按需替换。
PROJECT_SOURCES: dict[str, str] = {
    "NEW9830": "肖锦填、卢艳娟",
    "NEW9810P": "肖锦填、卢艳娟",
    "MDP910": "卢艳娟、肖锦填",
    "NEW9810": "肖锦填、卢艳娟",
    "MDP850": "卢艳娟、黄丽红",
    "MDP610": "卢艳娟、黄丽红",
    "NEW9850": "肖锦填、陈明华",
    "NEW9228": "黄丽红、李鹤祥",
    "空中云汇": "贺飞平",
    "NewStore": "王青虹",
}


def transform(text: str, *, period: int, summary_date: str) -> str:
    text = re.sub(
        r"汇报周期：[^\n]+",
        f"第{period}期 | 汇总日期：{summary_date} | 来源：{cfg.SENDER_NAME}",
        text,
        count=1,
    )
    # Drop 第一节「…本周重点」（兼容 OWNER 或历史 菜头 命名）直到「二、重点项目进展」前
    text = re.sub(
        r"## 一、.*?本周重点\n\n.*?(?=## 二、重点项目进展)",
        "",
        text,
        flags=re.DOTALL,
    )
    # Renumber sections（owner 名兼容：四/五节标题里的 owner 用通配匹配）
    text = text.replace("## 二、重点项目进展", "## 一、重点项目进展")
    text = text.replace("## 三、海外市场要闻", "## 二、海外市场要闻")
    text = re.sub(r"## 四、.*?业务线重点关注", "## 三、业务线重点关注", text)
    text = re.sub(r"## 五、需.*?关注的事项", f"## 四、需{cfg.OWNER}关注的事项", text)

    lines: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^### (.+)$", line.strip())
        if m:
            title = m.group(1).strip()
            for key, owners in PROJECT_SOURCES.items():
                if key.lower() in title.lower() or key in title:
                    lines.append(line)
                    parts = owners.replace("、", "**、**")
                    lines.append(f"> 周报来源：**{parts}**")
                    break
            else:
                lines.append(line)
        else:
            lines.append(line)

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: transform_report_md.py input.md output.md PERIOD YYYY-MM-DD", file=sys.stderr)
        return 2
    src, dst, period_s, date_s = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    out = transform(
        Path(src).read_text(encoding="utf-8"),
        period=int(period_s),
        summary_date=date_s,
    )
    Path(dst).write_text(out, encoding="utf-8")
    print(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
