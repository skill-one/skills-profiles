# AlphaEar 新闻技能

## 概述

获取实时热点新闻，生成统一趋势报告，并检索 Polymarket 预测数据。

## 功能

### 1. 获取热点新闻与趋势

通过 `NewsNowTools` 使用 `scripts/news_tools.py`。

-   **获取新闻**：`fetch_hot_news(source_id, count)`
    -   参考 [sources.md](references/sources.md) 获取有效的 `source_id`（例如，`cls`、`weibo`）。
-   **统一报告**：`get_unified_trends(sources)`
    -   从多个来源聚合顶级新闻。

### 2. 获取预测市场

通过 `PolymarketTools` 使用 `scripts/news_tools.py`。

-   **市场概览**：`get_market_summary(limit)`
    -   返回活跃预测市场的格式化报告。

## 依赖项

-   `requests`、`loguru`
-   `scripts/database_manager.py`（本地数据库）
