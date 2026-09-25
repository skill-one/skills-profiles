# /understand-chat

使用项目数据目录（`.ua/knowledge-graph.json`，或者在存在该目录时使用遗留的 `.understand-anything/knowledge-graph.json`）中的知识图谱来回答关于此代码库的问题。

## 图结构参考

知识图谱 JSON 具有如下结构：
- `project` — {name, description, languages, frameworks, analyzedAt, gitCommitHash}
- `nodes[]` — 每个 {id, type, name, filePath?, summary, tags[], complexity, languageNotes?}
  - 代码节点类型：文件、函数、类、模块、概念
  - 非代码节点类型：配置、文档、服务、表格、端点、管道、模式、资源
  - 领域/知识节点类型：领域、流程、步骤、文章、实体、主题、声明、来源
  - ID 使用节点类型作为前缀，例如 `file:path`、`function:path:name`、`config:path`、`article:path`
- `edges[]` — 每个 {source, target, type, direction, weight}
  - 关键类型：导入、包含、调用、依赖、配置、文档、部署、触发、包含流程、流程步骤、相关、引用
- `layers[]` — 每个 {id, name, description, nodeIds[]}
- `tour[]` — 每个 {order, title, description, nodeIds[]}

## 如何高效阅读

1. 在阅读完整文件之前，使用 Grep 在 JSON 中搜索相关条目
2. 只阅读需要的部分 — 不要将整个图谱加载到上下文中
3. 节点名称和摘要是最有用的字段，用于理解
4. 边缘告诉你组件如何连接 — 跟随导入和调用以获取依赖链

## 说明

1. **解析数据目录 `$UA_DIR`**。运行 `UA_DIR=$([ -d .understand-anything ] && echo .understand-anything || echo .ua)` — 当遗留的 `.understand-anything/` 已经存在时，这是遗留目录，否则是新目录 `.ua/`。检查当前项目根目录中是否存在 `$UA_DIR/knowledge-graph.json`。如果不存在，告诉用户先运行 `/understand`。

2. **在使用基于图谱的上下文之前检查图谱的新鲜度**：
   - 从图谱元数据中读取 `project.gitCommitHash` 作为 `GRAPH_COMMIT_RAW`。在将其用于任何 Git 差异之前，将其解析为提交，然后将其与 `git rev-parse HEAD` 进行比较，并从项目根目录检查项目范围的已提交和工作树变更：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .` 路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。当项目差异为空时，单独的哈希不匹配不是过时的。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/` 或遗留的 `.understand-anything/`），因为它包含生成的图谱工件，而不是项目源代码漂移。
   - 如果已提交的差异或任何工作树命令报告项目文件，则在回答之前发出警告，说明基于图谱的上下文可能遗漏了这些更改。建议：运行 `/understand` 以刷新图谱。
   - 仅当 `GRAPH_COMMIT_RAW` 解析成功时才运行提交差异。如果图谱提交或 Git 元数据丢失、无效或不可用，则给出简短的尽力而为的警告并继续，而不是阻止。

3. **仅读取项目元数据** — 使用 Grep 或带行数限制的读取来从文件顶部提取仅 `"project"` 部分以获取上下文（名称、描述、语言、框架）。

4. **搜索相关节点** — 使用 Grep 在知识图谱文件中搜索用户的查询关键字："$ARGUMENTS"
   - 搜索 `"name"` 字段：`grep -i "query_keyword"` 在图谱文件中
   - 搜索 `"summary"` 字段以进行语义匹配
   - 搜索 `"tags"` 数组以进行主题匹配
   - 记录所有匹配节点的 `id` 值

5. **查找连接的边缘** — 对于每个匹配的节点 ID，在 `edges` 部分中 Grep 该 ID 以找到：
   - 它导入或依赖的内容（下游）
   - 调用或导入它的内容（上游）
   - 这为您提供了查询周围的 1 跳子图谱

6. **读取层上下文** — Grep `"layers"` 以了解匹配的节点属于哪些架构层。

7. **使用相关子图谱回答查询**：
   - 引用图谱中的特定文件、函数和关系
   - 解释哪些层是相关的以及原因
   - 简洁但全面 — 将概念链接到实际代码位置
   - 如果查询没有匹配任何节点，请说明并建议图谱中的相关术语
