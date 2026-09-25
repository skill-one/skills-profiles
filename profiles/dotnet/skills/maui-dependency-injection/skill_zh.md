# .NET MAUI 中的依赖注入

.NET MAUI 使用与 ASP.NET Core 相同的 `Microsoft.Extensions.DependencyInjection` 容器。所有服务注册都在 `MauiProgram.CreateMauiApp()` 中的 `builder.Services` 上进行。容器在启动时构建一次，之后是不可变的。

## 何时使用

- 在 `MauiProgram.cs` 中注册服务、ViewModel 和页面
- 在 `AddSingleton`、`AddTransient` 和 `AddScoped` 之间进行选择
- 为页面和 ViewModel 配置构造函数注入
- 利用 Shell 导航自动解析 DI 注册的页面
- 使用 `#if` 指令注册平台特定的服务实现
- 为可测试的服务层设计接口

## 何时不使用

- XAML 数据绑定语法或编译绑定 — 使用 **maui-data-binding** 技能
- Shell 路由注册和查询参数 — 使用 **maui-shell-navigation** 技能
- 模拟框架或测试运行器 — 使用标准的 .NET 测试工具（xUnit、NUnit、MSTest）和模拟库（NSubstitute、Moq）

## 输入

- 具有一个 `MauiProgram.cs` 文件的 .NET MAUI 项目
- 知道哪些服务、ViewModel 和页面需要注册
- 目标平台（Android、iOS、Mac Catalyst、Windows）用于条件注册

## 改变答案的规则

| 情况 | 执行此操作 | 原因 |
|---|---|---|
| 注册页面或 ViewModel | 优先使用 `AddTransient` | 每次导航都提供新实例以避免状态过时，且 Singleton 页面在移除后无法重新添加到视觉树中。Singleton 对于确实只需要单例页面的情况（例如，您希望保持热状态的主标签页）是合理的 |
| 注册共享/昂贵的状态 | `AddSingleton` | 全局一个实例（设置、数据库连接、`HttpClient` 处理器） |
| 考虑使用 `AddScoped` | 使用 `AddTransient`（如果打算共享则使用 `AddSingleton`） | MAUI 没有像 ASP.NET Core HTTP 管道的内置请求范围。MAUI 为每个窗口创建一个 `IServiceScope`，因此 Scoped 服务与该窗口的生存期相同 — 从根提供程序解析时，它表现得像 Singleton。两者都不会提供每次导航的新鲜性 |
| 导航到 DI 注册的页面 | 注册页面及其 ViewModel，然后 `Routing.RegisterRoute` | `Shell.Current.GoToAsync` 通过 DI 解析页面并注入其构造函数依赖项 |
| 平台特定实现 | 每个平台使用 `#if` **并覆盖所有平台** | 缺少平台分支会导致服务未注册并在解析时抛出异常 |

**不要** 在未使用 DI 的项目中引入 DI，交换工作正常的服务生命周期，或仅为了对称而添加接口 — 除非用户要求或它修复了真实缺陷。

**狭义回答，但完整。** 当您建议生命周期更改时，请显示注册代码，并给出现实的替代方案而不是单一裁决 — 对于工作单元或 `DbContext` 问题，这意味着 `AddTransient`、显式的 `IServiceScopeFactory.CreateScope()` **和** 工厂模式 (`AddDbContextFactory`)，并说明每种情况适用时机。单行处方通常比简短菜单的权衡更差。

```csharp
// 当您确实需要工作单元语义时使用显式作用域
using var scope = scopeFactory.CreateScope();
var db = scope.ServiceProvider.GetRequiredService<MyDbContext>();
```

## 工作流程

1. 确定所有需要参与依赖注入的服务、ViewModel 和页面。
2. 为每种类型选择正确的生命周期 — `AddSingleton` 用于共享服务，`AddTransient` 用于页面和 ViewModel。
3. 在 `MauiProgram.CreateMauiApp()` 中的 `builder.Services` 上注册所有类型，按类别分组（服务、HTTP、ViewModel、页面）。
4. 在 `AppShell.xaml.cs` 中将页面注册为 Shell 路由，以便 Shell 导航自动解析完整的依赖关系图。
5. 通过构造函数注入将每个页面连接到其 ViewModel，并将 ViewModel 分配为 `BindingContext`。
6. 使用 `#if` 指令添加平台特定注册，确保覆盖所有目标平台或提供回退方案。
7. 通过运行应用程序并确认在运行时没有 `null` 依赖项或缺失注册异常来验证解析是否正常工作。

---

## 生命周期选择

| 生命周期 | 何时使用 | 典型类型 |
|---|---|---|
| `AddSingleton<T>()` | 共享状态、创建成本高、全局配置 | `HttpClient` 工厂、设置服务、数据库连接 |
| `AddTransient<T>()` | 轻量级、无状态或每次使用需要新实例 | 页面、ViewModel、每次调用 API 包装器 |
| `AddScoped<T>()` | 每个窗口生命周期，或手动创建的 `IServiceScope` | 范围工作单元（在 MAUI 中很少见） |

**关键规则：** 默认情况下将页面和 ViewModel 注册为 **Transient**。将共享服务注册为 **Singleton**。

> ⚠️ **除非您手动管理 `IServiceScope`，否则避免使用 `AddScoped`。** MAUI 没有像 ASP.NET Core 的 HTTP 管道的内置请求范围。MAUI 为每个窗口创建一个 `IServiceScope`，因此 Scoped 服务与该窗口的生存期相同；从根提供程序解析时，它表现得像 Singleton。两者都不会提供每次导航的新鲜性。

---

## MauiProgram.cs 中的注册模式

```csharp
public static MauiApp CreateMauiApp()
{
    var builder = MauiApp.CreateBuilder();
    builder.UseMauiApp<App>();

    // 服务 — 共享状态使用 Singleton
    builder.Services.AddSingleton<IDataService, DataService>();
    builder.Services.AddSingleton<ISettingsService, SettingsService>();

    // HTTP — 通过 IHttpClientFactory 使用类型或命名客户端
    // 需要 NuGet: Microsoft.Extensions.Http
    builder.Services.AddHttpClient<IApiClient, ApiClient>();

    // ViewModel — 每次导航使用 Transient 以保持新鲜状态
    builder.Services.AddTransient<MainViewModel>();
    builder.Services.AddTransient<DetailViewModel>();

    // 页面 — Transient 以确保每次构造函数注入都触发
    builder.Services.AddTransient<MainPage>();
    builder.Services.AddTransient<DetailPage>();

    return builder.Build();
}
```

---

## 构造函数注入

通过构造函数参数注入依赖项。当类型从 DI 解析时，容器会自动解析它们。

```csharp
public class MainViewModel
{
    private readonly IDataService _dataService;

    public MainViewModel(IDataService dataService)
    {
        _dataService = dataService;
    }

    public async Task LoadAsync() => Items = await _dataService.GetItemsAsync();
}
```

### ViewModel → 页面连接

注册页面和 ViewModel。将 ViewModel 注入页面并分配为 `BindingContext`：

```csharp
public partial class MainPage : ContentPage
{
    public MainPage(MainViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
```

---

## Shell 导航自动解析

当页面在 DI 中注册**且**作为 Shell 路由注册时，Shell 在导航时自动解析它（及其完整的依赖关系图）：

```csharp
// MauiProgram.cs
builder.Services.AddTransient<DetailPage>();
builder.Services.AddTransient<DetailViewModel>();

// AppShell.xaml.cs
Routing.RegisterRoute(nameof(DetailPage), typeof(DetailPage));

// 导航 — DI 解析 DetailPage + DetailViewModel
await Shell.Current.GoToAsync(nameof(DetailPage));
```

### 将参数传递给 DI 解析的 ViewModel

DI 提供 ViewModel 的*依赖项*；导航参数单独到达。
不要尝试通过构造函数注入它们 — 在 ViewModel 上实现 `IQueryAttributable` 以接收它们：

```csharp
public class DetailViewModel : ObservableObject, IQueryAttributable
{
    readonly IDataService _data;   // ← 由 DI 注入

    public DetailViewModel(IDataService data) => _data = data;

    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        // ← 由导航提供
        if (query.TryGetValue("id", out var id))
            LoadAsync(id.ToString()!);
    }
}

// 带参数导航 — 页面和其 ViewModel 仍然来自 DI
await Shell.Current.GoToAsync($"{nameof(DetailPage)}?id={product.Id}");
```

Shell 将查询属性应用于页面**和**其 `BindingContext`，因此 ViewModel 接收它们而无需页面中的任何连接。

---

## 平台特定注册

使用预处理器指令注册平台实现。始终覆盖所有目标平台或提供 no-op 回退以避免运行时 `null`。

```csharp
#if ANDROID
builder.Services.AddSingleton<INotificationService, AndroidNotificationService>();
#elif IOS || MACCATALYST
builder.Services.AddSingleton<INotificationService, AppleNotificationService>();
#elif WINDOWS
builder.Services.AddSingleton<INotificationService, WindowsNotificationService>();
#else
builder.Services.AddSingleton<INotificationService, NoOpNotificationService>();
#endif
```

---

## 显式解析（最后手段）

优先使用构造函数注入。仅在注入确实不可用时（自定义处理程序、平台回调）使用显式解析：

```csharp
// 从任何具有处理程序的元素
var service = this.Handler.MauiContext.Services.GetService<IDataService>();
```

对于动态解析，注入 `IServiceProvider`：

```csharp
public class NavigationService(IServiceProvider serviceProvider)
{
    public T ResolvePage<T>() where T : Page
        => serviceProvider.GetRequiredService<T>();
}
```

---

## 首先定义接口以提高可测试性

为每个服务定义接口，以便在测试中可以替换实现：

```csharp
public interface IDataService
{
    Task<List<Item>> GetItemsAsync();
}

// 生产注册
builder.Services.AddSingleton<IDataService, DataService>();

// 测试注册 — 无需修改生产代码即可替换
var services = new ServiceCollection();
services.AddSingleton<IDataService, FakeDataService>();
```

---

## 常见陷阱

### 1. Singleton ViewModel 导致数据过时

```csharp
// ❌ ViewModel 在导航之间保持过时状态
builder.Services.AddSingleton<DetailViewModel>();

// ✅ 每次导航都是新实例
builder.Services.AddTransient<DetailViewModel>();
```

### 2. ContentTemplate 页面不是通过 DI 创建的

通过 Shell XAML 声明的页面 `<ShellContent ContentTemplate="{DataTemplate views:DetailPage}">` 是通过 `Activator.CreateInstance` (`ElementTemplate.cs`) 实例化的，**不是**通过服务提供程序。构造函数注入不会在该路径上运行：如果页面的唯一构造函数需要依赖项，您会得到 `MissingMethodException` — 而不是静默的 `null` 依赖项。

通过 `Routing.RegisterRoute` + `GoToAsync` 到达的页面是不同的：它们通过 `ActivatorUtilities.GetServiceOrCreateInstance` (`Routing.cs`)，该函数注入注册的依赖项，即使页面类型本身从未注册，它也会**抛出**如果无法解析所需依赖项。

```csharp
// 注册页面及其依赖项可保持两种路径都正常工作
builder.Services.AddTransient<DetailPage>();
builder.Services.AddTransient<DetailViewModel>();
```

如果您需要为标签/飞出页面使用 DI，请提供一个无参数构造函数来解析它需要的内容，或通过路由导航到它，而不是将其嵌入 `ContentTemplate` 中。

### 3. XAML 资源解析与 DI 时间

`App.xaml` 中的 XAML 资源在 `InitializeComponent()` 期间解析 — 在容器完全可用之前。将依赖服务的操作推迟到 `CreateWindow()`：

```csharp
public partial class App : Application
{
    private readonly IServiceProvider _services;

    public App(IServiceProvider services)
    {
        _services = services;
        InitializeComponent();
    }

    protected override Window CreateWindow(IActivationState? activationState)
    {
        // 安全 — 容器已完全构建
        // 需要: builder.Services.AddTransient<AppShell>() 在 MauiProgram.cs 中
        var appShell = _services.GetRequiredService<AppShell>();
        return new Window(appShell);
    }
}
```

### 4. 服务定位器反模式

```csharp
// ❌ 隐藏依赖项，难以测试
var svc = this.Handler.MauiContext.Services.GetService<IDataService>();

// ✅ 构造函数注入 — 显式且可测试
public class MyViewModel(IDataService dataService) { }
```

### 5. 条件注册中遗漏平台

在 `#if` 块中遗漏平台会导致 `GetService<T>()` 在该平台上运行时返回 `null`。始终包含 `#else` 回退或覆盖所有目标。

### 6. 没有显式作用域的 AddScoped

见上表中的规则：`AddScoped` 给您要么窗口生命周期，要么 Singleton 行为，永远不会提供每次导航的新鲜性。除非您显式创建和管理 `IServiceScope`，否则使用 `AddTransient` 或 `AddSingleton`。

---

## 检查清单

- [ ] 需要注入的每个页面和 ViewModel 都在 `MauiProgram.cs` 中注册
- [ ] 页面和 ViewModel 使用 `AddTransient`；共享服务使用 `AddSingleton`
- [ ] 尽可能使用构造函数注入；仅在最后手段使用服务定位器
- [ ] 为需要测试替换的服务定义接口
- [ ] 平台特定 `#if` 注册覆盖所有目标平台或包含回退
- [ ] 依赖服务的操作推迟到 `CreateWindow()`，而不是在 XAML 解析期间运行
- [ ] 仅在打算使用窗口生命周期时使用 `AddScoped`，或与手动创建的 `IServiceScope` 一起使用

## 参考

- [Dependency injection in .NET MAUI](https://learn.microsoft.com/dotnet/maui/fundamentals/dependency-injection)
- [.NET dependency injection fundamentals](https://learn.microsoft.com/dotnet/core/extensions/dependency-injection)
