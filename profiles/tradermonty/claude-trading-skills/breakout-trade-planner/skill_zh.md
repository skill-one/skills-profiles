# 突破交易规划器

根据马克·明内维尼的突破交易方法论，从VCP筛选器输出中生成交易计划。使用最差情况入场价格计算仓位大小，执行投资组合风险限制，并输出与Alpaca API兼容的订单模板。

## 使用场景

- 用户拥有VCP筛选器JSON输出并需要交易计划
- 用户要求计算突破入场/止损/目标价格
- 用户需要VCP突破候选的Alpaca订单模板
- 用户需要投资组合热力管理下的仓位大小计算

## 前置条件

- VCP筛选器JSON输出，其中包含`schema_version: "1.0"`
- 无需API密钥（支持本地JSON文件）
- 无需外部技能依赖（仓位大小计算内置）

## 工作流程

### 第1步：生成交易计划

使用VCP筛选器输出运行规划器：

```bash
python3 skills/breakout-trade-planner/scripts/plan_breakout_trades.py \
  --input reports/vcp_screener_YYYY-MM-DD.json \
  --account-size 100000 \
  --risk-pct 0.5 \
  --output-dir reports/
```

### 第2步：查看输出

阅读生成的JSON和Markdown报告。展示：

1. **可执行订单** — 突破前的候选订单模板
2. **验证** — 需要实时确认的突破状态候选
3. **观察列表** — 需要监控的VCP发展中候选
4. **拒绝/推迟/受限** — 根据门禁或投资组合限制筛选的候选

### 第3步：解释交易计划

对每个可执行订单解释：
- 入场水平（信号与最差情况）和止损位置
- R倍数目标和风险回报比
- 两种执行模式：预放置（止损限价）与确认后（5分钟确认后的限价）
- 投资组合风险贡献和累积热力
- 经纪商和日内限制：这些模板是规划文档，非经纪商授权。如果计划可能产生同日回转交易或使用保证金，请确认用户经纪商特定的日内/日内交易控制。FINRA于2026年6月4日取代了旧的模式日交易者日计数和25,000美元最低净资产要求，改为日内保证金标准，允许经纪商通过2027年10月20日逐步实施。

## 明内维尼门禁（筛选标准）

候选必须满足所有条件：

| 条件 | 突破前 | 突破时 |
|------|--------|--------|
| valid_vcp | True | True |
| rating_band | good/strong/textbook | good/strong/textbook |
| risk_pct_worst | <= 8.0% | <= 8.0% |
| breakout_volume | — | True |
| distance_from_pivot | — | <= max_chase_pct |
| current_price | — | <= worst_entry |

## CLI参数

| 参数 | 默认值 | 描述 |
|------|--------|------|
| --account-size | (必需) | 账户净值（美元） |
| --risk-pct | 0.5 | 每笔交易的基础风险% |
| --max-position-pct | 10.0 | 最大单仓百分比 |
| --max-sector-pct | 30.0 | 最大行业敞口百分比 |
| --max-portfolio-heat-pct | 6.0 | 最大总开放风险百分比 |
| --target-r-multiple | 2.0 | 止盈R倍数 |
| --stop-buffer-pct | 1.0 | 收缩低点以下的止损缓冲 |
| --max-chase-pct | 2.0 | 超过枢轴的最大追逐 |
| --pivot-buffer-pct | 0.1 | 买入止损触发的枢轴缓冲 |
| --current-exposure-json | None | 现有投资组合敞口 |

## 输出

- `breakout_trade_plan_YYYY-MM-DD_HHMMSS.json` — 带订单模板的结构化计划
- `breakout_trade_plan_YYYY-MM-DD_HHMMSS.md` — 人类可读报告

## 交易所日历和重播

运行规划器前安装`requirements.txt`。`--as-of`接受`YYYY-MM-DD`（00:00 America/New_York）或带偏移的ISO-8601时间戳。计划有效性使用当前未关闭的XNYS会话或关闭、周末或交易所假期后的下一个真实会话。

## 资源

- `references/minervini_entry_rules.md` — 入场方法论和规则
