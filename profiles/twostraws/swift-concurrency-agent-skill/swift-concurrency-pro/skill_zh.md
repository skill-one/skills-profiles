审查 Swift 并发代码的正确性、现代 API 使用情况以及是否符合项目规范。仅报告真实问题——不要吹毛求疵或编造问题。

审查流程：

1. 使用 `references/hotspots.md` 扫描已知危险模式，以确定检查优先级。
1. 检查 Swift 6.2 并发行为，使用 `references/new-features.md`。
1. 验证 actor 的使用是否符合可重入性和隔离性，使用 `references/actors.md`。
1. 确保在适当情况下优先使用结构化并发而不是非结构化并发，使用 `references/structured.md`。
1. 检查非结构化任务的使用是否正确，使用 `references/unstructured.md`。
1. 验证取消操作是否正确处理，使用 `references/cancellation.md`。
1. 验证异步流和延续的使用情况，使用 `references/async-streams.md`。
1. 检查同步和异步世界之间的桥接代码，使用 `references/bridging.md`。
1. 审查任何遗留并发迁移，使用 `references/interop.md`。
1. 与常见失败模式进行交叉检查，使用 `references/bug-patterns.md`。
1. 如果项目存在严格并发错误，使用 `references/diagnostics.md` 将诊断映射到修复方案。
1. 如果审查测试，检查异步测试模式，使用 `references/testing.md`。

如果进行部分审查，仅加载相关的参考文件。

## 核心指令

- 针对 Swift 6.2 或更高版本进行严格并发检查。
- 如果代码跨越多个目标或包，在假设行为应匹配之前，比较它们的并发构建设置。
- 优先使用结构化并发（任务组）而不是非结构化并发（`Task {}`）。
- 新代码优先使用 Swift 并发而不是 Grand Central Dispatch。GCD 仍然可以在低级代码、框架互操作或需要队列和锁的性能关键同步工作中接受——不要将其标记为错误。
- 如果 API 同时提供 `async`/`await` 和基于闭包的变体，始终优先使用 `async`/`await`。
- 在询问之前不要引入第三方并发框架。
- 不要建议使用 `@unchecked Sendable` 来修复编译器错误。它在不修复潜在竞争条件的情况下静默地抑制了诊断。优先使用 actor、值类型或 `sending` 参数。唯一合法的使用情况是对于具有内部锁且可证明是线程安全的类型。

## 输出格式

按文件组织发现的问题。对于每个问题：

1. 说明文件和相关的行号。
2. 指出违反的规则。
3. 显示简短的原始/修复后的代码。

跳过没有问题的文件。最后以优先级总结最需要首先进行的影响最大的更改。

示例输出：

### DataLoader.swift

**行 18：Actor 可重入性——状态可能在 `await` 期间发生变化。**

```swift
// 原始
actor Cache {
    var items: [String: Data] = [:]

    func fetch(_ key: String) async throws -> Data {
        if items[key] == nil {
            items[key] = try await download(key)
        }
        return items[key]!
    }
}

// 修复后
actor Cache {
    var items: [String: Data] = [:]

    func fetch(_ key: String) async throws -> Data {
        if let existing = items[key] { return existing }
        let data = try await download(key)
        items[key] = data
        return data
    }
}
```

**行 34：使用 `withTaskGroup` 而不是在循环中创建任务。**

```swift
// 原始
for url in urls {
    Task { try await fetch(url) }
}

// 修复后
try await withThrowingTaskGroup(of: Data.self) { group in
    for url in urls {
        group.addTask { try await fetch(url) }
    }

    for try await result in group {
        process(result)
    }
}
```

### 总结

1. **正确性（高）：** 行 18 的 Actor 可重入性错误可能导致重复下载和强制解包崩溃。
2. **结构（中）：** 行 34 的循环中非结构化任务丢失取消传播。

示例结束。

## 参考

- `references/hotspots.md` - 代码审查的 Grep 目标：已知危险模式和每个模式需要检查的内容。
- `references/new-features.md` - 改变审查建议的 Swift 6.2 更改：默认 actor 隔离、隔离的协议、调用者 actor 异步行为、`@concurrent`、`Task.immediate`、任务命名和优先级升级。
- `references/actors.md` - Actor 可重入性、共享状态注释、全局 actor 推断和隔离模式。
- `references/structured.md` - 任务组优于循环、丢弃任务组、并发限制。
- `references/unstructured.md` - Task 与 Task.detached、何时 `Task {}` 是代码异味。
- `references/cancellation.md` - 取消传播、协作检查、损坏的取消模式。
- `references/async-streams.md` - AsyncStream 工厂、延续生命周期、背压。
- `references/bridging.md` - 检查延续、包装遗留 API、`@unchecked Sendable`。
- `references/interop.md` - 从 GCD 迁移、`Mutex`/锁、完成处理程序、代理和 Combine。
- `references/bug-patterns.md` - 常见并发失败模式及其修复方案。
- `references/diagnostics.md` - 严格并发编译器错误、协议一致性修复和可能的补救措施。
- `references/testing.md` - 使用 Swift Testing 的异步测试策略、竞争检测、避免基于时间的测试。
