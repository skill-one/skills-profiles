# Wiki查询 — 知识检索

你正在针对编译好的Obsidian维基回答问题，而不是原始的源文档。维基包含预合成、相互参照的知识。

## 此技能仅读不写

`wiki-query`用于回答问题。它**绝对不能**创建或修改任何维基内容。它唯一可以执行的是步骤6中对`log.md`的追加。

任何时候，即使改变看起来明显有帮助时：

- 也**不要**在`concepts/`、`entities/`、`skills/`、`references/`、`synthesis/`、`journal/`或`projects/`下创建或编辑页面
- 修改`index.md`、`hot.md`、`_insights.md`或`.manifest.json`

如果用户的消息包含新发现、行动请求（“保存这个”、“禁止X”、“记录下来”）或任何暗示要更改的内容，**请勿执行**。回答问题，**提出**更改，并将用户引导到正确的技能：
- 快速笔记/小技巧 → `wiki-capture --quick`
- 完整的新页面 → `wiki-capture`
- 项目知识同步 → `wiki-update`

## 开始前

1. **解决配置** — 遵循`llm-wiki/SKILL.md`中的配置解析协议（内联`@name`覆盖 → 沿当前工作目录向上查找`.env` → 全局配置 → 提示设置）。对于跨项目查询而没有`@name`的情况，即使它是指向保险库`.env`的符号链接，当存在时也优先使用全局配置。这提供了`OBSIDIAN_VAULT_PATH`和任何QMD变量。从任何项目目录都可以工作。
2. **在决定检索策略之前，从解析的配置中加载QMD设置**。如果`QMD_WIKI_COLLECTION`被设置，将QMD视为仅受以下传输/工具检查约束的可用主题。如果它为空或未设置，在使用grep/页面读取之前，简要说明为什么跳过QMD。
3. 如果`$OBSIDIAN_VAULT_PATH/hot.md`存在，首先读取它——它为您提供有关最近活动的即时上下文。如果用户的问题是关于最近摄入的内容，hot.md可能在您甚至打开`index.md`之前就能回答它。
4. 读取`$OBSIDIAN_VAULT_PATH/index.md`以了解维基的范围和结构

## 可见性过滤器（可选）

默认情况下，**所有页面都将返回，而不管可见性标签如何**。这保留了现有行为——除非用户要求，否则不会发生变化。

如果用户的查询包含如**"仅公开"**、**"面向用户"**、**"不包含内部内容"**、**"作为用户会看到的样子"**或**"排除内部"**等短语，请激活**过滤模式**：

- 构建**阻止标签集**：`{visibility/internal, visibility/pii}`
- 在索引传递（步骤2）中，跳过任何候选者的frontmatter标签包含阻止标签
- 在节/完整读取传递（步骤3-4）中，不要读取或引用任何阻止的页面
- 仅从允许的页面合成答案——不要提及被排除的页面

没有`visibility/`标签的页面，或标记为`visibility/public`的页面始终包含。

在过滤模式下，在步骤6的日志条目中注明过滤器：`mode=filtered`。

## 检索协议

**遵循`llm-wiki/SKILL.md`中的检索原语表**。读取是这个技能的主要成本——使用能回答问题的最便宜的原语，只有在它不能时才升级。永远不要直接跳到完整页面读取。

### 步骤0：GraphRAG预传递（快速索引查询——不读取页面）

在打开任何页面之前，查询编译的图形索引：

```bash
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --pretty
```

输出字段：

- **`answer_type`**：`direct` | `path` | `list` | `gap` | `impact` | `bridges` | `hubs` | `clusters` | `surprising` — 决定下一步该做什么。最后五个是**结构意图**：问题是关于保险库的形状，答案完全在`graph`中计算出来（见下文），并且没有任何页面读取。
- **`graph`**：仅对于结构意图存在——计算出的答案。否则为`null`。
- **`candidates`**：按标题/标签/摘要匹配+度数排名的前排页面，包括分数和摘要
- **`should_read`**：最值得打开的页面——从这里开始，而不是推测性地读取许多文件
- **`path`**：对于多跳查询，两个概念之间的最短维基链接路径
- **`god_nodes_relevant`**：与您的查询术语相关的中心页面——总是有用的上下文
- **`index_only`**：如果`true`，顶级候选者的摘要已经回答了问题——跳过页面读取
- **`temporal`**：`as_of`，`retrievable`，`excluded_historical`——事件时间过滤器阻止了多少页面（见下文）

**结构意图**——这些完全由图形回答。用户的措辞会自动路由：

| 用户询问 | `answer_type` | `graph`包含 |
|---|---|---|
| "如果删除X会破坏什么" / "什么依赖于X" / "什么链接到X" | `impact` | `direct_dependents`，`transitive_dependents`，`total` |
| "哪些页面连接我的集群" / "什么会使我的保险库碎片化" | `bridges` | 按介数排序的页面，带有`label`和`connects_labels` |
| "什么居中" / "顶级中心" / "我的主要主题" | `hubs` | 按度数排序的页面，带有输入/输出拆分 |
| "我有哪些集群" / "我的维基如何组织" | `clusters` | 每个集群的`label`，`size`，`cohesion`，`fragmented` |
| "惊人的连接" / "意外的链接" | `surprising` | 跨集群链接，按稀有度排序 |

直接报告`graph`负载——**不要**通过读取页面重新推导它。如果结构性问题命名了一个无法解析的页面，CLI会回退到`direct`和`graph`为`null`。

**决策树：**

1. 如果`graph`非空→结构答案已完成。报告它并停止；不读取页面。
2. 如果`index_only: true`→直接从`candidates[0].summary`回答。跳过步骤1-4，转到步骤5。
3. 如果`answer_type == "path"`且`path`非空→连接在`path`中。只读取那些页面。
4. 其他情况下→只打开`should_read`页面（不是所有候选者）。这取代了旧流程中所需的推测性5-10页面读取。

> 此处使用的图形排除了保险库账本文件（`index.md`，`log.md`，`hot.md`，`_insights.md`）。它们链接到几乎每个页面，因此将它们包含在内会使任何两个页面看起来大约是2跳远，并产生无意义的`A → index → B`路径。

**事件时间**。页面可能携带`valid_from` / `valid_until` / `superseded_by` frontmatter。一个`valid_until`已过期的页面是**历史性的**：它仍然在保险库和图形中，但默认情况下会从候选者中排除，因此“我们使用什么X”的答案是与当前情况相符的，而不是首先写下的内容。

- 当`temporal.excluded_historical`非零时，如果这对答案是重要的，请说明——用户可能是在询问被取代的状态。
- 如果问题是关于过去的（“2025年我们使用什么”，“迁移之前”），使用`--as_of YYYY-MM-DD`重新运行以检索当时的内容。
- 使用`--include-historical`当用户明确要求整个历史记录，或者当您正在跟踪决策如何变化时。
- 带有`superseded_by`的候选者会命名它的替代品——跟随它，而不是报告过时的声明为当前。

```bash
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --as-of 2025-06-01 --pretty
obsidian-wiki graph-query "$OBSIDIAN_VAULT_PATH" "<question>" --include-historical --pretty
```

结构意图故意忽略了此过滤器：删除页面仍然会破坏链接到它的历史页面，因此爆炸半径不会仅仅因为依赖项不再当前而缩小。

**回退**（如果`obsidian-wiki`未安装）：像正常一样使用grep和`index.md`进行步骤1。

### 步骤1：理解问题

分类查询类型：
- **事实查询**——"X是什么？" → 找到相关页面
- **关系查询**——"X如何与Y相关？" / "什么与X矛盾？" → 找到两个页面，它们的交叉引用，以及它们的`relationships:` frontmatter块用于类型边缘
- **路径/多跳查询**——"X如何连接到Y？" / "什么将X链接到Y？" / "从X到Z跟踪链条" / "X依赖什么？" → X和Y没有直接链接；连接通过中间页面运行。使用步骤4b中的多跳图遍历。
- **合成查询**——"关于X的当前想法是什么？" → 找到所有接触X的页面，合成
- **差距查询**——"我不知道X的哪些信息？" → 找到缺失的内容，检查开放问题部分

还要决定**模式**：
- **仅索引模式**——由"快速答案"、"仅扫描"、"不要读取页面"、"快速查找"触发。在步骤3停止。仅从frontmatter + `index.md`回答。
- **正常模式**——以下面的分层管道。

### 步骤2：索引传递（低成本）

在不打开任何页面正文的情况下构建候选集：

- 你已经读取了上面的`index.md`——将其用作第一个过滤器。它列出了每个页面的一行描述和标签。
- 使用`Grep`扫描页面**仅frontmatter**以查找标题、标签、别名和摘要匹配。一个像`^(title|tags|aliases|summary):`的范围到保险库`.md`文件的模式比内容grep便宜得多。
- 收集按以下顺序排名的前5-10个候选页面路径：
  1. 标题或别名完全匹配
  2. 标签匹配
  3. 摘要字段包含查询术语
  4. `index.md`条目包含查询术语
- **在每个排名桶内应用层级排序**：当两个候选者得分相同，优先`tier: core`而不是`tier: supporting`而不是`tier: peripheral`。使用与检索其他字段相同的cheap grep读取`tier:` frontmatter字段。没有`tier:`字段的页面被视为`supporting`。

**跟踪检索计数（为步骤5/6中的透明报告）：**
- `candidates_seen`——匹配任何排名标准*之前*的*总*不同页面，在修剪到前5-10之前。
- `candidates_used`——你实际上在步骤3/4中携带了多少个。
- `dropped`——`candidates_seen − candidates_used`，即存在但从未读取的匹配。如果这个非零，命名被丢弃的页面（如果有很多，则命名计数），以便用户知道检索不是详尽的——这不是错误，只是对被排除内容的诚实会计。

如果你处于**仅索引模式**，在这里停止。从`summary:`字段、标题和`index.md`描述中回答。明确标记答案：**"(仅索引答案——未读取页面正文；以下事实来自页面摘要，可能遗漏细节)"**。然后跳到步骤5。

### 步骤2b：QMD语义传递（可选——需要`QMD_WIKI_COLLECTION`在解析的配置中）

**警戒**：如果`$QMD_WIKI_COLLECTION`在配置解析后为空或未设置，跳过此整个步骤并继续到步骤3。在您的工作更新中提及缺失的变量。

> **没有QMD？** 跳到步骤3并直接在保险库上使用`Grep`。QMD更快、概念感知，但grep路径完全可用。见`.env.example`进行设置。

如果`QMD_WIKI_COLLECTION`被设置，在到达`Grep`之前运行QMD，除非问题已经完全由`hot.md`或`index.md`元数据回答。当问题语义、特定于项目、询问相关上下文或使用可能不会在标题/frontmatter中出现的术语时，特别推荐QMD。

选择QMD传输来自`$QMD_TRANSPORT`：

- `mcp`（默认）：使用在代理中配置的QMD MCP工具。
- `cli`：运行本地qmd CLI。如果设置了`$QMD_CLI`，请使用它；否则使用`qmd`。

有关详细CLI命令选择、维护和VM注意事项，当安装时使用本地`$qmd-cli`技能。

如果选定的传输不可用（没有MCP工具，`qmd`不在PATH上，或命令出错），跳过QMD并继续步骤3。

对于MCP传输：

```
mcp__qmd__query:
  collection: <QMD_WIKI_COLLECTION>   # 例如 "knowledge-base-wiki"
  intent: <用户的查询>
  searches:
    - type: lex    # 关键字匹配——适用于确切名称、文件路径、错误消息
      query: <关键词>
    - type: vec    # 语义匹配——适用于概念、模式、"X是什么样"
      query: <将问题改写为描述>
```

对于CLI传输，从`$QMD_CLI_SEARCH_MODE`选择命令：

保持类似运算符或标点符号重的标记，如`no-sudo`、`ansible_become=false`和`~/.local/bin`在`lex:`行中。将`vec:`行改写为纯自然语言，不带连字符`-term`单词；QMD将`-term`视为否定，否定在`vec`/`hyde`查询中不受支持。

- `quality`（默认）：最佳相关性；CPU上较慢。
  ```bash
  ${QMD_CLI:-qmd} query $'lex: <key terms>\nvec: <question rephrased as a description>' -c "$QMD_WIKI_COLLECTION" -n 8 --files
  ```
- `balanced`：无LLM重新排序的混合搜索；当`quality`太慢时使用。
  ```bash
  ${QMD_CLI:-qmd} query $'lex: <key terms>\nvec: <question rephrased as a description>' -c "$QMD_WIKI_COLLECTION" -n 8 --no-rerank --files
  ```
- `fast`：仅语义召回，或当确切名称、文件路径或错误消息很重要时使用`search`而不是。
  ```bash
  ${QMD_CLI:-qmd} vsearch "<question rephrased as a description>" -c "$QMD_WIKI_COLLECTION" -n 8 --files
  ```

使用`${QMD_CLI:-qmd} get "#docid"`通过CLI输出提供docid检索排名文档。返回的片段或排名文件充当预读部分摘要。如果它们完全回答了问题，跳过步骤3并直接转到步骤4（只读取QMD排名最高的页面）。如果未完全回答，请使用排名文件列表来指导步骤3中要grep或读取的文件。

将QMD命中折叠到来自步骤2的相同`candidates_seen`计数（按路径去重——一个页面由frontmatter grep和QMD各计数一次）。

**防御性过滤器：从维基集合结果中丢弃任何`_raw/`路径**。维基集合应该只索引编译好的页面，但配置错误的集合（见`.env.example`）可能会索引`_raw/`——包括位于`_raw/_archived/`中的过时草稿，它们已经被推广的页面取代了。在使用来自`$QMD_WIKI_COLLECTION`的QMD命中之前，检查其路径：如果它包含`_raw/`，请从维基集合结果集中丢弃它（它可能仍然通过`$QMD_PAPERS_COLLECTION`以原始来源身份出现）。这使配置错误的集合退化到“缺失召回”而不是“默默引用过时的草稿作为编译知识”。如果您看到来自维基集合的`_raw/`路径，请在您的工作更新中提及用户知道他们的集合范围需要修复（见`.env.example` QMD部分）。

**在问题可能包含源材料在`_raw/`时也搜索`papers`：**

如果`QMD_PAPERS_COLLECTION`被设置，并且用户询问的主题可能由摄入的论文（研究、理论、背景）涵盖，请运行针对论文集合的并行搜索。在您的答案中将原始来源与编译的维基页面分开引用。

### 步骤3：部分传递（中等成本——仅在步骤2/2b无结论时）

对于每个顶级候选者，拉取相关部分*而不读取整个页面*：

- 使用`Grep -A 10 -B 2 "<query-term>" <candidate-file>`只获取匹配周围的行。
- 这通常返回每个命中15-30行，而不是100-500行。
- 如果部分grep给出明确的答案，直接转到步骤5。

### 步骤4：完整读取（高成本——最后手段）

只有在步骤2和3无法回答问题时：

- 读取顶部**3**个候选者。当选择要读取的3个时，应用层级排序：先读取`core`页面，然后是`supporting`，并跳过`peripheral`页面，除非它们是唯一匹配。
- 如果答案需要交叉引用，请从这些页面遵循最多一个`[[wikilinks]]`跳。
- **对于关系查询**（"X如何与Y相关？" / "什么与X矛盾？"）：还读取候选页面的`relationships:` frontmatter块。每个条目提供一个类型化的、方向性的边缘（`extends`，`implements`，`contradicts`，`derived_from`，`uses`，`replaces`，`related_to`）。在您的答案中明确显示这些——"页面A *与* 页面B矛盾（类型边缘）"比"页面A链接到页面B"更有用。
- 检查“开放问题”部分以检查已知差距。
- 如果您仍然短缺，**然后**回退到跨保险库的广泛内容grep。告诉用户您升级了——这是昂贵的路径，他们应该知道。

### 步骤4b：多跳图遍历（类型边缘）

普通检索显示提及查询术语的页面。它不能回答**路径/多跳查询**——"X如何连接到Y？"，"X依赖什么？"，"从X到Z跟踪链条"——当X和Y从未出现在同一页面上时。答案存在于类型边缘图的*形状*中，而不是任何单个页面正文。这是执行这一步。

仅当路径/多跳查询（或当关系查询返回的两个页面之间没有直接边缘时）运行此步骤。它完全由frontmatter构建——永远不读取页面正文。

1. **构建类型边缘邻接（低成本）。** 一次grep每个页面的`relationships:`块——`Grep -A 20 "^relationships:" <vault>/**/*.md`（仅frontmatter）。每个条目产生一个有向、类型化的边缘`source —type→ target`。添加反向方向作为可遍历的边缘（标记为`(reverse)`），因为“连接到”是对称的，即使类型断言是方向性的。普通正文`[[wikilinks]]`仅作为未类型的`related_to`边缘，如果您需要它们来完成路径——优先使用类型边缘。

2. **定位端点。** 使用来自步骤2的注册表将X（以及查询命名两个的Y）解析为页面路径。如果端点有歧义，选择`tier: core`候选者并注意假设。

3. **有界BFS。** 如果`obsidian-wiki`已安装，让CLI首先在维基链接图上执行遍历——它是精确的且即时的：

   ```bash
   obsidian-wiki graph-analyse "$OBSIDIAN_VAULT_PATH" --path "<X>" "<Y>"                  # 两端点：最短链+跳数
   obsidian-wiki graph-analyse "$OBSIDIAN_VAULT_PATH" --around "<X>" --depth 3 [--direction out|in]  # 单端点：可到达页面按跳数
   ```

   `--path`在`--direction out`的情况下在任一方向跟随链接；`--around --direction in`回答"X依赖什么"（它的爆炸半径）。然后用步骤1中的类型边缘装饰返回的链。否则，或为了找到备用路径，手动执行：
   - **最大深度3跳**默认（连接很少有意义超过那）。仅在用户说“深” / “无论需要多少跳”时提高。
   - **前沿上限**：一旦访问集超过~60页，停止扩展节点——报告部分结果，而不是在整个保险库中发散。
   - 对于**两端点查询**（X→Y）：一旦找到最短路径就停止；然后简要继续以显示最多2个备用路径（如果存在）。
   - 对于**单端点查询**（X传递）：收集在深度限制内可到达的所有节点，按跳数分组。

4. **报告带有边缘类型的路径**。显示链条，而不仅仅是端点——类型边缘*就是*答案：

   ```
   [[concepts/transformers]] —uses→ [[concepts/attention]] —derived_from→ [[concepts/rnn-seq2seq]] —contradicts (reverse)→ [[concepts/lstm]]
   ```

   说明跳数以及是否有任何跳是`(reverse)`遍历或未类型的`related_to`回退（那些链条较弱——标记它们）。如果深度限制内没有路径，请明确说明： "在3跳内没有类型边缘路径从X到Y——它们位于图的分离区域。" 这本身就是一个有用的发现（一个图差距）。

**成本警戒**：此步骤仅通过grep读取frontmatter。如果邻接grep返回为空（没有页面使用`relationships:`），报告图形没有类型边缘可以遍历，并建议运行`cross-linker`来填充它们，然后回退到普通单跳检索。

### 步骤5：合成答案

从维基内容组合您的答案：
- 使用`[[page-name]]`符号引用特定的维基页面
- 注意答案来自哪个步骤（“在摘要中找到”与“grep部分”与“完整页面读取”）——这有助于用户了解信心
- 如果维基存在矛盾，请呈现双方
- 如果维基没有涵盖某些内容，请明确说明
- 建议哪些来源可能填补差距

**页面信任注释**：对于您答案中引用的每个页面，检查其`lifecycle` frontmatter并计算`is_stale = (today − updated) > 90 days`。内联注释有风险的页面，以便用户知道哪些引用需要验证：

| 条件 | 注释 |
|---|---|
| `lifecycle: archived` | `(ARCHIVED: 被 [[target]] 取代)` — 使用后继者 |
| `lifecycle: disputed` | `(DISPUTED, 标记 <lifecycle_changed>: <lifecycle_reason or "reason unspecified">)` |
| `is_stale` + `lifecycle: verified` | `(VERIFIED but stale: last updated <updated>)` — 读者应在依赖之前重新验证 |
| `is_stale`（其他生命周期） | `(过时: 最后更新 <updated>)` |

示例在一个合成的答案中：
```
[[concept-page]] (过时: 最后更新 2026-01-15) — 原始声明是X。
[[verified-page]] (VERIFIED but stale: last updated 2025-09-10) — 读者应在依赖之前重新验证。
[[disputed-page]] (DISPUTED, 标记 2026-04-30: 与 [[new-source]] 矛盾) — 以前说Y，现在不确定。
[[old-page]] (ARCHIVED: 被 [[new-page]] 取代) — 使用后继者。
```

没有生命周期字段的页面（预构模式早于模式方案的页面）与`draft`相同——如果过时则注释，否则跳过。永远不要编造`lifecycle_reason`；如果该字段缺失，请从注释中省略原因。

**显示项目源位置（项目范围查询）。** 当引用的页面是项目范围的——它们的路径在`projects/<name>/...`下，或者它们的frontmatter携带`source_path`/`source_repo`字段——解析实际代码的位置，以便可以命名真实文件，并且可以在后续回合中编辑它们：

1. 读取`$OBSIDIAN_VAULT_PATH/.manifest.json`并查找`.projects.<name>.source_repo`——这是**权威的、与机器无关**的身份（例如 `github.com/owner/name`）。这是您报告的。
2. 尝试按顺序解析本地签出根目录：`.projects.<name>.source_cwd_hint`（一个`~`-相对提示），然后是遗留的`.projects.<name>.source_cwd`（仅限绝对路径，仅限旧manifests），然后是页面的`source_path` frontmatter。展开`~`在任何候选者中，并在使用之前确认目录确实存在。仅使用遗留绝对路径仅作为本地便利——永远不要将其报告为项目的身份。

使用`source_repo`报告**`Source code:`**行。当步骤2中解析了本地签出时，附加具体的路径，以便读者可以采取行动（例如 `<repo> — 本地签出在 ~/code/name/public/lib/anticheat.js`）。当查询暗示需要代码修复时，并且本地签出存在，请命名要编辑的特定文件，并**提议将其作为明确的、单独的下一步执行**——但永远不要在查询本身编辑（见上面的READ-ONLY警戒）。如果无法解析本地签出，请报告仓库并说明代码在此机器上未签出。

### 步骤6：记录查询

这是此技能执行的*唯一*写入——不要编辑任何其他内容，并且不要手动追加到`log.md`：

```bash
obsidian-wiki memory log QUERY \
  query="用户的查询" result_pages=<N> \
  mode=<normal|index_only|filtered> escalated=<true|false> \
  candidates_seen=<N> candidates_used=<N> dropped=<N>
```

该命令获取内存锁并追加一行可解析的文本；它永远不会触及`index.md`或`hot.md`。
