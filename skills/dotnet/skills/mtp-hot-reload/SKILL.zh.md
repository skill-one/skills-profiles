---
name: mtp-hot-reload
description: 为 Microsoft Testing Platform 项目中的长期存在的控制台主机编辑/重新运行循环设置或恢复 MTP 热重载。用于显式的 MTP 控制台请求，例如“启用热重载”、“dotnet run 以编辑后重新运行”，或不受支持/粗鲁的编辑。涵盖设置、运行/监视、重启、过滤器以及 VSTest 无变更回退。对于一次性运行、精确命令、过滤器错误、TRX/转储，或仅仅是失败的测试，请使用 run-tests。当 Test Explorer 或 IDE 应在不使用 MTP 控制台主机的情况下重新运行测试时，请勿使用。不包括编辑器集成、持续集成以及测试的编写/调试。
---

# MTP 热重载用于迭代测试修复

设置并使用一个长生命周期的 Microsoft 测试平台主机，应用代码编辑并自动重新运行测试。

## 何时使用

- 用户明确要求测试热重载
- 用户希望主机保持运行并在重复编辑后自动重新运行
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

- 如果设置已经完成，并且用户只询问要使用哪个命令，
  返回一个 `dotnet run --project <path>` 命令和一个说明它启动持久主机的句子。不要重复包、启动配置或粗鲁编辑指导。
- 如果包已经安装，只显示剩余的启用和运行步骤。不要建议重新安装它或添加可选的持久化/恢复路径，除非请求。
- 对于命名测试，识别框架并返回一个可运行的命令，使用该框架的过滤器语法。永远不要用 MSTest/NUnit `--filter` 替换 xUnit v3 `--filter-method` 或 TUnit `--treenode-filter`。
- 直接启动的 MTP 主机本身就是持久的监视器：`dotnet run` 保持活动状态，热重载扩展对编辑做出反应。不要用 `dotnet watch run` 替换正常的 MTP 路径；保留 `dotnet watch` 用于下面的显式重启回退。

## 工作流程

### 第 1 步：在更改任何内容之前检测平台

热重载需要 MTP。它**不**与 VSTest 一起工作。

遵循 `platform-detection` 技能中的完整评估属性程序。读取导入的属性和包版本以及项目文件。在安装包、编辑文件或返回 MTP 启动命令之前执行此操作。

**VSTest 停止点：** 报告项目配置为不可用 MTP 热重载，并停止 MTP 设置路径。不要安装扩展、创建 `launchSettings.json`、设置环境变量、更改运行器属性/包或返回 `dotnet run` 热重载命令。永远不要将设置请求转换为隐式的 VSTest 到 MTP 迁移。

提供一个有效的非 MTP 回退方案以保留项目：

```shell
dotnet watch --project <project-path> test
```

当文件更改时，这将重新构建并重新运行现有的 VSTest 项目；它不是 MTP 热重载。作为单独的选项提供显式迁移，但除非用户请求，否则不要执行。精确的一次性测试命令仍然属于 `run-tests`。

### 第 2 步：添加热重载 NuGet 包

首先检查有效的包引用。如果 `Microsoft.Testing.Extensions.HotReload` 已经安装，保留其版本并跳过此步骤。否则安装它：

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

要过滤到特定失败的测试，在 `--` 后传递过滤器。语法取决于测试框架——有关完整详细信息，请参阅 `filter-syntax` 技能。快速示例：

| 框架 | 过滤器语法 |
|-------|--------------|
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

#### 不支持的编辑和粗鲁编辑

方法签名更改、新类型和其他不支持的编辑不能应用于活动进程。永远不要暗示陈旧的主持人已经捕获它们。

对于直接启动的 MTP 主机：

1. 保留启动当前主机时使用的确切命令、配置、环境、过滤器和参数。
2. 使用 `Ctrl+C` 停止它。
3. 重新构建相同的项目：`dotnet build <project-path>`。
4. 重新运行**相同的原始主机命令**。不要用通用的 `dotnet run` 命令替换一个未知的现有调用。

如果预期重复不支持的编辑，提供 `watch` 管理的重启回退：

```shell
# PowerShell
$env:TESTINGPLATFORM_HOTRELOAD_ENABLED = "1"
$env:DOTNET_WATCH_RESTART_ON_RUDE_EDIT = "1"
dotnet watch --project <project-path> run -- <existing-MTP-arguments>
```

`dotnet watch` 在无法应用粗鲁编辑时重新启动进程。如果没有自动重启变量，接受重启提示或按 `Ctrl+R`。在 `--` 后保留任何现有的测试过滤器。
`DOTNET_WATCH_RESTART_ON_RUDE_EDIT` 是 .NET SDK 文档中记录的开关，不是 MTP 扩展设置。当正确性可能受到质疑时，引用 `dotnet watch` 文档并说明它使监视器重新启动而不是提示。
永远不要省略原始过滤器或用请求的 `watch` 管理回退替换一次性 `dotnet run`。

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
- [ ] 代码更改被捕获而无需手动重启

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|----------|
| 使用 `dotnet test` 而不是 `dotnet run` | 热重载需要 `dotnet run --project <path>` 直接在控制台模式下运行测试主机 |
| 项目使用 VSTest，而不是 MTP | 不要修改它。提供 `dotnet watch --project <path> test` 作为重建/重新运行回退或单独的显式迁移 |
| 忘记设置环境变量 | 在运行之前设置 `TESTINGPLATFORM_HOTRELOAD_ENABLED=1` |
| 期望测试资源管理器集成 | 控制台模式仅支持——没有 VS/VS Code 测试资源管理器支持 |
| 进行不支持的代码更改（粗鲁编辑） | 停止、重新构建并重新运行相同的主持人调用，或使用 `dotnet watch` 与粗鲁编辑重启行为 |
