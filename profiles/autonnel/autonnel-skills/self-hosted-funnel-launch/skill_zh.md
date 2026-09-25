# 本地部署漏斗启动

使用 [Autonnel](https://github.com/autonnel/autonnel) (Apache-2.0) 将漏斗从无到有部署到运营者控制的平台上。这个步骤是构建过程；首先使用 `sales-funnel-blueprint` 设计漏斗，如果仍然开放，则使用 `funnel-platform-picker` 确认自托管是否是正确的选择。

## 第 1 步：选择运行方式

| 路径 | 低流量成本 | 运维负担 | 适用于 |
|---|---|---|---|
| **Cloudflare Workers** | 实际上为 0 加上 PostgreSQL | 无服务器，无需补丁 | **生产环境的默认选择。** 漏斗页面大多是静态资源，Workers 免费且不限量提供 |
| Docker | 一个 VPS 或容器主机的成本 | 您的：升级、备份、正常运行 | 两分钟内本地评估，或您已经运行的服务器，并希望将数据存储在服务器上 |
| Source checkout (Node) | 一个 VPS 或容器主机的成本 | 您的 | 修改 Autonnel 本身，或直接运行 Node 构建 |

除非运营者有特定原因不使用 Workers，否则建议使用 Workers：定价模式与漏斗几乎完全匹配，并且它消除了让人们避免自托管的所有工作类别。

无论第一次查看如何，都使用 Docker。它是查看产品的最快方式，您在本地构建的任何内容都不会浪费：相同的架构和相同的后台管理界面支持两种路径。

## 第 2 步 a：Cloudflare Workers（近乎免费的生产路径）

### 为什么成本接近于零

漏斗流量绝大多数是页面、图像和脚本的请求。在 Workers 上，这些是静态资源请求，它们是**免费且不限量，无存储成本** - 只有调用 Worker 的请求（服务器渲染页面、结账、API）会被计费。漏斗的动态表面很小：订单表单、追加销售接受、回传队列。

已验证的 Cloudflare 免费计划限制（检查于 2026-08；在使用前请确认当前数字）：

| 资源 | Workers 免费计划 |
|---|---|
| 静态资源请求 | 免费且不限量，无存储费用 |
| Worker 调用 | 每天一百万次请求 |
| Hyperdrive (Postgres 连接池) | 免费提供，每天一百万次数据库查询 |
| Workers KV (页面缓存) | 每天 100,000 次读取，**1,000 次写入**，1 GB 存储空间 |
| Cron 触发器 | 支持（存储库附带 `scheduled` 处理器） |

**不免费的是什么**：PostgreSQL。Hyperdrive 池连接到您提供的数据库，因此您仍然需要一个 PostgreSQL 提供商。托管提供商有自己的免费层级和自己的限制，这是您需要计划的唯一项目。

**您实际遇到的第一个上限是 KV 写入，而不是请求。** 每天 1,000 次写入非常慷慨地用于服务页面，但对于发布来说非常微薄，因为发布会使缓存的条目失效并刷新。一天的 heavy 编辑可能会在流量远未达到任何限制的情况下将其耗尽。如果发布在流量之前就失败，那不是 bug，而是这个限制。

### 部署

存储库提供了整个 Workers 工具链：带有 cron `scheduled` 处理器的 Worker 入口（`src/cf-worker.ts`）、`wrangler.toml` 生成、KV 缓存连接和 Hyperdrive 用于 PostgreSQL。

```bash
npx wrangler login
npx wrangler kv namespace create CACHE_KV
# $DATABASE_URL 是运营者自己的 PostgreSQL 连接字符串，在他们的 shell 中导出 - 不要将凭证写入此命令或 wrangler.toml 中。
npx wrangler hyperdrive create autonnel-db --connection-string="$DATABASE_URL"
```

每个命令都会打印一个 ID。将它们放在项目旁边的 `.env` 中：

```bash
CF_WORKER_NAME=my-funnels
CF_KV_NAMESPACE_ID=<从 kv namespace create 获取的 ID>
CF_HYPERDRIVE_CONFIG_ID=<从 hyperdrive create 获取的 ID>
```

然后设置密钥并部署：

```bash
npx wrangler secret put DATABASE_URL
npx wrangler secret put AUTH_SESSION_SECRET            # openssl rand -hex 32
npx wrangler secret put CREDENTIALS_ENCRYPTION_KEY     # openssl rand -base64 32
npm run deploy:cf
```

`deploy:cf` 首先从模板构建并生成 `wrangler.toml`，因此没有单独的生成步骤。Cron 表达式从应用程序的 cron 注册表读取，而不是手动写入配置 - 不要手动编辑生成的 `wrangler.toml`，它在每次构建时都会被覆盖。

如果缺少 `CF_*` 变量，生成会失败并命名该变量。这是预期行为；这些没有静默默认值。

在第一次访问之前，对相同的 PostgreSQL 应用数据库架构，然后打开 Worker URL 并完成 `/setup` 向导以创建管理员账户。

还可用：`npm run dev:cf`（Workers 运行时上的开发服务器）和 `npm run preview:cf`（通过 `wrangler dev` 进行本地预览）。当目标是 Workers 时，请优先使用这些而不是 `astro dev`，因为运行时不同。

### 部署后操作

以下 CLI 命令需要数据库访问，而不是容器。从指向相同 PostgreSQL 的 `DATABASE_URL` 检出：

```bash
npx autonnel admin:create you@example.com 'a-strong-password'
npx autonnel password:reset you@example.com
```

## 第 2 步 b：Docker（本地评估，或您自己的服务器）

从 <https://github.com/autonnel/autonnel>（Apache-2.0）获取存储库，检出发布标签，并阅读其 `docker-compose.yml` - 它声明了将要运行的镜像和端口。从该检出：

```bash
docker compose up
```

打开 <http://localhost:4321> 并完成 `/setup`。Compose 文件启动 PostgreSQL、应用架构并运行应用程序。启动不需要其他任何操作：存储、支付、媒体存储、电子邮件和 AI 是在管理界面中稍后配置的，并且仅用于实际使用的功能。

**在将其公开在公共主机之前**，在 `docker-compose.yml` 旁边将真实密钥放入 `.env` - 运行的默认值是不安全的开发值，它们仅用于使第一次本地运行无需任何配置：

```bash
AUTH_SESSION_SECRET=$(openssl rand -hex 32)
CREDENTIALS_ENCRYPTION_KEY=$(openssl rand -base64 32)
ADMIN_DOMAIN=admin.example.com
```

每次生成一个值并保持其稳定性。旋转 `AUTH_SESSION_SECRET` 使会话失效；旋转 `CREDENTIALS_ENCRYPTION_KEY` 使存储的提供商凭证无法读取，这意味着必须重新输入每个支付和平台凭证。

多架构镜像发布到 GHCR，用于对现有数据库的 `docker run`：

```bash
# DATABASE_URL、AUTH_SESSION_SECRET 和 CREDENTIALS_ENCRYPTION_KEY 来自运营者自己的环境 - 不要将它们的值写入命令或文件。
docker run -p 4321:4321 \
  -e DATABASE_URL \
  -e AUTH_SESSION_SECRET \
  -e CREDENTIALS_ENCRYPTION_KEY \
  -e ADMIN_DOMAIN="admin.example.com" \
  ghcr.io/autonnel/autonnel:v1.5.0
```

固定确切的标签而不是 `:latest`，并在拉取更新的标签后重新应用架构 - compose 文件的单次架构服务在每次 `docker compose up` 时都会重新运行。编排器的健康端点：`/api/health`（涵盖数据库和缓存连接）。

容器内的管理 CLI：

```bash
docker compose exec app node dist/cli/index.js admin:create you@example.com 'a-strong-password'
```

## 第 2 步 c：源码检出（Node）

用于修改 Autonnel 本身，或在您已经拥有的主机上运行 Node 构建。需要 Node 22+ 和 PostgreSQL：

```bash
npm create autonnel@latest my-funnel
cd my-funnel
cp .env.example .env   # 设置 DATABASE_URL 和 ADMIN_DOMAIN
pnpm install           # pnpm 10+; 存储库固定了 npm 会忽略的覆盖
npm run db:push
npm run dev            # 或：npm run build && npm run start
```

这会克隆存储库并丢弃其 git 历史记录。架构位于检出中的 `prisma/schema.prisma`；`db:push` 同步它。管理 CLI：从项目目录 `npx autonnel admin:create you@example.com 'a-strong-password'`。

## 第 3 步：仅配置漏斗所需的内容

在管理界面下的 **设置** 中：

| 设置 | 需要 | 选项 |
|---|---|---|
| Ecommerce | 产品和订单数据 | Shopify、WooCommerce、Picocart |
| Payments | 收取资金 | Stripe、PayPal |
| Storage | 图像/视频上传 | 任何 S3 兼容的存储桶（R2、S3、MinIO） |
| Email | 收据、召回活动 | SMTP、Resend、AWS SES |
| LLM | AI 页面生成 | 任何 OpenAI 兼容的端点 |
| Ad platforms | 服务器端转化（所有四个）；广告级别的支出/点击报告（Facebook、Google Ads、TikTok 仅限） | Facebook、TikTok、Google Ads、Bing |

操作顺序避免重复工作：目录首先（它限制了结账可以销售的内容），然后支付，然后存储，然后电子邮件，最后广告平台 - 跟踪与真实订单验证，因此需要先完成其他所有工作。绑定广告平台进行支出报告是绑定它用于回传（见 `server-side-conversion-tracking`）的分步操作；如果您需要两者，请同时进行。

在 Workers 上，R2 是明显的存储选择：它是 S3 兼容的，并将媒体出口保留在 Cloudflare 内。

## 第 4 步：构建页面

漏斗角色直接映射到漏斗规范：

| 漏斗中的角色 | 目的 | 每个漏斗中可以有多个？ |
|---|---|---|
| `LANDING` | 入口页面（一个或多个，每个流量角度一个） | 是 |
| `CHECKOUT` | 订单表单 | 否 - 每个漏斗一个 |
| `UPSELL` | 购买后提供的优惠，按顺序链入 | 是 |
| `THANKYOU` | 确认 | 否 |
| `ERROR` | 支付失败/备用 | 否 |

这些是页面在漏斗中扮演的角色。通过 API，页面的类型是 `CHECKOUT | THANKYOU | ERROR | UPSELL | CUSTOM` - 入口页面作为 `CUSTOM` 创建，并通过绑定到漏斗作为 `LANDING` 变成入口页面。

有两个编辑器可用：基于组件的可视化编辑器，其输出是可比较的 JSON，以及用于导入页面的原始 HTML。对于任何将来将进行 A/B 测试或由代理编辑的内容，请优先使用组件编辑器 - JSON 差异可以清晰地审查，HTML 块则不能。

在构建结账页面之前构建入口页面。结账页面决定了实际上可以销售什么以及价格，而首先编写的入口页面会承诺结账无法提供的内容。

## 第 5 步：连接漏斗

- 创建漏斗，然后使用其角色和顺序附加页面。
- 同一个页面可以被多个漏斗引用。域强制执行的唯一唯一性规则是 `stepSlug` 在一个漏斗内是唯一的（并且一个页面在每个漏斗中最多出现一次） - 没有跨漏斗拒绝需要设计。仅在您希望两个漏斗分叉时才克隆入口页面，因为对共享页面的编辑会应用于引用它的每个漏斗。
- `THANKYOU` 和 `ERROR` 如果存在，则在创建时自动绑定现有页面；如果租户没有，则在上线前创建它们。没有错误页面的漏斗在拒绝支付时静默失败。
- 广告活动中的 URL 是入口页面的自身 slug 在商店主机上 - `https://shop.example.com/{page.slug}` - 永远不是 `/n/` 步骤 URL。`/n/{funnelId}/{stepSlug}` 是一个转发重定向，它会找到该步骤，`302` 到下一个步骤的裸页面 slug 并附加 `?funnelId=`，在最后一个步骤上回答 `404 No next step in funnel`。将其指向您的结账页面，您会得到结账，或者如果没有后续内容，则会得到 404 - 无论如何，都不是入口页面。

**`entryStepSlug` 也不是要宣传的 URL。** 它就是 `steps[0]`，并且 `create_funnel` 在您添加任何内容之前会附加感谢页面和错误页面，因此在这种情况下构建的漏斗 `steps[0]` 是感谢页面。

**页面在其自己的裸 slug 上商店主机上提供服务**：`https://{storefront-host}/{page.slug}`。从 `get_funnel` 读取 `steps`，选择 `page.type` 为 `CUSTOM` 的步骤，并宣传该步骤的 `page.slug`。仅在页面绑定到多个漏斗时才附加 `?funnelId={id}`；对于单个绑定，漏斗上下文会自行解析。

**裸 slug 仅在非管理主机上工作。** 中间件在主机不匹配 `ADMIN_DOMAIN` 时将 `/{slug}` 重写为商店渲染器；在管理主机本身上该路径会传递到管理应用程序并 404，这看起来就像未发布的页面。因此，只有在附加商店域名后，才能对仅可通过 `*.workers.dev` 管理主机访问的 Workers 部署获得干净的入口页面 URL - 在购买流量之前附加一个。

**仅使用 API 密钥请求 `/storefront/{slug}` 来验证。** 该前缀在包括管理主机的每个主机上都是公开的，并渲染购物者获得的内容。它仅提供发布的页面 - 草稿 404，而 `get_page` 仍然愉快地返回其 `draftData`。`/preview/{slug}` 会渲染草稿，但需要登录会话，因此 API 密钥无法使用它。在花费钱之前确认 `200` 和预期副本在正文中。

要更改实时页面：`get_page` → 仅更改您打算更改的属性 → `update_page` 不发布 → `get_page` 以进行差异 → 发布。永远不要为单个标题重新生成整个 `draftData` 块；`update_page` 整体替换文档，组件 JSON 包含您未编写且无法重建的属性值。

### REST 不是相同的表面

REST 与 MCP 一样使用 `Authorization: Bearer <api-key>` 标头；没有它，您会得到一个裸的 `401`。

十三种工具也通过 REST 桥接可达，该桥接运行相同的架构和处理器，因此它们不能漂移。七种是 MCP 仅限：`list_funnels`、`get_funnel`、`list_pages`、`get_page`、`list_products`、`deliver_order`、`get_stats`。其中一些在相同路径上有较旧的独立编写的 REST 端点，具有不同的响应形状或参数名称（`GET /products` 接受 `q`，而不是 `search`）。不要假设与同名工具的 REST 端点匹配。

一条路径陷阱：`/api/v1.1/templates` 列出了 **电子邮件** 模板用于设置，而不是 Puck 页面模板。页面模板位于 `/api/v1.1/page-templates`。

## 诚实的运营成本

大声说出而不是让用户在启动后发现：

- **Workers 路径**：没有需要补丁的服务器，但您需要拥有 PostgreSQL 及其备份，并且免费计划限制是每日上限，它们会失败操作而不是向您计费。在流量高峰之前了解您最接近哪个限制。
- **Docker 路径**：升级、备份和正常运行是您自己的责任。架构更改随图像一起提供，必须在升级时应用。
- 支付配置及其 PCI 范围是每个路径上运营者的责任。
- 自托管构建没有支持 SLA。GitHub 上的问题和讨论是渠道。
- 为第一个生产部署预算小时，而不是分钟。两分钟数字是本地 Docker 评估，不是启动。

文档：<https://autonnel.com/docs> · Issues and Discussions: <https://github.com/autonnel/autonnel>
