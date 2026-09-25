# ASP.NET Minimal API with OpenAPI

你的目标是帮助我创建结构良好、类型正确且具有全面 OpenAPI/Swagger 文档的 ASP.NET Minimal API 端点。

## API 组织

- 使用 `MapGroup()` 扩展来分组相关的端点
- 使用端点过滤器处理横切关注点
- 使用单独的端点类来组织较大的 API
- 对于复杂的 API，考虑使用基于功能的文件夹结构

## 请求和响应类型

- 定义明确的请求和响应 DTO/模型
- 创建具有适当验证属性的清晰模型类
- 使用记录类型来表示不可变请求/响应对象
- 使用与 API 设计标准一致的具有意义的属性名称
- 应用 `[Required]` 和其他验证属性来强制执行约束
- 使用 `ProblemDetailsService` 和 `StatusCodePages` 获取标准错误响应

## 类型处理

- 使用强类型路由参数并显式绑定类型
- 使用 `Results<T1, T2>` 来表示多种响应类型
- 使用 `TypedResults` 而不是 `Results` 来返回强类型响应
- 利用 C# 10+ 功能，如可空注解和仅初始化属性

## OpenAPI 文档

- 使用 .NET 9 中添加的内置 OpenAPI 文档支持
- 定义操作摘要和描述
- 使用 `WithName` 扩展方法添加操作 ID
- 使用 `[Description()]` 为属性和参数添加描述
- 为请求和响应设置适当的内容类型
- 使用文档转换器来添加服务器、标签和安全方案等元素
- 使用模式转换器来对 OpenAPI 模式应用自定义修改
