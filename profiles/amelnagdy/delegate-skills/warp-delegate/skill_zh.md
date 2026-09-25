# Warp 委托代理

你是**协调者**。将一个有边界的编码任务委托给一个单独的**执行者**——Warp Agent CLI，然后审阅它生成的内容，并亲自将其部署。你编写简报并拥有最终判断权；执行者在自己的对话中做出更改；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 二进制文件是 `oz`，而不是 `warp`

Warp 提供了两个不同的程序，只有一个可以被委托：

- **`oz`** - Warp Agent CLI。无头且可脚本化；`oz agent run` 在本地目录上执行一个代理。**这是中继驱动的程序。**
- **`warp`** - 交互式 Warp TUI。它需要一个终端设备，没有提示符或打印标志（它的唯一选项是 `--resume`、`--auto-approve`、`--api-key` 和提供者密钥命令），当 stdin 是管道时，它会退出并显示 `Device not configured`。它不能被中继。

如果 `oz` 缺失但 `warp` 已安装，你拥有的是 TUI，而不是 CLI。

## 不应使用此方法的情况

- 任务足够小，可以直接在行内完成；委托的开销不值得。
- `oz` CLI 未安装或未进行身份验证。
- 你需要一个沙盒化或只读的执行者。`oz agent run` 具有**没有沙盒、没有权限模式、也没有只读运行**——请参阅 [自主性和权限](#autonomy-and-permissions)。
- 工作必须保持在 Warp 的服务器之外。`oz agent run` 除非传递 `--no-snapshot`，否则会上传运行结束的工作空间快照，而对话保存在服务器端。

## 前置条件（一次性检查）

1. 安装 Warp Agent CLI - 请参阅 <https://docs.warp.dev/cli/>。
2. 进行身份验证：`oz login`，或者为 CI、容器或任何无头主机设置 `WARP_API_KEY`。
3. 确认账户具有 AI 配额。**一个有效的登录并不足够**——与该软件包中的其他 CLI 不同。`oz whoami` 可能成功，而每个调度都因 `In order to use Warp's AI features, subscribe to a Warp plan, or bring your own inference.` 而失败。Warp 内部将其记录为 `QuotaLimit` / "缺乏 AI 配额"，因此它是一个账户的信用条件，而不是 CLI 特定的权限：`oz` 运行与 Warp 应用程序相同的代理 harness，并使用相同的账户、计划和信用。确认 `oz whoami` 指向持有计划的账户——如果它没有，`oz logout && oz login` 可以修复它。否则，请确认计划的 AI 信用尚未用尽，或者存储你自己的提供者密钥——`warp --set-provider-api-key <openai|anthropic|google|grok>`，或 TUI 中的 `/api-keys`。自带密钥不需要付费 Warp 计划。
4. 确认 `oz --version` 成功，并且 `oz whoami` 打印出你的用户。
5. 在目标 git 仓库中工作，或者将 `--cd` 指向该仓库。

在 macOS 上，CLI 作为已签名的 Developer ID 二进制文件分发；第一次运行可能会被 Gatekeeper 暂停，直到它被批准。

## 选择模型（可选）

省略 `--model` 以使用 Warp 配置的默认值。要选择另一个，从 `oz model list` 中选择一个 ID 并原样传递。中继只接受字母、数字和 `. _ : / -`，因此一个值不能被误认为是另一个 `oz` 标志。

## 循环

每个任务运行这五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Warp 只能看到你发送的文本以及它可以在工作空间中检查的内容——没有聊天历史或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁，以及报告合同。告诉它不要提交。每个简报保持一个任务。简报作为 `--prompt` 值传递给 argv，因此它在主机进程列表中可见——将其中的秘密排除在外，并参考工作空间文件。请参阅
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 调度

使用捆绑的中继。它运行 `oz agent run --output-format ndjson`，捕获事件流，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型：                          添加 --model <从 oz model list 中获取的 ID>
# 使用代理配置文件：                    添加 --profile <ID>
# 标记运行：                           添加 --name <标签>
# 继续现有对话：                       添加 --conversation <ID>（仅 delta 简报）
# 基于 Warp 技能运行：                 添加 --skill <name|repo:name|org/repo:name>
# 启动 MCP 服务器：                    添加 --mcp <路径或内联 JSON>  （可重复）
# 抑制工作空间快照上传：              添加 --no-snapshot
# 硬时间限制（看门狗）：              添加 --timeout 2h  （30m 默认适合短运行；实施简报通常需要 1-2h）
# 查看所有选项：                       node .../relay.mjs --help
```

中继使用工作空间，并传递给 Warp 自己的 `--cwd`。它默认在系统临时目录下写入工件，并且永远不会提交。请参阅
[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

中继会阻塞，直到 `oz` 完成。使用协调者的后台命令功能运行它，或者在 shell 中将其后台运行并轮询 `result.json`。运行前使用错误退出 2 并不写入结果；缺少 `oz` 退出 127 并写入 `status: "warp_unavailable"`。

相信进程状态和工作树而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。Warp 的报告是 `result.json` 中的 `finalMessage` 字段（也在报告标记之间打印在 stdout 上）；原始事件流始终在 `events.jsonl` 中。

### 4. 审阅——不要相信自我报告

将 Warp 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报进行 diff，从 `touchedFiles` 开始。
- 如果安装了相关守卫技能，请运行它们。
- 运行往返迁移，并在删除或重命名后查找悬空引用。

由于没有只读模式可以回退，diff 是**唯一**的记录——并且它记录了 git 在工作空间之后可以看到的内容，而不是运行所做的一切。从干净的树中调度，以便两者尽可能接近。请参阅
[references/review-and-land.md](references/review-and-land.md)。

### 5. 部署它

执行者编辑工作树；**协调者提交。** 只有在门禁通过并且 diff 符合要求后才能提交。如果需要重新工作，使用 `--conversation <ID>` 发送 delta 简报，并使用 `result.json` 中的 `conversationId`，然后再次审阅。

## 自主性和权限

`oz agent run` 具有**没有沙盒、没有权限模式、也没有只读模式**。无头运行以你自己的用户权限读取、写入、编辑和执行命令，并且永远不会提示。CLI 中没有任何东西可以限制该表面，因此这个中继不提供 `--read-only` 标志——提供一个标志意味着不存在强制执行。你实际拥有的控制是：

1. **按目录范围限制。** `--cd` 固定工作空间，并且中继将其传递给 Warp 自己的 `--cwd`。将其视为*目标*而不是*围栏*：在 oz 0.2026.05.27 中，shell 命令确实在工作空间中运行，但代理的文件工具将裸相对路径解析为 `$HOME`。在简报中指定绝对路径——请参阅 [references/writing-the-brief.md](references/writing-the-brief.md)。
2. **审阅 diff。** `touchedFiles` 是运行后 `git status --porcelain` 采取的——运行后，git 可见的工作树状态，而不是代理所做操作的日志。它不能显示忽略的文件、运行后已撤销的编辑，或仓库外的写入（见第 1 点），并且它包含调度前已经脏的内容。从干净的树中调度，以便这些是相同的集合，并将 diff 视为最佳可用记录，而不是完整记录。
3. **快照出口。** `--no-snapshot` 将 Warp 的标志转发，因此运行结束的工作空间快照不会被上传。如果没有它，上传是 Warp 的默认行为。

`--auto-approve` 属于交互式 `warp` TUI，并且对 `oz agent run` 没有影响。

## 授权模型

委托是用户选择进入的。一旦他们有了（“运行这个队列”、“继续”），提交经过验证的、门禁通过的工作是约定的合同。仍然有两个限制：**表面，不要吸收**（报告 Warp 的设计决策、可辩护但未询问的转弯、以及非阻塞的吹毛求疵），以及**停止范围变化**（如果正确完成需要超出简报，请询问而不是扩展授权）。请参阅 [references/review-and-land.md](references/review-and-land.md)。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、报告合同、实际门禁、argv 传递和 delta 简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) - 审阅清单、提交边界和通过 Warp 对话进行重新工作。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性检查。
