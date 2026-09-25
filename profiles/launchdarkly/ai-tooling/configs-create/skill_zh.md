# 创建配置

您正在使用一个技能，它将指导您在 LaunchDarkly 中创建配置。您的工作是理解用例、选择正确的模式、创建配置及其变体，并验证所有设置是否正确。

> **⚠️ 此技能创建配置——它不会使其可服务。** 新创建的配置的**fallthrough 指向自动生成的禁用变体**，而不是您刚刚创建的变体。SDK 在您打开目标并使 fallthrough 指向新的变体之前，每次评估都会返回 `ai_config.enabled=False`。这不是一个错误——这是默认状态。**您必须在验证 SDK 之前运行 `/configs-targeting`（或步骤 5 中显示的等效 REST / CLI 调用）**，否则验证看起来像 LD 服务路径已损坏，但实际上并没有。用户使用此技能遇到的最常见失败模式是跳过目标步骤并花费时间调试应用程序代码中的 `enabled=False`。

## 前提条件

此技能需要在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**主要 MCP 工具：**
- `setup-ai-config` -- 一步创建配置及其第一个变体（推荐）

**替代 MCP 工具（用于更多控制）：**
- `create-ai-config` -- 仅创建配置外壳（键、名称、模式）
- `create-ai-config-variation` -- 添加具有模型、提示和参数的变体
- `get-ai-config` -- 验证配置是否已正确创建

**可选 MCP 工具（增强工作流）：**
- `list-ai-configs` -- 浏览现有配置以了解命名约定
- `create-project` -- 如果尚不存在，则创建项目

## 重要提示：偏向行动

当用户提供足够的上下文（用例、模型、模式）时，不要停止询问可以推断的详细信息，直接通过整个工作流。为未指定字段使用合理默认值：`default` 用于变体键，用例作为指令/消息的基础，kebab-case 用于配置键。一次通过（创建 + 验证）完成所有步骤。

## 工作流

### 第 1 步：理解用例

创建之前，确定您正在构建的内容：

- **使用什么框架？** LangGraph、LangChain、CrewAI、Strands、OpenAI SDK、Anthropic SDK、自定义
- **代理需要什么？** 仅文本生成，还是工具/函数调用？
- **代理还是完成？** 请参阅下方的决策矩阵

### 第 2 步：选择代理模式 vs 完成模式

这个选择是关于**输入模式和框架兼容性**，而不是执行行为。代理模式返回一个 `instructions` 字符串；完成模式返回一个 `messages` 数组。两者都提供提供商抽象、A/B 测试和指标跟踪。

| 您的需求 | 模式 | 原因 |
|-----------|------|-----|
| LangGraph、CrewAI、Strands、AutoGen 框架 | **代理** | 框架期望目标/指令输入 |
| 跨交互的持久指令 | **代理** | 单个指令字符串，SDK 方法：`agent_config()`（Python） / `agentConfig()`（Node） |
| 直接 OpenAI/Anthropic API 调用 | **完成** | 消息数组直接映射到提供商 API |
| 完全控制消息结构 | **完成** | 基于角色（系统/用户/助手）的消息 |
| 一次性文本生成 | **完成** | 标准聊天格式 |
| 需要在线评估（LLM 作为裁判） | **完成** | 在线评估仅在完成模式下可用 |

**两种模式都支持工具。** 并非所有模型都支持代理模式——如果使用代理模式，请检查模型兼容性。如果不确定，请从完成模式开始（它是 API 默认值，更灵活）。

### 第 3 步：创建配置（推荐：一步完成）

使用 `setup-ai-config` 一次性创建配置及其第一个变体。这是推荐的方法：它自动处理创建、变体设置和验证。

**配置字段：**
- `key` -- 唯一标识符（小写，连字符）
- `name` -- 人类可读的名称
- `mode` -- `"agent"` 或 `"completion"`
- 可选：`description`, `tags`

**变体字段：**
- `variationKey`, `variationName` -- 第一个变体的标识符
- `modelConfigKey` -- 必须为 `Provider.model-id` 格式（例如，`OpenAI.gpt-4o`，`Anthropic.claude-sonnet-4-5`）
- `modelName` -- 模型标识符（例如，`gpt-4o`）。**始终在初始调用中传递此值**——不传递它会产生一个显示 "NO MODEL" 的变体，并强制进行第二次 PATCH 来设置它。该字段是 `modelName`；在**此端点**上它**不是** `name` 或 `model.name`。

**对于代理模式**，提供：
- `instructions` -- 包含代理系统指令的字符串

代理模式示例调用：
```json
{
  "projectKey": "my-project", "key": "support-agent", "name": "Support Agent",
  "mode": "agent", "variationKey": "default", "variationName": "Default",
  "modelConfigKey": "OpenAI.gpt-4o", "modelName": "gpt-4o",
  "instructions": "You are a customer support agent. Help users resolve their issues."
}
```

**对于完成模式**，提供：
- `messages` -- 包含 `{role, content}` 对象的数组（系统、用户、助手）

完成模式示例调用：
```json
{
  "projectKey": "my-project", "key": "product-descriptions", "name": "Product Descriptions",
  "mode": "completion", "variationKey": "default", "variationName": "Default",
  "modelConfigKey": "Anthropic.claude-sonnet-4-5", "modelName": "claude-sonnet-4-5",
  "messages": [
    {"role": "system", "content": "You are a product copywriter. Write compelling descriptions."},
    {"role": "user", "content": "Write a description for: {{product_name}}"}
  ]
}
```

**可选：**
- `parameters` -- 模型参数，如 `{temperature: 0.7, max_tokens: 2000}`（匹配 UI 的 snake_case 键）

工具返回带有变体的完整验证配置详细信息。

### 第 3 步（替代）：两步创建

如果用户希望更多控制或分步方法，请使用单个工具：

1. `create-ai-config` -- 创建配置外壳
2. `create-ai-config-variation` -- 添加具有模型、提示和参数的变体
3. `get-ai-config` -- 验证结果

**不要停止询问详细信息并执行所有三个步骤。** 从用户请求的上下文中推断变体键（`default`）、名称（`Default`）、指令/消息和模型。如果用户要求 GPT-4o 代理模式，您就有足够的信息完成整个流程。只有在模式或模型确实不明确的情况下，才询问澄清问题。

### 第 4 步：验证

如果您使用了 `setup-ai-config`，验证是自动的：响应包含完整的配置和变体。检查：

1. 配置存在且模式正确
2. 变体已分配模型（不是 "NO MODEL"）
3. 指令或消息存在
4. 参数已设置

**使用 `get-ai-config` 进行验证调用——不要降到原始 `curl` + `jq`。** MCP 工具返回您可以直接检查的 typed 对象。手写的 `jq` 过滤器针对 REST 响应通常会中断：配置详情端点根据 `expand` 返回变体列表在不同键下，而像 `.variations.items[]` 这样的过滤器会在响应形状是裸数组时失败，报错 "Cannot index array with string 'items'"。如果您必须调用 REST API，请先用 `jq -e .` 检查实际形状，然后再深入挖掘。

**报告结果：**
- 配置以正确的结构创建
- 变体已分配模型
- 标记任何缺失的模型或参数
- 提供配置 URL：`https://app.launchdarkly.com/projects/{projectKey}/ai-configs/{configKey}`

### 第 5 步：使变体可服务

`setup-ai-config` 和 `create-ai-config-variation` 创建变体，但**不会将其提升为 fallthrough**。新配置将对每个消费者返回 `enabled=False`，直到目标更新。这是最常见的 "我创建了配置，但我的 SDK 仍然获取回退" 失败。**工作流在完成此步骤之前未完成。**

#### 要告诉用户什么

在步骤 4 后将此清单原样打印给用户，然后等待确认。在用户确认 fallthrough 已翻转之前，不要声称技能成功。

> ✅ 配置和变体已创建。
>
> 🔴 **SDK 在您打开目标之前会返回 `enabled=False`。** fallthrough 目前指向自动生成的禁用变体，而不是您刚刚创建的 `{variationKey}`。
>
> **下一步——运行 `/configs-targeting`** 并使用以下输入：
> - 项目键：`{projectKey}`
> - 配置键：`{configKey}`
> - 环境键：SDK 键在 `.env` 中的环境（通常是 `test` 或 `production`）
> - fallthrough 变体：`{variationKey}`（此技能刚刚创建的）

在翻转目标后验证：
1. 在 LD UI 中打开配置，切换到正确环境，并确认 "Default rule serves: `{variationName}`" 显示为目标 **On**。
2. 运行快速测试：`ai_config = ai_client.{completion|agent}_config(...)` 并断言 `ai_config.enabled is True`。

#### 如果用户想在不调用兄弟技能的情况下翻转目标

`configs-targeting` 是标准路径——它处理百分比发布、目标规则和变体 ID 查找。但对于最简单的情况（在单个环境中将新变体提升为 fallthrough），一旦您知道新变体的 `_id`，您可以自己运行底层的语义 PATCH。

获取变体 ID（使用 `get-ai-config` MCP，或）：
```bash
curl -s "https://app.launchdarkly.com/api/v2/projects/$PROJECT/ai-configs/$CONFIG_KEY/targeting?env=$ENV" \
  -H "Authorization: $LD_API_KEY" -H "LD-API-Version: beta" \
  | jq '.variations[] | {key, _id}'
```

将 fallthrough 指向它：
```bash
curl -X PATCH "https://app.launchdarkly.com/api/v2/projects/$PROJECT/ai-configs/$CONFIG_KEY/targeting?env=$ENV" \
  -H "Authorization: $LD_API_KEY" \
  -H "Content-Type: application/json; domain-model=launchdarkly.semanticpatch" \
  -H "LD-API-Version: beta" \
  -d '{"instructions":[{"kind":"updateFallthroughVariationOrRollout","variationId":"<id-from-step-above>"}]}'
```

或者如果本地安装了 LD CLI，通过 LD CLI 执行相同操作：
```bash
ldcli resources ai-configs update-ai-config-targeting \
  --projectKey $PROJECT --configKey $CONFIG_KEY --envKey $ENV \
  --data '{"instructions":[{"kind":"updateFallthroughVariationOrRollout","variationId":"<id>"}]}'
```

不要使用 `turnTargetingOn`——该语义 PATCH 指令**不**适用于配置。`updateFallthroughVariationOrRollout` 是唯一实际翻转 fallthrough 的指令。

## modelConfigKey 格式

模型在 UI 中显示所需的格式。格式：`{Provider}.{model-id}`

- `OpenAI.gpt-4o`
- `OpenAI.gpt-4o-mini`
- `Anthropic.claude-sonnet-4-5`
- `Anthropic.claude-3-5-sonnet`

`create-ai-config-variation` 工具验证此格式并拒绝无效值。

## 边缘情况

| 情况 | 操作 |
|-----------|------|
| 配置已存在 | 询问用户是否要更新 |
| 变体显示 "NO MODEL" | 使用 `update-ai-config-variation` 设置 modelConfigKey |
| 需要附加工具 | 先创建工具（`tools` 技能），然后更新变体 |

## 不要做什么

- 不要在不理解用例的情况下创建配置
- 不要跳过两步过程（配置然后变体）
- 不要在初始创建时尝试附加工具——之后更新变体
- 不要忘记 modelConfigKey（模型不会在 UI 中显示）
- 不要在初始变体调用中省略 `modelName`。它在创建时是必需的；通过后续 PATCH 设置它是针对一个错误的 workaround，而不是预期流程。PATCH 字段也是 `modelName`，而不是 `name`。
- 不要降到原始 `curl` + `jq` 进行验证。使用 `get-ai-config`（MCP）——它返回 typed 对象并避免在响应形状变化时中断的脆弱 `jq` 过滤器。
- 不要认为工作流在用户被告知运行 `configs-targeting` 之前完成。未提升为 fallthrough 的创建变体会对每个消费者返回 `enabled=False`。

## 更多资源

要了解如何在 LaunchDarkly UI 中创建配置，请阅读 [创建配置](https://launchdarkly.com/docs/home/agentcontrol/create.md)

要了解如何配置 SDK，请阅读：

* [.NET AI SDK 参考](https://launchdarkly.com/docs/sdk/ai/dotnet.md)
* [Go AI SDK 参考](https://launchdarkly.com/docs/sdk/ai/go.md)
* [Node.js（服务器端）SDK AI 参考](https://launchdarkly.com/docs/sdk/ai/node-js.md)
* [Python AI SDK 参考](https://launchdarkly.com/docs/sdk/ai/python.md)
* [Ruby AI SDK 参考](https://launchdarkly.com/docs/sdk/ai/ruby.md)

## 相关技能

- `tools` -- 在附加之前创建工具
- `configs-variations` -- 添加更多变体进行实验
- `configs-update` -- 根据学习结果修改配置
