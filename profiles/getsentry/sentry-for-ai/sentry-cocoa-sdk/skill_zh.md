> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Cocoa SDK

# Sentry Cocoa SDK

一个有主见的向导，它会扫描您的 Apple 项目并指导您完成 Sentry 的完整设置。

## 在以下情况下调用此技能

- 用户询问在 iOS/macOS/tvOS 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Swift/ObjC 中进行错误监控、跟踪、分析、会话回放或日志记录，或在 Swift 中进行指标监控
- 用户提到 `sentry-cocoa`、`SentrySDK` 或 Apple/iOS Sentry SDK
- 用户希望监控崩溃、应用挂起、看门狗终止或性能

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的状态（sentry-cocoa 9.15.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/apple/](https://docs.sentry.io/platforms/apple/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检查现有的 Sentry 依赖项
grep -rEi "sentry|sentry-cocoa|SentrySPM|SentrySwiftUI" \
  --include="Package.swift" --include="Podfile" --include="Cartfile" \
  --include="Package.resolved" --include="project.pbxproj" . 2>/dev/null | head -20

# 检测 UI 框架（SwiftUI vs UIKit）
grep -rE "@main|struct .*: App" --include="*.swift" . 2>/dev/null | head -5
grep -rE "AppDelegate|UIApplicationMain|@UIApplicationDelegateAdaptor" --include="*.swift" . 2>/dev/null | head -5

# 检测平台和部署目标
grep -rE "platforms:|\\.iOS|\\.macOS|\\.tvOS|\\.watchOS|\\.visionOS|IPHONEOS_DEPLOYMENT_TARGET|MACOSX_DEPLOYMENT_TARGET|TVOS_DEPLOYMENT_TARGET|WATCHOS_DEPLOYMENT_TARGET|XROS_DEPLOYMENT_TARGET" \
  --include="Package.swift" --include="project.pbxproj" . 2>/dev/null | head -20
grep -E "platform :ios|platform :osx|platform :tvos|platform :watchos" Podfile 2>/dev/null

# 检测日志记录
grep -rE "import OSLog|import os\\.log|Logger\\(|CocoaLumberjack|DDLog" --include="*.swift" . 2>/dev/null | head -5

# 检测辅助后端
ls ../backend ../server ../api 2>/dev/null
ls ../go.mod ../requirements.txt ../Gemfile ../package.json 2>/dev/null
```

**需要注意的事项：**
- `sentry-cocoa` 是否已经在 `Package.swift` 或 `Podfile` 中？如果是，请跳到第二阶段（配置功能）。
- SwiftUI (`@main App` 结构) 还是 UIKit (`AppDelegate`)？这决定了初始化模式。
- 哪些 Apple 平台？（这会影响可用功能——请参阅平台支持矩阵。）
- 现有的日志记录库是什么？（启用结构化日志捕获。）
- SwiftUI 跟踪导入/产品？`SentrySwiftUI` 仍然存在，但在 SDK 9.4.1+ 中已弃用；对于发布的二进制产品，请优先使用主 `Sentry` 模块。
- 辅助后端？（触发第四阶段跨链接以进行分布式跟踪。）

---

## 第二阶段：推荐

根据您的发现，提出具体的建议。不要提出开放式问题——请直接提出建议：

**推荐（核心覆盖）：**
- **错误监控** — 总是；崩溃报告、应用挂起、看门狗终止、NSError/Swift 错误
- **跟踪** — 总是为应用；自动跟踪应用启动、网络、UIViewController、文件 I/O、Core Data
- **分析** — 生产 iOS/macOS 应用；通过 `configureProfiling` 进行 UI 分析

**可选（增强可观察性）：**
- **会话回放** — 面向用户的 iOS 应用；在 iOS 26+ / Liquid Glass 构建上验证掩码
- **日志记录** — 当需要结构化日志捕获时
- **指标** — 需要聚合计数器、仪表板或分布的 Swift 应用
- **用户反馈** — 希望从用户获取崩溃/错误反馈表单的应用

**Cocoa 不适用：**
- Crons — 仅后端
- AI 监控 — 仅限 JS/Python

**推荐逻辑：**

| 功能 | 当以下情况推荐... |
|------|------------------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终为应用** — 开箱即用的丰富自动跟踪 |
| 分析 | iOS/macOS 生产应用，性能很重要（不适用于 tvOS/watchOS/visionOS） |
| 会话回放 | 面向用户的 iOS 应用；tvOS 可能可用，但未正式支持 |
| 日志记录 | 现有的 `os.log` / CocoaLumberjack 使用，或需要结构化日志 |
| 指标 | 不应创建问题的聚合产品或健康信号；仅限 Swift，SDK 9.12+ |
| 用户反馈 | 希望在应用内报告错误并附带截图的应用 |

提议：*"我建议 Error Monitoring + Tracing + Profiling。您希望我添加 Session Replay 和 Logging 吗？*"

---

## 第三阶段：指导

### 安装

**选项 1 — Sentry 向导（推荐）：**

> **您需要自己运行此命令** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将其复制粘贴到终端：
>
> ```
> brew install getsentry/tools/sentry-wizard && sentry-wizard -i ios
> ```
>
> 它处理登录、组织/项目选择、认证令牌设置、SDK 安装、AppDelegate 更新以及 dSYM/调试符号上传构建阶段。
>
> **完成后，回来并跳到 [验证](#verification)。**

如果用户跳过向导，请继续使用选项 2（SPM/CocoaPods）和下面的手动设置。

**选项 2 — Swift Package Manager：** 文件 → 添加包 → 输入：
```
https://github.com/getsentry/sentry-cocoa.git
```

或在 `Package.swift` 中：
```swift
.package(url: "https://github.com/getsentry/sentry-cocoa", from: "9.15.0"),
```

**SPM 产品** — 每个目标选择**正好一个**：

| 产品 | 用例 |
|------|------|
| `Sentry` | **推荐** — 静态框架，快速应用启动；在 SDK 9.4.1+ 中包含 SwiftUI API |
| `Sentry-Dynamic` | 动态框架替代方案 |
| `SentrySwiftUI` | 用于 SwiftUI API 的遗留/弃用重新导出；仅在维护旧设置时使用 |
| `Sentry-WithoutUIKitOrAppKit` | watchOS、应用扩展、CLI 工具（Swift < 6.1） |
| `SentrySPM` + `NoUIFramework` 特性 | 无 UIKit/AppKit 的源构建，用于 CLI/无头目标（**SDK 9.7+ / Swift 6.1+ / Xcode 26.4+** 用于 Xcode UI） |

> 警告：Xcode 允许选择多个产品——请选择**一个**。
>
> 如果从源代码使用 `SentrySPM`，当前源代码项目可能导入 `SentrySwift` 而不是 `Sentry`；请验证目标中的模块名称。发布的二进制产品使用 `import Sentry`。

**Swift 6.1+ 特性基于选项的弃用 UIKit/AppKit**（需要 `Package@swift-6.1.swift` 构建文件）：

```swift
// Package.swift (Swift 6.1+)
.package(
    url: "https://github.com/getsentry/sentry-cocoa",
    from: "9.15.0",
    traits: ["NoUIFramework"]
),

// 在您的目标依赖项中：
.product(name: "SentrySPM", package: "sentry-cocoa")
```

这是 Swift 6.1+ 上命令行/无头目标的首选弃用路径。它从源代码编译 SDK，以便特性可以删除 UIKit/AppKit/SwiftUI 链接。对于 Swift < 6.1，请继续使用 `Sentry-WithoutUIKitOrAppKit`。

> **注意：** 包特性从 **Xcode 26.4+** 开始在 Xcode UI 中可见。在较旧的 Xcode 版本中，当在 `Package.swift` 中声明特性时，特性仍然有效，但不会出现在 GUI 中。

**选项 3 — CocoaPods（已弃用；优先使用 SPM）：**
```ruby
platform :ios, '15.0'
use_frameworks!

target 'YourApp' do
  pod 'Sentry', :git => 'https://github.com/getsentry/sentry-cocoa.git', :tag => '9.15.0'
end
```

Sentry 计划在 2026 年 6 月底停止发布 CocoaPods 发布版本；仅适用于现有的 CocoaPods 项目。

> **已知问题（Xcode 14+）：** 沙盒 `rsync.samba` 错误 → 目标设置 → “启用用户脚本沙盒” → `NO`。

**选项 4 — SentryObjC（用于纯 Objective-C/C++ 项目）：**

对于无法启用 Clang 模块的纯 Objective-C 或 Objective-C++ 项目（例如，`-fmodules=NO`），请使用 SentryObjC 包装 SDK。它提供与主 SDK 相同的功能，但使用纯 Objective-C 头文件，这些头文件不需要 Swift 模块导入。

**SPM:**
```swift
.package(url: "https://github.com/getsentry/sentry-cocoa", from: "9.17.1"),

// 在您的目标依赖项中：
.product(name: "SentryObjC", package: "sentry-cocoa")
```

或从 [发布页面](https://github.com/getsentry/sentry-cocoa/releases) 下载 `SentryObjC-Dynamic.xcframework.zip`。

**从常规 Sentry 迁移到 SentryObjC：**
- 将 `#import <Sentry/Sentry.h>` 更改为 `#import <SentryObjC/SentryObjC.h>`
- 将 `Sentry`-前缀的类型重命名为 `SentryObjC`（例如，`SentrySDK` → `SentryObjCSDK`，`SentryOptions` → `SentryObjCOptions`)
- API 表面否则相同

大多数用户应使用标准的 `Sentry` 产品（选项 2）。仅在您有特定要求阻止 Clang 模块时才使用 `SentryObjC`。

---

### 快速入门 — 推荐的初始化

启用最常见功能并具有合理默认值的完整 iOS 应用配置。在应用启动时任何其他代码之前添加。

对于 macOS、watchOS、应用扩展或 `NoUIFramework` 构建，省略对特定平台不可用的选项（`sessionReplay`、截图/视图层次结构、用户反馈 UI、UIKit 跟踪以及在 tvOS/watchOS/visionOS 上的分析）。保留适用于检测目标平台的核心 `dsn`、环境、错误监控、跟踪、日志和指标设置。

**SwiftUI — 应用入口点：**
```swift
import SwiftUI
import Sentry

@main
struct MyApp: App {
    init() {
        SentrySDK.start { options in
            options.dsn = ProcessInfo.processInfo.environment["SENTRY_DSN"]
                ?? "https://examplePublicKey@o0.ingest.sentry.io/0"
            options.environment = ProcessInfo.processInfo.environment["SENTRY_ENVIRONMENT"]
                ?? "production"
            // releaseName 默认为 "<bundle id>@<version>+<build>"；如果您需要自定义发布版本，请设置。

            // 错误监控（默认启用——明确指定以供清晰）
            options.enableCrashHandler = true
            options.enableAppHangTracking = true
            options.enableReportNonFullyBlockingAppHangs = true
            options.enableWatchdogTerminationTracking = true
            options.attachScreenshot = true
            options.attachViewHierarchy = true
            options.sendDefaultPii = true

            // 跟踪
            options.tracesSampleRate = 1.0          // 在高流量生产环境中降低到 0.2

            // 分析（SDK 9.0.0+ API）
            options.configureProfiling = {
                $0.sessionSampleRate = 1.0
                $0.lifecycle = .trace
            }

            // 会话回放。在生产中保持保守的采样率，并在 iOS 26+ 上验证掩码和任何手动 Liquid Glass 管理门。

            options.sessionReplay.sessionSampleRate = 0.1
            options.sessionReplay.onErrorSampleRate = 1.0

            // 日志记录（SDK 9.0.0+ 顶层；在 8.x 中使用 `options.experimental.enableLogs`）
            options.enableLogs = true

            // 指标默认在 SDK 9.12+ 中启用。仅在您选择退出时设置为 false。
            options.enableMetrics = true
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

**UIKit — AppDelegate：**
```swift
import UIKit
import Sentry

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        SentrySDK.start { options in
            options.dsn = ProcessInfo.processInfo.environment["SENTRY_DSN"]
                ?? "https://examplePublicKey@o0.ingest.sentry.io/0"
            options.environment = ProcessInfo.processInfo.environment["SENTRY_ENVIRONMENT"]
                ?? "production"
            // releaseName 默认为 "<bundle id>@<version>+<build>"；如果您需要自定义发布版本，请设置。

            options.enableCrashHandler = true
            options.enableAppHangTracking = true
            options.enableReportNonFullyBlockingAppHangs = true
            options.enableWatchdogTerminationTracking = true
            options.attachScreenshot = true
            options.attachViewHierarchy = true
            options.sendDefaultPii = true

            options.tracesSampleRate = 1.0

            options.configureProfiling = {
                $0.sessionSampleRate = 1.0
                $0.lifecycle = .trace
            }

            options.sessionReplay.sessionSampleRate = 0.1
            options.sessionReplay.onErrorSampleRate = 1.0

            // 日志记录（SDK 9.0.0+ 顶层；在 8.x 中使用 `options.experimental.enableLogs`）
            options.enableLogs = true

            // 指标默认在 SDK 9.12+ 中启用。仅在您选择退出时设置为 false。
            options.enableMetrics = true
        }
        return true
    }
}
```

> 警告：SDK 初始化必须在**主线程**上执行。

---

### 对于每个同意的功能

逐个功能进行操作。加载每个功能的参考文件，按照其步骤进行操作，并在继续下一个之前进行验证：

| 功能 | 参考文件 | 加载时...
|------|----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 应用启动、网络、UIViewController 性能 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 生产性能敏感的应用 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的 iOS 应用；tvOS 仅限特殊情况 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 需要结构化日志捕获 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 聚合计数器、仪表板或分布 |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 希望在应用内报告错误的应用 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<feature>.md`，完全按照步骤操作，并验证其是否正常工作。

---

## 配置参考

### 关键 `SentryOptions` 字段

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | `String?` | `nil` | 如果为空，则禁用 SDK；macOS 可以读取 `SENTRY_DSN`，其他 Apple 平台必须显式设置 |
| `environment` | `String` | `"production"` | 例如，`"production"` |
| `releaseName` | `String?` | 分发包派生 | 默认为 `<bundle id>@<version>+<build>` |
| `debug` | `Bool` | `false` | SDK 详细输出——**生产中禁用** |
| `sendDefaultPii` | `Bool` | `false` | 包括来自活动集成的 IP、用户信息 |
| `enableCrashHandler` | `Bool` | `true` | 崩溃报告的主开关 |
| `enableAppHangTracking` | `Bool` | `true` | 应用挂起跟踪的主开关 |
| `enableReportNonFullyBlockingAppHangs` | `Bool` | `true` | 在支持 UI 平台上报告非完全阻塞挂起 |
| `appHangTimeoutInterval` | `Double` | `2.0` | 秒数，在此之前将其分类为挂起 |
| `enableWatchdogTerminationTracking` | `Bool` | `true` | 跟踪看门狗终止（iOS、tvOS、Mac Catalyst） |
| `attachScreenshot` | `Bool` | `false` | 在错误时捕获截图 |
| `attachViewHierarchy` | `Bool` | `false` | 在错误时捕获视图层次结构 |
| `tracesSampleRate` | `NSNumber?` | `nil` | 事务采样率（`nil` = 禁用跟踪）；Swift 自动装箱 `Double` 字面量（例如 `1.0` → `NSNumber`） |
| `tracesSampler` | `Closure` | `nil` | 动态每笔交易采样（覆盖速率） |
| `enableAutoPerformanceTracing` | `Bool` | `true` | 自动跟踪的主开关 |
| `tracePropagationTargets` | `[Any]` | 所有请求 | 接收分布式跟踪头的字符串或 `NSRegularExpression` 值 |
| `enableCaptureFailedRequests` | `Bool` | `true` | 自动捕获 HTTP 5xx 错误作为事件 |
| `enableNetworkBreadcrumbs` | `Bool` | `true` | 出站 HTTP 请求的面包屑 |
| `add(inAppInclude:)` | 方法 | 包可执行文件 | 治理作为“应用内”代码的模块前缀 |
| `maxBreadcrumbs` | `Int` | `100` | 每个事件的最大面包屑 |
| `sampleRate` | `Float` | `1.0` | 错误事件采样率 |
| `beforeSend` | `Closure` | `nil` | 挂钩以修改/丢弃错误事件 |
| `onLastRunStatusDetermined` | `Closure` | `nil` | SDK 确定之前启动崩溃状态后调用 |
| `strictTraceContinuation` | `Bool` | `false` | 拒绝来自其他组织的传入跟踪；验证 `sentry-org_id` 在行李头中（sentry-cocoa ≥9.10.0） |
| `orgId` | `String?` | `nil` | 用于严格跟踪验证的组织 ID；如果未显式设置，则从 DSN 主机自动解析（例如 `o123.ingest.sentry.io` → `"123"`） |
| `enableLogs` | `Bool` | `false` | 启用结构化日志 |
| `enableMetrics` | `Bool` | `true` | 启用 Swift 指标 API（SDK 9.12+） |

### 环境变量

| 变量 | 映射到 | 目的 |
|------|--------|------|
| `SENTRY_DSN` | `dsn` | 仅 macOS 回退；iOS/tvOS/watchOS/visionOS 必须显式设置 |
| `SENTRY_RELEASE` | `releaseName` | 不要假设 Cocoa 自动回退；如果需要，请显式设置 |
| `SENTRY_ENVIRONMENT` | `environment` | 不要假设 Cocoa 自动回退；如果需要，请显式设置 |

### 平台功能支持矩阵

| 功能 | iOS | tvOS | macOS | watchOS | visionOS |
|------|-----|------|-------|---------|----------|
| 崩溃报告 | 是 | 是 | 是 | 否 | 是 |
| 应用挂起 | 是 | 是 | 是 | 否 | 是 |
| 看门狗终止 | 是 | 是 | 否 | 否 | 是 |
| 应用启动跟踪 | 是 | 是 | 否 | 否 | 是 |
| UIViewController 跟踪 | 是 | 是 | 否 | 否 | 是 |
| SwiftUI 跟踪 | 是 | 是 | 是 | 否 | 是 |
| 网络跟踪 | 是 | 是 | 是 | 否 | 是 |
| 分析 | 是 | 否 | 是 | 否 | 否 |
| 会话回放 | 是 | 非官方 | 否 | 否 | 否 |
| MetricKit | 是 (15+) | 否 | 是 (12+) | 否 | 是 |

### 生产设置

为生产降低采样率以控制卷和高成本：

```swift
options.tracesSampleRate = 0.2          // 20% 的交易

options.configureProfiling = {
    $0.sessionSampleRate = 0.1          // 10% 的会话
    $0.lifecycle = .trace
}

options.sessionReplay.sessionSampleRate = 0.1   // 10% 连续
options.sessionReplay.onErrorSampleRate = 1.0   // 100% 在错误时（保持较高）

options.enableLogs = true
options.enableMetrics = true             // SDK 9.12+ 默认为 true
options.debug = false                   // 生产中从不
```

---

## 验证

测试 Sentry 是否正在接收事件：

```swift
// 触发测试错误事件：
SentrySDK.capture(message: "Sentry Cocoa SDK test")

// 或测试崩溃报告（不要调试器——崩溃被调试器拦截）：
// SentrySDK.crash()  // 取消注释，不调试器运行，重新启动以查看崩溃报告
```

在几秒钟内检查 Sentry 仪表板。如果什么也没有出现：
1. 设置 `options.debug = true` — 将 SDK 内部打印到 Xcode 控制台
2. 验证 DSN 是否正确且项目存在
3. 确保初始化在**主线程**上

---

## 第四阶段：跨链接

在完成 Apple 设置后，检查是否缺少 Sentry 覆盖的辅助后端：

```bash
# 检测辅助后端
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -5
cat ../requirements.txt ../Pipfile 2>/dev/null | head -5
cat ../Gemfile 2>/dev/null | head -5
cat ../package.json 2>/dev/null | grep -E '"name"|"dependencies"' | head -5
```

如果发现后端，请配置 `tracePropagationTargets` 以启用端到端的分布式跟踪，并建议匹配的技能：

| 后端检测到 | 建议技能 | 跟踪头支持 |
|----------|----------|-------------|
| Go (`go.mod`) | `sentry-go-sdk` | 自动 |
| Python (`requirements.txt`) | `sentry-python-sdk` | 自动 |
| Ruby (`Gemfile`) | `sentry-ruby-sdk` | 自动 |
| Node.js 后端 (`package.json`) | `sentry-node-sdk` (或 `sentry-express-sdk`) | 自动 |

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 事件未出现 | 设置 `debug: true`，验证 DSN 格式，确保初始化在主线程上 |
| 崩溃未捕获 | **不附加调试器运行** — 调试器拦截信号 |
| 应用挂起未报告 | 调试器附加时自动禁用；检查 `appHangTimeoutInterval` |
| 会话回放未录制 | 验证 `sessionSampleRate > 0` 或 `onErrorSampleRate > 0`；在 iOS 26+ 上验证掩码和任何手动 Liquid Glass 管理门 |
| 跟踪数据缺失 | 确认 `tracesSampleRate > 0`；检查 `enableAutoPerformanceTracing = true` |
| 分析数据缺失 | 验证 `configureProfiling` 中的 `sessionSampleRate > 0`；对于 `.trace` 生命周期，必须启用跟踪 |
| `rsync.samba` 构建错误（CocoaPods） | 目标设置 → “启用用户脚本沙盒” → `NO` |
| 选择多个 SPM 产品 | 选择 **一个** 的 `Sentry`、`Sentry-Dynamic`、`SentrySwiftUI`、`Sentry-WithoutUIKitOrAppKit` 或 `SentrySPM`（在 Swift 6.1+ 上使用 `NoUIFramework` 特性） |
| `inAppExclude` 编译错误 | 在 SDK 9.0.0 中已删除——使用 `options.add(inAppInclude:)` |
| `enableAppHangTrackingV2` 编译错误 | 在 SDK 9.0.0 中已删除——使用 `enableAppHangTracking`；V2 行为是支持时的默认行为 |
| 看门狗终止未跟踪 | 需要 `enableCrashHandler = true`（默认情况下为 true） |
| 网络面包屑缺失 | 需要 `enableSwizzling = true`（默认情况下为 true） |
| `profilesSampleRate` 编译错误 | 在 SDK 9.0.0 中已删除——使用 `configureProfiling` 闭包代替 |
