# 使用 OpenRouter 构建模块化 AI 代理

这项技能将帮助你创建一个**模块化 AI 代理**，它包含：

- **独立代理核心** - 独立运行，可通过钩子扩展
- **OpenRouter SDK** - 统一访问 300 多种语言模型
- **可选 Ink TUI** - 美丽的终端界面（与代理逻辑分离）

## 架构

```
┌─────────────────────────────────────────────────────┐
│                    您的应用程序                 │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Ink TUI   │  │  HTTP API   │  │   Discord   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │         │
│         └────────────────┼────────────────┘         │
│                          ▼                          │
│              ┌───────────────────────┐              │
│              │      Agent Core       │              │
│              │  (hooks & lifecycle)  │              │
│              └───────────┬───────────┘              │
│                          ▼                          │
│              ┌───────────────────────┐              │
│              │    OpenRouter SDK     │              │
│              └───────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

## 前置条件

在 https://openrouter.ai/settings/keys 获取 OpenRouter API 密钥

⚠️ **安全提示**：切勿提交 API 密钥。使用环境变量。

## 项目设置

### 第 1 步：初始化项目

```bash
mkdir my-agent && cd my-agent
npm init -y
npm pkg set type="module"
```

### 第 2 步：安装依赖项

```bash
npm install @openrouter/sdk zod eventemitter3
npm install ink react  # 可选：仅用于 TUI
npm install -D typescript @types/react tsx
```

### 第 3 步：创建 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

### 第 4 步：向 package.json 添加脚本

```json
{
  "scripts": {
    "start": "tsx src/cli.tsx",
    "start:headless": "tsx src/headless.ts",
    "dev": "tsx watch src/cli.tsx"
  }
}
```

## 文件结构

```bash
src/
├── agent.ts        # 独立代理核心，带钩子
├── tools.ts        # 工具定义
├── cli.tsx         # Ink TUI（可选界面）
└── headless.ts     # 无界面使用示例
```

## 第 1 步：带钩子的代理核心

创建 `src/agent.ts` - 可在任何地方运行的独立代理：

```typescript
import { OpenRouter, tool, stepCountIs } from '@openrouter/sdk';
import type { Tool, StopCondition, StreamableOutputItem } from '@openrouter/sdk';
import { EventEmitter } from 'eventemitter3';
import { z } from 'z';

// 消息类型
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// 代理钩子事件（基于项目流模型）
export interface AgentEvents {
  'message:user': (message: Message) => void;
  'message:assistant': (message: Message) => void;
  'item:update': (item: StreamableOutputItem) => void;  // 同 ID 发送的项目，用 ID 替换
  'stream:start': () => void;
  'stream:delta': (delta: string, accumulated: string) => void;
  'stream:end': (fullText: string) => void;
  'tool:call': (name: string, args: unknown) => void;
  'tool:result': (name: string, result: unknown) => void;
  'reasoning:update': (text: string) => void;  // 扩展思考内容
  'error': (error: Error) => void;
  'thinking:start': () => void;
  'thinking:end': () => void;
}

// 代理配置
export interface AgentConfig {
  apiKey: string;
  model?: string;
  instructions?: string;
  tools?: Tool<z.ZodTypeAny, z.ZodTypeAny>[];
  maxSteps?: number;
}

// 代理类 - 独立于任何界面运行
export class Agent extends EventEmitter<AgentEvents> {
  private client: OpenRouter;
  private messages: Message[] = [];
  private config: Required<Omit<AgentConfig, 'apiKey'>> & { apiKey: string };

  constructor(config: AgentConfig) {
    super();
    this.client = new OpenRouter({ apiKey: config.apiKey });
    this.config = {
      apiKey: config.apiKey,
      model: config.model ?? 'openrouter/auto',
      instructions: config.instructions ?? 'You are a helpful assistant.',
      tools: config.tools ?? [],
      maxSteps: config.maxSteps ?? 5,
    };
  }

  // 获取对话历史
  getMessages(): Message[] {
    return [...this.messages];
  }

  // 清除对话
  clearHistory(): void {
    this.messages = [];
  }

  // 设置系统消息
  setInstructions(instructions: string): void {
    this.config.instructions = instructions;
  }

  // 运行时注册额外工具
  addTool(newTool: Tool<z.ZodTypeAny, z.ZodTypeAny>): void {
    this.config.tools.push(newTool);
  }

  // 发送消息并使用基于项目的流式响应
  // 项目多次使用相同 ID 但内容逐步更新
  // 用 ID 替换项目，而不是累积块
  async send(content: string): Promise<string> {
    const userMessage: Message = { role: 'user', content };
    this.messages.push(userMessage);
    this.emit('message:user', userMessage);
    this.emit('thinking:start');

    try {
      const result = this.client.callModel({
        model: this.config.model,
        instructions: this.config.instructions,
        input: this.messages.map((m) => ({ role: m.role, content: m.content })),
        tools: this.config.tools.length > 0 ? this.config.tools : undefined,
        stopWhen: [stepCountIs(this.config.maxSteps)],
      });

      this.emit('stream:start');
      let fullText = '';

      // 使用 getItemsStream() 进行基于项目的流式传输（推荐）
      // 每个项目都是完整的 - 用 ID 替换，不要累积
      for await (const item of result.getItemsStream()) {
        // 发射项目以管理 UI 状态（使用按 ID 键化的 Map）
        this.emit('item:update', item);

        switch (item.type) {
          case 'message':
            // 消息项目包含逐步更新的内容
            const textContent = item.content?.find((c: { type: string }) => c.type === 'output_text');
            if (textContent && 'text' in textContent) {
              const newText = textContent.text;
              if (newText !== fullText) {
                const delta = newText.slice(fullText.length);
                fullText = newText;
                this.emit('stream:delta', delta, fullText);
              }
            }
            break;
          case 'function_call':
            // 函数调用参数逐步流式传输
            if (item.status === 'completed') {
              this.emit('tool:call', item.name, JSON.parse(item.arguments || '{}'));
            }
            break;
          case 'function_call_output':
            this.emit('tool:result', item.callId, item.output);
            break;
          case 'reasoning':
            // 扩展思考/推理内容
            const reasoningText = item.content?.find((c: { type: string }) => c.type === 'reasoning_text');
            if (reasoningText && 'text' in reasoningText) {
              this.emit('reasoning:update', reasoningText.text);
            }
            break;
          // 其他项目类型：web_search_call、file_search_call、image_generation_call
        }
      }

      // 如果流式传输未捕获最终文本，则获取最终文本
      if (!fullText) {
        fullText = await result.getText();
      }

      this.emit('stream:end', fullText);

      const assistantMessage: Message = { role: 'assistant', content: fullText };
      this.messages.push(assistantMessage);
      this.emit('message:assistant', assistantMessage);

      return fullText;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      this.emit('error', error);
      throw error;
    } finally {
      this.emit('thinking:end');
    }
  }

  // 不带流式传输发送（程序化使用更简单）
  async sendSync(content: string): Promise<string> {
    const userMessage: Message = { role: 'user', content };
    this.messages.push(userMessage);
    this.emit('message:user', userMessage);

    try {
      const result = this.client.callModel({
        model: this.config.model,
        instructions: this.config.instructions,
        input: this.messages.map((m) => ({ role: m.role, content: m.content })),
        tools: this.config.tools.length > 0 ? this.config.tools : undefined,
        stopWhen: [stepCountIs(this.config.maxSteps)],
      });

      const fullText = await result.getText();
      const assistantMessage: Message = { role: 'assistant', content: fullText };
      this.messages.push(assistantMessage);
      this.emit('message:assistant', assistantMessage);

      return fullText;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      this.emit('error', error);
      throw error;
    }
  }
}

// 工厂函数，便于创建
export function createAgent(config: AgentConfig): Agent {
  return new Agent(config);
}
```

## 第 2 步：定义工具

创建 `src/tools.ts`:

```typescript
import { tool } from '@openrouter/sdk';
import { z } from 'z';

export const timeTool = tool({
  name: 'get_current_time',
  description: '获取当前日期和时间',
  inputSchema: z.object({
    timezone: z.string().optional().describe('时区（例如，"UTC"、"America/New_York"）'),
  }),
  execute: async ({ timezone }) => {
    return {
      time: new Date().toLocaleString('en-US', { timeZone: timezone || 'UTC' }),
      timezone: timezone || 'UTC',
    };
  },
});

export const calculatorTool = tool({
  name: 'calculate',
  description: '执行数学计算',
  inputSchema: z.object({
    expression: z.string().describe('数学表达式（例如，"2 + 2"、"sqrt(16)"）'),
  }),
  execute: async ({ expression }) => {
    // 简单安全的 eval 用于基本数学运算
    const sanitized = expression.replace(/[^0-9+\-*/().\s]/g, '');
    const result = Function(`"use strict"; return (${sanitized})`)();
    return { expression, result };
  },
});

export const defaultTools = [timeTool, calculatorTool];
```

## 第 3 步：无界面使用（无界面）

创建 `src/headless.ts` - 程序化使用代理：

```typescript
import { createAgent } from './agent.js';
import { defaultTools } from './tools.js';

async function main() {
  const agent = createAgent({
    apiKey: process.env.OPENROUTER_API_KEY!,
    model: 'openrouter/auto',
    instructions: 'You are a helpful assistant with access to tools.',
    tools: defaultTools,
  });

  // 钩入事件
  agent.on('thinking:start', () => console.log('\n🤔 思考中...'));
  agent.on('tool:call', (name, args) => console.log(`🔧 使用 ${name}:`, args));
  agent.on('stream:delta', (delta) => process.stdout.write(delta));
  agent.on('stream:end', () => console.log('\n'));
  agent.on('error', (err) => console.error('❌ 错误:', err.message));

  // 交互式循环
  const readline = await import('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log('代理已准备。输入您的消息（Ctrl+C 退出）:\n');

  const prompt = () => {
    rl.question('您: ', async (input) => {
      if (!input.trim()) {
        prompt();
        return;
      }
      await agent.send(input);
      prompt();
    });
  };

  prompt();
}

main().catch(console.error);
```

运行无界面：`OPENROUTER_API_KEY=sk-or-... npm run start:headless`

## 第 4 步：Ink TUI（可选界面）

创建 `src/cli.tsx` - 美丽的终端界面，使用基于项目的流式传输：

```tsx
import React, { useState, useEffect, useCallback } from 'react';
import { render, Box, Text, useInput, useApp } from 'ink';
import type { StreamableOutputItem } from '@openrouter/sdk';
import { createAgent, type Agent, type Message } from './agent.js';
import { defaultTools } from './tools.js';

// 初始化代理（独立于界面运行）
const agent = createAgent({
  apiKey: process.env.OPENROUTER_API_KEY!,
  model: 'openrouter/auto',
  instructions: 'You are a helpful assistant. Be concise.',
  tools: defaultTools,
});

function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color={isUser ? 'cyan' : 'green'}>
        {isUser ? '▶ 您' : '◀ 助手'}
      </Text>
      <Text wrap="wrap">{message.content}</Text>
    </Box>
  );
}

// 使用基于项目的模式渲染流式项目
function ItemRenderer({ item }: { item: StreamableOutputItem }) {
  switch (item.type) {
    case 'message': {
      const textContent = item.content?.find((c: { type: string }) => c.type === 'output_text');
      const text = textContent && 'text' in textContent ? textContent.text : '';
      return (
        <Box flexDirection="column" marginBottom={1}>
          <Text bold color="green">◀ 助手</Text>
          <Text wrap="wrap">{text}</Text>
          {item.status !== 'completed' && <Text color="gray">▌</Text>}
        </Box>
      );
    }
    case 'function_call':
      return (
        <Text color="yellow">
          {item.status === 'completed' ? '  ✓' : '  🔧'} {item.name}
          {item.status === 'in_progress' && '...'}
        </Text>
      );
    case 'reasoning': {
      const reasoningText = item.content?.find((c: { type: string }) => c.type === 'reasoning_text');
      const text = reasoningText && 'text' in reasoningText ? reasoningText.text : '';
      return (
        <Box flexDirection="column" marginBottom={1}>
          <Text bold color="magenta">💭 思考</Text>
          <Text wrap="wrap" color="gray">{text}</Text>
        </Box>
      );
    }
    default:
      return null;
  }
}

function InputField({
  value,
  onChange,
  onSubmit,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  disabled: boolean;
}) {
  useInput((input, key) => {
    if (disabled) return;
    if (key.return) onSubmit();
    else if (key.backspace || key.delete) onChange(value.slice(0, -1));
    else if (input && !key.ctrl && !key.meta) onChange(value + input);
  });

  return (
    <Box>
      <Text color="yellow">{'> '}</Text>
      <Text>{value}</Text>
      <Text color="gray">{disabled ? ' ···' : '█'}</Text>
    </Box>
  );
}

function App() {
  const { exit } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // 使用按 ID 键化的 Map 进行高效的 React 状态更新（基于项目的模式）
  const [items, setItems] = useState<Map<string, StreamableOutputItem>>(new Map());

  useInput((_, key) => {
    if (key.escape) exit();
  });

  // 使用基于项目的流式传输订阅代理事件
  useEffect(() => {
    const onThinkingStart = () => {
      setIsLoading(true);
      setItems(new Map()); // 新响应时清除项目
    };

    // 基于项目的流式传输：按 ID 替换项目，不要累积
    const onItemUpdate = (item: StreamableOutputItem) => {
      setItems((prev) => new Map(prev).set(item.id, item));
    };

    const onMessageAssistant = () => {
      setMessages(agent.getMessages());
      setItems(new Map()); // 清除流式项目
      setIsLoading(false);
    };

    const onError = (err: Error) => {
      setIsLoading(false);
    };

    agent.on('thinking:start', onThinkingStart);
    agent.on('item:update', onItemUpdate);
    agent.on('message:assistant', onMessageAssistant);
    agent.on('error', onError);

    return () => {
      agent.off('thinking:start', onThinkingStart);
      agent.off('item:update', onItemUpdate);
      agent.off('message:assistant', onMessageAssistant);
      agent.off('error', onError);
    };
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;
    const text = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    await agent.send(text);
  }, [input, isLoading]);

  return (
    <Box flexDirection="column" padding={1}>
      <Box marginBottom={1}>
        <Text bold color="magenta">🤖 OpenRouter Agent</Text>
        <Text color="gray"> (Esc 退出)</Text>
      </Box>

      <Box flexDirection="column" marginBottom={1}>
        {/* 渲染已完成消息 */}
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {/* 按类型渲染流式项目（基于项目的模式） */}
        {Array.from(items.values()).map((item) => (
          <ItemRenderer key={item.id} item={item} />
        ))}
      </Box>

      <Box borderStyle="single" borderColor="gray" paddingX={1}>
        <InputField
          value={input}
          onChange={setInput}
          onSubmit={sendMessage}
          disabled={isLoading}
        />
      </Box>
    </Box>
  );
}

render(<App />);
```

运行 TUI：`OPENROUTER_API_KEY=sk-or-... npm start`

## 理解基于项目的流式传输

OpenRouter SDK 使用**基于项目的流式传输模型** - 关键范式是项目多次使用相同 ID 但内容逐步更新的。不要累积块，而是用 ID 替换项目。

### 工作原理

`getItemsStream()` 的每次迭代都会生成一个完整的包含更新内容的项目：

```typescript
// 迭代 1：部分消息
{ id: "msg_123", type: "message", content: [{ type: "output_text", text: "Hello" }] }

// 迭代 2：更新消息（替换，不要追加）
{ id: "msg_123", type: "message", content: [{ type: "output_text", text: "Hello world" }] }
```

对于函数调用，参数逐步流式传输：

```typescript
// 迭代 1：部分参数
{ id: "call_456", type: "function_call", name: "get_weather", arguments: "{\"q" }

// 迭代 2：完整参数
{ id: "call_456", type: "function_call", name: "get_weather", arguments: "{\"query\": \"Paris\"}", status: "completed" }
```

### 为什么项目更好

**传统（需要手动累积）**：
```typescript
let text = '';
for await (const chunk of result.getTextStream()) {
  text += chunk;  // 手动累积
  updateUI(text);
}
```

**项目（完整替换）**：
```typescript
const items = new Map<string, StreamableOutputItem>();
for await (const item of result.getItemsStream()) {
  items.set(item.id, item);  // 用 ID 替换
  updateUI(items);
}
```

优点：
- **无需手动块管理** - 每个项目都是完整的
- **处理并发输出** - 函数调用和消息可以并行流式传输
- **完整的 TypeScript 推断** - 所有项目类型
- **自然的 Map-based 状态** - 与 React/UI 框架完美配合

## 扩展代理

### 添加自定义钩子

```typescript
const agent = createAgent({ apiKey: '...' });

// 记录所有事件
agent.on('message:user', (msg) => {
  saveToDatabase('user', msg.content);
});

agent.on('message:assistant', (msg) => {
  saveToDatabase('assistant', msg.content);
  sendWebhook('new_message', msg);
});

agent.on('tool:call', (name, args) => {
  analytics.track('tool_used', { name, args });
});

agent.on('error', (err) => {
  errorReporting.capture(err);
});
```

### 与 HTTP 服务器一起使用

```typescript
import express from 'express';
import { createAgent } from './agent.js';

const app = express();
app.use(express.json());

// 每个会话使用一个代理（存储在内存或 Redis 中）
const sessions = new Map<string, Agent>();

app.post('/chat', async (req, res) => {
  const { sessionId, message } = req.body;

  let agent = sessions.get(sessionId);
  if (!agent) {
    agent = createAgent({ apiKey: process.env.OPENROUTER_API_KEY! });
    sessions.set(sessionId, agent);
  }

  const response = await agent.sendSync(message);
  res.json({ response, history: agent.getMessages() });
});

app.listen(3000);
```

### 与 Discord 一起使用

```typescript
import { Client, GatewayIntentBits } from 'discord.js';
import { createAgent } from './agent.js';

const discord = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages],
});

const agents = new Map<string, Agent>();

discord.on('messageCreate', async (msg) => {
  if (msg.author.bot) return;

  let agent = agents.get(msg.channelId);
  if (!agent) {
    agent = createAgent({ apiKey: process.env.OPENROUTER_API_KEY! });
    agents.set(msg.channelId, agent);
  }

  const response = await agent.sendSync(msg.content);
  await msg.reply(response);
});

discord.login(process.env.DISCORD_TOKEN);
```

## 代理 API 参考

### 构造函数选项

| 选项 | 类型 | 默认 | 描述 |
|------|------|------|------|
| apiKey | string | required | OpenRouter API 密钥 |
| model | string | 'openrouter/auto' | 使用的模型 |
| instructions | string | 'You are a helpful assistant.' | 系统提示 |
| tools | Tool[] | [] | 可用工具 |
| maxSteps | number | 5 | 最大代理循环迭代次数 |

### 方法

| 方法 | 返回 | 描述 |
|------|------|------|
| `send(content)` | Promise<string> | 发送消息并使用流式传输 |
| `sendSync(content)` | Promise<string> | 发送消息而不使用流式传输 |
| `getMessages()` | Message[] | 获取对话历史 |
| `clearHistory()` | void | 清除对话 |
| `setInstructions(text)` | void | 更新系统提示 |
| `addTool(tool)` | void | 运行时添加工具 |

### 事件

| 事件 | 有效负载 | 描述 |
|------|----------|------|
| `message:user` | Message | 添加用户消息 |
| `message:assistant` | Message | 助手响应完成 |
| `item:update` | StreamableOutputItem | 发射项目（用 ID 替换，不要累积） |
| `stream:start` | - | 流式传输开始 |
| `stream:delta` | (delta, accumulated) | 新文本块 |
| `stream:end` | fullText | 流式传输完成 |
| `tool:call` | (name, args) | 正在调用工具 |
| `tool:result` | (name, result) | 工具返回结果 |
| `reasoning:update` | text | 扩展思考内容 |
| `thinking:start` | - | 代理正在处理 |
| `thinking:end` | - | 代理处理完成 |
| `error` | Error | 发生错误 |

### 项目类型（来自 getItemsStream）

SDK 使用基于项目的流式传输模型，其中项目多次使用相同 ID 但内容逐步更新的。用 ID 替换项目，而不是累积块。

| 类型 | 目的 |
|------|------|
| `message` | 助手文本响应 |
| `function_call` | 工具调用，参数逐步流式传输 |
| `function_call_output` | 执行工具的结果 |
| `reasoning` | 扩展思考/推理内容 |
| `web_search_call` | 网络搜索操作 |
| `file_search_call` | 文件搜索操作 |
| `image_generation_call` | 图像生成操作 |

## 探索模型

**不要硬编码模型 ID** - 它们经常变化。使用模型 API：

### 获取可用模型

```typescript
interface OpenRouterModel {
  id: string;
  name: string;
  description?: string;
  context_length: number;
  pricing: { prompt: string; completion: string };
  top_provider?: { is_moderated: boolean };
}

async function fetchModels(): Promise<OpenRouterModel[]> {
  const res = await fetch('https://openrouter.ai/api/v1/models');
  const data = await res.json();
  return data.data;
}

// 根据标准查找模型
async function findModels(filter: {
  author?: string;      // 例如，'anthropic', 'openai', 'google'
  minContext?: number;  // 例如，100000 for 100k 上下文
  maxPromptPrice?: number; // 例如，0.001 for 便宜模型
}): Promise<OpenRouterModel[]> {
  const models = await fetchModels();

  return models.filter((m) => {
    if (filter.author && !m.id.startsWith(filter.author + '/') return false;
    if (filter.minContext && m.context_length < filter.minContext) return false;
    if (filter.maxPromptPrice) {
      const price = parseFloat(m.pricing.prompt);
      if (price > filter.maxPromptPrice) return false;
    }
    return true;
  });
}

// 示例：获取最新的 Claude 模型
const claudeModels = await findModels({ author: 'anthropic' });
console.log(claudeModels.map((m) => m.id));

// 示例：获取 100k+ 上下文模型
const longContextModels = await findModels({ minContext: 100000 });

// 示例：获取便宜模型
const cheapModels = await findModels({ maxPromptPrice: 0.0005 });
```

### 代理中的动态模型选择

```typescript
// 使用发现的模型创建代理
const models = await fetchModels();
const bestModel = models.find((m) => m.id.includes('claude')) || models[0];

const agent = createAgent({
  apiKey: process.env.OPENROUTER_API_KEY!,
  model: bestModel.id,  // 使用发现的模型
  instructions: 'You are a helpful assistant.',
});
```

### 使用 openrouter/auto

为简单起见，使用 `openrouter/auto` 会自动选择最适合您请求的模型：

```typescript
const agent = createAgent({
  apiKey: process.env.OPENROUTER_API_KEY!,
  model: 'openrouter/auto',  // 自动选择最佳模型
});
```

### 模型 API 参考

- **端点**: `GET https://openrouter.ai/api/v1/models`
- **响应**: `{ data: OpenRouterModel[] }`
- **浏览模型**: https://openrouter.ai/models

## 资源

- OpenRouter 文档: https://openrouter.ai/docs
- 模型 API: https://openrouter.ai/api/v1/models
- Ink 文档: https://github.com/vadimdemedes/ink
- 获取 API 密钥: https://openrouter.ai/settings/keys
