# 记忆桥 — 跨工具知识浏览器

您正在帮助用户浏览和比较其 Obsidian 知识库，这些知识库是根据最初由哪个 AI 工具生成的进行筛选的。该知识库在 `.manifest.json` 中跟踪来源溯源，并在页面 `sources:` 前置中记录 — 这个技能将这种元数据以可导航的视图呈现出来。

## 开始前

1. **解析配置** — 遵循 `llm-wiki/SKILL.md` 中的配置解析协议（内联 `@name` 覆盖 → 向上遍历 CWD 查找 `.env` → 全局配置 → 提示设置）。这会提供 `OBSIDIAN_VAULT_PATH`。
2. 阅读 `$OBSIDIAN_VAULT_PATH/.manifest.json` — 这是决定什么工具生成了什么的权威来源。
3. 阅读 `$OBSIDIAN_VAULT_PATH/index.md` 获取页面标题和单行描述。

## 命令

解析用户的调用以确定模式：

| 调用 | 模式 |
|---|---|
| `/memory-bridge <工具>` | **浏览** — 列出所有来自 `<工具>` 的知识库页面 |
| `/memory-bridge <工具> "<主题>"` | **搜索** — 来自 `<工具>` 提及 `<主题>` 的页面 |
| `/memory-bridge diff` | **差异** — 每个工具独有的页面；重叠；盲点 |
| `/memory-bridge diff <工具-a> <工具-b>` | **差异** — 比较两个特定工具 |
| `/memory-bridge map` | **映射** — 完整的来源矩阵：每页 × 每个接触过它的工具 |

已识别的工具名称：`claude`、`codex`、`hermes`、`openclaw`、`copilot`、`pi`、`manual`（手写）、`ingest`（知识库导入文档）。

## 第 1 步：构建来源映射

读取 `.manifest.json`。对于每个来源条目，提取：
- `source_type` — 映射到工具名称：
  - `claude_conversation`、`claude_memory`、`claude_audit_log`、`claude_desktop_session` → `claude`
  - `codex_rollout`、`codex_index`、`codex_history` → `codex`
  - `hermes_memory`、`hermes_session` → `hermes`
  - `openclaw_memory`、`openclaw_daily_note`、`openclaw_session`、`openclaw_dreams` → `openclaw`
  - `copilot_session`、`copilot_checkpoint`、`copilot_transcript`、`copilot_memory_artifact` → `copilot`
  - `pi_session` → `pi`
  - `document` → `ingest`
  - 其他任何情况 → `manual`
- `pages_created` 和 `pages_updated` — 由这个来源生成的知识库页面

构建映射：

```
tool_pages = {
  "claude": set(pages created/updated by claude sources),
  "codex":  set(pages created/updated by codex sources),
  ...
}
```

如果多个工具对同一页做出了贡献，该页面可能会出现在多个工具的集合中。

## 第 2 步：执行模式

### 浏览模式

过滤 `tool_pages[<工具>]` 并以分组列表的形式呈现：

```
## 来自 <工具> 的知识 (<N> 页)

### 按类别
- concepts/ — N 页
- entities/ — N 页
- skills/   — N 页
...

### 页面
| 页面 | 类别 | 标签 | 最后更新 |
|------|----------|------|--------------|
| [[page-name]] | 概念 | tag1, tag2 | 2026-04-10 |
...
```

读取列出的页面的前置（grep 查找 `^(title|category|tags|updated):`） — 除非用户要求，否则不要读取完整的页面正文。

### 搜索模式

在过滤后的页面集合中运行：
```
rg -l "<主题>" <pages in tool set>
```
然后 grep 周围匹配的章节标题（`^##`）以提供上下文而不需要完整读取。以排名列表的形式呈现结果，并附带匹配的摘录。

### 差异模式

计算：
- `only_in_a` = `tool_pages[a]` − `tool_pages[b]`
- `only_in_b` = `tool_pages[b]` − `tool_pages[a]`
- `shared` = `tool_pages[a]` ∩ `tool_pages[b]`

如果没有给出特定工具，则成对比较所有工具（限制为重叠 >0 或独有页面以保持输出简洁）。

呈现：

```
## 记忆桥差异 — <工具-a> vs <工具-b>

### 仅在 <工具-a> 中 (<N> 页)
这些概念存在于您的知识库中，但来自 <工具-a> 会话，而 <工具-b> 从未接触过它们。
<来自 index.md 的一行描述列表>

### 仅在 <工具-b> 中 (<N> 页)
<列表>

### 共享 (<N> 页)
两个工具都为这些页面做出了贡献。
<列表 — 如果 ≤15 则显示；否则仅显示计数>

### 值得注意的差距
突出显示最有趣的非对称性 — 例如 "codex 有 12 页关于构建工具，而 claude 从未见过"。

### 映射模式

构建一个矩阵，显示每个页面和哪些工具接触过它。限制为 50 行；按贡献工具数量降序排序（最跨工具的页面优先 — 这些是最丰富的节点）。

```
| 页面 | claude | codex | hermes | copilot | pi |
|------|--------|-------|--------|---------|----|
| [[react-patterns]] | ✓ | ✓ | — | ✓ | — |
| [[rust-ownership]] | — | ✓ | — | — | ✓ |
```

## 第 3 步：启动 impl-validator（如果可用）

生成输出后，如果当前环境中可用 `impl-validator` 技能，则作为子代理启动它：

```
impl-validator check:
  目标: "根据来源工具浏览/差异知识库并揭示跨工具盲点"
  产物: [您刚刚生成的输出]
  检查：
    - 您是否正确解析了 .manifest.json 中的 source_type？
    - 页面计数是否合理（除非知识库为空，否则不为 0）？
    - 差异是否对称（a−b 和 b−a 是不相交的）？
    - 您是否在不需要时避免了读取完整页面正文？
```

在向用户展示输出之前应用它揭示的问题。

## 第 4 步：记录

追加到 `$OBSIDIAN_VAULT_PATH/log.md`：
```
- [TIMESTAMP] MEMORY-BRIDGE mode=<browse|search|diff|map> tool=<工具> pages_shown=N
```

## 输出约定

- 始终显示页面计数，以便用户可以校准每个工具的隔间中包含多少知识。
- 使用 `[[wikilinks]]` 进行页面引用（如果 `OBSIDIAN_LINK_FORMAT=markdown` 设置，则使用标准 Markdown 链接）。
- 在差异模式下，明确指出最*令人惊讶*的非对称性 — 那是用户来找的见解。
- 如果 `.manifest.json` 为空或缺失，请明确说明并建议首先运行 `/wiki-history-ingest`。
