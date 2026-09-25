# Binance现货技能

使用认证API端点在Binance上进行现货请求。某些端点需要API密钥和密钥。以JSON格式返回结果。

## 快速参考

| 端点 | 描述 | 必需 | 可选 | 认证 |
|------|------|------|------|------|
| `/api/v3/exchangeInfo` (GET) | 交易所信息 | 无 | symbol, symbols, permissions, showPermissionSets, symbolStatus | 否 |
| `/api/v3/ping` (GET) | 测试连接性 | 无 | 无 | 否 |
| `/api/v3/time` (GET) | 检查服务器时间 | 无 | 无 | 否 |
| `/api/v3/aggTrades` (GET) | 压缩/聚合交易列表 | symbol | fromId, startTime, endTime, limit | 否 |
| `/api/v3/avgPrice` (GET) | 当前平均价格 | symbol | 无 | 否 |
| `/api/v3/depth` (GET) | 订单簿 | symbol | limit, symbolStatus | 否 |
| `/api/v3/historicalTrades` (GET) | 旧交易查询 | symbol | limit, fromId | 否 |
| `/api/v3/klines` (GET) | K线/蜡烛图数据 | symbol, interval | startTime, endTime, timeZone, limit | 否 |
| `/api/v3/ticker` (GET) | 滚动窗口价格变化统计 | 无 | symbol, symbols, windowSize, type, symbolStatus | 否 |
| `/api/v3/ticker/24hr` (GET) | 24小时 ticker 价格变化统计 | 无 | symbol, symbols, type, symbolStatus | 否 |
| `/api/v3/ticker/bookTicker` (GET) | 符号订单簿ticker | 无 | symbol, symbols, symbolStatus | 否 |
| `/api/v3/ticker/price` (GET) | 符号价格ticker | 无 | symbol, symbols, symbolStatus | 否 |
| `/api/v3/ticker/tradingDay` (GET) | 交易日Ticker | 无 | symbol, symbols, timeZone, type, symbolStatus | 否 |
| `/api/v3/trades` (GET) | 最近交易列表 | symbol | limit | 否 |
| `/api/v3/uiKlines` (GET) | UIKlines | symbol, interval | startTime, endTime, timeZone, limit | 否 |
| `/api/v3/openOrders` (DELETE) | 在符号上取消所有未成交订单 | symbol | recvWindow | 是 |
| `/api/v3/openOrders` (GET) | 当前未成交订单 | 无 | symbol, recvWindow | 是 |
| `/api/v3/order` (POST) | 新订单 | symbol, side, type | timeInForce, quantity, quoteOrderQty, price, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | 是 |
| `/api/v3/order` (DELETE) | 取消订单 | symbol | orderId, origClientOrderId, newClientOrderId, cancelRestrictions, recvWindow | 是 |
| `/api/v3/order` (GET) | 查询订单 | symbol | orderId, origClientOrderId, recvWindow | 是 |
| `/api/v3/order/amend/keepPriority` (PUT) | 订单修改保持优先级 | symbol, newQty | orderId, origClientOrderId, newClientOrderId, recvWindow | 是 |
| `/api/v3/order/cancelReplace` (POST) | 取消现有订单并发送新订单 | symbol, side, type, cancelReplaceMode | timeInForce, quantity, quoteOrderQty, price, cancelNewClientOrderId, cancelOrigClientOrderId, cancelOrderId, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, cancelRestrictions, orderRateLimitExceededMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | 是 |
| `/api/v3/order/oco` (POST) | 新OCO - 已弃用 | symbol, side, quantity, price, stopPrice | listClientOrderId, limitClientOrderId, limitStrategyId, limitStrategyType, limitIcebergQty, trailingDelta, stopClientOrderId, stopStrategyId, stopStrategyType, stopLimitPrice, stopIcebergQty, stopLimitTimeInForce, newOrderRespType, selfTradePreventionMode, recvWindow | 是 |
| `/api/v3/order/test` (POST) | 测试新订单 | symbol, side, type | computeCommissionRates, timeInForce, quantity, quoteOrderQty, price, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | 是 |
| `/api/v3/orderList` (DELETE) | 取消订单列表 | symbol | orderListId, listClientOrderId, newClientOrderId, recvWindow | 是 |
| `/api/v3/orderList` (GET) | 查询订单列表 | 无 | orderListId, origClientOrderId, recvWindow | 是 |
| `/api/v3/orderList/oco` (POST) | 新订单列表 - OCO | symbol, side, quantity, aboveType, belowType | listClientOrderId, aboveClientOrderId, aboveIcebergQty, abovePrice, aboveStopPrice, aboveTrailingDelta, aboveTimeInForce, aboveStrategyId, aboveStrategyType, abovePegPriceType, abovePegOffsetType, abovePegOffsetValue, belowClientOrderId, belowIcebergQty, belowPrice, belowStopPrice, belowTrailingDelta, belowTimeInForce, belowStrategyId, belowStrategyType, belowPegPriceType, belowPegOffsetType, belowPegOffsetValue, newOrderRespType, selfTradePreventionMode, recvWindow | 是 |
| `/api/v3/orderList/opo` (POST) | 新订单列表 - OPO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingType, pendingSide | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce, pendingStrategyId, pendingStrategyType, pendingPegPriceType, pendingPegOffsetType, pendingPegOffsetValue, recvWindow | 是 |
| `/api/v3/orderList/opoco` (POST) | 新订单列表 - OPOCO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingAboveType | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingAboveStrategyId, pendingAboveStrategyType, pendingAbovePegPriceType, pendingAbovePegOffsetType, pendingAbovePegOffsetValue, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce, pendingBelowStrategyId, pendingBelowStrategyType, pendingBelowPegPriceType, pendingBelowPegOffsetType, pendingBelowPegOffsetValue, recvWindow | 是 |
| `/api/v3/orderList/oto` (POST) | 新订单列表 - OTO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingType, pendingSide, pendingQuantity | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce, pendingStrategyId, pendingStrategyType, pendingPegPriceType, pendingPegOffsetType, pendingPegOffsetValue, recvWindow | 是 |
| `/api/v3/orderList/otoco` (POST) | 新订单列表 - OTOCO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingQuantity, pendingAboveType | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingAboveStrategyId, pendingAboveStrategyType, pendingAbovePegPriceType, pendingAbovePegOffsetType, pendingAbovePegOffsetValue, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce, pendingBelowStrategyId, pendingBelowStrategyType, pendingBelowPegPriceType, pendingBelowPegOffsetType, pendingBelowPegOffsetValue, recvWindow | 是 |
| `/api/v3/sor/order` (POST) | 使用SOR的新订单 | symbol, side, type, quantity | timeInForce, price, newClientOrderId, strategyId, strategyType, icebergQty, newOrderRespType, selfTradePreventionMode, recvWindow | 是 |
| `/api/v3/sor/order/test` (POST) | 使用SOR测试新订单 | symbol, side, type, quantity | computeCommissionRates, timeInForce, price, newClientOrderId, strategyId, strategyType, icebergQty, newOrderRespType, selfTradePreventionMode, recvWindow | 是 |
| `/api/v3/account` (GET) | 账户信息 | 无 | omitZeroBalances, recvWindow | 是 |
| `/api/v3/account/commission` (GET) | 查询佣金率 | symbol | 无 | 是 |
| `/api/v3/allOrderList` (GET) | 查询所有订单列表 | 无 | fromId, startTime, endTime, limit, recvWindow | 是 |
| `/api/v3/allOrders` (GET) | 所有订单 | symbol | orderId, startTime, endTime, limit, recvWindow | 是 |
| `/api/v3/myAllocations` (GET) | 查询分配 | symbol | startTime, endTime, fromAllocationId, limit, orderId, recvWindow | 是 |
| `/api/v3/myFilters` (GET) | 查询相关过滤器 | symbol | recvWindow | 是 |
| `/api/v3/myPreventedMatches` (GET) | 查询阻止匹配 | symbol | preventedMatchId, orderId, fromPreventedMatchId, limit, recvWindow | 是 |
| `/api/v3/myTrades` (GET) | 账户交易列表 | symbol | orderId, startTime, endTime, fromId, limit, recvWindow | 是 |
| `/api/v3/openOrderList` (GET) | 查询未成交订单列表 | 无 | recvWindow | 是 |
| `/api/v3/order/amendments` (GET) | 查询订单修改 | symbol, orderId | fromExecutionId, limit, recvWindow | 是 |
| `/api/v3/rateLimit/order` (GET) | 查询未成交订单数量 | 无 | recvWindow | 是 |

---

## 参数

### 常见参数

* **symbol**: 查询的符号 (例如，BNBUSDT)
* **symbols**: 查询的符号列表
* **permissions**: 查询的权限列表
* **showPermissionSets**: 控制是否填充 `permissionSets` 字段的内容。默认值为 `true` (例如，true)
* **symbol**:  (例如，BNBUSDT)
* **fromId**: 从包含的聚合交易ID (例如，1)
* **startTime**: 包含的聚合交易开始时间戳 (ms) (例如，1735693200000)
* **endTime**: 包含的聚合交易结束时间戳 (ms) (例如，1735693200000)
* **limit**: 默认：500；最大：1000 (例如，500)
* **timeZone**: 默认：0 (UTC)
* **recvWindow**: 值不能大于 `60000`。支持最多三位小数精度 (例如，5000.346) 以指定微秒。 (例如，5000)
* **timestamp**:  (例如，1)
* **quantity**:  (例如，1)
* **quoteOrderQty**:  (例如，1)
* **price**:  (例如，400)
* **newClientOrderId**: 在未成交订单中唯一的id。如果未发送，将自动生成。具有相同 `newClientOrderID` 的订单只有在之前一个订单成交后才能接受，否则订单将被拒绝。
* **strategyId**:  (例如，1)
* **strategyType**: 值不能小于 `1000000`。 (例如，1)
* **stopPrice**: 与 `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT` 和 `TAKE_PROFIT_LIMIT` 订单一起使用。 (例如，1)
* **trailingDelta**: 请参阅跟踪止损订单常见问题解答。 (例如，1)
* **icebergQty**: 与 `LIMIT`, `STOP_LOSS_LIMIT` 和 `TAKE_PROFIT_LIMIT` 一起使用以创建冰山订单。 (例如，1)
* **pegOffsetValue**: 价格水平以将价格固定在 (最大：100)。请参阅固定订单信息 (例如，1)
* **orderId**:  (例如，1)
* **origClientOrderId**: 
* **newQty**: `newQty` 必须大于 0 且小于订单的数量。 (例如，1)
* **cancelNewClientOrderId**: 用于唯一标识此取消。默认情况下自动生成。
* **cancelOrigClientOrderId**: 必须发送 `cancelOrderId` 或 `cancelOrigClientOrderId` 中的一个。 </br>如果同时提供 `cancelOrderId` 和 `cancelOrigClientOrderId` 参数，则首先搜索 `cancelOrderId`，然后检查该结果中的 `cancelOrigClientOrderId` 是否与该订单匹配。  </br>如果两个条件都不满足，则请求将被拒绝。
* **cancelOrderId**: 必须发送 `cancelOrderId` 或 `cancelOrigClientOrderId` 中的一个。 </br>如果同时提供 `cancelOrderId` 和 `cancelOrigClientOrderId` 参数，则首先搜索 `cancelOrderId`，然后检查该结果中的 `cancelOrigClientOrderId` 是否与该订单匹配。  </br>如果两个条件都不满足，则请求将被拒绝。 (例如，1)
* **listClientOrderId**: 订单列表的唯一ID
* **quantity**:  (例如，1)
* **limitClientOrderId**: 限制订单的唯一ID
* **price**:  (例如，1)
* **limitStrategyId**:  (例如，1)
* **limitStrategyType**: 值不能小于 `1000000`。 (例如，1)
* **limitIcebergQty**: 用于将 `LIMIT_MAKER` 腿设置为冰山订单。 (例如，1)
* **stopClientOrderId**: 止损/止损限价腿的唯一ID
* **stopPrice**:  (例如，1)
* **stopStrategyId**:  (例如，1)
* **stopStrategyType**: 值不能小于 `1000000`。 (例如，1)
* **stopLimitPrice**: 如果提供，则需要 `stopLimitTimeInForce`。 (例如，1)
* **stopIcebergQty**: 与 `STOP_LOSS_LIMIT` 腿一起使用以创建冰山订单。 (例如，1)
* **computeCommissionRates**: 默认：`false`   请参阅佣金常见问题解答以了解更多信息。
* **orderListId**: 必须提供 `orderListId` 或 `listClientOrderId` 中的一个 (例如，1)
* **aboveClientOrderId**: 未成交订单中任意唯一的ID。如果未发送，将自动生成。
* **aboveIcebergQty**: 注意，这只能在使用 `aboveTimeInForce` 为 `GTC` 时使用。 (例如，1)
* **abovePrice**: 如果 `aboveType` 是 `STOP_LOSS_LIMIT` , `LIMIT_MAKER` 或 `TAKE_PROFIT_LIMIT`，则可以用于指定限价。 (例如，1)
* **aboveStopPrice**: 如果 `aboveType` 是 `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT` 或 `TAKE_PROFIT_LIMIT`，则必须指定 `aboveStopPrice` 或 `aboveTrailingDelta` 或两者都指定。 (例如，1)
* **aboveTrailingDelta**: 请参阅跟踪止损常见问题解答。 (例如，1)
* **aboveStrategyId**: 在订单策略中标识上述订单的任意数值。 (例如，1)
* **aboveStrategyType**: 在订单策略中标识上述订单策略的任意数值。小于 1000000 的值被保留且不能使用。 (例如，1)
* **abovePegOffsetValue**:  (例如，1)
* **belowClientOrderId**: 未成交订单中任意唯一的ID。如果未发送，将自动生成。
* **belowIcebergQty**: 注意，这只能在使用 `belowTimeInForce` 为 `GTC` 时使用。 (例如，1)
* **belowPrice**: 如果 `belowType` 是 `STOP_LOSS_LIMIT` 或 `TAKE_PROFIT_LIMIT`，则可以用于指定限价 (例如，1)
* **belowStopPrice**: 如果 `belowType` 是 `STOP_LOSS`, `STOP_LOSS_LIMIT, TAKE_PROFIT` 或 `TAKE_PROFIT_LIMIT`，则必须指定 `belowStopPrice` 或 `belowTrailingDelta` 或两者都指定。 (例如，1)
* **belowTrailingDelta**:  (例如，1)
* **belowIcebergQty**: 这只能在使用 `belowTimeInForce` 为 `GTC` 或 `pendingType` 为 `LIMIT_MAKER` 时使用。 (例如，1)
* **belowStrategyId**: 在订单策略中标识上述订单的任意数值。 (例如，1)
* **belowStrategyType**: 在订单策略中标识上述订单策略的任意数值。小于 1000000 的值被保留且不能使用。 (例如，1)
* **belowPegOffsetValue**:  (例如，1)
* **workingType**: LIMIT | LIMIT_MAKER
* **workingPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **workingPegOffsetType**: PRICE_LEVEL
* **pendingPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingPegOffsetType**: PRICE_LEVEL
* **pendingAboveType**: STOP_LOSS_LIMIT | STOP_LOSS | LIMIT_MAKER | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **pendingAbovePegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingAbovePegOffsetType**: PRICE_LEVEL
* **pendingBelowType**: STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **pendingBelowPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingBelowPegOffsetType**: PRICE_LEVEL
* **workingSide**: BUY | SELL
* **workingTimeInForce**: GTC | IOC | FOK
* **pendingType**: LIMIT | MARKET | STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT | LIMIT_MAKER
* **pendingSide**: BUY | SELL
* **pendingTimeInForce**: GTC | IOC | FOK
* **pendingAboveTimeInForce**: GTC | IOC | FOK
* **pendingBelowTimeInForce**: GTC | IOC | FOK


## 认证

对于需要认证的端点，您需要提供Binance API凭证。
必需的凭证：

* apiKey: 您的Binance API密钥 (用于标头)
* secretKey: 您的Binance API密钥 (用于签名)

基本URL：

* 主网：https://api.binance.com
* 测试网：https://testnet.binance.vision
* 演示：https://demo-api.binance.com

## 安全

### 分享凭证

用户可以通过不同方式提供Binance API凭证。代理将尝试使用前两种方式自动检索凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在`.env`文件中，代理应在他们这样做时重新读取该文件。代理还可以使用前两种方法在不询问用户的情况下进行HTTP请求。

1. **环境变量**

仅搜索以下特定变量 (永远不要转储完整的环境):

**授权环境变量**
- 主网：`BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`
- 测试网：`BINANCE_TESTNET_API_KEY` 和 `BINANCE_TESTNET_SECRET_KEY`
- 演示：`BINANCE_DEMO_API_KEY` 和 `BINANCE_DEMO_SECRET_KEY`

在一个exec调用中读取和使用，以便原始密钥永远不会进入代理的上下文：
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在OpenClaw启动之前设置。它们在进程启动时继承，不能注入到正在运行的实例中。如果您需要在不重启的情况下添加或更新凭证，请使用密钥文件 (见选项2)。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` , `~/.env` 或工作区中的 `.env` 文件。使用 `grep` 读取单个密钥，永远不要转储完整文件：
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env (KEY=VALUE格式然后原始行格式)
for dir in ~/.openclaw ~; do
  [ -n "$API_KEY" ] && break
  env_file="$dir/.env"
  [ -f "$env_file" ] || continue

  # 读取前两行
  line1=$(sed -n '1p' "$env_file")
  line2=$(sed -n '2p' "$env_file")

  # 检查行是否包含 `=` 表示 KEY=VALUE 格式
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

此文件可以随时更新而无需重启OpenClaw，每次调用都会读取新鲜的密钥。用户可以告诉您变量已设置或存储在`.env`文件中，您应在您这样做时重新读取该文件。

3. **内联文件**

发送一个文件，其中内容格式如下：

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`, `env`, `export` 或设置没有特定变量名的 `set`
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定密钥 ('`^VARNAME='`)
* 永远不要将密钥文件源到shell环境 (`source .env` 或 `. .env`)
* 仅读取当前任务明确需要的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制，如果其中包含真实凭证 - 添加到 `.gitignore`

### 永远不要泄露API密钥和密钥

永远不要泄露API密钥和密钥文件的位置。

永远不要将API密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

向用户显示凭证时：
- **API Key**: 显示前5个字符加上最后4个字符: `su1Qc...8akf`
- **Secret Key**: 始终遮盖，仅显示最后5个: `***...aws1`

请求凭证时显示的示例响应：
账户：main
API Key: su1Qc...8akf
Secret: ***...aws1
环境：主网

### 列出账户

列出账户时，仅显示名称和环境，永远不要显示密钥：
Binance账户：
* main (主网/测试网)
* testnet-dev (测试网)
* futures-keys (主网)

### 主网中的交易

在执行主网交易时，始终在继续之前与用户确认，方法是要求他们写入 "CONFIRM" 继续。

---

## Binance账户

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret
- Testnet: false 

### testnet-dev
- API Key: your_testnet_api_key
- Secret: your_testnet_secret
- Testnet: true

### TOOLS.md结构

```bash
## Binance账户

### main
- API Key: abc123...xyz
- Secret: secret123...key
- Testnet: false
- 描述：主要交易账户

### testnet-dev
- API Key: test456...abc
- Secret: testsecret...xyz
- Testnet: true
- 描述：开发/测试

### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- Testnet: false
- 描述：期货交易账户
```

## 代理行为

1. 请求凭证：遮盖密钥 (仅显示最后5个字符)
2. 列出账户：显示名称和环境，永远不要密钥
3. 账户选择：如果存在歧义，请询问，默认为主网
4. 在主网执行交易时，通过要求用户写入 "CONFIRM" 来确认继续
5. 新凭证：提示输入名称、环境和签名模式
6. 当请求需要签名时，如果请求不是订单，并且API密钥不是描述为 `mainnet`、`testnet` 或 `demo` 密钥，则尝试使用不同的基本URL进行请求并查看是否有效，而无需询问用户。如果有效，则将密钥存储与相应的环境。

## 添加新账户

当用户通过内联文件或消息提供新凭证时：

* 询问账户名称
* 询问：主网、测试网或演示
* 存储在 `TOOLS.md` 中，并遮盖显示确认 

## 签名请求

对于需要签名的交易端点：

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 构建包含所有参数的查询字符串，包括时间戳 (Unix ms)。
3. 使用UTF-8根据RFC 3986对参数进行百分比编码。
4. 使用 `secretKey` 使用HMAC SHA256、RSA或Ed25519 (取决于账户配置) 对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包含 `X-MBX-APIKEY` 标头。

否则，不要执行步骤4-6。

## 新客户订单ID 

对于包含 `newClientOrderId` 参数的端点，值必须始终以 `agent-` 开头。如果未提供该参数，将自动生成 `agent-` 后跟18个随机字母数字字符。如果提供了值，它将被 `agent-` 前缀

示例：`agent-1a2b3c4d5e6f7g8h9i`

## 用户代理标头

包含 `User-Agent` 标头，如下面的字符串：`binance-spot/1.1.0 (Skill)`

另请参阅 [`references/authentication.md`](./references/authentication.md) 以获取实现细节。
