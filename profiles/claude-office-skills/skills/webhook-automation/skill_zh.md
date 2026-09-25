# Webhook 自动化

全面的技能，用于构建基于 webhook 的集成和实时事件处理。

## 核心概念

### webhook 架构

```
WEBHOOK 流程:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   源系统    │────▶│   webhook  │────▶│   处理逻辑  │
│   系统     │     │   端点     │     │   逻辑     │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼───────┐
                    │                          │       │
                    ▼                          ▼       ▼
              ┌──────────┐              ┌──────────┐ ┌──────────┐
              │  动作 A  │              │  动作 B  │ │  动作 C  │
              │    A     │              │    B     │ │    C     │
              └──────────┘              └──────────┘ └──────────┘
```

### webhook 类型

```yaml
webhook_types:
  incoming:
    description: "接收外部服务的事件"
    用例:
      - 支付通知 (Stripe, PayPal)
      - 表单提交
      - CRM 更新
      - CI/CD 事件
      
  outgoing:
    description: "向外部服务发送事件"
    用例:
      - 通知外部系统
      - 触发工作流
      - 同步数据
      - 提醒集成
```

## webhook 端点设置

### 基本端点

```yaml
webhook_endpoint:
  url: "https://api.example.com/webhooks/incoming"
  method: POST
  
  认证:
    类型: 签名
    header: "X-Signature-256"
    算法: "HMAC-SHA256"
    密钥: "${WEBHOOK_SECRET}"
    
  验证:
    必要头:
      - "Content-Type"
      - "X-Request-ID"
    内容类型:
      - "application/json"
      - "application/x-www-form-urlencoded"
      
  响应:
    成功:
      状态: 200
      正文: { "received": true }
    错误:
      状态: 400
      正文: { "error": "无效的负载" }
```

### 签名验证

```javascript
// 验证 webhook 签名
function verifySignature(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(digest),
    Buffer.from(signature)
  );
}

// 使用
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-signature-256'];
  const payload = JSON.stringify(req.body);
  
  if (!verifySignature(payload, signature, process.env.WEBHOOK_SECRET)) {
    return res.status(401).json({ error: '无效的签名' });
  }
  
  // 处理 webhook...
  processWebhook(req.body);
  res.status(200).json({ received: true });
});
```

## 事件处理

### 事件路由器

```yaml
event_router:
  路由:
    - event_type: "payment.succeeded"
      处理器: processPayment
      动作:
        - update_order_status
        - send_confirmation_email
        - notify_fulfillment
        
    - event_type: "customer.created"
      处理器: processNewCustomer
      动作:
        - create_crm_contact
        - send_welcome_email
        - assign_to_sales
        
    - event_type: "subscription.cancelled"
      处理器: processChurn
      动作:
        - update_subscription_status
        - trigger_retention_flow
        - notify_customer_success
        
    - event_type: "*"
      处理器: logUnhandled
      动作:
        - log_to_monitoring
```

### 负载转换

```yaml
transformations:
  - name: stripe_to_internal
    源: stripe_webhook
    目标: internal_order
    映射:
      id: "data.object.id"
      amount: "data.object.amount / 100"  # 分到美元
      currency: "data.object.currency | uppercase"
      customer_email: "data.object.receipt_email"
      created_at: "data.object.created | timestamp"
      metadata: "data.object.metadata"
      
  - name: github_to_slack
    源: github_webhook
    目标: slack_message
    映射:
      text: |
        *{{action | capitalize}} {{repository.name}}*
        {{#if pull_request}}
        PR: {{pull_request.title}}
        By: {{pull_request.user.login}}
        {{/if}}
      channel: "{{repository.name}}-notifications"
```

## 常见集成

### Stripe webhook

```yaml
stripe_webhooks:
  endpoint_secret: "${STRIPE_WEBHOOK_SECRET}"
  
  事件:
    - type: "checkout.session.completed"
      处理器: |
        async function(event) {
          const session = event.data.object;
          await fulfillOrder(session);
          await sendReceipt(session.customer_email);
        }
        
    - type: "invoice.payment_failed"
      处理器: |
        async function(event) {
          const invoice = event.data.object;
          await notifyCustomer(invoice);
          await createDunningTask(invoice);
        }
        
    - type: "customer.subscription.updated"
      处理器: |
        async function(event) {
          const subscription = event.data.object;
          await syncSubscriptionStatus(subscription);
        }
```

### GitHub webhook

```yaml
github_webhooks:
  secret: "${GITHUB_WEBHOOK_SECRET}"
  
  事件:
    - type: "push"
      分支: ["main", "develop"]
      处理器: |
        async function(event) {
          await triggerCI(event.repository, event.ref);
          await notifyTeam(event.commits);
        }
        
    - type: "pull_request"
      动作: ["opened", "synchronize"]
      处理器: |
        async function(event) {
          await runTests(event.pull_request);
          await requestReview(event.pull_request);
        }
        
    - type: "issues"
      动作: ["opened"]
      处理器: |
        async function(event) {
          await triageIssue(event.issue);
          await assignOwner(event.issue);
        }
```

### Slack webhook

```yaml
slack_webhooks:
  incoming:
    # 接收斜杠命令和交互
    signing_secret: "${SLACK_SIGNING_SECRET}"
    
    事件:
      - type: "slash_command"
        command: "/deploy"
        处理器: handleDeployCommand
        
      - type: "interactive_message"
        callback_id: "approval_*"
        处理器: handleApproval
        
  outgoing:
    # 向 Slack 发送消息
    webhook_url: "${SLACK_WEBHOOK_URL}"
    
    模板:
      alert:
        blocks:
          - type: section
            text: "🚨 *Alert:* {{message}}"
          - type: context
            elements:
              - type: mrkdwn
                text: "源: {{source}} | 时间: {{timestamp}}"
```

## 错误处理

### 重试策略

```yaml
retry_config:
  启用: true
  
  策略:
    最大尝试: 5
    初始延迟: 1000  # ms
    最大延迟: 60000  # ms
    退避乘数: 2
    
  重试条件:
    状态码: [408, 429, 500, 502, 503, 504]
    异常: ["ECONNRESET", "ETIMEDOUT"]
    
  死信队列:
    启用: true
    目的地: "failed_webhooks_queue"
    保留天数: 7
```

### 错误日志

```yaml
error_handling:
  日志:
    级别: error
    包含:
      - request_id
      - event_type
      - payload_hash
      - error_message
      - stack_trace
      - retry_count
      
  报警:
    失败时:
      - 类型: slack
        频道: "#webhook-alerts"
        阈值: 5  # 每分钟失败次数
        
    死信时:
      - 类型: pagerduty
        严重性: warning
```

## webhook 测试

### 测试负载生成器

```yaml
test_payloads:
  stripe_payment:
    type: "checkout.session.completed"
    数据:
      object:
        id: "cs_test_123"
        amount_total: 2000
        currency: "usd"
        customer_email: "test@example.com"
        payment_status: "paid"
        
  github_push:
    ref: "refs/heads/main"
    repository:
      name: "my-repo"
      full_name: "org/my-repo"
    提交:
      - id: "abc123"
        消息: "测试提交"
        作者:
          name: "测试用户"
```

### webhook 调试

```yaml
debugging:
  工具:
    - name: "Request Bin"
      url: "https://requestbin.com"
      使用: "捕获和检查负载"
      
    - name: "ngrok"
      命令: "ngrok http 3000"
      使用: "暴露本地服务器"
      
    - name: "Webhook.site"
      url: "https://webhook.site"
      使用: "快速 webhook 测试"
      
  日志:
    启用: true
    记录负载: true
    记录头: true
    掩码密钥: true
```

## 安全最佳实践

### 安全检查清单

```yaml
security:
  认证:
    - 验证 webhook 签名
    - 仅使用 HTTPS
    - 定期轮换密钥
    
  验证:
    - 验证负载模式
    - 检查时间戳新鲜度
    - 如可能验证源 IP
    
  处理:
    - 等幂处理器
    - 速率限制
    - 超时保护
    
  存储:
    - 静态加密密钥
    - 审计日志
    - URL 中不包含敏感数据
```

### IP 白名单

```yaml
ip_allowlist:
  stripe:
    - "3.18.12.63"
    - "3.130.192.231"
    # ... 更多 IP
    
  github:
    - "192.30.252.0/22"
    - "185.199.108.0/22"
    # ... 更多范围
    
  slack:
    - "54.159.240.0/22"
    # ... 更多范围
```

## 监控

### 指标仪表板

```
WEBHOOK 指标 - 过去 24 小时
═══════════════════════════════════════

接收:      12,456
处理:     12,398 (99.5%)
失败:           58 (0.5%)
重试:         123

按源:
Stripe     ████████████░░░░ 5,230
GitHub     ██████████░░░░░░ 4,120
Slack      ████░░░░░░░░░░░░ 1,850
其他      ███░░░░░░░░░░░░░ 1,256

延迟 (p99):
处理: 245ms
响应:   52ms

错误分解:
超时:       25
无效签名:   18
解析错误:   10
速率限制:   5
```

## 最佳实践

1. **快速响应**: 立即返回 200，异步处理
2. **等幂性**: 优雅处理重复事件
3. **验证签名**: 始终验证 webhook 真实性
4. **记录所有操作**: 维持审计轨迹
5. **重试逻辑**: 实现指数退避
6. **死信队列**: 不要丢失失败事件
7. **速率限制**: 防止洪泛攻击
8. **监控**: 失败和延迟时报警
