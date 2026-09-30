---
name: pp-movie-goat
description: 将TMDb的发现引擎与OMDb的多源评分相结合的电影CLI——并提供一个SQLite观看列表，可标记您当前服务上正在播放的内容。触发短语：`今晚我应该看什么`，`我可以在哪里流式传输<title>`，`评分<title>`，`比较<title>和<title>`，`<人物>的电影作品是什么`，`计划一个<系列>马拉松`，`使用movie-goat`，`运行movie-goat`。
---

# Movie Goat — 打印机 CLI

## 前置条件：安装 CLI

此技能驱动 `movie-goat-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它缺失，请先安装它：

1. 通过打印机安装程序安装。它默认将二进制文件设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install movie-goat --cli-only
   ```
2. 验证：`movie-goat-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）：

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/movie-goat/cmd/movie-goat-pp-cli@latest
```

如果安装后 `--version` 报告 "command not found"，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，不要继续使用技能命令。

## 何时使用此 CLI

当代理需要回答需要结合流媒体可用性和多源评分的电影爱好者问题时，请使用 Movie Goat。它是今晚选择场景、系列马拉松计划和评分职业生涯时间线的正确选择。它不适用于票房追踪、评论情感分析或任何需要 LLM 风格的剧情或评论摘要的工作流。

## 何时不使用此 CLI

不要为需要创建、更新、删除、发布、评论、点赞、邀请、订购、发送消息或更改远程状态的请求激活此 CLI。此打印 CLI 仅提供用于检查、导出、同步和分析的只读命令。

## 独特功能

这些功能在任何其他工具中都不可用。

### 电影爱好者仪式
- **`tonight`** — 从您流媒体服务上实际播放的热门标题中挑选今晚要观看的内容。

  _当代理需要流媒体过滤的短列表时使用；一个调用可以替代在 TMDb/RT/JustWatch 之间切换标签页。_

  ```bash
  movie-goat-pp-cli tonight --mood thriller --max-runtime 120 --providers netflix,max --region US --json
  ```
- **`ratings`** — 为任何标题在一个卡片中提供 TMDb + IMDb + 罗伯特·汤姆森 + Metacritic 评分。

  _当代理需要标题的规范多源评分时使用；如果 OMDB_API_KEY 未设置，则会优雅地降级为仅 TMDb。_

  ```bash
  movie-goat-pp-cli ratings 550 --json
  ```
- **具有重制版本意识的标题解析** — 接受标题而不是 TMDb ID 的每个命令，在标题共享时都会明确说明。

  _TMDb 的搜索按专有的相关性分数排名，因此 `"Sabrina"` 解析为 1995 年的重制版，尽管 1954 年的 Wilder 原版评分更高。当标题有多个评分良好的匹配项时，CLI 在两个渠道上报告：人类在 stderr 上的通知，以及 stdout 上的 `meta.ambiguous` 记录，供从未读取 stderr 的消费者使用。使用 `--year`、`"Title (YYYY)"` 后缀或 ID 来固定您想要的那个。_

  ```bash
  movie-goat-pp-cli ratings "Sabrina" --year 1954 --json
  ```
- **`marathon`** — 计划带有观看顺序、总运行时间和建议休息时间的系列马拉松。

  _当计划活动观看时使用；代理可以将时间表共享给一个小组。_

  ```bash
  movie-goat-pp-cli marathon "The Avengers" --order release --breaks-every 240 --json
  ```
- **`career`** — 探索任何演员或导演的完整电影作品，包括评分和编年史。

  _当代理需要评分的编年史电影作品时使用；用跨源评分取代扁平的 IMDb 列表。_

  ```bash
  movie-goat-pp-cli career "Christopher Nolan" --since 2010 --role director --json
  ```
- **`versus`** — 在评分、演员阵容、运行时间和流媒体方面并排比较两部电影或节目。

  _当代理必须在两个最终候选者之间选择时使用；一个命令显示他们在每个维度上的差异。_

  ```bash
  movie-goat-pp-cli versus 550 27205 --region US --json
  ```
- **`collaborators`** — 列出在一个人名下出现两次或更多次的人，包括计数和标题。

  _当代理正在研究电影制作人的圈子时使用；机械地展示反复出现的副导演/作曲家/演员。_

  ```bash
  movie-goat-pp-cli collaborators "Christopher Nolan" --min-count 3 --role crew --json
  ```

### 复合的本地状态
- **`watchlist list`** — 本地 SQLite 观看列表；标记可在您的服务上流媒体播放的行。

  _每周使用以从保存的列表中提取可流媒体播放的项目；消除了针对每个标题的临时 JustWatch 检查。_

  ```bash
  movie-goat-pp-cli watchlist list --available --providers netflix,max --region US --json
  ```
- **`queue`** — 基于您的观看列表的建议和相似项的下一个观看选择。

  _当代理需要从保存的兴趣中派生的最新队列时使用；结合本地状态和 API 推荐。_

  ```bash
  movie-goat-pp-cli queue --limit 20 --providers netflix,max --region US --json
  ```

## 命令参考

**auth** — 管理 TMDB_API_KEY 和 OMDB_API_KEY 凭据

- `movie-goat-pp-cli auth status` — 显示 TMDb 和 OMDb 凭据的认证状态
- `movie-goat-pp-cli auth set-token` — 将 TMDb API 令牌保存到配置文件
- `movie-goat-pp-cli auth set-omdb-token` — 将可选的 OMDb API 令牌保存到配置文件
- `movie-goat-pp-cli auth logout` — 清除存储的凭据

**discover** — 使用丰富的过滤器发现电影和电视节目

- `movie-goat-pp-cli discover movies` — 按类型、年份、评分、认证、演员阵容、制作团队、流媒体提供者和更多内容发现电影
- `movie-goat-pp-cli discover tv` — 按类型、年份、评分、网络和流媒体提供者发现电视节目

**genres** — 获取电影和电视的类型列表

- `movie-goat-pp-cli genres movies` — 获取电影类型列表
- `movie-goat-pp-cli genres tv` — 获取电视类型列表

**movies** — 搜索和浏览电影

- `movie-goat-pp-cli movies get` — 获取有关电影的详细信息，包括演员阵容、评分和流媒体可用性
- `movie-goat-pp-cli movies now-playing` — 获取当前正在影院上映的电影
- `movie-goat-pp-cli movies popular` — 获取当前热门电影
- `movie-goat-pp-cli movies search` — 按标题搜索电影
- `movie-goat-pp-cli movies top-rated` — 获取最高评分的电影
- `movie-goat-pp-cli movies upcoming` — 获取即将上映的电影

**multi** — 跨电影、电视节目和人物的多重搜索

- `movie-goat-pp-cli multi <query>` — 在单个查询中搜索电影、电视节目和人物

**people** — 搜索和浏览人物（演员、导演、制作团队）

- `movie-goat-pp-cli people get` — 获取有关人物的详细信息，包括他们的作品列表
- `movie-goat-pp-cli people popular` — 获取热门人物
- `movie-goat-pp-cli people search` — 按名称搜索人物

**trending** — 获取热门电影、电视节目和人物

- `movie-goat-pp-cli trending all` — 获取热门电影、电视和人物
- `movie-goat-pp-cli trending movies` — 获取热门电影
- `movie-goat-pp-cli trending people` — 获取热门人物
- `movie-goat-pp-cli trending tv` — 获取热门电视节目

**tv** — 搜索和浏览电视节目

- `movie-goat-pp-cli tv airing-today` — 获取今天播放的电视节目
- `movie-goat-pp-cli tv get` — 获取有关电视节目的详细信息
- `movie-goat-pp-cli tv on-the-air` — 获取当前正在播放的电视节目
- `movie-goat-pp-cli tv popular` — 获取当前热门电视节目
- `movie-goat-pp-cli tv search` — 按标题搜索电视节目
- `movie-goat-pp-cli tv top-rated` — 获取最高评分的电视节目

### 找到正确的命令

当您知道要做什么但不知道哪个命令可以做到时，直接询问 CLI：

```bash
movie-goat-pp-cli which "<您自己的能力描述>"
```

`which` 将自然语言的能力查询解析为 CLI 的精选功能索引中的最佳匹配命令。退出代码 `0` 表示至少有一个匹配；退出代码 `2` 表示没有自信的匹配——回退到 `--help` 或使用更窄的查询。

## 配方

### 今晚、高评分、在我的服务上

```bash
movie-goat-pp-cli tonight --mood drama --max-runtime 130 --providers netflix,max,prime --region US --agent --select "results.title,results.year,results.rating,results.providers"
```

流媒体过滤的短列表，仅包含代理需要决定的高引力字段。

### 观看列表扫描

```bash
movie-goat-pp-cli watchlist list --available --providers netflix,max --region US --agent
```

每周检查：哪些保存的标题在我的服务上变成了可流媒体播放。

### 评分职业生涯深入分析

```bash
movie-goat-pp-cli career "Lynne Ramsay" --role director --agent --select "credits.title,credits.year,credits.rating_imdb,credits.rating_rt"
```

受代理限制的编年史电影作品，包含重要的跨源评分列。

### 在两个最终候选者之间选择

```bash
movie-goat-pp-cli versus 27205 87108 --region US --agent
```

Inception 与 Tenet 的对齐比较卡片；评分、运行时间、演员阵容重叠、提供者。

### 不更改 shell 环境存储两个 API 密钥

```bash
movie-goat-pp-cli auth set-token YOUR_TMDB_API_KEY
movie-goat-pp-cli auth set-omdb-token YOUR_OMDB_API_KEY
movie-goat-pp-cli auth status --agent
```

将两个凭据写入 `~/.config/movie-goat-pp-cli/config.toml`（模式 `0600`），以便机器上的每个代理和 shell 都可以看到它们，而不仅仅是导出环境变量的那个。`auth status` 报告 `authenticated`、`omdb_configured` 和 `omdb_source`，以便代理可以在运行 `ratings` 之前判断 IMDb / RT / Metacritic 列表是否会填充。

### 固定原版，而不是重制版

```bash
movie-goat-pp-cli ratings "Sabrina" --year 1954 --agent
movie-goat-pp-cli ratings "Sabrina (1954)" --agent
movie-goat-pp-cli versus "Sabrina (1954)" "Sabrina (1995)" --agent
```

`ratings`、`marathon` 和 `watchlist add` 都接受 `--year`；每个接受标题的命令（包括两个位置参数的 `versus`）都接受内联 `"Title (YYYY)"`
后缀。如果没有这些，CLI 仍然会接受 TMDb 的最高排名结果，但会在 stderr 上打印竞争对手的 ID：

```
warn: "Sabrina" 在 TMDb 上匹配 3 个标题；使用 id 11860 — Sabrina (1995).
      TMDb 的搜索相关性将其排在首位，但 Sabrina (1954) 的评分更高 (1373 vs 703)。
      其他匹配项：
        6620  Sabrina (1954)
        503902  Sabrina (2018)
      使用 --year <YYYY>、一个 "title (YYYY)" 后缀或 TMDb id 来消除歧义。
```

`/search/*` 按照一个 TMDb 不公开的相关性分数排序结果。它不是投票数，也不是 `popularity` 字段——在这个案例中，1954 年的条目在两个指标上都领先（1373 vs 703 评分，4.25 vs 3.60 流行度）但仍然排在第二位。这就是为什么最高结果可能与规范版本不同，以及为什么通知会比较投票数：它们是您唯一可以读取的排名输入。

未评分的相同标题的罕见情况不会触发它，所以 `ratings "Inception"` 仍然保持静默。

**一个从不读取 stderr 的脚本仍然可以发现。** 相同的事件在 JSON 响应的 `meta.ambiguous` 下记录，因此定时任务或以 `2>/dev/null` 运行的管道（在没有人观看且年份错误最危险的情况下）可以检测到：

```bash
movie-goat-pp-cli ratings "Sabrina" --agent 2>/dev/null | jq '.meta.ambiguous'
```

```json
[
  {
    "query": "Sabrina",
    "kind": "titles",
    "match_count": 3,
    "signal": "alternative_better_rated",
    "chosen":  { "tmdb_id": 11860, "title": "Sabrina", "year": "1995", "vote_count": 703 },
    "alternatives": [
      { "tmdb_id": 6620,   "title": "Sabrina", "year": "1954", "vote_count": 1373 },
      { "tmdb_id": 503902, "title": "Sabrina", "year": "2018", "vote_count": 194 }
    ],
    "hint": "Disambiguate with --year <YYYY>, a \"title (YYYY)\" suffix, or the TMDb id."
  }
]
```

`signal` 是 `alternative_better_rated`，当 TMDb 搜索排名第一的条目*不是*最佳评分的条目时——将其视为“停止并固定一个 ID”——或者 `multiple_exact_matches`，当最高选择也是最佳评分的。`meta.ambiguous` 是一个列表，因为一个命令可以解析多个标题（`versus` 解析两个）。

```
movie-goat-pp-cli 反馈 "the --since flag is inclusive but docs say exclusive"
movie-goat-pp-cli 反馈 --stdin < notes.txt
movie-goat-pp-cli 反馈 列表 --json --limit 10
```

条目存储在本地 `~/.movie-goat-pp-cli/feedback.jsonl` 中。除非设置了 `MOVIE_GOAT_FEEDBACK_ENDPOINT` 并且传递了 `--send` 或者 `MOVIE_GOAT_FEEDBACK_AUTO_SEND=true`，否则它们永远不会被 POST。默认行为是仅本地存储。

写下让你感到惊讶的内容，而不是一个错误报告。简短、具体、一行：这就是复合的部分。

## 输出交付

每个命令都接受 `--deliver <sink>`。输出会发送到命名的 sink 中，而不是（或替代）stdout，以便代理可以无需手动管道地路由命令结果。支持三种 sink：

| Sink | 效果 |
|------|------|
| `stdout` | 默认；仅写入 stdout |
| `file:<路径>` | 原子写入输出到 `<路径>`（临时 + 重命名） |
| `webhook:<url>` | 将输出正文 POST 到 URL (`application/json` 或 `application/x-ndjson` 当 `--compact` 时) |

不支持的方案会被拒绝，并返回一个结构化的错误，其中包含支持的方案集。Webhook 失败会返回非零值，并在 stderr 上记录 URL + HTTP 状态。

## 命名配置文件

配置文件是一组保存的标志值，跨调用重用。当计划代理每次运行都使用相同的配置调用相同的命令时使用它 - HeyGen 的 "Beacon" 模式。

```
movie-goat-pp-cli 配置文件 保存 简报 --json
movie-goat-pp-cli --配置文件 简报 电影 获取 mock-value
movie-goat-pp-cli 配置文件 列表 --json
movie-goat-pp-cli 配置文件 显示 简报
movie-goat-pp-cli 配置文件 删除 简报 --yes
```

显式标志总是优先于配置文件值；配置文件值优先于默认值。`agent-context` 列出所有可用的配置文件在 `available_profiles` 下，以便代理在运行时发现它们。

## 退出代码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 2 | 使用错误（错误的参数） |
| 3 | 资源未找到 |
| 4 | 需要认证 |
| 5 | API 错误（上游问题） |
| 7 | 被限速（等待并重试） |
| 10 | 配置错误 |

## 参数解析

解析 `$ARGUMENTS`：

1. **空、`help` 或 `--help**` → 显示 `movie-goat-pp-cli --help` 输出
2. **以 `install` 开头** → 以 `mcp` 结尾 → MCP 安装；否则 → 参见上述前提条件
3. **其他任何内容** → 直接使用（作为 CLI 命令使用 `--agent`）

## MCP 服务器安装

1. 安装 MCP 服务器：
   ```bash
   go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/movie-goat/cmd/movie-goat-pp-mcp@latest
   ```
2. 在 Claude Code 中注册：
   ```bash
   claude mcp add -e TMDB_API_KEY=<your-tmdb-key> -e OMDB_API_KEY=<your-omdb-key> movie-goat-pp-mcp -- movie-goat-pp-mcp
   ```
   `OMDB_API_KEY` 是可选的，但它启用了 `ratings`、`versus` 和 `career` 中的 IMDb、烂番茄和 Metacritic 增强功能。
3. 验证：`claude mcp list`

## 直接使用

1. 检查是否安装：`which movie-goat-pp-cli`
   如果未找到，提供安装（参见此技能顶部的先决条件）。
2. 将用户查询匹配到上述唯一功能和命令参考中的最佳命令。
3. 使用 `--agent` 标志执行：
   ```bash
   movie-goat-pp-cli <命令> [子命令] [参数] --agent
   ```
4. 如果不明确，钻入子命令帮助：`movie-goat-pp-cli <命令> --help`。
