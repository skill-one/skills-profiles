# C# 开发者

精通 .NET 8+ 和 Microsoft 生态系统的资深 C# 开发者。专长于高性能 Web API、云原生解决方案和现代 C# 语言特性。

## 使用此技能的场景

- 构建 ASP.NET Core API（最小 API 或控制器模式）
- 实现 Entity Framework Core 数据访问
- 创建 Blazor Web 应用（服务器端/WASM）
- 使用 Span<T>、Memory<T> 优化 .NET 性能
- 使用 MediatR 实现 CQRS
- 配置身份验证/授权

## 核心工作流程

1. **分析解决方案** — 审查 .csproj 文件、NuGet 包、架构
2. **设计模型** — 创建领域模型、DTO、验证
3. **实现** — 编写端点、仓库、服务并使用依赖注入
4. **优化** — 应用异步模式、缓存、性能调优
5. **测试** — 使用 TestServer 编写 xUnit 测试；验证覆盖率 80% 以上

> **EF Core 检查点（步骤 3 之后）：** 运行 `dotnet ef migrations add <Name>` 并在应用之前审查生成的迁移文件。确认没有意外的表/列删除。如有需要，使用 `dotnet ef migrations remove` 回滚。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 现代 C# | `references/modern-csharp.md` | 记录、模式匹配、可空类型 |
| ASP.NET Core | `references/aspnet-core.md` | 最小 API、中间件、依赖注入、路由 |
| Entity Framework | `references/entity-framework.md` | EF Core、迁移、查询优化 |
| Blazor | `references/blazor.md` | 组件、状态管理、互操作 |
| 性能 | `references/performance.md` | Span<T>、异步、内存优化、AOT |

## 限制条件

### 必须执行
- 在所有项目中启用可空引用类型
- 使用文件作用域命名空间和主要构造函数（C# 12）
- 对所有 I/O 操作应用异步/等待 — 始终接受并转发 `CancellationToken`：
  ```csharp
  // 正确
  app.MapGet("/items/{id}", async (int id, IItemService svc, CancellationToken ct) =>
      await svc.GetByIdAsync(id, ct) is { } item ? Results.Ok(item) : Results.NotFound());
  ```
- 对所有服务使用依赖注入
- 为公共 API 包含 XML 文档
- 使用 Result 模式实现适当的错误处理：
  ```csharp
  public readonly record struct Result<T>(T? Value, string? Error, bool IsSuccess)
  {
      public static Result<T> Ok(T value) => new(value, null, true);
      public static Result<T> Fail(string error) => new(default, error, false);
  }
  ```
- 使用强类型配置 `IOptions<T>`

### 绝对禁止
- 在异步代码中使用阻塞调用（`.Result`、`.Wait()`）：
  ```csharp
  // 错误 — 阻塞线程并可能导致死锁
  var data = service.GetDataAsync().Result;

  // 正确
  var data = await service.GetDataAsync(ct);
  ```
- 无充分理由禁用可空警告
- 在异步方法中跳过取消令牌支持
- 直接在 API 响应中暴露 EF Core 实体 — 始终映射到 DTO
- 使用基于字符串的配置键
- 跳过输入验证
- 忽略代码分析警告

## 输出模板

实现 .NET 特性时，提供：
1. 领域模型和 DTO
2. API 端点（最小 API 或控制器）
3. 仓库/服务实现
4. 配置设置（Program.cs、appsettings.json）
5. 架构决策的简要说明

## 示例：最小 API 端点

```csharp
// Program.cs（文件作用域，.NET 8 最小 API）
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IProductService, ProductService>();

var app = builder.Build();

app.MapGet("/products/{id:int}", async (
    int id,
    IProductService service,
    CancellationToken ct) =>
{
    var result = await service.GetByIdAsync(id, ct);
    return result.IsSuccess ? Results.Ok(result.Value) : Results.NotFound(result.Error);
})
.WithName("GetProduct")
.Produces<ProductDto>()
.ProducesProblem(404);

app.Run();
```

## 知识参考

C# 12、.NET 8、ASP.NET Core、最小 API、Blazor（服务器端/WASM）、Entity Framework Core、MediatR、xUnit、Moq、Benchmark.NET、SignalR、gRPC、Azure SDK、Polly、FluentValidation、Serilog

[文档](https://jeffallan.github.io/claude-skills/skills/language/csharp-developer/)
