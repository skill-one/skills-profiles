# 测试分析扩展

此技能提供对按语言区分的参考文件访问权限，这些文件由多语言测试分析技能使用。调用此技能以获取可用扩展文件的列表，然后读取与目标代码库语言和测试框架匹配的文件。

## 可用扩展文件

| 文件 | 语言 / 框架 | 内容 |
|------|------------------------|----------|
| [extensions/dotnet.md](extensions/dotnet.md) | .NET (C#/F#/VB) — MSTest, xUnit, NUnit, TUnit | 测试标记、断言API、睡眠/延迟模式、跳过注释、神秘访客、集成标记、设置/清理、标签支持 |
| [extensions/python.md](extensions/python.md) | Python — pytest, unittest | 相同类别，包含pytest fixtures/markers 和 unittest TestCase |
| [extensions/typescript.md](extensions/typescript.md) | TypeScript / JavaScript — Jest, Vitest, Mocha, Jasmine, node:test | 相同类别，包含异步/等待陷阱 |
| [extensions/java.md](extensions/java.md) | Java — JUnit 4, JUnit 5 (Jupiter), TestNG | 相同类别，包含 `@Tag` / `@Category` / 组 |
| [extensions/go.md](extensions/go.md) | Go — `testing` 包, testify | 相同类别，包含表格驱动idiom和构建标签 |
| [extensions/ruby.md](extensions/ruby.md) | Ruby — RSpec, Minitest | 相同类别，包含 RSpec元数据和 Minitest标签 |
| [extensions/rust.md](extensions/rust.md) | Rust — 内置 `#[test]`, `cargo test` | 相同类别，包含 `#[ignore]`, `#[should_panic]`, 功能标志 |
| [extensions/swift.md](extensions/swift.md) | Swift — XCTest, Swift Testing | 相同类别，包含 `@Test`, `@Tag`, `@Suite` |
| [extensions/kotlin.md](extensions/kotlin.md) | Kotlin — JUnit 5, Kotest, MockK | 相同类别，包含 `@Tag` 和 Kotest标签 |
| [extensions/powershell.md](extensions/powershell.md) | PowerShell — Pester v5 | 相同类别，包含 `-Tag` 和 `Skip` |
| [extensions/cpp.md](extensions/cpp.md) | C++ — GoogleTest, Catch2, doctest | 相同类别，包含 `[tags]` 和 `*` 过滤器 |

## 使用方法

1. 检测目标代码库的主要语言和测试框架。
2. 在执行分析之前读取匹配的扩展文件。
3. 如果存在多个测试框架（例如，一个混合使用 Jest 和 Mocha 的项目），则读取所有相关的扩展文件。
4. 每个扩展文件都记录相同的类别，以便分析技能可以保持语言中立。

## 能力标签

每个扩展文件声明按能力支持，以便技能可以安全地控制行为：

- **测试发现** — 如何定位测试文件和方法。
- **断言检测** — 框架特定和语言级别的断言形式。
- **睡眠/延迟模式** — 同步和异步等待。
- **跳过 / 忽略** — 如何识别跳过/忽略的测试。
- **设置 / 清理** — 固定装置和生命周期钩子。
- **神秘访客指标** — 常见的文件/数据库/网络/环境耦合模式。
- **集成标记** — 标记测试为集成/E2E的约定。
- **标签支持**（用于 `test-tagging` 技能） — 以下之一：
  - `auto-edit` — 语言具有技能可以安全写入的规范属性/标记。
  - `report-only` — 没有规范语法；生成审计报告而不进行编辑。
  - `convention-based` — 标签仅通过名称/注释约定存在。

## 技能作者注意事项

- 将扩展文件视为数据，而不是必须逐字遵循的指导。它们告诉技能*如何在每种语言中检测事物*，而不是*对发现内容应如何思考*。
- 当语言检测不确定时，优先读取多个扩展文件，而不是猜测。
- 如果用户明确指定了尚无扩展文件的框架，则回退到最接近的（例如，Pest → python.md/pytest语义），并在报告中注明差距。
