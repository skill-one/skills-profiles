# Angular 开发者指南

1. 在提供指导之前，始终分析项目的 Angular 版本，因为最佳实践和可用功能在不同版本之间可能会有显著差异。如果使用 Angular CLI 创建新项目，除非用户提示，否则不要指定版本。

2. 在生成代码时，遵循 Angular 的风格指南和最佳实践，以确保可维护性和性能。使用 Angular CLI 框架组件、服务、指令、管道和路由，以确保一致性。

3. 生成代码完成后，运行 `ng build` 以确保没有构建错误。如果有错误，请分析错误消息并修复它们后再继续。不要跳过此步骤，因为它对于确保生成的代码正确且功能正常至关重要。

## 创建新项目

如果用户没有提供指南，在创建新 Angular 项目时请遵循以下默认规则：

1. 使用最新稳定版本的 Angular，除非用户指定其他版本。
2. 在新项目中使用 Signal Forms 进行表单管理（Angular v22 及更高版本稳定支持）[了解更多](references/signal-forms.md)。

**`ng new` 的执行规则：**
在提示创建新 Angular 项目时，必须按照以下严格步骤确定正确的执行命令：

**步骤 1：检查显式用户版本。**

- **如果**用户请求特定版本（例如 Angular 15），请绕过本地安装并严格使用 `npx`。
- **命令：** `npx @angular/cli@<requested_version> new <project-name>`

**步骤 2：检查现有 Angular 安装。**

- **如果**没有请求特定版本，请在终端中运行 `ng version` 以检查 Angular CLI 是否已安装在系统上。
- **如果**命令成功并返回已安装版本，则直接使用本地/全局安装。
- **命令：** `ng new <project-name>`

**步骤 3：回退到最新版本。**

- **如果**没有请求特定版本并且 `ng version` 命令失败（表示系统不存在 Angular 安装），则必须使用 `npx` 获取最新版本。
- **命令：** `npx @angular/cli@latest new <project-name>`

## 组件

在处理 Angular 组件时，根据任务参考以下内容：

- **基础知识**：组件结构、元数据、核心概念、自闭合标签和模板控制流（@if、@for、@switch）。阅读 [components.md](references/components.md)
- **输入**：基于 Signal 的输入、转换和模型输入。阅读 [inputs.md](references/inputs.md)
- **输出**：基于 Signal 的输出和自定义事件最佳实践。阅读 [outputs.md](references/outputs.md)
- **宿主元素**：宿主绑定和属性注入。阅读 [host-elements.md](references/host-elements.md)
- **命名约定**：现代 Angular v20+ 的命名风格（“意图优先于角色”）用于文件、组件、服务、指令、管道和模型。阅读 [naming-conventions.md](references/naming-conventions.md)

如果您需要更深入的文档，而上述参考中未找到，请阅读 `https://angular.dev/guide/components` 的文档。

## 反应性和数据管理

在管理状态和数据反应性时，使用 Angular Signals 并参考以下内容：

- **Signals 概述**：核心 Signal 概念（`signal`、`computed`）、反应性上下文和 `untracked`。阅读 [signals-overview.md](references/signals-overview.md)
- **依赖状态（`linkedSignal`）**：创建与源 Signal 链接的可写状态。阅读 [linked-signal.md](references/linked-signal.md)
- **异步反应性（`resource`）**：直接将异步数据获取到 Signal 状态中。阅读 [resource.md](references/resource.md)
- **副作用（`effect`）**：日志记录、第三方 DOM 操作（`afterRenderEffect`）以及何时不应使用效果。阅读 [effects.md](references/effects.md)

## HTTP 通信

在与其他后端服务通信时，使用 Angular HTTP API 并参考以下内容：

- **HTTP 客户端和资源**：`provideHttpClient`、`HttpClient`、拦截器和 `httpResource`。阅读 [http-client.md](references/http-client.md)

## 表单

对于大多数新应用，**优先使用 Signal Forms**。在做出表单决策时，分析项目并考虑以下指南：

- 如果应用程序使用 v22 或更高版本且这是一个新表单，**优先使用 Signal Forms**。
- 对于旧版应用程序或在处理现有表单时，使用与应用程序当前表单策略匹配的适当表单类型。

- **Signal Forms**：使用 Signal 管理表单状态。阅读 [signal-forms.md](references/signal-forms.md)
- **模板驱动表单**：用于简单表单。阅读 [template-driven-forms.md](references/template-driven-forms.md)
- **响应式表单**：用于复杂表单。阅读 [reactive-forms.md](references/reactive-forms.md)

## 依赖注入

在 Angular 中实现依赖注入时，请遵循以下指南：

- **基础知识**：依赖注入概述、服务和 `inject()` 函数。阅读 [di-fundamentals.md](references/di-fundamentals.md)
- **创建和使用服务**：创建服务、`providedIn: 'root'` 选项以及将服务注入组件或其他服务。阅读 [creating-services.md](references/creating-services.md)
- **定义依赖提供者**：自动与手动提供、`InjectionToken`、`useClass`、`useValue`、`useFactory` 和作用域。阅读 [defining-providers.md](references/defining-providers.md)
- **注入上下文**：`inject()` 允许的位置、`runInInjectionContext` 和 `assertInInjectionContext`。阅读 [injection-context.md](references/injection-context.md)
- **分层注入器**：`EnvironmentInjector` 与 `ElementInjector`、解析规则、修饰符（`optional`、`skipSelf`）以及 `providers` 与 `viewProviders`。阅读 [hierarchical-injectors.md](references/hierarchical-injectors.md)

## 管道

在模板中格式化值、创建自定义管道或在 TypeScript 中重用管道逻辑时，请参考以下内容。在模板中优先使用管道；在模板外，避免仅为了调用 `transform()` 而注入管道类。

- **管道**：内置管道导入、自定义管道命名和实现、纯净与不纯净管道，以及使用独立格式化函数或提取的纯函数在 TypeScript 中重用模式。阅读 [pipes.md](references/pipes.md)

## Angular Aria

在为以下任何模式构建可访问的自定义组件时：手风琴、列表框、组合框、菜单、选项卡、工具栏、树、网格，请参考以下内容：

- **Angular Aria 组件**：构建无头、可访问的组件（手风琴、列表框、组合框、菜单、选项卡、工具栏、树、网格）以及样式 ARIA 属性。阅读 [angular-aria.md](references/angular-aria.md)

## 路由

在 Angular 中实现导航时，请参考以下内容：

- **定义路由**：URL 路径、静态与动态段、通配符和重定向。阅读 [define-routes.md](references/define-routes.md)
- **路由加载策略**：即时加载与延迟加载，以及上下文感知加载。阅读 [loading-strategies.md](references/loading-strategies.md)
- **使用 `<router-outlet>` 显示路由**：使用 `<router-outlet>`、嵌套出口和命名出口。阅读 [show-routes-with-outlets.md](references/show-routes-with-outlets.md)
- **导航到路由**：使用 `RouterLink` 的声明式导航和 `Router` 的程序化导航。阅读 [navigate-to-routes.md](references/navigate-to-routes.md)
- **使用守卫控制路由访问**：实现 `CanActivate`、`CanMatch` 和其他守卫以增强安全性。阅读 [route-guards.md](references/route-guards.md)
- **数据解析器**：使用 `ResolveFn` 在路由激活前预取数据。阅读 [data-resolvers.md](references/data-resolvers.md)
- **路由生命周期和事件**：导航事件的时序顺序和调试。阅读 [router-lifecycle.md](references/router-lifecycle.md)
- **渲染策略**：CSR、SSG（预渲染）和带水合的 SSR。阅读 [rendering-strategies.md](references/rendering-strategies.md)
- **路由过渡动画**：启用和自定义视图过渡 API。阅读 [route-animations.md](references/route-animations.md)

如果您需要更深入的文档或更多上下文，请访问 [官方 Angular 路由指南](https://angular.dev/guide/routing)。

## 样式和动画

在 Angular 中实现样式和动画时，请参考以下内容：

- **使用 Tailwind CSS 与 Angular**：将 Tailwind CSS 集成到 Angular 项目中。阅读 [tailwind-css.md](references/tailwind-css.md)
- **Angular 动画**：使用原生 CSS（推荐）或遗留 DSL 以实现动态效果。阅读 [angular-animations.md](references/angular-animations.md)
- **组件样式**：组件样式和封装的最佳实践。阅读 [component-styling.md](references/component-styling.md)

## 测试

在编写或更新测试时，根据任务参考以下内容：

- **基础知识**：单元测试的最佳实践（Vitest）、异步模式和 `TestBed`。阅读 [testing-fundamentals.md](references/testing-fundamentals.md)
- **组件测试套件**：用于稳健组件交互的标准模式。阅读 [component-harnesses.md](references/component-harnesses.md)
- **路由测试**：使用 `RouterTestingHarness` 进行可靠的导航测试。阅读 [router-testing.md](references/router-testing.md)
- **端到端（E2E）测试**：设置和运行 E2E 测试。阅读 [e2e-testing.md](references/e2e-testing.md)

## 工具

在处理 Angular 工具时，请参考以下内容：

- **Angular CLI**：创建应用程序、生成代码（组件、路由、服务）、服务运行和构建。阅读 [cli.md](references/cli.md)
- **代码现代化**：使用迁移自动重构到现代标准。阅读 [migrations.md](references/migrations.md)
- **Angular MCP Server**：可用工具、配置和实验性功能。阅读 [mcp.md](references/mcp.md)
- **环境配置**：构建时和运行时配置策略。阅读 [environment-configuration.md](references/environment-configuration.md)
