---
name: migrate-dotnet9-to-dotnet10
description: 将 .NET 9 项目或解决方案迁移到 .NET 10 并解决所有破坏性变更。用途：从 net9.0 升级 TargetFramework 到 net10.0，更新 .NET 10 SDK 后修复构建错误，解决 .NET 10 / C# 14 / ASP.NET Core 10 / EF Core 10 中的源代码和行为变更，更新 Debian 到 Ubuntu 基础镜像的 Dockerfile，解决弃用警告（SYSLIB0058-SYSLIB0062），适应 SDK/NuGet 变更（NU1510, PrunePackageReference），将 System.Linq.Async 迁移到内置的 AsyncEnumerable，修复 OpenApi v2 API 变更，加密重命名，以及 C# 14 编译器变更（字段关键字、扩展关键字、span 重载）。不适用于：.NET Framework 迁移，从 .NET 8 或更早版本升级（请先使用 migrate-dotnet8-to-dotnet9），全新的 .NET 10 项目，或仅用于美化现代化的场景。依赖项：csharp-compiler, core-libraries, sdk-msbuild（始终）；aspnet-core, efcore, cryptography, extensions-hosting, serialization-networking, winforms-wpf, containers-interop（选择性）。
---

# .NET 9 迁移到 .NET 10

将 .NET 9 项目或解决方案迁移到 .NET 10，系统性地解决所有破坏性变更。结果是一个目标为 `net10.0` 的项目，该项目可以干净地构建、通过测试，并考虑到 .NET 10 发布中引入的所有行为、源不兼容和二进制不兼容的变更。

## 使用场景

- 将 `TargetFramework` 从 `net9.0` 升级到 `net10.0`
- 更新 .NET 10 SDK 后解决构建错误或新的警告
- 适应 .NET 10 运行时、ASP.NET Core 10 或 EF Core 10 中的行为变更
- 更新用于 .NET 10 的 CI/CD 管道、Dockerfile 或部署脚本
- 从社区 `System.Linq.Async` 包迁移到内置的 `System.Linq.AsyncEnumerable`

## 不适用场景

- 项目已经目标为 `net10.0` 并可以干净地构建——迁移已完成
- 从 .NET 8 或更早版本升级——首先使用 `migrate-dotnet8-to-dotnet9` 技能达到 `net9.0`，然后返回此技能进行 `net9.0` → `net10.0` 的迁移
- 从 .NET Framework 迁移——这是一个单独的、更大的工作
- 从 .NET 10 开始的绿场项目（无需迁移）

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------------|
| 项目或解决方案路径 | 是 | 要迁移的 `.csproj`、`.sln` 或 `.slnx` 入口点 |
| 构建命令 | 否 | 如何构建（例如，`dotnet build`，一个仓库构建脚本）。如果未提供，将自动检测 |
| 测试命令 | 否 | 如何运行测试（例如，`dotnet test`）。如果未提供，将自动检测 |
| 项目类型提示 | 否 | 项目是否使用 ASP.NET Core、EF Core、WinForms、WPF、容器等。如果未提供，将根据 `PackageReferences` 和 SDK 属性自动检测 |

## 工作流程

> **直接从加载的参考文档中回答。** 不要搜索文件系统或获取网页上的破坏性变更信息——参考文档包含权威的详细信息。专注于识别哪些破坏性变更适用，并提供具体的修复方法。**例外：** 如果你怀疑安全漏洞（CVE）可能适用于项目的依赖项，请检查已发布的安全公告——参考文档可能不涵盖发布后的 CVE。

>
> **提交策略：** 在每个逻辑边界处提交——更新 TFM（步骤 2）后、解决构建错误（步骤 3）后、解决行为变更（步骤 4）后、更新基础设施（步骤 5）后。这使每个提交都保持专注且可审查。

### 步骤 1：评估项目

1. 确定项目如何构建和测试。查找构建脚本、`.sln`/`.slnx` 文件或单独的 `.csproj` 文件。
2. 运行 `dotnet --version` 以确认已安装 .NET 10 SDK。如果没有安装，停止并通知用户。
3. 通过检查以下内容来确定项目使用的技术领域：
   - **SDK 属性**：`Microsoft.NET.Sdk.Web` → ASP.NET Core；`Microsoft.NET.Sdk.WindowsDesktop` 与 `<UseWPF>` 或 `<UseWindowsForms>` → WPF/WinForms
   - **PackageReferences**：`Microsoft.EntityFrameworkCore.*` → EF Core；`Microsoft.Data.Sqlite` → Sqlite；`Microsoft.Extensions.Hosting` → 泛型主机 / BackgroundService
   - **Dockerfile 存在** → 与容器相关的变更相关
   - **P/Invoke 或原生互操作使用** → 与互操作相关的变更相关
   - **`System.Linq.Async` 包引用** → 需要进行 AsyncEnumerable 迁移
   - **使用 `System.Text.Json` 进行多态** → 与序列化相关的变更相关
4. 记录哪些参考文档是相关的（见步骤 3 中的参考加载表）。
5. 在当前的 `net9.0` 目标上执行**清理构建**（`dotnet build --no-incremental` 或删除 `bin`/`obj`）以建立干净的基线。记录任何预先存在的警告。

### 步骤 2：更新目标框架

1. 在每个 `.csproj`（或如果集中管理，则为 `Directory.Build.props`），将：
   ```xml
   <TargetFramework>net9.0</TargetFramework>
   ```
   更改为：
   ```xml
   <TargetFramework>net10.0</TargetFramework>
   ```
   对于多目标项目，将 `net10.0` 添加到 `<TargetFrameworks>` 或替换 `net9.0`。

2. 更新所有 `Microsoft.Extensions.*`、`Microsoft.AspNetCore.*`、`Microsoft.EntityFrameworkCore.*` 和其他 Microsoft 包引用到它们的 10.0.x 版本。如果使用中央包管理（`Directory.Packages.props`），则在那里更新版本。

3. 运行 `dotnet restore`。注意：
   - **NU1510**：NuGet 剪切直接引用——该包现在可能包含在共享框架中。如果如此，请删除显式的 `<PackageReference>`。
   - **现在没有版本号的 `PackageReference` 会引发错误**——每个 `<PackageReference>` 必须有 `Version`（或使用 CPM）。
   - **NuGet 对传递依赖项的审计**（`dotnet restore` 现在审计传递依赖项）——审查任何新的漏洞警告。

4. 运行一个清理构建。收集所有错误和新的警告。这些将在步骤 3 中解决。

### 步骤 3：解决构建错误和源不兼容的变更

系统地处理编译错误和新的警告。根据项目类型加载适当的参考文档：

| 如果项目使用… | 加载参考 |
|-----------------------|----------------|
| 任何 .NET 10 项目 | `references/csharp-compiler-dotnet9to10.md` |
| 任何 .NET 10 项目 | `references/core-libraries-dotnet9to10.md` |
| 任何 .NET 10 项目 | `references/sdk-msbuild-dotnet9to10.md` |
| ASP.NET Core | `references/aspnet-core-dotnet9to10.md` |
| Entity Framework Core | `references/efcore-dotnet9to10.md` |
| 加密 API | `references/cryptography-dotnet9to10.md` |
| Microsoft.Extensions.Hosting、BackgroundService、配置 | `references/extensions-hosting-dotnet9to10.md` |
| System.Text.Json、XmlSerializer、HttpClient、MailAddress、Uri | `references/serialization-networking-dotnet9to10.md` |
| Windows Forms 或 WPF | `references/winforms-wpf-dotnet9to10.md` |
| Docker 容器、单文件应用、原生互操作 | `references/containers-interop-dotnet9to10.md` |

**常见的源不兼容变更需要检查：**

1. **`System.Linq.Async` 冲突**——删除 `System.Linq.Async` 包引用或升级到 v7.0.0。如果消费的是传递的，请添加 `<ExcludeAssets>compile</ExcludeAssets>`。在需要的地方将 `SelectAwait` 调用重命名为 `Select`。

2. **新的弃用警告（SYSLIB0058–SYSLIB0062）**：
   - `SYSLIB0058`：用 `NegotiatedCipherSuite` 替换 `SslStream.KeyExchangeAlgorithm`/`CipherAlgorithm`/`HashAlgorithm`——如果旧属性用于拒绝弱 TLS 密码，请使用新 API 保留等效的验证逻辑
   - `SYSLIB0059`：用 `AppDomain.ProcessExit` 替换 `SystemEvents.EventsThreadShutdown`
   - `SYSLIB0060`：用 `Rfc2898DeriveBytes.Pbkdf2` 替换 `Rfc2898DeriveBytes` 构造函数
   - `SYSLIB0061`：用接受 `IComparer<TKey>` 的 `Queryable.MaxBy`/`MinBy` 重载替换接受 `IComparer<TSource>` 的重载
   - `SYSLIB0062`：替换 `XsltSettings.EnableScript` 使用

3. **C# 14 在属性访问器中的 `field` 关键字**——标识符 `field` 现在是属性 `get`/`set`/`init` 访问器内的上下文关键字。命名的局部变量 `field` 会引发 CS9272（错误）。未使用 `this.` 引用命名的类成员 `field` 会引发 CS9258（警告）。通过重命名（例如，`fieldValue`）或使用 `@field` 脚本解决。参见 `references/csharp-compiler-dotnet9to10.md`。

4. **C# 14 `extension` 上下文关键字**——命名的类型、别名或类型参数 `extension` 是不允许的。重命名或使用 `@extension` 脚本。

5. **C# 14 使用 span 参数的重载解析**——包含数组上的 `.Contains()` 的表达式树现在可能绑定到 `MemoryExtensions.Contains` 而不是 `Enumerable.Contains`。数组上的 `Enumerable.Reverse` 可能解析为原地 `Span` 扩展。通过将 `IEnumerable<T>` 强制转换为使用 `.AsEnumerable()` 或显式静态调用解决。参见 `references/csharp-compiler-dotnet9to10.md` 的完整详细信息。

6. **ASP.NET Core 弃用**（如果适用）：
   - `WebHostBuilder`、`IWebHost`、`WebHost` 已弃用——迁移到 `Host.CreateDefaultBuilder` 或 `WebApplication.CreateBuilder`
   - `IActionContextAccessor` / `ActionContextAccessor` 已弃用
   - `WithOpenApi` 扩展方法已弃用
   - `IncludeOpenAPIAnalyzers` 属性已弃用
   - `IPNetwork` 和 `ForwardedHeadersOptions.KnownNetworks` 已弃用
   - Razor 运行时编译已弃用
   - `Microsoft.Extensions.ApiDescription.Client` 包已弃用
   - **`Microsoft.OpenApi` v2.x 破坏性变更**——`Microsoft.AspNetCore.OpenApi 10.0` 拉入 `Microsoft.OpenApi` v2.x，该版本重新结构化了命名空间和模型。`OpenApiString`/`OpenApiAny` 类型已移除（使用 `JsonNode`），`OpenApiSecurityScheme.Reference` 被 `OpenApiSecuritySchemeReference` 替换，OpenAPI 模型对象上的集合可能为 null，并且 `OpenApiSchema.Nullable` 已移除。参见 `references/aspnet-core-dotnet9to10.md` 的迁移模式。

7. **SDK 变更**：
   - `dotnet new sln` 现在默认为 SLNX 格式——如果需要旧格式，请使用 `--format sln`
   - 文件级指令中的双引号是不允许的
   - `dnx.ps1` 从 .NET SDK 中移除
   - `project.json` 不再支持在 `dotnet restore` 中

8. **EF Core 源变更**（如果适用）——参见 `references/efcore-dotnet9to10.md`：
   - `ExecuteUpdateAsync` 现在接受常规 lambda（表达式树构造代码必须重写）
   - `IDiscriminatorPropertySetConvention` 签名已更改
   - `IRelationalCommandDiagnosticsLogger` 方法添加了 `logCommandText` 参数

9. **WinForms/WPF 源变更**（如果适用）：
   - 同时引用 WPF 和 WinForms 的应用程序必须区分 `MenuItem` 和 `ContextMenu` 类型
   - `HtmlElement.InsertAdjacentElement` 中的参数已重命名
   - WPF 中不允许空的 `ColumnDefinitions` 和 `RowDefinitions`

10. **加密源变更**（如果适用）：
    - `MLDsa` 和 `SlhDsa` 成员从 `SecretKey` 重命名为 `PrivateKey`（例如，`ExportMLDsaSecretKey` → `ExportMLDsaPrivateKey`，`SecretKeySizeInBytes` → `PrivateKeySizeInBytes`）
    - `Rfc2898DeriveBytes` 构造函数已弃用（SYSLIB0060）——用静态 `Rfc2898DeriveBytes.Pbkdf2(password, salt, iterations, hashAlgorithm, outputLength)` 替换
    - `CoseSigner.Key` 现在可以为 null——在使用前检查 null
    - `X509Certificate.GetKeyAlgorithmParameters()` 和 `PublicKey.EncodedParameters` 可能为 null
    - 环境变量从 `CLR_OPENSSL_VERSION_OVERRIDE` 重命名为 `DOTNET_OPENSSL_VERSION_OVERRIDE`

每次修复一批错误后重新构建。重复直到构建干净。

### 步骤 4：解决行为变更

行为变更不会导致构建错误，但可能会改变运行时行为。审查每个适用的项目，并确定是否依赖于之前的行为。

**高影响的行为变更（首先检查）：**

1. **移除了 SIGTERM 信号处理**——.NET 运行时不再注册默认的 SIGTERM 处理程序。如果你依赖于 `AppDomain.ProcessExit` 或 `AssemblyLoadContext.Unloading` 在 SIGTERM 时被触发：
   - ASP.NET Core 和泛型主机应用程序不受影响（它们注册了自己的处理程序）
   - 控制台应用程序和没有泛型主机的容器化应用程序必须显式注册 `PosixSignalRegistration.Create(PosixSignal.SIGTERM, _ => Environment.Exit(0))`

2. **BackgroundService.ExecuteAsync 完全在后台线程上运行**——第一个 `await` 之前的同步部分不再阻塞启动。如果启动顺序很重要，请将代码移到 `StartAsync` 或构造函数中，或实现 `IHostedLifecycleService`。

3. **配置 null 值现在被保留**——JSON `null` 值不再转换为空字符串。使用非默认值初始化的属性将被 `null` 覆盖。审查配置绑定代码。

4. **Microsoft.Data.Sqlite DateTimeOffset 变更**（所有高影响）：
   - 没有偏移量的 `GetDateTimeOffset` 现在假设为 UTC（之前假设为本地）
   - 将 `DateTimeOffset` 写入 REAL 列现在首先转换为 UTC
   - 偏移量的 `GetDateTime` 现在返回 UTC，`DateTimeKind.Utc`
   - 缓解：`AppContext.SetSwitch("Microsoft.Data.Sqlite.Pre10TimeZoneHandling", true)` 作为临时解决方案

5. **EF Core 参数化集合**——集合上的 `.Contains()` 现在使用多个标量参数而不是 JSON/OPENJSON。可能会影响大型集合的查询性能。缓解：`UseParameterizedCollectionMode(ParameterTranslationMode.Parameter)` 以恢复。

6. **EF Core Azure SQL 中的 JSON 数据类型**——Azure SQL 和兼容性级别 ≥170 现在使用 `json` 数据类型而不是 `nvarchar(max)`。将生成迁移来修改现有列。缓解：将兼容性级别设置为 160 或显式使用 `HasColumnType("nvarchar(max)")`。

7. **System.Text.Json 属性名称冲突验证**——具有与元数据名称冲突的属性的多态类型（`$type`、`$id`、`$ref`）现在会引发 `InvalidOperationException`。向冲突的属性添加 `[JsonIgnore]`。

**其他需要审查的行为变更：**

- `BufferedStream.WriteByte` 不再隐式刷新——如果需要，添加显式的 `Flush()` 调用
- 默认跟踪上下文传播器更新为 W3C 标准
- `DriveInfo.DriveFormat` 返回实际的 Linux 文件系统类型名称
- LDAP `DirectoryControl` 解析更加严格
- 默认的 .NET 容器镜像从 Debian 切换到 Ubuntu（Debian 镜像不再提供）
- 单文件应用默认不再在可执行目录中查找原生库
- `DllImportSearchPath.AssemblyDirectory` 仅搜索程序集目录
- `MailAddress` 强制执行连续点的验证
- 浏览器 HTTP 客户端中的流式 HTTP 响应默认启用
- `Uri` 长度限制已移除——如果 `Uri` 用于拒绝来自不可信来源的过大的输入，请添加显式的长度验证
- Cookie 登录重定向禁用已知 API 终点（ASP.NET Core）
- `XmlSerializer` 不再忽略 `[Obsolete]` 属性——审核弃用的属性以防止敏感数据意外暴露，并添加 `[XmlIgnore]` 以防止意外数据暴露
- `dotnet restore` 审计传递依赖项
- `dotnet watch` 日志记录到 stderr 而不是 stdout
- `dotnet` CLI 命令将非命令相关数据记录到 stderr
- 各种 NuGet 行为变更（参见 `references/sdk-msbuild-dotnet9to10.md`）
- `StatusStrip` 默认使用 System RenderMode（WinForms）
- `TreeView` 复选框图像截断修复（WinForms）
- `DynamicResource` 不正确使用会导致崩溃（WPF）

### 步骤 5：更新基础设施

1. **Dockerfile**：更新基础镜像。默认标签现在使用 Ubuntu 而不是 Debian。Debian 镜像不再为 .NET 10 提供。
   ```dockerfile
   # Before
   FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:9.0
   # After
   FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:10.0
   ```

2. **CI/CD 管道**：更新 SDK 版本引用。如果使用 `global.json`，请更新：
   ```json
   {
     "sdk": {
       "version": "10.0.100"
     }
   }
   ```

3. **环境变量重命名**：
   - `DOTNET_OPENSSL_VERSION_OVERRIDE` 替换了旧名称
   - `DOTNET_ICU_VERSION_OVERRIDE` 替换了旧名称
   - `NUGET_ENABLE_ENHANCED_HTTP_RETRY` 已移除

4. **OpenSSL 要求**：Unix 上现在需要 OpenSSL 1.1.1 或更高版本。macOS 上不再支持 OpenSSL 密码学原语。

5. **解决方案文件格式**：如果在脚本中使用 `dotnet new sln`，请注意它现在生成 SLNX 格式。如果需要旧格式，请传递 `--format sln`。

### 步骤 6：验证

1. 运行完整清理构建：`dotnet build --no-incremental`
2. 运行所有测试：`dotnet test`
3. 如果应用程序是容器化的，构建并测试容器镜像
4. 对应用程序进行冒烟测试，特别关注：
   - 信号处理/优雅关闭行为
   - 后台服务启动顺序
   - 配置绑定时使用空值
   - 使用 Sqlite 处理日期/时间
   - 使用多态类型进行 JSON 序列化
   - 使用 `.Contains()` 在集合上执行 EF Core 查询
5. **安全审查** — 验证迁移是否削弱了安全控制：
   - 在迁移 `SslStream` API 后，TLS 密码验证逻辑是否保留（SYSLIB0058）
   - 包含敏感数据的过时属性是否从序列化中排除（`[XmlIgnore]`，`[JsonIgnore]`）
   - 如果使用 `Uri` 作为长度门限，输入验证是否仍会拒绝过大的 URI
   - 异常处理器在返回 `true` 之前是否发出与安全相关的遥测数据（认证失败、访问违规）
   - 连接字符串是否设置了不泄露版本信息的显式 `Application Name`
   - `dotnet restore` 漏洞审查发现的问题是否已解决，而非被压制
6. 审查差异，确保未引入意外的行为变更

## 参考文档

`references/` 文件夹按技术领域组织了详细的破坏性变更信息。仅加载与正在迁移的项目相关的参考文档：

| 参考文件 | 加载时机 |
|----------|---------|
| `references/csharp-compiler-dotnet9to10.md` | 总是加载（C# 14 编译器破坏性变更 — 字段关键字、扩展关键字、span 重载） |
| `references/core-libraries-dotnet9to10.md` | 总是加载（适用于所有 .NET 10 项目） |
| `references/sdk-msbuild-dotnet9to10.md` | 总是加载（SDK 和构建工具变更） |
| `references/aspnet-core-dotnet9to10.md` | 项目使用 ASP.NET Core |
| `references/efcore-dotnet9to10.md` | 项目使用 Entity Framework Core 或 Microsoft.Data.Sqlite |
| `references/cryptography-dotnet9to10.md` | 项目使用 System.Security.Cryptography 或 X.509 证书 |
| `references/extensions-hosting-dotnet9to10.md` | 项目使用 Generic Host、BackgroundService 或 Microsoft.Extensions.Configuration |
| `references/serialization-networking-dotnet9to10.md` | 项目使用 System.Text.Json、XmlSerializer、HttpClient 或网络 API |
| `references/winforms-wpf-dotnet9to10.md` | 项目使用 Windows Forms 或 WPF |
| `references/containers-interop-dotnet9to10.md` | 项目使用 Docker 容器、单文件发布或原生互操作（P/Invoke） |
