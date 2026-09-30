---
name: sheets-automation
description: Google Sheets 自动化工作流 - 数据同步、任务管理、报告仪表板和多平台集成
---

# Google Sheets 自动化

自动化 Google Sheets 工作流，用于数据同步、任务管理、报告仪表板和多平台集成。基于 n8n 的 7,800 多个工作流模板。

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
│ (CRM)       │   │ (支付)      │   │ Analytics   │
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
workflow: "每日业务指标同步"

schedule: "每天上午 6:00"

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
      spreadsheet: "业务仪表板"
      sheet: "每日指标"
      action: append_row
      data:
        - date: today
        - leads: "{hubspot.new_leads}"
        - deals: "{hubspot.deals_closed}"
        - mrr: "{stripe.mrr}"
        - sessions: "{ga.sessions}"
        
  5. update_charts:
      refresh: automatic (Sheets 内置)
      
  6. send_summary:
      slack:
        channel: "#daily-metrics"
        message: |
          📊 每日指标 - {date}
          
          💰 收入: ${mrr} MRR
          👥 新增线索: {leads}
          🎯 已成交交易: {deals}
          📈 网站会话量: {sessions}
```

---

### 2. 带提醒的任务管理

```yaml
workflow: "Sheets 任务追踪器"

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
        状态 != "完成" AND
        截止日期 <= TODAY() + 1
        
  2. categorize_urgency:
      过期: 截止日期 < TODAY()
      今天到期: 截止日期 == TODAY()
      明天到期: 截止日期 == TODAY() + 1
      
  3. send_reminders:
      for_each: task
      
      过期:
        slack_dm:
          to: "{assignee_slack_id}"
          message: |
            🚨 *过期*: {task_name}
            截止日期: {due_date} ({days_overdue} 天前)
            优先级: {priority}
            
      今天到期:
        slack_dm:
          to: "{assignee_slack_id}"
          message: |
            ⏰ *今天到期*: {task_name}
            优先级: {priority}
            
  4. daily_recap:
      schedule: "下午 6:00"
      slack_channel: "#团队"
      message: |
        📋 *每日任务回顾*
        
        ✅ 已完成: {completed_count}
        ⏳ 进行中: {in_progress_count}
        🚨 过期: {overdue_count}
        
        明天优先事项:
        {tomorrow_tasks}
```

---

### 3. 自动化报告生成

```yaml
workflow: "每周报告生成器"

schedule: "周五下午 5:00"

steps:
  1. collect_data:
      sheets:
        - "销售数据"
        - "营销指标"
        - "支持工单"
        
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
      template: "每周报告模板"
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
        to: 领导团队
        subject: "每周业务报告 - 第 {week_number} 周"
        attach: [report_doc, charts_pdf]
        
      slack:
        channel: "#leadership"
        message: "📊 每周报告已准备好: {doc_link}"
```

---

### 4. 库存/库存追踪器

```yaml
workflow: "库存警报系统"

trigger:
  type: sheets_change
  sheet: "库存"
  
sheet_structure:
  columns:
    - 产品
    - SKU
    - 当前库存
    - 再订购水平
    - 供应商
    - 提前期 (天)

steps:
  1. check_stock_levels:
      condition: Current Stock <= Reorder Level
      
  2. generate_alerts:
      for_each: low_stock_item
      actions:
        - update_cell:
            column: "状态"
            value: "需要再订购"
            format: red_background
            
        - slack_alert:
            channel: "#库存"
            message: |
              ⚠️ *低库存警报*
              
              产品: {product_name}
              SKU: {sku}
              当前: {current_stock}
              再订购水平: {reorder_level}
              供应商: {supplier}
              
        - email_supplier:
            if: auto_reorder == true
            template: "reorder_request"
            
  3. daily_summary:
      schedule: "上午 9:00"
      report:
        - total_skus: count
        - low_stock_items: count
        - out_of_stock: count
        - pending_orders: list
```

---

### 5. 表单响应 → CRM + Slack

```yaml
workflow: "Google 表单线索捕获"

trigger:
  type: google_forms
  form: "联系我们表单"
  
steps:
  1. capture_response:
      fields: [name, email, company, message, source]
      
  2. append_to_sheet:
      spreadsheet: "线索追踪器"
      data:
        - timestamp: NOW()
        - name: "{name}"
        - email: "{email}"
        - company: "{company}"
        - message: "{message}"
        - status: "新线索"
        
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
        channel: "#新线索"
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

## 表格模板

### 销售仪表板

```
┌────────────────────────────────────────────────────────────────┐
│                    销售仪表板 - {月份}                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ 收入    │  │ 交易    │  │ 平均交易│  │ 胜率    │          │
│  │ $125K   │  │ 23      │  │ $5,400  │  │ 34%     │          │
│  │ ▲ 15%   │  │ ▲ 8%    │  │ ▲ 12%   │  │ ▼ 2%   │          │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
│                                                                │
│  [收入趋势图 - 折线图]                                  │
│  [按阶段划分的管道图 - 漏斗图]                                  │
│  [销售代表排名 - 条形图]                                        │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│ 日期    │ 交易      │ 金额   │ 代表    │ 阶段    │ 概率     │
│ 1/30    │ Acme Corp │ $15,000 │ Alice  │ 提案 │ 60%      │
│ 1/29    │ Tech Inc  │ $8,500  │ Bob    │ 演示     │ 40%      │
│ ...     │ ...       │ ...     │ ...    │ ...      │ ...      │
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
│ 有机     │ $0       │ 300   │ $0     │ 2.1%   │ $52,000   │
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
=IF(C2<TODAY(), "过期", IF(C2=TODAY(), "今天到期", "即将到来"))

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

# 从其他表格 VLOOKUP
=VLOOKUP(A2, '参考数据'!$A:$C, 3, FALSE)

# 仪表板查询
=QUERY(Data!A:F, "SELECT A, SUM(C) WHERE B='已成交胜利' GROUP BY A")
```

---

## 输出示例

**请求**: "从 Google Sheets 设置自动化任务提醒"

**输出**:

```markdown
# 任务提醒系统设置

## 表格结构

创建一个名为 "任务" 的表格，包含以下列：

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 任务 | 指派人员 | 截止日期 | 优先级 | 状态 | Slack ID |
| 审查提案 | Alice | 2026-01-31 | 高 | 进行中 | U12345 |
| 更新文档 | Bob | 2026-02-01 | 中 | 待办 | U67890 |

## 自动化工作流

```yaml
触发: 每 15 分钟
操作:
  1. 检查 24 小时内到期的任务
  2. 向指派人员发送 Slack DM
  3. 下午 6 点发布每日摘要
```

## 示例提醒

**过期提醒**:
```
🚨 *过期*: 审查提案
截止日期: Jan 29 (1 天前)
优先级: 高

请更新状态或标记为完成。
```

**今天到期**:
```
⏰ *今天到期*: 更新文档
优先级: 中

你一定能做到！ 💪
```

**每日摘要 (下午 6 点)**:
```
📋 *每日任务摘要*

✅ 今天完成: 5
⏳ 进行中: 3
🚨 过期: 1

明天优先事项:
• 审查提案 (高) - Alice
• 客户会议准备 (高) - Bob
```

## 设置步骤

1. 创建 Google 表格并使用上述结构
2. 设置 n8n 工作流并使用计划触发器
3. 连接 Google Sheets 和 Slack 节点
4. 使用示例任务测试
5. 激活工作流

您需要完整的 n8n 工作流 JSON 吗？
```

---

*Sheets 自动化技能 - 隶属于 Claude 办公技能*
