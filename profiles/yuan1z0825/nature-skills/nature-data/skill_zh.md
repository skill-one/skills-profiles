# 自然数据可用性 — 路由器

## 路由协议

对于新任务，加载以下核心和匹配资源。重用已加载的指导进行后续操作；仅在任务需要时才加载更多。

### 1. 加载清单和核心层

读取 [manifest.yaml](manifest.yaml)。然后读取 `always_load` 下列出的每个文件：

- `static/core/stance.md` — 数据可用性包是什么，默认立场以及来源层次结构。
- `static/core/workflow.md` — 八步工作流程和输出格式。

### 2. 无内容轴 — 确认期刊和语言内联

与自然写作或自然图表不同，自然数据没有片段轴。其变化在运行时处理，而不是通过加载不同的内容体：

- **期刊/文章类型** — 如果期刊特定说明与该技能冲突，则遵循期刊。
- **访问路径** — 每个数据集被分类到一个路径（公共存储库、受控访问、论文内、重用公共、第三方限制、合理请求或不适用）。
- **用户语言** — 如果用户使用中文或请求中文指导，读取 `static/core/chinese-mode.md` 并添加中文核对块，除非用户仅请求声明文本。

### 3. 运行工作流程

对于对现有声明的措辞编辑或审计，保留提供的存储库标识符和访问条件，并检查受影响的声明。报告与该声明相关的空白；不要要求全范围的数据集清单或存储库重新设计。对于新的数据共享计划、完整声明或提交审计，使用以下完整工作流程。

遵循 `core/workflow.md` 中的八步工作流程：识别期刊，清点所有支持数据集，将每个分类到一个访问路径，在起草前选择存储库和标识符策略，用明确的数据集到位置映射起草声明，添加正式数据集引用，运行 FAIR/元数据审计，并返回可粘贴的文本以及未解决的字段。

不要编造 DOI、登录号、存储库名称、许可证、 embargo 日期、伦理批准、访问委员会或数据使用条件。将“经请求可用”标记为弱，除非存在具体的法律、伦理、商业或第三方限制。

### 4. 仅在需要时查找参考文献

`references/` 下面的文件是深度参考文献，不是默认值。根据清单中的 `references.on_demand` 表格按需打开它们 — 例如 `references/policy-principles.md` 用于治理规则和边缘情况，`references/repository-and-identifiers.md` 用于存储库/登录号/DOI 选择，`references/statement-patterns.md` 用于可调整的声明，`references/fair-metadata-checklist.md` 用于 FAIR 审计，`references/chinese-author-alignment.md` 用于中文措辞，以及 `references/source-basis.md` 用于用其官方来源证明规则。

当目标是旗舰期刊 Nature 时，也打开 `references/nature-article-requirements.md` 用于声明位置、强制沉积路由、中央代码审查访问、材料和结构文件检查。

当目标是 Nature Machine Intelligence 时，打开 `../nature-shared/journal-formats/nature-machine-intelligence.md`。强制要求数据可用性声明，并在其后、参考文献之前添加单独的 `Code availability` 部分；检查审稿人访问权限、精确限制、存储库/标识符质量以及新开发的中央代码的软件提交清单。
