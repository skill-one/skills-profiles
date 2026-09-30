---
name: llm-wiki
description: 构建和维护AI驱动的Obsidian维基的基础知识蒸馏模式。基于Andrej Karpathy的LLM维基架构。当用户想要理解维基模式、设置新的知识库，或需要关于三层架构（原始资料→维基→模式）的指导时，请使用此技能。在讨论知识管理策略、维基结构决策或如何组织蒸馏知识时，也请使用此技能。这是“理论”技能——其他技能处理具体操作（如摄取、查询、校验）。
---

# LLM Wiki — 知识蒸馏模式

你正在维护一个持久化、复合型的知识库。这个维基不是聊天机器人——它是一个**编译后的产物**，知识被蒸馏一次并保持最新状态，而不是在每次查询时重新推导。

## 三层架构

### 第一层：原始来源（不可变）

用户的原始文档——文章、论文、笔记、PDF文件、对话记录、书签、**以及图片**（截图、白板照片、图表、幻灯片捕获）。这些文档永远不会被系统修改。它们存放在用户指定的位置（通过 `.env` 中的 `OBSIDIAN_SOURCES_DIR` 配置）。图片是一流来源：摄入技能通过读取工具的视觉支持读取它们，并将它们的解释内容视为推断内容，除非是逐字转录的文本。图片摄入需要一个支持视觉的模型——没有视觉支持的模型应跳过图片来源并报告被跳过的文件。

将原始来源视为“源代码”——权威但难以直接查询。

不要将其与库内的 `_raw/` 预处理文件夹混淆，这是另一回事：用于快速捕获和等待提升的草稿箱（参见 `wiki-capture` 和 `wiki-ingest`）。那里的文件不是第一层来源，但 `wiki-ingest` 在提升时仍然移动而不是删除它们，因为其中一些文件没有其他副本。

### 第二层：维基（由LLM维护）

一组通过类别组织的互连的Obsidian兼容Markdown文件。这是编译后的知识——综合的、交叉引用的、可导航的。每一页都有：

- YAML前导内容（标题、类别、标签、来源、时间戳）
- Obsidian `[[wikilinks]]` 连接相关概念
- 清晰的出处——每个声明都可以追溯到来源

维基位于通过 `.env` 中的 `OBSIDIAN_VAULT_PATH` 配置的路径下。

### 第三层：模式（此技能 + 配置）

管理维基结构的规则——类别、约定、页面模板和操作工作流。模式告诉LLM如何维护维基。

## 维基组织

库具有两个级别的结构：**类别**（知识类型）和**项目**（知识来源）。

### 类别

将页面组织到这些默认类别中（可在 `.env` 中自定义）：

| 类别 | 目的 | 示例 |
|---|---|---|
| `concepts/` | 概念、理论、心智模型 | `concepts/transformer-architecture.md` |
| `entities/` | 人物、组织、工具、项目 | `entities/andrej-karpathy.md` |
| `skills/` | 操作知识、程序 | `skills/fine-tuning-llms.md` |
| `references/` | 特定来源的摘要；学术论文使用 Paper Deep-Dive Template（下方） | `references/attention-is-all-you-need.md` |
| `synthesis/` | 跨来源的交叉分析 | `synthesis/scaling-laws-debate.md` |
| `journal/` | 带时间戳的观察、会话记录 | `journal/2024-03-15.md` |

### 项目

知识通常属于特定项目。`projects/` 目录反映了这一点：

```
$OBSIDIAN_VAULT_PATH/
├── projects/
│   ├── my-project/
│   │   ├── my-project.md      ← 项目概述（以项目命名）
│   │   ├── concepts/          ← 项目范围的类别页面
│   │   ├── skills/
│   │   └── ...
│   ├── another-project/
│   │   └── ...
│   └── side-project/
│       └── ...
├── concepts/                   ← 全局（跨项目）知识
├── entities/
├── skills/
└── ...
```

**当知识是项目特定时**（仅适用于一个代码库的调试技术、特定项目的架构决策），将其放在 `projects/<project-name>/<category>/` 下。

**当知识是通用时**（如“React Server Components”这样的概念、像“Andrej Karpathy”这样的人物、广泛适用的技能），将其放在全局类别目录中。

**交叉引用：** 项目页面应 `[[wikilink]]` 到全局页面，反之亦然。项目概述页面应链接到与该项目相关的关键概念、技能和实体页面——无论它们是位于项目下还是全局下。

**命名规则：** 项目概述文件必须命名为 `<project-name>.md`，而不是 `_project.md`。Obsidian的图视图使用文件名作为节点标签——`_project.md` 在图中使每个项目都显示为 `_project`，使其难以阅读。因此 `projects/my-project/my-project.md`、`projects/another-project/another-project.md` 等。

每个项目目录都有一个结构如下所示的概述页面：

```markdown
---
title: >-
    My Project
category: project
tags: [ai, web, backend]
source_path: ~/.claude/projects/-Users-name-Documents-projects-my-project
created: 2026-03-01T00:00:00Z
updated: 2026-04-06T00:00:00Z
---

# My Project

一句话总结这个项目是什么。

## 关键概念
- [[concepts/some-api]] — 用于核心功能
- [[projects/my-project/concepts/main-architecture]] — 项目特定架构

## 相关
- [[entities/some-service]] — 部署平台
```

## 特殊文件

每个维基在其根目录下都有这些文件：

> **使用 `obsidian-wiki memory` 写它们，不要手动写。** `index.md`、
> `log.md`、`hot.md` 以及 `_meta/` 表共享一个建议锁，并原子性写入；并行运行中的手动编辑会丢失第二个写入的写操作。`obsidian-wiki memory sync <VERB> key=value` 一次调用完成所有三个操作。完整过程——动词、`Key Takeaways` 插槽（保持为你的）、所有者配置文件和待办索引——在
> [`references/MEMORY.md`](references/MEMORY.md) 中。

### `index.md`
按类别组织的面向内容的目录。每个条目都有一个简短的摘要和标签。每次摄入操作后都要重建这个目录。格式：

```markdown
# Wiki Index

## 概念
- [[transformer-architecture]] — 适用于序列建模的主流架构 ( #ml #architecture)
- [[attention-mechanism]] — 变换器的核心构建块 ( #ml #fundamentals)

## 实体
- [[andrej-karpathy]] — 人工智能研究员、教育家、前特斯拉人工智能总监 ( #person #ml)
```
**格式规则：** 在开括号后添加一个空格和标签。
❌ 不要：`description (#tag)` — 会破坏标签解析
✅ 要：`description ( #tag)` — 正确的空格和标签解析

### `log.md`
按时间顺序记录的只增不删的记录，跟踪每次操作。每个条目都是可解析的：

```markdown
## Log

- [2024-03-15T10:30:00Z] INGEST source="papers/attention.pdf" pages_updated=12 pages_created=3
- [2024-03-15T11:00:00Z] QUERY query="Transformers如何处理长序列？" result_pages=4
- [2024-03-16T09:00:00Z] LINT issues_found=2 orphans=1 contradictions=1
- [2024-03-17T10:00:00Z] ARCHIVE reason="rebuild" pages=87 destination="_archives/..."
- [2024-03-17T10:05:00Z] REBUILD archived_to="_archives/..." previous_pages=87
```

### `.manifest.json`
跟踪所有已摄入的来源文件——路径、时间戳、以及它生成的维基页面。这是增量系统的骨干。参见 `wiki-status` 技能以获取完整模式。

清单启用：

- **增量计算** — 自上次摄入以来新内容或修改内容
- **追加模式** — 仅处理增量，不处理所有内容
- **审计** — 哪个来源生成了哪个维基页面
- **陈旧检测** — 来源已更改但维基页面未更新

**来源键合同（v2）。** 来源键——`.manifest.json` 中的 `sources` 键、页面上的 `sources:` 前导内容以及项目的 `source_repo` —— 必须是机器可移植的。库跨机器同步，因此裸绝对路径（`/Users/...`、`/home/...`）永远不会是有效的存储键。这是唯一的规范定义；其他技能参考它而不是重新声明它。

| 来源存储位置 | 规范键形式 | 示例 |
|---|---|---|
| 在库内 | **库相对路径** — POSIX分隔符、无开头的 `./`、无 `..` | `Raw/database/postgres.pdf`、`Clippings/article.md` |
| 在 `$HOME` 下 | **家相对路径** — 以 `~` 开头 | `~/.claude/projects/-Users-name-my-app/abc.jsonl` |
| 根本不是文件 | **伪键** — 任何 `scheme:`/`://` 标识符，视为不透明 | `url:https://example.com/article`、`agent:claude/<session-id>` |

规则：

1. **永远不要存储裸绝对路径。** 写入前转换，而不是写入后。
2. **比较前规范化。** 展开波浪号和环境变量，将库相对键与库根相对路径解析，并将 `scheme:`/`://` 伪键视为不透明标识符。在未规范化之前永远不要比较原始字符串。
3. **身份在路径更改后保持不变。** 同一个逻辑来源在不同的机器上保持相同的键。
4. **伪键是一个开放的命名空间。** 使键成为伪键的是它的形状（`scheme:` 或 `://`，因此它永远不会被误认为是文件路径），而不是固定的名称列表。推荐名称：`repo:<host/owner/name>` 用于git项目，`url:<canonical-url>` 用于网页，`agent:<agent>/<id>` 用于代理会话。既不在库内也不在 `$HOME` 下的来源仍然需要一个——不要让它回退到绝对路径。
5. **项目身份是一个仓库，而不是一个检出。** 在 `projects` 块中，通过 `source_repo`（`host/owner/name`）而不是机器路径来标识一个项目。如果机器特定的检出位置有用，它应该位于可选的 `source_cwd_hint`（波浪号相对），永远不会在身份中。

读取是向后兼容的：一个充满绝对键的现有清单仍然可以工作，并且 `scripts/manifest.py migrate <vault> --dry-run` 将其转换为合同v2（合并冲突，保留最新的 `ingested_at`）。**如果库在机器之间移动**，其绝对键以 *旧* 库路径为根，这与新库或 `$HOME` 都不匹配——显式传递旧根 `migrate <vault> --from-root <old-vault-root>`（如果库位于多个位置，请重复该标志）。然后命令报告 `nothing portable to write — N key(s) kept non-portable` 而不是声称成功。新写入通过相同的规范化，因此技能可以将绝对路径传递给 `obsidian-wiki cache-update`，并且仍然有一个可移植的键出现在清单中。

**记录出处。** 当你写入清单条目时，用该来源贡献的库相对页面路径填充 `pages_created` 和 `pages_updated`。这是使重新摄入（当来源更改时）能够找到要重新访问的页面的关键，而不是猜测。

## 页面模板

创建新的维基页面时，使用此结构：

```markdown
---
title: >-
    Page Title
category: concepts
tags: [ml, architecture]
aliases: [alternate name]
relationships:
  - target: "[[concepts/related-concept]]"
    type: extends
sources: [papers/attention.pdf]
summary: >-
    一两句话，≤200个字符，以便读者（或另一个技能）在不打开页面的情况下预览此页面。
provenance:
  extracted: 0.72
  inferred: 0.25
  ambiguous: 0.03
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: 2024-03-15
tier: supporting
created: 2024-03-15T10:30:00Z
updated: 2024-03-15T10:30:00Z
---

# Page Title

一句话总结此页面涵盖的内容。

## 关键思想

- 来源的核心声明，直接释义。
- 来源暗示但未明确说明的概括。 ^[inferred]
- 两个来源有分歧的图表。 ^[ambiguous]

使用 [[wikilinks]] 连接到相关页面。

## 未解决的问题

未解决或需要更多来源的事情。

## 来源

- [[references/attention-is-all-you-need]] — 原始论文
```

**解析安全的标量。** 写自由文本前导内容值——至少 `title` 和 `summary` —— 使用折叠标量语法（`>-`）如上所示：包含 `: `（冒号加空格）、`#` 或引号的裸标量会破坏YAML解析，Obsidian随后报告“无效属性”并隐藏前导内容。在 `title: >-` / `summary: >-` 后的行上保持值缩进。

## 论文深度解析模板

通用模板适用于大多数来源。**学术论文是例外。** 对于ML/AI/LLM/VLM（以及类似的）论文，落入 `references/` 的，实质内容存在于架构、方程式和结果表中——正好是简洁的“关键思想”列表扁平化掉的。对于这些，使用更丰富的模板。这是唯一一个“编译，不要检索”让位于深入、自包含的演练，读者可以研究而不是论文的地方。

Obsidian原生渲染所需的基本元素，因此不需要额外的工具：Mermaid fenced diagrams、`$$…$$` LaTeX（MathJax）、markdown表格、`![[image]]` / `![[paper.pdf#page=N]]` 嵌入。

仅当来源是带有承重图表或方程式的学术论文（arXiv/conference）时才使用此模板。其他所有内容使用上述通用页面模板。前导内容、出处标记、置信度、生命周期和 `relationships:` 保持不变——只有正文部分不同。

````markdown
---
# ...必需的前导内容，与通用模板相同；类别: references...
---

# Paper Title

> [!tldr] 一句话：新内容加上头条结果。

## 问题与动机

论文解决的问题是什么。

## 方法 / 架构

散文式演练。嵌入论文的真实架构图作为主要视觉（参见 `wiki-ingest` 中的 *Academic papers* 以获取 PyMuPDF提取配方）。只有在无法提取图表时才回退到 Mermaid 流程图。

![[attachments/<slug>-fig1.png]]
*图N（作者年份）：一句话说明。*

## 关键方程

1-3个核心方程式作为显示数学，而不是反引号代码：

$$ \mathcal{L} = \mathbb{E}_{x}\!\left[-\log p_\theta(y \mid z)\right] $$

## 结果

头条数字作为表格，而不是逗号分隔的块——如果论文有，则嵌入一个关键结果/激励图表（扩展图、基准图、能力拼贴）：

| 方法 | 基准 | 指标 | 成本 |
|---|---|---|---|
| 基线 | … | … | … |
| **此论文** | … | … | … |

![[attachments/<slug>-resultsN.png]]
*图N（作者年份）：一句话说明。*

## 限制

论文承认或回避的内容。标记在字里行间阅读为 ^[inferred]。

## 相关

到邻近工作的类型 `[[wikilinks]]`。

## 来源

- 可点击的规范链接，例如 <https://arxiv.org/abs/XXXX.XXXXX>
````

从论文的散文中重建的Mermaid图表是综合性的，而不是转录性的——当解释是非平凡时，将其视为 `^[inferred]`。

## 出处标记

维基页面上的每个声明都有三种出处状态中的一种。在行内标记它们，以便读者（和未来的摄入过程）可以区分信号和综合。

这些是框架默认值。库的 `AGENTS.md` 可能会添加标记或工作流标志。保留所有者扩展并单独处理正交工作流标志，而不是提取/推断/模糊真相轴。

| 状态 | 标记 | 含义 |
|---|---|---|
| **提取** | *(无标记——默认)* | 来源实际说的内容的释义。 |
| **推断** | `^[inferred]` 后缀 | 由LLM综合的声明——来源没有直接说明的连接、概括或暗示。 |
| **模糊** | `^[ambiguous]` 后缀 | 来源有分歧，或来源不明确。 |

示例：

```markdown
- 变换器跨位置并行，与RNN不同。
- 这就是它们在现代硬件上扩展更好的原因。 ^[inferred]
- GPT-4是在大约13T tokens上训练的。 ^[ambiguous]
```

**为什么使用这种语法：**
- `^[...]` 在Obsidian中是脚注相邻的——渲染干净且永远不会与 `[[wikilinks]]` 冲突。
- 行内（后缀），以便单个项目保持为单个项目。
- 默认为提取意味着没有标记的现有页面保持有效。

**前导内容摘要：** 可选地在此级别显示大致混合，以便用户可以扫描推测性强的页面而无需阅读它们：

```yaml
provenance:
  extracted: 0.72   # 无标记的句子/项目的大致比例
  inferred: 0.25
  ambiguous: 0.03
```

这些是由摄取技能在创建/更新时编写的最佳努力数字。`wiki-lint` 重新计算它们并标记漂移。该块是可选的——没有该块的页面按惯例视为完全提取。

## 带有类型的关联关系

页面正文中的普通 `[[wikilinks]]` 不携带语义权重——它们表示“相关”，但不是*如何*相关。可选的 `relationships:` 前置块为知识图谱添加了带有类型、方向性的边。

### `relationships:` 块

```yaml
relationships:
  - target: "[[Transformer Architecture]]"
    type: extends
  - target: "[[LSTM]]"
    type: contradicts
  - target: "[[Attention Mechanism]]"
    type: implements
```

每个条目有两个必填字段：
- `target` — 一个使用与 `OBSIDIAN_LINK_FORMAT` 相同格式的 wikilink，链接到相关页面
- `type` — 下面允许的语义类型之一

### 允许的关联关系类型

下面的表格是框架默认的允许列表。一个保险库的 `AGENTS.md` 可以扩展它；消费者必须使用有效的允许列表并保留所有者语义，而无需强制执行。

| 类型 | 含义 | 示例 |
|---|---|---|
| `extends` | 本页面基于或概括目标 | GPT 扩展 Transformer Architecture |
| `implements` | 本页面是目标概念的具象实现 | BERT 实现掩码语言建模 |
| `contradicts` | 本页面的声明与目标冲突或反驳 | 证据 A 与证据 B 冲突 |
| `derived_from` | 本页面基于或改编自目标 | 微调源自迁移学习 |
| `uses` | 本页面依赖于或依赖于目标 | RAG 使用向量数据库 |
| `replaces` | 本页面取代或弃用目标 | GPT-4 取代 GPT-3 |
| `related_to` | 万能：相关但没有更强的方向性类型适用 | 概念 A 与概念 B 相关 |

### 规则

- **可选字段** — 如果没有已知的有类型关联关系，则完全省略该块。未标记的 wikilink 保持有效，并由 `wiki-export` 视为 `related_to`。
- **不要重复** — 如果 `[[foo]]` 已经作为内联 wikilink 出现，则 `relationships:` 条目只是为其添加类型；它不是第二个链接。
- **方向很重要** — 声明条目的页面是*源*；`target` 是目的地。只能从本页面的角度声明关系。
- **不要编造** — 只有当源材料使关系方向和类型清晰时才添加有类型的条目。如有疑问，请使用 `related_to` 或省略。

读取 `relationships:` 的技能：`wiki-export`（发出有类型的边）、`cross-linker`（在推断链接时写入有类型的条目）、`wiki-query`（在答案中显示类型，并为多跳“X 如何连接到 Y”路径查询遍历有类型的边图——有界 BFS 遍历 `relationships:` 邻接矩阵，仅限于前置块）。

## 置信度和生命周期

每个页面都携带两个正交的信任信号和一个可选的替代链接。

下面的必填性和生命周期值是框架默认值。一个保险库的 `AGENTS.md` 可以扩展生命周期值或使信任字段可选。验证器必须应用有效的所有者模式，同时仍然验证任何存在的信任值。

确定性的 lint/trust 消费者通过 `OBSIDIAN_ALLOWED_LIFECYCLES`、`OBSIDIAN_ALLOWED_RELATIONSHIP_TYPES`、`OBSIDIAN_REQUIRED_TRUST_FIELDS` 和 `OBSIDIAN_SCHEMA_SOURCE` 接收所有者模式。解析优先级是 CLI > 环境配置 > 这些框架默认值（生命周期和关系扩展是可加的）。显式的空白或仅空白值会导致失败；省略变量以选择默认值。`wiki-lint/SKILL.md` 拥有操作调用合同。

### 必填字段

```yaml
base_confidence: 0.65          # [0.0, 1.0] — 与内容变化无关的质量估计。存储一次，在内容变化时重新计算。
lifecycle: draft               # draft | reviewed | verified | disputed | archived
lifecycle_changed: 2024-03-15  # ISO 日期，表示上次状态转换的时间
# lifecycle_reason: "..."      # 可选的自由文本——状态变化的原因；由 wiki-query 显示
# superseded_by: "[[new-page]]" # wikilink；仅当 lifecycle=archived 时
```

`lifecycle_reason` 和 `superseded_by` 是可选的。永远不要编造它们。

### 置信度公式

公式是一个**手动基础分数**，不是一个确定性 URL 分类器：

```
base_confidence = lineage_count_score * 0.5 + source_quality_score * 0.5

lineage_count_score  = min(independent_evidence_lineages / 3, 1.0)
source_quality_score = avg(reviewed quality score per independent lineage)
```

计算原始分数后，评估证据是否涵盖页面的材料声明。部分覆盖可能证明保持或降低分数；不支持的材料声明需要在任何置信度变化之前修复源/声明。避免在没有有意义的认识论变化的情况下出现小的分数波动。

**源质量分数**（使用最匹配的桶）：

| 桶 | 分数 | 示例 |
|---|---|---|
| `paper` | 1.0 | arXiv, 会议论文集 |
| `official` | 0.9 | `*.gov`，供应商文档 |
| `documentation` | 0.85 | 维护良好的第三方文档 |
| `book` | 0.8 | 书籍，技术参考 |
| `repository` | 0.75 | 内容寻址的存储库/代码证据 |
| `blog` | 0.55 | 个人博客 |
| `session_transcript` | 0.5 | 对话历史或完成的操作 |
| `forum` | 0.4 | Stack Overflow，HN，Reddit，问题等级报告 |
| `unknown` | 0.4 | 万能/当前配置 |
| `llm_generated` | 0.3 | LLM 合成或未验证的记忆种子 |

**一个独立证据谱系**是一个可以独立证实声明的起源。规范源 ID 对于识别仍然有用，但身份本身并不能证明独立性。在计数之前折叠依赖证据：

- 来自一个存储库的文件、发布和提交 → 一个存储库谱系；
- 在一个工作流中的重试/审查/修复任务 → 一个任务谱系；
- 父/子看板记录 → 一个任务谱系；
- 跨配置文件的字节相同记忆 → 一个记忆谱系；
- 一个快照加上它捕获的可变源 → 一个谱系；
- 指向一个起源的别名或元数据引用 → 一个谱系。

确定性的 `wiki-lint` 路径验证 `_meta/trust-ledger.json`；它不会从源字符串重新计算置信度。新页面或实质性变化的页面被标记为需要人工审查。只有在明确的人工批准后，才刷新账本。

**每个技能的默认值**（摄取技能自动计算这些）：

| 技能 | base_confidence | lifecycle |
|---|---|---|
| `wiki-ingest` (URL) | `0.17 + 0.5 × classify(url)` | `draft` |
| `wiki-ingest` (单个文档) | 按源分类器 | `draft` |
| `wiki-ingest` (多文档) | `min(N/3,1)×0.5 + avg_q×0.5` | `draft` |
| `wiki-research` | 变化，通常 0.85+ | `draft` |
| `wiki-capture` | 0.42 | `draft` |
| `*-history-ingest` | 0.42 | `draft` |
| `wiki-update` | 0.59 | `draft` |
| `wiki-synthesize` | `min(input_pages.base_confidence)` | `draft` |

### 生命周期状态机

五种状态。**`stale` 不是一种状态**——它是一个计算出的覆盖层：`is_stale = (今天 − 更新) > 90 天`。

| 状态 | 进入方式 | 备注 |
|---|---|---|
| `draft` | 任何摄取技能在第一次写入时 | 所有新页面的默认值 |
| `reviewed` | 仅人类编辑 | |
| `verified` | 仅人类编辑 | 时间本身永远不会降级已验证的页面 |
| `disputed` | 仅手动编辑 | 在显示中覆盖除 `archived` 之外的所有状态 |
| `archived` | 手动编辑，或摄取技能设置 `superseded_by` | 终端 |

只有摄取技能设置 `draft`。所有其他转换都需要人类编辑。每当状态变化时，更新 `lifecycle_changed`。

因此，两种边缘类别是**非法的**，并由 `obsidian-wiki lint` 报告为 `illegal_lifecycle_transitions`：任何回退到 `draft`（`reviewed|verified|disputed → draft`），以及任何从 `archived` 的退出（它是终端——恢复页面是一个故意的删除和重新创建，而不是转换）。检查与页面上次审查时 `_meta/trust-ledger.json` 中记录的生命周期进行比较，因此它只看到至少被审查过一次的页面。

## 重要性分层

`tier:` 字段控制每个摄取过程中哪些页面被更新以及它们在检索中的优先级。随着维基的增长，在每次摄取中重新读取每一页浪费代币——分层允许摄取和查询技能将精力集中在最重要的地方。

### 三个层级

| 层级 | 含义 | 摄取行为 | 查询优先级 |
|---|---|---|---|
| `core` | 承载页面——许多其他页面依赖于它们（高入站链接计数或桥梁位置）。始终值得更新。 | 如果源即使稍微相关，也始终更新 | 首先在索引和全读取遍历中显示 |
| `supporting` *(默认)* | 标准维基页面，具有适度的连接性 | 当源对此页面有明确的新的声明时更新 | 标准优先级 |
| `peripheral` | 低连接性页面——很少链接，范围狭窄 | 除非源*主要*是关于这个主题，否则跳过 | 最后手段；在修剪到上下文预算时跳过 |

### 分配规则

- **新页面**：默认为 `tier: supporting`
- **提升到 `core`**：当页面积累了 ≥5 个入站 wikilink **或**被 `wiki-status` 洞察模式标记为桥梁时
- **降级到 `peripheral`**：当页面有 ≤1 个入站链接并且 90 多天没有更新时
- **人工覆盖总是获胜**——手动编辑 `tier:` 以在任何级别锁定页面
- 没有 `tier:` 的现有页面被视为 `supporting`（向后兼容——不需要迁移）

### 谁管理层级

- `wiki-ingest` 读取 `tier:` 以决定在当前遍历中是否更新页面
- `wiki-query` 使用 `tier:` 对索引遍历中的候选者进行排序并修剪到上下文预算
- `wiki-status` 洞察模式计算图指标并**建议**层级分配——它永远不会自动写入它们
- `wiki-lint` 在新创建的页面（第二阶段执行，与 `base_confidence` 的时间线相同）上标记缺少 `tier:`

## 检索原语

读取保险库是每个读取端技能的主要成本。使用能够回答问题的最便宜的原语，并且**只有在更便宜的原语不足以满足需求时才升级**。任何需要从保险库获取内容的技能都应遵循此表，而不是直接跳到全页读取。

| 需要 | 原语 | 相对成本 |
|---|---|---|
| 页面是否存在？它的标题/分类/标签是什么？ | 读取 `index.md`；`Grep` 前置块（使用模式范围 `^---` 块在文件头部） | **最便宜** |
| 页面 1-2 句的预览 | 读取其前置块中的 `summary:` 字段 | **便宜** |
| 页面中的特定声明或部分 | `Grep -A <n> -B <n> "<term>" <file>`——仅返回匹配的行及其上下文 | **中等** |
| 整个页面内容 | `Read <file>` | **昂贵**——最后手段 |
| 跨页面的关系 | 在保险库中跨 `Grep "\[\[.*?\]\]"`，或从已知页面遍历 wikilinks | 按情况而定 |

**搜索命令偏好**：对于 shell/文件搜索，当可用时使用 ripgrep (`rg`，`rg --files`)；如果不可用，则回退到 `grep`/`find`。这些技能中带大写的 `Grep`/`Glob` 名称是通用原语，用于暴露这些工具的代理。

**规则**：只有在更便宜的原语无法回答问题时才升级。如果你只能从 `summary:` 字段中回答，就不要读取页面正文。如果一个带有 `-A 10 -B 2` 的抓取部分给你提供了声明，就不要读取整个页面。一个 500 行的页面打开读取 15 行是 485 行浪费的代币。

**为什么这很重要**：一个 20 页的保险库让你可以容忍全保险库扫描。一个 200 页的保险库则不行。上述原语是技能框架如何在不使用数据库的情况下扩展到大型保险库的方式。

消耗此表的技能：`wiki-query`，`cross-linker`，`wiki-lint`，`wiki-status`（洞察模式）。任何新的读取保险库的技能都应该引用本节，而不是重新发明模式。

## QMD 索引新鲜度

QMD 是一个可选的搜索索引，叠加在保险库之上。Markdown 保险库是真相来源。任何写入维基 Markdown 的技能在保险库写入完成后都应该刷新 QMD，但仅当 `QMD_WIKI_COLLECTION` 配置并且本地 QMD 传输可用时。如果 QMD 刷新失败，请保留保险库更改并单独报告 QMD 状态。

使用能够证明新内容可见的最便宜验证路径：`qmd update`，如果向量过时或丢失，则 `qmd embed`，然后对已写入的页面或集合根进行有针对性的 `qmd get` 或 `qmd ls` 检查。只读技能不应刷新 QMD。

## 核心原则

1. **编译，不要检索。** 维基是预先编译的知识。当您摄取一个源时，请更新所有相关页面——不要只是为源创建摘要。

2. **随着时间的推移进行复合。** 每次摄取都应该使维基变得更聪明，而不仅仅是变大。将新信息合并到现有页面中，解决矛盾，加强交叉引用。

3. **来源很重要。** 每个声明都应该追溯到一个来源。在更新页面时，请说明是哪个来源触发了更新。

4. **标记推断。** 默认句子是提取的。用 `^[inferred]` 标记合成的声明，用 `^[ambiguous]` 标记有争议的声明。一个隐藏其猜测的维基会无声地腐烂；一个标记它的维基会保持值得信赖。

5. **人类策展，LLM 维护。** 人类决定添加哪些来源和提出哪些问题。LLM 处理账本——更新交叉引用，保持一致性，记录矛盾。

6. **Obsidian 是 IDE。** 用户在 Obsidian 中浏览和探索维基。一切都必须是有效的 Obsidian Markdown 并具有可工作的 wikilinks。

## 链接格式

所有连接维基页面的内部链接都受 `OBSIDIAN_LINK_FORMAT` 控制，该格式来自解析的配置（默认：`wikilink`）。

| 设置 | 语法 | 示例 |
|---|---|---|
| `wikilink` *(默认)* | `[[path/to/page]]` 或 `[[path/to/page\|display text]]` | `[[concepts/foo\|foo]]` |
| `markdown` | `[display text](relative/path.md)` | `[foo](../concepts/foo.md)` |

### 生成 Markdown 格式链接

当 `OBSIDIAN_LINK_FORMAT=markdown` 时：
1. 从**当前文件的目录**计算到**目标 `.md` 文件**的路径，使用 `..` 如有需要向上爬。
2. 使用页面标题或自然短语作为显示文本。
3. 始终包含 `.md` 扩展名。

| 当前文件 | 目标 | 相对链接 |
|---|---|---|
| `index.md` | `concepts/foo.md` | `[foo](concepts/foo.md)` |
| `concepts/foo.md` | `entities/bar.md` | `[bar](../entities/bar.md)` |
| `projects/my-project/my-project.md` | `concepts/foo.md` | `[foo](../../concepts/foo.md)` |
| `projects/my-project/concepts/arch.md` | `entities/bar.md` | `[bar](../../../entities/bar.md)` |

`[[path\|display text]]` wikilink 形式映射到 Markdown 模式下的 `[display text](relative/path.md)`。

**范围**：此设置仅影响新写入或更新的链接。现有保险库内容永远不会自动迁移——想要转换旧链接的用户可以运行 `cross-linker` 或 `wiki-lint` 技能。

每个写入技能在生成链接之前都会从配置中读取 `OBSIDIAN_LINK_FORMAT` 并应用正确的格式。

## 配置解析协议

**所有技能必须使用此算法解析配置——不要直接硬编码 `.env` 或全局配置路径。** 这确保了单保险库、多保险库、项目本地和 VPS 设置都能正确工作。

### 全局配置目录

全局配置目录是**XDG 风格**：`$XDG_CONFIG_HOME/obsidian-wiki`（默认 `~/.config/obsidian-wiki`）。已经拥有 `~/.obsidian-wiki` 目录的安装继续使用它——因此现有设置永远不会中断——但任何**新**安装都位于 XDG 路径下。使用以下方式解析它：

```
obsidian_wiki_config_dir() {
  local xdg_dir="${XDG_CONFIG_HOME:-$HOME/.config}/obsidian-wiki"
  local legacy_dir="$HOME/.obsidian-wiki"
  if [[ -d "$legacy_dir" && ! -e "$xdg_dir" ]]; then
    echo "$legacy_dir"
  else
    echo "$xdg_dir"
  fi
}
```

在以下所有内容中，“全局配置目录”指的是 `$(obsidian_wiki_config_dir)`，“全局配置”指的是 `$(obsidian_wiki_config_dir)/config`。

### 解析顺序

0. **行内仓库覆盖 (`@name`)** — 如果用户的请求中包含 `@<name>` 令牌（例如 `@work save this`，`query @personal about X`），则直接解析 `<全局配置目录>/config.<name>` 并使用其 `OBSIDIAN_VAULT_PATH`。这**覆盖**了当前工作目录 `.env` 的向上查找和活动链接，并且仅适用于**该次调用** — 永远不要为 `@name` 请求运行 `ln -sf` 或以其他方式更改活动仓库。如果 `<全局配置目录>/config.<name>` 不存在，则告诉用户它不存在并列出可用的仓库（`wiki-switch` **列表**逻辑），然后停止 — 不要静默地回退到默认值。`@name` 是一个路由指令，不是内容：在将请求的其余部分视为实际指令或页面文本之前，请删除它。
1. **从当前工作目录向上查找** — 在当前目录中查找 `.env` 文件，然后逐级向上查找，直到 `$HOME`。在第一个包含 `OBSIDIAN_VAULT_PATH` 的 `.env` 文件处停止。
2. **全局配置** — 如果找不到本地 `.env`，则读取全局配置（`$(obsidian_wiki_config_dir)/config`）。
3. **提示设置** — 如果两者都不存在，则告诉用户：“未找到配置。运行 `wiki-setup` 初始化您的 wiki。”

`@name` 是一个**每次调用覆盖** — 它针对一个请求的一个仓库。`/wiki-switch <name>` 是**持久默认值** — 它重新指向所有未来请求的活动链接。使用 `@name` 可以从任何地方触摸其他仓库，而不会干扰您的默认（“大脑”）仓库。

```
find_config() {
  # $1 = 从请求中解析的 @name（如果有，否则为空）
  local config_dir
  config_dir="$(obsidian_wiki_config_dir)"
  if [[ -n "$1" ]]; then
    [[ -f "$config_dir/config.$1" ]] && { echo "$config_dir/config.$1"; return; }
    echo ""; return   # 命名仓库缺失 → 调用者报告 + 列表，无回退
  fi
  dir="$PWD"
  while [[ "$dir" != "$HOME" && "$dir" != "/" ]]; do
    [[ -f "$dir/.env" ]] && grep -q "OBSIDIAN_VAULT_PATH" "$dir/.env" && { echo "$dir/.env"; return; }
    dir="$(dirname "$dir")"
  done
  [[ -f "$config_dir/config" ]] && { echo "$config_dir/config"; return; }
  echo ""
}
```

### 仓库范围状态

写入运行时状态（例如 `daily-update`）的技能必须将该状态范围到解析的仓库，而不是全局路径。使用：

```
VAULT_ID=$(echo "$OBSIDIAN_VAULT_PATH" | md5sum 2>/dev/null || md5 -q - <<< "$OBSIDIAN_VAULT_PATH" | cut -c1-8)
STATE_DIR="$(obsidian_wiki_config_dir)/state/$VAULT_ID"
```

### 标准“开始前”块

每个技能的设置部分应读取：

> **解析配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议。首先尊重行内 `@name` 覆盖，然后从当前工作目录查找 `.env`，回退到全局配置，否则提示设置。这提供了 `OBSIDIAN_VAULT_PATH` 和任何特定于工具的路径覆盖。

## 写入配置解析

在起草或重写自然语言 Markdown 之前，使用上述 XDG/遗留算法解析全局配置目录，然后当它存在时读取 `<全局配置目录>/WRITING.md`。缺失或空的 `WRITING.md` 表示没有自定义写作偏好。如果该可选读取失败，则警告并继续使用默认框架指导。

有效优先级是框架不变性 > 当前任务/技能要求 > 当前项目 `AGENTS.md` > 仓库 `AGENTS.md` > 全局 `WRITING.md`。框架不变性包括模式、来源和安全性；特定于操作的请求对当前任务具有权威性。未指定的项目和仓库规则继承自较不具体的层，更具体的同主题规则优先。

写作偏好仅适用于新起草或重写的自然语言字段和正文内容。这包括 YAML 前置的 natural-language 标题和摘要值，但偏好不能更改 YAML 语法、必需键、结构、类型或机器生成的字段。JSON、结构化日志和传递内容保持不变，并保留其必需格式和源保真度。

## 环境变量

通过环境变量配置 wiki（参见 `.env.example`）。唯一必需的变量是仓库路径 — 其他所有内容都有合理的默认值。

- `OBSIDIAN_VAULT_PATH` — wiki 存放位置 **(必需)**
- `OBSIDIAN_SOURCES_DIR` — 原始源文档的位置
- `OBSIDIAN_CATEGORIES` — 以逗号分隔的类别列表
- `WIKI_SKIP_PROJECTS` — 以逗号分隔的子字符串；任何包含其中一个的项目的目录都将从历史记录摄取中排除（扫描 + delta + 元数据）。参见历史记录摄取技能中的“项目范围”步骤。
- `CLAUDE_HISTORY_PATH` — 查找 Claude 对话数据的位置
- `CODEX_HISTORY_PATH` — 查找 Codex 会话数据的位置
- `HERMES_HOME` — 查找 Hermes 代理数据的位置
- `OPENCLAW_HOME` — 查找 OpenClaw 数据的位置
- `COPILOT_HISTORY_PATH` — 查找 Copilot 会话数据的位置
- `OBSIDIAN_LINK_FORMAT` — 内部链接语法：`wikilink`（默认）或 `markdown`
- `WIKI_TOKEN_WARN_THRESHOLD` — 当全 wiki 令牌估计值超过此值时，在 `wiki-status` 中发出警告（默认：`100000`）。设置为 `0` 以禁用。参见 `wiki-status` 以获取令牌足迹报告。
- `WIKI_STAGED_WRITES` — 当 `true` 时，所有 LLM 编写的页面将先发送到 `_staging/<category>/` 以供人工审核，然后再提升。参见 `wiki-setup` 和 `wiki-stage-commit` 以获取详细信息。
- `CODE_UNDERSTANDING_BACKEND` — wiki-update 在提炼之前如何理解项目：`auto`（CodeGraph 可用时使用，否则使用内置 ast-extract + rg；默认）、`builtin` 或 `codegraph`（显式要求；如果不可用则警告/错误）。
- `CODE_UNDERSTANDING_CODEGRAPH_BIN` — 当 codegraph 不在 PATH 上时，可选的 codegraph 二进制路径。
- `CODE_UNDERSTANDING_CODEGRAPH_BIN` — 当 codegraph 不在 PATH 上时，可选的 codegraph 二进制路径。
  它们解析方式与 `OBSIDIAN_VAULT_PATH` 类似：真实的環境变量优先（空值视为未设置），然后是从项目目录向上查找的最近 `.env`，然后是全局配置（`$(obsidian_wiki_config_dir)/config`），然后是默认值。
- `OBSIDIAN_MAX_PAGES_PER_INGEST` — 每个 `wiki-ingest` 运行创建/更新的页面上限（默认：`15`）。参见 `wiki-ingest`，步骤 4。
- `LINT_SCHEDULE` — `daily-update` 还运行 `wiki-lint` 的频率：`daily` \| `weekly`（默认） \| `manual`。参见 `daily-update`，步骤 4a。

不需要 API 密钥 — 运行这些技能的代理已经内置了 LLM 访问权限。

## 操作模式

wiki 支持三种摄取模式：

| 模式 | 使用场景 | 发生什么 |
|---|---|---|
| **追加** | 小的增量更新 | 通过元数据计算增量，仅摄取新/修改的源 |
| **重建** | 需要重大漂移、需要全新开始 | 将当前 wiki 归档到 `_archives/`，清除，重新处理所有源 |
| **恢复** | 需要回退 | 恢复以前的归档 |

使用 `wiki-status` 查看增量并获取建议。使用 `wiki-rebuild` 执行归档/重建/恢复操作。

## 参考

有关特定操作的详细信息，请参阅配套技能：
- **wiki-status** — 审计已摄取的内容，计算增量，建议追加 vs 重建
- **wiki-rebuild** — 归档当前 wiki，从头开始重建，或从归档中恢复
- **wiki-ingest** — 将源文档提炼为 wiki 页面和原始文本/聊天/日志数据
- **claude-history-ingest** — 摄取 Claude 对话历史记录
- **codex-history-ingest** — 摄取 Codex CLI 会话历史记录
- **wiki-query** — 针对 wiki 回答问题
- **wiki-lint** — 审计和维护 wiki 健康状况
- **wiki-setup** — 初始化新的仓库
