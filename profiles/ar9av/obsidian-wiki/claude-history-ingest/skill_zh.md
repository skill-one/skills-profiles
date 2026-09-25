# Claude History Ingest — 对话挖掘

你正在从用户的过去 Claude Code 对话中提取知识，并将其提炼到 Obsidian 知识库中。对话内容丰富但杂乱——你的工作是找到信号并将其编译。

此技能可以直接调用，或通过 `wiki-history-ingest` 路由器 (`/wiki-history-ingest claude`) 调用。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `CLAUDE_HISTORY_PATH`（默认为 `~/.claude`）
2. 读取知识库根目录下的 `.manifest.json`，检查已导入的内容
3. 读取知识库根目录下的 `index.md`，了解知识库已包含的内容
4. **项目范围** — 从配置中读取 `WIKI_SKIP_PROJECTS`（逗号分隔的子字符串）。从**每个**以下步骤中排除任何名称包含其中之一的任何项目目录（扫描、差异、采样、manifest 写入）。如果用户为本次运行指定要跳过的额外项目，请添加它们。应用排除**一次，统一地**——不要将 `grep -v` 过滤器手动写入单个命令中，这会在扫描和 manifest 步骤之间漂移。

## 导入模式

### 追加模式（默认）

检查每个源文件（对话 JSONL、内存文件）的 `.manifest.json`。仅处理：

- 未在 manifest 中出现的文件（新对话、新内存文件、新项目）
- 修改时间比 manifest 中的 `ingested_at` 更新的文件

这通常是您想要的结果——用户运行了一些新会话，并希望捕获差异。

> **比较时的便携密钥。** Manifest 密钥遵循 `llm-wiki/SKILL.md` 中源密钥合同（v2）→ `.manifest.json`。`$HOME` 下方的会话以 `~` 相对键值（`~/.claude/projects/.../abc.jsonl`），永远不会以展开的机器路径为键；知识库相对路径和伪键是其他两种形式。在确定文件为“新”之前，以工具的方式解决存储键（展开 `~`/环境变量，相对于知识库根解决知识库相对路径）——否则已跟踪的文件看起来是新的，并会被重新导入。`scripts/manifest.py` 辅助工具会为您执行此操作：
>
> ```bash
> # 新/修改的源，尊重 WIKI_SKIP_PROJECTS + --skip:
> python3 "$OBSIDIAN_WIKI_REPO/scripts/manifest.py" delta "$OBSIDIAN_VAULT_PATH" \
>   --scan "$CLAUDE_HISTORY_PATH/projects/*/memory/*.md"
> # 如果 manifest 仍然保留遗留绝对键，则进行一次性修复：
> python3 "$OBSIDIAN_WIKI_REPO/scripts/manifest.py" migrate "$OBSIDIAN_VAULT_PATH" --dry-run
> ```
>
> 辅助工具是可选的——如果它不可用，请在每次 manifest 查找和写入之前内联应用相同的解决方案。

### 提取前（推荐——在导入前运行）

原始 JSONL 文件有 80-90% 的噪音：`tool_use` 块、`thinking` 块、`progress` 事件和
`file-history-snapshot` 条目按字节计数主导。`scripts/extract-jsonl.py` 辅助工具会剥离所有这些内容，并将紧凑的信号仅 JSON 写入 `~/.claude/extracted/`，实现 **50–200× 文件大小减少**（例如 12 MB JSONL → 64 KB 提取）。这允许该技能在相同的 token 预算内每次运行读取 5–10 倍更多的对话。

将其作为调用此技能前的预步骤运行：

```bash
# 首次运行——提取所有内容（跳过排除的项目）
python3 "$OBSIDIAN_WIKI_REPO/scripts/extract-jsonl.py" --skip tsg,autom8

# 增量——仅修改的最后一天内的会话
python3 "$OBSIDIAN_WIKI_REPO/scripts/extract-jsonl.py" \
    --since "$(date -v-1d +%Y-%m-%d)" --skip tsg,autom8
```

提取文件位于 `~/.claude/extracted/<项目目录>/<会话 ID>.json`，并包含：

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

**读取对话时，始终优先选择提取文件而不是原始 JSONL。**（见步骤 3。）

如果未首先运行 `extract-jsonl.py`，则回退到原始 JSONL——但请注意，覆盖范围将更浅，因为每个原始文件都需要花费更多的 token 来读取。

### 对话采样启发式算法

一个历史路径可以包含数百个对话 JSONL——不要尝试读取所有内容。每个项目：

- **如果项目已经具有内存文件** (`memory/*.md`)，则首先导入这些文件（它们是预先提炼的信号），然后**还处理尚未在 manifest 中的对话**——即使对于内存丰富的项目，也应该捕获新对话。
- **如果项目没有内存文件**，则仅读取**3 个最新**的对话（按 mtime）来描述它。优先选择预提取文件（见上文）——它们足够便宜，以至于您可以在相同的 token 预算内读取 5–10 个原始 JSONL。
- 始终报告您采样的内容与跳过的内容（例如，"agenttower: 7 个内存文件 + 4 个新对话导入，14 个未更改的对话跳过"），以便覆盖差距是可见的而不是沉默的。

### 完整模式

无论 manifest 如何，处理所有内容。在 `wiki-rebuild` 之后或如果用户明确要求时使用。

## Claude Code 数据布局

Claude Code 将数据存储在两个位置。扫描**两者**。

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

> **首先检查。** 许多用户仅使用 CLI，没有桌面会话。在遍历以下结构之前，确认它是非空的：
> ```bash
> DESKTOP_SESSIONS="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"
> [ -d "$DESKTOP_SESSIONS" ] && find "$DESKTOP_SESSIONS" -name "audit.jsonl" | head -1
> ```
> 如果它打印为空，请跳过整个部分（源 2 + 步骤 3b）并不要叙述它。

Claude 桌面应用程序在此处存储本地代理模式会话。结构深度嵌套：

```
~/Library/Application Support/Claude/local-agent-mode-sessions/
└── <outer-uuid>/
    └── <inner-uuid>/
        ├── local_<session-uuid>.json          # 会话元数据
        └── local_<session-uuid>/
            ├── audit.jsonl                    # 审计日志 — 工具调用，文件读取，命令运行
            └── .claude/
                └── projects/
                    └── <path-encoded-name>/   # 与 ~/.claude/projects/ 相同的路径编码
                        └── <uuid>.jsonl       # 对话转录（相同的 JSONL 格式与 CLI）
```

**如何找到所有本地代理模式会话：**

```bash
# 找到所有会话元数据文件
find ~/Library/Application\ Support/Claude/local-agent-mode-sessions -name "local_*.json" -maxdepth 4

# 找到所有审计日志
find ~/Library/Application\ Support/Claude/local-agent-mode-sessions -name "audit.jsonl"

# 找到所有对话转录
find ~/Library/Application\ Support/Claude/local-agent-mode-sessions -name "*.jsonl" -path "*/.claude/projects/*"
```

**会话元数据 (`local_<uuid>.json`)** — JSON 文件，包含 `sessionId`、`cwd`、`startedAt`、`model`、`title` 等字段。在打开转录之前，先读取它以了解会话上下文。

**审计日志 (`audit.jsonl`)** — 每一行都是一个 JSON 记录，记录代理的一个操作：

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

- **文件访问模式** — 代理反复读取或编辑哪些文件？这些是项目中的高价值文件。将它们作为项目参考进行记录。
- **Shell 命令** — 反复出现的 Bash 命令揭示了项目的构建/测试/部署工作流。将这些提炼成一个 `skills/` 页面（例如，“这个项目是如何构建和测试的”）。
- **工具调用序列** — 如果代理以特定顺序始终执行 Read → Edit → Bash，那是一个值得捕获的工作流模式。
- **错误模式** — 失败的工具调用（非零退出代码，错误输出）揭示了痛点、已知粗糙边缘或重复出现的错误。
- **MCP 工具调用** — 对 MCP 工具的调用揭示了项目集成了哪些外部服务和 API。

**从审计日志中跳过：**

- 没有模式的常规文件读取（例如，读取配置文件一次）
- 工具输出只是噪音（长堆栈跟踪，冗长日志）——总结错误类别，而不是完整输出
- 命令参数或输出中看起来像密钥、令牌或凭证的任何内容

**与对话转录交叉引用：** 审计日志告诉您*发生了什么*；对话告诉您*为什么*。当两者都可用于同一会话时，请将它们一起使用——审计日志使对话具体化在实际行动中。

在处理审计日志之前，先读取配对的 `local_<uuid>.json` 会话元数据——它提供了 `cwd`、`startedAt` 和 `title`，以 contextualize 行动。

## 步骤 4：按主题聚类

不要为每个对话创建一个知识库页面。相反：

- 跨对话按主题分组提取的知识
- 一个关于“调试身份验证 + 设置 CI”的对话 → 两个单独的主题
- 三天内在不同天关于“React 性能”的对话 → 一个合并的主题
- 项目目录名称为您提供了自然的顶级分组

## 步骤 5：提炼到知识库页面

每个 Claude 项目都映射到知识库中的一个项目目录。从 `~/.claude/projects/` 获取的项目目录名称编码了原始路径——解码它以获得干净的 项目名称：

```
-Users/Documents/projects/my-Project   → myproject
-Users/Documents/projects/Another-app  → anotherapp
```

### 项目特定知识与全局知识

| 您找到的内容                     | 存放位置               | 示例                                             |
| ---------------------------------- | --------------------------- | --------------------------------------------------- |
| 项目架构决策     | `projects/<name>/concepts/` | `projects/my-project/concepts/main-architecture.md` |
| 项目特定调试         | `projects/<name>/skills/`   | `projects/my-project/skills/api-rate-limiting.md`   |
| 用户学习的一般概念   | `concepts/` (全局)        | `concepts/react-server-components.md`               |
| 跨项目出现的重复问题  | `skills/` (全局)          | `skills/debugging-hydration-errors.md`              |
| 使用的工具/服务                | `entities/` (全局)        | `entities/vercel-functions.md`                      |
| 跨许多对话的模式 | `synthesis/` (全局)       | `synthesis/common-debugging-patterns.md`            |

对于每个包含内容的项目，创建或更新项目概述页面 `projects/<name>/<name>.md`——**以项目名称命名，而不是 `_project.md`**。Obsidian 的图视图使用文件名作为节点标签，所以 `_project.md` 使每个项目在图中显示为 `_project`。将其命名为 `<name>.md` 可以为每个项目提供一个独特的、可读的节点名称。

**重要：** 提炼知识，而不是对话。不要写“在 3 月 15 日的对话中，用户询问了 X。” 写知识本身，对话作为来源归因。

**在每页上写一个 `summary:` 前置字段**——1–2 句话，≤200 字符，回答“这个页面是关于什么的？”对于没有打开它的读者。`wiki-query` 的廉价检索路径读取此字段以避免打开页面正文。

**为每个新/更新的页面添加置信度和生命周期字段**到前置字段：
```yaml
base_confidence: 0.42
lifecycle: draft
lifecycle_changed: <ISO 日期今天>
```
更新时，保留 `lifecycle` 和 `lifecycle_changed` 不变——只有人类编辑器会转换生命周期状态。

**按 `llm-wiki` 中的约定（Provenance Markers 部分）标记来源：**

- **内存文件** 大部分是提取的——用户手动编写它们，并且它们已经被提炼。将内存派生的声明视为提取的，除非您正在将来自多个内存文件的声明拼接在一起。
- **对话提炼** 主要是指定的。您正在从许多对话回合中合成一个连贯的声明，通常填充隐含的推理。在合成模式、跨会话的一般化以及“用户真正想要什么”的解释上应用 `^[inferred]` 很自由。
- 当用户在会话中改变主意或当助手和用户相互矛盾且解决方案不明确时，使用 `^[ambiguous]`。
- 在每个新/更新的页面上写一个 `provenance:` 前置块，总结大致混合。

## 步骤 6：更新 Manifest、Journal 和特殊文件

### 更新 `.manifest.json`

对于每个处理的源文件，添加/更新其条目，包括：

- `ingested_at`, `size_bytes`, `modified_at`
- `source_type`: 之一 `"claude_conversation"`, `"claude_memory"`, `"claude_audit_log"`, `"claude_desktop_session"`
- `project`: 解码的项目名称
- `pages_created` 和 `pages_updated` 列表

还要更新 manifest 的 `projects` 部分：

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

### 创建 journal 条目 + 更新特殊文件

使用一个锁定调用更新 `index.md`、`log.md` 和 `hot.md`：

```bash
obsidian-wiki memory sync CLAUDE_HISTORY_INGEST \
  projects=<projects> conversations=<conversations> \
  desktop_sessions=<desktop_sessions> audit_logs=<audit_logs> \
  pages_updated=<pages_updated> pages_created=<pages_created> \
  mode=<mode> \
  --takeaways "导入 5 个 Claude 对话跨越 2 个项目；在 API 设计和测试策略中发现了模式。"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md`——该命令获取锁以防止并行写入者丢失您的更新。`--takeaways` 是以前放在最近活动中的单行概念摘要；
省略它以保留先前的 takeaways。

如果正在进行的项目现在有了更好的理解，请记录线程以便下次会话接手：`obsidian-wiki memory todo add "<thread>" --origin projects/<name>.md`。

有关完整过程的详细信息，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 隐私

- 提炼和综合——不要逐字复制原始对话文本
- 跳过任何看起来像密钥、API 密钥、密码、令牌的内容
- 如果您遇到个人/敏感内容，请在包含之前询问用户
- 用户的对话可能会引用其他人——在知识库中要谨慎考虑什么内容

## 参考

有关数据结构的更多详细信息，请参阅 `references/claude-data-format.md`。

## QMD 在 Vault 写入后刷新

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，请跳过此步骤。仅在 此技能写入或重写 Vault Markdown 后运行它。如果 QMD 刷新失败，请不要回滚 Vault 更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出说需要向量或嵌入可能已过时，请运行：

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

记录一个：

- `QMD 刷新：update + embed + verified`
- `QMD 刷新：update 仅 + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
