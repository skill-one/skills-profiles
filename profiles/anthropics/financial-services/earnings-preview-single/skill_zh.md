# 单公司盈利预览

生成一份简洁、专业的股票研究报告，针对单一公司。输出是一个自包含的HTML文件，目标打印4-5页。报告内容密集，包含大量图表和数据，叙述紧凑，直截了当。

**数据来源（零例外）：** 唯一允许的数据来源是 **Kensho Grounding MCP** (`search`) 和 **S&P Global MCP** (`kfinance`)。绝对不允许使用任何其他工具、数据来源或任何形式的网络访问。具体要求如下：
- 不要使用 `WebSearch`、`WebFetch`、`web_search`、`brave_search`、`google_search` 或任何通用的网络/互联网搜索工具——即使Kensho速度慢、没有返回结果或暂时不可用。
- 不要使用任何浏览器、URL获取或网络抓取工具。
- 如果Kensho Grounding对某个查询没有返回结果，请重新表述查询或报告中标明“数据不可用”。**绝对不能以网络搜索作为替代方案。**
- 报告中的每一条信息都必须可追溯到 `kfinance` MCP函数调用或Kensho `search` 调用。如果无法追溯到这两者之一，则不得出现在报告中。

**关键规则：** 你必须在撰写报告的任何部分之前完成所有研究和数据收集（阶段1-5）。

**中间文件规则：** MCP工具调用产生的所有原始数据必须在每次工具调用返回后立即写入 `/tmp/earnings-preview/` 目录——在调用下一个工具之前。这可以防止数据因上下文窗口压缩而丢失。不要只在内存中保留数据。在阶段1开始时，运行 `mkdir -p /tmp/earnings-preview` 创建该目录。**在生成HTML报告（阶段7）之前，你必须使用 `cat` 命令将所有中间文件重新读入上下文。** 这些文件——而不是你之前的对话记忆——是报告中每个数字、引文和来源URL的唯一来源。如果你跳过读取文件，报告将包含错误。

**财政季度规则：** 绝对不要根据日历报告日期推断财政季度。许多公司有非标准的财政年度（例如，沃尔玛的财政年度于1月31日结束，因此2026年2月的报告涵盖的是2026财年第四季度，而不是2025年第四季度或2026年第一季度）。始终使用 `get_next_earnings_from_identifiers` 或 `get_earnings_from_identifiers` 返回的盈利会议名称中精确的财政季度和财政年度（例如，“沃尔玛2026财年第四季度盈利会议”意味着季度是2026财年第四季度）。在报告标题、标题、表格和所有引用中逐字使用。如果会议名称不明确，请参考 `get_financial_line_item_from_identifiers` 期间标签。

**长度规则：** 报告必须简洁。打印时目标长度为4-5页。不要写冗长的多段落叙述。使用简洁、有力的要点。每句话都必须有价值。如果你可以用更少的字数表达，那就这样做。

**逐字引用规则：** 当在 `<blockquote>` 标签中引用管理层发言时，文本必须**完全复制**自会议记录——逐字，包括填充词和句子片段。不要释义，不要重新排列、合并不同部分的句子，也不要“清理”引文。如果你在会议记录中找不到确切的短语，请不要将其作为直接引文。相反，用你自己的叙述语气来释义，不要使用 `<blockquote>` 格式（例如，“管理层指出数据中心需求仍然很大”）。每个 `<blockquote>` 必须是逐字、复制粘贴的摘录，可以与会议记录进行验证。

**计算完整性规则：** 对于任何多步计算（从年度指导中隐含的季度数据、LTM市盈率、同比增长率、部门同比变化），必须明确写出每一步，并在使用它们之前验证中间结果。如果你声明 A + B + C = X，则在使用 X 进行后续公式之前，必须验证 X 是否在算术上正确。如果附录显示总和与其声明的组成部分不相等，则报告是错误的。如有疑问，请从原始数据重新计算，而不是重复使用先前计算的中间值。

**比率术语规则：** 所有估值比率必须明确标明为 **LTM**（过去12个月）或 **NTM**（未来12个月）。永远不要使用“滞后”或“前瞻”一词——始终使用 LTM 或 NTM。LTM比率使用最近4个报告季度的总和。NTM比率使用 `get_consensus_estimates_from_identifiers` 提供的**未来4个季度共识平均EPS估计值的总和**——不是单个年度数字。LTM 和 NTM 市盈率都必须在竞争对手比较表中计算和显示。

**超链接规则（严格执行）：** 报告中的每一项声明——数字和非数字——都必须用 `<a href="#ref-N" class="data-ref">` 链接到相应的附录条目。**这不是可选的。报告中的每个数字必须是可点击的链接。** 这包括：收入数据、EPS、利润率、增长率、市值、市盈率、股票回报、目标价、部门收入以及任何其他财务指标。这也包括来自会议记录或 Kensho 搜索的定性声明。如果你将其声明为事实，就必须链接到来源。为每个唯一声明分配一个顺序参考ID（`ref-1`、`ref-2` 等）。超链接样式非常微妙——海军蓝颜色，没有下划线，鼠标悬停时显示点状下划线。**不要在报告正文中写任何没有用 `<a>` 标签包装的数字。** 示例：写 `<a href="#ref-1" class="data-ref">$152.3B`，绝对不要将 `$152.3B` 作为纯文本写入。

---

## 第一阶段：公司简介和设置

1. 从 `$ARGUMENTS` 中解析单个公司股票代码（去除空白）。
2. 运行 `mkdir -p /tmp/earnings-preview` 创建工作目录。
3. 调用 `get_latest()` 以建立当前报告期上下文。
4. 调用 `get_info_from_identifiers` — 记录市值、行业。
5. 调用 `get_company_summary_from_identifiers` — 记录业务描述。
6. 调用 `get_next_earnings_from_identifiers` — 记录即将到来的盈利日期和财政季度名称。

**立即写入** `/tmp/earnings-preview/company-info.txt`：
```
TICKER: [ticker]
COMPANY: [全名]
INDUSTRY: [行业]
MARKET_CAP: [值]（截至[日期]）
NEXT_EARNINGS_DATE: [日期]
NEXT_EARNINGS_QUARTER: [Q# FY#### 恰好如API返回的那样]
BUSINESS_DESCRIPTION: [2-3句摘要]
```

---

## 第二阶段：盈利记录分析（强制执行——必须在撰写报告之前完成）

1. 调用 `get_latest_earnings_from_identifiers` 获取最新的已完成盈利会议 `key_dev_id`。
2. 调用 `get_transcript_from_key_dev_id` 获取该记录。
3. **立即写入** `/tmp/earnings-preview/transcript-extracts.txt`，包含以下部分。在仍然具有会议记录上下文时写入此文件——不要等待：

```
TRANSCRIPT_SOURCE: [会议名称，例如，“2025年第三季度盈利会议”]
KEY_DEV_ID: [key_dev_id]
CALL_DATE: [日期]
FISCAL_QUARTER: [Q# FY####]

=== 逐字引言（精确复制——不要释义） ===
QUOTE_1: "[从会议记录中精确文本]"
SPEAKER_1: [姓名], [职务]
CONTEXT_1: [一句话说明出处——准备好的发言或问答]

QUOTE_2: "[从会议记录中精确文本]"
SPEAKER_2: [姓名], [职务]
CONTEXT_2: [上下文]

QUOTE_3: "[从会议记录中精确文本]"
SPEAKER_3: [姓名], [职务]
CONTEXT_3: [上下文]

QUOTE_4: "[从会议记录中精确文本]"
SPEAKER_4: [姓名], [职务]
CONTEXT_4: [上下文]

=== 指导（仅限定量） ===
- [指标]: [范围或点估计，如管理层所述]
- [指标]: [范围或点估计]

=== 关键驱动因素 ===
- [驱动因素1，附带支持数据点]
- [驱动因素2，附带支持数据点]
- [驱动因素3，附带支持数据点]

=== 风险和不利因素 ===
- [风险1，如有可用数据请量化]
- [风险2]

=== 分析师问答主题 ===
- [主题1: 分析师推动的内容]
- [主题2]
- [主题3]

=== 综合分析：下一季度需要关注的主题 ===
- [主题1]
- [主题2]
- [主题3]
```

---

## 第三阶段：竞争对手分析

1. 调用 `get_competitors_from_identifiers`，`competitor_source="all"`。
2. 选择**最相关的5-7家公共竞争对手**。
3. 对于公司和所有选定的竞争对手，收集：
   - `get_prices_from_identifiers` with `periodicity="day"`, last 12 months
   - `get_financial_line_item_from_identifiers` for `diluted_eps`, `period_type="quarterly"`, `num_periods=8`
   - `get_capitalization_from_identifiers` with `capitalization="market_cap"` (latest)
   - `get_consensus_estimates_from_identifiers` with `period_type="quarterly"`, `num_periods_forward=4` — 这返回未来4个季度的共识平均EPS估计值，这些估计值相加计算NTM EPS

**每次工具调用返回后，立即将原始数据追加到相应的中间文件：**

**写入** `/tmp/earnings-preview/prices.csv` — 每行一个（股票代码, 日期, 收盘价）。包括 `source` 列，使用精确的 MCP 函数调用。首先写入主体公司的价格，然后按顺序写入每个竞争对手的价格：
```
ticker,date,close,source
D,2025-02-19,55.67,get_prices_from_identifiers(identifier='D',periodicity='day')
D,2025-02-20,55.82,get_prices_from_identifiers(identifier='D',periodicity='day')
...
DUK,2025-02-19,111.79,get_prices_from_identifiers(identifier='DUK',periodicity='day')
...
```
注意：`source` 值对于来自单个调用的所有行是相同的——在每个行上写入它，以便始终可用。

**写入** `/tmp/earnings-preview/peer-eps.csv` — 每行一个（股票代码, 期间, EPS）。立即在每次 `diluted_eps` 调用后写入：
```
ticker,period,diluted_eps,source
D,Q4 2024,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
DUK,Q4 2024,1.52,get_financial_line_item_from_identifiers(identifier='DUK',line_item='diluted_eps',period_type='quarterly')
...
```

**写入** `/tmp/earnings-preview/peer-market-caps.csv` — 每行一个股票代码。立即在每次 `market_cap` 调用后写入：
```
ticker,market_cap,retrieval_date,source
D,55900000000,2026-02-19,get_capitalization_from_identifiers(identifier='D',capitalization='market_cap')
DUK,98300000000,2026-02-19,get_capitalization_from_identifiers(identifier='DUK',capitalization='market_cap')
...
```

**写入** `/tmp/earnings-preview/consensus-eps.csv` — 每行一个（股票代码, 期间, 共识平均EPS）。立即在每次 `get_consensus_estimates_from_identifiers` 调用后写入：
```
ticker,period,consensus_mean_eps,num_estimates,source
D,Q4 2025,0.88,12,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q1 2026,0.72,10,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q2 2026,0.91,9,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q3 2026,1.05,8,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
DUK,Q4 2025,1.48,14,get_consensus_estimates_from_identifiers(identifier='DUK',period_type='quarterly',num_periods_forward=4)
...
```

4. **不要计算市盈率或回报率。** 原始数据现在已写入磁盘。计算将在阶段6（验证）中进行，从这些文件中读取。

**日期一致性规则（股票回报）：** 在计算比较股票回报（YTD %, 1-yr %, 30d %, 90d %）时，所有股票代码必须使用**完全相同的开始和结束日期**。在将所有价格数据写入 `prices.csv` 后，识别所有股票代码数据中出现的第一个交易日期，并使用该日期作为共同的基期。不要为不同股票使用不同的基期（例如，主体公司的数据从2月19日开始，而竞争对手的数据从2月28日开始）。如果一个股票的数据开始晚于其他股票，请使用第一个重叠日期进行所有计算。在附录中声明共同的基期，以便每个回报计算。

**市盈率货币规则（LTM 市盈率）：** 在计算每个公司的 LTM 市盈率时，使用该公司的**最近4个报告季度**，而不是应用于所有公司的固定日历窗口。如果一个竞争对手已经报告了2025年第四季度，而主体公司只有2025年第三季度报告，则竞争对手的 LTM EPS应包括2025年第四季度。检查每个公司的最新报告期间，并针对每个公司使用最近的4个期间。在附录中注明用于每个市盈率计算的4个季度。

**市值日期戳：** 报告市值时，使用 `peer-market-caps.csv` 中的 `retrieval_date`。如果它与报告日期不同，请在附录中注明。
