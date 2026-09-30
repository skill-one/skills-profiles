---
name: cass
description: 编码代理会话搜索 - 统一的命令行界面/文本用户界面，用于索引和搜索本地编码代理历史记录，支持 Claude Code、Codex、Gemini、Cursor、Aider、ChatGPT、Pi-Agent、Factory 等。专为 AI 代理消费而设计，支持机器人模式。
---

# CASS - 编码代理会话搜索

一个统一的、高性能的 CLI/TUI 工具，用于索引和搜索您本地的编码代理历史记录。聚合来自**23个代理**的会话，包括 Codex、Claude Code、Gemini CLI、Cline、OpenCode、Amp、Cursor、ChatGPT、Aider、Pi-Agent、Factory（Droid）、OpenHands、Antigravity 和 Grok Build。

## 关键：AI 代理需要启用机器人模式

**绝对不要直接运行 `cass`** - 它会启动一个交互式 TUI 并阻塞您的会话！

```bash
# 错误用法 - 阻塞终端
cass

# 正确用法 - 为代理生成 JSON 输出
cass search "查询" --robot
cass search "查询" --json  # 别名
```

**始终使用 `--robot` 或 `--json` 标志以获取机器可读的输出。**

---

## AI 代理快速参考

### 有界历史检索

对于快速的项目历史记录问题，从一个范围受限的查询开始。以下标志在 cass 0.8.0 上经过验证；每个安装版本后，请运行一次 `cass --version` 和 `cass search --help`。如果 `--no-maintenance` 不受支持，请停止并报告版本不匹配；静默删除它允许维护。

```bash
# 特定术语、一个工作区、最近的历史记录、小的引用结果集
cass search "性能回归" --workspace /path/to/project --days 7 \
  --mode lexical --no-maintenance --robot --robot-meta --fields minimal \
  --limit 5 --max-tokens 2000 --timeout 2000

# 仅扩展一个有用的结果，使用其确切的 source_path 和 line_number
cass view /path/to/session.jsonl -n 42 -C 3 --json --timeout 2000
```

`--timeout` 以毫秒为单位；`--max-tokens` 是一个近似输出预算，不是 CPU 或内存限制。同时应用调用方的时钟墙截止时间（例如，在命令前使用 GNU `timeout 10s`）。该包装器的退出码 124 是一个不完整的尝试；其中断的 stdout 可能不是有效的 JSON。在 JSON 搜索输出中，即使退出码为 0，也要检查 `budget.timed_out`：空的超时结果并不能证明不存在历史记录。

`view -C 3` 限制周围行，而不是字节或标记；一个 JSONL 记录可以很大。在将摘录添加到提示之前，请检查其输出大小。

混合模式是产品的默认设置。显式的词法模式将此工作流程排除在语义推理之外；`--no-maintenance` 防止索引修复、追赶和守护进程自动启动。如果它返回 `maintenance-required`，请报告该障碍并停止此检索尝试。不要将摘要请求转换为索引、修复、模型安装、通配符聚合或重复的健康/状态工作流。在诊断就绪状态时使用就绪命令；在开始单独的变异任务之前，请查看它们建议的操作。故意放宽日期或术语，在完成查询后；只有在需要概念检索并且其成本可以接受时，才选择语义/混合模式。在摘要中保留源/行引用。

### 基本命令

```bash
# 查找此工作区的当前会话
cass sessions --current --json

# 列出特定项目的最近会话
cass sessions --workspace "$(pwd)" --json --limit 5

# 常见的代理流程：查找当前会话，然后导出它
cass export-html "$(cass sessions --current --json | jq -r '.sessions[0].path')" --json

# 使用 JSON 输出进行搜索
cass search "authentication error" --robot --limit 5

# 搜索时包含元数据（elapsed_ms、缓存统计信息、新鲜度）
cass search "error" --robot --robot-meta

# 最小负载（路径、行、代理）
cass search "bug" --robot --fields minimal

# 在特定行查看源代码
cass view /path/to/session.jsonl -n 42 --json

# 扩展围绕某行的上下文
cass expand /path/to/session.jsonl -n 42 -C 5 --json

# 能力发现
cass capabilities --json

# 完整 API 模式
cass introspect --json

# LLM 优化的文档
cass robot-docs guide
cass robot-docs commands
cass robot-docs schemas
cass robot-docs examples
cass robot-docs exit-codes
```

---

## 为什么使用 CASS

### 跨代理知识迁移

您的编码代理创建分散的知识：
- Claude Code 会话位于 `~/.claude/projects`
- Codex 会话位于 `~/.codex/sessions`
- Cursor 状态存储在 SQLite 数据库中
- Aider 历史记录存储在 markdown 文件中

CASS 将所有这些**统一**到一个可搜索的索引中。当您在某个问题上卡住时，可以跨所有过去的代理会话搜索以找到相关的解决方案。

### 用例

```bash
# "我以前解决过这个问题..."
cass search "TypeError: Cannot read property" --robot --days 30

# 跨代理学习（任何代理关于 X 的说法是什么？）
cass search "authentication" --robot --workspace /path/to/project

# 代理到代理的交接
cass search "database migration" --robot --fields summary

# 每日回顾
cass timeline --today --json
```

---

## 命令参考

### 索引

```bash
# DB 和搜索索引的完整重建
cass index --full

# 增量更新（自上次扫描以来）
cass index

# 监视模式：自动在文件更改时重新索引
cass index --watch

# 即使模式未更改，也强制重建
cass index --full --force-rebuild

# 带有幂等性密钥的安全重试（24 小时 TTL）
cass index --full --idempotency-key "build-$(date +%Y%m%d)"

# 带有统计信息的 JSON 输出
cass index --full --json
```

### 搜索

```bash
# 基本搜索（需要 JSON 输出以供代理使用！）
cass search "query" --robot

# 带有过滤器
cass search "error" --robot --agent claude --days 7
cass search "bug" --robot --workspace /path/to/project
cass search "panic" --robot --today

# 时间过滤器
cass search "auth" --robot --since 2024-01-01 --until 2024-01-31
cass search "test" --robot --yesterday
cass search "fix" --robot --week

# 通配符
cass search "auth*" --robot          # 前缀：authentication, authorize
cass search "*tion" --robot          # 后缀：authentication, exception
cass search "*config*" --robot       # 子字符串：misconfigured

# 标记预算管理（对 LLM 至关重要！）
cass search "error" --robot --fields minimal              # 仅 path, line, agent
cass search "error" --robot --fields summary              # 添加 title, score
cass search "error" --robot --max-content-length 500      # 截断字段
cass search "error" --robot --max-tokens 2000             # 软预算（~4 字符/标记）
cass search "error" --robot --limit 5                     # 限制结果数量

# 分页（基于游标）
cass search "TODO" --robot --robot-meta --limit 20
# 使用响应中的 _meta.next_cursor：
cass search "TODO" --robot --robot-meta --limit 20 --cursor "eyJ..."

# 匹配高亮
cass search "authentication error" --robot --highlight

# 查询分析/调试
cass search "auth*" --robot --explain    # 解析查询，成本估计
cass search "auth error" --robot --dry-run  # 验证而不执行

# 聚合（服务器端计数）
cass search "error" --robot --aggregate agent,workspace,date

# 请求关联
cass search "bug" --robot --request-id "req-12345"

# 源过滤（用于多机设置）
cass search "auth" --robot --source laptop
cass search "error" --robot --source remote

# 可追溯性（用于调试代理管道）
cass search "error" --robot --trace-file /tmp/cass-trace.json
```

### 会话分析

```bash
# 将对话导出到 markdown/HTML/JSON
cass export /path/to/session.jsonl --format markdown -o conversation.md
cass export /path/to/session.jsonl --format html -o conversation.html
cass export /path/to/session.jsonl --format json --include-tools

# 扩展围绕某行的上下文（从搜索结果）
cass expand /path/to/session.jsonl -n 42 -C 5 --json
# 显示第 42 行前后的 5 条消息

# 在行查看源代码
cass view /path/to/session.jsonl -n 42 --json

# 活动时间线
cass timeline --today --json --group-by hour
cass timeline --days 7 --json --agent claude
cass timeline --since 7d --json

# 查找与文件相关的会话
cass context /path/to/source.ts --json
```

### 状态 & 诊断

```bash
# 就绪诊断，在需要时使用；不是每个查询的前提条件
cass health --json

# 完整状态快照
cass status --json
cass state --json  # 别名

# 统计信息
cass stats --json
cass stats --by-source  # 用于多机

# 完整诊断
cass diag --verbose
```

---

## 聚合 & 分析

在服务器端聚合搜索结果以获取计数和分布，而无需传输完整的结果数据：

聚合减少输出量，但不一定减少扫描工作。它们不是快速历史记录问题的第一步；使用上面提到的范围检索配方。

```bash
# 按代理计数结果
cass search "error" --robot --aggregate agent
# → { "aggregations": { "agent": { "buckets": [{"key": "claude_code", "count": 45}, ...] } } }

# 多字段聚合
cass search "bug" --robot --aggregate agent,workspace,date

# 与过滤器结合
cass search "TODO" --agent claude --robot --aggregate workspace
```

| 聚合字段 | 描述 |
|-------------------|-------------|
| `agent` | 按代理类型分组（claude_code, codex, cursor, 等） |
| `workspace` | 按工作区/项目路径分组 |
| `date` | 按日期（YYYY-MM-DD）分组 |
| `match_type` | 按匹配质量分组（exact, prefix, fuzzy） |

每个字段返回前 10 个桶，并带有 `other_count` 以表示剩余项。

---

## 远程源（多机搜索）

通过 SSH/rsync 搜索来自多台机器的会话。

### 设置向导（推荐）

```bash
cass sources setup
```

向导：
1. 从 `~/.ssh/config` 发现 SSH 主机
2. 探测每个主机上的代理数据和 cass 安装情况
3. 可选地在远程主机上安装 cass
4. 在远程主机上索引会话
5. 配置 `sources.toml`
6. 本地同步数据

```bash
cass sources setup --hosts css,csd,yto  # 特定主机
cass sources setup --dry-run             # 预览而不更改
cass sources setup --resume              # 恢复中断的设置
```

### 手动设置

```bash
# 添加远程机器
cass sources add user@laptop.local --preset macos-defaults
cass sources add dev@workstation --path ~/.claude/projects --path ~/.codex/sessions

# 列出源
cass sources list --json

# 同步会话
cass sources sync
cass sources sync --source laptop --verbose

# 检查连接性
cass sources doctor
cass sources doctor --source laptop --json

# 路径映射（将远程路径重写为本地）
cass sources mappings list laptop
cass sources mappings add laptop --from /home/user/projects --to /Users/me/projects
cass sources mappings test laptop /home/user/projects/myapp/src/main.rs

# 删除源
cass sources remove laptop --purge -y
```

配置存储在 `~/.config/cass/sources.toml`（Linux）或 `~/Library/Application Support/cass/sources.toml`（macOS）。

---

## 机器人模式深入解析

### 自描述 API

CASS 教授代理如何使用它自身：

```bash
# 快速能力检查
cass capabilities --json
# 返回：features, connectors, limits

# 完整 API 模式
cass introspect --json
# 返回：所有命令、参数、响应形状

# 基于主题的文档（LLM 优化）
cass robot-docs commands   # 所有命令和标志
cass robot-docs schemas    # 响应 JSON 模式
cass robot-docs examples   # 复制粘贴调用
cass robot-docs exit-codes # 错误处理
cass robot-docs guide      # 快速入门指南
cass robot-docs contracts  # API 版本控制
cass robot-docs sources    # 远程源指南
```

### 宽容语法（代理友好）

CASS 自动更正常见错误：

| 您输入的内容 | CASS 理解的内容 |
|---------------|----------------------|
| `cass serach "error"` | `cass search "error"`（拼写错误已更正） |
| `cass -robot -limit=5` | `cass --robot --limit=5`（单短横线已修复） |
| `cass --Robot --LIMIT 5` | `cass --robot --limit 5`（大小写已规范化） |
| `cass find "auth"` | `cass search "auth"`（别名已解析） |
| `cass --limt 5` | `cass --limit 5`（Levenshtein <=2） |

**命令别名：**
- `find`, `query`, `q`, `lookup`, `grep` → `search`
- `ls`, `list`, `info`, `summary` → `stats`
- `st`, `state` → `status`
- `reindex`, `idx`, `rebuild` → `index`
- `show`, `get`, `read` → `view`
- `docs`, `help-robot`, `robotdocs` → `robot-docs`

### 输出格式

```bash
# 美化打印的 JSON（默认）
cass search "error" --robot

# 流式传输的 JSONL（标题 + 每行一个结果）
cass search "error" --robot-format jsonl

# 紧凑的单行 JSON
cass search "error" --robot-format compact

# 带有性能元数据
cass search "error" --robot --robot-meta
```

**设计原则：** stdout = JSON 仅；诊断信息输出到 stderr。

### 标记预算管理

LLMs 有上下文限制。控制输出大小：

| 标志 | 效果 |
|------|--------|
| `--fields minimal` | 仅 `source_path`, `line_number`, `agent` |
| `--fields summary` | 添加 `title`, `score` |
| `--fields score,title,snippet` | 自定义字段选择 |
| `--max-content-length 500` | 截断长字段（UTF-8 安全） |
| `--max-tokens 2000` | 软预算（~4 字符/标记） |
| `--limit 5` | 限制结果数量 |

截断的字段包括 `*_truncated: true` 指示器。

---

## 结构化错误处理

错误是带有可操作提示的 JSON：

```json
{
  "error": {
    "code": 3,
    "kind": "index_missing",
    "message": "搜索索引未找到",
    "hint": "运行 'cass index --full' 以构建索引",
    "retryable": false
  }
}
```

### 退出码

| 代码 | 含义 | 操作 |
|------|---------|--------|
| 0 | 成功 | 解析 stdout |
| 1 | 健康检查失败 | 检查报告的条件；不会自动重建 |
| 2 | 用法错误 | 修复语法（提供提示） |
| 3 | 索引/DB 缺失 | 报告缺失资源；索引是单独的变异任务 |
| 4 | 网络错误 | 检查连接性 |
| 5 | 数据/维护失败 | 读取错误类型；保留存档并报告障碍 |
| 6 | 版本不兼容 | 更新 cass |
| 7 | 锁定/忙 | 过一段时间再试 |
| 8 | 部分结果 | 报告不完整覆盖；不要静默重试 |
| 9 | 未知错误 | 检查 `retryable` 标志 |

代码是命令特定的：请参考 `cass robot-docs exit-codes` 和 JSON 错误类型。搜索预算过期可能会返回退出码 0 但 `budget.timed_out=true`；会话路径输出使用退出码 10 表示超时。

---

## 搜索模式

三种搜索模式，可通过 `--mode` 标志选择：

| 模式 | 算法 | 适用于 |
|------|-----------|----------|
| **词法** | BM25 全文 | 精确术语匹配，有界历史配方 |
| **语义** | 向量相似度 | 概念查询，"查找相似" |
| **混合**（默认） | 互惠排序融合 | 词法检索，在就绪时使用语义细化 |

```bash
cass search "authentication" --mode lexical --robot
cass search "how to handle user login" --mode semantic --robot
cass search "auth error handling" --mode hybrid --robot
```

**混合** 使用 RRF 组合词法和语义：
```
RRF_score = Σ 1 / (60 + rank_i)
```

---

## 管道模式（串联搜索）

通过管道会话路径串联搜索：

```bash
# 查找提到 "auth" 的会话，然后在其中搜索 "token"
cass search "authentication" --robot-format sessions | \
  cass search "refresh token" --sessions-from - --robot

# 从今天的工作构建过滤语料库
cass search --today --robot-format sessions > today_sessions.txt
cass search "bug fix" --sessions-from today_sessions.txt --robot
```

用例：
- **下钻**：广泛搜索 → 在结果中缩小范围
- **交叉引用**：查找包含术语 A 的会话，然后在其中查找术语 B
- **语料库构建**：保存会话列表以进行重复搜索

---

## 查询语言

### 基本查询

| 查询 | 匹配 |
|-------|---------|
| `error` | 包含 "error" 的消息（不区分大小写） |
| `python error` | "python" 和 "error" 都必须匹配 |
| `"authentication failed"` | 精确短语 |

### 布尔运算符

| 运算符 | 示例 | 含义 |
|----------|---------|---------|
| `AND` | `python AND error` | 两个术语都必需（默认） |
| `OR` | `error OR warning` | 任何术语匹配 |
| `NOT` | `error NOT test` | 第一个术语，排除第二个 |
| `-` | `error -test` | NOT 的简写 |

```bash
# 复杂布尔查询
cass search "authentication AND (error OR failure) NOT test" --robot

# 排除测试文件
cass search "bug fix -test -spec" --robot

# 任意错误类型
cass search "TypeError OR ValueError" --robot
```

### 通配符模式

| 模式 | 类型 | 性能 |
|------|------|------|
| `auth*` | 前缀 | 快速（边缘n-gram） |
| `*tion` | 后缀 | 较慢（正则表达式） |
| `*config*` | 子字符串 | 最慢（正则表达式） |

### 匹配类型

结果包含 `match_type`：

| 类型 | 含义 | 分数提升 |
|------|------|----------|
| `exact` | 字面匹配 | 最高 |
| `prefix` | 通过前缀扩展 | 高 |
| `suffix` | 通过后缀模式 | 中等 |
| `substring` | 通过子字符串模式 | 较低 |
| `fuzzy` | 自动回退（稀疏结果） | 最低 |

### 自动模糊回退

当精确查询返回少于3个结果时，CASS会自动使用通配符重试：
- `auth` → `*auth*`
- 结果标记为 `wildcard_fallback: true`

### 灵活的时间输入

CASS 接受多种时间/日期格式：

| 格式 | 示例 |
|------|------|
| **相对** | `-7d`, `-24h`, `-30m`, `-1w` |
| **关键词** | `now`, `today`, `yesterday` |
| **ISO 8601** | `2024-11-25`, `2024-11-25T14:30:00Z` |
| **美国日期** | `11/25/2024`, `11-25-2024` |
| **Unix 时间戳** | `1732579200`（秒或毫秒） |

---

## 排序模式

在TUI中使用 `F12` 循环或使用 `--ranking` 标志：

| 模式 | 公式 | 适用于 |
|------|------|--------|
| **近期重要** | `relevance*0.3 + recency*0.7` | "我在处理什么？" |
| **平衡** | `relevance*0.5 + recency*0.5` | 一般搜索 |
| **相关性** | `relevance*0.8 + recency*0.2` | "X的最佳解释" |
| **匹配质量** | 惩罚模糊匹配 | 精确技术搜索 |
| **日期最新** | 纯时间顺序 | 近期活动 |
| **日期最早** | 逆时间顺序 | "我第一次..." |

### 分数组件

- **文本相关性（BM25）**：词频、逆文档频率、长度归一化
- **时效性**：指数衰减（今天 ~1.0，上周 ~0.7，上个月 ~0.3）
- **匹配精确度**：精确短语=1.0，前缀=0.9，后缀=0.8，子字符串=0.6，模糊=0.4

### 混合分数公式

```
Final_Score = BM25_Score × Match_Quality + α × Recency_Factor
```

| 模式 | α 值 | 效果 |
|------|------|------|
| 近期重要 | 1.0 | 时效性主导 |
| 平衡 | 0.4 | 适度时效性提升 |
| 相关性主导 | 0.1 | BM25主导 |
| 匹配质量 | 0.0 | 纯文本匹配 |

---

## 支持的代理（23个连接器）

| 代理 | 位置 | 格式 |
|------|------|------|
| **Claude Code** | `~/.claude/projects` | JSONL |
| **Codex** | `~/.codex/sessions` | JSONL（发布） |
| **Gemini CLI** | `~/.gemini/tmp` | JSON |
| **Cline** | VS Code全局存储 | 任务目录 |
| **OpenCode** | `.opencode` 目录 | SQLite |
| **Amp** | `~/.local/share/amp` + VS Code | 混合 |
| **Cursor** | `~/Library/Application Support/Cursor` | SQLite（state.vscdb） |
| **ChatGPT** | `~/Library/Application Support/com.openai.chat` | JSON（v1未加密） |
| **Aider** | `~/.aider.chat.history.md` + 每个项目 | Markdown |
| **Pi-Agent** | `~/.pi/agent/sessions` | JSONL带思考 |
| **Factory (Droid)** | `~/.factory/sessions` | JSONL按工作区 |
| **GitHub Copilot Chat** | VS Code全局存储 | JSON / SQLite |
| **GitHub Copilot CLI** | `~/.copilot/session-state` | JSONL |
| **OpenClaw** | `~/.openclaw` | JSONL |
| **ClawdBot** | `~/.clawdbot` | JSONL |
| **Vibe** | `~/.vibe/logs/session` | JSONL |
| **Crush** | `~/.crush/crush.db` | SQLite |
| **Hermes** | `~/.hermes` | JSONL |
| **Kimi Code** | `~/.kimi/sessions` | JSONL |
| **Qwen Code** | `~/.qwen/tmp` | JSON / JSONL |
| **OpenHands** | `~/.openhands/conversations` | JSON事件流 |
| **Antigravity** | `~/.gemini/antigravity-cli` | JSONL / SQLite |
| **Grok Build** | `$GROK_HOME/sessions`（默认 `~/.grok/sessions`） | ACP更新JSONL |

**注意**：ChatGPT v2/v3使用AES-256-GCM加密（需要钥匙串访问）。遗留v1未加密对话会自动索引。

---

## TUI功能（供人类使用）

使用 `cass` 启动（无标志）：

### 键盘快捷键

**导航：**
- `上/下`：移动选择
- `左/右`：切换面板
- `Tab/Shift+Tab`：循环焦点
- `Enter`：在 `$EDITOR` 中打开
- `空格`：全屏详细视图
- `Home/End`：跳转到第一个/最后一个结果
- `PageUp/PageDown`：按页滚动

**过滤：**
- `F3`：代理过滤
- `F4`：工作区过滤
- `F5/F6`：时间过滤（从/到）
- `Shift+F3`：范围到当前结果代理
- `Shift+F4`：清除工作区过滤
- `Shift+F5`：循环预设（24h/7d/30d/all）
- `Ctrl+Del`：清除所有过滤

**模式：**
- `F2`：切换主题（6个预设）
- `F7`：上下文窗口大小（S/M/L/XL）
- `F9`：匹配模式（前缀/标准）
- `F12`：排序模式
- `Ctrl+B`：切换边框样式

**选择与操作：**
- `m`：切换选择
- `Ctrl+A`：全选
- `A`：批量操作菜单
- `Ctrl+Enter`：添加到队列
- `Ctrl+O`：打开所有队列
- `y`：复制路径/内容
- `Ctrl+Y`：复制所有选择
- `/`：在详细面板中查找
- `n/N`：下一个/上一个匹配

**视图与调色板：**
- `Ctrl+P`：命令调色板
- `1-9`：加载保存的视图
- `Shift+1-9`：保存视图到槽位

**源过滤（多机）：**
- `F11`：循环源过滤（全部/本地/远程）
- `Shift+F11`：源选择菜单

**全局：**
- `Ctrl+C`：退出
- `F1`或`?`：切换帮助
- `Ctrl+Shift+R`：强制重新索引
- `Ctrl+Shift+Del`：重置所有TUI状态

### 详细面板标签页

| 标签页 | 内容 | 切换 |
|------|------|------|
| **消息** | 完整对话带Markdown | `[` / `]` |
| **片段** | 关键词提取摘要 | `[` / `]` |
| **原始** | 未格式化JSON/文本 | `[` / `]` |

### 上下文窗口大小

| 大小 | 字符数 | 用途 |
|------|--------|------|
| **小** | ~200 | 快速扫描 |
| **中** | ~400 | 默认平衡视图 |
| **大** | ~800 | 较长段落 |
| **XL** | ~1600 | 全部上下文，代码审查 |

**预览模式** (`Ctrl+Space`)：临时扩展到XL而不改变默认设置。

---

## 主题预设

使用 `F2` 循环6个内置主题：

| 主题 | 描述 | 适用于 |
|------|------|--------|
| **暗** | 受东京夜色启发的深蓝色 | 低光环境 |
| **亮** | 高对比度浅色背景 | 明亮环境 |
| **Catppuccin** | 温暖的柔和色调，减少眼疲劳 | 全天编程 |
| **Dracula** | 紫色点缀的深色主题 | 流行开发者主题 |
| **Nord** | 北极启发的冷色调 | 平静专注的工作 |
| **高对比度** | 最大可读性 | 无障碍需求 |

所有主题均通过WCAG对比度要求验证（文本最小4.5:1）。

### 基于角色的消息样式

| 角色 | 视觉处理 |
|------|----------|
| **用户** | 蓝色背景，粗体 |
| **助手** | 绿色背景 |
| **系统** | 灰色/柔和背景 |
| **工具** | 橙色背景 |

---

## 保存视图

将过滤配置保存到9个槽位以快速调用。

**保存的内容：**
- 活跃过滤（代理、工作区、时间范围）
- 当前排序模式
- 搜索查询

**键盘：**
- `Shift+1`至`Shift+9`：保存当前视图
- `1`至`9`：从槽位加载视图

**通过命令调色板：** `Ctrl+P` → "保存/加载视图"

视图保存在 `tui_state.json` 中跨会话持久化。

---

## 密度模式

控制每个搜索结果的行数。使用 `Shift+D` 循环：

| 模式 | 行数 | 适用于 |
|------|------|--------|
| **紧凑** | 3 | 最大结果可见 |
| **舒适** | 5 | 平衡视图（默认） |
| **宽敞** | 8 | 详细预览 |

---

## 书签系统

带注释和标签保存重要结果：

在TUI中：按 `b` 书签，添加注释和标签。

**书签结构：**
- `title`：简短描述
- `source_path`, `line_number`, `agent`, `workspace`
- `note`：您的注释
- `tags`：逗号分隔标签
- `snippet`：提取内容

存储：`~/.local/share/coding-agent-search/bookmarks.db`（SQLite）

---

## 可选语义搜索

本地仅语义搜索使用MiniLM（无需云：

**所需文件**（放在数据目录中）：
- `model.onnx`
- `tokenizer.json`
- `config.json`
- `special_tokens_map.json`
- `tokenizer_config.json`

向量索引存储为 `vector_index/index-minilm-384.cvvi`。

CASS 不会自动下载模型；您必须手动安装它们。

**哈希嵌入器回退：** 当MiniLM未安装时，CASS使用基于哈希的嵌入器进行近似语义相似度。

---

## 监视模式

实时索引更新：

```bash
cass index --watch
```

- **去抖动**：2秒（等待突发稳定）
- **最大等待**：5秒（在持续活动中强制刷新）
- **增量**：仅重新扫描修改的文件

TUI自动在后台启动监视模式。

---

## 去重策略

CASS使用多层去重：

1. **消息哈希**：`(角色 + 内容 + 时间戳)`的SHA-256 - 相同消息存储一次
2. **对话指纹**：前N条消息哈希的哈希 - 检测重复文件
3. **搜索时去重**：按内容相似度去重结果

**噪声过滤：**
- 空消息和纯空白
- 系统提示（除非在搜索它们）
- 重复的工具确认

---

## 性能特征

延迟和内存取决于存档大小、索引就绪状态、模型状态以及进程是否为冷启动。历史小语料库时间不是大型存档的截止时间。测量完整命令，绑定每次检索尝试，并区分成功结果与超时或维护拒绝。

---

## 响应形状

**搜索响应：**
```json
{
  "query": "error",
  "limit": 10,
  "count": 5,
  "total_matches": 42,
  "hits": [
    {
      "source_path": "/path/to/session.jsonl",
      "line_number": 123,
      "agent": "claude_code",
      "workspace": "/projects/myapp",
      "title": "身份验证调试",
      "snippet": "错误发生在...",
      "score": 0.85,
      "match_type": "exact",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "_meta": {
    "elapsed_ms": 12,
    "cache_hit": true,
    "wildcard_fallback": false,
    "next_cursor": "eyJ...",
    "index_freshness": { "stale": false, "age_seconds": 120 }
  }
}
```

**聚合响应：**
```json
{
  "aggregations": {
    "agent": {
      "buckets": [
        {"key": "claude_code", "count": 120},
        {"key": "codex", "count": 85}
      ],
      "other_count": 15
    }
  }
}
```

---

## 环境变量

| 变量 | 目的 |
|------|------|
| `CASS_DATA_DIR` | 覆盖数据目录 |
| `CHATGPT_ENCRYPTION_KEY` | 加密的ChatGPT的Base64密钥 |
| `PI_CODING_AGENT_DIR` | 覆盖Pi-Agent会话路径 |
| `CASS_CACHE_SHARD_CAP` | 每个分片的缓存条目（默认256） |
| `CASS_CACHE_TOTAL_CAP` | 总缓存命中（默认2048） |
| `CASS_DEBUG_CACHE_METRICS` | 启用缓存调试日志 |
| `CODING_AGENT_SEARCH_NO_UPDATE_PROMPT` | 跳过更新检查 |

---

## Shell自动补全

```bash
cass completions bash > ~/.local/share/bash-completion/completions/cass
cass completions zsh > "${fpath[1]}/_cass"
cass completions fish > ~/.config/fish/completions/cass.fish
cass completions powershell >> $PROFILE
```

---

## API合约与版本控制

```bash
cass api-version --json
# → { "version": "0.4.0", "contract_version": "1", "breaking_changes": [] }

cass introspect --json
# → 完整模式：所有命令、参数、响应类型
```

**保证稳定：**
- 退出代码及其含义
- `--robot`输出的JSON响应结构
- 标志名称和行为
- `_meta`块格式

---

## 与CASS记忆（cm）集成

CASS提供**情景记忆**（原始会话）。CM提取**程序记忆**（规则和剧本）：

```bash
# 1. CASS索引原始会话
cass index --full

# 2. 搜索相关过去的经验
cass search "authentication timeout" --robot --limit 10

# 3. CM反思会话以提取规则
cm reflect
```

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| "缺少索引" / `maintenance-required` | 报告障碍；将检索与授权索引/修复分开 |
| 陈旧警告 | 报告年龄/覆盖范围；单独决定是否刷新 |
| 空结果 | 检查 `budget.timed_out`；如果尝试完成则重新考虑查询范围 |
| JSON解析错误 | 使用 `--robot-format compact` |
| 监视未触发 | 检查 `watch_state.json`，验证文件事件支持 |
| 重置TUI状态 | `cass tui --reset-state` 或 `Ctrl+Shift+Del` |

---

## 安装

```bash
# 一行安装
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.sh \
  | bash -s -- --easy-mode --verify

# Windows
irm https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.ps1 | iex
```

---

## 与Flywheel集成

| 工具 | 集成 |
|------|------|
| **CM** | CASS提供情景记忆，CM提取程序记忆 |
| **NTM** | Robot模式标记用于搜索过去会话 |
| **Agent Mail** | 搜索跨代理历史记录的线程 |
| **BV** | 跨参考珠子与过去解决方案 |
