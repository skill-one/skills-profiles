# 配置

## 核心原则

1. **始终使用选项模式** — 不要在服务中直接读取 `IConfiguration`。将配置节绑定到具有验证的强类型类。
2. **启动时验证** — 使用 `ValidateDataAnnotations()` 和 `ValidateOnStart()` 在第一个请求之前捕获配置错误。
3. **密钥永不存入源码** — 开发环境中使用用户密钥，生产环境中使用 Azure Key Vault 或环境变量。切勿将密钥提交到 git。
4. **配置分层** — `appsettings.json` → `appsettings.{环境}.json` → 环境变量 → 用户密钥。后者的配置会覆盖前者。

## 模式

### 选项模式

```csharp
// 带验证属性的选项类
public class DatabaseOptions
{
    public const string SectionName = "Database";

    [Required]
    public required string ConnectionString { get; init; }

    [Range(1, 100)]
    public int MaxRetryCount { get; init; } = 3;

    [Range(1, 60)]
    public int CommandTimeoutSeconds { get; init; } = 30;
}

// 带验证的注册
builder.Services.AddOptions<DatabaseOptions>()
    .BindConfiguration(DatabaseOptions.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart(); // 如果配置无效，启动时失败
```

```json
// appsettings.json
{
  "Database": {
    "ConnectionString": "",
    "MaxRetryCount": 3,
    "CommandTimeoutSeconds": 30
  }
}
```

### 注入选项

```csharp
// IOptions<T> — 单例，启动时读取一次，不可变
public class OrderService(IOptions<DatabaseOptions> options)
{
    private readonly DatabaseOptions _db = options.Value;
}

// IOptionsSnapshot<T> — 作用域，每个请求重新读取（用于可重载配置）
public class OrderService(IOptionsSnapshot<DatabaseOptions> options)
{
    private readonly DatabaseOptions _db = options.Value;
}

// IOptionsMonitor<T> — 单例，主动监视变更
public class BackgroundWorker(IOptionsMonitor<WorkerOptions> options)
{
    public void DoWork()
    {
        var current = options.CurrentValue; // 始终最新
    }
}
```

### 自定义验证（复杂规则）

```csharp
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration("Jwt")
    .Validate(options =>
    {
        if (string.IsNullOrEmpty(options.Key) || options.Key.Length < 32)
            return false;
        if (options.ExpirationMinutes <= 0)
            return false;
        return true;
    }, "JWT 密钥至少 32 个字符且过期时间必须为正数")
    .ValidateOnStart();
```

### Azure Key Vault（生产环境）

```csharp
// Program.cs — 添加 Key Vault 作为配置源
if (builder.Environment.IsProduction())
{
    var keyVaultUri = new Uri(builder.Configuration["KeyVault:Uri"]!);
    builder.Configuration.AddAzureKeyVault(keyVaultUri, new DefaultAzureCredential());
}
```

### 多环境配置

```csharp
// 命名选项 — 每个命名实例不同配置
builder.Services.AddOptions<SmtpOptions>("internal")
    .BindConfiguration("Smtp:Internal");
builder.Services.AddOptions<SmtpOptions>("customer")
    .BindConfiguration("Smtp:Customer");

// 使用
public class EmailService(IOptionsSnapshot<SmtpOptions> options)
{
    public async Task SendInternalEmail(string to, string body)
    {
        var smtp = options.Get("internal");
        // ...
    }
}
```

## 反模式

### 不要直接读取 IConfiguration

```csharp
// BAD — 字符串类型，无验证，难以测试
public class OrderService(IConfiguration config)
{
    public void Process()
    {
        var timeout = int.Parse(config["Database:CommandTimeout"]!);
    }
}

// GOOD — 强类型选项
public class OrderService(IOptions<DatabaseOptions> options)
{
    public void Process()
    {
        var timeout = options.Value.CommandTimeoutSeconds;
    }
}
```

### 不要将密钥存入 appsettings.json

```json
// BAD — 提交到源码控制
{
  "Jwt": { "Key": "super-secret-key" },
  "Database": { "ConnectionString": "Server=prod;Password=secret" }
}

// GOOD — appsettings.json 仅包含默认值/结构
{
  "Jwt": { "Key": "", "Issuer": "myapp", "Audience": "myapp" },
  "Database": { "ConnectionString": "" }
}
// 密钥通过 user-secrets（开发）或 env 变量 / Key Vault（生产）提供
```

### 不要跳过启动验证

```csharp
// BAD — 运行时发现配置错误
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection("Jwt"));

// GOOD — 启动时快速失败
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration("Jwt")
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 将配置绑定到类 | 使用 `BindConfiguration` 的选项模式 |
| 简单、不可变配置 | `IOptions<T>` |
| 每个请求变更的配置 | `IOptionsSnapshot<T>` |
| 监视配置的后台服务 | `IOptionsMonitor<T>` |
| 开发环境密钥 | `dotnet user-secrets` |
| 生产环境密钥 | Azure Key Vault 或环境变量 |
| 验证配置 | `ValidateDataAnnotations()` + `ValidateOnStart()` |
| 同类型多个配置 | 使用 `IOptionsSnapshot<T>.Get(name)` 的命名选项 |
