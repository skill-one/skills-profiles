---
name: trading-signal
description: 每笔交易的智能资金信号——每个结果都是一个来自追踪的智能资金钱包的独立买入或卖出事件，包含触发价格、当前价格、自触发以来的最大收益和退出比率。仅限BSC和Solana。用途包括："智能资金在$X的买入信号"、"任何鲸鱼刚刚买入$Y"、"过去一小时的Alpha信号"、"值得复制的交易信号"、"这些交易中的触发价格和最大收益"、"来自智能资金的链上交易信号"。
---

# 交易信号技能

## 概述

该技能通过获取链上智能资金交易信号，帮助用户追踪专业投资者：

获取智能资金买入/卖出信号
比较信号触发价格与当前价格
分析信号的最大收益和退出率
获取代币标签（例如，Pumpfun，DEX Paid）

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 获取带收益和退出率数据的链上智能资金买入/卖出信号 | `smart-money` |

## 支持的链

| 链 | chainId |
|-------|---------|
| BSC | `56` |
| Solana | `CT_501` |

## 如何调用API

```bash
node <skill-dir>/scripts/cli.mjs smart-money '{"chainId":"CT_501","page":1,"pageSize":50}'
```

## 命令

| 命令 | 目的 | 必填参数 | 示例 |
|---------|---------|---------------|---------|
| `smart-money` | 带触发价格、最大收益、退出率的智能资金买入/卖出信号 | `chainId` | `node <skill-dir>/scripts/cli.mjs smart-money '{"chainId":"56","page":1,"pageSize":50}'` |

可选参数：`page`（默认1），`pageSize`（**最大100**），`smartSignalType`（过滤；空字符串 = 所有）。

## 规则

- **`pageSize`上限为100** — 较大的值会被上游静默限制。
- **`status`枚举**（在摘要时映射为用户友好语言）：
  - `active` — 信号仍然有效
  - `timeout` — 超出观察窗口（可能仍然具有信息性，但已过时）
  - `completed` — 达到目标 / 止损
  在呈现可采取的机会时，优先选择`active`信号。
- **质量指标**：较高的`smartMoneyCount`（更多独特的智能资金地址）意味着信号可靠性更高；高`exitRate`（%）表明智能资金已经退出，因此机会可能已过。
- **`direction`** 是`buy`或`sell` — 摘要信号时始终包含此信息。
- **图标URL前缀**：`logoUrl`是相对路径；在前面添加`https://bin.bnbstatic.com`。`chainLogoUrl`已经是完整URL。时间戳是毫秒；`maxGain`是百分比字符串 — 在进行算术前转换。

## 完整CLI参考

有关每个子命令的调用、参数表、信号/标签/性能字段表和真实响应示例，请参阅 [`references/cli.md`](references/cli.md)。
