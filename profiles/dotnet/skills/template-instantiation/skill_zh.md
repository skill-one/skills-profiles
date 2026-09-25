# 模板实例化

这项技能使用 `dotnet new` 命令行工具从模板创建 .NET 项目，并提供参数验证、中央包管理适应和多项目组合的指导。

> **匹配工作区，然后停止。** 最重要的操作是将新项目与它所在仓库进行对齐：检测 **中央包管理 (CPM)** (`Directory.Packages.props`) 以及邻近 `.csproj` 文件使用的 **目标框架**，并镜像两者。**将发现的目標框架视为显式选择** — 将其作为 `--framework` 传递，这样 `template-smart-defaults` 就不会覆盖它；只有在它与请求的功能不兼容时才进行偏离（然后向用户标记冲突）。尽可能少地执行这些步骤——通常一个 `--dry-run`、创建操作以及一次 `dotnet build` 来确认就足够了。额外的探索性步骤会增加成本而没有改善结果。

> **执行请求的创建。** 不要只返回一个计划或意向声明。
> 按顺序运行依赖于状态的命令：检查、干运行、创建，然后构建。永远不要并行启动创建和构建；创建前的构建竞争会产生一个错误失败。

| 情况 | 必要操作 |
|------|----------|
| 简单独立项目 | 仅检查请求的模板，在确切路径创建，然后构建 |
| 现有的邻近项目 | 首先读取它们的 TFM，并显式传递匹配的受支持的 `--framework` |
| 发现 `Directory.Packages.props` | 当支持时使用 `--no-restore` 创建，规范化生成的包引用，然后一次恢复/构建 |
| 多项目解决方案 | 在最终路径创建每个项目，添加引用，将所有项目添加到解决方案，然后一次构建解决方案 |
| 用户显式请求 `.sln` | 检查 `dotnet new sln --help`；当支持时传递 `--format sln`，否则使用旧 SDK 的默认 `.sln` 输出 |

不要预测生成的目标框架。如果用户和工作区没有提供，检查 `dotnet new <template> --help`，选择一个受支持值（通常是它的文档默认值），显式传递它，然后确认生成的 `.csproj`。永远不要宣布一个基于模板当前选择没有根据的中继框架猜测。

## 何时使用

- 用户请求创建新的 .NET 项目、应用或服务
- 用户需要一个包含多个项目（API + 测试 + 库）的解决方案
- 用户希望创建一个尊重现有 `Directory.Packages.props` 的项目
- 用户需要安装或管理模板包

## 何时不用

- 用户正在寻找模板——路由到 `template-discovery` 技能；为了进行详细的逐个比较——路由到 `template-comparison` 技能
- 用户想要编写自定义模板——路由到 `template-authoring` 技能
- 用户想要向现有项目添加包——直接使用 `dotnet add package`

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 模板名称或意图 | 是 | 模板的简短名称（例如，`webapi`）或自然语言描述 |
| 项目名称 | 是 | 创建项目的名称 |
| 输出路径 | 推荐 | 项目应创建的目录 |
| 参数 | 否 | 模板特定参数（例如，`--framework`、`--auth`、`--aot`） |

## 工作流程

### 第 1 步：解析模板和参数

如果用户提供了一个自然语言描述，将其映射到模板简短名称（参见 `template-discovery` 技能中的关键词表）。如果他们提供了一个模板名称，直接进行。

使用 `dotnet new <template> --help` 来查看用户未指定的任何参数的可用参数、默认值和类型。

当用户选择的参数隐含了未设置的 *相关* 参数的值时，**调用 `template-smart-defaults` 技能** 来在组装命令行之前解决这个差距——例如，原生 AOT 意味着需要一个较新的支持 AOT 的目标框架，非 `None` 的 `--auth` 选择意味着 HTTPS 必须保持启用（不要添加 `--no-https`），`--use-controllers` 排除了最小 API 选项。智能默认值仅填充差距；永远不要让它们覆盖用户显式设置的值。在第 2 步中发现的工 作区框架被视为这样一个显式值——将其作为选择的 `--framework` 传递给智能默认值，这样它就不会被视为一个未设置的差距；只有在它与请求的功能/模板不兼容时才偏离（然后向用户显示冲突）。

### 第 2 步：分析工作区

在创建之前检查现有的解决方案结构：
- 中央包管理 (CPM) 是否启用？查找 `Directory.Packages.props`
- 使用哪些目标框架？检查现有的 `.csproj` 文件
- 是否有 `global.json` 固定 SDK？

这确保了新项目与工作区一致。

### 第 3 步：预览创建

使用 `dotnet new <template> --dry-run` 向用户展示将要创建的文件。确认后再进行。

```bash
dotnet new webapi --name MyApi --framework net10.0 --dry-run
```

### 第 4 步：创建项目

使用 `dotnet new` 和模板名称以及所有参数：

```bash
dotnet new webapi --name MyApi --output ./src/MyApi --framework net10.0 --auth Individual
```

在运行它之前，发出一条紧凑的决定行：

`Creating <template> at <path>; framework=<value> (<user|workspace|template>); CPM=<on|off>.`

这使工作区适应变得明确，而不会增加一个长报告。

#### 常见参数组合

| 模板 | 参数 | 示例 |
|------|------|------|
| `webapi` | `--auth` (None, Individual, SingleOrg, Windows)、`--aot` (原生 AOT) | `dotnet new webapi -n MyApi --auth Individual --aot` |
| `webapi` | `--use-controllers` (使用控制器与最小 API) | `dotnet new webapi -n MyApi --use-controllers` |
| `blazor` | `--interactivity` (None, Server, WebAssembly, Auto)、`--auth` | `dotnet new blazor -n MyApp --interactivity Server` |
| `grpc` | `--aot` (原生 AOT) | `dotnet new grpc -n MyService --aot` |
| `worker` | `--aot` (原生 AOT) | `dotnet new worker -n MyWorker --aot` |

注意：使用 `dotnet new <template> --help` 查看任何模板的所有可用参数。

创建后，适应中央包管理并刷新过时的版本：

1. **创建前检测 CPM** — 从目标路径向上查找 `Directory.Packages.props`。
2. **避免注定失败的自动恢复** — 当 CPM 处于活动状态且模板暴露 `--no-restore` 时，在创建时传递它，以便包集中化首先发生。
3. **移除内联版本** — 对于每个生成的 `<PackageReference Include="X" Version="Y" />`，移除 `Version` 属性（留下 `<PackageReference Include="X" />`）。
4. **集中版本** — 在 `Directory.Packages.props` 中添加或合并一个 `<PackageVersion Include="X" Version="Y" />` 条目；保留无关的现有条目。
5. **可选地刷新过时的模板默认版本** — 模板经常硬编码旧版本。默认保留模板的版本（对可重复性和受控升级最安全）。只有在用户请求时才刷新，并且当你这样做时：
   - 优先使用工具驱动流程：运行 `dotnet list package --outdated` 并在更改任何内容之前与用户确认建议的更新。
   - 限制升级到相同的 **主**（或主/次）版本，除非用户明确选择更大的升级，因为跨主版本升级可能会引入破坏性更改。
   - 当概念上检查某个包的最新 **稳定** 版本时，该包 ID 的 NuGet V3 平面容器 `index.json` 端点列出了发布版本；永远不要选择预发布版本，除非请求。
6. **构建** — 运行 `dotnet build` 一次以恢复并确认集中化/刷新的版本解决。

### 第 5 步：多项目组合（可选）

对于复杂结构，按顺序创建每个项目并将它们连接起来：

```bash
dotnet new webapi --name MyApi --output ./src/MyApi
dotnet new xunit --name MyApi.Tests --output ./tests/MyApi.Tests
dotnet add ./tests/MyApi.Tests reference ./src/MyApi
dotnet sln add ./src/MyApi ./tests/MyApi.Tests
```

### 第 6 步：模板包管理

安装或卸载模板包：

```bash
dotnet new install Microsoft.DotNet.Web.ProjectTemplates.10.0
dotnet new uninstall Microsoft.DotNet.Web.ProjectTemplates.10.0
```

### 第 7 步：创建后验证

1. 验证项目可以构建：`dotnet build`
2. 对于可运行的模板（如 `console`），当请求简单且不需要外部服务时，运行生成的应用程序；报告观察到的输出而不是仅构建成功。
3. 如果添加到解决方案中，验证解决方案级别的 `dotnet build`
4. 如果 CPM 被适应，验证 `Directory.Packages.props` 有新的条目

## 验证

- [ ] 项目成功创建并包含预期文件
- [ ] 项目使用 `dotnet build` 可以干净构建
- [ ] 如果 CPM 处于活动状态，`.csproj` 没有版本属性，`Directory.Packages.props` 有匹配条目
- [ ] 项目中的包版本是最新的（不是过时的模板默认值）
- [ ] 如果是多项目，所有项目都正确构建并相互引用

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 创建项目前未检查 CPM | 如果存在 `Directory.Packages.props`，`dotnet new` 创建的项目会与内联版本冲突。创建后，将版本移动到 `Directory.Packages.props` 并从 `.csproj` 中移除它们。 |
| 在适应 CPM 之前让模板恢复失败 | 首先检测 CPM 并在可用时使用模板的 `--no-restore` 选项；在第一次恢复/构建之前集中版本。 |
| 未指定框架创建项目 | 当模板支持多个 TFM 时，始终指定 `--framework` 以避免默认为旧版本。 |
| 未将项目添加到解决方案 | 创建后，运行 `dotnet sln add` 将项目包含到解决方案中。 |
| 未验证项目构建 | 创建后始终运行 `dotnet build` 以尽早捕获缺少依赖项或参数问题。 |

## 更多信息

- [中央包管理](https://learn.microsoft.com/nuget/consume-packages/central-package-management) — CPM 文档
- [dotnet new](https://learn.microsoft.com/dotnet/core/tools/dotnet-new) — 命令行参考
