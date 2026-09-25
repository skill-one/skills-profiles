# 代码测试扩展

此技能可访问代码测试流程中使用的语言特定指导文件。调用此技能以获取文件路径，然后读取您目标语言的相应文件。

## 可用扩展文件

| 文件 | 语言 | 内容 |
|------|----------|----------|
| [extensions/dotnet.md](extensions/dotnet.md) | .NET (C#/F#/VB) | 构建命令、测试命令、项目引用验证、常见CS错误代码、MSTest模板 |
| [extensions/python.md](extensions/python.md) | Python | 框架自适应测试命令（pytest、自定义运行器）、项目布局检测、模拟指南、常见错误 |
| [extensions/typescript.md](extensions/typescript.md) | TypeScript/JavaScript | 构建测试命令（Jest/Vitest/Mocha）、框架检测、模拟、TS特定注意事项 |
| [extensions/powershell.md](extensions/powershell.md) | PowerShell | 测试命令（Pester v5）、模块导入模式、发现/运行陷阱、模拟、常见错误 |
| [extensions/cpp.md](extensions/cpp.md) | C++ | 使用友元声明的测试内部 |
| [extensions/go.md](extensions/go.md) | Go | `go test`命令、表格驱动测试、集成测试与单元测试布局、通过接口进行模拟、常见错误 |
| [extensions/java.md](extensions/java.md) | Java | Maven/Gradle命令、JUnit 4/5和TestNG检测、Mockito、Spring Boot切片、常见错误 |
| [extensions/rust.md](extensions/rust.md) | Rust | `cargo test`命令、单元测试与集成测试与文档测试、特性、异步测试框架、常见错误 |
| [extensions/ruby.md](extensions/ruby.md) | Ruby | RSpec和Minitest命令、Bundler使用、Rails特定内容、模拟模式、常见错误 |
| [extensions/swift.md](extensions/swift.md) | Swift | SPM和Xcode测试命令、XCTest与Swift Testing、`@testable import`、异步/抛出测试、常见错误 |
| [extensions/kotlin.md](extensions/kotlin.md) | Kotlin | Gradle命令、JUnit/Kotest检测、MockK、协程测试、KMP和Android特定内容、常见错误 |
| [extensions/dotnet-examples.md](extensions/dotnet-examples.md) | .NET (C#/F#/VB) | 具体流程示例：样本研究输出、计划、生成的测试、修复循环、最终报告 |
| [extensions/python-examples.md](extensions/python-examples.md) | Python | 具体流程示例（pytest）：研究、计划、生成的测试文件、修复循环、最终报告 |
| [extensions/typescript-examples.md](extensions/typescript-examples.md) | TypeScript/JavaScript | 具体流程示例（Vitest，适用于Jest）：研究、计划、生成的测试文件、修复循环、最终报告 |
| [extensions/go-examples.md](extensions/go-examples.md) | Go | 具体流程示例（标准`testing`）：研究、计划、表格驱动测试文件、修复循环、最终报告 |
| [extensions/java-examples.md](extensions/java-examples.md) | Java | 具体流程示例（JUnit 5 + Mockito on Maven）：研究、计划、生成的测试文件、修复循环、最终报告 |

## 使用方法

在编写测试代码之前，请读取目标语言的相应扩展文件。当目标语言存在`<语言>-examples.md`文件时，请与基础扩展文件一起阅读，以查看具体端到端流程演示（研究输出、计划、生成的测试、修复循环、最终报告）。
