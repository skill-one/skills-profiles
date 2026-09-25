<概述>
LangGraph 的持久化层通过检查点记录图状态，实现持久化执行：

- **检查点记录器（Checkpointer）**：在每次超级步骤（super-step）时保存/加载图状态
- **线程 ID（Thread ID）**：识别独立的检查点序列（对话）
- **存储（Store）**：跨线程内存，用于用户偏好设置和事实信息

**两种内存类型：**
- **短期**（检查点记录器）：线程范围对话历史
- **长期**（存储）：跨线程用户偏好设置和事实信息

</概述>

<检查点记录器选择>

| 检查点记录器 | 用例 | 生产就绪 |
|--------------|----------|------------------|
| `InMemorySaver` | 测试、开发 | 否 |
| `SqliteSaver` | 本地开发 | 部分 |
| `PostgresSaver` | 生产 | 是 |

</检查点记录器选择>

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

# 必须始终提供 thread_id
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

// 必须始终提供 thread_id
const config = { configurable: { thread_id: "conversation-1" } };

const result1 = await graph.invoke({ messages: [new HumanMessage("Hello")] }, config);
console.log(result1.messages.length);  // 2

const result2 = await graph.invoke({ messages: [new HumanMessage("How are you?")] }, config);
console.log(result2.messages.length);  // 4 (之前 + 新的)
```
</typescript>
</基础持久化示例>

<生产 PostgreSQL 持久化示例>
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
</生产 PostgreSQL 持久化示例>

---

## 线程管理

<分离线程示例>
<python>
演示不同线程 ID 之间的隔离状态。

```python
# 不同线程维护分离的状态
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
// 不同线程维护分离的状态
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
时间旅行：浏览检查点历史并从过去的状
