# Binance 代币化证券信息技能

## 概述

| API                 | 功能                  | 用例                                                        |
|---------------------|-----------------------|-----------------------------------------------------------------|
| Token Symbol List   | 列出所有代币化股票    | 浏览 Ondo 支持的股票代码，按类型筛选                   |
| RWA Meta            | 代币化股票元数据      | 公司信息、概念、鉴证报告                                 |
| Market Status       | 整体市场开/关状态     | 检查 Ondo 市场是否当前正在交易                           |
| Asset Market Status | 单个资产交易状态      | 检测公司行为（收益、股息、拆分、合并）                     |
| RWA Dynamic V2      | 全实时数据           | 链上价格、持有人、美国股票基本面、订单限额                 |
| Token K-Line        | K线图                | 链上代币价格技术分析 OHLC 数据                         |

## 推荐工作流

| 场景                                         | 步骤                                                                      |
|--------------------------------------------------|----------------------------------------------------------------------------|
| 查询股票的基本面和链上数据                     | API 1（通过股票代码获取 `chainId` + `contractAddress`）→ API 5（动态数据） |
| 检查股票代币是否可交易                       | API 3（整体市场状态）→ API 4（单个资产状态及原因代码）                  |
| 研究代币化股票                               | API 1（查找代币）→ API 2（公司元数据 + 鉴证报告）                        |
| 获取 K线图数据                            | API 1（查找代币）→ API 6（带时间间隔的 K线图）                          |

## 用例

1. **列出支持的股票**：获取所有 Ondo 代币化股票代码及链和合约信息
2. **公司研究**：获取公司元数据、CEO、行业、概念标签和鉴证报告
3. **市场状态检查**：确定 Ondo 市场是开市、闭市还是盘前/盘后时段
4. **公司行为检测**：检查特定资产是否因收益、股息、股票拆分、合并或维护而暂停或受限
5. **实时数据**：获取链上价格、持有人数量、流通供应量、美国股票 P/E、股息收益率、52周范围和订单限额
6. **技术分析**：获取带可配置时间间隔和时间范围的代币 K线（K线图）数据

## 关键概念：代币 ≠ 股份

每个代币代表 `multiplier` 股份的底层股票，**不是正好 1 股**。大多数代币的乘数接近 1.0（累积股息调整），但股票拆分代币可能是 5.0 或 10.0（例如乘数 = 10.0 表示 1 代币 = 10 股）。

```
referencePrice = tokenInfo.price ÷ sharesMultiplier
```

参见注释 §6 了解常见的乘数类别。

## 支持的链

| 链    | chainId |
|----------|---------|
| Ethereum | 1       |
| BSC      | 56      |

---

## API 1：Token Symbol List

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/stock/detail/list/ai
```

**请求参数**:

| 参数     | 类型    | 是否必需 | 描述                                                                                                                                                                  |
|-----------|---------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| type      | integer | 否       | 按平台筛选：`1` = Ondo Finance（目前唯一支持的代币化股票提供者）。省略则返回所有平台。**使用 `type=1` 仅检索 Ondo 代币。** |

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/stock/detail/list/ai' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": [
    {
      "chainId": "1",
      "contractAddress": "<CONTRACT_ADDRESS>",
      "symbol": "<TOKEN_SYMBOL_ON>",
      "ticker": "<UNDERLYING_TICKER>",
      "type": 1,
      "multiplier": "1.021663864228987186"
    },
    {
      "chainId": "56",
      "contractAddress": "<CONTRACT_ADDRESS>",
      "symbol": "<TOKEN_SYMBOL_ON>",
      "ticker": "<UNDERLYING_TICKER>",
      "type": 1,
      "multiplier": "1.010063782256545489"
    }
  ],
  "success": true
}
```

**响应字段**（`data` 中的每个条目）:

| 字段           | 类型    | 描述                                                   |
|-----------------|---------|---------------------------------------------------------------|
| chainId         | string  | 链 ID (`1` = Ethereum, `56` = BSC)                         |
| contractAddress | string  | 代币合约地址                                        |
| symbol          | string  | 代币符号（股票代码 + `on` 后缀，例如 `<TOKEN_SYMBOL_ON>`) |
| ticker          | string  | 底层美国股票代码                                    |
| type            | integer | 平台类型：`1` = Ondo                                     |
| multiplier      | string  | 股份乘数（见关键概念，注释 §6）                       |

---

## API 2：RWA Meta

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/meta/ai
```

**请求参数**:

| 参数       | 类型   | 是否必需 | 描述                                    |
|-----------------|--------|----------|------------------------------------------------|
| chainId         | string | 是      | 链 ID（例如 `56` 为 BSC，`1` 为 Ethereum） |
| contractAddress | string | 是      | 代币合约地址                         |

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/meta/ai?chainId=56&contractAddress=<CONTRACT_ADDRESS>' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": {
    "tokenId": "<TOKEN_ID>",
    "name": "<TOKEN_DISPLAY_NAME>",
    "symbol": "<TOKEN_SYMBOL_ON>",
    "ticker": "<UNDERLYING_TICKER>",
    "icon": "/images/web3-data/public/token/logos/<TOKEN_ID>.png",
    "dailyAttestationReports": "/images/web3-data/public/token/ondo/pdf/daily-<DATE>.pdf",
    "monthlyAttestationReports": "/images/web3-data/public/token/ondo/pdf/monthly-<MONTH>.pdf",
    "companyInfo": {
      "companyName": "<COMPANY_NAME_EN>",
      "companyNameZh": "<公司名称>",
      "homepageUrl": "",
      "description": "<COMPANY_DESCRIPTION_EN>",
      "descriptionZh": "<COMPANY_DESCRIPTION_CN>",
      "ceo": "<CEO_NAME>",
      "industry": "<INDUSTRY>",
      "industryKey": "<INDUSTRY_KEY>",
      "conceptsCn": ["概念标签A", "概念标签B", "概念标签C"],
      "conceptsEn": ["Concept Tag A", "Concept Tag B", "Concept Tag C"]
    },
    "decimals": 18
  },
  "success": true
}
```

**响应字段**（`data`）:

| 字段                     | 类型    | 描述                                                                                                                                                                  |
|---------------------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tokenId                   | string  | 代币唯一 ID                                                                                                                                                              |
| name                      | string  | 完全代币名称（例如 `<TOKEN_DISPLAY_NAME>`)                                                                                                                                |
| symbol                    | string  | 代币符号（例如 `<TOKEN_SYMBOL_ON>`)                                                                                                                                      |
| ticker                    | string  | 底层股票代码（例如 `<UNDERLYING_TICKER>`)                                                                                                                         |
| icon                      | string  | 图标图像**相对路径**。要获取完整 URL，请添加 `https://bin.bnbstatic.com`（例如 `https://bin.bnbstatic.com/images/web3-data/public/token/logos/<TOKEN_ID>.png`) |
| dailyAttestationReports   | string  | 每日鉴证报告**相对路径**。添加 `https://bin.bnbstatic.com` 获取完整 URL                                                                          |
| monthlyAttestationReports | string  | 每月鉴证报告**相对路径**。添加 `https://bin.bnbstatic.com` 获取完整 URL                                                                        |
| companyInfo               | object  | 公司详细信息（见下文）                                                                                                                                                  |
| decimals                  | integer | 代币小数位数（通常 `18`)                                                                                                                                              |

**公司信息字段**（`data.companyInfo`）:

| 字段         | 类型     | 描述                                                           |
|---------------|----------|-----------------------------------------------------------------------|
| companyName   | string   | 英文公司名称                                               |
| companyNameZh | string   | 中文公司名称                                               |
| homepageUrl   | string   | 公司主页 URL                                                  |
| description   | string   | 英文公司描述（中文）                                         |
| descriptionZh | string   | 中文公司描述（中文）                                         |
| ceo           | string   | CEO 名称                                                              |
| industry      | string   | 行业分类                                               |
| industryKey   | string   | 行业 i18n 键                                                     |
| conceptsCn    | string[] | 中文概念/主题标签                                         |
| conceptsEn    | string[] | 英文概念/主题标签（例如 `Concept Tag A`, `Concept Tag B`) |

---

## API 3：Market Status

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/market/status/ai
```

**请求参数**: 无

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/market/status/ai' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": {
    "openState": false,
    "reasonCode": "MARKET_PAUSED",
    "reasonMsg": "Paused for session transition",
    "nextOpen": "2026-03-23T08:01:00Z",
    "nextClose": "2026-03-23T13:29:00Z",
    "nextOpenTime": 1774252860000,
    "nextCloseTime": 1774272540000
  },
  "success": true
}
```

> **注意**：上面的示例捕获了 `openState=false`（市场关闭/暂停），因此 `nextOpen` 比 `nextClose` 早。

**响应字段**（`data`）:

| 字段         | 类型         | 描述                                                             |
|---------------|--------------|-------------------------------------------------------------------------|
| openState     | boolean      | Ondo 市场是否当前可进行交易                                  |
| reasonCode    | string\|null | 如果市场不在正常交易状态，则状态原因代码（见原因代码）                                           |
| reasonMsg     | string\|null | 人类可读的原因信息                                           |
| nextOpen      | string       | 从当前状态开始的下一个开市时间（ISO 8601 UTC）                 |
| nextClose     | string       | 从当前状态开始的下一个闭市时间（ISO 8601 UTC）                |
| nextOpenTime  | number       | 从当前状态开始的下一个开市时间（毫秒级 Unix 时间）         |
| nextCloseTime | number       | 从当前状态开始的下一个闭市时间（毫秒级 Unix 时间）        |

> **解释**：这些字段取决于状态。当 `openState=true` 时，`nextClose` 预期比 `nextOpen` 早（市场在下一个开市前关闭）。当 `openState=false` 时，`nextOpen` 预期比 `nextClose` 早（市场在下一个闭市前开市）。

---

## API 4：Asset Market Status

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/asset/market/status/ai
```

**请求参数**:

| 参数       | 类型   | 是否必需 | 描述            |
|-----------------|--------|----------|------------------------|
| chainId         | string | 是      | 链 ID               |
| contractAddress | string | 是      | 代币合约地址 |

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/asset/market/status/ai?chainId=56&contractAddress=<CONTRACT_ADDRESS>' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": {
    "openState": false,
    "marketStatus": "closed",
    "reasonCode": "MARKET_CLOSED",
    "reasonMsg": null,
    "nextOpenTime": 1774252860000,
    "nextCloseTime": 1774272540000
  },
  "success": true
}
```

**响应字段** (`data`）:

| 字段         | 类型         | 描述                                                                           |
|---------------|--------------|---------------------------------------------------------------------------------------|
| openState     | boolean      | 此特定资产是否可进行交易                                  |
| marketStatus  | string       | 当前会话：`premarket`, `regular`, `postmarket`, `overnight`, `closed`, `pause` |
| reasonCode    | string       | 状态原因代码（见原因代码）                                           |
| reasonMsg     | string\|null | 人类可读的原因信息（暂停/受限时填充）                         |
| nextOpenTime  | number       | 下一个开市时间（毫秒级 Unix 时间）                                                 |
| nextCloseTime | number       | 下一个闭市时间（毫秒级 Unix 时间）                                                |

### 原因代码

| reasonCode           | 描述                                                                |
|----------------------|----------------------------------------------------------------------------|
| `TRADING`            | 正常交易                                                             |
| `MARKET_CLOSED`      | 市场关闭（非交易时间）                                   |
| `MARKET_PAUSED`      | 市场范围交易暂停                                                   |
| `ASSET_PAUSED`       | 此特定资产暂停（见公司行为）                                     |
| `ASSET_LIMITED`      | 此特定资产有交易限制（见公司行为）                               |
| `UNSUPPORTED`        | 资产不受支持                                                     |
| `MARKET_MAINTENANCE` | 系统维护                                                         |

### 公司行为（当 `ASSET_PAUSED` 或 `ASSET_LIMITED`）

当资产暂停或受限时，`reasonMsg` 字段指示特定的公司行为：

| reasonCode      | reasonMsg          | 描述                                                |
|-----------------|--------------------|------------------------------------------------------------|
| `ASSET_PAUSED`  | `cash_dividend`    | 现金股息分配                                 |
| `ASSET_PAUSED`  | `stock_dividend`   | 股票股息分配                                |
| `ASSET_PAUSED`  | `stock_split`      | 股票拆分                                                |
| `ASSET_PAUSED`  | `merger`           | 公司合并                                             |
| `ASSET_PAUSED`  | `acquisition`      | 公司收购                                            |
| `ASSET_PAUSED`  | `spinoff`          | 企业分拆                                          |
| `ASSET_PAUSED`  | `maintenance`      | 资产级维护                                    |
| `ASSET_PAUSED`  | `corporate action` | 其他公司行为                                     |
| `ASSET_LIMITED` | `earnings`         | 收益发布 — 交易受限但未完全暂停 |

---

## API 5：RWA Dynamic V2

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v2/public/wallet-direct/buw/wallet/market/token/rwa/dynamic/ai
```

**请求参数**:

| 参数       | 类型   | 是否必需 | 描述            |
|-----------------|--------|----------|------------------------|
| chainId         | string | 是      | 链 ID               |
| contractAddress | string | 是      | 代币合约地址 |

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v2/public/wallet-direct/buw/wallet/market/token/rwa/dynamic/ai?chainId=56&contractAddress=<CONTRACT_ADDRESS>' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": {
    "symbol": "<TOKEN_SYMBOL_ON>",
    "ticker": "<UNDERLYING_TICKER>",
    "tokenInfo": {
      "price": "310.384196924055952519",
      "priceChange24h": "1.09518626611014170",
      "priceChangePct24h": "0.354098021064624509",
      "totalHolders": "1023",
      "sharesMultiplier": "1.001084338309087472",
      "volume24h": "8202859508.959922580629343392",
      "marketCap": "7116321.021286604958613714702150000306622972",
      "fdv": "7116321.021286604958613714702150000306622972",
      "circulatingSupply": "22927.459232171569002788",
      "maxSupply": "22927.459232171569002788"
    },
    "stockInfo": {
      "price": null,
      "priceHigh52w": "328.83",
      "priceLow52w": "140.53",
      "volume": "26429618",
      "averageVolume": "36255295",
      "sharesOutstanding": "5818000000",
      "marketCap": "1805815257704.157531755542",
      "turnoverRate": "0.4543",
      "amplitude": null,
      "priceToEarnings": "29.93",
      "dividendYield": "0.27",
      "priceToBook": null,
      | lastCashAmount | null
    },
    "statusInfo": {
      "openState": null,
      "marketStatus": null,
      "reasonCode": null,
      "reasonMsg": null,
      "nextOpenTime": null,
      "nextCloseTime": null
    },
    "limitInfo": {
      "maxAttestationCount": "1500",
      "maxActiveNotionalValue": "450000"
    }
  },
  "success": true
}
```

### 响应字段

**顶层** (`data`):

| 字段      | 类型   | 描述                                          |
|------------|--------|------------------------------------------------------|
| symbol     | string | 代币符号 (例如 `<TOKEN_SYMBOL_ON>`)              |
| ticker     | string | 底层股票代码 (例如 `<UNDERLYING_TICKER>`)             |
| tokenInfo  | object | 链上代币数据                                  |
| stockInfo  | object | 美国股票基本面                                |
| statusInfo | object | 市场/资产交易状态（与 API 4 响应相同）   |

**Token Info** (`data.tokenInfo`):

| 字段             | 类型   | 描述                                                                            |
|-------------------|--------|--------------------------------------------------------------------------------|
| price             | string | 链上代币价格 (USD) — 每个代币，不是每股（见关键概念，注释 §6）          |
| priceChange24h    | string | 24小时价格变化 (USD)                                                                 |
| priceChangePct24h | string | 24小时价格变化 (%)                                                                   |
| totalHolders      | string | 链上持有人数量                                                             |
| sharesMultiplier  | string | 与 API 1 中的 `multiplier` 相同（见关键概念，注释 §6）                        |
| volume24h         | string | ⚠️ **误导**：这是美国股票交易量 (USD)，**不是** 链上 DEX 交易量 |
| marketCap         | string | 链上市值 (USD) = `circulatingSupply × price`                                |
| fdv               | string | 完全稀释估值 (USD)                                                          |
| circulatingSupply | string | 流通供应量 (代币单位)                                                       |
| maxSupply         | string | 最大供应量 (代币单位)                                                           |

**Stock Info** (`data.stockInfo`):

| 字段             | 类型         | 描述                                                                      |
|-------------------|--------------|----------------------------------------------------------------------------------|
| price             | string\|null | 美国股票价格 (USD). 可能是 `null` 在非交易时间                        |
| priceHigh52w      | string       | 52周最高价格 (USD)                                                         |
| priceLow52w       | string       | 52周最低价格 (USD)                                                          |
| volume            | string       | ⚠️ 美国股票交易量在**股**（不是 USD）。乘以 `price` 获取 USD 值 |
| averageVolume     | string       | 平均每日交易量 (股)                                                    |
| sharesOutstanding | string       | 总发行股数                                                         |
| marketCap         | string       | 美国股票总市值 (USD)                                                  |
| turnoverRate      | string       | 转换率 (%)                                                                |
| amplitude         | string\|null | 当日振幅 (%)                                                           |
| priceToEarnings   | string       | P/E 比率 (TTM)                                                                  |
| dividendYield     | string       | 股息收益率 (TTM, 百分比值：`0.27` 表示 0.27%)                       |
| priceToBook       | string\|null | P/B 比率                                                                        |
| lastCashAmount    | string\|null | 最近现金股息金额（USD） per share (股)                                 |

**Status Info** (`data.statusInfo`):

与 API 4 响应相同。参见 [Asset Market Status](#api-4-asset-market-status) 了解字段细节和原因代码。

**Limit Info** (`data.limitInfo`):

| 字段                  | 类型   | 描述                                    |
|------------------------|--------|------------------------------------------------|
| maxAttestationCount    | string | 订单的最大鉴证数量                       |
| maxActiveNotionalValue | string | 订单的最大活跃名义价值 (USD)                 |

---

## API 6：Token K-Line

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/kline/ai
```

**请求参数**:

| 参数       | 类型    | 是否必需 | 默认 | 描述                                             |
|-----------------|---------|----------|---------|---------------------------------------------------------|
| chainId         | string  | 是      | -       | 链 ID (例如 `56` 为 BSC，`1` 为 Ethereum)          |
| contractAddress | string  | 是      | -       | 代币合约地址                                  |
| interval        | string  | 是      | -       | K线图时间间隔 (见时间间隔参考)                |
| limit           | integer | 否       | 300     | 返回的 K线数量（最多 300）                   |
| startTime       | long    | 否       | 开始时间 (ms), 基于蜡烛开盘时间         |
| endTime         | long    | 否       | 结束时间 (ms), 基于蜡烛开盘时间减 1ms |

> **关于 `startTime` / `endTime`**: 两者都参考蜡烛的开盘时间。如果省略，返回最新的蜡烛。当两者都提供时，`endTime` 应该是目标蜡烛的开盘时间减 1ms。

**时间间隔参考**:

| 时间间隔 | 描述 |
|----------|-------------|
| 1m       | 1 分钟    |
| 5m       | 5 分钟   |
| 15m      | 15 分钟  |
| 1h       | 1 小时      |
| 4h       | 4 小时     |
| 12h      | 12 小时    |
| 1d       | 1 天       |

**请求头**: `Accept-Encoding: identity`

**示例**:
```bash
curl 'https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/kline/ai?chainId=56&contractAddress=<CONTRACT_ADDRESS>&interval=1d&limit=5' \
  -H 'Accept-Encoding: identity' \
  -H 'User-Agent: binance-web3/1.1 (Skill)'
```

**响应**:

```json
{
  "code": "000000",
  "data": {
    "klineInfos": [
      [1773619200000, "302.935406291919976543", "306.960384694362870577", "302.25959298411397863", "305.249336787737745037", "0", 1773705599999],
      [1773705600000, "305.644964527245747627", "311.890874865402466994", "303.302517784917770672", "311.028506552196415779", "0", 1773791999999]
    ],
    "decimals": 5
  },
  "success": true
}
```

**K线数组格式**（`data.klineInfos[]` 中的每个元素）:

| Index | Field     | 类型   | 描述                 |
|-------|-----------|--------|-----------------------------|
| 0     | openTime  | number | 蜡烛开盘时间 (ms)  |
| 1     | open      | string | 开盘价格 (USD)            |
| 2     | high      | string | 最高价格 (USD)            |
| 3     | low       | string | 最低价格 (USD)             |
| 4     | close     | string | 收盘价格 (USD)           |
| 5     | -         | string | 保留字段              |
| 6     | closeTime | number | 蜡烛收盘时间 (ms) |

**响应字段**:

| 字段      | 类型    | 描述                               |
|------------|---------|-------------------------------------------|
| klineInfos | array   | 蜡烛数组 (见格式) (array) |
| decimals   | integer | 价格小数位数提示              |

---

## User Agent Header

包含以下字符串的 `User-Agent` 头: `binance-web3/1.1 (Skill)`

## 注释

1. **`volume24h` in tokenInfo 是误导性的**: `tokenInfo.volume24h` 从 RWA Dynamic API 返回的**美国股票每日交易量 (USD)**，**不是** 链上 DEX 交易量。实际链上买入/卖出交易量，请使用 Binance 链上动态 API (`/market/token/dynamic/info`)，使用 `volume24hBuy` + `volume24hSell` 字段。

2. **`dividendYield` 是百分比值，不是原始小数**: 值 `0.27` 表示 0.27% 股息收益率。

3. **图标和报告 URL 是相对路径 — 需要添加域名才能使用**: API 返回的 `icon`, `dailyAttestationReports`, 和 `monthlyAttestationReports`（例如 `/images/web3-data/public/token/logos/...`）。要构造完整 URL，请添加 `https://bin.bnbstatic.com`。示例: `/images/web3-data/public/token/logos/<TOKEN_ID>.png` → `https://bin.bnbstatic.com/images/web3-data/public/token/logos/<TOKEN_ID>.png`。

4. **无需 API 密钥**: 所有端点都是公开 API。无需身份验证。

5. **多链部署**: 每个支持的股票可能部署在多个链上（例如 Ethereum 和 BSC）。`stockInfo` 和 `tokenInfo.price` 在所有链上相同。`tokenInfo.totalHolders` 是跨链聚合。`tokenInfo.circulatingSupply` 和 `tokenInfo.marketCap` 是链特定的。

6. **`multiplier` / `sharesMultiplier` — 对价格比较至关重要**: 每个代币代表 `multiplier` 股份的底层股票，不是正好 1 股。乘数从 1.0 开始，随着现金股息的再投资（累积股息调整）而增加。一些代币也反映了股票拆分（例如乘数 = 10.0 表示 1 代币 = 10 股）。

   **公式**:
   ```
   referencePrice = tokenInfo.price ÷ sharesMultiplier
   ```

   > `tokenInfo.price` 和 `stockInfo.price` 来自不同的来源（链上预言机 vs 股票源）并具有不同的更新频率，所以一个小溢价/折价（通常在 ±0.1% 范围内）是正常的。

   **常见乘数类别**:

   | Multiplier         | Cause                                                   |
   |--------------------|---------------------------------------------------------|
   | Exactly 1.0        | 没有支付股息，或新上市                  |
   | Slightly above 1.0 | 累积现金股息再投资 (随时间增长)                 |
   | 5.0, 10.0          | 股票拆分反映在代币结构中                |

   > 乘数值会随着股息的积累而变化。在查询时从 API 读取它——永远不要硬编码。
