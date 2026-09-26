# AlphaEar 股票技能

## 概述

搜索 A 股/港股/美股代码，获取历史价格数据（OHLCV）。

## 功能

### 1. 股票搜索与数据

通过 `StockTools` 使用 `scripts/stock_tools.py`。

-   **搜索**：`search_ticker(query)`
    -   按代码或名称模糊搜索（例如，"茅台"，"600519"）。
    -   返回：`{code, name}` 列表。
-   **获取价格**：`get_stock_price(ticker, start_date, end_date)`
    -   返回包含 OHLCV 数据的 DataFrame。
    -   日期格式："YYYY-MM-DD"。
-   **获取基本面**：`get_stock_fundamentals(ticker)`
    -   返回包含行业、板块、市值、市盈率及简介的字典。
    -   支持 A 股/港股/美股。

## 依赖

-   `pandas`, `requests`, `akshare`, `yfinance`
-   `scripts/database_manager.py`（股票表）

## 注意事项

-   **代理**：对于通过 `yfinance` 获取的美股数据，如果您的网络无法直接访问雅虎财经，可能需要设置环境变量：
    ```bash
    export HTTP_PROXY="http://<代理IP>:<端口>"
    export HTTPS_PROXY="http://<代理IP>:<端口>"
    ```
-   **A 股/港股**：数据主要通过 `akshare`（东方财富）获取，在中国通常需要直接连接。该工具会自动检测代理问题并尝试直接连接这些市场。
