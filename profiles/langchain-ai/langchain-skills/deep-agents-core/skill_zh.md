<概述>
Deep Agents 是一个基于 LangChain/LangGraph 构建的有观点的代理框架，内置了以下中间件：

- **任务规划**：TodoListMiddleware 用于分解复杂任务
- **上下文管理**：具有可插拔后端的文件系统工具
- **任务委托**：SubAgent 中间件用于生成专门的代理
- **长期记忆**：通过 Store 在线程间持久化存储
- **人机交互**：用于敏感操作的审批工作流
- **技能**：按需加载专业能力

代理托管程序自动提供这些功能 - 您配置，而不是实现。
</概述>

<何时使用>

| 使用 Deep Agents 时 | 使用 LangChain's create_agent 时 |
|---------------------|-----------------------------------|
| 需要规划的多步任务 | 简单、单一用途的任务 |
| 需要文件管理的较大上下文 | 上下文适合单个提示 |
| 需要专门的子代理 | 单个代理就足够 |
| 跨会话的持久记忆 | 短暂的、单次会话的工作 |

</何时使用>

<中间件选择>

| 如果您需要... | 中间件 | 备注 |
|------------------|------------|-------|
| 跟踪复杂任务 | TodoListMiddleware | 默认启用 |
| 管理文件上下文 | FilesystemMiddleware | 配置后端 |
| 委托工作 | SubAgentMiddleware | 添加自定义子代理 |
| 添加人工审批 | HumanInTheLoopMiddleware | 需要检查点器 |
| 加载技能 | SkillsMiddleware | 提供技能目录 |
| 访问记忆 | MemoryMiddleware | 需要 Store 实例 |

</中间件选择>

<基本代理示例>
<python>
使用自定义工具创建一个基本 Deep Agent 并使用用户消息调用它。

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取给定城市的天气。"""
    return f"{city}总是阳光明媚"

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    system_prompt="您是一个有帮助的助手"
)

config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "东京的天气怎么样？"}]
}, config=config)
```
</python>
<typescript>
使用自定义工具创建一个基本 Deep Agent 并使用用户消息调用它。

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ city }) => `It is always sunny in ${city}`,
  { name: "get_weather", description: "Get weather for a city", schema: z.object({ city: z.string() }) }
);

const agent = await createDeepAgent({
  model: "claude-sonnet-4-5-20250929",
  tools: [getWeather],
  systemPrompt: "You are a helpful assistant"
});

const config = { configurable: { thread_id: "user-123" } };
const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in Tokyo?" }]
}, config);
```
</typescript>
</基本代理示例>

<完整配置示例>
<python>
配置一个 Deep Agent，包括子代理、技能和持久化。

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    name="my-assistant",
    model="claude-sonnet-4-5-20250929",
    tools=[custom_tool1, custom_tool2],
    system_prompt="自定义指令",
    subagents=[research_agent, code_agent],
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    interrupt_on={"write_file": True},
    skills=["./skills/"],
    checkpointer=MemorySaver(),
    store=InMemoryStore()
)
```
</python>
<typescript>
配置一个 Deep Agent，包括子代理、技能和持久化。

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver, InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  name: "my-assistant",
  model: "claude-sonnet-4-5-20250929",
  tools: [customTool1, customTool2],
  systemPrompt: "Custom instructions",
  subagents: [researchAgent, codeAgent],
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  interruptOn: { write_file: true },
  skills: ["./skills/"],
  checkpointer: new MemorySaver(),
  store: new InMemoryStore()
});
```
</typescript>
</完整配置示例>

<内置工具>
每个 Deep Agent 都可以访问：

1. **规划**：`write_todos` - 跟踪多步任务
2. **文件系统**：`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`
3. **委托**：`task` - 生成专门的子代理
</内置工具>

---

## 技能.md 格式

<skill-md-format>
技能使用**渐进式披露** - 代理仅在相关时加载内容。

### 目录结构

```
skills/
└── my-skill/
    ├── SKILL.md        # 必须的：主技能文件
    ├── examples.py     # 可选的：支持文件
    └── templates/      # 可选的：模板
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: 清晰、具体的技能用途描述
---

# 技能名称

## 概述
技能用途的简要说明。

## 何时使用
适用条件。

## 指令
代理的逐步指导。
```
</skill-md-format>

<技能与记忆对比>

| 技能 | 记忆 (AGENTS.md) |
|--------|-------------------|
| 按需加载 | 启动时始终加载 |
| 任务特定指令 | 一般偏好 |
| 大型文档 | 紧凑的上下文 |
| 目录中的 SKILL.md | 单个 AGENTS.md 文件 |

</技能与记忆对比>

<带文件系统后端的技能示例>
<python>
设置具有技能目录和文件系统后端的代理，用于按需加载技能。

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"],
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "使用 python-testing 技能"}]
}, config={"configurable": {"thread_id": "session-1"}})
```
</python>
<typescript>
设置具有技能目录和文件系统后端的代理，用于按需加载技能。

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"],
  checkpointer: new MemorySaver()
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the python-testing skill" }]
}, { configurable: { thread_id: "session-1" } });
```
</typescript>
</带文件系统后端的技能示例>

<带 Store 后端的技能示例>
<python>
将技能内容加载到 Store 后端，适用于没有文件系统访问的环境。

```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# 将技能内容加载到 store
skill_content = """---
name: python-testing
description: 使用 pytest 的 Python 测试最佳实践
---
# Python Testing Skill
..."""

store.put(
    namespace=("filesystem",),
    key="/skills/python-testing/SKILL.md",
    value=create_file_data(skill_content)
)

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store,
    skills=["/skills/"]
)
```
</python>
</带 Store 后端的技能示例>

<边界>

### 代理可以配置的内容

- 模型选择和参数
- 额外的自定义工具
- 系统提示自定义
- 后端存储策略
- 需要审批的工具
- 具有专业工具的自定义子代理

### 代理不能配置的内容

- 核心中间件的移除（TodoList、Filesystem、SubAgent 始终存在）
- `write_todos`、`task` 或文件系统工具的名称
- SKILL.md 的 frontmatter 格式
</边界>

<修复中断检查点>
<python>
中断需要检查点器。

```python
# 错误
agent = create_deep_agent(interrupt_on={"write_file": True})

# 正确
agent = create_deep_agent(interrupt_on={"write_file": True}, checkpointer=MemorySaver())
```
</python>
<typescript>
中断需要检查点器。

```typescript
// 错误
const agent = await createDeepAgent({ interruptOn: { write_file: true } });

// 正确
const agent = await createDeepAgent({ interruptOn: { write_file: true }, checkpointer: new MemorySaver() });
```
</typescript>
</修复中断检查点>

<修复 Store 以实现记忆>
<python>
StoreBackend 需要一个 Store 实例，以在线程间实现持久记忆。

```python
# 错误
agent = create_deep_agent(backend=lambda rt: StoreBackend(rt))

# 正确
agent = create_deep_agent(backend=lambda rt: StoreBackend(rt), store=InMemoryStore())
```
</python>
<typescript>
StoreBackend 需要一个 Store 实例，以在线程间实现持久记忆。

```typescript
// 错误
const agent = await createDeepAgent({ backend: (config) => new StoreBackend(config) });

// 正确
const agent = await createDeepAgent({ backend: (config) => new StoreBackend(config), store: new InMemoryStore() });
```
</typescript>
</修复 Store 以实现记忆>

<修复对话的 thread_id>
<python>
使用一致的 thread_id 以在调用间保持对话上下文。

```python
# 错误：每个调用是隔离的
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]})
agent.invoke({"messages": [{"role": "user", "content": "我刚才说了什么？"}]})

# 正确
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [...]}, config=config)
agent.invoke({"messages": [...]}, config=config)
```
</python>
<typescript>
使用一致的 thread_id 以在调用间保持对话上下文。

```typescript
// 错误：每个调用是隔离的
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// 正确
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [...] }, config);
await agent.invoke({ messages: [...] }, config);
```
</typescript>
</修复对话的 thread_id>

<修复 frontmatter 必须项>

```markdown
# 错误：SKILL.md 中缺少 frontmatter
# My Skill
这是我的技能...

# 正确：包含 YAML frontmatter
---
name: my-skill
description: 使用 pytest fixtures 和 mocking 的 Python 测试最佳实践
---
# My Skill
这是我的技能...
```
</修复 frontmatter 必须项>

<修复技能的后端>
<python>
技能需要适当的后端从文件系统加载。

```python
# 错误：没有适当的后端，技能将不会加载
agent = create_deep_agent(skills=["./skills/"])

# 正确：使用 FilesystemBackend 加载本地技能
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
</python>
</修复技能的后端>

<修复特定技能描述>
使用具体描述以帮助代理决定何时使用技能。

```markdown
# 错误：模糊描述
---
name: helper
description: 有帮助的技能
---

# 正确：具体描述
---
name: python-testing
description: 使用 pytest fixtures、mocking 和异步模式的 Python 测试最佳实践
---
```
</修复特定技能描述>

<修复子代理技能>
<python>
技能不会被子代理继承 - 明确提供它们。

```python
# 错误：自定义子代理不会继承技能
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # 没有技能
)

# 正确：明确提供技能
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", "skills": ["/helper-skills/"], ...}]
)
```
</python>
</修复子代理技能>
