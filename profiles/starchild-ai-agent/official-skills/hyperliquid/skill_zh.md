# Hyperliquid 交易

在 Hyperliquid 上交易永续期货和现货代币，Hyperliquid 是一个完全链上化的去中心化交易所。订单使用此代理的 EVM 钱包进行签名，并直接提交到 Hyperliquid L1。

## 前置条件

在交易之前，钱包策略必须处于活动状态。加载 **wallet-policy** 技能并提出标准通配符策略（拒绝密钥导出 + 允许 `*`）。这涵盖了所有 Hyperliquid 操作——USDC 存款、EIP-712 订单签名和提款。

## 运行时模型：如何调用 Hyperliquid（首先阅读此部分）

此技能是 **script-delivery**。它注册 **没有** `hl_*` 代理工具——调用 `hl_deposit`、`hl_order` 或任何其他 `hl_*` 名称作为工具将始终以“在注册表中找不到”失败。这是设计如此，而不是错误或缺失安装。

有且仅有两条工作通道：

### 通道 1 — 只读查询 (`exports.py`)

```python
from core.skill_tools import hyperliquid

account = hyperliquid.hl_account()
mids    = hyperliquid.hl_market()
candles = hyperliquid.hl_candles(coin="BTC", interval="1h", hours_back=24)
```

**任何钱包，而不仅仅是您自己的。** 每个用户范围的功能都接受可选的 `address`。省略它以使用代理自己的钱包；传递 0x 地址以检查第三方。这是“分析此钱包的 Hyperliquid PnL”可回答的原因——Hyperliquid 是一个链下订单簿，因此 DeBank 风格的链扫描无法看到任何内容。

```python
hyperliquid.hl_portfolio(address="0x1f16...")   # PnL 时间序列
hyperliquid.hl_account(address="0x1f16...")     # 他们未平仓的头寸
```

32 个功能，分组：

| 组 | 功能 |
|-------|-----------|
| 账户 | `hl_account` `hl_balances` `hl_total_balance` `hl_user_role` `hl_user_fees` `hl_rate_limit` `hl_sub_accounts` `hl_referral` `hl_extra_agents` |
| PnL & 历史记录 | `hl_portfolio` `hl_fills` `hl_fills_by_time` `hl_historical_orders` `hl_ledger` `hl_funding_payments` `hl_twap_fills` `hl_vault_equities` |
| 订单 | `hl_open_orders` `hl_open_orders_full` `hl_order_status` |
| 市场 | `hl_market` `hl_orderbook` `hl_candles` `hl_funding` `hl_predicted_funding` `hl_meta` `hl_meta_ctxs` `hl_spot_meta` `hl_spot_meta_ctxs` `hl_perp_dexs` |
| 增益分享 | `hl_staking` `hl_staking_delegations` `hl_staking_rewards` |

此通道只读——在此通道上不进行写入。

### 回答“这个钱包的 PnL 是什么？”

`hl_portfolio` 返回 8 个窗口——`day`、`week`、`month`、`allTime` 和 `perp*` 等同物——每个窗口都有 `accountValueHistory` 和 `pnlHistory` 作为 `[epoch_ms, value]` 对。`pnlHistory` 在每个窗口开始时重新开始为 0，因此读取 `allTime` 以获取终身 PnL。

```python
pf = dict(hyperliquid.hl_portfolio(address=addr))
pnl = float(pf["allTime"]["pnlHistory"][-1][1])
```

为了进行成本基础重建，结合三个来源：`hl_ledger`（资本出入——存款、提款、金库移动）、`hl_fills_by_time`（每笔交易的已实现 `closedPnl`，最大 2000 每次调用——通过将最后交易的 `time` 作为下一个 `start` 来分页）、`hl_funding_payments`（支付/接收的资金）。首先检查 `hl_user_role`：角色 `"missing"` 表示地址从未在此处交易，这与“没有头寸”不同。

### 通道 2 — 写入：订单、取消、转账、存款 (`client.py`)

每个写入都通过 `HyperliquidClient` 进行，它拥有 EIP-712 签名管道。它是一个 **异步** 类——`await` 每个调用。

```python
from skills.hyperliquid.client import HyperliquidClient

client = HyperliquidClient()

# 向 Hyperliquid 桥接存款 USDC（最低 5 USDC）
res = await client.deposit_usdc(amount=500)

# 下达订单
res = await client.place_order(
    coin="BTC", is_buy=True, size=0.001, price=95000, order_type="limit",
)

# 取消 / 杠杆 / 转账 / 提款
await client.cancel_all("BTC")
await client.update_leverage(coin="BTC", leverage=5, is_cross=True)
await client.transfer_usd(amount=100, to_perp=True)
await client.withdraw_from_bridge(amount=50)
```

通道 2 的先决条件：钱包策略必须处于活动状态——加载 **wallet-policy** 技能并提出标准通配符策略（拒绝密钥导出 + 允许 `*`）。这涵盖了存款、EIP-712 订单签名和提款。

**命名注意：** 本文档的其余部分使用历史 `hl_*` 名称（例如 "`hl_deposit`”）来指代操作。这些是操作的标签，而不是可调用的工具——始终通过上述通道 1 或通道 2 进行访问。

## 可用工具

### 账户 & 市场信息

| 工具 | 它的作用 |
|------|--------------|
| `hl_total_balance` | 检查您可以交易多少（使用此进行余额检查！） |
| `hl_account` | 未平仓头寸和未实现 PnL |
| `hl_balances` | 代币持有量（USDC、HYPE 等） |
| `hl_portfolio` | **随时间变化的 PnL 和账户价值** — day/week/month/allTime |
| `hl_ledger` | 存款、提款、转账——资本出入记录 |
| `hl_fills_by_time` | 日期范围内填充，用于成本基础工作 |
| `hl_market` | 获取加密货币或股票的当前价格 |
| `hl_meta_ctxs` | 市场范围扫描：markPx、资金、OI、每项资产的交易量 |
| `hl_orderbook` | 检查订单簿深度和流动性 |
| `hl_fills` | 查看最近的交易填充和执行价格 |
| `hl_candles` | 获取价格图表（1m、5m、1h、4h、1d） |
| `hl_funding` | 检查永续期货的资金利率 |
| `hl_open_orders` | 查看待处理的订单 |
| `hl_open_orders_full` | 待处理的订单**带有**止损 / 获利了结详情 |

以上所有工具都接受 `address="0x..."` 以检查任何钱包，而不仅仅是代理自己的。

### 交易

| 工具 | 它的作用 |
|------|--------------|
| `hl_order` | 买入或卖出永续期货（加密货币/股票） |
| `hl_spot_order` | 买入或卖出现货代币 |
| `hl_tpsl_order` | 下达止损或获利了结订单 |
| `hl_leverage` | 设置杠杆（1x 到资产最大值） |
| `hl_cancel` | 取消特定订单 |
| `hl_cancel_all` | 取消所有未平仓订单 |
| `hl_modify` | 更改订单价格或大小 |

### 资金

| 工具 | 它的作用 |
|------|--------------|
| `hl_deposit` | 从 Arbitrum 添加 USDC（最低 $5） |
| `hl_withdraw` | 将 USDC 发送到 Arbitrum（1 USDC 费用，约 5 分钟） |
| `hl_transfer_usd` | 在现货/永续之间转移 USDC（很少需要） |

### 平台

| 工具 | 它的作用 |
|------|--------------|
| `hl_approve_builder` | 批准 Starchild 建造者费用收集（第一次订单时自动完成） |
| `hl_builder_status` | 检查建造者批准状态和收集的奖励 |

---

## 快速入门

只需告诉代理您想交易什么——它将自动处理所有事情。

**示例：**

```
用户: "用 20 美元买入比特币，使用 5 倍杠杆"
代理: [检查余额 → 设置杠杆 → 下达订单 → 报告成交]
结果: "✓ 以 95,432 美元买入 0.0002 BTC，使用 5 倍杠杆。已开立头寸。"

用户: "做多 NVIDIA，50 美元，10 倍"
代理: [自动检测 NVIDIA = xyz:NVDA → 执行 → 验证]
结果: "✓ 以 198.50 美元买入 0.25 NVDA，使用 10 倍杠杆。成交价 198.62。"

用户: "卖掉我的 ETH 头寸"
代理: [检查头寸大小 → 平仓 → 报告 PnL]
结果: "✓ 以 3,421 美元卖出 0.5 ETH。实现 PnL: +$12.50"
```

**您不需要：**
- 理解账户模式或资金转移
- 手动检查余额（代理会为您做）
- 计算头寸大小（代理会为您做）
- 验证成交（代理会为您做）

**只需说您想要什么，代理会处理其余部分。**

---

## 代理行为指南

**🤖 作为代理，您应该始终自动执行这些操作（永远不要询问用户）：**

1. **检查可用资金** - 使用 `hl_total_balance` 在每次交易之前查看总可用保证金
2. **检测资产类型** - 识别用户是否想要加密货币（BTC、ETH、SOL）或股票/RWA（NVIDIA→xyz:NVDA, TESLA→xyz:TSLA）
3. **设置杠杆** - 始终调用 `hl_leverage` 在下达订单之前（除非用户指定不要）
4. **验证成交** - 在下达任何订单后，立即调用 `hl_fills` 来检查是否成交
5. **报告结果** - 告知用户结果：成交价格、大小和任何 PnL
6. **建议风险管理** - 对于杠杆头寸，提醒用户关于止损或提供设置止损

**🎯 用户只需说：** "buy X" 或 "sell Y" 或 "long Z with $N"

**🔧 您需要弄清楚：**
- 当前余额 (hl_total_balance)
- 资产解析（加密货币 vs RWA）
- 杠杆设置 (hl_leverage)
- 订单大小（根据用户 $ 数量或大小计算）
- 执行 (hl_order)
- 验证 (hl_fills)
- 向用户报告最终结果

**📊 余额检查层次结构：**
- ✅ 使用 `hl_total_balance` - 显示实际可用保证金，无论账户模式如何
- ❌ 不要使用 `hl_account` 进行余额检查 - 即使资金可用，也可能显示为 0
- ❌ 不要使用 `hl_balances` 进行保证金检查 - 仅显示现货代币

**🚀 采取主动，而不是被动：**
- 不要等待用户询问“是否成交？” - 自动检查
- 不要询问“是否检查余额？” - 直接进行
- 不要解释账户模式 - 用户不关心，直接执行

---

## 工具使用示例

### 检查账户状态

```
hl_account()              # 默认加密货币永续期货账户
hl_account(dex="xyz")     # 建造者 DEX (RWA/股票永续期货) 账户
```

返回 `marginSummary`（账户价值、已用总保证金、可提款）和 `assetPositions` 数组，其中包含每个头寸的币种、szi（已签名大小）、entryPx、未实现 PnL、杠杆。

**重要提示：** 建造者永续期货（HIP-3）使用隔离保证金——`hl_leverage` 会自动处理此问题。

### 检查现货余额

```
hl_balances()
```

返回余额数组，其中包含币种、hold、total，用于 USDC 和所有现货代币。

### 检查市场价格

```
hl_market()                  # 所有中间价
hl_market(coin="BTC")        # BTC 价格 + 元数据 (maxLeverage, szDecimals)
```

### 侧参数约定（首先阅读此部分）

所有订单工具（`hl_order`、`hl_spot_order`、`hl_tpsl_order`、`hl_modify`）
使用相同的 `side` 参数。**使用 `"buy"` 或 `"sell"`**——这些是文档中记录的值，并且应该是您的默认值。

为了安全起见，工具还接受这些别名，以便模型猜测不会在杠杆订单中反转方向：

- 买入系列: `"buy"`, `"B"`, `"bid"`, `"long"`, `"L"`, `1`, `true`
- 卖出系列: `"sell"`, `"S"`, `"A"`, `"ask"`, `"short"`, `0`, `false`

**未识别的值将导致调用失败并显示清晰的错误**——工具永远不会在 `side` 含义不明确时默认为卖出（或买入）。这是有意为之：在杠杆头寸中无声地反转方向是最糟糕的失败模式。

注意：Hyperliquid 的 L1 线路协议使用 `"B"` 和 `"A"` 内部，但工具界面在这里是 `buy`/`sell`。在您的调用中使用 `buy`/`sell`，您将永远不会感到意外。

### 下达永续限价订单

```
hl_order(coin="BTC", side="buy", size=0.01, price=95000)
```

下达 GTC 限价买入订单，0.01 BTC，价格 95,000 美元。

### 下达永续市价订单

```
hl_order(coin="ETH", side="sell", size=0.1)
```

省略 `price` 提交 IoC 订单，以中间价 +/- 3% 滑点成交。

**参数格式行为：**
- 首选：传递正确的 JSON 类型（`size` 作为数字，`reduce_only` 作为布尔值）
- Hyperliquid 工具现在包括对常见 LLM 格式错误的宽容强制转换：
  - 数字字符串如 `"0.01"` → `0.01`
  - 布尔字符串如 `"true"/"false"` → `true/false`
  - 整数字符串如 `"5"`/`"5.0"` → `5`
- 无效/空/非有限值仍然会以明确的验证错误失败

### 下达仅限做市订单

```
hl_order(coin="BTC", side="buy", size=0.01, price=94000, order_type="alo")
```

ALO（仅限做市）= 做市订单。如果它会导致立即成交，则会被拒绝。

**对机器人来说实用的保护措施：** 如果您的 ALO 价格与中间价太接近（通常在流动性较高的对中约为 ~0.1%），Hyperliquid 可能会拒绝它。对于市场做市和网格机器人，首先计算当前中间价，然后跳过或移动位于您的无交叉缓冲区内的级别。

### 下达止损订单

```
hl_tpsl_order(coin="BTC", side="sell", size=0.01, trigger_px=90000, tpsl="sl")
```

如果价格降至 90,000 美元，则自动卖出 0.01 BTC。触发时作为市价订单执行。

对于触发时为限价订单（而不是市价订单）：

```
hl_tpsl_order(coin="BTC", side="sell", size=0.01, trigger_px=90000, tpsl="sl", is_market=false, limit_px=89900)
```

### 下达获利了结订单

```
hl_tpsl_order(coin="ETH", side="sell", size=0.5, trigger_px=3500, tpsl="tp")
```

如果价格升至 3,500 美元，则自动卖出 0.5 ETH。触发时作为市价订单执行。

### 关闭永续期货头寸

```
hl_order(coin="BTC", side="sell", size=X, reduce_only=true)
```

使用 `reduce_only=true` 确保它只关闭头寸，永远不会打开新头寸。

### 下达现货订单

```
hl_spot_order(coin="HYPE", side="buy", size=10, price=25.0)
```

现货订单使用相同的界面——只需指定代币名称。

### 取消订单

```
hl_cancel(coin="BTC", order_id=12345678)
```

从 `hl_open_orders` 获取 `order_id`。

### 取消所有订单

```
hl_cancel_all()              # 取消所有订单
hl_cancel_all(coin="BTC")    # 仅取消 BTC 订单
```

### 修改订单

```
hl_modify(order_id=12345678, coin="BTC", side="buy", size=0.02, price=94500)
```

### 设置杠杆

```
hl_leverage(coin="BTC", leverage=10)               # 10 倍交叉保证金
hl_leverage(coin="ETH", leverage=5, cross=false)    # 5 倍隔离保证金
```

### 转移 USDC（很少需要）

```
hl_transfer_usd(amount=1000, to_perp=true)     # 现货 → 永续期货
hl_transfer_usd(amount=500, to_perp=false)      # 永续期货 → 现货
```

注意：通常不需要——资金会自动共享。只有在您收到错误消息称需要转移时才使用。

### 从 Arbitrum 提款 USDC

```
hl_withdraw(amount=100)                              # 提款到自己的钱包
hl_withdraw(amount=50, destination="0xABC...")        # 提款到特定地址
```

费用：Hyperliquid 扣除 1 USDC。处理时间约 5 分钟。

### 从 Arbitrum 存款 USDC

```
hl_deposit(amount=500)
```

从代理的 Arbitrum 钱包发送 USDC 到 Hyperliquid 桥接合约。最低存款：5 USDC。需要 Arbitrum 上的 USDC 余额。

### 获取 K线图

```
hl_candles(coin="BTC", interval="1h", lookback=48)
```

间隔：`1m`, `5m`, `15m`, `1h`, `4h`, `1d`。回溯小时数。

### 检查资金利率

```
hl_funding()                 # 所有预测资金
hl_funding(coin="BTC")       # BTC 预测 + 24 小时历史
```

### 获取最近成交

```
hl_fills(limit=10)
```

---

## 代币 vs RWA 解析

当用户询问要交易的代码时，您需要确定它是一个 **原生加密货币永续期货**（使用普通名称）还是一个 **RWA/股票永续期货**（使用 `xyz:TICKER` 前缀）。

### 决策流程

1. **已知加密货币** → 使用普通名称: `"BTC"`, `"ETH"`. 股票: `"xyz:NVDA"`, `"xyz:TSLA"` 等
2. **已知股票/商品/外汇** → 使用 `xyz:` 前缀: `"xyz:NVDA"`, `"xyz:TSLA"`, `"xyz:GOLD"`, 等
3. **不确定** → 使用工具调用解析:
   - 首先尝试 `hl_market(coin="X")` — 如果它返回价格，则它是加密货币永续期货
   - 如果找不到，尝试 `hl_market(dex="xyz")` 列出所有 RWA 市场，并在结果中搜索
   - 使用返回匹配项的任何工具

### 常见 RWA 类别（所有使用 `xyz:` 前缀）

| 类别 | 示例 |
|-------|----------|
| **美国股票** | `xyz:NVDA`, `xyz:TSLA`, `xyz:AAPL`, `xyz:MSFT`, `xyz:AMZN`, `xyz:GOOG`, `xyz:META`, `xyz:TSM` |
| **商品 — 金属** | `xyz:GOLD`, `xyz:SILVER`, `xyz:COPPER`, `xyz:PLATINUM`, `xyz:PALLADIUM`, `xyz:ALUMINIUM` |
| **商品 — 能源** | `xyz:CL` (WTI), `xyz:BRENTOIL`, `xyz:NATGAS`, `xyz:TTF` (EU Gas) |
| **商品 — 农业** | `xyz:CORN`, `xyz:WHEAT` |
| **商品 — 其他** | `xyz:URANIUM` |
| **指数** | `xyz:SPY` |
| **外汇** | `xyz:EUR`, `xyz:GBP`, `xyz:JPY` |

> 如果用户说“买入 NVDA”或“交易 GOLD”，使用 `xyz:NVDA` / `xyz:GOLD`。这些都是现实世界的资产，不是加密货币。

### ⚠️ HIP-3 商品价格查询

**所有 13 个商品市场都是 HIP-3 建造者部署的永续期货。** 它们的符号使用 `xyz:` 前缀（例如 `xyz:GOLD`, `xyz:CL`），而不是标准格式，如 XAU、XAG 或 WTI。

**完整商品列表：** GOLD, SILVER, COPPER, PLATINUM, PALLADIUM, ALUMINIUM, CL (WTI 原油), BRENTOIL, NATGAS, TTF (EU Gas), CORN, WHEAT, URANIUM.

**关键要点：** HIP-3 资产 **不包括** 在 `allMids`（标准价格源）中。这意味着：
- `hl_market(coin="xyz:GOLD")` 可能返回 **没有价格** 或找不到资产
- `hl_market(dex="xyz")` 列出所有建造者市场，但可能不包括中间价

**获取商品价格的可靠方法是 `hl_candles`:**

```
# 获取最新黄金价格（使用 1 小时 K线图，回溯 24 小时以获取 24 小时数据）
hl_candles(coin="xyz:GOLD", interval="1h", lookback=24)

# 获取最新铜价格
hl_candles(coin="xyz:COPPER", interval="1h", lookback=24)

# 获取最新白银价格
hl_candles(coin="xyz:SILVER", interval="1h", lookback=24)
```

最新 K 线的 `close` 字段 = 当前价格。最老 K 线的 `open` 与最新 `close` 的比较 = 24 小时变化。

### 前缀名称 — 相同工具

所有现有工具都使用 `xyz:TICKER`——只需传递前缀币种名称：

```
hl_market(coin="xyz:NVDA")                                    # 检查 NVIDIA 股票永续期货价格
hl_market(dex="xyz")                                           # 列出所有可用的 RWA/股票永续期货
hl_orderbook(coin="xyz:NVDA")                                 # 检查流动性
hl_leverage(coin="xyz:NVDA", leverage=3)                      # 设置杠杆（自动隔离）
hl_order(coin="xyz:NVDA", side="buy", size=0.5, price=188)    # 限价买入 0.5 NVDA
hl_order(coin="xyz:TSM", side="buy", size=1)                  # 市场买入 1 TSM
hl_cancel(coin="xyz:NVDA", order_id=12345678)                 # 取消订单
```

### 示例：用户说“买入 NVIDIA”

1. 识别 NVIDIA = 股票 → 使用 `xyz:NVDA`
2. `hl_market(coin="xyz:NVDA")` — 检查当前价格，杠杆限制
3. `hl_leverage(coin="xyz:NVDA", leverage=3)` — 设置杠杆（建造者永续期货使用隔离保证金）
4. `hl_order(coin="xyz:NVDA", side="buy", size=0.5, price=188)` — 下达限价买入
5. `hl_fills()` — 检查是否成交

### 注意事项

- 建造者永续期货（HIP-3）使用隔离保证金——`hl_leverage` 会自动处理此问题
- `dex` 前缀（例如 `xyz`) 识别哪个建造者部署了永续期货
- 所有工具（candles、orderbook、funding 等）在与前缀名称一起使用时工作方式相同

---

## 常见工作流程

### 查询商品价格

用户: "黄金价格是多少？" 或 "显示商品价格" 或 "石油价格？"

**名称 → 符号映射：**
- 金属: GOLD→`xyz:GOLD`, SILVER→`xyz:SILVER`, COPPER→`xyz:COPPER`, PLATINUM→`xyz:PLATINUM`, PALLADIUM→`xyz:PALLADIUM`, ALUMINIUM→`xyz:ALUMINIUM`
- 能源: WTI/Crude Oil→`xyz:CL`, Brent→`xyz:BRENTOIL`, 天然气→`xyz:NATGAS`, EU Gas→`xyz:TTF`
- 农业: Corn→`xyz:CORN`, Wheat→`xyz:WHEAT`
- 其他: Uranium→`xyz:URANIUM`

**步骤：**
1. 将商品名称映射到 HIP-3 符号，使用上面的表格
2. `hl_candles(coin="xyz:GOLD", interval="1h", lookback=24)` — 获取 24 小时的每小时 K 线
3. 当前价格 = 最后 K 线的 `close`
4. 24 小时变化 = `(last_close - first_open) / first_open * 100`
5. 如有需要，对每个商品重复上述步骤

**不要使用 `hl_market()` 进行商品查询** — HIP-3 资产不包括在 `allMids` 中。始终使用 `hl_candles`。

**流动性注意：** CL (WTI) 和 BRENTOIL 具有最高的交易量。ALUMINIUM、URANIUM、CORN、WHEAT、TTF 可能具有零或非常低的流动性——在交易这些商品之前警告用户。

### 交易加密货币永续期货 (BTC, ETH, SOL, 等)

用户: "买入 BTC" 或 "做多 ETH 使用 5 倍"

代理工作流程:
1. `hl_total_balance()` → 检查可用资金
2. `hl_leverage(coin="BTC", leverage=5)` → 设置杠杆
3. `hl_order(...)` → 下达订单
4. `hl_fills()` → 验证成交并报告结果

### 交易股票/RWA (NVIDIA, TESLA, GOLD, 等)

用户: "买入 NVIDIA" 或 "做空 TESLA"

代理工作流程:
1. 检测资产类型 → 将 "NVIDIA" 转换为 "xyz:NVDA"
2. `hl_total_balance()` → 检查可用资金
3. `hl_leverage(coin="xyz:NVDA", leverage=10)` → 设置杠杆
4. `hl_order(coin="xyz:NVDA", ...)` → 下达订单
5. `hl_fills()` → 验证成交并报告结果

### 关闭头寸

用户: "关闭我的 BTC 头寸"

代理工作流程:
1. `hl_account()` → 获取当前头寸大小
2. `hl_order(coin="BTC", side="sell", size=X, reduce_only=true)` → 关闭头寸
3. `hl_fills()` → 报告 PnL

### 网格/做市机器人循环（服务模式）

对于始终运行的机器人（在 FastAPI/worker 服务中运行）:

1. 通过 `get_open_orders(address)` 读取未平仓订单
2. 通过 `get_user_fills(address)` 读取成交
3. 使用 **成交** 作为“订单已成交”事件的来源
4. 在成交时:
   - 买入成交 → 在下一个网格级别放置配对卖出
   - 卖出成交 → 在前一个网格级别放置配对买入
5. 保持定期对账：本地状态与交易所未平仓订单

**重要提示：** 不要将“订单从未平仓订单中消失”视为保证成交。它也可能意味着取消/拒绝/过期。始终使用 `get_user_fills`（或 `get_order_status` 当需要时）进行确认。

### 现货交易

用户: "买入 100 HYPE 代币"

代理工作流程:
1. `hl_total_balance()` → 检查可用 USDC
2. `hl_spot_order(coin="HYPE", side="buy", size=100)` → 买入代币
3. `hl_balances()` → 验证购买

### 存款/提款资金

**存款:**
用户: "向 Hyperliquid 存款 500 美元 USDC"
代理: `hl_deposit(amount=500)` → 完成

**提款:**
用户: "将 100 美元提款到我的 Arbitrum 钱包"
代理: `hl_withdraw(amount=100)` → 完成（5 分钟，1 USDC 费用）

### 提款 USDC 到 Arbitrum

```
hl_deposit(amount=500)
```

将 USDC 从代理的 Arbitrum 钱包发送到 Hyperliquid 桥接合约。最低存款：5 USDC。需要 Arbitrum 上的 USDC 余额。

### 获取 K 线图

```
hl_candles(coin="BTC", interval="1h", lookback=48)
```

间隔：`1m`, `5m`, `15m`, `1h`, `4h`, `1d`。回溯小时数。

### 检查资金利率

```
hl_funding()                 # 所有预测资金
hl_funding(coin="BTC")       # BTC 预测 + 24 小时历史
```

### 获取最近成交

```
hl_fills(limit=10)
```

---

## 永续期货 vs 现货

| 方面 | 永续期货 | 现货 |
|------|-------|------|
| 工具 | `hl_order` | `hl_spot_order` |
| 杠杆 | 是的（最多为资产最大值） | 否 |
| 资金 | 支付/接收每小时 | 无 |
| 卖空 | 是的（原生） | 必须持有代币才能卖 |
| 检查头寸 | `hl_account` | `hl_balances` |

---

## 风险管理

- **交易前始终检查账户状态** — 了解您的保证金使用情况和现有头寸
- **明确设置杠杆** 在开立新头寸之前（默认值可能不同）
- **使用 reduce_only** 在关闭时——避免意外开立相反方向的订单
- **监控资金利率** — 高正资金利率意味着多头头寸持有成本高昂
- **从小尺寸开始** — Hyperliquid 每个资产都有最低订单大小（检查 szDecimals）
- **使用仅限做市订单** 节省费用（做市商 vs 交易商费率）
- **检查成交后市场订单** — IoC 订单可能部分成交或完全无法成交

---

## 建造者代码（平台费用）

Starchild 自动收集一个 **2 bps (0.02%) 建造者费用** 在通过此技能下达的每个永续期货和现货订单上。此费用支持平台运营，与 Hyperliquid 自己的交易费用分开。

**工作原理：**
- 用户第一次下达订单时，技能会自动批准 Starchild 建造者地址（由用户的 EVM 钱包签名）通过 `ApproveBuilderFee` 操作（由用户的 EVM 钱包签名）
- 所有后续订单都包括一个 `builder` 参数：`{"b": "0x2c5320F40305fFC933385c6DCec5493fbA7b98b8", "f": 20}`（20 个十分之一 bps = 2 bps）
- 费用以报价/抵押资产（USDC）的形式收取，并累积在建造者的推荐奖励中
- 用户可以在 app.hyperliquid.xyz 上随时撤销批准

**工具：**
- `hl_approve_builder` — 手动批准 Starchild 建造者（通常在第一次订单时自动完成）
- `hl_builder_status` — 检查批准状态并查看未领取的建造者奖励

**如果建造者批准失败：** 订单仍然可以通过，不会包含建造者参数。错误会被记录，但不会阻止交易。

---

## 常见错误

| 错误 | 修复 |
|------|-----|
| "未知永续期货资产" | 检查币种名称。加密货币: "BTC", "ETH". 股票: "xyz:NVDA", "xyz:TSLA" |
| "保证金不足" | 使用 `hl_total_balance` 检查资金。减小大小或添加更多 USDC |
| "订单必须具有最低价值为 $10" | 增大小。公式: `size × price ≥ $10` |
| "大小太小" | BTC 最小值通常是 0.001。检查资产的 szDecimals |
| "订单会跨越" | ALO 订单被拒绝。使用普通限价订单代替 |
| "用户或钱包不存在" | 首先使用 `hl_deposit(amount=500)` 存款 USDC |
| "最低存款是 5 USDC" | Hyperliquid 要求每次存款至少 5 USDC |
| "策略违规" | 加载钱包策略技能并提出通配符策略 |
| "统一账户激活时禁用操作" | 统一模式下（默认）阻止转账。直接下达订单即可 |
| "'side' 必须是: buy/sell ..." | 您传递了一个未识别的方向。使用 `"buy"` 或 `"sell"`。见上文的 **Side Parameter Convention** |
