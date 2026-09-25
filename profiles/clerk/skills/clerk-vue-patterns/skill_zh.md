# Vue 模式

SDK: `@clerk/vue` v2+ (Vue 3)。对于 Nuxt，使用 `clerk-nuxt-patterns`。

## 需要什么？

| 任务 | 参考 |
|------|-----------|
| 组合式: useAuth, useUser, useOrganization | references/composables.md |
| Vue Router 导航守卫 | references/vue-router-guards.md |
| 带有认证状态的 Pinia 存储 | references/pinia-integration.md |

## 思维模型

Vue 使用 `@clerk/vue` 的组合式：

- **`useAuth()`** — 反应式 `isSignedIn`, `userId`, `signOut`
- **`useUser()`** — 反应式 `user` 对象
- **`useClerk()`** — 完整的 Clerk 实例用于高级操作
- **`useOrganization()`** — 反应式 `organization`, `membership`

## 设置

### Vue (纯)

```ts
// main.ts
import { clerkPlugin } from '@clerk/vue'
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
app.use(clerkPlugin, {
  publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
})
app.mount('#app')
```

## 组合式使用

```vue
<script setup lang="ts">
import { useAuth, useUser } from '@clerk/vue'

const { isSignedIn, userId, signOut } = useAuth()
const { user } = useUser()
</script>

<template>
  <div v-if="isSignedIn">
    <p>Hello {{ user?.firstName }}</p>
    <button @click="signOut()">退出登录</button>
  </div>
  <SignInButton v-else />
</template>
```

## 组织切换

```vue
<script setup lang="ts">
import { useOrganizationList } from '@clerk/vue'

const { userMemberships, setActive } = useOrganizationList()
</script>

<template>
  <button
    v-for="mem in userMemberships.data ?? []"
    :key="mem.organization.id"
    @click="setActive({ organization: mem.organization.id })"
  >
    {{ mem.organization.name }}
  </button>
</template>
```

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| 组合式返回 `undefined` | 不在 `ClerkProvider` 树内 | 确保 `app.use(clerkPlugin, { publishableKey })` 被调用 |
| `userId` 反应式但未更新 | 解构丢失反应性 | 使用 `const { userId } = useAuth()` (toRefs-style 组合式，反应式) |

## 导入映射

| 内容 | 导入 |
|------|--------|
| 组合式 | `@clerk/vue` |
| 插件设置 | `@clerk/vue` |
| 组件 | `@clerk/vue` |

## 参考资料链接

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B 组织

## 文档

- [Vue SDK](https://clerk.com/docs/vue/getting-started/quickstart)
