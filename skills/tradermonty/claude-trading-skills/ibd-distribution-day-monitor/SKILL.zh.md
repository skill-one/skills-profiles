---
name: ibd-distribution-day-monitor
description: 检测 QQQ/SPY 的 IBD 风格分布日（收盘下跌至少 0.2%，成交量放大），跟踪 25 个交易日到期和 5% 作废率，统计 d5/d15/d25 集群，分类市场风险（正常/谨慎/高/严重），并发出 TQQQ/QQQ 投资组合建议。可在收盘后、TQQQ 投资组合调整前或作为 FTD/市场状态框架的输入使用。不执行交易。
---

# IBD 分配日监控器

## 目的
检测主要市场 ETF 的 IBD 风格分配日（以 QQQ 作为纳斯达克代理，SPY 作为标普 500 代理），并生成每日市场恶化信号以及 TQQQ/QQQ 投资比例建议。设计用于收盘后复盘。

## 使用场景
调用此技能：
- 美国市场收盘后每日。
- 增加 TQQQ 投资比例或调整杠杆头寸前。
- 评估上升趋势是否变得容易受到修正时。
- 作为 FTD（持续日）检测或其他市场状态框架的上游输入。

不要使用此技能：
- 执行交易或修改订单。
- 在 IBD 规则集之外生成自主的市场预测。

## 输入
- 符号（默认：QQQ、SPY）和回溯期（默认 80 个交易日）。
- 可选 `--as-of YYYY-MM-DD` 用于对历史会话进行回测。
- 策略上下文：工具（TQQQ 或 QQQ）、当前投资比例%、基础跟踪止损比例。
- 通过 `--api-key`、`config.data.api_key` 或 `FMP_API_KEY` 环境变量获取 FMP API 密钥（按优先级顺序）。

## 核心规则
当满足以下条件时检测到分配日：
1. 当天收盘价至少比前一天收盘价低 0.2%。
2. 当天成交量大于前一天成交量。

当满足以下任一条件时，分配日将从活跃计数中移除：
- 自分配日以来已超过 25 个交易日。
- 指数从分配日收盘价上涨了 5%（默认使用分配日后的最高价；可配置为收盘价）。

当天的分配日不会立即失效，因为没有分配日后的会话来评估 5% 的涨幅。

## 计数约定
- `d5_count` / `d15_count` / `d25_count` 计数活跃记录中 `age_sessions <= N` 的记录。
- 这意味着检查 **N+1 个会话**（包含 0 到 N 的会话）。因此报告会说“在 N 个会话内”而不是“直近 N 个交易日”以避免歧义。

## 风险分类
| 风险 | 触发条件 |
|------|---------|
| 正常 | `d25 <= 2` |
| 谨慎 | `d25 >= 3` |
| 高 | `d25 >= 5` 或 `d15 >= 3` 或 `d5 >= 2` |
| 严重 | `d25 >= 6` 或 `d15 >= 4` 或 (`market_below_21ema_or_50ma` AND `d25 >= 5`) |

当 QQQ 和 SPY 都加载时，QQQ 加权的整体逻辑适用（TQQQ 感知）：单个严重会升级为严重；QQQ 高风险升级为整体高风险；QQQ 正常 + SPY 高风险仍会升级为高风险（宽市场溢出）。

## TQQQ 投资比例策略
| 风险 | 动作 | 目标投资比例 | 跟踪止损 |
|------|--------|-----------------|---------------|
| 正常 | 持有或跟随基础策略 | 100% | 基础 |
| 谨慎 | 避免新增投资 | 75% | base, 7% 中的较小值 |
| 高 | 降低投资比例 | 50% | base, 5% 中的较小值 |
| 严重 | 关闭 TQQQ 或对冲 | 25% | base, 3% 中的较小值 |

QQQ 使用较缓和的策略（高风险=75%，严重=50%），因为它没有 3 倍杠杆。

## 工作流程
1. 通过 FMP 加载配置符号的 OHLCV（`get_historical_prices`）。
2. 验证数据质量；在审计中记录跳过的会话。
3. 通过 `prepare_effective_history` 重新基准，使 `effective_history[0]` 为评估会话。
4. 检测原始分配日；添加 `high_since`、失效事件和状态。
5. 计算 `d5` / `d15` / `d25` 活跃记录。
6. 计算 21EMA 和 50SMA 过滤器；标记 `market_below_21ema_or_50ma`（数据不足时为 None）。
7. 对每个指数进行分类，然后使用 QQQ 加权策略合并。
8. 为配置的工具生成投资组合动作。
9. 将 JSON + Markdown 报告写入 `--output-dir`，并自动隐藏 API 密钥。

## 输出
保存到 `reports/`（或 `--output-dir`）：
- `ibd_distribution_day_monitor_YYYY-MM-DD_HHMMSS.json`
- `ibd_distribution_day_monitor_YYYY-MM-DD_HHMMSS.md`

JSON 使用 UTF-8 并设置 `ensure_ascii=False`（保留日语说明）。敏感密钥（`api_key`、`fmp_api_key`、`token` 等）会自动隐藏。

## 运行原则
- 除非故意修改 `config/default.yaml`，否则不要覆盖 IBD 规则定义。
- 始终说明哪些日期贡献了活跃计数。
- 将缺失或不可靠的成交量数据视为警告（audit_flag），而不是分配日。
- 不要下单。投资组合动作是风险管理建议，不是执行指令。

## CLI
```bash
python3 skills/ibd-distribution-day-monitor/scripts/ibd_monitor.py \
  --symbols QQQ,SPY \
  --lookback-days 80 \
  --instrument TQQQ \
  --current-exposure 100 \
  --base-trailing-stop 10 \
  --output-dir reports/
```

## API 要求
需要 FMP API 密钥。免费套餐（每天 250 次调用）足以支持每日 QQQ + SPY 的运行。

## 相关技能
- `ftd-detector`：通过持续日进行底部确认（此顶部信号的对应方）。
- `market-top-detector`：使用 O'Neil 分配 + 其他组件生成 0-100 的顶部概率分数。
- `position-sizer`：将风险管理建议转换为股份数量。
