---
name: langgraph-persistence
description: 在您的LangGraph需要持久化状态、记忆对话、穿越历史或配置子图检查点作用域时，请调用此技能。涵盖检查点器、线程ID、时间旅行、存储以及子图持久化模式。
---

<概述>
LangGraph 的持久化层通过检查点记录图状态，实现持久化执行：

- **检查点记录器（Checkpointer）**：在每个超级步骤保存/加载图状态
- **线程 ID（Thread ID）**：识别独立的检查点序列（对话）
- **存储（Store）**：跨线程内存，用于用户偏好和事实

**两种内存类型：**
- **短期**（检查点记录器）：线程范围对话历史
- **长期**（存储）：跨线程用户偏好和事实

<检查点记录器选择>

| 检查点记录器 | 应用场景 | 生产就绪 |
|--------------|----------|------------------|
| `InMemorySaver` | 测试、开发 | 否 |
| `SqliteSaver` | 本地开发 | 部分就绪 |
| `PostgresSaver` | 生产环境 | 是 |

---

## 检查点记录器设置

<基础持久化示例>
<python>
设置具有内存检查点和基于线程的状态持久化的基本图。

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def add_message(state: State) -> dict:
    return {"messages": ["Bot response"]}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("respond", add_message)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)  # 在编译时传递
)

# 始终提供 thread_id
config = {"configurable": {"thread_id": "conversation-1"}}

result1 = graph.invoke({"messages": ["Hello"]}, config)
print(len(result1["messages"]))  # 2

result2 = graph.invoke({"messages": ["How are you?"]}, config)
print(len(result2["messages"]))  # 4 (之前 + 新的)
```
</python>
<typescript>
设置具有内存检查点和基于线程的状态持久化的基本图。

```typescript
import { MemorySaver, StateGraph, StateSchema, MessagesValue, START, END } from "@langchain/langgraph";
import { HumanMessage } from "@langchain/core/messages";

const State = new StateSchema({ messages: MessagesValue });

const addMessage = async (state: typeof State.State) => {
  return { messages: [{ role: "assistant", content: "Bot response" }] };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("respond", addMessage)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });

// 始终提供 thread_id
const config = { configurable: { thread_id: "conversation-1" } };

const result1 = await graph.invoke({ messages: [new HumanMessage("Hello")] }, config);
console.log(result1.messages.length);  // 2

const result2 = await graph.invoke({ messages: [new HumanMessage("How are you?")] }, config);
console.log(result2.messages.length);  // 4 (之前 + 新的)
```
</typescript>
</基础持久化示例>

<生产 PostgreSQL 示例>
<python>
为生产部署配置基于 PostgreSQL 的检查点记录。

```python
import os
from langgraph.checkpoint.postgres import PostgresSaver

# 部署时运行一次（不是在应用程序启动时）：
#   PostgresSaver.from_conn_string(os.environ["DATABASE_URL"]).setup()

with PostgresSaver.from_conn_string(os.environ["DATABASE_URL"]) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```
</python>
<typescript>
为生产部署配置基于 PostgreSQL 的检查点记录。

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

// 部署时运行一次（不是在应用程序启动时）：
//   await PostgresSaver.fromConnString(process.env.DATABASE_URL!).setup();

const checkpointer = PostgresSaver.fromConnString(process.env.DATABASE_URL!);
const graph = builder.compile({ checkpointer });
```
</typescript>
</生产 PostgreSQL 示例>

---

## 线程管理

<分离线程示例>
<python>
演示不同线程 ID 之间的隔离状态。

```python
# 不同线程维护独立状态
alice_config = {"configurable": {"thread_id": "user-alice"}}
bob_config = {"configurable": {"thread_id": "user-bob"}}

graph.invoke({"messages": ["Hi from Alice"]}, alice_config)
graph.invoke({"messages": ["Hi from Bob"]}, bob_config)

# Alice 的状态与 Bob 的状态隔离
```
</python>
<typescript>
演示不同线程 ID 之间的隔离状态。

```typescript
// 不同线程维护独立状态
const aliceConfig = { configurable: { thread_id: "user-alice" } };
const bobConfig = { configurable: { thread_id: "user-bob" } };

await graph.invoke({ messages: [new HumanMessage("Hi from Alice")] }, aliceConfig);
await graph.invoke({ messages: [new HumanMessage("Hi from Bob")] }, bobConfig);

// Alice 的状态与 Bob 的状态隔离
```
</typescript>
</分离线程示例>

---

## 状态历史与时间旅行

<从检查点恢复示例>
<python>
时间旅行：浏览检查点历史，从过去的状态重新播放或分叉。

```python
config = {"configurable": {"thread_id": "session-1"}}

result = graph.invoke({"messages": ["start"]}, config)

# 浏览检查点历史
states = list(graph.get_state_history(config))

# 从过去的检查点重新播放
past = states[-2]
result = graph.invoke(None, past.config)  # None = 从检查点恢复

# 或者分叉：在过去的检查点更新状态，然后恢复
fork_config = graph.update_state(past.config, {"messages": ["edited"]})
result = graph.invoke(None, fork_config)
```
</python>
<typescript>
时间旅行：浏览检查点历史，从过去的状态重新播放或分叉。

```typescript
const config = { configurable: { thread_id: "session-1" } };

const result = await graph.invoke({ messages: ["start"] }, config);

// 浏览检查点历史（异步可迭代，收集到数组）
const states: Awaited<ReturnType<typeof graph.getState>>[] = [];
for await (const state of graph.getStateHistory(config)) {
  states.push(state);
}

// 从过去的检查点重新播放
const past = states[states.length - 2];
const replayed = await graph.invoke(null, past.config);  // null = 从检查点恢复

// 或者分叉：在过去的检查点更新状态，然后恢复
const forkConfig = await graph.updateState(past.config, { messages: ["edited"] });
const forked = await graph.invoke(null, forkConfig);
```
</typescript>
</从检查点恢复示例>

<手动更新状态示例>
<python>
在恢复执行之前手动更新图状态。

```python
config = {"configurable": {"thread_id": "session-1"}}

# 恢复前修改状态
graph.update_state(config, {"data": "manually_updated"})

# 使用更新后的状态恢复
result = graph.invoke(None, config)
```
</python>
<typescript>
在恢复执行之前手动更新图状态。

```typescript
const config = { configurable: { thread_id: "session-1" } };

// 恢复前修改状态
await graph.updateState(config, { data: "manually_updated" });

// 使用更新后的状态恢复
const result = await graph.invoke(null, config);
```
</typescript>
</手动更新状态示例>

---

## 子图检查点记录器作用域

在编译子图时，`checkpointer` 参数控制持久化行为。这对于使用中断、需要多轮记忆或并行运行的子图至关重要。

<子图检查点记录器作用域表>

| 功能 | `checkpointer=False` | `None`（默认） | `True` |
|---|---|---|---|
| 中断（HITL） | 否 | 是 | 是 |
| 多轮记忆 | 否 | 否 | 是 |
| 多次调用（不同子图） | 是 | 是 | 警告（可能存在命名空间冲突） |
| 多次调用（相同子图） | 是 | 是 | 否 |
| 状态检查 | 否 | 警告（仅当前调用） | 是 |

<何时使用每种模式>

### 何时使用每种模式

- **`checkpointer=False`** — 子图不需要中断或持久化。最简单的选项，没有检查点开销。
- **`None`（默认 / 省略 `checkpointer`）** — 子图需要 `interrupt()` 但不需要跨调用记忆。每次调用都从新鲜状态开始，但可以暂停/恢复。并行执行工作，因为每个调用都获得唯一的命名空间。
- **`checkpointer=True`** — 子图需要跨调用记住状态（多轮对话）。每次调用都会从上次结束的地方继续。

<警告：并行状态子图>

**警告**：状态子图（`checkpointer=True`）不支持在单个节点内多次调用相同的子图实例——调用会写入相同的检查点命名空间并冲突。

<子图检查点记录器模式示例>
<python>
为你的子图选择正确的检查点记录器模式。

```python
# 不需要中断——退出检查点记录
subgraph = subgraph_builder.compile(checkpointer=False)

# 需要中断但不需要跨调用持久化（默认）
subgraph = subgraph_builder.compile()

# 需要跨调用持久化（有状态）
subgraph = subgraph_builder.compile(checkpointer=True)
```
</python>
<typescript>
为你的子图选择正确的检查点记录器模式。

```typescript
// 不需要中断——退出检查点记录
const subgraph = subgraphBuilder.compile({ checkpointer: false });

// 需要中断但不需要跨调用持久化（默认）
const subgraph = subgraphBuilder.compile();

// 需要跨调用持久化（有状态）
const subgraph = subgraphBuilder.compile({ checkpointer: true });
```
</typescript>
</子图检查点记录器模式示例>

<并行子图命名空间>

### 并行子图命名空间

当多个**不同**的状态子图并行运行时，将每个子图包装在自己的 `StateGraph` 中，并使用唯一的节点名称以实现稳定的命名空间隔离：

<python>

```python
from langgraph.graph import MessagesState, StateGraph

def create_sub_agent(model, *, name, **kwargs):
    """使用唯一节点名称包装代理以实现命名空间隔离."""
    agent = create_agent(model=model, name=name, **kwargs)
    return (
        StateGraph(MessagesState)
        .add_node(name, agent)  # 唯一名称 -> 稳定命名空间
        .add_edge("__start__", name)
        .compile()
    )

fruit_agent = create_sub_agent(
    "gpt-4.1-mini", name="fruit_agent",
    tools=[fruit_info], prompt="...", checkpointer=True,
)
veggie_agent = create_sub_agent(
    "gpt-4.1-mini", name="veggie_agent",
    tools=[veggie_info], prompt="...", checkpointer=True,
)
```
</python>
<typescript>

```typescript
import { StateGraph, StateSchema, MessagesValue, START } from "@langchain/langgraph";

function createSubAgent(model: string, { name, ...kwargs }: { name: string; [key: string]: any }) {
  const agent = createAgent({ model, name, ...kwargs });
  return new StateGraph(new StateSchema({ messages: MessagesValue }))
    .addNode(name, agent)  // 唯一名称 -> 稳定命名空间
    .addEdge(START, name)
    .compile();
}

const fruitAgent = createSubAgent("gpt-4.1-mini", {
  name: "fruit_agent", tools: [fruitInfo], prompt: "...", checkpointer: true,
});
const veggieAgent = createSubAgent("gpt-4.1-mini", {
  name: "veggie_agent", tools: [veggieInfo], prompt: "...", checkpointer: true,
});
```
</typescript>

注意：作为节点添加的子图（通过 `add_node`）已经自动获得基于名称的命名空间，不需要这个包装器。

</并行子图命名空间>

---

## 长期记忆（存储）

<长期记忆存储示例>
<python>
使用存储（Store）作为跨线程内存，以跨对话共享用户偏好。

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# 保存用户偏好（跨所有线程可用）
store.put(("alice", "preferences"), "language", {"preference": "简短回复"})

# 带存储的节点——通过运行时访问
from langgraph.runtime import Runtime

def respond(state, runtime: Runtime):
    prefs = runtime.store.get((state["user_id"], "preferences"), "language")
    return {"response": f"使用偏好：{prefs.value}"}

# 同时编译检查点记录器和存储
graph = builder.compile(checkpointer=checkpointer, store=store)

# 两个线程访问相同的长期记忆
graph.invoke({"user_id": "alice"}, {"configurable": {"thread_id": "thread-1"}})
graph.invoke({"user_id": "alice"}, {"configurable": {"thread_id": "thread-2"}})  # 相同的偏好！
```
</python>
<typescript>
使用存储（Store）作为跨线程内存，以跨对话共享用户偏好。

```typescript
import { MemoryStore } from "@langchain/langgraph";

const store = new MemoryStore();

// 保存用户偏好（跨所有线程可用）
await store.put(["alice", "preferences"], "language", { preference: "简短回复" });

// 带存储的节点——通过运行时访问
const respond = async (state: typeof State.State, runtime: any) => {
  const item = await runtime.store?.get(["alice", "preferences"], "language");
  return { response: `使用偏好：${item?.value?.preference}` };
};

// 同时编译检查点记录器和存储
const graph = builder.compile({ checkpointer, store });

// 两个线程访问相同的长期记忆
await graph.invoke({ userId: "alice" }, { configurable: { thread_id: "thread-1" } });
await graph.invoke({ userId: "alice" }, { configurable: { thread_id: "thread-2" } });  // 相同的偏好！
```
</typescript>
</长期记忆存储示例>

<存储操作示例>
<python>
基本存储操作：put、get、搜索和删除。

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

store.put(("user-123", "facts"), "location", {"city": "San Francisco"})  # Put
item = store.get(("user-123", "facts"), "location")  # Get
results = store.search(("user-123", "facts"), filter={"city": "San Francisco"})  # Search
store.delete(("user-123", "facts"), "location")  # Delete
```
</python>
</存储操作示例>

---

## 修复

<修复：线程 ID 必须提供>
<python>
始终在配置中提供 thread_id 以启用状态持久化。

```python
# 错误：没有 thread_id - 状态不持久化！
graph.invoke({"messages": ["Hello"]})
graph.invoke({"messages": ["What did I say?"]})  # 不记得！

# 正确：始终提供 thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"messages": ["Hello"]}, config)
graph.invoke({"messages": ["What did I say?"]}, config)  # 记得！
```
</python>
<typescript>
始终在配置中提供 thread_id 以启用状态持久化。

```typescript
// 错误：没有 thread_id - 状态不持久化！
await graph.invoke({ messages: [new HumanMessage("Hello")] });
await graph.invoke({ messages: [new HumanMessage("What did I say?")] });  // 不记得！

// 正确：始终提供 thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ messages: [new HumanMessage("Hello")] }, config);
await graph.invoke({ messages: [new HumanMessage("What did I say?")] }, config);  // 记得！
```
</typescript>
</修复：线程 ID 必须提供>

<修复：内存不适用于生产>
<python>
使用 PostgresSaver 而不是 InMemorySaver 用于生产持久化。

```python
# 错误：进程重启时数据丢失
checkpointer = InMemorySaver()  # 仅内存！

# 正确：使用持久化存储用于生产
from langgraph.checkpoint.postgres import PostgresSaver
with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()  # 仅在首次使用时需要以创建表
    graph = builder.compile(checkpointer=checkpointer)
```
</python>
<typescript>
使用 PostgresSaver 而不是 MemorySaver 用于生产持久化。

```typescript
// 错误：进程重启时数据丢失
const checkpointer = new MemorySaver();  // 仅内存！

// 正确：使用持久化存储用于生产
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = PostgresSaver.fromConnString("postgresql://...");
await checkpointer.setup(); // 仅在首次使用时需要以创建表
```
</typescript>
</修复：内存不适用于生产>

<fix-update-state-with-reducers>
<python>
使用 Overwrite 来替换状态值，而不是通过 reducers 传递。

```python
from langgraph.types import Overwrite

# 带有 reducer 的状态：items: Annotated[list, operator.add]
# 当前状态：{"items": ["A", "B"]}

# update_state 传递通过 reducers
graph.update_state(config, {"items": ["C"]})  # 结果：["A", "B", "C"] - 追加！

# 要替换，请使用 Overwrite
graph.update_state(config, {"items": Overwrite(["C"])})  # 结果：["C"] - 替换
```
</python>
<typescript>
使用 Overwrite 来替换状态值，而不是通过 reducers 传递。

```typescript
import { Overwrite } from "@langchain/langgraph";

// 带有 reducer 的状态：items 使用 concat reducer
// 当前状态：{ items: ["A", "B"] }

// updateState 传递通过 reducers
await graph.updateState(config, { items: ["C"] });  // 结果：["A", "B", "C"] - 追加！

// 要替换，请使用 Overwrite
await graph.updateState(config, { items: new Overwrite(["C"]) });  // 结果：["C"] - 替换
```
</typescript>
</fix-update-state-with-reducers>

<fix-store-injection>
<python>
通过图节点中的 Runtime 对象访问 store。

```python
# 错误：节点中不可用 store
def my_node(state):
    store.put(...)  # NameError! store 未定义

# 正确：通过 runtime 访问 store
from langgraph.runtime import Runtime

def my_node(state, runtime: Runtime):
    runtime.store.put(...)  # 正确的 store 实例
```
</python>
<typescript>
通过图节点中的 runtime 参数访问 store。

```typescript
// 错误：节点中不可用 store
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// 正确：通过 runtime 访问 store
const myNode = async (state, runtime) => {
  await runtime.store?.put(...);  // 正确的 store 实例
};
```
</typescript>
</fix-store-injection>

<boundaries>
### 你不应该做的事情

- 在生产中使用 `InMemorySaver` — 重启时数据会丢失；使用 `PostgresSaver`
- 忘记 `thread_id` — 没有它状态不会持久化
- 期望 `update_state` 跳过 reducers — 它会传递它们；使用 `Overwrite` 来替换
- 在一个节点内并行运行相同的状态子图 (`checkpointer=True`) — 命名空间冲突
- 直接在节点中访问 store — 通过 `Runtime` 参数使用 `runtime.store`
</boundaries>
