# Upbit 技能

使用 `upbit` CLI 二进制文件进行所有 Upbit REST API 交互。

## ⚠️ Onboarding — 当凭证缺失时

当 `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY` 未设置，或认证命令返回 401：

**在单次交互中，按以下顺序执行所有以下操作：**

1. 调用 `bash("curl -s https://api.ipify.org")` 获取出站 IP。
2. 在回复文本中写入以下设置说明（将 `<ip>` 替换为步骤 1 中的真实 IP）：

---

### 第 1 步 — 在 Upbit 上允许此 IP
Upbit 仅接受来自您明确允许的 IP 地址的 API 调用。添加此 IP：
```
<ip>
```

### 第 2 步 — 创建 API 密钥
1. 登录到 [upbit.com](https://upbit.com) → 个人资料 → **API 管理**
2. 点击 **API 密钥发行** (Issue API Key)
3. 当提示输入 IP 时，粘贴 `<ip>`
4. 启用范围：
   - **资产查询** (View assets) — 始终需要
   - **订单查询** (View orders) — 需要
   - **订单创建** (Place orders) — 需要交易
   - **提现** (Withdraw) — 仅当您需要提现支持时
5. 完成 2FA + 邮箱验证，然后复制您的 **访问密钥** 和 **密钥**

### 第 3 步 — 输入您的密钥
在以下安全输入卡片中输入您的访问密钥和密钥。

---

## 语言行为

检测用户的语言并相应地回复：

- **韩语用户**：使用韩语回复，使用 `references/glossary.md` 中的韩语术语（例如，订单，买入，余额，成交，报价）
- **英语用户**：使用英语回复，使用相同的词汇表
- **混合/模糊**：遵循最新消息的语言

在解释 API 字段或命令输出时，始终使用词汇表将字段名翻译成用户的语言。例如，如果用户使用韩语，将 `bid` 解释为“买入”，`ask` 解释为“卖出”，`balance` 解释为“持有余额”。

加载 `references/glossary.md` 进行术语翻译或解释响应字段。

## 设置

如果 `upbit` 未安装或凭证未配置，加载 `references/setup.md` 并按照其中的步骤操作。

检查 `upbit` 是否可用：

```bash
upbit --version
```

## 认证

私有端点需要凭证。通过 CLI 配置（推荐）：

```bash
upbit config set
```

凭证保存在 `~/.upbit/config` 中，并自动用于所有 CLI 命令。

或者，通过环境变量设置：

```bash
export UPBIT_ACCESS_KEY=<your-access-key>
export UPBIT_SECRET_KEY=<your-secret-key>
```

或者，按命令传递内联：

```bash
upbit <resource> <command> --access-key <key> --secret-key <secret>
```

**私有**（需要认证）：`accounts`，`api-keys`，`orders`，`withdraws`，`deposits`，`travel-rule`，`wallet-status`
**公共**（无需认证）：`tickers`，`orderbooks`，`trades`，`candles`，`trading-pairs`

## 安全规则 — 写入操作

在执行任何写入操作之前，显示完整命令并要求用户输入 `CONFIRM`。

写入操作：
- `orders create`，`orders cancel`，`orders cancel-and-new`，`orders cancel-by-uuids`，`orders cancel-open`
- `withdraws create-withdrawal`，`withdraws create-krw-withdrawal`，`withdraws cancel-withdrawal`
- `deposits deposit-krw`，`deposits create-coin-address`
- `travel-rule verify-deposit-by-txid`，`travel-rule verify-deposit-by-uuid`

`orders test-create` 是一个干运行——无需 `CONFIRM`。

## Upbit 域概念

### 市场对格式

- 字段名：`market`
- 格式：`{报价货币}-{基础资产}`——报价货币在前，基础资产在后
- 分隔符：连字符（`-`），不是斜杠（`/`）
- 始终大写
- 报价货币：`KRW`，`BTC`，`USDT`
- **不是** `{基础资产}-{报价货币}` 或 `{基础资产}/{报价货币}`——Upbit 逆转了大多数交易所使用的常规顺序

| 市场 | 含义 |
|---|---|
| `KRW-BTC` | BTC 以 KRW 计价；Upbit 使用 `KRW-BTC`，不是 `BTC/KRW` 或 `BTC-KRW` |
| `KRW-ETH` | ETH 以 KRW 计价 |
| `KRW-XRP` | XRP 以 KRW 计价 |
| `BTC-ETH` | ETH 以 BTC 计价 |
| `USDT-XRP` | XRP 以 USDT 计价 |

### 账户余额字段

`accounts list` 的每个条目：

| 字段 | 描述 |
|---|---|
| `currency` | 资产代码（例如，`KRW`，`BTC`，`ETH`） |
| `balance` | 可用余额（不在任何未成交订单中） |
| `locked` | 当前锁定在未成交订单或提现中的余额 |
| `avg_buy_price` | 平均购买价格（十进制字符串） |
| `unit_currency` | `avg_buy_price` 计价的货币（例如，`KRW`，`BTC`） |

总持有量 = `balance` + `locked`

### 订单类型 (`ord_type`)

| `ord_type` | 描述 | 需要 | 不能设置 |
|---|---|---|---|
| `limit` | 在指定价格下限价订单 | `price`，`volume` | — |
| `price` | 市场买入——花费固定报价金额 | `price` | `volume` |
| `market` | 市场卖出——卖出固定基础金额 | `volume` | `price` |
| `best` | 最佳可用价格（见规则） | 见下文 | 见下文 |

**`best` 订单规则**：
- `time_in_force` 必须是 `ioc` 或 `fok`（不是 `post_only`）
- 如果 `side=bid`（买入）：需要 `price`，必须省略 `volume`
- 如果 `side=ask`（卖出）：需要 `volume`，必须省略 `price`

**`post_only` + `smp_type` 冲突**：这两者是互斥的——不要同时设置。

### 方向值

| `side` | 含义 |
|---|---|
| `bid` | 买入 |
| `ask` | 卖出 |

### 订单状态

| 状态 | 含义 |
|---|---|
| `wait` | 待执行 |
| `watch` | 待保留（停止订单） |
| `done` | 已完全执行 |
| `cancel` | 已取消 |

### 订单费用字段

| 字段 | 描述 |
|---|---|
| `reserved_fee` | 订单创建时保留的总费用 |
| `paid_fee` | 已收取的费用（用于部分成交） |
| `remaining_fee` | `reserved_fee - paid_fee` |
| `locked` | 为此订单锁定的金额（买入的报价货币，卖出的基础资产） |

### 首次订单创建

在向不熟悉的市域能够创建订单之前，运行 `orders retrieve-chance` 以确认：
- 最小订单金额 (`bid.min_total`，`ask.min_total`)
- 支持的订单类型 (`bid_types`，`ask_types`)
- 费用率 (`bid_fee`，`ask_fee`，`maker_bid_fee`，`maker_ask_fee`)

```bash
upbit orders retrieve-chance --market "KRW-BTC"
```

### 提现 — 多链资产

对于在多个网络上可用的资产（例如，USDT），需要 `net_type` 指定区块链。在提现前使用 `withdraws list-coin-addresses` 查看支持的网络和地址：

```bash
upbit withdraws list-coin-addresses --currency "USDT"
```

### 提现 — 次要地址

某些资产除了主地址外，还需要次要地址（目标标签、备忘等）。始终通过 `withdraws list-coin-addresses` 检查注册地址，以查看是否存在 `secondary_address`，然后再发送。

### 提现 — 未注册地址 (`withdraw_address_not_registered`)

当 `withdraws create-withdrawal` 返回 400 错误并带有 `name: withdraw_address_not_registered` 时，该地址尚未在 Upbit Open API 提现允许列表中注册。

要注册提现地址，请访问您环境的允许列表管理页面：

| 环境 | URL |
|---|---|
| KR | https://www.upbit.com/mypage/open_api_management/withdraw_access_register |
| SG | https://sg.upbit.com/mypage/open_api_management/withdraw_access_register |
| ID | https://id.upbit.com/mypage/open_api_management/withdraw_access_register |
| TH | https://th.upbit.com/mypage/open_api_management/withdraw_access_register |

注册后，运行 `withdraws list-coin-addresses` 确认地址出现，然后重试。

### 存入/提现状态

| 状态 | 含义 |
|---|---|
| `PROCESSING` | 进行中 |
| `ACCEPTED` | 已完成 |
| `CANCELLED` | 已取消 |
| `REJECTED` | 已拒绝 |
| `TRAVEL_RULE_SUSPECTED` | 等待 Travel Rule 验证 |
| `REFUNDING` | 退款进行中 |
| `REFUNDED` | 退款完成 |

当存款处于 `TRAVEL_RULE_SUSPECTED` 状态时，使用 `travel-rule` 命令进行验证。

### 钱包状态

`wallet-status list` 返回按资产的网络状态：

| `wallet_state` | 含义 |
|---|---|
| `working` | 存入和提现均可用 |
| `withdraw_only` | 存入暂停 |
| `deposit_only` | 提现暂停 |
| `paused` | 均暂停 |
| `unsupported` | 不支持 |

### 蜡烛单位与限制

- 分钟蜡烛：仅支持单位 `1, 3, 5, 10, 15, 30, 60, 240`
- 秒蜡烛：数据保留最长 3 个月（更旧的查询返回空数组）
- `count`：默认 1，每请求最多 200

### 交易分页

- `count`：每请求最多 500
- `cursor`：传递最后一个结果中的 `sequential_id` 以向前翻页
- `days_ago`：整数 1–7（基于 UTC 的日偏移）

### 贴水键字段

| 字段 | 描述 |
|---|---|
| `trade_price` | 当前（最后）价格 |
| `acc_trade_price_24h` | 24 小时累计交易价值 |
| `acc_trade_volume_24h` | 24 小时累计交易量 |
| `change` | `RISE`，`EVEN` 或 `FALL` 与前一天收盘价比较 |
| `signed_change_price` | 签名的绝对变化（下跌时为负） |
| `highest_52_week_price` / `lowest_52_week_price` | 52 周范围 |

### 价格方向枚举 (`change`，`ask_bid`)

| `change` 值 | 含义 |
|---|---|
| `RISE` | 价格高于前一天收盘价 |
| `EVEN` | 与前一天收盘价相同 |
| `FALL` | 价格低于前一天收盘价 |

| `ask_bid` 值 | 含义 |
|---|---|
| `ASK` | 由卖单发起的交易 |
| `BID` | 由买单发起的交易 |

### 单位与格式

| 值 | 单位 | 格式 |
|---|---|---|
| `volume` | 基础资产数量 | 十进制字符串（例如，`"0.01"`） |
| `price` (limit) | 报价货币中的每单位价格 | 十进制字符串（例如，`"140000000"`） |
| `price` (market buy) | 花费的总报价金额 | 十进制字符串（例如，`"10000"`） |
| 费用字段 | 报价货币金额 | 十进制字符串 |
| `timestamp` | 自纪元以来的毫秒 | 整数 |
| `created_at` / `done_at` | ISO 8601 带有 KST 偏移 | 字符串（例如，`2024-01-01T09:00:00+09:00`） |
| `trade_date` | UTC 日期 | 字符串 `yyyyMMdd` |
| `trade_time` | UTC 时间 | 字符串 `HHmmss`（24 小时制） |
| 费用率 | 十进制（0.05% = `"0.0005"`） | 十进制字符串 |

日界线（开盘价、acc_trade_price 等）基于 **UTC 00:00**，不是 KST。

## 命令参考

当您需要某个资源详细标志信息时，请阅读相应的参考文件。

| 资源 | 子命令 | 参考 |
|---|---|---|
| `orders` | create，test-create，retrieve，list-open，list-closed，list-by-uuids，cancel，cancel-and-new，cancel-by-uuids，cancel-open，retrieve-chance | [`references/orders.md`](references/orders.md) |
| `tickers` | list-by-quote-currencies，list-by-trading-pairs | [`references/tickers.md`](references/tickers.md) |
| `candles` | list-minutes，list-days，list-weeks，list-months，list-years，list-seconds | [`references/candles.md`](references/candles.md) |
| `orderbooks` | list，list-instruments | [`references/orderbooks.md`](references/orderbooks.md) |
| `trades` | list | [`references/trades.md`](references/trades.md) |
| `trading-pairs` | list | [`references/trading-pairs.md`](references/trading-pairs.md) |
| `withdraws` | retrieve，list，cancel-withdrawal，create-withdrawal，create-krw-withdrawal，list-coin-addresses，retrieve-chance | [`references/withdraws.md`](references/withdraws.md) |
| `deposits` | retrieve，list，create-coin-address，deposit-krw，list-coin-addresses，retrieve-chance，retrieve-coin-address | [`references/deposits.md`](references/deposits.md) |
| `travel-rule` | list-vasps，verify-deposit-by-txid，verify-deposit-by-uuid | [`references/travel-rule.md`](references/travel-rule.md) |
| `accounts` / `api-keys` / `wallet-status` | list | [`references/account.md`](references/account.md) |
| 输出 & 过滤 | --format，--transform，GJSON，debug，auto-paging | [`references/output.md`](references/output.md) |
| 韩语 ↔ 英语 词汇表 | 术语翻译，字段名韩语 ↔ 英语映射 | [`references/glossary.md`](references/glossary.md) |
| CLI 设置 & 凭证 | 安装，环境选择，API 密钥设置，config set | [`references/setup.md`](references/setup.md) |

对于参考文件中未列出的标志，运行：`upbit <resource> <command> --help`

## 环境

```bash
upbit accounts list                   # kr (默认)
upbit accounts list --environment sg  # sg | id | th
upbit accounts list --base-url <url>  # 自定义基础 URL
```
