# 检测静态依赖

扫描 C# 代码库中难以测试的静态 API 调用，并生成一个排名报告，显示哪些静态成员出现频率最高，哪些文件受影响最严重，以及 .NET 生态系统中的哪些抽象可以用来替换它们。

## 使用场景

- 在添加单元测试之前审计项目的可测试性
- 了解遗留代码库中静态耦合的范围
- 优先处理哪些静态成员需要首先封装（频率最高的优先）
- 创建一个用于逐步提高可测试性的迁移计划

## 响应指南

- 根据用户请求调整响应的详细程度。例如，关于特定类别（如“查找时间静态成员”）的问题应专注于该类别，包括文件位置和计数，而不是生成涵盖所有类别的完整报告。
- 当用户提供特定的文件或目录路径时，仅扫描该范围——除非用户明确要求，否则不要扩展到整个解决方案。
- 完整的结构化报告格式（步骤 4）适用于全面的审计请求。对于有针对性的问题，只需返回相关的子集（例如，类别摘要 + 请求类别的受影响文件）。

## 执行协议

- 提示中命名的相对路径足以开始。使用可用的文件列表工具发现它，并立即扫描；在发现和内容搜索均失败之前，不要要求用户提供或重新上传文件。
- 从递归、带行号的内容搜索开始，扫描所有符合条件的 `.cs` 文件。不要仅搜索 `static` 关键字：LINQ 表达式、lambda 表达式、回调和插值字符串中的环境调用通常没有 `static` 修饰符。
- 如果文件读取工具在已证明存在的路径上失败，请在重试之前对失败进行分类。仅在确认工具可用性、传输或路径规范化失败，并且已验证规范路径仍然在工作区内部时，才回退到其他可用机制，如 `rg -n`、grep 或 shell 文件读取器。在内容排除、权限/策略、工作区边界或未知失败时停止。搜索输出可以用于生成出现次数记录；仅打开验证接收者来源所需的周围代码。
- 加载此技能或宣布扫描计划后，永远不要停止。在相同的响应中返回完成的审计。如果每个回退都确实失败，请报告已验证的部分发现和确切限制；不要编造发现或用要求重新运行来替换审计。

## 不应使用的情况

- 用户需要生成包装器（将任务交给 `generate-testability-wrappers`）
- 用户需要执行机械迁移（将任务交给 `migrate-static-to-wrapper`）
- 静态成员已经通过接口或 `TimeProvider` 隐藏
- 代码不是 C# / .NET

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------------|
| 目标路径 | 否 | 要扫描的文件、目录、项目 (.csproj) 或解决方案 (.sln)。默认为当前工作区。 |
| 排除模式 | 否 | 要跳过的 glob 模式（例如，`**/obj/**`，`**/Migrations/**`） |
| 类别过滤器 | 否 | 限制为特定类别：`time`、`filesystem`、`environment`、`network`、`console`、`process` |

## 工作流程

### 步骤 1：确定扫描范围

将目标解析为一系列 `.cs` 文件：
- 将提示命名的相对于工作区的路径视为目标；定位它，而不是要求用户提供绝对路径。
- 如果省略，则扫描当前工作区下所有符合条件的 `.cs` 文件；不要选择一个项目并默默地忽略其兄弟项目。
- 如果是 `.cs` 文件，则扫描该单个文件。
- 如果是目录，则递归扫描所有 `.cs` 文件（排除 `obj/`、`bin/`）。
- 如果是 `.csproj`，找到其目录并扫描其中的 `.cs` 文件。
- 如果是 `.sln`，解析它，找到所有项目目录，并在所有项目中扫描 `.cs` 文件。

始终排除 `obj/`、`bin/` 和任何用户指定的排除模式。

### 步骤 2：搜索静态依赖模式

扫描每个文件以查找匹配以下类别的调用：

将模式匹配视为候选者，而不是发现。在计算实例调用之前，跟踪其接收者如何进入类。通过构造函数、参数、属性或依赖注入（DI）提供的协作者已经是可测试的接缝。特别是，注入的 `HttpClient` 可以使用受控的 `HttpMessageHandler` 进行测试；不要因为注入的类型是具体的而计算其调用或建议替换它。

| 类别 | 搜索模式 | 推荐替换 |
|------|----------|----------|
| **时间** | `DateTime.Now`、`DateTime.UtcNow`、`DateTime.Today`、`DateTimeOffset.Now`、`DateTimeOffset.UtcNow`、`Task.Delay(`、`new CancellationTokenSource(TimeSpan` | `TimeProvider` (.NET 8+) |
| **文件系统** | `File.ReadAllText(`、`File.WriteAllText(`、`File.Exists(`、`File.Delete(`、`File.Copy(`、`File.Move(`、`Directory.Exists(`、`Directory.CreateDirectory(`、`Directory.GetFiles(`、`Directory.Delete(`、`Path.GetTempPath(`，以及访问磁盘的实例成员（`new FileInfo(...)`、`new DirectoryInfo(...)`、`.LastWriteTimeUtc`、`new StreamReader(path)`） | `IFileSystem` (System.IO.Abstractions NuGet) |
| **随机性 / 身份** | `new Random(`、`Random.Shared`、`Guid.NewGuid(`) | `TimeProvider` 风格的接缝：注入 `Random` / `IGuidProvider` |
| **文化 / 序列化** | `CultureInfo.CurrentCulture`、`CultureInfo.CurrentUICulture`、`JsonSerializer.Serialize(`、`JsonSerializer.Deserialize(`) | 显式传递文化/选项，或注入序列化抽象 |
| **环境** | `Environment.GetEnvironmentVariable(`、`Environment.SetEnvironmentVariable(`、`Environment.MachineName`、`Environment.UserName`、`Environment.CurrentDirectory`、`Environment.Exit(`) | 自定义 `IEnvironmentProvider` |
| **网络** | `new HttpClient(`、`.GetAsync(`、`.PostAsync(`、`.SendAsync(`（确认接收者是 `HttpClient`；排除接收者由注入或由注入工厂产生的调用） | 注入 `HttpClient`（通常由 `IHttpClientFactory` 提供） |
| **控制台** | `Console.WriteLine(`、`Console.ReadLine(`、`Console.Write(`、`Console.ReadKey(`) | `IConsole` 包装器或 `ILogger` |
| **进程** | `Process.Start(`、`Process.GetCurrentProcess(`、`Process.GetProcessesByName(`) | 自定义 `IProcessRunner` |

对于时间调用，检查使用情况以及计数。在一个逻辑操作中两个环境时钟读取是两个调用位置和一个一致性缺陷：例如，`CreatedAt` 和 `ExpiresAt = DateTime.UtcNow.AddDays(30)` 的两个 `DateTime.UtcNow` 读取可能会漂移。建议一个捕获的瞬间。使用 `TimeProvider` 时，尽可能保留 `DateTimeOffset`；当现有成员需要 UTC `DateTime` 时，使用 `GetUtcNow().UtcDateTime`，永远不要 `.DateTime`，这会丢失 UTC 样式。将捕获一个瞬间视为可选的行为级后续操作：机械包装器迁移必须一对一地保留原始读取，除非用户单独批准了语义更改。

### 步骤 3：汇总和排名结果

在整个扫描范围内计算每个调用位置——包括由以下规则覆盖的实例成员调用位置，而不仅仅是 `static` 的。

**计数规则——不准确的总量是此报告输给临时扫描的主要原因：**

- **在编写文本之前构建一个出现次数记录。** 给每个包含的调用位置恰好一行，包含类别、确切模式、`file:line` 和推荐接缝。通过分组该记录来导出每个类别、模式和每个文件的计数；在编写表格时，永远不要独立重新计数。
- **保持三个计数域分开。** `Files scanned` 包括每个符合条件的源文件；`affected files` 仅包括包含记录的文件；`call sites` 是记录的数量。永远不要用一个替换另一个。
- **一个权威的总计。** 你发现的每个调用位置都属于类别摘要和总计。永远不要将真实发现放在“附加观察”部分，而总计会排除它。
- **根据成员触及的内容进行分类，而不是根据它是否是 `static`。** 访问相同不可测试资源的实例成员仍然计算并属于匹配的类别（`new FileInfo(path).LastWriteTimeUtc` → 文件系统；`new HttpClient().GetAsync(...)` → 网络）。当成员是实例调用时，说“隐藏依赖”，而不是“静态”。
- **在计数实例调用之前检查接收者来源。** 只有当测试代码本身获取或构建依赖项时，才计算资源访问。排除构造函数、参数、属性和 DI 注入的协作者，包括具体的 `HttpClient` 实例，从“需要封装”总计中排除。
- **从“需要封装”总计中排除确定性纯辅助函数。** `Path.Combine`、`Path.GetExtension`、`Path.GetFileName`，以及 `Math.*`/`string.*` 静态只接受没有环境输入，并且可以轻松测试。如果列出，请将其放在单独的“无需操作”笔记中——永远不要将其作为可测试性障碍。
- **在报告之前覆盖所有类别**——时间、文件系统、环境、网络、控制台、进程、随机性（`new Random()`、`Guid.NewGuid()`）、文化（`CultureInfo.CurrentCulture`），以及序列化/静态，如 `JsonSerializer`。遗漏一个类别是低估。
- **为每个出现提供 `file:line`，以便用户可以直接跳转到它。**
- **发布前进行核对。** 类别总计、顶级模式表和每个文件表必须总和为相同的总计。
- **将排除视为范围决策，而不是类别。** 在构建记录之前，排除 `obj/`、`bin/`、生成的和用户排除的文件。不要将它们的文件或调用位置包含在任何报告计数中。一次说明排除，而不是将排除的候选者混合到算术中。
- **标记截断排名。** 在全面审计中，当需要核对时，列出所有不同的模式。如果用户只要求顶级 N 子集，则将其标记为子集，并且不要暗示其行总和为总计。

生成一个摘要，包括：

1. **类别摘要**——每个类别（时间、文件系统、环境等）的总调用位置
2. **顶级模式**——按计数排名的前 10 个最频繁的独立模式
3. **最受影响的文件**——静态依赖数量最多的文件
4. **可用的现有抽象**——对于每个类别，注意推荐的 .NET 抽象：
   - 时间 → `TimeProvider`（自 .NET 8 起内置）
   - 文件系统 → `System.IO.Abstractions`（NuGet 包）
   - HTTP → `IHttpClientFactory`（内置）
   - 环境 → 自定义 `IEnvironmentProvider`
   - 控制台 → 自定义 `IConsole` 或 `ILogger`
   - 进程 → 自定义 `IProcessRunner`

### 步骤 4：呈现报告

将输出格式化为结构化报告：

```
## 静态依赖报告

**范围**： <项目/解决方案名称>
**扫描文件数**： <数量>
**总静态调用位置**： <数量>

### 类别摘要
| 类别     | 调用位置 | 推荐抽象 |
|----------|----------|----------|
| 时间     | 42       | TimeProvider (.NET 8+) |
| 文件系统 | 31       | System.IO.Abstractions |
| 环境     | 12       | IEnvironmentProvider   |
| ...      | ...      | ...      |

### 前 10 个模式
| # | 模式             | 计数 | 文件 |
|---|------------------|------|------|
| 1 | DateTime.UtcNow  | 28   | 14   |
| 2 | File.ReadAllText  | 18   | 9    |
| ...                             |

### 最受影响的文件
| 文件                          | 静态调用 | 类别          |
|-------------------------------|----------|--------------|
| Services/OrderProcessor.cs    | 12       | 时间, 文件系统 |
| ...                            |

### 迁移优先级
1. **时间**（42 个位置）— 使用 `TimeProvider`，对 .NET 8+ 没有 NuGet 依赖
2. **文件系统**（31 个位置）— 使用 `System.IO.Abstractions` NuGet 包
3. ...

### 步骤 5：建议下一步

根据报告，建议首先处理哪个类别（计数最高，内置支持最好）。保持简短。

仅在用户的下一步操作明显需要时，才提及 `generate-testability-wrappers` 或 `migrate-static-to-wrapper`——转交笔记，而不是销售宣传。永远不要以稀释发现为代价的促销性下一步结束审计。

## 验证

- [ ] 范围内的所有 `.cs` 文件都被扫描（检查计数）
- [ ] 报告包括类别总计、顶级模式和受影响文件
- [ ] 类别总计、顶级模式和每个文件计数总和为相同的总计
- [ ] 扫描文件数、受影响文件和调用位置报告为不同的数量
- [ ] 每个聚合都来自一个出现次数记录，而不是独立重新计数
- [ ] 每个出现都带有 `file:line` 位置
- [ ] 没有发现被保留在总计之外的“附加”部分
- [ ] 注入协作者的调用从“需要封装”总计中排除
- [ ] 确定性纯辅助函数（`Path.Combine`、`Math.*`）不计为可测试性障碍
- [ ] 每个检测到的模式都有一个推荐的替换
- [ ] 排除了 `obj/` 和 `bin/` 目录
- [ ] 迁移优先级按影响（计数 × 替换的容易程度）排序

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 扫描 `obj/` 或生成代码 | 始终排除 `obj/`、`bin/` 和 `*.Designer.cs` |
| 计数注入协作者的调用 | 追踪接收者：注入的 `HttpClient`、`TimeProvider`、接口或其他调用者提供的依赖项已经有一个接缝，并且不需要替换 |
| 错过 lambda/LINQ 中的静态 | 搜索覆盖 `.cs` 文件中的所有代码，包括 lambda |
| 在 < .NET 8 时推荐 `TimeProvider` | 检查 `.csproj` 中的 `TargetFramework`——如果 < net8.0，推荐 `NodaTime.IClock` 或自定义 `ISystemClock` |
| 忽略测试项目 | 仅扫描生产代码——从扫描中排除 `*.Tests.csproj` 项目 |
| 通过将发现降级来低估 | 真实的调用位置属于类别总计，而不是在末尾的“也注意到”段落中，总计会忽略它 |
| 将实例成员称为静态 | `new FileInfo(p).LastWriteTimeUtc` 是实例调用，但仍然是隐藏的文件系统依赖——将其计入文件系统类别并准确描述 |
| 推荐为 `Path.Combine` 生成包装器 | 纯粹、确定性辅助函数不需要接缝；将它们列为障碍会使建议错误 |
