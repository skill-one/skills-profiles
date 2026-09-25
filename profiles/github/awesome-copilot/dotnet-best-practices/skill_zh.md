# .NET/C# 最佳实践

您的任务是确保 ${selection} 中的 .NET/C# 代码符合此解决方案/项目的特定最佳实践。这包括：

## 文档与结构

- 为所有公共类、接口、方法和属性创建全面的 XML 文档注释
- 在 XML 注释中包含参数描述和返回值描述
- 遵循已建立的命名空间结构：{Core|Console|App|Service}.{功能}

## 设计模式与架构

- 使用主要构造函数语法进行依赖注入（例如，`public class MyClass(IDependency dependency)`）
- 使用泛型基类实现命令处理器模式（例如，`CommandHandler<TOptions>`）
- 使用接口隔离并遵循清晰的命名约定（接口前缀为 'I'）
- 遵循工厂模式进行复杂对象创建。

## 依赖注入与服务

- 使用构造函数依赖注入，并通过 ArgumentNullException 进行空值检查
- 使用适当的生命周期注册服务（单例、作用域、瞬态）
- 使用 Microsoft.Extensions.DependencyInjection 模式
- 为可测试性实现服务接口

## 资源管理与本地化

- 使用 ResourceManager 进行本地化消息和错误字符串
- 分离 LogMessages 和 ErrorMessages 资源文件
- 通过 `_resourceManager.GetString("MessageKey")` 访问资源

## 异步/等待模式

- 对所有 I/O 操作和长时间运行的任务使用 async/await
- 从异步方法返回 Task 或 Task<T>
- 在适当的地方使用 ConfigureAwait(false)
- 正确处理异步异常

## 测试标准

- 使用 MSTest 框架和 FluentAssertions 进行断言
- 遵循 AAA 模式（安排、执行、断言）
- 使用 Moq 进行依赖模拟
- 测试成功和失败场景
- 包括空参数验证测试

## 配置与设置

- 使用带数据注解的强类型配置类
- 实现验证属性（Required、NotEmptyOrWhitespace）
- 使用 IConfiguration 绑定进行设置
- 支持appsettings.json配置文件

## 语义内核与 AI 集成

- 使用 Microsoft.SemanticKernel 进行 AI 操作
- 实现适当的内核配置和服务注册
- 处理 AI 模型设置（ChatCompletion、Embedding 等）
- 使用结构化输出模式以获得可靠的 AI 响应

## 错误处理与日志记录

- 使用 Microsoft.Extensions.Logging 进行结构化日志记录
- 包含作用域日志记录和有意义的上下文
- 抛出具有描述性消息的特定异常
- 使用 try-catch 块处理预期失败场景

## 性能与安全

- 在适用情况下使用 C# 12+ 功能和 .NET 8 优化
- 实现适当的输入验证和清理
- 使用参数化查询进行数据库操作
- 遵循 AI/ML 操作的安全编码实践

## 代码质量

- 确保 SOLID 原则的合规性
- 通过基类和工具避免代码重复
- 使用反映领域概念的具有意义的名称
- 保持方法专注和连贯
- 实现适当的资源清理模式
