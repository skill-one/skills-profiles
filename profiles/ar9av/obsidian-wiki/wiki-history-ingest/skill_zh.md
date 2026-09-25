# 统一历史数据导入路由器

这是一个仅用于**历史数据源**的瘦路由器。它不会取代 `wiki-ingest` 用于文档。

## 子命令

如果用户调用 `/wiki-history-ingest <目标>`（或等效文本命令），直接分发：

| 子命令 | 路由至 |
|---|---|
| `claude` | `claude-history-ingest` |
| `copilot` | `copilot-history-ingest` |
| `codex` | `codex-history-ingest` |
| `hermes` | `hermes-history-ingest` |
| `openclaw` | `openclaw-history-ingest` |
| `pi` | `pi-history-ingest` |
| `auto` | 使用以下规则根据上下文推断 |

## 路由规则

1. 如果用户明确说明 `claude`、`copilot`、`codex`、`hermes`、`openclaw` 或 `pi`，直接路由。
2. 如果用户提供路径/来源：
   - `~/.claude` 或 Claude 内存/会话 JSONL 文件 -> `claude-history-ingest`
   - `~/.copilot`、`session-store.db`、VS Code copilot-chat 转录 -> `copilot-history-ingest`
   - `~/.codex` 或 rollout/会话索引文件 -> `codex-history-ingest`
   - `~/.hermes` 或 Hermes 内存/会话文件 -> `hermes-history-ingest`
   - `~/.openclaw` 或 OpenClaw MEMORY.md/会话 JSONL 文件 -> `openclaw-history-ingest`
   - `~/.pi/agent/sessions` 或 Pi 会话 JSONL 文件 -> `pi-history-ingest`
3. 如果存在歧义，询问一个简短的澄清：
   - "我应该导入 `claude`、`copilot`、`codex`、`hermes`、`openclaw` 或 `pi` 的历史数据吗？"

## 执行契约

- 路由后，精确执行目标技能的工作流。
- 不要在此文件中重复目标逻辑。
- 将清单/索引/日志更新语义留给目标技能。

## 用户体验规范

- 使用 `wiki-ingest` 用于**文档/内容来源**
- 使用 `wiki-history-ingest` 用于**代理历史数据来源**

示例：

- `/wiki-history-ingest claude`
- `/wiki-history-ingest copilot`
- `/wiki-history-ingest codex`
- `/wiki-history-ingest hermes`
- `/wiki-history-ingest openclaw`
- `/wiki-history-ingest pi`
- `$wiki-history-ingest claude`（使用 `$skill` 调用的代理）
- `$wiki-history-ingest copilot`
