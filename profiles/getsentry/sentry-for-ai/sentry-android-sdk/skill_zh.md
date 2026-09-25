> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > Android SDK

# Sentry Android SDK

一个有主见的向导，它会扫描您的 Android 项目并指导您完成完整的 Sentry 设置——错误监控、跟踪、分析、会话回放、日志记录等。

## 在何时调用此技能

- 用户询问在 Android 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Android 中进行错误监控、崩溃报告、ANR 检测、跟踪、分析、会话回放或日志记录
- 用户提到 `sentry-android`、`io.sentry:sentry-android`、移动崩溃跟踪或 Sentry for Kotlin/Java Android
- 用户希望监控原生（NDK）崩溃、应用程序无响应（ANR）事件或应用启动性能

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的当前状态（`io.sentry:sentry-android:8.33.0`，Gradle 插件 `6.1.0`）。
> 在实施之前，请始终在 [docs.sentry.io/platforms/android/](https://docs.sentry.io/platforms/android/) 进行验证。

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

# 检测 Gradle 版本目录（libs.versions.toml）——现代 AGP 项目
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

# 相邻的后端（用于跨链接）
ls ../backend ../server ../api 2>/dev/null
find .. -maxdepth 2 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" \) 2>/dev/null | grep -v node_modules | head -5
```

**需要确定的内容：**

| 问题 | 影响 |
|----------|--------|
| `build.gradle.kts` 存在？ | 在所有示例中使用 Kotlin DSL 语法 |
| `gradle/libs.versions.toml` 存在？ | 将 Sentry 添加到版本目录；在构建文件中通过 `libs.*` 引用 |
| 目录中已经存在 `sentry` 条目？ | 重用现有的版本引用；不要重复或硬编码版本 |
| `minSdk < 26`？ | 注意会话回放需要 API 26+——低于此版本时为静默 no-op |
| 检测到 Compose？ | 推荐 `sentry-compose-android` 和针对 Compose 的特定掩码 |
| OkHttp 存在？ | 推荐 `sentry-okhttp` 拦截器或 Gradle 插件字节码自动instrumentation |
| Room/SQLite 存在？ | 推荐 `sentry-android-sqlite` 或插件字节码instrumentation |
| Timber 存在？ | 推荐 `sentry-android-timber` 集成 |
| Jetpack Navigation？ | 推荐 `sentry-android-navigation` 用于屏幕跟踪 |
| 已经存在 `SentryAndroid.init()`？ | 跳过安装，直接跳到功能配置 |
| 存在 Application 子类？ | `SentryAndroid.init()` 就放在那里 |

---

## 第二阶段：建议

根据您发现的内容，提出一个具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖——始终设置这些）：**
- ✅ **错误监控** — 自动捕获未捕获的异常、ANRs 和原生 NDK 崩溃
- ✅ **跟踪** — 自动instrument Activity 生命周期、应用启动、HTTP 请求和数据库查询
- ✅ **会话回放** — 记录屏幕捕获和用户交互以进行调试（API 26+）

**可选（增强的可观察性）：**
- ⚡ **分析** — 持续 UI 分析（推荐）或基于事务的采样
- ⚡ **日志记录** — 通过 `Sentry.logger()` 的结构化日志，可选 Timber 桥接
- ⚡ **用户反馈** — 从应用内部收集用户提交的 Bug 报告

**建议逻辑：**

| 功能 | 当...推荐 |
|----------|------------------|
| 错误监控 | **始终** — 任何 Android 应用的非协商性基线 |
| 跟踪 | **始终用于 Android** — 应用启动时间、Activity 生命周期、网络延迟很重要 |
| 会话回放 | 用户面生产应用（API 26+）；用户问题的可视化调试 |
| 分析 | 性能敏感的应用、启动时间调查、生产性能分析 |
| 日志记录 | 应用使用结构化日志或您希望在 Sentry 中进行日志到跟踪的关联 |
| 用户反馈 | Beta 或面向客户的应用，您希望收集用户提交的 Bug 报告 |

建议：*"对于您的 [Kotlin / Java] Android 应用（minSdk X），我建议设置错误监控 + 跟踪 + 会话回放。您还想我添加分析和日志记录吗？*"

---

## 第三阶段：指导

### 确定您的设置路径

| 项目类型 | 推荐设置 | 复杂性 |
|-------------|------------------|------------|
| 新项目，没有现有的 Sentry | Gradle 插件（推荐） | 低 — 插件处理大多数配置 |
| 现有项目，没有 Sentry | Gradle 插件或手动初始化 | 中等 — 添加依赖项 + Application 类 |
| 手动完全控制 | 在 Application 中 `SentryAndroid.init()` | 中等 — 显式配置，最灵活 |

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
> **完成后，回来并跳到 [验证](#verification)。**

如果用户跳过向导，请继续执行下面的“手动设置”。

---

### 选项 2：手动设置

#### 使用 Gradle 版本目录 (`gradle/libs.versions.toml`)

如果第一阶段检测到 `gradle/libs.versions.toml`，请首先将 Sentry 添加到目录中，然后从您的构建文件中引用它。这可以保持版本集中化，并匹配现代 AGP 项目的约定。

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
> 如果目录已经定义了 `sentry` 版本，请重用它而不是添加重复条目。

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

Groovy DSL (`app/build.gradle`) 等效:
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

然后继续使用 `sentry {}` 配置块从下面的路径 A，步骤 2 以下开始。设置（Application 类初始化、清单注册、验证）是相同的。

---

#### 路径 A：Gradle 插件（推荐）

Sentry Gradle 插件是最简单的设置路径。它：
- 在发布构建中自动上传 ProGuard/R8 映射文件
- 将源上下文注入堆栈帧
- 通过字节码转换可选地instrument OkHttp、Room/SQLite、文件 I/O、Compose 导航和 `android.util.Log`（零源代码更改）

**步骤 1 — 在项目级别的 `build.gradle[.kts]` 中添加插件**

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
    // 使用 BOM 以确保 Sentry 模块之间版本一致
    implementation platform("io.sentry:sentry-bom:8.33.0")
    implementation "io.sentry:sentry-android"

    // 可选集成（添加相关的）:
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

    // 启用通过字节码转换的自动instrumentation（无需源代码更改）
    tracingInstrumentation {
        enabled = true
        features = [InstrumentationFeature.DATABASE, InstrumentationFeature.FILE_IO,
                    InstrumentationFeature.OKHTTP, InstrumentationFeature.COMPOSE]
    }

    // 在发布构建中上传 ProGuard 映射和源上下文
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

    // 可选集成:
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

            // 环境和发布版本
            options.environment = BuildConfig.BUILD_TYPE     // "debug", "release", 等。
            options.release = "${BuildConfig.APPLICATION_ID}@${BuildConfig.VERSION_NAME}+${BuildConfig.VERSION_CODE}"

            // 跟踪——在开发环境中采样 100%，在生产环境中降低到 10–20%
            options.tracesSampleRate = 1.0

            // 分析——使用持续 UI 分析（推荐，SDK ≥ 8.7.0）
            options.profileSessionSampleRate = 1.0

            // 会话回放（仅限 API 26+；低于 API 26 时为静默 no-op）
            options.sessionReplay.sessionSampleRate = 0.1    // 所有会话的 10%
            options.sessionReplay.onErrorSampleRate = 1.0    // 错误的 100%

            // 结构化日志
            options.logs.isEnabled = true

            // 环境
            options.environment = BuildConfig.BUILD_TYPE
        }
    }
}
```

Java 等效:
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

#### 路径 B：手动设置（没有 Gradle 插件）

如果您无法使用 Gradle 插件（例如，非标准的构建设置），请使用此选项。

**步骤 1 — 在 `app/build.gradle[.kts]` 中添加依赖项**

```kotlin
dependencies {
    implementation(platform("io.sentry:sentry-bom:8.33.0"))
    implementation("io.sentry:sentry-android")
}
```

**步骤 2 — 在 Application 类中初始化**（与路径 A，步骤 3 相同）

**步骤 3 — 手动配置 ProGuard/R8**

Sentry SDK 随附一个 ProGuard 规则文件。对于手动映射上传，请在 CI 中安装 `sentry-cli` 并添加到您的 CI：

```bash
sentry-cli releases files "my-app@1.0.0+42" upload-proguard \
  --org YOUR_ORG --project YOUR_PROJECT \
  app/build/outputs/mapping/release/mapping.txt
```

---

### 快速参考：完整的 `SentryAndroid.init()`

```kotlin
SentryAndroid.init(this) { options ->
    options.dsn = "YOUR_SENTRY_DSN"

    // 环境和发布版本
    options.environment = BuildConfig.BUILD_TYPE     // "debug", "release", 等。
    options.release = "${BuildConfig.APPLICATION_ID}@${BuildConfig.VERSION_NAME}+${BuildConfig.VERSION_CODE}"

    // 跟踪——在开发环境中采样 100%，在生产环境中降低到 10–20%
    options.tracesSampleRate = 1.0

    // 分析——使用持续 UI 分析（推荐，SDK ≥ 8.7.0）
    options.profileSessionSampleRate = 1.0

    // 会话回放（仅限 API 26+；低于 API 26 时为静默 no-op）
    options.sessionReplay.sessionSampleRate = 0.1
    options.sessionReplay.onErrorSampleRate = 1.0
    options.sessionReplay.maskAllText = true         // 掩码文本以保护隐私
    options.sessionReplay.maskAllImages = true       // 掩码图像以保护隐私

    // 结构化日志
    options.logs.isEnabled = true

    // 错误丰富
    options.isAttachScreenshot = true                // 出错时捕获屏幕截图
    options.isAttachViewHierarchy = true             // 挂载视图层次结构 JSON

    // ANR 检测（默认 5 秒）——watchdog + ApplicationExitInfo API 30+
    options.isAnrEnabled = true

    // NDK 原生崩溃处理（默认启用）
    options.isEnableNdk = true

    // 发送 PII：IP 地址、用户数据
    options.sendDefaultPii = true

    // 跟踪传播（后端分布式跟踪）
    options.tracePropagationTargets = listOf(
        "api.yourapp.com",
        ".*\\.yourapp\\.com"
    )

    // 调试日志——生产环境中禁用
    options.isDebug = BuildConfig.DEBUG
}
```

---

## 验证

设置后，验证 Sentry 是否正在接收事件：

**测试错误捕获:**
```kotlin
// 在 Activity 或 Fragment 中
try {
    throw RuntimeException("Sentry Android SDK 测试")
} catch (e: Exception) {
    Sentry.captureException(e)
}
```

**测试跟踪:**
```kotlin
val transaction = Sentry.startTransaction("test-task", "task")
val span = transaction.startChild("test-span", "description")
span.finish()
transaction.finish()
```

**测试结构化日志（SDK ≥ 8.12.0）:**
```kotlin
Sentry.logger().info("Sentry 日志测试")
Sentry.logger().error("错误日志测试", Exception("测试错误"))
```

**检查 Sentry 仪表板:**
- **问题** → 您的测试异常应在几秒钟内出现
- **跟踪** → 查找 `test-task` 事务及其子跨度
- **回放** → 应用交互后可见会话录制（需要 API 26+）
- **日志** → 结构化日志条目在日志选项卡下可见

如果什么都没有出现：
1. 设置 `isDebug = true` — SDK 日志记录到 Logcat
2. 验证 DSN 是正确的，并与您的 Sentry 项目匹配
3. 确认您的 `Application` 类在 `AndroidManifest.xml` 中注册为 `android:name`
4. 确认设备/模拟器具有互联网连接
5. 对于 NDK 崩溃，确保 `isEnableNdk = true`（默认）并使用 NDK 支持构建

---

## 跨链接

完成 Android 设置后，检查是否有缺少 Sentry 覆盖的后端或 Web 前端：

```bash
# 相邻的后端目录
ls ../backend ../server ../api 2>/dev/null
cat ../go.mod 2>/dev/null | head -3
cat ../requirements.txt ../pyproject.toml 2>/dev/null | head -5
cat ../Gemfile 2>/dev/null | head -3
ls ../backend/package.json ../server/package.json 2>/dev/null

# iOS 对应应用
ls ../ios ../YourApp-iOS 2>/dev/null
find .. -maxdepth 3 -name "*.xcodeproj" 2>/dev/null | head -3
```

如果存在后端或相关平台没有 Sentry，建议匹配的技能：

| 检测到 | 建议技能 |
|----------|--------------|
| Go 后端 (`go.mod`) | `sentry-go-sdk` |
| Python 后端 (`requirements.txt`, `pyproject.toml`) | `sentry-python-sdk` |
| Ruby 后端 (`Gemfile`) | `sentry-ruby-sdk` |
| Node.js 后端 | `@sentry/node` — 请参阅 [docs.sentry.io/platforms/javascript/guides/express/](https://docs.sentry.io/platforms/javascript/guides/express/) |
| iOS 应用 (`.xcodeproj`) | `sentry-cocoa-sdk` |
| React Native (`package.json` 包含 `react-native`) | `sentry-react-native-sdk` |
| React / Next.js Web | `sentry-react-sdk` 或 `sentry-nextjs-sdk` |

**分布式跟踪设置** — 如果添加了后端技能，请在 Android 中配置 `tracePropagationTargets` 以将跟踪上下文传播到您的 API：

```kotlin
options.tracePropagationTargets = listOf(
    "api.yourapp.com",
    ".*\\.yourapp\\.com"
)
```

这将使移动事务与后端跟踪在 Sentry 水falls 视图中链接起来。
