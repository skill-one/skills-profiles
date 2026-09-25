## 诊断缓慢的并行构建（从这里开始）

按顺序执行此检查清单——它针对的是常见的根本原因（无法并行化的串行依赖链）：

1. **确认并行化已开启**。使用 `dotnet build -m /bl:{}`
   (PowerShell: `dotnet build -m -bl:{{}}`) 重新构建。`-m` 不带数字时使用所有逻辑处理器；没有 `-m` 时，MSBuild 运行单个节点（串行）。
2. **找到关键路径**。从 binlog 中读取每个项目的耗时和节点时间线。如果总构建时间 ≈ 某个依赖链上所有项目的总和，那么这条链——而不是 CPU 数量——就是瓶颈。
3. **明确命名该链**，例如 `Core → Api → Web → Tests`。长串行链无论如何 `-m` 多大都保持串行，因为每个项目都等待其前一个项目。
4. **查找不必要的 `ProjectReference` 边缘**，这些边缘会拉长链——只需要构建顺序（不需要输出程序集）的引用，或者可以是 `PackageReference` 的引用，会强制进行不需要的序列化。
5. **建议扁平化**：打破虚假依赖，使独立项目可以并行构建，并考虑使用 `/graph` 进行更好的调度。

## MSBuild 并行化模型

- `/maxcpucount` (或 `-m`)：工作节点（进程）的数量
- 默认：1 个节点（串行！）始终使用 `-m` 进行并行构建
- 推荐：`-m` 不带数字 = 使用所有逻辑处理器
- 每个节点一次构建一个项目
- 项目根据依赖图进行调度

## 项目依赖图

- MSBuild 按依赖顺序（拓扑排序）构建项目
- 关键路径：决定最小构建时间的依赖项目最长链
- 瓶颈：如果项目 A 依赖 B、C、D，而 B 需要 60 秒，C 和 D 只需 5 秒，则 B 是瓶颈
- 诊断：使用 `performancesummary` 将 binlog 重播到诊断日志中，并检查项目性能摘要——显示每个项目的耗时；grep `node.*assigned` 检查调度
- 宽图（许多独立项目）并行化效果良好；深图（长链）则不然

## 图构建模式 (`/graph`)

- `dotnet build /graph` 或 `msbuild /graph`
- 它改变的内容：MSBuild 在构建之前构建完整的项目依赖图
- 优点：更好的调度、避免冗余评估、启用隔离构建
- 限制：所有项目必须使用 `<ProjectReference>`（不能使用程序化 MSBuild 任务引用）
- 使用场景：包含许多项目的大型解决方案、CI 构建
- 不使用场景：在构建时动态发现引用的项目

## 优化项目引用

- 减少 `<ProjectReference>` 的不必要使用——每个都会增加依赖链
- 使用 `<ProjectReference ... SkipGetTargetFrameworkProperties="true">` 避免额外评估
- `<ProjectReference ... ReferenceOutputAssembly="false">` 用于仅需要构建顺序的依赖
- 考虑将 ProjectReference 替换为 PackageReference（预构建的 NuGet）
- 使用 `solution filters` (`.slnf`) 构建解决方案的子集

## BuildInParallel

- 在自定义目标中使用 `<MSBuild Projects="@(ProjectsToBuild)" BuildInParallel="true" />`
- 没有 `BuildInParallel="true"`，MSBuild 任务会按顺序批处理项目
- 确保 `/maxcpucount` > 1 才能生效

## 多线程 MSBuild 任务

- 单个项目构建内，单个任务可以运行多线程
- 实现 `IMultiThreadableTask` 接口的任务可以在多个线程上运行
- 任务必须通过 `[MSBuildMultiThreadableTask]` 声明线程安全

## 使用 Binlog 分析并行化

### 主要：binlog MCP（推荐）

使用 **binlog MCP 服务器** (`Microsoft.AITools.BinlogMcp`)（在 `binlog` MCP 命名空间下提供）：

1. 使用 expensive_projects 工具 → 找到最慢的项目，并比较单个与总构建时间
2. 使用 expensive_targets 工具 → 找到瓶颈目标
3. 使用 project_target_times 工具 → 深入特定项目的目标级耗时
4. 理想：构建时间应远小于项目时间总和（并行化）
5. 如果构建时间 ≈ 项目时间总和：太多串行依赖，或一个慢项目阻塞其他项目

### 备用：文本日志重播（当 MCP 不可用时）

逐步操作：

1. 重播 binlog：`dotnet msbuild build.binlog -noconlog -fl -flp:v=diag;logfile=full.log;performancesummary`
2. 在 `full.log` 的末尾检查项目性能摘要
3. 理想：构建时间应远小于项目时间总和（并行化）
4. 如果构建时间 ≈ 项目时间总和：太多串行依赖，或一个慢项目阻塞其他项目
5. `grep 'Target Performance Summary' -A 30 full.log` → 找到瓶颈目标
6. 考虑拆分大型项目或优化关键路径

## CI/CD 并行化技巧

- 在 CI 中使用 `-m`（许多 CI 运行器具有多个核心）
- 考虑将解决方案拆分为构建阶段以实现极致并行化
- 使用构建缓存（NuGet 锁文件、确定性构建）以避免重新构建未更改的项目
- `dotnet build /graph` 与结构化 CI 管道配合良好
