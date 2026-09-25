# Thread.Abort 迁移

这项技能帮助代理将使用 `Thread.Abort` 的 .NET Framework 代码迁移到现代 .NET（6+）所需的协作取消模型。在现代 .NET 中，`Thread.Abort` 会抛出 `PlatformNotSupportedException` —— 没有强制终止托管线程的方法。该技能首先识别使用模式，然后应用正确的替换策略。

## 使用场景

- 将调用 `Thread.Abort` 的 .NET Framework 项目迁移到 .NET 6+
- 替换使用控制流或清理逻辑的 `ThreadAbortException` 捕获块
- 移除用于取消挂起中止的 `Thread.ResetAbort` 调用
- 用 `Thread.Interrupt` 替换唤醒阻塞线程
- 迁移使用 `Response.End` 或 `Response.Redirect(url, true)` 的 ASP.NET 代码（后者内部调用 `Thread.Abort`）
- 在目标框架更改后解决 `PlatformNotSupportedException` 或 `SYSLIB0006` 警告

## 不适用场景

- **代码仅使用 `Thread.Join`、`Thread.Sleep` 或 `Thread.Start`，没有任何中止、中断或 `ThreadAbortException` 捕获块。** 这些 API 在现代 .NET 中工作方式完全相同 —— 无需迁移。到此为止，并告知用户无需迁移。如果您建议现代化（例如，`Task.Run`、`Parallel.ForEach`），您**必须**明确说明这些是可选的改进，与 Thread.Abort 迁移无关，现有代码在目标框架上可以正确编译和运行。
- 项目将永久停留在 .NET Framework 上
- `Thread.Abort` 的使用位于您无法控制的第三方库中

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 源项目或解决方案 | 是 | 包含 `Thread.Abort` 使用的 .NET Framework 项目 |
| 目标框架 | 是 | 要迁移到的现代 .NET 版本（例如，`net8.0`） |
| `Thread.Abort` 使用位置 | 推荐使用 | 引用 `Thread.Abort`、`ThreadAbortException`、`Thread.ResetAbort` 或 `Thread.Interrupt` 的文件或类 |

## 工作流程

> **提交策略：** 每次模式替换后提交，以便迁移可审查和可追溯。将相关的调用位置（例如，所有可取消的工作循环）分组到一个提交中。

### 第 1 步：列出所有线程终止使用情况

在代码库中搜索所有与线程终止相关的 API：

- `Thread.Abort` 和 `thread.Abort()`（实例调用）
- 捕获块中的 `ThreadAbortException`
- `Thread.ResetAbort`
- `Thread.Interrupt`
- `Response.End()`（在 ASP.NET Framework 中内部调用 `Thread.Abort`）
- `Response.Redirect(url, true)`（`true` 参数触发 `Thread.Abort`）
- `SYSLIB0006` 指令抑制

记录每个使用位置，并对中止背后的意图进行分类。

### 第 2 步：对每个使用模式进行分类

将每个使用情况分类到以下模式之一：

| 模式 | 描述 | 现代替换 |
|-------|-------------|--------------------|
| **可取消的工作循环** | 运行循环的线程应在需要时停止 | 在循环中检查 `CancellationToken` |
| **超时强制执行** | 终止超出时间限制的线程 | `CancellationTokenSource.CancelAfter` 或带有延迟的 `Task.WhenAny` |
| **阻塞调用中断** | 阻塞在 `Sleep`、`WaitOne` 或 `Join` 上的线程需要唤醒 | 使用 `WaitHandle.WaitAny` 和 `CancellationToken.WaitHandle`，或异步替代方案 |
| **ASP.NET 请求终止** | `Response.End` 或 `Response.Redirect(url, true)` | 从动作方法返回；使用 `HttpContext.RequestAborted` |
| **`ThreadAbortException` 作为控制流** | 捕获块检查 `ThreadAbortException` 以决定清理操作 | 用 `OperationCanceledException` 替换，并显式进行清理 |
| **使用 `Thread.ResetAbort` 继续执行** | 捕获中止并调用 `ResetAbort` 以保持线程存活 | 检查 `CancellationToken.IsCancellationRequested` 并决定是否继续 |
| **不合作的代码终止** | 终止运行无法修改以检查取消的代码的线程 | 将工作移到单独的进程中，并使用 `Process.Kill` |

**关键：** 基本范式转变是从抢占式取消（运行时强制注入异常）到协作取消（代码必须自愿检查并响应取消请求）。必须评估每个调用位置，以确定目标代码是否可以修改以进行协作。

### 第 3 步：为每个模式应用替换

- **可取消的工作循环**：添加 `CancellationToken` 参数。替换循环条件或在安全检查点添加 `token.ThrowIfCancellationRequested()`。调用者创建 `CancellationTokenSource` 并调用 `Cancel()` 而不是 `Thread.Abort()`。
- **超时强制执行**：使用 `new CancellationTokenSource(TimeSpan.FromSeconds(n))` 或 `cts.CancelAfter(timeout)`。将令牌传递给工作。对于基于任务的代码，使用 `Task.WhenAny(workTask, Task.Delay(timeout, cts.Token))` 并在延迟获胜时取消源；取消也会释放延迟的内部计时器。
- **阻塞调用中断**：将 `Thread.Sleep(ms)` 替换为 `Task.Delay(ms, token)` 或 `token.WaitHandle.WaitOne(ms)`。将 `ManualResetEvent.WaitOne()` 替换为 `WaitHandle.WaitAny(new[] { event, token.WaitHandle })`。
- **ASP.NET 请求终止**：完全移除 `Response.End()` —— 直接从方法返回。将 `Response.Redirect(url, true)` 替换为不带 `endResponse` 参数的 `Response.Redirect(url)` 或返回重定向结果。在 ASP.NET Core 中，使用 `HttpContext.RequestAborted` 作为长时间运行请求工作的取消令牌。
- **`ThreadAbortException` 作为控制流**：将 `catch (ThreadAbortException)` 替换为 `catch (OperationCanceledException)`。将清理逻辑移到 `finally` 块或 `CancellationToken.Register` 回调中。不要捕获 `OperationCanceledException` 并忽略它 —— 让它传播，除非您有特定的恢复操作。
- **使用 `Thread.ResetAbort` 继续执行**：将“可中止”的工作单元拆分，以便在处理循环中的取消可以继续到下一个单元，而不是依赖 `ResetAbort` 来防止线程被拆除。在每次单元后检查 `token.IsCancellationRequested` 并决定是否继续。为每个新的工作单元创建一个新的 `CancellationTokenSource`（可选地链接到父令牌），而不是尝试重置现有的令牌。
- **不合作的代码终止**：如果代码无法接受 `CancellationToken`（例如，第三方库、本地调用），将工作移到子进程。主机进程通过 stdin/stdout 或 IPC 通信，并在超时过期时调用 `Process.Kill`。

### 第 4 步：清理已移除的 API

迁移所有模式后，移除或替换任何剩余的引用：

| 已移除 API | 替换 |
|-------------|-------------|
| `Thread.Abort()` | `CancellationTokenSource.Cancel()` |
| `ThreadAbortException` 捕获块 | `OperationCanceledException` 捕获块 |
| `Thread.ResetAbort()` | 检查 `token.IsCancellationRequested` 并决定是否继续 |
| `Thread.Interrupt()` | 通过 `CancellationToken` 信号或设置 `ManualResetEventSlim`（也过时：.NET 9 中的 `SYSLIB0046`） |
| `Response.End()` | 移除调用；从方法返回 |
| `Response.Redirect(url, true)` | 不带 `endResponse` 的 `Response.Redirect(url)`，或返回重定向结果 |
| `#pragma warning disable SYSLIB0006` | 替换 Thread.Abort 调用后移除 |

### 第 5 步：验证迁移

1. 针对新框架构建项目。确认没有 `SYSLIB0006` 警告和与 `Thread.Abort` 相关的编译错误。
2. 在代码库中搜索任何剩余的 `Thread.Abort`、`ThreadAbortException`、`Thread.ResetAbort` 或 `Thread.Interrupt` 引用。
3. 运行现有测试。如果测试依赖于 `Thread.Abort` 进行清理或超时，请更新它们以使用 `CancellationToken`。
4. 对于超时场景，验证在取消请求后工作是否在合理时间内停止。
5. 对于阻塞调用场景，验证在取消令牌时阻塞线程是否及时唤醒。

## 验证

- [ ] 迁移后的代码中没有 `Thread.Abort` 的引用
- [ ] 没有 `ThreadAbortException` 捕获块剩余
- [ ] 没有 `Thread.ResetAbort` 调用剩余
- [ ] 没有 `SYSLIB0006` 指令抑制剩余
- [ ] 项目可以干净地针对目标框架，没有与线程中止相关的警告
- [ ] 所有可取消的工作都接受 `CancellationToken` 参数
- [ ] 超时场景使用 `CancellationTokenSource.CancelAfter` 或等效方案
- [ ] 阻塞调用使用 `WaitHandle.WaitAny` 和 `token.WaitHandle` 或异步替代方案
- [ ] 现有测试通过或已更新为协作取消

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 添加 `CancellationToken` 参数但在长时间运行的代码中从未检查它 | 在循环中的定期检查点或昂贵操作之间插入 `token.ThrowIfCancellationRequested()`。只有在代码合作时，取消才会生效。 |
| 未将令牌传递通过整个调用链 | 链中的每个异步或长时间运行的方法都必须接受并转发 `CancellationToken`。如果链中的某个方法忽略它，取消将在该点停滞。 |
| 期望 `CancellationToken` 中断像 `Thread.Sleep` 或 `socket.Receive` 这样的阻塞同步调用 | 这些调用不会检查令牌。将 `Thread.Sleep(ms)` 替换为 `token.WaitHandle.WaitOne(ms)`。将同步 I/O 替换为接受 `CancellationToken` 的异步重载。 |
| 捕获 `OperationCanceledException` 并忽略它 | 让 `OperationCanceledException` 向调用者传播。仅在顶层编排点捕获它，在那里您决定取消后的操作（记录、清理、返回结果）。 |
| 未释放 `CancellationTokenSource` | `CancellationTokenSource` 是 `IDisposable`。将其包装在 `using` 语句中或在 `finally` 块中释放它。泄漏它会导致计时器和回调泄漏。 |
| 假设取消是立即的 | 协作取消仅在下一个检查点生效。如果工作项很大或代码在检查点之间有长间隙，取消可能会延迟。根据可接受的延迟设计检查点频率。 |
| 使用 `Thread.Interrupt` 作为 `Thread.Abort` 的替代品 | `Thread.Interrupt` 在现代 .NET 中也不推荐。它仅在 `WaitSleepJoin` 状态的线程上工作，并抛出 `ThreadInterruptedException`，这是一个不同的异常类型。用 `CancellationToken` 信号替换。 |
| 未迁移清理逻辑就移除 `ThreadAbortException` 捕获块 | `ThreadAbortException` 捕获块通常包含关键清理（释放锁、回滚事务）。在移除捕获之前，将此逻辑移到 `finally` 块或 `CancellationToken.Register` 回调中。 |

## 更多信息

- [Thread.Abort 在 .NET 6+ 中的 breaking change](https://learn.microsoft.com/dotnet/core/compatibility/core-libraries/6.0/thread-abort) — 为什么 `Thread.Abort` 抛出 `PlatformNotSupportedException`
- [托管线程中的取消](https://learn.microsoft.com/dotnet/standard/threading/cancellation-in-managed-threads) — 使用 `CancellationToken` 的协作取消模型
- [CancellationTokenSource 类](https://learn.microsoft.com/dotnet/api/system.threading.cancellationtokensource) — 创建和管理取消令牌的 API 参考
- [SYSLIB0006 警告](https://learn.microsoft.com/dotnet/fundamentals/syslib-diagnostics/syslib0006) — `Thread.Abort` 已过时
- [SYSLIB0046 警告](https://learn.microsoft.com/dotnet/fundamentals/syslib-diagnostics/syslib0046) — `Thread.Interrupt` 已过时（.NET 9 中添加）
- [`Task.WaitAsync(CancellationToken)`](https://learn.microsoft.com/dotnet/api/system.threading.tasks.task.waitasync) — 基于任务的代码的可取消等待 (.NET 6+)
