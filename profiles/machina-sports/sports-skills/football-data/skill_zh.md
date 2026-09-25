# 足球数据

在编写查询之前，请查阅 `references/api-reference.md` 以获取端点、ID 约定和数据形状信息。

## 设置

在首次使用前，检查 CLI 是否可用：
```bash
which sports-skills || pip install sports-skills
```
如果 `pip install` 失败（包未找到或 Python 版本错误），则从 GitHub 安装：
```bash
pip install git+https://github.com/machina-sports/sports-skills.git
```
该包需要 Python 3.10 或更高版本。如果您的默认 Python 版本较旧，请使用特定版本：
```bash
python3 --version  # 检查版本
# 如果 < 3.10，尝试：python3.12 -m pip install sports-skills
# 在 macOS 上使用 Homebrew：/opt/homebrew/bin/python3.12 -m pip install sports-skills
```
无需 API 密钥。

## 快速入门

优先使用 CLI，以避免 Python 导入路径问题：
```bash
sports-skills football get_daily_schedule
sports-skills football get_season_standings --season_id=premier-league-2025
```

Python SDK（替代方案）：
```python
from sports_skills import football

standings = football.get_season_standings(season_id="premier-league-2025")
schedule = football.get_daily_schedule()
```

## 关键：在进行任何查询之前

在进行任何数据端点调用之前，请验证：
- 赛季 ID 应从 `get_current_season(competition_id="...")` 派生——切勿硬编码。
- 球队 ID 应通过 `search_team(query="...")` 解析，并作为数字 `team_id` 传递。对于 `get_head_to_head`、`get_team_strength` 和 `get_match_forecast`，始终传递 ID——模糊名称（例如两个“巴黎”俱乐部）可能会解析到错误的球队。
- 该端点是否实际涵盖所讨论的联赛——请参阅下方的 **覆盖范围与来源映射**。不同来源的覆盖范围不均匀；未覆盖的调用将返回一个带有 `message` 的空负载，而不是数据。
- `get_event_xg` 和 `get_event_players_statistics`（带 xG）仅针对前五个联赛（EPL、La Liga、Bundesliga、Serie A、Ligue 1）调用。
- `get_season_leaders` 和 `get_missing_players` 仅针对英超联赛赛季（season_id 必须以 `premier-league-` 开头）调用。

## 选择赛季

从系统提示的日期中获取当前年份（例如，`currentDate: 2026-02-16` → 当前年份为 2026）。

- **如果用户指定了赛季**，则直接使用。
- **如果用户说“当前”、“最新”或未指定**：调用 `get_current_season(competition_id="...")` 获取活动赛季_id。不要猜测或硬编码年份。
- **赛季格式**：始终为 `{league-slug}-{year}`（例如，`"premier-league-2025"` 用于 2025-26 赛季）。年份是赛季的开始年份，而不是结束年份。
- **MLS 例外**：MLS 在一个日历年内运行春季-秋季。使用 `get_current_season(competition_id="mls")`。

## 覆盖范围与来源映射

此技能将多个免费来源组合在一起。**覆盖范围不统一**——每个端点仅在它底层的来源有数据时才起作用。在承诺答案之前检查这一点；当端点未覆盖时，它将返回一个带有解释性 `message` 的空负载（不会返回错误）——请阅读该消息并回退。

| 端点 | 来源 | 覆盖范围 |
|---|---|---|
| standings, schedules, teams, event summary/lineups/stats/timeline | ESPN | **所有联赛**（最广泛——骨干） |
| `get_event_xg`, `get_event_players_statistics`（xG 字段） | Understat | **仅限前五个**（EPL、La Liga、Bundesliga、Serie A、Ligue 1）。*不适用于 RFPL —— Understat 已停止支持。* |
| `get_season_leaders`, `get_missing_players` | FPL | **仅限英超联赛** |
| `get_player_profile`, `get_season_transfers`（市场价值） | Transfermarkt | 任何具有 `tm_player_id` 的球员 |
| `get_head_to_head` | football-data.co.uk | **11 个欧洲国内联赛**（EPL、Championship、La Liga、Serie A、Bundesliga、Ligue 1、Eredivisie、Primeira Liga、Scottish、Belgian、Turkish）。仅限同分联赛对决。 |
| `get_team_strength` | ClubElo、回退到本地 Elo | **欧洲俱乐部**（包括俄罗斯）。如果 ClubElo 出现故障，则回退到从 football-data.co.uk 计算的评分。 |
| `get_match_forecast` | ClubElo | **欧洲俱乐部**（包括俄罗斯）。没有回退——需要 ClubElo 的赛程信息。 |

经验法则：**ESPN 回答“发生了什么”的答案；增强来源（Understat/FPL/ClubElo/football-data.co.uk）仅在它们的覆盖区域内增加深度。** ESPN 始终是赛程/比分权威——切勿让增强来源覆盖 ESPN 的比分。

### 实际测试中的注意事项
- **`get_team_profile` 返回阵容。** `data.players[]` 包含当前阵容，带有 ESPN 运动员 ID、球衣号码和年龄——使用它而不是逐场收集名称。
- **`get_player_season_stats` 使用与所有其他相同的联赛缩写**（`serie-a-brazil`，而不仅仅是 ESPN 的 `bra.1`），并且它的 gamelog 是跨比赛的最后 ~5 场比赛，而不是一个赛季的总和。
- **罚球得分在时间线中为 `penalty_goal`。** 在与比分核对时，请计算 `goal` + `penalty_goal` + `own_goal`。
- **使用 ID 而不是模糊名称。** 对于 H2H/Strength/Forecast，首先使用 `search_team` 解析球队，并传递数字 `team_id`。像“巴黎圣日耳曼”这样的名称在名称解析过程中可能会合并到错误的俱乐部（巴黎 FC）。
- **ClubElo 休赛期差距**：当前日期的 `get_team_strength` 可能会遗漏在夏季休赛期的俱乐部（一个俱乐部的每周 Elo 期间可能不包括今天）。如果知名俱乐部返回未解析，请传递一个赛季日期（例如 `date="2026-03-01"`）。
- **ClubElo 故障**：`get_team_strength` 回退到本地计算的 Elo 并设置 `source: "local-elo"`。在跨多个调用比较数字之前，请检查该字段——本地刻度是分区分的，所以在其自己的分区内没有意义，跨分区的比较被拒绝。回退会尊重 `date`（它在该日期下评估分区，并且每个条目的 `as_of` 是最后计数的比赛）。`get_match_forecast` 没有回退，并且为空。
- **`get_match_forecast` 是短视程**：ClubElo 仅预测约一周内——在比赛日之间/休赛期之间为空。这是预期的，不是失败。
- **H2H 仅限同分联赛**：在杯赛或跨级别相遇的两个俱乐部不会显示；它计算的是在解析分区内进行的联赛对决。
- **H2H 将“未解析”与“从未相遇”区分开来**：football-data.co.uk 使用简短的异名/缩写（“FC Koln”、“M'gladbach”、“Sp Lisbon”）。每个 `teams[]` 中的俱乐部报告 `resolved` + `matched_as`；如果一个俱乐部是 `resolved: false`，零次相遇意味着查找失败，而不是俱乐部从未比赛过。

## 组合端点（混合搭配）

组合来源以获得更丰富的答案。并行运行独立的调用。

- **比赛预告**（`X vs Y`）：`search_team` ×2 → `get_head_to_head`（最近战绩）+ `get_team_strength(team_id, team_id_2)`（Elo 差距/热门）+ `get_match_forecast`（如果在一周内：W/D/L + 比分）。对于前五个联赛的对决，添加最近比赛的 `get_event_xg` 历史背景。
- **比赛报告**（赛后）：`get_event_summary` + `get_event_statistics` + `get_event_timeline`，对于前五个联赛 `get_event_xg` + `get_event_players_statistics`。
- **球队状态+背景**：`get_team_schedule`（最近结果）+ `get_team_strength`（当前 Elo & 排名）+ `get_missing_players`（英超仅限）+ 每场比赛 `get_event_xg`（前五个）。
- **竞争/德比深入分析**：`get_head_to_head`（所有时间记录+进球）+ `get_team_strength` 比较当前实力平衡。
- **赔率合理性检查**：`get_match_forecast` 提供免费的模型基准（W/D/L）以与 `kalshi` / `polymarket` 赌博技能进行比较。

当一个组合部分未覆盖（例如，前五个联赛外的 xG、MLS 的 H2H），请静默跳过它，并提供已覆盖的部分——不要因为一个缺失的来源而阻止整个答案。

## 命令

| 命令 | 描述 |
|---|---|
| `get_current_season` | 检测比赛的当前赛季 |
| `get_competitions` | 列出可用比赛及其当前赛季信息 |
| `get_competition_seasons` | 某个比赛的可用赛季 |
| `get_season_schedule` | 全赛季比赛赛程 |
| `get_season_standings` | 赛季的联赛榜 |
| `get_season_leaders` | 排名靠前的球员/领导者（英超仅限） |
| `get_season_teams` | 赛季中的球队 |
| `search_team` | 通过名称搜索球队 |
| `search_player` | 通过名称搜索球员 |
| `get_team_profile` | 球队信息+当前阵容（阵容） |
| `get_daily_schedule` | 所有联赛的日期比赛 |
| `get_event_summary` | 带有比分的比赛摘要 |
| `get_event_lineups` | 比赛阵容 |
| `get_event_statistics` | 比赛球队统计数据 |
| `get_event_timeline` | 比赛时间线（进球、黄牌、替补） |
| `get_team_schedule` | 特定球队的赛程 |
| `get_head_to_head` | 历史H2H结果+统计（欧洲国内联赛） |
| `get_team_strength` | Elo 评分/两队比较（欧洲俱乐部）；如果 ClubElo 出现故障，则回退到本地 Elo |
| `get_match_forecast` | ClubElo 胜/平/负+比分预测（约一周内） |
| `get_event_xg` | xG 数据（仅限前五个联赛） |
| `get_event_players_statistics` | 球员级别的比赛统计数据，可选 xG |
| `get_missing_players` | 受伤/不确定球员（英超仅限） |
| `get_season_transfers` | 通过 Transfermarkt 获取转会历史 |
| `get_player_season_stats` | 通过 ESPN 获取球员赛季统计数据 |
| `get_player_profile` | 球员资料（FPL 和/或 Transfermarkt） |

有关完整参数列表、返回形状和数据覆盖表的详细信息，请参阅 `references/api-reference.md`。

## 示例

示例 1：英超联赛榜
用户说：“显示英超联赛榜”
操作：
1. 调用 `get_current_season(competition_id="premier-league")` 获取当前赛季_id
2. 调用 `get_season_standings(season_id=<步骤 1 中的赛季_id>)`
结果：带有位置、球队、已赛、胜、平、负、GD、积分的联赛榜

示例 2：比赛报告
用户说：“阿森纳对利物浦的比赛结果如何？”
操作：
1. 调用 `get_daily_schedule()` 或 `get_team_schedule(team_id="359")` 找到事件_id
2. 调用 `get_event_summary(event_id="...")` 获取比分
3. 调用 `get_event_statistics(event_id="...")` 获取控球率、射门等
4. 调用 `get_event_xg(event_id="...")` 获取 xG 对比（英超——仅限前五个）
结果：带有比分、关键统计数据和 xG 的比赛报告

示例 3：球队深入分析
用户说：“深入分析切尔西近期的状态”
操作：
1. 调用 `search_team(query="Chelsea")` → team_id=363, competition=premier-league
2. 调用 `get_team_schedule(team_id="363", competition_id="premier-league")` → 找到最近的已关闭事件
3. 对于每场最近的比赛，并行调用：`get_event_xg`, `get_event_statistics`, `get_event_players_statistics`
4. 调用 `get_missing_players(season_id=<赛季_id>)` → 过滤切尔西受伤/不确定球员
结果：跨比赛的 xG 趋势、关键球员统计数据和伤病报告

示例 4：球员市场价值
用户说：“Saka 的市场价值是多少？”
操作：
1. 调用 `get_player_profile(tm_player_id="433177")` 获取 Transfermarkt 数据
2. 可选地添加 `fpl_id` 获取 FPL 统计数据
结果：市场价值、价值历史和转会历史

示例 5：非 PL 俱乐部
用户说：“告诉我关于科林蒂安的事情”
操作：
1. 调用 `search_team(query="Corinthians")` → team_id=874, competition=serie-a-brazil
2. 调用 `get_team_schedule(team_id="874", competition_id="serie-a-brazil")` 获取赛程
3. 选择一场最近的比赛并调用 `get_event_timeline(event_id="...")` 获取进球、黄牌、替补
结果：赛程、时间线事件（注意：巴西圣保罗联赛的 xG、FPL 统计和赛季领导者不可用）

示例 6：比赛预告（混合搭配）
用户说：“预告本周末阿森纳对曼城”
操作：
1. 调用 `search_team(query="Arsenal")` 和 `search_team(query="Manchester City")` → team_ids 359, 382
2. 并行调用：`get_head_to_head(team_id="359", team_id_2="382")`（最近战绩+进球）、`get_team_strength(team_id="359", team_id_2="382")`（Elo 差距+热门）、`get_match_forecast(team_id="359", team_id_2="382")`（W/D/L + 可能的比分，如果在一周内）
3. 综合：状态/战绩 + 实力平衡 + 模型赔率。跳过任何返回空的部件（例如，如果比赛在一周之外，则跳过预测）。
结果：结合了历史战绩、当前实力和免费模型预测的预告

## 不存在的命令——切勿调用这些

- ~~`get_standings`~~ — 正确的命令是 `get_season_standings`（需要 `season_id`）。
- ~~`get_live_scores`~~ — 不可用。使用 `get_daily_schedule()` 获取今天的比赛。
- ~~`get_team_squad`~~ / ~~`get_team_roster`~~ — 使用 `get_team_profile`：`data.players[]` 是当前阵容，带有 ESPN 运动员 ID（见 Gotchas）。`get_season_leaders` + `get_player_profile` 仍然是获取职业生涯数据的路径。
- ~~`get_transfers`~~ — 正确的命令是 `get_season_transfers`（需要 `season_id` + `tm_player_ids`）。
- ~~`get_match_results`~~ / ~~`get_match`~~ — 使用 `get_event_summary` 并提供 `event_id`。
- ~~`get_player_stats`~~ — 使用 `get_event_players_statistics` 获取比赛级统计数据，或 `get_player_profile` 获取职业生涯数据。
- ~~`get_scores`~~ / ~~`get_results`~~ — 使用 `get_event_summary` 并提供 `event_id`。
- ~~`get_fixtures`~~ — 使用 `get_daily_schedule` 获取今天的比赛或 `get_season_schedule` 获取一个完整赛季。
- ~~`get_league_table`~~ — 使用 `get_season_standings` 并提供 `season_id`。

如果命令不在上面的命令表中，则不存在。不要尝试未列出的命令。

## 错误处理

当命令失败（事件_id 错误、数据缺失、网络错误等）时，**不要向用户显示原始错误**。相反：
1. 静默捕获它——将失败视为探索性遗漏。
2. 尝试替代方案——如果一个事件_id 返回无数据，调用 `get_daily_schedule()` 或 `get_team_schedule()` 以发现正确的 ID。
3. 仅在穷尽替代方案后报告失败——使用干净的提示（例如，“我找不到这场比赛——你能确认球队或日期吗？”）。

## 故障排除

错误：`sports-skills` 命令未找到
原因：包未安装
解决方案：运行 `pip install sports-skills`。如果不在 PyPI 上，则从 GitHub 安装：`pip install git+https://github.com/machina-sports/sports-skills.git`

错误：`ModuleNotFoundError: No module named 'sports_skills'`
原因：包未安装或路径问题
解决方案：安装包。优先使用 CLI 而不是 Python 导入，以避免路径问题

错误：`get_season_leaders` 或 `get_missing_players` 对于非 PL 联赛返回空
原因：这些命令仅适用于英超联赛；它们对其他联赛静默返回空
解决方案：检查 `references/api-reference.md` 中的数据覆盖表。对于其他联赛，使用 `get_event_players_statistics` 获取球员数据

错误：`get_team_profile` 返回没有球员
原因：ESPN 在给定联赛中为该球队 ID 没有阵容（错误的 `league_slug`，或国家队/青年队）
解决方案：传递俱乐部所在的 `league_slug`（例如 `serie-a-brazil`）；对于比赛日阵容使用 `get_event_lineups`

错误：赛季_id 格式错误
原因：赛季 ID 必须遵循 `{league-slug}-{year}` 格式
解决方案：使用 `get_current_season(competition_id="...")` 发现正确的格式。示例：`"premier-league-2025"`，而不是 `"2025-2026"` 或 `"EPL-2025"`

错误：最近比赛的 xG 数据不可用
原因：Understat 数据可能在比赛结束后 24-48 小时内滞后
解决方案：如果 `get_event_xg` 对于最近的顶级联赛比赛返回空，请稍后重试。仅适用于 EPL、La Liga、Bundesliga、Serie A、Ligue 1

错误：球队或事件 ID 未知
原因：ID 是猜测的，而不是查找的
解决方案：使用 `search_team(query="team name")` 找到球队 ID，或 `get_daily_schedule` / `get_season_schedule` 找到事件 ID。切勿猜测 ID。
