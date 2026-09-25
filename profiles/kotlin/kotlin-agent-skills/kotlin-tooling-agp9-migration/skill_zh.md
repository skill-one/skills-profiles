# KMP AGP 9.0 迁移

Android Gradle 插件 9.0 使 Android 应用和库插件与同一模块中的 Kotlin 多平台插件不兼容。本指南将指导您完成迁移过程。

## 第 0 步：分析项目

在做出任何更改之前，了解项目结构：

1. 读取 `settings.gradle.kts`（或 `.gradle`）以找到所有模块
2. 对于每个模块，读取其 `build.gradle.kts` 以识别已应用的插件
3. 检查项目是否使用 Gradle 版本目录（`gradle/libs.versions.toml`）。如果存在，则读取它以获取当前的 AGP/Gradle/Kotlin 版本。如果不存在，则直接在 `build.gradle.kts` 文件中查找版本（通常在根 `buildscript {}` 或 `plugins {}` 块中）。**请根据本指南中的所有示例进行相应调整**——版本目录示例使用 `alias(libs.plugins.xxx)`，而直接使用则使用 `id("plugin.id") version "x.y.z"`
4. 读取 `gradle/wrapper/gradle-wrapper.properties` 以获取 Gradle 版本
5. 检查 `gradle.properties` 中是否存在任何现有的解决方案（`android.enableLegacyVariantApi`）
6. 检查 `org.jetbrains.kotlin.android` 插件的使用情况——AGP 9.0 具有内置 Kotlin，此插件必须被移除
7. 检查 `org.jetbrains.kotlin.kapt` 插件的使用情况——与内置 Kotlin 不兼容，必须迁移到 KSP 或 `com.android.legacy-kapt`
8. 检查可能与 AGP 9.0 不兼容的第三方插件（见下文“插件兼容性”部分）

如果 Bash 可用，请从本指南的目录中运行 `scripts/analyze-project.sh` 以获取结构化摘要。

### 对每个模块进行分类

对于每个模块，确定其类型：

| 当前插件                                                          | 迁移路径                              |
|--------------------------------------------------------------------------|---------------------------------------------|
| `kotlin.multiplatform` + `com.android.library`                           | **路径 A** — 库插件交换            |
| `kotlin.multiplatform` + `com.android.application`                       | **路径 B** — 强制 Android 分割        |
| `kotlin.multiplatform` 在一个模块中具有多个平台入口点                 | **路径 C** — 完全重构（推荐） |
| `com.android.application` 或 `com.android.library`（无 KMP）              | 见下文“纯 Android 小贴士”               |

### 确定范围

- **路径 B 是强制的** 对于任何结合 KMP + Android 应用程序插件的模块
- **路径 C 是推荐的** 当项目具有一个整体的 `composeApp`（或类似）模块，其中包含多个平台（Android、桌面、Web）的入口点时。这符合新的 JetBrains 默认项目结构，其中每个平台都有自己的应用程序模块。
- **询问用户** 他们是否只想使用路径 B（最小要求）或路径 C（推荐完全重构）

## 路径 A：库模块迁移

当模块应用 `kotlin.multiplatform` + `com.android.library` 时使用此方法。

参见 [references/MIGRATION-LIBRARY.md](references/MIGRATION-LIBRARY.md) 以获取完整的原始/后代码。

摘要：

1. **替换插件**：`com.android.library` → `com.android.kotlin.multiplatform.library`
2. **如果存在，则移除 `org.jetbrains.kotlin.android`** 插件（AGP 9.0 具有内置 Kotlin 支持）
3. **迁移 DSL**：将配置从顶层 `android {}` 块移动到 `kotlin { android {} }`：
   ```kotlin
   kotlin {
       android {
           namespace = "com.example.lib"
           compileSdk = 35
           minSdk = 24
       }
   }
   ```
4. **重命名源目录**（仅当模块使用经典 Android 布局而不是 KMP 布局时）：
   - `src/main` → `src/androidMain`
   - `src/test` → `src/androidHostTest`
   - `src/androidTest` → `src/androidDeviceTest`
   - 如果模块已经使用 `src/androidMain/`，则无需重命名目录
5. **将依赖项** 从顶层 `dependencies {}` 移动到 `sourceSets`：
   ```kotlin
   kotlin {
       sourceSets {
           androidMain.dependencies {
               implementation("androidx.appcompat:appcompat:1.7.0")
           }
       }
   }
   ```
6. **如果模块使用 Android 或 Compose Multiplatform 资源，请显式启用资源**：
   ```kotlin
   kotlin {
       android {
           androidResources { enable = true }
       }
   }
   ```
7. **如果模块具有 `.java` 源文件，请显式启用 Java 编译**：
   ```kotlin
   kotlin {
       android {
           withJava()
       }
   }
   ```
8. **如果模块具有单元测试或仪器测试，请显式启用测试**：
   ```kotlin
   kotlin {
       android {
           withHostTest { isIncludeAndroidResources = true }
           withDeviceTest {
               instrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
           }
       }
   }
   ```
9. **更新 Compose 工具依赖项**：
   ```kotlin
   // 旧版：
   debugImplementation(libs.androidx.compose.ui.tooling)
   // 新版：
   androidRuntimeClasspath(libs.androidx.compose.ui.tooling)
   ```
10. **如果适用，请显式发布消费者 ProGuard 规则**：
    ```kotlin
    kotlin {
        android {
            consumerProguardFiles.add(file("consumer-rules.pro"))
        }
    }
    ```
11. **解决子依赖项变体（产品风味 / 构建类型）**：
    由于新的 KMP Android 库插件强制执行单变体架构，它无法原生理解如何解决发布多个变体的依赖项（例如 `debug`/`release` 构建类型，或产品风味如 `free`/`paid`）。使用 `localDependencySelection` 配置回退行为：
    ```kotlin
    kotlin {
        android {
            localDependencySelection {
                // 确定从 Android 库依赖项中消费哪个构建类型，按优先级顺序
                selectBuildTypeFrom.set(listOf("debug", "release"))
                
                // 如果依赖项具有 'tier' 维度，则选择 'free' 风味
                productFlavorDimension("tier") {
                    selectFrom.set(listof("free"))
                }
            }
        }
    }
    ```

## 路径 B：Android 应用程序 + 共享模块分割

当模块应用 `kotlin.multiplatform` + `com.android.application` 时使用此方法。这是 **强制的** 对于 AGP 9.0 兼容性。

参见 [references/MIGRATION-APP-SPLIT.md](references/MIGRATION-APP-SPLIT.md) 以获取完整指南。

摘要：

1. **创建 `androidApp` 模块** 并为其创建自己的 `build.gradle.kts`：
   ```kotlin
   plugins {
       alias(libs.plugins.androidApplication)
       // 不要应用 kotlin-android — AGP 9.0 包含 Kotlin 支持
       alias(libs.plugins.composeMultiplatform)  // 如果使用 Compose
       alias(libs.plugins.composeCompiler)       // 如果使用 Compose
   }

   android {
       namespace = "com.example.app"
       compileSdk = 35
       defaultConfig {
           applicationId = "com.example.app"
           minSdk = 24
           targetSdk = 35
           versionCode = 1
           versionName = "1.0"
       }
       buildFeatures { compose = true }
   }

   dependencies {
       implementation(projects.shared)  // 或 whatever the shared module is named
       implementation(libs.androidx.activity.compose)
   }
   ```
2. **将 Android 入口点代码** 从 `src/androidMain/` 移动到 `androidApp/src/main/`：
   - `MainActivity.kt`（以及任何其他 Activities/Fragments）
   - `AndroidManifest.xml`（应用级别的 manifest，带有 `<application>` 和启动器 `<activity>`）——验证 `<activity>` 上的 `android:name` 使用其在新位置的全限定类名
   - Android 应用程序类（如果存在）
   - 应用级别的资源（启动器图标、主题等）
3. **添加到 `settings.gradle.kts`**：`include(":androidApp")`
4. **添加到根 `build.gradle.kts`**：插件声明与 `apply false`
5. **将原始模块** 从应用程序转换为库，使用路径 A 步骤
6. **确保不同的命名空间**：应用程序模块和库模块必须具有不同的命名空间
7. **从共享模块中移除**：`applicationId`、`targetSdk`、`versionCode`、`versionName`
8. **更新 IDE 运行配置**：将模块从旧模块更改为 `androidApp`

## 路径 C：完全重构（推荐）

当项目具有一个整体的模块（通常为 `composeApp`）其中包含多个平台的入口点时使用此方法。这是可选的，但符合新的 JetBrains 默认。

参见 [references/MIGRATION-FULL-RESTRUCTURE.md](references/MIGRATION-FULL-RESTRUCTURE.md) 以获取完整指南。

### 目标结构

```
project/
├── shared/              ← KMP 库（以前的 composeApp），纯共享代码
├── androidApp/          ← 仅 Android 入口点
├── desktopApp/          ← 仅桌面入口点（如果存在桌面目标）
├── webApp/              ← 仅 Wasm/JS 入口点（如果存在 Web 目标）
├── iosApp/              ← iOS Xcode 项目（通常已经分离）
└── ...
```

### 步骤

1. **首先应用路径 B** — 提取 `androidApp`（对于 AGP 9.0 是强制的）
2. **提取 `desktopApp`**（如果存在桌面目标）：
   - 创建模块，应用 `org.jetbrains.compose` 和 `application {}` 插件
   - 将 `main()` 函数从 `desktopMain` 移动到 `desktopApp/src/main/kotlin/`
   - 将 `compose.desktop { application { ... } }` 配置移动到 `desktopApp/build.gradle.kts`
   - 依赖 `shared` 模块
3. **提取 `webApp`**（如果存在 wasmJs/js 目标）：
   - 创建模块，应用适当的 Kotlin/JS 或 Kotlin/Wasm 配置
   - 将 Web 入口点从 `wasmJsMain`/`jsMain` 移动到 `webApp/src/wasmJsMain/kotlin/`
   - 将浏览器/分发配置移动到 `webApp/build.gradle.kts`
   - 依赖 `shared` 模块
4. **iOS** — 通常已经在单独的 `iosApp` 目录中。验证：
   - 框架导出配置 (`binaries.framework`) 保持在 `shared` 模块中
   - Xcode 项目引用正确的框架路径
5. **重命名模块** 从 `composeApp` 到 `shared`：
   - 重命名目录
   - 更新 `settings.gradle.kts` include
   - 更新跨模块的所有依赖项引用
6. **清理共享模块**：移除所有平台入口点代码和已移动到平台应用程序模块的应用程序特定配置

### 变体：原生 UI

如果某些平台使用原生 UI（例如 iOS 的 SwiftUI），将 `shared` 分割为：
- `sharedLogic` — 被所有平台消费的业务逻辑
- `sharedUI` — 仅被使用共享 UI 的平台消费的 Compose Multiplatform UI

### 变体：服务器

如果项目包含服务器目标：
- 在根处添加 `server` 模块
- 将所有客户端模块置于 `app/` 目录下
- 添加 `core` 模块，用于服务器和客户端之间共享的代码（模型、验证）

## 版本更新

无论迁移路径如何，都需要执行以下操作：

1. **Gradle wrapper** — 更新到 9.1.0+：
   ```properties
   # gradle/wrapper/gradle-wrapper.properties
   distributionUrl=https\://services.gradle.org/distributions/gradle-9.1.0-bin.zip
   ```
2. **AGP 版本** — 更新到 9.0.0+ 并添加 KMP 库插件。

   使用版本目录 (`gradle/libs.versions.toml`)：
   ```toml
   [versions]
   agp = "9.0.1"

   [plugins]
   android-kotlin-multiplatform-library = { id = "com.android.kotlin.multiplatform.library", version.ref = "agp" }
   ```

   不使用版本目录 — 更新 `com.android.*` 插件版本，并在根 `build.gradle.kts` 中添加：
   ```kotlin
   plugins {
       id("com.android.application") version "9.0.1" apply false
       id("com.android.kotlin.multiplatform.library") version "9.0.1" apply false
   }
   ```
3. **JDK** — 确保使用 JDK 17+（AGP 9.0 所需）
4. **SDK 构建工具** — 更新到 36.0.0：
   ```
   通过 SDK Manager 安装或配置 android { buildToolsVersion = "36.0.0" }
   ```
5. **审查 gradle.properties** — 移除导致错误的属性，并审查更改的默认值（见“Gradle 属性默认值更改”部分）

## 内置 Kotlin 迁移

AGP 9.0 默认为所有 `com.android.application` 和 `com.android.library` 模块启用内置 Kotlin 支持。不再需要 `org.jetbrains.kotlin.android` 插件，如果应用它将会冲突。

**重要提示**：内置 Kotlin 不会取代 KMP 支持。KMP 库模块仍然需要 `org.jetbrains.kotlin.multiplatform` + `com.android.kotlin.multiplatform.library`。

### 第 1 步：移除 kotlin-android 插件

从所有模块级和根级构建文件中移除：

```kotlin
// 从模块 build.gradle.kts 中移除
plugins {
    // 移除：alias(libs.plugins.kotlin.android)
    // 移除：id("org.jetbrains.kotlin.android")
}

// 从根 build.gradle.kts 中移除
plugins {
    // 移除：alias(libs.plugins.kotlin.android) apply false
}
```

从版本目录 (`gradle/libs.versions.toml`) 中移除：
```toml
[plugins]
# 移除：kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
```

### 第 2 步：将 kapt 迁移到 KSP 或 legacy-kapt

`org.jetbrains.kotlin.kapt` 插件与内置 Kotlin **不兼容**。

**首选：迁移到 KSP** — 请参阅每个注解处理程序的 KSP 迁移指南。

**备用方案：使用 `com.android.legacy-kapt`**（与 AGP 相同版本）：
```toml
# gradle/libs.versions.toml
[plugins]
legacy-kapt = { id = "com.android.legacy-kapt", version.ref = "agp" }
```
```kotlin
// 模块 build.gradle.kts — 用 legacy-kapt 替换 kotlin-kapt
plugins {
    // 移除：alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.legacy.kapt)
}
```

### 第 3 步：将 kotlinOptions 迁移到 compilerOptions

对于纯 Android 模块（非 KMP），将 `android.kotlinOptions {}` 迁移到顶层 `kotlin.compilerOptions {}`：
```kotlin
// 旧版
android {
    kotlinOptions {
        jvmTarget = "11"
        languageVersion = "2.0"
        freeCompilerArgs += listOf("-Xopt-in=kotlin.RequiresOptIn")
    }
}

// 新版
kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_11)
        languageVersion.set(org.jetbrains.kotlin.gradle.dsl.KotlinVersion.KOTLIN_2_0)
        optIn.add("kotlin.RequiresOptIn")
    }
}
```

**注意**：在内置 Kotlin 中，`jvmTarget` 默认为 `android.compileOptions.targetCompatibility`，因此如果已经设置 `compileOptions`，则它可能是可选的。

### 第 4 步：将 kotlin.sourceSets 迁移到 android.sourceSets

在内置 Kotlin 中，仅支持带有 `kotlin` 集合的 `android.sourceSets {}`：
```kotlin
// 在内置 Kotlin 中不支持：
kotlin.sourceSets.named("main") {
    kotlin.srcDir("additionalSourceDirectory/kotlin")
}

// 正确：
android.sourceSets.named("main") {
    kotlin.directories += "additionalSourceDirectory/kotlin"
}
```

对于生成源，使用 Variant API：
```kotlin
androidComponents.onVariants { variant ->
    variant.sources.kotlin!!.addStaticSourceDirectory("additionalSourceDirectory/kotlin")
}
```

### 每个模块的迁移策略

对于大型项目，逐个模块迁移：

1. 全局禁用：在 `gradle.properties` 中 `android.builtInKotlin=false`
2. 通过应用选择插件逐个启用已迁移模块：
   ```kotlin
   plugins {
       id("com.android.built-in-kotlin") version "AGP_VERSION"
   }
   ```
3. 对该模块执行步骤 1-4
4. 所有模块迁移完成后，移除 `android.builtInKotlin=false` 和所有 `com.android.built-in-kotlin` 插件

### 可选：为非 Kotlin 模块禁用 Kotlin

对于包含**没有 Kotlin 源代码**的模块，禁用内置 Kotlin 以节省构建时间：
```kotlin
android {
    enableKotlin = false
}
```

### 选择退出（临时）

如果被插件不兼容阻止，可以临时选择退出：
```properties
# gradle.properties
android.builtInKotlin=false
android.newDsl=false  # 如果使用新 DSL 选择退出，也需要此属性
```

**警告**：询问用户是否要选择退出，如果是，请提醒他们这是一个临时措施。

## 插件兼容性

参见 [references/PLUGIN-COMPATIBILITY.md](references/PLUGIN-COMPATIBILITY.md) 以获取完整的兼容性表，其中包含已知的兼容版本、选择退出标志解决方案和损坏的插件。

**在迁移之前**，列出项目中的所有插件，并对照该表格检查每个插件。如果任何插件没有解决方案而损坏，请通知用户。如果插件需要选择退出标志，请将它们添加到 `gradle.properties` 并将它们记为临时解决方案。

## Gradle 属性默认值更改

AGP 9.0 更改了许多 Gradle 属性的默认值。检查 `gradle.properties` 中任何显式设置的值，看看是否可能现在存在冲突。主要更改：

| 属性                                             | 旧默认值 | 新默认值 | 操作                                            |
|------------------------------------------------------|-------------|-------------|---------------------------------------------------|
| `android.uniquePackageNames`                         | `false`     | `true`      | 确保每个库具有唯一的命名空间        |
| `android.enableAppCompileTimeRClass`                 | `false`     | `true`      | 重构 `switch` on R 字段的 `if/else`        |
| `android.defaults.buildfeatures.resvalues`           | `true`      | `false`     | 在需要的地方启用 `resValues = true`            |
| `android.defaults.buildfeatures.shaders`             | `true`      | `false`     | 在需要的地方启用着色器                       |
| `android.r8.optimizedResourceShrinking`              | `false`     | `true`      | 审查 R8 保留规则                              |
| `android.r8.strictFullModeForKeepRules`              | `false`     | `true`      | 更新保留规则以使其明确                  |
| `android.proguard.failOnMissingFiles`                | `false`     | `true`      | 移除无效的 ProGuard 文件引用           |
| `android.r8.proguardAndroidTxt.disallowed`           | `false`     | `true`      | 仅使用 `proguard-android-optimize.txt`          |
| `android.r8.globalOptionsInConsumerRules.disallowed` | `false`     | `true`      | 从库消费者规则中移除全局选项                 |
| `android.sourceset.disallowProvider`                 | `false`     | `true`      | 在 androidComponents 上使用 `Sources` API |
| `android.sdk.defaultTargetSdkToCompileSdkIfUnset`    | `false`     | `true`      | 显式指定 `targetSdk`                    |
| `android.onlyEnableUnitTestForTheTestedBuildType`    | `false`     | `true`      | 仅在测试非默认构建类型时启用          |

查找并移除现在导致错误的属性：
- `android.r8.integratedResourceShrinking` — 已移除，始终开启
- `android.enableNewResourceShrinker.preciseShrinking` — 已移除，始终开启

## 纯 Android 小贴士

对于升级到 AGP 9.0 的非 KMP Android 模块，请遵循上述“内置 Kotlin 迁移”步骤，然后审查“Gradle 属性默认值更改”表格。其他更改：

- **审查新的 DSL 接口** — `BaseExtension` 已移除；使用 `CommonExtension` 或特定扩展类型
- **Java 默认值已更改为 Java 8 到 Java 11** — 确保 `compileOptions` 反映此更改

## 验证

迁移后，使用 [checklist](assets/checklist.md) 进行验证。关键检查：

1. `./gradlew build` 成功且无错误
2. 所有平台目标成功构建（Android、iOS 通过 `xcodebuild`、桌面、JS/Wasm）
3. `./gradlew :shared:allTests` 和 Android 单元测试通过
4. KMP 模块中不存在 `com.android.library` 或 `com.android.application`
5. AGP 9.0 模块中不存在 `org.jetbrains.kotlin.android`
6. 源集使用正确的名称 (`androidMain`，`androidHostTest`，`androidDeviceTest`)
7. 无关于变体 API 或 DSL 的弃用警告

## 常见问题

参见 [references/KNOWN-ISSUES.md](references/KNOWN-ISSUES.md) 获取详细信息。关键注意事项：

### KMP 库插件问题
- **库模块中不可用 BuildConfig** — 使用 DI/`AppConfiguration` 接口，或使用 [BuildKonfig](https://github.com/yshrsmz/BuildKonfig) 或 [gradle-buildconfig-plugin](https://github.com/gmazzo/gradle-buildconfig-plugin) 用于编译时常量
- **无构建变体** — 单变体架构；编译时常量可以使用 BuildKonfig/gradle-buildconfig-plugin 风味，但变体特定的依赖项/资源/签名必须移动到应用程序模块
- **NDK/JNI 在新插件中不受支持** — 提取到单独的 `com.android.library` 模块
- **Compose 资源无 `androidResources { enable = true }` 会崩溃**
- **消费者 ProGuard 规则未迁移到 `consumerProguardFiles.add(file(...))` 在新 DSL 中会静默丢失**
- **KSP** 需要 2.3.1+ 版本以与 AGP 9.0 兼容

### AGP 9.0 一般问题
- **BaseExtension 已移除** — 使用旧 DSL 类型的约定插件需要重写为使用 `CommonExtension`
- **变体 API 已移除** — `applicationVariants`，`libraryVariants`，`variantFilter` 替换为 `androidComponents`
- **约定插件** 需要重构 — 旧的 `android {}` 扩展辅助函数已过时

## 参考文件

- [DSL 参考](references/DSL-REFERENCE.md) — 旧版→新版 DSL 对应关系
- [版本矩阵](references/VERSION-MATRIX.md) — AGP/Gradle/KGP/Compose/IDE 兼容性
- [插件兼容性](references/PLUGIN-COMPATIBILITY.md) — 第三方插件状态和解决方案
