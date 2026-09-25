# 交易信号技能

## 概述

该技能获取链上智能资金交易信号，帮助用户追踪专业投资者：

获取智能资金买入/卖出信号
比较信号触发价格与当前价格
分析信号最大收益和退出率
获取代币标签（例如，Pumpfun，DEX Paid）

## 何时使用此技能

| 用户意图 | 命令 |
|-------------|---------|
| 获取带收益+退出率数据的链上智能资金买入/卖出信号 | `smart-money` |

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
| `smart-money` | 智能资金买入/卖出信号，带触发价格、最大收益、退出率 | `chainId` | `node <skill-dir>/scripts/cli.mjs smart-money '{"chainId":"56","page":1,"pageSize":50}'` |

可选参数：`page`（默认1），`pageSize`(**最大100**)，`smartSignalType`（过滤；空字符串=全部）。

## 规则

- **`pageSize`上限为100** — 较大值会被上游静默限制。
- **`status`枚举**（在汇总时映射为用户友好语言）：
  - `active` — 信号仍然有效
  - `timeout` — 超出观察窗口（可能仍有参考价值，但已过时）
  - `completed` — 达到目标/止损
  查找可操作机会时优先选择`active`信号。
- **质量指标**：更高的`smartMoneyCount`（更多独特的智能资金地址）意味着信号可靠性更高；高`exitRate` (%)表明智能资金已退出，机会可能已过。
- **`direction`** 是`buy`或`sell` — 汇总信号时必须包含此项。
- **图标URL前缀**：`logoUrl`是相对路径；前置`https://bin.bnbstatic.com`。`chainLogoUrl`已是完整URL。时间戳为毫秒；`maxGain`是%字符串 — 运算前转换。

## 完整CLI参考

参考 [`references/cli.md`](references/cli.md) 了解每个子命令调用、参数表、信号/标签/性能字段表和真实响应示例。
