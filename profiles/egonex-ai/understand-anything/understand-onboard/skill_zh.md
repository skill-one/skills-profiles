# /understand-onboard

从项目的知识图谱生成一份全面的入门指南。

## 图结构参考

知识图谱的 JSON 结构如下：
- `project` — {name, description, languages, frameworks, analyzedAt, gitCommitHash}
- `nodes[]` — 每个 {id, type, name, filePath?, summary, tags[], complexity, languageNotes?}
  - 代码节点类型：file, function, class, module, concept
  - 非代码节点类型：config, document, service, table, endpoint, pipeline, schema, resource
  - 领域/知识节点类型：domain, flow, step, article, entity, topic, claim, source
  - ID 使用节点类型作为前缀，例如 `file:path`, `function:path:name`, `config:path`, `article:path`
- `edges[]` — 每个 {source, target, type, direction, weight}
  - 关键类型：imports, contains, calls, depends_on, configures, documents, deploys, triggers, contains_flow, flow_step, related, cites
- `layers[]` — 每个 {id, name, description, nodeIds[]}
- `tour[]` — 每个 {order, title, description, nodeIds[]}

## 如何高效阅读

1. 在阅读完整文件之前，使用 Grep 在 JSON 中搜索相关条目
2. 只阅读需要的部分 — 不要将整个图谱导入上下文
3. 节点名称和摘要是最有用的字段，用于理解
4. 边缘告诉您组件如何连接 — 跟随 imports 和 calls 以获取依赖链

## 操作说明

1. **解析数据目录 `$UA_DIR`**。运行 `UA_DIR=$([ -d .understand-anything ] && echo .understand-anything || echo .ua)` — 如果 `.understand-anything` 已经存在，这是遗留的 `.understand-anything/`，否则是新创建的 `.ua/`。检查 `$UA_DIR/knowledge-graph.json` 是否存在。如果不存在，提示用户先运行 `/understand`。

2. **在使用基于图谱的上下文之前检查图谱的新鲜度**：
   - 从图谱元数据中读取 `project.gitCommitHash` 作为 `GRAPH_COMMIT_RAW`。在将其用于任何 Git diff 之前解析它，然后将其与 `git rev-parse HEAD` 进行比较，并从项目根目录检查项目范围的已提交和工作树变更：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .` 路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。当项目 diff 为空时，哈希不匹配本身不是过时的。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/` 或遗留的 `.understand-anything/`），因为它包含生成的图谱工件，而不是项目源代码的漂移。
   - 如果已提交的 diff 或任何工作树命令报告项目文件，则在生成指南之前发出警告，提示入门内容可能省略了这些更改。建议：运行 `/understand` 刷新图谱。
   - 仅当 `GRAPH_COMMIT_RAW` 解析成功时才运行提交 diff。如果图谱提交或 Git 元数据丢失、无效或不可用，请给出简短的尽力而为的警告并继续，而不是阻止。

3. **读取项目元数据** — 使用 Grep 或带行数限制的 Read 来提取 `"project"` 部分（名称、描述、语言、框架）。

4. **读取层级** — Grep `"layers"` 以获取完整的层级数组。这些定义了架构，并将结构化指南。

5. **读取 tour** — Grep `"tour"` 以获取引导式演练步骤。这些提供了推荐的学习路径。

6. **仅读取文件级结构节点** — 使用 Grep 在知识图谱中查找具有文件级类型的节点（`file`, `config`, `document`, `service`, `pipeline`, `table`, `schema`, `resource`, `endpoint`）。跳过函数级和类级节点以保持指南的高层次。提取每个节点的 `name`, `filePath`, `summary` 和 `complexity`。

7. **识别复杂度热点** — 从文件级节点中找到具有最高 `complexity` 值的节点。这些是新开发人员应谨慎处理的区域。

8. **生成入门指南**，包含以下部分：
   - **项目概述**：名称、语言、框架、描述（来自项目元数据）
   - **架构层级**：每个层级的名称、描述和关键文件（来自层级 + 文件节点）
   - **关键概念**：重要模式和设计决策（来自节点摘要和标签）
   - **引导式 Tour**：分步演练（来自 tour 部分）
   - **文件映射**：每个关键文件的作用（来自文件级节点，按层级组织）
   - **复杂度热点**：需要谨慎处理的区域（来自复杂度值）

9. 格式化为干净的 markdown
10. 提供保存指南到项目中的 `docs/UA_ONBOARDING.md`
11. 建议用户将文件提交到仓库供团队使用
