# no-mistakes

`no-mistakes` 是一个本地网关，它在代码变更通过管道（意图、变基、审查、测试、文档、代码检查、推送、拉取请求、持续集成）到达配置的推送目标之前对其进行验证。您通过 `no-mistakes axi` 命令系列来驱动它，该命令系列将机器可读的 [TOON](https://toonformat.dev) 打印到标准输出，并将进度打印到标准错误。

## 活跃的验证步骤边界

一个 no-mistakes 验证步骤代理已经在一个活跃的外部运行中。它必须检查、修复并仅返回其分配的阶段。它永远不能初始化、启动、重新附加、重新运行、响应、同步、中止、弹出或直接推送 no-mistakes 管道。用户意图中的交付要求仍然是接受上下文，但外部执行者单独执行其他验证、推送、拉取请求和持续集成阶段。

`NO_MISTAKES_GATE` 是快速诊断证据，本身不是授权。运行时结合了管理的 Git 身份和经过身份验证的进程祖先。如果一个管道控制命令返回 `error.code: nested_gate_context`，请立即停止并返回控制权给外部执行者。通过 `no-mistakes axi status`、`no-mistakes axi logs`、帮助和 `no-mistakes doctor` 仍然可以安全地进行检查。

当用户调用 `/no-mistakes` 时，在末尾报告结果。如果用户要求特定内容，请自己将请求转换为匹配的 `axi run` 标志——例如，“跳过代码检查步骤”变为 `--skip=lint`。运行 `no-mistakes axi run --help` 查看可用的标志。

## 两种调用方式

`/no-mistakes` 在两种模式下工作，具体取决于用户是否在命令中提供了任务：

- **仅验证** - 纯 `/no-mistakes`（可选带有标志式请求，如“跳过代码检查步骤”）。用户的代码变更已经提交；验证它们并报告结果。
- **任务优先** - `/no-mistakes <任务>`，例如 `/no-mistakes 为状态命令添加一个 --json 标志`。首先自行执行任务，然后通过管道验证结果：
  1. **检查范围**。在更改或提交任何内容之前检查 `git status`。保留与任务无关的现有未提交更改，并在提交时仅提交属于用户任务的变化。
  2. **执行工作**。进行任务描述的更改，然后**在特性分支上提交它们**。如果用户位于存储库的默认分支上，请首先创建一个特性分支——网关验证非默认分支上的已提交历史记录，因此工作必须在运行之前到达那里。
  3. **然后验证**，将用户的任务作为 `--intent` 传递。任务文本是用户打算完成的内容，用他们自己的话表达，因此它就是意图——保留用户直接提出的所有要求，包括约束、排除、验收标准以及后续决定；不要将它们浓缩为差异摘要或在添加实现上下文时删除它们。用你在执行工作过程中做出的决定和权衡来丰富它（见 [意图是必需的](#intent-is-required)）。

## 测试质量规则

永远不要添加一个其唯一证据是打开、读取、grep、解析或快照实现源代码并找到或省略特定字符串、标记、行、命令、函数名、提示短语、正则表达式匹配、抽象语法树形状或偶然快照的测试。这并不能证明行为：匹配的文本可能是无效的或被注释掉的，并且行为保留的重构可能会改变它。

相反，执行公共或可执行接口并断言可观察的行为、状态、输出、副作用和失败模式。对于机器消费的声明性工件，如工作流 YAML、JSON、策略、.gitignore 或生成的配置，在可行的情况下调用实际消费者，或者解析为类型化或归一化的语义模型并断言含义。文件中的原始子字符串或正则表达式仍然是反模式。

当文件本身是生成的公共输出、序列化协议、持久状态、有意快照或另一个显式拥有的文本或字节合同时，读取文件是合法的。命名该合同，并且不要使用其内容作为无关代码工作的代理。自然语言提示或指令并不能因为其源包含一个句子而被证明是有效的。确定性持续集成可能会测试最终发出的提示作为代理有意生成的接口；模型解释属于开发评估，而不是实时 LLM 持续集成。

对于回归，在可行的情况下重现报告的失败：测试应在修复之前失败，并在修复后通过。

以下所有内容——先决条件、意图、验证和决策循环——一旦工作提交到特性分支，都以相同的方式适用。

## 开始之前

- 您要验证的工作必须**提交**到一个分支上。网关验证已提交的历史记录，而不是您的未提交工作区。
- 您必须在一个**特性分支**上，而不是存储库的默认分支上。
- 存储库必须已经使用 `no-mistakes init` 初始化。
- 守护进程必须有一个可运行的配置管道代理：一个受支持的本地代理二进制文件、`agent: cursor` 或 `agent: devin` ACP 别名，或通过 `acpx` 显式的 `acp:<目标>`。您是 AXI 驱动器，而不是隐式的管道代理后端。如果没有可用，运行会在第一步之前失败；`no-mistakes doctor` 会报告配置问题。

如果任何这些不满足，`axi run` 会返回一个 `error:`，其中包含修复它的确切命令——阅读它并采取行动（提交您的工作或创建一个分支）。如果存储库未初始化，请先运行 `no-mistakes init`；如果 `no-mistakes` 命令本身丢失或行为异常，`no-mistakes doctor` 会报告出错了。
开始之前，运行 `no-mistakes axi`（主页视图）。
如果它显示您当前分支上有一个活跃的运行，请使用 `no-mistakes axi status` 检查它。
如果它在网关处停泊，请使用 `no-mistakes axi respond` 驱动它。
通过重新运行 `no-mistakes axi run` 重新附加正在进行的运行，当它仍然与您当前的 `HEAD` 匹配时——无论是提交的头部还是当前管道头部。
只有在您打算在重新开始之前丢弃该运行时，才使用 `no-mistakes axi abort`；中止是在运行之间进行的操作，永远不会在运行仍在进行时接管或绕过网关（见 [验证和决策](#validate-and-decide)）。
如果它显示另一个分支上有一个活跃的运行，请让该运行保持原样，并使用 `no-mistakes axi run --intent "..."` 在您当前的分支上开始验证。

## 意图是必需的

当您启动运行时，必须传递 `--intent`：**用户打算完成什么**——这项工作的目标或请求，用他们自己的话表达。这不是对差异或您更改的文件的描述；它是变更旨在实现的目标。您从对话中知道它，因此直接传递它——`no-mistakes` 使用它原封不动，而不是从本地代理转录中推断它（更慢且更不稳定）。

倾向于完整性而不是简洁性。审查步骤使用 `--intent` 来区分有意决策和错误，因此简短的摘要会使用户已经选择的项被标记为错误。捕捉细微差别：用户的目標、他们沿途做出的特定决定和权衡、他们排除或纳入的任何约束或方法，以及他们明确要求但可能在差异中看起来令人惊讶的任何内容。几句话到一段简短的段落是正常的——写下您从对话中学到的，而只有阅读差异的审查者才不知道的内容。

## 验证和决策

运行管道并随着其出现对结果做出决定：

1. 启动运行。它会阻塞，直到第一个决策点或结束：
   ```sh
   no-mistakes axi run --intent "<用户打算完成什么>"
   ```
   `axi run` 和每个 `axi respond` 都会同步阻塞——审查、测试和持续集成步骤每个可能需要**几分钟**，因此一次调用可能不会很快返回。这是正常的；不要因为看起来慢而取消或重新发出命令。两者默认为 `--wait 8m`，因此具有 10 分钟工具上限的 harness 会得到结构化返回而不是无限期挂起。如果命令因为等待超时而返回，它不是失败的运行，也不意味着守护进程已死：使用 `no-mistakes axi status` 检查，并重新运行 `axi run` 或 `axi respond` 重新附加。慢速的实时守护进程会在健康探测后重新尝试，而不是将其视为 I/O 失败。要在不影响运行的情况下检查进度，请从单独的调用中使用 `no-mistakes axi status`。

   一个长时间运行的调用是在工作，而不是停滞——如果您的 harness 需要，可以将其置于后台，但运行**永远不会自行越过网关**。阅读每个返回；在 `gate:` 上，响应；循环，直到 `outcome:`。永远不要闲置等待运行自行前进。
   当状态输出在运行下包括 `awaiting_agent: parked <持续时间>` 时，运行在批准或修复审查网关处停泊，并等待您发送 `axi respond`。该字段仅用于可观察性：它不会改变网关分辨率、自动恢复运行或使 `--yes` 成为默认值。
   当一个步骤处于 `running` 或 `fixing` 状态时，`axi status` 可能包括一个 `active_steps` 表。`active_for` 是包含步骤的持续时间；`round_active_for` 是显示的执行或修复轮持续时间，并在修复轮中重置。没有轮时间信息的旧运行将 `round_active_for` 留空。
   `help` 列表位于大多数响应的底部，告诉您要运行的下一个命令。
   错误会作为 `error: ...` 打印到标准输出，并附带一个 `help` 列表；根据建议采取行动。
   退出代码：`0` 成功、无操作或正常决策网关，`1` 失败或取消的最终结果，`2` 坏使用。

一个等待您的 `gate:` 大致如下所示——一个命名步骤的 `gate:` 行、可选的步骤特定字段（如 `note`）、一个包含每行一个查找的 `findings[N]{...}:` 表，以及一个包含下一个命令的 `help[N]:` 列表：

```
gate: review
note: Review auto-fix is disabled by default (auto_fix.review: 0; a repo or global auto_fix.review > 0 override re-enables it), so blocking and ask-user review findings park for your decision rather than being silently self-fixed.
findings[2]{id,severity,file,line,action,description}:
  r1,warning,internal/pipeline/executor.go,,auto-fix,Error from os.Remove is ignored
  r2,error,cmd/no-mistakes/main.go,,ask-user,New --force flag bypasses the confirm prompt
help[6]:
  Run `no-mistakes axi respond --action approve` to accept this step and continue
  Run `no-mistakes axi respond --action fix --findings <ids>` to have the pipeline fix the selected findings (do not edit files yourself)
  Run `no-mistakes axi respond --action skip` to skip this step
  Run `no-mistakes axi logs --step review --full` to read the full step log
  A long-running call is working, not stalled - background it if your harness needs to, but the run never advances past a gate on its own. Read every return; on a `gate:`, respond; loop until an `outcome:`.
  Commit post-pipeline follow-up work on top of the existing branch so every pipeline fix commit remains present. Never abort-and-restart, reset, or replace the branch in a way that drops prior gate-fix commits.
```

逐行阅读 `action` 列：根据自己的判断决定 `r1`（auto-fix）——`respond --action fix --findings r1` 将其交给管道进行修复——但停止并将 `r2`（ask-user）提升给用户，然后再响应。最终状态
显示 `outcome: <checks-passed|passed|passed-with-override|passed-with-skips|failed|cancelled>`，没有 `findings` 表。字段名和确切列可能因步骤和版本而异，因此请阅读实际的 `findings` 标题，而不是假设此布局。
