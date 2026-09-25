# 加密市场排名技能
## 概述

一个CLI工具支持五个排行榜/排名端点。代理程序发出带有JSON数据的子命令；CLI负责URL路径、方法选择、查询字符串构建和上游错误映射。

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 社交热度排行榜，最高社交热度代币+情绪摘要 | `social-hype` |
| 统一代币排名，趋势/热搜/Alpha/股票代币列表（带过滤） | `token-rank` |
| 智能资金流入排名，当前接收最多智能资金净流入的代币 | `smart-money-inflow` |
| 梗图代币排名，Pulse启动板上表现最好的梗图代币（突破分数） | `meme-rank` |
| 地址PnL排名，顶级交易员PnL排行榜（全部/KOL） | `address-pnl-rank` |

## 支持的链

| 链 | chainId | 支持 |
|-------|---------|--------------|
| BSC | `56` | `social-hype`, `token-rank`, `smart-money-inflow`, `meme-rank`, `address-pnl-rank` |
| Solana | `CT_501` | `social-hype`, `token-rank`, `smart-money-inflow`, `address-pnl-rank` |
| Base | `8453` | `social-hype`, `token-rank`, `smart-money-inflow`, `address-pnl-rank` |
| Ethereum | `1` | `token-rank`, `address-pnl-rank` |

> `meme-rank` 仅支持BSC (`56`)。CLI会在调用API前，使用错误信息拒绝不支持的chainIds。

## 如何调用API

```bash
node <skill-dir>/scripts/cli.mjs token-rank \
  '{"rankType":10,"chainId":"56","period":50,"sortBy":70,"orderAsc":false,"page":1,"size":20}'
```

## 命令

| 命令 | 目的 | 必填参数 | 示例 |
|---------|---------|---------------|---------|
| `social-hype` | 社交热度排行榜（带情绪+摘要） | `chainId`, `targetLanguage`, `timeRange` | `node <skill-dir>/scripts/cli.mjs social-hype '{"chainId":"56","targetLanguage":"en","timeRange":1}'` |
| `token-rank` | 统一排名（趋势/热搜/Alpha/股票）带过滤 | `rankType`, `chainId` | `node <skill-dir>/scripts/cli.mjs token-rank '{"rankType":10,"chainId":"56","page":1,"size":20}'` |
| `smart-money-inflow` | 智能资金净流入排名 | `chainId` (CLI默认`tagType`为`2`) | `node <skill-dir>/scripts/cli.mjs smart-money-inflow '{"chainId":"56","period":"24h"}'` |
| `meme-rank` | Pulse启动板上表现最好的前100名梗图代币（突破分数） | `chainId` | `node <skill-dir>/scripts/cli.mjs meme-rank '{"chainId":"56"}'` |
| `address-pnl-rank` | 顶级交易员PnL排行榜 | `chainId`, `period`, `tag` | `node <skill-dir>/scripts/cli.mjs address-pnl-rank '{"chainId":"CT_501","period":"30d","tag":"ALL","pageNo":1,"pageSize":25}'` |

## 使用流程

> **在调用任何API之前，你必须阅读其参考文件以获取完整命令、参数、示例和响应字段。**

1. **选择命令** — 将用户意图与上表中的"何时使用"列匹配
   - 对于token-rank，还需决定`rankType`：`10`=趋势，`11`=热搜，`20`=Alpha，`40`=股票，见下文规则
2. **设置链** — 从支持的链中挑选`chainId`；对于token-rank可省略（支持所有链）
3. **设置时间窗口**（如适用）
   - social-hype: `timeRange=1` (24h)
   - token-rank `period`: `10`=1m, `20`=5m, `30`=1h, `40`=4h, `50`=24h (默认`50`)
   - smart-money-inflow `period`: `5m` / `1h` / `4h` / `24h` (默认`24h`)
   - address-pnl-rank `period`: `7d` / `30d` / `90d` (默认`30d`)
4. **设置过滤条件** — 如果用户提到特定条件（市值、交易量、持币者、PnL、胜率等），请参考过滤参数
5. **阅读参考** — 打开对应命令的参考文件，查看完整参数、示例和响应字段
6. **调用cli** — 运行scripts文件夹中的cli.mjs

## 规则

- **`rankType`枚举（用于`token-rank`）**：`10`=趋势，`11`=热搜，`20`=Alpha，`40`=股票。
  - **趋势（`10`）是默认值。** 适用于任何通用"热门/趋势/流行/热门/趋势/火"请求——这是用户99%情况下所指的排行榜。
  - **热搜（`11`）需要明确信号。** 仅在用户说"热搜"、"top search"、"最多搜索"、"搜索榜"或其他明确表示需要搜索量驱动的列表时选择（而非价格/交易量驱动）。搜索量排序（`sortBy: 2`）仅与热搜搭配有意义。
  - 模糊时选择趋势。不要无声地切换到热搜。
- **`smart-money-inflow`的`tagType`默认值**：CLI自动填充`tagType: 2`（上游需要它，且`2`是当前唯一支持的值）。调用者无需传递；如果传递，调用者的值优先。
- **`period`值因命令而异**：`social-hype.timeRange`是数字（`1`=24h）；`token-rank.period`是代码（`10`=1m, `20`=5m, `30`=1h, `40`=4h, `50`=24h）；`smart-money-inflow.period`是字符串（`5m`/`1h`/`4h`/`24h`）；`address-pnl-rank.period`是字符串（`7d`/`30d`/`90d`）。详情见`references/cli.md`。
- **`token-rank`支持丰富的过滤条件**（最小/最大对：`marketCap`, `volume`, `liquidity`, `holders`, `percentChange`等）。将它们作为JSON体的一级字段传递——CLI将原样转发。
- **图标/Logo URL前缀**：大多数`icon` / `logo` / `metaInfo.logo` / `tokenIconUrl`字段是相对路径。添加`https://bin.bnbstatic.com`以渲染。`chainLogoUrl`已是完整URL。
- **数值字段以字符串形式到达**（`price`, `marketCap`, `percentChange*`等）——在算术运算前转换。
- **`address-pnl-rank.pageSize`上限为25**——更大的值会被静默限制。
- **所有时间戳都是毫秒。**

## 完整CLI参考

参考[`references/cli.md`](references/cli.md)以获取每个子命令调用、参数表、返回字段表、排序选项和过滤表，以及真实响应示例。
