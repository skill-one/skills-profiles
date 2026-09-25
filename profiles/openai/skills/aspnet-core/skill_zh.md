# ASP.NET Core

## 概述

选择合适的 ASP.NET Core 应用程序模型，正确地组合主机和请求管道，并按照 Microsoft 文档的风格实现框架功能。

加载满足任务所需的最小引用集。不要默认加载所有引用。

## 工作流程

1. 确认目标框架、SDK 和当前应用模型。
2. 对于新应用程序或重大重构，首先打开 `[references/stack-selection.md](references/stack-selection.md)`。
3. 接下来打开 `[references/program-and-pipeline.md](references/program-and-pipeline.md)`，用于 `Program.cs`、依赖注入 (DI)、配置、中间件、路由、日志记录和静态资源。
4. 打开一个主要的应用模型引用：
   - `[references/ui-blazor.md](references/ui-blazor.md)`
   - `[references/ui-razor-pages.md](references/ui-razor-pages.md)`
   - `[references/ui-mvc.md](references/ui-mvc.md)`
   - `[references/apis-minimal-and-controllers.md](references/apis-minimal-and-controllers.md)`
5. 仅在需要时添加横切引用：
   - `[references/data-state-and-services.md](references/data-state-and-services.md)`
   - `[references/security-and-identity.md](references/security-and-identity.md)`
   - `[references/realtime-grpc-and-background-work.md](references/realtime-grpc-and-background-work.md)`
   - `[references/testing-performance-and-operations.md](references/testing-performance-and-operations.md)`
6. 在将新平台 API 引入到较旧解决方案中或在不同主要版本之间迁移之前，打开 `[references/versioning-and-upgrades.md](references/versioning-and-upgrades.md)`。
7. 当需要 Microsoft Learn 部分而当前关注的引用未涵盖该任务时，使用 `[references/source-map.md](references/source-map.md)`。

## 默认操作假设

- 除非存储库或用户要求固定较旧的目标版本，否则优先选择最新的稳定 ASP.NET Core 和 .NET。
- 从 2026 年 3 月起，对于新生产工作，优先选择 .NET 10 / ASP.NET Core 10。除非用户明确要求预览功能，否则将 ASP.NET Core 11 视为预览版。
- 优先选择 `WebApplicationBuilder` 和 `WebApplication`。除非代码库已使用它们或任务为迁移，否则避免使用较旧的 `Startup` 和 `WebHost` 模式。
- 优先选择内置的依赖注入 (DI)、选项/配置、日志记录、ProblemDetails、OpenAPI、健康检查、速率限制、输出缓存和 Identity，然后再添加第三方基础设施。
- 保持功能切片的完整性，以便页面、组件、端点、控制器、验证、服务、数据访问和测试易于追踪。
- 尊重现有的应用模型。除非有明确理由，否则不要将 Razor Pages 重写为 MVC 或控制器重写为最小 API。

## 参考指南

- `[references/_sections.md](references/_sections.md)`：快速索引和阅读顺序。
- `[references/stack-selection.md](references/stack-selection.md)`：选择合适的 ASP.NET Core 应用程序模型和模板。
- `[references/program-and-pipeline.md](references/program-and-pipeline.md)`：结构化 `Program.cs`、服务、中间件、路由、配置、日志记录和静态资源。
- `[references/ui-blazor.md](references/ui-blazor.md)`：构建 Blazor Web 应用，选择渲染模式，并正确使用组件、表单和 JS 互操作。
- `[references/ui-razor-pages.md](references/ui-razor-pages.md)`：构建以页面为中心的服务器渲染应用程序，包括处理程序、模型绑定和约定。
- `[references/ui-mvc.md](references/ui-mvc.md)`：构建具有明确关注点分离的控制器/视图应用程序。
- `[references/apis-minimal-and-controllers.md](references/apis-minimal-and-controllers.md)`：使用 Minimal APIs 或控制器构建 HTTP API，包括验证和响应模式。
- `[references/data-state-and-services.md](references/data-state-and-services.md)`：负责任地使用 EF Core、`DbContext`、选项、`IHttpClientFactory`、会话、临时数据和应用程序状态。
- `[references/security-and-identity.md](references/security-and-identity.md)`：应用身份验证、授权、Identity、密钥、数据保护、CORS、CSRF 和 HTTPS 指南。
- `[references/realtime-grpc-and-background-work.md](references/realtime-grpc-and-background-work.md)`：使用 SignalR、gRPC 和托管服务。
- `[references/testing-performance-and-operations.md](references/testing-performance-and-operations.md)`：添加集成测试、浏览器测试、缓存、压缩、健康检查、速率限制和部署注意事项。
- `[references/versioning-and-upgrades.md](references/versioning-and-upgrades.md)`：处理目标框架、破坏性更改、过时 API 和迁移。
- `[references/source-map.md](references/source-map.md)`：将官方 ASP.NET Core 文档树映射到此技能中的引用。

## 执行说明

- 生成新代码时，从正确的 `dotnet new` 模板开始，并保持生成的结构易于识别。
- 编辑现有解决方案时，首先遵循解决方案的约定，并使用这些参考指南避免框架误用或过时模式。
- 当任务提到“最新”时，在依赖内存之前，先在 Microsoft Learn 或 ASP.NET Core 文档存储库上验证该功能。
