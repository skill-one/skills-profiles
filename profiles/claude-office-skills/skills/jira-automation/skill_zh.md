# Jira 自动化

全面的技能，用于自动化 Jira 项目管理和敏捷工作流。

## 核心工作流

### 1. 问题管理流程

```
问题生命周期:
┌─────────────────┐
│    待办列表      │
└────────┬────────┘
         ▼
┌─────────────────┐
│   待办        │──────┐
└────────┬────────┘      │ 阻塞
         ▼               │
┌─────────────────┐      │
│   进行中       │◄─────┘
└────────┬────────┘
         ▼
┌─────────────────┐
│   审核中       │
└────────┬────────┘
         ▼
┌─────────────────┐
│     已完成      │
└─────────────────┘
```

### 2. 自动化规则

```yaml
automation_rules:
  - name: 自动分配到进行中
    trigger:
      type: issue_transitioned
      to_status: "进行中"
    condition:
      assignee: unassigned
    action:
      assign_to: trigger_user

  - name: 根据优先级添加标签
    trigger:
      type: issue_created
      priority: highest
    action:
      - add_label: "紧急"
      - send_slack: "#dev-alerts"

  - name: 自动关闭子任务
    trigger:
      type: issue_transitioned
      to_status: "已完成"
      issue_type: Story
    action:
      transition_subtasks: "已完成"

  - name: SLA 警告
    trigger:
      type: scheduled
      cron: "0 9 * * 1-5"
    condition:
      jql: "status = '进行中' AND updated < -3d"
    action:
      - add_comment: "@assignee 请更新此问题"
      - send_notification: assignee
```

## Sprint 管理

### Sprint 规划模板

```yaml
sprint_planning:
  name: "Sprint {{sprint_number}}"
  duration: 14  # 天
  
  capacity_planning:
    team_size: 6
    hours_per_day: 6
    total_capacity: 504  # 小时
    
  story_points:
    target: 42
    buffer: 10%  # 用于计划外工作
    
  ceremonies:
    - name: Sprint 规划
      day: 1
      duration: 2h
    - name: 每日站会
      day: "daily"
      duration: 15m
    - name: Sprint 评审
      day: 14
      duration: 1h
    - name: 回顾
      day: 14
      duration: 1h
```

### Sprint 看板配置

```yaml
board_config:
  type: scrum
  columns:
    - name: 待办列表
      statuses: ["待办列表"]
    - name: 待办
      statuses: ["待办", "已选择开发"]
      wip_limit: null
    - name: 进行中
      statuses: ["进行中"]
      wip_limit: 6
    - name: 审核中
      statuses: ["代码评审", "测试"]
      wip_limit: 4
    - name: 已完成
      statuses: ["已完成"]
      
  swimlanes:
    type: assignee
    show_epics: true
```

## 问题模板

### Bug 报告

```yaml
bug_template:
  project: DEV
  issue_type: Bug
  fields:
    summary: "[BUG] {{title}}"
    description: |
      ## 描述
      {{description}}
      
      ## 复现步骤
      1. {{step1}}
      2. {{step2}}
      3. {{step3}}
      
      ## 预期行为
      {{expected}}
      
      ## 实际行为
      {{actual}}
      
      ## 环境
      - 浏览器: {{browser}}
      - 操作系统: {{os}}
      - 版本: {{app_version}}
      
      ## 截图
      {{attachments}}
    
    priority: {{severity}}
    labels: ["bug", "需要评审"]
    components: ["{{component}}"]
```

### 功能请求

```yaml
feature_template:
  project: DEV
  issue_type: Story
  fields:
    summary: "[功能] {{title}}"
    description: |
      ## 用户故事
      作为 {{user_type}}，我想要 {{action}}，以便 {{benefit}}。
      
      ## 接受标准
      - [ ] {{criteria1}}
      - [ ] {{criteria2}}
      - [ ] {{criteria3}}
      
      ## 技术说明
      {{tech_notes}}
      
      ## 设计原型
      {{mockups}}
    
    labels: ["功能", "需要完善"]
    story_points: null  # 待估算
```

### Epic 结构

```yaml
epic_template:
  project: DEV
  issue_type: Epic
  fields:
    summary: "{{epic_name}}"
    description: |
      ## 概述
      {{overview}}
      
      ## 目标
      - {{goal1}}
      - {{goal2}}
      
      ## 成功指标
      | 指标 | 当前值 | 目标值 |
      |------|--------|--------|
      | {{metric1}} | {{current1}} | {{target1}} |
      
      ## 时间表
      开始: {{start_date}}
      目标完成: {{end_date}}
      
      ## 依赖关系
      {{dependencies}}
      
    child_issues:
      - type: Story
        count: "auto"
```

## JQL 查询库

### 常用查询

```jql
# 我的未解决问题
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC

# Sprint 进度
project = DEV AND Sprint = "Sprint 15" ORDER BY status

# 按严重程度分类的 Bug
project = DEV AND type = Bug AND resolution = Unresolved 
ORDER BY priority DESC, created ASC

# 过期问题
project = DEV AND status = "进行中" AND updated < -7d

# 准备评审
project = DEV AND status = "代码评审" AND "代码评审者" is EMPTY

# 发布范围
fixVersion = "v2.5.0" AND resolution = Unresolved

# 团队速度
project = DEV AND type = Story AND Sprint in closedSprints() 
AND resolved >= -90d

# 阻塞问题
project = DEV AND (priority = Blocker OR labels = blocked)
AND resolution = Unresolved
```

## 报告与看板

### Sprint 看板

```
Sprint 15 看板
═══════════════════════════════════════

进度:
Day 8 of 14 │ ████████░░░░░░ 57%

故事点:
承诺: 42
已完成: 24  │ ████████████░░░░░░░░ 57%
剩余: 18

燃尽图:
│ 42 ┤ ▪
│    │  ▪▪
│    │    ▪▪
│    │      ▪▪▪
│ 21 ┤         ▪ ← 理想
│    │          ▪▪
│    │            ▪▪
│    │              ▪▪
│  0 ┤                ▪
└────┴────────────────────
     Day 1           Day 14

问题状态:
待办        ███░░░░░░░ 6
进行中      █████░░░░░ 8
审核中      ████░░░░░░ 5
已完成      █████████░ 12
```

### 速度图

```
团队速度（最近 6 个 Sprint）
═══════════════════════════════════════

│  50 ┤
│     │           ▓▓
│  40 ┤    ▓▓     ▓▓     ▓▓     ▓▓
│     │    ▓▓ ▓▓  ▓▓     ▓▓ ▓▓  ▓▓
│  30 ┤ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│     │ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│  20 ┤ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│     │ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│  10 ┤ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│     │ ▓▓ ▓▓ ▓▓  ▓▓ ▓▓  ▓▓ ▓▓  ▓▓
│   0 ┴─────────────────────────────
       S10 S11 S12 S13 S14 S15

平均: 38 点 | 趋势: +5%
```

## 集成工作流

### GitHub 集成

```yaml
github_integration:
  branch_creation:
    trigger: issue_transitioned_to_in_progress
    pattern: "{{issue_type}}/{{issue_key}}-{{summary_slug}}"
    
  commit_linking:
    patterns:
      - "{{issue_key}}"
      - "#{{issue_key}}"
    action: add_comment_with_link
    
  pr_自动化:
    on_pr_open:
      - transition_issue: "代码评审"
      - add_pr_link_to_issue
    on_pr_merge:
      - transition_issue: "已完成"
      - add_comment: "已合并到 {{pr_url}}"
```

### Slack 集成

```yaml
slack_integration:
  channels:
    dev_updates: "#dev-updates"
    alerts: "#dev-alerts"
    
  notifications:
    - event: blocker_created
      channel: alerts
      message: "🚨 阻塞: {{issue.key}} - {{issue.summary}}"
      
    - event: sprint_started
      channel: dev_updates
      message: "🏃 Sprint {{sprint.name}} 已开始！目标: {{sprint.goal}}"
      
    - event: release_completed
      channel: dev_updates
      message: "🚀 版本 {{version}} 已上线！"
```

## 工作流自定义

### 自定义工作流

```yaml
workflow:
  name: 开发工作流
  statuses:
    - 待办列表
    - 准备开发
    - 进行中
    - 代码评审
    - 测试
    - 准备发布
    - 已完成
    
  transitions:
    - from: 待办列表
      to: 准备开发
      name: "完善"
      conditions:
        - story_points_set
        
    - from: 准备开发
      to: 进行中
      name: "开始工作"
      post_functions:
        - assign_to_current_user
        
    - from: 进行中
      to: 代码评审
      name: "提交评审"
      validators:
        - has_linked_pr
        
    - from: 代码评审
      to: 测试
      name: "通过评审"
      conditions:
        - all_reviewers_approved
        
    - from: 测试
      to: 已完成
      name: "通过测试"
      post_functions:
        - resolve_issue
```

## 最佳实践

1. **保持问题小**: 分解为 1-2 天可完成
2. **编写清晰的描述**: 包含所有需要的上下文
3. **关联相关问题**: 使用正确的问题关联
4. **定期更新状态**: 随着工作进展移动卡片
5. **一致使用标签**: 建立团队约定
6. **按点估算**: 使用相对大小
7. **每周回顾待办列表**: 保持待办列表整理
