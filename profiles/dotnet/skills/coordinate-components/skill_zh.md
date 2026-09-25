# 协调组件

## 第 1 步 — 阅读 AGENTS.md

在修改前，先在工作区根目录阅读 `AGENTS.md`，了解项目的规范。

## 第 2 步 — 确定范围

| 需求 | 机制 | 使用时机 |
|------|-----------|-------------|
| 子树（相同渲染模式） | `CascadingValue` 组件 | 布局内的主题、布局配置 |
| 应用范围（所有渲染模式） | 通过 DI 使用 `CascadingValueSource<T>` | 当前用户、功能标志、全局共享的主题 |
| 子电路内的可变共享状态 | 范围服务 + `Action` 事件 | 购物车、通知计数、选定的过滤器 |

对于父级→子级单级：使用 `[Parameter]` / `EventCallback`（参见 `author-component` 技巧）。
对于跨预渲染→交互的状态持久化：参见 `support-prerendering` 技巧。

## 工作流（快速参考）

1. 从第 2 步的表格中选择机制
2. 如果跨越渲染模式边界 → 使用 `CascadingValueSource<T>`（第 4 步）
3. 在 `Program.cs` 中使用 `AddCascadingValue(...)` 和 `isFixed: false` 注册
4. 在子组件中通过 `[CascadingParameter]` 消费
5. 通过 `NotifyChangedAsync(newValue)` 更新 — 永不使用页面刷新
6. 对于子电路内的额外可变状态 → 添加范围服务（第 5 步）
7. 将来自后台线程的任何 `StateHasChanged` 用 `InvokeAsync` 包装
8. 实现 `IDisposable` — 释放计时器、取消令牌、取消订阅事件

## 第 3 步 — 用于子树状态的 CascadingValue

用 `<CascadingValue>` 包裹子树，以便将数据传递给所有后代，而无需通过每个中间组件。

```razor
@* 在布局或父组件中 *@
<CascadingValue Value="theme">
    @Body
</CascadingValue>

@code {
    private ThemeInfo theme = new() { ButtonClass = "btn-primary" };
}
```

在任何后代中消费：

```csharp
[CascadingParameter]
private ThemeInfo? Theme { get; set; }
```

**规则：**
- 通过 **类型** 匹配，而不是名称。要级联同一类型的多个值，请添加 `Name`：
  ```razor
  <CascadingValue Value="primary" Name="PrimaryTheme">...</CascadingValue>
  ```
  ```csharp
  [CascadingParameter(Name = "PrimaryTheme")]
  private ThemeInfo? Primary { get; set; }
  ```
- 当值永不变化时，设置 `IsFixed="true"` — 避免订阅开销。
- **不会跨越渲染模式边界。** 静态 SSR 父组件中的 `<CascadingValue>` 对交互式子组件不可见。参见第 6 步。

## 第 4 步 — 用于应用范围状态的 CascadingValueSource<T>

当值必须对**所有组件（无论渲染模式如何）**可用时，在 DI 中注册 `CascadingValueSource<T>`。

```csharp
// Program.cs
builder.Services.AddCascadingValue(sp =>
{
    var theme = new ThemeInfo { ButtonClass = "btn-primary" };
    return new CascadingValueSource<ThemeInfo>(theme, isFixed: false);
});
```

与第 3 步相同地消费：

```csharp
[CascadingParameter]
private ThemeInfo? Theme { get; set; }
```

**要更新并通知订阅者**，要么修改现有对象，要么替换它：

```razor
@* 修改主题的组件 *@
@inject CascadingValueSource<ThemeInfo> ThemeSource

<button @onclick="ToggleDarkMode">切换主题</button>

@code {
    private bool isDark;

    private async Task ToggleDarkMode()
    {
        isDark = !isDark;
        // 完全替换值：
        var newTheme = new ThemeInfo { ButtonClass = isDark ? "btn-dark" : "btn-primary" };
        await ThemeSource.NotifyChangedAsync(newTheme);
    }
}
```

`NotifyChangedAsync()`（无参数）也适用 — 修改对象然后调用它。`NotifyChangedAsync(newValue)` 一步替换值并通知。

**更新协议：** 每当共享状态发生变化时，修改它的组件必须注入 `CascadingValueSource<T>` 并调用 `NotifyChangedAsync()`。这是唯一能触发所有 `[CascadingParameter]` 订阅器重新渲染的机制。如果没有这个调用，没有订阅者会更新。不要使用 `NavigationManager.Refresh()` 或页面刷新作为替代。

**规则：**
- `isFixed: false` 启用更改通知。`isFixed: true` 更适合真正静态的值（功能标志）。
- **跨越渲染模式边界** — 适用于每页交互性、全局交互性和 WebAssembly。相对于 `<CascadingValue>` 的主要优势。
- 保持级联类型 **粒度化**。每个 `NotifyChangedAsync` 都会重新渲染所有订阅者，无论哪个属性发生变化。不要将所有应用状态放入一个级联类型中。
- 对于 Auto/WebAssembly 应用，在服务器和 `.Client` `Program.cs` 中都注册。类型必须在共享程序集中。

## 第 5 步 — 带有更改事件的范围状态服务

对于多个组件读取和写入的**可变共享状态**（购物车、通知计数、过滤器），使用带有事件的范围服务进行更改通知。

**定义服务：**

```csharp
public class CartState
{
    private readonly List<CartItem> _items = [];

    public IReadOnlyList<CartItem> Items => _items;
    public int Count => _items.Count;

    public event Action? OnChange;

    public void Add(CartItem item)
    {
        _items.Add(item);
        OnChange?.Invoke();
    }

    public void Remove(CartItem item)
    {
        _items.Remove(item);
        OnChange?.Invoke();
    }
}
```

**作为范围注册：**

```csharp
builder.Services.AddScoped<CartState>();
```

**在组件中订阅：**

```razor
@inject CartState Cart
@implements IDisposable

<span class="badge">@Cart.Count</span>

@code {
    protected override void OnInitialized()
    {
        Cart.OnChange += StateHasChanged;
    }

    public void Dispose()
    {
        Cart.OnChange -= StateHasChanged;
    }
}
```

当事件从 Blazor 同步上下文触发时（按钮点击 → `Cart.Add(…)`），简单的 `Action OnChange` 模式即可工作。如果事件从**同步上下文外部**触发（计时器、后台任务、SignalR 中心），请用 `InvokeAsync` 包装：

```csharp
private Action? _handler;

protected override void OnInitialized()
{
    _handler = () => InvokeAsync(StateHasChanged);
    Cart.OnChange += _handler;
}

public void Dispose() => Cart.OnChange -= _handler;
```

将委托存储在字段中，以便可以取消订阅相同的实例。

## 第 6 步 — 渲染模式和状态服务生命周期规则

### 级联值不会跨越渲染模式边界

放置在静态 SSR 布局中的 `<CascadingValue>`（在布局静态渲染时 `MainLayout.razor`）将**不会**到达交互式子组件。交互式组件看到级联参数为 `null`。

**修复：** 使用 DI 中注册的 `CascadingValueSource<T>`（第 4 步）或范围服务（第 5 步）。两者都跨越边界，因为 DI 服务是按电路解析的，而不是从组件树解析的。

### 服务器与 WebAssembly 的服务生命周期

| 生命周期 | 服务器 | WebAssembly |
|----------|--------|-------------|
| **范围** | 每个电路（每个用户连接） | 每个浏览器标签页 |
| **单例** | 所有用户共享 | 每个浏览器标签页（安全） |
| **瞬态** | 每次注入新实例 | 每次注入新实例 |

在服务器上，**永远不要在单例中存储用户特定状态** — 每个用户的电路共享相同的单例。一个用户的购物车会泄露到另一个用户。使用 `AddScoped<T>()`。

在 WebAssembly 上，单例是按标签页的，且安全。但针对**服务器和 WebAssembly（Auto 模式）**设计的代码必须使用范围。

### Auto/WebAssembly 与预渲染

状态服务必须在 `.Client` 项目或共享程序集中定义 — 它们不能引用仅限服务器的类型。在两个 `Program.cs` 文件中注册服务。在预渲染期间创建的状态在切换到交互式运行时时不会保留。使用 `support-prerendering` 技巧的 `[PersistentState]` 模式来跨状态。

## 禁止事项

- **在服务器上不要使用单例来存储每个用户状态** — 所有电路共享它，导致用户间状态泄露。
- **不要将所有应用状态放入一个级联对象** — `NotifyChangedAsync` 在每次更改时都会重新渲染所有订阅者。将关注点分离到不同的类型（`ThemeState`、`CartState`、`UserPreferences`）。
- **不要忘记取消订阅** — 忘记在事件订阅上调用 `Dispose` 会导致内存泄漏，每个电路都会增长。
- **不要在静态布局中期望 `<CascadingValue>` 能到达交互式子组件** — 它不会跨越渲染模式边界。使用 DI 注册的 `CascadingValueSource<T>` 或范围服务。
- **不要使用 `NavigationManager.Refresh(forceReload: true)` 来传播级联值更改** — 这会销毁电路并强制页面刷新。相反，注入 `CascadingValueSource<T>` 并调用 `NotifyChangedAsync(newValue)`，以在不刷新页面的情况下将更新推送到所有 `[CascadingParameter]` 订阅者。
- **不要从非 Blazor 线程调用 `StateHasChanged`** — 用 `InvokeAsync` 包装。框架会抛出 `InvalidOperationException: The current thread is not associated with the Dispatcher`。
