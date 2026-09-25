# IBD分布日监控

## 目的
检测主要市场ETF（以QQQ作为纳斯达克代理，SPY作为标普500代理）的IBD风格分布日，并生成每日市场恶化信号以及TQQQ/QQQ敞口建议。设计用于收盘后复盘。

## 使用场景
调用此技能：
- 美国市场收盘后每日。
- 增加TQQQ敞口或调整杠杆头寸前。
- 评估上升趋势是否开始面临回调风险时。
- 作为FTD（跟随日）检测或其他市场状态框架的上游输入。

**禁止使用此技能**：
- 执行交易或修改订单。
- 在IBD规则集之外生成任意市场预测。

## 输入
- 符号（默认：QQQ, SPY）和回溯期（默认80个交易日）。
- 可选`--as-of YYYY-MM-DD`用于对历史会话进行回测。
- 策略上下文：工具（TQQQ或QQQ）、当前敞口%、基础跟踪止损%。
- FMP API密钥通过`--api-key`、`config.data.api_key`或`FMP_API_KEY`环境变量（按优先级顺序）获取。

## 核心规则
当满足以下条件时检测到分布日：
1. 当日收盘价至少低于昨日收盘价0.2%。
2. 当日成交量大于昨日成交量。

当满足以下任一条件时，分布日将从活跃计数中移除：
- 自分布日以来已超过25个交易日。
- 指数自分布日收盘价上涨5%（默认使用分布日后的最高价；可配置为收盘价）。

由于没有分布日后的会话来评估5%涨幅，因此当日的分布日永远不会立即失效。

## 计数约定
- `d5_count` / `d15_count` / `d25_count` 计数活跃记录中`age_sessions <= N`的记录。
- 这意味着将检查**N+1个会话**（包含0..N的会话）。因此报告会说“在N个会话内”而不是“直近N个交易日”以避免歧义。

## 风险分类
| 风险 | 触发条件 |
|------|---------|
| 正常 | `d25 <= 2` |
| 谨慎 | `d25 >= 3` |
| 高 | `d25 >= 5` 或 `d15 >= 3` 或 `d5 >= 2` |
| 严重 | `d25 >= 6` 或 `d15 >= 4` 或 (`market_below_21ema_or_50ma` AND `d25 >= 5`) |

当QQQ和SPY都加载时，将应用QQQ加权整体逻辑（TQQQ感知）：单个严重将升级为严重；QQQ高将升级为整体高；QQQ正常+SPY高仍将升级为高（宽市场溢出）。

## TQQQ敞口策略
| 风险 | 动作 | 目标敞口 | 跟踪止损 |
|------|--------|-----------------|---------------|
| 正常 | 持有或跟随基础策略 | 100% | 基础 |
| 谨慎 | 避免新增敞口 | 75% | base, 7%中较小值 |
| 高 | 降低敞口 | 50% | base, 5%中较小值 |
| 严重 | 关闭TQQQ或对冲 | 25% | base, 3%中较小值 |

QQQ使用较缓和的策略（高=75%，严重=50%），因为它没有3倍杠杆。

## 工作流程
1. 通过FMP加载配置符号的OHLCV（`get_historical_prices`）。
2. 验证数据质量；在审计中记录跳过的会话。
3. 通过`prepare_effective_history`重新基准化，使`effective_history[0]`为评估会话。
4. 检测原始分布日；添加`high_since`、失效事件和状态。
5. 计算`d5` / `d15` / `d25`活跃记录。
6. 计算21EMA和50SMA过滤器；标记`market_below_21ema_or_50ma`（数据不足时为None）。
7. 对每个指数进行分类，然后使用QQQ加权策略合并。
8. 为配置的工具生成投资组合动作。
9. 将JSON + Markdown报告写入`--output-dir`，并自动屏蔽API密钥。

## 输出
保存到`reports/`（或`--output-dir`）：
- `ibd_distribution_day_monitor_YYYY-MM-DD_HHMMSS.json`
- `ibd_distribution_day_monitor_YYYY-MM-DD_HHMMSS.md`

JSON使用UTF-8，`ensure_ascii=False`（保留日语说明）。敏感密钥（`api_key`、`fmp_api_key`、`token`等）将自动屏蔽。

## 运行原则
- 除非故意修改`config/default.yaml`，否则不要覆盖IBD规则定义。
- 始终说明哪些日期贡献了活跃计数。
- 将缺失或不可靠的成交量数据视为警告（audit_flag），而不是分布日。
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

## API需求
需要FMP API密钥。免费套餐（每日250次调用）足以支持每日QQQ + SPY运行。

## 相关技能
- `ftd-detector`：通过跟随日进行底部确认（此顶部信号的对应技能）。
- `market-top-detector`：使用O'Neil分布+其他组件生成0-100的顶部概率分数。
- `position-sizer`：将风险管理建议转换为股份数量。
