# 命令代码委托

你是**协调者**。这项技能让你将一个有边界的编码任务交给一个单独的**执行者**——命令代码CLI（`cmd`）——然后审查它生成的内容并亲自将其部署。
你编写简报并拥有最终判断权；命令代码在你的工作区中进行打字；你进行验证并提交。

这里没有任何内容是针对某个特定的协调代理的。这个循环只需要运行shell命令和读取文件的能力，所以无论你是Claude Code、带有选定模型的OpenCode，还是任何类似的代理，它的工作方式都是一样的。（它是为Claude Code设计的，并在Claude Code上运行；将其他协调者视为设计目标，尚未得到验证。）

## 不应使用此功能的情况

- 任务足够小，可以直接在行内完成——委托的开销不值得。
- `cmd` CLI未安装或未通过身份验证（运行`cmd login`）。
- 你想亲自编写代码，或者你只需要进行审查（命令代码有自己的`/review`）。
- 你在原生Windows上，并且`cmdc --version`无法工作。上游推荐使用WSL进行稳定的Windows使用。

## 在首次部署前阅读：自主模型

命令代码的无头模式有**恰好两个状态，中间没有任何状态**：

- **默认（无`--yolo`的`-p`）：** `read`、`grep`和`glob`有效。每个写入、编辑和shell调用都被CLI的权限层拒绝，并且无头模式在运行过程中没有提示来授予它们。这是中继的`--read-only`。
- **`--yolo`（别名`--dangerously-skip-permissions`）：** 允许所有工具，任何进程可以触及的地方都可以。没有文件系统沙盒和路径限制。这是执行运行需要的，所以中继默认传递它。

`--permission-mode auto-accept`和`--tools-all`**不会**解除无头写入门禁。直接CLI探测两者都拒绝写入、编辑和shell。所以通过命令代码执行的执行运行是完全信任的运行：用紧密的简报和干净的工作区来限制范围，而不是用沙盒。简报是指导，git worktree隔离了检出，但没有包含进程。如果目标树外的写入是不可接受的，请使用操作系统强制的沙盒，如`codex-delegate`或在此容器内运行此命令。

## 前置条件（检查一次）

1. `cmd --version`成功，并且`cmd status`报告已通过身份验证。如果不是，请安装命令代码并运行`cmd login`。
2. **确认CLI在PATH上。** 在macOS/Linux上，`command -v cmd`显示活动的`cmd`。在原生Windows上，使用`cmdc --version`；`cmd`是系统shell。中继使用`cmdc`在那里，并通过`cmd.exe`启动其npm `.cmd`包装器。`COMMANDCODE_BIN`保持绝对路径覆盖，并且永远不能指向系统命令解释器。中继在`result.json`中记录它运行的版本，所以错误的二进制文件在事后可见。
3. 你在（或将要指向`--cd`的目标）目标git仓库中，并且在部署前其树是干净的——与干净的基线相比，完全信任的运行更容易审查。

## 循环

每个任务运行这五个步骤。步骤1、4和5是你的判断；2和3是机械的。

### 1. 编写简报

命令代码只看到你发送的文本——没有仓库记忆、没有聊天历史、没有共享上下文（除了仓库自己的`AGENTS.md`，它会自动读取）。任务需要的所有内容都放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁命令（从仓库的AGENTS.md/CLAUDE.md/Makefile中查找它们——不要假设），以及报告合同。告诉它它将**不会**提交（你会）。每个简报保持一个任务。完整的指导和模板：[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 部署

使用捆绑的辅助工具将简报发送给命令代码。它包装`cmd -p`，捕获运行，并写入结构化的`result.json`——所以你唯一的工作就是“运行一个命令，读取一个文件。”（`<skill-dir>`下面是这个技能的安装目录——包含这个`SKILL.md`的文件夹，即你加载技能的目录。Claude Code在技能加载时将其打印为“此技能的基目录”；在其他协调者上使用相同的目录——如果不确定它在哪里着陆，请运行`find ~ -name relay.mjs -path '*commandcode-delegate*'`并替换它上面的目录。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 只读（审查/诊断，无编辑）：   添加`--read-only`
# 继续精确会话：               添加`--session <sessionId>`  （从result.json；只发送差异简报）
# 当没有会话ID可用时的回退：    添加`--continue-last`
# 硬时间限制（看门狗）：       添加`--timeout 2h`  （默认：关闭；执行运行通常需要1-2h）
# 查看所有选项：                node .../relay.mjs --help
```

辅助工具默认为可写运行（`--yolo`），它有意编辑目标仓库。其临时目录只保留中继工件，不包含在仓库中。中继**永远不会提交**——见步骤5。机械、标志和`result.json`形状：[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞，直到命令代码完成，所以用你的协调者提供的任何东西来支持它，并在它返回时恢复：

- **Claude Code：** 使用`run_in_background: true`运行Bash调用；你将在完成时收到通知。
- **普通shell / 其他代理：** 对于短任务，在前景运行它，或者将其后台化并轮询结果文件——bash/zsh中的`… &`，或你shell的等效项。运行完成时，当`result.json`存在并带有`status`时（预先运行的使用错误——错误的参数或空的简报——会以代码2退出，并带有stderr消息，并且不会写入结果文件，所以也要检查退出代码。缺少`cmd`二进制文件会退出127，但*确实*会写入带有状态`commandcode_unavailable`的`result.json`。）

不要相信进度跟踪器超过现实：运行完成时，当`result.json`被写入并且进程已经退出时，运行才算完成。读取工作区，而不是状态行。执行者的完整报告是`result.json`中的`finalMessage`字段（也在报告标记之间完整打印在stdout上）。

### 4. 审查——不要相信自我报告

`result.json`包括命令代码自己的摘要和门禁声明。**重新验证，不要接受：**

- **自己重新运行项目的门禁**（步骤1中的测试/检查/构建命令）。永远不要相信“门禁通过”。
- **与简报阅读差异**：它是否做了所要求的事情，没有更多（范围蔓延）和没有更少？`result`中的`touchedFiles`是你的起点——并且因为运行是完全信任的，检查简报命名的路径外的编辑，而不仅仅是路径内的编辑。
- **如果你安装了相关的守卫技能**（来自`guard-skills`的`clean-code-guard`、`test-guard`等）——这项技能生成工作；这些技能判断它。
- 对于模式/迁移更改，进行往返；对于删除，grep悬空引用。

完整的检查清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 部署它

中继永远不会提交，但它无法阻止在`--yolo`下命令代码写入`.git`。简报禁止执行者提交，并且审查者在部署前将`HEAD`与记录的预部署基线进行比较，然后再部署任何内容。**协调者提交。** 只有在门禁通过并且差异有效后：

- 自己提交经过验证的工作，并附带清晰的说明。
- 如果需要更改，请使用来自先前`result.json`的`--session <sessionId>`发送增量简报（当没有会话ID可用时，使用`--continue-last`），并再次审查。

## 只读的第二意见

中继也用作获取对抗性第二意见的干净方式：使用`--read-only`部署简报，列出同意的点，然后每个有争议的点都列出两个立场，并要求命令代码为每个点辩护或让步——以最终消息的形式交付，不触及任何文件。这里的只读保证是CLI自己的权限层，而不是操作系统沙盒，所以中继也在事后检查它：`readOnlyViolation: false`意味着Git可见检测没有看到任何更改（忽略或仓库外路径不涵盖）；`true`意味着它看到了一个；`null`意味着git无法判断。

## 授权模型

委托是人类选择进入的。一旦他们有了（“运行这个队列”、“继续”），提交经过验证、门禁通过的工作是约定的合同——这就是整个要点。对此授权有两个限制：**表面，不要吸收**（报告命令代码的设计决策、可辩护但未询问的转弯和非阻塞的吹毛求疵，而不是默默地保留它们）和**停止范围变化**（如果正确完成需要超出简报，请询问——不要自己扩展授权）。完整的处理在[references/review-and-land.md](references/review-and-land.md)中。

## 参考文献

- [references/writing-the-brief.md](references/writing-the-brief.md) — 如何编写命令代码可以盲目执行的简报：结构、XML块、报告合同、嵌入实际的门禁命令。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs`标志、`result.json`合同、每个协调者的后台化，以及当运行行为不当时恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查检查清单、提交边界和精确会话重新工作周期。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 运行顺序队列：将约束向前传递、进度跟踪和运行结束时的一致性检查。
