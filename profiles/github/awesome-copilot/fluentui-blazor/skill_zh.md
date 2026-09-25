# Fluent UI Blazor — 消费者使用指南

本技能教你如何在 Blazor 应用程序中正确使用 **Microsoft.FluentUI.AspNetCore.Components**（版本 4）NuGet 包。

## 关键规则

### 1. 无需手动添加 `<script>` 或 `<link>` 标签

库通过 Blazor 的静态 Web 资产和 JS 初始化器自动加载所有 CSS 和 JS。**绝对不要让用户添加 `<script>` 或 `<link>` 标签来加载核心库。**

### 2. 基于服务的组件必须使用提供者

这些提供者组件**必须**添加到根布局（例如 `MainLayout.razor`）中，以便其对应的服务能够工作。如果没有它们，服务调用会**静默失败**（无错误，无 UI）。

```razor
<FluentToastProvider />
<FluentDialogProvider />
<FluentMessageBarProvider />
<FluentTooltipProvider />
<FluentKeyCodeProvider />
```

### 3. 在 Program.cs 中注册服务

```csharp
builder.Services.AddFluentUIComponents();

// 或使用配置：
builder.Services.AddFluentUIComponents(options =>
{
    options.UseTooltipServiceProvider = true;  // 默认：true
    options.ServiceLifetime = ServiceLifetime.Scoped; // 默认
});
```

**ServiceLifetime 规则：**
- `ServiceLifetime.Scoped` — 用于 Blazor Server / 交互式（默认）
- `ServiceLifetime.Singleton` — 用于 Blazor WebAssembly 独立应用
- `ServiceLifetime.Transient` — **会抛出 `NotSupportedException`**

### 4. 图标需要单独的 NuGet 包

```
dotnet add package Microsoft.FluentUI.AspNetCore.Components.Icons
```

使用 `@using` 别名进行操作：

```razor
@using Icons = Microsoft.FluentUI.AspNetCore.Components.Icons

<FluentIcon Value="@(Icons.Regular.Size24.Save)" />
<FluentIcon Value="@(Icons.Filled.Size20.Delete)" Color="@Color.Error" />
```

模式：`Icons.[变体].[大小].[名称]`
- 变体：`Regular`, `Filled`
- 大小：`Size12`, `Size16`, `Size20`, `Size24`, `Size28`, `Size32`, `Size48`

自定义图片：`Icon.FromImageUrl("/path/to/image.png")`

**绝对不要使用基于字符串的图标名称** — 图标是强类型类。

### 5. 列表组件绑定模型

`FluentSelect<TOption>`, `FluentCombobox<TOption>`, `FluentListbox<TOption>`, 和 `FluentAutocomplete<TOption>` 不像 `<InputSelect>` 那样工作。它们使用：

- `Items` — 数据源 (`IEnumerable<TOption>`)
- `OptionText` — `Func<TOption, string?>` 用于提取显示文本
- `OptionValue` — `Func<TOption, string?>` 用于提取值字符串
- `SelectedOption` / `SelectedOptionChanged` — 用于单选绑定
- `SelectedOptions` / `SelectedOptionsChanged` — 用于多选绑定

```razor
<FluentSelect Items="@countries"
              OptionText="@(c => c.Name)"
              OptionValue="@(c => c.Code)"
              @bind-SelectedOption="@selectedCountry"
              Label="国家" />
```

**不**像这样（错误模式）：
```razor
@* 错误 — 不要使用 InputSelect 模式 *@
<FluentSelect @bind-Value="@selectedValue">
    <option value="1">一个</option>
</FluentSelect>
```

### 6. FluentAutocomplete 特殊说明

- 使用 `ValueText`（不是 `Value` — 已过时）作为搜索输入文本
- `OnOptionsSearch` 是过滤选项的必需回调
- 默认为 `Multiple="true"`

```razor
<FluentAutocomplete TOption="Person"
                    OnOptionsSearch="@OnSearch"
                    OptionText="@(p => p.FullName)"
                    @bind-SelectedOptions="@selectedPeople"
                    Label="搜索人员" />

@code {
    private void OnSearch(OptionsSearchEventArgs<Person> args)
    {
        args.Items = allPeople.Where(p =>
            p.FullName.Contains(args.Text, StringComparison.OrdinalIgnoreCase));
    }
}
```

### 7. 对话框服务模式

**不要切换 `<FluentDialog>` 标签的可见性。** 服务模式是：

1. 创建一个实现 `IDialogContentComponent<TData>` 的内容组件：

```csharp
public partial class EditPersonDialog : IDialogContentComponent<Person>
{
    [Parameter] public Person Content { get; set; } = default!;

    [CascadingParameter] public FluentDialog Dialog { get; set; } = default!;

    private async Task SaveAsync()
    {
        await Dialog.CloseAsync(Content);
    }

    private async Task CancelAsync()
    {
        await Dialog.CancelAsync();
    }
}
```

2. 通过 `IDialogService` 显示对话框：

```csharp
[Inject] private IDialogService DialogService { get; set; } = default!;

private async Task ShowEditDialog()
{
    var dialog = await DialogService.ShowDialogAsync<EditPersonDialog, Person>(
        person,
        new DialogParameters
        {
            Title = "编辑人员",
            PrimaryAction = "保存",
            SecondaryAction = "取消",
            Width = "500px",
            PreventDismissOnOverlayClick = true,
        });

    var result = await dialog.Result;
    if (!result.Cancelled)
    {
        var updatedPerson = result.Data as Person;
    }
}
```

对于方便使用的对话框：
```csharp
await DialogService.ShowConfirmationAsync("你确定吗？", "是", "否");
await DialogService.ShowSuccessAsync("完成！");
await DialogService.ShowErrorAsync("出错了。");
```

### 8. Toast 通知

```csharp
[Inject] private IToastService ToastService { get; set; } = default!;

ToastService.ShowSuccess("项目保存成功");
ToastService.ShowError("保存失败");
ToastService.ShowWarning("检查你的输入");
ToastService.ShowInfo("有新更新可用");
```

`FluentToastProvider` 参数：`Position`（默认 `TopRight`），`Timeout`（默认 7000ms），`MaxToastCount`（默认 4）。

### 9. 设计令牌和主题在渲染后才能生效

设计令牌依赖于 JS 互操作。**不要在 `OnInitialized` 中设置它们** — 使用 `OnAfterRenderAsync`。

```razor
<FluentDesignTheme Mode="DesignThemeModes.System"
                   OfficeColor="OfficeColor.Teams"
                   StorageName="mytheme" />
```

### 10. FluentEditForm 与 EditForm

`FluentEditForm` 仅在 `FluentWizard` 步骤中（每步验证）需要。对于普通表单，使用标准的 `EditForm` 并搭配 Fluent 表单组件：

```razor
<EditForm Model="@model" OnValidSubmit="HandleSubmit">
    <DataAnnotationsValidator />
    <FluentTextField @bind-Value="@model.Name" Label="名称" Required />
    <FluentSelect Items="@options"
                  OptionText="@(o => o.Label)"
                  @bind-SelectedOption="@model.Category"
                  Label="类别" />
    <FluentValidationSummary />
    <FluentButton Type="ButtonType.Submit" Appearance="Appearance.Accent">保存</FluentButton>
</EditForm>
```

使用 `FluentValidationMessage` 和 `FluentValidationSummary` 而不是标准的 Blazor 验证组件，以实现 Fluent 样式。

## 参考文件

有关特定主题的详细指南，请参阅：

- [设置和配置](references/SETUP.md)
- [布局和导航](references/LAYOUT-AND-NAVIGATION.md)
- [数据网格](references/DATAGRID.md)
- [主题化](references/THEMING.md)
