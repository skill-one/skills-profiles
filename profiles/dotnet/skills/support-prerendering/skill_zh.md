# 支持预渲染

## 预渲染的工作原理

预渲染默认适用于所有交互式渲染模式。服务器将组件渲染为静态 HTML 并立即发送到浏览器。然后交互式运行时（服务器/WebAssembly）加载并重新渲染具有完全交互性的组件。

这意味着：
- `OnInitializedAsync` 运行 **两次** — 一次在预渲染（静态）期间，一次在交互式运行时附加时。
- `OnAfterRenderAsync` 在预渲染期间 **不** 被调用 — 仅在交互式渲染后调用。
- 内部页面之间的交互式导航（交互式路由）**跳过预渲染** — 预渲染仅在完整页面加载时发生。

## 第一步 — 阅读项目的 AGENTS.md

检查项目的 `AGENTS.md` 文件以获取 **交互模式** 和 **交互范围**：

| 模式 | 是否应用预渲染 |
|------|----------------------|
| 无（静态 SSR） | 否 — 没有交互式传递 |
| 服务器 | 是 |
| WebAssembly | 是 |
| 自动 | 是 |

如果模式为 `None`，则此功能不适用。

## 在预渲染 → 交互式之间持久化状态

最常见的预渲染问题：在预渲染期间在 `OnInitializedAsync` 中加载的数据在交互式运行时附加时被丢弃并重新获取。这会导致闪烁和重复的 API/DB 调用。

### 推荐使用 `[PersistentState]` 属性

将属性标注为在预渲染期间自动序列化并在交互式激活时恢复：

```razor
@page "/forecasts"
@rendermode InteractiveServer

<h1>天气</h1>

@if (Forecasts is null)
{
    <p>加载中...</p>
}
else
{
    @foreach (var f in Forecasts)
    {
        <p>@f.Date: @f.TemperatureC°C</p>
    }
}

@code {
    [PersistentState]
    public WeatherForecast[]? Forecasts { get; set; }

    protected override async Task OnInitializedAsync()
    {
        Forecasts ??= await ForecastService.GetForecastsAsync();
    }
}
```

`??=` 模式至关重要 — 它表示“仅在属性未从预渲染状态恢复时才获取。”

### 相同组件的多个实例

当相同的组件类型出现多次时，使用 `@key` 来区分状态：

```razor
@foreach (var item in items)
{
    <ItemCard @key="item.Id" />
}
```

### 高级：`PersistentComponentState` 服务

对于复杂场景（动态键、自定义序列化），使用命令式 API：

```csharp
@inject PersistentComponentState ApplicationState

@code {
    private List<Order>? orders;

    protected override async Task OnInitializedAsync()
    {
        ApplicationState.RegisterOnPersisting(PersistOrders);

        if (!ApplicationState.TryTakeFromJson<List<Order>>("orders", out var restored))
        {
            orders = await OrderService.GetOrdersAsync();
        }
        else
        {
            orders = restored;
        }
    }

    private Task PersistOrders()
    {
        ApplicationState.PersistAsJson("orders", orders);
        return Task.CompletedTask;
    }
}
```

## 禁用预渲染

当组件依赖于浏览器 API 或预渲染+交互式双重渲染导致无法通过 `[PersistentState]` 解决的问题时，禁用预渲染。

### 在组件定义上

```razor
@rendermode @(new InteractiveServerRenderMode(prerender: false))
```

根据需要将 `InteractiveServerRenderMode` 替换为 `InteractiveWebAssemblyRenderMode` 或 `InteractiveAutoRenderMode`。

### 在组件实例上

```razor
<MyChart @rendermode="new InteractiveServerRenderMode(prerender: false)" />
```

### 在整个应用上

在 `App.razor` 中：

```razor
<HeadOutlet @rendermode="new InteractiveServerRenderMode(prerender: false)" />
<Routes @rendermode="new InteractiveServerRenderMode(prerender: false)" />
```

注意：父级的预渲染设置会覆盖子级。如果 `<Routes>` 禁用预渲染，则单个页面无法重新启用它。

## 从交互式路由中排除页面

在全局交互式应用中，某些页面可能需要 `HttpContext`（cookies、请求标头、响应状态码）。这些页面必须通过静态 SSR 渲染，而不是在交互式运行时内部渲染。

使用 `[ExcludeFromInteractiveRouting]`：

```razor
@page "/privacy"
@attribute [ExcludeFromInteractiveRouting]

<h1>隐私政策</h1>
```

这会强制在导航到此页面时进行 **完整页面重新加载**，退出交互式路由。页面以静态 SSR 渲染，具有完整的 `HttpContext` 访问权限。

在 `App.razor` 中，条件性地应用渲染模式：

```razor
<!DOCTYPE html>
<html>
<head>
    <HeadOutlet @rendermode="RenderModeForPage" />
</head>
<body>
    <Routes @rendermode="RenderModeForPage" />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>

@code {
    [CascadingParameter]
    public HttpContext HttpContext { get; set; } = default!;

    private IComponentRenderMode? RenderModeForPage =>
        HttpContext.AcceptsInteractiveRouting() ? InteractiveServer : null;
}
```

将 `InteractiveServer` 替换为应用的配置渲染模式。

## 在运行时检测预渲染与交互式

使用 `RendererInfo` 来保护仅在交互式运行时运行的代码：

```csharp
protected override async Task OnInitializedAsync()
{
    if (RendererInfo.IsInteractive)
    {
        // 仅在交互式渲染期间运行，不在预渲染期间运行
        await StartSignalRConnection();
    }
}
```

`RendererInfo` 属性：
- `IsInteractive` — 预渲染期间为 `false`，交互式运行时附加后为 `true`
- `Name` — 预渲染期间为 `"Static"`，交互式时为 `"Server"` 或 `"WebAssembly"`

## 客户端服务在预渲染期间失败

`.Client` 项目中的组件在服务器上预渲染。仅在客户端 `Program.cs` 中注册的服务（例如 `IWebAssemblyHostEnvironment`）在预渲染期间不可用。

通过以下方式之一修复：
1. **在服务器上注册匹配的服务** — 两个 `Program.cs` 文件都提供该服务
2. **使服务可选** — 使用构造函数注入并带有可空的默认值：`public MyComponent(IMyService? svc = null)`
3. **创建服务抽象** — 接口在 `.Client` 中，实现分别在两个项目中
4. **禁用该组件的预渲染**

## 禁止事项

- 不要在 `OnInitializedAsync` 中调用 JS 互操作 — 预渲染期间 JS 不可用。使用 `OnAfterRenderAsync(firstRender)`。
- 不要假设 `OnInitializedAsync` 运行一次 — 在预渲染时会运行两次。始终使用 `[PersistentState]` 或 `??=` 保护。
- 不要在交互式组件中使用 `HttpContext` — 它仅在静态预渲染期间可用，在交互式生命周期期间不可用。对于需要它的页面，使用 `[ExcludeFromInteractiveRouting]`。
- 不要首先禁用预渲染 — 这会损害感知加载时间和 SEO。使用 `[PersistentState]` 保留状态。
