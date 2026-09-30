---
name: binance-tokenized-securities-info
description: '在Binance Web3上查询Ondo代币化的美国股票数据。

  涵盖：支持的股票代币列表、RWA元数据（公司信息、鉴证报告）、市场和每项资产的交易状态（含盈余、股息、拆分的企业行动代码）、实时链上数据（代币价格、持有人、流通供应量、市值）、美国股票基本面（市盈率、股息收益率、52周区间）以及代币K线/蜡烛图。


  当用户询问以下内容时使用此技能：

  - 特定股票代码的代币化股票价格、持有人或链上数据

  - 股票代币是否可交易、暂停或停牌

  - Ondo RWA代币列表或哪些美国股票在链上可用

  - 影响代币的企业行动（股息、股票拆分、盈余暂停）

  - 股票代币K线或蜡烛图数据

  - 链上代币价格与美国股票价格的比较


  不适用于一般加密代币（BTC、ETH、SOL等）——请使用query-token-info查询这些代币。'
---

# Binance 证券通证信息技能

## 概述

| API                 | 功能                  | 应用场景                                                        |
|---------------------|-----------------------|-----------------------------------------------------------------|
| Token Symbol List   | 列出所有证券通证      | 浏览 Ondo 支持的行情代码，按类型筛选                           |
| RWA Meta            | 证券通证元数据        | 公司信息、概念、鉴证报告                                     |
| Market Status       | 整体市场开闭状态      | 检查 Ondo 市场是否当前交易                                   |
| Asset Market Status | 单一资产交易状态      | 检测公司行为（财报、分红、拆分、合并）                         |
| RWA Dynamic V2      | 全实时数据            | 链上价格、持有人、美股基本面、订单限额                         |
| Token K-Line        | K线图                 | 链上通证价格技术分析 OHLC 数据                             |

## 推荐工作流

| 场景                                         | 步骤                                                                      |
|--------------------------------------------------|----------------------------------------------------------------------------|
| 查询股票基本面和链上数据                     | API 1（通过行情代码获取 `chainId` + `contractAddress`）→ API 5（动态数据） |
| 检查股票通证是否可交易                     | API 3（整体市场状态）→ API 4（单一资产状态及原因码）                  |
| 研究证券通证                           | API 1（查找通证）→ API 2（公司元数据 + 鉴证报告）                        |
| 获取 K-Line 图数据                        | API 1（查找通证）→ API 6（带时间间隔的 K-Line）                          |

## 应用场景

1. **列出支持的股票**：获取所有 Ondo 证券通证行情代码及链和合约信息
2. **公司研究**：获取公司元数据、CEO、行业、概念标签和鉴证报告
3. **市场状态检查**：判断 Ondo 市场是否开市、闭市或处于盘前/盘后时段
4. **公司行为检测**：检查特定资产是否因财报、分红、股票拆分、合并或维护而暂停或受限
5. **实时数据**：获取链上价格、持有人数量、流通供应量、美股市盈率、股息收益率、52周区间和订单限额
6. **技术分析**：获取带可配置时间间隔和时间范围的通证 K-Line（K线）数据

## 关键概念：通证 ≠ 股份

每个通证代表 `multiplier` 股份的底层股票，**并非正好 1 股**。大多数通证的多倍数接近 1.0（累积股息调整），但股票拆分通证可能是 5.0 或 10.0（例如：多倍数 = 10.0 表示 1 通证 = 10 股）。

```
referencePrice = tokenInfo.price ÷ sharesMultiplier
```

参见注释 §6 了解常见多倍数类别。

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

| 参数     | 类型    | 必填 | 描述                                                                                                                                                                  |
|-----------|---------|------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| type      | integer | 否   | 按平台筛选：`1` = Ondo Finance（目前唯一支持的证券通证提供商）。不填则返回所有平台。**使用 `type=1` 仅获取 Ondo 通证。** |

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

**响应字段**（`data` 中的每一项）:

| 字段           | 类型    | 描述                                                   |
|-----------------|---------|-------------------------------------------------------|
| chainId         | string  | 链 ID (`1` = Ethereum, `56` = BSC)                     |
| contractAddress | string  | 通证合约地址                                        |
| symbol          | string  | 通证符号（行情代码 + `on` 后缀，例如 `<TOKEN_SYMBOL_ON>`） |
| ticker          | string  | 底层美股行情代码                                    |
| type            | integer | 平台类型：`1` = Ondo                                     |
| multiplier      | string  | 股份多倍数（参见关键概念，注释 §6）                   |

---

## API 2：RWA Meta

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/meta/ai
```

**请求参数**:

| 参数         | 类型   | 必填 | 描述                                    |
|--------------|--------|------|-----------------------------------------|
| chainId      | string | 是   | 链 ID（例如：`56` 对应 BSC，`1` 对应 Ethereum） |
| contractAddress | string | 是   | 通证合约地址                         |

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
      "descriptionZh": "<公司描述>",
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
|---------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tokenId                   | string  | 通证唯一 ID                                                                                                                                                              |
| name                      | string  | 通证全名（例如 `<TOKEN_DISPLAY_NAME>`）                                                                                                                                |
| symbol                    | string  | 通证符号（例如 `<TOKEN_SYMBOL_ON>`）                                                                                                                                      |
| ticker                    | string  | 底层股票行情代码（例如 `<UNDERLYING_TICKER>`）                                                                                                                             |
| icon                      | string  | 图标图片**相对路径**。获取完整 URL 需添加前缀 `https://bin.bnbstatic.com`（例如 `https://bin.bnbstatic.com/images/web3-data/public/token/logos/<TOKEN_ID>.png`） |
| dailyAttestationReports   | string  | 每日鉴证报告**相对路径**。添加前缀 `https://bin.bnbstatic.com` 获取完整 URL                                                                                              |
| monthlyAttestationReports | string  | 每月鉴证报告**相对路径**。添加前缀 `https://bin.bnbstatic.com` 获取完整 URL                                                                                              |
| companyInfo               | object  | 公司详情（见下文）                                                                                                                                                      |
| decimals                  | integer | 通证小数位数（通常 `18`）                                                                                                                                              |

**公司信息字段**（`data.companyInfo`）:

| 字段         | 类型     | 描述                                                           |
|--------------|----------|-----------------------------------------------------------------|
| companyName   | string   | 英文公司名称                                                   |
| companyNameZh | string   | 中文公司名称                                                   |
| homepageUrl   | string   | 公司官网 URL                                                  |
| description   | string   | 公司描述（英文）                                               |
| descriptionZh | string   | 公司描述（中文）                                               |
| ceo           | string   | CEO 姓名                                                         |
| industry      | string   | 行业分类                                                       |
| industryKey   | string   | 行业 i18n 键                                                     |
| conceptsCn    | string[] | 概念/主题标签（中文）                                         |
| conceptsEn    | string[] | 概念/主题标签（英文）（例如 `Concept Tag A`, `Concept Tag B`） |

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

> **注意**：上述示例为 `openState=false`（市场闭市/暂停）状态，因此 `nextOpen` 早于 `nextClose`。

**响应字段**（`data`）:

| 字段         | 类型         | 描述                                                             |
|--------------|--------------|-----------------------------------------------------------------|
| openState     | boolean      | Ondo 市场当前是否开市交易                                       |
| reasonCode    | string\|null | 若市场非正常交易状态，则显示原因码（见下文原因码）                 |
| reasonMsg     | string\|null | 人类可读的原因信息                                               |
| nextOpen      | string       | 从当前状态看下一个市场开市时间（ISO 8601 UTC）                   |
| nextClose     | string       | 从当前状态看下一个市场闭市时间（ISO 8601 UTC）                  |
| nextOpenTime  | number       | 从当前状态看下一个开市时间（Unix 时间戳，毫秒）                 |
| nextCloseTime | number       | 从当前状态看下一个闭市时间（Unix 时间戳，毫秒）                 |

> **解读**：这些字段的状态相关。当 `openState=true` 时，`nextClose` 预期早于 `nextOpen`（市场闭市早于下一个开市）。当 `openState=false` 时，`nextOpen` 预期早于 `nextClose`（市场开市早于下一个闭市）。

---

## API 4：Asset Market Status

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/asset/market/status/ai
```

**请求参数**:

| 参数         | 类型   | 必填 | 描述            |
|--------------|--------|------|-----------------|
| chainId      | string | 是   | 链 ID           |
| contractAddress | string | 是   | 通证合约地址 |

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

**响应字段**（`data`）:

| 字段         | 类型         | 描述                                                                           |
|--------------|--------------|---------------------------------------------------------------------------------|
| openState     | boolean      | 该特定资产是否可交易                                                         |
| marketStatus  | string       | 当前时段：`premarket`、`regular`、`postmarket`、`overnight`、`closed`、`pause` |
| reasonCode    | string       | 状态原因码（见下文原因码）                                                   |
| reasonMsg     | string\|null | 人类可读的原因信息（暂停/受限时填充）                                         |
| nextOpenTime  | number       | 下一个开市时间（Unix 时间戳，毫秒）                                           |
| nextCloseTime | number       | 下一个闭市时间（Unix 时间戳，毫秒）                                            |

### 原因码

| reasonCode           | Description                                                                |
|----------------------|----------------------------------------------------------------------------|
| `TRADING`            | 正常交易                                                                 |
| `MARKET_CLOSED`      | 市场关闭（非交易时间）                                                     |
| `MARKET_PAUSED`      | 全市场交易暂停                                                           |
| `ASSET_PAUSED`       | 此特定资产暂停（见下文公告信息）                                             |
| `ASSET_LIMITED`      | 此特定资产有限制交易（见下文公告信息）                                         |
| `UNSUPPORTED`        | 资产不支持                                                               |
| `MARKET_MAINTENANCE` | 系统维护                                                                 |

### 公告信息（当 `ASSET_PAUSED` 或 `ASSET_LIMITED` 时）

当资产暂停或有限制时，`reasonMsg` 字段指示具体的公告信息：

| reasonCode      | reasonMsg          | Description                                                |
|-----------------|--------------------|------------------------------------------------------------|
| `ASSET_PAUSED`  | `cash_dividend`    | 现金股息分配                                                 |
| `ASSET_PAUSED`  | `stock_dividend`   | 股票股息分配                                                 |
| `ASSET_PAUSED`  | `stock_split`      | 股票拆分                                                     |
| `ASSET_PAUSED`  | `merger`           | 公司合并                                                     |
| `ASSET_PAUSED`  | `acquisition`      | 公司收购                                                     |
| `ASSET_PAUSED`  | `spinoff`          | 企业分拆                                                     |
| `ASSET_PAUSED`  | `maintenance`      | 资产级维护                                                   |
| `ASSET_PAUSED`  | `corporate action` | 其他公告信息                                                   |
| `ASSET_LIMITED` | `earnings`         | 盈利发布 — 交易受限但未完全暂停                             |

---

## API 5：RWA 动态 V2

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v2/public/wallet-direct/buw/wallet/market/token/rwa/dynamic/ai
```

**请求参数**：

| Parameter       | 类型   | 必填 | Description            |
|-----------------|--------|------|------------------------|
| chainId         | string | 是   | 链 ID                  |
| contractAddress | string | 是   | 代币合约地址           |

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
      "lastCashAmount": null
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

| Field      | 类型   | Description                                          |
|------------|--------|------------------------------------------------------|
| symbol     | string | 代币符号（例如 `<TOKEN_SYMBOL_ON>`）                  |
| ticker     | string | 标的股票代码（例如 `<UNDERLYING_TICKER>`）            |
| tokenInfo  | object | 链上代币数据                                          |
| stockInfo  | object | 美股基本面                                             |
| statusInfo | object | 市场/资产交易状态（与 API 4 相同结构）               |
| limitInfo  | object | 订单限制信息                                            |

**代币信息** (`data.tokenInfo`):

| Field             | 类型   | Description                                                                            |
|-------------------|--------|----------------------------------------------------------------------------------------|
| price             | string | 链上代币价格（美元） — 按代币计算，非按股计算（见上文关键概念）                         |
| priceChange24h    | string | 24小时价格变动（美元）                                                                 |
| priceChangePct24h | string | 24小时价格变动百分比                                                                   |
| totalHolders      | string | 链上持有人数量                                                                     |
| sharesMultiplier  | string | 与 API 1 中的 `multiplier` 相同（见上文关键概念，注释 §6）                             |
| volume24h         | string | ⚠️ **误导性**：这是美股交易量（美元），不是链上 DEX 交易量                             |
| marketCap         | string | 链上市值（美元）= `circulatingSupply × price`                                            |
| fdv               | string | 完全稀释估值（美元）                                                                 |
| circulatingSupply | string | 流通供应量（代币单位）                                                               |
| maxSupply         | string | 最大供应量（代币单位）                                                               |

**股票信息** (`data.stockInfo`):

| Field             | 类型         | Description                                                                      |
|-------------------|--------------|----------------------------------------------------------------------------------|
| price             | string\|null | 美股价格（美元）。交易时间外可能为 `null`                                        |
| priceHigh52w      | string       | 52周最高价格（美元）                                                             |
| priceLow52w       | string       | 52周最低价格（美元）                                                             |
| volume            | string       | ⚠️ 股票交易量以**股**计（非美元）。乘以 `price` 获取美元价值                      |
| averageVolume     | string       | 平均日交易量（股）                                                               |
| sharesOutstanding | string       | 总发行股数                                                                     |
| marketCap         | string       | 美股总市值（美元）                                                               |
| turnoverRate      | string       | 换手率（%）                                                                   |
| amplitude         | string\|null | 当日振幅（%）                                                                 |
| priceToEarnings   | string       | P/E比率（TTM）                                                                 |
| dividendYield     | string       | 股息收益率（TTM，百分比值：`0.27` 表示 0.27%）                                    |
| priceToBook       | string\|null | P/B比率                                                                          |
| lastCashAmount    | string\|null | 最近现金股息金额（美元）                                                         |

**状态信息** (`data.statusInfo`):

与 API 4 响应相同结构。参见 [资产市场状态](#api-4-asset-market-status) 获取字段详情和原因代码。

**限制信息** (`data.limitInfo`):

| Field                  | 类型   | Description                                    |
|------------------------|--------|------------------------------------------------|
| maxAttestationCount    | string | 订单最大认证数量                                |
| maxActiveNotionalValue | string | 订单最大名义价值（美元）                        |

---

## API 6：代币 K线

### 方法：GET

**URL**:
```
https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/kline/ai
```

**请求参数**：

| Parameter       | 类型    | 必填 | 默认 | Description                                             |
|-----------------|---------|------|------|---------------------------------------------------------|
| chainId         | string  | 是   | -    | 链 ID（例如 `56` 为 BSC，`1` 为以太坊）                |
| contractAddress | string  | 是   | -    | 代币合约地址                                             |
| interval        | string  | 是   | -    | K线间隔（见间隔参考）                                     |
| limit           | integer | 否   | 300  | 返回烛线数量（最大 300）                                 |
| startTime       | long    | 否   | -    | 开始时间戳（ms），基于烛线开盘时间                     |
| endTime         | long    | 否   | -    | 结束时间戳（ms），基于烛线开盘时间减 1ms                |

> **关于 `startTime` / `endTime` 的注释**：两者均参考烛线开盘时间。若省略，返回最新烛线。当两者都提供时，`endTime` 应为目标烛线开盘时间减 1ms。

**间隔参考**：

| Interval | Description |
|----------|-------------|
| 1m       | 1 分钟      |
| 5m       | 5 分钟      |
| 15m      | 15 分钟     |
| 1h       | 1 小时      |
| 4h       | 4 小时      |
| 12h      | 12 小时     |
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

**烛线数组格式**（`data.klineInfos[]` 中的每个元素）：

| Index | Field     | 类型   | Description                 |
|-------|-----------|--------|-----------------------------|
| 0     | openTime  | number | 烛线开盘时间戳（ms）        |
| 1     | open      | string | 开盘价格（美元）            |
| 2     | high      | string | 最高价格（美元）            |
| 3     | low       | string | 最低价格（美元）            |
| 4     | close     | string | 收盘价格（美元）            |
| 5     | -         | string | 保留字段                    |
| 6     | closeTime | number | 烛线收盘时间戳（ms）        |

**响应字段**：

| Field      | 类型    | Description                               |
|------------|---------|-------------------------------------------|
| klineInfos | array   | 烛线数组（见格式说明）                     |
| decimals   | integer | 价格小数位数提示                           |

---

## 用户代理请求头

包含以下字符串的 `User-Agent` 请求头：`binance-web3/1.1 (Skill)`

## 注释

1. **`volume24h` 在 tokenInfo 中具有误导性**：`tokenInfo.volume24h` 从 RWA 动态 API 返回的是 **美股每日交易量（美元）**，不是链上 DEX 交易量。实际链上买卖量，请使用 Binance 链上动态 API（`/market/token/dynamic/info`）并使用 `volume24hBuy` + `volume24hSell` 字段。

2. **`dividendYield` 是百分比值，不是原始小数**：值为 `0.27` 表示 0.27% 股息收益率。

3. **图标和报告URL是相对路径 — 需要添加域名使用**：API 返回 `icon`、`dailyAttestationReports` 和 `monthlyAttestationReports` 的相对路径（例如 `/images/web3-data/public/token/logos/...`）。要构造完整URL，请添加 `https://bin.bnbstatic.com`。示例：`/images/web3-data/public/token/logos/<TOKEN_ID>.png` → `https://bin.bnbstatic.com/images/web3-data/public/token/logos/<TOKEN_ID>.png`。

4. **无需API密钥**：所有端点都是公开API。无需认证。

5. **多链部署**：每个支持的股票可能部署在多个链上（例如以太坊和BSC）。`stockInfo` 和 `tokenInfo.price` 在各链中相同。`tokenInfo.totalHolders` 跨链聚合。`tokenInfo.circulatingSupply` 和 `tokenInfo.marketCap` 链特定。

6. **`multiplier` / `sharesMultiplier` — 对价格比较至关重要**：每个代币代表 `multiplier` 股的标的股票，不是精确1股。乘数从 1.0 开始，随着现金股息再投资（累积股息调整）随时间增加。某些代币也反映股票拆分（例如乘数 = 10.0 表示 1 代币 = 10 股）。

   **公式**:
   ```
   referencePrice = tokenInfo.price ÷ sharesMultiplier
   ```

   > `tokenInfo.price` 和 `stockInfo.price` 来自不同来源（链上预言机 vs 股票数据源）并具有不同更新频率，因此存在微小溢价/折价（通常在 ±0.1% 范围内）是正常的。

   **常见乘数类别**：

   | Multiplier         | Cause                                                   |
   |--------------------|---------------------------------------------------------|
   | Exactly 1.0        | 尚未支付股息，或新上市                                  |
   | Slightly above 1.0 | 累计现金股息再投资（随时间增长）                        |
   | 5.0, 10.0          | 反映在代币结构中的股票拆分                              |
