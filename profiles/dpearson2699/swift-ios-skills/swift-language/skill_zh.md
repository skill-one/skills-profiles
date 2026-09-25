# Swift 语言模式

应用当前的 Swift 语言语法，而不改变行为或求值顺序。
将深层解码路由到 `swift-codable`，格式化路由到 `swift-formatstyle`，命名路由到 `swift-api-design-guidelines`，并发路由到 `swift-concurrency`，以及 SwiftUI 状态/视图工作路由到 `swiftui-patterns`。

## 目录

- [If/switch 表达式](#ifswitch-expressions)
- [带类型错误的函数](#typed-throws)
- [结果构建器](#result-builders)
- [属性包装器](#property-wrappers)
- [不透明类型和存在类型](#opaque-and-existential-types)
- [guard 模式](#guard-patterns)
- [Never 类型](#never-type)
- [正则表达式构建器](#regex-builders)
- [Codable 最佳实践](#codable-best-practices)
- [现代集合 API](#modern-collection-apis)
- [FormatStyle](#formatstyle)
- [字符串插值](#string-interpolation)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考文献](#references)

## If/switch 表达式

为了现代化，固定当前行为和求值顺序，进行一次语义重写，编译受影响的模块，并运行聚焦的测试用例/测试。在继续之前修复任何更改；重复此过程，直到行为得到保留。

Swift 5.9+ 允许 `if` 和 `switch` 作为返回值的表达式。使用它们直接进行赋值、返回或初始化。

```swift
// 从 if 表达式赋值
let icon = if isComplete { "checkmark.circle.fill" } else { "circle" }

// 从 switch 表达式赋值
let label = switch status {
case .draft: "Draft"
case .published: "Published"
case .archived: "Archived"
}

// 可用于返回位置
func badgeText(for priority: Priority) -> String {
    switch priority {
    case .high: "High"
    case .medium: "Medium"
    case .low: "Low"
    }
}
```

**规则：**
- 每个分支必须产生相同类型的值。
- 不允许多语句分支——每个分支都是一个单一的表达式。
- 作为函数参数使用时，用括号括起来以避免歧义。

## 带类型错误的函数

Swift 6+ 允许指定函数抛出的错误类型。

```swift
enum ValidationError: Error {
    case tooShort, invalidCharacters, alreadyTaken
}

func validate(username: String) throws(ValidationError) -> String {
    guard username.count >= 3 else { throw .tooShort }
    guard username.allSatisfy(\.isLetterOrDigit) else { throw .invalidCharacters }
    return username.lowercased()
}

// 调用者获得带类型的错误——无需强制转换
do {
    let name = try validate(username: input)
} catch {
    // error 是 ValidationError，而不是任何 Error
    switch error {
    case .tooShort: print("Too short")
    case .invalidCharacters: print("Invalid characters")
    case .alreadyTaken: print("Taken")
    }
}
```

**规则：**
- 仅当调用者受益于详尽的错误处理时，才使用 `throws(SomeError)`。对于混合错误源，使用无类型的 `throws`。
- 当现代化一个具有本地错误枚举的辅助函数时，优先使用 `throws(ErrorEnum)` 并注明 Swift 6+。
- `throws(Never)` 标记一个语法上会抛出但实际不会抛出的函数——在泛型上下文中很有用。
- 带类型错误的函数会传播：一个调用 `throws(A)` 和 `throws(B)` 的函数必须自身抛出涵盖两者的类型（或使用无类型的 `throws`）。

## 结果构建器

`@resultBuilder` 启用 DSL 风格的语法。SwiftUI 的 `@ViewBuilder` 是最常见的例子，但你可以为任何领域创建自定义构建器。

```swift
@resultBuilder
struct ArrayBuilder<Element> {
    static func buildBlock(_ components: [Element]...) -> [Element] {
        components.flatMap { $0 }
    }
    static func buildExpression(_ expression: Element) -> [Element] { [expression] }
    static func buildOptional(_ component: [Element]?) -> [Element] { component ?? [] }
    static func buildEither(first component: [Element]) -> [Element] { component }
    static func buildEither(second component: [Element]) -> [Element] { component }
    static func buildArray(_ components: [[Element]]) -> [Element] { components.flatMap { $0 } }
}

func makeItems(@ArrayBuilder<String> content: () -> [String]) -> [String] { content() }

let items = makeItems {
    "Always included"
    if showExtra { "Conditional" }
    for name in names { name.uppercased() }
}
```

**构建器方法：** `buildBlock`（组合语句），`buildExpression`（单个值），`buildOptional`（`if` 而无 `else`），`buildEither`（`if/else`），`buildArray`（`for..in`），`buildFinalResult`（可选的后处理）。

## 属性包装器

自定义 `@propertyWrapper` 类型封装存储和访问模式。

```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    var projectedValue: ClosedRange<Value> { range }

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

// 使用
struct Volume {
    @Clamped(0...100) var level: Int = 50
}

var v = Volume()
v.level = 150   // clamped to 100
print(v.$level) // projected value: 0...100
```

**设计规则：**
- `wrappedValue` 是主要的 getter/setter。
- `projectedValue`（通过 `$property` 访问）提供元数据或绑定。
- 属性包装器可以组合：`@A @B var x` 首先应用外部包装器。
- 当简单的计算属性足够时，不要使用属性包装器。

## 不透明类型和存在类型

### `some Protocol`（不透明类型）

调用者不知道具体类型，但编译器知道。一个 `-> some P` 返回在所有返回分支中都有一个固定的具体类型。

```swift
func makeCollection() -> some Collection<Int> {
    [1, 2, 3]  // Always returns Array<Int> -- compiler knows the concrete type
}
```

使用 `some` 的场景：
- 返回类型：当你想隐藏实现但保留类型身份时。
- 参数类型（Swift 5.7+）：`some P` 是 `<T: P>` 类型的简写。

### `any Protocol`（存在类型）

一个可以在运行时持有任何符合类型的存在盒子。它使用动态分发，并且当值不适合内联缓冲区时可能会分配。

```swift
func process(items: [any StringProtocol]) {
    for item in items {
        print(item.uppercased())
    }
}
```

### 选择时的建议

| 使用 `some` | 使用 `any` |
|---|---|
| 返回类型隐藏具体类型 | 异构集合 |
| 函数参数（替代简单泛型） | 需要动态类型擦除 |
| 更好的性能（静态分发） | 协议有 `Self` 或关联类型要求需要擦除 |

**经验法则：** 默认使用 `some`。仅在需要异构集合或运行时类型灵活性时使用 `any`。

## guard 模式

`guard` 强制执行前置条件并启用早期退出。它使快乐路径左对齐并减少嵌套。

```swift
func processOrder(_ order: Order?) throws -> Receipt {
    // 解包可选值
    guard let order else { throw OrderError.missing }

    // 验证条件
    guard order.items.isEmpty == false else { throw OrderError.empty }
    guard order.total > 0 else { throw OrderError.invalidTotal }

    // 布尔检查
    guard order.isPaid else { throw OrderError.unpaid }

    // 模式匹配
    guard case .confirmed(let date) = order.status else {
        throw OrderError.notConfirmed
    }

    return Receipt(order: order, confirmedAt: date)
}
```

**最佳实践：**
- 使用 `guard` 进行前置条件，`if` 进行分支逻辑。
- 组合相关的 guard：`guard let a, let b else { return }`。
- `else` 块必须退出作用域：`return`，`throw`，`continue`，`break` 或 `fatalError()`。
- 使用简写解包：`guard let value else { ... }`（Swift 5.7+）。

## Never 类型

`Never` 是一个无实例类型，用于那些永远不会产生值的代码路径。它只在与值表达式或推断相关的行为中表现得像 Swift 的底部类型；它不是通用的类型证明者，不会隐式符合任意协议，并且不能满足 `T: P` 类型的泛型约束，除非约束对 `Never` 有效。

```swift
// 终止程序的函数
func crashWithDiagnostics(_ message: String) -> Never {
    let diagnostics = gatherDiagnostics()
    logger.critical("\(message): \(diagnostics)")
    fatalError(message)
}

enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}
// Result<String, Never> -- 一个永远不会失败的 Result

// 详尽的 switch：不需要默认值，因为 Never 没有案例
func handle(_ result: Result<String, Never>) {
    switch result {
    case .success(let value): print(value)
    // 不需要 .failure 案例——编译器知道它是不可能的
    }
}
```

## 正则表达式构建器

Swift 5.7+ 正则表达式构建器 DSL 提供编译时检查的、可读的模式。

```swift
import Foundation
import RegexBuilder

// 将 "2024-03-15" 解析为组件
let dateRegex = Regex {
    Capture { /\d{4}/ }; "-"; Capture { /\d{2}/ }; "-"; Capture { /\d{2}/ }
}

if let match = "2024-03-15".firstMatch(of: dateRegex) {
    let (_, year, month, day) = match.output
    _ = (year, month, day)
}

// TryCapture 带转换
let priceRegex = Regex {
    "$"
    TryCapture { OneOrMore(.digit); "."; Repeat(.digit, count: 2) }
        transform: { Decimal(string: String($0)) }
}
```

**何时使用构建器 vs. 字面量：**
- 构建器：复杂模式，可重用组件，对捕获的强类型。
- 字面量（`/pattern/`）：简单模式，熟悉正则表达式语法。
- 两者可以混合：在构建器块中嵌入 `/.../` 字面量。

## Codable 最佳实践

仅对实际有效载荷形状或转换不匹配进行自定义解码。加载
[扩展 Swift 模式](references/swift-patterns-extended.md) 以获取紧凑的语言示例；使用 `swift-codable` 进行实现和验证。

## 现代集合 API

优先使用这些现代 API 而不是手动循环：

```swift
let numbers = [1, 2, 3, 4, 5, 6, 7, 8]

// count(where:) -- 代替 .filter { }.count
let evenCount = numbers.count(where: { $0.isMultiple(of: 2) })

// contains(where:) -- 在第一个匹配时短路
let hasNegative = numbers.contains(where: { $0 < 0 })

// first(where:) / last(where:)
let firstEven = numbers.first(where: { $0.isMultiple(of: 2) })

// String replacing() -- Swift 5.7+，返回新字符串
let cleaned = rawText.replacing(/\s+/, with: " ")
let snakeCase = name.replacing("_", with: " ")

// compactMap -- 从转换中解包可选值
let ids = strings.compactMap { Int($0) }

// flatMap -- 展平嵌套集合
let allTags = articles.flatMap(\.tags)

// Dictionary(grouping:by:)
let byCategory = Dictionary(grouping: items, by: \.category)

// reduce(into:) -- 高效的累积
let freq = words.reduce(into: [:]) { counts, word in
    counts[word, default: 0] += 1
}
```

## FormatStyle

使用 `.formatted()` 和 `Text(_:format:)` 进行基本显示。将样式选择、解析、本地化测试和可重用格式器设计路由到 `swift-formatstyle`。

## 字符串插值

扩展 `DefaultStringInterpolation` 以进行特定领域的格式化。使用 `"""` 进行多行字符串（缩进相对于闭合的 `"""`）。参见 [references/swift-patterns-extended.md](references/swift-patterns-extended.md) 获取自定义插值示例。

## 常见错误

1. **使用 `any` 而不是 `some`。** 默认使用 `some` 对于返回类型和参数，但每个 `-> some P` 分支必须返回相同的具体类型。
2. **手动循环或 `.filter { }.count` 而不是集合 API。** 使用 `count(where:)` 进行条件计数，以及 `contains(where:)`、`compactMap` 和 `flatMap` 而不是额外的迭代或数组。
3. **`DateFormatter` 而不是 FormatStyle。** `.formatted()` 更简单、类型安全，并自动处理本地化。
4. **强制解包 Codable 解码。** 使用 `decodeIfPresent` 带默认值，用于可选或缺失的键。
5. **现代化期间重新排序前置条件。** 使用 `guard` 而不移动规范化或转换之前进行验证。
6. **无效的 `@c` 签名。** 假设 `UnsafeBufferPointer` 是一个 Swift 结构/值包装器，然后拒绝 `String`、`Array`、闭包和泛型占位符。
7. **忽略带类型错误的函数。** 当函数具有单个、明确的错误类型时，带类型错误的函数为调用者提供详尽的 switch 而无需强制转换。
8. **过度使用属性包装器。** 当没有重用或投影值需要时，计算属性更简单。
9. **未指定 `Never`。** 对于 `Result<T, Never>` 或 `throws(Never)`，明确写出例外：Never 不会隐式符合任意协议，不能满足任意 `T: P` 约束，并且仅在有效表达式/推断上下文中才像底部类型。
10. **拥有兄弟实现。** 命名技能所有者并停止。避免为 `CodingKeys`、解码器、格式器、SwiftUI 或并发创建片段。

## 审查清单

- [ ] `some` 仅用于每个不透明返回分支具有一个具体类型
- [ ] `guard` 用于前置条件；`count(where:)` 代替手动计数或 `.filter { }.count`
- [ ] `.formatted()` 代替 `DateFormatter`/`NumberFormatter`
- [ ] Codable 类型使用 `CodingKeys` 进行 API 映射；`decodeIfPresent` 带默认值用于可选字段
- [ ] if/switch 表达式用于条件赋值；属性包装器有明确的重用理由
- [ ] Regex builder 用于复杂模式（简单模式可以使用字面量）
- [ ] 带类型错误的函数用于单个本地错误域，并注明 Swift 6+ 兼容性
- [ ] `@c` 修正调用 `UnsafeBufferPointer` 为 Swift 结构/值包装器，并按名称枚举拒绝的 Swift 类型
- [ ] `Never` 指导使用无实例和底部类型，并说明不隐式符合任意协议/泛型约束
- [ ] 深层 Codable 路由到 `swift-codable`；FormatStyle API 路由到 `swift-formatstyle`；市场/本地化显示 QA 路由到 `ios-localization`；命名/并发/SwiftUI 路由到兄弟技能

## 参考文献

- 扩展模式和 Codable 示例：[references/swift-patterns-extended.md](references/swift-patterns-extended.md)
- 属性和 C 互操作：[references/swift-attributes-interop.md](references/swift-attributes-interop.md)
