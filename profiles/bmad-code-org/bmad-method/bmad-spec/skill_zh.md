# BMad Spec
## 概述

BMad spec-kernel 生态系统的规范转换器。接受任何意图输入——模糊想法、思维导图、PRD、GDD、RFC、简报、Slack 聊天记录、客户邮件、会议记录、原型图、混合多源——并生成 **SPEC.md**，包含五字段内核（Why、功能、约束、非目标、成功信号）以及用于承载不适合内核或会膨胀内核的扩展明细内容的配套文件。它们共同构成了下游 BMad 技能所消费的机器合同。

多个技能可能随时间更新相同的规范。

## 规范

- 纯路径（例如 `assets/spec-template.md`）从技能根目录解析。
- `{skill-root}` 是此技能的安装目录；`{project-root}` 是工作目录。
- `{workflow.<name>}` 解析到 `customize.toml` 中的字段。

## 激活时

1. 解析自定义：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`。
   - 脚本未找到：此处未设置 BMad。建议运行 `bmad` 技能的设置，如果尚未安装 `bmad` 则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。
   - 其他任何失败：直接读取 `{skill-root}/customize.toml`。
2. 运行 `{workflow.activation_steps_prepend}`。将 `{workflow.persistent_facts}` 视为基础上下文（`file:` 条目被加载）。
3. 解析配置：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root}`（合并 `_bmad/config.toml` 和 `_bmad/custom/` 覆盖）。从合并的 JSON 中解析 `{project_name}`、`{output_folder}`（在 `core` 下）和 `{date}`。
4. 检测模式。**无头模式** 当任何以下情况发生时：没有 TTY、程序化调用者（另一个技能或非交互式运行器），或第一条消息预先提供所有输入并请求返回工件路径。**交互模式** 其他情况。在交互模式下，向用户打招呼，并提及 `bmad-party-mode` 和 `bmad-advanced-elicitation` 可用于任何字段的深度探索。

运行 `{workflow.activation_steps_append}`。

激活完成。如果 `activation_steps_prepend` 或 `activation_steps_append` 非空，请在继续之前确认每个条目是否按顺序执行。在所有激活步骤完成之前，不要开始主工作流。

## 工作区

规范始终是一个名为 `{workflow.spec_output_path}/{workflow.run_folder_pattern}` 的文件夹，默认解析为 `{output_folder}/specs/spec-{slug}/`。

`{slug}` 描述的是被规范化的对象，而不是输入形状：

- 源工件已包含 slug（例如 `prd-foo-bar-2026-05-23/`）：继承（`foo-bar`）。
- 稀疏、聊天中或多源输入：交互式询问；无头调用者作为输入的一部分提供它。如果缺失且无法推导，无头调用者会以 `error_code: "missing_slug"` 块。
- 相同 slug = 相同文件夹。第二次使用相同的 `{slug}` 会落在现有的规范文件夹并就地更新，保留功能 ID。

**无输入。** 交互式：要求用户共享文件路径、粘贴内容、详细解释想法或指向源。无头：以包含 `error_code: "insufficient_intent"` 的 JSON 响应。

在工作区文件夹内：

```
<spec-folder>/
  SPEC.md                  ← 大写，内核——从 .memlog.md 派生，从不手动编辑
  <companion-1>.md         ← 可选，内容类型化（例如 glossary.md）；规范编写的配套文件也派生
  <companion-2>.md
  .memlog.md               ← 规范，仅追加的内存；SPEC.md 派生自它
```

## 记忆和派生

`.memlog.md` 是规范的——一个仅追加的、按时间顺序记录每个决策、约束、功能（及其稳定的 `CAP-N`）、假设、开放问题以及用户指示的条目，每个条目按发生顺序排列，从不编辑或重新排序。`SPEC.md` 和每个规范编写的配套文件都在每次运行时从记忆日志（记录决策）以及它引用的原始内容源派生——从不手动修补。

从活着的日志中派生合同而不是就地编辑合同，这是允许规范周围的步骤（PRD、UX、架构、史诗）以任何顺序运行并输入相同的规范而不会产生合并漂移的原因：日志仅累积，工件被重新渲染。因此，规范仅通过在此重新派生来更新——bmad-spec 是它的唯一写入者；来自外部的 `SPEC.md` 手动编辑不受支持，并在下次派生时被覆盖。

写入通过共享脚本——`{project-root}/_bmad/scripts/memlog.py`（与 `resolve_customization.py` 相同的位置，原子；除了恢复外从不读取它）：

- `uv run {project-root}/_bmad/scripts/memlog.py init --workspace {spec-folder} --field topic="<正在规范的内容>"` — 创建时，一次。
- `uv run {project-root}/_bmad/scripts/memlog.py append --workspace {spec-folder} --type <decision|constraint|capability|assumption|question|direction|note|event> --text "<一句话的摘要，包括原因>"` — 每次落地时。
- 终端时刻（验证结果、"规范最终确定"）是 `--type event` 条目；记忆日志不包含状态字段。

## 操作

读取输入及其辅助链接材料。如果没有输入，请遵循 **工作区** 中的无输入分支（询问或阻止）。如果目标文件夹存在先前的 `.memlog.md`，请读取它——操作变为更新，记忆日志（而不是渲染的 `SPEC.md`）是关于已决定内容和功能 ID 的权威。保留这些 ID；新功能获得下一个未使用的 `CAP-N`；从不重用已退役的 ID。否则这是创建，第一个动作是 `memlog.py init`。

当输入结构化且预先排序（PRD 带有补充、GDD、由上游 BMad 技能生成的简报），信任编写的分离：将适合内核的内容移入 SPEC.md，将溢出内容移入命名适当的配套文件。当输入混合（思维导图、记录、RFC、客户邮件）时，自己进行排序：逐个检查声明，应用三镜头承载测试（Spec Law 规则 7），并将它们路由到内核字段或配套文件。

使用 `{workflow.spec_template}` 作为骨架，将输入蒸馏成五字段内核。当输入丰富时，直接提取——无需引导。当输入稀疏时，选择：**表达**（最佳尝试蒸馏，每个空白都成为 `open_questions[]` 条目）或 **引导**（逐个与用户一起走遍五个字段）。无头默认为表达并记录选择。交互式询问。

输入留下的已识别领域含义未解决的情况就是这样的空白——将其命名为 `open_questions[]` 条目（医疗输入对 PHI/HIPAA 保持沉默、支付对 PCI 保持沉默、控制系统对安全失效保持沉默）并继续。标记它；从不编造答案或指导它。如果这些占主导地位，输入太薄——建议 `bmad-prd`。

从第一次过中写精益：每个句子都必须证明其存在。装饰成本 token 并稀释下游读者。

将每个决策、功能、约束和接受的更改记录到 `.memlog.md` 中——那是渲染读取的运行记录。由于日志是仅追加的，较晚的条目在相同点上覆盖较早的条目，而历史记录保持完整。当两个当前活动的源或配套文件对同一字段意见不一致，或一个要么/要么从未解决时，向用户显示它而不是默默选择——解决本身就是一个新的记忆日志条目。

如果输入确实太薄无法蒸馏（例如，“为徒步者开发的应用”没有任何周围上下文），停止并建议 `bmad-prd`（或兄弟仪式技能）。这个技能蒸馏；它不指导。

## 承载

如果任何消费者（下游技能、实现代理、验证传递）会因它而改变决策，则声明是 **承载** 的。

## 配套文件

当承载内容不适合五字段内核时，它将存在于配套文件中。内核引用它；配套文件持有它。配套文件是合同的一部分；每个消费者读取 `companions:` 在 SPEC.md 前置中的内容以发现它们。配套文件遵循与 SPEC.md 相同的精益规范（Spec Law 规则 8）。

**当内容需要一个以上的内核形状行时生成配套文件**：多项目目录（例如实体的矩阵，如原型、饮料、模式、路线）、表格、图表（始终）、编辑声音规则、长格式参考材料内核通过名称引用（词汇表、棕色字段笔记、项目规范）。单行决策改变者留在约束中；意图+成功对留在功能中。如果一个内核字段开始变成子点，内容已经超出了内核并希望有一个配套文件。

配套文件要么：

- **规范编写的配套文件** 由 bmad-spec 编写并作为 **SPEC.md 的兄弟** 存在（例如 `glossary.md`、`patron-archetypes.md`）。bmad-spec 拥有它们，并在更新操作中可以编辑它们。
- **采用的** 配套文件是由上游技能编写的承载工件，下游仍然需要读取。bmad-spec 将它们引用到 `companions:` 中，但 **不编辑** 它们（例如来自 UX 运行的 `DESIGN.md` 或 `EXPERIENCE.md`、集成伙伴的 API 规范）。它们由原始技能拥有。

配套文件受两条规则管理：

1. **为规范编写的配套文件命名以反映其持有的内容类型**。`glossary.md`、`<entity-class>.md`（例如 `patron-archetypes.md`、`medication-routes.md`、`flight-modes.md`）、`stack.md`、`conventions.md`、`brownfield.md`、`architecture-diagrams.md`、`state-machines.md`、`failure-modes.md`、`compliance-references.md`。原则：“读者在打开它之前应该知道里面有什么。” 采用的配套文件保留其原始技能给它们的名称。
2. **图表始终落在配套文件中**，无论大小如何。SPEC.md 内核仅包含文本。Mermaid 块、ASCII 图表和图像引用都落在配套文件（例如 `architecture-diagrams.md`）中，从那里引用兄弟图像文件。

现有的项目范围文档（例如 `project-context.md`）如果下游需要，则列为 **采用的配套文件**，永远不会复制到 SPEC.md 或规范编写的配套文件中。

## 规范法

每个规范都必须满足这八条规则。操作旨在实现它们；自我验证扫描强制执行它们。

1. **每个功能都有 `intent` 和 `success`**。缺少任何一项 = 不是功能。
2. **意图描述“什么”，而不是“如何”**。实施处方属于配套文件（stack、conventions）。
3. **约束实际上会改变设计决策**。一个“约束”如果排除了任何可能性，就是装饰。
4. **非目标是明确的**。至少有一个。不存在意味着下游技能填补了真空。
5. **成功信号足够具体以供测试或验证**。“用户喜欢它”不合格。
6. **功能 ID 是稳定且唯一的**。从不重用，从不重新编号。
7. **保留**。每个承载来源声明都落在 SPEC.md 或配套文件中。包装仪式不保留。
8. **精益文本**。每个句子都承载承载内容。删除装饰、保留、背景故事、开场白。适用于 SPEC.md、配套文件和 `.memlog.md`。

## 自我验证

在每次创建或更新后，在呈现之前进行两次扫描结果。

**第一遍——连贯性**。根据 Spec Law 规则 1–6 和 8 判断规范。对于任何失败或感觉薄弱的内容，尝试在不编造输入未支持的内容的情况下修复它。没有直接确认的调用成为 `assumptions[]`；无法填补的空白成为 `open_questions[]`。

**第二遍——保留**。逐个检查来源声明。确认每个承载声明都落在 SPEC.md 或配套文件中。包装仪式丢弃的内容在“仅包装内容”下记录，以便记录丢弃，而不是沉默。

将每遍的结论记录到 `.memlog.md` 中（`append --type event`）。在交互模式下，与用户一起审查它。在无头模式下，`.memlog.md` 是返回的文件之一，因此调用者（或其下游 LLM）在那里读取结论。

## 无变更信号时的规范

当用户将技能指向现有规范文件夹（或其 SPEC.md）且无变更信号时，建议审查假设或开放问题，或确定他们想做什么。

## 传递到工单（可选，仅交互式）

需要 `SPEC.md` 存在磁盘上——如果不存在，请先运行正常的操作。无头运行永远不会这样做，即使调用文本要求它：如果模式检测（On Activation，步骤 4）解析为无头，请完全跳过本节并继续正常无头响应。在交互模式下，当输入读作多个独立可交付的切片时，最多提供一次传递；拒绝将结束本次运行的提议，而不是永远。

将规范文件夹传递给 `bmad-preview-ticketing` 作为需求源：它作为史诗与用户计划工作，其 `tickets.toml` 条目引用此规范的 `CAP-N` ID，并从那里运行看板。承载细节切片对话揭示的（约束、设计决策）作为规范更新返回，而不是单独返回到工单。

当规范更新运行时，在工单根目录中搜索此规范文件夹的路径在引用中；在引用它的工单中，命名描述不再匹配的条目和工单，并建议使用 `bmad-preview-ticketing` 重新切片它们。更新本身永远不会编辑工单。

## 输出

**交互式**——对话式共享规范文件夹路径。命名功能计数、生成的配套文件和结论。如果 `assumptions[]` 或 `open_questions[]` 非空，请将它们列出（简短——每行一个）并邀请用户逐个查看它们。明确指出解决它们可以更新源输入（如果是文件）、规范或两者——用户可以选择任何组合。不要转储 JSON 或呈现一堵墙的输出。

**无头**——根据 `assets/headless-schemas.md` 返回 JSON。

如果设置了 `{workflow.on_complete}`，请运行它。

## 输出规范后

规范的任何更新——解决的假设、回答的开放问题、其他更改——都是按发生顺序追加到 `.memlog.md` 中的。当更改覆盖来自源输入的内容时，建议更新该源，以便上游和规范不会默默分叉。

## 前置规范约定

- `companions:` `.md` 文件数组，下游必须与 SPEC.md 一起阅读以获得完整合同。路径可以指向规范文件夹内（规范编写的配套文件，如 `glossary.md`）或规范文件夹外（采用的配套文件，如 `../planning-artifacts/ux-designs/ux-foo-bar-2026-05-23/DESIGN.md`）。规范编写和采用的区分由路径隐式决定；下游将两者视为相同。
- `sources:` 文件路径数组，这些文件已 **完全吸收** 到 SPEC 中，没有剩余的下游价值（例如，PRD 的每个承载声明现在都在内核中）。列出以供审计，并供 bmad-spec 在更新时重新读取。下游不读取这些。下游仍然需要的文件属于 `companions:`，而不是这里。
- **不要列出** 记忆日志、README 文件、组织工件或任何上游技能生成其工件的操作记录。这些不是源内容；它们是过程元数据，下游消费者不需要。
