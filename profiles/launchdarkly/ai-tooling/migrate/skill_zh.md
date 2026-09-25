# 迁移到 AgentControl

您正在使用一个技能，它将指导您将应用程序从硬编码的 LLM 提示迁移到完整的 LaunchDarkly AgentControl 实现。您的工作是运行迁移，并在每个阶段停止以供用户确认：

1. **审计代码** — 只读扫描，生成一个结构化的列表，其中包含所有硬编码的内容（提示、模型、参数、工具、应用程序范围的旋钮）。
2. **包装调用** — 安装 SDK，在 LaunchDarkly 中创建配置，具有镜像硬编码值的回退，并重写调用位置以在每次请求时获取配置。
3. **移动工具** — 提取每个工具的 JSON 架构，将其附加到配置中，并交换每个引用旧工具列表的调用位置。
4. **添加跟踪** — 将每个请求的跟踪器（持续时间、令牌、成功/错误）围绕提供程序调用。
5. **附加评估器** — 通过 Playground + Datasets 进行离线评估，或自动评分采样流量的在线判官。

> **⚠️ 避免前三次运行失败模式。**
>
> 1. **跟踪器在错误的作用域中。** 对于具有循环的代理，在 `setup_run` 条目节点中一次为每个用户回合 mint `create_tracker()` — 不要在 `call_model` 内部。每次迭代工厂调用会产生 N 个 `runId` 并触发最多一次的守卫。参见 [agent-mode-frameworks.md § Custom `StateGraph`](references/agent-mode-frameworks.md)。
> 2. **`load_chat_model(f"{provider}/{name}")` 封装重用。** 模板如 `langchain-ai/react-agent` 提供一个 `load_chat_model(f"{provider}/{name}")` 辅助函数，它包装 `init_chat_model(...)` 并无声地丢弃每个变体参数。**删除它**（不要只是避免使用它）并用 `create_langchain_model(ai_config)` 替换调用位置。
> 3. **`/configs-create` 后回退没有翻转。** 新创建的配置的回退指向自动生成的禁用变体，因此 SDK 返回 `enabled=False`，直到 `/configs-targeting` 运行。在 Stage 2 验证之前翻转它。

## 覆盖范围 — 哪些形状是熟悉的，哪些需要推断

该技能针对 Python 和 Node.js / TypeScript 进行了优化；其他语言只需安装。在 Python 和 Node 中，覆盖范围级别如下：

| 形状 | Python | Node.js | 参考 |
|------|--------|--------|------|
| One-shot 完成单次调用（直接 OpenAI / Anthropic / Bedrock / Gemini 调用） | ✅ 工作示例 | ✅ 工作示例 | [before-after-examples.md](references/before-after-examples.md), 每个提供者的文档在 `built-in-metrics/references/` |
| 通过管理运行器进行聊天循环 (`ManagedModel`) | ✅ 级别 1 模式 | ✅ 级别 1 模式 | [built-in-metrics SKILL.md](../built-in-metrics/SKILL.md) |
| LangChain 单次调用 | ✅ 工作示例 | ✅ 工作示例 | [langchain-tracking.md](../built-in-metrics/references/langchain-tracking.md) |
| LangGraph 预构建代理（Python `langchain.agents.create_agent`, Node `createReactAgent`) | ✅ 工作示例 | ✅ 工作示例 | [agent-mode-frameworks.md § LangGraph](references/agent-mode-frameworks.md) |
| LangGraph 自定义 `StateGraph` 带有请求范围的跟踪器（`setup_run` + `call_model` + `finalize`) | ✅ 深入工作示例 | ⚠️ 提及 — 从 Python 翻译 | [agent-mode-frameworks.md § Custom `StateGraph`](references/agent-mode-frameworks.md) |
| CrewAI `Agent` | ✅ 工作示例 | — (不是 Node 框架) | [agent-mode-frameworks.md § CrewAI](references/agent-mode-frameworks.md) |
| Strands `Agent` | ✅ 工作示例 | ⚠️ BedrockModel + OpenAIModel 仅限（没有 Anthropic） | [agent-mode-frameworks.md § Strands](references/agent-mode-frameworks.md) |
| 自定义 ReAct 循环（手写，任何框架或无） | ✅ 工作示例 | ⚠️ 应用框架无关的不变量；从 Python 翻译 | [agent-mode-frameworks.md § Custom ReAct loop](references/agent-mode-frameworks.md) |
| Vercel AI SDK (`generateText` / `streamText`) | — (不是 Python 框架) | ⚠️ 提供者包存在；技能中没有工作示例 | `built-in-metrics` 提供者包矩阵 |
| 流式传输（SSE / WebSocket） | ⚠️ 委托给 `built-in-metrics` 流式传输文档 | ⚠️ 相同 — 使用 `trackStreamMetricsOf` + 手动 TTFT | [streaming-tracking.md](../built-in-metrics/references/streaming-tracking.md) |
| 多代理图（监督者 + 工作人员） | ⚠️ 主要范围内之外；见参考 | ⚠️ 主要范围内之外；见参考 | [agent-graph-reference.md](references/agent-graph-reference.md) |
| 非 LangGraph 代理框架（Pydantic AI, DSPy, AutoGen, Haystack, LlamaIndex 代理, Semantic Kernel) | ⚠️ 应用三个不变量；没有框架特定示例 | ⚠️ 相同 | [agent-mode-frameworks.md § 框架无关的不变量](references/agent-mode-frameworks.md) |
| Go, Ruby, .NET | ℹ️ 仅安装命令 | ℹ️ 仅安装命令 | [phase-1-analysis-checklist.md § SDK 路由表](references/phase-1-analysis-checklist.md) |

**阅读密钥：** ✅ = 原封不动地遵循技能；⚠️ = 架构适用，但您需要翻译习语或参考另一个技能；ℹ️ = 技能不会超过安装步骤。

如果目标应用程序在 ⚠️ 列表中，请从 [agent-mode-frameworks.md § Framework-agnostic invariants](references/agent-mode-frameworks.md) 开始阅读 — 那三个规则（每个 `agent_config` 每个回合，每个跟踪器每个回合，最多一次方法在回合结束时触发一次）适用于任何框架，并且此技能中的每个代码片段都是它们的实例化。将 Python 示例的形状映射到目标框架的原语。

## 前置条件

此技能要求您的环境中配置了远程托管的 LaunchDarkly MCP 服务器，并且您的应用程序已经使用硬编码的模型、提示和参数值调用 LLM 提供程序。

**所需环境：**
- `LD_SDK_KEY` — 目标 LaunchDarkly 项目的服务器端 SDK 密钥（以 `sdk-` 开头）

**此技能直接使用的 MCP 工具：** 无 — 每个 LaunchDarkly 写入都发生在聚焦的兄弟技能中。

**在应用任何模式之前检查 SDK CHANGELOG。** 此技能中描述的 API 表面针对 SDK 在技能最后更新时的行为；SDK 发布后可能会重命名、删除或拆分方法。在开始之前，获取 SDK 的最新 CHANGELOG 并快速浏览，以查找与您即将应用的模式相矛盾的内容：

- Python: https://github.com/launchdarkly/python-server-sdk-ai/blob/main/packages/sdk/server-ai/CHANGELOG.md (以及 `packages/ai-providers/server-ai-{openai,langchain}/CHANGELOG.md 下的每个提供者的 CHANGELOG.md)
- Node: https://github.com/launchdarkly/js-core/blob/main/packages/sdk/server-ai/CHANGELOG.md (以及 `packages/ai-providers/server-ai-{openai,langchain,vercel}/CHANGELOG.md 下的每个提供者的 CHANGELOG.md)

如果 CHANGELOG 条目在此技能之后发布并更改了您即将使用的 API，则 CHANGELOG 优先 — 并且技能应该更新。

**手交模型。** 此技能**不会**自动调用其他技能。在每个需要 LaunchDarkly 写入的阶段，此技能准备输入（配置键、模式、模型、提示、工具架构、判官键），然后**告诉用户自己运行下一个斜杠命令**。用户完成该兄弟技能后，返回此处的下一步。

**每个阶段用户运行的兄弟技能：**
- `projects` — 预 Stage 2，仅当尚不存在项目时
- `configs-create` — Stage 2（创建配置和第一个变体）
- `tools` — Stage 3（创建工具定义并附加它们）
- `configs-targeting` — Stage 2 和 Stage 4 之间（将新变体提升为回退，以便 SDK 实际提供它）
- `online-evals` — Stage 5（附加判官）

## 核心原则

1. **在修改之前进行检查。** 每个阶段都以只读审计开始。在用户确认步骤 1 之前，不要触摸代码。
2. **替换配置，而不是业务逻辑。** SDK 调用是替换模型、参数和提示定义的位置 — 不是提供程序调用本身。OpenAI/Anthropic/Bedrock 调用保持原位。
3. **回退镜像当前行为。** 传递给 `completion_config` / `agent_config` 的回退必须保留硬编码值，以便如果 LaunchDarkly 不可用，应用程序保持不变。
4. **阶段是有序的。** 在添加工具之前包装。在添加工具之前添加跟踪。在跟踪之前添加评估。跳过 ahead 会导致没有流量的配置、没有上下文指标的指标以及没有可评分的判官。

## 工作流

### 最小可接受迁移

阶段 1-4（审计、包装、工具、跟踪器）可以独立部署。**在 Stage 4 完成迁移的迁移是完整的、生产就绪的，并交付核心价值** — 外部化提示和模型配置、目标、变体 A/B 测试和 Monitoring-tab 指标。阶段 5（评估器）是生活质量改进，不是障碍。不要在 Stage 4 发布上阻塞评估器；发布运行范围，验证指标流，然后在团队有时间整理数据集时回来进行 Stage 5。但是，不要跳过 Stage 4。没有跟踪器的迁移提供了外部化提示，但没有可见性，这是大部分收益留在地上的部分。

## 边缘情况

| 情况 | 操作 |
|------|------|
| 应用程序已经初始化 `LDClient` 用于功能标志 | 重用它 — 将现有的客户端传递给 `LDAIClient()` / `initAi()`，不要创建第二个客户端 |
| 应用程序使用 LangChain `ChatOpenAI(model=...)` | 用 `create_langchain_model(config)`（Python）或 `createLangChainModel(config)`（Node）替换手写的模型构造函数。不要手动读取 `config.model.name` 并传递给 `ChatOpenAI(model=...)`，因为这种模式会丢失除了显式命名的变体参数之外的所有变体参数。`create_langchain_model` 会转发 `model.parameters` 中的所有键给提供程序 SDK，如果存在未知的关键字参数，则会导致提供程序崩溃。正确的位置是 `model.custom`，提供程序辅助程序会忽略它，应用程序通过 `ai_config.model.get_custom("key")` 读取它。MCP `update-ai-config-variation` 工具目前不暴露顶层 `custom`，因此选择以下两种路径之一：(a) 通过 REST API PATCH 变体以直接设置 `model.custom`，或 (b) 在 MCP 中通过 `parameters.custom`（作为嵌套字典）设置它，并使用防御性访问器读取这两个位置。包含代码示例的完整演练在 [langchain-tracking.md § MCP 备注说明](../built-in-metrics/references/langchain-tracking.md) 中。

## 不应该做什么

这些按它们作为首次运行失败出现的可能性排序。前三个规则——关于跟踪器和配置生命周期——解释了大多数“迁移看起来完成但 Monitoring tab 是碎片化的/错误的”报告。

### 跟踪器和配置生命周期（最常见的失败模式）

- **不要在用户说“只是包装它”时多次调用 `create_tracker()` / `createTracker()`。** 一个回合 = 完整的请求/响应周期，包括每个 ReAct 迭代、工具调用和重试。见 Stage 4 Step 1 中每个应用程序形状（完成 / 代理循环 / 管理运行器）的规范位置。
- **不要在循环体内调用 `track_duration` / `track_tokens` / `track_success` / `track_error` / `track_time_to_first_token`。** 这些是每个跟踪器最多一次；第二次调用会被丢弃。在循环内累积，在终端/完成节点中发出一次。每个事件方法（`track_tool_call`, `track_tool_calls`, `track_feedback`, `track_judge_result`）可以重复调用。完整矩阵：[sdk-ai-tracker-patterns.md § At-most-once guards](references/sdk-ai-tracker-patterns.md)。
- **不要多次调用 `agent_config()` / `completion_config()`。** 每次调用都是一个标志评估，并发出 `$ld:ai:agent:config` 事件。在循环步骤或工具体内重新获取会导致 Monitoring tab 中的 agent-config 计数膨胀，并允许在单个回合内切换 LLM 调用中的变体。在顶部解析一次，保存在状态中，并且每个后续消费者都从状态中读取。需要变体范围旋钮的工具应使用工具工厂模式（`make_search(ai_config)` 在设置时捕获旋钮）——见 [agent-mode-frameworks.md § Getting knobs into tools](references/agent-mode-frameworks.md)。
- 不要跨请求缓存配置对象——每个回合解析一次，是，但仍然每个回合解析一次。模块作用域缓存完全破坏了目标更改机制。
- 不要在 LaunchDarkly 接线后删除回退。它对于 `enabled=False` 和 SDK 不可用路径是必需的。
- 不要元组拆解 `completion_config` / `agent_config` / `completionConfig` / `agentConfig` 的返回值。它们返回一个**单个**配置对象（例如 `AIAgentConfig`, `AICompletionConfig`），而不是 `(config, tracker)`。通过调用 `config.create_tracker()` / `aiConfig.createTracker()` 获取跟踪器。LLM 会同时想象元组形状和 `config.tracker` 属性——实际 API 是一个工厂。

### LangChain / LangGraph 模式（第二常见的失败模式）

- **如果存储库中已经包含 `load_chat_model(f"{provider}/{name}")` 辅助函数，请删除它**——不要只是避免使用它。** 这种确切的形状与 `langchain-ai/react-agent` 一起提供，并复制到几十个衍生存储库中；查找 `utils.load_chat_model`, `utils.build_model` 或任何接受一个参数的 `init_chat_model` 包装器，它将 `"provider/model"` 字符串拆分。重用它是首次运行失败的模式：每个变体参数（温度、最大令牌、top_p、停止序列）都无声地丢失了，因为 `init_chat_model` 只接收名称和提供程序。`create_langchain_model(ai_config)` 是一对一的替换，并转发整个 `model.parameters` 字典。替换每个调用位置，然后删除包装器文件侧，这样下一个读者就无法找到它。
- **对于手写的 `resolve_tools` / `TOOL_REGISTRY` / `ALL_TOOLS` 辅助函数，应用相同的规则。** 如果模板已经具有 `resolve_tools(tool_keys)` 或 `ALL_TOOLS` 模块级列表，导入 `build_structured_tools` 从 `ldai_langchain.langchain_helper` 并删除手写的版本。`build_structured_tools(ai_config, TOOL_REGISTRY_DICT)` 读取 `ai_config.model.parameters.tools` 并将匹配的调用包装为 LangChain `StructuredTool`s，将 LD 工具键作为 `StructuredTool.name`——因此 `ToolNode` 查找可以在没有第二个映射的情况下工作。不要将两者都保留在存储库中。
- 不要将应用范围的旋钮直接放入 `model.parameters`。`create_langchain_model` 会转发 `parameters` 中的所有键给提供程序 SDK，如果存在未知的关键字参数，则会导致提供程序崩溃。正确的位置是 `model.custom`，提供程序辅助程序会忽略它，应用程序通过 `ai_config.model.get_custom("key")` 读取它。MCP `update-ai-config-variation` 工具目前不暴露顶层 `custom`，因此选择以下两种路径之一：(a) 通过 REST API PATCH 变体以直接设置 `model.custom`，或 (b) 在 MCP 中通过 `parameters.custom`（作为嵌套字典）设置它，并使用防御性访问器读取这两个位置。包含代码示例的完整演练在 [langchain-tracking.md § MCP 备注说明](../built-in-metrics/references/langchain-tracking.md) 中。
- 不要导入 `LaunchDarklyCallbackHandler` 从 `ldai.langchain`——既没有类也没有点分隔的模块路径存在。Python LangChain 辅助程序包是 `ldai_langchain`（顶级模块，下划线）。使用 `create_langchain_model(config)` + `track_metrics_of_async(get_ai_metrics_from_response, lambda: llm.ainvoke(messages))` 作为规范模式。

### 阶段/手交纪律

- 即使用户说“只是包装它”，也不要跳过步骤 1。如果没有审计，回退将漂移到硬编码行为。
- 不要在提取提示和模型之前委托给 `configs-create`——委托需要这些作为输入。
- 不要在初始 `setup-ai-config` 期间尝试附加工具。工具附件是 `tools` 的一个单独步骤拥有的。
- 不要声称你“委托给 `configs-create`” 或任何其他兄弟技能。此技能不会自动调用。在每个手交中，打印输入并告诉用户运行兄弟斜杠命令，然后等待。任何其他误导用户关于刚刚发生了什么的事情。
- 不要在 Stage 2 和 Stage 4 之间跳过 `/configs-targeting` 步骤。新创建的变体返回 `enabled=False`，直到 targeting 将其提升为回退——Stage 2 验证将静默地以每个请求取用回退路径。
- 不要尝试一次完成多代理图迁移。首先迁移一个代理；使用 [agent-graph-reference.md](references/agent-graph-reference.md) 作为下一步读取。

### Stage 5 评估

- 在跟踪器就位之前不要连接评估器。判官评分流量；没有 Stage 4 流量，没有可评分的内容。
- 不要将 Stage 5 表述为“要么 UI 要么程序化”。有**三种**路径：离线评估（迁移的默认默认值），UI 附加自动判官（仅完成模式），以及程序化直接判官。离线评估是人们跳过并通常正确的起点。
- 不要将 `sampling_rate` 传递给 `create_judge`——它是 `Judge.evaluate()` 的参数，而不是 `create_judge()`。
- 不要硬编码判官配置键（`"accuracy-judge"`, `"relevance-judge"`, 等）。内置键不是规范 SDK 常量；要求用户在 LD UI 中的 **AgentControl > Library** 中查找它们。
- 在 `create_judge` 之后不要忘记 `if judge and judge.enabled:` 守卫。它返回 `Optional[Judge]`，当判官配置对上下文禁用时返回 `None`。
