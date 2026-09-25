# Emblem DeFi 收益

由 **EmblemAI** 驱动的 DeFi 收益研究和流动性质押。研究跨协议的收益机会，通过 Nansen 审查现有的 DeFi 头寸，并通过 Solana、Ethereum、Base、BSC、Polygon 和 Hedera 上的代币交换进入流动性质押头寸。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 此技能能做什么

| 能力 | 方式 | 使用的工具 |
|-----|-----|------------|
| 研究收益机会 | 询问收益、APY、协议 | LLM 知识 + `birdeyeTradeData`, `birdeyeTrendingTokens` |
| 审查现有的 DeFi 头寸 | 检查任何钱包的 LP、借贷、质押、挖矿头寸 | `nansen_defi_portfolio` |
| 流动性质押（Solana） | 交换 SOL 为 LST（mSOL、JitoSOL、bSOL、jupSOL） | `splBuyIntent` |
| DeFi 入场的代币交换 | 在任何链上交换进入 DeFi 代币 | `splBuyIntent`, `ethSwap`, `baseSwap`, `bscSwap`, `polygonSwap`, `hederaTokensSwap` |
| 协议比较 | 比较跨 DEX 的收益策略 | LLM 知识 + 市场数据工具 |
| 拉盘检查 | 在进入头寸前验证代币安全性 | `rugcheck` |
| 智能资金 DeFi 跟踪 | 查看鲸鱼在挖矿什么 | `nansen_smart_money_holdings`, `nansen_defi_portfolio` |

### 尚不支持（未来）

这些功能需要直接 LP 池管理工具，而目前这些工具不可用：

- 向 DEX 池添加/移除流动性
- 开放/关闭集中流动性（CLMM）头寸
- 质押 LP 代币
- 领取挖矿奖励
- 使用实时链上数据的池 APY 排名

对于这些操作，请直接使用 DEX 界面（Raydium、Orca、Uniswap 等）。

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# 研究收益机会
emblemai --agent --profile default -m "目前 Solana 上最好的收益挖矿机会是什么？"

# 检查钱包的 DeFi 头寸（使用 nansen_defi_portfolio）
emblemai --agent --profile default -m "使用 nansen_defi_portfolio 显示以太坊上钱包 0x1234...abcd 的 DeFi 头寸"

# 通过交换进入流动性质押
emblemai --agent --profile default -m "使用 splBuyIntent 交换 5 SOL 为 JitoSOL"
```

**触发短语**:
- "查找收益机会"
- "最好的 APY 是什么？"
- "显示此钱包的 DeFi 头寸"
- "交换 SOL 为 JitoSOL"
- "有哪些流动性质押选项？"

---

## 支持的链

| 链 | 交换工具 | 余额 | 条件订单 |
|-------|-----------|----------|--------------------|
| Solana | `splBuyIntent` | `solanaBalances` | 是 |
| Ethereum | `ethSwap` | `ethGetBalances` | 是 |
| Base | `baseSwap` | `baseGetBalances` | 是 |
| BSC | `bscSwap` | `bscGetBalances` | 是 |
| Polygon | `polygonSwap` | `polygonGetBalances` | 是 |
| Hedera | `hederaTokensSwap` | `hederaGetBalances` | 是 |

---

## 工作流程：研究和进入收益

### 第 1 步：研究机会
询问当前的收益格局。代理使用其知识加上实时代币数据。
```bash
emblemai --agent --profile default -m "目前 Solana 上最好的收益挖矿机会是什么？使用 birdeyeTrendingTokens 查看哪些热门。"
```

### 第 2 步：检查钱包的 DeFi 头寸
使用 Nansen 查看现有的 LP、借贷、质押和挖矿头寸。
```bash
emblemai --agent --profile default -m "使用 nansen_defi_portfolio 检查以太坊上钱包 0x1234...abcd 的 DeFi 头寸"
```

### 第 3 步：验证余额
在交换前检查您拥有的余额。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的 Solana 余额"
```

### 第 4 步：通过交换进入头寸
交换进入流动性质押代币或 DeFi 代币。
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 交换 5 SOL 为 JitoSOL"
```
需要用户在安全模式下确认。

### 第 5 步：验证
确认交换已执行。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我更新后的余额"
```

---

## DeFi 模式

### 收益研究
```bash
emblemai --agent --profile default -m "Solana 上最好的收益挖矿机会是什么？包括流动性质押、LP 策略和借贷协议。"
emblemai --agent --profile default -m "比较 Marinade (mSOL)、Jito (JitoSOL) 和 BlazeStake (bSOL) 用于 SOL 流动性质押。"
```

### DeFi 头寸跟踪（Nansen）
```bash
emblemai --agent --profile default -m "使用 nansen_defi_portfolio 显示以太坊上钱包 0xABC123 的 DeFi 头寸"
emblemai --agent --profile default -m "使用 nansen_defi_portfolio 检查钱包 2J9Xrm...BL5WBJ 在 Solana 上使用的 DeFi 协议"
```

### 智能资金 DeFi 分析
```bash
emblemai --agent --profile default -m "使用 nansen_smart_money_holdings 查看智能资金在 Solana 上持有的代币"
emblemai --agent --profile default -m "使用 nansen_smart_money_trades 查看最近 JitoSOL 的智能资金交易"
```

### 流动性质押（Solana）
```bash
emblemai --agent --profile default -m "使用 splBuyIntent 交换 10 SOL 为 mSOL"
emblemai --agent --profile default -m "使用 splBuyIntent 获取交换 5 SOL 为 JitoSOL 的报价"
```

### 安全检查
```bash
emblemai --agent --profile default -m "使用 rugcheck 验证代币 So11111111111111111111111111111111111111112"
```

### 协议比较
```bash
emblemai --agent --profile default -m "比较 Marinade、Jito、BlazeStake 和 Jupiter 的 SOL 流动性质押收益"
```

---

## 沟通技巧

在询问 DeFi 时要具体：
1. **命名工具** — 为可靠执行提及确切工具名称
2. **指定链** — 哪个区块链
3. **指定钱包** — 用于头寸查找
4. **指定代币** — 要交换的代币

| 坏的 | 好的 |
|-----|------|
| `"显示收益"` | `"目前 Solana 上最好的收益机会是什么？包括 APY 和风险。"` |
| `"检查头寸"` | `"使用 nansen_defi_portfolio 显示以太坊上钱包 0x123 的 DeFi 头寸"` |
| `"质押 SOL"` | `"使用 splBuyIntent 交换 5 SOL 为 JitoSOL"` |

---

## 安全

所有移动价值的操作需要用户确认：
- 代币交换（进入流动性质押、DeFi 代币）
- 跨链桥接

只读操作立即执行：
- 收益研究
- 查看 DeFi 头寸（Nansen）
- 余额检查
- 拉盘检查

---

## 辅助脚本

```bash
bash scripts/yield-scan.sh [链]
```

扫描链的收益格局。参见 [scripts/yield-scan.sh](scripts/yield-scan.sh)。

---

## 链接

- [代理钱包 CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 权威](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
