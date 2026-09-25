这项技能是 `argent-react-native-optimization` 的补充，而不是它的替代品。

物理 iPhone：不支持；`react-profiler-*` 会拒绝 `kind: "device"`。请在模拟器上进行分析。

## 2. 工具概述

### React Profiler (Hermes / React 提交)

| 工具                              | 目的                                                                                                                                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `react-profiler-start`            | 开始 CPU 采样 + 注入 React 提交捕获钩子。可选：`sample_interval_us`（默认 100）。                                                                                                                                                              |
| `react-profiler-stop`             | 停止录制；将 cpuProfile + commitTree 存储在会话中。                                                                                                                                                                                                        |
| `react-profiler-status`           | **如果在流程中中断时调用，切勿在其他场景中调用**（调试器断开、Metro 重新加载、暂停、子代理交接、任何疑问）。返回 `session_status: "active" \| "taken_over" \| "stopped" \| "no_react_runtime"`。无副作用。 |
| `react-profiler-analyze`          | 运行管道 -> 带有 CPU 增强的热点提交报告，按 `totalRenderMs` 降序排列。原始数据保存到磁盘。                                                                                                                                                     |
| `react-profiler-component-source` | AST 查找：文件、行、记忆化状态、组件的 50 行源代码。                                                                                                                                                                                                   |
| `react-profiler-renders`          | 活态 fiber 遍历：每个组件的渲染次数 + 持续时间（无需分析会话）。                                                                                                                                                                                         |
| `react-profiler-fiber-tree`       | 活态 fiber 遍历：作为 JSON 的完整组件层次结构。                                                                                                                                                                                                        |

### 钻探查询工具（分析后调用）

| 工具                       | 目的                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| `profiler-cpu-query`       | 针对性 CPU 调查：顶级函数、时间窗口 CPU、调用树、每个组件的 CPU。                               |
| `profiler-commit-query`    | 针对性提交调查：按组件、时间范围、提交索引或级联树。                                          |
| `profiler-stack-query`     | iOS Instruments 钻探：挂起堆栈、函数调用者、线程分解、泄漏详细信息。                             |
| `profiler-combined-report` | 当 React Profiler 和原生 Profiler 并行运行时的交叉相关报告。                                     |
| `profiler-load`            | 从磁盘列出并重新加载以前的分析会话，以便使用查询工具重新调查。                                     |

对于原生分析（CPU 热点、UI 挂起、内存泄漏），请参阅 `argent-native-profiler` 技能。

---

## 3. 代理行为指南

在整个分析流程中遵循以下规则：

- 并行启动 `react-profiler-start` 和 `native-profiler-start`（一个消息中的两个工具调用）。两者都需要 `device_id`；为两者使用相同的 UDID，以便以后可以关联它们的数据。这提供了最佳覆盖率。
- 如果用户只想进行原生分析，请使用 `argent-native-profiler` 技能的工作流程。只有当用户**已经明确表示**在本会话中不想进行原生分析时，才跳过 `native-profiler-start`

### 分析后：询问下一步操作

在展示分析报告后，始终询问用户他们想做什么。提供以下选项：

1. **进一步调查** — 使用查询工具（CPU 调用树、提交级联、挂起堆栈等）深入特定发现，以便在做出更改之前有信心地确定根本原因。
2. **实施修复** — 根据当前发现应用更改，然后重新分析以测量指标是否发生变化（改善、退化或保持不变）。
3. **暂时完成** — 接受报告原样。

不要在报告后默默继续。报告是起点，不是终点——查询工具的存在就是为了让你深入挖掘报告标记的任何内容。

### 调查期间：主动使用查询工具

当钻探时，根据你发现的内容链式调用查询工具：

- 一个热点提交 -> `profiler-commit-query` 模式=`by_index` 查看所有组件 -> `profiler-cpu-query` 模式=`component_cpu` 对最慢的一个 -> `profiler-cpu-query` 模式=`call_tree` 对热点函数 -> 阅读源文件 -> 提出修复。
- 一个内存泄漏 -> `profiler-stack-query` 模式=`leak_stacks` 识别负责的模块 -> 如果可以行动，则阅读原生源代码。
- 一个原生挂起 -> `profiler-stack-query` 模式=`hang_stacks` 获取原生调用链 -> 与 React 提交时间进行关联。

### 修复后：始终重新分析

应用修复后，始终重新分析相同的场景。比较前/后指标（提交持续时间、CPU 时间、渲染次数）并如实报告：目标指标是否改善、保持不变或退化？是否有任何其他指标变差？如果你需要参考原始数据，请使用 `profiler-load` 重新加载修复前的会话。如果修复没有显示改善或引入回归，请明确说明并重新考虑方法。

### 使用流程进行可重复的分析

当分析需要特定的交互序列（滚动列表、导航屏幕、触发动画）时，**在第一次分析运行之前使用 `argent-create-flow` 技能记录交互为流程**。然后对每个后续运行重播相同的流程。这消除了交互差异作为混杂因素，并使前/后比较有意义。尤其是在：

- 你即将应用修复后重新分析（步骤 8）。
- 用户要求你比较多个分析会话。
- 交互路径超过 2-3 步。

---

## 4. 标准分析工作流程

**按顺序完成所有步骤——不要中途打断。**

### 步骤 1：开始分析

注意上面提到的 react-native 和 ios-native Profiler 选择，在启动会话时启动工具。**保存 `startedAtEpochMs` 从响应中**——你需要它用于注释偏移。本会话中的每个后续 Profiler/查询调用都必须使用相同的 `device_id`。开始之前，与用户定义轻量级的成功标准：哪个指标最重要（例如，`totalRenderMs`、特定提交持续时间、组件的渲染次数）以及什么阈值有意义。这为后续评估提供了锚点。成功：

- 如果用户要求你执行分析，确定如何使用 `argent-device-interact` 技能中描述的工具进行分析。
- 如果用户表示他们希望自己执行交互——建议执行什么交互（例如，“滚动列表”、“切换标签”）并等待他们的回复。
  如果你收到关于**现有分析会话**被另一个代理拥有的信息：
- 如果会话被标记为“过时”，你可以不经用户允许就接管它
- 如果会话不是“过时”——在采取行动并终止其他会话之前，**停止并询问用户你应该做什么**，解释情况。

#### 每次交互都注释

每次 `gesture-tap` 或 `gesture-swipe` 调用后，使用返回的 `timestampMs` 记录一个注释。计算 `offsetMs = timestampMs - startedAtEpochMs`。对**每个**交互进行此操作——包括后退导航滑动，而不仅仅是主要操作。将所有收集到的注释传递给 `react-profiler-analyze` 在步骤 3。

### 步骤 2：停止并收集

并行调用 `react-profiler-stop` **和** `native-profiler-stop`。如果步骤 1 中没有启动 `native-profiler-stop`，则跳过 `native-profiler-stop`。注意 `duration_ms` 和 `fiber_renders_captured`。
如果 `fiber_renders_captured: 0`，警告用户——React 提交数据可能丢失。

### 步骤 3：分析

使用 `port`、`device_id`、`project_root`、`platform` 和 `rn_version` 调用 `react-profiler-analyze`。报告包括元数据，例如 `reactCompilerEnabled`、`strictModeEnabled` 和 `buildMode`——在返回的 markdown 报告中检查这些内容。

如果你使用 `gesture-tap`/`gesture-swipe` 执行交互，请传递 `annotations` 以标记每个操作何时发生。每个注释的 `offsetMs` 必须计算为 `tapTimestampMs - startedAtEpochMs`，其中 `tapTimestampMs` 是 `gesture-tap/gesture-swipe` 工具返回的 `timestampMs`，`startedAtEpochMs` 是 `react-profiler-start` 返回的。**不要**使用 `Date.now()` 进行此计算——只使用工具返回值的服务器端时间戳。

如果双重分析，也调用 `native-profiler-analyze`，然后**你必须**调用 `profiler-combined-report` 获取交叉相关视图——当两个 Profiler 都运行时**不要跳过此步骤**；组合报告会显示单独报告遗漏的关联。

分析报告包括**每个提交的 CPU 热点**——显示在每个慢速 React 提交期间运行的确切 JS 函数。原始数据自动保存到磁盘以供后续重新加载。

### 步骤 4：评估结果

分析结果是否给你应用程序出错的清晰图像——**不要假设总是存在改进**，通过 react-native 的工作原理逻辑地验证结果。确保提供诚实的反馈，并在需要时准备好改变方法。

### 步骤 5：展示发现并询问下一步操作

展示关键发现的简洁摘要——展示是否存在改进的可能性以及执行进一步操作如何影响性能。然后遵循“分析后”指南——询问是否要进一步调查、实施修复（如果可用）或停止。

### 步骤 6：钻探调查（迭代）

根据报告中的发现，使用查询工具进行更深入的调查：

- **慢组件？** -> `profiler-cpu-query` 模式=`component_cpu` component_name=`AppNavigator` — 显示在该组件提交期间运行的 JS 函数。
- **想查看调用树？** -> `profiler-cpu-query` 模式=`call_tree` function_name=`expensiveFunction` — 显示调用者和被调用者。
- **在时间窗口期间发生了什么？** -> `profiler-commit-query` 模式=`by_time_range` — 列出范围内的所有提交。
- **完整的提交详情？** -> `profiler-commit-query` 模式=`by_index` commit_index=38 — 所有组件、属性更改、父级级联。
- **谁触发了谁？** -> `profiler-commit-query` 模式=`cascade_tree` — 视觉父级-子级级联。
- **iOS 挂起详情？** -> `profiler-stack-query` 模式=`hang_stacks` — 挂起期间的原生调用堆栈。

根据需要重复，直到你确定根本原因函数和文件，参考步骤 4 进行诚实评估。每次调查轮次后，询问用户是否想继续挖掘或转到修复。

### 步骤 7：重新加载以前的会话

如果你分析了多个场景并需要重新查看早期数据：

1. 调用 `profiler-load` 模式=`list` 查看所有保存的会话及其时间戳（列表现在还显示 Runtime / Device / Metro bundle 列来帮助识别正确的会话）。
2. 调用 `profiler-load` 模式=`load_react` session_id=`<timestamp>` device_id=`<UDID>` 重新加载 React 数据。`device_id` 将重新加载限制在 `port:device_id` 缓存槽中。
3. 调用 `profiler-load` 模式=`load_native` session_id=`<timestamp>` device_id=`<UDID>` 重新加载原生 Profiler 数据。
4. 查询工具现在在重新加载的会话数据上操作——**传递相同的 `device_id` 你加载的**，否则它们将错过缓存。

这对于前/后比较很有用：分析、修复、重新分析，然后重新加载原始会话以并排比较指标。

### 步骤 8：应用修复并重新分析

如果存在修复，使用 `react-profiler-component-source` 或读取工具阅读已识别瓶颈的源代码。应用修复，然后重新分析（步骤 1 -> 用户交互 -> 步骤 2 -> 步骤 3 -> 步骤 4）。报告目标指标是否改善、保持不变或退化。还要检查修复是否在其他指标上引入了回归（例如，渲染次数下降但 CPU 时间增加，或另一个组件现在重新渲染更多）。如果修复没有显示净收益或不可接受的权衡，请撤销并重新考虑。

**提示：** 如果交互序列被记录为流程（见“使用流程进行可重复的分析”），请使用 `flow-execute` 重播它，而不是手动重复步骤。这保证了比较的交互条件完全相同。如果流程在重播期间失败（例如，UI 修复改变了布局），请遵循 `argent-create-flow` 的 [诊断重播失败](../argent-create-flow/references/reliability-and-recovery.md#diagnose-a-replay-failure) 来修复流程，然后重试分析周期。

如果用户表示他们不想进行更改，请展示分析报告并跳过修复，但建议用户进行修复。

**React 编译器规则：** 如果分析报告指示 React 编译器已启用，除非你确认编译器退出（检查 `react-profiler-fiber-tree` 在该组件上缺少 `useMemoCache`），否则不要建议 `useCallback`/`useMemo`/`React.memo`。

---

## 5. 重要注意事项

- **开发模式膨胀**：`buildMode: "dev"` 渲染比生产慢约 3 倍。优先考虑高 `normalizedRenderCount`——它按比例扩展到生产。
- **修复后重新运行**：更改后始终重新分析。如实报告指标是否改善、退化或保持不变——不要假设会改善。
- **`excluded` 是信息性的**：`animatedSubtrees` 和 `recyclerChildren` 中的组件按设计重新渲染。
- **Strict Mode**：双重调用渲染。当检测到时，管道自动将 `normalizedRenderCount` 减半。
- **调试器连接**：如果中断，启动的分析也会关闭。在尝试恢复之前，调用 `react-profiler-status`——它告诉你会话是 `active`、`taken_over`、`stopped` 或 `no_react_runtime`，以便你可以决定是停止、重启还是首先重新连接。
- **需要关注的混杂因素**：
  - Live API 数据可能在运行之间不同（不同的有效载荷大小、内容计数），这会独立于你的修复而移动渲染次数和持续时间。注意数据相关组件显示差异时。
  - Profiler 开销使 CPU 测量值膨胀。如果 iOS Instruments 显示 `JSLexer`、`JSONEmitter` 或 Hermes 内部主导 JS 线程，这反映了 Profiler 仪器成本——而不是应用程序工作。忽略这些条目。
  - 运行并不完全可重复。提交持续时间的小幅变化（低于 ~10-15%）可能是噪声；只有一致的、方向性变化才被视为信号。

对于独立的诊断工具（实时渲染统计、fiber 树、CPU 摘要），请参阅 `references/diagnostic-tools.md`。
