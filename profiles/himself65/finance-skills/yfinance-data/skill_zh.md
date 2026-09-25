# yfinance 数据技能

使用 [yfinance](https://github.com/ranaroussi/yfinance) Python 库从雅虎财经获取金融和市场数据。

**重要提示**：yfinance 与雅虎公司没有关联。数据仅供研究和教育目的使用。

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

如果 yfinance 已经安装，则跳过安装步骤，直接进行下一步。

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
| 股息 | 公司行动 | `ticker.dividends` |
| 股票拆分 | 公司行动 | `ticker.splits` |
| 期权链、看涨期权、看跌期权 | 期权数据 | `ticker.option_chain()` |
| 盈利、每股收益 | 分析 | `ticker.earnings_history` |
| 分析师价格目标 | 分析 | `ticker.analyst_price_targets` |
| 建议、评级 | 分析 | `ticker.recommendations` |
| 评级上调/下调 | 分析 | `ticker.upgrades_downgrades` |
| 机构持有人 | 持有情况 | `ticker.institutional_holders` |
| 内部人士交易 | 持有情况 | `ticker.insider_transactions` |
| 公司概览、行业 | 一般信息 | `ticker.info` |
| 比较多只股票 | 批量下载 | `yf.download()` |
| 筛选/过滤股票 | 筛选器 | `yf.Screener` + `yf.EquityQuery` |
| 行业/行业数据 | 市场数据 | `yf.Sector` / `yf.Industry` |
| 新闻 | 新闻 | `ticker.news` |

---

## 第 3 步：编写和执行代码

### 通用模式

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])

import yfinance as yf

ticker = yf.Ticker("AAPL")
# ... 使用参考中的适当方法
```

### 关键规则

1. **始终使用 try/except 包裹** — 雅虎财经可能会限流或返回空数据
2. **使用 `yf.download()` 进行多只股票比较** — 它支持多线程，速度更快
3. **对于期权，首先列出到期日期** 使用 `ticker.options`，然后调用 `ticker.option_chain(date)`
4. **对于季度数据**，使用 `quarterly_` 前缀：`ticker.quarterly_income_stmt`、`ticker.quarterly_balance_sheet`、`ticker.quarterly_cashflow`
5. **对于大日期范围**，注意日内限制 — 1m 数据只能回溯约 7 天，1h 数据约 730 天
6. **清晰打印 DataFrame** — 使用 `.to_string()` 或 `.to_markdown()` 提高可读性，或选择关键列
7. **时区处理** — yfinance 返回时区感知的 datetime 索引（例如 `America/New_York`）。比较日期时，始终使用 `pd.Timestamp(..., tz=...)` 或使用 `.tz_localize(None)` 去除时区。参考文件中有详细信息。

### 有效周期和间隔

| 周期 | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` |
|---|---|
| **间隔** | `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` |

---

## 第 4 步：展示数据

获取数据后，清晰地展示：

1. **总结关键数据** 在简短的文本回复中（当前价格、市值、市盈率等）
2. **展示表格数据** 格式化以提高可读性 — 使用 Markdown 表格或格式化 DataFrame
3. **突出重要项** — 盈利超预期/不及预期、异常成交量、股息变化
4. **提供背景信息** — 与行业平均水平、历史范围或分析师共识进行比较（如适用）

如果用户似乎需要图表或可视化，结合适当的可视化方法（例如，生成 HTML 图表或描述趋势）。

---

## 参考文件

- `references/api_reference.md` — 完整的 yfinance API 参考，包含每个数据类别的代码示例

需要精确的方法签名或边缘情况处理时，请阅读参考文件。
