# Opus 4.5 迁移指南

从 Sonnet 4.0、Sonnet 4.5 或 Opus 4.1 一次性迁移到 Opus 4.5。

## 迁移工作流程

1.  搜索代码库中的模型字符串和 API 调用
2.  将模型字符串更新为 Opus 4.5（见下文特定平台的字符串）
3.  移除不支持的 Beta 头部
4.  将努力参数设置为 `"high"`（见 `references/effort.md`）
5.  总结所有已做的更改
6.  告知用户："如果您在使用 Opus 4.5 时遇到任何问题，请告诉我，我可以帮助调整您的提示。"

## 模型字符串更新

识别代码库使用的平台，然后相应地替换模型字符串。

### 不支持的 Beta 头部

如果存在 `context-1m-2025-08-07` Beta 头部，请移除——它目前尚未与 Opus 4.5 兼容。添加注释说明：

```python
# 注意：1M 上下文 Beta (context-1m-2025-08-07) 尚未与 Opus 4.5 兼容
```

### 目标模型字符串（Opus 4.5）

| 平台             | Opus 4.5 模型字符串          |
|------------------|-----------------------------|
| Anthropic API (1P) | `claude-opus-4-5-20251101` |
| AWS Bedrock      | `anthropic.claude-opus-4-5-20251101-v1:0` |
| Google Vertex AI | `claude-opus-4-5@20251101` |
| Azure AI Foundry  | `claude-opus-4-5-20251101` |

### 需要替换的源模型字符串

| 源模型       | Anthropic API (1P) | AWS Bedrock      | Google Vertex AI |
|--------------|-------------------|-------------|------------------|
| Sonnet 4.0   | `claude-sonnet-4-20250514` | `anthropic.claude-sonnet-4-20250514-v1:0` | `claude-sonnet-4@20250514` |
| Sonnet 4.5   | `claude-sonnet-4-5-20250929` | `anthropic.claude-sonnet-4-5-20250929-v1:0` | `claude-sonnet-4-5@20250929` |
| Opus 4.1     | `claude-opus-4-1-20250422` | `anthropic.claude-opus-4-1-20250422-v1:0` | `claude-opus-4-1@20250422` |

**不要迁移**：任何 Haiku 模型（例如，`claude-haiku-4-5-20251001`）。

## 提示调整

Opus 4.5 与之前的模型存在已知的行为差异。**仅当用户明确要求或报告特定问题时，才应用这些修复**。默认情况下，只需更新模型字符串。

**集成指南**：添加代码片段时，不要简单地将它们附加到提示中。要深思熟虑地集成：
- 使用 XML 标签（例如，`<code_guidelines>`、`<tool_usage>`）来组织添加内容
- 匹配现有提示的样式和结构
- 将代码片段放置在逻辑位置（例如，编码指南靠近其他编码指令）
- 如果提示已使用 XML 标签，请在适当的现有标签内添加新内容，或创建一致的新的标签

### 1. 工具过度触发

Opus 4.5 对系统提示更敏感。在之前的模型上防止工具触发不足的激进语言，现在可能导致工具过度触发。

**应用条件**：用户报告工具被过于频繁或不必要地调用。

**查找并缓和**：
- `CRITICAL:` → 移除或缓和
- `You MUST...` → `You should...`
- `ALWAYS do X` → `Do X`
- `NEVER skip...` → `Don't skip...`
- `REQUIRED` → 移除或缓和

仅应用于工具触发指令。其他强调用法保持不变。

### 2. 过度设计预防

Opus 4.5 倾向于创建额外文件、添加不必要的抽象或构建未请求的灵活性。

**应用条件**：用户报告不想要的文件、过度抽象或未请求的功能。添加来自 `references/prompt-snippets.md` 的代码片段。

### 3. 代码探索

Opus 4.5 在探索代码时可能过于保守，在未读取文件的情况下就提出解决方案。

**应用条件**：用户报告模型在未检查相关代码的情况下提出修复。添加来自 `references/prompt-snippets.md` 的代码片段。

### 4. 前端设计

**应用条件**：用户要求改进前端设计质量或报告输出看起来很通用。

添加来自 `references/prompt-snippets.md` 的前端美学代码片段。

### 5. 思考敏感性

当未启用扩展思考（默认情况下）时，Opus 4.5 对 "think" 及其变体特别敏感。只有在 API 请求包含 `thinking` 参数时，扩展思考才会启用。

**应用条件**：用户报告在未启用扩展思考（请求中无 `thinking` 参数）时与 "thinking" 相关的问题。

将 "think" 替换为 "consider"、"believe" 或 "evaluate" 等替代词。

## 参考

有关要添加的每个代码片段的完整文本，请参阅 `references/prompt-snippets.md`。

有关配置努力参数（仅当用户请求时），请参阅 `references/effort.md`。
