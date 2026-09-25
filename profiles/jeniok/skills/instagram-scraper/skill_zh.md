# Instagram Scraper

通过 Apify 的 [Instagram Scraper](https://apify.com/apify/instagram-scraper) 获取 Instagram 公开数据。无需 Instagram 登录，无需 Cookies，无需 Meta 应用审核。

| | |
|---|---|
| Actor | `apify/instagram-scraper` |
| Auth | `Authorization: Bearer $APIFY_TOKEN`，或已登录的 Apify CLI — 请参阅 Setup |
| Price | 从 **$2.30 每千条结果**，由 Apify 收费 |
| Free tier | $5/月信用额度 ≈ **2,000+ 条结果**，无需信用卡 |

---

## Setup — 在进行任何数据调用之前执行此操作

**始终先运行此预检。** 在它通过之前，不要尝试进行数据调用。

```bash
if [ -n "$APIFY_TOKEN" ]; then
  echo "AUTH_OK curl"
elif command -v apify >/dev/null 2>&1 && apify info >/dev/null 2>&1; then
  echo "AUTH_OK cli: apify"
elif { [ -f "$HOME/.apify/auth.json" ] || [ -f "$USERPROFILE/.apify/auth.json" ]; } \
     && npx --yes apify-cli@latest info >/dev/null 2>&1; then
  echo "AUTH_OK cli: npx --yes apify-cli@latest"
else
  echo "AUTH_MISSING"
fi
```

检查按成本从低到高排序。`npx` 回退大约需要四秒钟，因此仅在 Apify 配置目录显示先前登录时运行（新用户会立即达到 `AUTH_MISSING`，而不是等待可能永远不会找到会话的包下载）。

**`$HOME` 和 `$USERPROFILE` 都有意进行检查。** 在 Windows 上，它们可以指向不同的位置——沙盒和一些 CI 图像重新映射 `$HOME`，而 Apify CLI 仍然将写入 `$USERPROFILE\.apify`。仅测试 `$HOME` 会报告 `AUTH_MISSING`，对于已登录的用户来说完全正常，而技能会让他们注册他们已经拥有的帐户。如果在您认为已通过认证的机器上看到 `AUTH_MISSING`，请检查这两个路径，然后再信任它。

**两个 `AUTH_OK` 模式不能互换——预检会告诉您使用哪种调用形式。**

- `AUTH_OK curl` — 环境中存在 token。此技能中的 HTTP 调用按预期工作。
- `AUTH_OK cli: <prefix>` — Apify CLI 持有会话，**token 不可从磁盘读取**。`~/.apify/auth.json` 仅携带帐户元数据（用户名、计划、代理组——没有 `token` 字段）；当前 CLI 版本将 token 保存在操作系统密钥库后端。不要尝试从该文件中提取一个：一个虚假的 `Authorization: Bearer` 头会返回 `401`，看起来就像一个被吊销的 token。使用 `apify call`，并在预检打印 `cli:` 后添加 whatever 前缀（`apify`，或当 CLI 不在 `PATH` 上时 `npx --yes apify-cli@latest`）。

### 如果预检打印 `AUTH_OK cli`

此技能中的每个有效负载仍然适用——将其写入文件并将其交给 `apify call` 而不是 `curl`：

```bash
cat > /tmp/ig-input.json <<'EOF'
{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"details","resultsLimit":1}
EOF

apify call apify/instagram-scraper --input-file /tmp/ig-input.json --output-dataset --silent
```

- **始终明确传递 Actor id。** 没有 id，`apify call` 会运行 Actor repo 中定义的本地 `.actor/actor.json`——它会在沙盒中静默运行错误的东西。
- **优先使用 `--input-file` 而不是内联 `-i '{...}'`。** 内联 JSON 必须在 shell 中生存，PowerShell 和 `cmd.exe` 会破坏引号。文件永远不会这样。`--input-file -` 从 stdin 读取。
- **`--output-dataset` 将数据集打印到 stdout**——与 `run-sync-get-dataset-items` 返回的相同数组，因此输出部分中的每个字段都相同。`--silent` 使运行日志不显示在 stdout，以便输出解析为 JSON。
- `apify call` 等待运行完成，因此 `curl` 路径下不需要异步轮询模式。添加 `--timeout <seconds>` 来限制长时间作业。
- 运行由 CLI 登录的帐户计费。`apify info` 会打印它——如果用户可能拥有多个帐户，则值得向用户显示。

### 如果预检打印 `AUTH_MISSING`

在用户浏览器中打开 Apify 注册页面，然后请求 token。按如下方式运行此操作——它根据平台选择正确的命令，并在没有浏览器（CI、SSH、容器）时降级为打印 URL：

```bash
URL="https://console.apify.com/sign-up?fpr=z8j1nz"
# xdg-open 在 open 之前检查：在某些 Linux 发行版上 `open` 是 openvt，不是浏览器。
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
elif command -v open >/dev/null 2>&1; then open "$URL"
elif command -v powershell.exe >/dev/null 2>&1; then powershell.exe -NoProfile -Command "Start-Process '$URL'"
elif command -v cmd.exe >/dev/null 2>&1; then cmd.exe /c start "" "$URL"
else echo "在浏览器中打开此 URL：$URL"
fi
```

然后告诉用户正在发生什么——但**不要等待回复**：

> 我已为您在浏览器中打开 Apify 的注册页面。Instagram 数据通过 Apify，它是免费开始的——每月 5 美元的信用额度，无需信用卡，足够大约 2,000 条结果。
>
> 在那里注册（如果您已经有帐户，请登录）。我现在也打开授权步骤——批准它，这台机器就会保持连接，因此您不必再执行任何这些操作。
>
> _注册链接是一个推荐链接。_

立即运行登录。**不要询问用户是否已注册**——此命令打开 Apify 的授权页面，该页面本身提供注册，然后阻止用户完成。命令就是等待，因此没有需要检测和没有往返行程：

```bash
timeout 300 npx --yes apify-cli@latest login -m console
```

- **`-m console` 是必需的。** 脱胎换骨的 `apify login` 首先提示登录方法，并且将在无法回答的 stdin 上挂起。`-m console` 直接进入浏览器流程。
- **`timeout 300`** 限制它，因此一个被放弃的注册不会挂起会话。退出码 `124` 表示它超时——用户离开了，所以询问他们是否还想继续，而不是静默重试。
- 成功后，它会打印 *"成功：您已登录 Apify 作为 `<username>`。您的 token 存储在您的操作系统密钥库中。"* 从那时起，预检在**每个未来的会话**中都解析为 `AUTH_OK cli`——无需粘贴、存储或泄漏到会话记录中。

**然后重新运行预检。这就是您知道它是否成功的方式——不是消息，也不是假设浏览器步骤已成功：**

| 预检现在说 | 含义 | 做什么 |
|---|---|---|
| `AUTH_OK cli: <prefix>` | 已登录并持久化 | 继续请求 |
| `AUTH_MISSING` | 登录未完成 | 平静地说明并询问是否要重试——**不要循环** |

预检的 CLI 分支只是 `apify info`，当会话存在时它退出 `0`，当它不存在时它退出非零。它就是之前产生 `AUTH_MISSING` 的检查，因此重新运行它是真实的确认，而不是重申您已经相信的事情。

值得命名两种失败模式，因为它们从外部看起来都像成功：用户在未经批准的情况下关闭了授权标签（超时退出 `124`），以及用户注册但从未达到批准步骤。在这两种情况下，注册很可能成功，而**这台机器仍然没有连接**——这正是为什么要信任预检，而不是注册。

**保持注册标签和登录的顺序。** 注册页面是记录推荐的地方；之后的授权步骤只是这台机器连接到现在存在的任何帐户。反着打开它们会丢失归因。

### 不要向用户索要他们的 token

**在对话中不要请求、接受或处理 Apify API token。** 上述浏览器登录存在的目的正是为了让秘密永远不会到达代理：CLI 直接从 Apify 接收它并将其写入操作系统密钥库，而此技能只读取该结果的*结果*（`apify info` 的退出码），而不是值。

如果用户在未经提示的情况下提供 token，**拒绝它并指向下面两个安全路线之一。** 粘贴到会话中的任何内容都是一个实时凭证，位于会话记录、滚动回显和任何捕获对话的日志中。

**无头环境**——CI、SSH、容器、任何 OAuth 往返无法打开浏览器的环境。用户在自己的 shell / CI 秘密存储中设置凭证，*在启动代理之前*：

```bash
# 用户在自己的 shell / CI 秘密存储中运行此命令——不是通过代理
export APIFY_TOKEN="…"
```

预检现在报告 `AUTH_OK curl`，并且一切正常，值从未通过对话传递。

**或者 CLI 自己的提示**，它从 stdin 而不是对话中读取 token：

```bash
npx --yes apify-cli@latest login -m manual
```

避免 `login -t <token>`。将秘密作为命令行参数传递会在机器上的每个其他进程的进程列表中暴露它，并且也会在 shell 历史记录中暴露它。它还会**在验证之前清除存储的会话**，因此一个拼写错误或一个过时的值会导致用户退出一个正在工作的会话。

当 token 真正存在于环境中时，始终将其引用为 `$APIFY_TOKEN` 并让 shell 扩展它——此技能中的每个示例都这样做。永远不要将字面值替换到命令、日志行或消息中。

---

## 获取数据

一个调用，同步的，直接返回项目。适用于任何在 ~60 s 内完成的内容。**这是 `AUTH_OK curl` 形式**——在 `AUTH_OK cli` 下，将相同的 `-d` 有效负载放入文件并通过 `apify call` 运行，如上所示。

```bash
curl -s -X POST \
  "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?timeout=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: instagram-scraper-skill" \
  -d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"details","resultsLimit":1}'
```

`User-Agent` 标头只是为了让从此技能发起的运行能够在日志中区分开来。它不携带任何个人数据，可以删除。

### 选择 `resultsType`

| 值 | 返回 |
|---|---|
| `details` | 个人资料元数据：粉丝、关注、简介、帖子数量、个人资料图片。**最便宜——每个个人资料 1 条结果。** |
| `posts` | 帖子信息流 |
| `reels` | 仅限 Reels |
| `stories` | 当前直播的故事 |
| `comments` | 帖子上的评论 |
| `mentions` | 提及帐户的帖子 |

每当用户只需要个人资料数字时，请选择 `details`。使用 `posts` 来回答这个问题会花费高达 100 倍的成本，而且没有任何好处。

### 输入参考

| 字段 | 类型 | 默认 | 备注 |
|---|---|---|---|
| `directUrls` | 数组 | — | 个人资料、帖子、Reels、标签、位置或音频 URL——见下文的 URL 处理 |
| `resultsType` | 字符串 | `posts` | 见上表 |
| `resultsLimit` | 整数 | `100` | 每个URL。**驱动成本——始终设置它。** |
| `onlyPostsNewerThan` | 字符串 | — | `YYYY-MM-DD`、ISO 或 `1 day` / `2 months`。UTC |
| `search` | 字符串 | — | 关键字，而不是 `directUrls` |
| `searchType` | 字符串 | `hashtag` | `hashtag`、`profile`、`place`、`user` |
| `searchLimit` | 整数 | `10` | 每个搜索发现的最大项目数 |
| `addParentData` | 布尔值 | `false` | 将每个项目标记为产生它的查询 |

**还有四个字段可以工作，但未在发布的输入模式中。** 它们在 Actor 的 README 中有记录，并已验证可用——自由使用它们：

| 字段 | 类型 | 适用 | 备注 |
|---|---|---|---|
| `addProfileStatistics` | 布尔值 | `details` | 添加一个 `statistics` 对象（~60 个字段）——`account_type`（1 个人、2 商业、3 创作者）、`media_count`、`total_clips_count`、`category`、`city_name`、联系字段。也适用于私人个人资料 |
| `skipPinnedPosts` | 布尔值 | `posts` | 排除置顶帖子 |
| `isNewestComments` | 布尔值 | `comments` | 最新评论排序。**仅限付费计划**——免费计划获得默认顺序 |
| `includeNestedComments` | 布尔值 | `comments` | 包括回复。**仅限付费计划。** 每个回复都是一个单独的结果，因此总数超过 `resultsLimit` |

### URL 处理

`directUrls` 比看起来更宽容。所有这些都被接受：

- **个人资料 ID 可以在任何个人资料 URL 出现的地方工作**——一个裸数字 ID 就可以
- `instagram.com/_u/natgeo/profilecard/` — `_u` 和 `profilecard` 被剥离
- `instagram.com/stories/username/` — 简化为用户名
- `instagram.com/share/BAC6cDeb_-` — 解析为规范帖子 URL
- `instagram.com/explore/locations/7538318/` — 仅 ID 有效，无需别名

**不支持：** `posts`、`reels`、`mentions` 或 `details` 中的 URL 形式数字帖子 ID (`instagram.com/p/3369450800358839406/`)。改用短代码形式。这种格式*确实*适用于 `comments`。

**URL 类型驱动输出模式。** 标签、位置、音频和探索 URL 即使与另一个内容模式配对时也会返回它们自己的元数据——因此一个位置 URL 与 `resultsType: "details"` 一起返回位置详情，而不是个人资料详情。

### 会咬人的限制

- **每次运行一个内容类型。** 没有办法在单个调用中获取帖子*和*评论。运行两次。
- **URL 优先于搜索。** `directUrls` 和 `search` 不能组合；如果两者都存在，URL 会获胜，搜索会被忽略。
- **标签作为纯文本输入**——`travel`，而不是 `#travel`。
- **多个搜索词在一个字符串中用逗号分隔**：`"travel, fitness"`。
- **免费计划每个帖子大约有一页评论 (~15)。** 付费计划没有这样的限制。不要报告这是一个错误——说明它是什么。

### 常见任务

Actor 暴露的每个功能，以及每个功能的负载。将 `-d '...'` 替换到上面的 curl 中。

**几个帐户的个人资料统计**——最便宜的调用：

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/","https://www.instagram.com/natgeo/"],"resultsType":"details","resultsLimit":1}'
```

**一个个人资料的最新帖子，过去 30 天：**

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"posts","resultsLimit":30,"onlyPostsNewerThan":"1 month"}'
```

**一个个人资料的 Reels：**

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"reels","resultsLimit":20}'
```

**一个个人资料当前的故事**——仅在故事直播时返回任何内容，并且通常需要付费计划：

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"stories","resultsLimit":20}'
```

**提及帐户的帖子**——品牌监控：

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"mentions","resultsLimit":50}'
```

**一个帖子的评论：**

```bash
-d '{"directUrls":["https://www.instagram.com/p/SHORTCODE/"],"resultsType":"comments","resultsLimit":50}'
```

**标签下的帖子：**

```bash
-d '{"search":"wildlifephotography","searchType":"hashtag","searchLimit":50,"resultsType":"posts","resultsLimit":50}'
```

**通过关键字查找帐户**——`user` 返回帐户记录：

```bash
-d '{"search":"climate photographer","searchType":"user","searchLimit":20,"resultsType":"details"}'
```

**通过名称搜索个人资料**——`profile` 在个人资料页面上匹配：

```bash
-d '{"search":"national geographic","searchType":"profile","searchLimit":20,"resultsType":"details"}'
```

**来自位置的帖子：**

```bash
-d '{"search":"Yosemite National Park","searchType":"place","searchLimit":20,"resultsType":"posts","resultsLimit":50}'
```

**来自特定位置或标签 URL 的帖子**——直接传递 URL 而不是搜索：

```bash
-d '{"directUrls":["https://www.instagram.com/explore/tags/wildlife/"],"resultsType":"posts","resultsLimit":50}'
```

**跟踪哪个查询产生了哪个帖子**——当在一个运行中抓取几个标签或个人资料时，`addParentData` 将每个项目标记为其来源，以便之后可以将结果分组：

```bash
-d '{"search":"wildlife","searchType":"hashtag","searchLimit":30,"resultsType":"posts","resultsLimit":30,"addParentData":true}'
```

**深度个人资料统计**——帐户类型、帖子和 Reels 数量、类别、城市、公共联系字段。也适用于私人个人资料：

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"details","resultsLimit":1,"addProfileStatistics":true}'
```

**最新帖子，排除置顶帖子：**

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"posts","resultsLimit":30,"skipPinnedPosts":true}'
```

**仅置顶帖子**——反转相同的一对：

```bash
-d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"posts","skipPinnedPosts":false,"onlyPostsNewerThan":"0 minutes"}'
```

**最新评论，包括回复**——仅限付费计划：

```bash
-d '{"directUrls":["https://www.instagram.com/p/SHORTCODE/"],"resultsType":"comments","resultsLimit":50,"isNewestComments":true,"includeNestedComments":true}'
```

## 输出

**每种内容类型都产生不同的模式，它们不能在一个运行中组合。** 以下示例已缩减为有用的字段；您传递的 URL 类型可以覆盖形状（位置 URL 返回位置数据，即使处于另一种模式下）。

**帖子 / 轮播** (`resultsType: "posts"`) — 23 个字段：

```json
{
  "inputUrl": "https://www.instagram.com/p/DZxvMgyH8yR/",
  "id": "3923124318436838545",
  "type": "Image",
  "shortCode": "DZxvMgyH8yR",
  "caption": "在刚果民主共和国…",
  "hashtags": [], "mentions": ["carstenpeter"],
  "url": "https://www.instagram.com/p/DZxvMgyH8yR/",
  "likesCount": 34512, "commentsCount": 210,
  "timestamp": "2026-06-22T17:24:20.000Z",
  "displayUrl": "https://…", "images": [], "childPosts": [],
  "dimensionsWidth": 1080, "dimensionsHeight": 1350, "alt": "…",
  "ownerUsername": "natgeo", "ownerFullName": "National Geographic", "ownerId": "787132",
  "firstComment": "…", "latestComments": [], "isCommentsDisabled": false
}
```

**Reel** (`resultsType: "reels"`) — 31 个字段。帖子加上视频：

```json
{
  "…all post fields…": "…",
  "videoUrl": "https://…", "videoDuration": 28.28,
  "videoViewCount": 120433, "videoPlayCount": 98221,
  "audioUrl": "https://…", "musicInfo": {}, "productType": "clips",
  "isPinned": false
}
```

**评论** (`resultsType: "comments"`):

```json
{
  "postUrl": "https://www.instagram.com/p/DZ5T2XPllXv/",
  "commentUrl": "https://www.instagram.com/p/DZ5T2XPllXv/c/18093536360613690",
  "id": "18093536360613690",
  "text": "我们爱你 NASA 💙🌎🌊",
  "ownerUsername": "mavideniz5521__", "ownerProfilePicUrl": "https://…",
  "timestamp": "2026-06-22T17:24:20.000Z",
  "likesCount": 4, "repliesCount": null, "replies": null,
  "owner": { "username": "…" }
}
```

`repliesCount` 和 `replies` 仅在 `includeNestedComments: true`（付费计划）时填充。

**个人资料详情** (`resultsType: "details"`) — 22 个字段。验证为实时：

```json
{
  "inputUrl": "https://www.instagram.com/nasa/",
  "id": "528817151", "username": "nasa", "url": "https://www.instagram.com/nasa/",
  "fullName": "NASA", "biography": "让看似不可能的事情成为可能。 ✨",
  "externalUrl": "https://www.nasa.gov/", "externalUrls": [],
  "followersCount": 104423132, "followsCount": 92, "postsCount": 4888,
  "verified": true, "private": false,
  "isBusinessAccount": true, "businessCategoryName": "政府机构",
  "joinedRecently": false, "fbid": "17841401474538262",
  "profilePicUrl": "https://…", "profilePicUrlHD": "https://…",
  "highlightReelCount": 5, "igtvVideoCount": 171,
  "latestPosts": [], "relatedProfiles": []
}
```

**`details` 已经包含 `latestPosts`（最多 12 条）和 `relatedProfiles`（最多 48 条）而不需要额外成本。** 如果用户想要一个个人资料的数字*和*查看最新帖子，一个 `details` 调用就足够了——通常浪费第二个 `posts` 调用。

使用 `addProfileStatistics: true` 会附加一个 `statistics` 对象（~60 个字段）：`account_type`（1 个人、2 商业、3 创作者）、`media_count`、`total_clips_count`、`category`、`city_name`、`address_street`、`zip`、`bio_links`、`mutual_followers_count`。

**提及** (`resultsType: "mentions"`) — 21 个字段，帖子形状，加上 `taggedUsers`、`music`、`carouselImages`、`carouselImageCount`。

**位置详情**（位置 URL）— 16 个字段：

```json
{
  "inputUrl": "https://www.instagram.com/explore/locations/7538318/",
  "name": "哥本哈根，丹麦", "location_id": "7538318", "slug": "copenhagen",
  "lat": 55.6761, "lng": 12.5683,
  "location_address": "…", "location_city": "…", "location_zip": "…",
  "phone": "…", "category": "…", "price_range": "…",
  "media_count": 1284322, "ig_business": "…", "posts": [], "hours": {}
}
```

**标签详情**（标签 URL）— 15 个字段，包括 SEO 风格的额外内容：
`name`, `postsCount`, `url`, `id`, `posts`, `postsPerDay`, `difficulty`, `related`,
`frequent`, `average`, `rare`, `relatedFrequent`, `relatedAverage`, `relatedRare`.

**搜索结果** 携带 `searchTerm` 和 `searchSource`，以便您知道哪个查询生成了每一行：

- **标签搜索** — 6 个字段：`searchTerm`, `searchSource`, `name`, `postsCount`, `url`, `id`
- **位置搜索** — 17 个字段：位置详情形状加上 `searchTerm` / `searchSource`
- **个人资料搜索** — 13 个字段：帖子形状，带有 `ownerUsername`, `ownerFullName`, `taggedUsers`

### 图片是 URL，不是文件

每个图像和视频字段都是一个链接到 Instagram 的 CDN。没有任何内容被下载，并且**这些链接是经过签名的，并且几小时后过期。** 如果用户需要媒体本身，请立即使用自己的带宽获取它。

### 超过一分钟的运行

对于大型作业，启动异步并轮询，而不是保持同步连接：

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/apify~instagram-scraper/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"directUrls":["https://www.instagram.com/nasa/"],"resultsType":"posts","resultsLimit":1000}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")

curl -s "https://api.apify.com/v2/actor-runs/$RUN?waitForFinish=60" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])"

curl -s "https://api.apify.com/v2/actor-runs/$RUN/dataset/items?format=json" \
  -H "Authorization: Bearer $APIFY_TOKEN"
```

轮询，直到 `status` 是 `SUCCEEDED`，然后获取项目。`FAILED` 或 `ABORTED` 意味着停止并报告——不要静默重试用户正在付费的作业。

---

## 错误

| 状态 | 含义 | 做什么 |
|---|---|---|
| `401` | token 缺失、错误或被吊销 | 重新运行上面的 Setup 预检。不要重试调用。在 curl 路径中 CLI 登录时 `401` 意味着 token 被编造——切换到 `apify call`。 |
| `402` / `insufficient credit` | 月度信用额度已用尽 | 告诉用户；他们可以等待月度重置或升级到 https://apify.com/pricing?fpr=z8j1nz (推荐链接)。不要重试。 |
| `404` | Actor ID 或运行 ID 错误 | 检查 URL 是否使用 tilde 使用 `apify~instagram-scraper`，而不是斜杠。 |
| `408` / timeout | 同步调用超时限制 | 切换到上面的异步模式。 |
| 空数组 | 私人、已删除或确实为空 | 如实报告。**不要**假设这是一个计费问题。 |
| `apify call` 退出非零 | 运行失败，或 CLI 会话已消失 | CLI 打印原因和运行 URL——阅读它而不是重试。如果 `apify info` 也失败，会话已过期：重新运行 Setup。 |

空结果是一个真实答案。私人帐户、已删除的帖子和不活跃的标签都确实返回了空值。

### 需要准确报告的数据怪癖，而不是视为错误

- **`likesCount: -1`** 意味着创作者隐藏了点赞数。Instagram 不暴露它。说“由创作者隐藏” — 永远不要报告它为零或作为错误。
- **私人个人资料** 通常返回空值。一个例外：如果私人帐户在帖子中被标记为**合作者**，并且任何合著者都是公开的，Instagram 将该帖子视为公开的，它将出现在结果中。
- **指标可能与应用显示的指标不同。** Instagram 向未登录的访客提供略有不同的计数，并且大计数不断变化。小的差异是正常的。
- **结果计数不是保证的。** 没有固定的上限；您得到的正是 Instagram 公开的内容。为了检查应该可用的内容，请在隐身窗口中打开 URL。

---

## 成本纪律

用户按结果付费。将此视为真实金钱。

- **始终设置 `resultsLimit`。** 默认值是每个 URL 100 条结果；一个包含五个 URL 的调用在默认值下成本为 500 条结果，而用户可能只需要 25 条。
- **使用 `resultsType: "details"`** 对于任何关于粉丝、简介或帖子数量的问题。它返回每个个人资料 1 条结果。
- **从小开始。** 对于任何开放式内容，运行一个有界的第一次传递，向用户展示返回的内容，并在扩展之前确认。
- **在开始之前说明大运行的成本**。在 $2.30/1,000 的价格下，5,000 条结果的工作成本约为 $11.50。
- 永远不要在 `401` 或 `402` 后重试相同的调用——每次尝试都可能计费，而且它们都不会成功。
