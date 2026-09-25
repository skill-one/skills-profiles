# ClickUp 自动化

全面的技能，用于自动化 ClickUp 工作空间和任务管理。

## 核心概念

### 工作空间层级

```
CLICKUP 层级结构：
┌─────────────────────────────────────────────────────────┐
│ 🏢 工作空间                                            │
├─────────────────────────────────────────────────────────┤
│   ├── 📁 空间：工程                                     │
│   │   ├── 📂 文件夹：Q1 项目                           │
│   │   │   ├── 📋 列表：功能开发                       │
│   │   │   │   ├── ✅ 任务：实现认证                   │
│   │   │   │   │   └── ☑️ 子任务：OAuth 设置          │
│   │   │   │   └── ✅ 任务：构建 API                   │
│   │   │   └── 📋 列表：修复 Bug                       │
│   │   └── 📂 文件夹：基础设施                           │
│   │                                                     │
│   ├── 📁 空间：市场营销                               │
│   │   └── 📋 列表：内容日历                           │
│   │                                                     │
│   └── 📁 空间：运营                                   │
└─────────────────────────────────────────────────────────┘
```

### 任务结构

```yaml
task_structure:
  required:
    name: "{{task_name}}"
    list_id: "{{list_id}}"
    
  optional:
    description: "{{description}}"
    assignees: ["user_id_1", "user_id_2"]
    tags: ["功能", "优先级"]
    status: "开放"
    priority: 2  # 1=紧急, 2=高, 3=正常, 4=低
    due_date: "2024-01-20"
    start_date: "2024-01-15"
    time_estimate: 28800000  # 毫秒 (8 小时)
    
  custom_fields:
    - id: "field_id"
      value: "自定义值"
      
  checklists:
    - name: "验收标准"
      items:
        - name: "需求 1"
          resolved: false
```

## 自动化规则

### 内置自动化

```yaml
automations:
  - name: 创建时自动分配
    trigger:
      type: task_created
      list_id: "list_123"
    conditions:
      - tag_contains: "设计"
    actions:
      - add_assignee: "设计负责人_id"
      - set_priority: high
      
  - name: 截止日期提醒
    trigger:
      type: due_date
      before: 1_day
    actions:
      - send_notification:
          to: assignees
          message: "任务明天到期：{{task.name}}"
      - add_tag: "即将到期"
      
  - name: 状态变更工作流
    trigger:
      type: status_changed
      to: "待审核"
    actions:
      - remove_assignee: "{{previous_assignee}}"
      - add_assignee: "审核者_id"
      - add_comment: "准备审核 @reviewer"
      
  - name: 完成父任务
    trigger:
      type: all_subtasks_done
    actions:
      - set_status: "完成"
      - add_comment: "所有子任务已完成 ✓"
```

### 高级自动化

```yaml
advanced_rules:
  - name: 计划迭代
    trigger:
      type: schedule
      cron: "0 0 * * 1"  # 周一凌晨
    conditions:
      - status_not: "完成"
      - due_date_passed: true
    actions:
      - move_to_list: "{{next_sprint_list}}"
      - update_due_date: "+7 天"
      - add_comment: "从上一个迭代转移过来"
      
  - name: 升级工作流
    trigger:
      type: task_blocked
      duration: 48_hours
    actions:
      - set_priority: urgent
      - notify: manager
      - add_watcher: "manager_id"
      - add_tag: "已升级"
```

## 视图与布局

### 视图类型

```yaml
views:
  list_view:
    type: list
    group_by: status
    sort_by: priority
    columns:
      - name
      - assignees
      - due_date
      - priority
      - time_estimate
      
  board_view:
    type: board
    group_by: status
    card_fields:
      - assignees
      - due_date
      - tags
      - subtasks_count
      
  calendar_view:
    type: calendar
    date_field: due_date
    color_by: priority
    
  timeline_view:
    type: timeline
    start_field: start_date
    end_field: due_date
    dependencies: true
    
  workload_view:
    type: workload
    capacity_field: time_estimate
    group_by: assignee
```

### 仪表板小部件

```yaml
dashboard:
  widgets:
    - type: sprint_burndown
      list_id: "current_sprint"
      
    - type: workload
      space_id: "工程"
      period: this_week
      
    - type: task_status
      filter:
        assignee: me
        
    - type: time_tracked
      group_by: project
      period: this_month
      
    - type: goals_progress
      folder_id: "q1_goals"
```

## 时间跟踪

### 时间条目配置

```yaml
time_tracking:
  settings:
    billable_default: true
    rounding: 15 分钟
    require_description: false
    
  entry:
    task_id: "task_123"
    start: "2024-01-15T09:00:00Z"
    end: "2024-01-15T11:30:00Z"
    duration: 9000000  # 2.5 小时，毫秒
    billable: true
    description: "开发工作"
    
  reports:
    - type: user_summary
      period: this_week
      group_by: task
      
    - type: project_summary
      period: this_month
      group_by: user
```

### 时间报告仪表板

```
时间跟踪 - 本周
═══════════════════════════════════════

总计：32h 45m

按项目：
功能开发   ████████████████ 18h 30m
修复 Bug     ████████░░░░░░░░ 8h 15m
会议      ████░░░░░░░░░░░░ 4h 00m
管理       ██░░░░░░░░░░░░░░ 2h 00m

按天：
Mon    █████████████████ 7h 30m
Tue    ███████████████░░ 6h 45m
Wed    ██████████████░░░ 6h 15m
Thu    ████████████████░ 7h 00m
Fri    ███████████░░░░░░ 5h 15m

可计费：28h 00m (85%)
```

## 目标与 OKRs

### 目标结构

```yaml
goals:
  - name: "Q1 产品目标"
    type: folder
    
    targets:
      - name: "发布 v2.0"
        type: true_false
        due_date: "2024-03-31"
        
      - name: "减少 Bug 数量"
        type: number
        start: 45
        target: 10
        unit: "开放 Bug"
        
      - name: "提高测试覆盖率"
        type: 百分比
        start: 65
        target: 85
        
    key_results:
      - task_list: "v2.0 功能"
        measure: tasks_completed
```

### 目标仪表板

```
Q1 目标进度
═══════════════════════════════════════

发布 v2.0
████████████████████ 100% ✓
完成于 3 月 28 日

减少 Bug 数量
████████████████░░░░ 78%
当前：15 | 目标：10

提高测试覆盖率
██████████████░░░░░░ 72%
当前：79% | 目标：85%

总体 Q1：83% 完成
```

## 模板

### 任务模板

```yaml
task_templates:
  - name: "Bug 报告"
    status: "开放"
    priority: high
    tags: ["Bug"]
    description: |
      ## Bug 描述
      {{description}}
      
      ## 复现步骤
      1. 
      2. 
      3. 
      
      ## 预期行为
      
      ## 实际行为
      
      ## 环境
      - 浏览器： 
      - 操作系统： 
      - 版本： 
      
    checklists:
      - name: "Bug 修复工作流"
        items:
          - "复现 Bug"
          - "识别根本原因"
          - "实现修复"
          - "编写测试"
          - "代码审查"
          - "部署"
          
  - name: "功能请求"
    status: "待处理"
    custom_fields:
      story_points: null
    checklists:
      - name: "功能工作流"
        items:
          - "需求定义"
          - "设计批准"
          - "实现"
          - "测试"
          - "文档"
```

## 集成

### Slack 集成

```yaml
slack_integration:
  notifications:
    - trigger: task_created
      channel: "#项目更新"
      include: [name, assignees, due_date]
      
    - trigger: status_changed
      to: "完成"
      channel: "#胜利"
      message: "✅ {{task.name}} 已完成，由 {{user.name}} 完成"
      
  commands:
    /clickup:
      - create_task
      - my_tasks
      - log_time
```

### GitHub 集成

```yaml
github_integration:
  branch_naming:
    pattern: "{{task.id}}-{{task.slug}}"
    
  automations:
    - trigger: branch_created
      actions:
        - set_status: "进行中"
        - add_comment: "分支创建：{{branch.name}}"
        
    - trigger: pr_opened
      actions:
        - set_status: "待审核"
        - link_pr: "{{pr.url}}"
        
    - trigger: pr_merged
      actions:
        - set_status: "完成"
```

## API 示例

### 任务操作

```javascript
// 创建任务
const task = await clickup.tasks.create(listId, {
  name: "实现用户认证",
  description: "添加 OAuth2 支持",
  assignees: [userId],
  priority: 2,
  due_date: Date.now() + 7 * 24 * 60 * 60 * 1000,
  time_estimate: 28800000,
  custom_fields: [
    { id: "field_id", value: "5" }
  ]
});

// 更新任务
await clickup.tasks.update(taskId, {
  status: "进行中",
  assignees: { add: [newUserId] }
});

// 添加时间条目
await clickup.timeEntries.create(taskId, {
  start: Date.now() - 3600000,
  duration: 3600000,
  billable: true
});

// 创建检查清单
await clickup.checklists.create(taskId, {
  name: "验收标准"
});
```

## 最佳实践

1. **层级设计**：空间 → 文件夹 → 列表
2. **一致状态**：跨列表标准化
3. **自定义字段**：跟踪关键指标
4. **自动化**：减少手动工作
5. **时间跟踪**：启用容量规划
6. **模板**：标准化任务创建
7. **目标**：与目标对齐
8. **视图**：配置不同需求
