# 协调员

你是**协调者**。将一个有边界的编码任务交给一个单独的**执行者**——Aider——然后
审查它产生的结果并亲自将其合并。你编写简报并拥有判断权；Aider在自己的运行中完成打字；你验证并提交。

这个循环只需要一个shell命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 关于Aider需要知道的一件事

**Aider默认提交。** 它的两个默认设置会破坏这个技能存在的可审查差异：

- `--auto-commits`（默认 `True`） - Aider在每次交互后提交自己的编辑。
- `--dirty-commits`（默认 `True`） - Aider在开始编辑之前提交**你的**现有的未提交工作。

转发器始终传递 `--no-auto-commits` 和 `--no-dirty-commits`，并且它们都不能通过转发器进行配置。如果你手动而不是通过转发器驱动 `aider`，请自己传递这两个参数，否则工作将作为你未审查的提交落地。转发器还传递 `--no-gitignore`，因为Aider否则会在启动时将 `.aider*` 写入 `.gitignore` 并弄脏你即将读取的树。

## 不应使用此功能的情况

- 任务足够小，可以内联完成；委托的开销不值得。
- `aider` CLI未安装，或者没有为其配置模型。
- 你希望执行者管理自己的提交。Aider可以，但这个技能故意关闭该功能——差异是交付物。

## 前置条件（一次性检查）

1. 安装Aider - `python -m pip install aider-chat`，或从[Aider安装文档](https://aider.chat/docs/install.html)下载独立安装程序。
2. 配置模型。Aider从环境（`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、…）或自己的配置中读取提供者密钥；参见[Aider的模型文档](https://aider.chat/docs/llms.html)。
3. 确认 `aider --version` 成功。
4. 在目标git仓库中工作，或指向 `--cd`。

## 选择模型

当省略 `--model` 时，Aider使用其配置的模型。传递 `--model <name>` 以选择另一个。

## 本地和自托管模型

Aider与任何OpenAI兼容的端点通信，因此这也是将任务委托给在用户自己的硬件上运行的模型的技能——lama.cpp的服务器、Ollama、vLLM、LM Studio或任何其他提供相同API的服务。将 `--model` 与 `--api-base` 配合使用：

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo \
  --model openai/<served-model-name> --api-base http://127.0.0.1:<port>/v1
```

与托管提供者有三个不同之处：

- **必须使用 `openai/` 前缀。** 它告诉Aider向你的端点使用OpenAI协议；它后面的部分是你服务器报告的任何名称，而不是提供者目录名称。
- **仍然需要占位符密钥。** 导出任何非空的 `OPENAI_API_KEY`。客户端库即使在服务器忽略其值时也需要该标头。
- **请求较小的编辑格式。** 本地模型通常无法满足Aider的默认 `diff` 格式，该格式需要精确的搜索/替换块。`--edit-format whole` 用token换取可靠性；使用 `--file` 保持简报的范围紧密，以便整文件重写保持低成本。

不运行的本地端点看起来像挂起，而不是错误：Aider会重试连接，直到转发器的 `--timeout` 狗哨触发并报告 `status: "timeout"`。在派遣长简报之前确认服务器已启动。

### 保持离线

不涉及账户或提供者注册：Aider是一个pip安装，端点是你的，`OPENAI_API_KEY` 只需要非空。转发器将原本会自行到达网络的标志固定在它们身上 - `--no-check-update`、`--no-analytics`（Aider自己的默认值是 `random`，这本身就会使某些会话选择该选项）、`--no-detect-urls`，如果没有这些，Aider会提出抓取简报中的任何URL，`--yes-always` 会默默地接受该提议。

`--no-suggest-shell-commands` 通过关闭剩余的路径来关闭，该路径可以使运行在不被要求的情况下到达网络。简报本身不受转发器控制：告诉Aider安装包或调用API的指令仍然会被执行，并且 `--auto-lint` 会运行仓库自己的工具。这里的离线意味着在派遣路径中没有任何东西会自行到达网络——不是沙盒阻止它。

## 循环

每个任务运行这五个步骤。步骤1、4和5需要判断；2和3是机械的。

### 1. 编写简报

Aider只能看到你发送的文本以及它在编辑范围内的文件——没有聊天历史或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁以及报告合同。每个简报保持一个任务。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

使用捆绑的辅助工具。它封装了Aider的无头 `--message-file` 模式，捕获运行，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择模型：                        添加 --model <name>
# 指向一个OpenAI兼容的服务器：  添加 --api-base <url>
# 范围编辑表面：                添加 --file <path>（可重复），--read <path> 仅用于上下文
# 干运行，未修改文件：            添加 --read-only
# 继续之前的聊天：            添加 --resume-last  (delta 简报仅)
# 硬时间限制（狗哨）：            添加 --timeout 2h  (30m 默认适合短运行；实施简报通常需要 1-2h)
# 查看所有选项：                       node .../relay.mjs --help
```

子进程的cwd固定了工作空间。简报通过 `--message-file` 传递，因此它永远不会作为参数传递：它始终保持在主机进程列表之外，并且不受操作系统参数大小限制。转发器默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞，直到Aider完成。使用协调者的后台命令功能运行它，或在shell中将其后台运行并轮询 `result.json`。运行前使用错误退出 2 并不写入结果；缺少 `aider` 退出 127 并写入 `status: "aider_unavailable"`。

相信进程状态和工作树而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。Aider的报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在stdout上）。

即使Aider从未到达模型，它也会以退出 0 结束，因此转发器会扫描运行以查找Aider自己的端点和身份验证错误，并在找到它们时报告 `status: "failed"`。将 `failed` 状态与提及端点的错误一起处理，将其视为配置问题，而不是编码失败。

### 4. 审查——不要相信自我报告

将Aider的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报对比差异，从 `touchedFiles` 开始阅读。
- 如果安装了相关的守卫技能，请运行它们。
- 在删除或重命名后进行往返迁移，并在删除或重命名后搜索悬空引用。

Aider的 `--auto-lint` 默认开启，因此它可能已经运行了linter并修复了自己的投诉。那是Aider的linter，不是你的门禁——无论如何都要运行你的门禁。参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 合并

执行者编辑工作树；**协调者提交。** 只有在门禁通过并且差异有效时才提交。如果需要重新工作，请使用 `--resume-last` 发送delta简报，然后再次审查。

## 自主性和权限

转发器传递 `--yes-always`，这是Aider自己的术语，表示自动确认每个提示，因为无头运行无法回答一个。**事先了解它同意的内容。** 自动确认适用于Aider会提出但不会提出的每个提示，并且Aider的提示不仅限于文件编辑：保持默认情况下它还会提出运行它建议的shell命令，并且 `--yes-always` 会接受这些而无人阅读。因此，转发器固定了 `--no-suggest-shell-commands`，这会移除该路径。

剩下的不是沙盒，并且这里没有任何东西假装不是这样。Aider没有权限模式，也没有隔离：在其文件范围内它可以自由编辑，并且 `--auto-lint`（默认开启）会运行仓库配置的任何linter。告诉Aider运行命令的简报仍然会运行命令。委托是授权；如果运行不能接触主机，请在容器或一次性工作树中运行它，因为此转发器中的任何标志都不会给你这种权限。

**文件选择不是安全边界。** `--file`、`--read` 和 `--subtree-only` 设置Aider放入其聊天上下文的内容，这是范围和token成本决策。它们不会限制它可以访问的内容。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

`--read-only` 映射到Aider的 `--dry-run`，它在不修改文件的情况下执行运行。转发器不会独立验证该声明——它报告 `git status --porcelain` 显示的内容，并在 `--read-only` 运行后警告树已更改。`touchedFiles` 和差异，而不是标志，是保证。

## 恢复

Aider没有会话ID。它的恢复单元是它保存在仓库中的聊天历史文件（`.aider.chat.history.md`），因此 `--resume-last` 映射到Aider的 `--restore-chat-history` 和 `--history-file` 固定一个特定的文件。由于该历史记录存在于仓库中，恢复是按工作树而不是按用户进行的：两个相同项目的克隆不会共享它。

## 授权模型

委托是人类选择进入的。一旦他们有（“运行这个队列”、“继续”），提交经过验证的门禁通过的工作就是约定的合同。仍然有两个限制：**表面，不要吸收**（报告Aider的设计决策、可辩护但未询问的转弯和非阻塞的吹毛求疵）和**停止以适应范围变化**（如果正确的完成需要超出简报，请询问而不是扩展授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、报告合同、实际门禁、文件范围和delta简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json`、轮询和失败恢复。
- [references/review-and-land.md](references/review-and-land.md) - 审查清单、提交边界以及通过Aider的聊天历史记录进行重新工作。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性检查。
