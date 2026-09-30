---
name: emblem-token-swap
description: 通过EmblemAI在6条区块链上执行代币交换。通过ChangeNow进行自动路由优化和跨链桥接。当用户想要交换代币、兑换加密货币、转换货币或进行跨链资产桥接时使用。
---

# Emblem Token 交换

由 **EmblemAI** 驱动的引导式 token 交换。在 Solana、Ethereum、Base、BSC、Polygon 和 Hedera 上进行 token 交换，并自动路由。通过 ChangeNow 进行跨链桥接。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 此功能可以实现什么

| 链 | 引号工具 | 交换工具 | 余额工具 | Token 搜索 |
|-------|-----------|-----------|-------------|--------------|
| Solana | `splBuyIntent` (引号模式) | `splBuyIntent` (交换模式) | `solanaBalances` | `findSolanaSwapToken` |
| Ethereum | `ethSwapQuote` | `ethSwap` | `ethGetBalances` | `searchCryptoByName` |
| Base | `baseSwapQuote` | `baseSwap` | `baseGetBalances` | `searchEvmTokensBirdeye` |
| BSC | `bscSwapQuote` | `bscSwap` | `bscGetBalances` | `searchEvmTokensBirdeye` |
| Polygon | `polygonSwapQuote` | `polygonSwap` | `polygonGetBalances` | `searchEvmTokensBirdeye` |
| Hedera | `hederaTokensSwapQuote` | `hederaTokensSwap` | `hederaGetBalances` | `hederaFindTokens` |
| 跨链 | `getChangeNowSwapQuote` | `swapUsingChangeNow` | — | `getChangeNowSupportedCurrencies` |

### 注意事项

- **Solana** 使用 `splBuyIntent` 进行引号和执行 — 它通过名称/符号/CA 查找 token，并支持灵活的金额 ($USD, SOL 或 token 数量)
- **EVM 链** (Ethereum, Base, BSC, Polygon) 通过自动 DEX 聚合进行路由
- **跨链** 桥接通过 ChangeNow 支持 500+ 种货币
- 比特币支持余额 (`getBTCBalances`) 但没有链上交换工具 — 使用 ChangeNow 进行 BTC 桥接

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# Solana 交换 (使用 splBuyIntent)
emblemai --agent --profile default -m "使用 splBuyIntent 在 Solana 上交换 5 SOL 为 USDC"

# 跨链桥接 (使用 ChangeNow)
emblemai --agent --profile default -m "使用 getChangeNowSwapQuote 获取从 Ethereum 桥接 0.05 ETH 到 Solana 的报价"
```

**触发短语:**
- "交换 SOL 为 USDC"
- "用 ETH 兑换 USDT"
- "转换我的 token"
- "将 token 桥接到 Base"

---

## 工作流程：安全 Token 交换

### 第 1 步：检查余额
确认你有足够的源 token。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的 Solana token 余额"
```

### 第 2 步：获取报价
执行交换前预览。
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 获取交换 5 SOL 为 USDC 的报价"
```

### 第 3 步：执行交换
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 在 Solana 上交换 5 SOL 为 USDC"
```
安全模式需要在执行前获得你的确认。

### 第 4 步：验证
确认新的余额。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的更新余额"
```

---

## 交换模式

### Solana 交换
```bash
# 通过 token 金额
emblemai --agent --profile default -m "使用 splBuyIntent 交换 0.5 SOL 为 USDC"

# 通过美元金额
emblemai --agent --profile default -m "使用 splBuyIntent 交换 $20 的 SOL 为 JUP"

# 通过 token 名称
emblemai --agent --profile default -m "使用 splBuyIntent 交换 100 USDC 为 BONK"
```

### EVM 交换
```bash
# Ethereum
emblemai --agent --profile default -m "使用 ethSwapQuote 获取交换 0.01 ETH 为 USDC 的报价，然后使用 ethSwap 执行"

# Base
emblemai --agent --profile default -m "使用 baseSwapQuote 在 Base 上报价 0.005 ETH 为 USDC"

# BSC
emblemai --agent --profile default -m "使用 bscSwapQuote 在 BSC 上报价 0.1 BNB 为 USDT"

# Polygon
emblemai --agent --profile default -m "使用 polygonSwapQuote 在 Polygon 上报价 10 POL 为 USDC"
```

### Hedera 交换
```bash
emblemai --agent --profile default -m "使用 hederaTokensSwapQuote 获取 100 HBAR 为 USDC 的报价，然后使用 hederaTokensSwap 执行"
```

### 跨链桥接
```bash
emblemai --agent --profile default -m "使用 getChangeNowSwapQuote 报价桥接 0.1 ETH 到 SOL"
emblemai --agent --profile default -m "使用 getChangeNowSupportedCurrencies 显示可用的桥接货币"
```

---

## 沟通规则

**交换请求中必须包含以下内容:**
1. **工具名称** — 指定精确的工具以实现可靠的路由
2. **金额** — 美元价值或 token 数量
3. **源 token** — 你要交换的是什么
4. **目标 token** — 你要交换成什么

| 坏的 | 好的 |
|-----|------|
| `"swap sol usdc"` | `"使用 splBuyIntent 交换 5 SOL 为 USDC"` |
| `"buy eth"` | `"使用 ethSwap 交换 100 USDC 为 ETH 在 Ethereum"` |
| `"bridge"` | `"使用 getChangeNowSwapQuote 桥接 0.05 ETH 到 SOL"` |

---

## 安全性

所有交换都需要明确用户确认（安全模式）。代理将：
1. 向你展示交换详情（金额、路由、预计输出）
2. 等待你的批准后再执行
3. 报告交易结果

不会绕过任何值移动操作的确认。

---

## 辅助脚本

```bash
bash scripts/swap-helper.sh
```

有关交互式交换演示，请参阅 [scripts/swap-helper.sh](scripts/swap-helper.sh)。

---

## 链接

- [Agent Wallet CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 官方](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
