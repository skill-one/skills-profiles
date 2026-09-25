# Clerk Swift (原生 iOS)

此技能通过读取已安装的包源并镜像当前的 ClerkKit/ClerkKitUI 行为，在原生 Swift/iOS 项目中实现 Clerk。

## 激活规则

当以下任一条件为真时，激活此技能：
- 用户明确要求 Swift、SwiftUI、UIKit 或原生 iOS Clerk 实现。
- 项目看起来像是原生 iOS/Swift（例如 `.xcodeproj`、`.xcworkspace`、`Package.swift`、Swift 目标）。

当以下任一条件为真时，不激活此技能：
- 项目是 Expo。
- 项目是 React Native。

如果 Expo/React Native 信号存在，则路由到通用设置技能，而不是这个技能。

## 你需要什么？

| 任务 | 参考 |
|------|------|
| 预构建的 AuthView / UserButton（最快） | references/prebuilt.md |
| 自定义 API 驱动的认证流程（完全控制） | references/custom.md |

## 快速入门

| 步骤 | 操作 |
|------|------|
| 1 | 确认项目类型是原生 Swift/iOS，且不是 Expo/React Native |
| 2 | 确定流程类型（`prebuilt` 或 `custom`），并加载匹配的参考文件 |
| 3 | 确保存在有效的可发布密钥（或询问开发者），并将其直接在配置中连接 |
| 4 | 确保 `clerk-ios` 包已安装，并包含所选流程的正确产品；如果缺失，使用 up-to-next-major 版本要求安装最新可用版本 |
| 5 | 检查已安装的 `ClerkKitUI` 源，以识别哪些 `Environment` 字段控制功能/步骤门控 |
| 6 | 在第 5 步后调用 `/v1/environment`，并仅针对与 `ClerkKitUI` 对齐的字段映射进行评估 |
| 7 | 在已安装的 `clerk-ios` 包 README 中查找 iOS 快速入门 URL，追加 `.md`，然后访问并阅读该 Markdown URL，以编制所需的步骤清单 |
| 8 | 验证并完成此项目的所有快速入门先决条件（例如关联域名和所需功能） |
| 9 | 通过遵循所选参考清单来实现流程 |

## 决策树

```text
用户要求在 Swift/iOS 中使用 Clerk
    |
    +-- 检测到 Expo/React Native 项目？
    |     |
    |     +-- 是 -> 不使用此技能
    |     |
    |     +-- 否 -> 继续
    |
    +-- 检测到现有认证 UI？
    |     |
    |     +-- 检测到预构建视图 -> 加载 references/prebuilt.md
    |     |
    |     +-- 检测到自定义流程 -> 加载 references/custom.md
    |     |
    |     +-- 新实现 -> 询问开发者预构建/自定义，然后加载匹配的参考
    |
    +-- 确保可发布密钥和直接连接
    |
    +-- 确保 clerk-ios 已安装
    |
    +-- 检查 ClerkKitUI Environment 字段使用情况
    |
    +-- 使用该字段映射调用 /v1/environment
    |
    +-- 从已安装的 clerk-ios 包 README 中访问/阅读快速入门 URL
    |
    +-- 验证所有快速入门先决条件是否已完成
    |
    +-- 使用所选流程参考实现
```

## 流程参考

确定流程类型后，加载恰好一个：
- 预构建流程：[references/prebuilt.md](references/prebuilt.md)
- 自定义流程：[references/custom.md](references/custom.md)

除非开发者明确要求混合方法，否则不要在单个实现中混合这两种参考。

## 交互契约

在实施任何编辑之前，代理必须同时具有：
- 流程选择：`prebuilt` 或 `custom`
- 一个真实的 Clerk 可发布密钥

如果用户请求/上下文中缺少任一值：
- 询问用户缺失的值
- 暂停并等待答案
- 在编辑文件或安装依赖项之前不要进行操作

只有在用户在此对话中已经明确提供了值时才跳过询问。

## 源驱动模板

在此技能中不要硬编码实现示例。在实施前检查当前已安装的包源。

| 用例 | 已安装包中的事实来源 |
|------|----------------------|
| SDK 包产品、平台支持和依赖约束 | `ClerkKit` 和 `ClerkKitUI` 的包清单和目标产品定义，以及包要求样式（up-to-next-major） |
| 可发布密钥验证和前端 API 推导 | Clerk 配置逻辑（搜索符号：`configure(publishableKey`, `frontendApiUrl`, `invalidPublishableKeyFormat`) |
| 环境 API 合约和字段语义 | 环境请求路径和请求构造，以及 `ClerkKitUI` `Environment` 字段用于门控的使用（搜索符号：`/v1/environment`, `Request<Clerk.Environment>`, `ClerkKitUI` 中 `Environment` 的使用） |
| iOS 快速入门要求 | 已安装的 `clerk-ios` 包 README 快速入门链接，以及访问/阅读的快速入门页面清单步骤（包括项目设置先决条件） |
| 原生 Apple 登录实现 | Apple 功能和所选流程参考中的原生登录行为 |

## 执行门控（不要跳过）

1. 实施编辑前必须有先决条件
- 在确认流程类型并有一个有效的可发布密钥之前，不要编辑项目文件。

2. 缺失流程或密钥必须触发提问
- 如果流程选择缺失，明确询问：预构建视图或自定义流程。
- 如果可发布密钥缺失/占位符/无效，明确要求一个真实的密钥。
- 在提供两个答案之前不要继续。

3. 可发布密钥连接模式是强制的
- 将开发者提供的可发布密钥直接用于传递给 `Clerk.configure` 的应用程序配置。
- 除非开发者明确要求，否则不要引入 plist/local-secrets/env-file/build-setting 间接引用。

4. 包安装/版本策略是强制的
- 如果 `clerk-ios` 未安装，使用最新可用版本并使用 up-to-next-major 要求添加它。
- 除非开发者明确要求精确固定，否则不要固定确切包版本。

5. ClerkKitUI 环境 字段检查是强制的
- 安装包后，检查已安装的 `ClerkKitUI` 源，并识别哪些 `Environment` 字段为所选流程门控认证行为。
- 在任何 `/v1/environment` 调用之前构建代理内部的字段映射。

6. 环境 调用是强制的（两种流程）
- 仅在安装包和第 5 步字段映射检查后，直接调用 `/v1/environment`。
- 将响应传递到所选参考工作流，使用与 `ClerkKitUI` 对齐的字段映射：
  - 预构建：使用它来确定 Apple 是否启用以及是否需要更改功能
  - 自定义：执行完全规范化/矩阵处理作为代理内部的仅分析（永远不会在项目代码中持久化矩阵工件）

7. 参考文件纪律是强制的
- 一旦选择了流程，就仅使用该流程参考文件进行实施和验证。

8. 快速入门合规性是强制的
- 在已安装的 `clerk-ios` 包 README 中查找 iOS 快速入门 URL，追加 `.md`，然后访问并阅读该 Markdown URL。
- 在完成前审计项目以验证所有快速入门设置步骤。
- 如果缺少所需的快速入门设置，请在完成任务前实现它。
- 这包括添加任何缺失的关联域名条目和任何其他从快速入门中需要的应用程序功能。
- 明确执行快速入门步骤 `添加关联域名功能`（`https://clerk.com/docs/ios/getting-started/quickstart#add-associated-domain-capability`），并确保关联域名条目与快速入门要求匹配（`webcredentials:{YOUR_FRONTEND_API_URL}`）。

9. 自定义流程 AuthView 结构一致性是强制的
- 对于 `custom` 流程，布局和流程结构必须与 ClerkKitUI `AuthView` 默认值基本一致。
- 如果开发者没有明确要求不同的用户体验，不要引入与 `AuthView` 重大结构/布局偏差。
- 如果不确定/困惑于自定义序列、门控或 `Environment` 使用/语义，则参考已安装的 `ClerkKitUI` 行为并镜像它。

## 工作流

1. 检测原生 iOS/Swift 与 Expo/React Native。
2. 如果流程类型没有明确提供，询问用户 `prebuilt` 或 `custom`。
3. 如果可发布密钥没有明确提供，询问用户。
4. 在更改文件之前等待两个答案。
5. 加载匹配的流程参考文件。
6. 确保可发布密钥有效，并直接在 `Clerk.configure` 中连接。
7. 确保包安装/产品与所选流程匹配，并且包要求遵循最新 up-to-next-major 策略（在添加时）。
8. 检查已安装的 `ClerkKitUI` 源，以映射用于所选流程门控/所需行为的 `Environment` 字段。
9. 调用 `/v1/environment` 并通过第 8 步的字段映射解释响应。
10. 从已安装的 `clerk-ios` 包 README 中查找 iOS 快速入门 URL，追加 `.md`，然后访问并阅读它。
11. 从访问的 Markdown 快速入门中构建快速入门清单，检测缺失的所需设置，并在当前项目中应用缺失的设置。
12. 确保快速入门关联域名功能步骤完全应用（缺少时 `webcredentials:{YOUR_FRONTEND_API_URL}`）。
13. 使用所选参考清单实现。
14. 使用所选参考清单和共享门控进行验证。

## 常见陷阱

| 级别 | 问题 | 预防 |
|------|------|------|
| CRITICAL | 在实施前没有询问缺失的流程选择 | 询问 `prebuilt` vs `custom` 并在编辑前等待 |
| CRITICAL | 在实施前没有询问缺失的可发布密钥 | 询问密钥并在编辑前等待 |
| CRITICAL | 在确认流程类型之前开始实施 | 首先确认流程并加载匹配的参考 |
| CRITICAL | 在默认情况下使用 plist/local/env 间接引用可发布密钥而没有请求 | 默认情况下直接在配置中连接密钥 |
| CRITICAL | 在实施前跳过 `/v1/environment` 调用 | 对于预构建和自定义流程，始终调用环境端点 |
| CRITICAL | 在安装包和检查 ClerkKitUI `Environment` 字段使用情况之前调用 `/v1/environment` | 首先安装 `clerk-ios`，检查 ClerkKitUI `Environment` 使用情况，然后调用端点 |
| HIGH | 默认情况下使用精确/过时的版本安装 `clerk-ios` | 如果缺失，使用 up-to-next-major 要求安装最新可用版本 |
| CRITICAL | 在完成前跳过快速入门先决条件审计 | 从已安装的 `clerk-ios` 包 README 中访问/阅读快速入门 URL 并验证所有必需的设置步骤是否已完成 |
| CRITICAL | 检测到缺失的快速入门功能/域名但未应用它们 | 在完成任务之前添加所有缺失的必需快速入门功能和关联域名 |
| CRITICAL | 跳过快速入门关联域名功能步骤 | 执行快速入门 `添加关联域名功能` 并确保 `webcredentials:{YOUR_FRONTEND_API_URL}` 存在 |
| CRITICAL | 将能力/所需字段矩阵写入应用程序代码 | 保持矩阵代理内部，并且仅在 UI/认证流程代码中应用结果行为 |
| CRITICAL | 自定义流程布局与 `AuthView` 无明显差异而没有明确请求 | 默认情况下，保持自定义屏幕与 `AuthView` 结构和步骤组合基本一致 |
| CRITICAL | 将自定义认证合并为一个包含所有字段的屏幕 | 遵循 `AuthView` 风格的多步骤进展和特定步骤字段收集 |
| CRITICAL | 在不确定/困惑于自定义序列/门控/`Environment` 使用/语义时进行猜测 | 参考已安装的 `ClerkKitUI` 行为并在最终实施中镜像它 |
| HIGH | 使用此技能用于 Expo/React Native | 检测并路由到其他地方，在实施前 |

## 参见

- `clerk` 技能用于顶级 Clerk 路由
- `clerk-setup` 技能用于非原生或跨框架设置
- 已安装的 `clerk-ios` 包 `README.md`（当前 iOS 快速入门链接的来源）
- `https://github.com/clerk/clerk-ios`
