# 图片搜索

> **需要 API 密钥**：在 https://api.search.brave.com 获取
>
> **套餐**：包含在 **搜索** 套餐中。查看 https://api-dashboard.search.brave.com/app/subscriptions/subscribe

## 快速入门 (cURL)

### 基本搜索
```bash
curl -s "https://api.search.brave.com/res/v1/images/search?q=mountain+landscape" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}"
```

### 带参数
```bash
curl -s "https://api.search.brave.com/res/v1/images/search" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_SEARCH_API_KEY}" \
  -G \
  --data-urlencode "q=northern lights photography" \
  --data-urlencode "country=US" \
  --data-urlencode "search_lang=en" \
  --data-urlencode "count=20" \
  --data-urlencode "safesearch=strict"
```

## 端点

```http
GET https://api.search.brave.com/res/v1/images/search
```

**认证**：`X-Subscription-Token: <API_KEY>` 头部

## 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|--|--|--|--|--|
| `q` | 字符串 | **是** | - | 搜索查询 (1-400字符，最多50个词) |
| `country` | 字符串 | 否 | `US` | 搜索国家 (2字母国家代码或`ALL`) |
| `search_lang` | 字符串 | 否 | `en` | 2+字符语言代码 |
| `count` | 整数 | 否 | 50 | 返回结果数量 (1-200) |
| `safesearch` | 字符串 | 否 | `strict` | `off` 或 `strict` (图片不提供`moderate`) |
| `spellcheck` | 布尔值 | 否 | true | 自动纠正查询；纠正后的查询在`query.altered`中 |

## 响应格式

```json
{
  "type": "images",
  "query": {
    "original": "mountain landscape",
    "altered": null,
    "spellcheck_off": false,
    "show_strict_warning": false
  },
  "results": [
    {
      "type": "image_result",
      "title": "Beautiful Mountain Landscape",
      "url": "https://example.com/mountain-photo",
      "source": "example.com",
      "page_fetched": "2025-09-15T10:30:00Z",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/...",
        "width": 200,
        "height": 150
      },
      "properties": {
        "url": "https://example.com/images/mountain.jpg",
        "placeholder": "https://imgs.search.brave.com/placeholder/...",
        "width": 1920,
        "height": 1080
      },
      "meta_url": {
        "scheme": "https",
        "netloc": "example.com",
        "hostname": "example.com",
        "favicon": "https://imgs.search.brave.com/favicon/...",
        "path": "/mountain-photo"
      },
      "confidence": "high"
    }
  ],
  "extra": {
    "might_be_offensive": false
  }
}
```

## 响应字段

| 字段 | 类型 | 描述 |
|--|--|--|
| `type` | 字符串 | 始终为`"images"` |
| `query.original` | 字符串 | 原始查询 |
| `query.altered` | 字符串? | 拼写检查后的查询 (无纠正时为null) |
| `query.spellcheck_off` | 布尔值? | 是否禁用了拼写检查 |
| `query.show_strict_warning` | 布尔值? | 如果严格安全搜索隐藏了相关结果则为true |
| `results[]` | 数组 | 图片结果列表 |
| `results[].type` | 字符串 | 始终为`"image_result"` |
| `results[].title` | 字符串? | 图片标题 |
| `results[].url` | 字符串? | 图片所在的页面URL |
| `results[].source` | 字符串? | 源域名 |
| `results[].page_fetched` | 字符串? | 最后一次页面抓取的ISO日期时间 |
| `results[].thumbnail.src` | 字符串? | Brave代理的缩略图URL (~500px宽度) |
| `results[].thumbnail.width` | 整数? | 缩略图宽度 |
| `results[].thumbnail.height` | 整数? | 缩略图高度 |
| `results[].properties.url` | 字符串? | 原始全尺寸图片URL |
| `results[].properties.placeholder` | 字符串? | 低分辨率占位图URL (Brave代理) |
| `results[].properties.width` | 整数? | 原始图片宽度 (可能为null) |
| `results[].properties.height` | 整数? | 原始图片高度 (可能为null) |
| `results[].meta_url.scheme` | 字符串? | URL协议方案 |
| `results[].meta_url.netloc` | 字符串? | 网络位置 |
| `results[].meta_url.hostname` | 字符串? | 小写域名 |
| `results[].meta_url.favicon` | 字符串? | Favicon URL |
| `results[].meta_url.path` | 字符串? | URL路径 |
| `results[].confidence` | 字符串? | 相关性: `low`, `medium`, 或 `high` |
| `extra.might_be_offensive` | 布尔值 | 结果是否可能包含冒犯性内容 |

## 应用场景

- **视觉内容发现**：构建图片库、情绪板或视觉研究工具。使用`count=200`获取全面覆盖。当需要图片特定元数据（尺寸、缩略图）时优先于`web-search`。
- **内容丰富**：为文章或生成内容添加相关图片。使用`country`和`search_lang`定位受众的本地化环境。
- **安全图片获取**：默认`safesearch=strict`确保结果适合家庭。只有两种模式（off/strict）——不像网页/视频/新闻搜索那样提供moderate选项。
- **高容量批量获取**：每条请求最多200张图片（网页为20，视频/新闻为50）。适合批量图片获取或视觉分析管道。

## 注意事项

- **安全搜索**：图片默认为`strict`（比网页搜索更严格）
- **高容量**：每条请求最多返回200个结果
- **缩略图**：为用户隐私代理（500px宽度）。使用`properties.url`获取原始全分辨率图片。
- **尺寸**：`properties.width/height`对某些图片可能缺失
- **占位图**：`properties.placeholder`是低分辨率URL（非内联base64），适用于渐进式加载UX
