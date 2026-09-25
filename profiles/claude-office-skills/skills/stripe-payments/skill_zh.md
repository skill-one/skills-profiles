# Stripe 支付

全面的技能，用于自动化 Stripe 支付处理和订阅管理。

## 核心工作流

### 1. 支付流程

```
STRIPE 支付流程:
┌─────────────────┐
│    客户     │
│  支付意图   │
└────────┬────────┘
         ▼
┌─────────────────┐
│    结账     │
│  - 卡片输入   │
│  - 验证   │
└────────┬────────┘
         ▼
┌─────────────────┐
│   处理     │
│  - 认证         │
│  - 捕获      │
└────────┬────────┘
         ▼
┌─────────────────┐
│   确认     │
│  - 收据      │
│  - Webhook      │
└─────────────────┘
```

### 2. Webhook 事件

```yaml
webhook_handlers:
  payment_intent.succeeded:
    actions:
      - fulfill_order
      - send_receipt
      - update_crm
      
  payment_intent.payment_failed:
    actions:
      - notify_customer
      - retry_payment
      - log_failure
      
  customer.subscription.created:
    actions:
      - provision_access
      - send_welcome_email
      - update_metrics
      
  customer.subscription.deleted:
    actions:
      - revoke_access
      - send_offboarding_email
      - trigger_retention_flow
      
  invoice.payment_failed:
    actions:
      - send_dunning_email
      - update_subscription_status
      - create_support_ticket
```

## 订阅管理

### 计划配置

```yaml
subscription_plans:
  - name: Starter
    id: plan_starter
    price: 29
    currency: usd
    interval: month
    features:
      - "5 用户"
      - "10GB 存储空间"
      - "邮件支持"
    metadata:
      tier: 1
      
  - name: Growth
    id: plan_growth
    price: 79
    currency: usd
    interval: month
    features:
      - "25 用户"
      - "100GB 存储空间"
      - "优先支持"
    metadata:
      tier: 2
      
  - name: Enterprise
    id: plan_enterprise
    price: custom
    interval: month
    features:
      - "无限用户"
      - "无限存储空间"
      - "24/7 支持"
      - "定制集成"
    metadata:
      tier: 3
```

### 订阅生命周期

```yaml
subscription_automation:
  on_create:
    - provision_service
    - send_welcome_email
    - create_customer_record
    - schedule_onboarding_call
    
  on_upgrade:
    - adjust_limits
    - prorate_billing
    - send_upgrade_confirmation
    - unlock_features
    
  on_downgrade:
    - schedule_limit_reduction
    - send_downgrade_notice
    - offer_retention_discount
    
  on_cancel:
    - schedule_access_revocation
    - send_exit_survey
    - trigger_win_back_campaign
    
  on_renewal:
    - send_renewal_receipt
    - update_usage_quotas
    - check_plan_eligibility
```

## 发票管理

### 发票自动化

```yaml
invoice_settings:
  defaults:
    auto_advance: true
    collection_method: charge_automatically
    days_until_due: 30
    
  templates:
    header:
      company_name: "{{company}}"
      logo: "{{logo_url}}"
      
    footer:
      payment_terms: "Net 30"
      thank_you: "感谢您的业务！"
      
  automation:
    - event: invoice.created
      actions:
        - add_line_items
        - apply_discounts
        - calculate_tax
        
    - event: invoice.finalized
      actions:
        - send_to_customer
        - log_to_accounting
        
    - event: invoice.paid
      actions:
        - send_receipt
        - update_revenue
```

### 逾期管理

```yaml
dunning_sequence:
  - day: 0
    event: payment_failed
    actions:
      - retry_payment
      - email_template: payment_failed_1
      
  - day: 3
    actions:
      - retry_payment
      - email_template: payment_failed_2
      - sms_reminder
      
  - day: 7
    actions:
      - retry_payment
      - email_template: payment_failed_3
      - mark_at_risk
      
  - day: 14
    actions:
      - final_retry
      - email_template: final_notice
      - pause_subscription
      
  - day: 30
    actions:
      - cancel_subscription
      - email_template: cancellation
      - revoke_access
```

## 结账集成

### 结账会话

```javascript
// 创建结账会话
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  payment_method_types: ['card'],
  line_items: [{
    price: 'price_xxx',
    quantity: 1,
  }],
  success_url: 'https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://example.com/cancel',
  customer_email: 'customer@example.com',
  subscription_data: {
    trial_period_days: 14,
    metadata: {
      plan_tier: 'growth'
    }
  },
  allow_promotion_codes: true,
});
```

### 支付元素

```javascript
// 创建支付意图
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
  customer: 'cus_xxx',
  payment_method_types: ['card'],
  metadata: {
    order_id: '12345'
  }
});

// 确认支付
const result = await stripe.confirmCardPayment(
  paymentIntent.client_secret,
  {
    payment_method: {
      card: cardElement,
      billing_details: {
        name: 'John Doe'
      }
    }
  }
);
```

## 收入分析

### 仪表盘指标

```
STRIPE 收入仪表盘
═══════════════════════════════════════

MRR:          $125,450 (+8.5%)
ARR:          $1,505,400
新 MRR:      $12,340
流失 MRR:    $4,120
净 MRR:      +$8,220

订阅分解:
活跃:       892
试用:     156
逾期:     23
已取消:    45 (本月)

按计划:
Starter    ████████░░░░░░░░ 45%  │ $28,500
Growth     ██████████░░░░░░ 38%  │ $47,600
Enterprise ██████░░░░░░░░░░ 17%  │ $49,350

流失分析:
月度流失率:  4.2%
MRR 流失:    $4,120
原因:
- 价格             ████████░░░░ 35%
- 竞争对手        ██████░░░░░░ 25%
- 不再需要        ████░░░░░░░░ 20%
- 支持问题        ███░░░░░░░░░ 12%
- 其他             ██░░░░░░░░░░ 8%
```

### 群组分析

```yaml
cohort_metrics:
  - cohort: "2024-01"
    customers: 150
    month_1_retention: 95%
    month_3_retention: 82%
    month_6_retention: 71%
    ltv_estimate: $890
    
  - cohort: "2024-02"
    customers: 180
    month_1_retention: 93%
    month_3_retention: 79%
    ltv_estimate: $820
```

## 防欺诈

### 风险规则

```yaml
radar_rules:
  - name: block_high_risk
    condition: "risk_level = 'highest'"
    action: block
    
  - name: review_elevated_risk
    condition: "risk_level = 'elevated'"
    action: review
    
  - name: block_disposable_email
    condition: "email_domain in @disposable_domains"
    action: block
    
  - name: velocity_check
    condition: "card_country != ip_country"
    action: review
    
  - name: amount_threshold
    condition: "amount > 100000"  # $1000
    action: review
```

## 客户门户

### 门户配置

```yaml
customer_portal:
  features:
    subscription_update:
      enabled: true
      products:
        - product_starter
        - product_growth
        - product_enterprise
      proration_behavior: create_prorations
      
    subscription_cancel:
      enabled: true
      mode: at_period_end
      cancellation_reason:
        enabled: true
        options:
          - "太贵"
          - "缺少功能"
          - "转向竞争对手"
          - "不再需要"
          - "其他"
          
    payment_method_update:
      enabled: true
      
    invoice_history:
      enabled: true
      
  branding:
    colors:
      primary: "#5469d4"
    icon: "{{company_icon}}"
```

## 报告自动化

### 定时报告

```yaml
reports:
  - name: daily_revenue
    schedule: "0 9 * * *"
    metrics:
      - gross_volume
      - net_volume
      - new_customers
      - failed_payments
    destination: slack_finance
    
  - name: weekly_mrr
    schedule: "0 9 * * 1"
    metrics:
      - mrr
      - arr
      - churn_rate
      - expansion_revenue
    destination: email_leadership
    
  - name: monthly_reconciliation
    schedule: "0 9 1 * *"
    metrics:
      - total_revenue
      - fees
      - refunds
      - payouts
    destination: accounting_system
```

## API 示例

### 常见操作

```javascript
// 创建客户
const customer = await stripe.customers.create({
  email: 'customer@example.com',
  name: 'John Doe',
  metadata: {
    user_id: '12345'
  }
});

// 创建订阅
const subscription = await stripe.subscriptions.create({
  customer: customer.id,
  items: [{ price: 'price_xxx' }],
  trial_period_days: 14,
  payment_behavior: 'default_incomplete',
  expand: ['latest_invoice.payment_intent']
});

// 更新订阅
await stripe.subscriptions.update(subscription.id, {
  items: [{
    id: subscription.items.data[0].id,
    price: 'price_new_xxx'
  }],
  proration_behavior: 'create_prorations'
});

// 发出退款
const refund = await stripe.refunds.create({
  payment_intent: 'pi_xxx',
  amount: 1000  // 部分退款
});
```

## 最佳实践

1. **使用 Webhooks**: 不要仅依赖重定向
2. **幂等性键**: 防止重复收费
3. **错误处理**: 优雅的失败恢复
4. **PCI 合规**: 使用 Stripe Elements
5. **测试模式**: 生产前验证
6. **监控争议**: 及时响应
7. **逾期策略**: 恢复失败支付
8. **收入确认**: 正确跟踪 MRR
