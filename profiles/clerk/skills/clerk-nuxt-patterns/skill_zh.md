# Nuxt 模式

## 你需要什么？

| 任务 | 参考 |
|------|------|
| 使用中间件保护路由 | references/nuxt-middleware.md |
| 服务器 API 路由中的认证（Nitro） | references/server-api-routes.md |
| 组件中的 useAuth / useUser | references/composables.md |
| SSR 安全的认证模式 | references/ssr-auth.md |

## 参考

| 参考 | 描述 |
|------|------|
| `references/nuxt-middleware.md` | 路由保护，clerkMiddleware() |
| `references/server-api-routes.md` | Nitro 服务器路由认证 |
| `references/composables.md` | useAuth, useUser, useClerk |
| `references/ssr-auth.md` | SSR hydration，服务器与客户端 |

## 设置

```
npm install @clerk/nuxt
```

`.env`:
```
NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
NUXT_CLERK_SECRET_KEY=sk_...
```

`nuxt.config.ts`:
```typescript
export default defineNuxtConfig({
  modules: ['@clerk/nuxt'],
})
```

这一行代码会自动配置中间件、插件和组件自动导入。

## 思维模型

`@clerk/nuxt` 会自动导入所有 Clerk 组件和可组合函数 — 无需在 `<script setup>` 中显式导入。

- **可组合函数** (`useAuth`, `useUser`) — 客户端响应式，在 `<script setup>` 中使用
- **服务器路由** (`clerkClient`) — Nitro 服务器路由，`event.context.auth`
- **中间件** (`clerkMiddleware`) — 自动注册，使用 `auth().protect()` 锁定路由

## 最小模式

```vue
<!-- pages/dashboard.vue -->
<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const { userId } = useAuth()
</script>

<template>
  <Show when="signed-in">
    <p>Hello {{ userId }}</p>
  </Show>
</template>
```

> `definePageMeta({ middleware: 'auth' })` 使用 `@clerk/nuxt` 的内置认证中间件。

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|------|------|------|
| 可组合函数在服务器返回 `undefined` | useAuth 仅限客户端使用 | 在服务器路由中使用 `event.context.auth` |
| 路由未受保护 | 缺少 `middleware: 'auth'` 元数据 | 添加 `definePageMeta({ middleware: 'auth' })` |
| `clerkClient` 不可用 | 导入路径错误 | 从 `@clerk/nuxt/server` 导入 |
| hydration 不匹配 | 在挂载前渲染认证状态 | 使用 `<ClientOnly>` 或检查 `isLoaded` |
| 环境变量未生效 | 前缀错误 | Nuxt 要求 `NUXT_PUBLIC_` 用于公共，`NUXT_` 用于服务器 |

## 组织感知模式

```vue
<script setup lang="ts">
const { orgId, orgRole } = useAuth()
</script>

<template>
  <div v-if="orgId">
    <p>组织: {{ orgId }}</p>
    <p v-if="orgRole === 'org:admin'">管理员面板</p>
  </div>
  <div v-else>
    <OrganizationSwitcher />
  </div>
</template>
```

## 参考资料链接

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

[Nuxt SDK](https://clerk.com/docs/nuxt/getting-started/quickstart)
