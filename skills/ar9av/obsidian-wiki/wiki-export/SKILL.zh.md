---
name: wiki-export
description: 将 Obsidian 知识库的知识图谱导出为结构化格式，以便在外部工具中使用。当用户说“导出知识库”、“导出图谱”、“导出到 JSON”、“导出到 Gephi”、“导出到 Neo4j”、“导出到 Postgres”、“导出到 SQL”、“graphml”、“可视化知识库”、“知识图谱导出”、“导出到 OKF”、“OKF 套件”、“开放知识格式”、“导出为 Markdown 套件”，或希望将他们的知识库数据用于其他工具时，使用此功能。输出 graph.json、graph.graphml、cypher.txt（Neo4j）、postgres.sql（Postgres）和 graph.html（交互式浏览器可视化）到仓库根目录下的 wiki-export/ 目录，并可选择在 wiki-export/okf/ 目录下生成 OKF（开放知识格式）Markdown 套件。
---

# Wiki 导出 — 知识图谱导出

您正在将 wiki 的 wikilink 图导出到结构化格式，以便在外部工具（Gephi、Neo4j、自定义脚本、浏览器可视化）中使用。

## 开始前

1. **解析配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会给出 `OBSIDIAN_VAULT_PATH`
2. 确认保险库中有页面可以导出 — 如果少于 5 个页面存在，则警告用户并停止

## 项目过滤器（可选）

如果用户的调用包含项目名称 — 例如 `/wiki-export prismor`、`"export the prismor project"`、`"export project:security"` — 激活 **项目过滤器模式**：

1. **从参数或短语中提取项目名称**。规范化：小写、去除单词 "project"。
2. 仅保留满足 **任一** 条件的项目页面：
   - 页面 `id` 以 `projects/<name>/` 开头（基于路径匹配）
   - 页面的 `tags` 数组包含 `<name>`（基于标签匹配）
3. 删除任何端点被排除的边。
4. 在摘要中注明过滤器：`(filtered: project:<name> — X of Y pages)`
5. 在 JSON 输出中设置 `graph.graph.filter = "project:<name>"`。

如果同时激活了项目过滤器和可见性过滤器，则应用两者（先应用项目过滤器，然后在剩余集合上应用可见性过滤器）。

## 可见性过滤器（可选）

默认情况下，**所有页面都将被导出，无论可见性标签如何**。这保留了现有行为。

如果用户请求过滤导出 — 例如 **"public export"`、**`"user-facing export"`、**`"exclude internal"`、**`"no internal pages"` — 激活 **可见性过滤模式**：

- 构建 **阻塞标签集**：`{visibility/internal, visibility/pii}`
- 在构建节点列表时，跳过任何其 frontmatter 标签包含阻塞标签的页面
- 跳过任何端点被排除的边
- 在摘要中注明过滤器：`(filtered: visibility/internal, visibility/pii excluded)`

没有 `visibility/` 标签的页面，或标记为 `visibility/public` 的页面，始终被包含。

## 第 1 步：构建节点和边列表

在保险库中 GLOB 所有 `.md` 文件（排除 `_archives/`、`_raw/`、`_readouts/`、`.obsidian/`、`index.md`、`log.md`、`_insights.md`）。收集完整文件列表后应用任何激活的过滤器（项目和/或可见性）。

对于每个页面，从 frontmatter 中提取：
- `id` — 从保险库根目录的相对路径，不带 `.md` 扩展名（例如 `concepts/transformers`）
- `label` — frontmatter 中的 `title` 字段，如果缺失则为文件名
- `category` — 目录前缀（`concepts`、`entities`、`skills`、`references`、`synthesis`、`projects` 或 `journal`）
- `tags` — frontmatter 标签字段中的数组
- `summary` — 如果存在，则 frontmatter 中的 `summary` 字段

这是您的 **节点列表**。

对于每个页面，在正文中 Grep `\[\[.*?\]\]` 以提取所有 wikilink：
- 解析每个 `[[target]]` 或 `[[target|display]]` — 仅使用目标部分
- 将目标解析为节点 ID（规范化：小写、空格→连字符、去除 `.md`）
- 跳过指向节点列表外部的链接（断开的链接）
- 每个解析的链接成为边：`{source: page_id, target: linked_id, relation: "wikilink", confidence: "EXTRACTED"}`
- 如果链接的句子以 `^[inferred]` 或 `^[ambiguous]` 结尾，则相应地覆盖 `confidence`

**类型边增强**：在构建 wikilink 边列表后，读取每个页面的 `relationships:` frontmatter 块。对于每个 `{target, type}` 条目：
- `target` YAML 值是一个引号内的 wikilink 字符串，例如 `"[[concepts/lstm]]"`。去除周围的 `[[` 和 `]]` 字符，然后应用相同的规范化（小写、空格→连字符、去除 `.md`）以获取节点 ID。
- 跳过解析目标不在节点列表中的条目（断开的链接）
- 如果该 `(source, target)` 对的边已存在，则用类型值覆盖其 `relation` 字段（例如 `"contradicts"`）并设置 `typed: true`
- 如果该对尚未存在边，则添加一条边：`{source: page_id, target: target_id, relation: <type>, confidence: "EXTRACTED", typed: true}`

这意味着 `relation: "wikilink"` 是普通未类型链接的默认值；`relationships:` 条目将其提升为命名语义类型。同时来自正文 wikilink 和 `relationships:` 条目的边保留单个记录 — 类型版本优先。

这是您的 **边列表**。

## 第 2 步：分配社区 ID

通过标签聚类将页面分组到社区：
- 共享相同主导标签的页面属于同一社区
- 主导标签 = 页面 frontmatter 标签字数组中的第一个标签
- 没有标签的页面社区 ID 为 `null`
- 从 0 开始编号社区，按大小降序排列（最大社区为 0）

这使 HTML 可视化工具（如 Gephi）能够按社区着色。

## 第 3 步：写入输出文件

在保险库根目录创建 `wiki-export/`（如果不存在）。写入所有五个文件：

---

### 3a. `graph.json`

NetworkX node_link 格式 — 标准用于图工具和脚本：

```json
{
  "directed": false,
  "multigraph": false,
  "graph": {
    "exported_at": "<ISO timestamp>",
    "vault": "<OBSIDIAN_VAULT_PATH>",
    "total_nodes": N,
    "total_edges": M
  },
  "nodes": [
    {
      "id": "concepts/transformers",
      "label": "Transformer Architecture",
      "category": "concepts",
      "tags": ["ml", "architecture"],
      "summary": "The attention-based architecture introduced in Attention Is All You Need.",
      "community": 0
    }
  ],
  "links": [
    {
      "source": "concepts/transformers",
      "target": "entities/vaswani",
      "relation": "wikilink",
      "confidence": "EXTRACTED"
    },
    {
      "source": "concepts/transformers",
      "target": "concepts/lstm",
      "relation": "contradicts",
      "confidence": "EXTRACTED",
      "typed": true
    }
  ]
}
```

---

### 3b. `graph.graphml`

GraphML XML 格式 — 可在 Gephi、yEd 和 Cytoscape 中加载：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/graphml">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="category" for="node" attr.name="category" attr.type="string"/>
  <key id="tags" for="node" attr.name="tags" attr.type="string"/>
  <key id="community" for="node" attr.name="community" attr.type="int"/>
  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>
  <key id="type" for="edge" attr.name="type" attr.type="string"/>
  <key id="confidence" for="edge" attr.name="confidence" attr.type="string"/>
  <graph id="wiki" edgedefault="undirected">
    <node id="concepts/transformers">
      <data key="label">Transformer Architecture</data>
      <data key="category">concepts</data>
      <data key="tags">ml, architecture</data>
      <data key="community">0</data>
    </node>
    <!-- 未类型 wikilink — 没有 <data key="type"> 元素 -->
    <edge source="concepts/transformers" target="entities/vaswani">
      <data key="relation">wikilink</data>
      <data key="confidence">EXTRACTED</data>
    </edge>
    <!-- 来自 relationships: 块的类型边 -->
    <edge source="concepts/transformers" target="concepts/lstm">
      <data key="relation">contradicts</data>
      <data key="type">contradicts</data>
      <data key="confidence">EXTRACTED</data>
    </edge>
  </graph>
</graphml>
```

为每个页面写入一个 `<node>`，为每个链接写入一个 `<edge>`。对于类型边（边列表中 `typed: true`），发出 `<data key="relation">`（包含语义类型值）**和** `<data key="type">`（包含相同值）— 这使 `relation` 可供已消费它的工具读取，同时让类型感知工具通过专用的 `type` 键进行过滤。未类型的 wikilink 完全省略 `<data key="type">` 元素。

---

### 3c. `cypher.txt`

Neo4j Cypher `MERGE` 语句 — 复制到 Neo4j 浏览器或使用 `cypher-shell` 运行：

```cypher
// Wiki knowledge graph export — <TIMESTAMP>
// Load with: cypher-shell -u neo4j -p password < cypher.txt

// Nodes
MERGE (n:Page {id: "concepts/transformers"}) SET n.label = "Transformer Architecture", n.category = "concepts", n.tags = ["ml","architecture"], n.community = 0;
MERGE (n:Page {id: "entities/vaswani"}) SET n.label = "Ashish Vaswani", n.category = "entities", n.tags = ["person","ml"], n.community = 0;
MERGE (n:Page {id: "concepts/lstm"}) SET n.label = "LSTM", n.category = "concepts", n.tags = ["ml","rnn"], n.community = 0;

// Relationships
// 未类型 wikilinks 使用 [:WIKILINK]
MATCH (a:Page {id: "concepts/transformers"}), (b:Page {id: "entities/vaswani"}) MERGE (a)-[:WIKILINK {relation: "wikilink", confidence: "EXTRACTED"}]->(b);
// 类型边使用关系类型作为标签（UPPERCASE）
MATCH (a:Page {id: "concepts/transformers"}), (b:Page {id: "concepts/lstm"}) MERGE (a)-[:CONTRADICTS {relation: "contradicts", confidence: "EXTRACTED"}]->(b);
```

为每个页面写入一个 `MERGE` 节点语句，然后为每个边写入一个 `MATCH`/`MERGE` 关系语句。对于类型边，使用 `type` 值大写作为 Cypher 关系标签（例如 `contradicts` → `[:CONTRADICTS]`，`derived_from` → `[:DERIVED_FROM]`）。未类型 wikilinks 始终使用 `[:WIKILINK]`。

---

### 3d. `postgres.sql`

纯 SQL — 可加载到任何 Postgres 数据库（本地、Supabase、RDS、Neon 等）使用 `psql -f postgres.sql` 或迁移运行器。两个表：`wiki_pages`（节点）和 `wiki_edges`（链接），使用 `ON CONFLICT` 插入以使重新运行导出安全且幂等，类似于 `cypher.txt` 的 `MERGE` 语义。

```sql
-- Wiki knowledge graph export — <TIMESTAMP>
-- Load with: psql -d yourdb -f postgres.sql

CREATE TABLE IF NOT EXISTS wiki_pages (
  id        TEXT PRIMARY KEY,
  label     TEXT NOT NULL,
  category  TEXT,
  tags      JSONB NOT NULL DEFAULT '[]'::jsonb,
  summary   TEXT,
  community INT
);

CREATE TABLE IF NOT EXISTS wiki_edges (
  source     TEXT NOT NULL REFERENCES wiki_pages(id) ON DELETE CASCADE,
  target     TEXT NOT NULL REFERENCES wiki_pages(id) ON DELETE CASCADE,
  relation   TEXT NOT NULL DEFAULT 'wikilink',
  confidence TEXT,
  typed      BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (source, target, relation)
);

CREATE INDEX IF NOT EXISTS wiki_edges_source_idx ON wiki_edges(source);
CREATE INDEX IF NOT EXISTS wiki_edges_target_idx ON wiki_edges(target);

-- Nodes
INSERT INTO wiki_pages (id, label, category, tags, summary, community)
VALUES ('concepts/transformers', 'Transformer Architecture', 'concepts', '["ml","architecture"]'::jsonb, 'The attention-based architecture introduced in Attention Is All You Need.', 0)
ON CONFLICT (id) DO UPDATE SET
  label = EXCLUDED.label, category = EXCLUDED.category, tags = EXCLUDED.tags,
  summary = EXCLUDED.summary, community = EXCLUDED.community;

-- Edges
-- 未类型 wikilink
INSERT INTO wiki_edges (source, target, relation, confidence, typed)
VALUES ('concepts/transformers', 'entities/vaswani', 'wikilink', 'EXTRACTED', false)
ON CONFLICT (source, target, relation) DO UPDATE SET confidence = EXCLUDED.confidence, typed = EXCLUDED.typed;

-- 类型边来自 relationships: 块
INSERT INTO wiki_edges (source, target, relation, confidence, typed)
VALUES ('concepts/transformers', 'concepts/lstm', 'contradicts', 'EXTRACTED', true)
ON CONFLICT (source, target, relation) DO UPDATE SET confidence = EXCLUDED.confidence, typed = EXCLUDED.typed;
```

为每个页面写入一个 `INSERT ... ON CONFLICT (id) DO UPDATE` 语句（值转义：单引号加倍，`tags` 作为 JSON 数组字面量序列化为 `jsonb`），然后为每个边写入一个 `INSERT ... ON CONFLICT (source, target, relation) DO UPDATE` 语句。`relation` 这里保持小写（与 Cypher 关系标签的大写不同），因为它是一个普通列值，不是模式标识符 — 这使其可直接通过 `WHERE relation = 'contradicts'` 过滤或无需大小写折叠即可连接。`typed` 仅在 `relationships:` frontmatter 条目提升的边中为 `true`；普通 wikilinks 保持 `false`。

跳过 `id` 仅在 `ON CONFLICT` 子句触发后冲突的页面 — 不要尝试去重合成的多边（例如具有 `wikilink` 和类型关系的相同 source/target），因为复合主键 `(source, target, relation)` 已经将它们作为不同行保留，匹配 `graph.json`/`graph.graphml` 在查询层上的“类型版本优先”合并行为（`SELECT * FROM wiki_edges WHERE source=$1 AND target=$2 ORDER BY typed DESC LIMIT 1`）。

---

### 3e. `graph.html`

使用 vis.js CDN 的自包含交互式可视化（无需本地依赖）。用户在任何浏览器中打开此文件 — 无需服务器。

通过以下步骤构建 HTML 文件：

1. 生成 vis.js 节点对象的 JSON 数组：
```js
{id: "concepts/transformers", label: "Transformer Architecture", color: {background: "#4E79A7"}, size: <degree * 3 + 8>, title: "concepts | #ml #architecture", community: 0}
```
- 按社区着色（循环使用：`#4E79A7`、`#F28E2B`、`#E15759`、`#76B7B2`、`#59A14F`、`#EDC948`、`#B07AA1`、`#FF9DA7`、`#9C755F`、`#BAB0AC`）
- 按度（入站+出站链接数）调整大小：`size = degree * 3 + 8`，最大值 60
- `title` = 悬停时显示的提示文本：类别、标签、摘要（如果可用）

2. 生成 vis.js 边对象的 JSON 数组：
```js
// 未类型 wikilink
{from: "concepts/transformers", to: "entities/vaswani", dashes: false, width: 1, color: {color: "#666", opacity: 0.6}, title: "wikilink"}
// 类型边
{from: "concepts/transformers", to: "concepts/lstm", dashes: false, width: 2, color: {color: "#E15759", opacity: 0.8}, label: "contradicts", font: {size: 9, color: "#ccc"}, title: "contradicts"}
```
- `dashes: true` 用于 INFERRED 边
- `dashes: [4,8]` 用于 AMBIGUOUS 边
- **类型边**（`typed: true`）：设置 `width: 2`，添加 `label` 字段显示类型，并应用类型特定颜色：

| 类型 | 边颜色 |
|---|---|
| `extends` | `#59A14F`（绿色） |
| `implements` | `#4E79A7`（蓝色） |
| `contradicts` | `#E15759`（红色） |
| `derived_from` | `#F28E2B`（橙色） |
| `uses` | `#76B7B2`（青色） |
| `replaces` | `#B07AA1`（紫色） |
| `related_to` | `#BAB0AC`（灰色 — 与未类型相同） |

未类型的 `wikilink` 边保留现有的 `#666` 灰色颜色且无标签。

3. 写入完整 HTML 文件：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Wiki 知识图谱</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f0f1a; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; height: 100vh; }
  #graph { flex: 1; }
  #sidebar { width: 260px; background: #1a1a2e; border-left: 1px solid #2a2a4e; padding: 14px; overflow-y: auto; font-size: 13px; }
  #sidebar h3 { color: #aaa; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 10px; }
  #info { margin-bottom: 16px; line-height: 1.6; color: #ccc; }
  .legend-item { display: flex; align-items: center; gap: 8px; padding: 3px 0; font-size: 12px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  #stats { margin-top: 16px; color: #555; font-size: 11px; }
</style>
</head>
<body>
<div id="graph"></div>
<div id="sidebar">
  <h3>Wiki 知识图谱</h3>
  <div id="info">点击节点以查看详情。</div>
  <h3 style="margin-top:12px">社区</h3>
  <div id="legend"><!-- 由 JS 填充 --></div>
  <div id="stats"><!-- 由 JS 填充 --></div>
</div>
<script>
const NODES_DATA = /* NODES_JSON */;
const EDGES_DATA = /* EDGES_JSON */;
const COMMUNITY_COLORS = ["#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC"];

const nodes = new vis.DataSet(NODES_DATA);
const edges = new vis.DataSet(EDGES_DATA);
const network = new vis.Network(document.getElementById('graph'), {nodes, edges}, {
  physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -60, springLength: 120 }, stabilization: { iterations: 200 } },
  interaction: { hover: true, tooltipDelay: 100 },
  nodes: { shape: 'dot', borderWidth: 1.5 },
  edges: { smooth: { type: 'continuous' }, arrows: { to: { enabled: true, scaleFactor: 0.4 } } }
});
network.once('stabilizationIterationsDone', () => network.setOptions({ physics: { enabled: false } }));

network.on('click', ({nodes: sel}) => {
  if (!sel.length) return;
  const n = NODES_DATA.find(x => x.id === sel[0]);
  if (!n) return;
  document.getElementById('info').innerHTML = `<b>${n.label}</b><br>类别：${n.category||'—'}<br>标签：${n.tags||'—'}<br>${n.summary ? '<br>'+n.summary : ''}`;
});

// 构建图例
const communities = {};
NODES_DATA.forEach(n => { if (n.community != null) communities[n.community] = (communities[n.community]||0)+1; });
const leg = document.getElementById('legend');
Object.entries(communities).sort((a,b)=>b[1]-a[1]).forEach(([cid, count]) => {
  const color = COMMUNITY_COLORS[cid % COMMUNITY_COLORS.length];
  leg.innerHTML += `<div class="legend-item"><div class="dot" style="background:${color}"></div>社区 ${cid}（${count}）</div>`;
});
document.getElementById('stats').textContent = `${NODES_DATA.length} 个页面 · ${EDGES_DATA.length} 个链接`;
</script>
</body>
</html>
```

将 `/* NODES_JSON */` 和 `/* EDGES_JSON */` 替换为您在步骤 1 中生成的实际 JSON 数组。

---

## 步骤 3.5：OKF 捆绑包导出（可选）

**仅当**用户要求 OKF / markdown 捆绑包时（例如包含“export to OKF”、“OKF bundle”、“open knowledge format”、“export as markdown bundle”等短语）才执行此步骤。此步骤为附加功能——上述五个图谱文件始终会生成；此步骤额外写入一个完整的 markdown 捆绑包。

这五个图谱文件是一种*有损*投影（仅图谱骨架）。而**OKF 捆绑包是实际的页面正文**，因此通过 OKF 进行导出→`wiki-import` 往返可以保留完整内容，并且捆绑包可直接导入 MkDocs、Notion、Hugo、GitHub 的渲染器或任何 [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) 消费者。

### 标准 frontmatter 映射（obsidian-wiki ⇄ OKF）

此表是映射关系的唯一事实来源；`wiki-import` 在反向方向引用它。

| OKF 键       | ← 导出自           | → 导入到              | 备注 |
|---------------|-------------------------|--------------------------|-------|
| `type`（必需） | `category`，标题大写 | `category`（小写） | `concepts`→`Concept`，`entities`→`Entity`，`skills`→`Skill`，`references`→`Reference`，`synthesis`→`Synthesis`，`projects`→`Project`，`journal`→`Journal`。OKF 要求 `type`；消费者容忍任意字符串。 |
| `title`       | `title`                 | `title`                  | 原样保留。 |
| `description` | `summary`               | `summary`                | 我们的单行 `summary:` 正是 OKF 的 `description`（用于 `index.md` 条目）。 |
| `tags`        | `tags`                  | `tags`                   | 原样保留列表。`visibility/*` 系统标签原样通过。 |
| `timestamp`   | `updated`               | `updated`                | 两侧均为 ISO 8601。 |
| `resource`    | 第一个 `sources:` 条目**仅当**它是 `http(s)://` URL | — | 可选；无源 URL 时省略。大多数页面描述抽象知识，没有此项。 |
| *(扩展)* | `category`、`sources`、`created`、`relationships`、`lifecycle`、`tier`、`base_confidence`、… | 原样保留 | OKF §4.1 允许任意键，并要求消费者保留它们。**将我们的原生键作为 OKF 扩展 frontmatter 写入，正是使往返无损的原因** —— 在导入时，保留的 `category`/`created`/`sources` 优先于从 `type` 重新推导。 |

### 步骤

复用步骤 1 中的节点列表（已应用任何活动的项目/可见性筛选器）。在 `wiki-export/okf/` 下写入目录树：

1. **每个范围内的页面一个文件。** 对于每个页面，解析其 frontmatter，应用上述映射表构建 OKF frontmatter（先写必需的 `type`，然后是 `title`、`description`、`tags`、`timestamp`、可选的 `resource`，最后是保留的扩展键），转换正文链接（如下），并写入 `wiki-export/okf/<category>/<slug>.md` —— 与页面在保险库中的相对路径相同。

2. **正文链接转换**（`[[wikilinks]]` → 标准 markdown 链接）：
   - `[[concepts/transformers]]` → `[<目标标题>](<文件相对路径>.md)`，例如从 `entities/foo.md` 链接到 `concepts/transformers` 变为 `[Transformer Architecture](../concepts/transformers.md)`。链接文本 = 目标页面的 `title`（若未知则回退到目标 id）。
   - `[[target|display]]` → `[display](<相对路径>.md)`。
   - 使用**文件相对**路径（`../concepts/x.md`），**绝不用** `/` 绝对路径 —— `/` 根链接会破坏 GitHub 渲染。（这与 knowledge-catalog 自身的生产代理一致。）
   - 从**目标文件路径**（而非裸页面 id）计算相对路径：将 wikilink 目标规范化为其页面 id，追加 `.md`，然后计算 `relpath(<目标文件>, <源文件目录>)`。切勿在添加 `.md` 前对 id 调用 `relpath()`。
   - 对于常见的“文件夹笔记”布局（一个页面 id 同时作为文件和目录前缀存在）是必需的，例如 `projects/social-twitter.md` 加上 `projects/social-twitter/...`。从 `projects/social-twitter/concepts/mem0-memory-analysis.md` 出发，链接到 `[[projects/social-twitter]]` 必须导出为 `../../social-twitter.md`，而非 `...md`。
   - 使用步骤 1 中相同的规范化方法（小写、空格→连字符、去除 `.md`）解析链接目标。按形式处理未解析的目标，使前向引用在往返中存活：
     - **解析到范围内的页面** → 指向它的相对 markdown 链接。
     - **路径形式目标**（包含 `/`，例如 `[[concepts/attention-mechanism]]`）**尚无页面**，且未被活动筛选器排除 → 仍然发出相对 markdown 链接。OKF §5.3 将缺失的目标视为尚未编写的知识，保留链接使用户的前向引用在重新导入时无损。（已在 st3ve 上验证：丢弃这些会静默删除真实的 `[[wikilinks]]`。）
     - **被活动的项目/可见性筛选器排除** → 纯文本。不要发出指向被过滤内容的路径。
     - **裸标题目标**无匹配（例如范围内不存在该页面时的 `[[tractorex]]`） → 纯文本；没有可靠路径可写。
   - 保持现有外部 `http(s)://` 链接和 `# Citations` 部分不变。

3. **生成 `index.md` 文件**（OKF §6 渐进式披露；这些不包含每个条目的 frontmatter）：
   - 捆绑包根 `wiki-export/okf/index.md` —— 一个 `# Subdirectories` 部分，列出每个类别文件夹：`* [<category>](<category>/index.md) - <类别的单行描述>`。这是**唯一**允许 frontmatter 的索引：添加单个键 `okf_version: "0.1"`（OKF §11）。
   - 每个类别文件夹一个 `index.md`，列出其页面：`* [<title>](<slug>.md) - <来自页面 summary 的描述>`。

4. **复制 `log.md`** 从保险库根目录原样复制到 `wiki-export/okf/log.md`（OKF §7 将行首粗体动作词视为惯例，因此现有的基于行的日志是符合规范的）。

5. **筛选器。** 遵循与图谱导出相同的项目/可见性筛选器 —— 被过滤的页面从捆绑包中省略，其入向链接根据步骤 2 降级为纯文本。

排除在捆绑包之外（与图谱导出相同）：`_archives/`、`_raw/`、`_readouts/`、`.obsidian/`、`_insights.md`、`_meta/*.base`，以及保险库根 `index.md`（上述已重新生成）。

---

## 步骤 4：打印摘要

```
Wiki 导出完成 → wiki-export/
  graph.json    — N 个节点，M 个边（NetworkX node_link 格式）
  graph.graphml — N 个节点，M 个边（Gephi / yEd / Cytoscape）
  cypher.txt    — N 个 MERGE 节点 + M 个 MERGE 关系（Neo4j）
  postgres.sql  — N 条 upsert 行（wiki_pages）+ M 条 upsert 行（wiki_edges）（任意 Postgres）
  graph.html    — 交互式浏览器可视化（在任意浏览器中打开）
```

仅在生成了 OKF 捆绑包（步骤 3.5）时附加此行：
```
  okf/          — OKF v0.1 markdown 捆绑包（N 个页面，无损；通过 wiki-import 导入）
```

筛选器活动时附加筛选器说明：
```
  （已筛选：project:prismor — 67 个页面中的 19 个）
  （已筛选：排除了 Y 个页面中的 X 个 — visibility/internal、visibility/pii）
```
仅包含实际应用的筛选器对应的行。

## 备注

- **重新运行是安全的** —— 所有输出文件（及 `okf/` 捆绑包）在每次运行时都被覆盖
- **断开的 wikilinks 会被跳过** —— 仅导出指向保险库中存在页面的边；在 OKF 捆绑包中，指向缺失/被过滤页面的 wikilink 降级为纯文本
- **OKF 是无损格式** —— 导入时 `graph.json` 仅能重建存根，而 `okf/` 捆绑包保留完整页面正文。对于保险库到保险库的传输和外部 markdown 工具（MkDocs、Notion、GitHub），使用 OKF；对于分析工具（Gephi、Neo4j），使用图谱文件
- **如果保险库使用了版本控制，`wiki-export/` 目录应加入 gitignore** —— 这些是派生产物
- **`graph.json` 是主要格式** —— 其他格式均由它派生。如果未来某工具原生支持图查询，将其指向 `graph.json`
