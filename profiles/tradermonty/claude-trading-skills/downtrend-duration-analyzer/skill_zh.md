# 趋势下降持续时间分析器

## 概述

分析历史价格数据以识别下降趋势周期（峰到谷）并构建修正持续时间统计分布。生成按行业和市值分段的交互式 HTML 可视化，帮助交易者了解典型的复苏时间段，并为均值回归策略设定现实的预期。

## 使用场景

- 交易者询问某个行业或市值层级的典型修正长度
- 用户想了解历史回撤复苏时间
- 构建需要现实持有期估计的均值回归或回调策略
- 比较不同市场板块的修正行为
- 设置止损超时或仓位持有期限制

## 前置条件

- Python 3.9+
- FMP API 密钥（设置 `FMP_API_KEY` 环境变量或使用 `--api-key`）
- 必要的包：`requests`、`pandas`、`numpy`（标准数据分析栈）

## 工作流程

### 第 1 步：获取历史价格数据

运行分析脚本以获取股票组合的 OHLC 数据并识别下降趋势周期。

```bash
python3 skills/downtrend-duration-analyzer/scripts/analyze_downtrends.py \
  --sector "科技" \
  --lookback-years 5 \
  --output-dir reports/
```

### 第 2 步：分析下降趋势持续时间

脚本自动执行：
1. 使用滚动窗口分析识别局部峰和谷
2. 计算每个下降趋势的持续时间（交易日）和深度（% 下跌）
3. 按行业和市值层级（巨型、大型、中型、小型）分段结果
4. 计算汇总统计数据（中位数、均值、百分位数）

### 第 3 步：生成交互式 HTML 可视化

```bash
python3 skills/downtrend-duration-analyzer/scripts/generate_histogram_html.py \
  --input reports/downtrend_analysis_*.json \
  --output-dir reports/
```

这将创建一个交互式 HTML 文件，包含：
- 下降趋势持续时间的直方图
- 行业和市值的筛选器
- 悬停工具提示显示百分位数信息
- 汇总统计数据表格

### 第 4 步：审查分布洞察

加载生成的 Markdown 报告以解读发现：
- **短期修正（5-15 天）**：上涨趋势内的典型回调
- **中期修正（15-40 天）**：标准行业轮动
- **长期修正（40 天以上）**：趋势变化或熊市

## 输出格式

### JSON 报告

```json
{
  "schema_version": "1.0",
  "analysis_date": "2026-03-28T07:00:00Z",
  "parameters": {
    "lookback_years": 5,
    "sector_filter": "Technology",
    "peak_window": 20,
    "trough_window": 20
  },
  "summary": {
    "total_downtrends": 1234,
    "median_duration_days": 18,
    "mean_duration_days": 24.5,
    "p25_duration_days": 10,
    "p75_duration_days": 32,
    "p90_duration_days": 55
  },
  "by_sector": {
    "Technology": {
      "count": 456,
      "median_days": 15,
      "mean_days": 20.3
    }
  },
  "by_market_cap": {
    "Mega": {"count": 200, "median_days": 12},
    "Large": {"count": 300, "median_days": 16},
    "Mid": {"count": 400, "median_days": 22},
    "Small": {"count": 334, "median_days": 28}
  },
  "downtrends": [
    {
      "symbol": "AAPL",
      "sector": "Technology",
      "market_cap_tier": "Mega",
      "peak_date": "2025-01-15",
      "trough_date": "2025-02-10",
      "duration_days": 18,
      "depth_pct": -12.5
    }
  ]
}
```

### Markdown 报告

```markdown
# 趋势下降分析

**日期**：2026-03-28
**回溯期**：5 年
**行业**：科技

## 汇总统计

| 指标 | 值 |
|------|----|
| 总下降趋势 | 1,234 |
| 中位数持续时间 | 18 天 |
| 均值持续时间 | 24.5 天 |
| 25 百分位数 | 10 天 |
| 75 百分位数 | 32 天 |
| 90 百分位数 | 55 天 |

## 按市值层级

| 层级 | 数量 | 中位数 | 均值 |
|------|------|--------|------|
| 巨型 ($200B+) | 200 | 12 天 | 15.2 天 |
| 大型 ($10-200B) | 300 | 16 天 | 20.1 天 |
| 中型 ($2-10B) | 400 | 22 天 | 28.4 天 |
| 小型 (<$2B) | 334 | 28 天 | 35.6 天 |

## 关键洞察

1. 大型公司修正复苏更快
2. 科技行业的中位数修正时间短于市场平均水平
3. 90% 的修正在 55 个交易日内解决

### HTML 可视化

交互式直方图保存到 `reports/downtrend_histogram_YYYY-MM-DD.html`，包含：
- 基于 Plotly.js 的交互式图表
- 行业和市值下拉筛选器
- 持续时间分布与分段控制
- 百分位数标记（P25、P50、P75、P90）

报告保存到 `reports/`，文件名：
- `downtrend_analysis_YYYY-MM-DD_HHMMSS.json`
- `downtrend_analysis_YYYY-MM-DD_HHMMSS.md`
- `downtrend_histogram_YYYY-MM-DD_HHMMSS.html`

## 资源

- `scripts/analyze_downtrends.py` -- 主要分析脚本，用于获取数据和计算下降趋势持续时间
- `scripts/generate_histogram_html.py` -- HTML 可视化生成器，带交互式直方图
- `references/downtrend_methodology.md` -- 峰/谷检测算法和市值层级定义

## 关键原则

1. **统计严谨性**：使用稳健的峰/谷检测，避免噪声引起的假信号
2. **分段很重要**：始终按行业和市值分析；平均值会掩盖重要差异
3. **现实预期**：使用百分位数（而不仅仅是均值）了解结果的完整分布
