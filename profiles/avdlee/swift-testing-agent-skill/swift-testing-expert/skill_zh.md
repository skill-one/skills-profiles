# Swift 测试

## 概述

使用此技能，通过现代 Swift 测试 API 编写、审查、迁移和调试 Swift 测试。优先考虑可读性强的测试、稳健的并行执行、清晰的诊断，以及在需要时从 XCTest 进行增量迁移。

## 代理行为契约（请遵循这些规则）

1. 优先使用 Swift 测试进行 Swift 单元测试和集成测试，但对于 UI 自动化（`XCUIApplication`）、性能指标（`XCTMetric`）和纯 Objective-C 测试代码，请保留 XCTest。
2. 将 `#expect` 视为默认断言，并在后续行依赖于先决值时使用 `#require`。
3. 默认采用并行安全指南。如果测试未隔离，请首先建议修复共享状态，然后再应用 `.serialized`。
4. 优先使用 traits 进行行为和元数据（`.enabled`、`.disabled`、`.timeLimit`、`.bug`、标签）的配置，而不是命名约定或临时性注释。
5. 当多个测试共享逻辑且仅在输入值上不同时，建议使用参数化测试。
6. 在测试函数上使用 `@available` 以进行 OS 限制的行为，而不是在测试体内部使用运行时 `#available` 检查；永远不要用 `@available` 注解测试套件类型。
7. 保持迁移建议的增量性：首先转换断言，然后组织套件，然后引入参数化/traits。
8. 仅在测试目标中导入 `Testing`，绝不在应用/库/二进制目标中导入。

## 初步 60 秒（分诊模板）

- 明确目标：新测试、迁移、不稳定失败、性能、CI 过滤或异步等待。
- 收集最小事实：
  - Xcode/Swift 版本和平台目标
  - 测试当前是否使用 XCTest、Swift 测试或两者都使用
  - 失败是否确定或不稳定
  - 测试是否访问共享资源（数据库、文件、网络、全局状态）
- 快速分支：
  - 重复测试 -> 参数化测试
  - 噪音或不稳定失败 -> 已知问题处理和测试隔离
  - 迁移问题 -> XCTest 映射和共存策略
  - 异步回调复杂性 -> 继续使用/等待模式

## 路由图（快速阅读正确的参考）

- 测试构建块和套件组织 -> `references/fundamentals.md`
- `#expect`、`#require` 和抛出预期 -> `references/expectations.md`
- Traits、标签和 Xcode 测试计划过滤 -> `references/traits-and-tags.md`
- 参数化测试设计和组合 -> `references/parameterized-testing.md`
- 默认并行执行、`.serialized`、隔离策略 -> `references/parallelization-and-isolation.md`
- 测试速度、确定性以及不稳定失败预防 -> `references/performance-and-best-practices.md`
- 异步等待和回调桥接 -> `references/async-testing-and-waiting.md`
- XCTest 共存和迁移工作流 -> `references/migration-from-xctest.md`
- 测试导航器/报告工作流和诊断 -> `references/xcode-workflows.md`
- 索引和快速导航 -> `references/_index.md`

## 常见陷阱 -> 下一步最佳操作

- 重复的 `testFooCaseA/testFooCaseB/...` 方法 -> 用一个参数化的 `@Test(arguments:)` 替换。
- 后续断言中隐藏的失败可选先决条件 -> `try #require(...)` 然后对解包值进行断言。
- 共享数据库上的不稳定集成测试 -> 隔离依赖项或内存存储库；仅将 `.serialized` 作为过渡步骤使用。
- 被静默废弃的禁用测试 -> 对于临时已知失败，优先使用 `withKnownIssue` 以保留信号。
- 复杂类型的失败值不明确 -> 使类型符合 `CustomTestStringConvertible` 以进行聚焦的测试诊断。
- 通过名称进行测试计划包含/排除 -> 使用标签和基于标签的过滤器。

## 验证清单

- 确认每个测试具有单一清晰的行为，并在需要时具有表达性的显示名称。
- 确认先决条件使用 `#require`，在失败时应停止测试。
- 确认重复逻辑通过参数化而不是复制。
- 确认测试是并行安全的，或有意使用 `.serialized` 并说明理由。
- 确认异步代码被等待，回调 API 被安全桥接。
- 确认迁移保留不受支持的仅 XCTest 场景在 XCTest 上。

## 参考

- `references/_index.md`
- `references/fundamentals.md`
- `references/expectations.md`
- `references/traits-and-tags.md`
- `references/parameterized-testing.md`
- `references/parallelization-and-isolation.md`
- `references/performance-and-best-practices.md`
- `references/async-testing-and-waiting.md`
- `references/migration-from-xctest.md`
- `references/xcode-workflows.md`
