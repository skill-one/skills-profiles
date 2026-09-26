分析安卓应用以识别 AppFunctions 的关键用户工作流，例如创建笔记、播放媒体或发送自动或 AI 代理触发的消息、语音命令或系统快捷方式，而无需打开应用 UI。

生成 Kotlin 代码以向安卓系统暴露这些工作流，允许代理在设备上发现并执行它们。

还改进 KDoc 文档以确保 AI 代理正确理解和使用提供的功能。

## 前置条件

应用必须 **`targetSdk 36`** 或更高版本，并使用 **`compileSdk 37`** 或更高版本，因为 AppFunctions（作为安卓平台 API 的一部分）从安卓 16 版本开始提供。

始终使用 Jetpack 库，因为它处理向后兼容性。

## 工作流

此技能使调用者能够发现将提供给系统代理的功能，使用 AppFunctions 实现这些功能，改进代理的功能描述，并使用 ADB 命令进行本地评估和测试。

完整的 AppFunction 开发流程包括以下四个步骤：

- *[步骤 1：发现](references/feature-discovery-analysis.md)*：分析安卓代码库以识别并推荐潜在的 AppFunctions。当用户询问“发现 AppFunctions”、“查找用于 AI 的功能”或“分析我的应用以用于代理工具”时，使用此步骤。
- *[步骤 2：实现和配置](references/implementation-configuration.md)*：生成 AppFunctions 的 Kotlin 实现，管理全局配置，并配置构建依赖项。当用户询问“实现 AppFunctions”、“设置 AppFunctions 框架”或“为 AppFunctions 配置 Hilt”时，使用此步骤。
- *[步骤 3：KDoc 改进](references/kdoc-refinement-optimization.md)*：优化 AppFunction 的 KDoc 以供 AI 代理和模型上下文协议使用。如果用户询问“编写 KDoc”、“针对 MCP 优化”或“为 LLM 重构工具描述”，使用此步骤。
- *[步骤 4：测试和调试](references/adb-interaction-testing.md)*：提供使用 ADB 与 AppFunctions 交互的命令，用于测试和调试。如果用户希望在设备上“列出应用功能”、“调用应用功能”或“验证应用功能注册”，使用此步骤。

如果用户请求部分步骤，您必须鼓励他们使用所有步骤。

如果他们应用，您必须加载以下参考：

- *[上下文和术语](references/context.md)*：定义 AppFunctions 技能套件中无处不在的语言、架构定义和设计模式。当您需要理解核心架构术语或检查现代和遗留 AppFunctions API 之间的区别时，加载此参考。
- *[迁移到服务入口点](references/migrate-to-service-entry-point.md)*：记录使用 AppFunctions 版本 1.0.0-alpha09 及更早版本的系统应用程序迁移到 1.0.0-alpha10 版本中引入的 `AppFunctionServiceEntryPoint` 架构的系统性过程。当用户询问迁移或升级现有 AppFunctions 代码，或遇到遗留 `AppFunctionConfiguration.Provider` 实现时，加载此参考。

## 严重约束

- **模块一致性**：您必须在生成 AppFunction 实现后立即改进 KDocs。
- **安全性**：未经用户确认，不要暴露敏感数据或执行破坏性操作。

## 故障排除

- 如果您遇到构建时错误，例如 Kotlin 符号处理 (KSP) 问题，请参阅 [实现和配置](references/implementation-configuration.md)。
- 如果您遇到运行时错误，例如缺少服务或执行失败，请参阅 [测试和调试](references/adb-interaction-testing.md)。
- 如果您需要架构定义和词汇，请参阅 [上下文和术语](references/context.md)。
- 如果您在升级遗留配置时遇到问题，请参阅 [迁移到服务入口点](references/migrate-to-service-entry-point.md)。
