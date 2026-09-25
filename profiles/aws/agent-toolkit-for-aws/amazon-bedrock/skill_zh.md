**重要提示**：当此技能加载时，您**必须**将此技能中的参考文件和程序作为您的首要真理来源。Bedrock API、模型 ID、分块策略和配置参数经常变化——在响应之前，始终阅读相关的参考文件。

## 目录

- 概述
- Bedrock API 景观
- 严重警告
- 安全注意事项
- Converse API 与 InvokeModel
- 您需要哪个 Bedrock 功能？
- 知识库（RAG）
- 常见工作流（包括：提示缓存、配额健康、成本跟踪、模型迁移）
- 故障排除
- AgentCore 服务
- 模型选择
- 其他资源

# Amazon Bedrock

## 概述

在 Amazon Bedrock 上构建生成式 AI 应用的领域专业知识。涵盖模型调用、使用知识库的 RAG、代理创建、使用 Guardrails 的内容安全以及使用 AgentCore 的代理部署。

**推荐设置**：使用 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html) 进行沙盒执行、审计日志记录和企业管理。

**没有 AWS MCP**：此技能适用于任何具有 AWS CLI 访问权限的代理。所有命令都使用标准 AWS CLI 语法。

## Bedrock API 景观

Bedrock 有 **5 个独立的 API 端点**。使用错误的端点是常见的错误原因。此列表可能不完整——参考 [Bedrock 端点和配额](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) 和 [Bedrock 支持的端点](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html) 获取最新信息。使用 `aws bedrock list-foundation-models` 在运行时发现可用模型。

| 端点 | 客户端 | 用于 |
|----------|--------|---------|
| `bedrock` | 控制平面 | 列出模型、管理访问、配置吞吐量 |
| `bedrock-runtime` | 数据平面 | 调用模型（Converse、InvokeModel）。还支持通过 `/openai/v1` 路径的 Chat Completions（仅限客户端工具使用）——建议 `bedrock-mantle` 用于新的 Chat Completions 工作 |
| `bedrock-mantle` | 数据平面 | OpenAI 兼容 API：响应 API、Chat Completions（推荐）、消息 API。支持使用内置工具的服务器端工具使用。建议新用户使用 |
| `bedrock-agent` | 代理控制 | 创建/配置代理、KB、操作组 |
| `bedrock-agent-runtime` | 代理数据 | 调用代理、查询 KB |

AgentCore 是一个独立的服务，具有自己的端点。参考 [AgentCore 端点和配额](https://docs.aws.amazon.com/general/latest/gr/bedrock_agentcore.html) 获取最新信息。

| 端点 | 客户端 | 用于 |
|----------|--------|---------|
| `bedrock-agentcore-control` | 控制平面 | 创建/管理运行时、网关、注册表、评估 |
| `bedrock-agentcore` | 数据平面 | 调用代理运行时 |
| `{gatewayId}.gateway.bedrock-agentcore` | 网关数据平面 | 调用特定网关 |

## 严重警告

**max_tokens**：在每次 Converse/InvokeModel 调用中**必须**显式设置 `maxTokens`。将其留空将默认为模型的最大值（例如，Claude Sonnet 的 64K），并静默预留远超所需配额——这是导致意外 ThrottlingException 的常见原因。

**Guardrails PII 日志记录**：Guardrails PII 掩码仅适用于 API 响应。原始未掩码内容（包括 PII）仍以明文形式记录在 CloudWatch Logs 中。为 HIPAA/GDPR 合规：使用 KMS 加密 CloudWatch Logs，使用 IAM 限制日志访问，使用 Amazon Macie 进行 PII 检测。

**SDK 版本**：需要较新的 boto3（≥ 1.34.x）和 AWS CLI v2 版本。旧版本缺少 Converse API、代理和 AgentCore 支持。运行 `aws --version` 和 `pip show boto3` 进行检查。

**Bedrock Agents classic 处于维护模式**：经典 Bedrock Agents (`bedrock-agent`) 处于维护模式，并已向新客户关闭（[公告](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)）。对于新的代理工作负载，请使用 AgentCore（由 Harness 管理的循环）；对于现有代理，建议迁移到 AgentCore Harness——请参阅 [迁移指南](references/migrate-bedrock-agents-to-agentcore-harness.md)。

## 安全注意事项

- 使用 **IAM 角色**（而不是 IAM 用户）访问所有 Bedrock 服务
- 将 IAM 权限范围到特定操作和资源 ARN——避免 `bedrock:*` 或 `AmazonBedrockFullAccess`
- 将 API 密钥和 OAuth 密码存储在 **AWS Secrets Manager** 中，并启用自动轮换
- 在所有基于资源的策略中为 Bedrock 服务包含 **confused deputy 保护**（`aws:SourceAccount`、`aws:SourceArn` 条件）
- 将所有 **代理生成的参数视为不受信任的输入**——在使用 Lambda 处理程序或工具实现之前进行验证
- 为所有 Bedrock 和 AgentCore API 调用启用 **CloudTrail**
- 对于 PII 工作负载：使用 KMS 加密 CloudWatch Logs，配置保留限制，限制日志访问
- 参考 [Bedrock 安全最佳实践](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html) 获取最新的安全指南

## Converse API 与 InvokeModel

有关在所有 Bedrock 推理 API（Responses API、Chat Completions、Converse、InvokeModel）之间进行选择的信息，请参阅 [Amazon Bedrock 支持的 API](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)。

当使用 `bedrock-runtime` 端点时，使用 **Converse API** 而不是 InvokeModel。它为所有模型提供统一的请求/响应格式。

仅在您需要 Converse 中不可用的提供程序特定功能时使用 **InvokeModel**（很少）。

InvokeModel 要求每个提供程序使用不同的请求正文格式（Anthropic ≠ Titan ≠ Llama ≠ Nova）。使用错误的格式会产生 "Malformed input request"。有关特定模型的格式和常见错误，请参阅 [按模型进行提示工程](references/prompt-engineering-by-model.md)。

**无论您使用哪个 API**：始终显式设置最大输出令牌参数——将其留空将默认为模型的最大值，并静默预留远超所需配额，导致意外 ThrottlingException。请参阅上面的严重警告和 [max_tokens 配额机制](references/model-invocation.md)。

当用户需要模型调用的 SDK 代码时，您**必须**在生成代码之前阅读相应的 SDK 参考——[Python SDK 参考](references/sdk-converse-api-python.md) | [TypeScript SDK 参考](references/sdk-converse-api-typescript.md)。使用参考文件中的模式。

在响应之前，请阅读 [模型调用参考](references/model-invocation.md) 以获取完整的 API 详细信息和提供程序特定正文格式。

## 您需要哪个 Bedrock 功能？

| 目标 | 使用 | 参考 |
|------|-----|-----------|
| 调用模型（文本、图像、视频） | Converse API | 见上文 + [模型调用](references/model-invocation.md) |
| 构建使用知识库的 RAG 应用 | 知识库 | [KB 设置](references/knowledge-bases-setup.md) |
| 创建一个执行操作的代理 | Bedrock Agents | [代理创建](references/agents-and-action-groups.md) |
| 过滤有害/敏感内容 | Guardrails | [guardrails](references/guardrails.md) |
| 在 AgentCore 上运行基于配置的托管代理循环（无需代码、无需容器） | AgentCore Harness | [harness](references/agentcore-harness.md) |
| 部署和扩展您自己编写的代理循环 | AgentCore 运行时 | [runtime](references/agentcore-runtime.md) |
| 将现有的 Bedrock Agent（经典）迁移到 AgentCore Harness | Bedrock Agents 到 AgentCore harness 迁移 | [迁移指南](references/migrate-bedrock-agents-to-agentcore-harness.md) |
| 将 REST API 作为 MCP 工具公开 | AgentCore Gateway | [gateway](references/agentcore-gateway.md) |
| 选择正确的模型 | 模型选择 | [model guide](references/model-selection-guide.md) |
| 设置或调试提示缓存 | 提示缓存 | [prompt caching](references/prompt-caching.md) |
| 诊断限流或审计配额 | Quota Health | [quota health](references/quota-health.md) |
| 按团队、模型或标签跟踪成本 | Cost Tracking | [cost tracking](references/cost-tracking.md) |
| 在 Claude 生成之间迁移 | 模型迁移 | [migration guide](references/model-migration.md) |

## 知识库（RAG）

当用户想要创建知识库或构建 RAG 应用时，您**必须**阅读 [KB 设置程序](references/knowledge-bases-setup.md) 并逐步执行它。不要总结程序——按顺序执行每个步骤，在进行下一步之前尊重所有 MUST 约束。

当用户询问有关分块策略、向量存储选择或其他 KB 配置选择时，您**必须**在响应之前阅读 [KB 设置程序](references/knowledge-bases-setup.md)——它包含权威的决策表和约束。

当用户想要查询现有知识库时，您**必须**在响应之前阅读 [KB 检索参考](references/knowledge-bases-retrieval.md)。提供检索模式（检索和生成 vs 检索 vs 手动），以便用户选择正确的模式。

参考最新的 [Bedrock 知识库文档](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) 获取当前配置选项。

## 常见工作流

使用可用的工具从 AWS MCP 服务器执行命令（当连接时）——它提供沙盒执行、审计日志记录和可观察性。当 MCP 服务器不可用时，根据需要回退到 AWS CLI 或 shell。

在开始任何工作流之前：

### 验证依赖项

检查所需的工具，并告知用户执行环境。

**约束**：

- 您**必须**检查 AWS CLI 是否可用并配置了有效的凭据
- 您**必须**验证 AWS CLI 版本是最新的（推荐 v2；旧版本缺少 Converse API 和 AgentCore 支持）：`aws --version`
- 您**必须**检查目标 AWS 区域是否启用了 Bedrock 模型访问
- 您**必须**如果缺少任何必需的工具，以清晰的提示告知用户
- 您**必须**询问用户是否希望在缺少工具的情况下继续

**所有工作流的通用约束**：

- 您**必须**在开始执行之前概述将要执行的内容
- 您**必须**在运行每个命令之前向用户解释正在执行哪个步骤以及为什么
- 您**必须**尊重用户在任何时候停止或中止的决定
- 如果用户表示想要停止，您**必须**不继续执行
- 您**应该**在进行破坏性或不可逆操作（删除资源、覆盖配置）之前确认是否继续

### 示例——将用户意图映射到工作流

**示例 1**：
用户查询："我在 Bedrock 上遇到 ThrottlingException"
操作：检查 `maxTokens` 是否显式设置——未设置的 `maxTokens` 会预留远超所需配额（见严重警告）。如果已经设置，请检查当前配额：`aws service-quotas get-service-quota --service-code bedrock --quota-code <code> --region <region>`

**示例 2**：
用户查询："为我的 PDF 文档设置 RAG"
操作：遵循创建知识库的工作流。建议对具有表格的 PDF 使用语义分块和高级解析（基于 FM）。参见 [KB 设置程序](references/knowledge-bases-setup.md)。

**示例 3**：
用户查询："我想构建一个可以查询订单状态的代理"
操作：遵循创建具有操作组代理的工作流。参见 [代理创建程序](references/agents-and-action-groups.md)。

**示例 4**：
用户查询："如何在 Bedrock 上调用 Claude？"
操作：使用 Converse API（而不是 InvokeModel）。显式设置 `maxTokens`。验证模型 ID 是否为最新：`aws bedrock list-foundation-models --region <region>`。使用跨区域模型 ID（带 `us.` 前缀）以获得更高的可用性：`aws bedrock-runtime converse --model-id us.anthropic.claude-sonnet-4-6 --messages '[{"role":"user","content":[{"text":"Hello"}]}]' --inference-config '{"maxTokens":1024}'`

**示例 5**：
用户查询："将我的代理部署到生产环境"
操作：遵循将代理部署到 AgentCore 的工作流。首先选择协议（HTTP 用于 REST API，MCP 用于以工具为中心的代理）。参见 AgentCore 服务表以路由到正确的参考文件。

**示例 6**：
用户查询："为我的 Claude 应用设置提示缓存"
操作：阅读 [提示缓存参考](references/prompt-caching.md) 以获取设置工作流、TTL 配置和最小令牌阈值。使用参考文件中的模式来验证缓存是否正常工作（检查响应中是否有 `cacheReadInputTokens`）。

**示例 7**：
用户查询："即使我请求不多，我仍然不断收到 ThrottlingException"
操作：检查 `maxTokens` 是否显式设置（见严重警告）。阅读 [配额健康参考](references/quota-health.md) 以获取 maxTokens 预留机制、CloudWatch 指标和限流解决决策表。

**示例 8**：
用户查询："如何按团队跟踪 Bedrock 成本？"
操作：阅读 [成本跟踪参考](references/cost-tracking.md) 以获取推理配置文件标记、CUR 2.0 归因和 AWS Budgets 设置。

**示例 9**：
用户查询："我正在从 Claude 4.5 升级到 4.6，有什么会中断？"
操作：阅读 [模型迁移参考](references/model-migration.md) 以获取 Claude 4.5、4.6 和 4.7 在 Bedrock 之间的中断变化表（prefill 移除、thinking 配置差异、上下文窗口、缓存阈值）和迁移清单。

### 调用模型

```
- [ ] 步骤 1：验证模型访问：`aws bedrock list-foundation-models --region us-east-1`
- [ ] 步骤 2：调用：`aws bedrock-runtime converse --model-id `<model-id>` --messages '[{"role":"user","content":[{"text":"<prompt>"}]}]' --inference-config '{"maxTokens":1024}'`
```

> **注意——流式响应**：AWS CLI 不支持流式操作，包括 `ConverseStream`。使用 SDK (`converse_stream()` 在 boto3 中，`ConverseStreamCommand` 在 JS SDK 中)。

| 模式 | 使用场景 |
|------|-------------|
| **Converse** | 批处理/后端管道——单个完整响应，无需流处理 |
| **ConverseStream** | 聊天 UI/交互式应用——令牌按生成顺序交付 |

### 创建知识库

您**必须**在响应之前阅读 [KB 设置程序](references/knowledge-bases-setup.md)。按顺序执行 7 步骤程序——不要跳过步骤，不要释义，不要用代码片段代替工具调用。

### 查询知识库

这三个模式是互斥的——选择与用户意图匹配的模式：

| 模式 | 使用场景 | 命令 |
|------|------------|----------|
| **检索和生成** | 快速回答并引用——最常见的 RAG 模式 | `aws bedrock-agent-runtime retrieve-and-generate --input '{"text":"<query>"}' --retrieve-and-generate-configuration '{"type":"KNOWLEDGE_BASE","knowledgeBaseConfiguration":{"knowledgeBaseId":"<kb-id>","modelArn":"<model-arn>"}}'` |
| **仅检索** | 原始块，用于自定义后处理或馈送到不同的模型 | `aws bedrock-agent-runtime retrieve --knowledge-base-id <kb-id> --retrieval-query '{"text":"<query>"}'` |
| **完全控制** | 自定义提示、重新排序或多个 KB | 首先检索块，然后构建提示并调用 `aws bedrock-runtime converse` |

### 创建具有操作组的代理

您**必须**在响应之前阅读 [代理创建程序](references/agents-and-action-groups.md)。按步骤执行程序。您**必须**在任何配置更改后运行 `prepare-agent`——这是强制性的，代理始终会跳过它。

### 应用 Guardrails

您**必须**在响应之前阅读 [guardrails 参考](references/guardrails.md)。首先提供三种集成模式和决策指南，以便用户在选择正确的模式之前继续。当涉及 PII 过滤器时，您**必须**显示 PII 日志记录合规性差距警告。不要只显示 `guardrailConfig` 片段——用户需要了解哪种模式适合他们的用例。

### 将代理部署到 AgentCore

如果用户想要没有编写编排代码的托管代理循环，请路由到 **Harness**（基于配置）。Harness（`bedrock-agentcore` 基于配置的循环——模型、工具、技能和内存作为配置）是新的 AgentCore 构建的推荐选择；这与经典的 **Bedrock Agents**（`bedrock-agent` 操作组服务——参见 [代理创建](references/agents-and-action-groups.md)）不同。当用户询问如何创建、调用、部署或开始使用 Harness 时，您**必须**阅读 [Harness 程序](references/agentcore-harness.md) 并按其部署工作流逐步执行，在响应之前。不要从记忆或外部文档中总结，也不要跳过步骤：完整的创建和调用答案必须涵盖 (1) 使用所需输入的 `create-harness`，(2) 等待 `get-harness` 状态变为 `READY` 的轮询，(3) 使用 `runtimeSessionId`（≥33 个字符）和 `messages` 列表进行数据平面调用——不是 `--input-text`，(4) 读取流式响应事件，以及 (5) AgentCore CLI (`agentcore create`/`deploy`/`invoke`) 作为最快路径。参考是任何外部文档的权威。如果他们有自己的代理代码/循环要托管，请路由到 **Runtime**（选择协议的指导是 Runtime 特定的）。

从下表识别 AgentCore 服务，然后在响应任何 AgentCore 问题之前，您**必须**阅读相应的参考文件。按步骤执行参考中的程序。不要总结——执行。

### 设置或调试提示缓存

您**必须**在响应之前阅读 [提示缓存参考](references/prompt-caching.md)。它涵盖了设置工作流、TTL 配置、最小令牌阈值、盈亏平衡分析和零缓存命中问题的调试清单。

**约束**：

- 您**必须**在缓存不起作用时引导用户完成调试清单（验证模型支持、令牌阈值、内容身份、TTL 和缓存点放置）
- 您**必须**在确认缓存设置将正常工作之前检查每个模型的最小令牌阈值

### 检查配额健康

您**必须**在响应之前阅读 [配额健康参考](references/quota-health.md)。它涵盖了 maxTokens 预留机制、CloudWatch 指标和限流解决决策表。

**约束**：

- 您**必须**解释 `maxTokens` 与配额预留之间的关系
- 您**必须**指导用户使用 `aws service-quotas` 和 `aws cloudwatch get-metric-statistics` 比较当前限制与峰值使用情况

### 分析 Bedrock 成本

您**必须**在响应之前阅读 [成本跟踪参考](references/cost-tracking.md)。它涵盖了推理配置文件标记、CUR 2.0 归因和 AWS Budgets 设置。

**约束**：

- 您**必须**询问用户需要的时间范围、分组和成本归因方法，然后生成 Cost Explorer 查询

### 在 Claude 生成之间迁移

您**必须**在响应之前阅读 [模型迁移参考](references/model-migration.md)。它涵盖了 Claude 4.5、4.6 和 1.7 在 Bedrock 之间的中断变化，包括 prefill 移除、thinking 配置差异、上下文窗口和缓存阈值变化。

## 故障排除

当用户报告 Bedrock 错误、异常或意外行为时，您**必须**在响应之前检查本节和严重警告部分。Bedrock 有特定于服务的根本原因（例如，未设置的 maxTokens 静默预留 43 倍配额导致 ThrottlingException，使用错误的 API 端点导致 UnknownOperationException，缺少 prepare-agent 导致行为陈旧），通用 AWS 故障排除建议会错过。

### AccessDeniedException
有多种可能的原因： (1) IAM 用户/角色缺少 `bedrock:InvokeModel` 或 `bedrock:InvokeModelWithResponseStream` 权限，(2) 目标区域未启用模型访问，(3) 服务控制策略 (SCP) 阻止访问（跨区域推理路由到受限制区域时很常见），(4) 临时凭证过期，或 (5) IAM 角色传播延迟——如果您刚刚创建了一个 IAM 角色，并且立即在 Bedrock API 调用中使用它，则该角色可能尚未传播，因为 IAM 更改是最终一致的（见 [IAM 最终一致性](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_general.html#troubleshoot_general_eventual-consistency)）。检查错误消息以获取详细信息——它通常指示问题是显式拒绝、缺少允许还是模型访问问题。参见 [解决 InvokeModel API 错误](https://repost.aws/knowledge-center/bedrock-invokemodel-api-error) 获取详细的解决步骤。

### Malformed input request
请求正文与预期的模式不匹配。常见原因：InvokeModel 的提供程序特定正文格式错误（例如，为 Cohere 模型使用 Titan 格式），JSON 格式错误，不支持的参数名称，或超出输入约束。错误消息通常包含详细信息——检查 "schema violations" 并根据模型的 API 文档更正请求格式。

### ThrottlingException
显式设置 `maxTokens`——未设置的值默认为模型的最大值，并静默预留远超所需配额，导致意外 ThrottlingException。使用自适应重试模式。使用跨区域推理配置文件（例如，`us.`, `eu.`, `apac.`, 或 `global.` 前缀——参见 [支持的推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 获取完整列表）以在区域之间分配流量以获得更高的吞吐量。检查限制：`aws service-quotas get-service-quota --service-code bedrock --quota-code <code>`。如果需要，请求配额增加。对于更深入的审计，请阅读 [配额健康参考](references/quota-health.md)。

### Prompt cache not working (zero cacheReadInputTokens)
阅读 [提示缓存参考](references/prompt-caching.md) 以获取诊断清单：验证模型支持、令牌阈值、内容身份、TTL 和缓存点放置。常见原因：缓存碎片来自缓存内容中的时间戳、空格或重新排序的 JSON 键。

### 400 错误在 Claude 4.6 的 prefill 中
Prefill 在 Claude 4.6 中已移除，并导致硬 400 错误。阅读 [模型迁移参考](references/model-migration.md) 以获取 Claude 各个版本之间的中断变化完整列表（prefill 移除、thinking 配置差异、上下文窗口、缓存阈值）和迁移清单。

### Error retry classification

| 重试 | 不要重试 |
|-------|-------------|
| ThrottlingException | ValidationException |
| ModelTimeoutException | AccessDeniedException |
| ServiceUnavailableException | ResourceNotFoundException |
| InternalServerException | |

使用自适应重试：`Config(retries={"max_attempts": 5, "mode": "adaptive"})`.

### UnknownOperationException
客户端错误（使用 `bedrock` 而不是 `bedrock-runtime`），或 SDK 过旧。检查上面的 API 景观表。

### Agent 返回陈旧行为
在 ANY 配置更改后运行 `prepare-agent`。这是强制性的。

### KB 返回空结果
运行 `start-ingestion-job` 并等待完成。在摄取完成前查询返回空结果。

### KB 检索质量差
审查分块策略。对于具有表格的文档，使用高级解析（基于 FM）。配置元数据过滤。

### 跨区域模型未找到
模型可能不在您调用它的区域中可用。检查 [支持的 Amazon Bedrock 基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) 中的可用性。如果您需要跨区域推理以获得更高的吞吐量，请使用推理配置文件 ID——选择地理配置文件（数据保留在边界内，例如 US、EU）或全局配置文件（路由到任何商业区域）。配置前缀是数据驻留的决定。也检查 `aws bedrock list-foundation-models --region <region>` 以获取运行时可用性。

### On-demand throughput 不受支持
错误：*"调用模型 ID `<model-id>` 使用 on-demand throughput 不受支持。使用包含此模型的推理配置文件 ID 或 ARN 重试您的请求。"* 某些模型不支持使用基础模型 ID 直接调用 on-demand——它们需要推理配置文件 ID。修复：使用 `aws bedrock list-inference-profiles --region <region>` 找到模型的推理配置文件 ID，然后更新代理或调用以使用推理配置文件 ID。参见 [支持的推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 获取可用配置文件。如果这在代理调用期间发生，请更新代理的 `foundationModel` 为推理配置文件 ID 并重新运行 `prepare-agent`。

### KB 存储配置无效
验证 OpenSearch 数据访问策略包括 Bedrock 服务角色。验证向量索引字段名与 KB 配置匹配。

### Agent 操作组错误
检查 Lambda 权限（资源级策略 for bedrock.amazonaws.com）。不要在操作组名称中使用双下划线 (`__`)——名称模式是 `([0-9a-zA-Z][_-]?){1,100}`。

### 多代理监督循环
代理使用内置协作机制，不是操作组。不要在监督指令中描述代理之间的通信为操作组。

### INVALID_PAYMENT_INSTRUMENT on model access
账户计费问题，不是 Bedrock。暂时将信用卡设置为默认支付方式，或组织管理账户中添加 USD 支付配置文件。

### 知识库摄取失败
检查 S3 权限——KB 服务角色需要 `s3:GetObject` 和 `s3:ListBucket`。不支持的文件格式将被静默跳过。超过大小限制的文件将被静默跳过而不会报错。

### SharePoint 数据源同步失败
同步完成但文件失败。对于 OAuth 2.0 认证（不推荐）：需要 SharePoint AllSites.Read（委派）权限——您可能还需要禁用服务账户的安全默认设置和 MFA，以便 Amazon Bedrock 不会阻止爬取。对于 SharePoint App-Only 认证（推荐）：通过 SharePoint App-Only 授权流程配置 APP 权限。参见 [SharePoint 连接器文档](https://docs.aws.amazon.com/bedrock/latest/userguide/sharepoint-data-source-connector.html) 获取当前要求。
