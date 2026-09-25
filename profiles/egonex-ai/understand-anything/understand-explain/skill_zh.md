# /understand-explain

对特定代码组件提供全面、深入的说明。

## 图结构参考

知识图谱的 JSON 结构如下：
- `project` — {name, description, languages, frameworks, analyzedAt, gitCommitHash}
- `nodes[]` — 每个 {id, type, name, filePath?, summary, tags[], complexity, languageNotes?}
  - 代码节点类型：文件、函数、类、模块、概念
  - 非代码节点类型：配置、文档、服务、表格、端点、管道、模式、资源
  - 领域/知识节点类型：领域、流程、步骤、文章、实体、主题、声明、来源
  - ID 使用节点类型作为前缀，例如 `file:path`, `function:path:name`, `config:path`, `article:path`
- `edges[]` — 每个 {source, target, type, direction, weight}
  - 关键类型：导入、包含、调用、依赖、配置、文档、部署、触发、包含流程、流程步骤、相关、引用
- `layers[]` — 每个 {id, name, description, nodeIds[]}
- `tour[]` — 每个 {order, title, description, nodeIds[]}

## 如何高效阅读

1. 在阅读完整文件之前，使用 Grep 在 JSON 中搜索相关条目
2. 仅阅读需要的部分 — 不要将整个图谱加载到上下文中
3. 节点名称和摘要是最有用的字段，用于理解
4. 边缘告诉你组件如何连接 — 跟随导入和调用以获取依赖链

## 说明

1. **解析数据目录 `$UA_DIR`**。运行 `UA_DIR=$([ -d .understand-anything ] && echo .understand-anything || echo .ua)` — 如果 `.understand-anything` 已经存在，这是遗留的 `.understand-anything/`，否则是新创建的 `.ua/`。检查 `$UA_DIR/knowledge-graph.json` 是否存在。如果不存在，提示用户先运行 `/understand`。

2. **在使用基于图谱的上下文之前检查图谱的新鲜度**：
   - 从图谱元数据中读取 `project.gitCommitHash` 作为 `GRAPH_COMMIT_RAW`。在将其用于任何 Git 差异之前，将其解析为提交，然后将其与 `git rev-parse HEAD` 进行比较，并检查从项目根目录的项目范围提交和工作树变更：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .` 路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。当项目差异为空时，哈希不匹配本身不是过时的。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/` 或遗留的 `.understand-anything/`），因为它包含生成的图谱工件，而不是项目源代码的漂移。
   - 如果提交差异或任何工作树命令报告项目文件，请在解释之前发出警告，说明基于图谱的上下文可能遗漏这些更改。建议：运行 `/understand` 以刷新图谱。
   - 仅在 `GRAPH_COMMIT_RAW` 解析成功时运行提交差异。如果图谱提交或 Git 元数据丢失、无效或不可用，请给出简短的尽力而为的警告并继续，而不是阻止。

3. **找到目标节点** — 使用 Grep 在知识图谱中搜索组件："$ARGUMENTS"
   - 对于文件路径（例如 `src/auth/login.ts`）：搜索 `"filePath"` 匹配
   - 对于函数表示（例如 `src/auth/login.ts:verifyToken`）：在 `"name"` 字段中搜索函数名称，并按文件路径过滤
   - 记录确切的节点 `id`, `type`, `summary`, `tags` 和 `complexity`

4. **找到所有连接的边缘** — 在边缘部分中搜索目标节点的 ID：
   - `"source"` 匹配 → 此节点调用/导入/依赖的项（传出）
   - `"target"` 匹配 → 调用/导入/依赖此节点的项（传入）
   - 记录连接的节点 ID 和边缘类型

5. **阅读连接的节点** — 对于步骤 4 中的每个连接节点 ID，在节点部分中搜索这些 ID 以获取它们的 `name`, `summary` 和 `type`。这构建了组件的邻域。

6. **识别层级** — 在 `"layers"` 部分中搜索目标节点的 ID，以找到它所属的架构层级和该层级的描述。

7. **阅读实际的源文件** — 阅读节点 `filePath` 指向的源文件，以进行深入分析。

8. **在上下文中解释组件**：
   - 它在架构中的作用（哪个层级，为什么存在）
   - 内部结构（它包含的函数、类 — 来自 `contains` 边缘）
   - 外部连接（它导入的项、调用它的项、它依赖的项 — 来自边缘）
   - 数据流（输入 → 处理 → 输出 — 来自源代码）
   - 清晰解释，假设读者可能不熟悉编程语言
   - 突出任何值得理解的模式、惯用语句或复杂性
