---
name: wiki-query
description: 通过搜索编译好的 Obsidian 维基来回答问题。当用户询问其知识库相关的问题、想要在维基中查找信息、询问“我关于 X 知道什么”、“查找所有与 Y 相关的内容”，或需要从维基页面中提取带有引用的合成答案时，使用此技能。也适用于用户想要探索其维基中主题之间的联系，或提出多跳问题，如“X 与 Y 如何关联”、“X 与 Y 之间的链接是什么”、“从 X 到 Z 的链路追踪”或“X 的传递依赖关系是什么”——通过在多个跳点间键入边来回答。适用于任何项目。包含仅索引的快速模式，由“快速回答”、“仅扫描”、“不阅读页面”、“快速查找”触发——从页面摘要和前文返回答案，而无需读取页面正文。通过共享配置解析协议接受内联命名仓库路由，例如“wiki-query @work 我关于 X 知道什么”。
---

# Wiki查询 — 知识检索

你正在针对编译好的Obsidian维基回答问题，而不是原始的源文档。维基包含预合成、相互参照的知识。

## 此技能仅读不写

`wiki-query` 用于回答问题。它**绝对不能**创建或修改任何维基内容。它唯一可以执行的是第6步向`log.md`追加内容。

永远不要，即使当改变看起来明显有益时：
- 创建或编辑`concepts/`、`entities/`、`skills/`、`references/`、`synthesis/`、`journal/`或`projects/`下的页面
- 修改`index.md`、`hot.md`、`_insights.md`或`.manifest.json`

如果用户的消息包含新发现、行动请求（“保存这个”、“禁止X”、“记录下来”）或任何暗示要更改的内容，**不要执行它**。回答问题，**建议**更改，并将用户引导到正确的技能：
- 快速笔记/小窍门 → `wiki-capture --quick`
- 完整的新页面 → `wiki-capture`
- 项目知识同步 → `wiki-update`

## 开始前须知

1. **解决配置** — 遵循`llm-wiki/SKILL.md`中的配置解析协议（内联`@name`覆盖→向上遍历CWD查找`.env`→全局配置→提示设置）。对于跨项目查询没有`@name`的情况，即使它是指向保险库`.env`的符号链接，也优先使用全局配置。这提供了`OBSIDIAN_VAULT_PATH`和任何QMD变量。可以从任何项目目录工作。
2. **从解析的配置中加载QMD设置**，然后再决定检索策略。如果`QMD_WIKI_COLLECTION`被设置，将QMD视为可用的主题，仅受以下传输/工具检查的限制。如果它为空或未设置，在使用grep/页面读取之前，简要说明跳过QMD的原因。
3. 如果`$OBSIDIAN_VAULT_PATH/hot.md`存在，首先读取它——它提供了关于最近活动的即时上下文。如果用户的问题是关于最近摄入的内容，hot.md可能在您甚至打开`index.md`之前就回答了它。
4. 读取`$OBSIDIAN_VAULT_PATH/index.md`以了解维基的范围和结构

## 可见性过滤器（可选）

默认情况下，**所有页面都被返回**，而不管可见性标签如何。这保留了现有行为——除非用户要求，否则不会发生变化。

如果用户的查询包含短语，如**"仅公开"**、**"面向用户"**、**"不包含内部内容"**、**"作为用户会看到的样子"**或**"排除内部"**，请激活**过滤模式**：

- 构建**阻止标签集**：`{visibility/internal, visibility/pii}`
- 在索引传递（第2步），跳过任何候选者的frontmatter标签包含阻止标签
- 在节/完整读取传递（第3-4步），不要读取或引用任何阻止的页面
- 仅从**允许的页面**合成答案——不要提及被排除的页面

没有`visibility/`标签的页面，或标记为`visibility/public`的页面，始终被包含。

在过滤模式下，在步骤6的日志条目中注明过滤器：`mode=filtered`。

## 检索协议

**遵循`llm-wiki/SKILL.md`中的检索原语表**。读取是这个技能的主要成本——使用能回答问题的最便宜的原语，只有在它不能时才升级。永远不要直接跳到完整页面读取。

### 第0步：GraphRAG预传递（快速索引查询——不读取页面）

在打开任何页面之前，查询编译好的图索引：

```bash
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --pretty
```

输出字段：

- **`answer_type`**：`direct` | `path` | `list` | `gap` | `impact` | `bridges` | `hubs` | `clusters` | `surprising` — 决定下一步该做什么。最后五个是**结构意图**：问题是关于保险库的形状，答案完全在`graph`中计算出来（见下文），并且没有任何页面读取。
- **`graph`**：仅对于结构意图存在——计算出的答案。否则为`null`。
- **`candidates`**：按标题/标签/摘要匹配+度数排名的前几页，包括分数和摘要
- **`should_read`**：最值得打开的页面——从这里开始，而不是推测性地读取许多文件
- **`path`**：对于多跳查询，两个概念之间的最短维基链接路径
- **`god_nodes_relevant`**：与你的查询术语相关的中心页面——总是有用的上下文
- **`index_only`**：如果`true`，顶级候选者的摘要已经回答了问题——跳过页面读取
- **`temporal`**：`as_of`、`retrievable`、`excluded_historical`——事件时间过滤器阻止了多少页面（见下文）

**结构意图**——这些完全从图中回答。用户的措辞会自动路由：

| 用户询问 | `answer_type` | `graph`包含 |
|---|---|---|
| "如果删除X会破坏什么" / "X依赖什么" / "什么链接到X" | `impact` | `direct_dependents`、`transitive_dependents`、`total` |
| "哪些页面连接我的集群" / "我的保险库会碎片化" | `bridges` | 按betweenness排序的页面，带有`label`和`connects_labels` |
| "什么居中" / "顶级中心" / "我的主要主题" | `hubs` | 按度数排序的页面，带有入/出拆分 |
| "我有哪些集群" / "我的维基如何组织" | `clusters` | 每个集群的`label`、`size`、`cohesion`、`fragmented` |
| "惊人的连接" / "意外的链接" | `surprising` | 跨集群链接，按稀有度排序 |

直接报告`graph`负载——**不要**通过读取页面重新推导它。如果结构问题命名了一个无法解析的页面，CLI会回退到`direct`，并且`graph`为`null`。

**决策树：**

1. 如果`graph`非空→结构答案已完成。报告它并停止；不读取页面。
2. 如果`index_only: true`→直接从`candidates[0].summary`回答。跳过步骤1-4，直接进入步骤5。
3. 如果`answer_type == "path"`且`path`非空→连接在`path`中。只读取这些页面。
4. 否则→只打开`should_read`页面（不是所有候选者）。这取代了旧流程中需要推测性读取5-10个文件的做法。

> 这里使用的图排除了保险库账本文件（`index.md`、`log.md`、`hot.md`、`_insights.md`）。它们链接到几乎每个页面，所以包括它们使任何两个页面看起来大约是2跳远，并产生了无意义的`A → index → B`路径。

**事件时间**。页面可能携带`valid_from` / `valid_until` / `superseded_by` frontmatter。一个`valid_until`已过期的页面是**历史性的**：它仍然在保险库和图中，但默认情况下会从候选者中排除，所以“我们使用哪个X？”的答案是用现在真实的而不是最早写的内容来回答的。

- 当`temporal.excluded_historical`非零时，如果它与答案相关紧要，请说明——用户可能是在询问被取代的状态。
- 如果问题是关于过去的（“2025年我们使用什么”、“迁移之前”），使用`--as-of YYYY-MM-DD`重新运行以检索当时的内容。
- 使用`--include-historical`当用户明确要求完整历史，或者当你在追踪决策如何变化时。
- 返回的候选者携带`superseded_by`会命名它的替代品——跟随它，而不是报告过时的声明为当前。

```bash
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --as-of 2025-06-01 --pretty
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --include-historical --pretty
```

结构意图故意忽略了此过滤器：删除页面仍然会破坏链接到它的历史页面，所以爆炸半径不会因为依赖项不再当前而缩小。

**回退**（如果`obsidian-wiki`未安装）：像正常一样使用grep和`index.md`进行步骤1。

### 第1步：理解问题

对查询类型进行分类：
- **事实查询**——"X是什么？"→找到相关页面
- **关系查询**——"X如何与Y相关？" / "什么与X矛盾？"→找到两个页面、它们的交叉引用以及它们的`relationships:` frontmatter块用于类型边缘
- **路径/多跳查询**——"X如何连接到Y？" / "什么将X链接到Y？" / "从X到Z追踪链条" / "X转 transitively 依赖什么"→X和Y没有直接链接；连接通过中间页面运行。使用步骤4b中的多跳图遍历。
- **综合查询**——"关于X的当前想法是什么？"→找到所有触摸X的页面，综合
- **差距查询**——"我不知道X的哪些内容？"→找到缺失的内容，检查开放问题部分

同时决定**模式**：
- **仅索引模式**——由“快速答案”、“仅扫描”、“不要读取页面”、“快速查找”触发。在步骤3停止。仅从frontmatter + `index.md`回答。
- **正常模式**——下面完整的分层管道。

### 第2步：索引传递（低成本）

在不打开任何页面正文的情况下构建候选集：

- 你已经读取了上面的`index.md`——将其用作第一个过滤器。它列出了每个页面的简短描述和标签。
- 使用`Grep`扫描页面**frontmatter**仅用于标题、标签、别名和摘要匹配。一个像`^(title|tags|aliases|summary):`的范围到保险库`.md`文件的模式比内容grep便宜得多。
- 收集按以下顺序排名的前5-10个候选页面路径：
  1. 标题或别名完全匹配
  2. 标签匹配
  3. 摘要字段包含查询术语
  4. `index.md`条目包含查询术语
- **在每排名桶内应用层级顺序**：当两个候选者得分相同，优先`tier: core`而不是`tier: supporting`而不是`tier: peripheral`。使用与扫描其他字段相同的cheap grep读取`tier:` frontmatter字段。没有`tier:`字段的页面被视为`supporting`。

**跟踪检索计数（用于步骤5/6中的透明度报告）：**
- `candidates_seen` — 在修剪到前5-10之前匹配*任何*排名标准的总不同页面。
- `candidates_used` — 你实际上携带了多少个进入步骤3/4。
- `dropped` — `candidates_seen − candidates_used`，即存在但从未读取的匹配项。如果这个非零，命名被丢弃的页面（如果有很多，命名计数），以便用户知道检索不是详尽的——这不是错误，只是对被排除内容的诚实核算。

如果你在**仅索引模式**，在这里停止。从`summary:`字段、标题和`index.md`描述中回答。明确标记答案：**"(仅索引答案——未读取页面正文；以下事实来自页面摘要，可能会遗漏细节)"**。然后跳到步骤5。

### 第2b：QMD语义传递（可选——需要解析配置中的`QMD_WIKI_COLLECTION`）

**GUARD：如果`$QMD_WIKI_COLLECTION`在配置解析后为空或未设置，跳过此整个步骤并继续步骤3。在您的工作更新中提及缺失的变量。**

> **没有QMD？** 跳到步骤3并直接使用`grep`对保险库。QMD更快、概念感知，但grep路径是完全功能的。见`.env.example`进行设置。

如果`QMD_WIKI_COLLECTION`被设置，在到达`grep`之前运行QMD，除非问题已经完全由`hot.md`或`index.md`元数据回答。当问题语义、特定于项目、要求相关上下文或使用可能不会在标题/frontmatter中逐字出现的术语时，特别推荐QMD。

从`$QMD_TRANSPORT`选择QMD传输：

- `mcp`（默认）：使用在代理中配置的QMD MCP工具。
- `cli`：运行本地qmd CLI。如果设置了`$QMD_CLI`，请使用它；否则使用`qmd`。

有关详细CLI命令选择、维护和VM注意事项，使用安装时本地的`$qmd-cli`技能。

如果选定的传输不可用（没有MCP工具、`qmd`不在PATH上，或命令出错），跳过QMD并继续步骤3。

对于MCP传输：

```
mcp__qmd__query:
  collection: <QMD_WIKI_COLLECTION>   # 例如 "knowledge-base-wiki"
  intent: <用户的提问>
  searches:
    - type: lex    # 关键字匹配——适用于确切名称、文件路径、错误消息
      query: <关键术语>
    - type: vec    # 语义匹配——适用于概念、模式、"X像什么"
      query: <将问题改写为描述>
```

对于CLI传输，从`$QMD_CLI_SEARCH_MODE`选择命令：

保持类似运算符或标点符号密集的标记，如`no-sudo`、`ansible_become=false`和`~/.local/bin`在`lex:`行中。将`vec:`行改写为纯自然语言，不要带连字符`-term`单词；QMD将`-term`视为否定，而否定在`vec`/`hyde`查询中不受支持。

- `quality`（默认）：最佳相关性；CPU上较慢。
  ```bash
  ${QMD_CLI:-qmd} query $'lex: <key terms>\nvec: <question rephrased as a description>' -c "$QMD_WIKI_COLLECTION" -n 8 --files
  ```
- `balanced`：无LLM重新排序的混合搜索；当`quality`太慢时使用。
  ```bash
  ${QMD_CLI:-qmd} query $'lex: <key terms>\nvec: <question rephrased as a description>' -c "$QMD_WIKI_COLLECTION" -n 8 --no-rerank --files
  ```
- `fast`：语义仅召回，或当确切名称、文件路径或错误消息很重要时使用`search`。
  ```bash
  ${QMD_CLI:-qmd} vsearch "<question rephrased as a description>" -c "$QMD_WIKI_COLLECTION" -n 8 --files
  ```

使用`${QMD_CLI:-qmd} get "#docid"`通过CLI输出来检索按docid排名的文档。

返回的片段或排名文件充当预读节摘要。如果它们完全回答了问题，跳过步骤3并直接进入步骤4（只读取QMD排名最高的页面）。如果不是，使用排名文件列表来指导步骤3中要grep或读取的文件。

将QMD命中折叠到来自步骤2的相同`candidates_seen`计数（按路径去重——一个由frontmatter grep和QMD找到的页面只计一次）。

**防御性过滤器：从维基集合结果中丢弃任何`_raw/`路径**。维基集合应该只索引编译好的页面，但配置错误的集合（见`.env.example`）可能会索引`_raw/`——包括位于`_raw/_archived/`中的已过时草稿，这些草稿已经被提升的页面取代了。在从`$QMD_WIKI_COLLECTION`使用QMD命中之前，检查其路径：如果它包含`_raw/`，则从维基集合结果集中丢弃它（它可能仍然通过`$QMD_PAPERS_COLLECTION`真实地出现，作为原始来源引用）。这使配置错误的集合退化为“缺少召回”而不是“无声地引用一个过时的草稿作为编译知识。” 如果您看到从维基集合返回的`_raw/`路径，请在您的工作更新中提及用户知道他们的集合范围需要修复（见`.env.example` QMD部分）。

**当问题可能在`_raw/`中包含源材料时，也搜索`papers`：**

如果`QMD_PAPERS_COLLECTION`被设置，并且用户询问的主题可能由摄入的论文（研究、理论、背景）涵盖，运行针对论文集合的并行搜索。在您的答案中将原始来源与编译的维基页面分开引用。

### 第3步：节传递（中等成本——如果步骤2/2b无结论）

对于每个顶级候选者，拉取相关节*而不读取整个页面*：

- 使用`Grep -A 10 -B 2 "<query-term>" <candidate-file>`只获取匹配周围的行。
- 这通常返回每个命中15-30行，而不是100-500行。
- 如果节grep给出明确答案，直接进入步骤5。

### 第4步：完整读取（昂贵——最后手段）

只有在步骤2和3无法回答问题时：

- 阅读**前 3** 名候选页的全文。选择要阅读的 3 页时，应用层级排序：先读`核心`页面，再读`支持`页面，除非`外围`页面是唯一匹配项，否则跳过`外围`页面。
- 如果答案需要交叉引用，则从这些页面最多跟随一个`[[wikilinks]]`跳转。
- **对于关系查询**（“X 与 Y 的关系是什么？” / “什么与 X 相矛盾？”）：还要阅读候选页面的`relationships:`页眉块。每个条目都给出一个有类型的方向性边（`extends`、`implements`、`contradicts`、`derived_from`、`uses`、`replaces`、`related_to`）。在答案中明确展示这些信息——"页面 A *与页面 B 相矛盾*（有类型的边）"比"页面 A 链接到页面 B"更有用。
- 检查“开放问题”部分以查找已知空白。
- 如果仍然不足，**则**回退到整个库的广泛内容 grep。告诉用户你升级了——这是昂贵的路径，他们应该知道。

### 第 4b 步：多跳图遍历（有类型的边）

普通检索会显示提及查询术语的页面。它不能回答**路径/多跳查询**——"X 与 Y 的连接方式是什么？"、"X 依赖哪些传递关系？"、"从 X 到 Z 追踪链"——当 X 和 Y 从未出现在同一页面上时。答案存在于有类型边的图的*形状*中，而不是任何单个页面的正文里。这是执行这一步。

仅对路径/多跳查询（或在关系查询未在两个页面之间返回直接边时）运行此步骤。它完全由页眉构建——此处从不读取页面正文。

1. **构建有类型边的邻接矩阵（快速）。** 一次扫描中检索每个页面的`relationships:`块——`Grep -A 20 "^relationships:" <vault>/**/*.md`（仅页眉）。每个条目生成一个有方向的、有类型的边`source —type→ target`。也添加反向方向作为可遍历的边（标记为`(reverse)`），因为“连接到”是对称的，即使类型断言是方向性的。普通正文`[[wikilinks]]`计数仅作为无类型的`related_to`边，仅当你需要它们来完成路径时——优先使用有类型的边。

2. **定位端点。** 使用来自第 2 步的注册表将 X（如果查询命名了两个，则还有 Y）解析为页面路径。如果端点不明确，选择`tier: core`的候选项并注明假设。

3. **有界 BFS。** 如果安装了`obsidian-wiki`，让 CLI 首先在有向链接图上执行遍历——它是精确且即时的：

   ```bash
   obsidian-wiki graph-analyse "$OBSIDIAN_VAULT_PATH" --path "<X>" "<Y>"                  # 两端点：最短链 + 跳数
   obsidian-wiki graph-analyse "$OBSIDIAN_VAULT_PATH" --around "<X>" --depth 3 [--direction out|in]  # 一端点：可达页面按跳数
   ```

   `--path` 在`--direction out`之前跟随任一方向的链接；`--around --direction in`回答“什么依赖于 X”（其爆炸半径）。然后用第 1 步的有类型边装饰返回的链（CLI 看到`[[wikilinks]]`，而不是关系类型）。否则，或为了找到替代路径，手动遍历：
   - **默认最大 3 跳**（连接很少在 3 跳之外有意义）。仅在用户说“深层” / “无论需要多少跳”时才增加到 4。
   - **前沿上限：** 一旦访问集超过约 60 页，停止扩展节点——报告部分结果，而不是在整个库中发散。
   - 对于**两端点查询**（X→Y）：找到最短路径后立即停止；然后简要继续以显示最多 2 条替代路径（如果存在）。
   - 对于**一端点查询**（X 传递性）：收集在深度限制内可达的所有节点，按跳数距离分组。

4. **报告路径和边类型。** 显示链，而不仅仅是端点——有类型的边*就是*答案：

   ```
   [[concepts/transformers]] —uses→ [[concepts/attention]] —derived_from→ [[concepts/rnn-seq2seq]] —contradicts (reverse)→ [[concepts/lstm]]
   ```

   说明跳数以及任何跳是否为`(reverse)`遍历或无类型的`related_to`回退（这些链较弱——标记它们）。如果在深度限制内没有路径，明确说明： "在 3 跳内从 X 到 Y 没有有类型边的路径——它们位于图的断开区域。" 这本身就是一个有用的发现（一个图空白）。

**成本保护：** 此步骤仅通过 grep 读取页眉。如果邻接矩阵 grep 返回空（还没有页面使用`relationships:`），报告图没有有类型边可供遍历，并建议运行`cross-linker`来填充它们，然后回退到普通单跳检索。

### 第 5 步：合成答案

从 wiki 内容中组合你的答案：
- 使用`[[page-name]]`符号引用特定的 wiki 页面
- 注明答案来自哪个步骤（“在摘要中找到” vs “grep 部分” vs “全文阅读”）——这有助于用户理解置信度
- 如果 wiki 存在矛盾，展示双方
- 如果 wiki 没有涵盖某些内容，明确说明
- 建议哪些来源可能填补空白

**页面信任注释：** 对于答案中引用的每个页面，检查其`lifecycle`页眉并计算`is_stale = (今天 − 更新) > 90 天`。在行内注释有风险的页面，以便用户知道哪些引用需要验证：

| 条件 | 注释 |
|---|---|
| `lifecycle: 归档` | `(ARCHIVED: 被 [[目标]] 覆盖)` — 使用后继者 |
| `lifecycle: 争议` | `(争议, 标记 <lifecycle_changed>: <lifecycle_reason 或 "原因未指明">)` |
| `is_stale` + `lifecycle: 已验证` | `(已验证但过时: 最后更新 <更新>)` — 读者应在依赖前重新验证 |
| `is_stale`（其他生命周期） | `(过时: 最后更新 <更新>)` |

示例在合成答案中：
```
[[concept-page]] (过时: 最后更新 2026-01-15) — 原始声明是 X。
[[verified-page]] (已验证但过时: 最后更新 2025-09-10) — 读者应在依赖前重新验证。
[[disputed-page]] (争议, 标记 2026-04-30: 被 [[新来源]] 矛盾) — 早期说 Y，现在不确定。
[[old-page]] (归档: 被 [[新页面]] 覆盖) — 使用后继者。
```

没有生命周期字段的页面（预构型模式之前的遗留页面）与`draft`相同——如果过时则注释，否则跳过。永远不要编造`lifecycle_reason`；如果该字段缺失，则从注释中省略原因。

**显示项目源位置（项目范围查询）。** 当引用的页面是项目范围的——它们的路径在`projects/<name>/...`下，或者它们的页眉带有`source_path`/`source_repo`字段——解析实际代码的位置，以便建议的修复可以命名真实文件，并且后续步骤可以编辑它们：

1. 读取`$OBSIDIAN_VAULT_PATH/.manifest.json`并查找`.projects.<name>.source_repo`——这是**权威的、机器无关的**身份（例如`github.com/owner/name`）。这是你要报告的。
2. 通过以下顺序尝试解析本地检出根并停止在第一个存在的：`.projects.<name>.source_cwd_hint`（一个`~`相对提示），然后是遗留的`.projects.<name>.source_cwd`（一个绝对路径，仅限旧构型），然后是页面的`source_path`页眉。在任何候选中展开`~`并确认目录确实存在后再使用它。仅使用遗留绝对路径作为本地便利——永远不要将其报告为项目的身份。

报告**`源代码:`** 行使用`source_repo`。当第 2 步中解析了本地检出时，附加具体路径以便读者可以采取行动（例如`<repo> — 本地检出在 ~/code/name/public/lib/anticheat.js`）。当查询暗示需要代码修复并且存在本地检出时，命名要编辑的特定文件，并**提议将其作为明确的、单独的下一步来实现**——但永远不要在查询期间编辑（见上文的 READ-ONLY 保护）。如果未解析出本地检出，报告仓库并说明代码未在此机器上检出。

### 第 6 步：记录查询

这是此技能执行的*唯一*写操作——不要编辑任何其他内容，并且不要手动追加到`log.md`：

```bash
obsidian-wiki memory log QUERY \
  query="用户的提问" result_pages=<N> \
  mode=<normal|index_only|filtered> escalated=<true|false> \
  candidates_seen=<N> candidates_used=<N> dropped=<N>
```

该命令获取内存锁并追加一行可解析的文本；它永远不会触及`index.md`或`hot.md`。

使用自第 2 步以来跟踪的计数。如果未跟踪某个计数（例如，索引仅模式从未构建完整的候选集），则写`0`而不是省略该字段——日志格式应保持可解析。

## 答案格式

像这样结构化答案：

> **基于 wiki：**
>
> [你的合成答案，带有`[[wikilinks]]`到源页面的链接]
>
> **参考页面：** [[page-a]], [[page-b]], [[page-c]]
>
> **空白：** [wiki 没有涵盖可能相关的哪些内容]
>
> **检索：** N 个候选页面看到，M 个读取，D 个丢弃（未处理的匹配项，如果有：[[page-d]], [[page-e]])
>
> **源代码：** `<source_repo>`（本地检出在`~/code/<name>`) — 要实现，相关文件是`…`。
> (说这个词，我会切换出查询模式来做出更改。)

**源代码**行是可选的——仅当为项目范围查询并解析了`source_repo`时才包含它（见第 5 步）。报告仓库，而不是机器绝对路径；仅在它实际上存在于此机器上时才添加本地检出路径。

**检索**行始终包含——这是自第 2 步以来跟踪的透明报告（镜像`candidates_seen`/`candidates_used`/`dropped`字段在第 6 步中记录的值）。在索引仅模式下，报告前缀扫描的计数；如果 D 为 0，则省略括号中的内容，而不是编写空列表。
