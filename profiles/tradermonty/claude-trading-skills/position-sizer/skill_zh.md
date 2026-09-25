# 仓位计算器

## 概述

根据风险管理原则，计算多头股票交易的理想股数。支持三种计算方法：

- **固定比例法**：每笔交易风险账户净值的固定百分比（默认：1%）
- **ATR法**：使用平均真实波幅设置波动率调整后的止损距离
- **凯利准则**：根据历史盈亏统计数据计算数学上最优的风险分配

所有方法都应用投资组合限制（最大仓位百分比、最大行业百分比），并输出最终建议的股数和完整的风险分解。默认输出为整数股。仅在用户经纪商支持该证券和订单类型的小数股时使用`--fractional`。

## 使用场景

- 用户询问“我应该买入多少股？”
- 用户需要为特定交易设置计算仓位大小
- 用户提及每笔交易风险、止损规模或投资组合分配
- 用户询问凯利准则或基于ATR的仓位计算
- 用户拥有小账户，整数股舍入会导致定义的风险预算未充分利用
- 用户想检查仓位是否在投资组合集中度限制范围内

## 前置条件

- 无需API密钥
- 仅需Python 3.9+及标准库

## 工作流程

### 第1步：收集交易参数

从用户收集以下信息：
- **必需**：账户规模（总净值）
- **模式A（固定比例法）**：入场价、止损价、风险百分比（默认1%）
- **模式B（ATR法）**：入场价、ATR值、ATR乘数（默认2.0倍）、风险百分比
- **模式C（凯利准则）**：胜率、平均盈利、平均亏损；可选入场价和止损价用于计算股数
- **可选限制**：账户最大仓位百分比、最大行业百分比、当前行业敞口
- **可选股数模式**：默认为整数股，或使用`--fractional --share-precision N`（当经纪商支持时）进行小数股计算

如果用户提供股票代码但未提供具体价格，使用可用工具查询当前价格，并根据技术分析建议入场/止损水平。

### 第2步：执行仓位计算器脚本

运行仓位计算：

```bash
# 固定比例法（最常见）
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --entry 155 \
  --stop 148.50 \
  --risk-pct 1.0 \
  --output-dir reports/

# 小账户或高价股的小数股
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 1000 \
  --entry 155 \
  --stop 148.50 \
  --risk-pct 1.0 \
  --fractional \
  --share-precision 4 \
  --output-dir reports/

# ATR法
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --entry 155 \
  --atr 3.20 \
  --atr-multiplier 2.0 \
  --risk-pct 1.0 \
  --output-dir reports/

# 凯利准则（预算模式 - 无入场价）
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --win-rate 0.55 \
  --avg-win 2.5 \
  --avg-loss 1.0 \
  --output-dir reports/

# 凯利准则（股数模式 - 带入场价/止损价）
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --entry 155 \
  --stop 148.50 \
  --win-rate 0.55 \
  --avg-win 2.5 \
  --avg-loss 1.0 \
  --output-dir reports/
```

### 第3步：加载方法学参考

阅读`references/sizing_methodologies.md`，提供所选方法、风险指南和投资组合限制最佳实践的相关背景。

### 第4步：计算多个场景

如果用户未指定单一方法，运行多个场景进行比较：
- 0.5%、1.0%、1.5%风险下的固定比例法
- 1.5倍、2.0倍、3.0倍乘数下的ATR法
- 展示每个场景的股数、仓位价值和风险金额的比较表

### 第5步：应用投资组合限制并确定最终规模

如果用户有投资组合背景，添加限制：

```bash
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --entry 155 \
  --stop 148.50 \
  --risk-pct 1.0 \
  --max-position-pct 10 \
  --max-sector-pct 30 \
  --current-sector-exposure 22 \
  --output-dir reports/
```

解释哪个限制是决定性的，以及为什么它限制了仓位。

### 第6步：生成仓位报告

呈现最终建议，包括：
- 所用方法和理由
- 精确股数和仓位价值
- 风险金额和账户百分比
- 止损价
- 任何决定性限制
- 风险管理提醒（投资组合热度、止损纪律）
- 小账户提醒：小数股不会消除经纪商最低要求、价差/滑点、佣金/费用、保证金限额、借款可用性或日内交易控制

## 输出格式

### JSON报告

```json
{
  "schema_version": "1.0",
  "mode": "shares",
  "parameters": {
    "entry_price": 155.0,
    "account_size": 100000,
    "stop_price": 148.50,
    "risk_pct": 1.0
  },
  "calculations": {
    "fixed_fractional": {
      "method": "fixed_fractional",
      "shares": 153,
      "risk_per_share": 6.50,
      "dollar_risk": 1000.0,
      "stop_price": 148.50
    },
    "atr_based": null,
    "kelly": null
  },
  "constraints_applied": [],
  "final_recommended_shares": 153,
  "final_position_value": 23715.0,
  "final_risk_dollars": 994.50,
  "final_risk_pct": 0.99,
  "binding_constraint": null
}
```

### Markdown报告

与JSON报告一起自动生成。包含：
- 参数摘要
- 活跃方法的计算详情
- 限制分析（如有）
- 最终建议（股数、价值、风险）

报告保存在`reports/`目录下，文件名分别为`position_sizer_YYYY-MM-DD_HHMMSS.json`和`.md`。

## 资源

- `references/sizing_methodologies.md`：固定比例法、ATR法和凯利准则方法的全面指南，包含示例、比较表和风险管理原则
- `scripts/position_sizer.py`：主计算脚本（CLI接口）

## 关键原则

1. **生存优先**：仓位计算是为了应对亏损连跌，而非最大化盈利
2. **1%规则**：默认每笔交易风险1%；无特殊理由不得超过2%
3. **默认整数股**：现有工作流默认保持整数股
4. **下限，永不向上舍入**：整数股模式下向下取整；小数股模式下按请求精度向下取整，以避免风险和集中度预算超支
5. **最严格限制优先**：当多个限制适用时，最严格的限制决定最终规模
6. **半凯利**：实践中永不使用全凯利；半凯利可获取75%的增长，但风险远低
7. **投资组合热度**：总开放风险不应超过账户净值的6-8%
8. **日内规则因经纪商而异**：FINRA于2026-06-04取代了旧的隔夜交易者日计数和$25,000最低净值要求，改为日内保证金标准，允许经纪商分阶段实施至2027-10-20。在保证金账户进行重复同日交易前，请检查经纪商的现行规则。
9. **亏损的非对称性**：50%亏损需要100%盈利才能恢复；相应调整仓位
