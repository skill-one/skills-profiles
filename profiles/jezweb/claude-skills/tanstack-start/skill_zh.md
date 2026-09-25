# TanStack Start on Cloudflare

从零开始构建一个完整的全栈应用。Claude 生成所有文件——无需模板克隆，无需 scaffold 命令。

技术栈：TanStack Start v1（SSR、基于文件的路由、通过 Nitro 的服务器函数）在 Cloudflare Workers 上；React 19 + Tailwind v4 + shadcn/ui；D1 + Drizzle；better-auth（Google OAuth + 邮箱/密码）。

## 项目文件树

```
PROJECT_NAME/
├── src/
│   ├── routes/
│   │   ├── __root.tsx              # 根布局（HTML 容器、主题、CSS 导入）
│   │   ├── index.tsx               # 登录页/认证重定向
│   │   ├── login.tsx               # 登录页面
│   │   ├── register.tsx            # 注册页面
│   │   ├── _authed.tsx             # 认证守卫布局路由
│   │   ├── _authed/
│   │   │   ├── dashboard.tsx       # 带统计卡片的仪表盘
│   │   │   ├── items.tsx           # 项目列表表格
│   │   │   ├── items.$id.tsx       # 编辑项目
│   │   │   └── items.new.tsx       # 创建项目
│   │   └── api/
│   │       └── auth/
│   │           └── $.ts            # better-auth API 通用捕获
│   ├── components/
│   │   ├── ui/                     # shadcn/ui 组件（自动安装）
│   │   ├── app-sidebar.tsx         # 导航侧边栏
│   │   ├── theme-toggle.tsx        # 亮色/暗色/系统切换
│   │   ├── user-nav.tsx            # 用户下拉菜单
│   │   └── stat-card.tsx           # 仪表盘统计卡片
│   ├── db/
│   │   ├── schema.ts               # Drizzle 模式（所有表格）
│   │   └── index.ts                # Drizzle 客户端工厂
│   ├── lib/
│   │   ├── auth.server.ts          # better-auth 服务器配置
│   │   ├── auth.client.ts          # better-auth React 钩子
│   │   └── utils.ts                # cn() 辅助函数用于 shadcn/ui
│   ├── server/
│   │   └── functions.ts            # 服务器函数（CRUD、认证检查）
│   ├── styles/
│   │   └── app.css                 # Tailwind v4 + shadcn/ui CSS 变量
│   ├── router.tsx                  # TanStack Router 配置
│   ├── client.tsx                  # 客户端入口（hydrateRoot）
│   ├── ssr.tsx                     # SSR 入口
│   └── routeTree.gen.ts            # 自动生成的路由树（不要编辑）
├── drizzle/                        # 生成的迁移文件
├── public/                         # 静态资源（favicon 等）
├── vite.config.ts
├── wrangler.jsonc
├── drizzle.config.ts
├── tsconfig.json
├── package.json
├── .dev.vars                       # 本地环境变量（不提交）
└── .gitignore
```

## 依赖项

**运行时：**
```json
{
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "@tanstack/react-router": "^1.120.0",
  "@tanstack/react-start": "^1.120.0",
  "drizzle-orm": "^0.38.0",
  "better-auth": "^1.2.0",
  "zod": "^3.24.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.1.0",
  "tailwind-merge": "^3.0.0",
  "lucide-react": "^0.480.0"
}
```

**开发：**
```json
{
  "@cloudflare/vite-plugin": "^1.0.0",
  "@tailwindcss/vite": "^4.0.0",
  "@vitejs/plugin-react": "^4.4.0",
  "tailwindcss": "^4.0.0",
  "typescript": "^5.7.0",
  "drizzle-kit": "^0.30.0",
  "wrangler": "^4.0.0",
  "tw-animate-css": "^1.2.0"
}
```

**脚本：**
```json
{
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "deploy": "wrangler deploy",
  "db:generate": "drizzle-kit generate",
  "db:migrate:local": "wrangler d1 migrations apply PROJECT_NAME-db --local",
  "db:migrate:remote": "wrangler d1 migrations apply PROJECT_NAME-db --remote"
}
```

## 工作流程

### 第 1 步：收集项目信息

| 必填 | 可选 |
|------|------|
| 项目名称（短横线命名） | Google OAuth 凭据 |
| 一行描述 | 自定义域名 |
| Cloudflare 账户 | 需要 R2 存储？ |
| 认证方法：Google OAuth、邮箱/密码或两者 | 管理员邮箱 |

### 第 2 步：初始化项目

从零开始创建项目目录和所有配置文件。

**`vite.config.ts`** — 插件顺序很重要。Cloudflare 必须是第一个：

```typescript
import { defineConfig } from "vite";
import { cloudflare } from "@cloudflare/vite-plugin";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import viteReact from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    cloudflare({ viteEnvironment: { name: "ssr" } }),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
});
```

**`wrangler.jsonc`**:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "PROJECT_NAME",
  "compatibility_date": "2025-04-01",
  "compatibility_flags": ["nodejs_compat"],
  "main": "@tanstack/react-start/server-entry",
  "account_id": "ACCOUNT_ID",
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "PROJECT_NAME-db",
      "database_id": "DATABASE_ID",
      "migrations_dir": "drizzle"
    }
  ]
}
```

要点：`main` 必须是 `"@tanstack/react-start/server-entry"`（Nitro 服务器入口）。使用 `nodejs_compat`（不是 `node_compat`）。添加 `account_id` 以避免交互式提示。

**`tsconfig.json`**:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] },
    "types": ["@cloudflare/workers-types/2023-07-01"]
  },
  "include": ["src/**/*", "vite.config.ts"]
}
```

**`.dev.vars`** — 使用 `openssl rand -hex 32` 生成 `BETTER_AUTH_SECRET`:

```
BETTER_AUTH_SECRET=<生成的32位十六进制>
BETTER_AUTH_URL=http://localhost:3000
TRUSTED_ORIGINS=http://localhost:3000
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
```

**`.gitignore`** — node_modules、.wrangler、dist、.output、.dev.vars、.vinxi、.DS_Store

然后安装并创建 D1 数据库：

```bash
cd PROJECT_NAME && pnpm install
npx wrangler d1 create PROJECT_NAME-db
# 将 database_id 复制到 wrangler.jsonc 中的 d1_databases 绑定
```

### 第 3 步：数据库模式

**`src/db/schema.ts`** — 所有表格。better-auth 需要：`users`、`sessions`、`accounts`、`verifications`。添加应用程序表格（例如 `items`）用于 CRUD 示例。

D1 特定规则：
- 使用 `integer` 用于时间戳（Unix 纪元），不要 Date 对象
- 使用 `text` 用于主键（nanoid/cuid2），不要自增
- 保持每个查询的绑定参数少于 100 个（批量插入大数据）
- 外键在 D1 中始终启用

**`src/db/index.ts`** — Drizzle 客户端工厂：

```typescript
import { drizzle } from "drizzle-orm/d1";
import { env } from "cloudflare:workers";
import * as schema from "./schema";

export function getDb() {
  return drizzle(env.DB, { schema });
}
```

**关键**：使用 `import { env } from "cloudflare:workers"` — 不是 `process.env`。在每个服务器函数（按请求）中创建 Drizzle 客户端，而不是在模块级别。

**`drizzle.config.ts`**:

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "sqlite",
});
```

生成并应用初始迁移：

```bash
pnpm db:generate
pnpm db:migrate:local
```

### 第 4 步：配置认证

**`src/lib/auth.server.ts`** — 服务器端 better-auth：

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle } from "drizzle-orm/d1";
import { env } from "cloudflare:workers";
import * as schema from "../db/schema";

export function getAuth() {
  const db = drizzle(env.DB, { schema });
  return betterAuth({
    database: drizzleAdapter(db, { provider: "sqlite" }),
    secret: env.BETTER_AUTH_SECRET,
    baseURL: env.BETTER_AUTH_URL,
    trustedOrigins: env.TRUSTED_ORIGINS?.split(",") ?? [],
    emailAndPassword: { enabled: true },
    socialProviders: {
      // 如果提供凭据，添加 Google OAuth
    },
  });
}
```

**关键**：`getAuth()` 必须按请求调用（在处理程序/加载器内），而不是模块级别。

**`src/lib/auth.client.ts`** — 客户端认证钩子：

```typescript
import { createAuthClient } from "better-auth/react";

export const { useSession, signIn, signOut, signUp } = createAuthClient();
```

**`src/routes/api/auth/$.ts`** — better-auth 的 API 通用捕获：

```typescript
import { createAPIFileRoute } from "@tanstack/react-start/api";
import { getAuth } from "../../../lib/auth.server";

export const APIRoute = createAPIFileRoute("/api/auth/$")({
  GET: ({ request }) => getAuth().handler(request),
  POST: ({ request }) => getAuth().handler(request),
});
```

**关键**：认证必须使用 API 路由（`createAPIFileRoute`），而不是服务器函数（`createServerFn`）。better-auth 需要直接访问请求/响应。

### 第 5 步：服务器函数

**核心模式** — 始终在处理程序内创建 DB 客户端：

```typescript
import { createServerFn } from "@tanstack/react-start";
import { getDb } from "../db";

export const getItems = createServerFn({ method: "GET" }).handler(async () => {
  const db = getDb();
  return db.select().from(items).all();
});
```

**输入验证** 使用 Zod：

```typescript
export const createItem = createServerFn({ method: "POST" })
  .inputValidator(
    z.object({
      name: z.string().min(1),
      description: z.string().optional(),
    })
  )
  .handler(async ({ data }) => {
    const db = getDb();
    const id = crypto.randomUUID();
    await db.insert(items).values({ id, ...data, createdAt: Date.now() });
    return { id };
  });
```

**受保护的服务器函数** — 检查认证，未认证则抛出重定向：

```typescript
import { redirect } from "@tanstack/react-router";
import { getAuth } from "../lib/auth.server";

async function requireSession(request?: Request) {
  const auth = getAuth();
  const session = await auth.api.getSession({
    headers: request?.headers ?? new Headers(),
  });
  if (!session) {
    throw redirect({ to: "/login" });
  }
  return session;
}

export const getSessionFn = createServerFn({ method: "GET" }).handler(
  async ({ request }) => {
    const auth = getAuth();
    return auth.api.getSession({ headers: request.headers });
  }
);

export const getItems = createServerFn({ method: "GET" }).handler(
  async ({ request }) => {
    const session = await requireSession(request);
    const db = getDb();
    return db.select().from(items).where(eq(items.userId, session.user.id)).all();
  }
);
```

**路由加载器模式** — 路由中的服务器函数：

```typescript
export const Route = createFileRoute("/_authed/items")({
  loader: () => getItems(),
  component: ItemsPage,
});

function ItemsPage() {
  const items = Route.useLoaderData();
  return <div>{items.map((item) => <div key={item.id}>{item.name}</div>)}</div>;
}
```

**认证守卫** (`_authed.tsx`) — 使用 `beforeLoad`：

```typescript
export const Route = createFileRoute("/_authed")({
  beforeLoad: async () => {
    const session = await getSessionFn();
    if (!session) {
      throw redirect({ to: "/login" });
    }
    return { session };
  },
});
```

子路由通过 `Route.useRouteContext()` 访问会话。

**变异 + 使无效** — 变异后，使路由无效以重新获取加载器：

```typescript
function CreateItemForm() {
  const router = useRouter();
  const handleSubmit = async (data: NewItem) => {
    await createItem({ data });
    router.invalidate();
    router.navigate({ to: "/items" });
  };
  return <form onSubmit={...}>...</form>;
}
```

**类型安全** — 使用 Drizzle 的 `InferSelectModel` / `InferInsertModel` 作为服务器函数输入/输出类型。对于认证失败，始终使用 `throw redirect()` — 不要使用错误响应。

### 第 6 步：应用外壳 + 主题

**`src/routes/__root.tsx`** — 完整 HTML 文档，包含 `<HeadContent />` + `<Scripts />` 来自 `@tanstack/react-router`，`suppressHydrationWarning` 在 `<html>` 上（SSR + 主题），内联主题初始化脚本以防止闪烁，全局 CSS 导入。

**`src/styles/app.css`** — `@import "tailwindcss"`（v4 语法）+ shadcn/ui CSS 变量在 `:root` 和 `.dark` 中。仅使用语义标记。

**`src/router.tsx`**:

```typescript
import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export function createRouter() {
  return createTanStackRouter({ routeTree });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof createRouter>;
  }
}
```

**`src/client.tsx`** + **`src/ssr.tsx`** — 标准 TanStack Start 入口样板。

安装 shadcn/ui：

```bash
pnpm dlx shadcn@latest init --defaults
pnpm dlx shadcn@latest add button card input label sidebar table dropdown-menu form separator sheet
```

**主题切换** — 三态（亮色 → 暗色 → 系统 → 亮色），localStorage 持久化，`.dark` 类在 `<html>` 上。**仅 JS** 系统偏好检测；不使用 CSS `@media (prefers-color-scheme)` 查询。

**组件** 在 `src/components/`：`app-sidebar.tsx`、`theme-toggle.tsx`、`user-nav.tsx`、`stat-card.tsx`。

### 第 7 步：CRUD 服务器函数

| 函数 | 方法 | 目的 |
|------|------|------|
| `getItems` | GET | 列出当前用户的所有项目 |
| `getItem` | GET | 通过 ID 获取单个项目 |
| `createItem` | POST | 创建新项目 |
| `updateItem` | POST | 更新现有项目 |
| `deleteItem` | POST | 通过 ID 删除项目 |

每个服务器函数： (1) 获取认证会话， (2) 通过 `getDb()` 创建按请求的 Drizzle 客户端， (3) 执行 DB 操作， (4) 返回类型化数据。路由加载器调用 GET 函数。变异调用 POST 函数然后 `router.invalidate()`。

### 第 8 步：本地验证

```bash
pnpm dev
```

- [ ] 应用程序加载在 http://localhost:3000
- [ ] 注册新账户（邮箱/密码）
- [ ] 登录和登出正常工作
- [ ] 仪表盘加载带统计卡片
- [ ] 创建、列出、编辑、删除项目
- [ ] 主题切换循环：亮色 -> 暗色 -> 系统
- [ ] 侧边栏在移动设备上收起
- [ ] 无控制台错误

### 第 9 步：部署到生产

**预部署检查清单** — 部署前验证：
- [ ] `wrangler.jsonc` 包含正确的 `account_id`；`main` 是 `"@tanstack/react-start/server-entry"`；`compatibility_flags` 中包含 `nodejs_compat`
- [ ] D1 数据库已创建，`database_id` 已设置
- [ ] `.dev.vars` 已 gitignore，源代码中无硬编码的凭据

**设置生产凭据：**

```bash
openssl rand -hex 32 | npx wrangler secret put BETTER_AUTH_SECRET
echo "https://PROJECT.SUBDOMAIN.workers.dev" | npx wrangler secret put BETTER_AUTH_URL
echo "http://localhost:3000,https://PROJECT.SUBDOMAIN.workers.dev" | npx wrangler secret put TRUSTED_ORIGINS

# Google OAuth（可选）
echo "your-client-id" | npx wrangler secret put GOOGLE_CLIENT_ID
echo "your-client-secret" | npx wrangler secret put GOOGLE_CLIENT_SECRET
```

如果使用 Google OAuth，在 Google Cloud Console 中添加生产重定向 URI：`https://PROJECT.SUBDOMAIN.workers.dev/api/auth/callback/google`。

**迁移和部署：**

```bash
pnpm db:migrate:remote
pnpm build && npx wrangler deploy
```

首次部署后，更新 `BETTER_AUTH_URL` 为实际 Worker URL 并重新部署。

**验证**：应用程序加载在生产 URL，认证正常，CRUD 正常，主题持久化。

**自定义域名**（可选）：Cloudflare 控制台 → Workers → Triggers → 自定义域名。更新 `BETTER_AUTH_URL` + `TRUSTED_ORIGINS` 凭据 + Google OAuth 重定向 URI 到新域名。重新部署。

## 常见问题

| 症状 | 原因 | 解决方法 |
|------|------|---------|
| `env` 未定义 | 在模块级别访问 | 仅在请求处理程序中使用 `import { env } from "cloudflare:workers"` |
| D1 数据库未找到 | 绑定不匹配 | 检查 `d1_databases` 绑定名称在 wrangler.jsonc 中是否与代码匹配 |
| 认证重定向循环 | URL 不匹配 | `BETTER_AUTH_URL` 必须与实际 URL 完全匹配（协议 + 域名，无尾随斜杠） |
| 认证静默失败 | 缺少原点 | 将所有有效 URL（逗号分隔）设置为 `TRUSTED_ORIGINS` 凭据 |
| 样式未加载 | 缺少插件 | 确保 `@tailwindcss/vite` 插件在 vite.config.ts 中 |
| SSR 水合不匹配 | 主题闪烁 | 在 `<html>` 元素上添加 `suppressHydrationWarning` |
| 在 Cloudflare 上构建失败 | 配置错误 | 检查 `nodejs_compat` 标志和 wrangler.jsonc 中的 `main` 字段 |
| 凭据未生效 | 未重新部署 | `wrangler secret put` 不会重新部署 — 运行 `npx wrangler deploy` 后 |
| 认证端点返回 404 | 路由类型错误 | 使用 `createAPIFileRoute`（API 路由），而不是 `createServerFn` 用于 better-auth |
| "redirect_uri_mismatch" | 缺少 URI | 在 Google Cloud Console OAuth 重定向 URI 中添加生产 URL |
| 模糊的 Vite 错误 | 插件顺序 | 必须是：`cloudflare()` -> `tailwindcss()` -> `tanstackStart()` -> `viteReact()` |
| "Table not found" 500s | 缺少迁移 | 部署前运行 `pnpm db:migrate:remote` |
