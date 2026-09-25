# 配置工具

您正在使用一个技能，它将指导您通过工具（函数调用）为您的智能体添加功能。您的工作是识别智能体需要执行的任务，创建工具定义，将它们附加到变体上，并验证它们是否正常工作。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-ai-tool` -- 使用模式创建新的工具定义
- `update-ai-config-variation` -- 将工具附加到配置变体
- `get-ai-config` -- 验证工具是否已附加到变体

**可选的 MCP 工具：**
- `list-ai-tools` -- 浏览项目中的现有工具
- `get-ai-tool` -- 检查特定工具的模式

## 核心原则

1. **从功能开始**：在创建工具之前，先考虑智能体需要执行的任务
2. **框架很重要**：LangGraph/CrewAI 通常自动生成模式；OpenAI SDK 需要手动模式
3. **先创建后附加**：必须先创建工具，才能将其附加到变体上
4. **验证**：智能体获取配置以确认附加
5. **完成完整的工作流程**：列出现有工具是一个发现步骤，而不是最终目标。列出后，始终继续创建所需的工具，附加它，并验证。不要在探索后停止。

## 工作流程

### 第 1 步：识别所需功能

智能体应该能够做什么？
- 查询数据库、调用 API、执行计算、发送通知
- 检查代码库中存在的内容（API 客户端、函数）
- 考虑框架：LangGraph/LangChain 自动生成模式；直接 SDK 需要手动模式

如果用户要求先检查现有工具，或者您没有关于现有工具的代码库上下文，请按以下顺序操作：
1. `list-ai-tools` -- 探索现有内容
2. `create-ai-tool` -- 创建新工具（键名与现有工具不同）
3. `update-ai-config-variation` -- 附加它
4. `get-ai-config` -- 验证

在创建任何内容之前，作为您的**第一个**工具调用调用 `list-ai-tools`。不要在列出后停止——始终继续执行所有四个步骤。

### 第 2 步：创建工具

使用 `create-ai-tool` 并提供：
- `key` -- 工具的唯一标识符
- `description` -- 清晰的描述（LLM 使用此内容来决定何时调用工具）
- `schema` -- 原始 JSON 模式（**不要**使用 OpenAI 函数调用包装器）：

```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string", "description": "搜索查询"},
    "limit": {"type": "integer", "default": 10}
  },
  "required": ["query"]
}
```

### 第 3 步：附加到变体

使用 `update-ai-config-variation` 附加工具。**仅传递 `tools` 字段。** 除非用户明确要求您也更新这些字段，否则不要将 `instructions`、`messages`、`model` 或 `parameters` 捆绑到此 PATCH 中。这些字段可能在变体创建后已在 LaunchDarkly UI 中被编辑，将它们包含在工具附加的 PATCH 中将无声地覆盖 UI 编辑。

```json
{
  "projectKey": "my-project",
  "configKey": "support-chatbot",
  "variationKey": "default",
  "tools": [
    {"key": "search-knowledge-base", "version": 1}
  ]
}
```

如果您观察到 UI 清除错误，其中附加工具会清除其他字段，**不要通过重新发送先前 `get-ai-config` 响应中的这些字段来绕过它**——这会掩盖错误，并且可能会恢复用户已编辑的过时值。相反，请报告该错误。

### 第 4 步：验证

1. 使用 `get-ai-tool` 确认工具存在且模式有效
2. 使用 `get-ai-config` 确认工具已附加到变体（检查变体的输出中的 `tools`）

**报告结果：**
- 工具使用有效模式创建
- 工具附加到变体
- 标记任何问题

## 提供商在调用位置的方案

LaunchDarkly 一次存储工具模式——您传递给 `create-ai-tool` 的扁平 `{type, name, description, parameters}` 形状。您的应用程序通过 `config.model.parameters.tools`（完成模式）或 `agent_config.model.parameters.tools`（代理模式）读取它，然后转换为提供商 SDK 期望的形状。LaunchDarkly 从不进行提供商调用；您的代码执行。实现每个工具的处理程序也保留在应用程序代码中——LaunchDarkly 存储模式，您的应用程序拥有行为。

| 提供商 / 框架 | 目标形状 | 在调用中的位置 |
|---|---|---|
| OpenAI Chat Completions (直接 SDK) | `{type: "function", function: {name, description, parameters}}` | 顶层 `tools=[...]` |
| Anthropic 直接 SDK | `{name, description, input_schema}` — 将 `parameters` 重命名为 `input_schema` | 顶层 `tools=[...]` |
| Bedrock Converse | `{toolSpec: {name, description, inputSchema: {json: parameters}}}` | `toolConfig.tools=[...]` 内部 |
| Gemini (`google-genai`) | `{function_declarations: [{name, description, parameters}]}` (Python) / `{functionDeclarations: [...]}` (Node) | `GenerateContentConfig.tools=[...]` |
| OpenAI 响应 API | LaunchDarkly 的扁平形状不变 | 顶层 `tools=[...]` |
| LangChain / LangGraph | `createLangChainModel(config)` (Node) / `create_langchain_model(config)` (Python) 并将 `ai_config.tools`（或您自己的 `StructuredTool` 列表）传递到 `bind_tools(...)` / `create_react_agent(tools=[...])` | 框架原生；没有每次调用的转换 |
| Strands Agents | LaunchDarkly 的扁平形状；在将参数传递给 Strands 模型类（`AnthropicModel`、`OpenAIModel`）之前删除 `parameters.tools` — Python `@tool` 装饰的调用保持不变 | `Agent(tools=[...])` 构造函数；没有每次调用的转换 |

最小转换代码片段（Python）：

```python
ld_tools = (ai_config.model.to_dict().get("parameters") or {}).get("tools", []) or []

# OpenAI Chat Completions
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t.get("description", ""),
            "parameters": t.get("parameters", {"type": "object", "properties": {}}),
        },
    }
    for t in ld_tools
]

# Anthropic
anthropic_tools = [
    {
        "name": t["name"],
        "description": t.get("description", ""),
        "input_schema": t.get("parameters", {"type": "object", "properties": {}}),
    }
    for t in ld_tools
]

# Bedrock Converse
bedrock_tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": t["name"],
                "description": t.get("description", ""),
                "inputSchema": {"json": t.get("parameters", {"type": "object", "properties": {}})},
            }
        }
        for t in ld_tools
    ]
}

# Gemini
gemini_tools = [
    {
        "function_declarations": [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("parameters", {"type": "object", "properties": {}}),
            }
            for t in ld_tools
        ]
    }
] if ld_tools else []
```

## 使用工具的智能体循环

使用工具的智能体运行一个短循环：调用提供商，分发任何工具调用，再次循环，直到提供商返回最终答案。无论提供商如何，都适用三条规则：

1. **限制循环**。`MAX_STEPS = 5` 是一个安全的默认值。失控的工具循环几乎总是提示或模式错误，而不是需要 50 次迭代的情况。
2. **跟踪每个工具调用**。对于智能体实际执行的每个工具，调用 `tracker.track_tool_call(tool_name)` / `tracker.trackToolCall(toolName)`。这是监控选项卡计为工具使用的内容。
3. **在提供商的“不再进行工具调用”信号处中断**。确切的信号因提供商而异：OpenAI Chat Completions → `choice.finish_reason != "tool_calls"`；Anthropic → `response.stop_reason != "tool_use"`；Bedrock Converse → `response["stopReason"] != "tool_use"`；Gemini → `response.function_calls` 为空；OpenAI 响应 API → `response.output` 中没有 `function_call` 项。

骨架（Python，Anthropic——其他提供商遵循相同的形状，但有自己的停止原因检查和工具结果格式化）：

```python
messages = [{"role": "user", "content": initial_input}]
MAX_STEPS = 5
for _ in range(MAX_STEPS):
    response = tracker.track_metrics_of(
        anthropic_metrics,
        lambda: anthropic_client.messages.create(
            model=agent.model.name,
            system=agent.instructions,
            messages=messages,
            tools=anthropic_tools,
            **params,
        ),
    )
    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        if block.name not in tool_handlers:
            raise ValueError(f"Unknown tool: {block.name}")
        result = tool_handlers[block.name](**block.input)
        tracker.track_tool_call(block.name)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": result,
        })
    messages.append({"role": "user", "content": tool_results})
```

每个提供商工具调用有效载荷形状位于 `built-in-metrics` 引用中：

- [openai-tracking.md](../built-in-metrics/references/openai-tracking.md) — Chat Completions + Responses API
- [anthropic-tracking.md](../built-in-metrics/references/anthropic-tracking.md) — `tool_use` 块和 `tool_result` 有效载荷
- [bedrock-tracking.md](../built-in-metrics/references/bedrock-tracking.md) — `toolUse` / `toolResult` Converse 格式
- [gemini-tracking.md](../built-in-metrics/references/gemini-tracking.md) — `functionCalls` / `functionResponse` 部分
- [langchain-tracking.md](../built-in-metrics/references/langchain-tracking.md) — LangGraph 工具循环继承自 `create_react_agent`

## 协调器笔记

LangGraph、CrewAI 和 AutoGen 通常从函数定义生成模式。您仍然需要在 LaunchDarkly 中创建工具并将键附加到变体上，以便 SDK 知道哪些工具可用。

## 边缘情况

| 情况 | 操作 |
|-----------|--------|
| 工具已存在（409） | 使用现有工具或创建不同键名的工具 |
| 模式无效 | 使用原始 JSON 模式格式（type: object, properties, required） |
| 假设了错误的端点 | 工具使用 `/ai-tools`，而不是 `/ai-configs/tools` |

## 不要做的事情

- 不要在配置创建期间尝试附加工具——之后更新变体
- 不要跳过清晰的工具描述（LLM 需要它们来决定何时调用）
- 不要忘记在更新变体后验证附加
- 不要将 `instructions`、`messages`、`model` 或 `parameters` 捆绑到工具附加的 PATCH 中。除非用户明确要求多字段更新，否则仅发送 `tools`——捆绑的 PATCH 会无声地覆盖对其他字段的 UI 编辑。

## 相关技能

- `configs-create` -- 在附加工具之前创建配置
- `configs-variations` -- 管理具有不同工具集的变体
