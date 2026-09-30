---
name: sentry-android-sdk
description: 完整的 Android Sentry SDK 配置。当被要求“为 Android 添加 Sentry”、“安装 sentry-android”、“在 Android 中配置 Sentry”或为 Android 应用程序配置错误监控、跟踪、性能分析、会话回放或日志记录时使用。支持 Kotlin 和 Java 代码库。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-install/SKILL.md) > Android SDK

# Sentry Android SDK

一个有主见的向导，它会扫描您的 Android 项目并指导您完成 Sentry 的完整设置——错误监控、追踪、性能分析、会话回放、日志记录等。

## 何时调用此技能

- 用户询问在 Android 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Android 中进行错误监控、崩溃报告、ANR 检测、追踪、性能分析、会话回放或日志记录
- 用户提到 `sentry-android`、`io.sentry:sentry-android`、移动崩溃跟踪或 Sentry for Kotlin/Java Android
- 用户希望监控原生（NDK）崩溃、应用程序无响应（ANR）事件或应用启动性能

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的当前状态（`io.sentry:sentry-android:8.33.0`，Gradle 插件 `6.1.0`）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/android/](https://docs.sentry.io/platforms/android/) 进行验证。

---

## 第一阶段：检测

在做出任何建议之前，运行这些命令以了解项目：

```bash
# 检测项目结构和构建系统
ls build.gradle build.gradle.kts settings.gradle settings.gradle.kts 2>/dev/null

# 检查 AGP 版本和现有的 Sentry
grep -r '"com.android.application"' build.gradle* app/build.gradle* 2>/dev/null | head -3
grep -ri sentry build.gradle* app/build.gradle* 2>/dev/null | head -10

# 检查应用级别的构建文件（Groovy vs KTS）
ls app/build.gradle app/build.gradle.kts 2>/dev/null

# 检测 Gradle 版本目录（libs.versions.toml）—— 现代 AGP 项目
ls gradle/libs.versions.toml 2>/dev/null

# 检查版本目录中现有的 Sentry 条目
grep -iE 'sentry|io\.sentry' gradle/libs.versions.toml 2>/dev/null | head -10

# 检查构建文件是否引用目录（alias/libs.* 使用）
grep -E 'alias\(libs\.|libs\.[a-zA-Z]' build.gradle build.gradle.kts app/build.gradle app/build.gradle.kts 2>/dev/null | head -5

# 检测 Kotlin vs Java
find app/src/main -name "*.kt" 2>/dev/null | head -3
find app/src/main -name "*.java" 2>/dev/null | head -3

# 检查 minSdk, targetSdk
grep -E 'minSdk|targetSdk|compileSdk|minSdkVersion|targetSdkVersion' app/build.gradle app/build.gradle.kts 2>/dev/null | head -6

# 检测 Jetpack Compose
grep -E 'compose|androidx.compose' app/build.gradle app/build.gradle.kts 2>/dev/null | head -5

# 检测 OkHttp（流行的 HTTP 客户端——有专门的集成）
grep -E 'okhttp|retrofit' app/build.gradle app/build.gradle.kts 2>/dev/null | head -3

# 检测 Room 或 SQLite
grep -E 'androidx.room|androidx.sqlite' app/build.gradle app/build.gradle.kts 2>/dev/null | head -3

# 检测 Timber（日志库）
grep -E 'timber' app/build.gradle app/build.gradle.kts 2>/dev/null | head -3

# 检测 Jetpack Navigation
grep -E 'androidx.navigation' app/build.gradle app/build.gradle.kts 2>/dev/null | head -3

# 检测 Apollo（GraphQL）
grep -E 'apollo' app/build.gradle app/build.gradle.kts 2>/dev/null | head -3

# 检查现有的 Sentry 初始化
grep -r "SentryAndroid.init\|io.sentry.Sentry" app/src/ 2>/dev/null | head -5

# 检查 Application 类
find app/src/main -name "*.kt" -o -name "*.java" 2>/dev/null | xargs grep -l "Application()" 2>/dev/null | head -3

# 相邻的后端（用于交叉链接）
ls ../backend ../server ../api 2>/dev/null
find .. -maxdepth 2 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" \) 2>/dev/null | grep -v node_modules | head -5
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `build.gradle.kts` 存在？ | 在所有示例中使用 Kotlin DSL 语法 |
| `gradle/libs.versions.toml` 存在？ | 将 Sentry 添加到版本目录；在构建文件中通过 `libs.*` 引用 |
| 目录中已经存在 `sentry` 条目？ | 重用现有的版本引用；不要重复或硬编码版本 |
| `minSdk < 26`？ | 注意会话回放需要 API 26+——低于此版本时为静默无操作 |
| 检测到 Compose？ | 推荐 `sentry-compose-android` 和 Compose 特定的掩码 |
| 存在 OkHttp？ | 推荐 `sentry-okhttp` 拦截器或 Gradle 插件字节码自动注入 |
| 存在 Room/SQLite？ | 推荐 `sentry-android-sqlite` 或插件字节码注入 |
| 存在 Timber？ | 推荐 `sentry-android-timber` 集成 |
| 存在 Jetpack Navigation？ | 推荐 `sentry-android-navigation` 用于屏幕跟踪 |
| 已经存在 `SentryAndroid.init()`？ | 跳过安装，跳转到功能配置 |

---

## 第二阶段：推荐

根据您发现的内容，提出一个具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖——始终设置这些）：**
- ✅ **错误监控** — 自动捕获未捕获的异常、ANRs 和原生 NDK 崩溃
- ✅ **追踪** — 自动注入 Activity 生命周期、应用启动、HTTP 请求和数据库查询
- ✅ **会话回放** — 记录屏幕捕获和用户交互以进行调试（API 26+）

**可选（增强的可观察性）：**
- ⚡ **性能分析** — 连续 UI 性能分析（推荐）或基于事务的采样
- ⚡ **日志记录** — 通过 `Sentry.logger()` 结构化日志，可选 Timber 桥接
- ⚡ **用户反馈** — 从应用内部收集用户提交的 Bug 报告

**推荐逻辑：**

| 功能 | 当满足以下条件时推荐... |
|---------|------------------|
| 错误监控 | **始终** — 任何 Android 应用的非协商性基线 |
| 追踪 | **始终用于 Android** — 应用启动时间、Activity 生命周期、网络延迟很重要 |
| 会话回放 | 生产环境中的面向用户的应用（API 26+）；用户问题的视觉调试 |
| 性能分析 | 性能敏感的应用、启动时间调查、生产性能分析 |
| 日志记录 | 应用使用结构化日志记录或您希望在 Sentry 中进行日志到追踪的关联 |
| 用户反馈 | Beta 或面向客户的应用，您希望收集用户提交的 Bug 报告 |

建议：*"对于您的 [Kotlin / Java] Android 应用（minSdk X），我建议设置错误监控 + 追踪 + 会话回放。是否还需要我添加性能分析和日志记录？*"

---

## 第三阶段：指导

### 确定您的设置路径

| 项目类型 | 推荐设置 | 复杂性 |
|-------------|------------------|------------|
| 新项目，没有现有的 Sentry | Gradle 插件（推荐） | 低——插件处理大多数配置 |
| 现有项目，没有 Sentry | Gradle 插件或手动初始化 | 中——添加依赖项 + Application 类 |
| 手动完全控制 | 在 Application 中 `SentryAndroid.init()` | 中——显式配置，最灵活 |

### 选项 1：向导（推荐）

> **您需要自己运行**——向导会打开浏览器进行登录，并需要交互式输入，代理无法处理。
> 将以下内容复制粘贴到您的终端：
>
> ```
> npx @sentry/wizard@latest -i android
> ```
>
> 它处理登录、组织/项目选择、Gradle 插件设置、依赖项安装、DSN 配置和 ProGuard/R8 映射上传。
>
> **完成后，回来并跳转到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的“选项 2：手动设置”。

---

### 选项 2：手动设置

#### 使用 Gradle 版本目录 (`gradle/libs.versions.toml`)

如果第一阶段检测到 `gradle/libs.versions.toml`，请首先将 Sentry 添加到目录中，然后从您的构建文件中引用它。这可以保持版本集中化，并符合现代 AGP 项目的规范。

**步骤 1 — 将条目添加到 `gradle/libs.versions.toml`**

```toml
[versions]
sentry = "8.33.0"
sentryGradlePlugin = "6.1.0"

[libraries]
sentry-android = { module = "io.sentry:sentry-android", version.ref = "sentry" }
sentry-bom = { module = "io.sentry:sentry-bom", version.ref = "sentry" }
# 可选集成——仅添加您的项目使用的那些：
sentry-android-timber = { module = "io.sentry:sentry-android-timber" }
sentry-android-fragment = { module = "io.sentry:sentry-android-fragment" }
sentry-compose-android = { module = "io.sentry:sentry-compose-android" }
sentry-android-navigation = { module = "io.sentry:sentry-android-navigation" }
sentry-okhttp = { module = "io.sentry:sentry-okhttp" }
sentry-android-sqlite = { module = "io.sentry:sentry-android-sqlite" }
sentry-kotlin-extensions = { module = "io.sentry:sentry-kotlin-extensions" }

[plugins]
sentry-android-gradle = { id = "io.sentry.android.gradle", version.ref = "sentryGradlePlugin" }
```

> **注意：** 可选集成条目省略了 `version.ref`——它们的版本在解析时来自 BOM。只有 `sentry-bom` 需要版本引用。
> 如果目录已经定义了 `sentry` 版本，请重用它而不是添加重复的条目。

**步骤 2 — 从 `build.gradle[.kts]` 引用目录**

项目级别的 `build.gradle.kts`:
```kotlin
plugins {
    alias(libs.plugins.sentry.android.gradle) apply false
}
```

应用级别的 `app/build.gradle.kts`:
```kotlin
plugins {
    id("com.android.application")
    alias(libs.plugins.sentry.android.gradle)
}

dependencies {
    implementation(platform(libs.sentry.bom))
    implementation(libs.sentry.android)
    // implementation(libs.sentry.okhttp)
    // implementation(libs.sentry.compose.android)
}
```

Groovy DSL (`app/build.gradle`) 等效：
```groovy
plugins {
    id "com.android.application"
    alias libs.plugins.sentry.android.gradle
}

dependencies {
    implementation platform(libs.sentry.bom)
    implementation libs.sentry.android
}
```

然后继续使用来自下面的“路径 A，步骤 2”的 `sentry {}` 配置块。设置的其他部分（Application 类初始化、清单注册、验证）是相同的。

---

#### 路径 A：Gradle 插件（推荐）

Sentry Gradle 插件是最简单的设置路径。它：
- 在发布构建时自动上传 ProGuard/R8 映射文件
- 将源上下文注入堆栈帧
- 可选地通过字节码转换注入 OkHttp、Room/SQLite、文件 I/O、Compose 导航和 `android.util.Log`（无需修改源代码）

**步骤 1 — 将插件添加到 `build.gradle[.kts]`（项目级别）**

Groovy DSL (`build.gradle`):
```groovy
plugins {
    id "io.sentry.android.gradle" version "6.1.0" apply false
}
```

Kotlin DSL (`build.gradle.kts`):
```kotlin
plugins {
    id("io.sentry.android.gradle") version "6.1.0" apply false
}
```

**步骤 2 — 在 `app/build.gradle[.kts]` 中应用插件 + 添加依赖项**

Groovy DSL:
```groovy
plugins {
    id "com.android.application"
    id "io.sentry.android.gradle"
}

android {
    // ...
}

dependencies {
    // 使用 BOM 以确保 Sentry 模块之间的一致版本
    implementation platform("io.sentry:sentry-bom:8.33.0")
    implementation "io.sentry:sentry-android"

    // 可选集成（添加相关的）：
    // implementation "io.sentry:sentry-android-timber"     // Timber 桥接
    // implementation "io.sentry:sentry-android-fragment"   // Fragment 生命周期跟踪
    // implementation "io.sentry:sentry-compose-android"    // Jetpack Compose 支持
    // implementation "io.sentry:sentry-android-navigation"  // Jetpack Navigation
    // implementation "io.sentry:sentry-okhttp"             // OkHttp 拦截器
    // implementation "io.sentry:sentry-android-sqlite"     // Room/SQLite 跟踪
    // implementation "io.sentry:sentry-kotlin-extensions"  // 协程上下文传播
}

sentry {
    org = "YOUR_ORG_SLUG"
    projectName = "YOUR_PROJECT_SLUG"
    authToken = System.getenv("SENTRY_AUTH_TOKEN")

    // 通过字节码转换启用自动注入（无需修改源代码）
    tracingInstrumentation {
        enabled = true
        features = [InstrumentationFeature.DATABASE, InstrumentationFeature.FILE_IO,
                    InstrumentationFeature.OKHTTP, InstrumentationFeature.COMPOSE]
    }

    // 在发布时上传 ProGuard 映射和源上下文
    autoUploadProguardMapping = true
    includeSourceContext = true
}
```

Kotlin DSL (`app/build.gradle.kts`):
```kotlin
plugins {
    id("com.android.application")
    id("io.sentry.android.gradle")
}

dependencies {
    implementation(platform("io.sentry:sentry-bom:8.33.0"))
    implementation("io.sentry:sentry-android")

    // 可选集成：
    // implementation("io.sentry:sentry-android-timber")
    // implementation("io.sentry:sentry-android-fragment")
    // implementation("io.sentry:sentry-compose-android")
    // implementation("io.sentry:sentry-android-navigation")
    // implementation("io.sentry:sentry-okhttp")
    // implementation("io.sentry:sentry-android-sqlite")
    // implementation("io.sentry:sentry-kotlin-extensions")
}

sentry {
    org = "YOUR_ORG_SLUG"
    projectName = "YOUR_PROJECT_SLUG"
    authToken = System.getenv("SENTRY_AUTH_TOKEN")

    tracingInstrumentation {
        enabled = true
        features = setOf(
            InstrumentationFeature.DATABASE,
            InstrumentationFeature.FILE_IO,
            InstrumentationFeature.OKHTTP,
            InstrumentationFeature.COMPOSE,
        )
    }

    autoUploadProguardMapping = true
    includeSourceContext = true
}
```

**步骤 3 — 在您的 Application 类中初始化 Sentry**

如果您没有 Application 子类，请创建一个：

```kotlin
// MyApplication.kt
import android.app.Application
import io.sentry.SentryLevel
import io.sentry.android.core.SentryAndroid
import io.sentry.android.replay.SentryReplayOptions

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        SentryAndroid.init(this) { options ->
            options.dsn = "YOUR_SENTRY_DSN"

            // 追踪——将采样率降低到 0.1–0.2 在高流量的生产环境中
            options.tracesSampleRate = 1.0

            // 性能分析——使用连续 UI 性能分析（推荐，SDK ≥ 8.7.0）
            options.profileSessionSampleRate = 1.0

            // 会话回放（仅限 API 26+；低于 API 26 时为静默无操作）
            options.sessionReplay.sessionSampleRate = 0.1    // 所有会话的 10%
            options.sessionReplay.onErrorSampleRate = 1.0    // 错误的 100%

            // 结构化日志记录
            options.logs.isEnabled = true

            // 环境
            options.environment = BuildConfig.BUILD_TYPE
        }
    }
}
```

Java 等效：
```java
// MyApplication.java
import android.app.Application;
import io.sentry.android.core.SentryAndroid;

public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();

        SentryAndroid.init(this, options -> {
            options.setDsn("YOUR_SENTRY_DSN");
            options.setTracesSampleRate(1.0);
            options.setProfileSessionSampleRate(1.0);
            options.getSessionReplay().setSessionSampleRate(0.1);
            options.getSessionReplay().setOnErrorSampleRate(1.0);
            options.getLogs().setEnabled(true);
            options.setEnvironment(BuildConfig.BUILD_TYPE);
        });
    }
}
```

**步骤 4 — 在 `AndroidManifest.xml` 中注册 Application**

```xml
<application
    android:name=".MyApplication"
    ... >
```

---

#### 路径 B：手动设置（不使用 Gradle 插件）

如果您无法使用 Gradle 插件（例如，非标准的构建设置），请使用此方法。

**步骤 1 — 在 `app/build.gradle[.kts]` 中添加依赖项**

```kotlin
dependencies {
    implementation(platform("io.sentry:sentry-bom:8.33.0"))
    implementation("io.sentry:sentry-android")
}
```

**步骤 2 — 在 Application 类中初始化**（与路径 A，步骤 3 相同）

**步骤 3 — 手动配置 ProGuard/R8**

Sentry SDK 随附一个 ProGuard 规则文件。对于手动映射上传，安装 `sentry-cli` 并将其添加到您的 CI：

```bash
sentry-cli releases files "my-app@1.0.0+42" upload-proguard \
  --org YOUR_ORG --project YOUR_PROJECT \
  app/build/outputs/mapping/release/mapping.txt
```

---

### 快速参考：全功能的 `SentryAndroid.init()`

```kotlin
SentryAndroid.init(this) { options ->
    options.dsn = "YOUR_SENTRY_DSN"

    // 环境和发布版本
    options.environment = BuildConfig.BUILD_TYPE     // "debug", "release", 等
    options.release = "${BuildConfig.APPLICATION_ID}@${BuildConfig.VERSION_NAME}+${BuildConfig.VERSION_CODE}"

    // 跟踪 — 开发环境中100%采样，生产环境中降低到10-20%
    options.tracesSampleRate = 1.0

    // 持续UI性能分析（推荐使用基于事务的性能分析）
    options.profileSessionSampleRate = 1.0

    // 会话回放（API 26+；API 21-25时为静默无操作）
    options.sessionReplay.sessionSampleRate = 0.1
    options.sessionReplay.onErrorSampleRate = 1.0
    options.sessionReplay.maskAllText = true         // 用于隐私保护，遮罩文本
    options.sessionReplay.maskAllImages = true       // 用于隐私保护，遮罩图片

    // 结构化日志记录
    options.logs.isEnabled = true

    // 错误增强
    options.isAttachScreenshot = true                // 错误时捕获屏幕截图
    options.isAttachViewHierarchy = true             // 附加视图层级JSON

    // ANR检测（默认5秒；API 30+的看门狗+ApplicationExitInfo API）
    options.isAnrEnabled = true

    // NDK原生崩溃处理（默认启用）
    options.isEnableNdk = true

    // 发送PII：IP地址、用户数据
    options.sendDefaultPii = true

    // 跟踪传播（后端分布式跟踪）
    options.tracePropagationTargets = listOf("api.yourapp.com", ".*\\.yourapp\\.com")

    // 调试日志记录 — 生产环境中禁用
    options.isDebug = BuildConfig.DEBUG
}
```

---

### 每个已同意的功能

逐个处理功能。加载每个功能的参考文件，按照其步骤操作，然后验证后再继续：

| 功能 | 参考文件 | 加载时机 |
|------|----------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基准） |
| 跟踪与性能 | `${SKILL_ROOT}/references/tracing.md` | 始终用于Android（Activity生命周期、网络） |
| 性能分析 | `${SKILL_ROOT}/references/profiling.md` | 性能敏感的生产应用 |
| 会话回放 | `${SKILL_ROOT}/references/session-replay.md` | 面向用户的应用（API 26+） |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志记录/日志与跟踪关联 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 自定义指标跟踪（SDK ≥ 8.30.0） |
| 定时任务 | `${SKILL_ROOT}/references/crons.md` | 定时任务、WorkManager检查 |
| 集成参考 | `${SKILL_ROOT}/references/integrations.md` | 内置、可选和Gradle字节码集成 |

每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确遵循步骤，验证其是否正常工作。

---

## 配置参考

### 核心的 `SentryOptions`（通过 `SentryAndroid.init`）

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | `String` | — | **必需。** 项目DSN；如果为空，SDK将静默禁用 |
| `environment` | `String` | — | 例如，`"production"`，`"staging"`。环境：`SENTRY_ENVIRONMENT` |
| `release` | `String` | — | 应用版本，例如，`"my-app@1.0.0+42"`。环境：`SENTRY_RELEASE` |
| `dist` | `String` | — | 构建变体/分发标识符 |
| `sendDefaultPii` | `Boolean` | `false` | 包含PII：IP地址、用户数据 |
| `sampleRate` | `Double` | `1.0` | 错误事件采样（0.0–1.0） |
| `maxBreadcrumbs` | `Int` | `100` | 每个事件的最大面包屑数 |
| `isAttachStacktrace` | `Boolean` | `true` | 自动将堆栈跟踪附加到消息事件 |
| `isAttachScreenshot` | `Boolean` | `false` | 错误时捕获屏幕截图 |
| `isAttachViewHierarchy` | `Boolean` | `false` | 附加JSON视图层级作为附件 |
| `isDebug` | `Boolean` | `false` | SDK的调试输出。**在生产环境中绝对禁用** |
| `isEnabled` | `Boolean` | `true` | 完全禁用SDK（例如，用于测试） |
| `beforeSend` | `SentryOptions.BeforeSendCallback` | — | 在发送前修改或丢弃错误事件 |
| `beforeBreadcrumb` | `SentryOptions.BeforeBreadcrumbCallback` | — | 在存储前过滤面包屑 |

### 跟踪选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `tracesSampleRate` | `Double` | `0.0` | 事务采样率（0–1）。开发环境中使用 `1.0` |
| `tracesSampler` | `TracesSamplerCallback` | — | 每个事务采样；覆盖 `tracesSampleRate` |
| `tracePropagationTargets` | `List<String>` | `[".*"]` | 接收 `sentry-trace` 和 `baggage` 头的主机/URL |
| `isEnableAutoActivityLifecycleTracing` | `Boolean` | `true` | 自动记录Activity生命周期 |
| `isEnableTimeToFullDisplayTracing` | `Boolean` | `false` | TTFD跨度（需要 `Sentry.reportFullyDisplayed()`） |
| `isEnableUserInteractionTracing` | `Boolean` | `false` | 自动将用户手势作为事务记录 |

### 性能分析选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `profileSessionSampleRate` | `Double` | `0.0` | 持续性能分析采样率（SDK ≥ 8.7.0，API 22+） |
| `profilesSampleRate` | `Double` | `0.0` | 传统事务性能分析率（与持续模式互斥） |
| `isProfilingStartOnAppStart` | `Boolean` | `false` | 应用启动时自动开始性能分析会话 |

### ANR选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `isAnrEnabled` | `Boolean` | `true` | 启用ANR看门狗线程 |
| `anrTimeoutIntervalMillis` | `Long` | `5000` | 报告ANR前的毫秒数 |
| `isAnrReportInDebug` | `Boolean` | `false` | 在调试构建中报告ANR（调试器中噪音较大） |

### NDK选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `isEnableNdk` | `Boolean` | `true` | 通过sentry-native启用原生崩溃捕获 |
| `isEnableScopeSync` | `Boolean` | `true` | 将Java作用域（用户、标签）同步到NDK层 |
| `isEnableTombstoneFetchJob` | `Boolean` | `true` | 检索NDK墓碑文件以进行增强 |

### 会话回放选项 (`options.sessionReplay`)

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `sessionSampleRate` | `Double` | `0.0` | 记录所有会话的分数 |
| `onErrorSampleRate` | `Double` | `0.0` | 记录错误会话的分数 |
| `maskAllText` | `Boolean` | `true` | 回放中遮罩所有文本 |
| `maskAllImages` | `Boolean` | `true` | 回放中遮罩所有图片 |
| `quality` | `SentryReplayQuality` | `MEDIUM` | 视频质量：`LOW`，`MEDIUM`，`HIGH` |

### 日志记录选项 (`options.logs`)

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `isEnabled` | `Boolean` | `false` | 启用 `Sentry.logger()` API（SDK ≥ 8.12.0） |
| `setBeforeSend` | `BeforeSendLogCallback` | — | 在发送前过滤/修改日志条目 |

### 环境变量

| 变量 | 目的 | 备注 |
|------|------|------|
| `SENTRY_DSN` | 数据源名称 | 在CI中设置；SDK在初始化时从环境读取 |
| `SENTRY_AUTH_TOKEN` | 上传ProGuard映射和源上下文 | **绝对不要提交 — 使用CI/CD密钥** |
| `SENTRY_ORG` | 组织缩写 | Gradle插件 `sentry.org` 使用 |
| `SENTRY_PROJECT` | 项目缩写 | Gradle插件 `sentry.projectName` 使用 |
| `SENTRY_RELEASE` | 发布标识符 | 从 `options.release` 回退 |
| `SENTRY_ENVIRONMENT` | 环境名称 | 从 `options.environment` 回退 |

您也可以通过 `AndroidManifest.xml` 元数据配置DSN和许多选项：

```xml
<application>
    <meta-data android:name="io.sentry.dsn" android:value="YOUR_DSN" />
    <meta-data android:name="io.sentry.traces-sample-rate" android:value="1.0" />
    <meta-data android:name="io.sentry.environment" android:value="production" />
    <meta-data android:name="io.sentry.anr.enable" android:value="true" />
    <meta-data android:name="io.sentry.attach-screenshot" android:value="true" />
    <meta-data android:name="io.sentry.attach-view-hierarchy" android:value="true" />
</application>
```

> ⚠️ Manifest元数据是一种便捷的替代方案，但**不支持完整的选项集**。对于复杂的配置（会话回放、性能分析、钩子），请使用 `SentryAndroid.init()`。

---

## 验证

配置完成后，验证Sentry是否接收事件：

**测试错误捕获：**
```kotlin
// 在Activity或Fragment中
try {
    throw RuntimeException("Sentry Android SDK测试")
} catch (e: Exception) {
    Sentry.captureException(e)
}
```

**测试跟踪：**
```kotlin
val transaction = Sentry.startTransaction("test-task", "task")
val span = transaction.startChild("test-span", "描述")
span.finish()
transaction.finish()
```

**测试结构化日志记录（SDK ≥ 8.12.0）：**
```kotlin
Sentry.logger().info("Sentry日志测试")
Sentry.logger().error("错误日志测试", Exception("测试错误"))
```

**检查Sentry控制台：**
- **问题** → 您的测试异常应在几秒钟内出现
- **跟踪** → 查找 `test-task` 事务及其子跨度
- **回放** → 应用交互后可见会话录制（需要API 26+）
- **日志** → 结构化日志条目在日志选项卡下可见

如果未出现任何内容：
1. 设置 `options.isDebug = true` — SDK将输出到Logcat
2. 验证DSN是否正确且与您的Sentry项目匹配
3. 确认您的 `Application` 类已在 `AndroidManifest.xml` 中注册为 `android:name`
4. 确认设备/模拟器具有互联网连接
5. 对于NDK崩溃，确保 `isEnableNdk = true`（默认）且项目在 `android.ndkVersion` 中配置了NDK

---

## 交叉链接

完成Android配置后，检查是否存在缺少Sentry覆盖的后端或Web前端：

```bash
# 相邻的后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -5
cat ../Gemfile 2>/dev/null | head -3
ls ../backend/package.json ../server/package.json 2>/dev/null

# iOS对应的应用
ls ../ios ../YourApp-iOS 2>/dev/null
find .. -maxdepth 3 -name "*.xcodeproj" 2>/dev/null | head -3
```

如果存在缺少Sentry的后端或相关平台，建议匹配的技能：

| 检测到 | 建议技能 |
|------|--------|
| Go后端 (`go.mod`) | `sentry-go-sdk` |
| Python后端 (`requirements.txt`，`pyproject.toml`) | `sentry-python-sdk` |
| Ruby后端 (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js后端 | `@sentry/node` — 查看文档.sentry.io/platforms/javascript/guides/express/ |
| iOS应用（`.xcodeproj`） | `sentry-cocoa-sdk` |
| React Native (`package.json` 包含 `react-native`) | `sentry-react-native-sdk` |
| React / Next.js Web | `sentry-react-sdk` 或 `sentry-nextjs-sdk` |

**分布式跟踪设置** — 如果添加了后端技能，请在Android中配置 `tracePropagationTargets` 以将跟踪上下文传播到您的API：

```kotlin
options.tracePropagationTargets = listOf(
    "api.yourapp.com",
    ".*\\.yourapp\\.com"
)
```

这将把移动事务与Sentry瀑布视图中的后端跟踪链接起来。

---

## 故障排除

| 问题 | 解决方案 |
|------|--------|
| 事件未出现在Sentry | 设置 `isDebug = true`，检查Logcat中的SDK错误；验证DSN是否正确且与您的项目匹配 |
| `SentryAndroid.init()` 未被调用 | 确认 `android:name=".MyApplication"` 已在 `AndroidManifest.xml` 中设置；Application类不是抽象的 |
| Gradle插件未找到 | 首先在项目级 `build.gradle.kts` 中添加插件，然后 `apply false`；验证版本 `6.1.0` |
| ProGuard映射未上传 | 设置 `SENTRY_AUTH_TOKEN` 环境变量；确保 `autoUploadProguardMapping = true` 在 `sentry {}` 块中 |
| NDK崩溃未捕获 | 验证 `isEnableNdk = true`（默认）；确保项目在 `android.ndkVersion` 中配置了NDK |
| 调试器中报告ANR | 设置 `isAnrReportInDebug = false`（默认）；ANR看门狗在调试器暂停线程时触发 |
| 会话回放未录制 | 需要API 26+；验证 `sessionSampleRate > 0` 或 `onErrorSampleRate > 0`；检查Logcat中的回放错误 |
| 会话回放显示空白屏幕 | PixelCopy（默认）需要硬件加速；尝试 `SentryReplayOptions.screenshotQuality = CANVAS` |
| 回放遮罩未对齐 | 具有属性 `translationX/Y` 或 `clipToPadding=false` 的视图可能会偏移遮罩；向 [github.com/getsentry/sentry-java](https://github.com/getsentry/sentry-java) 报告 |
| `beforeSend` 未触发 | `beforeSend` 仅拦截管理（Java/Kotlin）事件；NDK原生崩溃会绕过它 |
| OkHttp跨度未出现 | 将 `SentryOkHttpInterceptor` 添加到您的 `OkHttpClient`，或使用Gradle插件 `OKHTTP` 字节码增强 |
| 跨度未附加到事务 | 确保 `TransactionOptions().setBindToScope(true)` 在启动事务时设置；子跨度会查找作用域根 |
| 跟踪未记录 | 验证 `tracesSampleRate > 0`；Activity增强需要 `isEnableAutoActivityLifecycleTracing = true`（默认） |
| 持续性能分析未工作 | SDK ≥ 8.7.0需要；API 22+需要；设置 `profileSessionSampleRate > 0`；不要同时设置 `profilesSampleRate` |
| 两种性能分析模式都设置 | `profilesSampleRate` 和 `profileSessionSampleRate` 互斥 — 只使用一个 |
| TTFD跨度缺失 | 设置 `isEnableTimeToFullDisplayTracing = true` 并在屏幕准备好时调用 `Sentry.reportFullyDisplayed()` |
| Kotlin协程作用域丢失 | 添加 `sentry-kotlin-extensions` 依赖；使用 `Sentry.cloneMainContext()` 传播跟踪上下文 |
| 发布构建堆栈跟踪无法读取 | ProGuard映射未上传；确认Gradle插件 `autoUploadProguardMapping = true` 并设置了认证令牌 |
| 源上下文未在Sentry中显示 | 在 `sentry {}` 块中启用 `includeSourceContext = true`（需要Gradle插件） |
| BOM版本冲突 | 使用 `implementation(platform("io.sentry:sentry-bom:8.33.0"))` 并从所有其他 `io.sentry:*` 条目中省略版本 |
| 版本目录别名未解析 | 编辑 `gradle/libs.versions.toml` 后同步Gradle；别名名称在TOML中使用 `-`，在构建文件中使用 `.`（例如，`sentry-android` → `libs.sentry.android`） |
| 版本目录中存在重复的Sentry版本 | 重用现有的 `[versions] sentry = "..."` 条目；不要添加第二个键，并且在使用版本目录时不要在 `build.gradle` 中硬编码版本 |
| `SENTRY_AUTH_TOKEN` 暴露 | 认证令牌仅用于构建时间 — 绝对不要将其传递给 `SentryAndroid.init()` 或嵌入APK |
