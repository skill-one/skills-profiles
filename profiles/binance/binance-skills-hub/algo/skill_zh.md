# Binance 算法交易技能

使用认证 API 端点在 Binance 上进行算法交易请求。某些端点需要 API 密钥和密钥。结果以 JSON 格式返回。

## 快速参考

| 端点 | 描述 | 必填 | 可选 | 认证 |
|------|------|------|------|------|
| `/sapi/v1/algo/futures/order` (DELETE) | 取消算法订单(TRADE) | algoId | recvWindow | 是 |
| `/sapi/v1/algo/futures/openOrders` (GET) | 查询当前算法未成交订单(USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/algo/futures/historicalOrders` (GET) | 查询历史算法订单(USER_DATA) | 无 | symbol, side, startTime, endTime, page, pageSize, recvWindow | 是 |
| `/sapi/v1/algo/futures/subOrders` (GET) | 查询子订单(USER_DATA) | algoId | page, pageSize, recvWindow | 是 |
| `/sapi/v1/algo/futures/newOrderTwap` (POST) | 时间加权平均价格(Twap) 新订单(TRADE) | symbol, side, quantity, duration | positionSide, clientAlgoId, reduceOnly, limitPrice, recvWindow | 是 |
| `/sapi/v1/algo/futures/newOrderVp` (POST) | 量参与(VP) 新订单 (TRADE) | symbol, side, quantity, urgency | positionSide, clientAlgoId, reduceOnly, limitPrice, recvWindow | 是 |
| `/sapi/v1/algo/spot/order` (DELETE) | 取消算法订单(TRADE) | algoId | recvWindow | 是 |
| `/sapi/v1/algo/spot/openOrders` (GET) | 查询当前算法未成交订单(USER_DATA) | 无 | recvWindow | 是 |
| `/sapi/v1/algo/spot/historicalOrders` (GET) | 查询历史算法订单(USER_DATA) | 无 | symbol, side, startTime, endTime, page, pageSize, recvWindow | 是 |
| `/sapi/v1/algo/spot/subOrders` (GET) | 查询子订单(USER_DATA) | algoId | page, pageSize, recvWindow | 是 |
| `/sapi/v1/algo/spot/newOrderTwap` (POST) | 时间加权平均价格(Twap) 新订单(TRADE) | symbol, side, quantity, duration | clientAlgoId, limitPrice | 是 |

---

## 参数

### 常用参数

* **algoId**: 例如 14511 (例如 1)
* **recvWindow**: (例如 5000)
* **symbol**: 交易对，例如 BTCUSDT (例如 BTCUSDT)
* **side**: BUY 或 SELL (例如 BUY)
* **startTime**: 毫秒为单位，例如 1641522717552 (例如 1623319461670)
* **endTime**: 毫秒为单位，例如 1641522526562 (例如 1641782889000)
* **page**: 默认为 1 (例如 1)
* **pageSize**: 最小 1，最大 100；默认 100 (例如 100)
* **symbol**: 交易对，例如 BTCUSDT (例如 BTCUSDT)
* **side**: 交易方向 (BUY 或 SELL) (例如 BUY)
* **positionSide**: 默认 `BOTH` 为单向模式；`LONG` 或 `SHORT` 为对冲模式。在对冲模式下必须发送。 (例如 BOTH)
* **quantity**: 基础资产数量；每个订单的最大名义价值取决于交易对。如果您的订单超过每个订单的最大名义价值，请减少您的规模。(例如 1.0)
* **duration**: TWAP 订单的持续时间（秒）。[300, 86400] (例如 5000)
* **clientAlgoId**: 在算法订单中唯一的 ID（长度应为 32 个字符），如果未发送，我们将提供默认值 (例如 1)
* **reduceOnly**: "true" 或 "false"。默认 "false"；在对冲模式下不能发送；在您开仓时不能发送
* **limitPrice**: 订单的限价；如果未发送，将按市价默认下单 (例如 1.0)
* **urgency**: 表示当前执行的相对速度；ENUM: LOW, MEDIUM, HIGH (例如 LOW)

## 认证

对于需要认证的端点，您需要提供 Binance API 凭证。
所需凭证：

* apiKey: 您的 Binance API 密钥（用于头部）
* secretKey: 您的 Binance API 密钥（用于签名）

基本 URL：

* 主网: https://api.binance.com

## 安全

### 共享凭证

用户可以通过不同方式提供 Binance API 凭证。代理将尝试使用前两种方式自动检索凭证，但用户也可以明确告诉代理他们已设置凭证或将其存储在 `.env` 文件中，代理应在他们这样做时重新读取该文件。代理还可以使用前两种方法进行 HTTP 请求，而无需用户确认。

1. **环境变量**

仅搜索以下特定变量（永远不要转储完整环境）：

**授权环境变量**
- 主网: `BINANCE_API_KEY` 和 `BINANCE_SECRET_KEY`

在单个 exec 调用中读取和使用，因此原始密钥永远不会进入代理的上下文中：
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

检查 `~/.openclaw/secrets.env` ， `~/.env`，或工作区中的 `.env` 文件。使用 `grep` 逐个读取密钥，永远不要转储完整文件：
```bash
# 按顺序尝试所有凭证位置
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

此文件可以随时更新而无需重新启动 OpenClaw，密钥将在每次调用时重新读取。用户可以告诉您变量现在已设置或存储在 `.env` 文件中，您应在他们这样做时重新读取该文件。

3. **内联文件**

发送一个内容为以下格式的文件：

```bash
abc123...xyz
secret123...key
```

* 永远不要运行 `printenv`，`env`，`export` 或设置不带特定变量名的 `set`
* 永远不要在 `env` 文件上运行 `grep` 而不锚定到特定密钥（`'^VARNAME='`）
* 永远不要将密钥文件源到 shell 环境（`source .env` 或 `. .env`）
* 仅读取当前任务明确需要的凭证
* 永远不要在输出或回复中回显或记录原始凭证
* 如果 `TOOLS.md` 包含真实凭证，永远不要将其提交到版本控制——将其添加到 `.gitignore` 中

### 永远不要泄露 API 密钥和密钥

永远不要泄露 API 密钥和密钥文件的位置。

永远不要将 API 密钥和密钥发送到除主网和测试网以外的任何网站。

### 永远不要显示完整密钥

当向用户显示凭证时：
- **API Key:** 显示前 5 个 + 最后 4 个字符：`su1Qc...8akf`
- **Secret Key:** 始终遮盖，仅显示最后 5 个：`***...aws1`

请求凭证时的示例响应：
账户：main
API Key: su1Qc...8akf
Secret: ***...aws1

### 列出账户

当列出账户时，显示名称和环境——永远不要密钥：
Binance 账户：
* main (主网)
* futures-keys (主网)

### 主网中的交易

当在主网中执行交易时，始终在继续之前通过询问用户编写 "CONFIRM" 来确认。

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
- 描述: 主要交易账户

### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- 描述: 期货交易账户
```

## 代理行为

1. 请求凭证：遮盖密钥（仅显示最后 5 个字符）
2. 列出账户：显示名称和环境，永远不要密钥
3. 账户选择：如果模糊，询问，默认为主网
4. 在主网中执行交易时，通过询问编写 "CONFIRM" 来确认继续
5. 新凭证：提示名称、环境、签名模式

## 添加新账户

当用户通过内联文件或消息提供新凭证时：

* 询问账户名称
* 存储在 `TOOLS.md` 中，并遮盖显示确认

## 签名请求

对于需要签名的交易端点：

1. **首先检测密钥类型**，在签名之前检查密钥格式。
2. 使用所有参数构建查询字符串，包括时间戳（Unix ms）。
3. 使用 UTF-8 根据 RFC 3986 对参数进行百分比编码。
4. 使用 HMAC SHA256、RSA 或 Ed25519（取决于账户配置）使用 secretKey 对查询字符串进行签名。
5. 将签名附加到查询字符串。
6. 包括 `X-MBX-APIKEY` 头部。

否则，不要执行步骤 4–6。

## 用户代理头部

包含以下字符串的 `User-Agent` 头部：`binance-algo/1.1.0 (Skill)`

有关实现细节，请参阅 [`references/authentication.md`](./references/authentication.md)。
