# 创建 Blazor Web 应用

## 开始前 — 汇总需求

如果用户请求没有明确以下内容，请在生成项目前询问：

1. **应用的功能是什么？** 列出主要界面/功能（例如，“带搜索和购物车的产品目录”）。
2. **需要什么样的交互性？** 显示数据和表单？实时更新？离线支持？丰富的拖放 UI？
3. **部署环境？** 面向公众？内部网络？慢速连接的移动用户？
4. **需要身份验证吗？** 匿名？个人账户？组织（Azure AD）？

## 选择合适的交互级别

Blazor 渲染模式是一个渐进的等级。从满足需求的最简单级别开始，只有在有明确理由的情况下才向上移动。

```
静态 SSR ──→ SSR + 增强导航 ──→ 服务器交互 ──→ WebAssembly 交互
最简单                                                          最复杂
```

### 决策规则

| 应用需要... | 使用 | 原因 |
|---|---|---|
| 显示数据、简单表单、页面间链接 | **静态 SSR** (`-int None`) | 无 JS 运行时、无电路、无 WebAssembly 下载。表单通过 HTML POST 工作。增强导航使其感觉更流畅。 |
| 以上所有 + 少量具有客户端行为的组件（实时搜索、实时更新、复杂表单向导） | **服务器交互，按页面** (`-int Server`) | 只有需要交互的组件使用 `@rendermode` 选择交互模式。其余保持静态。服务器端执行，完全 .NET 访问，无需 API 层。 |
| 大多数页面需要丰富的交互性（仪表板、拖放、聊天） | **服务器交互，全局** (`-int Server -ai`) | 所有组件默认为交互。一致的 UX，更简单的思维模型。权衡：每个用户在服务器上持有一个 SignalR 电路。 |
| 网络延迟是问题，用户在移动/慢速连接上，或应用必须支持离线 | **WebAssembly 交互** (`-int WebAssembly`) | 代码在浏览器中运行。消除往返延迟，但需要 `.Client` 项目、API 层用于数据访问，并在首次访问时将 .NET 运行时下载到浏览器。为离线支持，启用 PWA：在生成项目后添加服务工作和清单（模板默认不包含）。 |
| 快速初始加载（服务器）+ 低延迟（WebAssembly）后 | **自动交互** (`-int Auto`) | 首次访问使用服务器；后续访问使用缓存的 WebAssembly 运行时。最复杂的设置 — 见自动约束下文。仅在服务器和 WebAssembly 约束都适用时选择。 |

**默认推荐：** 从 `-int Server`（按页面）开始。它涵盖了绝大多数应用。仅在特定需求要求时才升级到全局或 WebAssembly。

### 自动模式约束

自动模式意味着组件代码首先在服务器上运行，然后在后续访问中在浏览器中运行。这会带来实际约束：

- **所有交互组件必须位于 `.Client` 项目中** — 与 WebAssembly 相同。
- **交互组件不能直接访问服务器** — 无 EF `DbContext`，无文件系统，无服务器端服务。所有数据访问必须通过 HTTP API。
- **两个 `Program.cs` 文件必须注册匹配的服务** — 服务器和客户端 DI 容器必须为交互组件注入的任何服务都提供实现。
- **代码不能假设其执行环境** — 无 `HttpContext` 访问，无浏览器专用 API 而无 `RendererInfo` 保护。
- **在两种模式下都进行测试** — 在开发期间在服务器上工作的组件可能在生产（第二次访问）的 WebAssembly 上失效。测试两种路径。

### 禁止事项

- 不要因为“很酷”而选择 WebAssembly — 它会添加 `.Client` 项目，强制 API 介导的数据访问，并在首次访问时将 ~10MB 下载到浏览器。
- 不要选择自动，除非你能说明为什么单独的服务器和 WebAssembly 都不足够。
- 不要为大多数页面都是只读内容的应用选择全局交互性 — 按页面保留静态页面快速，并减少服务器内存。

## 生成项目

### 仅静态 SSR（显示数据 + 简单表单）

```shell
dotnet new blazor -o {AppName} -int None
```

无交互运行时。通过 `blazor.web.js` 默认启用增强导航。

### 服务器交互，按页面（推荐默认）

```shell
dotnet new blazor -o {AppName} -int Server
```

页面默认为静态。将 `@rendermode InteractiveServer` 添加到需要交互的组件中。

### 服务器交互，全局

```shell
dotnet new blazor -o {AppName} -int Server -ai
```

所有页面通过 `App.razor` 中的 `<Routes @rendermode="InteractiveServer" />` 默认为交互。

### WebAssembly 交互，按页面

```shell
dotnet new blazor -o {AppName} -int WebAssembly
```

创建 `{AppName}`（服务器）和 `{AppName}.Client`（WebAssembly）项目。交互组件必须位于 `.Client` 中。

### WebAssembly 交互，全局

```shell
dotnet new blazor -o {AppName} -int WebAssembly -ai
```

### 自动交互，按页面

```shell
dotnet new blazor -o {AppName} -int Auto
```

### 自动交互，全局

```shell
dotnet new blazor -o {AppName} -int Auto -ai
```

### 带身份验证

将 `-au Individual` 添加到上述任何命令：

```shell
dotnet new blazor -o {AppName} -int Server -au Individual
```

`-au Individual` 生成 ASP.NET Core Identity，使用 SQLite（CLI）或 SQL Server（Visual Studio）。身份验证页面始终为静态 SSR — 它们不使用交互渲染模式。

`blazor` 模板仅支持 `-au Individual`。对于组织身份验证（Microsoft Entra ID、Azure AD B2C），先使用 `-au Individual` 生成，然后替换身份验证提供程序为 `Microsoft.Identity.Web` / OIDC 中间件，并在 `appsettings.json` 中配置租户。

## 模板生成的内容

### 单个项目（静态 SSR，服务器）

```
{AppName}/
├── Components/
│   ├── App.razor              # 根组件 — 设置 <HeadOutlet> 和 <Routes>
│   ├── Routes.razor           # 使用 <Router> 包裹路由发现
│   ├── Layout/
│   │   ├── MainLayout.razor   # 应用外壳，带导航、头部、尾部
│   │   └── MainLayout.razor.css
│   └── Pages/
│       └── Home.razor         # @page "/" — 首页
├── Program.cs                 # 服务注册和中间件
├── wwwroot/                   # 静态文件（CSS、图片）
└── {AppName}.csproj
```

### 两个项目（WebAssembly，自动）

```
{AppName}/                     # 服务器项目 — 托管应用
├── Components/                # 服务器专用组件（静态 SSR 页面、布局）
│   ├── App.razor
│   ├── Routes.razor
│   └── Layout/
├── Program.cs                 # 服务器 Program.cs
└── {AppName}.Client/          # 客户端项目 — WebAssembly 组件
    ├── Pages/                 # 交互组件位于此处
    ├── Program.cs             # 客户端 Program.cs
    └── _Imports.razor
```

**规则：** 使用 `InteractiveWebAssembly` 或 `InteractiveAuto` 的组件必须位于 `.Client` 项目中。它们可以引用共享代码，但不能引用服务器专用类型（EF `DbContext`、服务器端服务）。

## Program.cs 连接

模板为所选模式生成正确的 `Program.cs`。验证以下注册是否与您的意图匹配：

### 仅静态 SSR

```csharp
// Program.cs
builder.Services.AddRazorComponents();

// ...

app.MapRazorComponents<App>();
```

### 服务器（按页面或全局）

```csharp
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// ...

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();
```

### WebAssembly（按页面或全局）

```csharp
// 服务器 Program.cs
builder.Services.AddRazorComponents()
    .AddInteractiveWebAssemblyComponents();

// ...

app.MapRazorComponents<App>()
    .AddInteractiveWebAssemblyRenderMode()
    .AddAdditionalAssemblies(typeof({AppName}.Client._Imports).Assembly);
```

```csharp
// 客户端 Program.cs
builder.Services.AddAuthorizationCore();
// 注册 HttpClient、其他客户端服务
```

## 创建项目 AGENTS.md

生成项目后，在项目根目录（靠近 `.csproj`）创建一个 `AGENTS.md` 文件（对于两个项目设置，将其放在服务器项目根目录）。

根据所选模式从 `assets/agents-md/` 选择匹配的模板：

| 模式 | 模板文件 |
|------|--------------|
| 静态 SSR (`-int None`) | `assets/agents-md/ssr-none.md` |
| 服务器，按页面 (`-int Server`) | `assets/agents-md/server-per-page.md` |
| 服务器，全局 (`-int Server -ai`) | `assets/agents-md/server-global.md` |
| WebAssembly，按页面 (`-int WebAssembly`) | `assets/agents-md/webassembly-per-page.md` |
| WebAssembly，全局 (`-int WebAssembly -ai`) | `assets/agents-md/webassembly-global.md` |
| 自动，按页面 (`-int Auto`) | `assets/agents-md/auto-per-page.md` |
| 自动，全局 (`-int Auto -ai`) | `assets/agents-md/auto-global.md` |

将模板内容复制到项目的 `AGENTS.md` 中，并将每个 `{AppName}` 替换为实际的项目名称。如果生成了身份验证 (`-au Individual`)，请添加一个 `## 身份验证` 部分，注明已配置 ASP.NET Core Identity，且 `Components/Account/` 下的身份验证页面始终为静态 SSR — 不要向它们添加 `@rendermode`。

**在生成项目并创建 AGENTS.md 后，继续实现用户请求的功能。** 删除默认模板页面（Counter、Weather），并用实际的应用页面替换它们。

### 自动（按页面或全局）

```csharp
// 服务器 Program.cs
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents()
    .AddInteractiveWebAssemblyComponents();

// ...

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode()
    .AddInteractiveWebAssemblyRenderMode()
    .AddAdditionalAssemblies(typeof({AppName}.Client._Imports).Assembly);
```

## App.razor — 全局与按页面

全局和按页面交互的区别完全在 `App.razor` 中：

### 按页面（默认）

```razor
<!DOCTYPE html>
<html>
<head>
    <HeadOutlet />
</head>
<body>
    <Routes />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>
```

`<Routes>` 或 `<HeadOutlet>` 上无 `@rendermode`。单个页面选择交互。

### 全局

```razor
<!DOCTYPE html>
<html>
<head>
    <HeadOutlet @rendermode="InteractiveServer" />
</head>
<body>
    <Routes @rendermode="InteractiveServer" />
    <script src="_framework/blazor.web.js"></script>
</body>
</html>
```

将 `InteractiveServer` 替换为 `InteractiveWebAssembly` 或 `InteractiveAuto`（根据需要）。

## 生成项目后

1. **验证是否可以构建：** `dotnet build`
2. **运行：** `dotnet run`（如果是两个项目设置，在服务器项目中运行）
3. **添加第一个页面：** 在 `Components/Pages/`（服务器项目）或 `Pages/`（WebAssembly 组件的 `.Client` 项目）中创建一个 `.razor` 文件

## 禁止事项

- 不要使用 `dotnet new blazorwasm` — 那会创建一个独立的 WebAssembly SPA 而没有服务器端渲染。使用 `blazor` 模板并添加 `-int WebAssembly` 代替。
- 不要手动将 `AddInteractiveServerComponents()` 添加到使用 `-int None` 生成的项目并期望它工作 — 你还需要 `@rendermode` 指令，可能还需要更改 `App.razor`。如果模式需要根本性改变，请重新生成项目。
- 不要将 WebAssembly 目标组件放在服务器项目中 — 它们在预渲染时可以工作，但在转交后失败。
