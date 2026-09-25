# 代理模式

使用以下步骤来规划或实现新的模式。模式是一种管理代理上下文并注入与产品、用例、JTBD（任务、目标、行为）等相关的工具、提示和模式相关行为的方式。代理具有 `switch_mode` 工具，允许其切换到另一个模式，这可能改变工具、提示和可执行文件，同时保留当前上下文。一些先前创建的工具是上下文相关的，这意味着它们会在前端特定页面上注入。模式会改变方法，并且始终在模式上下文中包含工具。

## 确定模式名称

探索 `ee/hogai/core/agent_modes/presets` 目录，检查是否已有符合用户意图的模式。如果您想创建新模式，应将其范围限定为 PostHog 产品（产品分析）、产品领域（SQL）或代理（仪器化代理）。

## (可选) 在架构中创建新模式

将新的 AgentMode 添加到 `frontend/src/queries/schema/schema-assistant-messages.ts`，并使用以下命令重新生成架构：

```bash
hogli build:schema
```

或者，您可以使用此命令：

```bash
pnpm run schema:build
```

## 创建或更新模式的脚手架

模式通常应至少包含以下内容：

- 一个 AgentToolkit，用于暴露特定于模式的工具，并为待办工具提供轨迹示例。
- 一个 AgentModeDefinition，包含 AgentMode、始终注入到代理上下文窗口的模式描述，以及用于工具和可执行文件的类。

注意：您只有在用户需要修改该模式的提示、行为或执行循环本身时，才应创建新的可执行文件。

## 向模式添加工具

相关工具可能位于 `ee/hogai/tools` 或 `products/<product_name>/backend/max_tools`。有一组工具始终会注入到上下文中，例如 `read_data` 工具，但所有其他工具都应特定于该模式。

在将工具添加到工具包之前，确定这些工具是否有工具依赖关系。如果有依赖关系（例如实验依赖于功能标志创建），请返回用户以确定他们是否希望将模式合并为单一模式。如果他们不想这样做，请确保您稍后添加一个轨迹示例，清楚地解释模式切换和工具选择。

您还应该验证这些工具是否以后台优先的方式运行。如果工具在不将适当上下文传递回对话的情况下应用前端更改，您应该提出一种方法，使它们以后台优先的方式运行，以便代理具有正确的上下文。

## 审查默认工具包

如果新模式包含新的 Django 模型，您应该审查 `read_data`、`search` 和 `list_data` 工具是否具有检索这些模型的功能。如果它们不支持这些模型，您应该使用或实现 `ee/hogai/context/...` 中可用的上下文提供程序之一。

## 编写类似 JTBD 的轨迹示例

更新 AgentToolkit 以包含轨迹示例。这些示例应该是 JTBD 风格的示例，展示代理如何使用可用工具完成典型任务。参考产品分析预设。

## 实现前端

更新 `max-constants.tsx` 以包含新工具，并将模式添加到模式选择器。您可能还需要创建新的 UI 元素来显示工具的数据。

### 示例

假设您已更新错误跟踪工具以列出问题。它曾经是一个仅更新过滤器的前端工具，但现在输出错误跟踪问题。虽然代理具有所需的上下文，但用户也需要以人类可读的方式查看这些问题。在这种情况下，您应该设计和实现一个新的组件来显示工具的输出。

## 添加功能标志

所有新模式都必须进行功能标志。示例：

```ee/hogai/chat_agent/mode_manager.py
    @property
    def mode_registry(self) -> dict[AgentMode, AgentModeDefinition]:
        registry = dict(DEFAULT_CHAT_AGENT_MODE_REGISTRY)
        if has_error_tracking_mode_feature_flag(self._team, self._user):
            registry[AgentMode.ERROR_TRACKING] = error_tracking_agent
        return registry
```

如果您创建了新工具，请确保您正确地进行功能标志：

1. 正在迁移的旧工具在功能标志激活时不应可用。
2. 新工具只有在功能标志激活时才可用。

## 实施和更新测试

您应该测试新工具、预设、可执行文件，并可选地实施 evals。
