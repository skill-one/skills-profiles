# 价值股息筛选器

## 概述

该技能使用**两阶段筛选方法**识别结合价值特征、吸引人收入生成和持续增长的优质股息股票：

1. **FINVIZ Elite API（可选但推荐）**：使用基本标准预筛选股票（快速、经济高效）
2. **Financial Modeling Prep (FMP) API**：对候选股票进行详细的财务分析

基于估值比率、股息指标、财务健康状况和盈利能力的量化标准筛选美国股票。生成综合质量评分排名的股票报告，并提供详细的财务分析。

**效率优势**：使用FINVIZ预筛选可减少FMP API调用量90%，因此这种方法非常适合免费层API用户。

## 使用场景

当用户请求以下内容时调用此技能：
- "寻找优质股息股票"
- "筛选价值股息机会"
- "显示具有强劲股息增长的股票"
- "寻找合理估值的收入股票"
- "筛选可持续的高收益股票"
- 任何结合股息收益率、估值指标和基本分析的请求

## 工作流程

### 第1步：验证API密钥可用性

**对于两阶段筛选（推荐）：**

检查两个API密钥是否可用：

```python
import os
fmp_api_key = os.environ.get('FMP_API_KEY')
finviz_api_key = os.environ.get('FINVIZ_API_KEY')
```

如果不可用，请要求用户提供API密钥或设置环境变量：
```bash
export FMP_API_KEY=your_fmp_key_here
export FINVIZ_API_KEY=your_finviz_key_here
```

**对于仅使用FMP筛选：**

检查FMP API密钥是否可用：

```python
import os
api_key = os.environ.get('FMP_API_KEY')
```

如果不可用，请要求用户提供API密钥或设置环境变量：
```bash
export FMP_API_KEY=your_key_here
```

**FINVIZ Elite API密钥：**
- 需要FINVIZ Elite订阅（约每月40美元或每年330美元）
- 提供预筛选结果的CSV导出访问权限
- 强烈推荐以减少FMP API使用量

如有需要，可提供`references/fmp_api_guide.md`中的说明。

### 第2步：执行筛选脚本

使用适当的参数运行筛选脚本：

#### **两阶段筛选（推荐）**

使用FINVIZ进行预筛选，然后使用FMP进行详细分析：

**默认执行（前20只股票）：**
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz
```

**使用显式API密钥：**
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz \
  --fmp-api-key $FMP_API_KEY \
  --finviz-api-key $FINVIZ_API_KEY
```

**自定义前N：**
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz --top 50
```

**自定义输出位置：**
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz --output /path/to/results.json
```

**脚本行为（两阶段）：**
1. FINVIZ Elite预筛选：
   - 市值：中盘或更高
   - 股息收益率：3%+
   - 股息增长（3年）：5%+
   - EPS增长（3年）：正值
   - P/B：低于2
   - P/E：低于20
   - 销售增长（3年）：正值
   - 地域：美国
2. FMP对FINVIZ结果的详细分析（通常20-50只股票）：
   - 股息增长率计算（3年CAGR）
   - 收入和EPS趋势分析
   - 股息可持续性评估（派息比率、自由现金流覆盖率）
   - 财务健康指标（负债权益比、流动比率）
   - 质量评分（ROE、利润率）
3. 综合评分和排名
4. 输出前N只股票到JSON文件

**预期运行时间（两阶段）：** 对于30-50个FINVIZ候选股票，2-3分钟（比仅使用FMP快得多）

#### **仅使用FMP筛选（原始方法）**

仅使用FMP股票筛选器API（API使用量较高）：

**默认执行：**
```bash
python3 scripts/screen_dividend_stocks.py
```

**使用显式API密钥：**
```bash
python3 scripts/screen_dividend_stocks.py --fmp-api-key $FMP_API_KEY
```

**脚本行为（仅使用FMP）：**
1. 使用FMP股票筛选器API进行初始筛选（股息收益率≥3.0%，P/E≤20，P/B≤2）
2. 对候选股票进行详细分析（通常100-300只股票）：
   - 与两阶段方法相同的详细分析
3. 综合评分和排名
4. 输出前N只股票到JSON文件

**预期运行时间（仅使用FMP）：** 对于100-300个候选股票，5-15分钟（适用速率限制）

**API使用量比较：**
- 两阶段：~50-100个FMP API调用（FINVIZ预筛选至~30只股票）
- 仅使用FMP：~500-1500个FMP API调用（分析所有筛选器结果）

### 第3步：解析和分析结果

读取生成的JSON文件：

```python
import json

with open('dividend_screener_results.json', 'r') as f:
    data = json.load(f)

metadata = data['metadata']
stocks = data['stocks']
```

**每只股票的关键数据点：**
- 基本信息："symbol"、"company_name"、"sector"、"market_cap"、"price"
- 估值："dividend_yield"、"pe_ratio"、"pb_ratio"
- 增长指标："dividend_cagr_3y"、"revenue_cagr_3y"、"eps_cagr_3y"
- 可持续性："payout_ratio"、"fcf_payout_ratio"、"dividend_sustainable"
- 财务健康状况："debt_to_equity"、"current_ratio"、"financially_healthy"
- 质量指标："roe"、"profit_margin"、"quality_score"
- 综合排名："composite_score"

### 第4步：生成Markdown报告

为用户提供结构化的Markdown报告，包含以下部分：

#### 报告结构

```markdown
# 价值股息股票筛选报告

**生成时间：** [时间戳]
**筛选标准：**
- 股息收益率：≥ 3.5%
- P/E比率：≤ 20
- P/B比率：≤ 2
- 股息增长（3年CAGR）：≥ 5%
- 收入趋势：3年内为正值
- EPS趋势：3年内为正值

**总结果：** [N]只股票

---

## 前20只按综合评分排名的股票

| 排名 | 符号 | 公司 | 收益率 | P/E | 股息增长 | 分数 |
|------|------|------|-------|-----|------------|-------|
| 1 | [TICKER] | [名称] | [%] | [X.X] | [%] | [XX.X] |
| ... |

---

## 详细分析

### 1. [SYMBOL] - [公司名称]（分数：XX.X）

**行业：** [行业名称]
**市值：** $[X.XX]B
**当前价格：** $[XX.XX]

**估值指标：**
- 股息收益率：[X.X]%
- P/E比率：[XX.X]
- P/B比率：[X.X]

**3年增长概况：**
- 股息CAGR：[X.X]% [✓ 持续增长 / ⚠ 一次削减]
- 收入CAGR：[X.X]%
- EPS CAGR：[X.X]%

**股息可持续性：**
- 派息比率：[XX]%
- 自由现金流派息比率：[XX]%
- 状态：[✓ 可持续 / ⚠ 关注 / ❌ 风险]

**财务健康状况：**
- 负债权益比：[X.XX]
- 流动比率：[X.XX]
- 状态：[✓ 健康 / ⚠ 注意]

**质量指标：**
- ROE：[XX]%
- 净利润率：[XX]%
- 质量分数：[XX]/100

**投资考虑：**
- [关键优势1]
- [关键优势2]
- [风险因素或考虑]

---

[重复其他前几只股票]

---

## 投资组合构建指导

**多元化建议：**
- 前20只结果的行业分布
- 建议的配置策略
- 集中风险警告

**监控建议：**
- 每季度跟踪的关键指标
- 每个头寸的警告信号
- 再平衡触发器

**风险考虑：**
- 市值集中度
- 结果中的行业偏差
- 经济敏感性警告
```

### 第5步：提供背景和方法论

在解释结果时参考筛选方法论：

**需要解释的关键概念：**
- 为什么这些特定阈值（3.5%收益率，P/E 20，P/B 2）
- 股息增长与静态高收益的重要性
- 综合分数如何平衡价值、增长和质量
- 股息可持续性与股息陷阱的区别
- 财务健康指标的重要性

加载`references/screening_methodology.md`以提供以下详细解释：
- 阶段1：初始量化筛选
- 阶段2：增长质量筛选
- 阶段3：可持续性和质量分析
- 综合评分系统
- 投资理念和局限性

### 第6步：回答后续问题

预见常见的用户问题：

**"为什么[TICKER]没有上榜？"**
- 检查它未通过哪些标准（收益率、估值、增长、可持续性）
- 解释排除了它的具体筛选标准

**"我可以筛选特定行业吗？"**
- 脚本中存在过滤功能（修改行383-388）
- 建议使用行业参数重新运行

**"如果我想要更高/更低的收益率阈值怎么办？"**
- 脚本参数是可调整的
- 收益率与增长之间的权衡
- 建议使用新参数重新筛选

**"我应该多久重新运行这个筛选？"**
- 建议每季度一次（与盈利周期一致）
- 对于长期持有者，半年一次足够
- 市场状况可能需要更频繁的检查

**"我应该购买多少只股票？"**
- 多元化指导：股息投资组合至少10-15只
- 行业平衡考虑
- 基于风险承受能力确定头寸大小

## 资源

### scripts/screen_dividend_stocks.py

全面的筛选脚本，执行以下操作：
- 使用FMP API获取数据
- 实现多阶段过滤逻辑
- 计算3年期间的CAGR增长率
- 通过派息比率和自由现金流覆盖率评估股息可持续性
- 评估财务健康（负债权益比、流动比率）
- 计算质量分数（ROE、利润率）
- 按综合评分系统对股票进行排名
- 输出结构化的JSON结果

**依赖项：** `requests`库（通过`pip install requests`安装）

**速率限制：** 内置延迟以尊重FMP API限制（免费层每天250个请求）

**错误处理：** 对缺失数据、速率限制重试、API错误进行优雅降级

### references/screening_methodology.md

筛选方法的全面文档：

**阶段1：初始量化筛选**
- 股息收益率≥3.5%的合理性和计算
- P/E比率≤20的阈值论证
- P/B比率≤2的估值逻辑

**阶段2：增长质量筛选**
- 股息增长（3年CAGR≥5%）
- 收入正增长分析
- EPS正增长分析

**阶段3：质量与可持续性分析**
- 股息可持续性指标（派息比率、自由现金流覆盖率）
- 财务健康指标（D/E、流动比率）
- 质量评分方法（ROE、利润率）

**综合评分系统（0-100分）**
- 分数组件分解和权重
- 解释指南

**投资理念**
- 为什么这种方法有效
- 避免的内容（股息陷阱、价值陷阱）
- 理想候选者特征

**使用说明和局限性**
- 投资组合构建的最佳实践
- 出售标准
- 阈值选择的背景

### references/fmp_api_guide.md

Financial Modeling Prep API的完整指南：

**API密钥设置**
- 获取免费API密钥
- 设置环境变量
- 免费层限制（每天250个请求）

**使用的关键端点**
- 股票筛选器API
- 收入报表API
- 资产负债表API
- 现金流量表API
- 关键指标API
- 历史股息API

**速率限制策略**
- 脚本中的内置保护
- 请求预算管理
- 免费层最佳实践

**错误处理**
- 常见错误和解决方案
- 调试技术

**数据质量考虑**
- 数据新鲜度和缺失数据
- 数据准确性注意事项
- 需要验证SEC文件的情况

## 高级用法

### 自定义筛选标准

修改`scripts/screen_dividend_stocks.py`中的阈值：

**行383-388** - 初始筛选参数：
```python
candidates = client.screen_stocks(
    dividend_yield_min=3.5,  # 调整收益率阈值
    pe_max=20,               # 调整P/E阈值
    pb_max=2,                # 调整P/B阈值
    market_cap_min=2_000_000_000  # 最小市值$2B
)
```

**行423** - 股息CAGR阈值：
```python
if not div_cagr or div_cagr < 5.0:  # 调整增长阈值
```

### 特定行业筛选

在初始筛选后添加行业过滤：

```python
# 筛选特定行业
目标行业 = ['消费品防御性', '公用事业', '医疗保健']
candidates = [s for s in candidates if s.get('sector') in target_sectors]
```

### 排除REITs和金融股

REITs和金融股票具有不同的股息特征（更高的派息率，不同的指标）：

```python
# 排除REITs和金融股
排除行业 = ['房地产', '金融服务']
candidates = [s for s in candidates if s.get('sector') not in exclude_sectors]
```

### 导出为CSV

将JSON结果转换为CSV以进行Excel分析：

```python
import json
import csv

with open('dividend_screener_results.json', 'r') as f:
    data = json.load(f)

stocks = data['stocks']

with open('screening_results.csv', 'w', newline='') as csvfile:
    if stocks:
        fieldnames = stocks[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stocks)
```

## 故障排除

### "ERROR: requests library not found"
**解决方案：** 安装requests库
```bash
pip install requests
```

### "ERROR: FMP API key required"
**解决方案：** 设置环境变量或通过命令行提供
```bash
export FMP_API_KEY=your_key_here
# OR
python3 scripts/screen_dividend_stocks.py --fmp-api-key your_key_here
```

### "ERROR: FINVIZ API key required when using --use-finviz"
**解决方案：** 设置环境变量或通过命令行提供
```bash
export FINVIZ_API_KEY=your_key_here
# OR
python3 scripts/screen_dividend_stocks.py --use-finviz --finviz-api-key your_key_here
```

**注意：** 需要FINVIZ Elite订阅（约每月40美元或每年330美元）

### "ERROR: FINVIZ API认证失败"
**可能原因：**
1. 无效的FINVIZ API密钥
2. FINVIZ Elite订阅已过期
3. API密钥格式不正确

**解决方案：**
- 验证FINVIZ Elite订阅是否有效
- 检查API密钥是否有拼写错误（应为字母数字字符串）
- 登录FINVIZ Elite账户并在设置中验证API密钥
- 尝试手动访问FINVIZ Elite筛选器以确认订阅

### "ERROR: FINVIZ预筛选失败或返回无结果"
**可能原因：**
1. FINVIZ API连接问题
2. 筛选标准过于严格（没有股票匹配）
3. 市场状况（熊市可能产生较少结果）

**解决方案：**
- 检查网络连接
- 验证FINVIZ Elite网站是否可访问
- 尝试使用FMP方法作为后备：
  ```bash
  python3 scripts/screen_dividend_stocks.py
  ```

### "WARNING: 速率限制超出"
**解决方案：** 脚本自动在60秒后重试。如果持续存在：
- 等待直到第二天（免费层每天重置）
- 减少分析的股票数量（修改行394限制）
- 考虑升级到FMP付费层

### "没有股票符合所有标准"
**解决方案：** 标准可能过于严格
- 放宽P/E阈值（从20提高）
- 降低股息收益率要求（从3.5%降低）
- 降低股息增长要求（从5%降低）
- 检查市场状况（熊市可能没有合格者）

### 脚本运行缓慢
**预期行为：** 脚本包含0.3秒的延迟以尊重FMP API限制（免费层每天250个请求）
- 100只股票分析 = ~8-10分钟
- 前20-30只合格股票通常在分析前50-70只时找到

## 性能和成本优化

### API调用比较

**两阶段筛选（FINVIZ + FMP）：**
- FINVIZ：1个API调用
- FMP报价API：~30-50个调用（每个预筛选符号一个）
- FMP财务数据：~150-250个调用（5个端点×30-50个符号）
- **总FMP调用：~180-300**

**仅使用FMP筛选：**
- FMP股票筛选器：1个调用（返回100-1000只股票）
- FMP财务数据：~500-5000个调用（5个端点×100-1000个符号）
- **总FMP调用：~500-5000**

**节省：60-94%的FMP API使用量**

### 成本分析

**FINVIZ Elite：**
- 每月：$39.50
- 每年：$299.50（约每月$24.96）

**FMP API：**
- 免费层：每天250个调用（两阶段筛选足够）
- 启动层：每月$29.99（每天750个调用）
- 专业层：每月$79.99（每天2000个调用）

**建议：**
- **对于免费FMP层用户**：使用两阶段筛选（FINVIZ + FMP免费层）
- **对于付费FMP层用户**：两种方法均可；两阶段更快
- **预算选项**：免费FMP层（每几天运行一次）
- **最佳选项**：FINVIZ Elite（$330/年）+ FMP免费层（完整解决方案）

## 版本历史

- **v1.1**（2025年11月）：添加FINVIZ Elite集成以实现两阶段筛选
- **v1.0**（2025年11月）：初始发布，具有全面的多阶段筛选
