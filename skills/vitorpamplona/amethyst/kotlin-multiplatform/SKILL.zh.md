---
name: kotlin-multiplatform
description: 紫晶 KMP 项目的平台抽象决策。指导何时进行抽象与何时保留平台特定实现，包括源集放置（commonMain、jvmAndroid、平台特定源集）以及 expect/actual 模式。涵盖主要目标平台（Android、JVM/桌面、iOS——均为成熟平台），并将 Web/WASM 作为可能的未来目标平台。与 gradle-expert 集成以解决依赖问题。触发场景包括：抽象决策（“我应该共享此代码吗？”）、源集放置问题、创建 expect/actual、编辑 build.gradle.kts、检测不正确的放置以及 KMP 依赖建议。
---

# Kotlin Multiplatform: 平台抽象决策

Amethyst 中 KMP 架构的专业指导 - 决定什么应该共享，什么应该保持平台特定。

## 何时使用此技能

进行平台抽象决策：
- "我应该创建 expect/actual 还是保持 Android 特定？"
- "我可以共享这个 ViewModel 逻辑吗？"
- "这个加密/JSON/网络实现属于哪里？"
- "这个使用 Android Context 的代码能被抽象吗？"
- "这段代码是否放在了错误的模块？"
- 准备支持 iOS/web/wasm 目标
- 检测不正确的放置

## 抽象决策树

**核心问题：** "这段代码应该在多个平台上重用吗？"

遵循这个决策路径（小于 1 分钟）：

```
Q: 是否被 2+ 平台使用？
├─ 否  → 保持平台特定
│         示例：Android 特定的权限处理
│
└─ 是  → 继续 ↓

Q: 是否是纯 Kotlin（不使用平台 API）？
├─ 是  → commonMain
│         示例：Nostr 事件解析，业务规则
│
└─ 否  → 继续 ↓

Q: 是否因平台而异或因 JVM 与非 JVM 而异？
├─ 因平台（Android ≠ iOS ≠ 桌面）
│  → expect/actual
│  示例：Secp256k1Instance（使用不同的安全 API）
│
├─ 因 JVM（Android = 桌面 ≠ iOS/web）
│  → jvmAndroid
│  示例：Jackson JSON 解析（JVM 库）
│
└─ 复杂/UI 相关
   → 在 commonsUI 中共享；expect/actual 或仅平台叶子节点的槽
   示例：导航。一个 shell 在 commonsUI 中，由窗口大小选择
   (ScreenLayoutSpec)；只有 Activity / Window 入口点是本地的

最终检查：
Q: 抽象的维护成本 < 重复的成本？
├─ 是  → 继续抽象
└─ 否  → 重复（更简单）
```

### 代码库中的真实示例

**加密 → expect/actual:**
```kotlin
// commonMain - expect 声明
expect object Secp256k1Instance {
    fun signSchnorr(data: ByteArray, privKey: ByteArray): ByteArray
}

// androidMain - 使用 Android Keystore
// jvmMain - 使用桌面 JVM 加密
// iosMain - 使用 iOS Security 框架
```
**原因：** 每个平台都有不同的安全 API。

**JSON 解析 → jvmAndroid:**
```kotlin
// quartz/build.gradle.kts
val jvmAndroid = create("jvmAndroid") {
    api(libs.jackson.module.kotlin)
}
```
**原因：** Jackson 是 JVM 特定的，在 Android + 桌面上工作，不在 iOS/web 上。

**导航 → 共享，入口点 → 平台特定:**
- 共享 (`commonsUI`，正在迁移那里)：导航主机，底部栏 / 轨道 / 永久抽屉，通过 `ScreenLayoutSpec` 由窗口大小选择
- Android：`MainActivity` 主持它；桌面：一个 `Window` (+ 菜单栏，托盘) 主持它
**原因：** Android 也可以在笔记本电脑上运行，并且新的桌面应用程序渲染相同的 UI。参见 `commons/plans/2026-09-27-one-ui-android-desktop.md`。今天的 `desktopApp` 侧边栏 shell 是遗留的。

## 心智模型：源集作为依赖图

将源集视为依赖图，而不是文件夹。

```
┌─────────────────────────────────────────────┐
│ commonMain = 合同（纯 Kotlin）             │
│ - 业务逻辑，协议，数据模型               │
│ - 没有平台 API                          │
└────────────┬────────────────────────────────┘
             │
             ├──────────────────────┬────────────────────
             │                      │
             ▼                      ▼
   ┌───────────────────┐  ┌──────────────────┐
   │ jvmAndroid        │  │ iosMain          │
   │ JVM 库共享       │  │ iOS common       │
   │ - Jackson         │  │                  │
   │ - OkHttp          │  └────┬─────────────┘
   └───┬───────────┬───┘       │
       │           │           │
       ▼           ▼           ├─→ iosArm64Main
  ┌─────────┐ ┌──────────┐     └─→ iosSimulatorArm64Main
  │android  │ │jvmMain   │
  │Main     │ │(桌面)   │
  └─────────┘ └──────────┘

未来：jsMain, wasmMain
```

**关键洞察：** jvmAndroid 不是平台 - 它是共享的 JVM 层。

## jvmAndroid 模式

**Amethyst 独有。** 在 Android 和桌面之间共享 JVM 库。

### 何时使用 jvmAndroid

当满足以下条件时使用 jvmAndroid：
- ✅ JVM 特定库（Jackson, OkHttp, url-detector）
- ✅ Android 实现 = 桌面实现（相同的 JVM）
- ✅ 库在 iOS/web 上不可用

**不要**使用 jvmAndroid：
- ❌ 纯 Kotlin 代码（使用 commonMain）
- ❌ 平台特定 API（使用 androidMain/jvmMain）
- ❌ 应该在所有平台上工作的代码

### quartz/build.gradle.kts 中的示例

```kotlin
// 必须在 androidMain 和 jvmMain 定义之前
val jvmAndroid = create("jvmAndroid") {
    dependsOn(commonMain.get())

    dependencies {
        api(libs.jackson.module.kotlin)  // JSON 解析 - JVM 仅限
        api(libs.url.detector)            // URL 提取 - JVM 仅限
        implementation(libs.okhttp)       // HTTP 客户端 - JVM 仅限
    }
}

// 两者都依赖于 jvmAndroid
jvmMain { dependsOn(jvmAndroid) }
androidMain { dependsOn(jvmAndroid) }
```

**为什么 Jackson 在 jvmAndroid 中，而不是 commonMain？**
- Jackson 是 JVM 特定库
- 在 Android 上工作（在 JVM 上运行）
- 在桌面（在 JVM 上运行）
- 不在 iOS（不是 JVM）或 web（不是 JVM）上工作

**Web/wasm 考虑：** 为了未来的 web 支持，考虑从 Jackson 迁移到 kotlinx.serialization（参见 Target-Specific Guidance）。

## 什么应该抽象 vs 保持平台特定

基于代码库模式的快速决策指南：

### 总是抽象
- **加密**（Secp256k1，加密，签名）
- **核心协议逻辑**（Nostr 事件，NIPs）
- **原因：** 到处都需要，平台安全 API 不同

### 经常抽象
- **I/O 操作**（文件读取，缓存）
- **日志记录**（平台日志系统不同）
- **序列化**（如果使用 kotlinx.serialization）
- **原因：** 常常重用，平台实现可用

### 有时抽象
- **业务逻辑：** 是的 - 状态机，数据处理
- **ViewModels：** 是的 - 状态 + 业务逻辑可共享（StateFlow/SharedFlow）
- **屏幕布局：** 是的 - 在 `commonsUI` 中共享；它们适应窗口大小，而不是平台
- **原因：** 一个 UI 用于 Android（手机到笔记本电脑）和桌面；只有入口点不同

### 很少抽象
- **复杂 UI 组件**（具有重平台依赖的 composables）
- **原因：** 平台范例可能差异很大

### 从不抽象
- **进程 / 窗口入口点**（Activity，Service，Window，托盘）
- **权限**（Android vs iOS API 不兼容）
- **平台 UX 模式**
- **原因：** 太平台特定，抽象会导致泄漏 API

### 来自 shared-ui-analysis.md 的证据

| 组件 | 是否共享 | 理由 |
|------|---------|------|
| PubKeyFormatter, ZapFormatter | ✅ 是 | 纯 Kotlin，没有平台 API |
| TimeAgoFormatter | ⚠️ 抽象 | 需要用于本地化字符串的 StringProvider |
| ViewModels（状态 + 逻辑） | ✅ 是 | StateFlow/SharedFlow 平台无关，Compose Multiplatform 生命周期兼容 |
| 屏幕布局（Scaffold，导航） | ✅ 是（正在迁移） | 一个 UI；`ScreenLayoutSpec` 通过窗口大小选择底部栏 / 轨道 / 抽屉 |
| Image loading（Coil） | ⚠️ 抽象 | Coil 3.x 支持 KMP，需要 expect/actual 包装 |

## expect/actual 机制

**何时使用：** 2+ 平台需要的代码，因平台而异。

### 代码库中的模式类别

**对象（单例）：**
```kotlin
// 找到 24 个 expect 声明，常见模式：
expect object Secp256k1Instance { ... }
expect object Log { ... }
expect object LibSodiumInstance { ... }
```

**类（可实例化）：**
```kotlin
expect class AESCBC { ... }
expect class DigestInstance { ... }
```

**函数（工具）：**
```kotlin
expect fun platform(): String
expect fun currentTimeSeconds(): Long
```

**参见** [references/expect-actual-catalog.md](references/expect-actual-catalog.md) 获取包含理由的完整目录。

## 目标特定指南

### Android，JVM（桌面），iOS - 当前主要目标

**状态：** 成熟模式，稳定 API

**Android (androidMain):**
- 使用 Android 框架（Activity，Context 等）
- secp256k1-kmp-jni-android（`libs.versions.toml` 中的 `0.23.0`）用于加密
- AndroidX 库

**桌面 JVM (jvmMain):**
- 使用 Compose Desktop（Window，MenuBar 等）
- secp256k1-kmp-jni-jvm（相同的 `0.23.0` 行）用于加密
- 纯 JVM 库

**iOS (iosMain):**
- 成熟目标 — 积极构建和测试
- 架构目标：iosArm64，iosSimulatorArm64，iosX64（以及用于主机工具的 macosArm64）
- 通过 platform.posix 和 Security 框架访问平台 API

### Web，wasm - 未来目标

**状态：** 尚未实现，考虑用于未来保护

**需要了解的约束：**
- ❌ 没有 platform.posix（文件 I/O 不同）
- ❌ 没有 JVM 库（Jackson，OkHttp 不工作）
- ❌ 不同的异步模型（JS 事件循环 vs 线程）

**未来保护技巧：**
1. 在 commonMain 中优先使用纯 Kotlin
2. 使用 kotlinx.* 库：
   - 使用 kotlinx.serialization 代替 Jackson
   - 使用 ktor 代替 OkHttp（ktor 支持 web）
   - 使用 kotlinx.datetime 代替自定义日期处理
3. 避免使用 platform.posix 进行文件操作
4. 测试抽象在没有 JVM 假设的情况下工作

**示例迁移路径：**
```kotlin
// 当前：jvmAndroid（仅限 JVM）
api(libs.jackson.module.kotlin)

// 未来：commonMain（所有平台）
api(libs.kotlinx.serialization.json)
```

## 集成：何时调用其他技能

### 调用 gradle-expert

当遇到以下情况时触发 gradle-expert 技能：
- 依赖冲突（例如，secp256k1-android vs secp256k1-jvm 版本不匹配）
- 与源集相关的构建错误
- 版本目录问题（libs.versions.toml）
- "重复类"错误
- 性能/构建时间问题

**示例触发：**
```
错误：找到重复的类：fr.acinq.secp256k1.Secp256k1
```
→ 调用 gradle-expert 进行依赖冲突解决。

### 需要标记的问题

**commonMain 中的平台代码：**
```kotlin
// ❌ 不正确 - Android API 在 commonMain 中
expect fun getContext(): Context  // Context 是 Android 特定的！
```
→ 标记："Android API 在 commonMain 中，在其他平台上无法编译"

**重复的业务逻辑：**
```kotlin
// ❌ 不正确 - 两个地方都有相同的逻辑
// androidMain/.../CryptoUtils.kt
fun validateSignature(...) { ... }

// jvmMain/.../CryptoUtils.kt
fun validateSignature(...) { ... }  // 重复！
```
→ 标记："业务逻辑重复，应该放在 commonMain 或 expect/actual"

**重新发明轮子 - 建议使用 KMP 替代方案：**
- 自定义日期/时间 → kotlinx.datetime
- OkHttp → ktor（支持 web）
- Jackson → kotlinx.serialization
- 自定义 UUID → kotlinx.uuid（当稳定时）

## 常见陷阱

### 1. 过度抽象
**问题：** 为 UI 组件创建 expect/actual
```kotlin
// ❌ 不良
expect fun NavigationComponent(...)
```
**原因：** 每个平台都会分支整个导航 UI。
**修复：** 在 `commonsUI` 中编写导航一次；将平台叶子节点（Activity 结果，文件选择器）通过 expect/actual 或槽放置

### 2. 分享不足
**问题：** 在不同平台上重复业务逻辑
```kotlin
// ❌ 不良 - 在 androidMain 和 jvmMain 中重复
fun parseNostrEvent(json: String): Event { ... }
```
**原因：** Bug 修复需要应用两次，测试重复
**修复：** 移动到 commonMain（纯 Kotlin）或创建 expect/actual

### 3. 泄漏抽象
**问题：** commonMain 中的平台代码
```kotlin
// commonMain - ❌ 不良
import android.content.Context  // 在 iOS 上无法编译！
```
**修复：** 使用 expect/actual 或依赖注入

### 4. 过早抽象
**问题：** 在第二个平台需要之前创建 expect/actual
```kotlin
// ❌ 不良 - 目前仅在 Android 上使用
expect fun showNotification(...)
```
**原因：** 错误的抽象边界，浪费精力
**修复：** 等待 iOS 真的需要它，然后抽象

### 5. 错误的源集
**问题：** commonMain 中的 JVM 库
```kotlin
// commonMain - ❌ 不良
import com.fasterxml.jackson.databind.ObjectMapper
```
**原因：** Jackson 在 iOS/web 上无法编译
**修复：** 移动到 jvmAndroid 或迁移到 kotlinx.serialization

## 快速参考

| 代码类型 | 推荐位置 | 原因 |
|---------|---------|------|
| 纯 Kotlin 业务逻辑 | commonMain | 到处都可用 |
| Nostr 协议，NIPs | commonMain | 核心逻辑，没有平台 API |
| JVM 库（Jackson，OkHttp） | jvmAndroid | Android + 桌面仅限 |
| 加密（因平台而异） | commonMain 中的 expect，平台中的 actual | 每个平台有不同的安全 API |
| I/O，日志记录 | commonMain 中的 expect，平台中的 actual | 平台实现不同 |
| 状态（业务逻辑） | commonMain 或 commons/jvmAndroid | 可重用的 StateFlow 模式 |
| **ViewModels** | **commons/commonMain/viewmodels/** | **StateFlow/SharedFlow + 逻辑可共享，Compose MP 生命周期兼容** |
| UI 表单格式化（纯） | commons/commonMain | 可重用，没有依赖 |
| 简单 UI 组件 | commonsUI/commonMain | 卡片，按钮，对话框（Compose UI 从不放在 `commons` 中） |
| **屏幕布局** | **commonsUI** | **一个 UI；通过 `ScreenLayoutSpec` 适应窗口大小** |
| 导航 | commonsUI（入口点平台特定） | 导航主机 + 界面共享；Activity / Window 主持它 |
| 权限 | 仅平台特定 | API 不兼容 |
| 平台 UX（菜单等） | 仅平台特定 | 需要本地感觉 |

## 参见

- [references/abstraction-examples.md](references/abstraction-examples.md) - 好的/坏的抽象示例及理由
- [references/source-set-hierarchy.md](references/source-set-hierarchy.md) - 带有 Amethyst 示例的可视化层次结构
- [references/expect-actual-catalog.md](references/expect-actual-catalog.md) - 所有 24 个 expect/actual 对象及"为什么抽象"的目录
- [references/target-compatibility.md](references/target-compatibility.md) - 平台约束和未来保护

## 脚本

- `scripts/validate-kmp-structure.sh` - 检测不正确的放置，验证源集
- `scripts/suggest-kmp-dependency.sh` - 建议使用 KMP 库替代方案（ktor，kotlinx.serialization 等）
