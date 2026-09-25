# Google Sheets 自动化

自动化 Google Sheets 工作流程，用于数据同步、任务管理、报告仪表板和多平台集成。基于 n8n 的 7,800 多个工作流模板。

## 概述

本技能涵盖：
- 从多个来源自动同步数据
- 使用 Slack 提醒进行任务管理
- 实时报告仪表板
- CRM/营销数据聚合
- 定时报告生成

---

## 核心工作流

### 1. 多源数据聚合

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ HubSpot     │   │ Stripe      │   │ Google      │
│ (CRM)       │   │ (Payments)  │   │ Analytics   │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Google Sheets    │
              │ (主仪表板)       │
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Slack/Email      │
              │ (每日报告)       │
              └──────────────────┘
```

**n8n 配置**：
```yaml
workflow: "Daily Business Metrics Sync"

schedule: "6:00 AM daily"

steps:
  1. fetch_crm_data:
      source: hubspot
      data:
        - new_leads_today
        - deals_closed
        - pipeline_value
        
  2. fetch_revenue_data:
      source: stripe
      data:
        - mrr
        - new_subscriptions
        - churn
        
  3. fetch_traffic_data:
      source: google_analytics
      data:
        - sessions
        - conversions
        - bounce_rate
        
  4. update_sheets:
      spreadsheet: "Business Dashboard"
      sheet: "Daily Metrics"
      action: append_row
      data:
        - date: today
        - leads: "{hubspot.new_leads}"
        - deals: "{hubspot.deals_closed}"
        - mrr: "{stripe.mrr}"
        - sessions: "{ga.sessions}"
        
  5. update_charts:
      refresh: automatic (Sheets built-in)
      
  6. send_summary:
      slack:
        channel: "#daily-metrics"
        message: |
          📊 Daily Metrics - {date}
          
          💰 Revenue: ${mrr} MRR
          👥 New Leads: {leads}
          🎯 Deals Closed: {deals}
          📈 Website Sessions: {sessions}
```

---

### 2. 带提醒的任务管理

```yaml
workflow: "Sheets Task Tracker"

trigger:
  type: schedule
  frequency: every_15_minutes

sheet_structure:
  columns:
    - A: 任务
    - B: 指派人员
    - C: 截止日期
    - D: 优先级 (高/中/低)
    - E: 状态 (待办/进行中/完成)
    - F: Slack ID

steps:
  1. read_tasks:
      filter: |
        Status != "Done" AND
        Due Date <= TODAY() + 1
        
  2. categorize_urgency:
      overdue: Due Date < TODAY()
      due_today: Due Date == TODAY()
      due_tomorrow: Due Date == TODAY() + 1
      
  3. send_reminders:
      for_each: task
      
      overdue:
        slack_dm:
          to: "{assignee_slack_id}"
          message: |
            🚨 *已逾期*: {task_name}
            截止: {due_date} ({days_overdue} 天前)
            优先级: {priority}
            
      due_today:
        slack_dm:
          to: "{assignee_slack_id}"
          message: |
            ⏰ *今日到期*: {task_name}
            优先级: {priority}
            
  4. daily_recap:
      schedule: "6:00 PM"
      slack_channel: "#team"
      message: |
        📋 *每日任务回顾*
        
        ✅ 已完成: {completed_count}
        ⏳ 进行中: {in_progress_count}
        🚨 已逾期: {overdue_count}
        
        明日优先事项:
        {tomorrow_tasks}
```

---

### 3. 自动报告生成

```yaml
workflow: "Weekly Report Generator"

schedule: "Friday 5:00 PM"

steps:
  1. collect_data:
      sheets:
        - "Sales Data"
        - "Marketing Metrics"
        - "Support Tickets"
        
  2. calculate_metrics:
      sales:
        - total_revenue: SUM(revenue_column)
        - deals_closed: COUNT(won_deals)
        - avg_deal_size: AVG(deal_value)
        - win_rate: won / (won + lost)
        
      marketing:
        - leads_generated: COUNT(new_leads)
        - cost_per_lead: spend / leads
        - conversion_rate: conversions / visitors
        
      support:
        - tickets_resolved: COUNT(resolved)
        - avg_response_time: AVG(first_response)
        - csat_score: AVG(satisfaction)
        
  3. generate_report:
      format: google_doc
      template: "Weekly Report Template"
      sections:
        - executive_summary
        - sales_performance
        - marketing_metrics
        - customer_support
        - next_week_priorities
        
  4. create_charts:
      google_sheets:
        - revenue_trend: line_chart
        - deal_funnel: bar_chart
        - lead_sources: pie_chart
        
  5. distribute:
      email:
        to: leadership_team
        subject: "Weekly Business Report - Week {week_number}"
        attach: [report_doc, charts_pdf]
        
      slack:
        channel: "#leadership"
        message: "📊 周报已准备好: {doc_link}"
```

---

### 4. 库存/股票追踪器

```yaml
workflow: "Inventory Alert System"

trigger:
  type: sheets_change
  sheet: "Inventory"
  
sheet_structure:
  columns:
    - 产品
    - SKU
    - 当前库存
    - 重新订购水平
    - 供应商
    - 提前期 (天)

steps:
  1. check_stock_levels:
      condition: Current Stock <= Reorder Level
      
  2. generate_alerts:
      for_each: low_stock_item
      actions:
        - update_cell:
            column: "Status"
            value: "需要重新订购"
            format: red_background
            
        - slack_alert:
            channel: "#inventory"
            message: |
              ⚠️ *低库存警报*
              
              产品: {product_name}
              SKU: {sku}
              当前: {current_stock}
              重新订购水平: {reorder_level}
              供应商: {supplier}
              
        - email_supplier:
            if: auto_reorder == true
            template: "reorder_request"
            
  3. daily_summary:
      schedule: "9:00 AM"
      report:
        - total_skus: count
        - low_stock_items: count
        - out_of_stock: count
        - pending_orders: list
```

---

### 5. 表单响应 → CRM + Slack

```yaml
workflow: "Google Form Lead Capture"

trigger:
  type: google_forms
  form: "Contact Us Form"
  
steps:
  1. capture_response:
      fields: [name, email, company, message, source]
      
  2. append_to_sheet:
      spreadsheet: "Lead Tracker"
      data:
        - timestamp: NOW()
        - name: "{name}"
        - email: "{email}"
        - company: "{company}"
        - message: "{message}"
        - status: "新"
        
  3. enrich_lead:
      clearbit:
        lookup_by: email
        append: [company_size, industry, linkedin]
        
  4. create_in_crm:
      hubspot:
        object: contact
        properties:
          email: "{email}"
          firstname: "{name}"
          company: "{company}"
          lead_source: "网站表单"
          
  5. notify_sales:
      slack:
        channel: "#new-leads"
        message: |
          🎉 *新线索!*
          
          👤 {name}
          🏢 {company} ({company_size} 员工)
          📧 {email}
          💬 "{message}"
          
          [在 HubSpot 中查看]({hubspot_link})
          
  6. auto_respond:
      email:
        to: "{email}"
        template: "感谢联系我们"
```

---

## 表单模板

### 销售仪表板

```
┌────────────────────────────────────────────────────────────────┐
│                    销售仪表板 - {月份}                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ 收入    │  │ 合同    │  │ 平均合同│  │ 赢率    │          │
│  │ $125K   │  │ 23      │  │ $5,400  │  │ 34%     │          │
│  │ ▲ 15%   │  │ ▲ 8%    │  │ ▲ 12%   │  │ ▼ 2%   │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│                                                                │
│  [收入趋势图 - 折线图]                                  │
│  [按阶段划分的管道图 - 漏斗]                                  │
│  [销售代表排名 - 条形图]                                        │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│ 日期    │ 合同      │ 金额   │ 代表    │ 阶段    │ 概率     │
│ 1/30    │ Acme Corp │ $15,000 │ Alice  │ 提案 │ 60%      │
│ 1/29    │ Tech Inc  │ $8,500  │ Bob    │ 演示 │ 40%      │
│ ...     │ ...       │ ...     │ ...    │ ...  │ ...      │
└────────────────────────────────────────────────────────────────┘
```

### 营销追踪器

```
┌────────────────────────────────────────────────────────────────┐
│                  营销指标                            │
├────────────────────────────────────────────────────────────────┤
│ 渠道     │ 支出    │ 线索 │ 单线索成本    │ 转化率 │ 收入   │
├─────────────┼──────────┼───────┼────────┼────────┼───────────┤
│ Google Ads  │ $5,000   │ 150   │ $33    │ 3.2%   │ $45,000   │
│ Facebook    │ $3,000   │ 200   │ $15    │ 1.8%   │ $28,000   │
│ LinkedIn    │ $2,500   │ 50    │ $50    │ 5.5%   │ $35,000   │
│ 有机      │ $0       │ 300   │ $0     │ 2.1%   │ $52,000   │
├─────────────┼──────────┼───────┼────────┼────────┼───────────┤
│ 总计       │ $10,500  │ 700   │ $15    │ 2.8%   │ $160,000  │
└────────────────────────────────────────────────────────────────┘

ROAS: 15.2x
最佳渠道: LinkedIn (转化率最高)
行动: 增加 LinkedIn 预算 20%
```

---

## 公式参考

### 常见自动化公式

```
# 基于日期自动状态
=IF(C2<TODAY(), "已逾期", IF(C2=TODAY(), "今日到期", "即将到期"))

# 截止日期剩余天数
=DATEDIF(TODAY(), C2, "D")

# 基于条件自动分配
=IFS(B2="企业", "Alice", B2="中市场", "Bob", TRUE, "Carol")

# 计算转化率
=IFERROR(D2/C2, 0)

# 累计总和
=SUMIF($A$2:A2, "<="&A2, $B$2:B2)

# 条件格式触发
=AND($E2="高", $F2<TODAY())

# 从其他表单 VLOOKUP
=VLOOKUP(A2, '参考数据'!$A:$C, 3, FALSE)

# 仪表板查询
=QUERY(Data!A:F, "SELECT A, SUM(C) WHERE B='已关闭赢利' GROUP BY A")
```

---

## 输出示例

**请求**: "从 Google Sheets 设置自动任务提醒"

**输出**:

```markdown
# 任务提醒系统设置

## 表单结构

创建一个名为 "Tasks" 的表单，包含以下列：

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 任务 | 指派人员 | 截止日期 | 优先级 | 状态 | Slack ID |
| 审查提案 | Alice | 2026-01-31 | 高 | 进行中 | U12345 |
| 更新文档 | Bob | 2026-02-01 | 中 | 待办 | U67890 |

## 自动化工作流

```yaml
trigger: 每 15 分钟
actions:
  1. 检查 24 小时内到期的任务
  2. 向指派人员发送 Slack DM
  3. 在 6pm 发布每日总结
```

## 示例提醒

**已逾期提醒**:
```
🚨 *已逾期*: 审查提案
截止: Jan 29 (1 天前)
优先级: 高

请更新状态或标记为完成。
```

**今日到期**:
```
⏰ *今日到期*: 更新文档
优先级: 中

你一定能做到！ 💪
```

**每日总结 (6pm)**:
```
📋 *每日任务总结*

✅ 今日完成: 5
⏳ 进行中: 3
🚨 已逾期: 1

明日优先事项:
• 审查提案 (高) - Alice
• 客户会议准备 (高) - Bob
```

## 设置步骤

1. 创建具有上述结构的 Google 表单
2. 设置带有计划触发器的 n8n 工作流
3. 连接 Google Sheets 和 Slack 节点
4. 使用示例任务进行测试
5. 激活工作流

您需要完整的 n8n 工作流 JSON 吗？
```

---

*Sheets Automation Skill - 隶属于 Claude Office Skills*
