# Yahoo Finance CLI

一个使用 yfinance 从 Yahoo Finance 获取全面股票数据的 Python CLI。

## 要求

- Python 3.11+
- uv（用于内联脚本依赖项）

## 安装 uv

该脚本需要 `uv` - 一个极其快速的 Python 包管理器。检查是否已安装：

```bash
uv --version
```

如果未安装，请使用以下任一方法安装：

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### macOS (Homebrew)
```bash
brew install uv
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### pip (任何平台)
```bash
pip install uv
```

安装后，重启您的终端或运行：
```bash
source ~/.bashrc  # 或 ~/.zshrc 在 macOS 上
```

## 安装

`yf` 脚本使用 PEP 723 内联脚本元数据 - 依赖项在首次运行时自动安装。

```bash
# 使脚本可执行
chmod +x /path/to/skills/yahoo-finance/yf

# 可选地创建符号链接到 PATH 以实现全局访问
ln -sf /path/to/skills/yahoo-finance/yf /usr/local/bin/yf
```

首次运行将安装依赖项（yfinance, rich）到 uv 的缓存中。后续运行即时完成。

## 命令

### 价格（快速检查）
```bash
yf AAPL              # 简写为 price
yf price AAPL
```

### 引用（详细）
```bash
yf quote MSFT
```

### 基本面
```bash
yf fundamentals NVDA
```
显示：市盈率、每股收益、市值、利润率、净资产收益率/总资产收益率、分析师目标。

### 盈利能力
```bash
yf earnings TSLA
```
显示：下次盈利日期、每股收益预估、盈利历史及意外情况。

### 公司概况
```bash
yf profile GOOGL
```
显示：行业、部门、员工人数、网站、地址、业务描述。

### 股息
```bash
yf dividends KO
```
显示：股息率/收益率、除息日、派息比率、近期股息历史。

### 分析师评级
```bash
yf ratings AAPL
```
显示：买入/持有/卖出分布、平均评级、近期上调/下调。

### 期权链
```bash
yf options SPY
```
显示：接近市值的看涨/看跌期权，包括行权价、买价/卖价、成交量、未平仓合约量、隐含波动率。

### 历史
```bash
yf history GOOGL 1mo     # 1 个月历史
yf history TSLA 1y       # 1 年
yf history BTC-USD 5d    # 5 天
```
时间范围：1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

### 比较
```bash
yf compare AAPL,MSFT,GOOGL
yf compare RELIANCE.NS,TCS.NS,INFY.NS
```
价格、变化、52 周范围、市值的并排比较。

### 搜索
```bash
yf search "reliance industries"
yf search "bitcoin"
yf search "s&p 500 etf"
```

## 代码格式

- **美国股票：** AAPL, MSFT, GOOGL, TSLA
- **印度 NSE：** RELIANCE.NS, TCS.NS, INFY.NS
- **印度 BSE：** RELIANCE.BO, TCS.BO
- **加密货币：** BTC-USD, ETH-USD
- **外汇：** EURUSD=X, GBPUSD=X
- **ETF：** SPY, QQQ, VOO

## 示例

```bash
# 快速价格检查
yf AAPL

# 获取估值指标
yf fundamentals NVDA

# 下次盈利日期 + 历史
yf earnings TSLA

# SPY 的期权链
yf options SPY

# 比较 科技巨头
yf compare AAPL,MSFT,GOOGL,META,AMZN

# 查找 印度股票
yf search "infosys"

# 可口可乐 的股息信息
yf dividends KO

# 苹果 的分析师评级
yf ratings AAPL
```

## 故障排除

### "command not found: uv"
使用上述说明安装 uv。

### 速率限制 / 连接错误
Yahoo Finance 可能对过多请求进行速率限制。等待几分钟再试。

### "没有数据" 对于某个代码
- 验证代码是否存在：`yf search "公司名称"`
- 某些数据（期权、股息）对所有证券都不可用

## 技术说明

- 使用 PEP 723 内联脚本元数据为 uv 依赖项
- Rich 库提供彩色、格式化的表格
- 首次运行将依赖项安装到 uv 缓存中（~5 秒）
- 后续运行即时完成（缓存环境）
- 恰当处理 NaN/None 值，并提供后备方案
