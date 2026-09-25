# OKX DeFi 投资

多链 DeFi 产品发现和投资执行。CLI 内部处理精度转换、多步骤编排和验证。

CLI 参数详情，请参阅 [references/cli-reference.md](references/cli-reference.md)。

## 技能路由

- 对于 DApp 命名的投资/借贷/质押 → 使用 `okx-dapp-discovery`
- 对于 DeFi 仓位 / 持仓 → 使用 `okx-defi-portfolio`
- 对于代币价格/图表 → 使用 `okx-dex-market`
- 对于按名称/合约搜索代币 → 使用 `okx-dex-token`
- 对于 DEX 现货交易执行 → 使用 `okx-agentic-wallet`
- 对于钱包代币余额 → 使用 `okx-agentic-wallet`
- 对于广播已签署的交易 → 使用 `okx-agentic-wallet`
- 对于 Agentic Wallet 登录、余额、合约调用 → 使用 `okx-agentic-wallet`

## 命令索引

| # | 命令 | 描述 |
|---|---------|-------------|
| 1 | `defi support-chains` | 获取 DeFi 支持的链 |
| 2 | `defi support-platforms` | 获取 DeFi 支持的平台 |
| 3 | `defi list` | 按 APY 列出顶级 DeFi 产品 |
| 4 | `defi search --token <tokens> [--platform <names>] [--chain <chain>] [--product-group <group>]` | 搜索 DeFi 产品 |
| 5 | `defi detail --investment-id <id>` | 获取完整产品详情 |
| 6 | `defi invest --investment-id <id> --address <addr> --token <symbol_or_addr> --amount <minimal_units> [--chain <chain>] [--slippage <pct>] [--tick-lower <n>] [--tick-upper <n>] [--token-id <nft>]` | 单步存款 (CLI 处理准备 + 精度 + calldata) |
| 7 | `defi withdraw --investment-id <id> --address <addr> --chain <chain> [--ratio <0-1>] [--amount <minimal_units>] [--token-id <nft>] [--platform-id <pid>] [--slippage <pct>]` | 单步提款 (CLI 处理仓位查询 + calldata) |
| 8 | `defi collect --address <addr> --chain <chain> --reward-type <type> [--investment-id <id>] [--platform-id <pid>] [--token-id <nft>] [--principal-index <idx>]` | 单步领取奖励 (CLI 处理奖励检查 + calldata) |
| 9 | `defi positions --address <addr> --chains <chains>` | 按平台列出 DeFi 仓位 |
| 10 | `defi position-detail --address <addr> --chain <chain> --platform-id <pid>` | 获取详细仓位信息 |
| 11 | `defi rate-chart --investment-id <id> [--time-range <range>]` | 历史 APY 图表数据 |
| 12 | `defi tvl-chart --investment-id <id> [--time-range <range>]` | 历史 TVL 图表数据 |
| 13 | `defi depth-price-chart --investment-id <id> [--chart-type <type>] [--time-range <range>]` | V3 池深度或价格历史图表 |

## 投资类型

| productGroup | 描述 |
|-------------|-------------|
| `SINGLE_EARN` | 单代币收益 (储蓄、质押、保险箱) |
| `DEX_POOL` | 流动性池 (Uniswap V2/V3、PancakeSwap 等) |
| `LENDING` | 借贷 / 贷出 (Aave、Compound 等) |

## 链支持

CLI 自动解析链名称 (例如 `ethereum` → `1`, `bsc` → `56`, `solana` → `501`)。

## 操作流程

### 第 0 步：地址解析

当用户未提供钱包地址时，在运行任何 defi 命令 **之前** 自动从 Agentic Wallet 中解析：

```
1. onchainos wallet status          → 检查是否登录，获取活跃账户
2. onchainos wallet addresses       → 获取按链类别分组的地址：
                                       - XLayer 地址
                                       - EVM 地址 (Ethereum、BSC、Polygon 等)
                                       - Solana 地址
3. 匹配地址到目标链：
   - EVM 链 → 使用 EVM 地址
   - Solana     → 使用 Solana 地址
   - XLayer     → 使用 XLayer 地址
```

规则：
- 如果用户提供显式地址，直接使用它 — 跳过此步骤
- 如果钱包未登录，先提示用户登录 (→ `okx-agentic-wallet`) 或手动提供地址
- 如果用户说“检查所有账户”或“所有钱包”，使用 `wallet balance --all` 获取所有账户 ID，然后对每个账户使用 `wallet switch <id>` + `wallet addresses`
- 如果账户有多个相同类型的地址，始终在继续之前与用户确认解析的地址

### 存款 (投资)

```
1. defi search --token USDC --chain ethereum       → 选择 investmentId
2. defi detail --investment-id <id>                 → 确认 APY/TVL，获取 underlyingToken[].tokenAddress
3. token search --query <tokenAddress> --chains <chain>  → 获取小数位数 (例如 6) 以进行金额转换
4. 询问用户金额 → 转换: userAmount × 10^decimal (例如 100 USDC → 100000000)
5. 检查钱包余额 (okx-agentic-wallet) → 如果不足，警告用户并停止
6. defi invest --investment-id <id> --address <addr> --token USDC --amount 100000000
   → CLI 返回 calldata (APPROVE + DEPOSIT 步骤)
7. 用户签署并按顺序广播每个步骤
```

> **代币小数位数**: 从 `defi detail` 获取 `tokenAddress` → `underlyingToken[].tokenAddress`，然后使用 `token search --query <tokenAddress>` 获取 `decimal`。与 DEX 交换相同的方法。
>
> **关键 — 余额检查是必需的，在调用 `defi invest` 之前。** 您必须调用 `okx-agentic-wallet` 来验证用户是否有足够的存款代币余额，然后再生成 calldata。如果余额不足，停止并警告用户。不要在不确认余额的情况下继续 `defi invest`。跳过此步骤会浪费 gas 并导致链上交易失败。

### 提款

> **关键 — position-detail 是提款前必需的。** 您必须在每次 `defi withdraw` 前立即调用 `defi position-detail`，即使您已经从之前的调用中获得了 position 数据。不要重复使用过时的 position-detail 结果。

```
1. defi positions --address <addr> --chains ethereum
2. defi position-detail --address <addr> --chain ethereum --platform-id <pid>
   → 必须调用最新数据 — 获取 investmentId、tokenPrecision、coinAmount (当前余额)
3. 完整退出:
   defi withdraw --investment-id <id> --address <addr> --chain ethereum --ratio 1 --platform-id <pid>
   部分退出 (将 coinAmount 转换为最小单位: amount × 10^tokenPrecision):
   defi withdraw --investment-id <id> --address <addr> --chain ethereum --amount <minimal_units> --platform-id <pid>
4. 用户签署并广播
```

> **部分退出 --amount**: position-detail 返回 `coinAmount` 在人类可读格式 (例如 "2.3792") 和 `tokenPrecision` (例如 6)。转换为最小单位: `floor(2.3792 × 10^6) = 2379200` → `--amount 2379200`。

### 领取奖励

> **关键 — position-detail 是领取奖励前必需的。** 您必须在每次 `defi collect` 前立即调用 `defi position-detail`，即使您已经从之前的对话中获得了 position 数据。Position 数据 (rewards、investmentId、platformId、tokenId) 在每次链上操作 (提款、之前的 collect 等) 后都会变化，因此过时的数据会导致参数错误或交易失败。不要跳过此步骤。不要重复使用对话中早期的 position-detail 结果。

```
1. defi positions --address <addr> --chains ethereum
2. defi position-detail --address <addr> --chain ethereum --platform-id <pid>
   → 必须调用最新数据 — 不要重复使用先前的结果
3. defi collect --address <addr> --chain ethereum --reward-type REWARD_INVESTMENT --investment-id <id> --platform-id <pid>
   → CLI 返回 calldata (或如果没有奖励则跳过)
4. 用户签署并广播
```

### V3 池存款

```
1. defi search --token USDT --platform PancakeSwap --chain bsc --product-group DEX_POOL
2. defi detail --investment-id <id>
3. (可选) defi depth-price-chart --investment-id <id>
   → 显示流动性深度分布以帮助用户选择 tick 范围
4. 询问用户金额和 tick 范围
5. 检查钱包余额 (okx-agentic-wallet) → 如果不足，警告用户并停止
6. defi invest --investment-id <id> --address <addr> --token USDT --amount 100000000 --range 5
   → CLI 内部处理 calculate-entry，返回 calldata
7. 用户签署并广播
```

### 查看图表数据

使用图表命令在投资前分析产品趋势或监控现有仓位。

**APY 历史** — 在存款前检查收益趋势：
```
defi rate-chart --investment-id <id> --time-range MONTH
```
- 时间范围: `WEEK` (默认), `MONTH`, `SEASON` (3 个月), `YEAR`。`DAY` 仅适用于 V3 池。
- 返回: `timestamp`, `rate` (APY), `bonusRate` (额外奖励), `limitValue` (1=峰值, -1=谷值)。

**TVL 历史** — 评估池规模稳定性：
```
defi tvl-chart --investment-id <id> --time-range SEASON
```
- 时间范围: 与 rate-chart 相同。
- 返回: `chartVos[]` 包含 `timestamp`, `tvl` (USD), `limitValue`。

**V3 深度图表** — 查看流动性集中度以选择最佳 tick 范围：
```
defi depth-price-chart --investment-id <id>
```
- 返回: 每个tick的 `tick`, `liquidity`, `liquidityNet`, `token0Price`, `token1Price`。
- 没有 `--time-range` 参数 — DEPTH 模式始终返回当前快照。
- 在 V3 池存款前使用此功能，以识别流动性集中位置并相应选择 `tickLower`/`tickUpper`。

**V3 价格历史** — 查看代币0和代币1之间的历史相对价格：
```
defi depth-price-chart --investment-id <id> --chart-type PRICE --time-range WEEK
```
- 图表类型: `DEPTH` (默认), `PRICE`。
- `--time-range` 仅适用于 PRICE 模式: `DAY` (默认), `WEEK`。
- 返回: `token0Price`, `token1Price`, `timestamp` 每个数据点。

### 第 3 步：签署并广播 calldata

在 `invest`/`withdraw`/`collect` 返回 `dataList` 后，通过以下两种路径之一执行每个步骤：

**路径 A (用户提供的钱包)**: 用户外部签署 → 通过网关广播
```bash
# 对于每个 dataList 步骤:
# 1. 用户使用 dataList[N].to, dataList[N].serializedData, dataList[N].value 外部签署 tx
# 2. 广播:
onchainos gateway broadcast --signed-tx <signed_hex> --address <addr> --chain <chain>
# 3. 等待确认:
onchainos gateway orders --address <addr> --chain <chain> --order-id <orderId>
# → 等待 txStatus=2，然后继续下一步
```

**路径 B (Agentic Wallet)**: 通过 `wallet contract-call` 签署并广播

EVM 链 (Ethereum、BSC、Polygon、Arbitrum、Base 等):
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain <chainIndex> \
  --input-data <dataList[N].serializedData> \
  --value <value_in_UI_units> \
  --biz-type defi
```

EVM (XLayer):
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain 196 \
  --input-data <dataList[N].serializedData> \
  --value <value_in_UI_units> \
  --biz-type defi
```

Solana:
```bash
onchainos wallet contract-call \
  --to <dataList[N].to> \
  --chain 501 \
  --unsigned-tx <dataList[N].serializedData> \
  --biz-type defi
```

`contract-call` 内部处理 TEE 签署和广播 — 无需单独的广播步骤。

**`--value` 单位转换**: `dataList[].value` 是最小单位 (wei)。`contract-call --value` 期望 UI 单位。转换: `value_UI = value / 10^nativeToken.decimal` (例如 18 对于 ETH/POL, 9 对于 SOL)。如果 `value` 是 `""`, `"0"`, 或 `"0x0"`，使用 `"0"`。

**`--chain` 映射**: `contract-call` 和 `gateway broadcast` 需要 `realChainIndex` (例如 `1`=Ethereum, `137`=Polygon, `56`=BSC, `501`=Solana, `196`=XLayer)。

**执行规则**:
- 首先执行 `dataList[0]`，然后 `dataList[1]`，等等。永远不要并行执行。
- 在执行下一步之前等待链上确认 (Path A: `txStatus=2`; Path B: `contract-call` 返回 txHash)。
- 如果任何步骤失败，停止所有剩余步骤并报告哪些步骤成功/失败。

> `invest`/`withdraw`/`collect` 仅返回 **未签署的 calldata** — 它们不广播。CLI 从不持有私钥。

## 显示搜索 / 列表结果

| # | 平台 | 链 | investmentId | 名称 | APY | TVL |
|---|---------|-------|-------------|------|-----|-----|
| 1 | Aave V3 | ETH | 9502 | USDC | 1.89% | $3.52B |

- `investmentId` 在每一行中都是 **必需的**
- `rate` 是十进制 → 乘以 100 并附加 `%`
- `tvl` → 格式化为人类可读的美元 ($3.52B, $537M)
- 原样显示数据 — 不要对 APY 值进行编辑

## rewardType 参考

| rewardType | 使用场景 | 必需参数 |
|------------|-------------|-----------------|
| `REWARD_PLATFORM` | 协议级奖励 (例如 AAVE 代币) | `--platform-id` |
| `REWARD_INVESTMENT` | 产品挖矿/质押奖励 | `--investment-id` + `--platform-id` |
| `V3_FEE` | V3 交易费收集 | `--investment-id` + `--token-id` |
| `REWARD_OKX_BONUS` | OKX 奖励奖励 | `--investment-id` + `--platform-id` |
| `REWARD_MERKLE_BONUS` | 基于默克尔证明的奖励 | `--investment-id` + `--platform-id` |
| `UNLOCKED_PRINCIPAL` | 锁定后解锁的本金 | `--investment-id` + `--principal-index` |

## 关键协议规则

- **Aave 借款**: 内部使用 `callDataType=WITHDRAW` — 不要暴露给用户
- **Aave 偿还**: 内部使用 `callDataType=DEPOSIT` — 不要暴露给用户
- **V3 池退出**: 传递 `--token-id` + `--ratio` (例如 `--ratio 1` 用于完整退出)
- **部分提款 (非 V3)**: 传递 `--amount` 用于退出金额
- **完整提款**: `--ratio 1`

## 执行后建议

| 刚刚完成 | 建议 |
|----------------|---------|
| `defi list` / `defi search` | 查看详情 → `defi detail`，或开始存款流程 |
| `defi detail` | 检查趋势 → `defi rate-chart` / `defi tvl-chart`，或继续 → `defi invest` |
| `defi detail` (V3 池) | 查看深度 → `defi depth-price-chart`，检查价格历史 → `defi depth-price-chart --chart-type PRICE` |
| `defi invest` 成功 | 查看仓位 → `okx-defi-portfolio`，或搜索更多 |
| `defi withdraw` 成功 | 查看仓位 → `okx-defi-portfolio`，或检查余额 → `okx-agentic-wallet` |
| `defi collect` 成功 | 查看仓位 → `okx-defi-portfolio`，或交换奖励 → `okx-agentic-wallet` |

## 错误代码

| 代码 | 场景 | 处理 |
|------|----------|----------|
| 84400 | 参数为空 | 检查必需参数 — 部分退出需要 `--amount` 或 `--ratio` |
| 84021 | 资产同步 | "仓位数据正在同步，请稍后重试" |
| 84023 | expectOutputList 无效 | CLI 自动从 position-detail 构建; 重试或传递 `--platform-id` |
| 84014 | 余额检查失败 | 余额不足 — 使用 `okx-agentic-wallet` 检查 |
| 84018 | 平衡失败 | V3 平衡失败 — 调整价格范围或增加 slippage |
| 84010 | 代币不支持 | 通过 `defi detail` 检查支持的代币 |
| 84001 | 平台不支持 | DeFi 平台不支持 |
| 84016 | 合约执行失败 | 检查参数并重试 |
| 84019 | 地址格式不匹配 | 地址格式无效，此链 |
| 50011 | 速率限制 | 等待并重试 |

## 全局说明

- `--amount` 必须为 **最小单位** (整数)。转换: userAmount × 10^tokenPrecision。示例: 0.1 USDC (precision=6) → `--amount 100000`。从 `defi detail` 或 `defi position-detail` 获取 tokenPrecision
- 所有 defi 命令的钱包地址参数是 `--address`
- `--slippage` 默认是 `"0.01"` (1%); 建议使用 `"0.03"`–`"0.05"` 用于波动性大的 V3 池
- **关键 — Solana 交易过期**: Solana DeFi 交易使用 base58 编码的 VersionedTransaction，其 blockhash 在约 60 秒后过期。在收到 calldata 后，您必须警告用户: "此 Solana 交易必须在 60 秒内签署和广播，否则将过期。请立即签署。" 不要在发出此警告之前继续其他对话。
- **关键 — 高 APY 风险警告**: 在显示搜索/列表结果时，如果任何产品 APY > 50% (rate > 0.5)，您必须警告用户: "警告: 此产品显示 APY 超过 50%，这表明风险较高 (潜在的不可持续性损失、智能合约风险或不可持续的奖励)。请谨慎操作。" 不要在未发出此警告的情况下静默显示高 APY 产品。
- **关键 — 地址-链兼容性**: 在调用 `defi positions` 或 `defi position-detail` 时，`--address` 和链参数必须兼容。EVM 地址 (`0x…`) 只能查询 EVM 链；Solana 地址 (base58) 只能查询 `solana`。永远不要混合它们 — API 将返回错误 84019 (地址格式错误)。
  - `0x…` 地址 → 只传递 EVM 链: `ethereum,bsc,polygon,arbitrum,base,xlayer,avalanche,optimism,fantom,linea,scroll,zksync`
  - base58 地址 → 只传递 `solana`
  - 如果用户想要跨 EVM 和 Solana 查询仓位，请进行 **两次单独调用** 并使用相应的地址
- 在执行 invest/withdraw/collect 之前需要用户确认
- 用于 calldata 生成的地址必须与签署地址匹配
