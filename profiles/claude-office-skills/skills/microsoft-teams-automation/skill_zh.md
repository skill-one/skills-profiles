# Microsoft Teams 自动化

自动化 Microsoft Teams 沟通和协作工作流。

## 核心功能

### 频道消息
```yaml
message_types:
  simple_message:
    channel_id: "channel_xxx"
    message: "你好，团队！"
    
  formatted_message:
    channel_id: "channel_xxx"
    content_type: "html"
    message: |
      <h1>每周更新</h1>
      <ul>
        <li>项目1</li>
        <li>项目2</li>
      </ul>
      
  adaptive_card:
    channel_id: "channel_xxx"
    card:
      type: "AdaptiveCard"
      body:
        - type: "TextBlock"
          text: "需要批准"
          weight: "bolder"
        - type: "Input.Text"
          id: "comment"
          placeholder: "添加评论"
      actions:
        - type: "Action.Submit"
          title: "批准"
          data:
            action: "approve"
```

### 会议自动化
```yaml
meeting_creation:
  subject: "每周站会"
  start: "2024-01-20T09:00:00"
  end: "2024-01-20T09:30:00"
  attendees:
    - "user1@company.com"
    - "user2@company.com"
  is_online_meeting: true
  settings:
    allow_new_time_proposals: true
    lobby_bypass: "organization"
    record_automatically: false
```

### 入站网关
```yaml
webhook_message:
  url: "https://outlook.webhook.office.com/..."
  payload:
    "@type": "MessageCard"
    themeColor: "0076D7"
    summary: "部署完成"
    sections:
      - activityTitle: "生产部署"
        activitySubtitle: "v2.1.0 部署成功"
        facts:
          - name: "环境"
            value: "生产"
          - name: "持续时间"
            value: "5分钟"
        markdown: true
    potentialAction:
      - "@type": "OpenUri"
        name: "查看仪表板"
        targets:
          - os: "default"
            uri: "https://dashboard.example.com"
```

### Bot 工作流
```yaml
bot_commands:
  /status:
    description: "检查系统状态"
    response:
      type: adaptive_card
      template: status_card
      
  /create-ticket:
    description: "创建支持工单"
    parameters:
      - title: required
      - priority: optional
    action: create_jira_issue
    
  /approve {id}:
    description: "批准请求"
    action: process_approval
    response: "请求 {{id}} 已批准 ✓"
```

## 集成工作流

### CI/CD 通知
```yaml
pipeline_notifications:
  on_build_start:
    channel: "#deployments"
    card:
      title: "🚀 构建开始"
      fields:
        - 分支: "{{branch}}"
        - 触发者: "{{user}}"
        
  on_build_complete:
    channel: "#deployments"
    card:
      title: "{{#if success}}✅{{else}}❌{{/if}} 构建 {{status}}"
      fields:
        - 持续时间: "{{duration}}"
        - 测试: "{{tests_passed}}/{{tests_total}}"
      actions:
        - title: "查看日志"
          url: "{{logs_url}}"
```

### 批准工作流
```yaml
approval_flow:
  trigger: expense_submitted
  actions:
    - send_adaptive_card:
        channel: "#approvals"
        card:
          title: "费用批准"
          body: "{{employee}} 提交了 ${{amount}}"
          actions:
            - 批准
            - 拒绝
    - wait_for_response:
        timeout: 48_hours
    - process_decision:
        approved: update_expense_status
        rejected: notify_submitter
```

## 最佳实践

1. **速率限制**：遵守 Microsoft Graph 限制
2. **自适应卡片**：用于丰富的交互
3. **权限**：请求最小权限范围
4. **线程**：在线程中回复以保持上下文
5. **提及**：谨慎使用 @提及
6. **网关**：用于单向通知
