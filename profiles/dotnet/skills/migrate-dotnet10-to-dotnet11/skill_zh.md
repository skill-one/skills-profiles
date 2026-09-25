# .NET 10 → .NET 11 迁移

将 .NET 10 项目或解决方案迁移到 .NET 11，系统性地解决所有破坏性变更。结果是一个目标为 `net11.0` 的项目，该项目可以干净地构建、通过测试，并考虑到 .NET 11 中引入的所有行为变化、源不兼容变化和二进制不兼容变化。

> **注意：** .NET 11 目前处于预览阶段。本技能涵盖到预览版 3 文档中记录的破坏性变更。

## 何时使用

- 将 `TargetFramework` 从 `net10.0` 升级到 `net11.0`
- 更新 .NET 11 SDK 后解决构建错误或新的警告
- 适应 .NET 11 运行时、ASP.NET Core 11 或 EF Core 11 中的行为变化
- 更新用于 .NET 11 的 CI/CD 管道、Dockerfile 或部署脚本
- SDK 升级后修复 C# 15 编译器破坏性变更

## 何时不使用

- 项目已经目标为 `net11.0` 且可以干净构建——迁移已完成
- 从 .NET 9 或更早版本升级——首先解决 .NET 9→10 的破坏性变更
- 从 .NET Framework 迁移——这是一个单独的、更大的工作
- 从 .NET 11 开始的绿场项目（无需迁移）

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 项目或解决方案路径 | 是 | 要迁移的 `.csproj`、`.sln` 或 `.slnx` 入口点 |
| 构建命令 | 否 | 如何构建（例如，`dotnet build`，一个仓库构建脚本）。如果未提供，则自动检测 |
| 测试命令 | 否 | 如何运行测试（例如，`dotnet test`）。如果未提供，则自动检测 |
| 项目类型提示 | 否 | 项目是否使用 ASP.NET Core、EF Core、Cosmos DB 等。如果未提供，则从 PackageReferences 和 SDK 属性中自动检测 |

## 工作流

> **直接从加载的参考文档中获取有关 .NET 11 破坏性变更的信息。** 您可以根据需要检查本地仓库（项目/解决方案文件、源代码、配置、构建/测试脚本），以确定哪些变更适用。不要获取网页或其他外部来源的破坏性变更信息——加载的参考是权威来源。专注于识别哪些破坏性变更适用，并提供具体的修复方案。
>
> **提交策略：** 在每个逻辑边界处提交——更新 TFM（步骤 2）后、解决构建错误（步骤 3）后、处理行为变化（步骤 4）后、更新基础设施（步骤 5）后。这使每个提交保持专注且可审查。

### 步骤 1：评估项目

1. 确定项目如何构建和测试。查找构建脚本、`.sln`/`.slnx` 文件或单独的 `.csproj` 文件。
2. 运行 `dotnet --version` 以确认已安装 .NET 11 SDK。如果没有，请停止并通知用户。
3. 通过检查以下内容来确定项目使用的技术领域：
   - **SDK 属性**：`Microsoft.NET.Sdk.Web` → ASP.NET Core；`Microsoft.NET.Sdk.WindowsDesktop` 与 `<UseWPF>` 或 `<UseWindowsForms>` → WPF/WinForms
   - **PackageReferences**：`Microsoft.EntityFrameworkCore.*` → EF Core；`Microsoft.EntityFrameworkCore.Cosmos` → Cosmos DB 提供程序
   - **Dockerfile 存在** → 与容器相关的变更
   - **加密 API 使用** → macOS 上 DSA 受影响；AIA 证书下载变更相关
   - **压缩 API 使用** → DeflateStream/GZipStream/ZipArchive 变更相关
   - **TAR API 使用** → 头部校验和验证和 HardLink 条目变更相关
   - **`NamedPipeClientStream` 与 `SafePipeHandle` 一起使用** → SYSLIB0063 构造函数弃用相关
   - **`BackgroundService` 使用** → 未处理的异常现在停止主机
   - **直接使用 `Microsoft.OpenApi`** → ASP.NET Core OpenAPI 中 v3 API 破坏性变更
   - **EF Core SQL Server 与 Entra ID 认证** → SqlClient 7.0 认证依赖项变更
   - **Unix 上的 NativeAOT 本地库** → 输出文件名前缀已更改
4. 记录哪些参考文档相关（见步骤 3 中的参考加载表）。
5. 在当前 `net10.0` 目标上执行**干净构建**（`dotnet build --no-incremental` 或删除 `bin`/`obj`）以建立干净的基线。记录任何现有警告。

### 步骤 2：更新目标框架

1. 在每个 `.csproj`（如果集中化，则为 `Directory.Build.props`），将：
   ```xml
   <TargetFramework>net10.0</TargetFramework>
   ```
   更改为：
   ```xml
   <TargetFramework>net11.0</TargetFramework>
   ```
   对于多目标项目，将 `net11.0` 添加到 `<TargetFrameworks>` 或替换 `net10.0`。

2. 更新所有 `Microsoft.Extensions.*`、`Microsoft.AspNetCore.*`、`Microsoft.EntityFrameworkCore.*` 和其他 Microsoft 软件包引用到它们的 11.0.x 版本。如果使用中央软件包管理（`Directory.Packages.props`），则在那里更新版本。

3. 运行 `dotnet restore`。在继续之前修复任何还原错误。

4. 运行 `dotnet build`。捕获所有错误和警告——这些将在步骤 3 中解决。

### 步骤 3：修复源破坏和编译变更

根据项目的技术领域加载参考文档：

| 参考文件 | 何时加载 |
|----------------|-------------|
| `references/csharp-compiler-dotnet10to11.md` | 总是（C# 15 编译器破坏性变更） |
| `references/core-libraries-dotnet10to11.md` | 总是（适用于所有 .NET 11 项目） |
| `references/sdk-msbuild-dotnet10to11.md` | 总是（SDK 和构建工具变更） |
| `references/aspnetcore-dotnet10to11.md` | 项目使用 ASP.NET Core（OpenAPI、Blazor） |
| `references/efcore-dotnet10to11.md` | 项目使用 Entity Framework Core |
| `references/cryptography-dotnet10to11.md` | 项目使用加密 API、mTLS 或目标 macOS |
| `references/runtime-jit-dotnet10to11.md` | 部署到较旧硬件、嵌入式设备或使用 NativeAOT |

系统地处理每个构建错误。常见模式：

1. **C# 15 Span 集合表达式安全上下文**—— `Span<T>`/`ReadOnlySpan<T>` 类型的集合表达式现在具有 `declaration-block` 安全上下文。将 span 集合表达式分配给外部作用域中的变量的代码将出错。使用数组类型或将表达式移到正确的范围。

2. **`ref readonly` 委托/本地函数需要 `InAttribute`**—— 如果从返回 `ref readonly` 的方法合成委托或使用 `ref readonly` 本地函数，请确保 `System.Runtime.InteropServices.InAttribute` 可用。

3. **属性中的 `nameof(this.)`**—— 移除 `this.` 限定符；使用 `nameof(P)` 而不是 `nameof(this.P)`。

4. **C# 15 集合表达式中的 `with()`**—— `with(...)` 现在被视为构造函数参数，而不是方法调用。使用 `@with(...)` 调用名为 `with` 的方法。

5. **动态 `&&`/`||` 与接口操作数**—— 作为 `&&`/`||` 左操作数的接口类型与 `dynamic` 右操作数现在在编译时出错。转换为具体类型或 `dynamic`。

6. **EF Core Cosmos 同步 I/O 移除**—— `ToList()`、`SaveChanges()` 等在 Cosmos 提供程序上始终抛出。转换为异步等效项。

7. **SYSLIB0063：`NamedPipeClientStream` `isConnected` 参数已弃用**—— 接受 `bool isConnected` 参数的构造函数重载已弃用。移除 `isConnected` 参数并使用新的 3 参数构造函数。使用 `TreatWarningsAsErrors` 的项目将无法构建。

8. **`when` switch-expression-arm 解析**—— `(X.Y) when` 现在解析为具有 `when` 子句的常量模式，而不是转换表达式，这可能导致现有代码无法编译或改变含义。检查使用 `when` 的 switch 表达式并按需调整语法。

9. **Microsoft.OpenApi v3 破坏性变更**—— `Microsoft.AspNetCore.OpenApi` 现在依赖于 `Microsoft.OpenApi` 3.x。直接使用 `Microsoft.OpenApi` 类型（`OpenApiDocument`、`OpenApiSchema` 等）的代码将出现编译错误。遵循 v3 升级指南。

10. **EF Core Design 软件包不再传递**—— `Microsoft.EntityFrameworkCore.Tools` 和 `.Tasks` 不再依赖于 `.Design`。如果需要，请添加显式的 `PackageReference`。

11. **EFOptimizeContext MSBuild 属性已移除**—— 用 `<EFScaffoldModelStage>` 和 `<EFPrecompileQueriesStage>` 替换。

### 步骤 4：处理行为变化

这些变更可以成功编译，但会改变运行时行为。检查每个变更并确定影响：

1. **DeflateStream/GZipStream 空有效负载**—— 现在即使对于空有效负载也会写入头部和尾部。如果您的代码检查零长度输出，请更新检查。

2. **MemoryStream 最大容量**—— 最大容量已更新，异常行为已更改。检查创建大型 MemoryStream 或依赖特定异常类型的代码。

3. **TAR 头部校验和验证**—— TAR 读取 API 现在验证校验和。损坏或手工制作的 TAR 文件可能现在无法读取。

4. **ZipArchive.CreateAsync 主动加载**—— `ZipArchive.CreateAsync` 主动加载条目。可能会影响大型存档的内存使用。

5. **Environment.TickCount 一致性**—— 与 Windows 超时行为一致。依赖特定 tick 计数行为的代码可能需要调整。

6. **macOS 上移除 DSA**—— macOS 上 DSA 加密操作会抛出异常。使用不同的算法（RSA、ECDSA）。

7. **日本日历最小日期**—— 最小支持日期已更正。使用非常早期的日本日历日期的代码可能受影响。

8. **最小硬件要求**—— x86/x64 基线已移动到 `x86-64-v2`；Windows Arm64 需要 `LSE`。验证所有部署目标是否满足要求。

9. **Mono .NET Framework 启动目标**—— 不再自动设置。如果使用 Linux 上的 Mono for .NET Framework 应用，请显式指定。

10. **Unhandled BackgroundService 异常停止主机**—— `ExecuteAsync()` 的异常现在会传播并崩溃主机。在不应导致应用程序停止的背景服务中添加 try/catch。

11. **ZipArchive CRC32 验证**—— ZIP 读取现在验证 CRC32 校验和。损坏或截断的存档（以前可能成功）现在会抛出 `InvalidDataException`。

12. **TarWriter 发出 HardLink 条目**—— 现在将硬链接文件写入为 `HardLink` 条目，而不是重复数据。消费 .NET 生成的 tar 存档的代码必须处理 `HardLink` 条目。

13. **AIA 证书下载禁用**—— 服务器端客户端证书验证不再默认通过 AIA 下载中间 CA。预装完整链或让客户端发送中间证书。

14. **Blazor Virtualize OverscanCount 默认值已更改**—— 默认 `OverscanCount` 已从 3 更改为 15。如果对性能敏感，请显式设置。

15. **Microsoft.Data.SqlClient 7.0 — Entra ID 认证分离**—— Azure/Entra ID 认证依赖项已从核心 SqlClient 软件包中移除。如果使用 Entra ID 认证，请添加 `Microsoft.Data.SqlClient.Extensions.Azure`。

16. **SqlVector<T> 从 SELECT 排除**—— 向量属性不再自动加载。使用显式投影来包含向量值。

17. **SQLitePCLRaw 加密包已移除**—— SQLitePCLRaw 3.0 中移除了 `bundle_e_sqlcipher` 和其他加密包。

18. **NativeAOT Unix 本地库 `lib` 前缀**—— 输出文件名现在在 Linux/macOS 上包含 `lib` 前缀（例如，`libMyLib.so`）。

### 步骤 5：更新基础设施

1. **Dockerfile**：将基础镜像从 10.0 更新到 11.0：
   ```dockerfile
   # Before
   FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:10.0
   # After
   FROM mcr.microsoft.com/dotnet/sdk:11.0 AS build
   FROM mcr.microsoft.com/dotnet/aspnet:11.0
   ```

2. **CI/CD 管道**：更新 SDK 版本引用。如果使用 `global.json`，请更新现有文件中的 `sdk.version`，同时保留其他键（如 `rollForward` 和测试配置）：
   ```diff
    {
      "sdk": {
   -    "version": "10.0.100",
   -    "rollForward": "latestFeature"
   +    "version": "11.0.100-preview.3",
   +    "rollForward": "latestFeature"
      },
      "otherSettings": {
        "...": "..."
      }
    }
   ```

3. **硬件部署目标**：验证所有部署目标是否满足更新的最小硬件要求（x86/x64 为 `x86-64-v2`，Windows Arm64 需要 `LSE`）。

### 步骤 6：验证

1. 运行完整干净构建：`dotnet build --no-incremental`
2. 运行所有测试：`dotnet test`
3. 如果应用程序是容器化的，构建和测试容器镜像
4. 对应用程序进行冒烟测试，特别关注：
   - 空流中的压缩行为
   - TAR 文件读取（校验和验证和 HardLink 条目）
   - EF Core Cosmos DB 操作（必须是异步的）
   - macOS 上的 DSA 使用
   - 内存密集型 MemoryStream 使用
   - Span 集合表达式分配
   - BackgroundService 异常处理
   - mTLS / 客户端证书链验证
   - EF Core SQL Server 与 Entra ID 认证
   - Unix 上的 NativeAOT 输出文件名
5. 检查差异，确保未引入任何意外的行为变化

## 参考文档

`references/` 文件夹包含按技术领域组织的详细破坏性变更信息。仅加载与正在迁移的项目相关的参考文档：

| 参考文件 | 何时加载 |
|----------------|-------------|
| `references/csharp-compiler-dotnet10to11.md` | 总是（C# 15 编译器破坏性变更） |
| `references/core-libraries-dotnet10to11.md` | 总是（适用于所有 .NET 11 项目） |
| `references/sdk-msbuild-dotnet10to11.md` | 总是（SDK 和构建工具变更） |
| `references/aspnetcore-dotnet10to11.md` | 项目使用 ASP.NET Core（OpenAPI、Blazor） |
| `references/efcore-dotnet10to11.md` | 项目使用 Entity Framework Core |
| `references/cryptography-dotnet10to11.md` | 项目使用加密 API、mTLS 或目标 macOS |
| `references/runtime-jit-dotnet10to11.md` | 部署到较旧硬件、嵌入式设备或使用 NativeAOT |
