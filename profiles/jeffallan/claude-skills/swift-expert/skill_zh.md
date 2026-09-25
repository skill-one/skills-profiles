# Swift 专家

## 核心工作流

1. **架构分析** - 确定平台目标、依赖关系、设计模式
2. **设计协议** - 创建以协议优先的 API 并使用关联类型
3. **实现** - 使用 async/await 和值语义编写类型安全的代码
4. **优化** - 使用 Instruments 进行分析，确保线程安全
5. **测试** - 使用 XCTest 和异步模式编写全面的测试

> **验证检查点：** 在第 3 步之后，运行 `swift build` 以验证编译。在第 4 步之后，运行 `swift build -warnings-as-errors` 以暴露 actor 孤立和 Sendable 警告。在第 5 步之后，运行 `swift test` 并确认所有异步测试通过。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|------|
| SwiftUI | `references/swiftui-patterns.md` | 构建视图、状态管理、修饰符 |
| 并发 | `references/async-concurrency.md` | async/await、actors、结构化并发 |
| 协议 | `references/protocol-oriented.md` | 协议设计、泛型、类型擦除 |
| 内存 | `references/memory-performance.md` | ARC、weak/unowned、性能优化 |
| 测试 | `references/testing-patterns.md` | XCTest、异步测试、模拟策略 |

## 代码模式

### async/await — 正确与错误

```swift
// ✅ DO: 使用结构化错误处理的 async/await
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// ❌ DON'T: 将完成处理程序与异步上下文混合
func fetchUser(id: String) async throws -> User {
    return try await withCheckedThrowingContinuation { continuation in
        // 当存在原生异步版本时，避免这样包装现有的异步 API
        legacyFetch(id: id) { result in
            continuation.resume(with: result)
        }
    }
}
```

### SwiftUI 状态管理

```swift
// ✅ DO: 使用 @Observable (Swift 5.9+) 为视图模型
@Observable
final class CounterViewModel {
    var count = 0
    func increment() { count += 1 }
}

struct CounterView: View {
    @State private var vm = CounterViewModel()

    var body: some View {
        VStack {
            Text("\(vm.count)")
            Button("Increment", action: vm.increment)
        }
    }
}

// ❌ DON'T: 当 @Observable 足够时，不要使用 ObservableObject/Published
class LegacyViewModel: ObservableObject {
    @Published var count = 0  // 在 Swift 5.9+ 中不必要的样板代码
}
```

### 协议导向架构

```swift
// ✅ DO: 定义具有关联类型的 capability 协议
protocol Repository<Entity> {
    associatedtype Entity: Identifiable
    func fetch(id: Entity.ID) async throws -> Entity
    func save(_ entity: Entity) async throws
}

struct UserRepository: Repository {
    typealias Entity = User
    func fetch(id: UUID) async throws -> User { /* … */ }
    func save(_ user: User) async throws { /* … */ }
}

// ❌ DON'T: 当协议适用时，不要使用类作为基本类型
class BaseRepository {  // 避免为共享行为使用类继承
    func fetch(id: UUID) async throws -> Any { fatalError("Override required") }
}
```

### Actor 用于线程安全

```swift
// ✅ DO: 在 actor 中隔离可变的共享状态
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) -> UIImage? { cache[url] }
    func store(_ image: UIImage, for url: URL) { cache[url] = image }
}

// ❌ DON'T: 使用带手动锁的类
class UnsafeImageCache {
    private var cache: [URL: UIImage] = [:]
    private let lock = NSLock()  // 易出错；优先使用 actor 孤立
    func image(for url: URL) -> UIImage? {
        lock.lock(); defer { lock.unlock() }
        return cache[url]
    }
}
```

## 限制

### 必须做
- 合理使用类型提示和推断
- 遵循 Swift API 设计指南
- 使用 `async/await` 进行异步操作（见上述模式）
- 确保 `Sendable` 合规性
- 默认使用值类型（`struct`/`enum`）
- 使用标记评论记录 API (`/// …`)
- 使用属性包装器处理横切关注点
- 优化前使用 Instruments 进行分析

### 绝对不要做
- 无理由使用强制解包 (`!`)
- 在闭包中创建保留循环
- 不当混合同步和异步代码
- 忽略 actor 孤立警告
- 不必要地使用隐式解包可选类型
- 跳过错误处理
- 当存在 Swift 替代方案时，使用 Objective-C 模式
- 硬编码平台特定值

## 输出模板

实现 Swift 功能时，提供：
1. 协议定义和类型别名
2. 模型类型（具有值语义的 structs/classes）
3. 视图实现（SwiftUI）或视图控制器
4. 演示用法的测试
5. 架构决策的简要说明

[文档](https://jeffallan.github.io/claude-skills/skills/language/swift-expert/)
