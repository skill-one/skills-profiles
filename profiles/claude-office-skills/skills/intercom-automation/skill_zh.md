# Intercom 自动化

全面的技能，用于自动化 Intercom 客户沟通和支持工作流程。

## 核心工作流程

### 1. 对话流程

```
客户对话流程：
┌─────────────────┐
│  用户消息   │
│   (入站)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│   机器人分派    │
│  - 意图       │
│  - 路由        │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│  机器人 │ │ 人工  │
│  回复   │ │ 代理  │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│   解决方案    │
│  - 关闭        │
│  - 跟进        │
└─────────────────┘
```

### 2. 自动化规则

```yaml
automations:
  - name: welcome_new_users
    trigger:
      event: user.created
      conditions:
        - signed_up_at: within_last_hour
    action:
      send_message:
        type: chat
        delay: 5_minutes
        message: |
          Hey {{first_name}}! 👋
          
          欢迎来到 {{company_name}}！我在这里帮助你
          开始使用。今天是什么风把你吹来了？
        buttons:
          - "探索功能"
          - "我有问题"
          - "随便看看"
          
  - name: trial_expiring
    trigger:
      event: user.attribute_changed
      attribute: trial_days_remaining
      value: 3
    action:
      send_message:
        type: email
        template: trial_expiring
        
  - name: feature_announcement
    trigger:
      segment: power_users
      event: feature_released
    action:
      send_message:
        type: in_app
        message: "🎉 新功能：{{feature_name}}"
```

## 用户细分

### 细分定义

```yaml
segments:
  - name: trial_users
    filter:
      subscription_status: trial
      
  - name: power_users
    filter:
      sessions_count: "> 50"
      last_seen: "< 7 days"
      features_used: "> 5"
      
  - name: at_risk_users
    filter:
      subscription_status: active
      last_seen: "> 30 days"
      
  - name: enterprise_prospects
    filter:
      company_size: "> 100"
      plan: free
      
  - name: feature_requesters
    filter:
      tag: feature_request
      conversations_count: "> 0"
```

### 动态属性

```yaml
custom_attributes:
  - name: health_score
    type: number
    compute: |
      (sessions_last_30_days * 2) +
      (features_used * 3) +
      (team_members_active * 5)
      
  - name: lifecycle_stage
    type: string
    rules:
      - condition: signed_up_at < 7_days
        value: "onboarding"
      - condition: subscription_status == "trial"
        value: "trial"
      - condition: subscription_status == "active"
        value: "customer"
      - condition: subscription_status == "cancelled"
        value: "churned"
        
  - name: account_tier
    type: string
    source: company.plan
```

## 消息活动

### 新手引导系列

```yaml
onboarding_campaign:
  name: "新用户新手引导"
  audience: 
    segment: new_signups
    
  messages:
    - day: 0
      channel: in_app
      content: |
        欢迎来到 {{company}}! 🎉
        
        让我带你参观一下。点击下方开始
        快速 2 分钟的游览。
      cta: "开始游览"
      
    - day: 1
      channel: email
      subject: "小贴士：{{feature_1}}"
      content: |
        Hi {{first_name}},
        
        你知道你可以 {{feature_1_benefit}} 吗？
        
        这里是如何操作：{{feature_1_tutorial_link}}
        
    - day: 3
      channel: in_app
      trigger: 
        not_completed: "setup_wizard"
      content: |
        Hey {{first_name}}, 我注意到你还没有
        完成设置。需要帮助吗？
        
    - day: 7
      channel: email
      subject: "最近怎么样？"
      content: |
        Hi {{first_name}},
        
        你现在使用 {{company}} 已经一周了。
        
        有任何问题或反馈吗？直接回复这封邮件！
```

### 产品游览

```yaml
product_tours:
  - name: "欢迎游览"
    trigger:
      event: first_login
    steps:
      - element: "#dashboard"
        title: "你的仪表盘"
        body: "这里将显示你的关键指标"
        position: bottom
        
      - element: "#create-button"
        title: "创建新项目"
        body: "点击这里创建你的第一个项目"
        position: left
        
      - element: "#help-menu"
        title: "需要帮助？"
        body: "在这里查找文档和联系支持"
        position: bottom
        
  - name: "功能游览：报告"
    trigger:
      event: page_viewed
      url: "/reports"
      first_time: true
    steps:
      - element: "#date-picker"
        title: "日期范围"
        body: "选择你的报告周期"
```

## 支持工作流程

### 对话路由

```yaml
routing_rules:
  - name: vip_priority
    conditions:
      - company.plan: enterprise
    actions:
      - set_priority: urgent
      - assign_team: enterprise_support
      - send_notification: slack_vip
      
  - name: billing_issues
    conditions:
      - message_contains: ["billing", "charge", "invoice", "refund"]
    actions:
      - add_tag: billing
      - assign_team: billing_support
      
  - name: technical_support
    conditions:
      - message_contains: ["error", "bug", "not working", "broken"]
    actions:
      - add_tag: technical
      - assign_team: tech_support
      - create_ticket: jira
```

### 机器人回复

```yaml
bot_responses:
  - intent: greeting
    patterns: ["hi", "hello", "hey"]
    response: |
      Hi there! 👋 今天我能帮你什么？
      
  - intent: pricing
    patterns: ["pricing", "cost", "how much", "plans"]
    response: |
      不错的问题！这是我们的定价：
      
      • **起步版**: $29/月
      • **成长版**: $79/月
      • **企业版**: 定制
      
      你想让我联系销售吗？
    buttons:
      - "是的，联系销售"
      - "查看完整对比"
      
  - intent: password_reset
    patterns: ["forgot password", "reset password", "can't login"]
    response: |
      没问题！你可以在以下链接重置密码：
      {{password_reset_link}}
      
      链接将在 24 小时后过期。
    auto_close: true
```

## 分析与报告

### 对话指标

```
支持指标 - 本周
═══════════════════════════════════════

对话：
新对话:          234 (+12%)
已关闭:       256 (+8%)
未关闭:         45

响应时间：
首次回复:  2.3 分钟 (目标: 5 分钟) ✓
中位数:       8 分钟
解决时间:   2.4 小时

CSAT 分数:   4.7/5 ⭐ (+0.2)

按渠道：
聊天      ████████████░░░░ 156
邮件     ██████░░░░░░░░░░ 58
应用内    ████░░░░░░░░░░░░ 20

热门话题：
┌────────────────────┬───────┐
│ 话题              │ 数量 │
├────────────────────┼───────┤
│ 账单问题          │ 45    │
│ 功能请求          │ 38    │
│ 错误报告          │ 32    │
│ 使用指南          │ 28    │
└────────────────────┴───────┘
```

### 参与度仪表盘

```yaml
engagement_metrics:
  - name: message_open_rate
    formula: opened / sent * 100
    target: 40%
    
  - name: click_through_rate
    formula: clicked / opened * 100
    target: 10%
    
  - name: tour_completion_rate
    formula: completed / started * 100
    target: 60%
    
  - name: bot_resolution_rate
    formula: resolved_by_bot / total * 100
    target: 30%
```

## 集成工作流程

### CRM 同步

```yaml
crm_integration:
  salesforce:
    sync_fields:
      - intercom: company.name
        salesforce: Account.Name
      - intercom: user.email
        salesforce: Contact.Email
      - intercom: custom.mrr
        salesforce: Account.MRR__c
        
    events:
      - trigger: conversation_closed
        action: log_activity
        type: "支持互动"
        
      - trigger: user.tag_added
        tag: "sales_qualified"
        action: create_lead
```

### Slack 集成

```yaml
slack_integration:
  notifications:
    - trigger: new_conversation
      channel: "#support-inbox"
      conditions:
        - priority: urgent
      message: "🚨 紧急：{{user.name}} 需要帮助"
      
    - trigger: conversation_assigned
      notify: assignee_dm
      message: "新对话分配给你"
      
  commands:
    /intercom:
      - lookup_user
      - send_message
      - add_tag
```

## API 示例

### 创建或更新用户

```javascript
// 创建/更新用户
const user = await intercom.users.create({
  user_id: "12345",
  email: "user@example.com",
  name: "John Doe",
  signed_up_at: Math.floor(Date.now() / 1000),
  custom_attributes: {
    plan: "pro",
    team_size: 10,
    onboarding_complete: true
  }
});

// 发送消息
await intercom.messages.create({
  message_type: "inapp",
  body: "Hey! 新功能警报 🎉",
  from: {
    type: "admin",
    id: "admin_id"
  },
  to: {
    type: "user",
    user_id: "12345"
  }
});

// 搜索对话
const conversations = await intercom.conversations.search({
  query: {
    field: "state",
    operator: "=",
    value: "open"
  }
});
```

## 最佳实践

1. **个性化消息**: 使用用户属性
2. **适时发送**: 考虑用户时区
3. **不要过度发送**: 尊重频率限制
4. **机器人+人工**: 知道何时升级
5. **跟踪一切**: 衡量消息效果
6. **仔细细分**: 针对正确用户
7. **A/B 测试**: 优化消息内容
8. **快速解决**: 最小化响应时间
