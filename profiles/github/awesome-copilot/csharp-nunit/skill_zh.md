# NUnit 最佳实践

你的目标是帮助我使用 NUnit 编写有效的单元测试，涵盖标准测试和数据驱动测试方法。

## 项目设置

- 使用单独的测试项目，命名规范为 `[ProjectName].Tests`
- 引用 Microsoft.NET.Test.Sdk、NUnit 和 NUnit3TestAdapter 包
- 创建与被测试类匹配的测试类（例如，为 `Calculator` 创建 `CalculatorTests`）
- 使用 .NET SDK 测试命令：`dotnet test` 运行测试

## 测试结构

- 将 `[TestFixture]` 属性应用于测试类
- 使用 `[Test]` 属性为测试方法
- 遵循 Arrange-Act-Assert (AAA) 模式
- 使用 `MethodName_Scenario_ExpectedBehavior` 模式命名测试
- 使用 `[SetUp]` 和 `[TearDown]` 进行每个测试的设置和清理
- 使用 `[OneTimeSetUp]` 和 `[OneTimeTearDown]` 进行类的设置和清理
- 使用 `[SetUpFixture]` 进行程序集级别的设置和清理

## 标准测试

- 保持测试专注于单一行为
- 避免在一个测试方法中测试多个行为
- 使用清晰的断言表达意图
- 仅包含验证测试用例所需的断言
- 使测试独立且幂等（可按任意顺序运行）
- 避免测试之间的相互依赖

## 数据驱动测试

- 使用 `[TestCase]` 进行内联测试数据
- 使用 `[TestCaseSource]` 进行程序生成测试数据
- 使用 `[Values]` 进行简单参数组合
- 使用 `[ValueSource]` 进行属性或方法数据源
- 使用 `[Random]` 进行随机数值测试值
- 使用 `[Range]` 进行序列数值测试值
- 使用 `[Combinatorial]` 或 `[Pairwise]` 组合多个参数

## 断言

- 使用 `Assert.That` 与约束模型（首选 NUnit 风格）
- 使用 `Is.EqualTo`、`Is.SameAs`、`Contains.Item` 等约束
- 使用 `Assert.AreEqual` 进行简单值等式（经典风格）
- 使用 `CollectionAssert` 进行集合比较
- 使用 `StringAssert` 进行字符串特定断言
- 使用 `Assert.Throws<T>` 或 `Assert.ThrowsAsync<T>` 测试异常
- 在断言中使用描述性消息，以便在失败时清晰明了

## 模拟和隔离

- 考虑在 NUnit 中使用 Moq 或 NSubstitute
- 模拟依赖项以隔离待测单元
- 使用接口以方便模拟
- 考虑使用 DI 容器进行复杂的测试设置

## 测试组织

- 按功能或组件分组测试
- 使用 `[Category("CategoryName")]` 使用分类
- 使用 `[Order]` 在必要时控制测试执行顺序
- 使用 `[Author("DeveloperName")]` 指示所有权
- 使用 `[Description]` 提供附加测试信息
- 考虑使用 `[Explicit]` 对于不应自动运行的测试
- 使用 `[Ignore("Reason")]` 暂时跳过测试
