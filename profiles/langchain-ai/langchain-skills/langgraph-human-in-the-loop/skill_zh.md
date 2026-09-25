<概述>
LangGraph 的人类参与循环模式允许您暂停图执行、将数据展示给用户，并使用他们的输入继续执行：

- **`interrupt(value)`** — 暂停执行，将值展示给调用者
- **`Command(resume=value)`** — 继续执行，将值返回给 `interrupt()`
- **检查点器** — 暂停时需要保存状态
- **线程 ID** — 需要用来识别要继续执行哪个暂停的执行

</概述>

---

## 要求

中断要正常工作，需要三个条件：

1. **检查点器** — 使用 `checkpointer=InMemorySaver()`（开发环境）或 `PostgresSaver`（生产环境）进行编译
2. **线程 ID** — 将 `{"configurable": {"thread_id": "..."}}` 传递给每个 `invoke`/`stream` 调用
3. **JSON 可序列化负载** — 传递给 `interrupt()` 的值必须是 JSON 可序列化的

---

## 基本中断 + 继续

`interrupt(value)` 暂停图。值在结果中以 `__interrupt__` 展示。`Command(resume=value)` 继续执行 — 继续的值成为 `interrupt()` 的返回值。

**关键**：当图继续执行时，节点将从 **开始处** 重新启动 — 所有 `interrupt()` 之前的代码都会重新运行。

<ex-basic-interrupt-resume>
<python>
为人类审查暂停执行，并使用 Command 继续。

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    approved: bool

def approval_node(state: State):
    # 暂停并请求批准
    approved = interrupt("Do you approve this action?")
    # 继续执行时，Command(resume=...) 会将值返回到这里
    return {"approved": approved}

checkpointer = InMemorySaver()
graph = (
    StateGraph(State)
    .add_node("approval", approval_node)
    .add_edge(START, "approval")
    .add_edge("approval", END)
    .compile(checkpointer=checkpointer)
)

config = {"configurable": {"thread_id": "thread-1"}}

# 初始运行 — 触发中断并暂停
result = graph.invoke({"approved": False}, config)
print(result["__interrupt__"])
# [Interrupt(value='Do you approve this action?')]

# 使用人类的响应继续执行
result = graph.invoke(Command(resume=True), config)
print(result["approved"])  # True
```
</python>
<typescript>
为人类审查暂停执行，并使用 Command 继续。

```typescript
import { interrupt, Command, MemorySaver, StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  approved: z.boolean().default(false),
});

const approvalNode = async (state: typeof State.State) => {
  // 暂停并请求批准
  const approved = interrupt("Do you approve this action?");
  // 继续执行时，Command({ resume }) 会将值返回到这里
  return { approved };
};

const checkpointer = new MemorySaver();
const graph = new StateGraph(State)
  .addNode("approval", approvalNode)
  .addEdge(START, "approval")
  .addEdge("approval", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "thread-1" } };

// 初始运行 — 触发中断并暂停
let result = await graph.invoke({ approved: false }, config);
console.log(result.__interrupt__);
// [{ value: 'Do you approve this action?', ... }]

// 使用人类的响应继续执行
result = await graph.invoke(new Command({ resume: true }), config);
console.log(result.approved);  // true
```
</typescript>
</ex-basic-interrupt-resume>

---

## 批准工作流

常见模式：中断以显示草稿，然后根据人类的决定进行路由。

<ex-approval-workflow>
<python>
为人类审查中断，然后根据决定路由发送或结束。

```python
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from typing import Literal
from typing_extensions import TypedDict

class EmailAgentState(TypedDict):
    email_content: str
    draft_response: str
    classification: dict

def human_review(state: EmailAgentState) -> Command[Literal["send_reply", "__end__"]]:
    """使用 interrupt 进行人类审查，并根据决定进行路由。"""
    classification = state.get("classification", {})

    # interrupt() 必须首先执行 — 它之前的任何代码在继续执行时都会重新运行
    human_decision = interrupt({
        "email_id": state.get("email_content", ""),
        "draft_response": state.get("draft_response", ""),
        "urgency": classification.get("urgency"),
        "action": "Please review and approve/edit this response"
    })

    # 处理人类的决定
    if human_decision.get("approved"):
        return Command(
            update={"draft_response": human_decision.get("edited_response", state.get("draft_response", ""))},
            goto="send_reply"
        )
    else:
        # 拒绝 — 人类将直接处理
        return Command(update={}, goto=END)
```
</python>
<typescript>
为人类审查中断，然后根据决定路由发送或结束。

```typescript
import { interrupt, Command, END, GraphNode } from "@langchain/langgraph";

const humanReview: GraphNode<typeof EmailAgentState> = async (state) => {
  const classification = state.classification!;

  // interrupt() 必须首先执行 — 它之前的任何代码在继续执行时都会重新运行
  const humanDecision = interrupt({
    emailId: state.emailContent,
    draftResponse: state.responseText,
    urgency: classification.urgency,
    action: "Please review and approve/edit this response",
  });

  // 处理人类的决定
  if (humanDecision.approved) {
    return new Command({
      update: { responseText: humanDecision.editedResponse || state.responseText },
      goto: "sendReply",
    });
  } else {
    return new Command({ update: {}, goto: END });
  }
};
```
</typescript>
</ex-approval-workflow>

---

## 验证循环

在循环中使用 `interrupt()` 来验证人类输入，并在无效时重新提示。

<ex-validation-loop>
<python>
在循环中验证人类输入，直到有效为止重新提示。

```python
from langgraph.types import interrupt

def get_age_node(state):
    prompt = "What is your age?"

    while True:
        answer = interrupt(prompt)

        # 验证输入
        if isinstance(answer, int) and answer > 0:
            break
        else:
            # 无效输入 — 使用更具体的提示再次提示
            prompt = f"'{answer}' is not a valid age. Please enter a positive number."

    return {"age": answer}
```

每个 `Command(resume=...)` 调用都会提供下一个答案。如果无效，循环会使用更清晰的提示重新中断。

```python
config = {"configurable": {"thread_id": "form-1"}}
first = graph.invoke({"age": None}, config)
# __interrupt__: "What is your age?"

retry = graph.invoke(Command(resume="thirty"), config)
# __interrupt__: "'thirty' is not a valid age..."

final = graph.invoke(Command(resume=30), config)
print(final["age"])  # 30
```
</python>
<typescript>
在循环中验证人类输入，直到有效为止重新提示。

```typescript
import { interrupt } from "@langchain/langgraph";

const getAgeNode = (state: typeof State.State) => {
  let prompt = "What is your age?";

  while (true) {
    const answer = interrupt(prompt);

    // 验证输入
    if (typeof answer === "number" && answer > 0) {
      return { age: answer };
    } else {
      // 无效输入 — 使用更具体的提示再次提示
      prompt = `'${answer}' is not a valid age. Please enter a positive number.`;
    }
  }
};
```
</typescript>
</ex-validation-loop>

---

## 多个中断

当并行分支都调用 `interrupt()` 时，通过将每个中断 ID 映射到其继续值，可以在单个调用中继续所有中断。

<ex-multiple-interrupts>
<python>
通过映射中断 ID 到值来继续多个并行中断。

```python
from typing import Annotated, TypedDict
import operator
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command, interrupt

class State(TypedDict):
    vals: Annotated[list[str], operator.add]

def node_a(state):
    answer = interrupt("question_a")
    return {"vals": [f"a:{answer}"]}

def node_b(state):
    answer = interrupt("question_b")
    return {"vals": [f"b:{answer}"]}

graph = (
    StateGraph(State)
    .add_node("a", node_a)
    .add_node("b", node_b)
    .add_edge(START, "a")
    .add_edge(START, "b")
    .add_edge("a", END)
    .add_edge("b", END)
    .compile(checkpointer=InMemorySaver())
)

config = {"configurable": {"thread_id": "1"}}

# 两个并行节点都触发中断并暂停
result = graph.invoke({"vals": []}, config)
# result["__interrupt__"] 包含两个带有 ID 的 Interrupt 对象

# 使用映射的 id -> 值一次性继续所有挂起的中断
resume_map = {
    i.id: f"answer for {i.value}"
    for i in result["__interrupt__"]
}
result = graph.invoke(Command(resume=resume_map), config)
# result["vals"] = ["a:answer for question_a", "b:answer for question_b"]
```
</python>
<typescript>
通过映射中断 ID 到值来继续多个并行中断。

```typescript
import { Command, END, MemorySaver, START, StateGraph, interrupt, isInterrupted, INTERRUPT, Annotation } from "@langchain/langgraph";

const State = Annotation.Root({
  vals: Annotation<string[]>({
    reducer: (left, right) => left.concat(Array.isArray(right) ? right : [right]),
    default: () => [],
  }),
});

function nodeA(_state: typeof State.State) {
  const answer = interrupt("question_a") as string;
  return { vals: [`a:${answer}`] };
}

function nodeB(_state: typeof State.State) {
  const answer = interrupt("question_b") as string;
  return { vals: [`b:${answer}`] };
}

const graph = new StateGraph(State)
  .addNode("a", nodeA)
  .addNode("b", nodeB)
  .addEdge(START, "a")
  .addEdge(START, "b")
  .addEdge("a", END)
  .addEdge("b", END)
  .compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "1" } };

const interruptedResult = await graph.invoke({ vals: [] }, config);

// 一次性继续所有挂起的中断
const resumeMap: Record<string, string> = {};
if (isInterrupted(interruptedResult)) {
  for (const i of interruptedResult[INTERRUPT]) {
    if (i.id != null) {
      resumeMap[i.id] = `answer for ${i.value}`;
    }
  }
}
const result = await graph.invoke(new Command({ resume: resumeMap }), config);
// result.vals = ["a:answer for question_a", "b:answer for question_b"]
```
</typescript>
</ex-multiple-interrupts>

用户可修复的错误使用 `interrupt()` 暂停并收集缺失数据 — 这就是本技能涵盖的模式。有关完整的四级错误处理策略（RetryPolicy、Command 错误循环等），请参阅 **基础知识** 技能。

---

## 中断前的副作用必须是幂等的

当图继续执行时，节点将从 **开始处** 重新启动 — 所有 `interrupt()` 之前的代码都会重新运行。在子图中，父节点和子图节点都会重新执行。

<idempotency-rules>

**做：**
- 在 `interrupt()` 之前使用 **upsert**（而不是 insert）操作
- 使用 **check-before-create** 模式
- 尽可能将副作用放在 `interrupt()` 之后
- 将副作用分离到自己的节点中

**不要：**
- 在 `interrupt()` 之前创建新记录 — 每次继续都会产生重复
- 在 `interrupt()` 之前向列表追加 — 每次继续都会产生重复条目

</idempotency-rules>

<ex-idempotent-patterns>
<python>
中断前幂等操作 vs 非幂等（错误）。

```python
# 好：upsert 是幂等的 — 在中断前安全
def node_a(state: State):
    db.upsert_user(user_id=state["user_id"], status="pending_approval")
    approved = interrupt("Approve this change?")
    return {"approved": approved}

# 好：副作用在 interrupt 之后 — 只运行一次
def node_a(state: State):
    approved = interrupt("Approve this change?")
    if approved:
        db.create_audit_log(user_id=state["user_id"], action="approved")
    return {"approved": approved}

# 错：插入会在每次继续时产生重复！
def node_a(state: State):
    audit_id = db.create_audit_log({  # 在继续时再次运行！
        "user_id": state["user_id"],
        "action": "pending_approval",
    })
    approved = interrupt("Approve this change?")
    return {"approved": approved}
```
</python>
<typescript>
中断前幂等操作 vs 非幂等（错误）。

```typescript
// 好：upsert 是幂等的 — 在中断前安全
const nodeA = async (state: typeof State.State) => {
  await db.upsertUser({ userId: state.userId, status: "pending_approval" });
  const approved = interrupt("Approve this change?");
  return { approved };
};

// 好：副作用在 interrupt 之后 — 只运行一次
const nodeA = async (state: typeof State.State) => {
  const approved = interrupt("Approve this change?");
  if (approved) {
    await db.createAuditLog({ userId: state.userId, action: "approved" });
  }
  return { approved };
};

// 错：插入会在每次继续时产生重复！
const nodeA = async (state: typeof State.State) => {
  await db.createAuditLog({  // 在继续时再次运行！
    userId: state.userId,
    action: "pending_approval",
  });
  const approved = interrupt("Approve this change?");
  return { approved };
};
```
</typescript>
</ex-idempotent-patterns>

<subgraph-interrupt-re-execution>

### 子图在继续时重新执行

当子图包含 `interrupt()` 时，继续执行会重新执行调用子图的父节点和调用 `interrupt()` 的子图节点：

<python>

```python
def node_in_parent_graph(state: State):
    some_code()  # <-- 在继续时重新执行
    subgraph_result = subgraph.invoke(some_input)
    # ...

def node_in_subgraph(state: State):
    some_other_code()  # <-- 也将在继续时重新执行
    result = interrupt("What's your name?")
    # ...
```
</python>
<typescript>

```typescript
async function nodeInParentGraph(state: State) {
  someCode();  // <-- 在继续时重新执行
  const subgraphResult = await subgraph.invoke(someInput);
  // ...
}

async function nodeInSubgraph(state: State) {
  someOtherCode();  // <-- 也将在继续时重新执行
  const result = interrupt("What's your name?");
  // ...
}
```
</typescript>
</subgraph-interrupt-re-execution>

---

## Command(resume) 警告

`Command(resume=...)` 是作为 `invoke()`/`stream()` 输入的 **唯一** 命令模式。**不要** 将 `Command(update=...)` 作为输入 — 它将从最新检查点继续执行，图看起来会卡住。有关完整反模式解释，请参阅基础知识技能。

---

## 修复

<fix-checkpointer-required-for-interrupts>
<python>
中断功能需要检查点器。

```python
# 错误
graph = builder.compile()

# 正确
graph = builder.compile(checkpointer=InMemorySaver())
```
</python>
<typescript>
中断功能需要检查点器。

```typescript
// 错误
const graph = builder.compile();

// 正确
const graph = builder.compile({ checkpointer: new MemorySaver() });
```
</typescript>
</fix-checkpointer-required-for-interrupts>

<fix-resume-with-command>
<python>
使用 Command 从中断中继续（普通字典会重新启动图）。

```python
# 错误
graph.invoke({"resume_data": "approve"}, config)

# 正确
graph.invoke(Command(resume="approve"), config)
```
</python>
<typescript>
使用 Command 从中断中继续（普通对象会重新启动图）。

```typescript
// 错误
await graph.invoke({ resumeData: "approve" }, config);

// 正确
await graph.invoke(new Command({ resume: "approve" }), config);
```
</typescript>
</fix-resume-with-command>

<boundaries>
### 你不应该做的事情

- 没有检查点器使用中断 — 将失败
- 使用不同的线程 ID 继续执行 — 创建新线程而不是继续
- 将 `Command(update=...)` 作为 invoke 输入 — 图看起来会卡住（使用普通字典）
- 在 `interrupt()` 之前执行非幂等副作用 — 在继续时会产生重复
- 假设 `interrupt()` 之前的代码只运行一次 — 它在每次继续时都会重新运行
</boundaries>
