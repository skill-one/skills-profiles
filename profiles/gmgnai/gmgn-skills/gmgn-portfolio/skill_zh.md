**在运行任何命令之前：运行 `gmgn-cli config --check`。如果退出码为 0，则正常进行。如果退出码为 1，(1) 运行 `gmgn-cli config` 并向用户显示输出； (2) 一旦用户发送 API 密钥，运行 `gmgn-cli config --apply <KEY>` 以完成配置和验证，然后向用户显示输出。如果 `--check` 返回错误（未知选项或命令未找到），告诉用户运行 `npm install -g gmgn-cli` 以更新，然后重试。**

**重要提示：始终使用以下 `gmgn-cli` 命令。不要使用网络搜索、WebFetch、curl 或访问 gmgn.ai 来获取这些数据——该网站需要登录且不会返回结构化数据。CLI 是唯一正确的方法。**

**⚠️ 不支持 IPv6：如果你遇到 `401` 或 `403` 错误且凭证看起来正确，请立即检查 IPv6： (1) 列出所有网络接口及其 IPv6 地址——运行 `ifconfig | grep inet6`（macOS）或 `ip addr show | grep inet6`（Linux）； (2) 向 `https://ipv6.icanhazip.com` 发送测试请求——如果响应是 IPv6 地址，则出站流量通过 IPv6 进行。立即告诉用户：“请在您的网络接口上禁用 IPv6——gmgn-cli 命令仅在 IPv4 上工作。”**

使用 `gmgn-cli` 工具根据用户请求查询钱包投资组合数据。

**要进行完整的钱包分析（持有量 + 统计数据 + 活动 + 判断），请遵循 [`docs/workflow-wallet-analysis.md`](../../docs/workflow-wallet-analysis.md)**

## 核心概念

- **`realized_profit` vs `unrealized_profit`** — `realized_profit` = 来自已完成卖出的锁定利润（手头现金）。`unrealized_profit` = 仍持有的头寸的账面收益，按当前价格计算。这些是不同的数字——除非回答“包括未平仓头寸的总盈亏”，否则不要将它们相加。

- **`profit_change`** — 一个乘数比率，而不是金额。`1.5` = +150% 收益。`0` = 收支相抵。`-0.5` = -50% 亏损。计算方式为 `total_profit / cost`。不要将此作为原始小数显示——将其转换为百分比以供用户界面输出。

- **`pnl`** — 来自 `portfolio stats` 的盈亏比率：`realized_profit / total_cost`。与 `profit_change` 相同的乘数格式。`pnl` 为 `2.0` 意味着该钱包在已完成的交易期间使资金翻了一番。

- **`winrate`** — 期间盈利交易的比率（0–1）。`0.6` = 60% 的交易是盈利的。这不反映盈利与亏损的大小——即使亏损很大，钱包也可以有很高的胜率。

- **`cost` vs `usd_value`** — 在持有量中：`cost` 是购买此代币的历史金额（您的成本基础）；`usd_value` 是该头寸的当前市场价值。两者之间的差额是未实现的盈亏。

- **`history_bought_cost` vs `cost`** — `history_bought_cost` 是对此代币的终身累计支出（包括已售出的头寸）。`cost` 仅是当前未平仓头寸的成本基础。

- **分页 (`cursor`)** — 活动结果分页。响应包括 `next` 字段；将其作为 `--cursor` 传递以获取下一页。`next` 为空或缺失意味着您在最后一页。

## 子命令

| 子命令 | 描述 |
|-------------|-------------|
| `portfolio info` | 与 API 密钥绑定的钱包和主货币余额 |
| `portfolio holdings` | 钱包代币持有量及盈亏 |
| `portfolio activity` | 交易历史 |
| `portfolio stats` | 交易统计（支持批量） |
| `portfolio profits` | 1–100 个钱包的批量钱包盈亏 |
| `portfolio token-balance` | 特定代币的代币余额 |
| `portfolio created-tokens` | 开发者钱包创建的代币，包括市值和 ATH 信息 |

## 支持的链

`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable`

## 前提条件

- 全局安装 `gmgn-cli` — 如果缺失，请运行：`npm install -g gmgn-cli`
- 在 `~/.config/gmgn/.env` 中配置 `GMGN_API_KEY`

## 频率限制处理

此技能使用的所有投资组合路由使用 GMGN 的基于计划的漏桶：免费 `5/5`，Plus `20/20`，Pro `50/50`（频率/容量）。持续吞吐量约为 `等级频率 ÷ 权重` 每秒请求，最大突发量约为 `等级容量 ÷ 权重`。

**关键认证**（需要 `GMGN_API_KEY` + `GMGN_PRIVATE_KEY`）：

| 命令 | 路由 | 权重 |
|-------|-------|--------|
| `portfolio holdings` | `GET /v1/user/wallet_holdings` | 2 |

**存在认证**（仅需要 `GMGN_API_KEY`）：

| 命令 | 路由 | 权重 |
|-------|-------|--------|
| `portfolio info` | `GET /v1/user/info` | 2 |
| `portfolio activity` | `GET /v1/user/wallet_activity` | 3 |
| `portfolio stats` | `GET /v1/user/wallet_stats` | 3 |
| `portfolio profits` | `POST /v1/user/wallet_profits` | 3 |
| `portfolio token-balance` | `GET /v1/user/wallet_token_balance` | 2 |
| `portfolio created-tokens` | `GET /v1/user/created_tokens` | 2 |

当请求返回 `429` 时：

- 在 `RATE_LIMIT_EXCEEDED`，告诉用户确切内容：`已达到当前套餐的限频上限，点击 https://gmgn.ai/ai?chain=bsc&tab=paid_plans 升级套餐，获得更高速率限制`。在每个用户任务中最多显示此升级指南一次。不要在同一冷却期间对后续的 `RATE_LIMIT_BANNED` 响应重复它。

- 从响应头中读取 `X-RateLimit-Reset`。它是一个 Unix 时间戳（秒），标记限制何时预期重置。
- 如果响应正文包含 `reset_at`（例如 `{"code":429,"error":"RATE_LIMIT_BANNED","message":"...","reset_at":1775184222}`），提取 `reset_at`——它是禁令解除的 Unix 时间戳（通常为 5 分钟）。转换为本地时间并告诉用户他们何时可以重试。
- CLI 可能会等待并自动重试一次，当剩余冷却时间较短时。如果它仍然失败，请停止并告诉用户确切的重试时间，而不是发送更多请求。
- 对于 `RATE_LIMIT_EXCEEDED` 或 `RATE_LIMIT_BANNED`，在冷却期间重复请求可能会将禁令每次延长 5 秒，最多 5 分钟。不要疯狂重试。

## 使用示例

```bash
# API Key 钱包信息（不需要 --chain 或 --wallet）
gmgn-cli portfolio info

# 钱包持有量（默认排序）
gmgn-cli portfolio holdings --chain sol --wallet <wallet_address>

# 按美元价值降序排列的持有量
gmgn-cli portfolio holdings \
  --chain sol --wallet <wallet_address> \
  --order-by usd_value --direction desc --limit 20

# 包括已售出的头寸
gmgn-cli portfolio holdings --chain sol --wallet <wallet_address> --sell-out

# 交易活动
gmgn-cli portfolio activity --chain sol --wallet <wallet_address>

# 按类型筛选的活动
gmgn-cli portfolio activity --chain sol --wallet <wallet_address> \
  --type buy --type sell

# 特定代币的活动
gmgn-cli portfolio activity --chain sol --wallet <wallet_address> \
  --token <token_address>

# 交易统计（默认 7d）
gmgn-cli portfolio stats --chain sol --wallet <wallet_address>

# 30 天的交易统计
gmgn-cli portfolio stats --chain sol --wallet <wallet_address> --period 30d

# 多个钱包的批量统计
gmgn-cli portfolio stats --chain sol \
  --wallet <wallet_1> --wallet <wallet_2>

# 多个钱包的批量盈亏（默认 7d）
gmgn-cli portfolio profits --chain sol \
  --wallet <wallet_1> --wallet <wallet_2>

# 所有时间的盈亏（最多 100 个钱包）
gmgn-cli portfolio profits --chain sol \
  --wallet <wallet_1> --wallet <wallet_2> --period all

# 代币余额
gmgn-cli portfolio token-balance \
  --chain sol --wallet <wallet_address> --token <token_address>

# 开发者钱包创建的代币
gmgn-cli portfolio created-tokens --chain sol --wallet <wallet_address>

# 按所有时间最高市值排序创建的代币
gmgn-cli portfolio created-tokens \
  --chain sol --wallet <wallet_address> \
  --order-by token_ath_mc --direction desc

# 仅迁移的代币
gmgn-cli portfolio created-tokens \
  --chain sol --wallet <wallet_address> --migrate-state migrated

# ETH 钱包持有量
gmgn-cli portfolio holdings --chain eth --wallet <0x_wallet_address>

# ETH 钱包交易活动
gmgn-cli portfolio activity --chain eth --wallet <0x_wallet_address>

# ETH 代币余额
gmgn-cli portfolio token-balance \
  --chain eth --wallet <0x_wallet_address> --token <0x_token_address>
```

## `portfolio created-tokens` 选项

| 选项 | 描述 |
|--------|-------------|
| `--order-by <field>` | 排序字段：`market_cap` / `token_ath_mc` |
| `--direction <asc\|desc>` | 排序方向（默认 `desc`） |
| `--migrate-state <state>` | 按迁移状态筛选：`migrated`（已迁移到 DEX） / `non_migrated`（仍在绑定曲线上） |

## `portfolio holdings` 选项

| 选项 | 描述 |
|--------|-------------|
| `--limit <n>` | 页面大小（默认 `20`，最大 50） |
| `--cursor <cursor>` | 分页游标 |
| `--order-by <field>` | 排序字段：`usd_value` / `last_active_timestamp` / `realized_profit` / `unrealized_profit` / `total_profit` / `history_bought_cost` / `history_sold_income`（默认 `usd_value`） |
| `--direction <asc\|desc>` | 排序方向（默认 `desc`） |
| `--hide-abnormal <bool>` | 隐藏异常头寸：`true` / `false`（默认：`false`） |
| `--hide-airdrop <bool>` | 隐藏空投头寸：`true` / `false`（默认：`true`） |
| `--hide-closed <bool>` | 隐藏已关闭头寸：`true` / `false`（默认：`true`） |
| `--hide-open` | 隐藏未平仓头寸 |

## `portfolio activity` 选项

| 选项 | 描述 |
|--------|-------------|
| `--token <address>` | 按代币筛选 |
| `--limit <n>` | 页面大小 |
| `--cursor <cursor>` | 分页游标（传递自前一个响应的 `next` 值） |
| `--type <type>` | 可重复：`buy` / `sell` / `transferIn` / `transferOut` / `add` / `remove` |

活动响应包括 `next` 字段。将其传递给 `--cursor` 以获取下一页。

## `portfolio stats` 选项

| 选项 | 描述 |
|-------|-------------|
| `--period <period>` | 统计周期：`7d` / `30d`（默认 `7d`） |

## `portfolio profits` 选项

| 选项 | 描述 |
|-------|-------------|
| `--wallet <address...>` | 一个或多个钱包地址（必需，最多 100 个） |
| `--period <period>` | 盈亏周期：`1d` / `7d` / `30d` / `all`（默认 `7d`） |

## 响应字段参考

### 响应信封——每个路由包装方式不同

在获取字段名之前，请检查信封。从错误级别读取字段名会返回
`undefined`，这会变成 `0`，这会读取为真实答案（“这个钱包什么都没赚”）而不是错误。

| 路由 | 顶层形状 | 行的位置 |
|-------|-----------------|--------------------|
| `portfolio stats` | 空对象（批量为数组） | 对象本身 |
| `portfolio profits` | `{"list": [ {…} ]}` | `list[0]` — 单个行，仍然在数组内 |
| `portfolio activity` | `{"activities": [...], "next": …}` | `activities` — **不是** `list` |
| `portfolio holdings` | `{"list": [...], "next": …}` | `list` — **不是** `holdings` |
| `portfolio created-tokens` | 空对象 | `tokens`，顶层还有汇总计数 |

某些部署还会将整个正文包装在 `{"data": …}` 中。

### `portfolio holdings` — 关键字段

行以 **`list`** 返回，带有 `next` 游标。与 gmgn-cli 1.5.8 活动响应进行确认——几个名称与本文档早期版本声称的不同，旧名称不再作为别名接受。

| 字段 | 描述 |
|-------|-------------|
| `token.token_address` | 代币合约地址（**不是** `token.address` — 该名称是 `activity` 的） |
| `token.symbol` / `token.name` | 代币代码和全名 |
| `token.price` | 当前代币价格（美元） |
| `token.is_honeypot` | 直接提供——不需要 `gmgn-token security` 调用。**如果此处为 `true`，则与同一行的 `history_total_sells > 0` 矛盾**：蜜罐不能出售，而限制转账的 RWA / 代币化股票合约会触发模拟器 |
| `token.launchpad_platform` / `token.launchpad` | 代币来自哪里——这是“这个钱包在哪里寻找”的基础 |
| `token.liquidity`, `token.max_supply`, `token.total_supply`, `token.creation_timestamp` | 也直接提供 |
| `balance` | 当前代币余额（人类可读单位） |
| `usd_value` | 此头寸的当前美元价值 |
| `accu_cost` | 仍持有的头寸的成本基础（**不是** `cost`） |
| `history_bought_cost` / `history_sold_income` | 对此代币的终身购买成本 / 出售收益 |
| `realized_profit` | 来自已完成卖出的利润（美元） |
| `unrealized_profit` | 当前未出售头寸按当前价格计算的账面收益（美元） |
| `total_profit` | `realized_profit + unrealized_profit`（美元） |
| `total_profit_pnl` | 总利润**比率**（**不是** `profit_change`）；`realized_profit_pnl` / `unrealized_profit_pnl` 是分割 |
| `history_total_buys` / `history_total_sells` | 购买 / 出售交易计数（**不是** `buy_tx_count` / `sell_tx_count`） |
| `history_total_transfer_ins` / `_outs` | 转账计数——空投和内部移动，不是交易 |
| `start_holding_at` / `end_holding_at` / `last_active_timestamp` | 头寸生命周期 |
| `wallet_token_tags` | 每个头寸的标签 |

没有 **`--sell-out` 标志**——gmgn-cli 1.5.8 拒绝它作为未知选项。`avg_cost` 没有返回；从 `accu_cost / balance` 推导。

### `portfolio activity` — 关键字段

行以 **`activities`** 返回，带有分页的 `next` 游标。

| 字段 | 描述 |
|-------|-------------|
| `tx_hash` | 链上交易哈希（**不是** `transaction_hash`） |
| `event_type` | 交易类型：`buy` / `sell` / `transferIn` / `transferOut`。某些链返回 `type` 而不是——读取 `event_type ?? type`。转账行是空投和内部移动，**不是交易**——从任何比率中排除它们 |
| `buy_cost_usd` | 在 `sell` 行中，已出售的成本基础——`cost_usd - buy_cost_usd` 是该卖出的实现盈亏 |
| `gas_usd` / `priority_fee` / `tip_fee` | 摩擦。比较 `gas_usd` 与每笔交易的净额，而不是与空值比较 |
| `launchpad_platform` | 代币来自哪里 |
| `token.address` | 代币合约地址 |
| `token.symbol` | 代币代码 |
| `token_amount` | 此交易的代币数量 |
| `cost_usd` | 此交易的美元价值 |
| `price` | 在交易对报价代币中按交易时计价的代币价格 |
| `price_usd` | 交易时代币的美元价格 |
| `timestamp` | 交易的 Unix 时间戳 |
| `next` | 分页游标——传递给 `--cursor` 以获取下一页 |

### `portfolio stats` — 关键字段

响应是一个对象（批量时为数组）。关键字段：

| 字段 | 描述 |
|-------|-------------|
| `realized_profit` | 期间总实现利润（美元） |
| `unrealized_profit` | 开放头寸的总未实现利润（美元） |
| `winrate` | 胜率——盈利交易的比率（0–1） |
| `total_cost` | 期间购买的总金额（美元） |
| `buy_count` | 购买交易数量 |
| `sell_count` | 出售交易数量 |
| `pnl` | 盈亏比率 = `realized_profit / total_cost` |

响应还包括一个 `common` 对象（如果上游身份服务不可用则不存在）：

| 字段 | 描述 |
|-------|-------------|
| `common.avatar` | 钱包头像 URL |
| `common.name` | 显示名称 |
| `common.ens` | ENS 域（仅限 EVM 链） |
| `common.tag` | 主要钱包标签 |
| `common.tags` | 所有钱包标签（例如 `["smart_money"]`） |
| `common.twitter_username` | Twitter 处理名 |
| `common.twitter_name` | Twitter 显示名称 |
| `common.followers_count` | Twitter 关注者数量 |
| `common.is_blue_verified` | Twitter 蓝色验证徽章 |
| `common.follow_count` | 关注此钱包的 GMGN 用户数量 |
| `common.remark_count` | 评论此钱包的 GMGN 用户数量 |
| `common.created_token_count` | 此钱包创建的代币数量 |
| `common.created_at` | 钱包创建时间（Unix 秒）——记录第一个资金交易到达的时间；将其用作钱包的年龄指标 |
| `common.fund_from` | 资金来源标签 |
| `common.fund_from_address` | 资助此钱包的地址 |
| `common.fund_amount` | 资助金额 |

使用 `common.tags` 和 `common.twitter_username` 构建钱包简介叙事。如果 `common` 在响应中不存在，则静默省略身份字段——不要报告它为错误。

### `portfolio profits` — 关键字段

响应有一个 `list` 数组，每个钱包一个项目。货币值是十进制字符串；在精确计算很重要时，使用十进制算术而不是二进制浮点数解析它们。

| 字段 | 描述 |
|-------|-------------|
| `wallet_address` | 钱包地址 |
| `realized_profit` | 选择周期内的实现利润 |
| `realized_profit_cost` | 与选择周期内实现利润相关的成本基础 |
| `buy` / `sell` | 选择周期内的购买/出售计数 |
| `unrealized_profit` | 当前持有头寸的未实现利润 |
| `total_realized_profit` | 所有时间的实现利润 |
| `total_realized_profit_cost` | 与所有时间实现利润相关的成本基础 |
| `total_profit` | 总利润 |
| `total_cost` | 总成本基础 |

### `portfolio created-tokens` — 关键字段

响应 `data` 对象有一个 `tokens` 数组加上汇总统计。

顶层字段：

| 字段 | 描述 |
|-------|-------------|
| `last_create_timestamp` | 最近创建代币的 Unix 时间戳 |
| `inner_count` | 仍在绑定曲线上（未毕业）的代币数量 |
| `open_count` | 已毕业到 DEX 的代币数量 |
| `open_ratio` | 毕业率（字符串，例如 `"0.25"`） |

> **总数 = `inner_count + open_count`**。**不要使用 `len(tokens)` 作为总数——`tokens` 数组最多 100 个条目，可能被截断。**
| `creator_ath_info` | 此钱包创建的最佳表现代币（ATH 市值） |
| `tokens` | 创建的代币数组——见下文 |

`creator_ath_info` 字段：

| 字段 | 描述 |
|-------|-------------|
| `creator` | 钱包地址 |
| `ath_token` | ATH 市值最高的代币地址 |
| `ath_mc` | ATH 市值（美元字符串） |
| `token_symbol` / `token_name` | 代币代码和名称 |
| `token_logo` | Logo URL |

每个代币字段 (`tokens[*]`)：

| 字段 | 描述 |
|-------|-------------|
| `token_address` | 代币合约地址 |
| `symbol` | 代币代码 |
| `chain` | 链名 |
| `create_timestamp` | 创建时间戳 |
| `is_open` | 如果已毕业到 DEX，则为 `true` |
| `market_cap` | 当前市值（美元字符串） |
| `token_ath_mc` | 所有时间最高市值（美元字符串） |
| `pool_liquidity` | 当前流动性（美元字符串） |
| `holders` | 当前持有人数量 |
| `swap_1h` | 最后 1 小时的交换次数 |
| `volume_1h` | 最后 1 小时的交易量（美元字符串） |
| `launchpad_platform` | 发售平台名称（例如 `Pump.fun`） |
| `is_pump` | 如果在 Pump.fun 上发售，则为 `true` |
| `bundler_rate` | Bundler 参与率（0–1） |
| `cto_flag` | 如果是社区接管代币，则为 `true` |

**不要猜测此处未列出的字段名称。** 如果响应中出现的字段在此表中不存在，则不要解释它，除非先阅读原始输出。
