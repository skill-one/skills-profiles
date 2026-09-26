# vinext — Vite上的Next.js API，随处部署

> 技能来自 [ara.so](https://ara.so) — 2026每日技能集合。

vinext是一个Vite插件，重新实现了Next.js的公共API表面（路由、SSR、RSC、`next/*`导入、CLI），使得现有的Next.js应用可以在Vite上运行，而不是Next.js编译器。它目标实现约94%的API覆盖率，同时支持Pages Router和App Router，并原生部署到Cloudflare Workers，同时支持AWS、Netlify、Vercel等平台的Nitro选项。

## 安装

### 新建项目（从Next.js迁移）

```bash
# 一键命令式迁移
npx vinext init
```

这将会：
1. 运行兼容性检查 (`vinext check`)
2. 将`vite`、`@vitejs/plugin-react`作为devDependencies安装
3. 为App Router安装`@vitejs/plugin-rsc`、`react-server-dom-webpack`
4. 在`package.json`中添加`"type": "module"`
5. 重命名CJS配置文件（例如`postcss.config.js` → `postcss.config.cjs`）
6. 添加`dev:vinext`和`build:vinext`脚本
7. 生成一个最小的`vite.config.ts`

迁移操作是**非破坏性**的 — Next.js仍然可以与vinext协同工作。

### 手动安装

```bash
npm install -D vinext vite @vitejs/plugin-react

# 仅App Router：
npm install -D @vitejs/plugin-rsc react-server-dom-webpack
```

更新`package.json`脚本：

```json
{
  "scripts": {
    "dev": "vinext dev",
    "build": "vinext build",
    "start": "vinext start",
    "deploy": "vinext deploy"
  }
}
```

### Agent技能（AI辅助迁移）

```bash
npx skills add cloudflare/vinext
# 然后在你的AI工具中： "将此项目迁移到vinext"
```

## CLI参考

| 命令 | 描述 |
|---|---|
| `vinext dev` | 使用HMR启动开发服务器 |
| `vinext build` | 生产环境构建 |
| `vinext start` | 本地生产服务器用于测试 |
| `vinext deploy` | 构建并部署到Cloudflare Workers |
| `vinext init` | 自动从Next.js迁移 |
| `vinext check` | 迁移前扫描兼容性问题 |
| `vinext lint` | 代理到eslint或oxlint |

### CLI选项

```bash
vinext dev -p 3001 -H 0.0.0.0
vinext deploy --preview
vinext deploy --env staging --name my-app
vinext deploy --skip-build --dry-run
vinext deploy --experimental-tpr
vinext init --port 3001 --skip-check --force
```

## 配置

vinext会自动检测`app/`或`pages/`目录，并自动加载`next.config.js`。基本使用不需要`vite.config.ts`。

### 最小的`vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { vinext } from 'vinext/vite'

export default defineConfig({
  plugins: [
    react(),
    vinext(),
  ],
})
```

### App Router的`vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import rsc from '@vitejs/plugin-rsc'
import { vinext } from 'vinext/vite'

export default defineConfig({
  plugins: [
    react(),
    rsc(),
    vinext(),
  ],
})
```

### Cloudflare Workers与bindings

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { vinext } from 'vinext/vite'
import { cloudflare } from '@cloudflare/vite-plugin'

export default defineConfig({
  plugins: [
    cloudflare(),
    react(),
    vinext(),
  ],
})
```

### 通过Nitro其他平台

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { vinext } from 'vinext/vite'
import nitro from 'vite-plugin-nitro'

export default defineConfig({
  plugins: [
    react(),
    vinext(),
    nitro({ preset: 'vercel' }), // 或 'netlify', 'aws-amplify', 'deno-deploy' 等
  ],
})
```

## 项目结构

vinext使用与Next.js相同的目录约定 — 无需更改：

```
my-app/
├── app/                  # App Router (自动检测)
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/route.ts
├── pages/                # Pages Router (自动检测)
│   ├── index.tsx
│   └── api/hello.ts
├── public/               # 静态资源
├── next.config.js        # 自动加载
├── package.json
└── vite.config.ts        # 基本使用可选
```

## 代码示例

### Pages Router — SSR页面

```typescript
// pages/index.tsx
import type { GetServerSideProps, InferGetServerSidePropsType } from 'next'

type Props = { data: string }

export const getServerSideProps: GetServerSideProps<Props> = async (ctx) => {
  return { props: { data: 'Hello from SSR' } }
}

export default function Home({ data }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return <h1>{data}</h1>
}
```

### Pages Router — 静态生成

```typescript
// pages/posts/[id].tsx
import type { GetStaticPaths, GetStaticProps } from 'next'

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [{ params: { id: '1' } }, { params: { id: '2' } }],
    fallback: false,
  }
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  return { props: { id: params?.id } }
}

export default function Post({ id }: { id: string }) {
  return <p>Post {id}</p>
}
```

### Pages Router — API路由

```typescript
// pages/api/hello.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({ message: 'Hello from vinext' })
}
```

### App Router — 服务器组件

```typescript
// app/page.tsx
export default async function Page() {
  const data = await fetch('https://api.example.com/data').then(r => r.json())
  return <main>{data.title}</main>
}
```

### App Router — 路由处理器

```typescript
// app/api/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  return NextResponse.json({ status: 'ok' })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  return NextResponse.json({ received: body })
}
```

### App Router — 服务器动作

```typescript
// app/actions.ts
'use server'

export async function submitForm(formData: FormData) {
  const name = formData.get('name')
  // 服务器端逻辑
  return { success: true, name }
}
```

```typescript
// app/form.tsx
'use client'
import { submitForm } from './actions'

export function Form() {
  return (
    <form action={submitForm}>
      <input name="name" />
      <button type="submit">Submit</button>
    </form>
  )
}
```

### 中间件

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

### Cloudflare Workers — Bindings访问

```typescript
// app/api/kv/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getCloudflareContext } from 'cloudflare:workers'

export async function GET(request: NextRequest) {
  const { env } = getCloudflareContext()
  const value = await env.MY_KV.get('key')
  return NextResponse.json({ value })
}
```

### 图片优化

```typescript
// app/page.tsx
import Image from 'next/image'

export default function Page() {
  return (
    <Image
      src="/hero.png"
      alt="Hero"
      width={800}
      height={400}
      priority
    />
  )
}
```

### 链接和导航

```typescript
// app/nav.tsx
'use client'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'

export function Nav() {
  const router = useRouter()
  const pathname = usePathname()

  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <button onClick={() => router.push('/dashboard')}>Dashboard</button>
    </nav>
  )
}
```

## 部署

### Cloudflare Workers

```bash
# 认证（一次）
wrangler login

# 部署
vinext deploy

# 部署到预览
vinext deploy --preview

# 部署到命名环境
vinext deploy --env production --name my-production-app
```

对于CI/CD，设置`CLOUDFLARE_API_TOKEN`环境变量而不是`wrangler login`。

### `wrangler.toml`（Cloudflare配置）

```toml
name = "my-app"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[[kv_namespaces]]
binding = "MY_KV"
id = "your-kv-namespace-id"

[[r2_buckets]]
binding = "MY_BUCKET"
bucket_name = "my-bucket"
```

### Netlify / Vercel / AWS通过Nitro

```bash
npm install -D vite-plugin-nitro

# 然后在vite.config.ts中添加目标预设的nitro插件
# nitro({ preset: 'netlify' })
# nitro({ preset: 'vercel' })
# nitro({ preset: 'aws-amplify' })
```

## `next.config.js`支持

vinext会自动加载你的现有`next.config.js`：

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.example.com' },
    ],
  },
  env: {
    MY_VAR: process.env.MY_VAR,
  },
  redirects: async () => [
    { source: '/old', destination: '/new', permanent: true },
  ],
  rewrites: async () => [
    { source: '/api/:path*', destination: 'https://backend.example.com/:path*' },
  ],
}

module.exports = nextConfig
```

## 兼容性检查

迁移前运行以识别不支持的特性：

```bash
npx vinext check
```

这将扫描：
- 不支持的`next.config.js`选项
- 已弃用的Pages Router API
- 尚未支持的实验性Next.js特性
- CJS配置文件冲突

## 常见模式

### 环境变量

与Next.js相同 — `.env`、`.env.local`、`.env.production`：

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.example.com
DATABASE_URL=$DATABASE_URL
```

```typescript
// 可在客户端代码中访问（NEXT_PUBLIC_前缀）
const apiUrl = process.env.NEXT_PUBLIC_API_URL

// 服务器端独有
const dbUrl = process.env.DATABASE_URL
```

### TypeScript路径别名

```json
// tsconfig.json — 原样工作
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Tailwind CSS

```bash
npm install -D tailwindcss postcss autoprefixer
# 重命名postcss.config.js → postcss.config.cjs（vinext init会自动完成）
```

```javascript
// postcss.config.cjs
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## 故障排除

### ESM与CJS配置文件冲突

```bash
# vinext init会自动处理，或手动重命名：
mv postcss.config.js postcss.config.cjs
mv tailwind.config.js tailwind.config.cjs
```

确保`package.json`包含`"type": "module"`。

### `vinext init`覆盖现有的`vite.config.ts`

```bash
vinext init --force
```

### 初始化时跳过兼容性检查

```bash
vinext init --skip-check
```

### 自定义端口

```bash
vinext dev -p 3001
vinext init --port 3001
```

### `wrangler`未认证部署

```bash
wrangler login
# 或设置环境变量：
export CLOUDFLARE_API_TOKEN=your_token_here
```

### 干运行部署以验证配置

```bash
vinext deploy --dry-run
```

### App Router多环境构建问题

App Router构建产生三个环境（RSC + SSR + 客户端）。如果看到构建错误，请确保安装了所有三个插件：

```bash
npm install -D @vitejs/plugin-rsc react-server-dom-webpack
```

并确保你的`vite.config.ts`按正确顺序包含`react()`和`rsc()`插件。

## 支持内容（Next.js API约94%）

- ✅ Pages Router (SSR, SSG, ISR, API routes)
- ✅ App Router (RSC, Server Actions, Route Handlers, Layouts, Loading, Error boundaries)
- ✅ 中间件
- ✅ `next/image`, `next/link`, `next/router`, `next/navigation`, `next/head`
- ✅ `next/font`, `next/dynamic`
- ✅ `next.config.js` (redirects, rewrites, headers, env, images)
- ✅ Cloudflare Workers原生部署与bindings
- ✅ 开发环境中的HMR
- ✅ TypeScript, Tailwind CSS, CSS Modules
- ⚠️ 实验性Next.js特性 — 低优先级
- ❌ 未文档化的Vercel特定行为 — 故意不支持
