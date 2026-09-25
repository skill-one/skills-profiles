# 配置提示片段

您正在使用一项技能，该技能将指导您在 LaunchDarkly 中创建和管理提示片段。您的工作是识别可重用文本、创建片段、在配置变体中引用它们，并验证所有内容是否正确连接。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-prompt-snippet` -- 创建新的可重用文本块
- `list-prompt-snippets` -- 浏览项目中的现有片段
- `get-prompt-snippet` -- 检查特定片段的内容

**可选的 MCP 工具：**
- `update-prompt-snippet` -- 编辑片段的文本、名称或标签
- `delete-prompt-snippet` -- 永久删除片段
- `update-ai-config-variation` -- 更新变体提示以引用片段

## 核心概念

### 提示片段是什么？

提示片段是存储在项目级别的、带版本控制的命名文本块。它们包含可重用的提示文本片段——角色、安全护栏、输出格式说明、领域知识——这些片段可以在多个配置变体之间共享。

当片段被更新时，会创建一个新版本。引用该片段的配置变体可以获取最新版本，以保持所有配置同步。

### 何时使用片段

| 场景 | 示例 |
|----------|---------|
| **共享角色** | "您是 Acme Corp 的友好、知识渊博的客户支持代理..." 由 5 个不同的配置使用 |
| **安全护栏** | "永远不要透露内部定价。永远不要生成访问生产数据库的代码。" |
| **输出格式** | "始终以 JSON 格式响应，键：answer、confidence、sources。" |
| **领域知识** | 公司特定术语、产品名称或流程描述 |
| **监管文本** | 每个响应都必须出现的合规声明 |

### 何时**不**使用片段

- 仅适用于单个变体的文本——直接将其放入提示中
- 按请求变化的动态内容——使用模板变量
- 完整的提示——片段是构建块，不是完整的提示

## 核心原则

1. **优先可重用性**：只有当文本将在 2 个以上位置使用时才创建片段
2. **单一职责**：每个片段应涵盖一个关注点（角色**或**安全护栏，不能两者兼有）
3. **描述性键**：使用键如 `safety-guardrails`、`json-output-format`、`support-persona`
4. **按类别标签**：添加标签以便团队成员按类别查找片段
5. **验证引用**：创建片段后，确认它在项目中出现

## 工作流程

### 第 1 步：识别可重用文本

在创建片段之前，了解共享内容：

1. 使用 `get-ai-config` 为每个项目列出现有配置
2. 查找变体提示中重复的文本
3. 识别应保持一致的文本（安全护栏、角色、格式）
4. 使用 `list-prompt-snippets` 检查现有片段，以避免重复

### 第 2 步：创建片段

使用 `create-prompt-snippet` 并提供：
- `key` -- 唯一标识符（小写、连字符，例如 `safety-guardrails`）
- `name` -- 人类可读的显示名称
- `text` -- 可重用的提示文本内容
- `description` (可选) -- 解释何时/为何使用此片段
- `tags` (可选) -- 按类别分类以供查找（例如 `["guardrails", "safety"]`）

```json
{
  "projectKey": "my-project",
  "key": "support-persona",
  "name": "Customer Support Persona",
  "text": "You are a friendly, knowledgeable customer support agent for Acme Corp. Always greet the customer by name when available. Be empathetic but concise. If you don't know the answer, say so honestly and offer to escalate.",
  "description": "标准角色，用于所有面向客户的支持配置",
  "tags": ["persona", "support"]
}
```

### 第 3 步：验证

1. 使用 `get-prompt-snippet` 确认片段是否以正确的文本创建
2. 使用 `list-prompt-snippets` 在项目列表中查看它
3. 确认新创建的片段版本号为 1

**报告结果：**
- 创建了具有键、名称和文本的片段
- 确认了版本号
- 标签应用正确

### 第 4 步：更新片段（按需）

使用 `update-prompt-snippet` 修改现有片段。仅传递您要更改的字段：

```json
{
  "projectKey": "my-project",
  "snippetKey": "safety-guardrails",
  "text": "更新了安全护栏文本，包含新的合规要求..."
}
```

每次更新都会创建一个新版本。引用该片段的现有配置变体可以获取新版本。

## 边缘情况

| 情况 | 操作 |
|-----------|--------|
| 片段键已存在 | 使用 `get-prompt-snippet` 检查，然后更新或选择不同的键 |
| 非常长的文本 | 片段可以容纳大块文本——但考虑拆分为多个片段以提高模块化 |
| 片段被配置引用 | 小心更新——更改将传播到所有引用配置 |
| 删除被引用的片段 | 警告用户配置将丢失引用。使用 `delete-prompt-snippet` 并设置 `confirm: true` |

## 不应做的事情

- 不要为仅在一个地方使用的文本创建片段
- 不要将整个提示放入单个片段——将其拆分为专注的片段
- 不要在不检查哪些配置引用它们的情况下删除片段
- 不要重复现有片段——先使用 `list-prompt-snippets` 检查

## 更多资源

要了解有关在 LaunchDarkly UI 中设置提示片段的更多信息，请阅读 [提示片段](https://launchdarkly.com/docs/home/agentcontrol/snippets.md)。
