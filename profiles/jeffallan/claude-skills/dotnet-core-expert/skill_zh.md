# .NET Core 专家

## 核心工作流

1. **分析需求** — 确定架构模式、数据模型、API 设计
2. **设计解决方案** — 创建具有适当分离的干净架构层
3. **实现** — 使用现代 C# 功能编写高性能代码；运行 `dotnet build` 验证编译 — 如果构建失败，则审查错误、修复问题并在继续之前重新构建
4. **安全** — 添加身份验证、授权和安全最佳实践
5. **测试** — 使用 xUnit 和集成测试编写全面测试；运行 `dotnet test` 确认所有测试通过 — 如果测试失败，则诊断故障、修复实现并在继续之前重新运行；使用 `curl` 或 REST 客户端验证端点

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| 最小 API | `references/minimal-apis.md` | 创建端点、路由、中间件 |
| 干净架构 | `references/clean-architecture.md` | CQRS、MediatR、层、依赖注入模式 |
| Entity Framework | `references/entity-framework.md` | DbContext、迁移、关系 |
| 身份验证 | `references/authentication.md` | JWT、Identity、授权策略 |
| 云原生 | `references/cloud-native.md` | Docker、健康检查、配置 |

## 约束条件

### 必须
- 使用 .NET 8 和 C# 12 功能
- 启用可空引用类型：在 `.csproj` 中的 `<Nullable>enable</Nullable>`
- 对所有 I/O 操作使用 async/await — 例如，`await dbContext.Users.ToListAsync()`
- 实现适当的依赖注入
- 使用记录类型作为 DTO — 例如，`public record UserDto(int Id, string Name);`
- 遵循干净架构原则
- 使用 `WebApplicationFactory<Program>` 编写集成测试
- 配置 OpenAPI/Swagger 文档

### 禁止
- 使用同步 I/O 操作
- 在 API 响应中直接暴露实体
- 跳过输入验证
- 使用遗留的 .NET Framework 模式
- 在架构层之间混合关注点
- 使用已弃用的 EF Core 模式

## 代码示例

### 最小 API 端点
```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

app.MapGet("/users/{id}", async (int id, ISender sender, CancellationToken ct) =>
{
    var result = await sender.Send(new GetUserQuery(id), ct);
    return result is null ? Results.NotFound() : Results.Ok(result);
})
.WithName("GetUser")
.Produces<UserDto>()
.ProducesProblem(404);

app.Run();
```

### MediatR 查询处理器
```csharp
// Application/Users/GetUserQuery.cs
public record GetUserQuery(int Id) : IRequest<UserDto?>;

public sealed class GetUserQueryHandler : IRequestHandler<GetUserQuery, UserDto?>
{
    private readonly AppDbContext _db;

    public GetUserQueryHandler(AppDbContext db) => _db = db;

    public async Task<UserDto?> Handle(GetUserQuery request, CancellationToken ct) =>
        await _db.Users
            .AsNoTracking()
            .Where(u => u.Id == request.Id)
            .Select(u => new UserDto(u.Id, u.Name))
            .FirstOrDefaultAsync(ct);
}
```

### 使用异步查询的 EF Core DbContext
```csharp
// Infrastructure/AppDbContext.cs
public sealed class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}

// 在服务中使用
public async Task<IReadOnlyList<UserDto>> GetAllAsync(CancellationToken ct) =>
    await _db.Users
        .AsNoTracking()
        .Select(u => new UserDto(u.Id, u.Name))
        .ToListAsync(ct);
```

### 使用记录类型的 DTO
```csharp
public record UserDto(int Id, string Name);
public record CreateUserRequest(string Name, string Email);
```

## 输出模板

在实现 .NET 功能时，提供：
1. 项目结构（解决方案/项目文件）
2. 领域模型和 DTO
3. API 端点或服务实现
4. 数据库上下文和迁移（如果适用）
5. 架构决策的简要说明

[文档](https://jeffallan.github.io/claude-skills/skills/backend/dotnet-core-expert/)
