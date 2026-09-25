# Next.js + Supabase Auth

Next.js App Router 与 Supabase Auth 的专家级集成

## 功能

- nextjs-auth
- supabase-auth-nextjs
- auth-middleware
- auth-callback

## 前置条件

- 必备技能：nextjs-app-router, supabase-backend

## 模式

### Supabase 客户端设置

为不同场景创建配置正确的 Supabase 客户端

**使用场景**：在 Next.js 项目中设置认证

// lib/supabase/client.ts (浏览器客户端)
'use client'
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// lib/supabase/server.ts (服务器客户端)
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options)
          })
        },
      },
    }
  )
}

### 认证中间件

在中间件中保护路由并刷新会话

**使用场景**：需要路由保护或会话刷新时

// middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  // 如果会话过期则刷新
  const { data: { user } } = await supabase.auth.getUser()

  // 保护仪表盘路由
  if (request.nextUrl.pathname.startsWith('/dashboard') && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}

### 认证回调路由

处理 OAuth 回调并兑换代码以获取会话

**使用场景**：使用 OAuth 提供商（Google、GitHub 等）

// app/auth/callback/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/auth/error`)
}

### 服务器操作认证

在服务器操作中处理认证

**使用场景**：从服务器组件进行登录、登出或注册

// app/actions/auth.ts
'use server'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function signIn(formData: FormData) {
  const supabase = await createClient()
  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  redirect('/dashboard')
}

export async function signOut() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  revalidatePath('/', 'layout')
  redirect('/')
}

### 服务器组件中获取用户

在服务器组件中访问认证用户

**使用场景**：服务器端渲染用户特定内容

// app/dashboard/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div>
      <h1>欢迎，{user.email}</h1>
    </div>
  )
}

## 验证检查

### 使用 getSession() 进行认证检查

严重程度：错误

消息：getSession() 不会验证 JWT。使用 getUser() 进行安全的认证检查。

修复操作：将 getSession() 替换为 getUser() 进行安全关键检查

### 缺少回调路由的 OAuth

严重程度：错误

消息：使用 OAuth 但缺少 app/auth/callback/route.ts 中的回调路由

修复操作：创建 app/auth/callback/route.ts 以处理 OAuth 重定向

### 服务器上下文中的浏览器客户端

严重程度：错误

消息：在服务器上下文中使用浏览器客户端。使用 createServerClient 代替。

修复操作：从 @supabase/ssr 导入并使用 createServerClient

### 缺少中间件的受保护路由

严重程度：警告

消息：未找到 middleware.ts。考虑添加中间件进行路由保护。

修复操作：创建 middleware.ts 以保护路由和刷新会话

### 硬编码的认证重定向 URL

严重程度：警告

消息：硬编码 localhost 重定向。使用 origin 以实现环境灵活性。

修复操作：使用 window.location.origin 或 process.env.NEXT_PUBLIC_SITE_URL

### 缺少错误处理的认证调用

严重程度：警告

消息：缺少错误处理的认证操作。始终检查错误。

修复操作：解构 { data, error } 并处理错误情况

### 缺少认证操作的重新验证

严重程度：警告

消息：缺少认证操作的重新验证。缓存可能显示过时的认证状态。

修复操作：认证操作后添加 revalidatePath('/', 'layout')

### 客户端路由保护

严重程度：警告

消息：客户端路由保护会短暂显示内容。使用中间件。

修复操作：将保护移动到 middleware.ts 以获得更好的用户体验

## 协作

### 授权触发器

- database|rls|queries|tables -> supabase-backend (认证需要数据库层)
- route|page|component|layout -> nextjs-app-router (认证需要 Next.js 模式)
- deploy|production|vercel -> vercel-deployment (认证需要部署配置)
- ui|form|button|design -> frontend (认证需要 UI 组件)

### 完整认证栈

技能：nextjs-supabase-auth, supabase-backend, nextjs-app-router, vercel-deployment

工作流程：

```
1. 数据库设置 (supabase-backend)
2. 认证实现 (nextjs-supabase-auth)
3. 路由保护 (nextjs-app-router)
4. 部署配置 (vercel-deployment)
```

### 受保护的 SaaS

技能：nextjs-supabase-auth, stripe-integration, supabase-backend

工作流程：

```
1. 用户认证 (nextjs-supabase-auth)
2. 客户同步 (stripe-integration)
3. 订阅门控 (supabase-backend)
```

## 相关技能

与：`nextjs-app-router`, `supabase-backend` 配合使用效果更佳

## 使用场景
- 用户提及或暗示：supabase auth next
- 用户提及或暗示：authentication next.js
- 用户提及或暗示：login supabase
- 用户提及或暗示：auth middleware
- 用户提及或暗示：protected route
- 用户提及或暗示：auth callback
- 用户提及或暗示：session management

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
