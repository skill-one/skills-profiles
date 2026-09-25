# 配置认证

## 第 1 步 — 阅读 AGENTS.md

在修改之前，请先在工作区根目录下阅读 `AGENTS.md`，了解项目的交互模式和作用域。

## 第 2 步 — 在 Program.cs 中注册认证服务

```csharp
// Program.cs (服务器项目)
builder.Services.AddCascadingAuthenticationState();
builder.Services.AddAuthorization();
```

对于 ASP.NET Core Identity，添加 Identity 服务：

```csharp
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = IdentityConstants.ApplicationScheme;
    options.DefaultSignInScheme = IdentityConstants.ExternalScheme;
})
.AddIdentityCookies();

builder.Services.AddIdentityCore<ApplicationUser>()
    .AddRoles<IdentityRole>()
    .AddEntityFrameworkStores<ApplicationDbContext>()
    .AddSignInManager()
    .AddDefaultTokenProviders();
```

## 第 3 步 — 配置 App.razor 以支持认证和渲染模式

`App.razor` 组件必须使用 `AuthorizeRouteView` 并根据条件应用渲染模式，以便从交互式路由中排除的页面以静态方式渲染。

```razor
<!DOCTYPE html>
<html>
<head>
    <HeadOutlet @rendermode="RenderModeForPage" />
</head>
<body>
    <Routes @rendermode="RenderModeForPage" />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>

@code {
    [CascadingParameter]
    public HttpContext HttpContext { get; set; } = default!;

    private IComponentRenderMode? RenderModeForPage =>
        HttpContext.AcceptsInteractiveRouting()
            ? InteractiveServer   // 替换为应用的渲染模式
            : null;
}
```

在 `Routes.razor`（或路由所在的任何位置）使用 `AuthorizeRouteView`：

```razor
<Router AppAssembly="typeof(Program).Assembly">
    <Found Context="routeData">
        <AuthorizeRouteView RouteData="routeData"
                            DefaultLayout="typeof(Layout.MainLayout)">
            <NotAuthorized>
                @if (context.User.Identity?.IsAuthenticated != true)
                {
                    <RedirectToLogin />
                }
                else
                {
                    <p>您没有权限访问此资源。</p>
                }
            </NotAuthorized>
        </AuthorizeRouteView>
        <FocusOnNavigate RouteData="routeData" Selector="h1" />
    </Found>
</Router>
```

## 第 4 步 — 保护页面和组件

### 页面上的 `[Authorize]` 属性

```razor
@page "/admin"
@attribute [Authorize]
```

使用角色或策略：

```razor
@attribute [Authorize(Roles = "Admin")]
@attribute [Authorize(Policy = "RequireManager")]
```

### 用于条件式 UI 的 `AuthorizeView`

```razor
<AuthorizeView>
    <Authorized>欢迎，@context.User.Identity?.Name!</Authorized>
    <NotAuthorized><a href="Account/Login">登录</a></NotAuthorized>
</AuthorizeView>
```

角色/策略变体：

```razor
<AuthorizeView Roles="Admin,Manager">
    <Authorized>管理员内容</Authorized>
</AuthorizeView>
```

### 在代码中访问认证状态

```csharp
[CascadingParameter]
private Task<AuthenticationState>? AuthState { get; set; }

protected override async Task OnInitializedAsync()
{
    if (AuthState is not null)
    {
        var state = await AuthState;
        var isAdmin = state.User.IsInRole("Admin");
    }
}
```

## 第 5 步 — Identity 页面必须保持静态 SSR

`SignInManager` 和 `UserManager` 内部使用 `HttpContext`，并在交互式组件中**抛出异常**。Identity 页面（登录、注册、管理）必须以静态 SSR 方式渲染。

在**全局交互式**应用中，标记每个 Identity 页面：

```razor
@page "/Account/Login"
@attribute [ExcludeFromInteractiveRouting]
```

这会强制全页导航（退出交互式电路），以便页面通过静态 SSR 管道渲染，并使用真实的 `HttpContext`。

`App.razor` 必须使用 `AcceptsInteractiveRouting()`（第 3 步）返回 `null` 以适用于这些页面——否则框架仍尝试以交互式方式渲染它们。

在**按页面**配置的应用中，Identity 页面默认为静态（没有 `@rendermode` 指令），因此不需要 `[ExcludeFromInteractiveRouting]`。

## 第 6 步 — WebAssembly / 自动模式下的认证状态

WebAssembly 组件在浏览器中运行，没有 `HttpContext`。认证状态必须在服务器预渲染期间序列化，并在客户端反序列化。

**服务器 `Program.cs`：**

```csharp
builder.Services.AddAuthenticationStateSerialization();
```

**客户端 `.Client/Program.cs`：**

```csharp
builder.Services.AddAuthenticationStateDeserialization();
```

如果没有这些调用，`Task<AuthenticationState>` 在 WebAssembly 接管预渲染后会解析为匿名用户。

`AddAuthenticationStateSerialization` 接受选项以包含角色和声明数据：

```csharp
builder.Services.AddAuthenticationStateSerialization(options =>
    options.SerializeAllClaims = true);
```

## 渲染模式 × 认证矩阵

| 渲染模式 | HttpContext.User | SignInManager | 认证状态源 | 关键要求 |
|---|---|---|---|---|
| 静态 SSR | 可用 | 可用 | 服务器管道 | 使用中间件进行重定向，`<NotAuthorized>` 不会渲染 |
| 服务器（交互式） | 不可用 | 抛出异常 | `CascadingAuthenticationState` | 使用 `[Authorize]` + `AuthorizeView`，不要使用 `HttpContext` |
| WebAssembly | 不可用 | 抛出异常 | 从服务器序列化 | `AddAuthenticationStateSerialization` / `Deserialization` |
| 自动 | WebAssembly 接管后不可用 | 抛出异常 | 从服务器序列化 | 与 WebAssembly 相同；在**两个** Program.cs 文件中注册 |

## 常见错误

| 错误 | 症状 | 修复 |
|---------|---------|-----|
| 在交互式组件中使用 `HttpContext.User` | 空或过期的声明 | 使用 `[CascadingParameter] Task<AuthenticationState>` |
| 交互式组件中的 `SignInManager` | `InvalidOperationException` | 移动到带有 `[ExcludeFromInteractiveRouting]` 的静态 SSR 页面 |
| 缺少 `AddAuthenticationStateSerialization` | WebAssembly 加载后为匿名用户 | 在服务器 Program.cs 中添加；在客户端 Program.cs 中添加 `Deserialization` |
| 静态 SSR 布局中的 `<NotAuthorized>` | 内容从未显示 | 静态 SSR 使用中间件管道；通过 `LoginPath` 或 `RedirectToLogin` 组件重定向 |
| 全局交互式而未使用 `AcceptsInteractiveRouting` | Identity 页面崩溃 | 在 App.razor（第 3 步）中添加 `AcceptsInteractiveRouting()` 检查 |
| 缺少 `AddCascadingAuthenticationState()` | `Task<AuthenticationState>` 为空 | 在 Program.cs（第 2 步）中注册 |
