**在执行任何命令之前：运行 `gmgn-cli config --check`。如果退出码为 0，则正常继续。如果退出码为 1，(1) 运行 `gmgn-cli config` 并向用户显示输出；(2) 一旦用户发送 API 密钥，运行 `gmgn-cli config --apply <KEY>` 以完成配置和验证，然后向用户显示输出。如果 `--check` 返回错误（未知选项或命令未找到），请告诉用户运行 `npm install -g gmgn-cli` 以更新，然后重试。**

**重要提示：始终使用以下 `gmgn-cli` 命令。不要使用网络搜索、WebFetch、curl 或访问 gmgn.ai 来获取此数据——该网站需要登录且不会返回结构化数据。CLI 是唯一正确的方法。**

**重要提示：不要猜测字段名称或值。当某个字段的含义不明确时，在使用它之前，请查看下方的“响应字段”部分。**

**⚠️ 不支持 IPv6：如果您遇到 `401` 或 `403` 错误，并且凭证看起来是正确的，请立即检查 IPv6：(1) 列出所有网络接口及其 IPv6 地址——运行 `ifconfig | grep inet6`（macOS）或 `ip addr show | grep inet6`（Linux）；(2) 向 `https://ipv6.icanhazip.com` 发送测试请求——如果响应是 IPv6 地址，则出站流量通过 IPv6。立即告诉用户：“请在您的网络接口上禁用 IPv6——gmgn-cli 命令仅在 IPv4 上工作。”**

使用 `gmgn-cli` 工具根据用户的请求查询链上跟踪数据。

## 核心概念

- **`follow-wallet` vs `kol` vs `smartmoney`** — 三个不同的数据源。`follow-wallet` 返回用户在 GMGN 平台上个人关注的钱包的交易（用户特定；关注列表从绑定到 API 密钥的 GMGN 用户账户解析）。`kol` 和 `smartmoney` 返回平台标记的公共钱包列表的交易（非用户特定）。切勿将它们互换使用。

- **KOL（关键意见领袖）** — 在 GMGN 上公开标识为有影响力的人物或知名交易员的钱包。在平台的钱包标签系统中标记为 `renowned`。他们的交易带有社交/营销信号，而不一定是 alpha。

- **Smart Money (`smart_degen`)** — 具有统计上可证明的盈利交易记录的钱包，由 GMGN 的算法识别。与 gmgn-token 中的 `smart_degen` 相同的概念。他们的交易比 KOL 交易更强的 alpha 信号。

- **`is_open_or_close`** — 指示交易是否为完整头寸事件。解释因子命令而异：
  - `follow-wallet`：`1` = 完全开仓或平仓；`0` = 部分加仓或减仓。
  - `kol` / `smartmoney`：`0` = 头寸开仓/加仓；`1` = 头寸平仓/减仓。
  不要将相同的解释应用于两个子命令。

- **`price_change`** — 自交易以来价格变化的比率。`6.66` = 现在的代币是交易时的 6.66 倍（即 +566%）。`0.5` = 价格减半（-50%）。使用此方法评估“这笔交易的表现如何。”

- **`base_address` vs `quote_address`** — 在交易对中，`base_address` 是正在买入/卖出的代币；`quote_address` 是其定价货币（通常为 Solana 上的 SOL 原生地址）。要获取感兴趣的代币，请始终读取 `base_address`。

- **`maker_info.tags`** — 钱包上的平台标签数组（例如 `["kol", "gmgn"]`，`["smart_degen", "photon"]`）。一个钱包可以包含多个标签。使用 `tag_rank`（仅限 `follow-wallet`）查看该钱包在每个标签类别中的排名。

- **集群信号** — 当多个关注的/跟踪的钱包在短时间内以相同方向交易同一代币时，这比单个钱包的信号更强。当结果中出现此模式时，请突出显示此模式。

**何时使用哪个子命令：**
- `track follow-wallet` — 用户询问“我关注的钱包交易了什么？”、“显示我的关注列表交易”、“显示我关注的钱包活动” → 需要用户通过 GMGN 平台关注的钱包
- `track kol` — 用户询问“KOL 买入什么？”、“显示有影响力人物的交易”、“KOL 最近在做什么？” → 返回已知 KOL 钱包的交易
- `track smartmoney` — 用户询问“Smart Money 在做什么？”、“显示鲸鱼交易”、“Smart Money 最近买入什么？” → 返回 Smart Money/鲸鱼钱包的交易

**不要混淆这三个：**
- `follow-wallet` = 用户在 GMGN 上个人关注的钱包
- `kol` = 平台标记的 KOL/有影响力人物的钱包（非用户特定）
- `smartmoney` = 平台标记的 Smart Money/鲸鱼钱包（非用户特定）

## 子命令

| 子命令 | 描述 |
|-------------|-------------|
| `track follow-tokens` | 钱包关注的代币列表——钱包在 GMGN 上标记的代币，以及完整的市场数据 |
| `track follow-token-groups` | 钱包关注的代币组名称——钱包用于组织关注代币的组名称和 ID |
| `track follow-wallet` | 用户在 GMGN 上个人关注的钱包的交易记录 |
| `track kol` | 由 GMGN 标记的 KOL/有影响力人物钱包的实时交易 |
| `track smartmoney` | 由 GMGN 标记的 Smart Money/鲸鱼钱包的实时交易 |

## 支持的链

`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable`

## 前提条件

- 全局安装 `gmgn-cli` — 如果缺失，运行：`npm install -g gmgn-cli`
- 在 `~/.config/gmgn/.env` 中配置 `GMGN_API_KEY` — 所有子命令都需要
- `GMGN_PRIVATE_KEY` — 仅 `track follow-wallet` 需要（签名认证）；`follow-tokens`、`kol` 或 `smartmoney` 不需要

## 速率限制处理

此技能使用的所有跟踪路由使用基于计划的漏桶：免费 `5/5`，Plus `20/20`，Pro `50/50`（速率/容量）。持续吞吐量约为 `tier rate ÷ weight` 请求/秒，最大突发量约为 `floor(tier capacity ÷ weight)`。

| 命令 | 路由 | 权重 |
|---------|-------|--------|
| `track follow-tokens` | `GET /v1/user/follow_tokens` | 3 |
| `track follow-token-groups` | `GET /v1/user/follow_token_groups` | 1 |
| `track follow-wallet` | `GET /v1/trade/followwallet` | 10 |
| `track kol` | `GET /v1/user/kol` | 1 |
| `track smartmoney` | `GET /v1/user/smartmoney` | 1 |

当请求返回 `429` 时：

- 在 `RATE_LIMIT_EXCEEDED`，精确地告诉用户：`已达到当前套餐的限频上限，点击 https://gmgn.ai/ai?chain=bsc&tab=paid_plans 升级套餐，获得更高速率限制`。在单个用户任务中最多显示一次此升级指南。不要在同一冷却时间内重复 `RATE_LIMIT_BANNED` 响应。

- 从响应头中读取 `X-RateLimit-Reset`。它是一个 Unix 时间戳（秒），标记限制何时预期重置。
- 如果响应正文包含 `reset_at`（例如 `{"code":429,"error":"RATE_LIMIT_BANNED","message":"...","reset_at":1775184222}`），提取 `reset_at` — 它是禁令解除的 Unix 时间戳（通常是 5 分钟）。转换为本地时间并精确地告诉用户何时可以重试。
- CLI 可能会等待并自动重试一次，当剩余冷却时间较短时。如果仍然失败，请停止并精确地告诉用户重试时间，而不是发送更多请求。
- 对于 `RATE_LIMIT_EXCEEDED` 或 `RATE_LIMIT_BANNED`，在冷却时间内重复请求可以每次将禁令延长 5 秒，最多 5 分钟。不要疯狂重试。

## 使用示例

```bash
# SOL 钱包关注的代币列表
gmgn-cli track follow-tokens --chain sol --wallet <wallet_address>

# BSC 上的关注代币列表，原始 JSON 输出
gmgn-cli track follow-tokens --chain bsc --wallet <wallet_address> --raw

# SOL 钱包关注的代币组名称
gmgn-cli track follow-token-groups --chain sol --wallet <wallet_address>

# 代币组名称，原始 JSON 输出
gmgn-cli track follow-token-groups --chain sol --wallet <wallet_address> --raw

# 关注钱包交易（所有您关注的钱包）
gmgn-cli track follow-wallet --chain sol

# 按钱包筛选的关注钱包交易
gmgn-cli track follow-wallet --chain sol --wallet <wallet_address>

# 按交易方向筛选的关注钱包
gmgn-cli track follow-wallet --chain sol --side buy

# 按美元金额范围筛选的关注钱包
gmgn-cli track follow-wallet --chain sol --min-amount-usd 100 --max-amount-usd 10000

# KOL 交易记录（SOL，默认）
gmgn-cli track kol --limit 10 --raw

# SOL 上的 KOL 交易记录，仅买入
gmgn-cli track kol --chain sol --side buy --limit 10 --raw

# Smart Money 交易记录（SOL，默认）
gmgn-cli track smartmoney --limit 10 --raw

# Smart Money 交易记录，仅卖出
gmgn-cli track smartmoney --chain sol --side sell --limit 10 --raw
```

## `track follow-tokens` 选项

| 选项 | 描述 |
|--------|-------------|
| `--chain` | 必须的。`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--wallet <address>` | 必须的。要查询的钱包地址 |
| `--group-id <id>` | 按组筛选：`all_group`（所有组中的代币）、`default`（默认组）或用户定义的组 ID |
| `--interval <interval>` | 价格变化统计的时间间隔（例如 `1m`、`5m`、`1h`、`6h`、`24h`） |
| `--order-by <field>` | 排序字段：`created_at` / `swaps` / `volume` / `market_cap` / `liquidity` / `price` / `open_timestamp` |
| `--direction <dir>` | 当 `--order-by` 设置时必须的。`asc` / `desc` |
| `--limit <n>` | 页面大小 |
| `--cursor <cursor>` | 之前响应中的分页游标 |
| `--search <text>` | 通过代币名称或地址搜索 |

## `track follow-tokens` 响应字段

顶级字段：

| 字段 | 描述 |
|-------|-------------|
| `cursor` | 用于获取下一页的透明游标 |
| `all_following` | 关注的代币总数 |
| `is_recommend` | 结果是否包含推荐代币 |
| `followings` | 关注代币对象数组 |

`followings` 中的每个项目包含：

| 字段 | 描述 |
|-------|-------------|
| `address` | 代币合约地址 |
| `symbol` | 代币代码 |
| `name` | 代币名称 |
| `chain` | 代币所在的链 |
| `price` | 当前代币价格 |
| `price_change_percent` | 价格变化百分比 |
| `volume` | 交易量 |
| `liquidity` | 池流动性 |
| `market_cap` | 市值 |
| `swaps` | 总交易次数 |
| `group_ids` | 此代币所属的跟随组 |
| `open_timestamp` | 交易开启的 Unix 时间戳 |

## `track follow-token-groups` 选项

| 选项 | 描述 |
|--------|-------------|
| `--chain` | 必须的。`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--wallet <address>` | 必须的。要查询的钱包地址 |

## `track follow-token-groups` 响应字段

`data` 是一个数组。每个项目包含：

| 字段 | 描述 |
|-------|-------------|
| `chain` | 组所在的链 |
| `group_id` | 组标识符（例如 `default`，或用户定义的 ID） |
| `group_name` | 人类可读的组名称 |
| `rank` | 显示顺序/排序排名 |

## `track follow-wallet` 选项

| 选项 | 描述 |
|--------|-------------|
| `--chain` | 必须的。`sol` / `bsc` / `base` / `eth` / `arbitrum` / `hyperevm` / `robinhood` / `arc` / `stable` |
| `--wallet <address>` | 按钱包地址筛选 |
| `--limit <n>` | 页面大小（1–100，默认 10） |
| `--side <side>` | 交易方向：`buy` / `sell` |
| `--filter <tag...>` | 可重复的筛选条件 |
| `--min-amount-usd <n>` | 最小交易金额（美元） |
| `--max-amount-usd <n>` | 最大交易金额（美元） |

## `track kol` / `track smartmoney` 选项

| 选项 | 描述 |
|--------|-------------|
| `--chain <chain>` | 必须的。链：`sol` / `bsc` / `base` / `eth` |
| `--limit <n>` | 页面大小（1–200，默认 100） |
| `--side <side>` | 按交易方向筛选：`buy` / `sell`（客户端筛选——在获取结果后本地应用） |

## `track follow-wallet` 响应字段

顶级字段：

| 字段 | 描述 |
|-------|-------------|
| `next_page_token` | 用于获取下一页结果的透明标记 |
| `list` | 交易记录数组 |

`list` 中的每个项目包含：

| 字段 | 描述 |
|-------|-------------|
| `id` | 记录 ID（base64 编码，用作游标） |
| `chain` | 链名称（例如 `sol`） |
| `transaction_hash` | 链上交易哈希 |
| `maker` | 跟踪的钱包地址 |
| `side` | 交易方向：`buy` 或 `sell` |
| `base_address` | 代币合约地址 |
| `quote_address` | 报价代币地址（在 SOL 上的买入/卖出） |
| `base_amount` | 代币数量（最小单位） |
| `quote_amount` | 报价代币金额（例如 SOL） |
| `amount_usd` | 交易价值（美元） |
| `cost_usd` | 与 `amount_usd` 相同——此交易腿的美元价值 |
| `buy_cost_usd` | 原始买入成本（美元）（如果此记录是买入本身则为 0） |
| `price` | 交易时以报价代币计价的代币价格 |
| `price_usd` | 交易时美元计价的代币价格 |
| `price_now` | 当前美元计价的代币价格 |
| `price_change` | 自交易以来的价格变化比率（例如 `6.66` = +666%） |
| `timestamp` | 交易的 Unix 时间戳 |
| `is_open_or_close` | `1` = 完全开仓或平仓；`0` = 部分加仓或减仓 |
| `launchpad` | 启动板显示名称（例如 `Pump.fun`） |
| `launchpad_platform` | 启动板平台标识符（例如 `Pump.fun`，`pump_agent`） |
| `migrated_pool_exchange` | 如果有的话，代币迁移到的 DEX（例如 `pump_amm`）；如果没有迁移则为空 |
| `base_token.symbol` | 代币代码 |
| `base_token.logo` | 代币标志图像 URL |
| `base_token.hot_level` | 热度级别（`0` = 正常，更高 = 趋势） |
| `base_token.total_supply` | 总代币供应量（字符串） |
| `base_token.token_create_time` | 代币创建的 Unix 时间戳 |
| `base_token.token_open_time` | 交易开启的 Unix 时间戳（如果尚未迁移/开启则为 0） |
| `maker_info.address` | 跟踪的钱包地址 |
| `maker_info.name` | 钱包显示名称 |
| `maker_info.twitter_username` | Twitter / X 用户名 |
| `maker_info.twitter_name` | Twitter / X 显示名称 |
| `maker_info.tags` | 钱包标签数组（例如 `["kol","gmgn"]`） |
| `maker_info.tag_rank` | 标签 → 该类别中的排名映射（例如 `{"kol": 854}`） |
| `balance_info` | 钱包代币余额信息；如果不可用则为 `null` |

## `track kol` / `track smartmoney` 响应字段

响应是一个包含 `list` 数组的对象。`list` 中的每个项目包含：

| 字段 | 描述 |
|-------|-------------|
| `transaction_hash` | 链上交易哈希 |
| `maker` | 交易者（KOL / Smart Money）的钱包地址 |
| `side` | 交易方向：`buy` 或 `sell` |
| `base_address` | 代币合约地址 |
| `base_token.symbol` | 代币代码 |
| `base_token.launchpad` | 启动板平台（例如 `pump`） |
| `amount_usd` | 交易价值（美元） |
| `token_amount` | 交易代币数量 |
| `price_usd` | 交易时美元计价的代币价格 |
| `buy_cost_usd` | 原始买入成本（美元）（如果此记录是买入则为 0） |
| `is_open_or_close` | `0` = 头寸开仓/加仓，`1` = 头寸平仓/减仓 |
| `timestamp` | 交易的 Unix 时间戳 |
| `maker_info.twitter_username` | KOL 的 Twitter 用户名 |
| `maker_info.tags` | 钱包标签（例如 `kol`、`smart_degen`、`photon`） |

## Smart Money 行为解释

收到交易数据后，使用这些框架进行分析，然后再呈现结果。不要只是列出交易——分析它们意味着什么。

### 1. 信号强度级别

| 级别 | 标准 |
|-------|----------|
| 弱 | 1 个 KOL 买入 |
| 中等 | 2–3 个 Smart Money 买入（相同方向），或 1 个 Smart Money 完全开仓 |
| 强 | ≥ 3 个 Smart Money 钱包在 30 分钟内相同方向（集群信号） |
| 非常强 | 集群信号 + 完全开仓 + KOL 加入相同交易 |

### 2. 阅读 `is_open_or_close` — 确认信号

该字段因子命令而异：

- **`follow-wallet`**：`1` = 完全开仓或平仓；`0` = 部分加仓或减仓。
- **`kol` / `smartmoney`**：`0` = 头寸开仓/加仓；`1` = 头寸平仓/减仓。

完全头寸事件（完全开仓或完全平仓）比部分加仓/减仓的确认信号更强。一个钱包开启一个完全新的头寸信号了高度自信。一个钱包进行完全平仓信号了他们完全退出——将此视为对该代币的潜在退出信号。

### 3. 使用 `price_change` 评估交易记录

`price_change` 是当前价格与交易时价格的比率：
- `price_change > 2` → 这笔钱包的交易表现良好（代币现在是交易时的 2 倍+）——强烈的确认信号
- `price_change 1–2` → 适度收益，交易在盈利
- `price_change < 1` → 交易处于亏损状态（当前价格低于入场价）

使用此方法构建一个钱包过去表现的模型，然后再根据其当前交易采取行动。

### 4. 集群信号检测

当多个交易在短时间内击中相同的 `base_address` 时，这是一个汇聚信号——比任何单个交易都更强。要识别：
- 按结果分组 `base_address`
- 计数相同的方向交易的不同 `maker` 地址
- 如果 ≥ 3 个不同的钱包在 ~30 分钟内买入同一代币 → 标记为 **集群信号**

来自 `smartmoney` 的集群信号比单独的 `kol` 更强。

### 5. Smart Money 数据中的警告标志

- **Smart Money 卖出** (`side = sell` + `is_open_or_close` = 完全平仓) → 退出信号——评估是否退出或减少头寸
- **仅 KOL 买入，没有 Smart_degen** → 社交炒作而没有基本面支持；风险更高
- **知名者买入 + Smart Money 同时卖出** → 分歧信号——内部人员可能正在分销到零售/KOL 需求；高风险
- **单个非常大的买入，没有后续** → 可能是偶发事件；等待其他钱包确认

## 输出格式

### `track follow-wallet` / `track kol` / `track smartmoney` — 交易摘要

以逆时间顺序的交易摘要呈现。不要直接输出原始 JSON。

```
{timestamp}  {side}  {base_token.symbol}  ${amount_usd}  by {maker_info.name or short address}
             [{tags}]  Price: ${price_usd}  |  Price now: ${price_now}  ({price_change}x since trade)
```

如果多个交易击中同一代币，请按代币分组。突出显示多个关注的钱包在短时间内以相同方向交易的模式（集群信号）。

对于 `follow-wallet`，还显示 `is_open_or_close`：将完全开仓/平仓与部分加仓/减仓明确区分。

### 集群信号摘要

在呈现交易摘要后，检查汇聚信号。如果 ≥ 2 个不同的钱包以相同方向交易同一代币，请显示摘要块：

```
⚡ 汇聚信号
──────────────────────────────────────────
TOKEN_X ({short_address})
  5 smart money 钱包 — 所有 BUY — $42,300 总额 — 在 15 分钟内
  信号强度：强

TOKEN_Y ({short_address})
  2 KOL 钱包 — BUY（完全开仓）— $8,100 总额
  信号强度：中等
```

对于强信号：在采取行动之前进行完整的代币研究——请参阅 [`docs/workflow-token-research.md`](../../docs/workflow-token-research.md)
对于中等信号：监控并等待更多钱包确认后再采取行动。

如果未检测到汇聚信号：输出“此结果集中未检测到汇聚信号。”

要研究 Smart Money 活动中出现的任何代币，请遵循 [`docs/workflow-token-research.md`](../../docs/workflow-token-research.md)

**Smart money 排行榜 / 钱包分析**：当用户询问“哪些 Smart Money 钱包最好跟随”、“按胜率排名钱包”或想要比较钱包表现时——使用 `track smartmoney` 收集活跃钱包地址，然后批量查询其统计数据 via `gmgn-portfolio stats`。完整工作流程：[`docs/workflow-smart-money-profile.md`](../../docs/workflow-smart-money-profile.md)

**每日简报**：当用户询问市场概述（“今天市场如何”、“Smart Money 今天在买什么”、“给我一个每日简报”）——结合 `track smartmoney` + `track kol` 与 `gmgn-market trending`。完整工作流程：[`docs/workflow-daily-brief.md`](../../docs/workflow-daily-brief.md)

## 安全限制

- **`follow-wallet` 会泄露您的关注列表**——结果会暴露您在 GMGN 上关注的钱包。不要在公共频道中分享原始输出。
- **`track kol` / `track smartmoney` 不会泄露任何个人数据**——这些仅使用 API Key 认证，并返回平台标记的公共钱包活动。安全共享原始输出。

## 注意事项

- `track follow-tokens` 使用现有认证（仅 API Key）；`--wallet` 是必须的
- `track follow-wallet` 使用签名认证（API Key + 私钥签名）；`track kol` 和 `track smartmoney` 使用现有认证（仅 API Key）
- `track follow-wallet` 返回在 GMGN 平台上关注的钱包的交易；关注列表自动从绑定到 API 密钥的 GMGN 用户账户解析——`--wallet` 是可选的
- 使用 `--raw` 获取单行 JSON 以进行进一步处理
- `track kol` / `track smartmoney` `--side` 是一个 **客户端筛选**——CLI 获取所有结果然后本地筛选；它**不会**发送到 API
