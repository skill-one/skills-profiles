---
name: claude-history-ingest
description: 将Claude代码对话历史导入Obsidian维基。当用户希望挖掘过去的Claude对话以获取知识、导入其 ~/.claude 文件夹、从之前的编程会话中提取见解，或说出类似“处理我的Claude历史”、“将我的对话添加到维基”、“我之前和Claude讨论了什么”等话时，使用此技能。此外，当用户提及其 .claude 文件夹、Claude项目、会话数据、过去的对话记录、本地代理模式会话或审计日志时，也会触发此技能。
---

# Claude 历史数据导入 — 对话挖掘

你正在从用户过去的 Claude Code 对话中提取知识，并将其提炼到 Obsidian 知识库中。对话内容丰富但杂乱——你的工作是找到信号并将其编译。

此技能可以直接调用，或通过 `wiki-history-ingest` 路由器（`/wiki-history-ingest claude`）调用。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。

`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `CLAUDE_HISTORY_PATH`（默认为 `~/.claude`）
2. 在保险库根目录下读取 `.manifest.json` 以检查已导入的内容
3. 在保险库根目录下读取 `index.md` 以了解知识库已包含的内容
4. **项目范围** — 从配置中读取 `WIKI_SKIP_PROJECTS`（逗号分隔的子字符串）。从以下每个步骤中排除任何包含其中之一的目录项目（扫描、差异、采样、manifest 写入）。如果用户指定要跳过此运行的额外项目，请添加它们。应用排除 **一次，统一** — 不要在单独命令中手动编写 `grep -v` 过滤器，这会导致扫描和 manifest 步骤之间漂移。

## 导入模式

### 追加模式（默认）

检查每个源文件（对话 JSONL、内存文件）的 `.manifest.json`。仅处理：

- 不在 manifest 中的文件（新对话、新内存文件、新项目）
- 修改时间比 manifest 中的 `ingested_at` 更新的文件

这通常是您想要的结果——用户运行了一些新会话，并希望捕获差异。

> **比较时的便携密钥。** Manifest 密钥遵循 `llm-wiki/SKILL.md` 中源密钥合同（v2）→ `.manifest.json`。`$HOME` 下方的会话以 `~` 相对键（`~/.claude/projects/.../abc.jsonl`）键入，永远不会以展开的机器路径键入；保险库相对键和伪键是其他两种形式。在确定文件是“新”之前，以与工具相同的方式解决存储键（展开 `~`/环境变量，相对于保险库根目录解析 manifest 相对路径）——否则已跟踪的文件看起来是新的，并会被重新导入。`scripts/manifest.py` 辅助工具会为您执行此操作：
>
> ```bash
> # 新/修改的源，尊重 WIKI_SKIP_PROJECTS + --skip:
> python3 "$OBSIDIAN_WIKI_REPO/scripts/manifest.py" delta "$OBSIDIAN_VAULT_PATH" \
>   --scan "$CLAUDE_HISTORY_PATH/projects/*/memory/*.md"
> # 如果 manifest 仍然包含遗留绝对键，则一次性修复：
> python3 "$OBSIDIAN_WIKI_REPO/scripts/manifest.py" migrate "$OBSIDIAN_VAULT_PATH" --dry-run
> ```
>
> 辅助工具是可选的——如果它不可用，请在每次 manifest 查找和写入之前内联应用相同的解析。

### 提取前（推荐——在导入前运行）

原始 JSONL 文件有 80-90% 的噪音：`tool_use` 块、`thinking` 块、`progress` 事件和 `file-history-snapshot` 条目按字节计数占主导地位。`scripts/extract-jsonl.py` 辅助工具会剥离所有这些内容，并将紧凑的信号 JSON 写入 `~/.claude/extracted/`，实现 **50–200× 的文件大小减少**（例如 12 MB JSONL → 64 KB 提取）。这使技能能够在相同的 token 预算内每次运行读取 5–10 倍更多的对话。

将其作为运行此技能的预步骤运行：

```bash
# 第一次运行——提取所有内容（跳过排除的项目）
python3 "$OBSIDIAN_WIKI_REPO/scripts/extract-jsonl.py" --skip tsg,autom8

# 增量——仅提取最近一天内修改的会话
python3 "$OBSIDIAN_WIKI_REPO/scripts/extract-jsonl.py" \
    --since "$(date -v-1d +%Y-%m-%d)" --skip tsg,autom8
```

提取文件位于 `~/.claude/extracted/<project-dir>/<session-id>.json`，并包含：

```json
{
  "session_id": "uuid",
  "project": "-Users-name-myapp",
  "cwd": "/Users/name/myapp",
  "start_ts": "...",
  "end_ts": "...",
  "n_turns": 18,
  "n_user_words": 620,
  "turns": [
    {"role": "user",      "text": "..."},
    {"role": "assistant", "text": "..."}
  ]
}
```

**在步骤 3 读取对话时，始终优先选择提取文件而不是原始 JSONL。**（见步骤 3。）

如果未首先运行 `extract-jsonl.py`，则回退到原始 JSONL——但请注意，覆盖范围将更浅，因为每个原始文件的成本远高于读取 token。

### 对话采样启发式算法

一个历史路径可以包含数百个对话 JSONL 文件——不要尝试读取所有文件。每个项目：

- **如果该项目已有内存文件**（`memory/*.md`），则首先导入这些文件（它们是预先提炼的信号），然后 **还处理尚未在 manifest 中的对话**——即使对于内存丰富的项目，也应该捕获新对话。
- **如果该项目没有内存文件**，则仅读取 **3 个最 recent** 的对话（按 mtime）来描述它。优先选择预提取文件（见上文）——它们足够便宜，以至于您可以在相同的 token 预算内读取 5–10 个原始 JSONL。
- 始终报告您采样的内容与跳过的内容（例如 "agenttower: 7 个内存文件 + 4 个新对话导入，14 个未更改的对话跳过"），以便覆盖差距是可见的而不是沉默的。

### 全部模式

无论 manifest 如何，都会处理所有内容。在 `wiki-rebuild` 后或用户明确要求时使用。

## Claude Code 数据布局

Claude Code 将数据存储在两个位置。扫描 **两者**。

### 源 1：`~/.claude/`（CLI 会话）

```
~/.claude/
├── projects/                          # 每个项目目录
│   ├── -Users-name-project-a/         # 路径派生的名称（斜杠 → 短横线）
│   │   ├── <session-uuid>.jsonl       # 对话数据（JSONL）
│   │   └── memory/                    # 结构化记忆
│   │       ├── MEMORY.md              # 记忆索引
│   │       ├── user_*.md              # 用户配置文件记忆
│   │       ├── feedback_*.md          # 工作流反馈记忆
│   │       └── project_*.md           # 项目上下文记忆
│   ├── -Users-name-project-b/
│   │   └── ...
├── sessions/                          # 会话元数据（JSON）
│   └── <pid>.json                     # {pid, sessionId, cwd, startedAt, kind, entrypoint}
├── history.jsonl                      # 全局会话历史
├── tasks/                             # 子代理任务数据
├── plans/                             # 保存的计划
└── settings.json
```

### 源 2：`~/Library/Application Support/Claude/local-agent-mode-sessions/`（桌面应用程序代理会话）

> **首先检查。** 许多用户仅使用 CLI 且没有桌面会话。在遍历以下结构之前，请确认它非空：
> ```bash
> DESKTOP_SESSIONS="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"
> [ -d "$DESKTOP_SESSIONS" ] && find "$DESKTOP_SESSIONS" -name "audit.jsonl" | head -1
> ```
> 如果输出为空，则跳过此整个部分（源 2 + 步骤 3b）并且不要描述它。

Claude 桌面应用程序在此处存储本地代理模式会话。结构深度嵌套：

```
~/Library/Application Support/Claude/local-agent-mode-sessions/
└── <outer-uuid>/
    └── <inner-uuid>/
        ├── local_<session-uuid>.json          # 会话元数据
        └── local_<session-uuid>/
            ├── audit.jsonl                    # 审计日志 — 工具调用、文件读取、命令运行
            └── .claude/
                └── projects/
                    └── <path-encoded-name>/   # 与 ~/.claude/projects/ 相同的路径编码
                        └── <uuid>.jsonl       # 对话记录（与 CLI 相同的 JSONL 格式）
```

**如何查找所有本地代理模式会话：**

```bash
# 查找所有会话元数据文件
find "$DESKTOP_SESSIONS" -name "local_*.json" -maxdepth 4

# 查找所有审计日志
find "$DESKTOP_SESSIONS" -name "audit.jsonl"

# 查找所有对话记录
find "$DESKTOP_SESSIONS" -name "*.jsonl" -path "*/.claude/projects/*"
```

**会话元数据（`local_<uuid>.json`）** — 包含 `sessionId`、`cwd`、`startedAt`、`model`、`title` 等字段的 JSON 文件。在打开记录之前，先读取此文件以了解会话上下文。

**审计日志（`audit.jsonl`）** — 每行是一个 JSON 记录，记录代理的一个操作：工具调用（Read、Write、Bash、Edit）、文件访问、执行的 shell 命令、MCP 调用。用于了解代理实际做了什么——通常比对话文本本身包含更多信号。字段：`type`、`toolName`、`input`、`output`、`timestamp`、`sessionId`。

**对话记录（`.claude/projects/.../<uuid>.jsonl`）** — 与 CLI 对话 JSONL 格式相同。与 `~/.claude/projects/*/*.jsonl` 以相同方式解析。

### 按价值排序的关键数据源（两个位置合并）：

1. **内存文件**（`~/.claude/projects/*/memory/*.md`）— 预提炼，已为知识库友好。黄金。
2. **对话 JSONL**（`~/.claude/projects/*/*.jsonl` 和桌面应用程序记录）— 完整对话记录。丰富但嘈杂。
3. **审计日志**（桌面会话中的 `audit.jsonl`）— 工具调用级别的记录，记录了做了什么。即使对话稀疏，也很有用，可以提取具体操作、文件模式、命令模式。
4. **会话元数据**（`sessions/*.json` 和 `local_*.json`）— 告诉您哪个项目、何时以及哪个 CWD。

## 步骤 1：调查并计算差异

扫描两个数据位置并与 `.manifest.json` 进行比较：

```bash
# --- 源 1：CLI 会话 (~/.claude) ---
# 查找所有项目
Glob: ~/.claude/projects/*/

# 查找内存文件（最高价值）
Glob: ~/.claude/projects/*/memory/*.md

# 查找对话 JSONL 文件
Glob: ~/.claude/projects/*/*.jsonl

# --- 源 2：桌面应用程序本地代理模式会话 ---
DESKTOP_SESSIONS="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"

# 会话元数据
find "$DESKTOP_SESSIONS" -name "local_*.json" -maxdepth 4

# 审计日志
find "$DESKTOP_SESSIONS" -name "audit.jsonl"

# 对话记录
find "$DESKTOP_SESSIONS" -name "*.jsonl" -path "*/.claude/projects/*"
```

构建统一清单并分类每个文件：

- **新** — 不在 manifest 中 → 需要导入
- **修改** — 在 manifest 中但文件更新 → 需要重新导入
- **未更改** — 在 manifest 中且未修改 → 追加模式下跳过

向用户报告："找到 X 个 CLI 项目，Y 个桌面会话。内存文件：A。对话：B。审计日志：C。差异：D 新，E 修改。"

## 步骤 2：首先导入内存文件

内存文件已使用 YAML 前置符结构化：

```markdown
---
name: memory-name
description: 一行描述
type: user|feedback|project|reference
---

此处为记忆内容。
```

对于每个内存文件：

- 读取它并解析前置符
- `user` 类型 → 输入到关于用户的实体页面，或关于其领域的概念页面
- `feedback` 类型 → 输入到技能页面（工作流模式、什么有效、什么无效）
- `project` 类型 → 输入到项目实体页面
- `reference` 类型 → 输入到指向外部资源的参考页面

每个项目中的 `MEMORY.md` 索引文件是一个快速摘要——首先读取它，以决定是否要完整读取单个内存文件。

## 步骤 3：解析对话 JSONL

**始终先检查是否有预提取文件**（见上文提取部分）。对于每个对话 `~/.claude/projects/<proj>/<uuid>.jsonl`，查找其对应文件 `~/.claude/extracted/<proj>/<uuid>.json`。如果找到，则读取该文件——它已经过滤为用户 + 助手文本回合，并且比原始 JSONL 成本 50–200× 更少。

```
# 每个会话的解析顺序：
1. ~/.claude/extracted/<project>/<session-id>.json   ← 优先（紧凑，仅信号）
2. ~/.claude/projects/<project>/<session-id>.jsonl   ← 回退（原始，嘈杂）
```

**读取预提取文件：** 它已经只包含您需要的回合。直接迭代 `turns[].{role, text}`。顶层字段（`cwd`、`start_ts`、`n_user_words` 等）无需进一步解析即可提供项目上下文。

**读取原始 JSONL（回退）：** 每行是一个 JSON 对象：

```json
{
  "type": "user|assistant|progress|file-history-snapshot",
  "message": {
    "role": "user|assistant",
    "content": "文本字符串"
  },
  "uuid": "...",
  "timestamp": "2026-03-15T10:30:00.000Z",
  "sessionId": "...",
  "cwd": "/path/to/project",
  "version": "2.1.59"
}
```

对于助手消息，`content` 可能是一个内容块数组：

```json
{
  "content": [
    {"type": "thinking", "text": "..."},
    {"type": "text", "text": "实际响应..."},
    {"type": "tool_use", "name": "Read", "input": {...}}
  ]
}
```

- 过滤 `type: "user"` 和 `type: "assistant"` 条目
- 对于助手条目，提取 `text` 块（跳过 `thinking` 和 `tool_use` —— 这些是噪音）
- `cwd` 字段告诉您此对话属于哪个项目
- 跳过 `type: "progress"` — 内部代理进度更新
- 跳过 `type: "file-history-snapshot"` — 文件状态跟踪
- 跳过子代理对话（在 `subagents/` 子目录下）——除非用户要求

## 步骤 3b：解析审计日志（仅桌面会话）

对于在 `local-agent-mode-sessions/` 下找到的每个 `audit.jsonl`，逐行读取。每行是一个代理操作的 JSON 记录：

```json
{
  "type": "tool_call",
  "toolName": "Bash",
  "input": {"command": "npm test"},
  "output": "...",
  "timestamp": "2026-04-10T14:22:00Z",
  "sessionId": "..."
}
```

**从审计日志中提取的内容：**

- **文件访问模式** — 代理反复读取或编辑哪些文件？这些是项目中的高价值文件。将它们作为项目参考记录下来。
- **Shell 命令** — 反复出现的 Bash 命令揭示了项目的构建/测试/部署工作流。将这些提炼到 `skills/` 页面（例如 "如何构建和测试此项目"）。
- **工具调用序列** — 如果代理按特定顺序始终执行 Read → Edit → Bash，那么这是一个值得捕获的工作流模式。
- **错误模式** — 失败的工具调用（非零退出代码、错误输出）揭示了痛点、已知粗糙边缘或重复出现的错误。
- **MCP 工具调用** — 对 MCP 工具的调用揭示了项目集成了哪些外部服务和 API。

**从审计日志中跳过：**

- 没有模式的常规文件读取（例如，读取配置文件一次）
- 工具输出只是噪音（长堆栈跟踪、详细日志）——总结错误类别，而不是完整输出
- 看起来像密钥、令牌或凭证的命令参数或输出中的任何内容

**与对话记录交叉引用：** 审计日志告诉您 *发生了什么*；对话告诉您 *为什么*。当两者都可用于同一会话时，请将它们一起使用——审计日志使对话具体化。

在处理审计日志之前，先读取配对的 `local_<uuid>.json` 会话元数据——它提供了 `cwd`、`startedAt` 和 `title`，以提供上下文。

## 步骤 4：按主题聚类

不要为每个对话创建一个知识库页面。相反：

- 跨对话按主题分组提取的知识
- 一个关于 "调试 auth + 设置 CI" 的对话 → 两个单独的主题
- 三天内在不同天关于 "React 性能" 的对话 → 一个合并的主题
- 项目目录名称提供了自然的顶级分组

### 项目特定知识 vs. 全局知识

| 你发现的内容                     | 存放位置               | 示例                                             |
| ---------------------------------- | --------------------------- | --------------------------------------------------- |
| 项目架构决策                     | `projects/<name>/concepts/` | `projects/my-project/concepts/main-architecture.md` |
| 项目特定调试                     | `projects/<name>/skills/`   | `projects/my-project/skills/api-rate-limiting.md`   |
| 用户学习到的通用概念             | `concepts/` (全局)        | `concepts/react-server-components.md`               |
| 跨多个项目的常见问题             | `skills/` (全局)          | `skills/debugging-hydration-errors.md`              |
| 使用的工具/服务                 | `entities/` (全局)        | `entities/vercel-functions.md`                      |
| 多个对话中的模式                 | `synthesis/` (全局)       | `synthesis/common-debugging-patterns.md`            |

对于每个有内容的**项目**，创建或更新项目概述页面，位于 `projects/<name>/<name>.md` — **以项目名称命名，而不是 `_project.md`**。Obsidian的图视图使用文件名作为节点标签，所以 `_project.md` 会使每个项目在图中显示为 `_project`。命名为 `<name>.md` 可以为每个项目提供一个独特、可读的节点名称。

**重要提示**：提炼**知识**，而不是对话。不要写“在3月15日的对话中，用户询问了X。”直接写知识本身，将对话作为来源归属。

**为每个新/更新的页面编写 `summary:` 前置字段** — 1-2句话，≤200字符，回答“这个页面是关于什么的？”对于未打开页面的读者。`wiki-query` 的廉价检索路径读取此字段以避免打开页面正文。

**为每个新页面的前置字段添加信心和生命周期字段**：
```yaml
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: <ISO 日期今天>
```
更新时，保持 `lifecycle` 和 `lifecycle_changed` 不变 — 只有人类编辑器会转换生命周期状态。

**按照 `llm-wiki` 中的约定（来源标记部分）标记来源**：

- **记忆文件** 大部分是提取的 — 用户手动编写，并且已经提炼。将记忆派生的声明视为提取的，除非你正在将来自多个记忆文件的声明拼接在一起。
- **对话提炼** 大部分是推断的。你正在从许多对话回合中综合出一个连贯的声明，通常填补隐含的推理。对综合的模式、跨会话的概括以及“用户真正想表达的意思”的解释，广泛使用 `^[inferred]`。
- 当用户跨会话改变主意，或者助手和用户相互矛盾且解决方案不明确时，使用 `^[ambiguous]`。
- 在每个新/更新的页面上编写 `provenance:` 前置字段，总结大致的混合。

## 第 6 步：更新清单、日志和特殊文件

### 更新 `.manifest.json`

对于每个处理的源文件，添加/更新其条目，包括：

- `ingested_at`, `size_bytes`, `modified_at`
- `source_type`: `"claude_conversation"`, `"claude_memory"`, `"claude_audit_log"`, `"claude_desktop_session"` 之一
- `project`: 解码的项目名称
- `pages_created` 和 `pages_updated` 列表

同时更新清单的 `projects` 部分：

```json
{
  "project-name": {
    "source_path": "~/.claude/projects/-Users-...",
    "vault_path": "projects/project-name",
    "last_ingested": "TIMESTAMP",
    "conversations_ingested": 5,
    "conversations_total": 8,
    "memory_files_ingested": 3,
    "desktop_sessions_ingested": 2,
    "audit_logs_ingested": 2
  }
}
```

### 创建日志条目 + 更新特殊文件

使用一个锁定调用更新 `index.md`, `log.md`, 和 `hot.md`：

```bash
obsidian-wiki memory sync CLAUDE_HISTORY_INGEST \
  projects=<projects> conversations=<conversations> \
  desktop_sessions=<desktop_sessions> audit_logs=<audit_logs> \
  pages_updated=<pages_updated> pages_created=<pages_created> \
  mode=<mode> \
  --takeaways "已导入 5 个 Claude 对话，涉及 2 个项目；在 API 设计和测试策略中发现了模式。"
```

永远不要手动编辑 `index.md`, `log.md`, 或 `hot.md` — 命令会获取锁，防止并行写入者覆盖你的更新。`--takeaways` 是过去放在最近活动中的单行概念性摘要；省略它以保留先前的摘要。

如果某个正在进行的项目现在理解得更清晰，记录该线程，以便下次会话继续：`obsidian-wiki memory todo add "<thread>" --origin projects/<name>.md`。

有关完整步骤，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 隐私

- 提炼和综合 — 不要逐字复制原始对话文本
- 跳过任何看起来像秘密、API 密钥、密码、令牌的内容
- 如果你遇到个人/敏感内容，请在包含之前询问用户
- 用户的对话可能引用其他人 — 在 wiki 中添加内容时要谨慎

## 参考

有关数据结构的更多详细信息，请参阅 `references/claude-data-format.md`。

## QMD 在 Vault 写入后刷新

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写 Vault Markdown 后运行它。如果 QMD 刷新失败，不要回滚 Vault 更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，则使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方式验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或者，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：

- `QMD refreshed: update + embed + verified`
- `QMD refreshed: update only + verified`
- `QMD skipped: QMD_WIKI_COLLECTION unset`
- `QMD skipped: qmd CLI unavailable`
- `QMD failed: <简短错误摘要>`
