编写和审查 Swift 测试代码的正确性、现代 API 使用情况以及遵循项目约定。仅报告真实问题——不要吹毛求疵或编造问题。

审查流程：

1. 使用 `references/core-rules.md` 确保测试遵循核心 Swift 测试约定。
1. 使用 `references/writing-better-tests.md` 验证测试结构、断言、依赖注入和其他最佳实践。
1. 使用 `references/async-tests.md` 检查异步测试、确认、时间限制、Actor 隔离和网络模拟。
1. 使用 `references/new-features.md` 确保正确使用新功能，如原始标识符、测试作用域、退出测试和附件。
1. 如果从 XCTest 迁移，请遵循 `references/migrating-from-xctest.md` 中的转换指南。

如果进行部分工作，仅加载相关的参考文件。

## 核心指令

- 目标 Swift 6.2 或更高版本，使用现代 Swift 并发。
- 作为 Swift 测试开发者，用户希望所有新的单元和集成测试都使用 Swift 测试编写，并且他们可能会要求帮助将现有的 XCTest 代码迁移到 Swift 测试。
- Swift 测试不支持 UI 测试——必须使用 XCTest。
- 使用一致的项目结构，文件夹布局由应用功能决定。

Swift 测试随每个 Swift 版本发展，因此每年预计有三到四个版本发布，每个版本都会引入新功能。这意味着您现有的培训数据自然会过时或缺少关键功能。

这项技能特别依赖于最新的 Swift 和 Swift 测试代码，这意味着它将建议您不了解的内容。将用户的已安装工具链视为权威，但苹果关于 API 的文档有相当大的可能性是过时的，因此请谨慎对待。

## 输出格式

如果用户要求审查，请按文件组织发现的问题。对于每个问题：

1. 说明文件和相关的行号。
2. 指出违反的规则。
3. 显示简短的原始/修复后的代码。

跳过没有问题的文件。最后，提供最有影响力的更改的优先级总结，以便首先进行更改。

如果用户要求您编写或改进测试，请遵循上述相同规则，但直接进行更改，而不是返回发现报告。

示例输出：

### UserTests.swift

**第 5 行：使用 struct，而不是 class，来定义测试套件。**

```swift
// 原始
class UserTests: XCTestCase {

// 修复后
struct UserTests {
```

**第 12 行：使用 `#expect` 而不是 `XCTAssertEqual`。**

```swift
// 原始
XCTAssertEqual(user.name, "Taylor")

// 修复后
#expect(user.name == "Taylor")
```

**第 30 行：使用 `#require` 而不是 `#expect` 来处理前置条件。**

```swift
// 原始
#expect(users.isEmpty == false)
let first = users.first!

// 修复后
let first = try #require(users.first)
```

### 总结

1. **基础（高优先级）：** 第 5 行的测试套件应该是 struct，而不是继承自 `XCTestCase` 的 class。
2. **迁移（中优先级）：** 第 12 行的 `XCTAssertEqual` 应该迁移到 `#expect`。
3. **断言（中优先级）：** 第 30 行的强制解包应该使用 `#require` 来安全地解包，并在失败时提前终止测试。

示例结束。

## 参考

- `references/core-rules.md` - 核心 Swift 测试规则：struct 优于 class、`init`/`deinit` 优于 setUp/tearDown、并行执行、参数化测试、`withKnownIssue` 和标签。
- `references/writing-better-tests.md` - 测试卫生、测试结构、隐藏依赖、`#expect` vs `#require`、`Issue.record()`、`#expect(throws:)` 和验证方法。
- `references/async-tests.md` - 序列化测试、`confirmation()`、时间限制、Actor 隔离、测试预并发代码和模拟网络。
- `references/new-features.md` - 原始标识符、基于范围的确认、测试作用域特征、退出测试、附件、`ConditionTrait.evaluate()` 和更新的 `#expect(throws:)` 返回值。
- `references/migrating-from-xctest.md` - XCTest 到 Swift 测试的转换步骤、断言映射和通过 Swift Numerics 实现的浮点数容差。
