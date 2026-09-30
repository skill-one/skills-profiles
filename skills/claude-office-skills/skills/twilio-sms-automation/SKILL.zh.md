---
name: Twilio SMS Automation
description: 使用 Twilio 自动化短信通信、双向消息、通知和语音工作流程
---

# Twilio 短信自动化

用于通过 Twilio 自动化短信、语音和验证工作流的全面技能。

## 核心工作流

### 1. 短信发送流程

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
│    发送        │
│  - Twilio API  │
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
    电话号码: "+1234567890"
    消息服务SID: "MG..."  # 用于提高吞吐量
    
  默认值:
    状态回调: "https://api.example.com/sms/status"
    有效期: 14400  # 4小时
    
  速率限制:
    每秒消息数: 10
    每日每人限制: 5
    
  合规性:
    退订关键词: ["STOP", "UNSUBSCRIBE", "CANCEL"]
    需要确认订阅: true
    安静时段:
      开始: "21:00"
      结束: "09:00"
      时区: "America/New_York"
```

## 消息模板

### 通知模板

```yaml
templates:
  订单确认:
    内容: |
      {{company}}: 您的订单 #{{order_id}} 已确认！
      总计: ${{total}}
      跟踪: {{tracking_url}}
      回复 HELP 获取帮助。
    最大长度: 160
    
  运输更新:
    内容: |
      {{company}}: 您的订单 #{{order_id}} 已发货！
      承运商: {{carrier}}
      跟踪号: {{tracking_number}}
      预计送达: {{estimated_date}}
    
  预约提醒:
    内容: |
      提醒：您明天与 {{provider}} 的预约时间为 {{time}}。
      地址: {{address}}
      回复 C 确认或 R 重新安排。
    
  双因素验证:
    内容: |
      您的 {{company}} 验证码是: {{code}}
      此验证码将在 10 分钟后过期。
      不要将此验证码分享给任何人。
```

### 对话式模板

```yaml
双向消息:
  欢迎:
    触发器: opt_in
    响应: |
      欢迎来到 {{company}} 更新！ 
      您将收到订单和运输通知。
      回复 HELP 获取命令或 STOP 取消订阅。
      
  帮助:
    触发器: ["HELP", "?", "INFO"]
    响应: |
      {{company}} 短信命令：
      STATUS - 查询订单状态
      TRACK - 获取跟踪信息
      SUPPORT - 联系客服
      STOP - 取消订阅
      
  状态查询:
    触发器: ["STATUS", "ORDER"]
    动作: lookup_order
    响应: |
      订单 #{{order_id}}: {{status}}
      {{#if tracking}}
      跟踪: {{tracking_url}}
      {{/if}}
      
  取消订阅:
    触发器: ["STOP", "UNSUBSCRIBE"]
    动作: opt_out
    响应: |
      您已取消订阅 {{company}} 消息。
      随时回复 START 重新订阅。
```

## 验证 (双因素认证)

### 验证 API 集成

```yaml
verification_config:
  通道: sms  # 或: call, email, whatsapp
  
  码设置:
    长度: 6
    过期分钟: 10
    
  速率限制:
    最大尝试次数: 5
    锁定分钟: 30
    
  模板:
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
  // 无效的代码
}
```

## 语音自动化

### 外呼

```yaml
voice_config:
  外呼:
    from: "+1234567890"
    twiml_url: "https://api.example.com/voice/script"
    状态回调: "https://api.example.com/voice/status"
    超时: 30
    录音: true
    
  twiml脚本: |
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Say voice="alice">
        您好 {{name}}，这是关于您明天 {{time}} 的预约提醒。
      </Say>
      <Gather numDigits="1" action="/handle-response">
        <Say>按 1 确认，按 2 重新安排。</Say>
      </Gather>
    </Response>
```

### IVR 菜单

```yaml
ivr_menu:
  欢迎语: |
    感谢致电 {{company}}。
    销售按 1，客服按 2，账单按 3。
    按 0 与客服代表通话。
    
  路由:
    - digit: "1"
      动作: transfer
      目的地: "+1987654321"
      队列: "sales"
      
    - digit: "2"
      动作: transfer
      目的地: "+1876543210"
      队列: "support"
      
    - digit: "3"
      动作: transfer
      目的地: "+1765432109"
      队列: "billing"
      
    - digit: "0"
      动作: operator
      备用: voicemail
```

## 批量消息

### 活动配置

```yaml
bulk_campaign:
  名称: "假日促销"
  
  受众:
    来源: segment
    筛选:
      已订阅: true
      最后购买: "> 30_days"
      
  消息:
    模板: holiday_promo
    变量:
      优惠码: "HOLIDAY20"
      
  安排:
    开始时间: "2024-11-25T10:00:00"
    时区: "America/New_York"
    批次大小: 100
    批次间延迟: 60  # 秒
    
  跟踪:
    送达报告: true
    点击跟踪: true
    转化跟踪: true
```

### 广播状态

```
活动状态：假日促销
═══════════════════════════════════════

进度： ████████████████░░░░ 78%

送达统计：
发送：        7,800
送达：   7,450 (95.5%)
失败：      125 (1.6%)
待处理：     225 (2.9%)

互动：
点击：      1,245 (16.7%)
回复：     892 (2.1%)
退订：        23 (0.3%)

错误：
无效号码：  45
已退订：    52
运营商阻止： 18
速率限制：    10

预计完成时间：25分钟
```

## 电话号码管理

### 号码查询

```yaml
number_lookup:
  功能:
    - 运营商信息
    - 主叫姓名
    - 线路类型
    
  验证:
    - 检查格式
    - 验证激活状态
    - 检测固定电话与移动电话
    
  示例响应:
    电话号码: "+14155551234"
    国家代码: "US"
    运营商:
      名称: "Verizon"
      类型: "移动电话"
    主叫姓名: "John Doe"
    有效：true
```

### 号码配置

```yaml
number_management:
  搜索条件:
    国家: "US"
    区号: "415"
    功能: ["SMS", "MMS", "Voice"]
    
  购买:
    电话号码: "+14155559999"
    友好名称: "营销线路"
    sms_url: "https://api.example.com/sms/incoming"
    voice_url: "https://api.example.com/voice/incoming"
```

## 分析仪表盘

```
短信分析 - 过去30天
═══════════════════════════════════════

发送量：
发送：        45,230
送达：   43,456 (96.1%)
失败：      1,774 (3.9%)

按类型：
通知  ████████████░░░░ 62%
营销      ██████░░░░░░░░░░ 23%
双因素验证  ████░░░░░░░░░░░░ 15%

按运营商送达：
Verizon     ████████████████ 97%
AT&T        ███████████████░ 95%
T-Mobile    ██████████████░░ 94%
Sprint      █████████████░░░ 92%

成本：
总支出：     $1,245.67
每条消息：   $0.0275
每条送达：   $0.0287

互动：
链接点击：     3,456 (7.9%)
回复：         892 (2.1%)
退订：        56 (0.1%)
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

// 使用消息服务（推荐用于扩展）
const message = await twilio.messages.create({
  body: '订单已确认！',
  messagingServiceSid: 'MG...',
  to: '+0987654321'
});

// 带媒体的多媒体消息
const mms = await twilio.messages.create({
  body: '查看这张图片！',
  from: '+1234567890',
  to: '+0987654321',
  mediaUrl: ['https://example.com/image.jpg']
});
```

### 处理入站短信

```javascript
// Express webhook 处理程序
app.post('/sms/incoming', (req, res) => {
  const { From, Body } = req.body;
  
  const twiml = new twilio.twiml.MessagingResponse();
  
  if (Body.toUpperCase() === 'STATUS') {
    twiml.message('您的订单正在运输中！');
  } else {
    twiml.message('感谢您的消息。我们将尽快回复。');
  }
  
  res.type('text/xml');
  res.send(twiml.toString());
});
```

## 最佳实践

1. **获取许可**：发送消息前始终需要确认订阅
2. **包含退订选项**：每条消息中都有 STOP 关键词
3. **尊重安静时段**：不要在深夜发送消息
4. **验证号码**：发送前使用查询 API
5. **处理失败**：为暂时性错误添加重试逻辑
6. **监控送达情况**：按运营商跟踪送达率
7. **保持合规**：遵循 TCPA/CTIA 指南
8. **使用模板**：保持一致、经过测试的消息
