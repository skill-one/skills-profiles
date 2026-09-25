# 股票分析 (v5.0)

使用雅虎财经数据分析美国股票和加密货币。包含投资组合管理、加密货币支持和周期性分析。

## 快速入门

**重要提示**：仅将股票代码作为参数传递。不要在命令中添加额外文本、标题或格式。

分析单个代码：

```bash
uv run {baseDir}/scripts/analyze_stock.py AAPL
uv run {baseDir}/scripts/analyze_stock.py MSFT --output json
```

比较多个代码：

```bash
uv run {baseDir}/scripts/analyze_stock.py AAPL MSFT GOOGL
```

## 加密货币分析 (v5.0)

分析市值排名前20的加密货币：

```bash
uv run {baseDir}/scripts/analyze_stock.py BTC-USD
uv run {baseDir}/scripts/analyze_stock.py ETH-USD SOL-USD
```

**支持的加密货币**：
BTC-USD, ETH-USD, BNB-USD, SOL-USD, XRP-USD, ADA-USD, DOGE-USD, AVAX-USD, DOT-USD, MATIC-USD, LINK-USD, ATOM-USD, UNI-USD, LTC-USD, BCH-USD, XLM-USD, ALGO-USD, VET-USD, FIL-USD, NEAR-USD

**加密货币分析维度**：
- 市值（大型/中型/小型分类）
- 类别（智能合约L1、去中心化金融、支付等）
- 与比特币的相关性（30天）
- 动量（RSI、价格区间）
- 市场环境（VIX、市场状态）

## 投资组合管理 (v5.0)

创建和管理混合资产（股票+加密货币）的投资组合：

```bash
# 创建投资组合
uv run {baseDir}/scripts/portfolio.py create "我的投资组合"

# 添加资产
uv run {baseDir}/scripts/portfolio.py add AAPL --quantity 100 --cost 150.00
uv run {baseDir}/scripts/portfolio.py add BTC-USD --quantity 0.5 --cost 40000 --portfolio "我的投资组合"

# 查看持仓及当前盈亏
uv run {baseDir}/scripts/portfolio.py show

# 更新/删除资产
uv run {baseDir}/scripts/portfolio.py update AAPL --quantity 150
uv run {baseDir}/scripts/portfolio.py remove BTC-USD

# 列出/删除投资组合
uv run {baseDir}/scripts/portfolio.py list
uv run {baseDir}/scripts/portfolio.py delete "我的投资组合"
```

**投资组合存储**：`~/.clawdbot/skills/stock-analysis/portfolios.json`

## 投资组合分析 (v5.0)

分析投资组合中的所有资产，可选周期回报：

```bash
# 分析投资组合
uv run {baseDir}/scripts/analyze_stock.py --portfolio "我的投资组合"

# 带周期回报（每日/每周/每月/每季度/每年）
uv run {baseDir}/scripts/analyze_stock.py --portfolio "我的投资组合" --period 每周
uv run {baseDir}/scripts/analyze_stock.py -p "我的投资组合" --period 每月
```

**投资组合摘要包括**：
- 总成本、当前价值、盈亏
- 周期回报（如指定）
- 集中度警告（单一资产占比>30%）
- 建议摘要（买入/持有/卖出计数）

**示例**：
- ✅ 正确：`uv run {baseDir}/scripts/analyze_stock.py BAC`
- ✅ 正确：`uv run {baseDir}/scripts/analyze_stock.py BTC-USD`
- ❌ 错误：`uv run {baseDir}/scripts/analyze_stock.py === 美国银行 (BAC) - 2025年第四季度盈利 ===`
- ❌ 错误：`uv run {baseDir}/scripts/analyze_stock.py "美国银行"`

仅使用代码（例如，BAC，而不是"美国银行"）。对于加密货币，使用-USD后缀（例如，BTC-USD）。

## 分析组件

脚本评估八个关键维度：

1. **盈利预期（权重30%**）：实际与预期EPS、收入超预期/不及预期
2. **基本面（权重20%**）：市盈率、利润率、收入增长、债务水平
3. **分析师情绪（权重20%**）：一致评级、目标价与当前价的对比
4. **历史模式（权重10%**）：过去盈利反应、波动性
5. **市场环境（权重10%**）：VIX、SPY/QQQ趋势、市场状态
6. **行业表现（权重15%**）：股票与行业对比、行业趋势
7. **动量（权重15%**）：RSI、52周范围、成交量、相对强度
8. **情绪分析（权重10%**）：恐惧/贪婪指数、空头兴趣、VIX期限结构、内幕交易、看跌/看涨比率

**情绪子指标**：
- **恐惧与贪婪指数（CNN）**：逆向信号（极度恐惧=买入机会，极度贪婪=谨慎）
- **空头兴趣**：高空头+挤压潜力=看涨；合理空头=看跌
- **VIX期限结构**：期货溢价=自满/看涨；期货贴水=压力/看跌
- **内幕交易**：来自SEC Form 4申报的净买入/卖出（90天窗口）
- **看跌/看涨比率**：高比率=过度恐惧/看涨；低比率=自满/看跌

如果某些组件不可用，权重将自动归一化。

**特殊时间检查**：
- 盈利预警前（<14天）：建议持有而不是买入
- 盈利后飙升检测（>15%在5天内）：标记"收益已被消化"
- 过度买入条件（RSI>70+接近52周高点）：降低信心

## 时间警告与风险标志

脚本检测高风险场景：

### 盈利时间
- **盈利预警前**：如果盈利<14天，买入信号变为持有
- **盈利后飙升**：如果股票在盈利后5天内上涨>15%，警告"收益可能已被消化"

### 技术风险
- **过度买入条件**：RSI>70+接近52周高点=高风险入场

### 市场风险
- **高VIX**：市场恐惧（VIX>30）降低买入信号的信心
- **避险模式（v4.0.0）**：当避险资产（GLD、TLT、UUP）同时上涨时，降低买入信心30%
  - 检测黄金、国债和美元的避险情绪
  - 当GLD ≥ +2%、TLT ≥ +1%、UUP ≥ +1%（5天变化）时触发

### 行业风险
- **行业疲软**：股票可能看起来不错，但行业正在轮动出

### 地缘政治风险 (v4.0.0)
脚本现在扫描过去24小时的突发新闻，查找危机关键词，并自动标记受影响的股票：

- **台湾冲突**：半导体（NVDA、AMD、TSM、INTC等）→ 降低30%信心
- **中国紧张局势**：科技/消费（AAPL、QCOM、NKE、SBUX等）→ 降低30%信心
- **俄罗斯-乌克兰**：能源/材料（XOM、CVX、MOS、CF等）→ 降低30%信心
- **中东**：石油/国防（XOM、LMT、RTX等）→ 降低30%信心
- **银行危机**：金融（JPM、BAC、WFC、C等）→ 降低30%信心

如果一个代码不在受影响列表中，但其行业受影响，将应用15%的信心惩罚。

**示例警报**：
```
⚠️ 行业风险：科技供应链和消费市场敞口（检测到：中国、关税）
```

### 突发新闻警报 (v4.0.0)
- 扫描Google新闻RSS查找危机关键词（战争、衰退、制裁、灾难等）
- 显示最多2条突发新闻警报（过去24小时）
- 使用1小时缓存以避免过多的API调用

## 输出格式

**默认（文本）**：简洁的买入/持有/卖出信号，3-5个要点和注意事项

**JSON**：结构化数据，包含分数、指标和原始数据，用于进一步分析

## 限制

- **数据新鲜度**：雅虎财经可能滞后15-20分钟
- **情绪数据陈旧性**：
  - 空头兴趣数据滞后约2周（FINRA报告时间表）
  - 内幕交易可能滞后申报2-3天
  - VIX期限结构仅在期货交易时段更新
- **突发新闻限制 (v4.0.0)**：
  - Google新闻RSS可能滞后15-60分钟
  - 关键词匹配可能有误报/漏报
  - 不分析情绪，仅检测关键词
  - 1小时缓存意味着警报可能稍显陈旧
- **缺失数据**：并非所有股票都有分析师覆盖、期权链或完整基本面
- **执行时间**：每个股票3-5秒，异步并行获取和缓存（共享指标缓存1小时）
- **免责声明**：所有输出均包含显眼的"非财务建议"警告
- **仅限美国市场**：非美国代码可能数据不完整

## 错误处理

脚本优雅地处理：
- 无效代码 → 清晰的错误消息
- 缺失分析师数据 → 仅基于可用指标发出信号
- API故障 → 指数退避重试，3次后失败
