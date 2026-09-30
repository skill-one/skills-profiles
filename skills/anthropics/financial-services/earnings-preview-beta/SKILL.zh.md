---
name: earnings-preview-single
description: 生成一份针对单一公司的简洁版4-5页股票研究盈利预览。分析最新盈利记录、竞争对手格局、估值以及近期新闻，以生成一份专业的HTML报告。
---

# 单公司盈利预告

生成一份简洁、专业的股票研究报告盈利预告，针对单一公司。输出结果是一个自包含的HTML文件，目标打印页数为4-5页。报告内容密集包含图表和数据，叙述紧凑，直截了当。

**数据来源（零例外）：** 唯一允许的数据来源是 **Kensho Grounding MCP** (`search`) 和 **S&P Global MCP** (`kfinance`)。绝对不允许使用任何其他工具、数据来源或任何形式的网络访问。具体要求如下：
- 不要使用 `WebSearch`、`WebFetch`、`web_search`、`brave_search`、`google_search` 或任何通用的网络/互联网搜索工具——即使Kensho响应缓慢、无结果或暂时不可用。
- 不要使用任何浏览器、URL获取或网络抓取工具。
- 如果Kensho Grounding对查询无结果，尝试重新表述查询或报告中注明“数据不可用”。**绝对不能以网络搜索作为替代方案。**
- 报告中的每一条信息都必须可追溯到 `kfinance` MCP函数调用或Kensho `search` 调用。如果无法追溯到这两者之一，则不能出现在报告中。

**关键规则：** 你必须在撰写报告的任何部分之前完成所有研究和数据收集（阶段1-5）。

**中间文件规则：** 所有来自MCP工具调用的原始数据必须在每次工具调用返回后立即写入 `/tmp/earnings-preview/` 目录下的文件——在执行下一个调用之前。这可以防止数据因上下文窗口压缩而丢失。不要只在内存中保留数据。在阶段1开始时，运行 `mkdir -p /tmp/earnings-preview` 创建该目录。**在生成HTML报告（阶段7）之前，你必须使用 `cat` 命令将所有中间文件重新读入上下文。文件——而不是你对之前对话的记忆——是报告中每个数字、引言和来源URL的唯一真实来源。如果你跳过读取文件，报告将包含错误。**

**财政季度规则：** 绝对不要从日历报告日期推断财政季度。许多公司有非标准的财政年度（例如，沃尔玛的财政年度于1月31日结束，因此2026年2月的报告涵盖的是Q4 FY2026，而不是Q4 2025或Q1 2026）。始终使用盈利电话名称中返回的财政季度和财政年度（例如，“沃尔玛Q4 FY2026盈利电话”意味着季度是Q4 FY2026）。在报告标题、标题、表格和所有引用中逐字使用该名称。如果电话名称不明确，请交叉参考 `get_financial_line_item_from_identifiers` 期间标签。

**长度规则：** 报告必须简洁。打印时目标页数为4-5页。不要写冗长的多段落叙述。使用紧凑、有力的要点。每个句子都必须有其存在的价值。如果你能用更少的字数表达，那就这样做。

**逐字引用规则：** 当在 `<blockquote>` 标签中引用管理层时，文本必须**完全**从速记稿中复制——逐字，包括填充词和句子片段。不要释义、重新排列、组合不同部分的速记稿，或“清理”引言。如果你在速记稿中找不到确切的短语，不要将其作为直接引言。相反，用你自己的叙述语气释义，不要使用 `<blockquote>` 格式（例如，“管理层指出数据中心需求仍然强劲”）。每个 `<blockquote>` 必须是逐字、复制粘贴的摘录，可以与速记稿核对。

**计算完整性规则：** 对于任何多步计算（从年度指导中得出的季度数据、LTM市盈率、同比增长率、部门同比变化），必须明确写出每一步，并在使用它们之前验证中间结果。如果你声明 A + B + C = X，必须在使用X在后续公式之前验证X在算术上是正确的。如果附录中显示的求和与其声明的组成部分不相等，则报告是错误的。如有疑问，请从原始数据重新计算，而不是重复使用先前计算的中间值。

**比率术语规则：** 所有估值比率必须明确标明为 **LTM**（过去12个月）或 **NTM**（未来12个月）。永远不要使用“滞后”或“前瞻”——始终使用LTM或NTM。LTM比率使用最近4个报告季度的总和。NTM比率使用 `get_consensus_estimates_from_identifiers` 中**未来4个季度共识平均EPS估计值的总和**——不是单个年度数字。LTM和NTM市盈率都必须在竞争对手比较表中计算和显示。

**超链接规则（严格执行）：** 报告中的每个声明——数字和非数字——都必须用 `<a href="#ref-N" class="data-ref">` 链接到相应的附录条目。**这不是可选的。报告中的每个数字都必须是可点击的链接。** 这包括：收入数据、EPS、利润率、增长率、市值、市盈率、股票回报、目标价、部门收入以及任何其他财务指标。这也包括来自速记稿或Kensho搜索的定性声明。如果你将其陈述为事实，就必须链接到来源。为每个唯一声明分配一个顺序参考ID（`ref-1`、`ref-2` 等）。超链接样式很微妙——海军蓝颜色，无下划线，悬停时出现点状下划线。**不要在报告正文中以纯文本形式写任何数字。** 示例：写 `<a href="#ref-1" class="data-ref">$152.3B</a>`，绝对不要写 `$152.3B` 作为纯文本。

---

## 阶段1：公司简介与设置

1. 从 `$ARGUMENTS` 中解析单个公司股票代码（去除空白）。
2. 运行 `mkdir -p /tmp/earnings-preview` 创建工作目录。
3. 调用 `get_latest()` 以建立当前报告期上下文。
4. 调用 `get_info_from_identifiers` — 记录市值、行业。
5. 调用 `get_company_summary_from_identifiers` — 记录业务描述。
6. 调用 `get_next_earnings_from_identifiers` — 记录即将到来的盈利日期和财政季度名称。

**立即写入** `/tmp/earnings-preview/company-info.txt`：
```
TICKER: [股票代码]
COMPANY: [公司全名]
INDUSTRY: [行业]
MARKET_CAP: [值]（截至[日期]）
NEXT_EARNINGS_DATE: [日期]
NEXT_EARNINGS_QUARTER: [Q# FY#### 恰如API返回的]
BUSINESS_DESCRIPTION: [2-3句摘要]
```

---

## 阶段2：盈利速记稿分析（强制执行——必须在撰写前完成）

1. 调用 `get_latest_earnings_from_identifiers` 获取最近完成的盈利电话 `key_dev_id`。
2. 调用 `get_transcript_from_key_dev_id` 获取该速记稿。
3. **立即写入** `/tmp/earnings-preview/transcript-extracts.txt`，包含以下部分。在您仍然拥有速记稿在上下文中的同时写入此文件——不要等待：

```
TRANSCRIPT_SOURCE: [电话名称，例如，“Q3 2025 盈利电话"]
KEY_DEV_ID: [key_dev_id]
CALL_DATE: [日期]
FISCAL_QUARTER: [Q# FY####]

=== 逐字引言（逐字复制粘贴——不要释义） ===
QUOTE_1: "[从速记稿中确切的文本]"
SPEAKER_1: [姓名]，[职务]
CONTEXT_1: [一句话说明出处——准备好的发言或问答]

QUOTE_2: "[从速记稿中确切的文本]"
SPEAKER_2: [姓名]，[职务]
CONTEXT_2: [上下文]

QUOTE_3: "[从速记稿中确切的文本]"
SPEAKER_3: [姓名]，[职务]
CONTEXT_3: [上下文]

QUOTE_4: "[从速记稿中确切的文本]"
SPEAKER_4: [姓名]，[职务]
CONTEXT_4: [上下文]

=== 指导（仅定量） ===
- [指标]: [范围或点估计值，如管理层所述]
- [指标]: [范围或点估计值]

=== 关键驱动因素 ===
- [驱动因素1，附带支持数据点]
- [驱动因素2，附带支持数据点]
- [驱动因素3，附带支持数据点]

=== 不利因素与风险 ===
- [风险1，如有可用，量化]
- [风险2]

=== 分析师问答主题 ===
- [主题1：分析师推动的内容]
- [主题2]
- [主题3]

=== 综合：下一季度需关注的主题 ===
- [主题1]
- [主题2]
- [主题3]
```

---

## 阶段3：竞争对手分析

1. 调用 `get_competitors_from_identifiers`，设置 `competitor_source="all"`。
2. 选择**前5-7个最相关的公共竞争对手**。
3. 对于公司和所有选定的竞争对手，收集：
   - 调用 `get_prices_from_identifiers`，设置 `periodicity="day"`，过去12个月
   - 调用 `get_financial_line_item_from_identifiers`，`diluted_eps`，`period_type="quarterly"`，`num_periods=8`
   - 调用 `get_capitalization_from_identifiers`，设置 `capitalization="market_cap"`（最新）
   - 调用 `get_consensus_estimates_from_identifiers`，设置 `period_type="quarterly"`，`num_periods_forward=4` — 这返回未来4个季度的共识平均EPS估计值，这些估计值将被求和以计算NTM EPS

**在每次工具调用返回后，立即将原始数据追加到相应的中间文件：**

**写入** `/tmp/earnings-preview/prices.csv` — 每行一个（股票代码，日期，收盘价）。包括 `source` 列，使用MCP函数调用的确切值。首先写入主体公司的价格，然后按顺序写入每个竞争对手的价格：
```
ticker,date,close,source
D,2025-02-19,55.67,get_prices_from_identifiers(identifier='D',periodicity='day')
D,2025-02-20,55.82,get_prices_from_identifiers(identifier='D',periodicity='day')
...
DUK,2025-02-19,111.79,get_prices_from_identifiers(identifier='DUK',periodicity='day')
...
```
注意：`source` 值是来自单个调用的所有行的相同值——在每一行上写上它，以便始终可用。

**写入** `/tmp/earnings-preview/peer-eps.csv` — 每行一个（股票代码，期间，EPS）。立即在每次 `diluted_eps` 调用后写入：
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

**写入** `/tmp/earnings-preview/consensus-eps.csv` — 每行一个（股票代码，期间，共识平均EPS）。立即在每次 `get_consensus_estimates_from_identifiers` 调用后写入：
```
ticker,period,consensus_mean_eps,num_estimates,source
D,Q4 2025,0.88,12,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q1 2026,0.72,10,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q2 2026,0.91,9,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q3 2026,1.05,8,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
DUK,Q4 2025,1.48,14,get_consensus_estimates_from_identifiers(identifier='DUK',period_type='quarterly',num_periods_forward=4)
...
```

4. **不要计算市盈率或回报率。** 现在原始数据已存储在磁盘上。计算将在阶段6（验证）中执行，从这些文件中读取。

**日期一致性规则（股票回报）：** 在计算比较股票回报（YTD %，1-yr %，30d %，90d %）时，所有股票代码必须使用**完全相同的开始和结束日期**。在将所有价格数据写入 `prices.csv` 后，识别所有股票代码数据中出现的第一个交易日期，并使用该日期作为公共基准日期。不要为不同股票使用不同的基准日期（例如，主体公司从2月19日开始，而竞争对手从2月28日开始）。如果一个股票代码的数据开始较晚，请使用第一个重叠日期进行所有计算。在附录中为每个回报计算声明公共基准日期。

**市盈率货币规则（LTM市盈率）：** 在计算每个公司的LTM市盈率时，使用该公司最新的4个报告季度（来自 `peer-eps.csv`）——而不是对所有公司应用固定的日历窗口。如果一个竞争对手已经报告了Q4 2025，而主体公司只有到Q3 2025的报告，那么竞争对手的LTM EPS应包括Q4 2025。检查每个公司的最新报告期间，并针对每个公司使用最近的4个季度。在附录中注明用于每个市盈率计算的4个季度。

**市值日期戳：** 报告市值时，使用 `peer-market-caps.csv` 中的 `retrieval_date`。如果它与报告日期不同，请在附录中注明。

---

## 阶段4：新闻、估计与行业洞察（通过Kensho Grounding）

针对以下每个类别运行这些 `search` 查询。不要跳过任何一项。

**关键——捕获来源URL：** 每个 Kensho `search` 结果都包括**来源URL**，用于底层文章、报告或数据页面。你必须记录URL与每个发现一起。

**在每次搜索调用后，立即使用以下格式追加结果到** `/tmp/earnings-preview/kensho-findings.txt`。不要等到所有搜索完成——每次一个：

```
=== 搜索："[查询]" ===
DATE_RUN: [今天的日期]
CATEGORY: [estimates|analyst_ratings|risks|news|sector]

FINDING_1: [关键发现或摘录]
URL_1: [搜索结果的来源URL]
SOURCE_1: [出版物名称，如有，日期]

FINDING_2: [关键发现或摘录]
URL_2: [来源URL]
SOURCE_2: [出版物名称，如有，日期]

[...继续所有相关结果，从该搜索中...]
```

**盈利估计与分析师情绪：**
1. `search` for "[TICKER] 盈利估计共识EPS收入下一季度"
   - 记录：共识EPS、共识收入、过去90天内估计修订方向。
   - **立即追加到 kensho-findings.txt。**
2. `search` for "[TICKER] 分析师评级目标价升级降级"
   - 记录：最近的升级/降级、目标价范围、牛市/熊市论点总结。
   - **立即追加到 kensho-findings.txt。**
3. `search` for "[TICKER] 风险熊市担忧投资者"
   - 记录：关键争论、熊市论点、即将到来的报告的摇摆因素。
   - **立即追加到 kensho-findings.txt。**

**近期新闻（强制执行——不要跳过）：**
4. `search` for "[TICKER] [公司名称] 近期新闻发展"
   - 记录：过去60天内的重要新闻——并购、产品发布、高管变动、监管行动、合作、法律发展、关税或任何可能影响即将到来的盈利报告或前瞻性指导的事件。
   - 对每个项目，注明日期、标题、潜在的盈利影响。
   - **立即追加到 kensho-findings.txt。**

**行业背景：**
5. `search` for "[公司行业/部门] 行业展望趋势"
   - 记录：行业层面的顺风/逆风、宏观经济数据、竞争动态。
   - **立即追加到 kensho-findings.txt。**

---

## 阶段5：财务数据收集

**季度财务报表（最近8个季度）：**
`get_financial_line_item_from_identifiers`，设置 `period_type="quarterly"`，`num_periods=8`，用于：
`revenue`、`gross_profit`、`operating_income`、`ebitda`、`net_income`、`diluted_eps`

**每条项目调用返回后，立即追加到** `/tmp/earnings-preview/financials.csv`。将原始值按返回值原样写入——不要四舍五入或转换。包含 `source` 列，其中包含确切的 MCP 函数调用和参数：
```
ticker,period,line_item,value,source
D,Q4 2024,revenue,3941000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q1 2025,revenue,3400000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q2 2025,revenue,4076000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q3 2025,revenue,3810000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q4 2024,diluted_eps,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,diluted_eps,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
```

**不要计算利润率或增长率。** 仅写入原始数据。计算将在第 6 阶段进行。

**按部门数据：**
- 使用 `get_segments_from_identifiers`，`segment_type="business"`，`period_type="quarterly"`，`num_periods=8`
- 您需要 8 个季度（而不是 4 个），以便进行同比比较。要计算 2025 年第 3 季度的同比，您需要 2024 年第 3 季度——这是第 5 个季度。**如果上一年的季度部门数据在 API 响应中不可用，则不要估计或虚构它。在报告中注明“同比不可用”。**

**立即写入** `/tmp/earnings-preview/segments.csv`：
```
ticker,period,segment_name,revenue,source
D,Q3 2024,Dominion Energy Virginia,2762000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Dominion Energy South Carolina,848000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Contracted Energy,260000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy Virginia,3311000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy South Carolina,945000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Contracted Energy,297000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
...
```

**盈利历史（用于股票图表注释）：**
- `get_earnings_from_identifiers`——收集过去 12 个月价格窗口内的盈利日期。
- **立即写入** `/tmp/earnings-preview/earnings-dates.csv`：
```
ticker,earnings_date,call_name,source
D,2025-05-02,Q1 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-08-01,Q2 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-10-31,Q3 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
...
```

---

## 第 6 阶段：验证与计算（强制执行——不要跳过）

在生成报告之前，读取所有中间文件并从干净的数据中进行计算。此阶段通过使用文件而不是压缩的对话上下文来确保数据完整性。

1. **使用 bash `cat` 命令读取所有中间文件**：
   - `cat /tmp/earnings-preview/company-info.txt`
   - `cat /tmp/earnings-preview/transcript-extracts.txt`
   - `cat /tmp/earnings-preview/financials.csv`
   - `cat /tmp/earnings-preview/segments.csv`
   - `cat /tmp/earnings-preview/prices.csv`
   - `cat /tmp/earnings-preview/peer-eps.csv`
   - `cat /tmp/earnings-preview/peer-market-caps.csv`
   - `cat /tmp/earnings-preview/consensus-eps.csv`
   - `cat /tmp/earnings-preview/kensho-findings.txt`
   - `cat /tmp/earnings-preview/earnings-dates.csv`

2. **从当前上下文中的原始数据计算派生指标**：
   - 毛利率 % = 毛利润 / 收入（每个季度）
   - 营业利润率 % = 营业收入 / 收入（每个季度）
   - 收入同比增长率 % = （当前季度收入 - 去年同期收入） / 去年同期收入
   - EPS 同比增长率 % = 相同逻辑；如果基准为负，则使用“n.m。”
   - 部门同比增长率 % = 通过部门名称匹配去年同期；如果缺失，则注明“同比不可用”
   - 公司 LTM 市盈率 = 最新价格 / 最近 4 个季度 EPS 的总和（使用 `peer-eps.csv` 检查每个股票可用的 4 个季度）
   - 公司 NTM 市盈率 = 最新价格 / NTM EPS，其中 **NTM EPS = 从 `consensus-eps.csv` 中获取的下一 4 个季度共识平均 EPS 估计的总和**。为每个股票添加所有 4 个季度的共识_mean_eps 值。如果一个同行少于 4 个前瞻季度可用，则将 NTM 市盈率标记为“n/a”。在附录中注明汇总的 4 个季度。
   - 股票回报（YTD、1 年、30 天、90 天）= 找到 `prices.csv` 中所有股票的**共同最早日期**，然后从该日期计算回报

3. **交叉检查**：
   - 验证 `segments.csv` 中的每个部门同比是否具有实际去年的行。如果没有，则标记“同比不可用”。
   - 验证所有股票回报基准日期在所有股票之间是否相同。
   - 通过重新汇总组件验证任何多步计算（例如，LTM EPS 总和与 4 个季度值匹配）。
   - 验证 `transcript-extracts.txt` 中的所有逐字引用是否为精确复制粘贴（不是释义）。

4. **写入** `/tmp/earnings-preview/calculations.csv`，其中包含所有派生值：
```
ticker,metric,value,formula,components
D,gross_margin_Q3_2025,32.5%,gross_profit/revenue,"gross_profit=1238100000,revenue=3810000000"
D,revenue_yoy_Q3_2025,+9.3%,(Q3_2025-Q3_2024)/Q3_2024,"Q3_2025=3810000000,Q3_2024=3486000000"
D,ltm_pe,24.2x,price/ltm_eps,"price=65.46,ltm_eps=2.70,quarters=Q4_2024+Q1_2025+Q2_2025+Q3_2025"
D,ntm_pe,18.5x,price/ntm_eps,"price=65.46,ntm_eps=3.56,quarters=Q4_2025(0.88)+Q1_2026(0.72)+Q2_2026(0.91)+Q3_2026(1.05),source=get_consensus_estimates_from_identifiers"
D,yoy_return,+17.6%,(end-start)/start,"end=65.46,start=55.67,base_date=2025-02-19"
DUK,yoy_return,+13.0%,(end-start)/start,"end=126.32,start=111.79,base_date=2025-02-19"
...
```

此文件成为报告中所有数字的唯一来源。

---

## 第 7 阶段：生成 HTML 报告

**停止——在编写任何 HTML 之前，你必须读取所有中间文件。这是一个阻塞的先决条件。**

这不是可选的。你必须作为**单独的 bash 工具调用**运行每个 `cat` 命令（不要合并成一个）。这确保了每个文件的內容被单独加载并在对话中可见。不要将它们合并成一个命令。不要跳过任何文件。

运行这些命令**逐个，每个作为其自己的 bash 调用**：

1. `cat /tmp/earnings-preview/company-info.txt`
2. `cat /tmp/earnings-preview/transcript-extracts.txt`
3. `cat /tmp/earnings-preview/financials.csv`
4. `cat /tmp/earnings-preview/segments.csv`
5. `cat /tmp/earnings-preview/prices.csv`
6. `cat /tmp/earnings-preview/peer-eps.csv`
7. `cat /tmp/earnings-preview/peer-market-caps.csv`
8. `cat /tmp/earnings-preview/consensus-eps.csv`
9. `cat /tmp/earnings-preview/kensho-findings.txt`
10. `cat /tmp/earnings-preview/earnings-dates.csv`
11. `cat /tmp/earnings-preview/calculations.csv`

**读取所有文件后，你必须向用户打印一条摘要消息**，列出每个文件及其状态。使用以下格式：

```
--- 数据文件验证 ---
1. company-info.txt        ✓ 加载 ([N] 行)
2. transcript-extracts.txt ✓ 加载 ([N] 行)
3. financials.csv          ✓ 加载 ([N] 行)
4. segments.csv            ✓ 加载 ([N] 行)
5. prices.csv              ✓ 加载 ([N] 行)
6. peer-eps.csv            ✓ 加载 ([N] 行)
7. peer-market-caps.csv    ✓ 加载 ([N] 行)
8. consensus-eps.csv       ✓ 加载 ([N] 行)
9. kensho-findings.txt     ✓ 加载 ([N] 行)
10. earnings-dates.csv     ✓ 加载 ([N] 行)
11. calculations.csv       ✓ 加载 ([N] 行)

所有中间数据文件加载成功。
使用文件数据作为单一来源生成报告。
---
```

如果任何文件缺失或为空，停止并告诉用户哪个文件失败。不要使用缺失数据生成报告。

**报告中 HTML 中的每个数字、引用、来源 URL 和 MCP 函数调用引用都必须来自这些文件——而不是你对我早先对话轮次的记忆。** 文件是单一来源。早先的对话內容可能已被压缩或总结，如果依赖它将包含错误。如果一个数据点不在文件中，它不应出现在报告中。

参见 [report-template.md](report-template.md) 以获取完整的 HTML 模板、CSS 和 Chart.js 配置。

**强制执行——使用模板辅助函数创建图表：**
`report-template.md` 提供了预构建、调试的 Chart.js 辅助函数。你必须使用这些确切的函数来创建图表。不要编写自定义的行内 Chart.js 代码。辅助函数是：
- `createRevEpsChart(canvasId, labels, revenueData, epsData, revLabel)` —— 用于图 1
- `createMarginChart(canvasId, labels, grossMargins, opMargins)` —— 用于图 2
- `createRevGrowthChart(canvasId, labels, growthData)` —— 用于图 3
- `createAnnotatedPriceChart(canvasId, labels, prices, earningsDates, ticker)` —— 用于图 5
- `createCompPerfChart(canvasId, labels, datasets)` —— 用于图 6
- `createPEChart(canvasId, companies)` —— 用于图 7

每个图表调用必须在包含在 try-catch 块中的自己的 `<script>` 标签中。这确保了一个图表中的错误不会阻止其他图表渲染。示例：
```html
<script>
try {
  createRevEpsChart('chart-rev-eps', [...], [...], [...], 'Revenue ($B)');
} catch(e) { console.error('图 1 错误:', e); }
</script>
<script>
try {
  createMarginChart('chart-margins', [...], [...], [...]);
} catch(e) { console.error('图 2 错误:', e); }
</script>
```

### 报告结构（4-5 页总计）

报告分为两半：**叙述**（第 1-2 页）和**图表**（第 3-5 页）。保持这些紧密集成。

---

**AI 免责声明（强制执行——必须在 3 个地方出现）：**
你必须将以下免责文本包含在报告 HTML 中。报告不完整，没有它是不行的：

> **“分析是 AI 生成的——请确认所有输出”**

它必须以以下格式出现在 3 个确切的位置：
1. **页眉横幅**——立即在封面页眉之前，作为居中的黄色横幅：`<div class="ai-disclaimer">分析是 AI 生成的——请确认所有输出</div>`
2. **页脚**——在 page-footer div 内，作为显眼的黄色横幅：`<div class="footer-disclaimer">分析是 AI 生成的——请确认所有输出</div>`
3. **附录**——作为附录部分的第一行，在表格之前：`<div class="ai-disclaimer">分析是 AI 生成的——请确认所有输出</div>`

---

**第 1 页：封面与论点**

- **AI 免责声明横幅**（黄色，居中——见 AI 免责声明规则）
- **页眉**：公司名称（TICKER）| 行业 | 报告日期
- **标题**：主题，针对本季度（例如，“沃尔玛公司 (WMT) 2026 财年第四季度盈利预览：假日丰收——Furner 的首次印刷能否证实 1 万亿美元的论点？”）
- **执行论点**（最多 2-3 短段，带项目符号）：
  - 用 1-2 句话说明我们对此印刷的期望
  - 4-6 个项目符号，涵盖：我们的 EPS 估计与共识、指引预期、要关注的关键指标、什么会推动股价、关键辩论
  - 保持直接和有观点——采取立场，不要回避一切
- **关键管理层引用**从最近的盈利电话会议中提取，在相关位置编织到叙述中。不要将它们放在单独的标题下。自然地整合它们作为支持论点点的证据。格式为缩进块引用。

---

**第 2 页：估计、主题与新闻**

- **共识估计表**（单个表格，标记为图）：
  - 列：指标 | 共识 | 我们的估计 | 同比变化
  - 行：收入、EPS、毛利率、营业收入，以及 2-3 个对公司而言重要的公司特定 KPI（例如，复合销售、电商增长、会员收入——华尔街对此公司关心的东西）
  - **严格机械着色**：如果同比变化值为负，使用 `class="neg"`（红色）。如果为正，使用 `class="pos"`（绿色）。如果为零或 N/A，使用 `class="neutral"`。数字的符号决定类——不要根据解释覆盖。 -1.1% 始终为红色，即使下降很小。
  - 这是唯一的指引/估计部分。不要在其他地方重复估计数据。

- **头条 EPS 以外的关键指标**（项目符号列表，3-5 项）：
  - 除了 EPS 数字之外，决定本季度是好是坏的具体指标
  - 每个指标：指标是什么，共识/管理层预期，为什么它很重要
  - 具体说明：“沃尔玛 Connect 广告收入增长（共识约 30% 同比，第三季度为 33%）”

- **要关注的主题**（3-5 个项目符号）：
  - 对即将到来的报告的前瞻性事项
  - 管理层需要实现什么，什么可能会令人惊讶，空头关注什么
  - 每个主题：最多 1-2 句话

- **最新新闻与发展**（3-5 个项目符号）：
  - 过去 60 天的重大新闻，每条一行
  - 日期 + 标题 + 简要影响评估
  - 仅包括可能影响即将到来的印刷或指引的项目

---

**第 3-5 页：图表（所有图表和表格）**

所有图表按顺序编号。每个图表都有标题和来源行。

- **图 1：季度收入与稀释 EPS**——条形/折线组合图，8 个季度
- **图 2：利润率趋势（毛利润率 % 和营业利润率 %）**——双线图，8 个季度
- **图 3：收入同比增长 %**——条形图，带绿色/红色条件着色。**仅包括当前和去年同期数据都存在的季度**（通常是获取的 8 个季度中最新的 4 个季度）。不要包括同比无法计算的季度——图表应有 4 个条形，而不是 8 个。
- **图 4：业务部门收入**——表格：部门 | 最新季度收入（百万） | 占比 | 同比变化
- **图 5：1 年股票价格与盈利日期**——价格线，在盈利日期处有垂直注释线，标明季度和盈利后 1 天的变动
- **图 6：股票表现与竞争对手（索引为 100）**——多线图，本公司为粗实线，竞争对手为细虚线
- **图 7：LTM 市盈率与竞争对手**——水平条形图，本公司突出显示为海军蓝
- **图 8：竞争对手比较表**——股票代码 | 公司 | 市值 | LTM 市盈率 | NTM 市盈率 | YTD % | 1 年 % 

---

**附录：数据来源与计算（强制执行——不要跳过或缩写）**

附录必须以 AI 免责声明横幅开头：`<div class="ai-disclaimer">分析是 AI 生成的——请确认所有输出</div>`

报告的最后一页（或几页）必须包含一个附录表格，记录报告中引用的**每个声明**——数字和非数字。报告中出现的每个数字都必须在附录中有一个对应的行，并且报告中出现的每个此类数字都必须是可点击的 `<a href="#ref-N">` 链接，滚动到其附录行。如果报告中出现数字而没有到附录的链接，则报告不完整。

- **表列**: 引用编号 | 事实 | 数值 | 来源及推导
- **引用编号**: 与报告正文中超链接锚点匹配的顺序ID（例如，`ref-1`，`ref-2`等）。每一行都有一个`id="ref-N"`属性，以便超链接滚动到该位置。
- **事实**: 人类可读的标签（例如，“2026财年第三季度收入”，“WMT的LTM市盈率”，“管理层指出关税逆风”，“巴克莱将评级上调至增持”）
- **数值**: 报告中显示的确切数字（例如，“$152.3B”，“24.5%”，“28.1x”）。对于非数字事实，留空或写“N/A”。
- **来源及推导**: 这是关键列。**每一行都必须有一个具体、详细的来源——不仅仅是标签。** 严格遵循以下规则：

  **对于来自S&P Capital IQ的原始财务数据（收入、每股收益、毛利润、营业收入、净利润、EBITDA、价格、市值等）:**
  - 说明使用的MCP函数及其关键参数。格式：`S&P Capital IQ — [function_name](identifier='[TICKER]'，line_item='[item]'，period_type='[type]'，period='[Q# FY####]')`
  - 示例：
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT'，line_item='revenue'，period_type='quarterly'，period='Q3 FY2026')`
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT'，line_item='diluted_eps'，period_type='quarterly'，period='Q3 FY2026')`
    - `S&P Capital IQ — get_prices_from_identifiers(identifier='WMT'，periodicity='day')`
    - `S&P Capital IQ — get_capitalization_from_identifiers(identifier='WMT'，capitalization='market_cap')`
  - **不要只写“S&P Capital IQ”而没有细节。** 读者必须确切知道哪个数据点从哪个工具调用中产生了这个数字。

  **对于计算值（利润率、增长率、市盈率、回报、同比变化）:**
  - 显示完整的公式，并使用**超链接组件**——每个组件必须是回退到附录行中该原始数据点的`<a href="#ref-N">`链接。这是关键：读者必须能够从计算值点击到其每个输入。
  - 示例：`毛利润率 = <a href='#ref-5'>毛利润 $37.2B</a> / <a href='#ref-1'>收入 $152.3B</a> = 24.4%。来源：S&P Capital IQ（计算）`
  - 示例：`LTM市盈率 = <a href='#ref-20'>价格 $172.35</a> / (<a href='#ref-8'>Q1每股收益 $1.47</a> + <a href='#ref-9'>Q2每股收益 $1.84</a> + <a href='#ref-10'>Q3每股收益 $1.53</a> + <a href='#ref-11'>Q4每股收益 $1.80</a>) = $172.35 / $6.64 = 25.9x`
  - 示例：`收入同比增长 = (<a href='#ref-12'>2026财年第三季度收入 $165.8B</a> - <a href='#ref-3'>2025财年第三季度收入 $160.8B</a>) / <a href='#ref-3'>2025财年第三季度收入 $160.8B</a> = +3.1%`
  - **每个公式组件必须是一个可点击的超链接。** 不要用纯文本数字写公式。

  **对于来自会议记录的声明（引言、管理层评论、指引）:**
  - 写出从会议记录中**逐字引用的句子**。
  - 通过其完整名称和用于获取它的`key_dev_id`来引用会议记录。
  - 格式：`"[逐字引用]" — [发言人]，[职务]。来源：[Q# FY#### 盈利电话会议记录] (key_dev_id: [ID])`
  - 示例：`"我们预计第四季度可比销售额增长3-4%" — CEO John Furner。来源：2026财年第三季度盈利电话会议记录 (key_dev_id: 12345678)`

  **对于Kensho Grounding搜索结果（新闻、分析师评级、一致预期）:**
  - 写出搜索结果中的关键发现或摘录。
  - **强制要求：包括Kensho `search` 工具返回的来源URL**作为可点击的`<a href="[URL]" target="_blank">`超链接。这是最重要的部分——读者必须能够点击到原始来源。
  - 格式：`"[发现/摘录]" — <a href="[URL]" target="_blank">[来源标题或出版物]</a>。查询：search("[使用的查询]")`
  - 示例：`"Barclays于2026年1月15日将WMT评级上调至增持，目标价210美元。" — <a href="https://www.investing.com/news/barclays-upgrades-wmt" target="_blank">Investing.com，2026年1月15日</a>。查询：search("WMT分析师评级目标价上调下调")`
  - 如果某个结果没有返回URL，写“来源URL不可用”，但仍需包括搜索查询。

**完整性检查：** 在最终确定报告之前，扫描报告正文中每个数字。如果任何数字没有被`<a href="#ref-N" class="data-ref">`包裹，请修复它。如果任何附录行中的来源及推导只是一个裸标签，如“S&P Capital IQ”而没有函数调用细节，请修复它。如果任何计算值的公式缺少超链接组件，请修复它。如果任何Kensho来源的声明缺少来源URL，请修复它。

将附录行按部分分组（财务、估值、预期与一致预期、会议记录声明、新闻与分析师评论、股票表现），使用子标题。使用较小的字体大小（10-11px）。

---

## 第8阶段：输出

1. 将完整的HTML文件写入`earnings-preview-[TICKER]-YYYY-MM-DD.html`到当前工作目录。
2. 在浏览器中打开它：`open earnings-preview-[TICKER]-YYYY-MM-DD.html`
3. 告知用户文件已创建，并总结关键发现。

---

## 写作指南

- **无表情符号**：不要在任何地方使用表情符号。这是一个专业的研究文件。
- **简洁**：目标4-5页打印。每句话都必须有价值。尽可能使用项目符号，而不是段落。如果一个部分感觉太长，请删减。
- **具体数字**："$52.4B收入，同比增长5.2%"，而不是“强劲的收入增长”。
- **表达观点**：这是一个盈利预览，不是摘要。说明你的预期，什么重要，为什么。要有观点，但要靠数据支持。
- **管理层引言无标题**：将最近电话会议上的3-4个关键管理层引言直接编织到叙述中作为块引用。不要创建“关键管理层引言”部分标题——让它们自然地作为支持证据流动。
- **专业语气**：卖方股票研究风格——分析性、直接、数据驱动。
- **图表必须使用真实数据**：每个图表填充实际MCP数据。永远不要编造。
- **竞争对手背景**：将估值与同行进行比较。25倍的市盈率意味着什么，除非知道同行交易在20倍或35倍。
- **超链接声明**：每个事实——数字或定性——必须是一个`<a class="data-ref">`标签链接到其附录条目。数字：`<a href="#ref-1" class="data-ref">$152.3B</a>`。定性：`<a href="#ref-25" class="data-ref">管理层指出关税逆风为主要利润率风险</a>`。没有事实应该没有可追溯的来源在附录中。
