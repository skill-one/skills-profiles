# 邮件营销

全面的邮件营销技能，涵盖活动创建、自动化序列、A/B测试、细分和可投递性优化。

## 概述

本技能涵盖：
- 邮件活动创建和模板
- 自动化滴灌序列
- A/B测试框架
- 列表细分策略
- 可投递性最佳实践

---

## 邮件类型与模板

### 1. 欢迎序列

```yaml
sequence: "欢迎系列"
trigger: subscriber_signup
duration: 14_days

emails:
  - day_0:
      subject: "欢迎来到 {Brand} 🎉"
      goal: deliver_lead_magnet + set_expectations
      template: |
        Hi {first_name},
        
        欢迎来到 {Brand}！这是您的 [免费资源]。
        
        在接下来的2周内，我将分享：
        • {benefit_1}
        • {benefit_2}
        • {benefit_3}
        
        首先：[邮件2的预告]
        
        即刻，
        {sender_name}
        
  - day_2:
      subject: "{audience} 的 #1 错误"
      goal: educate + build_trust
      
  - day_4:
      subject: "{first_name}，一个快速问题"
      goal: engagement + segmentation
      
  - day_7:
      subject: "{customer} 如何实现 {result}"
      goal: social_proof + soft_pitch
      
  - day_10:
      subject: "准备好 {achieve_goal} 吗？"
      goal: conversion + offer
      
  - day_14:
      subject: "最后机会：{offer_details}"
      goal: urgency + final_conversion
```

### 2. 新闻简报模板

```yaml
newsletter:
  frequency: 每周
  day: 周二
  time: 上午10:00
  
  structure:
    - header:
        logo: true
        issue_number: true
        
    - intro:
        personal_note: 2-3句话
        tease_content: true
        
    - main_content:
        sections: 3-5
        format: |
          ## {Section Title}
          
          {2-3段见解}
          
          **关键要点**：{一句话}
          
          [阅读更多 →]({link})
          
    - 精选链接：
        count: 3-5
        format: "• {title} - {一句话描述}"
        
    - CTA：
        primary: 产品/服务
        secondary: 分享/回复
        
    - 页脚：
        social_links: true
        unsubscribe: 必须提供
```

### 3. 促销邮件

```yaml
promo_email:
  type: sale_announcement
  
  subject_options:
    - "{first_name}，今晚30%折扣结束"
    - "🚨 最后几小时：您的专属优惠"
    - "最后机会：在 {product} 上节省 $X"
    
  structure:
    hero:
      headline: "{Offer headline}"
      subhead: "限时优惠"
      cta_button: "立即购买"
      
    body:
      - urgency: "促销将在 {countdown} 结束"
      - social_proof: "{X} 位客户已经节省"
      - benefits: 项目符号列表
      - testimonial: 1句简短引言
      
    cta:
      button_text: "领取 {X}% 折扣"
      link: "{promo_landing_page}"
      
    ps:
      text: "P.S. {紧迫性提醒或额外优惠}"
```

---

## 自动化序列

### 购物车放弃

```yaml
sequence: "购物车恢复"
trigger: cart_abandoned
wait_before_start: 1_hour

emails:
  - email_1:
      delay: 1_hour
      subject: "忘记什么了？ 🛒"
      content: |
        Hi {first_name},
        
        您在购物车中遗漏了一些商品：
        
        {cart_items_with_images}
        
        [完成订单 →]
        
        有问题？回复此邮件。
        
  - email_2:
      delay: 24_hours
      subject: "您的购物车还在等您"
      content: |
        还在犹豫吗？
        
        这里是 {X} 位客户喜欢 {product} 的原因：
        
        ⭐ "{testimonial}"
        
        [立即购买 →]
        
  - email_3:
      delay: 72_hours
      subject: "最后机会 + 免费运费"
      content: |
        Hi {first_name},
        
        您的购物车即将过期，但这里有一个小激励：
        
        使用代码 FREESHIP 赠送免费运费。
        
        [使用免费运费完成订单 →]
```

### 重新参与序列

```yaml
sequence: "Win-Back"
trigger: inactive_90_days

emails:
  - email_1:
      subject: "我们想念您，{first_name}"
      content: |
        有段时间没见了！这是 {Brand} 的新动态：
        
        • {New feature 1}
        • {New feature 2}
        • {New content}
        
        回来查看 →
        
  - email_2:
      delay: 7_days
      subject: "专为您提供的特别优惠"
      content: |
        {first_name},
        
        我们很乐意再次拥有您。这里是您下次购买的20%折扣。
        
        代码：COMEBACK20
        
  - email_3:
      delay: 14_days
      subject: "我们应该分开吗？"
      content: |
        Hi {first_name},
        
        我们注意到您有一段时间没有打开我们的邮件了。
        
        如果您想继续订阅，请点击这里：[继续订阅]
        
        如果不，我们将在7天内将您从我们的列表中移除。
        
        无论如何都没有关系。
```

---

## A/B 测试框架

### 要测试的内容

```yaml
ab_test_elements:
  high_impact:
    - subject_line:
        variants: 2-3
        sample_size: 列表的20%
        winner_criteria: 打开率
        
    - send_time:
        variants: [早晨, 下午, 晚上]
        test_duration: 2_weeks
        
    - cta_button:
        variants: [文本, 颜色, 位置]
        winner_criteria: 点击率
        
  medium_impact:
    - preview_text
    - email_length
    - personalization_level
    - image_vs_no_image
    
  low_impact:
    - font_choice
    - button_shape
    - footer_layout
```

### 主题行 A/B 测试示例

```yaml
test_1:
  hypothesis: "表情符号提高打开率"
  variant_a: "您的每周生产力技巧"
  variant_b: "您的每周生产力技巧 🚀"
  
test_2:
  hypothesis: "个性化提高打开率"
  variant_a: "您将喜爱的新功能"
  variant_b: "{first_name}，您将喜爱的新功能"
  
test_3:
  hypothesis: "好奇心差距提高打开率"
  variant_a: "省钱5种方法"
  variant_b: "我差点犯下的500美元错误"
  
test_4:
  hypothesis: "紧迫性提高打开率"
  variant_a: "周末30%折扣"
  variant_b: "24小时内30%折扣结束"
```

---

## 细分策略

```yaml
segmentation:
  behavioral:
    - purchase_history:
        segments: [从未购买, 一次性, 重复, VIP]
        
    - engagement_level:
        segments: [高度参与, 中度, 消极, 已流失]
        criteria:
          highly_engaged: 最近5封中打开5封
          moderate: 最近5封中打开2-5封
          inactive: 30天未打开
          churned: 90天未打开
          
    - product_interest:
        based_on: [点击, 页面浏览, 购物车添加]
        
  demographic:
    - location: 用于时区优化
    - industry: 用于B2B个性化
    - company_size: 用于优惠定制
    
  lifecycle:
    - stage: [潜在客户, 试用, 客户, 已流失]
    - tenure: [新客户, 已建立, 长期客户]

segment_specific_content:
  vip_customers:
    - early_access: true
    - exclusive_discounts: true
    - personalized_recommendations: true
    
  inactive_subscribers:
    - reduced_frequency: true
    - re_engagement_offers: true
    - sunset_flow: 90天后
```

---

## 可投递性最佳实践

```yaml
deliverability:
  authentication:
    required:
      - SPF: 发送者策略框架
      - DKIM: 域名密钥
      - DMARC: 对齐策略
    check: mxtoolbox.com
    
  list_hygiene:
    - remove_bounces: 立即
    - remove_unsubscribes: 立即
    - re_engage_inactive: 60天后
    - remove_inactive: 90天后
    
  content_best_practices:
    - spam_words_avoid: [免费, 立即行动, 限时, 点击这里]
    - text_to_image_ratio: 60:40
    - alt_text: 所有图片
    - unsubscribe_link: 突出显示
    - physical_address: 必须提供 (CAN-SPAM)
    
  sending_practices:
    - warm_up_new_domain: 2-4周
    - consistent_sending: 相同日期/时间
    - gradual_volume_increase: 最大每周20%
    - monitor_complaints: 目标 <0.1%
```

---

## 分析与KPI

```yaml
email_metrics:
  primary:
    - open_rate:
        benchmark: 20-25%
        improve_with: subject_lines, sender_name, send_time
        
    - click_rate:
        benchmark: 2-5%
        improve_with: content, cta, design
        
    - conversion_rate:
        benchmark: 1-3%
        improve_with: offer, landing_page, targeting
        
  secondary:
    - unsubscribe_rate:
        healthy: <0.5%
        action: 审查频率, 内容相关性
        
    - bounce_rate:
        healthy: <2%
        action: 清理列表, 验证邮件
        
    - spam_complaints:
        healthy: <0.1%
        action: 改进opt-in, 添加退订
        
  revenue:
    - revenue_per_email
    - revenue_per_subscriber
    - customer_lifetime_value

reporting_template: |
  # 邮件性能报告 - {周/月}
  
  ## 活动摘要
  | 活动 | 发送 | 打开 | 点击 | 转化 | 收入 |
  |------|------|------|------|------|------|
  | 新闻简报 | 10K | 22% | 3.5% | 1.2% | $5,000 |
  | 促销 | 10K | 28% | 5.2% | 2.8% | $12,000 |
  
  ## 列表健康状况
  - 总订阅者：50,000
  - 本周新增：500
  - 退订：45 (0.09%)
  - 退回：12 (0.02%)
  
  ## 表现最佳
  - 最佳主题："{subject}" (32% 打开率)
  - 最佳CTA："{cta}" (8% 点击率)
  
  ## 建议
  1. 测试更多基于好奇心的主题
  2. 下次促销按参与度细分
  3. 清理不活跃订阅者 (2,000+)
```

---

## 输出示例

**请求**： "为SaaS产品创建一个欢迎邮件序列"

**输出**：

```markdown
# 欢迎序列 - SaaS产品

## 邮件1：欢迎 (立即)
**主题**：欢迎来到 {Product}！这是您的快速入门指南 🚀

```
Hi {first_name},

欢迎来到 {Product}！我是 {founder_name}，很高兴您在这里。

您加入了10,000+团队，他们已经改变了他们的工作方式。

**您的第一步**：[完成您的个人资料] (需要2分钟)

在接下来的1周内，我将分享：
• 节省用户5+小时/周的3个功能
• {Company} 如何将生产力提高40%
• 功率用户的小贴士

有问题？回复此邮件——我阅读每一封邮件。

让我们开始吧，
{founder_name}

P.S. 需要帮助？[预约免费上线咨询]
```

---

## 邮件2：快速获胜 (第2天)
**主题**：{first_name}，试试这个2分钟的小技巧

```
Hi {first_name},

第2天，我想分享我们用户最喜欢的功能：

**[Feature Name]**

只需2分钟即可设置，用户报告每天节省1+小时。

设置方法：
1. 前往设置 → [Feature]
2. 点击"启用"
3. 就是这样！

[现在设置 →]

明天，我将向您展示 {Customer} 如何使用这个功能实现 {impressive result}。

很快见，
{founder_name}
```

---

## 邮件3：社会证明 (第4天)
**主题**：{Customer} 如何节省10小时/周

```
Hi {first_name},

认识Sarah，她是 {Company} 的项目经理。

在 {Product} 之前："我每周花费10+小时在状态更新上。"

在 {Product} 之后："一切都自动化了。我现在专注于实际工作。"

最好的部分？她一个下午就设置好了。

想知道类似的结果吗？这里是Sarah的3个顶级技巧：

1. {Tip 1}
2. {Tip 2}
3. {Tip 3}

[查看完整案例研究 →]

您最大的生产力挑战是什么？回复并告诉我。

{founder_name}
```

---

## 邮件4：参与检查 (第7天)
**主题**：{first_name}，一个快速问题

```
Hi {first_name},

已经一周了！快速检查：

{Product} 对您来说怎么样？

A) 🚀 很喜欢！
B) 🤔 还在摸索中
C) 😕 有些问题

[点击您的答案]

根据您的回复，我将发送最相关的资源。

{founder_name}

P.S. 如果您选择了C，回复并提供详细信息，我的团队将在24小时内帮助您。
```

---

## 邮件5：转化 (第10天)
**主题**：准备好解锁全部功能了吗？

```
Hi {first_name},

您已经使用 {Product} 10天了。您已经完成了：

📊 {personalized_stats}

很棒！但您只使用了 {Product} 的40%。

**升级到Pro，您可以解锁：**
✅ {Pro feature 1}
✅ {Pro feature 2}
✅ {Pro feature 3}

平均而言，升级团队的效率提高了 {X%}。

[升级到Pro →]

使用代码 WELCOME20 赠送第一年20%折扣。

{founder_name}
```

---

**序列设置：**
- 邮件间隔时间：按指定
- 跳过周末发送：是
- 退出条件：升级或退订
- 分支：如果第3封邮件后没有打开 → 较短的重新参与序列
```

---

*邮件营销技能 - 隶属于Claude办公技能*
