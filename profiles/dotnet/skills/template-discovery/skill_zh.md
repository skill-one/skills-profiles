# 模板发现

这项技能帮助代理使用 `dotnet new` 命令行工具的搜索、列表和参数检查功能，为给定任务找到、检查并选择合适的 `dotnet new` 模板。

## 使用场景

- 用户询问“X 可用哪些模板？”
- 用户用自然语言描述项目（“我需要一个带认证的 Web API”）
- 用户在创建项目前想比较模板或了解参数
- 用户在提交前需要知道模板会生成什么（文件、结构）

## 不适用场景

- 用户想创建项目 — 路由到 `template-instantiation` 技能
- 用户想编写或验证自定义模板 — 路由到 `template-authoring` 技能
- 用户需要模板的详细并排比较 — 路由到 `template-comparison` 技能
- 用户在创建时需要智能跨参数默认值 — 路由到 `template-smart-defaults` 技能
- 用户在排查构建问题 — 路由到 `dotnet-msbuild` 插件

> **建议请求：先回答，后确认。检查请求：先检查。** 对于一般的“哪个模板？”问题，从步骤 1 映射开始，以便暂时的 CLI 失败不会让用户没有答案。当用户明确询问已安装内容、请求确切选项/默认值或请求干运行输出时，在写出最终答案前运行相关的 `dotnet new` 命令。永远不要在 `dotnet new` 调用或“让我确认……”的提示语上结束回合。

> **检查请求需要检查。** 如果用户询问已安装选项、确切参数/默认值、兼容性约束或确切的干运行文件列表，运行相应的 `dotnet new` 命令。不要用记住的标志替换观察到的数据。只有在当前模板的 `--help` 输出包含它时才报告标志。

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 用户意图或关键词 | 是 | 自然语言描述或关键词（例如，“Web API”、“控制台应用”、“MAUI”） |
| 语言偏好 | 否 | C#、F# 或 VB — 默认为 C# |
| 框架偏好 | 否 | 目标框架（例如，net10.0、net9.0） |

## 工作流程

> 对于建议，使用步骤 1，然后使用步骤 2-4。对于明确的检查请求，先执行请求的检查，并将步骤 1 仅作为后备使用。

### 步骤 1：将意图映射到模板候选

使用这些映射将用户的自然语言描述映射到模板简短名称和参数。

**意图 → 模板简短名称：**

| 意图/短语 | 模板简短名称 |
|---|---|
| web api, web service, rest api, restful, api, minimal api | `webapi` |
| web app, web application | `webapp`, `blazorserver` |
| mvc | `mvc` |
| razor, razor pages | `webapp` |
| blazor, blazor web app | `blazor` |
| blazor server | `blazorserver` |
| blazor wasm, blazor webassembly | `blazorwasm` |
| grpc | `grpc` |
| signalr | `webapi`, `webapp` |
| console, console app, command line, cli | `console` |
| worker, background service, daemon, windows service | `worker` |
| class library, library, lib, nuget package | `classlib` |
| maui, mobile, cross-platform app, ios, android | `maui` |
| desktop | `maui`, `wpf`, `winforms` |
| wpf | `wpf` |
| winforms, windows forms | `winforms` |
| winui, winui3 | `winui3` |
| test, unit test | `xunit`, `nunit`, `mstest` |
| xunit / nunit / mstest | `xunit` / `nunit` / `mstest` |
| solution | `sln` |
| aspire, .net aspire | `aspire-starter`, `aspire` |
| azure functions, function app, serverless | `func` |
| orleans | `orleans` |
| razor component, web component | `razorcomponent` |
| razor class library | `razorclasslib` |
| gitignore / editorconfig / nuget config / global json | `gitignore` / `editorconfig` / `nugetconfig` / `globaljson` |

**关键词 → 参数：**

| 关键词/短语 | 参数 | 值 |
|---|---|---|
| authentication, auth, individual auth, individual accounts | `--auth` | `Individual` |
| windows auth | `--auth` | `Windows` |
| azure ad, entra id | `--auth` | `SingleOrg` |
| no auth, no authentication | `--auth` | `None` |
| controllers, with controllers | `--use-controllers` | (标志) |
| minimal api | (默认) | — |
| aot, native aot | `--aot` | (标志) |
| docker, container | 模板的 Docker/容器选项 | 模板不同 — 使用 `--help` 确认（并非所有模板都暴露此选项） |
| net8 / .net 8 / dotnet 8 | `--framework` | `net8.0` |
| net9 / .net 9 / dotnet 9 | `--framework` | `net9.0` |
| net10 / .net 10 / dotnet 10 | `--framework` | `net10.0` |

这些都是初步猜测。始终使用 `dotnet new <template> --help` 确认实际的参数名称/选项，因为参数名称因模板而异（例如，`--auth` 对 `--Authentication`）。

一些映射的简短名称不在默认 SDK 安装中 — 像是 `maui`、`winui3`、`aspire-starter`/`aspire`、`func` 和 `orleans` 这样的模板通常需要工作负载 (`dotnet workload install <id>`) 和/或额外的模板包 (`dotnet new install <package>`)。如果一个映射的简短名称没有出现在 `dotnet new list` 中，则回退到 `dotnet new list`/`dotnet new search` 找到正确的模板和提供它的包/工作负载，然后再建议它。

> **韧性 — 即使 CLI 失败也要回答。** 上述意图映射本身就是一个可用的答案。按顺序、一次一次地运行 `dotnet new` 命令 — 模板引擎使用全局互斥锁，因此同时发出多个 `dotnet new <template> --help`/`--dry-run` 调用可能会产生暂时的“互斥锁”/“持久性”错误和空输出。如果命令失败，重试一次；如果仍然失败，**回退到步骤 1 的意图映射，并给用户一个具体的建议**，注明确切的参数名称/选项无法通过 CLI 确认。因为 CLI 调用出错而没有任何答案的情况永远不要发生。

### 步骤 2：搜索模板

使用 `dotnet new search` 通过关键词在本地安装的模板和 NuGet.org 中查找模板：

```bash
dotnet new search blazor
```

使用 `dotnet new list` 仅显示已安装的模板，并可选过滤：

```bash
dotnet new list --language C# --type project
dotnet new list web
```

如果用户明确要求你检查已安装的模板和 NuGet.org，即使 SDK 已经包含合适的模板，也要运行并报告两种搜索。区分内置选择和可安装替代方案：

- 对于 SDK 内置的模板，说 **“无需安装 — 随 SDK 提供”**，不要编造包要求。
- 对于每个相关的 NuGet 结果，从实际搜索输出中复制包 ID，并给出 `dotnet new install <package-id>`。
- 如果 NuGet 搜索没有返回可信的替代方案，要明确说明；本地匹配仍然可以回答请求。

### 步骤 3：检查模板详情

使用 `dotnet new <template> --help` 获取特定模板的完整参数详情 — 参数名称、类型、默认值和允许的值：

```bash
dotnet new webapi --help
```

将观察到的选项名称、选择、默认值和兼容性说明复制到答案中。例如，Windows 服务支持并非所有工作模板标志都通用。如果已安装的 `worker --help` 没有暴露一个，就说这种情况，并区分模板创建与创建后托管配置；永远不要编造 `--windows` 或 `--use-windows-service`。

### 步骤 4：预览输出

使用 `dotnet new <template> --dry-run` 显示模板在不写入磁盘的情况下会创建哪些文件和目录：

```bash
dotnet new webapi --name MyApi --auth Individual --dry-run
```

如果干运行失败（暂时的“互斥锁”/“持久性”错误），重试一次；如果仍然失败，给出一个**代表性**的结构（模板 *系列* 和典型文件类型），并注明未通过 CLI 确认。不要编造具体值、选择或文件路径。当干运行**成功**时，保留其输出中的每个实际路径。对于长列表，将那些路径渲染为目录树，而不是平铺的完整路径墙；不要省略或编造条目。按树形结构逐行解释每个关键入口点的用途（例如 `Program.cs`、`App.razor` 和项目文件）。没有这些解释的文件列表是不完整的。

如果命令执行不可用，不要在“你自己运行这个”上停止。给出已知模板系列的代表性树形结构和关键文件解释，并明确标记为未确认，以便用户仍然获得有用的预览。

如果用户说不创建文件，每个可复制粘贴的创建命令必须包含 `--dry-run`。即使你没有亲自执行，一个纯 `dotnet new ...` 命令也与该请求相矛盾。

### 步骤 5：呈现结果

**先以一个可运行的命令作为答案开头**，然后进行解释。必须的格式：

> **使用 `<template>`** — 一行说明原因。
> ```bash
> dotnet new <template> --name <Name> [--key params]
> ```

然后添加支持性细节：
- 关键参数和推荐值（带选择，例如 `--auth`: None | Individual | SingleOrg | Windows）
- 预期结果（创建的文件、项目结构）
- 任何先决条件 — 指出**确切的包要安装** (`dotnet new install <id>`)，或对于内置模板说 **“无需安装 — 随 SDK 提供”**

没有具体、可复制粘贴的命令的答案会使这项技能与纯回复相同 — 始终给出下一步要运行的命令。

## 验证

- [ ] 至少为用户的意图找到了一个模板匹配
- [ ] 模板参数用类型和默认值解释
- [ ] 用户在创建前理解了模板会生成什么
- [ ] 确切选项的声明来自此模板的 `--help` 输出
- [ ] 必须不创建文件的仅建议性命令包含 `--dry-run`

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 因为本地模板存在而跳过明确请求的 NuGet 搜索 | 运行 `dotnet new list <keyword>` 和 `dotnet new search <keyword>`，然后将内置模板与真正的可安装替代方案区分开来。 |
| 当没有本地模板匹配时不搜索 NuGet | 使用 `dotnet new search <keyword>` 查找 NuGet.org 上的可安装模板。 |
| 没有检查模板约束 | 一些模板需要特定的 SDK 或工作负载。使用 `dotnet new <template> --help` 在建议前暴露约束。 |
| 在预览输出前推荐模板 | 始终使用 `dotnet new <template> --dry-run` 确认模板会生成用户期望的内容。 |
| `dotnet new` 调用因“互斥锁”/“持久性”错误失败且你没有返回任何内容 | 这些是暂时的（通常来自并发调用）。按顺序、一次一次地运行 `dotnet new` 命令，重试一次，然后回退到步骤 1 的意图映射，并仍然给用户一个具体的答案。 |
| 从其他 SDK/模板猜测 Windows 服务或 AOT 标志 | 仅引用在 `dotnet new <template> --help` 中观察到的选项；否则解释创建后的路径。 |

## 更多信息

- [dotnet new 模板](https://learn.microsoft.com/dotnet/core/tools/dotnet-new-sdk-templates) — 内置模板参考
- [模板引擎维基](https://github.com/dotnet/templating/wiki) — 模板引擎内部结构
