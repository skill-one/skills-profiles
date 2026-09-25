# ARS-Codex

这是一个用于ARS套件的Codex适配器。ARS内容存储在`ars/`下；将其作为源材料，并首先通过此文件。

## 版本控制

此Codex包的版本是`3.22.0`。仓库根目录`VERSION`、此`SKILL.md`元数据版本以及`manifest.json`的`adapter_version`必须匹配。从`3.22.0`开始，此版本号也与打包的ARS套件匹配。确切的上游版本、标签和提交记录在`manifest.json`中记录；历史`0.1.x`包发布保留其原始编号。

## 第一条规则

默认情况下不要加载整个套件。选择一个工作流，读取该工作流的`WORKFLOW.md`，然后仅加载用户当前阶段所需的代理、参考、模板或共享文件。

内部工作流条目文件命名为`WORKFLOW.md`，而不是`SKILL.md`，因此Codex仅注册此根路由技能，而不是将每个打包的上游工作流作为单独的技能公开。

## 工作流路由器

根据意图选择工作流：

| 用户意图 | 首先读取 |
|---|---|
| 深入研究、文献综述、系统综述、荟萃分析、事实核查、研究问题完善 | `ars/deep-research/WORKFLOW.md` |
| 学术论文写作、论文大纲、摘要、修订、引用格式化、AI披露、LaTeX/DOCX/PDF格式指导 | `ars/academic-paper/WORKFLOW.md` |
| 论文评审、同行评审模拟、编辑决策、评审员校准、修订后的重新评审 | `ars/academic-paper-reviewer/WORKFLOW.md` |
| 端到端研究到论文管道、完整性门禁、分阶段评审/修订/最终化工作流 | `ars/academic-pipeline/WORKFLOW.md` |
| 实验规划、代码实验执行计划、人体研究方案、统计分析、可重复性验证 | `ars/experiment-agent/WORKFLOW.md` |

如果请求跨越多个工作流，除非用户明确要求单个阶段，否则从`ars/academic-pipeline/WORKFLOW.md`开始。

### 西班牙意图路由

使用与打包的西班牙语触发短语相同的意图边界：

| 西班牙语意图 | 工作流和模式 |
|---|---|
| 文献综述 / 系统综述 / 荟萃分析 | `deep-research`: `lit-review` / `systematic-review` |
| 指导我的研究 / 帮我推理 | `deep-research`: `socratic` |
| 评审论文 / 评审这篇文章 / 同行评审 | `academic-paper-reviewer`: `full` |
| 修改我的论文 / 修改我的论文 | `academic-paper`: `revision` |
| 收到评审员评论 / 评审路径 | `academic-paper`: `revision-coach` |
| 写摘要 / 核实引用 / 转换格式 | `academic-paper`: `abstract-only` / `citation-check` / `format-convert` |
| 文献综述论文 | `academic-paper`: `lit-review` |
| 学术工作流 / 研究到论文 | `academic-pipeline`: `pipeline` |

保持评审和修订意图区分。对西班牙语中模糊的论文主题应用主题范围，明确的研究问题允许直接规划。这些激活短语不会添加支持的语言对。

### 论文主题范围覆盖

在一般论文/管道路由规则和Claude风格别名路由器之前应用此覆盖。无论用户是通过自然语言还是通过`ars-*`别名调用ARS，此覆盖都适用。

如果用户说他们想写论文、论文、提案、文章、期刊文章或手稿，但他们只提供了一个广泛的主题、暂定标题、研究兴趣或“题目/主题/方向”，并且**没有**提供一个清晰、可回答的研究问题，请首先将路由到`ars/deep-research/WORKFLOW.md`的`socratic`模式。这匹配了上游ARS体验，其中模糊的论文主题请求从SCR/Socratic缩小开始，而不是立即创建大纲或草稿。

即使措辞包含论文写作意图，也将其视为Socratic触发器：

- "我想写一篇关于..."
- "我有一个论文主题/标题..."
- "我想做一篇论文，题目是..."
- "我有一个研究方向/主题，但还不确定问题"
- "帮我想论文题目/收窄研究问题"
- "논문을 쓰고 싶은데 연구 질문이 아직 명확하지 않아"
- "논문 주제/연구 방향은 있지만 무엇을 연구할지 모르겠어"

在此路径中的第一个响应：

1. 说明请求正在路由到`deep-research` `socratic`模式，因为研究问题尚未精确。
2. 仅使用当前所需的材料缩小问题，使用`socratic_mentor_agent`和`research_question_agent`指导。
3. 在用户至少有一个候选RQ收敛之前，不要生成大纲、草稿、文献综述或完整的管道仪表板。

仅当用户已经有一个清晰的RQ、批准的研究框架、数据/结果、文献矩阵、草稿或明确要求跳过范围并继续大纲/草稿时，才直接路由到`ars/academic-paper/WORKFLOW.md`。仅当用户明确要求完整研究到论文管道或说在Socratic范围后继续时，才路由到`ars/academic-pipeline/WORKFLOW.md`。

## Claude风格别名路由器

Codex不会安装Claude斜杠命令，但此包模拟其意图。如果用户的请求以斜杠别名（`/ars-plan`）或纯别名（`ars-plan`）开头，将其视为模式快捷方式，从任务文本中删除别名标记，读取匹配的`ars/commands/ars-*.md`提示配方，然后路由到下方的工作流`WORKFLOW.md`。

命令前文的`model:`字段仅是Claude路由提示。Codex不会将其转换为Opus/Sonnet模型固定。应用Codex模型策略，并保留用户或运行时模型选择。

| 别名 | 读取命令配方 | 然后路由到 |
|---|---|---|
| `/ars-plan`, `ars-plan` | `ars/commands/ars-plan.md` | `ars/academic-paper/WORKFLOW.md`中的`plan`模式 |
| `/ars-outline`, `ars-outline` | `ars/commands/ars-outline.md` | `ars/academic-paper/WORKFLOW.md`中的`outline-only`模式 |
| `/ars-abstract`, `ars-abstract` | `ars/commands/ars-abstract.md` | `ars/academic-paper/WORKFLOW.md`中的`abstract-only`模式 |
| `/ars-lit-review`, `ars-lit-review` | `ars/commands/ars-lit-review.md` | `ars/academic-paper/WORKFLOW.md`中的`lit-review`模式；如果用户想要源发现和综合，则路由到`ars/deep-research/WORKFLOW.md`中的`lit-review`模式 |
| `/ars-3w`, `ars-3w` | `ars/commands/ars-3w.md` | `ars/deep-research/WORKFLOW.md`中的`three-way-scan`模式 |
| `/ars-citation-check`, `ars-citation-check` | `ars/commands/ars-citation-check.md` | `ars/academic-paper/WORKFLOW.md`中的`citation-check`模式 |
| `/ars-disclosure`, `ars-disclosure` | `ars/commands/ars-disclosure.md` | `ars/academic-paper/WORKFLOW.md`中的`disclosure`模式 |
| `/ars-format-convert`, `ars-format-convert` | `ars/commands/ars-format-convert.md` | `ars/academic-paper/WORKFLOW.md`中的`format-convert`模式 |
| `/ars-revision-coach`, `ars-revision-coach` | `ars/commands/ars-revision-coach.md` | `ars/academic-paper/WORKFLOW.md`中的`revision-coach`模式 |
| `/ars-revision`, `ars-revision` | `ars/commands/ars-revision.md` | `ars/academic-paper/WORKFLOW.md`中的`revision`模式 |
| `/ars-rebuttal-audit`, `ars-rebuttal-audit` | `ars/commands/ars-rebuttal-audit.md` | `ars/academic-paper/WORKFLOW.md`中的`rebuttal-audit`模式；需要评审员评论和现有的响应草稿 |
| `/ars-reviewer`, `ars-reviewer` | `ars/commands/ars-reviewer.md` | `ars/academic-paper-reviewer/WORKFLOW.md`中的`full`模式，除非明确指定其他评审模式 |
| `/ars-mark-read`, `ars-mark-read` | `ars/commands/ars-mark-read.md` | 在活动的材料护照上记录用户证实的阅读声明；每个新标记都需要用户拥有的`read_scope`；仅允许`sections`范围定位符 |
| `/ars-unmark-read`, `ars-unmark-read` | `ars/commands/ars-unmark-read.md` | 撤销对活动材料护照的先前行人阅读标记 |
| `/ars-cache-invalidate`, `ars-cache-invalidate` | `ars/commands/ars-cache-invalidate.md` | 使一个引用键的缓存验证条目失效 |
| `/ars-full`, `ars-full` | `ars/commands/ars-full.md` | `ars/academic-pipeline/WORKFLOW.md` |

如果别名后的请求正文是模糊的主题、暂定标题、研究方向或“题目/主题/方向”，但没有清晰的研究问题，请在路由到别名目标模式之前，参考上文的论文主题范围覆盖。这适用于`ars-plan`、`ars-outline`、`ars-abstract`、`ars-lit-review`和`ars-full`。

如果Codex客户端在它到达模型之前保留了以斜杠开头的输入，请告诉用户使用纯别名形式，例如`ars-plan my topic`。

## 模型和执行策略

对于新的Codex研究会话和支持的显式调度，使用GPT-6 Astra (`gpt-6-astra`)。保留显式的用户/运行时模型选择。技能不能更改已经运行的会话；当知道实际模型时报告它，并且永远不会将计划模型作为观察到的执行呈现。配置模型时，读取[`codex/model-runtime-policy.md`](codex/model-runtime-policy.md)，或运行长时间的研究/评审任务时，委派角色。

通过请求的停止点完成授权的可交付成果。从上下文中解决常规实施选择，并在材料问题悬而未决时继续独立工作。重用现有的授权；仅显示检查点本身不是新的权限请求。保留实际的ARS授权决策、评审标准、同意和机构拥有的授权门禁。如果技能要求阻止工作，请确定确切文件和规则，并解释它需要哪些缺失的决策。

使用适当的推理、简洁的进度更新和原生工具编排界面。批量独立的读取/搜索，保持依赖工作有序，并根据源证据和最终工件判断完成情况。增加工作或添加评审员来解决具体的确定性；避免通用的自我评分、重复不变的检查、固定的重试仪式和不请求的额外可交付成果。保留有用的状态和用户最新的指导，跨越长时间运行或上下文压缩。

## Codex运行时映射

上游ARS文件是为Claude Code编写的。在Codex中使用它们时，应用这些映射：

| 上游措辞 | Codex行为 |
|---|---|
| Agent Team, agent, dispatch, handoff | 将引用的`agents/*.md`作为范围角色合同读取。使用原生运行时执行内联或委派独立工作，如下所述。 |
| Agent tool, Task tool, subagent | 当原生协作可用并提高质量或时间时，委派有界、独立的工作。在它运行时继续有用的本地工作；尊重用户限制和可用插槽。使用`codex/agents/*.md`定义角色边界。固定的规划器拓扑仍然是可选的。 |
| AskUserQuestion | 提问简洁的澄清问题，或当活动模式中可用时使用Codex的结构的用户输入工具。 |
| WebSearch | 使用Codex网络浏览进行当前事实、源验证、引用检查和外部证据。提供源链接。 |
| Bash, Write, Edit | 将其视为能力描述，而不是必需的工具名称。遵循Codex安全规则和用户的文件系统限制。 |
| Agent frontmatter `tools: Read, Write, Edit, Grep, Glob` | 保留此作为最小权限角色边界。三个受保护的最高级代理角色在单独分派时不会接收Bash或网络传输；内联执行不得使用这些角色来扩大当前任务的权限。 |
| Claude, Claude Code, 模型特定措辞 | 解释为“当前的Codex代理”，除非文本是披露模板或历史示例的一部分。 |
| `ARS_MODEL_TIERING=economy|quality-boost` | 未设置保持默认值并保留当前模型行为。上游相对Opus/Sonnet层级名称不会硬映射到Codex模型ID。仅在活动Codex运行时支持显式的每个调度模型覆盖时应用层级。否则宣布一行无操作，并保持每个角色在活动模型上。使用`ars/shared/model_tiering.md`和`ars/scripts/model_tiering_manifest.json`作为分类合同。 |
| `ARS_CROSS_MODEL`, `ARS_CROSS_MODEL_REASONING_EFFORT`, `ARS_OPENAI_COMPAT_BASE_URL`, `ARS_OPENAI_COMPAT_API_KEY` | 除非用户明确要求跨模型评审，否则将上游次要模型分派指令视为无操作。当在此Codex包中明确启用时，请遵循`ars/shared/cross_model_verification.md`：识别提供者/模型/ID状态/内容类别，在进行任何外部上传之前获得明确的用户同意，保留风险分层采样和盲意分歧检查点规则，并仅调用配置的提供者API。分派的拥有者发出标准的`[CROSS-MODEL-HANDOFF v1]`信封；Codex上下文验证它，仅发送有效负载，应用机械结果路由，并将判断工作返回给拥有者。在评审`full`模式下，同意的跨模型轨道交换现有的评审员2座位，而不是添加评审员；重新评审运行独立的Priority-1法官通过，并记录法官记录。披露单个家庭或备用执行，并且永远不会通过活动Codex模型模拟任何轨道。 |
| `ARS_CROSS_MODEL_TRANSPORT=codex`, `scripts/cross_model_codex_transport.py` | 此显式选择仅限于在Stage 2.5 / 4.5通过ChatGPT订阅Codex应用服务器进行的包含的、单个引用引用检查。需要Codex CLI 0.147.0或更高版本、`ARS_CROSS_MODEL`、`Logged in using ChatGPT`在stdout或stderr上的确切证明，以及正常的提供者/内容/成本同意门禁；不接受调用者创作的提示或路径，将选择器扩展到评审/DA/校准/重新评审/交接调用，或自动回退到API。提供者模式省略了不支持的`uniqueItems`，但本地验证仍然会拒绝重复来源。在允许独立搜索工具所需的受限制的搜索主机允许的同时禁用`code_mode`；关闭事件允许列表保持权威。仅在`turn/completed`、干净的进程退出和stdout/stderr EOF之后才接受结果；晚到的禁止或格式错误的事件、排水超时、非零退出、读取器故障或stderr溢出会明显失败。 |
| `S2_API_KEY`, `OPENALEX_API_KEY`, `OPENALEX_POLITE_EMAIL`, `CROSSREF_POLITE_EMAIL` | 这些是可选的上游书目查找设置。仅在用户明确运行污染信号迁移或程序化引用验证时使用它们；正常的Codex路由不需要它们。永远不会记录带有凭证的查询字符串，并且不要使用浏览器检索来绕过API速率限制。 |
| `ARS_VERIFICATION_CACHE_PATH`, `ARS_CACHE_STALE_ADVISORY_DAYS`, `ARS_CACHE_REVALIDATE` | 这些配置了本地SQLite引用验证缓存、建议仅限陈旧行的阈值（默认30天；`0`禁用）和选择加入实时重新验证。当程序化引用门禁运行时，保留默认的缓存行为。实时重新验证可能会调用外部书目服务，因此仅在用户的验证任务和正常网络/凭证边界内使用它；建议永远不会成为门禁失败。 |
| Local PDF page anchors, `scripts/pdf_read_preflight.py` | 在信任从本地读取的PDF的`page`锚点之前，运行一次结构预检，并携带其`ref_slug`侧车。将`FAIL`视为对页面锚点读取完整性的正面证据，将`UNAVAILABLE`视为明确的建议；永远不要将缺失的依赖项、加密文件、解析修复或缺失的侧车转换为`PASS`。v3.20的`--classify-content`扩展是选择加入的、进程隔离的，依赖于单独固定的`requirements-pdf-content-classifier.txt`，并且仅发出`TEXT_AVAILABLE` / `OCR_RECOMMENDED` / `unavailable`建议，而裁决范围保持`STRUCTURE_ONLY`；永远不要将其转换为自动OCR或锚点接受门禁。 |
| `scripts/research_workflow_profile.py` | 将研究工作流配置文件视为确定性、默认关闭的底层，而不是自动路由器。仅使用显式选择或可见的`field_general`回退；永远不会从手稿中推断研究系列。更正追加收据，并标记先前的配置文件输出为陈旧，而不会重写学者拥有的工件。 |
| `ARS_INQUIRY_LEDGER=1`, `scripts/inquiry_branch_ledger.py` | 询问分支账本是选择加入的本地alpha。当明确激活时，保留作者拥有的追加事件、有界摘要、项目/路径身份、锁定、恢复和单独可见的陈旧原因。该标志授权不使用外部模型、API或搜索调用，也不产生新颖性、正确性、价值或可用性声明。 |
| `scripts/check_promotion_bakeoff_preregistration.py` | 保留密封的承诺/揭示合同，并使用本包中的密封单元测试。不要直接对重新根的打包子树运行`verify-tree`：它故意缺少该发布纪律检查所需的完整规范上游Git历史记录。真正的未来烘烤必须从上游存储库开始，并且仍然需要明确同意每个实时模型调用和成本。 |
| `fresh Claude Code session`, `Claude Code session` | 解释为“一个新的Codex对话”。材料护照重置语义仍然适用；仅运行时更改。此规则涵盖`ars/academic-pipeline/WORKFLOW.md`、`ars/academic-pipeline/agents/pipeline_orchestrator_agent.md`、`ars/academic-pipeline/references/passport_as_reset_boundary.md`、`ars/experiment-agent/README.md`、`ars/experiment-agent/README.zh-TW.md`和`ars/docs/PERFORMANCE.md`。 |
| `/ars-*`斜杠命令, Claude插件命令 | 将`ars/commands/ars-*.md`视为可选的提示配方。Codex不会注册此包的斜杠命令。 |
| SessionStart hook, SubagentStop hook, `hooks/hooks.json`, `scripts/ars_update_check.sh` | 将其视为上游Claude Code钩子元数据。v3.18更新检查是打包的，用于可追溯性和测试，但由Codex安装或执行；Codex包更新仍然是手动的，除非用户明确要求移植钩子行为。 |
### 书目网络路由

上游提示合同、Python解析器客户端和v3.21
声明地位适配器是不同的执行路径。在遵循任何说明查找自动发生的上游指令之前，应用此表：

| 路径 | 默认ARS-Codex行为 | 专用客户端触发 |
|---|---|---|
| 普通主题或候选发现 | 使用Codex浏览和权威网络来源。 | 从不启动语义学者、OpenAlex、Crossref或arXiv Python解析器客户端。 |
| 代理端摄取、去重和源验证 | 在默认路由中，将提示级别的`WebSearch`或索引查找转换为Codex浏览或官方元数据页面。 | 上游提示措辞，如“自动S2查找”，在Codex中不会自行启动Python客户端。 |
| 脚本支持的引用存在门禁 | 不要仅根据`ars-full`请求推断这一点。Stage 2.5和4.5仍然是强制性的完整性检查点，但默认Codex路由通过浏览执行其源工作，除非用户也请求程序化验证。 | 明确请求运行`verify_passport.py`、`verification_gate`或等效程序化引用验证。一旦调用，缓存未命中可能会调用Crossref、OpenAlex和Semantic Scholar进行非手动引用；仅当`arxiv_id`存在时才运行arXiv。手动引用跳过所有四个。 |
| 声明地位发现 | 仅在Stage  | 用户请求加上积极、计划约束的同意。它使用v3.21关键字发现适配器，而不是四个单引用解析器客户端；缺失、取消、失效或陈旧的同意意味着不调用。 |
| 污染回填或迁移 | 没有自动迁移。 | 仅明确选择的迁移CLI及其记录的索引。 |

上游的规范网络映射仍然可在`ars/docs/DATA_FLOWS.md`中找到；本节是Codex适配器覆盖，用于当这些流程实际在此处启动时覆盖这些流程。

### ARS v3.22.0 合同诚实界限

- 对于摘要输出，遵循用户语言。 
- 对于中文，除非用户要求否则使用繁体中文。 
- 对于分阶段工作流，显示当前阶段、所需输入、输出工件，以及下一个门禁是可选的还是强制的。 
- 对于论文/研究输出，保持不确定性明确且证据、推理和推荐分开。
