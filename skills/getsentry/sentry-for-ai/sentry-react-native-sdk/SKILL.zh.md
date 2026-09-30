---
name: sentry-react-native-sdk
description: React Native 和 Expo 的完整 Sentry SDK 配置。当被要求“为 React Native 添加 Sentry”、“安装 @sentry/react-native”、“在 Expo 中配置 Sentry”或为 React Native 应用配置错误监控、跟踪、性能分析、会话回放或日志记录时使用。支持 Expo 管理型、Expo 精简型以及纯 React Native。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > React Native SDK

# Sentry React Native SDK

一个有主见的向导，它会扫描您的 React Native 或 Expo 项目，并指导您完成完整的 Sentry 设置——错误监控、追踪、分析、会话回放、日志记录等。

## 在何时调用此技能

- 用户询问在 RN 或 Expo 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 React Native 中进行错误监控、追踪、分析、会话回放或日志记录
- 用户提到 `@sentry/react-native`、移动错误跟踪或 Sentry for Expo
- 用户希望监控 iOS/Android 上的原生崩溃、ANRs 或应用挂起

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的当前状态（`@sentry/react-native` ≥6.0.0，最低推荐 ≥8.0.0）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/react-native/](https://docs.sentry.io/platforms/react-native/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，请运行这些命令以了解项目：

```bash
# 检测项目类型和现有的 Sentry
cat package.json | grep -E '"(react-native|expo|@expo|@sentry/react-native|sentry-expo)"'

# 区分 Expo 管理的、精简的或纯 RN
ls app.json app.config.js app.config.ts 2>/dev/null
cat app.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('Expo 管理的' if 'expo' in d else '精简的/纯')" 2>/dev/null

# 检测 Expo SDK 版本（重要：Expo SDK 50+ 需要 `@sentry/react-native`）
cat package.json | grep '"expo"'

# 检测导航库
grep -E '"(@react-navigation/native|react-native-navigation)"' package.json

# 检测状态管理（Redux → 可用面包屑集成）
grep -E '"(redux|@reduxjs/toolkit|zustand|mobx)"' package.json

# 检测现有的 Sentry 初始化
grep -r "Sentry.init" src/ app/ App.tsx App.js _layout.tsx 2>/dev/null | head -5

# 检测 Hermes（影响源映射处理）
cat android/app/build.gradle 2>/dev/null | grep -i hermes
cat ios/Podfile 2>/dev/null | grep -i hermes

# 检测 Expo Router
ls app/_layout.tsx app/_layout.js 2>/dev/null

# 检测用于跨链接的后端
ls backend/ server/ api/ 2>/dev/null
find . -maxdepth 3 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" -o -name "package.json" \) 2>/dev/null | grep -v node_modules | head -10
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `package.json` 中是否有 `expo`？ | Expo 路径（配置插件 + `getSentryExpoConfig`）与精简的/纯 RN 路径 |
| Expo SDK ≥50？ | 直接使用 `@sentry/react-native`；旧版本 = `sentry-expo`（遗留，不要使用） |
| `app.json` 是否包含 `"expo"` 键？ | 管理的 Expo——向导最简单；配置插件处理所有原生配置 |
| 是否存在 `app/_layout.tsx`？ | Expo Router 项目——初始化放在 `_layout.tsx` 中 |
| `package.json` 中是否已存在 `@sentry/react-native`？ | 跳过安装，跳转到功能配置 |
| 是否存在 `@react-navigation/native`？ | 推荐 `reactNavigationIntegration` 用于屏幕跟踪 |
| 是否存在 `react-native-navigation`？ | 推荐 `reactNativeNavigationIntegration`（Wix） |
| 是否检测到后端目录？ | 触发第四阶段跨链接 |

---

## 第二阶段：推荐

根据您发现的内容提出具体的建议，不要提出开放式问题——直接提出建议：

**推荐（核心覆盖——始终设置这些）：**
- ✅ **错误监控**——捕获 JS 异常、原生崩溃（iOS + Android）、ANRs 和应用挂起
- ✅ **追踪**——移动性能至关重要；自动注入导航、应用启动、网络请求
- ✅ **会话回放**——移动回放捕获屏幕截图和触摸事件，用于调试用户问题

**可选（增强的可观察性）：**
- ⚡ **分析**——iOS CPU 分析（跨平台 JS 分析）；生产环境中低开销
- ⚡ **日志记录**——通过 `Sentry.logger.*` 结构化日志；链接到追踪以获取完整上下文
- ⚡ **用户反馈**——直接从您的应用收集用户提交的 Bug 报告

**推荐逻辑：**

| 功能 | 当...推荐 |
|---------|------------------|
| 错误监控 | **始终**——任何移动应用的最低基线 |
| 追踪 | **始终用于移动**——应用启动、导航和网络延迟很重要 |
| 会话回放 | 面向用户的生产品牌；可视化地调试用户报告的问题 |
| 分析 | 性能敏感的屏幕、启动时间问题或生产性能调查 |
| 日志记录 | 应用使用结构化日志，或您希望在 Sentry 中实现日志到追踪的关联 |
| 用户反馈 | Beta 或面向客户的品牌，您希望收集用户提交的 Bug 报告 |

建议：*"对于您的 [Expo 管理的 / 精简的 RN] 应用，我建议设置错误监控 + 追踪 + 会话回放。您希望我还要添加分析和日志记录吗？"*

如果你的应用在根组件挂载后执行大量异步工作（例如，获取配置、等待认证），请在工作完成后调用一次 `Sentry.appLoaded()`。这向 Sentry 信号应用启动的真正结束，并生成更准确的应用启动持续时间测量结果。

```typescript
// 在异步初始化完成后调用，例如在 useEffect 中或在加载屏幕之后：
useEffect(() => {
  fetchConfig().then(() => {
    Sentry.appLoaded();  // 标记应用启动阶段的结束
  });
}, []);
```

如果你不调用 `Sentry.appLoaded()`，SDK 会自动估计应用启动的结束时间。

---

### 导航设置 — React Navigation (v5+)

**推荐：使用 `Sentry.NavigationContainer` 包装器（SDK ≥8.13.0）**

`NavigationContainer` 的即插即用替代方案，可自动连接导航跟踪：

```typescript
import * as Sentry from "@sentry/react-native";

// 将 NavigationContainer 替换为 Sentry.NavigationContainer
<Sentry.NavigationContainer>
  <Stack.Navigator>
    {/* 你的屏幕 */}
  </Stack.Navigator>
</Sentry.NavigationContainer>
```

就这样！包装器会自动：
- 创建 `reactNavigationIntegration`
- 注册导航容器引用
- 捕获导航事件（SDK ≥8.13.0）的面包屑
- 按每个屏幕跟踪初始显示时间 (TTID)

**替代方案：手动设置（适用于 SDK <8.13.0 或自定义配置）**

```typescript
import { reactNavigationIntegration } from "@sentry/react-native";
import { NavigationContainer, createNavigationContainerRef } from "@react-navigation/native";

const navigationIntegration = reactNavigationIntegration({
  enableTimeToInitialDisplay: true,   // 按每个屏幕跟踪 TTID
  routeChangeTimeoutMs: 1_000,        // 路由变更稳定的最长等待时间
  ignoreEmptyBackNavigationTransactions: true,
});

// 添加到 Sentry.init 的 integrations 数组
Sentry.init({
  integrations: [navigationIntegration],
  // ...
});

// 在你的组件中：
const navigationRef = createNavigationContainerRef();

<NavigationContainer
  ref={navigationRef}
  onReady={() => {
    navigationIntegration.registerNavigationContainer(navigationRef);
  }}
>
```

### 导航设置 — Wix React Native Navigation

```typescript
import * as Sentry from "@sentry/react-native";
import { Navigation } from "react-native-navigation";

Sentry.init({
  integrations: [Sentry.reactNativeNavigationIntegration({ navigation: Navigation })],
  // ...
});
```

---

### 包装你的根组件

始终包装你的根组件——这启用了 React 错误边界，并确保组件树级别的崩溃被捕获：

```typescript
export default Sentry.wrap(App);
```

---

### 对每个约定的功能

逐个功能进行操作。加载每个功能的参考文件，按照其步骤操作，然后验证后再继续：

| 功能 | 参考 | 加载时...
|------|------|-------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基准） |
| 跟踪与性能 | `${SKILL_ROOT}/references/tracing.md` | 始终用于移动端（应用启动、导航、网络） |
| 性能分析 | `${SKILL_ROOT}/references/profiling.md` | 性能敏感的生产应用 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志 / 日志到跟踪关联 |
| 用户反馈 | `${SKILL_ROOT}/references/user-feedback.md` | 收集用户提交的报告 |
| Expo 配置插件 | `${SKILL_ROOT}/references/expo-config-plugin.md` | 配置 `@sentry/react-native/expo` 插件 |

对每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### 核心的 `Sentry.init()` 选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | `string` | — | **必需。** 项目 DSN；如果为空，SDK 将被禁用。环境变量：`SENTRY_DSN` |
| `environment` | `string` | — | 例如，`"production"`，`"staging"`。环境变量：`SENTRY_ENVIRONMENT` |
| `release` | `string` | — | 应用版本，例如，`"my-app@1.0.0+42"`。环境变量：`SENTRY_RELEASE` |
| `dist` | `string` | — | 构建编号 / 变体标识符（最多 64 个字符）。环境变量：`SENTRY_DIST` |
| `sendDefaultPii` | `boolean` | `false` | 是否包含 PII：IP 地址、Cookie、用户数据 |
| `sampleRate` | `number` | `1.0` | 错误事件采样（0.0–1.0） |
| `maxBreadcrumbs` | `number` | `100` | 每个事件的最大面包屑数量 |
| `attachStacktrace` | `boolean` | `true` | 自动将堆栈跟踪附加到消息 |
| `attachScreenshot` | `boolean` | `false` | 在错误时捕获屏幕截图（SDK ≥4.11.0） |
| `screenshot` | `object` | — | 精细的屏幕截图遮罩；仅在 `attachScreenshot: true` 时有效。见下方的 **屏幕截图遮罩选项** |
| `attachViewHierarchy` | `boolean` | `false` | 将 JSON 视图层次结构作为附件附加 |
| `debug` | `boolean` | `false` | SDK 的详细输出。**生产环境中绝不能使用** |
| `enabled` | `boolean` | `true` | 完全禁用 SDK（例如，用于测试） |
| `ignoreErrors` | `string[] \| RegExp[]` | — | 忽略匹配这些模式的错误 |
| `ignoreTransactions` | `string[] \| RegExp[]` | — | 忽略匹配这些模式的交易 |
| `maxCacheItems` | `number` | `30` | 离线缓存的信封最大数量 |
| `defaultIntegrations` | `boolean` | `true` | 设置为 `false` 以禁用所有默认集成 |
| `integrations` | `array \| function` | — | 添加或过滤集成 |

#### 屏幕截图遮罩选项

作为 `Sentry.init()` 中的 `screenshot` 键传递，当 `attachScreenshot: true` 时：

```typescript
Sentry.init({
  attachScreenshot: true,
  screenshot: {
    maskAllText: true,       // 默认：true — 遮罩所有文本节点
    maskAllImages: true,     // 默认：true — 遮罩所有图像
    maskedViewClasses: ['com.mapbox.maps.MapView'],    // 始终遮罩这些原生视图类
    unmaskedViewClasses: ['com.example.SafeView'],     // 始终显示这些原生视图类
  },
});
```

| 子选项 | 类型 | 默认值 | 目的 |
|--------|------|--------|------|
| `maskAllText` | `boolean` | `true` | 遮罩屏幕截图中的所有文本节点 |
| `maskAllImages` | `boolean` | `true` | 遮罩屏幕截图中的所有图像 |
| `maskedViewClasses` | `string[]` | `[]` | 原生视图类名，始终遮罩（Android/iOS） |
| `unmaskedViewClasses` | `string[]` | `[]` | 原生视图类名，始终显示（Android/iOS） |

### 跟踪选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `tracesSampleRate` | `number` | `0` | 交易采样率（0–1）。开发环境中使用 `1.0` |
| `tracesSampler` | `function` | — | 每个交易的采样；覆盖 `tracesSampleRate` |
| `tracePropagationTargets` | `(string \| RegExp)[]` | `[/.*/]` | 接收分布式跟踪头的 API URL |
| `profilesSampleRate` | `number` | `0` | 性能分析采样率（应用于跟踪的交易） |

### 原生 / 移动选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `enableNative` | `boolean` | `true` | 设置为 `false` 以仅使用 JS（无原生 SDK） |
| `enableNativeCrashHandling` | `boolean` | `true` | 捕获原生硬崩溃（iOS/Android） |
| `enableNativeFramesTracking` | `boolean` | — | 慢/冻结帧跟踪。**在 Expo Go 中禁用** |
| `enableWatchdogTerminationTracking` | `boolean` | `true` | OOM 杀死检测（iOS） |
| `enableAppHangTracking` | `boolean` | `true` | 应用挂起检测（iOS、tvOS、macOS） |
| `appHangTimeoutInterval` | `number` | `2` | 秒数，在此之前将分类为应用挂起（iOS） |
| `enableAutoPerformanceTracing` | `boolean` | `true` | 自动性能仪器 |
| `enableNdkScopeSync` | `boolean` | `true` | Java→NDK 范围同步（Android） |
| `attachThreads` | `boolean` | `false` | 在崩溃时自动附加所有线程（Android） |
| `attachAllThreads` | `boolean` | `false` | 将所有线程的完整堆栈跟踪附加到每个捕获的事件（iOS 仅限，需要 Cocoa SDK ≥9.9.0） |
| `autoInitializeNativeSdk` | `boolean` | `true` | 设置为 `false` 以手动初始化原生 SDK |
| `onReady` | `function` | — | 原生 SDK 初始化后的回调 |
| `enableTurboModuleTracking` | `boolean` | `false` | **实验性。** 安装原生 TurboModule 性能日志，用于崩溃归因和按模块的跨度。RN 0.75+ 新架构仅限；在旧架构上无操作（SDK ≥8.17.0） |

### 会话与发布健康选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `autoSessionTracking` | `boolean` | `true` | 会话跟踪（无崩溃的用户/会话） |
| `sessionTrackingIntervalMillis` | `number` | `30000` | 会话结束前背景运行毫秒数 |

### 回放选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `replaysSessionSampleRate` | `number` | `0` | 所有会话记录的分数 |
| `replaysOnErrorSampleRate` | `number` | `0` | 错误会话记录的分数 |

### 日志记录选项（SDK ≥7.0.0）

| 选项 | 类型 | 目的 |
|------|------|------|
| `enableLogs` | `boolean` | 启用 `Sentry.logger.*` API |
| `enableAutoConsoleLogs` | `boolean` | 当 `enableLogs: true` 时自动捕获 `console.*` 调用。设置为 `false` 以仅使用手动 `Sentry.logger.*`（SDK ≥8.14.0，默认：`true`） |
| `beforeSendLog` | `function` | 在发送前过滤/修改日志 |
| `logsOrigin` | `'native' \| 'js' \| 'all'` | 过滤日志源（SDK ≥7.7.0） |

### 回调选项

| 选项 | 类型 | 目的 |
|------|------|------|
| `beforeSend` | `(event, hint) => event \| null` | 修改/丢弃 JS 错误事件。⚠️ 不适用于原生崩溃 |
| `beforeSendTransaction` | `(event) => event \| null` | 修改/丢弃交易事件 |
| `beforeBreadcrumb` | `(breadcrumb, hint) => breadcrumb \| null` | 在存储前处理面包屑 |
| `onNativeLog` | `(log: { level, component, message }) => void` | 拦截原生 SDK 日志消息并转发到 JS 控制台。仅在 `debug: true` 时触发 |

### 环境变量

| 变量 | 目的 | 备注 |
|------|------|------|
| `SENTRY_DSN` | 数据源名称 | 从 `dsn` 选项回退 |
| `SENTRY_AUTH_TOKEN` | 上传源映射和 dSYMs | **绝不能提交——使用 CI 密钥** |
| `SENTRY_ORG` | 组织缩写 | 由向导和构建插件使用 |
| `SENTRY_PROJECT` | 项目缩写 | 由向导和构建插件使用 |
| `SENTRY_RELEASE` | 发布标识符 | 从 `release` 选项回退 |
| `SENTRY_DIST` | 分发标识符 | 从 `dist` 选项回退 |
| `SENTRY_ENVIRONMENT` | 环境名称 | 从 `environment` 选项回退 |
| `SENTRY_DISABLE_AUTO_UPLOAD` | 跳过源映射上传 | 在本地构建期间设置为 `true` |
| `EXPO_PUBLIC_SENTRY_DSN` | Expo 公共环境变量，用于 DSN | 安全地嵌入到客户端包中 |
| `SENTRY_EAS_BUILD_CAPTURE_SUCCESS` | EAS 构建钩子：捕获成功的构建 | 在 EAS 密钥中设置为 `true` |
| `SENTRY_EAS_BUILD_TAGS` | EAS 构建钩子：附加标签 JSON | 例如，`{"team":"mobile"}` |

### 默认集成（自动启用）

这些集成会自动启用——无需配置：

| 集成 | 它的作用 |
|------|------|
| `ReactNativeErrorHandlers` | 捕获未处理的 JS 异常和 Promise 拒绝 |
| `Release` | 将发布/版本附加到所有事件 |
| `Breadcrumbs` | 记录控制台日志、HTTP 请求、用户手势作为面包屑 |
| `HttpClient` | 添加 HTTP 请求/响应面包屑 |
| `DeviceContext` | 将设备/操作系统/电池信息附加到事件 |
| `AppContext` | 将应用版本、包 ID 和内存信息附加到事件 |
| `CultureContext` | 将区域设置和时区附加到事件 |
| `Screenshot` | 在错误时捕获屏幕截图（当 `attachScreenshot: true`） |
| `ViewHierarchy` | 附加视图层次结构（当 `attachViewHierarchy: true`） |
| `NativeLinkedErrors` | 将 JS 错误链接到其原生崩溃对应项 |
| `TurboModuleContext` | 跟踪 TurboModule 调用；将原生崩溃归因于高级 RN 模块 + 方法（例如，`RNSentry.captureEnvelope`） |

### 选择性集成

| 集成 | 如何启用 |
|------|----------|
| `mobileReplayIntegration()` | 添加到 `integrations` 数组 |
| `reactNavigationIntegration()` | 添加到 `integrations` 数组 |
| `reactNativeNavigationIntegration()` | 添加到 `integrations` 数组（Wix 仅限） |
| `feedbackIntegration()` | 添加到 `integrations` 数组（用户反馈小部件；支持 `enableShakeToReport` 用于原生摇晃检测） |
| `deeplinkIntegration()` | 添加到 `integrations` 数组（自动捕获深度链接 URL 作为面包屑；选择性启用） |
| `turboModuleContextIntegration()` | **默认**——自动跟踪 `RNSentry` TurboModule。可选配置 `{ modules: [...] }` 以跟踪自定义 TurboModules |

### 跟踪自定义 TurboModules

`TurboModuleContext` 集成默认启用，并自动跟踪内置的 `RNSentry` TurboModule。要跟踪自己的自定义 TurboModules，请显式配置该集成：

```typescript
import * as Sentry from "@sentry/react-native";
import { NativeModules } from "react-native";

Sentry.init({
  dsn: "YOUR_DSN",
  integrations: [
    Sentry.turboModuleContextIntegration({
      modules: [
        {
          name: "MyCustomModule",
          module: NativeModules.MyCustomModule,
          // 可选：跳过特定方法以避免跟踪开销
          skipMethods: ["addListener", "removeListeners"],
        },
      ],
    }),
  ],
});
```

当原生崩溃发生在跟踪的 TurboModule 方法调用内时，崩溃报告将包括 `contexts.turbo_module`，其中包含模块名称和方法，从而更容易识别触发崩溃的确切 RN API 调用。

### 愤怒点击检测（TouchEventBoundary）

`TouchEventBoundary`（包装你的应用根）包含内置的愤怒点击检测。当用户在 1 秒内对同一元素点击 3 次或更多次时，会发出 `ui.multiClick` 面包屑，并在回放时间轴上显示。通过属性配置：

```tsx
<Sentry.TouchEventBoundary
  enableRageTapDetection={true}   // 默认：true — 设置为 false 以禁用
  rageTapThreshold={3}            // 触发所需的点击次数（默认：3）
  rageTapTimeWindow={1000}        // 检测窗口毫秒数（默认：1000）
>
  <App />
</Sentry.TouchEventBoundary>
```

### 生产环境设置

在发布到生产环境之前降低采样率并加固配置：

```typescript
Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  environment: __DEV__ ? "development" : "production",

  // 在高流量的生产环境中跟踪 10–20% 的交易
  tracesSampleRate: __DEV__ ? 1.0 : 0.1,

  // 跟踪所有跟踪的交易的 100%（性能分析始终是跟踪的子集）
  profilesSampleRate: 1.0,

  // 捕获所有错误会话，正常会话采样 5%
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: __DEV__ ? 1.0 : 0.05,

  // 设置发布和 dist 以进行准确的源映射查找
  release: "my-app@" + Application.nativeApplicationVersion,
  dist: String(Application.nativeBuildVersion),

  // 在生产环境中禁用调试日志
  debug: __DEV__,
});
```

---

### 源映射与调试符号

源映射和调试符号将压缩的堆栈跟踪转换为可读的堆栈跟踪。配置正确时，Sentry 会显示你源代码的确切行号。通用的 auth-token 和 CI 设置位于 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)；React Native 特定的上传机制如下。

#### 上传如何工作

| 平台 | 上传的内容 | 时间 |
|------|------------|------|
| **iOS** (JS) | 源映射（`.map` 文件） | Xcode 构建期间 |
| **iOS** (原生) | dSYM 套件 | Xcode 归档 / Xcode Cloud 期间 |
| **Android** (JS) | 源映射 + Hermes `.hbc.map` | Gradle 构建期间 |
| **Android** (原生) | Proguard 映射 + NDK `.so` 文件 | Gradle 构建期间 |

#### Expo：自动上传

`@sentry/react-native/expo` 配置插件会自动为原生构建设置上传钩子。源映射文件会在 `eas build` 和 `expo run:ios/android`（发布版本）期间上传。

```bash
SENTRY_AUTH_TOKEN=sntrys_... npx expo run:ios --configuration Release
```

#### 手动上传（裸 RN）

如果需要手动上传源映射文件：

```bash
npx sentry-cli sourcemaps upload \
  --org YOUR_ORG \
  --project YOUR_PROJECT \
  --release "my-app@1.0.0+1" \
  ./dist
```

---

### EAS 构建钩子

在 Sentry 中监控您的 Expo 应用服务 (EAS) 构建。SDK 提供了三个二进制钩子——`sentry-eas-build-on-complete`、`sentry-eas-build-on-error` 和 `sentry-eas-build-on-success`，它们将构建事件捕获为 Sentry 错误或消息。

**步骤 1 — 在 `package.json` 中注册钩子**

```json
{
  "scripts": {
    "eas-build-on-complete": "sentry-eas-build-on-complete"
  }
}
```

使用 `eas-build-on-complete` 在一个钩子中捕获失败和（可选的）成功。如果您需要独立控制，可以使用 `eas-build-on-error` 或 `eas-build-on-success` 单独使用。

**步骤 2 — 在您的 EAS 秘密中设置 `SENTRY_DSN`**

```bash
eas secret:create --name SENTRY_DSN --value "https://...@sentry.io/..."
```

钩子从构建环境中读取 `SENTRY_DSN`——它不会使用与您的应用相同的 `.env` 文件。

**可选环境变量：**

| 变量 | 目的 |
|------|------|
| `SENTRY_EAS_BUILD_CAPTURE_SUCCESS` | 设置为 `true` 以捕获成功构建（默认仅捕获错误） |
| `SENTRY_EAS_BUILD_TAGS` | 额外标签的 JSON 对象，例如 `{"team":"mobile","channel":"production"}` |
| `SENTRY_EAS_BUILD_ERROR_MESSAGE` | 失败构建的自定义错误消息 |
| `SENTRY_EAS_BUILD_SUCCESS_MESSAGE` | 成功构建的自定义消息 |

> **工作原理：** 钩子脚本是一个 EAS 的 [npm 生命周期钩子](https://docs.expo.dev/build-reference/npm-hooks/)。EAS 在构建过程结束时调用匹配 `eas-build-on-*` 的 `package.json` 脚本。脚本从 `@expo/env`、`.env` 或 `.env.sentry-build-plugin` 加载环境变量——不会覆盖环境中已有的 EAS 秘密。

---

## 验证

设置完成后，测试 Sentry 是否接收事件：

```typescript
// 快速测试——抛出错误，Sentry.wrap(App) 捕获它
<Button
  title="测试 Sentry 错误"
  onPress={() => {
    throw new Error("我的第一个 Sentry 错误！");
  }}
/>

// 或者手动捕获
<Button
  title="测试 Sentry 消息"
  onPress={() => {
    Sentry.captureMessage("Sentry 测试消息", "info");
  }}
/>
```

**检查 Sentry 仪表板：**
- **问题** → 您的测试错误应在几秒钟内出现
- **跟踪** → 查找带有子跨度（spans）的 "main" 事务
- **回放** → 应用交互后可见会话录制（仅限原生构建——不适用于 Expo Go）
- **日志** → 如果 `enableLogs: true`，则显示结构化日志条目

> ⚠️ **Expo Go 限制：** 原生崩溃、会话回放、慢速/冻结帧、TTID 和 TTFD 仅在原生构建（`eas build` 或 `expo run`）中工作。Expo Go 仅以纯 JS 模式运行。设置 `enableNativeFramesTracking: !isRunningInExpoGo()` 以避免警告。

如果什么都没有出现：
1. 设置 `debug: true`——SDK 将日志输出到 Metro 控制台
2. 验证 DSN 是否正确且 Sentry 项目是否存在
3. 确保 `Sentry.wrap(App)` 应用于根组件
4. 对于原生崩溃，构建一个发布版本（调试模式下崩溃可能不会转发）

---

## 第 4 步：跨链接

完成 React Native 设置后，检查是否有后端或 Web 前端缺少 Sentry 覆盖：

```bash
# 相邻的后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
ls ../backend/package.json ../server/package.json 2>/dev/null

# 同一或兄弟仓库中的 Web 前端
ls ../web ../frontend ../dashboard 2>/dev/null
cat ../web/package.json ../frontend/package.json 2>/dev/null | grep -E '"react"|"svelte"|"next"'

# 检查 OpenTelemetry（用于分布式跟踪互操作性）
grep -r "opentelemetry" ../backend/go.mod ../server/requirements.txt 2>/dev/null
```

如果存在没有 Sentry 的后端或 Web 前端，建议匹配的技能：

| 检测到 | 建议技能 |
|-------|---------|
| Go 后端 (`go.mod`) | `sentry-go-sdk` |
| Python 后端 (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby 后端 (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js 后端（Express、Fastify 等） | `@sentry/node` — 查看 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |
| React / Next.js Web | `sentry-react-sdk` |
| Svelte / SvelteKit Web | `sentry-svelte-sdk` |

**分布式跟踪设置**——如果添加了后端技能，请在 React Native 中配置 `tracePropagationTargets` 以将跟踪上下文传播到您的 API：

```typescript
Sentry.init({
  tracePropagationTargets: [
    "localhost",
    /^https:\/\/api\.yourapp\.com/,
  ],
  // ...
});
```

这将把移动事务链接到 Sentry 水falls 视图中的后端跟踪。

---

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 事件未出现在 Sentry | 设置 `debug: true`，检查 Metro/Xcode 控制台中的 SDK 错误；验证 DSN 是否正确 |
| `pod install` 失败 | 运行 `cd ios && pod install --repo-update`；检查 CocoaPods 版本 |
| iOS 构建因 Sentry 脚本失败 | 验证 "Bundle React Native code and images" 脚本是否被替换（而不是追加到） |
| 添加 `sentry.gradle.kts` 后 Android 构建失败 | 确保 `apply from` 行在 `build.gradle` 中的 `android {}` 块之前；使用 `sentry.gradle`（SDK <8.13.0） |
| Android Gradle 8+ 兼容性问题 | 使用 `sentry-android-gradle-plugin` ≥4.0.0；检查 SDK 中的 `sentry.gradle` 版本 |
| 源映射文件未上传 | 验证 `sentry.properties` 具有有效的 `auth.token`；检查构建日志中的 `sentry-cli` 输出 |
| 源映射文件在 Sentry 中未解析 | 确认 `Sentry.init()` 中的 `release` 和 `dist` 与上传的捆绑元元数据匹配 |
| Hermes 源映射文件不工作 | Hermes 发出 `.hbc.map`——Gradle 插件会自动处理；验证 `sentry.gradle` 是否被应用 |
| 会话回放未录制 | 必须使用原生构建（不使用 Expo Go）；确认 `mobileReplayIntegration()` 在 `integrations` 中 |
| 回放显示空白/黑色屏幕 | 检查 `maskAllText`/`maskAllImages` 设置是否与您的隐私要求匹配 |
| 慢速/冻结帧未跟踪 | 设置 `enableNativeFramesTracking: true` 并确认您正在使用原生构建（不使用 Expo Go） |
| TTID / TTFD 未出现 | 需要在原生构建的 `reactNavigationIntegration()` 中设置 `enableTimeToInitialDisplay: true` |
| 添加 Sentry 后应用启动时崩溃 | 可能是原生初始化错误——检查 Xcode/Logcat 日志；尝试 `enableNative: false` 以隔离 |
| Expo SDK 49 或更早版本 | 使用 `sentry-expo`（遗留包）；`@sentry/react-native` 需要 Expo SDK 50+ |
| `isRunningInExpoGo` 导入错误 | 从 `expo` 包导入：`import { isRunningInExpoGo } from "expo"` |
| Xcode 构建期间未找到 Node | 将 `export NODE_BINARY=$(which node)` 添加到 Xcode 构建阶段，或创建符号链接：`ln -s $(which node) /usr/local/bin/node` |
| Expo Go 关于原生功能的警告 | 使用 `isRunningInExpoGo()` 守卫：`enableNativeFramesTracking: !isRunningInExpoGo()` |
| `beforeSend` 未在原生崩溃时触发 | 预期行为——`beforeSend` 仅拦截 JS 层错误；原生崩溃会绕过它 |
| Android 15+（16KB 页大小）崩溃 | 升级到 `@sentry/react-native` ≥6.3.0 |
| 仪表板中事务过多 | 将 `tracesSampleRate` 降低到 `0.1` 或使用 `tracesSampler` 放弃健康检查 |
| `SENTRY_AUTH_TOKEN` 在应用包中暴露 | `SENTRY_AUTH_TOKEN` 仅用于构建时上传——切勿将其传递给 `Sentry.init()` |
| EAS 构建：Sentry 认证令牌缺失 | 将 `SENTRY_AUTH_TOKEN` 作为 EAS 秘密设置：`eas secret:create --name SENTRY_AUTH_TOKEN` |
