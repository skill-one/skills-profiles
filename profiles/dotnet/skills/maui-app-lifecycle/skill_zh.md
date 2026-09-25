# .NET MAUI 应用生命周期

正确处理 .NET MAUI 中的应用状态转换。这项技能涵盖了跨平台的窗口生命周期事件、它们与平台原生映射的关系，以及跨后台和恢复周期保存状态的模式。

## 何时使用

- 应用后台或恢复时保存或恢复状态
- 订阅窗口生命周期事件（Created、Activated、Deactivated、Stopped、Resumed、Destroying）
- 通过 `ConfigureLifecycleEvents` 钩入平台原生生命周期回调
- 确定初始化、拆解或刷新逻辑的位置
- 理解 Deactivated 和 Stopped 之间的区别

## 何时不用

- 页面级导航事件 — 使用 Shell 导航指南
- 启动时注册服务 — 使用依赖注入指南
- 在生命周期上下文外调用平台特定 API — 使用平台调用指南

## 输入

- 目标生命周期转换（例如，“后台时保存草稿”，“恢复时刷新数据”）
- 开发者目标平台（Android、iOS、Mac Catalyst、Windows）
- 应用是否使用多个窗口（iPad、Mac Catalyst、桌面 Windows）

## 应用状态

.NET MAUI 应用会经历四种状态：

| 状态 | 描述 |
|---|---|
| **未运行** | 进程不存在 |
| **运行** | 前台，接收输入 |
| **Deactivated** | 可见但失去焦点（对话框、分屏、通知栏） |
| **Stopped** | 完全后台，UI 不可见 |

典型流程：未运行 → 运行 → Deactivated → Stopped → 运行（恢复）或未运行（终止）。

## 窗口生命周期事件

`Microsoft.Maui.Controls.Window` 提供了六个跨平台事件：

| 事件 | 触发时机 |
|---|---|
| `Created` | 原生窗口分配 |
| `Activated` | 窗口获得输入焦点 |
| `Deactivated` | 窗口失去焦点（可能仍然可见） |
| `Stopped` | 窗口不再可见 |
| `Resumed` | 窗口恢复到前台后 |
| `Destroying` | 原生窗口正在被销毁 |

### 通过 CreateWindow 订阅

在 `App` 类中重写 `CreateWindow` 并附加事件处理器：

```csharp
public partial class App : Application
{
    protected override Window CreateWindow(IActivationState? activationState)
    {
        var window = base.CreateWindow(activationState);

        window.Created += (s, e) => Debug.WriteLine("Created");
        window.Activated += (s, e) => Debug.WriteLine("Activated");
        window.Deactivated += (s, e) => Debug.WriteLine("Deactivated");
        window.Stopped += (s, e) => Debug.WriteLine("Stopped");
        window.Resumed += (s, e) => Debug.WriteLine("Resumed");
        window.Destroying += (s, e) => Debug.WriteLine("Destroying");

        return window;
    }
}
```

### 通过自定义窗口子类订阅

创建 `Window` 子类并重写虚拟方法：

```csharp
public class AppWindow : Window
{
    public AppWindow(Page page) : base(page) { }

    protected override void OnActivated() { /* 刷新 UI */ }
    protected override void OnStopped() { /* 保存状态 */ }
    protected override void OnResumed() { /* 恢复状态 */ }
    protected override void OnDestroying() { /* 清理 */ }
}
```

从 `CreateWindow` 返回它：

```csharp
protected override Window CreateWindow(IActivationState? activationState)
    => new AppWindow(new AppShell());
```

## 工作流：后台时保存和恢复状态

1. **识别临时状态** — 草稿文本、滚动位置、表单输入、计时器值。
2. **在 `OnStopped` 中保存** — 使用 `Preferences` 保存小值或文件序列化保存较大状态。
3. **在 `OnResumed` 中恢复** — 读取保存的值并应用到你的视图模型。
4. **在 Android 上也在 `OnDestroying` 中保存** — 后退按钮可能完全跳过 `Stopped`。
5. **保持处理器快速** — 在 1-2 秒内完成，以避免 Android 上的 ANR 或 iOS 上的看门狗杀死。

```csharp
protected override void OnStopped()
{
    base.OnStopped();
    Preferences.Set("draft_text", _viewModel.DraftText);
    Preferences.Set("scroll_y", _viewModel.ScrollY);
}

protected override void OnResumed()
{
    base.OnResumed();
    _viewModel.DraftText = Preferences.Get("draft_text", string.Empty);
    _viewModel.ScrollY = Preferences.Get("scroll_y", 0.0);
}

protected override void OnDestroying()
{
    base.OnDestroying();
    // Android back-button can skip Stopped
    Preferences.Set("draft_text", _viewModel.DraftText);
}
```

## 平台生命周期映射

### Android

| 窗口事件 | Android 回调 |
|---|---|
| Created | `OnCreate` |
| Activated | `OnResume` |
| Deactivated | `OnPause` |
| Stopped | `OnStop` |
| Resumed | `OnRestart` → `OnStart` → `OnResume` |
| Destroying | `OnDestroy` |

### iOS / Mac Catalyst

| 窗口事件 | UIKit 回调 | `AddiOS` 构建器方法 |
|---|---|---|
| Created | `WillFinishLaunching` / `SceneWillConnect` | `.WillFinishLaunching()` / `.SceneWillConnect()` |
| Activated | `DidBecomeActive` | `.OnActivated()` |
| Deactivated | `WillResignActive` | `.OnResignActivation()` |
| Stopped | `DidEnterBackground` | `.DidEnterBackground()` |
| Resumed | `WillEnterForeground` | `.WillEnterForeground()` |
| Destroying | `WillTerminate` | `.WillTerminate()` |

> ⚠️ UIKit 选择器名称和 `AddiOS` 构建器方法名称在激活时不同。没有 `.DidBecomeActive()` 或 `.WillResignActive()` 构建器方法 — 使用 `.OnActivated()` 和 `.OnResignActivation()`，否则代码将无法编译。

### Windows (WinUI)

| 窗口事件 | WinUI 回调 |
|---|---|
| Created | `OnLaunched` |
| Activated | `Activated`（前台） |
| Deactivated | `Activated`（后台） |
| Stopped | `VisibilityChanged`（false） |
| Resumed | `VisibilityChanged`（true） |
| Destroying | `Closed` |

## 直接钩入原生生命周期

当需要窗口事件提供的平台特定回调之外的功能时，在 `MauiProgram.cs` 中使用 `ConfigureLifecycleEvents`：

```csharp
builder.ConfigureLifecycleEvents(events =>
{
#if ANDROID
    events.AddAndroid(android => android
        .OnCreate((activity, bundle) => Debug.WriteLine("Android OnCreate"))
        .OnResume(activity => Debug.WriteLine("Android OnResume"))
        .OnPause(activity => Debug.WriteLine("Android OnPause"))
        .OnStop(activity => Debug.WriteLine("Android OnStop"))
        .OnDestroy(activity => Debug.WriteLine("Android OnDestroy")));
#elif IOS || MACCATALYST
    events.AddiOS(ios => ios
        .OnActivated(app => Debug.WriteLine("iOS OnActivated"))
        .OnResignActivation(app => Debug.WriteLine("iOS OnResignActivation"))
        .DidEnterBackground(app => Debug.WriteLine("iOS DidEnterBackground"))
        .WillEnterForeground(app => Debug.WriteLine("iOS WillEnterForeground")));
#elif WINDOWS
    events.AddWindows(windows => windows
        .OnLaunched((app, args) => Debug.WriteLine("Windows OnLaunched"))
        .OnActivated((window, args) => Debug.WriteLine("Windows Activated"))
        .OnClosed((window, args) => Debug.WriteLine("Windows Closed")));
#endif
});
```

## 常见陷阱

1. **首次启动时不会触发 Resumed。** 初始序列是 `Created` → `Activated`。使用 `OnActivated` 处理必须在每个前台进入时运行的逻辑，而不是 `OnResumed`。

2. **Deactivated ≠ Stopped。** 对话框、分屏或通知栏下拉会触发 `Deactivated` 而不触发 `Stopped`。不要在 `OnDeactivated` 中执行重保存 — 应用可能永远不会实际后台。

3. **Android 后退按钮跳过 Stopped。** 在 Android 上，按后退键可能直接调用 `Destroying` 而不调用 `Stopped`。在 `OnStopped` 和 `OnDestroying` 中放置关键保存逻辑。

4. **多窗口应用独立触发事件。** 在 iPad、Mac Catalyst 和桌面 Windows 上，每个 `Window` 实例都会独立触发其生命周期事件。不要假设有单个全局生命周期。

5. **长时间运行的处理器会导致杀死。** Android 强制约 5 秒的 ANR 超时；iOS 有限的后台执行时间。保持生命周期处理器同步且快速 — 使用 `Preferences` 进行快速保存，而不是数据库写入。

6. **不要使用遗留的 Xamarin.Forms 生命周期方法。** `Application.OnStart()`、`Application.OnSleep()` 和 `Application.OnResume()` 存在是为了向后兼容，但会绕过窗口级事件。在 .NET MAUI 中，优先使用 `Window` 生命周期事件（`OnActivated`、`OnStopped`、`OnResumed` 等）以获得正确的多窗口行为。
