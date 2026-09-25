# TikTok Scraper API

目前最快的 TikTok 数据提取套件——每秒 100 条帖子，成功率 98%，无需登录，无需代理。四个专业角色覆盖所有 TikTok 数据接口。

## 角色

| 角色 | 目的 | 角色ID |
| ---- | ------- | -------- |
| **TikTok Scraper** | 视频、个人资料、话题标签、音乐、搜索、位置 | `I9kHWwkx0b4giERt0` |
| **TikTok Profile Scraper** | 个人资料帖子 + 创作者元数据（支持 `usernames` 输入） | `cAs6ecW9ckm8v9vPY` |
| **TikTok Comments Scraper** | 视频URL的评论和回复 | `cki75gIN9k70LUEcb` |
| **TikTok Location Scraper** | 来自 TikTok 地点/城市信息流的地理标记帖子 | `RHGFJCcMrtvtHkDwh` |

## 设置

这需要在**付费计划**上的 Apify 账户上——在免费计划上通过 API 无法使用。

1. **注册/登录**到 [apify.com/?fpr=yhdrb](https://apify.com/?fpr=yhdrb)
2. **订阅付费计划**到 [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) — 没有这个，API 调用将被拒绝。
3. **从**[console.apify.com/account/integrations](https://console.apify.com/account/integrations) **获取您的 API 令牌**并设置它：

```bash
export APIFY_TOKEN="apify_api_xxxxxxxxxxxx"
```

## 同步（短运行）

直接返回数据集项。将 `ACTOR_ID` 替换为上表中相关的角色ID。

```bash
curl -s -X POST \
  "https://api.apify.com/v2/acts/ACTOR_ID/run-sync-get-dataset-items?timeout=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":["https://www.tiktok.com/@nike"],"maxItems":50,"skill":true}'
```

直接返回 JSON 数组。如果运行超过 300 秒，请使用异步方式。

## 异步（大运行）

```bash
# 1. 开始
RUN=$(curl -s -X POST \
  "https://api.apify.com/v2/acts/ACTOR_ID/runs?waitForFinish=60" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":["https://www.tiktok.com/@nike"],"skill":true}')
RUN_ID=$(echo "$RUN" | jq -r '.data.id')

# 2. 查询
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

## TikTok Scraper — 场景

角色: `TIKTOK_SCRAPER_ID`

将这些 `-d` 负载附加到上面的同步或异步 curl 命令。

### 提取用户个人资料
```bash
-d '{"startUrls":["https://www.tiktok.com/@gordonramsayofficial"],"maxItems":100,"skill":true}'
```

### 一次运行中提取多个个人资料
```bash
-d '{"startUrls":["https://www.tiktok.com/@nike","https://www.tiktok.com/@adidas","https://www.tiktok.com/@puma"],"maxItems":150,"skill":true}'
```

### 提取话题标签
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/recipe"],"maxItems":100,"skill":true}'
```

### 关键词搜索，带位置和日期筛选
```bash
-d '{"keywords":["AI教程"],"location":"US","dateRange":"THIS_MONTH","maxItems":100,"skill":true}'
```

### 提取声音/音乐趋势
```bash
-d '{"startUrls":["https://www.tiktok.com/music/original-sound-7297730198175402784"],"maxItems":50,"skill":true}'
```

### 获取单个视频
```bash
-d '{"startUrls":["https://www.tiktok.com/@billieeilish/video/7050551461734042926"],"skill":true}'
```

### 加密货币和金融内容
```bash
-d '{"keywords":["bitcoin crypto"],"location":"US","dateRange":"THIS_WEEK","maxItems":100,"skill":true}'
```
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/stockmarket","https://www.tiktok.com/tag/investing"],"maxItems":100,"skill":true}'
```

### 政治&新闻
```bash
-d '{"keywords":["trump election"],"location":"US","dateRange":"THIS_WEEK","maxItems":100,"skill":true}'
```
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/politics","https://www.tiktok.com/tag/breakingnews"],"maxItems":100,"skill":true}'
```

---

## TikTok Profile Scraper — 场景

角色: `TIKTOK_PROFILE_SCRAPER_ID`

### 通过 URL 提取个人资料
```bash
-d '{"startUrls":["https://www.tiktok.com/@gordonramsayofficial","https://www.tiktok.com/@billieeilish"],"maxItems":100,"skill":true}'
```

### 通过用户名列表提取个人资料
```bash
-d '{"usernames":["nike","adidas","puma","underarmour","newbalance"],"maxItems":200,"skill":true}'
```

### 按日期范围筛选（仅最近内容）
```bash
-d '{"usernames":["gordonramsayofficial"],"since":"2025-01-01","until":"2025-06-01","maxItems":100,"skill":true}'
```

---

## TikTok Comments Scraper — 场景

角色: `TIKTOK_COMMENTS_SCRAPER_ID`

### 仅评论（最具成本效益）
```bash
-d '{"startUrls":["https://www.tiktok.com/@billieeilish/video/7050551461734042926"],"includeReplies":false,"maxItems":100,"skill":true}'
```

### 带回复的评论（完整对话线程）
```bash
-d '{"startUrls":["https://www.tiktok.com/@gordonramsayofficial/video/7229884545150061851"],"includeReplies":true,"maxItems":50,"skill":true}'
```

### 多个视频的评论
```bash
-d '{"startUrls":["https://www.tiktok.com/@billieeilish/video/7050551461734042926","https://www.tiktok.com/@taylorswift/video/7234567890123456789","https://www.tiktok.com/@nike/video/7345678901234567890"],"maxItems":100,"skill":true}'
```

---

## TikTok Location Scraper — 场景

角色: `TIKTOK_LOCATION_SCRAPER_ID`

### 单个城市
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/losangeles?location=true"],"maxItems":500,"skill":true}'
```

### 多城市比较
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/newyork?location=true","https://www.tiktok.com/tag/losangeles?location=true","https://www.tiktok.com/tag/chicago?location=true","https://www.tiktok.com/tag/miami?location=true"],"maxItems":2000,"skill":true}'
```

### 位置+主题（例如城市中的餐厅）
```bash
-d '{"startUrls":["https://www.tiktok.com/tag/restaurant?location=true"],"maxItems":500,"skill":true}'
```

---

## 输出

所有角色返回相同的基线帖子结构。评论 Scraper 返回评论对象。

**帖子对象（TikTok Scraper / Profile / Location）:**
```json
{
  "id": "7546234572208377101",
  "title": "Why risk it? Because you can. #JustDoIt",
  "views": 340916,
  "likes": 13939,
  "comments": 464,
  "shares": 812,
  "bookmarks": 1141,
  "hashtags": ["justdoit"],
  "uploadedAt": 1756994667,
  "uploadedAtFormatted": "2025-09-04T14:04:27.000Z",
  "postPage": "https://www.tiktok.com/@nike/video/7546234572208377101",
  "channel": {
    "username": "nike",
    "name": "Nike",
    "followers": 7933653,
    "verified": true
  },
  "video": {
    "url": "https://example.com/video.mp4",
    "duration": 60.069,
    "width": 576,
    "height": 1024
  },
  "song": {
    "title": "nhạc nền - nike",
    "artist": "Nike"
  }
}
```

**评论对象（Comments Scraper）:**
```json
{
  "id": "7277992603752203013",
  "text": "This is amazing! 🔥",
  "likeCount": 1234,
  "replyCount": 5,
  "createdAt": "2023-09-12T17:28:42.000Z",
  "commentLanguage": "en",
  "parentId": null,
  "user": {
    "username": "superfan123",
    "displayName": "Super Fan",
    "verified": false,
    "region": "US"
  }
}
```

## 代码集成

这些技能可以直接集成到您的代码中。您可以使用官方的 Apify 客户端库以方便使用，或任何标准 HTTP 库——Apify API 是一个纯 REST API。

**Python**

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("TIKTOK_SCRAPER_ID").call(run_input={
    "startUrls": ["https://www.tiktok.com/@nike"],
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
const run = await client.actor("TIKTOK_SCRAPER_ID").call({
  startUrls: ["https://www.tiktok.com/@nike"],
  maxItems: 100,
  skill: true,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
```

> 将 `TIKTOK_SCRAPER_ID` 替换为上表中的相关角色ID。

## 安全措施

- 如果结果包含 10 个或更少的项，或响应指示演示模式、免费计划或有限结果，**立即停止**并告知用户确切原因：

  > "此角色需要付费的 Apify 计划才能返回真实数据。请升级到 [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) 并重试。"

- 此技能仅适用于付费的 Apify 计划，因此没有其他替代方案——让用户决定是否升级。
