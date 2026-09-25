# Worktrunk

Worktrunk 是一个用于管理 git worktrees 的命令行工具，帮助用户使用 Worktrunk。

## 可用的文档

参考文件从 [worktrunk.dev](https://worktrunk.dev) 文档同步：

- **reference/config.md**: 用户和项目配置（LLM、钩子、命令默认值）
- **reference/hook.md**: 钩子类型、执行时机和执行顺序
- **reference/switch.md**、**merge.md**、**list.md** 等：命令文档
- **reference/extending.md**: 别名、多步骤管道、自定义子命令和模板扩展的陷阱（两阶段 `{% raw %}` 延迟、`for-each` 菜单）
- **reference/llm-commits.md**: LLM 提交信息生成
- **reference/tips-patterns.md**: 实用菜谱 — 别名、按分支变量、每个 worktree 的开发服务器、并行代理模式
- **reference/shell-integration.md**: Shell 集成调试
- **reference/troubleshooting.md**: LLM 和钩子的故障排除（Claude 特定）

对于特定命令的选项，运行 `wt <command> --help`。对于配置，请遵循以下工作流程。

## 命令作用于哪个 worktree

`wt` 从工作目录中查找 *仓库*，从命令自己的参数中查找 *worktree*。两条规则涵盖了所有情况：

1. **命名一个分支的命令已经命名了它的 worktree。** Worktrees 通过分支名进行寻址，所以 `wt switch <branch>`、`wt remove <branch>`、`wt step diff --branch <branch>` 和 `wt config state marker set --branch <branch>` 都作用于该分支的 worktree，无论你从哪个 worktree 运行它们。每个这样的参数也接受 worktree 的路径，在分支无法命名的情况下 — 同一分支的第二次检出，或一个分离的 worktree（`marker` 仍然拒绝它，因为它按分支名键值状态）。
2. **`-C <path>` 移动工作目录，而不是 worktree 选择。** 当仓库查找有问题时使用它：一个 *不同的* 仓库；一个作用于当前 worktree 且不接受分支参数的命令（`wt merge`、`wt step rebase|squash|push` — 它们的 `[TARGET]` 是合并目标，而不是 worktree）；或者调用者的工作目录根本不在仓库内，例如主机固定在其他地方的代理钩子。

在分支参数之上叠加 `-C` 会导致两次命名同一个 worktree。在一个有 `alpha` worktree 的仓库的 `alpha` worktree 内：

```bash
wt step diff --branch beta                    # ✓ 分支参数选择 worktree
wt -C ../repo.beta step diff --branch beta    # ✗ 两次说 beta

wt switch --create beta                       # ✓ --base 已经默认为默认分支
wt -C ../repo switch --create beta            # ✗ -C 添加了 nothing；你已经在这个仓库内
```

## 两种类型的配置

Worktrunk 使用两个具有不同作用域和权限模型的配置文件：

**用户配置**（`~/.config/worktrunk/config.toml`，永远不会提交到 git）包含个人偏好：LLM 集成、worktree 路径模板、命令设置、用户钩子。保守地处理它 — 在编辑前提出更改并获取同意，永远不会代表用户安装工具，并保留文件现有的结构和注释。参见 `reference/config.md`。

**项目配置**（`<repo>/.config/wt.toml`，提交到 git）包含团队范围的自动化：worktree 生命周期钩子（预启动、预合并等）。主动编辑 — 更改是版本化的，可以通过 git 逆转。注释每个钩子的存在原因，并在添加破坏性命令（`rm -rf`、`DROP TABLE`）、管道到 shells 的网络获取或 `sudo` 前警告用户。参见 `reference/hook.md`。

一些请求跨越两者：提交信息生成是用户配置，而团队的质量检查是项目配置。

## 核心工作流程

### 设置提交信息生成（用户配置）

检测已安装的工具（`which claude codex llm aichat`）；如果没有，推荐 Claude Code。从 `reference/llm-commits.md` 中获取所选工具的确切命令，提出 `[commit.generation]` 更改，并在批准后应用它（如果不存在配置，则首先使用 `wt config create`）。为了验证，`wt step commit --dry-run` 渲染提示，运行 LLM，并打印消息而不提交。

### 配置项目钩子

根据命令应在何时运行以及它是否可能阻塞来选择钩子类型 — `reference/hook.md` 将所有十个（5 个事件 × 预/后）映射到它们的时机和典型用途。

从项目本身（`package.json` 脚本、`Cargo.toml`、`pyproject.toml`）派生命令，并在添加它们之前验证它们是否运行。

当一个新的钩子必须等待一个现有的钩子时，将条目转换为管道；命名表中的独立命令并行运行：

```toml
# 管道：安装完成后才开始迁移
[[pre-start]]
install = "npm install"

[[pre-start]]
migrate = "npm run db:migrate"

# 并行：一个表中的独立命令
[pre-start]
install = "npm install"
env = "cp .env.example .env"
```

使用 `wt switch --create test-hooks` 进行测试。

## 常见任务参考

### 用户配置任务
- 设置提交信息生成 → `reference/llm-commits.md`
- 自定义 worktree 路径 → `reference/config.md#worktree-path-template`
- 自定义提交模板 → `reference/llm-commits.md#prompt-templates`
- 配置命令默认值 → `reference/config.md#command-config`
- 设置个人钩子 → `reference/config.md#user-hooks`

### 项目配置任务
- 为新项目设置钩子 → `reference/hook.md`
- 向现有配置添加钩子 → `reference/hook.md#hook-forms`
- 使用模板变量 → `reference/hook.md#template-variables`
- 向列表添加开发服务器 URL → `reference/config.md#dev-server-url`

### 别名和多 worktree 任务
- 创建 `wt` 别名 → `reference/extending.md#aliases`
- 在每个 worktree 中运行命令 → `reference/step.md#wt-step-for-each`
- 重新构建每个 worktree（up-style）→ `reference/extending.md#recipe-rebase-every-worktree-onto-its-upstream`
- 将模板传递给嵌套的 `wt` 命令 → `reference/extending.md#nesting-templates`

## 关键命令

```bash
# 查看所有配置
wt config show

# 创建初始用户配置（LLM/提交设置：参见 reference/llm-commits.md）
wt config create

# 完整配置参考（子命令、模板、环境变量）
wt config --help
```

## 非交互式会话中的钩子批准

Worktrunk 不会在用户明确批准之前运行任何项目的钩子或别名。`.config/wt.toml` 中的命令是用户可能刚刚克隆的仓库中的任意 shell 代码，所以第一次运行时 Worktrunk 显示每个命令并等待用户批准它 — 不可信的 `.config/wt.toml` 不能静默执行任何内容。批准存储在每个项目的 `~/.config/worktrunk/approvals.toml` 中，并且每当命令模板更改时都会重新提示，所以一个钩子不能在批准后被替换为不同的命令。

运行 `wt merge`、`wt switch` 或其他触发钩子的命令的代理将遇到类似错误：

```
▲ cargo-difftest 需要批准执行 1 个命令：
○ post-merge install:
  cargo install --path .
✗ 无法在非交互式环境中提示批准
↳ 要在 CI/CD 中跳过提示，请添加 --yes；要预先批准命令，请运行 wt config approvals add --yes
```

解决方法是让用户自己做出信任决策：

- **`wt config approvals add`** — 交互式提示，用户在存储到 `~/.config/worktrunk/approvals.toml` 之前审查每个命令。每个项目运行一次；批准跨调用持久存在，直到命令模板更改或项目移动。这是推荐的方法 — 用户审查并同意将要运行的命令。

**当作为代理调用时，停止并升级到用户。** 批准项目的钩子是一个关于此仓库是否应该被信任在用户的机器上执行任意命令的安全决策 — 这个决策属于用户，而不是代理。告诉用户运行 `wt config approvals add` 并让他们审查命令。不要代表用户使用 `--yes`：在受阻命令上它跳过了该调用的门，而 `wt config approvals add --yes` 记录了项目声明的每个命令，没有人阅读它们。两者都存在于 CI/CD 管道和已经控制自己钩子内容的容器中；两者都不是交互式代理静默批准提示的捷径。

## 高级：代理传递

当用户请求在后台会话中用代理生成一个 worktree（“为...生成 worktree”、“传递给另一个代理”）时，使用 `reference/tips-patterns.md#agent-handoffs` 中的 tmux 或 Zellij 命令，用你正在运行的 CLI 替换 `claude`，并遵循该部分关于子命令（如 OpenCode 的 `run`）去哪里的说明。

**要求**（所有必须为真）：
- 用户明确请求生成/传递
- 用户位于支持的多路复用器（检查 `$TMUX` / `$ZELLIJ`）
- 用户的 项目指令（`CLAUDE.md` 或 `AGENTS.md`）或显式提示授权此模式

**不要使用此模式** 进行正常的 worktree 操作。

### 并行子代理（单个 Claude Code 会话）

要生成多个子代理，每个子代理都从单个 Claude Code 会话的自己的 worktree 中工作 — 没有终端多路复用器，另一个窗格中没有人类 — 从父级预启动每个 worktree 并将路径传递到子代理提示：

```bash
wt switch --create <branch> --no-cd
```

然后调用 `Agent` 工具 **不带** `isolation: "worktree"`，在提示中命名路径：

```
您正在 `/abs/path/to/myproject.<branch>` 分支上工作。
所有编辑都必须保留在该 worktree 中。
```

`--no-cd` 跳过父级无法消费的 shell-integration cd 脚本。仅在没有任何用户或项目钩子配置 worktree 且每个子代理都执行自己的构建/测试步骤时（例如 `cargo run -- hook pre-merge --yes`）添加 `--no-hooks` — 一个安装依赖项或链接 git 忽略的构建环境的 `pre-start` 钩子将子代理传递给一个它可以在跳过时无法构建的 worktree。保留钩子需要项目的钩子命令已经批准：父级会话无法提示，所以 `.config/wt.toml` 中的未批准命令会导致创建失败 — 参见 **非交互式会话中的钩子批准** 以上。

**不要** 使用 `Agent { isolation: "worktree" }`。Claude Code 将其内部代理 ID 作为 `name` 传递给 `WorktreeCreate` 钩子，所以 `wt` 在一个 throwaway 分支上创建 worktree 为 `myproject.agent-<id>`。如果子代理然后在上面创建一个特性分支，您最终会得到非规范路径、孤儿分支和针对错误分支触发的 post-start 钩子。使用 `wt switch --create` 预创建可以保持路径、分支和钩子目标一致。
