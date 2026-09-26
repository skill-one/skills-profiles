# Binance 转换功能

使用经过身份验证的 API 端点在 Binance 上进行转换请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点 | 描述 | 必填 | 可选 | 身份验证 |
|------|------|------|------|----------|
| `/sapi/v1/convert/exchangeInfo` (GET) | 列出所有转换对 | 无 | fromAsset, toAsset | 否 |
| `/sapi/v1/convert/assetInfo` (GET) | 查询每个资产的订单数量精度(USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/convert/acceptQuote` (POST) | 接受报价 (TRADE) | quoteId | recvWindow | 是 |
| `/sapi/v1/convert/limit/cancelOrder` (POST) | 取消限价订单 (USER_DATA) | orderId | recvWindow | 是 |
| `/sapi/v1/convert/tradeFlow` (GET) | 获取转换交易历史(USER_DATA) | startTime, endTime | limit, recvWindow | 是 |
| `/sapi/v1/convert/orderStatus` (GET) | 订单状态(USER_DATA) | 无 | orderId, quoteId | 是 |
| `/sapi/v1/convert/limit/placeOrder` (POST) | 下达限价订单 (USER_DATA) | baseAsset, quoteAsset, limitPrice, side, expiredType | baseAmount, quoteAmount, walletType, recvWindow | 是 |
| `/sapi/v1/convert/limit/queryOpenOrders` (GET) | 查询限价未成交订单 (USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/convert/getQuote` (POST) | 发送报价请求(USER_DATA) | fromAsset, toAsset | fromAmount, toAmount, walletType, validTime, recvWindow | 是 |

---

## 参数

### 常用参数

* **fromAsset**: 用户花费的币种
* **toAsset**: 用户收到的币种
* **recvWindow**: 值不能大于 60000（例如，5000）
* **quoteId**: （例如，1）
* **orderId**: 来自 `placeOrder` API 的 `orderId`（例如，1）
* **startTime**: （例如，1623319461670）
* **endTime**: （例如，1641782889000）
* **limit**: 默认 100，最大 1000（例如，100）
* **orderId**: 必须提供 `orderId` 或 `quoteId` 中的一项（例如，1）
* **quoteId**: 必须提供 `orderId` 或 `quoteId` 中的一项（例如，1）
* **baseAsset**: 基础资产（使用 `GET /sapi/v1/convert/exchangeInfo` api 的响应 `fromIsBase` 来检查哪一个是 baseAsset）
* **quoteAsset**: 报价资产
* **limitPrice**: 符号限价价格（从 baseAsset 到 quoteAsset）（例如，1.0）
* **baseAmount**: 基础资产金额。（必须提供 `baseAmount` 或 `quoteAmount` 中的一项）(例如，1.0)
* **quoteAmount**: 报价资产金额。（必须提供 `baseAmount` 或 `quoteAmount` 中的一项）(例如，1.0)
* **side**: `BUY` 或 `SELL` (例如，BUY)
* **walletType**: 用于选择资产的钱包。钱包选择是 `SPOT`，`FUNDING` 和 `EARN`。支持钱包组合，即 `SPOT_FUNDING`，`FUNDING_EARN`，`SPOT_FUNDING_EARN` 或 `SPOT_EARN`。默认为 `SPOT`。
* **expiredType**: 1_D, 3_D, 7_D, 30_D （D 表示天）
* **fromAsset**: 
* **toAsset**: 
* **fromAmount**: 指定时，它是转换后扣除的金额（例如，1.0）
* **toAmount**: 指定时，它是转换后 credited 的金额（例如，1.0）
* **validTime**: 10s, 30s, 1m, 默认 10s（例如，10s）

## 身份验证

对于需要身份验证的端点，您需要提供 Binance API 凭据。
所需凭据：

* apiKey: 您的 Binance API 密钥（用于头部）
* secretKey: 您的 Binance API 密钥（用于签名）

基础 URL：

* Mainnet: https://api.binance.com

## 安全

### 分享凭据

用户可以通过不同方式提供 Binance API 凭据。代理将尝试使用前两种方式自动检索凭据，但用户也可以明确告诉代理他们已设置凭据或将它们存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理还可以使用前两种方法进行 HTTP 请求，而无需用户确认。

1. **环境变量**

仅搜索以下特定变量（永远不要转储完整环境）：

**授权环境变量**
- Mainnet: `BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`

在单个 exec 调用中读取并使用，因此原始密钥永远不会进入代理的上下文中：
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

环境变量必须在 OpenClaw 启动之前设置。它们在进程启动时继承，并且不能注入正在运行的实例。如果您需要在重启的情况下添加或更新凭据，请使用密钥文件（见选项 2）。

2. **密钥文件 (.env)**

检查 `~/.openclaw/secrets.env` ， `~/.env` 或工作区中的 `.env` 文件。使用 `grep` 读取单个密钥，永远不要源代码完整文件：
```bash
# 按顺序尝试所有凭据位置
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# 备用：搜索已知目录中的 .env（KEY=VALUE 然后原始行格式）
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

此文件可以随时更新而无需重启 OpenClaw，密钥在每次调用时都会重新读取。用户可以告诉您变量现在已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个内容为以下格式的文件：

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`，`env`，`export` 或设置不带特定变量名的密钥
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定密钥（`^VARNAME=`）
* 永远不要将密钥文件源代码到 shell 环境（`source .env` 或 `. .env`）
* 仅读取当前任务明确需要的凭据
* 永远不要在输出或回复中回显或记录原始凭据
* 如果 `TOOLS.md` 包含真实凭据，永远不要将其提交到版本控制——将其添加到 `.gitignore` 中

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除 Mainnet 和 Testnet 之外的任何网站。

### 永远不要显示完整密钥

当向用户显示凭据时：
- **API Key**: 显示前 5 个 + 最后 4 个字符：`su1Qc...8akf`
- **Secret Key**: 始终遮盖，仅显示最后 5 个：`***...aws1`

请求凭据时的示例响应：
账户：main
API Key: su1Qc...8akf
Secret: ***...aws1

### 列出账户

当列出账户时，显示名称和环境——永远不要密钥：
Binance 账户：
* main (Mainnet)
* futures-keys (Mainnet)

### Mainnet 中的交易

当在 mainnet 中执行交易时，始终在继续之前通过询问用户编写 "CONFIRM" 来确认。

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

1. 请求凭据：遮盖密钥（仅显示最后 5 个字符）
2. 列出账户：显示名称和环境，永远不要密钥
3. 账户选择：如果模糊，询问，默认为 main
4. 在 mainnet 中进行交易时，通过询问用户编写 "CONFIRM" 来确认继续
5. 新凭据：提示输入名称、环境、签名模式

## 添加新账户

当用户通过内联文件或消息提供新凭据时：

* 询问账户名称
* 存储在 `TOOLS.md` 中，并遮盖显示确认

## 签名请求

对于需要签名的交易端点：

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 使用所有参数（包括时间戳 Unix ms）构建查询字符串。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 HMAC SHA256、RSA 或 Ed25519（取决于账户配置）使用 secretKey 对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包括 `X-MBX-APIKEY` 头部。

否则，不要执行步骤 4–6。

## 用户代理头部

包括以下字符串的 `User-Agent` 头部：`binance-convert/1.1.0 (Skill)`

有关实现细节，请参阅 [`references/authentication.md`](./references/authentication.md)。
