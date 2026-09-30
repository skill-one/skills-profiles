---
name: author-component
description: 创建或审查具有正确架构的Blazor组件（.razor文件）。适用范围：编写不涉及JavaScript互操作的Blazor组件、实现参数和EventCallback、RenderFragment插槽、组件生命周期（OnInitializedAsync、OnParametersSet）、异步模式、IAsyncDisposable、CancellationToken、CSS隔离、代码隐藏。不适用范围：创建新项目（使用create-blazor-project）、JavaScript互操作或从Blazor调用浏览器API（使用use-js-interop）、表单和验证（使用collect-user-input）、预渲染问题（使用support-prerendering）、HTTP数据获取模式（使用fetch-and-send-data）、协调无关组件之间的状态（使用coordinate-components）。
---

# 作者 Blazor 组件

## 核心规则

- 数据通过 `[Parameter]` **向下**流动。事件通过 `EventCallback<T>` **向上**流动（绝不能使用 `Action`/`Func`）。
- 绝不修改 `[Parameter]` 属性。在 `OnParametersSet` 中将其复制到私有字段。
- 使用 `[Parameter] public T Prop { get; set; }` — 绝不能使用 `required` 或 `init`（会导致 BL0007 错误）。
- 使用 `[EditorRequired]` 标记必填参数。
- 处理所有状态：加载中、空、已加载、错误 — 每个状态使用 `@if`/`@else`。
- 在循环中的重复元素上使用 `@key` 以实现高效的差异比较。
- 集合参数使用 `IReadOnlyList<T>`（而不是 `IEnumerable<T>`）。

## RenderFragment 与泛型

```csharp
[Parameter] public RenderFragment? ChildContent { get; set; }
[Parameter] public RenderFragment<TItem>? RowTemplate { get; set; }  // 泛型模板
```

使用 `@typeparam TItem` 标记泛型组件。

## 文件模式

- **单文件：** `.razor` 文件在逻辑行数 < ~50 行时使用 `@code` 块。
- **代码隐藏：** `.razor` + `.razor.cs` 文件使用 `partial class` 当逻辑行数 > ~50 行时。

## 释放

当组件拥有订阅、计时器或 CTS 时，实现 `IAsyncDisposable`（而不是 `IDisposable`）。
在 `DisposeAsync` 中：取消订阅（`-=`）、取消 CTS、释放资源。绝不能调用 `StateHasChanged`。

## 异步模式

- 每个异步操作都使用 `await`。绝不能使用 `.Result`、`.Wait()`、`Task.Run`、`ContinueWith`、`Thread.Start`。
- **防抖：** `Task.Delay` + `CancellationTokenSource`。取消旧的 CTS，创建新的，等待延迟，执行操作。绝不能使用 `System.Threading.Timer` 或 `System.Timers.Timer`。
- **轮询：** 在 `OnInitializedAsync` 中使用循环，并使用 `await Task.Delay(interval, token)` — 保持同步上下文。
- **外部事件** (`Action<T>`)：使用 `async void` 处理器 + `await InvokeAsync(() => { state++; StateHasChanged(); })` + `catch` → `DispatchExceptionAsync`。绝不能 `_ = InvokeAsync(...)`。
- 在 `DisposeAsync` 中取消 CTS。不要捕获 `ObjectDisposedException` — 使用 CTS 取消。

## 禁止事项

- `[Parameter]` 上的 `required`/`init` — 运行时失败
- 修改 `[Parameter]` — 在 `OnParametersSet` 中复制到私有字段
- 使用 `Action`/`Func` 处理事件 — 使用 `EventCallback<T>`
- 使用 `Task.Run`/`.Result`/`.Wait()`/计时器进行防抖 — 死锁或线程池逃逸
- 内联 `style` 属性 — 使用 CSS 类或 `data-*` 属性
- `catch { throw; }` — 使用 `when` 守卫或让异常传播
- 过度设计：ARIA、包装 div、未请求的可访问性功能
- `_ = InvokeAsync(...)` — 吞噬异常；使用 `async void` + `DispatchExceptionAsync`
