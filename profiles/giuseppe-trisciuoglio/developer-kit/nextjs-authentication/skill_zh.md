# Next.js 认证

## 概述

为 Next.js 15+ App Router 提供使用 Auth.js 5 (NextAuth.js) 的认证实现模式，涵盖从初始设置到生产就绪的基于角色的访问控制实现的完整认证生命周期。

## 何时使用

- 从头开始设置 Auth.js 5 或添加 OAuth 提供商
- 使用中间件实现受保护的路由
- 在服务器组件和服务器操作中处理认证
- 实现基于角色的访问控制 (RBAC)
- 创建基于凭证或 OAuth 的登录/登出流程

## 说明

### 1. 安装依赖项

为 Next.js App Router 安装 Auth.js v5 (beta)：

```bash
npm install next-auth@beta
```

### 2. 配置环境变量

创建 `.env.local` 并包含所需变量：

```bash
# Auth.js 所需
AUTH_SECRET="your-secret-key-here"
AUTH_URL="http://localhost:3000"

# OAuth 提供商（按需添加）
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

使用以下命令生成 `AUTH_SECRET`：

```bash
openssl rand -base64 32
```

### 3. 创建认证配置

在项目根目录下创建 `auth.ts` 并包含提供者和回调：

```typescript
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/error",
  },
});
```

### 4. 创建 API 路由处理器

在 `app/api/auth/[...nextauth]/route.ts` 中创建：

```typescript
export { GET, POST } from "@/auth";
```

### 5. 为路由添加中间件保护

在项目根目录下创建 `middleware.ts`：

```typescript
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { nextUrl } = req;
  const isLoggedIn = !!req.auth;
  const isApiAuthRoute = nextUrl.pathname.startsWith("/api/auth");
  const isPublicRoute = ["/", "/login", "/register"].includes(nextUrl.pathname);
  const isProtectedRoute = nextUrl.pathname.startsWith("/dashboard");

  if (isApiAuthRoute) return NextResponse.next();

  if (!isLoggedIn && isProtectedRoute) {
    return NextResponse.redirect(new URL("/login", nextUrl));
  }

  if (isLoggedIn && nextUrl.pathname === "/login") {
    return NextResponse.redirect(new URL("/dashboard", nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
```

### 6. 在服务器组件中访问会话

使用 `auth()` 函数在服务器组件中访问会话：

```tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect("/login");
  }

  return (
    <div>
      <h1>欢迎，{session.user.name}</h1>
    </div>
  );
}
```

### 7. 安全化服务器操作

在服务器操作前始终验证认证：

```tsx
"use server";

import { auth } from "@/auth";

export async function createTodo(formData: FormData) {
  const session = await auth();

  if (!session?.user) {
    throw new Error("未授权");
  }

  // 执行受保护的操作
  const title = formData.get("title") as string;
  await db.todo.create({
    data: { title, userId: session.user.id },
  });
}
```

### 8. 处理登录/登出

创建带有服务器操作的登录页面：

```tsx
// app/login/page.tsx
import { signIn } from "@/auth";
import { redirect } from "next/navigation";

export default function LoginPage() {
  async function handleLogin(formData: FormData) {
    "use server";

    const result = await signIn("credentials", {
      email: formData.get("email"),
      password: formData.get("password"),
      redirect: false,
    });

    if (result?.error) {
      return { error: "无效的凭证" };
    }

    redirect("/dashboard");
  }

  return (
    <form action={handleLogin}>
      <input name="email" type="email" placeholder="邮箱" required />
      <input name="password" type="password" placeholder="密码" required />
      <button type="submit">登录</button>
    </form>
  );
}
```

客户端端登出：

```tsx
"use client";

import { signOut } from "next-auth/react";

export function SignOutButton() {
  return <button onClick={() => signOut()}>登出</button>;
}
```

### 9. 实现基于角色的访问

在服务器组件中检查角色：

```tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();

  if (session?.user?.role !== "admin") {
    unauthorized();
  }

  return <AdminDashboard />;
}
```

### 10. 扩展 TypeScript 类型

创建 `types/next-auth.d.ts` 以实现类型安全的会话：

```typescript
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role: "user" | "admin";
    } & DefaultSession["user"];
  }

  interface User {
    role?: "user" | "admin";
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    role?: "user" | "admin";
  }
}
```

## 示例

### 示例 1：完整的受保护仪表板

**输入：** 用户需要访问仅限认证用户使用的仪表板

**实现：**

```tsx
// app/dashboard/page.tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { getUserTodos } from "@/app/lib/data";

export default async function DashboardPage() {
  const session = await auth();

  if (!session?.user?.id) {
    redirect("/login");
  }

  const todos = await getUserTodos(session.user.id);

  return (
    <main>
      <h1>欢迎，{session.user.name}</h1>
      <p>邮箱：{session.user.email}</p>
      <TodoList todos={todos} />
    </main>
  );
}
```

**输出：** 仪表板仅对认证用户渲染，并显示其特定数据。

### 示例 2：基于角色的管理员面板

**输入：** 管理员面板应仅对具有 "admin" 角色的用户可访问

**实现：**

```tsx
// app/admin/page.tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();

  if (session?.user?.role !== "admin") {
    unauthorized();
  }

  return (
    <main>
      <h1>管理员面板</h1>
      <p>欢迎，管理员 {session.user.name}</p>
    </main>
  );
}
```

**输出：** 仅管理员用户看到面板；其他人收到 401 错误。

### 示例 3：带表单的安全服务器操作

**输入：** 表单提交应仅对认证用户有效

**实现：**

```tsx
// app/components/create-todo-form.tsx
"use server";

import { auth } from "@/auth";
import { revalidatePath } from "next/cache";

export async function createTodo(formData: FormData) {
  const session = await auth();

  if (!session?.user?.id) {
    throw new Error("未授权");
  }

  const title = formData.get("title") as string;

  await db.todo.create({
    data: {
      title,
      userId: session.user.id,
    },
  });

  revalidatePath("/dashboard");
}

// 组件中使用
export function CreateTodoForm() {
  return (
    <form action={createTodo}>
      <input name="title" placeholder="新待办..." required />
      <button type="submit">添加待办</button>
    </form>
  );
}
```

**输出：** 仅认证用户创建待办事项；未授权请求抛出错误。

## 最佳实践

1. **默认使用服务器组件** - 直接访问会话，无需客户端 JavaScript
2. **最小化客户端组件** - 仅使用 `useSession()` 进行响应式会话更新
3. **缓存会话检查** - 使用 React 的 `cache()` 对同一渲染中的重复查找进行缓存
4. **中间件进行乐观检查** - 快速重定向，但在服务器操作中始终重新验证
5. **将服务器操作视为 API 端点** - 在变更前始终进行认证
6. **永不硬编码密钥** - 使用环境变量存储所有凭证
7. **实现适当的错误处理** - 返回适当的 HTTP 状态码
8. **使用 TypeScript 类型扩展** - 扩展 NextAuth 类型以包含自定义字段
9. **分离认证逻辑** - 创建数据访问层 (DAL) 以实现一致的检查
10. **测试认证流程** - 在单元测试中模拟 `auth()` 函数

## 限制和警告

### 关键限制

- **中间件在 Edge 运行时运行** - 无法使用 Node.js API 如数据库驱动
- **服务器组件无法设置 Cookie** - 使用服务器操作进行 Cookie 操作
- **会话回调时机** - 仅在会话创建/访问时调用，不是每个请求

### 常见错误

```tsx
// ❌ 错误：在服务器组件中设置 Cookie
export default async function Page() {
  cookies().set("key", "value"); // 不会工作
}

// ✅ 正确：使用服务器操作
async function setCookieAction() {
  "use server";
  cookies().set("key", "value");
}
```

```typescript
// ❌ 错误：在中间件中进行数据库查询
export default auth(async (req) => {
  const user = await db.user.findUnique(); // 不会工作
});

// ✅ 正确：仅使用 Edge 兼容 API
export default auth(async (req) => {
  const session = req.auth; // 这会工作
});
```

### 安全注意事项

- 始终在服务器操作中验证认证 - 中间件本身不足以确保安全
- 使用 `unauthorized()` 处理未认证访问，`redirect()` 处理其他情况
- 将敏感令牌存储在 `httpOnly` Cookie 中
- 在处理前验证所有用户输入
- 生产环境使用 HTTPS
- 设置适当的 Cookie `sameSite` 属性

## 参考

- [references/authjs-setup.md](references/authjs-setup.md) - 完整的 Auth.js 5 设置指南，包含 Prisma/Drizzle 适配器
- [references/oauth-providers.md](references/oauth-providers.md) - 提供商特定配置（GitHub、Google、Discord、Auth0 等）
- [references/database-adapter.md](references/database-adapter.md) - 使用 Prisma、Drizzle 和自定义适配器的数据库会话管理
- [references/testing-patterns.md](references/testing-patterns.md) - 使用 Vitest 和 Playwright 测试认证流程
