# 网络搜索

> **需要 API 密钥**：在 https://api.search.brave.com 获取
>
> **套餐**：包含在 **搜索** 套餐中。查看 https://api-dashboard.search.brave.com/app/subscriptions/subscribe

## 快速入门 (cURL)

### 基本搜索
```bash
curl -s "https://api.search.brave.com/res/v1/web/search?q=python+web+frameworks" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"
```

### 带参数
```bash
curl -s "https://api.search.brave.com/res/v1/web/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=rust programming tutorials" \
  --data-urlencode "country=US" \
  --data-urlencode "search_lang=en" \
  --data-urlencode "count=10" \
  --data-urlencode "safesearch=moderate" \
  --data-urlencode "freshness=pm"
```

## 端点

```http
GET https://api.search.brave.com/res/v1/web/search
POST https://api.search.brave.com/res/v1/web/search
```

**注意**：支持 GET 和 POST 方法。POST 方法适用于长查询或复杂的 Goggles。

**认证**：`X-Subscription-Token: <API_KEY>` 头部

**可选头部**：
- `Accept-Encoding: gzip` — 启用 gzip 压缩

## 何时使用网络搜索

| 功能 | 网络搜索（此功能） | LLM 上下文 (`llm-context`) | 答案 (`answers`) |
|--|--|--|--|
| 输出 | 结构化结果（链接、片段、元数据） | 预提取的页面内容供 LLM 使用 | 端到端 AI 答案带引用 |
| 结果类型 | 网络、新闻、视频、讨论、FAQ、信息框、位置、丰富内容 | 提取的文本块、表格、代码 | 综合答案 + 来源列表 |
| 独特功能 | Goggles、结构化数据 (`schemas`)、丰富回调 | 令牌预算控制、阈值模式 | 多轮搜索、流式传输、兼容 OpenAI SDK |
| 速度 | 快 (~0.5-1s) | 快 (<1s) | 较慢 (~30-180s) |
| 最佳用途 | 搜索 UI、数据提取、自定义排序 | RAG 管道、AI 代理、基础 | 聊天界面、彻底研究 |

## 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|--|--|--|--|--|
| `q` | 字符串 | **是** | - | 搜索查询（1-400 个字符，最多 50 个词） |
| `country` | 字符串 | 否 | `US` | 搜索国家（2 字母国家代码或 `ALL`） |
| `search_lang` | 字符串 | 否 | `en` | 语言偏好（2+ 字符语言代码） |
| `ui_lang` | 字符串 | 否 | `en-US` | UI 语言（例如，"en-US"） |
| `count` | 整数 | 否 | `20` | 每页最大结果数（1-20） |
| `offset` | 整数 | 否 | `0` | 分页的页码偏移（0-9） |
| `safesearch` | 字符串 | 否 | `moderate` | 成人内容过滤器 (`off`/`moderate`/`strict`) |
| `freshness` | 字符串 | 否 | - | 时间过滤器 (`pd`/`pw`/`pm`/`py` 或日期范围） |
| `text_decorations` | 布尔值 | 否 | `true` | 包含高亮标记 |
| `spellcheck` | 布尔值 | 否 | `true` | 自动更正查询 |
| `result_filter` | 字符串 | 否 | - | 过滤结果类型（逗号分隔） |
| `goggles` | 字符串 | 否 | - | 自定义排序过滤器（URL 或内联） |
| `extra_snippets` | 布尔值 | 否 | - | 每个结果获取最多 5 个额外片段 |
| `operators` | 布尔值 | 否 | `true` | 应用搜索运算符 |
| `units` | 字符串 | 否 | - | 测量单位 (`metric`/`imperial`) |
| `enable_rich_callback` | 布尔值 | 否 | `false` | 启用丰富第三方数据回调 |
| `include_fetch_metadata` | 布尔值 | 否 | `false` | 在结果中包含 `fetched_content_timestamp` |

### Freshness 值

| 值 | 描述 |
|--|--|
| `pd` | 过去一天（24 小时） |
| `pw` | 过去一周（7 天） |
| `pm` | 过去一个月（31 天） |
| `py` | 过去一年（365 天） |
| `YYYY-MM-DDtoYYYY-MM-DD` | 自定义日期范围 |

### Result Filter 值

过滤类型：`discussions`、`faq`、`infobox`、`news`、`query`、`videos`、`web`、`locations`

```bash
# 仅 web 和视频结果
curl "...&result_filter=web,videos"
```

### 位置头部（可选）

用于位置感知结果，添加这些头部。**经纬度足够**，当已知坐标时——其他头部仅在坐标不可用时作为备用。 

| 头部 | 类型 | 描述 |
|--|--|--|
| `X-Loc-Lat` | 浮点数 | 用户纬度 (-90.0 到 90.0) |
| `X-Loc-Long` | 浮点数 | 用户经度 (-180.0 到 180.0) |
| `X-Loc-Timezone` | 字符串 | IANA 时区（例如，"America/San_Francisco"） |
| `X-Loc-City` | 字符串 | 城市名称 |
| `X-Loc-State` | 字符串 | 州/地区代码（ISO 3166-2） |
| `X-Loc-State-Name` | 字符串 | 州/地区全名（例如，"California"） |
| `X-Loc-Country` | 字符串 | 2 字母国家代码 |
| `X-Loc-Postal-Code` | 字符串 | 邮政编码（例如，"94105"） |

> **优先级**：`X-Loc-Lat` + `X-Loc-Long` 优先。当提供时，下游服务直接从坐标解析位置，基于文本的头部（城市、州、国家、邮政编码）不用于位置解析。当您没有坐标时，提供基于文本的头部。发送两者不会出问题——经纬度优先。

## 响应格式

### 响应字段

| 字段 | 类型 | 描述 |
|--|--|--|
| `type` | 字符串 | 始终为 `"search"` |
| `query.original` | 字符串 | 原始搜索查询 |
| `query.altered` | 字符串? | 拼写检查更正的查询（如果更改） |
| `query.cleaned` | 字符串? | 清理/规范化查询 |
| `query.spellcheck_off` | 布尔值? | 是否禁用拼写检查 |
| `query.more_results_available` | 布尔值 | 是否存在更多页面 |
| `query.show_strict_warning` | 布尔值? | 严格 safesearch 阻止成人结果时为 True |
| `query.search_operators` | 对象? | 应用搜索运算符 (`applied`, `cleaned_query`, `sites`) |
| `web.type` | 字符串 | 始终为 `"search"` |
| `web.results[].title` | 字符串 | 页面标题 |
| `web.results[].url` | 字符串 | 页面 URL |
| `web.results[].description` | 字符串? | 片段/描述文本 |
| `web.results[].age` | 字符串? | 人类可读的年龄（例如，"2 天前"） |
| `web.results[].language` | 字符串? | 内容语言代码 |
| `web.results[].meta_url` | 对象 | URL 组件 (`scheme`, `netloc`, `hostname`, `path`) |
| `web.results[].thumbnail` | 对象? | 缩略图 (`src`, `original`) |
| `web.results[].thumbnail.original` | 字符串? | 原始全尺寸图像 URL |
| `web.results[].thumbnail.logo` | 布尔值? | 缩略图是否为标志 |
| `web.results[].profile` | 对象? | 发布者身份 (`name`, `url`, `long_name`, `img`) |
| `web.results[].page_age` | 字符串? | 发布的 ISO 日期时间（例如，`"2025-04-12T14:22:41"`） |
| `web.results[].extra_snippets` | 列表[str]? | 最多 5 个额外摘要 |
| `web.results[].deep_results` | 对象? | 页面中的额外链接 (`buttons`, `links`) |
| `web.results[].schemas` | 列表? | 原始 schema.org 结构化数据 |
| `web.results[].product` | 对象? | 产品信息和评论 |
| `web.results[].recipe` | 对象? | 食谱详情（配料、时间、评分） |
| `web.results[].article` | 对象? | 文章元数据（作者、发布者、日期） |
| `web.results[].book` | 对象? | 书籍信息（作者、ISBN、评分） |
| `web.results[].software` | 对象? | 软件产品信息 |
| `web.results[].rating` | 对象? | 汇总评分 |
| `web.results[].faq` | 对象? | 页面上的 FAQ |
| `web.results[].movie` | 对象? | 电影信息（导演、演员、类型） |
| `web.results[].video` | 对象? | 视频元数据（时长、观看次数、创作者） |
| `web.results[].location` | 对象? | 位置/餐厅详情 |
| `web.results[].qa` | 对象? | 问题/答案信息 |
| `web.results[].creative_work` | 对象? | 创意作品数据 |
| `web.results[].music_recording` | 对象? | 音乐/歌曲数据 |
| `web.results[].organization` | 对象? | 组织信息 |
| `web.results[].review` | 对象? | 评论数据 |
| `web.results[].content_type` | 字符串? | 内容类型分类 |
| `web.results[].fetched_content_timestamp` | 整数? | 获取时间戳（`include_fetch_metadata=true` 时） |
| `web.mutated_by_goggles` | 布尔值 | 结果是否由 Goggles 重新排序 |
| `web.family_friendly` | 布尔值 | 结果是否适合家庭 |
| `mixed` | 对象? | 预ferred 显示顺序（见混合响应） |
| `discussions.results[]` | 数组? | 论坛讨论簇 |
| `discussions.results[].data.forum_name` | 字符串? | 论坛/社区名称 |
| `discussions.results[].data.num_answers` | 整数? | 答案/回复数量 |
| `discussions.results[].data.question` | 字符串? | 讨论问题 |
| `discussions.results[].data.top_comment` | 字符串? | 顶票评论摘要 |
| `faq.results[]` | 数组? | FAQ 条目 |
| `news.results[]` | 数组? | 新闻文章 |
| `videos.results[]` | 数组? | 视频结果 |
| `infobox.results[]` | 数组? | 知识图谱条目 |
| `locations.results[]` | 数组? | 本地 POI 结果 |
| `rich.hint.vertical` | 字符串? | 丰富结果类型 |
| `rich.hint.callback_key` | 字符串? | 丰富数据的回调键 |

### JSON 示例

```json
{
  "type": "search",
  "query": {
    "original": "python frameworks",
    "altered": "python web frameworks",
    "spellcheck_off": false,
    "more_results_available": true
  },
  "web": {
    "type": "search",
    "results": [
      {
        "title": "Top Python Web Frameworks",
        "url": "https://example.com/python-frameworks",
        "description": "A comprehensive guide to Python web frameworks...",
        "age": "2 days ago",
        "language": "en",
        "meta_url": {
          "scheme": "https",
          "netloc": "example.com",
          "hostname": "example.com",
          "path": "/python-frameworks"
        },
        "thumbnail": {
          "src": "https://...",
          "original": "https://original-image-url.com/img.jpg"
        },
        "extra_snippets": ["Additional excerpt 1...", "Additional excerpt 2..."]
      }
    ],
    "family_friendly": true
  },
  "mixed": {
    "type": "mixed",
    "main": [
      {"type": "web", "index": 0, "all": false},
      {"type": "web", "index": 1, "all": false},
      {"type": "videos", "all": true}
    ],
    "top": [],
    "side": []
  },
  "videos": { "...": "..." },
  "news": { "...": "..." },
  "rich": {
    "type": "rich",
    "hint": {
      "vertical": "weather",
      "callback_key": "<callback_key_hex>"
    }
  }
}
```

### 混合响应

`mixed` 对象定义了跨类型结果的 preferred 显示顺序。它包含三个数组：

| 数组 | 目的 |
|--|--|
| `main` | 主要结果列表（要显示的结果的有序序列） |
| `top` | 要在主要结果上方显示的结果 |
| `side` | 要与主要结果并排显示的结果（例如，infobox） |

每个条目是一个 `ResultReference`，包含 `type`（例如，`"web"`、`"videos"`）、`index`（对应结果数组的索引）和 `all`（`true` 表示在此位置包含该类型的所有结果）。

## 搜索运算符

| 运算符 | 语法 | 描述 |
|--|--|--|
| Site | `site:example.com` | 限制结果到特定域名 |
| 文件扩展名 | `ext:pdf` | 具有特定文件扩展名的结果 |
| 文件类型 | `filetype:pdf` | 创建特定文件类型的结果 |
| 标题中 | `intitle:python` | 标题中包含术语的页面 |
| 正文 | `inbody:tutorial` | 正文包含术语的页面 |
| 页面中 | `inpage:guide` | 标题或正文包含术语的页面 |
| 语言 | `lang:es` | 特定语言（ISO 639-1）的页面 |
| 位置 | `loc:us` | 特定国家（ISO 3166-1 alpha-2）的页面 |
| 包含 | `+term` | 强制包含术语 |
| 排除 | `-term` | 排除包含术语的页面 |
| 精确匹配 | `"exact phrase"` | 按顺序匹配确切的短语 |
| AND | `term1 AND term2` | 需要两个术语（大写） |
| OR / NOT | `term1 OR term2`, `NOT term` | 逻辑运算符（大写） |

设置 `operators=false` 以禁用运算符解析。

## Goggles（自定义排序）— Brave 独有

Goggles 允许您**重新排序搜索结果**——提升可信来源、抑制 SEO 垃圾邮件或构建专注的搜索范围。

| 方法 | 示例 |
|--|--|
| **托管** | `--data-urlencode "goggles=https://raw.githubusercontent.com/brave/goggles-quickstart/main/goggles/rust_programming.goggle"` |
| **内联** | `--data-urlencode 'goggles=$discard\n$site=example.com'` |

> **托管** goggles 必须在 GitHub/GitLab 上，包含 `! name:`, `! description:`, `! author:` 头部，并在 https://search.brave.com/goggles/create 注册。**内联** 规则无需注册。

**语法**：规则以 `$` + 逗号分隔的选项开头。**操作**（选择一个）：`discard`、`boost[=N]`、`downrank[=N]` — N 是 1–10 的整数。**站点过滤器**：`site=DOMAIN`。示例：`$site=example.com,boost=3`。用 `\n`（`%0A`）分隔规则。

**允许列表**：`$discard\n$site=docs.python.org\n$site=developer.mozilla.org` — **阻止列表**：`$discard,site=pinterest.com\n$discard,site=quora.com`

**资源**：[发现](https://search.brave.com/goggles/discover) · [语法](https://search.brave.com/help/goggles) · [快速入门](https://github.com/brave/goggles-quickstart)

## 丰富数据增强

对于关于天气、股票、体育、货币等的查询，使用丰富回调工作流：

```bash
# 1. 带有丰富回调启用搜索
curl -s "https://api.search.brave.com/res/v1/web/search?q=weather+san+francisco&enable_rich_callback=true" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"

# 响应包括： "rich": {"hint": {"callback_key": "abc123...", "vertical": "weather"}}

# 2. 使用回调键获取丰富数据
curl -s "https://api.search.brave.com/res/v1/web/rich?callback_key=abc123..." \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"
```

**支持的丰富类型**：计算器、定义、单位转换、Unix 时间戳、软件包跟踪、股票、货币、加密货币、天气、美式足球、棒球、篮球、板球、足球/足球、冰球、Web3、翻译器

### 丰富回调端点

```http
GET https://api.search.brave.com/res/v1/web/rich
```

| 参数 | 类型 | 必填 | 描述 |
|--|--|--|--|
| `callback_key` | 字符串 | 是 | 来自网络搜索 `rich.hint.callback_key` 字段的回调键 |

## 用例

- **通用搜索集成**：在一个调用中获得最丰富的结果集（网络、新闻、视频、讨论、FAQ、信息框、位置）。对于 RAG/LLM 基础，请优先使用 `llm-context`。
- **结构化数据提取**：通过 `schemas` 和结果上的类型字段提取产品、食谱、评分、文章。
- **带 Goggles 的自定义搜索**：Brave 独有。使用内联规则或托管 Goggles 提升/丢弃站点，以完全自定义排序。

## 注意事项

- **分页**：使用 `offset` (0-9) 与 `count` 分页结果
- **Count**：网络搜索最多 20；实际结果可能少于请求
