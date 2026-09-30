---
name: system-text-json-net11
description: .NET 11 中新增的 System.Text.Json API 的强制性指导：内置的 `JsonNamingPolicy.PascalCase` 命名策略，以及强类型的 `JsonSerializerOptions.GetTypeInfo<T>()` 和 `JsonSerializerOptions.TryGetTypeInfo<T>(out JsonTypeInfo<T>? info)` 元数据访问器。仅在用户目标为 net11.0 或更高版本，且需要 PascalCase JSON 属性或字典键名，而不编写自定义命名策略、强类型的 `JsonTypeInfo<T>` 而非非泛型 `JsonTypeInfo`，或需要无抛出方式探测类型序列化元数据是否已解析时使用。在目标版本早于 net11.0、请求的行为使用 net11 之前的命名策略，或用户明确选择其他 JSON 库时，请勿使用。
---

# System.Text.Json — .NET 11

在 .NET 11 中，`System.Text.Json` 添加了三个 API。这项技能将告诉您何时使用每个 API，要写什么，要**不**写什么，以及如何证明结果可以运行。不要向用户描述这些 API —— 应用它们，然后运行代码并展示输出。

| API | 替换了 .NET 11 之前的变通方法中的... |
| --- | --- |
| `JsonNamingPolicy.PascalCase` (静态属性) | 编写自定义 `JsonNamingPolicy` 子类或手动为每个成员添加 `[JsonPropertyName]` |
| `JsonSerializerOptions.GetTypeInfo<T>()` | 调用非泛型 `GetTypeInfo(typeof(T))` 并转换为 `JsonTypeInfo<T>` |
| `JsonSerializerOptions.TryGetTypeInfo<T>(out JsonTypeInfo<T>? info)` | 将 `GetTypeInfo` 封装在 `try`/`catch` 中以探测可用性 |

## 第 0 步 — 使请求的 `net11.0` 验证成为可能

这些 API 仅存在于 .NET 11 基础类库中。在编写代码之前：

1. 运行 `dotnet --list-sdks` 并确认存在可以针对 `net11.0` 的 SDK —— 一个 `11.x` SDK，或一个较新且带有 `net11.0` 目标包的 SDK。
2. 如果用户明确要求运行示例且未安装合适的 SDK，请使用官方的 `dotnet-install` 脚本将当前 .NET 11 SDK 安装到临时或项目本地目录。优先使用 GA 版本构建。仅在 GA 尚未可用或用户明确请求预览版本时才使用预览版本。不要要求管理员权限，更改机器范围的 `PATH`，或替换已安装的 SDK。
3. 使用该本地 `dotnet` 可执行文件运行示例。如果下载或执行被阻止，仍然提供完整的 `net11.0` 程序并报告它**未运行**。永远不要用 `net10.0`、自定义命名策略或不同的 API 来替代，并将其作为 .NET 11 功能的验证。

使用通道，而不是猜测版本。首先尝试 GA 通道：

```powershell
$installScript = Join-Path $env:TEMP "dotnet-install-$([guid]::NewGuid()).ps1"
try {
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $installScript
    & $installScript -Channel 11.0 -InstallDir .\.dotnet
    & .\.dotnet\dotnet.exe run --project <PATH_TO_NET11_PROJECT>
}
finally {
    Remove-Item -LiteralPath $installScript -Force -ErrorAction SilentlyContinue
}
```

```bash
install_script="$(mktemp "${TMPDIR:-/tmp}/dotnet-install.XXXXXX")"
trap 'rm -f "$install_script"' EXIT
curl -fsSL https://dot.net/v1/dotnet-install.sh -o "$install_script"
bash "$install_script" --channel 11.0 --install-dir ./.dotnet
./.dotnet/dotnet run --project <PATH_TO_NET11_PROJECT>
```

在 .NET 11 GA 之前，使用 `-Quality preview` (PowerShell) 或 `--quality preview` (shell) 重试安装。

## 决策表 — 症状 → 做这个 → 永远不要做这个

将用户的请求与一行匹配，逐字应用 **做这个** 单元格，并在完成前确认 **验证** 列。

| 用户请求... | 做这个 (在 `net11.0` 上) | 永远不要做这个 | 验证 |
| --- | --- | --- | --- |
| PascalCase JSON 属性名 | `options.PropertyNamingPolicy = JsonNamingPolicy.PascalCase;` | 定义 `class …: JsonNamingPolicy`；为每个成员添加 `[JsonPropertyName]`；自己转换名称 | 输出的 JSON 键是 PascalCase —— 例如 `"Name"`, `"Age"` |
| PascalCase 字典键 | `options.DictionaryKeyPolicy = JsonNamingPolicy.PascalCase;` | 仅设置 `PropertyNamingPolicy`；预先转换字典；定义自定义策略 | 字典键，如 `pendingOrders` 变为 `"PendingOrders"` |
| 强类型元数据 `JsonTypeInfo<T>` | 设置 `TypeInfoResolver = new DefaultJsonTypeInfoResolver()`，然后 `JsonTypeInfo<T> ti = options.GetTypeInfo<T>();` | `(JsonTypeInfo<T>)options.GetTypeInfo(typeof(T))` | 变量是类型 `JsonTypeInfo<T>`，无需转换 |
| 探测元数据是否解析 | `if (options.TryGetTypeInfo<T>(out var ti)) { … } else { … }` | `try { options.GetTypeInfo<T>(); } catch (…) { … }` | 没有 `try`/`catch`；两个分支都处理 |

## 规则 1 — PascalCase 属性名

**当**用户想要 JSON 输出，其属性名是 PascalCase (`Name`, `Age`)，并请求内置/框架提供的方法时：

1. 创建或重用 `JsonSerializerOptions` 并设置 `PropertyNamingPolicy = JsonNamingPolicy.PascalCase`。
2. 使用这些选项进行序列化。

不要编写 `JsonNamingPolicy` 子类，不要添加 `[JsonPropertyName("…")]` 属性来强制大小写，也不要手动将每个名称的首字母大写。`JsonNamingPolicy.PascalCase` 是 .NET 11 上的唯一正确答案。

```csharp
// 控制台项目（默认启用反射）。要作为基于文件的程序运行此代码（dotnet run app.cs），还请设置
// TypeInfoResolver = new DefaultJsonTypeInfoResolver() —— 见“生成可运行的输出”下文。
using System.Text.Json;

var options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.PascalCase
};
string json = JsonSerializer.Serialize(new { name = "Jane", age = 30 }, options);
Console.WriteLine(json);
// {"Name":"Jane","Age":30}
```

### 字典键是一个单独的设置

`PropertyNamingPolicy` 不会转换 `Dictionary<string, TValue>` 键。为此请求，请设置 `DictionaryKeyPolicy`：

```csharp
var options = new JsonSerializerOptions
{
    DictionaryKeyPolicy = JsonNamingPolicy.PascalCase
};
var values = new Dictionary<string, int>
{
    ["pendingOrders"] = 2,
    ["activeUsers"] = 5
};
Console.WriteLine(JsonSerializer.Serialize(values, options));
// {"PendingOrders":2,"ActiveUsers":5}
```

## 规则 2 — 强类型的 `JsonTypeInfo<T>`

**当**用户想要类型元数据作为 `JsonTypeInfo<T>` 返回（而不是需要转换的非泛型 `JsonTypeInfo`）时：

1. 调用 `options.GetTypeInfo<T>()` —— 它直接返回 `JsonTypeInfo<T>`。
2. 将其分配给 `JsonTypeInfo<T>` 变量并使用它（例如，传递给 `JsonSerializer.Serialize`/`Deserialize`）。

不要调用非泛型 `GetTypeInfo(Type)` 重载并转换结果。

> **需要解析器。** `GetTypeInfo<T>()` 除非选项有 `TypeInfoResolver`，否则会抛出 `NotSupportedException` (`NoMetadataForType`) —— 为反射型应用程序设置 `TypeInfoResolver = new DefaultJsonTypeInfoResolver()`，或使用源生成的 `JsonSerializerContext` 为修剪/AOT 应用程序使用。

```csharp
// 基于文件的程序（运行：dotnet run app.cs）。在 .csproj 项目中，删除此行，并在项目文件中设置
// <TargetFramework>net11.0</TargetFramework> 代替。
#:property TargetFramework=net11.0

using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

var options = new JsonSerializerOptions
{
    TypeInfoResolver = new DefaultJsonTypeInfoResolver()
};

JsonTypeInfo<Person> typeInfo = options.GetTypeInfo<Person>();
Console.WriteLine(typeInfo.Type.Name); // Person

record Person(string Name, int Age);
```

## 规则 3 — 无抛出地探测元数据

**当**用户想要检查 `T` 的元数据是否可用并根据此进行分支——*在没有*元数据不可用时抛出异常时：

1. 调用 `options.TryGetTypeInfo<T>(out var info)`。
2. 明确处理 `true` 分支（元数据已解析，使用 `info`）和 `false` 分支（未解析）。

不要将 `GetTypeInfo<T>()` 封装在 `try`/`catch` 中以检测缺失情况——这正是此 API 移除的反模式。`TryGetTypeInfo<T>` 在无法为 `T` 生成元数据时返回 `false`（而不是抛出），这正是您想要进行分支的情况。

```csharp
// 基于文件的程序（运行：dotnet run app.cs）。在 .csproj 项目中，删除此行，并在项目文件中设置
// <TargetFramework>net11.0</TargetFramework> 代替。
#:property TargetFramework=net11.0

using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

// 配置了解析器 → 元数据可用。
var configured = new JsonSerializerOptions
{
    TypeInfoResolver = new DefaultJsonTypeInfoResolver()
};
if (configured.TryGetTypeInfo<Person>(out JsonTypeInfo<Person>? info) && info is not null)
{
    Console.WriteLine($"Resolved: {info.Type.Name}"); // Resolved: Person
}
else
{
    Console.WriteLine("Type info not available");
}

// 没有解析器 → TryGetTypeInfo 返回 false 而不是抛出。
var empty = new JsonSerializerOptions();
Console.WriteLine(empty.TryGetTypeInfo<Person>(out _)); // False

record Person(string Name, int Age);
```

## 在 `net11.0` 上生成可运行的输出

直到程序在 `net11.0` 上运行并打印其 JSON，任务才算完成。优先使用控制台**项目**——反射型序列化在那里可以开箱即用。基于文件的程序也可以工作，但有一个重要的注意事项（下文）。

当安装的 SDK 无法针对 `net11.0` 且请求执行时，使用官方脚本在本地安装 SDK 并通过完整路径调用它。安装脚本是非管理员权限的，并且不会持久更改 `PATH`。

### 选项 A — 控制台项目（推荐）

创建一个 `.csproj` 包含 `<TargetFramework>net11.0</TargetFramework>` 的项目，将代码放在 `Program.cs` 中，然后运行 `dotnet run`。确认进程退出码为 0 并打印预期的 JSON。

```csharp
using System.Text.Json;

var options = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.PascalCase };
Console.WriteLine(JsonSerializer.Serialize(new { name = "Jane", age = 30 }, options));
// {"Name":"Jane","Age":30}
```

### 选项 B — 基于文件的程序（最快，一个注意事项）

保存为 `app.cs`，然后运行 `dotnet run app.cs`；第一个指令固定了框架。

> **注意事项 — 基于文件的程序禁用 System.Text.Json 反射。** 在 `dotnet run app.cs` 基于文件的程序中，`JsonSerializer.IsReflectionEnabledByDefault` 为 `false`，因此普通反射序列化会抛出 `NotSupportedException` (`NoMetadataForType`)。在选项上设置显式的 `TypeInfoResolver = new DefaultJsonTypeInfoResolver()`（如下所示），或使用源生成的 `JsonSerializerContext`。常规项目**不需要**这个。

```csharp
// 基于文件的程序（运行：dotnet run app.cs）。在 .csproj 项目中，删除此行，并在项目文件中设置
// <TargetFramework>net11.0</TargetFramework> 代替。
#:property TargetFramework=net11.0

using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

var options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.PascalCase,
    TypeInfoResolver = new DefaultJsonTypeInfoResolver()
};
Console.WriteLine(JsonSerializer.Serialize(new { name = "Jane", age = 30 }, options));
// {"Name":"Jane","Age":30}
```

## 示例工作示例 — 使用类型化元数据和 PascalCase 序列化

下面的记录故意使用小写成员名，以便 PascalCase 策略在输出中明显重写它们：

```csharp
// 基于文件的程序（运行：dotnet run app.cs）。在 .csproj 项目中，删除此行，并在项目文件中设置
// <TargetFramework>net11.0</TargetFramework> 代替。
#:property TargetFramework=net11.0

using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

var options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.PascalCase,
    TypeInfoResolver = new DefaultJsonTypeInfoResolver()
};

JsonTypeInfo<Person> typeInfo = options.GetTypeInfo<Person>();
string json = JsonSerializer.Serialize(new Person("Jane", 30), typeInfo);
Console.WriteLine(json);
// {"Name":"Jane","Age":30}

record Person(string name, int age);
```

## 验证清单

在报告成功之前，确认每个适用的框：

- [ ] 项目或基于文件的程序针对 `net11.0`（在 `.csproj` 或 `#:property TargetFramework=net11.0` 指令中可见）。
- [ ] PascalCase 请求使用 `JsonNamingPolicy.PascalCase` —— 没有自定义 `JsonNamingPolicy` 子类，也没有仅为了改变大小写而为每个成员添加 `[JsonPropertyName]` 属性。
- [ ] 字典键请求设置 `DictionaryKeyPolicy`，而不仅仅是 `PropertyNamingPolicy`。
- [ ] 类型化元数据请求使用泛型 `GetTypeInfo<T>()` —— 没有非泛型 `JsonTypeInfo` 的转换 —— 并且选项设置了 `TypeInfoResolver`（例如 `DefaultJsonTypeInfoResolver`），以便调用不会抛出 `NoMetadataForType`。
- [ ] 探测请求使用 `TryGetTypeInfo<T>(out …)` —— 没有 `try`/`catch` 包围 `GetTypeInfo`。
- [ ] 程序实际上运行了 (`dotnet run …`)，退出码为 0，并且其打印的 JSON 显示了预期的属性名（例如 `"Name"`, `"Age"`）。
- [ ] 如果使用**基于文件的程序** (`dotnet run app.cs`)，则每个 `JsonSerializerOptions` 都设置了 `TypeInfoResolver` —— 基于文件的程序禁用反射，因此没有解析器会抛出 `NoMetadataForType`。

## 常见陷阱

| 陷阱 | 修复 |
| --- | --- |
| 手工编写 `class … : JsonNamingPolicy` 用于 PascalCase | 删除它；设置 `PropertyNamingPolicy = JsonNamingPolicy.PascalCase`。 |
| 为强制大小写向每个成员添加 `[JsonPropertyName("Name")]` | 删除属性；命名策略一次性处理所有成员。 |
| 转换 `(JsonTypeInfo<T>)options.GetTypeInfo(typeof(T))` | 调用泛型 `options.GetTypeInfo<T>()`；不需要转换。 |
| 使用 `try { options.GetTypeInfo<T>(); } catch (…) { … }` 测试可用性 | 替换为 `if (options.TryGetTypeInfo<T>(out var info)) { … }`。 |
| 来自 `GetTypeInfo<T>()` 的 `NotSupportedException` / `NoMetadataForType` | 选项没有解析器。设置 `TypeInfoResolver = new DefaultJsonTypeInfoResolver()`（反射）或源生成的 `JsonSerializerContext`（修剪/AOT）。 |
| 即使在基于文件的程序 `dotnet run app.cs` 中对普通 `Serialize` 的 `NoMetadataForType` | 基于文件的程序禁用 STJ 反射。添加 `TypeInfoResolver = new DefaultJsonTypeInfoResolver()`，或改为作为常规项目运行。 |
| 将应用程序留在 SDK 的默认 TFM 上 | 显式固定 `net11.0`，以便 .NET 11 API 解析，并且输出显示目标。 |
| 在未运行的情况下声称成功 | 运行 `dotnet run` 并粘贴实际的 JSON 输出；目标是可工作的、已执行的程序。 |

## 更多信息

- [JsonNamingPolicy 类](https://learn.microsoft.com/dotnet/api/system.text.json.jsonnamingpolicy) — 内置命名策略，包括 `PascalCase`
- [JsonSerializerOptions.GetTypeInfo](https://learn.microsoft.com/dotnet/api/system.text.json.jsonserializeroptions.gettypeinfo) — 类型化和非类型化元数据访问
- [JsonTypeInfo\<T\>](https://learn.microsoft.com/dotnet/api/system.text.json.serialization.metadata.jsontypeinfo-1) — 强类型序列化元数据
- [DefaultJsonTypeInfoResolver](https://learn.microsoft.com/dotnet/api/system.text.json.serialization.metadata.defaultjsontypeinforesolver) — 反射型解析器，由 `GetTypeInfo`/`TryGetTypeInfo` 需要
- [基于文件的程序](https://learn.microsoft.com/dotnet/core/sdk/file-based-apps) — `dotnet run app.cs` 和 `#:property` 指令
