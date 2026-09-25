# Swift 测试

Swift 测试是 Swift (Xcode 16+，Swift 6+) 的现代测试框架。对于新的单元测试，请优先使用它。在迁移仍在进行中时保留 XCTest，并使用 XCTest 进行 UI 自动化、性能 API、Objective-C 异常测试以及常见的快照测试工具。

## 目录

- [基本测试](#基本测试)
- [`@Test` 特性](#test-特性)
- [#expect 和 #require](#expect-and-require)
- [`@Suite` 和测试组织](#suite-and-test-组织)
- [执行模型](#执行模型)
- [XCTest 迁移边界](#xctest-迁移边界)
- [已知问题](#已知问题)
- [附加模式](#附加模式)
- [常见错误](#常见错误)
- [测试附件](#测试附件)
- [退出测试](#退出测试)
- [版本控制 API](#版本控制api)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

---

## 基本测试

```swift
import Testing

@Test("用户可以更新他们的显示名称")
func updateDisplayName() {
    var user = User(name: "Alice")
    user.name = "Bob"
    #expect(user.name == "Bob")
}
```

## `@Test` 特性

```swift
@Test("验证电子邮件格式")                                    // 显示名称
@Test(.tags(.验证, .电子邮件))                                  // 标签
@Test(.disabled("服务器迁移中"))                   // 禁用
@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] != nil)) // 条件
@Test(.bug("https://github.com/org/repo/issues/42"))               // 错误引用
@Test(.timeLimit(.minutes(1)))                                     // 时间限制
@Test("超时处理", .tags(.网络), .timeLimit(.seconds(30))) // 组合
```

## #expect 和 #require

```swift
// #expect 记录失败但继续执行
#expect(result == 42)
#expect(name.isEmpty == false)
#expect(items.count > 0, "项目不应为空")

// #expect 带错误类型检查
#expect(throws: ValidationError.self) {
    try validate(email: "not-an-email")
}

// #expect 带特定错误值
#expect {
    try validate(email: "")
} throws: { error in
    guard let err = error as? ValidationError else { return false }
    return err == .empty
}

// #require 记录失败并停止测试 (如 XCTUnwrap)
let user = try #require(await fetchUser(id: 1))
#expect(user.name == "Alice")

// #require 用于可选类型 -- 解包或失败
let first = try #require(items.first)
#expect(first.isValid)
```

**规则：当后续断言依赖于值时使用 `#require`。用于独立检查的 `#expect`。**

## `@Suite` 和测试组织

有关套件组织、确认模式、已知问题处理和执行模型详细信息，请参阅 [参考资料/testing-patterns.md](references/testing-patterns.md)。

## 执行模型

Swift 测试默认并行运行测试。除非您明确设计，否则不要假设测试顺序、共享套件实例或对可变状态的独占访问。

```swift
@Suite(.serialized)
struct KeychainTests {
    @Test func storesToken() throws { /* ... */ }
    @Test func deletesToken() throws { /* ... */ }
}
```

当测试或套件必须按顺序运行一次，因为它会触及共享的外部状态时，使用 `.serialized`。它不会使该范围内的不相关测试按顺序运行。

**规则：**
- 每个测试必须设置自己的状态。
- 共享的可变全局变量是错误，除非受保护或有意序列化。
- `@Suite(.serialized)` 用于独占执行，而不是表示测试之间的逻辑顺序。
- 如果测试依赖于顺序，将它们组合成一个测试或将序列移到共享辅助代码中。

## XCTest 迁移边界

Swift 测试单元测试不继承自 `XCTestCase`。在套件类型（如 `struct`、`class` 或 `actor`）上的自由函数或方法上声明 `@Test`；当不需要实例固定时使用 `static` 或 `class` 方法。

XCTest 和 Swift 测试在迁移期间可以共存。一次迁移一个文件或套件，比较发现/通过/失败/跳过计数，并将 UI 自动化、性能基准和常见快照流程保留在 XCTest/XCUITest 或快照工具上。当这使运行器期望更清晰时，将文件或目标分开。

对于 Xcode 27 时代的混合辅助工具，检查配置的互操作性模式，而不是声称跨框架 API 被禁止。旧测试计划继承 `limited`；新项目使用 `complete`；`strict` 和 `none` 也可以使用。在迁移期间优先使用 `complete` 或 `strict`，并在需要时使用 `SWIFT_TESTING_XCTEST_INTEROP_MODE` for SwiftPM。有关模式矩阵和工具链门，请参阅 [参考资料/testing-advanced.md](references/testing-advanced.md)。

不要机械地用 `#expect` 替换每个 XCTest 断言；保留这些迁移默认值所需的解包和无条件失败：
- `XCTAssert*` -> `#expect(...)`
- `XCTUnwrap` 或任何后续检查所需的值 -> `try #require(...)`
- `XCTFail("...")` 或手动无条件问题 -> `Issue.record("...")`
- UI 测试、性能基准和常见快照测试流程保留在 XCTest/XCUITest 或快照工具上。
- 在单个 `@Test` 函数上而不是在套件类型或其包含类型上添加 `@available`。

有关迁移示例，请参阅 [参考资料/testing-patterns.md](references/testing-patterns.md)，有关 Swift/Xcode 版本门，请参阅 [参考资料/testing-advanced.md](references/testing-advanced.md)。

## 已知问题

标记预期失败，以便它们不会导致测试失败：

```swift
withKnownIssue("丙烷罐是空的") {
    #expect(truck.grill.isHeating)
}

// 间歇性 / 不稳定的失败
withKnownIssue(isIntermittent: true) {
    #expect(service.isReachable)
}

// 条件已知问题
withKnownIssue {
    #expect(foodTruck.grill.isHeating)
} when: {
    !hasPropane
}
```

如果没有记录已知问题，Swift 测试会记录一个独特的问题，通知您问题可能已解决。

## 附加模式

有关参数化测试、标签和套件、异步测试、特性以及执行模型详细信息，请参阅 [参考资料/testing-patterns.md](references/testing-patterns.md)。

## 测试附件

将诊断数据附加到测试结果以进行调试失败。有关完整示例，请参阅 [参考资料/testing-patterns.md](references/testing-patterns.md)。

```swift
@Test func generateReport() async throws {
    let report = try generateReport()
    Attachment.record(report.data, named: "report.json")
    #expect(report.isValid)
}
```

对于图像附件及其工具链门，请使用 [版本控制 API](#版本控制api) 中的规范表格。

## 退出测试

测试调用 `exit()`、`fatalError()` 或在支持的环境中调用 `preconditionFailure()` 的代码。在纠正退出测试代码时，声明来自 [版本控制 API](#版本控制api) 的确切门。

```swift
@Test func invalidInputCausesExit() async {
    await #expect(processExitsWith: .failure) {
        processInvalidInput()  // 调用 fatalError()
    }
}
```

## 版本控制 API

对于高级 API，在修正旁边声明确切的工具链和运行时门。这是规范摘要；[参考资料/testing-advanced.md](references/testing-advanced.md) 包含详细的矩阵和示例。

```swift
@Test func exitsWithCapturedCode() async {
    let expectedCode: Int32 = 42
    await #expect(processExitsWith: .failure) { [expectedCode] in
        exit(expectedCode)
    }
}
```

| 用户代码以进行修正 | 当前指导 |
|---|---|
| `#expect(exitsWith:)` | 使用 `await #expect(processExitsWith: .failure) { ... }`。退出测试需要 Swift 6.2 / Xcode 26.0 或更高版本，并在 macOS、Linux、FreeBSD、OpenBSD 和 Windows 运行时目标上受支持，不支持 iOS、tvOS 或 watchOS。对于 iOS 应用程序目标，通过较小的非退出 API 或支持的宿主/工具目标测试致命路径逻辑。 |
| 退出测试闭包读取外部值 | 添加显式捕获列表，例如 `{ [expectedCode] in ... }`。退出测试捕获列表需要 Swift 6.3 编译器；捕获的值必须是 `Sendable` 和 `Codable`。 |
| 测试中等待工作的 `Test.cancel()` | 使测试 `async throws` 并调用 `try Test.cancel("reason")`。`Test.cancel(_:)` 需要 Swift 6.3 / Xcode 26.4 时代支持。 |
| `Issue.record(..., severity: .warning)` | 使用 `Issue.record("message", severity: .warning)`。警告严重性会报告，但不会使测试失败，并且需要 Swift 6.3 / Xcode 26.4 时代支持。 |
| `Attachment(image, named:).record()` | 使用 `Attachment.record(image, named: "name", as: .png)`。导入 `Testing` 以及相关的图像框架；Apple 平台的图像值包括 `UIImage`、`CGImage`、`CIImage` 和 `NSImage`。图像附件记录需要 Swift 6.3 / Xcode 26.4 时代支持。 |

## 常见错误

1. **测试实现而不是行为。** 测试代码做什么，而不是如何做。
2. **没有错误路径测试。** 如果函数可以抛出，测试抛出路径。
3. **不稳定的异步测试或睡眠。** 使用 `confirmation`、时钟注入或并发原语，而不是睡眠。
4. **测试之间共享可变状态。** 每个测试通过 `init()` 在 `@Suite` 中设置自己的状态。
5. **UI 测试中缺少可访问性标识符。** XCUITest 查询依赖于它们。
6. **未测试取消。** 如果代码支持 `Task` 取消，请验证它是否干净地取消。
7. **不明确的迁移边界。** 跟随 XCTest 迁移边界，而不是将任一框架视为全有或全无的选择。
8. **跨测试共享的非 `Sendable` 辅助工具。** 使共享辅助工具 `Sendable`；用 `@MainActor` 注释依赖于 MainActor 的测试代码。
9. **将序列化视为顺序。** 测试默认并行运行；`.serialized` 保护独占状态，但不会使一个测试为另一个测试提供输入。

## 审查清单

- [ ] 所有新测试使用 Swift 测试 (`@Test`，`#expect`)，而不是 XCTest 断言
- [ ] 测试名称描述行为 (`fetchUserReturnsNilOnNetworkError` 而不是 `testFetchUser`)
- [ ] 错误路径有专门的测试
- [ ] 异步测试使用 `confirmation()`，而不是 `Task.sleep`
- [ ] 参数化测试用于重复变化
- [ ] 标签应用于过滤 (`.critical`，`.slow`)
- [ ] 模拟符合协议，而不是继承具体类型
- [ ] 测试之间没有共享可变状态
- [ ] 测试不依赖于声明顺序或共享套件实例
- [ ] `.serialized` 仅用于真正独占状态，而不是模拟工作流顺序
- [ ] 测试取消可取消的异步操作

## 参考资料

- 测试模式：[参考资料/testing-patterns.md](references/testing-patterns.md)
- 高级测试（警告、取消、图像附件）：[参考资料/testing-advanced.md](references/testing-advanced.md)
