<概述>
深度代理包含三种编排能力：

1. **SubAgentMiddleware**：通过 `task` 工具将工作委托给专业代理
2. **TodoListMiddleware**：通过 `write_todos` 工具规划和跟踪任务
3. **HumanInTheLoopMiddleware**：在敏感操作前需要人工审批

所有这三种能力都会自动包含在 `create_deep_agent()` 中。

</概述>

---

## 子代理（任务委托）

<何时使用子代理>

| 使用子代理时 | 使用主代理时 |
|-------------|-------------|
| 任务需要专业工具 | 通用工具足够 |
| 想隔离复杂工作 | 单步操作 |
| 需要为主代理提供干净的上下文 | 上下文膨胀可接受 |

</何时使用子代理>

<子代理如何工作>
主代理拥有 `task` 工具 -> 创建新的子代理 -> 子代理自主执行 -> 返回最终报告。

**默认子代理**： "通用型" - 自动提供与主代理相同的工具/配置。

</子代理如何工作>

<自定义子代理示例>
<python>
创建一个具有学术论文搜索专业工具的 "研究者" 子代理。

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def search_papers(query: str) -> str:
    """搜索学术论文."""
    return f"找到关于 {query} 的 10 篇论文"

agent = create_deep_agent(
    subagents=[
        {
            "name": "researcher",
            "description": "进行网络研究和汇总结果",
            "system_prompt": "彻底搜索，返回简洁摘要",
            "tools": [search_papers],
        }
    ]
)

# 主代理委托：task(agent="researcher", instruction="研究 AI 趋势")
```
</python>
<typescript>
创建一个具有学术论文搜索专业工具的 "研究者" 子代理。

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchPapers = tool(
  async ({ query }) => `找到关于 ${query} 的 10 篇论文`,
  { name: "search_papers", description: "搜索论文", schema: z.object({ query: z.string() }) }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "researcher",
      description: "进行网络研究和汇总结果",
      systemPrompt: "彻底搜索，返回简洁摘要",
      tools: [searchPapers],
    }
  ]
});

// 主代理委托：task(agent="researcher", instruction="研究 AI 趋势")
```
</typescript>
</自定义子代理示例>

<带 HITL 批准的子代理示例>
<python>
配置一个在敏感操作前需要人工批准的子代理。

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    subagents=[
        {
            "name": "code-deployer",
            "description": "将代码部署到生产环境",
            "system_prompt": "在测试通过后进行部署。",
            "tools": [run_tests, deploy_to_prod],
            "interrupt_on": {"deploy_to_prod": True},  # 需要批准
        }
    ],
    checkpointer=MemorySaver()  # 必须用于中断
)
```
</python>
</带 HITL 批准的子代理示例>

<子代理是无状态的>
<python>
子代理是无状态的 - 在单次调用中提供完整指令。

```python
# 错误：子代理不会记住之前的调用
# task(agent='research', instruction='查找数据')
# task(agent='research', instruction='你找到了什么？')  # 重新开始！

# 正确：提前提供完整指令
# task(agent='research', instruction='查找 AI 数据，保存到 /research/，返回摘要')
```
</python>
<typescript>
子代理是无状态的 - 在单次调用中提供完整指令。

```typescript
// 错误：子代理不会记住之前的调用
// task research: 查找数据
// task research: 你找到了什么？  // 重新开始！

// 正确：提前提供完整指令
// task research: 查找 AI 数据，保存到 /research/，返回摘要
```
</typescript>
</子代理是无状态的>

<自定义子代理不会继承技能>
<python>
自定义子代理不会继承主代理的技能。

```python
# 错误：自定义子代理不会有主代理的技能
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # 不会继承技能
)

# 正确：明确提供技能（通用型子代理确实会继承）
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", "skills": ["/helper-skills/"], ...}]
)
```
</python>
</自定义子代理不会继承技能>

---

## TodoList（任务规划）

<何时使用 TodoList>

| 使用 TodoList 时 | 跳过 TodoList 时 |
|-----------------|-----------------|
| 复杂的多步骤任务 | 简单的单步任务 |
| 长时间运行的操作 | 快速操作（< 3 步） |

</何时使用 TodoList>

<todolist 工具>

```
write_todos(todos: list[dict]) -> None
```

每个待办事项包含：
- `content`：任务的描述
- `status`：`"pending"`、`"in_progress"`、`"completed"` 之一

</todolist 工具>

<TodoList 使用示例>
<python>
调用一个自动为多步骤任务创建待办列表的代理。

```python
from deepagents import create_deep_agent

agent = create_deep_agent()  # TodoListMiddleware 默认包含

result = agent.invoke({
    "messages": [{"role": "user", "content": "创建一个 REST API：设计模型，实现 CRUD，添加认证，编写测试"}]
}, config={"configurable": {"thread_id": "session-1"}})

# 代理的规划通过 write_todos：
# [
#   {"content": "设计数据模型", "status": "in_progress"},
#   {"content": "实现 CRUD 端点", "status": "pending"},
#   {"content": "添加认证", "status": "pending"},
#   {"content": "编写测试", "status": "pending"}
# ]
```
</python>
<typescript>
调用一个自动为多步骤任务创建待办列表的代理。

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent();  // TodoListMiddleware 默认包含

const result = await agent.invoke({
  messages: [{ role: "user", content: "创建一个 REST API：设计模型，实现 CRUD，添加认证，编写测试" }]
}, { configurable: { thread_id: "session-1" } });
```
</typescript>
</TodoList 使用示例>

<访问 TodoList 状态>
<python>
在调用后从代理的最终状态中访问待办列表。

```python
result = agent.invoke({...}, config={"configurable": {"thread_id": "session-1"}})

# 从最终状态访问待办列表
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['content']}")
```
</python>
</访问 TodoList 状态>

<TodoList 需要线程 ID>
<python>
待办列表状态需要在调用之间持久化，因此需要线程 ID。

```python
# 错误：没有线程 ID 的情况下每次都是新状态
agent.invoke({"messages": [...]})

# 正确：使用线程 ID
config = {"configurable": {"thread_id": "user-session"}}
agent.invoke({"messages": [...]}, config=config)  # 待办列表被保留
```
</python>
</TodoList 需要线程 ID>

---

## Human-in-the-Loop（人工审批工作流）

<何时使用 HITL>

| 使用 HITL 时 | 跳过 HITL 时 |
|--------------|--------------|
| 高风险操作（数据库写入、部署） | 只读操作 |
| 合规性需要人工监督 | 完全自动化工作流 |

</何时使用 HITL>

<HITL 配置示例>
<python>
配置哪些工具在执行前需要人工审批。

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={
        "write_file": True,  # 所有决策允许
        "execute_sql": {"allowed_decisions": ["approve", "reject"]},
        "read_file": False,  # 无需中断
    },
    checkpointer=MemorySaver()  # 必须用于中断
)
```
</python>
<typescript>
配置哪些工具在执行前需要人工审批。

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: {
    write_file: true,
    execute_sql: { allowedDecisions: ["approve", "reject"] },
    read_file: false,
  },
  checkpointer: new MemorySaver()  // 必须的
});
```
</typescript>
</HITL 配置示例>

<人工审批工作流示例>
<python>
完整工作流：触发中断、检查状态、批准操作、然后继续执行。

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "session-1"}}

# 第 1 步：代理提议 write_file - 执行暂停
result = agent.invoke({
    "messages": [{"role": "user", "content": "将配置写入 /prod.yaml"}]
}, config=config)

# 第 2 步：检查是否有中断
state = agent.get_state(config)
if state.next:
    print(f"待处理操作")

# 第 3 步：批准并继续
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
```
</python>
<typescript>
完整工作流：触发中断、检查状态、批准操作、然后继续执行。

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver, Command } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

// 第 1 步：代理提议 write_file - 执行暂停
let result = await agent.invoke({
  messages: [{ role: "user", content: "将配置写入 /prod.yaml" }]
}, config);

// 第 2 步：检查是否有中断
const state = await agent.getState(config);
if (state.next) {
  console.log("待处理操作");
}

// 第 3 步：批准并继续
result = await agent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }), config
);
```
</typescript>
</人工审批工作流示例>

<带反馈的拒绝示例>
<python>
拒绝待处理操作并提供反馈，提示代理尝试不同方法。

```python
result = agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "message": "先运行测试"}]}),
    config=config,
)
```
</python>
<typescript>
拒绝待处理操作并提供反馈，提示代理尝试不同方法。

```typescript
const result = await agent.invoke(
  new Command({ resume: { decisions: [{ type: "reject", message: "先运行测试" }] } }),
  config,
);
```
</typescript>
</带反馈的拒绝示例>

<执行前编辑操作参数示例>
<python>
在允许执行前编辑提议的操作参数。

```python
result = agent.invoke(
    Command(resume={"decisions": [{
        "type": "edit",
        "edited_action": {
            "name": "execute_sql",
            "args": {"query": "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"},
        },
    }]}),
    config=config,
)
```
</python>
</执行前编辑操作参数示例>

<代理能配置的边界>
### 代理能配置的

- 子代理名称、工具、模型、系统提示
- 需要审批的工具
- 每个工具允许的决策类型
- TodoList 内容和结构

### 代理不能配置的

- 工具名称（`task`、`write_todos`）
- HITL 协议（批准/编辑/拒绝结构）
- 跳过 checkpointer 要求的中断
- 使子代理状态化（它们是短暂的）

</代理能配置的边界>

<检查器必须的>
<python>
使用 interrupt_on 进行 HITL 工作流时，必须使用检查器。

```python
# 错误
agent = create_deep_agent(interrupt_on={"write_file": True})

# 正确
agent = create_deep_agent(interrupt_on={"write_file": True}, checkpointer=MemorySaver())
```
</python>
<typescript>
使用 interruptOn 进行 HITL 工作流时，必须使用检查器。

```typescript
// 错误
const agent = await createDeepAgent({ interruptOn: { write_file: true } });

// 正确
const agent = await createDeepAgent({ interruptOn: { write_file: true }, checkpointer: new MemorySaver() });
```
</typescript>
</检查器必须的>

<中断恢复需要一致的线程 ID>
<python>
要恢复中断的工作流，需要一致的线程 ID。

```python
# 错误：没有线程 ID 无法恢复
agent.invoke({"messages": [...]})

# 正确
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
# 使用相同配置的 Command 恢复
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
```
</python>
<typescript>
要恢复中断的工作流，需要一致的线程 ID。

```typescript
// 错误：没有线程 ID 无法恢复
await agent.invoke({ messages: [...] });

// 正确
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [...] }, config);
// 使用相同配置的 Command 恢复
await agent.invoke(new Command({ resume: { decisions: [{ type: "approve" }] } }), config);
```
</typescript>
</中断恢复需要一致的线程 ID>

<中断检查发生在调用之间>
<python>
中断发生在调用之间，而不是执行过程中。

```python
result = agent.invoke({...}, config=config)       # 第 1 步：触发中断
if "__interrupt__" in result:                      # 第 2 步：检查中断
    result = agent.invoke(                         # 第 3 步：恢复
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
    )
```
</python>
</中断检查发生在调用之间>
