# Binance Onchain-Pay Open API 技能

使用自动 RSA SHA256 请求签名调用 Binance Onchain-Pay Open API 端点。

## 用例与场景

此技能适用于以下场景：

### 1. 💳 法币-加密货币购买与发送
**使用场景**：用户希望用法币购买加密货币并直接发送到外部链上钱包地址
- 使用信用卡购买 USDT（美元/欧元/新台币）→ 发送到 BSC 上的 MetaMask 地址
- 使用 Google Pay 购买 BTC → 转账到硬件钱包
- 使用 P2P 购买 USDC → 发送到 DeFi 协议合约地址

**关键 API**：`trading-pairs` → `payment-method-list` → `estimated-quote` → `pre-order`

### 2. 🔄 直接加密货币转账（主要发送）
**使用场景**：用户在 Binance 账户中有加密货币并希望发送到外部地址
- 从 Binance 现货发送现有 USDT 到朋友的钱包地址
- 转账 ETH 到 Uniswap 合约进行交易
- 将加密货币从 Binance 转移到自托管钱包（Trust Wallet、Ledger 等）

**关键 API**：带 `SEND_PRIMARY` 定制的 `pre-order`

### 3. 🔗 跨链桥接操作
**使用场景**：用户需要在一条链上购买加密货币并转移到另一网络
- 在以太坊上购买 USDC → 桥接到 Polygon 以获得更低费用
- 在 BSC 上购买代币 → 转移到 Base 网络
- 在 Solana 上法币到加密货币 → 发送到 Arbitrum 进行 DeFi

**关键 API**：`crypto-network` → 带网络选择的 `pre-order`

### 4. 🏪 商户支付集成
**使用场景**：为电子商务或服务集成加密货币支付网关
- 接受法币支付并自动转换为加密货币
- 启用“使用加密货币支付”结账流程
- 使用加密货币处理订阅支付

**关键 API**：带 `externalOrderId` 追踪的 `pre-order`

### 5. 🤖 智能合约交互（Onchain-Pay Easy）
**使用场景**：在一个交易中购买加密货币并执行智能合约
- 购买 USDT 并存入借贷协议
- 购买代币并在 DeFi 池中质押
- 法币直接上币到 GameFi 或 NFT 市场place

**关键 API**：带 `ON_CHAIN_PROXY_MODE` 定制的 `pre-order`

### 6. 📊 查询与监控
**使用场景**：检查订单状态、可用网络或支付方式
- 监控订单处理状态（待处理、完成、失败）
- 列出支持的法币货币和加密货币
- 检查特定国家/金额的可用支付方式
- 验证网络费用和限额

**关键 API**：`order`、`crypto-network`、`trading-pairs`、`payment-method-list`

---

## 快速参考

| 端点 | API 路径 | 必填参数 | 可选参数 |
|------|----------|----------|----------|
| 支付方式列表 (v1) | `papi/v1/ramp/connect/buy/payment-method-list` | fiatCurrency, cryptoCurrency, totalAmount, amountType | network, contractAddress |
| 支付方式列表 (v2) | `papi/v2/ramp/connect/buy/payment-method-list` | (无) | lang |
| 交易对 | `papi/v1/ramp/connect/buy/trading-pairs` | (无) | (无) |
| 预估报价 | `papi/v1/ramp/connect/buy/estimated-quote` | fiatCurrency, requestedAmount, payMethodCode, amountType | cryptoCurrency, contractAddress, address, network |
| 预订单 | `papi/v1/ramp/connect/buy/pre-order` | externalOrderId, merchantCode, merchantName, ts | fiatCurrency, fiatAmount, cryptoCurrency, requestedAmount, amountType, address, network, payMethodCode, payMethodSubCode, redirectUrl, failRedirectUrl, redirectDeepLink, failRedirectDeepLink, customization, destContractAddress, destContractABI, destContractParams, affiliateCode, gtrTemplateCode, contractAddress |
| 获取订单 | `papi/v1/ramp/connect/order` | externalOrderId | (无) |
| 加密货币网络 | `papi/v1/ramp/connect/crypto-network` | (无) | (无) |
| P2P 交易对 | `papi/v1/ramp/connect/buy/p2p/trading-pairs` | (无) | fiatCurrency |

---

## 如何执行请求

### 第一步：收集凭证

除非用户另有指定，否则使用默认账户（prod）。您需要：

- **BASE_URL**：API 基础 URL
- **CLIENT_ID**：客户端标识符
- **API_KEY**：签名访问令牌
- **PEM_PATH**：RSA 私钥 PEM 文件的绝对路径

使用 `.local.md` 中标记为 `(default)` 的账户。

### 第二步：构建 JSON 正文

从用户指定的参数构建紧凑的 JSON 正文。删除用户未提供的任何参数。

**重要提示：地址和网络验证**
- `address`（目标钱包地址）和 `network`（区块链网络）对所有预订单请求都是必需的
- 如果用户在 `.local.md` 中配置了 `Default Address` 和 `Default Network`，则自动使用它们
- 如果未配置或未由用户提供，则在继续之前要求用户提供这两个值

### 第三步：使用捆绑脚本签名和调用

```bash
bash <skill_path>/scripts/sign_and_call.sh \
  "<BASE_URL>" \
  "<API_PATH>" \
  "<CLIENT_ID>" \
  "<API_KEY>" \
  "<PEM_PATH>" \
  '<JSON_BODY>'
```

### 第四步：返回结果

以可读格式向用户显示 JSON 响应。

---

## 认证

有关完整签名详情，请参阅 [`references/authentication.md`](./references/authentication.md)。

摘要：
1. Payload = `JSON_BODY` + `TIMESTAMP`（毫秒）
2. 使用 PEM 私钥通过 RSA SHA256 签名 Payload
3. 对签名进行 Base64 编码（单行）
4. 作为 POST 请求发送，带有以下标头：`X-Tesla-ClientId`、`X-Tesla-SignAccessToken`、`X-Tesla-Signature`、`X-Tesla-Timestamp`、`Content-Type: application/json`

---

## 参数参考

### 支付方式列表 v1 (`buy/payment-method-list`)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| fiatCurrency | string | 是 | 法币货币代码（例如，`USD`、`EUR`、`BRL`、`UGX`） |
| cryptoCurrency | string | 是 | 加密货币代码（例如，`BTC`、`USDT`、`USDC`、`SEI`） |
| totalAmount | number | 是 | 金额值 |
| amountType | number | 是 | `1` = 法币金额，`2` = 加密货币金额 |
| network | string | 否 | 区块链网络（例如，`BSC`、`ETH`、`SOL`、`BASE`、`SEI`） |
| contractAddress | string | 否 | 代币合约地址（非原生代币需要） |

### 支付方式列表 v2 (`v2/buy/payment-method-list`)

无需指定法币/加密货币参数即可获取所有可用支付方式。v1 的简化版本。

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| lang | string | 否 | 用于本地化支付方式名称的语言代码（例如，`en`、`cn`、`es`） |

**与 v1 的区别**：
- **更简单**：无需指定 fiatCurrency、cryptoCurrency 或金额
- **更全面**：返回商户的所有可用支付方式
- **用例**：在用户输入之前显示所有选项

**响应格式**：与 v1 相同，返回支付方式列表及其限额和属性。

### 预估报价 (`buy/estimated-quote`)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| fiatCurrency | string | 是 | 法币货币代码 |
| cryptoCurrency | string | 否 | 加密货币代码（如果提供 contractAddress 则可选） |
| requestedAmount | number | 是 | 金额值 |
| payMethodCode | string | 是 | 支付方式（例如，`BUY_CARD`、`BUY_GOOGLE_PAY`、`BUY_P2P`、`BUY_WALLET`） |
| amountType | number | 是 | `1` = 法币金额，`2` = 加密货币金额 |
| network | string | **是*** | 区块链网络（可使用 `.local.md` 中的默认值） |
| contractAddress | string | 否 | 代币合约地址 |
| address | string | **是*** | 接收加密货币的目标钱包地址 |

\* 推荐：应提供这些参数。如果用户未指定，请检查 `.local.md` 中的默认值。如果不存在默认值，则在继续之前要求用户提供。

### 预订单 (`buy/pre-order`)

创建购买预订单并返回支付的重定向链接。

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| externalOrderId | string | 是 | 合作伙伴的唯一订单 ID（必须唯一） |
| merchantCode | string | 是 | Binance 分配给您的商户代码（由用户提供） |
| merchantName | string | 是 | 商户显示名称（由用户提供） |
| ts | number | 是 | 当前时间戳（毫秒） |
| fiatCurrency | string | 否* | 法币货币代码（例如，`TWD`、`USD`、`EUR`） |
| fiatAmount | number | 否* | 要花费的法币金额 |
| cryptoCurrency | string | 否* | 要购买的加密货币（例如，`USDT`、`BTC`、`ETH`） |
| requestedAmount | number | 否* | 金额值（基于 amountType 的法币或加密货币） |
| amountType | number | 否* | `1` = 法币金额，`2` = 加密货币金额 |
| address | string | 否 | 接收加密货币的目标钱包地址 |
| network | string | 否 | 区块链网络（例如，`BSC`、`ETH`、`SOL`） |
| payMethodCode | string | 否 | 支付方式代码（例如，`BUY_CARD`、`BUY_P2P`、`BUY_GOOGLE_PAY`、`BUY_APPLE_PAY`、`BUY_PAYPAL`、`BUY_WALLET`、`BUY_REVOLUT`） |
| payMethodSubCode | string | 否 | 支付方式子代码（例如，`card`、`GOOGLE_PAY`、`WECHAT`） |
| redirectUrl | string | 否 | 成功重定向 URL |
| failRedirectUrl | string | 否 | 失败重定向 URL |
| redirectDeepLink | string | 否 | 成功的移动应用深度链接 |
| failRedirectDeepLink | string | 否 | 失败的移动应用深度链接 |
| customization | object | 否 | 自定义配置对象（见下文自定义部分） |
| destContractAddress | string | 否 | 目标合约地址（用于 Onchain-Pay Easy 模式） |
| destContractABI | string | 否 | 合约 ABI 名称（用于 Onchain-Pay Easy 模式） |
| destContractParams | object | 否 | 合约参数（用于 Onchain-Pay Easy 模式） |
| affiliateCode | string | 否 | 用于佣金跟踪的关联代码 |
| gtrTemplateCode | string | 否 | GTR 模板代码（例如，`OTHERS`） |
| contractAddress | string | 否 | 代币合约地址（用于非原生代币） |

\* 提供 `fiatAmount` 或 (`requestedAmount` + `amountType`)。如果未提供 `fiatCurrency`，系统将自动选择可用法币。

**响应示例**：
```json
{
  "code": "000000",
  "message": "success",
  "data": {
    "link": "https://app.binance.com/uni-qr/ccnt?...",
    "linkExpireTime": 1772852565045
  },
  "success": true
}
```

### 获取订单 (`order`)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| externalOrderId | string | 是 | 要查询的外部订单 ID |

---

## 自定义选项

预订单 API 中的 `customization` 字段接受各种标志来定制购买流程行为。每个商户必须在 `db.merchant_info` 表中配置相应的权限。

### 可用自定义标志

| 标志 | 代码 | 类型 | 可用性 | 描述 | 用例 |
|------|------|------|--------|------|------|
| `LOCK_ORDER_ATTRIBUTES` | 1 | array | Open API ✓ | 锁定特定订单属性，用户无法修改。值：`1`=法币货币，`2`=加密货币，`3`=金额，`4`=支付方式，`5`=网络，`6`=地址，`7`=法币金额，`8`=加密货币金额 | 固定参数订单 |
| `SKIP_CASHIER` | 2 | boolean | Open API ✓ | 跳过收银页面，直接进入支付。减少结账流程中的用户摩擦。 | 简化支付体验 |
| `AUTO_REDIRECTION` | 3 | boolean | Open API ✓ | 订单完成后自动重定向到 `redirectUrl`，不显示成功页面。 | 无缝用户体验 |
| `HIDE_SEND` | 6 | boolean | Open API ✓ | 在 UI 中隐藏“发送”选项卡。当只需要购买流程时很有用。 | 购买仅集成 |
| `SEND_PRIMARY` | 7 | boolean | Open API ✓ | 启用发送加密货币功能。如果用户 Binance 账户余额不足，将自动触发购买流程。 | 将加密货币发送到外部地址 |
| `MERCHANT_DISPLAY_NAME` | 8 | string | Open API ✓ | 覆盖 UI 中向用户显示的显示名称。 | 自定义品牌 |
| `NET_RECEIVE` | 9 | boolean | Open API ✓ | 用户在扣除所有费用后接收净金额。总成本更透明。 | 更好的 UX，显示最终接收金额 |
| `P2P_EXPRESS` | 10 | boolean | Open API ✓ | 启用 P2P 快速模式，以实现更快的 P2P 订单匹配。 | 快速 P2P 交易 |
| `OPEN_NETWORK` | 11 | boolean | Web3 仅限 | 允许用户选择不同网络。默认锁定到预选网络。**注意**：目前仅适用于 Web3 入口，Open API 中不可用。 | 多网络支持（Web3 仅限） |
| `ON_CHAIN_PROXY_MODE` | 12 | boolean | Open API ✓ | 启用 Onchain-Pay Easy 模式。购买加密货币后，Onchain-Pay 将执行智能合约交互，而不是直接提现到用户钱包。需要 `destContractAddress`、`destContractABI` 和 `destContractParams`。 | 法币到智能合约集成 |
| `SEND_PRIMARY_FLEXIBLE` | 13 | boolean | Open API ✓ | 更灵活的 Send Primary 模式，提供更多选项。 | 高级发送加密货币场景 |

### 自定义示例

**示例 1：基本信用卡支付**
```json
{
  "customization": {}
}
```

**示例 2：Onchain-Pay Easy（链上代理）**
```json
{
  "customization": {
    "ON_CHAIN_PROXY_MODE": true,
    "NET_RECEIVE": true,
    "SEND_PRIMARY": true
  },
  "destContractAddress": "0x128...974",
  "destContractABI": "depositFor",
  "destContractParams": {
    "accountType": 2
  }
}
```

**示例 3：发送加密货币**
```json
{
  "customization": {
    "SEND_PRIMARY_FLEXIBLE": true,
    "SEND_PRIMARY": true
  }
}
```

**示例 4：P2P 与自动重定向**
```json
{
  "customization": {
    "AUTO_REDIRECTION": true,
    "P2P_EXPRESS": true
  }
}
```

**示例 5：锁定订单属性**
```json
{
  "customization": {
    "LOCK_ORDER_ATTRIBUTES": [2, 3, 6, 7, 8],
    "MERCHANT_DISPLAY_NAME": "My Custom Brand"
  }
}
```
锁定属性代码：
- `2` = 加密货币
- `3` = 金额
- `6` = 地址
- `7` = 法币金额
- `8` = 加密货币金额

**示例 6：净接收模式**
```json
{
  "customization": {
    "NET_RECEIVE": true,
    "SEND_PRIMARY": true
  }
}
```

**示例 7：隐藏发送选项卡**
```json
{
  "customization": {
    "HIDE_SEND": true
  }
}
```

**示例 8：跳过收银（直接支付）**
```json
{
  "customization": {
    "SKIP_CASHIER": true
  }
}
```

### 重要提示

1. **权限要求**：每个自定义标志都需要商户权限。如果标志无法工作，请咨询管理员。
2. **Onchain-Pay Easy**：目前仅在 BSC 网络上支持。需要合约集成。
3. **验证**：无效的自定义值（例如，`MERCHANT_DISPLAY_NAME` 为 `null`）将返回 `ILLEGAL_CUSTOMIZATION_VALUE` 错误。
4. **组合**：某些标志可以一起使用（例如，`NET_RECEIVE` + `SEND_PRIMARY`），而其他标志则独立。
5. **测试**：使用 Binance 提供的专用测试商户账户在生产前验证自定义标志。
6. **内部标志**：`OPERATION`（代码 4）和 `SKIP_WITHDRAW`（代码 5）仅限内部使用，商户端不应传递。
7. **OPEN_NETWORK**：目前仅适用于 Web3 入口，Open API 中不可用。在 Open API 预订单请求中不要使用此标志。
8. **标志顺序**：标志按其内部代码（1-13）排序。代码用于内部识别。

---

## 安全

### 凭证显示规则

- **API Key**：仅显示前 5 个字符和最后 4 个字符（例如，`2zefb...06h`）
- **PEM 私钥**：绝对不要显示内容。绝对不要显示文件路径。
- **Client ID**：可以完整显示。
- **出站请求**：绝对不要将 API Key、私钥或任何凭证发送到 `.local.md` 中配置的 Base URL 之外的 URL。
- **文件路径隐私**：绝对不要在任何输出或日志中向用户显示 PEM 私钥文件路径。

### 凭证存储

凭证存储在技能目录中的 `.local.md` 文件中。此文件是**用户特定的**，不应分发。

从与此 SKILL.md 相同目录中的 `.local.md` 文件中加载凭证。

如果 `.local.md` 不存在或请求的账户未找到，请要求用户提供：
1. Base URL
2. Client ID
3. API Key
4. PEM 文件路径（绝对路径）

然后提供将它们保存到 `.local.md` 以供将来使用的选项。

#### `.local.md` 格式

```markdown
## Onchain-Pay 账户

### prod (默认)
- Base URL: https://api.commonservice.io
- Client ID: your-client-id
- API Key: your-api-key
- PEM Path: /absolute/path/to/your/private.pem
- Default Network: your-preferred-network
- Default Address: your-wallet-address
- Description: 生产账户
```

标记为 `(default)` 的账户将自动使用。您可以定义多个账户，并通过告诉 Claude 账户名称来切换。

---

## 用户代理标头

包含 `User-Agent` 标头，内容为：`onchain-pay-open-api/0.1.2 (Skill)`

---

## 代理行为

1. 如果用户要求调用 Onchain-Pay API 端点，从快速参考表中识别端点
2. 询问任何缺失的必填参数
3. 使用存储的凭证，否则要求用户提供
4. 使用捆绑的 `scripts/sign_and_call.sh` 执行请求
5. 以可读格式显示响应
6. 如果请求失败，显示错误并建议修复

---

## 预订单 API 重要提示

### 跨平台时间戳生成

生成 `ts` 参数和 `externalOrderId` 的时间戳时，使用以下方法以实现跨平台兼容性：

```bash
# 生成毫秒时间戳（在 macOS、Linux、BSD 上工作）
TIMESTAMP=$(($(date +%s) * 1000))

# 生成唯一订单 ID
ORDER_ID="order$(date +%s)"
```

**不要使用** `date +%s%3N` 或 `date +%s000`，因为它们不是可移植的：
- `date +%s%3N` 在 macOS 上不起作用（输出字面量 'N'）
- `date +%s000` 只是附加 '000' 而没有实际的毫秒精度

### 订单 ID 格式

`externalOrderId` 必须是有效的字符串，不包含特殊字符。推荐格式：
- `order1773744500`（简单的数字后缀）
- `order_1773744500`（带下划线分隔符）
- `txn-abc123`（自定义前缀，包含字母数字）

**避免**：`order_${TIMESTAMP}`，其中 TIMESTAMP 包含 shell 变量语法错误

### 示例预订单请求

```bash
# 正确创建预订单的方式
TIMESTAMP=$(($(date +%s) * 1000))
ORDER_ID="order$(date +%s)"

bash /path/to/scripts/sign_and_call.sh \
  "https://api.commonservice.io" \
  "papi/v1/ramp/connect/buy/pre-order" \
  "<YOUR_CLIENT_ID>" \
  "<YOUR_API_KEY>" \
  "/path/to/private.pem" \
  "{\"externalOrderId\":\"$ORDER_ID\",\"merchantCode\":\"<YOUR_MERCHANT_CODE>\",\"merchantName\":\"<YOUR_MERCHANT_NAME>\",\"ts\":$TIMESTAMP,\"fiatCurrency\":\"USD\",\"requestedAmount\":100,\"cryptoCurrency\":\"BNB\",\"amountType\":1,\"address\":\"0x...\",\"network\":\"BSC\",\"payMethodCode\":\"BUY_CARD\"}"
```
