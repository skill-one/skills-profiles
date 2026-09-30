---
name: netlify-blobs
description: 使用 @netlify/blobs 模块在 Netlify 上存储和检索非结构化对象、文件以及类似缓存的状体。适用于持久化用户文件上传（图像/文档）、缓存函数或 Background Functions 的计算输出、提供可下载资源、按 ID 键存储 JSON 对象，或为部署特定数据提供种子。适用于从函数、Edge Functions 或 Build 插件进行键/值或对象存储——不适用于按用户、事务性或关系型数据（请使用 Netlify DB）。触发场景包括“保存上传文件”、“缓存 API 结果”、“存储生成站点地图”、“函数的键/值存储”或“无需数据库的文件上传”。
---

# Netlify Blobs

现代语法 — 从 `@netlify/blobs` 导入并打开一个商店，然后在该句柄上调用方法：

```ts
import { getStore, getDeployStore, listStores } from "@netlify/blobs";
import type { Context } from "@netlify/functions"; // 或 "@netlify/edge-functions"
```

在函数、边缘函数和构建插件中，`siteID`、`deployID`、`token`（以及 `region` 用于 `getDeployStore`）会自动注入。使用 `npm install @netlify/blobs` 安装。

**这不是一个数据库。** 对于动态、按用户、事务性或关系型数据，请使用 Netlify DB。Blobs 用于对象、文件和类似缓存的状体，针对频繁读取和较少写入进行了优化。

**商店范围是一个陷阱枪 — 首先阅读此内容。** `getStore` 打开一个**全局商店，跨所有部署上下文共享**：部署预览上的代码会读取、覆盖并删除生产数据。切勿从预览中运行破坏性测试或播种一次性数据到全局商店。使用 `getDeployStore()` 或上下文特定的商店名称以实现隔离。

## 选择商店类型

- `getStore(name)` — 全局，跨所有部署共享。数据在部署之间持久化；预览会看到生产数据。
- `getDeployStore(name)` — 部署特定，仅限于一个部署。在回滚时同步，在部署删除时清理。用于隔离，以及任何失败部署不应破坏的内容。
- **构建插件可以读取站点任何商店的数据，但仅写入部署特定商店** (`getDeployStore`)。文件上传也仅写入部署特定商店。

## 核心写入和读取

```ts
const uploads = getStore("file-uploads");

// set: 值是 ArrayBuffer | Blob | string
await uploads.set(key, file, { metadata: { country: "Spain" } });

// setJSON: 任何 JSON 可序列化值
await uploads.setJSON(key, { hello: "world" });

// get: 返回值或 null。类型：text（默认） | json | arrayBuffer | blob | stream
const entry = await uploads.get(key);            // string
const obj = await uploads.get(key, { type: "json" });
if (entry === null) { /* 404 */ }
```

`set`/`setJSON` 会覆盖现有键。两者都返回 `{ modified, etag }` (`etag` 在未生成新条目时会被省略）。

### 持久化用户上传（函数）

```ts
import { getStore } from "@netlify/blobs";
import type { Context } from "@netlify/functions";
import { v4 as uuid } from "uuid";

export default async (req: Request, context: Context) => {
  const form = await req.formData();
  const file = form.get("file") as File;
  const key = uuid();
  const uploads = getStore("file-uploads");
  await uploads.set(key, file, { metadata: { country: context.geo.country.name } });
  return new Response("Submission saved");
};
```

边缘函数除了 `import type { Context } from "@netlify/edge-functions";` 外完全相同。

### 读取（函数）

```ts
export default async (req: Request, context: Context) => {
  const { key } = context.params;
  const uploads = getStore("file-uploads");
  const entry = await uploads.get(key);
  if (entry === null) return new Response(`Not found: ${key}`, { status: 404 });
  return new Response(entry);
};
```

## 元数据和条件读取

```ts
// getWithMetadata: 数据 + 元数据 + etag；支持条件读取
const { data, etag, metadata } = await uploads.getWithMetadata(key);

// getMetadata: 仅返回元数据 + etag，不下载 blob
const meta = await uploads.getMetadata(key); // { etag, metadata } 或 null
```

两者在键不存在时都返回 `null`。两者都接受 `{ consistency, etag, type }`。

**条件读取：** 传递缓存的 `etag`；如果它仍然与服务器端匹配，`data` 为 `null`（你的副本仍然新鲜）。比较整个 ETag 值，包括周围的引号和任何弱前缀。

```ts
const { data, etag } = await uploads.getWithMetadata("my-key", { etag: cachedETag });
if (etag === cachedETag) {
  // data is null — cached copy still fresh
}
```

## 并发：原子条件写入

**最后写入者胜出 — 没有并发控制。** 请勿在 blob 键上构建计数器、余额或读取-修改-写入逻辑，即使使用 `onlyIfMatch` 重试 — 那是事务性数据；请使用 Netlify DB。

`set`/`setJSON` 接受 `{ onlyIfNew, onlyIfMatch }`：

```ts
// 仅当键不存在时创建
const { modified } = await emails.set("jane@netlify.com", "Jane Doe", { onlyIfNew: true });
if (!modified) return new Response("Email already exists", { status: 400 });

// 仅当 ETag 仍然匹配时更新
const { modified } = await emails.set("jane@netlify.com", "New Jane", { onlyIfMatch: etag });
if (!modified) return new Response("Cached data is stale", { status: 400 });
```

## 列出

```ts
const { blobs } = await uploads.list(); // blobs: [{ etag, key }]
```

`list({ directories, paginate, prefix })`。使用 `/` 按层次结构分组键：

```ts
const { blobs, directories } = await animals.list({ directories: true });
// directories: ["cats", "dogs"]; blobs: 仅顶级键

// 深入挖掘 — 带尾随斜杠是必需的（否则 "catsuit" 也会匹配）
const res = await animals.list({ directories: true, prefix: "cats/" });
```

分页：`list` 默认返回所有页面（最多 1,000 条条目）。设置 `paginate: true` 以获取 `AsyncIterator`：

```ts
for await (const page of store.list({ paginate: true })) {
  console.log(page.blobs);
}
```

`listStores({ paginate })` 返回 `{ stores: string[] }` — **不包括部署特定商店**（最多 1,000 条）。

## 删除

```ts
await uploads.delete(key);                        // resolves undefined
const { deletedBlobs } = await uploads.deleteAll(); // 删除所有对象 = 删除商店
```

## 过期（没有服务器端 TTL）

Blobs 不会自动过期。在元数据中存储过期时间戳，在读取时检查它，并在过期时 `delete`：

```ts
await uploads.set(key, body, { metadata: { expiration: new Date("2025-01-01").getTime() } });
const entry = await uploads.getWithMetadata(key);
const { expiration } = entry.metadata;
if (expiration && expiration < Date.now()) await uploads.delete(key);
```

## 一致性

默认为**最终一致性**：写入会立即全局可用，但更新/删除会在 60 秒内向所有边缘位置传播。按商店或按读取选择**强一致性**：

```ts
const store = getStore({ name: "animals", consistency: "strong" }); // 整个商店
await store.get("dog", { consistency: "strong" });                  // 单个读取
```

Netlify CLI 总是使用强一致性。

## 区域

`region` 接收一个**AWS 区域代码**（不是函数机场代码）。支持（任何其他值会在请求前抛出 `InvalidBlobsRegionError`）：`ap-southeast-1`、`ap-southeast-2`、`eu-central-1`、`us-east-1`、`us-east-2`。

- **部署特定商店** 默认为你的函数区域（自动注入）。
- **全局商店** 默认为 `us-east-2`，并且**不跟随**你的函数区域。

**陷阱枪 — 全局区域是按调用**：如果你需要在特定区域中有一个全局商店，请为该商店的**每个 `getStore` 调用传递 `region`**（读取、写入、删除）。省略它的调用使用 `us-east-2` 并静默看不到数据 — 没有错误或警告。

**陷阱枪 — 更改区域不会移动数据**：在新区域中商店看起来为空，而数据仍然保留在旧区域。要迁移，请将每个条目复制到在新区域中打开的商店，然后从旧区域删除。

```ts
const uploads = getDeployStore({ name: "file-uploads", region: "ap-southeast-2" });
const profiles = getStore({ name: "user-profiles", region: "eu-central-1" });
```

## 基于文件的上传（没有构建插件）

将文件放置在基本目录下的 `.netlify/blobs/deploy/` 中；Netlify 会将它们上传（保留目录结构）到**部署特定商店**。使用同名的兄弟 JSON 文件 `$<filename>.json` 添加元数据（必须为有效的 JSON，否则部署会失败）。

```
.netlify/blobs/deploy/
├─ dogs/good-boy.jpg
├─ dogs/$good-boy.jpg.json   # good-boy.jpg 的元数据
├─ cat.jpg
└─ mouse.jpg
```

**注意：** Netlify 在每次构建前都会清空 `.netlify/blobs/deploy/`。提交到你的仓库的文件**不会**上传 — 在构建期间创建 blob 文件（构建命令或构建插件）。

## 访问控制（默认为私有）

Blobs 没有内置的访问控制 — 服务函数是门。Blobs 只能通过你自己的站点代码访问，存储在传输中和静态时加密。如有疑问，默认为私有：在经过身份验证的函数后面门控读取，而不是公开暴露 blobs。不要为敏感数据服务任意用户提供的键；使用调用者无法篡改的内容对键进行作用域化。Blobs 不是 Netlify 的 HIPAA 合规方案的一部分。

## 限制

- 商店名称：不能包含 `/` 或 `:`，最大 64 字节。
- 键：非空，不能以 `/` 开头，最大 600 字节，任何 Unicode（某些字符 >1 字节）。
- 对象大小最大 5 GB；元数据最大 2 KB。
- 使用 Go 编写的函数**无法**访问 Netlify Blobs。
- 需要 Fetch API（Node.js 18+）；否则传递自定义的 `fetch`：`getStore({ fetch, name: "file-uploads" })`。
- 本地开发（Netlify Dev）使用沙盒化的本地商店：没有基于文件的上传，无法读取生产数据。
- 基于文件的上传需要持续部署或 CLI 部署。

## 操作失败时

显示错误并读取函数日志。不要发明 REST 端点或侧信道 API 来重试。

## CLI 和 UI

`netlify blobs:list/get/set/delete` 存在用于检查 — 查看CLI命令参考 [https://cli.netlify.com/commands/blobs/](https://cli.netlify.com/commands/blobs/)。在 UI 中浏览和下载，位于**数据 & 存储 > Blobs**。

## 模块版本迁移

如果你使用 `@netlify/blobs` 6.5.0 或更早版本写入全局商店，升级后这些商店将由于命名空间更改而无法访问。使用最新 CLI 迁移，然后使用模块 7.0.0+：

```sh
netlify recipes blobs-migrate YOUR_STORE_NAME
```

## 参考

完整 API 和背景：[Netlify Blobs 文档](https://docs.netlify.com/build/data-and-storage/netlify-blobs/) 和 [数据 & 存储概述](https://docs.netlify.com/build/data-and-storage/overview/)。

<!-- system: agent-context/blobs/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 规则（blobs）

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. Blobs 不是一个数据库。对于动态、按用户或事务性数据，请使用 Netlify DB — Blobs 用于对象、文件和类似缓存的状体。
2. 当商店操作失败时，显示错误并读取函数日志 — 不要发明 REST 端点或侧信道 API 来重试。
3. `netlify blobs:list/get/set/delete` 存在用于检查；CLI 参考是它们的真实来源 — 链接，不要重述。
4. Blobs 没有内置的访问控制 — 服务函数是门。如有疑问，默认为私有：在经过身份验证的函数后面门控读取，而不是公开暴露 blobs。
5. 全局商店跨所有部署上下文共享 — 部署预览上的代码会读取、覆盖并删除生产数据。切勿从预览中运行破坏性测试或播种一次性数据；使用 `getDeployStore()` 或上下文特定的商店名称以实现隔离。
6. 不要在 blob 键上构建计数器、余额或读取-修改-写入逻辑 — 即使使用 `onlyIfMatch` 重试。那是事务性数据；使用 Netlify DB。
