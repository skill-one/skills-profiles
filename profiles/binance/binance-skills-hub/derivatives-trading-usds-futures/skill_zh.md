# Binance 期货交易-USDS 技能

使用经过身份验证的 API 端点在 Binance 上进行期货交易-USDS 请求。某些端点需要 API 密钥和密钥。以 JSON 格式返回结果。

## 快速参考

| 端点                     | 描述                     | 必填 | 可选 | 身份验证 |
| ------------------------ | ------------------------ | ---- | ---- | -------- |
| `/fapi/v1/accountConfig` (GET) | 期货账户配置(USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v2/account` (GET)   | 账户信息 V2(USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v3/account` (GET)   | 账户信息 V3(USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v2/balance` (GET)   | 期货账户余额 V2 (USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v3/balance` (GET)   | 期货账户余额 V3 (USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/apiTradingStatus` (GET) | 期货交易数量规则指标 (USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v1/feeBurn` (GET)   | 获取 BNB 燃烧状态 (USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/feeBurn` (POST)  | 在期货交易中切换 BNB 燃烧 (TRADE) | feeBurn | recvWindow | 是       |
| `/fapi/v1/multiAssetsMargin` (GET) | 获取当前多资产模式 (USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/multiAssetsMargin` (POST) | 更改多资产模式 (TRADE) | multiAssetsMargin | recvWindow | 是       |
| `/fapi/v1/positionSide/dual` (GET) | 获取当前头寸模式(USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/positionSide/dual` (POST) | 更改头寸模式(TRADE) | dualSidePosition | recvWindow | 是       |
| `/fapi/v1/order/asyn` (GET) | 获取期货订单历史下载 ID (USER_DATA) | startTime, endTime | recvWindow | 是       |
| `/fapi/v1/trade/asyn` (GET) | 获取期货交易历史下载 ID (USER_DATA) | startTime, endTime | recvWindow | 是       |
| `/fapi/v1/income/asyn` (GET) | 获取期货交易历史下载 ID(USER_DATA) | startTime, endTime | recvWindow | 是       |
| `/fapi/v1/order/asyn/id` (GET) | 通过 ID 获取期货订单历史下载链接 (USER_DATA) | downloadId | recvWindow | 是       |
| `/fapi/v1/trade/asyn/id` (GET) | 通过 ID 获取期货交易下载链接(USER_DATA) | downloadId | recvWindow | 是       |
| `/fapi/v1/income/asyn/id` (GET) | 通过 ID 获取期货交易历史下载链接 (USER_DATA) | downloadId | recvWindow | 是       |
| `/fapi/v1/income` (GET)     | 获取收入历史 (USER_DATA) | 无   | symbol, incomeType, startTime, endTime, page, limit, recvWindow | 是       |
| `/fapi/v1/leverageBracket` (GET) | 名义值和杠杆区间 (USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v1/rateLimit/order` (GET) | 查询用户速率限制 (USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/symbolConfig` (GET) | 符号配置(USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v1/commissionRate` (GET) | 用户佣金率 (USER_DATA) | symbol | recvWindow | 是       |
| `/fapi/v1/convert/acceptQuote` (POST) | 接受报价 (USER_DATA) | quoteId | recvWindow | 是       |
| `/fapi/v1/convert/exchangeInfo` (GET) | 列出所有转换对 | 无   | fromAsset, toAsset | 否       |
| `/fapi/v1/convert/orderStatus` (GET) | 订单状态(USER_DATA) | 无   | orderId, quoteId | 是       |
| `/fapi/v1/convert/getQuote` (POST) | 发送报价请求(USER_DATA) | fromAsset, toAsset | fromAmount, toAmount, validTime, recvWindow | 是       |
| `/fapi/v1/ticker/24hr` (GET) | 24 小时 ticker 价格变化统计 | 无   | symbol | 否       |
| `/fapi/v1/symbolAdlRisk` (GET) | ADL 风险 | 无   | symbol | 否       |
| `/futures/data/basis` (GET) | 基差 | pair, contractType, period, limit | startTime, endTime | 否       |
| `/fapi/v1/time` (GET)       | 检查服务器时间 | 无   | 无   | 否       |
| `/fapi/v1/indexInfo` (GET) | 复合指数符号信息 | 无   | symbol | 否       |
| `/fapi/v1/aggTrades` (GET) | 压缩/聚合交易列表 | symbol | fromId, startTime, endTime, limit | 否       |
| `/fapi/v1/continuousKlines` (GET) | 连续合约 K 线/蜡烛图数据 | pair, contractType, interval | startTime, endTime, limit | 否       |
| `/futures/data/delivery-price` (GET) | 季度合约结算价格 | pair | 无   | 否       |
| `/fapi/v1/exchangeInfo` (GET) | 交易所信息 | 无   | 无   | 否       |
| `/fapi/v1/fundingRate` (GET) | 获取资金费历史 | 无   | symbol, startTime, endTime, limit | 否       |
| `/fapi/v1/fundingInfo` (GET) | 获取资金费信息 | 无   | 无   | 否       |
| `/fapi/v1/constituents` (GET) | 查询指数价格成分 | symbol | 无   | 否       |
| `/fapi/v1/indexPriceKlines` (GET) | 指数价格 K 线/蜡烛图数据 | pair, interval | startTime, endTime, limit | 否       |
| `/fapi/v1/insuranceBalance` (GET) | 查询保险基金余额快照 | 无   | symbol | 否       |
| `/fapi/v1/klines` (GET)     | K 线/蜡烛图数据 | symbol, interval | startTime, endTime, limit | 否       |
| `/futures/data/globalLongShortAccountRatio` (GET) | 长空比率 | symbol, period | limit, startTime, endTime | 否       |
| `/fapi/v1/markPriceKlines` (GET) | 标记价格 K 线/蜡烛图数据 | symbol, interval | startTime, endTime, limit | 否       |
| `/fapi/v1/premiumIndex` (GET) | 标记价格 | 无   | symbol | 否       |
| `/fapi/v1/assetIndex` (GET) | 多资产模式资产指数 | 无   | symbol | 否       |
| `/fapi/v1/historicalTrades` (GET) | 旧交易查询 (MARKET_DATA) | symbol | limit, fromId | 否       |
| `/futures/data/openInterestHist` (GET) | 开仓量统计 | symbol, period | limit, startTime, endTime | 否       |
| `/fapi/v1/openInterest` (GET) | 开仓量 | symbol | 无   | 否       |
| `/fapi/v1/rpiDepth` (GET)   | RPI 订单簿 | symbol | limit | 否       |
| `/fapi/v1/depth` (GET)     | 订单簿 | symbol | limit | 否       |
| `/fapi/v1/premiumIndexKlines` (GET) | 精算指数 K 线数据 | symbol, interval | startTime, endTime, limit | 否       |
| `/fapi/v1/trades` (GET)     | 最近交易列表 | symbol | limit | 否       |
| `/fapi/v1/ticker/bookTicker` (GET) | 符号订单簿快照 | 无   | symbol | 否       |
| `/fapi/v2/ticker/price` (GET) | 符号价格快照 V2 | 无   | symbol | 否       |
| `/fapi/v1/ticker/price` (GET) | 符号价格快照 | 无   | symbol | 否       |
| `/futures/data/takerlongshortRatio` (GET) | 买卖量比率 | symbol, period | limit, startTime, endTime | 否       |
| `/fapi/v1/ping` (GET)       | 测试连接 | 无   | 无   | 否       |
| `/futures/data/topLongShortAccountRatio` (GET) | 顶级交易者长空比率 (账户) | symbol, period | limit, startTime, endTime | 否       |
| `/futures/data/topLongShortPositionRatio` (GET) | 顶级交易者长空比率 (头寸) | symbol, period | limit, startTime, endTime | 否       |
| `/fapi/v1/tradingSchedule` (GET) | 交易时间表 | 无   | 无   | 否       |
| `/fapi/v1/pmAccountInfo` (GET) | 经典组合保证金账户信息 (USER_DATA) | asset | recvWindow | 是       |
| `/fapi/v1/userTrades` (GET) | 账户交易列表 (USER_DATA) | symbol | orderId, startTime, endTime, fromId, limit, recvWindow | 是       |
| `/fapi/v1/allOrders` (GET) | 所有订单 (USER_DATA) | symbol | orderId, startTime, endTime, limit, recvWindow | 是       |
| `/fapi/v1/countdownCancelAll` (POST) | 自动取消所有未成交订单 (TRADE) | symbol, countdownTime | recvWindow | 是       |
| `/fapi/v1/algoOrder` (DELETE) | 取消算法订单 (TRADE) | 无   | algoId, clientAlgoId, recvWindow | 是       |
| `/fapi/v1/algoOrder` (POST) | 新算法订单(TRADE) | algoType, symbol, side, type | positionSide, timeInForce, quantity, price, triggerPrice, workingType, priceMatch, closePosition, priceProtect, reduceOnly, activatePrice, callbackRate, clientAlgoId, newOrderRespType, selfTradePreventionMode, goodTillDate, recvWindow | 是       |
| `/fapi/v1/algoOrder` (GET) | 查询算法订单 (USER_DATA) | 无   | algoId, clientAlgoId, recvWindow | 是       |
| `/fapi/v1/algoOpenOrders` (DELETE) | 取消所有算法未成交订单 (TRADE) | symbol | recvWindow | 是       |
| `/fapi/v1/allOpenOrders` (DELETE) | 取消所有未成交订单 (TRADE) | symbol | recvWindow | 是       |
| `/fapi/v1/batchOrders` (DELETE) | 取消多个订单 (TRADE) | symbol | orderIdList, origClientOrderIdList, recvWindow | 是       |
| `/fapi/v1/batchOrders` (PUT) | 修改多个订单(TRADE) | batchOrders | recvWindow | 是       |
| `/fapi/v1/batchOrders` (POST) | 下达多个订单(TRADE) | batchOrders | recvWindow | 是       |
| `/fapi/v1/order` (DELETE) | 取消订单 (TRADE) | symbol | orderId, origClientOrderId, recvWindow | 是       |
| `/fapi/v1/order` (PUT) | 修改订单 (TRADE) | symbol, side, quantity, price | orderId, origClientOrderId, priceMatch, recvWindow | 是       |
| `/fapi/v1/order` (POST) | 新订单(TRADE) | symbol, side, type | positionSide, timeInForce, quantity, reduceOnly, price, newClientOrderId, newOrderRespType, priceMatch, selfTradePreventionMode, goodTillDate, recvWindow | 是       |
| `/fapi/v1/order` (GET) | 查询订单 (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | 是       |
| `/fapi/v1/leverage` (POST) | 更改初始杠杆(TRADE) | symbol, leverage | recvWindow | 是       |
| `/fapi/v1/marginType` (POST) | 更改保证金类型(TRADE) | symbol, marginType | recvWindow | 是       |
| `/fapi/v1/openAlgoOrders` (GET) | 当前所有算法未成交订单 (USER_DATA) | 无   | algoType, symbol, algoId, recvWindow | 是       |
| `/fapi/v1/openOrders` (GET) | 当前所有未成交订单 (USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v1/orderAmendment` (GET) | 获取订单修改历史 (USER_DATA) | symbol | orderId, origClientOrderId, startTime, endTime, limit, recvWindow | 是       |
| `/fapi/v1/positionMargin/history` (GET) | 获取头寸保证金变更历史 (TRADE) | symbol | type, startTime, endTime, limit, recvWindow | 是       |
| `/fapi/v1/positionMargin` (POST) | 修改隔离头寸保证金(TRADE) | symbol, amount, type | positionSide, recvWindow | 是       |
| `/fapi/v1/order/test` (POST) | 测试订单(TRADE) | symbol, side, type | positionSide, timeInForce, quantity, reduceOnly, price, newClientOrderId, stopPrice, closePosition, activationPrice, callbackRate, workingType, priceProtect, newOrderRespType, priceMatch, selfTradePreventionMode, goodTillDate, recvWindow | 是       |
| `/fapi/v1/adlQuantile` (GET) | 头寸 ADL 分位数估计(USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v2/positionRisk` (GET) | 头寸信息 V2 (USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v3/positionRisk` (GET) | 头寸信息 V3 (USER_DATA) | 无   | symbol, recvWindow | 是       |
| `/fapi/v1/allAlgoOrders` (GET) | 查询所有算法订单 (USER_DATA) | symbol | algoId, startTime, endTime, page, limit, recvWindow | 是       |
| `/fapi/v1/openOrder` (GET) | 查询当前未成交订单 (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | 是       |
| `/fapi/v1/stock/contract` (POST) | 期货 TradFi Perps 合约(USER_DATA) | 无   | recvWindow | 是       |
| `/fapi/v1/forceOrders` (GET) | 用户的强制订单 (USER_DATA) | 无   | symbol, autoCloseType, startTime, endTime, limit, recvWindow | 是       |
| `/fapi/v1/listenKey` (DELETE) | 关闭用户数据流 (USER_STREAM) | 无   | 无   | 否       |
| `/fapi/v1/listenKey` (PUT) | 保持用户数据流活跃 (USER_STREAM) | 无   | 无   | 否       |
| `/fapi/v1/listenKey` (POST) | 启动用户数据流 (USER_STREAM) | 无   | 无   | 否       |

---

## 参数

### 常用参数

* **recvWindow**: (例如，5000)
* **symbol**: 
* **startTime**: 毫秒时间戳 (例如，1623319461670)
* **endTime**: 毫秒时间戳 (例如，1641782889000)
* **downloadId**: 通过下载 ID API 获取 (例如，1)
* **incomeType**: TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, COMMISSION, INSURANCE_CLEAR, REFERRAL_KICKBACK, COMMISSION_REBATE, API_REBATE, CONTEST_REWARD, CROSS_COLLATERAL_TRANSFER, OPTIONS_PREMIUM_FEE, OPTIONS_SETTLE_PROFIT, INTERNAL_TRANSFER, AUTO_EXCHANGE, DELIVERED_SETTELMENT, COIN_SWAP_DEPOSIT, COIN_SWAP_WITHDRAW, POSITION_LIMIT_INCREASE_FEE, STRATEGY_UMFUTURES_TRANSFER，FEE_RETURN，BFUSD_REWARD
* **startTime**: (例如，1623319461670)
* **endTime**: (例如，1641782889000)
* **page**: 
* **limit**: 默认 100；最大 1000 (例如，100)
* **feeBurn**: "true": 佣金折扣开启；"false": 佣金折扣关闭
* **symbol**: 
* **quoteId**: (例如，1)
* **fromAsset**: 用户花费的币种
* **toAsset**: 用户收到的币种
* **orderId**: 必须提供 orderId 或 quoteId 中的一个 (例如，1)
* **quoteId**: 必须提供 orderId 或 quoteId 中的一个 (例如，1)
* **fromAsset**: 
* **toAsset**: 
* **fromAmount**: 指定后，表示转换后扣除的金额 (例如，1.0)
* **toAmount**: 指定后，表示转换后 credited 的金额 (例如，1.0)
* **validTime**: 10s，默认 10s (例如，10s)
* **pair**: 
* **limit**: 默认 30，最大 500 (例如，30)
* **fromId**: 从 INCLUSIVE 获取聚合交易的 ID (例如，1)
* **asset**: 
* **orderId**: (例如，1)
* **countdownTime**: 倒计时时间，1000 为 1 秒。0 表示取消计时器
* **algoId**: (例如，1)
* **clientAlgoId**: (例如，1)
* **orderIdList**: 最大长度 10   e.g. [1234567,2345678]
* **origClientOrderIdList**: 最大长度 10  e.g. ["my_id_1","my_id_2"], encode the double quotes. No space after comma.
* **origClientOrderId**: (例如，1)
* **leverage**: 目标初始杠杆: 从 1 到 125 的整数值
* **multiAssetsMargin**: "true": 多资产模式；"false": 单一资产模式
* **dualSidePosition**: "true": 对冲模式；"false": 单向模式
* **algoType**: 
* **type**: 1: 添加头寸保证金，2: 减少头寸保证金
* **amount**: (例如，1.0)
* **type**: 
* **batchOrders**: 订单列表。最多 5 个订单
* **quantity**: 订单数量，不能与 `closePosition=true` 一起发送 (例如，1.0)
* **price**: (例如，1.0)
* **algoType**: 仅支持 `CONDITIONAL`
* **quantity**: (例如，1.0)
* **price**: (例如，1.0)
* **triggerPrice**: (例如，1.0)
* **closePosition**: `true`, `false`；全部关闭，与 `STOP_MARKET` 或 `TAKE_PROFIT_MARKET` 一起使用.
* **priceProtect**: "TRUE" 或 "FALSE", 默认 "FALSE". 与 `STOP/STOP_MARKET` 或 `TAKE_PROFIT/TAKE_PROFIT_MARKET` 订单一起使用.
* **reduceOnly**: "true" 或 "false". 默认 "false". 在对冲模式下不能发送
* **activatePrice**: 与 `TRAILING_STOP_MARKET` 订单一起使用，默认为最新价格(supporting different `workingType`) (例如，1.0)
* **callbackRate**: 与 `TRAILING_STOP_MARKET` 订单一起使用，最小 0.1，最大 5 其中 1 表示 1% (例如，1.0)
* **goodTillDate**: timeInForce `GTD` 的订单取消时间，设置 `timeInforce` 为 `GTD` 时必须; goodTillDate 时间戳仅保留秒级精度，毫秒部分将被忽略；goodTillDate 时间戳必须大于当前时间加 600 秒且小于 253402300799000
* **newClientOrderId**: 在所有未成交订单中唯一的 ID。如果未发送，将自动生成。只能遵循以下规则的字符串: `^[\.A-Z\:/a-z0-1-]{1,36}$` (例如，1)
* **stopPrice**: 与 `STOP/STOP_MARKET` 或 `TAKE_PROFIT/TAKE_PROFIT_MARKET` 订单一起使用。 (例如，1.0)
* **activationPrice**: 与 `TRAILING_STOP_MARKET` 订单一起使用，默认为最新价格(supporting different `workingType`) (例如，1.0)
* **batchOrders**: 订单列表。最多 5 个订单


### 枚举

* **contractType**: PERPETUAL | CURRENT_MONTH | NEXT_MONTH | CURRENT_QUARTER | NEXT_QUARTER | PERPETUAL_DELIVERING
* **period**: 5m | 15m | 30m | 1h | 2h | 4h | 6h | 12h | 1d
* **interval**: 1m | 3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1w | 1M
* **marginType**: ISOLATED | CROSSED
* **positionSide**: BOTH | LONG | SHORT
* **side**: BUY | SELL
* **priceMatch**: NONE | OPPONENT | OPPONENT_5 | OPPONENT_10 | OPPONENT_20 | QUEUE | QUEUE_5 | QUEUE_10 | QUEUE_20
* **timeInForce**: GTC | IOC | FOK | GTX | GTD | RPI
* **workingType**: MARK_PRICE | CONTRACT_PRICE
* **newOrderRespType**: ACK | RESULT
* **selfTradePreventionMode**: EXPIRE_TAKER | EXPIRE_BOTH | EXPIRE_MAKER
* **autoCloseType**: LIQUIDATION | ADL


## 身份验证

对于需要身份验证的端点，您需要提供 Binance API 凭证。
必需的凭证：

* apiKey: 您的 Binance API 密钥 (用于标题)
* secretKey: 您的 Binance API 密钥 (用于签名)

基本 URL：

* 主网: https://fapi.binance.com
* 测试网: https://demo-fapi.binance.com

## 安全

### 分享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试自动检索前两种方式中的凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理也可以使用前两种方法在不经用户确认的情况下进行 HTTP 请求。

1. **环境变量**

仅搜索以下特定变量（永远不要输出完整的环境）:

**授权环境变量**
- 主网: `BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`
- 测试网: `BINANCE_TESTNET_API_KEY` 和 `BINANCE_TESTNET_SECRET_KEY`

在一个 exec 调用中读取和使用，以便原始密钥永远不会进入代理的上下文:
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入到正在运行的实例中。如果您需要在重启之前添加或更新凭证，请使用密钥文件（见选项 2）。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` , `~/.env` 或工作区中的 `.env` 文件。使用 `grep` 读取单个密钥，永远不要输出完整文件:
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env (KEY=VALUE 格式然后原始行格式)
for dir in ~/.openclaw ~; do
  [ -n "$API_KEY" ] && break
  env_file="$dir/.env"
  [ -f "$env_file" ] || continue

  # 读取前两行
  line1=$(sed -n '1p' "$env_file")
  line2=$(sed -n '2p' "$env_file")

  # 检查行是否包含 '=' 表示 KEY=VALUE 格式
  if [[ "$line1" == *=* && "$line2" == *=* ]]; then
    API_KEY=$(grep '^BINANCE_API_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
    SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
  else
    # 将行视为原始值
    API_KEY="$line1"
    SECRET_KEY="$line2"
  fi
done
```

此文件可以随时更新而无需重启 OpenClaw，每次调用时都会读取新鲜的密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个文件，其内容格式如下:

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`, `env`, `export` 或设置没有特定变量名的命令
* 永远不要在没有锚定到特定键的 `env` 文件上运行 `grep` (`^VARNAME=`)
* 永远不要将密钥文件源代码到 shell 环境中 (`source .env` 或 `. .env`)
* 仅读取当前任务明确需要的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制中如果它包含真实凭证 — 将其添加到 `.gitignore`


### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

当向用户显示凭证时:
- **API Key:** 显示前 5 个字符加上最后 4 个字符: `su1Qc...8akf`
- **Secret Key:** 始终遮盖，仅显示最后 5 个字符: `***...aws1`

请求凭证时显示的示例响应:
Account: main
API Key: su1Qc...8akf
Secret: ***...aws1
环境: Mainnet

### 列出账户

当列出账户时，仅显示名称和环境 — 永远不要显示密钥:
Binance 账户:
* main (主网/测试网)
* testnet-dev (测试网)
* futures-keys (主网)


## 交易中的主网

当在主网执行交易时，始终在继续之前与用户确认，方法是要求他们写入 "CONFIRM" 继续。

---

## Binance 账户

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret
- Testnet: false 

### testnet-dev
- API Key: your_testnet_api_key
- Secret: your_testnet_secret
- Testnet: true

### TOOLS.md 结构

```bash
## Binance 账户

### main
- API Key: abc123...xyz
- Secret: secret123...key
- Testnet: false
- 描述: 主要交易账户

### testnet-dev
- API Key: test456...abc
- Secret: testsecret...xyz
- Testnet: true
- 描述: 开发/测试

### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- Testnet: false
- 描述: 期货交易账户
```

## 代理行为

1. 请求凭证: 遮盖密钥（仅显示最后 5 个字符）
2. 列出账户: 显示名称和环境，永远不要显示密钥
3. 账户选择: 如果不明确，询问，默认为主网
4. 当在主网进行交易时，在继续之前与用户确认，方法是要求他们写入 "CONFIRM" 继续
5. 新凭证: 提示输入名称、环境、签名模式
6. 当请求需要签名时，如果请求不是订单，并且 API 密钥不被描述为 `mainnet` 或 `testnet` 密钥，则尝试使用不同的基本 URL 进行请求，而无需询问用户。如果成功，则将密钥与相应环境一起存储。

## 添加新账户

当用户通过内联文件或消息提供新凭证时:

* 询问账户名称
* 询问: 主网, 测试网 
* 存储在 `TOOLS.md` 中，并确认遮盖显示 

## 签名请求

对于需要签名的交易端点:

1. **首先检测密钥类型**, 在签名之前检查密钥格式。
2. 构建包含所有参数的查询字符串，包括时间戳（Unix ms）。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 secretKey 使用 HMAC SHA256, RSA 或 Ed25519（取决于账户配置）对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包含 `X-MBX-APIKEY` 标题。

否则，不要执行步骤 4–6。

## 新客户端订单 ID 

对于包含 `newClientOrderId` 参数的端点，值必须始终以 `agent-` 开头。如果未提供参数，将自动生成 `agent-` 后跟 18 个随机字母数字字符。如果提供了值，它将被 `agent-` 前缀

示例: `agent-1a2b3c4d5e6f7g8h9i`

## 用户代理标题

包含 `User-Agent` 标题与以下字符串: `binance-derivatives-trading-usds-futures/1.1.0 (Skill)`

参见 [`references/authentication.md`](./references/authentication.md) 以获取实现细节。
