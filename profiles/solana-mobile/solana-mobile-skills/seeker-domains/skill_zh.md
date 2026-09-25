# .skr 域名解析

`.skr` 域名是 Solana 主网上的 AllDomains 域名。Seeker 用户默认获得一个，这使得它们成为 UI 中截断地址的绝佳替代品。

两个方向：

- **正向** — `alice.skr` 解析到钱包地址
- **反向** — 钱包地址解析到其拥有的 `.skr` 域名

两者都存在于 **主网** 上，无论其余应用目标哪个集群。运行在 devnet 上的应用仍然解析主网上的名称。

## 确定解析运行位置

解析读取链上公共数据，因此客户端可以直接执行。当您需要以下功能时，通过后端代理它：

- **RPC 密钥保护。** `EXPO_PUBLIC_*` 中的密钥可被任何拥有 APK 的人读取。如果您使用付费 RPC，则必须在服务器端执行。
- **共享缓存。** 名称很少更改。一个服务器端缓存胜过所有客户端重新解析相同地址。
- **批量查询。** 一次性请求解析整个好友列表胜过手机上的 N 次往返。
- **`getProgramAccounts` 访问。** 反向查询需要它，而且许多提供商会禁用或对该方法进行严格速率限制。针对您已验证的提供者的一个服务器端端点胜过在用户设备上发现限制。

对于原型或低流量应用，直接针对公共 RPC 的客户端解析是合理的。公共端点是速率限制的，因此它无法承受一个解析数十个地址的列表视图。

如果项目不明显，请询问用户的选择。默认情况下，为生产环境使用代理。

## 与现有后端集成

**在编写新服务器之前检查现有内容。** 在某个人的 NestJS 服务旁边添加一个 Express 应用程序是维护上的混乱。

1. 查找每个 `package.json` 中的后端依赖项 — `express`、`fastify`、`hono`、`@nestjs/core`、`koa` 或带有 API 路由的 Next.js 应用程序。
2. 查找入口点：`server.ts`、`app.ts`、`main.ts`、`index.ts`。
3. 查找路由组织：`routes/`、`api/`、`controllers/`。
4. 如果仍然不明确，请询问 — "我在 `apps/api` 中看到一个 Fastify 服务器；`.skr` 端点应该放在那里吗？"

将路由添加到现有内容中，匹配其路由、验证和错误处理的约定。只有在确实没有后端时才搭建一个最小的服务器。

## 核心解析逻辑

解析是框架无关的；只有围绕它的路由会变化。两个选项，默认是第一个。

### Kit（默认）

`.skr` 域名是 AllDomains（ANS）账户，解析一个域名是一个 PDA 派生加上一个单个账户读取 — 足够小，可以直接拥有，而不是使用 SDK。

```bash
npm install @solana/kit "@noble/hashes@^1"
```

将 `@noble/hashes` 固定为 `^1`。现在裸装安装会给出 2.x，其 `exports` 映射会删除无扩展名的 `./sha2` 子路径。解析器导入 `@noble/hashes/sha2.js`，两者都接受此版本，因此即使固定版本失效，它也能在升级中存活下来。

```ts
import { address, createSolanaRpc } from '@solana/kit'
import { resolveSkrDomain, resolveSkrNames } from './skr'

// 始终为主网，无论其余应用目标哪个集群。
const rpc = createSolanaRpc(process.env.SOLANA_MAINNET_RPC_URL)

const owner = await resolveSkrDomain(rpc, 'alice.skr') // 地址，或 null
const names = await resolveSkrNames(rpc, address('5FHw...')) // ['alice.skr']，已排序
```

从 [references/kit-resolver.md](references/kit-resolver.md) 复制实现 — 大约 140 行，在 `tsc --strict` 下类型检查，并且没有 `Buffer`/`TextEncoder`，因此同一个文件可以在服务器和 React Native 上运行。它接受 `alice.skr` 或 `alice`，对未注册的名称返回 `null`，并且只有在 RPC 本身失败时才会拒绝。

当您需要 ANS 记录、头像或用户的 `MainDomain`（他们选择的名称）时，这些都没有在辅助程序中实现，请使用 SDK。

### @onsol/tldparser（替代方案）

```bash
npm install @onsol/tldparser @solana/web3.js
```

```ts
import { TldParser } from '@onsol/tldparser'
import { Connection } from '@solana/web3.js'

const connection = new Connection(process.env.SOLANA_MAINNET_RPC_URL, 'confirmed')
const parser = new TldParser(connection)

// 正向：传递完整的域名，包括 `.skr` 后缀。
const owner = await parser.getOwnerFromDomainTld('alice.skr')

// 反向：TLD 不带点。返回 [{ nameAccount, domain: 'alice.skr' }]。
const domains = await parser.getParsedAllUserDomainsFromTld(publicKey, 'skr')
```

四个需要正确处理的地方，所有内容都在 1.2.1 主网上验证：

- **`getOwnerFromDomainTld` 需要完整的域名。** `'alice.skr'` 解析；`'alice'` 抛出。它按 `.` 分割并使用第二个段作为 TLD，因此一个裸名称会在 TLD `.undefined` 下派生 PDA 并找到 nothing。
- **它抛出而不是返回 null，并且未注册的名称与格式错误输入无法区分** — 两者都表现为 `TypeError: Cannot read properties of undefined (reading 'owner')`，因为 SDK 未检查名称记录就进行了解引用。将每个调用包装在 `try`/`catch` 中；永远不要基于 falsy 返回进行分支。要区分两者，请调用 `getNameRecordFromDomainTld(domain)`，它会在缺少账户时干净地返回 `undefined`。
- **`getParsedAllUserDomainsFromTld` 需要不带点的 TLD。** `'skr'` 有效；`'.skr'` 悄然返回 `[]`。每个结果的 `domain` 字段已经包括后缀。
- **反向查询返回一个数组。** 一个地址可以拥有多个 `.skr` 域名，顺序不是排名。排序并取第一个，否则显示名称会在调用之间改变。排序使标签稳定，而不是可信 — 见 [信任反向解析的名称](#信任反向解析的名称)。

它的 ESM 构建也是损坏的 — 见 [references/server.md](references/server.md#onsoltldparser-alternative) 和 `createRequire` 工作绕过。

## API 形状

两个端点，适应于使用的框架：

| 路由 | 请求体 | 成功 | 未找到 |
| --- | --- | --- | --- |
| `POST /api/resolve-domain` | `{ domain: "alice.skr" }` | `{ address }` | 404 |
| `POST /api/resolve-address` | `{ address: "5FHw..." }` | `{ domain }` | 404 |

在触摸 RPC 之前验证输入：拒绝格式错误的 base58 地址或不以 `.skr` 结尾的域名，以 400 错误拒绝，这样坏输入不会消耗 RPC 配额。

区分 "未注册域名"（404）和 "RPC 失败"（503）。将两者都折叠为 404 使停机看起来像每个用户都没有名称。

一个存在的代理必须不是其前面的开放中继。反向路由需要 `getProgramAccounts` 加上对地址拥有的每个名称的批量读取，因此端点需要一个来源白名单、每 IP 速率限制、请求体限制和存储负结果的缓存。在启动时要求 RPC URL 和来源列表，而不是回退到公共端点或打开 CORS。

完整的 Express 和 Hono 实现，以及 Fastify、NestJS、Koa 和 Next.js 路由处理器的说明：[references/server.md](references/server.md)。

## 客户端集成

```ts
const { data: domain } = useResolveAddress(account?.address)
const label = domain ?? ellipsify(account?.address)
```

始终回退到截断地址。一个解析失败的名称应该降级到可用的内容，而不是空白空间或一个永远不会解析的加载动画。

对于 Android 模拟器，`localhost` 是模拟器本身。连接到主机机器的 `http://10.0.2.2:3000`。在物理设备上使用主机的局域网 IP。将它们硬编码到源代码会破坏应用对下一个人的可用性 — 从 `EXPO_PUBLIC_API_URL` 读取，并使用 `__DEV__` 门控任何模拟器回退：`EXPO_PUBLIC_*` 在构建时内联，因此未门控的默认值会在发布 APK 中发送一个死的明文 URL，而 Android 默认会阻止它。任何带有 RPC 密钥的内容都不应存在于 `EXPO_PUBLIC_*` 变量中 — 那就是代理的作用。

上面的代码片段假设了代理。如果您直接从应用解析，则 Kit 解析器在 Hermes 下运行不变 — 从同一个钩子调用它，而不是 `fetch`。

钩子、组件和截断辅助程序：[references/client.md](references/client.md)。

### 信任反向解析的名称

反向解析的名称是一个地址碰巧拥有的第一个排序名称，而 `.skr` 转移不需要接收方 — 任何人都可以将名称推送到任何钱包。因此，一个陌生人可以通过注册一个排序靠前的名称并将其发送过来，来决定您的 UI 称呼用户。

- **在截断地址旁边显示名称，而不是替换它。** 地址是用户可以实际检查的部分。
- **在标签代表身份的地方** — 付款对象、交易对手、审核表面 — 优先考虑所有者的 `MainDomain`，他们选择的名称。这是 `@onsol/tldparser` 的 `getMainDomain`，当用户从未设置过时它会抛出；将抛出视为 "无" 并回退到地址。
- **反向查询必须尊重过期。** 一个过期的名称仍然解析，会继续用其所有者已失去的名称标记地址。

### 按方向缓存

| 方向 | 数据源 | 缓存 |
| --- | --- | --- |
| 正向（名称 → 地址） | 付款目的地 | 无。发送时重新解析。 |
| 反向（地址 → 名称） | 显示标签 | 长的 `staleTime`；一小时可以。 |

名称很少更改，因此缓存反向结果是几乎免费的。正向结果不同：`.skr` 域名是可转移和重新注册的，因此缓存一小时的正向结果并在签名时使用，会支付一小时前拥有该名称的人，而 UI 看起来没有问题。在签名前立即重新解析，并将解析的地址放在确认步骤中，以便用户看到资金实际去向。

这必须在 **双方** 都成立。一个在发送时重新解析的客户端如果代理从自己的正向缓存中回答，将一无所获，因此服务器仅缓存正向未命中，永远不会缓存解析的地址。

## 参考材料

- [references/kit-resolver.md](references/kit-resolver.md) — 默认解析器、`.skr` 域名如何在链上存储以及辅助程序故意省略的内容
- [references/server.md](references/server.md) — Express 实现、其他框架、验证和错误处理
- [references/client.md](references/client.md) — 解析钩子、显示组件、模拟器网络

## 相关技能

- `solana-mobile-wallet` — 提供要解析地址的钱包连接
- `seeker-genesis-token` — 验证 Seeker 拥有

## 链接

- AllDomains 开发者指南：https://docs.alldomains.id/protocol/developer-guide/ad-sdks/svm-sdks/solana-mainnet-sdk
- `@onsol/tldparser`：https://www.npmjs.com/package/@onsol/tldparser
- `@onsol/tldparser` 源代码，用于账户布局：https://github.com/onsol-labs/tld-parser
- `@solana/kit`：https://www.npmjs.com/package/@solana/kit
