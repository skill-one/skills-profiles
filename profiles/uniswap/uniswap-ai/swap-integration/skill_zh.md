# 交换集成

将 Uniswap 交换集成到前端、后端和智能合约中。

## 前置条件

此技能假定熟悉 viem 基础知识（客户端设置、账户管理、合约交互、交易签名）。安装 **uniswap-viem** 插件以获取 viem/wagmi 的全面指导：`claude plugin add @uniswap/uniswap-viem`

## 快速决策指南

| 构建...                    | 使用此方法               |
| ------------------------------ | ----------------------------- |
| 使用 React/Next.js 的前端    | 交易 API                   |
| 后端脚本或机器人          | 交易 API                   |
| 智能合约集成     | Universal Router 直接调用 |
| 需要完全控制路由     | Universal Router SDK          |

### 路由类型快速参考

| 类型     | 描述                             | 链条                             |
| -------- | --------------------------------------- | ---------------------------------- |
| CLASSIC  | 通过 Uniswap 池的标准 AMM 交换 | 所有支持的链                   |
| DUTCH_V2 | UniswapX Dutch 竞价 V2               | Ethereum, Arbitrum, Base, Unichain |
| PRIORITY | MEV-保护的优先级订单            | Base, Unichain                     |
| WRAP     | ETH 到 WETH 转换                  | 所有                                |
| UNWRAP   | WETH 到 ETH 转换                  | 所有                                |

有关 DUTCH_V3、DUTCH_LIMIT、LIMIT_ORDER、BRIDGE 和 QUICKROUTE 的完整列表，请参阅 [路由类型](#routing-types)。

## 集成方法

### 1. 交易 API（推荐）

最佳用途：前端、后端、脚本。自动处理路由优化。

**基础 URL**: `https://trade-api.gateway.uniswap.org/v1`

**认证**: `x-api-key: <your-api-key>` 头部是必需的

**获取 API 密钥**: 交易 API 需要一个 API 密钥进行认证。访问 [Uniswap 开发者门户](https://developers.uniswap.org/) 进行注册并获取您的 API 密钥。密钥通常在注册后即可立即使用。将密钥作为 `x-api-key` 头部包含在所有 API 请求中。

**代理归因**: 在每个交易 API 请求中发送 `X-Agent-Info` 头部（在以下示例中写为 `x-agent-info`）。它将流量归因于此集成以进行分析——它永远不会影响请求。值是一个紧凑的 JSON 对象，正好包含这三个字段，并且不超过 1 KB：

- `integration_name`: 始终为 `"swap-integration"`
- `decision_origin`: **必须选择——不要复制默认值。** 选择与您的集成匹配的值（这些是唯一有效的值；任何其他值都被视为格式错误）:
  - `"human_mediated"` — 人类在执行每个操作之前进行审查/批准
  - `"autonomous"` — 代理在没有每操作人类批准的情况下执行（例如计划任务或 agentic harnesses）
- `version`: `"1.6.0"` — 跟踪此技能的 `metadata.version`

**如果值格式错误**: 请求仍然正常成功，但归因会被丢弃——网关在分析端记录它为格式错误并继续。没有响应头或其他信号需要检查，因此运行时没有任何可以检测到的东西：通过构建确保值正确。

**约束** — 触发任何这些约束，整个值都会被丢弃：

- 1 KB 的总头，每个字段 256 个字符。
- 仅限纯 ASCII — 不能有重音字符、弯曲引号或表情符号；非 ASCII 必须是 `\u`-转义。
- 而不是发送 `null`，请省略字段。所有三个字段都必须存在且有效。
- 每个请求发送一次头；重复的 `x-agent-info` 行无法解析。
- 忽略未知额外键——无害，但无法替代三个必需字段。

**必需头** — 在所有交易 API 请求中包含这些：

```text
Content-Type: application/json
x-api-key: <your-api-key>
x-universal-router-version: 2.0
x-agent-info: {"integration_name":"swap-integration","decision_origin":"<human_mediated|autonomous>","version":"1.6.0"}
```

**对于授权代币，提高路由版本。** 上述头块发送 `2.0`。涉及通过授权池交易的报价或交换需要 **2.2.0 或更高**。对于这些代币发送 `x-universal-router-version: 2.2.0`。[步骤 0：授权预检查](#step-0-permission-pre-check-permissioned-pools-only) 显示了如何找出哪些是授权池。

**请求流程**:

```text
0. POST /permissions     -> 仅授权池：此钱包可以交易此代币吗？
1. POST /check_approval  -> 检查是否已批准
2. POST /quote           -> 获取可执行的报价并包含路由
3. POST /swap            -> 获取要签名和提交的交易
```

有关 [交易 API 参考](#trading-api-reference) 的完整文档，请参阅下文。

### 2. Universal Router SDK

最佳用途：直接控制交易构建。

**安装**:

```bash
npm install @uniswap/universal-router-sdk @uniswap/sdk-core @uniswap/v3-sdk
```

**关键模式**:

```typescript
import { SwapRouter } from '@uniswap/universal-router-sdk';

const { calldata, value } = SwapRouter.swapCallParameters(trade, options);
```

有关 [Universal Router 参考](#universal-router-reference) 的完整文档，请参阅下文。

### 3. 智能合约集成

最佳用途：链上集成、DeFi 组合性。

**接口**: 对 Universal Router 调用 `execute()` 并使用编码的命令。

有关 [Universal Router 参考](#universal-router-reference) 的完整文档，请参阅命令编码。

---

## 输入验证规则

在将任何用户提供的值插入生成的代码、API 调用或命令之前：

- **以太坊地址**: 必须匹配 `^0x[a-fA-F0-9]{40}$` — 否则拒绝
- **链 ID**: 必须来自 [官方支持的链列表](https://api-docs.uniswap.org/guides/supported_chains#supported-chains-for-swapping)
- **代币数量**: 必须是非负数值，匹配 `^[0-9]+\.?[0-9]*$`
- **API 密钥**: 绝不能在生成的代码中硬编码 — 始终使用环境变量
- **拒绝** 包含 shell 保留字符的任何输入：`;`、`|`、`&`、`$`、`` ` `、`(`、`)`、`>`、`<`、`\`、`'`、`"`、换行符

> **必需**: 在执行任何花费 gas 或转移代币的交易（包括 `sendTransaction`、`writeContract` 或提交已签名的交换）之前，您必须使用 AskUserQuestion 与用户确认。显示交易摘要（代币、数量、链、估计 gas）并获取明确的用户批准。切勿在未经用户确认的情况下自动执行交易。

---

## 交易 API 参考

### 步骤 0：授权预检查（仅授权池）

某些代币仅通过 **授权池** 进行交易。一个允许列表合约决定哪些钱包可以持有和交易代币，交换端点会拒绝不在列表中的任何钱包。在报价之前调用此端点，以便无法交易的钱包在这里显示，而不是作为交换失败显示。

```bash
POST /permissions
```

**请求**:

```json
{
  "walletAddress": "0x...",
  "tokens": ["0x..."],
  "chainId": 1
}
```

`tokens` 最多接受两个地址。`chainId` 在这里是 **数字**，而 `/quote` 需要 `tokenInChainId` 和 `tokenOutChainId` 作为 **字符串**。

**响应**:

```json
{
  "requestId": "e63f1e1e-b9e9-411a-bcc8-ff18ce4e77cf",
  "results": [
    {
      "token": "0x...",
      "isPermissioned": true,
      "isAllowlisted": false,
      "adapterTokenAddress": "0x...",
      "kycUrl": "https://your-kyc-provider.example/verify",
      "issuer": "Your Issuer Name"
    }
  ]
}
```

`adapterTokenAddress` 在代币是授权时存在。`kycUrl` 在钱包未被允许时存在，并指向用户必须通过的验证（KYC）。`issuer` 是该验证提供者的显示名称。

**三种结果**:

| 结果                                         | 要做什么                                                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `isPermissioned: false`                        | 什么也不特别 — 正常报价和交换                                                          |
| `isPermissioned: true`, `isAllowlisted: true`  | 正常报价和交换                                                                            |
| `isPermissioned: true`, `isAllowlisted: false` | 报价以供用户查看价格，然后 **阻止提交** 并渲染 `kycUrl` 调用操作 |

**此端点需要 `x-api-key`，就像所有其他交易 API 调用一样。** 它的 [发布示例](https://developers.uniswap.org/docs/trading/swapping-api/swapping-permissioned-pools) 省略了头。没有头，端点返回 `401` 和 `{"errorCode":"Unauthorized","detail":"Unauthenticated api key or session"}`，因此从该示例复制集成在到达权限逻辑之前就会失败。

**需要 Universal Router 2.2.0 或更高版本** 才能涉及授权代币的报价和交换。在 `/quote` 和 `/swap` 调用中为这些代币发送 `x-universal-router-version: 2.2.0`。普通的 `UniversalRouter` 部署是不同的、非授权的网关。只有 `#v2.2` 部署在其构造函数中包含权限适配器工厂。

发行授权代币是另一项工作：请参阅 `uniswap-permissioned-pools` 插件中的 `permissioned-pools-issuer` 技能。

### 步骤 1：检查代币批准

```bash
POST /check_approval
```

**请求**:

```json
{
  "walletAddress": "0x...",
  "token": "0x...",
  "amount": "1000000000",
  "chainId": 1
}
```

**响应**:

```json
{
  "approval": {
    "to": "0x...",
    "from": "0x...",
    "data": "0x...",
    "value": "0",
    "chainId": 1
  }
}
```

如果 `approval` 为 `null`，则代币已批准。

### 步骤 2：获取报价

```bash
POST /quote
```

**请求**:

```json
{
  "swapper": "0x...",
  "tokenIn": "0x...",
  "tokenOut": "0x...",
  "tokenInChainId": "1",
  "tokenOutChainId": "1",
  "amount": "1000000000000000000",
  "type": "EXACT_INPUT",
  "slippageTolerance": 0.5,
  "routingPreference": "BEST_PRICE"
}
```

> **注意**: `tokenInChainId` 和 `tokenOutChainId` 必须是 **字符串**（例如 `"1"`），而不是数字。

**关键参数**:

| 参数           | 描述                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `type`              | `EXACT_INPUT` 或 `EXACT_OUTPUT`                                   |
| `slippageTolerance` | 0-100 百分比                                                  |
| `protocols`         | 可选: `["V2", "V3", "V4"]`                                    |
| `routingPreference` | `BEST_PRICE`, `FASTEST`, `CLASSIC`                                |
| `autoSlippage`      | `true` 以自动计算滑点（覆盖 `slippageTolerance`）                |
| `urgency`           | `normal` 或 `fast` — 影响UniswapX拍卖时间                      |

**响应** — 路由类型的形状不同。`BEST_PRICE` 路由在以太坊主网上通常返回 UniswapX (DUTCH_V2)，而不是 CLASSIC。

**CLASSIC 响应**:

```json
{
  "routing": "CLASSIC",
  "quote": {
    "input": { "token": "0x...", "amount": "1000000000000000000" },
    "output": { "token": "0x...", "amount": "999000000" },
    "slippage": 0.5,
    "route": [],
    "gasFee": "5000000000000000",
    "gasFeeUSD": "0.01",
    "gasUseEstimate": "150000"
  },
  "permitData": null
}
```

**UniswapX (DUTCH_V2/V3/PRIORITY) 响应** — 不同的 `quote` 形状，没有 `quote.output`:

```json
{
  "routing": "DUTCH_V2",
  "quote": {
    "orderInfo": {
      "reactor": "0x...",
      "swapper": "0x...",
      "nonce": "...",
      "deadline": 1772031054,
      "cosigner": "0x...",
      "input": {
        "token": "0x...",
        "startAmount": "1000000000000000000",
        "endAmount": "1000000000000000000"
      },
      "outputs": [
        {
          "token": "0x...",
          "startAmount": "999000000",
          "endAmount": "994000000",
          "recipient": "0x..."
        }
      ],
      "chainId": 1
    },
    "encodedOrder": "0x...",
    "orderHash": "0x..."
  },
  "permitData": { "domain": {}, "types": {}, "values": {} }
}
```

> **UniswapX 输出数量**: 使用 `quote.orderInfo.outputs[0].startAmount` 获取最佳填充数量。`endAmount` 是在完全拍卖衰减后的地板值。UniswapX 响应中没有 `quote.output.amount` — 运行时访问它将抛出错误。
>
> **显示提示**: 对于 CLASSIC 路由，使用 `gasFeeUSD`（一个带有美元值的字符串）来显示 gas 成本。**不要**使用硬编码的 ETH 价格手动转换 `gasFee`（wei）——这会导致极不准确估计（例如，~$87 而不是 ~$0.01）。UniswapX 路由对交换者是无气的。

有关 [QuoteResponse TypeScript 类型](#7-quoteresponse-typescript-types) 的编译时类型安全性，请参阅不同路由类型的跨类型。

### 步骤 3：执行交换

```bash
POST /swap
```

**请求** - 直接将报价响应展开到正文：

```typescript
// 正确：展开报价响应，删除 null 字段
const quoteResponse = await fetchQuote(params);

// 始终删除 permitData/permitTransaction — 通过路由类型显式处理
const { permitData, permitTransaction, ...cleanQuote } = quoteResponse;
const swapRequest: Record<string, unknown> = { ...cleanQuote };

const isUniswapX =
  quoteResponse.routing === 'DUTCH_V2' ||
  quoteResponse.routing === 'DUTCH_V3' ||
  quoteResponse.routing === 'PRIORITY';

if (isUniswapX) {
  // UniswapX: 仅签名 — permitData 绝不能发送到 /swap
  if (permit2Signature) swapRequest.signature = permit2Signature;
} else {
  // CLASSIC: 两者都有签名和 permitData，或者两者都没有
  if (permit2Signature && permitData && typeof permitData === 'object') {
    swapRequest.signature = permit2Signature;
    swapRequest.permitData = permitData;
  }
}
```

**关键**: 不要将报价包装在 `{quote: quoteResponse}` 中。API 期望将报价响应字段展开到请求正文。

**Permit2 规则**（CLASSIC 路由）:

- `signature` 和 `permitData` 必须同时存在，或者同时不存在
- 不要设置 `permitData: null` — 完全省略该字段
- 报价响应通常包括 `permitData: null` — 发送前删除

**UniswapX 路由**（DUTCH_V2/V3/PRIORITY）: `permitData` 用于本地签名订单，但必须从 `/swap` 正文**排除**。请参阅 [签名与提交流程](#uniswapx-signing-vs-submission-flow)。

**响应**（准备签名的交易）:

```json
{
  "swap": {
    "to": "0x...",
    "from": "0x...",
    "data": "0x...",
    "value": "0",
    "chainId": 1,
    "gasLimit": "250000"
  }
}
```

**响应验证** — 在广播之前始终验证：

```typescript
function validateSwapResponse(response: SwapResponse): void {
  if (!response.swap?.data || response.swap.data === '' || response.swap.data === '0x') {
    throw new Error('swap.data is empty - quote may have expired');
  }
  if (!isAddress(response.swap.to) || !isAddress(response.swap.from)) {
    throw new Error('Invalid address in swap response');
  }
}
```

### 支持的链

有关当前链集及其 ID 的完整列表，请参阅 [官方支持的链列表](https://api-docs.uniswap.org/guides/supported_chains#supported-chains-for-swapping)。

### 路由类型

| 类型        | 描述                                       |
| ----------- | ------------------------------------------ |
| CLASSIC     | 通过 Uniswap 池的标准 AMM 交换             |
| DUTCH_V2    | UniswapX Dutch 竞价 V2                     |
| DUTCH_V3    | UniswapX Dutch 竞价 V3                     |
| PRIORITY    | MEV 保护优先订单（Base、Unichain）         |
| DUTCH_LIMIT | UniswapX Dutch 限价订单                   |
| LIMIT_ORDER | 限价订单                                   |
| WRAP        | ETH 到 WETH 转换                           |
| UNWRAP      | WETH 到 ETH 转换                           |
| BRIDGE      | 跨链桥                                     |
| QUICKROUTE  | 快速近似报价                               |

**UniswapX 可用性**：UniswapX V2 订单支持以太坊（1）、Arbitrum（42161）、Base（8453）和 Unichain（130）。拍卖机制因链而异——请参阅下文的 [UniswapX 拍卖类型](#uniswapx-auction-types)。

---

## 关键实现注意事项

这些是在实际世界 Trading API 集成过程中发现的常见陷阱。**遵循这些规则以避免链上回滚和 API 错误。**

### 1. 交换请求体格式

`/swap` 端点期望报价响应**展开到请求体中**，而不是包装在 `quote` 字段中。

```typescript
// 错误 - 会引发 "quote does not match any of the allowed types"
const badRequest = {
  quote: quoteResponse, // 不要包装！
  signature: '0x...',
};

// 正确 - 展开报价响应
const goodRequest = {
  ...quoteResponse,
  signature: '0x...', // 仅在使用 Permit2 时
};
```

### 2. 空字段处理

API 拒绝 `permitData: null`。此外，`permitData` 的处理方式因路由类型而异——请参阅 [签名与提交流程](#uniswapx-signing-vs-submission-flow) 的完整说明。

```typescript
function prepareSwapRequest(quoteResponse: QuoteResponse, signature?: string): object {
  // 总是移除 permitData 和 permitTransaction 并展开——显式处理它们
  const { permitData, permitTransaction, ...cleanQuote } = quoteResponse;
  const request: Record<string, unknown> = { ...cleanQuote };

  // UniswapX (DUTCH_V2, DUTCH_V3, PRIORITY): permitData 仅用于本地签名。
  // /swap 请求体必须**不**包含 permitData —— 订单编码在 quote.encodedOrder 中。
  // 仅需要签名。
  const isUniswapX =
    quoteResponse.routing === 'DUTCH_V2' ||
    quoteResponse.routing === 'DUTCH_V3' ||
    quoteResponse.routing === 'PRIORITY';

  if (isUniswapX) {
    if (signature) request.signature = signature;
  } else {
    // CLASSIC: 需要 signature 和 permitData 共同存在，或共同省略。
    // Universal Router 合约需要 permitData 以在链上验证 Permit2 授权。
    if (signature && permitData && typeof permitData === 'object') {
      request.signature = signature;
      request.permitData = permitData;
    }
  }

  return request;
}
```

### 3. Permit2 字段规则

`/swap` 请求体中 `signature` 和 `permitData` 的规则取决于路由类型：

**CLASSIC 路由**：

| 情景                   | `signature` | `permitData` |
| ---------------------- | ----------- | ------------ |
| 标准交换（无 Permit2） | 省略        | 省略         |
| Permit2 交换           | 需要        | 需要         |
| **无效**               | 存在        | 缺失         |
| **无效**               | 缺失        | 存在         |
| **无效（API 错误）**  | 任何        | `null`       |

**UniswapX 路由（DUTCH_V2/V3/PRIORITY）**：

| 情景       | `signature` | `permitData`             |
| ---------- | ----------- | ------------------------ |
| UniswapX 订单 | 需要        | **省略**（不要发送）   |
| **无效**    | 任何        | 存在（模式拒绝）       |

### 4. 预广播验证

在发送到区块链之前，始终验证交换响应：

```typescript
import { isAddress, isHex } from 'viem';

function validateSwapBeforeBroadcast(swap: SwapTransaction): void {
  // 1. data 必须是非空十六进制
  if (!swap.data || swap.data === '' || swap.data === '0x') {
    throw new Error('swap.data 为空 - 这将在链上回滚。重新获取报价。');
  }

  if (!isHex(swap.data)) {
    throw new Error('swap.data 不是有效的十六进制');
  }

  // 2. 地址必须有效
  if (!isAddress(swap.to)) {
    throw new Error('swap.to 不是有效的地址');
  }

  if (!isAddress(swap.from)) {
    throw new Error('swap.from 不是有效的地址');
  }

  // 3. Value 必须存在（对于非 ETH 交换可以是 "0"）
  if (swap.value === undefined || swap.value === null) {
    throw new Error('swap.value 缺失');
  }
}
```

### 5. 浏览器环境设置

在使用 viem/wagmi 的浏览器环境中，您需要 Node.js 通用填充：

**安装 buffer 通用填充**：

```bash
npm install buffer
```

**添加到您的入口文件（在其他导入之前）**：

```typescript
// src/main.tsx 或 src/index.tsx
import { Buffer } from 'buffer';
globalThis.Buffer = Buffer;

// 然后是其他导入
import React from 'react';
import { WagmiProvider } from 'wagmi';
// ...
```

**Vite 配置** (`vite.config.ts`)：

```typescript
export default defineConfig({
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['buffer'],
  },
  resolve: {
    alias: {
      buffer: 'buffer',
    },
  },
});
```

没有此设置，您将看到：`ReferenceError: Buffer is not defined`

#### CORS 代理配置

Trading API 不支持浏览器 CORS 预检请求——`OPTIONS` 请求返回 `415 Unsupported Media Type`。从浏览器直接 `fetch()` 调用将始终失败。您**必须**通过自己的服务器或开发服务器代理 API 请求。

**Vite 开发代理**（合并到上述 Buffer 通用填充使用的同一 `vite.config.ts` 中）：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api/uniswap': {
        target: 'https://trade-api.gateway.uniswap.org/v1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/uniswap/, ''),
      },
    },
  },
});
```

然后在您的前端代码中使用 `/api/uniswap/quote` 而不是完整 URL。

**Vercel 生产代理** (`vercel.json`)：

```json
{
  "rewrites": [
    {
      "source": "/api/uniswap/:path*",
      "destination": "https://trade-api.gateway.uniswap.org/v1/:path*"
    }
  ]
}
```

**Cloudflare Pages** (`public/_redirects`)：

```text
/api/uniswap/* https://trade-api.gateway.uniswap.org/v1/:splat 200
```

**Next.js** (`next.config.js`)：

```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/uniswap/:path*',
        destination: 'https://trade-api.gateway.uniswap.org/v1/:path*',
      },
    ];
  },
};
```

没有代理，您将看到：`415 Unsupported Media Type` 在预检或浏览器控制台中的 CORS 错误。

### 6. 报价新鲜度

- 报价快速过期（通常 30 秒）
- 如果用户花费时间审查，始终重新获取
- 使用 `deadline` 参数防止陈旧执行
- 如果 `/swap` 返回空的 `data`，则报价可能已过期

### 7. QuoteResponse TypeScript 类型

报价响应的形状因路由类型而异。使用 `routing` 字段的区分联合类型以获得编译时安全性，而不是将 `any` 强制转换为：

```typescript
type ClassicQuoteResponse = {
  routing: 'CLASSIC' | 'WRAP' | 'UNWRAP';
  quote: {
    input: { token: string; amount: string };
    output: { token: string; amount: string };
    slippage: number;
    route: unknown[];
    gasFee: string;
    gasFeeUSD: string;
    gasUseEstimate: string;
  };
  permitData: Record<string, unknown> | null;
};

type DutchOrderOutput = {
  token: string;
  startAmount: string;
  endAmount: string;
  recipient: string;
};

type UniswapXQuoteResponse = {
  routing: 'DUTCH_V2' | 'DUTCH_V3' | 'PRIORITY';
  quote: {
    orderInfo: {
      outputs: DutchOrderOutput[];
      input: { token: string; startAmount: string; endAmount: string };
      deadline: number;
      nonce: string;
    };
    encodedOrder: string;
    orderHash: string;
  };
  // EIP-712 类型数据——本地签名，不要发送到 /swap
  permitData: Record<string, unknown> | null;
};

type QuoteResponse = ClassicQuoteResponse | UniswapXQuoteResponse;

// 路由感知逻辑的类型守卫
function isUniswapXQuote(q: QuoteResponse): q is UniswapXQuoteResponse {
  return q.routing === 'DUTCH_V2' || q.routing === 'DUTCH_V3' || q.routing === 'PRIORITY';
}

// 通过路由类型读取输出金额
function getOutputAmount(q: QuoteResponse): string {
  if (isUniswapXQuote(q)) {
    const firstOutput = q.quote.orderInfo.outputs[0];
    if (!firstOutput) throw new Error('UniswapX 报价没有输出');
    // startAmount = 最佳填充；endAmount = 拍卖衰减后的地板值
    return firstOutput.startAmount;
  }
  return q.quote.output.amount;
}
```

---

## Universal Router 参考

Universal Router 是一个统一的接口，用于在 Uniswap v2、v3 和 v4 之间进行交换。

### 核心功能

```solidity
function execute(
    bytes calldata commands,
    bytes[] calldata inputs,
    uint256 deadline
) external payable;
```

### 命令编码

每个命令都是一个字节：

| 位 | 名称     | 目的                             |
| ---- | -------- | ----------------------------------- |
| 0    | flag     | 允许回滚（1 = 失败时继续）       |
| 1-2  | reserved | 使用 0                            |
| 3-7  | command  | 操作标识符                        |

### 交换命令

| 代码 | 命令           | 描述               |
| ---- | ----------------- | ------------------------- |
| 0x00 | V3_SWAP_EXACT_IN  | v3 交换，输入精确    |
| 0x01 | V3_SWAP_EXACT_OUT | v3 交换，输出精确    |
| 0x08 | V2_SWAP_EXACT_IN  | v2 交换，输入精确    |
| 0x09 | V2_SWAP_EXACT_OUT | v2 交换，输出精确    |
| 0x10 | V4_SWAP           | v4 交换               |

### 代币操作

| 代码 | 命令     | 描述                |
| ---- | ----------- | -------------------------- |
| 0x04 | SWEEP       | 清除路由器代币余额 |
| 0x05 | TRANSFER    | 发送特定金额       |
| 0x0b | WRAP_ETH    | ETH 到 WETH            |
| 0x0c | UNWRAP_WETH | WETH 到 ETH            |

### Permit2 命令

| 代码 | 命令               | 描述           |
| ---- | --------------------- | --------------------- |
| 0x02 | PERMIT2_TRANSFER_FROM | 单个代币转移     |
| 0x03 | PERMIT2_PERMIT_BATCH  | 批量授权        |
| 0x0a | PERMIT2_PERMIT        | 单个授权        |

### SDK 使用

```typescript
import { SwapRouter, UniswapTrade } from '@uniswap/universal-router-sdk'
import { TradeType } from '@uniswap/sdk-core'

// 使用 v3-sdk 或 router-sdk 构建交易
const trade = new RouterTrade({
  v3Routes: [...],
  tradeType: TradeType.EXACT_INPUT
})

// 获取 Universal Router 的 calldata
const { calldata, value } = SwapRouter.swapCallParameters(trade, {
  slippageTolerance: new Percent(50, 10000), // 0.5%
  recipient: walletAddress,
  deadline: Math.floor(Date.now() / 1000) + 1200 // 20 分钟
})

// 发送交易
const tx = await wallet.sendTransaction({
  to: UNIVERSAL_ROUTER_ADDRESS,
  data: calldata,
  value
})
```

---

## Permit2 集成

Permit2 允许基于签名的代币授权，而不是链上 approve() 调用。

### 授权目标：Permit2 与传统（直接到路由器）

存在两种授权路径。根据您的集成类型选择：

| 方法                    | 授权给       | 每次交换授权       | 适合于                         |
| ----------------------- | ------------ | ------------------- | -------------------------------- |
| **Permit2**（推荐）   | Permit2 合约 | EIP-712 签名       | 带有用户交互的前端            |
| **传统**（直接批准） | Universal Router | 无（预批准）      | 后端服务，智能账户            |

**Permit2 流程**（带用户签名的前端）：

1. 用户批准代币给 Permit2 合约（一次性）
2. 每次交换：用户签署 EIP-712 Permit 消息
3. Universal Router 使用签名通过 Permit2 转移代币

**传统流程**（后端服务，ERC-4337 智能账户）：

1. 直接批准代币给 Universal Router 地址（一次性）
2. 每次交换：不需要额外授权
3. 对于无法签署 EIP-712 消息的自动化系统更简单

使用 Trading API 的 `/check_approval` 端点——它根据路由类型返回正确的授权目标。

### 工作原理

1. 用户一次性批准 Permit2 合约（无限期授权）
2. 每次交换：用户签署授权转移的消息
3. Universal Router 使用签名通过 Permit2 转移代币

### 两种模式

| 模式              | 描述                                |
| ----------------- | ------------------------------------------ |
| SignatureTransfer | 一次性签名，无链上状态      |
| AllowanceTransfer | 基于时间的授权，带链上状态      |

### 集成模式

```typescript
import { getContract, maxUint256, type Address } from 'viem';

const PERMIT2_ADDRESS = '0x000000000022D473030F116dDEE9F6B43aC78BA3' as const;

// 检查是否存在 Permit2 授权
const allowance = await publicClient.readContract({
  address: PERMIT2_ADDRESS,
  abi: permit2Abi,
  functionName: 'allowance',
  args: [userAddress, tokenAddress, spenderAddress],
});

// 如果未授权，用户必须先批准 Permit2
if (allowance.amount < requiredAmount) {
  const hash = await walletClient.writeContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'approve',
    args: [PERMIT2_ADDRESS, maxUint256],
  });
  await publicClient.waitForTransactionReceipt({ hash });
}

// 然后为交换签署 permit
const permitSignature = await signPermit(...);
```

---

## UniswapX 拍卖类型

UniswapX 通过链下填充者进行交换，填充者竞争以提供比链上 AMM 更好的价格。拍卖机制因链而异。

### 独家荷兰拍卖（Ethereum）

- 开始于 RFQ（报价请求）阶段，授权报价者竞争
- 获胜报价者获得**独家填充权**一段时间
- 如果独家填充者未执行，则回退到开放荷兰拍卖，每个区块价格衰减
- 适用于需要 MEV 保护的较大交换

**Trading API 路由类型**：`DUTCH_V2` 或 `DUTCH_V3`

### 开放荷兰拍卖（Arbitrum）

- 无 RFQ 阶段的直接开放拍卖
- 填充者通过递减价格机制在链上竞争
- 利用 Arbitrum 的 0.25 秒区块时间进行快速价格发现
- **Unimind 算法**根据历史对性能设置拍卖参数

**Trading API 路由类型**：`DUTCH_V2`

### 优先 Gas 拍卖（Base、Unichain）

- 填充者通过在目标区块提交具有不同**优先费**的交易来竞价
- 最高优先费者赢得填充订单的权利
- 利用 OP Stack 的优先排序机制
- 在尊重优先排序机制的链上有效

**Trading API 路由类型**：`PRIORITY`

### 所有拍卖类型的关键属性

- **用户无 Gas 费**——填充者支付 Gas 费，包含在最终定价中
- **失败无成本**——如果交换未填充，用户无需支付任何费用
- **MEV 保护**——拍卖机制防止前置运行和挤压攻击
- UniswapX V2 目前支持以太坊（1）、Arbitrum（42161）、Base（8453）和 Unichain（130）

更多详情，请参阅 [UniswapX 拍卖类型文档](https://docs.uniswap.org/contracts/uniswapx/auctiontypes)。

### UniswapX：签名与提交流程

报价响应中的 `permitData` 字段根据路由类型具有不同目的。混淆两者会在 `/swap` 上引发 `RequestValidationError`。

**CLASSIC 流程**——`permitData` 发送到服务器：

1. `/quote` 返回 `permitData`（EIP-712 类型的 Permit2 授权数据）
2. 用户在本地签署 `permitData` → 生成 `signature`
3. `/swap` 请求体包含 **两者** `signature` 和 `permitData` — Universal Router 合约需要 `permitData` 在链上重建和验证 Permit2 授权

**UniswapX 流程（DUTCH_V2/V3/PRIORITY）— `permitData` 保持本地**：

1. `/quote` 返回 `permitData`（EIP-712 类型的荷兰订单）
2. 用户在本地签署 `permitData` → 生成 `signature`
3. `/swap` 请求体包含 **仅** `signature` — 订单已完全编码在 `quote.encodedOrder` 中，链下填充系统直接读取。将 `permitData` 发送到 `/swap` 会导致模式验证错误。

| 路径类型           | 是否使用 `permitData` 签署？ | 是否将 `permitData` 发送到 `/swap`？ | 是否将 `signature` 发送到 `/swap`？ |
| ----------------- | ----------------------- | ----------------------------- | ---------------------------- |
| CLASSIC              | 是                     | **是**（路由器需要它）     | 是（如果使用 Permit2）       |
| DUTCH_V2/V3/PRIORITY | 是                     | **否**（模式拒绝它）    | 是                          |

> **常见错误**：API 错误 `"quote" 不匹配任何允许的类型` 通常指向 `quote` 字段，但实际原因是 UniswapX 路径存在 `permitData`。在提交前移除 `permitData` — 查看 [Null 字段处理](#2-null-field-handling) 中的路由感知 `prepareSwapRequest`。

---

## 直接 Universal Router 集成（SDK）

无需 Trading API 的直接 Universal Router 集成，请使用 SDK 的高级 API。

### 安装

```bash
npm install @uniswap/universal-router-sdk @uniswap/router-sdk @uniswap/sdk-core @uniswap/v3-sdk viem
```

### 高级方法（推荐）

使用 `RouterTrade` + `SwapRouter.swapCallParameters()` 自动构建命令：

```typescript
import { SwapRouter } from '@uniswap/universal-router-sdk';
import { Trade as RouterTrade } from '@uniswap/router-sdk';
import { TradeType, Percent } from '@uniswap/sdk-core';
import { Route as V3Route, Pool } from '@uniswap/v3-sdk';

// 1. 获取池数据（构建路径所需）
// 使用 viem 读取链上池状态：
const slot0 = await publicClient.readContract({
  address: poolAddress,
  abi: [
    {
      name: 'slot0',
      type: 'function',
      stateMutability: 'view',
      inputs: [],
      outputs: [
        { name: 'sqrtPriceX96', type: 'uint160' },
        { name: 'tick', type: 'int24' },
        { name: 'observationIndex', type: 'uint16' },
        { name: 'observationCardinality', type: 'uint16' },
        { name: 'observationCardinalityNext', type: 'uint16' },
        { name: 'feeProtocol', type: 'uint8' },
        { name: 'unlocked', type: 'bool' },
      ],
    },
  ],
  functionName: 'slot0',
});
const liquidity = await publicClient.readContract({
  address: poolAddress,
  abi: [
    {
      name: 'liquidity',
      type: 'function',
      stateMutability: 'view',
      inputs: [],
      outputs: [{ type: 'uint128' }],
    },
  ],
  functionName: 'liquidity',
});

const pool = new Pool(tokenIn, tokenOut, fee, slot0[0].toString(), liquidity.toString(), slot0[1]);

// 2. 构建路径和交易
const route = new V3Route([pool], tokenIn, tokenOut);
const trade = RouterTrade.createUncheckedTrade({
  route,
  inputAmount: amountIn,
  outputAmount: expectedOut,
  tradeType: TradeType.EXACT_INPUT,
});

// 3. 获取 calldata
const { calldata, value } = SwapRouter.swapCallParameters(trade, {
  slippageTolerance: new Percent(50, 10000), // 0.5%
  recipient: walletAddress,
  deadline: Math.floor(Date.now() / 1000) + 1800,
});

// 4. 使用 viem 执行
const hash = await walletClient.sendTransaction({
  to: UNIVERSAL_ROUTER_ADDRESS,
  data: calldata,
  value: BigInt(value),
});
```

### 低级方法（手动命令）

用于自定义流程（费用收集、复杂路由），直接使用 `RoutePlanner`：

```typescript
import { RoutePlanner, CommandType, ROUTER_AS_RECIPIENT } from '@uniswap/universal-router-sdk';
import { encodeRouteToPath } from '@uniswap/v3-sdk';

// 特殊地址
const MSG_SENDER = '0x0000000000000000000000000000000000000001';
const ADDRESS_THIS = '0x0000000000000000000000000000000000000002';
```

### 示例：V3 交换（手动命令）

```typescript
import { RoutePlanner, CommandType } from '@uniswap/universal-router-sdk';
import { encodeRouteToPath, Route } from '@uniswap/v3-sdk';

async function swapV3Manual(route: Route, amountIn: bigint, amountOutMin: bigint) {
  const planner = new RoutePlanner();

  // 从路径编码 V3 路径
  const path = encodeRouteToPath(route, false); // false = exactInput

  planner.addCommand(CommandType.V3_SWAP_EXACT_IN, [
    MSG_SENDER, // recipient
    amountIn, // amountIn
    amountOutMin, // amountOutMin
    path, // 编码路径
    true, // payerIsUser
  ]);

  return executeRoute(planner);
}
```

### 示例：ETH 转代币（包装 + 交换）

```typescript
async function swapEthToToken(route: Route, amountIn: bigint, amountOutMin: bigint) {
  const planner = new RoutePlanner();
  const path = encodeRouteToPath(route, false);

  // 1. 将 ETH 包装为 WETH（保留在路由器中）
  planner.addCommand(CommandType.WRAP_ETH, [ADDRESS_THIS, amountIn]);

  // 2. 交换 WETH → 代币（使用路由器的 WETH，因此 payerIsUser = false）
  planner.addCommand(CommandType.V3_SWAP_EXACT_IN, [
    MSG_SENDER,
    amountIn,
    amountOutMin,
    path,
    false,
  ]);

  return executeRoute(planner, { value: amountIn });
}
```

### 示例：代币转 ETH（交换 + 解包）

```typescript
async function swapTokenToEth(route: Route, amountIn: bigint, amountOutMin: bigint) {
  const planner = new RoutePlanner();
  const path = encodeRouteToPath(route, false);

  // 1. 交换代币 → WETH（输出到路由器）
  planner.addCommand(CommandType.V3_SWAP_EXACT_IN, [
    ADDRESS_THIS,
    amountIn,
    amountOutMin,
    path,
    true,
  ]);

  // 2. 解包 WETH 为 ETH
  planner.addCommand(CommandType.UNWRAP_WETH, [MSG_SENDER, amountOutMin]);

  return executeRoute(planner);
}
```

### 示例：费用收集（PAY_PORTION）

```typescript
async function swapWithFee(route: Route, amountIn: bigint, feeRecipient: Address, feeBips: number) {
  const planner = new RoutePlanner();
  const path = encodeRouteToPath(route, false);
  const outputToken = route.output.wrapped.address;

  // 交换到路由器（ADDRESS_THIS）
  planner.addCommand(CommandType.V3_SWAP_EXACT_IN, [ADDRESS_THIS, amountIn, 0n, path, true]);

  // 支付费用部分（例如，30 bips = 0.3%）
  planner.addCommand(CommandType.PAY_PORTION, [outputToken, feeRecipient, feeBips]);

  // 扫描剩余部分到用户
  planner.addCommand(CommandType.SWEEP, [outputToken, MSG_SENDER, 0n]);

  return executeRoute(planner);
}
```

### 执行路径辅助函数

```typescript
import { UNIVERSAL_ROUTER_ADDRESS } from '@uniswap/universal-router-sdk';

const ROUTER_ABI = [
  {
    name: 'execute',
    type: 'function',
    stateMutability: 'payable',
    inputs: [
      { name: 'commands', type: 'bytes' },
      { name: 'inputs', type: 'bytes[]' },
      { name: 'deadline', type: 'uint256' },
    ],
    outputs: [],
  },
] as const;

async function executeRoute(planner: RoutePlanner, options?: { value?: bigint }) {
  const deadline = BigInt(Math.floor(Date.now() / 1000) + 1800);
  const routerAddress = UNIVERSAL_ROUTER_ADDRESS('2.0', 1); // version, chainId

  const { request } = await publicClient.simulateContract({
    address: routerAddress,
    abi: ROUTER_ABI,
    functionName: 'execute',
    args: [planner.commands, planner.inputs, deadline],
    account,
    value: options?.value ?? 0n,
  });

  return walletClient.writeContract(request);
}
```

### 命令速查表

| 命令           | 参数                                               |
| ----------------- | -------------------------------------------------------- |
| V3_SWAP_EXACT_IN  | (recipient, amountIn, amountOutMin, path, payerIsUser)   |
| V3_SWAP_EXACT_OUT | (recipient, amountOut, amountInMax, path, payerIsUser)   |
| V2_SWAP_EXACT_IN  | (recipient, amountIn, amountOutMin, path[], payerIsUser) |
| V2_SWAP_EXACT_OUT | (recipient, amountOut, amountInMax, path[], payerIsUser) |
| WRAP_ETH          | (recipient, amount)                                      |
| UNWRAP_WETH       | (recipient, amountMin)                                   |
| SWEEP             | (token, recipient, amountMin)                            |
| TRANSFER          | (token, recipient, amount)                               |
| PAY_PORTION       | (token, recipient, bips)                                 |

### 费用层级

| 层级   | 值 | 百分比 |
| ------ | ----- | ---------- |
| LOWEST | 100   | 0.01%      |
| LOW    | 500   | 0.05%      |
| MEDIUM | 3000  | 0.30%      |
| HIGH   | 10000 | 1.00%      |

---

## 常见集成模式

### 前端交换钩子（React）

**注意**：确保已设置 Buffer 多填充和 CORS 代理（见关键实现注意事项）。有关 wagmi v2 `useWalletClient()` 陷阱，请参阅 [wagmi v2 集成陷阱](#wagmi-v2-integration-pitfalls)。

```typescript
import { isAddress, isHex } from 'viem';
import { useWalletClient } from 'wagmi';

// 在浏览器应用中，请使用您的 CORS 代理路径（见 CORS 代理配置）
// 例如，const API_URL = '/api/uniswap';
const API_URL = 'https://trade-api.gateway.uniswap.org/v1';

// 必须定义 decision_origin — 'human_mediated'（人类在执行每个操作前审查/批准）
// 或 'autonomous'（无需每个操作的逐项人类批准）。
// 见上述代理归因。没有默认值 — 你必须选择。
declare const DECISION_ORIGIN: 'human_mediated' | 'autonomous';

const AGENT_INFO = JSON.stringify({
  integration_name: 'swap-integration',
  decision_origin: DECISION_ORIGIN,
  version: '1.6.0',
});

function useSwap() {
  const { data: walletClient } = useWalletClient();
  const [quoteResponse, setQuoteResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getQuote = async (params) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': API_KEY,
          'x-universal-router-version': '2.0',
          'x-agent-info': AGENT_INFO,
        },
        body: JSON.stringify(params),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Quote failed');
      setQuoteResponse(data); // 存储完整响应，而不仅仅是 data.quote
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const executeSwap = async (permit2Signature?: string) => {
    if (!quoteResponse) throw new Error('No quote available');

    // 移除 null 字段并展开 quote 响应到 body
    const { permitData, permitTransaction, ...cleanQuote } = quoteResponse;
    const swapRequest: Record<string, unknown> = { ...cleanQuote };

    // 关键：permitData 处理因路由类型而异
    const isUniswapX =
      quoteResponse.routing === 'DUTCH_V2' ||
      quoteResponse.routing === 'DUTCH_V3' ||
      quoteResponse.routing === 'PRIORITY';

    if (isUniswapX) {
      // UniswapX：仅 signature — permitData 必须不发送到 /swap
      // （permitData 用于本地签署订单，不提交到 API）
      if (permit2Signature) swapRequest.signature = permit2Signature;
    } else {
      // CLASSIC：需要同时提供 signature 和 permitData，或两者都省略
      if (permit2Signature && permitData && typeof permitData === 'object') {
        swapRequest.signature = permit2Signature;
        swapRequest.permitData = permitData;
      }
    }

    const swapResponse = await fetch(`${API_URL}/swap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        'x-universal-router-version': '2.0',
        'x-agent-info': AGENT_INFO,
      },
      body: JSON.stringify(swapRequest),
    });
    const data = await swapResponse.json();
    if (!swapResponse.ok) throw new Error(data.detail || 'Swap failed');

    // 关键：在广播前验证响应
    if (!data.swap?.data || data.swap.data === '' || data.swap.data === '0x') {
      throw new Error('空交换数据 - quote 可能已过期。请刷新。');
    }

    // 通过钱包（walletClient 从 useWalletClient()）发送交易
    if (!walletClient) throw new Error('钱包未连接');
    const tx = await walletClient.sendTransaction(data.swap);
    return tx;
  };

  return { quote: quoteResponse?.quote, loading, error, getQuote, executeSwap };
}
```

### wagmi v2 集成陷阱

来自 wagmi v2 的 `useWalletClient()` 钩子即使钱包已连接也可能返回 `undefined` — 它异步解析。这会导致交换时出现“钱包未连接”错误。此外，返回的客户端需要 `chain` 才能使用 `sendTransaction()`。

**推荐模式** — 在交换时使用 `@wagmi/core` 动作函数，而不是钩子：

```typescript
import { getWalletClient, getPublicClient, switchChain } from '@wagmi/core';
import type { Config } from 'wagmi';

async function executeSwapTransaction(
  config: Config,
  chainId: number,
  swapTx: { to: string; data: string; value: string }
) {
  // 1. 确保钱包在正确的链上
  await switchChain(config, { chainId });

  // 2. 获取带显式 chainId 的钱包客户端 — 避免 undefined 和缺少链
  const walletClient = await getWalletClient(config, { chainId });

  // 3. 执行交换
  const hash = await walletClient.sendTransaction({
    to: swapTx.to as `0x${string}`,
    data: swapTx.data as `0x${string}`,
    value: BigInt(swapTx.value || '0'),
  });

  // 4. 等待确认
  const publicClient = getPublicClient(config, { chainId });
  if (!publicClient) throw new Error(`未配置 chainId ${chainId} 的公共客户端`);
  return publicClient.waitForTransactionReceipt({ hash });
}
```

**为什么这很重要**：

- `useWalletClient()` 钩子在异步解析期间返回 `{ data: undefined }`，即使 `useAccount()` 显示已连接
- `getWalletClient(config, { chainId })` 是一个仅当客户端准备就绪时才解析的承诺，并包含链
- `switchChain()` 防止“链不匹配”错误，当钱包位于与交换不同的网络时

### 后端交换脚本（Node.js）

```typescript
import { createWalletClient, createPublicClient, http, isAddress, isHex, type Address } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet } from 'viem/chains';

const API_URL = 'https://trade-api.gateway.uniswap.org/v1';
const API_KEY = process.env.UNISWAP_API_KEY!;

// REQUIRED: define decision_origin yourself — 'human_mediated' (a human reviews/approves
// each action before it executes) or 'autonomous' (no per-action human approval).
// See Agent Attribution above. There is no default — you must choose.
declare const DECISION_ORIGIN: 'human_mediated' | 'autonomous';

const AGENT_INFO = JSON.stringify({
  integration_name: 'swap-integration',
  decision_origin: DECISION_ORIGIN,
  version: '1.6.0',
});

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);
const publicClient = createPublicClient({ chain: mainnet, transport: http() });
const walletClient = createWalletClient({ account, chain: mainnet, transport: http() });

// Helper to prepare /swap request body — routing-aware permitData handling
function prepareSwapRequest(quoteResponse: Record<string, unknown>, signature?: string): object {
  const { permitData, permitTransaction, ...cleanQuote } = quoteResponse;
  const request: Record<string, unknown> = { ...cleanQuote };

  // UniswapX (DUTCH_V2, DUTCH_V3, PRIORITY): permitData is for LOCAL signing only.
  // The /swap body must NOT include permitData — the order is already encoded
  // in quote.encodedOrder. Only the signature is needed.
  const isUniswapX =
    quoteResponse.routing === 'DUTCH_V2' ||
    quoteResponse.routing === 'DUTCH_V3' ||
    quoteResponse.routing === 'PRIORITY';

  if (isUniswapX) {
    if (signature) request.signature = signature;
  } else {
    // CLASSIC: both signature and permitData required together, or both omitted
    if (signature && permitData && typeof permitData === 'object') {
      request.signature = signature;
      request.permitData = permitData;
    }
  }

  return request;
}

// Validate swap response before broadcasting
function validateSwap(swap: { data?: string; to?: string; from?: string }): void {
  if (!swap?.data || swap.data === '' || swap.data === '0x') {
    throw new Error('swap.data is empty - quote may have expired');
  }
  if (!isHex(swap.data)) {
    throw new Error('swap.data is not valid hex');
  }
  if (!swap.to || !isAddress(swap.to) || !swap.from || !isAddress(swap.from)) {
    throw new Error('Invalid address in swap response');
  }
}

async function executeSwap(tokenIn: Address, tokenOut: Address, amount: string, chainId: number) {
  const ETH_ADDRESS = '0x0000000000000000000000000000000000000000';

  // 1. Check approval (for ERC20 tokens, not native ETH)
  if (tokenIn !== ETH_ADDRESS) {
    const approvalRes = await fetch(`${API_URL}/check_approval`, {
      method: 'POST',
      headers: {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json',
        'x-universal-router-version': '2.0',
        'x-agent-info': AGENT_INFO,
      },
      body: JSON.stringify({
        walletAddress: account.address,
        token: tokenIn,
        amount,
        chainId,
      }),
    });
    const approvalData = await approvalRes.json();

    if (approvalData.approval) {
      const hash = await walletClient.sendTransaction({
        to: approvalData.approval.to,
        data: approvalData.approval.data,
        value: BigInt(approvalData.approval.value || '0'),
      });
      await publicClient.waitForTransactionReceipt({ hash });
    }
  }

  // 2. Get quote
  const quoteRes = await fetch(`${API_URL}/quote`, {
    method: 'POST',
    headers: {
      'x-api-key': API_KEY,
      'Content-Type': 'application/json',
      'x-universal-router-version': '2.0',
      'x-agent-info': AGENT_INFO,
    },
    body: JSON.stringify({
      swapper: account.address,
      tokenIn,
      tokenOut,
      tokenInChainId: String(chainId),
      tokenOutChainId: String(chainId),
      amount,
      type: 'EXACT_INPUT',
      slippageTolerance: 0.5,
    }),
  });
  const quoteResponse = await quoteRes.json(); // Store FULL response

  if (!quoteRes.ok) {
    throw new Error(quoteResponse.detail || 'Quote failed');
  }

  // 3. Execute swap - CRITICAL: spread quote response, strip null fields
  const swapRequest = prepareSwapRequest(quoteResponse);

  const swapRes = await fetch(`${API_URL}/swap`, {
    method: 'POST',
    headers: {
      'x-api-key': API_KEY,
      'Content-Type': 'application/json',
      'x-universal-router-version': '2.0',
      'x-agent-info': AGENT_INFO,
    },
    body: JSON.stringify(swapRequest),
  });
  const swapData = await swapRes.json();

  if (!swapRes.ok) {
    throw new Error(swapData.detail || 'Swap request failed');
  }

  // 4. Validate before broadcasting
  validateSwap(swapData.swap);

  const hash = await walletClient.sendTransaction({
    to: swapData.swap.to,
    data: swapData.swap.data,
    value: BigInt(swapData.swap.value || '0'),
  });
  return publicClient.waitForTransactionReceipt({ hash });
}
```

### Smart Contract Integration (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IUniversalRouter {
    function execute(
        bytes calldata commands,
        bytes[] calldata inputs,
        uint256 deadline
    ) external payable;
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}

contract SwapIntegration {
    IUniversalRouter public immutable router;
    address public constant PERMIT2 = 0x000000000022D473030F116dDEE9F6B43aC78BA3;

    constructor(address _router) {
        router = IUniversalRouter(_router);
    }

    function swap(
        bytes calldata commands,
        bytes[] calldata inputs,
        uint256 deadline
    ) external payable {
        router.execute{value: msg.value}(commands, inputs, deadline);
    }

    // Approve token for Permit2 (one-time setup)
    function approveToken(address token) external {
        IERC20(token).approve(PERMIT2, type(uint256).max);
    }
}
```

---

## Advanced Patterns

### Smart Account Integration (ERC-4337)

通过 ERC-4337 智能账户和委托执行 Trading API 交易。模式：

1. 从 Trading API 获取 swap calldata（标准 3 步流程）
2. 将 calldata 封装在委托赎回执行中
3. 通过 **`bundlerClient.sendUserOperation()`** 提交——始终使用 viem bundler 客户端的 `sendUserOperation` 方法（而不是自定义的 `submitUserOperation` 包装函数）

> **REQUIRED:** 最终提交步骤必须使用 viem 无权限/bundler 客户端的 `bundlerClient.sendUserOperation()`。不要编写绕过此步骤的自定义 `submitUserOperation` 包装函数——bundler 客户端自动处理 UserOperation 构建、gas 估计和提交。

```typescript
// 从 Trading API 获取 swap calldata 后：
const { to, data, value } = swapResponse.swap;

// 封装在委托执行中
const execution = {
  target: to, // Universal Router
  callData: data,
  value: BigInt(value),
};

// 通过 bundler 提交——直接使用 sendUserOperation
const userOpHash = await bundlerClient.sendUserOperation({
  account: delegateSmartAccount,
  calls: [
    {
      to: delegationManagerAddress,
      data: encodeFunctionData({
        abi: delegationManagerAbi,
        functionName: 'redeemDelegations',
        args: [[[signedDelegation]], [0], [[execution]]],
      }),
      value: execution.value,
    },
  ],
});
```

**主要注意事项**：

- 对于智能账户，使用传统批准（直接到 Universal Router）而不是 Permit2——参见 [Approval Target](#approval-target-permit2-vs-legacy-direct-to-router)
- 为 bundler gas 估计添加 20-30% 的 gas 缓冲
- 分别处理 bundler 特定的错误代码和标准交易错误

参见 [Advanced Patterns Reference](./references/advanced-patterns.md#smart-account-integration-erc-4337) 获取包含类型和错误处理的完整实现。

### L2 上的 WETH 处理

在 L2 链（Base、Optimism、Arbitrum）上，输出 ETH 的交易可能会交付 WETH 而不是原生 ETH。交易后始终检查并解包：

```typescript
import { parseAbi, type Address } from 'viem';

const WETH_ABI = parseAbi([
  'function balanceOf(address) view returns (uint256)',
  'function withdraw(uint256)',
]);

const WETH_ADDRESSES: Record<number, Address> = {
  1: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  10: '0x4200000000000000000000000000000000000006',
  8453: '0x4200000000000000000000000000000000000006',
  42161: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
};

// L2 上交易完成后：
const wethAddress = WETH_ADDRESSES[chainId];
if (wethAddress) {
  const wethBalance = await publicClient.readContract({
    address: wethAddress,
    abi: WETH_ABI,
    functionName: 'balanceOf',
    args: [accountAddress],
  });

  if (wethBalance > 0n) {
    const hash = await walletClient.writeContract({
      address: wethAddress,
      abi: WETH_ABI,
      functionName: 'withdraw',
      args: [wethBalance],
    });
    await publicClient.waitForTransactionReceipt({ hash });
  }
}
```

参见 [Advanced Patterns Reference](./references/advanced-patterns.md#weth-handling-on-l2s) 获取特定链的 WETH 地址和集成细节。

### 速率限制

Trading API 执行速率限制（每个端点约 10 次/秒）。对于批量操作：

- 在顺序 API 调用之间添加 **100-200ms 延迟**
- 对 429 响应实现 **带抖动的指数退避**
- **缓存批准结果**——批准结果在调用之间很少变化

```typescript
// 对 429 响应的指数退避
async function fetchWithRetry(url: string, init: RequestInit, maxRetries = 5): Promise<Response> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url, init);
    if (response.status !== 429 && response.status < 500) return response;
    if (attempt === maxRetries) throw new Error(`Failed after ${maxRetries} retries`);

    const delay = Math.min(200 * Math.pow(2, attempt) + Math.random() * 100, 10000);
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
  throw new Error('Unreachable');
}
```

参见 [Advanced Patterns Reference](./references/advanced-patterns.md#rate-limiting-best-practices) 获取批量操作模式和完整重试实现。

---

## 关键合约地址

### Universal Router (v4)

地址按链区分。传统的 v1 地址 `0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD` 已弃用。

| 链       | ID      | 地址                                      |
| -------- | ------- | ------------------------------------------ |
| Ethereum | 1       | `0x66a9893cc07d91d95644aedd05d03f95e1dba8af` |
| Unichain | 130     | `0xef740bf23acae26f6492b10de645d6b98dc8eaf3` |
| Optimism | 10      | `0x851116d9223fabed8e56c0e6b8ad0c31d98b3507` |
| Base     | 8453    | `0x6ff5693b99212da76ad316178a184ab56d299b43` |
| Arbitrum | 42161   | `0xa51afafe0263b40edaef0df8781ea9aa03e381a3` |
| Polygon  | 137     | `0x1095692a6237d83c6a72f3f5efedb9a670c49223` |
| Blast    | 81457   | `0xeabbcb3e8e415306207ef514f660a3f820025be3` |
| BNB      | 56      | `0x1906c1d672b88cd1b9ac7593301ca990f94eae07` |
| Zora     | 7777777 | `0x3315ef7ca28db74abadc6c44570efdf06b04b020` |
| World Chain | 480     | `0x8ac7bee993bb44dab564ea4bc9ea67bf9eb5e743` |
| Avalanche | 43114   | `0x94b75331ae8d42c1b61065089b7d48fe14aa73b7` |
| Celo     | 42220   | `0xcb695bc5d3aa22cad1e6df07801b061a05a0233a` |
| Soneium  | 1868    | `0x4cded7edf52c8aa5259a54ec6a3ce7c6d2a455df` |
| Ink      | 57073   | `0x112908dac86e20e7241b0927479ea3bf935d1fa0` |
| Monad    | 143     | `0x0d97dc33264bfc1c226207428a79b26757fb9dc3` |

测试网地址，参见 [Uniswap v4 部署](https://docs.uniswap.org/contracts/v4/deployments)。

### Permit2

| 链      | 地址                                      |
| ------- | ------------------------------------------ |
| 所有链  | `0x000000000022D473030F116dDEE9F6B43aC78BA3` |

---

## 故障排除

### 常见问题

| 问题                                                  | 解决方案                                                                                                                                                                                                     |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "额度不足"                                             | 先调用 /check_approval，再提交审批交易                                                                                                                                                                        |
| "报价过期"                                             | 延长截止时间或重新获取报价                                                                                                                                                                          |
| "滑点超出限制"                                        | 增加slippageTolerance或重试                                                                                                                                                                          |
| "流动性不足"                                           | 尝试更小的金额或不同路线                                                                                                                                                                        |
| **"缓冲区未定义"**                                    | 添加Buffer polyfill（参见关键实现说明）                                                                                                                                                      |
| **链上回滚且数据为空**                                | 在广播前验证 `swap.data` 是否为非空十六进制值                                                                                                                                                    |
| **"permitData必须是对象类型"**                          | 从请求中移除 `permitData: null` - 完全省略该字段                                                                                                                                                  |
| **"quote不匹配任何允许的类型"**                        | 不要将quote包裹在 `{quote: ...}` 中 — 直接展开到请求体中。另外检查：对于UniswapX路线，`permitData` 必须从 `/swap` 请求体中省略（参见[API验证错误](#api-validation-errors-400)） |
| **L2上收到WETH而不是ETH**                             | 交换后检查并解包WETH（参见[WETH在L2上的处理](#weth-handling-on-l2s)）                                                                                                                         |
| **429 请求过多**                                      | 实现指数退避并在批量请求之间添加延迟（参见[速率限制](#rate-limiting)）                                                                                                    |
| **415 OPTIONS预检/CORS错误**                          | 设置CORS代理（参见浏览器环境设置中的[CORS代理配置](#cors-proxy-configuration)）                                                                                                 |
| **连接钱包时walletClient未定义**                     | 使用 `@wagmi/core` 中的 `getWalletClient()` 而不是 `useWalletClient()` 钩子（参见[wagmi v2集成陷阱](#wagmi-v2-integration-pitfalls)）                                                     |
| **"请提供带有chain参数的链"**                          | 将 `chainId` 传递给 `getWalletClient(config, { chainId })`                                                                                                                                                     |
| **交换时的链不匹配错误**                               | 在调用 `getWalletClient()` 前调用 `switchChain()`（参见[wagmi v2集成陷阱](#wagmi-v2-integration-pitfalls)）                                                                                        |

### API验证错误 (400)

| 错误信息                                     | 原因                                                                    | 修复                                                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `"permitData"必须是对象类型`             | 发送 `permitData: null`                                               | 当为null时完全省略该字段                                                                          |
| `"quote"不匹配任何允许的类型`             | 将quote包裹在 `{quote: quoteResponse}`                               | 展开quote响应：`{...quoteResponse}`                                                                |
| `"quote"不匹配任何允许的类型`             | 在UniswapX（DUTCH_V2/V3/PRIORITY）`/swap` 请求体中包含 `permitData` | 对于UniswapX路线省略 `permitData` — 参见[签名与提交](#uniswapx-signing-vs-submission-flow) |
| `signature和permitData必须同时存在`   | 仅包含Permit2字段中的一个（仅限CLASSIC路线）                   | 对于CLASSIC路线同时包含或都不包含；UniswapX路线省略 `permitData`                                        |

### API错误代码

| 代码 | 含义                                                  |
| ---- | -------------------------------------------------------- |
| 400  | 请求参数无效（参见上方的验证错误）                     |
| 401  | 无效或缺少API密钥（`/permissions`包含在内）             |
| 404  | 未找到对应的交易对                                  |
| 429  | 速率限制超出                                      |
| 500  | API错误 - 实现指数退避重试          |

### 广播前检查清单

在将交换交易发送到区块链之前：

1. **验证 `swap.data`** 是非空十六进制值（不是 `''`，不是 `'0x'`）
2. **验证地址** - `swap.to` 和 `swap.from` 是有效的
3. **检查报价新鲜度** - 如果超过30秒则重新获取
4. **验证gas** - 在估计值上增加10-20%的缓冲区
5. **确认余额** - 用户有足够的代币余额

---

## 其他资源

- [Universal Router GitHub](https://github.com/Uniswap/universal-router)
- [Uniswap文档](https://docs.uniswap.org)
- [SDK单一代码库](https://github.com/Uniswap/sdks)
- [Permit2模式](https://github.com/dragonfly-xyz/useful-solidity-patterns/tree/main/patterns/permit2)
