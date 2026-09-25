# 配置变体

您正在使用一项技能，它将指导您通过变体进行测试和优化配置。您的工作是设计实验、创建变体，并系统地找到最佳方案。

## 前置条件

此技能需要您的环境中配置了远程托管的 LaunchDarkly MCP 服务器。

**主要 MCP 工具：**
- `clone-ai-config-variation` -- 克隆基准变体并进行选择性覆盖（推荐用于实验）

**替代 MCP 工具（用于更多控制）：**
- `get-ai-config` -- 在添加新变体前查看现有变体
- `create-ai-config-variation` -- 从零开始创建新变体

**可选 MCP 工具：**
- `update-ai-config-variation` -- 创建后细化变体
- `delete-ai-config-variation` -- 删除未成功的变体

## 核心原则

1. **一次测试一个变量**：模型、提示或参数，一次只改一个
2. **有假设**：知道您试图改进什么
3. **衡量结果**：使用指标比较变体
4. **通过工具验证**：代理获取配置以确认变体存在

## 工作流程

### 第 1 步：确定要优化的内容

问题是什么？成本、质量、速度、准确性？您将如何衡量成功？

### 第 2 步：设计实验

| 目标 | 要变化的变量 |
|------|--------------|
| 降低成本 | 更便宜的模型（例如，`gpt-4o-mini`） |
| 提高质量 | 更好的模型或更详细的提示 |
| 减少延迟 | 更快的模型，较低的 `max_tokens` |
| 提高准确性 | 不同的模型系列（Claude vs GPT-4） |

### 第 3 步：创建变体（推荐：克隆并覆盖）

使用 `clone-ai-config-variation` 复制基准并仅覆盖您正在测试的内容。该工具读取源变体，合并您的覆盖，并创建新变体。您**未**传递的所有内容将自动从源继承。

**必填字段：**
- `sourceVariationKey` -- 要克隆的基准
- `key` 和 `name` -- 新变体的标识符（例如，`gpt4o-mini-cost-test`）

**仅覆盖您正在测试的字段。** 留空所有其他字段——即使您知道它们的当前值也不要传递。克隆工具会从源继承它们。这强制执行一次一个变量的原则：

- 测试更便宜的模型？仅传递 `modelConfigKey` 和 `modelName`。不要传递 `instructions`、`messages` 或 `parameters`。
- 测试不同的指令？仅传递 `instructions`。不要传递 `modelConfigKey` 或 `modelName`。
- 测试参数？仅传递 `parameters`。不要传递模型或提示字段。

响应将返回源和创建的变体，以便您可以立即验证差异。

### 第 3 步（替代方案）：从零开始创建

如果您需要完全控制，请先使用 `get-ai-config` 查看当前状态，然后使用 `create-ai-config-variation` 手动指定所有字段创建。始终在创建前获取，以便了解现有配置的模式、模型和参数。

### 第 4 步：验证

如果您使用了 `clone-ai-config-variation`，响应将包含源和创建的变体以供立即比较。否则，使用 `get-ai-config` 确认。

**报告结果：**
- 使用正确模型和参数创建的变体
- 变体之间仅预期的变量不同
- 标记任何问题

**关于 API 响应的说明：** 调用创建或克隆工具后，将成功响应视为操作成功的确认。API 响应可能不会回显您发送的每个字段（例如，模型字段可能显示默认值）。不要仅根据响应字段值重试或假设失败——如有必要，使用 `get-ai-config` 进行验证。

## modelConfigKey 格式

模型在 UI 中显示所需的格式：`{Provider}.{model-id}`：
- `OpenAI.gpt-4o`, `OpenAI.gpt-4o-mini`
- `Anthropic.claude-sonnet-4-5`, `Anthropic.claude-3-5-sonnet`

## 安全：保护基准

当用户想要尝试不同的模型、提示或参数时，**始终与基准一起创建新的变体**。切勿修改或删除现有的基准变体。即使用户说“替换”或“切换”，这也适用——正确的操作是创建新变体，并让目标/发布控制流量，而不是编辑原始配置。

- 使用 `clone-ai-config-variation` 或 `create-ai-config-variation` 添加新变体
- 不要在基准上使用 `update-ai-config-variation` 改变其模型或指令
- 不要在基准上使用 `delete-ai-config-variation`
- 向用户解释保留基准可以实现比较和安全回滚

## 不要做的事情

- 不要一次测试太多东西——每个变体只改一个变量
- 克隆时不要传递未更改的字段——让工具从源继承
- 不要忘记 `modelConfigKey`（没有它的变体在 UI 中显示为“NO MODEL”）
- 不要在小样本量上做决定
- 不要修改或删除基准变体——与它一起创建新变体
- 不要使用 `update-ai-config-variation` 来“替换”基准——创建新变体代替

## 更多资源

要了解更多关于创建和管理变体的信息，请阅读 [Create and manage config variations](https://launchdarkly.com/docs/home/agentcontrol/create-variation.md)。

## 相关技能

- `configs-create` -- 创建初始配置
- `configs-update` -- 基于学习进行细化
