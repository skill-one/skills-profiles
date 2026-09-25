# Wiki 状态 — 审计与差异

您正在计算 wiki 的当前状态：哪些内容已被导入，哪些内容是自上次导入以来新增的，以及差异的样子。这有助于用户决定是否追加（导入差异）或重建（存档并重新处理所有内容）。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作的要求优先。
仅将 `WRITING.md` 偏好应用于生成的 `_insights.md` 文本；保留分析器快照的原始内容。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 搜索 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`、`OBSIDIAN_SOURCES_DIR`、`CLAUDE_HISTORY_PATH` 和 `CODEX_HISTORY_PATH`。
2. 在保险库根目录下读取 `.manifest.json` — 这是导入跟踪账本

## 清单

清单位于 `$OBSIDIAN_VAULT_PATH/.manifest.json`。它跟踪每个已导入的源文件。如果不存在，这是一个全新的保险库，没有任何内容被导入。

> **源键是可移植的 — 永远不要裸绝对路径。** 原始键是保险库相对的，用于保险库内的源（`Raw/database/x.pdf`），`~` 相对于 `$HOME` 下的源（`~/.claude/projects/.../abc.jsonl`），或伪键（`repo:`/`url:`/`agent:`）用于没有可移植路径形式的源。永远不要混合形式 — 同一个文件会被跟踪两次并重新导入。参见 `llm-wiki/SKILL.md` → `.manifest.json`（源键合同 v2）。使用 `scripts/manifest.py migrate <vault>` 将遗留的绝对键清单转换为新的形式。

```json
{
  "version": 1,
  "last_updated": "2026-04-06T10:30:00Z",
  "sources": {
    "Raw/papers/attention.pdf": {
      "ingested_at": "2026-04-06T10:30:00Z",
      "size_bytes": 4523,
      "modified_at": "2026-04-05T08:00:00Z",
      "source_type": "document",
      "project": null,
      "pages_created": ["concepts/transformers.md"],
      "pages_updated": ["entities/vaswani.md"]
    },
    "~/.claude/projects/-Users-name-my-app/abc123.jsonl": {
      "ingested_at": "2026-04-06T11:00:00Z",
      "size_bytes": 128000,
      "modified_at": "2026-04-06T09:00:00Z",
      "source_type": "claude_conversation",
      "project": "my-app",
      "pages_created": ["entities/my-app.md"],
      "pages_updated": ["skills/react-debugging.md"]
    }
  },
  "projects": {
    "my-app": {
      "source_repo": "github.com/owner/my-app",
      "source_cwd_hint": "~/.claude/projects/-Users-name-my-app",
      "vault_path": "projects/my-app",
      "last_ingested": "2026-04-06T11:00:00Z",
      "conversations_ingested": 5,
      "conversations_total": 8,
      "memory_files_ingested": 3
    }
  },
  "stats": {
    "total_sources_ingested": 42,
    "total_pages": 87,
    "total_projects": 6,
    "last_full_rebuild": null
  }
}
```

## 第 1 步：扫描当前源

构建一个清单，列出当前可以导入的所有内容：

### 文档（来自 `OBSIDIAN_SOURCES_DIR`）
```
在 OBSIDIAN_SOURCES_DIR 中的每个目录中 glob 所有文本文件
记录：路径、大小、修改时间
```

### Claude 历史记录（来自 `CLAUDE_HISTORY_PATH`）
```
Glob: ~/.claude/projects/*/          → 项目目录
Glob: ~/.claude/projects/*/*.jsonl   → 会话文件
Glob: ~/.claude/projects/*/memory/*.md → 内存文件
记录：路径、大小、修改时间、父项目
```

### Codex 历史记录（来自 `CODEX_HISTORY_PATH`）
```
Glob: ~/.codex/session_index.jsonl            → 会话清单索引
Glob: ~/.codex/sessions/**/rollout-*.jsonl    → 会话回滚转录
Glob: ~/.codex/history.jsonl                  → 可选的本地历史记录日志
Glob: ~/.codex/archived_sessions/**/rollout-*.jsonl → 归档回滚（如果用户想要归档覆盖）
记录：路径、大小、修改时间、从可用时根据 cwd 推断的项目
```

### 任何其他用户之前指向的源
检查清单中标准目录外的源路径。

## 第 2 步：计算差异

将当前源与清单进行比较。对每个源文件进行分类：

| 状态 | 含义 | 需要的操作 |
|---|---|---|
| **新** | 文件存在于磁盘上，但不在清单中 | 需要导入 |
| **已修改** | 清单中的文件，哈希与 `content_hash` 不同 | 需要重新导入 |
| **已更改** | 清单中的文件，mtime 新但哈希未更改 | 跳过 — 内容相同，无需重新导入 |
| **未更改** | 清单中的文件，mtime 和哈希都匹配 | 无需操作 |
| **已删除** | 清单中的保险库本地源，但文件在磁盘上不再存在 | 记录下来 — wiki 页面可能已过时 |
| **不可用** | 机器本地源（以 `home` 相对或绝对键形式）在此机器上不存在 — 例如来自另一主机的同步条目 | 跳过 — 不要报告为已删除或清理；它可能存在于导入它的机器上 |

当清单条目没有 `content_hash`（旧条目）时，仅回退到 mtime 比较。

对于 Claude 历史记录特别地，还计算：
- 新项目（`~/.claude/projects/` 中的目录不在清单中）
- 现有项目内的新会话
- 更新的内存文件

对于 Codex 历史记录特别地，还计算：
- `sessions/**` 下新回滚文件
- 更新的 `session_index.jsonl` 条目（会话标题/新鲜度变化）
- 仅当请求归档覆盖时才计算归档回滚差异

## 第 3 步：报告状态

**可见性统计（在渲染报告之前）：** 在所有保险库 `.md` 页面的 frontmatter 中 grep `visibility/internal` 和 `visibility/pii` 标签值。统计：
- `public` = 具有 `visibility/public` 标签的页面 **或** 完全没有 `visibility/` 标签
- `internal` = 具有 `visibility/internal` 标签的页面
- `pii` = 具有 `visibility/pii` 标签的页面

将其包含在概述部分中，作为 `Page visibility: N public · M internal · K pii`。如果所有页面都没有标签（完全公开的保险库），则跳过该行。

呈现清晰的摘要：

```markdown
# Wiki 状态

## 概述
- **总 wiki 页面数：** 6 个类别中的 87 页
- **页面可见性：** 72 个公开 · 11 个内部 · 4 个 pii
- **已导入的总源：** 42
- **跟踪的项目：** 6
- **上次导入：** 2026-04-06T11:00:00Z
- **待处理的写入：** 4 页面 · 2 个补丁（最旧的：3 天前）  ← 仅当 WIKI_STAGED_WRITES=true 时显示

## 差异（自上次导入以来的变化）

### 新源（从未导入）：12
| 源 | 类型 | 大小 |
|---|---|---|
| ~/Documents/research/new-paper.pdf | document | 2.1 MB |
| ~/.claude/projects/-Users-.../session-xyz.jsonl | claude_conversation | 340 KB |
| ~/.codex/sessions/2026/04/12/rollout-...jsonl | codex_rollout | 220 KB |
| ... | | |

### 已修改的源（需要重新导入）：3
| 源 | 上次导入 | 上次修改 | 差异 |
|---|---|---|---|
| ~/notes/architecture.md | 2026-04-01 | 2026-04-05 | 4 天更新 |
| ... | | | |

### 新项目（尚未在 wiki 中）：2
- **tractorex**（3 个会话，2 个内存文件）
- **papertech**（1 个会话，0 个内存文件）

### 已删除的源（已导入但已消失）：0

## 摘要
- **准备导入：** 12 个新 + 3 个修改 = 15 个源
- **已更新：** 27 个未更改的源
- **建议：** 追加（差异相对于总量的比例很小）

## 令牌足迹（估计）

| 范围 | 页面 | ~令牌 |
|---|---|---|
| 核心层 | 12 | 18,400 |
| 支持层 | 87 | 94,200 |
| 外围层 | 43 | 31,600 |
| **完整 wiki（所有）** | **142** | **144,200** |

仅索引传递（frontmatter + 摘要）：~8,900 令牌
典型查询（索引 + 5 个完整页面）：      ~14,200 令牌

⚠️ 完整 wiki 超过 100K 令牌。考虑：
  - 降级外围页面（从 wiki-status insights 模式中的层级建议）
  - 运行 /wiki-lint --consolidate 以合并接近重复项
  - 使用 wiki-query 快速模式进行大多数查询
```

## 第 3 步：计算令牌足迹

构建状态摘要后，计算令牌足迹估计：

1. **每层级的页面大小** — glob 所有 `.md` 页面。读取每个页面的 `tier:` frontmatter 字段（cheap grep）。按层级值分组页面（`core`，`supporting`，`peripheral`；未设置 → `supporting`）。

2. **估计令牌** — 对于每个页面，估计令牌数量为 `file_size_bytes / 4`（4 个字符/令牌的启发式方法 — 无需实际分词器）。按层级求和和总计。

3. **仅索引估计** — 估计索引传递的成本：对每个页面的 frontmatter 求和 `len(title) + len(summary) + len(tags)`（平均每个约 100 个字符），除以 4。

4. **典型查询估计** — 索引仅估计 + 平均 5 个页面的完整读取成本（`total_chars / total_pages * 5 / 4`）。

5. **阈值检查** — 从配置中读取 `WIKI_TOKEN_WARN_THRESHOLD`（默认：`100000`）。如果 `0`，则跳过警告。如果完整 wiki 令牌估计超过阈值，则发出 `⚠️` 警告，并显示模板中显示的三个补救建议。

6. **包含在每次标准状态运行中** — 无论是正常模式还是 insights 模式。方法说明（`4 个字符/令牌的启发式方法）作为脚注显示在表格下方。

## 第 4 步：接下来该做什么

用排名的 **接下来该做什么** 部分替换旧的单一行建议。在渲染之前收集这些信号：

### 4a：收集信号

0. **待处理的写入**（仅当 `WIKI_STAGED_WRITES=true` 时）— glob `$OBSIDIAN_VAULT_PATH/_staging/**/*.md` 和 `**/*.patch.md`。分别统计新页面和补丁。报告最老文件的时间（mtime）。如果存在待处理的文件，则始终将其列在第一位 — 它具有最高的意图信号（LLM 已经完成了工作；人类只需要进行审查）。

1. **`_raw/` 文件** — 列出 `$OBSIDIAN_VAULT_PATH/_raw/` 顶层中每个不是 `.gitkeep` 的文件；排除 `_archived/` 子目录（保留用于来源的存档草稿，不是待处理的工作）。

2. **陈旧的 core 页面** — 扫描所有保险库 `.md` 文件。当页面的 `updated` frontmatter 字段 ≥90 天前于今天日期，并且它有 ≥5 个传入的 wikilink（即它是“core” — 其他页面依赖于它）时，该页面被认为是“陈旧的”。按名称 + 最后更新日期列出它们。

3. **孤儿页面** — 没有零传入 wikilink 的页面。要计算：glob 所有 `.md` 页面，提取每个 `[[wikilink]]`，计算每个页面引用的次数，收集传入链接为 0 的页面。最多显示 5 个名称；报告总数。

4. **合成机会** — 检查 `hot.md` 中的任何最近的 `/wiki-synthesize` 运行摘要。如果上次合成运行报告了 N 个机会，则显示该计数。如果没有最近运行合成（不在 `hot.md` 或 `log.md` 中 14 天内），则将其标记为“合成扫描过期”。

5. **源差异** — 来自第 2 步：准备导入的新 + 修改的源计数。

6. **Lint 问题** — 检查 `log.md` 中的最近 `/wiki-lint` 运行（在过去 30 天内）。如果最近的运行记录了损坏的链接或缺失的 frontmatter，则显示该计数。如果没有在日志中显示 lint 运行，则标记“最近未运行 lint”。

### 4b：排序和渲染

对每个类别进行评分，并发出排名列表，**最多 6 项**。始终按此优先级顺序排序（如果某个类别的计数为 0 或它没有可报告的内容，则跳过）：

| 优先级 | 类别 | 触发器 |
|---|---|---|
| 0 | 待处理的写入 | `_staging/` 中的任何 `.md`/`.patch.md`（仅当 `WIKI_STAGED_WRITES=true` 时） |
| 1 | `_raw/` 文件等待 | `_raw/` 中存在的任何文件 |
| 2 | 陈旧的 core 页面 | 任何页面：更新 ≥90 天前 AND ≥5 个传入链接 |
| 3 | 孤儿页面 | 任何具有零传入 wikilink 的页面 |
| 4 | 合成机会 | 来自上次合成运行 N 个机会，或扫描过期 |
| 5 | 新/修改的源 | 第 2 步中的差异计数 |
| 6 | Lint 问题 | 最近 lint 运行中的已知问题，或 lint 过期 |

渲染为：

```markdown
## 接下来该做什么

0. 📋  6 个待审查的页面（最旧的：3 天前）
   → 4 个新页面 + 2 个补丁在 _staging/
   运行: /wiki-stage-commit

1. 📥  导入 _raw/ 中等待的 3 个文件
   → architecture-notes.md, meeting-2026-05-10.md, paper-draft.pdf
   运行: /wiki-ingest

2. 🔄  刷新 2 个陈旧的 core 页面（90 天以上未更新）
   → [[System Architecture]] (最后更新 2026-02-10), [[API Design]] (2026-01-15)
   运行: 打开这些页面并重新运行 /wiki-update

3. 🔗  链接 7 个孤儿页面  → 运行: /cross-linker
   断开连接: [[Redis Caching]], [[JWT Tokens]], +5 更多

4. 🧩  确定 2 个合成机会  → 运行: /wiki-synthesize
   [[Redis Caching]] × [[Session Management]] (在 8 个页面中共同出现)

5. ✅  自上次导入以来 4 个源已修改  → 运行: /wiki-ingest (追加模式)

6. 🩺  30 天以上未运行 lint — 运行: /wiki-lint
```

**空状态：** 如果所有类别都没有可报告的内容（没有待处理的文件，没有 `_raw/` 文件，没有孤儿，没有陈旧的 core 页面，没有合成机会，没有新源，没有 lint 问题），则输出：

```markdown
## 接下来该做什么

✅  Wiki 健康 — 无紧急事项。
    所有源已更新 · 无孤儿 · 无陈旧的 core 页面 · 无 _raw/ 文件待处理 · 无待处理的写入
```

**溢出：** 如果显示的项超过 6 项，则添加一个页脚行：`_(N 更多项可用 — 运行 /wiki-status --full 查看所有)_`。`--full` 标志尚未实现；这是面向未来的文本，用于设定预期。

## Insights 模式

当用户询问类似“wiki insights”，“我 wiki 中的核心是什么”，“显示给我中心”，“跨域桥梁”，“哪些页面最重要”，或“wiki 结构”时，将触发此模式。此模式是 *附加的* — 它不会替换差异报告，它分析 wiki 本身的 *形状*。

差异报告告诉用户什么正在等待，insights 模式告诉他们已经构建了什么，以及有趣的结构的所在位置。补充 `wiki-lint`（它发现 *问题*）通过揭示 *有趣的结
