---
name: elevenlabs-agents
description: 在ElevenLabs平台上构建对话式AI语音代理。配置代理+工具+知识库，集成SDK（React / React Native / Swift / JS / 服务器端），测试，部署。当用户提及ElevenLabs、构建语音代理、AI电话系统、AI接待员、对话式AI，或排查过时@11labs包、webhook错误、CSP违规、localhost白名单或工具解析错误时使用。
---

# ElevenLabs Agent Builder

构建一个生产就绪的对话式 AI 语音代理。生成配置好的代理，包含工具、知识库和 SDK 集成。

## 包

```bash
npm install @elevenlabs/react           # React SDK
npm install @elevenlabs/client          # JavaScript SDK (浏览器 + 服务器)
npm install @elevenlabs/react-native    # React Native SDK
npm install @elevenlabs/elevenlabs-js   # 完整 API (仅限服务器)
npm install -g @elevenlabs/agents-cli   # CLI ("代理即代码")
```

**已弃用：** `@11labs/react`, `@11labs/client` -- 如果存在，请卸载。

**仅限服务器警告：** `@elevenlabs/elevenlabs-js` 使用 Node.js `child_process`，在浏览器中无法工作。在浏览器环境中使用 `@elevenlabs/client`，或创建一个代理服务器。

## 工作流程

### 第 1 步：通过控制面板或 CLI 创建代理

**控制面板：** https://elevenlabs.io/app/conversational-ai -> 创建代理

**CLI (代理即代码)：**
```bash
elevenlabs agents init
elevenlabs agents add "Support Bot" --template customer-service
# 编辑 agent_configs/support-bot.json
elevenlabs agents push --env dev
```

模板：`default`, `minimal`, `voice-only`, `text-only`, `customer-service`, `assistant`。

配置：
- **语音** -- 从 5000 多个语音中选择或克隆
- **LLM** -- GPT, Claude, Gemini 或自定义
- **系统提示** -- 使用下方的 6 组件框架
- **第一条消息** -- 代理在对话开始时说的话

### 第 2 步：编写系统提示

使用 6 组件框架编写有效的代理提示：

**1. 个性** -- 代理是谁：
```
你是 [NAME]，[ROLE] 在 [COMPANY]。
你有 [EXPERIENCE]。你的特质：[列特质]。
```

**2. 环境** -- 通信上下文：
```
你通过 [电话/聊天/视频] 进行通信。
考虑 [环境因素]。适应 [上下文]。
```

**3. 语气** -- 说话模式和正式程度：
```
语气：专业且温暖。使用缩写以实现自然对话。
避免术语。保持回复在 2-3 句话。一次只问一个问题。
```

**4. 目标** -- 目标和成功标准：
```
主要目标：在第一次通话中解决客户问题。
成功：客户口头确认问题已解决。
```

**5. 边界** -- 边界和道德规范：
```
绝不：提供医疗/法律/财务建议，分享机密信息。
始终：在访问账户前验证身份，记录交互。
升级：客户要求经理，问题超出知识库范围。
```

**6. 工具** -- 可用函数及其使用时机：
```
1. lookup_order(order_id) -- 当客户提到订单时使用。
2. transfer_to_supervisor() -- 当问题需要经理批准时使用。
始终在调用工具前解释你在做什么。
```

### 第 3 步：添加工具

**客户端工具（在浏览器中运行）：**

```typescript
const clientTools = {
  updateCart: {
    description: "向购物车添加或移除商品",
    parameters: z.object({
      action: z.enum(['add', 'remove']),
      item: z.string(),
      quantity: z.number().min(1)
    }),
    handler: async ({ action, item, quantity }) => {
      const cart = getCart();
      action === 'add' ? cart.add(item, quantity) : cart.remove(item, quantity);
      return { success: true, total: cart.total, items: cart.items.length };
    }
  },
  navigate: {
    description: "将用户导航到其他页面",
    parameters: z.object({ url: z.string().url() }),
    handler: async ({ url }) => { window.location.href = url; return { success: true }; }
  }
};
```

**服务器端工具（Webhooks）：**

```json
{
  "name": "get_weather",
  "description": "获取城市的当前天气",
  "url": "https://api.weather.com/v1/current",
  "method": "GET",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "城市名称" }
    },
    "required": ["city"]
  },
  "headers": {
    "Authorization": "Bearer {{secret__weather_api_key}}"
  }
}
```

使用 `{{secret__key_name}}` 在 webhook 头部中插入 API 密钥 -- 不要硬编码。

**MCP 工具 -- 关键兼容性说明：**

ElevenLabs 将其 MCP 集成标记为 "流式 HTTP"，但**不支持**实际的 MCP 2025-03-26 流式 HTTP 规范（SSE 响应）。ElevenLabs 需要的是：

- 纯 JSON 响应 (`application/json`)，不是 SSE (`text/event-stream`)
- 协议版本 `2024-11-05`，不是 `2025-03-26`
- 简单的 JSON-RPC over HTTP，直接返回 JSON 响应

什么**不**工作：
- 官方 MCP SDK 的 `createMcpHandler`（返回 SSE）
- Cloudflare Agents SDK `McpServer.serve()`（返回 SSE）
- 任何返回 `Content-Type: text/event-stream` 的服务器

适用于 ElevenLabs 的 MCP 服务器模式：

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';

const tools = [{
  name: "my_tool",
  description: "工具描述",
  inputSchema: {
    type: "object",
    properties: { param1: { type: "string", description: "描述" } },
    required: ["param1"]
  }
}];

async function handleMCPRequest(request, env) {
  const { id, method, params } = request;
  switch (method) {
    case 'initialize':
      return {
        jsonrpc: '2.0', id,
        result: {
          protocolVersion: '2024-11-05',  // **必须**是 2024-11-05
          serverInfo: { name: 'my-mcp', version: '1.0.0' },
          capabilities: { tools: {} }
        }
      };
    case 'tools/list':
      return { jsonrpc: '2.0', id, result: { tools } };
    case 'tools/call':
      const result = await handleTool(params.name, params.arguments, env);
      return { jsonrpc: '2.0', id, result };
    default:
      return { jsonrpc: '2.0', id, error: { code: -32601, message: `Unknown: ${method}` } };
  }
}

const app = new Hono();
app.use('/*', cors({ origin: '*', allowMethods: ['GET', 'POST', 'OPTIONS'] }));
app.post('/mcp', async (c) => {
  const body = await c.req.json();
  return c.json(await handleMCPRequest(body, c.env));  // 纯 JSON，不是 SSE
});
export default app;
```

### 第 4 步：添加知识库（RAG）

上传代理参考的文档：
- PDF、文本文件、网页 URL
- 通过控制面板配置：代理 -> 知识库 -> 上传
- 或通过 API：`POST /v1/convai/knowledge-base/upload`（multipart/form-data）
- 代理在对话期间自动搜索知识库

### 第 5 步：集成 SDK

**React** -- 复制并自定义 `assets/react-sdk-boilerplate.tsx`：

```typescript
import { useConversation } from '@elevenlabs/react';

const { startConversation, stopConversation, status } = useConversation({
  agentId: 'your-agent-id',
  signedUrl: '/api/elevenlabs/auth',
  clientTools,
  dynamicVariables: {
    user_name: 'John',
    account_type: 'premium',
  },
  onEvent: (event) => { /* transcript, agent_response, tool_call */ },
});
```

系统提示引用动态变量为 `{{user_name}}`。

**React Native** -- 查看 `assets/react-native-boilerplate.tsx`
**组件嵌入** -- 查看 `assets/widget-embed-template.html`
**Swift** -- 查看 `assets/swift-sdk-boilerplate.swift`

### 第 6 步：测试

**CLI 测试：**

```bash
# 运行代理的所有测试
elevenlabs agents test "Support Agent"

# 添加测试场景
elevenlabs tests add "Refund Request" --template basic-llm
```

**测试配置：**

```json
{
  "name": "Refund Request Test",
  "scenario": "客户请求退货，产品有缺陷",
  "user_input": "我想退订单 #12345。产品到了是坏的。",
  "成功标准": [
    "代理富有同情心地确认问题",
    "代理询问或使用提供的订单号",
    "代理验证订单详情",
    "代理提供清晰的下一步操作或退款时间表"
  ],
  "评估类型": "llm"
}
```

**工具调用测试：**

```json
{
  "name": "Order Lookup Test",
  "scenario": "客户询问订单状态",
  "user_input": "订单 ORD-12345 的状态是什么？",
  "预期工具调用": {
    "tool_name": "lookup_order",
    "parameters": { "order_id": "ORD-12345" }
  }
}
```

**API 模拟：**

```typescript
const simulation = await client.agents.simulate({
  agent_id: 'agent_123',
  scenario: '客户请求退货',
  user_messages: [
    "我想退订单 #12345",
    "它是坏的",
    "是的，处理退款"
  ],
  成功标准: [
    "代理表现出同情",
    "代理验证订单",
    "代理提供时间表"
  ]
});
console.log('通过：', simulation.passed);
```

**CI/CD 集成：**

```yaml
name: 测试代理
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g @elevenlabs/cli
      - run: elevenlabs tests push
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
      - run: elevenlabs agents test "Support Agent"
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
```

### 第 7 步：部署

```bash
# 先干跑（总是）
elevenlabs agents push --env prod --dry-run

# 部署到生产
elevenlabs agents push --env prod
```

多环境工作流程：
```bash
elevenlabs agents push --env dev       # 开发环境
elevenlabs agents push --env staging   # 测试环境
elevenlabs agents test "Agent Name"    # 在测试环境中测试
elevenlabs agents push --env prod      # 生产环境
```

---

## 关键模式

### 签名 URL（安全性）

不要在客户端代码中暴露 API 密钥。使用服务器端端点：

```typescript
app.get('/api/elevenlabs/auth', async (req, res) => {
  const response = await fetch(
    'https://api.elevenlabs.io/v1/convai/conversation/get-signed-url',
    {
      headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY },
      body: JSON.stringify({ agent_id: 'your-agent-id' }),
      method: 'POST'
    }
  );
  const { signed_url } = await response.json();
  res.json({ signed_url });
});
```

### 代理版本控制（A/B 测试）

控制面板：代理 -> 版本 -> 创建分支。比较指标，推广获胜者。

### 通话后 Webhook

```json
{
  "type": "post_call_transcription",
  "data": {
    "conversation_id": "conv_xyz789",
    "transcript": "...",
    "duration_seconds": 120,
    "analysis": { "sentiment": "positive", "resolution": true }
  }
}
```

使用 HMAC SHA-256 验证：
```typescript
const hmac = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET)
  .update(JSON.stringify(request.body)).digest('hex');
if (signature !== hmac) { /* 拒绝 */ }
```

---

## 成本优化

模型阵容和价格快速变化 — 在选择前，检查 ElevenLabs 控制面板（代理 → LLM 下拉菜单）或文档中的实时列表，并且不要硬编码未在本会话中验证的模型 ID。耐用的选择：为大多数代理使用当前廉价快速模型（仅在质量要求时升级），当知识库较大时使用长上下文模型。

主要节省：
- **LLM 缓存**：重复提示最高可节省 90%（在配置中启用）
- **提示长度**：150 个 token > 500 个 token 用于相同指令
- **RAG 超过上下文**：使用知识库而不是填充系统提示
- **持续时间限制**：设置 `max_duration_seconds` 以防止失控对话
- **回合模式**："耐心"模式 = 更少 LLM 调用 = 更低成本

---

## CLI 快速参考

```bash
elevenlabs auth login                              # 认证
elevenlabs agents init                             # 初始化项目
elevenlabs agents add "Name" --template default    # 添加代理
elevenlabs agents push --env dev                   # 部署到开发环境
elevenlabs agents push --env prod --dry-run        # 预览生产部署
elevenlabs agents push --env prod                  # 部署到生产环境
elevenlabs agents pull                             # 从平台拉取
elevenlabs agents test "Name"                      # 运行测试
elevenlabs agents list                             # 列出代理
elevenlabs agents status                           # 检查同步状态
elevenlabs agents widget "Name"                    # 生成组件
elevenlabs tools add-webhook "Name" --config-path tool.json  # 添加工具
elevenlabs tests add "Name" --template basic-llm   # 添加测试
```

环境：`ELEVENLABS_API_KEY` 用于 CI/CD。

---

## 可选参考

针对特殊用例，请参阅：
- `references/api-reference.md` -- 完整的 REST API 用于程序化代理管理
- `references/compliance-guide.md` -- GDPR、HIPAA、PCI DSS、数据驻留
- `references/workflow-examples.md` -- 多代理路由、升级、多语言

---

## 资产文件

- `assets/react-sdk-boilerplate.tsx` -- React 集成模板
- `assets/react-native-boilerplate.tsx` -- React Native 模板
- `assets/swift-sdk-boilerplate.swift` -- Swift/iOS 模板
- `assets/javascript-sdk-boilerplate.js` -- 纯 JavaScript 模板
- `assets/widget-embed-template.html` -- 可嵌入组件
- `assets/system-prompt-template.md` -- 系统提示指南
- `assets/agent-config-schema.json` -- 配置模式参考
- `assets/ci-cd-example.yml` -- CI/CD 管道模板
