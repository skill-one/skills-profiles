# 日历自动化

自动化 Google 日历和 Outlook 工作流程，用于会议管理、时间块、每日摘要和跨平台同步。基于 n8n 工作流模板。

## 概述

本技能涵盖：
- 会议安排自动化
- 时间块策略
- 每日日历摘要发送至 Slack
- 会议准备提醒
- 日历分析

---

## 核心工作流

### 1. 每日日历摘要发送至 Slack

```yaml
workflow: "晨间日历简报"

schedule: "每天早上 6:00"

steps:
  1. get_today_events:
      calendar: primary
      time_min: today_start
      time_max: today_end
      
  2. categorize_events:
      categories:
        meetings: has_attendees == true
        focus_time: title contains "Focus" OR "Deep Work"
        one_on_ones: title contains "1:1" OR "1-on-1"
        interviews: title contains "Interview"
        
  3. calculate_stats:
      total_meetings: count(meetings)
      total_hours: sum(duration)
      free_time: 8 - total_hours
      back_to_back: count(gap < 15min)
      
  4. format_message:
      template: |
        ☀️ *早上好！这是你的日程：*
        
        📅 *{date}*
        
        *日程概览：*
        • {total_meetings} 场会议 ({total_hours}h)
        • {free_time}h 的空闲时间
        • {back_to_back} 个连续时段 ⚠️
        
        *今日活动：*
        {event_list}
        
        💡 *提示：* {daily_tip}
        
  5. send_to_slack:
      channel: "#daily-schedule" 或 DM
      
  6. log_to_sheets:
      spreadsheet: "日历分析"
      data: [date, meetings, hours, categories]
```

**活动列表格式**：
```
• 9:00 AM - 团队晨会 (15m) 📞 Zoom
• 10:00 AM - 与 Sarah 的 1:1 (30m) 👥
• 11:00 AM - 专注时间 (2h) 🧠
• 2:00 PM - 客户电话 (1h) 🤝 Google Meet
• 4:00 PM - 面试 - 产品经理职位 (45m) 🎯
```

---

### 2. 会议准备自动化

```yaml
workflow: "会议准备"

trigger:
  type: calendar_event
  time: 会议前 1 小时
  filter: has_attendees AND duration >= 30min

steps:
  1. get_meeting_details:
      extract: [title, attendees, description, meeting_link]
      
  2. research_attendees:
      for_each: attendee
      actions:
        - linkedin_lookup: get_title_company
        - crm_lookup: get_past_interactions
        - email_search: recent_threads
        
  3. generate_prep_doc:
      template: |
        # 会议准备：{title}
        
        **时间：** {start_time}
        **时长：** {duration}
        **链接：** {meeting_link}
        
        ## 参会者
        {attendee_profiles}
        
        ## 背景
        - 最后互动：{last_meeting_date}
        - 待办事项：{open_tasks}
        - 近期邮件：{email_summary}
        
        ## 建议议程
        {ai_suggested_agenda}
        
        ## 演讲要点
        {ai_talking_points}
        
  4. send_reminder:
      slack_dm:
        message: |
          ⏰ 1 小时后开会：*{title}*
          
          📋 [准备文档]({prep_doc_link})
          🔗 [加入会议]({meeting_link})
          
          快速背景：{one_line_summary}
```

---

### 3. 智能时间块

```yaml
workflow: "自动时间块"

schedule: "周日晚上 8:00" # 规划下周

steps:
  1. analyze_calendar:
      range: next_7_days
      identify:
        - 现有会议
        - 周期性会议
        - 可用时段
        
  2. get_priorities:
      source: [todoist, asana, notion]
      filter: due_this_week AND high_priority
      
  3. allocate_focus_time:
      rules:
        - morning_block: 9-11am (深度工作)
        - afternoon_block: 2-4pm (协作)
        - 最小间隔：会议间 15min
        - 每天最多会议数：5
        
  4. create_blocks:
      types:
        deep_work:
          duration: 2h
          frequency: 每日
          preferred_time: 9-11am
          color: blue
          
        admin_time:
          duration: 1h
          frequency: 每日
          preferred_time: 4-5pm
          color: gray
          
        buffer:
          duration: 15min
          after: 外部会议
          color: yellow
          
  5. notify:
      slack: "✅ 每周时间块已创建。保护了 {x} 小时的专注时间。"
```

---

### 4. Calendly → 日历 + CRM

```yaml
workflow: "Calendly 预约处理"

trigger:
  type: calendly
  event: booking_created

steps:
  1. get_booking_details:
      extract: [invitee, event_type, scheduled_time, answers]
      
  2. enrich_contact:
      clearbit: lookup_by_email
      linkedin: get_profile
      
  3. create_calendar_event:
      google_calendar:
        title: "{event_type} with {invitee_name}"
        time: scheduled_time
        description: |
          **通过 Calendly 预约**
          
          姓名：{invitee_name}
          邮箱：{invitee_email}
          公司：{company}
          
          **会前问题：**
          {calendly_answers}
        attendees: [invitee_email, owner_email]
        reminders: [1_day, 1_hour, 15_min]
        
  4. update_crm:
      hubspot:
        create_or_update_contact:
          email: invitee_email
          properties:
            last_meeting_booked: scheduled_time
            meeting_type: event_type
        create_engagement:
          type: MEETING
          timestamp: scheduled_time
          
  5. send_confirmation:
      email:
        to: invitee_email
        template: meeting_confirmation
        include: [calendar_invite, prep_questions]
        
  6. notify_slack:
      channel: "#meetings"
      message: "📅 新预约：{event_type} with {invitee_name} on {date}"
```

---

### 5. 日历分析

```yaml
analytics_workflow:
  name: "每周日历报告"
  schedule: "周五下午 5:00"
  
  metrics:
    time_distribution:
      - meetings_total_hours
      - focus_time_hours
      - admin_time_hours
      - 1on1_time_hours
      
    meeting_quality:
      - avg_meeting_length
      - back_to_back_count
      - meetings_with_agenda
      - external_vs_internal
      
    productivity:
      - longest_focus_block
      - fragmentation_score
      - after_hours_meetings
      
  output:
    format: markdown
    destinations: [slack, google_sheets]
    
  report_template: |
    # 📊 每周日历分析
    
    ## 时间分配
    | 类别 | 小时 | 周百分比 |
    |----------|-------|-----------|
    | 会议 | {meetings_hours} | {meetings_pct}% |
    | 专注时间 | {focus_hours} | {focus_pct}% |
    | 管理 | {admin_hours} | {admin_pct}% |
    | 可用 | {available_hours} | {available_pct}% |
    
    ## 会议洞察
    - 总会议数：{total_meetings}
    - 平均时长：{avg_length} 分钟
    - 连续会议：{b2b_count} ({b2b_pct}%)
    - 有议程：{agenda_pct}%
    
    ## 生产力评分
    🎯 **{productivity_score}/100**
    
    - 最长专注块：{longest_focus}
    - 会议碎片化：{fragmentation}
    - 晚上会议：{after_hours_count}
    
    ## 建议
    {ai_recommendations}
```

---

## 时间块模板

### 个人贡献者时间表
```
┌─────────────────────────────────────┐
│ 9:00 - 11:00  │ 深度工作块 1  │
├─────────────────────────────────────┤
│ 11:00 - 11:30 │ 邮件/Slack        │
├─────────────────────────────────────┤
│ 11:30 - 12:30 │ 会议窗口    │
├─────────────────────────────────────┤
│ 12:30 - 1:30  │ 午餐              │
├─────────────────────────────────────┤
│ 1:30 - 3:30   │ 深度工作块 2  │
├─────────────────────────────────────┤
│ 3:30 - 4:00   │ 缓冲/管理       │
├─────────────────────────────────────┤
│ 4:00 - 5:00   │ 会议窗口    │
├─────────────────────────────────────┤
│ 5:00 - 5:30   │ 每日总结      │
└─────────────────────────────────────┘
```

### 经理时间表
```
┌─────────────────────────────────────┐
│ 8:00 - 8:30   │ 每日计划     │
├─────────────────────────────────────┤
│ 8:30 - 9:00   │ 团队晨会       │
├─────────────────────────────────────┤
│ 9:00 - 12:00  │ 1:1s / 会议    │
├─────────────────────────────────────┤
│ 12:00 - 1:00  │ 午餐              │
├─────────────────────────────────────┤
│ 1:00 - 2:00   │ 专注时间         │
├─────────────────────────────────────┤
│ 2:00 - 5:00   │ 会议           │
├─────────────────────────────────────┤
│ 5:00 - 5:30   │ 邮件/总结      │
└─────────────────────────────────────┘
```

---

## 输出示例

**请求**： "为我的 Slack 设置每日日历摘要"

**输出**：

```markdown
# 每日日历摘要设置

## 工作流配置

```yaml
name: "Morning Calendar Briefing"
schedule: "每天早上 6:00 工作日"
timezone: "Asia/Shanghai"

trigger:
  type: cron
  expression: "0 6 * * 1-5"

actions:
  1. fetch_events:
      calendar: primary
      date: today
      
  2. send_slack:
      channel: "@you" # 或 #your-channel
```

## 示例输出

```
☀️ 早上好！这是你的周四：

📅 2026年1月30日

━━━━━━━━━━━━━━━━━━━━━━

📊 概览：
• 5 场会议 (4.5h)
• 3.5h 空闲时间
• 1 个连续时段警告 ⚠️

━━━━━━━━━━━━━━━━━━━━━━

🗓️ 日程：

9:00 AM │ 团队晨会 (15m)
        │ 📞 Google Meet
        │
10:00 AM │ 与 Sarah 的 1:1 (30m)
         │ 👥 会议室 B
         │
11:00 AM │ 🧠 专注时间 (2h)
         │ 
1:00 PM │ 午餐
        │
2:00 PM │ 客户电话 - Acme (1h)
        │ 🤝 Zoom (链接已附)
        │
3:30 PM │ 产品评审 (1h)
        │ 📋 议程已附
        │
5:00 PM │ ✅ 结束日

━━━━━━━━━━━━━━━━━━━━━━

💡 提示：你有 2h 的专注时间 - 处理你的最高优先级任务！
```

## n8n 设置说明

1. 创建新工作流
2. 添加计划触发器节点 (工作日早上 6 点)
3. 添加 Google 日历节点 (获取活动)
4. 添加代码节点 (格式化消息)
5. 添加 Slack 节点 (发送消息)
6. 激活工作流

您需要我生成完整的 n8n 工作流 JSON 吗？
```

---

*日历自动化技能 - Claude 办公技能的一部分*
