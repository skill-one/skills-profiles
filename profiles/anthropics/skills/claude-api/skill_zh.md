# 使用 Claude 构建基于 LLM 的应用程序

这项技能将帮助您使用 Claude 构建基于 LLM 的应用程序。根据您的需求选择合适的界面，检测项目语言，然后阅读相关的语言特定文档。

## 开始前

扫描目标文件（如果没有目标文件，则扫描提示和项目）以查找非 Anthropic 提供商标记 - `import openai`，`from openai`，`langchain_openai`，`OpenAI(`，`gpt-4`，`gpt-5`，文件名如 `agent-openai.py` 或 `*-generic.py`，或任何明确指示保持代码提供者中立的建议。如果您发现任何，请停止并告知用户此技能生成 Claude/Anthropic SDK 代码；询问他们是否希望将文件切换到 Claude 或希望获得非 Claude 实现。不要用 Anthropic SDK 调用编辑非 Anthropic 文件。（例外：`prompt-audit` 子命令是非交互式的，不会在此停止 - 它会在其报告的声明假设中记录非 Anthropic 提供商标记，并且永远不会建议将非 Anthropic 文件切换到 Anthropic SDK。）

## 输出要求

当用户要求您添加、修改或实现 Claude 功能时，您的代码必须通过以下方式之一调用 Claude：

1. **项目的官方 Anthropic SDK**（语言为 `anthropic`，`@anthropic-ai/sdk`，`com.anthropic.*` 等）。只要项目支持 SDK 存在，这就是默认选项。
2. **原始 HTTP** (`curl`，`requests`，`fetch`，`httpx` 等） - 仅当用户明确要求 cURL/REST/原始 HTTP，项目是 shell/cURL 项目，或语言没有官方 SDK 时使用。

永远不要混合使用这两种方式 - 不要因为在 Python 或 TypeScript 项目中感觉更轻而使用 `requests`/`fetch`。永远不要回退到 OpenAI 兼容的遮蔽层。

**永远不要猜测 SDK 使用情况。** 函数名、类名、命名空间、方法签名和导入路径必须来自明确的文档 - 要么是此技能中的 `{lang}/` 文件，要么是官方 SDK 存储库或文档链接（列在 `shared/live-sources.md` 中）。如果您需要的绑定在技能文件中没有明确记录，请在编写代码前从 `shared/live-sources.md` 中 WebFetch 相关的 SDK 存储库。不要从 cURL 形状或从另一种语言的 SDK 推断 Ruby/Java/Go/PHP/C# API。

**如果 WebFetch 或存储库访问失败**（网络受限、超时、克隆被阻止）：不要不断重试 - 从 `{lang}/` 文件中的模式和命名空间/包表编写代码，运行编译器或解释器，并在错误输出上进行迭代。对于静态类型 SDK（C#、Java、Go），针对本地错误的编译修复循环比被阻止的网络研究更快地达到工作代码。

## 默认值

除非用户另有要求：

对于 Claude 模型版本，请使用 Claude Opus 5，您可以通过确切的模型字符串 `claude-opus-5` 访问它。对于任何稍微复杂的东西，请默认使用自适应思考（`thinking: {type: "adaptive"}`）。最后，对于可能涉及长输入、长输出或高 `max_tokens` 的任何请求，请默认使用流式传输 - 它可以防止达到请求超时。如果您不需要处理单个流事件，请使用 SDK 的 `.get_final_message()` / `.finalMessage()` 帮助程序获取完整响应

## 警告：API 漂移 - 您的训练先验可能已过时

在 2025-2026 年，几个常见的 Claude API 形状发生了变化。如果您在训练中记住了某种模式，请在编写之前将其与此技能中的 `{lang}/` 文件进行验证 - 以下行是最常见的漂移点：

| 区域 | 过时的先验 | 当前 API |
|---|---|---|
| 扩展思考 | `thinking: {type: "enabled", budget_tokens: N}` | 在 Claude 4.6+ 模型上：`thinking: {type: "adaptive"}`。`budget_tokens` 在 Opus 4.6 / Sonnet 4.6 上已弃用，并在 Fable 5/5.1 / Sonnet 5 / Opus 5 / 4.8 / 4.7 上被 400 拒绝。4.6 之前的模型仍然使用 `budget_tokens`。 |
| 网络搜索 / 网络获取工具类型 | `web_search_20250305`，`web_fetch_20250910` | `web_search_20260209`，`web_fetch_20260209`（动态过滤）在 Opus 5/4.8/4.7/4.6、Sonnet 5 和 Sonnet 4.6 上。旧模型保留基本变体；在 Vertex AI 上只有基本的 `web_search_20250305` 可用（网络获取在 Vertex 上不可用） - 请参阅下方的服务器工具 QR。 |
| PHP 参数名 | 作为命名参数的蛇形线名称（`max_tokens`） | 顶级命名参数是驼峰式（`maxTokens`）。嵌套数组键因功能而异（例如 `'taskBudget'`，`'skillID'`，`'mcp_server_name'`） - 从文档示例中复制确切的键；不要批量转换。 |
| 管理代理凭证 | 通过自定义工具在主机端保持密钥（在密钥库交付之前是唯一选项） | 密钥库 `environment_variable` 凭证 - 由 Anthropic 存储的，在出口时替换，永远不会在沙盒中可见（`shared/managed-agents-tools.md` -> 密钥库）。主机端自定义工具仍然是自托管沙盒的回退选项。 |
| 文件 API / 技能 | `client.beta.files.*` / `client.beta.skills.*` 与 beta `files-api-2025-04-14` / `skills-2025-10-02` | 已退出 beta：`client.files.*` / `client.skills.*`，没有 beta 标头。在当前 SDK 中，`client.beta.files` / `client.beta.skills` 从以前的版本有破坏性形状变化，匹配稳定的命名空间 - 根据 `shared/live-sources.md` -> 文件 API / 技能指南进行迁移。 |

此技能中的 `{lang}/` 文件对回忆的模式具有权威性。

---

## 子命令

如果此提示底部的用户请求是一个纯子命令字符串（没有散文），请搜索此文档中的每个 **子命令** 表 - 包括任何附加部分的表 - 并直接遵循匹配的 Action 列。这允许用户通过 `/claude-api <subcommand>` 调用特定流程。如果文档中没有匹配的表，请将请求视为正常散文。

| 子命令 | 操作 |
|---|---|
| `migrate` | 将现有的 Claude API 代码迁移到更新的模型。**立即阅读 `shared/model-migration.md`** 并按顺序遵循它：步骤 0（确认范围 - 在进行任何编辑之前询问哪些文件/目录），步骤 1（对每个文件进行分类），然后针对每个目标的破坏性更改部分。不要总结指南 - 执行它。如果用户没有指定目标模型，请在同一轮中询问要迁移到哪个模型（与范围问题一起）。在应用针对每个目标的更改后，根据 `shared/prompt-audit.md` 审计范围内的提示文本、工具描述和请求代码 - 为源模型编写的提示是每次迁移的一部分，并且它不会宣布自己。 |
| `prompt-audit` | 审计现有的提示、技能和工具描述，以查找为旧模型编写的过时模式（“垃圾”）。**立即阅读 `shared/prompt-audit.md`** 并按顺序遵循它：步骤 0（从请求和存储库建立范围和目标模型 - 在报告中声明假设，不要停止询问），清单，来源，然后模式扫描。提供完整的交付成果 - 审计报告（带有 `file:line`、模式、为什么它对目标模型已过时、置信度）和建议的 diff - 不要暂停以确认；仅当请求明确要求时才应用编辑。不要总结指南 - 执行它。 |
| `upgrade` | 升级项目的 Anthropic SDK 跨主要版本 - 目前是 Python SDK，`anthropic` 0.x -> 1.x。尾随词可以命名语言和/或范围（`upgrade python`，`upgrade python sdk src/`）。**立即阅读 `python/claude-api/sdk-upgrade.md`** 并按顺序遵循它：步骤 0（确认范围，然后建立当前和目标版本 - 必须在您编写固定之前存在发布的 1.x），步骤 1 清单，每个编号部分，然后验证和报告。不要总结指南 - 执行它。如果检测到的或命名的语言没有此技能中的 `sdk-upgrade.md`，请说明尚未为该 SDK 捆绑主要版本升级指南，并指向该 SDK 的 CHANGELOG（存储库在 `shared/live-sources.md` 中）；不要从 Python 指南中编造一个。这不是模型迁移 - 要将代码迁移到更新的 Claude 模型，请使用 `migrate`。 |
| `cost-optimize` | 减少现有 Claude API 代码的运行成本，同时不牺牲输出质量。**立即阅读 `shared/cost-optimization.md`** 并按顺序遵循它：步骤 0（建立范围、质量标准和基线），令牌配置 - 当用户有 Admin API 密钥时通过使用和成本 Admin API 进行测量，当它有这些时通过应用程序自己的 `response.usage` 日志进行测量（询问），否则从代码中估计 - 然后是一个按节省排名的短名单（以美元、账单的百分比或相对桶为单位，取决于您拥有哪些数据源），免费收益（缓存、输入令牌卫生、循环卫生、输出令牌卫生、批处理）在权衡（预算、工作、模型选择、多模型）；任何赢得位置的杠杆都成为其自己的 diff - 默认情况下建议，在用户请求并批准时应用并测量它所触及的流量所覆盖的评估 - 并且“不推荐更改”是有效结果。两个基本原则：任何使用模型的运行都会花费真实钱，因此请先获得用户的批准；当杠杆的上下文缺失时，与用户交互式地处理它 - 此工作流程不期望一键完成审计。不要总结指南 - 执行它；向用户展示配置文件和排名计划是执行它的一部分。 |

---

## 语言检测

在阅读代码示例之前，确定用户正在使用哪种语言（例外：对于 `prompt-audit` 子命令，跳过此部分的询问步骤 - 审计是非交互式的，其清单是语言无关的；当无法推断语言时，在不询问的情况下继续并在报告中声明假设）：

1. **查看项目文件** 以推断语言：

   - `*.py`，`requirements.txt`，`pyproject.toml`，`setup.py`，`Pipfile` -> **Python** - 从 `python/` 阅读
   - `*.ts`，`*.tsx`，`package.json`，`tsconfig.json` -> **TypeScript** - 从 `typescript/` 阅读
   - `*.js`，`*.jsx`（没有 `.ts` 文件）-> **TypeScript** - JS 使用相同的 SDK，从 `typescript/` 阅读
   - `*.java`，`pom.xml`，`build.gradle` -> **Java** - 从 `java/` 阅读
   - `*.kt`，`*.kts`，`build.gradle.kts` -> **Java** - Kotlin 使用 Java SDK，从 `java/` 阅读
   - `*.scala`，`build.sbt` -> **Java** - Scala 使用 Java SDK，从 `java/` 阅读
   - `*.go`，`go.mod` -> **Go** - 从 `go/` 阅读
   - `*.rb`，`Gemfile` -> **Ruby** - 从 `ruby/` 阅读
   - `*.cs`，`*.csproj` -> **C#** - 从 `csharp/` 阅读
   - `*.php`，`composer.json` -> **PHP** - 从 `php/` 阅读

2. **如果检测到多种语言**（例如，Python 和 TypeScript 文件）：

   - 检查用户当前文件或问题与哪种语言相关
   - 如果仍然不明确，询问：“我检测到 Python 和 TypeScript 文件。您使用哪种语言进行 Claude API 集成？”

3. **如果无法推断语言**（空项目、没有源文件或不受支持的语言）：

   - 使用 AskUserQuestion 带选项：Python、TypeScript、Java、Go、Ruby、cURL/原始 HTTP、C#、PHP
   - 如果 AskUserQuestion 不可用，默认为 Python 示例并注明：“显示 Python 示例。如果您需要其他语言，请告诉我。”

4. **如果检测到不受支持的语言**（Rust、Swift、C++、Elixir 等）：

   - 建议从 `curl/` 获取 cURL/原始 HTTP 示例，并注明社区 SDK 可能存在
   - 提供显示 Python 或 TypeScript 示例作为参考实现的选项

5. **如果用户需要 cURL/原始 HTTP 示例**，从 `curl/` 阅读。

### 语言特定功能支持

上述每个 SDK 语言都支持 beta 工具运行器和管理代理（beta）- Python（`@beta_tool` 装饰器）、TypeScript（`betaZodTool` + Zod）、Java（注解类）、Go（`BetaToolRunner` 在 `toolrunner` 包中）、Ruby（`BaseTool` + `tool_runner`）、C#（`BetaToolRunner` + 原始 JSON 模式）、PHP（`BetaRunnableTool` + `toolRunner()`）；代码入口点在下面的工具使用模式快速参考中。cURL 是原始 HTTP（没有 SDK 功能）并支持管理代理。

> **管理代理代码示例**：请参阅 `## Managed Agents (Beta)` 部分中的阅读指南。

---

## 我应该使用哪个界面？

> **从简单开始。** 默认使用满足您需求的最低级。单个 API 调用和工作流处理大多数用例 - 只有当任务确实需要开放式、模型驱动的工具使用时才使用代理。 “简单”意味着您拥有的代码最少：对于托管的、计划的或内存回代的代理，管理代理通常是简单的选项（没有循环代码、没有状态文件、没有调度器），尽管它是一个更大的平台。

| 用例                                        | 级别            | 推荐界面       | 原因                                                          |
| ----------------------------------------------- | --------------- | ------------------------- | ------------------------------------------------------------ |
| 分类、摘要、提取、Q&A  | 单个 LLM 调用 | **Claude API**            | 一个请求，一个响应                                    |
| 批量处理或嵌入                  | 单个 LLM 调用 | **Claude API**            | 特殊化端点                                        |
| 具有代码控制逻辑的多步管道 | 工作流        | **Claude API + 工具使用** | 您编排循环                                     |
| 带您自己工具的自定义代理                | 代理           | **Claude API + 工具使用** | 最大灵活性                                          |
| 服务器管理的有状态代理与工作区    | 代理           | **管理代理**        | Anthropic 运行循环并托管工具执行沙盒 |
| 持久化、版本化代理配置              | 代理           | **管理代理**        | 代理是存储对象；会话针对一个版本进行固定         |
| 长运行多轮代理与文件挂载  | 代理           | **管理代理**        | 每个会话容器，SSE 事件流，Skills + MCP       |
| 在计划上运行的代理（cron，“每晚”） | 代理       | **管理代理** - 计划部署 | 部署自动触发会话；没有客户端调度器 |

> **注意：** 当您希望 Anthropic 运行代理循环 *并* 托管工具执行的容器时，管理代理是正确的选择 - 文件操作、bash、代码执行都在每个会话的工作区中运行。如果您想自己托管计算或运行自己的自定义工具运行时，Claude API + 工具使用是正确的选择 - 使用工具运行器进行 agentic 循环 - 它的每轮钩子仍然为您提供审批门、日志记录、错误拦截和条件执行（见 `shared/tool-use-concepts.md`） - 或者在您想自己拥有整个循环时使用手动循环。

> **云提供者访问。** **AWS 上的 Claude 平台** 由 Anthropic 运营，具有同一天的 API 对等性 - 请参阅 `shared/claude-platform-on-aws.md` 进行客户端设置。对于 **AWS 上的 Claude 平台**、**Amazon Bedrock**、**Google Vertex AI** 和 **Microsoft Foundry** 的每个功能可用性，请参阅 `shared/platform-availability.md` - 该表是此技能中唯一的真相来源；不要从任何其他地方推断可用性。

### 构建代理：四种方法

一旦您确定实际上需要代理（开放式、模型驱动的工具使用），就有四种不同的方法来构建它。两个独立的问题将它们分开：**谁提供支架**（代理循环 + 上下文管理）和**谁提供部署**（代理运行的 infra）。工具运行器和 Claude 代理 SDK 都只提供 *支架* - 您仍然需要自己托管和部署它们 - 这就是为什么它们很容易混淆。管理代理（CMA）是唯一提供 **支架 *和* 管理部署** 的选项；手动循环提供两者都不提供。

| # | 方法 | 您编写 | 托管与部署 | 可用工具 | 使用场景 |
|---|------|--------|------------|----------|----------|
| 1 | **Claude API - 手动循环** | 您自己编写 `while stop_reason == "tool_use"` 循环 | 您构建托管工具；您部署 | 仅您定义的工具 | 您想拥有整个循环 - 没有依赖beta，或控制流程不适合工具运行器每回合钩子 |
| 2 | **Claude API - 工具运行器** (`client.beta.messages.tool_runner` + `@beta_tool` / `betaZodTool`) | 仅工具函数 | SDK提供循环（仅托管）；您部署 | 仅您定义的工具 | 无需手动编写循环的自定义工具代理（大多数情况）。每回合钩子仍然提供审批门、错误拦截、结果修改（例如 `cache_control`）、重试、流式传输和压缩 |
| 3 | **托管代理**（REST，beta） | 代理配置 + 您的工具结果 | Anthropic提供托管工具并部署每会话沙盒（托管+部署） | Anthropic托管的沙盒（bash，文件，代码执行）+ Skills/MCP + 您的工具 | 您希望Anthropic运行循环并部署每会话工作区；持久化/版本化配置；长时间运行的会话 |
| 4 | **Claude Agent SDK** - *独立产品* (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) | 一个提示 + 选项 | SDK提供Claude Code托管工具（仅托管）；您部署 | 内置的Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch + MCP + 子代理 | 您希望在自己的基础设施上运行包含所有功能的编码/文件系统代理 |

托管/部署分离是关键思维模型：选项1、2和4都将部署留给您；只有选项3（CMA）添加了托管部署。选项1-3是此技能生成的；选项4是具有自己文档的不同库 - 请参阅下文的消除歧义。

> **工具运行器 != Claude Agent SDK。** 这两个听起来相似，但它们是不同的包：
> - **工具运行器** 是Anthropic常规API SDK（`anthropic` / `@anthropic-ai/sdk`）的一部分，通过 `client.beta.messages.tool_runner` 访问。它自动化了请求 -> 执行 -> 循环周期 *对于您定义的工具*。没有内置工具，没有文件系统访问，没有沙盒 - 您提供每个工具并托管计算。它是上面选项2，`POST /v1/messages` 的一个薄辅助工具。
> - **Claude Agent SDK** (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) 是Claude Code打包为库。它提供内置工具（文件读写编辑、bash、grep、网络搜索）、完整的代理循环、上下文管理、钩子、子代理、权限和会话。您调用 `query(prompt, options)` 并它驱动一切。

两者都是 **仅托管 - 您托管和部署它们。** 区别在于托管的范围：工具运行器循环遍历您 *定义* 的工具（使用每回合钩子进行审批、拦截、结果修改和重试 - 但没有内置工具）；Agent SDK 是带有内置工具的完整Claude Code托管。两者都不提供托管部署 - 这是 **托管代理（CMA）** 添加的（Anthropic托管循环和每会话沙盒）。

**此技能涵盖Claude API和托管代理（选项1-3）；它不会生成Claude Agent SDK代码。** 如果用户实际上需要Claude Agent SDK，请指向其文档（`code.claude.com/docs/en/agent-sdk`） - 不要用API工具运行器替代它，反之亦然。

### 我是否应该构建一个代理？

在选择代理层之前，检查所有四个标准：

- **复杂性** - 任务是多步骤且难以事先完全指定吗？（例如，“将设计文档转换为PR”与“从PDF中提取标题”）
- **价值** - 结果是否值得更高的成本和延迟？
- **可行性** - Claude是否擅长这项任务类型？
- **错误成本** - 错误是否可以被捕获和恢复？（测试、审查、回滚）

如果对这些问题的回答是“否”，请保持在更简单的层（单个调用或工作流）。

---

## 架构

所有内容都通过 `POST /v1/messages` 进行。工具和输出约束是此单个端点的功能 - 不是单独的API。

**用户定义的工具** - 您定义工具（通过装饰器、Zod模式或原始JSON），SDK的工具运行器处理调用API、执行您的函数，并循环直到Claude完成。对于完全控制，您可以手动编写循环。

**服务器端工具** - Anthropic托管的在Anthropic基础设施上运行的工具。代码执行完全在服务器端（在 `tools` 中声明，Claude自动运行代码）。计算机使用可以是服务器托管或自托管。

**结构化输出** - 限制消息API响应格式（`output_config.format`）和/或工具参数验证（`strict: true`）。推荐的方法是 `client.messages.parse()`，它自动根据您的模式验证响应。注意：旧的 `output_format` 参数已弃用；在 `messages.create()` 上使用 `output_config: {format: {...}}`。

**支持端点** - 批次（`POST /v1/messages/batches`）、文件（`POST /v1/files`）、令牌计数（`POST /v1/messages/count_tokens` - 见 `shared/token-counting.md`）和模型（`GET /v1/models`，`GET /v1/models/{id}` - 活动能力/上下文窗口发现）为消息API请求提供输入或支持。

---

## 当前模型（缓存：2026-06-24）

| 模型             | 模型ID            | 上下文        | 输入 $/1M | 输出 $/1M |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
| Claude Fable 5.1    | `claude-fable-5-1`      | 1M             | $10.00     | $50.00      |
| Claude Mythos 5.1 (仅限Project Glasswing) | `claude-mythos-5-1` | 1M | $10.00     | $50.00      |
| Claude Fable 5 | `claude-fable-5` | 1M             | $10.00     | $50.00      |
| Claude Opus 5     | `claude-opus-5`       | 1M             | $5.00      | $25.00      |
| Claude Opus 4.8 | `claude-opus-4-8`  | 1M             | $5.00      | $25.00      |
| Claude Opus 4.7   | `claude-opus-4-7`   | 1M             | $5.00      | $25.00      |
| Claude Opus 4.6   | `claude-opus-4-6`   | 1M             | $5.00      | $25.00      |
| Claude Sonnet 5   | `claude-sonnet-5`   | 1M             | $2.00      | $10.00      |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M             | $3.00      | $15.00      |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00      | $5.00       |

**合作伙伴定价：** 上面的价格是Anthropic第一方API费率 - 它们也适用于Microsoft Foundry上的Claude，通过Microsoft Marketplace以标准API费率计费。Claude在Amazon Bedrock和Vertex AI上由合作伙伴运营，具有不同的定价 - 请参阅 [Bedrock](https://aws.amazon.com/bedrock/pricing/) 或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/pricing#claude-models)。对于WebFetch，使用 `shared/live-sources.md` 中的定价行。

**始终使用 `claude-opus-5`，除非用户明确指定了不同的模型。** 这是不容商量的。不要使用 `claude-sonnet-5`、`claude-sonnet-4-6` 或任何其他模型，除非用户字面意思是“使用sonnet”或“使用haiku”。永远不要因为成本而降级 - 这是用户的决定，不是您的。仅在用户明确要求Claude Fable 5.1、“fable”或Anthropic的最强大模型时使用 `claude-fable-5-1` - 它与Opus系列具有不同的API行为（见下文）和超过Opus级的定价。**仅使用表格中的确切模型ID字符串 - 它们是完整的，不要添加日期后缀**（`claude-sonnet-4-6`，不要 `claude-sonnet-4-6-20251114` 或任何其他您从训练数据中回忆起的日期后缀变体）。如果用户请求表格中未列出的旧模型（例如，“opus 4.5”、“sonnet 3.7”），请阅读 `shared/models.md` 以获取确切ID - 不要自己构造一个。

### Claude Fable 5.1 (`claude-fable-5-1`) - 最广泛发布的强大模型

Claude Fable 5.1是Anthropic最广泛发布的强大模型，用于最苛刻的推理和长视距代理工作；下面的一切也适用于 **Claude Mythos 5.1** (`claude-mythos-5-1`，Project Glasswing - 相同的能力、定价和API表面；它运行依赖于访问计划的保护措施，因此下文的 `refusal` 处理也适用于那里；Claude Mythos 5的继任者，它不运行安全分类器）。1M上下文窗口（最大值也是默认值），128K最大输出。与Opus级的关键API差异，见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 的详细信息：

- **思考始终开启** - 完全省略 `thinking` 参数（或发送 `{type: "adaptive"}`）。任何其他显式配置都会被拒绝：`{type: "disabled"}` 和 `{type: "enabled", budget_tokens: N}` 都返回400。使用 `output_config.effort` 控制深度（支持 `low` 通过 `xhigh` 和 `max`）。
- **原始思维链永远不会返回** - 响应包含常规的 `thinking` 块（不是 `redacted_thinking`）：`display: "summarized"` 返回可读的摘要，`"omitted"`（默认值）将 `thinking` 字段留为空字符串。重播规则：在相同模型上不变地传递思维块；其他模型静默地丢弃它们（未计费 - 没有可剥离的；Claude Mythos 5.1相反读取它们）；详细信息在 `shared/model-migration.md`。
- **分词器** - 与Opus 4.8相同（与Opus 4.7一起引入）。从Opus 4.7/4.8迁移时，令牌计数大致不变；每令牌定价不同。从Opus 4.6、Sonnet、Haiku或更旧的模型迁移，使用 `count_tokens` 重新基线（Opus 4.7分词器使用 ~1×-1.35×那么多令牌）。
- **`refusal` 停止原因 - 处理它，并默认选择回退** - 安全分类器可能会拒绝请求（HTTP 200，`stop_reason: "refusal"`，带有 `stop_details` 类别）；在读取 `content` 之前始终检查 `stop_reason`。**当您编写 `claude-fable-5-1` 或 `claude-opus-5` 代码时，默认包含服务器端 `fallbacks` 参数。** 最简单形式：`betas: ["server-side-fallback-2026-07-01"]` + `fallbacks: "default"`，它按拒绝类别路由，因此您永远不会维护模型列表。（旧数组形式 - `betas: ["server-side-fallback-2026-06-01"]` + `fallbacks: [{"model": "claude-opus-4-8"}]` - 仍然有效；Claude API 和 Claude Platform on AWS - 在 Bedrock、Vertex 和 Foundry 上，使用 SDK 的客户端 `BetaRefusalFallbackMiddleware` + `BetaFallbackState`）。告诉用户您已启用它；仅在它们拒绝时才放弃。完整语义（计费、中途拒绝、信用重新定价）在 `shared/model-migration.md` -> refusal 部分。**多语言代码示例在 `{lang}/claude-api/README.md` § Refusal Fallbacks 仅涵盖数组形式** - 对于 `"default"` 模式，遵循 `shared/model-migration.md` -> Migrating to Claude Opus 5 中的原始HTTP形状，并将 `fallbacks: [{...}]` 交换为 `fallbacks: "default"` 加上 `-2026-07-01` 标头；请求的其余部分保持不变。
- **没有助手预填充** - 与4.6+系列相同。
- **需要30天数据保留** - Claude Fable 5.1在零数据保留下不可用，除非Anthropic明确授权；来自不满足保留要求的组织的请求返回 `400 invalid_request_error`。
- **更长的回合，不同的提示** - 在硬任务上的单个请求可以运行多分钟（计划超时/流式传输/进度UX）；努力扫描应包括低/中用于常规工作；为先前模型编写的提示通常过于具体，会降低输出质量。见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 -> Behavioral shifts (prompt-tunable) 的推荐提示片段。
- **Claude Fable 5 (`claude-fable-5`，仍在服务）的继任者，在同一级别，相同每令牌价格。** 与Claude Fable 5具有相同的表面，但有三个破坏性更改 - 强制工具使用（`tool_choice` `any` / `tool`）返回400（使用 `auto` + 提示指令，`strict: true` 用于模式有效的参数，或结构化输出）；思维块绑定到产生模型（其他模型静默丢弃它们，未计费）；编辑早期回合使思维块无效（“保留思维”；在2026-08-31之后创建的新帐户在编辑历史上返回400；较新模型对所有人强制执行此规则 - 使每个托管为只读并运行三步检查；选择控制按平台划分，见 `shared/platform-availability.md`）- 加上每消息 `effort`（beta `mid-conversation-output-config-2026-07-01`，Claude Opus 5上也有），回合范围的 `clear_at: "next_user_message"` 系统消息（beta），`thinking.display: "updates"` 进度笔记（beta，所有平台），缓存读取 $0.25/MTok（无论Claude Mythos 5.1是否共享该费率，在发布时都是开放的），内容来源。覆盖模型 - ZDR组织像Claude Fable 5一样获得 `400 invalid_request_error`（ZDR仅如果Anthropic明确授权）；没有优先级层。与Claude Fable 5相同的分词器。见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 from Claude Fable 5。

如果上面任何模型字符串看起来不熟悉，那只是意味着它们是在您的训练数据截止日期之后发布的 - 它们是真实模型。

**实时能力查找：** 上面的表格是缓存的。当用户问“X的上下文窗口是什么”、“X是否支持视觉/思考/努力”或“哪些模型支持Y”时，查询模型API（`client.models.retrieve(id)` / `client.models.list()`） - 见 `shared/models.md` 以获取字段参考和能力过滤示例。

---

## 身份验证（快速参考）

**未设置的 `ANTHROPIC_API_KEY` 并不意味着没有凭证。** SDK和 `ant` CLI按以下顺序解析凭证（第一个匹配者胜出）：`ANTHROPIC_API_KEY` -> `ANTHROPIC_AUTH_TOKEN` -> 从 `ant auth login` 选择的或活动的OAuth配置文件 -> Workload Identity Federation环境变量 -> 磁盘上的默认配置文件。一个裸的 `Anthropic()` / `new Anthropic()` / `anthropic.NewClient()` 在 `ant auth login` 后无需设置环境变量即可工作。

**当您需要调用API且 `ANTHROPIC_API_KEY` 未设置时，不要向用户索要密钥。** 首先运行 `ant auth status` - 它显示哪个凭证源和配置文件是活动的。如果它报告一个活动配置文件：

- **SDK代码或 `ant` CLI：** 直接运行它。零参数客户端构造函数和每个 `ant ...` 子命令自动拾取配置文件 - 不需要环境变量。
- **原始 `curl` / HTTP：** 使用 `ant auth print-credentials --access-token` 获取一个短期令牌，并将其作为 `Authorization: Bearer <token>` 发送 **加上** 标头 `anthropic-beta: oauth-2025-04-20`（OAuth令牌放在 `Authorization: Bearer`，而不是 `x-api-key:` - 从curl转换为API密钥是标头更改，不是密钥交换）。始终传递 `--access-token`；无标志形式打印JSON，而不是裸令牌。

只有在 `ant auth status` 报告没有活动凭证源（或 `ant` 本身未安装）时才向用户索要密钥。建议 `ant auth login` 作为首选选项 - 它在 `~/.config/anthropic/` 下存储一个配置文件，SDK自动读取它 - 以及导出的 `ANTHROPIC_API_KEY` 作为替代方案。

完整身份验证详细信息（命名配置文件、范围、API密钥-阴影配置文件陷阱、刷新令牌过期）：`shared/anthropic-cli.md`。

---

## 思考 & 努力（快速参考）

在当前所有模型上使用自适应思考（`thinking: {type: "adaptive"}`）- Claude动态决定何时以及如何思考。每模型规则：

| 模型 | 思考配置 | 忽略 `thinking` | `budget_tokens` | 采样 (`temperature`/`top_p`/`top_k`) | 努力级别 |
|---|---|---|---|---|---|
| Fable 5 / Claude Fable 5.1 (以及对应的 Mythos 模型) | `{type: "adaptive"}` 或省略；显式 `{type: "disabled"}` 返回 400 - 直接省略参数（Claude Fable 5.1 / Claude Mythos 5.1 在强制 `tool_choice` `any`/`tool` 时也返回 400，并在重播思考块时保留思考历史编辑检查) | 运行自适应（思考始终开启） | 已移除 - `{type: "enabled", budget_tokens: N}` 返回 400 | 已移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Claude Opus 5 | `{type: "adaptive"}` 或省略；`{type: "disabled"}` 仅在努力级别 `high` 或更低时接受 - `xhigh`/`max` 时返回 400，并见下文禁用思考的陷阱 | 运行 **自适应**（思考默认开启 - 与 Opus 4.8/4.7 不同） | 已移除 - 400 | 已移除 - 400 | `low`-`max`（全部五个） |
| Opus 4.8 / 4.7 | `{type: "adaptive"}` 是唯一开启模式；`{type: "disabled"}` 接受 | 运行 **不**带思考 - 显式设置 `{type: "adaptive"}` | 已移除 - 400 | 已移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Sonnet 5 | `{type: "adaptive"}` 是唯一开启模式；`{type: "disabled"}` 接受 | 运行自适应 | 已移除 - 400 | 已移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Opus 4.6 / Sonnet 4.6 | `{type: "adaptive"}`（推荐；自动启用交错思考，无 beta 头部） | 显式设置 `{type: "adaptive"}` | 已弃用 - 新代码中不要使用；仅作为过渡的逃逸通道（见下文） | 允许 | `low`/`medium`/`high`/`max` (`xhigh` 随 Opus 4.7 一起出现) |
| 更旧的模型（Sonnet 4.5, Haiku 4.5, ...）- 仅在明确请求时 | `{type: "enabled", budget_tokens: N}` | 无思考 | 对思考是必需的；必须小于 `max_tokens`，最小 1024 - 否则报错 | 允许 | `effort` 在 Opus 4.5 上有效 (`low`/`medium`/`high` 仅 - 无 `xhigh`/`max`）；Sonnet 4.5 / Haiku 4.5 上报错 |

Opus 4.8 保留与 4.7 相同的请求表面（无新的破坏性变更）- 请参阅 `shared/model-migration.md` -> Migrating to Opus 4.8 以获取行为重新调整，以及 -> Migrating to Opus 4.7 以获取从 4.6 或更早版本来的完整破坏性变更列表。在禁用 `thinking` 时，Opus 4.8 可能会在可见响应中写入更长的推理 - 保持自适应思考开启，或添加仅最终答案的指令（见迁移指南）。

- **努力（GA，无 beta 头部）**：`output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}` - 在 `output_config` 内，不是顶层；默认 `high`（相当于省略它）。控制思考深度和总体 token 消耗；与自适应思考结合以获得最佳成本质量权衡。`xhigh`（在 Opus 4.7 中添加，位于 `high` 和 `max` 之间）是 Fable 5 / Opus 4.7/4.8 / Sonnet 5 上大多数编码和代理用例的最佳设置，也是 Claude Code 中的默认值；这些模型上的努力比同级别之前的任何模型都更重要 - 迁移时重新调整它，并使用完整的任务规范在前端运行长时程/代理任务于 `high`/`xhigh`。对智能敏感的工作使用至少 `high`，`max` 时的正确性比成本更重要，简单任务使用 `low` - 较低努力意味着较少且更整合的工具调用，较少的前置文本，以及更简洁的确认（`high` 通常是在质量和 token 效率之间取得平衡的甜点）。
- **选择努力级别（成本调整）**：努力是第一个质量权衡杠杆，在免费胜利（首先缓存）之后 - 它在单个模型内权衡彻底性对 token 消耗的交换，顶部的范围只在难题上才值得其成本（仅在测量显示在较低级别下有空间时才提高到 `max`）。哪些工作负载回报更高的努力是工作负载的特性：编码和长时程代理工作反应强烈；聊天、分类和高容量或延迟敏感的路由通常不需要，并且在 `low` 上表现良好，`medium` 作为成本节约的降级步骤，在质量保持的情况下（上述每级默认值涵盖了其余部分）。在提高默认值之前，在真实请求样本上进行测量，并按路由而不是全局进行调整。在构建多模型成本级联之前，首先测量更简单的替代方案 - 在相同任务上最新模型的较低努力下最强大的模型：在 Fable 5 上，较低的努力通常超过先前模型的 `xhigh`，并且一个模型意味着一个缓存命名空间（缓存是模型范围的，因此级联放弃了跨模型的缓存重用；对话中顶层的 `effort` 变化仍然使消息缓存失效，尽管每条消息的努力系统消息在 Claude Fable 5.1 / Claude Mythos 5.1 / Claude Opus 5 上避免了这一点 - `shared/prompt-caching.md` § 无声无效者审计清单）。按完成的任务成本而不是每个请求的成本进行判断 - 一个更便宜的请求需要更多回合或重试才能完成工作，并不便宜。有关按工作负载测量的努力/成本权衡和完整杠杆顺序，`shared/cost-optimization.md` § 2.6。
- **思考显示 - `"omitted"` 在 Fable 5 / Claude Fable 5.1 / Mythos 5 / Claude Mythos 5.1 / Opus 5 / 4.8 / 4.7 / Sonnet 5 上默认**：`display: "summarized"` 返回推理的可读摘要；`"omitted"`（在所有八个上默认 - 与 Opus 4.6 和 Sonnet 4.6 相比，当时它是 `"summarized"`）流式传输空文本的 `thinking` 块。`display` 仅控制可见性 - 思考在任何设置下都会发生并计费相同；任何模型都不会暴露原始的思考链。如果您向用户流式传输推理，默认情况下看起来像输出前的长时间暂停 - 显式设置 `thinking: {type: "adaptive", display: "summarized"}`。 （独立于显示，在相同模型上继续时回显不变的思考块；其他模型静默忽略它们（Claude Fable 5.1 / Claude Mythos 5.1 读取它们）- 见迁移指南。）在 Claude Fable 5.1 / Claude Mythos 5.1 / Claude Fable 上，`display: "updates"`（beta `thinking-display-updates-2026-08-18`，所有平台）隐藏推理如 `"omitted"`，但返回模型的工具调用间进度笔记作为简短的 `thinking` 块摘要 - 见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 from Claude Fable 5 -> 新 API 功能。
- **当用户要求“扩展思考”、“思考预算”或 `budget_tokens`**：始终使用 Fable 5/5.1、Opus 5、4.8、4.7 或 4.6 并设置 `thinking: {type: "adaptive"}` - 固定思考-token 预算的概念已弃用，自适应思考取代它。不要在新 4.6/4.7/4.8 代码中使用 `budget_tokens`，也不要因为用户提到它就切换到旧模型。*渐进式迁移例外*：`budget_tokens` 仅在 Opus 4.6 和 Sonnet 4.6 上仍然有效，作为现有代码在调整 `effort` 之前需要一个硬 token 封顶的过渡逃逸通道 - 见 `shared/model-migration.md` -> 过渡逃逸通道。它在 Fable 5/5.1、Opus 5/4.7/4.8 和 Sonnet 5 上已完全移除。

---

## 压缩（快速参考）

**Beta、Fable 5/5.1、Opus 5、Opus 4.8、Opus 4.7、Opus 4.6、Sonnet 5 和 Sonnet 4.6。** 对于可能超过 1M 上下文窗口的长时间运行对话，启用服务器端压缩。API 在接近触发阈值时自动总结早期上下文（默认：150K tokens）。需要 beta 头部 `compact-2026-01-12`。

**关键**：在每次回合时将 `response.content`（而不仅仅是文本）追加到您的消息中。响应中的压缩块必须保留 - API 使用它们在下一个请求中替换压缩的历史记录。仅提取文本字符串并追加将无声地丢失压缩状态。

有关代码示例，请参阅 `{lang}/claude-api/README.md`（压缩部分）。完整文档通过 WebFetch 在 `shared/live-sources.md` 中提供。

---

## 提示缓存（快速参考）

**前缀匹配。** 前缀中任何字节的变化都会使它之后的所有内容失效。渲染顺序是 `tools` -> `system` -> `messages`。保持稳定内容在前（冻结的系统提示、确定的工具列表），将易变内容（时间戳、每次请求的 ID、变化的问题）放在最后一个 `cache_control` 断点之后。

**对话中操作员指令**（Claude Opus 5、Claude Opus 4.8、Claude Fable 5、Claude Fable 5.1、Claude Mythos 5、Claude Mythos 5.1；不包括 Claude Sonnet 5；无 beta 头部）：将 `{"role": "system", ...}` 追加到 `messages[]` 而不是编辑顶层 `system`。保留缓存的上下文前缀，并是安全的提示注入操作通道。见 `shared/prompt-caching.md` § Mid-conversation system messages。

**顶层自动缓存**（`cache_control: {type: "ephemeral"}` 在 `messages.create()` 上）是最简单的选项，当您不需要细粒度位置时。最多 4 个断点每个请求。可缓存前缀的最小长度是模型相关的（512-4096 tokens - 见 `shared/prompt-caching.md` § API 参考）- 较短的前缀将无声地不会缓存。

**使用 `usage.cache_read_input_tokens` 进行验证** - 如果它在重复请求中为零，则存在无声无效者 (`datetime.now()` 在系统提示中、未排序的 JSON、变化的工具集)。

有关放置模式、架构指南和无声无效者审计清单：阅读 `shared/prompt-caching.md`。特定语言的语法：`{lang}/claude-api/README.md`（提示缓存部分）。

---

## 快速模式（快速参考）

**研究预览，Claude Opus 5 / Opus 4.8 仅** - Claude API 和 Managed Agents，不包括 Bedrock / Google Cloud / Foundry。Opus 4.7 快速模式已移除：在 4.7 上设置 `speed: "fast"` 返回错误。Claude Opus 5 上的快速模式定价为 $10 / $50 每百万 token。快速模式以溢价价格运行相同模型，每秒输出 token 高达 2.5 倍。每个请求都需要三个东西：使用 **beta** 消息端点 (`client.beta.messages....`), 传递 beta 标志 `fast-mode-2026-02-01`, 并将 `speed: "fast"` 作为顶层请求参数（不是头部，不是在 `extra_body` 中）。

```python
client.beta.messages.create(
    model="claude-opus-5", max_tokens=4096,
    speed="fast", betas=["fast-mode-2026-02-01"],
    messages=[...],
)
```

| 语言 | Beta 标志 | 速度参数 |
|---|---|---|
| Python | `betas=["fast-mode-2026-02-01"]` | `speed="fast"` |
| TypeScript / Ruby | `betas: ["fast-mode-2026-02-01"]` | `speed: "fast"` |
| Go | `[]anthropic.AnthropicBeta{anthropic.AnthropicBetaFastMode2026_02_01}` | `Speed: anthropic.BetaMessageNewParamsSpeedFast` |
| Java | `.addBeta(AnthropicBeta.FAST_MODE_2026_02_01)` | `.speed(MessageCreateParams.Speed.FAST)` |
| C# | `Betas = ["fast-mode-2026-02-01"]` | `Speed = Speed.Fast` (`Anthropic.Models.Beta.Messages`) |
| PHP | `betas: ['fast-mode-2026-02-01']` | `speed: 'fast'` |
| cURL | `anthropic-beta: fast-mode-2026-02-01` 头部 | `"speed": "fast"` 在主体中 |

`response.usage.speed` 报告使用了哪个速度。快速模式有自己的速率限制，与标准 Opus 分开；在 429 时，要么在 `retry-after` 延迟后重试，要么丢弃 `speed` 并回退到标准（注意：切换速度使提示缓存失效）。不适用于 Batch API、优先级层、Claude Platform on AWS 或第三方平台。

**优先级层不是在所有当前模型上都支持。** 它在 Claude Fable 5、Opus 4.8 和较旧的当前模型上支持，但 Claude Opus 5、Claude Sonnet 5、Claude Fable 5.1、Claude Mythos 5.1、Claude Mythos 5 和 Mythos Preview 被排除在外 - 命名其中之一的优先级层请求将失败验证。

---

## 任务预算（快速参考）

**Beta、Claude Opus 5 / Fable 5 / Claude Fable 5.1（启动时确认）/ Sonnet 5 / Opus 4.8 / 4.7。** 任务预算为 Claude 在代理循环中提供一个 token 封顶，使其能够自我调节并优雅地完成，而不是被切断 - 这与 `max_tokens` 不同，后者是模型不知道的强制的每个响应上限。最小 `total`：20,000。在 `client.beta.messages.stream(...)` 的 `output_config` 内设置 `task_budget` 并使用 beta 标志 `task-budgets-2026-03-13` - 使用流式传输，以便大型 `max_tokens` 不会触发 HTTP 超时（详细信息：`shared/model-migration.md` -> Task Budgets）：

```python
with client.beta.messages.stream(
    model="claude-opus-5", max_tokens=128000,
    output_config={"effort": "high", "task_budget": {"type": "tokens", "total": 64000}},
    betas=["task-budgets-2026-03-13"],
    messages=[...], tools=[...],
) as stream:
    response = stream.get_final_message()
```

`task_budget` 字段：`type`（始终 `"tokens"`）、`total` 和可选 `remaining`（默认为 `total`）。服务器在生成期间向 Claude 注入倒计时标记；预算计算 Claude 生成的和本回合读取的工具结果 - **不是**您每次请求重新发送的完整历史记录。这与 **Managed Agents 会话预算** 不同 - 那些是硬性、以美元计价的、平台强制执行的单一 CMA 会话上限（`shared/managed-agents-core.md` § Session budgets）；任务预算是建议性的，以 token 计价。

**观察支出**：如果您希望在循环迭代中累积 `response.usage.output_tokens`（以及您追加的工具结果块的 token 数）以显示进度，则保留 `remaining` 未设置在正常循环中 - 服务器自己跟踪倒计时，并且当您在重新发送完整历史记录的同时传递客户端计算的 `remaining` 时，会低估预算。**仅传递 `remaining`** 当您在请求之间压缩或重写历史记录并且服务器无法再推导出先前的支出时。

---

## 提供商客户端（快速参考）

当目标为第三方平台上的 Claude 时，使用该平台的专用客户端类 - 不要使用带有 `base_url` 覆盖的第一方 `Anthropic()` 客户端。构建后，客户端暴露与第一方 SDK 相同的 `messages.create` / `.stream` 表面。

### Amazon Bedrock

使用 **Mantle** 客户端（Messages-API Bedrock 端点）。Bedrock 模型 ID 需要一个 `anthropic.` 前缀（例如 `"anthropic.claude-opus-5"`）。区域是必需的。

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicBedrockMantle` -> `AnthropicBedrockMantle(aws_region="...")` |
| TypeScript | `import { AnthropicBedrockMantle } from "@anthropic-ai/bedrock-sdk"` -> `new AnthropicBedrockMantle({ awsRegion: "..." })` |
| Go | `bedrock.NewMantleClient(ctx, bedrock.MantleClientConfig{ AWSRegion: "..." })` |
| Java | `AnthropicOkHttpClient.builder().backend(BedrockMantleBackend.fromEnv()).build()` (from `com.anthropic.bedrock.backends`) |
| C# | `new AnthropicBedrockMantleClient(new() { AwsRegion = "..." })` (package `Anthropic.Bedrock`) |
| PHP | `use Anthropic\Bedrock\MantleClient;` -> `new MantleClient(awsRegion: '...')` |
| Ruby | `Anthropic::BedrockMantleClient.new(aws_region: "...")` |

`AnthropicBedrock` / `BedrockClient` / `BedrockBackend`（不带 `Mantle`）是遗留的 `bedrock-runtime` InvokeModel 路径 - 新代码请优先使用 Mantle 客户端。

### Microsoft Foundry

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicFoundry` -> `AnthropicFoundry(api_key=..., resource="...")` |
| TypeScript | `import AnthropicFoundry from "@anthropic-ai/foundry-sdk"` -> `new AnthropicFoundry({ ... })` |
| Java | `AnthropicOkHttpClient.builder().backend(FoundryBackend.fromEnv()).build()` (from `com.anthropic.foundry.backends`) |
| C# | `new AnthropicFoundryClient(new AnthropicFoundryApiKeyCredentials(...))` (package `Anthropic.Foundry`) |
| PHP | `Foundry\Client::withCredentials(...)` |

Go 和 Ruby SDK 目前不支持 Foundry。对于 Ruby，使用标准 `Anthropic::Client.new(base_url: "<foundry endpoint>")` 作为后备（Entra ID 认证未内置）。对于 Claude Platform on AWS，见 `shared/claude-platform-on-aws.md`。

### Google Cloud Vertex AI

两个必需的构造参数：GCP `project_id` 和 `region`。Vertex 模型 ID **不需要前缀** — 当前代模型（Opus 4.8/4.7/4.6、Sonnet 5、Sonnet 4.6）使用裸的第一方 ID（例如 `"claude-opus-5"`）；带日期快照的模型使用 `@` 版本分隔符（例如 `claude-opus-4-5@20251101`，而**不是** `claude-opus-4-5-20251101`）。认证使用 GCP ADC（`gcloud auth application-default login`）；无需 Anthropic API 密钥。`region` 可以是 `"global"`（推荐）、多区域（`"us"`/`"eu"`）或特定区域。构建后，使用相同的 `messages.create` / `.stream` 接口。

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicVertex` -> `AnthropicVertex(project_id="...", region="...")`（安装 `"anthropic[vertex]"`） |
| TypeScript | `import { AnthropicVertex } from "@anthropic-ai/vertex-sdk"` -> `new AnthropicVertex({ projectId, region })` |
| Go | `import "github.com/anthropics/anthropic-sdk-go/vertex"` -> `anthropic.NewClient(vertex.WithGoogleAuth(ctx, region, projectID))` |
| Java | `AnthropicOkHttpClient.builder().backend(VertexBackend.builder().region("...").project("...").build()).build()`（来自 `com.anthropic.vertex.backends`） |
| C# | `new AnthropicClient { Backend = new VertexBackend(projectId, region) }`（包 `Anthropic.Vertex`） |
| PHP | `use Anthropic\Vertex;` -> `Vertex\Client::fromEnvironment(location: '...', projectId: '...')` — 注意是 `location` 而非 `region` |
| Ruby | `Anthropic::VertexClient.new(region: "...", project_id: "...")` |

---

## 上下文编辑（快速参考）

**Beta。** 上下文编辑会在模型看到对话之前**清除**旧的工具结果或思考块；它**不是压缩**（压缩是摘要）。在 `client.beta.messages.*` 上使用 beta `context-management-2025-06-27`，传入带有策略类型的 `context_management.edits`：

```python
client.beta.messages.create(
    model="claude-opus-5", max_tokens=4096,
    betas=["context-management-2025-06-27"],
    context_management={"edits": [{"type": "clear_tool_uses_20250919"}]},
    tools=[...], messages=[...],
)
```

策略类型：`clear_tool_uses_20250919`（清除旧的工具结果；可选的 `clear_tool_inputs: true` 还会清除 tool_use 参数）和 `clear_thinking_20251015`（清除思考块）。**不要**使用 `compact_20260112` 或 beta `compact-2026-01-12` — 那些是独立的压缩功能。

---

## 对话中途系统消息（快速参考）

**Claude Opus 5、Claude Opus 4.8、Claude Fable 5、Claude Fable 5.1、Claude Mythos 5 和 Claude Mythos 5.1；不适用于 Claude Sonnet 5；无需 beta 头。** 将 `{"role": "system", "content": "..."}` 追加到 `messages` 数组中（而非顶层 `system` 字段），即可在对话中途添加操作员指令而不会使缓存前缀失效。使用常规的 `client.messages.create` — 没有 beta。对话中途的系统消息必须跟在一条 `user` 消息（或以 server-tool 使用结尾的 `assistant` 消息）之后，且必须是 `messages` 中的最后一个条目或后面跟着一个 `assistant` 回合 — 它不能是 `messages[0]`。可用性：`shared/platform-availability.md`。参见 `shared/prompt-caching.md` § 对话中途系统消息。随 Claude Fable 5.1 发布的 beta 扩展：`output_config: {effort: ...}` 配合 `content: []` 可从该点起更改 effort 而无需重置缓存（beta `mid-conversation-output-config-2026-07-01`；Claude Fable 5.1、Claude Mythos 5.1、Claude Opus 5；Claude API）。仅包含 effort 的消息（空 `content`）不受上述位置规则约束 — 它可以放在 `messages` 的任何位置，包括开头或 assistant 回路与下一条 user 回路之间；这些规则适用于文本消息和 `clear_at` 消息。对于单轮提醒，给消息设置 `clear_at: "next_user_message"`（beta `mid-conversation-system-clear-at-2026-08-21`）：它渲染一轮后保持在对话记录中但已清除 — 切勿删除更早的副本（在 Claude Fable 5.1 上删除一个会使后续思考块失效）；没有 beta 的情况下，工具结果后的文本块，保留更早的副本。参见 `shared/model-migration.md` -> 从 Claude Fable 5 迁移到 Claude Fable 5.1 -> 新 API 功能。

---

## 托管 Agent（Beta）

**托管 Agent** 是第三种接口：由服务器管理的有状态 agent，带有 Anthropic 托管的工具执行。你创建一个持久化的、带版本的 Agent 配置（`POST /v1/agents`），然后启动引用它的 Session。每个 session 会配置一个容器作为 agent 的工作区 — bash、文件操作和代码执行都在其中运行；agent 循环本身运行在 Anthropic 的编排层上，并通过工具作用于容器。Session 以流式方式发送事件；你回传消息和工具结果。

可用性：`shared/platform-availability.md`。对于在 Bedrock / Vertex / Foundry 上的 agent（不支持托管 Agent 的环境），使用 Claude API + 工具调用。

**强制流程：** Agent（一次）-> Session（每次运行）。`model`/`system`/`tools` 放在 agent 上，绝不放在 session 上。完整的阅读指南、beta 头和注意事项参见 `shared/managed-agents-overview.md`。

**Beta 头：** `managed-agents-2026-04-01` — SDK 会自动为所有 `client.beta.{agents,environments,sessions,vaults,memory_stores,deployments,deployment_runs}.*` 调用设置此头。Files API 和 Skills API 已退出 beta — 无需 beta 头（迁移指南参见上方的 API 漂移表）。

**子命令** — 通过 `/claude-api <subcommand>` 直接调用：

| 子命令 | 操作 |
|---|---|
| `managed-agents-onboard` | 引导用户从零开始设置一个托管 Agent。**立即阅读 `shared/managed-agents-onboarding.md`** 并按其访谈脚本执行：**描述 -> 配置 agent（提出建议，而非审问）-> 环境 -> session**（与 Console 快速入门相同的弧线，认证推迟到 session 步骤）— 默认值和内联建议承担主要工作，在生成任何代码之前有一个静默的可行性关卡（任务 vs 工具/凭据/数据）。不要总结 — 执行访谈。 |

**阅读指南：** 从 `shared/managed-agents-overview.md` 开始，然后是各主题的 `shared/managed-agents-*.md` 文件（core、environments、tools、events、outcomes、multiagent、webhooks、memory、scheduled-deployments、client-patterns、onboarding、api-reference）。对于 Python、TypeScript、Go、Ruby、PHP 和 Java，阅读 `{lang}/managed-agents/README.md` 获取代码示例。对于 cURL，阅读 `curl/managed-agents.md`。**Agent 是持久的 — 创建一次，通过 ID 引用。** 将 agent 和环境定义为版本控制的 YAML，使用 `ant` CLI 应用 — 这是推荐的流程（参见 `shared/anthropic-cli.md`）：CLI 拥有控制平面（创建和更新 agent），你的代码拥有数据平面（使用存储的 agent ID 调用 `sessions.create`）。仅在必须通过编程方式配置时才在代码中调用 `agents.create()`；无论如何，存储返回的 agent ID 并将其传递给后续的每次 `sessions.create`；绝不在请求路径中调用 `agents.create()`。如果你在语言 README 中未找到所需的绑定，WebFetch `shared/live-sources.md` 中相关的条目，而非猜测。C# 通过 `client.Beta.Agents` 和相关命名空间提供 beta 托管 Agent 支持 — 详情参见 `csharp/claude-api/README.md`，或 `curl/managed-agents.md` 获取原始 HTTP 参考。

**当用户想从零开始设置一个托管 Agent 时**（例如"我如何开始"、"带我创建一个"、"设置一个新 agent"）：阅读 `shared/managed-agents-onboarding.md` 并执行其访谈 — 与 `managed-agents-onboard` 子命令相同的流程。

**当用户问"如何编写 X 的客户端代码"时：** 查阅 `shared/managed-agents-client-patterns.md` — 涵盖无损流重连、`processed_at` 排队/已处理关卡、中断、`tool_confirmation` 往返、正确的 idle/terminated 退出关卡、idle 后的状态竞争、流优先排序、文件挂载陷阱等。对于凭据，首选 vault `environment_variable` 凭据 — 这是第一类机制；秘密在出口处被替换，绝不进入沙箱（`shared/managed-agents-tools.md` -> Vaults）。通过自定义工具在主机端保留凭据是 vault 凭据不适用时的后备方案（例如自托管沙箱）。

**当用户询问工具审批、权限策略或"自动模式"时**（哪些工具调用需要人工、让服务器评估调用、tool-use 事件上的 `evaluated_permission` / `evaluation`）：阅读 `shared/managed-agents-tools.md` § 权限策略 — `always_allow` / `always_ask` / `auto` 以及 `auto` 的三种结果（执行、作为高风险拒绝、不确定时暂停）。关于将终端连接到实时 session（`ant beta:sessions connect`）：`shared/anthropic-cli.md`。

**当用户希望 agent 按计划运行时**（cron、"每天晚上"、"每周报告"）：阅读 `shared/managed-agents-scheduled-deployments.md` — deployment 按 cron 节奏自主触发 session，带有每次触发的运行记录和生命周期控制（暂停/恢复/归档）。

**当 agent 的工作需要扇出时**（跨多个来源的研究、按文件或按记录的工作、"调查 N 件事，然后总结"）**或一个循环会因为大量阅读而填满上下文时：** 阅读 `shared/managed-agents-multiagent.md` 并建议使用多 agent session — 从名册中的 `{"type": "self"}` 开始，使 agent 可以委派给自身的副本，然后将大量阅读的子任务交给更便宜的 worker agent（例如 Claude Haiku 4.5），通过 ID 引用。

---

## 服务器工具（快速参考）

服务器端工具运行在 Anthropic 的基础设施上 — 无需客户端执行循环。在 `tools` 中声明；结果作为内容块在同一响应中返回。**除非另有说明，否则无需 beta 头。** **优先使用你的模型支持的最新类型变体。** 下方的 `_20260209` 网络搜索 / 网络获取变体（动态过滤）需要 Opus 5/4.8/4.7/4.6、Sonnet 5 或 Sonnet 4.6；旧模型的基本变体列在表格之后。

| 工具 | `type` | `name` | 主要可选参数 | 结果块类型 |
|---|---|---|---|---|
| 网络搜索 | `web_search_20260209` | `web_search` | `max_uses`、`allowed_domains`/`blocked_domains`、`user_location` | `web_search_tool_result` -> `.content` 是 `web_search_result` 列表 |
| 网络获取 | `web_fetch_20260209` | `web_fetch` | `max_uses`、`allowed_domains`/`blocked_domains`、`citations`、`max_content_tokens` | `web_fetch_tool_result` -> `.content` 是带有 `document` 块的 `web_fetch_result` |
| 代码执行 | `code_execution_20260521` | `code_execution` | 无 | `bash_code_execution_tool_result` -> `.content.stdout` / `.stderr` / `.return_code` |
| 工具搜索（正则） | `tool_search_tool_regex_20251119` | `tool_search_tool_regex` | 将其他工具标记为 `defer_loading: true` | `tool_search_tool_result` |
| 工具搜索（BM25） | `tool_search_tool_bm25_20251119` | `tool_search_tool_bm25` | 将其他工具标记为 `defer_loading: true` | `tool_search_tool_result` |

`web_search_20260209` / `web_fetch_20260209` 具有内置动态过滤 — 内部会运行代码执行，因此**不要**在 `tools` 中单独声明 `code_execution`（第二个执行环境会混淆模型）。对于 Opus 4.6 / Sonnet 4.6 之前的模型，改用基本变体 `web_search_20250305` / `web_fetch_20250910`；在 Vertex AI 上仅可使用基本 `web_search_20250305`。`code_execution_20260120`（REPL 持久化 + 程序化工具调用）适用于 Opus 4.5+ / Sonnet 4.5+。**仅 Go SDK**：`code_execution_20260521` 位于 `client.Beta.Messages.New` 下，带有 `Betas: []anthropic.AnthropicBeta{"code-execution-2025-08-25"}`（其他语言使用普通的 `client.messages.create`）；`code_execution_20260120` 在 Go 中使用非 beta 的 `client.Messages.New`，与其他地方相同。Web fetch 仅获取对话中已存在的 URL。各提供商的工具可用性因工具而异 — 参见 `shared/platform-availability.md`。`pause_turn` 处理参见 `shared/tool-use-concepts.md`。

## 文档与文件输入（快速参考）

**PDF（base64，无需 beta）：** `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": <b64 string>}}` 放在用户内容中，置于文本块之前。Base64 字符串不得包含换行符。限制：32 MB 请求，600 页（200k 上下文模型为 100 页）。Java：`ContentBlockParam.ofDocument(DocumentBlockParam... Base64PdfSource.builder().data(...))`。

**Files API（无需 beta）：** 通过 `client.files.upload(...)` 上传 -> 响应中的 `id` 即为 `file_id`。对 PDF/文本引用为 `{"type": "document", "source": {"type": "file", "file_id": "..."}}`，对图像引用为 `{"type": "image", ...}` — 内容块类型必须与文件的 MIME 类型匹配。要从 `files-api-2025-04-14` 迁移代码，WebFetch `shared/live-sources.md` 中 Files API 的行。可用性：`shared/platform-availability.md`。

**引用标注（无需 beta）：** 在每个 `document` 内容块上设置 `citations: {enabled: true}`（全部启用或不启用）。响应会拆分为多个 `text` 块；被引用的块带有 `citations` 数组。每个引用包含 `cited_text`、`document_index`、`document_title`，以及按 `type` 区分的定位：`char_location`（`start_char_index`/`end_char_index`）用于纯文本，`page_location`（`start_page_number`/`end_page_number`，从 1 开始）用于 PDF，`content_block_location` 用于自定义内容。与 `output_config.format` 不兼容（返回 400）。

## 工具调用模式（快速参考）

**严格工具调用（无需 beta）：** 在工具定义上设置 `strict: true` 作为顶层字段（与 `name`/`description`/`input_schema` 并列），而**不是**在 `tool_choice` 上。Schema 必须包含 `additionalProperties: false` + `required`。保证 `tool_use.input` 严格验证。Go：`Strict: anthropic.Bool(true)` + 通过 `InputSchema.ExtraFields` 设置 `additionalProperties`；Java：`.strict(true)` + `.putAdditionalProperty("additionalProperties", JsonValue.from(false))`。

**并行工具调用（默认开启）：** 一条 assistant 消息可包含多个 `tool_use` 块。并发执行它们，然后在**一条** user 消息中返回**所有** `tool_result` 块 — 将它们拆分到多条消息中会悄无声息地训练 Claude 停止并行调用。对于失败的工具，返回带有 `is_error: true` 的 `tool_result` — 不要丢弃它。

**工具运行器（SDK beta 辅助）：** 通过 `client.beta.messages.*` 为你驱动工具调用循环。Python：`@beta_tool` 装饰器 + `client.beta.messages.tool_runner(...)` -> `runner.until_done()`。TypeScript：来自 `@anthropic-ai/sdk/helpers/beta/zod` 的 `betaZodTool({...})` + `client.beta.messages.toolRunner(...)` -> `await runner`。Go：`toolrunner.NewBetaToolFromJSONSchema(...)` + `client.Beta.Messages.NewToolRunner(...)` -> `.RunToCompletion(ctx)`。Java 需要 `.addBeta("structured-outputs-2025-11-13")`。Ruby：`Anthropic::BaseTool` 子类 + `client.beta.messages.tool_runner(...)`。PHP：`BetaRunnableTool` + `->toolRunner(...)`。C#：原始 JSON-schema 工具 + 通过 `client.Beta.Messages.ToolRunner(...)` 使用 `BetaToolRunner`。

**程序化工具调用（无需 beta 头）：** Claude 在代码执行内部调用你的自定义工具。添加 `{"type": "code_execution_20260120", "name": "code_execution"}` **并且**在你的自定义工具上设置 `"allowed_callers": ["code_execution_20260120"]`。Opus 4.5+ / Sonnet 4.5+（可用性：`shared/platform-availability.md`）。响应待处理的程序化调用时，user 消息必须**仅**包含 `tool_result` 块（无文本）。与 `strict: true`、`disable_parallel_tool_use`、强制 `tool_choice` 或 MCP 工具不兼容。

## 其他 API 接口（快速参考）

**批量消息（无测试版；可用性：`shared/platform-availability.md`）：** `client.messages.batches.create(requests=[{custom_id, params}, ...])` -> 持续轮询 `client.messages.batches.retrieve(id).processing_status` 直到 `"ended"` -> 流式传输 `client.messages.batches.results(id)`。每个结果都有 `.custom_id` + `.result.type` (`succeeded`/`errored`/`canceled`/`expired`)；成功时读取 `.result.message.content`。Python 将请求包装为 `Request(custom_id=..., params=MessageCreateParamsNonStreaming(...))`。结果以**任意顺序**到达 - 按 `custom_id` 键控，而非位置。

**模型 API（无测试版；可用性：`shared/platform-availability.md`）：** `client.models.list()`（自动分页）和 `client.models.retrieve("claude-opus-5")`。每个模型对象都有 `id`、`display_name`、`created_at`，以及自 2026 年 3 月起 `max_input_tokens`（上下文窗口）、`max_tokens`（输出上限）和 `capabilities`。没有 `context_window` 字段。

**停止详情（GA，Opus 4.7+）：** `response.stop_details` 仅在 `stop_reason == "refusal"` 时填充（字段：`type: "refusal"`、`category` - 一个开放集，例如 `"cyber"`、`"bio"`、`"reasoning_extraction"`、`"frontier_llm"` 或 `null`；参见文档获取完整列表 - 以及 `explanation`）。对于其他 `stop_reason`（`end_turn`、`max_tokens`、`tool_use`、`pause_turn`、...）均为 `null` - 读取前务必进行防护。

**管理 API（测试版，自 2026-08-26）：** 组织管理 - 成员、邀请、工作空间和工作空间成员、API 密钥、速率限制报告、服务账户、联盟发行者/规则、CMEK 外部密钥 - 在所有七个 SDK 中的 `client.beta.organization` 和 CLI 中的 `ant beta:organization` 下。需要管理员凭证：管理员 API 密钥（`sk-ant-admin...`，从 `ANTHROPIC_API_KEY` 读取）或 `org:admin` OAuth 令牌（`ANTHROPIC_AUTH_TOKEN`）；普通 API 密钥将被拒绝。使用和成本报告以及 Claude 企业用户管理/分析端点**不**在 SDK 中 - 仅限原始 HTTP。参见 `shared/admin-api.md`。

**客户端配置（无测试版）：** `timeout` 默认 10 分钟；**单位因 SDK 而异** - Python/Ruby：秒；TypeScript：**毫秒**；Go `option.WithRequestTimeout(time.Duration)`；Java `Duration`；C# `TimeSpan`。TS 将默认值扩展到 60 分钟用于非流式请求上的大型 `max_tokens`；Java 对流式请求也这样做（Java 非流式扩展 30 秒-10 分钟）。`max_retries`/`maxRetries` 默认 2（重试 408/409/429/5xx + 连接错误）。`base_url`（或 `ANTHROPIC_BASE_URL` 环境）。请求级覆盖：Python `client.with_options(timeout=5.0).messages.create(...)`；TS `client.messages.create({...}, {timeout: 5_000})`；Ruby `request_options: {timeout: 5}`。超时会被重试 - 墙上时间可能达到 `timeout × (max_retries+1)`。

## 工作负载身份联盟（快速参考）

**GA，无测试版标题。** 构建正常的零参数客户端（`Anthropic()` / `new Anthropic()` / `anthropic.NewClient()` / `AnthropicOkHttpClient.fromEnv()`）；SDK 自动检测 WIF，当**所有** `ANTHROPIC_FEDERATION_RULE_ID`、`ANTHROPIC_ORGANIZATION_ID`、`ANTHROPIC_SERVICE_ACCOUNT_ID` 和 `ANTHROPIC_IDENTITY_TOKEN_FILE`（或 `ANTHROPIC_IDENTITY_TOKEN`）都设置时，交换 JWT 到 `/v1/oauth/token`，并自动刷新。`ANTHROPIC_WORKSPACE_ID` 不限制激活 - 仅在联盟规则跨越多个工作空间时需要（否则 400 `workspace_id_required`），单工作空间规则可选。`ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`（即使为空）优先于 WIF，且设置的 `ANTHROPIC_PROFILE` 也优先于联盟环境变量（缺少命名配置是错误，非降级）- 清除所有三个。

---

## 阅读指南

检测语言后，根据用户需求读取相关文件。本文档中引用的每个 `{lang}/...`、`shared/...` 和 `curl/...` 路径都相对于此技能的基目录，且上述文件内容均未包含 - 在依赖其内容前按需读取每个文件。

**所有 SDK 语言使用相同的多文件布局** - 目录 `{lang}/claude-api/` 包含 `README.md`（安装、客户端初始化、基本请求、思考、缓存、停止详情、杂项）、`tool-use.md`（工具定义、代理循环、Anthropic 定义工具、结构化输出）、`streaming.md`、`batches.md`、`files-api.md`。并非每种语言都有每种文件（例如，Ruby 没有 `batches.md`）；如果文件缺失，该语言的功能示例尚未文档化 - 回退到 cURL 形状或从 `shared/live-sources.md` WebFetch SDK 仓库。**cURL** -> `curl/examples.md`。

下方的快速任务参考对所有语言使用 `{lang}/claude-api/FILE.md` 路径表示法。

### 快速任务参考

**单文本分类/摘要/提取/Q&A：**
-> 仅读取 `{lang}/claude-api/README.md` - **任何任务前始终先读取 README**（安装、快速入门、常见模式、错误处理）

**聊天 UI 或实时响应显示：**
-> 读取 `{lang}/claude-api/README.md` + `{lang}/claude-api/streaming.md`

**长时间运行对话（可能超过上下文窗口）：**
-> 读取 `{lang}/claude-api/README.md` - 参见压缩部分
**迁移到更新模型（Fable 5.1 / Fable 5 / Opus 5 / Opus 4.8 / Opus 4.7 / Opus 4.6 / Sonnet 5 / Sonnet 4.6）、替换已停用模型、或翻译 `budget_tokens` / 预填模式到当前 API：**
-> 读取 `shared/model-migration.md`
**升级 Anthropic SDK 包本身跨主版本（`anthropic` 0.x -> 1.x: `httpx2`，期待异步 `.with_raw_response`，移除已弃用参数/别名/文本补全，Python >= 3.10）- 或针对已迁移到 1.x 的项目编写新代码：**
-> 读取 `{lang}/claude-api/sdk-upgrade.md`（目前 Python 仅限；其他 SDK 尚无捆绑主版本指南 - 通过 `shared/live-sources.md` 使用该 SDK 的 CHANGELOG）
**提示或调整 Fable 5/5.1（长回合、努力、冗长、自主运行、子代理）：**
-> 读取 `shared/model-migration.md` -> 迁移到 Claude Fable 5.1 -> 行为变化（提示可调）+ 长代理建议
**提示或调整 Claude Fable 5.1（进度更新、并行工具调用、写作密度/格式、自主性、测试蔓延、全文重写）或使适配器兼容保留的思考历史编辑检查（历史编辑、压缩、每回合提醒）：**
-> 读取 `shared/model-migration.md` -> 从 Claude Fable 5 迁移到 Claude Fable 5.1 -> 新 API 功能 + 行为变化（提示可调）；对于历史编辑检查本身（三步检查、追加编辑表、压缩形状），同一部分的变更 3
**提示缓存 / 优化缓存 / “我的缓存命中率为什么低”：**
-> 读取 `shared/prompt-caching.md`（前缀稳定性设计、断点放置、无声使缓存失效的反模式）+ `{lang}/claude-api/README.md`（提示缓存部分）
**审计或清理提示、技能或工具描述（“这个提示是否过时”、“删除冗余”、“这是为旧模型编写的”）：**
-> 读取 `shared/prompt-audit.md` - 带可搜索信号的日期模式表、保留列表（什么**不**要删除）、报告 + 提案差异输出合同
**计算文件/提示/差异中的 token 数（X 有多少 token）：**
-> 读取 `shared/token-counting.md` - 使用 `messages.count_tokens`，切勿使用 `tiktoken`
**减少或审查 API 花费（“账单太高”、“使其更便宜”、“我是否超支”，每项完成的任务成本，最便宜模型或努力保持质量）：**
-> 读取 `shared/cost-optimization.md` - 基线和 token 配置首先，然后按顺序（免费优先于权衡）调整杠杆，并带测量预期，以及工作负载形状 -> 杠杆映射表

**函数调用/工具使用/代理：**
-> 读取 `{lang}/claude-api/README.md` + `shared/tool-use-concepts.md`（概念基础：函数调用、代码执行、内存、结构化输出）+ `{lang}/claude-api/tool-use.md`（语言特定代码示例：工具运行器、手动循环、代码执行、内存、结构化输出）

**代理设计（工具表面、上下文管理、缓存策略）：**
-> 读取 `shared/agent-design.md`（bash 对专用工具，程序化工具调用，工具搜索/技能，上下文编辑 vs. 压缩 vs. 内存，缓存原则）

**批量处理（对延迟不敏感；异步运行，成本 50%）：**
-> 读取 `{lang}/claude-api/README.md` + `{lang}/claude-api/batches.md`

**跨多个请求上传文件（同一文件无需重新上传）：**
-> 读取 `{lang}/claude-api/README.md` + `{lang}/claude-api/files-api.md`

**组织管理（成员、邀请、工作空间、API 密钥、速率限制报告、服务账户、WIF 资源、CMEK）：**
-> 读取 `shared/admin-api.md` - `client.beta.organization` 端点/方法表、管理员凭证、各语言命名和分页，什么保留 cURL

**调试 HTTP 错误或实现错误处理：**
-> 读取 `shared/error-codes.md` - 每个语言类型的异常类表和 Go `errors.As` 模式

**最新官方文档：**
-> WebFetch `shared/live-sources.md` 中的 URL

**托管代理（带工作空间的服务器管理状态代理）：**
-> 参见上方“## 托管代理（测试版）”部分的阅读指南 - 它列出了每个 `shared/managed-agents-*.md` 文件和语言特定 README（`{lang}/managed-agents/README.md`，`curl/managed-agents.md`）。

---

## 何时使用 WebFetch

当需要获取最新文档时使用 WebFetch：

- 用户要求“最新”或“当前”信息
- 缓存数据似乎不正确
- 用户询问此处未涵盖的功能

实时文档 URL 在 `shared/live-sources.md`。

## 常见陷阱

- 传递文件或内容给 API 时不要截断输入。如果内容过长无法适应上下文窗口，应通知用户并讨论选项（如分块、摘要等），而不是默默截断。
- **预填已移除（Fable 5、Claude Fable 5.1、Opus 5、Sonnet 5 及 4.6/4.7/4.8 系列）：** 助手消息预填（last-assistant-turn 预填）在 Fable 5、Claude Fable 5.1、Opus 5、Sonnet 5、Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 上返回 400 错误。改用结构化输出（`output_config.format`）或系统提示指令来控制响应格式。（例外：fallback-credit 预填申领——当使用 `fallback_has_prefill_claim: true` 兑换积分时，服务器接受回显的助手消息；参见迁移指南的拒绝部分。）
- **迁移范围确认后再编辑：** 当用户要求将代码迁移到更新的 Claude 模型而不指定具体文件、目录或文件列表时，**必须先询问要首先应用哪个范围**——整个工作目录、特定子目录或特定文件集。在用户确认前不要开始编辑。命令式短语如“迁移我的代码库”、“将我的项目迁移到 X”、“升级到 Sonnet 4.6”或单纯的“迁移到 Opus 4.8”仍然**模糊不清**——它们告诉你该做什么但没说在哪里，所以需要询问。只有在提示明确指定了文件、特定目录或显式文件列表（“迁移 `app.py`”、“迁移 `services/` 下所有内容”、“更新 `a.py` 和 `b.py`”）时才无需询问。参见 `shared/model-migration.md` 第 0 步。
- **`max_tokens` 默认值：** 不要低估 `max_tokens`——达到上限会导致输出在思考中途截断并需要重试。对于非流式请求，默认设置为 `~16000`（保持响应在 SDK HTTP 超时范围内）。对于流式请求，默认设置为 `~64000`（超时不是问题，所以给模型留出空间）。只有在你有充分理由时才降低：分类（`~256`）、成本限制、故意生成短输出，或**`max_tokens: 0`** 用于缓存预热（参见 `shared/prompt-caching.md` -> 预热）。
- **禁用 Claude Opus 5 的思考会导致两种失败模式——优先选择低/中难度。** 仅影响明确选择禁用思考的代码；思考默认开启，所以要注意从 Opus 4.8 继承的禁用思考设置。使用 `thinking: {type: "disabled"}` 时，模型偶尔会在可见文本中写入工具调用，而不是 `tool_use` 块：回合成功，调用从未执行，未引发错误，并在代理循环中该文本污染后续回合。它还可能向响应中泄露 `<thinking>` 标签。开启思考并降低 `effort` 可修复这两种情况，同时仍能降低成本。如果必须保持禁用思考：**删除**任何“不要思考/不要推理”规则（这会使标签泄露更严重），不要命名思考标签，并添加组合指令 *"当使用工具时，你可能会先说一句简短的话。如果没有工具能表达用户的请求，就说出来而不是猜测。不要在响应中包含内部或系统 XML 标签。"* 详细说明：`shared/model-migration.md` -> 禁用思考时的两种失败模式。
- **128K 输出 token：** Fable 5、Claude Fable 5.1、Opus 5、Opus 4.6、Opus 4.7、Opus 4.8、Sonnet 5 和 Sonnet 4.6 支持 `max_tokens` 最高 128K，但 SDK 要求使用流式传输来避免 HTTP 超时。使用 `.stream()` 并配合 `.get_final_message()` / `.finalMessage()`。
- **强制工具使用已移除（Claude Fable 5.1 / Claude Mythos 5.1，如 Mythos 预览版）：** `tool_choice: {type: "any"}` 和 `{type: "tool", name: ...}` 返回 400（`tool_choice: type "tool" 和 "any" 不受此模型支持。`），在 `count_tokens` 和批处理中也一样。使用 `{type: "auto"}` 并加上明确命名工具的指令，在工具上设置 `strict: true` 以保持模式有效的参数，或使用结构化输出（`output_config.format`）——当强制调用仅存在以获取 JSON 返回时。`{type: "none"}` 不受影响；`disable_parallel_tool_use` 仍然与 `auto`（最多一个调用）一起工作。
- **工具调用 JSON 解析（Fable 5、Claude Fable 5.1、Opus 5 及 4.6/4.7/4.8 系列）：** Fable 5、Claude Fable 5.1、Opus 5、Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 在工具调用 `input` 字段中可能产生不同的 JSON 字符串转义（例如 Unicode 或正向斜杠转义）。始终使用 `json.loads()` / `JSON.parse()` 解析工具输入——永远不要对序列化输入进行原始字符串匹配。
- **结构化输出（所有模型）：** 使用 `output_config: {format: {...}}` 而不是 `messages.create()` 上的已弃用 `output_format` 参数。这是一个通用 API 变更，不是 4.6 特有的。
- **不要重新实现 SDK 功能：** SDK 提供高级辅助工具——使用它们而不是从零开始构建。具体来说：使用 `stream.finalMessage()` 而不是将 `.on()` 事件包装在 `new Promise()` 中；使用类型化异常类（`Anthropic.RateLimitError` 等）而不是字符串匹配错误消息；使用 SDK 类型（`Anthropic.MessageParam`、`Anthropic.Tool`、`Anthropic.Message` 等）而不是重新定义等效接口。
- **错误处理——捕获链式错误，而不是一个通用类。** 单个 `except APIStatusError` / `catch (AnthropicServiceException)` / `rescue APIError` 会丢失重试（429、>=500、网络）和非重试（400/404）失败的区分。按最具体优先级编写错误链——例如 `NotFoundError` -> `RateLimitError` -> `APIStatusError` -> `APIConnectionError`（或 Go 的等效：`errors.As` 到 `*anthropic.Error` 然后切换 `apierr.StatusCode { case 404: ...; case 429: ...; default: ... }`）。各语言类名和命名空间在 `shared/error-codes.md` 中。
- **不要研究 SDK 类型——先写代码。** 如果类型名称未在本文档包含的文档中显示，从语言特定文档中的命名空间/包表编写代码文件，让编译器的错误提示你正确的名称。不要在编写前花费时间在 WebFetch、SDK-repo 克隆或编译运行一个单独的反射程序来发现类型名称——先产生源文件，然后修复编译器报告的问题。快速 `strings` / `jar tf` / `javap` 对安装的 SDK 定位名称是可接受的（秒级返回），但不要升级到那之外。一个类型名称错误的文件可以修复；一个在发现过程中没有编写文件的会话无法修复。
- **Bash 和文本编辑器工具是 Anthropic 定义的、无模式的。** 声明 `{"type": "bash_20250124", "name": "bash"}` / `{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}` —— 没有 `input_schema`。一个具有你自己的模式名为 `"bash"` 的自定义工具是不同的工具。处理路径和安全检查在 `shared/tool-use-concepts.md` § 客户端工具。
- **顾问工具模型配对。** 顾问工具的 `model` 必须至少与请求的顶层 `model` 一样强大——例如执行器 `claude-sonnet-5` -> 顾问 `claude-opus-4-8` 或 `claude-opus-4-7`。无效的配对返回 400。配对表在 `shared/tool-use-concepts.md` § 顾问中。可用性：`shared/platform-availability.md`。
- **代理技能 != 管理代理。** 要让 Claude 通过代理技能生成 `.pptx`/`.xlsx`/等，调用 `client.beta.messages.create` 并使用 `container={"skills": [...]}`、`code_execution_20260521` 工具和 `code-execution-2025-08-25` beta（技能已出 beta——不需要 `skills-2025-10-02` 标头）。不要使用 `client.beta.agents` / `sessions` / `environments`——这些是管理代理界面，不是代理技能。
- **MCP 连接器需要两半。** `mcp_servers=[{type:"url", url, name}]` 单独被作为验证错误拒绝——同时添加 `tools=[{type:"mcp_toolset", mcp_server_name:<相同名称>}]` 并使用 beta `mcp-client-2025-11-20`。可用性：`shared/platform-availability.md`。
- **`inference_geo` 是一个直接顶级请求参数**——`client.messages.create(..., inference_geo="us")` / `.inferenceGeo("us")`。不要把它放在 `extra_body` / `putAdditionalBodyProperty` 中。（仅限消息 API——在管理代理中，`inference_geo` 而不是嵌套在代理的 `model` 对象中，永远不会是顶级；参见 `shared/managed-agents-core.md` § 固定推理地理位置。）支持 Opus 4.6 / Sonnet 4.6 及更高版本；可用性：`shared/platform-availability.md`。`response.usage.inference_geo` 报告推理运行的位置。
- **细粒度工具流不是 beta 功能。** 在工具定义上设置 `eager_input_streaming: true` 并调用常规的 `client.messages.stream(...)`。没有 beta 标头，也没有 `client.beta.*` 路径。
- **缓存诊断是 beta。** 使用 `client.beta.messages.*` 并配合 beta `cache-diagnosis-2026-04-07`。在第一回合传递 `diagnostics: {previous_message_id: null}`，在后续回合传递 `diagnostics: {previous_message_id: <前一个响应 ID>}`；结果在 `response.diagnostics` 中。可用性：`shared/platform-availability.md`。
- **内存工具类型是 `memory_20250818`。** 声明 `{"type": "memory_20250818", "name": "memory"}`。Go 使用 beta 命名空间类型 `{OfMemoryTool20250818: &anthropic.BetaMemoryTool20250818Param{}}` 在 `client.Beta.Messages.New` 上；Python/TypeScript/Ruby/PHP/C# 使用非 beta `client.messages.create`；Java 既有非 beta `MemoryTool20250818` 也有 beta 工具运行器路径。Python/TypeScript 提供 `BetaAbstractMemoryTool` / `betaMemoryTool` 辅助函数来实现后端。
- **使用该功能实际支持的模型。** 某些功能仅限于特定模型层级——快速模式仅限于 Claude Opus 5 / Opus 4.8（且仅限 Claude API），任务预算（仅限消息 API——管理代理会话预算没有模型层级限制）仅限于 Claude Opus 5 / Fable 5 / Claude Fable 5.1（启动时确认）/ Sonnet 5 / Opus 4.8 / 4.7，顾问工具需要有效的执行器<->顾问配对。如果用户的提示指定了该功能不支持的模型，改用支持的模型并输出中注明替换。
- **不要为 SDK 数据结构定义自定义类型：** SDK 导出所有 API 对象的类型。使用 `Anthropic.MessageParam` 用于消息，`Anthropic.Tool` 用于工具定义，`Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam` 用于工具结果，`Anthropic.Message` 用于响应。定义自己的 `interface ChatMessage { role: string; content: unknown }` 重复了 SDK 已提供的功能并丢失了类型安全。
- **报告和文档输出：** 对于生成报告、文档或可视化的任务，代码执行沙盒预装了 `python-docx`、`python-pptx`、`matplotlib`、`pillow` 和 `pypdf`。Claude 可以生成格式化文件（DOCX、PDF、图表）并通过文件 API 返回它们——考虑用于“报告”或“文档”类型请求，而不是纯 stdout 文本。
- **服务器工具错误不会引发异常。** Web 搜索和 Web Fetch 错误返回 HTTP 200 并带有 `web_search_tool_result` / `web_fetch_tool_result` 块，其 `content` 是单个错误对象（例如 `{error_code: "max_uses_exceeded"}`）——不是引发的异常。对于 Web 搜索，成功的 `content` 是一个 *列表*；错误的 `content` 是一个 *对象*——在索引前根据这一点分支。
- **管理代理 Web 工具忽略环境的 `networking`。** `web_search` / `web_fetch` 在云和自托管环境中都在 Anthropic 的服务器上运行，Console 组织级别的 Web 设置仅适用于消息 API。通过 `allowed_domains` 或 `blocked_domains`（永远不要同时使用；每个列表最多 1-64 个纯主机名，子域名包含在内；IP、裸 TLD、单标签和 `localhost` 风格名称在两者中都被拒绝；`web_search` 仅允许路径后缀）在工具集 `configs` 条目上限制它们——`shared/managed-agents-tools.md` § Web 搜索和 Web Fetch 设置。
- **代码执行输出块类型：** `code_execution_20260521` 返回 `bash_code_execution_tool_result`（带有 `.content.stdout`），**不是**传统的 `code_execution_tool_result`。迭代 `response.content` 并匹配正确的类型。
- **工具搜索：永远不要延迟所有内容。** 搜索工具本身不能有 `defer_loading: true`，且 `tools` 中至少有一个工具必须是非延迟的，否则 API 返回 400 `All tools have defer_loading set`。
