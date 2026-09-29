---
name: query-address-info
description: '特定链上单个钱包的代币持有情况快照——列出当前持有的所有代币，包括名称、符号、当前价格、24小时价格变动和持有数量。

  当用户提供明确的钱包地址（或说“我的钱包”）并希望查看当前投资组合时使用：

  “0x... 持有什么代币”，“钱包余额明细”，“列出此地址的持仓”，“这个钱包里有哪些代币”，“显示 <地址> 的持有情况”。'
---

# 查询地址信息技能

## 概述

该技能可查询任何链上钱包地址的代币持有情况，支持：

- 列出钱包地址持有的所有代币
- 每个代币的当前价格
- 24小时价格变动百分比
- 持有数量

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 列出钱包的代币持有情况（含价格和24小时变动） | `positions` |

## 支持的链

| 链 | chainId |
|-------|---------|
| BSC | `56` |
| Solana | `CT_501` |
| Base | `8453` |
| Ethereum | `1` |

## 如何调用API

```bash
node <skill-dir>/scripts/cli.mjs positions '{"address":"0x...","chainId":"56","offset":0}'
```

## 命令

| 命令 | 目的 | 必填参数 | 示例 |
|---------|---------|---------------|---------|
| `positions` | 列出钱包代币持有情况（价格 + 24小时变动 + 数量） | `address`, `chainId`, `offset` | `node <skill-dir>/scripts/cli.mjs positions '{"address":"0x...","chainId":"56","offset":0}'` |

## 规则

- **`offset` 每次调用都必须提供——包括第一页。** 传入 `0` 获取第一页；递增用于后续页面。省略会导致上游校验错误。
- **分页**：重复使用递增的 `offset`，直到 `data.list` 为空或小于页面大小。
- **图标URL前缀**：`icon` 是相对路径（例如，`/images/web3-data/public/token/logos/xxxx.png`）。需在前面添加 `https://bin.bnbstatic.com` 才能渲染。
- **数字作为字符串**：`price`, `percentChange24h`, `remainQty` 是字符串——进行算术运算前需转换为数字。

## 完整CLI参考

请参阅 [`references/cli.md`](references/cli.md) 了解每个子命令的调用方式、参数表、返回字段表和真实响应示例。
