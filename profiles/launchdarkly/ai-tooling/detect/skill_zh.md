# 检测仓库堆栈 (SDK 安装)

在安装任何东西之前，你必须理解这个项目。识别项目是用什么构建的，以及 LaunchDarkly 是否已经存在。

这项技能嵌套在 [LaunchDarkly SDK 安装 (onboarding)](../SKILL.md) 下；父级 **步骤 1** 是 **检测**。**下一步：** [生成集成计划](../plan/SKILL.md)，除非决策树将你引向其他地方。

### 1. 语言和框架

查找以下指示文件（以及相关的根布局），然后阅读相关的清单文件以推断语言和框架。

查找这些文件以识别堆栈：

| 文件 | 语言/框架 |
|------|--------------------|
| `package.json` | JavaScript/TypeScript (检查 React, Next.js, Vue, Angular, Express, React Native, Electron 等) |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python (检查 Django, Flask, FastAPI) |
| `go.mod` | Go (检查 Gin, Echo, Fiber, Chi) |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java/Kotlin (检查 Spring, Quarkus, Android) |
| `Gemfile` | Ruby (检查 Rails, Sinatra) |
| `*.csproj`, `*.sln`, `*.fsproj` | .NET/C# (检查 ASP.NET, MAUI, Xamarin, WPF, UWP) |
| `composer.json` | PHP (检查 Laravel, Symfony) |
| `Cargo.toml` | Rust (检查 Actix, Axum, Rocket) |
| `pubspec.yaml` | Flutter/Dart |
| `Package.swift`, `Podfile`, `*.xcodeproj` | Swift/iOS |
| `AndroidManifest.xml` | Android (也检查 `build.gradle` 中的 `com.android`) |
| `rebar.config`, `mix.exs` | Erlang/Elixir |
| `CMakeLists.txt`, `Makefile` (带有 C/C++ 模式) | C/C++ (检查 `#include` 模式) |
| `*.cabal`, `stack.yaml` | Haskell |
| `*.lua`, `rockspec` | Lua |
| `manifest`, `*.brs` | Roku (BrightScript) |
| `wrangler.toml` | Cloudflare Workers (边缘 SDK) |
| `vercel.json` 带有边缘函数 | Vercel Edge (边缘 SDK) |

阅读依赖文件以识别特定的框架。对于 `package.json`，检查 `dependencies` 和 `devDependencies`。

如果你无法识别语言或框架：

**D5 -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："我无法检测项目的语言或框架。你想使用哪个 SDK？"
- 选项：将 [SDK 配方](../../references/sdk/recipes.md) 中的可用 SDK 呈现为可选选项。
- 停止。不要将问题作为文本写入。直到用户选择选项之前，不要继续。

### 2. 包管理器

识别项目如何安装依赖项：

| 指示器 | 包管理器 |
|-----------|----------------|
| `package-lock.json` | npm |
| `yarn.lock` | yarn |
| `pnpm-lock.yaml` | pnpm |
| `bun.lockb` | bun |
| `Pipfile.lock` | pipenv |
| `poetry.lock` | poetry |
| `go.sum` | Go 模块 |
| `Gemfile.lock` | bundler |

使用检测到的包管理器进行所有安装命令。如果存在多个锁文件，优先选择最近修改的文件。

### 3. 单一仓库布局

一些仓库托管多个包或服务。查找这些指示器：

| 文件 / 模式 | 工具或布局 |
|----------------|----------------|
| `pnpm-workspace.yaml` | pnpm 工作区 |
| `lerna.json` | Lerna |
| `nx.json` | Nx |
| `turbo.json` | Turborepo |
| `rush.json` | Rush |
| `packages/` 目录带有多个 `package.json` 文件 | 通用单一仓库 |

当任何这些适用时，**不要假设仓库根目录是集成目标**：

**D5 -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："这是一个单一仓库。我应该将 LaunchDarkly 集成到哪个包、应用程序或服务中？"
- 选项：列出发现的包/应用程序作为可选选项。
- 停止。不要将问题作为文本写入。直到用户选择选项之前，不要继续。

然后运行此检测步骤的其余部分——语言、包管理器、入口点和 SDK 搜索——**在该目标目录**（及其子树）中，而不仅仅是在根目录。

### 4. 应用程序入口点

找到应用程序开始的主要文件。在单一仓库中，在 [第 3 节 单一仓库布局](#3-monorepo-layout) 之后，在选择的包内应用以下模式。常见模式：

- **Node.js (服务器)**：检查 `package.json` `"main"` 字段，或者查找 `index.js`、`server.js`、`app.js`、`src/index.ts`
- **NestJS**：查找 `src/main.ts` 或 `src/main.js`
- **Python**：查找 `app.py`、`main.py`、`manage.py`、`wsgi.py`，或者 `[tool.poetry.scripts]` 部分
- **Go**：查找 `main.go` 或 `cmd/*/main.go`
- **Java**：搜索 `public static void main` 或 `@SpringBootApplication`
- **Ruby**：查找 `config.ru`、`config/application.rb`
- **React/Vue/Angular**：查找 `src/index.tsx`、`src/main.tsx`、`src/App.tsx`、`src/main.ts`
- **Next.js**：应用路由器——`app/layout.tsx` 或 `app/layout.js`（根布局）。页面路由器——`pages/_app.tsx` 或 `pages/_app.js`
- **React Native**：查找 `App.tsx`、`App.js`、`index.js`（带有 `AppRegistry.registerComponent`）
- **Electron**：检查 `package.json` `"main"`；常见路径包括 `main.js` 或 `src/main.ts`
- **JavaScript (浏览器)**：查找 `index.html`、`src/index.js`，或者 `webpack.config.js` / `vite.config.ts` 中的捆绑器入口点
- **Flutter**：查找 `lib/main.dart`
- **Swift/iOS**：查找 `AppDelegate.swift`、`SceneDelegate.swift` 或 `@main` 结构
- **Android**：查找 `MainActivity.java` 或 `MainActivity.kt`

### 5a. 分类工作区置信度

在第 1-4 节之后，在继续之前将工作区分类为**三种状态之一**。此分类决定其余流程的进行方式。

| 状态 | 含义 | 标准 |
|-------|---------|----------|
| **清晰的应用程序** | 发现了一个可运行的应用程序 | 检测到语言/框架，存在真实的入口点，依赖清单中存在应用程序依赖项 |
| **不明确 / 弱证据** | 某些东西存在，但它并不明显地代表一个可运行的应用程序 | 随机或最小的 `package.json`（例如，只有 devDependencies，没有脚本）、隔离的配置/清单文件、主题或仅配置的文件夹、token/测试 JSON、没有相应源文件的锁文件，或者多个冲突的指示器，没有主导的应用程序结构 |
| **未找到应用程序** | 未检测到可识别的应用程序结构 | 没有依赖清单，没有入口点，没有匹配已知模式的源文件，或者工作区为空 / 只包含文档 |

**弱证据不得被视为确认。** 弱证据的示例：

- 一个没有 `scripts` 部分且没有应用程序源文件的 `package.json`
- 一个在数据文件或笔记本目录中的孤独的 `requirements.txt`
- 配置、主题或测试目录中的清单文件不代表可运行的服务
- 单一仓库根目录，其中真实的应用程序位于子目录中，但没有选择

**状态分支：**

- **清晰的应用程序** → 继续到 [第 6 节 现有的 LaunchDarkly SDK](#6-existing-launchdarkly-sdk) 然后确认 SDK。

- **不明确 / 弱证据:**

**D5-UNCLEAR -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："我发现了某些项目文件，但我不确定我已识别出正确的应用程序进行集成。你能指给我正确的应用文件夹吗？"
- 上下文：简要描述你发现了什么以及为什么它具有歧义（例如，“根目录有一个 `package.json`，但它没有启动脚本和应用程序源文件”）。
- 选项：
  - 呈现你检测到的任何候选文件夹作为可选选项
  - "它在其他地方——我会告诉你路径"
  - "还没有应用程序——帮助我创建一个演示"
- 停止。不要进行代码更改、安装包或生成集成计划，直到用户确认目标。直到用户选择选项之前，不要继续。

在用户指向正确的文件夹后，重新运行检测（第 1-4 节），范围限定在该文件夹。

- **未找到应用程序:**

明确告诉用户："我在这个工作区中没有找到可运行的应用程序。" 然后提供两条路径：

**D5-NOAPP -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："我在这个工作区中没有找到可运行的应用程序。你想如何继续？"
- 选项：
  - "指给我正确的文件夹——应用程序在别处"
  - "创建一个最小的演示应用程序，以便我尝试 LaunchDarkly"
- 停止。直到用户选择选项之前，不要继续。

如果用户选择"指给我正确的文件夹"，重新运行检测，范围限定在用户提供的路径。如果他们选择"创建一个演示应用程序"，在**新的子文件夹**（例如 `launchdarkly-demo/`）中创建一个最小的可运行应用程序，使用最简单的堆栈（Node.js + Express 或静态 HTML 页面是很好的默认值），然后从该子文件夹继续检测。

**不要**在应用程序目标已确认且应用程序实际上可以运行之前宣布 onboarding 完成。

### 6. 现有的 LaunchDarkly SDK

搜索代码库以查找现有的 LaunchDarkly 使用情况：

```
搜索：launchdarkly, ldclient, ld-client, LDClient, @launchdarkly, launchdarkly-
```

检查：

- SDK 是否已经在依赖文件中？
- 是否有初始化代码？
- 是否已正确配置或部分设置？
- 是否已有现有的功能标志评估？

## SDK 确认

检测堆栈后，使用户确认 SDK 选择：

- **如果有一个 SDK 显然是正确的选择**：呈现你的建议并获取确认：

**D5 -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："根据我所发现的，我建议使用 [SDK 名称] SDK。看起来对吗？"
- 选项：
  - "是，使用该 SDK 继续" -> 继续到计划
  - "不是，我想用不同的一个" -> 让用户指定
- 停止。不要将问题作为文本写入。直到用户选择选项之前，不要继续。

- **如果有多个 SDK 可能适用**（例如，一个具有服务器和客户端组件的 Next.js 项目）：
  - **如果用户已经要求两者**（例如，“前端和后端”、“服务器 + 浏览器”、“API 和 SPA”）：将此视为 **双 SDK** 范围。继续到 [生成集成计划](../plan/SKILL.md) 并在 **两者** 的范围内——**不要** 计划或实现一个，并假设另一个是“涵盖的”。
  - **如果范围不明确**：

**D5 -- BLOCKING:** 现在调用你的结构化问题工具。
- 问题："这个项目具有服务器端和客户端界面。你想集成哪一个？"
- 选项：
  - "仅服务器端"
  - "仅客户端端"
  - "服务器端和客户端"
- 停止。不要将问题作为文本写入。直到用户选择选项之前，不要继续。

如果他们选择 **两者**，计划必须包括 **两个** 具体的集成（见 [计划：双 SDK 集成](../plan/SKILL.md#dual-sdk-integrations)）。

- **如果你无法确定正确的 SDK**：在你的问题工具中呈现来自 [SDK 配方](../../references/sdk/recipes.md) 的可用选项作为可选选项，并使用上述阻塞模式。

## 决策树

检测和确认后：

- **未找到应用程序或不明确** --> 已通过 D5-NOAPP / D5-UNCLEAR 在 [第 5a 节](#5a-classify-workspace-confidence) 处理。直到用户确认真实的应用程序目标之前，不要继续到计划。
- **SDK 已安装并初始化** --> 跳到父级技能的 [步骤 4：第一个标志](../../SKILL.md#step-4-first-flag)
- **SDK 已安装但未初始化** --> 跳到 [应用代码更改](../apply/SKILL.md)（只需添加初始化代码）
- **SDK 未存在** --> 继续到 [生成集成计划](../plan/SKILL.md)
- **检测到多个目标（例如，前端 + 后端）** --> 如果用户想要 **两者** 的 SDK（通过 D5 确认），继续到 [生成集成计划](../plan/SKILL.md) 并具有 **双 SDK** 范围（两个包，两个入口点）。如果他们只想一个界面，计划该单个 SDK。
- **未检测到语言** --> 已通过 [第 1 节](#1-language-and-framework) 中的 D5 阻塞问题处理。

---

**完成时（正常路径）：** [生成集成计划](../plan/SKILL.md)
