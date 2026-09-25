# 股市专家

一款由雅虎财经数据支持的专业级金融分析工具。

## 核心功能

### 1. 实时报价 (`price`)
获取即时价格更新和当日涨跌范围。
```bash
uv run --script scripts/yf price [股票代码]
```

### 2. 专业图表 (`pro`)
生成高分辨率PNG图表，包含成交量和移动平均线。
- **K线图**: `uv run --script scripts/yf pro [股票代码] [周期]`
- **折线图**: `uv run --script scripts/yf pro [股票代码] [周期] line`
- **周期选项**: `1mo`, `3mo`, `6mo`, `1y`, `5y`, `max` 等。

### 3. 基本面分析 (`fundamentals`)
深入分析估值指标：市值、市盈率、每股收益、净资产收益率和利润率。
```bash
uv run --script scripts/yf fundamentals [股票代码]
```

### 4. 盈利与预期 (`earnings`)
查看即将发布的盈利日期和市场预期（预期营收/每股收益）。

### 5. 历史趋势 (`history`)
查看最近10天的趋势，并提供终端友好的ASCII图表。

## 股票代码示例
- **美国股票**: `AAPL`, `NVDA`, `TSLA`
- **韩国股票**: `005930.KS`（三星），`000660.KS`（SK海力士）
- **加密货币**: `BTC-USD`, `ETH-KRW`

## 技术说明
- **引擎**: Python 3.11+，`yfinance`，`mplfinance`，`rich`
- **主要优势**: 无需API密钥。通过 `uv` 自动处理依赖关系。

---
*韩语说明：可进行实时股价查询、财务指标分析及专业K线图生成的综合股票分析工具。*
