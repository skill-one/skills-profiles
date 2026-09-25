# MTP 热重载用于迭代测试修复

设置并使用一个长生命周期的 Microsoft 测试平台主机，应用代码编辑并自动重新运行测试。

## 何时使用

- 用户明确要求测试热重载
- 用户需要一个主机保持运行并在重复编辑后自动重新运行
- 用户需要在他们的项目中设置 MTP 热重载

## 何时不使用

- 用户需要从头开始编写新测试（使用通用编码辅助功能）
- 用户需要诊断测试失败的原因（使用诊断技能）
- 用户询问 Visual Studio 或 VS Code 测试资源管理器热重载或 IDE 集成的重新运行体验（不同的功能，不是 MTP 控制台主机热重载）
- 用户询问编辑器是否可以在不使用 MTP 控制台主机的情况下在源编辑后自动重新运行受影响的测试
- 用户希望进行一次正常运行而不重新构建（使用 `run-tests`）
- 用户需要 CI/CD 管道配置

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 测试项目路径 | 否 | 测试项目 (.csproj) 的路径。默认为当前目录。 |
| 失败的测试名称或过滤器 | 否 | 要迭代的特定测试 |

## 响应调整大小

- 如果设置已完成，并且用户仅询问要使用哪个命令，则返回一个 `dotnet run --project <path>` 命令，并附带一句说明它启动了持久化主机。不要重复包、启动配置或粗略编辑指导。
- 如果包已安装，仅显示剩余的启用和运行步骤。不要建议重新安装它或添加可选的持久化/恢复路径，除非有要求。
- 对于命名测试，识别框架并返回一个可运行的命令，使用该框架的过滤器语法。永远不要用 MSTest/NUnit `--filter` 替换 xUnit v3 `--filter-method` 或 TUnit `--treenode-filter`。
- 直接启动的 MTP 主机本身就是持久的监视器：`dotnet run` 保持活动状态，热重载扩展会响应编辑。不要用 `dotnet watch run` 替换正常的 MTP 路径；保留 `dotnet watch` 用于以下明确的重新启动回退。

## 工作流程

### 第 1 步：在更改任何内容之前检测平台

热重载需要 MTP。它**不**与 VSTest 一起工作。

遵循 `platform-detection` 技能中的完整评估属性过程。读取导入的属性和包版本以及项目文件。在安装包、编辑文件或返回 MTP 启动命令之前执行此操作。

**VSTest 停止点：** 报告项目配置下 MTP 热重载不可用，并停止 MTP 设置路径。不要安装扩展、创建 `launchSettings.json`、设置环境变量、更改运行器属性/包或返回 `dotnet run` 热重载命令。永远不要将设置请求转换为隐式的 VSTest 到 MTP 迁移。

提供一个有效的非 MTP 回退方案以保留项目：

```shell
dotnet watch --project <project-path> test
```

当文件更改时，这将重建并重新运行现有的 VSTest 项目；它不是 MTP 热重载。作为单独的选项提供明确的迁移，但除非用户要求，否则不要执行。精确的单次测试命令仍然属于 `run-tests`。

### 第 2 步：添加热重载 NuGet 包

首先检查有效的包引用。如果 `Microsoft.Testing.Extensions.HotReload` 已安装，保留其版本并跳过此步骤。否则安装它：

```shell
dotnet add <project-path> package Microsoft.Testing.Extensions.HotReload
```

> **注意**：当使用 `Microsoft.Testing.Platform.MSBuild`（由 MSTest、NUnit 和 xUnit 运行器传递包含）时，扩展在您安装其 NuGet 包时自动注册——无需代码更改。

### 第 3 步：启用热重载

热重载通过将 `TESTINGPLATFORM_HOTRELOAD_ENABLED` 环境变量设置为 `1` 来激活。

**选项 A——在运行测试之前在 shell 中设置它：**

```shell
# PowerShell
$env:TESTINGPLATFORM_HOTRELOAD_ENABLED = "1"

# bash/zsh
export TESTINGPLATFORM_HOTRELOAD_ENABLED=1
```

**选项 B——将其添加到 `launchSettings.json`（推荐用于可重复使用）：**

在测试项目中创建或更新 `Properties/launchSettings.json`：

```json
{
  "profiles": {
    "<ProjectName>": {
      "commandName": "Project",
      "environmentVariables": {
        "TESTINGPLATFORM_HOTRELOAD_ENABLED": "1"
      }
    }
  }
}
```

### 第 4 步：使用热重载运行测试

直接运行测试项目（而不是通过 `dotnet test`）以在控制台模式下使用热重载：

```shell
dotnet run --project <project-path>
```

要过滤到特定失败的测试，在 `--` 后传递过滤器。语法取决于测试框架——有关详细信息，请参阅 `filter-syntax` 技能。快速示例：

| 框架 | 过滤语法 |
|-------|----------|
| MSTest | `dotnet run --project <path> -- --filter "FullyQualifiedName~TestMethodName"` |
| NUnit | `dotnet run --project <path> -- --filter "FullyQualifiedName~TestMethodName"` |
| xUnit v3 | `dotnet run --project <path> -- --filter-method "*TestMethodName"` |
| TUnit | `dotnet run --project <path> -- --treenode-filter "/*/*/ClassName/TestMethodName"` |

测试主机将启动，运行测试，并**保持活动状态**等待代码更改。

### 第 5 步：迭代修复

1. 在编辑器中编辑源代码（测试代码或生产代码）
2. 测试主机检测到更改并自动重新运行受影响的测试
3. 在控制台中查看更新后的结果
4. 重复直到所有目标测试通过

> **重要**：热重载目前仅在**控制台模式下**工作。Visual Studio 或 Visual Studio Code 的测试资源管理器中没有热重载支持。

#### 不支持的编辑和粗略编辑

方法签名更改、新类型和其他不支持的编辑不能应用于活动进程。永远不要暗示陈旧的主机已经捕获了它们。

对于直接启动的 MTP 主机：

1. 保留启动当前主机时使用的确切命令、配置、环境、过滤器和参数。
2. 使用 `Ctrl+C` 停止它。
3. 重建相同的项目：`dotnet build <project-path>`。
4. 重新运行**相同的原始主机命令**。不要用通用的 `dotnet run` 命令替换一个未知的现有调用。

如果预期有重复的不支持的编辑，提供由监视管理的重新启动回退：

```shell
# PowerShell
$env:TESTINGPLATFORM_HOTRELOAD_ENABLED = "1"
$env:DOTNET_WATCH_RESTART_ON_RUDE_EDIT = "1"
dotnet watch --project <project-path> run -- <existing-MTP-arguments>
```

`dotnet watch` 在无法应用粗略编辑时重新启动进程。如果没有自动重新启动变量，接受重新启动提示或按 `Ctrl+R`。在 `--` 后保留任何现有的测试过滤器。
`DOTNET_WATCH_RESTART_ON_RUDE_EDIT` 是一个记录在案的 .NET SDK 开关，而不是 MTP 扩展设置。当正确性可能受到质疑时，引用 `dotnet watch` 文档并说明它使监视器重新启动而不是提示。
永远不要省略原始过滤器或用一次性的 `dotnet run` 替换请求的监视管理回退。

### 第 6 步：完成

一旦所有测试通过：

1. 停止测试主机（Ctrl+C）
2. 当用户请求精确的一次性验证命令、标志、过滤器、TRX 或转储时，使用 `run-tests`
3. 可选地从环境中删除 `TESTINGPLATFORM_HOTRELOAD_ENABLED` 或保留 `launchSettings.json` 以供将来使用

## 验证

- [ ] 项目使用 Microsoft 测试平台（不是 VSTest）
- [ ] `Microsoft.Testing.Extensions.HotReload` 包已安装
- [ ] `TESTINGPLATFORM_HOTRELOAD_ENABLED` 环境变量设置为 `1`
- [ ] 测试运行，主机保持活动状态等待更改
- [ ] 代码更改被捕获而无需手动重新启动

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|----------|
| 使用 `dotnet test` 而不是 `dotnet run` | 热重载需要 `dotnet run --project <path>` 直接在控制台模式下运行测试主机 |
| 项目使用 VSTest，而不是 MTP | 不要修改它。提供 `dotnet watch --project <path> test` 作为重建/重新运行的回退或作为单独的明确迁移 |
| 忘记设置环境变量 | 在运行前设置 `TESTINGPLATFORM_HOTRELOAD_ENABLED=1` |
| 期望测试资源管理器集成 | 仅控制台模式——没有 VS/VS Code 测试资源管理器支持 |
| 进行不支持的代码更改（粗略编辑） | 停止、重建并重新运行相同的**主机调用**，或使用具有粗略编辑重启动行为的 `dotnet watch` |
