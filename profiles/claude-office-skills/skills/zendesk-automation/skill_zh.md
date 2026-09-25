# Zendesk 自动化

全面的技能，用于自动化 Zendesk 支持工作流程和工单管理。

## 核心工作流程

### 1. 工单分派流程

```
入站工单流程：
┌─────────────────┐
│  新工单         │
└────────┬────────┘
         ▼
┌─────────────────┐
│  AI 分析         │
│  - 意图         │
│  - 情感         │
│  - 紧急程度      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  分类           │
│  - 类型         │
│  - 产品         │
│  - 所需技能      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  路由与分配      │
│  - 团队         │
│  - 代理         │
│  - 优先级       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  自动回复       │
│  (如适用)      │
└─────────────────┘
```

### 2. 路由规则

```yaml
routing_rules:
  - name: billing_issues
    conditions:
      - field: subject
        contains: ["billing", "invoice", "charge", "refund", "payment"]
      - field: tags
        includes: ["billing"]
    actions:
      - set_group: billing_team
      - set_priority: high
      - add_tags: ["billing_routed"]
  
  - name: technical_support
    conditions:
      - field: subject
        contains: ["error", "bug", "not working", "crash"]
      - field: product
        equals: "software"
    actions:
      - set_group: tech_support
      - set_priority: normal
      - add_tags: ["technical"]
  
  - name: enterprise_escalation
    conditions:
      - field: organization
        tier: enterprise
      - field: priority
        equals: urgent
    actions:
      - set_group: enterprise_team
      - set_priority: urgent
      - notify: slack_channel
```

### 3. 优先级矩阵

| 客户层级 | 问题类型 | 响应 SLA | 解决 SLA |
|--------------|------------|--------------|----------------|
| 企业级 | 关键 | 15 分钟 | 4 小时 |
| 企业级 | 高 | 1 小时 | 8 小时 |
| 商业级 | 关键 | 1 小时 | 8 小时 |
| 商业级 | 普通 | 4 小时 | 24 小时 |
| 标准级 | 所有 | 8 小时 | 48 小时 |

## 自动回复模板

### 常见问题回复

```yaml
auto_responses:
  password_reset:
    trigger:
      keywords: ["password", "reset", "forgot", "login"]
    response: |
      Hi {{ticket.requester.name}},
      
      我理解您在访问账户时遇到问题。以下是重置密码的方法：
      
      1. 访问 {{settings.login_url}}/forgot-password
      2. 输入您的邮箱地址
      3. 检查您的收件箱以获取重置链接
      4. 创建新密码
      
      如果您在 5 分钟内未收到邮件，请检查垃圾邮件文件夹。
      
      如果您需要进一步帮助，请告诉我！
    
    actions:
      - add_tags: ["auto_replied", "password_reset"]
      - set_status: pending

  shipping_inquiry:
    trigger:
      keywords: ["shipping", "tracking", "delivery", "order status"]
    response: |
      Hi {{ticket.requester.name}},
      
      感谢您联系我们查询订单！
      
      我查看了您的最近订单，以下是状态：
      {{#if order.tracking_number}}
      - 订单号: {{order.id}}
      - 状态: {{order.status}}
      - 追踪号: {{order.tracking_number}}
      - 预计送达: {{order.estimated_delivery}}
      {{else}}
      您的订单正在处理中，24 小时内将提供追踪信息。
      {{/if}}
      
      还有什么我可以帮助您的吗？
```

## 工单管理

### 宏库

```yaml
macros:
  - name: request_more_info
    actions:
      - add_comment: |
          感谢联系我们。为了更好地协助您，请提供：
          1. 您的账户邮箱
          2. 复现问题的步骤
          3. 您看到的任何错误信息
          4. 如果可能，请提供截图
      - set_status: pending
      - add_tags: ["awaiting_info"]

  - name: escalate_to_engineering
    actions:
      - add_internal_note: "已升级至工程团队"
      - set_group: engineering
      - set_priority: high
      - add_tags: ["escalated", "engineering"]
      - notify: engineering_slack

  - name: close_resolved
    actions:
      - add_comment: |
          很高兴我们能帮助您解决问题！ 
          
          如果您还有其他问题，随时可以联系我们。我们随时为您提供帮助。
          
          祝您有美好的一天!
      - set_status: solved
      - add_tags: ["resolved"]
```

### 批量操作

```yaml
bulk_actions:
  - name: close_stale_tickets
    schedule: "0 0 * * *"  # 每日
    conditions:
      - status: pending
      - last_update_days: 7
    actions:
      - add_comment: "由于未回复而关闭。如有需要请重新打开。"
      - set_status: solved
      - add_tags: ["auto_closed"]

  - name: escalate_breaching_sla
    schedule: "*/15 * * * *"  # 每 15 分钟
    conditions:
      - sla_breach_in_minutes: 30
    actions:
      - set_priority: urgent
      - notify: team_lead
      - add_tags: ["sla_at_risk"]
```

## SLA 管理

### SLA 政策

```yaml
sla_policies:
  - name: enterprise_sla
    conditions:
      organization_tag: enterprise
    targets:
      first_reply:
        urgent: 15  # 分钟
        high: 60
        normal: 240
      resolution:
        urgent: 240
        high: 480
        normal: 1440

  - name: standard_sla
    conditions:
      default: true
    targets:
      first_reply:
        urgent: 60
        high: 240
        normal: 480
      resolution:
        urgent: 480
        high: 1440
        normal: 2880
```

### SLA 仪表盘

```
SLA 性能 - 本周
═══════════════════════════════════════

首次回复 SLA:
企业级  ████████████████████ 98% ✓
商业级    ██████████████████░░ 94% ✓
标准级    █████████████████░░░ 89% ⚠

解决 SLA:
企业级  ████████████████████ 96% ✓
商业级    █████████████████░░░ 91% ✓
标准级    ████████████████░░░░ 85% ⚠

有风险的工单:
┌──────────┬──────────┬───────────┐
│ 工单     │ 客户     │ 剩余时间 │
├──────────┼──────────┼───────────┤
│ #45231   │ Acme Corp│ 12 分钟    │
│ #45198   │ TechStart│ 28 分钟    │
│ #45156   │ DataFlow │ 45 分钟    │
└──────────┴──────────┴───────────┘
```

## AI 驱动的功能

### 情感分析

```yaml
sentiment_analysis:
  enabled: true
  actions:
    negative:
      - add_tags: ["negative_sentiment"]
      - set_priority: +1  # 提高优先级
      - notify: team_lead
    
    frustrated:
      - add_tags: ["frustrated_customer"]
      - route_to: senior_agents
      - add_internal_note: "客户似乎很沮丧"
```

### 意图检测

```yaml
intent_detection:
  categories:
    - name: billing_inquiry
      keywords: ["charge", "invoice", "refund", "bill"]
      confidence_threshold: 0.8
    
    - name: technical_issue
      keywords: ["error", "bug", "broken", "crash"]
      confidence_threshold: 0.75
    
    - name: feature_request
      keywords: ["wish", "would be nice", "suggest", "feature"]
      confidence_threshold: 0.7
    
    - name: cancellation
      keywords: ["cancel", "stop", "end subscription"]
      confidence_threshold: 0.85
      actions:
        - route_to: retention_team
        - set_priority: high
```

## 集成工作流程

### Slack 集成

```yaml
slack_integration:
  notifications:
    - trigger: new_urgent_ticket
      channel: "#support-urgent"
      message: "🚨 新的紧急工单: {{ticket.subject}}"
    
    - trigger: sla_warning
      channel: "#support-alerts"
      message: "⚠️ 工单 #{{ticket.id}} 接近 SLA 违规"
    
    - trigger: negative_csat
      channel: "#support-feedback"
      message: "📉 收到低 CSAT 工单 #{{ticket.id}}"
```

### JIRA 集成

```yaml
jira_integration:
  sync_rules:
    - zendesk_tag: bug_confirmed
      create_jira:
        project: DEV
        issue_type: Bug
        priority_map:
          urgent: Highest
          high: High
          normal: Medium
        sync_fields:
          - description
          - attachments
        link_back: true
```

## 分析与报告

### 关键指标

```
支持指标仪表盘
═══════════════════════════════════════

量:
今日工单: 156 (+12% vs 平均)
未解决工单: 234
积压: 45

性能:
平均首次回复: 42 分钟 (目标: 60 分钟) ✓
平均解决: 4.2 小时 (目标: 8 小时) ✓
一键解决: 34%

满意度:
CSAT 分数: 4.6/5.0 ⭐
NPS: +45
回复质量: 92%

代理性能:
┌────────────┬────────┬──────────┬──────┐
│ 代理      │ 解决   │ 平均时间 │ CSAT │
├────────────┼────────┼──────────┼──────┤
│ Sarah      │ 28     │ 3.1 小时  │ 4.8  │
│ Mike       │ 25     │ 3.5 小时  │ 4.7  │
│ Lisa       │ 22     │ 4.0 小时  │ 4.6  │
└────────────┴────────┴──────────┴──────┘
```

## 最佳实践

1. **快速首次回复**: 即使解决需要较长时间，也要快速确认工单
2. **明智使用宏**: 个性化模板回复
3. **一致标记**: 启用更好的路由和报告
4. **监控 SLA**: 在违规前设置警报
5. **收集反馈**: 解决后发送 CSAT 问卷
6. **定期培训**: 更新代理关于常见问题
