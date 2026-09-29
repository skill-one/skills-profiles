---
name: claude-api
description: 'Claude API / Anthropic SDK 参考文档 — 模型 ID、定价、参数、流式处理、工具使用、MCP、代理、缓存、令牌计数、模型迁移。

  TRIGGER — 打开目标文件前必须阅读；不要因为看起来像单行代码而跳过 — 当出现以下情况时：提示中任何形式的提及 Claude/Anthropic（Claude、Anthropic、Fable、Opus、Sonnet、Haiku、`anthropic`、`@anthropic-ai`、`claude-*`、`us.anthropic.*`、`[1m]`）；用户询问关于 LLM（定价/模型选择/限制/缓存） — 永远不要凭记忆回答；或者任务具有 LLM 形态但未指明提供者（代理/MCP/工具定义/多代理/RAG/LLM 判定/计算机使用；生成/摘要/提取/分类/改写/对话处理自然语言；调试拒绝/中断/流式处理/工具调用/令牌）。

  仅在处理其他提供者时跳过（覆盖所有触发器）：查询中提及 OpenAI/GPT/Gemini/Llama/Mistral/Cohere/Ollama；或者 `grep -rE ''openai|langchain_openai|google.generativeai|genai|mistralai|cohere|ollama''` 在项目命中中搜索（如果没有提及提供者，则先运行此 grep — 不要读取文件）。'
---

# 使用 Claude 构建 LLM 应用

这项技能帮助你使用 Claude 构建 LLM 应用。根据你的需求选择合适的界面，检测项目语言，然后阅读相关的语言特定文档。

## 开始前

扫描目标文件（如果没有目标文件，则扫描提示和项目）以查找非 Anthropic 提供商标记 - `import openai`，`from openai`，`langchain_openai`，`OpenAI(`，`gpt-4`，`gpt-5`，文件名如 `agent-openai.py` 或 `*-generic.py`，或任何明确指示保持代码提供商中立的指令。如果你发现任何，请停止并告知用户此技能生成 Claude/Anthropic SDK 代码；询问他们是否想将文件切换到 Claude 或想要非 Claude 实现。不要用 Anthropic SDK 调用编辑非 Anthropic 文件。（例外：`prompt-audit` 子命令是非交互式的，不会在此停止 - 它会在其报告的声明假设中记录非 Anthropic 提供商标记，并且永远不会建议将非 Anthropic 文件切换到 Anthropic SDK。）

## 输出要求

当用户要求你添加、修改或实现 Claude 功能时，你的代码必须通过以下方式之一调用 Claude：

1. **项目的官方 Anthropic SDK**（语言为 `anthropic`，`@anthropic-ai/sdk`，`com.anthropic.*` 等）。当项目存在支持的 SDK 时，这是默认选项。
2. **原始 HTTP** (`curl`，`requests`，`fetch`，`httpx` 等） - 仅当用户明确要求 cURL/REST/原始 HTTP，项目是 shell/cURL 项目，或语言没有官方 SDK 时使用。

永远不要混合使用这两种方式 - 不要因为在 Python 或 TypeScript 项目中感觉更轻而使用 `requests`/`fetch`。永远不要回退到 OpenAI 兼容的遮蔽层。

**永远不要猜测 SDK 使用情况。** 函数名、类名、命名空间、方法签名和导入路径必须来自明确的文档 - 要么是此技能中的 `{lang}/` 文件，要么是官方 SDK 存储库或文档链接（在 `shared/live-sources.md` 中列出）。如果你需要的绑定在技能文件中没有明确记录，则在编写代码之前从 `shared/live-sources.md` 中的相关 SDK 存储库进行 WebFetch。不要从 cURL 形状或从另一种语言的 SDK 推断 Ruby/Java/Go/PHP/C# API。

**如果 WebFetch 或存储库访问失败**（网络受限、超时、克隆被阻止）：不要不断重试 - 从 `{lang}/` 文件中的模式和命名空间/包表运行编译器或解释器，并迭代错误输出。对于静态类型 SDK（C#、Java、Go），针对本地错误的编译修复循环比被阻止的网络研究更快地达到工作代码。

## 默认值

除非用户另有要求：

对于 Claude 模型版本，请使用 Claude Opus 5.5，你可以通过确切的模型字符串 `claude-opus-5-5` 访问它。对于任何稍微复杂的东西，请默认使用自适应思考（`thinking: {type: "adaptive"}`）。最后，对于可能涉及长输入、长输出或高 `max_tokens` 的任何请求，请默认使用流式传输 - 它可以防止遇到请求超时。如果你不需要处理单个流事件，请使用 SDK 的 `.get_final_message()` / `.finalMessage()` 辅助函数来获取完整响应。当流式请求定义用户定义（客户端）工具时，在每个工具上设置 `eager_input_streaming: true`，以便大型工具输入（文件内容、代码、文档）按生成顺序流式传输，而不是在服务器完成缓冲后一次性到达；然后客户端拥有验证：SDK 的容错解析器可以返回无声截断的输入而不是引发错误，因此在使用它之前验证每个解析的工具输入与其模式（如 `betaZodTool` / 带有类型的 `@beta_tool` 做到这一点；`betaTool()` JSON-Schema 工具和手动循环必须自行验证），将失败视为无效 JSON（当你持有块时 `tool_result` 返回 `INVALID_JSON` 错误，否则重新提交），在运行工具之前检查 `max_tokens` / `refusal` 停止原因，并且只捕获 SDK 的 JSON 错误，而不是其类型 API 错误 - 模式在 `shared/tool-use-concepts.md` -> Eager input streaming 中。对于非流式请求、服务器工具以及通过代理或较旧的 Bedrock 模型部署（该部署拒绝该字段）时，请关闭它。

## 警告：API 漂移 - 你的训练先验可能已过时

2025-2026 年，几个常见的 Claude API 形状发生了变化。如果你记得培训中的模式，请在编写之前将其与此技能中的 `{lang}/` 文件进行验证 - 以下行是最常见的漂移点：

| 区域 | 过时的先验 | 当前 API |
|---|---|---|
| 扩展思考 | `thinking: {type: "enabled", budget_tokens: N}` | 在 Claude 4.6+ 模型上：`thinking: {type: "adaptive"}`。`budget_tokens` 在 Opus 4.6 / Sonnet 4.6 上已弃用，并在 Fable 5/5.1 / Sonnet 5.5 / Sonnet 5 / Opus 5.5 / 5 / 4.8 / 4.7 上以 400 错误拒绝。预 4.6 模型仍然使用 `budget_tokens`。 |
| 网络搜索 / 网络获取工具类型 | `web_search_20250305`，`web_fetch_20250910` | `web_search_20260209`，`web_fetch_20260209`（动态过滤）在 Opus 5.5/5/4.8/4.7/4.6、Sonnet 5.5、Sonnet 5 和 Sonnet 4.6 上，以及 Vertex AI 仅提供基本的 `web_search_20250305`（网络获取在 Vertex 上不可用） - 见下方的服务器工具 QR。 |
| PHP 参数名 | 作为命名参数的蛇形线名称（`max_tokens`） | 顶级命名参数是驼峰式（`maxTokens`）。嵌套数组键因功能而异（例如 `'taskBudget'`，`'skillID'`，`'mcp_server_name'`） - 从文档示例中复制确切的键；不要批量转换。 |
| 管理代理凭证 | 通过自定义工具在主机端保持密钥（在密钥库交付之前是唯一选项） | 密钥库 `environment_variable` 凭证 - 由 Anthropic 存储并替换在出口时，永远不会在沙盒中可见（`shared/managed-agents-tools.md` -> 密钥库）。主机端自定义工具仍然是自托管沙盒的回退选项。 |
| 文件 API / 技能 | `client.beta.files.*` / `client.beta.skills.*` 与 beta `files-api-2025-04-14` / `skills-2025-10-02` | 已退出 beta：`client.files.*` / `client.skills.*`，没有 beta 标头。在当前 SDK 中，`client.beta.files` / `client.beta.skills` 有与之前版本不兼容的形状变化，匹配稳定的命名空间 - 根据 `shared/live-sources.md` -> Files API / Skills Guide 进行迁移。 |

此技能中的 `{lang}` 文件对回忆的模式具有权威性。

---

## 子命令

如果用户请求是此提示底部的裸子命令字符串（没有散文），请搜索此文档中的每个 **子命令** 表 - 包括任何附加部分中的表 - 并直接遵循匹配的 Action 列。这允许用户通过 `/claude-api <subcommand>` 调用特定流程。如果文档中没有匹配的表，请将请求视为正常散文。

| 子命令 | 操作 |
|---|---|
| `migrate` | 将现有的 Claude API 代码迁移到更新的模型。**立即阅读 `shared/model-migration.md`** 并按顺序遵循：步骤 0（确认范围 - 在进行任何编辑之前询问哪些文件/目录），步骤 1（对每个文件进行分类），然后针对目标目标的破坏性更改部分。不要总结指南 - 执行它。如果用户没有指定目标模型，请在同一轮中询问要迁移到哪个模型。在应用针对每个目标的更改后，根据 `shared/prompt-audit.md` 审计范围内的提示文本、工具描述和请求代码 - 为源模型编写的提示是每次迁移的一部分，并且它不会宣布自己。 |
| `prompt-audit` | 审计现有的提示、工具描述、技能和代理配置文件（`CLAUDE.md`，规则文件、命令、子代理）以查找过时的模式（“垃圾”）：为旧模型编写的文本，以及存储库已过时或相互矛盾的指令。**立即阅读 `shared/prompt-audit.md`** 并按顺序遵循：步骤 0（建立范围和目标模型 - 从请求和存储库中确定 - 在报告中声明假设，不要停止询问），清单、来源，然后模式扫描。以完整形式提供两个交付成果 - 审计报告（带有 `file:line`、模式、为什么已过时、置信度的发现）和建议的差异 - 而不暂停确认；仅当请求明确要求时才应用编辑。不要总结指南 - 执行它。 |
| `upgrade` | 升级项目的 Anthropic SDK 跨主要版本 - 目前是 Python SDK，`anthropic` 0.x -> 1.x。尾随词可以命名语言和/或范围（`upgrade python`，`upgrade python sdk src/`）。**立即阅读 `python/claude-api/sdk-upgrade.md`** 并按顺序遵循：步骤 0（确认范围，然后建立当前和目标版本 - 必须在您编写固定版 1.x 之前存在），步骤 1 清单，每个编号部分，然后验证和报告。不要总结指南 - 执行它。如果检测到的或命名的语言在此技能中没有 `sdk-upgrade.md`，请说明尚未捆绑该 SDK 的主要版本升级指南，并指向该 SDK 的 CHANGELOG（存储库在 `shared/live-sources.md` 中）；不要从 Python 指南中编造一个。这不是模型迁移 - 要将代码迁移到更新的 Claude 模型，请使用 `migrate`。 |
| `cost-optimize` | 减少现有 Claude API 代码的运行成本，同时不牺牲输出质量。**立即阅读 `shared/cost-optimization.md`** 并按顺序遵循：步骤 0（建立范围、质量标准和基线），令牌配置文件 - 当用户有 Admin API 密钥时通过使用情况和成本 Admin API 测量，当它有这些时从应用程序自己的 `response.usage` 日志测量（询问），否则从代码估计 - 然后是一个按节省排名的短名单杠杆（以美元、账单的百分比或相对桶表示，具体取决于您拥有的哪种数据源），免费收益（缓存、输入令牌卫生、循环卫生、输出令牌卫生、批量）在权衡（预算、工作、模型选择、多模型）；任何杠杆获得位置都成为其自己的差异 - 默认情况下建议，在用户请求并批准后应用并测量它所触及的流量覆盖的评估 - 并且“不推荐更改”是有效结果。两个固定规则：每个使用模型的运行都会花费真实钱，因此首先获得用户的批准；当杠杆的上下文缺失时，与用户交互式地处理它 - 这个工作流程不会预期一次性完成审计。不要总结指南 - 执行它；向用户展示配置文件和排名计划是执行的一部分。 |
| `build-eval` | 帮助用户为其 Claude 驱动的应用程序构建评估集。**立即阅读 `shared/evals/build-eval.md`** 并运行其面试：步骤 0（正在评估什么），步骤 1（获取提示 - 现有评估 / 文本 / 合成），步骤 2（评分方法），步骤 3（可运行脚本 + 测量成本）。在生成评估之前获得用户对输入、评分方法和成本的明确批准。 |
| `preserved-thinking-migration` | 使现有集成与保留思考兼容 - 保留思考块仅在生成它的对话中有效的检查。**立即阅读 `shared/preserved-thinking-migration.md`** 并按顺序遵循：步骤 0（范围、流量类别、平台和模型、执行状态、质量标准、基线），步骤 0.5（使用三个请求的自检证明检查正在运行），步骤 1（捕获请求正文，使用 `shared/preserved-thinking-migration/prefix_diff.py` 差分连续对，扫描代码以查找原因，命名每个编辑和是否故意），步骤 2（在 `thinking-binding-controls-2026-08-01` 标题下使用 `prefix_mismatch_behavior: "drop_block"` 重播测试切片，计算每个对话的新丢弃块数，当存在时读取诊断标题），步骤 3（每个差异一个原因，按推理丢失的顺序 - 默认建议，在用户请求时应用 - 然后重新测量，保留或还原；当存在评估时，三个臂协议），模型切换部分（在 `shared/preserved-thinking-migration/causes.md` 中，带有原因表和保留列表）当 harness 在模型之间路由时，步骤 4（破坏配置文件和更改）。两个固定规则：每个重播都会花费真实钱，因此首先获得用户对测量预算的批准；并且“不推荐更改” - 重播思考并且没有丢弃 - 是一个有效结果。具有仅在较新的 beta 下以追加形式存在的原型的原因（保留尾和后台压缩：`compact-2026-09-04`；相同名称工具更改：`inline-tools-2026-09-15`）在 beta 不可用时，测量和决定，而不是重写。对于 *为什么*（三个步骤检查、追加编辑表），它链接到 `shared/model-migration.md` -> 破坏性更改 3；不要总结指南 - 执行它。 |
| `hillclimb` | 逐次改进用户的应用程序以针对现有的评估。**立即阅读 `shared/evals/eval-hillclimb.md`** 并遵循：步骤 0（确认存在可运行的评估 - 如果不存在，路由到 `build-eval`），步骤 1（要更改什么 / 什么是不允许的），步骤 2（预算 + 停止条件来自测量每轮成本），获得计划批准，然后是读取->提议->应用->运行->记录循环，具有磁盘状态和训练/验证/测试拆分。 |

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

2. **如果检测到多种语言**（例如，同时检测到 Python 和 TypeScript 文件）：

 - 检查用户的当前文件或问题与哪种语言相关
 - 如果仍然不明确，询问：“我检测到 Python 和 TypeScript 文件。您使用哪种语言进行 Claude API 集成？”

3. **如果无法推断语言**（空项目、没有源文件或不受支持的语言）：

 - 使用 AskUserQuestion 带选项：Python、TypeScript、Java、Go、Ruby、cURL/原始 HTTP、C#、PHP
 - 如果 AskUserQuestion 不可用，默认为 Python 示例并注意：“显示 Python 示例。如果需要其他语言，请告诉我。”

4. **如果检测到不受支持的语言**（Rust、Swift、C++、Elixir 等）：

 - 建议从 `curl/` 的 cURL/原始 HTTP 示例，并注意社区 SDK 可能存在
 - 提供显示 Python 或 TypeScript 示例作为参考实现的选项

5. **如果用户需要 cURL/原始 HTTP 示例**，从 `curl/` 阅读。

### 语言特定功能支持

每個以上 SDK 語言都支援 beta 工具執行者和受管代理（beta）- Python (`@beta_tool` 裝飾器), TypeScript (`betaZodTool` + Zod), Java (註解類別), Go (`BetaToolRunner` 在 `toolrunner` 套件中), Ruby (`BaseTool` + `tool_runner`), C# (`BetaToolRunner` + 原生 JSON 模式), PHP (`BetaRunnableTool` + `toolRunner()`); 代码入口點在下方工具使用模式快速參考中。cURL 是原始 HTTP（沒有 SDK 功能）並支援受管代理。

> **受管代理代码示例**: 見下方 `## 受管代理 (Beta)` 節中的閱讀指南。

---

## 應使用哪個界面？

> **從簡單開始。** 預設為滿足您需求的最低級別。單次 API 調用和工作流程處理大多數用例 - 只有在任務真正需要開放式、模型驅動的探索時才使用代理。 "簡單" 意味著擁有的代碼最少：對於托管的、計時的或記憶體回憶的代理，受管代理通常是最低的選項（沒有迴圈代码，沒有狀態文件，沒有計時器），即使它是一個更大的平台。

| 使用案例                                        | 級別            | 推薦界面       | 為何                                                          |
| ----------------------------------------------- | --------------- | ------------------------- | ------------------------------------------------------------ |
| 分類、總結、提取、Q&A  | 單次 LLM 調用 | **Claude API**            | 一個請求，一個響應                                    |
| 批處理或嵌入                  | 單次 LLM 調用 | **Claude API**            | 專用終點                                        |
| 具有代碼控制邏輯的多步管線 | 工作流程        | **Claude API + 工具使用** | 您協調迴圈                                     |
| 自定義代理，使用您自己的工具                | 代理           | **Claude API + 工具使用** | 最大靈活性                                          |
| 服務器管理的有狀態代理，帶有工作區    | 代理           | **受管代理**        | Anthropic 運行迴圈並托管工具執行沙盒                     |
| 持久化、版本化的代理配置              | 代理           | **受管代理**        | 代理是存儲對象；會話釘定到一個版本         |
| 長時間運行的多輪代理，帶有文件掛載  | 代理           | **受管代理**        | 每個會話容器，SSE 事件流，技能 + MCP       |
| 在計時器上運行的代理（cron，“每晚”） | 代理       | **受管代理** - 計時部署 | 部署自動發起會話；沒有客戶端側計時器 |
| 必須達到質量標的代理工作（“直到正確”） | 代理 | **受管代理** - 結果 | 一個獨立的評分員對您的標準進行迭代，直到它通過 |

> **注意：** 當您希望 Anthropic 運行代理迴圈 *並* 托管工具執行的容器時，受管代理是正確的選擇 - 文件操作、bash、代码執行都在每個會話的工作區中運行。如果您想自己托管計算或運行您自己的自定義工具運行時，Claude API + 工具使用是正確的選擇 - 使用工具執行器來進行代理迴圈 - 它的每輪鉤子仍然給您批准門檻、日誌記錄、錯誤攔截和條件執行（見 `shared/tool-use-concepts.md”） - 或者在您想自己擁有整個迴圈時使用手動迴圈。

> **雲供應商訪問。** **AWS 上的 Claude 平台** 是 Anthropic 運營的，具有同日 API 並行性 - 見 `shared/claude-platform-on-aws.md` 進行客戶端設置。對於 **AWS 上的 Claude 平台**、**Amazon Bedrock**、**Google Vertex AI** 和 **Microsoft Foundry** 上的每個功能可用性，見 `shared/platform-availability.md` - 這個表是這個技能的唯一信息來源；不要從其他地方推斷可用性。

### 運行代理：四種方法

一旦您確定您確實需要一個代理（開放式、模型驅動的工具使用），就有四種不同的方法來構建它。兩個獨立問題將它們區分開：**誰提供組件**（代理迴圈 + 上下文管理）和**誰提供部署**（代理運行的基礎設施）。工具執行器和 Claude 代理 SDK 都只提供 *組件* - 您仍然需要自己托管和部署它們 - 這是它們容易混淆的原因。受管代理（CMA）是唯一提供 **組件和受管部署** 的選項；手動迴圈提供什麼也沒有。

| # | 方法 | 您編寫 | 組件和部署 | 可用工具 | 當使用時 |
|---|----------|-----------|----------------------|-----------------|----------|
| 1 | **Claude API - 手動迴圈** | 您自己編寫 `while stop_reason == "tool_use"` 迴圈 | 您構建組件；您托管 | 只有您定義的工具 | 您想擁有 *整個* 迴圈 - 沒有 beta 依賴，或者控制流程工具執行器的每輪鉤子不適合 |
| 2 | **Claude API - 工具執行器** (`client.beta.messages.tool_runner` + `@beta_tool` / `betaZodTool`) | 只需工具函數 | SDK 提供迴圈（**僅組件**）；您托管 | 只有您定義的工具 | 自定義工具代理，不需要手動編寫迴圈（大多數情況）。每輪鉤子仍然給您批准門檻、錯誤攔截、結果修改（例如 `cache_control`）、重試、流式傳輸和壓縮 |
| 3 | **受管代理** (REST, beta) | 代理配置 + 您的工具結果 | Anthropic 提供組件 **並** 托管每個會話的沙盒（**組件 + 部署**） | Anthropic 托管的沙盒（bash、文件、代码執行）+ 技能/MCP + 您的工具 | 您希望 Anthropic 運行迴圈 *並* 托管每個會話的工作區；持久化/版本化配置；長時間運行的會話 |
| 4 | **Claude 代理 SDK** - *獨立產品* (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) | 一個提示 + 選項 | SDK 提供Claude 代码組件 + 預設工具（**僅組件**）；您托管 | 預設的讀取/寫入/編輯/Bash/Glob/Grep/WebSearch/WebFetch + MCP + 子代理 | 您希望一個包含所有功能的編碼/文件系統代理在您自己的基礎設施上運行 |

組件/部署分離是關鍵心智模型：選項 1、2 和 4 都將部署留給您；只有選項 3（CMA）添加了受管部署。選項 1-3 是這個技能生成的；選項 4 是一個具有自己文档的不同庫 - 見下方的消除歧義部分。

> **工具執行器 != Claude 代理 SDK。** 這兩個聽起來相似，但它是不同的包：
> - **工具執行器** 是定期 Anthropic API SDK (`anthropic` / `@anthropic-ai/sdk`) 的一部分，通過 `client.beta.messages.tool_runner` 到達。它自動化請求 -> 執行 -> 迴圈循環 *對於您定義的工具*。沒有預設工具，沒有文件系統訪問，沒有沙盒 - 您提供每個工具並托管計算。它是上面選項 2，`POST /v1/messages` 的薄輔助。
> - **Claude 代理 SDK** (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) 是 Claude 代码打包為庫。它提供預設工具（文件讀取/寫入/編輯、bash、grep、web 搜索），完整的代理迴圈，上下文管理，鉤子，子代理，權限和會話。您調用 `query(prompt, options)` 並它驅動所有內容。
>
> 兩者都是 **僅組件** - 您托管並部署它們。區別在於組件的範圍：工具執行器迴圈遍歷您 *定義* 的工具（使用每輪鉤子進行批准、攔截、結果修改和重試 - 但沒有預設工具）；代理 SDK 是完整的 Claude 代码組件，帶有預設工具。它們都不提供受管部署 - 這是 **受管代理（CMA）** 添加的（Anthropic 托管迴圈和每個會話的沙盒）。
>
> **這個技能涵蓋了 Claude API 和受管代理（選項 1-3）；它不生成 Claude 代理 SDK 代码。** 如果用戶實際上需要 Claude 代理 SDK，請指導他們查看其文档（`code.claude.com/docs/en/agent-sdk`）- 不要用 API 工具執行器替換它，反之亦然。

### 我應該構建代理嗎？

在選擇代理級別之前，檢查所有四個標準：

- **複雜性** - 任務是多步的，難以事先完全規定？（例如，“將這份設計文件轉換為 PR” 與 “從這份 PDF 中提取標題”）
- **價值** - 結果是否值得更高的成本和延遲？
- **可行性** - Claude 能夠完成這種任務類型嗎？
- **錯誤的成本** - 錯誤能否被捕獲並恢復？（測試、審查、撤銷）

如果對這些中的任何一個回答是“否”，請停留在更簡單的級別（單次調用或工作流程）。

---

## 架構

所有內容都通過 `POST /v1/messages`。工具和輸出約束是這個單獨端點的功能 - 不是分離的 API。

**用戶定義的工具** - 您定義工具（通過裝飾器、Zod 模式或原始 JSON），SDK 的工具執行器處理調用 API、執行您的函數，並迴圈直到 Claude 完成為止。對於完全控制，您可以手動編寫迴圈。

**服務器端工具** - Anthropic 托管的工具，在 Anthropic 的基礎設施上運行。代码執行是完全服務器端的（在 `tools` 中聲明，Claude 自动運行代码）。計算機使用可以是服務器主機或自定義主機。

**結構化輸出** - 約束消息 API 响應格式（`output_config.format`）和/或工具參數驗證（`strict: true`）。推薦的方法是 `client.messages.parse()`，它自動驗證響應是否符合您的模式。注意：舊的 `output_format` 參數已過時；在 `messages.create()` 上使用 `output_config: {format: {...}}`。

**支持端點** - 批次（`POST /v1/messages/batches`）、文件（`POST /v1/files`）、令牌計數（`POST /v1/messages/count_tokens` - 見 `shared/token-counting.md`）、模型（`GET /v1/models`, `GET /v1/models/{id}` - 活動能力/上下文窗口發現）為消息 API 請求提供輸入或支持。

---

## 當前模型（緩存：2026-09-25）

| 模型             | 模型 ID            | 上下文        | 輸入 $/1M | 輸出 $/1M |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
| Claude Fable 5.1    | `claude-fable-5-1`      | 1M             | $10.00     | $50.00      |
| Claude Mythos 5.1 (Project Glasswing 唯一) | `claude-mythos-5-1` | 1M | $10.00     | $50.00      |
| Claude Fable 5 | `claude-fable-5` | 1M             | $10.00     | $50.00      |
| Claude Opus 5.5 | `claude-opus-5-5` | 1M | $4.00 | $20.00 |
| Claude Opus 5     | `claude-opus-5`       | 1M             | $5.00      | $25.00      |
| Claude Opus 4.8 | `claude-opus-4-8`  | 1M             | $5.00      | $25.00      |
| Claude Opus 4.7   | `claude-opus-4-7`   | 1M             | $5.00      | $25.00      |
| Claude Opus 4.6   | `claude-opus-4-6`   | 1M             | $5.00      | $25.00      |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 1M | $2.00 | $10.00 |
| Claude Sonnet 5   | `claude-sonnet-5`   | 1M             | $2.00      | $10.00      |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M             | $3.00      | $15.00      |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00      | $5.00       |

**合作夥伴定價：** 上面的價格是 Anthropic 首方 API 價率 - 它們也適用於 Microsoft Foundry 上的 Claude，通過 Microsoft 市場以標準 API 價率計費。Claude 在 Amazon Bedrock 和 Vertex AI 上是合作夥伴運營的，具有不同的定價 - 見 [Bedrock](https://aws.amazon.com/bedrock/pricing/) 或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/pricing#claude-models)。對於 WebFetch，使用 `shared/live-sources.md` 中的定價行。

**總是使用 `claude-opus-5-5`，除非用戶明確指定了不同的模型。** 這是非協商的。不要使用 `claude-sonnet-5-5`、`claude-sonnet-5` 或任何其他模型，除非用戶字面說“使用 sonnet”或“使用 haiku”。從不因成本而下調 - 這是用户的決定，不是您的。描述 Sonnet 的請求（“最便宜的 Sonnet”，“更便宜的 Sonnet”，“最新的 Sonnet”，“最新的 Sonnet”）解析為 `claude-sonnet-5-5`。當第二個更便宜的模型與主模型一起出現時（工作器或子代理線程、批量提取器、LLM 評判員、在顧問下方的執行器），因為用戶要求它或這個技能中的指南要求它 - 或者用戶說“sonnet”或“haiku”而不帶版本，那麼這意味著上面的當前一代（`claude-sonnet-5-5`，`claude-haiku-4-5`）；舊一代 ID，如 `claude-sonnet-5`，僅供那些指定該版本的用戶使用。只有在用戶明確要求 Claude Fable 5.1、"fable" 或 Anthropic 最能干的模型時才使用 `claude-fable-5-1` - 它的 API 行為與 Opus 家族不同（見下文）和定價超過 Opus 級別。**只使用表格中的確切模型 ID 字符串 - 它們是完整的，就像這樣；從不附加日期後綴** (`claude-opus-5-5`，從不 `claude-opus-5-5-20260401` 或您訓練數據中可能記得的其他日期後綴變體）。如果用戶要求表格中沒有的舊模型（例如，“opus 4.5”，“sonnet 3.7”），請閱讀 `shared/models.md` 以獲得確切 ID - 不要自己構建一個。

### Claude Fable 5.1 (`claude-fable-5-1`) - 最廣泛發布的最能干模型

Claude Fable 5.1 是 Anthropic 最廣泛發布的最能干的模型，用於最嚴格的推理和長遠的代理工作；下面的一切也適用於 **Claude Mythos 5.1** (`claude-mythos-5-1`，Project Glasswing - 相同的能力、定價和 API 表面；它運行取決於訪問計劃的安全防護措施，所以下面的 `refusal` 處理也適用於它；Claude Mythos 5 的後繼者，它沒有運行安全分類器）。1M 上下文窗口（最大值也是默認值），128K 最大輸出。與 Opus 級別的關鍵 API 差異見 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 的詳細信息：

- **思考始终开启** - 完全省略 `thinking` 参数（或发送 `{type: "adaptive"}`）。任何其他显式配置都将被拒绝：`{type: "disabled"}` 和 `{type: "enabled", budget_tokens: N}` 都返回 400。使用 `output_config.effort` 控制深度（支持 `low` 到 `xhigh` 和 `max`）。
- **原始的思考链永远不会返回** - 响应包含常规的 `thinking` 块（而不是 `redacted_thinking`）：`display: "summarized"` 返回可读的摘要，`"omitted"`（默认值）将 `thinking` 字段留为空字符串。重放规则：在相同模型上保持思考块不变；其他模型将它们静默丢弃（不收费 - 无需移除；Claude Mythos 5.1 反而会读取它们）；详情见 `shared/model-migration.md`。
- **分词器** - 与 Opus 4.8 相同（与 Opus 4.7 一起引入）。从 Opus 4.7/4.8 迁移时，分词计数大致不变；每条分词的定价不同。从 Opus 4.6、Sonnet、Haiku 或更早版本迁移，使用 `count_tokens` 重新基线（Opus 4.7 的分词器使用约 1×-1.35× 的分词）。
- **`refusal` 停止原因 - 处理它，并默认选择回退** - 安全分类器可能拒绝请求（HTTP 200，`stop_reason: "refusal"`，带有 `stop_details` 类别）；在读取 `content` 之前始终检查 `stop_reason`。**当您编写 `claude-fable-5-1`、`claude-opus-5-5`、`claude-opus-5` 或 `claude-sonnet-5-5` 代码时，默认包含服务器端的 `fallbacks` 参数**（对于 `claude-sonnet-5-5`，仅 `"default"` 形式，仅在 Claude API 上；在其他平台上使用下面的 SDK 中间件，除非请求发送 `between_tools`：仅 Claude Sonnet 5.5 接受它，中间件在回退模型上重新发送相同的请求体，因此您需要自己编写重试并发送，不使用 `between_tools` - 见 `shared/model-migration.md` -> Migrating to Claude Sonnet 5.5 -> Safeguards and fallback）。最简单形式：`betas: ["server-side-fallback-2026-07-01"]` + `fallbacks: "default"`，它按拒绝类别路由，因此您无需维护模型列表。（旧数组形式 - `betas: ["server-side-fallback-2026-06-01"]` + `fallbacks: [{"model": "claude-opus-4-8"}]` 仍然有效；Claude API 和 Claude Platform on AWS - 在 Bedrock、Vertex 和 Foundry 上，使用 SDK 的客户端 `BetaRefusalFallbackMiddleware` + `BetaFallbackState`）。告诉用户您已启用它；仅在它们拒绝时才移除。完整语义（计费、中途拒绝、信用重新定价）在 `shared/model-migration.md` -> refusal 部分。**多语言代码示例在 `{lang}/claude-api/README.md` § Refusal Fallbacks 仅涵盖数组形式** - 对于 `"default"` 模式，遵循 `shared/model-migration.md` -> Migrating to Claude Opus 5 -> New API features 并将 `fallbacks: [{...}]` 交换为 `fallbacks: "default"` 加上 `-2026-07-01` 标头；其余请求保持不变。
- **无助手预填充** - 与 4.6 及以上系列的其余部分相同。
- **需要 30 天数据保留** - 除非得到 Anthropic 的明确授权，Claude Fable 5.1 在零数据保留下不可用；来自保留配置不符合要求的组织的请求返回 `400 invalid_request_error`。
- **更长的回合，不同的提示** - 在硬任务上的单个请求可以运行很多分钟（计划超时/流式传输/进度 UX）；努力扫描应包括低/中用于常规工作；为先前模型编写的提示通常过于具体，会降低输出质量。见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 -> Behavioral shifts (prompt-tunable) 获取推荐的提示片段。
- **Claude Fable 5 (`claude-fable-5`，仍在服务）在同一级别，每条分词价格相同。** 与 Claude Fable 5 相同，有三个破坏性变更 - 强制工具使用 (`tool_choice` `any` / `tool`) 返回 400（使用 `auto` + 提示指令，`strict: true` 用于 schema 合法的参数，或结构化输出）；思考块绑定到生成模型（其他模型丢弃它们，不收费）；以及编辑早期回合使思考块无效（“保留思考”；在 2026-08-31 或之后创建的新账户在所有平台上对编辑历史返回 400，且执行范围由每个模型决定，Claude Mythos 5.1 不执行此检查。使每个 harness 不可变并运行三步检查；选择 beta 的控制开关在 Claude API、Claude Platform on AWS、Bedrock 和 Vertex 上 - Foundry 未经证实，见 `shared/platform-availability.md`）- 加上每条消息的 `effort`（beta `mid-conversation-output-config-2026-07-01`，Claude Opus 5 和 Claude Opus 5.5 也支持）、回合范围的 `clear_at: "next_user_message"` 系统消息（beta）、`thinking.display: "updates"` 进度笔记（beta，所有平台）、缓存读取 $0.25/MTok 和内容来源。覆盖模型 - ZDR 组织与 Claude Fable 5 相同返回 `400 invalid_request_error`（仅 ZDR 需要得到 Anthropic 的明确授权）；无优先级层级。与 Claude Fable 5 相同的分词器。见 `shared/model-migration.md` -> Migrating to Claude Fable 5.1 from Claude Fable 5。

### Claude Opus 5.5 (`claude-opus-5-5`) - 当前 Opus 和默认模型

Opus 系列的继任者，价格更低（$4 / $20 per MTok，缓存读取 $0.20），相同 1M 上下文 / 128K 输出 / 分词器 / 功能集。Claude Opus 5 上运行的代码有四个破坏性变更：**思考无法禁用**（`{type: "disabled"}` 和 `budget_tokens` 在所有努力级别都返回 400 - 努力是唯一控制项，其**默认是 `medium`**，比 Claude Opus 5 的 `high` 低一个级别，因此需要显式设置）；**强制的 `tool_choice` `any`/`tool` 返回 400**（使用 `auto` + `strict: true` 并从提示中引导，或结构化输出）；**思考块绑定到模型和对话**（保留思考：仅 Claude Fable 5.1 / Claude Mythos 5.1 在 Claude API 上读取其块，因此回退到 Claude Opus 5 不带它们运行；在 2026-08-31 或之后创建的账户在 Claude API 和 Amazon Bedrock 上强制执行历史编辑检查）；以及在 Claude API 和 Google Cloud 上仅通过 `computer_toolset_20260801` 使用计算机（`computer_20251124` 在那里返回 400；Amazon Bedrock 仍然接受它）。工具调用之间的文本作为进度更新 `thinking` 块返回（默认为空 - 设置 `display: "updates"`）。更广泛的安全分类器：`bio` 和 `reasoning_extraction` 加入 `cyber`。快速模式仅限 Claude API，$8 / $40 per MTok（2x 标准）。见 `shared/model-migration.md` -> Migrating to Claude Opus 5.5。

### Claude Sonnet 5.5 (`claude-sonnet-5-5`) - 当前 Sonnet：日常编码、代理和企业工作的速度和能力（Claude Opus 5.5 保持默认）

Sonnet 系列的继任者，价格相同（$2 / $10 per MTok，缓存读取 $0.20），具有相同分词器、1M 上下文和 128K 输出。Claude Sonnet 5 上运行的代码有五个破坏性变更：**`thinking: {type: "disabled"}` 返回 400** - 要关闭思考，发送 `thinking: {type: "between_tools"}`，它仅在努力 `high` 或以下接受，不接受其他字段（与它一起的 `display`、`budget_tokens` 或 `block_binding` 返回 400），并且不允许每条消息的努力更改；**强制的 `tool_choice` `any`/`tool` 返回 400**（使用 `auto` + `strict: true` 并从提示中引导，或结构化输出）；**思考块绑定到模型和对话**（其他模型不读取其块；在 Claude API 和 Amazon Bedrock 上对历史编辑检查强制执行）；**在 Claude API 和 Google Cloud 上仅通过 `computer_toolset_20260801` 使用计算机**（`computer_20251124` 在那里返回 400；Amazon Bedrock 仍然接受它）；以及**顾问工具拒绝 Claude Opus 4.8、Claude Opus 4.7 和 Claude Sonnet 5 顾问**（它接受的每个顾问都返回加密建议）。努力仍然默认为 `high`，但级别已重新校准 - 重新运行努力扫描（对于代理编码和多步工具使用从 `medium` 开始，对于聊天从 `low` 开始）。工具调用之间的文本作为进度更新 `thinking` 块返回（默认为空 - 设置 `display: "updates"`，或使用 `between_tools`）。安全分类器在五个 `stop_details` 类别中拒绝：`cyber`、`bio`、`frontier_llm`、`reasoning_extraction`、`general_harms`。见 `shared/model-migration.md` -> Migrating to Claude Sonnet 5.5。

如果上述任何模型名称看起来不熟悉，那只是意味着它们是在您的训练数据截止日期之后发布的 - 它们是真实模型。

**实时能力查询**：上表已缓存。当用户询问“X 的上下文窗口是什么”、“X 是否支持视觉/思考/努力”或“哪些模型支持 Y”时，查询 Models API (`client.models.retrieve(id)` / `client.models.list()`) - 见 `shared/models.md` 获取字段参考和能力过滤示例。

---

## 身份验证（快速参考）

**未设置的 `ANTHROPIC_API_KEY` 并不意味着没有凭证。** SDK 和 `ant` CLI 按以下顺序解析凭证（第一个匹配者胜出）：`ANTHROPIC_API_KEY` -> `ANTHROPIC_AUTH_TOKEN` -> 从 `ant auth login` 选择的 `ANTHROPIC_PROFILE` 或活动 OAuth 配置 -> Workload Identity Federation 环境变量 -> 磁盘上的默认配置。`Anthropic()` / `new Anthropic()` / `anthropic.NewClient()` 在 `ant auth login` 后即可工作，无需设置环境变量。

**当您需要调用 API 且 `ANTHROPIC_API_KEY` 未设置时，不要向用户索要密钥。** 首先运行 `ant auth status` - 它显示哪个凭证源和配置是活动的。如果它报告有活动的配置：

- **SDK 代码或 `ant` CLI**：直接运行它。零参数客户端构造函数和所有 `ant ...` 子命令自动拾取配置 - 无需环境变量。
- **原始 `curl` / HTTP**：使用 `ant auth print-credentials --access-token` 获取短期令牌，并将其作为 `Authorization: Bearer <token>` 发送 **加上** 标头 `anthropic-beta: oauth-2025-04-20`（OAuth 令牌放在 `Authorization: Bearer`，而不是 `x-api-key:` - 从 API 密钥转换 curl 是标头更改，不是密钥交换）。始终传递 `--access-token`；无标志形式打印 JSON，而不是裸令牌。

仅在 `ant auth status` 报告没有活动凭证源（或 `ant` 本身未安装）时才向用户索要密钥。建议 `ant auth login` 作为首选选项 - 它在 `~/.config/anthropic/` 下存储一个配置文件，SDK 自动读取它 - 以及导出的 `ANTHROPIC_API_KEY` 作为替代方案。

完整身份验证细节（命名配置文件、范围、API 密钥阴影配置文件陷阱、刷新令牌过期）：`shared/anthropic-cli.md`。

---

## 思考 & 努力（快速参考）

在当前模型上使用自适应思考（`thinking: {type: "adaptive"}`），Haiku 4.5 除外，它仍然使用 `budget_tokens`（下表）- Claude 动态决定何时以及多少思考。每模型规则：

| 模型 | 思考配置 | 省略 `thinking` | `budget_tokens` | 采样 (`temperature`/`top_p`/`top_k`) | 努力级别 |
|---|---|---|---|---|---|
| Fable 5 / Claude Fable 5.1（以及对应的 Mythos） | `{type: "adaptive"}` 或省略；显式 `{type: "disabled"}` 返回 400 - 省略参数（Claude Fable 5.1 / Claude Mythos 5.1 在强制的 `tool_choice` `any`/`tool` 上也返回 400；Claude Fable 5.1 在重放思考块时运行保留思考的历史编辑检查，Claude Mythos 5.1 不运行） | 运行自适应（思考始终开启） | 移除 - `{type: "enabled", budget_tokens: N}` 返回 400 | 移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Claude Opus 5.5 | `{type: "adaptive"}` 或省略；`{type: "disabled"}` 和 `{type: "enabled", budget_tokens}` 在 **所有** 努力级别返回 400 - 省略参数并降低努力（在强制的 `tool_choice` `any`/`tool` 上也返回 400，并运行保留思考 - 见 `shared/model-migration.md` -> Migrating to Claude Opus 5.5） | 运行 **自适应** | 移除 - 400 | 移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` - **默认 `medium`**（不是 `high`）；支持每条消息的努力（beta） |
| Claude Opus 5 | `{type: "adaptive"}` 或省略；`{type: "disabled"}` 仅在努力 `high` 或以下接受 - 在 `xhigh`/`max` 返回 400，并见禁用思考的陷阱下方 | 运行 **自适应**（思考默认开启 - 与 Opus 4.8/4.7 不同） | 移除 - 400 | 移除 - 400 | `low`-`max`（所有五个） |
| Opus 4.8 / 4.7 | `{type: "adaptive"}` 是唯一开启模式；`{type: "disabled"}` 接受 | 运行 **无** 思考 - 显式设置 `{type: "adaptive"}` | 移除 - 400 | 移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Claude Sonnet 5.5 | `{type: "adaptive"}` 或省略；`{type: "disabled"}` 返回 400 - 要关闭思考，发送 `{type: "between_tools"}`（无其他字段；在 `xhigh`/`max` 返回 400；努力不能用它在中途更改对话）（在强制的 `tool_choice` `any`/`tool` 上也返回 400，并运行保留思考 - 见 `shared/model-migration.md` -> Migrating to Claude Sonnet 5.5） | 运行 **自适应** | 移除 - 400 | 非默认值 - 400 | `low`/`medium`/`high`/`xhigh`/`max` - 默认 `high`，级别从 Claude Sonnet 5 重新校准；在开启思考时支持每条消息的努力（beta） |
| Sonnet 5 | `{type: "adaptive"}` 是唯一开启模式；`{type: "disabled"}` 接受 | 运行自适应 | 移除 - 400 | 移除 - 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Opus 4.6 / Sonnet 4.6 | `{type: "adaptive"}`（推荐；自动启用交错思考，无 beta 标头） | 显式设置 `{type: "adaptive"}` | 已弃用 - 新代码中不要使用；仅作为过渡逃生（见下方） | 允许 | `low`/`medium`/`high`/`max`（`xhigh` 随 Opus 4.7 到来） |
| Haiku 4.5；较旧模型（Sonnet 4.5、...）仅如果明确请求 | `{type: "enabled", budget_tokens: N}` | 无思考 | 必须为思考提供；必须小于 `max_tokens`，最小 1024 - 否则出错 | 允许 | `effort` 在 Opus 4.5 上工作（`low`/`medium`/`high` 仅 - 无 `xhigh`/`max`）；在 Sonnet 4.5 / Haiku 4.5 上出错 |

Opus 4.8 保留与 4.7 相同的请求表面（无新的破坏性变更）- 见 `shared/model-migration.md` -> Migrating to Opus 4.8 获取行为重新调整，以及 -> Migrating to Opus 4.7 获取从 4.6 或更早版本迁移时的完整破坏性变更列表。在禁用思考时，Opus 4.8 可能将更长的推理写入可见响应 - 保持自适应思考开启，或添加仅最终答案的指令（见迁移指南）。

- **努力程度（GA，无beta头部）**：`output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}` - 在`output_config`内部，而不是顶层；在当前所有模型上默认为`high`（等同于省略它），除了Claude Opus 5.5，其默认值为`medium`（如上表所示）- 在那里明确设置它。控制思考深度和总体token消耗；与自适应思考结合，以获得最佳成本质量权衡。`xhigh`（在Opus 4.7中添加，位于`high`和`max`之间）是Fable 5 / Opus 4.7/4.8 / Sonnet 5上大多数编码和代理用例的最佳设置，也是Claude Code中的默认值；在这些模型上，努力程度比任何先前同级别的模型都更重要 - 在迁移时重新调整它，并使用完整的任务规范在前端运行长期/代理任务，在`high`/`xhigh`。对智能敏感的工作，使用至少`high`，当正确性比成本更重要时使用`max`，对于子代理或简单任务使用`low` - 较低的努力程度意味着更少的工具调用和更集中的工具调用，前置信息更少，确认更简洁（`high`通常是平衡质量和token效率的甜点）。
- **选择努力程度（成本调整）**：努力程度是第一个质量权衡杠杆，在免费获胜（首先缓存）之后 - 它在单个模型内权衡彻底性相对于token消耗，顶部的范围只在硬问题上才值得其成本（仅在测量显示在较低级别下有空间时才提高到`max`）。哪些工作负载能偿还更高的努力程度是工作负载的属性：编码和长期/代理工作对此反应强烈；聊天、分类和高容量或延迟敏感的路由通常不会，并且在`low`下表现良好，`medium`是成本节约的降级步骤，在质量保持的情况下（上述每级默认值涵盖了其余部分）。在提高默认值之前，在真实请求样本上进行测量，并针对路由而不是全局进行微调。在构建多模型成本级联之前，首先测量更简单的替代方案 - 在相同任务上具有较低努力的最新模型的最能干的模型：在Fable 5上，较低的努力程度通常超过先前模型的`xhigh`，并且一个模型意味着一个缓存命名空间（缓存是模型范围的，因此级联放弃了跨其模型的缓存重用；对话中途的顶层`effort`更改仍然使消息缓存失效，尽管每条消息的努力程度系统消息在Claude Fable 5.1 / Claude Mythos 5.1 / Claude Opus 5.5 / Claude Opus 5 / Claude Sonnet 5.5（带自适应思考）- `shared/prompt-caching.md` § 无效化层次结构）。按完成的任务成本而不是每个请求的成本进行判断 - 一个更便宜的请求如果需要更多回合或重试才能完成工作，则不便宜。有关按工作负载测量的努力/成本权衡以及完整杠杆顺序，请参阅`shared/cost-optimization.md` § 2.6。
- **思考显示 - Fable 5 / Claude Fable 5.1 / Mythos 5 / Claude Mythos 5.1 / Opus 5.5 / 5 / 4.8 / 4.7 / Sonnet 5 / Claude Sonnet 5.5默认为`omitted`**：`display: "summarized"`返回推理的可读摘要；`"omitted"`（在所有十个上都为默认值 - 与Opus 4.6和Sonnet 4.6相比，当时它是`"summarized"`）流式传输带有空文本的`thinking`块。`display`仅控制可见性 - 思考在任何设置下都会发生并按相同的方式计费；任何模型都不会暴露原始的思考链。如果您向用户流式传输推理，默认情况下看起来像输出之前的长时间暂停 - 明确设置`thinking: {type: "adaptive", display: "summarized"}`。 （与显示无关，在相同模型上继续时回显不变的思考块；其他模型静默地忽略它们（Claude Fable 5.1 / Claude Mythos 5.1读取它们，Claude Sonnet 5.5读取Claude Sonnet 5，Opus 4.8，Haiku 4.5和更早模型的块）- 请参阅迁移指南。）在Claude Fable 5.1 / Claude Mythos 5.1 / Claude Fable 5 / Claude Opus 5.5 / Claude Sonnet 5.5上，`display: "updates"`（beta `thinking-display-updates-2026-08-18`，每个平台）隐藏推理，如`"omitted"`，但返回模型在工具调用之间的进度笔记作为简短的`thinking`块摘要 - 请参阅`shared/model-migration.md` -> 从Claude Fable 5迁移到Claude Fable 5 -> 新API功能。
- **当用户要求“扩展思考”，“思考预算”或`budget_tokens`时**：始终使用Fable 5/5.1，Opus 5.5，5，4.8，4.7或4.6，并使用`thinking: {type: "adaptive"}` - 固定思考token预算的概念已弃用，自适应思考取代了它。不要在新4.6/4.7/4.8代码中使用`budget_tokens`，也不要因为用户提到了它就切换到较旧的模型。 *渐进式迁移例外*：`budget_tokens`仅在Opus 4.6和Sonnet 4.6上仍然有效，作为一个过渡性逃生通道，用于在您调整`effort`之前需要硬token上限的现有代码 - 请参阅`shared/model-migration.md` -> 过渡性逃生通道。它在Fable 5/5.1，Opus 5.5/5/4.7/4.8和Sonnet 5上已完全移除。

---

## 压缩（快速参考）

**Beta，Fable 5/5.1，Opus 5.5，Opus 5，Opus 4.8，Opus 4.7，Opus 4.6，Sonnet 5.5，Sonnet 5，和Sonnet 4.6。** 对于可能超过1M上下文窗口的长时间运行对话，启用服务器端压缩。API在接近触发阈值时自动总结先前的上下文（默认：150K tokens）。需要beta头部`compact-2026-01-12`。

**关键**：在每次回合时将`response.content`（而不仅仅是文本）附加到您的消息中。响应中的压缩块必须保留 - API使用它们在下一个请求中替换压缩的历史记录。仅提取文本字符串并附加将静默地丢失压缩状态。

有关代码示例，请参阅`{lang}/claude-api/README.md`（压缩部分）。完整文档通过WebFetch在`shared/live-sources.md`中。

---

## 提示缓存（快速参考）

**前缀匹配。** 前缀中任何字节的变化都会使它之后的所有内容失效。渲染顺序是`tools` -> `system` -> `messages`。首先保持稳定内容（冻结的系统提示，确定性工具列表），然后将易变内容（时间戳，每次请求的ID，变化的问题）放在最后一个`cache_control`断点之后。

**对话中期的操作员指令**（Claude Opus 5，Claude Opus 5.5，Claude Opus 4.8，Claude Fable 5，Claude Fable 5.1，Claude Mythos 5，Claude Mythos 5.1，Claude Sonnet 5.5；不包括Claude Sonnet 5；无beta头部）：将`{"role": "system", ...}`附加到`messages[]`，而不是编辑顶层`system`。保留缓存的对话前缀，并且是安全的提示注入操作通道。请参阅`shared/prompt-caching.md` § 对话中期的系统消息。

**顶层自动缓存**（在`messages.create()`上`cache_control: {type: "ephemeral"}`）是最简单的选项，当您不需要细粒度位置时。最多4个断点每个请求。可缓存前缀的最小长度是模型相关的（512-4096 tokens - 请参阅`shared/prompt-caching.md` § API参考）- 较短的前缀将静默地不会缓存。

**使用`usage.cache_read_input_tokens`进行验证** - 如果它在重复请求中为零，则存在静默无效器（系统提示中的`datetime.now()`，未排序的JSON，变化的工具集）。

有关放置模式，架构指南和静默无效器审计清单：阅读`shared/prompt-caching.md`。特定语言的语法：`{lang}/claude-api/README.md`（提示缓存部分）。

---

## 快速模式（快速参考）

**研究预览，Claude Opus 5 / Claude Opus 5.5 / Opus 4.8仅限** - Claude API和Managed Agents，不包括Bedrock / Google Cloud / Foundry。Opus 4.7快速模式已移除：在4.7上`speed: "fast"`返回错误。Claude Opus 5上的快速模式定价为$10 / $50每个MTok；在Claude Opus 5.5上，$8 / $40。快速模式以溢价价格运行相同的模型，每秒输出tokens高达2.5倍。在每次请求上都需要三件事：使用**beta**消息端点（`client.beta.messages....`），传递beta标志`fast-mode-2026-02-01`，并将`speed: "fast"`作为顶层请求参数设置（不是头部，不是在`extra_body`中）。

```python
client.beta.messages.create(
    model="claude-opus-5-5", max_tokens=4096,
    speed="fast", betas=["fast-mode-2026-02-01"],
    messages=[...],
)
```

| 语言 | Beta标志 | 速度参数 |
|---|---|---|
| Python | `betas=["fast-mode-2026-02-01"]` | `speed="fast"` |
| TypeScript / Ruby | `betas: ["fast-mode-2026-02-01"]` | `speed: "fast"` |
| Go | `[]anthropic.AnthropicBeta{anthropic.AnthropicBetaFastMode2026_02_01}` | `Speed: anthropic.BetaMessageNewParamsSpeedFast` |
| Java | `.addBeta(AnthropicBeta.FAST_MODE_2026_02_01)` | `.speed(MessageCreateParams.Speed.FAST)` |
| C# | `Betas = ["fast-mode-2026-02-01"]` | `Speed = Speed.Fast` (`Anthropic.Models.Beta.Messages`) |
| PHP | `betas: ['fast-mode-2026-02-01']` | `speed: 'fast'` |
| cURL | `anthropic-beta: fast-mode-2026-02-01` 头部 | `"speed": "fast"` 在正文 |

`response.usage.speed`报告使用了哪个速度。快速模式有自己的速率限制，与标准Opus分开；在429时，要么在`retry-after`延迟后重试，要么放弃`speed`并回退到标准（注意：切换速度使提示缓存失效）。在不使用Batch API，优先级层，Claude Platform on AWS或第三方平台的情况下不可用。

**优先级层不是在所有当前模型上都支持。** 它在Claude Fable 5，Opus 4.8和较旧的当前模型上支持，但在Claude Opus 5.5，Claude Opus 5，Claude Sonnet 5，Claude Sonnet 5.5，Claude Fable 5.1，Claude Mythos 5.1，Claude Mythos 5和Mythos Preview中排除 - 命名其中一个的优先级层请求将失败验证。

---

## 任务预算（快速参考）

**Beta，Claude Opus 5 / Claude Opus 5.5 / Fable 5 / Claude Fable 5.1（启动时确认）/ Claude Sonnet 5.5 / Opus 4.8 / 4.7（不包括Claude Sonnet 5）。** 任务预算为Claude提供一个token上限，用于代理循环，以便它自我调节并优雅地完成，而不是被切断 - 这与`max_tokens`不同，`max_tokens`是模型不知道的强制每响应上限。最小`total`：20,000。在`client.beta.messages.stream(...)`内部设置`task_budget`，并使用beta标志`task-budgets-2026-03-13` - 使用流式传输，以便大型`max_tokens`不会导致HTTP超时（完整详细信息：`shared/model-migration.md` -> 任务预算）：

```python
with client.beta.messages.stream(
    model="claude-opus-5-5", max_tokens=128000,
    output_config={"effort": "high", "task_budget": {"type": "tokens", "total": 64000}},
    betas=["task-budgets-2026-03-13"],
    messages=[...], tools=[...],
) as stream:
    response = stream.get_final_message()
```

`task_budget`字段：`type`（始终为`"tokens"`），`total`，以及可选的`remaining`（默认为`total`）。服务器在生成期间向Claude注入倒计时标记；预算计算Claude生成的和它这轮读取的工具结果 - **不是**您每次请求重新发送的完整历史记录。这与**Managed Agents会话预算**不同 - 那些是硬的，以美元计价的，平台强制执行的针对单个CMA会话的限额（`shared/managed-agents-core.md` § 会话预算）；任务预算是建议性的，以token计价。

**观察支出**：如果您希望在循环迭代中累积`response.usage.output_tokens`（以及您附加的工具结果块的token计数），以便显示进度。在正常循环中不要在`remaining`中设置值 - 服务器自己跟踪倒计时，并且在重新发送完整历史记录时，传递客户端计算的`remaining`也会低估预算。**仅当**您在请求之间压缩或重写历史记录并且服务器无法再推导出先前的支出时，**才**传递`remaining`。

---

## 提供商客户端（快速参考）

当针对第三方平台上的Claude时，使用该平台的专用客户端类 - 而不是带有`base_url`覆盖的第一方`Anthropic()`客户端。构建后，客户端暴露与第一方SDK相同的`messages.create` / `.stream`表面。

### Amazon Bedrock

使用**Mantle**客户端（Messages-API Bedrock端点）。Bedrock模型ID需要一个`anthropic.`前缀（例如`"anthropic.claude-opus-5-5"`）。区域是必需的。

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicBedrockMantle` -> `AnthropicBedrockMantle(aws_region="...")` |
| TypeScript | `import { AnthropicBedrockMantle } from "@anthropic-ai/bedrock-sdk"` -> `new AnthropicBedrockMantle({ awsRegion: "..." })` |
| Go | `bedrock.NewMantleClient(ctx, bedrock.MantleClientConfig{ AWSRegion: "..." })` |
| Java | `AnthropicOkHttpClient.builder().backend(BedrockMantleBackend.fromEnv()).build()` (from `com.anthropic.bedrock.backends`) |
| C# | `new AnthropicBedrockMantleClient(new() { AwsRegion = "..." })` (package `Anthropic.Bedrock`) |
| PHP | `use Anthropic\Bedrock\MantleClient;` -> `new MantleClient(awsRegion: '...')` |
| Ruby | `Anthropic::BedrockMantleClient.new(aws_region: "...")` |

`AnthropicBedrock` / `BedrockClient` / `BedrockBackend`（没有`Mantle`）是遗留的`bedrock-runtime` InvokeModel路径 - 新代码请优先使用Mantle客户端。

### Microsoft Foundry

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicFoundry` -> `AnthropicFoundry(api_key=..., resource="...")` |
| TypeScript | `import AnthropicFoundry from "@anthropic-ai/foundry-sdk"` -> `new AnthropicFoundry({ ... })` |
| Java | `AnthropicOkHttpClient.builder().backend(FoundryBackend.fromEnv()).build()` (from `com.anthropic.foundry.backends`) |
| C# | `new AnthropicFoundryClient(new AnthropicFoundryApiKeyCredentials(...))` (package `Anthropic.Foundry`) |
| PHP | `Foundry\Client::withCredentials(...)` |

Go和Ruby SDK目前不支持Foundry。对于Ruby，使用标准`Anthropic::Client.new(base_url: "<foundry endpoint>")`作为后备（Entra ID认证未内置）。对于Claude Platform on AWS，请参阅`shared/claude-platform-on-aws.md`。

### Google Cloud Vertex AI

两个必需的构造函数参数：GCP `project_id`和`region`。Vertex模型ID**不带前缀** - 当前一代模型（Opus 5.5/5/4.8/4.7/4.6，Sonnet 5.5，Sonnet 5，Sonnet 4.6）使用纯第一方ID（例如`"claude-opus-5-5"`）；日期快照模型使用`@`版本分隔符（例如`claude-opus-4-5@20251101`，**不是**`claude-opus-4-5-20251101`）。认证是GCP ADC（`gcloud auth application-default login`）；没有Anthropic API密钥。`region`可以是`"global"`（推荐），一个多区域（`"us"`/`"eu"`），或特定区域。构建后，使用相同的`messages.create` / `.stream`表面。

| 语言 | 客户端 |
|---|---|
| Python | `from anthropic import AnthropicVertex` -> `AnthropicVertex(project_id="...", region="...")` (安装`"anthropic[vertex]"`) |
| TypeScript | `import { AnthropicVertex } from "@anthropic-ai/vertex-sdk"` -> `new AnthropicVertex({ projectId, region })` |
| Go | `import "github.com/anthropics/anthropic-sdk-go/vertex"` -> `anthropic.NewClient(vertex.WithGoogleAuth(ctx, region, projectID))` |
| Java | `AnthropicOkHttpClient.builder().backend(VertexBackend.builder().region("...").project("...").build()).build()` (from `com.anthropic.vertex.backends`) |
| C# | `new AnthropicClient { Backend = new VertexBackend(projectId, region) }` (package `Anthropic.Vertex`) |
| PHP | `use Anthropic\Vertex;` -> `Vertex\Client::fromEnvironment(location: '...', projectId: '...')` - 注意`location`，不是`region` |
| Ruby | `Anthropic::VertexClient.new(region: "...", project_id: "...")` |

---

## 上下文编辑（快速参考）

**Beta。** 上下文编辑在模型看到它之前清除对话中的旧工具结果或思考块；它**不是**压缩（压缩会总结）。在`client.beta.messages.*`上使用beta `context-management-2025-06-27`时，传递`context_management.edits`与策略类型：

```python
client.beta.messages.create(
    model="claude-opus-5-5", max_tokens=4096,
    betas=["context-management-2025-06-27"],
    context_management={"edits": [{"type": "clear_tool_uses_20250919"}]},
    tools=[...], messages=[...],
)
```

策略类型：`clear_tool_uses_20250919`（清除旧的工具结果；可选 `clear_tool_inputs: true` 也会清除工具使用的参数）和 `clear_thinking_20251015`（清除思考块）。**不要**使用 `compact_20260112` 或 beta `compact-2026-01-12` —— 这些是独立的压缩功能。

---

## 会话中系统消息（快速参考）

**Claude Opus 5、Claude Opus 5.5、Claude Opus 4.8、Claude Fable 5、Claude Fable 5.1、Claude Mythos 5、Claude Mythos 5.1 和 Claude Sonnet 5.5；不包括 Claude Sonnet 5；没有 beta 头部。** 将 `{"role": "system", "content": "..."}` 添加到 `messages` 数组（而不是顶层 `system` 字段）中，以在会话中添加操作员指令，而不会使缓存的头部无效。使用常规的 `client.messages.create` —— 没有 beta。会话中的系统消息必须跟在 `user` 消息（或以服务器工具使用结束的 `assistant` 消息）之后，并且必须是 `messages` 中的最后一个条目，或者后面跟着一个 `assistant` 轮次 —— 它不能是 `messages[0]`。可用性：`shared/platform-availability.md`。参见 `shared/prompt-caching.md` § 会话中系统消息。Claude Fable 5.1 随附的 beta 扩展：`output_config: {effort: ...}` 与 `content: []` 在该点更改努力程度，而无需重置缓存（beta `mid-conversation-output-config-2026-07-01`；Claude Fable 5.1、Claude Mythos 5.1、Claude Opus 5.5、Claude Opus 5 和 Claude Sonnet 5.5 带有思考；Claude API 和 Google Cloud）。仅包含努力的消息（空的 `content`）可以遵守上述放置规则——它可以位于 `messages` 中的任何位置，包括第一个或位于一个 assistant 轮次和下一个 user 轮次之间；规则适用于文本和 `clear_at` 消息。对于每轮提醒，给消息 `clear_at: "next_user_message"`（beta `mid-conversation-system-clear-at-2026-08-21`）：它在下一轮显示，然后保持在记录中清除——永远不会删除早期副本（在 Claude Fable 5.1、Claude Opus 5.5 和 Claude Sonnet 5.5 中删除一个会使后续思考块无效）；没有 beta 时，工具结果后的文本块会保留早期副本。参见 `shared/model-migration.md` -> 从 Claude Fable 5 到 Claude Fable 5.1 的迁移 -> 新 API 功能。

---

## 管理代理（Beta）

**管理代理** 是一个第三方界面：由服务器管理的有状态代理，具有 Anthropic 托管的工具执行。您创建一个持久的、版本化的代理配置（`POST /v1/agents`），然后启动引用它的会话。每个会话都会为代理的工作空间配置一个容器——bash、文件操作和代码执行都在那里运行；代理循环本身在 Anthropic 的编排层上运行，并通过工具作用于容器。会话流式传输事件；您将消息和工具结果发送回去。

可用性：`shared/platform-availability.md`。对于 Bedrock / Vertex / Foundry 上的代理（Managed Agents 不受支持），请使用 Claude API + 工具使用。

**强制流程：** 代理（一次）-> 会话（每次运行）。`model`/`system`/`tools` 存在于代理上，永远不会存在于会话上。参见 `shared/managed-agents-overview.md` 以获取完整的阅读指南、beta 头部和陷阱。

**Beta 头部：** `managed-agents-2026-04-01` —— SDK 会自动为所有 `client.beta.{agents,environments,sessions,vaults,deployments,deployment_runs}.*` 调用设置此头部。内存存储使用 `agent-memory-2026-07-22`，该 SDK 在 `client.beta.memory_stores.*` 调用上设置它；在内存存储请求中发送两个头部会返回 400。文件 API 和 Skills API 已退出 beta —— 不需要 beta 头部（请参阅上面的 API Drift 表格以获取迁移指南）。

**子命令** —— 直接使用 `/claude-api <subcommand>` 调用：

| 子命令 | 操作 |
|---|---|
| `managed-agents-onboard` | 引导用户从头开始设置管理代理。**立即阅读 `shared/managed-agents-onboarding.md`** 并遵循其访谈脚本：**描述 -> 配置代理（建议，不要审问）-> 环境 -> 会话**（与控制台快速入门相同的弧线，身份验证延迟到会话步骤）—— 默认值和内联建议会完成工作，并在发出任何代码之前进行无声的可行性检查（工作与工具/凭据/数据）。不要总结——运行访谈。 |

**阅读指南：** 从 `shared/managed-agents-overview.md` 开始，然后是主题相关的 `shared/managed-agents-*.md` 文件（核心、环境、工具、事件、结果、多代理、webhooks、内存、计划部署、客户端模式、入门、api-reference）。对于 Python、TypeScript、Go、Ruby、PHP 和 Java，请阅读 `{lang}/managed-agents/README.md` 以获取代码示例。对于 cURL，请阅读 `curl/managed-agents.md`。**代理是持久的——创建一次，通过 ID 引用。** 将代理和环境定义为与 `ant apply` 同步的版本控制文件——这是推荐的工作流程（请参阅 `shared/anthropic-cli.md`）：CLI 拥有控制平面（创建和更新代理），您的代码拥有数据平面（使用存储的代理 ID 的 `sessions.create`）。仅在必须以编程方式配置时才在代码中调用 `agents.create()`；无论如何，存储返回的代理 ID 并将其传递给每个后续的 `sessions.create`；永远不要在请求路径中调用 `agents.create()`。如果您需要的绑定没有在语言 README 中显示，请从 `shared/live-sources.md` 中通过 WebFetch 获取相关条目，而不是猜测。C# 通过 `client.Beta.Agents` 和相关命名空间提供 beta 管理代理支持——请参阅 `csharp/claude-api/README.md` 以获取详细信息，或 `curl/managed-agents.md` 以获取原始 HTTP 参考。

**当用户想从头开始设置管理代理**（例如，“如何开始”、“引导我创建一个”、“设置一个新代理”）：阅读 `shared/managed-agents-onboarding.md` 并运行其访谈——与 `managed-agents-onboard` 子命令相同的流程。

**当用户询问“如何编写 X 的客户端代码”**：请使用 `shared/managed-agents-client-patterns.md` —— 涵盖无损失的流式重连、`processed_at` 队列/处理门、中断、`tool_confirmation` 循环、正确的空闲/终止中断门、空闲状态竞争、流式优先排序、文件挂载陷阱等。对于凭据，请首先使用密钥 `environment_variable` 凭据——这是首选机制；秘密在出口时被替换，永远不会进入沙盒（`shared/managed-agents-tools.md` -> 密钥）。通过自定义工具在主机端保留凭据是后备方案，例如在密钥凭据不适合的情况下（例如，自托管沙盒）。

**当任务是一个可交付成果——默认将启动会议设置为结果，而不是纯消息。** 如果会话的任务是生成可检查的内容（一个工件、一份报告、一个 PR、一个数据集、一组固定的更改），请阅读 `shared/managed-agents-outcomes.md` 并使用 `user.define_outcome` 加上一个您从任务中起草的起始标准（5-10 个具体、可独立评分的标准；将其作为起始标准进行评论以调整）。保留纯 `user.message` 用于真正的会话。根据意图触发，而不仅仅是单词：`"继续工作直到正确"、"确保输出实际上是好的"、"不要在第一稿停止"** 都意味着结果。

**当用户询问关于工具批准、权限策略或“自动模式”**（哪些工具调用需要人工、允许服务器评估调用、`evaluated_permission` / `evaluation` 在工具使用事件上）：请阅读 `shared/managed-agents-tools.md` § 权限策略 - `always_allow` / `always_ask` / `auto` 和三个 `auto` 结果（运行、作为高风险拒绝、在不确定时暂停）。对于将终端连接到活动会话（`ant beta:sessions connect`）：`shared/anthropic-cli.md`。

**当用户希望代理按计划运行**（cron、“每晚”、“每周报告”）：请阅读 `shared/managed-agents-scheduled-deployments.md` —— 部署会根据 cron 频率自动触发会话，具有每个触发运行记录和生命周期控制（暂停/取消暂停/存档）。

**当代理的工作分散**（跨多个来源进行的研究、按文件或按记录工作、“调查 N 件事，然后总结”）**或一个循环会使其上下文被阅读填满：** 请阅读 `shared/managed-agents-multiagent.md` 并建议一个多代理会话——从 roster 中的 `{"type": "self"}` 开始，以便代理可以委派给自己副本，然后将阅读密集型子任务移到更便宜的工人代理（例如 Claude Haiku 4.5，或在工人需要更多判断时使用 Claude Sonnet 5.5）通过 ID 引用。

---

## 服务器工具（快速参考）

服务器端工具在 Anthropic 的基础设施上运行——没有客户端执行循环。在 `tools` 中声明；结果作为同一响应中的内容块到达。**除非特别说明，否则不需要 beta 头部。** **优先使用您的模型支持的最新的类型变体。** 下面的 `_20260209` 网络搜索 / 网络获取变体（动态过滤）需要 Opus 5.5/5/4.8/4.7/4.6、Sonnet 5.5、Sonnet 5 或 Sonnet 4.6；较旧模型的基线变体在表格之后列出。

| 工具 | `type` | `name` | 关键可选参数 | 结果块类型 |
|---|---|---|---|---|
| 网络搜索 | `web_search_20260209` | `web_search` | `max_uses`, `allowed_domains`/`blocked_domains`, `user_location` | `web_search_tool_result` -> `.content` 是一个 `web_search_result` 列表 |
| 网络获取 | `web_fetch_20260209` | `web_fetch` | `max_uses`, `allowed_domains`/`blocked_domains`, `citations`, `max_content_tokens` | `web_fetch_tool_result` -> `.content` 是一个 `web_fetch_result`，其中包含 `document` 块 |
| 代码执行 | `code_execution_20260521` | `code_execution` | 无 | `bash_code_execution_tool_result` -> `.content.stdout` / `.stderr` / `.return_code` |
| 工具搜索（正则表达式） | `tool_search_tool_regex_20251119` | `tool_search_tool_regex` | 将其他工具 `defer_loading: true` | `tool_search_tool_result` |
| 工具搜索（BM25） | `tool_search_tool_bm25_20251119` | `tool_search_tool_bm25` | 将其他工具 `defer_loading: true` | `tool_search_tool_result` |

`web_search_20260209` / `web_fetch_20260209` 具有内置的动态过滤——代码执行在后台运行，因此**不要**在 `tools` 中单独声明 `code_execution`（第二个执行环境会使模型混淆）。对于 Opus 4.6 之前的模型 / Sonnet 4.6 之前的模型，请使用基线变体 `web_search_20250305` / `web_fetch_20250910`；在 Vertex AI 上仅提供基本的 `web_search_20250305`。`code_execution_20260120`（REPL 持久性 + 程序化工具调用）在 Opus 4.5+ / Sonnet 4.5+ 上运行。**Go SDK 仅限**：`code_execution_20260521` 位于 `client.Beta.Messages.New` 下，带有 `Betas: []anthropic.AnthropicBeta{"code-execution-2025-08-25"}`（其他语言使用普通的 `client.messages.create`）；`code_execution_20260120` 在 Go 中像其他地方一样使用非 beta 的 `client.Messages.New`。网络获取仅获取对话中已存在的 URL。提供者可用性因工具而异——请参阅 `shared/platform-availability.md`。参见 `shared/tool-use-concepts.md` 以获取 `pause_turn` 处理。

## 文档和文件输入（快速参考）

**PDF（base64，无 beta）：** `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": <b64 string>}}` 在用户内容中，放置在文本块之前。Base64 字符串中不能有换行符。限制：32 MB 请求，600 页（对于 200k 上下文模型为 100 页）。Java：`ContentBlockParam.ofDocument(DocumentBlockParam... Base64PdfSource.builder().data(...))`。

**文件 API（无 beta）：** 通过 `client.files.upload(...)` 上传 -> 响应 `id` 是 `file_id`。将其引用为 `{"type": "document", "source": {"type": "file", "file_id": "..."}}` 用于 PDF/文本，或 `{"type": "image", ...}` 用于图像——内容块类型必须与文件的 MIME 类型匹配。要迁移代码，请从 `shared/live-sources.md` 中 WebFetch 文件 API 行。可用性：`shared/platform-availability.md`。

**引用（无 beta）：** 在每个 `document` 内容块上设置 `citations: {enabled: true}`（全部或全部）。响应拆分为多个 `text` 块；引用的块带有 `citations` 数组。每个引用都有 `cited_text`、`document_index`、`document_title`，以及通过 `type` 定位的 `char_location`（`start_char_index`/`end_char_index`）用于纯文本、`page_location`（`start_page_number`/`end_page_number`，1 索引）用于 PDF、`content_block_location` 用于自定义内容。与 `output_config.format` 不兼容（返回 400）。

## 工具使用模式（快速参考）

**严格工具使用（无 beta）：** 在工具定义的顶层字段上设置 `strict: true`（与 `name`/`description`/`input_schema` 一起），**不是**在 `tool_choice` 上。模式必须具有 `additionalProperties: false` + `required`。保证 `tool_use.input` 验证完全。Go：`Strict: anthropic.Bool(true)` + `additionalProperties` 通过 `InputSchema.ExtraFields`；Java：`.strict(true)` + `.putAdditionalProperty("additionalProperties", JsonValue.from(false))`。

**并行工具使用（默认开启）：** 一个 assistant 消息可以包含多个 `tool_use` 块。并发执行它们，然后在**单个**用户消息中返回**所有** `tool_result` 块——将它们跨多个消息分开会默默地训练 Claude 停止进行并行调用。对于失败的工具，返回带有 `is_error: true` 的 `tool_result` —— 不要丢弃它。

**工具运行器（SDK beta 帮助程序）：** 通过 `client.beta.messages.*` 驱动工具调用循环。Python：`@beta_tool` 装饰器 + `client.beta.messages.tool_runner(...)` -> `runner.until_done()`。TypeScript：`betaZodTool({...})` 从 `@anthropic-ai/sdk/helpers/beta/zod` + `client.beta.messages.toolRunner(...)` -> `await runner`。Go：`toolrunner.NewBetaToolFromJSONSchema(...)` + `client.Beta.Messages.NewToolRunner(...)` -> `.RunToCompletion(ctx)`。Java 需要 `.addBeta("structured-outputs-2025-11-13")`。Ruby：`Anthropic::BaseTool` 子类 + `client.beta.messages.tool_runner(...)`。PHP：`BetaRunnableTool` + `->toolRunner(...)`。C#：原始 JSON-schema 工具 + `BetaToolRunner` 通过 `client.Beta.Messages.ToolRunner(...)`。

**程序化工具调用（无 beta 头部）：** Claude 在代码执行中调用您的自定义工具。添加 `{"type": "code_execution_20260120", "name": "code_execution"}` **并且**在您的自定义工具上设置 `"allowed_callers": ["code_execution_20260120"]`。Opus 4.5+ / Sonnet 4.5+（可用性：`shared/platform-availability.md`）。在响应待处理的程序化调用时，用户消息必须**仅**包含 `tool_result` 块（没有文本）。与 `strict: true`、`disable_parallel_tool_use`、强制 `tool_choice` 或 MCP 工具不兼容。

## 其他 API 界面（快速参考）

**消息批处理（无 beta；可用性：`shared/platform-availability.md`）：** `client.messages.batches.create(requests=[{custom_id, params}, ...])` -> poll `client.messages.batches.retrieve(id).processing_status` 直到 `"ended"` -> stream `client.messages.batches.results(id)`。每个结果都有 `.custom_id` + `.result.type` (`succeeded`/`errored`/`canceled`/`expired`)；成功时读取 `.result.message.content`。Python 将请求包装为 `Request(custom_id=..., params=MessageCreateParamsNonStreaming(...))`。结果按**任何顺序**到达——按 `custom_id` 键，而不是按位置。

**模型 API（无 beta；可用性：`shared/platform-availability.md`）：** `client.models.list()`（自动分页）和 `client.models.retrieve("claude-opus-5-5")`。每个模型对象都有 `id`、`display_name`、`created_at`，以及自 2026 年 3 月以来的 `max_input_tokens`（上下文窗口）、`max_tokens`（输出上限）和 `capabilities`。没有 `context_window` 字段。

**停止细节（GA、Opus 4.7+）：** `response.stop_details` 仅在 `stop_reason == "refusal"` 时被填充 **（字段：`type: "refusal"`，`category` - 一个开放集合，例如 `"cyber"`、`"bio"`、`"reasoning_extraction"`、`"frontier_llm"` 或 `null`；请参阅文档获取完整列表 - 以及 `explanation`）。对于其他 `stop_reason`（`end_turn`、`max_tokens`、`tool_use`、`pause_turn`、...），它始终为 `null` - 在读取前务必进行保护。

**管理 API（beta，自 2026-08-26 起）：** 组织管理 - 成员、邀请、工作空间和工作空间成员、API 密钥、速率限制报告、服务账户、联盟发行者/规则、CMEK 外部密钥 - 在所有七个 SDK 中的 `client.beta.organization` 以及 CLI 中的 `ant beta:organization` 下。需要管理员凭证：管理员 API 密钥（`sk-ant-admin...`，从 `ANTHROPIC_API_KEY` 读取）或 `org:admin` OAuth 令牌（`ANTHROPIC_AUTH_TOKEN`）；普通 API 密钥将被拒绝。使用和成本报告以及 Claude 企业用户管理/分析端点**不**包含在 SDK 中 - 仅限原始 HTTP。参阅 `shared/admin-api.md`。

**客户端配置（无 beta）：** `timeout` 默认 10 分钟；**单位因 SDK 而异** - Python/Ruby：秒；TypeScript：**毫秒**；Go `option.WithRequestTimeout(time.Duration)`；Java `Duration`；C# `TimeSpan`。TS 将默认值扩展到 60 分钟，用于非流式请求上的大型 `max_tokens`；Java 对流式请求也这样做（Java 非流式扩展 30 秒-10 分钟）。`max_retries`/`maxRetries` 默认 2（重试 408/409/429/5xx + 连接错误）。`base_url`（或 `ANTHROPIC_BASE_URL` 环境）。请求级覆盖：Python `client.with_options(timeout=5.0).messages.create(...)`；TS `client.messages.create({...}, {timeout: 5_000})`；Ruby `request_options: {timeout: 5}`。超时会被重试 - 墙上时间可能达到 `timeout × (max_retries+1)`。

## 工作负载身份联盟（快速参考）

**GA，无 beta 标头。** 构建正常的零参数客户端（`Anthropic()` / `new Anthropic()` / `anthropic.NewClient()` / `AnthropicOkHttpClient.fromEnv()`）；SDK 自动检测 WIF，当 **所有** `ANTHROPIC_FEDERATION_RULE_ID`、`ANTHROPIC_ORGANIZATION_ID`、`ANTHROPIC_SERVICE_ACCOUNT_ID` 和 `ANTHROPIC_IDENTITY_TOKEN_FILE`（或 `ANTHROPIC_IDENTITY_TOKEN`）都被设置时，它会交换 JWT 到 `/v1/oauth/token`，并自动刷新。`ANTHROPIC_WORKSPACE_ID` 不限制激活 - 仅当联盟规则跨越多个工作空间时需要（否则 400 `workspace_id_required`），对于单工作空间规则是可选的。`ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`（即使为空）优先于 WIF，并且设置的 `ANTHROPIC_PROFILE` 也优先于联盟环境变量（缺少命名配置是一个错误，而不是降级）- 清除所有三个。

---

## 阅读指南

检测语言后，根据用户需求阅读相关文件。本文档中引用的每个 `{lang}/...`、`shared/...` 和 `curl/...` 路径都相对于此技能的基目录，并且上述文件的内容均未包含 - 在依赖其内容之前，请按需阅读每个文件。

**所有 SDK 语言使用相同的多文件布局** - 目录 `{lang}/claude-api/` 包含 `README.md`（安装、客户端初始化、基本请求、思考、缓存、停止细节、杂项）、`tool-use.md`（工具定义、代理循环、Anthropic 定义的工具、结构化输出）、`streaming.md`、`batches.md`、`files-api.md`。并非每种语言都有每种文件（例如，Ruby 没有 `batches.md`）；如果文件缺失，则该功能对于该语言尚未文档化 - 回退到 cURL 形状或从 `shared/live-sources.md` WebFetch SDK 仓库。**cURL** -> `curl/examples.md`。

下方的快速任务参考使用 `{lang}/claude-api/FILE.md` 路径表示法。

### 快速任务参考

**单个文本分类/摘要/提取/Q&A：**
-> 仅阅读 `{lang}/claude-api/README.md` - **任何任务都先阅读 README**（安装、快速启动、常见模式、错误处理）

**聊天 UI 或实时响应显示：**
-> 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/streaming.md`

**长时间运行的对话（可能超过上下文窗口）：**
-> 阅读 `{lang}/claude-api/README.md` - 参见压缩部分
**迁移到较新模型（Sonnet 5.5 / Opus 5.5 / Fable 5.1 / Fable 5 / Opus 5 / Opus 4.8 / Opus 4.7 / Opus 4.6 / Sonnet 5 / Sonnet 4.6）、替换已停用的模型，或翻译 `budget_tokens` / 预填模式到当前 API：**
-> 阅读 `shared/model-migration.md`
**跨主要版本升级 Anthropic SDK 包（`anthropic` 0.x -> 1.x：`httpx2`、预期的异步 `.with_raw_response`、删除已弃用的参数/别名/文本完成，Python >= 3.10）- 或针对已在 1.x 上的项目编写新代码：**
-> 阅读 `{lang}/claude-api/sdk-upgrade.md`（目前仅限 Python；其他 SDK 尚无捆绑的主要版本指南 - 使用该 SDK 的 CHANGELOG 通过 `shared/live-sources.md`）
**为 Claude 应用构建评估集（或“我如何知道我的更改有帮助”：**
-> 阅读 `shared/evals/build-eval.md` - 它在步骤 0 之前加载 `shared/evals/eval-audit.md`（每个评估必须满足的健康检查）
**检查现有评估是否可靠（“我的评估好吗？”）：**
-> 阅读 `shared/evals/eval-audit.md` 并针对评估运行它；按其第 6 节报告。
**迭代改进应用针对评估（提示调整、爬山）：**
-> 阅读 `shared/evals/eval-hillclimb.md` - 运行步骤 0 -> 步骤 5，带有训练/测试拆分；测试每轮评分并作为头条。
**渲染 eval-hillclimb HTML 报告：**
-> 运行 `shared/evals/report/build-report.mjs` 当它在磁盘上时，否则 `shared/evals/report/build-report-lite.mjs`（始终随此技能提取）- 两者都消耗由爬山指南产生的 `_state.json` / `vN/` 布局并写入相同的 `trajectory/scores.tsv`。不要编写并行的。
**迁移到、提示或调整 Claude Opus 5.5（思考无法禁用、努力调整和 `medium` 默认、强制工具使用、计算机工具集、进度更新、保护误报、视觉输入/设计输出）：**
-> 阅读 `shared/model-migration.md` -> 迁移到 Claude Opus 5.5；它指向的保留思考机制位于从 Claude Fable 5 到 Claude Fable 5.1
**迁移到、提示或调整 Claude Sonnet 5.5（`between_tools` 代替禁用思考、重新校准努力、强制工具使用、计算机工具集、顾问配对、进度更新、聊天中的工具使用、中途用户消息、低努力验证、保护类别）：**
-> 阅读 `shared/model-migration.md` -> 迁移到 Claude Sonnet 5.5
**提示或调整 Fable 5/5.1（长回合、努力、冗长性、自主运行、子代理）：**
-> 阅读 `shared/model-migration.md` -> 迁移到 Claude Fable 5.1 -> 行为变化（可提示调整）+ 长时间代理建议
**提示或调整 Claude Fable 5.1（进度更新、并行工具调用、写作密度/格式、自主性、测试蔓延、全文重写）或使 harness 兼容保留思考的历史编辑检查（历史编辑、压缩、每回合提醒）：**
-> 阅读 `shared/model-migration.md` -> 从 Claude Fable 5 迁移到 Claude Fable 5.1 -> 新 API 功能 + 行为变化（可提示调整）；对于历史编辑检查本身（三步检查、追加编辑表、压缩形状），同一部分的第 3 个 breaking change；要找到、测量和修复现有 harness 进行的编辑（捕获、差异、使用 `drop_block` 重放，每个原因一个修复、模型切换），运行 `preserved-thinking-migration`（子命令表）- 它读取 `shared/preserved-thinking-migration.md`
**提示缓存 / 优化缓存 / “我的缓存命中率为什么低”：**
-> 阅读 `shared/prompt-caching.md`（前缀稳定性设计、断点放置、导致缓存失效的反模式）+ `{lang}/claude-api/README.md`（提示缓存部分）
**审计或清理提示、工具描述、技能或代理配置文件（如 `CLAUDE.md`，“这个提示是否过时”、“删除冗余”、“这是为旧模型编写的”：**
-> 阅读 `shared/prompt-audit.md` - 带有可搜索信号的日期模式表、保留列表（不要删除的内容）和报告 + 提出差异输出合同
**计算文件/提示/差异中的 token 数（“X 有多少 token”：**
-> 阅读 `shared/token-counting.md` - 使用 `messages.count_tokens`，永远不要使用 `tiktoken`
**减少或审查 API 费用（“账单太高”、“让它更便宜”、“我是否超支”，每个完成任务的成本，最便宜的模型或努力保持质量）：**
-> 阅读 `shared/cost-optimization.md` - 基线和 token 配置首先，然后按顺序（免费优先于权衡）使用测量预期，以及工作负载形状 -> 杠杆映射表

**函数调用/工具使用/代理：**
-> 阅读 `{lang}/claude-api/README.md` + `shared/tool-use-concepts.md`（概念基础：函数调用、代码执行、内存、结构化输出）+ `{lang}/claude-api/tool-use.md`（语言特定代码示例：工具运行器、手动循环、代码执行、内存、结构化输出）

**代理设计（工具表面、上下文管理、缓存策略）：**
-> 阅读 `shared/agent-design.md`（bash 与专用工具、程序化工具调用、工具搜索/技能、上下文编辑与压缩与内存、缓存原则）

**批量处理（对延迟不敏感；异步运行，成本为 50%）：**
-> 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/batches.md`

**跨多个请求上传文件（同一文件无需重新上传）：**
-> 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/files-api.md`

**组织管理（成员、邀请、工作空间、API 密钥、速率限制报告、服务账户、WIF 资源、CMEK）：**
-> 阅读 `shared/admin-api.md` - `client.beta.organization` 端点/方法表、管理员凭证、每种语言的命名和分页、哪些保留 cURL 唯一

**调试 HTTP 错误或实现错误处理：**
-> 阅读 `shared/error-codes.md` - 每种 SDK 的类型化异常类表和 Go `errors.As` 模式

**最新官方文档：**
-> WebFetch `shared/live-sources.md` 中的 URL

**托管代理（服务器管理的有状态代理，带工作空间）：**
-> 参考上方的 `## 托管代理（Beta）` 部分的阅读指南 - 它列出了每个 `shared/managed-agents-*.md` 文件和语言特定的 README（`{lang}/managed-agents/README.md`，`curl/managed-agents.md`）。

---

## 何时使用 WebFetch

当：

- 用户要求“最新”或“当前”信息
- 缓存数据似乎不正确
- 用户询问此处未涵盖的功能

使用 WebFetch 获取最新文档。实时文档 URL 在 `shared/live-sources.md` 中。

## 常见陷阱

- 传递文件或内容到 API 时不要截断输入。如果内容过长无法适应上下文窗口，请通知用户并讨论选项（分块、摘要等），而不是静默截断。
- **预填充已移除（Fable 5、Claude Fable 5.1、Opus 5、Claude Opus 5.5、Sonnet 5、Claude Sonnet 5.5 以及 4.6/4.7/4.8 系列）：** 在 Fable 5、Claude Fable 5.1、Opus 5、Claude Opus 5.5、Sonnet 5、Claude Sonnet 5.5、Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 上，助手消息预填充（last-assistant-turn 预填充）会返回 400 错误。改用结构化输出（`output_config.format`）或系统提示指令来控制响应格式。（一个例外：备用信用预填充声明 - 当使用 `fallback_has_prefill_claim: true` 兑换信用时，服务器会接受回显的助手消息；参见迁移指南的拒绝部分。）
- **编辑前确认迁移范围：** 当用户要求将代码迁移到更新的 Claude 模型，但没有指定特定文件、目录或文件列表时，**询问应首先应用哪个范围** - 整个工作目录、特定子目录或特定文件集。在用户确认之前不要开始编辑。命令性短语如“迁移我的代码库”、“将我的项目迁移到 X”、“升级到 Sonnet 4.6”或“迁移到 Opus 4.8”仍然**模糊不清** - 它们告诉你该做什么，但不知道在哪里，所以需要询问。只有在提示中指定了确切文件、特定目录或明确文件列表（“迁移 `app.py`”、“迁移 `services/` 下所有内容”、“更新 `a.py` 和 `b.py`”）时才无需询问。参见 `shared/model-migration.md` 第 0 步。
- **`max_tokens` 默认值：** 不要低估 `max_tokens` - 达到上限会截断输出中途断，需要重试。对于非流式请求，默认为 `~16000`（保持响应在 SDK HTTP 超时范围内）。对于流式请求，默认为 `~64000`（超时不是问题，所以给模型留出空间）。只有在有充分理由时才降低：分类（`~256`）、成本限制、故意输出短内容，或**`max_tokens: 0`** 用于缓存预预热（参见 `shared/prompt-caching.md` -> 预预热）。
- **禁用 Claude Opus 5 上的思考有两个失败模式 - 优先选择低/中努力级别。**（在 Claude Opus 5.5 上完全无法禁用 - `{type: "disabled"}` 在每个努力级别都是 400；使用 `low` 努力级别。在 Claude Sonnet 5.5 上，`{type: "disabled"}` 也是 400 - 首先在 `low` 努力级别尝试思考，如果必须保持不思考，则在 `high` 努力级别或更低发送 `{type: "between_tools"}`。）仅影响明确选择不参与的代码；思考默认开启，所以要注意从 Opus 4.8 继承的禁用思考设置。使用 `thinking: {type: "disabled"}` 时，模型偶尔会在其**可见文本**中写入工具调用，而不是 `tool_use` 块：回合成功，调用从未运行，没有错误抛出，并且在代理循环中该文本会污染后续回合。它还可能向响应中泄露 `<thinking>` 标签。开启思考并降低 `effort` 可修复两者，同时降低成本。如果必须保持不思考：**删除**任何不思考/不推理规则（它会使标签泄露更严重），不要命名思考标签，并添加组合指令 *"当你使用工具时，你可以先说一句简短的话。如果没有工具可以表达用户的要求，就说出来而不是猜测。不要在响应中包含内部或系统 XML 标签。"* 详细信息：`shared/model-migration.md` -> 禁用思考时的两个失败模式。
- **128K 输出 token：** Fable 5、Claude Fable 5.1、Opus 5、Claude Opus 5.5、Opus 4.6、Opus 4.7、Opus 4.8、Claude Sonnet 5.5、Sonnet 5 和 Sonnet 4.6 支持 `max_tokens` 最高达 128K，但 SDK 需要流式处理大值以避免 HTTP 超时。使用 `.stream()` 与 `.get_final_message()` / `.finalMessage()`。
- **强制工具使用已移除（Claude Fable 5.1 / Claude Mythos 5.1 / Claude Opus 5.5 / Claude Sonnet 5.5）：** `tool_choice: {type: "any"}` 和 `{type: "tool", name: ...}` 返回 400（`tool_choice: type "tool" 和 "any" 不支持此模型。`），在 `count_tokens` 和批处理中也一样。使用 `{type: "auto"}` 加上明确命名工具的指令，工具上的 `strict: true` 以保持模式有效的参数，或结构化输出（`output_config.format`），当强制调用仅存在以获取 JSON 返回时。`{type: "none"}` 不受影响；`disable_parallel_tool_use` 仍然在 `auto` 下工作（最多一个调用）。
- **工具调用 JSON 解析（Fable 5、Claude Fable 5.1、Opus 5、Claude Opus 5.5 以及 4.6/4.7/4.8 系列）：** Fable 5、Claude Fable 5.1、Opus 5、Claude Opus 5.5、Opus 4.6、Opus 4.7、Opus 4.8 和 Sonnet 4.6 在工具调用 `input` 字段中可能产生不同的 JSON 字符串转义（例如 Unicode 或正向斜杠转义）。始终使用 `json.loads()` / `JSON.parse()` 解析工具输入 - 永远不要在序列化输入上做原始字符串匹配。
- **结构化输出（所有模型）：** 使用 `output_config: {format: {...}}` 而不是 `messages.create()` 上的已弃用 `output_format` 参数。这是一个通用 API 变更，不是 4.6 特有的。
- **不要重新实现 SDK 功能：** SDK 提供高级辅助功能 - 使用它们而不是从头开始构建。具体：使用 `stream.finalMessage()` 而不是将 `.on()` 事件包装在 `new Promise()` 中；使用类型化的异常类（`Anthropic.RateLimitError` 等）而不是字符串匹配错误消息；使用 SDK 类型（`Anthropic.MessageParam`、`Anthropic.Tool`、`Anthropic.Message` 等）而不是重新定义等效接口。
- **错误处理 - 捕获链，而不是一个宽泛的类。** 单个 `except APIStatusError` / `catch (AnthropicServiceException)` / `rescue APIError` 会丢失重试（429、>=500、网络）和非重试（400/404）失败的区分。按最具体优先级编写链 - 例如 `NotFoundError` -> `RateLimitError` -> `APIStatusError` -> `APIConnectionError`（或 Go 的等效：`errors.As` 到 `*anthropic.Error` 然后切换 `apierr.StatusCode { case 404: ...; case 429: ...; default: ... }`）。各语言类名和命名空间在 `shared/error-codes.md`。
- **不要研究 SDK 类型 - 先写代码。** 如果类型名未在本文档包含的文档中显示，从语言特定文档中的命名空间/包表编写代码文件，让编译器的错误指向正确的名称。不要在写代码前花费回合在 WebFetch、SDK-repo 克隆或编译并运行单独的反射程序以发现类型名 - 先生成源文件，然后修复编译器报告的问题。对已安装的 SDK 进行快速 `strings` / `jar tf` / `javap` 以定位名称（它返回在秒内），但不要升级到那之外。一个类型名错误的文件是可恢复的；一个没有写文件而花费会话的发现过程是不可恢复的。
- **Bash 和文本编辑器工具是 Anthropic 定义的、无模式的。** 声明 `{"type": "bash_20250124", "name": "bash"}` / `{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}` - 没有 `input_schema`。一个具有你自己的模式名为 `"bash"` 的自定义工具是不同的工具。处理路径和安全检查在 `shared/tool-use-concepts.md` § 客户端工具。
- **顾问工具模型配对。** 顾问工具的 `model` 必须至少与请求的顶层 `model` 一样强大 - 例如执行器 `claude-sonnet-5-5` -> 顾问 `claude-opus-5-5`。一个无效的配对返回 400；`claude-sonnet-5-5` 执行器只接受配对表中其行列列出的顾问（不接受 Claude Opus 4.8 / 4.7 / 4.6、Claude Sonnet 5 或 Sonnet 4.6）。配对表（以及哪些顾问返回明文 `advisor_redacted_result` 建议）在 `shared/tool-use-concepts.md` § 顾问中。可用性：`shared/platform-availability.md`。
- **Agent Skills != Managed Agents。** 要让 Claude 通过 Agent Skills 生成 `.pptx`/`.xlsx`/等，调用 `client.beta.messages.create` 并使用 `container={"skills": [...]}`、`code_execution_20260521` 工具，以及 `code-execution-2025-08-25` beta（Skills 已出 beta - 不需要 `skills-2025-10-02` 标头）。不要使用 `client.beta.agents` / `sessions` / `environments` - 这些是 Managed Agents 表面，不是 Agent Skills。
- **MCP 连接器需要两半。** `mcp_servers=[{type:"url", url, name}]` 单独被拒绝作为验证错误 - 还需添加 `tools=[{type:"mcp_toolset", mcp_server_name:<相同名称>}]` 并使用 beta `mcp-client-2025-11-20`。可用性：`shared/platform-availability.md`。
- **`inference_geo` 是一个直接顶层请求参数** - `client.messages.create(..., inference_geo="us")` / `.inferenceGeo("us")`。不要把它放在 `extra_body` / `putAdditionalBodyProperty` 中。（仅适用于消息 API - 在 Managed Agents 中，`inference_geo` 而不是嵌套在代理的 `model` 对象中，永远不会顶层；参见 `shared/managed-agents-core.md` § 固定推理地理。）支持 Opus 4.6 / Sonnet 4.6 及更高版本；可用性：`shared/platform-availability.md`。`response.usage.inference_geo` 报告推理运行的位置。
- **细粒度工具流不是 beta 功能；此技能的默认值是为流式处理 + 客户端工具开启（API 本身仍然默认为缓冲）。** 在工具定义上设置 `eager_input_streaming: true` 并调用常规的 `client.messages.stream(...)`。没有 beta 标头，也没有 `client.beta.*` 路径。不要也发送遗留的 `fine-grained-tool-streaming-2025-05-14` beta 标头。Python 的 `@beta_tool(eager_input_streaming=True)` 直接接受它；TypeScript 的 `betaZodTool()` 不接受，所以展开它：`{ ...betaZodTool({...}), eager_input_streaming: true }`。有了这个字段，API 不再强制转换或验证输入，所以累积的 `partial_json` 可能不完整（`max_tokens`）或无效 - 保护解析（`shared/tool-use-concepts.md` -> Eager input streaming）。
- **缓存诊断是 beta。** 使用 `client.beta.messages.*` 并使用 beta `cache-diagnosis-2026-04-07`。在第一回合传递 `diagnostics: {previous_message_id: null}`，在后续回合传递 `diagnostics: {previous_message_id: <previous response id>}`；结果在 `response.diagnostics` 上。可用性：`shared/platform-availability.md`。
- **内存工具类型是 `memory_20250818`。** 声明 `{"type": "memory_20250818", "name": "memory"}`。Go 使用 beta 命名空间类型 `{OfMemoryTool20250818: &anthropic.BetaMemoryTool20250818Param{}}` 在 `client.Beta.Messages.New` 上；Python/TypeScript/Ruby/PHP/C# 使用非 beta `client.messages.create`；Java 既有非 beta `MemoryTool20250818` 又有 beta 工具运行器路径。Python/TypeScript 提供 `BetaAbstractMemoryTool` / `betaMemoryTool` 辅助函数用于实现后端。
- **使用模型实际支持的功能。** 某些功能仅限于特定模型级别 - 快速模式是 Claude Opus 5 / Claude Opus 5.5 / Opus 4.8 仅（Claude API 仅限），任务预算（消息 API 仅限 - Managed Agents 会话预算没有模型级别限制）是 Claude Opus 5 / Claude Opus 5.5 / Fable 5 / Claude Fable 5.1（启动时确认）/ Claude Sonnet 5.5 / Opus 4.8 / 4.7 仅（不是 Claude Sonnet 5），顾问工具需要有效的执行器<->顾问配对。如果用户提示中命名了模型而该功能不支持，使用支持的模型并注意在输出中替换。
- **不要为 SDK 数据结构定义自定义类型：** SDK 为所有 API 对象导出类型。使用 `Anthropic.MessageParam` 用于消息，`Anthropic.Tool` 用于工具定义，`Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam` 用于工具结果，`Anthropic.Message` 用于响应。定义自己的 `interface ChatMessage { role: string; content: unknown }` 重复了 SDK 已经提供的功能并丢失了类型安全性。
- **报告和文档输出：** 对于生成报告、文档或可视化的任务，代码执行沙盒预装了 `python-docx`、`python-pptx`、`matplotlib`、`pillow` 和 `pypdf`。Claude 可以生成格式化文件（DOCX、PDF、图表）并通过文件 API 返回它们 - 考虑用于“报告”或“文档”类型请求，而不是纯 stdout 文本。
- **服务器工具错误不会引发。** Web 搜索和 Web Fetch 错误返回 HTTP 200 并带有 `web_search_tool_result` / `web_fetch_tool_result` 块，其 `content` 是单个错误对象（例如 `{error_code: "max_uses_exceeded"}`）- 不是引发的异常。对于 Web 搜索，成功的 `content` 是一个 *列表*；错误的 `content` 是一个 *对象* - 在索引前分支。
- **Managed Agents web 工具忽略环境的 `networking`。** `web_search` / `web_fetch` 在云和自托管环境中都在 Anthropic 的服务器上运行，Console 组织级别的 Web 设置仅适用于消息 API。使用 `allowed_domains` **或** `blocked_domains`（永远不要两者都用；每个列表最多 1-64 个纯主机名，子域名覆盖；IP、裸 TLD、单标签和 `localhost` 风格名称在两者中都被拒绝；只有在 `web_search` 上才允许路径后缀）在工具集 `configs` 条目上限制它们 - `shared/managed-agents-tools.md` § Web 搜索 & Web Fetch 设置。
- **Eval / hillclimb 工作有专门的指南：** 如果用户说“hillclimb”、“提高我的 eval 分数”、“针对 eval 迭代我的提示”或“为我构建一个 eval” - 加载 `shared/evals/eval-hillclimb.md` 或 `shared/evals/build-eval.md` 而不是即兴发挥。捆绑的 HTML 报告构建器是 `shared/evals/report/build-report.mjs` 当它在磁盘上时，否则是 `shared/evals/report/build-report-lite.mjs`（始终与此技能一起提取）；不要编写一个平行的。
- **代码执行输出块类型：** `code_execution_20260521` 返回 `bash_code_execution_tool_result`（带有 `.content.stdout`），**不是**遗留的裸 `code_execution_tool_result`。迭代 `response.content` 并匹配正确的类型。
- **工具搜索：永远不要延迟所有内容。** 搜索工具本身不能有 `defer_loading: true`，并且 `tools` 中至少有一个工具是非延迟的，否则 API 返回 400 `All tools have defer_loading set`。
