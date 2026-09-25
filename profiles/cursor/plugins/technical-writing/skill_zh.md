# 技术写作

目标是让一个疲惫的工程师在第一遍阅读时就能理解。四个层次能帮你达到这个目标，每个层次一个问题：这是什么类型的文档，句子如何面向读者，每个句子承载多少信息，以及任何句子是否都可以有两种解读方式。应用所有四个层次。

有三个规则位于层次之上：

- **删除每个不工作的词。** 如果句子在没有某个词的情况下仍然成立，那么这个词就可以删除。"In order to" 就是 "to"。"It is important to note that" 什么也不是。
- **使用简短、日常的词。** "Use"，而不是 "utilize"。"Help"，而不是 "facilitate"。"Do"，而不是 "perform"。一个长词必须用精确性来证明它的长度。
- **当一条规则使句子变得更糟时，用另一种方式修复句子或保持原样。** 这些规则是为了服务读者。一个遵循每条规则的句子听起来像机器写的，那么这个句子就失败了。

代码库是词汇表。写出真实的符号、文件、标志或命令名称，而不是同义词或对其的描述。

不要创造术语。使用开发者会大声说出的词："move"、"delete"、"一个只减少的预算"，而不是 "evacuate"、"ratchet" 或 "endgame"。当文档第一次说明它的含义时，命名模式是允许的。在你的回复中提议一个新的违规词及其替代词，作为 `unslop` 抽象隐喻规则的补充，并提供差异。不要编辑这项技能。

## 调整节奏

层次决定了文档说什么以及每个句子承载多少信息。文档可以遵守所有这些层次，仍然读起来像机器写的：每个句子都剪得很短，没有任何观点，没有任何具体内容。

- 故意混合句子的长度。短句要点明。较长的句子则慢慢陈述事实及其条件或后果。
- 每个句子一个想法并不意味着每个句子一个长度。将承载两个想法的句子拆分。保持承载一个想法的长句。
- 在允许的情况下有一个观点。解释权衡，所以说说你对它们的看法，而不是列出优缺点。参考保持简洁。
- 具体而不是冷漠。不是 "schema changes can cause issues" 而是 "a column rename fails the build"。

## 首先选择模式（Diátaxis）

一个文档，一个模式。两个问题选择它：内容是传达行动（做）还是理解（思考），它服务于学习还是工作？

- 行动 + 学习：**教程**。
- 行动 + 工作：**如何操作**。
- 理解 + 工作：**参考**。
- 理解 + 学习：**解释**。

在整篇文档或一个句子上使用指南针。

**教程：边做边学。** 你是老师。学习者的成功是你的工作，而不是他们的。以学习者将构建什么开头，而不是他们将 "学习" 什么。每一步都产生一个可见的结果，早期和频繁。告诉他们应该看到什么：预期的输出，提示变化，日志行。将解释削减到一个从句和一个链接。教学暂停会打断课程。保持具体。以 "我们" 的方式写作，在命令中："首先，做 x。现在，做 y。"

**如何操作：达到目标的步骤。** 解决一个人有问题的方案，而不是机器可以执行的操作。假设能力。跳过教学。只有行动：没有离题，没有背景，没有为了自身完整性而完整性。链接那些。允许分支和判断："如果你想要 x，做 y。" 以任务命名指南："How to calibrate the radar array"，而不是 "Radar array calibration"。

**参考：用于查找的事实。** 描述。只描述。没有指令，没有说服力，没有意见。保持干燥、完整和确定。用没有犹豫的语气陈述事实、选项、限制和错误。镜像所描述事物的结构，以便代码和文档可以一起导航。将材料放在读者期望的地方。尽可能从代码中生成，以便它保持真实。

**解释：理解和原因。** 一个有边界的主题，可以在产品之外阅读。每个标题都应该容忍一个隐含的 "About..." 在前面。锚定在一个真实的原因问题上。提供背景：设计决策、历史、限制、替代方案。在这里和别处允许意见。

不要混合模式：参考表格不可以在教程内，教程指导不可以在参考内，如何操作内不要争论。拆分并链接。

来源：diataxis.fr，获取于 2026-07-18。

## 面向读者写句子（Google 开发者风格）

- 以 "你" 的方式与读者交谈，使用现在时态。"Will" 只用于真正发生在之后的事情。
- 说明谁做了什么："the compiler checks"，而不是 "is checked"。只有当行为者未知或无关紧要时，被动语态才是可以的。
- 将指令写成命令："Click Submit." 平静地陈述事实。永远不要 "should be done"。
- 将条件放在指令之前："To delete the document, click Delete。" 读者会跳过不适用于他们的内容。
- 将常见情况放在前面。例外情况放在后面。
- 像一个知识渊博的朋友一样说话。没有 Buzzwords，没有比喻语言，指令中不要用 "please"，并且永远不要在程序中使用 "simply"、"easy" 或 "quickly"。如果它很简单，读者就不会在这里。
- 不要预先宣布（"we will soon support..."）并且不要开始连续的句子使用相同的短语。
- 使用说明链接去向的词：页面标题或简短描述。永远不要 "click here"。更喜欢页面上的上下文句子，而不是页面外的链接。
- 标题承载要点，而不仅仅是主题（"Pick the mode first"，而不是 "Modes"）。句子大小写。一个任务标题是一个裸动词短语（"Create an instance"）。一个概念标题是一个名词短语。每页一个 h1，不要跳过级别。
- 使用编号列表表示序列，使用项目符号表示其他所有内容。用一个完整的句子介绍列表。保持项目平行。
- 代码使用代码字体。UI 元素使用粗体。使用串行逗号。省略 "etc." 并在前面说明列表是部分的。

来源：developers.google.com/style，获取于 2026-07-18。

## 让陈述一次只加载一个（STE 规则）

- 每个句子一个指令。其他地方每个句子一个想法。
- 将长度超过大约 20 个词的指令和其他长度超过大约 25 个词的句子拆分。
- 将警告或条件放在它保护的步骤之前："If hot oil touches your skin, injuries can occur."
- 保持 "the" 和 "a"："Remove backup file" 读取两种方式。"Remove the backup file" 读取一种方式。
- 给每个词一个含义和一个工作，然后保持它。如果 "check" 意味着检查，不要也用它来表示限制。
- 为每个动作选择一个词并坚持使用："start"，而不是 "start" 这里和 "initiate" 那里。
- 将程序写成直接的命令，永远不要写成叙述，也永远不要使用被动语态："Install the component"，而不是 "the component must be installed"。
- 尽量避免 "-ing" 词。它们承担太多的语法工作，并导致误读。

来源：asd-ste100.org（问题 9，2025 年），获取于 2026-07-18。编号规则和词典存在于规范 PDF 中。上述原则是可转移的核心。

## 不要让句子有两种解读方式（全球英语）

- 保持像 "only" 和 "not" 这样的词紧挨着它们改变的词："only fails on growth" 和 "fails only on growth" 说的是不同的事情。
- 拆分长名词串："the proto import ratchet budget script" 变成 "the script that checks the proto-import budget"。
- 让每个 "it"、"they" 和 "this" 指向一个明显的东西。有疑问时重复名词。永远不要使用 "this" 或 "which" 指向一个整个子句。
- 不要省略动词："Phase 1 moves the converters and Phase 2 the runtime" 让 Phase 2 没有动词。给它一个。
- 保持显示结构的短词。"Ensure that the switch is off" 保持 "that"，因为它使句子以一种方式解析。永远不要为了字数而牺牲清晰度。
- 在系列中重复冠词，以防止误读："the client and the host"，而不是 "the client and host"，当它们是两个事物时。
- 当句子可以以两种方式分组时，说明 "and" 或 "or" 连接的部分。"Both...and"、"either...or" 和 "if...then" 是免费的消歧义器。
- 使用句号，而不是分号。用一个新句子替换一个连字符。
- 将括号中的文本作为一个完整的语法单元或其自己的句子。永远不要用 "(s)" 形成复数。
- 不要使用斜杠：写 "a, b, or both" 而不是 "a/b" 或 "and/or"。
- 在每个地方都叫每个东西一个名字。一个说 "the gate"、"the ratchet" 和 "the budget check" 的文档教了三件事。在编辑之间重写一个未更改的句子会以同样的方式成本。不要更改变未更改的内容。
- 跳过习语、俚语、拉丁缩写和隐喻。非母语读者、翻译家和代理人都最适合解析简单的结构。

来源：Kohl, The Global English Style Guide (SAS Press)。指南文本从互联网档案和 SAS 样本章节获取，2026-07-18。

## 声音和仓库特定内容

- 应用 **unslop** 技能到这个技能触及的每个文档。这项技能拥有斜坡模式目录：AI 词汇、填充、犹豫、格式提示。
- PR 描述和提交信息也是写作。除了 Diátaxis 之外的所有层次都适用。PR 正文是一个简报，审阅者可以在一分钟内阅读。不要粘贴群集日志、SHA 列表或指标表格。链接它们。
- 产品 UI 字符串不是文档。使用您产品的复制指南来处理这些。
- 使用制表符缩进代码片段。写真实的路径和真实的符号。确保每个计数或树声明在提交时都是真实的，并包括生成它的命令。

## 示例

之前：

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

之后：

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
