# Apple 快捷指令集成

与 Apple 生态系统集成，实现 iOS 和 macOS 自动化。

## 核心功能

### 运行快捷指令
```yaml
shortcut_execution:
  run:
    name: "早晨例行公事"
    input: 可选
    
  run_with_input:
    name: "处理文本"
    input: "{{text_to_process}}"
    
  run_with_clipboard:
    name: "分享到应用"
    input: 剪贴板
```

### Apple Reminders
```yaml
reminders:
  create:
    title: "{{task}}"
    list: "工作"
    due_date: "{{date}}"
    due_time: "09:00"
    priority: 高
    notes: "{{details}}"
    
  query:
    list: "购物"
    completed: false
    
  complete:
    reminder_id: "{{id}}"
```

### Apple Notes
```yaml
notes:
  create:
    title: "会议笔记 - {{date}}"
    folder: "工作"
    body: |
      # {{meeting_title}}
      
      ## 参会人员
      {{attendees}}
      
      ## 笔记
      {{notes}}
      
  append:
    note_title: "跑步日志"
    content: "- {{date}}: {{entry}}"
    
  search:
    query: "项目 alpha"
    folder: "项目"
```

### 日历
```yaml
calendar:
  create_event:
    title: "{{event_title}}"
    calendar: "工作"
    start: "{{start_time}}"
    end: "{{end_time}}"
    location: "{{location}}"
    notes: "{{notes}}"
    alerts:
      - 30  # 分钟前
      
  query:
    calendar: "全部"
    start: 今天
    end: "+7 天"
```

## 快捷指令示例

### 每日日志
```yaml
shortcut_daily_log:
  steps:
    - get_current_date
    - prompt_for_input:
        message: "你今天过得怎么样？"
    - append_to_note:
        title: "每日日记"
        content: |
          ## {{date}}
          {{input}}
    - create_reminder:
        title: "日记条目"
        due: 明天 9am
```

### 快速捕捉
```yaml
shortcut_quick_capture:
  trigger: share_sheet
  steps:
    - get_shared_input
    - create_note:
        title: "捕捉 - {{date}}"
        body: "{{input}}"
    - notify: "捕捉成功"
```

## 集成工作流

### 跨平台同步
```yaml
sync_workflow:
  trigger: note_created
  actions:
    - if: tag == "工作"
      then:
        - sync_to: notion
        - sync_to: obsidian
    - if: has_task
      then:
        - create_reminder: from_task
```

## 最佳实践

1. **命名**: 清晰、描述性的快捷指令名称
2. **输入处理**: 验证输入
3. **错误处理**: 优雅地处理失败
4. **隐私**: 最小化数据暴露
5. **测试**: 在所有设备上测试
