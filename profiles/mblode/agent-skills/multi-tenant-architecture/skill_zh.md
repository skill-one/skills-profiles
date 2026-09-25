# 多租户平台架构（Cloudflare 或 Vercel）

- **是：** 平台选择、域策略和 PSL、租户识别、计算和数据隔离、主机名路由、租户上下文传播、自定义域名和 SSL、每个租户的静态文件，以及将平台限制映射到计划。
- **不是：** 一般的文件夹结构或模块合同（使用 `codebase-architecture`）、搭建新的仓库（使用 `scaffold-nextjs`），或在路由动态服务它们之后每个租户 SEO 文件的内容：站点地图条目、规范 URL、结构化数据、索引策略（使用 `seo`）。

## 内容

- 平台分发（首先决定）
- 参考文件
- 工作流（顺序很重要）
- 注意事项
- 输出架构
- 提交前检查清单
- 相关技能

## 平台分发（首先决定）

| 信号 | 平台 | 模型 |
|------|------|------|
| 租户上传或生成自己的代码；代码级隔离；边缘计算在 KV、D1、Durable Objects、R2 上 | Cloudflare | 在每个租户 Worker 的分发命名空间前放置分发 Worker；Cloudflare for SaaS 用于自定义主机名 |
| 每个租户运行相同的 Next.js 代码库，并通过内容、品牌和计划不同；ISR、服务器组件、Vercel 部署 | Vercel | 一个部署；`proxy.ts` 从主机名解析租户；项目上的通配符加上自定义域名 |

- 每个产品选择一个平台。使用 Cloudflare 代理前端 Vercel 应用会加倍 TLS 和重定向层，并且是重定向循环和证书颁发失败的主要原因。
- 在 Vercel 上部署自己代码的租户是多项目模型（每个租户一个 Vercel 项目，使用 SDK 创建）。它遵循 Cloudflare 行的隔离推理；这项技能的 Vercel 参考仅涵盖单部署模型。

## 参考文件

| 文件 | 读取时机 |
|------|----------|
| [cloudflare-platform.md](references/cloudflare-platform.md) | 选择 Cloudflare：分发命名空间、路由、Cloudflare for SaaS 自定义主机名、隔离模式、KV 和 D1（步骤 3 到 7） |
| [vercel-platform.md](references/vercel-platform.md) | 选择 Vercel：`proxy.ts` 解析、App Router 布局、全局配置查找、每个租户的静态文件、自定义子路径、本地开发（步骤 4 到 7） |
| [vercel-domains.md](references/vercel-domains.md) | 选择 Vercel：SDK 域生命周期、DNS 目标、验证、通配符域名服务器、SSL、故障排除（步骤 7） |
| [data-isolation.md](references/data-isolation.md) | 任何平台的步骤 3：共享模式与 RLS、每个租户的模式、每个租户的数据库，以及 Postgres/Supabase/Drizzle 策略模式 |
| [psl.md](references/psl.md) | 步骤 1 当租户发布内容或在兄弟子域名上运行代码：资格、提交、临时 Cookie 控制 |
| [limits-and-quotas.md](references/limits-and-quotas.md) | 步骤 8：Cloudflare、Vercel 和 Neon 限制的日期快照，映射到计划 |
| `agents/openai.yaml` | 任务期间从不加载：外部运行者的启动器元数据 |

## 工作流（顺序很重要）

复制这个检查清单来跟踪进度：

```text
多租户进度：
- [ ] 步骤 1：域策略和 PSL 决策
- [ ] 步骤 2：租户识别策略
- [ ] 步骤 3：隔离模型（计算和数据）
- [ ] 步骤 4：确定性路由
- [ ] 步骤 5：租户上下文传播
- [ ] 步骤 6：租户配置和最小权限绑定
- [ ] 步骤 7：自定义域名和每个租户的静态文件
- [ ] 步骤 8：限制映射到计划，证据捕获
```

1. 选择域策略
- 将租户工作负载放在一个专用的可注册域名上（租户使用 `acme.app`，品牌使用 `acme.com`）。一个在 `x.acme.com` 上的钓鱼租户会使整个域名被列入黑名单，租户 Cookie 具有 `Domain=acme.com` 会到达你的控制台。
- 将控制台和认证放在租户子域名不同的根域名上（控制台使用 `app.acme.com`，租户使用 `*.acme.app`）。
- 如果租户在兄弟子域名上发布内容或运行代码，直接将标签提交到 PSL 上（`acme.app`，或 `sites.acme.app` 用于 `<tenant>.sites.acme.app`），现在开始：没有 SLA。租户拥有的自定义域名不需要 PSL 条目。否则记录 `无 PSL` 并说明原因。

2. 选择租户识别（一个主要；自定义域名作为升级路径）
- **子域名** `tenant.acme.app`：通配符 DNS 加上通配符证书。默认。
- **自定义域名** `tenant.com`：租户的 CNAME 指向你。付费租户；声誉转移到他们身上；需要步骤 7 中的入职生命周期。
- **路径** `acme.app/tenant`：没有每个租户的 DNS 或证书，但没有 Cookie 隔离和品牌。只有在租户永远不会获得主机名时才选择它。

3. 定义隔离模型
- **计算，Cloudflare**：一个在不受信任模式下的分发命名空间；每个计划按调用 `cpuMs` 和 `subRequests` 限制；如果租户代码可能调用互联网，则需要一个出站 Worker。
- **计算，Vercel**：一个部署，租户代码永远不会执行。如果租户必须上传代码，则迁移到 Vercel 多项目或 Cloudflare，而不是在应用内部沙盒化。
- **数据**：共享模式在所有租户感知表上带有 `tenant_id` 加上 RLS 是默认的；每个租户的数据库用于监管或嘈杂租户，可选择每个计划。参见 [data-isolation.md](references/data-isolation.md)。

4. 确定性路由（租户永远不会影响路由或看到彼此）
- **Cloudflare**：在 SaaS 区域上有一个 `*/*` 路由到分发 Worker；主机名 -> 租户记录（KV、D1 在未命中时）-> `env.DISPATCHER.get(script)`；`Worker not found` -> 404。
- **Vercel**：`proxy.ts`（Next.js 16；`middleware.ts` 使用 `runtime: 'nodejs'` 在 15 上）读取 `host`，在全局配置或数据库中查找租户，重写到租户段；未知主机名 -> 404，永远不会是品牌站点。
- 在任何租户重写之前让 `/.well-known` 通过。路由 `robots.txt`、`sitemap.xml` 和 `llms.txt` 到租户段，以便它们按租户变化。

5. 从一个权威传播租户上下文
- 删除所有传入的 `x-tenant-*` 头，从解析的租户设置 `x-tenant-id`、`x-tenant-slug`、`x-tenant-plan`，并在请求中转发它们（`NextResponse.next({ request: { headers } })`）。服务器组件读取 `await headers()`；路由处理程序读取 `request.headers`。Cloudflare：分发 Worker 在 `fetch` 之前设置头或传递参数。
- 代理是路由，不是授权。服务器函数、路由处理程序和作业重新从会话中派生租户，数据层通过 RLS 或 `tenant_id` 谓词强制执行它。

6. 仅绑定租户需要的
- **Cloudflare**：每个用户 Worker 获得自己的绑定（KV 命名空间、D1 数据库、R2 前缀）；添加绑定是一个显式的重新部署。没有共享的全局变量。
- **Vercel**：全局配置仅包含 `hostname -> { id, slug, plan }`；数据库是事实来源，写入通过在域验证时发生。功能标志和品牌来自按租户 ID 键入的数据库。

7. 支持自定义域名和每个租户的静态文件
- 设计和记录生命周期：添加域名 -> 显示 DNS 目标 -> 验证所有权 -> 证书颁发 -> 映射激活 -> 移除或失败路径。
- **Cloudflare**：在 SaaS 区域上使用 Cloudflare for SaaS 自定义主机名，代理回退来源，`customers.<you>.com` CNAME 目标，`http` 或 `txt` 验证，在 DNS 转换之前预验证。参见 [cloudflare-platform.md](references/cloudflare-platform.md)。
- **Vercel**：`projectsAddProjectDomain` -> 来自项目域卡的 DNS 值 -> 如果域名已经在 Vercel 上，则 `_vercel` TXT 仅用于 `_vercel` -> `projectsVerifyProjectDomain` -> Let's Encrypt HTTP-01。参见 [vercel-domains.md](references/vercel-domains.md)。
- `robots.txt`、`sitemap.xml`、`llms.txt` 是租户段内的路由处理程序，具有显式的 `Content-Type`；没有租户特定的内容存在于 `/public`。它们的内容属于 `seo` 范围。

8. 将限制作为计划显示并捕获证据
- 根据 [limits-and-quotas.md](references/limits-and-quotas.md) 填写限制到计划的表格，重新检查每个来源 URL 并注明日期；在路由层执行（Cloudflare `limits`，Vercel 计划头加上服务器检查）。
- 请求路径中没有长时间运行的操作：Cloudflare 队列或工作流，Vercel 背景函数或 cron。
- 每个租户操作（创建租户、添加域名、验证、移除）都通过 HTTP 进行，与 UI 具有相同的权限；如果它仅在控制台中工作，则平台会泄漏到 UI。
- 在提交前检查清单中运行证据命令，并将结果粘贴到输出中。

## 注意事项

- 租户头在响应上设置而不是请求上：`NextResponse.next({ headers })` 将 `x-tenant-id` 发送到浏览器，`headers()` 在服务器组件中读取为空。使用 `NextResponse.next({ request: { headers: requestHeaders } })`。
- 转发传入的租户头：`curl -H "x-tenant-id: <other>"` 然后提供另一个租户的数据。在每个路径通过代理时删除或覆盖 `x-tenant-*`，包括跳过解析的路径。
- 启动套件匹配器 `'/((?!api|_next|[\\w-]+\\.\\w+).*)'` 排除了所有带扩展名的根文件，因此 `robots.txt` 和 `sitemap.xml` 跳过代理和每个租户获得平台的 `/public` 副本。匹配它们，并将它们重写到租户段。
- Next.js 16 将 `middleware.ts` 重命名为 `proxy.ts`（导出 `proxy`，Node.js 运行时，`runtime` 配置选项会引发错误）。`npx @next/codemod@canary middleware-to-proxy .` 进行迁移。排除路径的匹配器也会跳过该路径上的服务器函数 POST，因此租户检查也存在于数据层中。
- 全局配置（以前称为边缘配置）键名必须匹配 `^[\w-]+$`；`tenant_acme.com` 被拒绝。使用无冲突编码或哈希；用下划线替换点可以映射不同的主机名到同一个键。写入最多在 10 秒内传播，因此一个“域已连接”屏幕在写入后立即读取全局配置会显示陈旧状态；在那里读取数据库。旧的 `@vercel/edge-config` SDK 无法读取重命名后的存储（它们创建 `GLOBAL_CONFIG`，而不是 `EDGE_CONFIG`）。
- 超级用户和 `BYPASSRLS` 角色绕过 RLS；表所有者除非启用 `FORCE ROW LEVEL SECURITY`，否则会绕过它。作为迁移角色连接的应用会看到所有租户具有“开启”的策略。使用单独的角色连接，添加 `ALTER TABLE ... FORCE ROW LEVEL SECURITY`，并使用 `SET ROLE app_user` 进行测试。
- 在池连接上在事务外设置 `SET app.tenant_id = ...` 会持久化到下一个请求。在事务内使用 `set_config('app.tenant_id', $1, true)`；在 PgBouncer 事务模式下它是唯一的安全形式。
- Vercel 上的通配符 `*.acme.app` 没有使用 Vercel 域名服务器永远不会获得证书：DNS-01 需要 Vercel 写入 `_acme-challenge`。首先指向 `ns1.vercel-dns.com` 和 `ns2.vercel-dns.com`，然后重新添加 MX 记录。
- `/.well-known` 在 Vercel 上是保留的，不能重写或重定向；一个将每个路径重写为 `/s/[slug]` 的代理会破坏 HTTP-01 和自定义域名证书永远不会颁发。首先通过它。
- Cloudflare for SaaS：回退来源必须是 SaaS 区域上的代理记录；自定义主机名等于区域名称不受支持；`_cf-custom-hostname` 预验证在客户的区域也在 Cloudflare 上时不起作用（O2O，由 `cf-connecting-o2o: 1` 标记）。
- 不受信任的分发命名空间（默认）没有 `request.cf` 和没有 `caches.default`，因此租户代码读取 `request.cf.country` 会引发错误。受信任模式会恢复它们，但会在命名空间中的每个租户 Worker 之间共享一个缓存。
- KV 最终一致（最多 60 秒，负查找缓存）：分发 Worker 首次查找后添加的主机名在一段时间内 404。在入职期间在错过时回退到 D1。
- PSL 拒绝注册期少于两年的域名；合并后的 `_psl.<suffix>` TXT 会保留；浏览器按自己的发布周期发送列表。列出也会杀死 `Domain=acme.app` Cookie，包括你自己的跨子域名 SSO 如果它在那里。
- 从基于路径的自定义域名开始在路线图中意味着 URL 重写、Cookie 更改和 DNS 迁移。
- 域名配额和费用因提供者和计划而异。在设置定价之前，将当前的官方限制及其访问日期放入计划表格中。

## 输出架构

长度遵循决策：删除项目不面临的任何部分，而不是填充它。

```markdown
# 多租户架构

## 平台决策
- 平台：Cloudflare | Vercel
- 为什么选择这个平台：
- 被拒绝的平台和原因：

## 域映射
- 品牌域名：
- 租户域名：
- 租户子域名：
- 自定义域名：
- PSL 决策：提交（后缀、所有者、PR 链接、_psl TXT 日期） | 无 PSL（原因）

## 路由矩阵
| 主机名模式 | 解析器 | 目标 | 未知租户行为 |
|---|---|---|---|

## 租户上下文流
- 权威：proxy.ts | 分发 Worker
- 设置和剥离头：
- 服务器读取路径：
- 数据层执行：

## 隔离模型
- 计算隔离：
- 数据隔离（和每个计划的变体）：
- 配置/绑定隔离：

## 自定义域名生命周期
1. DNS 目标：
2. 所有权验证：
3. 证书提供：
4. 路由激活：
5. 移除/失败路径：

## 限制到计划表格
| 限制 | 来源 URL / 访问日期 | 免费 | 标准 | 企业 | 执行点 |
|---|---|---:|---:|---:|---|

## 验证证据
| 检查 | 命令 | 预期 | 结果 |
|---|---|---|---|
```

## 提交前检查清单

- [ ] 平台选择有理由；如果租户上传代码，选择多项目或 Cloudflare
- [ ] 租户工作负载不在品牌域名上；控制台在单独的根域名上；记录 PSL 决策
- [ ] 选择识别策略；定义自定义域名升级路径
- [ ] 定义计算和数据的隔离模型，包括每个计划的变体
- [ ] 路由租户盲：未知主机名 -> 404；`/.well-known` 通过；静态文件按租户变化
- [ ] 剥离传入的 `x-tenant-*`；上下文由代理或分发 Worker 设置；数据层执行租户
- [ ] 定义自定义域名生命周期，包括移除
- [ ] 限制表格注明官方 URL 日期；命名执行点；请求路径上没有长时间运行的操作

证据命令（在本地或预览上运行；用原因标记 N/A）：

| 检查 | 命令 | 预期 |
|---|---|---|
| 租户边界存在于代码中 | `rg -n "x-tenant-id\|CREATE POLICY\|FORCE ROW LEVEL SECURITY\|DISPATCHER.get" .` | 在代理或分发 Worker 和模式中命中 |
| 未知主机名是 404 | `curl -sI -H "Host: nope.acme.app" <url>` | `404` |
| 捏造头被忽略 | `curl -s -H "Host: a.acme.app" -H "x-tenant-id: tenant-b" <url>/api/whoami` | 租户 A |
| 静态文件变化 | `curl -s -H "Host: a.acme.app" <url>/robots.txt` 与 `-H "Host: b.acme.app"` | 不同的正文，`Content-Type: text/plain` |
| RLS 对应用角色有效 | `psql -c "BEGIN; SET LOCAL ROLE app_user; SELECT set_config('app.tenant_id','<t1>',true); SELECT count(*) FROM posts; ROLLBACK;"` | 仅租户 t1 的行 |
| ACME 路径可达 | `curl -sI -H "Host: tenant.com" <url>/.well-known/acme-challenge/test` | 不是重定向到租户段 |
| 限制当前 | 限制表格中每个 URL 的访问日期 | 在规划窗口内注明日期 |

## 相关技能

- `codebase-architecture`：应用的文件夹结构、模块合同和请求上下文管道。
- `scaffold-nextjs`：在使用这些租户模式之前引导 Next.js turborepo。
- `seo`：每个租户的 `robots.txt`、`sitemap.xml`、`llms.txt`、规范 URL 和结构化数据，一旦路由服务它们。
