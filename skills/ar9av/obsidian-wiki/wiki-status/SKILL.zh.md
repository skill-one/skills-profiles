---
name: wiki-status
description: 展示维基的当前状态——已导入的内容、待处理的内容以及源内容与维基内容之间的差异。当用户询问“状态如何”、“已导入多少”、“还有多少待处理”、“显示差异”、“自上次导入以来有哪些变化”、“维基仪表盘”，或需要了解其知识库的健康状况和完整性时，使用此技能。此外，在决定是否追加或重建之前也使用此技能。包含一个由“维基洞察”、“核心内容是什么”、“显示我中心节点”、“核心页面”、“哪些内容相连”、“维基结构”等触发的内容洞察模式——分析维基本身的形态，以揭示顶级中心节点、跨域桥梁和孤儿相邻页面。此外还包括一个平衡模式，由“我的保险库是否达到平衡”、“维基平衡”、“维护是否完成”、“保险库是否收敛”或“我的技能是否在冲突”等触发——运行每个维护技能的仅审计通过，并报告它们中是否仍有待处理的变更。
---

# Wiki 状态 — 审计与差异

您正在计算 wiki 的当前状态：哪些内容已被导入，哪些内容自上次导入以来已更新，以及差异看起来如何。这有助于用户决定是否追加（导入差异）或重建（存档并重新处理所有内容）。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作的要求优先。

仅将 `WRITING.md` 偏好应用于生成的 `_insights.md` 文本；保留分析器快照的原始内容。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`、`OBSIDIAN_SOURCES_DIR`、`CLAUDE_HISTORY_PATH` 和 `CODEX_HISTORY_PATH`。
2. 读取 vault 根目录下的 `.manifest.json` — 这是导入跟踪账本

## 账本

账本位于 `$OBSIDIAN_VAULT_PATH/.manifest.json`。它跟踪每个已导入的源文件。如果不存在，这是一个全新的 vault，其中未导入任何内容。

> **源键是可移植的 — 永远不要裸用绝对路径。** 原始键对于 vault 内部源是相对的（`Raw/database/x.pdf`）、对于 `$HOME` 下的源是相对于 `~`（`~/.claude/projects/.../abc.jsonl`），或伪键（`repo:`/`url:`/`agent:`）对于没有可移植路径形式的源。永远不要混合形式 — 同一个文件会被跟踪两次并重新导入。参见 `llm-wiki/SKILL.md` → `.manifest.json`（源键合同 v2）。使用 `scripts/manifest.py migrate <vault>` 将遗留的绝对键账本转换为新的格式。

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

构建当前可用来导入的清单：

### 文档（来自 `OBSIDIAN_SOURCES_DIR`）
```
Glob 每个在 `OBSIDIAN_SOURCES_DIR` 中的目录以查找所有文本文件
记录：路径、大小、修改时间
```

### Claude 历史记录（来自 `CLAUDE_HISTORY_PATH`）
```
Glob: ~/.claude/projects/*/          → 项目目录
Glob: ~/.claude/projects/*/*.jsonl   → 对话文件
Glob: ~/.claude/projects/*/memory/*.md → 内存文件
记录：路径、大小、修改时间、父项目
```

### Codex 历史记录（来自 `CODEX_HISTORY_PATH`）
```
Glob: ~/.codex/session_index.jsonl            → 会话清单索引
Glob: ~/.codex/sessions/**/rollout-*.jsonl    → 会话回放文本
Glob: ~/.codex/history.jsonl                  → 可选的本地历史记录日志
Glob: ~/.codex/archived_sessions/**/rollout-*.jsonl → 归档回放（如果用户希望归档覆盖）
记录：路径、大小、修改时间、从 cwd 推断的项目
```

### 用户之前指向的任何其他源
检查账本中标准目录外的源路径。

## 第 2 步：计算差异

将当前源与账本进行比较。对每个源文件进行分类：

| 状态 | 含义 | 需要的操作 |
|---|---|---|
| **新** | 文件存在于磁盘上，但未在账本中 | 需要导入 |
| **已修改** | 账本中的文件，哈希与 `content_hash` 不同 | 需要重新导入 |
| **已更改** | 账本中的文件，修改时间更新但哈希未变 | 跳过 — 内容相同，无需重新导入 |
| **未更改** | 账本中的文件，修改时间和哈希都匹配 | 无需操作 |
| **已删除** | vault 本地源在账本中，但文件在磁盘上已不存在 | 记录下来 — wiki 页面可能已过时 |
| **不可用** | 机器本地源（相对于 home 的路径或绝对键）在此机器上不存在 — 例如来自另一主机的同步条目 | 跳过 — 不要报告为已删除或清理；它可能存在于导入它的机器上 |

当账本条目没有 `content_hash`（旧条目）时，仅回退到修改时间比较。

对于 Claude 历史记录特别计算：
- 新项目（`~/.claude/projects/` 中的目录未在账本中）
- 现有项目中的新对话
- 更新的内存文件

对于 Codex 历史记录特别计算：
- 在 `sessions/**` 下新回放文件
- 更新的 `session_index.jsonl` 条目（会话标题/新鲜度变化）
- 仅在请求归档覆盖时计算归档回放差异

## 第 3 步：报告状态

**可见性统计（在渲染报告之前）：** 在所有 vault `.md` 页面的 frontmatter 中搜索 `visibility/internal` 和 `visibility/pii` 标签值。统计：
- `public` = 具有 `visibility/public` 标签的页面 **或** 完全没有 `visibility/` 标签的页面
- `internal` = 具有 `visibility/internal` 标签的页面
- `pii` = 具有 `visibility/pii` 标签的页面

将此信息包含在概述部分中，作为 `Page visibility: N public · M internal · K pii`。如果所有页面都没有标签（完全公开的 vault），则跳过此行。

提供清晰的摘要：

```markdown
# Wiki 状态

## 概述
- **总 wiki 页面数：** 87 个跨 6 个类别
- **页面可见性：** 72 个公开 · 11 个内部 · 4 个 pii
- **已导入的总源数：** 42
- **跟踪的项目数：** 6
- **上次导入时间：** 2026-04-06T11:00:00Z
- **待处理的写入：** 4 个页面 · 2 个补丁（最旧的：3 天前）  ← 仅当 WIKI_STAGED_WRITES=true 时显示

## 差异（自上次导入以来发生了哪些变化）

### 新源（从未导入）：12
| 源 | 类型 | 大小 |
|---|---|---|
| ~/Documents/research/new-paper.pdf | document | 2.1 MB |
| ~/.claude/projects/-Users-.../session-xyz.jsonl | claude_conversation | 340 KB |
| ~/.codex/sessions/2026/04/12/rollout-...jsonl | codex_rollout | 220 KB |
| ... | | |

### 已修改的源（需要重新导入）：3
| 源 | 最后导入时间 | 最后修改时间 | 差异 |
|---|---|---|---|
| ~/notes/architecture.md | 2026-04-01 | 2026-04-05 | 4 天更新 |
| ... | | | |

### 新项目（尚未在 wiki 中）：2
- **tractorex**（3 个对话，2 个内存文件）
- **papertech**（1 个对话，0 个内存文件）

### 已删除的源（已导入但已不存在）：0

## 总结
- **准备导入：** 12 个新源 + 3 个已修改源 = 15 个源
- **已更新：** 27 个未更改的源
- **建议：** 追加（差异相对于总量的比例较小）

## 令牌足迹（估计）

| 范围 | 页面 | ~令牌 |
|---|---|---|
| 核心层 | 12 | 18,400 |
| 支持层 | 87 | 94,200 |
| 外围层 | 43 | 31,600 |
| **完整 wiki（全部）** | **142** | **144,200** |

索引仅通过（frontmatter + 摘要）：~8,900 令牌
典型查询（索引 + 5 个完整页面）：      ~14,200 令牌

⚠️  完整 wiki 超过 100K 令牌。考虑：
  - 降级外围页面（从 wiki-status insights 模式中提升层级建议）
  - 运行 /wiki-lint --consolidate 合并近似重复项
  - 使用 wiki-query 快速模式处理大多数查询
```

## 第 3 步 b：计算令牌足迹

构建状态摘要后，计算令牌足迹估计：

1. **每层页面大小** — Glob 所有 `.md` 页面。读取每个页面的 `tier:` frontmatter 字段（廉价的 grep）。按层级值（`core`、`supporting`、`peripheral`；未设置 → `supporting`）分组页面。

2. **估计令牌数** — 对于每个页面，估计令牌数为 `file_size_bytes / 4`（4 字符/令牌的启发式方法 — 无需实际分词器）。按层级求和和总计。

3. **索引仅估计** — 估计索引仅通过的成本：对每个页面的 frontmatter 汇总 `len(title) + len(summary) + len(tags)`（平均每个约 100 字符），除以 4。

4. **典型查询估计** — 索引仅估计 + 5 个页面平均完整读取成本（`total_chars / total_pages * 5 / 4`）。

5. **阈值检查** — 从配置中读取 `WIKI_TOKEN_WARN_THRESHOLD`（默认：`100000`）。如果为 `0`，则跳过警告。如果完整 wiki 令牌估计超过阈值，则发出 `⚠️` 警告，并显示模板中显示的三个补救建议。

6. **包含在每次标准状态运行中** — 无论是正常模式还是 insights 模式。方法学注释（`4 字符/令牌的启发式方法`）作为脚注显示在表格下方。

## 第 4 步：下一步该做什么

用排名 **下一步该做什么** 部分替换旧的单行建议。在渲染之前收集这些信号：

### 第 4a：收集信号

0. **待处理的写入**（仅当 `WIKI_STAGED_WRITES=true` 时）— Glob `$OBSIDIAN_VAULT_PATH/_staging/**/*.md` 和 `**/*.patch.md`。分别统计新页面和补丁。报告最旧文件的时间（mtime）。如果存在任何待处理文件，则始终将其列为第一项 — 它具有最高的意图信号（LLM 已经完成了工作；人类只需要进行审查）。

1. **`_raw/` 文件** — 列出 `$OBSIDIAN_VAULT_PATH/_raw/` 顶层中每个不是 `.gitkeep` 的文件（排除 `_archived/` 子目录，其中保留存档的草稿用于来源证明，而不是待处理的工作）。计数并命名它们。

2. **过时的核心页面** — 扫描所有 vault `.md` 文件。当页面的 `updated` frontmatter 字段 ≥90 天前于今天日期，并且它有 ≥5 个入站 wiki 链接时（即它是“核心” — 其他页面依赖于它），页面被认为是“过时”。按名称 + 最后更新日期列出它们。

3. **孤儿页面** — 没有零个入站 wiki 链接的页面。计算方法：glob 所有 `.md` 页面，提取每个 `[[wikilink]]`，统计每个页面的引用，收集 `incoming == 0` 的页面。最多显示 5 个名称；报告总数。

4. **合成机会** — 检查 `hot.md` 中任何最近的 `/wiki-synthesize` 运行摘要。如果上次合成运行报告了 N 个机会，则显示该计数。如果没有最近运行合成（不在 `hot.md` 或 `log.md` 中，最近 14 天内），则将其标记为“合成扫描过期”。

5. **源差异** — 来自第 2 步：准备导入的新源 + 修改源的计数。

6. **Lint 问题** — 检查 `log.md` 中最近的 `/wiki-lint` 运行（最近 30 天内）。如果最近的运行记录了损坏的链接或缺失的 frontmatter，则显示该计数。如果没有在日志中显示的 lint 运行，则标记为“lint 最近未运行”。

### 第 4b：排序和渲染

对每个类别进行评分并发出排名列表，**最多 6 项**。始终按此优先级顺序排序（如果某个类别的计数为 0 或没有报告内容，则跳过该类别）：

| 优先级 | 类别 | 触发条件 |
|---|---|---|
| 0 | 待处理的写入 | `_staging/` 中的任何 `.md`/`.patch.md`（仅当 `WIKI_STAGED_WRITES=true`） |
| 1 | `_raw/` 文件等待 | `_raw/` 中存在的任何文件 |
| 2 | 过时的核心页面 | 任何页面：更新 ≥90 天前 AND ≥5 个入站链接 |
| 3 | 孤儿页面 | 任何具有零个入站 wiki 链接的页面 |
| 4 | 合成机会 | 来自上次合成运行 N 个机会，或扫描过期 |
| 5 | 新/修改的源 | 第 2 步中的计数 |
| 6 | Lint 问题 | 来自上次 lint 运行的已知问题，或 lint 过期 |

渲染为：

```markdown
## 下一步该做什么

0. 📋  6 个待审查的页面（最旧的：3 天前）
   → 4 个新页面 + 2 个补丁在 _staging/
   运行：/wiki-stage-commit

1. 📥  导入 _raw/ 中等待的 3 个文件
   → architecture-notes.md, meeting-2026-05-10.md, paper-draft.pdf
   运行：/wiki-ingest

2. 🔄  刷新 2 个过时的核心页面（90 天以上未更新）
   → [[System Architecture]]（最后更新 2026-02-10），[[API Design]]（2026-01-15）
   运行：打开这些页面并重新运行 /wiki-update

3. 🔗  链接 7 个孤儿页面  →  运行：/cross-linker
   断开连接：[[Redis Caching]], [[JWT Tokens]], +5 更多

4. 🧩  确定 2 个合成机会  →  运行：/wiki-synthesize
   [[Redis Caching]] × [[Session Management]]（在 8 个页面中共同出现）

5. ✅  自上次导入以来 4 个源已修改  →  运行：/wiki-ingest（追加模式）

6. 🩺  30 天以上未运行 Lint — 运行：/wiki-lint
```

**空状态：** 如果所有类别都没有报告内容（没有待处理文件、没有 `_raw/` 文件、没有孤儿、没有过时的核心页面、没有合成机会、没有新源、没有 lint 问题），则输出：

```markdown
## 下一步该做什么

✅  Wiki 健康 — 无紧急事项。
    所有源已更新 · 无孤儿 · 无过时的核心页面 · 无 _raw/ 文件待处理 · 无待处理的写入
```

**溢出：** 如果显示的项超过 6 项，则添加一个页脚行：`_(N 更多项可用 — 运行 /wiki-status --full 查看所有)_`。`--full` 标志尚未实现；这是面向未来的文本，用于设定预期。

## Insights 模式

在用户询问类似“wiki insights”、“我的 wiki 中什么是最核心的”、“显示给我中心”、“跨域桥梁”、“哪些页面最重要”或“wiki 结构”时触发。此模式是 *附加的* — 它不会替换差异报告，而是分析 wiki 本身的 *形状*。

差异报告告诉用户哪些内容待处理，insights 模式告诉他们已经构建了什么以及有趣的结构的所在位置。补充 `wiki-lint`（它查找 *问题*）通过揭示 *有趣的结构*。

### 需要计算的内容

**首先，运行图分析器。** 这替换了手动 wikilink 解析 — 一个命令产生您需要的所有原始数据：

```bash
obsidian-wiki graph-analyse "$OBSIDIAN_VAULT_PATH" --pretty --snapshot \
  --diff-against "$OBSIDIAN_VAULT_PATH/_insights.md"   # 如果没有之前的 _insights.md，则省略
```

分析器运行与 graphify 应用于代码图相同的算法家族，纯 Python：度排名、社区检测（如果 `obsidian-wiki[graph]` 已安装则使用 Leiden，否则使用标签传播）、社区凝聚力、Brandes 介数中心性、跨社区意外评分和快照差异。Vault 书籍管理文件（`index`、`log`、`hot`、`_insights`、`_meta/`、`_readouts/`）被排除，以免它们主导每个排名。

以下是您提供的文档的简体中文翻译：

---

### 以下是使用的输出字段：
- `god_nodes` — 按总度数（入度+出度）排序的页面，包含 `in_degree`/`out_degree`。用于锚页面和中心节点分类。
- `bridges` — 按介数中心性（最短路径中经过它们的比例）排序的页面，包含 `community` 和它们连接的其他社区列表。直接用于桥接页面部分 — 无需手动查找标签对。
- `communities` — 按链接密度分组的页面集群，每个集群包含 `label`、`size`、`pages` 和 `cohesion`（集群内边密度，0–1）。用于集群标签和凝聚力部分。
- `surprising_connections` — 跨社区边按意外性排序，每个社区对之前重复对之前，每个包含一个 `note` 标识两个社区。直接用于意外连接部分。
- `suggested_questions` — 从桥接、汇点、孤立点和低凝聚力集群中派生的 `{type, question, why}`。用这些为问题部分提供种子。
- `dead_ends` — 出度为零的页面。用于孤儿相邻和跨链接器建议。
- `isolated` — 双向链接为零的页面。用于 stubs/孤儿报告。
- `stats` — 总页面数、边数、社区数、图 `密度`。
- `diff`（仅与 `--diff-against` 一起使用）— `added_pages`、`removed_pages`、`added_edges`、`removed_edges`、`newly_connected`、`lost_incoming`、`summary`。用于图变化部分。
- `snapshot`（仅与 `--snapshot` 一起使用）— 将此 JSON 原文写入 `_insights.md` 结尾的 `<!-- GRAPH_SNAPSHOT: ... -->` 评论中。

查询模式（当用户询问后续问题时有用）: `--path A B` 返回两个页面之间的最短链接链；`--around PAGE --depth N [--direction in|out|both]` 返回 N 跳邻域 (`--direction in` = 如果 PAGE 被重命名或删除，则为其的爆炸半径）。

**备用**（如果 `obsidian-wiki` 未安装）：glob 所有 `.md` 页面，提取每个 `[[wikilink]]`，然后手动构建 `incoming`、`outgoing` 和 `tags` 映射，然后手动近似以下部分。

你将在以下所有部分中重复使用这些数据。

---

1. **锚页面（顶级中心节点）。** 拥有最多入链的页面 — 承重概念。
   - 按 `incoming` 计数对所有页面进行排序，取前 10
   - 对每个页面，注意入链和出链计数：入链和出链都高的页面是连接器中心节点（最有价值）
   - 入链高但出链为零的页面是汇点 — 标记为跨链接器候选

2. **桥接页面。** 连接原本断开集群的页面 — 移除它们会分区图。这些通常比原始中心节点计数更重要。
   - 取 `bridges` 的前 5（按介数中心性排序）
   - 使用社区标签对每个页面进行标记："`P` 桥接 `[community label]` ↔ `[connects labels]`"。空 `connects` 列表的桥接是集群内瓶颈 — 标记为 " `[label]` 的内部中心节点"
   - 显示介数分数以便跨时间比较

3. **集群凝聚力。** 每个社区页面之间相互链接的紧密程度 — 直接从 `communities[].cohesion` 读取 (`actual_links / (n × (n−1) / 2)`).
   - **碎片化集群**（凝聚力 < 0.15，大小 ≥ 5）：这些页面共享主题但未紧密编织。将它们作为跨链接器目标展示。
   - 显示凝聚力最强的前 5 个社区和最碎片化的后 5 个，每个都包含其标签和大小
   - 如果用户关心标签级凝聚力，可以按标签重复相同公式（对于 ≥ 5 页面的标签）

4. **意外连接。** 非直观的跨社区 wikilink。
   - 从 `surprising_connections` 开始（结构分数 = 1/√(跨度(A)·跨度(B))；每个社区对在重复之前只有一个边，所以单个中心节点无法填满列表）
   - 使用分析器无法看到的内容信号重新对候选进行排序：
     - **+3** 如果链接页面或声明标记为 `^[ambiguous]`（不确定连接，值得审查）
     - **+2** 如果链接页面标记为 `^[inferred]`（综合，未直接声明）
     - **+2** 如果类别在不同知识层（例如，`concepts` ↔ `entities` 比较意外于 `concepts` ↔ `concepts`）
   - 显示前 5 个，每个都有一个简单的语言解释（使用 `note` — "桥接 `[label A]` → `[label B]`" 加上任何内容奖励）

5. **孤儿相邻建议。** 从顶级 10 个中心节点链接的页面但自身没有出链。高流量区域的死胡同 — 优先级高的跨链接器候选。

6. **粗略集群。** 按主导标签对锚页面进行分组。（简单的标签交集 — 仅用于方向）

7. **自上次运行以来的图变化。** 直接从 `diff` 字段读取（由 `--diff-against` 在之前的 `_insights.md` 产生，分析器从其 `<!-- GRAPH_SNAPSHOT: ... -->` 评论中读取）：
   - `summary` → "+N 页面，+M wikilinks"；列出 `added_pages` / `removed_pages`
   - `newly_connected` → "新连接：X, Y"（上次运行时没有入链的页面）
   - `lost_incoming` → "链接目标可能已被重命名：A, B"
   - 如果没有之前的快照（没有 `diff` 字段），跳过此部分

8. **层级分配建议。** 计算中心节点和桥接后，建议 `tier:` 变化。永远不会写入 `tier:` 到页面 — 仅展示建议供人类决定。
   - **提升到 `core`**：有 ≥5 入链的页面或当前为 `tier: supporting` 的前 5 个桥接位置
   - **降级到 `peripheral`**：有 ≤1 入链且 90+ 天未更新的页面当前为 `tier: supporting` 或 `tier: core`
   - 显示最多 10 个建议（提升优先，然后降级），格式化为：
     ```
     层级建议：
     ↑ core    [[concepts/attention-mechanism]] — 14 入链，当前 tier=supporting
     ↑ core    [[entities/andrej-karpathy]]     — 桥接 (3 集群对)，当前未设置
     ↓ peripheral [[concepts/old-concept]]       — 0 入链，120 天陈旧
     ```
   - 如果所有高链接页面都已有 `tier: core` 且所有低链接页面都已有 `tier: peripheral`，发出： "层级分配看起来健康 — 没有建议变更。"

9. **建议问题。** 此 wiki 结构独特地能够回答的问题 — 或揭示差距：
   - 从 `^[ambiguous]` 声明（内容扫描 — 分析器看不到这些）： "解决：`X` 和 `Y` 之间的确切关系是什么？"（^[ambiguous] 声明）
   - 从 `suggested_questions` — 已经为你生成：`bridge_node` → "探索：…"，`sink_hub` → "链接：…"，`isolated_nodes` → "链接：…"，`low_cohesion` → "审计：…"。将每个重写为匹配的前缀形式
   - 显示最多 7 个，优先级为 AMBIGUOUS，然后是桥接节点，然后是汇点/孤立点，然后是凝聚力审计

---

### 输出

将结果写入 `_insights.md` 在保险库根目录。自由覆盖 — 它是可再生的。在最末尾，将分析器的 `snapshot` 字段原样嵌入为 HTML 评论，以便下次运行时可以使用 `--diff-against` 与其进行比较。

```markdown
# Wiki Insights — <TIMESTAMP>

## 锚页面（前 10 个中心节点）
| 页面 | 入链 | 出链 | 备注 |
|---|---|---|---|
| [[concepts/transformer-architecture]] | 23 | 8 | 连接器中心节点 |
| [[entities/andrej-karpathy]] | 17 | 0 | 汇点 — 跨链接器候选 |

## 桥接页面（前 5）
| 页面 | 桥接 | 跨集群对 |
|---|---|---|
| [[concepts/exponential-growth]] | #ml ↔ #economics | 4 对 |

## 标签集群凝聚力
### 凝聚力最强（紧密链接）
- **#ml** — 12 页面，凝聚力 0.41
### 凝聚力最弱（跨链接器目标）
- **#systems** — 7 页面，凝聚力 0.06 ⚠️ 运行跨链接器在此标签上

## 意外连接（前 5）
- [[concepts/scaling-laws]] → [[entities/gordon-moore]] — 分数 5
  - 原因：跨层（概念 ↔ 实体），标记 ^[inferred]
- ...

## 孤儿相邻（靠近中心节点的死胡同）
- [[concepts/foo]] — 从 3 个中心节点链接，0 出链

## 粗略集群
- **#ml** — transformer-architecture, attention-mechanism, scaling-laws
- **#systems** — distributed-consensus, raft, paxos

## 自上次运行以来的图变化
- +3 新页面，+11 新 wikilinks
- 新连接：[[concepts/bar]], [[entities/baz]]
- 失去入链：[[references/old-paper]] (目标可能已被重命名)

## 层级建议
↑ core    [[concepts/attention-mechanism]] — 14 入链，当前 tier=supporting
↑ core    [[entities/andrej-karpathy]]     — 顶级桥接 (4 集群对)，当前未设置
↓ peripheral [[concepts/old-concept]]       — 0 入链，132 天陈旧

## 值得提问的问题
1. 解决：`scaling-laws` 和 `moore's-law` 之间的确切关系是什么？(^[ambiguous] 声明)
2. 探索：为什么 `exponential-growth` 桥接 #ml 和 #economics？
3. 链接：`references/foo.md` 没有入链 — 应该引用它什么？
4. 审计：是否应该拆分标签 `#systems`？(凝聚力 0.06, 7 页面)

<!-- GRAPH_SNAPSHOT: {"nodes":["concepts/foo","entities/bar"],"edges":[["concepts/foo","entities/bar"]]} -->
```

写入文件后，追加到 `log.md`：
```
- [TIMESTAMP] STATUS_INSIGHTS anchors=10 bridges=N cohesion_checked=T surprising=5 questions=7 delta="+N pages +M links" tier_suggestions=N
```

### 跳过时机

- 页面少于 20 个的保险库 — 图结构不足。告诉用户并跳过。
- 在 `wiki-rebuild` 后 — 等待至少一次摄取发生。

## 平衡模式

当用户询问 "我的保险库是否处于平衡状态"、"wiki 平衡"、"保险库是否收敛"、"维护是否完成"、"我的技能是否在对抗" 或 "所有维护技能中还有哪些未完成" 时触发。

维护技能是 **在一个共享保险库中玩游戏的角色**。每个角色都有一个动作集（lint 修复、去重合并、新链接、标签规范化），每个角色都根据自己的目标判断保险库。当没有玩家有盈利的偏差时，保险库处于 **平衡状态** — 每次审计建议零变更。这就是真正的 "维护完成" 信号，比任何单个技能报告干净都更强，因为技能可以相互抵消。

此模式是 **对玩家只读的**：运行每个审计在其报告形式，永不应用更改。它只写入 `_insights.md` 中的快照行。

### 玩家

| 玩家 | 仅审计调用 | 计数是否为一次移动 |
|---|---|---|
| `wiki-lint` | `obsidian-wiki lint "$OBSIDIAN_VAULT_PATH" --json` | `findings` 中的每个发现（累加 `stats.findings` 计数） |
| `wiki-dedup` | 审计模式（无 `--merge`，无 `--auto`） | 每个 HIGH 或 MEDIUM 重复对 |
| `cross-linker` | 仅审计通过 — 报告建议链接，不插入任何 | 它会链接的每个未链接提及 |
| `tag-taxonomy` | 仅审计第一步 — 报告漂移，不规范化任何 | 它会重命名或删除的每个标签 |

只有 `wiki-lint` 是确定性的；其他三个是 LLM 通过，所以它们的计数是它们自己报告的估计。在输出中说明这一点，而不是暗示精确性。

### 要报告的内容

```
# 保险库平衡 — <TIMESTAMP>

equilibrium: no

| 玩家 | 待处理移动 | 顶级建议移动 |
|---|---|---|
| wiki-lint | 4 | 修复 synthesis/foo.md 中损坏的链接 [[concepts/old-name]] |
| wiki-dedup | 1 | 合并 entities/gpt-4.md ← entities/gpt4.md (0.91) |
| cross-linker | 12 | 在 concepts/transformers.md 中链接 "attention mechanism" |
| tag-taxonomy | 0 | — |

偏离的玩家：wiki-lint, wiki-dedup, cross-linker
收敛的玩家：tag-taxonomy
```

当每个计数为零时，报告 `equilibrium: yes` 并明确说明立即运行任何维护技能不会改变任何内容。

### 振荡检测

一个计数在被驱动到零后又不断返回的玩家意味着两个玩家在 **对抗** — 经典案例是 `tag-taxonomy` 规范一个标签，而摄取技能的默认值不断重新添加，所以保险库无限循环且永远不会收敛。

在 `_insights.md` 中现有 `GRAPH_SNAPSHOT` 旁边追加一个快照：

```
<!-- EQUILIBRIUM_SNAPSHOT: {"ts":"2026-08-25T10:00:00Z","lint":4,"dedup":1,"crosslink":12,"tags":0} -->
```

读取之前的 `EQUILIBRIUM_SNAPSHOT` 行（保留最后 5 个；删除旧的），并进行比较：
- 一个玩家在运行中从 `0 → N → 0 → N` 是 **振荡** — 通过名称标记它并命名可能的对手（重新引入这些移动的技能）。
- 一个玩家计数只增长的是 **失去进展** — 没有人运行它。
- 没有之前的快照：报告 "首次运行，尚无基线" 并跳过比较。

振荡是一个报告，不是修复。解决方案是人类的决定，关于哪个玩家的目标获胜 — 通常是 `_meta/taxonomy.md` 中的规则变更或所有者的 `AGENTS.md`，而不是另一个维护运行。

### 源记录

待处理移动在源之间分布不均。将它们回溯：对于出现在玩家发现中的每个页面，查找它是由哪个清单源产生的（`.manifest.json` → `pages_created` / `pages_produced`）。

当一个源解释 ≥3 个问题或 ≥50% 的玩家待处理移动时，添加一行：

```
源记录：
- ~/exports/slack-dump/ — 12 个 cross-linker 移动中的 7 个，4 个 lint 发现中的 3 个。
  它的页面需要持续修复；考虑审查其 `source_quality` 桶。
```

这是重复博弈的观点：一个不断产生需要修复页面的源已经赢得了较低的 `source_quality`。**仅报告** — 永远不要自动调整 `source_quality` 或信任账本。所有者决定，通过现有的信任流程 (`obsidian-wiki trust-record`)，与每个其他信心变更完全相同。

### 跳过时机

- 页面少于 20 个的保险库 — 在该规模下审计是噪音。
- 如果任何玩家的审计不能以干净的报告形式运行，省略该行并说明缺少哪个玩家，而不是猜测计数。

## 备注

- 如果清单不存在，将所有内容报告为 "新" 并建议完整摄取
- 此技能只读取和报告 — 它不修改任何内容（除了在洞察模式下写入 `_insights.md`，它是可再生的）
- 实际摄取工作是由摄取技能 (`wiki-ingest`, `claude-history-ingest`, `codex-history-ingest`) 完成的
- 这些技能负责在它们完成后更新清单

## QMD 在保险库写入后刷新

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在技能写入或重写了保险库 markdown 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，使用 `$QMD_CLI`；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出说需要向量或嵌入可能已过时，运行：

```bash
${QMD_CLI:-qmd} embed
```

使用以下任一方法验证集合：

```bash
${QMD_CLI:-qmd} ls "$QMD_WIKI_COLLECTION"
```

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录一个：
- `QMD 刷新：update + embed + verified`
- `QMD 刷新：update 仅 + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
