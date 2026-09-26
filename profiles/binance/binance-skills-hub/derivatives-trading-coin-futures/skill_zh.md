# Binance 期货交易技能

使用认证 API 端点在 Binance 上进行期货交易请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点                  | 描述                     | 必填   | 可选   | 认证   |
|---------------------|------------------------|--------|--------|--------|
| `/dapi/v1/account` (GET) | 账户信息 (USER_DATA)       | 无     | recvWindow | 是     |
| `/dapi/v1/balance` (GET) | 期货账户余额 (USER_DATA)     | 无     | recvWindow | 是     |
| `/dapi/v1/positionSide/dual` (GET) | 获取当前位置模式 (USER_DATA)   | 无     | recvWindow | 是     |
| `/dapi/v1/positionSide/dual` (POST) | 更改位置模式 (TRADE)       | dualSidePosition | recvWindow | 是     |
| `/dapi/v1/order/asyn` (GET) | 获取期货订单历史下载 ID (USER_DATA) | startTime, endTime | recvWindow | 是     |
| `/dapi/v1/trade/asyn` (GET) | 获取期货交易历史下载 ID (USER_DATA) | startTime, endTime | recvWindow | 是     |
| `/dapi/v1/income/asyn` (GET) | 获取期货交易历史下载 ID (USER_DATA) | startTime, endTime | recvWindow | 是     |
| `/dapi/v1/order/asyn/id` (GET) | 通过 ID 获取期货订单历史下载链接 (USER_DATA) | downloadId | recvWindow | 是     |
| `/dapi/v1/trade/asyn/id` (GET) | 通过 ID 获取期货交易下载链接 (USER_DATA) | downloadId | recvWindow | 是     |
| `/dapi/v1/income/asyn/id` (GET) | 通过 ID 获取期货交易历史下载链接 (USER_DATA) | downloadId | recvWindow | 是     |
| `/dapi/v1/income` (GET) | 获取收入历史 (USER_DATA)     | 无     | symbol, incomeType, startTime, endTime, page, limit, recvWindow | 是     |
| `/dapi/v1/leverageBracket` (GET) | 对应对的名义区间 (USER_DATA)   | 无     | pair, recvWindow | 是     |
| `/dapi/v2/leverageBracket` (GET) | 对应标的的名义区间 (USER_DATA)   | 无     | symbol, recvWindow | 是     |
| `/dapi/v1/commissionRate` (GET) | 用户佣金率 (USER_DATA)       | symbol | recvWindow | 是     |
| `/dapi/v1/ticker/24hr` (GET) | 24 小时 ticker 价格变动统计   | 无     | symbol, pair | 否     |
| `/futures/data/basis` (GET) | 基差                   | pair, contractType, period | limit, startTime, endTime | 否     |
| `/dapi/v1/time` (GET) | 检查服务器时间           | 无     | 无     | 否     |
| `/dapi/v1/aggTrades` (GET) | 压缩/聚合交易列表         | symbol | fromId, startTime, endTime, limit | 否     |
| `/dapi/v1/continuousKlines` (GET) | 连续合约 K 线/蜡烛图数据     | pair, contractType, interval | startTime, endTime, limit | 否     |
| `/dapi/v1/exchangeInfo` (GET) | 交易所信息               | 无     | 无     | 否     |
| `/dapi/v1/fundingInfo` (GET) | 获取资金费信息           | 无     | 无     | 否     |
| `/dapi/v1/fundingRate` (GET) | 获取永续期货资金费历史     | symbol | startTime, endTime, limit | 否     |
| `/dapi/v1/constituents` (GET) | 查询指数价格成分         | symbol | 无     | 否     |
| `/dapi/v1/indexPriceKlines` (GET) | 指数价格 K 线/蜡烛图数据     | pair, interval | startTime, endTime, limit | 否     |
| `/dapi/v1/premiumIndex` (GET) | 指数价格和市价           | 无     | symbol, pair | 否     |
| `/dapi/v1/klines` (GET) | K 线/蜡烛图数据           | symbol, interval | startTime, endTime, limit | 否     |
| `/futures/data/globalLongShortAccountRatio` (GET) | 长空比率               | pair, period | limit, startTime, endTime | 否     |
| `/dapi/v1/markPriceKlines` (GET) | 市价 K 线/蜡烛图数据         | symbol, interval | startTime, endTime, limit | 否     |
| `/dapi/v1/historicalTrades` (GET) | 查找旧交易 (MARKET_DATA)   | symbol | limit, fromId | 否     |
| `/futures/data/openInterestHist` (GET) | 开仓量统计             | pair, contractType, period | limit, startTime, endTime | 否     |
| `/dapi/v1/openInterest` (GET) | 开仓量                 | symbol | 无     | 否     |
| `/dapi/v1/depth` (GET) | 订单簿                 | symbol | limit | 否     |
| `/dapi/v1/premiumIndexKlines` (GET) | 精算指数 K 线数据         | symbol, interval | startTime, endTime, limit | 否     |
| `/dapi/v1/trades` (GET) | 最近交易列表           | symbol | limit | 否     |
| `/dapi/v1/ticker/bookTicker` (GET) | 标的订单簿快照         | 无     | symbol, pair | 否     |
| `/dapi/v1/ticker/price` (GET) | 标的价格快照           | 无     | symbol, pair | 否     |
| `/futures/data/takerBuySellVol` (GET) | 主动买入/卖出量         | pair, contractType, period | limit, startTime, endTime | 否     |
| `/dapi/v1/ping` (GET) | 测试连接性             | 无     | 无     | 否     |
| `/futures/data/topLongShortAccountRatio` (GET) | 顶级交易者长空比率 (账户)   | symbol, period | limit, startTime, endTime | 否     |
| `/futures/data/topLongShortPositionRatio` (GET) | 顶级交易者长空比率 (仓位)   | pair, period | limit, startTime, endTime | 否     |
| `/dapi/v1/pmAccountInfo` (GET) | 经典组合保证金账户信息 (USER_DATA) | asset | recvWindow | 是     |
| `/dapi/v1/userTrades` (GET) | 账户交易列表 (USER_DATA)     | 无     | symbol, pair, orderId, startTime, endTime, fromId, limit, recvWindow | 是     |
| `/dapi/v1/allOrders` (GET) | 所有订单 (USER_DATA)       | 无     | symbol, pair, orderId, startTime, endTime, limit, recvWindow | 是     |
| `/dapi/v1/countdownCancelAll` (POST) | 自动取消所有未成交订单 (TRADE) | symbol, countdownTime | recvWindow | 是     |
| `/dapi/v1/allOpenOrders` (DELETE) | 取消所有未成交订单 (TRADE)   | symbol | recvWindow | 是     |
| `/dapi/v1/batchOrders` (DELETE) | 取消多个订单 (TRADE)       | symbol | orderIdList, origClientOrderIdList, recvWindow | 是     |
| `/dapi/v1/batchOrders` (PUT) | 修改多个订单 (TRADE)       | batchOrders | recvWindow | 是     |
| `/dapi/v1/batchOrders` (POST) | 下达多个订单 (TRADE)       | batchOrders | recvWindow | 是     |
| `/dapi/v1/order` (DELETE) | 取消订单 (TRADE)         | symbol | orderId, origClientOrderId, recvWindow | 是     |
| `/dapi/v1/order` (PUT) | 修改订单 (TRADE)         | symbol, side | orderId, origClientOrderId, quantity, price, priceMatch, recvWindow | 是     |
| `/dapi/v1/order` (POST) | 新订单 (TRADE)         | symbol, side, type | positionSide, timeInForce, quantity, reduceOnly, price, newClientOrderId, stopPrice, closePosition, activationPrice, callbackRate, workingType, priceProtect, newOrderRespType, priceMatch, selfTradePreventionMode, recvWindow | 是     |
| `/dapi/v1/order` (GET) | 查询订单 (USER_DATA)       | symbol | orderId, origClientOrderId, recvWindow | 是     |
| `/dapi/v1/leverage` (POST) | 更改初始杠杆 (TRADE)       | symbol, leverage | recvWindow | 是     |
| `/dapi/v1/marginType` (POST) | 更改保证金类型 (TRADE)       | symbol, marginType | recvWindow | 是     |
| `/dapi/v1/openOrders` (GET) | 当前所有未成交订单 (USER_DATA) | 无     | symbol, pair, recvWindow | 是     |
| `/dapi/v1/orderAmendment` (GET) | 获取订单修改历史 (USER_DATA)   | symbol | orderId, origClientOrderId, startTime, endTime, limit, recvWindow | 是     |
| `/dapi/v1/positionMargin/history` (GET) | 获取仓位保证金变更历史 (TRADE) | symbol | type, startTime, endTime, limit, recvWindow | 是     |
| `/dapi/v1/positionMargin` (POST) | 修改隔离仓位保证金 (TRADE)   | symbol, amount, type | positionSide, recvWindow | 是     |
| `/dapi/v1/adlQuantile` (GET) | 仓位 ADL 分位数估计 (USER_DATA) | 无     | symbol, recvWindow | 是     |
| `/dapi/v1/positionRisk` (GET) | 仓位信息 (USER_DATA)       | 无     | marginAsset, pair, recvWindow | 是     |
| `/dapi/v1/openOrder` (GET) | 查询当前未成交订单 (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | 是     |
| `/dapi/v1/forceOrders` (GET) | 用户的强制订单 (USER_DATA)   | 无     | symbol, autoCloseType, startTime, endTime, limit, recvWindow | 是     |
| `/dapi/v1/listenKey` (DELETE) | 关闭用户数据流 (USER_STREAM) | 无     | 无     | 否     |
| `/dapi/v1/listenKey` (PUT) | 保持用户数据流活跃 (USER_STREAM) | 无     | 无     | 否     |
| `/dapi/v1/listenKey` (POST) | 启动用户数据流 (USER_STREAM) | 无     | 无     | 否     |

---

## 参数

### 常见参数

* **recvWindow**:  (例如，5000)
* **startTime**: 毫秒时间戳 (例如，1623319461670)
* **endTime**: 毫秒时间戳 (例如，1641782889000)
* **downloadId**: 通过下载 ID API 获取 (例如，1)
* **symbol**: 
* **incomeType**: "TRANSFER","WELCOME_BONUS", "FUNDING_FEE", "REALIZED_PNL", "COMMISSION", "INSURANCE_CLEAR", 和 "DELIVERED_SETTELMENT"
* **startTime**:  (例如，1623319461670)
* **endTime**:  (例如，1641782889000)
* **page**: 
* **limit**: 默认 100；最大 1000 (例如，100)
* **pair**: 
* **symbol**: 
* **pair**: BTCUSD
* **fromId**: 获取聚合交易的起始 ID (包含在内)。(例如，1)
* **asset**: 
* **orderId**:  (例如，1)
* **orderId**:  (例如，1)
* **countdownTime**: 倒计时时间，1000 为 1 秒。0 表示取消计时器
* **orderIdList**: 最大长度 10   例如. [1234567,2345678]
* **origClientOrderIdList**: 最大长度 10  例如. ["my_id_1","my_id_2"], 双引号进行编码。逗号后无空格。
* **origClientOrderId**:  (例如，1)
* **leverage**: 目标初始杠杆: 从 1 到 125 的整数
* **dualSidePosition**: "true": 套保模式；"false": 单向模式
* **type**: 1: 添加仓位保证金,2: 减少仓位保证金
* **amount**:  (例如，1.0)
* **batchOrders**: 订单列表。最大 5 个订单
* **quantity**: 以合约数量计量的数量，不能与 `closePosition`=`true` 同时发送 (例如，1.0)
* **price**:  (例如，1.0)
* **reduceOnly**: "true" 或 "false". 默认 "false". 不能在套保模式下发送；不能与 `closePosition`=`true`(全部关闭) 同时发送
* **newClientOrderId**: 在所有未成交订单中唯一的 ID。如果未发送，将自动生成。只能为符合以下规则的字符串: `^[\.A-Z\:/a-z0-9_-]{1,36}$` (例如，1)
* **stopPrice**: 与 `STOP/STOP_MARKET` 或 `TAKE_PROFIT/TAKE_PROFIT_MARKET` 订单一起使用。(例如，1.0)
* **closePosition**: `true`, `false`；全部关闭，与 `STOP_MARKET` 或 `TAKE_PROFIT_MARKET` 一起使用。
* **activationPrice**: 与 `TRAILING_STOP_MARKET` 订单一起使用，默认为最新价格(支持不同的 `workingType`) (例如，1.0)
* **callbackRate**: 与 `TRAILING_STOP_MARKET` 订单一起使用，最小 0.1，最大 10，其中 1 表示 1%
* **priceProtect**: "TRUE" 或 "FALSE", 默认 "FALSE"。与 `STOP/STOP_MARKET` 或 `TAKE_PROFIT/TAKE_PROFIT_MARKET` 订单一起使用。
* **batchOrders**: 订单列表。最大 5 个订单
* **marginAsset**: 


### 枚举

* **contractType**: PERPETUAL | CURRENT_QUARTER | NEXT_QUARTER | CURRENT_QUARTER_DELIVERING | NEXT_QUARTER_DELIVERING | PERPETUAL_DELIVERING
* **period**: 5m | 15m | 30m | 1h | 2h | 4h | 6h | 12h | 1d
* **interval**: 1m | 3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1w | 1M
* **marginType**: ISOLATED | CROSSED
* **positionSide**: BOTH | LONG | SHORT
* **type**: LIMIT | MARKET | STOP | STOP_MARKET | TAKE_PROFIT | TAKE_PROFIT_MARKET | TRAILING_STOP_MARKET
* **side**: BUY | SELL
* **priceMatch**: NONE | OPPONENT | OPPONENT_5 | OPPONENT_10 | OPPONENT_20 | QUEUE | QUEUE_5 | QUEUE_10 | QUEUE_20
* **timeInForce**: GTC | IOC | FOK | GTX
* **workingType**: MARK_PRICE | CONTRACT_PRICE
* **newOrderRespType**: ACK | RESULT
* **selfTradePreventionMode**: NONE | EXPIRE_TAKER | EXPIRE_BOTH | EXPIRE_MAKER
* **autoCloseType**: LIQUIDATION | ADL


## 认证

对于需要认证的端点，您需要提供 Binance API 凭证。
所需凭证：

* apiKey: 您的 Binance API 密钥 (用于请求头)
* secretKey: 您的 Binance API 密钥 (用于签名)

基本 URL:
* 主网: https://dapi.binance.com
* 测试网: https://testnet.binancefuture.com

## 安全

### 共享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试使用前两种方式自动检索凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，并且在他们这样做时代理应重新读取该文件。代理也可以使用前两种方法进行 HTTP 请求，而无需用户确认。

1. **环境变量**

仅搜索以下特定变量 (永远不要导出完整环境):

**授权环境变量**
- 主网: `BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`
- 测试网: `BINANCE_TESTNET_API_KEY` 和 `BINANCE_TESTNET_SECRET_KEY`

在单个 exec 调用中读取并使用，以便原始密钥永远不会进入代理的上下文:
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入到正在运行的实例中。如果您需要在不重新启动的情况下添加或更新凭证，请使用密钥文件 (见选项 2)。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` , `~/.env`，或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，永远不要源码完整文件:
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用: 搜索已知目录中的 .env (KEY=VALUE 格式然后原始行格式)
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

此文件可以随时更新而无需重新启动 OpenClaw，每次调用时都会重新读取密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，并且在您这样做时应该重新读取该文件。

3. **内联文件**

发送一个文件，其中内容格式如下:

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`, `env`, `export` 或设置没有特定变量名的命令
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定密钥 ('`^VARNAME='`)
* 永远不要将密钥文件源码到 shell 环境 (`source .env` 或 `. .env`)
* 仅读取当前任务所需的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制，如果它包含真实凭证 — 添加到 `.gitignore` 中

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

当向用户显示凭证时:
- **API 密钥:** 显示前 5 个字符 + 最后 4 个字符: `su1Qc...8akf`
- **密钥:** 总是遮盖，仅显示最后 5 个: `***...aws1`

请求凭证时的示例响应:
账户: main
API 密钥: su1Qc...8akf
密钥: ***...aws1
环境: 主网

### 列出账户

当列出账户时，仅显示名称和环境 — 永远不要显示密钥:
Binance 账户:
* main (主网/测试网)
* testnet-dev (测试网)
* futures-keys (主网)

### 主网中的交易

当在主网中执行交易时，始终在继续之前通过询问用户是否写入 "CONFIRM" 来确认。

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

1. 请求凭证: 遮盖密钥 (仅显示最后 5 个字符)
2. 列出账户: 显示名称和环境，永远不要显示密钥
3. 账户选择: 如果不明确，询问，默认为主账户
4. 当在主网进行交易时，通过询问用户是否写入 "CONFIRM" 来确认继续
5. 新凭证: 提示输入名称、环境和签名模式
6. 当请求需要签名时，如果请求不是订单，并且 API 密钥不描述为 `mainnet` 或 `testnet` 密钥，则尝试使用不同的基本 URL 发送请求，而无需询问用户。如果成功，则将密钥与相应环境一起存储。

## 添加新账户

当用户通过内联文件或消息提供新凭证时:

* 询问账户名称
* 询问: 主网, 测试网 
* 存储在 `TOOLS.md` 中，并遮盖显示确认 

## 签名请求

对于需要签名的交易端点:

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 构建包含所有参数的查询字符串，包括时间戳 (Unix ms)。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 secretKey 使用 HMAC SHA256、RSA 或 Ed25519 签名查询字符串 (取决于账户配置)。
5. 将签名附加到查询字符串。
6. 包含 `X-MBX-APIKEY` 头。

否则，不要执行步骤 4–6。

## 新客户订单 ID 

对于包含 `newClientOrderId` 参数的端点，值必须始终以 `agent-` 开头。如果未提供该参数，将自动生成 `agent-` 后跟 18 个随机字母数字字符。如果提供了值，它将被 `agent-` 前缀

示例: `agent-1a2b3c4d5e6f7g8h9i`

## 用户代理头

包含 `User-Agent` 头，如下面的字符串: `binance-derivatives-trading-coin-futures/1.1.0 (Skill)`

有关实现细节，请参阅 [`references/authentication.md`](./references/authentication.md)。
