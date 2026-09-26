在执行任何命令之前：运行 `gmgn-cli config --check`。如果退出码为 0，则正常继续。如果退出码为 1，(1) 运行 `gmgn-cli config` 并向用户展示输出； (2) 一旦用户发送 API 密钥，运行 `gmgn-cli config --apply <KEY>` 以完成配置和验证，然后向用户展示输出。如果 `--check` 返回错误（未知选项或命令未找到），告诉用户运行 `npm install -g gmgn-cli` 以更新，然后重试。

**重要提示：** 以下始终使用 `gmgn-cli` 命令。不要使用网络搜索、WebFetch、curl 或访问 gmgn.ai 来获取这些数据——该网站需要登录且不会返回结构化数据。CLI 是唯一正确的获取方法。

**重要提示：** 不要猜测字段名或值。当某个字段的含义不明确时，在使用它之前，先在下面的“响应字段”部分中查找。

**⚠️ 不支持 IPv6：** 如果你遇到 `401` 或 `403` 错误且凭证看起来正确，请立即检查 IPv6： (1) 列出所有网络接口及其 IPv6 地址——运行 `ifconfig | grep inet6`（macOS）或 `ip addr show | grep inet6`（Linux）； (2) 向 `https://ipv6.icanhazip.com` 发送测试请求——如果响应是 IPv6 地址，则出站流量是通过 IPv6 进行的。立即告诉用户：“请禁用您的网络接口上的 IPv6——gmgn-cli 命令仅在 IPv4 上工作。”

使用 `gmgn-cli` 工具查询代币的 K 线数据，浏览热门代币，或查看 Trenches 代币列表。

## 核心概念

- **`--filter` 链默认值** — SOL 和 EVM 链有不同的默认安全过滤器，当省略 `--filter` 时会自动应用。不要假设跨链的默认值相同：
  - **SOL**：默认为 `renounced frozen`（铸造和冻结授权已放弃）
  - **BSC / Base / ETH (EVM)**：默认为 `not_honeypot verified renounced`
  - 省略 `--filter` 并不等于“无过滤器”——链默认值始终会被应用。要使用自定义过滤器集，请显式指定所有所需的过滤器标签。

- **`volume` vs `amount` (kline)** — 命名具有反直觉性。`volume` = 交易美元价值；`amount` = 交易代币单位。对于价格为 $0.0002 的代币，这两者相差 5,000 倍。始终使用 `volume` 来表示“交易了多少美元”，使用 `amount` 来表示“有多少代币发生了交易”。

- **`rug_ratio`** — 0–1 分数，估计拉高出货的可能性。值高于 `0.3` 的风险较高。不要将其视为二元值——结合 `top_10_holder_rate`、`dev_team_hold_rate` 和 `is_honeypot` 来获得完整图景。

- **`smart_degen_count` / `renowned_count`** — 平台标记的聪明资金钱包（`smart_degen`）和 KOL 钱包（`renowned`）持有或交易此代币的数量。高值是看涨信号。这些是 GMGN 标记的钱包列表，不是用户定义的。

- **`hot_level`** — 趋势强度分数。越高 = 当前交易越活跃。未标准化——在同一结果集中比较相对值，而不是跨时间段比较。

- **`renounced_mint` / `renounced_freeze_account`** — SOL 特有。指示创建者是否放弃了铸造更多代币或冻结钱包的能力。两者都为 `1` 是 Solana 上的安全基准。在 EVM 链上始终为 `false`（此概念不适用）。

- **`is_honeypot`** — EVM 特有（BSC / Base）。指示代币合约是否阻止出售。在 SOL 上始终为空/空值——不要将空值解释为 Solana 上的“不是蜜罐”。

- **`creator_token_status`** — 开发者持有状态。`creator_hold` = 开发者仍持有代币（卖压风险）。`creator_close` = 开发者已出售或烧毁其配额（退出信号确认）。

- **`cto_flag`** — 社区接管标志。`1` = 原始开发者放弃了项目，社区团体接管了市场/开发。中等到积极信号；结合上下文评估。

- **Trenches 类别** — 发起平台代币的三个生命周期阶段：`new_creation`（刚创建，仍在锁仓曲线上）、`near_completion`（锁仓曲线几乎满，即将毕业）、`completed`（毕业到开放市场 / DEX）。在响应中，`near_completion` 始终在 `data.pump` 下返回，无论输入 `--type` 如何。

- **`wash_trading` / `rat_trader_amount_rate` / `bundler_rate`** — 人工活动的风险信号。`is_wash_trading` = 检测到协调的虚假交易量。`rat_trader_amount_rate` = 内部/偷袭交易比率。`bundler_rate` = 启动时机器人捆绑购买比率。高值（> 0.3）表明价格操纵。

## 子命令

| 子命令 | 描述 |
|-------------|-------------|
| `market kline` | 代币蜡烛图 / OHLCV 数据和一段时间内的交易量 |
| `market trending` | 按交换活动排名的热门代币——使用 `--interval` 指定时间段（例如 `1m` 为 1 分钟最热，`1h` 为 1 小时趋势） |
| `market trenches` | 新推出的发起平台代币——**当用户询问“新代币”、“刚推出代币”、“pump.fun/letsbonk 上的最新代币”时使用**。三个类别：`new_creation`（刚创建）、`near_completion`（锁仓曲线几乎满）、`completed`（毕业到开放市场 / DEX） |
| `market signal` | 实时代币信号源——价格飙升、聪明资金购买、大额购买、DEX 广告、CTO 事件等。结果按 `trigger_at` 降序排序。**sol / bsc / robinhood / arc / stable 仅限。每组最多 50 个结果。** |
| `market hot-searches` | 热搜索排名——最受欢迎的代币，按 `visiting_count`（搜索热度）排名。**当用户询问“人们在搜索哪些代币”、“最受欢迎的代币”、“热搜索列表”、“热搜榜”时使用**。支持在单个请求中查询多个链。 |
| `market search` | 通过名称、符号、合约地址、钱包地址或 ENS 查找**特定**代币或钱包。返回匹配的代币（`coins`）和钱包（`wallets`）。**当用户命名代币/钱包并希望找到它时使用——例如“搜索 PEPE”、“查找此地址”、“找到 vitalik.eth”、“查一下这个代币/钱包”**——而不是浏览排名（`trending` / `hot-searches`）。 |

## 支持的链

`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable`（kline / trending / trenches / hot-searches；signal：`sol` / `bsc` / `robinhood` / `arc` / `stable`；search：`--chain` 是**可选**的——省略以搜索所有链；接受 `all` 和任何搜索模块已启用的链，包括动态启用的链，如 `tron` / `monad` / `megaeth` / `xlayer`）

## 前置条件

- 全局安装 `gmgn-cli`——如果缺失，运行：`npm install -g gmgn-cli`
- 在 `~/.config/gmgn/.env` 中配置 `GMGN_API_KEY`

## 速率限制处理

此技能使用的所有标准市场路由使用 GMGN 的基于计划的漏桶：免费 `5/5`，Plus `20/20`，Pro `50/50`（速率/容量）。持续吞吐量约为 `等级速率 ÷ 权重` 请求/秒，最大突发量约为 `等级容量 ÷ 权重`。Pro 仅有的 `1s` K 线路由使用 Pro API 密钥桶及其单独的共享全局桶。

| 命令 | 路由 | 权重 |
|---------|-------|--------|
| `market kline`（标准分辨率） | `GET /v1/market/token_kline` | 2 |
| `market kline --resolution 1s`（**Pro 仅限**） | `GET /v1/market/token_kline` | 3 对 Pro API 密钥桶；共享全局限制：500 req/s |
| `market trending` | `GET /v1/market/rank` | 3 |
| `market trenches` | `POST /v1/trenches` | 2 |
| `market signal` | `POST /v1/market/token_signal` | 1 |
| `market hot-searches` | `POST /v1/market/hot_searches` | 3 |
| `market search` | `GET /v1/market/search` | 1 |

当请求返回 `429` 时：

- 在 `RATE_LIMIT_EXCEEDED`，准确告诉用户：`已达到当前套餐的限频上限，点击 https://gmgn.ai/ai?chain=bsc&tab=paid_plans 升级套餐，获得更高速率限制`。在每个用户任务中最多显示一次此升级指南。不要在同一冷却期间对后续的 `RATE_LIMIT_BANNED` 响应重复它。

- 从响应头中读取 `X-RateLimit-Reset`。它是一个 Unix 时间戳（秒），标记限制何时预期重置。
- 如果响应正文包含 `reset_at`（例如 `{"code":429,"error":"RATE_LIMIT_BANNED","message":"...","reset_at":1775184222}`），提取 `reset_at`——它是禁令解除的 Unix 时间戳（通常为 5 分钟）。转换为本地时间并准确告诉用户何时可以重试。
- CLI 可能会等待并自动重试一次，当剩余冷却时间较短时。如果仍然失败，停止并告诉用户确切的重试时间，而不是发送更多请求。
- 对于 `RATE_LIMIT_EXCEEDED` 或 `RATE_LIMIT_BANNED`，在冷却期间重复请求可以每次将禁令延长 5 秒，最多 5 分钟。不要疯狂重试。

## `market kline` 参数

| 参数 | 必填 | 描述 |
|-----------|----------|-------------|
| `--chain` | 是 | `sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--address` | 是 | 代币合约地址 |
| `--resolution` | 是 | 蜡烛图分辨率：`1s`（**Pro 仅限；最多每请求 500 根蜡烛**）/ `30s` / `1m` / `5m` / `15m` / `1h` / `4h` / `1d` |
| `--from` | 否 | 开始时间（Unix 秒） |
| `--to` | 否 | 结束时间（Unix 秒） |

## `market kline` 响应字段

响应是一个对象，其中包含一个 `list` 数组。`list` 中的每个元素是一个蜡烛图：

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `time` | number | 蜡烛开盘时间——Unix 时间戳（秒） |
| `open` | string | 期间开始时的美元开盘价 |
| `close` | string | 期间结束时的美元收盘价 |
| `high` | string | 期间内的最高美元价 |
| `low` | string | 期间内的最低美元价 |
| `volume` | string | 交易量（基础代币单位）（交易代币数量） |
| `amount` | string | 交易量（美元）（此期间所有交易的美元价值） |

**重要区别（命名具有反直觉性——不要猜测）：**
- `volume` = 代币数量（例如 `5379110` 表示 ~5.38M 代币发生了交易）
- `amount` = 美元价值（例如 `1214` 表示 ~$1,214 交易）——用于“多少美元交易”
- 对于价格不为 $1 的代币，`volume` 和 `amount` 将相差几个数量级（例如 $1,214 金额 = 5,379,110 代币，对于 $0.0002 的代币）
- 要获得**一段时间内的总美元交易量**，请跨范围内的所有蜡烛求和 `amount`
- 要获得**价格趋势**，按时间顺序（`time` 升序）读取 `close` 值
- 要检测**波动性**，比较每个蜡烛内的 `high` vs `low`
- 蜡烛按时间顺序返回（最旧的首先）

## `market trending` 选项

**`--interval` 选择指南——始终与用户声明的时间窗口匹配：**

| 用户说 | `--interval` |
|-----------|-------------|
| "1m trending" / "hottest right now" | `1m` |
| "5m" / "5 minute" | `5m` |
| "1h" / "1 hour" / 未指定时间（默认） | `1h` |
| "6h" / "6 hour" | `6h` |
| "24h" / "today" / "daily" | `24h` |

| 选项 | 描述 |
|--------|-------------|
| `--chain` | 必需。`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--interval` | 必需。`1m` / `5m` / `1h` / `6h` / `24h`（默认 `1h`） |
| `--limit <n>` | 结果数量（默认 100，最大 100） |
| `--order-by <field>` | 排序字段：`default` / `swaps` / `marketcap` / `history_highest_market_cap` / `liquidity` / `volume` / `holder_count` / `smart_degen_count` / `renowned_count` / `gas_fee` / `price` / `change1m` / `change5m` / `change1h` / `creation_timestamp` |
| `--direction <asc\|desc>` | 排序方向（默认 `desc`） |
| `--filter <tag...>` | 可重复的过滤器标签（链特定）。**⚠️ SOL 默认：`renounced frozen`；BSC/Base/ETH 默认：`not_honeypot verified renounced`。省略 `--filter` 并不等于“无过滤器”——链默认值始终会被应用。** **sol** 标签：`renounced` / `frozen` / `burn` / `token_burnt` / `has_social` / `not_social_dup` / `not_image_dup` / `dexscr_update_link` / `not_wash_trading` / `is_internal_market` / `is_out_market`。**evm** 标签：`not_honeypot` / `verified` / `renounced` / `locked` / `token_burnt` / `has_social` / `not_social_dup` / `not_image_dup` / `dexscr_update_link` / `is_internal_market` / `is_out_market` |
| `--platform <name...>` | 可重复的平台过滤器（链特定）。**sol**：`Pump.fun` / `pump_mayhem` / `pump_mayhem_agent` / `pump_agent` / `letsbonk` / `bonkers` / `bags` / `memoo` / `liquid` / `bankr` / `zora` / `surge` / `anoncoin` / `moonshot_app` / `wendotdev` / `heaven` / `sugar` / `token_mill` / `believe` / `trendsfun` / `trends_fun` / `jup_studio` / `Moonshot` / `boop` / `xstocks` / `ray_launchpad` / `meteora_virtual_curve` / `pool_ray` / `pool_meteora` / `pool_pump_amm` / `pool_orca`。**bsc**：`fourmeme` / `fourmeme_agent` / `bn_fourmeme` / `four_xmode_agent` / `cubepeg` / `likwid` / `goplus_creator` / `goplus_skills` / `openfour` / `flap` / `flap_stocks` / `flap_aioracle` / `clanker` / `lunafun` / `pool_uniswap` / `pool_pancake`。**base**：`clanker` / `bankr` / `flaunch` / `zora` / `zora_creator` / `baseapp` / `basememe` / `virtuals_v2` / `klik`。**eth**：`trench` / `clanker` / `klik` / `livo` / `stroid` / `pool_uniswap_v2` / `pool_uniswap_v3` / `printr` |

### `market trending` 范围过滤器

可选的 `--min-*` / `--max-*` 标志应用服务器端数值范围过滤（包含）。服务忽略未知指标。

| 选项 | 描述 |
|--------|-------------|
| `--min-volume` / `--max-volume` | 交易量（美元） |
| `--min-liquidity` / `--max-liquidity` | 流动性（美元） |
| `--min-marketcap` / `--max-marketcap` | 市值（美元） |
| `--min-history-highest-marketcap` / `--max-history-highest-marketcap` | 历史最高市值（美元） |
| `--min-swaps` / `--max-swaps` | 交换次数 |
| `--min-holder-count` / `--max-holder-count` | 持有者数量 |
| `--min-gas-fee` / `--max-gas-fee` | 燃气费 |
| `--min-renowned-count` / `--max-renowned-count` | KOL / 著名钱包数量 |
| `--min-smart-degen-count` / `--max-smart-degen-count` | 智能资金持有者数量 |
| `--min-bot-degen-count` / `--max-bot-degen-count` | 机器人钱包数量 |
| `--min-visiting-count` / `--max-visiting-count` | 访问者数量 |
| `--min-price-change-percent` / `--max-price-change-percent` | 时间段内的价格变化比率 |
| `--min-insider-rate` / `--max-insider-rate` | 内部交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-bundler-rate` / `--max-bundler-rate` | 捆绑机器人交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-entrapment-ratio` / `--max-entrapment-ratio` | 诱捕交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-top10-holder-rate` / `--max-top10-holder-rate` | 顶部 10 持有者集中度（0–1） |
| `--min-top70-sniper-hold-rate` / `--max-top70-sniper-hold-rate` | 顶部 70 枪手持有比率（0–1） |
| `--min-dev-team-hold-rate` / `--max-dev-team-hold-rate` | 开发者持有比率（0–1）；`--min-dev-team-hold-rate` 也排除 `creator-close` 代币 |
| `--min-created` / `--max-created` | 代币年龄窗口，持续时间字符串带有 `m`（分钟）/ `h`（小时）/ `d`（天）后缀，例如 `30m` / `6h` / `7d`。`--min-created` 是最小年龄（排除较新的代币）；`--max-created` 是最大年龄（排除较旧的代币）。**注意**：原始上游排名接口仅接受分钟；openapi-service 不转发此字段——它自己评估年龄窗口（截止日期 = 现在 - 持续时间，原生计算 `m`/`h`/`d`），因此 `6h` / `7d` 在这里有效。始终包含单位后缀——裸数字**不**被接受。 |

## 使用示例

### Kline

`1s` 仅限 Pro API 密钥可用。保持请求范围在 500 秒或更短，因为 1 秒请求最多返回 500 根蜡烛。免费和 Plus 密钥会收到 `403 PRO_PLAN_REQUIRED`；不要重试相同的密钥。如果安装的 CLI 拒绝 `1s`，请在重试前更新它；不要静默回退到更粗糙的分辨率。

```bash
# 最后 500 秒的 1 秒 K线图（专业版；macOS）
gmgn-cli market kline \
  --chain sol \
  --address <token_address> \
  --resolution 1s \
  --from $(date -v-500S +%s) \
  --to $(date +%s)

# 最后 1 小时的 1 分钟 K线图
# macOS:
gmgn-cli market kline \
  --chain sol \
  --address <token_address> \
  --resolution 1m \
  --from $(date -v-1H +%s) \
  --to $(date +%s)
# Linux: 使用 $(date -d '1 hour ago' +%s) 而不是 $(date -v-1H +%s)

# 最后 24 小时的 1 小时 K线图
# macOS:
gmgn-cli market kline \
  --chain sol \
  --address <token_address> \
  --resolution 1h \
  --from $(date -v-24H +%s) \
  --to $(date +%s)
# Linux: 使用 $(date -d '24 hours ago' +%s) 而不是 $(date -v-24H +%s)

# 原始输出以供进一步处理
gmgn-cli market kline --chain sol --address <addr> \
  --resolution 5m --from <ts> --to <ts> --raw | jq '.[]'

# ETH 代币 K线图 — 最后 24 小时，1 小时 K线图（macOS）
gmgn-cli market kline \
  --chain eth \
  --address 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 \
  --resolution 1h \
  --from $(date -v-24H +%s) \
  --to $(date +%s)
```

### 热门趋势 — 普通版

```bash
# SOL 上过去 1 小时排名前 20 的热门代币，按交易量排序
gmgn-cli market trending --chain sol --interval 1h --order-by volume --limit 20

# SOL 上排名前 50 的代币，5 分钟窗口，按交易量排序
gmgn-cli market trending --chain sol --interval 5m --order-by volume --limit 50

# BSC 上仅带社交链接的热门代币，已验证且非蜜罐，超过 24 小时
gmgn-cli market trending \
  --chain bsc --interval 24h \
  --filter has_social --filter not_honeypot --filter verified
```

### 热门趋势 — SOL 通过启动平台

使用 `--platform` 参数仅筛选来自特定启动平台的趋势结果。

```bash
# SOL 1 分钟最热门 — Pump.fun + letsbonk 仅（最活跃的启动平台），按交易量排序
gmgn-cli market trending \
  --chain sol --interval 1m \
  --platform Pump.fun --platform letsbonk \
  --order-by volume --limit 50 --raw

# SOL 5 分钟最热门 — Pump.fun + letsbonk + Moonshot，按交易量排序
gmgn-cli market trending \
  --chain sol --interval 5m \
  --platform Pump.fun --platform letsbonk --platform moonshot_app \
  --order-by volume --limit 50 --raw

# SOL 1 小时趋势 — Pump.fun 仅，带安全筛选
gmgn-cli market trending \
  --chain sol --interval 1h \
  --platform Pump.fun \
  --filter renounced --filter frozen --filter not_wash_trading \
  --order-by volume --limit 20 --raw

# SOL 1 小时趋势 — 所有主要启动平台合并
gmgn-cli market trending \
  --chain sol --interval 1h \
  --platform Pump.fun --platform letsbonk --platform moonshot_app \
  --platform pump_mayhem --platform pump_mayhem_agent --platform bonkers \
  --order-by volume --limit 50 --raw
```

### 热门趋势 — BSC 通过启动平台

```bash
# BSC 1 分钟最热门 — fourmeme（主 BSC 启动平台），按交易量排序
gmgn-cli market trending \
  --chain bsc --interval 1m \
  --platform fourmeme --platform four_xmode_agent \
  --order-by volume --limit 50 --raw

# BSC 5 分钟最热门 — 所有 BSC 启动平台，按交易量排序
gmgn-cli market trending \
  --chain bsc --interval 5m \
  --platform fourmeme --platform fourmeme_agent --platform bn_fourmeme --platform four_xmode_agent \
  --platform cubepeg --platform likwid --platform goplus_creator --platform goplus_skills --platform openfour \
  --platform flap --platform flap_stocks --platform flap_aioracle --platform clanker --platform lunafun \
  --order-by volume --limit 50 --raw

# BSC 1 小时趋势 — 所有 BSC 启动平台带安全筛选
gmgn-cli market trending \
  --chain bsc --interval 1h \
  --platform fourmeme --platform fourmeme_agent --platform bn_fourmeme --platform four_xmode_agent \
  --platform cubepeg --platform likwid --platform goplus_creator --platform goplus_skills --platform openfour \
  --platform flap --platform flap_stocks --platform flap_aioracle --platform clanker --platform lunafun \
  --filter not_honeypot --filter verified \
  --order-by volume --limit 20 --raw
```

### 热门趋势 — ETH 通过启动平台

```bash
# ETH 1 小时趋势 — 所有平台，按交易量排序
gmgn-cli market trending --chain eth --interval 1h --order-by volume --limit 20

# ETH 1 小时趋势 — 仅特定平台
gmgn-cli market trending \
  --chain eth --interval 1h \
  --platform trench --platform clanker --platform klik \
  --order-by volume --limit 50 --raw

# ETH 1 小时趋势 — 所有 ETH 平台带安全筛选
gmgn-cli market trending \
  --chain eth --interval 1h \
  --platform trench --platform clanker --platform klik --platform livo --platform stroid \
  --platform pool_uniswap_v2 --platform pool_uniswap_v3 --platform printr \
  --filter not_honeypot --filter verified \
  --order-by volume --limit 20 --raw

# ETH 24 小时趋势 — 按智能资金数量排序
gmgn-cli market trending \
  --chain eth --interval 24h \
  --filter not_honeypot --filter verified \
  --order-by smart_degen_count --limit 20 --raw
```

### 热门趋势 — 数值范围筛选

```bash
# SOL 1 小时趋势 — 流动性 10k–1M，市值超过 50k，按交易量排序
gmgn-cli market trending \
  --chain sol --interval 1h \
  --min-liquidity 10000 --max-liquidity 1000000 --min-marketcap 50000 \
  --order-by volume --limit 30 --raw

# SOL 5 分钟最热门 — 新代币（30 分钟以内）带智能资金兴趣
gmgn-cli market trending \
  --chain sol --interval 5m \
  --max-created 30m --min-smart-degen-count 1 \
  --order-by volume --limit 50 --raw

# SOL 1 小时趋势 — 排除高内部人/高捆绑代币
gmgn-cli market trending \
  --chain sol --interval 1h \
  --max-insider-rate 0.3 --max-bundler-rate 0.3 \
  --order-by volume --limit 20 --raw
```

### 热门趋势 — Base 通过启动平台

```bash
# Base 1 分钟最热门 — clanker + zora（主 Base 启动平台），按交易量排序
gmgn-cli market trending \
  --chain base --interval 1m \
  --platform clanker --platform zora --platform zora_creator \
  --order-by volume --limit 50 --raw

# Base 5 分钟最热门 — clanker + zora + virtuals_v2 + flaunch，按交易量排序
gmgn-cli market trending \
  --chain base --interval 5m \
  --platform clanker --platform zora --platform zora_creator \
  --platform virtuals_v2 --platform flaunch \
  --order-by volume --limit 50 --raw

# Base 1 小时趋势 — 所有主要启动平台带安全筛选
gmgn-cli market trending \
  --chain base --interval 1h \
  --platform clanker --platform zora --platform zora_creator \
  --platform virtuals_v2 --platform flaunch --platform baseapp \
  --filter not_honeypot --filter verified \
  --order-by volume --limit 20 --raw
```

## `market trending` 响应字段

响应是 `data.rank` — 一个排名项数组。每个项代表一个代币。

**基本信息**

| 字段 | 描述 |
|-------|-------------|
| `address` | 代币合约地址 |
| `symbol` / `name` | 代币代码和全名 |
| `logo` | 代币标志图片 URL |
| `chain` | 链标识符 |
| `total_supply` | 总代币供应量 |
| `creator` | 创建者钱包地址 |
| `launchpad_platform` | 启动/池平台（例如 `Pump.fun`, `letsbonk`, `pool_meteora`, `fourmeme`) |
| `exchange` | 当前 DEX（例如 `meteora_damm_v2`, `raydium`, `pump_amm`) |
| `open_timestamp` | 开放市场上市时间（Unix 秒） |
| `creation_timestamp` | 代币创建时间（Unix 秒） |
| `rank` | 此趋势列表中的位置（越低越热） |
| `hot_level` | 趋势强度级别（越高越热） |

**价格 & 市场**

| 字段 | 描述 |
|-------|-------------|
| `price` | 当前价格（美元） |
| `market_cap` | 市值（美元）（直接可用 — 无需计算） |
| `liquidity` | 当前流动性（美元） |
| `volume` | 查询间隔内的交易量（美元） |
| `history_highest_market_cap` | 历史最高市值（美元） |
| `initial_liquidity` | 代币上市时的初始流动性 |
| `price_change_percent` | 查询间隔内的价格变化百分比 |
| `price_change_percent1m` | 最后 1 分钟的价格变化百分比 |
| `price_change_percent5m` | 最后 5 分钟的价格变化百分比 |
| `price_change_percent1h` | 最后 1 小时的价格变化百分比 |

**交易活动**

| 字段 | 描述 |
|-------|-------------|
| `swaps` | 查询间隔内的总交易次数 |
| `buys` / `sells` | 间隔内的买入/卖出次数 |
| `holder_count` | 独特代币持有者数量 |
| `gas_fee` | 每笔交易的平均 gas 费用 |

**安全 & 风险**

| 字段 | 链 | 描述 |
|-------|--------|-------------|
| `renounced_mint` | SOL | 锁定授权已放弃（`1` = 是，`0` = 否） |
| `renounced_freeze_account` | SOL | 冻结授权已放弃（`1` = 是，`0` = 否） |
| `is_honeypot` | BSC / Base | 蜜罐标志（`1` = 是，`0` = 否） |
| `is_open_source` | all | 合约已验证（`1` = 是，`0` = 否） |
| `is_renounced` | all | 所有权已放弃（`1` = 是，`0` = 否） |
| `buy_tax` / `sell_tax` | all | 税率 — 空字符串表示 `0`（无税） |
| `burn_status` | all | 流动性燃烧状态（例如 `"none"`, `"burn"`) |
| `top_10_holder_rate` | all | 前 10 个钱包集中度（0–1） |
| `rug_ratio` | all | 拉高风险评分（0–1） |
| `is_wash_trading` | all | 洗售交易检测（`true` / `false`） |
| `rat_trader_amount_rate` | all | 内部人/偷袭交易量占比 |
| `bundler_rate` | all | 捆绑机器人交易量占比 |
| `entrapment_ratio` | all | 诱捕交易比率 |
| `sniper_count` | all | 启动时狙击钱包数量 |
| `bot_degen_count` / `bot_degen_rate` | all | 机器人退化钱包数量/比率 |
| `dev_team_hold_rate` | all | 开发团队持有比率 |
| `top70_sniper_hold_rate` | all | 前 70 个狙击手当前持有比率 |
| `lock_percent` | all | 流动性锁定百分比 |

**开发状态**

| 字段 | 描述 |
|-------|-------------|
| `creator_token_status` | 开发者持有状态：`creator_hold`（仍持有）/ `creator_close`（已卖出/关闭） |
| `creator_close` | `creator_token_status == creator_close` 的布尔简写 |
| `dev_token_burn_ratio` | 开发者已燃烧代币的比率 |

**智能资金**

| 字段 | 描述 |
|-------|-------------|
| `smart_degen_count` | 持有该代币的智能资金钱包数量 |
| `renowned_count` | 持有该代币的知名/KOL 钱包数量 |
| `bluechip_owner_percentage` | 持有者中蓝筹钱包的比率（0–1） |

**社交**

| 字段 | 描述 |
|-------|-------------|
| `twitter_username` | Twitter / X 用户名（不是完整 URL — 在前面添加 `https://x.com/` 获取链接） |
| `website` | 项目网站 URL |
| `telegram` | Telegram URL |
| `cto_flag` | 社区接管标志（`1` = CTO 已发生） |

**Dexscreener 营销**

| 字段 | 描述 |
|-------|-------------|
| `dexscr_ad` | Dexscreener 广告已放置（`1` = 是） |
| `dexscr_update_link` | Dexscreener 上的社交链接已更新（`1` = 是） |
| `dexscr_trending_bar` | 已为 Dexscreener 趋势条付费（`1` = 是） |
| `dexscr_boost_fee` | Dexscreener 加速金额（0 = 无） |

---

## 工作流程：通过热门趋势发现交易机会

发现市场机会的完整工作流程：[`docs/workflow-market-opportunities.md`](../../docs/workflow-market-opportunities.md)

步骤：获取热门趋势（50 个结果，安全筛选）→ AI 多因素分析（智能资金、交易量、动量、流动性、成熟度）→ 展示前 5 个表格并说明理由 → 提供深入分析或交易。

当结果包含有趣的代币时，进行完整代币尽职调查：[`docs/workflow-token-research.md`](../../docs/workflow-token-research.md)

**对于新/启动平台代币** (`market trenches`)：应用结构化的早期项目筛选工作流程，包括安全检查和智能资金进入检测 — [`docs/workflow-early-project-screening.md`](../../docs/workflow-early-project-screening.md)

**对于每日市场概览**（用户问“今天市场怎么样”，“给我一个每日简报”，“今天智能资金在买什么”）：结合 `market trending` + `market trenches` 与 `gmgn-track smartmoney` — [`docs/workflow-daily-brief.md`](../../docs/workflow-daily-brief.md)

## 代币质量筛选标准

在评估从 `market trending` 或 `market trenches` 返回的代币时，应用这些标准以快速区分高质量机会和噪音。不要在没有筛选的情况下展示原始结果。

### 通过/观察/跳过标准

| 信号 | 🟢 通过 | 🟡 观察 | 🔴 跳过 |
|--------|---------|---------|---------|
| `smart_degen_count` | ≥ 3 | 1–2 | 0 |
| `rug_ratio` | < 0.1 | 0.1–0.3 | > 0.3 |
| `creator_token_status` | `creator_close` | — | `creator_hold` |
| `is_wash_trading` | `false` | — | `true` → 立即跳过 |
| `top_10_holder_rate` | < 0.20 | 0.20–0.50 | > 0.50 |
| `liquidity` | > $50k | $10k–$50k | < $10k |
| `has_social`（或任何社交字段存在） | 是 | — | 否（仅弱信号） |

**快速排除规则**：如果 `rug_ratio > 0.3` OR `is_wash_trading = true` OR `is_honeypot = 1` → 立即跳过，无需进一步分析。

**强烈买入信号组合**：`smart_degen_count ≥ 3` + `rug_ratio < 0.2` + `creator_close` + `is_wash_trading = false` + `liquidity > $50k` → 高质量机会，进行完整代币研究。

对于这里出现的任何代币的完整尽职调查：[`docs/workflow-token-research.md`](../../docs/workflow-token-research.md)

## 代币生命周期阶段

使用字段组合来确定代币处于哪个阶段。这会影响信号的解释方式。

### 阶段 1 — 早期（新出生）

**指标**：
- `creation_timestamp` < 1 小时前
- `hot_level` 低或刚开始上升
- `smart_degen_count = 0`, `renowned_count = 0`

**解释**：太早，智能资金信号无效。无链上记录。高风险，高潜在回报。**在进入阶段 2 确认之前等待。** 只有最能承受风险的交易者会进入这里。

### 阶段 2 — 爆发

**指标**：
- `smart_degen_count ≥ 3` AND 上升
- 交易量激增（比较 `swaps_1h` vs `swaps_24h / 24` — 显著更高）
- `price_change_percent1h > 20%`
- `creator_token_status = creator_hold` 在此阶段可以接受（开发人员尚未分配）

**解释**：最强进入信号。智能资金正在积累。在行动前验证安全。这个窗口通常很短 — 基于确认而非预期采取行动。

### 阶段 3 — 分配

**指标**：
- `creator_token_status = creator_close`（开发人员已出售其配额）
- `renowned_count` 购买（后期社交信号 — KOL 通常在智能资金之后进入）
- `smart_degen_count` 达到平台期或下降
- 交易量仍然很高但动量放缓

**解释**：后期进入。智能资金可能正在退出以进入零售/KOL 需求。对新进入者风险较高。如果从阶段 2 持有，评估退出水平。

### 阶段 4 — 下降

**指标**：
- 所有窗口的交易量下降
- `holder_count` 下降
- `rat_trader_amount_rate` 高（内部人/偷袭交易主导）
- `smart_degen_count = 0` 或明显下降

**解释**：完全避免新进入。如果仍持有，考虑退出。机会可能已经过去。

## `market trenches` 参数

**意图 → `--type` 映射（始终明确指定 `--type`）：**

| 用户意图 | `--type` 值 |
|-------------|----------------|
| "新代币", "刚刚启动", "新创建", "最新代币" | `new_creation` |
| "即将毕业", "接近完成", "绑定曲线几乎满" | `near_completion` |
| "已毕业代币", "已在 DEX 上", "开放市场代币" | `completed` |
| 未提及特定阶段 | 不指定 `--type`（返回所有三个） |

| 参数 | 是否必需 | 描述 |
|-------|----------|-------------|
| `--chain` | 是 | `sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--type` | 否 | 查询类别，可重复：`new_creation` / `near_completion` / `completed` (默认：全部三个) |
| `--launchpad-platform` | 否 | 启动平台过滤器，可重复。省略：sol/bsc/base/eth/robinhood 使用服务器的固定默认允许列表；arc/stable 应用无平台过滤器。传递值将替换该默认值。 |
| `--limit` | 否 | 每个类别的最大结果数，最大 80 (默认：80) |
| `--filter-preset` | 否 | 命名服务器端过滤器预设：`safe` / `smart-money` / `strict` |
| `--sort-by` | 否 | 客户端按类别排序：`smart_degen_count` / `renowned_count` / `volume_24h` / `volume_1h` / `swaps_24h` / `swaps_1h` / `rug_ratio` / `holder_count` / `usd_market_cap` / `created_timestamp` |
| `--direction` | 否 | 排序方向：`asc` / `desc` (默认：`desc`; `asc` 用于 `rug_ratio`) |
| `--min-*` / `--max-*` | 否 | 服务器端过滤器范围标志 — 见下方过滤器字段参考 |

**`--launchpad-platform` 值按链** (在 sol/bsc/base/eth/robinhood 上，省略标志使用服务器默认允许列表而不是所有平台):

| 链 | 平台 |
|-------|-----------|
| `sol`  | `Pump.fun` / `pump_mayhem` / `pump_mayhem_agent` / `pump_agent` / `letsbonk` / `bonkers` / `bags` / `memoo` / `liquid` / `bankr` / `zora` / `surge` / `anoncoin` / `moonshot_app` / `wendotdev` / `heaven` / `sugar` / `token_mill` / `believe` / `trendsfun` / `trends_fun` / `jup_studio` / `Moonshot` / `boop` / `ray_launchpad` / `meteora_virtual_curve` / `xstocks` |
| `bsc`  | `fourmeme` / `fourmeme_agent` / `bn_fourmeme` / `four_xmode_agent` / `cubepeg` / `likwid` / `goplus_creator` / `goplus_skills` / `openfour` / `flap` / `flap_stocks` / `flap_aioracle` / `clanker` / `lunafun` |
| `base` | `clanker` / `bankr` / `flaunch` / `zora` / `zora_creator` / `baseapp` / `basememe` / `virtuals_v2` / `klik` |
| `eth`  | `trench` / `clanker` / `klik` / `livo` / `stroid` / `pool_uniswap_v2` / `pool_uniswap_v3` / `printr` |
| `arc`  | `dyorfun_v3` / `dyorswap` / `trench` / `onmifun` / `sharcfun` / `klik` |
| `stable` | `dyorfun_v3` / `dyorswap` / `trench` |

### 过滤器预设

预设在服务器端应用：API 在返回结果前过滤代币。

| 预设 | 应用服务器端过滤器 |
|--------|----------------------------|
| `safe` | `max_rug_ratio=0.3` + `max_bundler_rate=0.3` + `max_insider_ratio=0.3` |
| `smart-money` | `min_smart_degen_count=1` |
| `strict` | `max_rug_ratio=0.3` + `max_bundler_rate=0.3` + `max_insider_ratio=0.3` + `min_smart_degen_count=1` + `min_volume_24h=1000` |

**预设 + 显式标志交互**：显式过滤标志始终覆盖预设值。例如，`--filter-preset safe --max-rug-ratio 0.1` 应用 `safe` 预设，但覆盖 rug_ratio 阈值为 `0.1`。

**所有过滤标志作为 API 请求体的一部分发送（服务器端）** — 服务器在返回结果前过滤代币。使用 `--limit 80`（默认最大值）以最大化池。

响应字段：`data.new_creation`，`data.pump`，`data.completed` — 每个都是一个 `RankItem` 数组（与 `market trending` 排名项字段相同）。**重要：** 响应中的 `data.pump` 对应请求中的 `--type near_completion`。API 始终以 `pump` 键返回此类别，而不是 `near_completion`。

### 服务器端过滤字段

所有过滤标志作为 API 请求体的一部分发送 — 服务器在返回结果前过滤代币。标志遵循命名约定 `--min-{field}` / `--max-{field}`。

| 标志对 | 类型 | 描述 |
|-----------|------|-------------|
| `--min-volume-24h` / `--max-volume-24h` | float | 24h 交易量 (USD) |
| `--min-net-buy-24h` / `--max-net-buy-24h` | float | 24h 净买入量 (USD) |
| `--min-swaps-24h` / `--max-swaps-24h` | int | 24h 总交换次数 |
| `--min-buys-24h` / `--max-buys-24h` | int | 24h 买入次数 |
| `--min-sells-24h` / `--max-sells-24h` | int | 24h 卖出次数 |
| `--min-visiting-count` / `--max-visiting-count` | int | 访客数量 |
| `--min-progress` / `--max-progress` | float | 锚定曲线进度 (0–1) |
| `--min-marketcap` / `--max-marketcap` | float | 市值 (USD) |
| `--min-liquidity` / `--max-liquidity` | float | 流动性 (USD) |
| `--min-created` / `--max-created` | duration | 代币年龄 — 建议使用单位后缀：秒 (`30s`，`10s`) 或分钟 (`0.5m`，`1m`，`5m`，`30m`)。裸数字（例如 `5`）被视为分钟，并带警告。 |
| `--min-holder-count` / `--max-holder-count` | int | 持有者数量 |
| `--min-top-holder-rate` / `--max-top-holder-rate` | float | 顶部 10 持有者集中度 (0–1) |
| `--min-rug-ratio` / `--max-rug-ratio` | float | 拉高风险评分 (0–1) |
| `--min-bundler-rate` / `--max-bundler-rate` | float | 包裹机器人交易比率 (0–1) |
| `--min-insider-ratio` / `--max-insider-ratio` | float | 内部人交易比率 (0–1) |
| `--min-entrapment-ratio` / `--max-entrapment-ratio` | float | 诱捕/钓鱼交易比率 (0–1) |
| `--min-private-vault-hold-rate` / `--max-private-vault-hold-rate` | float | 私有金库持有比率 (0–1) |
| `--min-top70-sniper-hold-rate` / `--max-top70-sniper-hold-rate` | float | 顶部 70 枪手持有比率 (0–1) |
| `--min-bot-count` / `--max-bot-count` | int | 机器人钱包数量 |
| `--min-bot-degen-rate` / `--max-bot-degen-rate` | float | 机器人去中心化钱包比率 (0–1) |
| `--min-fresh-wallet-rate` / `--max-fresh-wallet-rate` | float | 新钱包比率 (0–1) |
| `--min-total-fee` / `--max-total-fee` | float | 总费用 |
| `--min-smart-degen-count` / `--max-smart-degen-count` | int | 智能资金持有者数量 |
| `--min-renowned-count` / `--max-renowned-count` | int | KOL / 著名钱包数量 |
| `--min-creator-balance-rate` / `--max-creator-balance-rate` | float | 创作者持有比率 (0–1) |
| `--min-creator-created-count` / `--max-creator-created-count` | int | 创作者总代币创建数量 |
| `--min-creator-created-open-count` / `--max-creator-created-open-count` | int | 创作者毕业代币数量 |
| `--min-creator-created-open-ratio` / `--max-creator-created-open-ratio` | float | 创作者毕业比率 (0–1) |
| `--min-x-follower` / `--max-x-follower` | int | Twitter / X 关注者数量 |
| `--min-twitter-rename-count` / `--max-twitter-rename-count` | int | Twitter 重命名次数 |
| `--min-tg-call-count` / `--max-tg-call-count` | int | Telegram 调用次数 |

### Trenches 过滤器示例

```bash
# 应用安全预设（服务器端）
gmgn-cli market trenches --chain sol --type new_creation --filter-preset safe

# 要求至少 1 个智能资金持有者（服务器端）
gmgn-cli market trenches --chain sol --type new_creation --min-smart-degen-count 1

# 安全预设 + 要求智能资金 + 按智能去中心化数量排序（服务器端过滤，客户端排序）
gmgn-cli market trenches --chain sol --type new_creation \
  --filter-preset safe --min-smart-degen-count 1 --sort-by smart_degen_count

# 严格预设 — 安全 + 智能资金 + 最小 1k 交易量（服务器端）
gmgn-cli market trenches --chain sol --type new_creation --type near_completion \
  --filter-preset strict --sort-by smart_degen_count

# 手动范围过滤器（全部发送服务器端）
gmgn-cli market trenches --chain sol --type new_creation \
  --max-rug-ratio 0.3 --max-bundler-rate 0.3 --max-insider-ratio 0.3 \
  --min-smart-degen-count 1 --min-volume-24h 1000

# 按代币年龄过滤：仅限在过去 30 分钟内创建的代币
gmgn-cli market trenches --chain sol --type new_creation --max-created 30m

# 按市值范围过滤
gmgn-cli market trenches --chain sol --type new_creation \
  --min-marketcap 10000 --max-marketcap 500000
```

## `market trenches` 响应字段

**基本信息**

| 字段 | 描述 |
|-------|-------------|
| `address` | 代币合约地址 |
| `symbol` / `name` | 代币符号和名称 |
| `launchpad_platform` | 启动平台 (例如 `Pump.fun`，`letsbonk`) |
| `exchange` | 当前交易所 (例如 `pump_amm`，`raydium`) |
| `usd_market_cap` | 市值 (USD) |
| `liquidity` | 流动性 (USD) |
| `total_supply` | 总代币供应量 |
| `created_timestamp` | 创建时间 (Unix 秒) |
| `open_timestamp` | 开放市场上市时间 (Unix 秒，仅 `completed`) |
| `complete_timestamp` | 锚定曲线完成时间 (Unix 秒) |
| `complete_cost_time` | 从创建到完成的时间 (秒) |

**交易数据**

| 字段 | 描述 |
|-------|-------------|
| `swaps_1m` / `swaps_1h` / `swaps_24h` | 每个时间窗口的交换次数 |
| `volume_1h` / `volume_24h` | 交易量 (USD) |
| `buys_24h` / `sells_24h` | 24h 买入/卖出次数 |
| `net_buy_24h` | 24h 净买入量 |
| `holder_count` | 代币持有者数量 |

**安全与风险**

| 字段 | 链 | 描述 |
|-------|--------|-------------|
| `renounced_mint` | SOL | 是否放弃铸造授权 (SOL 特有概念；EVM 链上始终为 `false`) |
| `renounced_freeze_account` | SOL | 是否放弃冻结授权 (SOL 特有概念；EVM 链上始终为 `false`) |
| `burn_status` | all | 流动性燃烧状态 |
| `rug_ratio` | all | 拉高风险比率 |
| `top_10_holder_rate` | all | 顶部 10 持有者集中度比率 |
| `rat_trader_amount_rate` | all | 内部人/偷袭交易量比率 |
| `bundler_trader_amount_rate` | all | 包裹交易量比率 |
| `is_wash_trading` | all | 是否检测到洗售交易 |
| `sniper_count` | all | 枪手钱包数量 |
| `suspected_insider_hold_rate` | all | 疑似内部人持有比率 |
| `open_source` | all | 是否验证合约源代码 (`"yes"` / `"no"` / `"unknown"`) |
| `owner_renounced` | all | 是否放弃合约所有权 (`"yes"` / `"no"` / `"unknown"`) |
| `is_honeypot` | BSC / Base | 代币是否为蜜罐 (`"yes"` / `"no"`；SOL 上返回空字符串 (不适用)) |
| `buy_tax` | all | 买入税率 (例如 `0.03` = 3%) |
| `dev_team_hold_rate` | all | 开发团队持有比率 |

**开发者持有**

| 字段 | 描述 |
|-------|-------------|
| `creator_token_status` | 开发者持有状态 (例如 `creator_hold`，`creator_close`) |
| `creator_balance_rate` | 开发者持有比率 (占总供应量的比例) |

**智能资金**

| 字段 | 描述 |
|-------|-------------|
| `smart_degen_count` | 智能资金持有者数量 |
| `renowned_count` | 著名钱包持有者数量 (KOL) |

**社交媒体**

| 字段 | 描述 |
|-------|-------------|
| `twitter` | Twitter / X 链接 |
| `telegram` | Telegram 链接 |
| `website` | 网站 |
| `instagram` | Instagram 链接 |
| `tiktok` | TikTok 链接 |
| `has_at_least_one_social` | 是否存在社交媒体链接 |
| `x_user_follower` | Twitter 关注者数量 |
| `cto_flag` | 是否发生过社区接管 (CTO) |

**Dexscreener 营销**

| 字段 | 描述 |
|-------|-------------|
| `dexscr_ad` | 是否已在 Dexscreener 上放置广告 |
| `dexscr_update_link` | 是否在 Dexscreener 上更新了社交链接 |
| `dexscr_trending_bar` | 是否为 Dexscreener 趋势条位放置付费 |
| `dexscr_boost_fee` | 为 Dexscreener 加速支付金额 (0 = 无) |

**获取 Trenches 结果后，在向用户展示代币前应用 Token Quality Filter Criteria 部分。** 不要直接倾倒原始结果 — 先过滤，再展示最强的候选者。

### Trenches 过滤器示例

```bash
# 快速安全筛选 — 排除拉高、洗售和包裹机器人
gmgn-cli market trenches --chain sol --type new_creation \
  --filter-preset safe --raw

# 智能资金筛选 — 仅限有智能资金或 KOL 存在的代币
gmgn-cli market trenches --chain sol \
  --type new_creation --type near_completion \
  --filter-preset smart-money \
  --sort-by smart_degen_count --raw

# 严格筛选 — 安全 + 智能资金 + 最小交易量，按智能去中心化排序
gmgn-cli market trenches --chain sol --type completed \
  --filter-preset strict --sort-by smart_degen_count --raw

# 自定义过滤器 — 无洗售交易、rug_ratio <= 0.2、至少 1 个智能去中心化
gmgn-cli market trenches --chain sol \
  --type new_creation --type near_completion \
  --exclude-wash-trading --max-rug-ratio 0.2 --min-smart-degen 1 \
  --sort-by smart_degen_count --raw

# BSC — 新代币的安全筛选来自 fourmeme
gmgn-cli market trenches --chain bsc --type new_creation \
  --launchpad-platform fourmeme --launchpad-platform fourmeme_agent \
  --filter-preset safe --sort-by volume_1h --raw

# 按 rug_ratio 升序排序 (最安全优先)，无其他过滤器
gmgn-cli market trenches --chain sol --type completed \
  --sort-by rug_ratio --raw

# 查找持有者众多且 1h 交换活动强劲的代币
gmgn-cli market trenches --chain sol --type completed \
  --min-holders 100 --min-swaps 50 \
  --sort-by swaps_1h --raw
```

### Solana Trenches 示例

```bash
# 三个类别同时获取
gmgn-cli market trenches --chain sol --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform Pump.fun --launchpad-platform pump_mayhem --launchpad-platform pump_mayhem_agent --launchpad-platform pump_agent --launchpad-platform letsbonk --launchpad-platform bonkers --launchpad-platform bags \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain sol --raw \
  --type new_creation \
  --launchpad-platform Pump.fun --launchpad-platform pump_mayhem --launchpad-platform pump_mayhem_agent --launchpad-platform pump_agent --launchpad-platform letsbonk --launchpad-platform bonkers --launchpad-platform bags \
  --limit 80

# 仅接近完成
gmgn-cli market trenches --chain sol --raw \
  --type near_completion \
  --launchpad-platform Pump.fun --launchpad-platform pump_mayhem --launchpad-platform pump_mayhem_agent --launchpad-platform pump_agent --launchpad-platform letsbonk --launchpad-platform bonkers --launchpad-platform bags \
  --limit 80

# 仅完成 (开放市场) 
gmgn-cli market trenches --chain sol --raw \
  --type completed \
  --launchpad-platform Pump.fun --launchpad-platform pump_mayhem --launchpad-platform pump_mayhem_agent --launchpad-platform pump_agent --launchpad-platform letsbonk --launchpad-platform bonkers --launchpad-platform bags \
  --limit 80
```

### BSC Trenches 示例

```bash
# 全部三个类别同时
gmgn-cli market trenches --chain bsc --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform fourmeme --launchpad-platform fourmeme_agent --launchpad-platform bn_fourmeme --launchpad-platform four_xmode_agent \
  --launchpad-platform cubepeg --launchpad-platform likwid --launchpad-platform goplus_creator --launchpad-platform goplus_skills --launchpad-platform openfour \
  --launchpad-platform flap --launchpad-platform flap_stocks --launchpad-platform flap_aioracle --launchpad-platform clanker --launchpad-platform lunafun \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain bsc --raw \
  --type new_creation \
  --launchpad-platform fourmeme --launchpad-platform fourmeme_agent --launchpad-platform bn_fourmeme --launchpad-platform four_xmode_agent \
  --launchpad-platform cubepeg --launchpad-platform likwid --launchpad-platform goplus_creator --launchpad-platform goplus_skills --launchpad-platform openfour \
  --launchpad-platform flap --launchpad-platform flap_stocks --launchpad-platform flap_aioracle --launchpad-platform clanker --launchpad-platform lunafun \
  --limit 80

# 仅接近完成
gmgn-cli market trenches --chain bsc --raw \
  --type near_completion \
  --launchpad-platform fourmeme --launchpad-platform fourmeme_agent --launchpad-platform bn_fourmeme --launchpad-platform four_xmode_agent \
  --launchpad-platform cubepeg --launchpad-platform likwid --launchpad-platform goplus_creator --launchpad-platform goplus_skills --launchpad-platform openfour \
  --launchpad-platform flap --launchpad-platform flap_stocks --launchpad-platform flap_aioracle --launchpad-platform clanker --launchpad-platform lunafun \
  --limit 80

# 仅已完成（开放市场）
gmgn-cli market trenches --chain bsc --raw \
  --type completed \
  --launchpad-platform fourmeme --launchpad-platform fourmeme_agent --launchpad-platform bn_fourmeme --launchpad-platform four_xmode_agent \
  --launchpad-platform cubepeg --launchpad-platform likwid --launchpad-platform goplus_creator --launchpad-platform goplus_skills --launchpad-platform openfour \
  --launchpad-platform flap --launchpad-platform flap_stocks --launchpad-platform flap_aioracle --launchpad-platform clanker --launchpad-platform lunafun \
  --limit 80
```

### 基础通道示例

```bash
# 全部三个类别同时
gmgn-cli market trenches --chain base --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform clanker --launchpad-platform bankr --launchpad-platform flaunch --launchpad-platform zora --launchpad-platform zora_creator --launchpad-platform baseapp --launchpad-platform basememe --launchpad-platform virtuals_v2 --launchpad-platform klik \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain base --raw \
  --type new_creation \
  --launchpad-platform clanker --launchpad-platform bankr --launchpad-platform flaunch --launchpad-platform zora --launchpad-platform zora_creator --launchpad-platform baseapp --launchpad-platform basememe --launchpad-platform virtuals_v2 --launchpad-platform klik \
  --limit 80

# 仅接近完成
gmgn-cli market trenches --chain base --raw \
  --type near_completion \
  --launchpad-platform clanker --launchpad-platform bankr --launchpad-platform flaunch --launchpad-platform zora --launchpad-platform zora_creator --launchpad-platform baseapp --launchpad-platform basememe --launchpad-platform virtuals_v2 --launchpad-platform klik \
  --limit 80

# 仅已完成（开放市场）
gmgn-cli market trenches --chain base --raw \
  --type completed \
  --launchpad-platform clanker --launchpad-platform bankr --launchpad-platform flaunch --launchpad-platform zora --launchpad-platform zora_creator --launchpad-platform baseapp --launchpad-platform basememe --launchpad-platform virtuals_v2 --launchpad-platform klik \
  --limit 80
```

### ETH 通道示例

```bash
# 全部三个类别同时
gmgn-cli market trenches --chain eth --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform trench --launchpad-platform clanker --launchpad-platform klik --launchpad-platform livo --launchpad-platform stroid --launchpad-platform pool_uniswap_v2 --launchpad-platform pool_uniswap_v3 --launchpad-platform printr \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain eth --raw \
  --type new_creation \
  --launchpad-platform trench --launchpad-platform clanker --launchpad-platform klik --launchpad-platform livo --launchpad-platform stroid --launchpad-platform pool_uniswap_v2 --launchpad-platform pool_uniswap_v3 --launchpad-platform printr \
  --limit 80

# 仅已完成（开放市场）
gmgn-cli market trenches --chain eth --raw \
  --type completed \
  --launchpad-platform trench --launchpad-platform clanker --launchpad-platform klik --launchpad-platform livo --launchpad-platform stroid --launchpad-platform pool_uniswap_v2 --launchpad-platform pool_uniswap_v3 --launchpad-platform printr \
  --limit 80
```

### Arc 通道示例

```bash
# 全部三个类别同时
gmgn-cli market trenches --chain arc --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench --launchpad-platform onmifun --launchpad-platform sharcfun --launchpad-platform klik \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain arc --raw \
  --type new_creation \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench --launchpad-platform onmifun --launchpad-platform sharcfun --launchpad-platform klik \
  --limit 80

# 仅接近完成
gmgn-cli market trenches --chain arc --raw \
  --type near_completion \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench --launchpad-platform onmifun --launchpad-platform sharcfun --launchpad-platform klik \
  --limit 80

# 仅已完成（开放市场）
gmgn-cli market trenches --chain arc --raw \
  --type completed \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench --launchpad-platform onmifun --launchpad-platform sharcfun --launchpad-platform klik \
  --limit 80
```

### 稳定通道示例

```bash
# 全部三个类别同时
gmgn-cli market trenches --chain stable --raw \
  --type new_creation --type near_completion --type completed \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench \
  --limit 80

# 仅新创建
gmgn-cli market trenches --chain stable --raw \
  --type new_creation \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench \
  --limit 80

# 仅接近完成
gmgn-cli market trenches --chain stable --raw \
  --type near_completion \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench \
  --limit 80

# 仅已完成（开放市场）
gmgn-cli market trenches --chain stable --raw \
  --type completed \
  --launchpad-platform dyorfun_v3 --launchpad-platform dyorswap --launchpad-platform trench \
  --limit 80
```

## 输出格式

### `market kline` — 价格摘要

获取K线后，提供简短的价格分析。不要输出原始K线数组。

```
{symbol} — {resolution}图表 ({from} → {to})
开盘：${第一个K线的开盘价}  |  收盘：${最后一个K线的收盘价}  |  波动范围：${最低低点} – {最高高点}
总成交量：${所有成交量字段的和}美元
趋势：[简要描述——例如："稳定上涨趋势"、"急剧下跌后反弹"、"横盘"]
```

### `market trending` — 顶级代币表格

以表格形式呈现顶级结果（默认：前10名，或按请求）：

```
# | Symbol | Price | MCap | Volume ({interval}) | 1h Chg | SM | Liq | Platform | Signal
```

其中**Signal** = 基于代币数据的质量标志：
- 🟢 通过：`smart_degen_count ≥ 3` AND `rug_ratio < 0.2` AND `is_wash_trading = false`
- 🔴 跳过：`rug_ratio > 0.3` OR `is_wash_trading = true` OR `is_honeypot = 1`
- 🟡 观察：其他所有情况

然后为任何突出的代币提供一行高亮（例如："TOKEN1有12个智能资金持有者，1小时内+85%——🟢 强信号”）。

### `market trenches` — 按类别分组

以标题单独呈现每个类别：

```
🆕 新创建 ({count}个代币)
# | Symbol | 创建时间 | 流动性 | 1小时交易量 | 智能资金持有者 | 社交

⏳ 接近完成 ({count}个代币)
# | Symbol | 市值 | 1小时交易量 | 智能资金持有者 | 社交

✅ 毕业生 ({count}个代币)
# | Symbol | 市值 | 1小时成交量 | 智能资金持有者 | 社交
```

## `market signal` 参数

链：`sol` / `bsc` / `robinhood` / `arc` / `stable` 仅限。**每组最多50个结果**——使用多个组通过 `--groups` 来覆盖单个请求中的不同信号类型。

**单组（单个标志）：**

不要在 `signal_type` / `--signal-type` / `--groups` JSON 中传递信号类型 **14、15 或 16**——如果任何组包含它们，OpenAPI 将返回 **400**。省略 `--signal-type` 查询所有支持类型：**1–13 和 17–21**。

| 选项 | 是否必需 | 描述 |
|------|----------|------|
| `--chain` | 是 | `sol` / `bsc` / `robinhood` / `arc` / `stable` |
| `--signal-type` | 否 | 信号类型（可重复）：`1`–`13`，`17`–`21`；默认：所有支持类型。见信号类型下方。 |
| `--mc-min` | 否 | 触发时最小市值（美元） |
| `--mc-max` | 否 | 触发时最大市值（美元） |
| `--trigger-mc-min` | 否 | 信号触发时刻最小市值（美元） |
| `--trigger-mc-max` | 否 | 信号触发时刻最大市值（美元） |
| `--total-fee-min` | 否 | 支付的总费用（美元） |
| `--total-fee-max` | 否 | 支付的总费用（美元） |
| `--min-create-or-open-ts` | 否 | 最小代币创建或打开时间戳（Unix秒字符串） |
| `--max-create-or-open-ts` | 否 | 最大代币创建或打开时间戳（Unix秒字符串） |

**多组覆盖：**

通过 `--groups '<json_array>'` 将多个过滤组查询为单个请求。上游并行执行所有组，并按 `trigger_at` 降序合并结果。当 `--groups` 存在时，所有上述单个标志将被忽略。

```bash
gmgn-cli market signal --chain sol \
  --groups '[{"signal_type":[12,13]},{"signal_type":[6,7],"mc_min":50000}]'
```

### 信号类型

| 值 | 名称 | 描述 |
|----|------|------|
| 1 | SignalType1 | 一般信号（K线价格飙升） |
| 2 | SignalTypeDexAd | DEX广告位置 |
| 3 | SignalTypeDexUpdateLink | DEX社交链接更新 |
| 4 | SignalTypeDexTrendingBar | DEX趋势条 |
| 5 | SignalTypeDexBoost | DEX增强 |
| 6 | SignalTypePriceUp | 价格飙升 |
| 7 | SignalTypePriceATH | 历史最高价 |
| 8 | SignalTypeMcpKeyLevel | 市值关键水平 |
| 9 | SignalTypeLive | 直播 |
| 10 | SignalTypeBundlerSell | Bundler卖出 |
| 11 | SignalTypeCto | 社区接管（CTO） |
| 12 | SignalTypeSmartDegenBuy | 智能资金买入 |
| 13 | SignalTypePlatformCall | 平台调用 |
| 14 | SignalTypeLargeAmountBuy | 大额买入 |
| 15 | SignalTypeMultiBuy | 多次买入 |
| 16 | SignalTypeMultiLargeBuy | 多次大额买入 |
| 17 | SignalTypeBagsClaims | 袋子声明 |
| 18 | SignalTypePumpClaims | 泵声明 |
| 19 | SignalTypePlatformCallV2 | 平台调用（V2） |
| 20 | SignalTypeKOLBuy | KOL买入 |
| 21 | SignalTypeBankerClaims | Banker声明（基础链Banker平台声明费用） |

### `market signal` 响应字段

响应数组中的每个项目是一个信号事件：

| 字段 | 类型 | 描述 |
|------|------|------|
| `id` | string | 信号事件ID |
| `token_address` | string | 代币合约地址 |
| `signal_type` | number | 信号类型（1–21，见上方信号类型） |
| `trigger_at` | number | 信号被触发时的Unix时间戳（秒） |
| `trigger_mc` | number | 信号触发时的市值（美元） |
| `first_trigger_mc` | number | 该代币首次触发的市值（美元） |
| `market_cap` | number | 当前市值（美元） |
| `ath` | number | 历史最高市值（美元） |
| `signal_times` | number | 该代币触发此信号的次数 |
| `signal_times_by_type` | object | 按类型细分的信号触发次数 |
| `cur_data` | object | 查询时实时代币统计数据（见下方） |
| `data` | object | 触发时的完整上游快照（链特定，原始传递） |

**`cur_data` 字段：**

| 字段 | 类型 | 描述 |
|------|------|------|
| `top_10_holder_rate` | number | 顶部10个持有者集中度（0–1） |
| `holder_count` | number | 当前持有者数量 |
| `liquidity` | number | 当前流动性（美元） |

### 使用示例

```bash
# SOL上所有支持信号类型（无 --signal-type）
gmgn-cli market signal --chain sol --raw

# 仅智能资金买入（类型12）
gmgn-cli market signal --chain sol --signal-type 12 --raw

# 价格飙升+ATH（类型6和7）带市值过滤
gmgn-cli market signal --chain sol \
  --signal-type 6 --signal-type 7 \
  --mc-min 50000 --mc-max 5000000 --raw

# BSC上的智能资金买入
gmgn-cli market signal --chain bsc --signal-type 12 --raw

# 多组：并行组（不要使用信号类型14–16——API返回400）
gmgn-cli market signal --chain sol \
  --groups '[{"signal_type":[12]},{"signal_type":[6,7]}]' --raw

# 多组：将信号类型过滤与每组市值范围结合
gmgn-cli market signal --chain sol \
  --groups '[{"signal_type":[12,13],"mc_min":100000},{"signal_type":[6,7],"mc_min":50000,"mc_max":1000000}]' --raw
```

## `market hot-searches` 参数

返回热门搜索排名——人们当前搜索最多的代币，按 `visiting_count`（搜索热度）排名。跨链前500名排名；一次请求可以覆盖多个链。**用于"最搜索代币"、"热门搜索列表"、"热搜榜"、"大家都在看"**——这与 `market trending`（按交易量排名）不同，后者回答"什么正在被交易最多"。

| 选项 | 描述 |
|------|------|
| `--chain <chain...>` | 可重复。`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable`。**省略以查询默认的9链集**（每个链使用适当的链安全过滤器，时间间隔为`24h`）。 |
| `--interval <interval>` | `1m` / `5m` / `1h` / `6h` / `24h`（默认`24h`）。应用于提供的每个`--chain`。 |
| `--limit <n>` | 每个链的最大结果数（默认`500`）。 |
| `--filter <tag...>` | 可重复 **布尔** 过滤标签（下游`filter.filters`数组）。**⚠️ SOL默认：`renounced frozen`；EVM默认：`not_honeypot verified renounced`**。省略`--filter`不是"无过滤器"——服务器应用链默认值。见过滤标签表以获取确切词汇。 |
| `--min-* / --max-* <n>` | 数值范围边界，**与`market trending`相同的指标名称**（例如：`--min-liquidity`，`--max-marketcap`，`--min-smart-degen-count`）。服务器端按`--interval`翻译。`--min-created` / `--max-created`是代币年龄持续时间。见范围过滤表。 |
| `--params <json>` | 完全覆盖：参数对象的JSON数组。提供时，`--chain` / `--interval` / `--limit` / `--filter`以及所有范围标志将被忽略。过滤字段被**展平到每个参数**（无嵌套`filter`对象）：`{ "label": "...", "chain": "...", "interval": "...", "filters": [...], "limit": 500, "min_liquidity": 1000 }`——参数接受`filters`，`limit`，`min_created`/`max_created`，以及排名式`min_<metric>`/`max_<metric>`键。 |

### `market hot-searches` 过滤标签 (`--filter` / `filter.filters`)

下游（gmgn 排名过滤服务）将每个标签视为一个 AND 条件——一个代币必须通过**所有**标签才能保留在列表中。**未知标签会被静默接受但不做任何操作**（直接通过），因此一个未识别的标签将**不会**过滤任何内容——拼写很重要。这个标签集是过滤服务的词汇表，与 `market trending` 的标签名称略有不同（见下文的别名说明）。

**这些是唯一被识别的标签**（任何其他内容都是无操作的）：

| 标签 | 链 | 通过条件 |
|----------------------|-------------|-------------|
| `renounced` | sol / EVM | sol: 薄饼铸造授权被放弃（`renounced_mint == 1`）；EVM: 所有者放弃（`is_renounced == 1`；宽松——nil 通过） |
| `frozen` | sol 仅 | 冻结授权被放弃（`renounced_freeze_account == 1`）；非 sol 总是失败 |
| `is_burnt` | 所有 | LP 池被燃烧（`burn_status == "burn"`) |
| `token_burnt` | 所有 | 创建者燃烧代币（`dev_token_burn_ratio > 0`) |
| `not_wash_trading` | 所有 | 未被标记为洗售交易 |
| `not_honeypot` | EVM | 不是蜜罐（`is_honeypot == 0`；宽松——nil 通过） |
| `verified` | EVM | 合约开源（`is_open_source == 1`；宽松——nil 通过） |
| `locked` | EVM | 流动性锁定 ≥ 50% (`lock_percent >= 0.5`) |
| `has_social` | 所有 | 有 Twitter、Telegram 或网站 |
| `distribed` | 所有 | 顶部 10 持有者比率在 (0, 0.3]（分布良好） |
| `not_risk` | 所有 | 复合低风险过滤（sol: 流动性≥4000 + 薄饼放弃 + 顶部<0.3 + 冻结放弃 + LP 燃烧；EVM: 不是蜜罐 + 流动性≥4000 + 开源 + 放弃 + 锁定≥0.5) |
| `img_not_duplicate` | 所有 | 头像图片未重复（`image_dup == "0"`) |
| `social_not_duplicate` | 所有 | 社交链接未共享（`twitter_dup == 0 && telegram_dup == 0 && website_dup == 0`) |
| `creator_hold` | 所有 | 开发者仍然持有（不是 `creator_close`) |
| `creator_close` | 所有 | 开发者出售/关闭（`creator_token_status == "creator_close"`) |
| `dexscr_update_link` | 所有 | 社交链接在 DexScreener 上更新（`> 0`) |
| `launching` | 所有 | 仍在启动板上绑定曲线（`launchpad_status == "0"`）；与 `migrated` 配合使用以允许两者 |
| `migrated` | 所有 | 毕业 / 迁移到 DEX（`launchpad_status == "1"`）；与 `launching` 配合使用以允许两者 |
| `hide_b20` | base 仅 | 代币标准不是 `b20`（在非 base 上无操作） |
| `hide_non_b20` | base 仅 | 代币标准是 `b20`（在非 base 上无操作） |

> **⚠️ 名称与 `market trending` 不同。** 此路径使用 `launching` / `migrated`（不是 `is_internal_market` / `is_out_market`）和 `img_not_duplicate` / `social_not_duplicate`（不是 `not_image_dup` / `not_social_dup`）。`market trending` 支持但此端点不识别的标签（在这里成为静默无操作的）：`dexscr_ad`、`dexscr_trending_bar`、`dexscr_boost`、`cto_flag`、`is_internal_market`、`is_out_market`、`not_image_dup`、`not_social_dup`。

### `market hot-searches` 范围过滤 (`--min-*` / `--max-*`)

数值边界使用与 `market trending` **相同的排名样式指标名称**。它们在每个参数上扁平化发送，并在服务器端转换为下游字段，用于参数的 `--interval`。闭区间；下游无法读取的指标会被丢弃（在网络上不是静默无操作的——它们在请求之前被移除）。

| 标签对 | 类型 | 指标 |
|------------------------------------------------------------|----------|--------|
| `--min-volume` / `--max-volume` | float | 交易量（美元）——绑定到 `--interval` 窗口 |
| `--min-swaps` / `--max-swaps` | int | 交换次数——绑定到 `--interval` 窗口 |
| `--min-price-change-percent` / `--max-price-change-percent` | float | 价格变化比率——**仅 `1m` / `5m` / `1h`；对于 `6h` / `24h` 被丢弃** |
| `--min-liquidity` / `--max-liquidity` | float | 流动性（美元） |
| `--min-marketcap` / `--max-marketcap` | float | 市值（美元） |
| `--min-history-highest-marketcap` / `--max-history-highest-marketcap` | float | 历史最高市值（美元） |
| `--min-holder-count` / `--max-holder-count` | int | 持有者数量 |
| `--min-gas-fee` / `--max-gas-fee` | float | 燃气费用 |
| `--min-renowned-count` / `--max-renowned-count` | int | KOL / 著名持有者数量 |
| `--min-smart-degen-count` / `--max-smart-degen-count` | int | 智能资金持有者数量 |
| `--min-bot-degen-count` / `--max-bot-degen-count` | int | Bot-degen 钱包数量 |
| `--min-visiting-count` / `--max-visiting-count` | int | 访问者数量 |
| `--min-insider-rate` / `--max-insider-rate` | float | 内部交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-bundler-rate` / `--max-bundler-rate` | float | Bundle-bot 交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-entrapment-ratio` / `--max-entrapment-ratio` | float | 诱捕交易比率（0–1）；缺少此字段的代币将被排除 |
| `--min-top10-holder-rate` / `--max-top10-holder-rate` | float | 顶部 10 持有者集中度（0–1） |
| `--min-top70-sniper-hold-rate` / `--max-top70-sniper-hold-rate` | float | 顶部 70 枪手持有比率（0–1） |
| `--min-dev-team-hold-rate` / `--max-dev-team-hold-rate` | float | 开发者团队持有比率（0–1） |
| `--min-created` / `--max-created` | 持续时间 | 代币年龄窗口（`30m` / `6h` / `7d`）。`min_created` = 最小年龄；`max_created` = 最大年龄 |

**行为说明：**

- `--chain all` 是**无效的**。要跨链聚合，请多次传递 `--chain`（或省略 `--chain` 以使用默认的 9 链集）。
- 当你传递 `--chain` 但省略 `--filter` 时，**服务器**会应用链相关的默认过滤条件——因此即使没有显式的 `--filter`，每个链也会被过滤。
- 不同链返回不同的计数：一个链的代币数量取决于其有多少代币进入了全球前 500（sol 通常是最大的）。

## `market hot-searches` 响应字段

响应 `data` 是一个数组。每个元素是一个 `(interval, chain)` 结果块：

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `interval` | string | 此块的间隔 |
| `chain` | string | 此块的链 |
| `version` | string | 订阅版本——在 WebSocket 重连时保留它 |
| `tokens` | 数组 | 排名代币（搜索热度降序），最多 500。每个代币都带有 1-based `rank` |

**代币字段与 `market trending` 的长格式字段相同**——服务器会为你映射上游的简码，因此你可以直接读取 `visiting_count` / `market_cap` / `symbol`（不是 `v_c` / `mc` / `s`）。关键字段：

| 字段 | 描述 |
|-------|-------------|
| `address` | 代币合约地址 |
| `chain` | 链 |
| `name` / `symbol` | 代币名称 / 贴票 |
| `price` | 当前价格（美元） |
| `visiting_count` | **主要排名键——搜索 / 访问热度** |
| `market_cap` | 市值（美元） |
| `volume` | 此间隔内的交易量（美元） |
| `liquidity` | 流动性（美元） |
| `swaps` / `buys` / `sells` | 交换 / 买入 / 卖出计数 |
| `holder_count` | 持有者数量 |
| `rank` | 块内的 1-based 位置 |

有关完整字段集，请参阅上方的 [`market trending` 响应字段](#market-trending-response-fields) 部分——热搜索代币使用相同的 `RankItem` 形状。

### `market hot-searches` 使用示例

```bash
# 默认 9 链热搜索排名（sol/bsc/base/eth/arbitrum/hyperevm/robinhood/arc/stable，每个 24h）
gmgn-cli market hot-searches --raw

# SOL 仅，24h 热搜索列表
gmgn-cli market hot-searches --chain sol --interval 24h --raw

# SOL + BSC + Base，1h 窗口，每个链前 50
gmgn-cli market hot-searches --chain sol --chain bsc --chain base --interval 1h --limit 50 --raw

# SOL 自定义布尔过滤
gmgn-cli market hot-searches --chain sol --interval 24h \
  --filter renounced --filter frozen --raw

# SOL 1h 热搜索与数值范围过滤（与 `market trending` 相同的指标名称）
gmgn-cli market hot-searches --chain sol --interval 1h \
  --min-liquidity 10000 --min-volume 5000 --min-smart-degen-count 1 --raw

# 通过代币年龄 + 市值进行范围过滤
gmgn-cli market hot-searches --chain sol --interval 24h \
  --max-created 7d --min-marketcap 50000 --raw

# 通过 JSON 每个参数完全覆盖（每个链不同的过滤条件，包括范围）
gmgn-cli market hot-searches --raw --params '[
  {"label":"hot-search","chain":"sol","interval":"24h","filters":["renounced","frozen"],"limit":500,"min_liquidity":10000},
  {"label":"hot-search","chain":"bsc","interval":"24h","filters":["not_honeypot","verified","renounced"],"limit":500}
]'
```

### `market hot-searches` — 输出格式

按链呈现，按 `visiting_count`（搜索热度）排序：

```
🔥 热搜索 — {chain} ({interval})
# | Symbol | Price | MCap | Volume | 搜索热度 (visiting_count) | Liq
```

---

## `market search` 参数

查找用户命名的**特定**代币或钱包——通过代币名称、符号、合约地址、钱包地址或 ENS。单个请求返回匹配的代币（`coins`）和钱包（`wallets`）。当用户提供了具体内容以查找时使用；当用户想浏览排名时使用 `market trending` / `market hot-searches`。

| 参数 | 必填 | 描述 |
|-----------|----------|-------------|
| `--query` / `-q` | 是 | 搜索关键字——代币名称、符号、合约地址、钱包地址或 ENS。删除不可见/控制字符后，它必须是 **1–100 个 Unicode 字符**。 |
| `--chain` | 否 | 将结果限制在一个链上。省略以搜索所有链。接受 `all` 和任何启用的链（见支持的链——包括 9 个核心链以及动态启用的链，如 `tron` / `monad` / `megaeth` / `xlayer` / `hyperevm`）。 |
| `--launchpad-platform` | 否 | 精确启动板平台过滤，**可重复**，最多 50 个值（例如 `pump` / `moonshot` / `raydium` / `pinksale`）。**仅过滤 `coins`——不影响 `wallets`。** |
| `--is-og` | 否 | `true` = 仅 OG 代币；`false` = 仅非 OG。省略无 OG 过滤。**仅 `coins`。** |
| `--is-launched` | 否 | `true` = 仅已启动（开放市场）代币；`false` 或省略应用无启动过滤。**仅 `coins`。** |
| `--order-by` | 否 | 仅接受 `weight`——按加权相关性分数降序排序 `coins` 并丢弃蜜罐代币。**仅 `coins`。** |

**行为说明：**

- `--launchpad-platform`、`--is-og`、`--is-launched` 和 `--order-by` 仅塑造 `coins` 列表。`wallets` 列表永远不会受这些标志的影响。
- `wallets` 最多限制为 **50** 个结果。
- 响应模式是下游 `search_v3` API 的原始附加传递，所有字符串字段在返回前都会进行元数据清理。新字段可能会出现而无需通知——不要假设封闭的字段集；而是查找不熟悉的字段而不是猜测。

## `market search` 响应字段

`data` 包含两个数组：`coins`（匹配的代币）和 `wallets`（匹配的钱包）。

**`coins[]` — 匹配的代币**

| 字段 | 描述 |
|-------|-------------|
| `chain` | 链标识符 |
| `address` | 代币合约地址 |
| `name` / `symbol` | 代币名称 / 贴票 |
| `price` | 当前价格（美元）（字符串） |
| `mcp` | 市值（美元）（字符串）——**注意简短键 `mcp`**，不是 `market_cap` |
| `holder_count` | 代币持有者数量 |

其他代币字段可能存在（来自 `search_v3` 的附加传递）。

**`wallets[]` — 匹配的钱包**

| 字段 | 描述 |
|-------|-------------|
| `chain` | 链标识符 |
| `address` | 钱包地址 |
| `twitter_username` | 链接的 Twitter / X 处理程序（可能为空） |
| `wallet_tags` | GMGN 钱包标签数组（例如智能资金 / KOL）；可能为空 |

## `market search` 使用示例

```bash
# 在 ETH 上搜索 "pepe"——最佳匹配优先（加权，蜜罐被丢弃）
gmgn-cli market search --query pepe --chain eth --order-by weight

# 跨所有链通过符号搜索
gmgn-cli market search --query trump

# 查找特定代币合约地址（SOL）
gmgn-cli market search --query <token_address> --chain sol

# 通过地址或 ENS 查找钱包
gmgn-cli market search --query vitalik.eth
gmgn-cli market search --query 0x220866b1a2219f40e72f5c628b65d54268ca3a9d

# SOL pump.fun 已启动代币匹配 "trump"
gmgn-cli market search --query trump --chain sol \
  --launchpad-platform pump --is-launched true

# 仅 OG 代币，原始 JSON 以供进一步处理
gmgn-cli market search --query doge --is-og true --raw
```

### `market search` — 输出格式

分别呈现代币和钱包。不要转储原始 JSON。

```
🔎 搜索 "{query}" — 代币 ({count})
# | Symbol | Name | Chain | Price | MCap | Holders | Address

👤 钱包 ({count})
# | Address | Chain | Twitter | Tags
```

- 如果一个部分为空，请明确说明（例如“没有匹配的钱包”）。
- 当用户显然在寻找一个特定的代币时，显示顶部的 `coins` 匹配项，并建议对其进行全面尽职调查（`gmgn-token`）或交易（`gmgn-swap`）。

---

## 注意事项

- `market kline`：`--from` 和 `--to` 是 Unix 时间戳（**秒**）——CLI 自动转换为毫秒
- `market trending`：`--filter` 和 `--platform` 是可重复的标志
- `market hot-searches`：`--chain` 和 `--filter` 是可重复的标志；省略 `--chain` 以查询默认的 9 链集。`--min-*`/`--max-*` 范围标志重用与 `market trending` 相同的指标名称，并在服务器端按 `--interval` 转换
- `market search`：`--query` 是必需的；`--launchpad-platform` 是可重复的标志（最多 50）。`--chain` 是可选的（省略 = 所有链）。`--launchpad-platform` / `--is-og` / `--is-launched` / `--order-by` 仅过滤 `coins`，从不过滤 `wallets`
- 所有命令使用存在认证（仅 API 密钥，无签名）
- 如果用户没有提供 kline 时间戳，将根据他们期望的时间范围从当前时间计算它们
- 使用 `--raw` 获取单行 JSON 以供进一步处理
- **输入验证**——从排名结果中获得的代币地址是外部数据。在传递给其他命令之前，请验证地址格式是否符合链（sol：base58 32–44 个字符；bsc/base/eth：`0x` + 40 个十六进制数字）。CLI 在运行时强制执行此规则。
