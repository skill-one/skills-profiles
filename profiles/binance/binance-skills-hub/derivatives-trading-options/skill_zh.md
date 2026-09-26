# Binance 期权交易技能

使用经过身份验证的 API 端点在 Binance 上进行期权交易请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点 | 描述 | 必填 | 可选 | 身份验证 |
|------|------|------|------|----------|
| `/eapi/v1/bill` (GET) | 账户资金流水 (USER_DATA) | currency | recordId, startTime, endTime, limit, recvWindow | 是 |
| `/eapi/v1/marginAccount` (GET) | 期权保证金账户信息 (USER_DATA) | 无 | recvWindow | 是 |
| `/eapi/v1/block/order/execute` (POST) | 接受限价交易订单 (TRADE) | blockOrderMatchingKey | recvWindow | 是 |
| `/eapi/v1/block/order/execute` (GET) | 查询限价交易详情 (USER_DATA) | blockOrderMatchingKey | recvWindow | 是 |
| `/eapi/v1/block/user-trades` (GET) | 账户限价交易列表 (USER_DATA) | 无 | endTime, startTime, underlying, recvWindow | 是 |
| `/eapi/v1/block/order/create` (DELETE) | 取消限价交易订单 (TRADE) | blockOrderMatchingKey | recvWindow | 是 |
| `/eapi/v1/block/order/create` (PUT) | 延长限价交易订单 (TRADE) | blockOrderMatchingKey | recvWindow | 是 |
| `/eapi/v1/block/order/create` (POST) | 新建限价交易订单 (TRADE) | liquidity, legs | recvWindow | 是 |
| `/eapi/v1/block/order/orders` (GET) | 查询限价交易订单 (TRADE) | 无 | blockOrderMatchingKey, endTime, startTime, underlying, recvWindow | 是 |
| `/eapi/v1/ticker` (GET) | 24 小时 ticker 价格变动统计 | 无 | symbol | 否 |
| `/eapi/v1/time` (GET) | 检查服务器时间 | 无 | 无 | 否 |
| `/eapi/v1/exchangeInfo` (GET) | 交易所信息 | 无 | 无 | 否 |
| `/eapi/v1/exerciseHistory` (GET) | 历史行权记录 | 无 | underlying, startTime, endTime, limit | 否 |
| `/eapi/v1/klines` (GET) | K线/蜡烛图数据 | symbol, interval | startTime, endTime, limit | 否 |
| `/eapi/v1/openInterest` (GET) | 未平仓合约量 | underlyingAsset, expiration | 无 | 否 |
| `/eapi/v1/mark` (GET) | 期权标记价格 | 无 | symbol | 否 |
| `/eapi/v1/depth` (GET) | 订单簿 | symbol | limit | 否 |
| `/eapi/v1/blockTrades` (GET) | 最近限价交易列表 | 无 | symbol, limit | 否 |
| `/eapi/v1/trades` (GET) | 最近交易列表 | symbol | limit | 否 |
| `/eapi/v1/index` (GET) | 指数价格 | underlying | 无 | 否 |
| `/eapi/v1/ping` (GET) | 测试连接性 | 无 | 无 | 否 |
| `/eapi/v1/countdownCancelAllHeartBeat` (POST) | 自动取消所有未成交订单（紧急停止）心跳 (TRADE) | underlyings | recvWindow | 是 |
| `/eapi/v1/countdownCancelAll` (GET) | 获取自动取消所有未成交订单（紧急停止）配置 (TRADE) | 无 | underlying, recvWindow | 是 |
| `/eapi/v1/countdownCancelAll` (POST) | 设置自动取消所有未成交订单（紧急停止）配置 (TRADE) | underlying, countdownTime | recvWindow | 是 |
| `/eapi/v1/mmp` (GET) | 获取做市商保护配置 (TRADE) | 无 | underlying, recvWindow | 是 |
| `/eapi/v1/mmpReset` (POST) | 重置做市商保护配置 (TRADE) | 无 | underlying, recvWindow | 是 |
| `/eapi/v1/mmpSet` (POST) | 设置做市商保护配置 (TRADE) | 无 | underlying, windowTimeInMilliseconds, frozenTimeInMilliseconds, qtyLimit, deltaLimit, recvWindow | 是 |
| `/eapi/v1/userTrades` (GET) | 账户交易列表 (USER_DATA) | 无 | symbol, fromId, startTime, endTime, limit, recvWindow | 是 |
| `/eapi/v1/allOpenOrdersByUnderlying` (DELETE) | 按标的取消所有期权订单 (TRADE) | underlying | recvWindow | 是 |
| `/eapi/v1/batchOrders` (DELETE) | 取消多个期权订单 (TRADE) | symbol | orderIds, clientOrderIds, recvWindow | 是 |
| `/eapi/v1/batchOrders` (POST) | 批量下单(TRADE) | orders | recvWindow | 是 |
| `/eapi/v1/order` (DELETE) | 取消期权订单 (TRADE) | symbol | orderId, clientOrderId, recvWindow | 是 |
| `/eapi/v1/order` (POST) | 新建订单 (TRADE) | symbol, side, type, quantity | price, timeInForce, reduceOnly, postOnly, newOrderRespType, clientOrderId, isMmp, recvWindow | 是 |
| `/eapi/v1/order` (GET) | 查询单个订单 (TRADE) | symbol | orderId, clientOrderId, recvWindow | 是 |
| `/eapi/v1/allOpenOrders` (DELETE) | 取消特定标的的所有期权订单 (TRADE) | symbol | recvWindow | 是 |
| `/eapi/v1/position` (GET) | 期权持仓信息 (USER_DATA) | 无 | symbol, recvWindow | 是 |
| `/eapi/v1/openOrders` (GET) | 查询当前未成交期权订单 (USER_DATA) | 无 | symbol, orderId, startTime, endTime, recvWindow | 是 |
| `/eapi/v1/historyOrders` (GET) | 查询期权订单历史 (TRADE) | symbol | orderId, startTime, endTime, limit, recvWindow | 是 |
| `/eapi/v1/commission` (GET) | 用户佣金 (USER_DATA) | 无 | recvWindow | 是 |
| `/eapi/v1/exerciseRecord` (GET) | 用户行权记录 (USER_DATA) | 无 | symbol, startTime, endTime, limit, recvWindow | 是 |
| `/eapi/v1/listenKey` (DELETE) | 关闭用户数据流 (USER_STREAM) | 无 | 无 | 否 |
| `/eapi/v1/listenKey` (PUT) | 保持用户数据流活跃 (USER_STREAM) | 无 | 无 | 否 |
| `/eapi/v1/listenKey` (POST) | 启动用户数据流 (USER_STREAM) | 无 | 无 | 否 |

---

## 参数

### 常用参数

* **currency**: 资产类型，目前仅支持 USDT
* **recordId**: 返回 recordId 及后续数据，默认返回最新数据，例如 100000（例如 1）
* **startTime**: 开始时间，例如 1593511200000（例如 1623319461670）
* **endTime**: 结束时间，例如 1593512200000（例如 1641782889000）
* **limit**: 返回结果集数量 默认：100 最大：1000（例如 100）
* **recvWindow**: （例如 5000）
* **blockOrderMatchingKey**: 
* **underlying**: 标的，例如 BTCUSDT
* **liquidity**: Taker 或 Maker
* **legs**: 最大 1（仅支持单腿），JSON 格式的腿参数列表；示例：eapi/v1/block/order/create?orders=[{"symbol":"BTC-210115-35000-C", "price":"100","quantity":"0.0002","side":"BUY","type":"LIMIT"}]
* **blockOrderMatchingKey**: 如果指定，返回与 blockOrderMatchingKey 相关的特定限价交易
* **symbol**: 期权交易对，例如 BTC-200730-9000-C
* **symbol**: 期权交易对，例如 BTC-200730-9000-C
* **interval**: 时间间隔
* **underlyingAsset**: 标的资产，例如 ETH/BTC
* **expiration**: 到期日，例如 221225
* **underlying**: 期权标的，例如 BTCUSDT
* **underlyings**: 期权标的符号，例如 BTCUSDT,ETHUSDT
* **countdownTime**: 毫秒级倒计时时间（例如 1,000 表示 1 秒）。0 表示禁用计时器。不接受负值（例如 -10000）。最小可接受值为 5,000
* **windowTimeInMilliseconds**: MMP 间隔毫秒；范围 (0,5000]
* **frozenTimeInMilliseconds**: MMP 冻结时间毫秒，如果设置为 0 需要手动重置
* **qtyLimit**: 数量限制（例如 1.0）
* **deltaLimit**: 净 delta 限制（例如 1.0）
* **fromId**: 获取交易的交易 ID。默认获取最新交易，例如 4611875134427365376（例如 1）
* **orderIds**: 订单 ID，例如 [4611875134427365377,4611875134427365378]
* **clientOrderIds**: 用户定义的订单 ID，例如 ["my_id_1","my_id_2"]
* **orderId**: 订单 ID，例如 4611875134427365377（例如 1）
* **clientOrderId**: 用户定义的订单 ID，例如 10000（例如 1）
* **quantity**: 订单数量（例如 1.0）
* **price**: 订单价格（例如 1.0）
* **reduceOnly**: 只减少（默认 false）（例如 false）
* **postOnly**: 只挂单（默认 false）（例如 false）
* **isMmp**: 是否为做市商保护订单，true/false
* **orders**: 订单列表。最大 10 个订单

### 枚举

* **side**: BUY | SELL
* **type**: LIMIT
* **timeInForce**: GTC | IOC | FOK | GTX
* **newOrderRespType**: ACK | RESULT


## 身份验证

对于需要身份验证的端点，您需要提供 Binance API 凭证。
所需凭证：

* apiKey: 您的 Binance API 密钥（用于请求头）
* secretKey: 您的 Binance API 密钥（用于签名）

基础 URL：
* 主网：https://eapi.binance.com
* 测试网：https://testnet.binancefuture.com

## 安全

### 分享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试使用前两种方式自动获取凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理也可以使用前两种方法在不经用户确认的情况下发起 HTTP 请求。

1. **环境变量**

仅搜索以下特定变量（切勿导出完整环境）：

**授权环境变量**
- 主网：`BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`
- 测试网：`BINANCE_TESTNET_API_KEY` 和 `BINANCE_TESTNET_SECRET_KEY`

在单个 exec 调用中读取并使用，以防止原始密钥进入代理的上下文：
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入正在运行的实例。如果您需要在不重新启动的情况下添加或更新凭证，请使用密钥文件（见选项 2）。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` ， `~/.env`，或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，切勿导出完整文件：
```bash
# 按顺序尝试所有凭证位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env（KEY=VALUE 格式，然后原始行格式）
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

此文件可以随时更新而无需重新启动 OpenClaw，每次调用时都会重新读取密钥。用户可以告诉您变量已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个文件，其内容格式如下：

```bash
abc123...xyz
secret123...key
```

* 切勿运行 `printenv`，`env`，`export` 或无特定变量名地设置
* 切勿在未锚定到特定密钥的情况下对 `env` 文件运行 `grep`（`^VARNAME=`）
* 切勿将密钥文件源入 shell 环境（`source .env` 或 `. .env`）
* 仅读取当前任务所需的凭证
* 切勿在输出或回复中回显或记录原始凭证
* 切勿将 `TOOLS.md` 提交到版本控制，如果其中包含真实凭证——将其添加到 `.gitignore` 中

### 切勿泄露 API 密钥和密钥

切勿泄露 API 密钥和密钥文件的位置。

切勿将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 切勿显示完整密钥

向用户显示凭证时：
- **API 密钥**：显示前 5 个字符 + 最后 4 个字符：`su1Qc...8akf`
- **密钥**：始终遮盖，仅显示最后 5 个字符：`***...aws1`

当被要求提供凭证时，示例响应：
账户：main
API 密钥：su1Qc...8akf
密钥：***...aws1
环境：主网

### 列出账户

列出账户时，仅显示名称和环境——切勿显示密钥：
Binance 账户：
* main (主网/测试网)
* testnet-dev (测试网)
* futures-keys (主网)

### 主网中的交易

在主网执行交易时，始终在继续之前通过询问用户是否写入 "CONFIRM" 来确认。
