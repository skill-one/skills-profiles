# 新闻搜索

> **需要 API 密钥**：在 https://api.search.brave.com 获取
>
> **套餐**：包含在 **搜索** 套餐中。查看 https://api-dashboard.search.brave.com/app/subscriptions/subscribe

## 快速入门 (cURL)

### 基本搜索
```bash
curl -s "https://api.search.brave.com/res/v1/news/search?q=space+exploration" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"
```

### 近期新闻（过去 24 小时）
```bash
curl -s "https://api.search.brave.com/res/v1/news/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=cybersecurity" \
  --data-urlencode "country=US" \
  --data-urlencode "freshness=pd" \
  --data-urlencode "count=20"
```

### 日期范围筛选
```bash
curl -s "https://api.search.brave.com/res/v1/news/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=climate summit" \
  --data-urlencode "freshness=2026-01-01to2026-01-31"
```

## 端点

```http
GET https://api.search.brave.com/res/v1/news/search
POST https://api.search.brave.com/res/v1/news/search
```

**认证**：`X-Subscription-Token: <API_KEY>` 头部

**注意**：支持 GET 和 POST 方法。POST 方法适用于长查询或复杂 Goggles。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|--|--|--|--|--|
| `q` | 字符串 | **是** | - | 搜索查询（1-400 个字符，最多 50 个词） |
| `country` | 字符串 | 否 | `US` | 搜索国家（2 字母国家代码或 `ALL`） |
| `search_lang` | 字符串 | 否 | `en` | 语言偏好（2+ 字符语言代码） |
| `ui_lang` | 字符串 | 否 | `en-US` | UI 语言（例如 "en-US"） |
| `count` | 整数 | 否 | `20` | 结果数量（1-50） |
| `offset` | 整数 | 否 | `0` | 页面偏移（0-9） |
| `safesearch` | 字符串 | 否 | `strict` | 成人内容过滤器（`off`/`moderate`/`strict`） |
| `freshness` | 字符串 | 否 | - | 时间过滤器（`pd`/`pw`/`pm`/`py` 或日期范围） |
| `spellcheck` | 布尔值 | 否 | `true` | 自动更正查询 |
| `extra_snippets` | 布尔值 | 否 | - | 每个结果最多 5 个附加摘要 |
| `goggles` | 字符串或数组 | 否 | - | 自定义排名过滤器（URL 或内联；重复参数用于多个） |
| `operators` | 布尔值 | 否 | `true` | 应用搜索运算符 |
| `include_fetch_metadata` | 布尔值 | 否 | `false` | 在结果中包含抓取时间戳 |

### Freshness 值

| 值 | 描述 |
|--|--|
| `pd` | 过去一天（24 小时）- 适用于突发新闻 |
| `pw` | 过去一周（7 天） |
| `pm` | 过去一个月（31 天） |
| `py` | 过去一年（365 天） |
| `YYYY-MM-DDtoYYYY-MM-DD` | 自定义日期范围 |

## 响应格式

```json
{
  "type": "news",
  "query": {
    "original": "space exploration"
  },
  "results": [
    {
      "type": "news_result",
      "title": "Space Exploration: New Developments",
      "url": "https://news.example.com/space-exploration",
      "description": "Recent missions have advanced our understanding of...",
      "age": "2 hours ago",
      "page_age": "2026-01-15T14:30:00",
      "page_fetched": "2026-01-15T15:00:00Z",
      "meta_url": {
        "scheme": "https",
        "netloc": "news.example.com",
        "hostname": "news.example.com",
        "favicon": "https://imgs.search.brave.com/favicon/news.example.com",
        "path": "/space-exploration"
      },
      "profile": {
        "name": "Example Outlet",
        "url": "https://news.example.com/space-exploration"
      },
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      }
    }
  ]
}
```

## 响应字段

| 字段 | 类型 | 描述 |
|--|--|--|
| `type` | 字符串 | 始终为 `"news"` |
| `query.original` | 字符串 | 原始搜索查询 |
| `query.altered` | 字符串? | 自动更正后的查询（如果已更改） |
| `query.cleaned` | 字符串? | 清理/规范化后的查询（来自自动更正器） |
| `query.spellcheck_off` | 布尔值? | 是否禁用自动更正 |
| `query.show_strict_warning` | 布尔值? | 如果严格 SafeSearch 阻止了结果，则为 True |
| `query.search_operators` | 对象? | 应用的搜索运算符 |
| `query.search_operators.applied` | 布尔值 | 是否应用了运算符 |
| `query.search_operators.cleaned_query` | 字符串? | 运算符处理后的查询 |
| `query.search_operators.sites` | 字符串列表? | 来自 `site:` 运算符的域名 |
| `results[].type` | 字符串 | 始终为 `"news_result"` |
| `results[].title` | 字符串 | 文章标题 |
| `results[].url` | 字符串 | 文章来源 URL |
| `results[].description` | 字符串? | 文章描述/摘要 |
| `results[].age` | 字符串? | 人类可读的年龄（例如 "2 hours ago"） |
| `results[].page_age` | 字符串? | 来源的发布日期（ISO 日期时间） |
| `results[].page_fetched` | 字符串? | 页面最后抓取时间（ISO 日期时间） |
| `results[].fetched_content_timestamp` | 整数? | 抓取时间戳（仅当 `include_fetch_metadata=true` 时） |
| `results[].meta_url.scheme` | 字符串? | URL 协议方案 |
| `results[].meta_url.netloc` | 字符串? | 网络位置 |
| `results[].meta_url.hostname` | 字符串? | 小写域名 |
| `results[].meta_url.favicon` | 字符串? | Favicon URL |
| `results[].meta_url.path` | 字符串? | URL 路径 |
| `results[].thumbnail.src` | 字符串 | 提供的缩略图 URL |
| `results[].thumbnail.original` | 字符串? | 原始缩略图 URL |
| `results[].extra_snippets` | 字符串列表? | 每个结果最多 5 个附加摘要 |
| `results[].profile.name` | 字符串? | 网站的名称 |
| `results[].profile.url` | 字符串? | 可以找到配置文件的原始 URL |
| `results[].profile.long_name` | 字符串? | 网站的完整名称 |
| `results[].profile.img` | 字符串? | 代表配置文件的提供图像 URL |

## Goggles（自定义排名）— Brave 独有

Goggles 允许你 **重新排序新闻结果** — 提升 trusted outlets 或抑制不想要的来源。

| 方法 | 示例 |
|--|--|
| **托管** | `--data-urlencode "goggles=https://raw.githubusercontent.com/brave/goggles-quickstart/main/goggles/hacker_news.goggle"` |
| **内联** | `--data-urlencode 'goggles=$discard\n$site=example.com'` |

> **托管** goggles 必须在 GitHub/GitLab 上，包含 `! name:`, `! description:`, `! author:` 头部，并在 https://search.brave.com/goggles/create 注册。**内联** 规则无需注册。

**语法**：规则以 `$` 开头 + 逗号分隔的选项。**操作**（选择一个）：`discard`, `boost[=N]`, `downrank[=N]` — N 是 1–10 的整数。**站点过滤器**：`site=DOMAIN`。示例：`$site=example.com,boost=3`。用 `\n`（`%0A`）分隔规则。

**允许列表**：`$discard\n$site=docs.python.org\n$site=developer.mozilla.org` — **阻止列表**：`$discard,site=pinterest.com\n$discard,site=quora.com`

**资源**：[发现](https://search.brave.com/goggles/discover) · [语法](https://search.brave.com/help/goggles) · [快速入门](https://github.com/brave/goggles-quickstart)

## 搜索运算符

使用搜索运算符来细化结果：
- `site:local-paper.com` - 限制到特定新闻网站
- `"exact phrase"` - 匹配确切短语
- `-exclude` - 排除术语

设置 `operators=false` 以禁用运算符解析。

## 用例

- **突发新闻监控**：使用 `freshness=pd` 获取主题的最新文章。
- **带 Goggles 的自定义新闻源**：提升 trusted sources 并丢弃其他来源 — Brave 独有。
- **历史新闻研究**：使用 `freshness=YYYY-MM-DDtoYYYY-MM-DD` 找到特定时间段的文章。
- **多语言新闻**：结合 `country`, `search_lang`, 和 `ui_lang` 获取跨区域结果。
- **数据管道**：设置 `include_fetch_metadata=true` 以在每个结果上获取 `fetched_content_timestamp`。

## 注意事项

- **SafeSearch**：默认为 `strict`
- **分页**：使用 `offset`（0-9）与 `count`
- **Extra snippets**：当 `extra_snippets=true` 时，最多 5 个附加摘要
