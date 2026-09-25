# 基于文件的 C# 应用

## 使用场景

- 使用基于文件的快速应用程序测试 C# 概念、API 或语言特性
- 在将其集成到大型项目之前进行逻辑原型设计
- 使用一个入口点文件和几个辅助 `.cs` 文件构建小型实用工具

## 不适用场景

- 用户要求语言无关的快速脚本、一次性计算或 shell/Python/PowerShell 风格的自动化
- 用户需要一个完整的项目、解决方案集成或在现有应用程序中存在项目引用
- 用户正在现有 .NET 解决方案中工作并希望在其中添加代码
- 应用程序足够大，以至于项目结构、构建自定义、测试或发布配置应存储在 `.csproj` 中

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------|
| C# 代码或意图 | 是 | 要运行的代码，或对基于文件的应做什么的描述 |

## 工作流程

### 第 1 步：检查 .NET SDK 版本

运行 `dotnet --version` 以验证 SDK 是否已安装并记下完整版本，包括功能带。基于文件的应使用 .NET 10 或更高版本。`#:include`、`#:exclude` 和传递指令处理需要 SDK 10.0.300 或更高版本；SDK 10.0.100/10.0.200 构建可以运行单文件应用程序，但不支持这些多文件指令。如果版本低于 10，请改用 [旧版 SDK 的回退方案](#fallback-for-net-9-and-earlier)。

### 第 2 步：编写应用文件

使用顶级语句创建一个入口点 `.cs` 文件。将其放置在任何现有项目目录之外，以避免与 `.csproj` 文件冲突。

```csharp
#!/usr/bin/env dotnet
// hello.cs
Console.WriteLine("来自基于文件的应的问候！");

var numbers = new[] { 1, 2, 3, 4, 5 };
Console.WriteLine($"总和: {numbers.Sum()}");
```

指南：

- 使用顶级语句（没有 `Main` 方法、类或命名空间样板）
- 将 `using` 指令放在文件顶部（在 `#!` 行和任何 `#:` 指令之后）
- 将类型声明（类、记录、枚举）放在所有顶级语句之后

### 第 3 步：运行应用

```bash
dotnet hello.cs
```

自动构建并运行文件。已缓存，因此后续运行速度快。在 `--` 后传递参数：

```bash
dotnet hello.cs -- arg1 arg2 "多词参数"
```

### 第 4 步：添加指令（如果需要）

在文件顶部放置指令（在可选的 shebang 行之后），在 `using` 指令或其他 C# 代码之前。所有指令都以 `#:` 开头。

#### `#:package` — NuGet 包引用

指定版本，除非应用程序有意使用中心包管理。使用 `@*` 当可用的最新包可以接受时（或 `@*-*` 用于预发布）：

```csharp
#:package Humanizer@2.14.1

using Humanizer;

Console.WriteLine("hello world".Titleize());
```

#### `#:property` — MSBuild 属性

内联设置任何 MSBuild 属性。语法：`#:property PropertyName=Value`

```csharp
#:property AllowUnsafeBlocks=true
#:property PublishAot=false
#:property NoWarn=CS0162
```

支持 MSBuild 表达式和属性函数：

```csharp
#:property LogLevel=$([MSBuild]::ValueOrDefault('$(LOG_LEVEL)', 'Information'))
```

常见属性：

| 属性 | 目的 |
|------|------|
| `AllowUnsafeBlocks=true` | 启用 `unsafe` 代码 |
| `PublishAot=false` | 禁用原生 AOT（默认启用） |
| `NoWarn=CS0162;CS0219` | 抑制特定警告 |
| `LangVersion=preview` | 启用预览语言特性 |
| `InvariantGlobalization=false` | 启用特定文化的全球化 |

#### `#:project` — 项目引用

通过相对路径引用另一个项目：

```csharp
#:project ../MyLibrary/MyLibrary.csproj
```

#### `#:ref` — 基于文件的应引用

当它应该编译成单独的程序集而不是包含在相同的编译中时，将另一个 `.cs` 文件作为单独的基于文件的应项目引用。当您希望项目引用边界时，使用 `#:include` 用于普通辅助文件，这些文件应与入口点共享相同的程序集；使用 `#:ref`。

```csharp
#:property ExperimentalFileBasedProgramEnableRefDirective=true
#:ref ../Shared/Formatter.cs

Console.WriteLine(Formatter.Title("hello world"));
```

指南：

- 被引用的文件作为其自己的虚拟项目编译，并作为项目引用添加。
- 如果被引用的文件是一个没有顶级语句的库，请在该引用文件中放置 `#:property OutputType=Library`。
- 必须被引用的应用程序消费的成员应该是公有的；内部成员在程序集边界处不可见。
- `#:ref` 是传递的：被引用的文件可以包含它自己的 `#:ref` 和其他 `#:` 指令。
- 相对路径相对于包含指令的文件解析。
- 某些 SDK 构建需要 `#:property ExperimentalFileBasedProgramEnableRefDirective=true`；如果 SDK 接受 `#:ref` 而不需要它，请删除该属性。

#### `#:sdk` — SDK 选择

覆盖默认 SDK (`Microsoft.NET.Sdk`)：

```csharp
#:sdk Microsoft.NET.Sdk.Web
```

#### `#:include` 和 `#:exclude` — 多文件应

在 .NET SDK 10.0.300 及更高版本中，基于文件的应可以包含同一虚拟项目中的其他文件。在使用这些指令之前检查完整的 `dotnet --version` 输出；10.0.100 或 10.0.200 SDK 仍然是 .NET 10，但它们不支持它们。使用 `#:include` 用于辅助源文件和支持的资产，并使用 `#:exclude` 从包含模式或默认项集中删除文件。

```csharp
#!/usr/bin/env dotnet
#:include Helpers.cs
#:include Models/*.cs
#:exclude Models/Generated/*.cs

Console.WriteLine(Formatter.Title("hello world"));
```

指南：

- 将传递给 `dotnet` 的文件视为入口点；将顶级语句放在那里。
- 将类、记录和枚举等声明放在包含的 `.cs` 文件中。
- 优先使用显式通配符，如 `Helpers.cs` 或 `Models/*.cs`，而不是广泛的递归通配符。
- 路径相对于包含指令的文件解析。
- 来自非入口点 C# 文件的包含指令也会被处理，因此辅助文件可以声明它自己的 `#:package`、`#:property`、`#:sdk`、`#:project`、`#:ref`、`#:include` 或 `#:exclude` 指令。
- 除非指令类型明确支持重复，否则避免在包含文件中跨重复指令；重复的 `#:package`、`#:property`、`#:sdk`、`#:include` 和 `#:exclude` 条目可能会失败。
- 当应用程序使用 `#:include` 时，在类 Unix 系统的入口点文件上添加 shebang (`#!/usr/bin/env dotnet`)，以便工具可以清楚地了解入口点。使用 `LF` 行尾和没有 BOM 的 shebang 文件。

示例布局：

```text
scratch/
    hello.cs
    Helpers.cs
    Models/
        Person.cs
```

```csharp
#!/usr/bin/env dotnet
// hello.cs
#:include Helpers.cs
#:include Models/*.cs

var person = new Person("Ada");
Console.WriteLine(Formatter.Title(person.Name));
```

```csharp
// Helpers.cs
static class Formatter
{
    public static string Title(string value) => value.ToUpperInvariant();
}
```

```csharp
// Models/Person.cs
record Person(string Name);
```

### 第 5 步：清理

当用户完成时删除应用文件。要清除缓存的构建工件：

```bash
dotnet clean hello.cs
```

## Unix shebang 支持

在 Unix 平台上，使 `.cs` 文件可直接执行：

1. 将 shebang 作为文件的第一行添加：

    ```csharp
    #!/usr/bin/env dotnet
    Console.WriteLine("我是可执行的！");
    ```

2. 设置执行权限：

    ```bash
    chmod +x hello.cs
    ```

3. 直接运行：

    ```bash
    ./hello.cs
    ```

添加 shebang 时使用 `LF` 行尾（不要使用 `CRLF`）。此指令在 Windows 上被忽略。

## 源生成的 JSON

基于文件的应默认启用原生 AOT。在 AOT 下，基于反射的 API（如 `JsonSerializer.Serialize<T>(value)`）在运行时失败。改用源生成序列化：

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;

var person = new Person("Alice", 30);
var json = JsonSerializer.Serialize(person, AppJsonContext.Default.Person);
Console.WriteLine(json);

var deserialized = JsonSerializer.Deserialize(json, AppJsonContext.Default.Person);
Console.WriteLine($"姓名: {deserialized!.Name}, 年龄: {deserialized.Age}");

record Person(string Name, int Age);

[JsonSerializable(typeof(Person))]
partial class AppJsonContext : JsonSerializerContext;
```

## 转换为项目

当基于文件的应超出此工作流程时，将其转换为完整项目：

```bash
dotnet project convert hello.cs
```

## .NET 9 及更早版本的回退方案

如果 .NET SDK 版本低于 10，则基于文件的应不可用。使用临时控制台项目代替：

```bash
mkdir -p /tmp/csharp-file-based-app && cd /tmp/csharp-file-based-app
dotnet new console -o . --force
```

用应用内容替换生成的 `Program.cs` 并使用 `dotnet run` 运行。使用 `dotnet add package <name>` 添加 NuGet 包。完成后删除目录。

## 验证

- [ ] `dotnet --version` 报告 10.0 或更高版本（或使用回退路径）
- [ ] 如果应用程序使用 `#:include`，则 `dotnet --version` 报告 SDK 10.0.300 或更高版本
- [ ] 应用程序编译没有错误（可以使用 `dotnet build <file>.cs` 明确检查）
- [ ] `dotnet <file>.cs` 产生预期输出
- [ ] 多文件应用程序包含每个必需的辅助文件并排除意外匹配
- [ ] 应用程序文件和缓存的工件在会话后清理

## 常见陷阱

| 陷阱 | 解决方案 |
|------|---------|
| `.cs` 文件位于包含 `.csproj` 的目录中 | 将应用程序移出项目目录，或使用 `dotnet run --file file.cs` |
| `#:package` 而没有版本 | 指定版本：`#:package PackageName@1.2.3` 或 `@*` 用于最新版本 |
| `#:property` 语法错误 | 使用 `PropertyName=Value`，`=` 两侧没有空格，没有引号：`#:property AllowUnsafeBlocks=true` |
| 指令放置在 C# 代码之后 | 所有 `#:` 指令必须出现在可选 shebang 行（如果存在）之后，以及任何 `using` 指令或其他 C# 语句之前 |
| 辅助文件未编译 | 在入口点文件中添加 `#:include Helper.cs` 或适当的通配符 |
| 需要程序集边界的共享文件 | 使用 `#:ref Shared.cs` 而不是 `#:include Shared.cs`，如果引用文件没有入口点，则在引用文件中设置 `#:property OutputType=Library` |
| 广泛的包含拉入不相关的文件 | 优先使用狭窄的包含模式，并使用 `#:exclude` 删除生成的、备份的或实验性的文件 |
| 包含文件中的重复指令 | 保持包、属性、SDK、包含和排除指令在入口点和包含的 C# 文件中唯一 |
| 基于反射的 JSON 序列化失败 | 使用源生成 JSON 并使用 `JsonSerializerContext`（见 [源生成的 JSON](#source-generated-json)） |
| 预期之外的构建行为或版本错误 | 基于文件的应继承自父目录的 `global.json`、`Directory.Build.props`、`Directory.Build.targets` 和 `nuget.config`。如果继承的设置冲突，请将应用程序移动到隔离目录 |

## 更多信息

有关基于文件的应的完整参考，请参阅 https://learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps。
