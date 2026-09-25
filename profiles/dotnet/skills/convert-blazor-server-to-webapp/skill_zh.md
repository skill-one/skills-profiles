# 将 Blazor Server 应用转换为 Blazor Web 应用

这项技能帮助代理将预-.NET 8 的 Blazor Server 应用转换为 .NET 8+ 的 Blazor Web 应用。旧的托管模型使用 `AddServerSideBlazor`/`MapBlazorHub`，并以 `_Host.cshtml` Razor 页面作为入口点。新的 Blazor Web 应用模型使用 `AddRazorComponents`/`MapRazorComponents`，以 `App.razor` 根组件为入口，支持组件级渲染模式、增强导航、流式渲染等 .NET 8+ 功能。转换后的应用使用 `InteractiveServer` 渲染模式以保留现有的交互行为。

## 使用场景

- 将 Blazor Server 应用从 .NET 6 或 .NET 7 迁移到 .NET 8+
- 应用当前在 `Program.cs`（或 `Startup.cs`）中使用 `AddServerSideBlazor()` 和 `MapBlazorHub()`
- 应用使用 `Pages/_Host.cshtml`（或 `_Host.razor`）作为带组件标签辅助的宿主页面
- 希望采用新的 Blazor Web 应用功能，同时保留服务器端交互渲染

## 不适用场景

- **应用已经使用 `AddRazorComponents` 和 `MapRazorComponents`。** 它已经是 Blazor Web 应用 — 无需转换。停止此处并告知用户应用已使用 Blazor Web 应用模型。
- Blazor WebAssembly 或托管 Blazor WebAssembly 应用 — 这些有不同的迁移路径
- 应用应保留在传统的 Blazor Server 托管模型（只需更新 TFM 和包）
- 应用目标为 .NET Framework — 它必须先迁移到 .NET

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| Blazor Server 项目 | 是 | Blazor Server 应用的 `.csproj` 和源文件 |
| 目标框架 | 是 | .NET 8 或更高版本（例如 `net8.0`、`net9.0`、`net10.0`） |
| `Program.cs` 或 `Startup.cs` | 是 | 应用的服务和中间件配置 |
| `_Host.cshtml` 位置 | 推荐 | 通常为 `Pages/_Host.cshtml`；某些项目中可能是 `_Host.razor` |

## 工作流程

> **提交策略：** 每完成一个逻辑步骤后提交，以便迁移过程可审查和可二分法测试。

### 第 1 步：更新项目文件

更新 `.csproj` 文件：

1. 将目标框架标记器 (TFM) 更改为目标版本：
   ```xml
   <TargetFramework>net8.0</TargetFramework>
   ```
2. 将所有 `Microsoft.AspNetCore.*`、`Microsoft.EntityFrameworkCore.*`、`Microsoft.Extensions.*` 和 `System.Net.Http.Json` 包引用更新为匹配的版本。

对于非 Blazor 项目文件更改（空值引用类型、隐式使用、HTTP/3 支持、等），请参阅 [通用 ASP.NET Core 迁移指南](https://learn.microsoft.com/aspnet/core/migration/70-to-80)。

### 第 2 步：从 `App.razor` 创建 `Routes.razor`

旧的 `App.razor` 包含 `<Router>` 组件。此内容将移动到新的 `Routes.razor` 文件中，以便 `App.razor` 可以成为根 HTML 文档组件。

1. 在项目根目录中创建一个新文件 `Routes.razor`。
2. 将 `App.razor` 的全部内容移动到 `Routes.razor`。
3. 如果内容被包裹在 `<CascadingAuthenticationState>` 中，请移除该包装器（在步骤 5 中将使用服务替换）。
4. 将 `App.razor` 留空，以便进行下一步。

生成的 `Routes.razor` 应类似于：

```razor
<Router AppAssembly="@typeof(Program).Assembly">
    <Found Context="routeData">
        <RouteView RouteData="@routeData" DefaultLayout="@typeof(MainLayout)" />
        <FocusOnNavigate RouteData="@routeData" Selector="h1" />
    </Found>
    <NotFound>
        <LayoutView Layout="@typeof(MainLayout)">
            <p>Sorry, there's nothing at this address.</p>
        </LayoutView>
    </NotFound>
</Router>
```

如果应用使用 `<AuthorizeRouteView>` 而不是 `<RouteView>`，请保留它 — 它在 Blazor Web 应用中工作方式相同。

### 第 3 步：将 `_Host.cshtml` 转换为 `App.razor`

将 `Pages/_Host.cshtml` 中的 HTML 容器移动到现在空的 `App.razor` 中，并将其从 Razor 页面转换为 Razor 组件：

1. **移除 Razor 页面指令** — 删除 `@page "/"`、`@using Microsoft.AspNetCore.Components.Web`、`@namespace` 和 `@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers`。
2. **添加组件注入** — 如果使用环境条件错误 UI，请添加：
   ```razor
   @inject IHostEnvironment Env
   ```
3. **修复 base 标签** — 将 `<base href="~/" />` 替换为 `<base href="/" />`。
4. **替换 HeadOutlet 组件标签辅助器** — 将：
   ```html
   <component type="typeof(HeadOutlet)" render-mode="ServerPrerendered" />
   ```
   替换为：
   ```razor
   <HeadOutlet @rendermode="InteractiveServer" />
   ```
5. **用 Routes 替换 App 组件标签辅助器** — 将：
   ```html
   <component type="typeof(App)" render-mode="ServerPrerendered" />
   ```
   替换为：
   ```razor
   <Routes @rendermode="InteractiveServer" />
   ```
6. **替换环境标签辅助器** — 将：
   ```html
   <environment include="Staging,Production">
       An error has occurred. This application may no longer respond until reloaded.
   </environment>
   <environment include="Development">
       An unhandled exception has occurred. See browser dev tools for details.
   </environment>
   ```
   替换为：
   ```razor
   @if (Env.IsDevelopment())
   {
       <text>
           An unhandled exception has occurred. See browser dev tools for details.
       </text>
   }
   else
   {
       <text>
           An error has occurred. This app may no longer respond until reloaded.
       </text>
   }
   ```
7. **更新 Blazor 脚本** — 将：
   ```html
   <script src="_framework/blazor.server.js"></script>
   ```
   替换为：
   ```html
   <script src="_framework/blazor.web.js"></script>
   ```
8. **添加渲染模式导入** — 在 `_Imports.razor` 中添加：
   ```razor
   @using static Microsoft.AspNetCore.Components.Web.RenderMode
   ```
9. **删除 `Pages/_Host.cshtml`**（如果存在，则删除 `Pages/_Host.cshtml.cs`）。

**预渲染说明：** 如果原始应用使用 `render-mode="Server"`（而不是 `"ServerPrerendered"`），则预渲染被禁用。通过使用 `new InteractiveServerRenderMode(prerender: false)` 而不是 `InteractiveServer`，保留此行为，`HeadOutlet` 和 `Routes` 都使用此设置。

### 第 4 步：更新 `Program.cs`

对 `Program.cs`（如果应用使用旧的托管模式，则为 `Startup.cs`）进行以下更改：

1. **替换 Blazor Server 服务** — 将：
   ```csharp
   builder.Services.AddServerSideBlazor();
   ```
   替换为：
   ```csharp
   builder.Services.AddRazorComponents()
       .AddInteractiveServerComponents();
   ```

   如果 `AddServerSideBlazor` 配置了选项（例如，电路选项、Hub 选项、详细错误），请将它们迁移到 `AddInteractiveServerComponents`：
   ```csharp
   // 旧：
   builder.Services.AddServerSideBlazor(options =>
   {
       options.DetailedErrors = true;
       options.DisconnectedCircuitRetentionPeriod = TimeSpan.FromMinutes(10);
   });

   // 新：
   builder.Services.AddRazorComponents()
       .AddInteractiveServerComponents(options =>
       {
           options.DetailedErrors = true;
           options.DisconnectedCircuitRetentionPeriod = TimeSpan.FromMinutes(10);
       });
   ```

2. **替换 Blazor 端点映射** — 将：
   ```csharp
   app.MapBlazorHub();
   ```
   替换为：
   ```csharp
   app.MapRazorComponents<App>()
       .AddInteractiveServerRenderMode();
   ```

   确保有对项目根命名空间的 `using` 语句，以便 `App` 解析为 `App.razor` 组件。

3. **移除回退路由** — 删除：
   ```csharp
   app.MapFallbackToPage("/_Host");
   ```

4. **移除显式路由中间件** — 如果存在，则删除：
   ```csharp
   app.UseRouting();
   ```
   端点路由是默认的，显式 `UseRouting()` 不再需要。

5. **添加防篡改中间件** — 如果存在 `UseAuthentication`/`UseAuthorization`，则在之后添加：
   ```csharp
   app.UseAntiforgery();
   ```
   `AddRazorComponents` 自动注册防篡改服务，但必须显式将中间件添加到管道中。没有它，表单 POST 请求会因 400 错误而失败。

### 第 5 步：迁移 `CascadingAuthenticationState`（如果存在）

如果应用使用 `<CascadingAuthenticationState>` 包裹路由器：

1. 移除 `<CascadingAuthenticationState>` 组件包装器（如果遵循此工作流程，则在步骤 2 中已完成）。
2. 在 `Program.cs` 中添加级联身份验证状态服务：
   ```csharp
   builder.Services.AddCascadingAuthenticationState();
   ```

组件包装器方法在 Blazor Web 应用中跨越渲染模式边界不起作用。服务方法为所有组件提供 `Task<AuthenticationState>` 作为级联值，无论渲染模式如何。

### 第 6 步：推荐改进（可选）

这些是可选的现代化改进 — 不是转换所必需的。如果您建议任何这些，请明确说明它们是可选的。

- **用 `MapStaticAssets` 替换 `UseStaticFiles`**（.NET 9+）：`app.MapStaticAssets()` 提供带指纹、预压缩和基于内容的 ETags 的优化静态文件服务。请参阅 [MapStaticAssets 文档](https://learn.microsoft.com/aspnet/core/fundamentals/static-files#mapstaticassets)。
- **为具有异步数据加载（`OnInitializedAsync`）的页面添加 `@attribute [StreamRendering]`** 以提高感知性能。页面会立即渲染其初始同步内容，并在异步数据到达时重新渲染。
- **更新 CSS 隔离包引用** — 如果 `<link>` 标签引用了 `_Host` 程序集名称；确保它匹配项目的实际程序集名称：`<link href="{AssemblyName}.styles.css" rel="stylesheet" />`。
- 对于其他非 Blazor 改进（最小化托管、HTTP/3、输出缓存、等），请参阅 [通用 ASP.NET Core 迁移指南](https://learn.microsoft.com/aspnet/core/migration/70-to-80)。

### 第 7 步：验证迁移

1. 针对新框架构建项目。确认无编译错误。
2. 搜索剩余的已删除 API 引用：
   - `AddServerSideBlazor`
   - `MapBlazorHub`
   - `MapFallbackToPage`
   - `blazor.server.js`
   - `_Host.cshtml`
3. 运行应用并验证：
   - 页面加载和渲染正确
   - 交互功能正常（表单、事件处理程序、SignalR 电路）
   - 页面间导航正常
   - 如果存在，身份验证和授权流程正常
4. 运行现有测试。

## 验证

- [ ] 无 `AddServerSideBlazor` 引用剩余
- [ ] 无 `MapBlazorHub` 引用剩余
- [ ] 无 `MapFallbackToPage("/_Host")` 引用剩余
- [ ] 无 `blazor.server.js` 引用剩余
- [ ] `Pages/_Host.cshtml` 已删除
- [ ] `App.razor` 作为根组件，具有完整的 HTML 文档结构
- [ ] `Routes.razor` 包含 `<Router>` 配置
- [ ] `Program.cs` 使用 `AddRazorComponents().AddInteractiveServerComponents()`
- [ ] `Program.cs` 使用 `MapRazorComponents<App>().AddInteractiveServerRenderMode()`
- [ ] `app.UseAntiforgery()` 存在于中间件管道中
- [ ] 如果应用使用 `<CascadingAuthenticationState>`，它已替换为 `AddCascadingAuthenticationState()` 服务注册
- [ ] 应用在目标框架上构建和运行成功

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 缺少 `UseAntiforgery()` 中间件 | `AddRazorComponents` 注册防篡改服务，但必须显式添加中间件。在 `UseAuthentication`/`UseAuthorization` 之后放置 `app.UseAntiforgery()`。没有它，表单 POST 请求会因 400 错误而失败。 |
| 忘记将 `blazor.server.js` 替换为 `blazor.web.js` | 旧的脚本在 Blazor Web 应用模型中不起作用。将所有 `_framework/blazor.server.js` 引用替换为 `_framework/blazor.web.js`。 |
| 未移除 `<CascadingAuthenticationState>` 包装器 | 组件包装器在 Blazor Web 应用中跨越渲染模式边界不起作用。使用 `builder.Services.AddCascadingAuthenticationState()`。 |
| 留下 `app.UseRouting()` 在管道中 | 显式 `UseRouting()` 不再需要，并且会干扰端点路由。除非其他中间件需要它，否则删除它。 |
| 使用 `InteractiveServer` 而预渲染被禁用 | 如果原始应用使用 `render-mode="Server"`（而不是 `"ServerPrerendered"`），请使用 `new InteractiveServerRenderMode(prerender: false)` 以保留相同行为。使用 `InteractiveServer` 启用预渲染，这可能导致依赖 JS 互操作的组件在初始化期间出现意外问题。 |
| 未迁移 `AddServerSideBlazor` 电路选项 | 如果配置了电路选项、Hub 选项或详细错误设置，请将它们迁移到 `AddInteractiveServerComponents(options => { ... })`。否则这些设置将静默丢失。 |
| `UseAntiforgery()` 放置在身份验证中间件之前 | 防篡改中间件必须放在 `UseAuthentication` 和 `UseAuthorization` 之后。放在前面会导致在用户身份建立之前运行防篡改验证。 |
| CSS 隔离包链接具有错误的程序集名称 | 如果 `<link href="{Name}.styles.css">` 标签引用了旧的项目名称，请更新它以匹配当前程序集名称。 |
