# 收集用户输入

## 第 1 步 — 读取项目的 AGENTS.md

检查 `AGENTS.md` 文件中的 **交互模式** 和 **交互范围**。这决定了适用哪些表单模式：

| 模式 | 表单机制 |
|------|---------------|
| 无（静态 SSR） | `EditForm` 配合 `FormName` + `[SupplyParameterFromForm]`。不需要 `@bind`，不需要 `@onchange`。 |
| 服务器 | `EditForm` 配合 `@bind-Value`。完全交互——实时验证，动态 UI。 |
| WebAssembly | 与服务器模式相同，但需要服务器数据的验证器必须调用 API。 |
| 自动 | 与 WebAssembly 模式相同——代码必须在浏览器和服务器中都能工作。 |

| 范围 | 影响 |
|-------|--------|
| 全局 | 所有表单都是交互式的。只有在显式选择页面为静态 SSR 时才需要 `FormName`。 |
| 每页 | 静态页面中的表单使用 `FormName` + `[SupplyParameterFromForm]`。`@rendermode` 页面中的表单使用 `@bind-Value`。 |

## EditForm 设置

`EditForm` 需要 **要么** `Model`，要么 `EditContext` —— 永远不能同时使用。

### 基于模型（默认）

```razor
<EditForm Model="Employee" OnValidSubmit="HandleSubmit" FormName="employee">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <label>
        名称： <InputText @bind-Value="Employee!.Name" />
        <ValidationMessage For="() => Employee!.Name" />
    </label>

    <button type="submit">保存</button>
</EditForm>

@code {
    [SupplyParameterFromForm]
    private EmployeeModel? Employee { get; set; }

    protected override void OnInitialized() => Employee ??= new();

    private async Task HandleSubmit()
    {
        // 保存 Employee
    }
}
```

这种单一模式适用于 **两种** SSR 和交互模式：
- 在 SSR 中：`FormName` 识别表单，`[SupplyParameterFromForm]` 绑定 POST 数据，`??=` 在 GET 时初始化。
- 在交互中：`@bind-Value` 提供双向绑定，`[SupplyParameterFromForm]` 被忽略，`FormName` 无害。

### 基于 EditContext（高级）

当你需要程序化字段跟踪、动态验证规则或手动 `EditContext.Validate()` 调用时使用：

```csharp
private EditContext? editContext;
private EmployeeModel model = new();

protected override void OnInitialized()
{
    editContext = new EditContext(model);
}
```

```razor
<EditForm EditContext="editContext" OnValidSubmit="HandleSubmit" FormName="employee">
```

## 提交处理程序

| 处理程序 | 触发条件 | 使用场景 |
|---------|-----------|----------|
| `OnValidSubmit` | 验证通过 | 标准 `DataAnnotationsValidator` 表单 |
| `OnInvalidSubmit` | 验证失败 | 需要对无效状态进行自定义处理 |
| `OnSubmit` | 总是——验证是手动 | 自己使用 `EditContext.Validate()` |

`OnSubmit` 不能与 `OnValidSubmit`/`OnInvalidSubmit` 结合使用。

## 内置输入组件

| 组件 | 绑定到 | 备注 |
|-----------|----------|-------|
| `InputText` | `string` | 渲染 `<input type="text">` |
| `InputTextArea` | `string` | 渲染 `<textarea>` |
| `InputNumber<T>` | `int`，`double`，`decimal` | 渲染 `<input type="number">` |
| `InputDate<T>` | `DateTime`，`DateOnly`，`DateTimeOffset` | 渲染 `<input type="date">` |
| `InputCheckbox` | `bool` | 渲染 `<input type="checkbox">` |
| `InputSelect<T>` | `string`，枚举，数值类型 | 渲染 `<select>` |
| `InputRadioGroup<T>` | `string`，枚举，数值类型 | 包装 `InputRadio<T>` 子元素 |
| `InputFile` | `IBrowserFile` | 文件上传——仅限交互模式 |

所有输入组件都使用 `@bind-Value` 进行绑定。始终将文本包裹在 `<label>` 中，或使用 `id`/`for` 属性以提高可访问性。

### 使用枚举值的 InputSelect

```razor
<InputSelect @bind-Value="Model!.Status">
    <option value="">-- 选择 --</option>
    @foreach (var value in Enum.GetValues<OrderStatus>())
    {
        <option value="@value">@value</option>
    }
</InputSelect>
```

### InputRadioGroup

```razor
<InputRadioGroup @bind-Value="Model!.Priority">
    @foreach (var p in Enum.GetValues<Priority>())
    {
        <label>
            <InputRadio Value="p" /> @p
        </label>
    }
</InputRadioGroup>
```

## 验证

### 数据注解

在模型上定义验证规则：

```csharp
public class EmployeeModel
{
    [Required, StringLength(100)]
    public string? Name { get; set; }

    [Required, EmailAddress]
    public string? Email { get; set; }

    [Range(18, 99)]
    public int Age { get; set; }

    [Required]
    public string? Department { get; set; }
}
```

在 `EditForm` 内部添加 `<DataAnnotationsValidator />`——如果没有它，注解属性会被静默忽略。

使用以下方式显示错误：
- `<ValidationSummary />`——所有错误在一个列表中
- `<ValidationMessage For="() => Model!.FieldName" />`——每个字段的行内错误

### 自定义验证器组件

对于服务器端验证（唯一性检查，业务规则）：

```csharp
public class CustomValidator : ComponentBase
{
    [CascadingParameter]
    private EditContext? EditContext { get; set; }

    private ValidationMessageStore? messageStore;

    protected override void OnInitialized()
    {
        messageStore = new ValidationMessageStore(EditContext!);
        EditContext!.OnValidationRequested += (s, e) => messageStore.Clear();
        EditContext!.OnFieldChanged += (s, e) => messageStore.Clear(e.FieldIdentifier);
    }

    public void DisplayErrors(Dictionary<string, List<string>> errors)
    {
        foreach (var (field, messages) in errors)
        {
            foreach (var message in messages)
            {
                messageStore!.Add(EditContext!.Field(field), message);
            }
        }
        EditContext!.NotifyValidationStateChanged();
    }

    public void ClearErrors()
    {
        messageStore?.Clear();
        EditContext?.NotifyValidationStateChanged();
    }
}
```

在表单中使用：

```razor
<EditForm Model="Model" OnValidSubmit="HandleSubmit" FormName="register">
    <DataAnnotationsValidator />
    <CustomValidator @ref="customValidator" />
    <ValidationSummary />
    @* 输入字段 *@
</EditForm>

@code {
    private CustomValidator? customValidator;

    private async Task HandleSubmit()
    {
        var errors = await RegistrationService.ValidateAsync(Model!);
        if (errors.Count > 0)
        {
            customValidator!.DisplayErrors(errors);
            return;
        }
        // 继续
    }
}
```

## 仅交互模式下的输入变化响应

### @bind:after

在绑定值变化后运行逻辑：

```razor
<InputText @bind-Value="Model!.ZipCode" @bind:after="OnZipCodeChanged" />

@code {
    private async Task OnZipCodeChanged()
    {
        // 根据新邮编获取城市/州
        var location = await LocationService.LookupAsync(Model!.ZipCode);
        Model.City = location?.City;
        Model.State = location?.State;
    }
}
```

### @oninput 用于实时过滤

```razor
<input type="text" @oninput="OnSearchInput" placeholder="搜索..." />

@code {
    private string searchTerm = "";
    private List<Item> filteredItems = new();

    private void OnSearchInput(ChangeEventArgs e)
    {
        searchTerm = e.Value?.ToString() ?? "";
        filteredItems = allItems.Where(i =>
            i.Name.Contains(searchTerm, StringComparison.OrdinalIgnoreCase)).ToList();
    }
}
```

## 仅适用于静态 SSR 的模式

当表单在静态 SSR 中渲染时适用（模式为 None，或每页没有 `@rendermode`）。

### SupplyParameterFromForm

将 POST 数据绑定到表单提交时模型上的属性：

```csharp
[SupplyParameterFromForm]
private ContactModel? Contact { get; set; }

protected override void OnInitialized() => Contact ??= new();
```

**关键：** `OnInitialized` 中的 `??=` 是必需的。在 GET 时属性为 null——`??=` 创建模型。在 POST 时框架填充它——`??=` 保留已发布值。

### FormName —— 一页上的多个表单

每个表单需要一个唯一的 `FormName`：

```razor
<EditForm Model="Search" OnSubmit="DoSearch" FormName="search">...</EditForm>
<EditForm Model="Contact" OnValidSubmit="SaveContact" FormName="contact">...</EditForm>
```

将 `[SupplyParameterFromForm]` 与其表单匹配：

```csharp
[SupplyParameterFromForm(FormName = "search")]
private SearchModel? Search { get; set; }

[SupplyParameterFromForm(FormName = "contact")]
private ContactModel? Contact { get; set; }
```

### 表单的增强导航

添加 `Enhance` 以实现类似 SPA 的表单提交，无需全页刷新：

```razor
<EditForm Model="Model" OnValidSubmit="Save" FormName="quick" Enhance>
```

增强表单通过 `fetch` 提交，修补 DOM，并保留滚动位置。页面即使在 SSR 中也保持交互感。

### 纯 HTML 表单

在 SSR 中使用原始 `<form>` 而不是 `EditForm` 时，手动添加防篡改令牌：

```razor
<form method="post" @onsubmit="Submit" @formname="raw-form">
    <AntiforgeryToken />
    <input name="Model.Name" value="@Model?.Name" />
    <button type="submit">发送</button>
</form>
```

`EditForm` 自动包含防篡改令牌。

## 文件上传

`InputFile` 仅在 **交互模式** 下工作——不在静态 SSR 中。

```razor
<InputFile OnChange="OnFileSelected" accept=".pdf,.jpg,.png" />

@code {
    private IBrowserFile? selectedFile;

    private async Task OnFileSelected(InputFileChangeEventArgs e)
    {
        selectedFile = e.File;

        // 读取带大小限制的流
        await using var stream = selectedFile.OpenReadStream(maxAllowedSize: 10 * 1024 * 1024);
        // 处理流——保存到磁盘，上传到存储等
    }
}
```

流大小限制：
- **服务器：** 默认约 30 KB SignalR 消息大小。调用 `OpenReadStream(maxAllowedSize)` 增大。大文件流经电路。
- **WebAssembly：** 浏览器中读取文件。没有 SignalR 限制，但内存受限。

对于多个文件：

```razor
<InputFile OnChange="OnFilesSelected" multiple />

@code {
    private async Task OnFilesSelected(InputFileChangeEventArgs e)
    {
        foreach (var file in e.GetMultipleFiles(maxAllowedFiles: 10))
        {
            await using var stream = file.OpenReadStream(maxAllowedSize: 10 * 1024 * 1024);
            // 处理每个文件
        }
    }
}
```

## 防止重复提交

提交时禁用按钮：

```razor
<button type="submit" disabled="@isSubmitting">
    @(isSubmitting ? "保存中..." : "保存")
</button>

@code {
    private bool isSubmitting;

    private async Task HandleSubmit()
    {
        isSubmitting = true;
        try
        {
            await SaveService.SaveAsync(Model!);
        }
        finally
        {
            isSubmitting = false;
        }
    }
}
```

## 自定义验证 CSS

替换默认的 `valid`/`invalid` CSS 类：

```csharp
public class BootstrapFieldCssClassProvider : FieldCssClassProvider
{
    public override string GetFieldCssClass(EditContext editContext, in FieldIdentifier fieldIdentifier)
    {
        var isValid = !editContext.GetValidationMessages(fieldIdentifier).Any();
        return editContext.IsModified(fieldIdentifier)
            ? (isValid ? "is-valid" : "is-invalid")
            : "";
    }
}
```

应用于表单：

```csharp
protected override void OnInitialized()
{
    editContext = new EditContext(model);
    editContext.SetFieldCssClassProvider(new BootstrapFieldCssClassProvider());
}
```

## 不要

- 不要在静态 SSR 表单中使用 `@bind` 或 `@oninput`——它们需要交互。使用 `[SupplyParameterFromForm]` 和 `FormName`。
- 不要忘记 `Model ??= new()` 在 `OnInitialized` 中——模型在 GET 时为 null，在 POST 时被填充。
- 不要将 `OnSubmit` 与 `OnValidSubmit`/`OnInvalidSubmit` 结合使用——它们是互斥的。
- 不要省略 `<DataAnnotationsValidator />`——没有它，验证属性会被静默忽略。
- 不要在 SSR 中省略 `FormName`——当页面有多个表单时，两者都会在任意提交时触发。
- 不要在静态 SSR 中使用 `InputFile`——它需要交互式渲染模式。
- 不要在 `EditForm` 上同时使用 `Model` 和 `EditContext`——选择一个。
- 不要忘记 `<AntiforgeryToken />` 在原始 `<form>` 元素中——没有它，服务器会拒绝 POST。
