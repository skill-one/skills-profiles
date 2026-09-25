# 自然风格科学写作 — 路由器

## 路由协议

对于新的撰写任务，请遵循以下路由流程。对于后续编辑，请重用已建立的选项和已加载的指导；仅当请求的范围发生变化时，才读取额外的片段。

### 1. 加载清单和核心层

读取 [manifest.yaml](manifest.yaml)。它声明了轴（`task`、`paper_type`、`section`、`language`、`journal`）、允许的值以及每个值映射到的文件路径。

同时读取 `always_load` 下列出的每个文件。这些文件包含适用于每个撰写工作的默认立场、写作流程和输出格式。

### 2. 检测此请求的轴值

对于清单中的每个轴，使用清单的 `detect:` 提示和用户输入来决定值：

- `task` — 手稿 / 提交包。对于首次提交材料，使用 `submission-package`，绝不要用于修改信函。
- `paper_type` — 研究 / 方法 / 假设 / 算法 / 综述。默认：研究。
- `section` — 摘要 / 引言 / 相关工作 / 方法 / 实验 / 讨论 / 结论 / 标题。可以是多个。如果存在歧义且对草稿有影响，请询问用户。
- `language` — en 或 zh-to-en。从用户笔记本身中检测。
- `journal` — nature / nature-family / nat-comms / nat-mach-intell / generic。
  默认：generic。仅用于旗舰期刊 Nature，`nat-comms` 用于 Nature Communications，`nat-mach-intell` 用于 Nature Machine Intelligence (NMI)，`nature-family` 用于其他 Nature Portfolio 标题或未指定的 Nature-family 请求。

在草稿之前，向用户简短声明检测到的轴值，以便他们可以廉价地纠正。这是一个进度更新，不是批准关卡；除非必要的决策仍然未解决，否则继续。

### 3. 加载匹配的片段

对于每个轴值，读取清单中映射的文件。当任务为 `submission-package` 或用户明确要求无章节上下文的自由浮动参数段落时，跳过 `section` 轴。

**不要**读取 `static/` 中的每个片段。仅加载步骤 2 选择的内容。

### 4. 使用加载的材料进行草稿

按此优先级顺序应用加载的片段：

1. 核心立场 + 摄取 (`core/stance.md`) — 在草稿前表面缺失的声明 / 证据 / 边界。
2. 论文类型手册 — 论证链、草稿顺序。
3. 部分特定的撰写规则和结构。
4. 当 `task=submission-package` 时的任务特定提交规则。
5. 期刊特定的框架和约束。
6. 语言特定的句子和段落规则（最后应用）。

对于 `task=manuscript`，在请求的规模下使用 `core/workflow.md`。规划新部分或重大重构的论证；标题、单个段落或本地后续只需要适用的证据、措辞和一致性检查。完成请求的散文，除非有未解决的材料决策阻止或用户首先请求批准大纲。

当草稿或重构结果，或压缩完整手稿的主文本时，在构建段落映射之前，也加载 `../nature-shared/core/main-text-discipline.md`。按功能分类每个结果，分配到主文本、图注、方法/源数据、SI，然后草拟最短的充分证据链。不要将完整分析记录等同于完整的主文本。

当目标是旗舰期刊 Nature、Nature Communications、Nature Machine Intelligence 或其他 Nature Portfolio 标题时，加载正在草稿的章节匹配的共享 Nature 风格语料库指导：

- 结果或讨论 →
  `../nature-shared/core/nature-results-discussion.md`
- 引言或整篇手稿叙事 →
  `../nature-shared/core/nature-introduction.md`
- 摘要 → `../nature-shared/core/nature-abstract.md`

使用这些文件进行声明升级、问题链对齐、以发现为中心的压缩和综合。它们最初是从已发表的 NMI 论文提炼并作为 Nature 风格默认值泛化的；不要将其作为官方政策，并让目标期刊的当前规则覆盖它们。

对于任何讨论草稿、重构或部分审核，也加载 `../nature-shared/core/discussion-argument-language.md`。使用它来选择开篇锚点、控制反向漏斗扩展、区分文献定位与引用装饰、校准模态强度到证据，并将局限性和未来工作转化为特定声明的推理。这是通用写作指导，而不是官方期刊规则。

对于 `task=submission-package`，请遵循 `static/fragments/task/submission-package.md` 和 `references/submission-package.md`。构建交付矩阵和准备状态审核；不要将手稿段落架构强加到行政提交材料上。

如果缺少必要的证据或边界，请写一个占位符，并在 `Assumptions or missing inputs:` 下列出，而不是编造内容。

### 5. 仅在需要时才查找参考文献

`references/` 下面的文件是深度参考文献和示例库，不是默认值。根据清单中 `references.on_demand` 表格的需求打开它们。典型触发器：

- 用户要求具体示例或模板 → `references/examples/index.md`。
- 某个部分的草稿存在结构问题，而部分片段本身无法解释 → 匹配的 `references/<section>.md`。
- 用户需要一个面向广泛受众的 `Nature` 摘要开篇或询问关于 `摘要段落` → `references/nature-summary-paragraph.md`。
- 用户询问“这段话的流畅性如何？” → `references/paragraph-flow.md`。
- 用户要求自我评审或拒绝风险审核 → `references/paper-review.md`。
- 用户询问主文本、图注或 SI 中应包含的内容；想要更短的结果部分；或正在添加审稿人驱动的解释 →
  `../nature-shared/core/main-text-discipline.md`。
- 用户请求完整的首次提交包、模板或提交准备状态审核 → `references/submission-package.md`。
- 目标是旗舰期刊 Nature，且精确的提交或格式要求很重要 → `../nature-shared/journal-formats/nature.md`。
- 目标是 Nature Machine Intelligence，且精确的内容类型、提交、数据/代码或生产要求很重要 →
  `../nature-shared/journal-formats/nature-machine-intelligence.md`。
- 任何 Nature / Nature Portfolio 目标需要结果声明进展、证据约束解释、稳健性定位或讨论综合 →
  `../nature-shared/core/nature-results-discussion.md`。
- 任何目标需要讨论功能链、证据校准的模态语言、特定声明的局限性、非冗余的文献定位或不确定性驱动的未来工作 →
  `../nature-shared/core/discussion-argument-language.md`。
- 任何 Nature / Nature Portfolio 目标需要一个引言漏斗、精确的差距、文献逻辑、问题优先的新颖性、研究路线图或与结果的协调 →
  `../nature-shared/core/nature-introduction.md`。
- 任何 Nature / Nature Portfolio 目标需要一个摘要证据链、主/支持声明、数值结果或最终收益决策 →
  `../nature-shared/core/nature-abstract.md`。
- 该工作涉及监管或专业研究合规性 →
  `../nature-shared/core/research-compliance.md`。

## 提交边界

- `nature-writing` 拥有**初始提交**材料，这些材料在同行评审之前准备。
- `nature-response` 拥有修改信函、反驳意见、逐点回复、标记的手稿、申诉和其他决策后的通信。
- 将图形摘要和 TOC 图形路由到 `nature-figure`；将模拟预提交同行评审路由到 `nature-reviewer`。
