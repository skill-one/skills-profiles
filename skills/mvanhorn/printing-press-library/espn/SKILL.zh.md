---
name: pp-espn
description: 在用户询问实时体育比分、赛程排名、球队数据、比赛总结（含赛果统计、得分榜、关键得分、赔率及胜率）、NFL/NBA/MLB/NHL/NCAA/MLS/EPL/WNBA比赛、球队赛程、投票或排名时，请使用此技能。ESPN体育CLI提供10个联赛的实时比分、离线搜索、对阵比较及丰富的每场比赛总结数据。无需API密钥。支持自然语言触发，如“湖人队比赛的比分是多少”、“爱国者队本周赛程”、“NFL赛程排名”、“马刺队今晚比赛的赛果统计”、“chiefs队对eagles队的交锋记录”、“AP投票榜首的是谁”。
---

# ESPN — 打印机 CLI

## 前置条件：安装 CLI

此技能驱动 `espn-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它缺失，请先安装：

1. 通过打印机安装程序安装。它将二进制文件默认设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install espn --cli-only
   ```
2. 验证：`espn-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）：

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/espn/cmd/espn-pp-cli@latest
```

如果安装后 `--version` 报告 "command not found"，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，不要继续使用技能命令。

## 何时使用此 CLI

当用户想要快速查找体育信息时使用此 CLI - 当前比分、排名、即将进行的赛程、对决记录或丰富的每场比赛摘要（比分单、得分榜、得分回放、赔率、获胜概率）。也适用于跨联赛发现（`today`）和在同步数据中离线搜索。

如果用户有付费数据源（如 Stats Perform 或 Sportradar）提供更清晰的数据，或者他们需要实时 websocket 更新（ESPN 的端点是轮询式的），则不要使用此 CLI。对于单独的博彩赔率，每场比赛的 `summary` 有效负载包括它们，但没有跨联赛的赔率命令。

## 独特功能

仅因本地同步和跨联赛工具而存在的命令。

### 跨联赛发现

- **`today`** — 一次调用即可获取所有主要体育项目的当天比分。无需先选择运动项目，即可快速获得“今晚有什么比赛”的答案。

- **`trending`** — 按当前人气对所有联赛中最受关注的运动员和球队进行排名。适用于“现在谁很火”而无需提及运动项目。

- **`dashboard`** — 从 `~/.config/espn-pp-cli/config.toml` 中的 `[favorites]` 读取，并显示每个收藏球队在各个联赛中的比分，一次调用即可。

- **`watch <sport> <league> --event <game_id>`** — 某个特定比赛的实时比分更新（每 30 秒轮询一次）。使用 `scores` 或 `today` 找到比赛，然后使用 `watch` 实时跟踪它。

### 比赛状态智能

- **`summary <sport> <league> --event <game_id>`** — 包括比分单、得分榜、得分回放、赔率和获胜概率的详细比赛摘要。每场比赛最丰富的有效负载。

- **`boxscore <event_id>`** — 某个事件每个球员的比分单，运动+联赛从最近的比分缓存命中中推断。传递 `--sport`/`--league` 以跳过推断。

- **`plays <sport> <league> --event <id>`** — 某个事件的逐场回放。可选的 `--limit`（默认 200）。

- **`recap <sport> <league>`** — 联赛中最最近完成的比赛的赛后回放，包括比分单和得分榜。

- **`scoreboard <sport> <league>`** — 带有日期过滤、周/组选择器和比赛元数据的实时比分板。

- **`odds <sport> <league>`** — 今晚赛程的让分、大小分和投注线，从比分板有效负载中派生（没有每场比赛摘要调用）。

### 排名和排名

- **`standings <sport> <league>`** — 联盟/分区的排名。

- **`rankings <sport> <league>`** — 当前 AP、教练和 CFP 汇票排名（NCAAF/NCAAM）。

- **`streak <sport> <league>`** — 联赛中各队的当前胜负连续记录，从同步数据中计算得出。

- **`rivals <sport> <league>`** — 联赛中球队之间的对决记录，从同步数据中获取。

- **`h2h <team1> <team2> --sport <s> --league <l>`** — 某一对更详细的对决信息，包括平均得分和最近交锋列表。

- **`sos <sport> <league>`** — 每个队伍的赛程强度，从排名有效负载中派生，降序排列。

### 人物

- **`leaders <sport> <league> [--category <name>]`** — 按类别进行统计的领先者，可选过滤器。

- **`compare <athlete1> <athlete2> --sport <s> --league <l>`** — 两位运动员的赛季统计对比。歧义名称会列出候选者并退出 2。

- **`injuries <sport> <league>`** — 联盟中活跃的伤病报告，按球队分组。

- **`transactions <sport> <league>`** — 最近的交易、签约和弃权。

### 本地存储

- **`sync`** — 将运动+联赛数据集拉入本地 SQLite 以进行离线分析。

- **`search "<query>"`** — 在同步的事件和新闻中进行全文搜索。

- **`sql <query>`** — 对本地数据库运行只读 SQL 查询。

## 命令参考

实时操作：

- `espn-pp-cli scores <sport> <league>` — 当前比分
- `espn-pp-cli today` — 所有主要体育项目的当天比分
- `espn-pp-cli scoreboard <sport> <league>` — 带有可选日期过滤的比分板
- `espn-pp-cli watch <sport> <league> --event <game_id>` — 某个比赛的实时比分轮询
- `espn-pp-cli standings <sport> <league>` — 联赛排名
- `espn-pp-cli trending` — 联赛中最受关注的运动员和球队
- `espn-pp-cli dashboard` — 从 `~/.config/espn-pp-cli/config.toml` 中的收藏夹获取快照

球队详情：

- `espn-pp-cli teams <sport> <league> <team_id>` — 某个球队的赛程（过去 + 即将进行）
- `espn-pp-cli teams get <sport> <league> <team_id>` — 球队记录、链接和标志
- `espn-pp-cli teams list <sport> <league>` — 联赛中的所有球队
- `espn-pp-cli streak <sport> <league>` — 从同步数据中获取的当前胜负连续记录
- `espn-pp-cli rivals <sport> <league>` — 联赛中球队之间的对决记录，从同步数据中获取
- `espn-pp-cli h2h <team1> <team2> --sport <s> --league <l>` — 某个球队对的更详细信息（平均得分、最近交锋）
- `espn-pp-cli sos <sport> <league>` — 赛程强度，降序排列

比赛详情：

- `espn-pp-cli summary <sport> <league> --event <game_id>` — 完整比赛摘要（比分单、得分榜、得分回放、赔率、获胜概率）
- `espn-pp-cli boxscore <event_id>` — 仅比分单子树（运动/联赛从缓存中推断）
- `espn-pp-cli plays <sport> <league> --event <id>` — 逐场回放（可选 `--limit`，默认 200）
- `espn-pp-cli recap <sport> <league>` — 最最近完成的比赛回放
- `espn-pp-cli odds <sport> <league>` — 今晚赛程的让分、大小分和投注线

人物：

- `espn-pp-cli leaders <sport> <league> [--category <name>]` — 按类别进行统计的领先者
- `espn-pp-cli compare <athlete1> <athlete2> --sport <s> --league <l>` — 两位运动员的赛季统计对比
- `espn-pp-cli injuries <sport> <league>` — 活跃的伤病报告
- `espn-pp-cli transactions <sport> <league>` — 最近的交易、签约和弃权

投票和排名：

- `espn-pp-cli rankings <sport> <league>` — AP、教练和 CFP 汇票

信息：

- `espn-pp-cli news <sport> <league>` — 最新新闻

发现和本地：

- `espn-pp-cli search "<query>"` — 在同步的事件和新闻中进行全文搜索
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

一个 `today` 调用涵盖跨联赛活动，一个 `scores` 用于你关心的联赛，一个 `standings` 用于提供背景信息。嵌套的 `--select` 路径将来自数十 KB 的比分板有效负载削减到实际需要的字段——这对于保持代理上下文小至关重要。

### 赛前研究（使用同步数据）

```bash
espn-pp-cli sync --sport football --league nfl
espn-pp-cli rivals football nfl --agent         # 从同步数据中获取的历史记录
espn-pp-cli streak football nfl --agent         # 当前连续记录
espn-pp-cli summary football nfl --event <id> --agent   # 包含赔率和比分单的特定比赛的完整有效负载
```

运行一次 `sync`，然后 `rivals` 和 `streak` 从本地存储中即时回答。`summary` 是特定比赛的 richest 单一有效负载（比分单、得分榜、得分回放、赔率、获胜概率）。

### 同步后的离线搜索

```bash
espn-pp-cli sync --sport football --league nfl
espn-pp-cli search "Mahomes"                    # 在本地存储中查找
```

在连接不良的环境中进行重复查找或批量分析历史数据时很有用。

### 收藏夹仪表板

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

一次调用即可显示每个收藏球队在各个联赛中的今晚比赛状态，按联赛分组。跨联赛获取并行运行，并报告成功结果和部分失败结果。

### 赛前赔率和球员挖掘

```bash
espn-pp-cli odds basketball nba --agent          # 今晚的让分 / 大小分 / 投注线
espn-pp-cli leaders basketball nba --category points --agent
espn-pp-cli compare "LeBron James" "Stephen Curry" --sport basketball --league nba --agent
espn-pp-cli boxscore <event_id> --agent          # 赛后球员统计
espn-pp-cli plays basketball nba --event <id> --limit 50 --agent
```

`odds` 读取比分板的每场比赛赔率（没有每场比赛摘要调用）。`leaders --category` 过滤到单个统计类别。`compare` 通过名称解析运动员 ID，列出候选者并在歧义时退出 2。`boxscore` 从最近的缓存命中中推断运动+联赛；传递 `--sport`/`--league` 以跳过推断。

## 认证设置

**无需认证。** ESPN 的公共端点不需要 API 密钥。`auth` 命令存在以保持一致性，但它是空的。

可选配置：
- `ESPN_CONFIG` — 覆盖配置文件路径
- `ESPN_BASE_URL` — 覆盖基本 URL（用于代理或镜像）
- `NO_COLOR` — 标准的无颜色环境变量

## 代理模式

向任何命令添加 `--agent`。扩展为 `--json --compact --no-input --no-color --yes`。使用 `--select` 进行字段挑选，`--dry-run` 预览请求，`--no-cache` 跳过 GET 缓存。

### 过滤输出

`--select` 接受点路径以深入嵌套响应；数组逐元素遍历：

```bash
espn-pp-cli <command> --agent --select id,name
espn-pp-cli <command> --agent --select items.id,items.owner.name
```

使用此方法将巨大的有效负载削减到您实际需要的字段——这对于深度嵌套的 API 响应至关重要。

### 响应包

数据层命令将输出包装在 `{"meta": {...}, "results": <data>}` 中。解析 `.results` 获取数据，`.meta.source` 知道它是 `live` 还是本地。当 stdout 是 TTY 时，`N results (live)` 摘要仅在 stderr 中打印；管道/代理消费者在 stdout 上看到纯 JSON。

## 退出代码

| 代码 | 含义 |
|------|---------|
| 0 | 成功 |
| 2 | 使用错误 |
| 3 | 未找到（球队、比赛、运动员） |
| 5 | API 错误 |
| 7 | 被限流 |

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

1. **空、`help` 或 `--help**` → 运行 `espn-pp-cli --help`
2. **`install**` → CLI；**`install mcp**` → MCP
3. **其他任何内容** → 从用户意图解析 `<sport> <league>`（例如，“Lakers” → `basketball nba`），检查 `which espn-pp-cli`（如果缺失则提供安装），使用 `--agent` 运行。

<!-- pr-218-features -->
## 自动学习

两步协议：`recall` 在发现之前，`teach &` 在发出之前。CLI 执行实体感知匹配验证，并显示查询系列的存储剧本；您阅读包封并遵循六分支决策树。跳过任何一侧都会导致未来会话中免费召回命中减少。

### 第一步：`recall` 在任何发现之前

在新用户问题的 `scoreboard`、`teams`、`boxscore`、`search`、`standings` 或任何其他发现命令之前运行：

```bash
espn-pp-cli recall "<user's question>" --agent
```

响应包封：

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
  "mismatches": [ /* 仅当 --debug-mismatches */ ],
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

### 第二步：六分支决策树

按顺序读取 `playbook`、`notes`、`results[0]` 和警告：

```
if Playbook 存在:
    -> 首先逐字读取 Playbook.notes（CLI 暴露的 workarounds + gotchas）
    -> 按顺序重放 Playbook.steps，用 Playbook.slots_resolved 条目替换实体槽标记。如果一个步骤的槽未解决，则仅回退该步骤的发现。
    -> Playbook 的 expected_tool_calls 是预算；如果您发现自己运行的材料更多，请在会话结束时通过 teach-playbook 记录偏差。

elif Notes 存在（没有 Playbook）:
    -> 在任何发现步骤之前逐字读取 Notes；即使没有结构化编排，它们也包含此查询系列的已知 gotchas。

elif Found AND Results[0].EntityMatch == "exact" AND Results[0].Confidence >= 2:
    -> 跳过发现；并行获取 Results[*].ResourceID 的实时数据（例如，espn-pp-cli boxscore <eid> 对于一个事件，espn-pp-cli teams ... 对于一个球队）

elif Found AND Results[0].EntityMatch == "partial":
    -> 候选提示，不是命中；在信任之前读取资源标题进行验证

elif (任何 --debug-mismatches 传递时 Mismatches[] 中的行):
    -> 视为冷启动；存储的学习适用于不同的实体（例如，“Cowboys”学习不会满足“Niners”查询——不同的 canonical）

else:  // Found == false, 没有剧本，没有笔记
    -> 冷启动；正常运行发现；事后教授答案，并通过 teach --playbook-file --playbook-notes-file 记录剧本 + 笔记，以便下次相同系列的会话更快。
```

剧本和笔记与每个资源路径正交。召回响应可以同时携带剧本和 Results[] 命中——使用剧本告诉您要运行哪些编排；资源命中会短路特定步骤。默认跳过 `mismatches`；仅在调查冷启动意外时传递 `--debug-mismatches`。

### 第三步：始终读取 `warnings`

- `low_confidence`: 在 `confidence<2` 时存在行。将其视为提示，而非跳过发现的命中。
- `resource_not_in_store`: 本地存储中没有指向学习点的资源。匹配验证器无法分类实体 — 直接获取并重新评估。
- 顶层 `no_learnings_for_query_family`: 表格在Jaccard地板以上没有行。纯粹的冷启动。

### 第 4 步：`teach &` 在最终确定您的响应后

在组装包含事件/团队 ID 的用户界面响应，但在发出之前，在后台执行 teach 调用。附加 shell `&` 以使调用立即返回，并且不会阻塞用户界面响应：

```bash
espn-pp-cli teach --query "<用户的问题>" --resource-type <events|news|teams> --resource <id1> --resource <id2>
# (附加 shell `&` 以将其置于后台)
```

成功时保持静默。教 **最具体** 的资源 — 如果用户询问“下一场马刺队比赛什么时候”，而您通过团队记分牌找到事件 `401747632`，请教该事件 ID，而不是团队 ID。CLI 使用种子实体查找（NFL/NBA/MLB/MLS 团队名册，具有别名，如 Niners/49ers/SF）在召回时进行跨别名解析，因此“Niners”下的 teach 将自动满足未来的“49ers”查询。

### 第 5 步：当发现需要 >5 次调用时记录剧本

如果您运行了超过 5 次工具调用来回答问题，并且您发现了 CLI 没有显示的解决方案（静默丢弃的标志、未记录的参数、分页技巧、有效载荷陷阱），请记录它们，以便下次相同查询系列的会话跳过发现。两种显示方式：

```bash
# 常见情况：与资源 teach 一起
espn-pp-cli teach --query "<问题>" --resource-type <类型> --resource <id> \
  --playbook-file ~/playbooks/season-recap.json \
  --playbook-notes-file ~/playbooks/season-recap-notes.md
# (附加 shell `&` 以将其置于后台)

# 独立：仅笔记或配方
espn-pp-cli teach-playbook --query "<问题>" \
  --playbook-file ~/playbooks/season-recap.json \
  --notes "byathlete needs seasontype=2; categories has dup labels"
```

剧本文件是 JSON，具有 `steps`、`entity_slots`、`expected_tool_calls`。笔记文件是 markdown，包含原文的陷阱。任一字段可以为空；两个字段都为空将被拒绝。剧本按结构化查询系列（去除实体）进行键控，因此从“勇士队如何结束本赛季”中学习的配方适用于活塞队、热火队以及所有其他形状相同的团队查询。

当您确实在未来的召回中找到剧本时，将其视为事实依据：使用 `slots_resolved` 替换重播步骤，跳过剧本已经记录的发现步骤，并在任何步骤之前阅读 `notes`。

### 第 6 步：当您的调试响应确定更正时 `playbook amend &`

如果您的调试协议响应确定了笔记或剧本应知道的更正 — 一个解决方案、一个未记录的端点形状、一个过时的字段名、观察到的模式漂移、一个空有效载荷回退 — 在发出您的用户界面响应之前，执行 `playbook amend`。与 `teach` 相同，采用“发射并忘记”的态度。

```bash
espn-pp-cli playbook amend \
  --query "<确切的召回查询字符串>" \
  --add-note "<您的具体更正>"
# (附加 shell `&` 以将其置于后台)
```

什么值得更正：本会话中观察到的行为，未来您会从中受益。值得更正的示例：
- "摘要端点用 `{meta, results}` 包裹响应 — 数据位于 `.results.header`，而不是 `.header`"
- "compare 返回空 `team` 字段，对于其团队不在当前季后赛中的运动员"
- "byathlete 类别索引平均篮板在本赛季从 general[9] 漂移到 general[11]"

笔记中不应包含：
- 年度特定答案（“Curry 在他最后一场比赛中命中 4-16”）。这是响应，不是学习。
- 团队特定或运动员特定数据，剧本已经在运行时检索。
- 重述现有笔记中已经说明的内容的陈述。

更正命令将时间戳标记（`[amend YYYY-MM-DDTHH:MMZ]: <text>`）附加到系列的现有笔记中。多次更正累积；审计跟踪可见。如果系列还没有剧本，更正将创建一个仅包含笔记的剧本（以便冷启动更正仍然有效）。

### 工作示例

1. **冷启动：“下一场马刺队比赛什么时候？”** — `recall` 返回 `found=false`。遍历团队记分牌，找到下一场即将到来的马刺队事件 ID，回答。教该事件：

   ```bash
   espn-pp-cli recall "下一场马刺队比赛什么时候?" --agent
   # found=false -> 发现
   espn-pp-cli teams basketball nba 24 --agent --select events.id,events.shortName,events.date
   # ...回答 "5 月 26 日周二 SA @ OKC, 事件 401747632"...
   espn-pp-cli teach --query "下一场马刺队比赛什么时候?" --resource-type events --resource 401747632
   # (附加 shell `&` 以将其置于后台)
   ```

2. **热启动：“49ers 比赛今晚”** — `recall` 返回 `found=true`，`results[0].entity_match="exact"`，`results[0].confidence>=2`。跳过发现；直接获取比分：

   ```bash
   espn-pp-cli recall "49ers 比赛今晚" --agent
   # found=true, results=[{resource_id: "401547432", entity_match: "exact"}]
   espn-pp-cli boxscore 401547432 --agent
   ```

3. **跨别名命中：“49ers 比赛今晚”** — 从未直接教过。`recall` 通过实体查找解析“49ers”→“San Francisco 49ers”规范，找到“Niners 比赛今晚”学习（相同的规范），返回 `found=true`。跳过发现。

4. **实体不匹配：“Cowboys 比赛今晚”** — 在非实体标记（`game`，`tonight`）上高于 Jaccard 地板的 Niners 学习，但实体规范不同（Dallas Cowboys ≠ San Francisco 49ers）。过滤到 `mismatches`；召回返回 `found=false`。将其视为冷启动。

当循环中断时：`learnings list --warnings` 显示本地问题；`espn-pp-cli feedback "<什么让您卡住了>"` 记录摩擦，以便下次打印修复它。

---

## Agent Workflow Features

此 CLI 暴露了三个从 cli-printing-press PR #218 补丁中的共享 agent-workflow 功能。

### 命名配置文件

将一组标志在名称下持久化，并在多次调用中重用它们。

```bash
# 将当前非默认标志保存为命名配置文件
espn-pp-cli profile save <name>

# 使用配置文件 — 将其值覆盖到您未显式设置的任何标志
espn-pp-cli --profile <name> <命令>

# 列出/检查/删除
espn-pp-cli profile list
espn-pp-cli profile show <name>
espn-pp-cli profile delete <name> --yes
```

标志优先级：显式标志 > 环境变量 > 配置文件 > 默认值。

### --deliver

将命令输出路由到 stdout 之外的接收器。当代理需要将结果交给文件、webhook 或其他进程，而无需管道时，这很有用。

```bash
espn-pp-cli <命令> --deliver file:/path/to/out.json
espn-pp-cli <命令> --deliver webhook:https://hooks.example/in
```

文件接收器原子写入（tmp + 重命名）。webhook 接收器 POST `application/json`（或 `application/x-ndjson` 当 `--compact` 设置时）。未知方案将产生一个列出支持集的结构化拒绝。

### feedback

从循环的代理端记录关于此 CLI 的带内反馈。默认情况下仅本地；无需配置即可安全调用。

```bash
espn-pp-cli feedback "什么让您惊讶或卡住了"
espn-pp-cli feedback list         # 显示本地条目
espn-pp-cli feedback clear --yes  # 清除
```

条目追加到 `~/.espn-pp-cli/feedback.jsonl` 作为 JSON 行。当 `ESPN_FEEDBACK_ENDPOINT` 设置，并且传递了 `--send` 或 `ESPN_FEEDBACK_AUTO_SEND=true` 时，条目也会 POST 到上游（非阻塞 — 本地写入始终成功）。
