---
name: Mailchimp Automation
description: 自动 Mailchimp 邮件营销活动、受众管理、自动化和数据分析
---

# Mailchimp 自动化

全面的技能，用于自动化 Mailchimp 电子邮件营销和受众管理。

## 核心工作流

### 1. 营销活动流程

```
电子邮件活动流程：
┌─────────────────┐
│  规划活动      │
│  - 目标        │
│  - 受众        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  创建内容      │
│  - 设计        │
│  - 文案        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  配置          │
│  - 标题        │
│  - 预览        │
│  - 设置        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  测试与审核    │
│  - A/B 测试    │
│  - 预览        │
└────────┬────────┘
         ▼
┌─────────────────┐
│  安排/发送    │
│  - 时间        │
│  - 发送        │
└────────┬────────┘
         ▼
┌─────────────────┐
│    分析        │
│  - 打开/点击    │
│  - 收入        │
└─────────────────┘
```

### 2. 营销活动配置

```yaml
campaign_config:
  type: regular  # regular, automated, plaintext, ab_test
  
  recipients:
    list_id: "abc123"
    segment_opts:
      saved_segment_id: "seg123"
      # 或动态条件
      
  settings:
    subject_line: "{{subject}}"
    preview_text: "{{preview}}"
    from_name: "{{company}}"
    reply_to: "{{email}}"
    
  tracking:
    opens: true
    clicks: true
    ecommerce: true
    google_analytics: "campaign_name"
    
  content_type: "template"
  template_id: "template_123"
```

## 受众管理

### 分段规则

```yaml
segments:
  - name: active_subscribers
    conditions:
      - field: last_opened
        op: greater_than
        value: "30_days_ago"
        
  - name: high_value_customers
    conditions:
      - field: ecomm_total_spent
        op: greater_than
        value: 500
      - field: ecomm_orders
        op: greater_than
        value: 3
        
  - name: at_risk
    conditions:
      - field: last_opened
        op: greater_than
        value: "90_days_ago"
      - field: email_campaigns_opened
        op: greater_than
        value: 5
        
  - name: new_subscribers
    conditions:
      - field: timestamp_signup
        op: greater_than
        value: "30_days_ago"
```

### 受众标签

```yaml
tagging_automation:
  - trigger: form_submit
    form: "newsletter_signup"
    actions:
      - add_tag: "newsletter"
      - add_tag: "{{form.interest}}"
      
  - trigger: purchase
    actions:
      - add_tag: "customer"
      - add_tag: "purchased_{{product_category}}"
      
  - trigger: link_clicked
    url_contains: "/pricing"
    actions:
      - add_tag: "interested_in_pricing"
```

## 电子邮件自动化

### 欢迎系列

```yaml
welcome_automation:
  name: "Welcome Series"
  trigger:
    type: signup
    list_id: "main_list"
    
  emails:
    - delay: immediate
      subject: "Welcome to {{company}}! 🎉"
      template: welcome_email_1
      
    - delay: 2_days
      subject: "Here's how to get started"
      template: welcome_email_2
      
    - delay: 5_days
      subject: "{{first_name}}, your exclusive tips"
      template: welcome_email_3
      
    - delay: 10_days
      subject: "Ready to take the next step?"
      template: welcome_email_4
      content: offer_cta
```

### 购物车遗弃

```yaml
abandoned_cart:
  name: "Cart Recovery"
  trigger:
    type: ecommerce
    event: cart_abandoned
    delay: 1_hour
    
  emails:
    - delay: 1_hour
      subject: "You left something behind..."
      template: cart_reminder_1
      show_cart_items: true
      
    - delay: 24_hours
      condition: cart_not_recovered
      subject: "Your cart is waiting"
      template: cart_reminder_2
      include_discount: false
      
    - delay: 72_hours
      condition: cart_not_recovered
      subject: "Last chance: 10% off your cart"
      template: cart_reminder_3
      include_discount: true
      discount_code: "COMEBACK10"
```

### 购买后

```yaml
post_purchase:
  name: "Post-Purchase Nurture"
  trigger:
    type: ecommerce
    event: purchase
    
  emails:
    - delay: immediate
      type: transactional
      subject: "Order confirmed #{{order_id}}"
      template: order_confirmation
      
    - delay: 3_days
      type: transactional
      subject: "Your order has shipped"
      template: shipping_notification
      condition: order_shipped
      
    - delay: 7_days
      subject: "How's your {{product_name}}?"
      template: review_request
      condition: order_delivered
      
    - delay: 30_days
      subject: "You might also like..."
      template: cross_sell
      content: recommended_products
```

## A/B 测试

### 测试配置

```yaml
ab_test:
  type: subject_line  # or content, send_time, from_name
  
  variants:
    a:
      subject: "Don't miss out: Sale ends tonight"
    b:
      subject: "⚡ Flash sale: 24 hours only"
      
  test_settings:
    split_percentage: 20  # 测试 20%，胜者占 80%
    winning_metric: open_rate  # or click_rate, revenue
    wait_time: 4_hours
    
  auto_winner:
    enabled: true
    send_remaining: true
```

### 多变量测试

```yaml
multivariate_test:
  factors:
    subject_line:
      - "New arrivals just dropped"
      - "You'll love what's new"
    preview_text:
      - "Shop the latest styles"
      - "See what's trending now"
    send_time:
      - "09:00"
      - "14:00"
      
  combinations: 8
  sample_size: 25%
  duration: 24_hours
```

## 电子邮件模板

### 新闻简报模板

```yaml
newsletter_template:
  layout: multi_column
  
  sections:
    - type: header
      logo: "{{logo_url}}"
      navigation: true
      
    - type: hero
      image: "{{hero_image}}"
      headline: "{{headline}}"
      subheadline: "{{subheadline}}"
      cta:
        text: "{{cta_text}}"
        url: "{{cta_url}}"
        
    - type: content_blocks
      columns: 2
      items:
        - image: "{{item1_image}}"
          title: "{{item1_title}}"
          description: "{{item1_desc}}"
          link: "{{item1_url}}"
          
    - type: footer
      social_links: true
      unsubscribe: true
      company_address: true
```

### 个性化

```yaml
personalization:
  merge_tags:
    - "*|FNAME|*": first_name
    - "*|LNAME|*": last_name
    - "*|EMAIL|*": email
    - "*|COMPANY|*": company
    
  conditional_content:
    - condition: "*|IF:VIP|*"
      content: "As a VIP member, you get early access!"
      
  dynamic_content:
    - tag: "*|PRODUCT_RECS|*"
      source: ecommerce
      type: recommended_products
      limit: 4
```

## 分析仪表盘

### 营销活动表现

```
营销活动分析 - "一月新闻简报"
═══════════════════════════════════════

发送:
发送:          25,430
送达:     24,892 (97.9%)
退回:       538 (2.1%)

参与度:
打开:        8,450 (33.9%)
点击:       2,156 (8.7%)
退订:       45 (0.18%)

收入 (如果电子商务):
订单:        89
收入:       $4,523
每封邮件收入: $0.18

按设备:
桌面   ████████████████ 52%
手机    ██████████░░░░░░ 38%
平板    ███░░░░░░░░░░░░ 10%

最点击的链接:
┌────────────────────────┬────────┐
│ 链接                   │ 点击次数 │
├────────────────────────┼────────┤
│ 主 CTA 按钮        │ 1,245  │
│ 产品图片 1        │ 456    │
│ "了解更多" 链接      │ 234    │
│ 社交 - Twitter       │ 123    │
└────────────────────────┴────────┘

打开时间:
高峰: 10:00 AM - 12:00 PM (42%)
```

### 受众健康状况

```yaml
audience_metrics:
  total_subscribers: 45,230
  growth_rate: "+3.2% 每月"
  
  health_indicators:
    active_30_days: 78%
    engaged_90_days: 65%
    dormant: 22%
    
  list_quality:
    average_open_rate: 28.5%
    average_click_rate: 4.2%
    unsubscribe_rate: 0.15%
    bounce_rate: 1.8%
```

## API 示例

### 创建营销活动

```javascript
// 创建营销活动
const campaign = await mailchimp.campaigns.create({
  type: "regular",
  recipients: {
    list_id: "abc123",
    segment_opts: {
      saved_segment_id: "seg123"
    }
  },
  settings: {
    subject_line: "Your Weekly Update",
    preview_text: "This week's top stories",
    from_name: "Company Name",
    reply_to: "hello@company.com"
  }
});

// 设置内容
await mailchimp.campaigns.setContent(campaign.id, {
  template: {
    id: "template_123",
    sections: {
      headline: "Welcome to our newsletter!"
    }
  }
});

// 发送营销活动
await mailchimp.campaigns.send(campaign.id);
```

### 管理订阅者

```javascript
// 添加订阅者
await mailchimp.lists.addListMember("list_id", {
  email_address: "user@example.com",
  status: "subscribed",
  merge_fields: {
    FNAME: "John",
    LNAME: "Doe"
  },
  tags: ["newsletter", "customer"]
});

// 更新订阅者
await mailchimp.lists.updateListMember("list_id", "subscriber_hash", {
  merge_fields: {
    COMPANY: "Acme Inc"
  }
});

// 添加标签
await mailchimp.lists.updateListMemberTags("list_id", "subscriber_hash", {
  tags: [{ name: "vip", status: "active" }]
});
```

## 最佳实践

1. **清理您的列表**: 移除退回和未活跃的
2. **深思熟虑地分段**: 对正确的人发送正确的信息
3. **测试一切**: 标题、内容、时间
4. **移动优先**: 为移动阅读者设计
5. **个性化**: 使用合并标签和动态内容
6. **监控指标**: 跟踪并持续改进
7. **尊重频率**: 不要过度发送
8. **遵守法律**: CAN-SPAM, GDPR
