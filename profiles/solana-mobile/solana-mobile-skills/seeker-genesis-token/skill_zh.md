# Seeker Genesis Token 验证

Seeker Genesis Token (SGT) 是每个 Seeker 设备上一次铸造的 Token-2022 NFT。持有其中一个
是拥有 Seeker 的证明，这使其适用于门控奖励和每设备限领逻辑。

验证分为两个部分，**两者都必须满足**：

1. **证明用户控制钱包** — Solana 登录 (SIWS)
2. **证明钱包持有 SGT** — 检查钱包的 Token-2022 铸造记录

仅执行第二项意味着任何人都可以提交真实 Seeker 拥有者的公钥并通过。
仅执行第一项可以证明钱包控制，但无法说明设备信息。

## 必须在服务器上运行

**绝不能在客户端决定权限。** 客户端可能被篡改，因此客户端的 `hasSGT` 布尔值毫无价值。客户端的任务是收集签名；服务器验证它并拥有结果。

要求：

- 一个你可以控制的能够进行 Solana 主网 RPC 调用的后端
- 用于存储随机数和领奖记录的存储空间
- 一个 RPC 端点。付费提供商会有所帮助，因为检查可能枚举许多代币账户 — 将该密钥仅存储在服务器端，绝不能在 `EXPO_PUBLIC_*` 变量中

## 前置条件

一个可工作的钱包连接。如果应用没有，首先使用 `solana-mobile-wallet` 技能；该技能假设 `useMobileWallet()` 可用。

测试需要一个物理 Seeker 设备 — 模拟器无法持有 SGT。计划一个无需设备的代码路径，例如开发中的服务器端允许列表。

## 第 1 步：从服务器发出负载

服务器发出**完整的** SIWS 负载，而不仅仅是随机数，并将其存储在随机数下，并设置较短的 TTL。客户端提供的每个字段都是攻击者选择的字段，并且每个字段都直接输入签名检查，因此请在发出时固定所有字段。

```ts
// POST /api/siws/nonce
const issuedAt = new Date()
const nonce = crypto.randomBytes(16).toString('hex')

const payload = {
  chainId: 'solana:mainnet',
  domain: 'yourdapp.com',
  expirationTime: new Date(issuedAt.getTime() + 300_000).toISOString(),
  issuedAt: issuedAt.toISOString(),
  nonce,
  statement: '登录以验证 Seeker 拥有',
  uri: 'https://yourdapp.com',
  version: '1',
}

await store.put(nonce, payload, { ttlSeconds: 300 })
return payload
```

随机数必须是**服务器生成、单次使用、短寿命**的。客户端生成或可重用的随机数会使签名可重放，这会破坏验证。

`address` 是服务器无法填写的唯一字段。客户端在步骤 2 中添加它。

`chainId` 是故意固定为 `solana:mainnet` 而不是从钱包的 `chain` 中获取：SGT 仅存在于主网，因此针对 devnet 的签名对设备证明毫无意义。服务器端发出它将此转换为保证而不是评论。

## 第 2 步：在客户端登录

`signIn` 从钱包钩子授权并证明所有权，通过单个提示。传播发出的负载并添加地址：

```ts
import { useMobileWallet } from '@wallet-ui/react-native-kit'

const { signIn } = useMobileWallet()

const issued = await fetch('https://yourdapp.com/api/siws/nonce', { method: 'POST' }).then(
  (response) => response.json(),
)

const address = account.address.toString()
const output = await signIn({ ...issued, address })

await fetch('https://yourdapp.com/api/siws/verify', {
  body: JSON.stringify({
    address,
    nonce: issued.nonce,
    signature: Array.from(output.signature),
    signedMessage: Array.from(output.signedMessage),
  }),
  headers: { 'Content-Type': 'application/json' },
  method: 'POST',
})
```

仅发送这四个字段。**不要发送 `output.account`，并且服务器绝不能接受来自客户端的账户对象或公钥** — 签名检查所使用的密钥必须从服务器即将操作的地址派生。第 3 步将说明原因。
`nonce` 仅是查找键；签名检查才是绑定它的关键。

这是完全指定的负载，而不是简短的 `signIn` 表单。`domain`、`nonce` 和 `version` 使签名不可重放并绑定到你的应用，并且服务器必须为这有效果发出它们。`solana-mobile-wallet` 技能涵盖了两种表单以及何时使用每种表单。

## 第 3 步：在服务器上验证签名

```bash
npm install @solana/kit @solana/wallet-standard-util
```

```ts
import { getBase58Encoder } from '@solana/kit'
import { verifySignIn } from '@solana/wallet-standard-util'

function verifySiws(issued, { address, signature, signedMessage }) {
  // 在 ed25519 验证内部，拒绝格式错误的输入。
  if (!Array.isArray(signature) || signature.length !== 64) {
    throw new Error('格式错误的签名。')
  }
  if (!Array.isArray(signedMessage)) throw new Error('格式错误的已签名消息。')

  // 从地址派生验证密钥，绝不能从请求正文派生。
  const publicKey = getBase58Encoder().encode(address)
  if (publicKey.length !== 32) throw new Error('格式错误的地址。')

  return verifySignIn(
    { ...issued, address },
    {
      account: { address, chains: [], features: [], publicKey },
      signature: new Uint8Array(signature),
      signedMessage: new Uint8Array(signedMessage),
    },
  )
}
```

这三个形状检查首先进行，因为每个值都是攻击者选择的。如果没有它们，格式错误的案例会到达 `new Uint8Array()` 然后是 ed25519 验证，在那里它们不一致：短签名会引发库错误关于字节长度，而非数组的 `signedMessage` 会强制为空数组并返回一个简单的 `false`。在形状上拒绝提供清晰答案，并且不依赖你无法控制的内部。

`verifySignIn` 将你传递给它的字段与已签名文本内的字段进行比较，然后用 `account.publicKey` 验证签名。**它从不检查密钥和地址是否一致。** 从请求正文中获取该密钥，任何一次性密钥对都可以签名一个命名任何地址的消息：签名是真实的，但它不是地址持有者的。

因为服务器发出了 `issued`，`domain` 和 `chainId` 是构建时固定的。没有客户端的任何副本到达检查，因此无需单独的域名比较。如果你仍然想进行防御性断言，请断言 `issued.domain` — 存储的副本 — 绝不能请求中的值。

## 第 4 步：检查钱包是否持有 SGT

参见 [references/sgt-verification.md](references/sgt-verification.md) 获取完整实现。它确认 Token-2022 铸造的三个属性 — 铸造授权、元数据指针和代币组成员资格 — 并且必须全部匹配。

## 第 5 步：正确组合检查

这是微妙错误存在的位置。`verifySignIn` 不会将账户密钥绑定到已签名消息中的地址，因此服务器必须自己执行绑定：从它将要操作的地址派生密钥，并针对相同的地址查找 SGT。

```ts
async function verifySeekerUser({ address, nonce, signature, signedMessage }) {
  // 1. 原子地消耗随机数。读后标记会在两个并发请求都看到它未使用的情况下留下一个窗口，并且一个签名被接受两次。
  //    Redis: GETDEL. SQL: 从 nonces 删除 nonce = $1 返回 payload。
  const issued = await store.consume(nonce)
  if (!issued) throw new Error('无效、重复使用或过期的随机数。')

  // 2. 签名必须对我们在步骤 1 中发出的负载和此地址有效。
  if (!verifySiws(issued, { address, signature, signedMessage })) {
    throw new Error('无效的签名。')
  }

  // 3. 检查 SGT 与刚刚验证的签名对应的地址。
  const { hasSGT, mintAddress } = await checkWalletForSGT(address)

  return { address, hasSGT, mintAddress }
}
```

检查 SGT 对任何其他地址都会让调用者提交真实 Seeker 拥有者的地址和自己的签名并获得访问权限。

## Anti-Sybil：每设备限领一次

SGT 是每设备一个，因此**铸造地址**是设备身份。存储它，而不是钱包地址 — 钱包可以持有不同的 SGT，并且设备的 SGT 可以在钱包之间移动。

一个 `UNIQUE` 约束是强制每设备限领，而不是应用代码：

```sql
CREATE TABLE claims (
  claimed_at timestamptz NOT NULL DEFAULT now(),
  mint_address text NOT NULL UNIQUE,
  paid_at timestamptz
);
```

```ts
const { address, hasSGT, mintAddress } = await verifySeekerUser(request.body)
if (!hasSGT) throw new Error('未找到 Seeker Genesis Token。')

// 首先插入并让约束决定。询问是否存在行然后插入会导致双领奖错误：两个并发请求都找不到。
try {
  await claims.insert({ claimedAt: new Date(), mintAddress })
} catch (error) {
  // 23505 是 Postgres 的唯一违反。其他驱动程序报告它不同。
  if (error.code === '23505') throw new Error('此设备已经领奖。')
  throw error
}

// 仅在插入完成后才支付。在它之前支付的任何内容都可能被支付两次。
await grantReward(address)
await claims.markPaid(mintAddress)
```

插入和支付是两个独立的写入，因此决定当第二个写入失败时会发生什么。如所写，一个在行提交后抛出错误的 `grantReward` 会让该设备无法重试：约束现在会拒绝它为已领奖。要么让重试依赖于具有 null `paid_at` 的行，要么让 `grantReward` 在 `mintAddress` 上幂等，以便重放它是免费的。
这一个是鲁棒性而不是安全性：如果做得不对，会拒绝真实所有者的奖励，它不会让任何人双领奖。

让 `checkWalletForSGT` 返回铸造地址而不是一个简单的布尔值 — 参见参考文件的末尾。

## 参考材料

- [references/sgt-verification.md](references/sgt-verification.md) — 完整验证
  实现、SGT 常量、标准-RPC 和 Helius 变体

## 相关技能

- `solana-mobile-wallet` — 钱包连接和两个 `signIn` 负载表单
- `seeker-domains` — `.skr` 域名解析，Seeker 用户默认具有

## 链接

- 检测 Seeker 用户：https://docs.solanamobile.com/react-native/detecting-seeker-users
- Sign-in-with-Solana 规范：https://github.com/phantom/sign-in-with-solana
