# 生成集成计划（SDK 安装）

根据您的检测结果，选择合适的 SDK 并规划所需的最小变更集。

此技能嵌套在 [LaunchDarkly SDK 安装（引导）](../SKILL.md) 下；父级 **步骤 2** 是 **计划**。**优先：** [检测仓库堆栈](../detect/SKILL.md)。**下一步：** [应用代码变更](../apply/SKILL.md)。

## 选择合适的 SDK

使用 [SDK 配方](../../references/sdk/recipes.md) 参考文档，将检测到的堆栈与 SDK 进行匹配。从该文件中的 **前 10 个 SDK（从这里开始）** 开始，用于常见堆栈；使用 **(其他)** 部分用于不太常见的 SDK。

关键决策：

| 项目类型 | SDK 类型 | 关键类型 |
|-------------|----------|----------|
| 后端 API、服务器渲染应用、CLI 工具 | 服务器端 SDK | SDK 密钥 |
| 浏览器 SPA（React、Vue、Angular、原生 JS） | 客户端 SDK | 客户端 ID |
| iOS 或 Android 原生应用 | 移动 SDK | 移动密钥 |
| React Native | 移动 SDK | 移动密钥 |
| Flutter（iOS、Android 或桌面 **应用** 目标） | 客户端 SDK（Flutter） | 移动密钥 |
| Flutter **Web** | 客户端 SDK（Flutter） | 客户端 ID |
| Electron 桌面应用 | 客户端 SDK（Node.js） | 客户端 ID |
| Cloudflare Workers、Vercel Edge、AWS Lambda@Edge | 边缘 SDK | SDK 密钥 |
| .NET 客户端（MAUI、Xamarin、WPF、UWP） | 移动 SDK (.NET) | 移动密钥 |
| C/C++ 客户端应用程序 | 客户端 SDK（C/C++） | 移动密钥 |
| C/C++ 服务器应用程序 | 服务器端 SDK（C/C++） | SDK 密钥 |
| Haskell 服务器 | 服务器端 SDK（Haskell） | SDK 密钥 |
| Lua 服务器 | 服务器端 SDK（Lua） | SDK 密钥 |
| Roku（BrightScript） | 客户端 SDK（Roku） | 移动密钥 |

对于每个支持的 SDK，包名、安装提示和官方 **文档** 链接，请使用 [SDK 配方](../../references/sdk/recipes.md) 以及 [`snippets/`](../../references/sdk/snippets/) 下链接的文件。

## 双重 SDK 集成

当用户要求 **同时** 进行服务器端和客户端集成，或者堆栈明显需要 **两个** LaunchDarkly SDK（例如 Next.js 带服务器评估 **和** 浏览器 UI 标志、一个工作区中分离的后端 + SPA 仓库等）时，使用此部分。

**不要** 在 **忽略** 第二个（`package.json` 中没有第二个包、没有第二个初始化路径、没有遵循第二个配方）的情况下“完成”引导。每个 SDK 都是一个独立的产品，有自己的安装命令和初始化。

对于这两个 SDK 中的 **每个**，计划必须明确说明（没有遗漏）：

**服务器端跟踪：**

1. 配方 / [SDK 配方](../../references/sdk/recipes.md) 行或片段名称
2. 包名（精确的工件）
3. 安装命令（配方中的完整命令）
4. 依赖文件（添加行的位置）
5. 入口点文件（例如 `instrumentation.ts`、API 入口点、`main.py`）
6. 环境变量（通常 `LAUNCHDARKLY_SDK_KEY`）
7. 初始化摘要（运行位置；哪个文档/片段）

**客户端跟踪：**

1. 配方 / 片段名称（**不同**于服务器）
2. 包名（例如 React Web 与 Node 服务器 -- 必须是 **客户端** 工件）
3. 安装命令（**第二个** 命令 -- 永不暗示）
4. 依赖文件
5. 入口点文件（例如 `app/providers.tsx`、根布局、`main.tsx`）
6. 环境变量（捆绑器前缀 **客户端** ID，例如 `NEXT_PUBLIC_...`）
7. 初始化摘要（来自 **客户端** 配方的提供程序/包装器/钩子）

如果您无法命名 **两个** 包和 **两个** 入口点，则您尚未完成计划——请返回到 [SDK 配方](../../references/sdk/recipes.md) 和检测。

**重要区别：**

- **Next.js**：服务器端 SDK 用于 API 路由 / 服务器组件 / RSC 上下文在服务器上评估；React 客户端 SDK 用于客户端组件。如果用户要求 **两者**，则计划中列出 **两个** 跟踪的完整内容。如果他们只想从单个表面开始，请在计划中明确说明。
- **Node.js**：如果是后端服务（Express、Fastify 等），请使用服务器端 SDK。还有一个 [Node.js 客户端 SDK](https://launchdarkly.com/docs/sdk/client-side/node-js) 用于桌面/Electron 应用。
- **React**：如果是独立的 SPA，请使用 `launchdarkly-react-client-sdk`。如果是 Next.js 的一部分，请参阅上述内容。
- **.NET**：对于 ASP.NET 和后端服务，请使用 **服务器** SDK (`LaunchDarkly.ServerSdk`)。对于 MAUI、Xamarin、WPF 和 UWP，请使用 **.NET 移动 SDK** (`LaunchDarkly.ClientSdk`，**移动密钥**)——[SDK 配方——.NET (客户端)](../../references/sdk/recipes.md#net-client)。**Blazor WebAssembly**（和其他浏览器托管的 .NET 客户端 UI）仍然使用 `LaunchDarkly.ClientSdk`，但使用 **客户端 ID**，而不是移动密钥——请参阅相同的配方。
- **Flutter**：使用 Flutter 客户端 SDK (`launchdarkly_flutter_client_sdk`——[SDK 配方——Flutter](../../references/sdk/recipes.md#flutter))。对于典型的 iOS/Android/桌面 **应用** 构建，使用 **移动密钥**；对于 **Flutter web**，使用 **客户端 ID**（和项目对公共环境变量的模式）。如果用户发送多个目标，请确认首先连接哪个，或为每个目标计划单独的环境/配置。

## 规划变更

您的集成计划应明确标识：

### 1. 要修改的文件

使用在 [检测仓库堆栈](../detect/SKILL.md) 过程中收集的信息——特别是检测到的包管理器、依赖文件和应用程序入口点：

- **依赖文件**：检测期间确定的文件（例如 `package.json`、`requirements.txt`、`go.mod`）——使用检测到的包管理器添加 SDK
- **入口点文件**：检测期间确定的应用程序入口点——SDK 初始化代码将放置的位置。双重 SDK 计划列出 **两个** 入口点（参见 [双重 SDK 集成](#dual-sdk-integrations)）。
- **环境/配置文件**：在集成根目录下优先使用 `.env` 存储真实密钥（如果不存在则创建它）；确保 `.env` 在该位置的 `.gitignore` 中列出。使用 `.env.example` / `.env.sample` 仅用于占位符。如果项目不使用 dotenv，请遵循其现有的配置模式——参见 [应用代码变更](../apply/SKILL.md) 步骤 2 的同意、写入密钥和服务器+客户端混合情况。

### 2. 代码变更

对于范围内的每个 SDK（一个或两个跟踪），描述具体变更：

1. **添加 SDK 依赖**——来自 SDK 配方的安装命令（当双重 SDK 时重复每个包）
2. **添加 SDK 导入**——该跟踪入口点顶部的导入语句
3. **添加 SDK 初始化**——来自该配方/片段的该 SDK 初始化代码，放置在正确的生命周期早期（服务器与客户端）
4. **配置凭证**——通过环境变量，永不硬编码（每个跟踪的 SDK 密钥与客户端 ID）

### 3. 环境变量约定

检查项目如何处理配置：

- **`.env:`**：如果堆栈使用 dotenv（或您为 LaunchDarkly 引入了它），计划在集成根目录下创建 `.env`（如果缺失），然后添加 `LAUNCHDARKLY_SDK_KEY`、`LAUNCHDARKLY_CLIENT_SIDE_ID` / 捆绑器前缀客户端 ID，或 `LAUNCHDARKLY_MOBILE_KEY`（参见 [应用代码变更](../apply/SKILL.md) 步骤 2 的名称、在真实值之前获取同意和服务器+客户端混合情况）。计划验证 `.gitignore` 包含该根目录下的 `.env`（如果缺失，则添加条目，权限与其他仓库编辑相同）。
- **`.env.example` / `.env.sample:`**：如果存在，计划仅添加占位符条目（无真实密钥）。
- **配置模块或 `process.env:`**：如果项目不使用 `.env`，计划遵循现有的密钥模式。

## 展示计划

在进行任何更改之前，向用户总结计划。

**单个 SDK:**

1. 使用 `[包名]` 安装 `[安装命令]`
2. 将 SDK 依赖添加到 `[依赖文件]`
3. 在 `[入口点文件]` 中添加导入和初始化
4. 将 `[环境变量]` 添加到 `.env`（如果缺失则创建；用户同意后的真实值）
5. 确保 `.env` 在 `.gitignore` 中
6. 如果项目使用，在 `.env.example` 中添加占位符

除非用户明确批准其他依赖项更改，否则将仅添加 LaunchDarkly SDK 包。

**双重 SDK：** 以编号格式 **分别** 为每个跟踪呈现（例如，“服务器端：”步骤 1-7，然后“客户端：”步骤 1-7），遵循 [双重 SDK 集成](#dual-sdk-integrations)。不要省略第二个跟踪。

展示计划后：

**D6 -- 非阻塞（除非反对）：** 向用户展示计划摘要，并附带类似“我要做什么——如果看起来有问题请说停止或告诉我”的注释。然后 **继续进入 [应用代码变更](../apply/SKILL.md)** 而不等待明确批准。如果用户反对或说看起来有问题，请停止并调整计划，然后再继续。

这故意设计为非阻塞，以减少仪式。计划对用户可见，他们可以在任何时候中断。真正的安全门是 D7（密钥同意）和 D8（非 LD 依赖项更改）在应用步骤中。

如果入口点不明确或多个 SDK 适用，这些问题 **是** 阻塞的——使用您的结构化问题工具作为计划展示的一部分提问，并在获得答案之前等待再继续。

**不要** 作为计划确认的一部分请求 SDK 密钥、客户端 ID 或移动密钥——父流程在 [应用代码变更](../apply/SKILL.md) 中收集这些。上面的 **密钥类型** 列仅用于技术规划，不是提示密钥。

**不要** 承诺或暗示您将升级无关依赖项以满足最新的 SDK——[应用](../apply/SKILL.md) 要求在 **明确同意** 之前进行任何非 LaunchDarkly 包更改。

---

**完成时：** [应用代码变更](../apply/SKILL.md)
