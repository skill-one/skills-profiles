# Solana 移动端 Privy

Privy 拥有**用户**：一个持久的账户标识符和一个后端可以验证的 JWT。移动钱包适配器拥有**密钥**。在此设置中，Privy 不会签署任何内容——所有签名仍然来自钱包应用。

Sign-In-With-Solana 连接了这两者。Privy 生成一条消息，MWA 签署它，Privy 交换签名以获取会话。

当应用需要在多个设备上保持稳定的用户记录、需要服务器可验证的会话或登录方式超出钱包范围时，请使用此方案。如果应用只需要一个连接的地址，则不需要 Privy——单独使用 `solana-mobile-wallet` 技能即可。

**仅限 Android，且仅限开发版本。** MWA 没有 iOS 支持，并且在 Expo Go 中不运行，这限制了整个集成。

## 开始前

| 要求 | 来源 |
| --- | --- |
| 可用的 `useMobileWallet()` | `solana-mobile-wallet` 技能 |
| Android 开发版本 | `solana-mobile` 技能 |
| Privy 应用 ID 和客户端 ID | Privy 控制台——步骤 1 |

## 步骤 1：创建 Privy 应用

先执行此操作。这两个值是编译时环境变量，而一个控制台开关决定登录是否起作用。

1. 在 https://dashboard.privy.io 签入，并在组织概览页点击 **新建应用**
2. 命名、选择 **移动应用**、创建并保存 **应用 ID**
3. 在 **用户管理 > 认证** 下，在 **外部钱包** 卡中启用 **SVM (Solana) 钱包**
4. 在 **应用设置 > 客户端** 下，将应用标识符设置为 `expo.android.package` 值（来自 `app.json`），并保存 **客户端 ID**

**SVM 钱包** 开关很容易被忽略，但调试起来很昂贵——当它关闭时，即使钱包正确签署，`login` 也会拒绝每个 SIWS 尝试。**应用标识符** 很重要，因为 Privy 会检查调用应用的包名是否与客户端匹配。

```bash
EXPO_PUBLIC_PRIVY_APP_ID=your-privy-app-id
EXPO_PUBLIC_PRIVY_CLIENT_ID=your-privy-client-id
```

两者都是客户端侧的公共标识符，因此 `EXPO_PUBLIC_` 是正确的。**Privy 应用密钥永远不会出现在移动应用中**——以 `EXPO_PUBLIC_` 开头的任何内容都可以在分发的包中读取。密钥仅用于服务器代码。

## 步骤 2：安装和配置

```bash
npx expo install @privy-io/expo @privy-io/expo-native-extensions
```

`@privy-io/expo` 带有一个很长的依赖列表，在版本之间会发生变化——包括密钥、安全存储、网络浏览器、加密和 `viem`。安装你选择的版本要求的内容，而不是从任何地方复制列表，包括从这里复制。

需要三个原生连接，并且 SDK 在每个地方都会以不同的方式失败：

- 加载自入口模块并在任何其他内容之前加载的加密和文本编码polyfills
- 在 `app.json` 插件中的 `expo-secure-store` 和 `expo-web-browser`
- 一个 Metro 解析器覆盖，以便 `jose` 解析到其浏览器构建版本

每个的完整内容以及如何确认它们是否生效：[references/setup.md](references/setup.md)。
在此步骤后以原生方式重建 (`npx expo run:android`)——JS 重载不会加载新的原生模块。

## 步骤 3：挂载提供者

```tsx
import { PrivyProvider } from '@privy-io/expo'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type AppIdentity, createSolanaDevnet, MobileWalletProvider } from '@wallet-ui/react-native-kit'
import type { ReactNode } from 'react'

const cluster = createSolanaDevnet()
const identity: AppIdentity = { name: 'My App', uri: 'myapp://myapp' }
const privyAppId = process.env.EXPO_PUBLIC_PRIVY_APP_ID
const privyClientId = process.env.EXPO_PUBLIC_PRIVY_CLIENT_ID
const queryClient = new QueryClient()

export function AppProviders({ children }: { children: ReactNode }) {
  if (!privyAppId || !privyClientId) {
    throw new Error('缺少 Privy 环境变量')
  }

  return (
    <QueryClientProvider client={queryClient}>
      <PrivyProvider appId={privyAppId} clientId={privyClientId}>
        <MobileWalletProvider cluster={cluster} identity={identity}>
          {children}
        </MobileWalletProvider>
      </PrivyProvider>
    </QueryClientProvider>
  )
}
```

`PrivyProvider` 和 `MobileWalletProvider` 互不依赖，因此它们的相对嵌套是自由的——但两者都必须位于每个屏幕之上，如果下面的钩子是查询和变更，则 `QueryClientProvider` 必须位于两者之上。

故意抛出缺失环境变量。未定义的值会作为格式错误的 App ID 到达 Privy，并且会以不透明的初始化错误在更晚的时候暴露。`clientId` 在 `PrivyProviderProps` 中是类型可选的，这在这里具有误导性：Privy 的移动文档将其视为必需的，并且控制台为每个移动客户端发布一个。传递它。

## 步骤 4：等待 `isReady`

`usePrivy()` 返回的状态在 SDK 完成读取存储的令牌之前是无意义的：

| 值 | 类型 | 备注 |
| --- | --- | --- |
| `isReady` | `boolean` | 在此为 `true` 之前，其他所有内容都是临时的 |
| `user` | `User \| null` | 未认证时为 `null`——不是 `undefined` |
| `error` | `Error \| null` | 初始化失败，通常是存储访问 |
| `logout` | `() => Promise<void>` | 没有人登录时为空操作 |
| `getAccessToken` | `() => Promise<string \| null>` | 每次请求调用；永远不要缓存结果 |

```tsx
const { error, isReady, user } = usePrivy()

if (!isReady) return <Loading />
if (error) return <ErrorCard message={error.message} />
```

在 `isReady` 为 `false` 时渲染未登录状态会使已经认证的用户在每次冷启动时闪烁登录屏幕。

## 步骤 5：使用 SIWS 登录

整个集成是一个序列：生成、签署、交换。

```tsx
import { useLoginWithSiws } from '@privy-io/expo'
import type { Address } from '@solana/kit'
import { useMutation } from '@tanstack/react-query'
import { fromUint8Array, useMobileWallet } from '@wallet-ui/react-native-kit'

const siwsDomain = 'myapp.com'
const siwsUri = 'myapp://privy-login'

export function usePrivySignInMutation(address: Address) {
  const { generateMessage, login } = useLoginWithSiws()
  const { signMessages } = useMobileWallet()

  return useMutation({
    mutationFn: async () => {
      const { message } = await generateMessage({
        from: { domain: siwsDomain, uri: siwsUri },
        wallet: { address: address.toString() },
      })

      const signedPayload = await signMessages(new TextEncoder().encode(message))

      await login({ message, signature: fromUint8Array(signedPayload) })
    },
  })
}
```

仅在钱包连接后调用它——`useMobileWallet().account` 必须定义，因为 `signMessages` 否则会触发它自己的授权。

三个编码细节决定此操作是否成功：

1. **传递 `account.address`，它是 base58。** `account.addressBase64` 也存在；它是 MWA 的线格式，Privy 不会接受它。Privy 自己的配方花费三行将 base64 转换为 base58，因为它驱动原始协议——`@wallet-ui/react-native-kit` 已经为你完成了这个转换。
2. **`fromUint8Array` 产生 base64，不是 base58。** 它是 `js-base64` 的重新导出。Privy 在这里想要 base64 字符串；base58 会失败验证。
3. **不要切片字节。** `signMessages` 解析为 MWA 的 *已签署的有效负载*，而不是一个裸的 64 字节签名。将整个字节 base64 编码并传递——模板和 Privy 的配方都完全这样做。

`from.domain` 是 RFC 3986 权威：一个裸主机，没有方案和路径。`from.uri` 是一个完整的 URI，通常是你的应用的深度链接。保持两者稳定——它们嵌入在用户在钱包中看到的已签署消息中。

将钱包链接到已存在的账户，并在服务器上验证会话：[references/siws.md](references/siws.md)。

## 步骤 6：从两者中登出

```tsx
const { logout } = usePrivy()
const { disconnect } = useMobileWallet()

await logout()
await disconnect()
```

只做其中一个而不做另一个会使应用处于半登出状态。单独 `disconnect()` 保留一个活跃的 Privy 会话，但没有钱包在后面；单独 `logout()` 保留钱包授权，并在下次尝试时静默重新登录。

## 哪一方拥有什么

| 关注点 | 所有者 |
| --- | --- |
| 私钥和签名 | 钱包应用，通过 MWA |
| 连接的地址 | `useMobileWallet().account` |
| 跨设备用户身份 | `usePrivy().user` |
| 服务器可验证的会话 | `usePrivy().getAccessToken()` |
| 发送交易 | `useMobileWallet().sendTransactions` |

在此设置中，没有 Privy 签名者。用户已登录 Privy 并通过 MWA 连接是两个独立的事实，并且 UI 必须处理每种组合——最有用的是“已连接但未登录”，这是登录按钮的位置。

## 参考资料

- [references/setup.md](references/setup.md) — polyfills、Metro 配置、`app.json` 插件、环境变量以及如何验证每个都成功到达
- [references/siws.md](references/siws.md) — 深入了解 SIWS 交换、链接其他钱包、服务器端令牌验证以及没有 Wallet UI 的原始协议变体
- [references/troubleshooting.md](references/troubleshooting.md) — Privy 特定的失败及其原因

这里的模式遵循
[`expo-kit-privy`](https://github.com/solana-mobile/templates/tree/main/mobile/expo-kit-privy)，一个完整的工作应用。当此文件不明确时，请阅读它：

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-privy --skip-install
```

## 相关技能

- `solana-mobile-wallet` — MWA 连接、签名和发送，这是此方案构建的基础
- `solana-mobile` — 开发版本、模拟器、工具链检查
- `seeker-genesis-token` — 没有 Privy 的 SIWS 服务器端验证，当 JWT 过于复杂时

## 链接

- Privy Solana MWA 配方：https://docs.privy.io/recipes/solana/adding-solana-mwa
- Privy Expo SIWS 登录：https://docs.privy.io/guide/expo/authentication/siws
- Privy 控制台：https://dashboard.privy.io
