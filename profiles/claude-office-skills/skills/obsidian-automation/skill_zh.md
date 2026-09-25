# Obsidian 自动化

自动化 Obsidian 知识管理和个人知识库工作流程。

## 核心功能

### 笔记创建
```yaml
note_templates:
  daily_note:
    filename: "{{date:YYYY-MM-DD}}"
    folder: "每日笔记"
    template: |
      # {{date:dddd, MMMM D, YYYY}}
      
      ## 早晨目标
      - [ ] 
      
      ## 任务
      - [ ] 
      
      ## 笔记
      
      ## 傍晚反思
      
      ---
      [[{{date:YYYY-MM-DD|-1d}}|← 昨天]] | [[{{date:YYYY-MM-DD|+1d}}|明天 →]]

  meeting_note:
    filename: "会议 - {{title}} - {{date}}"
    folder: "会议"
    template: |
      ---
      date: {{date}}
      attendees: {{attendees}}
      tags: meeting
      ---
      
      # {{title}}
      
      ## 议程
      
      ## 笔记
      
      ## 行动项
      - [ ] 
      
      ## 跟进
      
      [[会议 MOC]]
```

### 智能链接
```yaml
auto_linking:
  rules:
    - pattern: "[[人物/{{name}}]]"
      trigger: "@{{name}}"
      create_if_missing: true
      
    - pattern: "[[项目/{{project}}]]"
      trigger: "#proj/{{project}}"
      
  backlink_suggestions:
    enabled: true
    min_mentions: 2
    
  alias_support:
    - "[[机器学习|ML]]"
    - "[[人工智能|AI]]"
```

### Dataview 查询
```yaml
dataview_examples:
  tasks_due_today:
    query: |
      ```dataview
      TASK
      WHERE !completed AND due = date(today)
      SORT due ASC
      ```
      
  recent_meetings:
    query: |
      ```dataview
      TABLE date, attendees
      FROM "会议"
      WHERE date >= date(today) - dur(7 days)
      SORT date DESC
      LIMIT 10
      ```
      
  project_dashboard:
    query: |
      ```dataview
      TABLE status, due, priority
      FROM #project
      WHERE status != "completed"
      SORT priority ASC
      ```
```

### 模板
```yaml
templates:
  zettelkasten:
    filename: "{{date:YYYYMMDDHHmmss}}"
    content: |
      ---
      id: {{date:YYYYMMDDHHmmss}}
      tags: 
      links: 
      ---
      
      # {{title}}
      
      ## 思想
      
      ## 来源
      
      ## 连接
      - 相关于: 
      
      ## 参考文献
      
  book_note:
    filename: "书籍 - {{title}}"
    content: |
      ---
      author: {{author}}
      finished: 
      rating: 
      tags: book
      ---
      
      # {{title}}
      by {{author}}
      
      ## 摘要
      
      ## 核心观点
      
      ## 精华
      
      ## 我的思考
      
      ## 行动项
```

## 工作流程自动化

### Web Clipper
```yaml
web_clipper:
  trigger: browser_extension
  actions:
    - extract_content:
        title: "{{page.title}}"
        url: "{{page.url}}"
        content: "{{selection}}"
    - create_note:
        folder: "剪藏"
        template: web_clip
    - add_tags: ["web-clip", "{{domain}}"]
```

### 研究工作流
```yaml
research_workflow:
  steps:
    - create_topic_note:
        filename: "研究 - {{topic}}"
        folder: "研究"
    - gather_sources:
        search: "{{topic}}"
        link_to_note: true
    - generate_questions:
        based_on: sources
    - create_sub_notes:
        for_each: key_concept
```

## 图形分析

```yaml
graph_insights:
  orphan_notes:
    query: "没有入链的笔记"
    action: suggest_connections
    
  clusters:
    identify: true
    visualize: true
    
  link_suggestions:
    based_on: content_similarity
    threshold: 0.7
```

## 最佳实践

1. **原子笔记**：每条笔记一个想法
2. **命名规范**：使用约定
3. **自由链接**：连接相关想法
4. **每日实践**：定期回顾
5. **模板**：标准化笔记类型
6. **标签与链接**：策略性使用
