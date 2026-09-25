# XUnit 最佳实践

你的目标是帮助我使用 XUnit 编写有效的单元测试，涵盖标准测试和数据驱动测试方法。

## 项目设置

- 使用单独的测试项目，命名规范为 `[ProjectName].Tests`
- 引用 Microsoft.NET.Test.Sdk、xunit 和 xunit.runner.visualstudio 包
- 创建与被测试类匹配的测试类（例如，为 `Calculator` 创建 `CalculatorTests`）
- 使用 .NET SDK 测试命令：`dotnet test` 运行测试

## 测试结构

- 无需测试类属性（与 MSTest/NUnit 不同）
- 使用 `[Fact]` 属性的基于事实的测试进行简单测试
- 遵循 Arrange-Act-Assert (AAA) 模式
- 使用 `MethodName_Scenario_ExpectedBehavior` 格式命名测试
- 使用构造函数进行设置，使用 `IDisposable.Dispose()` 进行清理
- 使用 `IClassFixture<T>` 在类中的测试之间共享上下文
- 使用 `ICollectionFixture<T>` 在多个测试类之间共享上下文

## 标准测试

- 保持测试专注于单一行为
- 避免在一个测试方法中测试多个行为
- 使用清晰的断言表达意图
- 仅包含验证测试用例所需的断言
- 使测试独立且幂等（可按任意顺序运行）
- 避免测试之间的相互依赖

## 数据驱动测试

- 使用 `[Theory]` 结合数据源属性
- 使用 `[InlineData]` 用于行内测试数据
- 使用 `[MemberData]` 用于基于方法的测试数据
- 使用 `[ClassData]` 用于基于类的测试数据
- 通过实现 `DataAttribute` 创建自定义数据属性
- 在数据驱动测试中使用有意义的参数名

## 断言

- 使用 `Assert.Equal` 进行值相等性断言
- 使用 `Assert.Same` 进行引用相等性断言
- 使用 `Assert.True`/`Assert.False` 进行布尔条件断言
- 使用 `Assert.Contains`/`Assert.DoesNotContain` 进行集合断言
- 使用 `Assert.Matches`/`Assert.DoesNotMatch` 进行正则表达式模式匹配
- 使用 `Assert.Throws<T>` 或 `await Assert.ThrowsAsync<T>` 测试异常
- 使用流畅断言库进行更易读的断言

## 模拟和隔离

- 考虑在 XUnit 中与 Moq 或 NSubstitute 一起使用
- 模拟依赖项以隔离待测单元
- 使用接口以方便模拟
- 考虑使用 DI 容器进行复杂的测试设置

## 测试组织

- 按功能或组件分组测试
- 使用 `[Trait("Category", "CategoryName")]` 进行分类
- 使用集合固定程序将具有共享依赖项的测试分组
- 考虑使用输出辅助程序（`ITestOutputHelper`）进行测试诊断
- 使用 `Skip = "reason"` 在 fact/theory 属性中条件性跳过测试
