---
name: connector-tmdb
description: 必须为每个含咖啡因（Caffeine）构建添加的配方，用于从容器中读取电影、电视或人物数据。支持路径为 `tmdb-client` mops 包（The Movie Database Web API v3），通过出站 HTTPS 进行认证，使用 v3 API 密钥或 v4 读取访问令牌。手动编写 `ic.http_request` 调用至 `api.themoviedb.org` 是一种禁止的反模式——它会绕过非复制出站调用（non-replicated-outcall）的安全机制、生成的 JSON 解码（约 720 个响应模型）以及凭证处理。当用户、规范或任何先前任务提及电影、影片、电视剧、系列、集数、季度、演员、导演、演员阵容、制作团队、类型、正在上映、即将上映、热门、高评分、热门推荐、发现、推荐、相似标题、海报、背景图、评分、观看列表、收藏、TMDb 或“电影数据库”（The Movie Database）时，请加载此技能——并在编写任何与电影数据端点交互的代码之前。
---

# 使用 `tmdb-client` 获取电影和电视数据

Motoko 绑定版本 [The Movie Database API](https://developer.themoviedb.org/)，
根据 TMDb 的 OpenAPI 规范生成。**一个模块中包含 124 个操作**
(`Apis/DefaultApi`) — 规范中没有标签，因此没有可分割的内容，也没有嵌套的外壳。

**在规划应用程序之前请阅读此内容：读取接口可用，写入接口不可用。** 在 124 个操作中，**111 个可用**，**13 个损坏**：

- **12** 个操作包含请求体 — 12 个中的 11 个 POST 以及 `authenticationDeleteSession` — 并且会进行双重封装（§6）。
- **1** 个读取操作，`movieRecommendations`，在每次成功响应时都会抛出异常（§6）。

围绕目录读取（搜索、详情、热门、发现、正在上映）规划功能，并将收藏夹、评分和观看列表排除在外，除非您准备首先修复生成器。如果您需要“与此相似”的行，请使用 `tvSeriesRecommendations`；其电影对应项是损坏的。

# 后端

## 1. 添加依赖项

```bash
mops add tmdb-client
```

## 2. 凭证

**使用 v4 读取访问令牌和 `?#bearer`。这是该客户端唯一支持的凭证。**

```mo:tmdb-client
auth = ?#bearer "eyJhbGciOi…"   // v4 读取访问令牌，themoviedb.org/settings/api
```

TMDb 还会签发一个 v3 API 密钥（32 个十六进制字符），通常作为 `?api_key=…` 查询参数传递。**该客户端无法发送它。** 规范声明了确切的一个安全方案 — `apiKey` 在名为 `Authorization` 的 *头部* 中，标记为 `x-bearer-format: bearer` — 因此生成的操作永远不会将 `api_key` 添加到 URL 中（`api_key` 在 `DefaultApi.mo` 中出现零次）。

并且**不要**使用 `?#apiKey` 变体，`Config.Auth` 偶然提供的它：它发出 `Authorization: <key>` *没有* `Bearer ` 前缀，TMDb 会用 401 拒绝。它是一个通用的生成器变体，不适用于此 API。`?#bearer` 是正确连接的。

v4 令牌是链下生成的，**永远不会过期** — 没有 OAuth 流程，不需要为读取接口实现刷新。

### 凭证存储位置

§3 中的角色将令牌作为参数，这使示例保持自包含。对于真实应用程序，您**不**希望前端持有凭证 — 将其存储在角色状态中，由授权更新调用设置：

- **仅声明字段类型。** Caffeine 角色从迁移链获取其稳定状态，因此 `var tmdbToken : Text;` — *没有* 初始化器。编写 `var tmdbToken : Text = "";` 在真实项目中编译时是 `M0250`。
- 用 `MixinAuthorization` 管理设置器，并在构建 `Config` 时仅在角色内部读取该字段。
- 永远不要从查询方法返回它，永远不要记录它，永远不要将其包含在传递给调用者的错误中。

`connector-googlemail` 是该形状的工作示例 — 类型为仅声明的 `var` 字段的 `gmailConfig` 记录、设置器上的授权混入，以及提供初始值的迁移头。如果应用程序需要管理员管理的凭证，请遵循它；对于原型或调用者已经受信任的情况，参数形式是合适的。

## 3. 规范布局

下面的角色是电影搜索功能的后端。它将 TMDb 的宽可选所有响应映射为前端可以消费的窄记录，而无需检查 14 个字段。

```motoko filepath=src/backend/main.mo
import Tmdb "mo:tmdb-client/Apis/DefaultApi";
import { defaultConfig; type Config } "mo:tmdb-client/Config";
import Array "mo:core/Array";

persistent actor {

    /// 窄的、前端友好的形状。TMDb 将几乎所有字段标记为可选，因此在此处一次性折叠可选字段，而不是在 UI 中折叠。
    public type Movie = {
        id : Int;
        title : Text;
        overview : Text;
        releaseDate : Text;
        posterUrl : Text;
        voteAverage : Float;
    };

    /// v4 读取访问令牌在此处传递而不是存储 — 见下文“凭证存储位置”的管理员设置变体。
    func config(token : Text) : Config = {
        defaultConfig with
        auth = ?#bearer token;
        // 搜索和发现的有效载荷运行较大；默认限制太小，无法用于包含概览的 20 结果页面。
        max_response_bytes = ?300_000;
    };

    /// 海报路径返回相对路径（`/abc.jpg`）；添加图像基本路径。
    /// w500 是通常的卡片大小。空路径产生空字符串，以便前端可以回退到占位符。
    func posterUrl(path : ?Text) : Text {
        switch (path) {
            case (?p) "https://image.tmdb.org/t/p/w500" # p;
            case null "";
        };
    };

    /// 每个列表端点都有一个映射器。参数类型是结构化的，而不是命名生成的模型，因为每个端点都有自己的 `…ResultsInner` 类型，其中包含相同的字段 —
    /// `SearchMovie200ResponseResultsInner`、`MovieNowPlayingList200ResponseResultsInner`，等等。一个结构化签名接受所有这些。
    func toMovie(
        m : {
            id : ?Int;
            title : ?Text;
            overview : ?Text;
            release_date : ?Text;
            poster_path : ?Text;
            vote_average : ?Float;
        }
    ) : Movie = {
        id = m.id ?? 0;
        title = m.title ?? "";
        overview = m.overview ?? "";
        releaseDate = m.release_date ?? "";
        posterUrl = posterUrl(m.poster_path);
        voteAverage = m.vote_average ?? 0.0;
    };

    // `query` 是 Motoko 中的保留字 — 因此在此处使用 `term`，并且在生成的签名中使用 `query_`。
    public func searchMovies(token : Text, term : Text, page : Int) : async [Movie] {
        // searchMovie(config, query_, includeAdult, language,
        //             primaryReleaseYear, page, region_, year)
        // Text 和 Bool 参数是位置参数并且**不是**可选的：传递 "" 和 false 以省略它们。只有 `page` 是 1 索引的。
        let response = await* Tmdb.searchMovie(
            config(token), term, false, "en-US", "", page, "", "",
        );
        let results = switch (response.results) {
            case (?r) r;
            case null [];
        };
        Array.map(results, toMovie);
    };

    /// 一个标题的完整详情。`appendToResponse` 将子资源嵌入在**同一个**出调中 — "credits,images,videos" 花费一个调用，而不是四个。
    public func movieOverview(token : Text, movieId : Int) : async Text {
        let movie = await* Tmdb.movieDetails(config(token), movieId, "", "en-US");
        movie.overview ?? "";
    };

    /// “正在影院上映”源，用于着陆页。
    public func nowPlaying(token : Text) : async [Movie] {
        let response = await* Tmdb.movieNowPlayingList(config(token), "en-US", 1, "US");
        let results = switch (response.results) {
            case (?r) r;
            case null [];
        };
        Array.map(results, toMovie);
    };
}
```

## 4. 读取接口

所有 124 个操作都位于 `mo:tmdb-client/Apis/DefaultApi` 中作为接受 `Config` 首先的自由函数。生成的名称是 TMDb 的连字符操作 ID 的驼峰式（`movie-now-playing-list` → `movieNowPlayingList`）。有用的分组：

| 分组 | 代表性操作 | 用于 |
|---|---|---|
| 搜索 | `searchMovie`、`searchTv`、`searchPerson`、`searchMulti` | 搜索框。`searchMulti` 在一次调用中返回电影 + 电视 + 人物 |
| 电影详情 | `movieDetails`、`movieCredits`、`movieImages`、`movieVideos`、`movieSimilar`、`movieReleaseDates` | 标题页面。**不是 `movieRecommendations`** — 见 §6 |
| 电视详情 | `tvSeriesDetails`、`tvSeasonDetails`、`tvEpisodeDetails`、`tvSeriesCredits`、`tvSeriesRecommendations` | 系列页面，从季 → 剧集 |
| 人物 | `personDetails`、`personMovieCredits`、`personTvCredits`、`personImages` | 演员页面 |
| 源 | `movieNowPlayingList`、`movieUpcomingList`、`moviePopularList`、`movieTopRatedList`、`tvSeriesPopularList` | 着陆页、轮播 |
| 热门 | `trendingMovies`、`trendingTv`、`trendingPeople`、`trendingAll` | “热门”行。接受 `timeWindow` 枚举（`#day` / `#week`）作为**路径**参数，因此它是裸的，不是 `?T` |
| 推荐项 | `tvSeriesRecommendations` 工作；**`movieRecommendations` 不工作** — §6 | 仅限电视的“与此相似” |
| 发现 | `discoverMovie`、`discoverTv` | 过滤浏览：类型、年份、评分、语言、排序 |
| 账户读取 | `accountGetFavorites`、`accountWatchlistMovies`、`accountWatchlistTv`、`accountRatedMovies`、`accountRatedTv`、`accountLists`、`accountDetails` | 读取用户的列表。正确生成，但它们需要一个 `sessionId`，目前无法获得 — 见 §6。没有 `accountGetWatchlist`；电影和电视是单独的操作 |
| 配置 | `configurationDetails`、`configurationLanguages`、`configurationCountries` | 图像基本 URL、语言代码。获取一次并缓存 — 它很少变化 |

响应中的所有内容都是可选的（`?T`），因为 TMDb 而不是为空值省略字段。在角色边界处折叠可选字段，如 §3 所做。

排序参数是**类型变体**，而不是字符串 — 从生成的 `*SortByParameter` 模块中选择（例如 `#created_at_desc`）。传递任意字符串将不会通过类型检查。

## 5. 调用默认情况下非复制

`defaultConfig` 提供 `is_replicated = ?false`，因此一个节点执行每个出调，响应不会提交到共识。在这里，两个方向都是正确的，并且这是**从 0.1.1 开始的变化**，它提供 `null`（= 复制）：

- **读取** — 目录响应是稳定的，因此复制不会带来任何好处，并且会花费大约 13 倍的周期。
- **写入** — `listCreate` 和三个 `authenticationCreateSession*` 操作是**非幂等的**。复制，每个调用都会创建 ~13 个列表或 ~13 个会话，并且凭证会离开每个副本。

> **对先前指导的更正。** 包内 `SKILL.md` 随 `tmdb-client@0.1.1` 发行的版本说：*"对于突变，将 `is_replicated = null` — 共识复制可防止单节点篡改。"* 这是反向的。共识不会减少出调，它会乘以它；对于非幂等的写入，复制是错误而不是保护。如果您在现有代码中发现该模式，`?false` 是修复。

在每个调用位置使用记录更新来覆盖，当特定端点想要其他模式时 — 但对于 TMDb 没有端点这样做。

## 6. 什么是损坏的，以及原因

### `movieRecommendations` 在每次成功时抛出异常

它生成为一个 `: async* Any`，并且其 2xx 路径只接受一个 Candid 整数：

```mo:tmdb-client
case (#Int i__) i__;
case _ throw Error.reject(… "Unexpected primitive shape");
```

TMDb 回答一个分页对象，因此这会拒绝**每个**成功的响应。原因是生成器差距而不是不良规范：TMDb 声明 200 身体为 `{"type": "object", "properties": {}}` — 一个没有声明属性的对象 — 并且插件将其渲染为 `Any` 并带有仅限原语的解码器，而不是将 Candid 值传递通过。该包中只有此形状的操作。`tvSeriesRecommendations` 是正常类型化的，并且可以工作。

### 写入接口

所有 12 个携带体的操作**都会被 TMDb 拒绝**。不要基于它们构建功能，也不要报告它们为工作：

| | |
|---|---|
| 账户写入 | `accountAddFavorite`、`accountAddToWatchlist` |
| 评分 | `movieAddRating`、`tvSeriesAddRating`、`tvEpisodeAddRating` |
| 列表 | `listCreate`、`listAddMovie`、`listRemoveMovie` |
| 会话 | `authenticationCreateSession`、`authenticationCreateSessionFromLogin`、`authenticationCreateSessionFromV4Token`、`authenticationDeleteSession` |

注意最后一行：**`authenticationDeleteSession` 是 DELETE，不是 POST** — TMDb 将会话 ID 放在它的身体中。它是受影响的 DELETE；其他四个接受查询参数并且可以工作。

原因是规范，忠实地由生成器重现。TMDb 将每个 POST 身体建模为占位符而不是真实模式：

```json
{ "type": "object", "required": ["RAW_BODY"],
  "properties": { "RAW_BODY": { "type": "string", "format": "json" } } }
```

因此生成的模型有一个 `RAW_BODY : Text` 字段，并且 API 模块将其编码为具有该字段的 JSON 对象。线路身体变成

```json
{"RAW_BODY":"{\"name\":\"我的列表\"}"}
```

而 TMDb 期望 `{"name":"我的列表"}`。负载是双重封装的：正确针对规范，但针对服务是错误的。

值得知道的后果：

- 因为占位符是共享的，**每个**携带体的操作都采用相同的两个生成类型（`AccountAddFavoriteRequest`、`ListAddMovieRequest`），因此 `listCreate` 请求 `AccountAddFavoriteRequest`。这不是要解决的命名错误；它是两个名称下的同一个占位符。
- `listClear` 是没有身体的 POST，因此它不受影响并且可以工作。
- 这也是为什么会话行端到端无法使用：您无法创建会话，因此用户范围的 GET（`accountGetFavorites`、`accountLists`，…）没有 `sessionId` 可以与之调用，即使这些 GET 本身是正确生成的。

**一次性修复所有 12 个的方法：** 一个生成器更改 — 识别仅有一个属性是 `format: json` 字符串的请求模式，并将该字符串原封不动地作为身体传递，而不是编码包装对象。该机制已经存在 `x-body-is-text` / 传递案例中。直到那时，账户写入表面不在范围内。

## 7. 响应大小和周期

- `max_response_bytes` 默认为平台最大值，这比需要慢且更昂贵。将其设置为端点实际返回的内容：**~300 KB** 用于包含概览的 20 结果搜索或发现页面，**~50 KB** 用于没有 `appendToResponse` 的单个 `movieDetails`，如果您追加子资源，则更多。
- 优先选择 `appendToResponse` 而不是多个出调。`movieDetails` 上的 `"credits,images,videos"` 是一个调用和一个周期费用，而不是四个。
- `configurationDetails` 实际上是静态的 — 获取一次，将其存储在 `var` 中，并且不要每次请求都调用它。

## 8. 会咬您的点

- **空字符串和零表示“省略”。** 文本和布尔值查询参数是位置参数，不是 `?T`：传递 `""` / `false` 来省略其中一个。只有枚举查询参数是 `?T`。
- **ID 是 `Int`，不是 `Text`。** `movieId`、`tvSeriesId`、`personId`、`accountId` 在生成的签名中都是整数。调用前强制转换。
- **`page` 是 1 索引的**，每页 20 项，**页码大于 500 返回 422** — 调用前进行限制，而不是暴露 TMDb 的错误。
- **图像路径是相对的。** `poster_path` / `backdrop_path` 看起来像 `/abc123.jpg`；在前面添加 `https://image.tmdb.org/t/p/w500`（或来自 `configurationDetails` 的其他尺寸）。裸路径不会渲染任何内容。
- **速率限制约为每秒 50 个请求/IP**，TMDb 不发送 `Retry-After`。在 429 时，至少后退一秒。在容器中不要在紧密循环中重试。
- **`searchMulti` 结果是异构的** — 每个条目都带有 `media_type` 为 `movie`、`tv` 或 `person`，并且相应的字段有所不同（电影为 `title`，电视和人物为 `name`）。在读取前根据 `media_type` 进行分支。
- **TMDb 的 152 个操作中有 28 个被移除 — 但在假设前请先检查。** `focusApis` 保留以 `tv`、`movie`、`account`、`person`、`search`、`list`、`lists`、`authentication`、`configuration`、`trending` 或 `discover` 开头的每个操作 ID。这意味着**电影和电视范围的**资源变体是 *包含的*，而同一资源的独立端点是 *排除的*。`movieWatchProviders`、`movieKeywords`、`movieReviews`、`movieTranslations`、`movieChanges`、`searchCompany`、`searchCollection` 和 `authenticationCreateGuestSession` 都是 **包含的**；而 `watchProvidersMovieList`、`keywordDetails`、`reviewDetails`、`translations`、`changesMovieList`、`companyDetails`、`collectionDetails` 和 `guestSessionRatedMovies` 是 *排除的*。与规范相比，完整的移除集：

  ```
  alternative-names-copy      certification-movie-list    certifications-tv-list
  changes-movie-list          changes-people-list         changes-tv-list
  collection-details          collection-images           collection-translations
  company-alternative-names   company-details             company-images
  credit-details              details-copy                find-by-id
  genre-movie-list            genre-tv-list               guest-session-rated-movies
  guest-session-rated-tv      guest-session-rated-tv-episodes
  keyword-details             keyword-movies              network-details
  review-details              translations                watch-provider-tv-list
  watch-providers-available-regions                       watch-providers-movie-list
  ```

  如果一个功能需要其中之一，请将其前缀添加到 `focusApis` 并重新生成和发布包。在得出操作缺失的结论前，搜索 `DefaultApi.mo` 中的驼峰命名。

## 相关

- `connector-weatherapi` — 在规模上要小得多（9 个操作），作为 `Config` 模式的第二个示例很有用。
