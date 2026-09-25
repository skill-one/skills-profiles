# 机构资金流向追踪器

## 概述

该技能通过追踪 13F SEC 报告来追踪机构投资者的活动，以识别"聪明资金"流入和流出股票的趋势。通过分析季度内机构持股的变化，你可以发现复杂投资者在重大价格变动前正在积累的股票，或在机构减少头寸时识别潜在风险。

**关键洞察：** 机构投资者（对冲基金、养老基金、共同基金）管理着数万亿美元资产，并进行广泛的研究。他们的集体买入/卖出模式通常在重大价格变动前 1-3 个季度出现。

## 前置条件

- **FMP API Key：** 设置 `FMP_API_KEY` 环境变量或向脚本传递 `--api-key`
- **Python 3.9+：** 运行分析脚本所需
- **依赖项：** `pip install requests`（脚本会友好处理缺失的依赖项）

## 使用此技能的场景

在以下情况下使用此技能：
- 验证投资想法（检查聪明资金是否同意你的假设）
- 发现新机会（找到机构正在积累的股票）
- 风险评估（识别机构正在退出的股票）
- 投资组合监控（追踪机构对你持仓的支持）
- 追踪特定投资者（追踪沃伦·巴菲特、凯茜·伍德等）
- 行业轮动分析（识别机构正在转移资金的领域）

**不使用场景：**
- 寻求实时日内信号（13F 数据有 45 天的报告滞后）
- 分析微盘股（市值 <1000 万美元且机构兴趣有限）
- 寻找短期交易信号（<3 个月的时间范围）

## 数据源和要求

### 必需：FMP API Key

该技能使用 Financial Modeling Prep (FMP) API 访问 13F 报告数据：

**设置：**
```bash
# 设置环境变量（推荐）
export FMP_API_KEY=your_key_here

# 或在运行脚本时提供
python3 scripts/track_institutional_flow.py --api-key YOUR_KEY
```

**API 层级要求：**
- **免费层级：** 每天最多 250 次请求（足够分析每季度 20-30 支股票）
- **付费层级：** 更高的限额用于广泛的筛选

**13F 报告时间表：**
- 每季度在季度结束后的 45 天内提交
- Q1（1 月-3 月）：在 5 月中旬前提交
- Q2（4 月-6 月）：在 8 月中旬前提交
- Q3（7 月-9 月）：在 11 月中旬前提交
- Q4（10 月-12 月）：在 2 月中旬前提交

## 分析工作流程

### 第 1 步：识别具有显著机构变化的股票

执行主筛选脚本以找到具有显著机构活动的股票：

**快速扫描（按机构变化排名前 50 支股票）：**
```bash
python3 scripts/track_institutional_flow.py \
  --top 50 \
  --min-change-percent 10
```

**按行业扫描：**
```bash
python3 scripts/track_institutional_flow.py \
  --sector Technology \
  --min-institutions 20
```

**自定义筛选：**
```bash
python3 scripts/track_institutional_flow.py \
  --min-market-cap 2000000000 \
  --min-change-percent 15 \
  --top 100 \
  --output institutional_flow_results.json
```

**输出包括：**
- 股票代码和公司名称
- 当前机构持股比例（占总股本）
- 季度环比持股变化
- 持有该股票的机构数量
- 机构数量变化（新买家与卖家的变化）
- 顶级机构持有人

### 第 2 步：对特定股票进行深入分析

对特定股票的机构持股进行详细分析：

```bash
python3 scripts/analyze_single_stock.py AAPL
```

**这将生成：**
- 历史机构持股趋势（8 个季度）
- 顶级 20 位机构持有人及其头寸变化
- 集中度分析（前 10 位持有人占总机构持股的百分比）
- 大型持有人新增/增持/减持
- 数据质量评估及覆盖率可靠性等级

**评估关键指标：**
- **持股比例：** 较高的机构持股（>70%）= 更稳定但上涨空间有限
- **持股趋势：** 上涨 = 买入，下跌 = 卖出
- **集中度：** 高集中度（前 10 位 >50%）= 如果他们卖出则存在风险
- **持有人质量：** 质量长期投资者（伯克希尔、富达）与动量基金

### 第 3 步：追踪特定机构投资者

> **注意：** `track_institution_portfolio.py` **尚未实现**。FMP API 按股票组织机构持有人数据（而非按机构），仅通过此 API 无法实现完整的投资组合重建。

**替代方法——使用 `analyze_single_stock.py` 检查特定机构是否持有某股票：**
```bash
# 分析一支股票并搜索报告中的顶级持有人表以查找特定机构
python3 institutional-flow-tracker/scripts/analyze_single_stock.py AAPL
# 然后在报告中搜索 "Berkshire" 或 "ARK"
```

**用于完整机构级投资组合追踪的外部资源：**
1. **WhaleWisdom：** https://whalewisdom.com（提供免费层级，13F 投资组合查看器）
2. **SEC EDGAR：** https://www.sec.gov/cgi-bin/browse-edgar（官方 13F 报告）
3. **DataRoma：** https://www.dataroma.com（超级投资者投资组合追踪器）

### 第 4 步：解读和行动

参考指南以获取解读建议：
- `references/13f_filings_guide.md` - 了解 13F 数据及其局限性
- `references/institutional_investor_types.md` - 不同类型机构投资者及其策略
- `references/interpretation_framework.md` - 如何解读机构资金流信号

**信号强度框架：**

**强烈买入（考虑买入）：**
- 机构持股环比增长 >15%
- 机构数量环比增长 >10%
- 质量长期投资者增持
- 当前持股比例较低（<40%）且仍有增长空间
- 多个季度持续积累

**温和买入：**
- 机构持股环比增长 5-15%
- 新买家与卖家并存，净买入为正
- 当前持股比例 40-70%

**中性：**
- 持股比例变化较小（<5%）
- 买家与卖家数量相似
- 稳定的机构基础

**温和卖出：**
- 机构持股环比下降 5-15%
- 卖家多于买家
- 高持股比例 (>80%) 限制新买家

**强烈卖出（考虑卖出/避免）：**
- 机构持股环比下降 >15%
- 机构数量环比下降 >10%
- 质量投资者减持
- 多个季度持续派发
- 集中度风险（顶级持有人卖出大额头寸）

### 第 5 步：投资组合应用

**对于新仓位：**
1. 对你的股票想法进行机构分析
2. 查看机构是否也在积累
3. 如果有强烈卖出信号，重新考虑或减少仓位大小
4. 如果有强烈买入信号，增强你的假设信心

**对于现有持仓：**
1. 在 13F 报告截止日期后进行季度审查
2. 监控派发（早期预警系统）
3. 如果机构正在退出，重新评估你的假设
4. 如果出现广泛机构卖出，考虑减仓

**筛选工作流集成：**
1. 使用 Value Dividend Screener 或其他筛选器找到候选股票
2. 对候选股票运行机构资金流追踪器
3. 优先考虑机构增持的股票
4. 避免机构派发的股票

## 输出格式

所有分析都会生成结构化的 Markdown 报告并保存在仓库根目录：

**文件命名规范：** `institutional_flow_analysis_<TICKER/THEME>_<DATE>.md`

**报告部分：**
1. 执行摘要（关键发现）
2. 机构持股趋势（当前与历史对比）
3. 顶级持有人及变化
4. 新买家与卖家
5. 集中度分析
6. 解读与建议
7. 数据来源和时间戳

## 数据可靠性等级

所有分析都包含**基于覆盖率的可靠性等级**：

- **A级：** 存在可比的前一季度且该股票有 **>= 50** 机构（13F）持有人。密集覆盖，适合排名。
- **B级：** 存在可比的前一季度且该股票有 **>= 10** 持有人。可用但稀疏——仅作参考。
- **C级：** 无可比前一季度（无法衡量变化）或 **< 10** 持有人。**排除**于筛选结果之外。

筛选脚本 (`track_institutional_flow.py`) 会自动排除 C 级股票。
单只股票分析 (`analyze_single_stock.py`) 会显示等级并附上适当警告。

**为什么是覆盖率而非持有人逐个核对：** 指标来自 FMP 的汇总 13F 数据 (`institutional-ownership/symbol-positions-summary`)，该数据在源头处就跨所有申报管理人 reconciled 了季度环比增量。这取代了已停用的 `/api/v3/institutional-holder` 接口，该接口返回季度间不对称的持有人列表（例如，一个季度 5,415 位持有人，下一个季度只有 201 位），并需要客户端过滤以避免百分比变化被夸大。通过汇总摘要，实践中最重要的信号是 **广度**（有多少管理人持有该名称）以及是否存在可比的前一季度来衡量变化——这就是现在等级反映的内容。

## 局限性和注意事项

**数据滞后：**
- 13F 报告有 45 天的报告延迟
- 申报日期以来的头寸可能已发生变化
- 仅作为确认指标，而非领先信号

**覆盖率：**
- 仅要求管理 >1000 万美元的机构提交
- 排除个人投资者和规模较小的基金
- 国际机构可能不提交 13F

**报告规则：**
- 仅报告长期股权头寸（无空头、期权、债券）
- 持仓为季度末快照
- 部分头寸可能保密（延迟报告）

**解读：**
- 相关性不等于因果关系（即使机构买入，股票也可能下跌）
- 考虑整体市场环境和基本面
- 结合技术分析和其他技能

## 高级用例

**内幕+机构组合：**
- 查找内幕人士和机构都在买入的股票
- 尤其当两者一致时，信号特别强大

**行业轮动检测：**
- 跟踪按行业的机构资金总流向
- 识别价格出现前轮动趋势

**逆势操作：**
- 找到机构正在卖出的优质股票（潜在价值）
- 需要强烈的基本面信念

**聪明资金验证：**
- 在重大仓位变动前，检查聪明资金是否同意
- 增强信心或发现被忽视的风险

## 参考文献

`references/` 文件夹包含详细指南：

- **13f_filings_guide.md** - 13F SEC 报告的全面指南，包括其包含内容、报告要求及数据质量考虑
- **institutional_investor_types.md** - 不同类型的机构投资者（对冲基金、共同基金、养老基金等）、其典型策略及如何解读其动向
- **interpretation_framework.md** - 解读机构持股变化的详细框架、信号质量评估及与其他分析的整合

## 脚本参数

### track_institutional_flow.py

主筛选脚本，用于找到具有显著机构变化的股票。

**必需：**
- `--api-key`：FMP API Key（或设置 FMP_API_KEY 环境变量）

**可选：**
- `--top N`：按机构变化排名前 N 支股票（默认：50）
- `--min-change-percent X`：机构持股最小百分比变化（默认：10）
- `--min-market-cap X`：最小市值（美元）（默认：1B）
- `--sector NAME`：按特定行业筛选
- `--min-institutions N`：最小机构持有人数量（默认：10）
- `--limit N`：从筛选器获取的股票数量（默认：100）。较低值可节省 API 调用。
- `--output FILE`：输出 JSON 文件路径
- `--output-dir DIR`：输出报告目录（默认：reports/）
- `--sort-by FIELD`：按 'ownership_change' 或 'institution_count_change' 排序

### analyze_single_stock.py

对特定股票的机构持股进行深入分析。

**必需：**
- 股票代码（位置参数）
- `--api-key`：FMP API Key（或设置 FMP_API_KEY 环境变量）

**可选：**
- `--quarters N`：分析季度数量（默认：8，即 2 年）
- `--output FILE`：输出 Markdown 报告路径
- `--output-dir DIR`：输出报告目录（默认：reports/）
- `--compare-to TICKER`：比较另一支股票的机构持股（未来功能）

### track_institution_portfolio.py

**状态：尚未实现**

此脚本是一个占位符。它打印替代资源（WhaleWisdom、SEC EDGAR、DataRoma）并退出错误代码 1。FMP API 按股票组织机构持有人数据（而非按机构），使得完整投资组合重建不切实际。

对于机构级投资组合追踪，使用：
1. WhaleWisdom：https://whalewisdom.com（提供免费层级）
2. SEC EDGAR：https://www.sec.gov/cgi-bin/browse-edgar
3. DataRoma：https://www.dataroma.com

### 数据质量模块（data_quality.py）

由 `track_institutional_flow.py` 和 `analyze_single_stock.py` 共用的共享工具模块：

- **coverage_grade()：** 根据持有人广度 + 可比前一季度可用性分配 A/B/C 等级
- **latest filed quarter helpers** (`current_quarter()`, `iter_quarters()`, `quarter_end_date()`)：回溯到最近有 13F 数据的季度
- **normalize_holder()：** 将 `extract-analytics/holder` 行映射到 `{name, shares, change, is_new, is_sold_out}`
- **is_tradable_stock()：** 过滤 ETF、基金和未活跃股票
- **deduplicate_share_classes()：** 移除 BRK-A/B、GOOG/GOOGL 重复

## 与其他技能的集成

**Value Dividend Screener + 机构资金流：**
```
1. 运行 Value Dividend Screener 找到候选股票
2. 对每个候选股票检查机构资金流
3. 优先考虑机构增持的股票
```

**US Stock Analysis + 机构资金流：**
```
1. 运行全面基本面分析
2. 用机构持股趋势验证
3. 如果机构在卖出，调查原因
```

**Portfolio Manager + 机构资金流：**
```
1. 通过 Alpaca 获取当前投资组合
2. 对每个持仓运行机构分析
3. 标记机构支持恶化的持仓
4. 考虑减仓以避免派发
```

**技术分析师 + 机构资金流：**
```
1. 识别技术设置（例如，突破）
2. 检查机构买入是否确认
3. 两者一致时，信心更高
```

## 最佳实践

1. **季度审查：** 设置日历提醒 13F 报告截止日期
2. **多季度趋势：** 查找持续趋势（3 个季度以上），而非一次性变化
3. **质量胜于数量：** 伯克希尔增持 >100 小基金增持
4. **背景重要：** 在下跌股票中上涨持股可能是价值投资者接住下跌的刀
5. **结合信号：** 永远不要单独使用机构资金流
6. **更新数据：** 每季度新 13F 报告提交后重新运行分析

## 支持 & 资源

- FMP API 文档：https://financialmodelingprep.com/developer/docs
- SEC 13F 报告数据库：https://www.sec.gov/cgi-bin/browse-edgar
- 机构投资者数据库：https://whalewisdom.com（提供免费层级）

---

**注意：** 此技能专为长期投资者（3-12 个月时间范围）设计。对于短期交易，结合技术分析和其他动量指标。
