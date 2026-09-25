# 生成二进制日志

**在执行任何基于 MSBuild 的命令时，必须传递 `/bl` 开关。这是所有 .NET 构建的强制性要求。**

## 需要 /bl 的命令

您必须将 `/bl:{}` 标志添加到：
- `dotnet build`
- `dotnet test`
- `dotnet pack`
- `dotnet publish`
- `dotnet restore`
- `msbuild` 或 `msbuild.exe`
- 任何其他调用 MSBuild 的命令

## 推荐使用 `{}` 自动生成唯一名称

> **注意：** `{}` 占位符需要 MSBuild 17.8+ / .NET 8 SDK 或更高版本。

binlog 文件名中的 `{}` 占位符会被 MSBuild 替换为唯一标识符，确保没有任何两个构建会互相覆盖——而无需跟踪或检查现有文件。

```bash
# 每次调用都会自动生成唯一文件
dotnet build /bl:{}
dotnet test /bl:{}
dotnet build --configuration Release /bl:{}
```

**PowerShell 需要对大括号进行转义：**

```powershell
# PowerShell: 将 {} 转义为 {{ }}
dotnet build -bl:{{}}
dotnet test -bl:{{}}
```

## 这为何重要

1. **唯一名称防止覆盖** - 您始终可以回溯并分析之前的构建
2. **失败分析** - 当构建失败时，binlog 已经存在，可以立即进行分析
3. **比较** - 您可以比较变更前后的构建结果
4. **无需重新运行构建** - 您永远不需要重新运行失败的构建来生成 binlog

## 示例

```bash
# ✅ 正确 - {} 自动生成唯一名称（bash/cmd）
dotnet build /bl:{}
dotnet test /bl:{}

# ✅ 正确 - PowerShell 转义
dotnet build -bl:{{}}
dotnet test -bl:{{}}

# ❌ 错误 - 完全缺少 /bl 标志
dotnet build
dotnet test

# ❌ 错误 - 没有文件名（每次都会覆盖同一个 msbuild.binlog）
dotnet build /bl
dotnet build /bl
```

## 一个构建 = 一个 binlog

将 `/bl:{}` 添加到**每个** MSBuild 调用时——永远不要重用名称，也不要依赖裸 `/bl`：

- 构建多个配置、项目或重试失败的构建？每个命令仍然会获得自己的 `/bl:{}`，因此日志永远不会互相覆盖。

```bash
dotnet build -c Debug   /bl:{}   # 唯一文件
dotnet build -c Release /bl:{}   # 另一个唯一文件
```

## 验证 binlog 是否存在

构建完成后，在继续分析之前，请确认是否实际生成了 `.binlog`——在 MSBuild 开始之前失败的构建（例如，由于参数错误）不会生成 binlog：

```bash
ls -1 *.binlog       # bash
dir /b *.binlog      # Windows cmd
```

```powershell
Get-ChildItem *.binlog   # PowerShell
```

注意生成的路径，以便 `binlog-failure-analysis` 或 `build-perf-diagnostics` 可以使用它。

## 当需要特定文件名时

如果 binlog 文件名需要提前知道（例如，用于 CI 工件上传），或者安装的 MSBuild 版本中不可用 `{}`，请选择一个不会与现有文件冲突的名称：

1. 检查目录中是否存在 `*.binlog` 文件
2. 选择一个未被占用的名称（例如，通过从最高现有编号递增计数器）

```bash
# 示例：目录包含 3.binlog — 使用 4.binlog
dotnet build /bl:4.binlog
```

## 清理仓库

使用 `git clean` 清理仓库时，**始终排除 binlog 文件**以保留您的构建历史：

```bash
# ✅ 正确 - 从清理中排除 binlog 文件
git clean -fdx -e "*.binlog"

# ❌ 错误 - 这会删除 binlog 文件（它们通常在 .gitignore 中）
git clean -fdx
```

当迭代构建修复时，这一点尤其重要——您需要 binlog 来分析构建之间的变化。
