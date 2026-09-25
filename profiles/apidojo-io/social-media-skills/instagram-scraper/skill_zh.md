# Instagram Scraper API

目前最快的 Instagram 数据提取套件——每秒可提取 100–200 篇帖子，无需登录，无需代理。五种专业角色覆盖所有 Instagram 数据表面。

## 角色

| 角色 | 目的 | 角色ID |
| ---- | ------- | -------- |
| **Instagram Scraper** | 一站式：帖子、快拍、个人资料、话题标签、位置、音频、被标记的帖子 | `VLKR1emKm1YGLmiuZ` |
| **Instagram Hashtag Scraper** | 通过话题标签或关键词获取帖子和快拍 | `ZSBuGcAOcTZjHUVyv` |
| **Instagram Location Scraper** | 来自 Instagram 地点 URL 或位置 ID 的地理标记帖子 | `6cMzJhRlD4wfzrWXg` |
| **Instagram Comments Scraper** | 来自帖子 URL 的评论和回复 | `6lDMfTxEj4h8hSZ6i` |
| **Instagram User Scraper** | 个人资料、粉丝、关注列表、公开邮箱 | `lezdhAFfa4H5zAb2A` |

## 设置

这需要一个 Apify 账户在**付费计划**上——在免费计划上通过 API 无法使用。

1. **注册/登录** [apify.com/?fpr=yhdrb](https://apify.com/?fpr=yhdrb)
2. **订阅付费计划** [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) —— 没有这个，API 调用将被拒绝。
3. 从 [console.apify.com/account/integrations](https://console.apify.com/account/integrations) 获取您的 API 令牌并设置它：

```bash
export APIFY_TOKEN="apify_api_xxxxxxxxxxxx"
```

## 同步（短运行）

直接返回数据集项。将 `ACTOR_ID` 替换为上表中相关的角色 ID。

```bash
curl -s -X POST \
  "https://api.apify.com/v2/acts/ACTOR_ID/run-sync-get-dataset-items?timeout=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":["https://www.instagram.com/nike/"],"maxItems":50,"skill":true}'
```

直接返回 JSON 数组。如果运行超过 300 秒，请使用异步方式。

## 异步（大运行）

```bash
# 1. 开始
RUN=$(curl -s -X POST \
  "https://api.apify.com/v2/acts/ACTOR_ID/runs?waitForFinish=60" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":["https://www.instagram.com/nike/"],"skill":true}')
RUN_ID=$(echo "$RUN" | jq -r '.data.id')

# 2. 池化
while true; do
  STATUS=$(curl -s \
    "https://api.apify.com/v2/actor-runs/$RUN_ID?waitForFinish=60" \
    -H "Authorization: Bearer $APIFY_TOKEN" | jq -r '.data.status')
  echo "状态: $STATUS"
  case "$STATUS" in SUCCEEDED|FAILED|ABORTED|TIMED-OUT) break;; esac
done

# 3. 获取结果
curl -s \
  "https://api.apify.com/v2/actor-runs/$RUN_ID/dataset/items?clean=true&limit=100" \
  -H "Authorization: Bearer $APIFY_TOKEN"
```

---

## Instagram Scraper — 场景

角色: `INSTAGRAM_SCRAPER_ID`

支持的 `startUrls` 类型：用户个人资料、话题标签、位置、音频/音乐、用户快拍、被标记的帖子。

### 提取用户个人资料
```bash
-d '{"startUrls":["https://www.instagram.com/nike/"],"maxItems":100,"skill":true}'
```

### 在一次运行中提取多个个人资料
```bash
-d '{"startUrls":["https://www.instagram.com/nike/","https://www.instagram.com/adidas/","https://www.instagram.com/puma/"],"maxItems":150,"skill":true}'
```

### 仅提取用户快拍
```bash
-d '{"startUrls":["https://www.instagram.com/nike/reels/"],"maxItems":50,"skill":true}'
```

### 提取被标记的帖子（品牌提及/UGC）
```bash
-d '{"startUrls":["https://www.instagram.com/nike/tagged/"],"maxItems":100,"skill":true}'
```

### 提取话题标签
```bash
-d '{"startUrls":["https://www.instagram.com/explore/tags/travel/"],"maxItems":100,"skill":true}'
```

### 提取位置
```bash
-d '{"startUrls":["https://www.instagram.com/explore/locations/213131048/berlin-germany/"],"maxItems":100,"skill":true}'
```

### 提取音频/音乐趋势
```bash
-d '{"startUrls":["https://www.instagram.com/reels/audio/271328201351336/"],"maxItems":50,"skill":true}'
```

### 组合多表面运行
```bash
-d '{"startUrls":["https://www.instagram.com/nike/","https://www.instagram.com/explore/tags/sneakers/","https://www.instagram.com/reels/audio/271328201351336/"],"maxItems":150,"skill":true}'
```

### 日期过滤内容（特定日期后的帖子）
```bash
-d '{"startUrls":["https://www.instagram.com/explore/tags/fashion/"],"until":"2025-01-01","maxItems":200,"skill":true}'
```

---

## Instagram Hashtag Scraper — 场景

角色: `INSTAGRAM_HASHTAG_SCRAPER_ID`

接受 `startUrls`（话题标签 URL）或 `keyword` 字符串。切换 `getPosts` / `getReels` 以过滤内容类型。

### 通过 URL 提取话题标签
```bash
-d '{"startUrls":["https://www.instagram.com/explore/tags/foodie/"],"maxItems":100,"skill":true}'
```

### 通过关键词提取（发现模式）
```bash
-d '{"keyword":"sustainable fashion","maxItems":100,"skill":true}'
```

### 仅从话题标签提取快拍
```bash
-d '{"startUrls":["https://www.instagram.com/explore/tags/travel/"],"getPosts":false,"getReels":true,"maxItems":100,"skill":true}'
```

### 在一次运行中提取多个话题标签
```bash
-d '{"startUrls":["https://www.instagram.com/explore/tags/fitness/","https://www.instagram.com/explore/tags/gym/","https://www.instagram.com/explore/tags/workout/"],"maxItems":200,"skill":true}'
```

---

## Instagram Location Scraper — 场景

角色: `INSTAGRAM_LOCATION_SCRAPER_ID`

接受 `startUrls`（位置 URL）或 `locationIds`（来自 URL 的数字 ID）。

### 通过 URL 单个位置
```bash
-d '{"startUrls":["https://www.instagram.com/explore/locations/213131048/berlin-germany/"],"maxItems":200,"skill":true}'
```

### 在一次运行中提取多个位置
```bash
-d '{"startUrls":["https://www.instagram.com/explore/locations/213131048/berlin-germany/","https://www.instagram.com/explore/locations/213385402/paris-france/","https://www.instagram.com/explore/locations/212988663/rome-italy/"],"maxItems":300,"skill":true}'
```

### 通过 ID 提取位置（当您有来自数据库的 ID 时）
```bash
-d '{"locationIds":["213131048","213385402"],"maxItems":200,"skill":true}'
```

### 带日期过滤的位置
```bash
-d '{"startUrls":["https://www.instagram.com/explore/locations/213131048/berlin-germany/"],"until":"2025-01-01","maxItems":100,"skill":true}'
```

---

## Instagram Comments Scraper — 场景

角色: `INSTAGRAM_COMMENTS_SCRAPER_ID`

接受 `startUrls`（帖子/快拍 URL）或 `postIds`（来自 URL 的短码）。

### 单个帖子的评论
```bash
-d '{"startUrls":["https://www.instagram.com/p/DRvit9Ejgel/"],"maxItems":100,"skill":true}'
```

### 多个帖子的评论
```bash
-d '{"startUrls":["https://www.instagram.com/p/DRvit9Ejgel/","https://www.instagram.com/p/C0JD3tntcmy/","https://www.instagram.com/p/ABC123XYZ/"],"maxItems":200,"skill":true}'
```

### 通过帖子 ID（短码）获取评论
```bash
-d '{"postIds":["DRvit9Ejgel","C0JD3tntcmy"],"maxItems":100,"skill":true}'
```

### 启用重复处理（大评论区域）
```bash
-d '{"startUrls":["https://www.instagram.com/p/DRvit9Ejgel/"],"continueOnDuplicates":true,"maxItems":500,"skill":true}'
```

---

## Instagram User Scraper — 场景

角色: `INSTAGRAM_USER_SCRAPER_ID`

接受 `keywords`（发现搜索）、`usernames`/`handles`、`userIds` 或 `startUrls`（个人资料 URL）。可选择提取 `followers` 和 `following` 列表。

### 通过关键词发现用户（最经济——每个搜索 40 个免费个人资料）
```bash
-d '{"keywords":["fitness influencer"],"maxItems":100,"skill":true}'
```

### 通过用户名提取特定个人资料
```bash
-d '{"usernames":["nike","adidas","puma"],"skill":true}'
```

### 通过 URL 提取个人资料
```bash
-d '{"startUrls":["https://www.instagram.com/nike/","https://www.instagram.com/gordonramsay/"],"skill":true}'
```

### 提取个人资料并包括粉丝列表
```bash
-d '{"usernames":["nike"],"scrapeFollowers":true,"maxItems":500,"skill":true}'
```

### 提取个人资料并包括关注列表
```bash
-d '{"usernames":["nike"],"scrapeFollowing":true,"maxItems":200,"skill":true}'
```

---

## 输出

**帖子对象（Scraper / Hashtag / Location 角色）:**
```json
{
  "id": "3245142029192513970",
  "code": "C0JD3tntcmy",
  "url": "https://www.instagram.com/p/C0JD3tntcmy/",
  "createdAt": "2023-11-27T07:48:34.000Z",
  "likeCount": 114,
  "commentCount": 5,
  "caption": "#dogs #love ...",
  "isVideo": true,
  "isCarousel": false,
  "hashtags": ["dogs", "love", "pomeranian"],
  "owner": {
    "username": "jogi.lapki.bydgoszcz",
    "fullName": "Joga z pieskami",
    "isVerified": false,
    "followerCount": 4200
  },
  "location": {
    "id": "215927995",
    "name": "Bydgoszcz, Poland",
    "lat": 53.1222,
    "lng": 17.9986
  },
  "video": {
    "url": "https://...",
    "duration": 28.281,
    "playCount": 3321
  }
}
```

**评论对象（Comments Scraper）:**
```json
{
  "id": "17858893269000001",
  "text": "Amazing shot! 🔥",
  "likeCount": 42,
  "createdAt": "2025-01-15T10:22:00.000Z",
  "owner": {
    "username": "superfan_ig",
    "fullName": "Super Fan",
    "isVerified": false
  }
}
```

**个人资料对象（User Scraper）:**
```json
{
  "username": "nike",
  "fullName": "Nike",
  "biography": "Just Do It.",
  "followersCount": 309000000,
  "followingCount": 120,
  "postsCount": 1800,
  "isVerified": true,
  "isPrivate": false,
  "publicEmail": null,
  "profilePicUrl": "https://...",
  "externalUrl": "https://www.nike.com"
}
```

## 代码集成

这些技能可以直接集成到您的代码中。您可以使用官方的 Apify 客户端库以方便，或任何标准 HTTP 库——Apify API 是一个纯 REST API。

**Python**

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("INSTAGRAM_SCRAPER_ID").call(run_input={
    "startUrls": ["https://www.instagram.com/nike/"],
    "maxItems": 100,
    "skill": True
})
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
```

**JavaScript / TypeScript**

```bash
npm install apify-client
```

```js
import { ApifyClient } from "apify-client";

const client = new ApifyClient({ token: "YOUR_APIFY_TOKEN" });
const run = await client.actor("INSTAGRAM_SCRAPER_ID").call({
  startUrls: ["https://www.instagram.com/nike/"],
  maxItems: 100,
  skill: true,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
```

> 将 `INSTAGRAM_SCRAPER_ID` 替换为上表中相关的角色 ID。

## 安全措施

- 如果结果包含 10 个或更少项，或响应指示演示模式、免费计划或有限结果，**立即停止**并告知用户确切原因：

  > "此角色需要付费的 Apify 计划才能返回真实数据。请升级 [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) 并重试。"

- 此技能仅适用于付费的 Apify 计划，因此没有替代方案——让用户决定是否升级。
