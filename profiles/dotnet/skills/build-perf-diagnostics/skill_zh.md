## 性能分析方法论

1. **生成 binlog**：`dotnet build /bl:{} -m`
2. 使用 **binlog MCP 服务器**（`Microsoft.AITools.BinlogMcp`，在 `binlog` MCP 命名空间下暴露）, 该服务器随此插件一起打包

### 当 MCP 不可用时，binlog 重放至文本日志的替代流程：

1. **生成 binlog**：`dotnet build /bl:{} -m`
2. **重放至带性能摘要的诊断日志**：
   ```bash
   dotnet msbuild build.binlog -noconlog -fl -flp:v=diag;logfile=full.log;performancesummary
   ```
3. **读取性能摘要**（在 `full.log` 的末尾）：
   ```bash
   grep "Target Performance Summary\|Task Performance Summary" -A 50 full.log
   ```
4. **查找耗时的目标和任务**：`PerformanceSummary` 部分按累积时间列出了所有目标和任务
5. **检查节点利用率**：grep 查找调度和节点消息
   ```bash
   grep -i "node.*assigned\|building with\|scheduler" full.log | head -30
   ```
6. **检查分析器**：grep 查找分析器耗时
   ```bash
   grep -i "analyzer.*elapsed\|Total analyzer execution time\|CompilerAnalyzerDriver" full.log
   ```

## 关键指标和阈值

- **构建时长**：什么是“正常”——小项目 <10 秒，中等 <60 秒，大型 <5 分钟
- **节点利用率**：理想情况下，节点活跃时间 >80%。利用率低 = 序列化瓶颈
- **单个目标主导**：如果某个目标 >50% 的构建时间，请调查
- **分析器时间与编译时间**：分析器应 <30% 的 Csc 任务时间。如果更高，请考虑移除耗时的分析器
- **RAR 时间**：ResolveAssemblyReference >5 秒令人担忧。>15 秒是病态的

## 常见瓶颈

### 1. ResolveAssemblyReference (RAR) 缓慢

- **症状**：RAR 每个项目耗时 >5 秒
- **根本原因**：引用的 assembly 数量过多，基于网络的引用路径，大型 assembly 搜索路径
- **修复方法**：减少引用数量，为 RAR 重分析使用 `<DesignTimeBuild>false</DesignTimeBuild>`，为诊断设置 `<ResolveAssemblyReferencesSilent>true</ResolveAssemblyReferencesSilent>`
- **高级**：`<DesignTimeBuild>` 和 `<ResolveAssemblyWarnOrErrorOnTargetArchitectureMismatch>`
- **关键洞察**：RAR 在增量构建中无条件运行，因为用户可能已安装 targeting packs 或 GACed assemblies（见 dotnet/msbuild#2015）。对于 .NET Core 微型 assembly，引用计数通常非常高。
- **减少传递性引用**：设置 `<DisableTransitiveProjectReferences>true</DisableTransitiveProjectReferences>` 以避免拉取完整的传递闭包（注意：项目可能需要添加直接引用以使用任何类型）。在构建时仅需要的 ProjectReferences 上使用 `ReferenceOutputAssembly="false"`（API 表面除外）。修剪未使用的 PackageReferences。

### 2. Roslyn 分析器和源生成器

- **症状**：Csc 任务耗时远超预期（文件数 >2× 清理编译时间）
- **诊断**：检查重放日志中 Csc 任务的 Task Performance Summary；grep 分析器耗时消息；比较带和不带分析器的 Csc 时长（`/p:RunAnalyzers=false`）
- **修复方法**：
  - 开发环境中条件禁用：`<RunAnalyzers Condition="'$(ContinuousIntegrationBuild)' != 'true'">false</RunAnalyzers>`
  - 按配置禁用：`<RunAnalyzers Condition="'$(Configuration)' == 'Debug'">false</RunAnalyzers>`
  - 仅代码风格：`<EnforceCodeStyleInBuild Condition="'$(ContinuousIntegrationBuild)' == 'true'">true</RunAnalyzers>`
  - 移除真正冗余的分析器
  - .editorconfig 中的严重性配置（对较低优先级规则）
- **关键原则**：在 CI 中保留分析器强制执行。永远不要直接“移除”分析器——条件配置它们。
- **GlobalPackageReference**：在 `Directory.Packages.props` 中通过 `GlobalPackageReference` 添加的分析器适用于所有项目。考虑测试项目是否需要与生产代码相同的分析器集。
- **EnforceCodeStyleInBuild**：在 `Directory.Build.props` 中设置为 `true` 时，强制在每次构建时进行代码风格分析。应在 CI 环境下（`ContinuousIntegrationBuild`）条件化，以避免减慢开发内循环。

### 3. 序列化瓶颈（单线程目标）

- **症状**：性能摘要显示大部分构建时间集中在单个项目；诊断日志显示节点空闲而一个节点工作
- **常见原因**：没有正确声明依赖的目标，关键路径上的单个项目
- **修复方法**：拆分大型项目，优化关键路径项目，确保 `BuildInParallel`

### 4. 过度文件 I/O（复制任务）

- **症状**：复制任务显示高聚合时间
- **根本原因**：复制数千个文件，跨网络驱动器复制，复制任务无意中每个项目（每个文件）运行一次，而不是作为一个批处理（见 dotnet/msbuild#12884）
- **修复方法**：使用硬链接（`<CreateHardLinksForCopyFilesToOutputDirectoryIfPossible>true</CreateHardLinksForCopyFilesToOutputDirectoryIfPossible>`），减少 `CopyToOutputDirectory` 项，在适当情况下使用 `<UseCommonOutputDirectory>true</UseCommonOutputDirectory>`，设置 `<SkipCopyUnchangedFiles>true</SkipCopyUnchangedFiles>`，考虑 `--artifacts-path` (.NET 8+) 用于集中输出布局
- **开发驱动器**：在 Windows 上，切换到开发驱动器（ReFS 带有写时复制和减少的 Defender 扫描）可以显著减少复制密集型构建的文件 I/O 开销。建议用于开发机器和自托管 CI 代理。

### 5. 评估开销

- **症状**：构建开始慢，在编译前没有任何编译
- **根本原因**：复杂的 `Directory.Build.props`，通配符 glob 扫描大型目录，NuGetSdkResolver 开销（即使恢复时也会增加 180-400ms 每个项目评估——见 dotnet/msbuild#4025）
- **修复方法**：减少 `Directory.Build.props` 复杂性，使用 `<EnableDefaultItems>false</EnableDefaultItems>` 为具有显式文件列表的遗留项目，如果可能，避免 NuGet 基于的 SDK 解析器
- 参考：`eval-performance` 技巧以获取详细指导

### 6. 构建中的 NuGet 还原

- **症状**：即使不必要，还原也在每次构建时运行
- **修复方法**：
  - 将还原与构建分离：`dotnet restore` 然后 `dotnet build --no-restore`
  - 启用静态图评估：`Directory.Build.props` 中的 `<RestoreUseStaticGraphEvaluation>true</RestoreUseStaticGraphEvaluation>`——在大型构建中可以节省大量时间（结果取决于工作负载）

### 7. 大型项目数量和图形状

- **症状**：许多小型项目，每个项目耗时很少，但开销累积；深度依赖链使构建序列化
- **考虑**：项目合并，或使用 `/graph` 模式进行更好的调度
- **图形状很重要**：宽依赖图（较少层级，许多并行分支）比深度图（许多层级，序列化）构建更快。从深度重构为宽可以显著提高清理和增量构建时间。
- **操作**：查找不必要的项目依赖，考虑将瓶颈项目拆分为两个，或合并小型叶项目

## 使用 Binlog 重放进行性能分析

使用文本日志重放的逐步工作流程：

1. **带性能摘要的重放**：
   ```bash
   dotnet msbuild build.binlog -noconlog -fl -flp:v=diag;logfile=full.log;performancesummary
   ```
2. **读取目标和任务性能摘要**（在 `full.log` 的末尾）：
   ```bash
   grep "Target Performance Summary\|Task Performance Summary" -A 50 full.log
   ```
   这显示了按累积时间排序的所有目标和任务——相当于查找耗时的目标和任务。
3. **查找每个项目的构建时间**：
   ```bash
   grep "done building project\|Project Performance Summary" full.log
   ```
4. **检查并行性**（多节点调度）：
   ```bash
   grep -i "node.*assigned\|RequiresLeadingNewline\|Building with" full.log | head -30
   ```
5. **检查分析器开销**：
   ```bash
   grep -i "Total analyzer execution time\|analyzer.*elapsed\|CompilerAnalyzerDriver" full.log
   ```
6. **深入特定慢目标**：
   ```bash
   grep 'Target "CoreCompile"\|Target "ResolveAssemblyReferences"' full.log
   ```

## 快速见效清单

- [ ] 使用 `/maxcpucount`（或 `-m`）进行并行构建
- [ ] 将还原与构建分离（`dotnet restore` 然后 `dotnet build --no-restore`）
- [ ] 启用静态图还原（`<RestoreUseStaticGraphEvaluation>true</RestoreUseStaticGraphEvaluation>`）
- [ ] 为复制启用硬链接（`<CreateHardLinksForCopyFilesToOutputDirectoryIfPossible>true</CreateHardLinksForCopyFilesToOutputDirectoryIfPossible>`）
- [ ] 在开发内循环条件禁用分析器：`<RunAnalyzers Condition="'$(ContinuousIntegrationBuild)' != 'true'">false</RunAnalyzers>`
- [ ] 启用引用 assembly（`<ProduceReferenceAssembly>true</ProduceReferenceAssembly>`）
- [ ] 检查损坏的增量构建（见 `incremental-build` 技巧）
- [ ] 检查 bin/obj 冲突（见 `check-bin-obj-clash` 技巧）
- [ ] 使用图构建（`/graph`）进行多项目解决方案
- [ ] 使用 `--artifacts-path` (.NET 8+) 用于集中输出布局
- [ ] 在 Windows 开发机器和自托管 CI 上启用 Dev Drive (ReFS)

## 影响分类

报告发现时，按影响分类以帮助优先修复：

- 🔴 **高影响**（优先处理）：消耗 >10% 总构建时间的项，或单个目标 >50% 的构建时间
- 🟡 **中等影响**：消耗 2-10% 构建时间的项
- 🟢 **快速见效**：易于更改且影响适度的项（例如 Directory.Build.props 中的属性标志）
