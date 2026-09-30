---
name: openrouter-typescript-sdk
description: 通过 OpenRouter TypeScript SDK 使用 callModel 模式集成 300 多个 AI 模型的完整参考
---

# OpenRouter TypeScript SDK

一个用于与 OpenRouter 统一 API 交互的全面 TypeScript SDK，通过单一、类型安全的接口访问 300 多个 AI 模型。该技能使 AI 代理能够利用 `callModel` 模式进行文本生成、工具使用、流式传输和多轮对话。

---

## 安装

```bash
npm install @openrouter/sdk
```

## 设置

从 [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) 获取您的 API 密钥，然后初始化：

```typescript
import OpenRouter from '@openrouter/sdk';

const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});
```

---

## 认证

SDK 支持两种认证方法：适用于服务器端应用程序的 API 密钥和适用于面向用户应用程序的 OAuth PKCE 流程。

### API 密钥认证

主要的认证方法使用您 OpenRouter 账户中的 API 密钥。

#### 获取 API 密钥

1. 访问 [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
2. 创建一个新的 API 密钥
3. 安全地存储在环境变量中

#### 环境设置

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

#### 客户端初始化

```typescript
import OpenRouter from '@openrouter/sdk';

const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});
```

客户端自动使用此密钥进行所有后续请求：

```typescript
// API 密钥自动包含在内
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: 'Hello!'
});
```

#### 获取当前密钥元数据

检索当前配置的 API 密钥信息：

```typescript
const keyInfo = await client.apiKeys.getCurrentKeyMetadata();
console.log('Key name:', keyInfo.name);
console.log('Created:', keyInfo.createdAt);
```

#### API 密钥管理

程序化管理 API 密钥：

```typescript
// 列出所有密钥
const keys = await client.apiKeys.list();

// 创建一个新的密钥
const newKey = await client.apiKeys.create({
  name: 'Production API Key'
});

// 通过哈希获取特定密钥
const key = await client.apiKeys.get({
  hash: 'sk-or-v1-...'
});

// 更新密钥
await client.apiKeys.update({
  hash: 'sk-or-v1-...',
  requestBody: {
    name: 'Updated Key Name'
  }
});

// 删除密钥
await client.apiKeys.delete({
  hash: 'sk-or-v1-...'
});
```

### OAuth 认证（PKCE 流程）

对于用户端应用程序，其中用户应控制自己的 API 密钥，OpenRouter 支持使用 OAuth 和 PKCE（证明密钥交换）。此流程允许用户通过浏览器授权流程生成 API 密钥，而无需您的应用程序处理他们的凭证。

#### createAuthCode

生成授权代码和 URL 以启动 OAuth 流程：

```typescript
const authResponse = await client.oAuth.createAuthCode({
  callbackUrl: 'https://myapp.com/auth/callback'
});

// authResponse 包含：
// - authorizationUrl: 重定向用户到的 URL
// - code: 后续交换的授权代码

console.log('Redirect user to:', authResponse.authorizationUrl);
```

**参数：**

| 参数 | 类型 | 是否必需 | 描述 |
|-----------|------|----------|-------------|
| `callbackUrl` | `string` | 是 | 用户授权后的应用程序回调 URL |

**浏览器重定向：**

```typescript
// 在浏览器环境中
window.location.href = authResponse.authorizationUrl;

// 或在服务器渲染的应用程序中，返回重定向响应
res.redirect(authResponse.authorizationUrl);
```

#### exchangeAuthCodeForAPIKey

用户授权您的应用程序后，他们将被重定向回您的回调 URL，并带有授权代码。用此代码交换 API 密钥：

```typescript
// 在您的回调处理程序中
const code = req.query.code;  // 来自重定向 URL

const apiKeyResponse = await client.oAuth.exchangeAuthCodeForAPIKey({
  code: code
});

// apiKeyResponse 包含：
// - key: 用户的 API 密钥
// - 关于密钥的其他元数据

const userApiKey = apiKeyResponse.key;

// 安全地存储以供此用户未来的请求使用
await saveUserApiKey(userId, userApiKey);
```

**参数：**

| 参数 | 类型 | 是否必需 | 描述 |
|-----------|------|----------|-------------|
| `code` | `string` | 是 | OAuth 重定向的授权代码 |

#### 完整 OAuth 流程示例

```typescript
import OpenRouter from '@openrouter/sdk';
import express from 'express';

const app = express();
const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY  // 您应用程序的密钥，用于 OAuth 操作
});

// 第 1 步：启动 OAuth 流程
app.get('/auth/start', async (req, res) => {
  const authResponse = await client.oAuth.createAuthCode({
    callbackUrl: 'https://myapp.com/auth/callback'
  });

  // 存储回调所需的任何状态
  req.session.oauthState = { /* ... */ };

  // 重定向用户到 OpenRouter 授权页面
  res.redirect(authResponse.authorizationUrl);
});

// 第 2 步：处理回调并交换代码
app.get('/auth/callback', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    return res.status(400).send('缺少授权代码');
  }

  try {
    const apiKeyResponse = await client.oAuth.exchangeAuthCodeForAPIKey({
      code: code as string
    });

    // 安全地存储用户的 API 密钥
    await saveUserApiKey(req.session.userId, apiKeyResponse.key);

    res.redirect('/dashboard?auth=success');
  } catch (error) {
    console.error('OAuth 交换失败:', error);
    res.redirect('/auth/error');
  }
});

// 第 3 步：使用用户的 API 密钥进行他们的请求
app.post('/api/chat', async (req, res) => {
  const userApiKey = await getUserApiKey(req.session.userId);

  // 使用用户的密钥创建客户端
  const userClient = new OpenRouter({
    apiKey: userApiKey
  });

  const result = userClient.callModel({
    model: 'openai/gpt-5-nano',
    input: req.body.message
  });

  const text = await result.getText();
  res.json({ response: text });
});
```

### 安全最佳实践

1. **环境变量**：将 API 密钥存储在环境变量中，绝不在代码中
2. **密钥轮换**：使用密钥管理 API 定期轮换密钥
3. **环境分离**：为开发、测试和生产使用不同的密钥
4. **OAuth for Users**：使用 OAuth PKCE 流程为用户端应用程序，避免处理用户凭证
5. **安全存储**：在您的数据库中加密存储用户 API 密钥
6. **最小权限**：创建仅具有所需权限的密钥

---

## 核心概念：callModel

`callModel` 函数是文本生成的主要接口。它提供了一种统一的、类型安全的方法来与任何支持的模型交互。

### 基本用法

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '用一句话解释量子计算。'
});

const text = await result.getText();
```

### 主要优势

- **类型安全的参数**，具有完整的 IDE 自动补全
- **从 OpenAPI 规范自动生成** - 随新模型自动更新
- **多种消费模式** - 文本、流式传输、结构化数据
- **自动工具执行**，支持多轮对话

---

## 输入格式

SDK 接受灵活的输入类型作为 `input` 参数：

### 字符串输入
一个简单的字符串成为用户消息：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '你好，你好吗？'
});
```

### 消息数组
用于多轮对话：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: [
    { role: 'user', content: '法国的首都是什么？' },
    { role: 'assistant', content: '法国的首都是巴黎。' },
    { role: 'user', content: '它的人口是多少？' }
  ]
});
```

### 多模态内容
包括图像和文本：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: [
    {
      role: 'user',
      content: [
        { type: 'text', text: '这张图像中有什么？' },
        { type: 'image_url', image_url: { url: 'https://example.com/image.png' } }
      ]
    }
  ]
});
```

### 系统指令
使用 `instructions` 参数进行系统级指导：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  instructions: '你是一个有帮助的编程助手。要简洁。',
  input: '如何在 Python 中反转一个字符串？'
});
```

---

## 响应方法

结果对象提供多种方法来消费响应：

| 方法 | 目的 |
|--------|---------|
| `getText()` | 获取所有工具完成后完整的文本 |
| `getResponse()` | 带有令牌使用的完整响应对象 |
| `getTextStream()` | 按到达顺序流式传输文本增量 |
| `getReasoningStream()` | 流式传输推理令牌（对于 o1/reasoning 模型） |
| `getToolCallsStream()` | 按完成顺序流式传输工具调用 |

### getText()

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '写一首关于编程的俳句'
});

const text = await result.getText();
console.log(text);
```

### getResponse()

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '你好！'
});

const response = await result.getResponse();
console.log('文本:', response.text);
console.log('令牌使用:', response.usage);
```

### getTextStream()

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '写一个简短的故事'
});

for await (const delta of result.getTextStream()) {
  process.stdout.write(delta);
}
```

---

## 工具系统

使用 Zod 模式创建强类型工具，用于自动验证和类型推断。

### 定义工具

```typescript
import { tool } from '@openrouter/sdk';
import { z } from 'zod';

const weatherTool = tool({
  name: 'get_weather',
  description: '获取某个地点的当前天气',
  inputSchema: z.object({
    location: z.string().describe('城市名称'),
    units: z.enum(['celsius', 'fahrenheit']).optional().default('celsius')
  }),
  outputSchema: z.object({
    temperature: z.number(),
    conditions: z.string(),
    humidity: z.number()
  }),
  execute: async (params) => {
    // 实现天气获取逻辑
    return {
      temperature: 22,
      conditions: '晴朗',
      humidity: 45
    };
  }
});
```

### 使用工具与 callModel

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '巴黎的天气怎么样？',
  tools: [weatherTool]
});

const text = await result.getText();
// SDK 自动执行工具并继续对话
```

### 工具类型

#### 普通工具
标准执行函数返回结果：

```typescript
const calculatorTool = tool({
  name: 'calculate',
  description: '执行数学计算',
  inputSchema: z.object({
    expression: z.string()
  }),
  execute: async ({ expression }) => {
    return { result: eval(expression) };
  }
});
```

#### 生成器工具
使用 `eventSchema` 生成进度事件：

```typescript
const searchTool = tool({
  name: 'web_search',
  description: '搜索网络',
  inputSchema: z.object({ query: z.string() }),
  eventSchema: z.object({
    type: z.literal('progress'),
    message: z.string()
  }),
  outputSchema: z.object({ results: z.array(z.string()) }),
  execute: async function* ({ query }) {
    yield { type: 'progress', message: '正在搜索...' };
    yield { type: 'progress', message: '处理结果...' };
    return { results: ['结果 1', '结果 2'] };
  }
});
```

#### 手动工具
设置 `execute: false` 以自行处理工具调用：

```typescript
const manualTool = tool({
  name: 'user_confirmation',
  description: '请求用户确认',
  inputSchema: z.object({ message: z.string() }),
  execute: false
});
```

---

## 带停止条件的多轮对话

使用停止条件控制自动工具执行：

```typescript
import { stepCountIs, maxCost, hasToolCall } from '@openrouter/sdk';

const result = client.callModel({
  model: 'openai/gpt-5.2',
  input: '彻底研究这个主题',
  tools: [searchTool, analyzeTool],
  stopWhen: [
    stepCountIs(10),      // 10 轮后停止
    maxCost(1.00),        // 成本超过 $1.00 时停止
    hasToolCall('finish') // 调用 'finish' 工具时停止
  ]
});
```

### 可用的停止条件

| 条件 | 描述 |
|-----------|-------------|
| `stepCountIs(n)` | 10 轮后停止 |
| `maxCost(amount)` | 成本超过 amount 时停止 |
| `hasToolCall(name)` | 调用特定工具时停止 |

### 自定义停止条件

```typescript
const customStop = (context) => {
  return context.messages.length > 20;
};

const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '复杂任务',
  tools: [myTool],
  stopWhen: customStop
});
```

---

## 动态参数

根据对话上下文计算参数：

```typescript
const result = client.callModel({
  model: (ctx) => ctx.numberOfTurns > 3 ? 'openai/gpt-4' : 'openai/gpt-4o-mini',
  temperature: (ctx) => ctx.numberOfTurns > 1 ? 0.3 : 0.7,
  input: '你好！'
});
```

### 上下文对象属性

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `numberOfTurns` | number | 当前轮次数 |
| `messages` | array | 所有消息 |
| `instructions` | string | 当前系统指令 |
| `totalCost` | number | 累计成本 |

---

## nextTurnParams：上下文注入

工具可以修改后续轮次的参数，实现技能和上下文感知行为：

```typescript
const skillTool = tool({
  name: 'load_skill',
  description: '加载一个专业技能',
  inputSchema: z.object({
    skill: z.string().describe('要加载的技能名称')
  }),
  nextTurnParams: {
    instructions: (params, context) => {
      const skillInstructions = loadSkillInstructions(params.skill);
      return `${context.instructions}\n\n${skillInstructions}`;
    }
  },
  execute: async ({ skill }) => {
    return { loaded: skill };
  }
});
```

### nextTurnParams 的用例

- **技能系统**：动态加载专业能力
- **上下文累积**：在多轮中构建上下文
- **模式切换**：在对话中改变模型行为
- **记忆注入**：将检索到的上下文添加到指令中

---

## 生成参数

使用这些参数控制模型行为：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '写一个创意故事',
  temperature: 0.7,        // 创意性（0-2，默认因模型而异）
  maxOutputTokens: 1000,   // 生成最大令牌数
  topP: 0.9,               // 核心采样参数
  frequencyPenalty: 0.5,   // 减少重复
  presencePenalty: 0.5,    // 鼓励新主题
  stop: ['\n\n']           // 停止序列
});
```

---

## 流式传输

所有流式传输方法支持从单个结果对象中并发消费者：

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '写一个详细的解释'
});

// 消费者 1：将文本流到控制台
const textPromise = (async () => {
  for await (const delta of result.getTextStream()) {
    process.stdout.write(delta);
  }
})();

// 消费者 2：同时获取完整响应
const responsePromise = result.getResponse();

// 两者同时运行
const [, response] = await Promise.all([textPromise, responsePromise]);
console.log('\n\n总令牌数:', response.usage.totalTokens);
```

### 流式传输工具调用

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: '搜索有关 TypeScript 的信息',
  tools: [searchTool]
});

for await (const toolCall of result.getToolCallsStream()) {
  console.log(`调用了工具: ${toolCall.name}`);
  console.log(`参数: ${JSON.stringify(toolCall.arguments)}`);
  console.log(`结果: ${JSON.stringify(toolCall.result)}`);
}
```

---

## 格式转换

在生态系统格式之间转换以实现互操作性：

### OpenAI 格式

```typescript
import { fromChatMessages, toChatMessage } from '@openrouter/sdk';

// OpenAI 消息 → OpenRouter 格式
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: fromChatMessages(openaiMessages)
});

// 响应 → OpenAI 聊天消息格式
const response = await result.getResponse();
const chatMsg = toChatMessage(response);
```

### Claude 格式

```typescript
import { fromClaudeMessages, toClaudeMessage } from '@openrouter/sdk';

// Claude 消息 → OpenRouter 格式
const result = client.callModel({
  model: 'anthropic/claude-3-opus',
  input: fromClaudeMessages(claudeMessages)
});

// 响应 → Claude 消息格式
const response = await result.getResponse();
const claudeMsg = toClaudeMessage(response);
```

---

## 响应 API 消息形状

SDK 使用 **OpenResponses** 格式进行消息。理解这些形状对于构建健壮的代理至关重要。

### 消息角色

消息包含一个 `role` 属性，该属性决定消息类型：

| 角色 | 描述 |
|------|-------------|
| `user` | 用户提供的输入 |
| `assistant` | 模型生成的响应 |
| `system` | 系统指令 |
| `developer` | 开发者级指令 |
| `tool` | 工具执行结果 |

### 文本消息

来自用户或助手的简单文本内容：

```typescript
interface TextMessage {
  role: 'user' | 'assistant';
  content: string;
}
```

### 多模态消息（数组内容）

具有混合内容类型的消息：

```typescript
interface MultimodalMessage {
  role: 'user';
  content: Array<
    | { type: 'input_text'; text: string }
    | { type: 'input_image'; imageUrl: string; detail?: 'auto' | 'low' | 'high' }
    | {
        type: 'image';
        source: {
          type: 'url' | 'base64';
          url?: string;
          media_type?: string;
          data?: string
        }
      }
  >;
}
```

### 工具函数调用消息

当模型请求工具执行时：

```typescript
interface ToolCallMessage {
  role: 'assistant';
  content?: null;
  tool_calls?: Array<{
    id: string;
    type: 'function';
    function: {
      name: string;
      arguments: string;  // JSON 编码的参数
    };
  }>;
}
```

### 工具结果消息

工具执行后返回的结果：

```typescript
interface ToolResultMessage {
  role: 'tool';
  tool_call_id: string;
  content: string;  // JSON 编码的结果
}
```

### 非流式响应结构

来自 `getResponse()` 的完整响应对象：

```typescript
interface OpenResponsesNonStreamingResponse {
  output: Array<ResponseMessage>;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    cachedTokens?: number;
  };
  finishReason?: string;
  warnings?: Array<{
    type: string;
    message: string
  }>;
  experimental_providerMetadata?: Record<string, unknown>;
}
```

### 响应消息类型

响应数组中的输出消息：

```typescript
// 文本/内容消息
interface ResponseOutputMessage {
  type: 'message';
  role: 'assistant';
  content: string | Array<ContentPart>;
  reasoning?: string;  // 对于推理模型（o1 等）
}

// 输出中的工具调用
interface FunctionCallOutputMessage {
  type: 'function_call_output';
  call_id: string;
  output: string;
}
```

### 解析后的工具调用

当工具调用从响应中解析时：

```typescript
interface ParsedToolCall {
  id: string;
  name: string;
  arguments: unknown;  // 与 inputSchema 验证
}
```

### 工具执行结果

工具完成执行后：

```typescript
interface ToolExecutionResult {
  toolCallId: string;
  toolName: string;
  result: unknown;                  // 与 outputSchema 验证
  preliminaryResults?: unknown[];   // 来自生成器工具
  error?: Error;
}
```

### 步骤结果（用于停止条件）

在自定义停止条件回调中可用：

```typescript
interface StepResult {
  stepType: 'initial' | 'continue';
  text: string;
  toolCalls: ParsedToolCall[];
  toolResults: ToolExecutionResult[];
  response: OpenResponsesNonStreamingResponse;
  usage?: {
    inputTokens: number;
    outputTokens: number;
    cachedTokens?: number;
  };
  finishReason?: string;
  warnings?: Array<{ type: string; message: string }>;
  experimental_providerMetadata?: Record<string, unknown>;
}
```

### TurnContext

工具和动态参数函数可用：

```typescript
interface TurnContext {
  numberOfTurns: number;                     // 回合计数（1 索引）
  turnRequest?: OpenResponsesRequest;        // 当前正在进行的请求
  toolCall?: OpenResponsesFunctionToolCall;  // 当前工具调用（在工具上下文中）
}
```

---

## 事件形状

SDK 提供多种流式方法，生成不同的事件类型。

### 响应流事件

`getFullResponsesStream()` 方法生成这些事件类型：

```typescript
type EnhancedResponseStreamEvent =
  | ResponseCreatedEvent
  | ResponseInProgressEvent
  | OutputTextDeltaEvent
  | OutputTextDoneEvent
  | ReasoningDeltaEvent
  | ReasoningDoneEvent
  | FunctionCallArgumentsDeltaEvent
  | FunctionCallArgumentsDoneEvent
  | ResponseCompletedEvent
  | ToolPreliminaryResultEvent;
```

### 事件类型参考

| 事件类型 | 描述 | 有效负载 |
|------------|-------------|---------|
| `response.created` | 响应对象初始化 | `{ response: ResponseObject }` |
| `response.in_progress` | 生成已开始 | `{}` |
| `response.output_text.delta` | 接收文本块 | `{ delta: string }` |
| `response.output_text.done` | 文本生成完成 | `{ text: string }` |
| `response.reasoning.delta` | 推理块（o1 模型） | `{ delta: string }` |
| `response.reasoning.done` | 推理完成 | `{ reasoning: string }` |
| `response.function_call_arguments.delta` | 工具参数块 | `{ delta: string }` |
| `response.function_call_arguments.done` | 工具参数完成 | `{ arguments: string }` |
| `response.completed` | 完整响应完成 | `{ response: ResponseObject }` |
| `tool.preliminary_result` | 生成器工具进度 | `{ toolCallId: string; result: unknown }` |

### 文本增量事件

```typescript
interface OutputTextDeltaEvent {
  type: 'response.output_text.delta';
  delta: string;
}
```

### 推理增量事件

对于推理模型（o1 等）：

```typescript
interface ReasoningDeltaEvent {
  type: 'response.reasoning.delta';
  delta: string;
}
```

### 函数调用参数增量事件

```typescript
interface FunctionCallArgumentsDeltaEvent {
  type: 'response.function_call_arguments.delta';
  delta: string;
}
```

### 工具预览结果事件

来自生成器工具的进度：

```typescript
interface ToolPreliminaryResultEvent {
  type: 'tool.preliminary_result';
  toolCallId: string;
  result: unknown;  // 匹配工具的 eventSchema
}
```

### 响应完成事件

```typescript
interface ResponseCompletedEvent {
  type: 'response.completed';
  response: OpenResponsesNonStreamingResponse;
}
```

### 工具流事件

`getToolStream()` 方法生成：

```typescript
type ToolStreamEvent =
  | { type: 'delta'; content: string }
  | { type: 'preliminary_result'; toolCallId: string; result: unknown };
```

### 示例：处理流事件

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: 'Analyze this data',
  tools: [analysisTool]
});

for await (const event of result.getFullResponsesStream()) {
  switch (event.type) {
    case 'response.output_text.delta':
      process.stdout.write(event.delta);
      break;

    case 'response.reasoning.delta':
      console.log('[Reasoning]', event.delta);
      break;

    case 'response.function_call_arguments.delta':
      console.log('[Tool Args]', event.delta);
      break;

    case 'tool.preliminary_result':
      console.log(`[Progress: ${event.toolCallId}]`, event.result);
      break;

    case 'response.completed':
      console.log('\n[Complete]', event.response.usage);
      break;
  }
}
```

### 消息流事件

`getNewMessagesStream()` 生成 OpenResponses 格式更新：

```typescript
type MessageStreamUpdate =
  | ResponsesOutputMessage        // 文本/内容更新
  | OpenResponsesFunctionCallOutput;  // 工具结果
```

### 示例：跟踪新消息

```typescript
const result = client.callModel({
  model: 'openai/gpt-5-nano',
  input: 'Research this topic',
  tools: [searchTool]
});

const allMessages: MessageStreamUpdate[] = [];

for await (const message of result.getNewMessagesStream()) {
  allMessages.push(message);

  if (message.type === 'message') {
    console.log('Assistant:', message.content);
  } else if (message.type === 'function_call_output') {
    console.log('Tool result:', message.output);
  }
}
```

---

## API 参考

### 客户端方法

除了 `callModel`，客户端还提供对其他 API 端点的访问：

```typescript
const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});

// 列出可用模型
const models = await client.models.list();

// 聊天补全（替代 callModel）
const completion = await client.chat.send({
  model: 'openai/gpt-5-nano',
  messages: [{ role: 'user', content: 'Hello!' }]
});

// 遗留补全格式
const legacyCompletion = await client.completions.generate({
  model: 'openai/gpt-5-nano',
  prompt: 'Once upon a time'
});

// 使用分析
const activity = await client.analytics.getUserActivity();

// 信用余额
const credits = await client.credits.getCredits();

// API 密钥管理
const keys = await client.apiKeys.list();
```

---

## 错误处理

SDK 提供特定错误类型和可操作的错误消息：

```typescript
try {
  const result = await client.callModel({
    model: 'openai/gpt-5-nano',
    input: 'Hello!'
  });
  const text = await result.getText();
} catch (error) {
  if (error.statusCode === 401) {
    console.error('无效的 API 密钥 - 检查您的 OPENROUTER_API_KEY');
  } else if (error.statusCode === 402) {
    console.error('信用不足 - 在 openrouter.ai 添加信用');
  } else if (error.statusCode === 429) {
    console.error('速率限制 - 实现退避重试');
  } else if (error.statusCode === 503) {
    console.error('模型暂时不可用 - 重试或使用备用方案');
  } else {
    console.error('意外错误:', error.message);
  }
}
```

### 错误状态码

| 代码 | 含义 | 操作 |
|------|---------|--------|
| 400 | 请求错误 | 检查请求参数 |
| 401 | 未授权 | 验证 API 密钥 |
| 402 | 需要支付 | 添加信用 |
| 429 | 速率限制 | 实现指数退避 |
| 500 | 服务器错误 | 重试并使用退避 |
| 503 | 服务不可用 | 尝试替代模型 |

---

## 完整示例：带工具的代理

```typescript
import OpenRouter, { tool, stepCountIs } from '@openrouter/sdk';
import { z } from 'zod';

const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});

// 定义工具
const searchTool = tool({
  name: 'web_search',
  description: '在网络上搜索信息',
  inputSchema: z.object({
    query: z.string().describe('搜索查询')
  }),
  outputSchema: z.object({
    results: z.array(z.object({
      title: z.string(),
      snippet: z.string(),
      url: z.string()
    }))
  }),
  execute: async ({ query }) => {
    // 实现实际搜索
    return {
      results: [
        { title: '示例', snippet: '示例结果', url: 'https://example.com' }
      ]
    };
  }
});

const finishTool = tool({
  name: 'finish',
  description: '使用最终答案完成任务',
  inputSchema: z.object({
    answer: z.string().describe('最终答案')
  }),
  execute: async ({ answer }) => ({ answer })
});

// 运行代理
async function runAgent(task: string) {
  const result = client.callModel({
    model: 'openai/gpt-5-nano',
    instructions: '你是一个有帮助的研究助理。使用 web_search 查找信息，然后使用 finish 提供你的最终答案。',
    input: task,
    tools: [searchTool, finishTool],
    stopWhen: [
      stepCountIs(10),
      hasToolCall('finish')
    ]
  });

  // 流式处理进度
  for await (const toolCall of result.getToolCallsStream()) {
    console.log(`[${toolCall.name}] ${JSON.stringify(toolCall.arguments)}`);
  }

  return await result.getText();
}

// 使用
const answer = await runAgent('量子计算的最新发展是什么？');
console.log('最终答案:', answer);
```

---

## 最佳实践

### 1. 优先使用 callModel 而不是直接 API 调用
`callModel` 模式提供自动工具执行、类型安全和多回合处理。

### 2. 使用 Zod 进行工具模式
Zod 提供运行时验证和出色的 TypeScript 推断：

```typescript
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1),
  age: z.number().int().positive()
});
```

### 3. 实现停止条件
始终设置合理的限制以防止无限成本：

```typescript
stopWhen: [stepCountIs(20), maxCost(5.00)]
```

### 4. 优雅地处理错误
实现重试逻辑以处理瞬态故障：

```typescript
async function callWithRetry(params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await client.callModel(params).getText();
    } catch (error) {
      if (error.statusCode === 429 || error.statusCode >= 500) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw error;
    }
  }
}
```

### 5. 使用流式处理长响应
流式处理提供更好的用户体验并允许提前终止：

```typescript
for await (const delta of result.getTextStream()) {
  // 按增量处理
}
```

---

## 其他资源

- **API 密钥**：[openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
- **模型列表**：[openrouter.ai/models](https://openrouter.ai/models)
- **GitHub 问题**：[github.com/OpenRouterTeam/typescript-sdk/issues](https://github.com/OpenRouterTeam/typescript-sdk/issues)

---

*SDK 状态：Beta - 在 GitHub 上报告问题*
