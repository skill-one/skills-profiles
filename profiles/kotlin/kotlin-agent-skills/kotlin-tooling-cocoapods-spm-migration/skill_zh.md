# CocoaPods to SwiftPM 迁移指南

将 Kotlin Multiplatform 项目从 `kotlin("native.cocoapods")` 迁移到 `swiftPMDependencies {}` DSL。

## 要求

- **Kotlin**: 2.4.0-Beta2 或更高版本（首次发布 `swiftPMDependencies` 支持的版本，可在 Maven Central 上获取）
- **Xcode**: 16.4 或 26.0+
- **iOS 部署目标**: 推荐 16.0+

## 迁移概述

**重要提示**: 在第 6 步之前，请保持 `cocoapods {}` 块和插件处于活动状态。迁移过程会先添加 `swiftPMDependencies {}` 与现有的 CocoaPods 设置一起，然后重新配置 Xcode，最后才移除 CocoaPods。

| 步骤 | 操作 |
|------|------|
| 1 | 分析现有的 CocoaPods 配置 |
| 2 | 更新 Gradle 配置（仓库、Kotlin 版本） |
| 3 | 在现有的 `cocoapods {}` 旁边添加 `swiftPMDependencies {}` |
| 4 | 转换 Kotlin 导入 |
| 5 | 重新配置 iOS 项目并解集成 CocoaPods |
| 6 | 从 Gradle 中移除 CocoaPods 插件 |
| 7 | 验证 Gradle 构建和 Xcode 项目构建 |
| 8 | 编写 MIGRATION_REPORT.md |

---

## 第 1 步：迁移前分析

### 1.0 验证项目构建

在开始迁移之前，确定要迁移的模块并确认其成功编译。

1. **找到使用 CocoaPods 的模块** — 查找包含 `cocoapods` 的 `build.gradle.kts` 文件：
   ```bash
   grep -rl "cocoapods" --include="build.gradle.kts" .
   ```
   从路径中提取模块名称（例如，`./shared/build.gradle.kts` → 模块名称是 `shared`）。注意：多个模块可能使用 CocoaPods — 记录所有模块。通常只有生成链接到 iOS 应用的框架的模块需要 `swiftPMDependencies`；其他模块只需要移除 CocoaPods（第 6 步）。

2. **编译 Kotlin 代码** — 运行该模块的 Kotlin 编译任务以验证 Kotlin 源代码编译：
   ```bash
   ./gradlew :moduleName:compileKotlinIosSimulatorArm64
   ```
   将 `moduleName` 替换为模块的目录名称（例如，`:shared:compileKotlinIosSimulatorArm64`）。这比完整的 `build`（它还会运行发布链接）更快，并且足以验证 Kotlin 代码的正确性。

3. **构建 iOS 应用（可选）** — 尝试定位 Xcode 项目并构建它以确认整个应用编译：
   ```bash
   # 定位 Xcode 项目
   find . -name "*.xcworkspace" -not -path "*/Pods/*" -maxdepth 2
   # 构建（替换方案名称为实际的应用方案）
   cd /path/to/iosApp
   xcodebuild -workspace *.xcworkspace -scheme "<AppScheme>" -destination 'generic/platform=iOS Simulator' ARCHS=arm64
   ```
   如果用户想跳过 Xcode 构建，或者找不到 Xcode 项目，可以不进行此步骤 — 第 2 步的 Kotlin 编译就足够继续。

4. **如果 Kotlin 编译失败**，请要求用户：
   - 提供正确的 Gradle 命令以验证模块构建，或者
   - 确认模块处于工作状态，并且可以继续

   如果用户确认而不提供构建命令，**记录迁移前构建无法验证**，并在迁移结束时（第 7 步）警告用户。

### 1.0a 确认 Kotlin 版本支持 Swift 导入

从 `gradle/libs.versions.toml`（或 `build.gradle.kts`）读取当前 Kotlin 版本。

**如果项目已经使用 Kotlin 2.4.0-Beta2 或更高版本** → 记录版本并跳过第 2.1 步（不需要版本更改）。

**如果项目使用较旧的 Kotlin 版本** → 第 2.1 步将将其升级到 `2.4.0-Beta2`（首次发布支持 `swiftPMDependencies` 的版本，可在 Maven Central 上获取 — 无需自定义仓库）。警告用户："⚠️ Kotlin 版本跳跃 — 跨小版本升级可能会引入与迁移无关的破坏性更改。推荐：先更新，验证它构建，然后重新运行此迁移。" 如果用户确认，请继续。

### 1.1 检查已弃用的 CocoaPods 工作绕过属性

在 `gradle.properties` 中搜索已弃用的属性：

```properties
kotlin.apple.deprecated.allowUsingEmbedAndSignWithCocoaPodsDependencies=true
```

此属性是一个工作绕过（参见 [KT-64096](https://youtrack.jetbrains.com/issue/KT-64096)），用于使用 `embedAndSign` 与 CocoaPods 依赖项一起使用的项目。它抑制了关于不受支持配置的错误，该错误会导致运行时崩溃或符号重复。迁移到 SwiftPM 导入后，此属性不再需要，并且在第 6 步**必须**移除。如果找到，请记录它。

### 1.2 检查 EmbedAndSign 禁用器

在所有 `build.gradle.kts` 文件中搜索禁用 `EmbedAndSign` 任务（例如，`TaskGraph.whenReady` 过滤器，`tasks.matching` 块）。这是一个 CocoaPods 时代的工作绕过，它**会破坏迁移**，因为 `integrateEmbedAndSign`（在第 5 步中需要）也会被禁用。记录任何此类代码 — 它们**必须**在第 6 步中移除，可能需要更早移除。参见 [troubleshooting.md](references/troubleshooting.md) § "`integrateEmbedAndSign` Skipped" 以获取模式。

### 1.3 检查捆绑了 cinterop klibs 的第三方 KMP 库

一些 KMP 库使用 `cocoapods.*` 包命名空间捆绑了预构建的 cinterop klibs。迁移后，swiftPMDependencies cinterop 生成器会检测到这些现有的绑定，并且**会跳过为这些 Clang 模块生成新的绑定**以避免重复。这意味着 `cocoapods.*` 导入对于这些模块**必须保持原样** — 它们解析为第三方库的捆绑 klib，而不是实际的 CocoaPods。

**已知使用捆绑 `cocoapods.*` klibs 的库:**

| 库 | Maven 产物 | 捆绑 klib 命名空间 | 提供的类 |
|-----|------------|------------------|----------|
| [KMPNotifier](https://github.com/mirzemehdi/KMPNotifier) | `io.github.mirzemehdi:kmpnotifier` | `cocoapods.FirebaseMessaging` | `FIRMessaging`, `FIRMessagingAPNSTokenType`, 等. |

**如何检测:** 搜索 Gradle 依赖声明以识别已知库，然后交叉引用它们捆绑的命名空间与步骤 4 中找到的 `import cocoapods.*` 语句。标记任何匹配项 — 这些导入在步骤 4 中**不会**被转换。

如果不确定某个第三方 KMP 库是否捆绑 cinterop klibs，检查项目是否在 `Podfile` 中有 `linkOnly = true` 的 pod 依赖项 — 这是一个强烈指示该库为这些类提供了自己的 klib。

要检查 klib 内容并验证捆绑绑定，请参阅 [troubleshooting.md](references/troubleshooting.md) § "Third-Party KMP Libraries with Bundled Klibs"。

**记录:**

1. **CocoaPods 配置** - 在 `build.gradle.kts` 文件中搜索 `cocoapods`
2. **Pod 依赖项** - 从 `cocoapods {}` 块中提取 pod 名称、版本
3. **框架配置** - 记录 `baseName`, `isStatic`, 部署目标从 `cocoapods.framework {}`
4. **linkOnly pods** - 记录使用 `linkOnly = true` 声明的 pods。这些有两个常见模式:
   - **KMP 包装库**（例如，`dev.gitlive:firebase-*`）：包装库提供 Kotlin API，而 pod 仅链接。参见 [common-pods-mapping.md](references/common-pods-mapping.md) 了解影响。
   - **多模块项目**: 消费模块声明 `linkOnly = true`，因为子模块已经提供了该 pod 的 cinterop 绑定。在 SwiftPM 中，`swiftPackage()` 声明应该**仅**在直接使用 pod 的子模块中。消费模块**不能**重新声明相同的包 — 它只需要一个没有这些包的 `swiftPMDependencies {}` 块（如果所有 pods 都是 `linkOnly`，则为空）。**导入命名空间含义**: 当消费模块导入来自子模块的 `swiftPMDependencies` 的 SPM 类时，导入路径使用**子模块**的组名称和模块名称作为命名空间（参见第 4 步导入命名空间公式）。
5. **Kotlin 导入** - 查找所有 `import cocoapods.*` 语句。交叉引用步骤 1.3 以识别哪些导入来自捆绑的 klibs（必须保留），哪些来自直接 pod cinterop（必须转换）。
6. **将 pods 映射到 SPM** - 参见 [common-pods-mapping.md](references/common-pods-mapping.md)
7. **定位 iOS 项目目录** - 找到包含 `Podfile` 和 `.xcworkspace` 的目录：
   ```bash
   find . -name "Podfile" -type f
   ```
   记录此路径（例如，`iosApp/`, `ios/`, 或项目根目录）- 需要在第 5 步中使用。
8. **检查非 KMP CocoaPods** - 确定项目是否使用 CocoaPods 依赖项除了 KMP 之外。这会影响第 5 步中的清理策略。
9. **交叉引用 Podfile 与 `cocoapods {}` 块** - 解析 `Podfile` 并比较其 pod 条目与 Gradle `cocoapods {}` 块中声明的 pods。记录任何存在于 `Podfile` 但**不在** `cocoapods {}` 块中的依赖项。这些 Podfile 仅依赖项仍然通过 CocoaPods 链接到应用中，并且必须迁移到 `swiftPMDependencies` — 默默删除会导致运行时出现难以理解的链接错误。
10. **检查 Xcode 构建阶段** - 打开 `.xcodeproj` 的 `project.pbxproj` 并搜索 Gradle 构建阶段脚本。检查 `embedAndSignAppleFrameworkForXcode` 是否存在但**被注释掉**（以 `#` 开头）。如果被注释掉，则在第 5 步中必须取消注释 — `integrateEmbedAndSign` 任务可能会自动处理此问题。
11. **检查现有的 Crashlytics dSYM 上传脚本** - 如果使用 FirebaseCrashlytics，请搜索 `project.pbxproj` 中的 dSYM 上传 shell 脚本阶段。记录其当前路径（CocoaPods 时代的脚本引用 `${PODS_ROOT}/FirebaseCrashlytics/upload-symbols`）。这必须更新为 SPM 路径，在第 5 步中。
12. **识别 CocoaPods 相关的额外内容** - 在所有 `build.gradle.kts` 文件中搜索超出标准 `cocoapods {}` 块的 CocoaPods 工作绕过（例如，`podInstall` 的自定义任务挂钩，`Pods.xcodeproj` 补丁，podspec 元数据，`extraSpecAttributes`, `noPodspec()`, 等.）。参见 [cocoapods-extras-patterns.md](references/cocoapods-extras-patterns.md) 获取完整模式列表。记录所有发现的内容 — 这些将在第 6 步中处理。

---

## 第 2 步：Gradle 配置

**重要范围说明**: 在此迁移过程中**不要**升级 Gradle 包装器版本，更新 KSP 或更新任何其他依赖项。这些是单独的问题，不在此范围内。仅更改以下内容。

### 2.1 更新 Kotlin 版本

**如果项目已经使用 Kotlin 2.4.0-Beta2 或更高版本** → 记录版本并跳过第 2.1 步（不需要版本更改）。

在 `gradle/libs.versions.toml` 中将 Kotlin 更新为 `2.4.0-Beta2`（或最新支持 Swift 导入的发布版本）：

```toml
[versions]
kotlin = "2.4.0-Beta2"
```

`2.4.0-Beta2` 可在 Maven Central 上获取 — 无需自定义仓库。

---

## 第 3 步：添加 swiftPMDependencies（保留 CocoaPods）

**在此步骤之前，请勿移除 `cocoapods {}` 块或 `kotlin("native.cocoapods")` 插件。** 先在现有的 CocoaPods 设置旁边添加 `swiftPMDependencies {}`，然后重新配置 Xcode，最后才移除 CocoaPods。

### 3.1 添加 group 属性

```kotlin
group = "org.example.myproject"  // 必须用于导入命名空间
```

**Compose 资源警告:** 如果项目使用 Compose Multiplatform 资源（`org.jetbrains.compose` 插件或 `compose.resources`），则 `group` 属性也用作生成资源访问器的命名空间（例如，`Res.string.*`, `Res.drawable.*`）。如果 `group` 在 `build.gradle.kts` 中已经存在，则**不要**更改它。如果你第一次添加 `group`，则警告用户现有的 Compose 资源访问器调用点在整个项目中将更改命名空间，可能需要更新。

### 3.2 在 cocoapods 旁边添加 swiftPMDependencies 块

对于每个 pod 依赖项，添加等效的 SwiftPM 包声明。使用 [common-pods-mapping.md](references/common-pods-mapping.md) 将每个 pod 映射到其 SPM 包 URL、产品名称和 `importedClangModules`。

**版本保留:** 在迁移过程中**不要**更改依赖项版本。使用与 `cocoapods {}` 块中指定的完全相同的版本。更改版本可能会导致解析到不同的库构建，从而破坏 cinterop API（移除符号，更改签名）并引入与迁移本身无关的问题。

| CocoaPods 版本规范 | SPM 等效 | 示例 |
|------------------------|---------------|---------|
| `version = "1.2.3"` (exact) | `version = "1.2.3"` (simple) or `exact("1.2.3")` (typed) | `pod("GoogleMaps") { version = "10.3.0" }` → `version = "10.3.0"` |
| `version = "~> 1.2"` (optimistic) | `version = "1.2.0"` (simple) or `from("1.2.0")` (typed) | `pod("FirebaseAuth") { version = "~> 12.5" }` → `version = "12.5.0"` |
| 未指定版本 | 询问用户要固定哪个版本 | 询问用户要使用哪个版本 |

**两种 API 形式:** DSL 有一个简单的字符串 API 和一个类型化 API。**对于大多数包使用简单的字符串 API**:
```kotlin
swiftPackage(
    url = "https://github.com/owner/repo.git",
    version = "1.0.0",
    products = listOf("ProductName"),
)
```
简单的 API 会自动默认 `importedClangModules` 为 `products` 列表。仅在需要精确版本固定、平台约束或显式 Clang 模块控制时使用类型化 API（使用 `url()`, `exact()`, `product()` 包装器）。参见 [dsl-reference.md](references/dsl-reference.md) 获取类型化 API。

**关键概念:** `products` = SPM 产品名称（控制链接）。`importedClangModules` = Clang 模块名称用于 cinterop 绑定（仅在 `discoverClangModulesImplicitly = false` 时）。`discoverClangModulesImplicitly` 默认为 `true`（为所有 Clang 模块生成绑定）；当传递的 C/C++ 模块失败 cinterop（Firebase, gRPC），则将其设置为 `false`，然后显式列出需要的模块。

**重要提示:** SPM 产品名称和 Clang 模块名称不总是匹配。始终参考 [common-pods-mapping.md](references/common-pods-mapping.md) 获取正确值。

**Podfile 仅依赖项:** 如果第 1 步步骤 9 确定了存在于 `Podfile` 但不在 Gradle `cocoapods {}` 块中的依赖项，则这些依赖项也必须添加到 `swiftPMDependencies` 作为 `products` 条目。即使 KMP 模块没有声明它们，它们也通过 CocoaPods 链接到应用中，并且可能需要应用才能构建。查找每个 Podfile 仅依赖项的 SPM 包 URL 并将其作为 `swiftPackage()` 添加，至少包含其 `products`。如果这些 pods 中的任何 pod 通过 cinterop 使用（检查是否有 `import cocoapods.*` 语句引用它们），也添加 `importedClangModules`。

**不要在 CocoaPods 和 SPM 中混合相同的库套件。** 共享相同仓库的库（例如，所有 Firebase 产品）共享传递依赖项。将一些产品通过 CocoaPods 链接，而其他产品通过 SPM 链接会导致运行时出现重复/冲突的符号和 dyld 崩溃。当迁移此类套件时，请一次性将**所有** pods 从该套件迁移到 SPM — 包括 Kotlin 不直接使用的 Swift 仅 pods。将 Swift 仅 pods 作为 `products` 条目添加（不需要 `importedClangModules`）。添加新产品后，重新运行 `integrateLinkagePackage` 以重新生成链接的 Swift 包。

```kotlin
kotlin {
    // 保留现有的目标
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

### 3.3 将框架配置移出 cocoapods 块

如果 `cocoapods` 块包含 `framework {}` 配置，将其移动到每个目标的 `binaries` API 上。**推荐 `isStatic = true`** — 动态框架已知存在与 SwiftPM 导入相关的边缘情况，可能导致链接器错误、dyld 崩溃或重复类警告：

```kotlin
listOf(iosArm64(), iosSimulatorArm64(), iosX64()).forEach { iosTarget ->
    iosTarget.binaries.framework { baseName = "Shared"; isStatic = true }
}
```

如果 `cocoapods.framework {}` 块包含 `export(project(...))` 或 `transitiveExport = true`，则保留这些设置在新 `binaries.framework {}` 块中 — 它们对于多模块项目至关重要，这些项目导出子模块。

### 3.4 处理 dev.gitlive/firebase-kotlin-sdk 和类似的 CocoaPods 时代 KMP 包装库

如果项目使用 `dev.gitlive:firebase-*` 或类似的 KMP 包装库，需要执行两个附加步骤：

**A. 切换到 `isStatic = true`** — 动态框架 + Firebase SPM = 运行时 dyld 崩溃。切换后：重新运行 `integrateLinkagePackage`，移除任何 "Embed Frameworks" 复制阶段，将链接器标志移动到 `OTHER_LDFLAGS`。

**B. 添加框架搜索路径** — 在 `build.gradle.kts` 中添加条件 `-F` 链接器选项，并在 Xcode 项目中添加匹配的 `FRAMEWORK_SEARCH_PATHS`。

参见 [common-pods-mapping.md](references/common-pods-mapping.md) 和 [troubleshooting.md](references/troubleshooting.md) 获取代码片段和完整产品列表。

### 3.5 添加 opt-in 注释

`swiftPackage()` 和 `localSwiftPackage()` DSL 函数使用 `@ExperimentalKotlinGradlePluginApi` 注释。在每个调用 `swiftPackage()` 或 `localSwiftPackage()` 的 `build.gradle.kts` 文件顶部添加此 opt-in：

```kotlin
@file:OptIn(org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi::class)
```

还添加 Kotlin 源文件的 cinterop opt-in：

```kotlin
kotlin.compilerOptions {
    optIn.add("kotlinx.cinterop.ExperimentalForeignApi")
}
```

对于完整 DSL 参考，请参阅 [dsl-reference.md](references/dsl-reference.md).

---

## 第 4 步：Kotlin 源代码更新

### 导入命名空间公式

```
swiftPMImport.<group>.<module>.<ClassName>

其中:
- group: 声明 swiftPMDependencies 的模块的 `build.gradle.kts` `group` 属性，连字符 (-) → 点 (.)。
- module: 声明 swiftPMDependencies 的模块的 Gradle 模块名称，连字符 (-) → 点 (.), 下划线 (_) 保留为原样。
- ClassName: Objective-C 类名（FIR* 用于 Firebase, GMS* 用于 Google Maps）
```

**命名空间使用声明 swiftPMDependencies 的模块的组名称和模块名称，而不是导入模块的。** 这是最常见的错误。当模块 A 依赖于模块 B，并且模块 B 声明 `swiftPMDependencies` 时，模块 A 导入 SPM 类使用模块 B 的组名称和模块名称 — **不是**模块 A 的。

### 示例转换 — 单个模块

```kotlin
// group = "org.jetbrains.kotlin.firebase.sample", module = "kotlin.library"

// 之前:
import cocoapods.FirebaseAnalytics.FIRAnalytics

// 之后:
import swiftPMImport.org.jetbrains.kotlin.firebase.sample.kotlin.library.FIRAnalytics
```

### 示例转换 — 多模块（linkOnly pods）

当消费模块有 `pod("GoogleMaps") { linkOnly = true }`，因为子模块已经提供了 cinterop 绑定时：

```kotlin
// composeApp/App.kt — composeApp 依赖于 :google-maps Gradle 模块
// google-maps 有 group = "org.jetbrains.kotlin.google-maps", module name = "google-maps"
// google-maps 声明 swiftPMDependencies 与 GoogleMaps

// 之前 (在 composeApp):
import cocoapods.GoogleMaps.GMSServices

// 之后 — 使用 google-maps 模块的命名空间，而不是 composeApp 的命名空间:
import swiftPMImport.org.jetbrains.kotlin.google.maps.google.maps.GMSServices
//                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^
// google-maps 的组 (连字符→点)  google-maps 的模块名称 (连字符→点)
```

导入路径**不**使用 Clang 模块名称（例如，`FirebaseFirestoreInternal`, `FirebaseAuth`）— 所有类都展平在相同的 `swiftPMImport.<group>.<module>` 前缀下，无论它们来自哪个库。例如，`cocoapods.FirebaseAuth.FIRAuth` 和 `cocoapods.FirebaseFirestoreInternal.FIRFirestore` 都变成 `swiftPMImport.<group>.<module>.FIRAuth` 和 `swiftPMImport.<group>.<module>.FIRFirestore`.

### 保留捆绑 Klib 导入

> **关键:** **不要**替换解析为第三方 KMP 库捆绑 cinterop klibs 的 `cocoapods.*` 导入。这些导入必须保持原样 — `cocoapods` 前缀是库发布的 klib 中的包命名空间，而不是实际的 CocoaPods 依赖项。swiftPMDependencies cinterop 生成器会检测到这些现有的绑定，并且会跳过为这些 Clang 模块生成新的绑定以避免重复。这意味着 `cocoapods.*` 导入对于这些模块**必须保持原样** — 它们解析为第三方库的捆绑 klib，而不是实际的 CocoaPods。

**示例**（项目使用 [KMPNotifier](https://github.com/mirzemehdi/KMPNotifier)）:
```kotlin
// 保留 — 解析为 kmpnotifier 的捆绑 klib
import cocoapods.FirebaseMessaging.FIRMessaging
```

### 批量替换

使用正则表达式查找和替换所有 Kotlin 源文件，**排除**步骤 1.3 中识别的导入。在多模块项目中，使用该模块的组名称和名称分别对每个模块运行替换（使用该模块的组名称和名称）：

```
查找:    cocoapods\.\w+\.
替换:    swiftPMImport.<declaring.module.group>.<declaring.module.name>.
```

替换后，**手动恢复**任何应保留的 `cocoapods.*` 导入（来自捆绑的 klibs）。

**查找正确的导入路径:** 运行 `./gradlew :moduleName:compileKotlinIosSimulatorArm64` - 错误显示可用类。

---

## 第 5 步：iOS 项目重新配置

### 5.1 获取迁移命令

构建 CocoaPods 工作区以获取迁移命令：

```bash
cd /path/to/iosApp

xcodebuild -scheme "$(echo -n *.xcworkspace | python3 -c 'import sys, json; from subprocess import check_output; print(list(set(json.loads(check_output(["xcodebuild", "-workspace", sys.stdin.readline(), "-list", "-json"]))["workspace"]["schemes"]) - set(json.loads(check_output(["xcodebuild", "-project", "Pods/Pods.xcodeproj", "-list", "-json"]))["project"]["schemes"]) - set(json.loads(check_output(["xcodebuild", "-workspace", sys.stdin.readline(), "-list", "-json"]))["workspace"]["schemes"]) - set(json.loads(check_output(["xcodebuild", "-project", "Pods/Pods.xcodeproj", "-list", "-json"]))["project"]["schemes"]))[0])')" -workspace *.xcworkspace -destination 'generic/platform=iOS Simulator' ARCHS=arm64 | grep -A5 'What went wrong'
```

构建输出将包含类似以下命令：
```bash
XCODEPROJ_PATH='/path/to/project/iosApp.xcodeproj' GRADLE_PROJECT_PATH=':shared' '/path/to/project/gradlew' -p '/path/to/project' ':shared:integrateEmbedAndSign' ':shared:integrateLinkagePackage'
```

运行此命令。它修改 `.xcodeproj` 以在构建过程中触发 `embedAndSignAppleFrameworkForXcode`。`integrateLinkagePackage` 是一次性设置 — 它不需要添加为构建阶段。如果 `integrateEmbedAndSign` 被跳过，请检查 EmbedAndSign 禁用器（第 5 步）— 移除它们后，重新运行。

**验证 `embedAndSignAppleFrameworkForXcode` 是否激活:** 运行迁移后，检查构建阶段脚本中的 `project.pbxproj`。如果 `embedAndSignAppleFrameworkForXcode` 被注释掉（以 `#` 开头），则必须取消注释。

`integrateLinkagePackage` 任务会生成 `KotlinMultiplatformLinkedPackage/` 在 `<iosDir>/` — 一个本地 Swift 包，它镜像你的 `products` 列表，并确保 SPM 库链接到最终二进制文件中。

运行集成任务后，**禁用用户脚本沙盒** (`ENABLE_USER_SCRIPT_SANDBOXING = NO`) 在 `.xcodeproj` 中：

```bash
sed -i '' 's/ENABLE_USER_SCRIPT_SANDBOXING = YES/ENABLE_USER_SCRIPT_SANDBOXING = NO/g' "$XCODEPROJ_PATH/project.pbxproj"
```

如果该设置不存在（Xcode 默认启用它），则添加 `ENABLE_USER_SCRIPT_SANDBOXING = NO;` 到应用程序目标的 `buildSettings` 部分。然后重新启动 Gradle 守护进程： `./gradlew --stop`

**替代方案（如果 xcodebuild 方法失败）:** 参见 [troubleshooting.md](references/troubleshooting.md) § "Manual Integration Command Discovery" 以获取后备脚本以发现路径并直接运行集成任务。

### 5.2 更新 Crashlytics dSYM 上传脚本（如果适用）

如果项目使用 FirebaseCrashlytics，并且有一个 dSYM 上传运行脚本阶段（第 1 步步骤 11 中识别），请更新脚本路径从 `${PODS_ROOT}/FirebaseCrashlytics/upload-symbols` 到 `"${BUILD_DIR%/Build/*}/SourcePackages/checkouts/firebase-ios-sdk/Crashlytics/run"`。参见 [troubleshooting.md](references/troubleshooting.md) § "Firebase Crashlytics: dSYM Upload Script" 和 [common-pods-mapping.md](references/common-pods-mapping.md) 获取完整脚本和输入文件列表。

### 5.3 解集成 CocoaPods

**选项 A: 完全解集成**（如果 CocoaPods 仅用于 KMP 依赖项）:

在删除文件之前，运行 `git status --short` 并验证路径。如果不确定，请将文件移动到备份位置，而不是立即删除。

```bash
cd /path/to/iosApp
pod deintegrate
rm -rf Podfile Podfile.lock Pods/
# 删除与您的应用 xcodeproj 名称匹配的工作区
XCODEPROJ_NAME=$(basename "$(find . -maxdepth 1 -name "*.xcodeproj" -type d | grep -v Pods | head -1)" .xcodeproj)
rm -rf "${XCODEPROJ_NAME}.xcworkspace"
# 返回项目根目录
cd ..
# 删除迁移的模块 podspec 仅（例如，shared.podspec）
# 如果未知，列出候选者并显式删除匹配的项:
ls -1 *.podspec
# rm -f shared.podspec
```

此清理片段是自包含的，不依赖于 `XCODEPROJ_PATH` 或 `GRADLE_PROJECT_PATH` 从先前的迁移命令中提供的值。如果 `pod deintegrate` 不可用，请参见 [troubleshooting.md](references/troubleshooting.md) § "Manual CocoaPods Deintegration from pbxproj" 以获取要删除的完整引用列表。还要从 `.gitignore` 中删除 `Pods/` 并删除 `.xcworkspace` 目录。

**选项 B: 部分删除**（如果保留其他非 KMP CocoaPods 依赖项）:

从 `Podfile` 中删除 KMP pod 行并重新运行 pod install:

```ruby
target 'iosApp' do
  # 删除此行:
  pod 'shared', :path => '../shared'
  # 保留其他非 KMP pods
end
```

```bash
cd /path/to/iosApp && pod install
```

> **提示:** 考虑将剩余 pods 也迁移到 SPM — 大多数流行的 iOS 库都原生支持它。通过 Xcode 中的 File → Add Package Dependencies 添加它们，然后完全解集成 CocoaPods（一旦所有 pods 都被替换）。

### 5.4 手动集成（如果自动失败）

参见 [troubleshooting.md](references/troubleshooting.md) § "Manual Xcode Integration Steps" 以获取 5 步手动设置（构建阶段、沙盒、链接包）。

---

## 第 6 步：从 Gradle 中移除 CocoaPods

现在 iOS 项目已重新配置，从**所有**使用它的模块中移除 CocoaPods 插件和块（而不仅仅是主模块）:

### 6.1 移除 CocoaPods 插件

从每个模块的 `plugins {}` 中移除 `kotlin("native.cocoapods")` 或 `alias(libs.plugins.kotlinCocoapods)`:

```kotlin
plugins {
    // 移除: kotlin("native.cocoapods")  or  alias(libs.plugins.kotlinCocoapods)
    alias(libs.plugins.kotlinMultiplatform)  // 保留
}
```

如果所有模块都已迁移，则从 `gradle/libs.versions.toml` 中删除 `kotlinCocoapods` 插件条目：

```toml
[plugins]
# 移除: kotlinCocoapods = { id = "org.jetbrains.kotlin.native.cocoapods", version.ref = "kotlin" }
```

### 6.2 移除 cocoapods 块

从 `build.gradle.kts` 中删除整个 `cocoapods { ... }` 块。`swiftPMDependencies {}` 块和 `binaries.framework {}` 配置在第 3 步中添加，它们替换了它。还删除模块目录中的任何生成的 `.podspec` 文件（例如，`shared/shared.podspec`）— 这些是由 CocoaPods 插件生成的，不再需要。

### 6.3 移除已弃用的 gradle.properties 条目

如果第 1.1 步中找到，从 `gradle.properties` 中删除：

```properties
# 移除 — 迁移到 CocoaPods 后不再需要 (KT-64096)
kotlin.apple.deprecated.allowUsingEmbedAndSignWithCocoaPodsDependencies=true
```

### 6.4 清理 CocoaPods 相关的额外内容

审查步骤 1.12 中识别的 extras。Podspec 元数据、`noPodspec()`, CocoaPods 任务挂钩, `Pods.xcodeproj` 补丁，podspec 元数据, `extraSpecAttributes`, `noPodspec()`, 等.）。无需用户确认即可安全删除。非标准的 pod 配置（`extraOpts`, `moduleName`），自定义 cinterop `defFile` 设置，以及 CocoaPods 特有的编译器/链接器标志需要分析 — 不确定时请咨询用户。

参见 [cocoapods-extras-patterns.md](references/cocoapods-extras-patterns.md) 获取完整分类列表和示例。

---

## 第 7 步：验证

**在应用成功构建之前不要停止。** 此阶段是迭代的 — 如果任何步骤失败，诊断错误，修复它（参考 [troubleshooting.md](references/troubleshooting.md) 并重新检查第 2-6 步），然后重新运行失败的验证步骤。重复直到构建成功或问题明显超出迁移范围（预存在的错误，与工具无关的问题）。不要在构建成功之前编写迁移报告（第 8 步）。

### 7.1 编译 Kotlin 代码

编译迁移的模块以验证 Kotlin 源代码正确：

```bash
./gradlew :moduleName:compileKotlinIosSimulatorArm64
```

如果编译失败并出现未解决的引用，请检查导入转换（第 4 步）和 SwiftPM 依赖项声明（第 3.2 步）。

常见原因：缺少 `importedClangModules`, Clang 模块名称错误，保留捆绑的 klib 导入应被转换（或反之）。

### 7.2 链接框架

```bash
./gradlew :moduleName:linkDebugFrameworkIosSimulatorArm64
```

如果链接失败，请检查所有必需的 SPM 产品是否声明，并且版本约束是否解析正确。链接器错误关于缺少符号通常表示遗漏了产品，或者版本不匹配导致 API 移除，从而引入与迁移本身无关的问题。

### 7.3 构建iOS/macOS Xcode 项目

Gradle 步骤成功后，构建 Xcode 项目以验证整个应用编译。使用 `-project *.xcodeproj` 如果所有 CocoaPods 都已删除（选项 A），或者使用 `-workspace *.xcworkspace` 如果保留非 KMP CocoaPods（选项 B）：

```bash
cd /path/to/iosApp
# 发现方案并构建（替换 -project/-workspace 如有必要；对于 macOS 使用 -destination 'platform=macOS'):
xcodebuild -project *.xcodeproj -list -json 2>/dev/null | python3 -c "import sys,json; from subprocess import check_output; print(list(set(json.loads(check_output(["xcodebuild", "-workspace", sys.stdin.readline(), "-list", "-json")))["project"]["schemes"]) - set(json.loads(check_output(["xcodebuild", "-project", "Pods/Pods.xcodeproj", "-list", "-json")))["project"]["schemes"]))[0])')" -project *.xcodeproj -scheme "<AppScheme>" -destination 'generic/platform=iOS Simulator' ARCHS=arm64 build
```

**如果 `checkSandboxAndWriteProtection` 失败** — 沙盒未在第 5.1 步中禁用。返回并应用第 5.1 步中的沙盒修复，然后重试。

**如果迁移前的构建未验证**（第 1.0 落败时使用了替代方案），请警告用户：
> 注意：迁移前构建无法验证。如果现在出现构建错误，一些错误可能是迁移无关的预现有问题。将错误与迁移前构建输出进行比较，以区分迁移问题和先前问题。

### 如果构建失败

**不要**还原迁移。阅读错误日志，重新检查第 2-6 步，并参考 [troubleshooting.md](references/troubleshooting.md) 进行修复。如果不确定，请向用户呈现选项，不要默默撤销迁移工作。修复问题并重新运行失败的验证步骤。重复直到构建成功或问题明显超出迁移范围。

---

## 第 8 步：迁移报告

构建成功后，在项目根目录编写一个全面的 `MIGRATION_REPORT.md`。使用 [migration-report-template.md](references/migration-report-template.md) 中的模板。

报告必须包括：
1. **迁移前状态** — CocoaPods 依赖项（名称、版本、`linkOnly`），框架配置，`cocoapods.*` 导入，非 KMP CocoaPods，非典型配置
2. **迁移步骤** — 每个阶段的精确更改，非平凡更改的 before/after 片段
3. **导入转换** — 每个导入更改的表格，清楚地标记保留的 `cocoapods.*` 导入和哪些捆绑的 klib 提供它们
4. **遇到的错误** — 结构化的 `Error #N` 条目：阶段、确切症状、根本原因、修复，通用标志
5. **非平凡决策** — `isStatic` 更改，保留导入，框架搜索路径，权衡
6. **更改的文件** — 按类型分组（Gradle, Kotlin, Xcode, 创建的，删除的）

---

## 其他资源

- [DSL 参考](references/dsl-reference.md) - 完整 swiftPMDependencies 语法
- [常见 Pods 映射](references/common-pods-mapping.md) - Pods 到 SPM 映射表
- [CocoaPods 额外模式](references/cocoapods-extras-patterns.md) - CocoaPods 工作绕过检测和清理模式
- [故障排除](references/troubleshooting.md) - 问题，解决方案，回滚
- [迁移报告模板](references/migration-report-template.md) - 迁移后报告模板
