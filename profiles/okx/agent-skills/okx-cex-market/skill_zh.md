# OKX CEX 市场数据 CLI

> **合规声明**：此技能仅提供原始市场数据。不包含任何策略、建议或优化逻辑。所有指标输出均为客观数值；解释和交易决策仍由用户自行负责。

OKX 公共市场数据：价格、订单簿、K线图、资金费率、未平仓合约量、合约信息和技术指标。所有命令均为**只读**，无需 API 凭证。

**技能路由**
- 市场数据 / 指标 → `okx-cex-market`（此技能）
- 账户余额 / 持仓 → `okx-cex-portfolio`
- 下单 / 取消订单 → `okx-cex-trade`
- **以方向性观点作为事件合约进行交易** → `okx-cex-trade`
- 市场情绪 / 最看涨-看跌的币种 → `okx-sentiment-tracker`
- 网格 / DCA 机器人 → `okx-cex-bot`

## 预检查

在运行任何命令前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置元数据中的 `metadata.version` 作为步骤 2 的参考。

## 安装

```bash
npm install -g @okx_ai/okx-trade-cli
okx market ticker BTC-USDT   # 验证
```

市场数据命令无论在模拟/实盘模式下都返回相同的公共数据——无需 API 凭证。如果用户配置文件中设置了 `demo=true` 且他们希望获取实盘数据上下文，可以使用 `--live` 确认他们处于实盘模式（它对公共市场数据无效，但可明确环境）。当与用户查询相关时，始终告知用户当前激活的环境（模拟或实盘）。运行任何市场命令前无需确认。向任何命令添加 `--json` 以获取原始 OKX API v5 响应。添加 `--env` 将输出包装为 `{"env", "profile", "data"}`。

---

## 命令索引

| # | 命令 | 描述 |
|---|---|---|
| 1 | `okx market ticker <instId>` | 最新价格、24 小时最高/最低/成交量/变化率 |
| 2 | `okx market tickers <instType>` | SPOT / SWAP / 期货 / 期权 的所有报价 |
| 3 | `okx market instruments --instType <type> [--instId <id>] [--uly <uly>] [--instFamily <fam>] [--seriesId <id>]` | 列出合约（instId、ctVal、lotSz、minSz、tickSz、状态）；期权需要 `--uly` 或 `--instFamily`；事件需要 `--seriesId` |
| 4 | `okx market orderbook <instId> [--sz <n>]` | 订单簿买单/卖单（默认每侧前 5 个，最大 400） |
| 5 | `okx market candles <instId> [--bar <bar>] [--limit <n>] [--after <ts>] [--before <ts>]` | OHLCV K线图（默认 `--bar 1m`）；自动路由到历史端点以获取 2021 年以来的数据；`--after` 分页回溯时间，`--before` 分页向前 |
| 6 | `okx market index-candles <instId> [--bar <bar>] [--limit <n>] [--history]` | 指标 OHLCV（使用 `BTC-USD` 而不是 `BTC-USDT`） |
| 7 | `okx market funding-rate <instId> [--history] [--limit <n>]` | 当前或历史资金费率（仅限 SWAP） |
| 8 | `okx market trades <instId> [--limit <n>]` | 近期公开交易 |
| 9 | `okx market mark-price --instType <type> [--instId <id>]` | 做市价（SWAP / 期货 / 期权） |
| 10 | `okx market index-ticker [--instId <id>] [--quoteCcy <ccy>]` | 指标价格（例如，BTC-USD） |
| 11 | `okx market price-limit <instId>` | 上限/下限价格（仅限 SWAP / 期货） |
| 12 | `okx market open-interest --instType <type> [--instId <id>]` | 合约和基础货币的未平仓合约量 |
| 13 | `okx market instruments-by-category --instCategory <3\|4\|5\|6\|7>` | 按资产类别发现合约：3=股票代币（AAPL/TSLA），4=金属（黄金/白银），5=大宗商品（石油/天然气），6=外汇（EUR/USD），7=债券 |
| 13† | `okx market stock-tokens` | **已弃用**——请使用 `instruments-by-category --instCategory 3` |
| 14 | `okx market filter --instType <SPOT\|SWAP\|FUTURES> [--sortBy <field>] [--sortOrder <asc\|desc>] [--limit <n>] [--baseCcy <ccy>] [--quoteCcy <ccy>] [--settleCcy <ccy>] [--instFamily <fam>] [--ctType <linear\|inverse>] [--minLast <n>] [--maxLast <n>] [--minChg24hPct <n>] [--maxChg24hPct <n>] [--minMarketCapUsd <n>] [--maxMarketCapUsd <n>] [--minVolUsd24h <n>] [--maxVolUsd24h <n>] [--minFundingRate <n>] [--maxFundingRate <n>] [--minOiUsd <n>] [--maxOiUsd <n>]` | 按多维标准筛选/排名合约（价格、成交量、OI、资金费率、市值）。打印 `Total: N` + 匹配合约的排名表格（仅当无匹配时显示 `No results`）。添加 `--json` 获取原始 OKX API v5 响应（结构不变） |
| 15 | `okx market oi-history <instId> [--bar <5m\|15m\|1H\|4H\|1D>] [--limit <n>] [--ts <ms>]` | 单个合约的 OI 历史时间序列，包含逐条 K 线的增量 |
| 16 | `okx market oi-change --instType <SWAP\|FUTURES> [--bar <5m\|15m\|1H\|4H\|1D>] [--sortBy <field>] [--sortOrder <asc\|desc>] [--limit <n>] [--minOiUsd <n>] [--minVolUsd24h <n>] [--minAbsOiDeltaPct <n>]` | 查找 OI 变化最大的合约（累积/分配扫描器） |
| 17 | `okx market indicator list` | 列出所有支持的指标名称和描述 |
| 18 | `okx market indicator <indicator> <instId> [--bar] [--params] [--list] [--limit] [--backtest-time]` | 技术指标值。对于基于周期的指标（ema/ma/wma/rsi/macd/bb/…），当省略 `--params` 时，CLI 会应用合理的默认周期（例如 EMA/RSI → `14`，MACD → `12,26,9`，BB → `20,2`），因此值会自动渲染而无需您指定参数；显式 `--params` 总是优先。如果未返回值，CLI 会打印可见提示（`try --params …`）——永远不会沉默。 |
| 19 | `okx market pair-spread <instIdA> <instIdB> [--bar <5m\|15m>] [--window <window>] [--backtest-time <ms>]` | 回溯窗口内的价差统计（绝对值+比率：均值/标准差/中位数/最小值/最大值）；支持回测模式 |

---

## 操作流程

### 第 1 步 — 确定数据类型并加载参考

| 用户意图 | 加载参考 |
|---|---|
| 价格、K线图、订单簿、近期交易 | `{baseDir}/references/price-data-commands.md` |
| 技术指标（RSI、MACD、EMA、BB、KDJ、SuperTrend、AHR999、Rainbow 等） | `{baseDir}/references/indicator-commands.md` |
| 资金费率、做市价、未平仓合约量、价格限制、指标报价 | `{baseDir}/references/derivatives-commands.md` |
| 筛选/排名合约；查找最大波动性、高 OI、高成交量合约 | 直接使用 `okx market filter` |
| 单个合约的 OI 历史时间序列 | 直接使用 `okx market oi-history` |
| OI 变化扫描器；查找 OI 变化大的合约 | 直接使用 `okx market oi-change` |
| 价差统计；均值回归/配对交易规模 | 直接使用 `okx market pair-spread` |
| 列出合约、发现股票代币、金属/大宗商品/外汇/债券、查找期权合约 ID | `{baseDir}/references/instrument-commands.md` |
| 多步或跨技能工作流；MCP 工具名称 | `{baseDir}/references/workflows.md` |

**事件合约不由此技能提供。**

| 用户询问 | 执行 |
|---|---|
| 资产如何移动——"BTC 是否上涨"、"15 分钟趋势是什么" | **在此处回答**，使用 K 线图 / 指标 |
| 方向以及他们是否可以交易它 | 在此处回答数据部分，然后命名 `okx-cex-trade` 以处理交易部分 |
| 交易事件合约——"在…上买入 YES/NO" | **路由到 `okx-cex-trade`**，此处不提供任何服务 |

切勿用其他产品替代事件合约——不是永续合约，不是期货头寸，不是作为合约请求的市场数据。如果您无法加载 `okx-cex-trade`，请说明并停止。

### 第 2 步 — 立即运行命令

所有市场数据命令都是只读的——无需确认。

### 第 3 步 — 无写入、无需验证

此技能中的所有命令都是只读的。

---

## 边缘情况

- **instId 格式**：SPOT `BTC-USDT` · SWAP `BTC-USDT-SWAP` · 期货 `BTC-USDT-250328` · 期权 `BTC-USD-250328-95000-C` · 指标 `BTC-USD` · 股票代币 `TSLA-USDT-SWAP` · 金属/大宗商品/外汇/债券：首先使用 `instruments-by-category` 发现有效的 instIds
- **期权列表**：`instruments --instType OPTION` 需要 `--uly BTC-USD` 或 `--instFamily BTC-USD`；如果未知，请先运行 `open-interest --instType OPTION` 以发现活跃的 instIds
- **事件列表**：`instruments --instType EVENTS` 需要 `--seriesId`（例如 `--seriesId BTC-ABOVE-DAILY`）；请先运行 `okx event series` 以发现有效的系列 ID
- **资金费率 / 价格限制**：仅限 SWAP · 做市价：仅限 SWAP / 期货 / 期权
- **K线图 `--bar`**：大写——`1H` 而不是 `1h`；使用 `--after <ts>` 分页回溯历史数据（回溯到 2021 年）；`index-candles` 支持 `--history` 以获取扩展历史
- **⚠️ 大范围历史数据**：在使用 `--after`/`--before` 获取前，估计 K 线数量 = `time_range_ms / bar_interval_ms`。如果估计 > 500，请告知用户估计数量并要求在继续前确认。这可防止无声填充上下文窗口。
- **指标 `--bar`**：使用 `1Dutc` 而不是 `1D`，`1Wutc` 而不是 `1W`——与 K 线图条值不同
- **`market filter` sortBy 值**：`last` `chg24hPct` `marketCapUsd` `volUsd24h` `fundingRate` `oiUsd` `listTime`——默认 `volUsd24h`
- **`market filter` ctType**：`linear` 或 `inverse`（仅限 SWAP/FUTURES）；SPOT 时省略
- **`market filter` quoteCcy**：支持逗号分隔列表，例如 `--quoteCcy USDT,USDC`
- **`market filter` SPOT + quoteCcy**：当 `--instType SPOT` 时，API 返回跨越 **所有** 报价货币（USDT、USDC、BTC、ETH 等）混合的结果——这会污染排序顺序并使结果膨胀。默认始终传递 `--quoteCcy USDT`，除非用户明确要求其他报价货币。
- **`market filter` chg24hPct**：值为百分比数字——`--minChg24hPct -5` 表示 -5%，`--maxChg24hPct 10` 表示 10%
- **`market oi-history` ts**：Unix ms 时间戳；返回 ts ≤ 此值的条形图以用于历史分页
- **`market oi-history` / `oi-change` bar**：有效值 `5m` `15m` `1H` `4H` `1D`——默认 `1H`。服务器接受大小写变体（`1h` == `1H`），但优先使用规范大小写。
- **`market oi-history` limit**：1–500（默认 50）
- **`market oi-change` instType**：仅支持 `SWAP` 或 `FUTURES`（不支持 SPOT）
- **`market oi-change` minAbsOiDeltaPct**：按绝对 OI 变化过滤——`1.0` 仅保留 `|oiDeltaPct| ≥ 1%` 的行
- **`market oi-change` sortBy 值**：`oiUsd` `oiDeltaUsd` `oiDeltaPct` `absOiDeltaPct` `volUsd24h` `fundingRate` `last`——默认 `oiDeltaPct`（带符号）。使用 `absOiDeltaPct` 按绝对值排序（无论方向大小）。
- **`market oi-change` limit**：1–100（默认 20）。对于超过 100 行的情况，逐个 instId 获取 `oi-history`。
- **指标 `--bar` 有效值**：`3m` `5m` `15m` `1H` `4H` `12Hutc` `1Dutc` `3Dutc` `1Wutc`——`1m` **不支持**用于指标（使用 `candles` 获取 1 分钟数据）
- **指标 `--limit**：1–100（仅用于 `returnList`，即请求历史序列时）
- **指标参数顺序**：指标名称在前，instId 在后——`okx market indicator rsi BTC-USDT`
- **指标 `--params**：逗号分隔，无空格——`--params 5,20`。对于基于周期的指标（ema/ma/wma/rsi/macd/bb/…），省略 `--params` 会使 CLI 替换默认周期（EMA/MA/WMA/RSI → `14`，MACD → `12,26,9`，BB → `20,2`）以填充表格而不是空白；显式传递 `--params` 以覆盖默认值。（CLI 仅便利性——MCP 的 `market_get_indicator` 原始数据路径仍需要显式的 `paramList`。）
- **指标未返回值**：CLI 从不打印空白——如果查询未返回值（例如非周期指标，或周期指标无默认值），它会打印可见提示：`No indicator values returned. This indicator may require a period — try --params (e.g. --params 14).`
- **BTC 仅指标**：`ahr999`，`rainbow`——仅 BTC-USDT
- **未知指标名称**：在调用 API 之前返回 `ValidationError` 并提供类似名称建议——使用 `market_list_indicators` / `okx market indicator list` 查看所有有效名称
- **股票代币交易时间**：美国股票交易周一至周五约 09:30–16:00 ET；在行动前验证实时价格
- **无数据返回**：合约可能已退市——使用 `okx market instruments` 验证
- **`boll`** 是 `bb` 的别名

## 全局说明

- 此技能中的任何命令都不需要 API 密钥
- 速率限制：每 2 秒 20 个请求/IP
- K线图数据按最新优先排序
- `vol24h` 为基础货币（例如，BTC 对于 BTC-USDT）
- `--demo`/`--live` 和 `--profile` 不通过 CLI 影响 市场数据结果（公共端点）；它们仅确定激活的交易环境上下文
