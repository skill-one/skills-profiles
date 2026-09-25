# OpenCode 委托

你是**协调者**。这项技能让你可以将一个有边界的编码任务交给一个独立的**执行者**——OpenCode CLI，然后审查它生成的内容并自行完成。你编写简报并拥有判断权；OpenCode在自己的会话中进行打字；你进行验证并提交。

这里没有什么是针对某一个协调代理的特定内容。这个循环只需要运行shell命令和读取文件的能力，因此任何具有这两种能力的代理——Claude Code、驱动兄弟会话的OpenCode或可比较的代理——都可以驱动它。（它是为Claude Code设计的，并在Claude Code上运行；将其他协调者视为设计目标，尚未得到验证。）

## 不应使用此功能的情况

- 任务足够小，可以直接在行内完成——委托的开销不值得。
- `opencode` CLI未安装或未进行身份验证（运行`opencode auth login`）。
- 你想自己编写代码，或者你只需要进行审查（使用通过`--read-only`的`plan`代理）。

## 前提条件（检查一次）

1. `opencode --version`成功。如果不是，请安装（`npm i -g opencode-ai`，或从opencode.ai下载原生安装程序）并运行`opencode auth login`。
2. **确认`opencode`是否在PATH中**。`command -v opencode`显示活动二进制文件，`opencode --version`显示其版本。中继记录它运行的版本到`result.json`中，因此过时的二进制文件在事后可见。
3. 一个模型提供程序已进行身份验证——`opencode auth list`显示至少一个凭证。
4. 你位于（或将要指向`--cd`的）目标git存储库。

## 选择执行者模型

OpenCode没有**安全的默认值**——一个简单的`opencode run`会出错——因此新的运行需要一个通过`--model`或设置一个模型的`--lane`（恢复的运行会继承其会话的模型）。命名模型是单一模型后端（如codex-delegate）从未有的一个决定，它有两个所有者：

- **人类拥有允许哪些模型**。`opencode models`列出了数百个条目，大多数按token计费（如OpenRouter等）；只有人类知道哪些是他们的固定费率订阅，而CLI无法区分它们。因此可用的集合是他们的——理想情况下，在存储库的`AGENTS.md`或他们的`CLAUDE.md`中一次性声明（例如，“将机械工作委托给`opencode-go/…`，将硬逻辑委托给`…`”）。
- **你，作为协调者，为每个任务选择——从那个集合中**。根据简报匹配模型：一个便宜、快速的模型用于机械扫描（重命名、迁移、删除）；一个强大的模型用于微妙错误或金钱/安全路径。
- **如果没有声明可用的集合，请询问——不要猜测**。从目录中猜测有导致计费模型和意外账单的风险。向人类命名约束，让他们选择。

更多深度：[references/writing-the-brief.md](references/writing-the-brief.md)。

## 循环

每个任务运行这五个步骤。步骤1、4和5是你的判断；2和3是机械的。

### 1. 编写简报

OpenCode只能看到你发送的文本以及它可以从工作树中读取的内容——没有聊天历史记录，没有共享上下文。任务所需的所有内容都应放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门控命令（从存储库的AGENTS.md/CLAUDE.md/Makefile中查找它们——不要假设），以及报告合同。告诉OpenCode它将**不会**提交（你会）。每个简报保持一个任务。完整指南和模板：
[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

将简报与捆绑的辅助工具一起发送给OpenCode。它包装`opencode run`，捕获运行，并写入结构化的`result.json`——因此你唯一的工作是“运行一个命令，读取一个文件。”（`<skill-dir>`下面是这个技能的安装目录——包含这个`SKILL.md`的文件夹。Claude Code在技能加载时将其打印为“此技能的基础目录”；在其他协调者处使用同一个目录——如果不确定它在哪里，请运行`find ~ -name relay.mjs -path '*opencode-delegate*'`并替换它上面的目录。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --model <provider/model> --cd /path/to/repo
# --model（或设置模型的--lane）在新的运行中是必需的
# fleet lane from delegate-setup:           添加--lane <name>  (dials apply; flags still win)
# read-only (审查/诊断，无编辑):   添加--read-only   (使用plan代理)
# 继续之前的OpenCode会话:   添加--resume-last  (delta brief only; keeps the model)
# 硬时间限制（watchdog):               添加--timeout 2h  (默认：关闭；常规运行需要1-2h)
# 查看所有选项:                          node .../relay.mjs --help
```

辅助工具默认为可写入的`build`代理，并将其工件写入临时目录，因此正在审查的存储库保持干净。它**永远不会提交**——见步骤5。机制、标志和`result.json`的形状：[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到OpenCode完成，因此用你的协调者提供的内容支持它，并在返回时恢复：

- **Claude Code**：使用`run_in_background: true`运行Bash调用；你将在完成时收到通知。
- **纯shell / 其他代理**：对于短任务，在前景运行它，或者将其后台化并轮询结果文件——`… &`在bash/zsh（包括Git Bash/WSL），或你的shell的等效项（`Start-Job`在PowerShell，`start /b`在cmd）。运行完成时，当`result.json`存在并带有`status`时（预先运行的使用错误——错误的参数或空的简报——会以代码2退出并写入没有结果文件，因此也要检查退出代码。缺少`opencode`二进制文件会退出127，但*确实*会写入带有状态`opencode_unavailable`的`result.json`。）

不要信任进度跟踪器超过现实：运行完成时，当`result.json`被写入并且进程已退出时。读取工作树，而不是状态行。执行者的完整报告是`result.json`中的`finalMessage`字段（在报告标记之间在stdout上完整打印）。

### 4. 审查——不要相信自我报告

OpenCode的`result.json`包括它自己的最终消息和任何门控声明。**重新验证，不要接受：**

- **自己重新运行项目的门控**（步骤1中的测试/检查/构建命令）。永远不要相信“门控通过”。
- **与简报阅读差异**：OpenCode是否做了所要求的事情，没有更多（范围蔓延）和更少？`result.json`中的`touchedFiles`是你的起点。
- **如果你安装了相关的门控技能**，在差异上运行它们（来自`guard-skills`的clean-code-guard、test-guard等）——这项技能生成工作；这些技能对其进行判断。
- 对于模式/迁移更改，进行往返测试；对于删除，grep悬空引用。

完整清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

执行者编辑工作树；**协调者提交**。提交应该是验证工作的一方采取的行动。只有在门控通过并且差异有效后：

- 自己提交已验证的工作，并附带清晰的说明。
- 如果需要更改，使用`--resume-last`发送delta简报（不要重新陈述整个任务）并再次审查。

## 自主模型

OpenCode的自主权由**代理**管理，而不是沙盒枚举：

- **`build`**（中继默认值）——可写入；无头地在工作目录中编辑文件。相当于“让它实现”。
- **`plan`**（通过`--read-only`）——只读；审查和诊断而不触摸树。相当于“让它查看但不编辑”。

权限**默认自动批准**：中继传递`--auto`，因此无头运行永远不会在没有人可以回答的提示上阻塞。这就是未attended委托的目的——协调者的差异审查和执行者扫描（步骤4）是安全网，而不是每个操作的提示。传递`--no-auto`以尊重代理自己的权限配置（每个操作允许/询问/拒绝）；将其与工作空间权限设置为*允许*的代理配对，或者无头运行可能会等待`ask`而挂起。**只读（`plan`）运行永远不会获得`--auto`**——自动批准会让plan代理的ask-gated编辑/bash权限通过并破坏“只读”，因此审查不能被欺骗为触摸树。

## 授权模型

委托是人类选择进入的。一旦他们有了（“运行这个队列”，“继续”），提交已验证、门控通过的工作就是约定的合同——这就是整个要点。对此授权有两个限制：**表面，不要吸收**（报告OpenCode的设计决策、可辩护但未询问的转弯，以及非阻塞的吹毛求疵，而不是默默保留它们）和**因范围变化而停止**（如果正确完成需要超出简报，请询问——不要自己扩展授权）。完整讨论在[references/review-and-land.md](references/review-and-land.md)中。

## 参考文献

- [references/writing-the-brief.md](references/writing-the-brief.md) — 如何编写OpenCode可以盲目执行的简报：结构、XML块、报告合同、嵌入实际门控命令。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs`标志、`result.json`合同、根据协调者后台运行，以及当运行行为异常时的恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界，以及通过`--resume-last`的重新工作周期。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 运行顺序队列：将约束向前传递、进度跟踪，以及运行结束时的连贯性检查。
