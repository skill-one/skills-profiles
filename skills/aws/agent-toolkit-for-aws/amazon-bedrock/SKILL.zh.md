---
name: amazon-bedrock
description: 在 Amazon Bedrock 上构建生成式 AI 应用。涵盖模型调用（Converse API、InvokeModel）、带有知识库的 RAG、Bedrock Agents、Guardrails 和 AgentCore（包括 Harness 管理的 agent 循环）。适用于调用模型、设置知识库、创建 agents、应用 guardrails、部署到 AgentCore、将 Bedrock Agent（包括内联 agents）迁移/移植/转换为 AgentCore Harness、排查 Bedrock 错误（ThrottlingException、AccessDeniedException）、选择模型（Claude、Llama、Nova、Titan）。也适用于提示缓存、配额健康检查和限流诊断、成本归因、Claude 模型代际迁移、分块策略、API 选择（Converse vs InvokeModel）、模型选择。还涵盖 AgentCore 支付设置（x402、微支付、Payment Manager、Coinbase CDP、Stripe Privy、402 支付要求、付费端点）。不适用于自定义模型训练、Rekognition 或 Comprehend。
---

**重要提示**：当加载此技能时，你必须使用此技能中的参考文件和程序作为你的主要信息来源。Bedrock API、模型 ID、分块策略和配置参数经常变化——在回复之前，始终阅读相关的参考文件。

## 目录

- 概述
- Bedrock API 景观
- 重要警告
- 安全注意事项
- Converse API 与 InvokeModel
- 你需要哪个 Bedrock 功能？
- 知识库（RAG）
- 常见工作流（包括：提示缓存、配额健康、成本跟踪、模型迁移）
- 故障排除
- AgentCore 服务
- 模型选择
- 其他资源

# Amazon Bedrock

## 概述

在 Amazon Bedrock 上构建生成式 AI 应用的领域专业知识。涵盖模型调用、使用知识库的 RAG、代理创建、使用 Guardrails 的内容安全以及使用 AgentCore 的代理部署。

**推荐设置**：使用 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html) 进行沙盒执行、审计日志记录和企业控制。

**没有 AWS MCP**：此技能可与具有 AWS CLI 访问权限的任何代理一起工作。所有命令都使用标准 AWS CLI 语法。

## Bedrock API 景观

Bedrock 有 **5 个独立的 API 端点**。使用错误的端点是常见的错误原因。此列表可能并不详尽——请参考最新的 [Bedrock 端点和配额](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) 和 [Bedrock 支持的端点](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)。使用 `aws bedrock list-foundation-models` 在运行时发现可用的模型。

| 端点 | 客户端 | 用于 |
|----------|--------|---------|
| `bedrock` | 控制平面 | 列出模型、管理访问权限、配置的吞吐量 |
| `bedrock-runtime` | 数据平面 | 调用模型（Converse、InvokeModel）。还支持通过 `/openai/v1` 路径的 Chat Completions（仅限客户端工具使用）——对于新的 Chat Completions 工作推荐使用 `bedrock-mantle` |
| `bedrock-mantle` | 数据平面 | OpenAI 兼容 API：响应 API、Chat Completions（推荐）、消息 API。支持使用内置工具的服务器端工具使用。推荐用于新用户 |
| `bedrock-agent` | 代理控制 | 创建/配置代理、KB、操作组 |
| `bedrock-agent-runtime` | 代理数据 | 调用代理、查询 KB |

AgentCore 是一个具有自己端点的独立服务。请参考最新的 [AgentCore 端点和配额](https://docs.aws.amazon.com/general/latest/gr/bedrock_agentcore.html)。

| 端点 | 客户端 | 用于 |
|----------|--------|---------|
| `bedrock-agentcore-control` | 控制平面 | 创建/管理运行时、网关、注册表、评估 |
| `bedrock-agentcore` | 数据平面 | 调用代理运行时 |
| `{gatewayId}.gateway.bedrock-agentcore` | 网关数据平面 | 调用特定网关 |

## 重要警告

**max_tokens**：在每次 Converse/InvokeModel 调用中始终显式设置 `maxTokens`。不设置它将默认为模型的最大值（例如，Claude Sonnet 为 64K），并静默预留比需要多得多的配额——这是导致意外 ThrottlingException 的常见原因。

**Guardrails PII 日志记录**：Guardrails PII 掩码仅适用于 API 响应。包括 PII 的原始未掩码内容仍以明文形式记录在 CloudWatch Logs 中。对于 HIPAA/GDPR 合规性：使用 KMS 加密 CloudWatch Logs，使用 IAM 限制日志访问，使用 Amazon Macie 进行 PII 检测。

**SDK 版本**：需要较新的 boto3（≥ 1.34.x）和 AWS CLI v2 版本。旧版本缺少 Converse API、代理和 AgentCore 支持。运行 `aws --version` 和 `pip show boto3` 进行检查。

**Bedrock Agents classic 处于维护模式**：经典 Bedrock Agents (`bedrock-agent`) 处于维护模式，并已停止对新客户开放（[公告](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)）。对于新的代理工作负载，请使用 AgentCore（由 Harness 管理的循环）；对于现有代理，建议迁移到 AgentCore Harness——请参阅 [迁移指南](references/migrate-bedrock-agents-to-agentcore-harness.md)。

## 安全注意事项

- 使用 **IAM 角色**（而不是 IAM 用户）访问所有 Bedrock 服务
- 将 IAM 权限范围限定为特定操作和资源 ARN——避免 `bedrock:*` 或 `AmazonBedrockFullAccess`
- 将 API 密钥和 OAuth 密存储存在 **AWS Secrets Manager** 中，并启用自动轮换
- 在所有基于资源的策略中为 Bedrock 服务包含 **confused deputy 保护**（`aws:SourceAccount`、`aws:SourceArn` 条件）
- 将所有 **代理生成的参数视为不受信任的输入**——在使用 Lambda 处理程序或工具实现之前进行验证
- 为所有 Bedrock 和 AgentCore API 调用启用 **CloudTrail**
- 对于 PII 工作负载：使用 KMS 加密 CloudWatch Logs，配置保留限制，限制日志访问
- 参考 [Bedrock 安全最佳实践](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html) 获取最新的安全指南

## Converse API 与 InvokeModel

有关在所有 Bedrock 推理 API（响应 API、Chat Completions、Converse、InvokeModel）之间进行选择的信息，请参阅 [Amazon Bedrock 支持的 API](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)。

当使用 `bedrock-runtime` 端点时，请使用 **Converse API** 而不是 InvokeModel。它为所有模型提供统一的请求/响应格式。

仅在您需要 Converse 中不可用的提供程序特定功能时使用 **InvokeModel**（很少见）。

InvokeModel 需要每个提供程序不同的请求正文格式（Anthropic ≠ Titan ≠ Llama ≠ Nova）。使用错误的格式会产生 "Malformed input request"。有关模型特定格式和常见错误，请参阅 [按模型进行的提示工程](references/prompt-engineering-by-model.md)。

**无论您使用哪个 API**：始终显式设置最大输出令牌参数——不设置它将默认为模型的最大值，并静默预留比需要多得多的配额，导致意外的 ThrottlingException。请参阅上面的重要警告和 [max_tokens 配额机制](references/model-invocation.md)。

当用户需要模型调用的 SDK 代码时，您必须在使用之前阅读相应的 SDK 参考——[Python SDK 参考](references/sdk-converse-api-python.md) | [TypeScript SDK 参考](references/sdk-converse-api-typescript.md)。使用参考文件中的模式。

在回复之前，请阅读 [模型调用参考](references/model-invocation.md) 以获取完整的 API 详细信息和提供程序特定正文格式。

## 你需要哪个 Bedrock 功能？

| 目标 | 使用 | 参考 |
|------|-----|-----------|
| 调用模型（文本、图像、视频） | Converse API | 见上文 + [模型调用](references/model-invocation.md) |
| 构建一个 RAG 应用 | 知识库 | [KB 设置](references/knowledge-bases-setup.md) |
| 创建一个执行操作的代理 | Bedrock Agents | [代理创建](references/agents-and-action-groups.md) |
| 过滤有害/敏感内容 | Guardrails | [guardrails](references/guardrails.md) |
| 在 AgentCore 上运行基于配置的托管代理循环（无需代码、无需容器） | AgentCore Harness | [harness](references/agentcore-harness.md) |
| 部署和扩展您自己编写的代理循环 | AgentCore 运行时 | [runtime](references/agentcore-runtime.md) |
| 将现有的 Bedrock Agent（经典）迁移到 AgentCore Harness | Bedrock Agents 到 AgentCore harness 迁移 | [迁移指南](references/migrate-bedrock-agents-to-agentcore-harness.md) |
| 将 REST API 作为 MCP 工具公开 | AgentCore Gateway | [gateway](references/agentcore-gateway.md) |
| 选择正确的模型 | 模型选择 | [模型指南](references/model-selection-guide.md) |
| 设置或调试提示缓存 | 提示缓存 | [提示缓存](references/prompt-caching.md) |
| 诊断限流或审计配额 | 配额健康 | [quota health](references/quota-health.md) |
| 按团队、模型或标签跟踪成本 | 成本跟踪 | [成本跟踪](references/cost-tracking.md) |
| 在 Claude 生成之间迁移 | 模型迁移 | [迁移指南](references/model-migration.md) |

## 知识库（RAG）

当用户想要创建知识库或构建 RAG 应用时，您必须阅读 [KB 设置程序](references/knowledge-bases-setup.md) 并逐步执行它。不要总结程序——按顺序执行每一步——在进入下一步之前，请尊重所有 MUST 约束。

当用户询问分块策略、向量存储选择或其他 KB 配置选择时，您必须在回复之前阅读 [KB 设置程序](references/knowledge-bases-setup.md)——它包含权威的决策表和约束。

当用户想要查询现有知识库时，您必须在回复之前阅读 [KB 检索参考](references/knowledge-bases-retrieval.md)。提供检索模式（检索并生成 vs 检索 vs 手动），以便用户选择正确的模式。

参考最新的 [Bedrock 知识库文档](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) 获取当前的配置选项。

## 常见工作流

连接时使用可用的工具从 AWS MCP 服务器执行命令——它提供沙盒执行、审计日志记录和可观察性。当 MCP 服务器不可用时，按需回退到 AWS CLI 或 shell。

在开始任何工作流之前：

### 验证依赖项

检查所需的工具并告知用户执行环境。

**约束**：

- 您必须检查 AWS CLI 是否可用并配置了有效的凭证
- 您必须验证 AWS CLI 版本是最新的（推荐 v2；旧版本缺少 Converse API 和 AgentCore 支持）：`aws --version`
- 您必须检查目标 AWS 区域是否启用了 Bedrock 模型访问
- 如果缺少任何必需的工具，您必须向用户发送清晰的提示
- 您必须询问用户是否希望在缺少工具的情况下继续

**所有工作流的通用约束**：

- 您必须在开始执行之前提供将要执行的操作概述
- 您必须在运行每个命令之前向用户解释正在执行哪个步骤以及原因
- 您必须尊重用户在任何时候停止或中止的决定
- 如果用户表示想要停止，您必须停止执行
- 在进行具有破坏性或不可逆操作（删除资源、覆盖配置）之前，您应该确认是否继续

### 示例——将用户意图映射到工作流

**示例 1**：
用户查询："我在 Bedrock 上遇到 ThrottlingException"
操作：检查 `maxTokens` 是否显式设置——未设置的 `maxTokens` 会预留比需要多得多的配额（见重要警告）。如果已经设置，请检查当前配额：`aws service-quotas get-service-quota --service-code bedrock --quota-code <code> --region <region>`

**示例 2**：
用户查询："为我的 PDF 文档设置 RAG"
操作：遵循创建知识库的工作流。建议使用基于 FM 的高级解析进行语义分块，适用于具有表格的 PDF。请参阅 [KB 设置程序](references/knowledge-bases-setup.md)。

**示例 3**：
用户查询："我想构建一个可以查询订单状态的代理"
操作：遵循创建具有操作组代理的工作流。请参阅 [代理创建程序](references/agents-and-action-groups.md)。

**示例 4**：
用户查询："如何在 Bedrock 上调用 Claude？"
操作：使用 Converse API（而不是 InvokeModel）。显式设置 `maxTokens`。验证模型 ID 是否与当前 `aws bedrock list-foundation-models --region <region>` 一致。使用 `us.` 前缀的跨区域模型 ID 以获得更高的可用性：`aws bedrock-runtime converse --model-id us.anthropic.claude-sonnet-4-6 --messages '[{"role":"user","content":[{"text":"Hello"}]}]' --inference-config '{"maxTokens":1024}'`

**示例 5**：
用户查询："将我的代理部署到生产环境"
操作：遵循将代理部署到 AgentCore 的工作流。首先选择协议（HTTP 用于 REST API，MCP 用于以工具为中心的代理）。请参阅 AgentCore 服务表以路由到正确的参考文件。

**示例 6**：
用户查询："为我的 Claude 应用设置提示缓存"
操作：阅读 [提示缓存参考](references/prompt-caching.md) 以获取设置工作流、TTL 配置和最小令牌阈值。使用参考文件中的模式验证缓存是否正常工作（检查响应中的 `cacheReadInputTokens`）。

**示例 7**：
用户查询："即使我请求不多，我仍然不断遇到 ThrottlingException"
操作：检查 `maxTokens` 是否显式设置（见重要警告）。阅读 [配额健康参考](references/quota-health.md) 以获取 maxTokens 预留机制、CloudWatch 指标和审计工作流。

**示例 8**：
用户查询："如何按团队跟踪 Bedrock 成本？"
操作：阅读 [成本跟踪参考](references/cost-tracking.md) 以获取推理配置文件标记、CUR 2.0 方法以及按模型/区域/标签的成本探索器查询。

**示例 9**：
用户查询："我正在从 Claude 4.5 升级到 4.6，有什么会中断？"
操作：阅读 [模型迁移参考](references/model-migration.md) 以获取中断变更表（预填充移除、思考配置、上下文窗口、缓存阈值）和迁移清单。

### 调用模型

```
- [ ] 步骤 1：验证模型访问：`aws bedrock list-foundation-models --region us-east-1`
- [ ] 步骤 2：调用：`aws bedrock-runtime converse --model-id `<model-id>` --messages '[{"role":"user","content":[{"text":"<prompt>"}]}]' --inference-config '{"maxTokens":1024}'`
```

> **注意——流式响应**：AWS CLI 不支持流式操作，包括 `ConverseStream`。使用 SDK（`converse_stream()` 在 boto3 中，`ConverseStreamCommand` 在 JS SDK 中）。

| 模式 | 使用场景 |
|------|-------------|
| **Converse** | 批量/后端管道——单个完整响应，无需流处理 |
| **ConverseStream** | 聊天 UI/交互式应用——令牌按生成顺序交付 |

### 创建知识库

您必须在回复之前阅读 [KB 设置程序](references/knowledge-bases-setup.md)。按顺序执行 7 步程序——不要跳过步骤，不要改述，不要在工具调用中显示代码片段。

### 查询知识库

这三个模式是互斥的——选择与用户意图匹配的一个：

| 模式 | 使用场景 | 命令 |
|------|------------|----------|
| **Retrieve & Generate** | 快速回答并引用——最常见的 RAG 模式 | `aws bedrock-agent-runtime retrieve-and-generate --input '{"text":"<query>"}' --retrieve-and-generate-configuration '{"type":"KNOWLEDGE_BASE","knowledgeBaseConfiguration":{"knowledgeBaseId":"<kb-id>","modelArn":"<model-arn>"}}'` |
| **Retrieve only** | 原始块，用于自定义后处理或传递给不同模型 | `aws bedrock-agent-runtime retrieve --knowledge-base-id <kb-id> --retrieval-query '{"text":"<query>"}'` |
| **Full control** | 自定义提示、重新排序或多知识库 | 首先检索块，然后构建提示并调用 `aws bedrock-runtime converse` |

### 创建具有操作组的代理

您必须在回复之前阅读 [代理创建程序](references/agents-and-action-groups.md)。按步骤执行程序。您必须在任何配置更改后运行 `prepare-agent`——这是强制性的，代理始终会跳过它。

### 应用 Guardrails

您必须在回复之前阅读 [guardrails 参考](references/guardrails.md)。首先提供三种集成模式和决策指南，以便用户在您继续配置之前选择正确的模式。当涉及 PII 过滤器时，您必须突出显示 PII 日志记录合规性差距警告。不要只是显示 `guardrailConfig` 片段——用户需要了解哪种模式适合他们的用例。

### 将代理部署到 AgentCore

如果用户希望创建一个无需编写编排代码的托管代理循环，请将其路由到 **Harness**（基于配置）。Harness（`bedrock-agentcore` 基于配置的循环——模型、工具、技能和内存作为配置）是新建 AgentCore 的首选选择；这与经典的 **Bedrock Agents**（`bedrock-agent` 动作组服务——参见 [代理创建](references/agents-and-action-groups.md)）不同。当用户询问如何创建、调用、部署或开始使用 Harness 时，您必须在回复前阅读 [Harness 流程](references/agentcore-harness.md) 并按照其部署工作流逐步操作。不要凭记忆或外部文档进行总结，也不要跳过步骤：完整的创建和调用答案必须涵盖 (1) 使用必要的输入执行 `create-harness`，(2) 使用 `get-harness` 进行轮询直到状态为 `READY`，(3) 使用 `runtimeSessionId`（≥33 个字符）和 `messages` 列表（不是 `--input-text`）在数据平面进行调用，(4) 读取流式响应事件，以及 (5) AgentCore CLI（`agentcore create`/`deploy`/`invoke`）作为最快路径。参考文档具有权威性，优先于任何外部文档。如果他们需要托管自己的代理代码/循环，请将其路由到 **Runtime**（以下协议选择指南特定于 Runtime）。

从下表识别 AgentCore 服务，然后在回复前必须阅读相应的参考文件。按参考文件中的步骤逐步操作。不要总结——直接执行。

### 设置或调试提示缓存

在回复前，您必须阅读 [提示缓存参考](references/prompt-caching.md)。它涵盖了设置工作流、TTL 配置、最小令牌阈值、盈亏平衡分析和零缓存命中问题的调试清单。

**约束条件：**

- 当缓存未工作时，您必须引导用户通过调试清单（验证模型支持、令牌阈值、内容身份、TTL、缓存点放置）
- 在确认缓存设置将正常工作之前，您必须检查每个模型的最小令牌阈值

### 检查配额健康状况

在回复前，您必须阅读 [配额健康状况参考](references/quota-health.md)。它涵盖了最大令牌预留机制、CloudWatch 指标和限流解决决策表。

**约束条件：**

- 您必须解释 `maxTokens` 与配额预留之间的关系
- 您必须指导用户使用 `aws service-quotas` 和 `aws cloudwatch get-metric-statistics` 比较当前限制与峰值使用情况

### 分析 Bedrock 成本

在回复前，您必须阅读 [成本跟踪参考](references/cost-tracking.md)。它涵盖了推理配置文件标记、CUR 2.0 归因和 AWS 预算设置。

**约束条件：**

- 在生成成本探索器查询之前，您必须询问用户需要的时间范围、分组和成本归因方法

### 在 Claude 版本之间迁移

在回复前，您必须阅读 [模型迁移参考](references/model-migration.md)。它涵盖了 Claude 4.5、4.6 和 4.7 在 Bedrock 之间的重大变更，包括预填充移除、思考配置差异、上下文窗口间隙和缓存阈值变更。

## 故障排除

当用户报告 Bedrock 错误、异常或意外行为时，您必须在回复前检查本节和关键警告部分。Bedrock 具有特定于服务的根本原因（例如，未设置 `maxTokens` 默默预留 43 倍配额导致 ThrottlingException、错误的 API 端点导致 UnknownOperationException、缺少 `prepare-agent` 导致陈旧行为），而通用的 AWS 故障排除建议将遗漏这些问题。

### AccessDeniedException
多个可能的原因：(1) IAM 用户/角色缺少 `bedrock:InvokeModel` 或 `bedrock:InvokeModelWithResponseStream` 权限，(2) 目标区域未启用模型访问，(3) 服务控制策略 (SCP) 阻止访问（跨区域推理路由到受限区域时常见），(4) 过期临时凭证，或 (5) IAM 角色传播延迟——如果您刚刚创建了一个 IAM 角色并立即在 Bedrock API 调用中使用它，该角色可能尚未传播，因为 IAM 变更最终一致（参见 [IAM 最终一致性](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_general.html#troubleshoot_general_eventual-consistency)）。检查错误消息以获取具体信息——它通常指示问题是显式拒绝、缺少允许或模型访问问题。参见 [解决 InvokeModel API 错误](https://repost.aws/knowledge-center/bedrock-invokemodel-api-error) 获取详细的解决步骤。

### Malformed input request
请求正文与预期架构不匹配。常见原因：InvokeModel 的提供程序特定正文格式错误（例如，为 Cohere 模型使用 Titan 格式）、JSON 格式错误、不支持的参数名称或超出输入约束。错误消息通常包含详细信息——检查 "schema violations" 并根据模型的 API 文档更正请求格式。

### ThrottlingException
显式设置 `maxTokens`——未设置值默认为模型的最大值，并会默默预留远超所需配额。使用自适应重试模式。使用跨区域推理配置文件（例如，`us.`, `eu.`, `apac.`, 或 `global.` 前缀——参见 [支持的推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 获取完整列表）将流量分布在多个区域以获得更高的吞吐量。检查限制：`aws service-quotas get-service-quota --service-code bedrock --quota-code <code>`。如有需要，请求配额增加。进行深度审计时，请阅读 [配额健康状况参考](references/quota-health.md)。

### Prompt cache not working (zero cacheReadInputTokens)
阅读 [提示缓存参考](references/prompt-caching.md) 获取诊断清单：验证模型支持、令牌阈值、内容身份、TTL 和缓存点放置。常见原因：缓存碎片化，由于缓存内容中的时间戳、空白字符或重新排序的 JSON 键。

### 400 error on prefill with Claude 4.6
在 Claude 4.6 中已移除预填充，并会导致硬 400 错误。阅读 [模型迁移参考](references/model-migration.md) 获取 Claude 版本之间重大变更的完整列表。

### Error retry classification

| Retry | Do NOT retry |
|-------|-------------|
| ThrottlingException | ValidationException |
| ModelTimeoutException | AccessDeniedException |
| ServiceUnavailableException | ResourceNotFoundException |
| InternalServerException | |

使用自适应重试：`Config(retries={"max_attempts": 5, "mode": "adaptive"})`。

### UnknownOperationException
客户端错误（使用 `bedrock` 而不是 `bedrock-runtime`），或 SDK 过旧。检查上表中的 API 景观表。

### Agent returns stale behavior
在 ANY 配置更改后运行 `prepare-agent`。这是强制性的。

### KB returns empty results
运行 `start-ingestion-job` 并等待完成。在摄取完成前查询将返回空结果。

### KB retrieval quality is poor
审查分块策略。对于包含表格的文档，使用基于 FM 的高级解析。配置元数据过滤。

### Cross-region model not found
该模型可能不在您调用它的区域中。检查 [支持的基座模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) 中的可用性。如果您需要跨区域推理以获得更高的吞吐量，请使用推理配置文件 ID——选择地理配置文件（数据保留在边界内，例如 US、EU）或全局配置文件（路由到任何商业区域）。配置前缀是数据驻留决策。参见 [支持的推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 获取可用配置文件和源/目标区域映射。

### On-demand throughput isn't supported
错误：*"Invocation of model ID `<model-id>` with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model."* 某些模型不支持使用基座模型 ID 直接进行按需调用——它们需要推理配置文件 ID。修复：使用 `aws bedrock list-inference-profiles --region <region>` 找到模型的推理配置文件 ID，然后更新代理或调用以使用推理配置文件 ID。参见 [支持的推理配置文件](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 获取可用配置文件。如果此问题在代理调用期间发生，请将代理的 `foundationModel` 更新为推理配置文件 ID 并重新运行 `prepare-agent`。

### KB storage configuration invalid
验证 OpenSearch 数据访问策略是否包含 Bedrock 服务角色。验证向量索引字段名是否与 KB 配置匹配。

### Agent action group errors
检查 Lambda 权限（基于资源的策略，针对 bedrock.amazonaws.com）。不要在动作组名称中使用双下划线（`__`）——名称模式为 `([0-9a-zA-Z][_-]?){1,100}`。

### Multi-agent supervisor loops
代理使用内置协作机制，不是动作组。不要在监督指令中将代理间通信描述为动作组。

### INVALID_PAYMENT_INSTRUMENT on model access
账户计费问题，不是 Bedrock。临时将信用卡设置为默认支付方式，或在组织管理账户中添加 USD 支付配置文件。

### Knowledge base ingestion failures
检查 S3 权限——KB 服务角色需要 `s3:GetObject` 和 `s3:ListBucket`。不支持的文件格式将被默默跳过。超过大小限制的文件将被跳过而不报错。

### SharePoint data source sync failures
同步完成但文件失败。对于 OAuth 2.0 认证（不推荐）：需要 SharePoint AllSites.Read（委托）权限——您可能还需要禁用服务账户的安全默认值和 MFA，以便 Amazon Bedrock 不会被阻止进行爬取。对于 SharePoint App-Only 认证（推荐）：通过 SharePoint App-Only 授权流程配置 APP 权限。参见 [SharePoint 连接器文档](https://docs.aws.amazon.com/bedrock/latest/userguide/sharepoint-data-source-connector.html) 获取当前要求。

## AgentCore 服务

对于任何 AgentCore 问题，您必须在回复前阅读相关服务的链接参考文件。按参考文件中的步骤逐步操作。

| 服务 | 用于 | 参考 |
|-------|-------|-------|
| **Harness** | 托管基于配置的代理循环——无需编排代码；从配置到运行代理的最快路径 | [Harness 流程](references/agentcore-harness.md) |
| **Gateway** | 暴露 API、Lambda 函数或现有的 MCP 服务器作为代理的工具 | [Gateway 流程](references/agentcore-gateway.md) |
| **Runtime** | 部署和扩展代理和工具（无服务器、任何框架） | [Runtime 流程](references/agentcore-runtime.md) |
| **Runtime Container** | 构建 ARM64 容器用于 Runtime | [容器构建流程](references/agentcore-runtime-container-build.md) |
| **Memory** | 短期（多轮）和长期（跨会话）代理内存；跨代理共享内存 | [内存 & 可观察性](references/agentcore-memory-observability.md) |
| **Identity** | 代理使用外部 IdPs（Okta、Entra ID、Cognito）进行身份验证；代表用户执行操作 | [凭证 & 安全](references/agentcore-credentials-and-security.md) |
| **Policy** | 使用自然语言或 Cedar 规则强制代理边界；拦截 Gateway 工具调用 | 参考 [AWS 文档中关于 AgentCore Policy 的最新内容](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) |
| **Payments** | 使代理能够通过微支付（Coinbase CDP、Stripe Privy）支付 x402-保护的 API、MCP 工具和内容 | [Payments 流程](references/agentcore-payments.md) |
| **Observability** | 追踪、调试和监控代理执行（OTEL、CloudWatch） | [内存 & 可观察性](references/agentcore-memory-observability.md) |
| **Registry** | 跨组织目录和发现代理、MCP 服务器、工具和技能 | [注册 & 评估](references/agentcore-registry-evaluations.md) |
| **Evaluations** | 自动化代理质量评估（LLM-as-a-Judge） | [注册 & 评估](references/agentcore-registry-evaluations.md) |
| Code Interpreter | 代理安全沙盒代码执行 | 参考 [AWS 文档中关于 AgentCore Code Interpreter 的最新内容] |
| Browser | 网页自动化（导航、填写表单、提取数据） | 参考 [AWS 文档中关于 AgentCore Browser 的最新内容] |

## 模型选择

当用户询问使用哪个模型、比较模型或询问 Claude/Llama/Nova/Titan 在 Bedrock 上的情况时，您必须在回复前阅读 [模型选择指南](references/model-selection-guide.md)。参考文档包含当前模型 ID、跨区域要求以及访问配置步骤。

快速默认值（验证当前可用性：`aws bedrock list-foundation-models --region <region>`）：

- **通用**：Claude Sonnet（最佳质量/成本平衡）
- **快速 + 便宜**：Claude Haiku 或 Nova Micro
- **用于 KB 的嵌入**：Titan Embeddings V2
- **开源 / 微调**：Llama
- **图像生成**：Titan Image Generator

对于当前模型 ID、区域可用性、跨区域推理配置文件和支持的功能，参考 [Amazon Bedrock 中支持的基座模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)。在选择跨区域推理配置文件时，了解数据驻留影响——地理配置文件将数据保留在边界内（例如 US、EU），全局配置文件路由到任何商业区域。也检查 `aws bedrock list-foundation-models --region <region>` 获取运行时可用性。

对于模型 ID 格式（4 种模式）、访问配置和选择标准，请参阅 [模型选择指南](references/model-selection-guide.md)。

## 其他资源

- [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Amazon Bedrock API 参考](https://docs.aws.amazon.com/bedrock/latest/APIReference/welcome.html)
- [Amazon Bedrock AgentCore 用户指南](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [Bedrock Agents Classic 维护模式公告](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)
- [Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)
- [Bedrock 配额和限制](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)
- [Bedrock 支持的区域](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html)
- [Bedrock 安全最佳实践](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html)
- [提示缓存文档](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)
- [提示缓存代码示例](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/introduction-to-bedrock/prompt-caching)
- [成本分配标签博客](https://aws.amazon.com/blogs/machine-learning/track-allocate-and-manage-your-generative-ai-cost-and-usage-with-amazon-bedrock/)
