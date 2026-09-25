# OpenClaw 历史数据导入 — 会话与内存挖掘

您正在从用户的 OpenClaw 代理历史记录中提取知识，并将其提炼到 Obsidian 知识库中。OpenClaw 存储结构化的长期内存文件 MEMORY.md 以及每个会话的 JSONL 文本记录 — 专注于持久知识，而非操作级遥测数据。

此技能可以直接调用，或通过 `wiki-history-ingest` 路由器 (`/wiki-history-ingest openclaw`) 调用。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `OPENCLAW_HISTORY_PATH`（默认为 `~/.openclaw`）
2. 在保险库根目录下读取 `.manifest.json` 以检查已导入的内容
3. 在保险库根目录下读取 `index.md` 以了解知识库已包含的内容

## 导入模式

### 追加模式（默认）

检查每个源文件的 `.manifest.json`。仅处理：

- 未在清单中出现的文件（新的会话日志、更新的 MEMORY.md 或每日笔记）
- 修改时间比清单中的 `ingested_at` 更新的文件

使用此模式进行常规同步。

### 全量模式

无论清单如何，处理所有内容。在执行 `wiki-rebuild` 后或用户明确要求完整重新导入时使用。

## OpenClaw 数据布局

OpenClaw 将所有本地文件存储在 `~/.openclaw/` 下。

```
~/.openclaw/
├── openclaw.json                          # 全局配置
├── credentials/                           # 认证令牌（完全跳过）
├── workspace/                             # 代理工作区
│   ├── MEMORY.md                          # 长期记忆（每次会话加载）
│   ├── DREAMS.md                          # 可选的梦境日记/摘要
│   └── memory/
│       ├── YYYY-MM-DD.md                  # 每日笔记（今天和昨天自动加载）
│       └── ...
└── agents/
    └── <agentId>/
        ├── agent/
        │   └── models.json                # 代理配置（跳过）
        └── sessions/
            ├── sessions.json              # 会话索引
            └── <sessionId>.jsonl          # 会话记录（JSONL，仅追加）
```

### 按价值排序的关键数据源

1. `workspace/MEMORY.md` — 最高信号；代理积累的长期持久事实
2. `workspace/memory/YYYY-MM-DD.md` — 每日笔记；最近的条目通常包含活跃项目上下文
3. `agents/*/sessions/<id>.jsonl` — 会话记录；丰富但嘈杂
4. `agents/*/sessions/sessions.json` — 会话索引，用于清单和时间戳
5. `workspace/DREAMS.md` — 可选摘要；如果存在则导入

完全跳过 `credentials/`。跳过 `agents/*/agent/models.json`（运行时配置，非用户知识）。

## 第 1 步：调查并计算差异

扫描 `OPENCLAW_HISTORY_PATH` 并与 `.manifest.json` 进行比较：

- `~/.openclaw/workspace/MEMORY.md`
- `~/.openclaw/workspace/DREAMS.md`（如果存在）
- `~/.openclaw/workspace/memory/*.md`
- `~/.openclaw/agents/*/sessions/sessions.json`
- `~/.openclaw/agents/*/sessions/*.jsonl`

对每个文件进行分类：

- **新文件** — 未在清单中
- **已修改** — 在清单中但文件比清单中的 `ingested_at` 更新
- **未更改** — 已导入且未更改

在深度解析之前报告简洁的差异摘要。

## 第 2 步：首先解析 MEMORY.md

`MEMORY.md` 是价值最高的来源。它是纯 Markdown，人类可读和可编辑。它通常包含：

- 关于用户偏好、环境和重复模式的持久事实
- 代理被指示记住的决策和上下文
- 代理在多个会话中积累的项目特定笔记

完整读取并提取概念级知识。不要为每个 MEMORY.md 条目创建一个知识库页面 — 按主题进行聚类。

## 第 3 步：解析每日笔记

`workspace/memory/YYYY-MM-DD.md` 文件包含当天会话的时间戳笔记。优先考虑最近文件（最后 30-90 天）。提取：

- 活跃项目上下文和做出的决策
- 发现的模式或技术
- 反复出现的障碍或已解决的问题

较旧的每日笔记信号递减 — 批量总结而不是逐行提取。

## 第 4 步：安全地解析会话 JSONL

每个会话文件是 JSONL（仅追加，每行一个 JSON 对象）：

```json
{"role": "user",      "content": "...", "timestamp": "..."}
{"role": "assistant", "content": "...", "timestamp": "..."}
{"role": "tool",      "name": "...",   "content": "...", "timestamp": "..."}
```

### 提取规则

- 优先考虑声明结论、决策或模式的助手回合
- 从高信号回合中提取用户意图；跳过低信息的后续信息
- 工具调用是上下文，不是主要知识 — 仅在结果包含可重用见解时提取
- 在打开单个记录之前，交叉引用 `sessions.json` 索引以获取会话名称/标签

### 关键隐私过滤器

会话记录可能包含注入的指令、工具有效负载和敏感文本。不要逐字导入。

- 移除 API 密钥、令牌、密码、凭证
- 除非相关且经用户批准，否则编辑私人标识符
- 总结；不要逐字引用原始记录

## 第 5 步：按主题聚类

不要为每个会话或每个 MEMORY.md 条目创建一个知识库页面。

- 按稳定主题（概念、工具、项目、技术）分组
- 将混合会话拆分为单独主题
- 跨日期和代理合并重复模式
- 当可用时，使用会话 `cwd` 或工作区路径推断项目范围

## 第 6 步：提炼到知识库页面

使用现有知识库约定路由提取的知识：

- 项目特定架构/流程 → `projects/<name>/...`
- 一般概念 → `concepts/`
- 重复技术/调试剧本 → `skills/`
- 工具/服务/框架 → `entities/`
- 跨会话模式 → `synthesis/`

对于每个受影响的项目，创建/更新 `projects/<name>/<name>.md`。

### 写作规则

- 提炼知识，而非编年史
- 除非日期上下文至关重要，否则避免“在日期 X 我们讨论了...”
- 在每个新/更新的页面上添加 `summary:` 前置内容（1-2 句话，≤ 200 字符）
- 为每个新页面添加置信度字段和生命周期字段：
  ```yaml
  base_confidence: 0.42
  lifecycle: draft
  lifecycle_changed: <ISO 日期今天>
  ```
  更新时保持 `lifecycle` 不变。
- 添加来源标记：
  - `^[extracted]` 当直接基于显式会话/内存内容时
  - `^[inferred]` 当跨多个会话合成模式时
  - `^[ambiguous]` 当会话冲突时
- 为每个更改的页面添加/更新 `provenance:` 前置内容混合

## 第 7 步：更新清单、记录和索引

### 更新 `.manifest.json`

对于每个处理的源文件：

- `ingested_at`, `size_bytes`, `modified_at`
- `source_type`: `openclaw_memory` | `openclaw_daily_note` | `openclaw_session` | `openclaw_dreams`
- `agent_id`: 代理目录名称（当适用时）
- `pages_created`, `pages_updated`

添加/更新顶级摘要块：

```json
{
  "openclaw": {
    "source_path": "~/.openclaw/",
    "last_ingested": "TIMESTAMP",
    "memory_updated_at": "TIMESTAMP",
    "daily_notes_ingested": 14,
    "sessions_ingested": 23,
    "pages_created": 6,
    "pages_updated": 18
  }
}
```

### 更新特殊文件

使用单个锁定调用更新 `index.md`、`log.md` 和 `hot.md`：

```bash
obsidian-wiki memory sync OPENCLAW_HISTORY_INGEST \
  memory=<memory> daily_notes=<daily_notes> sessions=<sessions> \
  pages_updated=<pages_updated> pages_created=<pages_created> \
  mode=<mode> \
  --takeaways "导入 OpenClaw MEMORY.md 和 14 份每日笔记；提取自动化模式和跨代理协调知识。"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令会获取锁定以防止并行写入者丢弃您的更新。`--takeaways` 是以前放在最近活动中的概念性摘要；
省略它以保留先前的摘要。

查看 `.skills/llm-wiki/references/MEMORY.md` 获取完整流程。

## 隐私和合规

- 提炼和合成；避免原始内存或记录转储
- 默认对看起来敏感的内容进行编辑
- 存储个人或敏感细节前先询问用户
- 对其他人的引用应最小化且目的明确

## 参考

查看 `references/openclaw-data-format.md` 获取字段级笔记和解析指南。

## QMD 在保险库写入后刷新

QMD 是搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写保险库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

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

或，当知道特定页面路径时：

```bash
${QMD_CLI:-qmd} get "qmd://$QMD_WIKI_COLLECTION/<page>.md" -l 5
```

记录以下之一：

- `QMD 刷新：update + embed + verified`
- `QMD 刷新：update 仅 + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
