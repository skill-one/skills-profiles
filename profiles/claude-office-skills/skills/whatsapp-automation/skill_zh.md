# WhatsApp 自动化

自动化 WhatsApp Business 沟通，包括客户支持、通知、聊天机器人和广播消息。基于 n8n 的 WhatsApp 集成模板。

## 概述

本技能涵盖：
- WhatsApp Business API 设置
- 自动化聊天机器人流程
- 订单/发货通知
- 客户支持自动化
- 广播消息

---

## 设置与配置

### WhatsApp Business API

```yaml
setup_requirements:
  1. meta_business_account:
      - 在 business.facebook.com 创建
      - 验证业务
      
  2. whatsapp_business_api:
      - 通过 Meta 开发者门户访问
      - 创建 WhatsApp Business 应用
      - 获取电话号码 ID
      - 获取访问令牌
      
  3. webhook 配置:
      - 设置回调 URL
      - 验证令牌
      - 订阅消息
      
  4. 消息模板:
      - 在 Business Manager 中创建模板
      - 等待批准（24-48 小时）
```

### 消息模板

```yaml
template_categories:
  事务性:
    - 订单确认
    - 发货更新
    - 配送通知
    - 预约提醒
    
  营销:
    - 促销优惠
    - 产品发布
    - 新闻简报
    
  实用性:
    - 账户验证
    - 密码重置
    - 支付提醒
    
template_example:
  name: "order_confirmation"
  language: "en"
  category: "TRANSACTIONAL"
  components:
    - type: HEADER
      format: TEXT
      text: "订单已确认！🎉"
      
    - type: BODY
      text: |
        您好 {{1}},
        
        您的订单 #{{2}} 已确认！
        
        商品：{{3}}
        总计：{{4}}
        
        我们将在发货时通知您。
        
    - type: FOOTER
      text: "回复 HELP 获取支持"
      
    - type: BUTTONS
      buttons:
        - type: URL
          text: "跟踪订单"
          url: "https://example.com/track/{{1}}"
```

---

## 聊天机器人流程

### 客户支持机器人

```yaml
chatbot_flow:
  name: "客户支持"
  
  欢迎语:
    trigger: first_message
    response: |
      👋 欢迎来到 {Company} 支持！
      
      今天我能帮您什么？
      
      1️⃣ 跟踪订单
      2️⃣ 退货/换货
      3️⃣ 产品问题
      4️⃣ 联系客服
      
      回复数字继续。
      
  流程:
    track_order:
      trigger: "1" OR "track" OR "order"
      steps:
        - ask: "请输入您的订单号:"
        - validate: order_number_format
        - lookup: order_status
        - respond: |
            📦 *订单 #{order_number}*
            
            状态：{status}
            {if_shipped: 追踪：{tracking_number}}
            预计送达：{eta}
            
            [跟踪包裹]({tracking_url})
            
    return_exchange:
      trigger: "2" OR "return" OR "exchange"
      steps:
        - ask: "退货订单号?"
        - check: return_eligibility
        - if_eligible:
            respond: return_instructions
        - if_not:
            respond: contact_support
            
    product_questions:
      trigger: "3" OR "product" OR "question"
      steps:
        - ai_response:
            model: gpt-4
            context: product_faq_knowledge_base
            
    agent_handoff:
      trigger: "4" OR "agent" OR "human"
      steps:
        - check: agent_availability
        - if_available:
            transfer: to_live_agent
            notify: "#support-queue"
        - if_unavailable:
            respond: "我们的团队目前无法接听。留言后，我们将在 24 小时内回复您。"
            create: support_ticket
```

### AI 驱动的回复

```yaml
ai_chatbot:
  model: gpt-4
  
  system_prompt: |
    您是 {Company} 的 WhatsApp 客户支持代理。
    
    指南：
    - 友善且有帮助
    - 保持回复简洁（WhatsApp 偏好短消息）
    - 适当使用表情符号
    - 如果无法帮助，提供联系人工代理的选项
    - 不要编造有关订单或产品的信息
    
    您可以访问：
    - 订单查询
    - 产品目录
    - FAQ 知识库
    
  工具：
    - lookup_order: 通过订单号
    - search_products: 通过关键词
    - check_inventory: 通过产品 ID
    - create_ticket: 复杂问题
    
  升级触发器：
    - 情感：非常负面
    - 关键词：["投诉", "退款", "生气", "起诉"]
    - 循环检测：重复问题 3 次
```

---

## 通知工作流

### 订单通知

```yaml
order_notifications:
  order_placed:
    trigger: shopify_order_created
    template: order_confirmation
    variables:
      - customer_name
      - order_number
      - items_summary
      - total_amount
      
  payment_received:
    trigger: payment_captured
    message: |
      ✅ 已收到订单 #{order_number} 的付款！
      
      金额：{amount}
      
      我们正在准备您的订单。
      
  shipped:
    trigger: fulfillment_created
    template: shipping_update
    variables:
      - tracking_number
      - carrier
      - estimated_delivery
      
  out_for_delivery:
    trigger: tracking_status_change
    condition: status == "out_for_delivery"
    message: |
      🚚 您的订单正在配送中！
      
      预计今天送达 {eta}。
      
      实时跟踪：{tracking_url}
      
  delivered:
    trigger: tracking_status_change
    condition: status == "delivered"
    message: |
      📦 您的订单已送达！
      
      希望您喜欢！ 
      
      [留下评价]({review_url})
      [需要帮助?]({support_url})
```

### 预约提醒

```yaml
appointment_reminders:
  schedule:
    - 提前 24 小时
    - 提前 1 小时
    
  template: appointment_reminder
  
  24h_message: |
    📅 *预约提醒*
    
    您好 {name},
    
    您明天有一个预约：
    
    📍 {location}
    🕐 {time}
    👤 {provider}
    
    回复：
    ✅ 确认
    ❌ 取消
    📅 更改时间
    
  1h_message: |
    ⏰ 您的预约在 1 小时后！
    
    {provider} 在 {location}
    
    很快见！
```

---

## 广播消息

### 活动管理

```yaml
broadcast_campaigns:
  setup:
    - 从 CRM 导入联系人
    - 根据标准划分受众
    - 获取模板批准
    - 安排发送
    
  定位选项：
    - 所有联系人
    - 标签：[vip, 新客户, 不活跃]
    - 购买历史
    - 位置
    - 自定义分段
    
  合规性：
    - opt_in_required: true
    - opt_out 易于操作：回复_STOP
    - 频率限制：每个联系人每天
    - 安静时间：尊重时区
    
  跟踪：
    - 已送达
    - 已读
    - 已回复
    - 点击链接
    - 已选择退出
```

### 活动模板

```yaml
campaign_templates:
  促销:
    template: |
      🎉 *特别优惠为您！*
      
      您好 {name},
      
      {offer_description}
      
      代码：{promo_code}
      有效期至：{expiry}
      
      [立即购买]({url})
      
      回复 STOP 取消订阅
      
  产品发布:
    template: |
      🚀 *新品警报*
      
      {name}，查看我们的最新产品：
      
      {product_name}
      {product_description}
      
      {price}
      
      [查看产品]({url})
      
  重新参与:
    template: |
      👋 *我们想念您，{name}！*
      
      自上次访问以来已经有一段时间了。
      
      欢迎回来，享受 15% 折扣：
      
      代码：COMEBACK15
      
      [立即购买]({url})
```

---

## n8n 集成

### 工作流示例

```yaml
workflow: "WhatsApp 订单机器人"

nodes:
  - name: "WhatsApp 触发器"
    type: "n8n-nodes-base.whatsAppTrigger"
    parameters:
      events: ["messages"]
      
  - name: "解析消息"
    type: "n8n-nodes-base.code"
    parameters:
      code: |
        const message = $input.first().json;
        return {
          from: message.from,
          text: message.text.body,
          type: message.type
        };
        
  - name: "AI 回复"
    type: "n8n-nodes-base.openAi"
    parameters:
      model: "gpt-4"
      messages: [
        { role: "system", content: "..." },
        { role: "user", content: "{{ $json.text }}" }
      ]
      
  - name: "发送回复"
    type: "n8n-nodes-base.whatsApp"
    parameters:
      operation: "sendMessage"
      phoneNumberId: "{{ $env.WHATSAPP_PHONE_ID }}"
      recipientPhoneNumber: "{{ $json.from }}"
      message: "{{ $json.response }}"
```

---

## 输出示例

**请求**： "创建 WhatsApp 订单通知流程"

**输出**：

```markdown
# WhatsApp 订单通知

## 消息模板（需要 Meta 批准）

### 1. 订单确认
```
您好 {{1}}！ 🎉

您的订单 #{{2}} 已确认！

商品：{{3}}
总计：{{4}}

我们将更新您何时发货。

[跟踪订单]({{5}})
```

### 2. 发货更新
```
📦 您的订单正在配送中！

订单：#{{1}}
承运商：{{2}}
追踪：{{3}}

预计送达：{{4}}

[跟踪包裹]({{5}})
```

### 3. 已送达
```
✅ 已送达！

您的订单 #{{1}} 已送达。

喜欢吗？留下评价！
需要帮助？回复此消息。

[评价]({{2}})
```

## n8n 工作流

```yaml
触发器：Shopify 订单创建
步骤：
  1. 获取客户电话
  2. 格式化订单详情
  3. 发送 WhatsApp 模板
  4. 记录到 CRM
```

## 自动化规则

- 订单创建 → 确认（立即）
- 发货 → 跟踪（立即）
- 配送中 → 提醒（立即）
- 已送达 → 请求评价（1 天后）
```

---

*WhatsApp 自动化技能 - 隶属于 Claude 办公技能*
