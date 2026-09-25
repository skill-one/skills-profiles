# Wiki Agent — 针对性跨代理历史记录搜索 + 整合

您正在进行**查询驱动的针对性整合**，从特定 AI 代理的原始对话历史记录中提取信息。用户当前通常在*其他*代理上工作，并希望从另一个代理的过去会话中提取上下文。

这不是批量整合。您需要找到关于特定主题的会话，提取相关的内容块，将其提炼到维基中，并返回用户可以立即采取行动的综合答案。

## 命令路由

解析调用以确定目标代理和可选查询：

| 命令 | 目标 | 示例 |
|---|---|---|
| `/wiki-claude [查询]` | Claude 代码历史记录 | `/wiki-claude "如何设置认证中间件"` |
| `/wiki-codex [查询]` | Codex CLI 历史记录 | `/wiki-codex "Rust 拥有模式"` |
| `/wiki-hermes [查询]` | Hermes 代理历史记录 | `/wiki-hermes "内存架构"` |
| `/wiki-openclaw [查询]` | OpenClaw 历史记录 | `/wiki-openclaw "项目规划方法"` |
| `/wiki-copilot [查询]` | Copilot 聊天历史记录 | `/wiki-copilot "API 路由的测试策略"` |
| `/wiki-pi [查询]` | Pi 代理历史记录 | `/wiki-pi "如何重构认证模块"` |

如果没有提供查询，则默认为**最近会话模式**：从该代理整合最后 5 个未处理的会话并返回找到的内容摘要。这相当于仅针对该代理的 `wiki-history-ingest`。

## 开始前

**编写配置文件**：在起草或重写自然语言 Markdown 之前，请阅读并应用 `llm-wiki/SKILL.md` 中的 `Writing Profile Resolution` 部分。框架模式、来源、安全性和特定操作要求优先。

`WRITING.md` 偏好仅适用于新起草或重写的自然语言 Markdown；保留源内容和结构化记录。

1. **解决配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解决协议（内联 `@name` 覆盖 → 沿 CWD 向上查找 `.env` → 全局配置 → 提示设置）。这会给出 `OBSIDIAN_VAULT_PATH`。
2. 读取 `$OBSIDIAN_VAULT_PATH/.manifest.json` → 了解已经整合的内容。
3. 如果存在 `$OBSIDIAN_VAULT_PATH/hot.md`，请读取它 → 了解最近的维基活动。

---

## 第 1 步：定位代理的历史记录根目录

| 代理 | 默认路径 | 配置覆盖 |
|---|---|---|
| `claude` | `~/.claude` + `~/Library/Application Support/Claude/local-agent-mode-sessions/` | `.env` 中的 `CLAUDE_HISTORY_PATH` |
| `codex` | `~/.codex` | `.env` 中的 `CODEX_HISTORY_PATH` |
| `hermes` | `~/.hermes` | 环境变量或 `.env` 中的 `HERMES_HOME` |
| `openclaw` | `~/.openclaw` | `.env` 中的 `OPENCLAW_HOME` |
| `copilot` | `~/.copilot` | `.env` 中的 `COPILOT_HISTORY_PATH` |
| `pi` | `~/.pi/agent/sessions` | `.env` 中的 `PI_HISTORY_PATH` |

如果历史记录根目录不存在，请停止并告知用户： "在 `<path>` 处未找到 `<agent>` 历史记录。您是否在这个机器上运行过 `<agent>`？您可以在 `.env` 中使用 `<CONFIG_VAR>` 设置自定义路径。"

---

## 第 2 步：构建会话清单

为每个代理使用**最便宜的索引源**，直到知道哪些会话相关，才打开会话文件。

### Claude
```
主要索引：   ~/.claude/projects/  (目录 = projects，文件 = sessions)
会话文件：   ~/.claude/projects/*/*.jsonl
桌面索引：   find ~/Library/Application Support/Claude/local-agent-mode-sessions -name "local_*.json"
信号字段：   sessionId, cwd, startedAt, title (在 local_*.json 中)
```
构建会话列表：`{path, project_dir, modified_at, already_ingested}`。

### Codex
```
主要索引：   ~/.codex/session_index.jsonl
会话文件：   ~/.codex/sessions/**/rollout-*.jsonl
信号字段：   thread_id, name/title, updated_at (在 session_index.jsonl 中)
```
将 `session_index.jsonl` 作为清单读取。每行：`{thread_id, name, updated_at}`。通过匹配目录名称将 thread IDs 映射到 rollout 文件。

### Hermes
```
主要索引：   ~/.hermes/memories/*.md  (快速扫描)
会话文件：   ~/.hermes/sessions/**/*.jsonl
信号字段：   文件名，记忆标题，每个记忆的前 3 行
```
首先扫描记忆文件名（它们通常按主题命名）。如果需要，则回退到会话列表。

### OpenClaw
```
主要索引：   ~/.openclaw/workspace/memory/MEMORY.md  (结构化长期记忆)
每日笔记：     ~/.openclaw/workspace/memory/YYYY-MM-DD.md
会话索引：   ~/.openclaw/agents/*/sessions/sessions.json
会话文件：   ~/.openclaw/agents/*/sessions/*.jsonl
```
首先读取 `MEMORY.md` 部分——它是所有内容的预编译摘要。每日笔记提供时效性信号。

### Copilot
```
主要索引：   会话文件名 / 目录列表
会话文件：   因客户端而异（VS Code: ~/.copilot/sessions/*.jsonl 或类似）
信号字段：   会话时间戳，文件名
```

### Pi
```
主要索引：   ~/.pi/agent/sessions/--<cwd>--/ 目录
会话文件：   ~/.pi/agent/sessions/--<cwd>--/<timestamp>_<uuid>.jsonl
信号字段：   cwd（从目录名解码），session_info.name，文件名中的时间戳
```
首先扫描会话目录。解码 `--<cwd>--` 以获取工作目录。读取第一行（会话标题）和任何 `session_info` 条目以获取会话名称。没有单独的索引文件——文件系统就是索引。

---

## 第 3 步：根据查询对会话进行评分

如果提供了查询，则在不打开完整会话文件的情况下对清单中的每个会话进行评分：

1. **名称/标题匹配**——会话名称或线程标题是否包含查询术语？评分：+3
2. **cwd/项目匹配**——工作目录是否暗示正确的项目？评分：+2
3. **时效性**——应用指数时间衰减，半衰期为 90 天，作为匹配分数的乘数，而不是添加到匹配分数上：

   ```
   base  = name_match(3) + cwd_match(2)
   score = base * (0.35 + 0.65 * 0.5 ** (age_days / 90))
   ```

   0.35 的地板是故意的：一个与查询完全匹配的旧会话必须比一个几乎匹配的新会话排名更高，否则该技能永远无法回答“我第一次如何解决这个问题？” 这与 `session-brain` 使用的衰减相同，因此这两个技能的排名一致。
4. **已整合**——如果此会话以前已整合并且维基页面已经涵盖了查询（检查 `hot.md` + `index.md`），则标记为“已涵盖”，但仍然显示在结果中

根据分数选择**前 3–5 个会话**。如果没有提供查询，则选择 5 个最近未处理的会话。

---

## 第 4 步：提取相关内容块

打开每个选定的会话文件并仅提取与查询相关的內容。**如果会话很大，请不要读取完整会话——使用针对性提取。**

### 每个代理的提取策略

**Claude**（JSONL 对话）：
- 每行：`{role, content, timestamp, ...}`
- 搜索：`rg -i "<query terms>" <session.jsonl>` 以找到相关行
- 提取：每个命中周围的对话窗口（每个命中前 10 行 + 后 20 行）
- 特殊信号：工具调用（Read/Write/Bash/Edit）显示实际执行的内容——即使没有关键词匹配，如果它们在相关窗口中，也要提取这些

**Codex**（rollout JSONL）：
- 每行：`{type: "session_meta|turn_context|event_msg|response_item", ...}`
- 筛选到 `type: "event_msg"`（用户回合）和 `type: "response_item"`（模型输出）
- 搜索：`rg -i "<query terms>" <rollout.jsonl>`
- 提取：匹配的回合及其父上下文（匹配之前的 `turn_context`）
- 跳过：`session_meta` 事件（操作元数据，不是知识）

**Hermes**（记忆文件 + 会话 JSONL）：
- 对于记忆文件：读取完整文件（它们很短——每个通常 <500 字）
- 对于会话 JSONL：`rg -i "<query terms>"` + 周围窗口
- 标题匹配的记忆文件 → 读取完整；其他 → 仅 grep

**OpenClaw**（MEMORY.md + 每日笔记 + 会话 JSONL）：
- `MEMORY.md`：grep 包含查询术语的节标题 → 提取该节
- 每日笔记：grep 最近 30 天的查询术语 → 提取匹配的段落
- 会话 JSONL：与 Claude 相同的 grep 窗口方法
- 优先 `MEMORY.md`/每日笔记而不是会话 JSONL（它们是预综合的）

**Copilot**（会话 JSONL）：
- 与 Claude 相同的 grep 窗口方法
- 如果可用，查找检查点文件（预总结）

**Pi**（带树布局的结构化 JSONL）：
- 每行是树条目：`{type, id, parentId, timestamp, message?, ...}`
- 构建活动分支：通过 `id` 映射条目，找到叶（没有子项的最后一个条目），沿 `parentId` 向根行走
- 搜索：`rg -i "<query terms>" <session.jsonl>` 以找到匹配的条目
- 提取：匹配的条目及其活动分支上的祖先（跟随父链）
- 特殊信号：助手消息中的 `toolCall` 块显示实际执行的内容——即使没有关键词匹配，如果它们在相关窗口中，也要提取这些
- 优先 `compaction` 和 `branch_summary` 条目（如果可用）——它们是预综合的摘要
- 跳过 `thinking` 内容块（噪音）和 `model_change` / `thinking_level_change` 条目

---

## 第 5 步：将内容块提炼为维基页面

对于每个提取的内容块，确定其在维基中的位置：

1. **检查维基页面是否已涵盖此内容**——grep `index.md` 和页面前缀，如果已涵盖主题，则更新现有页面而不是创建新页面。
2. **确定类别**使用标准规则（来自 `llm-wiki/SKILL.md`）：
   - 技术 / 如何操作 → `skills/`
   - 抽象概念 / 模式 → `concepts/`
   - 工具 / 库 / 人 → `entities/`
   - 跨领域见解 → `synthesis/`
3. **编写或更新页面**，使用所需的前缀：
   ```yaml
   ---
   title: <主题>
   category: skill|concept|entity|synthesis
   tags: [tag1, tag2]
   sources: [<agent>://<路径/to/session>]
   created: <日期>
   updated: <日期>
   confidence: high|medium|low
   lifecycle: stable|draft
   ---
   ```
   使用代理前缀设置 `sources`，以便 `memory-bridge` 可以稍后找到它。
4. **添加交叉链接**到在 `index.md` 中找到的相关维基页面。

提炼规则（与其他整合技能相同）：
- 提取持久知识，而不是操作遥测
- 每个维基页面对应一个概念，而不是每个会话一个页面
- 合并到现有页面而不是重复
- 保留信号：做出的决定，发现的模式，有效的方法，解释的错误

---

## 第 6 步：返回综合答案

整合后，立即从新整合的 + 现有维基内容中综合并返回答案：

```
## 从 <agent> 历史记录："<query>"

**在** <N> 个会话中找到**（<会话名称/标题>）**

**关键见解：**
<Synthesized answer — 3–5 个最有用的知识要点>

**更新的/创建的维基页面：**
- [[page-name]] — <添加的内容>
- [[page-name]] — <添加的内容>

**整合的会话：**
| 会话 | 日期 | 相关性 |
|---------|------|-----------|
| <name>  | <date> | <为什么选择该会话的一句话> |

**差距：** <会话未涵盖但可能相关的主题>
```

如果提供了查询但未找到相关会话，请明确说明： "在 `<agent>` 历史记录中未找到关于 '<query>' 的会话。最近的会话涵盖了：<列出最后 3 个会话的主题>。"

---

## 第 7 步：更新跟踪文件

更新每个已处理的会话文件文件的 `.manifest.json`：
```json
{
  "<path>": {
    "ingested_at": "<now>",
    "source_type": "<agent>_conversation",
    "modified_at": "<file mtime>",
    "pages_created": [...],
    "pages_updated": [...]
  }
}
```

一个锁定调用更新日志、索引和热缓存：

```bash
obsidian-wiki memory sync WIKI-AGENT \
  agent=<agent> query="<query>" \
  sessions_searched=<N> sessions_ingested=<M> \
  pages_created=<X> pages_updated=<Y> \
  --takeaways "<一句话：提取了什么以及它如何改变>"
```

永远不要手动编辑 `index.md`、`log.md` 或 `hot.md`——命令会获取锁，以防止并行写入者丢失您的更新。

查看 `.skills/llm-wiki/references/MEMORY.md` 以获取完整流程。

---

## 跨代理使用模式

这是该技能设计的主要用例：

**"我在 Codex 上。我在 Claude 中解决了关于 X 的什么？"**
→ `/wiki-claude "X"` — 找到关于 X 的 Claude 会话，整合它们，返回答案

**"我上周在 Hermes 上解决了一个错误。我现在需要在 Claude Code 中获取该上下文。"**
→ `/wiki-hermes "错误描述"` — 查找并整合 Hermes 会话

**"我在所有我的工具中尝试了 X 的所有方法是什么？"**
→ 依次运行 `/wiki-claude "X"`、`/wiki-codex "X"`、`/wiki-hermes "X"`——每个代理整合其切片，维基积累跨代理的图景，然后 `/memory-bridge diff` 显示每个工具的独特贡献

**没有查询——只是“让我了解最近的 Codex 工作”**
→ `/wiki-codex` — 整合最后 5 个 Codex 会话并返回摘要

**"我在 Claude Code 上。我在 Pi 中解决了关于 X 的什么？"**
→ `/wiki-pi "X"` — 找到关于 X 的 Pi 会话，整合它们，返回答案

**没有查询——只是“让我了解最近的 Pi 工作”**
→ `/wiki-pi` — 整合最后 5 个 Pi 会话并返回摘要

## QMD 在 Vault 写入后刷新

QMD 是一个搜索索引，不是真相来源。如果 `$QMD_WIKI_COLLECTION` 为空或未设置，跳过此步骤。仅在此技能写入或重写 Vault Markdown 后运行它。如果 QMD 刷新失败，不要回滚 Vault 更改；单独报告 QMD 状态。

如果设置了 `$QMD_CLI`，请使用它；否则使用 `qmd`。

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
