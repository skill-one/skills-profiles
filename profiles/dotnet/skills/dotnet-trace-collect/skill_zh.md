# .NET 跟踪收集

这项技能通过为开发者推荐适合其环境的诊断工具、指导数据收集以及建议分析方法，帮助开发者诊断生产环境中的性能问题。它不会分析代码中的反模式或执行分析本身。

## 使用场景

- 开发者需要调查生产环境中的性能问题（如高 CPU、内存泄漏、请求缓慢、过度 GC、网络错误等）
- 为特定的运行时、操作系统或部署拓扑选择合适的诊断工具
- 设置和运行诊断工具命令以收集数据
- 了解可用工具之间的权衡（例如 PerfView 与 dotnet-trace）
- 从容器化或 Kubernetes 工作负载中收集诊断信息

## 不适用场景

- 审查源代码以查找性能反模式（应使用代码审查技能）
- 开发过程中的基准测试（例如 BenchmarkDotNet 设置）
- 分析收集的跟踪或转储文件（这项技能推荐用于分析的工具，但不执行分析）

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------------|
| 症状 | 是 | 开发者观察到的现象（高 CPU、内存增长、请求缓慢、挂起、过度 GC、HTTP 5xx 错误、网络超时、连接失败、程序集加载失败等） |
| 运行时 | 是 | .NET Framework 或现代 .NET（以及版本，特别是是否为 .NET 10+） |
| 操作系统 | 是 | Windows 或 Linux |
| 部署 | 是 | 非容器、容器或 Kubernetes |
| 管理员权限 | 推荐使用 | 开发者是否在目标机器上具有管理员/root 访问权限 |
| 复现特征 | 推荐使用 | 问题是否容易复现或需要很长时间才能显现 |

## 工作流程

### 第一步：理解环境

确定或询问开发者澄清以下内容：

1. **症状**：他们观察到的现象（高 CPU、内存泄漏、请求缓慢、挂起、过度 GC、HTTP 5xx 错误、网络超时、连接失败、程序集加载失败等）
2. **运行时**：.NET Framework 还是现代 .NET？如果是现代 .NET，哪个版本？（特别是是否为 .NET 10 或更高版本。）
3. **操作系统**：Windows 还是 Linux？
4. **部署**：直接在主机上运行、在容器中运行还是在 Kubernetes 中运行？
5. **管理员权限**：他们是否在目标机器或容器上具有管理员/root 访问权限？
6. **复现特征**：问题是否快速复现，还是需要很长时间才能显现？
7. **工作负载上下文**：确定或询问用户是否在工作负载上下文中运行（即，在发生问题的同一台机器或环境中）。如果是，可以直接代表他们运行诊断命令。如果不是，请提供命令作为指导，让用户自行运行。

使用这些信息在第二步中选择合适的工具。

### 第二步：推荐诊断工具

根据以下优先级规则，根据环境选择工具。一旦选择了一个工具，加载相应的参考文件以获取详细的命令行用法。

#### 工具参考查找

| 环境 | 参考文件 |
|-------------|-------------------|
| Windows + 现代 .NET + 管理 | `references/perfview.md` |
| Windows + 现代 .NET，无管理 | `references/dotnet-trace-collect.md` |
| Windows + .NET Framework | `references/perfview.md` |
| Linux + .NET 10+ + root | `references/dotnet-trace-collect-linux.md` |
| Linux + .NET 10 之前 | `references/dotnet-trace-collect.md` |
| Linux + 需要原生堆栈 | `references/perfcollect.md` |
| 容器/K8s（控制台访问） | `references/dotnet-trace-collect.md`（或 `dotnet-trace-collect-linux.md`） |
| 容器/K8s（无控制台） | `references/dotnet-monitor.md` |

#### 快速决策矩阵（初步筛选）

| 环境 | 推荐工具 | 备用/备注 |
|-------------|----------------|------------------|
| Windows + 现代 .NET + 管理 | PerfView | 如果管理员不可用，使用 `dotnet-trace` |
| Windows + .NET Framework + 管理 | PerfView | 无管理员时，没有跟踪备用；对于挂起/内存泄漏，直接提供转储命令（`procdump -ma` 或任务管理器），因为 `dump-collect` 不支持 .NET Framework |
| Linux + .NET 10+ + root | `dotnet-trace collect-linux` | 如果 root 或内核先决条件未满足，使用 `dotnet-trace` |
| Linux + .NET 10 之前 | `dotnet-trace` | 当需要原生堆栈时添加 `perfcollect`（需要 root） |
| Linux 容器/Kubernetes | 控制台工具（如果处于工作负载上下文中）；`dotnet-monitor`（如果无控制台访问） | 详细信息请参阅 Linux 容器 / Kubernetes 部分 |

#### Windows（非容器，现代 .NET）

1. **PerfView**（首选）— 生成更丰富的基于 ETW 的数据；需要管理员权限。对于 **请求缓慢**，添加 `/ThreadTime` 以捕获线程级等待和阻塞细节。
2. **`dotnet-trace`** — 当管理员权限不可用时作为备用。
3. 对于 **长时间运行的复现**：使用 PerfView 并带有 `/StopOn` 触发器，该触发器在您想要捕获的症状上触发（例如，`/StopOnPerfCounter`、`/StopOnGCEvent`、`/StopOnException`），并带有循环缓冲区（`/CircularMB` + `/BufferSizeMB`）。**关键**：停止触发器必须在有趣的事件上触发，而不是在恢复时触发。循环缓冲区会不断覆盖旧数据，因此如果您在恢复时触发，收集停止时缓冲区可能已经覆盖了有趣的行为。仅在已知启动事件先于停止事件时添加 `/StartOn`。对于 **请求缓慢**，默认情况下不包含停止触发器——让用户根据其特定场景设计一个。

#### Windows 容器

1. **PerfView** — 大多数 Windows 容器（包括 Windows 上的 Kubernetes）默认使用进程隔离。从主机收集数据时使用 `/EnableEventsInContainers`。收集后，您有两个选项：
   - **在容器仍在运行时本地分析** — PerfView 可以深入到正在运行的容器中以解析符号，因此您可以在主机机器上立即打开跟踪。
   - **离机分析** — 在容器关闭之前，将 `.etl.zip` 复制到容器中，并在其中运行 `PerfViewCollect merge /ImageIDsOnly` 以嵌入符号信息。然后复制合并后的跟踪。如果没有此合并步骤，容器中的二进制文件的符号在其他机器上将无法解析。
   
   对于不太常见的 Hyper-V 容器，直接在容器内收集。详细命令请参阅 [references/perfview.md](references/perfview.md)。
2. **`dotnet-monitor`**、**`dotnet-trace`** — 如果工具已安装在镜像中，则可以在容器内运行。对于转储，调用 **`dump-collect`** 技能。

#### Windows (.NET Framework)

1. **PerfView** — Windows 上 .NET Framework 的主要诊断工具。需要管理员权限。
2. 相同的长时间复现触发器指导：使用 `/StopOn` 触发器，在症状上触发（例如，`/StopOnPerfCounter`、`/StopOnGCEvent`、`/StopOnException`）并带有 `/CircularMB` + `/BufferSizeMB`。
3. **无管理员权限**：PerfView 需要管理员权限，对于 .NET Framework 没有备用的跟踪工具。在没有管理员权限的情况下仍然可以捕获进程转储——直接提供转储命令（例如，`procdump -ma <PID>` 或任务管理器），因为 `dump-collect` 技能不支持 .NET Framework。转储有助于诊断挂起和内存泄漏。但是，对于 **高 CPU**、**请求缓慢** 和 **过度 GC**，如果没有管理员权限，则无法在 .NET Framework 上进行调查。建议用户获取管理员权限。

#### Linux（非容器，.NET 10+）

1. **`dotnet-trace collect-linux`**（首选）— 使用 `perf_events` 以获取更丰富的跟踪，包括原生调用堆栈和内核事件。默认情况下捕获整个机器（不需要 PID）。需要 root 和内核 >= 6.4。
2. **`dotnet-trace`** — 当 root 权限不可用或内核要求未满足时作为备用。仅捕获托管堆栈。

#### Linux（非容器，.NET 10 之前）

1. **`dotnet-trace`**（首选）— 托管跟踪收集；不需要管理员权限。
2. **`perfcollect`** — 当需要 **原生调用堆栈** 时（需要管理员/root）。

#### Linux 容器 / Kubernetes

**如果在工作负载上下文中运行**（即，您有控制台访问权限到容器），优先使用基于控制台的工具。这些比 `dotnet-monitor` 更容易设置，`dotnet-monitor` 需要身份验证配置和 sidecar 部署：

1. **`dotnet-trace collect-linux`** (.NET 10+ with root) — 生成最丰富的跟踪，包括原生调用堆栈和内核事件。
2. **`dotnet-trace`** — 如果工具已安装在镜像中，则可以在容器内运行。对于转储，调用 **`dump-collect`** 技能。
3. **`perfcollect`** — 当在 .NET 10 之前的容器中需要原生堆栈时（需要 `SYS_ADMIN` / `--privileged`）。

**如果不在工作负载上下文中运行**（无控制台访问），或者 `dotnet-monitor` 已经部署：

1. **`dotnet-monitor`** — 专为容器设计；作为 sidecar 运行。应用程序容器中不需要任何工具。当控制台访问不可用时，这是最简单的选项。

#### 内存转储

当需要转储时（内存泄漏、挂起），**不要**为现代 .NET 直接提供转储收集命令——调用 **`dump-collect`** 技能。`dump-collect` 技能仅支持现代 .NET (.NET Core 3.0+)。对于 **.NET Framework**，直接提供转储收集指导（例如，`procdump -ma <PID>` 或任务管理器）。这项技能仅专注于跟踪收集。

#### 内存泄漏

- **捕获两个转储**，随着内存增加（例如，一个早期，一个在显著增长后）。调用 **`dump-collect`** 技能进行转储收集——不要直接提供转储命令。在 PerfView 中比较转储，以查看哪些对象增加了——这是识别泄漏最有效的方法。
- **无管理员权限**：两个进程转储可以提供关于堆上增长的信息，但可能不足以识别根本原因。如果转储不足以解决问题，请在具有管理员权限的环境中复现问题以收集更丰富的数据（跟踪）。
- **Linux 上的现代 .NET（.NET 10 之前）**：建议两个转储捕获（调用 `dump-collect` 技能）进行堆比较，加上 `dotnet-trace` 在内存增长期间（用于分配跟踪）。两者结合提供了最佳视图。
- **Linux 上的现代 .NET 10+ with root**：建议两个转储捕获（调用 `dump-collect` 技能）进行堆比较，加上 `dotnet-trace collect-linux` 在内存增长期间（包括原生堆栈的更丰富数据）。不需要触发器——在增长期间捕获即可。两者结合提供了最佳视图。
- **.NET Framework**：建议两个转储加上内存增长期间的 PerfView 跟踪，以查看正在分配的内容。`dump-collect` 技能不支持 .NET Framework，因此直接提供转储命令（例如，`procdump -ma <PID>` 或任务管理器中的右键单击 → 创建转储文件）。不需要触发器——只需在增长期间捕获跟踪即可。不要等待 `OutOfMemoryException`。

#### 过度 GC

过度 GC 需要一个 **跟踪** 来分析 GC 事件、暂停时间和分配模式——转储是不够的。

- **Windows (PerfView)**: 使用 `PerfView collect /GCCollectOnly` 以捕获 GC 事件。
- **Linux (dotnet-trace)**: 使用 `dotnet-trace collect -p <PID> --profile gc-verbose`。
- **Linux .NET 10+ with root**: 使用 `dotnet-trace collect-linux --profile gc-verbose` 以获取更丰富的数据，包括原生堆栈。
- **容器**：`dotnet-monitor` 可以通过其 REST API (`/trace?profile=gc-verbose`) 捕获 GC 跟踪。

#### 请求缓慢

请求缓慢需要一个 **线程时间跟踪** 来查看线程花费时间的位置——等待锁、I/O、外部调用等。由于线程时间跟踪会生成更多数据，因此请使用更大的缓冲区。对于 ASP.NET Core 应用程序，还启用 `Microsoft.AspNetCore.Hosting` 和 `Microsoft-AspNetCore-Server-Kestrel` 提供程序以获取服务器端请求生命周期时间（请求何时到达，处理请求花费多长时间）。

- **Windows (PerfView)**: 使用 `PerfView /ThreadTime collect /BufferSizeMB:1024 /CircularMB:2048`。`/ThreadTime` 参数添加了线程级等待和阻塞细节。对于 ASP.NET Core，添加 Kestrel 提供程序：`PerfView /ThreadTime collect /BufferSizeMB:1024 /CircularMB:2048 /Providers:*Microsoft.AspNetCore.Hosting,*Microsoft-AspNetCore-Server-Kestrel`。默认情况下不包含停止触发器——让用户根据其特定场景设计一个。
- **Linux (dotnet-trace)**: `dotnet-trace` 默认捕获线程时间数据——不需要特殊参数。使用 `dotnet-trace collect -p <PID>`。对于 ASP.NET Core，添加 Kestrel 提供程序：`dotnet-trace collect -p <PID> --providers Microsoft.AspNetCore.Hosting,Microsoft-AspNetCore-Server-Kestrel`。
- **Linux .NET 10+ with root**: 使用 `dotnet-trace collect-linux --profile thread-time` 以获取更丰富的数据，包括原生堆栈。对于 ASP.NET Core，添加：`--providers Microsoft.AspNetCore.Hosting,Microsoft-AspNetCore-Server-Kestrel`。
- **容器**：`dotnet-monitor` 可以通过其 REST API (`/trace?pid=<PID>&durationSeconds=30`) 捕获跟踪。

#### 挂起

1. **首先使用跟踪** 了解线程正在做什么。使用适用于环境的适当跟踪工具（Windows 上的 PerfView 带有 `/ThreadTime`，Linux 上的 `dotnet-trace`，.NET 10+ Linux with root 上的 `dotnet-trace collect-linux --profile thread-time`）。跟踪可以揭示：
   - **活锁**（线程在没有前进的情况下旋转）——线程看起来很忙，但应用程序没有进展。
   - **线程饥饿**——线程池已耗尽，排队的工作项没有被处理。这看起来像死锁，但根本原因不同。
   - **是否有任何前进**——如果某些线程在进展，问题可能是瓶颈而不是真正的挂起。
2. **如果跟踪不能解释挂起**，问题可能是一个 **真正的死锁**（线程相互等待形成循环）。在这种情况下，调用 **`dump-collect`** 技能收集进程转储——不要直接提供转储命令。
3. **使用调试器分析转储** 以检查线程堆栈并识别锁循环：
   - **Windows**：Visual Studio 或 WinDbg 带有 SOS 调试器扩展。
   - **Linux**：`lldb` 带有 SOS 调试器扩展。

#### 网络问题

网络问题（来自下游服务的 HTTP 5xx 错误、请求超时、连接失败、DNS 解析失败、TLS 握手失败、连接池耗尽）需要一个 **线程时间跟踪** 和 **网络事件提供程序**。线程时间跟踪显示线程被阻塞的位置（慢速下游调用、线程饥饿），而网络事件显示请求生命周期——哪些请求失败、返回了哪些状态码、DNS 解析和 TLS 握手花费了多长时间、请求等待连接池多长时间。

对于 **.NET Framework**，`PerfView /ThreadTime` 已经收集了相关的网络事件（来自 `System.Net` ETW 提供程序）——不需要额外的提供程序。对于 **现代 .NET**，必须显式启用 `System.Net.*` EventSource 提供程序：

| 提供程序 | 覆盖范围 |
|----------|----------|
| `System.Net.Http` | HttpClient/SocketsHttpHandler — 请求生命周期、HTTP 状态码、连接池 |
| `System.Net.NameResolution` | DNS 查找（开始/停止、持续时间） |
| `System.Net.Security` | TLS/SSL 握手（SslStream） |
| `System.Net.Sockets` | 低级套接字连接/断开 |

来自 `System.Net.Http` 的关键事件：`RequestStart`（方案、主机、端口、路径），`RequestStop`（statusCode — 如果没有收到响应则为 `-1`），`RequestFailed`（超时、连接拒绝等的异常消息），`RequestLeftQueue`（等待池中连接的时间——指示连接池耗尽），`ConnectionEstablished`，`ConnectionClosed`。

使用带有网络提供程序的线程时间跟踪收集（仅限现代 .NET——.NET Framework 仅需要 `PerfView /ThreadTime`）：

- **Windows (PerfView)**: 使用 `PerfView /ThreadTime collect /BufferSizeMB:1024 /CircularMB:2048 /Providers:*System.Net.Http,*System.Net.NameResolution,*System.Net.Security,*System.Net.Sockets`。对于 .NET Framework，省略 `/Providers` 标志——`/ThreadTime` 已经包含网络事件。线程时间跟踪显示线程被阻塞的位置，而网络事件显示请求失败的原因。
- **Linux (dotnet-trace)**: `dotnet-trace` 默认捕获线程时间数据，但指定 `--providers` 会覆盖默认值，因此您必须包含 `--profile`：`dotnet-trace collect -p <PID> --profile dotnet-common,dotnet-sampled-thread-time --providers System.Net.Http,System.Net.NameResolution,System.Net.Security,System.Net.Sockets`。
- **Linux .NET 10+ with root**: 使用 `dotnet-trace collect-linux --profile dotnet-common,cpu-sampling,thread-time --providers System.Net.Http,System.Net.NameResolution,System.Net.Security,System.Net.Sockets`。
- **容器**：`dotnet-monitor` 可以通过其 REST API 捕获带有自定义提供程序的跟踪。

#### 程序集加载问题

对于现代 .NET，程序集加载问题（`FileNotFoundException`、`FileLoadException`、`ReflectionTypeLoadException`、版本冲突、跨 AssemblyLoadContext 的重复程序集加载）需要收集来自 `Microsoft-Windows-DotNETRuntime` 提供程序的 **程序集加载绑定事件**，关键字为 `0x4`。这些事件跟踪运行时程序集解析算法的每个步骤——哪些路径被探测、哪个 AssemblyLoadContext 处理加载、加载是否成功或失败，以及原因。对于 .NET Framework，相同的提供程序和关键字适用于基于 ETW 的收集；此外，Fusion Log Viewer (`fuslogvw.exe`) 可以在不需要跟踪的情况下诊断程序集绑定失败。

提供程序规范是 `Microsoft-Windows-DotNETRuntime:0x4:4`（提供程序名称、AssemblyLoader 关键字、信息性详细程度）。

- **Windows (PerfView)**: 默认 PerfView 跟踪已经包含绑定事件——只需运行 `PerfView collect` 而无需额外的提供程序。对于较小的跟踪文件，使用 `PerfView collect /ClrEvents:Default-Profile`，这将删除最详细的默认事件，同时保留诊断程序集加载问题所需的绑定事件。
- **Linux / 跨平台 (dotnet-trace)**: 使用 `dotnet-trace collect --clrevents assemblyloader -- <path-to-built-exe>` 启动并跟踪进程，或 `dotnet-trace collect --clrevents assemblyloader -p <PID>` 附加到正在运行的进程。
- **Linux .NET 10+ with root**: 使用 `dotnet-trace collect-linux --clrevents assemblyloader`。
- **容器**：`dotnet-monitor` 可以通过其 REST API 捕获带有加载提供程序的跟踪。

对于在启动时失败且生命周期短暂的进程（加载程序集问题很常见），优先使用 `dotnet-trace` 启动形式（`-- <path-to-built-exe>`）而不是通过 PID 附加，因为进程可能在您能够附加之前就退出了。

推荐工具时解释权衡。例如：
- PerfView 提供更丰富的数据，但需要管理员；在 Windows（包括 Windows 容器）上运行。
- `dotnet-trace` 跨平台运行，不需要管理员权限，但捕获的系统级细节较少。
- `perfcollect` 捕获原生调用堆栈，但需要管理员/root。
- `dotnet-monitor` 是容器/K8s 中控制台访问不可用时最佳选项，但需要 sidecar 部署和身份验证配置。

### 第三步：指导数据收集

提供推荐的工具的特定命令。从 [工具参考查找](#tool-reference-lookup) 表中加载适当的参考文件以获取详细的命令行示例。

包含以下关键指导：

1. **安装**：如果工具尚未可用，如何安装工具（例如，`dotnet tool install -g dotnet-trace`）。**当推荐多个工具时，提供每个工具的安装和使用说明**——不要提及工具而不显示如何安装和使用它。
2. **PID 发现（在任何 `-p <PID>` 命令之前必需）**：首先验证目标进程（例如：`dotnet-trace ps`, `curl <monitor-endpoint>/processes`, 或在容器内使用 `ps`）。如果应用程序预期为容器中的 PID 1，仍然在收集之前验证。
3. **收集命令**：要运行的精确命令，包括相关提供程序、输出格式和持续时间。
4. **容器注意事项**：
   - 从**容器内部**收集：确保工具已安装在镜像中，或使用 `kubectl cp` 将其复制到容器中。
   - 从**容器外部**收集：使用 `dotnet-monitor` 作为 sidecar，并使用共享诊断端口（`/tmp` 中的 Unix 域套接字）。
   - Kubernetes: `dotnet-monitor` 作为 sidecar 容器，或 `kubectl debug` 用于临时调试容器。
5. **长时间运行的复现**（Windows/PerfView）：显示如何使用触发器参数和循环缓冲区设置。
6. **输出位置**：收集的文件将保存的位置以及如何将其复制到目标以进行分析。
7. **工件交接清单**：包括运行时版本、操作系统/内核、容器镜像标签或构建 SHA、PID/进程名称、UTC 收集开始/结束时间戳、使用的精确命令和最终工件路径，以便将跟踪交给其他人进行分析。

### 第四步：推荐分析方法

数据收集后，推荐用于分析的适当工具。**不要**执行分析——只需向开发者指向正确的工具和文档。

| 收集的数据 | 分析工具 | 备注 |
|-------------|----------------|-------|
| `.nettrace` 文件 | PerfView (Windows), Speedscope (web) | PerfView 在 Windows 上提供最丰富的视图 |
| `.etl` / `.etl.zip` 文件 | PerfView | PerfView 或 perfcollect 的 ETW 跟踪 |
| `perf.data.nl` from perfcollect | PerfView (Windows) | 将文件复制到 Windows 机器上并使用 PerfView 打开 |

## 验证

- [ ] 推荐的工具与开发者的运行时、操作系统和部署拓扑兼容
- [ ] 收集命令无错误运行
- [ ] 输出文件生成在预期位置
- [ ] 开发者知道使用哪个分析工具来分析收集的数据

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|----------|
| 在 .NET Framework 上使用 `dotnet-trace` | `dotnet-trace` 仅适用于现代 .NET (.NET Core 3.0+)。使用 PerfView for .NET Framework。 |
| 无管理员权限的 PerfView | PerfView 需要管理员权限进行 ETW 跟踪。如果管理员不可用，则回退到 `dotnet-trace`。 |
| 容器中无 `SYS_ADMIN` 的 `perfcollect` | 容器默认会丢弃 `SYS_ADMIN`。运行时使用 `--privileged` 或添加 `SYS_ADMIN` 功能，或回退到 `dotnet-trace`。 |
| 来自长时间复现的巨大跟踪文件 | 在 Windows 上，使用 PerfView `/StopOn` 触发器，在您想要捕获的症状上触发（例如，`/StopOnPerfCounter`, `/StopOnGCEvent`, `/StopOnException`）并带有 `/CircularMB` 和 `/BufferSizeMB`。**永远不要在恢复时触发**——循环缓冲区会不断覆盖旧数据，因此在收集停止时，有趣的行为可能会丢失。 |
| 容器中无法访问诊断端口 | 将 `/tmp` 挂载为应用程序容器和 `dotnet-monitor` sidecar 之间的共享卷，以便诊断 Unix 域套接字。 |
| 忘记在容器镜像中安装工具 | 将 `dotnet tool install` 添加到您的 Dockerfile 中，或使用 `dotnet-monitor` 作为 sidecar 来避免修改应用程序镜像。 |
| 在生产环境中使用 `--no-auth` 暴露 `dotnet-monitor` | 保持身份验证启用，绑定到 localhost，并使用 `kubectl port-forward` 进行访问。仅对短期隔离调试使用 `--no-auth`。 |
| 仅收集 CPU/线程时间跟踪以解决网络问题 | 仅使用 CPU 和线程时间跟踪无法显示 HTTP 状态代码、DNS 时间或连接池行为。在 CPU 和线程时间跟踪旁边添加网络提供程序 (`System.Net.Http`, `System.Net.NameResolution`, `System.Net.Security`, `System.Net.Sockets`)。 |
| 启用所有网络提供程序，而只需要一个 | 每个网络提供程序都会增加开销。如果问题是明显的 HTTP 级别（5xx 状态代码），`System.Net.Http` 可能就足够了。当根原因不明确时，添加 DNS、TLS 和套接字提供程序。 |
