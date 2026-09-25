# OKX 新闻与市场情绪

OKX 的加密货币新闻聚合、币种情绪分析以及宏观经济日历。所有命令均为**只读**，并需要**API 凭证**（OAuth2.1）。

## 功能

| 用户意图 | 命令 |
|-------------|---------|
| 最新/重要新闻 | `okx news latest` |
| 币种特定新闻 | `okx news by-coin` |
| 关键词新闻搜索 | `okx news search` |
| 情绪过滤新闻 | `okx news by-sentiment` |
| 完整文章内容 | `okx news detail` |
| 币种情绪快照 | `okx news coin-sentiment` |
| 情绪趋势 | `okx news coin-trend` |
| 情绪排名 | `okx news sentiment-rank` |
| 新闻来源列表 | `okx news platforms` |
| 经济日历查询 | `okx news economic-calendar` |
| 有效日历区域 | `okx news list-regions` |

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 在 `~/.okx/config.toml` 中配置凭证
3. 验证设置：
   ```bash
   okx news latest --limit 3
   ```

OKX 新闻不支持演示模式。始终使用 `--profile live` 静默地 — 除非出现错误，否则不要提及。

**关于“不可用于演示”错误的说明：** 用户的当前配置使用了演示/模拟凭证。告诉用户：“新闻模块不支持演示模式。请切换到实时配置。” 指导他们：
- 如果存在实时配置，使用 `--profile live`：`okx --profile live news latest`
- 或者创建一个：`okx config add-profile AK=<key> SK=<secret> PP=<passphrase> name=live`

所有命令支持 `--json` 用于原始 JSON 输出。

## 快速入门

```bash
# 最新新闻
okx news latest --limit 5

# 当天的重要新闻
okx news important --begin $(date -d 'today 00:00:00' +%s000 2>/dev/null || date -v0H -v0M -v0S +%s000)

# BTC 新闻
okx news by-coin --coins BTC

# 搜索 SEC ETF 新闻
okx news search --keyword "SEC ETF"

# BTC 情绪概述
okx news coin-sentiment --coins BTC

# 热门币种（当前最热门）
okx news sentiment-rank

# 即将到来的经济事件（仅今天）
okx news economic-calendar --before $(date -v0H -v0M -v0S +%s000) --after $(date -v+1d -v0H -v0M -v0S +%s000) --limit 100
```

## 意图 → 命令映射

### 浏览新闻

`latest`、`by-coin` 和 `search` 默认 `--importance low`，返回**所有**新闻（无论高低重要性）。仅在用户明确要求获取重大/突发/重要新闻时才传递 `--importance high`。专门的 `okx news important` 命令是这种情况的快捷方式。

| 用户说 | 命令 |
|-----------|---------|
| "最近加密货币发生了什么" / "让我了解最近的新闻" | `okx news latest` |
| "今天有什么重大新闻" / "当前有哪些主要新闻" | `okx news important` |
| "昨天加密货币发生了什么" | `okx news latest --begin <yesterday_0am> --end <today_0am>` |
| "最近有什么关于 BTC 的新闻" / "BTC 的情况如何" | `okx news by-coin --coins BTC` |
| "ETH 或 SOL 有什么重大更新" | `okx news by-coin --coins ETH,SOL --importance high` |

### 搜索新闻

| 用户说 | 命令 |
|-----------|---------|
| "有任何关于 SEC ETF 决定的更新" | `okx news search --keyword "SEC ETF"` |
| "最新关于稳定币监管的消息" | `okx news search --keyword "stablecoin regulation"` |
| "有任何关于比特币减半的新闻" | `okx news search --keyword "Bitcoin halving"` |

### 币种情绪分析

| 用户说 | 命令 |
|-----------|---------|
| "BTC 市场目前是看涨还是看跌" / "人们如何看待 BTC" | `okx news coin-sentiment --coins BTC` |
| "比较人们对 ETH 和 SOL 的看法" | `okx news coin-sentiment --coins ETH,SOL` |
| "BTC 情绪在过去 24 小时内如何变化" | `okx news coin-trend BTC --period 1h --points 24` |
| "显示过去一周的 BTC 情绪" | `okx news coin-trend BTC --period 24h --points 7` |
| "目前加密货币中什么最热门" / "哪些币种最受关注" | `okx news sentiment-rank` |
| "哪些币种人们最兴奋" / "最看涨的币种" | `okx news sentiment-rank --sort-by bullish` |
| "哪些币种的负面情绪最多" | `okx news sentiment-rank --sort-by bearish` |

### 经济日历

> **关键 — 总是使用 `--before` 和 `--after` 来形成时间窗口。** 仅使用 `--before` 会返回到 2028 年的事件，而 `--limit` 会剪切最远的事件 — 不是最近的。始终成对使用。
>
> 语义（反直觉）：`--before <ts>` = 比 ts 新的事件（下限），`--after <ts>` = 比 ts 旧的事件（上限，默认为现在）。

| 用户说 | 命令 |
|-----------|---------|
| "今天有什么经济数据" / "今天的经济事件" | `okx news economic-calendar --before <today_0am_ms> --after <tomorrow_0am_ms> --limit 100` |
| "这周美国有什么重要经济事件" | `okx news economic-calendar --region united_states --importance 3 --before <week_start_ms> --after <week_end_ms> --limit 100` |
| "非农什么时候出" / "NFP 何时发布" | `okx news economic-calendar --region united_states --importance 3 --before <now_ms> --after <now_plus_60d_ms> --limit 100` 然后在客户端筛选 `event` 字段以查找 "Non Farm" |
| "CPI 出来了吗" / "最新 CPI 数据" | `okx news economic-calendar --region united_states --importance 3 --limit 20` （默认 `after=now` 获取过去高重要性事件；检查 `actual` 字段） |
| "欧洲央行利率决议" / "ECB 利率决议" | `okx news economic-calendar --region euro_area --importance 3 --before <now_ms> --after <now_plus_90d_ms> --limit 100` 然后筛选 "Interest Rate Decision" |

**如何选择 `before` / `after`：**

| 意图 | 参数 | 说明 |
|--------|-----------|-------------|
| 当天的事件 | `--before <today_0am> --after <tomorrow_0am>` | 窗口 = 今天 0:00 → 明天 0:00 |
| 本周的事件 | `--before <week_start> --after <week_end>` | 窗口 = 周一 0:00 → 周日 24:00 |
| 下一 N 天 | `--before <now> --after <now_plus_Nd>` | 窗口 = 现在 → N 天后 |
| 过去的事件（默认） | 省略两者，或 `--after <upper_bound>` | 默认 `after=now`，返回最近的过去 |
| 历史窗口 | `--before <window_start> --after <window_end>` | 两个边界都明确 |

注意：
- ⚠️ **始终使用 `--before` 和 `--after`** 进行未来事件查询。`--before` 单独使用会返回到 2028 年，而 `--limit` 会剪切错误的一端。过去事件查询的唯一例外是默认 `after=now` 是正确的。
- 速率限制：每 5 秒 1 个请求（基于 IP）。不要重复调用。
- 没有关键词/事件过滤器 — 在客户端筛选响应 `event` 字段。使用**单个** API 调用，带有 `--limit 100` 和宽泛窗口，然后在本地筛选结果（不要循环调用尝试不同的关键词）。
- 当用户要求特定的重要性级别（例如 "重要的"，"high importance"）时，传递 `--importance 3` 并且仅包含重要性为 3 的事件在输出中。不要用低重要性事件填充响应。
- 当搜索特定事件（NFP、CPI、ECB 决议）时，始终添加 `--importance 3` 以减少噪音 — 这些都是高重要性事件。使用 `--limit 100` 和宽泛窗口以确保捕获目标事件。
- `actual=""` = 尚未发布；非空 = 已发布。
- 历史数据超过 3 个月需要 VIP1+。
- 不支持演示模式 — 静默使用 `--profile live`。
- `--region` 值是蛇形命名（例如 `united_states`，`euro_area`）。**无效值会静默返回空结果**（无错误）。如果您得到空结果并怀疑区域拼写错误，请运行 `okx news list-regions` 获取 210 个有效值的完整列表，然后对用户输入进行模糊匹配并重试。如果您不确定确切值，**请省略 `--region`** 并在客户端通过响应中的 `region` 字段进行筛选。

### BTC 宏观影响（跨技能）

| 用户说 | 工作流 |
|-----------|---------|
| "BTC 受哪些宏观数据影响" / "本周 BTC 的宏观影响" | → [BTC 宏观影响工作流](references/workflows.md#btc-macro-impact-analysis) |
| "本周宏观对加密货币有什么影响" / "宏观数据将如何影响加密货币" | → [BTC 宏观影响工作流](references/workflows.md#btc-macro-impact-analysis) |

这些查询需要**并行**执行经济日历 + BTC 情绪/新闻 + 市场数据。不要按顺序运行它们。

### 情绪异常检测（多币种）

| 用户说 | 工作流 |
|-----------|---------|
| "哪些币种的情绪变化最大" / "有任何情绪异常" / "哪些币种的情绪发生了变化" | → [异常检测工作流](references/workflows.md#sentiment-anomaly-detection--multi-coin-scan) |
| "过去一周有什么异动" / "突然的情绪变化" / "情绪逆转" | → [异常检测工作流](references/workflows.md#sentiment-anomaly-detection--multi-coin-scan) |
| "有没有突然看涨/看跌的" / "任何币种转为看涨/看跌" | → [异常检测工作流](references/workflows.md#sentiment-anomaly-detection--multi-coin-scan) |

这些查询需要**先广后深**的方法：首先扫描所有币种的异常，然后使用新闻相关性进行深入分析。遵循 `references/workflows.md` 中的多阶段工作流 — 不要只是挑选几个币种进行分析。

### 来源过滤新闻

使用 `--platform` 直接按新闻来源过滤。始终从 `okx news platforms` 中解析确切值 — 不要根据用户的措辞猜测平台标识符。

| 用户说 | 命令 |
|-----------|---------|
| "ChainCatcher 最近报道了什么" / "显示来自 ChainCatcher 的新闻" | `okx news latest --platform <platform_id> --limit 10` |
| "Odaily 有什么新闻" / "TechFlowPost 的新闻" | `okx news latest --platform <platform_id> --limit 10` |
| "吴说区块链最近有什么" / "来自特定出处的新闻" | `okx news latest --platform <platform_id> --limit 20` |

**重要**：当按来源过滤时，使用更大的 `--limit`（10–20）以最大化结果，因为单个来源通常比聚合源具有更少的文章。`--importance low`（默认）是正确的设置；不要缩小到 `--importance high`。

**发布频率在不同平台之间不均衡。** API 默认 `--begin` 为 72 小时前，这对于突发源来说太窄，通常会导致 0 结果。如果一个 `--platform` 过滤查询返回少于 ~5 项（或 0），**在得出该来源没有数据的结论之前，将 `--begin` 设置为 7 天前，然后 30 天前重试**。从 `okx news platforms` 中解析候选平台 ID；不要硬编码关于哪些平台活跃的假设。

## 跨技能工作流

参见 [references/workflows.md](references/workflows.md) 了解多步骤场景（市场概述、每日简报等）和完整 MCP 工具 → CLI 映射。

## 命令参考

### `okx news latest`
按时间获取最新加密货币新闻。

```bash
okx news latest [--coins BTC,ETH] [--begin <ms>] [--end <ms>]
               [--importance high|low] [--platform <source>]
               [--detail-lvl brief|summary|full] [--lang zh-CN|en-US]
               [--limit 10] [--after <cursor>] [--json]
```

`--importance` 默认为 `low`（返回所有新闻，无论高低）。传递 `--importance high` 以缩小到仅突发/重大新闻 — 或使用 `okx news important`。

---

### `okx news important`
获取重大突发新闻（由多个来源报道）。

```bash
okx news important [--coins BTC,ETH] [--begin <ms>] [--end <ms>]
                  [--detail-lvl brief|summary|full]
                  [--lang zh-CN|en-US] [--limit 10] [--json]
```

---

### `okx news by-coin`
获取特定币种新闻。

```bash
okx news by-coin --coins <BTC,ETH,...>
               [--importance high|low] [--platform <source>]
               [--begin <ms>] [--end <ms>] [--lang zh-CN|en-US]
               [--limit 10] [--json]
```

`--importance` 默认为 `low`（返回所有新闻）。仅当用户明确要求获取突发/重大新闻时才传递 `--importance high`。

---

### `okx news search`
全文关键词搜索，带可选过滤器。

```bash
okx news search --keyword <text>
               [--coins BTC,ETH] [--importance high|low]
               [--platform <source>]
               [--sentiment bullish|bearish|neutral]
               [--sort-by latest|relevant]
               [--begin <ms>] [--end <ms>] [--lang zh-CN|en-US]
               [--limit 10] [--after <cursor>] [--json]
```

`--importance` 默认为 `low`（返回所有新闻）。仅当用户明确要求获取突发/重大新闻时才传递 `--importance high`。

---

### `okx news detail`
按 ID 获取完整文章内容。

```bash
okx news detail <id>                  # 从先前结果中获取新闻 ID
               [--lang zh-CN|en-US] [--json]
```

---

### `okx news by-sentiment`
按情绪浏览新闻（无需关键词）。

```bash
okx news by-sentiment --sentiment <bullish|bearish|neutral>
               [--coins BTC,ETH] [--importance high|low]
               [--sort-by latest|relevant]
               [--begin <ms>] [--end <ms>] [--lang zh-CN|en-US]
               [--limit 10] [--after <cursor>] [--json]
```

`--importance` 默认为 `low`（返回所有新闻）。仅当用户明确要求获取突发/重大新闻时才传递 `--importance high`。

---

### `okx news platforms`
列出可用新闻平台。使用返回的值与 `latest`、`by-coin` 或 `search` 命令上的 `--platform` 结合使用以按来源过滤。

```bash
okx news platforms [--json]
```

---

### `okx news coin-sentiment`
获取特定币种的当前情绪快照。

```bash
okx news coin-sentiment --coins <BTC,ETH,...>
               [--period 1h|4h|24h]  # 聚合粒度，默认 24h
               [--json]
```

返回：`symbol`，`label`（看涨/看跌/中性/混合），`bullishRatio`，`bearishRatio`，`mentionCount`。

---

### `okx news coin-trend`
获取币种的时间序列情绪趋势。注意：使用位置参数（不是 `--coins`）。

```bash
okx news coin-trend <coin>            # 位置参数，例如 BTC
               [--period 1h|4h|24h]  # 聚合粒度，默认 1h
               [--points 24]          # 趋势数据点，默认 24
               [--json]
```

`trendPoints` 指导：1h 期间 → 使用 24（过去 24 小时），4h → 使用 6，24h → 使用 7。

---

### `okx news sentiment-rank`
按社交热度或情绪方向获取币种排名。

```bash
okx news sentiment-rank [--period 1h|4h|24h]
               [--sort-by hot|bullish|bearish]  # hot=按提及次数（默认），bullish，bearish
               [--limit 10]                     # 最大 50
               [--json]
```

---

### `okx news economic-calendar`
获取宏观经济日历数据。超过 3 个月的历史数据需要 VIP1+。

```bash
okx news economic-calendar [--region <country>] [--importance <1|2|3>]
                           [--before <ms>] [--after <ms>]
                           [--limit 100] [--json]
```

速率限制：每 5 秒 1 个请求（基于 IP）。比其他新闻命令更严格。

**`before`/`after` 是相反的**：`--before <ts>` = 比 ts 新的事件（未来），`--after <ts>` = 比 ts 旧的事件（过去）。参见 [经济日历意图映射](#economic-calendar) 获取示例。

常用区域：united_states, china, euro_area, united_kingdom, japan, germany, canada, australia

重要性：1=低，2=中，3=高

---

### `okx news list-regions`
列出 `economic-calendar` 的所有有效 `--region` 值。当区域查询返回空时使用，以验证值。

```bash
okx news list-regions [--json]
```

---

## MCP 工具参考

| 工具 | 描述 |
|------|-------------|
| `news_get_latest` | 按时间排序的最新新闻。服务器默认 `importance=high`（狭窄）；传递 `importance=low` 以扩展到所有新闻。 |
| `news_get_by_coin` | 特定币种新闻 (`coins` 是逗号分隔的字符串) |
| `news_search` | 全文关键词搜索，带过滤器（可选 `sentiment` 过滤器） |
| `news_get_detail` | 按 ID 获取完整文章内容 |
| `news_get_domains` | 列出可用的新闻来源域 |
| `news_get_coin_sentiment` | 情绪快照（无 `trendPoints`）或时间序列趋势（传递 `trendPoints`） |
| `news_get_sentiment_ranking` | 按热度或情绪方向获取币种排名 |
| `news_get_economic_calendar` | 宏观经济日历数据；速率限制 1/5s |
| `news_list_calendar_regions` | 列出经济日历的 210 个有效区域值 |

## 币种符号标准化

API 仅接受标准的大写票面符号（例如 `BTC`，`ETH`，`SOL`）。用户可以通过全名、缩写、俚语或本地语言昵称来引用币种。始终在传递到任何命令之前将它们解析为正确的票面符号。如果目标币种不明确，请在查询之前要求用户确认。

## 空结果与网络搜索回退

OKX 新闻数据对于小众币种或高度特定的关键词搜索可能很稀疏。API 默认 `--begin` 窗口仅为 72 小时，这本身就解释了许多空结果。当命令返回空或结果不足时，按顺序应用以下步骤 — 不要跳转到网络搜索：

1. **如果使用了 `--platform`** — 在更改任何其他内容之前，将 `--begin` 扩展到 7 天前，然后 30 天前，再尝试。突发源常规地在默认窗口中返回 0 项，但在更宽泛的范围内可以返回几十项。
2. **如果传递了 `--importance high`** — 放弃它（默认已经是 `low` = 所有新闻）。
3. **对于任何查询**（不仅仅是 `--platform`）在怀疑狭窄时间窗口时扩展 `--begin` / `--end`。
4. **省略 `--coins`** 以获取一般新闻，如果币种特定查询未产生任何结果。
5. **使用网络搜索作为补充** — 在网上搜索 `"<主题> news site:coindesk.com OR site:cointelegraph.com OR site:theblock.co"` 以收集更多背景信息，然后将 OKX 结果与任何网络搜索结果合并为统一的简报。
6. **保持透明** — 告知用户哪些结果来自 OKX API vs. 网络搜索，以便他们可以判断来源的可信度。

这种回退对于以下情况特别有价值：
- 覆盖率低的币种（例如，新上市的代币）
- 高度特定的关键词搜索没有匹配项
- `--platform` 查询，其中选择的源发布频率不均衡

## 已知限制

### 来源覆盖

平台发布频率不同，并且会随时间变化。有些来源每天发布许多文章；其他来源在一段时间内发布一次，然后出现静默期。在默认 72 小时窗口中返回很少或零文章的来源**不是证据表明它不活跃** — 它可能只是最近没有发布，或者其最近的帖子可能已被去重。

在得出 `--platform` 过滤查询没有数据的结论之前：

1. 将 `--begin` 扩展到 7 天前，然后 30 天前，并重试。
2. 如果在 30 天窗口后仍然为空，请向用户报告该源没有最近的文章，并建议要么移除 `--platform`（回退到聚合源），要么进行网络搜索。

不要硬编码关于哪些平台活跃的假设 — 从 `okx news platforms` 中解析候选者，让数据说话。

### 历史搜索限制

`okx news search` 和 `okx news by-coin` 主要索引**最近的文章**（通常为今天和最近几天）。使用 `--begin`/`--end` 搜索日期超过 ~7 天可能会返回空结果，即使在该时间点存在文章。这是一个 API 索引限制，不是数据缺失。

对于历史分析，`okx news coin-trend`（情绪趋势数据）比文章搜索更可靠 — 它保留了更长时间段的时间序列数据。
