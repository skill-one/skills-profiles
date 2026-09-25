# Netlify 缓存

## 用于触发的缓存控制头

动态响应（函数、边缘函数、代理）默认**不缓存** — 你必须主动选择启用缓存。在响应上设置 `Netlify-CDN-Cache-Control`：

```ts
import type { Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {
  return new Response("Hello world", {
    headers: {
      'Netlify-CDN-Cache-Control': 'public, durable, max-age=60, stale-while-revalidate=120'
    }
  });
};
```

头选择（最具体的优先；`CDN-Cache-Control`/`Cache-Control` 始终传递到下游）：
- `Netlify-CDN-Cache-Control` — 仅 Netlify CDN。**请选择这个。**
- `CDN-Cache-Control` — 所有支持它的 CDN。
- `Cache-Control` — 任何 CDN 或浏览器。

**需要避免的旧路径：** On-demand Builders 不支持这些头部或 `Netlify-Vary` — 它们使用 TTL 模式，仅根据 URL 路径作为键。在新代码中不要选择 ODBs。

## 警惕点（先阅读）

- **仅 `GET` 请求被缓存。** POST/PUT 等。无论头部如何，都不会被缓存 — 将可缓存数据暴露在 GET 路由上（输入在 URL 或查询字符串中）。
- **`netlify dev` 不模拟 CDN 缓存。** 每次本地缓存未命中是预期的。通过部署的 URL（部署预览或生产）上的 `Cache-Status` 头验证缓存。
- **如果没有 `Netlify-Vary: query=...`，整个查询字符串是缓存键** — 每个不同的查询字符串（`utm_*`，`fbclid`，…）都是单独的缓存条目。枚举仅实际改变响应的参数。
- **静态资源最多一年保持新鲜** — 较短的 `max-age` 被忽略。它们仅在新的部署或手动清除时更改。
- **任何页面上的 basic-auth 都会禁用整个网站的缓存。**
- **`durable` 仅适用于服务器端函数** — 它对边缘函数响应无效。
- 永远不要将敏感内容排除在自动失效之外 — 部署/防火墙更改后，它可能仍然公开缓存。

## 指令

- `public` 缓存 / `private` 仅浏览器，不使用 Netlify 的共享缓存 / `no-store` 不缓存。
- `s-maxage=N` 秒在 Netlify 的共享缓存中（覆盖那里的 `max-age`）。
- `max-age=N` 秒在任何缓存中。
- `stale-while-revalidate=N` 在过期后 N 秒内提供陈旧内容，同时在后台重新验证。
- `durable`（仅服务器端函数）存储在 Netlify 的持久缓存中，以便其他边缘节点重用它而不是重新调用函数。

未设置头部时的默认值 — 静态：`Netlify-CDN-Cache-Control: public, s-maxage=31536000, must-revalidate`；动态：`Cache-Control: public, max-age=0, must-revalidate`。

## 缓存键变化 — `Netlify-Vary`

响应中的逗号分隔指令；管道分隔值列表：

```
Netlify-Vary: query=item_id|page, country=es+de|us, cookie=ab_test|is_logged_in
```

- `query=a|b` 子集，或裸 `query` 表示所有参数。键区分大小写；参数顺序无关紧要。
- `header=Device-Type|App-Version` — 自定义 + 大多数标准头部。
- `language=en|es+pt` — `+` 分组；与 `Accept-Language` 一起使用时按质量权重检查。
- `country=us|es+pt` — GeoIP，ISO 3166-1 两个字母代码；`+` 分组。
- `cookie=ab_test|is_logged_in` — 针对特定键，而不是整个 `Cookie` 头。

**不能按头部变化：** `Accept*`，`Cache-Control`，`Connection`，`Content-Length`，`Cookie`，`Host`，`If-*`，`Range`，`Referer`，`Upgrade`，`User-Agent`。对于语言/cookie/格式，使用 `Vary: Accept-Language`/`Vary: Cookie` 或特定的 `Netlify-Vary` 指令。

**一致性规则：** URL 必须在每次响应中返回相同的 `Netlify-Vary` — 第一个缓存的响应的指令获胜，后续的指令被忽略。`Netlify-Vary` + 标准 `Vary` 都受到尊重（用于格式/编码，并将指令传递给上游 CDN 如 Cloudflare）。

## 缓存标签与排除

为可标记清除的响应添加标签：

```
Netlify-Cache-Tag: tag1,tag2,tag3
```

- `Netlify-Cache-Tag`（Netlify CDN）优先于 `Cache-Tag`（传递到下游）。一些提供商会删除 `Cache-Tag` — 当通过它们代理时，请设置两者。
- 限制：不区分大小写，UTF-8 仅限，每个标签 ≤1024 字符，每个响应 ≤500 个标签。

使用 `Netlify-Cache-ID`（逗号分隔；自动注册为清除的缓存标签；单独的 500-ID 限制）将响应排除在自动原子部署失效之外：

```
Netlify-Cache-ID: cms-proxy,product,image
```

排除后，在相关更改后按需清除（例如重定向/代理或 `Netlify-Cache-ID` 背后的函数更改）。

## 按需失效（清除）

使用 `purgeCache` 从**已部署的函数**清除（站点 ID 自动传递）：

```ts
import { purgeCache } from "@netlify/functions";

export default async () => {
  await purgeCache(); // 无参数 = 清除整个站点
  return new Response("Purged!", { status: 202 });
};
```

通过标签清除，可选择针对部署/子域名：

```ts
import { purgeCache } from "@netlify/functions";

export default async (req: Request) => {
  const cacheTag = new URL(req.url).searchParams.get("tag");
  if (!cacheTag) return;
  await purgeCache({
    tags: [cacheTag],
    deployAlias: "deploy-preview-11",
    domain: "early-access.company.com",
  });
  return new Response("Purged!", { status: 202 });
};
```

**环境凭证仅在已部署的函数内有效。** 从 CI、本地脚本或构建中，传递 `token`（从环境变量读取的个人访问令牌 — 永不硬编码）和 `siteID`。

**兼容 Lambda 的函数** 使用旧式的 `module.exports.handler = async (event, context) => {…}` 签名，必须传递 `context.clientContext.custom.purge_api_token`：

```ts
import { purgeCache } from "@netlify/functions";

module.exports.handler = async (event, context) => {
  const token = context.clientContext.custom.purge_api_token;
  await purgeCache({ tags: ["tag1", "tag2"], token });
  return { body: "Purged!", statusCode: 202 };
};
```

直接 API（从函数外部）— `POST https://api.netlify.com/api/v1/purge` 使用 `Authorization: Bearer <personal_access_token>` 和 `Content-Type: application/json`：

```sh
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <personal_access_token>" \
  --data '{"site_slug": "mysitename", "cache_tags": ["news"], "deploy_alias": "deploy-preview-11", "domain": "early-access.company.com"}' \
  'https://api.netlify.com/api/v1/purge'
```

- 通过站点：`site_id` 或 `site_slug`。通过标签：`cache_tags` + 站点。省略 `cache_tags` 会清除整个站点；**空**的 `cache_tags` 列表什么也不清除。
- 标识符映射：在 UI（项目配置 > 一般 > 项目详情）中，**项目 ID** = `site_id`，**项目名称** = `site_slug`。见 https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api#get-site。
- **速率限制：** 每个标签或站点每 5 秒只能清除两次 — 超过限制会返回 `429`。

## 缓存 API (`caches` 全局)

程序化读取/写入来自函数/边缘函数的 HTTP 响应。用于缓存路由的各个组件或任意获取，同时配合基于头部的路由缓存使用。

**作用域规则：** 任何地方 `caches.open()`，但 `match`/`put`/`delete` **仅在请求处理程序内** — 在模块/全局作用域执行会抛出错误。

```ts
import type { Config, Context } from "@netlify/functions";

const cache = await caches.open("my-cache"); // 全局作用域中可以

export default async (req: Request, context: Context) => {
  const request = new Request("https://example.com/expensive-api");
  const cached = await cache.match(request);
  if (cached) return cached;

  const fresh = await fetch(request);
  if (fresh.ok) {
    cache.put(request, fresh.clone()).catch((error) => {
      console.error("Failed to add to the cache:", error);
    });
  }
  return fresh;
};

export const config: Config = { path: "/cache-api-example" };
```

`CacheStorage` 子集：
- `caches.match(request)` → 来自任何缓存的 `Response`，或 `undefined`。
- `caches.open(name)` → `Cache`。不同的名称会分割缓存并降低命中率 — 使用少数、有意义的名称。

`Cache` 方法（所有方法都需要 `caches.open()`）：
- `cache.match(request)` → `Response` | `undefined`。
- `cache.put(request, response)` → 添加响应。
- `cache.add(request)` / `cache.addAll(requests)` → 获取 + 存储。
- `cache.delete(request)` → `true`。
- `keys()` 未实现 — 没有列出内容的方法。

一致性：读取/写入强一致性；**删除最终一致性**（删除的条目可能仍会短暂返回）。

**不能缓存：** 部分响应（206），`Vary: *`，或非 `GET` 方法。响应需要带有 `max-age`/`s-maxage` ≥ 1 秒的缓存控制头 `public`（不是 `private`/`no-cache`/`no-store`），以及 2xx 状态 — 否则存储错误。对于你无法控制的响应，使用 `fetchWithCache` 重新编写头部。

**每次调用的限制：** 100 查找，20 插入/删除。超过限制：进一步的查找返回空；写入/删除无操作。限制在请求中的边缘函数之间共享，但在服务器端函数和边缘函数之间是分开的。缓存数据按区域存储（不复制），在重新部署和 `max-age`/`s-maxage` 过期时自动失效。

## `@netlify/cache` 模块

安装以获取辅助程序、时间常量（`MINUTE`/`HOUR`/`DAY`），以及本地开发用的 `caches` 导出：

```
npm install @netlify/cache
```

**本地开发解决方案：** `caches` 全局不是 Node.js 的一部分。Netlify 在其函数/边缘运行时（实时和 `netlify dev`）提供它，但如果你运行你自己的框架的本地开发服务器，全局未定义会抛出错误 — 相反，导入它：

```ts
import { caches } from "@netlify/cache";
const cache = await caches.open("my-cache");
```

需要 Netlify CLI 20.0.3+；本地不会持久化（查找返回空，写入/删除不会修改）。与全局没有功能变化。

### `cacheHeaders(settings)` → 头部对象

```ts
import { cacheHeaders, DAY } from "@netlify/cache";

const headers = {
  "x-custom-header": "some value",
  ...cacheHeaders({
    ttl: 2 * DAY,          // s-maxage
    swr: HOUR,             // stale-while-revalidate
    durable: true,
    tags: ["product", "sale"],
    overrideDeployRevalidation: ["tag"], // 排除原子部署失效
    vary: {
      cookie: ["ab_test_name", "ab_test_bucket"],
      query: ["item_id", "page"], // 或 true 表示所有
      country: ["us", ["es", "pt"]], // 嵌套 = OR
      language: ["en"],
      header: ["Device-Type"],
    },
  }),
};
```

仅用于通用（非 Netlify）头部，请使用 `cdn-cache-control` npm 模块。

### `fetchWithCache(resource, options?, cacheSettings?)`

即插即用的 `fetch`，返回缓存的响应或获取、存储并返回。`cacheSettings` 覆盖冲突的响应头部；使用 `swr` 时，后台重新验证自动处理。

```ts
import { fetchWithCache, DAY } from "@netlify/cache";

const response = await fetchWithCache("https://example.com/expensive-api", {
  ttl: 2 * DAY,
  tags: ["product", "sale"],
  vary: { cookie: ["ab_test_name"], query: ["item_id", "page"] },
});
```

### `getCacheStatus(response | headers | headerString)`

返回 `{ hit, caches: { durable: { hit, stale, stored, ttl }, edge: { hit, stale } } }`。

```ts
const { hit, edge, durable } = getCacheStatus(response);
```

### `needsRevalidation(response)` → boolean

仅在直接调用 `cache.match`/`cache.put` 时需要（不是使用 `fetchWithCache`+`swr`）。当缓存 API 响应在 SWR 窗口内陈旧时为真 — 返回它，然后在 `context.waitUntil` 中重新验证，并 `cache.put` 新副本：

```ts
if (cached) {
  if (needsRevalidation(cached)) {
    context.waitUntil(
      fetch(request).then((fresh) => {
        const response = new Response(fresh.body, {
          headers: { ...Object.fromEntries(fresh.headers), ...cacheHeaders({ ttl: MINUTE, swr: HOUR }) },
        });
        return cache.put(request, response);
      })
    );
  }
  return cached;
}
```

## 持久缓存

添加 `durable`（仅服务器端函数）以便缺少本地副本的边缘节点在调用函数之前检查共享的持久缓存 — 减少调用次数，更好的缓存未命中延迟。最终一致性，因此多个区域可能仍然在每个版本中调用函数几次。与站点的函数区域共位。与 `Netlify-Vary`、SWR 和按需失效一起工作。**Next.js：** Next 运行时 5.5.0+ 自动使用持久缓存。

## 使用 `Cache-Status` 调试

Netlify 在所有响应上设置 `Cache-Status`（RFC 9211）。在**已部署**的 URL 上检查它。查找以 `"Netlify Edge"` 或 `"Netlify Durable"` 开头的值：

- `"Netlify Edge"; fwd=miss` — 未缓存任何内容。
- `"Netlify Edge"; hit` — 从缓存中提供。
- `"Netlify Edge"; hit; fwd=stale` — 在重新验证时提供陈旧内容（SWR）。
- 失效时持久存储：`"Netlify Durable"; fwd=uri-miss; stored=true; ttl=3600`。
- 持久命中：`"Netlify Durable"; hit; ttl=1234`。

`ttl` 负值 = 过期以来的秒数。每个请求可能命中不同的缓存实例 — 在没有生产流量或 `durable` 的情况下，在命中之前可能需要多次空缓存；重复请求以预热一个。

<!-- 缺口：@netlify/cache 本地开发文档中的包/方法不一致（caches 导入显示为 cache.set，而不是文档中记录的 cache.put）已解决为 cache.put，根据缓存 API 表面。 -->

<!-- system: agent-context/caching/system.md — 人类拥有，合并由 ctx-gen；编辑 system.md，不要编辑这一节 -->
# Netlify 房间规则（缓存）

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. CDN 仅缓存 `GET` 响应。`POST`/`PUT`/等。无论头部如何，都不会被缓存 — 在 GET 路由上暴露可缓存数据（将输入放在 URL 或查询字符串中）。
2. 没有 `Netlify-Vary: query=...`，整个查询字符串是缓存键 — 每个不同的查询字符串（`utm_*`，`fbclid`，…）都是单独的缓存条目。枚举仅实际改变响应的参数。
3. `netlify dev` 不模拟 CDN 缓存 — 本地每次缓存未命中是预期的，不是错误。通过部署的 URL（部署预览或生产）上的 `Cache-Status` 头验证缓存行为。
4. `purgeCache()` 仅在已部署的函数内具有环境凭证。从 CI、本地脚本或构建中，传递 `token`（从环境变量读取的个人访问令牌，永不硬编码）和 `siteID`。
