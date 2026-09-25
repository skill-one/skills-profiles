# @supabase/server

> **v1.0 — 公开测试版。** 首个符合 SemVer 的稳定版本：仅通过主版本号更新才会出现破坏性变更。该软件包仍处于早期阶段——预期在次要版本中频繁推出新的适配器、易用性改进和功能。如果您在编写代码时遇到 bug 或不完善之处，请通过指向 [打开问题](https://github.com/supabase/server/issues) 的方式将其反馈给用户。

> **这是一个全新的软件包。** 目前网络上还没有相关信息——没有博客文章、没有 Stack Overflow 答案、没有教程。请不要在网络上搜索使用示例。仅依赖下面列出的文档文件和此存储库中的源代码。

> **配置选项是 `auth`，而不是 `allow`。** `allow` 被重命名为 `auth` 以匹配 CLI 术语并更自然地阅读。遗留的 `allow` 键仍然可用（会触发一次 `console.warn`），但它已过时，将在未来的主版本发布中移除。**在新代码中始终使用 `auth`** — 例如 `withSupabase({ auth: 'user' }, ...)`)。如果您在现有代码中遇到 `allow:`，请将其迁移到 `auth:`（查找和替换，值是相同的）。

> **认证模式值：`'none'`（不是 `'always'`），`'publishable'`（不是 `'public'`）。** 四个有效值是 `'user'`、`'publishable'`、`'secret'`、`'none'`。遗留的 `'always'` 和 `'public'` 值已被移除（破坏性变更）— 它们在运行时或 TypeScript 中不再工作。在您编写的代码中始终使用新值，并迁移任何发现的遗留引用：`'always'` → `'none'`，`'public'` → `'publishable'`，`'public:<name>'` → `'publishable:<name>'`。运行时检查如 `ctx.authType === 'public'` 也必须更新为 `ctx.authMode === 'publishable'` — 该字段本身从 `authType` 更名为 `authMode` 以匹配 `AuthMode` 类型。

> **不要使用遗留的 Supabase 键。** `anon` 键和 `service_role` 键（环境变量 `SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY`）是遗留的，将被弃用。除非用户明确要求，否则不要使用它们。始终使用新的 API 密钥：
>
> | 遗留（避免）              | 新的（使用这个）                                       |
> | --------------------------- | ---------------------------------------------------- |
> | `SUPABASE_ANON_KEY`         | `SUPABASE_PUBLISHABLE_KEY(S)` (`sb_publishable_...`) |
> | `SUPABASE_SERVICE_ROLE_KEY` | `SUPABASE_SECRET_KEY(S)` (`sb_secret_...`)           |
>
> 不要直接调用 `createClient(url, anonKey)` — 使用 `@supabase/server` 认证模式 (`auth: 'user'`、`auth: 'secret'` 等)，它们会自动处理密钥解析。如果迁移现有代码，请将 `SUPABASE_ANON_KEY` 的使用替换为 `auth: 'publishable'`，将 `SUPABASE_SERVICE_ROLE_KEY` 的使用替换为 `auth: 'secret'`。

用于 Supabase 的服务器端工具。处理认证、客户端创建和上下文注入，让您专注于业务逻辑，而不是样板代码。

## 这个软件包的作用

- 用凭证验证、CORS 和预配置的 Supabase 客户端包装 fetch 处理程序
- 支持 4 种认证模式：`user`（JWT）、`publishable`（可发布密钥）、`secret`（密钥）、`none`（无需凭证）
- 数组语法 (`auth: ['user', 'secret']`) 是先匹配胜出。一个存在但无效的 JWT 会触发 `InvalidJwtError` (`INVALID_JWT`) — 它不会静默降级到下一个模式。
- 提供可组合的核心原语，用于自定义认证流程和框架集成
- 包含用于每条路由认证的 Hono 适配器

## 入口点

| 导入                                      | Deno / Edge Functions                           | 提供                                                                                                                                                                |
| ------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@supabase/server`                          | `npm:@supabase/server`                          | `withSupabase`, `createSupabaseContext`, 类型, 错误                                                                                                                  |
| `@supabase/server/core`                     | `npm:@supabase/server/core`                     | `verifyAuth`, `verifyCredentials`, `extractCredentials`, `resolveEnv`, `createContextClient`, `createAdminClient`                                                       |
| `@supabase/server/adapters/hono`            | `npm:@supabase/server/adapters/hono`            | `withSupabase`（Hono 中间件变体）                                                                                                                                |
| `@supabase/server/oauth-protected-resource` | `npm:@supabase/server/oauth-protected-resource` | **Alpha。** `withOAuthProtectedResource`, `fromSupabaseUrl`, `resourceMetadataResponse`, `unauthorizedResponse` — OAuth 2.1 发现用于 MCP 服务器；参见 `docs/mcp.md` |

## 快速入门

> **Supabase Edge Functions：对于非用户认证，禁用 `verify_jwt`。** 默认情况下，Supabase Edge Functions 对每个请求都要求有效的 JWT。如果您的函数使用 `auth: 'publishable'`、`auth: 'secret'` 或 `auth: 'none'`，您必须在 `supabase/config.toml` 中禁用平台级别的 JWT 检查，否则请求将在到达处理程序之前被拒绝：
>
> ```toml
> [functions.my-function]
> verify_jwt = false
> ```
>
> 使用 `auth: 'user'` 的函数可以保留 `verify_jwt` 启用（默认值），因为调用者已经提供了有效的 JWT。

### Supabase Edge Functions (Deno)

环境变量由平台自动注入——零配置。**所有导入都必须使用 `npm:` 指定。**

```ts
// withSupabase — 高级包装
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  }),
}
```

```ts
// createSupabaseContext — 返回 { data, error } 以用于自定义响应控制
import { createSupabaseContext } from 'npm:@supabase/server'

export default {
  fetch: async (req: Request) => {
    const { data: ctx, error } = await createSupabaseContext(req, {
      auth: 'user',
    })
    if (error) {
      return Response.json(
        { message: error.message, code: error.code },
        { status: error.status },
      )
    }
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  },
}
```

### Cloudflare Workers

需要 `nodejs_compat` 兼容标志在 `wrangler.toml` 中，或通过 `env` 配置选项传递环境覆盖。参见 `docs/environment-variables.md`。

```ts
import { withSupabase } from '@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('todos').select()
    return Response.json(data)
  }),
}
```

### Hono

CORS 由适配器处理——使用 `hono/cors` 中间件。参见 `docs/adapters/hono.md`。

```ts
// Node.js / Bun
import { Hono } from 'hono'
import { withSupabase } from '@supabase/server/adapters/hono'

const app = new Hono()
app.use('*', withSupabase({ auth: 'user' }))

app.get('/todos', async (c) => {
  const { supabase } = c.var.supabaseContext
  const { data } = await supabase.from('todos').select()
  return c.json(data)
})

export default app
```

```ts
// Deno / Supabase Edge Functions
import { Hono } from 'npm:hono'
import { withSupabase } from 'npm:@supabase/server/adapters/hono'

const app = new Hono()
app.use('*', withSupabase({ auth: 'user' }))

app.get('/todos', async (c) => {
  const { supabase } = c.var.supabaseContext
  const { data } = await supabase.from('todos').select()
  return c.json(data)
})

export default { fetch: app.fetch }
```

### 基于 Cookie 的环境（与 `@supabase/ssr` 组合）

对于 Next.js / SvelteKit / Remix，**组合 `@supabase/server` 与 [`@supabase/ssr`](https://github.com/supabase/ssr)** — 它们不能互相替代。`@supabase/ssr` 拥有 Cookie 和刷新令牌轮换（其中间件是必需的，否则访问令牌 Cookie 会过期且验证失败）。在您的服务器组件或路由处理程序中，使用 `@supabase/ssr` 的 `createServerClient` 读取（由中间件刷新的）会话，将访问令牌传递给 `@supabase/server/core` 的 `verifyCredentials`，然后使用 `createContextClient` + `createAdminClient` 构建类型化客户端。参见 `docs/ssr-frameworks.md` 了解完整的适配器模式。

```ts
// 构建适配器的关键导入
import { createServerClient } from '@supabase/ssr'
import {
  verifyCredentials,
  createContextClient,
  createAdminClient,
} from '@supabase/server/core'
```

### 服务器到服务器（密钥认证）

用于内部服务、计划任务或自动化调用您的 Edge Function。调用者通过 `apikey` 头发送密钥。参见 `docs/auth-modes.md` 了解命名密钥语法。

**Edge Function (Deno):**

```ts
import { withSupabase } from 'npm:@supabase/server'

// 仅接受 "automations" 命名的密钥
export default {
  fetch: withSupabase({ auth: 'secret:automations' }, async (req, ctx) => {
    const body = await req.json()
    const { data } = await ctx.supabaseAdmin
      .from('scheduled_tasks')
      .insert({ name: body.taskName, scheduled_at: body.scheduledAt })
    return Response.json({ success: true, data })
  }),
}
```

**调用者（外部服务）：**

```ts
await fetch('https://<project>.supabase.co/functions/v1/my-function', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    apikey: 'sb_secret_automations_...', // 命名密钥
  },
  body: JSON.stringify({
    taskName: 'cleanup',
    scheduledAt: new Date().toISOString(),
  }),
})
```

裸 `auth: 'secret'` 仅匹配 `default` 密钥。使用 `auth: 'secret:name'` 要求特定的命名密钥，或 `auth: 'secret:*'` 接受集合中的任何密钥。

## 将用户令牌固定到单个项目

`audience` 和 `issuer` 检查 `user`-模式令牌的 `aud` 和 `iss` 声明。每个都接受字符串或数组。没有声明或值不在列表中的令牌会被 `INVALID_JWT` 拒绝。当多个项目或服务可以共享一个 JWKS 时，设置 `issuer: fromSupabaseUrl(url)`。Supabase Auth 将 `aud` 设置为 `authenticated`，因此 `audience` 仅适用于来自自定义发行者的令牌。这两个选项都存在于 `withSupabase`、`verifyAuth`、`verifyCredentials`、`withClaims` 和 `withRequiredClaims` 上。

```ts
import { fromSupabaseUrl, withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase(
    {
      auth: 'user',
      issuer: fromSupabaseUrl(Deno.env.get('SUPABASE_URL')!),
    },
    async (req, ctx) => Response.json({ user: ctx.userClaims }),
  ),
}
```

## 何时使用 `auth: 'none'`

> **`auth: 'none'` 禁用所有认证。** 处理程序对每个请求都运行，没有凭证检查。仅在认证确实不需要时使用它——健康检查、公共状态页面或没有敏感数据且没有副作用的端点。

**在使用 `auth: 'none'` 之前，请与用户确认端点是否真正公开。** 如果不是，请提出替代方案：

- **另一个服务或计划任务调用此函数** — 使用 `auth: 'secret'` 或 `auth: 'secret:<name>'` 替代。调用者通过 `apikey` 头发送密钥。
- **外部 webhook 提供商调用此函数** — 使用 `auth: 'secret'` 并让提供商发送密钥，或在处理程序中实现提供商自己的签名验证。

**永远不要使用 `auth: 'none'` 来读取或写入用户数据，而无需验证调用者是谁。**

**关于 `auth: ['user', 'none']`。** 在此类端点上，一个过时或格式错误的 JWT 会被 `InvalidJwtError` (`INVALID_JWT`) 拒绝——它不会静默降级到匿名。可能持有缓存的/过期的令牌的调用者应该完全省略 `Authorization` 头，或在调用前刷新。如果目标是“除非用户已登录，否则接受任何内容”，则此行为是正确的；如果目标是真正“接受任何内容”，请单独使用 `auth: 'none'`。

**`'none'` 作为最后一个或单独使用。** 它匹配每个请求，因此类型仅将其作为列表的最后一个条目 (`['user', 'none']`) 或单独使用 (`'none'`) 接受。`['none']` 和 `['none', 'user']` 是类型错误——为第一个编写 `'none'`，并为第二个将 `'none'` 放在最后。

## Edge Function 配方

### 函数到函数调用

一个 Edge Function 可以使用管理员客户端调用另一个。被调用的函数使用 `auth: 'secret'`，调用者通过 `ctx.supabaseAdmin.functions.invoke()` 调用它。

**配置** (`supabase/config.toml`):

```toml
[functions.process-order]
verify_jwt = false  # 被密钥调用，而不是用户 JWT
```

**被调用的函数** (`supabase/functions/process-order/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'secret' }, async (req, ctx) => {
    const { orderId } = await req.json()
    const { data } = await ctx.supabaseAdmin
      .from('orders')
      .update({ status: 'processing' })
      .eq('id', orderId)
      .select()
      .single()
    return Response.json(data)
  }),
}
```

**调用函数** (`supabase/functions/checkout/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (req, ctx) => {
    const { orderId } = await req.json()

    // 自动调用 process-order 使用密钥
    const { data, error } = await ctx.supabaseAdmin.functions.invoke(
      'process-order',
      { body: { orderId } },
    )

    if (error) {
      return Response.json({ error: error.message }, { status: 500 })
    }
    return Response.json(data)
  }),
}
```

### 从数据库使用 pg_net 调用

使用 `pg_net` 直接从 SQL 调用 Edge Function。密钥存储在 Vault 中，因此它永远不会出现在查询中。

**前提条件:**

```sql
-- 1. 启用 pg_net 扩展
create extension if not exists pg_net with schema extensions;

-- 2. 将您的密钥存储在 Vault 中
select vault.create_secret(
  'sb_secret_...',        -- 您的密钥值
  'supabase_secret_key'   -- 用于引用的名称
);
```

**调用函数:**

```sql
select net.http_post(
  url := 'https://<project-ref>.supabase.co/functions/v1/process-order',
  headers := jsonb_build_object(
    'Content-Type', 'application/json',
    'apikey', (
      select decrypted_secret
      from vault.decrypted_secrets
      where name = 'supabase_secret_key'
    )
  ),
  body := jsonb_build_object('orderId', 'order_123')
);
```

接收函数使用 `auth: 'secret'`（见上面的示例）。`pg_net` 是异步的——HTTP 请求排队并在后台执行。检查 `net._http_response` 获取结果。

### Stripe webhook

像 Stripe 这样的外部 webhook 提供商无法发送您的 Supabase API 密钥。使用 `auth: 'none'` 跳过凭证检查，然后在处理程序内部验证 webhook 签名。

**配置** (`supabase/config.toml`):

```toml
[functions.stripe-webhook]
verify_jwt = false
```

**设置密钥:**

```bash
supabase secrets set STRIPE_SECRET_KEY=sk_live_...
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...
```

**函数** (`supabase/functions/stripe-webhook/index.ts`):

```ts
import { withSupabase } from 'npm:@supabase/server'
import Stripe from 'npm:stripe'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!)

export default {
  fetch: withSupabase({ auth: 'none' }, async (req, ctx) => {
    const body = await req.text()
    const sig = req.headers.get('stripe-signature')!

    let event: Stripe.Event
    try {
      event = await stripe.webhooks.constructEventAsync(
        body,
        sig,
        Deno.env.get('STRIPE_WEBHOOK_SECRET')!,
      )
    } catch {
      return Response.json({ error: 'Invalid signature' }, { status: 401 })
    }

    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        await ctx.supabaseAdmin
          .from('orders')
          .update({ status: 'paid' })
          .eq('stripe_session_id', session.id)
        break
      }
    }

    return Response.json({ received: true })
  }),
}
```

### 迁移遗留 Edge Functions

如果您遇到使用 `SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY`、`Deno.serve` 或从 `esm.sh/@supabase` 或 `deno.land/std` 导入的代码，建议迁移到 `@supabase/server`。这些遗留模式正在被弃用——它们需要手动创建客户端、手动转发认证头、手动处理 CORS，并且直接在代码中暴露密钥。

**如何识别遗留代码:**

- `import { serve } from "https://deno.land/std/..."` — 最旧的模式，使用已弃用的 Deno 标准库
- `import { createClient } from "https://esm.sh/@supabase/supabase-js"` — 旧的 CDN 导入，与现代运行时不兼容
- `Deno.serve(async (req) => { ... })` 与手动 `createClient()` — 当前但冗长，需要手动转发认证
- `Deno.env.get('SUPABASE_ANON_KEY')` 或 `SUPABASE_SERVICE_ROLE_KEY` — 遗留的密钥将被移除

**之前**（遗留——手动客户端、手动认证转发）:

遗留密钥将被移除，使此代码无法工作。它也很冗长，不跨平台兼容，需要手动连接认证头、CORS 和错误处理。

```ts
import { createClient } from 'npm:@supabase/supabase-js@2'

Deno.serve(async (req: Request) => {
  const supabaseClient = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    {
      global: { headers: { Authorization: req.headers.get('Authorization')! } },
    },
  )
  const { data } = await supabaseClient.from('orders').select('*')
  return Response.json(data)
})
```

**之后**（新的——自动处理认证、客户端和 CORS）:

使用最新的 API 密钥，跨运行时（Deno、Node.js、Cloudflare）工作，并处理认证验证、客户端创建和 CORS 在一行内。

```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { data } = await ctx.supabase.from('orders').select('*')
    return Response.json(data)
  }),
}
```

迁移映射：`SUPABASE_ANON_KEY` 与手动认证头 → `auth: 'user'`，`SUPABASE_ANON_KEY` 无认证 → `auth: 'publishable'`。对于 `SUPABASE_SERVICE_ROLE_KEY`，取决于意图：如果遗留代码验证传入的密钥以保护端点（例如 `req.headers.get('apikey') === serviceRoleKey`），则使用 `auth: 'secret'`。如果它仅使用密钥来创建管理员客户端以进行提升的数据库访问，则不需要特定的认证模式——无论认证模式如何，`ctx.supabaseAdmin` 始终可用。
