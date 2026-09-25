# 构建性能基线与优化

## 概述

在优化构建之前，你需要一个**基线**。没有测量数据，优化就是盲猜。这项技能涵盖了如何建立基线以及应用系统化优化技术。

**相关技能：**
- `build-perf-diagnostics` — 基于binlog的瓶颈识别
- `incremental-build` — 输入/输出和最新状态检查
- `build-parallelism` — 并行和图构建调优
- `eval-performance` — 全局和导入链优化

---

## 第1步：建立性能基线

测量三种场景以了解时间消耗在哪里：

### 冷构建（首次构建）

不存在之前的构建输出。测量包括恢复、编译和所有目标的完整端到端时间。

```bash
# 首先清理所有内容
dotnet clean
# 删除bin/obj以真正从头开始
Get-ChildItem -Recurse -Directory -Include bin,obj | Remove-Item -Recurse -Force
# 或者在Linux/macOS上：
# find . -type d \( -name bin -o -name obj \) -exec rm -rf {} +

# 测量冷构建
dotnet build /bl:cold-build.binlog -m
```

### 热构建（增量构建）

构建输出存在，一些文件已更改。测量增量构建的效果。

```bash
# 构建一次以填充输出
dotnet build -m

# 做一个小的更改（触摸一个.cs文件）
# 然后重新构建
dotnet build /bl:warm-build.binlog -m
```

### 无操作构建（未更改）

构建输出存在，没有任何更改。这应该是几乎即时的。如果它很慢，则增量构建有问题。

```bash
# 构建一次以填充输出
dotnet build -m

# 立即重新构建而不做更改
dotnet build /bl:noop-build.binlog -m
```

### 正常表现是怎样的

| 场景 | 预期行为 |
|------|----------|
| 冷构建 | 完整编译，所有目标运行。这是你的绝对基线 |
| 热构建 | 仅更改的项目重新编译。时间与更改范围成正比 |
| 无操作构建 | 小型仓库< 5秒，大型仓库< 30秒。所有编译目标应报告"跳过目标——所有输出都是最新的" |

**红旗：**
- 无操作构建 > 30秒 → 增量构建有问题（见`incremental-build`技能）
- 热构建重新编译所有内容 → 项目依赖链强制完整重建
- 冷构建恢复时间长 → NuGet缓存问题

### 记录基线

在优化之前和之后以结构化的方式记录基线：

```
| 场景    | 之前  | 之后   | 改进 |
|---------|-------|-------|-----|
| 冷构建  | 2m 15s |        |     |
| 热构建  | 1m 40s |        |     |
| 无操作构建 | 45s   |        |     |
```

---

## 第2步：工件输出布局

`UseArtifactsOutput`功能（在.NET 8中引入）更改输出目录结构以避免bin/obj冲突问题并启用更好的缓存。

### 启用工件输出

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <UseArtifactsOutput>true</UseArtifactsOutput>
</PropertyGroup>
```

### 之前与之后

```
# 传统布局（之前）
src/
  MyLib/
    bin/Debug/net8.0/MyLib.dll
    obj/Debug/net8.0/...
  MyApp/
    bin/Debug/net8.0/MyApp.dll

# 工件布局（之后）
artifacts/
  bin/MyLib/debug/MyLib.dll
  bin/MyApp/debug/MyApp.dll
  obj/MyLib/debug/...
  obj/MyApp/debug/...
```

### 优点

- **无bin/obj冲突**：每个项目+配置自动获得唯一路径
- **更容易缓存**：单一`artifacts/`目录用于CI中的缓存/恢复
- **更干净的.gitignore**：只需忽略`artifacts/`
- **多目标安全**：每个TFM获得自己的子目录

### 自定义

```xml
<!-- 更改工件根目录 -->
<PropertyGroup>
  <ArtifactsPath>$(MSBuildThisFileDirectory)output</ArtifactsPath>
</PropertyGroup>
```

---

## 第3步：确定性构建

确定性构建在给定相同输入时会产生字节对字节完全相同的输出。这对于构建缓存和可重复性至关重要。

### 启用确定性构建

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <!-- 自.NET SDK项目SDK 2.0+默认启用 -->
  <Deterministic>true</Deterministic>

  <!-- 为完全可重复性，还设置： -->
  <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
</PropertyGroup>
```

### 确定性影响的内容

- 移除PE头中的时间戳
- 在PDB中使用一致文件路径
- 对相同输入产生相同输出

### 这对性能的重要性

- **构建缓存**：如果输出是确定性的，你可以跨构建和机器缓存和重用它们
- **CI优化**：通过比较输入来跳过未更改项目的重新构建
- **分布式构建**：在共享存储中缓存编译结果安全

---

## 第4步：依赖图修剪

减少不必要的项目引用可以缩短关键路径并减少构建内容。

### 审计依赖图

```bash
# 可视化依赖图
dotnet build /bl:graph.binlog

# 在binlog中检查项目引用和构建时间
# 寻找被引用但可以修剪的项目
```

### 技术

#### 移除冗余的传递引用

```xml
<!-- BAD: Utils已经通过Core transitively引用 -->
<ItemGroup>
  <ProjectReference Include="..\Core\Core.csproj" />
  <ProjectReference Include="..\Utils\Utils.csproj" />
</ItemGroup>

<!-- GOOD: 让传递引用自动流动 -->
<ItemGroup>
  <ProjectReference Include="..\Core\Core.csproj" />
</ItemGroup>
```

#### 仅构建顺序引用

当你需要某个项目在你构建之前构建，但不需要其程序集输出时：

```xml
<!-- 仅确保构建顺序，不引用输出程序集 -->
<ProjectReference Include="..\CodeGen\CodeGen.csproj"
                  ReferenceOutputAssembly="false" />
```

#### 防止传递流动

当依赖项是内部实现细节，不应该传递给消费者时：

```xml
<!-- 不要传递这个依赖 -->
<ProjectReference Include="..\InternalHelpers\InternalHelpers.csproj"
                  PrivateAssets="all" />
```

#### 禁用传递项目引用

对于显式依赖管理（非常大的仓库的极端措施）：

```xml
<PropertyGroup>
  <DisableTransitiveProjectReferences>true</DisableTransitiveProjectReferences>
</PropertyGroup>
```

**注意**：这要求列出所有依赖项。仅在传递闭包导致过度重建的大型仓库中使用。

---

## 第5步：静态图构建（`/graph`）

静态图模式在构建之前评估整个项目图，从而实现更好的调度和隔离。

### 启用图构建

```bash
# 单次调用
dotnet build /graph

# 带二进制日志进行分析
dotnet build /graph /bl:graph-build.binlog
```

### 优点

- **更好的并行性**：MSBuild事先知道完整图并可以最佳调度
- **构建隔离**：每个项目独立构建（无跨项目状态泄漏）
- **缓存潜力**：隔离后，单个项目结果可以缓存

### 何时使用

| 场景 | 建议 |
|------|------|
| 大型多项目解决方案（20+项目） | ✅ 尝试`/graph`——可能会看到显著的并行性收益 |
| 小型解决方案（< 5项目） | ❌ 图评估开销大于收益 |
| CI构建 | ✅ 图构建更可预测且可并行化 |
| 本地开发 | ⚠️ 两者都测试——可能或不可能帮助，取决于项目结构 |

### 图构建故障排除

图构建要求所有`ProjectReference`项是静态可确定的（无动态引用在目标中计算）。如果图构建失败：

```
error MSB4260: Project reference "..." could not be resolved with static graph.
```

**修复**：确保所有`ProjectReference`项在`<ItemGroup>`中声明，在目标之外（不在`<Target>`块内动态计算）。

---

## 第6步：并行构建调优

### MaxCpuCount

```bash
# 使用所有可用核心（dotnet build默认）
dotnet build -m

# 指定显式核心数（在共享代理的CI中有用）
dotnet build -m:4

# MSBuild.exe语法
msbuild /m:8 MySolution.sln
```

### 识别并行性瓶颈

在binlog中查找：
- **长顺序链**：由于依赖关系必须一个接一个构建的项目
- **负载不均**：某些构建节点空闲时，其他节点过载
- **单个项目瓶颈**：关键路径上的一个大项目阻塞所有其他项目

使用`grep 'Target Performance Summary' -A 30 full.log`在binlog分析中查看构建节点利用率。

### 缩短关键路径

关键路径是依赖项目的最长链。要缩短它：
1. **将大项目拆分成更小的项目**，以便可以并行构建
2. **移除不必要的`ProjectReference`**（见第5步）
3. **使用`ReferenceOutputAssembly="false"`**对于仅构建顺序的依赖
4. **将共享代码移到基础库**，然后并行化消费者

---

## 第7步：其他快速见效

### 将还原与构建分开

```bash
# 在CI中，还原一次，然后无还原构建
dotnet restore
dotnet build --no-restore -m
dotnet test --no-build
```

### 跳过不必要的目标

```bash
# 跳过构建文档
dotnet build /p:GenerateDocumentationFile=false

# 开发期间跳过分析器（不用于CI！）
dotnet build /p:RunAnalyzers=false
```

### 使用项目级过滤

```bash
# 只构建你正在工作的项目（及其依赖项）
dotnet build src/MyApp/MyApp.csproj

# 如果你只需要一个项目，不要构建整个解决方案
```

### 二进制日志用于所有调查

始终从binlog开始：
```bash
dotnet build /bl:perf.binlog -m
```

然后使用`build-perf-diagnostics`技能和binlog工具进行系统化的瓶颈识别。

---

## 优化决策树

```
你的无操作构建是否慢（> 10秒/项目）？
├── 是 → 见`incremental-build`技能（修复输入/输出）
└── 否
    你的冷构建是否慢？
    ├── 是
    │   恢复是否慢？
    │   ├── 是 → 优化NuGet还原（使用锁文件，配置本地缓存）
    │   └── 否
    │       编译是否慢？
    │       ├── 是
    │       │   分析器/生成器是否慢？
    │       │   ├── 是 → 见`build-perf-diagnostics`技能
    │       │   └── 否 → 检查并行性，图构建，关键路径（本技能 + `build-parallelism`）
    │       └── 否 → 检查自定义目标（通过`build-perf-diagnostics`进行binlog分析）
    └── 否
        你的热构建是否慢？
        ├── 是 → 项目不必要地重新构建 → 检查`incremental-build`技能
        └── 否 → 构建健康！考虑图构建或UseArtifactsOutput以获得进一步收益
```
