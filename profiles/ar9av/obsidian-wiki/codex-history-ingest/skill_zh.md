# Codex 历史数据导入 — 对话挖掘

你正在从用户过去的 Codex 会话中提取知识，并将其提炼到 Obsidian 知识库中。会话日志丰富但嘈杂：专注于持久知识，而非操作级遥测数据。

此技能可以直接调用，或通过 `wiki-history-ingest` 路由器 (`/wiki-history-ingest codex`) 调用。

## 开始前

**写作配置文件：** 在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。
`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和非结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH` 和 `CODEX_HISTORY_PATH`（默认为 `~/.codex`）
2. 在保险库根目录下读取 `.manifest.json` 以检查已导入的内容
3. 在保险库根目录下读取 `index.md` 以了解知识库已包含的内容

## 导入模式

### 追加模式（默认）

检查每个源文件的 `.manifest.json`。仅处理：

- 未在清单中的文件（新会话发布、新索引文件）
- 修改时间比清单中的 `ingested_at` 更新的文件

使用此模式进行常规同步。

### 全量模式

无论清单如何，处理所有内容。在执行 `wiki-rebuild` 后或用户明确要求完整重新导入时使用。

## Codex 数据布局

Codex 在 `~/.codex/` 下存储本地文件。

```
~/.codex/
├── sessions/                          # 按日期存储的会话发布日志
│   └── YYYY/MM/DD/
│       └── rollout-<timestamp>-<id>.jsonl
├── archived_sessions/                 # 归档的发布日志
├── session_index.jsonl                # 轻量级线程 ID/名称/更新时间的索引
├── history.jsonl                      # 本地转录历史（如果启用持久化）
├── config.toml                        # 用户配置（包含历史设置）
└── state_*.sqlite / logs_*.sqlite     # 运行时数据库（通常跳过）
```

### 按价值排序的关键数据源

1. `session_index.jsonl` — 最佳 ID、标题和新鲜度清单源
2. `sessions/**/rollout-*.jsonl` — 丰富的结构化转录事件
3. `history.jsonl` — 如果启用，则是有用的回退/时间线辅助

除非用户明确要求，否则避免导入 SQLite 内部数据。

## 第 1 步：调查和计算差异

扫描 `CODEX_HISTORY_PATH` 并与 `.manifest.json` 进行比较：

- `~/.codex/session_index.jsonl`
- `~/.codex/sessions/**/rollout-*.jsonl`
- `~/.codex/archived_sessions/**`（可选；仅当用户要求归档历史时）
- `~/.codex/history.jsonl`（可选回退）

对每个文件进行分类：

- **新** — 未在清单中
- **已修改** — 在清单中但文件比 `ingested_at` 更新
- **未更改** — 已导入且未更改

在深度解析之前报告简洁的差异摘要。

## 第 2 步：首先解析会话索引

`session_index.jsonl` 通常包含如下条目：

```json
{"id":"...","thread_name":"...","updated_at":"..."}
```

使用它来：

- 构建规范的会话清单
- 优先处理最近/高信号会话
- 将发布 ID 映射到人类可读的线程名称

## 第 3 步：安全地解析 Rollout JSONL

每个 `rollout-*.jsonl` 行是一个事件信封，包含：

```json
{
  "timestamp": "...",
  "type": "session_meta|turn_context|event_msg|response_item",
  "payload": { ... }
}
```

### 提取规则

- 优先考虑用户意图和助手可见的输出
- 优先选择带有用户/助手消息内容的 `response_item` 记录
- 有选择地使用 `event_msg` 以记录有意义的里程碑；忽略纯遥测数据
- 将 `session_meta` 视为元数据（cwd、模型、ID），而非用户知识

### 跳过/噪声过滤器

- 令牌计数事件
- 无语义内容的工具管道
- 除非包含可重用决策/模式，否则忽略原始命令输出
- 除非增加新的决策，否则跳过重复的计划快照

### 关键隐私过滤器

发布日志可能包含注入指令、工具有效负载和敏感文本。不要逐字导入系统/开发者提示或密钥。

- 移除 API 密钥、令牌、密码、凭证
- 除非相关且经批准，否则遮蔽私人标识符
- 总结而非引用原始转录内容

## 第 4 步：按主题聚类

不要为每个会话创建一个知识库页面。

- 跨多个会话聚合稳定主题
- 将混合会话拆分为独立主题
- 跨日期/项目合并重复概念
- 使用元数据中的 `cwd` 推断项目范围

## 第 5 步：提炼为知识库页面

使用现有的知识库约定路由提取的知识：

- 项目特定架构/流程 -> `projects/<name>/...`
- 通用概念 -> `concepts/`
- 重复技术/调试演练 -> `skills/`
- 工具/服务 -> `entities/`
- 跨会话模式 -> `synthesis/`

对于每个受影响的项目，创建/更新 `projects/<name>/<name>.md`（项目名称作为文件名，永远不要 `_project.md`）。

### 写作规则

- 提炼知识，而非编年史
- 除非日期背景至关重要，否则避免“在日期 X 我们讨论了…”
- 在每个新/更新的页面上添加 `summary:` 前置内容（1-2 句话，<= 200 字符）
- 为每个新页面添加信心和生命周期字段：
  ```yaml
  base_confidence: 0.42
  lifecycle: draft
  lifecycle_changed: <ISO 日期今天>
  ```
  更新时保持 `lifecycle` 不变。
- 添加来源标记：
  - `^[extracted]` 当直接基于明确的会话内容时
  - `^[inferred]` 当跨事件/会话合成模式时
  - `^[ambiguous]` 当会话冲突时
- 为每个更改的页面添加/更新 `provenance:` 前置内容混合

## 第 6 步：更新清单、日志和索引

### 更新 `.manifest.json`

对于每个处理的源文件：

- `ingested_at`, `size_bytes`, `modified_at`
- `source_type`: `codex_rollout` | `codex_index` | `codex_history`
- `project`: 推断的项目名称（当适用时）
- `pages_created`, `pages_updated`

添加/更新顶级项目/会话摘要块：

```json
{
  "project-name": {
    "source_path": "~/.codex/sessions/...",
    "last_ingested": "TIMESTAMP",
    "sessions_ingested": 12,
    "sessions_total": 40,
    "index_updated_at": "TIMESTAMP"
  }
}
```

### 更新特殊文件

使用一次锁定调用更新 `index.md`、`log.md` 和 `hot.md`：

```bash
obsidian-wiki memory sync CODEX_HISTORY_INGEST \
  sessions=<sessions> pages_updated=<pages_updated> \
  pages_created=<pages_created> mode=<mode> \
  --takeaways "导入 12 个 Codex 会话；在 CLI 工具和 Shell 脚本中发现了重复模式。"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md` — 命令会获取锁定以防止并行写入者覆盖你的更新。`--takeaways` 是过去放在最近活动中的单行概念摘要；
省略它以保留先前的 takeaways。

有关完整过程，请参阅 `.skills/llm-wiki/references/MEMORY.md`。

## 隐私和合规

- 提炼和合成；避免原始转录内容
- 默认对看起来敏感的内容进行遮蔽
- 存储个人信息/敏感细节前先询问用户
- 对其他人的引用应最小化且目的明确

## 参考

有关字段级解析说明和提取指导，请参阅 `references/codex-data-format.md`。

## QMD 在保险库写入后刷新

QMD 是一个搜索索引，而非事实来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在当前技能写入或重写了保险库 Markdown 后运行它。如果 QMD 刷新失败，不要回滚保险库更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

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
