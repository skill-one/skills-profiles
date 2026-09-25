# /understand-diff

分析当前代码变更与项目数据目录（`.ua/knowledge-graph.json`，或当该目录存在时为遗留的`.understand-anything/knowledge-graph.json`）中的知识图谱进行比对。

## 图结构参考

知识图谱的JSON具有以下结构：
- `project` — {name, description, languages, frameworks, analyzedAt, gitCommitHash}
- `nodes[]` — 每个节点包含 {id, type, name, filePath?, summary, tags[], complexity, languageNotes?}
  - 代码节点类型：文件、函数、类、模块、概念
  - 非代码节点类型：配置、文档、服务、表格、端点、管道、模式、资源
  - 领域/知识节点类型：领域、流程、步骤、文章、实体、主题、声明、来源
  - ID使用节点类型作为前缀，例如 `file:path`, `function:path:name`, `config:path`, `article:path`
- `edges[]` — 每个边包含 {source, target, type, direction, weight}
  - 关键类型：导入、包含、调用、依赖、配置、文档、部署、触发、包含流程、流程步骤、相关、引用
- `layers[]` — 每个层包含 {id, name, description, nodeIds[]}
- `tour[]` — 每个导览包含 {order, title, description, nodeIds[]}

## 如何高效阅读

1. 在阅读完整文件之前，使用Grep在JSON中搜索相关条目
2. 仅阅读需要的部分 — 不要将整个图谱加载到上下文中
3. 节点名称和摘要是最有用的字段，用于理解
4. 边描述了组件如何连接 — 跟踪导入和调用以获取依赖链

## 操作步骤

1. **解析数据目录`$UA_DIR`**。运行`UA_DIR=$([ -d .understand-anything ] && echo .understand-anything || echo .ua)` — 当遗留的`.understand-anything/`目录已存在时使用它，否则使用新的`.ua/`。检查`$UA_DIR/knowledge-graph.json`是否存在。如果不存在，提示用户先运行`/understand`。

2. **获取变更文件列表**（此时不要读取图谱）：
   - 如果在包含未提交变更的分支上：`git diff --name-only`
   - 如果在特性分支上：`git diff main...HEAD --name-only`（或基础分支）
   - 如果用户指定了PR编号：从该PR获取变更差异

3. **读取项目元数据和检查图谱新鲜度** — 使用Grep或带行数限制的Read提取`"project"`部分，包括`gitCommitHash`作为`GRAPH_COMMIT_RAW`，然后：
   - 在使用Git diff之前将其解析为提交。从项目根目录，比较解析的提交与`git rev-parse HEAD`，并检查项目范围的已提交和工作树变更：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .`路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。当项目diff为空时，仅哈希不匹配不是过时的。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/`或遗留的`.understand-anything/`），因为它包含生成的图谱工件，而不是项目源代码漂移。
   - 如果已提交的diff或任何工作树命令报告项目文件，在影响分析之前发出警告，图谱可能遗漏了这些变更。建议：运行`/understand`以刷新图谱。
   - 仅当`GRAPH_COMMIT_RAW`解析成功时运行提交diff。如果图谱提交或Git元数据缺失、无效或不可用，给出简短的最佳努力警告并继续，而不是阻止。

4. **查找变更文件的节点** — 对于每个变更文件路径，使用Grep在知识图谱中搜索：
   - 匹配`"filePath"`值的节点（例如，`grep "changed/file/path"`）
   - 这会找到文件级节点（包括非代码类型）以及在这些文件中定义的函数/类节点
   - 记录所有匹配节点的`id`值

5. **查找连接的边（1跳）** — 对于每个匹配的节点ID，在边中Grep该ID以查找：
   - 导入或依赖变更节点的组件（上游调用者）
   - 变更节点导入或调用的组件（下游依赖）
   - 这些是"受影响的组件" — 可能会中断或需要更新的东西

6. **识别受影响的层** — 在`"layers"`部分中Grep匹配的节点ID，以确定哪些架构层被触及。

7. **提供结构化分析**：
   - **变更组件**：直接修改的内容（来自匹配节点的摘要）
   - **受影响组件**：可能受影响的组件（来自1跳边）
   - **受影响层**：被触及的架构层和跨层关注点
   - **风险评估**：根据节点`complexity`值、跨层边的数量和爆炸半径（受影响的组件数量）
   - 建议仔细审查的内容和任何潜在问题

8. **为仪表板编写diff叠加** — 在生成分析后，将diff数据写入`$UA_DIR/diff-overlay.json`，以便仪表板可以可视化变更和受影响的组件。文件包含：
   ```json
   {
     "version": "1.0.0",
     "baseBranch": "<使用的基分支>",
     "generatedAt": "<ISO时间戳>",
     "changedFiles": ["<变更文件路径列表>"],
     "changedNodeIds": ["<步骤4的节点ID>"],
     "affectedNodeIds": ["<步骤5的节点ID，排除changedNodeIds>"]
   }
   ```
   写入后，告诉用户可以运行`/understand-anything:understand-dashboard`查看diff叠加的可视化效果。
