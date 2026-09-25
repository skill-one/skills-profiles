# Swift 并发专家

## 概述

通过应用演员隔离、可发送安全性和现代并发模式，以最小的行为变更审查和修复 Swift 6.2+ 代码库中的并发问题。

## 工作流程

### 1. 评估问题

- 捕获确切的编译器诊断信息以及有问题的符号。
- 检查项目并发设置：Swift 语言版本（6.2+）、严格并发级别，以及是否启用可访问并发（默认演员隔离/主演员默认）。
- 确定当前演员上下文（`@MainActor`、`actor`、`nonisolated`）以及是否启用了默认演员隔离模式。
- 确认代码是否 UI 绑定或打算在主演员之外运行。

### 2. 应用最小的安全修复

优先选择保留现有行为同时满足数据竞争安全性的编辑。

常见修复：
- **UI 绑定型**：用 `@MainActor` 注解类型或相关成员。
- **主演员类型上的协议一致性**：使一致性隔离（例如，`extension Foo: @MainActor SomeProtocol`）。
- **全局/静态状态**：用 `@MainActor` 保护或移入演员。
- **后台工作**：将昂贵工作移入 `@concurrent` 异步函数在 `nonisolated` 类型上，或使用 `actor` 保护可变状态。
- **可发送错误**：优先选择不可变/值类型；仅在正确时添加 `Sendable` 一致性；除非能证明线程安全，否则避免 `@unchecked Sendable`。

### 3. 验证修复

- 重新构建并确认所有并发诊断已解决且未引入新警告。
- 运行测试套件检查回归——即使构建干净，并发变更也可能引入微妙的运行时问题。
- 如果修复暴露了新警告，将每个警告视为新的评估（返回步骤 1），迭代解决直到构建干净且测试通过。

### 示例

**UI 绑定型 — 添加 `@MainActor`**

```swift
// 之前：由于 ViewModel 从主线程访问但无演员隔离，存在数据竞争警告
class ViewModel: ObservableObject {
    @Published var title: String = ""
    func load() { title = "Loaded" }
}

// 之后：用 `@MainActor` 注解整个类型，使所有存储状态和方法自动隔离到主演员
@MainActor
class ViewModel: ObservableObject {
    @Published var title: String = ""
    func load() { title = "Loaded" }
}
```

**协议一致性隔离**

```swift
// 之前：编译器错误——SomeProtocol 方法非隔离，但符合类型是 @MainActor
@MainActor
class Foo: SomeProtocol {
    func protocolMethod() { /* 访问主演员状态 */ }
}

// 之后：将符合范围限定为 @MainActor，使要求在正确的隔离上下文中得到满足
@MainActor
extension Foo: SomeProtocol {
    func protocolMethod() { /* 安全访问主演员状态 */ }
}
```

**使用 `@concurrent` 的后台工作**

```swift
// 之前：昂贵计算阻塞主演员
@MainActor
func processData(_ input: [Int]) -> [Int] {
    input.map { heavyTransform($0) }   // 在主线程运行
}

// 之后：将重工作移出主演员，然后返回结果
// 调用者等待结果并保持在自己的演员上
nonisolated func processData(_ input: [Int]) async -> [Int] {
    await Task.detached(priority: .userInitiated) {
        input.map { heavyTransform($0) }
    }.value
}

// 或，使用 `@concurrent` 异步函数（Swift 6.2+）：
@concurrent
func processData(_ input: [Int]) async -> [Int] {
    input.map { heavyTransform($0) }
}
```

## 参考资料

- 参考 `references/swift-6-2-concurrency.md` 了解 Swift 6.2 变更、模式和示例。
- 参考 `references/approachable-concurrency.md` 当项目启用可访问并发模式时。
- 参考 `references/swiftui-concurrency-tour-wwdc.md` 获取 SwiftUI 特定的并发指导。
