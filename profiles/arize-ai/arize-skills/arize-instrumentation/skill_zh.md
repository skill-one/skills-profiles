# Arize 代理技能

首次为应用程序添加 **Arize AX 追踪**：**检测堆栈 → 获取匹配的集成文档 → 自动连接追踪 → 验证追踪到达。**

**本地路由。** 通过 [references/integration-routing.md](references/integration-routing.md) 将检测到的堆栈映射到单个文档页面（对于追踪集成而言是详尽的），并获取 **仅该页面**。当应用程序使用代理框架时，基于 **框架** 而不是它包装的提供者 SDK 进行路由——框架应用程序中的 `openai`/`anthropic` 简单导入不是集成目标；只有在应用程序直接调用提供者 SDK 而没有框架参与时才路由到提供者页面。如果堆栈在那里没有列出，则没有专门的集成——使用 [手动代理](https://arize.com/docs/ax/instrument/manual-instrumentation)。切勿批量获取 [PROMPT.md](https://arize.com/docs/PROMPT.md)/[llms.txt](https://arize.com/docs/llms.txt) 聚合。

**规则：** 修改前检查；追踪是可叠加的，永远不要修改业务逻辑；遵循现有风格；代码中不包含密钥，**永远不要要求用户将密钥（API 密钥、令牌）粘贴到聊天中**——仅引用 `ARIZE_API_KEY`/`ARIZE_SPACE_ID` 环境变量，由用户在其自己的 `.env`/shell 中设置；保留或请求应用程序的 Arize 区域/导出端点，而不是假设美国——参见 [references/regions-and-endpoints.md](references/regions-and-endpoints.md)；在持久本地状态（`ax` 配置文件、`.zshrc`、环境变量）之前询问——参见 [references/ax-profiles.md](references/ax-profiles.md)。

## 第一阶段：分析（只读——无代码/文件）

从清单和导入中检测：语言、包管理器、LLM 提供者、框架、现有追踪（`TracerProvider`、`register()`、`ARIZE_*`/`OTEL_*`、Datadog/Honeycomb）、现有 Arize 端点/区域配置（`ARIZE_COLLECTOR_ENDPOINT`、代码中的 Arize 端点选项，或确认目标 Arize 的 `OTEL_EXPORTER_OTLP_ENDPOINT`），以及应用程序是否运行工具/代理循环（手动 CHAIN/TOOL 追踪仅在匹配的框架代理器尚未覆盖它们时才决定——在第二阶段决定）。**首先确认范围**——单体存储库、多个服务或多个框架在触摸任何东西之前需要一个“哪个？”的问题；不要为用户选择。

输出简短摘要（堆栈、建议的集成、现有追踪、范围）。如果目标明确且用户要求立即代理，则继续；如果模糊或请求仅分析，则停止并确认。

## 第二阶段：实现（目标确认后）

1. **获取匹配的集成文档** 并逐字遵循其安装 + 连接说明。
2. **安装** 使用检测到的包管理器，在编写代码之前——确切的包来自匹配的文档。Python 基础：`arize-otel`（最新 **0.13.0**，在 PyPI 上验证）+ `openinference-instrumentation-{name}`（包连字符，导入下划线）。TS/JS：`@opentelemetry/sdk-trace-node` + 匹配的 `@arizeai/openinference-*`（或第三方导出器，例如 Mastra 的 `@mastra/arize`）。Go 没有集成文档——参见 [references/go.md](references/go.md) 了解安装、连接、刷新和手动追踪。
3. **凭证和区域**——应用程序需要一个 API 密钥 + Space + 导出端点/区域。仅检查目标应用程序自己的配置；切勿扫描兄弟存储库/shell 文件，暴露密钥，或接受粘贴的密钥。参见 [references/credentials-and-config.md](references/credentials-and-config.md)、[references/regions-and-endpoints.md](references/regions-and-endpoints.md) 和 [references/ax-profiles.md](references/ax-profiles.md)。
4. **集中** 初始化到一个模块中，**在**任何 LLM 客户端创建之前。现有 OTel → 将 Arize 添加为 *附加* 导出器；不要替换它。

**自动与手动：** 优先使用自动代理器——不要手动创建它已经覆盖的追踪（重复追踪，偏离 semconv）。仅当代理器看不到逻辑或堆栈完全没有代理器时才添加手动追踪。**当应用程序直接调用提供者 SDK 时，OpenAI 和 Anthropic SDK 代理器捕获 LLM 调用——包括模型的工具调用请求（名称 + 参数）——但不捕获工具的执行、其返回值或代理/链边界。原始 SDK 应用程序与其自己的工具调用循环必须为每次执行添加一个 TOOL 追踪（以捕获结果）并添加一个 CHAIN（或 AGENT）追踪以分组该回合**，否则这些永远不会出现——在函数存在的地方使用 `@tracer.tool`/`@tracer.chain` 装饰器（它们自动设置类型、元数据和状态）；仅在无法装饰的函数中手动创建追踪。某些代理框架通过自己的客户端层驱动模型并发出自己的 OpenTelemetry 追踪；对于这些，提供者代理器捕获**什么都没有**，因此通过框架的集成页面而不是提供者 SDK 进行代理。框架代理器（LangChain/LangGraph/OpenAI Agents SDK）*通常*覆盖工具和链——在匹配的文档中验证之前不要跳过手动追踪。保留 `register()`/`arize-otel-go` 用于设置；参见 [references/manual-spans.md](references/manual-spans.md) 和 [手动代理](https://arize.com/docs/ax/instrument/manual-instrumentation)。

**跨切（每个堆栈）：**
- **必须提供项目名称**——缺失它 → HTTP 500（仅 `service.name` 失败）。作为资源属性设置：Python `register(project_name=…)`；TS `SEMRESATTRS_PROJECT_NAME`/`model_id`；Go `Options{ProjectName}` 或 `openinference.project.name`。
- **不要手动创建 `TracerProvider`/导出器**——使用 `register()`/`arize-otel-go`；仅在集成现有提供器时使用原始 OTel。
- **顺序：** 注册追踪器 → 代理器 → 客户端。
- **区域：** 不要假设美国。保留 `ARIZE_COLLECTOR_ENDPOINT` 或已确认目标 Arize 的端点。通用的 `OTEL_EXPORTER_OTLP_ENDPOINT` 可能属于现有的非 Arize 导出器；单独保留该导出器并请求 Arize SaaS 区域，而不是盲目地重用它。参见 [references/regions-and-endpoints.md](references/regions-and-endpoints.md)。
- **优先使用 `@tracer.*` 装饰器而不是手动创建的追踪**——它们自动设置类型、`input.value`/`output.value`、完整的 TOOL 元数据和终端状态，因此它们不能发出手动创建的追踪所执行的 `UNSET`/不完整的追踪。装饰器在函数*定义*上，因此动态分发不是手动创建的原因。参见 [references/manual-spans.md](references/manual-spans.md)。
- **手动创建的追踪必须在退出前设置：** `openinference.span.kind`、`input.value`/`output.value`，以及对于 TOOL 追踪所有 `tool.name`/`tool.description`/`tool.parameters`。**最遗漏的行：** `start_as_current_span` 记录抛出的异常为 `ERROR` 但**永远不会设置 `OK`**——因此请在成功路径上添加 `span.set_status(Status(StatusCode.OK))` 或追踪导出 `UNSET` 并失败评分。参见 [references/manual-spans.md](references/manual-spans.md)。
- **退出前刷新**（CLI/脚本/笔记本）或异步导出丢失：Python `force_flush()`+`shutdown()`，TS `shutdown()`，Go `defer tp.Shutdown(ctx)`（在追踪中永远不会 `log.Fatalf`/`os.Exit`）。参见 [references/session-tracking.md](references/session-tracking.md)。
- **会话：** 对于明显的多回合交互（例如多回合聊天机器人）或当用户请求时，添加 `session.id` 以使回合组合成一个对话——参见 [references/session-tracking.md](references/session-tracking.md)。
- **永远不要静默覆盖**应用程序的项目/空间/ID/端点——暴露不匹配。

## 验证

仅在以下情况下完成：应用程序构建/类型检查、启动时包含追踪、发出 ≥1 个真实请求，并您在 Arize 中确认追踪**或**给出精确的应用程序与 Arize 阻塞器。触发 LLM 调用，然后使用 **`arize-trace`** 技能确认追踪（类型、`input.value`/`output.value`、父子关系；如果工具运行则 CHAIN+TOOL）。没有追踪 → 检查 `ARIZE_SPACE_ID`/`ARIZE_API_KEY`、初始化顺序、配置的收集器端点/区域、导出器日志（`GRPC_VERBOSITY=debug`）；常见原因：错误的区域端点、缺少项目名称（500）、未刷新的短生命周期进程，或导出/验证**凭证上下文不匹配**（报告它，不要重写配置——[references/credentials-and-config.md](references/credentials-and-config.md)）。对于确定的追踪查找序列、阻塞器分类和到达后的冒烟检查，请遵循 [references/verification.md](references/verification.md)。

## 确认追踪后

发出里程碑（安装 → 连接 → 运行 → 导出 → 验证）；标记恢复的错误为已解决；结束将完成的与阻塞器区分开。然后简要提供下一步：**`arize-trace`**（检查/调试）、**`arize-dataset`**（整理）、**`arize-evaluator`**（评估）、**`arize-experiment`**（比较）、**`arize-prompt-optimization`**（改进提示）。质量问题 → **`arize-trace`** 首先进行。

## 参考

[integration-routing](references/integration-routing.md)（路由器） · [credentials-and-config](references/credentials-and-config.md) · [regions-and-endpoints](references/regions-and-endpoints.md) · [ax-profiles](references/ax-profiles.md) · [manual-spans](references/manual-spans.md) · [go](references/go.md)（Go——没有文档页面存在） · [session-tracking](references/session-tracking.md) · [verification](references/verification.md) · [tracing-assistant-mcp](references/tracing-assistant-mcp.md)。
