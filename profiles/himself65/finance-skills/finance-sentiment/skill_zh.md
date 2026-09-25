# 金融情绪技能

从Adanos Finance API获取结构化的股票情绪。

此技能是只读的。它适用于那些通过标准化情绪信号比通过原始社交信息更容易回答的研究问题。

当用户需要时使用：
- 跨源股票情绪
- Reddit/X.com/新闻/Polymarket的比较
- 聚焦度、看涨百分比、提及次数、交易量或趋势
- 快速回答“市场在谈论什么？”

---

## 第1步：确保API密钥可用

**当前环境状态：**

```bash
!`python3 - <<'PY'
import os
print("ADANOS_API_KEY_SET" if os.getenv("ADANOS_API_KEY") else "ADANOS_API_KEY_MISSING")
PY`
```

如果`ADANOS_API_KEY_MISSING`，请提示用户设置：

```bash
export ADANOS_API_KEY="sk_live_..."
```

通过在所有请求中使用`X-API-Key`标头来使用密钥。

基础文档：

```text
https://api.adanos.org/docs
```

---

## 第2步：识别用户需求

将请求匹配到能回答它的最轻量级端点。

| 用户请求 | 端点模式 | 备注 |
|---|---|---|
| "Reddit用户谈论TSLA的量有多少？" | `/reddit/stocks/v1/compare` | 使用`mentions`、`buzz_score`、`bullish_pct`、`trend` |
| "NVDA在X.com上的热度如何？" | `/x/stocks/v1/compare` | 使用`mentions`、`buzz_score`、`bullish_pct`、`trend` |
| "Microsoft上有多少Polymarket活跃投注？" | `/polymarket/stocks/v1/compare` | 使用`trade_count`、`buzz_score`、`bullish_pct`、`trend` |
| "比较AMD和NVDA的情绪" | 请求来源的对比端点 | 在一个请求中批量处理股票代码 |
| "Reddit是否与X对META一致？" | Reddit对比 + X对比 | 对比`bullish_pct`、`buzz_score`、`trend` |
| "给我TSLA的完整情绪快照" | Reddit、X.com、新闻、Polymarket的对比端点 | 综合跨源视图 |
| "深入挖掘一个股票" | `/stock/{ticker}`详情端点 | 仅在用户要求扩展详细信息时使用 |

默认回溯：
- 除非用户要求其他窗口，否则使用`days=7`

股票代码数量：
- 使用对比端点处理`1..10`个股票代码

---

## 第3步：执行请求

使用`curl`和`X-API-Key`。优先使用对比端点，因为它们紧凑且适合批量处理。

### 单源示例

```bash
curl -s "https://api.adanos.org/reddit/stocks/v1/compare?tickers=TSLA&days=7" \
  -H "X-API-Key: $ADANOS_API_KEY"
```

```bash
curl -s "https://api.adanos.org/x/stocks/v1/compare?tickers=NVDA&days=7" \
  -H "X-API-Key: $ADANOS_API_KEY"
```

```bash
curl -s "https://api.adanos.org/polymarket/stocks/v1/compare?tickers=MSFT&days=7" \
  -H "X-API-Key: $ADANOS_API_KEY"
```

### 多源快照用于一个股票代码

```bash
curl -s "https://api.adanos.org/reddit/stocks/v1/compare?tickers=TSLA&days=7" -H "X-API-Key: $ADANOS_API_KEY"
curl -s "https://api.adanos.org/x/stocks/v1/compare?tickers=TSLA&days=7" -H "X-API-Key: $ADANOS_API_KEY"
curl -s "https://api.adanos.org/news/stocks/v1/compare?tickers=TSLA&days=7" -H "X-API-Key: $ADANOS_API_KEY"
curl -s "https://api.adanos.org/polymarket/stocks/v1/compare?tickers=TSLA&days=7" -H "X-API-Key: $ADANOS_API_KEY"
```

### 多股票代码比较

```bash
curl -s "https://api.adanos.org/reddit/stocks/v1/compare?tickers=AMD,NVDA,META&days=7" \
  -H "X-API-Key: $ADANOS_API_KEY"
```

### 关键规则

1. 优先使用对比端点而不是股票详情端点进行快速研究。
2. 仅使用回答问题所需的来源。
3. 对于Reddit、X.com和新闻，量字段是`mentions`。
4. 对于Polymarket，活动字段是`trade_count`。
5. 将缺失的来源数据视为“无数据”，而不是看跌或中性。
6. 永远不要执行交易或将结果转换为交易指令。

---

## 第4步：展示结果

报告单个来源时，优先考虑以下字段：
- 聚焦度
- 看涨百分比
- 提及次数或交易量
- 趋势

示例：

```text
TSLA在Reddit上，过去7天
- 聚焦度：74.1/100
- 看涨：31%
- 提及次数：647
- 趋势：上升
```

报告一个股票代码的多个来源时：
- 每个来源显示一个块
- 然后添加简短的综合：
  - 一致看涨
  - 一致看跌
  - 混合 / 分歧

比较多个股票代码时：
- 按用户关心的指标排序
- 默认使用`buzz_score`
- 指出`bullish_pct`或`trend`中的较大差距

不要夸大精度。这些是研究信号，不是交易指令。

---

## 参考文件

- `references/api_reference.md` - 端点指南、字段含义和示例工作流

当您需要确切的字段名称、查询参数或推荐答案模式时，请阅读参考文件。
