# Netlify Blobs

现代语法 — 从 `@netlify/blobs` 导入，打开一个存储库，对其进行操作：

```ts
import { getStore } from "@netlify/blobs";
const store = getStore("file-uploads");        // 全站范围
await store.set(key, value, { metadata: { … } });
const entry = await store.get(key);            // 如果不存在则为 null
```

部署特定的隔离：
```ts
import { getDeployStore } from "@netlify/blobs";
const store = getDeployStore("file-uploads");
```

需要 Fetch API (Node.js 18+)。**用 Go 编写的函数无法访问 Blobs。** 不适用于每个用户/事务性/关系型数据 — 请使用 Netlify DB。

## 常见陷阱（首先阅读）

- **站点范围的存储库 (`getStore`) 在所有部署上下文中共享。** 部署预览上的代码会读取、覆盖并删除生产数据。切勿从预览中运行破坏性测试或播种一次性数据 — 使用 `getDeployStore()` 或上下文特定的存储库名称以实现隔离。
- **站点范围的存储库不会跟随您的函数区域。** `getStore` 默认为 `us-east-2`，无论您的函数运行在哪里 — 不会引发错误或警告。要使用另一个区域，您必须在**每个**对该存储库的 `getStore` 调用中传递 `region`（读取、写入、删除）；省略它的调用会使用 `us-east-2` 并且看不到其他地方持有的数据。更改存储库的区域不会迁移数据。
- **最后写入者胜出。** 没有并发控制。不要在 blob 键上构建计数器、余额或读-改-写逻辑 — 即使使用 `onlyIfMatch` 重试。那是事务性数据；请使用 Netlify DB。
- **没有内置的访问控制。** 服务函数是门。默认为私有：在经过身份验证的函数后面进行读取，而不是公开暴露 blobs。将用户输入视为不安全的 — 不要提供任意调用者提供的键；用调用者无法篡改的东西来限定键的范围。
- **默认情况下为最终一致性** — 更新/删除可能需要长达 60 秒才能传播。如果读取必须立即看到最新的写入，请传递 `consistency: "strong"`（读取速度较慢）。
- **当操作失败时，显示错误并读取函数日志。** 不要发明 REST 端点或侧信道 API 来重试。

## 存储库选择

- `getStore(name)` — 全站范围；跨部署持久化，所有上下文均可读取。
- `getDeployStore(name)` — 限定于一个部署；用于隔离，以及从**构建插件**或基于文件的上传中的任何写入。
- **构建插件：** 可以从站点存储库中的任何存储库读取，但只能写入部署特定的存储库（`getDeployStore`）。

两者都接受位置形式 `getStore(name, { region, siteID, token })` / `getDeployStore(name, { deployID, region, siteID, token })` 或对象形式 `getStore({ name, consistency, region, siteID, token, fetch })`。`siteID`、`deployID` 和 `token` 在 Functions/Edge Functions/Build Plugins 中自动设置；仅当要覆盖（例如另一个您拥有的站点的 `siteID`）时才明确提供。`region` 仅对 `getDeployStore` 自动设置（默认为您的函数区域）；对于 `getStore` 它**不**自动设置，默认为 `us-east-2`。站点 ID = API `site_id` = `NETLIFY_SITE_ID` = UI 的**项目 ID**。

## 常见任务

持久化上传（函数）：
```ts
import { getStore } from "@netlify/blobs";
import type { Context } from "@netlify/functions";
import { v4 as uuid } from "uuid";

export default async (req: Request, context: Context) => {
  const form = await req.formData();
  const file = form.get("file") as File;
  const uploads = getStore("file-uploads");
  await uploads.set(uuid(), file, {
    metadata: { country: context.geo.country.name }
  });
  return new Response("Submission saved");
};
```

持久化 JSON — 使用 `setJSON`：
```ts
const uploads = getStore("json-uploads");
await uploads.setJSON(key, data, { metadata: { … } });
```

读取一个 blob（如果不存在则为 null）：
```ts
const entry = await uploads.get(key);
if (entry === null) return new Response("Not found", { status: 404 });
return new Response(entry);
```

带元数据的读取：
```ts
const { data, metadata } = await uploads.getWithMetadata(key);
```

删除 / 删除整个存储库：
```ts
await uploads.delete(key);
const { deletedBlobs } = await uploads.deleteAll(); // 如果存储库不存在则为 0
```

## API 界面

打开存储库：`getStore`、`getDeployStore`、`listStores`（从 `@netlify/blobs` 导入）。
存储库实例方法：`get`、`getWithMetadata`、`getMetadata`、`set`、`setJSON`、`list`、`delete`、`deleteAll`。

**`set(key, value, { metadata, onlyIfMatch, onlyIfNew })`** — `value` 是 `ArrayBuffer | Blob | string`。默认情况下会覆盖。解析为 `{ modified, etag }`。
**`setJSON(key, value, { metadata, onlyIfMatch, onlyIfNew })`** — 相同，`value` 任何可序列化为 JSON 的值。
**`get(key, { consistency, type })`** — `type` 为 `text`（默认）/ `json` / `arrayBuffer` / `blob` / `stream` 之一。解析为值，如果不存在则为 `null`。
**`getWithMetadata(key, { consistency, etag, type })`** — 解析为 `{ data, etag, metadata }`，如果不存在则为 `null`。如果 `etag` 与传递的值匹配，`data` 为 `null`（缓存仍然新鲜）。
**`getMetadata(key, { consistency, etag, type })`** — 解析为 `{ metadata, etag }`，如果不存在则为 `null`。无需下载 blob 即可检查存在性。
**`list({ directories, paginate, prefix })`** — 解析为 `{ blobs: [{ etag, key }], directories: string[] }`。
**`listStores({ paginate })`** — 解析为 `{ stores: string[] }`。**不包括**部署特定的存储库。
**`delete(key)`** — 解析为 `undefined`。
**`deleteAll()`** — 解析为 `{ deletedBlobs }`；删除存储库即删除其所有 blobs。

### 原子条件写入
- `onlyIfNew: true` — 只有当键不存在时才写入。
- `onlyIfMatch: etag` — 只有当当前 ETag 匹配时才写入（乐观并发）。
- 检查返回的 `modified` 布尔值以检测成功/失败。
```ts
const { modified } = await emails.set("jane@netlify.com", "Jane Doe", { onlyIfNew: true });
if (!modified) return new Response("Email already exists", { status: 400 });
```
（这些用于单个键的创建如果不存在/比较并设置，而不是用于构建事务性计数器。）

### 分层列出
使用 `/` 组合键。`list({ directories: true })` 返回顶级目录加上根 blob。使用 `prefix` 钻探 — **前缀必须包含尾随斜杠**（`"cats/"`），或者像 `catsuit` 这样的键也会匹配。
```ts
const { blobs, directories } = await animals.list({ directories: true });
const cats = await animals.list({ directories: true, prefix: "cats/" });
```

### 分页
服务器最多分页**1,000** 条条目（`list`）/ **1,000** 个存储库（`listStores`）。默认情况下自动处理；传递 `paginate: true` 以获取 `AsyncIterator`：
```ts
for await (const entry of store.list({ paginate: true })) {
  console.log(entry.blobs);
}
```

### 条件请求 / 本地缓存
将缓存的 `etag` 传递给 `getWithMetadata`/`getMetadata`；如果匹配，`data` 为 `null`（您的副本是新鲜的）。比较整个值，包括周围的引号和任何弱前缀。

## 配置

### 一致性
默认为**最终一致性**（单区域、边缘缓存；传播时间在 60 秒内）。按存储库或按读取启用**强一致性**：
```ts
const store = getStore({ name: "animals", consistency: "strong" }); // 存储库级别
const dog = await store.get("dog", { consistency: "strong" });      // 操作级别
```
Netlify CLI 总是使用强一致性。

### 区域
有效区域（比[函数区域](https://docs.netlify.com/build/functions/configuration#region)更小的集合）：`us-east-1`、`us-east-2`、`eu-central-1`、`ap-southeast-1`、`ap-southeast-2`。

- **部署特定的存储库**（`getDeployStore`）默认为您的函数区域；`region` 在 Functions/Edge Functions/Build Plugins 中自动设置。显式覆盖：
  ```ts
  const uploads = getDeployStore({ name: "file-uploads", region: "ap-southeast-2" });
  ```
- **站点范围的存储库**（`getStore`）默认为 `us-east-2` 并且**不**跟随您的函数区域。`region` 在这里**不**自动设置。
  ```ts
  const profiles = getStore({ name: "user-profiles", region: "eu-central-1" });
  ```

**陷阱 — 在每个调用中传递 `region`。** 站点范围的存储库只有在**每个** `getStore` 调用（读取、写入、删除）都传递相同的 `region` 时才能访问非默认区域的数据。省略它，调用会默默地使用 `us-east-2` — 不会引发错误。**更改存储库的区域不会迁移数据**：存储库在新区域中为空，而原始数据仍保留在旧区域中。要移动数据，请将每个条目复制到在新区域中打开的存储库中，然后从旧存储库中删除。

### 自定义 `fetch`
如果您无法使用 Node.js 18，请提供您自己的 `fetch`：
```ts
const uploads = getStore({ fetch, name: "file-uploads" });
```

## 基于文件的上传（部署特定的存储库）

用于框架/工具作者在不使用构建插件的情况下集成的。将 blob 文件放置在站点基本目录的 `.netlify/blobs/deploy` 下；Netlify 在构建后、部署前上传它们（保留目录结构）。

**Netlify 在每次构建前都会删除 `.netlify/blobs/deploy`** — 提交到存储库的文件**不会**上传。您必须在构建期间（构建命令或插件）创建 blob 文件。

使用带前缀 `$` 和以 `.json` 结尾的 JSON 文件为 blob 文件名前缀附加元数据：
```
.netlify/blobs/deploy/
├─ dogs/
│  ├─ good-boy.jpg
│  └─ $good-boy.jpg.json
├─ cat.jpg
└─ mouse.jpg      (无元数据)
```
元数据文件必须是有效的 JSON，否则部署会失败。需要持续部署或 CLI 部署。

## 部署特定的存储库生命周期
- 在回滚时同步；随自动部署删除而清理。
- **下载部署****不会**下载部署特定的 blobs。
- **锁定已发布的部署****不会**阻止向其部署特定的存储库写入。

## 过期（无内置 TTL）
自行实现：`set` 带有元数据中的时间戳 → `getWithMetadata` 检查 → 如果过期则 `delete`。

## CLI
`netlify blobs:list/get/set/delete` 存在用于检查 — 有关详细信息，请参阅[CLI blobs 命令参考](https://cli.netlify.com/commands/blobs/)。CLI 总是使用强一致性，并需要一个站点范围的存储库。

## 本地开发
Netlify Dev 使用一个沙盒化的本地存储库：没有基于文件的上传，并且您无法在本地读取生产数据。

## 限制
- 存储库名称：不能包含 `/` 或 `:`，最大**64 字节**。
- 键：非空，不能以 `/` 开头，任何 Unicode，最大**600 字节**。
- 对象最大**5 GB**；元数据最大**2 KB**。（字节限制，不是字符计数 — 某些 UTF-8 字符是多字节的。）
- Blobs 在静止和传输过程中加密；只能通过您的站点访问。
- **不**是 Netlify 的 HIPAA 合规托管服务的一部分。
- 在信任任何第三方构建插件进行 blob 访问之前，请检查其代码。

## 迁移（`@netlify/blobs` 6.5.0 → 7.0.0）
使用 6.5.0 或更早版本编写的站点范围存储库在升级后无法访问（命名空间更改）。使用最新的[Netlify CLI](https://docs.netlify.com/api-and-cli-guides/cli-guides/get-started-with-cli) 按存储库迁移：
```sh
netlify recipes blobs-migrate YOUR_STORE_NAME
```
迁移后的存储库可以在 7.0.0+ 版本中访问。

<!-- system: agent-context/blobs/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 规则（blobs）

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. Blobs 不是一个数据库。对于动态、每个用户或事务性数据，请使用 Netlify DB — Blobs 用于对象、文件和类似缓存的状态。
2. 当存储库操作失败时，显示错误并读取函数日志 — 不要发明 REST 端点或侧信道 API 来重试。
3. `netlify blobs:list/get/set/delete` 存在用于检查；CLI 参考是它们的真实来源 — 链接，不要重述。
4. Blobs 没有内置的访问控制 — 服务函数是门。如有疑问，默认为私有：在经过身份验证的函数后面进行读取，而不是公开暴露 blobs。
5. 站点范围的存储库在所有部署上下文中共享 — 部署预览上的代码会读取、覆盖并删除生产数据。切勿从预览中运行破坏性测试或播种一次性数据；使用 `getDeployStore()` 或上下文特定的存储库名称以实现隔离。
6. 不要在 blob 键上构建计数器、余额或读-改-写逻辑 — 即使使用 `onlyIfMatch` 重试。那是事务性数据；请使用 Netlify DB。
7. 构建插件：同时声明两半 — 它们可以读取站点存储库中的任何存储库，但只能写入部署特定的存储库（`getDeployStore`）。
