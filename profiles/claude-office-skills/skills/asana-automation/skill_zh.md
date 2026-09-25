# Asana 自动化

全面的技能，用于自动化 Asana 项目管理和团队协作。

## 核心工作流

### 1. 任务管理流程

```
任务生命周期：
┌─────────────────┐
│   新请求       │
└────────┬────────┘
         ▼
┌─────────────────┐
│   初筛与      │
│   优先级排序    │
└────────┬────────┘
         ▼
┌─────────────────┐
│   指派与      │
│   安排        │
└────────┬────────┘
         ▼
┌─────────────────┐
│   进行中       │
└────────┬────────┘
         ▼
┌─────────────────┐
│   审查        │
└────────┬────────┘
         ▼
┌─────────────────┐
│   完成        │
└─────────────────┘
```

### 2. 自动化规则

```yaml
automation_rules:
  - name: 按板块自动指派
    trigger:
      type: task_moved_to_section
      section: "设计"
    action:
      assign_to: "设计团队"
      add_followers: ["设计主管"]
      set_custom_field:
        部门: "设计"

  - name: 截止日期提醒
    trigger:
      type: due_date_approaching
      days_before: 2
    action:
      add_comment: "@{{assignee}} 提醒：此任务在2天内到期"
      add_to_project: "本周到期"

  - name: 完成通知
    trigger:
      type: task_completed
    action:
      notify_followers: true
      move_to_section: "已完成"
      add_comment: "✅ 完成于 {{completion_date}}"

  - name: 子任务创建
    trigger:
      type: task_added_to_project
      project: "新功能"
    action:
      add_subtasks:
        - "需求收集"
        - "设计原型"
        - "开发"
        - "测试"
        - "文档"
```

## 项目模板

### 功能发布模板

```yaml
project_template:
  name: "功能发布 - {{feature_name}}"
  team: "产品"

  sections:
    - name: "规划"
      tasks:
        - name: "定义需求"
          assignee: "产品经理"
          subtasks:
            - "用户故事"
            - "验收标准"
            - "成功指标"
        - name: "技术规格"
          assignee: "技术主管"
          
    - name: "设计"
      tasks:
        - name: "UX研究"
          duration: 5
        - name: "线框图"
          duration: 3
        - name: "视觉设计"
          duration: 5
          
    - name: "开发"
      tasks:
        - name: "后端实现"
          duration: 10
        - name: "前端实现"
          duration: 10
        - name: "API集成"
          duration: 5
          
    - name: "测试"
      tasks:
        - name: "QA测试"
          duration: 5
        - name: "修复缺陷"
          duration: 3
        - name: "用户验收测试"
          duration: 3
          
    - name: "发布"
      tasks:
        - name: "文档"
          duration: 3
        - name: "营销材料"
          duration: 5
        - name: "发布说明"
          duration: 1
        - name: "上线"
          milestone: true
```

### 爆发模板

```yaml
sprint_template:
  name: "爆发 {{number}} - {{dates}}"
  
  sections:
    - "积压"
    - "待办"
    - "进行中"
    - "评审"
    - "已完成"
    
  custom_fields:
    - name: "故事点"
      type: number
    - name: "优先级"
      type: dropdown
      options: ["P0", "P1", "P2", "P3"]
    - name: "类型"
      type: dropdown
      options: ["功能", "缺陷", "技术债务", "研究"]
```

## 自定义字段

### 字段配置

```yaml
custom_fields:
  - name: 优先级
    type: dropdown
    options:
      - name: "🔴 紧急"
        color: red
      - name: "🟠 高"
        color: orange
      - name: "🟡 中"
        color: yellow
      - name: "🟢 低"
        color: green
    
  - name: 状态
    type: dropdown
    options:
      - "未开始"
      - "进行中"
      - "阻塞"
      - "评审中"
      - "已完成"
    
  - name: 预计工时
    type: number
    precision: 1
    
  - name: 部门
    type: dropdown
    options:
      - "工程"
      - "设计"
      - "市场"
      - "销售"
      - "运营"
    
  - name: 截止周
    type: date
    format: week
```

## 负载管理

### 团队容量

```
团队负载 - 本周
═══════════════════════════════════════

Sarah (设计师)
██████████████████░░ 85% | 8个任务
容量: 40小时 | 已分配: 34小时

Mike (工程师)
████████████████░░░░ 78% | 12个任务
容量: 40小时 | 已分配: 31小时

Lisa (产品经理)
██████████████████████ 110% ⚠️ | 15个任务
容量: 40小时 | 已分配: 44小时

重新平衡建议:
• 将"API文档"从Lisa转移到Mike
• 延长"研究报告"的截止日期
• 为"发布准备"增加资源
```

### 时间线视图

```yaml
timeline_config:
  view: gantt
  date_range: "本季度"
  
  grouping: 
    primary: 项目
    secondary: 指派人
    
  里程碑:
    show: true
    style: 菱形
    
  依赖关系:
    show: true
    type: 完成-开始
    
  按字段着色:
    custom_field.priority
```

## 表单与接入

### 请求表单

```yaml
intake_form:
  name: "工作请求"
  project: "待处理请求"
  
  fields:
    - name: "请求标题"
      type: 单行文本
      required: true
      
    - name: "描述"
      type: 多行文本
      required: true
      
    - name: "请求类型"
      type: dropdown
      options:
        - "新功能"
        - "缺陷修复"
        - "内容更新"
        - "设计请求"
      required: true
      
    - name: "优先级"
      type: dropdown
      options: ["低", "中", "高", "紧急"]
      required: true
      
    - name: "截止日期"
      type: 日期
      required: false
      
    - name: "附件"
      type: 附件
      
  路由:
    - condition:
        field: "请求类型"
        equals: "设计请求"
      action:
        assign_to: "设计团队"
        add_to_project: "设计请求"
```

## 报表

### 投资组合仪表板

```
项目投资组合状态
═══════════════════════════════════════

活跃项目: 12
按计划: 8 (67%)
有风险: 3 (25%)
偏离计划: 1 (8%)

按状态:
┌────────────────────┬────────┬─────────┐
│ 项目              │ 状态   │ 完成率  │
├────────────────────┼────────┼─────────┤
│ 网站改版          │ 🟢     │ 78%     │
│ 移动应用v2        │ 🟡     │ 45%     │
│ CRM集成          │ 🟢     │ 92%     │
│ Q2市场             │ 🔴     │ 23%     │
│ 安全审计          │ 🟢     │ 65%     │
└────────────────────┴────────┴─────────┘

即将到来的里程碑:
• 1月25日: 网站Beta发布
• 1月30日: 移动应用QA完成
• 2月5日: CRM上线
```

### 团队指标

```yaml
reports:
  - name: "每周团队报告"
    metrics:
      - 完成的任务
      - 创建的任务
      - 过期任务
      - 完成率
    group_by: 指派人
    period: 过去7天
    
  - name: "项目进度"
    metrics:
      - 总任务数
      - 完成百分比
      - 剩余天数
      - 阻塞数量
    group_by: 项目
    
  - name: "燃尽图"
    type: 图表
    x轴: 日期
    y轴:
      - 总范围
      - 完成的任务
    period: 当前爆发
```

## 集成工作流

### Slack集成

```yaml
slack_integration:
  通知:
    - trigger: task_assigned_to_me
      channel: 私信
      message: "📋 新任务指派: {{task.name}}"
      
    - trigger: task_completed
      channel: "#团队更新"
      message: "✅ {{user}} 完成: {{task.name}}"
      
    - trigger: comment_added
      channel: 私信
      message: "💬 新评论在 {{task.name}}"
      
  命令:
    /asana:
      - 创建任务
      - 列出我的任务
      - 标记为完成
```

### GitHub集成

```yaml
github_integration:
  同步规则:
    - github_event: issue_opened
      asana_action:
        create_task:
          project: "GitHub问题"
          name: "{{issue.title}}"
          description: "{{issue.body}}"
          custom_fields:
            GitHub_Issue: "{{issue.number}}"
            
    - github_event: pr_merged
      asana_action:
        complete_task:
          match_field: "GitHub_PR"
          value: "{{pr.number}}"
```

## 最佳实践

1. **清晰的任务名称**: 使用行动动词，具体明确
2. **单一指派人**: 每个任务由一个人负责
3. **截止日期**: 始终设置现实的截止日期
4. **子任务**: 将复杂工作分解为更小的部分
5. **自定义字段**: 在所有项目中一致使用
6. **模板**: 创建可复用的项目结构
7. **定期评审**: 每周项目检查
8. **归档已完成**: 保持工作空间整洁
