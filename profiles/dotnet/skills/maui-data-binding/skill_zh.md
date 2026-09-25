# .NET MAUI 数据绑定

使用编译时安全性、正确的变更通知和最小的开销将 UI 控件与 ViewModel 属性连接起来。在所有地方优先使用编译绑定，并将绑定警告视为构建错误。

## 使用场景

- 为新页面或现有页面添加 `x:DataType` 编译绑定
- 实现 `INotifyPropertyChanged` 或 CommunityToolkit 的 `ObservableObject`
- 创建或使用 `IValueConverter` / `IMultiValueConverter`
- 为控件属性选择正确的 `BindingMode`
- 在 XAML 或代码隐藏中设置 `BindingContext`
- 使用相对绑定（`Self`、`AncestorType`、`TemplatedParent`）
- 应用 `StringFormat`、`FallbackValue` 或 `TargetNullValue`
- 使用 `SetBinding` 和 lambda 表达式（.NET 9+）编写 AOT 安全的代码绑定

## 不使用场景

- **CollectionView 布局/模板** — 使用 `maui-collectionview` 技能
- **Shell 导航参数** — 使用 `maui-shell-navigation` 技能
- **服务注册/DI** — 使用 `maui-dependency-injection` 技能
- **属性变更触发的动画** — 使用内置的 [.NET MAUI 动画 API](https://learn.microsoft.com/dotnet/maui/user-interface/animation/basic)

## 输入

- 目标为 .NET 8 或更高版本的 .NET MAUI 项目
- 声明绑定的 XAML 页面或 C# 代码隐藏
- ViewModel 类（或计划创建一个）

## 影响答案的规则

将这些应用于每个绑定答案 — 它们是“它编译了”和“它实际更新了 UI”之间的区别。

| 情况 | 执行 | 不执行 |
|---|---|---|
| 决定 `x:DataType` 的位置 | 放在绑定作用域开始的地方 — 页面/视图根，以及**每个** `DataTemplate` | 在任意子元素上分散它，这些子元素共享父元素的 `BindingContext` |
| 绑定回退到反射（XC0022 / XC0023） | 为该绑定作用域添加正确的 `x:DataType`；对于 XC0023 移除显式的 `x:DataType="{x:Null}"` | 使用 `x:DataType="x:Object"` 来抑制它 — 这会禁用编译时检查 |
| `DataTemplate` 继承外层作用域的 `x:DataType`（XC0024） | 给 `DataTemplate` 它**自己的** `x:DataType` | 留下它以匹配错误类型 |
| ViewModel 变更通知 | `ObservableObject` + `[ObservableProperty]`，或实现 `INotifyPropertyChanged` | 一个普通的 POCO 基类 — 绑定将永远不会更新 |
| 绑定显示为空白 | 检查 `BindingContext` 是否实际设置 | 假设绑定路径错误 |
| 强制编译绑定 | 将 `MauiEnableXamlCBindingWithSourceCompilation` 设置为 `true`，**然后** `<WarningsAsErrors>XC0022;XC0025</WarningsAsErrors>` | 如果项目使用 `Source=` / `RelativeSource` 绑定，则不使用开关来提升 `XC0025` |

**不要**重新结构 ViewModel 或添加用户未请求且未解决实际缺陷的转换器。添加 `x:DataType` 不同：当你已经在编辑页面的绑定时，推荐编译绑定是在范围内的。

---

## 编译绑定 — x:DataType 位置

编译绑定比基于反射的绑定快 **8–20 倍**，并且是 NativeAOT / 修剪所必需的。使用 `x:DataType` 来启用它们。

### 位置规则

只在设置 `BindingContext` 的地方设置 `x:DataType`：

1. **页面 / 视图根** — 你分配 `BindingContext` 的地方。
2. **DataTemplate** — 创建新的绑定作用域。

不要在任意子元素上分散 `x:DataType`。在子元素上添加 `x:DataType="x:Object"` 以逃避编译绑定是一个反模式 — 它禁用编译时检查并重新引入反射。

```xml
<!-- ✅ 正确：页面根处的 x:DataType -->
<ContentPage xmlns:vm="clr-namespace:MyApp.ViewModels"
             x:DataType="vm:MainViewModel">
    <StackLayout>
        <Label Text="{Binding Title}" />
        <Slider Value="{Binding Progress}" />
    </StackLayout>
</ContentPage>

<!-- ❌ 错误：子元素上分散 x:DataType -->
<ContentPage x:DataType="vm:MainViewModel">
    <StackLayout>
        <Label Text="{Binding Title}" />
        <Slider x:DataType="x:Object" Value="{Binding Progress}" />
    </StackLayout>
</ContentPage>
```

### DataTemplate 总是需要它自己的 x:DataType

```xml
<CollectionView ItemsSource="{Binding People}">
    <CollectionView.ItemTemplate>
        <DataTemplate x:DataType="model:Person">
            <Label Text="{Binding FullName}" />
        </DataTemplate>
    </CollectionView.ItemTemplate>
</CollectionView>
```

### 强制绑定警告作为错误

| 警告 | 含义 |
|---------|---------|
| **XC0022** | 绑定在作用域中**未使用 `x:DataType`** — 未编译，回退到反射 |
| **XC0023** | 由于 `x:DataType` 显式为 **`null`**，绑定未编译 |
| **XC0024** | `x:DataType` 来自**外层作用域** — 为 `DataTemplate` 添加它自己的 `x:DataType` |
| **XC0025** | 绑定未编译，因为它有显式的**`Source`** — 启用 `<MauiEnableXamlCBindingWithSourceCompilation>` |

> 这四个代码针对 .NET 10 / .NET 11 MAUI **进行了验证**
> (`Build.Tasks/BuildException.cs`, `ErrorMessages.resx`)。诊断编号对 SDK 带敏感 — 在依赖它之前，请针对 `BuildException.cs` 重新检查较新的 SDK。

添加到 `.csproj`：

```xml
<!-- 编译使用 Source= 的绑定；否则在每次
     Source= / RelativeSource 绑定上触发 XC0025。截至 .NET 10/11，
     这仅在 AOT / 完全修剪构建中默认启用。 -->
<MauiEnableXamlCBindingWithSourceCompilation>true</MauiEnableXamlCBindingWithSourceCompilation>
<WarningsAsErrors>XC0022;XC0025</WarningsAsErrors>
```

如果你在不启用该开关的情况下提升 `XC0025`，请确保项目没有 `Source=` / `RelativeSource` 绑定 — 否则它们将被报告。

---

## 绑定模式

仅在覆盖默认值时显式设置 `Mode`。大多数属性已经有了正确的默认值：

| 模式 | 方向 | 用例 |
|------|-----------|----------|
| `OneWay` | 源 → 目标 | 仅显示（大多数属性的默认值） |
| `TwoWay` | 源 ↔ 目标 | 可编辑控件（`Entry.Text`、`Switch.IsToggled`） |
| `OneWayToSource` | 目标 → 源 | 读取用户输入而不推回 UI |
| `OneTime` | 源 → 目标（一次） | 静态值；无变更跟踪开销 |

```xml
<!-- ✅ 默认值 — 省略 Mode -->
<Label Text="{Binding Score}" />
<Entry Text="{Binding UserName}" />
<Switch IsToggled="{Binding DarkMode}" />

<!-- ✅ 仅在需要时覆盖 -->
<Label Text="{Binding Title, Mode=OneTime}" />
<Entry Text="{Binding SearchQuery, Mode=OneWayToSource}" />

<!-- ❌ 冗余 — 添加噪声 -->
<Label Text="{Binding Score, Mode=OneWay}" />
<Entry Text="{Binding UserName, Mode=TwoWay}" />
```

---

## BindingContext 和属性路径

每个 `BindableObject` 从其父级继承 `BindingContext`，除非显式设置。属性路径支持点表示法和索引器：

```xml
<Label Text="{Binding Address.City}" />
<Label Text="{Binding Items[0].Name}" />
```

在 XAML 中设置 `BindingContext`：

```xml
<ContentPage xmlns:vm="clr-namespace:MyApp.ViewModels"
             x:DataType="vm:MainViewModel">
    <ContentPage.BindingContext>
        <vm:MainViewModel />
    </ContentPage.BindingContext>
</ContentPage>
```

或在代码隐藏中（使用 DI 更受推荐）：

```csharp
public MainPage(MainViewModel vm)
{
    InitializeComponent();
    BindingContext = vm;
}
```

---

## INotifyPropertyChanged 和 ObservableObject

### 手动实现

```csharp
public class MainViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    private string _title = string.Empty;
    public string Title
    {
        get => _title;
        set
        {
            if (_title != value)
            {
                _title = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Title)));
            }
        }
    }
}
```

### CommunityToolkit.Mvvm（推荐）

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private string _title = string.Empty;

    [RelayCommand]
    private async Task LoadDataAsync() { /* ... */ }
}
```

源生成器自动创建 `Title` 属性、`PropertyChanged` 抛出和 `LoadDataCommand`。

---

## 值转换器 — IValueConverter

实现 `Convert`（源 → 目标）和 `ConvertBack`（目标 → 源）：

```csharp
public class IntToBoolConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType,
        object? parameter, CultureInfo culture)
        => value is int i && i != 0;

    public object? ConvertBack(object? value, Type targetType,
        object? parameter, CultureInfo culture)
        => value is true ? 1 : 0;
}
```

在 XAML 资源中声明并使用：

```xml
<ContentPage.Resources>
    <local:IntToBoolConverter x:Key="IntToBool" />
</ContentPage.Resources>

<Switch IsToggled="{Binding Count, Converter={StaticResource IntToBool}}" />
```

`ConverterParameter` 始终作为**字符串**传递 — 在 `Convert` 中解析：

```xml
<Label Text="{Binding Score, Converter={StaticResource ThresholdConverter},
              ConverterParameter=50}" />
```

---

## 多绑定

使用 `IMultiValueConverter` 组合多个源值：

```xml
<Label>
    <Label.Text>
        <MultiBinding Converter="{StaticResource FullNameConverter}">
            <Binding Path="FirstName" />
            <Binding Path="LastName" />
        </MultiBinding>
    </Label.Text>
</Label>
```

```csharp
public class FullNameConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType,
        object parameter, CultureInfo culture)
    {
        if (values.Length == 2 && values[0] is string first
            && values[1] is string last)
            return $"{first} {last}";
        return string.Empty;
    }

    public object[] ConvertBack(object value, Type[] targetTypes,
        object parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

---

## 相对绑定

| 源 | 语法 | 用例 |
|--------|--------|----------|
| Self | `{Binding Source={RelativeSource Self}, Path=WidthRequest}` | 绑定到自己的属性 |
| Ancestor | `{Binding BindingContext.Title, Source={RelativeSource AncestorType={x:Type ContentPage}}}` | 访问父级 `BindingContext` |
| TemplatedParent | `{Binding Source={RelativeSource TemplatedParent}, Path=Padding}` | 在 ControlTemplate 中 |

```xml
<!-- 正方形框：高度 = 宽度 -->
<BoxView WidthRequest="100"
         HeightRequest="{Binding Source={RelativeSource Self}, Path=WidthRequest}" />
```

---

## StringFormat

使用 `Binding.StringFormat` 进行简单的显示格式化，而无需转换器：

```xml
<Label Text="{Binding Price, StringFormat='Total: {0:C2}'}" />
<Label Text="{Binding DueDate, StringFormat='{0:MMM dd, yyyy}'}" />
```

当格式字符串包含逗号或大括号时，用单引号括起来。

---

## 绑定回退

- **FallbackValue** — 在绑定路径无法解析或转换器抛出时使用。
- **TargetNullValue** — 在绑定值为 `null` 时使用。

```xml
<Label Text="{Binding MiddleName, TargetNullValue='(none)',
              FallbackValue='unavailable'}" />
<Image Source="{Binding AvatarUrl, TargetNullValue='default_avatar.png'}" />
```

---

## .NET 9+ 代码绑定（AOT 安全）

完全 AOT 安全，无反射：

```csharp
label.SetBinding(Label.TextProperty,
    static (PersonViewModel vm) => vm.FullName);

entry.SetBinding(Entry.TextProperty,
    static (PersonViewModel vm) => vm.Age,
    mode: BindingMode.TwoWay,
    converter: new IntToStringConverter());
```

---

## 线程

MAUI 自动将 `PropertyChanged` 托管到 UI 线程 — 你可以从任何线程触发它。**但是**，从后台线程直接修改 `ObservableCollection`（Add / Remove）可能会导致崩溃：

```csharp
// ✅ 安全 — PropertyChanged 自动托管
await Task.Run(() => Title = "Loaded");

// ⚠️ ObservableCollection.Add — 分发到 UI 线程
MainThread.BeginInvokeOnMainThread(() => Items.Add(newItem));
```

---

## 常见陷阱

| 错误 | 修复 |
|---------|-----|
| 缺少 `x:DataType` — 绑定静默回退到反射 | 在页面根和每个 `DataTemplate` 中添加 `x:DataType`；提升 `XC0022`（见 [强制绑定警告作为错误](#enforce-binding-warnings-as-errors)） |
| 忘记设置 `BindingContext` | 在 XAML 中设置 (`<Page.BindingContext>`) 或通过构造函数注入 |
| 指定冗余的 `Mode=OneWay` / `Mode=TwoWay` | 使用控件默认值时省略 `Mode` |
| ViewModel 未实现 `INotifyPropertyChanged` | 使用 CommunityToolkit.Mvvm 的 `ObservableObject` 或手动实现 |
| 在 UI 线程之外修改 `ObservableCollection` | 将突变包装在 `MainThread.BeginInvokeOnMainThread` 中 |
| 热路径中的复杂转换器链 | 在 ViewModel 中预先计算值 |
| 使用 `x:DataType="x:Object"` 来逃避编译绑定 | 重新结构绑定；保持编译时安全性 |
| 绑定到非公共属性 | 绑定目标必须是 `public` 属性（字段被忽略） |

---

## 参考

- [数据绑定概述](https://learn.microsoft.com/dotnet/maui/fundamentals/data-binding/)
- [编译绑定](https://learn.microsoft.com/dotnet/maui/fundamentals/data-binding/compiled-bindings)
- [值转换器](https://learn.microsoft.com/dotnet/maui/fundamentals/data-binding/converters)
- [相对绑定](https://learn.microsoft.com/dotnet/maui/fundamentals/data-binding/relative-bindings)
- [多绑定](https://learn.microsoft.com/dotnet/maui/fundamentals/data-binding/multibindings)
- [CommunityToolkit.Mvvm](https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/)
