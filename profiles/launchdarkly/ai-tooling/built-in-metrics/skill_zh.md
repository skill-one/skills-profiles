# 代理指标监控

你正在使用一个技能，将 LaunchDarkly 代理指标围绕现有的提供者调用进行配置。你的工作是对现有内容进行审计，从下方的梯形中选择合适的层级，并实现它，同时确保监控标签页所需的指标（持续时间、输入/输出令牌、成功/失败，以及流式传输时的TTFT）被捕获，且过程尽可能简洁。

最重要的一点：**默认选择与调用形状最匹配的最高层级**。选择较低层级（“手动编写追踪器调用”）看似灵活，但会导致指标漂移、遗漏指标以及SDK已经弃用的传统模式。

## 四层级梯形

这是官方SDK README（Python核心、Node核心以及每个提供者包）推荐的顺序。从顶部开始向下查找，并在第一个匹配的层级停止：

| 层级 | 模式 | 使用场景 | 自动追踪 |
|------|-------|----------|----------|
| **1 — 管理运行器** | Python: `ai_client.create_model(...)` 返回 `ManagedModel`，然后 `await model.run(...)`。 <br>Node: `aiClient.createModel(...)` 返回 `ManagedModel`，然后 `await model.run(...)`。 | 调用是会话式的（聊天历史、回合制）。这是提供者README重点介绍的内容。 | 持续时间、令牌、成功/失败——**全部自动追踪，无需追踪器调用**。 |
| **2 — 提供者包 + `trackMetricsOf`** | `tracker.trackMetricsOf(Provider.getAIMetricsFromResponse, () => providerCall())`。当前提供者包：`@launchdarkly/server-sdk-ai-openai`、`-langchain`、`-vercel`（Node）和 `launchdarkly-server-sdk-ai-openai`、`-langchain`（Python）。 | 调用形状不是聊天循环（单次完成、结构化输出、代理步骤），但框架或提供者有包可用。 | 来自包装器的持续时间和成功/失败；来自包内置的 `getAIMetricsFromResponse` 提取器的令牌。 |
| **3 — 自定义提取器 + `trackMetricsOf`** | 相同的 `trackMetricsOf` 包装器，但你编写一个小函数，将提供者响应映射到 `LDAIMetrics`（令牌+成功）。 | 不存在提供者包（Anthropic直接调用、Gemini、Cohere、自定义HTTP）。 | 来自包装器的持续时间和成功/失败；来自你的提取器的令牌。 |
| **4 — 原始手动** | 分别调用 `trackDuration`、`trackTokens`、`trackSuccess` / `trackError`，以及流式传输时调用 `trackTimeToFirstToken`。 | 流式传输带TTFT、不寻常的响应形状、部分追踪、任何2-3层级无法清晰包装的内容。 | 仅追踪你显式调用的内容——你需要确保不遗漏任何指标。 |

每个提供者——OpenAI、LangChain、Vercel、Bedrock、Anthropic、Gemini、自定义HTTP——都使用相同的通用形状：Node中的 `tracker.trackMetricsOf(getAIMetricsFromResponse, () => providerCall())`，Python中的 `tracker.track_metrics_of(get_ai_metrics_from_response, provider_call)`。提取器是唯一随提供者变化的元素：从匹配的 `@launchdarkly/server-sdk-ai-<provider>`（或 `ldai_<provider>`）包中导入 `getAIMetricsFromResponse`，或者编写一个小自定义函数返回 `LDAIMetrics`。没有提供者特定的追踪器方法。

## 工作流程

### 1. 探索现有调用位置

在选择层级之前，找到提供者调用并回答以下问题：

- [ ] **形状？** 是聊天循环（历史+回合制）、单次完成、代理步骤，还是其他？→ 决定1级与2级。
- [ ] **框架？** 原始提供者SDK？LangChain / LangGraph？Vercel AI SDK？CrewAI？Strands？→ 决定是否适用2级提供者包。
- [ ] **提供者？** OpenAI、Anthropic、Bedrock、Gemini、Azure、自定义HTTP？→ 与下方的包可用性矩阵进行交叉验证。
- [ ] **流式传输？** 如果是，你需要TTFT追踪，这意味着即使其他部分是2级，TTFT部分也需要4级。
- [ ] **语言？** Python或Node？提供者包在两者之间的覆盖范围不同。
- [ ] **是否已使用配置？** 如果没有，请先路由到 `configs-create`——追踪需要追踪器，而追踪器是通过在 `completion_config()` / `completionConfig()` / `createModel()` 返回的配置对象上调用 `create_tracker()` / `createTracker()` 获取的。
- [ ] **当前SDK API？** 如果调用位置使用 `aiclient.config(...)` / `aiClient.config(...)` 或构造 `AIConfig(...)` / `LDAIConfig` 默认值，它位于0.20之前的表面。将迁移作为此项工作的一部分，然后添加追踪：
   - `aiclient.config(...)` → `aiclient.completion_config(...)` 用于单次/聊天，或 `aiclient.agent_config(...)` 用于代理模式（镜像调用签名）。Node使用驼峰命名法。
   - `AIConfig(...)` 默认值 → `AICompletionConfigDefault(...)` 或 `AIAgentConfigDefault(...)`（Node: `LDAICompletionConfigDefault` / `LDAIAgentConfigDefault`）。`AIConfig` 是SDK返回的基类；它不是有效的默认值构造器——带 `*Default` 的类型化变体才是。
   - 如果结果是元组解构 (`config, tracker = aiclient.config(...)`)，请删除解构——新方法返回单个配置对象。通过 `config.create_tracker()` / `aiConfig.createTracker()` 获取追踪器。
   - 对于更深层次的改写（包含硬编码模型/提示的调用位置），请将任务委托给 `migrate` 而不是在此处执行完整迁移。

### 2. 查找你的2级选项

使用此矩阵决定你的情况下是否可用2级（提供者包）。如果不可用，则降级到3级（自定义提取器）。如果形状是聊天循环，则无论如何都先跳转到1级。

| 框架 / 提供者 | Python提供者包 | Node提供者包 | 参考 |
|---|---|---|---|
| OpenAI (直接SDK) | `launchdarkly-server-sdk-ai-openai` | `@launchdarkly/server-sdk-ai-openai` | [openai-tracking.md](references/openai-tracking.md) |
| LangChain / LangGraph | `launchdarkly-server-sdk-ai-langchain` | `@launchdarkly/server-sdk-ai-langchain` | [langchain-tracking.md](references/langchain-tracking.md) |
| Vercel AI SDK | — | `@launchdarkly/server-sdk-ai-vercel` | （使用Vercel提供者文档） |
| AWS Bedrock (Converse或InvokeModel) | — (使用LangChain-aws或自定义提取器) | — (使用LangChain-aws或自定义提取器) | [bedrock-tracking.md](references/bedrock-tracking.md) |
| Anthropic直接SDK | — | — | [anthropic-tracking.md](references/anthropic-tracking.md) |
| Gemini / Google GenAI | — | — | [gemini-tracking.md](references/gemini-tracking.md) |
| Strands Agents | — (3级自定义提取器) | — (3级自定义提取器) | [strands-tracking.md](references/strands-tracking.md) |
| Cohere、Mistral、自定义HTTP | — | — | 3级自定义提取器 |
| **任何提供者，流式传输+TTFT** | — (仅4级) | `trackStreamMetricsOf` (无TTFT) + 手动TTFT | [streaming-tracking.md](references/streaming-tracking.md) |

### 3. 根据匹配的参考实现

一旦你知道了层级和提供者，打开参考文件并遵循模式。参考文件编写方式确保1级始终是第一个示例，2/3级其次，4级最后。停止于与应用程序形状匹配的第一个层级。

适用于每个层级的约束：

1. **始终在调用追踪器之前检查 `config.enabled`**。如果配置已禁用，意味着用户已将功能标记为关闭——你应该短路到应用程序使用的任何回退方案（缓存响应、错误、降级路径），而不是调用提供者。
2. **包装现有调用，不要重写它。** 2级和3级设计为在不修改提供者调用的前提下嵌入。如果你发现自己需要重写调用以适应追踪器，那么你选错了层级——应降级一级。
3. **错误在 `trackMetricsOf` 内部处理。** 包装器捕获异常，内部记录 `trackError()` 并重新抛出——不要在顶部添加 `except: tracker.trackError()`，它是无用的，并且会触发最多一次保护。1级自动处理两种路径。在4级（原始、流式、`track_duration_of`）中，调用者拥有错误追踪调用。
4. **始终在关闭前刷新。** 在关闭客户端之前调用 `ldClient.flush()`（Python: `ldclient.get().flush()`；Node: `await ldClient.flush()`）。否则，尾随事件有丢失的风险——无论是短时脚本还是长时间运行的服务。在Node中，`ldClient.close()` 返回一个Promise；等待它。

### 4. 验证

确认监控标签页填充：

- [ ] 运行一个真实请求通过已监控的路径。
- [ ] 在LaunchDarkly中打开配置→**监控**标签页。持续时间、令牌计数和生成计数应在1-2分钟内出现。
- [ ] 强制一个错误（坏API密钥、零 `max_tokens`，或其他任何错误）并确认错误计数增加。
- [ ] 如果流式传输：验证TTFT出现。如果没有，你可能用 `trackMetricsOf` 包装了流创建，但没有添加手动 `trackTimeToFirstToken` 调用——见 [streaming-tracking.md](references/streaming-tracking.md)。

## 快速参考：追踪器方法

通过配置对象上的工厂获取追踪器：`tracker = config.create_tracker()`（Python）或 `const tracker = aiConfig.createTracker()`（Node）。对每个执行调用工厂一次并重用返回的 `tracker` 对每个调用——每个工厂调用都会生成一个新的 `runId`，该ID会标记该追踪器发出的每个追踪事件，以便将同一执行的多个事件关联起来（通过导出事件/下游系统）。今天监控标签页聚合事件而不是按运行分组——`runId` 在事件导出或UI外部查询时很有用，并且是SDK最多一次保护的键值。下面的方法是原始API表面——大多数情况下你不应该单独调用它们；使用 `trackMetricsOf` 或1级管理运行器。列出这些方法是为了让你能识别现有代码中的方法，并在你确实需要4级时选择正确的方法。

| 方法（Python ↔ Node） | 层级 | 它的作用 |
|---|---|---|
| `track_metrics_of(extractor, fn)` / `trackMetricsOf(extractor, fn)` | **2 / 3** | 包装提供者调用，捕获持续时间和成功/失败，调用你的提取器获取令牌。**这是默认的通用追踪器。** |
| `track_metrics_of_async(extractor, fn)` (Python) | 2 / 3 | 上述的异步变体。 |
| `trackStreamMetricsOf(extractor, streamFn)` (Node only) | 2 / 3 | 流式变体。当提取器处理块时捕获每个块的用量。**不会**自动捕获TTFT。 |
| `track_duration(ms)` / `trackDuration(ms)` | 4 | 记录毫秒级延迟。 |
| `track_duration_of(fn)` / `trackDurationOf(fn)` | 4 | 包装可调用对象并自动记录持续时间。不捕获令牌或成功——需要与显式调用配对。 |
| `track_tokens(TokenUsage)` / `trackTokens({input, output, total})` | 4 | 记录令牌使用情况。 |
| `track_time_to_first_token(ms)` / `trackTimeToFirstToken(ms)` | 4 | 记录流式响应的TTFT。 |
| `track_success()` / `trackSuccess()` | 4 | 将生成标记为成功。监控标签页需要它来计数。 |
| `track_error()` / `trackError()` | 4 | 将生成标记为失败。不要在同一请求中同时调用 `trackSuccess()`。 |
| `track_feedback({kind})` / `trackFeedback({kind})` | 任何 | 记录来自反馈UI的点赞/点踩。独立于成功/失败路径。 |
| `track_tool_call(name)` / `trackToolCall(name)` | 任何 | 记录单个工具调用。两SDK都可用。 |
| `track_tool_calls([names])` / `trackToolCalls([names])` | 任何 | 批量变体——一次调用中记录一组工具调用。 |
| `track_judge_result(result)` / `trackJudgeResult(result)` | 任何 | 记录程序化裁判评估。`result.sampled` 指示评估是否运行。 |

## 相关技能

- `configs-create` — 如果应用程序还没有配置，这是前提条件
- `custom-metrics` — 业务指标（转化、解决、留存）叠加在此技能捕获的代理指标之上
- `online-evals` — 对采样实时请求的自动质量评分（LLM作为裁判）；与这些指标互补
- `migrate` — 硬编码到AgentControl迁移的第四阶段将任务委托给此技能
