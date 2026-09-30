---
name: migrate
description: 将具有硬编码LLM提示的应用迁移到完整的LaunchDarkly AgentControl实现中，分为五个阶段：审计代码、封装调用、迁移工具、添加跟踪、附加评估器。适用于用户希望将模型/提示配置外部化、从直接提供者调用（OpenAI、Anthropic、Bedrock、Gemini、Strands）迁移到管理配置，或进行从硬编码到LaunchDarkly的完整迁移。
---

# 迁移到 AgentControl

您正在使用一个技能，它将引导您将应用程序从硬编码的 LLM 提示迁移到完整的 LaunchDarkly AgentControl 实现。您的工作是在五个阶段运行迁移，并在每个阶段停止以供用户确认：

1. **审计代码** — 只读扫描，生成一个结构化的列表，其中包含所有硬编码的内容（提示、模型、参数、工具、应用程序范围的开关）。
2. **包装调用** — 安装 SDK，在 LaunchDarkly 中创建配置，并使用镜像硬编码值的回退，然后重写调用位置以在每次请求时获取配置。
3. **移动工具** — 提取每个工具的 JSON 架构，将其附加到配置中，并交换每个引用旧工具列表的调用位置。
4. **添加跟踪** — 将每个请求的跟踪器（持续时间、令牌、成功/错误）绕绕提供程序调用。
5. **附加评估器** — 通过 Playground + Datasets 进行离线评估，或自动对采样流量进行评分的在线裁判。

> **⚠️ 避免前三次运行失败模式。**
>
> 1. **跟踪器在错误的范围内。** 对于具有循环的代理，在 `setup_run` 的入口节点中一次为每个用户回合 mint `create_tracker()` — 而不是在 `call_model` 中。每次迭代的工厂调用会产生 N 个 `runId` 并触发最多一次的守卫。参见 [agent-mode-frameworks.md § 自定义 `StateGraph`](references/agent-mode-frameworks.md)。
> 2. **`load_chat_model` 包装器重用。** 类似 `langchain-ai/react-agent` 的模板提供 `load_chat_model(f"{provider}/{name}")` 辅助程序，它包装 `init_chat_model(...)` 并静默地丢弃每个变化参数。**删除它**（不要只是避免使用它）并用 `create_langchain_model(ai_config)` 替换调用位置。
> 3. **`/configs-create` 后未翻转回退。** 新创建的配置的回退指向自动生成的禁用变体，因此 SDK 返回 `enabled=False`，直到 `/configs-targeting` 运行。在 Stage 2 验证之前翻转它。

## 覆盖范围 — 哪些形状是经过充分验证的，哪些需要推断

该技能针对 Python 和 Node.js / TypeScript 进行了优化；其他语言只需安装。在 Python 和 Node 中，覆盖级别如下：

| 形状 | Python | Node.js | 参考 |
|-------|--------|---------|-----------|
| 单次完成（直接 OpenAI / Anthropic / Bedrock / Gemini 调用） | ✅ 工作示例 | ✅ 工作示例 | [before-after-examples.md](references/before-after-examples.md)，在 `built-in-metrics/references/` 中按提供程序提供的文档 |
| 通过管理运行器进行聊天循环 (`ManagedModel`) | ✅ 级别 1 模式 | ✅ 级别 1 模式 | [built-in-metrics SKILL.md](../built-in-metrics/SKILL.md) |
| LangChain 单次调用 | ✅ 工作示例 | ✅ 工作示例 | [langchain-tracking.md](../built-in-metrics/references/langchain-tracking.md) |
| LangGraph 预构建代理（Python `langchain.agents.create_agent`，Node `createReactAgent`） | ✅ 工作示例 | ✅ 工作示例 | [agent-mode-frameworks.md § LangGraph](references/agent-mode-frameworks.md) |
| LangGraph 自定义 `StateGraph` 带有运行范围跟踪器（setup_run + call_model + finalize） | ✅ 深度工作示例 | ⚠️ 提及 — 从 Python 翻译 | [agent-mode-frameworks.md § 自定义 `StateGraph`](references/agent-mode-frameworks.md) |
| CrewAI `Agent` | ✅ 工作示例 | —（不是 Node 框架） | [agent-mode-frameworks.md § CrewAI](references/agent-mode-frameworks.md) |
| Strands `Agent` | ✅ 工作示例 | ⚠️ BedrockModel + OpenAIModel 仅限（没有 Anthropic） | [agent-mode-frameworks.md § Strands](references/agent-mode-frameworks.md) |
| 自定义 ReAct 循环（手工编写，任何框架或无框架） | ✅ 工作示例 | ⚠️ 应用框架无关的不变量；从 Python 翻译 | [agent-mode-frameworks.md § 自定义 ReAct 循环](references/agent-mode-frameworks.md) |
| Vercel AI SDK (`generateText` / `streamText`) | —（不是 Python 框架） | ⚠️ 提供程序包存在；技能中没有工作示例 | `built-in-metrics` 提供程序包矩阵 |
| 流式传输（SSE / WebSocket） | ⚠️ 委托给 `built-in-metrics` 流式传输文档 | ⚠️ 相同 — 使用 `trackStreamMetricsOf` + 手动 TTFT | [streaming-tracking.md](../built-in-metrics/references/streaming-tracking.md) |
| 多代理图（监督者 + 工作人员） | ⚠️ 超出主范围；参见参考 | ⚠️ 超出主范围；参见参考 | [agent-graph-reference.md](references/agent-graph-reference.md) |
| 非 LangGraph 代理框架（Pydantic AI，DSPy，AutoGen，Haystack，LlamaIndex 代理，Semantic Kernel） | ⚠️ 应用三个不变量；没有框架特定示例 | ⚠️ 相同 | [agent-mode-frameworks.md § 框架无关的不变量](references/agent-mode-frameworks.md) |
| Go，Ruby，.NET | ℹ️ 仅安装命令 | ℹ️ 仅安装命令 | [phase-1-analysis-checklist.md § SDK 路由表](references/phase-1-analysis-checklist.md) |

**阅读键：** ✅ = 逐字遵循技能；⚠️ = 架构适用，但您需要翻译习语或参考另一个技能；ℹ️ = 技能不会超过安装步骤。

如果目标应用程序在 ⚠️ 列中，请先阅读 [agent-mode-frameworks.md § 框架无关的不变量](references/agent-mode-frameworks.md) — 这三个规则（每个回合一个 `agent_config`，每个回合一个跟踪器，最多一次方法在回合结束时触发一次）无论框架如何都适用，此技能中的每个代码片段都是它们的实例化。将 Python 示例的形状映射到目标框架的原语上。

## 前置条件

此技能要求远程托管的 LaunchDarkly MCP 服务器在您的环境中配置，并且一个已经使用硬编码的模型、提示和参数值调用 LLM 提供程序的应用程序。

**所需环境：**
- `LD_SDK_KEY` — 目标 LaunchDarkly 项目的服务器端 SDK 密钥（以 `sdk-` 开头）

**此技能直接使用的 MCP 工具：** 无 — 所有 LaunchDarkly 写入都在一个集中的兄弟技能中发生。

**在应用任何模式之前检查 SDK CHANGELOG。** 此技能中描述的 API 表面针对技能最后更新时的 SDK 行为；SDK 发布后可能会重命名、删除或拆分方法。在开始之前，获取您将目标 SDK 的最新 CHANGELOG 并快速浏览，以查找任何与您即将应用的模式相矛盾的内容：

- Python: https://github.com/launchdarkly/python-server-sdk-ai/blob/main/packages/sdk/server-ai/CHANGELOG.md（以及在每个提供程序下 `packages/ai-providers/server-ai-{openai,langchain}/CHANGELOG.md` 的 CHANGELOG）
- Node: https://github.com/launchdarkly/js-core/blob/main/packages/sdk/server-ai/CHANGELOG.md（以及在每个提供程序下 `packages/ai-providers/server-ai-{openai,langchain,vercel}/CHANGELOG.md` 的 CHANGELOG）

如果 CHANGELOG 条目在此技能之后发布并更改了您即将使用的 API，则 CHANGELOG 胜出 — 并且技能应该更新。

**交接模型。** 此技能**不会**自动触发其他技能。在每个需要 LaunchDarkly 写入的阶段，此技能准备输入（配置键、模式、模型、提示、工具架构、裁判键），然后**告诉用户自己运行下一个斜杠命令**。用户完成该兄弟技能后，返回到此处的下一个步骤。将下面的“委托”行视为下一步说明，而不是自动交接。

**每个阶段用户运行的兄弟技能：**
- `projects` — 阶段 2 之前，如果尚未存在项目
- `configs-create` — 阶段 2（创建配置和第一个变体）
- `tools` — 阶段 3（创建工具定义并附加它们）
- `configs-targeting` — 阶段 2 和阶段 4 之间（将新变体提升为回退，以便 SDK 实际提供它）
- `online-evals` — 阶段 5（附加裁判，创建自定义裁判）

## 核心原则

1. **在修改之前检查。** 每个阶段都以只读审计开始。在用户确认步骤 1 之前，不要触摸代码。
2. **替换配置，而不是业务逻辑。** SDK 调用是模型、参数和提示定义位置的即插即用 — 不是提供程序调用本身。OpenAI/Anthropic/Bedrock 调用保持原位。
3. **回退镜像当前行为。** 传递给 `completion_config` / `agent_config` 的回退必须保留您移除的硬编码值，因此如果 LaunchDarkly 不可用，应用程序将保持不变。
4. **阶段按顺序进行。** 在添加工具之前包装。在添加工具之前跟踪。在跟踪之前添加评估器。跳过前进会产生没有流量的配置、没有上下文的指标和没有可评分的裁判。
5. **手动交接给专注技能。** 需要LaunchDarkly写入的每个阶段都告诉用户运行一个兄弟斜杠命令（`/configs-create`，`/tools`，`/configs-targeting`，`/online-evals`），并等待他们回来。此技能**不会**自动触发其他技能。

## 工作流程

### 最小可行迁移

阶段 1–4（审计、包装、工具、跟踪器）可以独立部署。**一个在阶段 4 完成后迁移是完整、生产就绪的，并交付核心价值** — 外部化提示和模型配置、目标、变体 A/B 测试和 Monitoring-tab 指标。阶段 5（评估器）是一个提升质量的附加功能，而不是一个门槛。不要因为评估器而阻塞阶段 4 的发布；发布运行范围跟踪器路径，验证指标流，然后在团队有时间整理数据集时再回来处理阶段 5。

话虽如此，不要*跳过*阶段 4。没有跟踪器的迁移会为您提供外部化提示，但没有可见性，这几乎是未实现的收益。

### 步骤 1：审计代码库（阶段 1）

这是第一个阶段。它是**只读的** — 没有代码写入，没有 LaunchDarkly 资源创建。目标是对存储库进行扫描并生成一个结构化的清单，其中包含需要移动的每个硬编码值，然后在触摸任何代码以进行阶段 2 之前，将清单交还给用户确认。

使用 [phase-1-analysis-checklist.md](references/phase-1-analysis-checklist.md) 进行扫描：

1. **语言和包管理器** — Python (pip/poetry/uv)，TypeScript/JavaScript (npm/pnpm/yarn)，Go，Ruby，.NET
2. **LLM 提供程序** — OpenAI，Anthropic，Bedrock，Gemini，LangChain，LangGraph，CrewAI，Strands
3. **现有的 LaunchDarkly 使用情况** — 任何预先存在的 `LDClient` 或 `ldclient` 初始化以供重用
4. **硬编码的模型配置** — 模型名称字符串字面量，温度 / 最大令牌 / top_p，系统提示，指令字符串
5. **提示中的模板占位符** — `.format()` 调用，提示常量中的 f-字符串，JS/TS 模板字面量，`%(var)s`，手工编写的 `str.replace("__VAR__", ...)`. 标记每个占位符名称及其运行时值源；所有内容在阶段 2 中都会被重写为 Mustache `{{ variable }}`。
6. **外部化提示文件** — 扫描 YAML / JSON / TOML / Markdown / `.prompt` / `.j2` 文件**和**提示模板注册表（`langchain.hub.pull(...)`，LangSmith `client.pull_prompt(...)`）以在运行时加载提示。常见形状：CrewAI `agents.yaml` / `tasks.yaml`，LangChain Promptfiles，k8s ConfigMap 覆盖，Pydantic Settings 类带有 `prompt_*` 字段。如果占位符语法不同，则应用相同的 Mustache 重写（阶段 2 的子步骤 5）。参见 [phase-1-analysis-checklist.md § 4](references/phase-1-analysis-checklist.md)。
7. **硬编码的应用程序范围开关** — 搜索结果限制，重试预算，工具超时覆盖，功能开关，任何不是提示或模型参数但仍然控制代理行为的配置数据类字段。这些属于变体的 `model.custom`（不是 `model.parameters`，它将转发给提供程序 SDK，并且在未知 kwargs 上会崩溃）。
8. **模式决策** — 完成模式（聊天消息数组）或代理模式（单个指令字符串）。完成模式是默认模式，并且是唯一支持在 UI 中附加裁判的模式。

对于审计发现的每个硬编码目标，记录：

- 文件路径和行范围
- 当前值（模型名称，完整提示文本，参数字典）
- 目标配置字段（`model.name`，`model.parameters.temperature`，`messages[].content`，`instructions`)
- 周围调用是否使用函数调用 / 工具（驱动阶段 3）
- 周围调用是否有重试逻辑（影响阶段 4 跟踪器调用位置）

此清单是下一阶段四个阶段的合同。

**阶段 1 输出**（作为结构化摘要返回给用户）：

```
语言：Python 3.12
包管理器：uv
LLM 提供程序：OpenAI
现有的 LD SDK：无
目标模式：完成
硬编码目标：
  - src/chat.py:42   model="gpt-4o"
  - src/chat.py:43   temperature=0.7, max_tokens=2000
  - src/chat.py:45   system="You are a helpful assistant..."
外部化提示文件：无（例如 "prompts/agents.yaml — CrewAI role/goal/backstory"）
提示模板注册表：无（例如在 app.py:14 的 langchain.hub.pull("rlm/rag-prompt")）
覆盖总数：3 个硬编码代码目标 · 0 个外部化提示文件 · 0 个注册表拉取
建议计划：单个配置键 `chat-assistant`，镜像回退，阶段 3（工具）跳过（没有函数调用），阶段 4（跟踪）内联，阶段 5（评估器）附加内置准确裁判。
```

**停止。** 呈现此摘要，大声说出覆盖总数（例如 "我发现了 **N** 个硬编码代码目标和 **M** 个外部化提示文件 — 这是否与您的预期相符？"), 并等待用户以四种明确的格式之一回复：

- **`confirm`** — 进入阶段 2。
- **`add: <文件或路径>`** — 重新运行审计，并呈现更新后的摘要。
- **`fix: <修正>`** — 更新列表中的目标（提供程序、模式、提示内容等），并再次询问。
- **`stop`** — 在此处暂停迁移。

不要将任何其他单词解释为确认 — 包括 `skip`，`next`，`go`，`ok`，`proceed` —; 要求用户选择四种格式之一。**这是工作流程中最重要的检查点** — 如果审计错误，此后的每个阶段都会错误。用户应该在给出许可之前，将硬编码目标列表与他们对代码中内容的了解进行交叉检查。

### 步骤 2：在 AI SDK 中包装调用（阶段 2）

这是第一个写入代码的阶段。它有九个子步骤。

1. **删除审计标记的手工编写的模型 / 工具包装器。** 在安装新的 SDK 之前这样做，以便替换落在没有混淆回退导入的存储库中。阶段 1 审计应该暴露的两种形状：
   - **`load_chat_model(f"{provider}/{name}")` 或任何 `init_chat_model(...)` 包装器。** 随 `langchain-ai/react-agent` 和许多衍生存储库一起提供。删除该函数及其模块；替换是 `create_langchain_model(ai_config)`（在下一个子步骤中安装）。保留包装器意味着此存储库中的下一个编辑将导入熟悉的辅助程序并静默地丢弃变化参数。
   - **手工编写的 `resolve_tools` / `TOOL_REGISTRY` / `ALL_TOOLS` 辅助程序，硬编码静态工具列表。** 删除它们；`ldai_langchain.langchain_helper.build_structured_tools(ai_config, TOOL_REGISTRY_DICT)` 是规范替换，并在阶段 3 中连接。如果您保留手工编写的版本，这两个形状将并排存在，下一个贡献者将选择熟悉的那个。

   如果存储库的审查流程受益于将删除单独提交，则单独提交删除 — 否则与子步骤 2 捆绑在一起。

2. **安装 AI SDK。** 从步骤 1 检测包管理器，然后安装：
   - Python: `launchdarkly-server-sdk` + `launchdarkly-server-sdk-ai>=0.20.0`
   - Node.js/TypeScript: `@launchdarkly/node-server-sdk` + `@launchdarkly/server-sdk-ai@^0.20.0`
   - Go: `github.com/launchdarkly/go-server-sdk/v7` + `github.com/launchdarkly/go-server-sdk-ai`

二级提供商包（在第四阶段安装，仅如果您使用匹配的提供商）：
- OpenAI: `launchdarkly-server-sdk-ai-openai>=0.4.0` (Python) / `@launchdarkly/server-sdk-ai-openai@^0.5.5` (Node)
- LangChain / LangGraph: `launchdarkly-server-sdk-ai-langchain>=0.5.0` (Python) / `@launchdarkly/server-sdk-ai-langchain@^0.5.5` (Node)
- Vercel AI SDK (Node 仅): `@launchdarkly/server-sdk-ai-vercel@^0.5.5`
- Anthropic, Gemini, Bedrock — 未发布提供商包；使用三级自定义提取器（见 `built-in-metrics`）

3. **在启动时初始化一次 `LDAIClient`。** 重复使用任何现有的 `LDClient` — 不要创建第二个基础客户端。将初始化放在拥有现有应用配置的同一模块中。

   **Python:**
   ```python
   import os
   import ldclient
   from ldclient.config import Config
   from ldai.client import LDAIClient

   # 顺序很重要：如果调用 `ldclient.get()` 之前没有调用 `ldclient.set_config()`，则会引发错误。
   # `set_config` 调用是初始化单例；`.get()` 只是返回它。
   sdk_key = os.environ.get("LD_SDK_KEY")
   if sdk_key:
       ldclient.set_config(Config(sdk_key))
   else:
       # 缺少密钥：以离线模式初始化，以便应用仍然启动，并且回退路径在每次调用时运行。
       # 不要在导入时为缺少的环境变量引发错误 — 那会将配置差距转换为启动失败。
       import logging
       logging.getLogger(__name__).warning(
           "LD_SDK_KEY 未设置；配置将仅使用回退值。"
       )
       ldclient.set_config(Config("", offline=True))

   ai_client = LDAIClient(ldclient.get())
   ```

   **Node.js/TypeScript:**
   ```typescript
   import { init } from '@launchdarkly/node-server-sdk';
   import { initAi } from '@launchdarkly/server-sdk-ai';

   // Node SDK 没有显式的离线模式 — 缺少或无效的密钥在 `waitForInitialization` 期间快速失败，
   // 并且每个 `agent_config` / `completion_config` 调用都返回回退值。记录警告；不要抛出。
   if (!process.env.LD_SDK_KEY) {
     console.warn('LD_SDK_KEY 未设置；配置将仅使用回退值。');
   }
   const ldClient = init(process.env.LD_SDK_KEY ?? 'sdk-offline');
   await ldClient.waitForInitialization({ timeout: 10 }).catch(() => {
     // 在离线模式下吞下初始化失败；回退路径运行。
   });
   const aiClient = initAi(ldClient);
   ```

4. **移交给 `configs-create`。** 打印从第一阶段清单中提取的模型、提示/指令、参数和模式，然后告诉用户：*"使用这些输入运行 `/configs-create`，然后回来这里。"* 提供您希望代码调用的配置密钥（例如 `chat-assistant`）。不要尝试自动调用兄弟技能 — 等待用户完成后再继续。

   **`configs-create` 完成后，用户还必须运行 `/configs-targeting` 以将新变体提升为回退路径。** 新创建的变体将对每个消费者返回 `enabled=False`，直到目标更新。跳过此步骤和第二阶段验证（下一个小步骤 9）将在每次请求上静默地使用回退路径。

5. **将模板占位符重写为 Mustache 语法。** 如果硬编码的提示使用 Python `.format()`、f-strings、JS 模板字面量或任何其他非 Mustache 语法（例如 `{system_time}`、`${userName}`、`%(topic)s`），请将每个占位符重写为 `{{ variable }}` Mustache 形式。在即将发送到 `/configs-create` 的文件和您将在下一个小步骤 6 中写入的回退字符串中执行此操作。AI SDK 通过在 LD 服务路径和回退路径上使用 Mustache 渲染器以及使用第四个参数 `variables` 字典来 `completion_config(...)` / `completionConfig(...)` 插值变量。在回退中保留 Python 风格的 `{system_time}` 字面量会导致当 LaunchDarkly 不可用时出现静默回归 — 渲染器不会匹配单大括号形式，并且字面量 `{system_time}` 会作为提示的一部分发送给提供商。

   **之前:**
   ```python
   SYSTEM_PROMPT = "You are a helpful assistant. The time is {system_time}."
   prompt = SYSTEM_PROMPT.format(system_time=datetime.now().isoformat())
   ```

   **之后（在源代码中）:**
   ```python
   SYSTEM_PROMPT = "You are a helpful assistant. The time is {{ system_time }}."
   # 在调用位置移除 `.format()` — SDK 通过 `variables` 插值
   config = ai_client.completion_config(
       CONFIG_KEY,
       context,
       fallback,
       variables={"system_time": datetime.now().isoformat()},
   )
   ```

   常见的形状需要重写：
   - Python `"{var}"` / `"{var!s}"` / `"%(var)s"` → `"{{ var }}"`
   - JS/TS `` `${var}` `` 模板字面量在提示字符串内 → `"{{ var }}"`
   - 任何手写的 `str.replace("__VAR__", value)` 方案 → `"{{ var }}"`

   参考 [fallback-defaults-pattern.md § Template placeholders](references/fallback-defaults-pattern.md) 获取回退特定的变体。

6. **构建回退。** 反射您提取的硬编码值。在 Python 中使用 `AICompletionConfigDefault` / `AIAgentConfigDefault`，在 Node 中使用普通的对象字面量。参考 [fallback-defaults-pattern.md](references/fallback-defaults-pattern.md) 获取内联、文件后援和引导生成的模式。

   **Python 回退（完成模式）:**
   ```python
   from ldai.client import AICompletionConfigDefault, ModelConfig, ProviderConfig, LDMessage

   fallback = AICompletionConfigDefault(
       enabled=True,
       model=ModelConfig(name="gpt-4o", parameters={"temperature": 0.7, "max_tokens": 2000}),
       provider=ProviderConfig(name="openai"),
       messages=[LDMessage(role="system", content="You are a helpful assistant...")],
   )
   ```

7. **替换硬编码的调用位置。** 将硬编码的模型/提示/参数替换为 `completion_config` / `completionConfig`（或 `agent_config` / `agentConfig`），然后将返回的字段读取到现有的提供商调用中。保留提供商调用完整。

   **Python — 之前:**
   ```python
   response = openai_client.chat.completions.create(
       model="gpt-4o",
       temperature=0.7,
       max_tokens=2000,
       messages=[
           {"role": "system", "content": "You are a helpful assistant..."},
           {"role": "user", "content": user_input},
       ],
   )
   ```

   **Python — 之后:**
   ```python
   context = Context.builder(user_id).set("email", user.email).build()
   config = ai_client.completion_config("chat-assistant", context, fallback)

   if not config.enabled:
       return disabled_response()

   params = config.model.parameters or {}
   response = openai_client.chat.completions.create(
       model=config.model.name,
       temperature=params.get("temperature"),
       max_tokens=params.get("max_tokens"),
       messages=[m.to_dict() for m in (config.messages or [])] + [
           {"role": "user", "content": user_input},
       ],
   )
   ```

   **Python — 之后（代理模式）** — 对于 LangGraph、CrewAI 或任何接受目标/指令字符串的框架：

   ```python
   context = Context.builder(user_id).kind("user").build()
   config = ai_client.agent_config("support-agent", context, FALLBACK)

   if not config.enabled:
       return disabled_response()

   # config 是一个 AIAgentConfig 对象 — 不是 `(config, tracker)` 元组。
   # 通过工厂每次执行获取 tracker：tracker = config.create_tracker()
   model_name = f"{config.provider.name}/{config.model.name}"
   instructions = config.instructions
   params = config.model.parameters or {}

   # 将 model_name + instructions 传递到您的框架的代理构造函数中。
   # 示例：LangGraph 预构建代理（Python — `from langchain.agents import create_agent`；
   # 这替换了 `langgraph.prebuilt.create_react_agent`，在 LangGraph 1.0 中已弃用，
   # 在 2.0 中已移除。相同的返回形状；`prompt=` 已重命名为 `system_prompt=`。）
   # agent = create_agent(
   #     create_langchain_model(config),  # 转发每个变体参数
   #     TOOLS,                            # 第三阶段将使用配置的工具加载器替换此配置.tools
   #     system_prompt=instructions,
   # )
   ```

   参考 [before-after-examples.md](references/before-after-examples.md) 获取完整的 Python OpenAI、Node Anthropic 和 LangGraph 代理模式配对片段。

8. **检查 `config.enabled`。** 如果它返回 `False`，则处理禁用路径，不要崩溃，也不要调用提供商。此检查是必需的 — 不是可选的。

9. **验证。** 使用有效的 `LD_SDK_KEY` 运行应用；确认调用成功并且响应与迁移前输出匹配。然后临时设置 `LD_SDK_KEY=sdk-invalid`（或取消设置它）并确认回退路径无错误运行。两个路径都必须工作，然后才能进入第三阶段。

委托：**`configs-create`**（下一个小步骤 4）。

### 第三阶段：将工具移入配置（第三阶段）

如果经过审计的应用没有函数调用/工具，则跳过此步骤。否则：

1. **枚举当前注册的工具。** 常见形状如下：

   - `openai.chat.completions.create(tools=[...])` — OpenAI 直接
   - `anthropic.messages.create(tools=[...])` — Anthropic 直接
   - `create_agent(llm, tools=[...], system_prompt=...)` — LangGraph 预构建（Python，`langchain.agents`；替换已弃用的 `langgraph.prebuilt.create_react_agent`)
   - `createReactAgent({ llm, tools: [...] })` — LangGraph.js 预构建（Node，`@langchain/langgraph/prebuilt`)
   - `Agent(tools=[...])` — CrewAI
   - `Agent(tools=[...])` — Strands（Python `@tool`-装饰的调用able通过构造函数传递；TS SDK 使用 Zod-模式工具）
   - **自定义 `StateGraph`** — 模块级别的 `TOOLS = [...]` 列表在 **`model.bind_tools(TOOLS)`** 和 **`ToolNode(TOOLS)`** 中引用。这是 `langchain-ai/react-agent` 模板形状；列表通常在 `tools.py` 模块中。一起搜索 `bind_tools(` 和 `ToolNode(` — 它们将指向相同的列表。

   记录每个工具的名称、描述和 JSON 模式。

   对于使用 `@tool` 定义的 LangChain/LangGraph 工具，通过 `tool.args_schema.model_json_schema()`（或等效的 Pydantic `model_json_schema()` 调用）提取模式。对于用作工具的普通异步调用able（在自定义 `StateGraph` 形状中很常见），LangChain 在绑定时从函数签名推断模式 — 通过 `StructuredTool.from_function(fn).args_schema.model_json_schema()` 提取它。不要手写模式。

2. **移交给 `tools`。** 打印提取的工具名称、描述和模式，然后告诉用户：*"使用这些工具和变体密钥运行 `/tools`，然后回来这里。"* 兄弟技能创建工具定义（`create-ai-tool`）并将它们附加到变体（`update-ai-config-variation`）。等待用户完成后再继续到下一个小步骤 3。不要自动调用。

3. **在调用位置替换硬编码的工具数组** 为从 `config.tools`（或您的语言的 SDK 等效项）读取。动态加载实际实现函数，参考 [agent-mode-frameworks.md](references/agent-mode-frameworks.md) 获取来自 devrel 代理教程的动态工具工厂模式。

   **对于自定义 `StateGraph` 形状**，您必须更新 **两个** 调用位置：`.bind_tools(TOOLS)` 和 `ToolNode(TOOLS)` 必须都读取自 `config.tools`-派生的列表。遗漏一个会导致 LLM 看到新工具，但执行者仍然运行旧工具，反之亦然。

4. **验证。** 运行应用；确认工具流程仍然正确执行。`get-ai-config`（通过委托）确认工具在服务器端附加。

委托：**`tools`**（下一个小步骤 2）。

### 第四阶段：监控追踪器（第四阶段）

委托：**`built-in-metrics`** 将每个请求的 `tracker.track_*` 调用（持续时间、令牌、成功/错误、反馈）围绕提供商调用。如果应用需要超出内置代理的业务指标，请与 **`custom-metrics`** 一起使用。注意：不要将其与 `launchdarkly-metric-instrument` 混淆，后者用于 `ldClient.track()` 功能指标 — 不同的 API。参考 [sdk-ai-tracker-patterns.md](references/sdk-ai-tracker-patterns.md) 获取委托技能使用的完整 Python + Node 方法矩阵。

移交：打印配置密钥、变体密钥、提供商以及调用是否为流式，然后告诉用户：*"使用这些输入运行 `/built-in-metrics`，然后回来这里。"* 不要自动调用。完成后再回来进行下一个小步骤 5（验证）。

1. **创建追踪器。** 通过在第二阶段返回的配置上的工厂获取每个执行追踪器：`tracker = config.create_tracker()`（Python）或 `const tracker = aiConfig.createTracker();`（Node）。每次用户回合调用工厂 **一次** 并重用返回的 `tracker`，在该回合中的每个追踪调用中使用 — 每个调用都会生成一个新鲜的 `runId`，该 `runId` 会标记从该回合发出的每个事件，以便通过导出事件或下游查询进行关联。（监控标签今天聚合；运行级分组是下游问题 — 但 `runId` 也是 SDK 的最多一次保护键，因此在中回合生成新的 `runId` 会破坏保护语义，无论事件最终在哪里结束。）

   **调用工厂的位置取决于调用形状:**

   - **完成模式/一次性提供商调用：** 在 `completion_config(...)` 返回后立即生成追踪器，在处理请求的同一函数中。
   - **代理模式与 ReAct 循环（LangGraph、LangChain、自定义）：** 在循环执行 **一次** 之前在专用的 `setup_run` 入口节点中生成追踪器，将其存储在图状态上，并在 `call_model` / 工具处理程序 / 终端 `finalize` 节点中读取它。在循环体内发出 `track_duration` / `track_tokens` / `track_success` 将触发最多一次保护。参考 [agent-mode-frameworks.md § Custom `StateGraph` (run-scoped architecture)](references/agent-mode-frameworks.md) 获取完整的 `setup_run` + `call_model` + `finalize` 模式。
   - **管理运行者（第一级）：** 完全跳过此步骤。`ManagedModel` 每次调用 `run()` / `invoke()` 内部生成追踪器。如果应用使用的是，请移至下一个小步骤 4。

2. **从四级阶梯中选择一个级别。** 参考 [sdk-ai-tracker-patterns.md § Tier 决策表](references/sdk-ai-tracker-patterns.md) 获取完整表格（聊天循环 → 第一级；提供商包调用 → 第二级；自定义提取器 → 第三级；流式/手动 → 第四级）。

3. **连接选择的级别。** 委托技能为每个级别提供完整的 Python + Node 示例，以及每个提供商的文件。以下是 OpenAI 通过提供商包的简化的第二级/三级示例：

   **Python:**
   ```python
   from ldai_openai import get_ai_metrics_from_response
   import openai

   client = openai.OpenAI()

   tracker = config.create_tracker()

   def call_openai():
       return client.chat.completions.create(
           model=config.model.name,
           messages=[{"role": "system", "content": config.messages[0].content},
                     {"role": "user", "content": user_prompt}],
       )

   # 异常会自动跟踪 — `track_metrics_of` 捕获异常，
   # 记录 `tracker.track_error()`，然后重新抛出。仅对本地处理（日志记录、回退）
   # 包装自己的 try/except。
   response = tracker.track_metrics_of(get_ai_metrics_from_response, call_openai)
   ```

   **Node:**
   ```typescript
   import { getAIMetricsFromResponse } from '@launchdarkly/server-sdk-ai-openai';

   const tracker = aiConfig.createTracker();
   // 异常会自动跟踪 — `trackMetricsOf` 捕获异常，
   // 记录 `tracker.trackError()`，然后重新抛出。
   const response = await tracker.trackMetricsOf(
     getAIMetricsFromResponse,
     () => openaiClient.chat.completions.create({
       model: aiConfig.model!.name,
       messages: [...aiConfig.messages, { role: 'user', content: userPrompt }],
     }),
   );
   ```

为Anthropic直接、Bedrock（无提供者包）、Gemini和自定义HTTP，编写一个小型提取器返回`LDAIMetrics`——参见代理技能的[anthropic-tracking.md](../built-in-metrics/references/anthropic-tracking.md)、[bedrock-tracking.md](../built-in-metrics/references/bedrock-tracking.md)和[gemini-tracking.md](../built-in-metrics/references/gemini-tracking.md)。LangChain单节点和LangGraph通过`launchdarkly-server-sdk-ai-langchain` / `@launchdarkly/server-sdk-ai-langchain`提供者包。使用`create_langchain_model(config)`（Python） / `createLangChainModel(config)`（Node）构建模型——两者都转发所有变体参数——并通过`get_ai_metrics_from_response` / `getAIMetricsFromResponse`进行跟踪。参见[langchain-tracking.md](../built-in-metrics/references/langchain-tracking.md)。

4. **如果应用程序具有点赞/点踩UI，则连接反馈跟踪。** 两个SDK都暴露了带有`{kind}`参数的`trackFeedback`。

   **Python:**
   ```python
   from ldai.tracker import FeedbackKind
   tracker.track_feedback({"kind": FeedbackKind.Positive})
   ```

   **Node:**
   ```typescript
   import { LDFeedbackKind } from '@launchdarkly/server-sdk-ai';
   tracker.trackFeedback({ kind: LDFeedbackKind.Positive });
   ```

   **跨进程的延迟反馈。** 如果点赞UI在不同的进程（而不是生成响应的进程）中触发，则**不要**在消费者中再次调用`create_tracker()`——这将生成一个新的`runId`。将跟踪器的恢复令牌（Python中的`tracker.resumption_token`，Node中的`tracker.resumptionToken`）与消息一起持久化，然后在反馈处理程序中使用`LDAIConfigTracker.from_resumption_token(...)`（Python）或`aiClient.createTracker(token, context)`（Node）重新激活跟踪器。

5. **验证。** 在暂存环境中点击包装的端点，然后在LaunchDarkly中打开配置的监控选项卡。持续时间、令牌和生成计数应在1-2分钟内出现。如果什么都没有显示，请按照[sdk-ai-tracker-patterns.md](references/sdk-ai-tracker-patterns.md)下的“故障排除”清单进行操作。

### 第5步：附加评估（第5阶段）

1. **在三个评估路径之间进行选择。** 这是最常被误解的阶段——有**三个**路径，而不是两个，迁移环境中的正确默认值通常是人们跳过的那个。

   | 路径 | 使用时机 | 是否支持代理模式？ |
   |------|-------------|---------------------|
   | **离线评估**（推荐迁移默认值） | 发布前回归：在LD Playground中通过新变体运行固定数据集，并与基线进行评分。最适合迁移，因为您希望在发布之前证明新配置的行为至少与硬编码版本一样好。 | 是——所有模式 |
   | **UI附加自动判断** | 在LD UI中将一个或多个判断器附加到变体上；判断器在采样的实时请求上自动运行。无需代码更改。 | 完成模式仅（今天的UI小部件仅支持完成） |
   | **程序化直接判断** | 在请求处理程序中调用`ai_client.create_judge(...)`，并在每次调用上对`input`和`output`调用`judge.evaluate`。增加每个请求的成本和代码复杂性。最适合工作流的持续实时评分，其中采样的自动判断不够。 | 是——所有模式（SDK以相同方式处理两者） |

   **大多数迁移用户应从离线评估开始**，然后在发布稳定后，如果需要持续实时评分，才添加程序化直接判断。

2. **对于代理模式迁移，默认使用离线评估。** UI附加自动判断仅支持完成模式。代理模式的文档路径是：(a) 通过LD Playground + 数据集的**离线回归**（适用于所有模式），或 (b) **程序化直接判断**，将其连接到调用位置。从审计清单生成一个起始数据集CSV（每行一个代表性输入），并将用户指向[离线评估指南](https://docs.launchdarkly.com/guides/ai-configs/offline-evaluations)进行Playground演练。只有在用户明确要求持续实时评分时，才将程序化直接判断连接到生产代码。

   **推荐迁移的离线评估形状：**
   - 首先将`default`变体（或镜像迁移前硬编码行为的变体）与数据集运行——这是基线。
   - 将其克隆到第二个变体，指向**不同的模型系列**（例如，如果基线是`anthropic/claude-sonnet-4-5`，则克隆到`openai/gpt-4o`或`openai/gpt-4o-mini`）。跨系列比较比跨兄弟更有信息量。
   - 附加内置**准确性**判断器，通过**0.85**的通过阈值，并让两个变体针对同一数据集运行。
   - 只有当它在准确性上胜过基线，并且在相关性或毒性上没有回归时，才通过`/configs-targeting`将获胜者提升为fallthrough。

   将此形状写入项目的`datasets/README.md`（或等效文件），以便在迁移发布后可重复比较模式。

3. **移交给`online-evals`**——仅适用于UI附加判断（完成模式）或创建将被程序化路径引用的自定义判断配置。告诉用户：*"使用这些输入运行`/online-evals`，然后回来。"*不要自动调用。传递：
   - 父配置键和变体键
   - 内置判断器（准确性、相关性、毒性）或自定义判断器键的列表以创建/附加
   - 目标环境

   代理处理创建自定义判断器配置、通过变体PATCH端点附加它们，并为每个判断器配置设置fallthrough。离线评估**不**通过此代理——这是一个Playground工作流，而不是API写入。

4. **对于程序化直接判断：连接`create_judge` + `evaluate` + `track_judge_result`。** 这是第5阶段唯一写入代码的路径。Python形状：

   ```python
   from ldai.client import AIJudgeConfigDefault

   judge = ai_client.create_judge(
       judge_key,                               # LD中的判断器配置键
       ld_context,
       AIJudgeConfigDefault(enabled=False),     # 备用：如果SDK未命中则跳过评估
   )

   if judge and judge.enabled:
       result = await judge.evaluate(
           input_text,
           output_text,
           sampling_rate=0.25,                  # 可选；默认1.0（始终评估）
       )
       if result.sampled:
           tracker.track_judge_result(result)
   ```

   四条规则：
   - **`create_judge`返回`Optional[Judge]`。** 始终使用`if judge and judge.enabled:`进行保护——如果上下文中禁用判断器配置或提供者缺失，它将返回`None`。对`None`返回进行直接`.evaluate()`将引发`AttributeError`。
   - **传递`AIJudgeConfigDefault`**，而不是`AICompletionConfigDefault`。`create_judge`的`default`参数是类型为`Optional[AIJudgeConfigDefault]`；传递完成类型将无法通过类型检查，并且在某些较旧的示例中是文档级别的错误。
   - **`sampling_rate`是`evaluate()`的参数**，而不是`create_judge`的。它默认为`1.0`（每次调用评估）。对于实时路径，传递较低值（0.1–0.25）以控制成本。
   - **`evaluate()`返回一个`JudgeResult`**（永远不会是`None`）。检查`result.sampled`以知道评估是否实际运行，并调用`track_judge_result(result)`。Node使用`trackJudgeResult(result)`和`LDJudgeResult`，具有相同的`sampled`字段。

   **询问用户要使用哪个判断器配置键。** LaunchDarkly提供三个内置判断器——准确性、相关性、毒性——但内置的实际配置**键**不是规范的SDK常量，也未记录。让用户在LD UI中打开**AgentControl > Library**并复制他们要引用的判断器的键，或者先通过`configs-create`创建自定义判断器配置。

5. **验证。**
   - **UI附加自动判断器：** 在暂存环境中触发请求，打开监控选项卡→“评估器指标”下拉菜单。在配置的采样率下，分数在1-2分钟内出现。
   - **程序化直接判断：** 点击包装的端点，并确认`track_judge_result`出现在父配置的监控选项卡上。
   - **离线评估：** 在LD Playground中运行数据集，并逐侧比较基线与新变体分数。无需运行时连接。

代理：**`online-evals`**（子步骤3，可选——仅适用于UI附加判断器或自定义判断器创建；离线评估不代理）。

## 边缘情况

| 情况 | 操作 |
|-----------|--------|
| 应用程序已经为功能标志初始化`LDClient` | 重用它——将现有客户端传递给`LDAIClient()` / `initAi()`，不要创建第二个客户端 |
| 应用程序使用LangChain `ChatOpenAI(model=...)` | 用`create_langchain_model(config)`（Python）或`createLangChainModel(config)`（Node）替换手写的模型构建。不要读取`config.model.name`并手动将其传递给`ChatOpenAI(model=...)`——这种模式会丢失除明确命名的参数之外的所有变体参数 |
| 提供者调用周围的重试包装器 | 跟踪器在用户回合顶部生成一次；重试循环在同一个范围内。每个重试尝试共享相同的`runId`。跟踪器调用（`track_duration` / `track_tokens` / `track_success` / `track_error`）位于重试体*外部*——在回合结束时的成功路径或最终失败路径上调用一次 |
| 应用程序没有工具——跳过第3阶段 | 直接从第2阶段验证到第4阶段（跟踪） |
| 模式不匹配：用户说代理，审计显示单次聊天 | 选择完成模式，除非应用程序使用LangGraph预构建代理（Python中的`langchain.agents.create_agent`或Node中的`createReactAgent`）、CrewAI `Agent`、Strands `Agent`或类似的以目标为导向的框架 |
| 应用程序使用Strands Agents（Python） | 代理模式。构建一个`create_strands_model`调度器，按`agent_config.provider.name`键值返回`AnthropicModel(model_id=..., max_tokens=...)`或`OpenAIModel(model_id=..., params=...)`。在将参数传递给模型类之前丢弃`parameters.tools`——Strands通过`Agent(tools=[...])`接收工具。跟踪是第3级：用`tracker.track_duration_of(...)`包装`invoke_async`并记录来自`result.metrics.accumulated_usage`的令牌。参见[agent-mode-frameworks.md § Strands Agent](references/agent-mode-frameworks.md)和[strands-tracking.md](../built-in-metrics/references/strands-tracking.md) |
| TypeScript上的Strands应用程序 | TS SDK仅提供`BedrockModel`和`OpenAIModel`——无法提供Anthropic支持的变体。如果需要多提供者变体，请使用Python SDK |
| 使用Anthropic SDK的TypeScript应用程序 | 不存在`trackAnthropicMetrics`辅助函数。使用第3级：`trackMetricsOf`与一个小型自定义提取器，该提取器读取`response.usage.input_tokens` / `response.usage.output_tokens`并返回`LDAIMetrics`。参见[anthropic-tracking.md](../built-in-metrics/references/anthropic-tracking.md)在`built-in-metrics`技能中获取确切的提取器 |
| 由于缺少`LD_SDK_KEY`而回退将静默崩溃 | 记录启动警告；继续回退。切勿在导入时引发异常 |
| 多代理图（监督者+工作器） | 迁移单个代理后停止。代理图定义在**两者**SDK中都可用——Python通过`launchdarkly-server-sdk-ai.agent_graph`，Node通过`@launchdarkly/server-sdk-ai`中的图API。阅读[agent-graph-reference.md](references/agent-graph-reference.md)以获取图级别的迁移路径——它故意超出此技能的主要范围 |
| 单代理（ReAct、工具循环）+代理模式 | 默认通过LD Playground + 数据集在第5阶段使用离线评估。今天的UI附加判断器仅支持完成，程序化直接判断增加了每次调用的成本，通常在迁移上线并稳定后才有价值。指向[离线评估指南](https://docs.launchdarkly.com/guides/ai-configs/offline-evaluations) |
| 具有Pydantic `args_schema`的工具（LangChain `@tool`） | 通过`tool.args_schema.model_json_schema()`提取模式；不要手动编写用于代理的JSON模式 |
| 自定义`StateGraph`具有通过`.bind_tools(TOOLS)`绑定在模块级别`TOOLS`列表并通过`ToolNode(TOOLS)`运行（例如`langchain-ai/react-agent`模板） | 找到`TOOLS`列表（通常在单独的`tools.py`模块中）。以相同方式提取模式。交换**两者**调用位置——`.bind_tools(...)`和`ToolNode(...)`——以从相同的`config.tools`派生列表读取 |
| 应用程序已经将配置外部化为`Context`数据类，具有环境变量回退（例如`react-agent`模板的`context.py`） | 用`ai_client.agent_config(...)`替换`runtime.context.model` / `runtime.context.system_prompt`的消费者，并从返回的`AIAgentConfig`中读取。**清空数据类**而不是将其保留为回退形状——规范的回退是在Python中（在`agent_config`调用附近的一个顶级常量`FALLBACK = AIAgentConfigDefault(...)`），而不是一个平行的Python数据类。回退值的两个来源会导致真相漂移。空的`Context`只是一个满足LangGraph的`context_schema`要求的占位符；`thread_id`和任何其他每个请求的管道都通过`config: RunnableConfig`而不是（参见[agent-mode-frameworks.md § Custom `StateGraph`](references/agent-mode-frameworks.md)） |

## 不要做的事情

这些是按首次运行失败出现的可能性排序的。前三个规则——关于跟踪器和配置生命周期——占大多数“迁移看起来完成但监控选项卡是碎片化/错误的”报告。

### 跟踪器和配置生命周期（最常见失败模式）

- **不要在用户回合中多次调用`create_tracker()` / `createTracker()`。** 一个回合=完整的请求/响应周期，包括每个ReAct迭代、工具调用和重试。
- **不要在循环体内部调用`track_duration` / `track_tokens` / `track_success` / `track_error` / `track_time_to_first_token`。** 这些最多一次每个跟踪器；第二次调用会被丢弃。在循环内累积，在终端/最终节点发出一次。每次事件方法（`track_tool_call`，`track_tool_calls`，`track_feedback`，`track_judge_result`）可以重复调用。完整矩阵：[sdk-ai-tracker-patterns.md § At-most-once guards](references/sdk-ai-tracker-patterns.md)。
- **不要在用户回合中多次调用`agent_config()` / `completion_config()`。** 每次调用都是一个标志评估，并发出一个`$ld:ai:agent:config`事件。在循环步骤或工具体内部重新获取会膨胀监控选项卡上的代理配置计数，并允许中途目标更改在单个回合中交换LLM调用。在顶部解决一次，将状态存储在状态中，并让每个后续消费者从状态中读取。需要变体范围旋钮的工具应使用工具工厂模式（在设置时间关闭时捕获旋钮的`make_search(ai_config)`）——参见[agent-mode-frameworks.md § Getting knobs into tools](references/agent-mode-frameworks.md)。
- 不要跨请求缓存配置对象——每个回合解决一次，是的，但仍然每个回合解决一次。在模块范围内缓存完全破坏了目标更改机制。
- 不要在LaunchDarkly连接后删除回退。它对于`enabled=False`和SDK无法到达的路径是必需的。
- 不要元组解包`completion_config` / `agent_config` / `completionConfig` / `agentConfig`的返回值。它们返回一个**单个**配置对象（例如`AIAgentConfig`，`AICompletionConfig`），而不是`(config, tracker)`。通过调用`config.create_tracker()` / `aiConfig.createTracker()`获取跟踪器。LLMs会同时产生元组形状和`config.tracker`属性——实际API是一个工厂。

- **如果仓库中已经包含一个 `load_chat_model(f"{provider}/{name}")` 辅助函数，请删除它——不要仅仅避免使用它。** 这个确切的结构随 `langchain-ai/react-agent` 一起发布，并复制到几十个衍生仓库中；查找 `utils.load_chat_model`、`utils.build_model` 或任何接受一个参数的 `init_chat_model` 包装器，该包装器将 `"provider/model"` 字符串拆分。重用它是最初运行时的失败模式：每个变体参数（温度、最大令牌数、top_p、停止序列）都无声地掉落在地上，因为 `init_chat_model` 只接收名称和提供者。`create_langchain_model(ai_config)` 是一对一的替代方案，它转发整个 `model.parameters` 字典。替换每个调用点，然后在文件侧删除包装器文件，以便下一个读者无法触及它。
- **相同的规则适用于手工编写的 `resolve_tools` / `TOOL_REGISTRY` / `ALL_TOOLS` 辅助函数。** 如果模板已经有一个 `resolve_tools(tool_keys)` 或一个模块级别的 `ALL_TOOLS` 列表，请从 `ldai_langchain.langchain_helper` 导入 `build_structured_tools` 并删除手工编写的版本。`build_structured_tools(ai_config, TOOL_REGISTRY_DICT)` 读取 `ai_config.model.parameters.tools` 并将匹配的可调用项包装为 LangChain `StructuredTool`，其中 LD 工具键作为 `StructuredTool.name` — 因此 `ToolNode` 查找可以在没有第二个映射的情况下工作。不要将两者都保留在仓库中。
- 不要将应用范围的开关直接放在 `model.parameters` 中。`create_langchain_model` 通过 `init_chat_model` 将 `parameters` 中的每个键转发给提供者 SDK，因此 `max_search_results` / `retry_budget` / `feature_toggle` 条目会因意外的关键字参数错误而使提供者崩溃。正确的位置是 `model.custom`，提供者辅助函数会忽略它，而应用通过 `ai_config.model.get_custom("key")` 读取它。MCP `update-ai-config-variation` 工具目前没有公开顶层 `custom`，因此选择以下两种路径之一：(a) 通过 REST API 补丁变体以直接设置 `model.custom`，或 (b) 通过 MCP 在 `parameters.custom`（作为嵌套字典）中设置它，并使用防御性访问器读取这两个位置。包含代码示例的完整步骤说明在 [langchain-tracking.md § MCP 注意事项](../built-in-metrics/references/langchain-tracking.md)。
- 不要在回退中重新编码工具模式。当 LaunchDarkly 不可用时，回退应该在没有工具（或使用应用程序为保持运行所需的最小提供者绑定参数）的情况下运行。构建 `_FALLBACK_TOOLS` 数组以复制配置的工具模式会重新引入迁移本应从代码中移除的硬编码配置。
- 不要从 `ldai.langchain` 导入 `LaunchDarklyCallbackHandler`——类和点式模块路径都不存在。Python LangChain 辅助函数包是 `ldai_langchain`（顶层模块，下划线）。使用 `create_langchain_model(config)` + `track_metrics_of_async(get_ai_metrics_from_response, lambda: llm.ainvoke(messages))` 作为规范模式。

### 阶段 / 交接规范

- 即使用户说“直接包装它”，也不要跳过步骤 1。没有审计，回退将偏离硬编码行为。
- 在提取提示和模型之前不要委托给 `configs-create`——委托者需要它们作为输入。
- 在初始 `setup-ai-config` 期间不要尝试附加工具。工具附加是一个由 `tools` 拥有的单独步骤。
- 不要声称你“委托给 `configs-create`”或任何其他兄弟技能。此技能不会自动调用。在每个交接时，打印输入并告诉用户运行兄弟斜杠命令，然后等待。否则会误导用户关于刚刚发生了什么。
- 在阶段 2 和阶段 4 之间不要跳过 `/configs-targeting` 步骤。新创建的变体返回 `enabled=False`，直到目标推广它为回退——阶段 2 验证将在每个请求上静默地采取回退路径。
- 不要尝试一次性进行多代理图迁移。首先迁移单个代理；使用 [agent-graph-reference.md](references/agent-graph-reference.md) 作为下一步阅读。

### 阶段 5 评估

- 在跟踪器就位之前不要连接评估。裁判评分流量；没有阶段 4 流量，就没有可评分的内容。
- 不要将阶段 5 表述为“要么 UI 要么程序化”。有**三个**路径：离线评估（推荐默认迁移）、UI 附加自动裁判（仅完成模式）、程序化直接裁判。大多数人会跳过离线评估，并且通常是正确的起点。
- 不要将 `sampling_rate` 传递给 `create_judge`——它是 `Judge.evaluate()` 的参数，不是 `create_judge()` 的参数。
- 不要硬编码裁判配置键（`"accuracy-judge"`、`"relevance-judge"` 等）。内置键不是规范 SDK 常量；请要求用户在 LD UI 中的 **AgentControl > Library** 中查找它们。
- 在 `create_judge` 之后不要忘记 `if judge and judge.enabled:` 守卫。它返回 `Optional[Judge]`，并且在上下文禁用裁判配置时返回 `None`。

### API 表面注意事项

- 不要在阶段 4（跟踪）中使用 `launchdarkly-metric-instrument`。该技能用于 `ldClient.track()` 功能指标，而不是代理 `tracker.track_*` 调用——它们是不同的 API。
- 不要在 Python 中使用 `track_request()`——它不存在于 `launchdarkly-server-sdk-ai`。使用 `track_metrics_of` 并提供者包或自定义提取器，或者如果你在流路径上，则降至显式的 `track_duration` + `track_tokens` + `track_success` / `track_error`。
- 不要将 `graph_key=...` 传递给 Python 中的 `tracker.track_*()` 方法——它不是接受的参数。在图遍历中获得的跟踪器会自动配置正确的图键。

## 相关技能

- `configs-create` — 由阶段 2 调用来创建配置
- `tools` — 由阶段 3 调用来创建和附加工具定义
- `online-evals` — 由阶段 5 调用来附加裁判
- `configs-variations` — 在迁移完成后添加用于 A/B 测试的变体
- `configs-targeting` — 在迁移完成后将新变体推送给用户
- `configs-update` — 随着应用的演变修改配置属性
- `launchdarkly-metric-instrument` — 用于 `ldClient.track()` 功能指标（不用于代理跟踪调用）

## 参考

- [phase-1-analysis-checklist.md](references/phase-1-analysis-checklist.md) — 步骤 1 审计清单、grep 模式、SDK 路由表、模式决策树
- [before-after-examples.md](references/before-after-examples.md) — 配对硬编码到包装的 Python OpenAI、Node Anthropic、Python LangGraph 示例
- [sdk-ai-tracker-patterns.md](references/sdk-ai-tracker-patterns.md) — Python 和 Node 端的每个 `tracker.track_*` 方法并排、自动辅助器矩阵和常见注意事项
- [agent-mode-frameworks.md](references/agent-mode-frameworks.md) — 如何将 `agent_config` 链接到 LangGraph、CrewAI 和自定义 react 循环；动态工具加载模式
- [fallback-defaults-pattern.md](references/fallback-defaults-pattern.md) — 三个回退模式（内联、文件后援、引导生成）以及何时使用每个模式
- [agent-graph-reference.md](references/agent-graph-reference.md) — 多代理迁移的超出范围指针文档
