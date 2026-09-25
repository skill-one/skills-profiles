## 1. 工具

- `native-profiler-start` — 在已启动的设备上开始分析。iOS：使用 xctrace 进行 CPU、卡顿和内存泄漏的录制。
- `native-profiler-stop` — 停止分析器并将跟踪数据导出到带时间戳的 XML 文件。
- `native-profiler-analyze` — 解析导出的跟踪数据并返回结构化的瓶颈负载。
- `profiler-stack-query` — 深入解析数据：卡顿堆栈、函数调用者、线程分解、内存泄漏详情。
- `profiler-load` — 列出并重新加载来自磁盘的先前跟踪会话以重新调查。
- 物理iPhone：不支持；请使用模拟器。

---

## 2. 平台支持

- **iOS**：后端：通过已启动的模拟器或连接的设备上的 xctrace 使用 Xcode Instruments。需要在 PATH 中安装 Xcode 命令行工具。显示 CPU 热点、UI 卡顿和内存泄漏（instruments `Leaks` 表格）。
- **Android**：后端：通过 `adb shell perfetto` + 进程内 WASM 跟踪处理引擎。显示 CPU 热点和 UI 卡顿，每个卡顿的延迟原因代码，主线程状态分解（`blocked_function` 归因），以及 GC 重叠注释。还报告 RSS 增长信号以指示内存压力；将其视为手动确认的提示，而不是确认的泄漏。目标应用必须可调试或在其清单中包含 `<profileable android:shell="true"/>` 以便捕获 `perf_sample` 调用堆栈。

---

## 3. 调查模式

在 `native-profiler-analyze` 提交发现后，使用 `profiler-stack-query` 深入挖掘根本原因：

- **检测到卡顿** → `profiler-stack-query` 模式=`hang_stacks` 以获取完整的原生调用链 → 模式=`function_callers` 以获取可疑函数 → 阅读原生源代码。
- **CPU 热点** → `profiler-stack-query` 模式=`thread_breakdown` 以获取每个线程的分布 → 模式=`function_callers` 以获取主要函数。
- **内存泄漏** → `profiler-stack-query` 模式=`leak_stacks` 按照对象类型过滤以获取负责的帧和库。
  - iOS：如果泄漏返回未归因（负责帧 `<Call stack limit reached>`），重新运行 `native-profiler-start` 并使用 `malloc_stack_logging: true`。这会冷启动应用并启用 Malloc Stack Logging，使泄漏带有真实的分配回溯（负责帧 + 库）。它重新启动应用并增加开销，因此仅在需要泄漏归因时使用——不用于 CPU/卡顿分析。

在展示发现后，询问用户是否要进一步调查、实施修复或停止。在应用修复后，始终重新分析相同场景并与 `profiler-load` 进行比较。诚实地报告目标指标是否改善、恶化或保持不变。如果修复没有显示净收益或引入其他回归，请说明并重新考虑。

**提示**：为了可重复的 before/after 比较，在第一次分析运行之前使用 `argent-create-flow` 技能将交互序列记录为流程。在后续运行中使用 `flow-execute` 重放以消除交互差异。

> **注意**：`argent-react-native-profiler` 指示在 React 分析的同时自动开始原生分析。此技能的工作流程和调查模式在两种情况下都适用。

---

## 4. 工作流程

**按顺序完成所有步骤——不要中途中断。**

### 第 0 步：确保目标应用正在运行

`native-profiler-start` 工具 **自动检测** 设备上正在运行的应用。
您不需要手动推导 `app_process` — 只需确保应用已启动。

1. 如果应用已在设备上运行，跳到第 1 步（不要传递 `app_process`）。
2. 如果应用未运行，首先使用正确的 bundle ID 使用 `launch-app`。
3. 仅在工具报告多个正在运行的用户应用并且您需要区分时显式传递 `app_process`。

> **注意**：如果有多个构建变体已安装（dev、staging、prod），工具将检测当前正在运行的一个。如果两个都在运行，它将要求您指定。

### 第 1 步：开始录制

调用 `native-profiler-start` 并传递 `device_id`（iOS UDID 或 Android 序列）。工具自动检测正在运行的应用并将跟踪数据保存到 `/tmp/argent-profiler-cwd/`，文件名带时间戳。
让用户与应用交互或通过模拟器工具驱动交互（参见 `argent-device-interact` 技能）。

### 第 2 步：停止并导出

调用 `native-profiler-stop` 并传递 `device_id`。iOS 向 xctrace 发送 SIGINT，等待跟踪打包，并将 CPU、卡顿和泄漏数据导出到 XML — 检查 `exportDiagnostics` 以获取任何导出警告。Android 向设备上的 perfetto 守护进程发送 SIGTERM，轮询 `/proc/<pid>` 直到它退出，然后 `adb pull` `.pftrace` 到主机。

### 第 3 步：分析

调用 `native-profiler-analyze` 并传递 `device_id`。返回一个 Markdown 报告，瓶颈按严重程度分类为 CPU 热点、UI 卡顿或内存泄漏，并按严重程度排序。

### 第 4 步：展示发现并询问下一步操作

展示关键发现的简洁摘要。然后遵循“分析后”指南——询问是否要使用查询工具进一步调查、实施修复或停止。

### 第 5 步：深入调查

使用 `profiler-stack-query` 调查特定发现。参见 §3 调查模式以获取链式指导。

### 第 6 步：重新加载先前会话

要重新访问先前的跟踪：

1. 调用 `profiler-load` 模式=`list` 以查看可用会话。
2. 调用 `profiler-load` 模式=`load_native` session_id=`<timestamp>` device_id=`<UDID>` 以重新解析 XML 文件。
3. 使用 `profiler-stack-query` 调查重新加载的数据。

---

## 5. 理解结果

瓶颈按严重程度分类：

- **RED**：消耗总时间 >15% 的 CPU 函数、所有 UI 卡顿和 **归因** 的内存泄漏（具有已解决的负责帧）。需要立即关注。
- **YELLOW**：消耗总时间 3-15% 的 CPU 函数和 **未归因** 的内存泄漏（`<Call stack limit reached>`，无库——参见内存泄漏的注意事项）。值得调查但可能可以接受。

每种瓶颈类型指示不同类型的问题：

- **CPU 热点**：消耗过多 CPU 时间的原生函数。查找紧密循环、昂贵计算或冗余工作。
- **UI 卡顿**：主线程阻塞足够长时间以导致可见延迟或无响应。通常由同步 I/O、重型布局传递或锁竞争引起。
- **内存泄漏**：已分配但未释放的对象。常见原因包括保留循环、未关闭的资源或忘记的观察者。Argent 通过 `xctrace --attach` 记录，该记录没有 malloc 堆栈历史，因此在模拟器上大多数泄漏返回 **未归因**（`<Call stack limit reached>`，无库）并由良性系统分配主导——这些报告为低置信度的黄色摘要，而不是确认的红色泄漏。对于归因堆栈，在启动时启用 malloc 堆栈日志捕获。

---

## 6. 重要注意事项

- **模拟器与设备**：模拟器分析反映主机 Mac 性能，而不是真实设备硬件。使用设备分析以获取准确的 CPU 时间和内存行为。
- **xctrace 可用性（iOS）**：需要安装 Xcode 命令行工具。使用 `xcrun xctrace version` 验证。
- **分析器开销**：xctrace 仪器增加 CPU 负载。如果 `JSLexer`、`JSONEmitter` 或 Hermes 运行时内部在 CPU 热点结果中主导 JS 线程，这些反映分析器开销——不是应用工作。在评估发现时忽略这些条目。
- **运行间差异**：运行之间 CPU 百分比的小波动是正常的。仅将一致的方向性变化（跨 2 次运行或 >15% 差异）视为可操作的信号。
- **实时数据差异**：如果应用获取实时 API 数据，运行之间不同的响应会独立于代码更改改变渲染工作负载。注意数据依赖屏幕的波动。
