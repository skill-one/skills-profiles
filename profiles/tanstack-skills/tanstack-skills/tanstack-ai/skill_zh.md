## 概述

TanStack AI 是一个模块化、提供者无关的 AI SDK，具有可树摇动的 OpenAI、Anthropic、Gemini、Ollama 等适配器。它提供流式优先的文本生成、带审批流程的工具调用、使用 Zod 模式的结构化输出、多模态内容支持，以及用于聊天/完成 UI 的 React 钩子。

**核心：** `@tanstack/ai`
**纯客户端：** `@tanstack/ai-client`（框架无关）
**React：** `@tanstack/ai-react`
**Solid：** `@tanstack/ai-solid`
**适配器：** `@tanstack/ai-openai`, `@tanstack/ai-anthropic`, `@tanstack/ai-gemini`, `@tanstack/ai-ollama`
**语言：** TypeScript/JavaScript, PHP, Python
**状态：** Alpha

## 安装

```bash
npm install @tanstack/ai @tanstack/ai-react
# 或用于框架无关的纯客户端：
npm install @tanstack/ai @tanstack/ai-client
# 提供者适配器（仅安装所需的）：
npm install @tanstack/ai-openai
npm install @tanstack/ai-anthropic
npm install @tanstack/ai-gemini
npm install @tanstack/ai-ollama
```

### PHP 安装

```bash
composer require tanstack/ai tanstack/ai-openai
```

### Python 安装

```bash
pip install tanstack-ai tanstack-ai-openai
```

## 核心：generate()

```typescript
import { generate } from '@tanstack/ai'
import { openaiText } from '@tanstack/ai-openai/adapters'

const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Explain React hooks in 3 sentences.' },
  ],
})

// 流式传输与异步迭代
for await (const chunk of result) {
  process.stdout.write(chunk.text)
}
```

## 提供者适配器

```typescript
import { openaiText } from '@tanstack/ai-openai/adapters'
import { anthropicText } from '@tanstack/ai-anthropic/adapters'
import { geminiText } from '@tanstack/ai-gemini/adapters'
import { ollamaText } from '@tanstack/ai-ollama/adapters'

// OpenAI
const openai = openaiText({ model: 'gpt-4o' })

// Anthropic
const anthropic = anthropicText({ model: 'claude-sonnet-4-20250514' })

// Google Gemini
const gemini = geminiText({ model: 'gemini-pro' })

// Ollama（本地）
const ollama = ollamaText({ model: 'llama3' })

// 运行时适配器切换
const adapter = process.env.AI_PROVIDER === 'anthropic' ? anthropic : openai
```

## React 钩子

### useChat

```tsx
import { useChat } from '@tanstack/ai-react'

function ChatUI() {
  const { messages, input, setInput, handleSubmit, isLoading } = useChat({
    adapter: openaiText({ model: 'gpt-4o' }),
  })

  return (
    <div>
      {messages.map((msg) => (
        <div key={msg.id}>
          <strong>{msg.role}:</strong> {msg.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
        />
        <button type="submit" disabled={isLoading}>
          发送
        </button>
      </form>
    </div>
  )
}
```

### useCompletion

```tsx
import { useCompletion } from '@tanstack/ai-react'

function CompletionUI() {
  const { completion, input, setInput, handleSubmit, isLoading } = useCompletion({
    adapter: openaiText({ model: 'gpt-4o' }),
  })

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入提示..."
        />
        <button type="submit" disabled={isLoading}>生成</button>
      </form>
      {completion && <div>{completion}</div>}
    </div>
  )
}
```

## Solid.js 钩子

```tsx
import { createChat } from '@tanstack/ai-solid'

function ChatUI() {
  const chat = createChat({
    adapter: openaiText({ model: 'gpt-4o' }),
  })

  return (
    <div>
      <For each={chat.messages()}>
        {(msg) => (
          <div>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        )}
      </For>
      <form onSubmit={chat.handleSubmit}>
        <input
          value={chat.input()}
          onInput={(e) => chat.setInput(e.target.value)}
          placeholder="输入消息..."
        />
        <button type="submit" disabled={chat.isLoading()}>
          发送
        </button>
      </form>
    </div>
  )
}
```

## 纯客户端

用于无需 React 或 Solid 的框架无关使用：

```typescript
import { createAIClient } from '@tanstack/ai-client'
import { openaiText } from '@tanstack/ai-openai/adapters'

const client = createAIClient({
  adapter: openaiText({ model: 'gpt-4o' }),
})

// 订阅状态变化
client.subscribe((state) => {
  console.log('消息:', state.messages)
  console.log('加载中:', state.isLoading)
})

// 发送消息
await client.send('你好，世界！')

// 清除对话
client.clear()
```

## 流式传输

### 流式传输策略

```typescript
import { generate } from '@tanstack/ai'

// 默认：按到达顺序流式传输块
const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [...],
  stream: true,
})

for await (const chunk of result) {
  // 处理每个块
  console.log(chunk.text)
}
```

可用的流式传输策略：
- **批量** - 在传输前收集所有块
- **标点符号** - 在句子边界流式传输
- **单词边界** - 在单词边界流式传输
- **组合** - 组合多个策略

### 服务器发送事件 (SSE)

```typescript
// 服务器端 SSE 端点
import { createReplayStream } from '@tanstack/ai'

export async function handler(req: Request) {
  const stream = createReplayStream({
    adapter: openaiText({ model: 'gpt-4o' }),
    messages: await req.json(),
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

## 结构化输出

```typescript
import { generate } from '@tanstack/ai'
import { convertZodToJsonSchema } from '@tanstack/ai'
import { z } from 'zod'

const RecipeSchema = z.object({
  name: z.string(),
  ingredients: z.array(z.object({
    item: z.string(),
    amount: z.string(),
  })),
  steps: z.array(z.string()),
  cookTime: z.number(),
})

const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [{ role: 'user', content: '给我一个意面食谱' }],
  schema: convertZodToJsonSchema(RecipeSchema),
})

// result 类型为 z.infer<typeof RecipeSchema>
console.log(result.name, result.ingredients)
```

## 工具调用

### 基本工具

```typescript
import { generate } from '@tanstack/ai'

const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [{ role: 'user', content: '纽约的天气如何?' }],
  tools: {
    getWeather: {
      description: '获取某个位置的天气',
      parameters: z.object({
        location: z.string(),
        unit: z.enum(['celsius', 'fahrenheit']).optional(),
      }),
      execute: async ({ location, unit }) => {
        const data = await fetchWeather(location, unit)
        return data
      },
    },
  },
})
```

### 带审批流程的工具调用

```typescript
import { ToolCallManager } from '@tanstack/ai'

const manager = new ToolCallManager({
  tools: {
    deleteUser: {
      description: '删除用户账户',
      parameters: z.object({ userId: z.string() }),
      requiresApproval: true, // 需要人工审批
      execute: async ({ userId }) => {
        await deleteUser(userId)
        return { success: true }
      },
    },
  },
  onApprovalRequired: async (toolCall) => {
    // 向用户展示审批界面
    return await showApprovalDialog(toolCall)
  },
})
```

### 代理循环

```typescript
const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [{ role: 'user', content: '研究和总结这个主题' }],
  tools: { search, summarize, writeReport },
  maxIterations: 10, // 限制代理循环迭代次数
})
```

## 多模态内容

```typescript
// 图片
const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: '这张图片里有什么?' },
      { type: 'image_url', image_url: { url: 'https://example.com/photo.jpg' } },
    ],
  }],
})

// 使用 DALL-E 生成图片
import { openaiImage } from '@tanstack/ai-openai/adapters'

const image = await generate({
  adapter: openaiImage({ model: 'dall-e-3' }),
  messages: [{ role: 'user', content: '山脉日落' }],
})

// 使用 Gemini Imagen 生成图片
import { geminiImage } from '@tanstack/ai-gemini/adapters'

const image = await generate({
  adapter: geminiImage({ model: 'imagen-3' }),
  messages: [{ role: 'user', content: '夜晚的未来城市景观' }],
})
```

## 思考模型（推理令牌）

支持具有扩展推理/思考能力的模型：

```typescript
import { generate } from '@tanstack/ai'
import { anthropicText } from '@tanstack/ai-anthropic/adapters'

const result = await generate({
  adapter: anthropicText({ model: 'claude-sonnet-4-20250514' }),
  messages: [{ role: 'user', content: '逐步解决这个复杂的数学问题...' }],
  thinking: {
    enabled: true,
    budget: 10000, // 最大思考令牌数
  },
})

// 访问思考/推理输出
console.log('思考:', result.thinking)
console.log('回复:', result.text)

// 带思考令牌的流式传输
for await (const chunk of result) {
  if (chunk.type === 'thinking') {
    console.log('[思考]', chunk.text)
  } else {
    process.stdout.write(chunk.text)
  }
}
```

## 消息工具

```typescript
import { generateMessageId, normalizeToUIMessage } from '@tanstack/ai'

// 生成唯一消息 ID
const id = generateMessageId()

// 将提供者特定消息转换为 UI 格式
const uiMessage = normalizeToUIMessage(providerMessage)
```

## 可观察性

```typescript
const result = await generate({
  adapter: openaiText({ model: 'gpt-4o' }),
  messages: [...],
  onEvent: (event) => {
    // 结构化、类型的事件
    switch (event.type) {
      case 'text':
        console.log('文本块:', event.data)
        break
      case 'tool_call':
        console.log('调用了工具:', event.name)
        break
      case 'error':
        console.error('错误:', event.error)
        break
    }
  },
})
```

## AI 开发工具

TanStack AI 包含一个专用的开发工具面板用于调试 AI 工作流：

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { AIDevtoolsPanel } from '@tanstack/ai-react/devtools'

function App() {
  return (
    <TanStackDevtools
      plugins={[
        {
          id: 'ai',
          name: 'AI',
          render: () => <AIDevtoolsPanel />,
        },
      ]}
    />
  )
}
```

AI 开发工具功能：
- **消息检查器** - 查看完整对话历史和元数据
- **令牌使用情况** - 跟踪输入/输出令牌和每次请求的成本
- **流式传输可视化** - 实时查看流式传输块
- **工具调用调试** - 检查工具调用、参数和结果
- **思考/推理查看器** - 调试思考模型的推理令牌
- **适配器切换** - 在开发中测试不同的提供者
- **请求/响应日志** - 完整的 HTTP 请求/响应检查

## TanStack Start 集成

```typescript
// AI 工具和服务器函数之间的共享实现
import { createServerFn } from '@tanstack/react-start'
import { generate } from '@tanstack/ai'

const aiChat = createServerFn({ method: 'POST' })
  .validator(z.object({ messages: z.array(messageSchema) }))
  .handler(async ({ data }) => {
    const result = await generate({
      adapter: openaiText({ model: 'gpt-4o' }),
      messages: data.messages,
    })
    return result
  })
```

## 部分JSON解析器

用于流式传输逐步到达的结构化输出：

```typescript
import { parsePartialJson } from '@tanstack/ai'

// 在流式传输过程中解析不完整的 JSON
const partial = parsePartialJson('{"name": "Pasta", "ingredients": [{"item": "flour"')
// 返回: { name: "Pasta", ingredients: [{ item: "flour" }] }
```

## 最佳实践

1. **仅导入所需的适配器** - 树摇动设计最小化包大小
2. **使用结构化输出** 与 Zod 模式，用于类型安全的 AI 响应
3. **设置 `maxIterations`** 在代理循环上，防止无限执行
4. **使用 `requiresApproval`** 对于破坏性工具调用
5. **优雅地处理流式传输错误** 在异步迭代周围使用 try/catch
6. **使用服务器函数** 用于 API 密钥安全（切勿在客户端暴露密钥）
7. **使用 `onEvent`** 用于开发中的可观察性和调试
8. **在运行时切换适配器** 用于 A/B 测试或回退策略
9. **使用部分 JSON 解析** 用于流式传输期间的渐进式 UI 更新
10. **规范化消息** 在切换提供者之间

## 常见陷阱

- 在客户端代码中暴露 API 密钥（使用服务器函数）
- 不处理流式传输错误（异步迭代可能会抛出异常）
- 忘记代理循环中的 `maxIterations`（可能会无限运行）
- 导入所有适配器而不是仅导入所需的（包膨胀）
- 不使用结构化输出进行数据提取（不可靠的字符串解析）
- 在每次渲染时创建新的适配器实例（memoize 或在模块级别定义）
