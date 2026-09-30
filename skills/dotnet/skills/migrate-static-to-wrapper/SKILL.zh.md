---
name: migrate-static-to-wrapper
description: 在要求迁移、替换或使现有 C# 静态调用可测试时，始终使用命名的包装器或内置抽象：使用 DateTime.UtcNow/Now 或 DateTimeOffset.UtcNow 替换 TimeProvider/IClock，使用 File.* 替换 IFileSystem 或现有存储（如 ITextFileStore），以及使用 Environment.* 替换现有读取器（如 IEnvironmentReader）。涵盖作用域文件/项目、构造函数注入、用假体替换临时文件或进程环境测试、"已注册"的抽象，以及调用者/签名必须保持不变的静态类。保留 DateTimeKind 和调用次数。不应用于查找静态（检测静态依赖）、选择/设计新包装器（生成可测试包装器）、无选定接口的行为测试（可测试障碍），或测试框架迁移。
---

# 将静态迁移到包装器

执行机械式、codemod 风格的替换，将静态依赖调用点替换为对注入的包装器接口或内置抽象的调用。它在有限范围内操作（单个文件、项目或命名空间），因此迁移可以增量进行。

## 何时使用

- 生成包装器（通过 `generate-testability-wrappers`）或识别内置抽象之后
- 在整个项目中迁移 `DateTime.UtcNow` → `TimeProvider.GetUtcNow()` 
- 在命名空间中迁移 `File.*` → `IFileSystem.File.*`
- 为受影响类添加新的抽象的构造函数注入
- 通过添加环境接口（步骤 3）使 `static` 工具类可测试，同时其现有的调用点保持编译不变
- 增量迁移：一次一个项目或命名空间
- 当请求的迁移命名了替换抽象时，使用假体更新受影响的测试

## 何时不使用

- 尚未存在包装器或抽象，必须从头设计（首先使用 `generate-testability-wrappers`）。
  例如 `TimeProvider` 或 `IFileSystem` 等内置抽象始终视为已存在。
- 用户想要检测静态，而不是迁移它们（使用 `detect-static-dependencies`）
- 在测试框架之间迁移（使用适当的迁移技能）
- 用户主要要求确定性行为测试，并且尚未选择生产接口（使用 `testability-obstacle`）

> 一个 `static` 类或没有依赖注入容器的项目**不是**跳过此技能的理由——这正是步骤 3 中的环境接口的目的。每当调用点必须保持编译不变时，请使用它。

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 静态模式 | 否 | 从请求和发现的调用点推断（例如，`DateTime.UtcNow`、`File.ReadAllText`） |
| 替换抽象 | 否 | 从请求和现有项目抽象推断；当没有命名/现有抽象可用时停止 |
| 范围 | 否 | 从请求的文件/项目/命名空间推断，否则发现最窄的相关工作区范围 |
| 注入策略 | 否 | `constructor`（默认）、`primary-constructor` 或 `ambient` |

## 工作流程

### 不可协商的迁移边界

- **缺少抽象意味着停止。** 如果命名的接口/包不存在，并且请求仅授权调用点替换，则不要添加包、发明本地类似接口或编辑生产代码。报告确切的缺失先决条件以及继续所需的授权。
- **一个源读取保持一个替换读取。** 不要提升或合并调用，即使共享捕获的时间戳看起来更整洁。
- **请求的范围是详尽且排他的。** 替换范围内的每个命名调用，并且不替换相邻的成员或文件。
- **基于存储库的请求需要存储库工作。** 从当前工作区开始发现文件。不要声称存储库不可用或要求用户提供路径或文件内容，直到工作区相对发现未找到目标。除非确认编辑器可用性、传输或路径规范化失败，否则不要说工作已实施，除非差异证明。使用主机原生 shell 读取器（`sed`/`cat` 或 `Get-Content`）仅在使用确认的读取器可用性、传输或路径规范化失败之后，并且仅在验证规范路径仍然位于当前工作区内部之后。在内容排除、权限/策略、工作区边界或未知读取失败时停止。仅在确认编辑器可用性、传输或路径规范化失败时使用 shell 编辑回退，绝不要用于陈旧上下文、并发更改、权限/策略拒绝或路径边界错误。回退之前，在工作区内部解决规范路径，重新读取文件，并要求使用预期的旧文本和确切的匹配计数进行锚定替换；如果任何内容更改，则中止。然后重新打开文件，检查差异并验证。不要要求用户粘贴可读的发现的文件或报告建议的补丁作为已完成的工作。

### 步骤 1：验证先决条件

在修改任何代码之前：

1. **确认包装器/抽象存在**：检查接口或内置抽象是否在项目中可用。对于 `TimeProvider`，验证目标框架为 .NET 8+ 或 `Microsoft.Bcl.TimeProvider` 被引用。对于 `System.IO.Abstractions`，验证 NuGet 包被引用。能够提供抽象的包与该项目可用的抽象不同。

2. **确认生产组合存在**：检查 `Program.cs`、`Startup.cs` 或手动构造位置。如果缺少包、包装器或注册工作，仅在用户明确授权依赖项/组合更改时才添加它。否则，在编辑调用点之前停止并报告确切的先决条件；不要将范围迁移转换为首次抽象设计。

3. **确定范围内的所有文件**：列出将要修改的 `.cs` 文件。排除测试项目、`obj/`、`bin/` 和生成代码。

4. **编辑前锁定并计算成员集**：使用用户指定的确切成员，或从请求和发现的调用点推断最小的不模糊集。记录该集合，然后搜索每个成员并捕获文件/行清单。编辑期间不要更改该集合，也不要从部分读取中推断计数。

### 步骤 2：为每个文件规划迁移

**精确迁移请求的内容——不要相邻。** 如果用户命名了成员（`DateTime.UtcNow`），则仅迁移该成员并保留兄弟成员（如 `DateTime.Now`）不变。如果用户命名了文件，不要触摸其他文件。保留标记为故意的调用点（例如 `// 故意使用本地时间`），除非用户明确命名该位置并请求保留语义的迁移。在“剩余（超出范围）”下列出所有故意保留的内容，以便用户可以在后续请求中获取；建议是可以的，无声扩大范围是不可以的。

对于包含静态模式的每个文件，确定：

1. **哪些类包含调用点**——识别类声明
2. **类是否已经注入了依赖项**——检查构造函数中现有的 `TimeProvider`、`IFileSystem` 等参数
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

> **保留 `DateTimeKind`——这是最常见的无声回归。** `TimeProvider.GetUtcNow()` / `GetLocalNow()` 返回 `DateTimeOffset`。转换回 `DateTime` **必须保持原始 `Kind`**，否则您会引入行为变化，即使代码仍然可以编译：
>
> - `DateTime.UtcNow` 有 `Kind == Utc` → 使用 `.UtcDateTime`（**不是** `.DateTime`，它会产生 `Kind == Unspecified`）。
> - `DateTime.Now` 有 `Kind == Local` → 使用 `.LocalDateTime`（**不是** `.DateTime`）。
> - 当调用点直接消耗 `DateTimeOffset`（一个已经为 `DateTimeOffset` 类型化的字段/参数/返回值）时，删除 `.UtcDateTime`/`.LocalDateTime` 后缀，并按原样分配 `DateTimeOffset`——不要强制它通过 `DateTime`。
>
> 匹配**目标成员的类型**：如果周围的字段/属性是 `DateTime`，则保持 `DateTime`（通过上述正确的 `Kind` 属性），不要将其更改为 `DateTimeOffset` 作为“机械”迁移的一部分——这是一个设计更改，而不是委托。
>
> 保留**读取的数量、顺序和位置**以及值类型。
> 将每个原始时钟读取就地替换为一个提供者读取。不要提升、缓存或合并两个读取为一个共享的 `now` 本地，即使它们在同一对象初始化器或方法中。两个连续的 `DateTime.UtcNow` 调用可能会观察到不同的瞬间；使 `CreatedAt` 和 `ExpiresAt` 从一个捕获的值派生是行为变化，而不是机械迁移。只有在原始代码已经捕获并重用了一个值时，才重用该值。

### 步骤 3：添加构造函数注入

按照类的现有模式添加新的依赖项：

- **主要构造函数**（C# 12+）：将参数添加到主要构造函数：`public class OrderProcessor(ILogger<OrderProcessor> logger, TimeProvider timeProvider)`
- **传统构造函数**：添加 `private readonly` 字段 + 构造函数参数，匹配现有的字段命名约定（`_camelCase` 或 `m_camelCase`）

#### 静态类：使用环境上下文（无构造函数注入）

仅包含静态成员的 `static` 类**不能**接收构造函数注入——添加实例构造函数或实例字段会破坏它。**不要**将其转换为非静态类只是为了注入依赖项；这会改变其设计并使每个调用点发生变化。相反，应用范围环境接口，它默认为真实实现，并且可以覆盖而不会泄露进程全局状态。

当用户想要保持类为静态时，以下环境接口是**答案**——将其作为*解决方案*直接呈现并实现它。**不要**通过提供“将其转换为非静态类”或“将 `TimeProvider` 作为方法参数传递”作为同等替代来犹豫；这些会改变类的设计或公共 API，并且不是所请求的。优先考虑接口，然后注意并行性权衡。

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

- 生产读取 `TimeProvider.System`，只要没有活动的覆盖；不需要启动突变。
- 测试为每个异步流创建一个新的假体/提供者，并处置返回的范围。嵌套处置恢复外部提供者。
- `AsyncLocal<T>` 在 `await` 期间保持独立建立的测试流隔离。不要在插槽中存储可变的堆栈/列表或修改多个子流继承的假体。
- 添加针对替换、嵌套恢复和并行异步隔离的聚焦测试。仅构建检查不能证明此接口。
- 相同的形状适用于其他静态（`IFileSystem`、自定义包装器）：将抽象值存储在 `AsyncLocal<T>` 中，默认为真实实现，并从范围恢复以前的值。

### 步骤 4：替换调用点

机械执行每个替换。对于每个调用点：

1. 用包装器调用替换静态调用
2. 保留周围的表达式结构和求值顺序；一个原始依赖项读取保持一个包装器读取
3. 如果尚未存在，则添加所需的 `using` 指令

编辑后，重复确切的搜索并要求范围内每个生产文件中零次出现。重新打开每个更改的文件，并将结果与编辑前清单进行比较。摘要计数不是证据，如果有一个方法被无声遗漏。

还要验证范围的排他性：搜索或比较用户明确说过的要保留的每个文件，并要求其原始静态调用和内容保持不变。对于单个文件迁移，即使数量很小，也要报告两个数字：`N/N` 范围内替换的调用和 `M` 保留的命名超出范围的调用。

#### 添加 using 指令

| 抽象 | using 指令 |
|------|------------|
| `TimeProvider` | 无（在 `System` 命名空间中） |
| `IFileSystem` | `using System.IO.Abstractions;` |
| `IHttpClientFactory` | `using System.Net.Http;`（通常已经存在） |
| 自定义包装器 | `using <wrapper 命名空间>;` |

### 步骤 5：更新受影响的测试文件

如果迁移的类存在测试文件：

1. **更新构造函数调用**——将新参数添加到测试类实例化
2. **使用测试双体**：
   - `TimeProvider` → `new FakeTimeProvider()` 从 `Microsoft.Extensions.TimeProvider.Testing`
   - `IFileSystem` → `new MockFileSystem()` 从 `System.IO.Abstractions.TestingHelpers`
   - 自定义包装器 → `new Mock<IWrapperName>()` 或手写假体

保留所有依赖于原始静态结果的可见分支。例如，迁移 `Environment.GetEnvironmentVariable(name) ?? "production"` 需要测试配置值和 `null`/缺失输入选择回退的情况。仅使用假体的快乐路径不足以证明机械迁移。当测试已经存在时，保留其框架和断言样式，但使替换依赖项可见：至少包含一个配置/假体值断言和一个回退或错误路径断言，其中原始静态 API 暴露了两种结果。仅仅使旧测试编译是不完整的迁移证据。

当请求明确将受影响的单元测试从真实文件或环境访问转换为假体时，证明这些测试不再触摸进程全局依赖项：编辑后搜索它们以查找临时文件、真实磁盘或环境突变 API。保留请求范围之外的故意集成测试。报告确定性假体的配置和回退/错误情况，而不是仅仅说添加了假体。

### 步骤 6：构建验证

在当前范围内的所有更改后，构建受影响的生产项目，并在存在或更改测试时运行最窄的受影响测试项目：

```bash
dotnet build <project.csproj>
dotnet test <affected-test-project.csproj>
```

**报告您实际观察到的构建结果。** 只有当命令退出 0 时才写“构建成功”；如果它失败——包括还原/NuGet 失败，如“资产文件未找到”——请这样说，引用错误，并要么修复它（`dotnet restore`，添加缺失的包），要么向用户提供一个精确的障碍。错误的成功声明比未完成的迁移更糟。

如果构建失败：
- **缺少 using**：添加所需的 `using` 指令
- **缺少 NuGet 包**：仅在明确授权依赖项更改时添加它；否则报告未满足的先决条件并停止
- **测试中的构造函数不匹配**：更新测试实例化（步骤 5）
- **模糊调用**：完全限定包装器调用

不要用成功的构建结果来代替请求的测试运行。当迁移更改构造函数调用、模拟对象、进程全局状态或真实I/O时，只有目标测试能证明完整路径。如果测试命令被阻塞，应报告那个阻塞点，而不是声称迁移已完全验证。

### 第7步：报告变更

总结已完成的操作。即使只有一个生产文件和一个测试文件，也要包含精确的范围内替换计数、已验证未变更的命名范围外文件或调用，以及目标构建/测试结果：

```
## 迁移摘要

**模式**: DateTime.UtcNow → TimeProvider.GetUtcNow()
**范围**: MyProject/Services/

### 修改的生产文件
| 文件 | 替换的调用点 | 添加的注入 |
|------|--------------------:|:----------------|
| OrderProcessor.cs | 3 | 是（构造函数） |
| NotificationService.cs | 1 | 是（主构造函数） |

### 修改的测试文件
| 文件 | 变更 |
|------|--------|
| OrderProcessorTests.cs | 添加了 FakeTimeProvider 参数 |

### 剩余（范围外）
- MyProject/Legacy/ — 8个调用点未迁移（不同命名空间）
```

## 验证

- [ ] 范围内的所有调用点都已替换（无一遗漏）
- [ ] 通过前后精确成员搜索证明范围内的出现计数已达到零
- [ ] 范围外的请求成员/文件外的调用点未被修改
- [ ] 文档中标记为故意的调用点保持未变并报告，除非用户明确要求保留语义的迁移
- [ ] 所有受影响的类都添加了构造函数注入
- [ ] 字段命名遵循现有的类规范
- [ ] 添加了必要的 `using` 指令
- [ ] 引用了必要的 NuGet 包
- [ ] 迁移后构建成功，报告结果与实际命令退出码匹配
- [ ] 测试文件更新了适当的测试替身
- [ ] 现有的配置、回退/空值和错误分支仍有直接测试证据
- [ ] 当存在或更改测试时，受影响的测试运行成功
- [ ] 未引入行为变更（包装委托直接指向静态）
- [ ] 静态读取一对一替换；无一被提升、缓存或合并
- [ ] `DateTimeKind` 保持不变 — 以前的 `DateTime.UtcNow` 保持 `Utc`（`.UtcDateTime`），以前的 `DateTime.Now` 保持 `Local`（`.LocalDateTime`）

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 测试代码中的静态替换 | 仅在生产代码中替换；测试应使用模拟对象/模拟 |
| 破坏静态类 | 静态类不能有构造函数 — 使用环境上下文接缝（第3步）代替将它们转换为非静态 |
| 缺少 `FakeTimeProvider` NuGet | 在测试项目中添加 `Microsoft.Extensions.TimeProvider.Testing` |
| 用 `.DateTime` 替换 `DateTime` 值，该值来自 `DateTimeOffset` | `DateTimeOffset.DateTime` 返回 `Kind == Unspecified` — 使用 `.UtcDateTime`（以前的 `DateTime.UtcNow`）或 `.LocalDateTime`（以前的 `DateTime.Now`）以保留原始 `DateTimeKind`。只有在用户要求时才将字段/返回类型更改为 `DateTimeOffset`。 |
| 对多个原始时钟读取捕获一个提供者值 | 原地替换每个读取。合并读取即使看起来更简洁也会改变可观察的时序。 |
| 一次性迁移过多 | 遵循定义的范围 — 每次运行一个项目或命名空间 |
| 当只请求 `UtcNow` 而迁移 `DateTime.Now` 时 | 尊重字面请求；将其他调用点列为范围外建议而不是重写它们 |
| 在失败恢复后声称“构建成功” | 读取退出码和输出；报告真实失败并修复它或将其作为阻塞点暴露 |
| 在仅调用点迁移期间添加包 | 停止并请求授权或先运行包装器/采用设置 |
| 遗忘生产组合 | 在替换调用点前验证DI注册、手动构造或环境生产默认值 |
