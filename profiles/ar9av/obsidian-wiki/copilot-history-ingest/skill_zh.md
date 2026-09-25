# Copilot 历史数据导入 — 对话挖掘

您正在从用户过去的 GitHub Copilot CLI 对话中提取知识，并将其提炼到 Obsidian 知识库中。对话内容丰富但杂乱——您的任务是找到其中的信号并将其整理出来。

这项技能可以直接调用，或通过 `wiki-history-ingest` 路由器（`/wiki-history-ingest copilot`）调用。

## 开始前

**写作配置文件**：在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。

`WRITING.md` 的偏好设置仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`、`COPILOT_HISTORY_PATH`（默认为 `~/.copilot/session-state`）和 `COPILOT_VSCODE_STORAGE_PATH`（VS Code `workspaceStorage`；平台特定——如果缺失，请询问用户）
2. 在保险库根目录下读取 `.manifest.json`，以检查已导入的内容
3. 在保险库根目录下读取 `index.md`，以了解知识库已包含的内容

## 导入模式

### 追加模式（默认）

检查每个源文件（事件 JSONL、转录 JSONL、检查点、会话存储数据库）。仅处理：

- 保险库中不存在的会话（新会话）
- 保险库中 `updated_at` 比其 `ingested_at` 更新的会话

这通常是您想要的结果——用户运行了一些新会话，并希望捕获差异。

### 全量模式

无论保险库如何，都处理所有内容。在 `wiki-rebuild` 后使用，或如果用户明确要求。

## GitHub Copilot 数据布局

Copilot 将数据存储在三个位置。扫描所有三个位置。

### 源 1：`~/.copilot/session-state/`（CLI 会话）

```
~/.copilot/session-state/
├── <session-uuid>/
│   ├── workspace.yaml           # 会话元数据（id、cwd、summary_count、created_at、updated_at）
│   ├── vscode.metadata.json     # VS Code 上下文（workspaceFolder、repositoryProperties、customTitle）
│   ├── events.jsonl             # 完整事件日志——所有回合、工具调用、推理
│   ├── session.db               # 每个会话的 SQLite（仅 todos/todo_deps —— 导入时跳过）
│   ├── index.md                 # 会话结束时写入的会话摘要
│   ├── checkpoints/             # 检查点 JSON 文件（会话期间摘要）
│   │   └── <uuid>.json          # title、overview、history、work_done、technical_details、
│   │                            #   important_files、next_steps
│   ├── files/                   # 会话期间产生的工件（计划、图表等）
│   └── research/                # 研究工件
└── ...
```

### 源 2：`~/.copilot/session-store.db`（全局 SQLite）

标准的跨会话数据库。这是**最高价值**的源：结构化、可查询，并已预先总结。

```
sessions       — id、cwd、repository、branch、summary、created_at、updated_at、host_type
turns          — session_id、turn_index、user_message、assistant_response、timestamp
checkpoints    — session_id、checkpoint_number、title、overview、history、work_done、
                 technical_details、important_files、next_steps、created_at
session_files  — session_id、file_path、tool_name、turn_index、first_seen_at
session_refs   — session_id、ref_type（commit/pr/issue）、ref_value、turn_index、created_at
search_index   — FTS5 虚拟表（content、session_id、source_type、source_id）
```

### 源 3：VS Code 工作区存储（`<workspaceStorage>/<hash>/GitHub.copilot-chat/`）

VS Code 扩展数据，按工作区哈希键值对。路径平台特定，必须来自 `.env` 或用户输入。

```
<hash>/GitHub.copilot-chat/
├── transcripts/
│   └── <session-uuid>.jsonl     # 对话转录（与 events.jsonl 相同的 JSONL 格式）
├── memory-tool/
│   └── memories/
│       └── <base64-session-id>/ # 每个会话保存的工件（plan.md 等）
│           └── plan.md
└── codebase-external.sqlite     # 代码库索引（跳过——不含对话知识）
```

### 关键数据源按价值排序：

1. **检查点**（`session-store.db` `checkpoints` 表 + 每个会话的 `checkpoints/*.json`）—— 预提炼的摘要，包含 `overview`、`work_done`、`technical_details`、`important_files`、`next_steps`。黄金。
2. **会话摘要**（`session-store.db` `sessions.summary` + `index.md`）—— 每个会话的段落式概要。
3. **回合**（`session-store.db` `turns` 表 + `events.jsonl` / 转录 JSONL）—— 完整对话。丰富但冗长。
4. **记忆工件**（`memory-tool/memories/<id>/plan.md` 等）—— 用户明确保存的预写计划和结构化笔记。值得逐字导入（或轻度总结）。
5. **文件访问模式**（`session_files` 表 + `tool.execution_*` 事件）—— 代理反复接触的文件——揭示高价值项目文件。
6. **会话引用**（`session_refs` 表）—— 链接到会话的提交、PR 和问题。
7. **`vscode.metadata.json`** — 工作区文件夹路径、分支、`customTitle`（用户设置的会话标签）。用于分组和命名。

## 第 1 步：调查并计算差异

扫描所有三个数据位置，并与 `.manifest.json` 进行比较：

```bash
# --- 源 1：每个会话目录 ---
# 查找所有会话目录（每个目录都有 workspace.yaml）
ls ~/.copilot/session-state/

# 对于每个会话，读取 workspace.yaml 获取 id/cwd/updated_at
# 和 vscode.metadata.json 获取 customTitle / repositoryProperties

# --- 源 2：全局数据库 ---
# 使用 sqlite3（或 Python sqlite3）查询 session-store.db
SELECT s.id, s.cwd, s.repository, s.branch, s.summary, s.updated_at,
       COUNT(DISTINCT t.turn_index) AS turn_count,
       COUNT(DISTINCT c.id)         AS checkpoint_count
FROM sessions s
LEFT JOIN turns t ON t.session_id = s.id
LEFT JOIN checkpoints c ON c.session_id = s.id
GROUP BY s.id
ORDER BY s.updated_at DESC;

# --- 源 3：VS Code 工作区存储 ---
# 对于 workspaceStorage 下每个 <hash> 目录，检查 GitHub.copilot-chat/
# 查找转录文件
ls <workspaceStorage>/<hash>/GitHub.copilot-chat/transcripts/
```

构建统一清单——每个会话 UUID 一个条目——并进行分类：

- **新**—— 不在保险库中 → 需要导入
- **修改**—— 在保险库中但 `updated_at` 更新 → 需要重新导入
- **未修改**—— 在保险库中且未修改 → 追加模式下跳过

向用户报告："在 session-state 中找到 X 个会话，在 session-store.db 中找到 Y 个，在 VS Code 转录文件中找到 Z 个。检查点：A。差异：B 个新，C 个修改。"

## 第 2 步：首先导入检查点和摘要

检查点已预提炼——在接触原始回合之前处理它们。

### 从 `session-store.db`：

```sql
SELECT s.id, s.cwd, s.repository, s.branch, s.summary,
       c.checkpoint_number, c.title, c.overview, c.work_done,
       c.technical_details, c.important_files, c.next_steps,
       c.created_at
FROM checkpoints c
JOIN sessions s ON c.session_id = s.id
ORDER BY s.updated_at DESC, c.checkpoint_number ASC;
```

### 从每个会话的 `checkpoints/*.json`：

每个检查点文件包含：`title`、`overview`、`history`、`work_done`、`technical_details`、`important_files`、`next_steps`。

读取 `index.md`（如果存在）作为会话级摘要——它通常在会话结束时编写，并且已经简洁。

### 要提取的内容：

- `overview` → 会话完成的高层次描述
- `work_done` → 完成的具体任务（适合技能/项目页面）
- `technical_details` → 实现细节（适合概念页面）
- `important_files` → 项目中的高价值文件（适合项目页面）
- `next_steps` → 打开的线索（适合链接到正在进行的项目工作）

## 第 3 步：解析会话回合

从 `session-store.db`（首选——已解析）或从 `events.jsonl` / 转录 JSONL 读取回合。

### 从 `session-store.db`：

```sql
SELECT turn_index, user_message, assistant_response, timestamp
FROM turns
WHERE session_id = '<uuid>'
ORDER BY turn_index ASC;
```

### 从 `events.jsonl` / 转录 JSONL：

每个文件是一个会话。每行是一个 JSON 事件。有关完整架构，请参阅 `references/copilot-data-format.md`。

**相关事件类型：**

| `type`                | 它是什么                              | 值得读取？                            |
| --------------------- | --------------------------------------- | ----------------------------------------- |
| `session.start`       | 会话元数据（cwd、branch、version）     | 是——建立项目上下文                     |
| `user.message`        | 用户回合                               | 是——`data.content`                      |
| `assistant.message`   | 代理回合                              | 是——`data.content`（文本） + `data.toolRequests` |
| `tool.execution_start`| 工具调用                               | 浏览——揭示使用的文件/命令             |
| `tool.execution_end`  | 工具结果                             | 否——通常是噪音                        |

**`assistant.message` 的提取策略：**

- `data.content` 是代理的文本响应——提取这个
- `data.reasoningText` 是内部推理——跳过（它是解包的 `reasoningOpaque` 字段）
- `data.toolRequests` 列出工具调用——浏览工具名称和参数以查找文件访问模式
- 完全跳过 `type: "tool.execution_end"`

## 第 3b 步：处理记忆工件

对于 VS Code 工作区存储中 `memory-tool/memories/<base64-id>/` 目录的每个会话，读取其中保存的任何 Markdown 文件（通常为 `plan.md`）。这些是用户明确保存的文档——将它们视为高质量、用户创作的內容。

解码 base64 目录名称以获取会话 UUID：

```python
import base64
session_id = base64.b64decode(dir_name).decode('utf-8')
```

记忆工件映射到项目 `skills/` 或 `concepts/` 页面，具体取决于内容类型。

## 第 3c 步：提取文件和引用模式

从 `session-store.db`：

```sql
-- 每个项目最常接触的文件
SELECT repository, file_path, COUNT(*) AS touch_count
FROM session_files
GROUP BY repository, file_path
ORDER BY touch_count DESC;

-- 每个会话链接的提交/PR/问题
SELECT session_id, ref_type, ref_value, turn_index
FROM session_refs
ORDER BY session_id, turn_index;
```

**文件访问模式**揭示架构上重要的文件——在项目页面上记录它们。

**会话引用**将 Copilot 会话链接到 git 历史记录——这对于将知识库知识连接到具体的代码更改很有用。

## 第 4 步：按主题聚类

不要为每个会话创建一个知识库页面。相反：

- 跨会话按主题**分组**提取的知识
- 一个关于“调试认证 + 设置 CI”的会话 → 两个不同的主题
- 三天内在不同天关于“React 性能”的会话 → 一个合并的主题
- `cwd` / `repository` 提供自然的顶级分组；`vscode.metadata.json` 的 `customTitle` 提供人类可读的会话标签

## 第 5 步：提炼到知识库页面

每个 Copilot 项目映射到保险库中的一个项目目录。从 `cwd` 或 `repository` 推导项目名称：

```
C:\Users\name\git\my-project   → my-project
/Users/name/code/another-app   → another-app
```

当可用时，优先使用 `repository`（例如 `owner/repo`）来自 `session-store.db` 覆盖原始 `cwd`。

### 项目特定与全局知识

| 您找到的内容                      | 放在哪里               | 示例                                              |
| ----------------------------------- | --------------------------- | ---------------------------------------------------- |
| 项目架构决策      | `projects/<name>/concepts/` | `projects/my-project/concepts/main-architecture.md`  |
| 项目特定调试模式 | `projects/<name>/skills/`   | `projects/my-project/skills/api-rate-limiting.md`    |
| 用户学习的通用概念    | `concepts/`（全局）        | `concepts/react-server-components.md`                |
| 跨项目重复的问题   | `skills/`（全局）          | `skills/debugging-hydration-errors.md`               |
| 使用的工具/服务    | `entities/`（全局）        | `entities/vercel-functions.md`                       |
| 跨许多会话的模式   | `synthesis/`（全局）       | `synthesis/common-debugging-patterns.md`             |

对于每个有内容的**项目**，创建或更新项目概述页面在 `projects/<name>/<name>.md`——**以项目名称命名，而不是 `_project.md`**。Obsidian 的图视图使用文件名作为节点标签，所以 `_project.md` 使每个项目在图中显示为 `_project`。命名为 `<name>.md` 可以为每个项目提供一个独特的、可读的节点名称。

**重要**：提炼知识，而不是对话。不要写“在 3 月 15 日的会话中，用户询问了 X。” 写知识本身，会话作为来源归因。

**为每个新/更新的页面编写 `summary:` 前置字段**——1-2 句话，≤200 字符，回答“这个页面是关于什么的？”对于未打开页面的读者。`wiki-query` 的廉价检索路径读取此字段以避免打开页面正文。

**为每个新页面添加** `base_confidence` 和 `lifecycle` 字段**到前置字段**：
```yaml
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: <ISO 日期今天>
```
更新时保持 `lifecycle` 不变。

**按 `llm-wiki` 中的约定（Provenance Markers 部分）标记来源**：

- **检查点和 index.md** 由系统预提炼——将检查点派生的声明视为提取（系统根据观察到的行为编写它们）。
- **记忆工件**是用户创作的——视为提取。
- **对话回合提炼**主要是推断的。您正在从许多回合中合成一个连贯的声明。对合成的模式、跨会话的概括以及“用户真正意图”的解释应用 `^[inferred]` 很大方。
- 当用户在会话中途改变方向或会话结束时未解决时，使用 `^[ambiguous]`。
- 在每个新/更新的页面编写 `provenance:` 前置字段，总结大致混合。

## 第 6 步：更新保险库、日记和特殊文件

### 更新 `.manifest.json`

对于每个处理的会话，添加/更新其条目，包含：

- `ingested_at`、`session_id`、`updated_at`
- `source_type`：`"copilot_session"`、`"copilot_checkpoint"`、`"copilot_transcript"`、`"copilot_memory_artifact"` 之一
- `project`：解码的项目名称
- `pages_created` 和 `pages_updated` 列表

同时更新保险库的 `projects` 部分：

```json
{
  "project-name": {
    "repository": "owner/repo",
    "cwd": "C:\\Users\\name\\git\\project-name",
    "vault_path": "projects/project-name",
    "last_ingested": "TIMESTAMP",
    "sessions_ingested": 5,
    "sessions_total": 8,
    "checkpoints_ingested": 12,
    "memory_artifacts_ingested": 3
  }
}
```

### 创建日记条目 + 更新特殊文件

使用一个锁定调用更新 `index.md`、`log.md` 和 `hot.md`：

```bash
obsidian-wiki memory sync COPILOT_HISTORY_INGEST \
  projects=<projects> sessions=<sessions> checkpoints=<checkpoints> \
  pages_updated=<pages_updated> pages_created=<pages_created> \
  mode=<mode> \
  --takeaways "导入 5 个 Copilot 会话，跨越 2 个项目；在 API 设计和测试策略中发现了模式。"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md`——命令获取的锁防止并行写入者覆盖您的更新。`--takeaways` 是以前放在 Recent Activity 中的概念摘要；省略它以保留先前的 takeaways。

如果正在进行的项目现在理解得更好，记录该线索以便下一个会话接手：`obsidian-wiki memory todo add "<thread>" --origin projects/<name>.md`。

有关完整过程，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 隐私

- 提炼和合成——不要逐字复制原始对话文本
- 跳过看起来像秘密、API 密钥、密码、令牌的内容
- `data.reasoningOpaque` / `data.reasoningText` 在代理事件中是内部推理——完全跳过，永远不要复制到知识库
- 如果您遇到个人/敏感内容，请在包含之前询问用户
- 用户的对话可能引用其他人——在知识库中要谨慎

## 参考

有关详细数据结构文档，请参阅 `references/copilot-data-format.md`。

## QMD 在保险库写入后刷新

QMD 是一个搜索索引，不是真相。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在**此技能写入或重写保险库 Markdown** 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出说需要向量或嵌入可能过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录其中一个：

- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
