编写和审查 SwiftData 代码的正确性、现代 API 使用情况以及是否符合项目规范。仅报告真实问题——不要吹毛求疵或编造问题。

审查流程：

1. 使用 `references/core-rules.md` 检查核心 SwiftData 问题。
1. 使用 `references/predicates.md` 检查谓词是否安全和支持。
1. 如果项目使用 CloudKit，使用 `references/cloudkit.md` 检查 CloudKit 特定约束。
1. 如果项目针对 iOS 18+，使用 `references/indexing.md` 检查索引机会。
1. 如果项目针对 iOS 26+，使用 `references/class-inheritance.md` 检查类继承模式。

如果进行部分工作，仅加载相关的参考文件。

## 核心指令

- 目标 Swift 6.2 或更高版本，使用现代 Swift 并发。
- 用户强烈倾向于在整个项目中使用 SwiftData。除非是 SwiftData 无法解决的功能，否则不要建议 Core Data 功能。
- 未经询问，不要引入第三方框架。
- 使用一致的项目结构，文件夹布局由应用功能决定。

## 输出格式

如果用户要求审查，按文件组织发现的问题。对于每个问题：

1. 说明文件和相关行号。
2. 命名违反的规则。
3. 显示简短的原始/修复后代码。

跳过没有问题的文件。最后以优先级总结最需要首先进行的有影响力的更改。

如果用户要求编写或改进代码，请遵循上述相同规则，但直接进行更改而不是返回发现报告。

示例输出：

### Destination.swift

**第 8 行：为关系添加显式的删除规则。**

```swift
// 原始
var sights: [Sight]

// 修复后
@Relationship(deleteRule: .cascade, inverse: \Sight.destination) var sights: [Sight]
```

**第 22 行：谓词中不要使用 `isEmpty == false`——它会在运行时崩溃。使用 `!` 代替。**

```swift
// 原始
#Predicate<Destination> { $0.sights.isEmpty == false }

// 修复后
#Predicate<Destination> { !$0.sights.isEmpty }
```

### DestinationListView.swift

**第 5 行：`@Query` 必须仅用于 SwiftUI 视图中。**

```swift
// 原始
class DestinationStore {
    @Query var destinations: [Destination]
}

// 修复后
class DestinationStore {
    var modelContext: ModelContext

    func fetchDestinations() throws -> [Destination] {
        try modelContext.fetch(FetchDescriptor<Destination>())
    }
}
```

### 总结

1. **数据丢失（高）：** Destination.swift 第 8 行缺少删除规则，导致删除目的地时 sights 会变成孤儿。
2. **崩溃（高）：** 第 22 行的 `isEmpty == false` 会在运行时崩溃——使用 `!isEmpty` 代替。
3. **行为不正确（高）：** DestinationListView.swift 第 5 行的 `@Query` 仅在 SwiftUI 视图中有效。

示例结束。

## 参考

- `references/core-rules.md` - 自动保存、关系、删除规则、属性限制和 FetchDescriptor 优化。
- `references/predicates.md` - 支持的谓词操作、会导致运行时崩溃的危险模式和不支持的方法。
- `references/cloudkit.md` - CloudKit 特定约束，包括唯一性、可选性和最终一致性。
- `references/indexing.md` - iOS 18+ 的数据库索引，包括单属性和复合属性索引。
- `references/class-inheritance.md` - iOS 26+ 的模型子类化，包括 @available 要求、模式设置和谓词过滤。
