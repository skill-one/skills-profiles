# LLM Wiki — 知识蒸馏模式

你正在维护一个持续累积的知识库。这个维基不是聊天机器人——它是一个**编译好的工件**，知识被蒸馏一次并保持最新，而不是在每次查询时重新推导。

## 三层架构

### 第一层：原始来源（不可变）

用户的原始文档——文章、论文、笔记、PDF、对话记录、书签、**以及图片**（截图、白板照片、图表、幻灯片捕获）。这些文档永远不会被系统修改。它们存放在用户保存它们的地方（通过 `.env` 中的 `OBSIDIAN_SOURCES_DIR` 配置）。图片是一流来源：摄取技能通过阅读工具的视觉支持读取它们，并将它们的解释内容视为推断，除非它是逐字转录的文本。图片摄取需要一个支持视觉的模型——没有视觉支持的模型应该跳过图片来源并报告跳过的文件。

将原始来源视为“源代码”——权威但难以直接查询。

不要将其与库中的 `_raw/` 阶段文件夹混淆，后者是另一回事：一个用于快速捕获和等待提升的草稿邮箱（参见 `wiki-capture` 和 `wiki-ingest`）。那里的文件不是第一层来源，但 `wiki-ingest` 在提升时仍然移动而不是删除它们，因为有些文件没有其他副本。

### 第二层：维基（由 LLM 维护）

一系列相互连接的 Obsidian 兼容的 Markdown 文件按类别组织。这是编译后的知识——综合、交叉引用、可导航。每个页面都有：

- YAML 前置内容（标题、类别、标签、来源、时间戳）
- Obsidian `[[wikilinks]]` 连接相关概念
- 清晰的来源——每个声明都可以追溯到来源

维基位于通过 `.env` 中的 `OBSIDIAN_VAULT_PATH` 配置的路径下。

### 第三层：模式（此技能 + 配置）

控制维基结构规则的规则——类别、约定、页面模板和操作工作流。模式告诉 LLM *如何*维护维基。

## 维基组织

库有两层结构：**类别**（知识类型）和**项目**（知识来源）。

### 类别

将页面组织到这些默认类别中（可以在 `.env` 中自定义）：

| 类别 | 目的 | 示例 |
|---|---|---|
| `concepts/` | 概念、理论、心智模型 | `concepts/transformer-architecture.md` |
| `entities/` | 人物、组织、工具、项目 | `entities/andrej-karpathy.md` |
| `skills/` | 如何知识、程序 | `skills/fine-tuning-llms.md` |
| `references/` | 特定来源的摘要；学术论文使用 Paper Deep-Dive Template（见下文） | `references/attention-is-all-you-need.md` |
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

**当知识是项目特定时**（仅适用于一个代码库的调试技术、项目特定的架构决策），将其放在 `projects/<project-name>/<category>/` 下。

**当知识是通用时**（如“React Server Components”的概念、像“Andrej Karpathy”的人、广泛适用的技能），将其放在全局类别目录中。

**交叉引用：** 项目页面应 `[[wikilink]]` 到全局页面，反之亦然。项目概述页面应链接到与该项目相关的关键概念、技能和实体页面——无论它们是放在项目下还是全局。

**命名规则：** 项目概述文件必须命名为 `<project-name>.md`，而不是 `_project.md`。Obsidian 的图视图使用文件名作为节点标签——`_project.md` 在图中使每个项目都显示为 `_project`，使其难以阅读。所以 `projects/my-project/my-project.md`、`projects/another-project/another-project.md` 等。

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
- [[projects/my-project/concepts/main-architecture]] — 项目特定的架构

## 相关
- [[entities/some-service]] — 部署平台
```

## 特殊文件

每个维基在其根目录下都有这些文件：

> **使用 `obsidian-wiki memory` 写它们，不要手动编写。** `index.md`、`log.md`、`hot.md` 以及 `_meta/` 表共享一个建议锁，并原子写入；并行运行中的手动编辑会丢失第二个写入。`obsidian-wiki memory sync <VERB> key=value` 一次完成所有三个操作。完整过程——动词、`Key Takeaways` 插槽保持为你的所有内容、所有者配置文件和待办事项索引——在 [`references/MEMORY.md`](references/MEMORY.md) 中。

### `index.md`
面向内容的目录按类别组织。每项都有一个简短的摘要和标签。每次摄取操作后重建此文件。格式：

```markdown
# Wiki Index

## Concepts
- [[transformer-architecture]] — 适用于序列建模的主导架构 ( #ml #architecture)
- [[attention-mechanism]] — Transformer 的核心构建块 ( #ml #fundamentals)

## Entities
- [[andrej-karpathy]] — AI 研究员、教育家、前 Tesla AI 总监 ( #person #ml)
```
**格式规则**：在开括号后添加一个空格和标签。
❌ 不要：`description (#tag)` — 会破坏标签解析
✅ 要：`description ( #tag)` — 正确的空格和标签解析

### `log.md`
按时间顺序的仅追加记录，跟踪每次操作。每项都是可解析的：

```markdown
## Log

- [2024-03-15T10:30:00Z] INGEST source="papers/attention.pdf" pages_updated=12 pages_created=3
- [2024-03-15T11:00:00Z] QUERY query="How do transformers handle long sequences?" result_pages=4
- [2024-03-16T09:00:00Z] LINT issues_found=2 orphans=1 contradictions=1
- [2024-03-17T10:00:00Z] ARCHIVE reason="rebuild" pages=87 destination="_archives/..."
- [2024-03-17T10:05:00Z] REBUILD archived_to="_archives/..." previous_pages=87
```

### `.manifest.json`
跟踪每个已摄取的来源文件——路径、时间戳，以及它产生的维基页面。这是 delta 系统的骨干。有关完整模式，请参阅 `wiki-status` 技能。

该清单启用：
- **Delta 计算** — 自上次摄取以来新增或修改的内容
- **追加模式** — 仅处理 delta，不处理所有内容
- **审计** — 哪个来源产生了哪个维基页面
- **陈旧检测** — 来源已更改但维基页面未更新

**来源密钥合同 (v2)。** 来源密钥——`.manifest.json` 中的 `sources` 密钥、页面上的 `sources:` 前置内容值以及项目的 `source_repo`——必须机器可移植。库跨机器同步，因此裸绝对路径（`/Users/...`、`/home/...`）永远不会是有效的存储密钥。这是唯一的规范定义；其他技能参考它而不是重新陈述它。

| 来源存储位置 | 规范密钥形式 | 示例 |
|---|---|---|
| 在库内 | **库相对路径** — POSIX 分隔符，没有前导 `./`，没有 `..` | `Raw/database/postgres.pdf`、`Clippings/article.md` |
| 在 `$HOME` 下 | **`home` 相对路径** — 以 `~` 开头 | `~/.claude/projects/-Users-name-my-app/abc.jsonl` |
| 根本不是文件 | **伪密钥** — 任何 `scheme:`/`://` 标识符，被视为不透明 | `url:https://example.com/article`、`agent:claude/<session-id>` |

规则：

1. **永远不要存储裸绝对路径。** 在写入之前转换，而不是写入后转换。
2. **在比较之前进行规范化。** 展开波浪号和环境变量，将库相对密钥与库根目录解析，并将 `scheme:`/`://` 伪密钥视为不透明标识符。永远在比较原始字符串之前进行规范化。
3. **身份在路径更改时保持不变。** 同一个逻辑来源在跨机器上保持相同的密钥。
4. **伪密钥是一个开放的命名空间。** 使密钥成为伪密钥的是其形状（`scheme:` 或 `://`，因此它永远不会被误认为是文件路径），而不是固定的名称列表。推荐名称：`repo:<host/owner/name>` 用于 git 项目，`url:<canonical-url>` 用于网页，`agent:<agent>/<id>` 用于代理会话。既不在库中也不在 `$HOME` 下来源仍然需要一个——不要让它回退到绝对路径。
5. **项目身份是一个仓库，而不是一个检出。** 在 `projects` 块中，通过 `source_repo` (`host/owner/name`) 来识别项目，而不是机器路径。如果有用的特定于机器的检出位置，则应将其放在可选的 `source_cwd_hint` (`~` 相对)，永远不会放在身份中。

读取是向后兼容的：一个充满绝对密钥的现有清单仍然可以工作，并且 `scripts/manifest.py migrate <vault> --dry-run` 将其转换为合同 v2（合并冲突，保留最新的 `ingested_at`）。**如果库在机器之间移动**，其绝对密钥以 *旧* 库路径为根，这与新库或 `$HOME` 都不匹配——显式传递旧根（如果库在多个位置存在）。（命令然后报告 `nothing portable to write — N key(s) kept non-portable` 而不是声称成功。新写入通过相同的规范化，因此技能可以将绝对路径传递给 `obsidian-wiki cache-update`，并且仍然有一个可移植的密钥出现在清单中。

**记录来源。** 当你编写清单条目时，用库相对页面路径填充 `pages_created` 和 `pages_updated`，该来源贡献了哪些页面。这是使重新摄取（当来源更改时）能够找到要重新访问的页面的关键，而不是猜测。

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
    一两句话，≤200 字符，以便读者（或另一个技能）在不打开页面的情况下预览此页面。
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

- 来源的中心声明，直接释义。
- 来源暗示但未明确说明的概括。 ^[inferred]
- 两个来源对某个图形意见不一致。 ^[ambiguous]

使用 [[wikilinks]] 连接到相关页面。

## 未解决的问题

尚未解决或需要更多来源的事情。

## 来源

- [[references/attention-is-all-you-need]] — 原始论文
```

**解析安全的标量。** 写自由文本前置内容值——至少 `title` 和 `summary`——使用折叠标量语法（`>-`）如上所示：包含 `: `（冒号 + 空格）、`#` 或引号的无符号标量会破坏 YAML 解析，Obsidian 然后报告“无效属性”并隐藏前置内容。在 `title: >-` / `summary: >-` 之后的行上保持值的缩进。

## 论文深度解析模板

通用模板适用于大多数来源。**学术论文是例外。** 对于 ML/AI/LLM/VLM（以及类似）论文落入 `references/`，其内容存在于架构、方程式和结果表中——正好是简洁的“关键思想”列表扁平化掉的内容。为此，请使用下面更丰富的模板。这是唯一一个“编译，不要检索”让位于深入、自包含的逐步分析的地方，读者可以研究它而不是论文。

Obsidian 原生渲染所需的基本结构，因此不需要额外的工具：Mermaid 管理区域内的图表、`$$…$$` LaTeX（MathJax）、Markdown 表格和 `![[image]]` / `![[paper.pdf#page=N]]` 嵌入。

仅当来源是具有承载图形或方程式的学术论文（arXiv/conference）时才使用此模板。其他所有内容都使用上面提到的通用页面模板。前置内容、来源标记、置信度、生命周期和 `relationships:` 保持不变——只有正文部分不同。

````markdown
---
# ...必需的前置内容，与通用模板相同；类别: references...
---

# Paper Title

> [!tldr] 一句话总结：新内容是什么，加上标题结果。

## 问题与动机

论文解决了什么已损坏或缺失的东西。

## 方法 / 架构

散文式逐步分析。将论文的真实架构图作为主要视觉（参见 `wiki-ingest` 中的 *Academic papers* 以获取 PyMuPDF 提取配方）。当无法提取图形时，仅当没有视觉支持时才回退到 Mermaid 流程图。

![[attachments/<slug>-fig1.png]]
*图 N (作者年份): 一行简短说明。*

## 关键方程

1-3 个核心方程作为显示数学，而不是反引号代码：

$$ \mathcal{L} = \mathbb{E}_{x}\!\left[-\log p_\theta(y \mid z)\right] $$

## 结果

标题数字作为表格，而不是逗号分隔的块——如果论文有一个，则嵌入一个关键结果/激励图形（缩放图、基准图表、能力马赛克）：

| 方法 | 基准 | 指标 | 成本 |
|---|---|---|---|
| 基线 | … | … | … |
| **本文** | … | … | … |

![[attachments/<slug>-resultsN.png]]
*图 N (作者年份): 一行简短说明。*

## 限制

论文承认或回避的内容。标记为“在行间阅读”的内容。

## 相关

到邻近工作的类型化 `[[wikilink]]`。

## 来源

- 可点击的规范链接，例如 <https://arxiv.org/abs/XXXX.XXXXX>

A 从论文的散文中重建的 Mermaid 图形是综合，而不是转录——当解释是非平凡的时，将其视为 `^[inferred]`。

## 来源标记

维基页面上的每个声明都有三种来源状态之一。将它们内联标记，以便读者（以及未来的摄取过程）能够区分信号和综合。

这些是框架默认值。库的 `AGENTS.md` 可能会添加标记或工作流标志。保留所有者扩展并独立于提取/推断/模糊真实性轴处理正交工作流标志。

| 状态 | 标记 | 含义 |
|---|---|---|
| **提取** | *(无标记——默认)* | 来源实际说的内容的释义。 |
| **推断** | `^[inferred]` 后缀 | 由 LLM 综合的声明——来源没有直接说明的连接、概括或暗示。 |
| **模糊** | `^[ambiguous]` 后缀 | 来源意见不一致，或者来源不清楚。 |

示例：

```markdown
- Transformers 并行化跨位置，与 RNN 不同。
- 这是它们在现代硬件上扩展更好的原因。 ^[inferred]
- GPT-4 的训练数据约为 13T tokens。 ^[ambiguous]
```

**为什么这种语法：**
- `^[...]` 在 Obsidian 中与脚注相邻——干净地渲染，永远不会与 `[[wikilinks]]` 冲突。
- 内联（后缀）以便单个项目保持为单个项目。
- 默认为提取意味着现有页面没有标记保持有效。

**前置内容摘要：** 可选地在此级别显示大致混合，以便用户可以扫描推测性强的页面而无需阅读它们：

```yaml
provenance:
  extracted: 0.72   # 粗略的句子/项目数比例，无标记的句子/项目保持不变
  inferred: 0.25
  ambiguous: 0.03
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: 2024-03-15
tier: supporting
created: 2024-03-15T10:30:00Z
updated: 2024-03-15T10:30:00Z
```

这些是摄取技能在创建/更新时编写的最佳努力数字。`wiki-lint` 重新计算它们并标记漂移。该块是可选的——没有它的页面按惯例被视为完全提取。

## 关系类型

页面正文中的普通 `[[wikilinks]]` 不携带语义权重——它们表示“相关”，而不是 *如何*。可选的 `relationships:` 前置内容块为知识图谱添加了带类型的、方向的边缘。

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

每个条目有两个必需字段：
- `target` — 一个维基链接（使用与 `OBSIDIAN_LINK_FORMAT` 相同的格式）到相关页面
- `type` — 以下允许的语义类型之一

### 允许的关系类型

下面的表格是框架默认的允许列表。库的 `AGENTS.md` 可能会扩展它；消费者必须使用有效的允许列表并保留所有者语义而无需强制。

| 类型 | 含义 | 示例 |
|---|---|---|
| `extends` | 此页面扩展或概括了目标 | GPT 扩展 Transformer Architecture |
| `implements` | 此页面是目标概念的具体实现 | BERT 实现掩码语言建模 |
| `contradicts` | 此页面的声明与目标冲突或反驳 | 证据 A 与证据 B 冲突 |
| `derived_from` | 此页面基于或改编自目标 | 微调衍生自迁移学习 |
| `uses` | 此页面依赖于或依赖于目标 | RAG 使用向量数据库 |
| `replaces` | 此页面取代或弃用目标 | GPT-4 取代 GPT-3 |
| `related_to` | 捕获所有其他更强的方向类型不适用 | 概念 A 与概念 B 相关 |

### 规则

- **可选字段**——如果知道没有类型关系，则省略整个块。未标记的维基链接保持有效，并由 `wiki-export` 视为 `related_to`
- **不要重复**——如果 `[[foo]]` 已经作为内联维基链接出现，则 `relationships:` 条目只是为其添加类型；它不是第二个链接。
- **方向很重要**——声明关系的页面是 *来源*；`target` 是目的地。仅从此页面的角度声明关系。
- **不要编造**——只有当来源材料使关系方向和类型清晰时才添加类型条目。当不确定时，使用 `related_to` 或省略。

读取 `relationships:` 的技能：`wiki-export`（发出类型边缘）、`cross-linker`（在推断链接时写入类型条目）、`wiki-query`（在答案中显示类型并遍历类型边缘图进行多跳“X 如何连接到 Y”路径查询——有界的 BFS over `relationships:` 邻接矩阵，仅限于前端内容）。

## 置信度和生命周期

每个页面都带有两个正交的信任信号和一个可选的替代链接。

所需的必要性和生命周期值是框架默认值。库的 `AGENTS.md` 可能会扩展生命周期值或使信任字段可选。验证器必须应用有效的所有者模式，同时仍然验证任何存在的信任值。

确定性的 `wiki-lint` 路径验证 `_meta/trust-ledger.json`；它不会从来源字符串重新计算置信度。新页面或内容发生实质性变化的页面被标记为手动审查。只有在明确人工批准后才能刷新账本。

**每项技能的默认值**（摄取技能自动计算此内容）：

| 技能 | base_confidence | lifecycle |
|---|---|---|
| `wiki-ingest` (URL) | `0.17 + 0.5 × classify(url)` | `draft` |
| `wiki-ingest` (单个文档) | 每个来源分类器 | `draft` |
| `wiki-ingest` (多个文档) | `min(N/3,1)×0.5 + avg_q×0.5` | `draft` |
| `wiki-research` | 变化很大，通常为 0.85+ | `draft` |
| `wiki-capture` | 0.42 | `draft` |
| `*-history-ingest` | 0.42 | `draft` |
| `wiki-update` | 0.59 | `draft` |
| `wiki-synthesize` | `min(input_pages.base_confidence)` | `draft` |

没有 API 密钥是必要的——运行这些技能的代理已经内置了 LLM 访问。

## 操作模式

维基支持三种摄取模式：

| 模式 | 使用时机 | 发生的事情 |
|---|---|---|
| **追加** | 小型增量更新 | 通过清单计算 delta，仅摄取新/修改的来源 |
| **重建** | 需要重大漂移、需要全新开始 | 将当前维基存档到 `_archives/`，清除，重新处理所有来源 |
| **恢复** | 需要回退 | 恢复以前的存档 |

使用 `wiki-status` 查看差异并获取建议。使用 `wiki-rebuild` 执行存档/重建/恢复操作。

## 参考

有关特定操作的详细信息，请参阅配套技能：
- **wiki-status** — 审计已摄取的内容，计算 delta，建议追加与重建
- **wiki-rebuild** — 存档当前维基，从头开始重建，或从存档中恢复
- **wiki-ingest** — 将来源文档蒸馏成维基页面和原始文本/聊天/日志数据
- **claude-history-ingest** — 摄入 Claude 对话历史记录
- **codex-history-ingest** — 摄入 Codex CLI 会话历史记录
- **wiki-query** — 针对维基回答问题
- **wiki-lint** — 审计和维护维基健康
- **wiki-setup** — 初始化新的库
