# LaunchDarkly SDK 安装（引导）

按照**三个嵌套步骤的顺序**安装和初始化用户项目的正确 LaunchDarkly SDK。**不要**在此处跳转到功能标志——父级 [LaunchDarkly 引导](../SKILL.md) 继续进行 **步骤 4：第一个标志**。

## 前置条件

- 来自父级 **步骤 1：探索项目** 的项目上下文（重用它；如果存在不明确的情况，仅重新运行深度检测）
- **SDK 密钥 / 客户端 ID / 移动端密钥**：在您达到 [应用代码更改](apply/SKILL.md) 时需要（环境连接）。**不要**在检测或计划阶段仅因为您打开了此技能而向用户索要这些信息——请遵循父级引导：账户状态通过 MCP OAuth 授权进行推断（当 MCP 已配置时），或在 D7 应用中显示；密钥材料在应用时收集（参见父级 [前置条件](../SKILL.md#prerequisites)）。

## 密钥类型（摘要）

| SDK 类型    | 变量（逻辑）        | LaunchDarkly 中的来源        |
|-------------|---------------------------|-------------------------------|
| 服务器端    | `LAUNCHDARKLY_SDK_KEY`    | 环境 → SDK 密钥        |
| 客户端      | 客户端 ID（捆绑器前缀环境名称） | 环境 → 客户端 ID |
| 移动端      | `LAUNCHDARKLY_MOBILE_KEY` | 环境 → 移动端密钥     |

**永远不要硬编码密钥。** 完整环境规则、同意和捆绑器表：[应用代码更改](apply/SKILL.md) 步骤 2。

## 工作流程 — 按顺序运行这些嵌套技能

除非 [检测决策树](detect/SKILL.md#decision-tree) 短路（例如仅跳转到应用），否则执行**所有三个**。每个嵌套技能可能包含决策点——一些 **阻塞**（标记为 `D<N> -- BLOCKING`，您必须调用您的结构化问题工具并等待用户的响应才能继续）和一些 **非阻塞**（您展示信息并继续，除非用户反对）。**不要**跨阻塞边界批量工具调用。

| 顺序 | 嵌套技能 | 角色 |
|-------|----------------|------|
| 1 | [检测仓库堆栈](detect/SKILL.md) | 语言、包管理器、单体仓库目标、入口点、现有 LD 使用 |
| 2 | [生成集成计划](plan/SKILL.md) | SDK 选择、要更改的文件、环境计划——向用户展示（非阻塞；参见 plan SKILL.md D6） |
| 3 | [应用代码更改](apply/SKILL.md) | 安装包、`.env` / 带同意的密钥、初始化代码、编译检查（当 [双 SDK 计划](plan/SKILL.md#dual-sdk-integrations) 时 **两者** 都需要） |

所有步骤的共享参考：[SDK 配方](../references/sdk/recipes.md)、[SDK 片段](../references/sdk/snippets/)。

### 完成步骤 3 后

继续父级技能：

- **步骤 4：** [第一个标志](../SKILL.md#step-4-first-flag)

除非用户明确需要一个可丢弃的检查，否则**不要**在此技能中添加独立的“示例标志”评估；父级流程按顺序创建第一个标志。

## 指南

- 匹配现有代码库的导入、配置和样式约定。
- 在 TypeScript 项目中优先使用 TypeScript。
- 如果项目使用共享配置层，请在其中初始化 LaunchDarkly。
- 当项目使用 dotenv 时，添加 `.env.example` 条目。
- **依赖范围：** 仅从配方添加 LaunchDarkly SDK 包，除非用户**明确批准**升级或添加其他包（[应用 — 在更改其他依赖关系之前获得权限](apply/SKILL.md#permission-before-changing-other-dependencies)）。

## 边缘情况

- **多个环境（例如 Next.js 服务器 + 客户端）或用户要求前端 + 后端：** 使用 **双 SDK** [计划](plan/SKILL.md#dual-sdk-integrations) 并 [应用](apply/SKILL.md) **两个** 包和 **两个** 初始化——永远不要在没有锁文件 + 入口点证据的情况下将第二个 SDK 总结为已完成。
- **单体仓库：** 集成父级引导中用户选择的项目包；保持在该子树中。
- **SDK 已安装并初始化：** 父级可能会跳过此交接——参见父级 **边缘情况** 和 [检测决策树](detect/SKILL.md#decision-tree)。
- **不支持的或不常见的技术栈：** 使用 [SDK 配方](../references/sdk/recipes.md) 和 [完整 SDK 目录](https://launchdarkly.com/docs/sdk)。

## 参考

- [检测仓库堆栈](detect/SKILL.md)
- [生成集成计划](plan/SKILL.md)
- [应用代码更改](apply/SKILL.md)
- [SDK 配方](../references/sdk/recipes.md)
- [SDK 片段](../references/sdk/snippets/)
- [LaunchDarkly 引导（父级）](../SKILL.md)
