[所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > React Native SDK

# Sentry React Native SDK

一个有主见的向导，扫描您的 React Native 或 Expo 项目，并引导您完成完整的 Sentry 设置——错误监控、跟踪、分析、会话回放、日志记录等。

## 何时调用此技能

- 用户询问在 React Native 或 Expo 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 React Native 中进行错误监控、跟踪、分析、会话回放或日志记录
- 用户提到 `@sentry/react-native`、移动错误跟踪或 Sentry for Expo
- 用户希望监控 iOS/Android 上的原生崩溃、ANRs 或应用挂起

> **注意:** 以下 SDK 版本和 API 反映了编写时当前的 Sentry 文档 (`@sentry/react-native` ≥6.0.0，最低推荐 ≥8.0.0)。
> 在实施之前，请始终在 [docs.sentry.io/platforms/react-native/](https://docs.sentry.io/platforms/react-native/) 验证。

---

## 第一阶段：检测

运行这些命令以了解项目，然后再进行任何建议：

```bash
# 检测项目类型和现有的 Sentry
cat package.json | grep -E '"(react-native|expo|@expo|@sentry/react-native|sentry-expo)"'

# 区分 Expo 管理的、无的或纯 React Native
ls app.json app.config.js app.config.ts 2>/dev/null
cat app.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('Expo managed' if 'expo' in d else 'Bare/Vanilla')" 2>/dev/null

# 检查 Expo SDK 版本（重要：Expo SDK 50+ 需要 `@sentry/react-native`）
cat package.json | grep '"expo"'

# 检测导航库
grep -E '"(@react-navigation/native|react-native-navigation)"' package.json

# 检测状态管理（Redux → 可用面包屑集成）
grep -E '"(redux|@reduxjs/toolkit|zustand|mobx)"' package.json

# 检查现有的 Sentry 初始化
grep -r "Sentry.init" src/ app/ App.tsx App.js _layout.tsx 2>/dev/null | head -5

# 检测 Hermes（影响源映射处理）
cat android/app/build.gradle 2>/dev/null | grep -i hermes
cat ios/Podfile 2>/dev/null | grep -i hermes

# 检测 Expo Router
ls app/_layout.tsx app/_layout.js 2>/dev/null

# 检测后端以用于跨链接
ls backend/ server/ api/ 2>/dev/null
find . -maxdepth 3 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" -o -name "package.json" \) 2>/dev/null | grep -v node_modules | head -10
```

**要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `package.json` 中是否有 `expo`？ | Expo 路径（配置插件 + `getSentryExpoConfig`）与无的/纯 React Native 路径 |
| Expo SDK ≥50？ | 直接使用 `@sentry/react-native`；旧版 = `sentry-expo`（遗留，不要使用） |
| `app.json` 是否有 `"expo"` 键？ | 管理的 Expo——向导最简单；配置插件处理所有原生配置 |
| `app/_layout.tsx` 存在？ | Expo Router 项目——初始化放在 `_layout.tsx` 中 |
| `package.json` 中是否已存在 `@sentry/react-native`？ | 跳过安装，跳到功能配置 |
| `@react-navigation/native` 存在？ | 推荐 `reactNavigationIntegration` 用于屏幕跟踪 |
| `react-native-navigation` 存在？ | 推荐 `reactNativeNavigationIntegration`（Wix） |
| 检测到后端目录？ | 触发阶段 4 跨链接 |

---

## 第二阶段：建议

根据您发现的内容提出具体的建议。不要问开放式问题——直接提出建议：

**推荐（核心覆盖——始终设置这些）：**
- ✅ **错误监控**——捕获 JS 异常、原生崩溃（iOS + Android）、ANRs 和应用挂起
- ✅ **跟踪**——移动性能至关重要；自动注入导航、应用启动、网络请求
- ✅ **会话回放**——移动回放捕获屏幕截图和触摸事件以调试用户问题

**可选（增强的可观察性）：**
- ⚡ **分析**——iOS CPU 分析（跨平台 JS 分析）；生产环境中低开销
- ⚡ **日志记录**——通过 `Sentry.logger.*` 进行结构化日志；链接到跟踪以获取完整上下文
- ⚡ **用户反馈**——直接从您的应用收集用户提交的错误报告

**建议逻辑：**

| 功能 | 推荐当... |
|---------|------------------|
| 错误监控 | **始终**——任何移动应用的基线
| 跟踪 | **始终用于移动**——应用启动、导航和网络延迟很重要 |
| 会话回放 | 用户面生产应用；可视化调试用户报告的问题 |
| 分析 | 性能敏感的生产应用 |
| 日志记录 | 应用使用结构化日志，或您希望在 Sentry 中进行日志到跟踪的关联 |
| 用户反馈 | Beta 或面向客户的 应用，您希望收集用户提交的错误报告 |

提出建议：*"对于您的 [Expo 管理的 / 无的] 应用，我建议设置错误监控 + 跟踪 + 会话回放。是否要我还要添加分析和日志记录？"*

---

## 第三阶段：指导

### 确定您的设置路径

| 项目类型 | 推荐设置 | 复杂性 |
|-------------|------------------|------------|
| Expo 管理的（SDK 50+） | 向导 CLI 或使用配置插件的手动操作 | 低——向导做所有事情 |
| Expo 无的（SDK 50+） | 推荐使用向导 CLI | 中等——处理 iOS/Android 配置 |
| 纯 React Native（0.69+） | 推荐使用向导 CLI | 中等——处理 Xcode + Gradle |
| Expo SDK <50 | 使用 `sentry-expo`（遗留） | 参考 [遗留文档](https://docs.sentry.io/platforms/react-native/manual-setup/expo/) |

---

### 路径 A：向导 CLI（推荐用于所有项目类型）

> **您需要自己运行此命令**——向导会打开浏览器进行登录，需要交互输入，代理无法处理。将内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i reactNative
> ```
>
> 它处理登录、组织/项目选择、SDK 安装、原生配置、源映射上传和 `Sentry.init()`。以下是它创建/修改的内容：
>
> | 文件 | 操作 | 目的 |
> |------|--------|---------|
> | `package.json` | 安装 `@sentry/react-native` | 核心 SDK |
> | `metro.config.js` | 添加 `@sentry/react-native/metro` 序列化器 | 源映射生成 |
> | `app.json` | 添加 `@sentry/react-native/expo` 插件（仅限 Expo） | 配置插件用于原生构建 |
> | `App.tsx` / `_layout.tsx` | 添加 `Sentry.init()` 和 `Sentry.wrap()` | SDK 初始化 |
> | `ios/sentry.properties` | 存储组织/项目/令牌 | iOS 源映射 + dSYM 上传 |
> | `android/sentry.properties` | 存储组织/项目/令牌 | Android 源映射上传 |
> | `android/app/build.gradle` | 添加 Sentry Gradle 插件 | Android 源映射 + proguard |
> | `ios/[AppName].xcodeproj` | 包装 "Bundle RN" 构建阶段 + 添加 dSYM 上传 | iOS 符号上传 |
> | `.env.local` | `SENTRY_AUTH_TOKEN` | 认证令牌（添加到 `.gitignore`） |

**一旦完成，请回来并跳到 [验证](#verification)。**

如果用户跳过向导，请根据他们的项目类型继续进行路径 B 或 C（手动设置）。

---

### 路径 B：手动——Expo 管理的

**步骤 1 — 安装**

```bash
npx expo install @sentry/react-native
```

**步骤 2 — `metro.config.js`**

```javascript
const { getSentryExpoConfig } = require("@sentry/react-native/metro");
const config = getSentryExpoConfig(__dirname, {
  // 自动在构建时包装 Expo Router ErrorBoundary 导出（SDK ≥8.17.0）
  autoWrapExpoRouterErrorBoundary: true,
});
module.exports = config;
```

如果 `metro.config.js` 还不存在：
```bash
npx expo customize metro.config.js
# 然后用上面的内容替换
```

**Metro 配置选项：**

| 选项 | 类型 | 默认 | 目的 |
|--------|------|---------|---------|
| `autoWrapExpoRouterErrorBoundary` | `boolean` | `false` | 自动在构建时包装 `export { ErrorBoundary } from 'expo-router'`（SDK ≥8.17.0）。捕获命中每个路由 ErrorBoundary 的错误，而无需手动包装 |
| `annotateReactComponents` | `boolean` | `false` | 注入组件名称以获得更好的错误上下文 |
| `includeWebReplay` | `boolean` | `true` | 包含 Web 回放捆绑包（设置为 `false` 对于仅原生应用） |
| `includeWebFeedback` | `boolean` | `true` | 包含 Web 反馈捆绑包（设置为 `false` 对于仅原生应用） |
| `enableSourceContextInDevelopment` | `boolean` | `true` | 在开发构建中启用源上下文 |

**步骤 3 — `app.json` — 添加 Expo 配置插件**

```json
{
  "expo": {
    "plugins": [
      [
        "@sentry/react-native/expo",
        {
          "url": "https://sentry.io/",
          "project": "YOUR_PROJECT_SLUG",
          "organization": "YOUR_ORG_SLUG",
          "disableAutoUpload": false
        }
      ]
    ]
  }
}
```

> **注意:** 将 `SENTRY_AUTH_TOKEN` 作为环境变量设置用于原生构建——永远不要将其提交到版本控制。

**插件选项：**

| 选项 | 类型 | 默认 | 目的 |
|--------|------|---------|---------|
| `url` | `string` | `"https://sentry.io/"` | Sentry 实例 URL |
| `project` | `string` | — | 项目别名 |
| `organization` | `string` | — | 组织别名 |
| `disableAutoUpload` | `boolean` | `false` | 在本地构建期间跳过源映射 + dSYM 上传（SDK ≥8.13.0） |

**步骤 4 — 初始化 Sentry**

对于 **Expo Router** (`app/_layout.tsx`)：

```typescript
import { Stack } from "expo-router";
import { isRunningInExpoGo } from "expo";
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN ?? "YOUR_SENTRY_DSN",
  sendDefaultPii: true,
  // 跟踪
  tracesSampleRate: 1.0, // 生产中降低到 0.1–0.2
  // 分析
  profilesSampleRate: 1.0,
  // 会话回放
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  // 日志记录（SDK ≥7.0.0）
  enableLogs: true,
  // 会话回放
  integrations: [
    Sentry.mobileReplayIntegration(),
  ],
  enableNativeFramesTracking: !isRunningInExpoGo(), // 慢/冻结帧
  environment: __DEV__ ? "development" : "production",
});

function RootLayout() {
  return <Stack />;
}

export default Sentry.wrap(RootLayout);
```

> **注意:** Expo Router 自动处理导航跟踪。不需要 `Sentry.NavigationContainer` 包装器——导航范围会自动捕获。

**Expo Router ErrorBoundary 设置（SDK ≥8.16.0）**

Expo Router 的每个路由 `ErrorBoundary` 默认情况下会吞噬渲染错误——除非您显式捕获它们。有两种选项：

1. **自动包装（推荐，SDK ≥8.17.0）** — 在 `metro.config.js` 中启用 `autoWrapExpoRouterErrorBoundary: true`（如上所示）。Babel 插件自动重写所有路由文件中的 `export { ErrorBoundary } from 'expo-router'`。

2. **手动包装** — 在每个路由文件中自己包装边界：

   ```typescript
   // app/_layout.tsx（或任何路由文件）
   import { ErrorBoundary as ExpoErrorBoundary } from 'expo-router';
   import * as Sentry from '@sentry/react-native';

   export const ErrorBoundary = Sentry.wrapExpoRouterErrorBoundary(ExpoErrorBoundary);
   ```

这两种方法都会捕获命中边界并带有路由上下文（`route.name`, `route.path`, `route.params`），将活动的导航范围标记为错误，并发出面包屑。具体路径/参数尊重 `sendDefaultPii`。

对于 **标准 Expo** (`App.tsx`)：

```typescript
import { isRunningInExpoGo } from "expo";
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  sendDefaultPii: true,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: __DEV__ ? 1.0 : 0.05,
  release: "my-app@" + Application.nativeApplicationVersion,
  dist: String(Application.nativeBuildVersion),

  // 设置 release 和 dist 以便 Sentry.init() 匹配上传的捆绑包元数据
  debug: __DEV,
});
```

---

### 路径 C：手动——纯 React Native

**步骤 1 — 安装**

```bash
npm install @sentry/react-native --save
cd ios && pod install
```

**步骤 2 — `metro.config.js`**

```javascript
const { getDefaultConfig } = require("@react-native/metro-config");
const { withSentryConfig } = require("@sentry/react-native/metro");

const config = getDefaultConfig(__dirname);
module.exports = withSentryConfig(config, {
  // 设置为 false 以排除 @sentry-internal/replay 从原生捆绑包中（仅限 Web）。
  // includeWebReplay: true,
  // 设置为 false 以排除 @sentry-internal/feedback 从原生捆绑包中（仅限 Web）。
  // includeWebFeedback: true,
  // 自动在构建时包装 Expo Router ErrorBoundary 导出（SDK ≥8.17.0, Expo Router 仅限）
  // autoWrapExpoRouterErrorBoundary: true,
});
```

**步骤 3 — iOS：修改 Xcode 构建阶段**

在 Xcode 中打开 `ios/[AppName].xcodeproj`。找到 **"Bundle React Native code and images"** 构建阶段，并将脚本内容替换为：

```bash
# RN 0.81.1+
set -e
WITH_ENVIRONMENT="../node_modules/react-native/scripts/xcode/with-environment.sh"
SENTRY_XCODE="../node_modules/@sentry/react-native/scripts/sentry-xcode.sh"
/bin/sh -c "$WITH_ENVIRONMENT $SENTRY_XCODE"
```

**步骤 4 — iOS：添加 "Upload Debug Symbols to Sentry" 构建阶段**

在 Xcode 中添加一个新的 **Run Script** 构建阶段（在捆绑阶段之后）：

```bash
/bin/sh ../node_modules/@sentry/react-native/scripts/sentry-xcode-debug-files.sh
```

**步骤 5 — iOS: `ios/sentry.properties`

```properties
defaults.url=https://sentry.io/
defaults.org=YOUR_ORG_SLUG
defaults.project=YOUR_PROJECT_SLUG
auth.token=YOUR_ORG_AUTH_TOKEN
```

**步骤 6 — Android: `android/app/build.gradle`

在 `android {}` 块之前添加：

```groovy
apply from: "../../node_modules/@sentry/react-native/sentry.gradle.kts"
```

> **注意:** SDK ≥8.13.0 使用 `sentry.gradle.kts`（Kotlin DSL）。对于旧版 SDK，使用 `sentry.gradle`（Groovy）。两者都是向后兼容的。

**步骤 7 — Android: `android/sentry.properties`

```properties
defaults.url=https://sentry.io/
defaults.org=YOUR_ORG_SLUG
defaults.project=YOUR_PROJECT_SLUG
auth.token=YOUR_ORG_AUTH_TOKEN
```

**步骤 8 — 初始化 Sentry (`App.tsx` 或入口点)

```typescript
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: "YOUR_DSN",
  sendDefaultPii: true,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  enableLogs: true,
  integrations: [
    Sentry.mobileReplayIntegration(),
  ],
  enableNativeFramesTracking: true,
  environment: __DEV__ ? "development" : "production",
});

function App() {
  return (
    <Sentry.NavigationContainer>
      {/* 您的导航在这里 */}
    </Sentry.NavigationContainer>
  );
}

export default Sentry.wrap(App);
```

---

### 快速参考：完整的 `Sentry.init()` 配置

这是一个推荐的起始配置，所有功能都已启用：

```typescript
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: "YOUR_DSN",
  environment: __DEV__ ? "development" : "production",

  // 跟踪 10–20% 的交易量高的生产环境中
  tracesSampleRate: __DEV__ ? 1.0 : 0.1,

  // 分析所有跟踪的交易量（分析始终是跟踪的子集）
  profilesSampleRate: 1.0,

  // 回放所有错误会话，正常会话采样 5%
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: __DEV__ ? 1.0 : 0.05,

  // 设置 release 和 dist 以便 Sentry.init() 匹配上传的捆绑包元数据
  release: "my-app@" + Application.nativeApplicationVersion,
  dist: String(Application.nativeBuildVersion),

  // 生产设置

  // 设置 release 和 dist 以便 Sentry.init() 匹配上传的捆绑包元数据
  debug: __DEV,
});
```

---

### 源映射和调试符号

源映射和调试符号将 minified 堆栈跟踪转换为可读的跟踪。当设置正确时，Sentry 显示您抛出的确切源代码行。通用认证令牌和 CI 设置位于 [`sentry-source-maps`](../sentry-source-maps/SKILL.md)；React Native 特定的上传机制如下所示。

#### 上传如何工作

| 平台 | 上传的内容 | 上传时间 |
|----------|----------------|------|
| **iOS** (JS) | 源映射 (`.map` 文件) | 在 Xcode 构建期间 |
| **iOS** (原生) | dSYM 捆绑包 | 在 Xcode 归档 / Xcode Cloud 期间 |
| **Android** (JS) | 源映射 + Hermes `.hbc.map` | 在 Gradle 构建期间 |
| **Android** (原生) | Proguard 映射 + NDK `.so` 文件 | 在 Gradle 构建期间 |

#### Expo: 自动上传

`@sentry/react-native/expo` 配置插件自动设置原生构建的上传挂钩。源映射在 `eas build` 和 `expo run:ios/android`（发布）期间上传。

```bash
SENTRY_AUTH_TOKEN=snrys_... npx expo run:ios --configuration Release
```

#### 手动上传（纯 React Native）

如果您需要手动上传源映射：

```bash
npx sentry-cli sourcemaps upload \
  --org YOUR_ORG \
  --project YOUR_PROJECT \
  --release "my-app@1.0.0+1" \
  ./dist
```

---

### EAS 构建挂钩

在 Sentry 中监控您的 Expo 应用服务 (EAS)。SDK 提供三个二进制挂钩——`sentry-eas-build-on-complete`、`sentry-eas-build-on-error` 和 `sentry-eas-build-on-success`——将构建事件捕获为 Sentry 错误或消息。

**步骤 1 — 在 `package.json` 中注册挂钩**

```json
{
  "scripts": {
    "eas-build-on-complete": "sentry-eas-build-on-complete"
  }
}
```

使用 `eas-build-on-complete` 将失败和（可选的）成功捕获到一个挂钩中。如果您想要独立的控制，可以使用 `eas-build-on-error` 或 `eas-build-on-success` 单独使用。

**步骤 2 — 在您的 EAS 秘密中设置 `SENTRY_DSN`

```bash
eas secret:create --name SENTRY_DSN --value "https://...@sentry.io/..."
```

挂钩从构建环境读取 `SENTRY_DSN`——它不会共享与应用相同的 `.env`。

**可选环境变量：**

| 变量 | 目的 |
|----------|---------|
| `SENTRY_EAS_BUILD_CAPTURE_SUCCESS` | 设置 `true` 以捕获成功构建（默认仅错误） |
| `SENTRY_EAS_BUILD_TAGS` | 额外标签的 JSON 对象，例如 `{"team":"mobile","channel":"production"` |
| `SENTRY_EAS_BUILD_ERROR_MESSAGE` | 失败构建的自定义错误消息 |
| `SENTRY_EAS_BUILD_SUCCESS_MESSAGE` | 成功构建的自定义消息 |

> **工作原理:** 挂钩是 EAS 的 [npm 生命周期挂钩](https://docs.expo.dev/build-reference/npm-hooks/)。EAS 在构建过程结束时调用匹配 `eas-build-on-*` 的 `package.json` 脚本。脚本从 `@expo/env`、`.env` 或 `.env.sentry-build-plugin` 读取环境，而不会覆盖环境中的 EAS 秘密。

---

## 验证

设置后，测试 Sentry 是否接收事件：

```typescript
// 快速测试——抛出并 Sentry.wrap(App) 捕获它
<Button
  title="测试 Sentry 错误"
  onPress={() => {
    throw new Error("我的第一个 Sentry 错误！");
  }}
/>

或者手动捕获

<Button
  title="测试 Sentry 消息"
  onPress={() => {
    Sentry.captureMessage("Sentry 测试消息", "info");
  }}
/>
```

**检查 Sentry 仪表板：**
- **问题** → 您的测试错误应在几秒钟内出现
- **跟踪** → 查找带有 "main" 事务和子范围的跟踪
- **回放** → 会话记录在应用交互后可见（仅限原生构建——Expo Go 不适用）
- **日志** → 结构化日志条目如果 `enableLogs: true`

> ⚠️ **Expo Go 限制：** 原生崩溃、会话回放、慢/冻结帧、TTID 和 TTFD 仅在原生构建中工作（`eas build` 或 `expo run`）。Expo Go 运行在纯 JS 模式下。设置 `enableNativeFramesTracking: !isRunningInExpoGo()` 以避免警告。

如果什么都没有出现：
1. 设置 `debug: true`——SDK 日志记录到 Metro 控制台
2. 验证 DSN 是正确的，Sentry 项目是否存在
3. 确保 `Sentry.wrap(App)` 已应用于根组件
4. 对于原生崩溃，构建一个发布构建（调试模式下崩溃可能不会转发）

---

## 第四阶段：跨链接

完成 React Native 设置后，检查是否有缺少 Sentry 覆盖的后端或 Web 前端：

```bash
# 相邻的后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -3
cat ../Gemfile 2>/dev/null | head -3
ls ../backend/package.json ../server/package.json 2>/dev/null

# Web 前端在相同或兄弟存储库中
ls ../web ../frontend ../dashboard 2>/dev/null
cat ../web/package.json ../frontend/package.json 2>/dev/null | grep -E '"react"|"svelte"|"next"'
```

如果存在没有 Sentry 的后端或 Web 前端，建议匹配的技能：

| 检测到 | 建议技能 |
|----------|--------------|
| Go 后端 (`go.mod`) | `sentry-go-sdk` |
| Python 后端 (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby 后端 (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js 后端 (Express, Fastify 等) | `@sentry/node`——请参阅 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |
| React / Next.js Web | `sentry-react-sdk` |
| Svelte / SvelteKit Web | `sentry-svelte-sdk` |

**分布式跟踪设置**——如果添加了后端技能，请配置 React Native 中的 `tracePropagationTargets` 以将跟踪上下文传播到您的 API：

```typescript
Sentry.init({
  tracePropagationTargets: [
    "localhost",
    /^https:\/\/api\.yourapp\.com/,
  ],
  // ...
});
```

这将移动移动事务到 Sentry 水falls 视图中与后端跟踪链接。

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 事件未出现在 Sentry 中 | 设置 `debug: true`，检查 Metro/Xcode 控制台中的 SDK 错误；验证 DSN 是正确的 |
| `pod install` 失败 | 运行 `cd ios && pod install --repo-update`；检查 CocoaPods 版本 |
| iOS 构建失败，Sentry 脚本 | 验证 "Bundle React Native code and images" 脚本是否被替换（而不是附加到） |
| Android 构建在添加 `sentry.gradle.kts` 后失败 | 确保 `apply from` 行在 `android {}` 块之前；使用 `sentry.gradle` 对于 SDK <8.13.0 |
| Android Gradle 8+ 兼容性问题 | 使用 `sentry-android-gradle-plugin` ≥4.0.0；检查 `sentry.gradle` 中 SDK 版本 |
| 源映射未上传 | 验证 `sentry.properties` 是否有有效的 `auth.token`；检查构建日志中的 `sentry-cli` 输出 |
| 源映射在 Sentry 中无法解析 | 确认 `release` 和 `dist` 在 `Sentry.init()` 中与上传的捆绑包元数据匹配 |
| Hermes 源映射不工作 | Hermes 发出 `.hbc.map`——Gradle 插件自动处理；验证 `sentry.gradle` 是否已应用 |
| 会话回放未记录 | 必须使用原生构建（不适用于 Expo Go）；确认 `mobileReplayIntegration()` 在 `integrations` 中 |
| 回放显示空白/黑色屏幕 | 检查 `maskAllText`/`maskAllImages` 设置是否与您的隐私要求匹配 |
| 慢/冻结帧未跟踪 | 设置 `enableNativeFramesTracking: true` 并确认您处于原生构建中（不适用于 Expo Go） |
| TTID / TTFD 未出现 | 需要在原生构建上的 `reactNavigationIntegration()` 中设置 `enableTimeToInitialDisplay: true` |
| 应用在添加 Sentry 后启动崩溃 | 很可能是原生初始化错误——检查 Xcode/Logcat 日志；尝试 `enableNative: false` 以隔离 |
| Expo SDK 49 或更旧 | 使用 `sentry-expo`（遗留包）；`@sentry/react-native` 需要 Expo SDK 50+ |
| `isRunningInExpoGo` 导入错误 | 从 `expo` 包导入：`import { isRunningInExpoGo } from "expo"` |
| Node 未在 Xcode 构建期间找到 | 在 Xcode 构建阶段添加 `export NODE_BINARY=$(which node)`；或者创建符号链接：`ln -s $(which node) /usr/local/bin/node` |
| Expo Go 警告原生功能 | 使用 `isRunningInExpoGo()` 守卫：`enableNativeFramesTracking: !isRunningInExpoGo()` |
| `beforeSend` 对于原生崩溃未触发 | 预期——`beforeSend` 仅拦截 JS 层级错误；原生崩溃会绕过它 |
| Android 15+ (16KB 页面大小) 崩溃 | 升级到 `@sentry/react-native` ≥6.3.0 |
| 仪表板中事务过多 | 将 `tracesSampleRate` 降低到 `0.1` 或使用 `tracesSampler` 放弃健康检查 |
| `SENTRY_AUTH_TOKEN` 在应用捆绑包中暴露 | `SENTRY_AUTH_TOKEN` 仅用于构建时上传——永远不要将其传递给 `Sentry.init()` |
| EAS 构建中 Sentry 认证令牌丢失 | 将 `SENTRY_AUTH_TOKEN` 作为 EAS 秘密设置：`eas secret:create --name SENTRY_AUTH_TOKEN` |
