---
name: ecosystem-primer
description: 在使用 LangChain、LangGraph 或 Deep Agents 构建任何 LangChain/LangGraph/Deep Agents 代理项目之前，请先使用 INVOKE FIRST，然后再咨询其他技能或编写任何代理代码。这是获取最新框架选择信息（LangChain 与 LangGraph 与 Deep Agents 与混合组合）、代理模式、安装、环境设置以及下一步加载哪个技能的必要起点。
---

<概述>
LangChain Inc. 维护着三个分层开源工具用于构建代理，以及用于可观察性的 LangSmith。该工具栈自上而下：

- **深度代理**（顶层，*套件*）— 基于 LangChain + LangGraph 构建的包含所有电池的工具包。开箱即用，包含规划、文件管理、子代理生成和内存。
- **LangGraph**（中间层，*运行时*）— 用于持久执行的底层编排、自定义控制流和有状态工作流。LangChain 代理在 LangGraph 之上运行。
- **LangChain**（底层，*框架*）— 模型、工具和代理循环的抽象。与提供者无关，最容易开始使用。
- **LangSmith**（横切）— 可观察性和评估平台。与框架无关；始终建议与上述任何一项一起使用。

高层依赖于低层，但你不需要直接使用低层。深度代理为你提供 LangGraph 的持久执行，而无需编写图代码。LangChain 为你提供模型和工具，而无需管理图边。

</概述>

---

## 第 1 步 — 选择你的工具

<决策表>

按顺序评估这些条件，并在第一个匹配项处停止：

1. 如果任务需要规划、跨长时间段的文件管理、持久内存、子代理委派或按需技能 → **深度代理**
2. 否则，如果任务需要自定义控制流（确定性循环、分支逻辑）→ **LangGraph**
3. 否则，如果它是一个具有固定工具集的单用途代理 → **LangChain** (`create_agent` 函数)
4. 否则，如果它是一个纯模型调用、检索管道或无代理循环的简单提示链 → **LangChain** (直接模型 / 链)

这是你的 **层**。但是你还没有完成：在步骤 4 中稍后，你必须在使用任何代理代码之前加载特定于层的技能。

</决策表>

---

## 工具简介

<langchain简介>

### LangChain — 代理框架

**最适合：**
- 具有固定工具集的单用途代理
- RAG 管道和文档问答
- 模型调用、提示模板、结构化输出

**不太理想时：**
- 代理需要在多个步骤中规划或管理大型上下文
- 控制流是条件性的、迭代的或并行的
- 状态必须在会话之间持续

所有 LangChain 代理都使用 `create_agent(model, tools=[...])`。

</langchain简介>

<langgraph简介>

### LangGraph — 代理运行时

**最适合：**
- 自定义控制流 — 确定性循环、反射循环、并行发散
- 结合确定性和代理步骤的复杂工作流
- 人类参与循环，具有精确的中断和恢复点
- 必须在失败后存活或跨越长时间段的状态

**不太理想时：**
- 你希望开箱即用规划、文件管理和子代理委派（使用深度代理代替）
- 工作流简单到足以使用直接的工具循环

所有 LangGraph 图都使用 `StateGraph(State)`，具有明确的节点、边和条件边。

</langgraph简介>

<deep-agents简介>

### Deep Agents — 代理套件

**最适合：**
- 需要规划和分解的长时间运行任务
- 在会话中读取、写入和管理文件的代理
- 将子任务委派给专门的子代理
- 跨会话的持久内存
- 按需加载特定于领域的技能

**不太理想时：**
- 任务简单到足以使用单用途代理
- 你需要对每个图边进行精确的手工控制（直接使用 LangGraph）

所有深度代理都使用 `create_deep_agent(model, tools=[...])`。

</deep-agents简介>

---

## 混合层

<mixing-layers>

这些工具是分层的，因此它们可以在同一个项目中组合。常见模式：

- **深度代理编排器 → LangGraph 子代理** — 当主代理需要规划和内存，但一个子任务需要确定性图时。
- **作为工具或子代理包装的 LangGraph 图** — 当一个专用管道（例如 RAG、反射循环）被更广泛的代理调用时。

一个编译的 LangGraph 图可以作为命名子代理在深度代理中注册 — 编排器通过 `task` 工具将其委托，而无需知道其内部结构。LangChain 工具和检索器可以在 LangGraph 节点和深度代理工具中自由工作。

</mixing-layers>

---

## 第 2 步 — 设置环境变量

始终为此设置这些以进行可观察性。这些是当前的 LangSmith 环境变量名称。按原样复制它们。旧名称不再工作。

<环境变量>
LANGSMITH_API_KEY=<你的密钥>
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=<项目名称>
</环境变量>

模型提供者和工具特定的密钥（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`TAVILY_API_KEY` 等）取决于你的堆栈 — 根据需要设置它们。

---

## 第 3 步 — 文档如何工作

<文档>

所有文档都位于 **docs.langchain.com**，组织为两个顶层部分：

- **OSS** — LangChain、LangGraph、深度代理。Python（`/oss/python/`）和 TypeScript（`/oss/javascript/`）并行树。
- **LangSmith** — 可观察性、评估、部署、提示工程。

每个产品都有自己的页面树：概述 → 快速入门 → 如何指南 → 参考。

### 标准着陆页

从这里开始，而不是从根目录进行树搜索（将 `python` 交换为 `javascript` 以用于 TypeScript）：

- **LangChain** — `/oss/python/langchain/overview`
- **LangGraph** — `/oss/python/langgraph/overview`
- **深度代理** — `/oss/python/deepagents/overview`
- **LangSmith** — `/langsmith/home`（无语言分割）

### 在代理上下文中访问文档

**如果 LangChain 文档 MCP 服务器已连接**（`mcp__docs-langchain__*` 工具可用），直接查询它：
```
tree /oss/python -L 2                        # 探索 Python 结构
tree /oss/javascript -L 2                    # 并行的 TypeScript 结构
cat /oss/python/langchain/quickstart.mdx     # 读取特定页面
rg -il "checkpointer" /oss/python/langgraph/ # 按关键字搜索
```

**如果 MCP 服务器不可用**，使用 `llms.txt` 索引：
1. 获取 `https://docs.langchain.com/llms.txt` — 所有页面的结构化列表和描述
2. 确定与问题最相关的 2-4 个页面
3. 直接获取这些页面以获取准确、最新的内容

> 始终优先获取实时文档，而不是依赖训练数据的知识 — 这些库发展迅速，API 经常变化。

</文档>

---

## 第 4 步 — 下一步加载正确的技能

如果用户只想获取一个最小的本地工作代理（新项目、桩工具、提供者密钥），首先加载匹配的快速入门：

- LangChain → `langchain-python-quickstart` 或 `langchain-typescript-quickstart`
- LangGraph → `langgraph-python-quickstart` 或 `langgraph-typescript-quickstart`
- 深度代理 → `deepagents-python-quickstart` 或 `deepagents-typescript-quickstart`

否则，加载与步骤 1 中的层匹配的技能。这是必需的 — 特定于层的技能包含当前的 API；仅提示本身不包含。

<下一步技能>

### LangChain

- **`langchain-fundamentals`** — 构建任何 LangChain 代理
- **`langchain-rag`** — 添加 RAG / 向量存储检索
- **`langchain-middleware`** — 使用 Pydantic 的结构化输出
- **`langchain-dependencies`** — 包版本、安装或依赖管理问题

### LangGraph

- **`langgraph-fundamentals`** — 任何 LangGraph 图
- **`langgraph-human-in-the-loop`** — 人类参与循环或批准工作流
- **`langgraph-persistence`** — 必须在重新启动后存活或跨线程内存的状态

### 深度代理

**始终首先加载 `deep-agents-core`。** 然后，根据需要：

- **`deep-agents-orchestration`** — 子代理委派或编排
- **`deep-agents-memory`** — 跨会话的持久内存

</下一步技能>
