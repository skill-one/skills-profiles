# 安全区域与边缘到边缘布局 (.NET 10+)

.NET 10 引入了一个全新的跨平台安全区域 API，取代了传统的仅适用于 iOS 的 `UseSafeArea` 和布局级别的 `IgnoreSafeArea` 属性。新的 `SafeAreaEdges` 属性和 `SafeAreaRegions` 标志枚举让你能够在 Android、iOS 和 Mac Catalyst 上通过单一 API 表面进行每边每控件的独立安全区域管理。

> **这是 .NET 10 中的新 API 表面。** 如果项目目标是 .NET 9 或更早版本，则这些 API 不存在。请开发人员使用传统的 `ios:Page.UseSafeArea` 和 `Layout.IgnoreSafeArea` 属性。

## 何时使用

- 升级到 .NET 10 后，内容与状态栏、缺口、动态岛或主指示器重叠
- 实现边缘到边缘/沉浸式布局（照片查看器、视频播放器、地图）
- 聊天或表单 UI 的键盘避免
- 从 `ios:Page.UseSafeArea`、`Layout.IgnoreSafeArea` 或 `WindowSoftInputModeAdjust.Resize` 迁移
- 需要协调 CSS `env(safe-area-inset-*)` 的 Blazor 混合应用
- 混合布局，具有边缘到边缘的标题但安全区域兼容的正文

## 何时不使用

- 目标为 .NET 9 或更早版本的项目 — 使用传统的 iOS 特定 API
- 与系统栏或键盘无关的通用页面布局问题 — 使用标准布局指南
- 应用生命周期或导航结构 — 使用 maui-app-lifecycle 或 Shell 指南
- 主题或视觉样式 — 使用 **maui-theming** 技能

## 输入

- 目标框架：必须为 `net10.0-*` 或更高版本以使用新 API
- 目标平台：Android、iOS、Mac Catalyst（Windows 没有系统栏内边距）
- UI 方法：XAML/C#、Blazor 混合或 MauiReactor

## SafeAreaRegions 枚举

```csharp
[Flags]
public enum SafeAreaRegions
{
    None      = 0,       // 边缘到边缘 — 无安全区域填充
    SoftInput = 1 << 0,  // 填充以避免屏幕键盘
    Container = 1 << 1,  // 停留在状态栏、缺口、主指示器内
    Default   = -1,      // 使用控件类型的平台默认值
    All       = 1 << 15  // 尊重所有安全区域内边距（最严格的）
}
```

`SoftInput` 和 `Container` 是可组合的标志：
`SafeAreaRegions.Container | SafeAreaRegions.SoftInput` = 尊重系统栏 **和** 键盘。

## SafeAreaEdges 结构

```csharp
public readonly struct SafeAreaEdges
{
    public SafeAreaRegions Left { get; }
    public SafeAreaRegions Top { get; }
    public SafeAreaRegions Right { get; }
    public SafeAreaRegions Bottom { get; }

    // 统一 — 所有四边的值相同
    public SafeAreaEdges(SafeAreaRegions uniformValue)

    // 水平 / 垂直
    public SafeAreaEdges(SafeAreaRegions horizontal, SafeAreaRegions vertical)

    // 每边
    public SafeAreaEdges(SafeAreaRegions left, SafeAreaRegions top,
                         SafeAreaRegions right, SafeAreaRegions bottom)
}
```

静态预设：`SafeAreaEdges.None`、`SafeAreaEdges.All`、`SafeAreaEdges.Default`。

### XAML 类型转换器

遵循类似 Thickness 的逗号分隔语法：

```xaml
<!-- 统一 -->
SafeAreaEdges="Container"

<!-- 水平、垂直 -->
SafeAreaEdges="Container, SoftInput"

<!-- 左、上、右、下 -->
SafeAreaEdges="Container, Container, Container, SoftInput"
```

## 控件默认值

| 控件 | 默认值 | 备注 |
|------|------|------|
| `ContentPage` | `None` | 边缘到边缘。**从 .NET 9 在 Android 上引入的破坏性变更。** |
| `Layout`（Grid、StackLayout 等） | `Container` | 尊重栏/缺口，在键盘下流动 |
| `ScrollView` | `Default` | iOS 映射到自动内容内边距。仅 `Container` 和 `None` 生效。 |
| `ContentView` | `None` | 继承父行为 |
| `Border` | `None` | 继承父行为 |

## 从 .NET 9 引入的破坏性变更

### ContentPage 默认值更改为 `None`

在 .NET 9 中，Android `ContentPage` 的行为类似于 `Container`。在 .NET 10 中，默认值在 **所有平台** 上都是 `None`。如果您在升级后 Android 内容在状态栏下方：

```xaml
<!-- .NET 10 默认 — 内容延伸到状态栏下方 -->
<ContentPage>

<!-- 恢复 .NET 9 Android 行为 -->
<ContentPage SafeAreaEdges="Container">
```

### WindowSoftInputModeAdjust.Resize 被取代

`WindowSoftInputModeAdjust.Resize` 仍然存在并且仍然可以编译（它没有被移除且不标记为过时），但它仅适用于 Android。对于跨平台的键盘避免，请在 ContentPage 上使用 `SafeAreaEdges="All"`（或 `SoftInput` 区域）。

## 使用模式

### 边缘到边缘沉浸式内容

在页面和布局上**都**设置 `None` — 布局默认为 `Container`：

```xaml
<ContentPage SafeAreaEdges="None">
    <Grid SafeAreaEdges="None">
        <Image Source="background.jpg" Aspect="AspectFill" />
        <VerticalStackLayout Padding="20" VerticalOptions="End">
            <Label Text="Overlay text" TextColor="White" FontSize="24" />
        </VerticalStackLayout>
    </Grid>
</ContentPage>
```

### 表单和关键内容

```xaml
<ContentPage SafeAreaEdges="All">
    <VerticalStackLayout Padding="20">
        <Label Text="Safe content" FontSize="18" />
        <Entry Placeholder="Enter text" />
        <Button Text="Submit" />
    </VerticalStackLayout>
</ContentPage>
```

### 键盘感知聊天布局

```xaml
<ContentPage>
    <Grid RowDefinitions="*,Auto"
          SafeAreaEdges="Container, Container, Container, SoftInput">
        <ScrollView Grid.Row="0">
            <VerticalStackLayout Padding="20" Spacing="10">
                <Label Text="Messages" FontSize="24" />
            </VerticalStackLayout>
        </ScrollView>
        <Border Grid.Row="1" BackgroundColor="LightGray" Padding="20">
            <Grid ColumnDefinitions="*,Auto" Spacing="10">
                <Entry Placeholder="Type a message..." />
                <Button Grid.Column="1" Text="Send" />
            </Grid>
        </Border>
    </Grid>
</ContentPage>
```

### 混合：边缘到边缘的标题 + 安全正文 + 键盘页脚

```xaml
<ContentPage SafeAreaEdges="None">
    <Grid RowDefinitions="Auto,*,Auto">
        <Grid BackgroundColor="{StaticResource Primary}">
            <Label Text="App Header" TextColor="White" Margin="20,40,20,20" />
        </Grid>
        <ScrollView Grid.Row="1" SafeAreaEdges="Container">
            <!-- 使用 Container，而不是 All — ScrollView 仅尊重 Container 和 None -->
            <VerticalStackLayout Padding="20">
                <Label Text="Main content" />
            </VerticalStackLayout>
        </ScrollView>
        <Grid Grid.Row="2" SafeAreaEdges="SoftInput"
              BackgroundColor="LightGray" Padding="20">
            <Entry Placeholder="Type a message..." />
        </Grid>
    </Grid>
</ContentPage>
```

### 代码（C#）

```csharp
var page = new ContentPage
{
    SafeAreaEdges = SafeAreaEdges.All
};

var grid = new Grid
{
    SafeAreaEdges = new SafeAreaEdges(
        left: SafeAreaRegions.Container,
        top: SafeAreaRegions.Container,
        right: SafeAreaRegions.Container,
        bottom: SafeAreaRegions.SoftInput)
};
```

## 决策框架

| 场景 | SafeAreaEdges 值 |
|------|------------------|
| 表单、关键输入 | `All` |
| 照片查看器、视频播放器、游戏 | `None`（在页面 **和** 布局上） |
| 可滚动内容带固定页眉/页脚 | `Container` |
| 带底部输入栏的聊天/消息 | 每边：`Container, Container, Container, SoftInput` |
| Blazor 混合应用 | 页面为 `None`；CSS `env()` 用于内边距 |

## Blazor 混合集成

对于 Blazor 混合应用，让 CSS 处理安全区域以避免双重填充。

1. **页面保持边缘到边缘**（.NET 10 中的默认值）：

```xaml
<ContentPage SafeAreaEdges="None">
    <BlazorWebView HostPage="wwwroot/index.html">
        <BlazorWebView.RootComponents>
            <RootComponent Selector="#app" ComponentType="{x:Type local:Routes}" />
        </BlazorWebView.RootComponents>
    </BlazorWebView>
</ContentPage>
```

2. **在 `index.html` 中添加 `viewport-fit=cover`**：

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
```

3. **使用 CSS `env()` 函数**：

```css
body {
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}
```

可用的 CSS 环境变量：`env(safe-area-inset-top)`、`env(safe-area-inset-bottom)`、`env(safe-area-inset-left)`、`env(safe-area-inset-right)`。

## 从传统 API 迁移

| 传统（.NET 9 及更早版本） | 新版（.NET 10+） |
|---------------------------|------------------|
| `ios:Page.UseSafeArea="True"` | `SafeAreaEdges="Container"` |
| `Layout.IgnoreSafeArea="True"` | `SafeAreaEdges="None"` |
| `WindowSoftInputModeAdjust.Resize` | `SafeAreaEdges="All"` 在 ContentPage |

传统的 `ios:Page.UseSafeArea` 和 `Layout.IgnoreSafeArea` 属性仍然可以编译但已标记为过时。`IgnoreSafeArea="True"` 内部映射到 `SafeAreaRegions.None`。`WindowSoftInputModeAdjust.Resize` **不**过时 — 它仍然受支持，但仅适用于 Android。

```xaml
<!-- .NET 9（传统，仅适用于 iOS） -->
<ContentPage xmlns:ios="clr-namespace:Microsoft.Maui.Controls.PlatformConfiguration.iOSSpecific;assembly=Microsoft.Maui.Controls"
             ios:Page.UseSafeArea="True">

<!-- .NET 10+（跨平台） -->
<ContentPage SafeAreaEdges="Container">
```

## 平台特定行为

### iOS & Mac Catalyst

- 安全区域内边距覆盖：状态栏、导航栏、标签栏、缺口/Dynamic Island、主指示器
- `SoftInput` 在键盘可见时包括键盘
- 内边距在旋转和 UI 可见性变化时自动更新
- `ScrollView` 与 `Default` 映射到 `UIScrollViewContentInsetAdjustmentBehavior.Automatic`

内容在导航栏后面的透明导航栏：

```xaml
<Shell Shell.BackgroundColor="#80000000" Shell.NavBarHasShadow="False" />
```

### Android

- 安全区域内边距覆盖：系统栏（状态/导航）和显示缺口
- `SoftInput` 包括软键盘
- MAUI 使用 `WindowInsetsCompat` 和 `WindowInsetsAnimationCompat` 内部
- 行为因 Android 版本和 OEM 边缘到边缘设置而异

## 常见陷阱

1. **忘记在布局上设置 `None`。** `ContentPage SafeAreaEdges="None"` 使页面边缘到边缘，但子布局默认为 `Container` 并仍然向内填充。在页面和布局上**都**设置 `None` 以获得真正的沉浸式内容。

2. **在 ScrollView 上直接使用 `SoftInput`。** ScrollView 管理自己的内容内边距并忽略 `SoftInput`。将 ScrollView 包裹在 Grid 或 StackLayout 中，并在其中应用 `SoftInput`。

3. **混淆 `Default` 与 `None`。** `Default` 意味着“此控件类型的平台默认值” — 在 ScrollView（iOS）上这将启用自动内容内边距。`None` 意味着“完全没有安全区域填充”。

4. **Blazor 混合中的双重填充。** 在页面上设置 `SafeAreaEdges="Container"` **和** 使用 CSS `env(safe-area-inset-*)` 导致双重内边距。选择一种方法 — CSS 推荐用于 Blazor。

5. **Blazor 中缺少 `viewport-fit=cover`。** 没有此 meta 标签，CSS `env(safe-area-inset-*)` 值在 iOS 上始终为零。

6. **假设 .NET 9 在 Android 上的行为。** 升级到 .NET 10 后，Android `ContentPage` 默认为 `None`（以前实际上是 `Container`）。添加 `SafeAreaEdges="Container"` 以恢复之前的行为。

7. **在新代码中使用传统 `ios:Page.UseSafeArea`。** 旧 API 仅适用于 iOS 且已过时。始终使用 `SafeAreaEdges` 进行跨平台安全区域管理。

## 检查清单

- [ ] Android 升级：`SafeAreaEdges="Container"` 添加，如果内容在状态栏下方
- [ ] 边缘到边缘：在页面和布局上**都**设置 `None`
- [ ] ScrollView 键盘避免使用包装 Grid，而不是 ScrollView 自身的 `SafeAreaEdges`
- [ ] Blazor 混合：使用 XAML 或 CSS 安全区域，而不是两者都使用
- [ ] Blazor 的 `index.html` `<meta viewport>` 标签中包含 `viewport-fit=cover`
- [ ] 从传统 `UseSafeArea` / `IgnoreSafeArea` 迁移到 `SafeAreaEdges`
