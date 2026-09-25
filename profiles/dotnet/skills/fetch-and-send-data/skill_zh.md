# 获取和发送数据

## 第 1 步 — 读取 AGENTS.md

检查 **交互模式** 和 **范围**：

| 模式 | 数据访问 |
|------|-------------|
| 无（静态 SSR） | 服务器端：注入服务/`DbContext`。使用 `[StreamRendering]` 加载 UX。 |
| 服务器 | 服务器端：注入服务/`DbContext`。使用 `??=` + `[PersistentState]` 保护预渲染。 |
| WebAssembly | 浏览器端：仅使用 `HttpClient`。无法直接访问服务器。 |
| 自动 | 服务器和浏览器端。始终通过 API 进行访问。 |

## 第 2 步 — 注册 HttpClient

仅在从服务器调用外部 API 或 WebAssembly/Auto 模式时需要。服务器组件访问自己的数据库应直接注入 `DbContext` 或服务。

```csharp
// 命名客户端 — 需要 Microsoft.Extensions.Http NuGet
builder.Services.AddHttpClient("CatalogAPI", client =>
{
    client.BaseAddress = new Uri("https://api.example.com/");
});

// 类型化客户端
builder.Services.AddHttpClient<CatalogClient>(client =>
    client.BaseAddress = new Uri("https://api.example.com/"));
```

对于 WebAssembly/Auto 模式且需要预渲染的情况，在服务器和 `.Client` `Program.cs` 中注册。

## 第 3 步 — 获取数据

### 简单加载

```razor
@page "/products"
@inject CatalogClient Catalog

@if (products is null)
{
    <p>加载中…</p>
}
else
{
    @foreach (var p in products)
    {
        <p>@p.Name — @p.Price.ToString("C")</p>
    }
}

@code {
    private Product[]? products;

    protected override async Task OnInitializedAsync()
    {
        products = await Catalog.GetProductsAsync();
    }
}
```

最简单的情况下无需错误处理 — 在父级/布局级别将组件使用包裹在 `<ErrorBoundary>` 中以捕获未处理的异常。

### 静态 SSR — StreamRendering

如果没有 `[StreamRendering]`，用户在 `OnInitializedAsync` 完成前什么也看不到：

```razor
@attribute [StreamRendering]
```

仅影响静态 SSR。对交互式组件无效。

### 预渲染保护

预渲染会两次调用 `OnInitializedAsync`。跳过重复调用：

```csharp
[PersistentState] private Product[]? products;

protected override async Task OnInitializedAsync()
{
    products ??= await Catalog.GetProductsAsync();
}
```

有关详细信息，请参阅 `support-prerendering` 技能。

## 第 4 步 — 处理错误

使用 `<ErrorBoundary>` 作为默认错误策略。它提供跨所有组件的一致错误体验，无需每个组件的捕获逻辑。在布局或父级级别包裹组件使用：

```razor
<ErrorBoundary>
    <ChildContent>
        <ProductList />
    </ChildContent>
    <ErrorContent>
        <div class="alert alert-danger">出错了。请刷新。</div>
    </ErrorContent>
</ErrorBoundary>
```

非取消异常（`HttpRequestException` 等）会自动传播到 `ErrorBoundary` — 组件中无需捕获块。

### 取消是特殊的

`ComponentBase` 默默地吞下**所有** `OperationCanceledException` — 无论是自发起的（释放、参数更改）还是外部的（`HttpClient` 超时）。`ErrorBoundary` 从不看到它们。这意味着：

- 自定义取消 → 默默忽略。正确行为，无需操作。
- 外部取消（超时）→ 也被默默吞下。组件会卡在加载状态。通常可以接受 — 超时很少发生。

### 何时添加组件级错误处理

仅在组件需要 `ErrorBoundary` 无法提供的功能时添加捕获块 — 通常是**重试**或**特定超时消息**。即使如此，也只需捕获所需内容：

```csharp
// 仅捕获外部取消（超时）— 其他异常会传递到 ErrorBoundary
catch (OperationCanceledException ex) when (!cancellationToken.IsCancellationRequested)
{
    Logger.LogWarning(ex, "请求超时，分类 {CategoryId}", CategoryId);
    error = "请求超时。请重试。";
}
```

如果组件还需要使用重试按钮而不是让 `ErrorBoundary` 接管来处理一般错误：

```csharp
catch (OperationCanceledException ex) when (!cancellationToken.IsCancellationRequested)
{
    Logger.LogWarning(ex, "请求超时，分类 {CategoryId}", CategoryId);
    error = "请求超时。请重试。";
}
catch (Exception ex)
{
    Logger.LogError(ex, "加载分类 {CategoryId} 的产品失败", CategoryId);
    error = "无法加载产品。请重试。";
}
```

### 规则

- **永远不要显示 `exception.Message`** — 它可能包含 PII、连接字符串或内部细节。使用硬编码的用户友好消息。
- **始终通过 `ILogger` 记录** — 真实的异常会传递到日志管道。
- **服务必须接受 `CancellationToken`** — 将它传递给每个异步调用，以便在组件取消时停止工作。

## 第 5 步 — 参数驱动重新加载

当数据依赖于会变化的路由或查询参数（例如，在 `/products/1` 和 `/products/2` 之间导航）时，使用 `OnParametersSetAsync` 并带有一个保护措施，以跳过不会影响数据的重新加载。

### 模式：取消并重新加载，覆盖陈旧数据

```razor
@page "/products/{CategoryId:int}"
@implements IAsyncDisposable
@inject ProductService ProductService
@inject ILogger<Products> Logger

@if (error is not null)
{
    <div class="alert alert-danger">
        <p>@error</p>
        <button @onclick="LoadAsync">重试</button>
    </div>
}
else if (products is null)
{
    <p>加载中…</p>
}
else
{
    @if (isLoading)
    {
        <p><em>正在刷新…</em></p>
    }
    @foreach (var p in products)
    {
        <p>@p.Name — @p.Price.ToString("C")</p>
    }
}

@code {
    [Parameter] public int CategoryId { get; set; }
    [SupplyParameterFromQuery] public string? ViewMode { get; set; } // 仅 UI

    private CancellationTokenSource? cts;
    private int? loadedCategoryId;
    private List<Product>? products;
    private bool isLoading;
    private string? error;

    protected override async Task OnParametersSetAsync()
    {
        if (CategoryId == loadedCategoryId)
        {
            return; // 仅 ViewMode 变化 — 无需重新加载
        }

        loadedCategoryId = CategoryId;
        await LoadAsync();
    }

    private async Task LoadAsync()
    {
        if (cts is not null)
        {
            await cts.CancelAsync();
            cts.Dispose();
        }

        cts = new CancellationTokenSource();
        var cancellationToken = cts.Token; // 在 await 前本地捕获

        error = null;
        isLoading = true;

        try
        {
            var result = await ProductService.GetByCategoryAsync(CategoryId, cancellationToken);
            products = result;
        }
        catch (OperationCanceledException ex) when (!cancellationToken.IsCancellationRequested)
        {
            Logger.LogWarning(ex, "加载分类 {CategoryId} 超时", CategoryId);
            error = "请求超时。请重试。";
        }
        finally
        {
            isLoading = false;
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (cts is not null)
        {
            await cts.CancelAsync();
            cts.Dispose();
        }
    }
}
```

关键细节：
- **使用跟踪值进行保护**：`loadedCategoryId` 在仅 UI 参数变化时跳过重新加载。
- **在 await 前本地捕获令牌** — CTS 字段可能被并发参数更改替换。
- **后续加载时不要将 `products` 设为 null** — 使用 `isLoading` 覆盖层保持现有数据可见。
- **`IAsyncDisposable`** 在用户导航时取消挂起的任务。

## 第 6 步 — 发送数据

```csharp
var response = await http.PostAsJsonAsync("products", newProduct);
response.EnsureSuccessStatusCode();

var response = await http.PutAsJsonAsync($"products/{id}", updated);
response.EnsureSuccessStatusCode();

var response = await http.DeleteAsync($"products/{id}");
response.EnsureSuccessStatusCode();
```

保存时禁用提交按钮以防止重复请求。显示保存指示器。

## 第 7 步 — 自动或带预渲染的 WebAssembly 的服务抽象

当组件在服务器和浏览器中运行（自动模式，或带预渲染的 WebAssembly）时，将数据访问抽象在抽象基类后面：

```csharp
public abstract class ProductServiceBase
{
    public abstract Task<Product[]> GetAllAsync(CancellationToken ct = default);
}

// 服务器 — 直接访问数据库
public class ServerProductService(AppDbContext db) : ProductServiceBase
{
    public override async Task<Product[]> GetAllAsync(CancellationToken ct = default) =>
        await db.Products.ToArrayAsync(ct);
}

// 客户端 — 调用 API
public class ClientProductService(HttpClient http) : ProductServiceBase
{
    public override async Task<Product[]> GetAllAsync(CancellationToken ct = default) =>
        await http.GetFromJsonAsync<Product[]>("api/products", ct) ?? [];
}
```

在每个项目的 `Program.cs` 中注册适当的实现。组件注入抽象基类。

## 禁止事项

- **不要在构造函数中调用 API** — 使用 `OnInitializedAsync`。
- **除非数据依赖于变化的参数，否则不要使用 `OnParametersSetAsync`**。初始加载使用 `OnInitializedAsync`。
- **不要在 WebAssembly/Auto 组件中注入 `DbContext`** — 浏览器中没有数据库。
- **不要通过 `HttpClient` 调用自己的服务器** — 直接注入服务。
- **不要向用户显示 `exception.Message`** — PII 风险。记录它，显示通用消息。
- **不要捕获自发起的 `OperationCanceledException`** — `ComponentBase` 会处理它。
