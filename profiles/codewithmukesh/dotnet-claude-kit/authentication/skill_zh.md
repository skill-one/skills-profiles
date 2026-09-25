# 身份验证与授权

## 核心原则

1. **使用 ASP.NET Identity 进行用户管理** — 不要自行构建用户存储。Identity 处理密码哈希、锁定、双因素认证、电子邮件确认，并且自 .NET 10 起，还支持内置密钥/WebAuthn 的无密码登录。
2. **API 使用 JWT，Web 应用使用 Cookie** — API 使用 Bearer 令牌认证；Blazor/MVC 应用使用 Cookie 认证。
3. **基于策略的授权优于角色** — 策略是可测试的、可组合的，并且比 `[Authorize(Roles = "Admin")]` 更具表现力。
4. **切勿在代码中存储密钥** — 开发环境中使用用户密钥，生产环境中使用 Azure Key Vault / 环境变量。

## 模式

### JWT Bearer 认证

```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!)),
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();
```

### 令牌生成

使用 `Microsoft.IdentityModel.JsonWebTokens` 中的 `JsonWebTokenHandler` — 这是 ASP.NET Core 自身用于验证的维护型、基于 span 的处理器。`JwtSecurityTokenHandler` (System.IdentityModel.Tokens.Jwt) 是遗留堆栈。

```csharp
public sealed class TokenService(IConfiguration config, TimeProvider clock)
{
    private static readonly JsonWebTokenHandler TokenHandler = new();

    public string GenerateToken(User user, IEnumerable<string> roles)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(config["Jwt:Key"]!));
        var now = clock.GetUtcNow();

        var descriptor = new SecurityTokenDescriptor
        {
            Issuer = config["Jwt:Issuer"],
            Audience = config["Jwt:Audience"],
            IssuedAt = now.UtcDateTime,
            Expires = now.AddHours(1).UtcDateTime,
            Claims = new Dictionary<string, object>
            {
                [JwtRegisteredClaimNames.Sub] = user.Id,
                [JwtRegisteredClaimNames.Email] = user.Email!,
                [JwtRegisteredClaimNames.Name] = user.UserName!,
                ["roles"] = roles.ToArray()
            },
            SigningCredentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256)
        };

        return TokenHandler.CreateToken(descriptor);
    }
}
```

### 基于策略的授权

```csharp
// 定义策略
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("CanManageOrders", policy => policy
        .RequireAuthenticatedUser()
        .RequireClaim("permission", "orders:write"))
    .AddPolicy("MinimumAge", policy => policy
        .AddRequirements(new MinimumAgeRequirement(18)));

// 自定义要求 + 处理器
public class MinimumAgeRequirement(int minimumAge) : IAuthorizationRequirement
{
    public int MinimumAge => minimumAge;
}

public class MinimumAgeHandler(TimeProvider clock) : AuthorizationHandler<MinimumAgeRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        MinimumAgeRequirement requirement)
    {
        var dateOfBirthClaim = context.User.FindFirst("date_of_birth");
        if (dateOfBirthClaim is not null &&
            DateOnly.TryParse(dateOfBirthClaim.Value, out var dob) &&
            dob.AddYears(requirement.MinimumAge) <= DateOnly.FromDateTime(clock.GetUtcNow().DateTime))
        {
            context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}
```

### 保护端点

```csharp
// 保护整个组
app.MapGroup("/api/admin")
    .WithTags("Admin")
    .RequireAuthorization("AdminOnly")
    .MapAdminEndpoints();

// 保护单个端点
group.MapPost("/", CreateOrder)
    .RequireAuthorization("CanManageOrders");

// 对受保护的组允许匿名访问
group.MapGet("/public-info", GetPublicInfo)
    .AllowAnonymous();
```

### OpenID Connect (外部身份提供者)

```csharp
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
})
.AddCookie()
.AddOpenIdConnect(options =>
{
    options.Authority = builder.Configuration["Oidc:Authority"];
    options.ClientId = builder.Configuration["Oidc:ClientId"];
    options.ClientSecret = builder.Configuration["Oidc:ClientSecret"];
    options.ResponseType = "code";
    options.SaveTokens = true;
    options.Scope.Add("openid");
    options.Scope.Add("profile");
    options.Scope.Add("email");
});
```

### 访问当前用户

```csharp
// 在最小 API 处理器中 — 注入 ClaimsPrincipal 或 HttpContext
group.MapGet("/me", (ClaimsPrincipal user) =>
{
    var userId = user.FindFirstValue(ClaimTypes.NameIdentifier);
    var email = user.FindFirstValue(ClaimTypes.Email);
    return TypedResults.Ok(new { userId, email });
}).RequireAuthorization();
```

## 反模式

### 不要到处使用角色字符串

```csharp
// BAD — 魔术字符串，难以重构，不可测试
[Authorize(Roles = "Admin,SuperAdmin,Manager")]
public class AdminController { }

// GOOD — 基于策略
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminAccess", p => p.RequireRole("Admin", "SuperAdmin", "Manager"));

group.MapGet("/", Handler).RequireAuthorization("AdminAccess");
```

### 不要在 appsettings.json 中存储密钥

```json
// BAD — 提交到源代码控制
{
  "Jwt": {
    "Key": "super-secret-key-12345"
  }
}
```

```bash
# GOOD — 开发中使用用户密钥
dotnet user-secrets set "Jwt:Key" "super-secret-key-12345"
```

### 不要跳过令牌验证

```csharp
// BAD — 禁用验证
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer = false,      // 不要
    ValidateAudience = false,    // 不要
    ValidateLifetime = false,    // 绝对不要
};

// GOOD — 验证所有内容（有关完整设置，请参阅 JWT Bearer 认证模式）
```

## 决策指南

| 场景 | 建议 |
|------|------|
| REST API | JWT Bearer 认证 |
| Blazor Server / MVC | Cookie 认证 |
| 外部身份提供者 | OpenID Connect |
| 用户注册 / 登录 | ASP.NET Identity |
| 无密码登录 | ASP.NET Identity 密钥（WebAuthn，自 .NET 10 内置） |
| 权限检查 | 基于策略的授权 |
| 多租户 API | 基于声明的租户声明 |
| API 间通信 | 客户端凭证（OAuth 2.0） |
| 简单 API 密钥 | 自定义 `AuthenticationHandler<T>` |
