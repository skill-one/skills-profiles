# Telegram Bot

构建用于聊天机器人、通知、AI 助手和群组自动化的 Telegram 机器人。基于 n8n 的 Telegram 工作流模板。

## 概述

本技能涵盖：
- 机器人设置和配置
- 消息处理模式
- AI 驱动的助手
- 通知工作流
- 群组自动化

---

## 机器人设置

### 创建机器人

```yaml
setup_steps:
  1. create_bot:
      - open: @BotFather on Telegram
      - command: /newbot
      - provide: bot_name
      - provide: bot_username (必须以 'bot' 结尾)
      - receive: API_token
      
  2. configure_bot:
      - command: /setdescription
      - command: /setabouttext
      - command: /setuserpic
      - command: /setcommands
      
  3. get_chat_id:
      - start: 与机器人对话
      - call: https://api.telegram.org/bot{TOKEN}/getUpdates
      - extract: chat.id 从响应中
```

### 机器人命令

```yaml
commands:
  - command: /start
    description: "启动机器人"
    
  - command: /help
    description: "显示可用命令"
    
  - command: /status
    description: "检查系统状态"
    
  - command: /subscribe
    description: "订阅通知"
    
  - command: /unsubscribe
    description: "取消订阅通知"
```

---

## 消息处理器

### 基本消息处理器

```yaml
workflow: "Telegram 消息处理器"
trigger: telegram_message

handlers:
  text_message:
    action: |
      1. 解析消息文本
      2. 确定意图
      3. 处理请求
      4. 发送响应
      
  command:
    pattern: "^/"
    action: route_to_command_handler
    
  photo:
    action: |
      1. 下载照片
      2. 使用视觉 AI 处理
      3. 发送分析结果
      
  document:
    action: |
      1. 下载文档
      2. 提取内容
      3. 处理并响应
      
  voice:
    action: |
      1. 下载音频
      2. 使用 Whisper 转录
      3. 处理文本
      4. 发送（文本或语音）
      
  location:
    action: |
      1. 提取坐标
      2. 查询本地信息
      3. 发送相关数据
```

### n8n 工作流

```yaml
workflow: "Telegram Bot n8n"

nodes:
  - name: "Telegram Trigger"
    type: "n8n-nodes-base.telegramTrigger"
    parameters:
      updates: ["message", "callback_query"]
      
  - name: "Route Message Type"
    type: "n8n-nodes-base.switch"
    parameters:
      rules:
        - output: 0
          condition: "{{ $json.message.text.startsWith('/') }}"
        - output: 1
          condition: "{{ $json.message.photo }}"
        - output: 2
          condition: "{{ $json.message.voice }}"
        - output: 3
          fallback: true
          
  - name: "Process with AI"
    type: "n8n-nodes-base.openAi"
    parameters:
      model: "gpt-4"
      messages:
        - role: "system"
          content: "You are a helpful Telegram assistant."
        - role: "user"
          content: "{{ $json.message.text }}"
          
  - name: "Send Response"
    type: "n8n-nodes-base.telegram"
    parameters:
      chatId: "{{ $json.message.chat.id }}"
      text: "{{ $json.response }}"
```

---

## AI 驱动的机器人

### GPT-4 集成

```yaml
ai_bot:
  name: "AI 助手机器人"
  
  system_prompt: |
    你是一个 Telegram 上的有用 AI 助手。
    
    指南：
    - 保持简洁（Telegram 有消息限制）
    - 适当使用表情符号
    - 在需要时使用 Markdown 格式
    - 如有需要，请询问澄清问题
    
  features:
    - conversational_memory: true
    - context_window: last_10_messages
    - tools: [web_search, calculator, weather]
    
  message_formatting:
    max_length: 4096
    split_long_messages: true
    use_markdown: true
```

### 多模态机器人

```yaml
multimodal_bot:
  handlers:
    text:
      model: gpt-4
      action: chat_completion
      
    image:
      model: gpt-4-vision
      action: analyze_and_respond
      
    voice:
      transcribe: whisper
      process: gpt-4
      respond: text_or_voice
      
    document:
      extract: based_on_type
      summarize: gpt-4
      respond: text
```

---

## 通知系统

### 警报机器人

```yaml
workflow: "系统警报机器人"

triggers:
  - source: monitoring_system
    event: alert
  - source: ci_cd
    event: build_status
  - source: ecommerce
    event: new_order
    
notification_templates:
  alert:
    format: |
      🚨 *警报：{severity}*
      
      *服务：* {service}
      *消息：* {message}
      *时间：* {timestamp}
      
      [查看仪表盘]({dashboard_link})
      
  build:
    format: |
      {status_emoji} *构建 {status}*
      
      *项目：* {project}
      *分支：* {branch}
      *提交：* `{commit_short}`
      
      {details}
      
  order:
    format: |
      🛒 *新订单！*
      
      *订单：* #{order_id}
      *客户：* {customer}
      *总金额：* ${total}
      *商品数量：* {item_count}
      
routing:
  by_severity:
    critical: [admin_group, on_call_user]
    warning: [team_group]
    info: [logging_channel]
```

### 定时通知

```yaml
scheduled_notifications:
  daily_digest:
    schedule: "9am daily"
    template: |
      📊 *每日摘要 - {date}*
      
      📈 销售额：${sales} ({change})
      👥 新用户：{new_users}
      🎫 打开工单：{tickets}
      
      祝你今天愉快！ ☀️
      
  weekly_report:
    schedule: "周一 9am"
    template: weekly_metrics_report
    
  reminder:
    trigger: custom_event
    template: |
      ⏰ *提醒*
      
      {reminder_text}
      
      安排人：{creator}
```

---

## 群组自动化

### 欢迎机器人

```yaml
group_bot:
  on_member_join:
    action: |
      1. 检查新成员
      2. 发送欢迎消息
      3. 分享规则
      4. 建议自我介绍
      
    template: |
      👋 欢迎加入 {group_name}, {user_name}!
      
      请：
      1. 阅读 /rules
      2. 进行自我介绍
      3. 随时提问！
      
      祝你愉快！ 🎉
      
  on_member_leave:
    action: optional_goodbye
    
  moderation:
    - spam_detection: auto_delete + warn
    - link_filtering: whitelist_only
    - flood_control: rate_limit
```

### 投票与调查机器人

```yaml
poll_bot:
  commands:
    /poll:
      format: "/poll 问题 | 选项1 | 选项2 | ..."
      action: create_poll
      
    /survey:
      action: start_multi_question_survey
      
    /results:
      action: show_aggregated_results
      
  features:
    - 匿名投票：可选
    - 多项选择：可选
    - 定时关闭：可选
    - 导出结果：到电子表格
```

---

## 内联功能

### 内联键盘

```yaml
inline_keyboard:
  example:
    text: "选择一个选项："
    keyboard:
      - row:
          - text: "选项 1"
            callback_data: "opt_1"
          - text: "选项 2"
            callback_data: "opt_2"
      - row:
          - text: "取消"
            callback_data: "cancel"
            
  callback_handler:
    opt_1:
      action: process_option_1
      response: "你选择了选项 1"
      
    opt_2:
      action: process_option_2
      response: "你选择了选项 2"
      
    cancel:
      action: cancel_operation
      response: "操作已取消"
```

### 内联查询

```yaml
inline_mode:
  trigger: "@botname query"
  
  results:
    - type: article
      title: "{query} 结果"
      description: "点击发送"
      message_text: "结果为：{query}"
      
    - type: photo
      photo_url: "{search_result_image}"
      
    - type: gif
      gif_url: "{gif_url}"
```

---

## 输出示例

**请求**： "创建一个用于服务器警报的 Telegram 通知机器人"

**输出**：

```markdown
# 服务器警报 Telegram 机器人

## 设置

1. 使用 @BotFather 创建机器人
2. 获取 token：`123456:ABC-DEF...`
3. 获取警报通道的 chat ID

## n8n 工作流

```yaml
nodes:
  1. Webhook（接收警报）
  2. 格式化消息
  3. Telegram 发送
```

## 警报模板

**严重警报：**
```
🚨 严重警报

服务器：production-web-01
状态：宕机
时间：2026-01-30 14:32:05 UTC

详情：
- CPU：98%
- 内存：95%
- 磁盘：89%

[查看 Grafana] [确认]
```

**恢复：**
```
✅ 恢复

服务器：production-web-01
停机时间：5 分钟
状态：所有系统正常

自动解决事件。
```

## 实现

```javascript
// 发送警报函数
async function sendAlert(severity, message, details) {
  const emoji = {
    critical: '🚨',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅'
  };
  
  const text = `${emoji[severity]} *${severity.toUpperCase()}*\n\n${message}\n\n${details}`;
  
  await telegram.sendMessage({
    chat_id: ALERT_CHANNEL_ID,
    text: text,
    parse_mode: 'Markdown'
  });
}
```

## 功能
- 基于严重性的路由
- 内联操作按钮
- 确认跟踪
- 升级规则
```

---

*Telegram 机器人技能 - Claude 办公技能的一部分*
