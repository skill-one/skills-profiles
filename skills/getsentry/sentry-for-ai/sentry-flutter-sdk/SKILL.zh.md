---
name: sentry-flutter-sdk
description: Flutter和Dart的完整Sentry SDK设置。当被要求“将Sentry添加到Flutter”、“安装sentry_flutter”、“在Dart中设置Sentry”或为Flutter应用程序配置错误监控、跟踪、分析、会话回放或日志记录时使用。支持Android、iOS、macOS、Linux、Windows和Web。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Flutter SDK

# Sentry Flutter SDK

一个有倾向性的向导，它会扫描您的 Flutter 或 Dart 项目，并指导您完成完整的 Sentry 设置——错误监控、跟踪、会话回放、日志记录、性能分析以及生态系统集成。

## 在何时调用此技能

- 用户询问在 Flutter 或 Dart 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Flutter 中进行错误监控、跟踪、性能分析、会话回放或日志记录
- 用户提到 `sentry_flutter`、`sentry_dart`、移动错误跟踪或 Sentry for Flutter
- 用户希望监控 iOS/Android 上的原生崩溃、ANRs 或应用挂起

> **注意：** 以下 SDK 版本和 API 反映了 `sentry_flutter` ≥9.14.0（当前稳定版，2026年2月）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/flutter/](https://docs.sentry.io/platforms/flutter/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检测 Flutter 项目类型和现有的 Sentry
cat pubspec.yaml | grep -E '(sentry|flutter|dart)'

# 检查 SDK 版本
cat pubspec.yaml | grep -A2 'environment:'

# 检查现有的 Sentry 初始化
grep -r "SentryFlutter.init\|Sentry.init" lib/ 2>/dev/null | head -5

# 检测导航库
grep -E '(go_router|auto_route|get:|beamer|routemaster)' pubspec.yaml

# 检测 HTTP 客户端
grep -E '(dio:|http:|chopper:)' pubspec.yaml

# 检测数据库包
grep -E '(sqflite|drift|hive|isar|floor)' pubspec.yaml

# 检测状态管理（用于集成模式）
grep -E '(flutter_bloc|riverpod|provider:|get:)' pubspec.yaml

# 检测 GraphQL
grep -E '(graphql|ferry|gql)' pubspec.yaml

# 检测 Firebase
grep -E '(firebase_core|supabase)' pubspec.yaml

# 检测用于跨链接的后端
ls ../backend/ ../server/ ../api/ 2>/dev/null
find .. -maxdepth 3 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" -o -name "*.csproj" \) 2>/dev/null | grep -v flutter | head -10

# 检测平台目标
ls android/ ios/ macos/ linux/ windows/ web/ 2>/dev/null
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `sentry_flutter` 已经在 `pubspec.yaml` 中？ | 跳过安装，跳转到功能配置 |
| Dart SDK `>=3.5`？ | `sentry_flutter` ≥9.0.0 所需 |
| `go_router` 或 `auto_route` 存在？ | 使用 `SentryNavigatorObserver`——特定模式适用 |
| `dio` 存在？ | 推荐 `sentry_dio` 集成 |
| `sqflite`、`drift`、`hive`、`isar` 存在？ | 推荐匹配的 `sentry_*` 数据库包 |
| 有 `android/` 和 `ios/` 目录吗？ | 可用完整移动功能集 |
| 只有 `web/` 目录吗？ | 会话回放和性能分析不可用 |
| 有 `macos/` 目录吗？ | 性能分析可用（alpha） |
| 检测到后端目录吗？ | 触发第四阶段跨链接 |

---

## 第二阶段：推荐

根据您发现的内容，提出具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖——始终设置这些）：**
- ✅ **错误监控** — 捕获 Dart 异常、Flutter 框架错误和原生崩溃（iOS + Android）
- ✅ **跟踪** — 自动注入导航、应用启动、网络请求和 UI 交互
- ✅ **会话回放** — 捕获用于调试的组件树截图（iOS + Android 仅限）

**可选（增强可观察性）：**
- ⚡ **性能分析** — CPU 性能分析；仅限 iOS 和 macOS（alpha）
- ⚡ **日志记录** — 通过 `Sentry.logger.*` 和 `sentry_logging` 集成进行结构化日志记录
- ⚡ **指标** — 计数器、仪表板、分布（SDK ≥9.11.0）

**平台限制——坦诚相告：**

| 功能 | 平台 | 备注 |
|-------|-----------|-------|
| 会话回放 | iOS、Android | macOS、Linux、Windows、Web 上不可用 |
| 性能分析 | iOS、macOS | alpha 状态；Android、Linux、Windows、Web 上不可用 |
| 原生崩溃 | iOS、Android、macOS | NDK/signal 处理；Linux/Windows/Web：仅 Dart 异常 |
| 应用启动指标 | iOS、Android | 桌面/Web 上不可用 |
| 慢/冻结帧 | iOS、Android、macOS | Linux、Windows、Web 上不可用 |
| Crons | N/A | **不可用** 在 Flutter/Dart SDK 中 |

建议："对于您的目标为 iOS/Android 的 Flutter 应用，我建议 Error Monitoring + Tracing + Session Replay。您希望我同时添加 Logging 和 Profiling（iOS/macOS alpha）吗？"

---

## 第三阶段：指导

### 确定您的设置路径

| 项目类型 | 推荐设置 |
|-------------|------------------|
| 任何 Flutter 应用 | 向导 CLI（处理 pubspec、初始化、符号上传） |
| 偏好手动 | 下方 B 路径——`pubspec.yaml` + `main.dart` |
| Dart 仅（CLI、服务器） | 下方 C 路径——纯 `sentry` 包 |

---

### 路径 A：向导 CLI（推荐）

> **您需要自行运行此命令**——向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```bash
> brew install getsentry/tools/sentry-wizard && sentry-wizard -i flutter
> ```
>
> 它处理组织/项目选择，将 `sentry_flutter` 添加到 `pubspec.yaml`，更新 `main.dart`，配置 `sentry_dart_plugin` 以上传调试符号，并添加构建脚本。以下是它创建/修改的内容：
>
> | 文件 | 操作 | 目的 |
> |------|--------|---------|
> | `pubspec.yaml` | 添加 `sentry_flutter` 依赖和 `sentry:` 配置块 | SDK + 符号上传配置 |
> | `lib/main.dart` | 用 `SentryFlutter.init()` 包装 `main()` | SDK 初始化 |
> | `android/app/build.gradle` | 添加 Proguard 配置引用 | Android 加密支持 |
> | `.sentryclirc` | 认证令牌和组织/项目配置 | 符号上传凭证 |
>
> **一旦完成，请返回并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下方的 B 路径（手动设置）。

---

### 路径 B：手动——Flutter 应用

**步骤 1 — 安装**

```bash
flutter pub add sentry_flutter
```

或手动添加到 `pubspec.yaml`：

```yaml
dependencies:
  flutter:
    sdk: flutter
  sentry_flutter: ^9.14.0
```

然后运行：

```bash
flutter pub get
```

**步骤 2 — 在 `lib/main.dart` 中初始化 Sentry**

```dart
import 'package:flutter/widgets.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = 'YOUR_SENTRY_DSN';
      options.sendDefaultPii = true;

      // 跟踪
      options.tracesSampleRate = 1.0; // 生产环境中降低到 0.1–0.2

      // 性能分析（仅限 iOS 和 macOS — alpha）
      options.profilesSampleRate = 1.0;

      // 会话回放（仅限 iOS 和 Android）
      options.replay.sessionSampleRate = 0.1;
      options.replay.onErrorSampleRate = 1.0;

      // 结构化日志记录（SDK ≥9.5.0）
      options.enableLogs = true;

      options.environment = const bool.fromEnvironment('dart.vm.product')
          ? 'production'
          : 'development';
    },
    // 必须项：包装根组件以启用截图、回放和用户交互跟踪
    appRunner: () => runApp(SentryWidget(child: MyApp())),
  );
}
```

**步骤 3 — 添加导航观察者**

将 `SentryNavigatorObserver` 添加到您的 `MaterialApp` 或 `CupertinoApp`：

```dart
import 'package:flutter/material.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorObservers: [
        SentryNavigatorObserver(),
      ],
      // 始终为 Sentry 命名您的路由以进行跟踪
      routes: {
        '/': (context) => HomeScreen(),
        '/profile': (context) => ProfileScreen(),
      },
    );
  }
}
```

对于 **GoRouter**：

```dart
import 'package:go_router/go_router.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

final GoRouter router = GoRouter(
  observers: [SentryNavigatorObserver()],
  routes: [
    GoRoute(
      path: '/',
      name: 'home', // 名称对于 Sentry 路由跟踪是必需的
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'profile/:id',
          name: 'profile', // 名称是必需的
          builder: (context, state) => ProfileScreen(
            id: state.pathParameters['id']!,
          ),
        ),
      ],
    ),
  ],
);
```

**步骤 4 — 配置调试符号上传**

可读的 Sentry 堆栈跟踪需要在使用 `--obfuscate` 构建时上传调试符号。

添加到 `pubspec.yaml`：

```yaml
dev_dependencies:
  sentry_dart_plugin: ^3.2.1

sentry:
  project: YOUR_PROJECT_SLUG
  org: YOUR_ORG_SLUG
  auth_token: YOUR_AUTH_TOKEN  # 优先使用 SENTRY_AUTH_TOKEN 环境变量
  upload_debug_symbols: true
  upload_sources: true
  upload_source_maps: true     # 用于 Web
```

构建和上传：

```bash
# Android
flutter build apk \
  --release \
  --obfuscate \
  --split-debug-info=build/debug-info \
  --extra-gen-snapshot-options=--save-obfuscation-map=build/app/obfuscation.map.json
dart run sentry_dart_plugin

# iOS
flutter build ipa \
  --release \
  --obfuscate \
  --split-debug-info=build/debug-info \
  --extra-gen-snapshot-options=--save-obfuscation-map=build/app/obfuscation.map.json
dart run sentry_dart_plugin

# Web
flutter build web --release --source-maps
dart run sentry_dart_plugin
```

---

### 路径 C：手动——Dart 仅（CLI / 服务器）

```yaml
# pubspec.yaml
dependencies:
  sentry: ^9.14.0
```

```dart
import 'package:sentry/sentry.dart';

Future<void> main() async {
  await Sentry.init(
    (options) {
      options.dsn = 'YOUR_SENTRY_DSN';
      options.tracesSampleRate = 1.0;
      options.enableLogs = true;
    },
    appRunner: myApp,
  );
}
```

---

### 快速参考：全功能的 `SentryFlutter.init()`

```dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = 'YOUR_SENTRY_DSN';
      options.sendDefaultPii = true;

      // 环境——通过 dart.vm.product 检测发布构建
      options.environment = const bool.fromEnvironment('dart.vm.product')
          ? 'production'
          : 'development';

      // 发布版本在 iOS/Android 上自动设置为 "packageName@version+build"
      // 如需覆盖：
      // options.release = 'my-app@1.0.0+42';

      // 错误采样——在高流量生产环境中减少以丢弃部分错误
      options.sampleRate = 1.0;

      // 跟踪——在高流量生产环境中降低到 0.1–0.2
      options.tracesSampleRate = 1.0;

      // 性能分析——仅限 iOS 和 macOS（alpha）；相对于 tracesSampleRate
      options.profilesSampleRate = 1.0;

      // 会话回放——仅限 iOS 和 Android（SDK ≥9.0.0）
      options.replay.sessionSampleRate = 0.1;   // 记录 10% 的所有会话
      options.replay.onErrorSampleRate = 1.0;   // 总是记录错误会话

      // 隐私默认值——所有文本和图像被遮盖
      options.privacy.maskAllText = true;
      options.privacy.maskAllImages = true;

      // 结构化日志记录（SDK ≥9.5.0）
      options.enableLogs = true;

      // 附件
      options.attachScreenshot = true;          // 错误时截图
      options.attachViewHierarchy = true;       // 错误时组件树

      // HTTP 客户端
      options.captureFailedRequests = true;     // 自动捕获 HTTP 错误
      options.maxRequestBodySize = MaxRequestBodySize.small;

      // Android 特定配置
      options.anrEnabled = true;                // ANR 检测
      options.enableNdkScopeSync = true;        // 同步范围到原生
      options.enableTombstone = false;          // Android 12+ 尸体（可选）

      // 导航（完全显示时间 — 可选）
      options.enableTimeToFullDisplayTracing = true;
    },
    appRunner: () => runApp(SentryWidget(child: MyApp())),
  );
}
```

---

### 导航：完全显示时间（TTFD）

TTID（初始显示时间）始终启用。TTFD 是可选的：

```dart
// 在 options 中启用：
options.enableTimeToFullDisplayTracing = true;
```

然后报告当您的屏幕加载了数据：

```dart
// 选项 1：组件包装器（在子组件首次渲染时标记 TTFD）
SentryDisplayWidget(child: MyWidget())

// 选项 2：手动 API 调用（异步数据加载后）
await _loadData();
SentryFlutter.currentDisplay()?.reportFullyDisplayed();
```

---

### 对于每个同意的功能

逐个通过功能。加载每个功能的参考文件，按照其步骤操作，然后在继续之前进行验证：

| 功能 | 参考 | 加载时... |
|---------|-----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基础） |
| 跟踪和性能 | `${SKILL_ROOT}/references/tracing.md` | 始终——导航、HTTP、数据库跨度 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | iOS/Android 面向用户的应用 |
| 性能分析 | `${SKILL_ROOT}/references/profiling.md` | iOS/macOS 性能敏感的应用 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志记录 / 日志跟踪关联 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 自定义业务指标 |
| 生态系统集成 | `${SKILL_ROOT}/references/ecosystem-integrations.md` | HTTP 客户端、数据库、GraphQL、状态管理 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### 核心的 `SentryFlutter.init()` 选项

| 选项 | 类型 | 默认值 | 目的 |
|--------|------|---------|---------|
| `dsn` | `string` | — | **必需。** 项目 DSN。环境：`SENTRY_DSN` 通过 `--dart-define` |
| `environment` | `string` | — | 例如，`"production"`，`"staging"`。环境：`SENTRY_ENVIRONMENT` |
| `release` | `string` | iOS/Android 自动设置 | `"packageName@version+build"`。环境：`SENTRY_RELEASE` |
| `dist` | `string` | — | 分发标识符；最多 64 个字符。环境：`SENTRY_DIST` |
| `sendDefaultPii` | `bool` | `false` | 包含 PII：IP 地址、用户标签、组件文本在回放中 |
| `sampleRate` | `double` | `1.0` | 错误事件采样（0.0–1.0） |
| `maxBreadcrumbs` | `int` | `100` | 每个事件的最大面包屑数 |
| `attachStacktrace` | `bool` | `true` | 自动将堆栈跟踪附加到消息 |
| `attachScreenshot` | `bool` | `false` | 错误时捕获截图（移动/桌面仅限） |
| `screenshotQuality` | 枚举 | `high` | 截图质量：`full`，`high`，`medium`，`low` |
| `attachViewHierarchy` | `bool` | `false` | 将 JSON 组件树作为附件在错误时附加 |
| `debug` | `bool` | 在调试中为 `true` | 详细的 SDK 输出。**在生产中永远不要强制 `true`** |
| `diagnosticLevel` | 枚举 | `warning` | 日志详细程度：`debug`，`info`，`warning`，`error`，`fatal` |
| `enabled` | `bool` | `true` | 完全禁用 SDK（例如，用于测试） |
| `maxCacheItems` | `int` | `30` | 最大离线缓存的信封数（Web 上不支持） |
| `sendClientReports` | `bool` | `true` | 发送 SDK 健康报告（丢失事件等） |
| `reportPackages` | `bool` | `true` | 报告 `pubspec.yaml` 依赖列表 |
| `reportSilentFlutterErrors` | `bool` | `false` | 捕获 `FlutterErrorDetails.silent` 错误 |
| `idleTimeout` | `Duration` | `3000ms` | 自动结束空闲用户交互事务 |

### 跟踪选项

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `tracesSampleRate` | `double` | — | 事务采样率 (0–1)。通过设置 >0 启用 |
| `tracesSampler` | `function` | — | 每个事务采样；覆盖 `tracesSampleRate` |
| `tracePropagationTargets` | `List` | — | 附加 `sentry-trace` + `baggage` 头部的 URL |
| `propagateTraceparent` | `bool` | `false` | 同时发送 W3C `traceparent` 头部 (SDK ≥9.7.0) |
| `enableTimeToFullDisplayTracing` | `bool` | `false` | 每个屏幕的 TTFD 跟踪（需主动选择） |
| `enableAutoPerformanceTracing` | `bool` | `true` | 自动启用性能监控 |
| `enableUserInteractionTracing` | `bool` | `true` | 为点击/触摸/长按事件创建事务 |
| `enableUserInteractionBreadcrumbs` | `bool` | `true` | 每个用户交互的面包屑 |

### 性能分析选项

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `profilesSampleRate` | `double` | — | 相对于 `tracesSampleRate` 的性能分析率。**仅限 iOS/macOS** |

### 本地 / 移动选项

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `autoInitializeNativeSdk` | `bool` | `true` | 自动初始化原生 Android/iOS SDK 层 |
| `enableNativeCrashHandling` | `bool` | `true` | 捕获原生崩溃 (NDK, 信号, Mach 异常) |
| `enableNdkScopeSync` | `bool` | `true` | 将 Dart 作用域同步到 Android NDK |
| `enableScopeSync` | `bool` | `true` | 将作用域数据同步到原生 SDK |
| `anrEnabled` | `bool` | `true` | ANR 检测 (Android) |
| `anrTimeoutInterval` | `int` | `5000` | ANR 超时（毫秒，Android） |
| `enableWatchdogTerminationTracking` | `bool` | `true` | OOM 杀死跟踪 (iOS) |
| `enableTombstone` | `bool` | `false` | Android 12+ 原生崩溃信息通过 `ApplicationExitInfo` 获取 |
| `attachThreads` | `bool` | `false` | 崩溃时附加所有线程 (Android) |
| `captureNativeFailedRequests` | `bool` | — | 原生 HTTP 错误捕获，独立于 Dart 客户端 (iOS/macOS, v9.11.0+) |
| `enableAutoNativeAppStart` | `bool` | `true` | 应用启动时间监控 (iOS/Android) |
| `enableFramesTracking` | `bool` | `true` | 慢/冻结帧监控 (iOS/Android/macOS) |
| `proguardUuid` | `string` | — | Android 加密映射的 Proguard UUID |

### 会话 & 发布健康选项

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `enableAutoSessionTracking` | `bool` | `true` | 崩溃无异常用户/会话指标会话跟踪 |
| `autoSessionTrackingInterval` | `Duration` | `30s` | 背景无活动前会话结束 |

### 重放选项 (`options.replay`)

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `replay.sessionSampleRate` | `double` | `0.0` | 所有会话记录的比例 |
| `replay.onErrorSampleRate` | `double` | `0.0` | 错误会话记录的比例 |

### 重放隐私选项 (`options.privacy`)

| 选项 / 方法 | 默认值 | 用途 |
|-------------|---------|---------|
| `privacy.maskAllText` | `true` | 掩盖所有文本组件内容 |
| `privacy.maskAllImages` | `true` | 掩盖所有图片组件 |
| `privacy.maskAssetImages` | `true` | 掩盖来自根资源包的图片 |
| `privacy.mask<T>()` | — | 掩盖特定组件类型及其所有子类 |
| `privacy.unmask<T>()` | — | 掩盖特定组件类型 |
| `privacy.maskCallback<T>()` | — | 每个组件实例的定制掩码决策 |

### HTTP 选项

| 选项 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `captureFailedRequests` | `bool` | `true` (Flutter) | 自动捕获 HTTP 错误 |
| `maxRequestBodySize` | enum | `never` | 请求体捕获：`never`、`small`、`medium`、`always` |
| `failedRequestStatusCodes` | `List` | `[500–599]` | 视为失败的 HTTP 状态码 |
| `failedRequestTargets` | `List` | `['.*']` | 监控的 URL 模式 |

### Hook 选项

| 选项 | 类型 | 用途 |
|------|------|------|
| `beforeSend` | `(SentryEvent, Hint) → SentryEvent?` | 修改或丢弃错误事件。返回 `null` 则丢弃 |
| `beforeSendTransaction` | `(SentryEvent) → SentryEvent?` | 修改或丢弃事务事件 |
| `beforeBreadcrumb` | `(Breadcrumb, Hint) → Breadcrumb?` | 存储前处理面包屑 |
| `beforeSendLog` | `(SentryLog) → SentryLog?` | 发送前过滤结构化日志 |

### 环境变量

在构建时通过 `--dart-define` 传递：

| 变量 | 用途 | 备注 |
|------|------|------|
| `SENTRY_DSN` | 数据源名称 | 从 `options.dsn` 回退 |
| `SENTRY_ENVIRONMENT` | 部署环境 | 从 `options.environment` 回退 |
| `SENTRY_RELEASE` | 发布标识符 | 从 `options.release` 回退 |
| `SENTRY_DIST` | 构建分发 | 从 `options.dist` 回退 |
| `SENTRY_AUTH_TOKEN` | 上传调试符号 | **仅构建工具使用 — 应用中绝不应嵌入** |
| `SENTRY_ORG` | 组织别名 | 由 `sentry_dart_plugin` 使用 |
| `SENTRY_PROJECT` | 项目别名 | 由 `sentry_dart_plugin` 使用 |

使用示例：

```bash
flutter build apk --release \
  --dart-define=SENTRY_DSN=https://xxx@sentry.io/123 \
  --dart-define=SENTRY_ENVIRONMENT=production
```

然后在代码中：

```dart
options.dsn = const String.fromEnvironment('SENTRY_DSN');
options.environment = const String.fromEnvironment('SENTRY_ENVIRONMENT', defaultValue: 'development');
```

### 生产环境设置

在发布前降低采样率并加固配置：

```dart
Future<void> main() async {
  final isProduction = const bool.fromEnvironment('dart.vm.product');

  await SentryFlutter.init(
    (options) {
      options.dsn = const String.fromEnvironment('SENTRY_DSN');
      options.environment = isProduction ? 'production' : 'development';

      // 高流量生产环境中的事务 10% 被跟踪
      options.tracesSampleRate = isProduction ? 0.1 : 1.0;

      // 跟踪的事务 100% 进行性能分析（性能分析始终是子集）
      options.profilesSampleRate = 1.0;

      // 所有错误会话重放，正常会话采样 5%
      options.replay.onErrorSampleRate = 1.0;
      options.replay.sessionSampleRate = isProduction ? 0.05 : 1.0;

      // 生产环境禁用调试日志
      options.debug = !isProduction;
    },
    appRunner: () => runApp(SentryWidget(child: MyApp())),
  );
}
```

### 默认自动启用的集成

调用 `SentryFlutter.init()` 时无需额外配置即激活：

| 集成 | 功能 |
|------|------|
| `FlutterErrorIntegration` | 捕获 `FlutterError.onError` 框架错误 |
| `RunZonedGuardedIntegration` | 捕获 runZonedGuarded 中的未处理 Dart 异常 |
| `NativeAppStartIntegration` | 应用启动时间 (iOS/Android) |
| `FramesTrackingIntegration` | 慢/冻结帧监控 (iOS/Android/macOS) |
| `NativeUserInteractionIntegration` | 原生层用户交互面包屑 |
| `UserInteractionIntegration` | Dart 层点击/触摸事务（需 `SentryWidget`） |
| `DeviceContextIntegration` | 设备型号、OS 版本、屏幕分辨率 |
| `AppContextIntegration` | 应用版本、构建号、bundle ID |
| `ConnectivityIntegration` | 网络连接变化面包屑 |
| `HttpClientIntegration` | 自动监控 Dart `http` 请求 |
| `SdkIntegration` | SDK 元数据标记 |
| `ReleaseIntegration` | 从包信息自动设置 iOS/Android 发布版本 |

---

## 验证

设置后，测试 Sentry 是否接收事件：

```dart
// 开发期间在可见位置添加测试按钮：
ElevatedButton(
  onPressed: () {
    throw Exception('Sentry 测试错误!');
  },
  child: const Text('测试 Sentry 错误'),
)

// 或手动捕获：
ElevatedButton(
  onPressed: () {
    Sentry.captureMessage('Sentry 测试消息', level: SentryLevel.info);
  },
  child: const Text('测试 Sentry 消息'),
)

// 测试结构化日志：
ElevatedButton(
  onPressed: () {
    Sentry.logger.info('来自 Flutter 应用的测试日志');
  },
  child: const Text('测试 Sentry 日志'),
)
```

**检查 Sentry 仪表盘：**
- **问题** → 测试错误应在几秒内出现
- **跟踪** → 查找导航事务及其子跨度
- **重放** → 应用交互后可见会话记录 (iOS/Android 仅限)
- **日志** → 结构化日志条目（若 `enableLogs: true`）

> ⚠️ **调试模式下的平台限制：**
> - 原生崩溃、会话重放、慢/冻结帧和应用启动指标仅在 iOS/Android 的发布版本中完全工作
> - 运行 `flutter run --release` 或使用真实设备/模拟器测试原生功能
> - 调试模式使用 Dart VM JIT 编译 — 部分原生集成表现不同

---

## 第 4 步：跨链

完成 Flutter 设置后，检查缺少 Sentry 覆盖的后端：

```bash
# 相邻后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
ls ../backend/package.json ../server/package.json 2>/dev/null
```

若后端缺少 Sentry，建议匹配技能：

| 检测到 | 建议技能 |
|------|------|
| Go 后端 (`go.mod`) | `sentry-go-sdk` |
| Python 后端 (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby 后端 (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js 后端 | `sentry-node-sdk` |
| .NET 后端 (`*.csproj`) | `sentry-dotnet-sdk` |
| React / Next.js 网站 | `sentry-react-sdk` / `sentry-nextjs-sdk` |

**分布式跟踪** — 若添加后端技能，在 Flutter 中配置 `tracePropagationTargets` 将跟踪上下文传播到 API：

```dart
options.tracePropagationTargets = ['api.myapp.com', 'localhost'];
options.propagateTraceparent = true; // 同时发送 W3C traceparent 头部
```

这可将移动事务与后端跟踪在 Sentry 水falls 视图中关联。

---

## 故障排除

| 问题 | 解决方案 |
|------|------|
| 事件未出现在 Sentry | 设置 `options.debug = true` — SDK 日志输出 Flutter 控制台；验证 DSN 是否正确 |
| `SentryFlutter.init` 抛出异常 | 确保主函数是 `async` 并 `await SentryFlutter.init(...)` |
| Sentry 中的堆栈跟踪无法读取 | 使用 `sentry_dart_plugin` 上传调试符号；构建时使用 `--obfuscate --split-debug-info` |
| Web 上的堆栈跟踪缺失 | 构建 `--source-maps` 并运行 `dart run sentry_dart_plugin` 上传 |
| 原生崩溃未捕获 | 确认 `enableNativeCrashHandling: true`；在发布模式下测试，而非调试模式 |
| 会话重放未记录 | 仅限 iOS/Android；确认 `SentryWidget` 包裹根组件；检查 `replay.onErrorSampleRate` |
| 重放显示空白屏幕 | 确认 `SentryWidget(child: MyApp())` 是最外层组件；不在 navigator 内 |
| 性能分析未工作 | 仅限 iOS 和 macOS (alpha)；确认 `tracesSampleRate > 0` 首先设置 |
| 导航未跟踪 | 添加 `SentryNavigatorObserver()` 到 `navigatorObservers`；命名所有路由 |
| GoRouter 路由未命名 | 所有 `GoRoute` 条目添加 `name:` — 未命名路由被视为 `null` 被跟踪 |
| TTFD 从未报告 | 加载数据后调用 `SentryFlutter.currentDisplay()?.reportFullyDisplayed()`，或使用 `SentryDisplayWidget` 包裹 |
| `sentry_dart_plugin` 认证错误 | 设置 `SENTRY_AUTH_TOKEN` 环境变量，而非在 `pubspec.yaml` 中硬编码 |
| Android ProGuard 映射缺失 | 确保 `--extra-gen-snapshot-options=--save-obfuscation-map=...` 标志设置 |
| iOS dSYM 未上传 | `sentry_dart_plugin` 处理此功能；检查 `pubspec.yaml` `sentry:` 块中的 `upload_debug_symbols: true` |
| `pub get` 失败：Dart SDK 过旧 | `sentry_flutter` ≥9.0.0 需要 Dart ≥3.5.0；运行 `flutter upgrade` |
| Android 调试模式热重启崩溃 | 已知问题 (SDK ≥9.9.0 已修复)；若版本较旧则升级 |
| ANR 检测过于激进 | 增加 `anrTimeoutInterval` (默认：5000ms) |
| 仪表盘事务过多 | 降低 `tracesSampleRate` 至 `0.1` 或使用 `tracesSampler` 丢弃健康检查 |
| `beforeSend` 未对原生崩溃触发 | 预期行为 — `beforeSend` 仅拦截 Dart 层事件；原生崩溃绕过它 |
| 定时任务不可用 | Flutter/Dart SDK 不支持 Sentry 定时任务；使用服务器端 SDK 替代 |
| 测试中的 `SentryWidget` 警告 | 在 `setUpAll` 中用 `SentryFlutter.init()` 包裹测试组件，或使用 `enabled: false` |
| Firebase Remote Config：Linux/Windows | `sentry_firebase_remote_config` 不支持 Linux/Windows (Firebase 限制) |
| Web 上的 Isar 跟踪 | `sentry_isar` **不支持 Web** (Isar 不支持 Web) |
