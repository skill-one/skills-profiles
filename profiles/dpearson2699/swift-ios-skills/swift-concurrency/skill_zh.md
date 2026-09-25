# Swift 并发

针对 Swift 6.3+ 审查、修复和编写并发 Swift 代码。清理 Swift 6.4 / Xcode 27 beta 后台 API，将其置于显式工具链和可用性检查之后。应用 actor 孤立、Sendable 安全性以及现代并发模式，同时最小化行为变化。

## 目录

- [审查工作流](#审查工作流)
- [Swift 6.2 语言变更](#swift-62语言变更)
- [Actor 孤立规则](#actor孤立规则)
- [Sendable 规则](#sendable规则)
- [结构化并发模式](#结构化并发模式)
- [任务取消](#任务取消)
- [Actor 重入](#actor重入)
- [AsyncSequence 和 AsyncStream](#asyncsequence和asyncstream)
- [`@Observable` 和并发](#observable和并发)
- [同步原语](#同步原语)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 审查工作流

在诊断并发问题时，请按照以下顺序操作：

### 第一步：捕获上下文

- 复制确切的编译器诊断信息和有问题的符号。
- 确定项目的并发设置：
  - Swift 语言版本（必须是 6.2+）。
  - Xcode/工具链版本，用于特定版本的功能和发布说明中的解决方案。
  - 是否启用 Approachable Concurrency。
  - 是否将 Default Actor Isolation 设置为 `MainActor`。
  - Swift 6 严格并发状态：在 Swift 6 语言模式下为完整/错误；在审计 Swift 5 迁移设置时为完整/目标/最小。
- 确定代码当前的 actor 上下文（`@MainActor`、自定义 `actor`、`nonisolated`）以及是否激活了默认隔离模式。
- 确认代码是否 UI 绑定或打算在主 actor 之外运行。

### 第二步：应用最小的安全修复

优先选择保留现有行为同时满足数据竞争安全性的编辑。

| 情况 | 推荐修复 |
|---|---|
| UI 绑定型 | 用 `@MainActor` 标注类型或相关成员。 |
| 在 MainActor 类型上实现协议 | 使用隔离实现：`extension Foo: @MainActor Proto`。 |
| 全局/静态状态 | 用 `@MainActor` 保护或移入 actor 中。 |
| 需要在后台工作 | 在 `nonisolated` 类型上使用 `@concurrent` 异步函数。 |
| Sendable 错误 | 优先使用不可变值类型。仅在正确时添加 `Sendable`。 |
| 跨隔离回调 | 使用 `sending` 参数（SE-0430）进行更细粒度的隔离控制。 |

### 第三步：验证

- 重新构建并确认诊断已解决。
- 检查修复引入的新警告。
- 确保没有添加不必要的 `@unchecked Sendable` 或 `nonisolated(unsafe)`。
- 对于构建设置审查，在设置加上最小的代码级修复后停止。除非提示需要诊断或迁移，否则不要添加 Thread Sanitizer、广泛的迁移顺序或架构建议。

## Swift 6.2 语言变更

Swift 6.2 引入了“可访问并发”——一组使并发代码默认更安全并减少注解负担的语言变更。在 Xcode 中，Approachable Concurrency 和 Default Actor Isolation 是单独的构建设置：使用 Approachable Concurrency 用于即将捆绑的功能标志，并将 Default Actor Isolation 设置为 `MainActor`，当你希望未注解的代码被推断为 `@MainActor` 时。

### SE-0466: 默认 MainActor 孤立

使用 `-default-isolation MainActor` 编译器标志、SwiftPM `.defaultIsolation(MainActor.self)` 或 Xcode 的 `Default Actor Isolation` 设置为 `MainActor`，模块中的未注解声明除非明确选择退出，否则会被推断为 `@MainActor`。

**效果：** 消除了 UI 绑定代码和全局/静态状态的大多数数据竞争安全错误，而无需到处写 `@MainActor`。

```swift
// 启用默认 MainActor 孤立后，这些隐式为 @MainActor：
final class StickerLibrary {
    static let shared = StickerLibrary()  // 安全——在 MainActor 上
    var stickers: [Sticker] = []
}

final class StickerModel {
    let photoProcessor = PhotoProcessor()
    var selection: [PhotosPickerItem] = []
}

// 适配也是隐式隔离的：
extension StickerModel: Exportable {
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```

**何时使用：** 推荐用于大多数代码为 UI 绑定的应用程序、脚本和其他可执行目标。不推荐用于应保持 actor 无关的库目标。

### SE-0461: nonisolated(nonsending)

非隔离异步函数现在默认在调用者的 actor 上运行，而不是跳转到全局并发执行器。这是 `nonisolated(nonsending)` 行为。

```swift
class PhotoProcessor {
    func extractSticker(data: Data, with id: String?) async -> Sticker? {
        // 在 Swift 6.2+ 中，这将在调用者的 actor 上运行（例如 MainActor）
        // 而不是跳转到后台线程。
        // ...
    }
}

@MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else {
            return nil
        }
        // 无数据竞争——photoProcessor 保持在 MainActor 上
        return await photoProcessor.extractSticker(data: data, with: item.itemIdentifier)
    }
}
```

当需要显式请求后台执行时，使用 `@concurrent`。

### `@concurrent` 属性

`@concurrent` 确保函数始终在并发线程池上运行，释放调用者 actor 以运行其他任务。

```swift
class PhotoProcessor {
    var cachedStickers: [String: Sticker] = [:]

    func extractSticker(data: Data, with id: String) async -> Sticker {
        if let sticker = cachedStickers[id] { return sticker }

        let sticker = await Self.extractSubject(from: data)
        cachedStickers[id] = sticker
        return sticker
    }

    @concurrent
    static func extractSubject(from data: Data) async -> Sticker {
        // 昂贵的图像处理——在后台线程池上运行
        // ...
    }
}
```

要将函数移到后台线程，一起显示两个选择退出：
1. 确保包含类型是 `nonisolated` 或函数可以从非隔离上下文中调用。
2. 在卸载的函数中添加 `@concurrent`。`nonisolated` 单独不会将 CPU 密集型工作移出调用者的 actor。
3. 如果尚未异步，则添加 `async`。
4. 在调用位置添加 `await`。

```swift
nonisolated struct PhotoProcessor {
    @concurrent
    func process(data: Data) async -> ProcessedPhoto? { /* ... */ }
}

// 调用者：
processedPhotos[item.id] = await PhotoProcessor().process(data: data)
```

### SE-0472: Task.immediate

`Task.immediate` 在任何挂起点之前同步在当前 actor 上执行，而不是被入队。

```swift
Task.immediate { await handleUserInput() }
```

用于应立即开始的延迟敏感工作。还有一个 `Task.immediateDetached`，它结合了立即开始和分离语义。

### SE-0475: 事务性观察（观察）

`Observations { }` 通过 `AsyncSequence` 提供 `@Observable` 类型的异步观察，从而实现事务性变更跟踪。

```swift
for await _ in Observations { model.count } {
    print("计数已更改为 \(model.count)")
}
```

### 孤立适配

需要 MainActor 状态的适配称为 *孤立适配*。编译器确保它仅在匹配的隔离上下文中使用。

```swift
protocol Exportable {
    func export()
}

// 孤立适配：仅可在 MainActor 上使用
extension StickerModel: @MainActor Exportable {
    func export() {
        photoProcessor.exportAsPNG()
    }
}

@MainActor
struct ImageExporter {
    var items: [any Exportable]

    mutating func add(_ item: StickerModel) {
        items.append(item)  // 可以——ImageExporter 在 MainActor 上
    }
}
```

如果 `ImageExporter` 是 `nonisolated`，添加 `StickerModel` 将失败：
"Main actor 孤立的 'StickerModel' 到 'Exportable' 的适配不能在非隔离上下文中使用。"

### 时钟纪元

`ContinuousClock` 和 `SuspendingClock` 现在暴露 `.epoch`（SE-0473），允许在时钟类型之间进行即时比较和转换。

```swift
let continuous = ContinuousClock()
let elapsed = continuous.now - continuous.epoch  // 系统启动以来的持续时间
```

## Actor 孤立规则

1. 所有可变共享状态必须由 actor 或全局 actor 保护。
2. 所有触摸 UI 的代码都必须使用 `@MainActor`。没有例外。
   全局 actor 是 actor 孤立；使用 `@MainActor` 作为 UI 绑定共享状态的常用模式。
3. 仅用于访问不可变（`let`）属性或纯计算的方法，使用 `nonisolated`。
4. 使用 `@concurrent` 显式将工作移出调用者的 actor。
5. 除非你已经证明了数据竞争安全并穷尽了更安全的替代方案，否则永远不要使用 `nonisolated(unsafe)`。它是一个不安全的审计边界，而不是同步原语。对于同步并行循环中的窄 unsafe-pointer 捕获模式，请遵循
   [桥接和互操作](references/bridging-interop.md#synchronous-parallel-for-concurrentperform-versus-task-groups) 中的证明要求。
   互斥的每个迭代访问可以消除冲突的并发访问和同步的需要；互斥性本身不是同步。
6. 永远不要在 actor 内部添加手动锁（`NSLock`、`DispatchSemaphore`）。

## Sendable 规则

1. 当所有存储属性都是 `Sendable` 时，值类型（structs、enums）自动为 `Sendable`。
   对于可变引用类型的诊断，首先提取不可变的 `Sendable` 值快照或 DTO，而不是共享引用。
2. Actors 自动为 `Sendable`。
3. `@MainActor` 类自动为 `Sendable`。不要添加冗余的 `Sendable` 适配。
4. 非 actor 类：必须为 `final`，所有存储属性为 `let` 和 `Sendable`。
5. `@unchecked Sendable` 是最后的选择。记录编译器无法证明安全的原因。
6. 使用 `sending` 参数（SE-0430）进行更细粒度的隔离控制。
7. 仅用于第三方库的 `@preconcurrency import`，计划移除它。

## 结构化并发模式

### Async Defer (Swift 6.4+)

在 Swift 6.4+ 中，异步上下文中的 `defer` 块可以包含 `await`（SE-0493）。用于异步清理：关闭连接、刷新缓冲区或释放需要异步调用的资源。

`defer` 主体继承周围的隔离，并在作用域退出时隐式等待。它不会抑制取消；检查 `Task.isCancelled` 或 `Task.checkCancellation()` 的清理仍然会观察取消。

```swift
func fetchData() async throws -> Data {
    let connection = try await openConnection()
    defer { await connection.close() }
    return try await connection.read()
}
```

**Task：** 非结构化，继承调用者上下文。
```swift
Task { await doWork() }
```

**Task.detached：** 没有继承的上下文。仅在明确需要打破隔离继承时使用。

**Task.immediate：** 在当前 actor 上立即开始。用于延迟敏感工作。
```swift
Task.immediate { await handleUserInput() }
```

**async let：** 固定数量的并发操作。
```swift
async let a = fetchA()
async let b = fetchB()
let result = try await (a, b)
```

**TaskGroup：** 动态数量的并发操作。
```swift
try await withThrowingTaskGroup(of: Item.self) { group in
    for id in ids {
        group.addTask { try await fetch(id) }
    }
    for try await item in group { process(item) }
}
```

## 任务取消

- 取消是协作的。在循环中检查 `Task.isCancelled` 或调用
  `try Task.checkCancellation()`。
- 使用 SwiftUI 中的 `.task` 修饰符——它处理视图消失时的取消。
- 使用 `withTaskCancellationHandler` 进行清理。
- Swift 6.4 / iOS 27+ beta：仅用于短清理或回滚必须在取消后完成的 `withTaskCancellationShield`。在屏蔽范围内，`Task.isCancelled` 为 false，`Task.checkCancellation()` 不会抛出；
  取消在作用域退出后再次可观察。
- 在 `deinit` 或 `onDisappear` 中取消存储的任务。

## Actor 重入

Actors 是可重入的。状态可以在挂起点之间改变。

```swift
// 错误：在 await 期间状态可能会改变
actor Counter {
    var count = 0
    func increment() async {
        let current = count
        await someWork()
        count = current + 1  // BUG：count 可能已更改
    }
}

// 正确：同步修改，无重入风险
actor Counter {
    var count = 0
    func increment() { count += 1 }
}
```

## AsyncSequence 和 AsyncStream

使用 `AsyncStream` 桥接回调/委托 API：

```swift
let stream = AsyncStream<Location> { continuation in
    let delegate = LocationDelegate { location in
        continuation.yield(location)
    }
    continuation.onTermination = { _ in delegate.stop() }
    delegate.start()
}
```

使用 `withCheckedContinuation` / `withCheckedThrowingContinuation` 用于单值回调。精确地恢复一次。

## `@Observable` 和并发

- `@Observable` 类应为 view models 使用 `@MainActor`。
- 使用 `@State` 拥有 `@Observable` 实例（替换 `@StateObject`）。
- 使用 `Observations { }`（SE-0475）异步观察 `@Observable` 属性作为 `AsyncSequence`。

## 同步原语

当 actors 不适用时——同步访问、性能关键路径或桥接 C/ObjC——使用低级同步原语：

- **Actors** 在调用者可以挂起时仍然是异步共享状态的首选，它们提供编译器强制的隔离和结构化并发集成，但外部调用是异步 actor 跳转，需要在 await 跨 reentrancy 仔细处理，并且不适合同步 C 回调。使用全局 actors，例如 `@MainActor`，用于 UI 绑定共享状态；永远不要将 `nonisolated(unsafe)` 作为同步替代方案。
- **`Mutex<Value>`**（iOS 18+，`Synchronization` 模块）：新代码的首选锁。在锁内存储受保护状态。`withLock { }` 模式。
- **`OSAllocatedUnfairLock`**（iOS 16+，`os` 模块）：在针对较旧 iOS 版本时使用。支持调试时的所有权断言。
- **`Atomic<Value>`**（iOS 18+，`Synchronization` 模块）：无锁原子操作，用于独立的计数器和标志。`Atomic` 是 `Sendable`，可以存储在 `Sendable` 持有类型中。仅在孤立指标中仅使用 `.relaxed`；使用获取/释放排序或锁来协调其他数据。

**关键规则：** 永远不要在 actors 内部放置锁（双重同步），并且永远不要在 await 跨持有锁（通过挂起阻塞线程，可能会耗尽协作池或死锁）。有关完整 API 详细信息、代码示例和选择锁与 actors 的决策指南，请参阅
[参考资料/synchronization-primitives.md](references/synchronization-primitives.md)。`Mutex.withLock` 和 `OSAllocatedUnfairLock.withLock` 使用同步闭包；该 API 形状是保持关键部分非挂起的原因。
使用运行时 `if #available(iOS 18, *)` 门禁 `Mutex` 和 `Atomic`，永远不要 `#if swift(...)` 或平台编译时检查。对于 `NSLock`，仅修正错误的 Sendable 前提，并避免解释适配机制。
如果遗留锁包装器确实需要 `@unchecked Sendable`，请命名不变量：所有可变状态都是私有的，所有访问都使用一个锁，没有可变引用逸出，并且没有锁在 await 跨持有。

## 常见错误

1. **阻塞主 actor。** 在 `@MainActor` 上的重计算冻结 UI。移到 `@concurrent` 函数。
2. **不必要的 @MainActor。** 网络层、数据处理和模型代码不需要 `@MainActor`。只有触摸 UI 的代码需要。
3. **为无状态代码使用 Actors。** 无可变状态意味着不需要 actor。使用普通的 struct 或函数。
4. **为不可变数据使用 Actors。** 使用 `Sendable` struct，而不是 actor。
5. **没有充分理由的 Task.detached。** 丢失优先级、任务本地值和取消传播。
6. **忘记任务取消。** 存储 `Task` 引用并取消它们，或使用 `.task` 视图修饰符。
7. **Tasks 中的保留循环。** 在长生命周期的存储 Tasks 中捕获 `self` 时使用 `[weak self]`。
8. **异步上下文中的信号量。** `DispatchSemaphore.wait()` 可能会阻塞协作执行器线程，并且在信号发送者需要被阻塞的执行器时可能会死锁。使用异步原语或结构化并发。
9. **隔离拆分。** 在一个类型中混合 `@MainActor` 和 `nonisolated` 属性。始终一致地隔离整个类型。
10. **MainActor.run 而不是静态隔离。** 优先使用 `@MainActor func` 而不是 `await MainActor.run { }`。
11. **默认使用 GCD 进行新的异步编排。** 优先使用 async/await、actors 和 task groups。在 API 要求队列时保留 dispatch queues，用于自定义执行器，或在有限的遗留互操作期间。测量的同步 CPU 密集型并行 for 仍然可以使用
    `DispatchQueue.concurrentPerform`；task group 是异步设计替代方案，而不是同步 API 的即插即用替换。遵循
    [桥接和互操作](references/bridging-interop.md#synchronous-parallel-for-concurrentperform-versus-task-groups) 中的捕获和内存安全审计。在审查此诊断的每个审查中，明确将 `@Sendable` 操作连接到非 `Sendable` 不安全缓冲区视图，并将任何选择退出限制为已证明的本地基础指针绑定。每个保留并行路径的审查都必须要求进行与串行相比的基准测试、串行结果和嵌套并行性检查。

## 审查清单

- [ ] 所有可变共享状态都是 actor 孤立的
- [ ] 没有数据竞争（没有未保护的跨隔离访问）
- [ ] 任务在不再需要时取消
- [ ] `@MainActor` 上没有阻塞调用
- [ ] actors 内部没有手动锁
- [ ] `Sendable` 适配是正确的（没有不合理的 `@unchecked`）
- [ ] Actor 重入已处理（没有跨 await 的状态假设）
- [ ] `@preconcurrency` 导入有移除计划记录
- [ ] 重工作使用 `@concurrent`，而不是 `@MainActor`
- [ ] SwiftUI 中使用 `.task` 修饰符而不是手动 Task 管理
- [ ] 同步并行循环证明非冲突的内存访问和指针生命周期不变量

## 参考资料

- [references/concurrency-patterns.md](references/concurrency-patterns.md) — 详细的并发模式和迁移示例
- [references/approachable-concurrency.md](references/approachable-concurrency.md) — 可访问并发模式快速参考
- [references/swiftui-concurrency.md](references/swiftui-concurrency.md) — SwiftUI 特定并发指南
- [references/synchronization-primitives.md](references/synchronization-primitives.md) — Mutex、OSAllocatedUnfairLock、锁与 actors
- [references/bridging-interop.md](references/bridging-interop.md) — 检查的连续性、委托桥接、GCD 迁移表
- [references/diagnostics.md](references/diagnostics.md) — 编译器诊断 → 修复参考，严格并发采用
- [references/async-algorithms.md](references/async-algorithms.md) — swift-async-algorithms：debounce、throttle、merge、combineLatest、chunks
