<概述>
LangChain、LangGraph 和 Deep Agents 是 **分层** 的，不是相互竞争的选择。每一层都建立在下一层之上：

```
┌─────────────────────────────────────────┐
│              Deep Agents                │  ← 最高层：包含所有功能
│   (规划、记忆、技能、文件)     │
├─────────────────────────────────────────┤
│               LangGraph                 │  ← 协调：图、循环、状态
│    (节点、边、状态、持久化)   │
├─────────────────────────────────────────┤
│               LangChain                 │  ← 基础：模型、工具、链
│      (模型、工具、提示、RAG)      │
└─────────────────────────────────────────┘
```

选择更高层不会让你与较低层隔绝——你可以在 Deep Agents 中使用 LangGraph 图，也可以在两者中使用 LangChain 基础组件。

> **此技能应在选择其他技能或编写 agent 代码之前加载到任何项目的最顶层。** 你选择的框架决定了下一步调用哪些其他技能。

</概述>

---

## 决策指南

<决策表>

按顺序回答这些问题：

| 问题 | 是 → | 否 → |
|----------|-------|-------|
| 任务是否需要将工作分解为子任务、跨长时间会话管理文件、持久化记忆或按需加载技能？ | **Deep Agents** | ↓ |
| 任务是否需要复杂的控制流——循环、动态分支、并行工作、人工参与或自定义状态？ | **LangGraph** | ↓ |
| 这是一个单用途 agent，它接收输入、运行工具并返回结果吗？ | **LangChain** (`create_agent`) | ↓ |
| 这是一个纯模型调用、链或检索管道，没有 agent 循环吗？ | **LangChain** (链) | — |

</决策表>

---

## 框架简介

<langchain简介>

### LangChain — 当任务聚焦且自包含时使用

**最适合：**
- 使用固定工具集的单用途 agent
- RAG 管道和文档问答
- 模型调用、提示模板、输出解析
- agent 逻辑简单的快速原型

**不太适合：**
- Agent 需要在多步骤中规划
- 状态需要在多个会话中持久化
- 控制流是条件性或迭代的

**下一步调用的技能：** `langchain-models`, `langchain-rag`, `langchain-middleware`

</langchain简介>

<langgraph简介>

### LangGraph — 当你需要控制流时使用

**最适合：**
- 具有分支逻辑或循环的 agent（例如重试直到正确、反思）
- 多步骤工作流，其中不同路径取决于中间结果
- 在特定步骤中需要人工参与批准
- 并行发散/收敛（map-reduce 模式）
- 会话内调用的持久化状态

**不太适合：**
- 你希望规划、文件管理和子 agent 委托由 Deep Agents 处理（使用 Deep Agents 而不是）
- 工作流足够简单，可以使用简单 agent

**下一步调用的技能：** `langgraph-fundamentals`, `langgraph-human-in-the-loop`, `langgraph-persistence`

</langgraph简介>

<deep-agents简介>

### Deep Agents — 当任务是开放性且多维时使用

**最适合：**
- 长时间运行的任务，需要将工作分解为待办事项列表
- 需要在会话中读取、写入和管理文件的 agent
- 将子任务委托给专门的子 agent
- 按需加载特定领域的技能
- 跨多个会话持久化的记忆

**不太适合：**
- 任务简单到可以使用单用途 agent
- 你需要精确控制每个图边（直接使用 LangGraph）

**中间件——内置且可扩展：**

Deep Agents 默认附带内置的中间件层——你配置它，而不是实现它。以下预连接；你也可以在顶部添加自己的：

| 中间件 | 提供什么 | 始终启用？ |
|------------|-----------------|------------|
| `TodoListMiddleware` | `write_todos` 工具——agent 规划和跟踪多步骤任务 | ✓ |
| `FilesystemMiddleware` | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` 工具 | ✓ |
| `SubAgentMiddleware` | `task` 工具——将工作委托给命名的子 agent | ✓ |
| `SkillsMiddleware` | 从技能目录按需加载 SKILL.md 文件 | 选择性 |
| `MemoryMiddleware` | 通过 `Store` 实例在会话间实现长期记忆 | 选择性 |
| `HumanInTheLoopMiddleware` | 在敏感工具调用之前中断并请求人工批准 | 选择性 |

**下一步调用的技能：** `deep-agents-core`, `deep-agents-memory`, `deep-agents-orchestration`

</deep-agents简介>

---

## 混合层

<混合层>
由于框架是分层的，它们可以在同一个项目中组合。最常见的模式是使用 Deep Agents 作为顶层协调器，同时在需要时切换到 LangGraph 用于专门的子 agent。

### 何时混合

| 场景 | 推荐模式 |
|----------|---------------------|
| 主 agent 需要规划和记忆，但一个子任务需要精确的图控制 | Deep Agents 协调器 → LangGraph 子 agent |
| 由更广泛的 agent 调用的专用管道（例如 RAG、反思循环） | 作为工具或子 agent 封装的 LangGraph 图 |
| 高级协调但特定领域的低级图 | Deep Agents + LangGraph 编译图作为子 agent |

### 实际工作原理

一个 LangGraph 编译的图可以注册为 Deep Agents 中的子 agent。这意味着你可以构建一个严格控制流程的 LangGraph 工作流（例如检索和验证循环），并将其作为命名的子 agent 交给 Deep Agents `task` 工具——Deep Agents 协调器将其委托给它，而不关心其内部图结构。

LangChain 工具、链和检索器可以在 LangGraph 节点和 Deep Agents 工具中自由使用——它们是每个层级共享的构建块。

</混合层>

---

## 快速参考

<快速参考>

| | LangChain | LangGraph | Deep Agents |
|---|-----------|-----------|-------------|
| **控制流** | 固定（工具循环） | 自定义（图） | 管理（中间件） |
| **中间件层** | 仅回调 | ✗ 无 | ✓ 显式、可配置 |
| **规划** | ✗ | 手动 | ✓ TodoListMiddleware |
| **文件管理** | ✗ | 手动 | ✓ FilesystemMiddleware |
| **持久化记忆** | ✗ | 通过检查点 | ✓ MemoryMiddleware |
| **子 agent 委托** | ✗ | 手动 | ✓ SubAgentMiddleware |
| **按需技能** | ✗ | ✗ | ✓ SkillsMiddleware |
| **人工参与** | ✗ | 手动中断 | ✓ HumanInTheLoopMiddleware |
| **自定义图边** | ✗ | ✓ 完全控制 | 有限 |
| **设置复杂度** | 低 | 中等 | 低 |
| **灵活性** | 中等 | 高 | 中等 |

> **中间件是 LangChain（回调）和 Deep Agents（显式中间件层）特有的概念。LangGraph 没有中间件——你直接将行为连接到节点和边。**
