---
name: cargo-hosting
description: 从 Cargo 中将内容发布到互联网上——包括托管式网络应用（默认使用 Vite，其他静态框架也能检测）和响应 HTTP 请求的无服务器边缘工作器，以及构建和发布它们的部署流程、工作器读取的环境变量和密钥、本地运行工作器、以及公共站点的自定义域名和搜索索引。触发器："为我构建一个仪表盘"、"托管这个应用"、"给我一个分享的 URL"、"部署这个"、"我需要一个 webhook 端点"、"让它上线"、"发布到生产环境"、"为我的团队开发 UI"、"给我的工作器一个 API 令牌"、"在工作器上设置一个密钥"、"缺少 CARGO_API_TOKEN"、"我的应用无法调用我的工作器"、"本地运行工作器"、"将它部署到我的自定义域名"、"让网站可被 Google 索引"。当应用或工作器应被声明为已提交的工作空间代码时跳过——请使用 cargo-project。
---

# Cargo CLI — 托管

**Cargo Hosting** 运行两种工作区范围资源，以及它们所承载的部署：

- **App** — 一个静态前端（默认为 Vite 单页应用；也会检测 Next.js 静态导出、Astro、SvelteKit、Nuxt、Gatsby 和 Create React App）在其自己的子域名上提供服务（参见 [URLs](#urls)）。模板基于 `@cargo-ai/app-sdk` 构建（Vite + refine + shadcn 基础，并连接了 `getCargoEnv()` / `useCargoApi()` 到工作区）。
- **Worker** — 一个无服务器的 HTTP 处理程序，在边缘运行 (`fetch(request, env)`)，基于 `@cargo-ai/worker-sdk`（自动生成 OpenAPI 3.1 规范在 `/openapi.json`，Swagger UI 在 `/docs`）。
- **Deployment** — 将本地源目录的一次构建+上传到应用或 Worker。部署在**被提升之前不会生效**。

> 要将应用/Worker 组织到 **文件夹** 中，请使用 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`folder …`)。这里的 `--folder-uuid` 标志会消耗这些文件夹 UUID。

> 参考 `references/examples/apps.md`、`references/examples/workers.md` 和 `references/examples/deployments.md` 获取端到端的演练。
> 参考 `references/response-shapes.md` 获取 JSON 响应结构。
> 参考 `references/troubleshooting.md` 获取常见错误及其解决方法。

## 初始化

如果已经登录 (`cargo-ai whoami` 返回工作区)，则跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器）· --token <api-token>（CI）
cargo-ai whoami                         # 在进行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批次的任何操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌作用域和管理员专用的界面。

## 生命周期

应用和 Worker 遵循相同的形状——**脚手架 → 创建槽位 → 部署 → 提升**：

```
init (本地脚手架) → create (槽位 + 拼缀符) → deployment create (构建+上传) → deployment promote (上线)
```

1. **从模板在本地创建项目** — `hosting app init <dir>` / `hosting worker init <dir>`。
2. **在工作区中创建槽位** — `hosting app create --name --slug` → `appUuid`（或 `workerUuid`）。`--slug` 成为子域名的一部分，必须在工作区内唯一。
3. **(可选) 本地开发连接** — 对于应用，`hosting app env <appUuid>` 会打印本地副本需要的 `.env.local` 行（Cargo OAuth + 工作区 + 应用 UUID + API URL）。对于 Worker，在脚手架中运行 `npm run dev`（参见 [本地运行 Worker](#run-a-worker-locally)）。调用 Cargo API 的 Worker 在首次部署前还需要一个 `CARGO_API_TOKEN` 密钥（参见 [Worker 环境变量和密钥](#worker-env-vars-and-secrets)）。
4. **部署** — `hosting deployment create --app-uuid <uuid> --source <dir>` 上传源代码。后台会在沙盒中构建它：对于应用，运行 `npm ci --ignore-scripts` 后跟应用的自己的 `build` 脚本，或者如果没有则运行框架的默认构建（参见 [App 构建](#app-builds)）；对于 Worker，它会打包入口点。返回 `deploymentUuid`。
5. **提升** — `hosting deployment promote --uuid <deploymentUuid>` 将活动 URL 指向该构建。

部署是异步构建的——**在提升之前轮询 `hosting deployment get <uuid>`**，直到状态变为终端状态（参见 [异步轮询](#async-polling)）。

## URL

活动主机是 **`<slug>-<工作区 UUID 的前 8 个字符>`** 在托管根域名下，应用和 Worker 有**不同的根域名**——生产环境中的应用是 `https://<slug>-<ws>.app.getcargo.run`，Worker 是 `https://<slug>-<ws>.worker.getcargo.run`。工作区后缀使其主机全局唯一，这就是为什么 slug 只需在工作区内唯一。

不要手动构建 URL。从 `create` 或 `get` 中读取 `url`——每个环境的根域名都不同。每个部署在提升前都会获得一个预览主机，`https://deployment-<deploymentUuid>.<root>`。

由于根域名不同，**应用调用 Worker 总是跨源请求。** 没有选项可以在同一源上提供它们，因此 Worker 必须处理 CORS。参见 [`references/examples/workers.md`](references/examples/workers.md#calling-a-worker-from-an-app) 中的应用+Worker 模式。

## 应用

```bash
# 发现
cargo-ai hosting app list                          # 所有应用（使用 --folder-uuid <uuid> 过滤）
cargo-ai hosting app get <uuid>                     # 一个应用的详细信息 + URL

# 本地从模板创建项目（Vite + @cargo-ai/app-sdk）
cargo-ai hosting app init ./my-app --list-templates # 查看可用模板，然后：
cargo-ai hosting app init ./my-app --template blank --name "My App"

# 在工作区中创建槽位（slug 在工作区内唯一；响应中的 `url` 是活动主机）
cargo-ai hosting app create --name "My App" --slug my-app --folder-uuid <folder-uuid>

# 打印 .env.local 用于本地开发
cargo-ai hosting app env <app-uuid>
cargo-ai hosting app env <app-uuid> --api-url https://api.getcargo.io

# 更新/删除
cargo-ai hosting app update --uuid <app-uuid> --name "Renamed"
cargo-ai hosting app update --uuid <app-uuid> --folder-uuid null   # 移动到工作区根目录
cargo-ai hosting app remove <app-uuid>                             # 也会删除其部署
```

模板：`blank`（最小起点）、`territories-overview`（只读区域网格演示 `useCargoApi()` + react-query）、`public-site`（一个公共、可索引的站点，从其自己的构建脚本预渲染每个路由，并附带 `robots.txt` + `sitemap.xml`）。运行 `app init <dir> --list-templates` 获取当前列表。

### App 构建

如果 `package.json` 声明了一个 `build` 脚本，Cargo 会运行它，并且该脚本拥有整个构建。Cargo 不会在它之前或之后运行任何内容，因此该脚本必须生成客户端包以及任何额外内容，例如预渲染的 HTML。如果没有 `build` 脚本，则会运行检测到的框架的默认命令：

| 框架（从依赖项检测） | 默认构建 | 输出目录 | 公共环境前缀 |
|---|---|---|---|
| Vite 和未检测到的任何内容 | `vite build` | `dist` | `VITE_` |
| Next.js（静态导出） | `next build` | `out` | `NEXT_PUBLIC_` |
| Astro | `astro build` | `dist` | `PUBLIC_` |
| SvelteKit | `svelte-kit build` | `build` | `PUBLIC_` |
| Nuxt | `nuxt generate` | `.output/public` | `NUXT_PUBLIC_` |
| Gatsby | `gatsby build` | `public` | `GATSBY_` |
| Create React App | `react-scripts build` | `build` | `REACT_APP_` |

- **输出必须位于该框架的输出目录中，并包含 `index.html`**，否则构建失败。未知路径会回退到该 shell。
- **构建脚本现在在每次部署时都会运行。** 这包括 `tsc` 遍历、不同的 `--mode` 和 `prebuild`/`postbuild` 钩子。失败的脚本会导致部署失败。活动部署会继续服务，因为提升只跟在成功的构建之后。
- **Cargo 无法使用的构建脚本会静默回退。** 这包括无法解析的 `package.json`、空的脚本或非字符串条目。部署仍然会变绿，并且只有构建日志会说明原因，因此当预渲染步骤似乎被跳过时，请检查它。
- **平台值会注入到每个公共前缀下。** Vite 应用读取 `VITE_CARGO_API_URL`，Next.js 应用读取 `NEXT_PUBLIC_CARGO_API_URL`。当使用 `build` 脚本时，它们也会作为真实的进程环境变量传递，因此纯 Node 预渲染步骤会看到它们。用户环境值会被从构建日志中删除。

### App 环境变量是公开的

应用只读取以**公共前缀**开头的环境变量：`VITE_`、`NEXT_PUBLIC_`、`PUBLIC_`、`NUXT_PUBLIC_`、`GATSBY_` 或 `REACT_APP_`。无论框架如何，这些前缀都有效。它们来自工作区环境变量和应用级别的条目（`POST /v1/hosting/env-vars`，其中 `"kind":"app"`，或 CDK `defineApp({ env })`）。它们中的每一个都会被编译成一个任何人都可以下载的包。出于这个原因：

- **App 环境变量不能是密钥。** API 会拒绝 `isSecret: true` 并返回 `secretNotSupportedForApp`，CDK `defineApp` 会抛出 `secret()` 值，并且密钥工作区条目永远不会到达应用构建。凭证应存储在一个应用调用的 Worker 中。
- 匹配任何前缀下的平台键（`*_CARGO_API_URL`、`*_CARGO_WORKSPACE_UUID`、`*_APP_BASE_PATH`、…）是保留的。
- 值在构建时嵌入，因此需要新的部署 + 提升。

### 自定义域名和搜索索引

**Cargo 拥有的主机是 `noindex`。** 默认的 `*.app.getcargo.run` 主机和每个 `deployment-<uuid>` 预览都会回答 `X-Robots-Tag: noindex`，因此**应用只有在自定义域名上才会被索引**。自 CLI 1.0.96 起，没有 CLI 命令会附加其中一个，因此请使用 API：

```bash
CARGO_API_BASE=$(cargo-ai whoami | jq -r '.baseUrl')   # 生产环境中的 https://api.getcargo.io
curl -X POST "$CARGO_API_BASE/v1/hosting/custom-domains" \
  -H "authorization: Bearer $CARGO_API_TOKEN" -H "content-type: application/json" \
  -d '{"kind":"app","appUuid":"<uuid>","hostname":"www.example.com"}'
# → 需要添加的 DNS 记录：证书验证记录 + 主机名的 cnameTarget
curl -X POST "$CARGO_API_BASE/v1/hosting/custom-domains/<domain-uuid>/refresh-status" \
  -H "authorization: Bearer $CARGO_API_TOKEN"                                   # 重复直到状态为 "active"
```

- 域名需要**至少三个标签**，因此请附加 `www.example.com`，而不是 `example.com`。
- Worker 也支持自定义域名（`"kind":"worker","workerUuid":…`）。即使使用不同的主机名，它们仍然是不同的源，因此应用→Worker 的 CORS 仍然适用。
- **索引也需要每个 URL 的真实 HTML。** 在 `build` 脚本中预渲染（`public-site` 模板展示了如何）。将预渲染路由作为 `.html` 路径链接：`/about.html` 服务器预渲染文件，而 `/about` 会回退到 SPA shell。发送 `public/robots.txt` + `public/sitemap.xml`，并在每个预渲染的头部中放入标题、描述、规范和 Open Graph 标签。
- **托管应用永远不会返回 404。** 未知路径会以 SPA shell 和 200 状态返回，因此客户端未找到视图应设置 `<meta name="robots" content="noindex">`。
- **基于 `CargoRefineApp` 构建的应用需要 Cargo 登录**，并且不能被索引。公共站点会渲染自己的树。
- 你不会为你提交任何内容到搜索引擎。请在 Search Console 中提交站点地图。

## Worker

与应用的命令形状相同——将 `worker` 替换为 `app`：

```bash
cargo-ai hosting worker list                        # 使用 --folder-uuid <uuid> 过滤
cargo-ai hosting worker get <uuid>

# 脚手架（基于 @cargo-ai/worker-sdk 的边缘 fetch(request, env) 处理程序）
cargo-ai hosting worker init ./my-worker --list-templates
cargo-ai hosting worker init ./my-worker --template blank --name "My Worker"

cargo-ai hosting worker create --name "My Worker" --slug my-worker --folder-uuid <folder-uuid>
cargo-ai hosting worker update --uuid <worker-uuid> --name "Renamed"
cargo-ai hosting worker remove <worker-uuid>        # 也会删除其部署
```

模板：`blank`（自动 OpenAPI 规范 + Swagger UI）和 `custom-integration`（Cargo 自定义集成——清单 / 操作 / 提取器 / 自动完成 / 动态模式）。

**入口点。** 构建会打包 `src/index.ts`、`src/index.js`、`index.ts`、`index.js` 中存在的第一个，如果没有则失败。`.mjs`、`.mts` 和 `.cjs` 入口点不会被选中，因此请将它们重命名为 `.js`/`.ts`；ES 模块语法在 `.js` 中有效，因为脚手架的 `package.json` 设置了 `"type": "module"`。

### Worker 环境变量和密钥

Worker 从 `c.env.KEY`（Hono 上下文）或 `fetch(request, env)` 的 `env` 参数读取配置。三个来源为其提供数据：

| 来源 | 设置方式 | 可达 |
|---|---|---|
| **平台绑定** | 自动 | `CARGO_API_URL`、`CARGO_WORKSPACE_UUID`、`CARGO_WORKER_UUID` |
| **工作区环境变量** | `cargo-ai workspaceManagement envVar create --key K [--secret]` | 工作区中的每个 Worker（应用只能获取非密钥、公共前缀的条目） |
| **Worker 环境变量** | CDK 中的 `defineWorker({ env })`，或 `POST /v1/hosting/env-vars`（CLI 1.0.96 没有托管 CLI 命令） | 仅该 Worker，并且 Worker 条目会覆盖具有相同键的工作区条目 |

**`CARGO_API_TOKEN` 不会被注入。** `createCargoApi(c.env)` 会抛出 `Missing CARGO_API_TOKEN…`，直到你提供它。创建工作区 API 令牌并将其作为密钥存储在首次部署之前：

```bash
cargo-ai workspaceManagement token create --name "worker: my-worker"   # 值仅显示一次
export CARGO_API_TOKEN=<token value>
cargo-ai workspaceManagement envVar create --key CARGO_API_TOKEN --secret \
  --description "Cargo API 令牌，用于托管 Worker"                     # --value 被省略 → 从 $CARGO_API_TOKEN 读取
```

工作区条目会提供给*每个* Worker。如果只有一个 Worker 应该持有它，请在该 Worker 上设置它：

- **CDK:** `defineWorker("my-worker", { path, env: { CARGO_API_TOKEN: secret("CARGO_API_TOKEN") } })`。
- **API:** `POST /v1/hosting/env-vars`，其中 `{"kind":"worker","workerUuid":"<uuid>","key":"CARGO_API_TOKEN","value":"…","isSecret":true}`。在 TypeScript 中是 `api.hosting.envVars.create(…)` 在 `@cargo-ai/api` 中，`list` 需要 `{ workerUuid }`。

**值在部署时捕获，而不是实时读取。** 绑定在部署提升时附加，非密钥值也会在构建时编译为 `process.env.KEY`。添加或更改变量后，**再次运行 `deployment create` 和 `promote`**。运行中的 Worker 会保持旧值，直到那时。

**密钥永远不会进入包中。** 密钥会作为加密的运行时值绑定。只有非密钥值会被编译，并且包可以从每个部署的预览主机下载，因此任何敏感信息都必须是 `--secret` / `isSecret: true`。

### 本地运行 Worker

两个模板都附带一个 `dev.ts` 托管：`npm run dev` 在 Node 下提供 `src/index.ts`，并在 `http://localhost:8787` 上热重载（可使用 `PORT` 覆盖）。`dev.ts` 永远不会部署。

- **本地不存在平台绑定**，因此 `c.env` 为空。`createCargoApi` 会回退到 `process.env`，因此请在 `npm run dev` 之前在 shell 中导出 `CARGO_API_TOKEN`（以及非生产 API 的 `CARGO_API_URL`）。你自己的变量需要在代码中具有相同的回退。
- **`manifest.json` `outboundAllowlist` 和 cron 触发器在本地不会强制执行。** 在部署上测试它们。

在 `dev.ts` 存在之前创建的项目可以复制它从新的 `hosting worker init`，以及 `dev` 脚本和 `@hono/node-server` + `tsx` 开发依赖项。

### Worker 日志和错误

`createWorker()` 会捕获 Cargo 分发每个请求期间的 `console.log/info/warn/error/debug`，并将它们发送到 Worker 的日志（每个请求最多 50 行）。未捕获的错误会记录其堆栈并回答一个裸 `500`。

**捕获的错误不会留下痕迹。** 如果路由捕获异常并返回自己的清理响应，例如 `502 "The data provider is unavailable"`，则日志只会得到 HTTP 行。**在清理之前记录错误：**

```ts
try {
  return c.json(await loadData(createCargoApi(c.env)));
} catch (err) {
  console.error(err);                        // 堆栈会发送到日志；响应保持干净
  return c.json({ error: "The data provider is unavailable." }, 502);
}
```

在 CLI 1.0.96 版本中，日志可以通过 Web 应用或 API 进行查看：使用 `POST /v1/hosting/logs/list` 并传入 `{"workerUuid":"<uuid>","levels":["error"],"limit":50}`，或者在 TypeScript 中使用 `api.hosting.log.list(…)`。它还支持按 `runUuid`、`search` 以及 `occurredAfter`/`occurredBefore` 进行过滤。目前 CLI 尚无日志命令。

## 部署

一个部署只能属于一个应用 **或** 一个工作进程（`--app-uuid` 和 `--worker-uuid` 互斥）。

```bash
# 列出/检查
cargo-ai hosting deployment list --app-uuid <uuid>          # 或 --worker-uuid <uuid>
cargo-ai hosting deployment get <deployment-uuid>           # 状态 + 元数据
cargo-ai hosting deployment get-promoted --app-uuid <uuid>  # 当前运行的内容

# 构建 & 上传本地源目录（指向包根目录，不是 dist/）
cargo-ai hosting deployment create --app-uuid <uuid> --source ./my-app
cargo-ai hosting deployment create --worker-uuid <uuid> --source ./my-worker
# 默认忽略：node_modules,dist,build,.git,.next — 可用 --ignore "a,b,c" 覆盖

# 正式上线
cargo-ai hosting deployment promote --uuid <deployment-uuid>
```

## 关键规则

- **`--slug` 在工作区中唯一**，在线主机为 `<slug>-<工作区前缀>.<根>`，应用和工作进程使用不同的根。使用 `get` 命令返回的 `url` 而不是自行组合（参见 [URLs](#urls)）。重复的 slug 在 `create` 时会因 `duplicateSlug` 失败。
- **应用调用工作进程是跨域的**。工作进程必须为应用的来源发送 CORS 头部。不存在同源挂载。
- **`CARGO_API_TOKEN` 由你提供**。它不会被注入，且 `createCargoApi` 在没有它时会报错。在需要它的部署前将其设置为密钥（工作区或工作进程环境变量）。
- **环境变量变更需要新的部署 + 上线**。值在上线时绑定，非密钥变量会被编译到包中，因此编辑变量不会立即生效，需等到下一次部署上线。
- **上线前先记录日志**。只有未捕获的错误会带有堆栈信息到达日志。返回友好消息的 `catch` 必须先 `console.error(err)`，否则原因会丢失。
- **部署 ≠ 上线**。`deployment create` 用于构建和上传；URL 仅在 `deployment promote` 时改变。使用 `deployment get-promoted` 查看当前运行的内容。
- **`--source` 是包根目录，不是 `dist/`**。构建在 Cargo 沙盒中运行：`npm ci --ignore-scripts` 后运行应用的 `build` 脚本（或框架默认脚本）用于应用，工作进程使用入口捆绑。上传预构建的 `dist/` 不可行。
- **应用环境变量公开且永不保密**。它们会被编译到包中，且 `isSecret` 会被拒绝。将凭证放在工作进程中。
- **Cargo 拥有的主机是 `noindex`**。公开站点需要自定义域名（API 仅在 1.0.96 版本支持）和预渲染 HTML 才能被索引。
- **构建是异步的** — 在上线前轮询 `deployment get` 直到状态终止（见下文）。
- **`--app-uuid` / `--worker-uuid` 在 `deployment create`、`deployment list` 和 `deployment get-promoted` 中互斥**。必须传入一个。
- **`remove` 级联删除** — 删除应用或工作进程也会删除其所有部署。
- **`update --folder-uuid null`**（字面字符串 `null`）将资源移回工作区根目录。
- **Hosting 按月消耗资源**。每个应用/工作进程有一个 `chargedUntil`，每小时轮询会每月递增，因此在线应用或工作进程会持续消耗 Hosting 信用 — 删除不再服务的资源。通过 [`cargo-billing`](../cargo-billing/SKILL.md) 追踪消耗。

## 异步轮询

`deployment create` 启动沙盒构建。部署的 `status` 会从 `pending → building → success`（或 `error` / `cancelled`）。轮询直到状态终止，然后上线 `success` 的部署：

```bash
cargo-ai hosting deployment get <deployment-uuid>   # 轮询 ~2–5s 直到状态终止
```

终止状态为 `success`、`error` 和 `cancelled` — 仅上线 `success` 部署。出现 `error` 时，查看部署的 `errorMessage`（和 `buildLogS3Filename`）以诊断构建问题。关于轮询模式（间隔、重试），参见 [`../cargo-orchestration/references/polling.md`](../cargo-orchestration/references/polling.md)。

## 帮助

每个命令支持 `--help`：

```bash
cargo-ai hosting app create --help
cargo-ai hosting deployment create --help
```
