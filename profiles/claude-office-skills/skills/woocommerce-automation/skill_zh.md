# WooCommerce 自动化

全面的技能，用于自动化 WooCommerce 店铺运营和工作流程。

## 核心工作流程

### 1. 订单处理流程

```
订单流程：
┌─────────────────┐
│  新订单      │
│  已接收       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  验证       │
│  - 支付      │
│  - 库存      │
│  - 欺诈检查  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  处理        │
│  - 确认      │
│  - 预留库存  │
│  - 通知       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  履行        │
│  - 拣货打包  │
│  - 发货       │
│  - 追踪        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  完成        │
│  - 交付      │
│  - 跟进    │
└─────────────────┘
```

### 2. 订单状态自动化

```yaml
order_automations:
  - trigger: order_placed
    conditions:
      payment_status: completed
    actions:
      - set_status: processing
      - send_email: order_confirmation
      - create_fulfillment_task
      - update_inventory
      
  - trigger: order_shipped
    actions:
      - set_status: shipped
      - send_email: shipping_notification
      - add_tracking_note
      
  - trigger: order_delivered
    actions:
      - set_status: completed
      - schedule_review_request:
          delay: 7_days
      - update_customer_stats
      
  - trigger: payment_failed
    actions:
      - set_status: on-hold
      - send_email: payment_failed
      - create_followup_task
```

## 产品管理

### 库存同步

```yaml
inventory_sync:
  sources:
    - name: 仓库A
      type: api
      sync_frequency: "*/15 * * * *"  # 每15分钟
      
    - name: 供应商数据源
      type: ftp
      file_pattern: "inventory_*.csv"
      sync_frequency: "0 */4 * * *"  # 每4小时
      
  rules:
    - condition: quantity <= low_stock_threshold
      actions:
        - set_stock_status: "onbackorder"
        - send_alert: low_stock
        - create_purchase_order
        
    - condition: quantity == 0
      actions:
        - set_stock_status: "outofstock"
        - hide_from_catalog: false
        - show_back_in_stock_form: true
```

### 产品数据结构

```yaml
product_template:
  name: "{{product_name}}"
  type: "simple"  # simple, variable, grouped, external
  
  general:
    regular_price: "{{price}}"
    sale_price: "{{sale_price}}"
    sku: "{{sku}}"
    
  inventory:
    manage_stock: true
    stock_quantity: "{{quantity}}"
    backorders: "notify"
    low_stock_threshold: 5
    
  shipping:
    weight: "{{weight}}"
    dimensions:
      length: "{{length}}"
      width: "{{width}}"
      height: "{{height}}"
    shipping_class: "{{shipping_class}}"
    
  attributes:
    - name: "颜色"
      values: ["红色", "蓝色", "绿色"]
      visible: true
      variation: true
    - name: "尺寸"
      values: ["S", "M", "L", "XL"]
      visible: true
      variation: true
      
  categories: ["{{category}}"]
  tags: ["{{tags}}"]
  images:
    - src: "{{image_url}}"
      alt: "{{image_alt}}"
```

### 批量产品更新

```yaml
bulk_operations:
  - name: 价格上调
    filter:
      category: "电子产品"
      stock_status: "instock"
    action:
      update_price:
        type: percentage
        value: 10
        
  - name: 促销活动
    filter:
      tag: "夏季促销"
    action:
      set_sale_price:
        discount: 25
        schedule:
          start: "2024-06-01"
          end: "2024-06-30"
          
  - name: 更新物流
    filter:
      weight_greater_than: 5
    action:
      set_shipping_class: "重型商品"
```

## 客户管理

### 客户细分

```yaml
customer_segments:
  - name: 高级客户
    criteria:
      total_spent: ">= 1000"
      order_count: ">= 5"
    actions:
      - assign_role: "vip_customer"
      - apply_discount: 15
      - send_vip_welcome
      
  - name: 风险客户
    criteria:
      last_order: "> 90 days"
      total_spent: ">= 200"
    actions:
      - add_tag: "at_risk"
      - send_win_back_campaign
      
  - name: 首次购买者
    criteria:
      order_count: 1
      registered: "< 30 days"
    actions:
      - send_onboarding_series
      - offer_second_purchase_discount
```

### 客户生命周期邮件

```yaml
email_automation:
  welcome_series:
    - delay: 0
      template: welcome_email
      subject: "欢迎来到 {{store_name}}!"
      
    - delay: 3_days
      template: product_highlights
      subject: "您会喜欢的畅销产品"
      
    - delay: 7_days
      template: first_purchase_offer
      subject: "特别优惠：首次订单10%折扣"
      
  购买后:
    - delay: 0
      trigger: order_completed
      template: order_confirmation
      
    - delay: 3_days
      template: shipping_update
      condition: order_status == "shipped"
      
    - delay: 14_days
      template: review_request
      condition: order_status == "completed"
      
  恢复客户:
    - delay: 30_days
      condition: no_order_since
      template: miss_you_email
      subject: "我们想念您！这里15%折扣"
      
    - delay: 60_days
      condition: no_order_since
      template: last_chance
      subject: "最后机会：仅限您20%折扣"
```

## 营销自动化

### 优惠券管理

```yaml
coupon_automations:
  - name: 生日优惠券
    trigger: customer_birthday
    coupon:
      type: percent
      amount: 20
      individual_use: true
      usage_limit: 1
      expiry: 30_days
    notification:
      email_template: birthday_coupon
      
  - name: 购物车放弃优惠券
    trigger: cart_abandoned
    delay: 24_hours
    coupon:
      type: percent
      amount: 10
      minimum_amount: 50
      expiry: 7_days
    notification:
      email_template: abandoned_cart
      
  - name: 忠诚度奖励
    trigger: order_count_reached
    threshold: 10
    coupon:
      type: fixed_cart
      amount: 25
      individual_use: true
```

### 购物车恢复

```yaml
cart_recovery:
  triggers:
    - cart_abandoned_minutes: 60
    - cart_value_minimum: 30
    
  sequence:
    - delay: 1_hour
      template: cart_reminder_1
      subject: "您遗漏了些东西..."
      include_cart_items: true
      
    - delay: 24_hours
      template: cart_reminder_2
      subject: "您的购物车在等待"
      include_discount: false
      
    - delay: 72_hours
      template: cart_reminder_3
      subject: "最后机会+10%折扣"
      include_discount: true
      discount_code: "COMEBACK10"
```

## 分析与报告

### 销售仪表盘

```
销售概览 - 过去30天
═══════════════════════════════════════

收入:      $45,230 (+12.5%)
订单:       892 (+8.3%)
平均订单价值: $50.70 (+3.9%)
转化率:   3.2% (+0.4%)

畅销产品:
┌────────────────────────┬────────┬─────────┐
│ 产品                │ 销售   │ 收入   │
├────────────────────────┼────────┼─────────┤
│ 高级小工具         │ 245    │ $12,250 │
│ 标准套餐       │ 189    │ $7,560  │
│ 豪华套装          │ 156    │ $9,360  │
└────────────────────────┴────────┴─────────┘

按渠道销售:
直接      ██████████████░░ 65%
自然      ████████░░░░░░░░ 22%
付费      ████░░░░░░░░░░░░ 10%
推荐      █░░░░░░░░░░░░░░░ 3%
```

### 库存报告

```yaml
inventory_report:
  metrics:
    - total_products: 1,234
    - in_stock: 1,089
    - out_of_stock: 98
    - low_stock: 47
    
  alerts:
    - type: out_of_stock
      products: 98
      action: reorder_required
      
    - type: low_stock
      products: 47
      threshold_days: 14
      
    - type: overstock
      products: 23
      recommendation: run_promotion
```

## API 集成示例

### WooCommerce REST API

```javascript
// 创建订单
const order = {
  payment_method: "bacs",
  payment_method_title: "直接银行转账",
  set_paid: true,
  billing: {
    first_name: "John",
    last_name: "Doe",
    email: "john@example.com",
    address_1: "123 Main St",
    city: "San Francisco",
    state: "CA",
    postcode: "94103",
    country: "US"
  },
  line_items: [
    {
      product_id: 93,
      quantity: 2
    }
  ],
  shipping_lines: [
    {
      method_id: "flat_rate",
      method_title: "Flat Rate",
      total: "10.00"
    }
  ]
};

// 更新产品库存
const updateStock = {
  stock_quantity: 100,
  manage_stock: true
};

// 创建优惠券
const coupon = {
  code: "SAVE20",
  discount_type: "percent",
  amount: "20",
  individual_use: true,
  exclude_sale_items: true,
  minimum_amount: "50.00"
};
```

## 最佳实践

1. **自动化状态更新**: 让客户保持知情
2. **实时同步库存**: 防止超卖
3. **细分客户**: 个性化营销
4. **恢复放弃的购物车**: 捕获丢失的收入
5. **监控库存水平**: 设置低库存警报
6. **优化邮件发送时间**: 测试发送时间
7. **追踪转化率**: 衡量营销ROI
8. **定期备份**: 保护订单数据
