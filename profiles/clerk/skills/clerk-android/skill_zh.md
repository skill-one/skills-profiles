# Clerk Android (原生)

此技能通过遵循当前的 `clerk-android` SDK 和文档模式，在原生 Android 项目中实现 Clerk。

## 激活规则

当满足以下任一条件时，激活此技能：
- 用户明确要求在 Android 上使用 Kotlin、Jetpack Compose 或原生移动 Clerk 实现。
- 项目看起来是原生 Android 项目（例如 `build.gradle(.kts)` 包含 Android 插件、`AndroidManifest.xml`、`app/src/main/java`、Compose UI 文件）。

当满足以下任一条件时，不激活此技能：
- 项目是 Expo。
- 项目是 React Native。

如果 Expo/React Native 信号存在，则路由到通用设置技能。

## 您需要什么？

| 任务 | 参考 |
|------|------|
| 预构建的 AuthView / UserButton（最快） | references/prebuilt.md |
| 自定义 API 驱动的认证流程（完全控制） | references/custom.md |

## 快速入门

| 步骤 | 操作 |
|------|------|
| 1 | 确认项目类型是原生 Android 且不是 Expo/React Native |
| 2 | 确定流程类型（`prebuilt` 或 `custom`）并加载匹配的参考文件 |
| 3 | 确保存在真实的可发布 Clerk 密钥（或询问开发者） |
| 4 | 确保为所选流程安装了正确的 Clerk 资产 |
| 5 | 阅读官方 Android 快速入门并验证所需设置（原生 API、最小 SDK/Java、清单、初始化） |
| 6 | 检查与所选流程相关的 `clerk-android` 源/示例模式 |
| 7 | 通过仅遵循所选参考清单来实现流程 |

## 决策树

```text
用户要求在 Android/Kotlin 中使用 Clerk
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
    +-- 确保可发布密钥和 SDK 初始化路径
    |
    +-- 确保安装了正确的 Android 资产
    |
    +-- 验证项目中的快速入门先决条件
    |
    +-- 使用所选流程参考实现
```

## 流程参考

确定流程类型后，加载一个：
- 预构建流程：[references/prebuilt.md](references/prebuilt.md)
- 自定义流程：[references/custom.md](references/custom.md)

除非开发者明确要求混合方法，否则不要在单个实现中混合这两个参考。

## 交互契约

在实施任何编辑之前，代理必须同时具有：
- 流程选择：`prebuilt` 或 `custom`
- 一个真实的可发布 Clerk 密钥

如果用户请求/上下文中缺少任一值：
- 询问用户缺失的值
- 暂停并等待答案
- 在编辑文件或安装依赖项之前不要继续

仅当用户在此对话中已经明确提供了值时才跳过询问。

## 源驱动模板

在此技能中不要硬编码实现示例。在实施之前，检查当前的 `clerk-android` 源/文档以获取安装的 SDK 版本。

| 使用案例 | 真实来源 |
|----------|----------|
| SDK 资产和依赖项拆分（`clerk-android-api` vs `clerk-android-ui`） | `clerk-android` README 和 Android 安装文档 |
| SDK 初始化和可发布密钥连接 | Android 快速入门和 `source/api/.../Clerk.kt` |
| 预构建认证和配置文件行为 | `source/ui/.../AuthView.kt`、`source/ui/.../UserButton.kt` 和预构建示例 |
| 自定义认证顺序和因素处理 | `source/ui/auth/*`、`source/api/auth/*` 和自定义流程示例 |
| 从实例设置中启用功能/特性门控 | `Clerk` 公共字段（例如 `enabledFirstFactorAttributes`、`socialProviders`、`isGoogleOneTapEnabled`、`mfaIsEnabled`）和环境模型源 |
| 所需 Android 设置清单 | 官方 Android 快速入门（`/docs/android/getting-started/quickstart`） |

## 执行门（不可跳过）

1. 在先决条件之前不进行任何实施编辑
- 在确认流程类型并存在有效可发布密钥之前，不要编辑项目文件。

2. 缺失流程或密钥必须触发提问
- 如果流程选择缺失，明确询问：预构建视图或自定义流程。
- 如果可发布密钥缺失/占位符/无效，明确询问一个真实密钥。
- 在提供两个答案之前不要继续。

3. 可发布密钥连接模式是强制性的
- 默认情况下，在 `Clerk.initialize(...)` 中直接连接开发者提供的密钥。
- 除非明确要求，否则不要引入密钥管理间接层。

4. 资产安装策略是强制性的
- 预构建流程：使用 `clerk-android-ui`（包含 API）。
- 自定义流程：使用 `clerk-android-api`，除非明确请求预构建组件。
- 如果缺少 Clerk 资产，添加最新稳定版本。

5. Android 快速入门合规性是强制性的
- 验证为 Clerk 应用启用了原生 API。
- 验证项目实现了快速入门中的 Android 要求（最小 SDK 和 Java 目标、清单互联网权限、应用级 Clerk 初始化）。
- 验证应用在假设认证就绪状态之前等待 SDK 初始化（`Clerk.isInitialized`）。

6. 能力驱动行为是强制性的
- 使用 Clerk 运行时能力/设置状态（例如启用因素/社交提供者/MFA 标志）来门控流程行为。
- 不要硬编码可能与仪表板配置冲突的因素假设。

7. 参考文件纪律是强制性的
- 选择流程后，仅遵循该流程参考文件进行实施和验证。

8. 自定义流程结构一致性是强制性的
- 对于 `custom` 流程，保留多步骤认证进展和因素特定处理（默认不使用单字段所有表单）。
- 将 UI、状态协调和 Clerk API 集成保持在不同的模块中。

9. 预构建优先级是强制性的（当选择时）
- 对于 `prebuilt` 流程，除非明确请求，否则不要使用自定义 API 调用重建认证表单。
- 使用 `AuthView`/`UserButton` 作为默认构建块。

## 工作流

1. 检测原生 Android vs Expo/React Native。
2. 如果流程类型没有明确提供，询问用户 `prebuilt` 或 `custom`。
3. 如果可发布密钥没有明确提供，询问用户密钥。
4. 在更改文件之前等待两个答案。
5. 加载匹配的流程参考文件。
6. 确保 `Clerk.initialize(...)` 路径和可发布密钥连接有效。
7. 确保依赖项/资产匹配所选流程。
8. 审查 Android 快速入门要求并在项目中应用缺失的设置。
9. 使用所选参考清单实现。
10. 使用所选参考清单和共享门进行验证。

## 常见陷阱

| 级别 | 问题 | 预防 |
|------|------|------|
| CRITICAL | 在实施之前没有询问缺失的流程选择 | 询问 `prebuilt` vs `custom` 并在编辑前等待 |
| CRITICAL | 在实施之前没有询问缺失的可发布密钥 | 询问密钥并在编辑前等待 |
| CRITICAL | 在确认流程类型之前开始实施 | 首先确认流程并加载匹配的参考 |
| CRITICAL | 跳过 Android 快速入门先决条件 | 验证并应用官方 Android 快速入门中的所需设置 |
| CRITICAL | 缺失应用级 `Clerk.initialize(...)` 调用 | 从 `Application` 启动路径初始化 Clerk |
| HIGH | 为所选流程选择了错误的资产 | 预构建：`clerk-android-ui`；自定义：`clerk-android-api` |
| HIGH | 在 SDK 初始化完成之前渲染认证 UI | 使用 `Clerk.isInitialized` 状态门控 UI |
| HIGH | 硬编码认证因素/社交提供者 | 从 Clerk 运行时能力字段驱动行为 |
| HIGH | 使用此技能用于 Expo/React Native | 检测并实施前路由 |

## 参考文档

- `clerk` 技能用于顶级 Clerk 路由
- `clerk-setup` 技能用于跨框架快速入门设置
- `https://github.com/clerk/clerk-android`
- `https://clerk.com/docs/android/getting-started/quickstart`
