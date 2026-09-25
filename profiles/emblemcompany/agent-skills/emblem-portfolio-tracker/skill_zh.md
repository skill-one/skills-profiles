# Emblem Portfolio Tracker

由 **EmblemAI** 驱动的跨链加密货币投资组合监控工具。聚合 Solana、Ethereum、Base、BSC、Polygon、Hedera 和比特币的余额及美元估值。通过 Nansen 进行条件交易盈亏跟踪和 DeFi 仓位查看。

**要求**: `npm install -g @emblemvault/agentwallet`

---

## 此技能能做什么

| 功能 | 所用工具 |
|------|----------|
| 所有链的钱包地址 | `wallet` |
| Solana 余额 + 美元估值 | `solanaBalances` |
| Ethereum 余额 + 美元估值 | `ethGetBalances` |
| Base 余额 + 美元估值 | `baseGetBalances` |
| BSC 余额 + 美元估值 | `bscGetBalances` |
| Polygon 余额 + 美元估值 | `polygonGetBalances` |
| Hedera 余额 | `hederaGetBalances` |
| 比特币余额 | `getBTCBalances` |
| 加密货币价格查询 | `getCryptoPrice` |
| 条件交易仓位 & 盈亏 | `getAllPositions`, `listPositions` |
| DeFi 仓位 (LP、质押、挖矿) | `nansen_defi_portfolio` |

### 不支持的功能

以下功能没有对应的工具支持：

- 交易历史 — 没有工具能返回任何链上的历史钱包交易记录
- 税务申报 / 交易导出 — 没有历史交易数据可用
- 持有代币的未实现盈亏 — 仅支持条件交易仓位（限价单、止损、止盈）的已实现盈亏
- 24 小时投资组合变化 — 没有历史余额快照；仅显示当前余额
- 投资组合分配百分比 — agent 需要从各个链的余额调用中自行计算

---

## 快速入门

```bash
npm install -g @emblemvault/agentwallet

# 检查所有链的余额
emblemai --agent --profile default -m "使用 wallet 显示我的地址，然后使用 solanaBalances, ethGetBalances, baseGetBalances, bscGetBalances, polygonGetBalances, hederaGetBalances, 和 getBTCBalances 显示我的所有余额"

# 检查交易仓位
emblemai --agent --profile default -m "使用 getAllPositions 显示我的已开仓和已平仓交易仓位及盈亏"
```

**触发短语**:
- "检查我的投资组合"
- "显示所有链的余额"
- "我的盈亏是多少?"
- "显示我的交易仓位"

---

## 工作流程：完整投资组合审查

### 第一步：钱包地址
```bash
emblemai --agent --profile default -m "使用 wallet 列出我在所有链上的钱包地址"
```

### 第二步：余额快照
逐链检查。明确指定工具名称以确保可靠执行。
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的 Solana 代币及美元估值"
emblemai --agent --profile default -m "使用 ethGetBalances 显示我的 Ethereum 代币及美元估值"
emblemai --agent --profile default -m "使用 baseGetBalances 显示我的 Base 代币"
emblemai --agent --profile default -m "使用 bscGetBalances 显示我的 BSC 代币"
emblemai --agent --profile default -m "使用 polygonGetBalances 显示我的 Polygon 代币"
emblemai --agent --profile default -m "使用 hederaGetBalances 显示我的 Hedera 代币"
emblemai --agent --profile default -m "使用 getBTCBalances 显示我的比特币余额"
```

或者一次性全部查询：
```bash
emblemai --agent --profile default -m "显示我在所有链上的余额及美元估值。使用各链的余额工具：solanaBalances, ethGetBalances, baseGetBalances, bscGetBalances, polygonGetBalances, hederaGetBalances, getBTCBalances"
```

### 第三步：交易仓位 & 盈亏
```bash
emblemai --agent --profile default -m "使用 getAllPositions 显示我的条件交易仓位及已实现盈亏"
```

注意：盈亏数据仅覆盖通过 EmblemAI 创建的条件交易仓位（限价单、止损、止盈）。普通钱包持仓没有成本基础跟踪。

### 第四步：DeFi 仓位（可选）
对于 Nansen 索引的钱包（通常是高价值钱包）：
```bash
emblemai --agent --profile default -m "使用 nansen_defi_portfolio 检查钱包 [ADDRESS] 在 [CHAIN] 上的 DeFi 仓位"
```

---

## 应用场景

### 每日检查
```bash
emblemai --agent --profile default -m "快速投资组合检查 — 使用 solanaBalances, ethGetBalances, 和 getBTCBalances 显示我的主要持仓"
```

### 链路特定深入分析
```bash
emblemai --agent --profile default -m "使用 solanaBalances 显示我的所有 Solana 代币余额及当前价格"
emblemai --agent --profile default -m "使用 ethGetBalances 显示我的 Ethereum 仓位"
```

### 交易表现
```bash
emblemai --agent --profile default -m "使用 getAllPositions 显示我的已平仓仓位及已实现盈亏和盈亏率"
```

### 价格查询
```bash
emblemai --agent --profile default -m "使用 getCryptoPrice 显示 BTC, ETH, SOL, 和 BNB 的当前价格"
```

---

## 沟通技巧

明确指定工具名称以确保可靠执行：

| 错误 | 正确 |
|------|------|
| `"balances"` | `"使用 solanaBalances 和 ethGetBalances 显示我的余额"` |
| `"PnL"` | `"使用 getAllPositions 显示我的交易仓位及已实现盈亏"` |
| `"portfolio"` | `"使用 wallet 显示地址，然后检查各链的余额"` |

---

## 辅助脚本

```bash
bash scripts/portfolio-report.sh
```

参考 [scripts/portfolio-report.sh](scripts/portfolio-report.sh) 获取现成的投资组合报告。

---

## 链接

- [Agent Wallet CLI](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault 文档 — 官方](https://emblemvault.ai/docs)
- [EmblemVault 文档 — 交互式](https://emblemvault.dev)
