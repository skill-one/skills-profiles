# Blazor 中的 JS 互操作

## 1. 并置 JS 模块

始终使用并置的 `.razor.js` 文件，并包含 `export` — 永远不要使用全局 `window.*` 函数或 `<script>` 标签。

```javascript
// ChartPanel.razor.js — 放置在 ChartPanel.razor 旁边
export function initialize(canvas, dotNetRef) { /* ... */ }
export function updateData(points) { /* ... */ }
export function dispose() { /* ... */ }
```

导入路径：同一项目 = `"./Components/ChartPanel.razor.js"`，RCL = `"./_content/{AssemblyName}/..."`。

## 2. 生命周期时机

**所有 JS 互操作都必须在 `OnAfterRenderAsync` 或事件处理程序中发生** — 永远不要在 `OnInitialized`、`OnParametersSet` 或构造函数中。在服务器预渲染期间不可用 JS。

使用带类型的互操作包装器（见第 4 节）— 永远不要用原始字符串字面量调用 `InvokeAsync`/`InvokeVoidAsync`：

```csharp
private ChartInterop? _chart;

protected override async Task OnAfterRenderAsync(bool firstRender)
{
    if (firstRender)
    {
        _chart = new ChartInterop(JS);
        await _chart.InitializeAsync(_canvasRef);
    }
}
```

**参数变化**：在 `OnParametersSet` 中设置一个标志，在 `OnAfterRenderAsync` 中应用：

```csharp
private bool _dataChanged;

protected override void OnParametersSet() => _dataChanged = true;

protected override async Task OnAfterRenderAsync(bool firstRender)
{
    if (firstRender) { /* 初始化 */ }
    else if (_dataChanged && _chart is not null)
    {
        _dataChanged = false;
        await _chart.UpdateDataAsync(DataPoints);
    }
}
```

## 3. 批量相关操作

每次 JS 互操作调用都会跨越 .NET 到 JS 的边界（在 Blazor Server 中，还会跨越 SignalR 电路）。批量操作适用于**两个方向** — .NET→JS 和 JS→.NET。

### .NET → JS：合并连续调用

如果 C# 端连续进行两个或多个 JS 调用，将它们合并为一个 JS 函数：

```csharp
// ❌ 两次往返 — 主题和区域设置总是同时应用
await _module.InvokeVoidAsync("applyTheme", theme);
await _module.InvokeVoidAsync("applyLocale", locale);

// ❌ 一个调用的结果输入到另一个 — 两者都可以保持在 JS
var token = await _module.InvokeAsync<string>("createAccessToken");
await _module.InvokeVoidAsync("storeToken", token);
```

```javascript
// ✅ 一次调用应用全部 — 无数据依赖，无两次往返的必要
export function applyPreferences(theme, locale) {
    document.documentElement.dataset.theme = theme;
    document.documentElement.lang = locale;
}

// ✅ 链保持在 JS — 令牌永远不需要跨越边界
export function createAndStoreToken() {
    const token = crypto.randomUUID();
    sessionStorage.setItem('access-token', token);
    return token;
}
```

### JS → .NET：批量回调

当 JS 需要将多个数据块发送回 .NET 时，将它们发送在一个 `invokeMethodAsync` 调用中，而不是进行单独的回调：

```javascript
// ❌ 从 JS 发起两次 .NET 往返
await dotNetRef.invokeMethodAsync(ON_VOLUME_CHANGED, volume);
await dotNetRef.invokeMethodAsync(ON_PLAYBACK_CHANGED, isPlaying);

// ✅ 一个回调包含所有数据
await dotNetRef.invokeMethodAsync(ON_PLAYER_STATE_CHANGED, { volume, isPlaying });
```

**规则**：如果从任一侧始终发生两个互操作调用，将它们合并为一个函数。

## 4. 带类型的互操作包装器

将一个功能的互操作封装在一个普通类中，该类拥有模块生命周期：

```csharp
public sealed class ChartInterop : IAsyncDisposable
{
    internal const string ModulePath = "./Components/ChartPanel.razor.js";
    internal const string InitMethod = "initialize";
    internal const string UpdateMethod = "updateData";
    internal const string DisposeMethod = "dispose";

    private readonly IJSRuntime _js;
    private IJSObjectReference? _module;

    public ChartInterop(IJSRuntime js) => _js = js;

    private async ValueTask<IJSObjectReference> GetModuleAsync()
        => _module ??= await _js.InvokeAsync<IJSObjectReference>("import", ModulePath);

    public async ValueTask InitializeAsync(ElementReference canvas)
    {
        var module = await GetModuleAsync();
        await module.InvokeVoidAsync(InitMethod, canvas);
    }

    public async ValueTask UpdateDataAsync(IReadOnlyList<DataPoint> points)
    {
        var module = await GetModuleAsync();
        await module.InvokeVoidAsync(UpdateMethod, points);
    }

    public async ValueTask DisposeAsync()
    {
        try
        {
            if (_module is not null)
            {
                await _module.InvokeVoidAsync(DisposeMethod);
                await _module.DisposeAsync();
            }
        }
        catch (JSDisconnectedException) { }
    }
}
```

组件使用包装器，无需魔法字符串：

```razor
@inject IJSRuntime JS
@implements IAsyncDisposable

<canvas @ref="_canvasRef" width="600" height="400"></canvas>

@code {
    private ElementReference _canvasRef;
    private ChartInterop? _chart;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            _chart = new ChartInterop(JS);
            await _chart.InitializeAsync(_canvasRef);
        }
    }

    async ValueTask IAsyncDisposable.DisposeAsync()
    {
        if (_chart is not null)
            await _chart.DisposeAsync();
    }
}
```

优先使用具体类而不是接口+实现来作为互操作包装器。对于单元测试，直接替换 `IJSRuntime`（它已经是接口）。

## 5. DotNetObjectReference 用于 JS→.NET 回调

```csharp
_dotNetRef = DotNetObjectReference.Create(this);
await _module.InvokeVoidAsync("initialize", _dotNetRef);
```

在 JS 端，将 `dotNetRef` 封装在一个类中。使用 `async`/`await` 与 `try/catch`（而不是 `.catch()）` 来防止电路丢失。在顶部定义 .NET 方法名称常量：

```javascript
const ON_CLIPBOARD_CHANGED = 'OnClipboardChanged';

class ClipboardMonitor {
    #dotNetRef;
    #abortController;

    constructor(dotNetRef) {
        this.#dotNetRef = dotNetRef;
        this.#abortController = new AbortController();
    }

    start() {
        document.addEventListener('copy', async () => {
            try {
                const text = await navigator.clipboard.readText();
                await this.#dotNetRef.invokeMethodAsync(ON_CLIPBOARD_CHANGED, text);
            } catch { /* 电路断开或剪贴板拒绝 */ }
        }, { signal: this.#abortController.signal });
    }

    dispose() {
        this.#abortController.abort();
    }
}

let monitor;
export function initialize(dotNetRef) {
    monitor = new ClipboardMonitor(dotNetRef);
    monitor.start();
}

export function dispose() {
    monitor?.dispose();
}
```

规则：
- `[JSInvokable]` 方法**必须为 `public`** — 私有/内部在运行时静默失败
- 在 `[JSInvokable]` 回调中将 `StateHasChanged` 封装在 `InvokeAsync` 内：
  ```csharp
  [JSInvokable]
  public async Task OnClipboardChanged(string text)
  {
      await InvokeAsync(() => { _lastClipboard = text; StateHasChanged(); });
  }
  ```
- 在 JS 中始终 `try/catch` 围绕 `invokeMethodAsync` — 电路丢失会抛出异常
- 在 JS 中使用 `const` 定义 .NET 方法名称字符串 — 防止因拼写错误而静默失败的 bug
- 在 `DisposeAsync` 中释放 `DotNetObjectReference`

## 6. 释放和服务器安全

始终实现 `IAsyncDisposable`。首先调用 JS 清理，然后释放引用。捕获 `JSDisconnectedException` 以处理 Blazor Server 电路丢失：

```csharp
public async ValueTask DisposeAsync()
{
    try
    {
        if (_module is not null)
        {
            await _module.InvokeVoidAsync("dispose");
            await _module.DisposeAsync();
        }
    }
    catch (JSDisconnectedException) { }

    _dotNetRef?.Dispose();
}
```

永远不要使用同步 `IDisposable` 进行 JS 互操作清理 — `InvokeVoidAsync` 返回 `ValueTask` 必须被 `await`。

## 7. ElementReference

通过 `@ref` 传递 DOM 元素，而不是字符串 ID：

```razor
<canvas @ref="_canvasRef" width="600" height="400"></canvas>
```

```csharp
await _chart.InitializeAsync(_canvasRef);
```

## 检查清单

- [ ] JS 在并置的 `.razor.js` 中，包含 `export` — 没有 `window.*` 全局变量
- [ ] 所有互操作在 `OnAfterRenderAsync` 或事件处理程序中 — 永远不在预渲染期间
- [ ] `IAsyncDisposable` 捕获 `JSDisconnectedException`
- [ ] `DotNetObjectReference` 在 `DisposeAsync` 中释放；JS 端在 `invokeMethodAsync` 周围使用 `try/catch`
- [ ] `[JSInvokable]` 方法是 `public`，并使用 `await InvokeAsync(StateHasChanged)`
- [ ] 使用 `InvokeVoidAsync` 当不需要返回值时
- [ ] 使用 `ElementReference` 而不是字符串 ID
- [ ] 相关操作批量合并为单个互操作调用（.NET→JS 和 JS→.NET）

## 常见错误检查清单

| 错误 | 修复 |
|------|------|
| 使用 JS 实现可用 CSS 实现的功能 | 使用 CSS 自定义属性、`data-` 属性、伪类 |
| 许多细粒度的互操作调用 | 批量合并为粗函数 — .NET→JS 和 JS→.NET |
| 组件直接导入 JS 模块 | 封装在带类型的互操作类中 |
| 方法名称/模块路径的魔法字符串 | 在互操作类中定义 `internal const` 字段 |
| 互操作包装器使用接口+实现 | 使用普通类；测试时模拟 `IJSRuntime` |
| JS 调用在 `OnInitializedAsync` 中 | 移动到 `OnAfterRenderAsync(firstRender)` |
| `InvokeAsync<object>` 用于空调用 | 使用 `InvokeVoidAsync` |
| `IDisposable` 与火并忘的 JS 调用 | 使用 `IAsyncDisposable` 并 `await` |
| 全局 `window.*` JS 函数 | 使用并置的 `.razor.js` 并包含 `export` |
| 传递给 JS 的字符串元素 ID | 使用 `ElementReference` 与 `@ref` |
| `[JSInvokable]` 在私有方法上 | 必须为 `public` — 否则运行时静默失败 |
| 未释放的 `DotNetObjectReference` | 在 `DisposeAsync` 中释放 — 导致内存泄漏 |
| 没有 `InvokeAsync` 的 `StateHasChanged()` | 在 `await InvokeAsync(() => { StateHasChanged(); })` 中封装 |
| JS `invokeMethodAsync` 没有错误处理 | 在 `try/catch` 中封装 — 电路丢失会抛出异常 |
| JS 事件处理程序中的裸 `dotNetRef` | 封装在一个类中，带有 `#dotNetRef` 私有字段 |
| JS `invokeMethodAsync` 调用中的魔法字符串 | 在模块顶部使用 `const` — 运行时拼写错误会静默失败 |
| `OnParametersSetAsync` 中的 JS 调用 | 跟踪变化，在 `OnAfterRenderAsync` 中应用，带保护 |
| 调用模块前没有空检查 | 在使用前检查 `module is not null` |
