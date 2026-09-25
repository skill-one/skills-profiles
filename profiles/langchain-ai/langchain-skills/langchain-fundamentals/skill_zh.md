<oneliner>
使用 `create_agent()`、中间件模式以及 `@tool` 装饰器 / `tool()` 函数来构建生产环境代理。在创建 LangChain 代理时，你必须使用 create_agent()，并配合中间件实现自定义流程。所有其他替代方案都已过时。
</oneliner>

<create_agent>
## 使用 create_agent 创建代理

`create_agent()` 是推荐的构建代理方式。它处理代理循环、工具执行和状态管理。

### 代理配置选项

| 参数 | 目的 | 示例 |
|-------|-------|-------|
| `model` | 使用的 LLM | `"anthropic:claude-sonnet-4-5"` 或模型实例 |
| `tools` | 工具列表 | `[search, calculator]` |
| `system_prompt` / `systemPrompt` | 代理指令 | `"You are a helpful assistant"` |
| `checkpointer` | 状态持久化 | `MemorySaver()` |
| `middleware` | 处理钩子 | `[HumanInTheLoopMiddleware]` (Python) / `[humanInTheLoopMiddleware({...})]` (TypeScript) |
</create_agent>

<ex-basic-agent>
<python>

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """获取某个地点的当前天气。

    Args:
        location: 城市名称
    """
    return f"Weather in {location}: Sunny, 72F"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Paris?"}]
})
print(result["messages"][-1].content)
```
</python>
<typescript>

```typescript
import { createAgent } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny, 72F`,
  {
    name: "get_weather",
    description: "Get current weather for a location.",
    schema: z.object({ location: z.string().describe("City name") }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [getWeather],
  systemPrompt: "You are a helpful assistant.",
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});
console.log(result.messages[result.messages.length - 1].content);
```
</typescript>
</ex-basic-agent>

<ex-agent-with-persistence>
<python>
添加 MemorySaver checkpointer 以跨调用维护对话状态。

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)
result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Alice"
```
</python>
<typescript>
添加 MemorySaver checkpointer 以跨调用维护对话状态。

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  checkpointer,
});

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);
const result = await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Alice"
```
</typescript>
</ex-agent-with-persistence>

<tools>
## 定义工具

工具是可以被代理调用的函数。使用 `@tool` 装饰器 (Python) 或 `tool()` 函数 (TypeScript)。
</tools>

<ex-basic-tool>
<python>

```python
from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """将两个数字相加。

    Args:
        a: 第一个数字
        b: 第二个数字
    """
    return a + b
```
</python>
<typescript>

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const add = tool(
  async ({ a, b }) => a + b,
  {
    name: "add",
    description: "Add two numbers.",
    schema: z.object({
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```
</typescript>
</ex-basic-tool>

<middleware>
## 代理控制中间件

中间件拦截代理循环，以添加人工审批、错误处理、日志记录等。深入理解中间件对于生产环境代理至关重要 — 使用 `HumanInTheLoopMiddleware` (Python) / `humanInTheLoopMiddleware` (TypeScript) 实现审批工作流，以及 `@wrap_tool_call` (Python) / `createMiddleware` (TypeScript) 实现自定义钩子。

关键导入：

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware, wrap_tool_call
```

```typescript
import { humanInTheLoopMiddleware, createMiddleware } from "langchain";
```

关键模式：
- **HITL**: `middleware=[HumanInTheLoopMiddleware(interrupt_on={"dangerous_tool": True})]` — 需要 `checkpointer` + `thread_id`
- **中断后继续**: `agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)`
- **自定义中间件**: `@wrap_tool_call` 装饰器 (Python) 或 `createMiddleware({ wrapToolCall: ... })` (TypeScript)
</middleware>

<structured_output>
## 结构化输出

使用 `response_format` 或 `with_structured_output()` 获取代理的带类型验证的响应。

<python>

```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str = Field(description="Phone number with area code")

# 选项 1：带结构化输出的代理
agent = create_agent(model="gpt-4.1", tools=[search], response_format=ContactInfo)
result = agent.invoke({"messages": [{"role": "user", "content": "Find contact for John"}]})
print(result["structured_response"])  # ContactInfo(name='John', ...)

# 选项 2：模型级别的结构化输出（无需代理）
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4.1")
structured_model = model.with_structured_output(ContactInfo)
response = structured_model.invoke("Extract: John, john@example.com, 555-1234")
# ContactInfo(name='John', email='john@example.com', phone='555-1234')
```
</python>
<typescript>

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string().email(),
  phone: z.string().describe("Phone number with area code"),
});

// 模型级别的结构化输出
const model = new ChatOpenAI({ model: "gpt-4.1" });
const structuredModel = model.withStructuredOutput(ContactInfo);
const response = await structuredModel.invoke("Extract: John, john@example.com, 555-1234");
// { name: 'John', email: 'john@example.com', phone: '555-1234' }
```
</typescript>
</structured_output>

<model_config>
## 模型配置

`create_agent` 接受模型字符串 (`"anthropic:claude-sonnet-4-5"`, `"openai:gpt-4.1"`) 或模型实例以进行自定义设置：

```python
from langchain_anthropic import ChatAnthropic
agent = create_agent(model=ChatAnthropic(model="claude-sonnet-4-5", temperature=0), tools=[...])
```
</model_config>


<fix-missing-tool-description>
<python>
清晰的描述有助于代理知道何时使用每个工具。

```python
# 错误：模糊或缺失描述
@tool
def bad_tool(input: str) -> str:
    """做一些事情。"""
    return "result"

# 正确：清晰的、具体的描述，带 Args
@tool
def search(query: str) -> str:
    """搜索网络以获取某个主题的当前信息。

    当你需要最新数据或事实时使用此工具。

    Args:
        query: 搜索查询（建议 2-10 个词）
    """
    return web_search(query)
```
</python>
<typescript>
清晰的描述有助于代理知道何时使用每个工具。

```typescript
// 错误：模糊描述
const badTool = tool(async ({ input }) => "result", {
  name: "bad_tool",
  description: "Does stuff.", // 太模糊了！
  schema: z.object({ input: z.string() }),
});

// 正确：清晰的、具体的描述
const search = tool(async ({ query }) => webSearch(query), {
  name: "search",
  description: "Search the web for current information about a topic. Use this when you need recent data or facts.",
  schema: z.object({
    query: z.string().describe("The search query (2-10 words recommended)"),
  }),
});
```
</typescript>
</fix-missing-tool-description>

<fix-no-checkpointer>
<python>
添加 checkpointer 和 thread_id 以跨调用维护对话记忆。

```python
# 错误：无持久化 - 代理在调用间会忘记
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search])
agent.invoke({"messages": [{"role": "user", "content": "I'm Bob"}]})
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember!

# 正确：添加 checkpointer 和 thread_id
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    checkpointer=MemorySaver(),
)
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({"messages": [{"role": "user", "content": "I'm Bob"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Bob"
```
</python>
<typescript>
添加 checkpointer 和 thread_id 以跨调用维护对话记忆。

```typescript
// 错误：无持久化
const agent = createAgent({ model: "anthropic:claude-sonnet-4-5", tools: [search] });
await agent.invoke({ messages: [{ role: "user", content: "I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember!

// 正确：添加 checkpointer 和 thread_id
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  checkpointer: new MemorySaver(),
});
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [{ role: "user", content: "I'm Bob" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Bob"
```
</typescript>
</fix-no-checkpointer>

<fix-infinite-loop>
<python>
在 invoke 配置中设置 recursion_limit 以防止代理无限循环。

```python
# 错误：无迭代限制 - 可能无限循环
result = agent.invoke({"messages": [("user", "Do research")]})

# 正确：在 config 中设置 recursion_limit
result = agent.invoke(
    {"messages": [("user", "Do research")]},
    config={"recursion_limit": 10},  # 在 10 步后停止
)
```
</python>
<typescript>
在 invoke 配置中设置 recursionLimit 以防止代理无限循环。

```typescript
// 错误：无迭代限制
const result = await agent.invoke({ messages: [["user", "Do research"]] });

// 正确：在 config 中设置 recursionLimit
const result = await agent.invoke(
  { messages: [["user", "Do research"]] },
  { recursionLimit: 10 }, // 在 10 步后停止
);
```
</typescript>
</fix-infinite-loop>

<fix-accessing-result-wrong>
<python>
从结果中访问 messages 数组，而不是直接访问 result.content。

```python
# 错误：尝试直接访问 result.content
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result.content)  # AttributeError!

# 正确：从结果字典中访问 messages
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result["messages"][-1].content)  # 最后一条消息内容
```
</python>
<typescript>
从结果中访问 messages 数组，而不是直接访问 result.content。

```typescript
// 错误：尝试直接访问 result.content
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.content); // undefined!

// 正确：从结果对象中访问 messages
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.messages[result.messages.length - 1].content); // 最后一条消息内容
```
</typescript>
</fix-accessing-result-wrong>
