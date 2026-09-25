# .NET MAUI Shell 导航

使用 Shell 在 .NET MAUI 应用中实现页面导航。Shell 提供基于 URI 的导航、飞出菜单、标签栏，并具有四级视觉层次结构——所有这些都在 XAML 中声明式配置。

## 何时使用

- 使用标签栏或飞出菜单设置顶层应用导航
- 使用 `GoToAsync` 以编程方式在页面之间导航
- 通过查询参数或对象参数在页面之间传递数据
- 注册用于推送导航的详情页面路由
- 使用确认对话框（例如，未保存的更改）保护导航
- 根据页面自定义后退按钮行为

## 何时不使用

- 从外部 URL 或应用链接进行深度链接——请参阅 [.NET MAUI 深度链接文档](https://learn.microsoft.com/dotnet/maui/fundamentals/app-links)
- 在导航目标页面上进行数据绑定——使用 `maui-data-binding`
- 为页面和视图模型进行依赖注入——使用 `maui-dependency-injection`
- 使用 `NavigationPage` 而不使用 Shell 的应用（不同的导航 API）

## 输入

- 具有 `AppShell.xaml` 作为根 Shell 的 .NET MAUI 项目
- 用于导航的页面（`ContentPage`）
- 不在视觉层次结构中的详情页面的路由名称

## 会改变答案的规则

这些是容易出错 Shell 特定决策。在它们与用户询问内容相关时，始终应用它们。

| 情况 | 应该这样做 | 不应该这样做 |
|---|---|---|
| 在 `AppShell.xaml` 中声明页面 | 声明 `xmlns:views="clr-namespace:MyApp.Views"`：`<ShellContent ContentTemplate="{DataTemplate views:MyPage}" />`——页面在第一次导航时创建 | `<ShellContent><views:MyPage /></ShellContent>`，这会在启动时构造**所有**页面 |
| 导航到不在视觉层次结构中的页面 | 首先调用 `Routing.RegisterRoute("details", typeof(DetailsPage))` | 未注册的 `GoToAsync("details")`——它在运行时抛出异常 |
| 接收导航参数 | 在**视图模型**上实现 `IQueryAttributable` | 在页面上实现它，这会分离状态与绑定上下文 |
| 传递整个对象 | `ShellNavigationQueryParameters` | 将对象序列化到查询字符串 |
| 任何 `GoToAsync` 调用 | 使用 `await` 它 | 瞬发并忘记——异常被吞噬且导航竞争 |
| 在后退导航之前确认 | `ShellNavigatingEventArgs.GetDeferral()` … `deferral.Complete()` | 在对话框任务上同步阻塞 |
| 检测后退导航 | 检查 `e.Source == ShellNavigationSource.Pop` | 假设每次导航都是后退操作 |

**不要**为 Shell 应用程序提出 `NavigationPage` / `PushAsync` 解决方案，并且在用户没有要求的情况下不要重新结构一个工作的 `AppShell` 层次结构。

**狭义但完整地回答。** 留在主题内并不意味着要简洁。当你显示导航更改时，请包括运行它所需的组件：`AppShell.xaml` 标记和 `Routing.RegisterRoute` 调用，或 `GoToAsync` 调用和接收 `IQueryAttributable` / `[QueryProperty]` 代码。当两种方法都有效时（查询字符串与 `ShellNavigationQueryParameters`），显示两者并说明何时使用每种方法——用户仍然需要完成的单个代码片段是一个更差的答案。

## Shell 视觉层次结构

Shell 使用四级层次结构。每个级别都包装其下一级别：

```
Shell
 ├── FlyoutItem / TabBar          (顶层分组)
 │    ├── Tab                     (底部标签分组)
 │    │    ├── ShellContent        (页面插槽 → ContentPage)
 │    │    └── ShellContent        (多个 = 顶部标签)
 │    └── Tab
 └── FlyoutItem / TabBar
```

- **FlyoutItem** — 出现在飞出菜单中；包含 `Tab` 子元素
- **TabBar** — 底部标签栏，没有飞出条目
- **Tab** — 分组 `ShellContent`；多个子元素产生顶部标签
- **ShellContent** — 每个指向一个 `ContentPage`

### 隐式转换

你可以省略中间包装器。Shell 自动包装：

| 你编写                    | Shell 创建                         |
|------------------------------|---------------------------------------|
| `ShellContent` 仅          | `FlyoutItem > Tab > ShellContent`     |
| `Tab` 仅                   | `FlyoutItem > Tab`                    |
| `TabBar` 中的 `ShellContent`   | `TabBar > Tab > ShellContent`         |

## 工作流：设置 AppShell

1. 定义继承自 `Shell` 的 `AppShell.xaml`
2. 添加 `FlyoutItem` 或 `TabBar` 元素用于顶层导航
3. 添加 `Tab` 元素用于底部标签；嵌套多个 `ShellContent` 用于顶部标签
4. **始终使用 `ContentTemplate`** 与 `DataTemplate` 以便页面按需加载
5. **为每个 `ShellContent` 指定显式的 `Route`**（见下文）
6. 在 `AppShell` 构造函数中注册详情页面路由

> **为每个 `ShellContent` 设置 `Route=`。** 如果你省略它，MAUI 会使用共享计数器自动生成名称——`Routing.cs` 生成 `D_FAULT_{TypeName}{n}`。具有三个未命名 `ShellContent` 元素的 Shell 会生成类似 `D_FAULT_ShellContent2` 和 `D_FAULT_ShellContent5` 的路由：数字不是连续的，它们取决于首先构建了多少 Shell 元素，当你重新排序或添加页面时它们会变化。你不能编写一个稳定的绝对路由（`//dashboard`）或针对该路由进行深度链接。显式的 `Route="dashboard"` 永远是稳定的。

```xml
<Shell xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
       xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
       xmlns:views="clr-namespace:MyApp.Views"
       x:Class="MyApp.AppShell"
       FlyoutBehavior="Flyout">

    <FlyoutItem Title="动物" Icon="animals.png">
        <Tab Title="猫">
            <ShellContent Title="家养" Route="domesticcats"
                          ContentTemplate="{DataTemplate views:DomesticCatsPage}" />
            <ShellContent Title="野生" Route="wildcats"
                          ContentTemplate="{DataTemplate views:WildCatsPage}" />
        </Tab>
        <Tab Title="狗" Icon="dogs.png">
            <ShellContent Route="dogs" ContentTemplate="{DataTemplate views:DogsPage}" />
        </Tab>
    </FlyoutItem>

    <TabBar>
        <ShellContent Title="首页" Icon="home.png" Route="home"
                      ContentTemplate="{DataTemplate views:HomePage}" />
        <ShellContent Title="设置" Icon="settings.png" Route="settings"
                      ContentTemplate="{DataTemplate views:SettingsPage}" />
    </TabBar>
</Shell>
```

```csharp
// AppShell.xaml.cs
public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
        Routing.RegisterRoute("animaldetails", typeof(AnimalDetailsPage));
        Routing.RegisterRoute("editanimal", typeof(EditAnimalPage));
    }
}
```

## 工作流：使用 GoToAsync 导航

所有程序化导航都使用 `Shell.Current.GoToAsync`。始终 `await` 调用。

### 路由前缀

| 前缀 | 含义                                     |
|--------|---------------------------------------------|
| `//`   | 从 Shell 根的绝对路由                    |
| (无)   | 相对；推送到当前导航栈                   |
| `..`   | 后退一级                               |
| `../`  | 后退然后导航前进                       |

### 导航示例

```csharp
// 1. 绝对——切换到特定层次结构位置
await Shell.Current.GoToAsync("//animals/cats/domestic");

// 2. 相对——推送一个注册的详情页面
await Shell.Current.GoToAsync("animaldetails");

// 3. 带查询字符串参数
await Shell.Current.GoToAsync($"animaldetails?id={animal.Id}");

// 4. 后退一级
await Shell.Current.GoToAsync("..");

// 5. 后退两级
await Shell.Current.GoToAsync("../..");

// 6. 后退一级，然后推送一个不同的页面
await Shell.Current.GoToAsync("../editanimal");
```

## 工作流：在页面之间传递数据

### 选项 1：IQueryAttributable（首选）

在视图模型上实现以在单次调用中接收所有参数：

```csharp
public class AnimalDetailsViewModel : ObservableObject, IQueryAttributable
{
    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        if (query.TryGetValue("id", out var id))
            AnimalId = id.ToString();
    }
}
```

### 选项 2：QueryProperty 属性

应用于**视图模型**类（如果页面确实拥有状态）。优先在视图模型上使用 `IQueryAttributable`——它将导航状态与 `BindingContext` 保持一致，并可以一次性处理多个参数：

```csharp
[QueryProperty(nameof(AnimalId), "id")]
public partial class AnimalDetailsViewModel : ObservableObject
{
    [ObservableProperty]
    private string _animalId = string.Empty;
}
```

Shell 在页面构造函数设置 `BindingContext` 之后应用查询属性，因此属性必须引发变更通知——一个普通的自动属性会使绑定停留在其初始值。

### 选项 3：通过 ShellNavigationQueryParameters 传递复杂对象

无需将对象序列化为字符串即可传递对象：

```csharp
var parameters = new ShellNavigationQueryParameters
{
    { "animal", selectedAnimal }
};
await Shell.Current.GoToAsync("animaldetails", parameters);
```

通过 `IQueryAttributable` 接收：

```csharp
public void ApplyQueryAttributes(IDictionary<string, object> query)
{
    Animal = query["animal"] as Animal;
}
```

## 工作流：保护导航

在 `OnNavigating` 中使用 `GetDeferral()` 进行异步检查（例如，“保存未保存的更改？”）：

```csharp
// 在 AppShell.xaml.cs 中
protected override async void OnNavigating(ShellNavigatingEventArgs args)
{
    base.OnNavigating(args);
    if (hasUnsavedChanges && args.Source == ShellNavigationSource.Pop)
    {
        var deferral = args.GetDeferral();
        bool discard = await ShowConfirmationDialog();
        if (!discard)
            args.Cancel();
        deferral.Complete();
    }
}
```

## 标签配置

### 底部标签

在 `TabBar` 或 `FlyoutItem` 内部的多个 `ShellContent`（或 `Tab`）子元素产生底部标签。

### 顶部标签

在单个 `Tab` 内部的多个 `ShellContent` 子元素产生顶部标签：

```xml
<Tab Title="照片">
    <ShellContent Title="最近的"    ContentTemplate="{DataTemplate views:RecentPage}" />
    <ShellContent Title="收藏的"    ContentTemplate="{DataTemplate views:FavoritesPage}" />
</Tab>
```

### 标签栏外观

| 绑定属性              | 类型    | 目的                        |
|--------------------------------|---------|--------------------------------|
| `Shell.TabBarBackgroundColor`  | `Color` | 标签栏背景             |
| `Shell.TabBarForegroundColor`  | `Color` | 选中的图标颜色            |
| `Shell.TabBarTitleColor`       | `Color` | 选中的标签标题颜色       |
| `Shell.TabBarUnselectedColor`  | `Color` | 未选中的图标/标题      |
| `Shell.TabBarIsVisible`        | `bool`  | 显示/隐藏标签栏          |

```xml
<!-- 在特定页面上隐藏标签栏 -->
<ContentPage Shell.TabBarIsVisible="False" ... />
```

## 飞出配置

### FlyoutBehavior

在 `Shell` 上设置：`Disabled`、`Flyout` 或 `Locked`。

```xml
<Shell FlyoutBehavior="Flyout"> ... </Shell>
```

### FlyoutDisplayOptions

控制子元素在飞出中如何显示：

- `AsSingleItem`（默认）——一个飞出条目用于分组
- `AsMultipleItems` —— 每个子 `Tab` 获得自己的条目

```xml
<FlyoutItem Title="动物" FlyoutDisplayOptions="AsMultipleItems">
    <Tab Title="猫" ... />
    <Tab Title="狗" ... />
</FlyoutItem>
```

### MenuItem（非导航飞出条目）

```xml
<MenuItem Text="注销"
          Command="{Binding LogOutCommand}"
          IconImageSource="logout.png" />
```

## 后退按钮行为

根据页面自定义后退按钮：

```xml
<Shell.BackButtonBehavior>
    <BackButtonBehavior Command="{Binding BackCommand}"
                       IconOverride="back_arrow.png"
                       TextOverride="取消"
                       IsVisible="True" />
</Shell.BackButtonBehavior>
```

属性：`Command`、`CommandParameter`、`IconOverride`、`TextOverride`、`IsVisible`、`IsEnabled`。

## 检查导航状态

```csharp
// 当前 URI 位置
string location = Shell.Current.CurrentState.Location.ToString();

// 当前页面
Page page = Shell.Current.CurrentPage;

// 当前标签的导航栈
IReadOnlyList<Page> stack = Shell.Current.Navigation.NavigationStack;
```

## 导航事件

在 `AppShell` 中重写：

```csharp
protected override void OnNavigated(ShellNavigatedEventArgs args)
{
    base.OnNavigated(args);
    // args.Current, args.Previous, args.Source
}
```

`ShellNavigationSource` 值：`Push`、`Pop`、`PopToRoot`、`Insert`、`Remove`、`ShellItemChanged`、`ShellSectionChanged`、`ShellContentChanged`、`Unknown`。

## 常见陷阱

- **急切页面创建**：使用 `Content` 直接代替 `ContentTemplate` 与 `DataTemplate` 会在 Shell 初始化时创建所有页面，影响启动时间。始终使用 `ContentTemplate`。
- **重复路由名称**：如果 `Routing.RegisterRoute` 的路由名称与现有路由或视觉层次结构路由匹配，则会抛出 `ArgumentException`。应用中的每个路由必须唯一。
- **未注册的相对路由**：除非 `somepage` 使用 `Routing.RegisterRoute` 注册，否则不能 `GoToAsync("somepage")`。视觉层次结构页面使用绝对 `//` 路由。
- **瞬发并忘记的 GoToAsync**：不 `await` `GoToAsync` 会导致竞争条件和静默失败。始终 `await` 调用。
- **错误的绝对路由路径**：绝对路由必须匹配通过视觉层次结构的完整路径（`//FlyoutItem/Tab/ShellContent`）。错误路径会导致静默无操作，而不是异常。
- **直接操作 Tab.Stack**：导航栈是只读的。使用 `GoToAsync` 进行所有导航更改。
- **忘记 `GetDeferral()` 用于异步保护**：在 `OnNavigating` 中的同步取消有效，但异步检查需要 `GetDeferral()` / `deferral.Complete()` 以避免竞争条件。

## 参考

- `references/shell-navigation-api.md` — Shell 层次结构、路由、标签、飞出和导航的完整 API 参考
- [.NET MAUI Shell 导航](https://learn.microsoft.com/dotnet/maui/fundamentals/shell/navigation)
- [.NET MAUI Shell 标签](https://learn.microsoft.com/dotnet/maui/fundamentals/shell/tabs)
- [.NET MAUI Shell 飞出](https://learn.microsoft.com/dotnet/maui/fundamentals/shell/flyout)
- [.NET MAUI Shell 页面](https://learn.microsoft.com/dotnet/maui/fundamentals/shell/pages)
