---
name: sentry-cocoa-sdk
description: 苹果平台（iOS、macOS、tvOS、watchOS、visionOS）的完整Sentry SDK设置。当被要求“将Sentry添加到iOS”、“将Sentry添加到Swift”、“安装sentry-cocoa”，或为苹果应用程序配置错误监控、跟踪、分析、会话回放、日志记录或指标时使用。支持SwiftUI和UIKit。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Cocoa SDK

# Sentry Cocoa SDK

一个有主见的向导，它会扫描您的 Apple 项目并指导您完成完整的 Sentry 设置。

## 何时调用此技能

- 用户询问在 Apple 应用中“添加 Sentry 到 iOS/macOS/tvOS”或“设置 Sentry”
- 用户希望在 Swift/ObjC 中需要错误监控、跟踪、分析、会话回放或日志记录，或在 Swift 中需要指标
- 用户提到 `sentry-cocoa`、`SentrySDK` 或 Apple/iOS Sentry SDK
- 用户希望监控崩溃、应用程序挂起、看门狗终止或性能

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的状态（sentry-cocoa 9.15.0）。
> 在实施之前，请始终与 [docs.sentry.io/platforms/apple/](https://docs.sentry.io/platforms/apple/) 进行核对。

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
- SwiftUI (`@main App` 结构）还是 UIKit (`AppDelegate`)？这决定了初始化模式。
- 哪些 Apple 平台？（这会影响哪些功能可用——请参阅平台支持矩阵。）
- 现有的日志记录库是什么？（启用结构化日志捕获。）
- SwiftUI 跟踪导入/产品？`SentrySwiftUI` 仍然存在，但在 SDK 9.4.1+ 中已弃用；对于发布的二进制产品，请优先使用主 `Sentry` 模块。
- 辅助后端？（触发第四阶段分布式跟踪的跨链接。）

---

## 第二阶段：建议

根据您的发现，提出具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- **错误监控** — 总是；崩溃报告、应用程序挂起、看门狗终止、NSError/Swift 错误
- **跟踪** — 总是为应用程序；自动检测应用程序启动、网络、UIViewController、文件 I/O、Core Data
- **分析** — 生产 iOS/macOS 应用程序；通过 `configureProfiling` 进行 UI 分析

**可选（增强可观察性）：**
- **会话回放** — 面向用户的 iOS 应用程序；在 iOS 26+ / Liquid Glass 构建中验证掩码
- **日志记录** — 当需要结构化日志捕获时
- **指标** — 需要 aggregate 计数器、仪表板或分布的 Swift 应用程序
- **用户反馈** — 希望从用户那里获取崩溃/错误反馈表单的应用程序

**Cocoa 不适用：**
- Crons — 仅后端
- AI 监控 — 仅限 JS/Python

**建议逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 跟踪 | **始终为应用程序** — 开箱即用的丰富自动检测 |
| 分析 | iOS/macOS 生产应用程序，其中性能很重要（不适用于 tvOS/watchOS/visionOS） |
| 会话回放 | 面向用户的 iOS 应用程序；tvOS 可能可用，但未正式支持 |
| 日志记录 | 现有的 `os.log` / CocoaLumberjack 使用，或需要结构化日志 |
| 指标 | 不应创建问题的聚合产品或健康信号；仅限 Swift，SDK 9.12+ |
| 用户反馈 | 希望在应用程序内报告错误的程序 |

建议："我建议 Error Monitoring + Tracing + Profiling。您希望我还要添加 Session Replay 和 Logging 吗？"

---

## 第三阶段：指导

### 安装

**选项 1 — Sentry 向导（推荐）：**

> **您需要自己运行此命令** — 向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将其复制粘贴到您的终端：
>
> ```
> brew install getsentry/tools/sentry-wizard && sentry-wizard -i ios
> ```
>
> 它处理登录、组织/项目选择、认证令牌设置、SDK 安装、AppDelegate 更新和 dSYM/调试符号上传构建阶段。
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
| `Sentry` | **推荐** — 静态框架，快速启动应用程序；在 SDK 9.4.1+ 中包含 SwiftUI API |
| `Sentry-Dynamic` | 动态框架替代方案 |
| `SentrySwiftUI` | 用于 SwiftUI API 的遗留/弃用重新导出；仅在维护旧设置时使用 |
| `Sentry-WithoutUIKitOrAppKit` | watchOS、应用程序扩展、CLI 工具（Swift < 6.1） |
| `SentrySPM` + `NoUIFramework` 特性 | 用于 CLI/无头目标的源构建，不包含 UIKit/AppKit（**SDK 9.7+ / Swift 6.1+ / Xcode 26.4+** 用于 Xcode UI） |

> 警告：Xcode 允许选择多个产品——选择一个。
>
> 如果从源代码使用 `SentrySPM`，当前源构建项目可能会导入 `SentrySwift` 而不是 `Sentry`；在目标中验证模块名称。发布的二进制产品使用 `import Sentry`。

**Swift 6.1+ 特性基于的 UIKit/AppKit 选择退出**（需要 `Package@swift-6.1.swift` 清单）：

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

这是 Swift 6.1+ 上命令行/无头目标的首选选择退出路径。它从源代码编译 SDK，以便特性可以删除 UIKit/AppKit/SwiftUI 链接。对于 Swift < 6.1，请继续使用 `Sentry-WithoutUIKitOrAppKit`。

> **注意：** 包含特性从 **Xcode 26.4+** 开始在 Xcode UI 中可见。在较旧的 Xcode 版本中，即使声明在 `Package.swift` 中，特性仍然有效，但也不会出现在 GUI 中。

**选项 3 — CocoaPods（已弃用；优先使用 SPM）：**
```ruby
platform :ios, '15.0'
use_frameworks!

target 'YourApp' do
  pod 'Sentry', :git => 'https://github.com/getsentry/sentry-cocoa.git', :tag => '9.15.0'
end
```

Sentry 计划在 2026 年 6 月底停止发布 CocoaPods 发布版本；仅用于现有的 CocoaPods 项目。

> **已知问题（Xcode 14+）：** 沙盒 `rsync.samba` 错误 → 目标设置 → "启用用户脚本沙盒" → `NO`。

**选项 4 — SentryObjC（用于纯 Objective-C/C++ 项目）：**

对于无法启用 Clang 模块的纯 Objective-C 或 Objective-C++ 项目（例如 `-fmodules=NO`），请使用 SentryObjC 包装 SDK。它提供与主 SDK 相同的功能，但使用纯 Objective-C 头文件，这些头文件不需要 Swift 模块导入。

**SPM：**
```swift
.package(url: "https://github.com/getsentry/sentry-cocoa", from: "9.17.1"),

// 在您的目标依赖项中：
.product(name: "SentryObjC", package: "sentry-cocoa")
```

或从 [发布页面](https://github.com/getsentry/sentry-cocoa/releases) 下载 `SentryObjC-Dynamic.xcframework.zip`。

**从常规 Sentry 迁移到 SentryObjC：**
- 将 `#import <Sentry/Sentry.h>` 更改为 `#import <SentryObjC/SentryObjC.h>`
- 将 `Sentry`-前缀的类型重命名为 `SentryObjC`（例如，`SentrySDK` → `SentryObjCSDK`，`SentryOptions` → `SentryObjCOptions`）
- API 表面其余部分相同

大多数用户应使用标准的 `Sentry` 产品（选项 2）。仅在您有特定要求阻止 Clang 模块时才使用 `SentryObjC`。

---

### 快速入门 — 推荐的初始化

启用最常见功能并具有合理默认值的完整 iOS 应用程序配置。在应用程序启动之前添加任何其他代码之前。

对于 macOS、watchOS、应用程序扩展或 `NoUIFramework` 构建，请省略对那些平台不可用的选项（`sessionReplay`、屏幕截图/视图层次结构、用户反馈 UI、UIKit 跟踪以及 tvOS/watchOS/visionOS 上的分析）。保留适用于检测目标的核心 `dsn`、环境、错误监控、跟踪、日志记录和指标设置。

**SwiftUI — 应用程序入口点：**
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

            // 错误监控（默认启用——明确指定）
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

            // 会话回放。保持生产采样保守，并在 iOS 26+ 上验证掩码。
            options.sessionReplay.sessionSampleRate = 0.1
            options.sessionReplay.onErrorSampleRate = 1.0

            // 日志记录（SDK 9.0.0+ 顶层；在 8.x 中使用 options.experimental.enableLogs）
            options.enableLogs = true

            // 指标默认在 SDK 9.12+ 中启用。仅当选择退出时设置为 false。
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

            // 日志记录（SDK 9.0.0+ 顶层；在 8.x 中使用 options.experimental.enableLogs）
            options.enableLogs = true

            // 指标默认在 SDK 9.12+ 中启用。仅当选择退出时设置为 false。
            options.enableMetrics = true
        }
        return true
    }
}
```

> 警告：SDK 初始化必须在**主线程**上执行。

---

### 对于每个同意的功能

一次走一遍功能。加载每个功能的参考文件，按照其步骤进行操作，并在进入下一个功能之前进行验证：

| 功能 | 参考文件 | 加载时... |
|------|----------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 应用程序启动、网络、UIViewController 性能 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 生产性能敏感的应用程序 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的 iOS 应用程序；tvOS 仅带限制 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 需要结构化日志捕获 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 聚合计数器、仪表板、分布 |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 希望在应用程序内报告错误 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，完全按照步骤操作，并验证其是否正常工作。

---

## 配置参考

### `SentryOptions` 关键字字段

| 选项 | 类型 | 默认值 | 用途 |
|--------|------|---------|---------|
| `dsn` | `String?` | `nil` | 如果为空则 SDK 被禁用；macOS 可读取 `SENTRY_DSN`，其他 Apple 平台必须显式设置 |
| `environment` | `String` | `"production"` | 例如 `"production"` |
| `releaseName` | `String?` | 由 bundle 派生 | 默认为 `<bundle id>@<version>+<build>` |
| `debug` | `Bool` | `false` | 冗长的 SDK 输出——**在生产环境中禁用** |
| `sendDefaultPii` | `Bool` | `false` | 包含来自活动集成的 IP、用户信息 |
| `enableCrashHandler` | `Bool` | `true` | 崩溃报告的主开关 |
| `enableAppHangTracking` | `Bool` | `true` | 应用挂起跟踪的主开关 |
| `enableReportNonFullyBlockingAppHangs` | `Bool` | `true` | 在支持的 UI 平台上报告非完全阻塞的挂起 |
| `appHangTimeoutInterval` | `Double` | `2.0` | 在将问题归类为挂起前的秒数 |
| `enableWatchdogTerminationTracking` | `Bool` | `true` | 跟踪看门狗终止（iOS、tvOS、Mac Catalyst） |
| `attachScreenshot` | `Bool` | `false` | 在出错时捕获屏幕截图 |
| `attachViewHierarchy` | `Bool` | `false` | 在出错时捕获视图层次结构 |
| `tracesSampleRate` | `NSNumber?` | `nil` | 事务采样率（`nil` = 跟踪被禁用）；Swift 会自动装箱 `Double` 字面量（例如 `1.0` → `NSNumber`） |
| `tracesSampler` | `Closure` | `nil` | 动态的每事务采样（覆盖比率） |
| `enableAutoPerformanceTracing` | `Bool` | `true` | 自动插桩的主开关 |
| `tracePropagationTargets` | `[Any]` | 所有请求 | 接收分布式跟踪头的字符串或 `NSRegularExpression` 值 |
| `enableCaptureFailedRequests` | `Bool` | `true` | 自动捕获 HTTP 5xx 错误作为事件 |
| `enableNetworkBreadcrumbs` | `Bool` | `true` | 发出的 HTTP 请求的碎屑 |
| `add(inAppInclude:)` | 方法 | bundle 可执行文件 | 添加被当作“应用内”代码的模块前缀 |
| `maxBreadcrumbs` | `Int` | `100` | 每个事件的最大碎屑数 |
| `sampleRate` | `Float` | `1.0` | 错误事件的采样率 |
| `beforeSend` | `Closure` | `nil` | 用于修改/丢弃错误事件的钩子 |
| `onLastRunStatusDetermined` | `Closure` | `nil` | 在 SDK 确定上一次启动的崩溃状态后调用 |
| `strictTraceContinuation` | `Bool` | `false` | 拒绝来自其他组织的传入跟踪；验证 baggage 头中的 `sentry-org_id`（sentry-cocoa ≥9.10.0） |
| `orgId` | `String?` | `nil` | 用于严格跟踪验证的组织 ID；如果未显式设置，则从 DSN 主机自动解析（例如 `o123.ingest.sentry.io` → `"123"`） |
| `enableLogs` | `Bool` | `false` | 启用结构化日志 |
| `enableMetrics` | `Bool` | `true` | 启用 Swift 指标 API（SDK 9.12+） |

### 环境变量

| 变量 | 映射到 | 用途 |
|----------|---------|---------|
| `SENTRY_DSN` | `dsn` | 仅 macOS 的回退方案；在 iOS/tvOS/watchOS/visionOS 上需显式设置 |
| `SENTRY_RELEASE` | `releaseName` | 不要假设 Cocoa 的自动回退方案；如需使用请显式设置 |
| `SENTRY_ENVIRONMENT` | `environment` | 不要假设 Cocoa 的自动回退方案；如需使用请显式设置 |

### 平台功能支持矩阵

| 功能 | iOS | tvOS | macOS | watchOS | visionOS |
|---------|-----|------|-------|---------|----------|
| 崩溃报告 | 是 | 是 | 是 | 否 | 是 |
| 应用挂起 | 是 | 是 | 是 | 否 | 是 |
| 看门狗终止 | 是 | 是 | 否 | 否 | 是 |
| 应用启动跟踪 | 是 | 是 | 否 | 否 | 是 |
| UIViewController 跟踪 | 是 | 是 | 否 | 否 | 是 |
| SwiftUI 跟踪 | 是 | 是 | 是 | 否 | 是 |
| 网络跟踪 | 是 | 是 | 是 | 否 | 是 |
| 性能分析 | 是 | 否 | 是 | 否 | 否 |
| 会话回放 | 是 | 非官方 | 否 | 否 | 否 |
| MetricKit | 是（15+） | 否 | 是（12+） | 否 | 否 |
| 指标 API | 是 | 是 | 是 | 待验证 | 是 |

### 生产环境设置

在生产环境中降低采样率以控制数据量和成本：

```swift
options.tracesSampleRate = 0.2          // 20% 的事务

options.configureProfiling = {
    $0.sessionSampleRate = 0.1          // 10% 的会话
    $0.lifecycle = .trace
}

options.sessionReplay.sessionSampleRate = 0.1   // 10% 连续
options.sessionReplay.onErrorSampleRate = 1.0   // 出错时 100%（保持高位）

options.enableLogs = true
options.enableMetrics = true             // SDK 9.12+ 默认为 true
options.debug = false                   // 绝不在生产环境中使用
```

---

## 验证

测试 Sentry 是否正在接收事件：

```swift
// 触发一个测试错误事件：
SentrySDK.capture(message: "Sentry Cocoa SDK test")

// 或者测试崩溃报告（在没有调试器的情况下——调试器会拦截崩溃）：
// SentrySDK.crash()  // 取消注释，在没有调试器的情况下运行，重新启动以查看崩溃报告
```

在几秒内检查 Sentry 仪表板。如果没有出现任何内容：
1. 设置 `options.debug = true` —— 将 SDK 内部信息打印到 Xcode 控制台
2. 验证 DSN 是否正确且项目存在
3. 确保初始化在 **主线程** 上进行

---

## 第 4 阶段：交叉链接

在完成 Apple 设置后，检查是否有缺少 Sentry 覆盖的配套后端：

```bash
# 检测配套后端
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -5
cat ../requirements.txt ../Pipfile 2>/dev/null | head -5
cat ../Gemfile 2>/dev/null | head -5
cat ../package.json 2>/dev/null | grep -E '"name"|"dependencies"' | head -5
```

如果发现了后端，请配置 `tracePropagationTargets` 以启用端到端的分布式跟踪，并建议相应的技能：

| 检测到的后端 | 建议的技能 | 跟踪头支持 |
|-----------------|--------------|---------------------|
| Go（`go.mod`） | `sentry-go-sdk` | 自动 |
| Python（`requirements.txt`） | `sentry-python-sdk` | 自动 |
| Ruby（`Gemfile`） | `sentry-ruby-sdk` | 自动 |
| Node.js 后端（`package.json`） | `sentry-node-sdk`（或 `sentry-express-sdk`） | 自动 |

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 事件未出现 | 设置 `debug: true`，验证 DSN 格式，确保初始化在主线程上进行 |
| 崩溃未被捕获 | **在没有调试器附加的情况下运行**——调试器会拦截信号 |
| 应用挂起未被报告 | 当调试器附加时自动禁用；检查 `appHangTimeoutInterval` |
| 会话回放未记录 | 验证 `sessionSampleRate > 0` 或 `onErrorSampleRate > 0`；在 iOS 26+ 上验证掩码和任何手动 Liquid Glass 门控 |
| 跟踪数据缺失 | 确认 `tracesSampleRate > 0`；检查 `enableAutoPerformanceTracing = true` |
| 性能分析数据缺失 | 验证 `configureProfiling` 中的 `sessionSampleRate > 0`；对于 `.trace` 生命周期，必须启用跟踪 |
| `rsync.samba` 构建错误（CocoaPods） | 目标设置 → “启用用户脚本沙箱” → `NO` |
| 选择了多个 SPM 产品 | 只选择 `Sentry`、`Sentry-Dynamic`、`SentrySwiftUI`、`Sentry-WithoutUIKitOrAppKit` 或 `SentrySPM` 中的**一个**（在 Swift 6.1+ 上使用 `NoUIFramework` 特性） |
| `inAppExclude` 编译错误 | 在 SDK 9.0.0 中已移除——请使用 `options.add(inAppInclude:)` |
| `enableAppHangTrackingV2` 编译错误 | 在 SDK 9.0.0 中已移除——请使用 `enableAppHangTracking`；在支持的地方 V2 行为是默认的 |
| 看门狗终止未被跟踪 | 需要 `enableCrashHandler = true`（默认如此） |
| 网络碎屑缺失 | 需要 `enableSwizzling = true`（默认如此） |
| `profilesSampleRate` 编译错误 | 在 SDK 9.0.0 中已移除——请改用 `configureProfiling` 闭包 |
