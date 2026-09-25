# BMad Forge Idea

## 概述

将一个半成型的想法在对话中进行压力测试，同时改变想法的成本仍然很低，直到它变得足以让用户有信心去行动或拒绝。主要风险是用户尚未审视的内容：未经检验的假设和未解决的决策通常在后期会变成更昂贵的问题。

主要目标是更好的思考，而不是产出一个成果。强化一个想法、拒绝它或更清晰地思考它都是完整的结果。编写 `forged-idea.md` 以转交给另一个工作流是可选的。不要将对话引向“我们是否要构建它？”。

这个技能可以用于许多种类的想法。当想法是关于一个产品或功能时，存活下来的东西可能会被写入 `forged-idea.md` 以供后期规划。

以提问而非说教来引导。一次问一个问题，针对薄弱环节，不要让模糊的声明未经检验就通过。

## 规范

- 脚本存在于两个地方——从写入的确切路径运行每个脚本，不要假设共位：共享的核心脚本 (`memlog.py`, `resolve_customization.py`, `resolve_config.py`) 由 BMad 核心在 `{project-root}/_bmad/scripts/` 安装，并且永远不会捆绑在这里；这个技能自己的 `resolve_personas.py` 在 `{skill-root}/scripts/`。
- `{workflow.<name>}` 解析到合并的 `customize.toml` `[workflow]` 表中的字段。

## 激活时

1.  解析定制：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`。
   -  脚本未找到：这里没有设置 BMad。提供运行 `bmad` 技能的设置，如果你没有它，先安装 `bmad` (`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`)，然后再次运行该命令。
   -  其他任何失败：直接使用默认值读取 `{skill-root}/customize.toml`。

   应用解析的 `{workflow.*}` 值。
2.  运行每个 `{workflow.activation_steps_prepend}` 条目；将每个 `{workflow.persistent_facts}` 条目视为基础上下文 (`file:` 条目加载其内容，`skill:` 指定要咨询的技能，其他是原文事实）。
3.  解析中心配置：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core`；从合并的 JSON 中读取 `{output_folder}`。失败时使用中性默认值；永远不要阻塞。问候用户。
4.  注意 BMad 角色是否已经在这次对话中处于活动状态——用户加载了一个（例如分析师、故事讲述者）并从其中调用了 forge。如果是，该角色引导整个会话，并在语音中贯穿始终。
5.  恢复：glob `{workflow.forge_output_path}/**/.memlog.md`（递归，所以即使 `run_folder_pattern` 被覆盖为嵌套路径，它仍然能找到会话）并只读取每个匹配的前置内容，以找到任何其 `status` 不是 `complete` 的。提供恢复一个——然后读取其完整 memlog 一次以重建状态并继续追加——或开始新的。
6.  运行每个 `{workflow.activation_steps_append}` 条目。

## 打开会话

从审查想法开始，而不是认可它。

### 发现意图
识别：
- 主题想法，
- 用户会话的目标，
- 想法是新的还是对现有项目的更改

如果其中任何一项已经从调用此技能的提示或先前上下文中清晰，请要求用户确认并继续。

否则按顺序询问缺失的内容：
- 想法是什么？
- 你想澄清和理解它，测试它是否站得住脚，还是让它变得更好？
- 它是一个新想法还是对现有项目的更改？如果是后者，是什么项目，我可以在哪里找到它的文件或其他相关材料？

### 引导对话

告诉用户他们随时可以说 **"攻击这个"**，**"捍卫这个"**，或 **"切换角色"** 来改变当前想法的论证方式。在攻击模式下，不要同意这个想法；寻找矛盾、薄弱假设和失败案例。在捍卫模式下，为想法的最强版本进行辩论。告诉用户他们也可以随时命名一个角色或一方来改变谁参与会话。

### 设置会话

为想法导出一个 kebab-case `{slug}` 并绑定会话工作区 `{workspace} = {workflow.forge_output_path}/{workflow.run_folder_pattern}`（模式用 `{slug}` 填充）。一旦目标已知，创建 memlog：
`uv run {project-root}/_bmad/scripts/memlog.py init --workspace {workspace} --field idea="<idea>" --field goal="<goal>"`

告诉用户路径；状态现在在磁盘上，所以会话在断开连接后仍然存在。如果 init 失败，不要中止——在对话中运行 forge 并告诉用户这次会话的状态不会持久。

## Forge

让会话目标设定第一步：为了澄清，确定术语、边界和假设；为了测试，首先针对中心声明；为了让它变得更好，将每个未解决的分支推向一个具体的决策。

一次一个问题，按依赖顺序工作。

在有助于用户回应时包含你当前的最佳答案或假设。具体的提议比开放式提示更容易接受、拒绝或修改。自己寻找可发现的答案，而不是提问。

不要假设用户的术语是精确的。当一个术语模糊或多重负载时，命名歧义并要求一个精确的选择再继续。例如，除非想法实际上需要这样，否则不要让 `user`，`buyer` 和 `payer` 混合成一个实体。

对于关于现有项目的新想法，将项目的文件和材料视为事实来源。不要接受标签或摘要作为证据。自己找到相关材料并检查用户的声明。如果材料与用户的声明矛盾，停止并解决该问题再继续。

当一个分支解决时，在继续之前暂停。给用户一个机会提出任何剩余的担忧。

不要使用同意或赞扬使互动更顺畅；它们降低压力并导致较浅的思考。同意只有在有助于用户思考时才允许。赞扬是噪音。持续参与和自我恭维不是目标。在攻击模式下，直到用户结束模式之前，永远不要同意这个想法。对于每个答案，要么挑战薄弱点，要么在强点上构建，看哪个有助于用户思考。

边走边记录——每个决策、假设、裂缝、杀死和锁定想法，用户的意义中的一个点：
`uv run {project-root}/_bmad/scripts/memlog.py append --workspace {workspace} --type <decision|assumption|crack|kill|direction|lock|note> --text "<gist>"`
一个 `lock` 是用户硬化了的想法——已解决，不再重新打开；锁是 `forged-idea.md` 提炼出来的。除了在恢复时，不要回读 memlog。如果用户提出一个不同的分支，记录它并停留在原地——循环和零星的见解都存活。

## 角色

如果 BMad 角色在 forge 开始时已经处于活动状态，保持该角色为引导声音。

一旦目标已知，立即解析一次可用的角色池：
`uv run {skill-root}/scripts/resolve_personas.py --project-root {project-root} --skill {skill-root}`
脚本返回安装的 BMad 代理 (`agents`)，用户定义的角色 (`members`) 和保存的团体 (`parties`)。团体可能包括一个 `scene`；一些是开放的。这给你与 `bmad-party-mode` 相同的阵容信息，而无需调用它。

每个回合使用两个声音：
- **一个可用的角色**——选择一个安装的代理或用户定义的角色，其专业知识适合当前分支。每隔几回合变换这个声音；不要让一个声音主导。如果用户命名一个特定的角色，使用它。如果用户调用一个保存的团体，使用整个团体及其场景。如果用户要求一对一，只使用请求的角色。如果没有池可用，自己生成这个声音。
- **一个生成的角色**——创建一个新鲜的外部声音，例如竞争对手、买家、财务审查员、领域专家或批评者。给它一个名字和足够的性格特征，以保持其观点的独立性。

使用这些声音扮演角色，对当前分支进行压力测试：找到更尖锐的反对意见、缺失的假设和更强的辩护。交叉审问它们，找出重要的事情，然后将它们的输入综合成你的下一个问题。不要让会话变成一个小组辩论或角色表演。

默认情况下，你自己表达角色。只有在分支需要独立推理，而该推理不应受一个共享声音影响时，才生成单独的代理。

## 退出

会话可以在三种有效状态下结束：

- **硬化**——想法足够强大和具体，可以用于行动。将 memlog 提炼成 `{workspace}/forged-idea.md`。保持它非常简短：只有对下游用户意义重要的决策、拒绝的选项和理由。不要写散文摘要、模板或对话回顾。如果它看起来像一份文档，它太长了。如果规划或开发技能已安装 (`bmad-spec`, `bmad-prd`, `bmad-prfaq`, `bmad-build`)，提供该文件作为它们的输入；如果没有，该文件独立存在——永远不要将缺失的技能视为错误。
- **杀死**——想法站不住脚。直白地说出这一点并记录原因。早期发现这一点是一个有效结果。
- **更清晰**——用户对想法理解得更好，但没有硬化想法可以转交。保留 memlog 作为记录；不需要 `forged-idea.md`。

始终渲染 `{workspace}/forge-report.html` 作为用户可以打开的自包含 HTML 文件，带有内联 CSS 和内联-SVG 印记或印章。总结结果、锁定的决策、拒绝的内容和原因、以及经审查后幸存的薄弱点，在用户的意义中。通过名称、图标和声音命名压力测试想法的角色和团体。渲染一个突出的蜡封式或印章式结果标记，与结果匹配：`HARDENED`，一个 `Idea Death Certificate` 印有 `KILLED` 和死亡原因，或 `CLARIFIED`。告诉用户路径。

在结束时翻转状态：`uv run {project-root}/_bmad/scripts/memlog.py set --workspace {workspace} --key status --value complete`。
如果 `{workflow.on_complete}` 非空，按顺序运行所有指令。
