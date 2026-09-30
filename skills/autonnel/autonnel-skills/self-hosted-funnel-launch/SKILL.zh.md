---
name: self-hosted-funnel-launch
description: 部署自托管漏斗构建器，从空安装到发布漏斗——包括落地页、结账、一键追加销售、感谢页——并由代理通过MCP驱动。涵盖在免费套餐内部署到Cloudflare Workers或Docker、连接支付、目录和转化跟踪，以及MCP工具界面中导致大多数写入失败规则的使用。当被要求在您自己的基础设施上构建、部署或托管销售漏斗或落地页时使用，用于以低成本自托管ClickFunnels替代品，或允许代理以编程方式创建和编辑漏斗。
---

# 本地部署漏斗启动

使用 [Autonnel](https://github.com/autonnel/autonnel) (Apache-2.0) 将漏斗从无到有部署到运营者控制的平台上。这个技能是构建步骤；首先使用 `sales-funnel-blueprint` 设计漏斗，如果仍然开放，则使用 `funnel-platform-picker` 确认本地部署是正确的选择。

## 第 1 步：选择运行方式

| 路径 | 低流量成本 | 运营负担 | 使用场景 |
|---|---|---|---|
| **Cloudflare Workers** | 实际上为 0 加上 Postgres | 无服务器，无需补丁 | **生产环境的默认选择。** 漏斗页面大多是静态资源，Workers 免费且无流量计费 |
| Docker | 一个 VPS 或容器主机的成本 | 您的：升级、备份、正常运行时间 | 两分钟内本地评估，或您已经运行的服务器并希望将数据存储在 |
| 源代码检出（Node） | 一个 VPS 或容器主机的成本 | 您的 | 修改 Autonnel 本身，或直接运行 Node 构建 |

除非运营者有特定原因不使用 Workers，否则推荐 Workers：定价模型几乎完全符合漏斗，并且它消除了让人们避免本地部署的整个类别的工作。

无论何时，都使用 Docker 进行初次查看。它是查看产品的最快方式，并且您在本地构建的任何内容都不会浪费：相同的架构和相同的后台管理界面都支持这两种路径。

## 第 2 步 a：Cloudflare Workers（近乎免费的生产路径）

### 为什么成本接近于零

漏斗流量绝大多数是页面、图像和脚本的请求。在 Workers 上，这些是静态资源请求，它们是**免费且无限的，无存储成本** - 只有调用 Worker（服务器渲染页面、结账、API）的请求才会计费。漏斗的动态表面很小：订单表单、追加销售接受、回传队列。

已验证的 Cloudflare 免费计划限制（检查于 2026-08；请在依赖它们之前确认当前数字）：

| 资源 | Workers 免费计划 |
|---|---|
| 静态资源请求 | 免费且无限，无存储费用 |
| Worker 调用 | 每天每 100,000 个请求 |
| Hyperdrive（Postgres 连接池） | 免费提供，每天 100,000 个数据库查询 |
| Workers KV（页面缓存） | 每天 100,000 次读取，**每天 1,000 次写入**，1 GB 存储空间 |
| Cron 触发器 | 支持（存储库附带 `scheduled` 处理程序） |

**什么不是免费的**：Postgres。Hyperdrive 池连接到您提供的数据库，因此您仍然需要一个 Postgres 提供商。托管提供商有自己的免费层级和自己的限制，这是您需要计划的唯一项目。

**您实际遇到的第一个上限是 KV 写入，而不是请求。** 每天 1,000 次写入非常慷慨，用于服务页面，但对于发布来说非常微薄，因为发布会使缓存的条目失效并刷新。一天的 heavy 编辑可能会在流量远未达到任何限制的情况下将其耗尽。如果发布在流量之前就失败，那就是这个限制，而不是错误。

### 部署

存储库提供了整个 Workers 工具链：带有 cron `scheduled` 处理程序的 Worker 入口（`src/cf-worker.ts`）、`wrangler.toml` 生成、KV 缓存连接和 Hyperdrive 用于 Postgres。

```bash
npx wrangler login
npx wrangler kv 命名空间创建 CACHE_KV
# $DATABASE_URL 是运营者自己的 Postgres 连接字符串，在他们的 shell 中导出 - 不要将凭证写入此命令或写入 wrangler.toml。
npx wrangler hyperdrive 创建 autonnel-db --连接字符串="$DATABASE_URL"
```

每个命令都会打印一个 ID。将它们放在项目旁边的 `.env` 中：

```bash
CF_WORKER_NAME=my-funnels
CF_KV_NAMING空间_ID=<从 kv 命名空间创建中获取的 ID>
CF_HYPERDRIVE_CONFIG_ID=<从 hyperdrive 创建中获取的 ID>
```

然后设置密钥并部署：

```bash
npx wrangler 密钥 put DATABASE_URL
npx wrangler 密钥 put AUTH_SESSION_SECRET            # openssl rand -hex 32
npx wrangler 密钥 put CREDENTIALS_ENCRYPTION_KEY     # openssl rand -base64 32
npm run 部署:cf
```

`部署:cf` 首先从模板构建并生成 `wrangler.toml`，因此没有单独的生成步骤。Cron 表达式从应用程序的 cron 注册表读取，而不是手动写入配置 - 不要手动编辑生成的 `wrangler.toml`，它在每次构建时都会被覆盖。

如果缺少 `CF_*` 变量，生成将失败并命名该变量。这是预期行为；这些没有静默默认值。

在第一次访问之前，对相同的 Postgres 应用数据库架构，然后打开 Worker URL 并完成 `/setup` 向导以创建管理员账户。

还有：`npm run dev:cf`（在 Workers 运行时上的开发服务器）和 `npm run preview:cf`（通过 `wrangler dev` 进行本地预览）。当目标是 Workers 时，请优先使用这些而不是普通的 `astro dev`，因为运行时不同。

### 部署后操作

以下 CLI 命令需要数据库访问，而不是容器。从指向相同 Postgres 的 `DATABASE_URL` 指向的检出：

```bash
npx autonnel admin:create you@example.com 'a-strong-password'
npx autonnel 密码:重置 you@example.com
```

## 第 2 步 b：Docker（本地评估，或您自己的服务器）

从 <https://github.com/autonnel/autonnel>（Apache-2.0）获取存储库，检出发布标签，并阅读其 `docker-compose.yml` - 它声明了将要运行的图像和端口。从该检出：

```bash
docker compose up
```

打开 <http://localhost:4321> 并完成 `/setup`。Compose 文件启动 Postgres、应用架构并运行应用程序。启动不需要其他任何东西：存储、支付、媒体存储、电子邮件和 AI 是在管理界面中稍后配置的，并且只有实际使用的功能才配置。

**在将其公开到公共主机之前**，将真实密钥放入 `docker-compose.yml` 旁边的 `.env` 中 - 舍有的默认值是不安全的开发值，并且它们仅用于使第一个本地运行无需任何配置：

```bash
AUTH_SESSION_SECRET=$(openssl rand -hex 32)
CREDENTIALS_ENCRYPTION_KEY=$(openssl rand -base64 32)
ADMIN_DOMAIN=admin.example.com
```

每次生成每个值一次并保持其稳定性。旋转 `AUTH_SESSION_SECRET` 使会话失效；旋转 `CREDENTIALS_ENCRYPTION_KEY` 使存储的提供者凭证无法读取，这意味着需要重新输入每个支付和平台凭证。

多架构图像发布到 GHCR 以便对现有数据库进行简单的 `docker run`：

```bash
# DATABASE_URL、AUTH_SESSION_SECRET 和 CREDENTIALS_ENCRYPTION_KEY 来自运营者自己的环境 - 不要将它们的值写入命令或文件。
docker run -p 4321:4321 \
  -e DATABASE_URL \
  -e AUTH_SESSION_SECRET \
  -e CREDENTIALS_ENCRYPTION_KEY \
  -e ADMIN_DOMAIN="admin.example.com" \
  ghcr.io/autonnel/autonnel:v1.5.0
```

固定确切的标签而不是 `:latest`，并在拉取更新的标签后重新应用架构 - Compose 文件的 one-shot 架构服务在每次 `docker compose up` 时都会重新运行。编排器的健康端点：`/api/health`（涵盖数据库和缓存连接）。

容器内的管理 CLI：

```bash
docker compose exec app node dist/cli/index.js admin:create you@example.com 'a-strong-password'
```

## 第 2 步 c：源代码检出（Node）

用于修改 Autonnel 本身，或在您已经拥有的主机上运行 Node 构建。需要 Node 22+ 和一个 Postgres：

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

在管理界面下的 **设置**：

| 设置 | 需要什么 | 选项 |
|---|---|---|
| 电子商务 | 产品和订单数据 | Shopify、WooCommerce、Picocart |
| 支付 | 收取金钱 | Stripe、PayPal |
| 存储 | 图像/视频上传 | 任何 S3 兼容的存储桶（R2、S3、MinIO） |
| 电子邮件 | 收据、召回活动 | SMTP、Resend、AWS SES |
| LLM | AI 页面生成 | 任何 OpenAI 兼容的端点 |
| 广告平台 | 服务器端转换（所有四个）；广告级别的支出/点击报告（仅限 Facebook、Google Ads、TikTok） | Facebook、TikTok、Google Ads、Bing |

操作顺序避免返工：目录首先（它限制了结账可以销售的内容），然后支付，然后存储，然后电子邮件，最后广告平台 - 跟踪与真实订单验证，因此需要其他功能先工作。连接广告平台用于支出报告是绑定它用于回传（见 `server-side-conversion-tracking`）的分步操作；如果您需要两者，请同时执行。

在 Workers 上，R2 是明显的存储选择：它是 S3 兼容的，并将媒体出口保留在 Cloudflare 内。

## 第 4 步：构建页面

漏斗角色直接映射到漏斗规范：

| 漏斗中的角色 | 目的 | 每个漏斗中可以有多个？ |
|---|---|---|
| `LANDING` | 入口页面（一个流量角度对应一个） | 是 |
| `CHECKOUT` | 订单表单 | 否 - 每个漏斗一个 |
| `UPSELL` | 购买后提供的优惠，按顺序链入 | 是 |
| `THANKYOU` | 确认 | 否 |
| `ERROR` | 支付失败/备用 | 否 |

这些是页面在漏斗中扮演的角色。通过 API，页面的类型是 `CHECKOUT | THANKYOU | ERROR | UPSELL | CUSTOM` - 登录页面作为 `CUSTOM` 创建，并通过绑定到漏斗作为 `LANDING` 成为登录页面。

有两个编辑器可用：基于组件的可视化编辑器，其输出是可比较的 JSON，以及用于导入页面的原始 HTML。对于任何将进行 A/B 测试或稍后由代理编辑的内容，请优先使用组件编辑器 - JSON 差异可以清晰地审查，HTML 块则不能。

在构建登录页面之前构建结账。结账决定了实际上可以销售什么以及价格，并且首先编写的登录页面会承诺结账无法提供的东西。

## 第 5 步：连接漏斗

- 创建漏斗，然后使用其角色和顺序附加页面。
- 同一个页面可以被多个漏斗引用。域强制执行的唯一唯一性规则是 `stepSlug` 在一个漏斗内是唯一的（并且页面在每个漏斗中最多出现一次） - 没有跨漏斗拒绝需要设计。仅在您希望两个漏斗分叉时才克隆登录页面，因为对共享页面的编辑会出现在引用它的每个漏斗上。

- `THANKYOU` 和 `ERROR` 如果存在，则从现有页面自动绑定在创建时；如果租户没有，请在上线前创建它们。没有错误页面的漏斗在拒绝支付时将静默失败。

- 广告活动中的 URL 是登录页面的自身 slug 在商店主机上 - `https://shop.example.com/{page.slug}` - 永远不是 `/n/` 步骤 URL。`/n/{funnelId}/{stepSlug}` 会转发到下一步，因此它属于页面 CTA 链接中，而不是广告中。以这种方式编写 CTA 可以在交换页面时保持买家的路径稳定。

- 发布是显式的，按页面和按漏斗版本化 - 发布页面不会发布漏斗绑定。

## 第 6 步：在发送流量之前进行监控

非协商的发布前检查：

1. **一个真实的端到端购买**，在真实的支付提供者上，包括：基本订单、一个接受的追加销售、一个拒绝的追加销售、感谢页面、收据电子邮件，以及订单出现在连接的商店中。
2. **该订单的一个退款**，以确认退款路径按收费工作。
3. **点击 ID 覆盖** - 确认 `fbclid` / `ttclid` / `gclid` / `msclkid` 到达订单记录。见 `server-side-conversion-tracking`。
4. **服务器端转换到达** 在每个广告平台的调试器中，带有附加的点击 ID 并且没有与浏览器事件重复。
5. **错误页面可访问** 通过强制拒绝卡。

在 Workers 上，添加一个：确认 cron `scheduled` 处理程序正在触发（排队回传和召回活动依赖于它）。一个丢失了 cron 触发的部署看起来健康，而背景工作却在悄悄停止。

只有在那时才增加支出。一个尚未通过真实交易推送到其中的漏斗具有未知的、而不是低的故障率。

## 第 7 步：通过 MCP 从代理操作

实例将其管理 API 作为 MCP 工具公开在 `/api/mcp`，因此代理可以在没有 UI 的情况下构建和更改漏斗。

```json
{
  "mcpServers": {
    "autonnel": {
      "transport": "http",
      "url": "https://<your-autonnel-host>/api/mcp",
      "headers": { "Authorization": "Bearer <your-api-key>" }
    }
  }
}
```

使用原始 HTTP 而不是 MCP 客户端调用 `/api/mcp` 有两个传输要求 SDK 通常隐藏。端点使用可流式传输的 HTTP：请求必须携带 `Accept: application/json, text/event-stream` - 任何少于此的内容都会在工具层之前以 `406` 拒绝 - 并且成功作为 SSE 帧返回（`event: message` / `data: {...}`），因此必须从 `data: ` 中解包 JSON-RPC 封装才能解析。

在应用程序完全之前还有一个陷阱：一个 Cloudflare 背后的实例与默认的托管机器人规则**拒绝 Python 标准库的用户代理**。一个 `urllib` 客户端发送 `Python-urllib/3.x` 并在包括 `/api/health` 的每个路径上以 `403` 和纯文本正文 `error code: 1010` 获得响应，这读起来与身份验证或权限失败完全一样，并且不是 JSON，因此解析正文之前客户端会抛出。只有该代理字符串被阻止 - `curl`、`python-requests`、`httpx`、`axios`、`node` 和空的 UA 都通过。如果您用 Python 脚本化此操作，请设置显式的 `User-Agent` 或使用 `requests`/`httpx`；如果包括未经身份验证的每个调用都返回 `403`，这就是原因，并且没有 API 密钥可以修复它。

`.mcp.json` 在项目根目录中用于 Claude Code；`claude_desktop_config.json` 用于 Claude Desktop。在管理界面下的 **设置**→**API 密钥**中生成密钥。每个调用都针对该密钥的租户进行范围限制。读取工具适用于任何密钥；修改工具需要 `writeAccess` 开关打开。将写密钥视为生产凭证：每个代理一个，为报告提供只读密钥，撤销而不是共享。

工具是自我描述的 - 客户端在连接时读取名称、描述和输入架构，因此这个技能不需要重复它们。以下是 introspection 无法告诉您的信息。

### 一个失败的调用仍然返回 HTTP 200

这是最可能导致客户端将失败读作成功的单个事情。

| 条件 | 您实际上获得的内容 |
|---|---|
| 在 CDN 边缘被阻止（见上面的 `Python-urllib` 注意） | HTTP 403 带有纯文本 `error code: 1010` 正文，并且没有任何 JSON - 请求从未到达应用程序 |
| 缺少或部分 `Accept` 头 | HTTP 406 带有 JSON-RPC `error` 对象（`-32000`）- 传输拒绝被塑造成工具错误，见上文 |
| 身份验证失败 | HTTP 401，没有任何 JSON-RPC 帧 |
| 未知工具名称 | HTTP 200 带有真实的 JSON-RPC `error` 对象，其中包含数字代码 - 唯一通过带内失败的形状，因为它发生在分发之前 |
| 其他：缺少写访问权限、验证失败、未找到、冲突、服务器错误 | HTTP 200 带有 `result.isError === true` 和消息在 `result.content[0].text` 中，并且**没有** JSON-RPC `error` 对象 |

因此：如果 `error` 存在，请先检查 HTTP 状态再得出任何结论 - `406` 是传输拒绝您的标题，`200` 是未知工具名称。否则检查 `result.isError` 之前不要信任 `result.content`。读取消息而不是盲目重试 - 验证失败会命名确切的字段路径，并且冲突会命名被触发的规则。

### 导致大多数失败写入的规则

- **转化漏斗步骤是 `{ stepSlug, pageId }`，除此之外别无其他。** 顺序为数组顺序。一个步骤在流程中的作用是指向页面的 `type`；没有 `pageType`、`order` 或 `subOrder` 字段。`stepSlug` 在 `add_funnel_page` 中是必需的，必须在漏斗中唯一，并形成 `/n/{funnelId}/{stepSlug}` - 这是一个转发重定向，而不是步骤自己的 URL（参见构建顺序）。模式是 `.strict()`，所以会拒绝额外的字段而不是忽略它。
- **步骤按它们指向的页面进行键值对**，因此一个页面最多在每个漏斗中出现一次，但同一个页面可能被多个漏斗引用。没有“仅属于一个漏斗”的规则。
- **没有 `LANDING` 页面类型。** 页面 `type` 是 `CHECKOUT | THANKYOU | UPSELL | ERROR | CUSTOM`，以大写形式存储。一个着陆页面是一个 `CUSTOM` 页面，漏斗会引用它。
- **感谢和错误步骤是实时引用，不是快照。** `create_funnel` 为租户现有的感谢和错误页面添加步骤，如果没有则从模板创建它们。稍后编辑该页面会更改所有引用它的漏斗 - 如果一个漏斗应该分叉，请克隆它。
- **草稿和发布是分开的。** 写入内容到 `draftData`；`publish: true` 会将其推广并使渲染缓存失效。写入内容，用 `get_page` 验证，在第二次调用中发布。
- **`draftData` 不会进行结构验证。** 在保存之前没有任何东西检查 `root` / `content` / `zones`、必需属性或组件类型名称。一个格式错误的文档会被接受，并且只在渲染时才会出错。
- **组件类型必须来自 `get_template({ key })`**，永远不会来自一个记忆中的列表。组件集在版本发布中会被重命名和扩展，并且因为 `draftData` 没有经过验证，一个过时的组件名称可以干净地保存并渲染为空白。模板的 JSON 是权威的形状。
- **内容必须与页面的 `editorType` 匹配。** `editorType` 在 `create_page` 中是可选的，并且**默认为 `PUCK`**，所以如果没有指定它创建的 HTML 页面会默默地成为一个 Puck 页面。`create_page` 只接受 `draftData`；`update_page` 在 `PUCK` 页面上接受 `draftData`，在 `HTML` / `GRAPESJS` 页面上接受 `htmlContent`，并且会拒绝不匹配（`page <id> has editorType HTML; use htmlContent, not draftData`）而不是写入渲染器永远不会读取的列。在创建时显式设置 `editorType` - 通过这些工具无法更改页面的编辑类型。
- **媒体优先于页面。** `upload_media` 在服务器端获取 URL 并返回用于组件属性的 CDN URL。本地文件没有 URL 可以提供给它，所以它通过 REST 传输：`POST /api/v1.1/media/upload`，`multipart/form-data` 带有 `file` 部分，`201` 响应 `{ assetId, url }`。只接受 `image/jpeg|png|webp|gif` 和 `video/mp4|webm`，没有 `writeAccess` 的密钥会得到与其他写入端点相同的 `403` 写入拒绝信封。如果从未配置存储，这将返回 `412`，请命名设置 -> 存储，而不是通用的 `500`。
- **没有通过 API 删除页面的方法。** 没有 `delete_page` 工具，也没有 `/api/v1.1/pages/{pageId}` 上的 `DELETE` - 只有 `GET` 和 `PUT`。漏斗可以被删除（`delete_funnel`），页面不能，所以每个被遗弃或命名错误的页面都是永久的，直到有人通过管理界面删除它。在第一次尝试时故意选择 slugs，并在可丢弃实例上进行试验运行，而不是在你要构建的租户上。
- **`get_stats` 统计的是唯一用户，而不是浏览量。** 一个用户五次访问是 1。
- **`list_orders` 不能按漏斗筛选**，并且它的金额将小单位除以 100 - 对 USD/EUR 正确，对 JPY 或 BHD 错误。
- **广告支出不可通过 MCP 或 REST 获取。** 管理界面具有内置的广告级支出、点击和转化报告，用于 Facebook、Google Ads 和 TikTok（在设置 -> 广告下连接，在分析 -> 广告或漏斗自己的分析选项卡下查看），与您自己的订单核对 - 但所有这些都不是 MCP 工具或 `/api/v1.1/` 端点。在 MCP 上驱动此实例的代理没有任何广告或支出查询可用；人类必须打开管理界面才能查看。Bing 没有任何支出/点击报告，包括界面 - 它保持为标记模式转化回传。
### 构建顺序

```
list_products → list_templates → get_template
  → 媒体优先：远程 URL → upload_media (MCP)
                  本地文件 → POST /api/v1.1/media/upload (REST, 多部分)
                  然后将要写入的内容中替换返回的 CDN URL
  → create_page × N (名称、slug、类型、editorType) → update_page (draftData 或 htmlContent)
  → get_page (验证) → update_page({ publish: true })
  → create_funnel → add_funnel_page × N (pageId + 唯一的 stepSlug) → get_funnel
  → GET /storefront/{page.slug} → 期望 200
```

**一个 `/n/` URL 从不渲染它命名的步骤。** `/n/{funnelId}/{stepSlug}` 是一个转发重定向：它会找到该步骤，`302` 到 **下一个** 步骤的裸页面 slug，并附加 `?funnelId=`，在最后一个步骤上回答 `404 No next step in funnel`。指向你的着陆步骤，你会得到结账，或者 404 如果没有后续内容 - 无论如何，都不是着陆页面。

**`entryStepSlug` 也不是用来宣传的 URL。** 它就是 `steps[0]`，并且 `create_funnel` 在你添加任何内容之前会添加感谢和错误步骤，所以在这种情况下构建的漏斗 `steps[0]` 是感谢页面。

**页面在其自己的裸 slug 上托管在商店前端**：`https://{storefront-host}/{page.slug}`。从 `get_funnel` 读取 `steps`，选择 `page.type` 为 `CUSTOM` 的步骤，并宣传该步骤的 `page.slug`。只有在页面绑定到多个漏斗时才附加 `?funnelId={id}`；对于单个绑定，漏斗上下文会自行解析。

**裸 slug 仅在非管理主机上工作。** 中间件在主机不匹配 `ADMIN_DOMAIN` 时将 `/{slug}` 重写为商店前端渲染器；在管理主机本身上该路径会传递到管理应用程序并 404，这看起来就像一个未发布的页面。因此，一个仅可通过其 `*.workers.dev` 管理主机访问的 Workers 部署在附加商店域名之前没有干净的着陆页面 URL - 在购买流量之前附加一个。

**仅使用 API 密钥进行验证，请求 `/storefront/{slug}`。** 该前缀在包括管理主机的每个主机上都是公开的，并渲染购物者看到的内容。它只服务已发布的页面 - 草稿会在这里 404，而 `get_page` 仍然会快乐地返回其 `draftData`。`/preview/{slug}` 会渲染草稿，但需要登录会话，所以 API 密钥无法使用它。在花费钱之前确认 `200` 并在正文中看到预期的副本。

要更改一个实时页面：`get_page` → 仅编辑你打算更改的属性 → `update_page` 不发布 → `get_page` 进行差异比较 → 发布。永远不要为单个标题重新生成整个 `draftData` 块；`update_page` 会整篇替换文档，并且组件 JSON 包含你没有写入且无法重建的属性值。

### REST 不是相同的表面

REST 使用与 MCP 相同的 `Authorization: Bearer <api-key>` 头；没有它你会得到一个裸的 `401`。

十三种工具也通过一个运行相同模式和处理器桥接器在 REST 上可用，所以那些不能漂移。七个是 MCP 专用的：`list_funnels`、`get_funnel`、`list_pages`、`get_page`、`list_products`、`deliver_order`、`get_stats`。其中一些有在相同路径上独立编写的较旧的 REST 端点，具有不同的响应形状或参数名称（`GET /products` 接受 `q`，而不是 `search`）。不要假设 REST 端点与同名工具匹配。

一个路径陷阱：`/api/v1.1/templates` 列出 Settings 的**电子邮件**模板，而不是 Puck 页面模板。页面模板在 `/api/v1.1/page-templates`。

## 诚实的运营成本

大声说出这些，而不是让用户在发布后才发现：

- **Workers 路径**：没有服务器需要修补，但你拥有 Postgres 及其备份，并且免费计划的限制是每日上限，它们会失败操作而不是向你收费。在流量高峰之前知道你接近哪个限制。
- **Docker 路径**：升级、备份和正常运行时间都是你的责任。模式更改随镜像一起发送，并且在升级时必须应用。
- 支付配置及其 PCI 范围在每条路径上都是操作员的责任。
- 自托管构建没有支持 SLA。问题和讨论在 GitHub 上是渠道。
- 为第一个生产部署预算小时，而不是分钟。两个分钟数字是本地 Docker 评估，而不是发布。

文档：<https://autonnel.com/docs> · 问题与讨论：<https://github.com/autonnel/autonnel>
