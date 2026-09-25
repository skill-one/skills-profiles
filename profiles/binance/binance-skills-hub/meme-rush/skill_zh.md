# Meme Rush 技能

## 概述

两个排名源由一个 CLI 前端：`meme-rush`（启动板生命周期跟踪）和 `topic-rush`（AI 热点话题发现及其相关代币）。CLI 拥有 URL、方法、JSON 编码、超时和上游错误映射——代理仅选择子命令并填充过滤 JSON。

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 启动板上的新/最终化/迁移的 Meme 代币 | `meme-rush` |
| AI 生成的市场热点话题及其相关代币 | `topic-rush` |

## 支持的链

| 链 | chainId | 支持 |
|-------|---------|--------------|
| BSC | `56` | `meme-rush`, `topic-rush` |
| Solana | `CT_501` | `meme-rush`, `topic-rush` |
| Base | `8453` | `meme-rush` |

## 如何调用 API

```bash
node <skill-dir>/scripts/cli.mjs meme-rush '{"chainId":"CT_501","rankType":10,"limit":20}'
node <skill-dir>/scripts/cli.mjs topic-rush '{"chainId":"CT_501","rankType":10,"sort":10,"asc":false}'
```

## 命令

| 命令 | 目的 | 必填参数 | 示例 |
|---------|---------|---------------|---------|
| `meme-rush` | 启动板代币生命周期排名（新/最终化/迁移） | `chainId`, `rankType` | `node <skill-dir>/scripts/cli.mjs meme-rush '{"chainId":"CT_501","rankType":10,"limit":20}'` |
| `topic-rush` | AI 生成的热点话题及其相关代币 | `chainId`, `rankType`, `sort` | `node <skill-dir>/scripts/cli.mjs topic-rush '{"chainId":"CT_501","rankType":10,"sort":10}'` |

`meme-rush` 的可选过滤器（所有最小/最大对）：`progress`, `tokenAge`, `holders`, `liquidity`, `volume`, `marketCap`, `count{,Buy,Sell}`, `holders{Top10,Dev,Sniper,Insider}Percent`, `bundlerHoldingPercent`, `newWalletHoldingPercent`, `bnHoldingPercent`, `{bn,kol,pro}Holders`, `devMigrateCount`, `globalFee`; 以及 `keywords`, `excludes`, `limit`（最大 200），`protocol[]`, `devPosition`, `devBurnedToken`, `excludeDevWashTrading`, `excludeInsiderWashTrading`, `exclusive`, `paidOnDexScreener`, `pumpfunLiving`, `cmcBoost`, `pairAnchorAddress[]`, `tokenSocials.atLeastOne`, `tokenSocials.socials[]`。请参阅 `references/cli.md` 了解每个字段的类型和语义。

`topic-rush` 的可选过滤器：`asc`（布尔值），`keywords`, `topicType`, `tokenSizeMin/Max`, `netInflowMin/Max`。

## 规则

- **`meme-rush` `rankType`** 枚举——代币的启动板生命周期阶段：
  - `10` = **新**（新创建，仍在锁仓曲线上）
  - `20` = **最终化**（锁仓曲线几乎完成，即将迁移）
  - `30` = **迁移**（刚迁移到 DEX）
- **`topic-rush` `rankType`** 枚举——话题新鲜度：
  - `10` = **最新**（最新的热点话题）
  - `20` = **上升**（上升的话题，全天净流入在 $1k–$20k 之间）
- **`topic-rush` `sort`** 枚举：`10` = 创建时间，`20` = 净流入。**默认为 `sort=10`**，当用户未指定排序偏好时。
- **仅 `chainId` 和 `rankType` 是 `meme-rush` 所需**；所有其他参数是可选过滤器。`topic-rush` 额外需要 `sort`。
- **百分比字段已预格式化**——`progress`, 持有者 %, `devSellPercent`, `taxRate`, `priceChange`, `priceChange24h` 已经是像 `"42.5"` 这样的字符串，因此**直接追加 `%`** 进行显示；**不要乘以 100**。
- **图标 URL 前缀**：`icon` 是上游返回的相对路径；渲染前需在前面添加 `https://bin.bnbstatic.com`。`topic-rush` 响应中的 `tokenList[].icon` 遵循相同规则。
- **`taxRate` 可见性**：对于 `protocol=2001`（Four.meme）`taxRate` 仅在 **迁移** 列表中显示；对于 `protocol=2002`（Flap）则在所有列表中显示。
- **协议代码**（`1001`–`2002`）映射到特定的启动板（Pump.fun, Moonit, Pump AMM, Raydium V4/CPMM/CLMM, BONK, Dynamic BC, Moonshot, Jup Studio, Bags, Believer, Meteora DAMM V2 / Pools, Orca, Four.meme, Flap）。请参阅 `references/cli.md` 了解完整表格。

## 完整 CLI 参考

请参阅 [`references/cli.md`](references/cli.md) 了解每个子命令的调用方式、完整参数表（所有过滤器字段、持有者分布过滤器、开发者和启动过滤器）、返回字段表（核心、交易计数、持有者分布、开发者和迁移、标签和标志、社交链接、AI 叙述、话题 + tokenList），以及真实响应示例。
