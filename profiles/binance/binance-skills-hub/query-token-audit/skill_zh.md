# 查询代币审计技能

## 概述

| API          | 功能            | 应用场景          |
|--------------|-----------------|-------------------|
| 代币安全审计 | 代币安全扫描    | 检测蜜罐、拉高抛低、诈骗、恶意功能 |

## 应用场景

1. **交易前安全检查**：在购买或交换前验证代币安全
2. **诈骗检测**：识别蜜罐、假代币和恶意合约
3. **合约分析**：检查危险的所有权功能和隐藏风险
4. **税收验证**：在交易前检测异常的买入/卖出税

## 支持的链

| 链名称   | chainId |
|----------|---------|
| BSC      | 56      |
| Base     | 8453    |
| Solana   | CT_501  |
| Ethereum | 1       |

---

## API：代币安全审计

### 方法：POST

**URL**: 
```
https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit
```

**请求参数**：

| 参数         | 类型   | 必填 | 描述             |
|--------------|--------|------|------------------|
| binanceChainId | 字符串 | 是   | 链 ID：`CT_501` (Solana), `56` (BSC), `8453` (Base), `1` (Ethereum) |
| contractAddress | 字符串 | 是   | 代币合约地址     |
| requestId    | 字符串 | 是   | 唯一请求 ID (UUID v4 格式) |

**请求头**：
```
Content-Type: application/json
Accept-Encoding: identity
User-Agent: binance-web3/1.4 (Skill)
```

**示例请求**：
```bash
curl --location 'https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit' \
--header 'Content-Type: application/json' \
--header 'source: agent' \
--header 'Accept-Encoding: identity' \
--header 'User-Agent: binance-web3/1.4 (Skill)' \
--data '{
    "binanceChainId": "56",
    "contractAddress": "0x55d398326f99059ff775485246999027b3197955",
    "requestId": "'$(uuidgen)'"
}'
```

**响应示例**：
```json
{
    "code": "000000",
    "data": {
        "requestId": "d6727c70-de6c-4fad-b1d7-c05422d5f26b",
        "hasResult": true,
        "isSupported": true,
        "riskLevelEnum": "LOW",
        "riskLevel": 1,
        "extraInfo": {
            "buyTax": "0",
            "sellTax": "0",
            "isVerified": true
        },
        "riskItems": [
            {
                "id": "CONTRACT_RISK",
                "name": "Contract Risk",
                "details": [
                    {
                        "title": "Honeypot Risk Not Found",
                        "description": "A honeypot is a token that can be bought but not sold",
                        "isHit": false,
                        "riskType": "RISK"
                    }
                ]
            }
        ]
    },
    "success": true
}
```

**响应字段**：

| 字段                             | 类型   | 描述                                               |
|----------------------------------|--------|---------------------------------------------------|
| hasResult                        | 布尔值 | 是否有审计数据可用                                 |
| isSupported                      | 布尔值 | 代币是否支持审计                                   |
| riskLevelEnum                    | 字符串 | 风险等级：`LOW`, `MEDIUM`, `HIGH`                  |
| riskLevel                        | 数字   | 风险等级数字 (1-5)                                |
| extraInfo.buyTax                 | 字符串 | 买入税百分比 (未知时为 null)                       |
| extraInfo.sellTax                | 字符串 | 卖出税百分比 (未知时为 null)                       |
| extraInfo.isVerified             | 布尔值 | 合约代码是否已验证                                 |
| riskItems[].id                   | 字符串 | 风险类别：`CONTRACT_RISK`, `TRADE_RISK`, `SCAM_RISK` |
| riskItems[].details[].title      | 字符串 | 风险检查标题                                       |
| riskItems[].details[].description | 字符串 | 风险检查描述                                       |
| riskItems[].details[].isHit      | 布尔值 | true = 检测到风险                                   |
| riskItems[].details[].riskType   | 字符串 | `RISK` (严重) 或 `CAUTION` (警告)                  |

**风险等级参考**：

| riskLevel | riskLevelEnum | 行动建议 | 描述             |
|-----------|---------------|----------|------------------|
| 0-1       | LOW           | 小心操作 | 检测到低风险，但**不保证安全**。DYOR。 |
| 2-3       | MEDIUM        | 仔细审查 | 检测到中等风险，仔细查看风险项 |
| 4         | HIGH          | 避免交易 | 检测到严重风险，高概率亏损 |
| 5         | HIGH          | 拒绝交易 | 确认严重风险，**不要进行** |

**重要提示**：低风险**不代表安全**。审计结果仅是**即时快照**。项目团队可能在购买后修改合约或限制流动性。这些风险无法提前预测。

**响应处理**：

- 如果 `hasResult=false` OR `isSupported=false`:
  → 回复："该链上此代币暂无安全审计数据。"
  → **不显示** `riskLevel`, `riskLevelEnum`, 或 `riskItems` (任一字段为 false 时数据不可靠)
  → 建议用户验证合约地址和链，或稍后再试
- 如果 `hasResult=true` AND `isSupported=true`:
  → 显示完整审计结果，包括风险等级、税收信息和所有风险项
  → 参照上表风险等级参考表提供行动建议

---

## User Agent 头部

包含以下字符串的 `User-Agent` 头部：`binance-web3/1.4 (Skill)`

## 注意事项

1. 所有数字字段均为字符串格式，使用时需转换
2. 审计结果仅当 `hasResult: true` AND `isSupported: true` 时有效
3. `riskLevel: 5` 表示应拒绝交易；`riskLevel: 4` 为高风险
4. 税收阈值：>10% 为严重，5-10% 为警告，<5% 为可接受
5. 每次审计请求生成唯一的 UUID v4
6. 仅输出安全检查风险标志，**不提供任何投资建议**
7. 始终以免责声明结尾：`⚠️ 此审计结果仅供参考，不构成投资建议。请自行研究。`
