# Pipedrive 自动化

全面的技能，用于自动化 Pipedrive CRM 和销售管道管理。

## 核心工作流

### 1. 销售管道

```
PIPEDRIVE 管道流程:
┌─────────────────────────────────────────────────────────┐
│                     管道视图                        │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ 潜在客户 │ 联系人  │ 提案 │ 商谈  │   赢得/     │
│  入口    │ 促成    │  发送    │  中    │   失去     │
├──────────┼──────────┼──────────┼──────────┼────────────┤
│ $15,000  │ $45,000  │ $80,000  │ $35,000  │ $125,000   │
│ 5 笔交易  │ 8 笔交易  │ 6 笔交易  │ 3 笔交易  │ 12 笔交易   │
├──────────┼──────────┼──────────┼──────────┼────────────┤
│ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │            │
│ │Acme  │ │ │Tech  │ │ │StartX│ │ │BigCo │ │            │
│ │$5,000│ │ │$12K  │ │ │$25K  │ │ │$20K  │ │            │
│ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘ │            │
└──────────┴──────────┴──────────┴──────────┴────────────┘
```

### 2. 自动化触发器

```yaml
automations:
  - name: new_deal_setup
    trigger:
      type: deal_created
    actions:
      - create_activity:
          type: call
          subject: "初步发现通话"
          due_days: 1
      - send_email:
          template: welcome_sequence
      - add_label: "新"

  - name: stage_progression
    trigger:
      type: deal_stage_changed
      to_stage: "Proposal Sent"
    actions:
      - create_activity:
          type: task
          subject: "跟进提案"
          due_days: 3
      - update_custom_field:
          field: "Proposal Date"
          value: "{{today}}"
          
  - name: stale_deal_alert
    trigger:
      type: deal_rotting
      days: 14
    actions:
      - send_notification:
          to: owner
          message: "交易在14天内没有进展"
      - add_label: "有风险"
```

## 交易管理

### 交易配置

```yaml
deal_structure:
  required_fields:
    - title
    - value
    - organization
    - stage
    - owner
    
  custom_fields:
    - name: "潜在客户来源"
      type: enum
      options:
        - "入口 - 网站"
        - "入口 - 推荐人"
        - "出口 - 冷接触"
        - "活动"
        - "合作伙伴"
        
    - name: "产品兴趣"
      type: set
      options:
        - "产品 A"
        - "产品 B"
        - "服务"
        
    - name: "决策时间线"
      type: enum
      options:
        - "< 1 个月"
        - "1-3 个月"
        - "3-6 个月"
        - "6+ 个月"
        
    - name: "提案金额"
      type: monetary
      
    - name: "关闭概率"
      type: numeric
      format: 百分比
```

### 管道阶段

```yaml
pipeline_config:
  name: "销售管道"
  
  stages:
    - name: "潜在客户入口"
      probability: 10%
      rotting_days: 7
      
    - name: "联系人促成"
      probability: 20%
      rotting_days: 10
      
    - name: "需求定义"
      probability: 40%
      rotting_days: 14
      
    - name: "提案发送"
      probability: 60%
      rotting_days: 14
      
    - name: "商谈"
      probability: 80%
      rotting_days: 7
      
    - name: "赢得"
      probability: 100%
      
    - name: "失去"
      probability: 0%
```

## 活动管理

### 活动类型

```yaml
activity_types:
  - name: "通话"
    icon: phone
    default_duration: 15
    
  - name: "会议"
    icon: calendar
    default_duration: 60
    
  - name: "邮件"
    icon: mail
    default_duration: 5
    
  - name: "任务"
    icon: checkbox
    default_duration: 30
    
  - name: "演示"
    icon: presentation
    default_duration: 45
```

### 活动自动化

```yaml
activity_workflows:
  discovery_call_complete:
    trigger:
      activity_type: call
      marked_done: true
      deal_stage: "Lead In"
    actions:
      - move_deal_stage: "Contact Made"
      - create_activity:
          type: task
          subject: "发送跟进邮件"
          due_days: 1
      - update_deal:
          custom_field: "首次联系日期"
          value: "{{activity.done_time}}"
          
  meeting_scheduled:
    trigger:
      activity_type: meeting
      created: true
    actions:
      - send_email:
          template: meeting_confirmation
          to: "{{deal.contact}}"
      - create_activity:
          type: task
          subject: "准备会议议程"
          due_before_meeting: 1_day
```

## 邮件集成

### 邮件模板

```yaml
email_templates:
  - name: "初步接触"
    subject: "{{company}} + {{prospect_company}}"
    body: |
      Hi {{first_name}},
      
      我注意到 {{company_insight}} 并认为 
      {{value_proposition}}。
      
      你这周愿意安排一个 15 分钟的通话吗？
      
      Best,
      {{sender_name}}
      
  - name: "提案跟进"
    subject: "关于我们提案的跟进"
    body: |
      Hi {{first_name}},
      
      我想跟进我于 {{proposal_date}} 发送的提案。
      
      你有任何问题我可以帮忙解答吗？
      
      Best,
      {{sender_name}}
```

### 邮件追踪

```yaml
email_tracking:
  features:
    - open_tracking
    - link_tracking
    - attachment_tracking
    
  automations:
    on_email_opened:
      - create_activity:
          type: task
          subject: "跟进 - 邮件已打开"
          due_hours: 2
          
    on_link_clicked:
      - add_note: "点击链接: {{link_url}}"
      - update_custom_field:
          field: "参与程度"
          value: "高"
```

## 报告与分析

### 销售仪表盘

```
销售仪表盘 - 2024年1月
═══════════════════════════════════════

管道价值: $175,000
加权: $89,500

按阶段:
潜在客户入口       ████░░░░░░░░░░░░ $15,000
联系人促成        ████████░░░░░░░░ $45,000
提案            ████████████░░░░ $80,000
商谈            ██████░░░░░░░░░░ $35,000

销售速度:
成交交易:     12
平均价值:    $10,400
赢率:         28%
销售周期:      34 天

按代表:
┌────────────┬────────┬──────────┬───────┐
│ 代表        │ 交易  │ 价值    │ 赢率 │
├────────────┼────────┼──────────┼───────┤
│ Sarah      │ 5      │ $52,000  │ 35%   │
│ Mike       │ 4      │ $41,000  │ 28%   │
│ Lisa       │ 3      │ $32,000  │ 22%   │
└────────────┴────────┴──────────┴───────┘

预测:
本月:   $45,000 (加权)
下月:   $68,000 (加权)
```

### 赢/输分析

```yaml
win_loss_tracking:
  won_reasons:
    - "最佳产品匹配"
    - "竞争性定价"
    - "关系/信任"
    - "实施时间线"
    
  lost_reasons:
    - "价格太高"
    - "选择了竞争对手"
    - "没有预算"
    - "没有做出决定"
    - "失去联系"
    
  analysis:
    win_rate_by_source:
      inbound: 35%
      outbound: 18%
      referral: 45%
      
    win_rate_by_size:
      small: 42%
      medium: 28%
      enterprise: 15%
```

## 集成工作流

### Slack 集成

```yaml
slack_notifications:
  - trigger: deal_won
    channel: "#wins"
    message: |
      🎉 *交易赢得!*
      *公司:* {{organization.name}}
      *价值:* ${{deal.value}}
      *负责人:* {{deal.owner}}
      
  - trigger: deal_stage_changed
    to_stage: "Negotiation"
    channel: "#sales"
    message: |
      📊 交易进入商谈
      {{deal.title}} - ${{deal.value}}
      
  - trigger: activity_overdue
    notify: owner_dm
    message: |
      ⚠️ 过期活动: {{activity.subject}}
```

### 日历同步

```yaml
calendar_integration:
  provider: google_calendar
  
  sync_settings:
    meetings: bidirectional
    calls: to_calendar
    
  automations:
    on_calendar_event:
      - create_activity:
          type: meeting
          link_to: attendee_organization
```

## API 示例

### 交易操作

```javascript
// 创建交易
const deal = await pipedrive.deals.create({
  title: "Acme Corp - 企业计划",
  value: 50000,
  currency: "USD",
  org_id: 123,
  person_id: 456,
  stage_id: 1,
  expected_close_date: "2024-02-28",
  custom_fields: {
    "Lead Source": "入口 - 网站",
    "Decision Timeline": "1-3 个月"
  }
});

// 更新交易阶段
await pipedrive.deals.update(deal.id, {
  stage_id: 3  // 移动到 "Proposal Sent"
});

// 添加活动
await pipedrive.activities.create({
  deal_id: deal.id,
  type: "call",
  subject: "发现通话",
  due_date: "2024-01-20",
  due_time: "14:00"
});

// 标记活动完成
await pipedrive.activities.update(activityId, {
  done: true,
  note: "很好的通话，继续提案"
});
```

## 最佳实践

1. **阶段纪律**: 每个阶段都有明确的标准
2. **活动记录**: 记录所有互动
3. **管道卫生**: 定期审查交易
4. **过期警报**: 不要让交易停滞
5. **自定义字段**: 跟踪关键数据点
6. **模板**: 保持沟通一致
7. **报告**: 每周管道审查
8. **集成**: 连接所有触点
