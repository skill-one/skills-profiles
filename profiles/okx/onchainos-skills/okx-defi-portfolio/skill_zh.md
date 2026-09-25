# OKX DeFi 投资组合

2 个命令用于查看跨协议和链的 DeFi 仓位和持有情况。

## 技能路由

- 对于 DeFi 存入/赎回/领取 → 使用 `okx-defi-invest`
- 对于代币价格/图表 → 使用 `okx-dex-market`
- 对于钱包代币余额 → 使用 `okx-agentic-wallet`
- 对于 DEX 现货兑换 → 使用 `okx-agentic-wallet`

## 快速入门

```bash
# 获取跨链的 DeFi 持有情况概览
onchainos defi positions \
  --address 0xYourWallet \
  --chains ethereum,bsc,solana

# 获取特定协议的详细持有情况（positions 输出中的 analysisPlatformId）
onchainos defi position-detail \
  --address 0xYourWallet \
  --chain ethereum \
  --platform-id 67890
```

## 命令索引

| # | 命令 | 描述 |
|---|---------|-------------|
| 1 | `onchainos defi support-chains` | 获取 DeFi 支持的链 |
| 2 | `onchainos defi support-platforms` | 获取 DeFi 支持的平台 |
| 3 | `onchainos defi positions --address <addr> --chains <chains>` | 获取用户 DeFi 持有情况概览 |
| 4 | `onchainos defi position-detail --address <addr> --chain <chain> --platform-id <id>` | 获取特定协议的详细持有情况 |

## 链支持

| 链 | 名称/别名 | chainIndex |
|-------|----------------|-----------|
| Ethereum | `ethereum`, `eth` | `1` |
| BSC | `bsc`, `bnb` | `56` |
| Polygon | `polygon`, `matic` | `137` |
| Arbitrum | `arbitrum`, `arb` | `42161` |
| Base | `base` | `8453` |
| X Layer | `xlayer`, `okb` | `196` |
| Avalanche | `avalanche`, `avax` | `43114` |
| Optimism | `optimism`, `op` | `10` |
| Fantom | `fantom`, `ftm` | `250` |
| Sui | `sui` | `784` |
| Tron | `tron`, `trx` | `195` |
| TON | `ton` | `607` |
| Linea | `linea` | `59144` |
| Scroll | `scroll` | `534352` |
| zkSync | `zksync` | `324` |
| Solana | `solana`, `sol` | `501` |

## 操作流程

### 第 0 步：地址解析

当用户未提供钱包地址时，在运行任何 DeFi 命令**之前**自动从 Agentic Wallet 解析地址：

```
1. onchainos wallet status          → 检查是否登录，获取活跃账户
2. onchainos wallet addresses       → 获取按链类别分组的地址：
                                       - XLayer 地址
                                       - EVM 地址（Ethereum, BSC, Polygon 等）
                                       - Solana 地址
3. 将地址匹配到目标链：
   - EVM 链 → 使用 EVM 地址
   - Solana     → 使用 Solana 地址
   - XLayer     → 使用 XLayer 地址
```

规则：
- 如果用户提供明确的地址，直接使用它 — 跳过此步骤
- 如果钱包未登录，先提示用户登录（→ `okx-agentic-wallet`）或手动提供地址
- 如果用户说“检查所有账户”或“所有钱包”，使用 `wallet balance --all` 获取所有账户 ID，然后对每个账户使用 `wallet switch <id>` + `wallet addresses`，并为每个账户查询仓位
- 如果账户有多个相同类型的地址，在继续操作前始终向用户确认解析的地址

### 第 1 步：识别意图

| 用户说 | 操作 |
|-----------|--------|
| 查看仓位 / 投资组合 / 持有情况 | `onchainos defi positions` |
| 查看特定协议的详情 | `onchainos defi position-detail` |
| 查看后赎回 / 领取 | 建议使用 `okx-defi-invest` |

### 第 2 步：收集参数

- **缺少钱包地址** → 通过第 0 步（wallet status → wallet addresses）解析，或如果未登录则询问用户
- **缺少链** → 询问用户要查询哪些链，或建议常用链（ethereum, bsc, solana）
- **缺少 platform-id** → 先运行 `defi positions` 获取 `analysisPlatformId`

### 第 3 步：显示结果

#### 显示仓位结果

当显示 `defi positions` 输出时，必须使用**完全相同**的列顺序 — 不可替换、不可遗漏：

| # | 平台 | analysisPlatformId | 链 | 仓位 | Value(USD) |
|---|---------|--------------------|----|--------|-----------|
| 1 | Aave V3 | 12345 | ETH,BSC | 2 | $120.00 |

规则：
- **`analysisPlatformId` 在每一行中都是必需的** — 用户必须复制此值以运行 `position-detail`
- **永远不要省略、隐藏或用其他字段替换 `analysisPlatformId`**
- **永远不要分组平台** — 无论价值大小，都显示每个平台为单独一行
- 原始 JSON 路径：`walletIdPlatformList[*].platformList[*]` — 每个元素是一个平台行
  - `platformName` → 平台
  - `analysisPlatformId` → analysisPlatformId
  - `networkBalanceList[*].network` → 链（用逗号连接）
  - `investmentCount` → 仓位
  - `currencyAmount` → Value(USD)

#### 显示仓位详情结果

**输出形状**：`{ "ok": true, "data": [ { "walletIdPlatformDetailList": [...] }, ... ] }` — `data` 是一个**数组**。不要直接对 `data` 调用 `.get()`；将其作为列表进行迭代。

当显示 `defi position-detail` 输出时，以**单个扁平表格**形式渲染所有代币，列精确为：

| 类型 | 资产 | 数量 | Value(USD) | investmentId | aggregateProductId | 代币合约 | 奖励 |
|------|------|------|-----------|--------------|--------------------|-----------|------|
| Supply | USDT | 1.002285 | $1.0025 | 127 | 71931 | 0x970223...7 | 0.000080 AVAX |
| Pending | sAVAX | 0.00000091 | $0.000012 | – | – | – | 平台奖励 |

规则：
- 每个代币行是一个行；从其父投资条目中合并 `investmentId` 和 `aggregateProductId`
- **`investmentId` 在每一行中都是必需的** — 用户需要它进行 `redeem`/`claim`（通过 `okx-defi-invest`）
- `aggregateProductId` — 如果存在则显示，否则 `–`
- 代币合约：显示**完整的合约地址**，不可截断；如果是原生/空则显示 `–`
- 奖励：如果存在则显示待领取奖励金额+符号，否则 `–`；平台奖励显示 `Platform reward`
- 类型：将 investType 映射为 Supply/Borrow/Stake/Farm/Pool 等；待领取奖励行使用 `Pending`
- **健康率**：在表格下方单独显示，如果 `healthRate < 1.5` 则显示警告

#### V3 池仓位 — 额外字段

对于 V3 池仓位（`positionList` 存在），每个仓位显示一个额外部分：

| tokenId | 状态 | 范围 | tickLower | tickUpper |
|---------|--------|-------|-----------|-----------|
| 93828 | ACTIVE | 0.892 – 0.992 USDC/DAI | -33500 | -30450 |

- `tokenId`: 来自 `positionList[].tokenId`
- `positionStatus`: `ACTIVE` 或 `INACTIVE`
- `range`: 来自 `positionList[].range`
- `tickLower` / `tickUpper`: 来自 `positionList[].rangeInfo.tickLower` / `rangeInfo.tickUpper`
- 这些字段对 V3 操作（添加流动性、提取、收集 V3 费用）至关重要

## investType 参考

| investType | 描述 |
|------------|-------------|
| 1 | 存款（储蓄/收益） |
| 2 | 池（流动性池） |
| 3 | 农场（收益农场） |
| 4 | 保险库 |
| 5 | 质押 |
| 6 | 借款 |
| 7 | 质押 |
| 8 | 锁定 |
| 9 | 存款 |
| 10 | 授权 |

## 执行后建议

| 刚刚完成 | 建议 |
|----------------|---------|
| `defi positions` | 1. 查看详情 → `defi position-detail`  2. 赎回 → `okx-defi-invest`  3. 领取奖励 → `okx-defi-invest` |
| `defi position-detail` | 1. 赎回仓位 → 使用 `okx-defi-invest` 并传入表格中的 `investmentId`  2. 领取奖励 → 使用 `okx-defi-invest`  3. 添加更多 → 使用 `okx-defi-invest` |
| `defi position-detail` (V3 池) | 1. 查看深度图表 → `defi depth-price-chart --investment-id <id>` (通过 `okx-defi-invest`)  2. 查看价格历史 → `defi depth-price-chart --investment-id <id> --chart-type PRICE` |

## 全局说明

- **关键 — 地址-链兼容性**：`--address` 和 `--chains` 参数必须兼容。EVM 地址（`0x…`）只能查询 EVM 链；Solana 地址（base58）只能查询 `solana`。永远不要在单个调用中混合它们 — API 将返回错误 84019（地址格式错误）。
  - `0x…` 地址 → 仅传递 EVM 链：`ethereum,bsc,polygon,arbitrum,base,xlayer,avalanche,optimism,fantom,linea,scroll,zksync`
  - base58 地址 → 仅传递 `solana`
  - Sui 地址 → 仅传递 `sui`
  - Tron 地址 (`T…`) → 仅传递 `tron`
  - TON 地址 → 仅传递 `ton`
  - 如果用户要跨 EVM 和 Solana 查询仓位，请**分别进行两次调用**并使用相应的地址
- `defi positions` 使用 `--chains`（复数，逗号分隔，例如 `--chains ethereum,bsc`）— 不要使用 `--chain`
- `defi position-detail` 使用 `--chain`（单数）— 不要使用 `--chains`
- 钱包地址参数对两个命令都是 `--address`
- `position-detail` 需要 `positions` 输出中的 `analysisPlatformId` 作为 `--platform-id`
- CLI 自动解析链名称（`ethereum` → `1`，`bsc` → `56`，`solana` → `501`）
