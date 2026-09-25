# 将静态依赖迁移到包装器

执行机械式、codemod 风格的替换，将静态依赖调用点替换为对注入的包装器接口或内置抽象的调用。它作用于一个有界的作用域（单个文件、项目或命名空间），以便可以增量地执行迁移。

## 何时使用

- 生成包装器（通过 `generate-testability-wrappers`）或识别内置抽象之后
- 在整个项目中迁移 `DateTime.UtcNow` → `TimeProvider.GetUtcNow()` 
- 在命名空间中迁移 `File.*` → `IFileSystem.File.*`
- 为受影响类添加新抽象的构造函数注入
- 通过添加环境分隔（步骤 3）使 `static` 工具类可测试，同时其现有的调用点保持编译不变
- 增量迁移：一次一个项目或命名空间
- 当请求的迁移命名了替换抽象时，使用假体更新受影响的测试

## 何时不使用

- 尚未存在包装器或抽象，必须从头设计（首先使用 `generate-testability-wrappers`）。
  像`TimeProvider`或`IFileSystem`这样的内置抽象始终算作已存在。
- 用户想要检测静态依赖，而不是迁移它们（使用 `detect-static-dependencies`）
- 在测试框架之间迁移（使用相应的迁移技能）
- 用户主要要求确定性行为测试，并且尚未选择生产分隔（使用 `testability-obstacle`）

> 一个 `static` 类或没有依赖注入容器的项目**不是**跳过此技能的理由——这正是步骤 3 中的环境分隔的目的。当调用点必须保持编译不变时，随时使用它。

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------------|
| 静态模式 | 否 | 从请求和发现的调用点推断（例如，`DateTime.UtcNow`、`File.ReadAllText`） |
| 替换抽象 | 否 | 从请求和现有项目抽象推断；只有在没有命名/现有抽象可用时才停止 |
| 范围 | 否 | 从请求的文件/项目/命名空间推断，否则发现最窄的相关工作区范围 |
| 注入策略 | 否 | `constructor`（默认）、`primary-constructor` 或 `ambient` |

## 工作流程

### 不可协商的迁移边界

- **缺少抽象意味着停止。** 如果命名的接口/包不存在，并且请求仅授权调用点替换，则不要添加包、发明本地类似接口或编辑生产代码。报告确切的缺失先决条件以及继续所需的授权。
- **一个源读取保持一个替换读取。** 不要提升或合并调用，即使共享捕获的时间戳看起来更整洁。
- **请求的范围是详尽且排他的。** 替换范围内的每个命名调用，并且不修改相邻的成员或文件。
- **基于存储库的请求需要存储库工作。** 从当前工作区开始发现文件。不要声称存储库不可用，或要求用户提供路径或文件内容，直到工作区相对发现找不到目标。除非确认了读者可用性、传输或路径规范化失败，并且验证了规范路径仍然在工作区内，否则不要使用主机原生 shell 读取器（`sed`/`cat` 或 `Get-Content`）。在内容排除、权限/策略、工作区边界或未知读取失败时停止。仅在确认了编辑器可用性、传输或路径规范化失败后，才使用 shell 编辑回退，绝不要因为陈旧上下文、并发更改、权限/策略拒绝或路径边界错误而使用它。回退之前，在工作区内解决规范路径，重新读取文件，并要求使用预期的旧文本和确切的匹配计数进行锚定替换；如果任何内容发生变化，则中止。然后重新打开文件，检查差异并验证。不要要求用户粘贴可读的发现的文件或报告建议的补丁作为已完成的工作。

### 步骤 1：验证先决条件

在修改任何代码之前：

1. **确认包装器/抽象存在**：检查接口或内置抽象是否在项目中可用。对于 `TimeProvider`，验证目标框架是 .NET 8+ 或 `Microsoft.Bcl.TimeProvider` 被引用。对于 `System.IO.Abstractions`，验证 NuGet 包被引用。一个可能提供抽象的包与该项目可用的抽象不同。

2. **确认生产组合存在**：检查 `Program.cs`、`Startup.cs` 或手动构造位置。如果缺少包、包装器或注册工作，仅在用户明确授权依赖项/组合更改时才添加它。否则，在编辑调用点之前停止并报告确切的先决条件；不要将范围迁移转换为首次抽象设计。

3. **确定范围内的所有文件**：列出将要修改的 `.cs` 文件。排除测试项目、`obj/`、`bin/` 和生成代码。

4. **编辑前锁定并计算成员集**：使用用户指定的确切成员，或从请求和发现的调用点推断出最小的无歧义集。记录该集合，然后搜索每个成员并捕获文件/行清单。在编辑期间不要更改该集合，也不要从部分读取中推断计数。

### 步骤 2：为每个文件规划迁移

**迁移用户请求的确切内容——不要修改相邻内容。** 如果用户命名了一个成员（`DateTime.UtcNow`），则仅迁移该成员，并保留兄弟成员（如 `DateTime.Now`）不变。如果用户命名了文件，则不要触摸其他文件。保留标记为故意的调用点（例如 `// 故意使用本地时间`），除非用户明确命名该位置并请求保留语义的迁移。将你故意保留的内容列在“剩余（超出范围）”下，以便用户可以在后续请求中要求它；建议是可以的，默默扩大范围是不可以的。

对于包含静态模式的每个文件，确定：

1. **哪些类包含调用点**——识别类声明
2. **该类是否已经注入了依赖项**——检查构造函数中现有的 `TimeProvider`、`IFileSystem` 等参数
3. **每个调用点的替换表达式**

#### 替换映射

| 类别 | 原始 | DI 替换 |
|------|------|--------|
| 时间 | `DateTime.Now` | `_timeProvider.GetLocalNow().LocalDateTime` |
| 时间 | `DateTime.UtcNow` | `_timeProvider.GetUtcNow().UtcDateTime` |
| 时间 | `DateTime.Today` | `_timeProvider.GetLocalNow().LocalDateTime.Date` |
| 时间 | `DateTimeOffset.Now` | `_timeProvider.GetLocalNow()` |
| 时间 | `DateTimeOffset.UtcNow` | `_timeProvider.GetUtcNow()` |
| 文件 | `File.ReadAllText(path)` | `_fileSystem.File.ReadAllText(path)` |
| 文件 | `File.WriteAllText(path, text)` | `_fileSystem.File.WriteAllText(path, text)` |
| 文件 | `File.Exists(path)` | `_fileSystem.File.Exists(path)` |
| 文件 | `Directory.Exists(path)` | `_fileSystem.Directory.Exists(path)` |
| 环境 | `Environment.GetEnvironmentVariable(name)` | `_env.GetEnvironmentVariable(name)` |
| 控制台 | `Console.WriteLine(msg)` | `_console.WriteLine(msg)` |
| 进程 | `Process.Start(info)` | `_processRunner.Start(info)` |

对每个类别中的其他成员应用相同的模式。

> **保留 `DateTimeKind`——这是最常见的无声回归。** `TimeProvider.GetUtcNow()` / `GetLocalNow()` 返回一个 `DateTimeOffset`。将它们转换回 `DateTime` **必须保留原始 `Kind`**，否则你引入了行为变化，即使代码仍然可以编译：
>
> - `DateTime.UtcNow` 有 `Kind == Utc` → 使用 `.UtcDateTime`（**不是** `.DateTime`，它会产生 `Kind == Unspecified`）。
> - `DateTime.Now` 有 `Kind == Local` → 使用 `.LocalDateTime`（**不是** `.DateTime`）。
> - 当调用点直接消耗 `DateTimeOffset`（一个已经为 `DateTimeOffset` 类型化的字段/参数/返回值）时，删除 `.UtcDateTime`/`.LocalDateTime` 后缀，并按原样分配 `DateTimeOffset`——不要通过 `DateTime` 强制转换。
>
> 匹配**目标成员的类型**：如果周围的字段/属性是 `DateTime`，保持它为 `DateTime`（通过上述正确的属性），不要将其更改为 `DateTimeOffset`，因为这是设计更改，而不是委托。

### 步骤 3：添加构造函数注入

按照类的现有模式添加新依赖项：

- **主构造函数**（C# 12+）：向主构造函数添加参数：`public class OrderProcessor(ILogger<OrderProcessor> logger, TimeProvider timeProvider)`
- **传统构造函数**：添加 `private readonly` 字段 + 构造函数参数，匹配现有的字段命名约定（`_camelCase` 或 `m_camelCase`）

#### 静态类：使用环境上下文（无构造函数注入）

一个只有静态成员的 `static` 类**不能**接收构造函数注入——添加实例构造函数或实例字段会破坏它。**不要**将其转换为非静态类只是为了注入依赖项；这将改变其设计并更改每个调用点。相反，应用一个范围的环境分隔，它默认为真实实现，并且可以无泄漏地覆盖进程全局状态。

当用户想要保持类为静态时，以下环境分隔是答案——将其作为*解决方案*直接呈现并实现它。**不要**通过提供“将其转换为非静态类”或“将 `TimeProvider` 作为方法参数传递”作为同等替代来犹豫；这些会改变类的设计或公共 API，并且不是用户要求的。优先考虑分隔，然后指出并行性权衡。

```csharp
public static class TimestampFormatter
{
  private static readonly AsyncLocal<TimeProvider?> s_clock = new();

  private static TimeProvider Clock => s_clock.Value ?? TimeProvider.System;

  public static string Now() => Clock.GetUtcNow().ToString("O");

  public static IDisposable OverrideClock(TimeProvider clock)
  {
      ArgumentNullException.ThrowIfNull(clock);
      var previous = s_clock.Value;
      s_clock.Value = clock;
      return new Scope(() => s_clock.Value = previous);
  }

  private sealed class Scope : IDisposable
  {
      private Action? _restore;

      public Scope(Action restore)
      {
          _restore = restore;
      }

      public void Dispose() => Interlocked.Exchange(ref _restore, null)?.Invoke();
  }
}
```

- 生产时读取 `TimeProvider.System`，只要没有活动的覆盖；不需要启动时的更改。
- 测试为每个异步流创建一个新的假体/提供程序，并处置返回的范围。嵌套处置恢复外部提供程序。
- `AsyncLocal<T>` 保持独立建立的测试流跨 `await` 隔离。不要在槽中存储可变的栈/列表或修改多个子流继承的假体。
- 添加针对替换、嵌套恢复和并行异步隔离的聚焦测试。仅构建检查不能证明此分隔。
- 相同的结构适用于其他静态（`IFileSystem`、自定义包装器）：将抽象值存储在 `AsyncLocal<T>` 中，默认为真实实现，并从范围中恢复以前的值。

### 步骤 4：替换调用点

机械地执行每个替换。对于每个调用点：

1. 用包装器调用替换静态调用
2. 保留周围的表达式结构和求值顺序；一个原始依赖项读取保持一个包装器读取
3. 如果尚未存在，则添加所需的 `using` 指令

编辑后，重复确切的搜索，并要求每个范围内的生产文件中零次出现。重新打开每个更改的文件，并将结果与编辑前清单进行比较。如果有一个方法被无声地遗漏，汇总计数不是证据。

还要验证范围的排他性：搜索或比较用户明确表示要保留的每个文件，并要求其原始静态调用和内容保持不变。对于单个文件迁移，即使数量很小，也要报告两个数字：`N/N` 范围内替换的调用和 `M` 命名超出范围的调用保留。

#### 添加 using 指令

| 抽象 | using 指令 |
|------|------------|
| `TimeProvider` | 无（在 `System` 命名空间中） |
| `IFileSystem` | `using System.IO.Abstractions;` |
| `IHttpClientFactory` | `using System.Net.Http;`（通常已经存在） |
| 自定义包装器 | `using <wrapper namespace>;` |

### 步骤 5：更新受影响的测试文件

如果迁移的类存在测试文件：

1. **更新构造函数调用**——向测试类实例化添加新参数
2. **使用测试双体**：
   - `TimeProvider` → `new FakeTimeProvider()` 来自 `Microsoft.Extensions.TimeProvider.Testing`
   - `IFileSystem` → `new MockFileSystem()` 来自 `System.IO.Abstractions.TestingHelpers`
   - 自定义包装器 → `new Mock<IWrapperName>()` 或手写假体

保留所有依赖于原始静态结果的可见分支。例如，迁移 `Environment.GetEnvironmentVariable(name) ?? "production"` 需要测试配置值和 `null`/缺失输入选择回退的情况。只有假体的快乐路径是不够的，无法证明机械迁移。当测试已经存在时，保留其框架和断言风格，但使替换依赖项可见：至少包含一个配置/假体值断言和一个回退或错误路径断言，其中原始静态 API 暴露了两种结果。仅仅使旧测试编译不是完整的迁移证据。

当请求明确将受影响的单元测试从真实文件或环境访问转换为假体时，证明这些测试不再触摸进程全局依赖项：编辑后搜索它们中的临时文件、真实磁盘或环境变更 API。保留请求范围之外的故意集成测试。报告确定性假体的配置和回退/错误情况，而不是只说添加了假体。

### 步骤 6：构建验证

在当前范围内的所有更改后，构建受影响的生产项目，并在存在或更改测试时运行最窄的受影响测试项目：

```bash
dotnet build <project.csproj>
dotnet test <affected-test-project.csproj>
```

**报告你实际观察到的构建结果。** 只有当命令退出 0 时才写“构建成功”；如果它失败——包括还原/NuGet 失败，如“资产文件未找到”——就说出来，引用错误，并要么修复它（`dotnet restore`，添加缺失的包），要么将精确的障碍交给用户。一个虚假的成功声明比未完成的迁移更糟。

如果构建失败：
- **缺少 using**：添加所需的 `using` 指令
- **缺少 NuGet 包**：仅在明确授权依赖项更改时添加它；否则报告未满足的先决条件并停止
- **测试中的构造函数不匹配**：更新测试实例化（步骤 5）
- **模糊调用**：完全限定包装器调用

不要用成功的构建代替请求的测试运行。当迁移更改构造函数调用、假体、进程全局状态或真实 I/O 时，只有目标测试才能证明完整路径。如果测试命令被阻塞，报告该阻塞，而不是声称迁移已完全验证。

### 步骤 7：报告更改

总结做了什么。即使对于单个生产文件和一个测试文件，也要包括确切的范围内替换计数、命名超出范围的文件或调用验证未更改，以及目标构建/测试结果：

```
## 迁移摘要

**模式**： DateTime.UtcNow → TimeProvider.GetUtcNow()
**范围**： MyProject/Services/

### 修改的文件（生产）
| 文件 | 替换的调用点 | 注入添加 |
|------|--------------------:|:----------------|
| OrderProcessor.cs | 3 | 是（构造函数） |
| NotificationService.cs | 1 | 是（主构造函数） |

### 修改的文件（测试）
| 文件 | 变更 |
|------|--------|
| OrderProcessorTests.cs | 添加了 FakeTimeProvider 参数 |

### 剩余（超出范围）
- MyProject/Legacy/ — 8 个调用点未迁移（不同的命名空间）
```

## 验证

- [ ] 范围内的所有调用点都被替换（没有遗漏）
- [ ] 通过精确成员的 before/after 搜索证明范围内出现次数达到零
- [ ] 没有修改请求的成员/文件范围之外的调用点
- [ ] 文档为故意保留的调用点保持未更改，除非用户明确命名它们以进行保留语义的迁移
- [ ] 所有受影响的类都添加了构造函数注入
- [ ] 字段命名遵循现有的类约定
- [ ] 添加了所需的 using 指令
- [ ] 引用了所需的 NuGet 包
- [ ] 迁移后构建成功，并且报告的结果与实际命令退出代码匹配
- [ ] 测试文件使用适当的测试双体更新
- [ ] 现有的配置、回退/空值和错误分支仍有直接的测试证据
- [ ] 当存在或更改测试时，受影响的目标测试运行成功
- [ ] 没有引入行为变化（包装器直接委托给静态）
- [ ] 静态读取一对一替换；没有提升、缓存或合并
- [ ] 保留 `DateTimeKind`——以前的 `DateTime.UtcNow` 保持 `Utc`（`.UtcDateTime`），以前的 `DateTime.Now` 保持 `Local`（`.LocalDateTime`）

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 在测试代码中替换静态 | 仅在生产代码中替换；测试应使用假体/模拟 |
| 破坏静态类 | 静态类不能有构造函数——使用步骤 3 中的环境分隔代替将它们转换为非静态 |
| 缺少 `FakeTimeProvider` NuGet | 将 `Microsoft.Extensions.TimeProvider.Testing` 添加到测试项目 |
| 用 `.DateTime` 替换 `DateTime` 值从 `DateTimeOffset` | `DateTimeOffset.DateTime` 返回 `Kind == Unspecified`——使用 `.UtcDateTime`（对于以前的 `DateTime.UtcNow`）或 `.LocalDateTime`（对于以前的 `DateTime.Now`）以保留原始 `DateTimeKind`。只有在用户要求它时才更改字段/返回类型为 `DateTimeOffset` |
| 为多个原始时钟读取捕获一个提供程序值 | 在原位替换每个读取。合并读取会改变可观察的时间，即使它看起来更整洁 |
| 一次性迁移太多 | 坚持定义的范围——一次一个项目或命名空间 |
| 请求迁移 `DateTime.Now` 而只请求 `UtcNow` | 尊重字面请求；将其他调用点作为超出范围的建议列出，而不是重写它们 |
| 在构建失败后声称“构建成功” | 读取退出代码和输出；报告真实失败并修复它或将其作为障碍呈现 |
| 在调用点仅迁移期间添加包 | 停止并请求授权或首先运行包装器/采用设置 |
| 遗忘生产组合 | 在替换调用点之前验证依赖项注册、手动构造或环境生产默认值 |
