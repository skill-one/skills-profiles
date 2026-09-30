---
name: helmor-cli
description: 使用 Helmor CLI 从终端远程控制 Helmor。当用户需要检查 Helmor 数据/设置、管理仓库/工作区/会话/文件、向代理发送提示、列出模型、使用 GitHub 集成、检查脚本、以 MCP 服务器方式运行 Helmor、生成 shell 补全、退出正在运行的应用、检查/安装/更新 Helmor CLI Beta、通过 Beta 应用流程安装/更新 Helmor 技能，或需要 Helmor 命令参考时使用。此外，还可以规划和构建一个大型变更，将其作为一系列依赖的 PR 堆栈 (`/helmor-cli stack`)，将已编写好的变更拆分为堆栈 (`/helmor-cli break`)，以及在较低层变更或合并后重新同步堆栈 (`/helmor-cli restack`)。
---

# Helmor CLI

使用此技能来引导以终端为主的简单 Helmor 工作流。保持答案实用：优先选择一到两个具体的命令，而不是一个冗长的 CLI 教程。

## 命令路由

通过 `/helmor-cli` 后面的第一个单词进行路由：

- `restack` — 在较低层发生变化或合并后重新同步 PR 堆栈。参考 `references/restack.md`。（这是作曲家的 **Restack** 按钮发送的内容。）
- `stack` — 将一个大的变更计划并构建为一堆依赖的 PR。参考 `references/stacked-pr.md`。
- `break` — 将您已经在当前工作区中编写的变更拆分为一堆较小的依赖的 PR，并在首先确认切片粒度后进行确认。参考 `references/break.md`。
- 其他任何内容（或无参数） — 一个普通的 Helmor CLI 任务；使用下面的二进制名称指导和命令参考。

## 二进制名称（发布版本与开发版本）

以下示例使用字面量名称 `helmor` — 发布用户在其 PATH 上的二进制文件。

- **发布版本构建**：以 `helmor <子命令>` 的形式调用命令。
- **开发版本构建**：不要假设 `helmor-dev` 在 PATH 上。在 Helmor 的工作树式开发工作流中，每个工作树都有自己的 `target/debug/helmor-cli`，而共享的 `/usr/local/bin/helmor-dev` 符号链接（如果存在）只能指向其中一个。相反：
  - 如果您是运行在 Helmor 内部的 **代理**，系统提示已经为您提供了确切的 CLI 调用（通常是一个绝对路径，如 `<worktree>/src-tauri/target/debug/helmor-cli>`）。直接调用它——不要用 `which` / `file` / `--version` 重新验证。
  - 如果您是终端前的 **人类用户**，运行 `<your-worktree>/src-tauri/target/debug/helmor-cli <子命令>`（或您的活跃 Helmor 构建的任何路径）。

无论构建版本如何，每个命令的其余部分都是相同的。

## 初步检查

1.  检查 CLI 是否已安装以及它针对哪种数据模式：

```bash
helmor cli-status
```

2.  检查活动数据目录和数据库：

```bash
helmor data
```

当输出将被脚本或另一个工具解析时，使用 `--json`。

## CLI 安装与更新

将 Helmor CLI 安装/更新视为 Beta 版。

- 优先使用 Helmor 桌面的 onboarding/设置 Components 面板来安装或修复管理的 CLI 入口点。
- 使用 `helmor cli-status` 来验证 PATH 入口点是否指向当前应用程序管理的 CLI。
- 除非它存在于 `helmor --help` 或子命令帮助页面中，否则不要编造一个稳定的独立安装/更新命令。
- 如果用户遇到问题，请让他们运行 `helmor cli-status` 并共享输出，或者在 Helmor 仓库内检查应用程序的 Components 面板。

## Helmor 技能安装与更新

将 Helmor 技能安装/更新视为 Beta 应用程序管理流程。

- 优先使用 Helmor 桌面的 onboarding/设置 Components 面板来安装或更新捆绑的 Helmor 技能。
- 不要编造 `helmor skills` 命令；顶级 CLI 帮助目前没有暴露它。
- 如果用户要求在仓库内更新捆绑的 Helmor 技能，直接编辑技能文件并使用技能验证工具进行验证。
- 保持用户界面的技能内容简洁，并优先使用英语，除非用户明确要求其他语言。

## 常见任务

### 管理仓库和工作区

使用这些命令组进行本地优先的项目设置和工作区编排：

```bash
helmor repo --help
helmor workspace --help
```

创建工作区时，优先使用明确的仓库名称和简洁的目的标签：

```bash
helmor workspace new --repo helmor
```

### 检查会话和文件

使用会话进行对话历史记录，使用文件进行编辑器表面操作：

```bash
helmor session --help
helmor files --help
```

### 向代理发送提示

当用户希望从终端派发工作时，使用 `send`：

```bash
helmor send --help
```

优先使用 JSON 输出进行自动化：

```bash
helmor --json send --help
```

### 集成和本地工具

使用相关命令组：

```bash
helmor github --help
helmor scripts --help
helmor models --help
```

### MCP 服务器

通过 stdio 以 MCP 服务器方式运行 Helmor：

```bash
helmor mcp
```

当另一个代理/运行时需要通过模型上下文协议调用 Helmor 时，使用此命令。

## 命令参考

当您需要完整的顶级 `helmor --help` 命令列表时，请阅读 `references/helmor-help.md`。

对于命令组的精确标志，请运行组的帮助而不是猜测：

```bash
helmor <命令> --help
```
