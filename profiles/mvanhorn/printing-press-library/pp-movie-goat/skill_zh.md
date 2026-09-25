<!-- GENERATED FILE — DO NOT EDIT.
     This file is a verbatim mirror of library/media-and-entertainment/movie-goat/SKILL.md,
     regenerated post-merge by tools/generate-skills/. Hand-edits here are
     silently overwritten on the next regen. Edit the library/ source instead.
     See the repository agent guide, section "Generated artifacts: registry.json, cli-skills/". -->

# Movie Goat — 印刷机 CLI

## 前置条件：安装 CLI

此技能驱动 `movie-goat-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它缺失，请先安装它：

1. 通过印刷机安装程序安装。它默认将二进制文件设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install movie-goat --cli-only
   ```
2. 验证：`movie-goat-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），则回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）：

```bash
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/movie-goat/cmd/movie-goat-pp-cli@latest
```

如果安装后 `--version` 报告“命令未找到”，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，不要继续使用技能命令。

## 何时使用此 CLI

当代理需要回答需要结合流媒体可用性和多源评分的影迷问题时，使用 Movie Goat。它是今晚选择、系列马拉松规划和评分职业生涯时间线的正确选择。它不是票房追踪、评论情感分析或任何需要 LLM 风格的剧情或评论摘要的工作流的正确选择。

## 何时不使用此 CLI

不要为需要创建、更新、删除、发布、评论、投票、邀请、订购、发送消息、预订或更改远程状态的要求激活此 CLI。此印刷 CLI 仅暴露用于检查、导出、同步和分析的只读命令。

## 独特功能

这些功能在任何其他为此 API 的工具中都不提供。

### 影迷仪式
- **`tonight`** — 从您流媒体服务上实际播放的热门标题中挑选今晚要观看的内容。

  _当代理需要一个流媒体过滤的短列表时使用；一个调用可以替代在 TMDb/RT/JustWatch 之间切换标签页。_

  ```bash
  movie-goat-pp-cli tonight --mood thriller --max-runtime 120 --providers netflix,max --region US --json
  ```
- **`ratings`** — 任何标题的 TMDb + IMDb + 罗伯特·汤姆森 + Metacritic 评分，以一张卡片显示。

  _当代理需要一个标题的规范多源评分时使用；如果 OMDB_API_KEY 未设置，则会优雅地降级为仅 TMDb。_

  ```bash
  movie-goat-pp-cli ratings 550 --json
  ```
- **具有重制片意识的标题解析** — 接受标题而不是 TMDb ID 的每个命令，在标题共享时都会大声说明。

  _TMDb 的搜索按专有的相关性分数排名，因此 `"Sabrina"` 解析为 1995 年的重制版，尽管 1954 年的 Wilder 原版评分更高。当一个标题有多个高评分匹配时，CLI 在 **两个** 渠道上报告：人类在 stderr 上的通知，以及 stdout 上的 `meta.ambiguous` 记录，供从未读取 stderr 的消费者使用。用 `--year`、`"Title (YYYY)"` 后缀或 ID 来固定您想要的那个。_

  ```bash
  movie-goat-pp-cli ratings "Sabrina" --year 1954 --json
  ```
- **`marathon`** — 计划一个系列马拉松，包括观看顺序、总运行时间和建议的休息时间。

  _当计划活动观看时使用；代理可以将日程表导出并与一组人分享。_

  ```bash
  movie-goat-pp-cli marathon "The Avengers" --order release --breaks-every 240 --json
  ```
- **`career`** — 探索任何演员或导演的完整片单，包括评分和年代顺序。

  _当代理需要一个带评分的年代顺序片单时使用；用跨源评分取代扁平的 IMDb 列表。_

  ```bash
  movie-goat-pp-cli career "Christopher Nolan" --since 2010 --role director --json
  ```
- **`versus`** — 在评分、演员阵容、运行时间和流媒体方面，并排比较两部电影或节目。

  _当代理必须在两个最终候选人之间选择时使用；一个命令显示他们在每个维度上的差异。_

  ```bash
  movie-goat-pp-cli versus 550 27205 --region US --json
  ```
- **`collaborators`** — 列出在一个人的作品中出现两次或更多次的人，包括计数和标题。

  _当代理在研究电影人的圈子时使用；机械地展示反复出现的副导演/作曲家/演员。_

  ```bash
  movie-goat-pp-cli collaborators "Christopher Nolan" --min-count 3 --role crew --json
  ```

### 复合的本地状态
- **`watchlist list`** — 本地 SQLite 观看列表；标记可在您的服务上流媒体播放的行。

  _每周使用以从保存的列表中提取可流媒体播放的项目；消除了针对每个标题的临时 JustWatch 检查。_

  ```bash
  movie-goat-pp-cli watchlist list --available --providers netflix,max --region US --json
  ```
- **`queue`** — 基于您的观看列表的建议和相似性，建议下一个观看选择。

  _当代理需要一个基于保存兴趣的新队列时使用；结合本地状态和 API 推荐。_

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

- `movie-goat-pp-cli discover movies` — 按类型、年份、评分、认证、演员阵容、制作人员、流媒体提供程序等发现电影
- `movie-goat-pp-cli discover tv` — 按类型、年份、评分、网络和流媒体提供程序发现电视节目

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

**multi** — 跨电影、电视节目和人进行多搜索

- `movie-goat-pp-cli multi <query>` — 在单个查询中搜索电影、电视节目和人

**people** — 搜索和浏览人物（演员、导演、制作人员）

- `movie-goat-pp-cli people get` — 获取有关人物的详细信息，包括他们的片单
- `movie-goat-pp-cli people popular` — 获取热门人物
- `movie-goat-pp-cli people search` — 按名称搜索人物

**trending** — 获取热门电影、电视节目和人

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
movie-goat-pp-cli which "<您自己的话描述的功能>"
```

`which` 将自然语言的功能查询解析为此 CLI 的精选功能索引中的最佳匹配命令。退出代码 `0` 表示至少有一个匹配；退出代码 `2` 表示没有自信的匹配——回退到 `--help` 或使用更窄的查询。

## 烹饪方法


### 今晚，高评分，在我的服务上

```bash
movie-goat-pp-cli tonight --mood drama --max-runtime 130 --providers netflix,max,prime --region US --agent --select "results.title,results.year,results.rating,results.providers"
```

仅包含代理需要决定的高引力字段的流媒体过滤短列表。

### 观看列表扫描

```bash
movie-goat-pp-cli watchlist list --available --providers netflix,max --region US --agent
```

每周检查：哪些保存的标题在我的服务上变成了可流媒体播放。

### 评分职业生涯深入分析

```bash
movie-goat-pp-cli career "Lynne Ramsay" --role director --agent --select "credits.title,credits.year,credits.rating_imdb,credits.rating_rt"
```

受代理限制的年代顺序片单，包括重要的跨源评分列。

### 在两个最终候选人之间选择

```bash
movie-goat-pp-cli versus 27205 87108 --region US --agent
```

对 Inception 和 Tenet 的对齐比较卡片；评分、运行时间、演员阵容重叠、提供程序。

### 在 shell 环境中存储两个 API 密钥而不进行修改

```bash
movie-goat-pp-cli auth set-token YOUR_TMDB_API_KEY
movie-goat-pp-cli auth set-omdb-token YOUR_OMDB_API_KEY
movie-goat-pp-cli auth status --agent
```

将两个凭据写入 `~/.config/movie-goat-pp-cli/config.toml`（模式 `0600`），以便机器上的每个代理和 shell 都可以看到它们，而不仅仅是导出了环境变量的那个。`auth status` 报告 `authenticated`、`omdb_configured` 和 `omdb_source`，以便代理在运行 `ratings` 之前可以告诉 IMDb / RT / Metacritic 列表是否会填充。

### 固定原始版本，而不是重制版

```bash
movie-goat-pp-cli ratings "Sabrina" --year 1954 --agent
movie-goat-pp-cli ratings "Sabrina (1954)" --agent
movie-goat-pp-cli versus "Sabrina (1954)" "Sabrina (1995)" --agent
```

`ratings`、`marathon` 和 `watchlist add` 都接受 `--year`；每个接受标题的命令（包括两个位置参数的 `versus`）都接受内联 `"Title (YYYY)"`
后缀。如果没有这些，CLI 仍然会采用 TMDb 的最高排名结果，但会在 stderr 上打印竞争对手的 ID：

```
warn: "Sabrina" 在 TMDb 上匹配 3 个标题；使用 id 11860 — Sabrina (1995).
      TMDb 的搜索相关性将其排在第一位，但 Sabrina (1954) 的评分更高 (1373 vs 703)。
      其他匹配项：
        6620  Sabrina (1954)
        503902  Sabrina (2018)
      使用 --year <YYYY>、一个 "title (YYYY)" 后缀或 TMDb id 来消除歧义。
```

`/search/*` 按照一个 TMDb 不公开的相关性分数排序结果。它不是投票数，也不是 `popularity` 字段——在这个案例中，1954 年的条目在两个指标上都领先 (1373 vs 703 评分，4.25 vs 3.60 人气)，但仍然排在第二位。这就是为什么最高结果可能与规范版本不同，以及为什么通知会比较投票数：它们是您唯一可以读取的排名输入。

未评分的相同标题的冷门作品不会触发它，所以 `ratings "Inception"` 仍然保持静默。

**一个从不读取 stderr 的脚本仍然会发现。** 相同的事件记录在 JSON 响应的 `meta.ambiguous` 下，因此定时任务或以 `2>/dev/null` 运行的管道（在没有人关注且年份错误最危险的情况下）可以检测到：

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

`signal` 是 `alternative_better_rated`，当 TMDb 的搜索排名第一的条目 *不是* 最好的评分时——将其视为“停止并固定一个 ID” ——或者 `multiple_exact_matches`，当最高选择也是最好的评分时。`meta.ambiguous` 是一个列表，因为一个命令可以解析多个标题（`versus` 解析两个）。
