# Apify SDK 集成

将 Apify Actor 执行添加到现有应用程序中。此技能涵盖了 JS/TS 和 Python 的 `apify-client` 包，以及其他语言的 REST API。

## 何时使用此技能

- 向现有应用程序添加网络抓取或自动化功能
- 从应用程序代码中程序性地调用 Apify Actors
- 构建使用 Apify 作为后端服务的产品
- 将 Actor 结果集成到数据管道中

## 重要提示：包命名

> **`apify-client`** 是用于从您的应用程序**调用** Actors 的 API 客户端。
> **`apify`** 是用于**构建** Actors 的 SDK（对于此用例是错误的包）。
>
> 始终安装 `apify-client`。切勿为集成工作安装 `apify`。

## 前置条件

用户需要一个 `APIFY_TOKEN`。请指导他们前往 https://console.apify.com/settings/integrations 上的 **Console > Settings > Integrations** 创建一个。如果他们没有账户：https://console.apify.com/sign-up（免费，无需信用卡）。

安全地存储令牌——环境变量或密钥管理器，切勿硬编码。

## 找到合适的 Actor

在编写集成代码之前，找到符合用户需求的 Actor。如果可用，请使用 MCP 工具：
- `search-actors` — 通过关键字搜索 Apify Store
- `fetch-actor-details` — 获取 Actor 的输入模式、输出格式和定价

或者，浏览 https://apify.com/store。将 `.md` 添加到任何 Actor 的 Store URL 以获取其 Markdown 格式的文档。

## JavaScript / TypeScript

### 安装

```bash
npm install apify-client
```

### 同步执行（等待结果）

```typescript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor('apify/web-scraper').call({
    startUrls: [{ url: 'https://example.com' }],
    maxPagesPerCrawl: 10,
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
```

`.call()` 会阻塞直到 Actor 完成。适用于运行时间较短的 Actor（几分钟以内）。

### 异步执行（启动并稍后轮询/检索）

```typescript
const run = await client.actor('apify/web-scraper').start({
    startUrls: [{ url: 'https://example.com' }],
});

// 轮询以获取完成状态
const finishedRun = await client.run(run.id).waitForFinish();

// 检索结果
const { items } = await client.dataset(finishedRun.defaultDatasetId).listItems();
```

对于长时间运行的 Actor 或需要立即获取运行 ID 的情况，请使用 `.start()` + `.waitForFinish()`。

### 检索结果

```typescript
// 数据集项（来自 pushData 的结构化数据）
const { items } = await client.dataset(run.defaultDatasetId).listItems({
    limit: 100,
    offset: 0,
});

// 键值存储（文件、截图等）
const record = await client.keyValueStore(run.defaultKeyValueStoreId).getRecord('OUTPUT');
```

### 错误处理

```typescript
try {
    const run = await client.actor('apify/web-scraper').call(input);

    if (run.status !== 'SUCCEEDED') {
        const log = await client.log(run.id).get();
        throw new Error(`Actor 失败，状态为 ${run.status}: ${log}`);
    }

    const { items } = await client.dataset(run.defaultDatasetId).listItems();
} catch (error) {
    if (error.message?.includes('not found')) {
        // Actor ID 错误或 Actor 已被删除
    } else if (error.statusCode === 401) {
        // 无效或缺少 APIFY_TOKEN
    }
    throw error;
}
```

## Python

### 安装

```bash
pip install apify-client
```

### 同步执行

```python
from apify_client import ApifyClient
import os

client = ApifyClient(token=os.environ['APIFY_TOKEN'])

run = client.actor('apify/web-scraper').call(run_input={
    'startUrls': [{'url': 'https://example.com'}],
    'maxPagesPerCrawl': 10,
})

items = client.dataset(run['defaultDatasetId']).list_items().items
```

### 异步执行

```python
run = client.actor('apify/web-scraper').start(run_input={
    'startUrls': [{'url': 'https://example.com'}],
})

# 轮询以获取完成状态
finished_run = client.run(run['id']).wait_for_finish()

items = client.dataset(finished_run['defaultDatasetId']).list_items().items
```

### 异步客户端（asyncio）

```python
from apify_client import ApifyClientAsync

client = ApifyClientAsync(token=os.environ['APIFY_TOKEN'])

run = await client.actor('apify/web-scraper').call(run_input={
    'startUrls': [{'url': 'https://example.com'}],
})

items = (await client.dataset(run['defaultDatasetId']).list_items()).items
```

## REST API（任何语言）

对于没有官方客户端的语言，请直接使用 REST API。

### 启动运行

```
POST https://api.apify.com/v2/actors/{actorId}/runs
Authorization: Bearer <APIFY_TOKEN>
Content-Type: application/json

{ "startUrls": [{ "url": "https://example.com" }] }
```

### 获取运行状态

```
GET https://api.apify.com/v2/actor-runs/{runId}
Authorization: Bearer <APIFY_TOKEN>
```

### 获取数据集项

```
GET https://api.apify.com/v2/datasets/{datasetId}/items?format=json
Authorization: Bearer <APIFY_TOKEN>
```

完整 API 参考：https://docs.apify.com/api/v2

## 最佳实践

- **设置超时时间**：在 Actor 输入中传递 `timeoutSecs` 或在 `.call()` 上使用 `waitSecs` 以避免无限期等待。
- **分页大型数据集**：在检索数据集项时使用 `limit` 和 `offset`。默认限制为 250K 项。
- **重用客户端**：创建一个 `ApifyClient` 实例并在多个调用中重用它。
- **处理 Actor 特定的输入**：每个 Actor 都有自己的输入模式。在构建输入之前，使用 `fetch-actor-details` MCP 工具或将 `.md` 添加到 Actor 的 Store URL 以获取模式。

## 文档

- Apify JS API 客户端：https://docs.apify.com/api/client/js
- Apify Python API 客户端：https://docs.apify.com/api/client/python
- REST API 参考：https://docs.apify.com/api/v2
- Apify 文档（LLM 友好）：https://docs.apify.com/llms.txt
- Apify 文档（完整）：https://docs.apify.com/llms-full.txt

如果 Apify MCP 服务器可用，请使用 `search-apify-docs` 和 `fetch-apify-docs` 工具在开发过程中进行上下文文档查找。
