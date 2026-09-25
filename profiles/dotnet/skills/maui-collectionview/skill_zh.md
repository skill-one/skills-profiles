# CollectionView — .NET MAUI

`CollectionView` 是 .NET MAUI 中用于显示可滚动列表和网格数据的主要控件。它取代了 `ListView`，具有更好的性能、灵活的布局，并且不需要 `ViewCell`。

## 何时使用

- 显示可滚动的数据项列表或网格
- 将对象集合绑定到模板化的项布局
- 添加选择（单选或多选）、分组或下拉刷新
- 实现无限滚动 / 增量加载
- 在列表项上显示滑动操作
- 在没有数据时显示空状态

## 何时不使用

- 静态布局，具有固定数量的项 — 直接使用 `Grid` 或 `StackLayout`
- 地图标记列表 — 使用 `Microsoft.Maui.Controls.Maps` NuGet 包
- 基于表格的数据输入表单 — 使用标准表单控件
- 简单的纯文本列表，没有交互 — 考虑在 `StackLayout` 上的 `BindableLayout`

## 范围控制 — 仅回答所问

这项技能是一个**参考指南**，而不是一个需要应用的清单。大多数请求只需要其中一两个部分。引用其他部分会使答案更差。

**停止条件 — 在以下情况下不要操作：**

- **用户提出了一个狭窄的问题。** 仅回答该问题。不要附加未询问的分组、滑动操作、空视图、快照点或性能提示。
- **用户的现有代码已经可以工作。** 不要重写可以工作的标记以匹配这里的示例。指出具体的缺陷；如果没有，就说没有，并回答所问的问题。
- **更改是风格上的。** 重命名、重新排序属性或重构已经正确行为的模板是重复工作，而不是修复。
- **控件不是 `CollectionView`。** `CarouselView`、`BindableLayout` 和维护中的 `ListView` 有不同的规则。不要重写用户未要求修改的 `ListView` 代码 — 但如果他们询问使用哪个控件，或者从 Xamarin.Forms 迁移，建议使用 `CollectionView`（见 [从 ListView 迁移](#migrating-from-listview)）。
- **问题实际上是绑定、依赖注入或导航问题**，只是恰好涉及列表 — 查询 `maui-data-binding`、`maui-dependency-injection` 或 `maui-shell-navigation`。

**下面的 API 部分是参考，而不是清单 — 仅在相关时提供。** 四条规则是不可协商的，因为违反它们会产生无法工作或无声丢失编译时检查的代码：

1. 在 `CollectionView` 中，**永远不要将 `ViewCell` 作为 `DataTemplate` 的根**。
2. 当列表在首次渲染后发生变化时，使用 `ObservableCollection<T>`。
3. 在 UI 线程上修改绑定的集合。
4. 在每个 `DataTemplate`（以及页面根）上设置 `x:DataType` 以用于编译时绑定。

其他所有内容 — 尺寸策略、快照点、头部/尾部、空视图 — 都是可选的，并且仅在解决用户实际问题时提供。

## 输入

- 数据源（通常是 `ObservableCollection<T>`），绑定到 `ItemsSource`
- 定义每个项如何渲染的 `DataTemplate`
- 可选：布局配置、选择模式、分组模型、空视图

## 基本设置

一个完整的、可复制粘贴的页面。两个承重部分：每个 `x:DataType="models:Item"` 都假设的 `xmlns:models` 声明，以及**根 `x:DataType`** — 没有它外部的 `ItemsSource` 绑定不会编译：

```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:models="clr-namespace:MyApp.Models"
             xmlns:vm="clr-namespace:MyApp.ViewModels"
             x:DataType="vm:ItemsViewModel"
             x:Class="MyApp.ItemsPage">
    <ContentPage.BindingContext>
        <vm:ItemsViewModel />
    </ContentPage.BindingContext>
    <CollectionView ItemsSource="{Binding Items}">
        <CollectionView.ItemTemplate>
            <DataTemplate x:DataType="models:Item">
                <HorizontalStackLayout Padding="8" Spacing="8">
                    <Image Source="{Binding Icon}" WidthRequest="40" HeightRequest="40" />
                    <Label Text="{Binding Name}" VerticalOptions="Center" />
                </HorizontalStackLayout>
            </DataTemplate>
        </CollectionView.ItemTemplate>
    </CollectionView>
</ContentPage>
```

后面的片段只显示 `CollectionView` 元素。当你将片段交给用户时，包括它使用的任何前缀的匹配 `xmlns:` 声明，否则 XAML 将无法编译。

上面的内联 `<ContentPage.BindingContext>` 使示例自包含。在一个使用依赖注入的应用中，注册 ViewModel 并通过构造函数注入分配它（`BindingContext = vm;`） — 见 **maui-dependency-injection** 技能。

**关键规则：**

- 将 `ItemsSource` 绑定到 `ObservableCollection<T>` 以便在添加/删除时更新 UI。
- 每个项模板根必须是 `Layout` 或 `View` — **永远不要使用 `ViewCell`**。
- 始终在 `DataTemplate` 上设置 `x:DataType` 以用于编译时绑定。

## 布局

设置 `ItemsLayout` 以控制排列。默认是 `VerticalList`。

| 布局 | XAML 值 |
|---|---|
| 垂直列表 | `VerticalList`（默认） |
| 水平列表 | `HorizontalList` |
| 垂直网格 | `GridItemsLayout`，`Orientation="Vertical"` |
| 水平网格 | `GridItemsLayout`，`Orientation="Horizontal"` |

### 网格布局

```xml
<CollectionView ItemsSource="{Binding Items}">
    <CollectionView.ItemsLayout>
        <GridItemsLayout Orientation="Vertical"
                         Span="2"
                         VerticalItemSpacing="8"
                         HorizontalItemSpacing="8" />
    </CollectionView.ItemsLayout>
    <CollectionView.ItemTemplate>
        <DataTemplate x:DataType="models:Item">
            <Border Padding="8" StrokeThickness="0">
                <VerticalStackLayout>
                    <Image Source="{Binding Image}" HeightRequest="120" Aspect="AspectFill" />
                    <Label Text="{Binding Name}" FontAttributes="Bold" />
                </VerticalStackLayout>
            </Border>
        </DataTemplate>
    </CollectionView.ItemTemplate>
</CollectionView>
```

### 水平列表

```xml
<CollectionView ItemsSource="{Binding Items}"
                ItemsLayout="HorizontalList" />
```

## 选择

### 选择模式

| 模式 | 绑定属性 | 绑定模式 |
|---|---|---|
| `None` | — | — |
| `Single` | `SelectedItem` | `TwoWay` |
| `Multiple` | `SelectedItems` | `OneWay` |

```xml
<CollectionView ItemsSource="{Binding Items}"
                SelectionMode="Single"
                SelectedItem="{Binding CurrentItem, Mode=TwoWay}"
                SelectionChangedCommand="{Binding ItemSelectedCommand}" />
```

对于 `Multiple` 选择，绑定 `SelectedItems`（类型 `IList<object>`）：

```xml
<CollectionView SelectionMode="Multiple"
                SelectedItems="{Binding ChosenItems, Mode=OneWay}" />
```

### 选中视觉效果

使用 `VisualStateManager` 突出显示选中的项：

```xml
<CollectionView.ItemTemplate>
    <DataTemplate x:DataType="models:Item">
        <Grid Padding="8">
            <VisualStateManager.VisualStateGroups>
                <VisualStateGroup Name="CommonStates">
                    <VisualState Name="Normal">
                        <VisualState.Setters>
                            <Setter Property="BackgroundColor" Value="Transparent" />
                        </VisualState.Setters>
                    </VisualState>
                    <VisualState Name="Selected">
                        <VisualState.Setters>
                            <Setter Property="BackgroundColor"
                                    Value="{AppThemeBinding Light={StaticResource Primary}, Dark={StaticResource PrimaryDark}}" />
                        </VisualState.Setters>
                    </VisualState>
                </VisualStateGroup>
            </VisualStateManager.VisualStateGroups>
            <Label Text="{Binding Name}" />
        </Grid>
    </DataTemplate>
</CollectionView.ItemTemplate>
```

## 分组

1. 创建一个继承自 `List<T>` 的组类：

```csharp
public class AnimalGroup : List<Animal>
{
    public string Name { get; }
    public AnimalGroup(string name, List<Animal> animals) : base(animals)
    {
        Name = name;
    }
}
```

2. 绑定到 `ObservableCollection<AnimalGroup>` 并设置 `IsGrouped="True"`：

```xml
<CollectionView ItemsSource="{Binding AnimalGroups}"
                IsGrouped="True">
    <CollectionView.GroupHeaderTemplate>
        <DataTemplate x:DataType="models:AnimalGroup">
            <Label Text="{Binding Name}"
                   FontAttributes="Bold"
                   BackgroundColor="{StaticResource Gray100}"
                   Padding="8" />
        </DataTemplate>
    </CollectionView.GroupHeaderTemplate>
    <CollectionView.ItemTemplate>
        <DataTemplate x:DataType="models:Animal">
            <Label Text="{Binding Name}" Padding="16,4" />
        </DataTemplate>
    </CollectionView.ItemTemplate>
</CollectionView>
```

## 下拉刷新

将 `CollectionView` 包裹在 `RefreshView` 中。完成时将 `IsRefreshing` 设置回 `false`：

```xml
<RefreshView IsRefreshing="{Binding IsRefreshing}"
             Command="{Binding RefreshCommand}">
    <CollectionView ItemsSource="{Binding Items}" />
</RefreshView>
```

## 增量加载（无限滚动）

```xml
<CollectionView ItemsSource="{Binding Items}"
                RemainingItemsThreshold="5"
                RemainingItemsThresholdReachedCommand="{Binding LoadMoreCommand}" />
```

> ⚠️ **不要与非虚拟化布局一起使用。** `LinearItemsLayout` 和 `GridItemsLayout` 支持虚拟化。作为 `CollectionView` 的替代方案，在 `StackLayout` 上使用 `BindableLayout` 没有虚拟化，这会触发无限阈值达到事件。

## SwipeView — 从 DataTemplate 内部绑定

`DataTemplate` 内部的命令不能直接到达你的 ViewModel。使用 `RelativeSource AncestorType`：

```xml
<CollectionView.ItemTemplate>
    <DataTemplate x:DataType="models:Item">
        <SwipeView>
            <SwipeView.RightItems>
                <SwipeItems>
                    <SwipeItem Text="Delete"
                               BackgroundColor="Red"
                               Command="{Binding BindingContext.DeleteCommand, Source={RelativeSource AncestorType={x:Type ContentPage}}}"
                               CommandParameter="{Binding}" />
                </SwipeItems>
            </SwipeView.RightItems>
            <Grid Padding="8">
                <Label Text="{Binding Name}" />
            </Grid>
        </SwipeView>
    </DataTemplate>
</CollectionView.ItemTemplate>
```

## 空视图

当 `ItemsSource` 为空或为 null 时显示。

```xml
<CollectionView ItemsSource="{Binding SearchResults}"
                EmptyView="No items found." />
```

对于自定义空视图，包裹在 `ContentView` 中：

```xml
<CollectionView ItemsSource="{Binding SearchResults}">
    <CollectionView.EmptyView>
        <ContentView>
            <VerticalStackLayout HorizontalOptions="Center" VerticalOptions="Center">
                <Image Source="empty_state.png" WidthRequest="120" />
                <Label Text="Nothing here yet" HorizontalTextAlignment="Center" />
            </VerticalStackLayout>
        </ContentView>
    </CollectionView.EmptyView>
</CollectionView>
```

## 头部和尾部

```xml
<CollectionView ItemsSource="{Binding Items}">
    <CollectionView.Header>
        <Label Text="Header" FontAttributes="Bold" Padding="8" />
    </CollectionView.Header>
    <CollectionView.Footer>
        <Label Text="Footer" FontAttributes="Italic" Padding="8" />
    </CollectionView.Footer>
</CollectionView>
```

当头部或尾部是数据绑定时，使用 `HeaderTemplate` / `FooterTemplate`。

## 滚动

### ScrollTo

通过索引或项编程方式滚动：

```csharp
// 滚动到索引
collectionView.ScrollTo(index: 10, position: ScrollToPosition.Center, animate: true);

// 滚动到项
collectionView.ScrollTo(item: myItem, position: ScrollToPosition.MakeVisible, animate: true);
```

| ScrollToPosition | 行为 |
|---|---|
| `MakeVisible` | 滚动足够的距离使项可见 |
| `Start` | 将项滚动到视口的开始 |
| `Center` | 将项滚动到视口的中心 |
| `End` | 将项滚动到视口的末尾 |

### 快照点

```xml
<CollectionView.ItemsLayout>
    <LinearItemsLayout Orientation="Horizontal"
                       SnapPointsType="MandatorySingle"
                       SnapPointsAlignment="Center" />
</CollectionView.ItemsLayout>
```

- `SnapPointsType`: `None`，`Mandatory`，`MandatorySingle`
- `SnapPointsAlignment`: `Start`，`Center`，`End`

## 从 ListView 迁移

`ListView` 仍然可以编译，但**自 .NET 10 起**它被标记为 `[Obsolete]`（"*ListView 已弃用。请使用 CollectionView 代替。*"）。它在 .NET 9 及更早版本上**不是**弃用的，因此在使用目标框架之前，不要将其描述为弃用。**如果用户询问使用哪个控件，或者从 Xamarin.Forms 迁移，建议使用 `CollectionView`** — 它更快，不需要 `ViewCell`，并支持灵活的布局。要避免的是无声地重写用户未要求你修改的 `ListView` 代码。

| `ListView` | `CollectionView` 等效 |
|---|---|
| `ViewCell` 模板根 | 任何 `View`/`Layout` 根 — **`ViewCell` 不受支持** |
| `ItemSelected` 事件 | `SelectionChanged` 事件，或 `SelectionChangedCommand` |
| `ItemTapped` 事件 | 在项模板中有一个 `TapGestureRecognizer` — `SelectionChanged` 仅在选中*变化*时触发，因此它不会重新触发已选中项的点击 |
| `IsPullToRefreshEnabled` + `Refreshing` | 将 `CollectionView` 包裹在 `RefreshView` 中 |
| `IsGroupingEnabled` | `IsGrouped` |
| `HasUnevenRows="True"` | 默认 `ItemSizingStrategy="MeasureAllItems"` |
| `RowHeight`（固定高度） | 在项模板中设置高度。`MeasureFirstItem` 仅重用第一个项的测量大小 — 它不是一个显式的行高 |
| `SeparatorVisibility` / `SeparatorColor` | **没有等效项** — 在项模板中自己绘制 `BoxView`/`Border` |

缺少分隔符 API 是最常见的迁移意外：`CollectionView` 没有内置的分隔符，因此自己向模板中添加一个。

## 性能提示

仅在用户报告性能问题或明确询问性能时应用这些提示 — 它们不是默认的清单。

- **使用 `MeasureFirstItem`** 用于均匀的项尺寸 — 比默认的 `MeasureAllItems`（单独测量每个项）快得多。在 `CollectionView` 上设置它（它是在 `StructuredItemsView` 上声明的），**而不是**在 `LinearItemsLayout` / `GridItemsLayout` 上：
  ```xml
  <CollectionView ItemsSource="{Binding Items}"
                  ItemSizingStrategy="MeasureFirstItem">
      <CollectionView.ItemTemplate>
          <DataTemplate x:DataType="models:Item">
              <Grid Padding="8" ColumnDefinitions="44,*" ColumnSpacing="8">
                  <Image WidthRequest="44" HeightRequest="44" />
                  <Label Grid.Column="1" Text="{Binding Name}" VerticalOptions="Center" />
              </Grid>
          </DataTemplate>
      </CollectionView.ItemTemplate>
  </CollectionView>
  ```
  **当 `MeasureFirstItem` 是错误选择时** — 如果项高度不同（换行文本、可选行、不同纵横比的图像） — 第一个项的大小将应用于所有项，因此其余项会被裁剪或拉伸。
  - `DataTemplateSelector` 返回不同的模板 — 第一个项不会代表其他项。
  - 第一个项是非典型的（一个像头部或“精选”的行） — 每个项都会继承其大小。通过重新排序数据来修复此问题是一种迹象；使用 `MeasureAllItems` 代替。
  - 第一个项的大小取决于在测量第一个项时尚未加载的运行时数据。

- **当列表在首次渲染后发生变化时，使用 `ObservableCollection<T>`。** 它实现了 `INotifyCollectionChanged`，因此就地 `Add`/`Remove`/`Insert` 会增量更新 UI。`List<T>` 对于绑定后永远不会改变的列表是合适的。请注意，*替换* `ItemsSource` 无论集合类型如何都会重新渲染所有内容 — 因此在原地修改绑定的集合，而不是重新分配它。
- **在 UI 线程上更新集合** — `MainThread.BeginInvokeOnMainThread(() => Items.Add(item))`。

## 常见陷阱

| 问题 | 修复 |
|---|---|
| UI 在项更改时不更新 | 使用 `ObservableCollection<T>`，而不是 `List<T>`。 |
| 应用程序崩溃或空白项 | **永远不要使用 `ViewCell`** — 使用 `Grid`、`StackLayout` 或任何 `View` 作为模板根。 |
| 项消失或布局中断 | 始终在 UI 线程上更新 `ItemsSource` 和集合（`MainThread.BeginInvokeOnMainThread`）。 |
| 增量加载无限触发 | 不要使用 `StackLayout` 作为布局；使用 `LinearItemsLayout` 或 `GridItemsLayout`。 |
| 空视图渲染不正确 | 将自定义空视图包裹在 `ContentView` 中。 |
| 滚动性能差 | 使用 `MeasureFirstItem` 尺寸策略用于均匀的项尺寸。 |
| `ItemSizingStrategy` 无法编译 | 它是在 `StructuredItemsView` 上声明的 — 在 `<CollectionView>` 上设置它，而不是在 `<LinearItemsLayout>` / `<GridItemsLayout>` 上。 |
| 项被裁剪或拉伸 | `MeasureFirstItem` 假设均匀的项尺寸。对于可变高度的项，使用默认的 `MeasureAllItems`。 |
| 选中状态不可见 | 在项模板根元素中添加 `VisualState Name="Selected"`。 |
| SwipeView 命令中的绑定错误 | 使用 `RelativeSource AncestorType` 从项模板内部到达 ViewModel。 |

## 验证

在返回你编写或编辑的 `CollectionView` 标记之前，确认：

- [ ] `DataTemplate` 根是 `View`/`Layout` — **不是** `ViewCell`。
- [ ] `DataTemplate` 声明 `x:DataType` 以用于编译时绑定。
- [ ] `ItemsSource` 绑定到 `ObservableCollection<T>` 如果列表会变化。
- [ ] `ItemSizingStrategy`（如果使用）是在 `<CollectionView>` 上，而不是在布局上。
- [ ] `Multiple` 选择绑定 `SelectedItems`；`Single` 绑定 `SelectedItem`（`TwoWay`）。
- [ ] `RefreshView.IsRefreshing` 在刷新完成时设置回 `false`。
- [ ] 答案仅涵盖用户所问 — 没有未请求的部分。

## 参考

- [CollectionView 概述](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/)
- [CollectionView 布局](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/layout)
- [CollectionView 选择](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/selection)
- [CollectionView 分组](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/grouping)
- [CollectionView 滚动](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/scrolling)
- [CollectionView EmptyView](https://learn.microsoft.com/dotnet/maui/user-interface/controls/collectionview/emptyview)
