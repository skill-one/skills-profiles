---
name: value-dividend-screener
description: 筛选美国股市的高质量股息机会，结合价值特征（市盈率低于20，市净率低于2）、有吸引力的收益率（3%或更高）以及持续增长（股息/营收/每股收益在过去3年内呈上升趋势）。支持使用FINVIZ Elite API进行两阶段筛选，先进行高效预筛选，再使用FMP API进行详细分析。当用户请求股息股票筛选、收入投资组合建议或基本面强劲的高质量价值股票时使用。
---

# 价值股息筛选器

## 概述

该技能使用**两阶段筛选方法**识别结合价值特征、吸引人收入生成和持续增长的高质量股息股票：

1. **FINVIZ 卓越 API（可选但推荐）**：使用基本标准预筛选股票（快速、经济高效）
2. **财务建模准备（FMP）API**：对候选股票进行详细的财务分析

基于估值比率、股息指标、财务健康状况和盈利能力的量化标准筛选美国股票。生成综合质量评分排名的股票报告，并提供详细的财务分析。

**效率优势**：使用 FINVIZ 预筛选可减少 FMP API 调用 90%，使这种方法成为免费套餐 API 用户的首选。

## 使用场景

当用户请求以下内容时，调用此技能：

- "寻找高质量股息股票"
- "筛选价值股息机会"
- "显示股息增长强劲的股票"
- "寻找合理估值的收入股票"
- "筛选可持续的高收益股票"
- 任何结合股息收益率、估值指标和基本面分析的请求

## 工作流程

### 第 1 步：验证 API 密钥可用性

**对于两阶段筛选（推荐）**：

检查两个 API 密钥是否可用：

```python
import os
fmp_api_key = os.environ.get('FMP_API_KEY')
finviz_api_key = os.environ.get('FINVIZ_API_KEY')
```

如果不可用，请要求用户提供 API 密钥或设置环境变量：
```bash
export FMP_API_KEY=your_fmp_key_here
export FINVIZ_API_KEY=your_finviz_key_here
```

**对于仅 FMP 筛选**：

检查 FMP API 密钥是否可用：

```python
import os
api_key = os.environ.get('FMP_API_KEY')
```

如果不可用，请要求用户提供 API 密钥或设置环境变量：
```bash
export FMP_API_KEY=your_key_here
```

**FINVIZ 卓越 API 密钥**：
- 需要 FINVIZ 卓越订阅（约每月 40 美元或每年 330 美元）
- 提供预筛选结果的 CSV 导出访问权限
- 强烈推荐以减少 FMP API 使用

如有需要，可提供 `references/fmp_api_guide.md` 中的说明。

### 第 2 步：执行筛选脚本

使用适当的参数运行筛选脚本：

#### **两阶段筛选（推荐）**

使用 FINVIZ 进行预筛选，然后使用 FMP 进行详细分析：

**默认执行（前 20 只股票）**：
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz
```

**使用显式 API 密钥**：
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz \
  --fmp-api-key $FMP_API_KEY \
  --finviz-api-key $FINVIZ_API_KEY
```

**自定义前 N**：
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz --top 50
```

**自定义输出位置**：
```bash
python3 scripts/screen_dividend_stocks.py --use-finviz --output /path/to/results.json
```

**脚本行为（两阶段）**：
1. FINVIZ 卓越预筛选：
   - 市值：中盘或更高
   - 股息收益率：3%+
   - 股息增长（3 年）：5%+
   - EPS 增长（3 年）：正值
   - P/B：低于 2
   - P/E：低于 20
   - 销售增长（3 年）：正值
   - 地理区域：美国
2. FMP 对 FINVIZ 结果进行详细分析（通常 20-50 只股票）：
   - 股息增长率计算（3 年 CAGR）
   - 收入和 EPS 趋势分析
   - 股息可持续性评估（派息比率、自由现金流覆盖率）
   - 财务健康指标（负债权益比、流动比率）
   - 质量评分（ROE、利润率）
3. 综合评分和排名
4. 输出前 N 只股票到 JSON 文件

**预期运行时间（两阶段）**：对 30-50 个 FINVIZ 候选股票进行 2-3 分钟（比仅 FMP 快得多）

#### **仅 FMP 筛选（原始方法）**

仅使用 FMP 股票筛选器 API（API 使用量较高）：

**默认执行**：
```bash
python3 scripts/screen_dividend_stocks.py
```

**使用显式 API 密钥**：
```bash
python3 scripts/screen_dividend_stocks.py --fmp-api-key $FMP_API_KEY
```

**脚本行为（仅 FMP）**：
1. 使用 FMP 股票筛选器 API 进行初始筛选（股息收益率 >=3.0%，P/E <=20，P/B <=2）
2. 对候选股票进行详细分析（通常 100-300 只股票）：
   - 与两阶段方法相同的详细分析
3. 综合评分和排名
4. 输出前 N 只股票到 JSON 文件

**预期运行时间（仅 FMP）**：对 100-300 个候选股票进行 5-15 分钟（适用速率限制）

**API 使用量比较**：
- 两阶段：~50-100 个 FMP API 调用（FINVIZ 预筛选至 ~30 只股票）
- 仅 FMP：~500-1500 个 FMP API 调用（分析所有筛选器结果）

### 第 3 步：解析和分析结果

读取生成的 JSON 文件：

```python
import json

with open('dividend_screener_results.json', 'r') as f:
    data = json.load(f)

metadata = data['metadata']
stocks = data['stocks']
```

**每只股票的关键数据点**：
- 基本信息：`symbol`、`company_name`、`sector`、`market_cap`、`price`
- 估值：`dividend_yield`、`pe_ratio`、`pb_ratio`
- 增长指标：`dividend_cagr_3y`、`revenue_cagr_3y`、`eps_cagr_3y`
- 可持续性：`payout_ratio`、`fcf_payout_ratio`、`dividend_sustainable`
- 财务健康状况：`debt_to_equity`、`current_ratio`、`financially_healthy`
- 质量指标：`roe`、`profit_margin`、`quality_score`
- 整体排名：`composite_score`

### 第 4 步：生成 Markdown 报告

为用户提供结构化的 Markdown 报告，包含以下部分：

#### 报告结构

```markdown
# 价值股息股票筛选报告

**生成时间**：[时间戳]
**筛选标准**：
- 股息收益率：>= 3.5%
- P/E 比率：<= 20
- P/B 比率：<= 2
- 股息增长（3 年 CAGR）：>= 5%
- 收入趋势：3 年内为正值
- EPS 趋势：3 年内为正值

**总结果**：[N] 只股票

---

## 前 20 只按综合评分排名的股票

| 排名 | 符号 | 公司 | 收益率 | P/E | 股息增长 | 分数 |
|------|------|------|-------|-----|------------|-------|
| 1 | [TICKER] | [Name] | [%] | [X.X] | [%] | [XX.X] |
| ... |

---

## 详细分析

### 1. [SYMBOL] - [Company Name] (分数：XX.X)

**行业**：[行业名称]
**市值**：$[X.XX]B
**当前价格**：$[XX.XX]

**估值指标**：
- 股息收益率：[X.X]%
- P/E 比率：[XX.X]
- P/B 比率：[X.X]

**增长概况（3 年）**：
- 股息 CAGR：[X.X]% [✓ 持续增长 / ⚠ 一次削减]
- 收入 CAGR：[X.X]%
- EPS CAGR：[X.X]%

**股息可持续性**：
- 派息比率：[XX]%
- 自由现金流派息比率：[XX]%
- 状态：[✓ 可持续 / ⚠ 关注 / ❌ 风险]

**财务健康状况**：
- 负债权益比：[X.XX]
- 流动比率：[X.XX]
- 状态：[✓ 健康 / ⚠ 注意]

**质量指标**：
- ROE：[XX]%
- 净利润率：[XX]%
- 质量分数：[XX]/100

**投资考虑**：
- [关键优势 1]
- [关键优势 2]
- [风险因素或考虑]

---

[重复其他前几只股票]

---

## 投资组合构建指导

**多元化建议**：
- 前 20 只结果的行业分布
- 建议的配置策略
- 集中风险警告

**监控建议**：
- 每季度跟踪的关键指标
- 每个头寸的警告信号
- 再平衡触发器

**风险考虑**：
- 市值集中度
- 结果中的行业偏差
- 经济敏感性警告

### 第 5 步：提供背景和方法论

在解释结果时参考筛选方法论：

**需要解释的关键概念**：
- 为什么这些特定阈值（3.5% 收益率，P/E 20，P/B 2）
- 股息增长与静态高收益的重要性
- 综合分数如何平衡价值、增长和质量
- 股息可持续性与股息陷阱的区别
- 财务健康指标的重要性

加载 `references/screening_methodology.md` 以提供以下方面的详细解释：
- 阶段 1：初始量化筛选
- 阶段 2：增长质量筛选
- 阶段 3：可持续性和质量分析
- 综合评分系统
- 投资理念和局限性

### 第 6 步：回答后续问题

预见常见的用户问题：

**"为什么 [股票] 没有上榜？"**
- 检查它未通过哪些标准（收益率、估值、增长、可持续性）
- 解释排除了它的特定筛选标准

**"我可以筛选特定行业吗？"**
- 脚本中存在过滤功能（修改第 383-388 行）
- 建议重新运行并添加行业参数

**"如果我想要更高/更低的收益率阈值怎么办？"**
- 脚本参数是可调整的
- 收益率和增长之间的权衡
- 建议使用新参数重新筛选

**"我应该多久重新运行这个筛选？"**
- 建议每季度运行（与盈利周期一致）
- 半年一次对长期持有者足够
- 市场状况可能需要更频繁的检查

**"我应该购买多少只股票？"**
- 多元化指导：股息投资组合至少 10-15 只
- 行业平衡考虑
- 基于风险承受能力确定头寸大小

## 资源

### scripts/screen_dividend_stocks.py

全面的筛选脚本，执行以下操作：
- 使用 FMP API 获取数据
- 实现多阶段过滤逻辑
- 计算 3 年期增长率（CAGR）
- 通过派息比率和自由现金流覆盖率评估股息可持续性
- 评估财务健康状况（负债权益比、流动比率）
- 计算质量分数（ROE、利润率）
- 按综合评分系统对股票进行排名
- 输出结构化 JSON 结果

**依赖项**：`requests` 库（通过 `pip install requests` 安装）

**速率限制**：内置延迟以尊重 FMP API 限制（免费套餐每天 250 个请求）

**错误处理**：对缺失数据、速率限制重试和 API 错误进行优雅降级

### references/screening_methodology.md

筛选方法的全面文档：

**阶段 1：初始量化筛选**
- 股息收益率 >= 3.5% 的合理性和计算
- P/E 比率 <= 20 的阈值理由
- P/B 比率 <= 2 的估值逻辑

**阶段 2：增长质量筛选**
- 股息增长（3 年 CAGR >= 5%）
- 收入正向趋势分析
- EPS 正向趋势分析

**阶段 3：质量和可持续性分析**
- 股息可持续性指标（派息比率、自由现金流覆盖率）
- 财务健康指标（D/E、流动比率）
- 质量评分方法（ROE、利润率）

**综合评分系统（0-100 分）**
- 分数组件分解和权重
- 解释指南

**投资理念**
- 为什么这种方法有效
- 避免的内容（股息陷阱、价值陷阱）
- 理想候选股票特征

**使用说明和局限性**
- 投资组合构建的最佳实践
- 出售标准
- 阈值选择的背景

### references/fmp_api_guide.md

Financial Modeling Prep API 的完整指南：

**API 密钥设置**
- 获取免费 API 密钥
- 设置环境变量
- 免费套餐限制（每天 250 个请求）

**使用的 API 端点**
- 股票筛选器 API
- 收入报表 API
- 资产负债表 API
- 现金流量表 API
- 关键指标 API
- 历史股息 API

**速率限制策略**
- 脚本中的内置保护
- 请求预算管理
- 免费套餐的最佳实践

**错误处理**
- 常见错误和解决方案
- 调试技术

**数据质量考虑**
- 数据新鲜度和缺失数据
- 数据准确性注意事项
- 需要验证美国证券交易委员会报告的情况

## 高级用法

### 自定义筛选标准

修改 `scripts/screen_dividend_stocks.py` 中的阈值：

**第 383-388 行** - 初始筛选参数：
```python
candidates = client.screen_stocks(
    dividend_yield_min=3.5,  # 调整收益率阈值
    pe_max=20,               # 调整 P/E 阈值
    pb_max=2,                # 调整 P/B 阈值
    market_cap_min=2_000_000_000  # 最小市值 $2B
)
```

**第 423 行** - 股息 CAGR 阈值：
```python
if not div_cagr or div_cagr < 5.0:  # 调整增长阈值
```

### 特定行业筛选

在初始筛选后添加行业过滤：

```python
# 筛选特定行业
target_sectors = ['消费防御性', '公用事业', '医疗保健']
candidates = [s for s in candidates if s.get('sector') in target_sectors]
```

### 排除 REITs 和金融股

REITs 和金融股票具有不同的股息特征（更高的派息率，不同的指标）：

```python
# 排除 REITs 和金融股
exclude_sectors = ['房地产', '金融服务']
candidates = [s for s in candidates if s.get('sector') not in exclude_sectors]
```

### 导出为 CSV

将 JSON 结果转换为 CSV 以进行 Excel 分析：

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
**解决方案**：安装 requests 库
```bash
pip install requests
```

### "ERROR: FMP API key required"
**解决方案**：设置环境变量或通过命令行提供
```bash
export FMP_API_KEY=your_key_here
# OR
python3 scripts/screen_dividend_stocks.py --fmp-api-key your_key_here
```

### "ERROR: FINVIZ API key required when using --use-finviz"
**解决方案**：设置环境变量或通过命令行提供
```bash
export FINVIZ_API_KEY=your_key_here
# OR
python3 scripts/screen_dividend_stocks.py --use-finviz --finviz-api-key your_key_here
```

**注意**：需要 FINVIZ 卓越订阅（约每月 40 美元或每年 330 美元）

### "ERROR: FINVIZ API 认证失败"
**可能原因**：
1. 无效的 FINVIZ API 密钥
2. FINVIZ 卓越订阅已过期
3. API 密钥格式不正确

**解决方案**：
- 验证 FINVIZ 卓越订阅是否激活
- 检查 API 密钥是否有拼写错误（应为字母数字字符串）
- 登录 FINVIZ 卓越账户并在设置中验证 API 密钥
- 尝试手动访问 FINVIZ 卓越筛选器以确认订阅

### "ERROR: FINVIZ 预筛选失败或返回无结果"
**可能原因**：
1. FINVIZ API 连接问题
2. 筛选标准过于严格（没有股票匹配）
3. 市场状况（熊市可能产生较少结果）

**解决方案**：
- 检查网络连接
- 验证 FINVIZ 卓越网站是否可访问
- 尝试仅使用 FMP 作为后备方案：
  ```bash
  python3 scripts/screen_dividend_stocks.py
  ```

### "WARNING: 速率限制超出"
**解决方案**：脚本自动在 60 秒后重试。如果仍然存在：
- 等待第二天（免费套餐每天重置）
- 减少分析的股票数量（修改第 394 行限制）
- 考虑升级到 FMP 付费套餐

### "没有股票符合所有标准"
**解决方案**：标准可能过于严格
- 放宽 P/E 阈值（从 20 增加到）
- 降低股息收益率要求（从 3.5% 降低）
- 降低股息增长要求（从 5% 降低）
- 检查市场状况（熊市可能没有合格者）

### 脚本运行缓慢
**预期行为**：脚本包含 0.3 秒的延迟以尊重 FMP API 限制（免费套餐每天 250 个请求）
- 分析 100 只股票 = ~8-10 分钟
- 前 20-30 只合格股票通常在分析的前 50-70 只中找到

## 性能和成本优化

### API 调用比较

**两阶段筛选（FINVIZ + FMP）**：
- FINVIZ：1 个 API 调用
- FMP 股票报价 API：~30-50 个调用（每个预筛选符号一个）
- FMP 财务数据：~150-250 个调用（5 个端点 × 30-50 个符号）
- **总 FMP 调用：~180-300**

**仅 FMP 筛选**：
- FMP 股票筛选器：1 个调用（返回 100-1000 只股票）
- FMP 财务数据：~500-5000 个调用（5 个端点 × 100-1000 个符号）
- **总 FMP 调用：~500-5000**

**节省：60-94% 的 FMP API 使用量**

### 成本分析

**FINVIZ 卓越**：
- 每月：$39.50
- 每年：$299.50 (~$24.96/月)

**FMP API**：
- 免费套餐：每天 250 个调用（两阶段筛选足够）
- 启动套餐：每月 $29.99，每天 750 个调用
- 专业套餐：每月 $79.99，每天 2000 个调用

**推荐方案：**
- **免费 FMP 层用户**：使用两阶段筛选（FINVIZ + FMP 免费层）
- **付费 FMP 层用户**：两种方法均可；两阶段更快
- **预算方案**：仅使用 FMP 免费层（每隔几天运行一次筛选）
- **最佳方案**：FINVIZ Elite（每年 330 美元）+ FMP 免费层 = 完整解决方案

## 版本历史

- **v1.1**（2025 年 11 月）：添加了用于两阶段筛选的 FINVIZ Elite 集成
- **v1.0**（2025 年 11 月）：初始版本，包含全面的多阶段筛选
