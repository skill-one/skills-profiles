# 生成可测试包装器

为不可测试的静态依赖生成包装接口、默认实现和 DI 服务注册代码。对于已有 .NET 内置抽象（如 `TimeProvider`、`IHttpClientFactory`）的静态，引导采用内置抽象。对于没有内置替代方案的静态，生成自定义最小包装器。

## 使用场景

- 运行 `detect-static-dependencies` 并识别要包装的静态后
- 当用户通过替换静态为注入抽象来使类可测试时
- 当采用 `TimeProvider` (.NET 8+) 或 `System.IO.Abstractions` 时
- 当创建 `Environment.*`、`Console.*` 或 `Process.*` 的自定义包装器时
- 当已发布的静态 API 需要环境接口（因为签名不能更改）时

## 不适用场景

- 用户想先查找静态（使用 `detect-static-dependencies`）
- 用户想批量替换调用点（使用 `migrate-static-to-wrapper`）
- 静态已经被接口封装

如果目标已消费注入接口或内置抽象，则停止：
不要添加第二个包装器、项目、注册或围绕该接口的测试。

> 缺少 DI 包本身并不强制要求环境接口。对于可实例化类，优先使用构造函数注入并显式组合或显示请求的注册。当 API 是静态且其签名必须保持静态，或用户明确禁止调用者构建/DI 变化时，使用步骤 5。

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 静态类别 | 是 | 哪个类别：`time`、`filesystem`、`environment`、`network`、`console`、`process` |
| 目标框架 | 是 | `.csproj` 中的 `TargetFramework`（影响哪些内置抽象存在） |
| 组合 | 否 | 现有的 DI 框架、显式/手动构建或不可变静态 API |
| 命名空间 | 否 | 生成的包装器代码的目标命名空间 |

## 工作流程

### 步骤 1：确定抽象策略

根据类别和目标框架：

| 类别 | .NET 8+ | .NET 6-7 | .NET Framework |
|------|--------|--------|---------------|
| 时间 | `TimeProvider`（内置） | `TimeProvider` 通过 `Microsoft.Bcl.TimeProvider` NuGet | 自定义 `ISystemClock` |
| 文件系统 | `System.IO.Abstractions`（NuGet） | 相同 | 相同 |
| HTTP | `IHttpClientFactory`（内置） | 相同 | 相同 |
| 环境 | 自定义 `IEnvironmentProvider` | 相同 | 相同 |
| 控制台 | 自定义 `IConsole` | 相同 | 相同 |
| 进程 | 自定义 `IProcessRunner` | 相同 | 相同 |

该表格选择 *哪个抽象*。它如何到达测试代码是另一个维度：

- 可实例化类：构造函数注入，即使当前调用者手动组合对象；
- 现有容器：按照其约定添加可编译的注册；
- 公共静态 API/签名不能更改：步骤 5 的环境接口。

检查主机构建器、`IServiceCollection`、现有注册和构建点。不要因为项目当前没有容器就推断“必须保持静态”。

### 步骤 2：生成内置抽象采用（时间、HTTP）

#### TimeProvider (.NET 8+)

不需要包装代码。完成四个部分：生产注册、构造函数注入、`FakeTimeProvider` 测试和测试包。

1. 在 DI 中注册：
```csharp
builder.Services.AddSingleton(TimeProvider.System);
```

2. 注入到类中：
```csharp
public class OrderProcessor(TimeProvider timeProvider)
{
    public bool IsExpired(Order order)
        => timeProvider.GetUtcNow() > order.ExpiresAt;
}
```

3. 使用 `FakeTimeProvider` 进行测试：
```csharp
// 需要 Microsoft.Extensions.TimeProvider.Testing NuGet
var fakeTime = new FakeTimeProvider(new DateTimeOffset(2026, 1, 15, 0, 0, 0, TimeSpan.Zero));
var processor = new OrderProcessor(fakeTime);
fakeTime.Advance(TimeSpan.FromDays(1));
Assert.True(processor.IsExpired(order));
```

断言必须在固定或推进假时间后证明时间依赖结果。仅仅构建 `FakeTimeProvider` 不是测试。当项目没有容器但目标是可实例化类时，仍然注入 `TimeProvider` 并显示显式生产构建的 `TimeProvider.System`；不要用自定义静态时钟替换它。

在调用采用完成之前，验证存储库包含或答案提供所有必需工件：测试包引用、生产组合/注册、每个受影响的构造函数调用和一个可运行的假时间测试。省略其中一个集成点的代码片段是指导，不是完成的采用。

#### TimeProvider (.NET 8 之前)

引导：安装 `Microsoft.Bcl.TimeProvider` NuGet。与上述 API 相同。

#### IHttpClientFactory

不需要包装代码。通过 `builder.Services.AddHttpClient<MyService>()` 注册类型化的客户端，并将 `HttpClient` 直接注入到类构造函数中。通过将调用者的令牌传递给 HTTP 操作来保留取消操作。

对于测试，提供一个完整的假 `HttpMessageHandler`，其 `SendAsync` 返回确定的 `HttpResponseMessage`，使用该处理程序构建 `HttpClient`，并在不访问网络的情况下执行类型化客户端。当任务要求实现时编译和运行聚焦测试；不要在概念性处理程序方法处停止。

当生产使用类型化客户端注册时，测试相同的注册管道：在 `ServiceCollection` 中配置其主处理程序，解析类型化客户端，并调用它。手动构建 `HttpClient` 的测试证明类，但不是任务请求采用的 DI 注册。

### 步骤 3：生成自定义包装器（环境、控制台、进程）

对于没有内置抽象的类别，遵循此模板：

#### 接口——定义最小表面

仅包含在代码库中实际检测到的方法。不要为每个可能成员生成包装器——仅包装实际使用的方法。

优先选择无状态的操作形接口。例如，如果调用者只需要启动进程、等待并返回其退出代码，则暴露一个 `Run` 操作，而不是一个有状态包装器，该包装器会泄漏 `Process` 生命周期。

```csharp
namespace <Namespace>;

/// <summary>
/// 对 <static class> 的可测试性抽象。 
/// </summary>
public interface I<WrapperName>
{
    // 每个检测到的静态调用一个方法
    <return type> <MethodName>(<parameters>);
}
```

#### 默认实现——委托给真实静态

```csharp
namespace <Namespace>;

/// <summary>
/// 默认实现委托给 <static class>。
/// </summary>
public sealed class <WrapperName> : I<WrapperName>
{
    public <return type> <MethodName>(<parameters>)
        => <StaticClass>.<Method>(<arguments>);
}
```

#### DI 注册

```csharp
// 在 Program.cs 或 Startup.cs 中：
builder.Services.AddSingleton<I<WrapperName>, <WrapperName>>();
```

将注册视为交付成果，而不是摘要中的句子。如果存在现有注册表面，将其添加到存储库中。否则显示确切的编译就绪语句，并标识调用者应放置的位置。无状态委托包装器是单例；如果必须保留状态，解释为什么需要更短的生存期。

### 步骤 4：生成文件系统包装器采用

优先选择已建立的 `System.IO.Abstractions` NuGet 包而不是自定义包装器：

1. 安装包：
```
dotnet add package System.IO.Abstractions
```

2. 在 DI 中注册：
```csharp
builder.Services.AddSingleton<IFileSystem, FileSystem>();
```

3. 将 `IFileSystem` 注入到类中：
```csharp
public class ConfigLoader(IFileSystem fileSystem)
{
    public string LoadConfig(string path)
        => fileSystem.File.ReadAllText(path);
}
```

4. 使用 `MockFileSystem` 进行测试：
```
dotnet add <TestProject> package System.IO.Abstractions.TestingHelpers
```
```csharp
var mockFs = new MockFileSystem(new Dictionary<string, MockFileData>
{
    { "/config.json", new MockFileData("{\"key\": \"value\"}") }
});
var loader = new ConfigLoader(mockFs);
Assert.Equal("{\"key\": \"value\"}", loader.LoadConfig("/config.json"));
```

包优先采用是排他的：添加两个包引用，在生产中使用 `IFileSystem`，注册或显式组合 `FileSystem`，并在执行消费者之前初始化 `MockFileSystem`。不要生成第二个自定义文件系统接口，也不要展示未初始化的假接口，其测试可以在不证明请求的读写行为的情况下通过。

### 步骤 5：生成签名保留的环境上下文

当 API 必须保持静态或其发布的签名不能接受依赖时，使用此模式：

```csharp
public static class Clock
{
    private static readonly AsyncLocal<Func<DateTime>?> s_override = new();
    public static DateTime UtcNow
        => s_override.Value?.Invoke() ?? TimeProvider.System.GetUtcNow().UtcDateTime;

    internal static IDisposable Override(DateTime fixedUtcTime)
    {
        if (fixedUtcTime.Kind != DateTimeKind.Utc)
            throw new ArgumentException("The override must be UTC.", nameof(fixedUtcTime));

        var previous = s_override.Value;
        s_override.Value = () => fixedUtcTime;
        return new Scope(previous);
    }
    private sealed class Scope : IDisposable
    {
        private readonly Func<DateTime>? _previous;
        private bool _disposed;

        public Scope(Func<DateTime>? previous)
        {
            _previous = previous;
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            s_override.Value = _previous;
            _disposed = true;
        }
    }
}
```

关键权衡：`AsyncLocal<T>` 确保并行测试不会相互干扰；生产成本是每个调用一个空值检查；`static readonly` 字段本质上免费。

此模式必须保留三个属性，因为每个属性都破坏了真实的迁移：

- **范围化覆盖并使其可逆。** 返回一个 `IDisposable`，它恢复以前的值，因此测试不会将固定时间泄漏到下一个测试中。裸 setter，或在每个调用点手动 `try`/`finally`，将此负担放在每个测试作者身上。
- **使用 `AsyncLocal<T>`，永远不要 `[ThreadStatic]`。** `[ThreadStatic]` 不会跨 `await` 流动，因此覆盖在测试中途无声消失。
- **保留你要替换的成员的语义。** 用本地时间源替换 `DateTime.UtcNow` 会改变每个现有调用者和存储值依赖的 `DateTimeKind` — 将 `UtcNow` 与 `GetUtcNow()`，`Now` 与 `GetLocalNow()` 配对。
- **证明测试程序集可以到达覆盖。** 内部覆盖除非生产项目为该测试程序集添加了确切的 `InternalsVisibleTo`，否则无法从单独的测试程序集访问。否则使用已公开的接口，仅当授权公共 API 变化时。永远不要展示测试调用不可访问的成员。

相同的形状适用于非时间静态：将 `TimeProvider.System.GetUtcNow()` 替换为真实静态调用，并保留覆盖槽、可作用域的 `IDisposable` 和原始语义。

### 步骤 6：放置生成的文件

按照项目的现有约定生成文件：
- 如果有 `Abstractions/` 或 `Interfaces/` 文件夹，将接口放在那里
- 如果有 `Infrastructure/` 或 `Services/` 文件夹，将实现放在那里
- 否则，在使用静态的代码旁边创建文件

始终生成：
1. 接口文件（或内置抽象的采用说明）
2. 默认实现文件
3. 可编译的 DI 注册，应用于现有注册表面或显示在确切的组合点
4. 一个确定性替换示例或聚焦测试，它在不使用环境资源的情况下执行消费者

在环境接口路径上完全跳过注册：没有容器可以注册到，而且无论如何提供容器都是导致用户请求接口的失败模式。

在报告完成之前，验证交付的输出包含所有请求的项目。特别是，不要在未添加或显示注册代码时总结“单例注册”，也不要在没有证明消费者如何接收假的情况下声称可测试。

对于控制台包装器，使用一个假来执行消费者，该假既捕获提示又提供返回输入；仅构建或横幅运行不能证明提示流程。

## 验证

- [ ] 生成的接口仅包装实际检测到的静态（不是推测性的）
- [ ] 默认实现委托给真实静态，行为无变化
- [ ] DI 注册使用 `AddSingleton` 为无状态包装器，`AddTransient` 为有状态包装器
- [ ] 推荐使用 NuGet 包，因为已建立库存在（System.IO.Abstractions 等）
- [ ] 对于 .NET 8+，推荐 `TimeProvider` 而不是自定义 `ISystemClock`
- [ ] TimeProvider 采用包括注入、生产组合、`FakeTimeProvider`、其测试包和对时间依赖结果的断言
- [ ] HTTP 采用包括完整的假处理程序测试并保留取消操作
- [ ] 在注入路径上，注册或显式组合是编译就绪的，假演示了消费者而无需真实环境依赖
- [ ] 环境上下文模式包括 `AsyncLocal<T>`、一个作用域的 `IDisposable`，它恢复以前的值，以及权衡说明
- [ ] 在环境接口路径上，不提出 `IServiceCollection` 注册，单独的测试程序集可以到达覆盖，且替换成员的返回类型和语义（`UtcNow` vs `Now`，及其 `DateTimeKind`）被保留

## 常见陷阱

| 陷阱 | 解决方案 |
|------|------|
| 将“无 DI 包”视为“必须是环境” | 注入到可实例化类并显式组合；为静态/签名保留 API 保留步骤 5 |
| 包装静态类的所有成员 | 仅包装代码库中实际调用的方法 |
| .NET 8+ 上的自定义时间包装器 | 使用内置 `TimeProvider` 而不是 |
| 自定义文件系统包装器 | 优先选择 `System.IO.Abstractions` NuGet — 经验证、完整 |
| 当单例足够时注册作用域 | 无状态包装器应为 `AddSingleton` |
| 忘记测试辅助包 | `Microsoft.Extensions.TimeProvider.Testing` 用于时间，`System.IO.Abstractions.TestingHelpers` 用于文件系统 |
| 没有 `AsyncLocal` 的环境上下文 | 非异步 `[ThreadStatic]` 在 `async`/`await` 中会破坏 — 始终使用 `AsyncLocal<T>` |
| 向外部测试展示内部环境覆盖 | 添加确切的友元程序集或使用授权的公共接口；编译测试程序集 |
