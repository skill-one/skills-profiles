# 线性自动化

全面的技能，用于自动化线性问题跟踪和工程工作流。

## 核心工作流

### 1. 问题生命周期

```
线性问题流程：
┌─────────────────┐
│    初筛       │
│   (待办列表)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│    待办         │
│  (优先级排序)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  进行中        │
│   (活跃)      │
└────────┬────────┘
         ▼
┌─────────────────┐
│   审核中       │
│  (PR已创建)   │
└────────┬────────┘
         ▼
┌─────────────────┐
│     已完成       │
│   (已合并)      │
└────────┬────────┘
         ▼
┌─────────────────┐
│   已取消        │
│  (如需)    │
└─────────────────┘
```

### 2. 自动化触发器

```yaml
automations:
  - name: auto_assign_on_start
    trigger:
      type: status_changed
      to: "进行中"
    condition:
      assignee: null
    action:
      set_assignee: "{{trigger_user}}"
      
  - name: add_to_cycle
    trigger:
      type: issue_created
      labels: ["sprint-ready"]
    action:
      add_to_cycle: current
      set_priority: 紧急
      
  - name: create_pr_reminder
    trigger:
      type: status_changed
      to: "进行中"
      duration: "48小时"
    condition:
      no_linked_pr: true
    action:
      add_comment: "@{{assignee}} 请关联您的PR"
      
  - name: close_on_merge
    trigger:
      type: github_pr_merged
    action:
      set_status: "已完成"
      add_comment: "通过PR合并关闭"
```

## 问题模板

### 缺陷报告

```yaml
bug_template:
  title: "[缺陷] {{summary}}"
  team: "工程"
  
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
    - 操作系统: {{os}}
    - 浏览器: {{browser}}
    - 版本: {{version}}
    
    ## 日志/截图
    {{attachments}}
    
  labels: ["缺陷", "需要初筛"]
  priority: "{{severity}}"
  estimate: null
```

### 功能请求

```yaml
feature_template:
  title: "[功能] {{summary}}"
  team: "产品"
  
  description: |
    ## 概述
    {{overview}}
    
    ## 用户故事
    作为 {{user_type}}，我想要 {{action}}，以便 {{benefit}}。
    
    ## 接受标准
    - [ ] {{criteria1}}
    - [ ] {{criteria2}}
    - [ ] {{criteria3}}
    
    ## 设计
    {{design_link}}
    
    ## 技术考虑
    {{tech_notes}}
    
  labels: ["功能", "需要完善"]
  project: "{{roadmap_project}}"
```

### 子问题结构

```yaml
epic_breakdown:
  parent:
    title: "{{epic_name}}"
    type: "项目"
    
  sub_issues:
    - title: "设计: {{epic_name}}"
      labels: ["设计"]
      estimate: 3
      
    - title: "后端: {{epic_name}}"
      labels: ["后端"]
      estimate: 5
      
    - title: "前端: {{epic_name}}"
      labels: ["前端"]
      estimate: 5
      
    - title: "测试: {{epic_name}}"
      labels: ["测试"]
      estimate: 2
      
    - title: "文档: {{epic_name}}"
      labels: ["文档"]
      estimate: 1
```

## 周期管理

### 周期规划

```yaml
cycle_config:
  duration: 2周
  
  planning:
    capacity_per_engineer: 8  # 点数
    buffer_percentage: 20
    
  里程碑:
    - day: 1
      event: "周期开始"
    - day: 10
      event: "功能冻结"
    - day: 12
      event: "代码冻结"
    - day: 14
      event: "发布"
      
  auto_rollover:
    enabled: true
    statuses: ["待办", "待办"]
    exclude_labels: ["阻塞"]
```

### 周期仪表盘

```
周期24 - 第2/2周
═══════════════════════════════════════

进度:
████████████████░░░░ 78% 完成

故事点:
计划:    42
已完成:  33  ████████████████░░░░
剩余:    9  ████░░░░░░░░░░░░░░░░

按状态:
已完成         ████████████████ 18
审核中    ████░░░░░░░░░░░░ 5
进行中  ██░░░░░░░░░░░░░░░ 3
待办    ██░░░░░░░░░░░░░░ 2

团队进度:
Sarah    ██████████████░░ 8/10 点
Mike     ████████████████ 12/12 点
Alex     ██████████░░░░░░ 7/10 点
Lisa     ████████████░░░░ 6/10 点

阻塞项:
• LIN-234: 等待API访问
• LIN-256: 设计审核待定
```

## GitHub集成

### 分支与PR同步

```yaml
github_sync:
  branch_format: "{{username}}/lin-{{issue_number}}-{{issue_slug}}"
  
  on_branch_created:
    - set_status: "进行中"
    - add_assignee: branch_creator
    
  on_pr_opened:
    - set_status: "审核中"
    - add_link: pr_url
    - add_comment: "PR已打开: {{pr_url}}"
    
  on_pr_merged:
    - set_status: "已完成"
    - add_comment: "已合并到 {{pr_url}}"
    
  on_pr_closed:
    - add_comment: "PR关闭未合并"
    
  commit_linking:
    patterns:
      - "LIN-{{number}}"
      - "lin-{{number}}"
      - "Fixes LIN-{{number}}"
```

### CI/CD集成

```yaml
cicd_integration:
  on_build_failed:
    - add_label: "ci-failed"
    - add_comment: |
        ❌ 构建失败
        {{build_url}}
        
  on_build_passed:
    - remove_label: "ci-failed"
    
  on_deploy_staging:
    - add_label: "on-staging"
    - add_comment: "部署到预发布环境: {{staging_url}}"
    
  on_deploy_production:
    - add_label: "已发布"
    - add_comment: "发布到生产环境 🚀"
```

## 标签与组织

### 标签系统

```yaml
labels:
  type:
    - name: "缺陷"
      color: "#eb5757"
    - name: "功能"
      color: "#5e6ad2"
    - name: "改进"
      color: "#26b5ce"
    - name: "维护"
      color: "#bec2c8"
      
  优先级:
    - name: "紧急"
      color: "#eb5757"
    - name: "高"
      color: "#f2994a"
    - name: "中"
      color: "#f2c94c"
    - name: "低"
      color: "#bec2c8"
      
  领域:
    - name: "前端"
      color: "#5e6ad2"
    - name: "后端"
      color: "#26b5ce"
    - name: "基础设施"
      color: "#bb87fc"
    - name: "设计"
      color: "#f7b500"
      
  状态:
    - name: "阻塞"
      color: "#eb5757"
    - name: "需要审核"
      color: "#f2994a"
    - name: "就绪"
      color: "#0e7a42"
```

## 报表

### 速度跟踪

```yaml
velocity_report:
  metrics:
    - completed_points_per_cycle
    - issues_closed_per_cycle
    - cycle_completion_rate
    - carryover_percentage
    
  chart_data:
    cycles: last_6
    show_trend: true
    show_commitment: true
```

### 团队分析

```
团队速度 - 最近6个周期
═══════════════════════════════════════

│  50 ┤
│     │              ▓▓
│  40 ┤    ▓▓  ▓▓    ▓▓  ▓▓
│     │    ▓▓  ▓▓    ▓▓  ▓▓  ▓▓
│  30 ┤ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│     │ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│  20 ┤ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│     │ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│  10 ┤ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│     │ ▓▓ ▓▓  ▓▓ ▓▓ ▓▓  ▓▓  ▓▓
│   0 ┴─────────────────────────
       C19 C20 C21 C22 C23 C24

平均: 38点 | 趋势: +8%
完成率: 92%
```

## API示例

### GraphQL查询

```graphql
# 创建问题
mutation CreateIssue {
  issueCreate(input: {
    teamId: "team-id"
    title: "新功能请求"
    description: "描述"
    priority: 2
    labelIds: ["label-id"]
  }) {
    success
    issue {
      id
      identifier
      url
    }
  }
}

# 更新问题状态
mutation UpdateIssue {
  issueUpdate(
    id: "issue-id"
    input: {
      stateId: "state-id"
      assigneeId: "user-id"
    }
  ) {
    success
  }
}

# 查询周期问题
query CycleIssues {
  cycle(id: "cycle-id") {
    name
    issues {
      nodes {
        identifier
        title
        state {
          name
        }
        assignee {
          name
        }
        estimate
      }
    }
  }
}
```

## 最佳实践

1. **快速初筛**: 每日处理新问题
2. **一致估计**: 使用计划扑克
3. **关联所有内容**: 连接PR、提交、文档
4. **使用项目**: 组织相关工作
5. **周期承诺**: 保护冲刺范围
6. **定期梳理**: 保持待办列表健康
7. **自动化状态**: 让集成更新
8. **衡量速度**: 跟踪团队容量
