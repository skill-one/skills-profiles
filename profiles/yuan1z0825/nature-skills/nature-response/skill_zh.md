# Nature Reviewer Response — 路由器

## 路由协议

对于新任务，加载以下核心和匹配资源。重用已加载的指导文件用于后续任务；仅在任务需要时才加载更多。

### 1. 加载清单和核心层

读取 `[manifest.yaml](manifest.yaml)`。然后读取 `always_load` 下列出的每个文件：

- `static/core/stance.md` — 面向编辑器的目的、默认立场、红线以及适用于每个响应任务的内容层级结构。
- `static/core/workflow.md` — 接受的输入、修订对应工作流以及输出包格式。

### 2. 无内容轴 — 在行内识别模式和语言

与 nature-writing 或 nature-figure 不同，nature-response 没有片段轴。其变化在运行时识别，而不是通过加载不同的内容体：

- **任务模式** — `draft` / `audit` / `revise` / `triage-only` / `cover-letter` / `revision-package` / `latex-template` / `appeal-like`。
- **决策类型** — 轻微修订、重大修订、修改后重投、评审后转移或不确定。
- **用户语言** — 如果用户使用中文，也生成中文核对 block。

决策类型对于新包级修订策略或完整响应包是必需的。
首先从编辑信或任务上下文中提取它。如果仍然不明确，询问这是 `Major Revision` 还是 `Minor Revision` 并仅暂停决策相关的任务。本地措辞编辑、现有回复的审计或评论级分派可以标记决策类型为未知。不要从评审人评论的数量、语气或难度中推断决策。

使用 `references/intake-and-routing.md` 在起草前固定任务模式、最小输入和准备状态。单独路由类似申诉的案例；不要将申诉作为默认路径起草。

对于本地编辑或有限范围的审计，返回修订的段落或发现以及相关的缺失事实。除非要求，否则不要将其扩展为主跟踪器、封面信或完整修订包。仅将以下包工作流应用于请求的输出所需的部分。

### 3. 运行工作流

遵循 `core/workflow.md` 中的工作流：如果用户粘贴了期刊邮件，首先从邮件中解析稿件元数据、决策类型、编辑指令、评审人报告、所需文件、截止日期和评审人可见性规则；识别模式并通过决策类型关卡；应用重大或轻微修订策略而不降低单个评论的严重性；提取编辑指令（ID `E.1`）和评审人评论（`R1.1`，`R2.1`）时存在；按响应动作和独立验证的工作状态对每个项目进行分类；构建内部/编辑器主策略和跟踪器；为每个相互盲审的评审人起草独立的隐私过滤响应；当评审人遗漏的稿件中已存在的内容，将其视为清晰信号并修订呈现方式，而不是回复该点已陈述；在需要时起草修订封面信；将每个声称的变更映射到稿件位置或显式占位符；在编辑时在备份副本上将修改的稿件文本标记为红色；在响应信中将引用的修订稿件文本格式化为斜体；标记缺失的作者输入；运行 QA；并根据每个项目的状态和阻塞状态推导包准备状态。

每当响应建议或执行稿件正文编辑时，也加载 `../nature-shared/core/main-text-discipline.md`。在信中完全回答评审人，但将稿件变更保留为读者所需的最短文本。优先考虑替换或压缩，除非它改变了中心解释，否则将非中心稳健性或协调细节路由到 SI。

永远不要编造实验、引用、行号、图面板、补充项、编辑指令或稿件变更。将作者必须提供的任何内容标记为 `AUTHOR_INPUT_NEEDED`。

### 4. 仅在需要时参考

`references/` 和 `templates/` 下的文件是深度资源，不是默认值。根据清单中 `references.on_demand` 表的需求打开它们 — 例如 `references/comment-taxonomy.md` 用于评论分类，`references/action-mapping.md` 用于跟踪器字段，`references/tone-and-stance.md` 用于分歧措辞，`references/difficult-cases.md` 用于不可能的实验 / 冲突的评审人 / 类似申诉的案例，`references/chinese-author-alignment.md` 用于中文作者注释，`references/latex-templates.md` 用于 `.tex` 封面/响应/修订输出，`../nature-shared/core/main-text-discipline.md` 用于评审人驱动的稿件添加和证据重新定位，`references/package-consistency-audit.md` 每当稿件与信件一起编辑或包即将编译和交付时，以及 `references/qa-checklist.md` 在最终确定之前。

`qa-checklist.md` 和 `package-consistency-audit.md` 是互补的，并且都适用于最终包：前者询问响应是否完整、诚实和语气良好；后者询问编辑后标记的稿件、干净的稿件和信件是否彼此一致。对于 LaTeX 包，在第一个完整草稿后、每次稿件编辑后和交付前立即运行 `scripts/check_package_consistency.py`。任何稿件编辑都会使信件的逐字引用和页码引用失效，因此重新运行审计，而不是将其视为一次性最终检查。
