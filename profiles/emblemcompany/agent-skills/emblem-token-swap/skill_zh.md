# Emblem Token Swap

由 **EmblemAI** 驱动的引导式代币兑换。在 Solana、Ethereum、Base、BSC、Polygon 和 Hedera 上进行代币兑换，并自动路由。通过 ChangeNow 进行跨链桥接。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 此功能可以实现什么

| 链 | 引用工具 | 兑换工具 | 余额工具 | 代币搜索 |
|-------|-----------|-----------|-------------|--------------|
| Solana | `splBuyIntent` (引用模式) | `splBuyIntent` (兑换模式) | `solanaBalances` | `findSolanaSwapToken` |
| Ethereum | `ethSwapQuote` | `ethSwap` | `ethGetBalances` | `searchCryptoByName` |
| Base | `baseSwapQuote` | `baseSwap` | `baseGetBalances` | `searchEvmTokensBirdeye` |
| BSC | `bscSwapQuote` | `bscSwap` | `bscGetBalances` | `searchEvmTokensBirdeye` |
| Polygon | `polygonSwapQuote` | `polygonSwap` | `polygonGetBalances` | `searchEvmTokensBirdeye` |
| Hedera | `hederaTokensSwapQuote` | `hederaTokensSwap` | `hederaGetBalances` | `hederaFindTokens` |
| 跨链 | `getChangeNowSwapQuote` | `swapUsingChangeNow` | — | `getChangeNowSupportedCurrencies` |

### 注意事项

- **Solana** 使用 `splBuyIntent` 进行引用和执行 — 它通过名称/符号/CA 查找代币，并支持灵活的金额 ($USD, SOL 或代币数量)
- **EVM 链** (Ethereum, Base, BSC, Polygon) 通过自动 DEX 聚合进行路由
- **跨链** 桥接通过 ChangeNow 支持 500+ 种货币
- 比特币支持余额查询 (`getBTCBalances`) 但没有链上兑换工具 — 使用 ChangeNow 进行 BTC 桥接

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# Solana 兑换 (使用 splBuyIntent)
emblemai --agent --profile default -m "使用 splBuyIntent 在 Solana 上兑换 5 SOL 为 USDC"

# 跨链桥接 (使用 ChangeNow)
emblemai --agent --profile default -m "使用 getChangeNowSwapQuote 获取从 Ethereum 桥接 0.05 ETH 到 Solana 的报价"
```

**触发短语:**
- "Swap SOL to USDC"
- "Exchange ETH for USDT"
- "Convert my tokens"
- "Bridge tokens to Base"

---

## 工作流程：安全代币兑换

### 第 1 步：检查余额
确认你有足够的源代币。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的 Solana 代币余额"
```

### 第 2 步：获取报价
在执行前预览兑换。
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 获取兑换 5 SOL 为 USDC 的报价"
```

### 第 3 步：执行兑换
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 在 Solana 上兑换 5 SOL 为 USDC"
```
安全模式需要在执行前获得你的确认。

### 第 4 步：验证
确认新的余额。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的更新后的余额"
```

---

## 兑换模式

### Solana 兑换
```bash
# 通过代币数量
emblemai --agent --profile default -m "使用 splBuyIntent 兑换 0.5 SOL 为 USDC"

# 通过美元金额
emblemai --agent --profile default -m "使用 splBuyIntent 兑换 $20 的 SOL 为 JUP"

# 通过代币名称
emblemai --agent --profile default -m "使用 splBuyIntent 兑换 100 USDC 为 BONK"
```

### EVM 兑换
```bash
# Ethereum
emblemai --agent --profile default -m "使用 ethSwapQuote 获取兑换 0.01 ETH 为 USDC 的报价，然后使用 ethSwap 执行"

# Base
emblemai --agent --profile default -m "使用 baseSwapQuote 在 Base 上报价 0.005 ETH 为 USDC"

# BSC
emblemai --agent --profile default -m "使用 bscSwapQuote 在 BSC 上报价 0.1 BNB 为 USDT"

# Polygon
emblemai --agent --profile default -m "使用 polygonSwapQuote 在 Polygon 上报价 10 POL 为 USDC"
```

### Hedera 兑换
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

**在兑换请求中始终包含以下内容:**
1. **工具名称** — 指定精确的工具以实现可靠的路由
2. **金额** — 美元价值或代币数量
3. **源代币** — 你要兑换的是什么
4. **目标代币** — 你要兑换成什么

| 坏的 | 好的 |
|-----|------|
| `"swap sol usdc"` | `"Use splBuyIntent to swap 5 SOL for USDC"` |
| `"buy eth"` | `"Use ethSwap to swap 100 USDC to ETH on Ethereum"` |
| `"bridge"` | `"Use getChangeNowSwapQuote to bridge 0.05 ETH to SOL"` |

---

## 安全性

所有兑换都需要明确用户确认（安全模式）。代理将：
1. 向你展示兑换详情（金额、路由、预计输出）
2. 在执行前等待你的批准
3. 报告交易结果

不会绕过任何值移动作确认。

---

## 辅助脚本

```bash
bash scripts/swap-helper.sh
```

有关交互式兑换演示，请参阅 [scripts/swap-helper.sh](scripts/swap-helper.sh)。

---

## 链接

- [Agent Wallet CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 官方](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
