# 移动端 Solana 钱包

通过移动钱包适配器（MWA），结合 `@wallet-ui/react-native-kit`（或 `@wallet-ui/react-native-web3js` 在旧版堆栈上）实现钱包连接和交易签名。

**MWA 需要在 Android 上使用开发版本。Expo Go 无法工作。** 如果项目还没有开发版本，或者项目不存在，可以从 `solana-mobile` 技能开始。

## 第 1 步：选择堆栈 — 在编写任何代码之前完成

**编写 kit 代码。** `@solana/kit` 与 `@wallet-ui/react-native-kit` 是推荐的堆栈，本文件中描述了所有相关内容。

只有一种原因需要使用 `@solana/web3.js`：项目已经基于它运行。首先检查 `package.json`。

| `package.json` 显示 | 执行此操作 |
| --- | --- |
| `@wallet-ui/react-native-kit`，或尚未有 Solana 客户端 | Kit。本文件，加上 [references/kit.md](references/kit.md) |
| `@wallet-ui/react-native-web3js` 是应用的 Solana 客户端 | [references/web3js.md](references/web3js.md) |
| 用户明确要求使用 web3.js | [references/web3js.md](references/web3js.md)，并说明为什么 kit 更好 |

不要将 web3.js 引入 kit 项目，或在单个应用中混合使用两者。它们的提供者属性、钩子返回值和交易构建方式都不同，因此来自一个项目的代码在另一个项目上会静默失败。如果项目根本没有 Solana 客户端，那是一个新项目 — 使用 kit。

将 *新* 钱包功能添加到现有的 web3.js 应用中并不是中途迁移的理由。匹配现有内容，如果认为值得，可以在后续提及迁移。

## 第 2 步：确认提供者已挂载

`useMobileWallet` 在其上方没有 `MobileWalletProvider` 时返回空状态。在根布局或应用提供者模块中查找它。

使用 `createSolana*` 辅助函数构建集群，而不是手动构建 — `SolanaCluster` 还需要一个 `label`，辅助函数会自动填充：

```tsx
import {
  type AppIdentity,
  createSolanaDevnet,
  MobileWalletProvider,
  type SolanaCluster,
} from '@wallet-ui/react-native-kit'

const identity: AppIdentity = { name: '我的应用' }
const cluster: SolanaCluster = createSolanaDevnet({ url: 'https://api.devnet.solana.com' })

<MobileWalletProvider cluster={cluster} identity={identity}>
  {children}
</MobileWalletProvider>
```

`createSolanaDevnet`、`createSolanaTestnet` 和 `createSolanaLocalnet` 接受可选属性；`createSolanaMainnet` 需要 `url`，因为主网没有合理的公共默认值。

提供者属性是 `cluster`、`identity` 和可选的 `cache`、`createClient`、`children`。**没有 `chain` 属性，也没有 `endpoint` 属性** — 传递这些属性没有任何作用。

`AppIdentity` 的每个字段都是可选的。仅 `name` 足够开始；作为实际深度链接添加 `uri`，因为钱包在授权期间显示它，而占位符可能会被误认为是钓鱼尝试。

将 `@tanstack/react-query` 的 `QueryClientProvider` 放在钱包提供者上方 — 下面的钩子模式是查询和变异。

## 第 3 步：使用钩子

```tsx
import { useMobileWallet } from '@wallet-ui/react-native-kit'

const { account, connect, disconnect, client } = useMobileWallet()
```

在 kit 堆栈上，钩子实际返回的值：

| 值 | 类型 | 备注 |
| --- | --- | --- |
| `account` | `Account \| undefined` | 断开连接时为 `undefined`，不是 `null` |
| `accounts` | `Account[] \| null` | 所有授权账户 |
| `connect` | `() => Promise<Account>` | 打开钱包选择器 |
| `disconnect` | `() => Promise<void>` | |
| `client` | `Client` | Kit 客户端 — 使用 `client.rpc` 进行 RPC 调用 |
| `chain` | `SolanaClusterId` | 活跃集群。将其放入查询键中 |
| `sendTransactions` | `(instructions: Instruction[]) => Promise<string>` | 最简单的发送路径 |
| `signAndSendTransaction` | `(tx, minContextSlot) => Promise<SignatureBytes>` | 注意第二个参数 |
| `signTransaction` | `(tx) => Promise<Transaction>` | 不广播的签名 |
| `signMessages` | `(msg: Uint8Array) => Promise<Uint8Array>` | |
| `signIn` | `(payload) => Promise<SignInOutput>` | 使用 Solana 进行签名；也可以连接 |
| `identity`, `store` | | 配置和授权存储 |

对于其中几个，存在单数别名 — `sendTransaction`、`signMessage`、`signTransactions` — 具有相同的签名。模板使用复数形式；两者都可以，因此跟随项目已经使用的任何一种。

让四个容易让人困惑的地方：

1. **没有 `connected` 布尔值。** 推导它：`const connected = !!account`。
2. **`signAndSendTransaction` 将 `minContextSlot` 作为第二个参数。** 仅传递交易调用它会失败。从 `getLatestBlockhash` 获取槽位，或使用 `sendTransactions(instructions)`，它会为您处理此问题。
3. **kit 钩子暴露 `client`，而不是 `connection`。** `connection` 仅存在于 web3.js 堆栈上。
4. **在所有持有链数据的 React Query 键中包含 `chain`。** 否则切换集群会提供先前网络的缓存余额，看起来像钱包错误。

`account.address` 是 kit 的 `Address`（一个品牌化字符串），因此可以直接插值到文本中。`account.label` 是钱包提供的名称，可能未定义。

## 连接和断开连接

```tsx
import { Pressable, Text } from 'react-native'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function ConnectButton() {
  const { account, connect, disconnect } = useMobileWallet()

  async function onPress() {
    try {
      if (account) await disconnect()
      else await connect()
    } catch (error) {
      // 用户取消钱包选择器会进入此处。不要将其视为崩溃。
      console.error(error)
    }
  }

  return (
    <Pressable onPress={onPress}>
      <Text>{account ? '断开连接' : '连接钱包'}</Text>
    </Pressable>
  )
}
```

始终用 try/catch 包裹 `connect()` — 取消钱包选择器会拒绝承诺。取消是一个正常的结果，不是值得向用户发出警报的错误状态；请参阅 [references/kit.md](references/kit.md) 了解如何区分取消和实际失败。

授权是缓存的，因此应用在重新启动时无需新提示即可重新连接。

## 读取链数据

使用钩子中的 `client`。没有必要自己构建客户端：

```tsx
import type { Address } from '@solana/kit'
import { useQuery } from '@tanstack/react-query'
import { useMobileWallet } from '@wallet-ui/react-native-kit'

export function useGetBalance({ address }: { address: Address }) {
  const { chain, client } = useMobileWallet()

  return useQuery({
    queryFn: () => client.rpc.getBalance(address).send(),
    queryKey: ['get-balance', chain, address],
  })
}
```

Kit RPC 调用是惰性的：`client.rpc.someMethod(...)` 构建请求，`.send()` 运行它。忘记 `.send()`，没有任何错误 — 数据只是不会到达。

余额以 `bigint` lamports 返回。故意转换，并且永远不要用 `parseFloat`：

```ts
export function lamportsToSol(lamports: bigint) {
  return Number(lamports) / 1e9
}
```

## 发送交易

构建指令并交出。这涵盖了大多数情况：

```tsx
import { getAddMemoInstruction } from '@solana-program/memo'
import type { Instruction } from '@solana/kit'

const { sendTransactions } = useMobileWallet()

const instructions: Instruction[] = [getAddMemoInstruction({ memo: 'gm' })]
const signature = await sendTransactions(instructions)
```

`sendTransactions` 处理 blockhash、`minContextSlot`、费用支付者和签名解码。它在钱包提交后立即返回，因此确认签名后再将交易视为完成 — [references/kit.md](references/kit.md#confirming-a-transaction) 有辅助工具。

仅在需要费用支付者控制、特定 blockhash 生命周期或费用预检查时使用显式的 `pipe` 形式。完整的示例，包括余额与费用断言和签名解码：[references/kit.md](references/kit.md)。

## 参考资料

- [references/kit.md](references/kit.md) — kit 堆栈：集群和配置、读取链数据、交易、使用 Solana 进行签名、消息签名、错误处理
- [references/web3js.md](references/web3js.md) — 旧版 `@solana/web3.js` 堆栈，以及迁移草图
- [references/troubleshooting.md](references/troubleshooting.md) — 具有已知原因的连接和签名失败

当此处内容不明确时，请阅读模板。此技能中的模式遵循 [`expo-kit-minimal`](https://github.com/solana-mobile/templates/tree/main/mobile/expo-kit-minimal)，这是一个完整的应用程序，并以与文字描述不同的方式保持最新：

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-minimal --skip-install
```

## 检查是钱包还是应用出了问题

在调试连接或签名代码之前，在没有应用参与的情况下运行相同的流程：

```bash
npx solana-mobile@latest device install fakewallet   # 如果设备没有钱包
npx solana-mobile@latest playground
```

`playground` 在设备上提供钱包测试页面，并将每个 MWA 交互（连接、签名、签名消息、签名交易、签名并发送）流回终端。如果它也失败了，那么错误在于钱包或设备，而不是此代码。`solana-mobile` 技能涵盖了这两个命令。

## 相关技能

- `solana-mobile` — 项目设置、模板、模拟器、开发版本
- `integration-privy` — 在此钱包连接之上添加 Privy 账户和会话
- `seeker-genesis-token` — 连接后验证 Seeker 设备所有权
- `seeker-domains` — 显示 `.skr` 名称，而不是原始地址

## 链接

- Wallet UI: https://wallet-ui.dev
- MWA 文档: https://docs.solanamobile.com/react-native/overview
- Solana Kit: https://www.solanakit.com
