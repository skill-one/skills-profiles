---
name: understand-diff
description: 当您需要分析 git 差异或拉取请求，以了解发生了什么更改、受影响的组件以及风险时使用。
---

# /understand-diff

分析当前代码变更与项目数据目录（`.ua/knowledge-graph.json`，或在存在该目录时使用遗留的 `.understand-anything/knowledge-graph.json`）中的知识图谱。

## 图结构参考

知识图谱 JSON 具有如下结构：
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
2. 仅阅读需要的部分 — 不要将整个图谱导入上下文
3. 节点名称和摘要是最有用的字段，用于理解
4. 边缘告诉你组件如何连接 — 跟随导入和调用以获取依赖链

## 操作说明

1. **解析数据目录 `$UA_DIR`**。运行 `UA_DIR=$([ -d .understand-anything ] && echo .understand-anything || echo .ua)` — 当已存在时，这是遗留的 `.understand-anything/`，否则是新的 `.ua/`。检查 `$UA_DIR/knowledge-graph.json` 是否存在。如果不存在，提示用户先运行 `/understand`。

2. **获取变更文件列表**（不要先读取图谱）：
   - 如果在包含未提交变更的分支上：`git diff --name-only`
   - 如果在特性分支上：`git diff main...HEAD --name-only`（或基础分支）
   - 如果用户指定了 PR 编号：从该 PR 获取变更

3. **读取项目元数据和检查图谱新鲜度** — 使用 Grep 或带行数限制的 Read 提取 `"project"` 部分，包括 `gitCommitHash` 作为 `GRAPH_COMMIT_RAW`，然后：
   - 在使用 Git diff 之前将其解析为提交。从项目根目录，比较解析的提交与 `git rev-parse HEAD`，并检查项目范围的已提交和工作树变更：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .` 路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。仅哈希不匹配本身在项目 diff 为空时不是过时。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/` 或遗留的 `.understand-anything/`），因为它包含生成的图谱工件，而不是项目源代码漂移。
   - 如果已提交的 diff 或任何工作树命令报告项目文件，则在影响分析之前警告图谱可能遗漏这些变更。建议：运行 `/understand` 刷新图谱。
   - 仅在 `GRAPH_COMMIT_RAW` 解析成功时运行提交 diff。如果图谱提交或 Git 元数据缺失、无效或不可用，给出简短的尽力警告并继续，而不是阻止。

4. **查找变更文件的节点** — 对于每个变更文件路径，使用 Grep 在知识图谱中搜索：
   - 匹配 `"filePath"` 值的节点（例如，`grep "changed/file/path"`）
   - 这会找到文件级节点（包括非代码类型）和在这些文件中定义的函数/类节点
   - 记录所有匹配节点的 `id` 值

5. **查找连接的边（1跳）** — 对于每个匹配的节点 ID，Grep 该 ID 在边中查找：
   - 导入或依赖变更节点的（上游调用者）
   - 变更节点导入或调用的（下游依赖）
   - 这些是“受影响的组件”——可能中断或需要更新的东西

6. **识别受影响的层** — Grep 匹配的节点 ID 在 `"layers"` 部分中，以确定哪些架构层被触及。

7. **提供结构化分析**：
   - **变更组件**：直接修改的内容（来自匹配节点的摘要）
   - **受影响组件**：可能受影响的（来自 1 跳边）
   - **受影响层**：被触及的架构层和跨层问题
   - **风险评估**：基于节点 `complexity` 值、跨层边的数量和爆炸半径（受影响的组件数量）
   - 建议仔细审查的内容和任何潜在问题

8. **为仪表板编写 diff 叠加** — 在生成分析后，将 diff 数据写入 `$UA_DIR/diff-overlay.json`，以便仪表板可以可视化变更和受影响的组件。文件包含：
   ```json
   {
     "version": "1.0.0",
     "baseBranch": "<使用的基分支>",
     "generatedAt": "<ISO 时间戳>",
     "changedFiles": ["<变更文件路径列表>"],
     "changedNodeIds": ["<来自步骤 4 的节点 ID>"],
     "affectedNodeIds": ["<来自步骤 5 的节点 ID，排除 changedNodeIds>"]
   }
   ```
   写入后，告诉用户可以运行 `/understand-anything:understand-dashboard` 查看diff叠加的可视化效果。
