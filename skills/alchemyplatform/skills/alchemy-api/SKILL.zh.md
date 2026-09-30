---
name: alchemy-api
description: 使用标准 API 密钥将 Wire Alchemy 集成到应用程序代码（服务器、后端、dApp、脚本）中。这是普通服务器/后端使用的首选应用集成路径。涵盖 EVM JSON-RPC、Token API、NFT API、转账 API、价格 API、投资组合 API、模拟、Webhooks、Solana RPC、Solana DAS、Solana Yellowstone gRPC、Sui gRPC、钱包/账户套件以及运营相关主题。需要 `$ALCHEMY_API_KEY`。若在此会话中进行实时代理工作（查询、管理、本地自动化），请使用 `alchemy-cli`（首选）或 `alchemy-mcp`。对于没有 API 密钥的应用代码（自主代理按请求付费，或显式 x402/MPP），请使用 `agentic-gateway`。
---

# Alchemy API (使用 API 密钥)

使用标准 API 密钥将 Alchemy API 集成到应用程序代码中的参考和集成指南。仅此文件就足以发布基本的集成；`references/` 目录包含对每个产品表面的更深入覆盖。

## 何时使用此技能

当以下所有条件都满足时，使用 `alchemy-api`：

- 用户正在将 Alchemy 集成到**应用程序代码**（服务器、后端、dApp、工作进程、脚本）中，该代码运行在**当前代理会话之外**
- 他们拥有或愿意创建一个 Alchemy API 密钥（可在 [dashboard.alchemy.com](https://dashboard.alchemy.com/) 免费获取）

这是**正常服务器/后端使用的首选应用程序集成路径**。

## 何时使用其他技能

| 情况 | 使用此技能替代 |
| --- | --- |
| 在此会话中执行实时代理工作（查询、管理、本地机自动化）并且本地安装了 `@alchemy/cli` — 或者 CLI 和 MCP 都可用 | `alchemy-cli` |
| 在此会话中执行实时代理工作并且仅将 MCP 集成到客户端（没有 CLI） | `alchemy-mcp` |
| 执行实时代理工作并且两者都不可用 | 安装 `alchemy-cli` 并使用 `alchemy-cli` |
| 没有API密钥的应用程序代码 — 自主代理按请求付费，或用户显式希望 x402/MPP | `agentic-gateway` |

不要使用此技能从代理会话内部运行临时的实时查询 — 那是 `alchemy-cli` / `alchemy-mcp` 路径。此技能用于要发布的代码。

## 强制性的预检查关卡

在编写应用程序代码或进行任何网络调用之前：

1. 确认用户正在构建**应用程序代码**（不是请求代理运行实时查询）。如果用户正在请求实时工作，请重定向到 `alchemy-cli`（首选）或 `alchemy-mcp`。
2. 检查 `$ALCHEMY_API_KEY` 是否已设置（例如 `echo $ALCHEMY_API_KEY`）。
3. 如果 `$ALCHEMY_API_KEY` 未设置或为空，采取以下首先适用的一项：
   - **CLI 桥接（如果本地安装了 `@alchemy/cli` 则推荐）：** CLI 可以从用户的 Alchemy 账户中获取密钥，因此他们永远不会离开终端。见下文 [从 CLI 桥接到 API 密钥](#从-cli桥接到-api密钥)。
   - 告知用户他们可以在 [https://dashboard.alchemy.com/](https://dashboard.alchemy.com/) 创建一个免费 API 密钥、**或**
   - 切换到 `agentic-gateway` 技能（x402/MPP 网关，基于钱包的认证，不需要 API 密钥）。

您**必须**不调用任何无密钥或公共回退（包括 `.../v2/demo`），除非用户明确请求该端点。不作为回退使用任何公共 RPC 端点（publicnode、llamarpc、cloudflare-eth 等）。

### 从 CLI 桥接到 API 密钥

如果本地安装了 `@alchemy/cli`（使用 `command -v alchemy` 验证），请使用它在不离开终端的情况下获取密钥**并将其持久化到项目的 `.env` 文件**，以便跨终端会话持久存在，并且在运行时对应用程序可用。

> **安全提示：** 永远不要在对话输出中回显、打印或以其他方式暴露提取的 API 密钥值。导出后仅将其引用为 `$ALCHEMY_API_KEY`。将其视为密码一样对待。

```bash
# 1. 尝试从 CLI 配置中读取缓存的密钥（只读，安全地运行非交互式操作）。
KEY="$(alchemy --no-interactive --json --reveal config get api-key 2>/dev/null | jq -r .value)"

# 2. 如果为空/空值（尚未缓存密钥），运行交互式流程。
#    注意：auth login 会打开浏览器，apps select 会显示选择器，因此在此处**不要**传递 --no-interactive。如果您已经知道应用 ID，请显式传递它以跳过选择器：`alchemy --no-interactive --json apps select <id>`。
if [ -z "$KEY" ] || [ "$KEY" = "null" ]; then
  alchemy auth login              # 打开浏览器；推导认证凭据
  alchemy --json apps select      # 交互式选择器（省略 --no-interactive 以便它可以渲染）
  KEY="$(alchemy --no-interactive --json --reveal config get api-key | jq -r .value)"
fi

# 3. 持久化到项目的 .env（应用程序代码的标准做法，以便密钥在终端重新启动后仍然存在，并由 dotenv / 框架环境加载器加载）。
#    如果您的框架期望使用 .env.local，则使用 .env.local（例如 Next.js）。
ENV_FILE=".env"   # 或 ".env.local" 取决于项目约定
touch "$ENV_FILE"
if grep -q '^ALCHEMY_API_KEY=' "$ENV_FILE"; then
  # 原地替换现有行（跨 BSD/GNU sed 便携）
  sed -i.bak "s|^ALCHEMY_API_KEY=.*|ALCHEMY_API_KEY=$KEY|" "$ENV_FILE" && rm "$ENV_FILE.bak"
else
  echo "ALCHEMY_API_KEY=$KEY" >> "$ENV_FILE"
fi

# 4. 确保环境文件被 git 忽略。
grep -qxF "$ENV_FILE" .gitignore 2>/dev/null || echo "$ENV_FILE" >> .gitignore

# 5. 还要导出到当前 shell，以便代理可以立即调用 API。
export ALCHEMY_API_KEY="$KEY"
```

> **为什么我们持久化到 `.env`：** 没有它，密钥仅在当前 shell 会话中设置，当终端选项卡关闭时会消失。应用程序代码通常通过 `dotenv`（Node）、`python-dotenv`（Python）、`direnv` 或框架原生加载器（Next.js、Vite、Bun、Deno、Rails 等）加载 `.env`，因此将密钥写入 `.env` 是使密钥对 `npm run dev` 和部署应用程序的本地副本都持久的规范方式。

> **为什么整个流程有效：** CLI 是一个运行时执行器（`alchemy-cli` 技能）。当用户安装它时，您可以使用它来配置此应用程序代码技能所需的凭证，将其写入应用程序将加载的位置，然后继续 `alchemy-api` 流程的其余部分。在步骤 5 之后，继续执行下文的 [基础 URL + 认证](#基础URL+认证速查表) 和 [快速入门](#单文件快速入门-复制粘贴)。

> **注意：** 如果 `auth login` 成功但 `config get api-key` 仍然返回“未找到”，CLI 的 `setup status` 可能错误地报告了 `complete: true`，只有 `auth_token`。重新运行 `alchemy --json apps select`（或使用 `--no-interactive` 传递显式的 `<id>` 以跳过选择器）：`alchemy --no-interactive --json apps select <id>`。有关 `alchemy-cli` 技能中记录的相同注意点，请参阅预检查。

## 摘要

一个用于 AI 代理使用 API 密钥集成 Alchemy API 的自包含指南。仅此文件就足以发布基本的集成。使用参考文件以获取深度、边缘情况和高级工作流。

开发者可以始终在 [https://dashboard.alchemy.com/](https://dashboard.alchemy.com/) 创建一个免费 API 密钥。

## 首先做这些

1. 确认应用程序集成范围（见 [强制性预检查关卡](#强制性预检查关卡)）。
2. 使用下文的 [端点选择器](#端点选择器-顶级任务) 选择正确的产品。
3. 使用 [基础 URL + 认证](#基础URL+认证速查表) 表格获取正确的端点和标头。
4. 复制一个 [快速入门示例](#单文件快速入门-复制粘贴)，首先在测试网中测试。

## 基础 URL + 认证（速查表）
| 产品 | 基础 URL | 认证 | 备注 |
| --- | --- | --- | --- |
| Ethereum RPC (HTTPS) | `https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 标准 EVM 读取和写入。 |
| Ethereum RPC (WSS) | `wss://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 订阅和实时。 |
| Base RPC (HTTPS) | `https://base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | EVM L2。 |
| Base RPC (WSS) | `wss://base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 订阅和实时。 |
| Arbitrum RPC (HTTPS) | `https://arb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | EVM L2。 |
| Arbitrum RPC (WSS) | `wss://arb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 订阅和实时。 |
| BNB RPC (HTTPS) | `https://bnb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | EVM L1。 |
| BNB RPC (WSS) | `wss://bnb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 订阅和实时。 |
| Solana RPC (HTTPS) | `https://solana-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | Solana JSON-RPC。 |
| Solana Yellowstone gRPC | `https://solana-mainnet.g.alchemy.com` | `X-Token: $ALCHEMY_API_KEY` | gRPC 流式传输（Yellowstone）。 |
| Sui gRPC | `sui-mainnet.g.alchemy.com:443` | `Authorization: Bearer $ALCHEMY_API_KEY` | Sui gRPC API（对象、交易、余额、流式传输）。 |
| NFT API | `https://<网络>.g.alchemy.com/nft/v3/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | NFT 所有权和元数据。 |
| Prices API | `https://api.g.alchemy.com/prices/v1/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 通过符号或地址获取价格。 |
| Portfolio API | `https://api.g.alchemy.com/data/v1/$ALCHEMY_API_KEY` | URL 中的 API 密钥 | 多链钱包视图。 |
| Notify API | `https://dashboard.alchemy.com/api` | `X-Alchemy-Token: <ALCHEMY_NOTIFY_AUTH_TOKEN>` | 在控制台生成令牌。 |

## 端点选择器（顶级任务）
| 您需要 | 使用这个 | 技能/文件 |
| --- | --- | --- |
| EVM 读取/写入 | JSON-RPC `eth_*` | `references/node-json-rpc.md` |
| 实时事件 | `eth_subscribe` | `references/node-websocket-subscriptions.md` |
| 代币余额 | `alchemy_getTokenBalances` | `references/data-token-api.md` |
| 代币元数据 | `alchemy_getTokenMetadata` | `references/data-token-api.md` |
| 交易历史记录 | `alchemy_getAssetTransfers` | `references/data-transfers-api.md` |
| NFT 所有者 | `GET /getNFTsForOwner` | `references/data-nft-api.md` |
| NFT 元数据 | `GET /getNFTMetadata` | `references/data-nft-api.md` |
| 价格（实时） | `GET /tokens/by-symbol` | `references/data-prices-api.md` |
| 价格（历史） | `POST /tokens/historical` | `references/data-prices-api.md` |
| Portfolio（多链） | `POST /assets/*/by-address` | `references/data-portfolio-apis.md` |
| 模拟交易 | `alchemy_simulateAssetChanges` | `references/data-simulation-api.md` |
| 创建 webhook | `POST /create-webhook` | `references/webhooks-details.md` |
| Solana NFT 数据 | `getAssetsByOwner` (DAS) | `references/solana-das-api.md` |
| Solana 实时事件（按账户/按程序/日志/交易状态） | `accountSubscribe`、`programSubscribe`、`logsSubscribe`、`signatureSubscribe`（PubSub WebSocket） | `references/solana-websocket-subscriptions.md` |
| Sui 对象/交易 | `GetObject`、`GetTransaction` (gRPC) | `references/sui-grpc-objects-and-ledger.md` |
| Sui 余额 | `GetBalance`、`ListBalances` (gRPC) | `references/sui-grpc-state-and-balances.md` |
| Sui 检查点流 | `SubscribeCheckpoints` (gRPC) | `references/sui-grpc-subscriptions.md` |

## 单文件快速入门（复制粘贴）

> **没有 API 密钥？** 使用 `agentic-gateway` 技能代替。将 API 密钥 URL 替换为 `https://x402.alchemy.com/eth-mainnet/v2` 并添加 `Authorization: SIWE <token>`（或 `SIWS <token>` 用于 Solana 钱包）。有关设置，请参阅 `agentic-gateway` 技能。

### EVM JSON-RPC（读取）
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
```

### 代币余额
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"alchemy_getTokenBalances","params":["0x00000000219ab540356cbb839cbe05303d7705fa"]}'
```

### 交易历史记录
```bash
curl -s https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"alchemy_getAssetTransfers","params":[{"fromBlock":"0x0","toBlock":"latest","toAddress":"0x00000000219ab540356cbb839cbe05303d7705fa","category":["erc20"],"withMetadata":true,"maxCount":"0x3e8"}]}'
```

### NFT 所有者
```bash
curl -s "https://eth-mainnet.g.alchemy.com/nft/v3/$ALCHEMY_API_KEY/getNFTsForOwner?owner=0x00000000219ab540356cbb839cbe05303d7705fa"
```

### 价格（实时）
```bash
curl -s "https://api.g.alchemy.com/prices/v1/$ALCHEMY_API_KEY/tokens/by-symbol?symbols=ETH&symbols=USDC"
```

### 价格（历史）
```bash
curl -s -X POST "https://api.g.alchemy.com/prices/v1/$ALCHEMY_API_KEY/tokens/historical" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETH","startTime":"2024-01-01T00:00:00Z","endTime":"2024-01-02T00:00:00Z"}'
```

### 创建 Notify webhook
```bash
curl -s -X POST "https://dashboard.alchemy.com/api/create-webhook" \
  -H "Content-Type: application/json" \
  -H "X-Alchemy-Token: $ALCHEMY_NOTIFY_AUTH_TOKEN" \
  -d '{"network":"ETH_MAINNET","webhook_type":"ADDRESS_ACTIVITY","webhook_url":"https://example.com/webhook","addresses":["0x00000000219ab540356cbb839cbe05303d7705fa"]}'
```

### 验证 webhook 签名（Node）
```ts
import crypto from "crypto";

export function verify(rawBody: string, signature: string, secret: string) {
  const hmac = crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(signature));
}
```

## 网络命名规则
- 数据 API 和 JSON-RPC 使用小写网络枚举，如 `eth-mainnet`。
- Notify API 使用大写枚举，如 `ETH_MAINNET`。

## 分页 + 限制（速查表）
| 端点 | 限制 | 备注 |
| --- | --- | --- |
| `alchemy_getTokenBalances` | `maxCount` <= 100 | 使用 `pageKey` 进行分页。 |
| `alchemy_getAssetTransfers` | `maxCount` 默认 `0x3e8` | 使用 `pageKey` 进行分页。 |
| Portfolio 代币余额 | 3 个地址/网络对，20 个网络 | 支持 `pageKey`。 |
| Portfolio NFTs | 2 个地址/网络对，每个 15 个网络 | 支持 `pageKey`。 |
| 按地址获取价格 | 25 个地址，3 个网络 | POST 正文 `addresses[]`。 |
| 交易历史记录（测试版） | 1 个地址/网络对，2 个网络 | 仅限 ETH 和 BASE 主网。 |

## 常见代币地址
| 代币 | 链 | 地址 |
| --- | --- | --- |
| ETH | ethereum | `0x0000000000000000000000000000000000000000` |
| WETH | ethereum | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| USDC | ethereum | `0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eB48` |
| USDC | base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

## 错误模式 + 重试
- HTTP `429` 表示速率限制。使用带抖动的指数退避重试。
- 即使 HTTP 200，JSON-RPC 错误也会出现在 `error` 字段中。
- 使用 `pageKey` 在失败后恢复分页。
- 在重新连接时分页 websocket 事件。

## 技能映射

有关按产品区域（Node、数据、Webhooks、Solana、Sui gRPC、钱包、Rollups、配方、运营、生态系统）组织的所有 90 多个参考文件的完整索引，请参阅 `references/skill-map.md`。

快速类别概述：
- **Node**: JSON-RPC、WebSocket、调试、跟踪、增强 API、实用工具
- **数据**: NFT、Portfolio、价格、模拟、代币、交易
- **Webhooks**: 地址活动、自定义（GraphQL）、NFT 活动、有效负载、签名
- **Solana**: JSON-RPC、DAS、Yellowstone gRPC（流式传输）、钱包
- **Sui gRPC**: 对象、交易、余额、Move 包、名称服务、订阅、签名验证
- **钱包**: 账户套件、捆绑器、Gas 管理器、钱包 API（以前称为“智能钱包”）
- **Rollups**: L2/L3 部署概述
- **配方**: 10 个端到端集成工作流
- **运营**: 认证、速率限制、监控、最佳实践
- **生态系统**: viem、ethers、wagmi、Hardhat、Foundry、Anchor，以及更多

## 转移到其他技能

| 用户想要... | 转移到 |
| --- | --- |
| 在此会话中运行一次性实时查询、管理命令或本地机自动化（安装了 CLI） | `alchemy-cli` |
| 在此会话中运行一次性实时查询（仅 MCP 集成在客户端） | `alchemy-mcp` |
| 构建没有 API 密钥的应用程序代码（自主代理，或显式 x402/MPP） | `agentic-gateway` |

## 故障排除

### API 密钥无效
- 验证 `$ALCHEMY_API_KEY` 是否已设置：`echo $ALCHEMY_API_KEY`
- 确认密钥在 [dashboard.alchemy.com](https://dashboard.alchemy.com/) 有效
- 检查是否允许列表限制密钥仅限于特定 IP/域（见 `references/operational-allowlists.md`）

### HTTP 429（速率限制）
- 在重试之前使用带抖动的指数退避
- 检查 Alchemy 控制台中的计算单元预算
- 有关每个计划的限制，请参阅 `references/operational-rate-limits-and-compute-units.md`

### 错误的网络缩写
- 数据API和JSON-RPC使用小写：`eth-mainnet`, `base-mainnet`
- 通知API使用大写：`ETH_MAINNET`, `BASE_MAINNET`
- 请参阅`references/operational-supported-networks.md`获取完整列表

### JSON-RPC错误与HTTP 200
- Alchemy即使在200状态码下也会在`error`字段中返回JSON-RPC错误
- 除了HTTP状态码外，始终检查`response.error`

## 官方链接
- [开发者文档](https://www.alchemy.com/docs)
- [入门指南](https://www.alchemy.com/docs/get-started)
- [创建免费API密钥](https://dashboard.alchemy.com/)
