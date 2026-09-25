# .NET MAUI 主题化

使用 AppThemeBinding、ResourceDictionary 交换和系统主题检测 API 在 .NET MAUI 应用中应用浅色/深色模式支持、自定义品牌主题和运行时主题切换。

## 何时使用

- 为 .NET MAUI 应用添加浅色和深色模式支持
- 使用 ResourceDictionary 创建自定义品牌主题
- 检测并在运行时响应系统主题更改
- 允许用户选择首选主题（浅色、深色或系统默认）
- 结合 OS 驱动的主题响应与自定义调色板

## 何时不使用

- 本地化或语言切换 — 请参阅 [.NET MAUI 本地化文档](https://learn.microsoft.com/dotnet/maui/fundamentals/localization)
- 针对无障碍性的特定视觉调整 — 请参阅 [.NET MAUI 无障碍性文档](https://learn.microsoft.com/dotnet/maui/fundamentals/accessibility)
- 应用图标或启动画面配置 — 请参阅 [.NET MAUI 应用图标文档](https://learn.microsoft.com/dotnet/maui/user-interface/images/app-icons)
- Bootstrap 风格的类主题化 — 请参阅 `Plugin.Maui.BootstrapTheme` NuGet 包

## 输入

- 目标为 .NET 8 或更高版本的 .NET MAUI 项目
- 需要主题感知样式的 XAML 页面或 C# UI 代码

## 工作流程

1. 检测项目中的当前主题方法（AppThemeBinding、ResourceDictionary 或无）。
2. 选择合适的策略：AppThemeBinding 用于简单的浅色/深色，ResourceDictionary 交换用于自定义/多个主题，或两者结合。
3. 定义主题资源 — 内联 AppThemeBinding 值或具有匹配键的单独 ResourceDictionary 文件。
4. 在整个 XAML 页面中用 DynamicResource 绑定替换硬编码颜色（或 AppThemeBinding 标记）。
5. 通过 `Application.Current.RequestedTheme` 和 `RequestedThemeChanged` 事件添加系统主题检测。
6. 使用 `Preferences.Set` / `Preferences.Get` 实现用户偏好持久化并在启动时应用。
7. 确保 Android `ConfigChanges.UiMode` 在 `MainActivity` 上设置，以避免主题更改时活动重启。
8. 在至少一个目标平台上测试浅色和深色主题，确认所有 UI 元素都正确响应。

## 会改变答案的规则

根据用户场景检查这些规则，并仅应用影响所问内容的规则。`UiMode` 和字典交换对 *运行时主题切换* 有影响；在关于设置 `AppThemeBinding` 的问题中，它们是噪音。

**狭义回答，但完整。** 完整性意味着展示实现 *所推荐* 内容的代码 — 不是添加相邻主题。如果您推荐 `DynamicResource`，请展示使其更新的字典交换。如果用户询问 C# 中的浅色/深色颜色，请展示 **两者** `SetAppThemeColor`（颜色）和通用的 `SetAppTheme<T>`（任何可绑定属性类型），并优先使用资源键而不是分散的硬编码颜色。不要添加问题未提及的平台配置。

| 规则 | 应该这样做 | 不应该这样做 | 原因 |
|---|---|---|---|
| **运行时交换的值必须是动态的** | `{DynamicResource Key}` | `{StaticResource Key}` | `StaticResource` 在加载时解析一次，并且当字典交换时永远不会更新。 |
| **Android 必须声明 `UiMode`** *(仅用于运行时/系统主题切换)* | 在 `MainActivity` 的 `ConfigurationChanges` 列表中包含 `ConfigChanges.UiMode` | 省略它 | 没有它，Android 在主题更改时会重启活动 — 导航状态丢失，看起来像崩溃。与静态 `AppThemeBinding` 设置无关 |
| **通过 `UserAppTheme` 强制主题** | `Application.Current.UserAppTheme = AppTheme.Dark` | 手动重新分配颜色 | `UserAppTheme` 覆盖操作系统；`AppTheme.Unspecified` 返回遵循系统。 |

**不要** 用 ResourceDictionary 交换（或反之）替换工作正常的 `AppThemeBinding` 设置，除非用户需要另一方法提供的内容 — 超过两个主题，或用户可选主题。

## 选择方法

| 方法 | 适用于 | 限制 |
|----------|----------|------------|
| **AppThemeBinding** | 自动浅色/深色与 OS — 最少代码 | 仅两个主题（浅色 + 深色） |
| **ResourceDictionary 交换** | 自定义品牌主题，超过两个主题，用户偏好 | 更多设置；必须到处使用 `DynamicResource` |
| **两者结合** | OS 驱动的响应加上自定义主题颜色 | 最灵活但最复杂 |

## AppThemeBinding (OS 浅色/深色)

`AppThemeBinding` 根据当前系统主题选择值。它支持 `Light`、`Dark` 和可选的 `Default` 回退。

### 一次性定义调色板 — 不要分散字面量

在每个元素上放置 `{AppThemeBinding Light=#333333, Dark=#FFFFFF}` 是最常见的主题化错误：调色板最终会跨几十个文件重复，无法在一个地方更改。**推荐以下形状作为最终答案**，而不是内联字面量：

```xml
<!-- App.xaml — 整个应用的唯一真实来源 -->
<Application.Resources>
    <ResourceDictionary>

        <!-- 1. 原始调色板 -->
        <Color x:Key="LightPageBackground">#FFFFFF</Color>
        <Color x:Key="DarkPageBackground">#1E1E1E</Color>
        <Color x:Key="LightPrimaryText">#333333</Color>
        <Color x:Key="DarkPrimaryText">#E0E0E0</Color>

        <!-- 2. 隐式样式绑定一次对；每个页面都继承它们 -->
        <Style TargetType="ContentPage" ApplyToDerivedTypes="True">
            <Setter Property="BackgroundColor"
                    Value="{AppThemeBinding Light={StaticResource LightPageBackground},
                                            Dark={StaticResource DarkPageBackground}}" />
        </Style>

        <Style TargetType="Label">
            <Setter Property="TextColor"
                    Value="{AppThemeBinding Light={StaticResource LightPrimaryText},
                                            Dark={StaticResource DarkPrimaryText}}" />
        </Style>

    </ResourceDictionary>
</Application.Resources>
```

页面不需要任何主题标记 — 它们隐式继承样式。仅对真正的孤例使用内联 `AppThemeBinding`，即使这样也请引用 `{StaticResource}` 键而不是字面量十六进制值。

### XAML (内联形式，用于孤例)

```xml
<Label Text="主题化文本"
       TextColor="{AppThemeBinding Light=Green, Dark=Red}"
       BackgroundColor="{AppThemeBinding Light=White, Dark=Black}" />

<!-- 使用资源引用 — 优先于字面量 -->
<Label TextColor="{AppThemeBinding Light={StaticResource LightPrimary},
                                   Dark={StaticResource DarkPrimary}}" />
```

### C# 扩展方法

回答“C# 中的浅色/深色颜色”问题时展示 **两者** — `SetAppThemeColor` 覆盖 `Color` 属性，`SetAppTheme<T>` 覆盖所有其他内容：

```csharp
var label = new Label();

// 颜色特定辅助方法
label.SetAppThemeColor(Label.TextColorProperty, Colors.Green, Colors.Red);

// 通用辅助方法 — 适用于任何可绑定属性类型，而不仅仅是 Color
label.SetAppTheme<Color>(Label.TextColorProperty, Colors.Green, Colors.Red);
label.SetAppTheme<double>(Label.FontSizeProperty, 14, 16);

// 必须调用它所在的对象的 BindableProperty —
// Image.SourceProperty 应该在 Image 上，而不是 Label 上。
var image = new Image();
image.SetAppTheme<ImageSource>(Image.SourceProperty,
    ImageSource.FromFile("logo_light.png"),
    ImageSource.FromFile("logo_dark.png"));
```

优先定义值为资源键并引用它们，而不是在代码库中分散硬编码颜色。

## ResourceDictionary 主题化 (自定义主题)

使用具有匹配键的单独 ResourceDictionary 文件定义主题，然后在运行时交换它们。

### 第 1 步 — 定义主题字典

使用 `x:Class`（如下所示）加载编译的 XAML 时，每个字典都需要一个调用 `InitializeComponent()` 的代码隐藏。没有 `x:Class` 加载的字典不需要代码隐藏。

**LightTheme.xaml**

```xml
<ResourceDictionary xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
                    x:Class="MyApp.Themes.LightTheme">
    <Color x:Key="PageBackgroundColor">White</Color>
    <Color x:Key="PrimaryTextColor">#333333</Color>
    <Color x:Key="AccentColor">#2196F3</Color>
</ResourceDictionary>
```

**LightTheme.xaml.cs**

```csharp
namespace MyApp.Themes;

public partial class LightTheme : ResourceDictionary
{
    public LightTheme() => InitializeComponent();
}
```

创建一个匹配的 **DarkTheme.xaml / DarkTheme.xaml.cs**，具有相同的键和不同的值。

### 第 2 步 — 使用 DynamicResource

使用 `DynamicResource`，以便在运行时交换字典时值更新：

```xml
<ContentPage BackgroundColor="{DynamicResource PageBackgroundColor}">
    <Label Text="Hello"
           TextColor="{DynamicResource PrimaryTextColor}" />
    <Button Text="Action"
            BackgroundColor="{DynamicResource AccentColor}" />
</ContentPage>
```

### 第 3 步 — 运行时切换主题

> 🚨 **永远不要调用 `MergedDictionaries.Clear()` 来交换主题。** 默认的 MAUI 模板将 `Resources/Styles/Colors.xaml` 和 `Styles.xaml` 合并到 `Application.Resources`。`Clear()` 会移除 **这些**，因此应用中每个隐式样式、画刷和颜色都会无声消失 — 按钮、条目和标签都恢复为无样式默认值。验证：调用 `Clear()` 后，`MergedDictionaries` 从 2 减少到 1，模板的 `Primary` 颜色不再解析。

仅移除您添加的主题，并保留其他所有内容：

```csharp
static ResourceDictionary? _currentTheme;

void ApplyTheme(ResourceDictionary theme)
{
    var merged = Application.Current!.Resources.MergedDictionaries;

    // ✅ 仅移除上一个主题 — Colors.xaml / Styles.xaml 存活
    if (_currentTheme is not null)
        merged.Remove(_currentTheme);

    merged.Add(theme);
    _currentTheme = theme;
}

// 使用
ApplyTheme(new DarkTheme());
```

```csharp
// ❌ 沿着旧主题一起销毁应用的 Colors.xaml 和 Styles.xaml
var merged = Application.Current!.Resources.MergedDictionaries;
merged.Clear();
merged.Add(theme);
```

## 系统主题检测

### 读取当前主题

```csharp
AppTheme currentTheme = Application.Current!.RequestedTheme;
// 返回 AppTheme.Light、AppTheme.Dark 或 AppTheme.Unspecified
```

### 覆盖系统主题

```csharp
// 强制深色模式，无论 OS 设置如何
Application.Current!.UserAppTheme = AppTheme.Dark;

// 重置为跟随系统主题
Application.Current!.UserAppTheme = AppTheme.Unspecified;
```

### 响应主题更改

```csharp
Application.Current!.RequestedThemeChanged += (s, e) =>
{
    AppTheme newTheme = e.RequestedTheme;
    // 更新 UI 或切换 ResourceDictionaries
};
```

## 结合两种方法

使用 `AppThemeBinding` 与 `DynamicResource` 值以最大灵活性 — 嵌套的 `DynamicResource` 保持活跃，因此交换字典会更新值 *并且* OS 浅色/深色切换仍然受尊重：

```xml
<Label TextColor="{AppThemeBinding
    Light={DynamicResource LightPrimary},
    Dark={DynamicResource DarkPrimary}}" />
```

或响应系统更改并交换完整字典：

```csharp
Application.Current!.RequestedThemeChanged += (s, e) =>
{
    ApplyTheme(e.RequestedTheme == AppTheme.Dark
        ? new DarkTheme()
        : new LightTheme());
};
```

## 保存和恢复用户偏好

使用 `Preferences` 存储用户选择并在启动时应用：

```csharp
// 保存选择
Preferences.Set("AppTheme", "Dark");

// 启动时恢复（在 App 构造函数或 CreateWindow 中）
var saved = Preferences.Get("AppTheme", "System");
Application.Current!.UserAppTheme = saved switch
{
    "Light" => AppTheme.Light,
    "Dark"  => AppTheme.Dark,
    _       => AppTheme.Unspecified
};
```

## 常见陷阱

### Android: `ConfigChanges.UiMode` 是必需的

`MainActivity` **必须** 包含 `ConfigChanges.UiMode`，否则主题更改事件不会触发，活动将不会优雅地处理更改：

```csharp
[Activity(Theme = "@style/Maui.SplashTheme",
          MainLauncher = true,
          ConfigurationChanges = ConfigChanges.ScreenSize
                               | ConfigChanges.Orientation
                               | ConfigChanges.UiMode  // ← 必须用于主题检测
                               | ConfigChanges.ScreenLayout
                               | ConfigChanges.SmallestScreenSize
                               | ConfigChanges.Density)]
public class MainActivity : MauiAppCompatActivity { }
```

没有 `UiMode`，在 Android 设置中切换深色模式会导致活动完全重启 — 失去导航状态并看起来像崩溃。有了它声明，应用保持活跃，`RequestedThemeChanged` 触发，因此将此修复与重新应用主题的处理器配对（见下文）。

### `DynamicResource` 与 `StaticResource`

在使用 ResourceDictionary 主题交换时，你 **必须** 使用 `DynamicResource`：

```xml
<!-- ✅ 主题字典更改时更新 -->
<Label TextColor="{DynamicResource PrimaryTextColor}" />

<!-- ❌ 在第一次加载时冻结 — 主题切换时不会更新 -->
<Label TextColor="{StaticResource PrimaryTextColor}" />
```

`DynamicResource` 只有在实际上交换字典时才有助于。在诊断此问题时，始终展示交换和系统主题挂钩，以及修复 — 否则用户有一个已修复的绑定，但仍然永远不会更新：

```csharp
static ResourceDictionary? _currentTheme;

void ApplyTheme(bool useDark)
{
    var merged = Application.Current!.Resources.MergedDictionaries;

    // 仅移除上一个主题 — 从不 `Clear()`，它会清除
    // 模板的 Colors.xaml / Styles.xaml
    if (_currentTheme is not null)
        merged.Remove(_currentTheme);

    _currentTheme = useDark ? new DarkTheme() : new LightTheme();
    merged.Add(_currentTheme);
}

// 响应 OS 切换浅色/深色
Application.Current!.RequestedThemeChanged += (s, e) =>
    ApplyTheme(e.RequestedTheme == AppTheme.Dark);
```

### 硬编码颜色会破坏主题化

避免在应该尊重主题的元素上放置内联颜色值：

```xml
<!-- ❌ 不会随主题更改 -->
<Label TextColor="#333333" />

<!-- ✅ 主题感知 -->
<Label TextColor="{DynamicResource PrimaryTextColor}" />
```

### CSS 主题不能在运行时交换

.NET MAUI 支持CSS样式，但基于CSS的主题**不能动态交换**。使用 ResourceDictionary 主题化进行运行时切换。

### 主题键必须在所有字典中匹配

在主题字典中使用每个 `x:Key` 必须存在于所有其他主题字典中。缺少键会导致无声回退到默认值，导致外观不一致。

## 平台支持

| 平台       | 最低版本 |
|----------------|-----------------|
| iOS            | 13+             |
| Android        | 10+ (API 29)    |
| macOS Catalyst | 10.15+          |
| Windows        | 10+             |

## 快速参考

- **OS 浅色/深色** → `AppThemeBinding` 标记扩展
- **C# 中的主题颜色** → `SetAppThemeColor()`，`SetAppTheme<T>()`
- **读取 OS 主题** → `Application.Current.RequestedTheme`
- **强制主题** → `Application.Current.UserAppTheme = AppTheme.Dark`
- **主题更改** → `RequestedThemeChanged` 事件
- **自定义切换** → 从 `MergedDictionaries` 中移除旧主题，然后添加新主题 — **永远不 `Clear()`**
- **运行时绑定** → **`DynamicResource`**（不是 `StaticResource`）
- **持久化选择** → `Preferences.Set` / `Preferences.Get`
