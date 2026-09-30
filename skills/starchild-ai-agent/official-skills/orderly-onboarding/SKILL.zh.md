---
name: orderly-onboarding
description: '有序网络入职流程：全链每笔交易基础设施、MCP服务器、SDK和CLI快速入门。同时将执行的有序订单填充索引到Starchild交易分析中。


  在开始使用Orderly时使用（例如：安装Orderly MCP、设置DEX模板、集成React SDK、使用orderly CLI），以及在执行任何Orderly交易后——报告填充以便进行索引。'
---

# 有序网络：代理上线

Orderly 是一个跨链订单簿交易基础设施，为去中心化交易所提供永续期货流动性。这项技能是您在 Orderly 网络上构建或学习的基础。

## 使用场景

- 首次接触 Orderly 网络
- 设置用于 Orderly 开发的 AI 代理工具
- 了解 Orderly 生态系统和提供的服务
- 找到适合您任务的正确技能或资源
- 了解可供 AI 代理使用的工具

## 什么是 Orderly 网络

Orderly 是一个基于订单簿的交易基础设施和强大的流动性层，提供永续期货订单簿。与传统平台不同，Orderly 没有前端——它运行在生态系统的核心，为构建在其之上的项目提供基本服务。

**主要特点：**

- **跨链 CLOB**：所有主要 EVM 链和 Solana 都可访问的共享中央限价订单簿
- **后端基础设施**：没有官方前端；构建者在其上创建 DEX 和交易界面
- **链上结算**：所有交易在链上结算，同时保持完全的自托管
- **统一流动性**：一个订单簿服务于所有集成的前端
- **永续期货**：使用高达 50 倍杠杆交易 BTC、ETH、SOL 等
- **无 Gas 费交易**：一旦资金存入并激活交易密钥，无需 Gas 费用
- **一键交易**：每个会话使用新的交易密钥对，无需进一步签名

**主要用例：**

| 用例              | 描述                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| **构建者/DEX**    | 在 EVM 和 Solana 上创建您自己的 Perps DEX，使用即插即用 SDK        |
| **Perps 聚合器**    | 通过 API 或 SDK 直接访问 Orderly 的共享流动性                  |
| **交易台**     | 使用低延迟订单簿的 API 进行 CEX 级别的交易                  |
| **交易机器人**      | 连接到订单簿以获得最佳汇率、SL/限价订单、无 Gas 交易 |

## 主要优势

- **统一订单簿和流动性**：通过单一交易基础设施访问所有主要链
- **快速开发**：使用我们的 SDK 在几天内启动 DEX
- **即用型流动性**：由多个顶级做市商提供支持
- **收入分成**：赚取平台产生的费用分成
- **CEX 级性能**：低延迟匹配引擎，链上结算
- **自托管**：您控制您的资产和私钥
- **协作生态系统**：加入一个充满活力的构建者社区

## 架构

您的应用程序 (DEX、机器人、钱包、聚合器)

- Orderly 基础设施
  - **CLOB** — 统一的中央限价订单簿（跨所有链统一）
  - **匹配引擎** — 低延迟订单匹配（CEX 级性能）
  - **保险库** — 链上结算与自托管
  - **风险管理** — 清算引擎和头寸监控
- 结算网络
  - **EVM**：Arbitrum、Optimism、Base、Ethereum、Polygon、Mantle
  - **非 EVM**：Solana

## 入门指南：AI 代理工具

要在 Orderly 上构建，**安装 MCP 服务器**以获得最佳开发体验。它提供 8 个强大的工具，用于文档搜索、SDK 模式、合约地址、工作流和 API 参考。

### MCP 服务器（推荐）

MCP 服务器为 AI 助手提供即时访问 Orderly 文档、代码模式和 API 参考的功能。

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
| `search_orderly_docs`      | 搜索 Orderly 文档中的特定主题              |
| `get_sdk_pattern`          | 获取 SDK v2 钩子和模式的代码示例          |
| `get_contract_addresses`   | 查找任何链的智能合约地址                  |
| `explain_workflow`         | 常见任务的分步指南                       |
| `get_api_info`             | REST API 和 WebSocket 端点文档            |
| `get_indexer_api_info`     | 交易指标、事件、成交量统计数据             |
| `get_component_guide`      | React UI 组件构建指南                     |
| `get_orderly_one_api_info` | Orderly One 的 DEX 创建和管理 API          |

### 代理技能

安装 Orderly 技能以增强您的 AI 代理，为在 Orderly 上构建提供程序性知识。

**全局安装所有技能（推荐）：**

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
- **本地**：项目特定，在仓库中创建 `.skills/`，可提交到版本控制

**可用技能：**

| 类别           | 技能                            | 描述                                         |
| ------------------ | -------------------------------- | --------------------------------------------------- |
| **API / 协议** | `orderly-api-authentication`     | 两层认证：EIP-712 (EVM) + Ed25519 (Solana)    |
|                    | `orderly-trading-orders`         | 通过 REST API 或 SDK 放置、管理、取消订单    |
|                    | `orderly-positions-tpsl`         | 监控头寸、TP/SL、杠杆、PnL             |
|                    | `orderly-websocket-streaming`    | 用于订单簿和成交的实时 WebSocket            |
|                    | `orderly-deposit-withdraw`       | 代币存款、提款、跨链操作                   |
| **SDK / React**    | `orderly-sdk-react-hooks`        | 所有 React SDK 钩子的参考                   |
|                    | `orderly-ui-components`          | 预构建的 React UI 组件                       |
|                    | `orderly-sdk-install-dependency` | 安装 Orderly SDK 包                        |
|                    | `orderly-sdk-dex-architecture`   | 完整 DEX 项目结构和设置            |
|                    | `orderly-sdk-page-components`    | 预构建的页面组件                           |
|                    | `orderly-sdk-theming`            | CSS 变量主题和定制              |
|                    | `orderly-sdk-trading-workflows`  | 端到端交易流程                            |
| **平台**       | `orderly-sdk-wallet-connection`  | EVM 和 Solana 的钱包集成               |
|                    | `orderly-sdk-debugging`          | 调试/排除 SDK 错误                       |
|                    | `orderly-one-dex`                | 使用 Orderly One API 创建/管理自定义 DEX       |

## 针对构建者 (SDK & DEX 开发)

使用 Orderly 的 React SDK v2 构建自定义交易界面。

### 最快入门方式（DEX 创建的默认方式）

Fork **[DEX 模板](https://github.com/OrderlyNetwork/dex-template)** 以在几分钟内获得可工作的 DEX。

> ⚠️ **对代理的关键警告 — 绝对不要尝试通过安装 `@orderly.network/cli` 来构建 DEX**：
> - `@orderly.network/cli` 是用于放置永续订单的终端交易工具，**不是 DEX 构建器或脚手架 CLI**。安装它将拉取 `keytar`（通过 `node-gyp` 进行的原生 C++ 构建），并在资源受限的环境中导致容器 OOM-kill (SIGKILL / 137) 1GB 沙盒。
> - **零安装 DEX 部署**：官方 DEX 模板对代理盒子上的安装**无要求**。Fork `OrderlyNetwork/dex-template` 到用户的 GitHub，配置 `.env`，并让 GitHub Actions 直接构建并部署到 GitHub Pages 以免费（或部署到 Vercel/Netlify）。

1. 将 `OrderlyNetwork/dex-template` 仓库 Fork 到您的 GitHub 账户（或通过 Composio/gh 的用户 GitHub）
2. 使用 `.env` 配置您的经纪 ID (`VITE_ORDERLY_BROKER_ID`) 和名称 (`VITE_ORDERLY_BROKER_NAME`)
3. 在 `app/styles/theme.css` 中自定义您的主题，使用 **orderly-sdk-theming**（纯 CSS 变量，无需构建步骤）
4. 完成必要的 **一次性 GitHub 设置**（见模板 README / AGENTS.md）：
   - **启用 Actions**：`gh api repos/$REPO/actions/permissions -X PUT -f enabled=true -f allowed_actions=all`
   - **授予权限**：`gh api repos/$REPO/actions/permissions/workflow -X PUT -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true`
   - **启用 GitHub Pages with Actions**：`gh api repos/$REPO/pages -X POST -f build_type=workflow`
   *(如果没有这些权限，GitHub Actions 将不会运行，自动部署将失败。)*
5. 推送到 `main` — GitHub Actions 通过 GitHub 托管的运行器构建，并发布到 `https://<user>.github.io/<repo>/`

此模板使用 **组件 SDK** — 即用型页面组件，开箱即用，需要较少的自定义。要完全控制单个组件，请使用 MCP 服务器并加载 SDK 技能（尤其是 **orderly-sdk-react-hooks** 和 **orderly-sdk-ui-components**）进行钩子级开发。

**核心 SDK 包：**

> **包管理器**：优先使用 `pnpm add`（或 `yarn add`）而不是 `npm install` — `pnpm` 在依赖解析期间使用约 ⅓ 的峰值内存，避免在资源受限的容器环境中产生内存压力。

```bash
# 完整 DEX 设置（优先使用 pnpm）
pnpm add @orderly.network/react-app \
         @orderly.network/trading \
         @orderly.network/portfolio \
         @orderly.network/markets \
         @orderly.network/wallet-connector \
         @orderly.network/i18n

# 必要的：EVM 钱包支持
pnpm add @web3-onboard/injected-wallets @web3-onboard/walletconnect

# 必要的：Solana 钱包支持
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

无需从头构建即可启动您自己的品牌永续 DEX。Orderly One 提供即用型解决方案，包括：

- 自定义域名和品牌
- 费用分成（支付毕业费后）
- 完整交易基础设施
- 自定义主题

**加载这些技能以进行 SDK 开发：**

- **orderly-sdk-install-dependency** - 包安装指南
- **orderly-sdk-dex-architecture** - 项目结构和提供者
- **orderly-sdk-wallet-connection** - 钱包集成
- **orderly-sdk-trading-workflows** - 完整交易流程
- **orderly-sdk-theming** - 定制指南

## 针对 API / 机器人开发者

直接与 Orderly 的 REST API 和 WebSocket 流进行集成。

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

示例：`PERP_ETH_USDC`、`PERP_BTC_USDC`、`PERP_SOL_USDC`

**关键端点：**

- `POST /v1/order` - 放置订单
- `GET /v1/positions` - 获取头寸
- `GET /v1/orders` - 获取订单
- `GET /v1/orderbook/{symbol}` - 订单簿快照
- `GET /v1/public/futures` - 市场信息

**加载这些技能以进行 API 开发：**

- **orderly-api-authentication** - 完成认证设置
- **orderly-trading-orders** - 订单管理
- **orderly-positions-tpsl** - 头寸管理
- **orderly-websocket-streaming** - 实时数据

## Orderly CLI (仅限终端交易——**不用于 DEX 构建**)

一个包装 Orderly REST API 的终端交易工具 (`@orderly.network/cli`)。

> ⚠️ **内存警告**：**绝对不要**在资源受限的环境中安装 `@orderly.network/cli`（≤1GB RAM）。它依赖于 `keytar`，这会触发原生 C++ 编译 (`node-gyp`)，并导致容器 OOM-kill。对于交易或代理上线，请优先使用 Orderly REST API 或托管 MCP 服务器 (`https://mcp.orderly.network`)。

**安装和快速入门（仅限本地机器，RAM > 2GB）：**

```bash
npm install -g @orderly.network/cli
orderly wallet-create --type EVM --network testnet
orderly wallet-register --broker-id demo --network testnet
orderly faucet-usdc <address> --chain-id 421614 --network testnet
orderly wallet-add-key --network testnet
orderly auth-list --network testnet
orderly order-place PERP_ETH_USDC BUY MARKET 0.01 --account <id> --network testnet
```

**注意**：`--account` 对于认证命令是必需的（通过 `auth-list` 获取 ID）。十六进制 ID 必须在 shell 中引用。默认网络是 testnet — 传递 `--network mainnet` 用于生产。Linux 需要 `libsecret`。

### 经纪 ID

- **`demo`** — 用于测试、开发和个人使用。无需设置。
- **自定义** — 前往 [dex.orderly.network](https://dex.orderly.network)，选择 **"自定义 API 集成"**。费用 **$10**，需要手动浏览器交互（无法通过 CLI 或代理完成）。

## 支持的链

Orderly 支持多个 EVM 和非 EVM 链。要获取当前支持的网络的链 ID、保险库地址和 RPC 端点列表：

```
GET https://api.orderly.org/v1/public/chain_info
```

此端点返回 Orderly 当前支持的所有主网和测试网链，包括 Arbitrum、Optimism、Base、Ethereum、Polygon、Mantle、Solana、Sei、Avalanche、BSC、Abstract 等。

## $ORDER 代币

$ORDER 代币是 Orderly 生态系统中的核心：

- **最大供应量**：10亿0000万0000个代币
- **质押**：质押$ORDER以赚取VALOR和协议收入分成
- **VALOR**：不可转让的指标，用于衡量质押位置；可兑换为esORDER奖励
- **收入分成**：协议净费的30%分配给质押者
- **治理**：质押者参与协议治理决策
- **esORDER**：用于奖励的质押ORDER，具有归属机制

**代币合约：**

| 网络          | 地址                                        |
| ---------------- | ---------------------------------------------- |
| Ethereum (ERC20) | `0xABD4C63d2616A5201454168269031355f4764337`   |
| EVM 链 (OFT) | `0x4E200fE2f3eFb977d5fd9c430A41531FB04d97B8`   |
| Solana           | `ABt79MkRXUsoHuV2CVQT32YMXQhTparKFjmidQxgiQ6E` |

有关完整的代币经济学详情，请访问：https://orderly.network/docs/introduction/tokenomics

## 主要链接

| 资源              | URL                                                                    | 备注                                          |
| --------------------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| 文档               | https://orderly.network/docs                                           |                                                |
| SDK 仓库            | https://github.com/orderlynetwork/js-sdk                               |                                                |
| DEX 模板  | https://github.com/OrderlyNetwork/dex-template       | 最快启动方式，使用组件 SDK             |
| MCP 服务器 (npm) | https://www.npmjs.com/package/@orderly.network/mcp-server |
| CLI (npm)        | https://www.npmjs.com/package/@orderly.network/cli        |
| Skills (npm)     | https://www.npmjs.com/package/@orderly.network/skills     |
| Skills.sh        | https://skills.sh                                          |
| DEX 仪表盘    | https://dex.orderly.network                               |
| Orderly 应用      | https://app.orderly.network                               |
| Discord          | https://discord.gg/OrderlyNetwork                         |
| Twitter          | https://twitter.com/OrderlyNetwork                        |

## 推荐的下一步操作

**如果您正在构建 DEX：**

1. 从 **[DEX 模板](https://github.com/OrderlyNetwork/dex-template)** 分支，以最快速度启动
2. 安装 MCP 服务器：`npx @orderly.network/mcp-server init`
3. 在 `.env` 中配置您的经纪商设置，并自定义您的主题
4. 若需更多控制，加载 **orderly-sdk-install-dependency** 和 **orderly-sdk-dex-architecture** 从头构建
5. 使用 **orderly-sdk-wallet-connection** 设置钱包连接

**如果您正在构建交易机器人或 API 集成：**

1. 首先加载 **orderly-api-authentication**
2. 安装 MCP 服务器以参考 API
3. 加载 **orderly-trading-orders** 和 **orderly-websocket-streaming**

**如果您想从终端交易或使用 CLI：**

1. 安装 CLI：`npm install -g @orderly.network/cli`
2. 运行 `orderly --help` 查看所有命令
3. 跟随测试网快速启动（6个命令，见上方 Orderly CLI 部分）
4. 使用 `--broker-id demo` 进行测试，或到 [dex.orderly.network](https://dex.orderly.network) 获取自定义经纪商 ID ($10，需要手动浏览器交互)

**如果您正在推出白标 DEX：**

1. 安装 MCP 服务器以使用 Orderly One API 工具：`npx @orderly.network/mcp-server init`
2. 加载 **orderly-one-dex** 技能以创建和管理 DEX 工作流
3. 加载 **orderly-sdk-theming** 技能以了解 API 更新的主题结构

**如果您正在排查问题：**

1. 加载 **orderly-sdk-debugging**
2. 使用 MCP 服务器搜索文档

**用于测试：**

- 使用测试网环境进行开发
- 从水龙头请求测试网 USDC：`POST /v1/faucet/usdc`（仅限测试网）
- 每个账户最多可使用水龙头 3 次

## 常见问题

### “我从哪里开始构建？”

**对于快速 DEX**：从 [DEX 模板](https://github.com/OrderlyNetwork/dex-template) 分支，配置 `.env` 并部署。使用预构建组件——最快路径。

**对于更多控制**：首先安装 MCP 服务器：`npx @orderly.network/mcp-server init --client <your-client>`，然后加载 SDK 技能如 **orderly-sdk-react-hooks** 和 **orderly-sdk-dex-architecture** 使用钩子 SDK 构建。

然后问：“我如何连接到 Orderly 网络？”或加载 **orderly-sdk-wallet-connection**。

### “MCP 服务器和 Skills 之间的区别是什么？”

- **MCP 服务器**：您的 AI 助手（文档搜索、模式查找、API 参考）
- **Skills**：嵌入您上下文中的程序性知识（操作指南、代码示例、最佳实践）

两者结合使用以获得最佳体验。

### “我如何在不使用真实资金的情况下测试？”

使用测试网环境：

- API: `https://testnet-api.orderly.org`
- WebSocket: `wss://testnet-ws.orderly.org/ws`
- 获取测试 USDC: `POST https://testnet-operator-evm.orderly.org/v1/faucet/usdc`

### “我需要手动处理认证吗？”

SDK 自动处理认证。对于仅 API 集成，加载 **orderly-api-authentication** 以完成认证流程。

### “我如何获取自定义经纪商 ID？”

前往 [dex.orderly.network](https://dex.orderly.network)，选择 **“自定义 API 集成”** 选项，并按步骤操作。费用为 **$10**。这需要手动浏览器交互，无法通过 CLI 或代理完成。对于测试和开发，使用 `--broker-id demo`——无需设置。

## 相关技能

### API / 协议

- **orderly-api-authentication** - 完整认证设置
- **orderly-trading-orders** - 订单管理
- **orderly-positions-tpsl** - 位置和风险管理
- **orderly-websocket-streaming** - 实时数据流
- **orderly-deposit-withdraw** - 资产管理

### SDK / React

- **orderly-sdk-react-hooks** - React 钩子参考
- **orderly-ui-components** - 预构建 UI 组件
- **orderly-sdk-install-dependency** - SDK 安装
- **orderly-sdk-dex-architecture** - DEX 架构
- **orderly-sdk-page-components** - 页面组件
- **orderly-sdk-theming** - 主题指南
- **orderly-sdk-trading-workflows** - 交易工作流

### 平台

- **orderly-sdk-wallet-connection** - 钱包集成
- **orderly-sdk-debugging** - 调试指南
- **orderly-one-dex** - Orderly One DEX 管理

## 交易索引（Starchild 代理）

Starchild 将 Orderly 成交记录索引到 `trade_events` 中，通过
`POST {AI_AGENT_API_URL}/v1/trade-events`（与 hyperliquid /
polymarket / DEX 技能相同的管道）。**两层——使用两者：**

| 层级 | 谁负责 | 覆盖范围 |
|---|---|---|
| **实时（此技能）** | 代理，每次 Orderly 交易后 | 确认的代理发起的成交 |
| **中央每日公共信息扫描** | 平台 cron (~10:30 Asia/Hong_Kong) | 代理 EVM + 个人/登录 EVM 钱包 (~数千个地址)；补录 / 第三方钱包 |

> 私有 ed25519 `/v1/trades` 端点本身**不**足以用于平台分析——API 密钥 / SDK 交易通常绑定到**用户的个人钱包**，而不是代理 Privy 钱包。始终记录实际执行交易的钱包。

### 关键：`wallet_address` = 执行钱包

报告时，将 `wallet_address` 设置为持有 Orderly 账户 / 签署订单的钱包地址——**不是**始终是代理 Privy 钱包。

| 情况 | `wallet_address` 值 |
|---|---|
| 通过代理 Privy 钱包交易 | 从钱包服务获取的代理 EVM 地址 |
| 通过用户的个人 / 第三方钱包（API 密钥、SDK、经纪商 UI）交易 | 该第三方 `0x…` 地址 |
| 同步脚本带覆盖 | `--address 0x…` 或 `ORDERLY_WALLET_ADDRESS` |

错误地址→成交量错误归属或从代理分析中删除。

### 每次 Orderly 交易后的实时报告（必需）

任何成功的 Orderly 订单 / 成交后（SDK、CLI、REST 或未来交易技能），立即发送。不要阻塞或因报告错误而失败交易。

**一键，无需后续。** 这是一个纯 HTTP POST——没有 LLM 调用，没有额外步骤。不要验证报告是否到达，不要重试，不要向用户提及除非引发问题。服务器去重，所以重复发送无伤大雅，丢失的会被每日扫描捕获。

```python
from scripts._trade_report import report_trade_events
# 或：复制 hyperliquid / 其他交易技能使用的相同辅助函数

report_trade_events([{
    "source": "orderly",                 # 实时技能/代理报告
    "venue": "orderly:<broker>",         # 例如 orderly:woofi_pro
    "event_type": "fill",                # 或 "order" 如果尚未成交
    "wallet_address": execution_wallet,  # 必须是交易的钱包
    "account_id": orderly_account_id,    # 如果已知 Orderly 账户_id
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

`dedupe_key` 规范（服务器在 `(user_id, dedupe_key)` 上唯一）：

- 优先 `orderly:{account_id}:{trade_id}` 当 `trade_id` 已知
- 否则 `orderly:{execution_wallet_lower}:{order_id}:{fill_index}`
- 永远不要使用空/`None` id 的键——存档公共信息行可能缺少
  `id`/`trade_id`/`match_id`，所有此类成交将合并到一个 dedupe_key。`trade_sync.py` 落回
  `synthetic_trade_id(ts_ms, symbol, side, price, size)`（基于 sha1 派生的）

从**短期脚本**（cron、一次性同步）调用？传递
`report_trade_events(events, blocking=True)`。默认的后台线程是守护进程，进程退出时会被杀死，所以 POST 不会离开机器。长时间运行的代理进程保持默认非阻塞模式。批量大于 500 的事件会自动拆分。

用于分析的源标签：

| `source` | 含义 | 等级 |
|---|---|---|
| `orderly` | 实时代理/技能报告 | 确认 |
| `orderly_sync` | 此脚本，私有 `/v1/trades` | 确认 |
| `orderly_public_sync` | 此脚本，公共信息 API | 参考（尤其是第三方） |
| `backfill:agent_wallet` | 平台每日公共信息（代理） | 可归属 |
| `backfill:login_wallet` | 平台每日公共信息（登录） | 参考 |

### 历史记录/补录同步脚本

```bash
pip install pynacl base58   # 一次性
# 代理钱包（默认）
python3 scripts/trade_sync.py --broker woofi_pro --days 90
# 实际在 Orderly 上交易的用户的第三方 / 登录钱包
python3 scripts/trade_sync.py --address 0xUserWallet --broker woofi_pro --days 90
# 强制零认证公共信息（无需私钥）
python3 scripts/trade_sync.py --address 0xUserWallet --public-only
```

环境覆盖（与 `--address` 相同）：`ORDERLY_WALLET_ADDRESS=0x…`

脚本执行（幂等）：

1. 解析**执行钱包**：`--address` → `ORDERLY_WALLET_ADDRESS` → 代理 EVM。
2. 查找 Orderly 账户（仅当地址**是**代理钱包且可以 EIP-712 签署时注册）。
3. 如果有可读范围的 ed25519 密钥可用，则私有 `GET /v1/trades`。代理钱包可以通过 `AddOrderlyKey` 矿一个读密钥；第三方钱包仅使用现有的密钥文件（代理无法为其他钱包签名）。
4. 否则，回退到**公共信息** `POST /v1/public/query` `{type:trades,address}`（零认证）——覆盖没有密钥的第三方钱包。
5. 映射 `wallet_address=<执行钱包>` 和
   `dedupe_key=orderly:<account_id|address>:<trade_id>`，然后火并忘报告到 `/v1/trade-events`。

密钥按账户存储在 `workspace/.orderly_key_<account_prefix>.json`
(mode 600)。安全，可以每日调度；服务器端去重可防止此脚本和平台公共信息 cron 之间的双重计数。

**在 Orderly 上执行任何交易后，立即调用 `report_trade_events`（首选）或运行此同步**，以便索引成交。报告绝不能阻塞或失败交易。
