# Binance 法币功能

使用 **公开API** 查询Binance法币支付功能、可用支付方式、价格以及支持的国家/货币（无需认证）。订单和支付历史记录，请参阅 [认证端点](./references/sapi-endpoints.md)。

## 基础URL

```
https://www.binance.com/bapi/fiat/v1/public/fiatpayment/agent
```

## 可用API

### 1. get_capabilities

查询一个国家支持的法币、加密货币和业务类型。

```bash
curl "https://www.binance.com/bapi/fiat/v1/public/fiatpayment/agent/get-capabilities?country={COUNTRY_CODE}"
```

可选：`businessType`（BUY、SELL、DEPOSIT、WITHDRAW）用于筛选。

**响应：** `data.supportedBusinessTypes`, `data.fiatCurrencies[]`（包含 `code`, `name`, `supportedBusinessTypes`），`data.cryptoCurrencies[]`

### 2. get_buy_and_sell_payment_methods

```bash
curl "https://www.binance.com/bapi/fiat/v1/public/fiatpayment/agent/get-buy-and-sell-payment-methods?businessType={BUY|SELL}&fiatCurrency={FIAT}&cryptoCurrency={CRYPTO}&country={COUNTRY_CODE}"
```

所有4个参数都必需。

**响应：** `data.paymentMethods[]` 和 `data.p2pPaymentMethods[]`，每个包含 `code`, `paymentMethodName`, `fiatMinLimit`, `fiatMaxLimit`, `cryptoMinLimit`, `cryptoMaxLimit`, `quotation`, `suspended`

### 3. get_deposit_and_withdraw_payment_methods

```bash
curl "https://www.binance.com/bapi/fiat/v1/public/fiatpayment/agent/get-deposit-and-withdraw-payment-methods?businessType={DEPOSIT|WITHDRAW}&fiatCurrency={FIAT}&country={COUNTRY_CODE}"
```

所有3个参数都必需。没有 `cryptoCurrency`，没有 `quotation`，没有P2P方法。

**响应：** `data.paymentMethods[]` 包含 `code`, `paymentMethodName`, `fiatMinLimit`, `fiatMaxLimit`, `suspended`

### 4. get_price

```bash
curl "https://www.binance.com/bapi/fiat/v1/public/fiatpayment/agent/get-price?fiatCurrency={FIAT}&cryptoCurrency={CRYPTO}&country={COUNTRY_CODE}"
```

可选：`businessType`（BUY 或 SELL，默认为 BUY）。

**响应：** `data.bestPrice` — 指示性参考价格，可能与执行价格不同

## 推荐工作流程

1. **首先使用 `get_capabilities`** — 在进行其他调用前确认支持情况
2. **支付方式API** — BUY/SELL → `get_buy_and_sell_payment_methods`；DEPOSIT/WITHDRAW → `get_deposit_and_withdraw_payment_methods`
3. **`get_price`** — 如果用户需要汇率信息，则添加此步骤

对于简单的价格查询（例如，“BTC是多少美元？”），可跳过步骤1。

## 调用API

使用 `WebFetch` 或 `Bash`（curl）。所有响应遵循：

```json
{ "code": "000000", "message": null, "data": { ... }, "success": true }
```

`code: "000000"` = 成功；否则检查 `message`。

## 操作链接

在展示API结果后，始终包含一个相关的操作链接，以便用户可以直接在Binance上操作。根据对话上下文中的法币、加密货币和业务类型动态构建URL。

### URL模板

| 业务类型 | URL模板 | 示例 |
|---|---|---|
| BUY | `https://www.binance.com/en/crypto/buy/{FIAT}/{CRYPTO}` | [使用USD购买BTC](https://www.binance.com/en/crypto/buy/USD/BTC) |
| SELL | `https://www.binance.com/en/crypto/sell/{FIAT}/{CRYPTO}` | [使用BTC出售USD](https://www.binance.com/en/crypto/sell/USD/BTC) |
| DEPOSIT | `https://www.binance.com/en/fiat/deposit/{FIAT}` | [存款USD](https://www.binance.com/en/fiat/deposit/USD) |
| WITHDRAW | `https://www.binance.com/en/fiat/withdraw/{FIAT}` | [取款USD](https://www.binance.com/en/fiat/withdraw/USD) |

### 带语言感知的URL

将 `/en/` 语言片段替换为匹配用户的语言。支持的地区：

```
en, zh-CN, zh-TC, ru, es, es-LA, fr, vi, en-TR, it, pl, id, uk-UA, ar,
en-AU, pt-BR, en-IN, en-NG, ro, bg, cs, lv, sv, pt, es-MX, el, sk, sl,
es-AR, fr-AF, en-KZ, en-ZA, en-NZ, en-BH, ar-BH, ru-UA, de, kk-KZ,
ru-KZ, ja, da-DK, en-AE, en-JP, hu, lo-LA, si-LK, az-AZ, uz-UZ, pt-AO
```

常见映射示例：

| 用户语言 | 地区 | 示例URL |
|---|---|---|
| 英语 | `en` | `https://www.binance.com/en/crypto/buy/USD/BTC` |
| 简体中文 | `zh-CN` | `https://www.binance.com/zh-CN/crypto/buy/CNY/BTC` |
| 葡萄牙语 (BR) | `pt-BR` | `https://www.binance.com/pt-BR/crypto/buy/BRL/BTC` |
| 土耳其语 | `en-TR` | `https://www.binance.com/en-TR/crypto/buy/TRY/BTC` |

对于区域性英语变体（en-AU、en-IN、en-NG、en-AE、en-NZ等），使用特定区域地区，而不是简单的 `en` — 这确保用户看到区域适内容。

如果用户语言不明确，默认为 `en`。

在涉及特定法币/加密货币对或业务类型的对话中，始终至少包含一个操作链接。对于一般性问题，包含 `get_capabilities` 返回的所有相关链接。以行动号召格式呈现，例如： "准备购买？[在Binance上使用USD购买BTC](https://www.binance.com/en/crypto/buy/USD/BTC)"

## 展示结果

- 表格格式展示支付方式（名称、限额、价格）；标记暂停状态的方法
- 注意价格是指示性/参考价格
- 使用用户的语言响应
- **始终以相关操作链接结束**

### 价格排序和最佳价值逻辑

价格方向取决于业务类型 — 始终应用正确的比较：

| 业务类型 | 更好的价格方向 | 理由 |
|---|---|---|
| **BUY** | **较低价格更好** | 您支付更少的法币购买每个单位的加密货币 — 同样的法币可以购买更多加密货币 |
| **SELL** | **较高价格更好** | 您出售每个单位的加密货币可以获得更多法币 |

在总结时：对于BUY，突出显示 **最低** `quotation`；对于SELL，突出显示 **最高** `quotation`。示例（BUY USD/BTC）：$70,236 胜过 $74,291 — 每美元可以购买更多BTC。

### 钱包支付方式（BUY）

如果BUY响应中包含 `code` 包含 `WALLET`（不区分大小写）的支付方式，它表示使用用户的Binance法币钱包余额购买加密货币。

当这种情况发生时，主动提及：
> "一种可用的支付方式是您的Binance法币钱包余额。如果您的钱包余额不足，您需要先存款。您希望我为您查找可用的存款方式吗？"

如果用户确认，调用 `get_deposit_and_withdraw_payment_methods`，使用相同的法币和国家，`businessType=DEPOSIT`，并展示结果以及 [存款操作链接](#url-templates)。

## 订单和支付历史（认证）

参见 [`references/sapi-endpoints.md`](./references/sapi-endpoints.md) 获取认证端点（订单/支付历史记录、存款/取款记录）。需要Binance API密钥和密钥。

## 国家代码参考

使用ISO 3166-1 alpha-2代码：BR、GB、DE、FR、JP、KR、AU等。**永远不要将 `US` 作为国家参数** — 美国用户不受Binance法币支付API支持。

### 国家推断规则

使用以下优先级顺序确定 `country` 参数：

1. **明确上下文** — 如果国家已从对话中得知（用户已声明或在前一回合中推断），则无需重新推断。

2. **法币→国家映射** — 直接从货币映射。示例：
   - `SGD` → `SG`, `BRL` → `BR`, `JPY` → `JP`, `KRW` → `KR`, `AUD` → `AU`, `GBP` → `GB`, `CAD` → `CA`, `INR` → `IN`, `TRY` → `TR`, `MXN` → `MX`, `NGN` → `NG`
   - `EUR` → `FR`（因为用户未指定国家，使用 `FR` 作为EUR的默认值）
   - `USD` → `SG`（因为用户未指定国家，使用 `SG` 作为USD的默认值）

   > **强制要求**：`US` 在任何情况下都绝对不能作为国家参数使用。 

3. **空结果** — 如果API返回无支付方式或不受支持的组合，请询问：*"根据当前设置未找到结果。您想尝试其他国家吗？如果是，请告诉我哪个国家。"* 然后使用用户提供的国家。
