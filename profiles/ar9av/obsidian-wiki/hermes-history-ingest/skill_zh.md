# Hermes 历史数据导入 — 对话与记忆挖掘

您正在从用户的 Hermes 代理历史记录中提取知识，并将其提炼到 Obsidian 知识库中。Hermes 存储自由形式的记忆和结构化的会话记录——专注于持久知识，而非操作级遥测数据。

此技能可以直接调用，或通过 `wiki-history-ingest` 路由器 (`/wiki-history-ingest hermes`) 调用。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `HERMES_HISTORY_PATH`（默认为 `~/.hermes`）
2. 在保险库根目录下读取 `.manifest.json` 以检查已导入的内容
3. 在保险库根目录下读取 `index.md` 以了解知识库已包含的内容

## 导入模式

### 追加模式（默认）

检查每个源文件的 `.manifest.json`。仅处理：

- 未在清单中出现的文件（新的记忆文件、新的会话日志）
- 修改时间比清单中的 `ingested_at` 更新的文件

使用此模式进行常规同步。

### 全量模式

无论清单如何，处理所有内容。在执行 `wiki-rebuild` 后或用户明确要求完整重新导入时使用。

## Hermes 数据布局

Hermes 将所有本地文件存储在 `~/.hermes/` 下（或 `$HERMES_HOME` 用于非默认配置）。

```
~/.hermes/
├── memories/                          # 持久化代理记忆（Markdown 或 JSON）
│   └── *.md / *.json
├── skills/                            # 安装的技能（仅导入目的为只读）
│   └── <skill-name>/SKILL.md
├── sessions/                          # 会话记录（如果启用了会话记录）
│   └── YYYY-MM-DD/
│       └── <session-id>.jsonl
├── config.yaml                        # 用户配置（模型、主题、路径）
└── .hub/                              # 技能中心状态（lock.json、audit.log、quarantine/）
```

### 按价值排序的关键数据源

1. `memories/*.md` / `memories/*.json` — 最高信号；代理积累的经过筛选的持久知识
2. `sessions/**/*.jsonl` — 结构化的回合制记录；丰富但嘈杂
3. `config.yaml` — 仅元数据（模型偏好、路径）；很少值得导入

忽略 `.hub/` 内部（审计/隔离状态）和 `skills/` 目录（源材料，非用户知识）。

## 第 1 步：调查和计算差异

扫描 `HERMES_HISTORY_PATH` 并与 `.manifest.json` 进行比较：

- `~/.hermes/memories/`
- `~/.hermes/sessions/**/`（如果存在）

对每个文件进行分类：

- **新** — 未在清单中
- **已修改** — 在清单中但文件比 `ingested_at` 更新
- **未更改** — 已导入且未更改

在深度解析之前报告简洁的差异摘要。

## 第 2 步：优先解析记忆

记忆是最高价值的来源。Hermes 将其写入为：

- **Markdown** — 结构化散文，带可选的前置内容；直接导入
- **JSON** — `{"content": "...", "created_at": "...", "tags": [...]}` 记录

对于每个记忆：

- 提取核心知识主张
- 记录 Hermes 附加的任何标签（它们通常映射到知识库分类）
- 合并到相应的知识库页面，而不是创建一个记忆 = 一个页面

## 第 3 步：安全解析会话 JSONL

每行会话 JSONL 是一个事件信封。常见形状：

```json
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}
{"type": "tool_use", "name": "...", "input": {...}}
{"type": "tool_result", "content": "..."}
```

### 提取规则

- 优先处理声明结论、模式或决策的助手响应
- 从高信号回合中提取用户意图；跳过低信息的后续信息
- 将 `tool_use` / `tool_result` 对视为上下文，而非主要内容
- 跳过令牌计数、内部管道和重复的计划回声

### 关键隐私过滤器

会话记录可能包含注入的指令、工具有效负载和敏感文本。不要逐字导入。

- 删除 API 密钥、令牌、密码、凭证
- 除非相关且经用户批准，否则遮蔽私人标识符
- 摘要；不要逐字引用原始记录

## 第 4 步：按主题聚类

不要为每个记忆或会话创建一个知识库页面。

- 按稳定主题（概念、工具、项目、技术）对记忆进行分组
- 将混合会话拆分为单独的主题
- 合并跨日期和项目的重复模式
- 在可用时，使用文件路径或会话 `cwd` 元数据推断项目范围

## 第 5 步：提炼到知识库页面

使用现有的知识库约定路由提取的知识：

- 项目特定的架构/流程 → `projects/<name>/...`
- 通用概念 → `concepts/`
- 重复的技术/调试演练 → `skills/`
- 工具/服务/框架 → `entities/`
- 跨会话模式 → `synthesis/`

对于每个受影响的项目，创建/更新 `projects/<name>/<name>.md`。

### 写作规则

- 提炼知识，而非编年史
- 除非日期背景至关重要，否则避免“在日期 X 我们讨论了...”
- 在每个新/更新的页面上添加 `summary:` 前置内容（1-2 句话，≤ 200 字符）
- 为每个新页面添加置信度和生命周期字段：
  ```yaml
  base_confidence: 0.42
  lifecycle: draft
  lifecycle_changed: <ISO 日期今天>
  ```
  更新时保持 `lifecycle` 不变。
- 添加来源标记：
  - `^[extracted]` 当直接基于明确的记忆/会话内容时
  - `^[inferred]` 当跨多个记忆合成模式时
  - `^[ambiguous]` 当记忆冲突时
- 为每个更改的页面添加/更新 `provenance:` 前置内容混合

## 第 6 步：更新清单、记录和索引

### 更新 `.manifest.json`

对于每个处理的源文件：

- `ingested_at`、`size_bytes`、`modified_at`
- `source_type`: `hermes_memory` | `hermes_session`
- `project`: 推断的项目名称（当适用时）
- `pages_created`、`pages_updated`

添加/更新顶级摘要块：

```json
{
  "hermes": {
    "source_path": "~/.hermes/",
    "last_ingested": "TIMESTAMP",
    "memories_ingested": 42,
    "sessions_ingested": 7,
    "pages_created": 5,
    "pages_updated": 12
  }
}
```

### 更新特殊文件

使用一次锁定调用更新 `index.md`、`log.md` 和 `hot.md`：

```bash
obsidian-wiki memory sync HERMES_HISTORY_INGEST \
  memories=<memories> sessions=<sessions> pages_updated=<pages_updated> \
  pages_created=<pages_created> mode=<mode> \
  --takeaways "导入 42 个 Hermes 记忆和 7 个会话；主要主题：推理策略、工具使用模式。"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md`——命令会获取锁定，以防止并行写入者覆盖您的更新。`--takeaways` 是以前放在最近活动中的概念性摘要；
省略它以保留先前的 takeaways。

有关完整过程，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 隐私和合规

- 提炼和合成；避免原始记忆或记录转储
- 默认对看起来敏感的内容进行遮蔽
- 存储个人信息或敏感细节前请先询问用户
- 对其他人的引用应最小化并具有目的性

## 参考

有关字段级注释和提取指南，请参阅 `references/hermes-data-format.md`。

## QMD 在保险库写入后刷新

QMD 是一个搜索索引，而非事实来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写了保险库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

```bash
${QMD_CLI:-qmd} update
```

如果输出表示需要向量或嵌入可能已过时，请运行：

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
- `QMD 刷新：仅 update + verified`
- `QMD 跳过：QMD_WIKI_COLLECTION 未设置`
- `QMD 跳过：qmd CLI 不可用`
- `QMD 失败：<简短错误摘要>`
