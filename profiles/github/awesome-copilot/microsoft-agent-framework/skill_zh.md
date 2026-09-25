# Microsoft Agent Framework

在使用基于 Microsoft Agent Framework 构建的应用程序、代理、工作流或迁移时，请使用此技能。

Microsoft Agent Framework 是 Semantic Kernel 和 AutoGen 的统一继承者，它结合了它们的优势并引入了新功能。由于它目前仍处于公共预览阶段且变化迅速，因此在实施建议时，应始终以最新的官方文档和示例为基础，而不是依赖过时的知识。

## 首先确定目标语言

在提供建议或代码更改之前，请先选择语言工作流：

1. 当存储库包含 `.cs`、`.csproj`、`.sln`、`.slnx` 或其他 .NET 项目文件，或用户明确要求 C# 或 .NET 指导时，使用 **.NET** 工作流。遵循 [references/dotnet.md](references/dotnet.md)。
2. 当存储库包含 `.py`、`pyproject.toml`、`requirements.txt`，或用户明确要求 Python 指导时，使用 **Python** 工作流。遵循 [references/python.md](references/python.md)。
3. 如果存储库包含两个生态系统，则匹配正在编辑的文件使用的语言或用户声明的目标语言。
4. 如果语言不明确，请先检查当前工作区，然后选择最接近的语言特定参考。

## 始终参考实时文档

- 首先阅读 Microsoft Agent Framework 概述：<https://learn.microsoft.com/agent-framework/overview/agent-framework-overview>
- 优先使用当前 API 表面的官方文档和示例。
- 在可用时，使用 Microsoft Docs MCP 工具来获取最新的框架指导示例。
- 将旧的 Semantic Kernel 或 AutoGen 模式视为迁移输入，而不是默认的实现模型。

## 共享指导

在任何语言中使用 Microsoft Agent Framework 时：

- 使用异步模式进行代理和工作流操作。
- 实现显式的错误处理和日志记录。
- 优先使用强类型、清晰的接口和可维护的组合模式。
- 在适用 Azure 身份验证时使用 `DefaultAzureCredential`。
- 使用代理进行自主决策、临时规划、对话流程、工具使用和 MCP 服务器交互。
- 使用工作流进行多步骤编排、预定义执行图、长时间运行的任务和人工介入场景。
- 支持模型提供者，如 Azure AI Foundry、Azure OpenAI、OpenAI 等，但在符合用户需求时，优先为新项目使用 Azure AI Foundry 服务。
- 在适用时，使用基于线程或等效的状态处理、上下文提供者、中间件、检查点、路由和编排模式。

## 迁移指导

- 如果从 Semantic Kernel 迁移，请使用官方迁移指南：<https://learn.microsoft.com/agent-framework/migration-guide/from-semantic-kernel/>
- 如果从 AutoGen 迁移，请使用官方迁移指南：<https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/>
- 首先保留行为，然后逐步采用原生的 Agent Framework 模式。

## 工作流

1. 确定目标语言并阅读匹配的参考文件。
2. 在做出实施选择之前，获取最新的官方文档和示例。
3. 应用此技能中的共享代理和工作流指导。
4. 使用所选参考的语言特定包、存储库、示例路径和编码实践。
5. 当存储库中的示例与当前文档不同时，解释差异并遵循当前支持的模式。

## 参考

- [.NET 参考](references/dotnet.md)
- [Python 参考](references/python.md)

## 完成标准

- 建议与目标语言匹配。
- 包名、存储库路径和示例位置与所选生态系统匹配。
- 指导反映当前 Microsoft Agent Framework 文档，而不是遗留假设。
- 迁移建议仅在相关时提及 Semantic Kernel 和 AutoGen。
