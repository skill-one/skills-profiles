# LaunchDarkly 标志创建与配置

您正在使用一个技能，它将指导您将一个新的功能标志引入到代码库中。您的工作是探索此代码库中标志的现有使用方式，以符合 LaunchDarkly 中的标志创建方式，添加与现有模式匹配的评估代码，并验证所有内容是否正确连接。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-flag`：在项目中创建新的功能标志
- `get-flag`：验证标志是否正确创建

**可选的 MCP 工具（增强工作流程）：**
- `list-flags`：浏览现有标志以了解命名约定和标签
- `update-flag-settings`：更新标志元数据（名称、描述、标签、临时/永久状态）

## 工作流程

### 第 1 步：探索代码库

在创建任何内容之前，了解此代码库如何使用功能标志。

1. **找到 SDK。** 搜索 LaunchDarkly SDK 导入或初始化：
   - 在导入中查找 `launchdarkly`、`ldclient`、`ld-client`、`LDClient`
   - 检查 `package.json`、`requirements.txt`、`go.mod`、`Gemfile` 或等效的 SDK 依赖项
   - 确定正在使用的 SDK（服务器端 Node、React、Python、Go、Java 等）

2. **找到现有的标志评估。** 搜索变体调用以了解此代码库使用的模式：
   - 直接 SDK 调用：`variation()`、`boolVariation()`、`useFlags()` 等
   - 包装模式：此代码库是否将标志封装在服务或工具后面？
   - 常量定义：标志键是否在某个地方定义为常量？
   - 参考 [SDK 评估模式](references/sdk-evaluation-patterns.md) 了解不同语言的模式

3. **了解约定。** 查看现有标志以学习：
   - **命名约定**：键是 `kebab-case`、`snake_case`、`camelCase` 吗？
   - **组织方式**：标志键是与功能一起放置，还是集中在一个常量文件中？
   - **默认值**：现有评估使用什么默认值？
   - **上下文/用户构建**：此代码库如何构建传递给 SDK 的用户/上下文对象？这决定了未来任何目标可以使用哪些上下文类型和属性。这因表面（服务器 vs 客户端 vs 匿名）而异。在规划规则、单个目标或发布之前，请参考 [上下文可用性](../launchdarkly-flag-targeting/references/context-availability.md)。

4. **检查 LaunchDarkly 项目约定。** 可选地使用 `list-flags` 查看现有标志：
   - 常用的标签是什么？
   - 标志是否标记为临时或永久？
   - 项目中存在哪些命名模式？

### 第 2 步：确定正确的标志类型

根据用户的需求，选择适当的标志配置。参考 [标志类型和模式](references/flag-types.md) 了解完整指南。

**快速决策：**

| 用户意图 | 标志类型 | 变体 |
|----------|----------|------|
| "开启或关闭功能" | `boolean` | `true` / `false` |
| "逐渐发布功能" | `boolean` | `true` / `false` |
| "在选项之间进行 A/B 测试" | `multivariate`（字符串） | 用户定义的值 |
| "配置数值阈值" | `multivariate`（数字） | 用户定义的值 |
| "提供不同的配置对象" | `multivariate`（JSON） | 用户定义的值 |

**应用默认值：**
- 除非用户明确说明这是一个永久/长寿命标志，否则将 `temporary: true`。大多数标志是发布标志，最终应该被清理。
- 如果未提供，则从名称生成 `key`（例如，"新结账流程" -> `new-checkout-flow`），但如果存在命名约定，请匹配代码库的命名约定。
- 根据用户提到的功能区域、团队或上下文建议相关的标签。

### 第 3 步：在 LaunchDarkly 中创建标志

使用在第 2 步中确定的配置使用 `create-flag`。

创建后：
- 标志在所有环境中都创建为 **目标关闭**。
- 标志向所有人提供 `offVariation`，直到目标开启。
- 提醒用户他们需要使用 [标志目标技能](../launchdarkly-flag-targeting/SKILL.md) 来开启标志，并可选地设置发布规则。

### 第 4 步：向代码中添加标志评估

现在添加评估标志的代码，**匹配第 1 步中找到的模式**。

1. **使用代码库已经使用的相同 SDK 模式**。如果有包装器，请使用包装器。如果有常量，请将新键添加到常量文件中。
2. **使用适当的默认值**。代码中的默认（备用）值应该是“安全”行为：通常是标志之前的现有行为。这确保如果 SDK 无法连接到 LaunchDarkly，功能保持关闭。
3. **添加条件逻辑**。将新行为包装在标志检查中。
4. **处理两个分支**。确保每个变体的代码路径清晰完整。

参考 [SDK 评估模式](references/sdk-evaluation-patterns.md) 了解不同语言和框架的实现示例。

### 第 5 步：验证

确认标志已正确设置：

1. **代码编译/通过代码检查**。运行项目的构建或代码检查步骤。
2. **LaunchDarkly 中存在标志**。使用 `get-flag` 确认它是否以正确的配置创建。
3. **两个代码路径都有效**。标志关闭路径保留现有行为；标志开启路径启用新功能。
4. **默认值是安全的**。如果 LaunchDarkly 无法连接，代码回退到默认值：确保那是现有/安全的行为。

## 更新标志设置

如果用户想更改标志元数据（不是目标），请使用 `update-flag-settings`。支持的更改：

| 更改 | 说明 |
|------|------|
| 重命名 | `{kind: "updateName", value: "New Name"}` |
| 更新描述 | `{kind: "updateDescription", value: "New description"}` |
| 添加标签 | `{kind: "addTags", values: ["tag1", "tag2"]}` |
| 删除标签 | `{kind: "removeTags", values: ["old-tag"]}` |
| 标记为临时 | `{kind: "markTemporary"}` |
| 标记为永久 | `{kind: "markPermanent"}` |

多个指令可以批量在一个调用中执行。这些更改是项目范围的，不是环境特定的。

**重要提示：** 元数据更新（上述内容）与目标更改（切换、发布、规则）是分开的。如果用户想更改谁看到什么，请直接引导他们使用 [标志目标技能](../launchdarkly-flag-targeting/SKILL.md)。

## 重要上下文

- **标志键是不可变的**。一旦创建，标志的键不能更改。请谨慎选择。
- **标志默认关闭**。创建永远不会启用标志。这是一个安全功能。
- **代码中的默认值是您的安全网**。当 SDK 无法连接到 LaunchDarkly 时，它会提供默认值。始终使用“安全”/现有行为作为默认值。
- **遵循现有代码库约定**。最常见的错误是引入与团队现有做法不匹配的标志模式。第 1 步的存在就是为了防止这种情况。

## 参考

- [标志类型和模式](references/flag-types.md)：布尔值 vs 多变量，命名约定，配置最佳实践
- [SDK 评估模式](references/sdk-evaluation-patterns.md)：如何在每个 SDK 中评估标志，包括常见的包装器模式
- [上下文可用性](../launchdarkly-flag-targeting/references/context-availability.md)：目标可以使用哪些上下文类型/属性，与标志读取的表面（服务器 vs 客户端 vs 匿名）匹配（在标志将用于目标而不是简单的开/关切换时相关）
