# Emblem Memecoin Scout

由 **EmblemAI** 驱动的 Memecoin 发现和风险评估工具。实时新代币警报、热门 Memecoin、跑路检测、持币者分析，以及跨 Solana、Base 和 Hedera 的聪明资金追踪。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 本技能能做什么

| 功能 | 使用工具 | 链 |
|-----|---------|----|
| Pump.fun 新代币发行 | `getPumpFunTokens` | Solana |
| LaunchLab / Bonk.fun 新代币 | `discoverLaunchLabTokens` | Solana |
| 热门 Memecoin | `findSolanaGems`, `birdeyeTrendingTokens` | Solana, 多链 |
| Clanker 代币发现 | `baseFindClankerTokens` | Base |
| Hedera Memecoin 发现 | `hederaFindMemeCoins` | Hedera |
| 跑路检测 | `rugcheck` | Solana |
| 代币深度分析（交易量、交易） | `birdeyeTradeData` | 多链 |
| 聪明资金 Memecoin 追踪 | `nansen_smart_money_trades` | 多链 |
| CoinGecko 热门 | `getTrendingCoins` | 全链 |
| 代币搜索 | `searchCryptoByName`, `findSolanaSwapToken` | 全链 |

### 不支持的功能

以下功能没有对应的工具支持：

- 社交情绪（Twitter、Telegram、Discord 监控）—— 没有社交 API 工具
- 退出策略生成—— 仅 LLM 生成建议，非数据驱动
- 价格图表/技术水平—— 没有图表工具
- BSC/FourMeme 发现—— `bscfindMemeCoinsViaFourMeme` 返回 404（API 已损坏）

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# Pump.fun 上的热门代币（使用 getPumpFunTokens）
emblemai --agent --profile default -m "使用 getPumpFunTokens 显示 Pump.fun 即将毕业的代币及持币者数据"

# 风险检查代币（使用 rugcheck）
emblemai --agent --profile default -m "使用 rugcheck 分析 Solana 上的 [TOKEN_ADDRESS] 代币"
```

**触发短语**:
- "哪些 Memecoin 正在流行？"
- "在 Pump.fun 上查找新代币"
- "这个代币是跑路吗？"
- "在 Solana 上侦察 Memecoin"
- "今天有哪些新代币发行？"

---

## 支持的平台

| 平台 | 工具 | 链 | 数据 |
|------|------|----|------|
| **Pump.fun** | `getPumpFunTokens` | Solana | 新发行、毕业代币、持币者数据、开发者持币比例、狙击/捆绑检测 |
| **LaunchLab** | `discoverLaunchLabTokens` | Solana | 新代币发行及曲线数据 |
| **Clanker** | `baseFindClankerTokens` | Base | 新代币及市值、创作者信息 |
| **MemeJob** | `hederaFindMemeCoins` | Hedera | Memecoin 及市值、社交、DEX 链接 |
| **Birdeye** | `birdeyeTradeData`, `birdeyeTrendingTokens` | 多链 | 交易量、价格变动、交易数据 |
| **Rugcheck** | `rugcheck` | Solana | 风险评分、持币者集中度、内部网络、冻结/铸造权限 |

---

## 工作流程：侦察和评估

### 第 1 步：发现
找到正在获得关注的项目。
```bash
emblemai --agent --profile default -m "使用 findSolanaGems 并按 trending 排序，显示 Solana 热门代币及市值、交易量、持币者数量和自然评分"
```

### 第 2 步：风险检查
在建立任何头寸前进行评估。
```bash
emblemai --agent --profile default -m "使用 rugcheck 分析 [TOKEN_ADDRESS] — 显示风险评分、主要持币者、内部网络、冻结权限和 LP 状态"
```

### 第 3 步：交易量深度分析
检查代币的真实交易数据。
```bash
emblemai --agent --profile default -m "使用 birdeyeTradeData 显示 Solana 上的 [TOKEN_ADDRESS] — 各时间段的价格变化、唯一钱包、买入/卖出交易量"
```

### 第 4 步：聪明资金检查
查看是否有鲸鱼参与。
```bash
emblemai --agent --profile default -m "使用 nansen_smart_money_trades 检查最近 Solana 上是否有聪明资金交易 [TOKEN_NAME]"
```

---

## 侦察模式

### 新发行（Solana）
```bash
emblemai --agent --profile default -m "使用 getPumpFunTokens 并设置 type about_to_graduate，显示即将毕业的代币及交易量和持币者数据"
emblemai --agent --profile default -m "使用 discoverLaunchLabTokens 显示最新的 LaunchLab 代币发行"
```

### 新发行（Base）
```bash
emblemai --agent --profile default -m "使用 baseFindClankerTokens 显示 Base 上的新 Clanker 代币及市值和创作者信息"
```

### 新发行（Hedera）
```bash
emblemai --agent --profile default -m "使用 hederaFindMemeCoins 显示 Hedera 上的热门 Memecoin 及市值和社交信息"
```

### 热门宝石
```bash
emblemai --agent --profile default -m "使用 findSolanaGems 显示按自然评分排序的热门代币"
emblemai --agent --profile default -m "使用 birdeyeTrendingTokens 在 Solana 上显示按交易量排名的顶级代币"
```

### 鲸鱼观察
```bash
emblemai --agent --profile default -m "使用 nansen_smart_money_trades 显示 Solana 上聪明资金正在交易的项目"
emblemai --agent --profile default -m "使用 getCoinglassHyperliquidWhaleAlert 显示大型 Memecoin 头寸"
```

### 红旗检测
```bash
emblemai --agent --profile default -m "使用 rugcheck 分析 [TOKEN_ADDRESS] — 检查蜜罐指标、铸造权限、集中持币者和锁定 LP"
```

---

## 风险评估

`rugcheck` 工具返回 `score_normalised`（0-100）及详细风险数据：

| 评分 | 风险等级 | 含义 |
|------|---------|------|
| 80-100 | 低 | 持币者分散，无冻结/铸造权限，锁定 LP |
| 50-79 | 中 | 部分集中或未锁定 LP — 谨慎操作 |
| 20-49 | 高 | 重大红旗（集中持币者、活跃铸造权限） |
| 0-19 | 危急 | 检测到蜜罐/跑路指标 — 不要参与 |

额外 rugcheck 数据：主要持币者百分比、内部网络分析、创作者代币历史、LP 流动性深度、冻结权限状态。

---

## 沟通技巧

明确指定工具以获得可靠执行：

| 不良 | 良好 |
|------|------|
| `"memes"` | `"使用 findSolanaGems 并按 trending 排序显示 Solana Memecoin"` |
| `"safe?"` | `"使用 rugcheck 分析 Solana 上的 [TOKEN_ADDRESS]"` |
| `"new coins"` | `"使用 getPumpFunTokens 并设置 type about_to_graduate 显示最新发行"` |

---

## 安全提示

Memecoin 风险极高。本技能提供数据和分析以辅助决策——不保证安全性。始终：
- 不要投资超过你能承受损失的资金
- 独立验证合约地址
- 在行动前检查多个数据源
- 对任何头寸使用止损

---

## 辅助脚本

```bash
bash scripts/memecoin-scan.sh [chain]
```

查看 [scripts/memecoin-scan.sh](scripts/memecoin-scan.sh) 获取热门 Memecoin 扫描功能。

---

## 链接

- [Agent Wallet CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 官方](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
