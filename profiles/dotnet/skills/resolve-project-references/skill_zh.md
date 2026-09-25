# 虚假 ResolveProjectReferences 时间

通过解释其报告的时间是墙上时间（wall-clock wait time），而不是 CPU 工作时间，来防止对 `ResolveProjectReferences` 的误导性优化。

## 使用场景

- `ResolveProjectReferences` 在目标性能摘要（Target Performance Summary）中显示为最昂贵的目标
- 开发人员尝试直接优化 `ResolveProjectReferences`
- 构建性能分析显示单个目标消耗了 50-80% 的总构建时间

## 不适用场景

- 一般构建性能优化（应使用 `build-perf-diagnostics`）
- 瓶颈明显是其他目标（例如，`Csc`、`ResolveAssemblyReference`）
- 用户尚未捕获 binlog 或性能摘要

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 构建日志或 binlog | 是 | 包含目标性能摘要的诊断构建日志或 binlog |

## 工作流程

### 第 1 步：确认虚假症状

验证 `ResolveProjectReferences` 是否在 **目标** 性能摘要中显示为顶级目标。这是虚假的指标。

### 第 2 步：解释为什么它是虚假的

报告的时间包括 **等待依赖项目构建** 的时间，而 MSBuild 节点处于让出状态（参见 dotnet/msbuild#3135）。在此等待期间，节点可能正在其他项目上执行有用的工作。该目标本身几乎不做工作。

### 第 3 步：重定向到任务自时间

使用 **任务** 性能摘要来识别真正的瓶颈。

#### 主要：binlog MCP（首选）

使用 **binlog MCP 服务器** 的 `expensive_tasks` 工具直接从 binlog 获取任务自时间排名。

#### 备用：文本日志重放（当 MCP 不可用时）

```bash
dotnet msbuild build.binlog -noconlog -fl "-flp:v=diag;logfile=full.log;performancesummary"
grep "Task Performance Summary" -A 50 full.log
```

关注实际任务的自时间：

- **Csc**：参见 `build-perf-diagnostics` 技巧（第 2 节：Roslyn 分析器）
- **ResolveAssemblyReference**：参见 `build-perf-diagnostics` 技巧（第 1 节：RAR）
- **Copy**：参见 `build-perf-diagnostics` 技巧（第 4 节：文件 I/O）
- **序列化瓶颈**：参见 `build-parallelism` 技巧

## 验证

- [ ] 使用了任务性能摘要而不是目标性能摘要
- [ ] 未将 `ResolveProjectReferences` 设置为优化目标
- [ ] 识别了具体任务（例如，`Csc`、`Copy`、`ResolveAssemblyReference`）作为真正的瓶颈
