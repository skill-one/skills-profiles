# Herdr

Herdr 将终端组织成工作区、标签页和窗格，识别窗格内运行的编码代理，并通过 `herdr` 命令行界面暴露当前会话。

在发出任何控制命令之前，请验证该代理是否在 Herdr 管理的窗格内运行：

```bash
test "${HERDR_ENV:-}" = 1
```

如果检查失败，请说明您不在 Herdr 内运行并停止。不要从 Herdr 外部检查或控制聚焦的 Herdr 会话。

当检查通过时，`PATH` 中的 `herdr` 二进制文件会与当前会话通信。使用它来检查相邻工作、创建终端布局、启动代理和命令、读取输出，以及等待状态变化。

## 学习当前 CLI

已安装的二进制文件是命令语法的权威。从以下内容开始：

```bash
herdr --help
```

然后通过运行不带子命令的组来打印相关命令组：

```bash
herdr agent
herdr pane
herdr workspace
herdr tab
herdr worktree
herdr terminal
herdr notification
herdr integration
herdr session
herdr machine
```

不要直接运行 `herdr` 进行发现；它会启动或附加 TUI。不要通过省略参数来探测可变嵌套命令。像 `herdr workspace create` 这样的命令在默认情况下是有效的，并且会执行。

大多数控制命令返回 JSON。从这些响应中读取标识符和状态，而不是预测它们。

## 理解布局、窗格和代理

根据任务选择合适的原语：

- 工作区、标签页和窗格拓扑组织终端位置。
- 窗格命令控制原始终端、外壳、测试、服务器、输入和输出。
- 代理命令控制当前占据窗格的已识别编码代理。

窗格是否存在与其是否包含代理无关。`agent start` 需要一个现有的可用外壳窗格，并且永远不会创建、分割或移动布局。对于普通进程，请使用窗格命令。当 Herdr 必须验证代理身份或解释 `idle`、`working`、`blocked`、`done` 和 `unknown` 生命周期状态时，请使用代理命令。

代理命令接受唯一的实时代理名称或当前托管该代理的窗格 ID。它们不接受终端 ID 或裸的代理类型标签。名称必须匹配 `[a-z][a-z0-9_-]{0,31}`，并且在实时代理中是唯一的。名称跟随当前窗格的占用者，当该代理退出、被释放或被替换时，名称会被清除。

`idle` 和 `done` 都表示代理准备好输入。CLI/API 使用服务器的已见状态来区分它们；显式聚焦命令标记目标已见，而读取不会。每个 TUI 客户端独立跟踪已查看的完成情况，因此其 Done 徽章可能与 CLI 或另一个客户端的徽章不同。`blocked` 表示 Herdr 识别了一个批准或提问的 UI。`unknown` 表示代理存在，但 Herdr 无法自信地对其进行分类；它不能证明完成。

## 使用 ID 和调用者上下文

公共 ID 是不透明的稳定句柄：

- 工作区：`w1`
- 标签页：`w1:t1`
- 窗格：`w1:p1`

已关闭的标签页和窗格 ID 不会被重用。一个移动到另一个工作区的窗格将获得一个新的工作区限定窗格 ID。在 `pane move` 后，继续使用 `.result.move_result.pane.pane_id` 或实时代理名称。旧值作为 `.result.move_result.previous_pane_id` 报告；只有移动进程继承的调用者上下文保留解析该旧 ID，因此不要将其用作通用代理目标。

Herdr 将调用者的上下文注入每个管理的窗格：

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
```

当窗格命令应针对调用窗格时，请优先使用 `--current`。省略的 `pane split` 目标在 `HERDR_PANE_ID` 可用时使用调用窗格，否则使用聚焦窗格。其他命令可能使用 UI 聚焦窗格，该窗格可以属于用户或另一个客户端。

使用以下命令发现实时状态：

```bash
herdr workspace list
herdr tab list --workspace "$HERDR_WORKSPACE_ID"
herdr pane current --current
herdr pane list --workspace "$HERDR_WORKSPACE_ID"
herdr agent list
```

创建响应会暴露下次要使用的 ID。`workspace create` 返回 `.result.workspace`、`.result.tab` 和 `.result.root_pane`。`tab create` 返回 `.result.tab` 和 `.result.root_pane`。`pane split` 返回新的窗格作为 `.result.pane`。

ID 和实时代理名称在一个服务器的作用域内。两个保存的 SSH 机器都可以有 `w1:p1` 或名为 `reviewer` 的代理。在 TUI 中选择机器不会重新定位在您的窗格中运行的命令：如果没有 `--machine`，它们仍然使用继承的会话和套接字上下文。

要控制保存的 SSH 机器，请使用相同的全局前缀进行发现和每个后续命令：

```bash
herdr --machine <label-or-id> agent list
herdr --machine <label-or-id> pane list
herdr --machine <label-or-id> agent prompt <remote-agent-name> "Reply with your current status." --wait --timeout 120000
```

选择器必须是启用的保存配置文件 ID 或唯一、区分大小写的标签，而不是任意的 SSH 主机名。命令使用该配置文件的远程会话，而无需打开 TUI。不要将 `--machine` 与 `--session` 或 `--remote` 结合使用。在远程机器上发现 ID；继承的本地 ID 和 `--current` 不能标识远程窗格。

两个安装都必须支持机器 API 转发，并且远程服务器必须已经运行且 API 兼容。转发永远不会安装、启动或重启服务器，并且永远不会回退到本地。本地配置、会话管理、安装命令和交互式附加不会转发。远程工作树路径必须是绝对的、`~` 或以 `~/` 开头；插件链接路径必须是绝对的。连接失败并不能证明没有应用变更：在重试之前检查远程状态。

`herdr machine list` 列出保存的连接配置文件，而不是跨机器窗格清单；添加 `--json` 以便脚本使用。只有在用户要求时才添加、删除、启用或禁用配置文件。删除配置文件会断开客户端，但不会停止远程会话。添加机器使用远程默认会话，除非明确提供 `--remote-session`。设置会在停止不兼容的服务器之前询问，默认为“否”；不要在未经用户同意的情况下批准替换。实验性传递不是 `machine add` 的一部分。

## 启动和协调代理

默认情况下，在当前标签页的兄弟窗格中，并使用当前工作目录。除非用户明确要求拓扑结构或位置，否则不要创建工作区、标签页、工作树或不同的 cwd。

尊重用户请求的方向。否则检查调用窗格：

```bash
herdr pane layout --pane "$HERDR_PANE_ID"
```

将宽窗格向右分割，将窄窗格或高窗格向下分割。避免重复同一方向的分割，这会创建无法使用的窄列或短行。保持用户的焦点在调用窗格中，并显式保留调用者的工作目录：

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

当合适时，将 `right` 替换为 `down`。从 `.result.pane.pane_id` 读取新的窗格 ID。

必须有一个可用的外壳窗格，其交互式提示符处于活动状态，外壳本身在前景，没有前景命令、编辑器或代理运行。在该窗格中启动一个支持代理，并使用一个有用的唯一名称：

```bash
herdr agent start reviewer --kind codex --pane <returned-pane-id>
```

使用用户请求的类型。运行 `herdr agent` 以检查安装的代理类型列表和选项。在 `--` 之后仅传递原生代理参数：

```bash
herdr agent start reviewer --kind codex --pane <returned-pane-id> -- <agent-args...>
```

成功的 `agent start` 只有在 Herdr 在同一窗格中检测到预期的代理并认为其准备好交互式输入时才会返回。如果代理在启动期间被阻塞，命令会立即返回 `agent_not_ready`，但会保留名称以供 `agent read` 和 `agent send-keys` 使用。在提示它之前，等待代理变为空闲。启动默认超时时间为 30 秒。

通过代理表面提交工作：

```bash
herdr agent prompt reviewer "Review the current diff and report only actionable findings." --wait --timeout 120000
```

`agent prompt` 尊重窗格的实时括号粘贴模式，并将文本后跟编码的 Enter 作为一次有序提交发送。它只有在两者都写入后才报告成功提交；仅凭这一点并不能证明代理开始了回合。对于 Windows 上的 Codex，Herdr 在 Enter 之前发送粘贴边界，因此提交不依赖于提示大小。它会在发送任何输入之前，使用 `agent_blocked` 拒绝已经在批准或提问对话框中等待的代理。在回答之前检查阻塞 UI 并询问用户。对于正常代理工作，`--wait` 足够：它等待第一个稳定的 `idle`、`done` 或 `blocked` 状态。不要重复这些默认值与 `--until`。

使用 `--wait` 时，从非工作状态发送的提示必须产生观察到的 `working` 或 `blocked` 活动。提交后，Herdr 会等待最多五秒钟以观察该活动；无关的 `idle`、`done` 或会话更改不会满足此门。如果没有观察到活动，它将返回 `agent_prompt_stalled`；如果调用者的超时先过期，它将返回 `timeout`。调用者超时包括提交时间。如果没有超时，活动观察到后，稳定状态等待是无限的。此等待跟踪生命周期状态，而不是单个回合；如果代理已经在工作，当前活跃回合的完成可能满足它。

仅用于特定状态的工作流程，例如等待已运行的代理请求输入，使用 `--until`：

```bash
herdr agent wait reviewer --until blocked --timeout 120000
```

如果没有 `--until`，独立的 `agent wait` 使用与 `agent prompt --wait` 相同的稳定状态默认值。

使用逻辑键进行交互式代理 UI 控制：

```bash
herdr agent send-keys reviewer esc
herdr agent send-keys reviewer ctrl+c
```

Herdr 在写入任何字节之前会验证所有键。通过解析的代理读取结果：

```bash
herdr agent get reviewer
herdr agent read reviewer --source recent-unwrapped --lines 120
```

如果等待失败或返回 `blocked`，在决定要发送什么输入之前，请检查 `agent get` 和 `agent read`。超时或停滞响应并不能证明提示从未送达；不要盲目再次提交。仅在有意进行原始终端控制时使用窗格表面。

## 在另一个窗格中运行普通命令

创建具有相同几何规则的兄弟窗格，保留调用者的工作目录，并保持用户焦点不变：

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

从 `.result.pane.pane_id` 读取新的窗格 ID，然后运行和检查命令：

```bash
herdr pane run <returned-pane-id> "just test"
herdr pane wait-output <returned-pane-id> --match "test result" --timeout 120000
herdr pane read <returned-pane-id> --source recent-unwrapped --lines 120
```

`pane run` 原子性地发送命令文本和 Enter。`pane wait-output` 立即搜索选定的快照，因此已存在的输出可以匹配。使用 `--match <text>` 表示字面子字符串，或使用 `--regex <pattern>` 表示 Rust 正则表达式。省略 `--timeout` 允许无限等待。

使用与任务匹配的读取源：

- `visible`：当前渲染的视口。
- `recent`：最近渲染的输出，包括软换行。
- `recent-unwrapped`：最近输出，软换行已连接；为日志和转录文件优先使用它。
- `detection`：用于代理检测的纯文本底部缓冲区快照。

使用 `--format ansi` 当颜色和终端样式是证据时。否则使用文本。

`--lines` 请求 Herdr 从窗格的可用屏幕和主机滚动缓冲区获取更多行。交替屏幕行不会进入普通主机滚动缓冲区。对于支持的空闲代理，Herdr 可以收集应用程序拥有的历史记录并在之后恢复视口，但不是每个应用程序或响应都可以通过这种方式恢复。

如果一个更大的最近读取仍然没有揭示完成的响应，请让代理将内容作为 Markdown 写入临时目录，并仅以文件路径回复，然后在同一机器上读取该文件。仅将其用作后备；不要在初始提示中请求文件输出。

## 安全和协调规则

- 除非用户要求切换上下文，否则对于后台工作使用 `--no-focus`。
- 使用 `--current`、显式的窗格 ID 或唯一的代理名称。不要依赖另一个客户端的聚焦窗格。
- 从 JSON 响应中解析 ID。不要从侧边栏顺序或示例中推导它们。
- 除非用户明确要求，否则不要关闭您未创建的工作区、标签页、窗格或会话。`workspace close --group` 关闭主工作区和其链接的工作树工作区；永远不要仅仅为了绕过 `workspace_group_close_required` 而添加它。
- 仅在用户验证了存储库之后使用 `--trust-repository`。它授予每次请求的 Git 信任；它不是失败的工作树命令的常规重试。
- 客户端和服务器版本在更新后可能不同。在依赖新服务器功能之前，检查 `herdr status`。缺少方法不是停止或升级服务器的许可。
- 除非用户明确打算停止服务器及其窗格进程，否则不要从活动会话中运行 `herdr server stop`。
- 不要杀死主 Herdr 进程。使用命名的测试会话进行需要隔离服务器的实验。
- CLI 服务器错误在 stderr 上是 JSON，退出状态为 1。CLI 语法错误退出状态为 2。
