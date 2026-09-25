# Twilio 短信自动化

用于通过 Twilio 自动化短信、语音和验证工作流的全面技能。

## 核心工作流

### 1. 短信消息流程

```
短信自动化流程：
┌─────────────────┐
│    触发器      │
│  (事件/API)    │
└────────┬────────┘
         ▼
┌─────────────────┐
│  消息构建      │
│  - 模板        │
│  - 个性化      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  号码查询      │
│  - 验证        │
│  - 格式化      │
└────────┬────────┘
         ▼
┌─────────────────┐
│     发送        │
│  - Twilio API   │
│  - 队列        │
└────────┬────────┘
         ▼
┌─────────────────┐
│    送达        │
│  - 状态        │
│  - 回调        │
└─────────────────┘
```

### 2. 消息配置

```yaml
sms_config:
  发送者:
    phone_number: "+1234567890"
    messaging_service_sid: "MG..."  # 用于更高的吞吐量
    
  默认值:
    status_callback: "https://api.example.com/sms/status"
    validity_period: 14400  # 4小时
    
  速率限制:
    messages_per_second: 10
    daily_limit_per_recipient: 5
    
  合规性:
    opt_out_keywords: ["STOP", "UNSUBSCRIBE", "CANCEL"]
    opt_in_required: true
    安静时段:
      start: "21:00"
      end: "09:00"
      timezone: "America/New_York"
```

## 消息模板

### 通知模板

```yaml
templates:
  order_confirmation:
    content: |
      {{company}}: 您的订单 #{{order_id}} 已确认！
      总计: ${{total}}
      跟踪: {{tracking_url}}
      回复 HELP 获取帮助。
    max_length: 160
    
  shipping_update:
    content: |
      {{company}}: 您的订单 #{{order_id}} 已发货！
      承运商: {{carrier}}
      跟踪: {{tracking_number}}
      预计送达: {{estimated_date}}
    
  appointment_reminder:
    content: |
      提醒: 您明天与 {{provider}} 的预约时间为 {{time}}。
      地址: {{address}}
      回复 C 确认或 R 重新安排。
    
  two_factor:
    content: |
      您的 {{company}} 验证码是: {{code}}
      此验证码将在 10 分钟后过期。
      不要将此验证码分享给任何人。
```

### 对话式模板

```yaml
two_way_messaging:
  welcome:
    trigger: opt_in
    response: |
      欢迎关注 {{company}} 更新！ 
      您将收到订单和物流通知。
      回复 HELP 获取命令或 STOP 取消订阅。
      
  help:
    trigger: ["HELP", "?", "INFO"]
    response: |
      {{company}} 短信命令:
      STATUS - 查询订单状态
      TRACK - 获取跟踪信息
      SUPPORT - 联系客服
      STOP - 取消订阅
      
  status_inquiry:
    trigger: ["STATUS", "ORDER"]
    action: lookup_order
    response: |
      订单 #{{order_id}}: {{status}}
      {{#if tracking}}
      跟踪: {{tracking_url}}
      {{/if}}
      
  unsubscribe:
    trigger: ["STOP", "UNSUBSCRIBE"]
    action: opt_out
    response: |
      您已取消订阅 {{company}} 消息。
      随时回复 START 重新订阅。
```

## 验证 (2FA)

### 验证 API 集成

```yaml
verification_config:
  channel: sms  # 或: call, email, whatsapp
  
  code_settings:
    length: 6
    expiry_minutes: 10
    
  rate_limits:
    max_attempts: 5
    lockout_minutes: 30
    
  templates:
    sms: "您的 {{company}} 码是 {{code}}"
    call: "您的验证码是 {{code_spoken}}"
```

### 验证流程

```javascript
// 开始验证
const verification = await twilio.verify.v2
  .services('VA...')
  .verifications
  .create({
    to: '+1234567890',
    channel: 'sms',
    customCode: '123456', // 可选
    locale: 'en'
  });

// 检查验证
const check = await twilio.verify.v2
  .services('VA...')
  .verificationChecks
  .create({
    to: '+1234567890',
    code: '123456'
  });

// 结果
if (check.status === 'approved') {
  // 验证成功
} else {
  // 码无效
}
```

## 语音自动化

### 外呼

```yaml
voice_config:
  outbound_call:
    from: "+1234567890"
    twiml_url: "https://api.example.com/voice/script"
    status_callback: "https://api.example.com/voice/status"
    timeout: 30
    record: true
    
  twiml_script: |
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Say voice="alice">
        您好 {{name}}，这是关于您明天 {{time}} 预约的提醒。
      </Say>
      <Gather numDigits="1" action="/handle-response">
        <Say>按 1 确认，按 2 重新安排。</Say>
      </Gather>
    </Response>
```

### IVR 菜单

```yaml
ivr_menu:
  greeting: |
    感谢致电 {{company}}。
    销售请按 1。
    客服请按 2。
    账单请按 3。
    要与客服通话请按 0。
    
  routing:
    - digit: "1"
      action: transfer
      destination: "+1987654321"
      queue: "sales"
      
    - digit: "2"
      action: transfer
      destination: "+1876543210"
      queue: "support"
      
    - digit: "3"
      action: transfer
      destination: "+1765432109"
      queue: "billing"
      
    - digit: "0"
      action: operator
      fallback: voicemail
```

## 批量消息

### 活动配置

```yaml
bulk_campaign:
  name: "假日促销"
  
  受众:
    source: segment
    filter:
      opted_in: true
      last_purchase: "> 30_days"
      
  消息:
    template: holiday_promo
    variables:
      discount_code: "HOLIDAY20"
      
  计划:
    start_time: "2024-11-25T10:00:00"
    timezone: "America/New_York"
    batch_size: 100
    delay_between_batches: 60  # 秒
    
  跟踪:
    delivery_report: true
    click_tracking: true
    conversion_tracking: true
```

### 广播状态

```
活动状态: 假日促销
═══════════════════════════════════════

进度: ████████████████░░░░ 78%

发送统计:
发送:        7,800
送达:       7,450 (95.5%)
失败:        125 (1.6%)
待处理:      225 (2.9%)

互动:
点击:       1,245 (16.7%)
回复:        892 (1.2%)
取消订阅:     23 (0.3%)

错误:
无效号码:   45
已取消订阅:   52
运营商阻止:   18
速率限制:    10

预计完成时间: 25 分钟
```

## 电话号码管理

### 号码查询

```yaml
number_lookup:
  功能:
    - carrier_info
    - caller_name
    - line_type
    
  验证:
    - check_format
    - verify_active
    - detect_landline_vs_mobile
    
  示例响应:
    phone_number: "+14155551234"
    country_code: "US"
    carrier:
      name: "Verizon"
      type: "mobile"
    caller_name: "John Doe"
    valid: true
```

### 号码配置

```yaml
number_management:
  搜索条件:
    country: "US"
    area_code: "415"
    capabilities: ["SMS", "MMS", "Voice"]
    
  购买:
    phone_number: "+14155559999"
    friendly_name: "营销线路"
    sms_url: "https://api.example.com/sms/incoming"
    voice_url: "https://api.example.com/voice/incoming"
```

## 分析仪表盘

```
短信分析 - 过去 30 天
═══════════════════════════════════════

发送量:
发送:        45,230
送达:       43,456 (96.1%)
失败:        1,774 (3.9%)

按类型:
通知  ████████████░░░░ 62%
营销  ██████░░░░░░░░░░ 23%
2FA  ████░░░░░░░░░░░░ 15%

按运营商送达:
Verizon     ████████████████ 97%
AT&T        ███████████████░ 95%
T-Mobile    ██████████████░░ 94%
Sprint      █████████████░░░ 92%

成本:
总支出:     $1,245.67
每条消息:   $0.0275
每条送达:   $0.0287

互动:
链接点击:   3,456 (7.9%)
回复:        892 (2.1%)
取消订阅:     56 (0.1%)
```

## API 示例

### 发送短信

```javascript
// 简单短信
const message = await twilio.messages.create({
  body: '来自 Twilio 的问候！',
  from: '+1234567890',
  to: '+0987654321',
  statusCallback: 'https://api.example.com/sms/status'
});

// 使用消息服务 (推荐用于扩展)
const message = await twilio.messages.create({
  body: '订单已确认！',
  messagingServiceSid: 'MG...',
  to: '+0987654321'
});

// 带媒体的 MMS
const mms = await twilio.messages.create({
  body: '查看这张图片！',
  from: '+1234567890',
  to: '+0987654321',
  mediaUrl: ['https://example.com/image.jpg']
});
```

### 处理入站短信

```javascript
// Express webhook 处理器
app.post('/sms/incoming', (req, res) => {
  const { From, Body } = req.body;
  
  const twiml = new twilio.twiml.MessagingResponse();
  
  if (Body.toUpperCase() === 'STATUS') {
    twiml.message('您的订单正在配送中！');
  } else {
    twiml.message('感谢您的消息。我们将尽快回复。');
  }
  
  res.type('text/xml');
  res.send(twiml.toString());
});
```

## 最佳实践

1. **获取许可**: 在发送消息前始终获取 opt-in
2. **包含退订**: 每条消息中包含 STOP 关键词
3. **尊重安静时段**: 不要在深夜发送消息
4. **验证号码**: 在发送前使用 Lookup API
5. **处理失败**: 为临时错误添加重试逻辑
6. **监控送达**: 按运营商跟踪送达率
7. **遵守合规**: 遵循 TCPA/CTIA 指南
8. **使用模板**: 保持一致、经过测试的消息
