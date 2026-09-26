# Binance 杠杆交易技能

使用认证 API 端点在 Binance 上进行杠杆交易请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点                     | 描述                                                         | 必填 | 可选 | 认证 |
| ------------------------ | ------------------------------------------------------------ | ---- | ---- | ---- |
| `/sapi/v1/margin/max-leverage` (POST) | 调整跨保证金最大杠杆 (USER_DATA)                           | maxLeverage | 无   | 是   |
| `/sapi/v1/margin/isolated/account` (DELETE) | 禁用隔离保证金账户 (TRADE)                                   | symbol | recvWindow | 是   |
| `/sapi/v1/margin/isolated/account` (POST) | 启用隔离保证金账户 (TRADE)                                   | symbol | recvWindow | 是   |
| `/sapi/v1/margin/isolated/account` (GET) | 查询隔离保证金账户信息 (USER_DATA)                         | 无   | symbols, recvWindow | 是   |
| `/sapi/v1/bnbBurn` (GET) | 获取 BNB 燃烧状态 (USER_DATA)                               | 无   | recvWindow | 是   |
| `/sapi/v1/margin/tradeCoeff` (GET) | 获取保证金账户摘要 (USER_DATA)                              | 无   | recvWindow | 是   |
| `/sapi/v1/margin/capital-flow` (GET) | 查询跨隔离保证金资金流 (USER_DATA)                          | 无   | asset, symbol, type, startTime, endTime, fromId, limit, recvWindow | 是   |
| `/sapi/v1/margin/account` (GET) | 查询跨保证金账户详情 (USER_DATA)                            | 无   | recvWindow | 是   |
| `/sapi/v1/margin/crossMarginData` (GET) | 查询跨保证金费数据 (USER_DATA)                              | 无   | vipLevel, coin, recvWindow | 是   |
| `/sapi/v1/margin/isolated/accountLimit` (GET) | 查询已启用隔离保证金账户限额 (USER_DATA)                    | 无   | recvWindow | 是   |
| `/sapi/v1/margin/isolatedMarginData` (GET) | 查询隔离保证金费数据 (USER_DATA)                            | 无   | vipLevel, symbol, recvWindow | 是   |
| `/sapi/v1/margin/interestHistory` (GET) | 获取利息历史 (USER_DATA)                                     | 无   | asset, isolatedSymbol, startTime, endTime, current, size, recvWindow | 是   |
| `/sapi/v1/margin/next-hourly-interest-rate` (GET) | 获取未来每小时利率 (USER_DATA)                              | assets, isIsolated | 无   | 是   |
| `/sapi/v1/margin/borrow-repay` (POST) | 保证金账户借/还 (MARGIN)                                    | asset, isIsolated, symbol, amount, type | recvWindow | 是   |
| `/sapi/v1/margin/borrow-repay` (GET) | 查询保证金账户借/还记录 (USER_DATA)                         | type | asset, isolatedSymbol, txId, startTime, endTime, current, size, recvWindow | 是   |
| `/sapi/v1/margin/interestRateHistory` (GET) | 查询保证金利率历史 (USER_DATA)                              | asset | vipLevel, startTime, endTime, recvWindow | 是   |
| `/sapi/v1/margin/maxBorrowable` (GET) | 查询最大可借 (USER_DATA)                                    | asset | isolatedSymbol, recvWindow | 是   |
| `/sapi/v1/margin/crossMarginCollateralRatio` (GET) | 跨保证金抵押率 (MARKET_DATA)                                | 无   | 无   | 否   |
| `/sapi/v1/margin/allPairs` (GET) | 获取所有跨保证金对 (MARKET_DATA)                            | 无   | symbol | 否   |
| `/sapi/v1/margin/isolated/allPairs` (GET) | 获取所有隔离保证金符号 (MARKET_DATA)                         | 无   | symbol, recvWindow | 否   |
| `/sapi/v1/margin/allAssets` (GET) | 获取所有保证金资产 (MARKET_DATA)                            | 无   | asset | 否   |
| `/sapi/v1/margin/delist-schedule` (GET) | 获取退市计划 (MARKET_DATA)                                  | 无   | recvWindow | 否   |
| `/sapi/v1/margin/limit-price-pairs` (GET) | 获取限价对 (MARKET_DATA)                                    | 无   | 无   | 否   |
| `/sapi/v1/margin/list-schedule` (GET) | 获取上市计划 (MARKET_DATA)                                  | 无   | recvWindow | 否   |
| `/sapi/v1/margin/risk-based-liquidation-ratio` (GET) | 获取保证金资产风险抵押率 (MARKET_DATA)                      | 无   | 无   | 否   |
| `/sapi/v1/margin/restricted-asset` (GET) | 获取保证金受限资产 (MARKET_DATA)                            | 无   | 无   | 否   |
| `/sapi/v1/margin/isolatedMarginTier` (GET) | 查询隔离保证金等级数据 (USER_DATA)                          | symbol | tier, recvWindow | 是   |
| `/sapi/v1/margin/leverageBracket` (GET) | 查询跨保证金专业模式下的责任币杠杆区间 (MARKET_DATA)        | 无   | 无   | 否   |
| `/sapi/v1/margin/priceIndex` (GET) | 查询保证金价格指数 (MARKET_DATA)                            | symbol | 无   | 否   |
| `/sapi/v1/margin/available-inventory` (GET) | 查询保证金可用库存 (USER_DATA)                              | type | 无   | 是   |
| `/sapi/v1/margin/listen-key` (DELETE) | 关闭用户数据流 (USER_STREAM)                                | 无   | 无   | 否   |
| `/sapi/v1/margin/listen-key` (PUT) | 保持用户数据流 (USER_STREAM)                                | listenKey | 无   | 否   |
| `/sapi/v1/margin/listen-key` (POST) | 启动用户数据流 (USER_STREAM)                                | 无   | 无   | 否   |
| `/sapi/v1/margin/apiKey` (POST) | 创建特殊密钥（低延迟交易）(TRADE)                          | apiName | symbol, ip, publicKey, permissionMode, recvWindow | 是   |
| `/sapi/v1/margin/apiKey` (DELETE) | 删除特殊密钥（低延迟交易）(TRADE)                          | 无   | apiName, symbol, recvWindow | 是   |
| `/sapi/v1/margin/apiKey` (GET) | 查询特殊密钥（低延迟交易）(TRADE)                          | 无   | symbol, recvWindow | 是   |
| `/sapi/v1/margin/apiKey/ip` (PUT) | 编辑特殊密钥的 IP（低延迟交易）(TRADE)                     | ip | symbol, recvWindow | 是   |
| `/sapi/v1/margin/forceLiquidationRec` (GET) | 获取强制平仓记录 (USER_DATA)                                | 无   | startTime, endTime, isolatedSymbol, current, size, recvWindow | 是   |
| `/sapi/v1/margin/exchange-small-liability` (GET) | 获取小责任交换币列表 (USER_DATA)                            | 无   | recvWindow | 是   |
| `/sapi/v1/margin/exchange-small-liability` (POST) | 小责任交换 (MARGIN)                                          | assetNames | recvWindow | 是   |
| `/sapi/v1/margin/exchange-small-liability-history` (GET) | 获取小责任交换历史 (USER_DATA)                              | current, size | startTime, endTime, recvWindow | 是   |
| `/sapi/v1/margin/openOrders` (DELETE) | 在特定符号上取消保证金账户所有未成交订单 (TRADE)              | symbol | isIsolated, recvWindow | 是   |
| `/sapi/v1/margin/openOrders` (GET) | 查询保证金账户的未成交订单 (USER_DATA)                      | 无   | symbol, isIsolated, recvWindow | 是   |
| `/sapi/v1/margin/orderList` (DELETE) | 保证金账户取消 OCO (TRADE)                                  | symbol | isIsolated, orderListId, listClientOrderId, newClientOrderId, recvWindow | 是   |
| `/sapi/v1/margin/orderList` (GET) | 查询保证金账户的 OCO (USER_DATA)                            | 无   | isIsolated, symbol, orderListId, origClientOrderId, recvWindow | 是   |
| `/sapi/v1/margin/order` (DELETE) | 保证金账户取消订单 (TRADE)                                  | symbol | isIsolated, orderId, origClientOrderId, newClientOrderId, recvWindow | 是   |
| `/sapi/v1/margin/order` (POST) | 保证金账户新订单 (TRADE)                                    | symbol, side, type | isIsolated, quantity, quoteOrderQty, price, stopPrice, newClientOrderId, icebergQty, newOrderRespType, sideEffectType, timeInForce, selfTradePreventionMode, autoRepayAtCancel, recvWindow | 是   |
| `/sapi/v1/margin/order` (GET) | 查询保证金账户的订单 (USER_DATA)                            | symbol | isIsolated, orderId, origClientOrderId, recvWindow | 是   |
| `/sapi/v1/margin/order/oco` (POST) | 保证金账户新 OCO (TRADE)                                    | symbol, side, quantity, price, stopPrice | isIsolated, listClientOrderId, limitClientOrderId, limitIcebergQty, stopClientOrderId, stopLimitPrice, stopIcebergQty, stopLimitTimeInForce, newOrderRespType, sideEffectType, selfTradePreventionMode, autoRepayAtCancel, recvWindow | 是   |
| `/sapi/v1/margin/order/oto` (POST) | 保证金账户新 OTO (TRADE)                                    | symbol, workingType, workingSide, workingPrice, workingQuantity, workingIcebergQty, pendingType, pendingSide, pendingQuantity | isIsolated, listClientOrderId, newOrderRespType, sideEffectType, selfTradePreventionMode, autoRepayAtCancel, workingClientOrderId, workingTimeInForce, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce | 是   |
| `/sapi/v1/margin/order/otoco` (POST) | 保证金账户新 OTOCO (TRADE)                                  | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingQuantity, pendingAboveType | isIsolated, sideEffectType, autoRepayAtCancel, listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce | 是   |
| `/sapi/v1/margin/manual-liquidation` (POST) | 保证金手动平仓 (MARGIN)                                     | type | symbol, recvWindow | 是   |
| `/sapi/v1/margin/rateLimit/order` (GET) | 查询当前保证金订单使用情况 (TRADE)                          | 无   | isIsolated, symbol, recvWindow | 是   |
| `/sapi/v1/margin/allOrderList` (GET) | 查询保证金账户的所有 OCO (USER_DATA)                         | 无   | isIsolated, symbol, fromId, startTime, endTime, limit, recvWindow | 是   |
| `/sapi/v1/margin/allOrders` (GET) | 查询保证金账户的所有订单 (USER_DATA)                         | symbol | isIsolated, orderId, startTime, endTime, limit, recvWindow | 是   |
| `/sapi/v1/margin/openOrderList` (GET) | 查询保证金账户的未成交 OCO (USER_DATA)                       | 无   | isIsolated, symbol, recvWindow | 是   |
| `/sapi/v1/margin/myTrades` (GET) | 查询保证金账户的交易列表 (USER_DATA)                         | symbol | isIsolated, orderId, startTime, endTime, fromId, limit, recvWindow | 是   |
| `/sapi/v1/margin/myPreventedMatches` (GET) | 查询阻止匹配 (USER_DATA)                                     | symbol | preventedMatchId, orderId, fromPreventedMatchId, recvWindow, isIsolated | 是   |
| `/sapi/v1/margin/api-key-list` (GET) | 查询特殊密钥列表（低延迟交易）(TRADE)                       | 无   | symbol, recvWindow | 是   |
| `/sapi/v1/margin/transfer` (GET) | 获取跨保证金转账历史 (USER_DATA)                            | 无   | asset, type, startTime, endTime, current, size, isolatedSymbol, recvWindow | 是   |
| `/sapi/v1/margin/maxTransferable` (GET) | 查询最大可转出金额 (USER_DATA)                              | asset | isolatedSymbol, recvWindow | 是   |

---

## 参数

### 常见参数

* **maxLeverage**: 仅能调整 3、5 或 10，示例：maxLeverage = 5 或 3 用于跨保证金经典模式；maxLeverage=10 用于跨保证金专业模式 10 倍杠杆，若合规允许则为 20 倍杠杆。
* **symbol**: 
* **recvWindow**: 不超过 60000（例如，5000）
* **asset**: 
* **symbol**: 隔离保证金对
* **type**: 转账类型：ROLL_IN、ROLL_OUT
* **startTime**: 仅支持查询过去 90 天的数据。（例如，1623319461670）
* **endTime**: （例如，1641782889000）
* **fromId**: 如果设置了 `fromId`，将返回 `id` 大于 `fromId` 的数据。否则，将返回最新数据。（例如，1）
* **limit**: 每次请求返回的数据记录数限制。默认：500；最大：1000。（例如，500）
* **vipLevel**: 如果省略 vipLevel，将返回用户的当前特定保证金数据（例如，1）
* **coin**: 
* **symbols**: 最多可发送 5 个符号；用逗号分隔。例如 "BTCUSDT,BNBUSDT,ADAUSDT"
* **isolatedSymbol**: 隔离符号
* **current**: 当前查询页。从 1 开始。默认：1（例如，1）
* **size**: 默认：10 最大：100（例如，10）
* **assets**: 资产列表，用逗号分隔，最多 20 个
* **isIsolated**: 用于隔离保证金或非隔离保证金，"TRUE"、"FALSE"
* **asset**: 
* **isIsolated**: `TRUE` 用于隔离保证金，`FALSE` 用于跨保证金，默认 `FALSE`（例如，FALSE）
* **amount**: 
* **type**: `MARGIN`,`ISOLATED`
* **txId**: 在 `POST /sapi/v1/margin/loan` 中的 `tranId`（例如，1）
* **tier**: 如果省略 tier，将返回所有保证金等级数据
* **listenKey**: 
* **apiName**: 
* **ip**: 可批量添加，用逗号分隔。每个 API 密钥最多 30 个
* **publicKey**: 1. 如果输入了 publicKey，将创建 RSA 或 Ed25519 密钥。2. 需要编码为 URL 编码格式
* **permissionMode**: 此参数仅用于 Ed25519 API 密钥，对其他加密方法无效。值可以是 TRADE（所有权限的 TRADE）或 READ（仅 USER_DATA、FIX_API_READ_ONLY 的 READ）。默认值为 TRADE。（例如，值）
* **apiName**: 
* **ip**: 可批量添加，用逗号分隔。每个 API 密钥最多 30 个
* **current**: 当前查询页。从 1 开始。默认：1（例如，1）
* **size**: 默认：10，最大：100（例如，10）
* **isIsolated**: 用于隔离保证金或非隔离保证金，"TRUE"、"FALSE"，默认 "FALSE"
* **orderListId**: 必须提供 `orderListId` 或 `listClientOrderId` 中的一个（例如，1）
* **listClientOrderId**: 必须提供 `orderListId` 或 `listClientOrderId` 中的一个（例如，1）
* **newClientOrderId**: 用于唯一标识此取消。默认自动生成（例如，1）
* **orderId**:  （例如，1）
* **origClientOrderId**:  （例如，1）
* **quantity**:  （例如，1.0）
* **limitClientOrderId**: 限价订单的唯一 ID（例如，1）
* **price**:  （例如，1.0）
* **limitIcebergQty**:  （例如，1.0）
* **stopClientOrderId**: 止损/止损限价腿的唯一 ID（例如，1）
* **stopPrice**:  （例如，1.0）
* **stopLimitPrice**: 如果提供，需要 `stopLimitTimeInForce`。（例如，1.0）
* **stopIcebergQty**:  （例如，1.0）
* **stopLimitTimeInForce**: 有效值为 `GTC`/`FOK`/`IOC`
* **sideEffectType**: NO_SIDE_EFFECT, MARGIN_BUY, AUTO_REPAY,AUTO_BORROW_REPAY；默认 NO_SIDE_EFFECT。更多信息请参考 FAQ（例如，NO_SIDE_EFFECT）
* **selfTradePreventionMode**: 允许的枚举值取决于符号的配置。可能支持的字面值是 EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE（例如，NONE）
* **autoRepayAtCancel**: 仅当 MARGIN_BUY 或 AUTO_BORROW_REPAY 订单生效时，true 表示订单取消后需要偿还由此产生的债务。默认为 true（例如，true）
* **workingType**: 支持的值：`LIMIT`, `LIMIT_MAKER`
* **workingSide**: BUY, SELL
* **workingClientOrderId**: 在所有未成交订单中为工作订单的任意唯一 ID。如果未发送，将自动生成。（例如，1）
* **workingPrice**:  （例如，1.0）
* **workingQuantity**:  （例如，1.0）
* **workingIcebergQty**: 只有在使用 `workingTimeInForce` 为 `GTC` 时才能使用。（例如，1.0）
* **workingTimeInForce**: GTC,IOC,FOK
* **pendingType**: 支持的值：订单类型注意使用 `quoteOrderQty` 的 `MARKET` 订单不受支持。（例如，订单类型）
* **pendingSide**: BUY, SELL
* **pendingClientOrderId**: 在所有未成交订单中为待处理订单的任意唯一 ID。如果未发送，将自动生成。（例如，1）
* **pendingPrice**:  （例如，1.0）
* **pendingStopPrice**:  （例如，1.0）
* **pendingTrailingDelta**:  （例如，1.0）
* **pendingQuantity**:  （例如，1.0）
* **pendingIcebergQty**: 只有在使用 `pendingTimeInForce` 为 `GTC` 时才能使用。（例如，1.0）
* **pendingTimeInForce**: GTC,IOC,FOK
* **workingIcebergQty**: 只有在使用 `workingTimeInForce` 为 `GTC` 时才能使用。（例如，1.0）
* **pendingAboveType**: 支持的值：`LIMIT_MAKER`, `STOP_LOSS`, 和 `STOP_LOSS_LIMIT`
* **pendingAboveClientOrderId**: 在所有未成交订单中为待处理订单的任意唯一 ID。如果未发送，将自动生成。（例如，1）
* **pendingAbovePrice**:  （例如，1.0）
* **pendingAboveStopPrice**:  （例如，1.0）
* **pendingAboveTrailingDelta**:  （例如，1.0）
* **pendingAboveIcebergQty**: 只有在使用 `pendingAboveTimeInForce` 为 `GTC` 时才能使用。（例如，1.0）
* **pendingAboveTimeInForce**: 
* **pendingBelowType**: 支持的值：`LIMIT_MAKER`, `STOP_LOSS`, 和 `STOP_LOSS_LIMIT`
* **pendingBelowClientOrderId**: 在所有未成交订单中为待处理订单的任意唯一 ID。如果未发送，将自动生成。（例如，1）
* **pendingBelowPrice**:  （例如，1.0）
* **pendingBelowStopPrice**:  （例如，1.0）
* **pendingBelowTrailingDelta**:  （例如，1.0）
* **pendingBelowIcebergQty**: 只有在使用 `pendingBelowTimeInForce` 为 `GTC` 时才能使用。（例如，1.0）
* **pendingBelowTimeInForce**: 
* **quantity**:  （例如，1.0）
* **quoteOrderQty**:  （例如，1.0）
* **price**:  （例如，1.0）
* **stopPrice**: 与 `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, 和 `TAKE_PROFIT_LIMIT` 订单一起使用。（例如，1.0）
* **icebergQty**: 与 `LIMIT`, `STOP_LOSS_LIMIT`, 和 `TAKE_PROFIT_LIMIT` 一起使用，以创建冰山订单。（例如，1.0）
* **preventedMatchId**:  （例如，1）
* **fromPreventedMatchId**:  （例如，1）
* **assetNames**: 小责任交换的资产列表，例如：assetNames = BTC,ETH


### 枚举

* **side**: BUY | SELL
* **newOrderRespType**: ACK | RESULT | FULL
* **timeInForce**: GTC | IOC | FOK


## 认证

对于需要认证的端点，您需要提供 Binance API 凭证。
所需凭证：

* apiKey: 您的 Binance API 密钥（用于头部）
* secretKey: 您的 Binance API 密钥（用于签名）

基本 URL：

* 主网：https://api.binance.com

## 安全

### 分享凭证

用户可以通过多种方式提供 Binance API 凭证。代理将尝试使用前两种方法自动检索凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理还可以使用前两种方法在不确认的情况下进行 http 请求。

1. **环境变量**

仅搜索以下特定变量（永远不要输出完整的环境）：

**授权环境变量**
- 主网：`BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`

在一个 exec 调用中读取并使用，因此原始密钥永远不会进入代理的上下文：
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，不能注入正在运行的实例。如果您需要在重启之前添加或更新凭证，请使用密钥文件（见选项 2）。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` , `~/.env` 或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，永远不要输出完整文件：
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env（KEY=VALUE 格式然后原始行格式）
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

此文件可以随时更新而无需重启 OpenClaw，每次调用都会重新读取密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个文件，其内容格式如下：

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`, `env`, `export` 或设置没有特定变量名的 `export`
* 永远不要在没有锚点到特定键的情况下对 `env` 文件运行 `grep`（例如，`^VARNAME='`)
* 永远不要将密钥文件源代码到 shell 环境中（例如，`source .env` 或 `. .env`)
* 仅读取当前任务明确需要的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 永远不要将 `TOOLS.md` 提交到版本控制中如果它包含真实凭证 — 将其添加到 `.gitignore`

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

向用户显示凭证时：
- **API Key:** 显示前 5 个字符加上最后 4 个字符：`su1Qc...8akf`
- **Secret Key:** 始终遮盖，仅显示最后 5 个：`***...aws1`

请求凭证时返回的示例响应：
账户：main
API Key: su1Qc...8akf
Secret: ***...aws1

### 列出账户

列出账户时，仅显示名称和环境 — 永远不要显示密钥：
Binance 账户：
* main (主网)
* futures-keys (主网)

### 主网中的交易

在主网执行交易时，始终在继续之前与用户确认，方法是要求他们写入 "CONFIRM" 继续。

---

## Binance 账户

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret

### TOOLS.md 结构

```bash
## Binance 账户

### main
- API Key: abc123...xyz
- Secret: secret123...key
- 描述：主要交易账户


### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- 描述：期货交易账户
```

## 代理行为

1. 请求凭证：遮盖密钥（仅显示最后 5 个字符）
2. 列出账户：显示名称和环境，永远不要显示密钥
3. 账户选择：如果存在歧义，请询问，默认为主账户
4. 在主网执行交易时，通过要求用户写入 "CONFIRM" 来确认继续
5. 新凭证：提示输入名称、环境、签名模式

## 添加新账户

当用户通过内联文件或消息提供新凭证时：

* 询问账户名称
* 存储在 `TOOLS.md` 中，并确认遮盖显示 

## 签名请求

对于需要签名的交易端点：

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 构建包含所有参数的查询字符串，包括时间戳（Unix ms）。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 secretKey 使用 HMAC SHA256、RSA 或 Ed25519（取决于账户配置）对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包括 `X-MBX-APIKEY` 头部。

否则，不要执行步骤 4–6。

## 新客户端订单 ID 

对于包含 `newClientOrderId` 参数的端点，值必须始终以 `agent-` 开头。如果未提供该参数，将自动生成 `agent-` 后跟 18 个随机字母数字字符。如果提供了值，它将被 `agent-` 前缀。
示例：`agent-1a2b3c4d5e6f7g8h9i`

## 用户代理头部

包含以下字符串的 `User-Agent` 头部：`binance-margin-trading/1.1.0 (Skill)`

另请参阅 [`references/authentication.md`](./references/authentication.md) 以获取实现细节。
