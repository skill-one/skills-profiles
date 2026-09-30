---
name: yfinance-data
description: 使用 yfinance Python 库（Yahoo Finance）获取金融和市场数据。每当用户需要股票数据时，都可以使用此技能：当前报价和价格历史、财务报表（利润表、资产负债表、现金流量表）、期权链、股息和拆分、盈利和分析师预测、价格目标及评级、机构及内幕人士持股、新闻、多股票比较、股票筛选器或行业和部门数据。即使用户只提供股票代码（AAPL、MSFT、TSLA），且需要推断意图时，也可以使用它。对于盈利预览或回顾、估值修正、相关性、流动性或 ETF 溢价分析，请优先使用专用技能。
---

# yfinance 数据技能

使用 [yfinance](https://github.com/ranaroussi/yfinance) Python 库从雅虎财经获取金融和市场数据。

**重要提示**：yfinance 与雅虎公司无关。数据仅供研究和教育目的使用。

---

## 第 1 步：确保 yfinance 可用

**当前环境状态：**

```
!`python3 -c "exec('try:\n import yfinance\n print(\'yfinance \' + yfinance.__version__ + \' 已安装\')\nexcept Exception:\n print(\'YFINANCE_NOT_INSTALLED\')')"`
```

如果显示 `YFINANCE_NOT_INSTALLED`，请在运行任何代码前安装它：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
```

如果 yfinance 已安装，则跳过安装步骤，直接进行下一步。

---

## 第 2 步：确定用户需求

将用户的请求与下表中的一个或多个数据类别匹配，然后使用 `references/api_reference.md` 中的相应代码。

| 用户请求 | 数据类别 | 主要方法 |
|---|---|---|
| 股票价格、报价 | 当前价格 | `ticker.info` 或 `ticker.fast_info` |
| 价格历史、图表数据 | 历史OHLCV | `ticker.history()` 或 `yf.download()` |
| 资产负债表 | 财务报表 | `ticker.balance_sheet` |
| 收入报表、收入 | 财务报表 | `ticker.income_stmt` |
| 现金流量 | 财务报表 | `ticker.cashflow` |
| 股息 | 重大事件 | `ticker.dividends` |
| 股票拆分 | 重大事件 | `ticker.splits` |
| 期权链、看涨期权、看跌期权 | 期权数据 | `ticker.option_chain()` |
| 盈利、每股收益 | 分析 | `ticker.earnings_history` |
| 分析师价格目标 | 分析 | `ticker.analyst_price_targets` |
| 推荐意见、评级 | 分析 | `ticker.recommendations` |
| 升级/降级 | 分析 | `ticker.upgrades_downgrades` |
| 机构持有人 | 持有情况 | `ticker.institutional_holders` |
| 内部人士交易 | 持有情况 | `ticker.insider_transactions` |
| 公司概览、行业 | 基本信息 | `ticker.info` |
| 比较多只股票 | 批量下载 | `yf.download()` |
| 筛选/过滤股票 | 筛选器 | `yf.screen()` + `yf.EquityQuery` |
| 行业/行业数据 | 市场数据 | `yf.Sector` / `yf.Industry` |
| 新闻 | 新闻 | `ticker.news` |

---

## 第 3 步：编写和执行代码

### 通用模式

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
# ... 使用参考资料中的适当方法
```

### 关键规则

1. **始终使用 try/except 包裹** — 雅虎财经可能会限流或返回空数据
2. **使用 `yf.download()` 进行多只股票比较** — 它支持多线程，速度更快
3. **对于期权，先列出到期日期** 使用 `ticker.options`，然后调用 `ticker.option_chain(date)`
4. **对于季度数据**，使用 `quarterly_` 前缀：`ticker.quarterly_income_stmt`、`ticker.quarterly_balance_sheet`、`ticker.quarterly_cashflow`
5. **对于大日期范围**，注意日内限制 — 1m 数据只能回溯约 7 天，1h 数据约 730 天
6. **清晰打印数据框** — 使用 `.to_string()` 或 `.to_markdown()` 提高可读性，或选择关键列
7. **时区处理** — yfinance 返回带时区的 datetime 索引（例如 `America/New_York`）。比较日期时，始终使用 `pd.Timestamp(..., tz=...)` 或使用 `.tz_localize(None)` 移除时区。参考文件中有详细说明。

### 有效周期和间隔

| 周期 | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` |
|---|---|
| **间隔** | `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` |

---

## 第 4 步：展示数据

首先回答用户要求的数据，然后提供支持性表格（Markdown 格式，或带有关键列的 DataFrame）。突出数据中的任何显著信息——盈利超预期或不及预期、异常成交量、股息变动——并在需要时添加背景信息，如行业平均数、历史范围或分析师共识，以改变数据的解读方式。如果用户需要图表，请将数据与可视化结合展示。

---

## 参考文件

- `references/api_reference.md` — 完整的 yfinance API 参考文件，包含每个数据类别的代码示例

需要精确的方法签名或边缘情况处理时，请查阅参考文件。
