<!-- 自动生成的文件 — 请勿编辑。
     此文件是库/media-and-娱乐/espn/SKILL.md 的逐字镜像，
     合并后由 tools/generate-skills/ 中的工具重新生成。在此处的手动编辑
     在下次重新生成时将被静默覆盖。请编辑库/源代码。
     请参阅仓库代理指南，第“生成的工件：registry.json, cli-skills/”部分。 -->

# ESPN — 印刷机 CLI

## 前置条件：安装 CLI

此技能驱动 `espn-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它丢失，请先安装它：

1. 通过印刷机安装程序安装。它将二进制文件默认设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install espn --cli-only
   ```
2. 验证：`espn-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）：

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-娱乐/espn/cmd/espn-pp-cli@latest
```

如果安装后 `--version` 报告“命令未找到”，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，不要继续使用技能命令。

## 何时使用此 CLI

当用户想要快速查找体育信息时使用此 CLI - 当前比分、排名、即将到来的赛程、对头记录或丰富的每场比赛摘要（计分板、领袖、得分回放、赔率、获胜概率）。也适用于跨联赛发现（`today`）和离线搜索跨同步数据。

如果用户有像 Stats Perform 或 Sportradar 这样的付费源，它们提供更干净的数据，或者他们需要实时 websocket 更新（ESPN 的端点是轮询的），则不要使用此 CLI。对于单独的投注赔率，每场比赛的 `summary` 有效负载包括它们，但没有跨联赛的赔率命令。

## 独特功能

仅因为本地同步和跨联赛工具而工作的命令。

### 跨联赛发现

- **`today`** — 一次调用中所有主要体育项目的当天比分。最快的“今晚有什么比赛”答案，无需先选择体育项目。

- **`trending`** — 在所有联赛中最受关注的运动员和球队，按当前人气排名。适用于“现在谁很火”而无需命名体育项目。

- **`dashboard`** — 从 `~/.config/espn-pp-cli/config.toml` 读取 `[favorites]` 并显示每个收藏球队在联赛中的比分，一次调用。

- **`watch <sport> <league> --event <game_id>`** — 某个特定比赛的实时比分更新（每 30 秒轮询一次）。使用 `scores` 或 `today` 找到比赛，然后使用 `watch` 实时跟踪它。

### 比赛状态智能

- **`summary <sport> <league> --event <game_id>`** — 包括计分板、领袖、得分回放、赔率和获胜概率的详细比赛摘要。每场比赛最丰富的有效负载。

- **`boxscore <event_id>`** — 某个事件的对每个球员的计分板，从最近的计分板缓存命中推断出运动+联赛。传递 `--sport`/`--league` 以跳过推断。

- **`plays <sport> <league> --event <id>`** — 某个特定事件的逐场回放。可选的 `--limit`（默认 200）。

- **`recap <sport> <league>`** — 最近完成的联赛中最最近比赛的赛后回放，包括计分板和领袖。

- **`scoreboard <sport> <league>`** — 带有日期过滤、周/组选择器和比赛元数据的实时计分板。

- **`odds <sport> <league>`** — 今晚赛程的让分、大小分和投注线，从计分板有效负载派生（没有每场比赛摘要调用）。

### 排名和排名

- **`standings <sport> <league>`** — 联盟/分区的排名。

- **`rankings <sport> <league>`** — 当前 AP、教练和 CFP 汇票排名（NCAAF/NCAAM）。

- **`streak <sport> <league>`** — 联赛中各队的当前胜负连续记录，由同步数据计算得出。

- **`rivals <sport> <league>`** — 联赛中球队之间的对头记录，来自同步数据。

- **`h2h <team1> <team2> --sport <s> --league <l>`** — 某一对更详细的对头信息，包括平均得分和最近交锋列表。

- **`sos <sport> <league>`** — 每个队的赛程强度，从排名有效负载派生，降序排列。

### 人物

- **`leaders <sport> <league> [--category <name>]`** — 各类别的统计领袖，可选过滤器。

- **`compare <athlete1> <athlete2> --sport <s> --league <l>`** — 两位运动员的逐行赛季统计数据。歧义名称会列出候选者并退出 2。

- **`injuries <sport> <league>`** — 联盟中活跃的伤病报告，按球队分组。

- **`transactions <sport> <league>`** — 最近交易、签约和弃权。

### 本地存储

- **`sync`** — 将运动+联赛数据集拉入本地 SQLite 以进行离线分析。

- **`search "<query>"`** — 跨同步事件和新闻的全文搜索。

- **`sql <query>`** — 对本地数据库运行只读 SQL 查询。

## 命令参考

实时操作：

- `espn-pp-cli scores <sport> <league>` — 当前比分
- `espn-pp-cli today` — 所有主要体育项目的当天比分
- `espn-pp-cli scoreboard <sport> <league>` — 带有可选日期过滤的计分板
- `espn-pp-cli watch <sport> <league> --event <game_id>` — 某个游戏的实时比分轮询
- `espn-pp-cli standings <sport> <league>` — 联赛排名
- `espn-pp-cli trending` — 联赛中最受关注的运动员和球队
- `espn-pp-cli dashboard` — 从 `~/.config/espn-pp-cli/config.toml` 中的收藏快照

球队详情：

- `espn-pp-cli teams <sport> <league> <team_id>` — 某个球队的赛程（过去 + 即将到来）
- `espn-pp-cli teams get <sport> <league> <team_id>` — 球队记录、链接和标志
- `espn-pp-cli teams list <sport> <league>` — 联赛中的所有球队
- `espn-pp-cli streak <sport> <league>` — 来自同步数据的当前胜负连续记录
- `espn-pp-cli rivals <sport> <league>` — 联赛中球队之间的对头记录，来自同步数据
- `espn-pp-cli h2h <team1> <team2> --sport <s> --league <l>` — 某个球队对的更详细信息（平均得分、交锋）
- `espn-pp-cli sos <sport> <league>` — 赛程强度，降序排列

比赛详情：

- `espn-pp-cli summary <sport> <league> --event <game_id>` — 完整比赛摘要（计分板、领袖、得分回放、赔率、获胜概率）
- `espn-pp-cli boxscore <event_id>` — 仅计分板子树（从缓存推断运动/联赛）
- `espn-pp-cli plays <sport> <league> --event <id>` — 逐场回放（可选 `--limit`，默认 200）
- `espn-pp-cli recap <sport> <league>` — 最最近完成的比赛回放
- `espn-pp-cli odds <sport> <league>` — 今晚赛程的让分、大小分、投注线

人物：

- `espn-pp-cli leaders <sport> <league> [--category <name>]` — 按类别的统计领袖
- `espn-pp-cli compare <athlete1> <athlete2> --sport <s> --league <l>` — 两位运动员的逐行赛季统计数据
- `espn-pp-cli injuries <sport> <league>` — 活跃的伤病报告
- `espn-pp-cli transactions <sport> <league>` — 最近交易、签约和弃权

投票和排名：

- `espn-pp-cli rankings <sport> <league>` — AP、教练和 CFP 汇票

信息：

- `espn-pp-cli news <sport> <league>` — 最新新闻

发现和本地：

- `espn-pp-cli search "<query>"` — 跨同步事件和新闻的全文搜索
- `espn-pp-cli sync` — 将运动+联赛同步到本地 SQLite
- `espn-pp-cli sql "<query>"` — 对本地存储运行只读 SQL
- `espn-pp-cli load` — 显示每个分配者的工作负载分布（同步数据）
- `espn-pp-cli orphans` / `stale` — 本地存储的维护视图
- `espn-pp-cli doctor` — 验证连接性和配置

运动值：`football`、`basketball`、`baseball`、`hockey`、`soccer`。
联赛值：`nfl`、`nba`、`mlb`、`nhl`、`ncaaf`、`ncaam`、`ncaaw`、`mls`、`eng.1`（EPL）、`wnba`。

## 配方

### 早晨体育扫描

```bash
espn-pp-cli today --agent --select events.shortName,events.status
espn-pp-cli scores football nfl --agent --select events.shortName,events.competitions.competitors.team.displayName,events.status.type.detail
espn-pp-cli standings football nfl --agent
```

一个 `today` 调用涵盖跨联赛活动，一个 `scores` 用于您关心的联赛，一个 `standings` 用于背景信息。嵌套的 `--select` 路径将计分板有效负载从几十 KB 切割到实际需要的字段——这对于保持代理上下文小至关重要。

### 赛前研究来自同步数据

```bash
espn-pp-cli sync --sport football --league nfl
espn-pp-cli rivals football nfl --agent         # 来自同步数据的历史记录
espn-pp-cli streak football nfl --agent         # 当前连续记录
espn-pp-cli summary football nfl --event <id> --agent   # 特定游戏的完整有效负载，包括赔率和计分板
```

运行一次 `sync`，然后 `rivals` 和 `streak` 从本地存储中即时回答。`summary` 是特定游戏最丰富的单个有效负载（计分板、领袖、得分回放、赔率、获胜概率）。

### 离线搜索同步后

```bash
espn-pp-cli sync --sport football --league nfl
espn-pp-cli search "Mahomes"                    # 在本地存储中查找
```

在连接不良的环境中进行重复查找或批量分析历史数据时很有用。

### 收藏仪表板

向 `~/.config/espn-pp-cli/config.toml` 添加 `[favorites]` 块：

```
[favorites]
nfl = ["KC", "BAL"]
nba = ["LAL"]
```

然后：

```bash
espn-pp-cli dashboard --agent
```

一次调用即可显示每个收藏球队在联赛中的今晚比赛状态，按联赛分组。跨联赛获取并行运行，并报告成功结果 alongside 部分失败结果。

### 赛前赔率和球员挖掘

```bash
espn-pp-cli odds basketball nba --agent          # 今晚的让分/大小分/投注线
espn-pp-cli leaders basketball nba --category points --agent
espn-pp-cli compare "LeBron James" "Stephen Curry" --sport basketball --league nba --agent
espn-pp-cli boxscore <event_id> --agent          # 赛后球员统计数据
espn-pp-cli plays basketball nba --event <id> --limit 50 --agent
```

`odds` 读取计分板的每场比赛线（没有每场比赛摘要调用）。`leaders --category` 过滤到单个统计数据类别。`compare` 通过名称解析运动员 ID，歧义时列出候选者并退出 2。`boxscore` 从最近的缓存命中推断出运动+联赛；传递 `--sport`/`--league` 以跳过推断。

## 认证设置

**无需认证。** ESPN 的公共端点不需要 API 密钥。`auth` 命令存在以保持一致性，但它是无操作的。

可选配置：
- `ESPN_CONFIG` — 覆盖配置文件路径
- `ESPN_BASE_URL` — 覆盖基本 URL（用于代理或镜像）
- `NO_COLOR` — 标准无颜色环境变量

## 代理模式

在任何命令中添加 `--agent`。扩展为 `--json --compact --no-input --no-color --yes`。使用 `--select` 进行字段挑选，`--dry-run` 预览请求，`--no-cache` 跳过 GET 缓存。

### 过滤输出

`--select` 接受点状路径以深入嵌套响应；数组按元素遍历：

```bash
espn-pp-cli <command> --agent --select id,name
espn-pp-cli <command> --agent --select items.id,items.owner.name
```

使用此功能将巨大的有效负载缩小到您实际需要的字段——这对于深度嵌套 API 响应至关重要。

### 响应包

数据层命令将输出包装在 `{"meta": {...}, "results": <data>}` 中。解析 `.results` 获取数据，`.meta.source` 了解它是 `live` 还是本地。当 stdout 是 TTY 时，`N results (live)` 摘要仅打印到 stderr；管道/代理消费者在 stdout 上看到纯 JSON。

## 退出代码

| 代码 | 含义 |
|------|---------|
| 0 | 成功 |
| 2 | 使用错误 |
| 3 | 未找到（球队、比赛、运动员） |
| 5 | API 错误 |
| 7 | 速率限制 |

## 安装

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/espn/cmd/espn-pp-cli@latest
espn-pp-cli doctor
```

### MCP 服务器

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/espn/cmd/espn-pp-mcp@latest
claude mcp add espn-pp-mcp -- espn-pp-mcp
```

## 参数解析

给定 `$ARGUMENTS`：

1. **空、`help` 或 `--help** → 运行 `espn-pp-cli --help`
2. **`install** → CLI；**`install mcp** → MCP
3. **其他任何内容** → 从用户意图解析 `<sport> <league>`（例如，“Lakers” → `basketball nba`），检查 `which espn-pp-cli`（如果缺少则提供安装），使用 `--agent` 运行。

<!-- pr-218-features -->
## 自动学习

两调用协议：`recall` 在发现之前，`teach &` 在发出之前。CLI 执行实体感知匹配验证，并显示查询族的存储剧本；您阅读包并遵循六个分支的决策树。跳过任何一侧都会导致您在未来的会话中失去免费召回命中。

### 第 1 步：`recall` 在任何发现之前

在新用户问题的任何发现命令（`scoreboard`、`teams`、`boxscore`、`search`、`standings` 或任何其他发现命令）之前运行：

```bash
espn-pp-cli recall "<user's question>" --agent
```

响应包：

```json
{
  "query": "...",
  "normalized": "game tonight",
  "query_entities": ["Niners"],
  "found": true | false,
  "match_score": 0.0,
  "results": [
    { "resource_id": "...", "resource_type": "events|news|...", "venue": "...",
      "confidence": 2, "entity_match": "exact|partial|unknown",
      "source": "taught|preseed|pattern", "warnings": ["..."] }
  ],
  "mismatches": [ /* 仅当传递 `--debug-mismatches` 时 */ ],
  "warnings": [ /* 顶层 */ ],
  "playbook": {
    "query_family": "...",
    "playbook": {
      "steps": [ { "cmd": "teams basketball nba {team.id}", "purpose": "..." }, ... ],
      "entity_slots": ["$TEAM", "$STATS"],
      "expected_tool_calls": 3
    },
    "slots_resolved": { "$TEAM": { "token": "pistons", "canonical": "Detroit Pistons" } },
    "notes": "byathlete needs seasontype=2; categories has dup labels"
  },
  "notes": "byathlete needs seasontype=2; categories has dup labels"
}
```

### 第 2 步：六个分支的决策树

按顺序读取 `playbook`、`notes`、`results[0]` 和警告：

```
if Playbook 存在:
    -> 首先逐字读取 Playbook.notes（工作绕过 + CLI 暴露的已知陷阱）
    -> 按顺序重放 Playbook.steps，用 Playbook.slots_resolved 条目替换实体槽标记。如果一个步骤的槽未解决，则仅对那个步骤进行发现。
    -> Playbook 的 expected_tool_calls 是一个预算；如果您发现自己运行的材料更多，请在会话结束时通过 teach-playbook 记录偏差。

elif Notes 存在（没有 Playbook）:
    -> 在任何发现步骤之前逐字读取 Notes；即使没有结构化编排，它们也包含此查询族的已知陷阱。

elif Found AND Results[0].EntityMatch == "exact" AND Results[0].Confidence >= 2:
    -> 跳过发现；并行获取 Results[*].ResourceID 的实时数据（例如，espn-pp-cli boxscore <eid> for an event, espn-pp-cli teams ... for a team）

elif Found AND Results[0].EntityMatch == "partial":
    -> 候选提示，不是命中；阅读资源标题以验证后再信任

elif (任何行在 Mismatches[] 当传递 `--debug-mismatches` 时):
    -> 治作为冷启动；存储的学习适用于不同的实体
       （例如，“Cowboys”学习不会满足“Niners”查询——不同的规范名称）

else:  // Found == false, no playbook, no notes
    -> 冷启动；正常运行发现；在回答后教授答案并通过 teach --playbook-file --playbook-notes-file 记录剧本 + Notes，以便下次相同查询族的会话更快。

### 第 3 步：始终读取 `warnings`

- `low_confidence`: 行存在于 `confidence<2`。将其视为提示，而不是跳过发现命中。
- `resource_not_in_store`: 本地存储中没有存储学习指向的资源。匹配验证器无法分类实体——直接获取并重新评估。
- 顶层 `no_learnings_for_query_family`: 表格在 Jaccard 地板以上没有行。纯粹的冷启动。

### 第 4 步：`teach &` 在最终确定您的响应后

在包含事件/球队 ID 的用户界面响应中，但在发出之前，启动后台教学调用。附加 shell `&` 以使其立即返回并阻止用户界面响应：

```bash
espn-pp-cli teach --query "<user's question>" --resource-type <events|news|teams> --resource <id1> --resource <id2>
# (附加 shell `&` 以使其后台运行)
```

成功时静默。教授**最具体的**资源——如果用户询问“Spurs 的下一场比赛何时进行”并且您通过球队计分板找到事件 `401747632`，请教授该事件 ID，而不是球队 ID。CLI 使用种子实体查找 (NFL/NBA/MLB/MLS 球队名册，具有别名如 Niners/49ers/SF) 在召回时进行跨别名解析，因此“Niners”下的教学将自动满足未来的“49ers”查询。

### 第 5 步：当发现超过 5 个调用时记录剧本

如果您运行了超过 5 个工具调用来回答问题，并且您发现了 CLI 没有显示的工作绕过（静默丢弃的标志、未记录的参数、分页技巧、有效负载陷阱），请记录它们，以便下次相同查询族的会话跳过发现。两种表面：

```bash
# 常见情况：与资源教学一起出现
espn-pp-cli teach --query "<question>" --resource-type <type> --resource <id> \
  --playbook-file ~/playbooks/season-recap.json \
  --playbook-notes-file ~/playbooks/season-recap-notes.md
# (附加 shell `&` 以使其后台运行)

# 独立：笔记仅或配方仅
espn-pp-cli teach-playbook --query "<question>" \
  --playbook-file ~/playbooks/season-recap.json \
  --notes "byathlete needs seasontype=2; categories has dup labels"
```

剧本文件是 JSON，包含 `steps`、`entity_slots`、`expected_tool_calls`。笔记文件是 markdown，包含逐字的工作绕过。这两个字段都可以为空；两个字段都为空则会被拒绝。剧本按结构化查询家族键入（去除实体），因此从“勇士队如何结束本赛季”学到的配方适用于活塞队、热火队和所有其他形状相同的球队查询。

当您在未来的召回中找到剧本时，将其视为绝对真理：使用 `slots_resolved` 替换重放步骤，跳过剧本已经记录的发现，并在任何步骤之前读取 `notes`。

### 第 6 步：`playbook amend &` 当您的调试响应确定一个修正

如果您的调试协议响应确定笔记或剧本应知道的具体修正——一个工作绕过、一个未记录的端点形状、一个过时的字段名、观察到的架构漂移、一个空有效负载回退——在发出用户界面响应之前，启动 `playbook amend`。与 `teach` 相同，采取“发射并忘记”的态度。

```bash
espn-pp-cli playbook amend \
  --query "<exact recall query string>" \
  --add-note "<your concrete correction>"
# (附加 shell `&` 以使其后台运行)
```

什么值得修正：您在本会话中观察到的行为，未来您会从中受益。值得修正的示例：
- “summary 端点将响应包装在 `{meta, results}` 中——数据位于 `.results.header`，而不是 `.header`”
- “compare 返回运动员的空 `team` 字段，其球队不在当前季后赛中”
- “byathlete 类别索引 for avgRebounds 本赛季从 general[9] 漂移到 general[11]”

不属于笔记的：
- 年特定答案（“Curry 在他最后一场比赛中投了 4-16”）。这是响应，不是学习。
- 每支球队或每名运动员的数据，剧本已经在运行时检索。
- 重述现有笔记中已经说过的内容的语句。

修正命令将标记添加到现有笔记，带有时间戳标记（`[amend YYYY-MM-DDTHH:MMZ]: <text>`）。多个修正会累积；审计跟踪可见。如果该家族不存在剧本，则修正会创建一个仅包含笔记的剧本（因此冷启动修正仍然会到达）。

### 工作示例

1. **冷启动：“Spurs 的下一场比赛何时进行？”** — `recall` 返回 `found=false`。遍历球队计分板，找到下一场即将到来的 Spurs 事件 ID，回答。教学事件：

   ```bash
   espn-pp-cli recall "Spurs 的下一场比赛何时进行？" --agent
   # found=false -> 发现
   espn-pp-cli teams basketball nba 24 --agent --select events.id,events.shortName,events.date
   # ...回答“周二 5 月 26 日 SA @ OKC, 事件 401747632”...
   espn-pp-cli teach --query "Spurs 的下一场比赛何时进行？" --resource-type events --resource 401747632
   # (附加 shell `&` 以使其后台运行)
   ```

2. **热启动：“Niners 的比赛今晚进行？”** — `recall` 返回 `found=true`, `results[0].entity_match="exact"`, `results[0].confidence>=2`。跳过发现；直接获取计分板：

   ```bash
   espn-pp-cli recall "Niners 的比赛今晚进行？" --agent
   # found=true, results=[{resource_id: "401547432", entity_match: "exact"}]
   espn-pp-cli boxscore 401547432 --agent
   ```

3. **跨别名命中：“49ers 的比赛今晚进行？”** — 从未直接教学。`recall` 解析 "49ers" → "San Francisco 49ers" 规范名称通过实体查找 (nfl_team 类型)，找到 "Niners 的比赛今晚进行？" 学习（相同的规范名称），返回 `found=true`。跳过发现。

4. **实体不匹配：“Cowboys 的比赛今晚进行？”** — 在非实体标记 (`game`, `tonight`) 上有 Niners 学习超过 Jaccard 地板，但实体规范名称不同 (Dallas Cowboys ≠ San Francisco 49ers)。过滤到 `mismatches`；召回返回 `found=false`。将其视为冷启动。

当循环中断时：`learnings list --warnings` 显示本地问题；`espn-pp-cli feedback "<what tripped you up>"` 记录摩擦，以便下次打印可以修复它。
