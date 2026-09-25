# 有序网络：代理入职

Orderly 是一个基于订单簿的全链路交易基础设施，为去中心化交易所提供永续期货流动性。这项技能是您在 Orderly 网络上构建或学习的基础。

## 使用场景

- 首次接触 Orderly 网络
- 设置用于 Orderly 开发的 AI 代理工具
- 了解 Orderly 生态系统和提供的服务
- 找到适合您任务的正确技能或资源
- 了解可用于 AI 代理的工具

## 什么是 Orderly 网络

Orderly 是一个基于订单簿的交易基础设施和强大的流动性层，提供永续期货订单簿。与传统平台不同，Orderly 没有前端——它运行在生态系统的核心，为构建在其之上的项目提供基本服务。

**主要特点：**

- **全链路 CLOB**：可从所有主要 EVM 链和 Solana 访问的共享中央限价订单簿
- **后端基础设施**：没有官方前端；构建者创建 DEX 和交易界面
- **链上结算**：所有交易在链上结算，同时保持完全的自托管
- **统一流动性**：一个订单簿服务于所有集成的前端
- **永续期货**：使用高达 50 倍杠杆交易 BTC、ETH、SOL 等
- **无 Gas 费交易**：一旦资金存入并激活交易密钥，无需 Gas 费
- **一键交易**：每个会话一个新交易密钥对，无需进一步签名

**主要用例：**

| 用例              | 描述                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| **构建者/DEX**    | 在 EVM 和 Solana 上创建您自己的 Perps DEX，使用即插即用 SDK        |
| **Perps 聚合器** | 通过 API 或 SDK 直接访问 Orderly 的共享流动性                  |
| **交易台**     | 使用低延迟订单簿的 API 进行 CEX 级别的交易                  |
| **交易机器人**   | 连接到订单簿以获得最佳汇率、SL/限价订单、无 Gas 交易          |

## 主要优势

- **统一订单簿 & 流动性**：通过单一交易基础设施访问所有主要链
- **快速开发**：使用我们的 SDK 在几天内启动 DEX
- **即用型流动性**：由多个顶级做市商提供支持
- **收入分成**：赚取您平台产生的费用分成
- **CEX 级性能**：低延迟匹配引擎，链上结算
- **自托管**：您控制您的资产和私钥
- **协作生态系统**：加入一个充满活力的构建者社区

## 架构

您的应用程序 (DEX、机器人、钱包、聚合器)

- Orderly 基础设施
  - **CLOB** — 统一的全链路中央限价订单簿
  - **匹配引擎** — 低延迟订单匹配 (CEX 级性能)
  - **保险库** — 链上结算与自托管
  - **风险管理** — 液化引擎和头寸监控
- 结算网络
  - **EVM**：Arbitrum、Optimism、Base、Ethereum、Polygon、Mantle
  - **非 EVM**：Solana

## 入门指南：AI 代理工具

要在 Orderly 上构建，**安装 MCP 服务器**以获得最佳开发体验。它提供 8 个强大的工具，用于文档搜索、SDK 模式、合约地址、工作流程和 API 参考。

### MCP 服务器 (推荐)

MCP 服务器为 AI 助手提供即时访问 Orderly 文档、代码模式和 API 参考的权限。

**快速安装：**

```bash
npx @orderly.network/mcp-server init --client <client>
```

**支持的客户端：**

| 客户端      | 命令             | 配置文件            |
| ----------- | ------------------- | ---------------------- |
| Claude Code | `--client claude`   | `.mcp.json`            |
| Cursor      | `--client cursor`   | `.cursor/mcp.json`     |
| VS Code     | `--client vscode`   | `.vscode/mcp.json`     |
| Codex       | `--client codex`    | `~/.codex/config.toml` |
| OpenCode    | `--client opencode` | `.opencode/mcp.json`   |

**手动配置：**

如果自动设置不起作用，请将此配置添加到您的 AI 客户端：

**Claude Code** (`.mcp.json`):

```json
{
  "mcpServers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**OpenCode** (`.opencode/mcp.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "orderly": {
      "type": "local",
      "command": ["npx", "@orderly.network/mcp-server@latest"],
      "enabled": true
    }
  }
}
```

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.orderly]
command = "npx"
args = ["@orderly.network/mcp-server@latest"]
```

**MCP 服务器提供的内容：**

| 工具                       | 描述                                      |
| -------------------------- | ------------------------------------------------ |
| `search_orderly_docs`      | 搜索 Orderly 文档中的特定主题                 |
| `get_sdk_pattern`          | 获取 SDK v2 钩子和模式的代码示例              |
| `get_contract_addresses`   | 查找任何链的智能合约地址                   |
| `explain_workflow`         | 常见任务的分步指南                       |
| `get_api_info`             | REST API 和 WebSocket 端点文档             |
| `get_indexer_api_info`     | 交易指标、事件、成交量统计                 |
| `get_component_guide`      | React UI 组件构建指南                     |
| `get_orderly_one_api_info` | Orderly One API 的 DEX 创建和管理 API       |

### 代理技能

安装 Orderly 技能以增强您的 AI 代理，为在 Orderly 上构建提供程序性知识。

**全局安装所有技能 (推荐)：**

```bash
npx skills add OrderlyNetwork/skills --all --agent '*' -g
```

**本地安装所有技能：**

```bash
npx skills add OrderlyNetwork/skills --all
```

**安装特定技能：**

```bash
# 列出可用技能
npx skills add OrderlyNetwork/skills --list

# 安装特定技能
npx skills add OrderlyNetwork/skills --skill orderly-trading-orders

# 安装多个技能
npx skills add OrderlyNetwork/skills --skill orderly-api-authentication --skill orderly-trading-orders

# 为特定代理安装
npx skills add OrderlyNetwork/skills --all --agent claude-code -g
```

**全局与本地：**

- **全局 (`-g`)**：跨所有项目可用，安装到用户目录
- **本地**：项目特定，在 repo 中创建 `.skills/`，可以提交到版本控制

**可用技能：**

| 类别           | 技能                            | 描述                                         |
| ------------------ | -------------------------------- | --------------------------------------------------- |
| **API / 协议** | `orderly-api-authentication`     | 两层认证：EIP-712 (EVM) + Ed25519 (Solana)    |
|                    | `orderly-trading-orders`         | 通过 REST API 或 SDK 放置、管理、取消订单    |
|                    | `orderly-positions-tpsl`         | 监控头寸、TP/SL、杠杆、PnL             |
|                    | `orderly-websocket-streaming`    | 用于订单簿和执行的实时 WebSocket 流       |
|                    | `orderly-deposit-withdraw`       | 代币存款、提款、跨链操作                   |
| **SDK / React**    | `orderly-sdk-react-hooks`        | React SDK 钩子参考                   |
|                    | `orderly-ui-components`          | 预构建的 React UI 组件                   |
|                    | `orderly-sdk-install-dependency` | 安装 Orderly SDK 包                        |
|                    | `orderly-sdk-dex-architecture`   | 完整 DEX 项目结构和设置            |
|                    | `orderly-sdk-page-components`    | 预构建的页面组件                           |
|                    | `orderly-sdk-theming`            | CSS 变量主题和定制              |
|                    | `orderly-sdk-trading-workflows`  | 端到端交易流程                            |
| **平台**       | `orderly-sdk-wallet-connection`  | EVM 和 Solana 的钱包集成               |
|                    | `orderly-sdk-debugging`          | 调试/排除 SDK 错误                       |
|                    | `orderly-one-dex`                | 创建/管理 Orderly One API 的自定义 DEX       |

## 针对构建者 (SDK & DEX 开发)

使用 Orderly 的 React SDK v2 构建自定义交易界面。

### 最快启动方式 (DEX 创建的默认方式)

Fork **[DEX 模板](https://github.com/OrderlyNetwork/dex-template)** 以在几分钟内获得可工作的 DEX。

> ⚠️ **对代理来说至关重要——切勿尝试通过安装 `@orderly.network/cli` 来构建 DEX**：
> - `@orderly.network/cli` 是用于放置永续订单的终端交易工具，**不是** DEX 构建器或脚手架 CLI。安装它将拉取 `keytar` (通过 `node-gyp` 进行的原生 C++ 构建)，这将导致容器 OOM-kill (SIGKILL / 137) 1GB 沙盒。
> - **零安装 DEX 部署**：官方 DEX 模板不需要在代理盒子上进行大量安装。Fork `OrderlyNetwork/dex-template` 到用户的 GitHub，配置 `.env`，并让 GitHub Actions 直接构建并部署到 GitHub Pages 以免费使用（或部署到 Vercel/Netlify）。

1. 将 `OrderlyNetwork/dex-template` 存储库 Fork 到您的 GitHub 账户（或通过 Composio/gh 将其 Fork 到用户的 GitHub）
2. 使用 `.env` 配置您的经纪商 ID (`VITE_ORDERLY_BROKER_ID`) 和名称 (`VITE_ORDERLY_BROKER_NAME`)
3. 在 `app/styles/theme.css` 中自定义您的主题，使用 **orderly-sdk-theming** (纯 CSS 变量，无需构建步骤)
4. 完成**一次性 GitHub 设置**后 Fork（见模板 README / AGENTS.md）：
   - **启用 Actions**：`gh api repos/$REPO/actions/permissions -X PUT -f enabled=true -f allowed_actions=all`
   - **授予工作流程写入权限**：`gh api repos/$REPO/actions/permissions/workflow -X PUT -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true`
   - **使用 Actions 启用 GitHub Pages**：`gh api repos/$REPO/pages -X POST -f build_type=workflow`
   *(如果没有这些权限，GitHub Actions 将不会运行，自动部署将失败。)*
5. 推送到 `main` — GitHub Actions 通过 GitHub 托管的运行器构建，并发布到 `https://<user>.github.io/<repo>/`

此模板使用**组件 SDK** — 即用型预构建页面组件，需要较少的定制。对于对单个组件进行完全控制，请使用 MCP 服务器并加载 SDK 技能（特别是 **orderly-sdk-react-hooks** 和 **orderly-sdk-ui-components**）进行钩子级开发。

**核心 SDK 包：**

> **包管理器**：优先使用 `pnpm add`（或 `yarn add`）而不是 `npm install` — `pnpm` 在依赖解析期间使用约 ⅓ 的峰值内存，避免在资源受限的容器环境中产生内存压力。

```bash
# 完整 DEX 设置 (优先使用 pnpm)
pnpm add @orderly.network/react-app \
         @orderly.network/trading \
         @orderly.network/portfolio \
         @orderly.network/markets \
         @orderly.network/wallet-connector \
         @orderly.network/i18n

# 必需的：EVM 钱包支持
pnpm add @web3-onboard/injected-wallets @web3-onboard/walletconnect

# 必需的：Solana 钱包支持
pnpm add @solana/wallet-adapter-base @solana/wallet-adapter-wallets
```

**可用组件：**

- `OrderEntry` - 订单放置表单
- `Orderbook` - 市场深度显示
- `PositionsView` - 头寸管理表格
- `TradingPage` - 完整交易页面
- `Portfolio` - 用户投资组合仪表板
- `ConnectWalletButton` - 钱包连接 UI

**Orderly One (白标 DEX)：**

无需从头开始构建，即可启动您自己的品牌永续期货 DEX。Orderly One 提供即用型解决方案，包括：

- 自定义域名和品牌
- 收入分成（在支付毕业费后）
- 完整的交易基础设施
- 自定义主题

**加载这些技能以进行 SDK 开发：**

- **orderly-sdk-install-dependency** - 包安装指南
- **orderly-sdk-dex-architecture** - 项目结构和提供者
- **orderly-sdk-wallet-connection** - 钱包集成
- **orderly-sdk-trading-workflows** - 完整交易流程
- **orderly-sdk-theming** - 定制指南

## 针对 API / 机器人开发

直接与 Orderly 的 REST API 和 WebSocket 流集成。

**API 基础 URL：**

| 网络 | URL                               |
| ------- | --------------------------------- |
| Mainnet | `https://api.orderly.org`         |
| Testnet | `https://testnet-api.orderly.org` |

**WebSocket URL：**

| 网络 | URL                               |
| ------- | --------------------------------- |
| Mainnet | `wss://ws.orderly.org/ws`         |
| Testnet | `wss://testnet-ws.orderly.org/ws` |

**认证：**

- Ed25519 密钥对生成用于 API 签名
- EIP-712 钱包签名用于 EVM 账户
- Ed25519 消息签名用于 Solana 账户

**符号格式：**

```
PERP_<TOKEN>_USDC
```

示例：`PERP_ETH_USDC`, `PERP_BTC_USDC`, `PERP_SOL_USDC`

**主要端点：**

- `POST /v1/order` - 放置订单
- `GET /v1/positions` - 获取头寸
- `GET /v1/orders` - 获取订单
- `GET /v1/orderbook/{symbol}` - 订单簿快照
- `GET /v1/public/futures` - 市场信息

**加载这些技能以进行 API 开发：**

- **orderly-api-authentication** - 完整认证设置
- **orderly-trading-orders** - 订单管理
- **orderly-positions-tpsl** - 头寸和风险管理
- **orderly-websocket-streaming** - 实时数据流
- **orderly-deposit-withdraw** - 资产管理

## Orderly CLI (仅限终端交易——不用于 DEX 构建)

一个包装 Orderly REST API 的终端交易工具 (`@orderly.network/cli`)。

> ⚠️ **内存警告**：**切勿**在资源受限的环境中安装 `@orderly.network/cli`。它依赖于 `keytar`，这会触发原生 C++ 编译 (`node-gyp`)，并会导致容器 OOM-kill (SIGKILL / 137) 1GB 沙盒。对于交易或代理入职，请优先使用 Orderly REST API 或托管 MCP 服务器 (`https://mcp.orderly.network`)。

**安装和快速启动（仅限 Testnet，仅在具有 >2GB RAM 的本地机器上）：**

```bash
npm install -g @orderly.network/cli
orderly wallet-create --type EVM --network testnet
orderly wallet-register --broker-id demo --network testnet
orderly faucet-usdc <address> --chain-id 421614 --network testnet
orderly wallet-add-key --network testnet
orderly auth-list --network testnet
orderly order-place PERP_ETH_USDC BUY MARKET 0.01 --account <id> --network testnet
```

**注意：** `--account` 对于认证命令是必需的（通过 `auth-list` 获取 ID）。十六进制 ID 必须用引号引起来。默认网络是 Testnet — 使用 `--network mainnet` 用于生产。Linux 需要 `libsecret`。

### 经纪商 ID

- **`demo`** — 用于测试、开发和个人使用。无需设置。
- **自定义** — 前往 [dex.orderly.network](https://dex.orderly.network)，选择 **"Custom API integration"**。费用 **$10**，需要手动浏览器交互（无法通过 CLI 或代理完成）。

## 支持的链

Orderly 支持多个 EVM 和非 EVM 链。要获取当前支持的网络的列表及其链 ID、保险库地址和 RPC 端点：

```
GET https://api.orderly.org/v1/public/chain_info
```

此端点返回 Orderly 目前支持的所有主网和测试网链，包括 Arbitrum、Optimism、Base、Ethereum、Polygon、Mantle、Solana、Sei、Avalanche、BSC、Abstract 等。

## $ORDER 代币

$ORDER 代币是 Orderly 生态系统中的核心：

- **最大供应量**：1,000,000,000 代币
- **质押**：质押 $ORDER 以赚取 VALOR 和协议收入分成
- **VALOR**：不可转让的指标，衡量质押头寸；可兑换为 esORDER 奖励
- **收入分成**：30% 的协议净费用分配给质押者
- **治理**：质押者参与协议治理决策
- **esORDER**：用于奖励的托管 ORDER，具有归属机制

**代币合约：**

| 网络          | 地址                                        |
| ---------------- | ---------------------------------------------- |
| Ethereum (ERC20) | `0xABD4C63d2616A5201454168269031355f4764337`   |
| EVM 链 (OFT) | `0x4E200fE2f3eFb977d5fd9c430A41531FB04d97B8`   |
| Solana           | `ABt79MkRXUsoHuV2CVQT32YMXQhTparKFjmidQxgiQ6E` |

有关完整代币经济学的详细信息，请访问：https://orderly.network/docs/introduction/tokenomics

## 关键链接

| 资源              | URL                                                                    | 备注                                          |
| --------------------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| 文档         | https://orderly.network/docs                                           |                                                |
| SDK 存储库        | https://github.com/orderlynetwork/js-sdk                               |                                                |
| DEX 模板  | https://github.com/OrderlyNetwork/dex-template       | 最快启动，使用组件 SDK             |
| MCP 服务器 (npm) | https://www.npmjs.com/package/@orderly.network/mcp-server |
| CLI (npm)        | https://www.npmjs.com/package/@orderly.network/cli        |
| Skills (npm)     | https://www.npmjs.com/package/@orderly.network/skills     |
| Skills.sh        | https://skills.sh                                          |
| DEX 仪表板    | https://dex.orderly.network                               |
| Orderly 应用      | https://app.orderly.network                               |
| Discord          | https://discord.gg/OrderlyNetwork                         |
| Twitter          | https://twitter.com/OrderlyNetwork                        |

## 推荐的下一步

**如果您正在构建 DEX：**

1. Fork the **[DEX Template](https://github.com/OrderlyNetwork/dex-template)** 以获得最快的启动
2. 安装 MCP 服务器：`npx @orderly.network/mcp-server init`
3. 在 `.env` 中配置您的经纪商设置并自定义您的主题
4. 对于更多控制，加载 **orderly-sdk-install-dependency** 和 **orderly-sdk-dex-architecture** 以从头开始构建
5. 设置钱包连接，使用 **orderly-sdk-wallet-connection**

**如果您正在构建交易机器人或 API 集成：**

1. 加载 **orderly-api-authentication** 首先进行
2. 安装 MCP 服务器以获取 API 参考
3. 加载 **orderly-trading-orders** 和 **orderly-websocket-streaming**

**如果您想从终端进行交易或使用 CLI：**

1. 安装 CLI：`npm install -g @orderly.network/cli`
2. 运行 `orderly --help` 以查看所有命令
3. 跟随 Testnet 快速启动（6 个命令，见 Orderly CLI 部分）
4. 使用 `--broker-id demo` 进行测试，或前往 [dex.orderly.network](https://dex.orderly.network) 获取自定义经纪商 ID（需要手动浏览器交互）。对于测试和开发，使用 `--broker-id demo` — 无需设置。

**如果您正在推出白标 DEX：**

1. 安装 MCP 服务器以获取 Orderly One API 工具：`npx @orderly.network/mcp-server init`
2. 加载 **orderly-one-dex** 技能以了解 Orderly One DEX 创建和管理工作流程
3. 加载 **orderly-sdk-theming** 技能以了解主题结构，以便进行 API 更新

**如果您正在排除故障：**

1. 加载 **orderly-sdk-debugging**
2. 使用 MCP 服务器搜索文档

**用于测试：**

- 使用 Testnet 环境进行开发
- 从/faucet 请求 Testnet USDC：`POST /v1/faucet/usdc`（仅限 Testnet）
- 每个账户最多可以使用 faucet 3 次

## 常见问题

### “我从哪里开始构建？”

**对于快速 DEX**：Fork the [DEX Template](https://github.com/OrderlyNetwork/dex-template), configure `.env`, and deploy. 使用预构建组件——最快路径。

**对于更多控制**：首先安装 MCP 服务器：`npx @orderly.network/mcp-server init --client <your-client>`, 然后加载 SDK 技能，如 **orderly-sdk-react-hooks** 和 **orderly-sdk-dex-architecture**，以使用钩子 SDK 构建。

然后询问："如何连接到 Orderly 网络？" 或加载 **orderly-sdk-wallet-connection**。

### “MCP 服务器和技能的区别是什么？”

- **MCP 服务器**：AI 助手的运行时工具（文档搜索、模式查找、API 参考）
- **技能**：嵌入到您的上下文中的程序性知识（如何指南、代码示例、最佳实践）

使用两者以获得最佳体验。

### “我如何在不使用真实资金的情况下测试？”

使用 Testnet 环境：

- API: `https://testnet-api.orderly.org`
- WebSocket: `wss://testnet-ws.orderly.org/ws`
- 获取 Test USDC: `POST https://testnet-operator-evm.orderly.org/v1/faucet/usdc`

### “我需要手动处理认证吗？”

SDK 处理认证自动。对于 API 仅集成，加载 **orderly-api-authentication** 以获取完整的认证流程。

### “我如何获取自定义经纪商 ID？”

前往 [dex.orderly.network](https://dex.orderly.network), select the **"Custom API integration"** option, and follow the steps. It costs **$10**. 这需要手动浏览器交互，无法通过 CLI 或代理完成。对于测试和开发，使用 `--broker-id demo` — 无需设置。

## 相关技能

### API / 协议

- **orderly-api-authentication** - 完整认证设置
- **orderly-trading-orders** - 订单管理
- **orderly-positions-tpsl** - 头寸和风险管理
- **orderly-websocket-streaming** - 实时数据流
- **orderly-deposit-withdraw** - 资产管理

### SDK / React

- **orderly-sdk-react-hooks** - React 钩子参考
- **orderly-ui-components** - 预构建的 UI 组件
- **orderly-sdk-install-dependency** - SDK 安装
- **orderly-sdk-dex-architecture** - DEX 架构
- **orderly-sdk-page-components** - 页面组件
- **orderly-sdk-theming** - 主题指南
- **orderly-sdk-trading-workflows** - 交易流程

### 平台

- **orderly-sdk-wallet-connection** - 钱包集成
- **orderly-sdk-debugging** - 调试指南
- **orderly-one-dex** - Orderly One DEX 管理

## 交易索引 (Starchild 代理)

Starchild 将 Orderly 填充索引到 `trade_events`，通过 `POST {AI_AGENT_API_URL}/v1/trade-events`（与 hyperliquid / polymarket / DEX 技能相同的管道）。**两层——使用两者：**

| 层级 | 谁 | 涵盖内容 |
|---|---|---|
| **实时** | 代理, 在每个 Orderly 交易后 | 确认的代理发起的填充 |
| **中央每日公共信息扫描** | 平台 cron (~10:30 Asia/Hong_Kong) | 代理 EVM + 个人登录 EVM 钱包 (~数千个地址); 捕获/第三方钱包 |

> 私有 ed25519 `/v1/trades` 端点**本身**不足以用于平台分析——API 密钥 / SDK 交易通常绑定到**用户的个人钱包**，而不是代理 Privy 钱包。始终将 `wallet_address` 设置为实际持有 Orderly 账户 / 签署订单的地址——**不是**始终是代理 Privy 钱包。

### 关键：`wallet_address` = 执行钱包

报告时，将 `wallet_address` 设置为持有 Orderly 账户 / 签署订单的地址——**不是**始终是代理 Privy 钱包。

| 情况 | `wallet_address` 值 |
|---|---|
| 通过代理 Privy 钱包进行交易 | 代理 EVM 地址从钱包服务 |
| 通过用户的个人钱包/第三方钱包 (API 密钥、SDK、经纪商 UI) | 那个第三方 `0x…` 地址 |
| 同步脚本使用覆盖 | `--address 0x…` 或 `ORDERLY_WALLET_ADDRESS` |

错误的地址→交易量错误归因或从代理分析中丢失。

### 每个 Orderly 交易后的实时报告（必需）

在任何成功的 Orderly 订单/填充（SDK、CLI、REST 或未来的交易技能）后立即报告。报告不应阻止或因报告错误而失败交易。
**一键发送，无需后续。** 这是一个纯 HTTP POST——没有 LLM 调用，没有额外回合。不要验证报告是否已到达，不要重试，不要向用户提及，除非引发问题。服务器端去重，因此重复发送是无害的，丢失的会被每日扫描捕获。

```python
from scripts._trade_report import report_trade_events
# 或: 复制 hyperliquid / 其他交易技能中使用的相同辅助程序

report_trade_events([{
    "source": "orderly",                 # 实时技能/代理报告
    "venue": "orderly:<broker>",         # 例如 orderly:woofi_pro
    "event_type": "fill",                # 或 "order" 如果尚未成交
    "wallet_address": execution_wallet,  # 必须是执行交易的钱包
    "account_id": orderly_account_id,    # 如果知道，Orderly 账户 ID
    "symbol": "PERP_ETH_USDC",
    "side": "buy",                       # buy | sell
    "price": "2500.1",
    "size": "0.5",
    "notional_usd": "1250.05",
    "fee": "0.12",
    "fee_currency": "USDC",
    "order_id": str(order_id),
    "dedupe_key": f"orderly:{account_id}:{trade_id}",  # 稳定的唯一值
    "occurred_at": "2026-07-15T12:00:00Z",             # ISO8601 UTC
    "raw": {"trade_id": trade_id, "broker": broker},
}])
```

`dedupe_key` 规范（服务器端唯一，基于 `(user_id, dedupe_key)`）：

- 优先 `orderly:{account_id|address}:{trade_id}` 当 `trade_id` 已知时
- 否则 `orderly:{execution_wallet_lower}:{order_id}:{fill_index}`
- 永远不要使用空/`None` ID 的键发出键——归档公共信息行可能缺少 `id`/`trade_id`/`match_id`，所有此类填充都将合并到一个 dedupe_key。`trade_sync.py` 会回退到
`synthetic_trade_id(ts_ms, symbol, side, price, size)` (基于 sha1 生成的)

从**任何**在 Orderly 上执行的交易中，无论是通过代理 Privy 钱包、用户自己的钱包还是第三方钱包 (API 密钥、SDK、经纪商 UI), **立即调用 `report_trade_events`** 或运行此同步**以确保填充被索引**。报告不应阻止或因报告错误而失败交易。
