# Pi 委托人

你是**协调者**。将一个有边界的编码任务委托给一个单独的**实现者**——Pi 编码代理 CLI，然后审查它生成的内容，并亲自将其部署。你编写简报并拥有判断权；实现者在它自己的会话中做出更改；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接完成；委托的开销不值得。
- `pi` CLI 未安装或未进行身份验证。
- 你需要一个沙盒化的实现者。Pi 没有沙盒，也没有权限模式；`--read-only` 限制了工具表面，但具有写入能力的运行会无提示执行。

## 前置条件（一次性检查）

1. 使用 `npm install -g @earendil-works/pi-coding-agent` 安装 pi。
2. 进行身份验证：在 pi 中使用 `/login`（针对订阅提供者），或使用 API 密钥环境变量 / `pi` 的认证文件（针对 API 密钥提供者）。
3. 确认 `pi --version` 成功。
4. 在目标 git 仓库中工作，或将 `--cd` 指向该仓库。

## 选择模型（可选）

省略 `--model` 以使用 pi 配置的默认模型。要选择其他模型，请从 `pi --list-models` 中选择，并传递一个显式的 ID 或模式，如 `<提供者>/<模型 ID>` 或 `sonnet:high`。中继器仅接受字母、数字和 `. _ : / -`（在 Windows 上，该值会传递到 shell），因此带有 `*` 的通配符模式不会被转发。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Pi 只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁，以及报告合同。告诉 pi 不要提交。每个简报保持一个任务。Pi 会自动加载工作区及其父目录中的 `AGENTS.md`/`CLAUDE.md` 上下文文件，因此仓库指令可以无需内联即可到达它。参见
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派发

使用捆绑的中继器。它将简报通过 `pi --mode json` 传递到 stdin，捕获 JSON 事件流，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型：                          添加 --model <从 pi --list-models 获取的 ID>
# 选择提供者：                       添加 --provider <名称>
# 只读运行（审查/诊断）：            添加 --read-only
# 信任项目 .pi 资源：             添加 --approve
# 恢复最近的会话：                添加 --resume-last  (仅限增量简报)
# 恢复特定会话：                  添加 --session <ID> (仅限增量简报)
# 硬时间限制（看门狗）：            添加 --timeout 2h  (30m 的默认值适合短运行；实现简报通常需要 1-2h)
# 查看所有选项：                         node .../relay.mjs --help
```

子进程的当前工作目录固定了工作区。中继器默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

中继器会阻塞，直到 pi 完成。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。运行前使用错误会退出 2 并不写入结果；缺少 `pi` 会退出 127 并写入 `status: "pi_unavailable"`。

信任进程状态和工作树，而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。Pi 的完整报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在 stdout 上）。

### 4. 审查——不要信任自我报告

将 pi 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报进行差异比较，从 `touchedFiles` 开始。
- 如果安装了相关守卫技能，请运行它们。
- 在删除或重命名后进行往返迁移，并在删除或重命名后查找悬空引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

实现者编辑工作树；**协调者提交**。只有在门禁通过并且差异有效时才提交。如果需要重新工作，请使用 `--resume-last` 或 `--session <ID>` 发送增量简报，然后再次审查。

## 自主性和权限

Pi 没有沙盒和权限模式。默认的无头运行会读取、写入、编辑和执行 shell 命令，没有任何提示——控制项是：

1. `--read-only` 限制 pi 可调用的工具为 `--tools read,grep,find,ls`，涵盖内置、扩展和自定义工具。安装的扩展代码仍然以用户的主机权限运行。
2. 中继器默认传递 `--no-approve`，因此项目的 `.pi` 设置、扩展和技能保持未受信任。`--approve` 是用户信任的仓库的明确选择入。
3. `touchedFiles` 和差异是更改的记录。每次运行后检查它们。

## 授权模型

委托是用户选择入的。一旦他们确认了（“运行这个队列”，“继续”），提交经过验证的门禁通过的工作是约定的合同。仍然有两个限制：**表面，不要吸收**（报告 pi 的设计决策、可辩护但未询问的转弯和非阻塞的吹毛求疵）和**停止范围变化**（如果正确完成需要超出简报，请询问而不是扩展授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考资料

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、报告合同、实际门禁、stdin 传递和增量简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json`、轮询和失败恢复。
- [references/review-and-land.md](references/review-and-land.md) - 审查清单、提交边界和通过 pi 会话进行重新工作。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性检查。
