#!/usr/bin/env python3
"""
周报消息格式化 - 针对微信/企业微信优化

关键优化：
1. 每行不超过 30 个字符（避免换行）
2. 使用简单分隔符（避免断裂）
3. 列表项单独成行
4. 减少 emoji 使用（某些平台显示异常）
"""

def format_for_mobile(week_num, department, period, employees, focus_config=None):
    """格式化周报为移动端友好的消息"""
    
    lines = []
    
    # 标题（每行≤25 字符）
    lines.append(f"📋 工作周报·第{week_num}期")
    lines.append(f"🏢 {department}")
    lines.append(f"📅 {period}")
    lines.append("-" * 20)
    lines.append("")
    
    # 您的关注
    lines.append("⭐ 您的关注")
    lines.append("-" * 20)
    
    if not focus_config or (not focus_config.get('people') and not focus_config.get('projects')):
        lines.append("")
        lines.append("💡 暂无关注配置")
        lines.append("")
        lines.append("📝 添加关注方法：")
        lines.append("告诉强仔：")
        lines.append("  • 关注某人：关注周强")
        lines.append("  • 关注项目：关注 NEWSTORE")
    else:
        lines.append("")
        for person in focus_config.get('people', []):
            lines.append(f"👤 {person}")
        for project in focus_config.get('projects', []):
            lines.append(f"📁 {project}")
    
    lines.append("")
    lines.append("-" * 20)
    lines.append("")
    
    # 本周概览
    lines.append("📊 本周概览")
    lines.append("-" * 20)
    lines.append(f"• 总人数：{len(employees)} 人")
    lines.append(f"• 周期：{period}")
    lines.append("")
    lines.append("-" * 20)
    lines.append("")
    
    # 重点成果（每项单独成行）
    lines.append("🔴 重点成果 Top5")
    lines.append("-" * 20)
    lines.append("")
    
    for i, emp in enumerate(employees[:5], 1):
        # 姓名（≤10 字符）
        name = emp['name'][:10]
        # 成果（≤25 字符，换行显示）
        work = emp['work'].split('\n')[0][:25]
        
        lines.append(f"{i}. {name}")
        lines.append(f"   {work}")
        lines.append("")
    
    lines.append("-" * 20)
    lines.append("")
    lines.append("📄 PDF 报告稍后发送")
    lines.append("✅ 周报整理完成")
    
    return '\n'.join(lines)


# 示例数据
if __name__ == '__main__':
    employees = [
        {'name': '林旭伟', 'work': 'Airwallex 项目 UI 适配完成'},
        {'name': '丁璞', 'work': 'Winfopay 9220U 识别解决'},
        {'name': '胡陈琛', 'work': '欧洲装机程序开发'},
        {'name': '李家俊', 'work': 'OMA 5320 固件交付'},
        {'name': '李响', 'work': '土耳其税控模块跟进'},
    ]
    
    report = format_for_mobile(
        week_num='23',
        department='海外应用开发部',
        period='2026.06.01-06.07',
        employees=employees
    )
    
    print(report)
