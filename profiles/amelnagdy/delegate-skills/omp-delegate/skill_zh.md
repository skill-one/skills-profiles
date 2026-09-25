# Oh My Pi 委托

你是**协调者**。将一个有边界的编码任务委托给一个单独的**实现者**——Oh My Pi (`omp`)，然后审查它产生的内容并自行合并。你编写简报并拥有判断权；实现者在自己的会话中做出更改；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 二进制文件是 `omp`，而不是 `pi`

Oh My Pi 是 Pi 的一个分支。这项技能驱动 **`omp`** (`@oh-my-pi/pi-coding-agent`)。原始的 Pi CLI 是一个不同的二进制文件 (`pi`)，具有不同的技能 (`pi-delegate`)。如果 `omp` 缺失但 `pi` 已安装，你拥有的是 Pi，而不是 Oh My Pi。

## 不应使用此功能的情况

- 任务足够小，可以直接内联完成；委托的开销不值得。
- `omp` CLI 未安装或未进行身份验证。
- 用户要求使用原始的 Pi CLI (`pi`) — 使用 `pi-delegate`。
- 你需要一个沙盒化的实现者。Oh My Pi 没有沙盒。`--read-only` 限制了工具表面；一个可写能力的运行不会提示 (`--yolo`)。

## 前置条件（一次性检查）

1. 使用 `bun install -g @oh-my-pi/pi-coding-agent`（或从 https://omp.sh 获取的安装路径）安装 omp。
2. 进行身份验证：在 omp 中使用 `/login` 进行订阅提供者的身份验证，或使用 API 密钥提供者的 API 密钥环境变量。凭证存储在 `~/.omp/` 下。
3. 确认 `omp --version` 成功。
4. 在目标 git 仓库中工作，或将 `--cd` 指向该仓库。

## 选择模型（可选）

省略 `--model`（和 `--provider`）以使用 omp 为此项目/配置配置的默认值。目录是**此安装**的经过身份验证的提供者 — 不是此技能中的固定列表。

要选择另一个模型：

1. **列出此安装实际可以运行的模型。** 不要传递 `omp --list-models` — 该标志已删除，omp 将其视为未知标志（退出码 2）。使用 `models` 子命令：
   - `omp models` — 每个可用模型，按提供者分组
   - `omp models --json` — 相同的目录，机器可读
   - `omp models find <substring>` — 通过提供者、ID 或名称进行过滤（例如：`omp models find sonnet`）
   - `omp models <provider>` — 一个提供者的模型
2. **将那个 ID 传递给中继。** `--model <pattern>` 是 omp 自己的 `--model`：与目录进行模糊匹配（提供者/ID、一个裸 ID，或一个唯一子字符串）。`--provider <name>` 在模式模糊时固定提供者。
3. 中继仅转发字母、数字和 `. _ : / -`。带 `*` 的通配符模式会被拒绝。

`--thinking <level>` 是一个单独的推理旋钮，不是模型 ID。允许的值：`off`、`auto`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`。中继会拒绝任何其他内容（包括 `inherit`），然后再分发 — omp 会发出警告并忽略无效值。

一个舰队通道 (`--lane`) 可以设置 `provider`、`model` 和 `effort`。通道 `effort` 成为 `--thinking`；显式的 `--thinking` / `--model` / `--provider` 标志会覆盖通道。

中继不会转发 `--api-key`、`--smol`、`--slow` 或 `--plan`。这些仍然属于 omp 自己的 CLI。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Oh My Pi 只能看到你发送的文本以及它可以在工作区中检查的内容 — 没有聊天历史记录或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁，以及报告合同。告诉 omp 不要提交。每个简报保持一个任务。
omp 自动加载工作区及其父目录中的 `AGENTS.md`/`CLAUDE.md` 上下文文件，因此仓库指令可以到达它而无需内联。参见
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 分发

使用捆绑的中继。它将简报通过 `omp --mode json` 的标准输入管道，捕获 JSON 事件流，并写入 `result.json`。 (`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。)

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 先列出模型：                       omp models   (或：omp models --json)
# 选择一个模型：                     添加 --model <omp models 中的 ID>
# 选择一个提供者：                   添加 --provider <name>
# 设置推理级别：                     添加 --thinking high
# 只读运行（审查/诊断）：            添加 --read-only
# 信任项目的 .omp 资源：             添加 --approve
# 恢复最新的会话：                  添加 --resume-last  (仅 delta 简报)
# 恢复特定会话：                   添加 --session <id> (仅 delta 简报)
# 硬时间限制（看门狗）：            添加 --timeout 2h  (30m 默认适合短运行；实现简报通常需要 1-2h)
# 查看所有选项：                    node .../relay.mjs --help
```

子进程的当前工作目录固定了工作区。中继默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

中继会阻塞直到 omp 完成。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。预运行使用错误会退出码 2 并不写入结果；缺少 `omp` 会退出码 127 并写入 `status: "omp_unavailable"`。

信任进程状态和工作树而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。omp 的完整报告是 `result.json` 中的 `finalMessage` 字段（也完整打印在标准输出上，在报告标记之间）。

### 4. 审查 — 不要信任自我报告

将 omp 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 阅读与简报的 diff，从 `touchedFiles` 开始。
- 如果安装了相关守卫技能，请运行它们。
- 在删除或重命名后进行往返迁移，并在删除或重命名后搜索悬空引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 合并

实现者编辑工作树；**协调者合并**。只有在门禁通过并且 diff 符合要求后才能合并。如果需要返工，请使用 `--resume-last` 或 `--session <id>` 发送 delta 简报，然后再次审查。

## 自主性和权限

Oh My Pi 没有沙盒。打印模式没有审批 UI，因此可写的中继运行始终通过 `--yolo` (`tools.approvalMode: yolo`) — 否则用户的 `always-ask` 或 `write` 配置会停滞直到看门狗。其他控制是：

1. `--read-only` 限制 omp 的可调用工具为 `--tools read,grep,glob`。它不会传递 `--yolo`。已安装的扩展代码仍然以用户的宿主机权限运行，如果项目资源受信任。
2. 中继默认传递 `--no-extensions --no-skills --no-rules`，因此项目的 `.omp` 扩展、技能和规则保持未发现。`--approve` 是用户信任的仓库的显式选择入。
3. `touchedFiles` 和 diff 是记录了什么已更改的记录。每次运行后检查它们。

## 授权模型

委托是用户选择进入的。一旦他们确认了（“运行这个队列”、“继续”），提交经过验证、门禁通过的工作就是约定的合同。仍然有两个限制：**表面，不要吸收**（报告 omp 的设计决策、可辩护但未询问的转弯，以及非阻塞的吹毛求疵）和**停止范围变化**（如果正确完成需要超出简报，请询问而不是扩展授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、报告合同、实际门禁、标准输入交付、模型列表和 delta 简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) - 审查清单、提交边界和通过 omp 会话进行返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性检查。
