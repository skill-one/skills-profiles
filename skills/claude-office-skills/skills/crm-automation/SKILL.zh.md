---
name: crm-automation
description: HubSpot、Salesforce、Pipedrive的CRM工作流自动化 - 销售线索管理、交易跟踪和多CRM同步
---

# CRM 自动化

自动化 HubSpot、Salesforce 和 Pipedrive 的 CRM 工作流程，包括潜在客户管理、交易跟踪、管道自动化和多 CRM 同步。基于 n8n 工作流模板。

## 概述

本技能涵盖：
- 潜在客户捕获和丰富自动化
- 交易阶段进展工作流
- 多 CRM 数据同步
- 自动化跟进流程
- 销售分析和报告

---

## 核心工作流模式

### 1. 潜在客户捕获 → 丰富 → 分配

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 潜在客户来源 │───▶│ 丰富数据   │───▶│ 评分潜在客户 │───▶│ 分配给销售代表 │
│ (表单/API)  │    │ (Clearbit)  │    │ (AI/规则)  │    │ (HubSpot)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                         ┌─────────────┐    ┌─────────────┐    │
                         │ 开始       │◀───│ 创建在CRM   │◀───┘
                         │ 跟进流程    │    │ 中         │
                         └─────────────┘    └─────────────┘
```

**n8n 配置**：
```yaml
workflow: "潜在客户捕获到CRM"

trigger:
  - type: webhook
    event: form_submission
    source: [网站, 登录页面, Calendly]

steps:
  1. capture_lead:
      fields: [email, name, company, phone, source]
  
  2. enrich_data:
      provider: clearbit
      lookup_by: email
      append: [company_size, industry, title, linkedin]
  
  3. score_lead:
      model: ai_scoring  # 或基于规则
      factors:
        - company_size: {1-50: 10, 51-200: 20, 201+: 30}
        - industry_fit: {high: 30, medium: 20, low: 10}
        - title_seniority: {c-level: 30, director: 20, manager: 10}
      threshold: 50  # MQL 阈值
  
  4. route_lead:
      rules:
        - if: score >= 80 AND industry == "tech"
          assign_to: "企业团队"
        - if: score >= 50
          assign_to: "中小企业团队"
        - else:
          assign_to: "市场培育"
  
  5. create_in_crm:
      platform: hubspot
      object: contact
      properties:
        email: "{email}"
        firstname: "{first_name}"
        company: "{company}"
        lead_score: "{score}"
        lead_source: "{source}"
  
  6. start_sequence:
      if: score >= 50
      sequence: "新潜在客户欢迎"
      delay: 1_hour
```

---

### 2. 交易阶段自动化

```yaml
workflow: "交易阶段进展"

trigger:
  - type: hubspot_deal_updated
    property: dealstage

stages:
  appointment_scheduled:
    actions:
      - create_task: "准备会议"
        due: 1天前
      - notify_slack: "#sales-pipeline"
      - update_property: last_activity_date
  
  qualified_to_buy:
    actions:
      - create_task: "发送提案"
        due: 3天
      - notify_manager: true
      - add_to_forecast: true
  
  presentation_scheduled:
    actions:
      - create_task: "准备演示环境"
      - send_reminder: 1小时前
      - log_activity: "演示已安排"
  
  contract_sent:
    actions:
      - set_close_date: 14天后
      - create_task: "跟进合同"
        due: 7天
      - notify_legal: if amount > 50000
  
  closed_won:
    actions:
      - notify_slack: "#wins"
      - trigger_onboarding: true
      - update_forecast: remove
      - celebrate: confetti  # Slack 庆祝
  
  closed_lost:
    actions:
      - log_loss_reason: required
      - add_to_nurture: true
      - schedule_reengagement: 90天
```

---

### 3. 多 CRM 同步

```yaml
workflow: "HubSpot + Salesforce + Pipedrive 同步"

sync_rules:
  contacts:
    master: hubspot
    sync_to: [salesforce, pipedrive]
    frequency: 实时
    fields:
      - email (唯一键)
      - name
      - company
      - phone
      - owner
    conflict_resolution: 最近优先
    deduplication: 
      provider: openai
      similarity_threshold: 0.85
  
  deals:
    master: salesforce
    sync_to: [hubspot, pipedrive]
    frequency: 每15分钟
    field_mapping:
      salesforce.Opportunity.Amount → hubspot.deal.amount
      salesforce.Opportunity.CloseDate → hubspot.deal.closedate
      salesforce.Opportunity.StageName → hubspot.deal.dealstage
  
  activities:
    aggregate_to: google_sheets
    types: [电话, 邮件, 会议, 备注]
    columns: [日期, 潜在客户, 类型, 摘要, 结果]
```

**n8n 实现**：
```javascript
// 多 CRM 同步节点
{
  "nodes": [
    {
      "name": "获取 HubSpot 潜在客户",
      "type": "n8n-nodes-base.hubspot",
      "parameters": {
        "operation": "getAll",
        "limit": 100,
        "additionalFields": {
          "propertiesToInclude": ["email", "firstname", "lastname", "company"]
        }
      }
    },
    {
      "name": "获取 Salesforce 潜在客户",
      "type": "n8n-nodes-base.salesforce",
      "parameters": {
        "operation": "getAll",
        "sobject": "Contact"
      }
    },
    {
      "name": "使用 OpenAI 去重",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "operation": "message",
        "model": "gpt-4",
        "prompt": "比较这些潜在客户并识别重复项: {{$json}}"
      }
    },
    {
      "name": "同步到主表",
      "type": "n8n-nodes-base.googleSheets",
      "parameters": {
        "operation": "append",
        "sheetId": "your-sheet-id"
      }
    }
  ]
}
```

---

## 潜在客户评分模型

### 基于规则的评分

```yaml
lead_score_rules:
  人口统计:
    职位:
      - C级|VP|总监: +30
      - 经理|负责人: +20
      - 个体贡献者: +10
    
    公司规模:
      - 1-50: +10
      - 51-200: +20
      - 201-1000: +25
      - 1000+: +30
    
    行业:
      - 技术|SaaS: +30
      - 金融|医疗保健: +25
      - 制造业|零售: +15
  
  行为:
    网站访问:
      - 1-2: +5
      - 3-5: +10
      - 6+: +20
    
    内容下载:
      - 白皮书: +15
      - 案例研究: +20
      - 定价页面: +25
    
    邮件参与:
      - 打开: +5
      - 点击: +10
      - 回复: +20

阈值:
  - MQL: 50
  - SQL: 75
  - 热潜在客户: 90
```

### 基于AI的评分

```yaml
ai_scoring_model:
  provider: openai
  prompt: |
    根据以下因素为这个潜在客户评分（0-100）：
    - 与我们理想客户画像（ICP）的匹配度
    - 购买意向信号
    - 预算授权
    - 时间紧迫性
    
    潜在客户数据: {lead_data}
    ICP: B2B SaaS公司，50-500名员工，A+轮
    返回JSON: {"score": X, "reasoning": "...", "next_action": "..."}
```

---

## 自动化流程

### 流程 1：新潜在客户欢迎

```yaml
sequence: "新潜在客户欢迎"
trigger: lead_created AND score >= 50

steps:
  - day_0:
      type: email
      template: "welcome_intro"
      subject: "欢迎到 {Company} - 接下来该做什么"
  
  - day_2:
      type: email
      template: "value_prop"
      subject: "如何 {Similar_Company} 实现了 {Result}"
      condition: not_replied
  
  - day_4:
      type: task
      action: "LinkedIn 连接请求"
      assign_to: owner
  
  - day_7:
      type: email
      template: "case_study"
      subject: "快速案例研究为 {Lead_Company}"
      condition: not_replied
  
  - day_10:
      type: email
      template: "meeting_request"
      subject: "15分钟讨论 {Pain_Point}？"
      include: calendly_link
  
  - day_14:
      type: task
      action: "电话尝试"
      assign_to: owner
      condition: not_responded
```

### 流程 2：交易跟进

```yaml
sequence: "提案跟进"
trigger: deal_stage == "contract_sent"

steps:
  - day_3:
      type: email
      template: "contract_check_in"
      subject: "提案有任何问题吗？"
  
  - day_7:
      type: task
      action: "电话 - 合同跟进"
  
  - day_10:
      type: email
      template: "deadline_reminder"
      subject: "定价有效至 {deadline}"
      condition: not_responded
  
  - day_14:
      type: alert
      notify: sales_manager
      message: "交易卡在合同阶段"
```

---

## 集成方案

### 方案 1：Calendly → HubSpot

```yaml
trigger: calendly.booking_created

actions:
  1. 搜索潜在客户:
      hubspot.search: email == calendly.invitee_email
  
  2. 创建或更新:
      if: contact_exists
        hubspot.update_contact:
          last_meeting_booked: calendly.start_time
      else:
        hubspot.create_contact:
          email: calendly.invitee_email
          firstname: calendly.invitee_name
          lifecycle_stage: "salesqualifiedlead"
  
  3. 创建会议:
      hubspot.create_engagement:
        type: MEETING
        scheduled_time: calendly.start_time
        title: calendly.event_name
  
  4. 通知:
      slack.send:
        channel: "#sales"
        message: "会议已安排: {name} at {time}"
```

### 方案 2：LinkedIn → HubSpot

```yaml
trigger: linkedin.connection_accepted

actions:
  1. 丰富:
      linkedin.get_profile: connection_id
  
  2. 创建潜在客户:
      hubspot.create:
        email: linkedin.email
        firstname: linkedin.first_name
        lastname: linkedin.last_name
        jobtitle: linkedin.title
        company: linkedin.company
        linkedin_url: linkedin.profile_url
        lead_source: "LinkedIn"
  
  3. 添加到流程:
      if: title contains ["CEO", "CTO", "VP"]
      sequence: "LinkedIn C级拓展"
```

---

## 报告模板

### 每周销售报告

```markdown
# 销售管道报告 - 第 {week_number} 周

## 管道摘要
| 阶段 | 交易 | 金额 | 变化 |
|------|------|------|------|
| 新建 | 15 | $150K | +5 |
| 合格 | 8 | $120K | +2 |
| 提案 | 5 | $85K | -1 |
| 谈判 | 3 | $45K | +1 |
| **总管道** | **31** | **$400K** | **+7** |

## 本周活动
- 新增潜在客户: 45
- 召开会议: 12
- 发送提案: 4
- 关闭交易: 2 ($35K)

## 团队表现
| 代表 | 会议 | 提案 | 关闭 |
|------|------|------|------|
| Alice | 5 | 2 | 1 |
| Bob | 4 | 1 | 1 |
| Carol | 3 | 1 | 0 |

## 预测
- 承诺: $45K (3笔交易)
- 最佳情况: $85K (5笔交易)
- 管道: $400K (31笔交易)

## 需要采取的行动
- [ ] 跟进3笔停滞交易 (>14天无活动)
- [ ] 安排演示给企业潜在客户X
- [ ] 发送修订提案给公司Y
```

---

## 最佳实践

### 数据卫生

```yaml
data_hygiene_rules:
  - 去重: 每周
    方法: 邮箱匹配 + 公司模糊匹配
  
  - 验证邮箱: 创建时
    动作: 删除无效
  
  - 丰富缺失: 每日
    字段: [公司, 职位, linkedin]
  
  - 归档陈旧: 每月
    标准: 无活动 > 180天
    动作: 移至归档
```

### 安全

```yaml
security_practices:
  - api_keys: 每季度轮换
  - 访问控制: 基于角色
  - 审计日志: 所有变更
  - 敏感信息处理: 休息时加密
  - gdpr合规: 同意跟踪
```

---

*CRM自动化技能 - Claude 办公技能的一部分*
