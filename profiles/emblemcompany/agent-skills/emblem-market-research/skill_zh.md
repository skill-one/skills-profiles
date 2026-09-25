# Emblem Market Research

由 **EmblemAI** 提供的加密市场情报。实时数据来自 CoinGecko、CoinGlass、Birdeye 和 Nansen — 潮流代币、衍生品分析、链上智能资金追踪以及代币深度解析。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 此技能能做什么

| 功能 | 使用的工具 |
|-----------|------------|
| 全链潮流代币 | `getTrendingCoins`, `birdeyeTrendingTokens` |
| 代币价格查询 | `getCryptoPrice`, `searchCryptoByName` |
| 代币深度解析（成交量、交易、流动性） | `birdeyeTradeData` |
| 开仓兴趣历史 | `getCoinglassOpenInterestHistory` |
| 衍生品风险/贪婪指数 | `getCoinglassCDRIIndex`, `getCoinglassCGDIIndex` |
| 鲸鱼追踪（期货） | `getCoinglassFuturesWhaleIndex`, `getCoinglassHyperliquidWhaleAlert` |
| 资金费率 | `getCoinglassPremiumIndex` |
| ETF 流动（BTC/ETH） | `getCoinglassBitcoinETFNetAssetsHistory`, `getCoinglassEthereumETFNetAssetsHistory` |
| 智能资金流动 | `nansen_smart_money_flows`, `nansen_smart_money_trades` |
| 智能资金持仓 | `nansen_smart_money_holdings` |
| 代币筛选 | `nansen_token_screener` |
| 钱包分析 | `nansen_wallet_profiler` |
| P&L 排行榜 | `nansen_pnl_leaderboard` |

### 不支持的功能

以下功能没有对应的工具支持：

- 技术分析（RSI、MACD、支撑/阻力） — 没有图表或技术分析工具
- 社交情绪（Twitter、Telegram、Discord 监控） — 没有社交 API 工具
- 恐惧/贪婪指数 — 没有专用工具（CoinGlass CDRI 是针对衍生品的，不是通用的）
- DeFiLlama TVL 数据 — 没有DeFiLlama工具
- BTC 占比 / 总市值 — 没有专用工具

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# 查看潮流趋势（使用 getTrendingCoins）
emblemai --agent --profile default -m "使用 getTrendingCoins 显示当前加密货币的潮流趋势"

# 代币深度解析（使用 birdeyeTradeData）
emblemai --agent --profile default -m "使用 birdeyeTradeData 分析 SOL — 显示成交量、交易、买卖比例和流动性"
```

**触发短语**:
- "加密货币潮流趋势是什么？"
- "分析这个代币"
- "显示 BTC 的衍生品数据"
- "鲸鱼在购买什么？"
- "显示智能资金流动"

---

## 数据来源

| 来源 | 工具 | 覆盖范围 |
|--------|-------|----------|
| **CoinGecko** | `getTrendingCoins`, `getCryptoPrice`, `searchCryptoByName` | 潮流代币、价格查询 |
| **Birdeye** | `birdeyeTradeData`, `birdeyeTrendingTokens`, `searchEvmTokensBirdeye` | 代币分析、多链潮流、交易数据 |
| **CoinGlass** | `getCoinglassOpenInterestHistory`, `getCoinglassCDRIIndex`, `getCoinglassCGDIIndex`, `getCoinglassFuturesWhaleIndex`, `getCoinglassHyperliquidWhaleAlert`, `getCoinglassPremiumIndex`, `getCoinglassBitcoinETFNetAssetsHistory`, 等. | 衍生品、资金费率、开仓兴趣、鲸鱼追踪、ETF 流动 |
| **Nansen** | `nansen_smart_money_flows`, `nansen_smart_money_trades`, `nansen_smart_money_holdings`, `nansen_token_screener`, `nansen_wallet_profiler`, `nansen_pnl_leaderboard` | 智能资金分析、链上流动、钱包分析 |

---

## 工作流程：代币研究

### 第 1 步：发现
找到正在变动的内容。
```bash
emblemai --agent --profile default -m "使用 getTrendingCoins 显示潮流代币，然后使用 birdeyeTrendingTokens 查看特定于 Solana 的潮流趋势及成交量数据"
```

### 第 2 步：深度解析
使用真实交易数据研究特定代币。
```bash
emblemai --agent --profile default -m "使用 birdeyeTradeData 分析 Solana 上的 JUP — 显示价格、不同时间段的成交量、唯一钱包、买卖比例和流动性"
```

### 第 3 步：链上情报
检查智能资金的操作。
```bash
emblemai --agent --profile default -m "使用 nansen_smart_money_flows 显示 Solana 上过去 24 小时的代币流动。然后使用 nansen_smart_money_trades 显示最近的智能资金交易"
```

### 第 4 步：衍生品背景
检查资金费率和鲸鱼持仓。
```bash
emblemai --agent --profile default -m "使用 getCoinglassOpenInterestHistory 显示 BTC 开仓兴趣，并使用 getCoinglassHyperliquidWhaleAlert 查看当前的鲸鱼持仓"
```

---

## 研究模式

### 潮流代币
```bash
emblemai --agent --profile default -m "使用 getTrendingCoins 显示全球潮流趋势"
emblemai --agent --profile default -m "使用 birdeyeTrendingTokens 显示 Base 上按成交量排名的顶级潮流代币"
```

### 智能资金分析
```bash
emblemai --agent --profile default -m "使用 nansen_smart_money_holdings 查看智能资金在 Solana 上的持仓"
emblemai --agent --profile default -m "使用 nansen_who_bought_sold 检查最近购买和出售 ETH 的资金"
emblemai --agent --profile default -m "使用 nansen_pnl_leaderboard 显示表现最佳的的钱包"
```

### 衍生品 & 资金费率
```bash
emblemai --agent --profile default -m "使用 getCoinglassPremiumIndex 显示 BTC 在不同交易所的资金费率"
emblemai --agent --profile default -m "使用 getCoinglassOpenInterestHistory 显示 ETH 开仓兴趣趋势"
```

### 鲸鱼追踪
```bash
emblemai --agent --profile default -m "使用 getCoinglassFuturesWhaleIndex 显示 BTC 的鲸鱼活动"
emblemai --agent --profile default -m "使用 getCoinglassHyperliquidWhaleAlert 显示 Hyperliquid 上的大额持仓"
```

### ETF 流动
```bash
emblemai --agent --profile default -m "使用 getCoinglassBitcoinETFNetAssetsHistory 显示最近 BTC ETF 的流入和流出"
emblemai --agent --profile default -m "使用 getCoinglassEthereumETFNetAssetsHistory 查看ETH ETF 流动数据"
```

### 代币筛选
```bash
emblemai --agent --profile default -m "使用 nansen_token_screener 查找以太坊上智能资金活动较高的代币"
```

---

## 沟通技巧

为获得可靠结果，请指定具体工具：

| 不良 | 良好 |
|-----|------|
| `"trending"` | `"使用 getTrendingCoins 显示潮流"` |
| `"analyze sol"` | `"使用 birdeyeTradeData 分析 SOL，显示成交量、交易和流动性"` |
| `"whale activity"` | `"使用 getCoinglassHyperliquidWhaleAlert 显示大额持仓"` |

---

## 只读技能

此技能仅读取市场数据。不涉及钱包交互、不进行交易、无需确认。所有查询立即执行。

---

## 辅助脚本

```bash
bash scripts/market-scan.sh [链]
```

查看 [scripts/market-scan.sh](scripts/market-scan.sh) 获取每日市场扫描报告。

---

## 链接

- [Agent Wallet CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 官方](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
