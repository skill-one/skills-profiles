# session-logs

搜索存储在会话 JSONL 文件中的完整对话历史记录。当用户引用旧的/父对话或询问之前说过什么时使用此功能。

## 触发条件

当用户询问之前的聊天记录、父对话或记忆文件中不存在的背景信息时，使用此技能。

## 位置

会话日志存储在活动状态目录下：
`$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`（默认：`~/.openclaw/agents/<agentId>/sessions/`）。
使用系统提示符运行行中的 `agent=<id>` 值。

- **`sessions.json`** - 会话键到会话 ID 的索引映射
- **`<会话-id>.jsonl`** - 每个会话的完整对话记录
- **`<会话-id>.jsonl.reset.<时间戳>Z`** - 通过 `/new` 或 `/reset` 归档的记录
- **`<会话-id>.jsonl.deleted.<时间戳>Z`** - 会话被删除时归档的记录

搜索历史记录时，也要包含归档（`.reset.*`，`.deleted.*`）变体——它们仍然包含真实的对话内容。下面的 plain-glob 示例仅捕获活动的 `*.jsonl` 文件；当您需要完整回忆时，请使用“包含归档记录”片段。

## 结构

每个 `.jsonl` 文件包含以下消息：

- `type`: "session"（元数据）或 "message"
- `timestamp`: ISO 时间戳
- `message.role`: "user"、"assistant" 或 "toolResult"
- `message.content[]`: 文本、思考或工具调用（过滤 `type=="text"` 以获取人类可读的内容）
- `message.usage.cost.total`: 每条回复的成本

## 常见查询

### 包含归档记录（`.reset.*`，`.deleted.*`）

```bash
# Bash 辅助工具，发出所有可搜索的会话记录路径——活动和归档的。
# 本地保存和恢复 `nullglob`，以免干扰调用者的 shell 选项。
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"
list_session_transcripts() {
  local _nullglob_state
  _nullglob_state=$(shopt -p nullglob 2>/dev/null)
  shopt -s nullglob
  for f in "$SESSION_DIR"/*.jsonl \
           "$SESSION_DIR"/*.jsonl.reset.*Z \
           "$SESSION_DIR"/*.jsonl.deleted.*Z; do
    [ -f "$f" ] && printf '%s\n' "$f"
  done
  eval "$_nullglob_state"
}
```

如果您需要包含归档会话，请使用 `list_session_transcripts`（或等效的 `find` 调用）替换下面显示的 plain `*.jsonl` 通配符：

```bash
find "$SESSION_DIR" -maxdepth 1 -type f \
  \( -name '*.jsonl' -o -name '*.jsonl.reset.*Z' -o -name '*.jsonl.deleted.*Z' \) -print
```

### 按日期和大小列出所有会话

```bash
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"
for f in "$SESSION_DIR"/*.jsonl; do
  date=$(head -1 "$f" | jq -r '.timestamp' | cut -dT -f1)
  size=$(ls -lh "$f" | awk '{print $5}')
  echo "$date $size $(basename $f)"
done | sort -r
```

_提示:_ 将 `for f in ...` 行替换为对 `list_session_transcripts`（见上面的片段）的 `while`-read，当您还想在列表中包含 `.reset` / `.deleted` 文件时。`while`-read 模式对包含空格或其他 IFS 字符的路径是安全的：

```bash
while IFS= read -r f; do
  date=$(head -1 "$f" | jq -r '.timestamp' | cut -dT -f1)
  size=$(ls -lh "$f" | awk '{print $5}')
  echo "$date $size $(basename "$f")"
done < <(list_session_transcripts) | sort -r
```

### 查找特定日期的会话

```bash
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"
for f in "$SESSION_DIR"/*.jsonl; do
  head -1 "$f" | jq -r '.timestamp' | grep -q "2026-01-06" && echo "$f"
done
```

### 从会话中提取用户消息

```bash
jq -r 'select(.message.role == "user") | .message.content[]? | select(.type == "text") | .text' <会话>.jsonl
```

### 在助手回复中搜索关键词

```bash
jq -r 'select(.message.role == "assistant") | .message.content[]? | select(.type == "text") | .text' <会话>.jsonl | rg -i "关键词"
```

### 获取会话的总成本

```bash
jq -s '[.[] | .message.usage.cost.total // 0] | add' <会话>.jsonl
```

### 每日成本摘要

```bash
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"
for f in "$SESSION_DIR"/*.jsonl; do
  date=$(head -1 "$f" | jq -r '.timestamp' | cut -dT -f1)
  cost=$(jq -s '[.[] | .message.usage.cost.total // 0] | add' "$f")
  echo "$date $cost"
done | awk '{a[$1]+=$2} END {for(d in a) print d, "$"a[d]}' | sort -r
```

### 统计会话中的消息和令牌数量

```bash
jq -s '{
  messages: length,
  user: [.[] | select(.message.role == "user")] | length,
  assistant: [.[] | select(.message.role == "assistant")] | length,
  first: .[0].timestamp,
  last: .[-1].timestamp
}' <会话>.jsonl
```

### 工具使用分析

```bash
jq -r '.message.content[]? | select(.type == "toolCall") | .name' <会话>.jsonl | sort | uniq -c | sort -rn
```

### 在所有会话中搜索短语

```bash
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"

# 仅活动会话：
rg -l "短语" "$SESSION_DIR"/*.jsonl

# 活动会话 + 归档（`.reset.*`，`.deleted.*`）—— 当检查可能已被压缩/重置/删除的内容时使用：
rg -l "短语" "$SESSION_DIR"/*.jsonl \
               "$SESSION_DIR"/*.jsonl.reset.*Z \
               "$SESSION_DIR"/*.jsonl.deleted.*Z 2>/dev/null
```

## 小贴士

- 会话是仅追加的 JSONL（每行一个 JSON 对象）
- 大型会话可能有几 MB——使用 `head`/`tail` 进行采样
- `sessions.json` 索引将聊天提供者（discord、whatsapp 等）映射到会话 ID
- **重置/压缩会话** 有 `.jsonl.reset.<时间戳>Z` 后缀——仍然包含完整记录且可搜索。
- **已删除会话** 有 `.jsonl.deleted.<时间戳>Z` 后缀——也仍然可搜索。
- 一个 plain `*.jsonl` 通配符会遗漏这两种归档形式。当您需要完整历史记录时，请显式包含它们（见上面的“包含归档记录”片段）。

## 快速文本提示（低噪声）

```bash
AGENT_ID="<agentId>"
SESSION_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/agents/$AGENT_ID/sessions"
jq -r 'select(.type=="message") | .message.content[]? | select(.type=="text") | .text' "$SESSION_DIR"/<id>.jsonl | rg '关键词'
```
