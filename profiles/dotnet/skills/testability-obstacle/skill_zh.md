# 解决可测试性障碍

介绍测试特定 C# 行为所需的最小行为保留接口，然后添加确定性测试来证明该行为和接口。生产代码修改是实现所需测试的手段，而非重新设计相邻代码的邀请。

## 使用场景

- 请求的测试否则会读写真实的文件系统。
- 行为依赖于当前时间、延迟、随机值、环境、控制台、进程或其他环境依赖。
- 用户明确允许或请求安全的生产行为保留接口。
- 现有测试无法在不进行全局进程级修改的情况下控制依赖。

## 不适用场景

- 依赖项已经注入或作为参数传递。通过现有接口使用 `code-testing-agent` 编写使用假数据的测试。
- 用户需要全库可测试性审计。使用 `detect-static-dependencies`。
- 用户需要生成包装器但不想更改调用点或测试。使用 `generate-testability-wrappers`。
- 用户请求广泛的机械迁移。使用 `migrate-static-to-wrapper`，然后单独生成测试。
- 用户已经选择了现有替代方案（如 `TimeProvider` 或 `IFileSystem`）并请求将其调用点迁移到该方案。使用 `migrate-static-to-wrapper`，该方案还会更新受影响的测试。
- 代码不是 C#/.NET。

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 要测试的行为 | 是 | 方法/工作流和预期的可观察行为 |
| 目标范围 | 否 | 当省略时，发现最窄的相关文件/项目 |
| 允许的生产行为修改 | 否 | 默认为最小的内部/构造函数接口 |

## 工作流程

### 第 1 步：证明障碍

读取目标生产行为路径及其现有测试。识别阻止确定性测试的确切环境操作和必须保持不变的行为。不要为单个类请求运行全库静态扫描。

如果已经存在足够的接口，则停止重构并使用它。当可以使用假数据时，这项技能不会增加任何价值。

### 第 2 步：选择最小的安全接口

根据依赖项和库约束进行选择：

| 依赖项 | 推荐接口 |
|--------|----------|
| 当前时间/计时器 | 注入 `TimeProvider`；在测试中使用 `FakeTimeProvider` |
| 文件系统 | 现有库抽象；对于一次写/读操作，当约定允许时使用注入的委托，否则使用单成员接口或已接受的 `System.IO.Abstractions` |
| HTTP | 现有的类型化 `HttpClient`/处理器或 `IHttpClientFactory` 接口 |
| 随机性 | 一个生成的值：注入的委托，生产默认值为 `Random.Shared`；多个操作/状态：注入 `Random` 或最小生成器接口 |
| 环境/控制台/进程 | 仅包含目标使用的成员的最小接口 |

作用域 `AsyncLocal<T>` 规则适用于所有必须保留其公共静态形状的静态 API——时钟、文件系统访问、环境查找、身份生成和随机性。作用域捕获并恢复先前值；永远不要将 `Dispose()` 实现为无条件赋值给 `null`。将提供程序/值本身存储在 `AsyncLocal<T>` 中。不要在槽中放置可变的 `Stack<T>`、列表或其他共享可变集合：子执行上下文可以继承相同的对象并相互破坏嵌套。当提供程序本身是可变的（例如内存存储或假时间提供程序）时，在每个并行流内部建立一个新的提供程序，而不是从一个父上下文继承一个已继承的实例。

实例类默认使用构造函数注入。重用库的 DI 和命名约定，但不要只为满足此工作流程将 DI 容器添加到类库中。

除非用户授权 API 修改，否则保留现有的公共构造表面。将公共无参数构造函数作为真实依赖的默认值，并将测试专用委托/提供程序构造函数放在测试项目可以触及的最窄可见性。不要仅仅为了测试便利而将接口变成一个新的公共可选参数。

对于静态类或无法更改的公共 API，仅在构造函数/参数注入不可能时使用作用域环境接口。覆盖必须：

- 跨越 `await`（`AsyncLocal<T>`，而不是 `[ThreadStatic]`）；
- 返回 `IDisposable` 并恢复先前值，包括嵌套作用域；
- 默认为真实生产依赖；
- 避免进程级可变假数据，使测试无法并行。

使用内置的假时间感知重载，而不是发明 `IDelay` 包装器：

| 环境操作 | 替换 |
|--------|------|
| `Task.Delay(delay, token)` | `Task.Delay(delay, timeProvider, token)` |
| `new CancellationTokenSource(delay)` | `new CancellationTokenSource(delay, timeProvider)` |
| `PeriodicTimer(period)` | 当目标框架提供时 `new PeriodicTimer(period, timeProvider)` |

通过启动操作、证明其不完整、推进 `FakeTimeProvider`，然后等待来测试延迟行为。对于截止日期或边界，推进到截止日期之前立即并断言任务仍然不完整，然后再推进过截止日期；仅断言立即启动后并不能证明边界。永远不要等待墙上时钟时间。

对于嵌套环境覆盖，每个作用域拥有在其启动时活动的值。使用 `using`（它发出 `try/finally`）或显式 `finally` 按后进先出顺序释放作用域；释放内部作用域会恢复外部值，永远不会是无条件的 `null`。对于基于环境的静态 API，使用此形状：

```csharp
public static class FeatureFlags
{
    private static readonly AsyncLocal<Func<string, string?>?> s_environment = new();

    public static bool IsEnabled(string name)
    {
        var reader = s_environment.Value;
        var value = reader is null
            ? Environment.GetEnvironmentVariable(name)
            : reader(name);

        return string.Equals(value, "true", StringComparison.OrdinalIgnoreCase);
    }

    public static IDisposable OverrideEnvironment(Func<string, string?> reader)
    {
        ArgumentNullException.ThrowIfNull(reader);

        var previous = s_environment.Value;
        s_environment.Value = reader;
        return new RestoreScope(() => s_environment.Value = previous);
    }

    private sealed class RestoreScope : IDisposable
    {
        private Action? _restore;

        public RestoreScope(Action restore)
        {
            _restore = restore;
        }

        public void Dispose() =>
            Interlocked.Exchange(ref _restore, null)?.Invoke();
    }
}
```

异常测试必须在异常从内部 `using` 作用域逸出但在外部作用域释放之前观察到外部值：

```csharp
using var outer = FeatureFlags.OverrideEnvironment(_ => "true");
Assert.True(FeatureFlags.IsEnabled("Preview"));

Assert.Throws<InvalidOperationException>(() =>
{
    using var inner = FeatureFlags.OverrideEnvironment(_ => "false");
    Assert.False(FeatureFlags.IsEnabled("Preview"));
    throw new InvalidOperationException("test");
});

Assert.True(FeatureFlags.IsEnabled("Preview"));
```

还重叠两个异步流，每个流都建立一个新的覆盖并断言每个流只看到自己的值。仅并行测试不会捕获常见的“释放设置为 null”错误。在这些测试中不要修改进程环境变量；作用域读取器是确定性输入。选择与生产回退不同的外部值，以便清除槽不会意外通过恢复断言。

### 第 3 步：保留行为和 API 形状

保持生产行为机械：

- 仅包装目标行为使用的成员。
- 默认实现直接委托到原始 API。
- 保留异常、路径处理、时区以及 `DateTime.Kind`。
- 除非用户明确允许 API 修改，否则保留现有的公共签名。
- 不要将业务逻辑移入包装器或修复无关的生产错误。

确定性序列化文本是对保留环境平台格式的故意例外。如果用户要求跨平台精确可重复的输出，请使用格式的显式分隔符（如果没有指定，请使用字面值 `\n`）并断言字面内容。仅在平台原生输出是现有合同的一部分时保留 `Environment.NewLine`。

对于时间替换：

- `DateTime.UtcNow` -> `timeProvider.GetUtcNow().UtcDateTime`
- `DateTime.Now` -> `timeProvider.GetLocalNow().LocalDateTime`
- `DateTimeOffset.UtcNow` -> `timeProvider.GetUtcNow()`
- `DateTimeOffset.Now` -> `timeProvider.GetLocalNow()`

### 第 4 步：保持生产默认连接

更新受接口影响的每个组合根或构造函数调用。生产必须默认使用真实时间/文件系统等。如果项目使用 DI，请使用与库约定匹配的生命周期注册默认实现。如果不使用 DI，请显式组合；不要引入容器。
现有的手动工厂必须显式传递真实依赖项（例如，`new ExpirationPolicy(TimeProvider.System)`）。不要将责任移入可选构造函数或向工厂添加可选提供程序参数。

在编写测试之前构建受影响的生产行为项目。此处编译失败是接口问题，不是测试问题。

### 第 5 步：编写确定性测试

使用库的现有测试项目。如果不存在，请先调用 `scaffold-dotnet-test-project`。

测试必须提供受控依赖项：

- 固定/推进时间而不是墙上时钟等待；
- 内存假文件系统或手写的假数据而不是临时/真实文件；
- 无环境修改、外部进程、控制台输入或网络。

在编写测试之前，检查测试项目并遵循现有的框架、全局使用和断言约定。使用该项目已经引用的框架包；永远不要添加手写的 `FactAttribute`、替代测试框架类型或不相关的测试项目管道以使测试编译。

断言请求的业务结果以及至少一个交互/状态可观察项，以证明假依赖项驱动了路径。仅在它可以保持确定性时才包含生产默认测试；永远不要触摸真实文件系统仅仅为了证明适配器委托。

选择支持行为的最窄接口。单个 `File.WriteAllText` 调用可以是具有真实默认值的注入的 `Action<string, string>`；除非库约定或多个操作证明它们，否则不要创建接口、实现、朋友程序集设置和额外的项目连接。

保留公共 API 表面以及现有的签名。不要仅为了测试而添加公共依赖注入构造函数。当类目前只有其隐式公共无参数构造函数且测试程序集已知时，保留该构造函数行为并将测试专用构造函数设置为内部；在这种情况下，`InternalsVisibleTo` 条目是合理的，因为它可以防止接口变成公共 API。当存在时，优先考虑现有的库朋友程序集约定。

当现有公共接口已经接受假数据或测试项目可以否则提供它时，不要添加 `InternalsVisibleTo`。朋友程序集访问仅在以下情况下合理：选择的最小构造函数/委托接口必须保持内部以保留公共 API，且测试程序集已知。

### 第 6 步：验证完整路径

运行受影响的生产行为构建、目标测试项目和库级测试命令。重新阅读差异并确认：

1. 每个生产行为修改都是由接口必需的；
2. 新测试没有使用任何真实的环境资源；
3. 当前时间语义和公共行为得到保留；
4. 现有测试没有被替换或重复。

检查测试摘要，而不仅仅是退出代码。零发现的测试、没有运行请求测试的构建或任何失败的/错误的测试都意味着任务未完成。修复发现/执行并重新运行，然后再报告成功。
当新测试无法编译时，在更改生产行为之前，根据现有测试框架修正其导入、断言重载或异步测试形状；不要在源代码中模拟缺失的框架 API。
对于静态环境接口，完成需要替换执行的测试、嵌套恢复和重叠异步流隔离的测试；仅生产编译不足以证明。在交接中捕获通过测试的数量或请求的测试名称。如果没有发现测试或输出未证明执行，请修正项目/测试源并重新运行，而不是报告接口已验证。

## 输出契约

提供紧凑的 `需求 | 证据` 表格。引用生产行为接口、生产行为默认连接、确切的测试名称和通过命令。如果包恢复或构建阻止验证，请报告该阻塞器，而不是声称测试通过。

## 验证

- [ ] 原始障碍是具体的且在请求的路径上。
- [ ] 当可用时重用了现有接口。
- [ ] 新的抽象仅暴露目标行为所需的成员。
- [ ] 生产默认仍然委托到原始依赖项。
- [ ] 接口在内部测试接口足够时没有扩大公共 API。
- [ ] 时间转换保留本地/UTC 和 `DateTime.Kind` 语义。
- [ ] 静态环境覆盖是异步安全的、作用域的、嵌套的和可逆的。
- [ ] 新测试使用固定/内存依赖项，没有真实 I/O 或墙上时钟。
- [ ] 生产构建和目标/库测试至少发现一个请求的测试通过。

## 常见陷阱

| 陷阱 | 更正措施 |
|------|--------|
| 在证明障碍之前重构 | 重用现有接口并直接编写测试 |
| 包装整个静态 API | 仅暴露目标调用的成员 |
| 使用 `.DateTime` 转换 `UtcNow` | 使用 `.UtcDateTime` 以保留 `DateTimeKind.Utc` |
| 可变静态假数据由测试共享 | 使用构造函数注入或作用域 `AsyncLocal<T>` 覆盖 |
| 向没有容器的库添加 DI | 显式组合依赖项 |
| 使用临时文件作为捷径 | 提供内存假数据；该场景不需要真实 I/O |
| 在重构构建后停止 | 编写并运行证明接口的业务测试 |
| 将零测试运行报告为成功 | 修复发现并要求请求的测试执行并通过 |
