# 查询代币信息技能

## 概述

四个只读的代币端点由一个 CLI 统一管理。代理选择一个子命令并传递 JSON 数据；通过这个技能用户可以：

搜索代币：跨链通过名称、符号或合约地址查找代币。
代币研究：获取代币元数据、社交链接和创作者信息。
市场分析：实时价格、交易量、持有人分布和流动性数据。
图表分析：K线蜡烛图数据用于技术分析。

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 通过关键词、符号或合约地址搜索代币 | `search` |
| 获取静态元数据（名称、符号、标志、社交链接、创作者） | `meta` |
| 获取实时市场数据（价格、交易量、持有人、流动性） | `dynamic` |
| 获取蜡烛图 / OHLCV 数据 | `kline` |

## 支持的链

| 链 | `chainId` |
|-------|-----------|
| Ethereum | `1` |
| BSC | `56` |
| Base | `8453` |
| Solana | `CT_501` |

所有四个命令（`search`、`meta`、`dynamic`、`kline`）都使用相同的 `chainId` 值。

## 如何调用 API

```bash
node <skill-dir>/scripts/cli.mjs <command> '<json_params>'
```

示例：

```bash
node <skill-dir>/scripts/cli.mjs search '{"keyword":"<keyword>","chainIds":"56"}'
```

## 命令

| 命令 | 目的 | 必填参数 | 示例 |
|---------|---------|---------------|---------|
| `search` | 通过关键词搜索代币 | `keyword`（可选：`chainIds`、`orderBy`） | `node <skill-dir>/scripts/cli.mjs search '{"keyword":"<keyword>","chainIds":"1,56,8453,CT_501"}'` |
| `meta` | 静态代币元数据 | `chainId`、`contractAddress` | `node <skill-dir>/scripts/cli.mjs meta '{"chainId":"56","contractAddress":"0x..."}'` |
| `dynamic` | 实时市场数据 | `chainId`、`contractAddress` | `node <skill-dir>/scripts/cli.mjs dynamic '{"chainId":"56","contractAddress":"0x..."}'` |
| `kline` | 蜡烛图数据 | `chainId`、`contractAddress`、`interval`（可选：`limit`、`from`、`to`、`pm`） | `node <skill-dir>/scripts/cli.mjs kline '{"chainId":"56","contractAddress":"0x...","interval":"1min","limit":500}'` |

## 规则

- **图标 URL**：`icon` 字段是相对路径。在前面添加 `https://bin.bnbstatic.com` 以获得可用的 URL。
- **数字作为字符串**：所有数值市场字段（`price`、`volume24h`、`marketCap` 等）都作为字符串返回。在进行算术运算前进行转换。
- **Kline 是二维数组**，不是 JSON 对象。每个蜡烛图：`[open, high, low, close, volume, timestamp_ms, count]`。
- **Kline 时间窗口**：`limit` 优先于 `from`（当两者都提供时）。使用 `to` 与 `limit` 结合可以获取以 `to` 结尾的最近 N 个蜡烛图。`pm` 选择价格（`p`，默认）或市值（`m`）序列。
- **`kline` 支持的间隔**：`1s`、`1min`、`3min`、`5min`、`15min`、`30min`、`1h`、`2h`、`4h`、`6h`、`8h`、`12h`、`1d`、`3d`、`1w`、`1m`。

## 完整 CLI 参考

有关每个子命令的调用方式、参数表、返回字段表和真实响应示例，请参阅 [`references/cli.md`](references/cli.md)。
