# 用于 CLI 缓存的 MSBuild 服务器

使用 MSBuild 服务器缓存 CLI 构建的评估结果，以匹配 Visual Studio 从其长生命周期的 MSBuild 进程中获得的性能优势。

## 使用场景

- 从 CLI 进行的小型增量构建（`dotnet build`）比预期慢
- 开发人员发现同一项目的 VS 构建比 CLI 构建快
- CI 代理运行同一仓库的许多顺序构建

## 不适用场景

- 基于IDE的构建（Visual Studio 已经使用长生命周期的 MSBuild 进程）
- 冷启动开销可接受的单独构建
- 疑似构建正确性问题（禁用服务器以隔离问题）

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| Shell 上下文 | 否 | 将环境变量设置在哪个 shell 中（bash、PowerShell 或 Windows 持久化） |

## 工作流

### 第 1 步：确认 CLI 上下文

验证开发人员是从命令行构建（`dotnet build`），而不是从 Visual Studio 或其他 IDE 构建。MSBuild 服务器在 IDE 内部无法提供任何好处。

### 第 2 步：设置环境变量

```bash
# Bash / CI
export MSBUILDUSESERVER=1

# PowerShell
$env:MSBUILDUSESERVER = "1"

# Windows (持久化)
setx MSBUILDUSESERVER 1
```

### 第 3 步：验证改进

运行同一项目的两次顺序构建并比较时间：

1. 第一次构建（冷启动）：`dotnet build` -- 服务器启动，无缓存优势
2. 第二次构建（热启动）：`dotnet build` -- 应该明显更快

最明显的改进体现在包含许多项目或复杂的 `Directory.Build.props` 链的仓库中。

## 验证

- [ ] `MSBUILDUSESERVER=1` 已在 shell 中设置
- [ ] 第二次顺序构建比第一次快
- [ ] 运行 `dotnet build-server shutdown` 后再重建可确认服务器干净重启

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 期望在 Visual Studio 中改进 | VS 已经使用长生命周期的 MSBuild 节点；服务器不会提供额外好处 |
| 启用后出现构建正确性问题 | 运行 `dotnet build-server shutdown` 重置；如果问题仍然存在，禁用服务器 |
| 服务器进程使用意外内存 | 服务器在后台持久化；空闲时使用 `dotnet build-server shutdown` 关闭 |
