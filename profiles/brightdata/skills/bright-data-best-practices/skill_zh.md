# CLI安装参考

Bright Data CLI (`bdata`) 的安装、认证和故障排除都在一个权威的地方进行了说明：

→ [`references/cli-setup.md`](references/cli-setup.md)

在执行任何调用 `bdata` 的任务之前，请查阅它。

# Bright Data API

Bright Data 提供用于大规模网络数据提取的基础设施。四个主要 API 覆盖不同的用例——始终为工作选择最具体的工具。

## 选择正确的 API

| 用例 | API | 原因 |
|------|-----|-----|
| 通过 URL 抓取任何网页（无交互） | Web Unlocker | 基于HTTP，自动绕过机器人检测，最便宜 |
| Google / Bing / Yandex 搜索结果 | SERP API | 专门用于SERP提取，返回结构化数据 |
| 来自 Amazon、LinkedIn、Instagram、TikTok 等的结构化数据 | Web Scraper API | 预构建的抓取器，无需解析 |
| 点击、滚动、填写表单、运行JS、拦截XHR | 浏览器API | 全浏览器自动化 |
| Puppeteer / Playwright / Selenium 自动化 | 浏览器API | 通过CDP/WebDriver连接 |
| 将您自己的HTTP客户端通过原始代理（数据中心/ISP/住宅/移动）路由 | 代理网络 | 当您需要直接代理访问而不是管理API时，使用自己的请求逻辑——请参阅 `proxy.md` 技能 |

## 认证模式（所有API）

所有API共享相同的认证模型。以下环境变量适用于直接REST API集成——如果您使用 `bdata` CLI，`bdata login` 会自动处理所有这些（请参阅 [`references/cli-setup.md`](references/cli-setup.md)）。

```bash
export BRIGHTDATA_API_KEY="your-api-key"         # 从控制面板 > 账户设置获取
export BRIGHTDATA_UNLOCKER_ZONE="zone-name"       # Web Unlocker区域名称
export BRIGHTDATA_SERP_ZONE="serp-zone-name"      # SERP API区域名称
export BROWSER_AUTH="brd-customer-ID-zone-NAME:PASSWORD"  # 浏览器API凭证
```

Web Unlocker 和 SERP API 的 REST API 认证标头：
```
Authorization: Bearer YOUR_API_KEY
```

---

## Web Unlocker API

基于HTTP的抓取代理。最适合简单的页面获取，无需浏览器交互。

**端点:** `POST https://api.brightdata.com/request`

```python
import requests

response = requests.post(
    "https://api.brightdata.com/request",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "zone": "YOUR_ZONE_NAME",
        "url": "https://example.com/product/123",
        "format": "raw"
    }
)
html = response.text
```

### 关键参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `zone` | string | 区域名称（必需） |
| `url` | string | 目标URL，包含 `http://` 或 `https://`（必需） |
| `format` | string | `"raw"`（HTML）或 `"json"`（结构化包装器）（必需） |
| `method` | string | HTTP动词，默认 `"GET"` |
| `country` | string | 2字母ISO代码用于地理定位（例如，`"us"`，`"de"`） |
| `data_format` | string | 转换：`"markdown"` 或 `"screenshot"` |
| `async` | boolean | `true` 用于异步模式 |

### 快速模式

```python
# 获取markdown（最佳用于LLM输入）
response = requests.post(
    "https://api.brightdata.com/request",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"zone": ZONE, "url": url, "format": "raw", "data_format": "markdown"}
)

# 地理定位请求
json={"zone": ZONE, "url": url, "format": "raw", "country": "de"}

# 调试用截图
json={"zone": ZONE, "url": url, "format": "raw", "data_format": "screenshot"}

# 异步用于批量处理
json={"zone": ZONE, "url": url, "format": "raw", "async": True}
```

**关键规则:** 不要将 Web Unlocker 与 Puppeteer、Playwright、Selenium 或反检测浏览器一起使用。使用浏览器API。

请参阅 **[references/web-unlocker.md](references/web-unlocker.md)** 获取完整参考，包括代理接口、特殊标头、异步流程、功能、计费和反模式。

---

## SERP API

结构化搜索引擎结果提取，用于 Google、Bing、Yandex、DuckDuckGo。

**端点:** `POST https://api.brightdata.com/request`（与 Web Unlocker 相同）

```python
response = requests.post(
    "https://api.brightdata.com/request",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "zone": "YOUR_SERP_ZONE",
        "url": "https://www.google.com/search?q=python+web+scraping&brd_json=1&gl=us&hl=en",
        "format": "raw"
    }
)
data = response.json()
for result in data.get("organic", []):
    print(result["rank"], result["title"], result["link"])
```

### 必要的 Google URL 参数

| 参数 | 描述 | 示例 |
|-----------|-------------|---------|
| `q` | 搜索查询 | `q=python+web+scraping` |
| `brd_json` | 解析的JSON输出 | `brd_json=1`（始终用于数据管道） |
| `gl` | 搜索国家 | `gl=us` |
| `hl` | 语言 | `hl=en` |
| `start` | 分页偏移量 | `start=10`（第2页），`start=20`（第3页） |
| `tbm` | 搜索类型 | `tbm=nws`（新闻），`tbm=isch`（图像），`tbm=vid`（视频） |
| `brd_mobile` | 设备 | `brd_mobile=1`（移动），`brd_mobile=ios` |
| `brd_browser` | 浏览器 | `brd_browser=chrome` |
| `brd_ai_overview` | 触发AI概述 | `brd_ai_overview=2` |
| `uule` | 编码的地理位置 | 用于精确位置定位 |

**注意:** `num` 参数自2025年9月起已**弃用**。使用 `start` 进行分页。

### 解析的JSON响应结构

```json
{
  "organic": [{"rank": 1, "global_rank": 1, "title": "...", "link": "...", "description": "..."}],
  "paid": [],
  "people_also_ask": [],
  "knowledge_graph": {},
  "related_searches": [],
  "general": {"results_cnt": 1240000000, "query": "..."}
}
```

### Bing 关键参数

| 参数 | 描述 |
|-----------|-------------|
| `q` | 搜索查询 |
| `setLang` | 语言（优先使用4字母：`en-US`) |
| `cc` | 国家代码 |
| `first` | 分页（递增10：1, 11, 21...) |
| `safesearch` | `off`，`moderate`，`strict` |
| `brd_mobile` | 设备类型 |

### 异步用于批量 SERP

```python
# 提交
response = requests.post(
    "https://api.brightdata.com/request",
    params={"async": "1"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"zone": SERP_ZONE, "url": "https://www.google.com/search?q=test&brd_json=1", "format": "raw"}
)
response_id = response.headers.get("x-response-id")

# 获取（获取调用不收费）
result = requests.get(
    "https://api.brightdata.com/serp/get_result",
    params={"response_id": response_id},
    headers={"Authorization": f"Bearer {API_KEY}"}
)
```

**计费:** 仅按1,000个成功请求付费。异步获取调用不收费。

请参阅 **[references/serp-api.md](references/serp-api.md)** 获取完整参考，包括地图、趋势、评论、镜头、酒店、航班参数。

---

## Web Scraper API

100多个平台的预构建抓取器，用于结构化数据提取，无需解析逻辑。

**同步端点:** `POST https://api.brightdata.com/datasets/v3/scrape`
**异步端点:** `POST https://api.brightdata.com/datasets/v3/trigger`

```python
# 同步（最多20个URL，立即返回）
response = requests.post(
    "https://api.brightdata.com/datasets/v3/scrape",
    params={"dataset_id": "YOUR_DATASET_ID", "format": "json"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"input": [{"url": "https://www.amazon.com/dp/B09X7M8TBQ"}]}
)

if response.status_code == 200:
    data = response.json()  # 结果已准备好
elif response.status_code == 202:
    snapshot_id = response.json()["snapshot_id"]  # 等待完成
```

### 参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `dataset_id` | string | 抓取器标识符来自抓取器库（必需） |
| `format` | string | `json`（默认），`ndjson`，`jsonl`，`csv` |
| `custom_output_fields` | string | 管道分隔字段：`url\|title\|price` |
| `include_errors` | boolean | 在结果中包含错误信息 |

### 请求正文

```json
{
  "input": [
    { "url": "https://www.amazon.com/dp/B09X7M8TBQ" },
    { "url": "https://www.amazon.com/dp/B0B7CTCPKN" }
  ]
}
```

### 异步结果轮询

```python
import time

# 触发
snapshot_id = requests.post(
    "https://api.brightdata.com/datasets/v3/trigger",
    params={"dataset_id": DATASET_ID, "format": "json"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"input": [{"url": u} for u in urls]}
).json()["snapshot_id"]

# 轮询
while True:
    status = requests.get(
        f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()["status"]

    if status == "ready": break
    if status == "failed": raise Exception("任务失败")
    time.sleep(10)

# 下载
data = requests.get(
    f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}",
    params={"format": "json"},
    headers={"Authorization": f"Bearer {API_KEY}"}
).json()
```

**进度状态值:** `starting` → `running` → `ready` | `failed`
**数据保留:** 30天。
**计费:** 按交付记录付费。无效输入URL失败仍会计费。

请参阅 **[references/web-scraper-api.md](references/web-scraper-api.md)** 获取完整参考，包括抓取器类型、输出格式、交付选项和计费详情。

---

## 浏览器API（抓取浏览器）

通过CDP/WebDriver进行全浏览器自动化。自动处理CAPTCHA、指纹识别和反机器人检测。

**连接:**
- Playwright/Puppeteer: `wss://${AUTH}@brd.superproxy.io:9222`
- Selenium: `https://${AUTH}@brd.superproxy.io:9515`

```javascript
const { chromium } = require("playwright-core");

const AUTH = process.env.BROWSER_AUTH;
const browser = await chromium.connectOverCDP(`wss://${AUTH}@brd.superproxy.io:9222`);
const page = await browser.newPage();
page.setDefaultNavigationTimeout(120000); // 始终设置为2分钟

await page.goto("https://example.com", { waitUntil: "domcontentloaded" });
const html = await page.content();
await browser.close();
```

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(f"wss://{AUTH}@brd.superproxy.io:9222")
    page = await browser.new_page()
    page.set_default_navigation_timeout(120000)
    await page.goto("https://example.com", wait_until="domcontentloaded")
    html = await page.content()
    await browser.close()
```

### 自定义CDP函数

| 函数 | 目的 |
|----------|---------|
| `Captcha.solve` | 手动触发CAPTCHA解决 |
| `Captcha.setAutoSolve` | 启用/禁用自动CAPTCHA解决 |
| `Proxy.setLocation` | 设置精确地理位置（在goto之前调用） |
| `Proxy.useSession` | 在会话中保持相同IP |
| `Emulation.setDevice` | 应用设备配置（iPhone 14等） |
| `Emulation.getSupportedDevices` | 列出可用设备配置 |
| `Unblocker.enableAdBlock` | 阻止广告以节省带宽 |
| `Unblocker.disableAdBlock` | 重新启用广告 |
| `Input.type` | 快速文本输入用于批量表单填写 |
| `Browser.addCertificate` | 为会话安装客户端SSL证书 |
| `Page.inspect` | 获取DevTools调试URL用于实时会话 |

```javascript
// 自定义函数的CDP会话模式
const client = await page.target().createCDPSession();

// 带超时的CAPTCHA解决
const result = await client.send("Captcha.solve", { timeout: 30000 });

// 精确地理位置（必须在goto之前）
await client.send("Proxy.setLocation", {
  latitude: 37.7749,
  longitude: -122.4194,
  distance: 10,
  strict: true
});

// 阻止不必要的资源
await client.send("Network.setBlockedURLs", { urls: ["*google-analytics*", "*.ads.*"] });

// 设备模拟
await client.send("Emulation.setDevice", { deviceName: "iPhone 14" });
```

### 会话规则
- **每个会话一次初始导航**——新URL = 新会话
- **空闲超时:** 5分钟
- **最大持续时间:** 30分钟

### 地理位置信息
- 国家级：在凭证用户名中追加 `-country-us`
- 欧盟范围：追加 `-country-eu`（通过29+欧洲国家路由）
- 精确：使用 `Proxy.setLocation` CDP命令（在导航之前）

### 错误代码

| 代码 | 问题 | 解决方法 |
|------|-------|-----|
| `407` | 错误端口 | Playwright/Puppeteer → `9222`，Selenium → `9515` |
| `403` | 认证错误 | 检查凭证格式和区域类型 |
| `503` | 服务扩展 | 等待1分钟，重新连接 |

**计费:** 仅基于流量计费。阻止图像/CSS/字体以降低成本。

请参阅 **[references/browser-api.md](references/browser-api.md)** 获取完整参考，包括所有CDP函数、带宽优化、CAPTCHA模式、调试和错误代码。

---

## 详细参考

- **[references/web-unlocker.md](references/web-unlocker.md)** — Web Unlocker：完整参数列表、代理接口、特殊标头、异步流程、功能、计费、反模式
- **[references/serp-api.md](references/serp-api.md)** — SERP API：所有Google参数（地图、趋势、评论、镜头、酒店、航班）、Bing参数、解析的JSON结构、异步、计费
- **[references/web-scraper-api.md](references/web-scraper-api.md)** — Web Scraper API：同步与异步、所有参数、轮询、抓取器类型、输出格式、计费
- **[references/browser-api.md](references/browser-api.md)** — 浏览器API：连接字符串、会话规则、所有CDP函数、地理定位、带宽优化、CAPTCHA、调试、错误代码

## 相关技能

- **`brightdata-proxy`** — 用于通过 Bright Data 的原始代理网络（数据中心、ISP、住宅、移动）路由请求，而不是使用管理API。涵盖网络/IP池选择、`brd-customer-...` 用户名格式、定位和粘性会话参数、住宅/移动的SSL CA设置，以及cURL、Python（requests/httpx/aiohttp/Scrapy）、Node（fetch/axios）、Playwright、Puppeteer 和 Selenium 的集成。当任务是需要原始代理访问而不是 Web Unlocker / SERP / Web Scraper / Browser API 时，请将其传递给它。当代理遇到一致阻止时，升级顺序：原始代理 → Web Unlocker → 浏览器API → Web Scraper API。
