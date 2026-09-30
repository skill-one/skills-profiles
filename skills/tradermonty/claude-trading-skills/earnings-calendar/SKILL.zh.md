---
name: earnings-calendar
description: 此技能通过Financial Modeling Prep (FMP) API获取美国股票的即将发布的盈利公告。当用户请求盈利日历数据、想知道哪些公司在未来一周发布盈利，或需要每周盈利回顾时，请使用此技能。该技能专注于市值超过20亿美元的中小型企业（中大型企业），这些企业具有显著的市场影响力，并将数据按日期和时间以清晰的Markdown表格格式组织。支持多种环境（CLI、桌面、网页），并提供灵活的API密钥管理。
---

# 财报日历

## 概述

本技能使用 Financial Modeling Prep (FMP) API 检索即将发布的美国股票财报公告。它重点关注市值较大（中大盘及以上，超过 20 亿美元）的公司，这些公司可能对市场走势产生影响。该技能会生成组织有序的 markdown 报告，展示未来一周哪些公司将发布财报，并按日期和发布时间（开盘前、收盘后或时间未公布）进行分组。

**主要功能**：
- 使用 FMP API 获取可靠且结构化的财报数据
- 按市值（>20 亿美元）筛选，聚焦于可能影响市场的公司
- 包含每股收益（EPS）和营收预估数据
- 多环境支持（CLI、桌面端、Web）
- 灵活的 API 密钥管理
- 按日期、发布时间和市值排序

## 先决条件

### FMP API 密钥

本技能需要 Financial Modeling Prep API 密钥。

**获取免费 API 密钥**：
1. 访问：https://site.financialmodelingprep.com/developer/docs
2. 注册免费账户
3. 立即获得 API 密钥
4. 免费套餐：每天 250 次 API 调用（足够用于每周财报日历）

**按环境设置 API 密钥**：

**Claude Code (CLI)**：
```bash
export FMP_API_KEY="your-api-key-here"
```

**Claude Desktop**：
在系统中设置环境变量，或配置 MCP 服务器。

**Claude Web**：
在执行技能时将要求提供 API 密钥（仅存储于当前会话）。

## 核心工作流程

### 步骤 1：获取当前日期并计算目标周

**关键**：始终从获取准确的当前日期开始。

获取当前日期和时间：
- 使用系统日期/时间获取今天的日期
- 注意：“今天的日期”在环境中提供（<env> 标签）
- 计算目标周：从当前日期起的未来 7 天

**日期范围计算**：
```
当前日期：[例如，2025 年 11 月 2 日]
目标周开始：[当前日期 + 1 天，例如，2025 年 11 月 3 日]
目标周结束：[当前日期 + 7 天，例如，2025 年 11 月 9 日]
```

**为何重要**：
- 财报日历具有时间敏感性
- “下一周”必须根据实际当前日期计算
- 为 API 请求提供准确的日期范围

**日期格式使用 YYYY-MM-DD** 以兼容 API。

### 步骤 2：加载 FMP API 指南

在检索数据之前，加载全面的 FMP API 指南：

```
读取：references/fmp_api_guide.md
```

该指南包含：
- FMP API 端点结构和参数
- 身份验证要求
- 市值筛选策略（通过 Company Profile API）
- 财报发布时间约定（BMO、AMC、TAS）
- 响应格式和字段说明
- 错误处理策略
- 最佳实践和优化技巧

### 步骤 3：API 密钥检测与配置

根据环境检测 API 密钥的可用性。

**多环境 API 密钥检测**：

#### 3.1 检查环境变量 (CLI/桌面端)

```bash
if [ ! -z "$FMP_API_KEY" ]; then
  echo "✓ 在环境中找到 API 密钥"
  API_KEY=$FMP_API_KEY
fi
```

如果已设置环境变量，请继续步骤 4。

#### 3.2 提示用户输入 API 密钥 (桌面端/Web)

如果未找到环境变量，请使用 AskUserQuestion 工具：

**问题配置**：
```
问题：“本技能需要 FMP API 密钥以检索财报数据。您是否有 FMP API 密钥？”
标题：“API 密钥”
选项：
  1. “有，我现在提供” → 继续到 3.3
  2. “没有，获取免费密钥” → 显示说明 (3.2.1)
  3. “跳过 API，使用手动输入” → 跳转到步骤 8（回退模式）
```

**3.2.1 如果用户选择“没有，获取免费密钥”**：

提供说明：
```
要获取免费的 FMP API 密钥：

1. 访问：https://site.financialmodelingprep.com/developer/docs
2. 点击“获取免费 API 密钥”或“注册”
3. 创建账户（电子邮件 + 密码）
4. 立即获得 API 密钥
5. 免费套餐包含每天 250 次 API 调用（足以满足日常使用）

一旦您拥有 API 密钥，请选择“有，我现在提供”以继续。
```

#### 3.3 请求输入 API 密钥

如果用户拥有 API 密钥，请求输入：

**提示**：
```
请在下方粘贴您的 FMP API 密钥：

（您的 API 密钥仅存储于本次对话会话中，会话结束后将被遗忘。如需常规使用，建议设置 FMP_API_KEY 环境变量。）
```

**将 API 密钥存储到会话变量中**：
```
API_KEY = [用户输入]
```

**与用户确认**：
```
✓ 已接收 API 密钥并存储于本会话。

安全说明：
- API 密钥仅存储于当前对话上下文中
- 不会保存到磁盘或持久存储
- 会话结束后将被遗忘
- 如果对话包含您的 API 密钥，请勿分享该对话

正在继续检索财报数据...
```

### 步骤 4：通过 FMP API 检索财报数据

使用 Python 脚本从 FMP API 获取财报数据。

**脚本位置**：
```
scripts/fetch_earnings_fmp.py
```

**执行**：

**选项 A：使用环境变量 (CLI)**：
```bash
python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09
```

**选项 B：使用会话 API 密钥 (桌面端/Web)**：
```bash
python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09 "${API_KEY}"
```

**脚本工作流程**（自动）：
1. 验证 API 密钥和日期参数
2. 针对日期范围调用 FMP Earnings Calendar API
3. 获取公司档案（市值、部门、行业）
4. 筛选市值 >20 亿美元的公司
5. 标准化发布时间（BMO/AMC/TAS）
6. 按日期 → 发布时间 → 市值（降序）排序
7. 将 JSON 输出到标准输出

**预期输出格式**（JSON）：
```json
[
  {
    "symbol": "AAPL",
    "companyName": "Apple Inc.",
    "date": "2025-11-04",
    "timing": "AMC",
    "marketCap": 3000000000000,
    "marketCapFormatted": "$3.0T",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "epsEstimated": 1.54,
    "revenueEstimated": 123400000000,
    "fiscalDateEnding": "2025-09-30",
    "exchange": "NASDAQ"
  },
  ...
]
```

**保存到文件**（推荐用于与报告生成器配合使用）：
```bash
python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09 "${API_KEY}" > earnings_data.json
```

或捕获到变量：
```bash
earnings_data=$(python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09 "${API_KEY}")
```

**错误处理**：

如果脚本返回错误：
- **401 未授权**：API 密钥无效 → 验证密钥或重新输入
- **429 速率限制**：超过每天 250 次调用 → 等待或升级套餐
- **空结果**：日期范围内没有财报 → 扩大日期范围或在报告中注明
- **连接错误**：网络问题 → 重试或使用可用的缓存数据

### 步骤 5：处理和组织数据

检索到财报数据（JSON 格式）后，对其进行处理和组织：

#### 5.1 解析 JSON 数据

从脚本输出加载 JSON 数据：
```python
import json
earnings_data = json.loads(earnings_json_string)
```

如果已保存到文件：
```python
with open('earnings_data.json', 'r') as f:
    earnings_data = json.load(f)
```

#### 5.2 验证数据结构

确认数据包含必需字段：
- ✓ symbol
- ✓ companyName
- ✓ date
- ✓ timing (BMO/AMC/TAS)
- ✓ marketCap
- ✓ sector

#### 5.3 按日期分组

将所有财报公告按日期分组：
- 周日，[完整日期]（如适用）
- 周一，[完整日期]
- 周二，[完整日期]
- 周三，[完整日期]
- 周四，[完整日期]
- 周五，[完整日期]
- 周六，[完整日期]（如适用）

#### 5.4 按发布时间子分组

在每个日期内，创建三个子部分：
1. **开盘前 (BMO)**
2. **收盘后 (AMC)**
3. **时间未公布 (TAS)**

数据已从脚本中按发布时间排序，因此请保持此顺序。

#### 5.5 每个发布时间组内

公司已按市值降序排序（脚本输出）：
- 超大盘（>2000 亿美元）排第一
- 大盘（100 亿-2000 亿美元）排第二
- 中盘（20 亿-100 亿美元）排第三

此优先级确保最先列出对市场影响最大的公司。

#### 5.6 计算摘要统计

计算：
- **公司总数**：数据集中所有公司的数量
- **超大盘/大盘数量**：市值 >= 100 亿美元的数量
- **中盘数量**：市值在 20 亿至 100 亿美元之间的数量
- **高峰期**：财报公告数量最多的星期几
- **部门分布**：按部门计数（科技、医疗、金融等）
- **市值最高公司**：按市值排名的前 5 家公司

### 步骤 6：生成 Markdown 报告

使用报告生成脚本从 JSON 数据创建格式化的 markdown 报告。

**脚本位置**：
```
scripts/generate_report.py
```

**执行**：

**选项 A：输出到标准输出**：
```bash
python scripts/generate_report.py earnings_data.json
```

**选项 B：保存到文件**：
```bash
python scripts/generate_report.py earnings_data.json earnings_calendar_2025-11-02.md
```

**脚本的功能**：
1. 从 JSON 文件加载财报数据
2. 按日期和发布时间（BMO/AMC/TAS）分组
3. 在每个组内按市值排序
4. 计算摘要统计
5. 生成格式化的 markdown 报告
6. 输出到标准输出或保存到文件

脚本自动处理所有格式，包括：
- 正确的 markdown 表格结构
- 日期分组和星期名称
- 市值排序
- EPS 和营收格式化
- 摘要统计计算

**报告结构**：

```markdown
# 即将发布的财报日历 - 第 [START_DATE] 至 [END_DATE] 周

**报告生成日期**：[当前日期]
**数据来源**：FMP API（中盘及以上，市值 >20 亿美元）
**覆盖范围**：未来 7 天
**公司总数**：[COUNT]

---

## 执行摘要

- **发布财报的公司总数**：[TOTAL_COUNT]
- **超大盘/大盘 (>100 亿美元)**：[LARGE_CAP_COUNT]
- **中盘 (20 亿-100 亿美元)**：[MID_CAP_COUNT]
- **高峰期**：[DAY_WITH_MOST_EARNINGS]

---

## [星期几], [完整日期]

### 开盘前 (BMO)

| 代码 | 公司 | 市值 | 部门 | EPS 预估 | 营收预估 |
|--------|---------|------------|--------|----------|--------------|
| [TICKER] | [COMPANY] | [MCAP] | [SECTOR] | [EPS] | [REV] |

### 收盘后 (AMC)

| 代码 | 公司 | 市值 | 部门 | EPS 预估 | 营收预估 |
|--------|---------|------------|--------|----------|--------------|
| [TICKER] | [COMPANY] | [MCAP] | [SECTOR] | [EPS] | [REV] |

### 时间未公布 (TAS)

| 代码 | 公司 | 市值 | 部门 | EPS 预估 | 营收预估 |
|--------|---------|------------|--------|----------|--------------|
| [TICKER] | [COMPANY] | [MCAP] | [SECTOR] | [EPS] | [REV] |

---

[对每周中的每一天重复]

---

## 关键观察

### 本周市值最高的公司
1. [COMPANY] ([TICKER]) - [MCAP] - [DATE] [TIME]
2. [COMPANY] ([TICKER]) - [MCAP] - [DATE] [TIME]
3. [COMPANY] ([TICKER]) - [MCAP] - [DATE] [TIME]

### 部门分布
- **科技**：[COUNT] 家公司
- **医疗**：[COUNT] 家公司
- **金融**：[COUNT] 家公司
- **消费**：[COUNT] 家公司
- **其他**：[COUNT] 家公司

### 交易考量
- **交易量大的日子**：[有多个大盘财报的 DATES]
- **盘前关注点**：[可能影响市场的 BMO 公司]
- **盘后关注点**：[可能影响市场的 AMC 公司]

---

## 发布时间参考

- **BMO (开盘前)**：公告通常在美东时间上午 6:00-8:00，即市场于美东时间上午 9:30 开盘之前
- **AMC (收盘后)**：公告通常在美东时间下午 4:00-5:00，即市场于美东时间下午 4:00 收盘之后
- **TAS (时间未公布)**：具体时间尚未披露 - 请关注公司投资者关系信息

---

## 数据说明

- **市值类别**：
  - 超大盘：>2000 亿美元
  - 大盘：100 亿-2000 亿美元
  - 中盘：20 亿-100 亿美元

- **筛选标准**：本报告包含市值在 20 亿美元及以上（中盘+）且未来一周安排发布财报的公司。

- **数据来源**：Financial Modeling Prep (FMP) API

- **数据新鲜度**：财报日期和时间可能会变化。请通过公司投资者关系网站核实关键日期以获取最新信息。

- **EPS 和营收预估**：来自 FMP API 的分析师共识预估。实际结果将在财报发布日期公布。

---

## 其他资源

- **FMP API 文档**：https://site.financialmodelingprep.com/developer/docs
- **Seeking Alpha 日历**：https://seekingalpha.com/earnings/earnings-calendar
- **Yahoo Finance 日历**：https://finance.yahoo.com/calendar/earnings

---

*报告使用 FMP Earnings Calendar API 及中盘+过滤器（市值 >20 亿美元）生成。数据截至报告生成时间有效。请始终通过官方公司渠道核实财报日期。*
```

**格式化最佳实践**：
- 使用 markdown 表格以清晰展示
- 如有需要，将重要公司名称（超大盘）加粗
- 以人类可读格式包含市值（$3.0T、$150B、$5.2B）- 已由脚本格式化
- 按日期然后按发布时间逻辑分组
- 在顶部包含摘要部分以便快速概览
- 如果可用，包含 EPS 和营收预估

### 步骤 7：质量保证

在最终确定报告之前，请验证：

**数据质量检查**：
1. ✓ 所有日期均落在目标周（未来 7 天）内
2. ✓ 所有公司均有市值数值
3. ✓ 每家公司都指定了发布时间（BMO/AMC/TAS）
4. ✓ 公司在每个部分中按市值排序
5. ✓ 摘要统计准确
6. ✓ 报告生成日期明确陈述
7. ✓ 包含可用的 EPS 和营收预估

**完整性检查**：
1. ✓ 包含目标周的所有天（即使没有财报）
2. ✓ 未遗漏已知的重大公司（如有必要，请对照外部来源验证）
3. ✓ 在可用时包含部门信息
4. ✓ 存在发布时间参考部分
5. ✓ 标明数据来源（FMP API）

**格式检查**：
1. ✓ Markdown 表格格式正确
2. ✓ 日期格式一致
3. ✓ 市值使用一致的计量单位（B 代表十亿，T 代表万亿）
4. ✓ 所有部分遵循模板结构
5. ✓ 没有保留占位符文本 ([PLACEHOLDER])
6. ✓ EPS 和营收预估格式正确

### 步骤 8：保存并交付报告

使用适当的文件名保存生成的报告：

**文件名约定**：
```
earnings_calendar_[YYYY-MM-DD].md
```

示例：`earnings_calendar_2025-11-02.md`

文件名中的日期代表报告生成日期，而非财报周。

**交付**：
- 将 markdown 文件保存到工作目录
- 通知用户报告已生成
- 提供主要发现的简要总结（例如，“下一周有 45 家公司发布财报，周一有 Apple 和 Microsoft”）

**示例总结**：
```
✓ 财报日历报告已生成：earnings_calendar_2025-11-02.md

2025 年 11 月 3 日至 9 日当周的总结：
- 45 家公司发布财报
- 28 家大型/超大型，17 家中型
- 高峰期：周四（15 家公司）
- 值得注意：Apple（周一 AMC）、Microsoft（周二 AMC）、Tesla（周三 AMC）

按市值排名前 5：
1. Apple - $3.0T（周一 AMC）
2. Microsoft - $2.8T（周二 AMC）
3. Alphabet - $1.8T（周四 AMC）
4. Amazon - $1.6T（周五 AMC）
5. Tesla - $800B（周三 AMC）
```

## 回退模式（步骤 8 替代方案）：手动数据录入

如果 API 访问不可用或用户选择跳过 API：

**提供手动录入说明**：

```
由于 FMP API 不可用，您可以手动收集财报数据：

1. 访问 Finviz：https://finviz.com/screener.ashx?v=111&f=cap_midover%2Cearningsdate_nextweek
2. 或 Yahoo Finance：https://finance.yahoo.com/calendar/earnings
3. 记下下一周发布财报的公司

请为每家公司提供以下信息：
- 股票代码
- 公司名称
- 财报日期
- 发布时间（BMO/AMC/TAS）
- 市值（近似值）
- 部门

我将把它格式化为标准的财报日历报告。
```

**处理手动输入**：
1. 解析用户提供的财报数据
2. 按日期、发布时间和市值组织
3. 使用相同的模板生成报告
4. 在报告中注明：“数据来源：手动录入”

## 用例和示例

### 用例 1：每周回顾（主要用例）

**用户请求**：“获取下一周的财报日历”

**工作流程**：
1. 获取当前日期（例如：2025年11月2日）
2. 计算目标周（例如：2025年11月3日至9日）
3. 加载FMP API指南
4. 检测/请求API密钥
5. 获取盈利数据：
   ```bash
   python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09 > earnings_data.json
   ```
6. 生成markdown报告：
   ```bash
   python scripts/generate_report.py earnings_data.json earnings_calendar_2025-11-02.md
   ```
7. 通知用户总结

**一键完成**：
```bash
python scripts/fetch_earnings_fmp.py 2025-11-03 2025-11-09 > earnings_data.json && \
python scripts/generate_report.py earnings_data.json earnings_calendar_2025-11-02.md
```

### 用例2：聚焦特定日期

**用户请求**："周一有哪些盈利发布？"

**工作流程**：
1. 获取当前日期并确定下一个周一（例如：2025年11月4日）
2. 获取整周数据（与用例1相同）
3. 生成完整报告但突出显示周一部分
4. 提供周一盈利的口头总结并强调重点

### 用例3：超级市值聚焦

**用户请求**："下周市值超过1000亿美元的公司盈利情况"

**工作流程**：
1. 获取完整盈利数据（脚本已过滤>200亿美元）
2. 正常处理和整理
3. 生成报告时，在顶部添加"超级市值聚焦"部分
4. 筛选表格仅显示市值>1000亿美元的公司
5. 注意：仍将完整数据包含在附录中供参考

### 用例4：行业特定

**用户请求**："下周有哪些科技公司盈利？"

**工作流程**：
1. 获取完整盈利数据
2. 正常处理和整理
3. 按行业筛选结果（行业=“科技”）
4. 生成报告聚焦科技行业
5. 注意：模板结构保持不变；内容被筛选

## 故障排除

### 问题：API密钥无效

**解决方案**：
- 验证API密钥是否正确（小心复制粘贴）
- 检查API密钥是否激活（登录FMP控制面板）
- 确保密钥前后没有多余空格
- 尝试从FMP控制面板生成新API密钥

### 问题：脚本返回空结果

**解决方案**：
- 验证日期范围是否为未来日期（不是过去日期）
- 检查日期格式是否为YYYY-MM-DD
- 尝试更宽泛的日期范围（例如：14天而不是7天）
- 验证这些公司确实宣布了该周的盈利日期

### 问题：遗漏主要公司

**解决方案**：
- 公司可能尚未宣布盈利日期
- 某些公司宣布日期非常晚（提前1-2天）
- 与公司投资者关系网站交叉核对
- 市值可能已低于200亿美元门槛

### 问题：达到速率限制（429错误）

**解决方案**：
- 免费套餐：每天250次调用
- 每个周报告使用~3-5次API调用
- 检查其他工具/脚本是否使用相同API密钥
- 等待24小时重置速率限制
- 如需频繁使用，考虑升级到付费套餐

### 问题：脚本执行错误

**解决方案**：
- 验证已安装Python 3：`python3 --version`
- 安装requests库：`pip install requests`
- 检查脚本具有执行权限：`chmod +x fetch_earnings_fmp.py`
- 明确使用python3运行：`python3 fetch_earnings_fmp.py ...`

## 最佳实践

### 应做事项
✓ 首先获取当前日期再进行任何数据检索
✓ 使用FMP API作为主要来源以确保可靠性
✓ 将API密钥存储在环境变量中用于CLI使用
✓ 按市值排序以优先处理高影响力公司
✓ 按日期和时间分组进行逻辑组织
✓ 包含摘要统计数据供快速概览
✓ 在报告页脚注明数据来源
✓ 使用干净的markdown表格提高可读性
✓ 提供时间参考部分以增强清晰度
✓ 注明数据新鲜度及可能的变化
✓ 当可用时包含EPS和收入预估

### 不应做事项
✗ 不计算当前日期就假设“下周”
✗ 不包含时间信息（BMO/AMC/TAS）
✗ 报告中混合日期格式（保持一致）
✗ 除非特别请求，否则不包含微型/小型市值公司
✗ 在各部分内按市值排序
✗ 不要在对话或报告中分享API密钥
✗ 不包含当前周或过去日期的盈利
✗ 未经质量保证检查不生成报告
✗ 不要将API密钥提交到版本控制

## 安全注意事项

### API密钥安全

**重要提醒**：
1. ✓ 测试时使用免费套餐API密钥
2. ✓ 定期轮换密钥
3. ✓ 不要在对话中分享包含API密钥的内容
4. ✓ 将API密钥设置为环境变量用于CLI
5. ✗ 会话中提供的密钥仅限当前会话（会话结束后忘记）
6. ✗ 永远不要将API密钥提交到Git仓库
7. ✗ 永远不要用生产API密钥访问敏感数据

**最佳实践**：
对于Claude Code（CLI），始终使用环境变量：
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export FMP_API_KEY="your-key-here"
```

对于Claude Web，理解：
- 在聊天中输入的API密钥是临时的
- 仅存储在对话上下文中
- 不会保存到磁盘
- 会话结束后忘记

## 资源

**FMP API**：
- 主文档：https://site.financialmodelingprep.com/developer/docs
- 获取API密钥：https://site.financialmodelingprep.com/developer/docs
- 盈利日历API：https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api
- 公司概况API：https://site.financialmodelingprep.com/developer/docs/companies-key-metrics-api
- 定价/速率限制：https://site.financialmodelingprep.com/developer/docs/pricing

**补充来源**（用于验证）：
- Seeking Alpha：https://seekingalpha.com/earnings/earnings-calendar
- Yahoo Finance：https://finance.yahoo.com/calendar/earnings
- MarketWatch：https://www.marketwatch.com/tools/earnings-calendar

**技能资源**：
- FMP API指南：`references/fmp_api_guide.md`
- Python脚本：`scripts/fetch_earnings_fmp.py`
- 报告模板：`assets/earnings_report_template.md`

---

## 总结

此技能提供了一种可靠、API驱动的生成美国股票周盈利日历的方法。通过使用FMP API，它确保了结构化、准确的数据，并附加了EPS/收入预估等额外见解。多环境支持使其适用于CLI、桌面和Web使用，而备用模式确保即使没有API访问权限也能正常工作。

**关键工作流程**：日期计算 → API密钥设置 → API数据检索 → 处理 → 报告生成 → 质量保证 → 交付

**输出**：干净、有组织的markdown报告，按日期/时间/市值分组盈利，包括摘要统计数据和交易考虑。
