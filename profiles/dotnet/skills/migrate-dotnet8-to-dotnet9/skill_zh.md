# .NET 8 → .NET 9 迁移

将 .NET 8 项目或解决方案迁移到 .NET 9，系统性地解决所有破坏性变更。结果是一个目标为 `net9.0` 的项目，该项目可以干净地构建、通过测试，并涵盖 .NET 9 发布中引入的所有行为变化、源不兼容变化和二进制不兼容变化。

## 何时使用

- 将 `TargetFramework` 从 `net8.0` 升级到 `net9.0`
- 更新 .NET 9 SDK 后解决构建错误或新警告
- 适应 .NET 9 运行时、ASP.NET Core 9 或 EF Core 9 中的行为变化
- 替换 `BinaryFormatter` 使用（现在在运行时始终抛出异常）
- 更新 .NET 9 的 CI/CD 管道、Dockerfile 或部署脚本

## 何时不使用

- 项目已经目标为 `net9.0` 且可以干净构建——迁移已完成。如果目标是达到 `net10.0`，请使用 `migrate-dotnet9-to-dotnet10` 技能作为下一步。
- 从 .NET 7 或更早版本升级——首先解决先前的版本破坏性变更
- 从 .NET Framework 迁移——这是一个单独的、更大的工作
- 从 .NET 9 开始的绿场项目（无需迁移）

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------|
| 项目或解决方案路径 | 是 | 要迁移的 `.csproj`、`.sln` 或 `.slnx` 入口点 |
| 构建命令 | 否 | 如何构建（例如，`dotnet build`，一个仓库构建脚本）。如果未提供，将自动检测 |
| 测试命令 | 否 | 如何运行测试（例如，`dotnet test`）。如果未提供，将自动检测 |
| 项目类型提示 | 否 | 项目是否使用 ASP.NET Core、EF Core、WinForms、WPF、容器等。如果未提供，将根据 PackageReferences 和 SDK 属性自动检测 |

## 工作流

> **直接从加载的参考文档中回答。** 不要搜索文件系统或获取网页以获取破坏性变更信息——参考文档包含权威详细信息。专注于识别哪些破坏性变更适用，并提供具体的修复方法。
>
> **提交策略：** 在每个逻辑边界处提交——更新 TFM（步骤 2）后、解决构建错误（步骤 3）后、解决行为变化（步骤 4）后、更新基础设施（步骤 5）后。这使每个提交保持专注且可审查。

### 步骤 1：评估项目

1. 确定项目如何构建和测试。查找构建脚本、`.sln`/`.slnx` 文件或单独的 `.csproj` 文件。
2. 运行 `dotnet --version` 以确认已安装 .NET 9 SDK。如果没有安装，停止并通知用户。
3. 通过检查以下内容来确定项目使用的技术领域：
   - **SDK 属性**：`Microsoft.NET.Sdk.Web` → ASP.NET Core；`Microsoft.NET.Sdk.WindowsDesktop` 与 `<UseWPF>` 或 `<UseWindowsForms>` → WPF/WinForms
   - **PackageReferences**：`Microsoft.EntityFrameworkCore.*` → EF Core；`Microsoft.Extensions.Http` → HttpClientFactory
   - **Dockerfile 存在** → 与容器相关的变更相关
   - **P/Invoke 或原生互操作使用** → 与互操作相关的变更相关
   - **`BinaryFormatter` 使用** → 需要序列化迁移
   - **`System.Text.Json` 使用** → 与序列化相关的变更相关
   - **X509Certificate 构造函数** → 与加密相关的变更相关
4. 记录哪些参考文档是相关的（见步骤 3 中的参考加载表）。
5. 对当前 `net8.0` 目标进行**清理构建**（`dotnet build --no-incremental` 或删除 `bin`/`obj`）以建立干净的基线。记录任何现有警告。

### 步骤 2：更新目标框架

1. 在每个 `.csproj`（如果集中化，则为 `Directory.Build.props`），将：
   ```xml
   <TargetFramework>net8.0</TargetFramework>
   ```
   更改为：
   ```xml
   <TargetFramework>net9.0</TargetFramework>
   ```
   对于多目标项目，将 `net9.0` 添加到 `<TargetFrameworks>` 或替换 `net8.0`。

2. 更新所有 `Microsoft.Extensions.*`、`Microsoft.AspNetCore.*`、`Microsoft.EntityFrameworkCore.*` 和其他 Microsoft 软件包引用到它们的 9.0.x 版本。如果使用中央软件包管理（`Directory.Packages.props`），请在那里更新版本。

3. 运行 `dotnet restore`。注意：
   - **版本要求**：.NET 9 SDK 要求 Visual Studio 17.12+ 以目标 `net9.0`（17.11 用于 `net8.0` 和更早版本）。
   - **.NET Standard 1.x 的新警告** 和 **.NET 7 目标的新警告** — 考虑更新或删除过时的目标框架。

4. 运行清理构建。收集所有错误和新的警告。这些将在步骤 3 中解决。

### 步骤 3：解决构建错误和源不兼容变更

系统性地处理编译错误和新的警告。根据项目类型加载适当的参考文档：

| 如果项目使用… | 加载参考 |
|----------------|----------|
| 任何 .NET 9 项目 | `references/csharp-compiler-dotnet8to9.md` |
| 任何 .NET 9 项目 | `references/core-libraries-dotnet8to9.md` |
| 任何 .NET 9 项目 | `references/sdk-msbuild-dotnet8to9.md` |
| ASP.NET Core | `references/aspnet-core-dotnet8to9.md` |
| Entity Framework Core | `references/efcore-dotnet8to9.md` |
| 加密 API | `references/cryptography-dotnet8to9.md` |
| System.Text.Json、HttpClient、网络 | `references/serialization-networking-dotnet8to9.md` |
| Windows Forms 或 WPF | `references/winforms-wpf-dotnet8to9.md` |
| Docker 容器、原生互操作 | `references/containers-interop-dotnet8to9.md` |
| 运行时配置、部署 | `references/deployment-runtime-dotnet8to9.md` |

**常见的源不兼容变更需要检查：**

1. **`params` span 重载解析** — 新的 `params ReadOnlySpan<T>` 重载在 `String.Join`、`String.Concat`、`Path.Combine`、`Task.WhenAll` 等上优先绑定。在这些方法内部调用 `Expression` lambdas 的代码将失败（CS8640/CS9226）。见 `references/core-libraries-dotnet8to9.md`。

2. **`StringValues` 模棱两可的重载** — `params Span<T>` 功能与 `String.Concat`、`String.Join`、`Path.Combine` 等方法上的 `StringValues` 隐式运算符创建歧义。通过显式转换参数来修复。见 `references/core-libraries-dotnet8to9.md`。

3. **新的弃用警告（SYSLIB0054–SYSLIB0057）**：
   - `SYSLIB0054`：用 `Volatile.Read`/`Volatile.Write` 替换 `Thread.VolatileRead`/`VolatileWrite`
   - `SYSLIB0057`：用 `X509CertificateLoader` 方法替换 `X509Certificate2`/`X509Certificate` 二进制/文件构造函数
   - 也包括 `SYSLIB0055`（ARM AdvSimd 有符号重载）和 `SYSLIB0056`（使用哈希算法的 `Assembly.LoadFrom`）——见 `references/core-libraries-dotnet8to9.md`

4. **C# 13 `InlineArray` 在记录结构上** — `[InlineArray]` 属性在 `record struct` 类型上现在被禁止（CS9259）。更改为一个常规的 `struct`。见 `references/csharp-compiler-dotnet8to9.md`。

5. **C# 13 迭代器安全上下文** — 迭代器现在在 C# 13 中引入了一个安全上下文。迭代器内部的本地函数如果使用了来自外部 `unsafe` 类的 unsafe 代码将现在报错。为本地函数添加 `unsafe` 修饰符。见 `references/csharp-compiler-dotnet8to9.md`。

6. **C# 13 集合表达式重载解析** — 空集合表达式（`[]`）不再使用 span vs 非span 来打破重载。现在优先使用确切的元素类型。见 `references/csharp-compiler-dotnet8to9.md`。

7. **`String.Trim(params ReadOnlySpan<char>)` 已移除** — 针对 .NET 9 预览编译的代码将 `ReadOnlySpan<char>` 传递给 `Trim`/`TrimStart`/`TrimEnd` 必须重新构建；该重载在 GA 中已移除。见 `references/core-libraries-dotnet8to9.md`。

8. **`BinaryFormatter` 始终抛出** — 如果项目使用 `BinaryFormatter`，**停止并通知用户**——这是一个重大决策。见 `references/serialization-networking-dotnet8to9.md`。

9. **`HttpListenerRequest.UserAgent` 是可空的** — 属性现在为 `string?`。添加空检查。见 `references/serialization-networking-dotnet8to9.md`。

10. **Windows Forms 可空性注解变更** — 一些 WinForms API 参数从可空更改为不可空。更新调用位置。见 `references/winforms-wpf-dotnet8to9.md`。

11. **Windows Forms 安全分析器（WFO1000）** — 新的分析器为没有显式序列化配置的属性产生错误。见 `references/winforms-wpf-dotnet8to9.md`。

每次修复一批错误后重新构建。重复直到构建干净。

### 步骤 4：解决行为变化

行为变化不会导致构建错误，但可能会改变运行时行为。审查每个适用的项目，并确定是否依赖于之前的行为。

**高影响的行为变化（首先检查）：**

1. **浮点数到整数的转换现在饱和** — 从 `float`/`double` 到整数类型的转换现在在 x86/x64 上饱和而不是回绕。见 `references/deployment-runtime-dotnet8to9.md`。

2. **EF Core：待处理的模型变更异常** — `Migrate()`/`MigrateAsync()` 如果模型有待处理的变化将抛出异常。**搜索任何 `HasData` 调用中的 `DateTime.Now`、`DateTime.UtcNow` 或 `Guid.NewGuid()`——这些必须替换为固定常量**（例如，`new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc)`）。见 `references/efcore-dotnet8to9.md`。

3. **EF Core：显式事务异常** — 用户事务内的 `Migrate()` 现在抛出异常。见 `references/efcore-dotnet8to9.md`。

4. **HttpClientFactory 默认使用 `SocketsHttpHandler`** — 将主处理程序强制转换为 `HttpClientHandler` 的代码将得到 `InvalidCastException`。见 `references/serialization-networking-dotnet8to9.md`。

5. **HttpClientFactory 默认隐藏标头** — 所有 `Trace` 级别日志中的标头值现在被隐藏。见 `references/serialization-networking-dotnet8to9.md`。

6. **环境变量优先于 `runtimeconfig.json`** — 来自环境变量的运行时配置设置现在覆盖 `runtimeconfig.json`。见 `references/deployment-runtime-dotnet8to9.md`。

7. **ASP.NET Core 开发中的 `ValidateOnBuild`/`ValidateScopes`** — `HostBuilder` 现在默认启用开发中的 DI 验证。见 `references/aspnet-core-dotnet8to9.md`。

**其他需要审查的行为变化（可能导致运行时异常 ⚠️ 或细微的行为差异）：**

- ⚠️ `FromKeyedServicesAttribute` 不再注入非键服务回退——抛出 `InvalidOperationException`
- ⚠️ 容器镜像不再安装 zlib——依赖系统 zlib 的应用程序将失败
- ⚠️ Intel CET 现在默认启用——非 CET 兼容的原生库可能导致进程终止
- `BigInteger` 现在的最大长度为 `(2^31) - 1` 位
- `JsonDocument` 反序列化 JSON `null` 现在返回非空的 `JsonDocument`，具有 `JsonValueKind.Null` 而不是 C# `null`
- `System.Text.Json` 元数据读取器现在转义元数据属性名称
- `ZipArchiveEntry` 名称/注释现在尊重 UTF-8 标志
- `IncrementingPollingCounter` 初始回调现在是异步的
- `InMemoryDirectoryInfo` 将 rootDir 前缀添加到文件
- `RuntimeHelpers.GetSubArray` 返回不同的类型
- `PictureBox` 抛出 `HttpRequestException` 而不是 `WebException`
- `StatusStrip` 使用不同的默认渲染器
- `IMsoComponent` 支持是可选的
- `SafeEvpPKeyHandle.DuplicateHandle` 上引句柄
- `HttpClient` 指标无条件报告 `server.port`
- URI 查询字符串在 HttpClient EventSource 事件和 IHttpClientFactory 日志中被隐藏
- `dotnet watch` 与旧框架的热重载不兼容
- WPF `GetXmlNamespaceMaps` 返回 `Hashtable` 而不是 `String`

### 步骤 5：更新基础设施

1. **Dockerfile**：更新基础镜像。注意 .NET 9 容器镜像不再安装 zlib。如果您的应用程序依赖 zlib，请将 `RUN apt-get update && apt-get install -y zlib1g` 添加到您的 Dockerfile。
   ```dockerfile
   # Before
   FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:8.0
   # After
   FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:9.0
   ```

2. **CI/CD 管道**：更新 SDK 版本引用。如果使用 `global.json`，请更新：
   ```json
   {
     "sdk": {
       "version": "9.0.100",
       "rollForward": "latestFeature"
     }
   }
   ```
   审查 `rollForward` 策略——如果设置为 `"disable"` 或 `"latestPatch"`，SDK 升级后可能无法正确解析。`"latestFeature"`（推荐）允许 SDK 向最新的 9.0.x 功能带前进。

3. **Visual Studio 版本**：.NET 9 SDK 要求 VS 17.12+ 以目标 `net9.0`。VS 17.11 只能目标 `net8.0` 和更早版本。

4. **终端记录器**：`dotnet build` 现在在交互式终端中默认使用终端记录器。解析 MSBuild 控制台输出的 CI 脚本可能需要 `--tl:off` 或 `MSBUILDTERMINALLOGGER=off`。

5. **`dotnet workload` 输出**：输出格式已更改。更新任何解析 workload 命令输出的脚本。

6. **.NET Monitor 镜像**：标签简化为仅版本（影响引用特定标签的容器编排）。

### 步骤 6：验证

1. 运行完整的清理构建：`dotnet build --no-incremental`
2. 运行所有测试：`dotnet test`
3. 如果应用程序是容器化的，构建和测试容器镜像
4. 对应用程序进行冒烟测试，特别关注：
   - `BinaryFormatter` 使用（将在运行时抛出）
   - 浮点数到整数的转换行为
   - EF Core 迁移应用程序
   - HttpClientFactory 处理器强制转换和日志记录
   - 开发环境中的 DI 验证
   - 运行时配置设置（环境变量优先级）
5. 审查差异，确保未引入任何意外的行为变化

## 参考文档

`references/` 文件夹包含按技术领域组织的详细破坏性变更信息。仅加载与正在迁移的项目相关的参考文档：

| 参考文件 | 何时加载 |
|----------|----------|
| `references/csharp-compiler-dotnet8to9.md` | 总是（C# 13 编译器破坏性变更——记录结构上的 InlineArray、迭代器安全上下文、集合表达式重载） |
| `references/core-libraries-dotnet8to9.md` | 总是（适用于所有 .NET 9 项目） |
| `references/sdk-msbuild-dotnet8to9.md` | 总是（SDK 和构建工具变更） |
| `references/aspnet-core-dotnet8to9.md` | 项目使用 ASP.NET Core |
| `references/efcore-dotnet8to9.md` | 项目使用 Entity Framework Core |
| `references/cryptography-dotnet8to9.md` | 项目使用 System.Security.Cryptography 或 X.509 证书 |
| `references/serialization-networking-dotnet8to9.md` | 项目使用 BinaryFormatter、System.Text.Json、HttpClient 或网络 API |
| `references/winforms-wpf-dotnet8to9.md` | 项目使用 Windows Forms 或 WPF |
| `references/containers-interop-dotnet8to9.md` | 项目使用 Docker 容器或原生互操作（P/Invoke） |
| `references/deployment-runtime-dotnet8to9.md` | 项目使用运行时配置、部署或具有浮点数到整数的转换 |
