---
name: kotlin-tooling-cocoapods-spm-migration
description: 将 KMP 项目从 CocoaPods (kotlin("native.cocoapods")) 迁移到 Swift Package Manager (swiftPMDependencies DSL) — 替换 pod() 为 swiftPackage()，将 cocoapods.* 导入转换为 swiftPMImport.*，并重新配置 Xcode 项目。
---

# KMP 从 CocoaPods 迁移到 SwiftPM

将 Kotlin Multiplatform 项目从 `kotlin("native.cocoapods")` 迁移到 `swiftPMDependencies {}` DSL。

## 要求

- **Kotlin**: 2.4.0-Beta2 或更高版本（首次公开发布支持 `swiftPMDependencies` 的版本，可在 Maven Central 上获取）
- **Xcode**: 16.4 或 26.0+
- **iOS 部署目标**: 推荐 16.0+

## 迁移概述

**重要提示**: 在第 6 步之前，请保持 `cocoapods {}` 块和插件处于活动状态。迁移过程首先在现有 CocoaPods 设置旁边添加 `swiftPMDependencies {}`，然后重新配置 Xcode，最后才移除 CocoaPods。

| 步骤 | 操作 |
|------|------|
| 1 | 分析现有的 CocoaPods 配置 |
| 2 | 更新 Gradle 配置（仓库、Kotlin 版本） |
| 3 | 在现有的 `cocoapods {}` 旁边添加 `swiftPMDependencies {}` |
| 4 | 转换 Kotlin 导入 |
| 5 | 重新配置 iOS 项目并解耦 CocoaPods |
| 6 | 从 Gradle 中移除 CocoaPods 插件 |
| 7 | 验证 Gradle 构建和 Xcode 项目构建 |
| 8 | 编写 MIGRATION_REPORT.md |

---

## 第 1 步：迁移前分析

### 1.0 验证项目构建

在开始迁移之前，识别要迁移的模块并确认其成功编译。

1. **找到使用 CocoaPods 的模块** — 查找包含 `cocoapods` 的 `build.gradle.kts` 文件：
   ```bash
   grep -rl "cocoapods" --include="build.gradle.kts" .
   ```
   从路径中提取模块名称（例如，`./shared/build.gradle.kts` → 模块名称是 `shared`）。注意：多个模块可能使用 CocoaPods — 记录所有模块。通常只有生成链接到 iOS 应用的框架的模块需要 `swiftPMDependencies`；其他模块只需移除 CocoaPods（第 6 步）。

2. **编译 Kotlin 代码** — 运行该模块的 Kotlin 编译任务以验证 Kotlin 源代码编译：
   ```bash
   ./gradlew :moduleName:compileKotlinIosSimulatorArm64
   ```
   将 `moduleName` 替换为模块的目录名称（例如，`:shared:compileKotlinIosSimulatorArm64`）。这比完整的 `build`（还会运行发布链接）更快，并且足以验证 Kotlin 代码的正确性。

3. **构建 iOS 应用（可选）** — 尝试找到 Xcode 项目并构建它以确认整个应用成功编译：
   ```bash
   # 找到 Xcode 项目
   find . -name "*.xcworkspace" -not -path "*/Pods/*" -maxdepth 2
   # 构建（替换方案名称为实际的应用方案）
   cd /path/to/iosApp
   xcodebuild -workspace *.xcworkspace -scheme "<AppScheme>" -destination 'generic/platform=iOS Simulator' ARCHS=arm64
   ```
   如果用户想跳过 Xcode 构建，或者找不到 Xcode 项目，可以不进行此步骤 — 第 2 步的 Kotlin 编译足以继续。

4. **如果 Kotlin 编译失败**，要求用户：
   - 提供正确的 Gradle 命令以验证模块构建，或
   - 确认模块处于工作状态，并且可以继续

   如果用户确认而不提供构建命令，**记录迁移前构建无法验证**，并在迁移结束（第 7 步）时警告。

### 1.0a 确认 Kotlin 版本支持 Swift 导入

从 `gradle/libs.versions.toml`（或 `build.gradle.kts`）中读取当前的 Kotlin 版本。

**如果项目已经使用 Kotlin 2.4.0-Beta2 或更高版本** → 记录版本并跳过第 2.1 步（无需版本变更）。

**如果项目使用较旧的 Kotlin 版本** → 第 2.1 步将将其升级到 `2.4.0-Beta2`（首次公开发布支持 `swiftPMDependencies` 的版本，可在 Maven Central 上获取 — 无需自定义仓库）。警告用户："⚠️ Kotlin 版本跳跃 — 跨小版本升级可能会引入与迁移无关的破坏性变更。推荐：先更新，验证可构建，然后重新运行此迁移。" 如果用户确认，则继续。

### 1.1 检查已弃用的 CocoaPods 工作绕过属性

搜索 `gradle.properties` 中的已弃用属性：

```properties
kotlin.apple.deprecated.allowUsingEmbedAndSignWithCocoaPodsDependencies=true
```

此属性是一个工作绕过（参见 [KT-64096](https://youtrack.jetbrains.com/issue/KT-64096)），用于使用 `embedAndSign` 与 CocoaPods 依赖项的项目。它抑制了关于不受支持配置的错误，该错误可能导致运行时崩溃或符号重复。迁移到 SwiftPM 导入后，此属性不再需要，并且在第 6 步**必须移除**。如果找到，则记录其存在。

### 1.2 检查 EmbedAndSign 禁用代码

搜索所有 `build.gradle.kts` 文件中禁用 `EmbedAndSign` 任务（例如，`TaskGraph.whenReady` 过滤器、`tasks.matching` 块）。这是一个 CocoaPods 时代的绕过方法，会**破坏迁移**，因为 `integrateEmbedAndSign`（在第 5 步中需要）也会被禁用。记录任何此类代码 — 它们**必须**在第 6 步中移除，可能需要更早移除。参见 [troubleshooting.md](references/troubleshooting.md) § "`integrateEmbedAndSign` Skipped" 以获取模式。

### 1.3 检查捆绑 cinterop klibs 的第三方 KMP 库

一些 KMP 库随附预构建的 cinterop klibs，并使用 `cocoapods.*` 包命名空间。迁移后，swiftPMDependencies cinterop 生成器检测到这些现有的绑定，并**跳过为这些 Clang 模块生成新绑定**以避免重复。这意味着 `cocoapods.*` 导入对于这些模块必须**保持原样** — 它们解析到第三方库的捆绑 klib，而不是实际的 CocoaPods。

**已知使用捆绑 `cocoapods.*` klibs 的库**：

| 库 | Maven 件 | 捆绑 klib 命名空间 | 提供的类 |
|-----|---------|------------------|---------|
| [KMPNotifier](https://github.com/mirzemehdi/KMPNotifier) | `io.github.mirzemehdi:kmpnotifier` | `cocoapods.FirebaseMessaging` | `FIRMessaging`, `FIRMessagingAPNSTokenType`, 等. |

**如何检测**：搜索 Gradle 依赖声明以查找已知库，然后交叉引用其捆绑命名空间与第 4 步中找到的 `import cocoapods.*` 语句。标记任何匹配项 — 这些导入在第 4 步中**不会**被转换。

如果不确定某个第三方 KMP 库是否捆绑 cinterop klibs，检查项目中的 `linkOnly = true` pod 依赖项 — 这是一个强指示器，表明该库为这些类提供了自己的 klib。

要检查 klib 内容并验证捆绑绑定，参见 [troubleshooting.md](references/troubleshooting.md) § "Third-Party KMP Libraries with Bundled Klibs"。

**查找并记录**：

1. **CocoaPods 配置** - 在 `build.gradle.kts` 文件中搜索 `cocoapods`
2. **Pod 依赖项** - 从 `cocoapods {}` 块中提取 pod 名称和版本
3. **框架配置** - 记录 `baseName`、`isStatic`、部署目标，从 `cocoapods.framework {}`
4. **linkOnly pods** - 记录使用 `linkOnly = true` 声明的 pods。它们有两种常见模式：
   - **KMP 包装库**（例如，`dev.gitlive:firebase-*`）：包装库提供 Kotlin API，而 pod 仅用于链接。参见 [common-pods-mapping.md](references/common-pods-mapping.md) 了解影响。
   - **多模块项目**：消费模块声明 `linkOnly = true`，因为子模块已经提供了该 pod 的 cinterop 绑定。在 SwiftPM 中，`swiftPackage()` 声明应仅在直接使用 pod 的子模块中声明。消费模块**不能**重新声明相同的包 — 它只需要一个没有这些包的 `swiftPMDependencies {}` 块（如果所有 pods 都是 `linkOnly`，则为空）。**导入命名空间影响**：当消费模块导入来自子模块 `swiftPMDependencies` 的 SPM 类时，导入路径使用**子模块的**组和名称作为命名空间（参见第 4 步导入命名空间公式）。
5. **Kotlin 导入** - 查找所有 `import cocoapods.*` 语句。交叉引用以识别哪些导入来自捆绑 klibs（必须保留），哪些来自直接 pod cinterop（必须转换）。
6. **将 pods 映射到 SPM** - 参见 [common-pods-mapping.md](references/common-pods-mapping.md)
7. **定位 iOS 项目目录** - 找到包含 `Podfile` 和 `.xcworkspace` 的目录：
   ```bash
   find . -name "Podfile" -type f
   ```
   记录此路径（例如，`iosApp/`、`ios/` 或项目根目录）— 需要在第 5 步中使用。
8. **检查非 KMP CocoaPods** - 确定项目是否使用 CocoaPods 用于 KMP 之外的依赖项。这会影响第 5 步中的清理策略。
9. **交叉引用 Podfile 与 `cocoapods {}` 块** - 解析 `Podfile` 并将其 pod 条目与 Gradle `cocoapods {}` 块中的 pods 进行比较。记录存在于 `Podfile` 但**未**列在 `cocoapods {}` 中的依赖项。这些 Podfile 仅依赖项通过 CocoaPods 链接到应用中，必须迁移到 `swiftPMDependencies` — 默默删除会导致运行时链接错误。
10. **检查 Xcode 构建阶段** - 打开 `.xcodeproj` 的 `project.pbxproj` 并搜索 Gradle 构建阶段脚本。检查 `embedAndSignAppleFrameworkForXcode` 是否存在但**被注释掉**（以 `#` 开头）。如果被注释掉，则在第 5 步中必须取消注释 — `integrateEmbedAndSign` 任务可能或可能不会自动处理此操作。
11. **检查现有的 Crashlytics dSYM 上传脚本** - 如果使用 FirebaseCrashlytics，搜索 `project.pbxproj` 中的 dSYM 上传 shell 脚本阶段。记录其当前路径（CocoaPods 时代的脚本引用 `${PODS_ROOT}/FirebaseCrashlytics/upload-symbols`）。这必须在第 5 步中更新为 SPM 路径。
12. **识别构建脚本中的 CocoaPods 相关额外内容** - 搜索所有 `build.gradle.kts` 文件中超出标准 `cocoapods {}` 块的 CocoaPods 工作绕过（例如，挂钩到 `podInstall` 的自定义任务、`Pods.xcodeproj` 补丁、podspec 元数据、`extraSpecAttributes`、`noPodspec()` 等）。参见 [cocoapods-extras-patterns.md](references/cocoapods-extras-patterns.md) 获取完整模式列表。记录所有发现 — 这些将在第 6 步中处理。

---

## 第 2 步：Gradle 配置

**重要范围说明**: 在此迁移期间**不要**升级 Gradle 包装器版本、更新 KSP 或更新任何其他依赖项。这些是单独的问题，不在范围内。仅更改以下内容。

### 2.1 更新 Kotlin 版本

**如果项目已经使用 Kotlin 2.4.0-Beta2 或更高版本**（第 1.0a 中记录），则跳过此步骤。

在 `gradle/libs.versions.toml` 中更新到 `2.4.0-Beta2`（或最新支持 Swift 导入的版本）：

```toml
[versions]
kotlin = "2.4.0-Beta2"
```

`2.4.0-Beta2` 可在 Maven Central 上获取 — 无需自定义仓库。

---

## 第 3 步：添加 swiftPMDependencies（保留 CocoaPods）

**在此步骤之前**不要**移除 `cocoapods {}` 块或 `kotlin("native.cocoapods")` 插件。在现有的 CocoaPods 配置旁边添加 `swiftPMDependencies {}`。

### 3.1 添加 group 属性

```kotlin
group = "org.example.myproject"  // 对于导入命名空间是必需的
```

**Compose 资源警告**：如果项目使用 Compose Multiplatform 资源（`org.jetbrains.compose` 插件或 `compose.resources`），`group` 属性也用作生成资源访问器的命名空间（例如，`Res.string.*`、`Res.drawable.*`）。如果 `group` 在 `build.gradle.kts` 中已存在，**不要**更改它。如果你是第一次添加 `group`，则警告用户，因为项目中的现有 Compose 资源访问器调用将更改命名空间，可能需要更新。

### 3.2 在 cocoapods 旁边添加 swiftPMDependencies 块

对于每个 pod 依赖项，添加等效的 SwiftPM 包声明。使用 [common-pods-mapping.md](references/common-pods-mapping.md) 将每个 pod 映射到其 SPM 包 URL、产品名称和 `importedClangModules`。

**版本保留**：迁移期间**不要**更改依赖项版本。使用 `cocoapods {}` 块中指定的确切版本。更改版本可能导致不同的库构建，破坏 cinterop API（移除符号、更改签名）并引入与迁移本身无关的问题。

| CocoaPods 版本规范 | SPM 等效 | 示例 |
|------------------|---------|------|
| `version = "1.2.3"`（确切） | `version = "1.2.3"`（简单）或 `exact("1.2.3")`（类型化） | `pod("GoogleMaps") { version = "10.3.0" }` → `version = "10.3.0"` |
| `version = "~> 1.2"`（乐观） | `version = "1.2.0"`（简单）或 `from("1.2.0")`（类型化） | `pod("FirebaseAuth") { version = "~> 12.5" }` → `version = "12.5.0"` |
| 未指定版本 | 询问用户要固定哪个版本 | 询问用户要使用哪个版本 |

**两种 API 形式**：DSL 提供简单字符串 API 和类型化 API。**对于大多数包使用简单字符串 API**：
```kotlin
swiftPackage(url = "https://github.com/owner/repo.git", version = "1.0.0", products = listOf("ProductName"))
```
简单 API 自动将 `importedClangModules` 默认为 `products` 列表。仅在需要精确版本固定、平台约束或显式 Clang 模块控制时使用类型化 API（使用 `url()`、`exact()`、`product()` 包装器）。参见 [dsl-reference.md](references/dsl-reference.md) 获取类型化 API。

**关键概念**：`products` = SPM 产品名称（控制链接）。`importedClangModules` = Clang 模块名称用于 cinterop 绑定（仅在 `discoverClangModulesImplicitly = false` 时）。`discoverClangModulesImplicitly` 默认为 `true`（所有 Clang 模块的绑定）；设置为 `false` 当传递的 C/C++ 模块 cinterop 失败（Firebase、gRPC）时，显式列出需要的模块。

**重要**：SPM 产品名称和 Clang 模块名称不总是匹配。始终参考 [common-pods-mapping.md](references/common-pods-mapping.md) 获取正确值。

**Podfile 仅依赖项**：如果第 1 步步骤 9 确定了存在于 `Podfile` 但不在 Gradle `cocoapods {}` 块中的依赖项，这些依赖项也必须添加到 `swiftPMDependencies` 作为 `products` 条目。即使 KMP 模块没有声明它们，它们也通过 CocoaPods 链接到应用中，并且可能需要构建应用。查找每个 Podfile 仅 pod 的 SPM 包 URL，并将其作为 `swiftPackage()` 添加，至少包含其 `products`。如果这些 pods 中的任何 pod 通过 cinterop 使用（检查引用它们的 `import cocoapods.*` 语句），也添加 `importedClangModules`。

**不要在 CocoaPods 和 SPM 中混合相同的库套件**。共享相同仓库的库（例如，所有 Firebase 产品）共享传递依赖项。将一些产品通过 CocoaPods 链接，而其他产品通过 SPM 链接会导致重复/冲突符号和运行时 dyld 错误。迁移此类套件时，一次将**所有**从该套件中的 pods 移动到 SPM — 包括 Kotlin 不直接使用的 Swift 仅 pods。将 Swift 仅 pods 作为 `products` 条目添加（不需要 `importedClangModules`）。添加新产品后，重新运行 `integrateLinkagePackage` 以重新生成链接 Swift 包。

```kotlin
kotlin {
    // 保留现有目标
    iosArm64()
    iosSimulatorArm64()
    iosX64()

    swiftPMDependencies {
        iosMinimumDeploymentTarget = "16.0"

        swiftPackage(
            url = "https://github.com/owner/repo.git",
            version = "1.0.0",
            products = listOf("ProductName"),
        )
    }

    cocoapods {
        // ... 保留现有的 cocoapods 块，暂时
    }
}
```

### 3.3 将框架配置从 cocoapods 块移出

如果 `cocoapods` 块包含 `framework {}` 配置，将其移到每个目标的 `binaries` API 上。**建议 `isStatic = true`** — 动态框架已知存在与 SwiftPM 导入相关的边缘情况，可能导致链接器错误、dyld 错误或重复类警告：

```kotlin
listOf(iosArm64(), iosSimulatorArm64(), iosX64()).forEach { iosTarget ->
    iosTarget.binaries.framework { baseName = "Shared"; isStatic = true }
}
```

如果 `cocoapods.framework {}` 块包含 `export(project(...))` 或 `transitiveExport = true`，请在新 `binaries.framework {}` 块中保留这些内容——它们对于多模块项目至关重要，因为框架导出子模块。

### 3.4 处理 dev.gitlive/firebase-kotlin-sdk 和类似的 CocoaPods 时代 KMP 包装器

如果项目使用 `dev.gitlive:firebase-*` 或类似的 KMP 包装器库，需要执行两个额外的步骤：

**A. 切换到 `isStatic = true`** — 动态框架 + Firebase SPM = 运行时 `dyld` 异常。切换后：重新运行 `integrateLinkagePackage`，删除任何 "嵌入框架" 复制阶段，将链接器标志移动到 `OTHER_LDFLAGS`。

**B. 添加框架搜索路径** — 在 `build.gradle.kts` 中添加条件 `-F` 链接器选项，并在 Xcode 项目中添加匹配的 `FRAMEWORK_SEARCH_PATHS`。

参见 [common-pods-mapping.md](references/common-pods-mapping.md) § dev.gitlive 和 [troubleshooting.md](references/troubleshooting.md) 获取代码片段和完整产品列表。

### 3.5 添加选择加入注解

`swiftPackage()` 和 `localSwiftPackage()` DSL 函数使用 `@ExperimentalKotlinGradlePluginApi` 注解。添加此选择加入以抑制编译器警告：

```kotlin
@file:OptIn(org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi::class)
```

将此内容放在每个调用 `swiftPackage()` 或 `localSwiftPackage()` 的 `build.gradle.kts` 文件的顶部。

此外，为 Kotlin 源文件添加 cinterop 选择加入：

```kotlin
kotlin.compilerOptions {
    optIn.add("kotlinx.cinterop.ExperimentalForeignApi")
}
```

有关完整 DSL 参考，请参阅 [dsl-reference.md](references/dsl-reference.md)。

---

## Phase 4: Kotlin 源代码更新

### 导入命名空间公式

```
swiftPMImport.<group>.<module>.<ClassName>

其中：
- group: 声明 swiftPMDependencies 的模块的 `build.gradle.kts` `group` 属性，短横线 (-) → 点 (.)
- module: 声明 swiftPMDependencies 的模块的 Gradle 模块名称，短横线 (-) → 点 (.), 下划线 (_) 保留原样
- ClassName: Objective-C 类名 (FIR* 用于 Firebase, GMS* 用于 Google Maps)
```

**命名空间使用声明模块的 group+name，而不是导入模块的。** 这是代理最常见的错误。当模块 A 依赖于模块 B，并且模块 B 声明 `swiftPMDependencies` 时，模块 A 使用模块 B 的 group 和模块名称导入 SPM 类——不是模块 A 的。

### 示例转换——单个模块

```kotlin
// group = "org.jetbrains.kotlin.firebase.sample", module = "kotlin-library"

// 之前：
import cocoapods.FirebaseAnalytics.FIRAnalytics

// 之后：
import swiftPMImport.org.jetbrains.kotlin.firebase.sample.kotlin.library.FIRAnalytics
```

### 示例转换——多模块（仅链接 pods）

当消费模块因为子模块提供 cinterop 绑定而使用 `pod("GoogleMaps") { linkOnly = true }` 时：

```kotlin
// composeApp/App.kt — composeApp 依赖于 :google-maps Gradle 模块
// google-maps 的 group = "org.jetbrains.kotlin.google-maps", 模块名称 = "google-maps"
// google-maps 声明 swiftPMDependencies 使用 GoogleMaps

// 之前（在 composeApp 中）：
import cocoapods.GoogleMaps.GMSServices

// 之后——使用 google-maps 模块的命名空间，而不是 composeApp 的命名空间：
import swiftPMImport.org.jetbrains.kotlin.google.maps.google.maps.GMSServices
//                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^
//                    google-maps 的 group (短横线→点)  google-maps 的模块名称 (短横线→点)
```

导入路径**不使用** composeApp 的 group (`org.jetbrains.kotlin.compose.sample`)。它使用声明模块的标识，因为 cinterop 绑定是在那里生成的。

**导入扁平化：** Clang 模块名称（例如，`FirebaseFirestoreInternal`，`FirebaseAuth`）会从导入路径中消失——所有类都在相同的 `swiftPMImport.<group>.<module>` 前缀下扁平化，无论它们来自哪个库。例如，`cocoapods.FirebaseAuth.FIRAuth` 和 `cocoapods.FirebaseFirestoreInternal.FIRFirestore` 都会变成 `swiftPMImport.<group>.<module>.FIRAuth` 和 `swiftPMImport.<group>.<module>.FIRFirestore`。

### 保留捆绑 Klib 导入

> **关键：** 不要替换解析为第三方 KMP 库捆绑的 cinterop klibs 的 `cocoapods.*` 导入（在 Phase 1 步骤 1.3 中识别）。这些导入必须保持原样——`cocoapods` 前缀是库发布的 klib 中的包命名空间，而不是实际的 CocoaPods 依赖项。swiftPMDependencies cinterop 生成器会跳过依赖项 klib 已经提供的模块，因此 `swiftPMImport.*` 对于这些类将失败，显示 "未解析的引用"。

**示例**（使用 [KMPNotifier](https://github.com/mirzemehdi/KMPNotifier) 的项目）：
```kotlin
// 保留——解析到 kmpnotifier 的捆绑 cinterop klib
import cocoapods.FirebaseMessaging.FIRMessaging
```

### 批量替换

在所有 Kotlin 源文件中使用正则表达式查找和替换，**排除 Phase 1 步骤 1.3 中标识的导入**。在多模块项目中，使用该模块的 group 和名称分别对每个模块运行替换：

```
查找：    cocoapods\.\w+\.
替换：    swiftPMImport.<声明模块的.group>.<声明模块的.name>.
```

批量替换后，**手动恢复** 应保留的任何 `cocoapods.*` 导入（来自捆绑的 klibs）。

**查找正确的导入路径：** 运行 `./gradlew :moduleName:compileKotlinIosSimulatorArm64` - 错误显示可用类。

---

## Phase 5: iOS 项目重新配置

### 5.1 获取迁移命令

构建 CocoaPods 工作区以获取迁移命令：

```bash
cd /path/to/iosApp

xcodebuild -scheme "$(echo -n *.xcworkspace | python3 -c 'import sys, json; from subprocess import check_output; print(list(set(json.loads(check_output(["xcodebuild", "-workspace", sys.stdin.readline(), "-list", "-json"]))["workspace"]["schemes"]) - set(json.loads(check_output(["xcodebuild", "-project", "Pods/Pods.xcodeproj", "-list", "-json"]))["project"]["schemes"]))[0])')" -workspace *.xcworkspace -destination 'generic/platform=iOS Simulator' ARCHS=arm64 | grep -A5 'What went wrong'
```

构建输出将包含类似以下命令：
```bash
XCODEPROJ_PATH='/path/to/project/iosApp.xcodeproj' GRADLE_PROJECT_PATH=':shared' '/path/to/project/gradlew' -p '/path/to/project' ':shared:integrateEmbedAndSign' ':shared:integrateLinkagePackage'
```

运行此命令。它修改 `.xcodeproj` 以在构建期间触发 `embedAndSignAppleFrameworkForXcode`。`integrateLinkagePackage` 是一次性设置——不需要将其添加为构建阶段。如果 `integrateEmbedAndSign` 被跳过，请检查 EmbedAndSign 禁用器（Phase 1 步骤 1.2）——首先删除它们，然后重新运行。

**验证 `embedAndSignAppleFrameworkForXcode` 是否处于活动状态：** 运行集成后，检查 `project.pbxproj` 中的构建阶段脚本。如果 `embedAndSignAppleFrameworkForXcode` 被注释掉（以 `#` 开头），则取消注释它。

`integrateLinkagePackage` 任务在 `<iosDir>/` 生成 `KotlinMultiplatformLinkedPackage/` — 一个本地 Swift 包，它镜像你的 `products` 列表并确保 SPM 库链接到最终二进制文件。

运行集成任务后，**禁用用户脚本沙盒** (`ENABLE_USER_SCRIPT_SANDBOXING = NO`) 在 `.xcodeproj` 中：

```bash
sed -i '' 's/ENABLE_USER_SCRIPT_SANDBOXING = YES/ENABLE_USER_SCRIPT_SANDBOXING = NO/g' "$XCODEPROJ_PATH/project.pbxproj"
```

如果该设置不存在（Xcode 默认为 YES），请将 `ENABLE_USER_SCRIPT_SANDBOXING = NO;` 添加到应用程序目标的 `buildSettings` 部分中。然后重新启动 Gradle 守护进程：`./gradlew --stop`

**替代方案（如果 xcodebuild 方法失败）：** 参见 [troubleshooting.md](references/troubleshooting.md) § "手动集成命令发现" 以获取备用脚本，直接发现路径并运行集成任务。

### 5.2 更新 Crashlytics dSYM 上传脚本（如果适用）

如果项目使用 FirebaseCrashlytics 并具有 dSYM 上传运行脚本阶段（在 Phase 1 步骤 11 中标识），请将脚本路径从 `${PODS_ROOT}/FirebaseCrashlytics/upload-symbols` 更新为 `"${BUILD_DIR%/Build/*}/SourcePackages/checkouts/firebase-ios-sdk/Crashlytics/run"`。参见 [troubleshooting.md](references/troubleshooting.md) § "Firebase Crashlytics: dSYM 上传脚本" 和 [common-pods-mapping.md](references/common-pods-mapping.md) 获取完整脚本和输入文件列表。

### 5.3 解除 CocoaPods 集成

**选项 A：完全解除集成**（如果 CocoaPods 仅用于 KMP 依赖项）：

在删除文件之前，运行 `git status --short` 并验证路径。如有不确定，请将文件移动到备份位置，而不是立即删除。

```bash
cd /path/to/iosApp
pod deintegrate
rm -rf Podfile Podfile.lock Pods/
# 删除与您的应用程序 xcodeproj 名称匹配的工作区
XCODEPROJ_NAME=$(basename "$(find . -maxdepth 1 -name "*.xcodeproj" -type d | grep -v Pods | head -1)" .xcodeproj)
rm -rf "${XCODEPROJ_NAME}.xcworkspace"
# 返回项目根目录
cd ..
# 删除迁移的模块 podspec 仅（例如，shared.podspec）
# 如果未知，列出候选者并显式删除匹配的：
ls -1 *.podspec
# rm -f shared.podspec
```

此清理片段是自包含的，并且不依赖于之前一次性迁移命令中的 `XCODEPROJ_PATH` 或 `GRADLE_PROJECT_PATH` 在您的 shell 中可用。

如果 `pod deintegrate` 不可用，请参见 [troubleshooting.md](references/troubleshooting.md) § "手动从 pbxproj 中解除 CocoaPods 集成" 以获取要删除的完整引用列表。还请从 `.gitignore` 中删除 `Pods/` 并删除 `.xcworkspace` 目录。

**选项 B：部分删除**（如果其他非 KMP CocoaPods 依赖项仍然存在）：

仅从 `Podfile` 中删除 KMP pod 行并重新运行 pod install：

```ruby
target 'iosApp' do
  # 删除此行：
  pod 'shared', :path => '../shared'
  # 保留其他非 KMP pods
end
```

```bash
cd /path/to/iosApp && pod install
```

> **提示：** 考虑将剩余的 pods 迁移到 SPM——大多数流行的 iOS 库原生支持它。通过 Xcode 的 "File → Add Package Dependencies" 添加它们，然后一旦所有 pods 都被替换，完全解除 CocoaPods 集成。

### 5.4 手动集成（如果自动失败）

参见 [troubleshooting.md](references/troubleshooting.md) § "手动 Xcode 集成步骤" 以获取 5 步手动设置（构建阶段，沙盒，链接）。

---

## Phase 6: 从 Gradle 中删除 CocoaPods

现在 iOS 项目已重新配置，从所有使用它的模块中删除 CocoaPods 插件和块（而不仅仅是主模块）：

### 6.1 删除 CocoaPods 插件

从每个使用它的模块的 `plugins {}` 中删除 `kotlin("native.cocoapods")` 或 `alias(libs.plugins.kotlinCocoapods)`：

```kotlin
plugins {
    // 删除：kotlin("native.cocoapods")  或  alias(libs.plugins.kotlinCocoapods)
    alias(libs.plugins.kotlinMultiplatform)  // 保留
}
```

如果所有模块都已迁移，请也从 `gradle/libs.versions.toml` 中删除 `kotlinCocoapods` 插件条目：

```toml
[plugins]
# 删除：kotlinCocoapods = { id = "org.jetbrains.kotlin.native.cocoapods", version.ref = "kotlin" }
```

### 6.2 删除 cocoapods 块

从 `build.gradle.kts` 中删除整个 `cocoapods { ... }` 块。Phase 3 中添加的 `swiftPMDependencies {}` 块和 `binaries.framework {}` 配置取代了它。还删除模块目录中生成的任何 `.podspec` 文件（例如，`shared/shared.podspec`）——这些文件由 CocoaPods 插件生成，不再需要。

### 6.3 删除已弃用的 gradle.properties 条目

如果在 Phase 1.1 中找到，从 `gradle.properties` 中删除：

```properties
# 删除——迁移到 CocoaPods 后不再需要 (KT-64096)
kotlin.apple.deprecated.allowUsingEmbedAndSignWithCocoaPodsDependencies=true
```

### 6.4 清理 CocoaPods 相关的 extras

审查 Phase 1 步骤 12 中标识的 extras。Podspec 元数据、`noPodspec()`、CocoaPods 任务挂钩和 `Pods.xcodeproj` 补丁代码**可以安全删除**，无需用户咨询。非标准 pod 配置（`extraOpts`，`moduleName`）、自定义 cinterop `defFile` 设置和 CocoaPods 特定的编译器/链接器标志**需要分析**——如有不确定，请咨询用户是否 SPM 自动处理它们。

参见 [cocoapods-extras-patterns.md](references/cocoapods-extras-patterns.md) 获取完整分类列表和示例。

---

## Phase 7: 验证

**直到应用程序成功构建才停止。** 此阶段是迭代的——如果任何步骤失败，请诊断错误，修复它（参考 [troubleshooting.md](references/troubleshooting.md) 并重新检查 Phases 2–6），然后重新运行失败的步骤。重复直到构建成功或问题明显超出迁移范围（预迁移错误，不相关的工具问题）。**不要**在构建成功之前编写迁移报告（Phase 8）。

### 7.1 编译 Kotlin 代码

编译迁移的模块以验证 Kotlin 源代码是否正确：

```bash
./gradlew :moduleName:compileKotlinIosSimulatorArm64
```

如果编译失败并显示未解析的引用，请检查导入转换（Phase 4）和 SwiftPM 依赖项声明（Phase 3.2）。常见原因：缺少 `importedClangModules`、Clang 模块名称错误、保留的捆绑 klib 导入应被转换（或反之）。

### 7.2 链接框架

```bash
./gradlew :moduleName:linkDebugFrameworkIosSimulatorArm64
```

如果链接失败，请检查是否声明了所有必需的 SPM 产品，并且版本约束正确解析。链接错误关于缺少符号通常表示产品被遗漏了 `swiftPMDependencies` 或版本不匹配导致 API 移除。

### 7.3 构建 iOS/macOS Xcode 项目

在 Gradle 步骤成功后，构建 Xcode 项目以验证整个应用程序是否可以编译。如果所有 CocoaPods 已删除（选项 A），请使用 `-project *.xcodeproj`；如果非 KMP CocoaPods 仍然存在（选项 B），请使用 `-workspace *.xcworkspace`：

```bash
cd /path/to/iosApp
# 发现方案并构建（根据需要替换 -project/-workspace；对于 macOS 使用 -destination 'platform=macOS')：
xcodebuild -project *.xcodeproj -list -json 2>/dev/null | python3 -c "import sys,json; schemes=json.load(sys.stdin)['project']['schemes']; [print(s) for s in schemes]"
xcodebuild -project *.xcodeproj -scheme "<AppScheme>" -destination 'generic/platform=iOS Simulator' ARCHS=arm64 build
```

**如果 `checkSandboxAndWriteProtection` 失败**——沙盒未在 Phase 5.1 中禁用。返回并应用 Phase 5.1 中的沙盒修复，然后重试。

**如果迁移前的构建未验证**（Phase 1.0 回退使用），请警告用户：
> 注意：迁移前的构建无法完全验证。如果现在出现构建错误，其中一些可能是预迁移问题，与迁移无关。将错误与预迁移构建输出进行比较，以区分迁移问题与先前的错误。

### 如果构建失败

**不要回滚迁移。** 读取错误日志，重新检查 Phases 2-6，并参考 [troubleshooting.md](references/troubleshooting.md)。如有不确定，请向用户提供选项——不要无声地撤销迁移工作。修复问题并重新运行失败的验证步骤。重复迭代，直到构建成功或问题明显超出迁移范围（预迁移错误，不相关的工具问题）。

报告必须包含：
1. **迁移前状态** — CocoaPods 依赖（名称、版本、`linkOnly`），框架配置，`cocoapods.*` 导入，非 KMP pod，非典型配置
2. **迁移步骤** — 每个阶段的精确变更，对于非平凡的变更提供前后代码片段
3. **导入转换** — 每个导入变更的表格，清晰标记保留的 `cocoapods.*` 导入以及哪些捆绑的 klib 提供它们
4. **遇到的问题** — 结构化的 `错误 #N` 条目：阶段、精确症状、根本原因、修复方案、通用性标记
5. **非平凡决策** — `isStatic` 变更，保留的导入，框架搜索路径，权衡方案
6. **变更的文件** — 按类型分组（Gradle、Kotlin、Xcode、创建、删除）的完整列表

---

## 额外资源

- [DSL 参考](references/dsl-reference.md) - 完整 swiftPMDependencies 语法
- [常见 Pod 映射](references/common-pods-mapping.md) - Pod 到 SPM 映射表
- [CocoaPods 附加模式](references/cocoapods-extras-patterns.md) - CocoaPods 补丁的检测和清理模式
- [故障排除](references/troubleshooting.md) - 问题、解决方案、回滚
- [迁移报告模板](references/migration-report-template.md) - 迁移后报告模板
