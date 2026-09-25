<概述>
生产环境 LangChain 代理的中介模式：

- **HumanInTheLoopMiddleware** / **humanInTheLoopMiddleware**：在危险工具调用前暂停以供人工批准
- **自定义中介**：拦截工具调用以进行错误处理、日志记录、重试逻辑
- **命令恢复**：在人工决策后继续执行（批准、编辑、拒绝）

**要求**：所有 HITL 工作流需要 Checkpointer + thread_id 配置。
</概述>

---

## Human-in-the-Loop

<基础 HITL 设置>
<python>
设置一个使用 HITL 中介的代理，在发送邮件前暂停以供批准。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件。"""
    return f"邮件已发送至 {to}"

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # HITL 所需
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
            }
        )
    ],
)
```
</python>
<typescript>
设置一个使用 HITL 的代理，在发送邮件前暂停以供人工批准。

```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const sendEmail = tool(
  async ({ to, subject, body }) => `邮件已发送至 ${to}`,
  {
    name: "send_email",
    description: "发送邮件",
    schema: z.object({ to: z.string(), subject: z.string(), body: z.string() }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [sendEmail],
  checkpointer: new MemorySaver(),
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: { send_email: { allowedDecisions: ["approve", "edit", "reject"] } },
    }),
  ],
});
```
</typescript>
</基础 HITL 设置>

<中断执行示例>
<python>
运行代理，检测中断，然后在人工批准后恢复执行。

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "session-1"}}

# 第一步：代理运行到需要调用工具时停止
result1 = agent.invoke({
    "messages": [{"role": "user", "content": "发送邮件至 john@example.com"}]
}, config=config)

# 检测中断
if "__interrupt__" in result1:
    print(f"等待批准：{result1['__interrupt__']}")

# 第二步：人工批准
result2 = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
```
</python>
<typescript>
运行代理，检测中断，然后在人工批准后恢复执行。

```typescript
import { Command } from "@langchain/langgraph";

const config = { configurable: { thread_id: "session-1" } };

// 第一步：代理运行到需要调用工具时停止
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "发送邮件至 john@example.com" }]
}, config);

// 检测中断
if (result1.__interrupt__) {
  console.log(`等待批准：${result1.__interrupt__}`);
}

// 第二步：人工批准
const result2 = await agent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  config
);
```
</typescript>
</中断执行示例>

<编辑工具参数示例>
<python>
在原始值需要修正时，在批准前编辑工具参数。

```python
# 人工编辑参数 — edited_action 必须包含 name + args
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {
                    "to": "alice@company.com",  # 修正的邮箱
                    "subject": "项目会议 - 已更新",
                    "body": "...",
                },
            },
        }]
    }),
    config=config
)
```
</python>
<typescript>
在原始值需要修正时，在批准前编辑工具参数。

```typescript
// 人工编辑参数 — editedAction 必须包含 name + args
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{
        type: "edit",
        editedAction: {
          name: "send_email",
          args: {
            to: "alice@company.com",  // 修正的邮箱
            subject: "项目会议 - 已更新",
            body: "...",
          },
        },
      }]
    }
  }),
  config
);
```
</typescript>
</编辑工具参数示例>

<拒绝并提供反馈示例>
<python>
拒绝一个工具调用，并提供解释拒绝原因的反馈。

```python
# 人工拒绝
result2 = agent.invoke(
    Command(resume={
        "decisions": [{
            "type": "reject",
            "feedback": "未经经理批准不能删除客户数据",
        }]
    }),
    config=config
)
```
</python>
</拒绝并提供反馈示例>

<不同工具不同策略示例>
<python>
根据风险级别为每个工具配置不同的 HITL 策略。

```python
agent = create_agent(
    model="gpt-4.1",
    tools=[send_email, read_email, delete_email],
    checkpointer=MemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "delete_email": {"allowed_decisions": ["approve", "reject"]},  # 无编辑
                "read_email": False,  # 读取不使用 HITL
            }
        )
    ],
)
```
</python>
</不同工具不同策略示例>

<可配置范围>
### 你可以配置的内容

- 哪些工具需要批准（每工具策略）
- 每个工具允许的决策（批准、编辑、拒绝）
- 自定义中介钩子：`before_model`, `after_model`, `wrap_tool_call`, `before_agent`, `after_agent`
- 工具特定中介（仅适用于某些工具）
</可配置范围>

---

## 自定义中介钩子

提供六个装饰器钩子。两种模式：

- **包装钩子** (`wrap_tool_call`, `wrap_model_call`)：`(request, handler)` — 调用 `handler(request)` 以继续，或提前返回以中断。
- **前后钩子** (`before_model`, `after_model`, `before_agent`, `after_agent`)：`(state, runtime)` — 检查或修改状态。返回 `None` 或状态更新字典。

<包装工具调用示例>
<python>
`@wrap_tool_call` 拦截工具执行。**不要使用 `yield`** — 它会创建生成器并导致 `NotImplementedError`。

```python
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def retry_middleware(request, handler):
    for attempt in range(3):
        try:
            return handler(request)
        except Exception:
            if attempt == 2:
                raise

@wrap_tool_call
def guard_middleware(request, handler):
    if request.tool_call["name"] == "dangerous_tool":
        return "此工具已被禁用"  # 中断
    return handler(request)
```
</python>
<typescript>
`createMiddleware({ wrapToolCall })` 拦截工具执行。

```typescript
import { createMiddleware } from "langchain";

const retryMiddleware = createMiddleware({
  wrapToolCall: async (request, handler) => {
    for (let attempt = 0; attempt < 3; attempt++) {
      try { return await handler(request); }
      catch (e) { if (attempt === 2) throw e; }
    }
  },
});
```
</typescript>
</包装工具调用示例>

<前后钩子示例>
<python>
`before_model` / `after_model` / `before_agent` / `after_agent` 都共享 `(state, runtime)` 签名。

```python
from langchain.agents.middleware import before_model, after_model

@before_model
def log_calls(state, runtime):
    print(f"使用 {len(state['messages'])} 条消息调用模型")

@after_model
def check_output(state, runtime):
    print(f"模型已响应")
```
</python>
<typescript>
所有前后钩子都通过 `createMiddleware` 共享相同的 `(state, runtime)` 签名。

```typescript
import { createMiddleware } from "langchain";

const loggingMiddleware = createMiddleware({
  beforeModel: (state, runtime) => {
    console.log(`使用 ${state.messages.length} 条消息调用模型`);
  },
  afterModel: (state, runtime) => {
    console.log("模型已响应");
  },
});
```
</typescript>
</前后钩子示例>

<不可配置范围>
### 你不能配置的内容

- 工具执行后中断（必须提前）
- 为 HITL 忽略检查点器要求
</不可配置范围>

<修复缺失检查点器>
<python>
HITL 中介需要一个检查点器来持久化状态。

```python
# 错误
agent = create_agent(model="gpt-4.1", tools=[send_email], middleware=[HumanInTheLoopMiddleware({...})])

# 正确
agent = create_agent(
    model="gpt-4.1", tools=[send_email],
    checkpointer=MemorySaver(),  # 必须提供
    middleware=[HumanInTheLoopMiddleware({...})]
)
```
</python>
<typescript>
HITL 需要一个检查点器来持久化状态。

```typescript
// 错误：没有检查点器
const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5", tools: [sendEmail],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { send_email: true } })],
});

// 正确：添加检查点器
const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5", tools: [sendEmail],
  checkpointer: new MemorySaver(),
  middleware: [humanInTheLoopMiddleware({ interruptOn: { send_email: true } })],
});
```
</typescript>
</修复缺失检查点器>

<修复未提供 thread_id>
<python>
使用 HITL 时始终提供 thread_id 以跟踪对话状态。

```python
# 错误
agent.invoke(input)  # 无 config!

# 正确
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
</python>
</修复未提供 thread_id>

<修复错误恢复语法>
<python>
使用 Command 类在中断后恢复执行。

```python
# 错误
agent.invoke({"resume": {"decisions": [...]}})

# 正确
from langgraph.types import Command
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
```
</python>
<typescript>
使用 Command 类在中断后恢复执行。

```typescript
// 错误
await agent.invoke({ resume: { decisions: [...] } });

// 正确
import { Command } from "@langchain/langgraph";
await agent.invoke(new Command({ resume: { decisions: [{ type: "approve" }] } }), config);
```
</typescript>
</修复错误恢复语法>
