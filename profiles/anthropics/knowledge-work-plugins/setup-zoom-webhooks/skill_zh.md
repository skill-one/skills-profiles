# /setup-zoom-webhooks

Zoom 事件通过 HTTP 传输的背景参考。建议先掌握工作流技能，然后使用此文件进行验证、订阅和交付详情。

## 前置条件

- 启用了事件订阅的 Zoom 应用
- 用于接收 webhooks 的 HTTPS 端点
- 用于验证的 webhook 密钥令牌

> **需要身份验证方面的帮助？** 请参阅 **[zoom-oauth](../oauth/SKILL.md)** 技能进行 OAuth 设置。

## 快速入门

```javascript
// Express.js webhook 处理器
const crypto = require('crypto');

// 捕获原始请求体以进行签名验证（避免重新序列化 JSON）。
app.use(require('express').json({
  verify: (req, _res, buf) => { req.rawBody = buf; }
}));

app.post('/webhook', (req, res) => {
  // 验证 webhook 签名
  const signature = req.headers['x-zm-signature'];
  const timestamp = req.headers['x-zm-request-timestamp'];
  const body = req.rawBody ? req.rawBody.toString('utf8') : JSON.stringify(req.body);
  const payload = `v0:${timestamp}:${body}`;
  const hash = crypto.createHmac('sha256', WEBHOOK_SECRET)
    .update(payload).digest('hex');
  
  if (signature !== `v0=${hash}`) {
    return res.status(401).send('Invalid signature');
  }

  // 处理事件
  const { event, payload } = req.body;
  console.log(`Received: ${event}`);
  
  res.status(200).send();
});
```

## 常见事件

| 事件 | 描述 |
|-------|-------------|
| `meeting.started` | 会议已开始 |
| `meeting.ended` | 会议已结束 |
| `meeting.participant_joined` | 参与者加入会议 |
| `recording.completed` | 云录制就绪 |
| `user.created` | 新用户添加 |

## 详细参考

- **[references/events.md](references/events.md)** - 完整的事件类型参考
- **[references/verification.md](references/verification.md)** - webhook URL 验证
- **[references/subscriptions.md](references/subscriptions.md)** - 事件订阅 API

## 故障排除

- **[RUNBOOK.md](RUNBOOK.md)** - 深入调试前的 5 分钟预检
- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - 签名验证、重试、URL 验证

## 示例仓库

### 官方（由 Zoom 提供）

| 类型 | 仓库 | 星标 |
|------|------------|-------|
| Node.js | [webhook-sample](https://github.com/zoom/webhook-sample) | 34 |
| PostgreSQL | [webhook-to-postgres](https://github.com/zoom/webhook-to-postgres) | 5 |
| Go/Fiber | [Go-Webhooks](https://github.com/zoom/Go-Webhooks) | - |
| Header Auth | [zoom-webhook-verification-headers](https://github.com/zoom/zoom-webhook-verification-headers) | - |

### 社区

| 语言 | 仓库 | 描述 |
|----------|------------|-------------|
| Laravel | [binary-cats/laravel-webhooks](https://github.com/binary-cats/laravel-webhooks) | Laravel webhook 处理器 |
| AWS Lambda | [splunk/zoom-webhook-to-hec](https://github.com/splunk/zoom-webhook-to-hec) | 无服务器到 Splunk HEC |
| Node.js | [Will4950/zoom-webhook-listener](https://github.com/Will4950/zoom-webhook-listener) | webhook 转发器 |
| Express+Redis | [ojusave/eventSubscriptionPlayground](https://github.com/ojusave/eventSubscriptionPlayground) | Socket.io + Redis |

### 多语言示例（由 tanchunsiong 提供）

| 语言 | 仓库 |
|----------|------------|
| Node.js | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-NodeJS](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-NodeJS) |
| C# | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-ASP.NET-Core-C-](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-ASP.NET-Core-C-) |
| Java | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Java-Spring-Boot](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Java-Spring-Boot) |
| Python | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Python](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Python) |
| PHP | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-PHP](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-PHP) |

**完整列表**: 查看 [general/references/community-repos.md](../general/references/community-repos.md)

## 资源

- **Webhook 文档**: https://developers.zoom.us/docs/api/webhooks/
- **事件参考**: https://developers.zoom.us/docs/api/rest/reference/zoom-api/events/
- **开发者论坛**: https://devforum.zoom.us/

## 环境变量

- 查看 [references/environment-variables.md](references/environment-variables.md) 以获取标准化的 `.env` 键以及每个值的查找位置。
