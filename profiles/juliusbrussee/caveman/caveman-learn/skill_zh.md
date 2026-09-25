你正在学习原始人编辑技能。 "原始人学习" 命令测量代理的 token 去向；你是将测量结果转化为编辑的授权部分——需要用户批准每个编辑。你从不声称未经测量的节省，并且你从不让代理变得更笨。

你可能看到的新汇点及其用途：
- cache_efficiency — 在缓存重用后，一百万个输入 token 实际的成本。这是一个其他汇点定价的比率，而不是一个量；永远不要将其添加到任何东西中。
- tool_output_portfolio — 主导上下文的调用形状，按排名排列。
- session_outcomes — 在其窗口中没有提交的会话中的 token 占比。相关性。将其作为观察结果呈现并大声朗读其注意事项；没有提交的会话不是浪费的会话。
- subagent_spend — 在子代理中运行的上下文占比。仅用于可见性。不要将其转化为建议生成更少的子代理。
- procedure_repeat:* — 一个蒸馏候选者。见下文 SKILL_DISTILLATION。

首先阅读计划：

1. 运行：caveman learn report --json
   解析 caveman.learn.v1 JSON。显示原始人分数、其四个组成部分以及排名的 token 汇点。对于每个汇点，说明其类别和基础。行为汇点是观察结果——将其数字作为事实呈现，将其建议柔和地呈现。不要将行为发现转化为命令。

   如果计划包含一个 `spend` 块，首先引导它：扫描窗口的成本以及缓存重用后的有效输入率（`effective_input_multiplier`）。在展示金钱时，你必须遵守的规则：
   - Spend 是窗口的成本。它永远不会是修复将返回的值。
   - 说明它覆盖的窗口。永远不要将其乘以一个月、一年或运行率。
   - 如果 `unpriced` 非空，说明总数是一个底线，并命名排除的模型。
   - 添加订阅行：在 Max/Plus/Advanced 计划上，边际成本为零，并且该数字是 token 的 API 等价值，而不是花费的金钱。
   - 永远不要称任何为已验证。

然后，仅对于用户选择采取行动的汇点，按类别运行授权循环。

在提出修复之前，你可以运行：caveman learn simulate <sink_id>。仅将其作为扫描历史中的规模显示：它对扫描历史求和，并且永远不会向前预测。

REDUCIBLE（一个沉重的 CLAUDE.md，一个永远不会调用的技能）：
- 运行：caveman learn apply <sink_id> --dry-run   （这会实现一个候选者；它不会编辑任何东西）。
- 提出一个具体的 diff 并在之前 -> 之后 token/回合显示。
- 询问用户是或否。在是的情况下，使用你自己的文件工具应用编辑。
- 重新运行 caveman learn report --json（或重新计算触摸的文件）以确认减少。这是净 token 负面门：如果之后不在之前之下，则回滚并报告。永远不要保留一个不会减少 token/回合的编辑。

RECURRING_CONTEXT（一个在会话之间重新建立的沉重块；修复类型 cavemem_offload）：将其移入 cavemem，以便它被紧凑地回忆起来，而不是每次回合都重新粘贴。候选者只包含一个 LOCATOR——永远不会包含块体。
- 运行：caveman learn apply <sink_id>   并读取它在 ~/.caveman/candidates/ 下写入的候选者 JSON。只取定位器、数字和提议的指针文本。不要信任候选者中的任何主体；没有主体。
- 你自己本地重新读取真实块：打开定位器的 rel_path，转到它的 jsonl_line，以相同的方式重新分割该回合（按空行分割，按顺序），选择 block_index，并验证原始块的 sha256 等于定位器的内容_sha256。如果不匹配，文件自扫描以来已更改——中止此项。
- 存储它：caveman mem remember -- "<the real block>"   并捕获返回的 id。`--` 结束选项解析，因此以 `---` 规则开头的块将按原样存储，而不是作为标志读取。
- 诚实地测量门。before = 块的 token/回合（它在每个回合中加载）。after = 指针的 token/回合加上召回成本。通过运行 caveman mem recall "<topic>" 并读取 hit 上的 tokens_added 来获取召回成本。如果 after 不在 before 之下，运行 caveman mem forget <id>，保留源不变，并停止。
- 修剪源并写入指针。从其 CLAUDE.md 或 AGENTS.md 部分删除块（或，对于用户手动粘贴的内容，告诉他们停止粘贴），并将候选者提议的指针文本写入其位置。指针命名召回路径：caveman mem recall "<topic>" 用于紧凑形式，caveman mem recover <handle> 用于精确的字节原始形式。
- 永远不要让代理变得更笨：在你完成之前，确认 caveman mem recall "<topic>" 返回命中并且指针已就位。如果召回返回空，或者你没有写入指针，则 REVERT（caveman mem forget <id> 并恢复源）。在没有工作召回路径的情况下删除上下文是这个保护机制存在的唯一失败点。
- 重新测量并报告确认的减少和召回路径。

SKILL_DISTILLATION（一个 procedure_repeat 汇点；修复类型 skill_distillation）：用户在会话之间重复的一系列工具步骤。将其记录为技能可能会阻止代理重新推导它——但是技能在每个会话中都加载到前缀中，并且只有在会话中命中模式时才会偿还。这是此报告惩罚的 dead_load 汇点的相同形状，因此它的评分不同，你必须不能走捷径。
- 永远不要通过净 token 负面门应用此修复。该门重新计算文件；它看不到成本和收益落在不同的地方。
- 首先显示候选者：步骤、它在多少个会话中重复、以及这些跨度消耗的 token。直白地说，回报尚未得到证明。
- 如果用户想要它，编写技能，然后在同一句话中开始一个保留：caveman learn experiment start <label> --sink <sink_id> --fix-kind skill_distillation
  告诉他们它是如何工作的：将其保留一段时间，然后运行
  `caveman learn experiment arm <label> off` 并在不使用它的可比时间段内工作。每个臂至少需要 5 个会话才能存在任何结论。
- 使用 `caveman learn experiment report <label>` 读取结果。`insufficient_data` 判决意味着继续——永远不要将其呈现为一个小胜利。`regressed` 判决意味着删除技能；直接说明。
- 承轨比较每个会话的中位数 token。如果它标志在臂上每回合遇到更多工具错误，首先引导这一点：一个更便宜的会话失败更多并不是节省。

LOAD_BEARING：永远不要触摸。它仅在报告中出现，以便分数保持诚实。

报告节省（caveman learn savings）：

账本显示了应用修复后返回的内容，按其测量方式分组。当你展示它时，分组不是装饰——它是声明强度：
- deterministic_remeasure — 我们编辑的文件被重新计数。最强的本地运行等级。
- controlled_holdout — 在本机上的更改前后测量。
- counterfactual_replay — 带有更改实际历史重跑。
- interrupted_time_series — 会话前与会话后，没有控制臂。

三条规则，全部具有约束力：
- 永远不要跨等级求和，并且永远不要呈现一个单一的混合节省标题。重新计数的文件和会话中位数不是同一种证据。
- 始终读取你作为胜利呈现的行的 `confounders`。它们是站立的警告，不是小字，并且它们确实存在是为了好消息的情况。
- 读取 `attribution.provenance`。`intact` 意味着文件仍然携带我们提议的编辑。`changed_since` 意味着有人编辑了它之后，并且部分 delta 不是我们的——说明。`target_missing` 意味着 delta 无法与修复关联。永远不要将 `changed_since` 或 `target_missing` 行呈现为原始人结果。

回归在设计上不包含美元金额。使用其判决展示它，并提供回滚路径；不要软化它，也不要省略它。

约束规则：
- 每个编辑的授权。没有“全部应用”会隐藏单个 diff。
- 在编辑应用并且其重新测量门通过后，运行：caveman learn applied <sink_id>。未来的学习运行使用它来报告纵向判决：改进、未改变、回归或 insufficient_data。诚实地呈现回归并提供该编辑的确切回滚路径。
- 每个编辑都是可逆的：准确报告你更改了什么。卸载通过 caveman mem forget <id> 加上恢复修剪的源来撤销。
- inferred 仅。永远不要将本地数字作为已验证呈现。货币仅在报告本身携带它（`spend` 和定价节省行）并且该块自己的框架保持完整的情况下允许——窗口限制，永远不会预测，永远不会验证。
- 分析器（caveman learn）是只读的。你是唯一的写入者，并且只有在说是之后。
