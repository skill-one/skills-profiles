---
name: profilecli-insights
description: 使用 profilecli 查询 Pyroscope 的实时性能分析文件，使用 pprof 对其进行分析，并将热点函数与已检出的源代码进行关联。当用户需要调查已配置了 Pyroscope 服务器、profilecli 和 pprof 的服务时使用。
---

# Profilecli Insights

你是一个性能分析助手。使用 `profilecli` 查询远程的 Pyroscope 持续分析服务器，然后将分析结果与当前仓库中的源代码进行关联，以提供可操作的洞察。

按以下步骤依次操作。不要跳过步骤。

## 第 1 步：确保 profilecli 可用

检查 `profilecli` 是否在 PATH 中：

```bash
profilecli --version
```

如果未找到，请指示用户从 `https://github.com/grafana/pyroscope/releases/latest/download/` 下载。

选择用于后续所有分析命令：

```bash
if command -v pprof >/dev/null 2>&1; then
  PPROF=(pprof)
else
  PPROF=(go tool pprof)
fi
```

## 第 2 步：验证连接和数据是否存在

运行一系列查询以验证连接并发现分析类型：

```bash
profilecli query series --label-names=__profile_type__ --output json
```

如果成功，解析 JSON 输出并保留可用的 `__profile_type__` 值。常见类型包括：

- `process_cpu:cpu:nanoseconds:cpu:nanoseconds`（CPU）
- `memory:alloc_space:bytes:space:bytes`（内存分配）
- `memory:inuse_space:bytes:space:bytes`（内存使用）
- `goroutine:goroutine:count:goroutine:count`（goroutine）
- `mutex:contentions:count:contentions:count`（互斥锁争用）
- `block:contentions:count:contentions:count`（阻塞争用）

你需要在第 4 步中使用这些分析类型。

如果查询失败，帮助用户配置连接：

- 在端口 `4040` 上运行本地 Pyroscope 服务器。
- 或者使用服务账户令牌连接到 Grafana。

`PROFILECLI_URL` 是必需的。将其设置为 Pyroscope 服务器 URL，例如 `http://localhost:4040`，或者在使用 `PROFILECLI_TOKEN` 时设置为 Grafana 数据源代理 URL，例如 `https://my-grafana.example.com/api/datasources/proxy/uid/<datasource-uid>`。

`PROFILECLI_TOKEN` 对于 Grafana Cloud 是必需的。它必须是一个 `glsa_...` 格式的 Grafana 服务账户令牌，具有 Viewer 角色。`PROFILECLI_TENANT_ID` 对于多租户设置是可选的。

然后停止并等待用户配置环境，并等待初始查询成功。

## 第 3 步：发现服务

列出可用服务并找到与已检出的仓库相关联的服务：

```bash
profilecli query series --query '{}' --label-names service_repository --label-names service_name --output json
```

解析 JSON 输出中的 `service_name` 和 `service_repository`。比较 `service_repository` 与 `git remote get-url origin`；匹配的服务最相关。将用户的问题与一个或多个服务名称进行匹配。

如果问题不能明确映射到某个服务，请显示可用服务，突出显示仓库匹配，并询问用户要分析哪个服务。

## 第 4 步：查询相关分析类型

使用第 2 步中发现的适当类型查询目标服务。查询必须是有效的 ProfileQL 标签选择器。

```bash
PROFILE="$(mktemp -t profilecli-insights)"

profilecli query profile \
  --query '<QUERY>' \
  --profile-type <PROFILE_TYPE> \
  --from now-1h --to now \
  --output "pprof=${PROFILE}" -f
```

如果输出为空，将范围扩展到 `--from now-6h` 或 `--from now-24h`。

分析生成的分析文件：

```bash
"${PPROF[@]}" -lines -top -cum "${PROFILE}"
```

## 第 5 步：识别热点函数

提取具有最多扁平样本和累积样本的函数。突出显示：

- 高扁平时间，这可以识别自时间。
- 高累积时间，这包括被调用者。
- 显著的运行时和标准库函数：`runtime.mallocgc` 暗示分配压力，`runtime.futex` 或 `runtime.lock` 暗示锁争用，`runtime.gcBgMarkWorker` 或 `runtime.gcDrain` 暗示 GC 压力，`compress/gzip` 或 `compress/flate` 暗示压缩开销。

## 第 6 步：将热点函数映射到源代码

`pprof -lines -top -cum` 输出以以下格式列出函数：

```
<flat> <flat%> <sum%> <cum> <cum%>  <function-name> <source-file>:<line>
```

例如：

```
1859.03s 23.50%  ...  github.com/grafana/pyroscope/pkg/distributor.(*Distributor).PushBatch.func1 github.com/grafana/pyroscope/pkg/distributor/distributor.go:380
```

使用函数名后的源路径将分析帧与当前检出的内容关联：

1. 将选定服务的 `service_repository` 规范化为模块前缀：移除 URL 方案、任何 SSH 用户和主机分隔符以及尾随的 `.git`。例如，`https://github.com/grafana/pyroscope.git` 变为 `github.com/grafana/pyroscope`。
2. 以该模块前缀开头的帧，且不带 `@version` 后缀，很可能在此仓库中。第三方 Go 依赖项通常在其模块路径中包含 `@v...`。
3. 从仓库中的帧中移除模块前缀以获取相对路径。例如，`github.com/grafana/pyroscope/pkg/distributor/distributor.go:380` 变为 `pkg/distributor/distributor.go` 在第 380 行。
4. 如果 pprof 构建 ID 包含 JSON 并具有 `git_ref`，将其与 `git log --oneline -1` 进行比较。如果它们不同，警告说行号可能已过时。使用 `git log --oneline <git_ref>..HEAD -- <file>` 查看映射的文件是否已更改。如果构建 ID 没有包含 `git_ref`，则注意无法验证源对齐。
5. 读取报告的源行前后约 20 行。从完全限定的函数名中提取相关的方法或函数。

对于重要的第三方或运行时函数，即使无法从当前检出中读取源代码，也要报告其可能的影响。

## 第 7 步：交付分析

以以下部分呈现结构化报告：

### 摘要

给出对分析的简短（两到三句话）概述。

### 热点函数排名

提供一个包含函数名、扁平样本百分比和累积样本百分比、仓库函数的源文件和行号以及简要描述的排名表。

### 源代码分析

对于每个热点仓库函数，显示相关的源代码片段，解释为什么它可能是热点，并提出具体的优化建议，例如减少分配、缓存结果、使用 `sync.Pool` 或减少锁争用。

### 建议

按预期影响顺序列出可操作的优化建议。

## 错误处理

- 如果 `profilecli` 缺失，请将用户引导至 `https://github.com/grafana/pyroscope/releases/latest`。
- 对于连接错误，验证 `PROFILECLI_URL` 和网络访问。
- 对于 `401` 或 `403` 错误，验证 `PROFILECLI_TOKEN` 和 `PROFILECLI_TENANT_ID`。
- 对于空结果，扩展时间范围并验证服务（使用 `query series`）。
- 如果找不到服务，列出可用服务并询问用户选择一个。
