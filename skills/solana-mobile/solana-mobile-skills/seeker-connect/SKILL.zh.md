---
name: seeker-connect
description: 通过 Seeker Connect 将网页 dApp 连接到 Seeker 设备的内置钱包。在以下场景中使用：为运行在 Seeker 手机浏览器上的网站添加钱包连接、通过 Solana 登录、消息签名或交易签名功能；注册“Seeker Connect” Wallet Standard 钱包；选择 relayDomain 的 Nostr relay；使用 seeker-connect-button 元素；或调试类似 association-failed 的 SeekerConnectError 错误代码。
---

# Seeker Connect for web dapps

Seeker Connect将浏览器**在设备上**打开的网页链接到Solana Mobile认证设备的钱包——Seeker是首款此类设备。它是一个dapp专用的SDK，构建在官方Mobile Wallet Adapter库之上：是一个UX/DX层，而非协议重实现。通用MWA侧重于“选择钱包”的选项器，而Seeker Connect通过MWA规范的Endpoint特定URI（Android App Link）机制直接启动设备钱包，通过Nostr中继传递会话，并使用Seeker品牌的进度和错误UI——所有这些都以普通Wallet Standard钱包的形式**“Seeker Connect”**的形式暴露给应用程序。

目标：**Web目前可用。** 计划支持React Native和Android（Kotlin）。在它们发布之前，Expo或React Native应用内的钱包连接使用`solana-mobile-wallet`技能。

## 思维模型——编写代码前请阅读

- **没有持久的连接。** 每个钱包交互（连接、签名消息、签名交易）都会打开自己的短-lived MWA会话，运行一个请求，然后关闭。每次交互都会启动钱包应用并显示品牌化的进度覆盖层——唯一的例外是静默连接，它只读取缓存，从不打开会话。这是设计如此——不要围绕它构建重连循环或保持活动逻辑。
- **“已连接”意味着“持有缓存的授权。** 首次`connect()`存储钱包发布的`authToken`以及账户和功能（默认为localStorage）。后续操作会静默重放该令牌——不会重复提示同意。
- **断开连接仅本地忘记令牌。** 它故意从不调用钱包的`deauthorize`，因为那样会启动钱包应用来进行断开连接。
- **它只在设备上完成。** 在桌面端，连接会以`association-failed`失败——通常在几秒钟内，当没有任何应用响应钱包启动时；关联超时仅适用于启动但从未连接的钱包。无条件注册钱包——它只是在其他地方无法通过关联。
- **中继是一个公共的Nostr中继，SDK不提供默认中继。** 除非开发者指定，否则使用步骤2中的验证默认值。Solana Mobile自己的中继在用户接受使用条款后才提供，并且永远不会属于你。

## 第1步：安装

**新项目：** Solana Mobile CLI的`react-kit-shadcn`模板已预装Seeker Connect，使用与步骤2相同的默认中继：

```bash
npx solana-mobile@latest create my-app --template react-kit-shadcn
```

**现有应用：** 安装Wallet Standard入口点以及以下代码片段导入的Wallet Standard辅助工具：

```bash
npm install @solana-mobile/seeker-connect-wallet-standard @solana/wallet-standard-features @wallet-standard/app @wallet-standard/features
```

Wallet Standard包会引入其他Seeker Connect包（`core`、`ui`、`web`）作为依赖项。尽管它们没有被重新导出——因此，如果应用直接导入它们中的任何包（`@solana-mobile/seeker-connect-ui`用于下方的可选按钮，`@solana-mobile/seeker-connect-web`用于引用中的命令式路径），也需要安装它们；像pnpm这样的严格包管理器会拒绝导入未声明的传递依赖项。

| 包 | 角色 |
| --- | --- |
| `@solana-mobile/seeker-connect-core` | 共享合约：配置、错误分类、`SeekerLink`端口 |
| `@solana-mobile/seeker-connect-ui` | Lit元素：进度覆盖层、错误对话框、品牌化按钮 |
| `@solana-mobile/seeker-connect-wallet-standard` | **入口点**——Wallet Standard钱包 |
| `@solana-mobile/seeker-connect-web` | MWA-over-Nostr传输，以及一个命令式SDK |

## 第2步：选择中继

Seeker Connect通过Nostr中继承载MWA的扩展远程通信协议，由`relayDomain`命名。每个会话都会生成一个新的Nostr密钥对并发布临时事件（kind 20012），因此中继必须接受它从未见过的公钥的临时事件——无需身份验证、支付、允许列表或信任网络检查。有效载荷在dapp和钱包之间端到端加密；中继携带密文，因此一个不良的中继会影响可用性而非机密性。

**默认使用`relay.primal.net`。** 在重复探测（2026年9月）中，它满足该要求：每个kind 20012事件都被接受和传递，无速率限制，有资金的操作员，Cloudflare anycast前置。从应用的环境配置中读取它（例如`VITE_SEEKER_RELAY_DOMAIN`变量），将其作为备用值，以便开发者无需代码更改即可切换中继。

**Solana Mobile的中继由开发者提供，而非你。** Solana Mobile运行一个更快的中继，但其域名仅在Seeker Connect快速入门页面上发布，需要开发者点击通过使用条款：
https://docs.solanamobile.com/solana-mobile-stack/seeker-connect-quickstart

- **切勿将Solana Mobile中继域名自行写入应用**——无论是从记忆中、从其他项目中复制、从搜索结果中。接受条款是开发者的行为，他们接受的页面是唯一提供域名的位置。如果开发者需要，将他们带到那里，让他们粘贴回值。
- **不要编造任何其他主机名。** 许多公共中继会拒绝未知的公钥或临时kind，并且失败会在稍后以`association-failed`的形式出现，而不是清晰的配置错误。坚持默认值、开发者命名的中继，或来自
  [references/troubleshooting.md](references/troubleshooting.md#association-failed-on-every-connect)中验证列表的中继。

## 第3步：启动时注册一次

在UI渲染之前调用`registerSeekerConnect`，以便钱包发现从第一次渲染就能看到它。它必须在浏览器中运行——以下代码片段读取`window`，因此在使用SSR（Next.js等）的情况下，将调用放在客户端仅模块中或用`typeof window !== 'undefined'`进行保护；在纯客户端渲染的应用中，入口文件的模块作用域即可：

```ts
import { registerSeekerConnect } from '@solana-mobile/seeker-connect-wallet-standard';

registerSeekerConnect({
  identity: {
    name: '我的Dapp',
    uri: window.location.origin,
    icon: '/icon.png', // 相对于uri解析；在钱包的同意UI中显示
  },
  relayDomain: 'relay.primal.net', // 验证的公共默认值；第2步涵盖覆盖它
});
```

配置：

| 选项 | 必填 | 备注 |
| --- | --- | --- |
| `associationTimeoutMs` | 否 | 启动可能需要多长时间才会`association-failed`。默认30秒 |
| `chain` | 否 | 授权时请求的链。默认`solana:mainnet` |
| `firstConnectWalletBaseUri` | 否 | **除非Solana Mobile发布要粘贴的值，否则留空**。未设置，首次连接使用通用的`solana-wallet:`方案；设置，页面导航到该主机——见[references/troubleshooting.md](references/troubleshooting.md#first-connect-opens-a-generic-wallet-chooser) |
| `identity` | 是 | `name`、`uri`、可选的`icon`。在钱包的同意UI中显示 |
| `relayDomain` | 是 | 承载会话流量的Nostr中继。默认为`relay.primal.net`——第2步 |

`registerSeekerConnect`还接受`seekerLink`、`authorizationCache`和`presenter`覆盖——见[references/imperative-api.md](references/imperative-api.md)。

## 第4步：像其他钱包一样使用

注册后，“Seeker Connect”会出现在Wallet Standard注册表中，因此wallet-adapter、ConnectorKit、`@solana/react-hooks`或原始`@wallet-standard/app`会自动获取它，无需进一步连接。现有的连接按钮和签名代码仍然有效。

暴露的功能：`standard:connect`、`standard:disconnect`、`standard:events`、`solana:signMessage`、`solana:signIn`，以及——根据钱包在首次连接后报告的功能——`solana:signTransaction`和/或`solana:signAndSendTransaction`。

直接与钱包交互：

```ts
import { SeekerConnectWalletName } from '@solana-mobile/seeker-connect-wallet-standard';
import { getWallets } from '@wallet-standard/app';
import { StandardConnect } from '@wallet-standard/features';

const seeker = getWallets()
  .get()
  .find((wallet) => wallet.name === SeekerConnectWalletName);
const { accounts } = await seeker.features[StandardConnect].connect();
```

**页面加载时恢复会话**，使用静默连接——它读取缓存，从不启动钱包，当没有缓存时解析为零个账户：

```ts
const { accounts } = await seeker.features[StandardConnect].connect({ silent: true });
```

**检测签名路由。** 在首次连接之前，两个交易功能都被假设；之后它们会根据钱包的实际功能重新导出，通过`standard:events`的`change`事件宣布。在调用之前检查：

```ts
import { SolanaSignAndSendTransaction } from '@solana/wallet-standard-features';

const feature = seeker.features[SolanaSignAndSendTransaction];
if (feature) {
  const [{ signature }] = await feature.signAndSendTransaction({
    account,
    chain: seeker.chains[0],
    transaction,
  });
}
```

`chain`是Wallet Standard输入的一部分，但这个钱包会忽略它——网络是通过`registerSeekerConnect`传递的，并在每次调用时从缓存的授权中重放。没有任何东西会交叉检查这两个，因此每次调用`solana:devnet`对主网注册提交在主网上不会抱怨。传递`seeker.chains[0]`，这样两者永远不会不一致，并且可以在注册时更改网络。

交易作为原始序列化字节（`Uint8Array`）跨功能边界传递，传统和v0都支持——使用应用已使用的客户端库进行序列化。登录遵循SIWS规范通过`solana:signIn`；`domain`默认为`window.location.host`。

当登录验证用户时，服务器是权威，不是客户端：在服务器端发布一次性、短寿命的nonce，并在服务器上验证返回的消息和签名——包括预期的域名和有效窗口——在创建会话之前。`seeker-genesis-token`技能逐步引导服务器流程。

## 通过代码处理错误

钱包结果会以`SeekerConnectError`携带`code`拒绝：

| 代码 | 含义 |
| --- | --- |
| `association-failed` | 没有钱包完成启动：超时、中继无法到达或配置错误，或不在Seeker上 |
| `authorization-declined` | 用户拒绝授权。缓存的令牌被清除；下次连接提示新的同意 |
| `cancelled` | 用户关闭了进度覆盖层。**正常结果——永远不会将其作为错误显示** |
| `request-declined` | 钱包拒绝签名或提交 |
| `session-closed` | 交互完成前会话结束 |
| `wallet-error` | 任何其他钱包报告的错误 |

三种失败是普通的`Error`，而不是钱包结果：在报告不支持它的钱包上调用`signAndSendTransaction`、在成功连接之前任何签名调用，以及钱包无结果响应的登录。

这种区别决定了谁显示错误。品牌化对话框仅对`SeekerConnectError`和任何其他情况触发——除了`cancelled`，这是一个正常结果并保持静默。三种普通的`Error`永远不会到达presenter，所以如果应用不显示任何内容，它们会无声地失败。首先按类型分支，然后按`.code`：

```ts
import { SeekerConnectError, SeekerConnectErrorCode } from '@solana-mobile/seeker-connect-wallet-standard';

try {
  await seeker.features[StandardConnect].connect();
} catch (error) {
  if (error instanceof SeekerConnectError) {
    if (error.code === SeekerConnectErrorCode.cancelled) {
      return; // 用户关闭了覆盖层；无报告内容
    }
    // SDK已显示其对话框。记录，并将UI保持在断开连接状态。
    console.error(error);
    return;
  }
  // 对此未显示对话框。自己显示它。
  showToast('无法连接到钱包.'); // 应用自己的错误UI
  console.error(error);
}
```

## 可选：品牌化连接按钮

`@solana-mobile/seeker-connect-ui`提供了一个`<seeker-connect-button>`自定义元素在Shadow DOM中（无需主机CSS）。SDK在首次使用时定义其元素；在启动时调用`defineSeekerConnectElements()`来提前定义它们：

```ts
import { defineSeekerConnectElements } from '@solana-mobile/seeker-connect-ui';

defineSeekerConnectElements();
```

```html
<seeker-connect-button theme="dark" variant="sign-in"></seeker-connect-button>
```

属性：`disabled`、`theme="light" | "dark"`（命名主机页面的主题），以及`variant="connect"`（默认）或`variant="sign-in"`用于标签。自己连接或登录调用`click`——按钮仅用于呈现。

## 参考资料

- [references/imperative-api.md](references/imperative-api.md) — 非Wallet-Standard路径通过`createNostrSeekerLink().transact`，以及`seekerLink` /
  `authorizationCache` / `presenter`覆盖
- [references/troubleshooting.md](references/troubleshooting.md) — 关联失败、桌面测试、功能派生功能、缓存行为

## 相关技能

- `seeker-domains` — 显示`.skr`名称而不是原始地址
- `seeker-genesis-token` — 连接后验证Seeker设备所有权
- `solana-mobile` — CLI、模板和工具链，支持`solana-mobile create`
- `solana-mobile-wallet` — React Native应用中的钱包连接（直接Mobile Wallet Adapter）

## 链接

- MWA web文档：https://docs.solanamobile.com/get-started/web/installation
- Seeker Connect文档：https://docs.solanamobile.com/solana-mobile-stack/seeker-connect
- Seeker Connect快速入门（中继条款在此处）：https://docs.solanamobile.com/solana-mobile-stack/seeker-connect-quickstart
- Seeker Connect存储库：https://github.com/solana-mobile/seeker-connect
