# Swift 并发

## 快速路径

在提出修复方案之前：

1.  分析 `Package.swift` 或 `.pbxproj` 文件，以确定 Swift 语言模式、严格并发级别、默认隔离级别和即将推出的特性。务必始终执行此操作，而不仅限于迁移工作。
2.  捕获精确的诊断信息和违规符号。
3.  确定隔离边界：`@MainActor`、自定义 actor、actor 实例隔离或 `nonisolated`。
4.  确认代码是否 UI 相关或打算在主 actor 之外运行。在生成非结构化任务时，检查同步前缀（第一个 `await` 之前的所有内容）：只有当该前缀确实需要主 actor 访问时，才从 `@MainActor` 开始；否则使用 `Task { @concurrent in ... }` 并在挂起后使用 `MainActor.run` 返回。同一前缀中跟在简单非主行（例如 `print`）后面的主 actor 工作并不是使用 `@concurrent` 的理由。对于延迟重试、计时器和退避任务，将等待与 UI 变更分开。即使最终状态更新属于主 actor，睡眠通常也属于主 actor 之外。

改变并发行为的配置项目：

| 设置 | SwiftPM (`Package.swift`) | Xcode (`.pbxproj`) |
|---|---|---|
| 语言模式 | `swiftLanguageVersions` 或 `-swift-version` (`// swift-tools-version:` 不是一个可靠的代理) | Swift 语言版本 |
| 严格并发 | `.enableExperimentalFeature("StrictConcurrency=targeted")` | `SWIFT_STRICT_CONCURRENCY` |
| 默认隔离 | `.defaultIsolation(MainActor.self)` | `SWIFT_DEFAULT_ACTOR_ISOLATION` |
| 即将推出的特性 | `.enableUpcomingFeature("NonisolatedNonsendingByDefault")` | `SWIFT_UPCOMING_FEATURE_*` |
| 可接近并发 | N/A (使用单个即将推出的特性) | `SWIFT_APPROACHABLE_CONCURRENCY` |

> **Xcode 26 注意**: 在 Xcode 26 中创建的新项目通常会默认启用 `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` 和 `SWIFT_APPROACHABLE_CONCURRENCY = YES`。将这些视为新创建项目的可能默认值，而不是确认的设置。

如果其中任何一项未知，请要求开发者确认后再提供与迁移相关的指导。即使对于新 Xcode 26 项目也不要猜测。

安全边界：

- 不要将 `@MainActor` 作为通用的修复建议。说明代码为何真正 UI 相关。
- 优先选择结构化并发而非非结构化任务。仅在有明确理由的情况下使用 `Task.detached`。
- 如果建议使用 `@preconcurrency`、`@unchecked Sendable` 或 `nonisolated(unsafe)`，需要要求提供文档化的安全不变量和后续移除计划。
- 优化为最小的安全更改。在迁移期间不要重构无关的架构。
- 课程参考仅用于深入学习。仅在它们明确有助于回答开发者问题时才使用它们。

## 快速修复模式

当所有这些条件都满足时使用快速修复模式：

- 问题局限于一个文件或一个类型。
- 隔离边界清晰。
- 修复方案可以在 1-2 步行为保持的情况下解释清楚。

当任何一项为真时跳过快速修复模式：

- 构建设置或默认隔离未知。
- 问题跨越模块边界或更改公共 API 行为。
- 可能的修复方案依赖于不安全的逃逸通道。

## 常见诊断

| 诊断 | 首先检查 | 最小的安全修复 | 升级到 |
|---|---|---|---|
| `Main actor-isolated ... cannot be used from a nonisolated context` | 这是否真正 UI 相关？ | 将调用者隔离到 `@MainActor`，或仅在主 actor 所有权正确时使用 `await MainActor.run { ... }`。 | `references/actors.md`，`references/threading.md` |
| `Actor-isolated type does not conform to protocol` | 必须在 actor 上运行要求吗？ | 优先选择隔离的协议实现（例如，`extension Foo: @MainActor SomeProtocol`）；仅在真正非隔离要求的情况下使用 `nonisolated`。 | `references/actors.md` |
| `Sending value of non-Sendable type ... risks causing data races` | 正在跨越哪个隔离边界？ | 将访问保留在一个 actor 内，或将传输的值转换为不可变/值类型。 | `references/sendable.md`，`references/threading.md` |
| `SwiftLint async_without_await` | `async` 是否确实由协议、重写或 `@concurrent` 需要呢？ | 移除 `async`，或使用具有合理理由的窄抑制。永远不要添加假的 `await`。 | `references/linting.md` |
| `wait(...) is unavailable from asynchronous contexts` | 这是遗留的 XCTest 异步等待吗？ | 替换为 `await fulfillment(of:)` 或 Swift 测试等效项。 | `references/testing.md` |
| Core Data 并发警告 | `NSManagedObject` 实例是否跨越上下文或 actor？ | 传递 `NSManagedObjectID` 或映射到可发送的值类型。 | `references/core-data.md` |
| `@Observable` 隔离或可发送错误 | `@Observable` 类是否标注了正确的 actor？ | 为 UI 状态添加 `@MainActor`；跨边界传递可发送的快照。 | `references/observation.md` |
| `Thread.current` 在异步上下文中不可用 | 你是否通过线程而不是隔离来调试？ | 用隔离术语进行推理，并使用 Instruments/调试器。 | `references/threading.md` |
| SwiftLint 并发相关警告 | 哪个特定的 lint 规则触发了？ | 使用 `references/linting.md` 了解规则意图和首选修复方案；避免假 `await`。 | `references/linting.md` |
| `... cannot satisfy conformance requirement for a 'Sendable' type parameter` (`SendableMetatype`) | 协议实现是否携带全局 actor 隔离？ | 从协议中移除 actor 隔离，或避免跨隔离边界传递元类型。参见 `references/actors.md` 中的 `SendableMetatype` 部分。 | `references/actors.md` |

## 快速修复失败时

1.  如果尚未确认，收集项目设置。
2.  重新评估类型跨越的隔离边界。
3.  路由到匹配的参考文件进行更深层次的修复。
4.  如果修复可能改变行为，记录不变量并添加验证步骤。

## 最小安全修复

优先选择在满足数据竞争安全性的同时保持行为的更改：

- **UI 相关状态**：将类型或成员隔离到 `@MainActor`。
- **共享可变状态**：将其放在 `actor` 后面，或仅在状态属于 UI 所有时使用 `@MainActor`。
- **后台工作**：当工作必须从调用者隔离跳转时，使用标记为 `@concurrent` 的 `async` API；当工作可以安全地继承调用者隔离时，使用 `nonisolated` 而不使用 `@concurrent`。在生成 `Task` 时，匹配其同步前缀的入口隔离。如果第一个 `await` 之前没有任何内容需要主 actor，使用 `Task { @concurrent in ... }` 并通过 `await MainActor.run { ... }` 返回 UI 更新。如果前缀混合了简单的非主行和主 actor 工作，保持继承的 `@MainActor` 开始——将廉价行移出主 actor 并不是值得额外跳转的。

- **可发送性问题**：优先选择不可变值和显式边界，而不是 `@unchecked Sendable`。

## 并发工具选择

| 需求 | 工具 | 关键指导 |
|---|---|---|
| 单个异步操作 | `async/await` | 顺序异步工作的默认选择 |
| 固定并行操作 | `async let` | 编译时已知数量；在抛出时自动取消 |
| 动态并行操作 | `withTaskGroup` | 数量未知；结构化——在作用域退出时取消子任务 |
| 同步到异步桥接 | `Task { }` | 继承 actor 上下文；仅在文档化理由的情况下使用 `Task.detached` |
| 共享可变状态 | `actor` | 优先于锁/队列；保持隔离部分小 |
| UI 相关状态 | `@MainActor` | 仅适用于真正 UI 相关的代码；说明隔离 |

### 常见场景

**带 UI 更新的网络请求**
```swift
Task { @concurrent in
    let data = try await fetchData()
    await MainActor.run { self.updateUI(with: data) }
}
```

**并行处理数组项**
```swift
await withTaskGroup(of: ProcessedItem.self) { group in
    for item in items {
        group.addTask { await process(item) }
    }
    for await result in group {
        results.append(result)
    }
}
```

## Task 入口隔离

匹配 `Task` 的入口隔离与其同步前缀（从 `{` 到第一个 `await`）。

- 如果该前缀中的任何内容需要 `@MainActor`，保持继承的 `@MainActor` 开始。
- 如果该前缀中的任何内容不需要 `@MainActor`，优先选择 `Task { @concurrent in ... }` 并仅在 UI 所有权的情况下返回。

```swift
// ❌ 同步前缀为空；第一个工作跳转到其他隔离域
Task {
    await hopToOtherIsolationDomain()
}

// ❌ 同步前缀只有 `print`（简单、非主）；第一个 await 跳转到其他隔离域
Task {
    print("Also not main-thread-bound")
    await hopToOtherIsolationDomain()
}

// ✅ 从主 actor 开始，仅在 UI 工作时返回
Task { @concurrent in
    await hopToOtherIsolationDomain()
    await MainActor.run { updateUI() }
}

// ✅ 同步前缀包含主 actor 工作——保持继承
Task {
    print("debug")              // 简单、非主——随行
    self.isLoading = true       // 需要 @MainActor，在任何 await 之前
    await fetchData()
}
```

## Swift 6 迁移快速指南

Swift 6 中的关键更改：

- **严格并发检查** 默认启用
- **编译时完全数据竞争安全**
- **边界上的可发送要求**
- **所有异步边界的隔离检查**

### 迁移验证循环

对每个迁移更改应用此循环：

1. **构建** — 运行 `swift build` 或 Xcode 构建以暴露新的诊断信息
2. **修复** — 一次解决一类错误（例如，首先解决所有可发送问题）
3. **重新构建** — 在继续之前确认修复干净
4. **测试** — 运行测试套件以捕获回归 (`swift test` 或 Cmd+U)
5. **仅当所有诊断都解决** 时才继续到下一个文件/模块

如果修复引入了新的警告，解决它们后再继续。永远不要批量多个无关的修复——保持提交小且可审查。

有关详细的迁移步骤，请参阅 `references/migration.md`。

## 参考路由器

打开与问题最匹配的最小参考：

- 基础
  - `references/async-await-basics.md` — async/await 语法、执行顺序、async let、URLSession 模式
  - `references/tasks.md` — Task 生命周期、取消、优先级、任务组、结构化与非结构化
  - `references/actors.md` — Actor 隔离、@MainActor、全局 actor、可重入性、自定义执行器、Mutex
  - `references/sendable.md` — 可发送协议实现、值/引用类型、@unchecked、区域隔离
  - `references/threading.md` — 执行模型、挂起点、Swift 6.2 隔离行为
- 流
  - `references/async-sequences.md` — AsyncSequence、AsyncStream、何时使用 vs 普通异步方法
  - `references/async-algorithms.md` — Debounce、throttle、merge、combineLatest、通道、计时器
- 应用主题
  - `references/testing.md` — Swift 测试优先、XCTest 降级、内存泄漏检查
  - `references/performance.md` — 使用 Instruments 进行分析、减少挂起点、执行策略
  - `references/memory-management.md` — 任务中的保留循环、内存安全模式
  - `references/core-data.md` — NSManagedObject 可发送性、自定义执行器、隔离冲突
  - `references/observation.md` — @Observable 与 @MainActor、跨隔离访问、可发送约束
- 迁移和工具
  - `references/migration.md` — Swift 6 迁移策略、闭包到异步转换、@preconcurrency、FRP 迁移
  - `references/linting.md` — 并发相关的 lint 规则和 SwiftLint `async_without_await`
- 术语表
  - `references/glossary.md` — 核心并发术语的快速定义

## 验证检查清单

更改并发代码时：

1. 在解释诊断信息之前重新检查构建设置。
2. 构建并清除一类错误后再继续。不要将无关的修复批量到同一个更改中。
3. 运行测试，特别是 actor-、生命周期-和取消敏感的测试。
4. 使用 Instruments 进行性能声明，而不是猜测。
5. 验证长生命周期任务的释放和取消行为。
6. 在长运行操作中检查 `Task.isCancelled`。
7. 永远不要在异步上下文中使用信号量或临时锁，当 actor 隔离或 `Mutex` 可以更安全地表达所有权时。
