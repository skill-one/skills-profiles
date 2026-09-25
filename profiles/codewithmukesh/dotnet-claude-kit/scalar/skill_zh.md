# 标量

## 核心原则

1. **标量取代 Swagger UI** — 标量是 .NET 10 推荐的 API 文档 UI。渲染更快，内置暗黑模式，支持数十种语言的代码生成，并完全支持 OpenAPI 3.1。
2. **默认仅开发环境使用** — 将 `MapScalarApiReference()` 包裹在 `IsDevelopment()` 检查中。API 文档会暴露内部结构。如果需要在生产环境中使用，请添加授权。
3. **对敏感 API 禁用代理** — 标量的 "Try It" 功能默认通过 `proxy.scalar.com` 路由。使用 `.WithProxy(null)` 禁用它以保持认证头本地化。
4. **安全方案来自 OpenAPI** — 标量从 OpenAPI 文档中读取安全方案。通过文档转换器配置它们，而不是直接在标量中配置。

## 模式

### 基本设置

```csharp
using Scalar.AspNetCore;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();  // UI 在 /scalar/v1
}

app.Run();
```

### 自定义配置

```csharp
app.MapScalarApiReference(options =>
{
    options
        .WithTitle("结账 API")
        .WithTheme(ScalarTheme.Mars)
        .WithDefaultHttpClient(ScalarTarget.CSharp, ScalarClient.HttpClient)
        .WithPreferredScheme("Bearer")
        .WithProxy(null)  // 禁用外部代理
        .WithSidebar(true);
});
```

### 认证预填（仅开发环境）

预填凭证，以便开发者无需手动粘贴令牌。OpenAPI 文档必须通过文档转换器包含安全方案。

```csharp
if (app.Environment.IsDevelopment())
{
    app.MapScalarApiReference(options =>
    {
        options
            .WithPreferredScheme("Bearer")
            .AddHttpAuthentication("Bearer", auth =>
            {
                auth.Token = "dev-only-test-token";
            });
    });
}
```

其他认证类型：

```csharp
// API 密钥
options.WithApiKeyAuthentication(apiKey =>
{
    apiKey.Token = "dev-api-key";
});

// OAuth2
options.WithOAuth2Authentication(oauth =>
{
    oauth.ClientId = "your-client-id";
    oauth.Scopes = ["openid", "profile"];
});
```

### 可用主题

```csharp
// ScalarTheme 选项：Default, Moon, Purple, BluePlanet, Saturn, Mars, DeepSpace, Kepler, Solarized, Laserwave
options.WithTheme(ScalarTheme.Mars);
```

### 多个 API 文档

```csharp
// 注册多个 OpenAPI 文档
builder.Services.AddOpenApi("v1");
builder.Services.AddOpenApi("v2-beta");

// 标量会自动获取它们
app.MapOpenApi();
app.MapScalarApiReference();
// 可在 /scalar/v1 和 /scalar/v2-beta 访问
```

或显式配置文档：

```csharp
app.MapScalarApiReference(options =>
{
    options
        .AddDocument("v1", "生产 API")
        .AddDocument("v2-beta", "Beta API", isDefault: true);
});
```

### 自定义路由前缀

```csharp
// 默认是 /scalar/{documentName}
app.MapScalarApiReference("/api-docs");
// 现在位于 /api-docs/v1
```

### 生产环境授权

```csharp
// 当合作伙伴需要在生产环境中访问文档时
app.MapOpenApi().RequireAuthorization("ApiDocs");
app.MapScalarApiReference().RequireAuthorization("ApiDocs");
```

### 强制暗黑模式

```csharp
options.ForceDarkMode();
```

### 经典布局（Swagger 风格）

```csharp
options.WithClassicLayout();
```

## 反模式

### 生产环境未授权暴露标量

```csharp
// BAD — 任何人都可以看到你的 API 结构
app.MapOpenApi();
app.MapScalarApiReference();

// GOOD — 仅开发环境
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

// GOOD — 生产环境授权
app.MapOpenApi().RequireAuthorization("ApiDocs");
app.MapScalarApiReference().RequireAuthorization("ApiDocs");
```

### 不要预填真实凭证

```csharp
// BAD — 浏览器中可见真实令牌
options.AddHttpAuthentication("Bearer", auth =>
{
    auth.Token = "eyJhbG...real-production-token";
});

// GOOD — 仅开发环境测试令牌
if (app.Environment.IsDevelopment())
{
    options.AddHttpAuthentication("Bearer", auth =>
    {
        auth.Token = "dev-only-test-token";
    });
}
```

### 不要忘记安全方案转换器

```csharp
// BAD — 因为 OpenAPI 文档没有安全方案，标量中没有认证 UI
builder.Services.AddOpenApi();
app.MapScalarApiReference(options =>
{
    options.WithPreferredScheme("Bearer"); // 无效操作！
});

// GOOD — 首先注册文档转换器
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});
app.MapScalarApiReference(options =>
{
    options.WithPreferredScheme("Bearer");
});
```

### 对敏感 API 不要启用代理

```csharp
// BAD — 认证头通过 proxy.scalar.com 流出
app.MapScalarApiReference();

// GOOD — 对包含敏感数据的 API 禁用代理
app.MapScalarApiReference(options =>
{
    options.WithProxy(null);
});
```

### 新的 .NET 10 项目不要使用 Swagger UI

```csharp
// BAD — Swashbuckle 已从模板中移除，存在维护问题
builder.Services.AddSwaggerGen();
app.UseSwaggerUI();

// GOOD — 内置 OpenAPI + 标量
builder.Services.AddOpenApi();
app.MapOpenApi();
app.MapScalarApiReference();
```

## 决策指南

| 场景 | 建议 |
|------|------|
| API 文档 UI | `MapScalarApiReference()` 与 `MapOpenApi()` |
| 开发环境 | 默认设置，使用 `IsDevelopment()` 防护 |
| 生产 API 文档 | 对两个端点添加 `.RequireAuthorization()` |
| 开发环境认证测试 | `AddHttpAuthentication()` 使用测试令牌 |
| 暗黑主题偏好 | `.ForceDarkMode()` 或 `.WithTheme(ScalarTheme.Moon)` |
| 多个 API 版本 | 多次调用 `AddOpenApi()` — 标量会自动检测 |
| 敏感 API | `.WithProxy(null)` 禁用外部代理 |
| Swagger 风格布局 | `.WithClassicLayout()` |
| 自定义路由 | `app.MapScalarApiReference("/api-docs")` |
