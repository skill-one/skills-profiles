# 使用二进制日志分析 MSBuild 失败

这项技能通过 `.binlog` 文件诊断 MSBuild 构建失败。首选路径使用 **二进制日志 MCP 服务器** (`Microsoft.AITools.BinlogMcp`)，该服务器在 `binlog` MCP 命名空间下提供，并随此插件捆绑。如果 MCP 服务器不可用，则回退到底部的 **二进制日志重放** 工作流。

## 主要工作流 — MCP

MCP 服务器提供结构化工具，用于在不解析文本日志的情况下检查 `.binlog`。直接调用这些工具，而不是将二进制日志重放到文本文件。如果您不确定有哪些工具可用，请首先调用 `tools/list`。

**重要约束：**
- `.binlog` 文件是 **二进制格式** — 请勿尝试 `cat`、`head`、`strings` 或直接读取它。仅使用 MCP 工具查询它。
- **原始源/项目文件可能存在也可能不存在于磁盘上**。项目文件 (.csproj、.props、.targets、App.config 等) - 如果您在磁盘上找不到它们，只能通过 MCP 工具从二进制日志中读取（例如，嵌入的源文件检索）。
- **边进行边综合分析结果**。不要花费所有可用时间进行调查 — 一旦您有足够的证据，就呈现您的结论。带有清晰推理的部分答案比在调查中途超时更好。

使用可用的 MCP 服务器工具查询二进制日志，以获取：
- 构建错误和警告
- MSBuild 属性及其值
- MSBuild 项目（PackageReference、ProjectReference 等）
- 项目评估数据
- 目标执行细节
- 嵌入在 binlog 中的文件内容

## 回退工作流 — 文本日志重放（当 MCP 不可用时）

仅在无法启动 MCP 服务器时使用（例如，在较旧的 SDK 或离线环境中）。

### 将二进制日志重放到文本日志

```bash
dotnet msbuild build.binlog -noconlog \
  -fl  -flp:v=diag;logfile=full.log;performancesummary \
  -fl1 -flp1:errorsonly;logfile=errors.log \
  -fl2 -flp2:warningsonly;logfile=warnings.log
```

> **PowerShell 注意：** 使用 `-flp:"v=diag;logfile=full.log;performancesummary"`（带引号的分号）。

### 搜索文本日志

```bash
cat errors.log
grep -n -B2 -A2 "CS0246" full.log
grep -i "CoreCompile.*FAILED\|Build FAILED\|error MSB" full.log
grep 'Target "CoreCompile"' full.log | grep -oP 'project "[^"]*"'
```

## 生成二进制日志（仅当不存在时）

```bash
dotnet build /bl:build.binlog
```
