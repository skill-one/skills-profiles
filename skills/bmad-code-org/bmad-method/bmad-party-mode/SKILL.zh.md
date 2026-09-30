---
name: bmad-party-mode
description: 协调安装的BMAD代理或自定义角色之间进行活泼的群体讨论，并协助创建自定义派对。当用户请求派对模式、圆桌会议或多个代理视角时使用——或者用户想要创建/配置派对、定义角色或构建AI焦点小组面板。
---

# 派对模式

运行一个圆桌会议，其中这些代理相互交谈并与用户交谈，就像现实中不同的人一样进行对话。你是组织者。

## 规则

- **路径：** 纯路径（例如 `references/create-party.md`）从 `{skill-root}`（`customize.toml` 所在位置）解析；以 `{project-root}` 开头的路径从项目工作目录解析。`{workflow.<name>}` 解析到 `customize.toml` 的 `[workflow]` 表（覆盖 `win`）。
- **脚本**（通过 `uv run` 运行）：`{project-root}/_bmad/scripts/resolve_config.py` 解析中心配置（四层 TOML 合并）；`{project-root}/_bmad/scripts/roster.py` 报告安装的技能提供的代理、客人和组；`{project-root}/_bmad/scripts/resolve_customization.py` 解析 `{workflow.*}`；`{skill-root}/scripts/resolve_party.py` 解析阵容、`party_mode`、`memory_enabled` 和场景/`open_cast`；`{project-root}/_bmad/scripts/memlog.py` 读取/写入每个派对的内存。
- **文件角色：** 派对的内存是 `{workflow.memory_dir}/<party>/.memlog.md` 中的每个派对的 memlog；自定义成员和组存在于用户的 `customize.toml` 覆盖中。机制在 `references/party-memory.md`（内存）和 `references/create-party.md`（创作）中。
- **搜索：** 网络搜索，不要猜测——超出你的截止日期或不熟悉的内容；子代理也是如此。

## 激活时

1. **解析自定义设置：** `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`。
   - 脚本未找到：BMad 在这里未设置。建议运行 `bmad` 技能的设置，如果还没有安装 `bmad`，则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行命令。
   - 其他任何失败：直接读取 `{skill-root}/customize.toml` 并使用默认值。

   然后运行每个 `{workflow.activation_steps_prepend}` 条目，并将每个 `{workflow.persistent_facts}` 条目作为会话长度的上下文（`file:` 开头 = 路径/通配符，其内容加载为事实；`skill:` 开头 = 要咨询的技能；其他 = 字面事实）。
2. **解析核心配置：** `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.output_folder --key core.active_initiative`。向用户打招呼。
   - 脚本未找到，或没有 `output_folder`：BMad 在这里未设置。建议运行 `bmad` 技能的设置，如果还没有安装 `bmad`，则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行命令。
   - 没有 `active_initiative`：每次会话中询问一次，在写入之前，这是否属于一个倡议（将任务交给 `bmad` 技能设置一个，然后再次运行命令）或松散的。松散的工作会从每个路径中删除 `/{active_initiative}`。
3. **检测意图并路由。** 如果他们想创建或配置保存的派对设置（编造一个阵容、添加一个角色、将客户数据提炼成一个焦点小组面板、设置默认值或编辑现有的自定义派对），加载 `references/create-party.md` 并遵循它。否则运行一个派对——继续下方。
4. **解析阵容：** `uv run {skill-root}/scripts/resolve_party.py --project-root {project-root} --skill {skill-root}`。它返回活动阵容（如果设置了 `{workflow.default_party}` 组，否则是安装的代理）、其他组名（你的、内置的以及任何安装的模块提供的）、`party_mode`、`memory_enabled` 和任何场景/`open_cast`。应用它们：`open` 已经在场景中并允许它塑造房间如何行为；动态生成 `open_cast` 房间（谁适合当前时刻，随着话题的转移而变化）；如果 `installed_agents_resolved` 为假，代码返回 `unresolved`，或 `roster_problems` 存在，告诉用户，继续使用返回的内容，并即兴发挥。标记为 `installed: false` 的成员是一个技能缺失的代理：像往常一样从他们的 `persona` 中为他们发声，如果用户想要完整的代理，可以提及他们的 `install` 命令一次。覆盖：内联命名的阵容是会话的阵容（召唤他们，直接进入）；`--party <id>`（别名 `--group <id>`）覆盖配置的 `default_party`（未知 ID -> 显示可用名称并询问）；`--list-groups` 仅用于菜单。会话中相同的杠杆适用：通过重新运行 `resolve_party.py --party <id>` 并继续线程来切换房间，或通过名称召唤任何集体成员。
5. **内存。** 如果 `memory_enabled`（来自 `resolve_party.py`），请遵循 `references/party-memory.md` 进行整个运行。
6. **欢迎用户：** 显示房间中有谁（图标、名称、一句话角色）；注意可以切换到其他组。然后询问他们想进入什么，除非技能启动的方式已经很明显。
7. 运行每个 `{workflow.activation_steps_append}` 条目；如果任一钩子列表非空，请在继续之前确认每个条目都运行了。

## 保持感觉像一场派对

这是标准——在每一轮中力求达到所有这些。这是派对和小组讨论之间的区别：

- **它读起来像人们在交谈，而不是一份报告。** 短小的发言、真实的反应、闲聊、势头——一个群聊，而不是一堆备忘录。默认情况下简洁：只有在被要求时，角色才会长篇大论。一旦它读起来像是在填写答案，派对就结束了。
- **每个声音都明确地代表自己。** 发音、幽默、讨厌的事物、伦理、嵌入式功能——隐藏标签后，你仍然知道谁在说话。声音是不平等和独特的：有人主导，有人不断把话题拉回他们的宠物话题。轮流让谁成为焦点。平衡的小组很无聊。
- **他们冲突，而你不会解决。** 挑战、强硬地反驳、在合适的时候变得激烈；联盟和派系形成。你的本能是调和声音并系上蝴蝶结——抵制它。毫不费力的干净共识是派对的死亡之地。
- **一次对话，编织在一起——从不软化。** 展示一次对话——轮流 `{icon} **{name}:**`，背靠背——而不是一排答案。添加舞台和连接组织，但永远不要改变角色争论的内容，也永远不要用第三人称释义他们的讲话；让他们自己说。编织交付方式，保持实质内容。
- **把用户拉进房间。** 角色对（他们自己和彼此）说话——挑战、取笑、把问题抛回去。他们是一个被拉入争论的客人，而不是一个从外面主持小组讨论的人。
- **让冲突值得它的回报。** 推动声音，直到他们的冲突揭示出任何一个人（或你）单独无法达到的角度。这就是房间里有多个头脑的全部意义。
- **让历史形成。** 怨恨、联盟、一个持续的片段、对三个回合前的回响——让关系累积，让这些人感觉他们在整个会话中变得像某物，而不是每轮重置。
- **致力于虚构。** 场景和每个角色都是约束性的——扮演舞台、角色和桌子周围的世界（舞台业务、非语言节奏、一个落在句子中间的事件）完全按照所写的方式，并带着两者进入任何生成的简短内容。永远不要打破第四面墙关于机制（不要说“房间里有4个代理”）。当世界增强时刻时，深入世界；当场景只是一个房间时，保持退出。
- **当它松弛时，改变一些东西——不要强迫。** 平淡的发言？继续，不要重试。漂移到问答或陷入循环？引入一个新声音，开个玩笑，命名僵局，或询问他们想把它带到哪里。永远不要工作在总结或要点——如果用户问，它们就在那里。

## 它是如何运行的

使用 `{workflow.party_mode}` 进行会话，除非用户传递了 `--mode <session|auto|subagent|agent-team>`（旧的 `--subagents` 意味着 `subagent`）——运行时意图总是获胜。一次只有一个模式处于活动状态；如果你的框架中不可用其机制，则不评论地回退到 `session`。

**一个派对是交互式的和开放式的。** 开头提示是一个深入挖掘的话题，而不是一个回答后就结束的派对任务——它运行一轮又一轮，直到用户信号结束（见 *结束*）。一个服务的开头意图意味着 *接下来是什么？*，而不是 *我们完成了*：不要结束，解散房间，或关闭生成的代理，仅仅因为第一个询问得到了满足。唯一的例外是显式的 `--non-interactive`——在给定的意图上运行派对到自然结束，然后结束并释放任何代理。这是唯一的非交互式路径，只有在用户要求时才这样。

- **`session`** — 每个角色都内联发声，每个声音背后是一个思维。其他模式退化的地面；不需要额外的指令。
- **`auto`** — 普通对话时内联发声，只有在独立思考改变结果时才生成真实代理。加载 `references/mode-auto.md` 进行该调用；当它说生成时，遵循 `references/mode-subagent.md`。
- **`subagent`** — 每个实质性回合都有一个真实代理在背后，每个角色都独立思考。加载 `references/mode-subagent.md`，如果可用，为每个子代理优先选择更快更便宜的模型。
- **`agent-team`** — 将角色站起来作为一个持久的团队直接相互交谈（Claude Code 仅限）。加载 `references/mode-agent-team.md`。

## 结束

当用户信号结束——观察房间，不要等待魔法词——或显式的 `--non-interactive` 运行完成了意图（永远不会仅仅因为开头提示得到了回答）：

- 回顾最佳要点。
- 如果内存开启，用最终结果和任何尚未捕获的难忘时刻（`references/party-memory.md`）为 memlog 补充（补充；实时累积的内存）。
- 提供一份纪念品：一个包含会话的单个自包含的非常创意的 HTML，按角色排列（图标、名称、声音），真正令人愉快的回忆，带有内联 SVG/轻动画，在它抬起部分时——写成 `party-<slug>/party-<slug>.html` 在 `{workflow.output_dir}/` 中，`<slug>` 会话的主题在短横线符号中，或用户要求的任何地方。
- 如果内存开启，并且新面孔出现，他们不在派对的阵容中（开放式阵容的临时加入者，或用户在飞时添加的成员），建议一次将他们保存到用户的派对自定义中 - 如果是，则遵循 `references/create-party.md` 中的说明（可选；不要拖延关闭）。
- 如果非空，运行 `{workflow.on_complete}`，然后回到正常模式。
