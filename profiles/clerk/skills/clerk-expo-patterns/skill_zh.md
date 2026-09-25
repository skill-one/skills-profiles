# Expo模式

SDK: `@clerk/expo` v3+. 需要 Expo 53+、React Native 0.73+。

## 需要什么？

| 任务 | 参考 |
|------|-----------|
| 使用SecureStore持久化令牌 | references/token-storage.md |
| OAuth（Google、Apple、GitHub） | references/oauth-deep-linking.md |
| 使用Expo Router保护屏幕 | references/protected-routes.md |
| 使用用户数据推送通知 | references/push-notifications.md |

## 思维模型

Clerk默认将会话令牌存储在内存中。在原生应用中：

- **SecureStore** — 在设备密钥链中加密令牌（推荐用于生产环境）
- **`tokenCache`** — `<ClerkProvider>`上的属性，提供自定义存储
- **`useAuth`** — 与Web端相同的API，在任何组件中均可使用
- **OAuth** — 需要`useSSO` + 在`app.json`中配置的深度链接方案

## 最小化设置

### app/_layout.tsx

```tsx
import { ClerkProvider } from '@clerk/expo'
import { tokenCache } from '@clerk/expo/token-cache'
import { Stack } from 'expo-router'

const publishableKey = process.env.EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY!

export default function RootLayout() {
  return (
    <ClerkProvider publishableKey={publishableKey} tokenCache={tokenCache}>
      <Stack />
    </ClerkProvider>
  )
}
```

> **关键提示**：使用`EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY` — 而不是`NEXT_PUBLIC_`。`node_modules`内的环境变量在生产构建中不会被内联。始终显式传递`publishableKey`。

## 内置令牌缓存

```tsx
import { tokenCache } from '@clerk/expo/token-cache'
```

这使用`expo-secure-store`并设置`keychainAccessible: AFTER_FIRST_UNLOCK`。安装依赖项：

```bash
npx expo install expo-secure-store
```

## 认证钩子

```tsx
import { useAuth, useUser, useSignIn, useSignUp, useClerk } from '@clerk/expo'

export function ProfileScreen() {
  const { isSignedIn, userId, signOut } = useAuth()
  const { user } = useUser()

  if (!isSignedIn) return <Redirect href="/sign-in" />
  return (
    <View>
      <Text>{user?.fullName}</Text>
      <Button title="Sign Out" onPress={() => signOut()} />
    </View>
  )
}
```

## OAuth流程（Google）

```tsx
import { useSSO } from '@clerk/expo'
import * as WebBrowser from 'expo-web-browser'

WebBrowser.maybeCompleteAuthSession()

export function GoogleSignIn() {
  const { startSSOFlow } = useSSO()

  const handlePress = async () => {
    try {
      const { createdSessionId, setActive } = await startSSOFlow({
        strategy: 'oauth_google',
        redirectUrl: 'myapp://oauth-callback',
      })
      if (createdSessionId) await setActive!({ session: createdSessionId })
    } catch (err) {
      console.error(err)
    }
  }

  return <Button title="使用Google继续" onPress={handlePress} />
}
```

## 组织切换

```tsx
import { useOrganization, useOrganizationList } from '@clerk/expo'

export function OrgSwitcher() {
  const { organization } = useOrganization()
  const { setActive, userMemberships } = useOrganizationList()

  return (
    <View>
      <Text>当前: {organization?.name ?? '个人'}</Text>
      {userMemberships.data?.map(mem => (
        <Button
          key={mem.organization.id}
          title={mem.organization.name}
          onPress={() => setActive({ organization: mem.organization.id })}
        />
      ))}
    </View>
  )
}
```

## 常见陷阱

| 症状 | 原因 | 解决方法 |
|---------|-------|-----|
| `publishableKey` 在生产中未定义 | 未使用`EXPO_PUBLIC_`前缀的环境变量 | 将其重命名为`EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY` |
| 应用重启时令牌丢失 | 没有`tokenCache` | 从`@clerk/expo/token-cache`传入`tokenCache` |
| OAuth重定向不工作 | `app.json`中缺少方案 | 在`app.json`中添加`"scheme": "myapp"` |
| `WebBrowser.maybeCompleteAuthSession` | 未被调用 | 在OAuth回调屏幕的顶层调用它 |
| `useSSO`未找到 | 旧版本的`@clerk/expo` | `useSSO`在v3+中替换了`useOAuth` |

## 导入映射

| 项目 | 导入自 |
|------|-------------|
| `ClerkProvider` | `@clerk/expo` |
| `tokenCache` | `@clerk/expo/token-cache` |
| `useAuth`, `useUser`, `useSignIn` | `@clerk/expo` |
| `useSSO` | `@clerk/expo` |
| `useOrganization`, `useOrganizationList` | `@clerk/expo` |

## 参考文档

- `clerk-setup` - 初始Clerk安装
- `clerk-custom-ui` - 自定义流程和外观
- `clerk-orgs` - B2B组织

## 文档

[Expo SDK](https://clerk.com/docs/expo/getting-started/quickstart)
