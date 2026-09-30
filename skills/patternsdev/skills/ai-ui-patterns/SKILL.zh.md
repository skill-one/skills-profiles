---
name: ai-ui-patterns
description: 教授用于构建人工智能驱动 React 界面的设计模式。在创建聊天机器人、智能助手、流式 UI 或任何 React 中的 AI 驱动用户体验时使用。
---

# AI UI 模式

## 目录

- [何时使用](#何时使用)
- [说明](#说明)
- [详情](#详情)
- [来源](#来源)

构建 AI 驱动的界面——从聊天机器人到智能助手——需要将后端 AI 服务与响应式 UI 组件进行仔细集成。在本章中，我们探讨了适用于此类界面的 React 设计模式，重点关注**两种实现方式**：一个纯 React 应用（使用 Vite）和一个 Next.js 应用。我们将使用 **OpenAI 的 API**（通过 Vercel AI SDK）作为我们的 AI 引擎，并使用 TailwindCSS 进行样式设计。关键主题包括提示管理、流式响应、输入防抖、错误处理以及 Vite 和 Next.js 之间这些模式的差异。我们还重点介绍了可重用组件模式以及 **Vercel 的 AI UI 组件（AI Elements）**，用于构建精致的聊天界面。

## 何时使用

- 在构建从大型语言模型（LLM）流式传输响应的对话式 AI 界面时使用此模式。
- 对于将 OpenAI、Anthropic 或其他 AI 提供商集成到 React 应用程序中非常有帮助。
- 当您需要提示管理、流式传输、错误处理和特定于 AI 的 UI 模式时使用。

## 说明

- 使用 Vercel AI SDK 的 `useChat` 钩子来管理对话状态和流式传输响应。
- 将 API 密钥保存在服务器上——使用 Next.js API 路由或单独的后端进行 AI 调用。
- 为聊天界面启用流式传输（`stream: true`）以实现响应式实时输出。
- 对输入进行防抖以实现自动完成功能；在流式传输响应期间禁用聊天输入。
- 构建与数据获取逻辑解耦的可重用组件（ChatMessage、InputBox）。

## 详情

> **注意**：虽然本文以 OpenAI 为例，但 Vercel AI SDK 支持多个模型提供者，包括 **Gemini**、**OpenAI** 和 **Anthropic**。您可以通过 SDK 的统一界面轻松切换提供者——我们只是选择了一个选项用于演示目的。

### 引言：React 中的 AI 界面

AI 驱动的用户界面（UI）随着 ChatGPT 等大型语言模型（LLM）的兴起而变得流行。与传统 UI 不同，AI 界面通常涉及对话式交互、动态内容流式传输和异步后端调用。这给 React 开发者带来了独特的挑战和模式。典型的 AI 聊天界面由一个**前端**（用于用户输入和显示响应）和一个**后端**（调用 AI 模型）组成。后端对于安全性和性能至关重要，以保持 API 密钥和重量级处理不在客户端。像 Vercel 的 **AI SDK** 这样的工具使连接到提供者（OpenAI、HuggingFace 等）和实时流式传输响应变得更加容易。我们将探讨如何设置 Next.js 应用程序和 Vite（React）应用程序来处理这些问题，并讨论适用于两者的最佳实践。

**涵盖的关键模式：**

- 结构化 AI 提示数据和管理对话状态
- 将 AI 响应流式传输到 UI 以实现实时反馈
- 防抖用户输入以避免向 API 发送过多请求
- 用户界面中的错误处理和回退
- 可重用的 UI 组件（消息、输入等），使用 TailwindCSS
- 架构差异：Next.js 路由处理程序与 Vite 和 Node 后端

到那时，您将能够使用 React 构建响应式、强大的 AI 驱动 UI，无论您是更喜欢 Next.js 还是 Vite 工具链。

### 项目设置和工具

在深入代码之前，请确保您拥有必要的包和配置：

- **React & Vite**：初始化一个 Vite + React 项目（例如 `npm create vite@latest my-ai-app -- --template react`）。对于 Next.js，您可以使用 `npx create-next-app` 或 Next 13 App Router 模板。两者都可以工作——我们将随着进展突出显示差异。

- **TailwindCSS**：在项目中设置 TailwindCSS 以快速进行样式设计。

- **OpenAI API & Vercel AI SDK**：安装 OpenAI 的库或 Vercel AI SDK。我们将使用 **Vercel 的 AI SDK**（`npm i ai`），它提供了有用的 React 钩子（`useChat`、`useCompletion`）和服务器实用程序。此 SDK 是框架无关的，适用于 Next.js、纯 React、Svelte 等。它简化了流式传输和状态管理，并且是免费/开源的。

- **API 密钥**：从 OpenAI 仪表板获取您的 OpenAI API 密钥并安全存储。在 Next.js 中，将其放在 `.env.local` 中（例如 `OPENAI_API_KEY=sk-...`），并且永远不要提交它。在 Vite 应用程序中，**不要**在客户端代码中暴露密钥——相反，使用后端代理或服务器上的环境变量。

### 设置 AI 端点（Next.js 与 Vite）

**Next.js 实现**：Next.js 允许我们创建**路由处理程序**作为服务器less函数。我们可以定义一个 API 路由，React 前端将调用它以获取 AI 响应：

```typescript
// app/api/chat/route.ts (Next.js)
import { Configuration, OpenAIApi } from 'openai-edge';
import { OpenAIStream, StreamingTextResponse } from 'ai';

export const runtime = 'edge';

const config = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
const openai = new OpenAIApi(config);

export async function POST(req: Request) {
  const { messages } = await req.json();
  const response = await openai.createChatCompletion({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages: messages.map((m: any) => ({ role: m.role, content: m.content }))
  });
  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}
```

在此处理程序中，我们接收一个包含消息数组（聊天历史记录）的 JSON 正文。我们使用 `stream: true` 调用 OpenAI 的聊天完成以获取流式响应。然后我们将响应包装在 AI SDK 提供的 `StreamingTextResponse` 中，以将数据块管道回客户端。Next.js API 路由将我们的 API 密钥保存在服务器上，并高效地流式传输数据。

**Vite（React）实现**：在 Vite 应用程序中，没有内置的服务器，因此我们需要创建自己的后端来处理 OpenAI 调用。这可以是一个简单的 Node/Express 服务器：

```javascript
// backend/server.js (Node/Express for Vite app)
import express from 'express';
import { Configuration, OpenAIApi } from 'openai';

const app = express();
app.use(express.json());

const config = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
const openai = new OpenAIApi(config);

app.post('/api/chat', async (req, res) => {
  try {
    const { messages = [] } = req.body;
    const systemMsg = { role: 'system', content: 'You are a helpful assistant.' };
    const inputMessages = [systemMsg, ...messages];
    const response = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      stream: false,
      messages: inputMessages
    });
    const content = response.data.choices[0].message?.content;
    res.json({ content });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.listen(6000, () => console.log('API server listening on http://localhost:6000'));
```

在开发期间，您可以配置 Vite 开发服务器将 `/api` 调用代理到此后端（例如，在 `vite.config.js` 中设置 `server.proxy['/api'] = 'http://localhost:6000'`）。关键是 React 应用程序调用一个**相对的 `/api/chat` 端点**，代理/托管将路由到您的服务器代码。这保持了 OpenAI 密钥的隐藏。

**在 Node 中启用流式传输**：上面的 Express 示例返回完成后的完整响应（为简单起见，`stream: false`）。要在 Node 中流式传输，您可以使用 OpenAI 的 HTTP 流：设置 `stream: true` 并处理响应作为数据流。这涉及读取 `response.data` 流并将数据块使用 `res.write()` 冲刷到客户端。如果您选择坚持使用完整响应（不流式传输），UI 模式仍然基本适用——但流式传输大大改善了用户体验。

### 提示处理和对话状态

任何 AI 界面的核心都是**提示管理**——将用户输入（以及上下文）组装成提示或消息序列以供 AI 模型使用。在聊天场景中，我们维护一个消息列表，每个消息都有一个角色和内容。OpenAI 的聊天 API 期望消息的格式为 `{ role: 'user' | 'assistant' | 'system', content: string }`。我们通常从一个系统消息开始（以设置助手的行为或上下文），然后随着对话的进行交替用户和助手消息。

**React 中的状态管理**：我们可以将对话存储在组件状态中。使用 Vercel SDK 的 React 钩子：

```jsx
import { useChat } from 'ai/react';

function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  // ...
}
```

`useChat` 钩子为我们处理了很多事情：它管理 `messages` 状态（一个消息对象数组）、`input` 状态用于当前文本输入，并提供了 `handleInputChange` 和 `handleSubmit` 辅助函数。默认情况下，`useChat()` 将在您提交时将数据 POST 到 `/api/chat`。

**手动状态处理**：如果您不使用 `useChat`，您可以使用 `useState` 或上下文来管理状态。在表单提交时，调用您的 API，然后通过向消息数组追加用户查询和助手的响应来更新消息。

**系统提示和上下文**：一个常见的模式是包括一个描述助手角色或知识库的初始系统消息。例如，如果构建一个文档助手，系统内容可能是“你是一个文档助手。用文档中的示例回答。”

**单轮与多轮**：如果您的界面是一个单问题回答（没有对话记忆），您可以使用 Vercel SDK 的 `useCompletion` 钩子。对于聊天机器人和多轮对话框，`useChat` 是首选模式，因为它保留并发送每次请求的消息历史记录。

### 将 AI 响应流式传输到 UI

现代 AI UI 的一个标志是**流式输出**：当 AI 生成标记时，用户会实时看到回复出现在界面上。这对于更好的用户体验至关重要，因为模型生成的答案可能很长或很慢。流式传输让我们能够立即显示部分结果，而不是在沉默中等待几秒钟。

**流式传输的工作原理**：当我们为 OpenAI API 启用 `stream: true` 时，响应作为一系列数据事件（数据块）而不是一个 JSON 块发送。Vercel AI SDK 简化了消费这些数据块。在服务器端，我们将响应转换为文本流（`StreamingTextResponse`）。在客户端，`useChat` 钩子处理读取此流并随着新文本到达而逐步更新消息状态。

如果您在 React 中手动实现流式传输（不使用 SDK），您会做类似的事情：

```javascript
const res = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ messages }) });
const reader = res.body.getReader();
const decoder = new TextDecoder();
let partial = "";
while(true) {
  const { value, done } = await reader.read();
  if (done) break;
  partial += decoder.decode(value);
  setAssistantMessage(partial);
}
```

**自动滚动**：在流式传输时，一个 UX 细节是确保最新消息可见。处理此问题的模式是使用 `useEffect` 观察 `messages` 数组长度并自动滚动消息容器。

**部分渲染和完成**：在流式传输期间显示一个视觉指示器——例如，一个闪烁的光标或“AI 正在输入…”消息。一旦流完成，就最终确定消息显示。

### 输入处理和防抖

对于聊天交互，您通常在用户提交表单时发送查询。在某些 AI 应用中，您可能希望连续响应输入——例如，**自动完成建议**或**AI 的实时验证**。在这种情况下，**防抖**很重要。

**为什么需要防抖**？在每次按键时调用 OpenAI API 将非常低效且昂贵。防抖会延迟 API 调用，直到用户停止输入一段时间。

```jsx
const [draft, setDraft] = useState("");

useEffect(() => {
  if (!draft) return;
  const timeout = setTimeout(() => {
    getSuggestion(draft);
  }, 500);
  return () => clearTimeout(timeout);
}, [draft]);
```

对于具有明确“发送”操作的简单聊天机器人，防抖通常不是必需的——您在用户按 Enter 时发送。但是，它仍然用于**禁用输入**或**防止多次提交**，在流式传输 AI 响应期间。

### 错误处理和弹性

在 AI 应用中，稳健的错误处理至关重要：

- **API 调用周围的 try/catch**：在服务器上，将 OpenAI 调用包装在 try/catch 中。如果失败，请返回一个适当的错误响应。

- **客户端错误状态**：处理响应指示错误的情况。

```javascript
try {
  await sendMessage({ text: input });
} catch (error) {
  console.error("Failed to send message:", error);
}
```

- **用户反馈**：当出现问题时，始终通知用户。将错误作为聊天中的特殊“系统”消息显示——例如，“*对不起，出了点问题。请重试。*”

- **重试机制**：考虑允许用户使用“重试”按钮重试。

- **验证错误**：在调用 API 之前在客户端进行验证。在输入为空时禁用发送，或截断超出某些长度的输入。

### 构建 UI：组件和样式模式

**聊天消息组件**：创建一个 `ChatMessage` 组件，该组件渲染单个消息气泡。根据角色，样式会有所不同：

```jsx
function ChatMessage({ role, content }) {
  const isUser = role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-2`}>
      <div className={`max-w-xl px-4 py-2 rounded-lg ${
        isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'
      }`}>
        {content}
      </div>
    </div>
  );
}
```

**输入组件**：

```jsx
function InputBox({ value, onChange, onSubmit, disabled }) {
  return (
    <form onSubmit={onSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="flex-1 border rounded px-3 py-2"
        placeholder="Type your message..."
      />
      <button type="submit" disabled={disabled} className="bg-blue-500 text-white px-4 py-2 rounded">
        Send
      </button>
    </form>
  );
}
```

**组合**：

```jsx
function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
  
  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} content={msg.content} />
        ))}
      </div>
      <InputBox 
        value={input} 
        onChange={handleInputChange} 
        onSubmit={handleSubmit}
        disabled={isLoading}
      />
    </div>
  );
}
```

这种分离关注点使得测试和交换 UI 部件变得容易。逻辑（`useChat`）与显示组件解耦。

### Vercel AI 元素（预构建的聊天 UI 组件）

Vercel 的 **AI 元素**库提供了一套现成的 React 组件，专门为 AI 聊天界面设计：

- **Conversation**：一个容器，用于渲染消息列表并自动滚动。
- **Prompt**：一个针对聊天提示优化的输入组件。
- **TypingIndicator**：显示 AI 正在“思考”或流式传输响应。
- **ErrorBoundary/ErrorMessage**：优雅地处理和显示错误。

```jsx
import { Conversation, Prompt, TypingIndicator } from '@vercel/ai-elements';

function ChatApp() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
  
  return (
    <div className="h-screen flex flex-col">
      <Conversation messages={messages} />
      {isLoading && <TypingIndicator />}
      <Prompt 
        value={input} 
        onChange={handleInputChange} 
        onSubmit={handleSubmit}
      />
    </div>
  );
}
```

### 将所有内容整合在一起

1. **后端 API 路由：** 无论是使用 Next.js 路由处理器还是独立的 Express 服务器，创建一个接收消息、调用 AI 模型并将响应流式传输回端的端点。

2. **状态管理：** 使用 Vercel AI SDK 的 `useChat` 钩子（或使用 `useState` 自行实现）来管理对话状态。

3. **流式传输：** 在服务器和客户端都启用流式传输，以实现响应式用户体验。

4. **防抖与速率限制：** 对于自动补全等特性，防抖 API 调用。对于聊天，在响应流式传输期间禁用输入。

5. **错误处理：** 将 API 调用包装在 try/catch 中，提供错误用户反馈，并考虑重试机制。

6. **可复用组件：** 构建与数据获取逻辑解耦的展示组件（`ChatMessage`、`InputBox`）。考虑使用 AI Elements 来创建生产就绪的组件。

7. **样式：** 使用 TailwindCSS（或您首选的样式解决方案）来创建干净、响应式的聊天界面。

### 架构比较：Next.js 与 Vite

| 方面 | Next.js | Vite + Node 后端 |
|------|--------|------------------|
| **API 路由** | 内置 (`pages/api/` 或 `app/api/`) | 需要独立的 Express/Node 服务器 |
| **流式传输** | Edge 运行时原生支持 | 需要手动实现 `res.write()` |
| **部署** | Vercel（优化）或自托管 | 前端（静态）与后端分别部署 |
| **复杂度** | 较低（一体化） | 较高（两个代码库） |
| **灵活性** | 框架约定 | 完全控制 |

对于大多数 AI 聊天应用，**Next.js** 提供了更简单的开发者体验，其集成的 API 路由和流式传输支持。但是，如果您有现有的 Vite/React 应用程序或更喜欢更多控制，这里描述的模式与独立后端配合使用效果良好。

## 来源

- [patterns.dev/react/ai-ui-patterns](https://patterns.dev/react/ai-ui-patterns)

### 参考文献

- [Vercel AI SDK 文档](https://ai-sdk.dev/)
- [Vercel Academy: 基础聊天机器人](https://vercel.com/academy/ai-sdk/basic-chatbot)
- [Vercel Academy: AI Elements](https://vercel.com/academy/ai-sdk/ai-elements)
- [使用 Vercel AI SDK 在 Next.js 中构建聊天机器人](https://blog.saeloun.com/2023/07/13/building-chatbot-in-next-js-using-vercel-ai-sdk/)
- [使用 React、Vite、Node 和 OpenAI 构建 Docs-Aware 聊天机器人](https://dev.to/cloudinary/build-a-docs-aware-chatbot-with-react-vite-node-and-openai-plus-fun-dalle-avatars-1chi)
