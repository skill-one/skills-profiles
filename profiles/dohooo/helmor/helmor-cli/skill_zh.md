# Helmor CLI

使用此技能来引导以终端为主的简单 Helmor 工作流。保持答案实用：优先选择一到两个具体的命令，而不是一个冗长的 CLI 教程。

## 命令路由

通过 `/helmor-cli` 后面的第一个单词进行路由：

- `restack` — 在较低层发生变化或合并后重新同步 PR 堆栈。参考 `references/restack.md`。（这是作曲家的 **Restack** 按钮发送的内容。）
- `stack` — 将一个大的变更作为一个依赖的 PR 堆栈来计划和构建。参考 `references/stacked-pr.md`。
- `break` — 将当前工作区中已经编写的变更拆分为一个较小的依赖的 PR 堆栈，并在用户确认切片粒度之前进行拆分。参考 `references/break.md`。
- 其他任何内容（或无参数） — 一个普通的 Helmor CLI 任务；使用下面的二进制名称指导和命令参考。

## 二进制名称（发布版本与开发版本）

以下示例使用字面名称 `helmor` — 发布用户在他们的 PATH 上的二进制文件。

- **发布版本构建**：以 `helmor <子命令>` 的形式调用命令。
- **开发版本构建**：不要假设 `helmor-dev` 在 PATH 上。在 Helmor 的基于工作区的开发工作流中，每个工作区都有自己的 `target/debug/helmor-cli`，并且共享的 `/usr/local/bin/helmor-dev` 符号链接（如果存在）只能指向其中一个。相反：
  - 如果你是一个在 Helmor 内部运行的 **代理**，系统提示已经为你提供了确切的 CLI 调用（通常是像 `<worktree>/src-tauri/target/debug/helmor-cli` 这样的绝对路径）。直接调用它——不要用 `which` / `file` / `--version` 重新验证。
  - 如果你是一个在终端前的 **人类用户**，运行 `<your-worktree>/src-tauri/target/debug/helmor-cli <子命令>`（或你的活跃 Helmor 构建的任何其他路径）。

无论构建版本如何，每个命令的其余部分都是相同的。

## 初步检查

1.  检查 CLI 是否已安装以及它针对的数据模式：

```bash
helmor cli-status
```

2.  检查活动数据目录和数据库：

```bash
helmor data
```

当输出将被脚本或另一个工具解析时，使用 `--json`。

## CLI 安装与更新

将 Helmor CLI 安装/更新视为 Beta 版本。

- 优先使用 Helmor 桌面的引导/设置组件面板来安装或修复管理的 CLI 入口点。
- 使用 `helmor cli-status` 来验证 PATH 是否指向当前应用程序管理的 CLI。
- 除非它存在于 `helmor --help` 或子命令帮助页面中，否则不要编造一个稳定的独立安装/更新命令。
- 如果用户遇到问题，请让他们运行 `helmor cli-status` 并共享输出，或者在 Helmor 仓库内检查应用程序的组件面板。

## Helmor 技能安装与更新

将 Helmor 技能安装/更新视为 Beta 应用程序管理流程。

- 优先使用 Helmor 桌面的引导/设置组件面板来安装或更新捆绑的 Helmor 技能。
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

为自动化优先选择 JSON 输出：

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

通过 stdio 将 Helmor 作为 MCP 服务器运行：

```bash
helmor mcp
```

当另一个代理/运行时需要通过模型上下文协议调用 Helmor 时使用此命令。

## 命令参考

当你需要完整的顶级 `helmor --help` 命令列表时，请阅读 `references/helmor-help.md`。

对于命令组的精确标志，运行该组的帮助而不是猜测：

```bash
helmor <命令> --help
```
