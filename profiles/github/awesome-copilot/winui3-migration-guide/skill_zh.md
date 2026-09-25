# WinUI 3 迁移指南

在将 UWP 应用迁移到 WinUI 3 / Windows App SDK 时，或验证生成的代码是否使用正确的 WinUI 3 API 而不是遗留 UWP 模式时，请使用此技能。

---

## 命名空间变更

所有 `Windows.UI.Xaml.*` 命名空间都迁移到 `Microsoft.UI.Xaml.*`：

| UWP 命名空间 | WinUI 3 命名空间 |
|--------------|-------------------|
| `Windows.UI.Xaml` | `Microsoft.UI.Xaml` |
| `Windows.UI.Xaml.Controls` | `Microsoft.UI.Xaml.Controls` |
| `Windows.UI.Xaml.Media` | `Microsoft.UI.Xaml.Media` |
| `Windows.UI.Xaml.Input` | `Microsoft.UI.Xaml.Input` |
| `Windows.UI.Xaml.Data` | `Microsoft.UI.Xaml.Data` |
| `Windows.UI.Xaml.Navigation` | `Microsoft.UI.Xaml.Navigation` |
| `Windows.UI.Xaml.Shapes` | `Microsoft.UI.Xaml.Shapes` |
| `Windows.UI.Composition` | `Microsoft.UI.Composition` |
| `Windows.UI.Input` | `Microsoft.UI.Input` |
| `Windows.UI.Colors` | `Microsoft.UI.Colors` |
| `Windows.UI.Text` | `Microsoft.UI.Text` |
| `Windows.UI.Core` | `Microsoft.UI.Dispatching`（用于 dispatcher） |

---

## 最常见的 3 个 Copilot 错误

### 1. 没有 XamlRoot 的 ContentDialog

```csharp
// ❌ 错误 — 在 WinUI 3 中会抛出 InvalidOperationException
var dialog = new ContentDialog
{
    Title = "Error",
    Content = "Something went wrong.",
    CloseButtonText = "OK"
};
await dialog.ShowAsync();
```

```csharp
// ✅ 正确 — 在显示前设置 XamlRoot
var dialog = new ContentDialog
{
    Title = "Error",
    Content = "Something went wrong.",
    CloseButtonText = "OK",
    XamlRoot = this.Content.XamlRoot  // WinUI 3 中需要
};
await dialog.ShowAsync();
```

### 2. 使用 MessageDialog 而不是 ContentDialog

```csharp
// ❌ 错误 — UWP API，WinUI 3 桌面版中不可用
var dialog = new Windows.UI.Popups.MessageDialog("Are you sure?", "Confirm");
await dialog.ShowAsync();
```

```csharp
// ✅ 正确 — 使用 ContentDialog
var dialog = new ContentDialog
{
    Title = "Confirm",
    Content = "Are you sure?",
    PrimaryButtonText = "Yes",
    CloseButtonText = "No",
    XamlRoot = this.Content.XamlRoot
};
var result = await dialog.ShowAsync();
if (result == ContentDialogResult.Primary)
{
    // 用户确认
}
```

### 3. 使用 CoreDispatcher 而不是 DispatcherQueue

```csharp
// ❌ 错误 — CoreDispatcher 在 WinUI 3 中不存在
await Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
{
    StatusText.Text = "Done";
});
```

```csharp
// ✅ 正确 — 使用 DispatcherQueue
DispatcherQueue.TryEnqueue(() =>
{
    StatusText.Text = "Done";
});

// 带优先级：
DispatcherQueue.TryEnqueue(DispatcherQueuePriority.High, () =>
{
    ProgressBar.Value = 100;
});
```

---

## 窗口迁移

### 窗口引用

```csharp
// ❌ 错误 — Window.Current 在 WinUI 3 中不存在
var currentWindow = Window.Current;
```

```csharp
// ✅ 正确 — 在 App 中使用静态属性
public partial class App : Application
{
    public static Window MainWindow { get; private set; }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        MainWindow = new MainWindow();
        MainWindow.Activate();
    }
}
// 任何地方访问：App.MainWindow
```

### 窗口管理

| UWP API | WinUI 3 API |
|---------|-------------|
| `ApplicationView.TryResizeView()` | `AppWindow.Resize()` |
| `AppWindow.TryCreateAsync()` | `AppWindow.Create()` |
| `AppWindow.TryShowAsync()` | `AppWindow.Show()` |
| `AppWindow.TryConsolidateAsync()` | `AppWindow.Destroy()` |
| `AppWindow.RequestMoveXxx()` | `AppWindow.Move()` |
| `AppWindow.GetPlacement()` | `AppWindow.Position` 属性 |
| `AppWindow.RequestPresentation()` | `AppWindow.SetPresenter()` |

### 标题栏

| UWP API | WinUI 3 API |
|---------|-------------|
| `CoreApplicationViewTitleBar` | `AppWindowTitleBar` |
| `CoreApplicationView.TitleBar.ExtendViewIntoTitleBar` | `AppWindow.TitleBar.ExtendsContentIntoTitleBar` |

---

## 对话框和选择器的迁移

### 文件/文件夹选择器

```csharp
// ❌ 错误 — UWP 风格，没有窗口句柄
var picker = new FileOpenPicker();
picker.FileTypeFilter.Add(".txt");
var file = await picker.PickSingleFileAsync();
```

```csharp
// ✅ 正确 — 使用窗口句柄初始化
var picker = new FileOpenPicker();
var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(App.MainWindow);
WinRT.Interop.InitializeWithWindow.Initialize(picker, hwnd);
picker.FileTypeFilter.Add(".txt");
var file = await picker.PickSingleFileAsync();
```

## 线程迁移

| UWP 模式 | WinUI 3 等价物 |
|-------------|-------------------|
| `CoreDispatcher.RunAsync(priority, callback)` | `DispatcherQueue.TryEnqueue(priority, callback)` |
| `Dispatcher.HasThreadAccess` | `DispatcherQueue.HasThreadAccess` |
| `CoreDispatcher.ProcessEvents()` | 无等价物 — 重新组织异步代码 |
| `CoreWindow.GetForCurrentThread()` | 不可用 — 使用 `DispatcherQueue.GetForCurrentThread()` |

**关键差异**：UWP 使用 ASTA（应用程序 STA）并具有内置的递归阻塞保护。WinUI 3 使用标准 STA 而没有这种保护。注意异步代码在消息泵时可能会出现递归问题。

---

## 后台任务迁移

```csharp
// ❌ 错误 — UWP IBackgroundTask
public sealed class MyTask : IBackgroundTask
{
    public void Run(IBackgroundTaskInstance taskInstance) { }
}
```

```csharp
// ✅ 正确 — Windows App SDK AppLifecycle
using Microsoft.Windows.AppLifecycle;

// 注册激活
var args = AppInstance.GetCurrent().GetActivatedEventArgs();
if (args.Kind == ExtendedActivationKind.AppNotification)
{
    // 处理后台激活
}
```

---

## 应用设置迁移

| 场景 | 打包应用 | 未打包应用 |
|----------|-------------|----------------|
| 简单设置 | `ApplicationData.Current.LocalSettings` | `LocalApplicationData` 中的 JSON 文件 |
| 本地文件存储 | `ApplicationData.Current.LocalFolder` | `Environment.GetFolderPath(SpecialFolder.LocalApplicationData)` |

---

## GetForCurrentView() 替换

WinUI 3 桌面应用中所有 `GetForCurrentView()` 模式都不可用：

| UWP API | WinUI 3 替换 |
|---------|-------------------|
| `UIViewSettings.GetForCurrentView()` | 使用 `AppWindow` 属性 |
| `ApplicationView.GetForCurrentView()` | `AppWindow.GetFromWindowId(windowId)` |
| `DisplayInformation.GetForCurrentView()` | Win32 `GetDpiForWindow()` 或 `XamlRoot.RasterizationScale` |
| `CoreApplication.GetCurrentView()` | 不可用 — 手动跟踪窗口 |
| `SystemNavigationManager.GetForCurrentView()` | 直接在 `NavigationView` 中处理后退导航 |

---

## 测试迁移

UWP 单元测试项目与 WinUI 3 不兼容。您必须迁移到 WinUI 3 测试项目模板。

| UWP | WinUI 3 |
|-----|---------|
| 单元测试应用（通用 Windows） | **单元测试应用（桌面中的 WinUI）** |
| 标准 MSTest 项目，包含 UWP 类型 | 必须使用 WinUI 测试应用进行 Xaml 运行时 |
| 所有测试使用 `[TestMethod]` | 逻辑使用 `[TestMethod]`，XAML/UI 测试使用 `[UITestMethod]` |
| 类库（通用 Windows） | **类库（桌面中的 WinUI）** |

```csharp
// ✅ WinUI 3 单元测试 — 使用 [UITestMethod] 进行任何 XAML 交互
[UITestMethod]
public void TestMyControl()
{
    var control = new MyLibrary.MyUserControl();
    Assert.AreEqual(expected, control.MyProperty);
}
```

**关键**：`[UITestMethod]` 属性告诉测试运行器在 XAML UI 线程上执行测试，这对于实例化任何 `Microsoft.UI.Xaml` 类型是必需的。

---

## 迁移检查清单

1. [ ] 将所有 `Windows.UI.Xaml.*` using 指令替换为 `Microsoft.UI.Xaml.*`
2. [ ] 将 `Windows.UI.Colors` 替换为 `Microsoft.UI.Colors`
3. [ ] 将 `CoreDispatcher.RunAsync` 替换为 `DispatcherQueue.TryEnqueue`
4. [ ] 将 `Window.Current` 替换为 `App.MainWindow` 静态属性
5. [ ] 为所有 `ContentDialog` 实例添加 `XamlRoot`
6. [ ] 使用 `InitializeWithWindow.Initialize(picker, hwnd)` 初始化所有选择器
7. [ ] 将 `MessageDialog` 替换为 `ContentDialog`
8. [ ] 将 `ApplicationView`/`CoreWindow` 替换为 `AppWindow`
9. [ ] 将 `CoreApplicationViewTitleBar` 替换为 `AppWindowTitleBar`
10. [ ] 将所有 `GetForCurrentView()` 调用替换为 `AppWindow` 等价物
11. [ ] 更新共享和打印管理器的互操作
12. [ ] 将 `IBackgroundTask` 替换为 `AppLifecycle` 激活
13. [ ] 更新项目文件：TFM 为 `net10.0-windows10.0.22621.0`，添加 `<UseWinUI>true</UseWinUI>`
14. [ ] 将单元测试迁移到 **单元测试应用（桌面中的 WinUI）** 项目；使用 `[UITestMethod]` 进行 XAML 测试
15. [ ] 测试打包和未打包配置
