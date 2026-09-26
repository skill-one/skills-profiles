# FinLab 量化交易套件

## 前置條件

**在運行任何 FinLab 代碼之前，請按順序驗證以下內容：**

1. **已安裝 uv** (Python 套件管理器)：

   ```bash
   uv --version
   ```

   如果 uv 未安裝，請告訴用戶安裝它。

   安裝後，確保 `uv` 在 PATH 中：

   ```bash
   source $HOME/.local/bin/env 2>/dev/null  # 將 uv 添加到當前 Shell
   ```

2. **通過 uv 安裝 FinLab** (需要 >= 2.0.0)：

   ```bash
   uv python install 3.12  # 確保 Python 可用 (如果已安裝則跳過)
   uv pip install --system "finlab>=2.0.0" 2>/dev/null || uv pip install "finlab>=2.0.0"
   ```

   **或者使用 `uv run` 進行零配置執行** (推薦用於一次性腳本)：

   ```bash
   uv run --with "finlab" python3 script.py
   ```

   `uv run --with` 會自動創建一個包含依賴項的臨時環境 — 不需要管理 venv。

   **偏好零安裝？** 直接在 [FinLab Studio](https://studio.finlab.finance) 中運行筆記本 — 一個托管的 Jupyter 環境，其中 `finlab` 已預先安裝，並且您的賬戶已經登錄。

3. **已登錄 FinLab** (需要 - 沒有它數據訪問會失敗)：

   **桌面版 (有瀏覽器)：** 登錄一次，然後只需導入：

   ```bash
   python -m finlab login   # 打開 FinLab (Firebase) 瀏覽器登錄；憑據將緩存到本地
   ```

   ```python
   import finlab            # 緩存憑據將自動獲取
   finlab.login()           # 選擇性：重用緩存憑據，或者如果沒有則開始瀏覽器登錄
   ```

   `finlab.login()` 打開 FinLab 瀏覽器登錄 (Firebase 認證)。沒有 TTY 時，它會打印一個登錄 URL，可以在任何設備上打開。

   **無頭機器 / cron / Docker：** 在一台有瀏覽器的機器上登錄，然後運行 `python -m finlab token --env`，然後在無頭機器上設置打印的 `FINLAB_REFRESH_TOKEN`、`FINLAB_SESSION_ID` 和 `FINLAB_API_KEY` 環境變量。

   **Google Colab：** 在一個單元格中運行 `finlab.login()`。

   不要使用 `FINLAB_API_TOKEN` 或 `finlab.login('<api_token>')` — 過時的 API 代碼登錄已被棄用 (`python -m finlab migrate` 顯示遷移指南)。

## 語言

**使用用戶的語言回應。** 如果用戶使用中文，使用中文回應。如果使用英文，使用英文回應。

## 市場支持

FinLab 支持TW（默認）、US、KR、JP、HK，以及台灣興櫃 (`rotc`) 和台灣可轉債券 (`tw_cb`)。每次會話中選擇一次市場，使用 `data.set_market(<code>)`；通用數據集名稱，如 `price:收盤價` 或 `monthly_revenue:當月營收` 將解析為活動市場的表格，因此策略代碼跨市場編寫方式相同。`data.set_market('rotc')` *(v2.0.9)* 啟用興櫃 (台灣興櫃) — 在您需要預上市價格行動或不存在於主 TSE/OTC 目錄中的收入因素時使用它。

此文件的其他部分以及 [dataframe-reference.md](dataframe-reference.md)、[backtesting-reference.md](backtesting-reference.md)、[best-practices.md](best-practices.md)、[factor-analysis-reference.md](factor-analysis-reference.md) 和 [machine-learning-reference.md](machine-learning-reference.md) 都是 **市場無關的** — API 在各市場行為相同。

對於 US 市場工作 — 無論是單個股票 (`data.set_market('us')`) 還是 ETF/基金 (`data.set_market('us_fund')`) — **首先閱讀 [us-market.md](us-market.md)**。應觸發它的查詢包括：US 股票、標普 500、納斯達克 100、美股、SPY / QQQ、行業 SPDRs、杠杆/反向 ETFs、ETF 轉動、`us_price:*`、`us_fund_price:*`、`data.us_universe(...)` 或 `us_income_statement:*` / `us_cash_flow:*` / `us_balance_sheet:*`。它記錄：

- 哪些 US 數據表格安全可用於回測，而不是僅僅是當前快照 (分析共識、比率、DCF 僅限當前 — 不要用於歷史)
- 與申報日期對齊的季度基本面 (`key_date == filing_date`) — 不需要 `.shift()` 工作區
- US `Report` API 名稱 (`creturn` / `daily_creturn` / `get_stats()`；沒有 `get_equity()`)
- US 回測默認值對於兩個市場：`USMarket` (`fee_ratio=0`，`tax_ratio=0`，`trade_at_price='close'`) 和 `USFundMarket` 用於 ETF/基金回測
- 如何 `data.set_market(...)` 是會話範圍的開關 (在 `data.get()` 上沒有 `market=` 關鍵字)
- 美元交易量頂 N 宇宙構建 (可回溯到 2016)，標普 500 / 納斯達克 100 成員身份通過 `data.us_universe(index='S&P 500' | 'NASDAQ 100')` 及其 2022-11 起始歷史限制、質量門檻和行業排除理由
- US 數據特定於前瞻性偏差清單 (滾動窗口宇宙過濾器、避免生存偏誤)
- 通過 `USFundMarket` 和 `us_fund_price:*` 的 ETF / 行業轉動回測

其他市場查詢可以跳過該文件。

## 帳戶層級與使用

### 層級

| 層級 | 每日限制 |
| ---- | ----------- |
| 免費 | 500 MB      |
| VIP  | 5000 MB     |

使用 `python -m finlab status` 檢查當前計劃和配額。

### 使用重置

- 每天在 **UTC+8 上午 8:00** 重置
- 超過限制時，用戶必須等待重置或升級到 VIP 在 [finlab.finance](https://finlab.finance)

## 快速啟動示例

```python
from finlab import data
from finlab.backtest import sim

# 1. 獲取數據
close = data.get("price:收盤價")
vol = data.get("price:成交股數")
pb = data.get("price_earning_ratio:股價淨值比")

# 2. 創建條件
cond1 = close.rise(10)  # 近 10 天漲幅
cond2 = vol.average(20) > 1000*1000  # 高流動性
cond3 = pb.rank(axis=1, pct=True) < 0.3  # 低 P/B 比率

# 3. 結合條件並選擇股票
position = cond1 & cond2 & cond3
position = pb[position].is_smallest(10)  # P/B 最小的前 10 標的

# 4. 回測
report = sim(position, resample="M", upload=False)

# 5. 打印指標 - 兩種等價方式：

# 選項 A：使用指標對象
print(report.metrics.annual_return())
print(report.metrics.sharpe_ratio())
print(report.metrics.max_drawdown())

# 選項 B：使用 get_stats() 字典 (鍵名不同!)
stats = report.get_stats()
print(f"CAGR: {stats['cagr']:.2%}")
print(f"Sharpe: {stats['monthly_sharpe']:.2f}")
print(f"MDD: {stats['max_drawdown']:.2%}")

# 基準指標 (finlab >= 2.0.17)：通過 report.get_benchmark_stats() 使用相同鍵

# 6. 將 FinLab 生成的 HTML 報告寫入 (必須 — 不要手動編輯自己的 HTML)
report.to_html("report.html")
print("打開 report.html 檢查股價曲線、月度收益、回撤和交易列表。")
```

## 核心工作流程：5 步驟策略開發

### 步驟 1：獲取數據

使用 `data.get("<TABLE>:<COLUMN>")` 獲取數據：

```python
from finlab import data

# 價格數據
close = data.get("price:收盤價")
volume = data.get("price:成交股數")

# 財務報表
roe = data.get("fundamental_features:ROE稅後")
revenue = data.get("monthly_revenue:當月營收")

# 定價
pe = data.get("price_earning_ratio:本益比")
pb = data.get("price_earning_ratio:股價淨值比")

# 机构交易
foreign_buy = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")

# 技術指標
rsi = data.indicator("RSI", timeperiod=14)
macd, macd_signal, macd_hist = data.indicator("MACD", fastperiod=12, slowperiod=26, signalperiod=9)
```

**使用 `data.universe()` 按市場/類別過濾：**

```python
# 限制為特定行業
with data.universe(market='TSE_OTC', category=['水泥工業']):
    price = data.get('price:收盤價')

# 全局設置
data.set_universe(market='TSE_OTC', category='半導體')
```

使用 `data.search('keyword', market='<market>')` 發現可用數據集。支持市場：`tw`，`us`，`kr`，`jp`，`hk`。使用數據集的原始語言中的關鍵字 (例如 `data.search('營收', market='tw')`，`data.search('revenue', market='us')`)。

### 步驟 2：創建因子與條件

使用 FinLabDataFrame 方法創建布爾條件：

```python
# 趨勢
rising = close.rise(10)  # 與 10 天前相比漲幅
sustained_rise = rising.sustain(3)  # 持續 3 個連續天漲幅

# 移動平均線
sma60 = close.average(60)
above_sma = close > sma60

# 排名
top_market_value = data.get('etl:market_value').is_largest(50)
low_pe = pe.rank(axis=1, pct=True) < 0.2  # P/E 排名最低的 20%

# 行業排名
industry_top = roe.industry_rank() > 0.8  # 行業內排名前 20%
```

參見 [dataframe-reference.md](dataframe-reference.md) 了解所有 FinLabDataFrame 方法。

### 步驟 3：構建 Position DataFrame

使用 `&` (AND)，`|` (OR)，`~` (NOT) 結合條件：

```python
# 簡單位置：持有滿足所有條件的股票
position = cond1 & cond2 & cond3

# 限制股票數量
position = factor[condition].is_smallest(10)  # 持有前 10 標的

# 入場/離場信號與 hold_until
entries = close > close.average(20)
exits = close < close.average(60)
position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
```

**重要：** Position DataFrame 應該具有：

- **索引**：DatetimeIndex (日期)
- **列**：股票 ID (例如，'2330'，'1101')
- **值**：布爾 (True = 持有) 或數字 (位置大小)

### 步驟 4：回測

```python
from finlab.backtest import sim

# 基本回測
report = sim(position, resample="M")

# 帶風險管理
report = sim(
    position,
    resample="M",
    stop_loss=0.08,
    take_profit=0.15,
    trail_stop=0.05,
    position_limit=1/3,
    fee_ratio=1.425/1000/3,
    tax_ratio=3/1000,
    trade_at_price='open',
    upload=False
)

# 提取指標 - 兩種方式：
# 選項 A：使用指標對象
print(f"Annual Return: {report.metrics.annual_return():.2%}")
print(f"Sharpe Ratio: {report.metrics.sharpe_ratio():.2f}")
print(f"Max Drawdown: {report.metrics.max_drawdown():.2%}")

# 選項 B：使用 get_stats() 字典 (注意：鍵名不同!)
stats = report.get_stats()
print(f"CAGR: {stats['cagr']:.2%}")           # 'cagr' 不是 'annual_return'
print(f"Sharpe: {stats['monthly_sharpe']:.2f}") # 'monthly_sharpe' 不是 'sharpe_ratio'
print(f"MDD: {stats['max_drawdown']:.2%}")     # 鍵名相同

# 基準比較 (finlab >= 2.0.17)：相同 ffn 鍵名，在回測期間對市場基準進行計算 — 不需要重新計算從市場
bench = report.get_benchmark_stats()
print(f"Benchmark CAGR: {bench['cagr']:.2%} | MDD: {bench['max_drawdown']:.2%}")
```

參見 [backtesting-reference.md](backtesting-reference.md) 了解完整的 `sim()` API。

### 步驟 4.5：交付 FinLab HTML 報告 (必須)

對於用戶將審閱的每個回測，使用一個 HTML 文件 — FinLab 生成的文件：

```python
report = sim(position, resample="M", upload=False)
report.to_html("report.html")            # FinLab 生成的文件是交付物
```

傳統的交付物是 `report.to_html()` 生成的文件 — 不要手動編輯一個獨立的報告 (自定義 HTML 頁面、Plotly 摘要、儀表板、markdown 文件) 除非用戶明確要求。為了總結結果，打印一個簡短的終端總結，並指向 FinLab 報告。例外：在批量運行 (參數掃描、篩選多個變體) 中，跳過每個運行的 HTML，僅對用戶將審閱的最終策略寫入。

在運行多個策略的同一會話中選擇描述性文件名 (例如 `momentum_top10.html`，`value_lowpb.html`)，以便用戶可以無需覆蓋即可比較。寫入後，告訴用戶路徑以便他們打開。僅在非 GUI 終端作為補充使用 `report.to_terminal()`；它不取代 HTML。

參見 [backtesting-reference.md](backtesting-reference.md) 中 "`report.to_html()` — 傳統交付物" 部分的詳細信息，了解文件包含什麼內容。

### 步驟 5：執行訂單 (選擇性)

將回測結果轉換為實際交易：

```python
from finlab.online.order_executor import Position, OrderExecutor
from finlab.online.sinopac_account import SinopacAccount

# 1. 將報告轉換為位置
position = Position.from_report(report, fund=1000000)

# 2. 連接經紀賬戶
acc = SinopacAccount()

# 3. 創建執行器並預覽訂單
executor = OrderExecutor(position, account=acc)
executor.create_orders(view_only=True)  # 首先預覽

# 4. 執行訂單 (準備好時)
executor.create_orders()
```

參見 [trading-reference.md](trading-reference.md) 了解完整的經紀設置和 OrderExecutor API。

## 參考文件

| 文件                                                           | 内容                                    |
| -------------------------------------------------------------- | ------------------------------------------ |
| [backtesting-reference.md](backtesting-reference.md)           | `sim()` 參數、stop-loss、rebalancing       |
| [trading-reference.md](trading-reference.md)                   | 券商設定、OrderExecutor、Position          |
| [factor-examples.md](factor-examples.md)                       | 60+ 策略範例                               |
| [dataframe-reference.md](dataframe-reference.md)               | FinLabDataFrame 方法                       |
| [factor-analysis-reference.md](factor-analysis-reference.md)   | IC、Shapley、因子分析                      |
| [best-practices.md](best-practices.md)                         | 常見錯誤、lookahead bias                   |
| [machine-learning-reference.md](machine-learning-reference.md) | ML 特徵工程                                |
| [us-market.md](us-market.md)                                   | US market specifics: data map, quarterly alignment, defaults, universe construction |

## 新增內容 (自 v1.5.8 以來)

最近版本中新增功能的簡短指針。每個參考文件標記了確切的 API 並標記為 `(vX.Y.Z)`。

**v2.0.15** (2026-07-18)
- `df.sector(by=...)`: 行業訪問器現在接受自定義分類 — 字典 / `pd.Series` (stock_id → group) 或變化的 `pd.DataFrame`；未上市股票被排除。與所有 `sector.*` 方法一起工作 — 參見 [dataframe-reference.md](dataframe-reference.md)
- `df.sector.map(mapping)`: 將行業級標量 (例如行業權重) 广播到完整 DataFrame 形狀以進行因子組合 — 參見 [dataframe-reference.md](dataframe-reference.md)
- `df.weight.by_group(weights, by, default)`: 在行業/組別之間分配資本 — 使持有量正常化，以便每個組別的總和等於其分額；未分配的資產保持現金 — 參見 [dataframe-reference.md](dataframe-reference.md)

**v2.0.12** (2026-06-01)
- `sim()` / `hold_until()`: `trail_stop_activation` — 要求在 `trail_stop` 激活之前達到最小未實現收益。參見 [backtesting-reference.md](backtesting-reference.md) 和 [dataframe-reference.md](dataframe-reference.md)
- `report.to_html(path, title=...)`: 獨立 HTML 現在設置瀏覽器標籤標題 + FinLab 結構圖標；傳遞 `title` 以區分多個策略報告文件夾 — 參見 [backtesting-reference.md](backtesting-reference.md)
- 控制面板設置模態：語言 / 亮/暗主題 / 蜡燭顏色方案 (默認、東方紅、西方綠) 合併到一個面板

**v2.0.9** (2026-05-27)
- `data.set_market("rotc")`: 興櫃現在一個一等市場代碼；`price:收盤價` / `monthly_revenue:*` / 等. 解析到 `rotc_` 目錄，`sim()` 使用 `ROTCMarket` 默認值
- `data.search(market="rotc")`: 受限於興業市場目錄

**v2.0.1** (2026-04-26)
- `python -m finlab cloud` *(CLI)*: 將策略部署到 `finlab-auto-update` Cloud Functions 运行时，每天亞洲/台灣時間安排 — `deploy`，`get`，`list`，`run`，`logs`，`schedule set/delete`，`delete`，`status`。參見 [trading-reference.md](trading-reference.md#cloud-strategy-deployment--python--m-finlab-cloud-v201)
- `sim()` 在完整市場月度策略上的峰值 RSS ~800 MB 降低 (從 ~2.0–2.2 GiB → ~1.29 GiB)；啟用了 s 級雲工作器，它們之前 OOM'd

**v2.0.0** (2026-04-04) — 大型發布
- `finlab.exceptions`: 結構化錯誤層級 (`FinlabError`, `DataError`, `BacktestError`, ...) — 參見 [backtesting-reference.md](backtesting-reference.md)
- `data.get(lazy=True)` / `data.gets(..., lazy=True)`: 批量獲取 + 延遲計算；`data.override()` / `DataContext` 用於範圍內的全局狀態
- `df.cs` / `df.sector` / `df.weight` 访问器；`rolling().std/var/skew/kurt/median` — 參見 [dataframe-reference.md](dataframe-reference.md)
- `PositionStreamMixin` 用於實時位置流 — 參見 [trading-reference.md](trading-reference.md)
- `from finlab import FinlabDataFrame` 顶层导出
- `backtest.sim()` 重构為 5 个可測試的階段；從 `optimize.combinations` 中移除了 `eval()`

**v1.5.13** (2026-03-22)
- `universe(index=...)` / `us_universe(index=...)`: 按美國股票過濾 S&P 500 / NASDAQ 100
- 新市場代碼 `TW_CB` (台灣可轉債券)

**v1.5.11** (2026-03-11)
- `data.get_role()` / `data.is_vip()`: 查詢用戶配額層級
- 報告遷移到傳統 Firestore 流程 (用戶透明)
- `v1.5.9`
- `finlab.schemas`: 虛擬的 `PositionEntry`，`OrderEntry`，`PortfolioData` 合約
- `OrderExecutor.generate_orders(as_entries, quantity_type)` 和 `generate_order_entries()`
- `PortfolioSyncManager.get_data_typed()` / `set_data_typed()`
- `data.get()` 80% 配额使用警告
- `sim()` 使用市場特定默認 `fee_ratio` / `tax_ratio` (不再硬編碼 TW 值)

**v1.5.8** (基線)
- `verify_strategy()`: 自動化前瞻性偏差檢測器
- `report.to_terminal()`: ASCII 報告，用於非 Jupyter 運行
- 總體策略執行 3.4x 更快

## 財務數據對齊

從來不使用 `reindex()` 或 `reindex_like()`，包括在最終位置上使用。FinLabDataFrame 在算術、比較和布爾操作期間自動重塑日期和股票列：`sales_to_price = eps_sales / close`。不要手動對齊或繞過此行為使用 pandas/NumPy。在組合每日數據之前計算季度變動和滾動窗口；使用 `sim(position, resample=...)` 設置再平衡計劃。僅使用 `index_str_to_date()` 進行檢查日期。出錯時，檢查類型和參考 [dataframe-reference.md](dataframe-reference.md)。

## 防止前瞻性偏差

**關鍵：** 避免使用未來數據來做出過去的決策：

```python
# ✅ 好的：使用 shift(1) 獲取上一個值
prev_close = close.shift(1)

# ❌ 不好的：不要使用 iloc[-2] (可能導致前瞻性)
# prev_close = close.iloc[-2]  # 錯誤

# ✅ 好的：即使有像 "2025Q1" 這樣的字符串，也保留索引
# FinLabDataFrame 運算符自動對齊日期和股票列

# ❌ 不好的：不要手動分配給 df.index
# df.index = new_index  # 禁止
```

參見 [best-practices.md](best-practices.md) 了解更多反模式。

## 性能默認值

**默認傳遞 `lazy=True`；僅在調試時才使用急切 pandas。** `data.get(..., lazy=True)` 和 `data.gets(..., lazy=True)` *(v2.0.0)* 返回緩存 FinlabDataFrames，它們延遲計算計算圖，直到終端調用時才實現它 — 鏈式操作避免冗餘遍歷 (單 CPU)。省略 `lazy=True` 當您需要打印/檢查交互式中間值時。

```python
# ✅ 默認：直接獲取緩存
price, volume, pe = data.gets(
    'price:收盤價', 'price:成交股數', 'price_earning_ratio:本益比',
    lazy=True,
)

# ✅ 調試：急切 pandas 用於行級檢查
close = data.get('price:收盤價')
print(close.loc['2024-01-15', '2330'])
```

## 反饋

請用戶開啟 GitHub 上的問題：https://github.com/koreal6803/finlab-ai/issues

## 注意事項

- 一些數據列使用中文名稱 — 這是預期的，在 `data.get()` 調用中使用它們
- 數據頻率各不相同：每日 (價格), 每月 (收入), 每季 (財務報表)
- `sim()` 默認 `upload=None`: 本地運行不上傳；FinLab Studio / 云計劃 (它們設置 `FINLAB_STRATEGY_NAME` / `FINLAB_FORCED_STRATEGY_NAME`) 將上傳。傳遞 `upload=False` 以確保不會上傳，傳遞 `upload=True` 以強制上傳
