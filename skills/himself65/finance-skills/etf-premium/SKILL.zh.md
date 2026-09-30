---
name: etf-premium
description: 从Yahoo Finance数据（yfinance）计算ETF相对于NAV的溢价或折价，比较或筛选ETF的溢价，解释溢价差距的原因，并将ETF的突然变动分解为NAV驱动因素与结构性因素（包括做市商伽马敞口、受限申购赎回套利、市场情绪）。当用户询问ETF是否交易在NAV之上或之下、比较ETF溢价或折价、筛选最大溢价ETF、询问ETF套利或溢价收敛，或想知道ETF为何跳涨或与持仓出现背离（包括伽马挤压、做市商伽马敞口（GEX）、受限申购赎回）时，请使用此技能。尤其适用于杠杆型、反向型、国际型、债券型、商品型及加密货币ETF（如IBIT、BITO、HYG、KWEB）。
---

# ETF溢价/折价分析技能

使用来自Yahoo Finance的数据（通过[yfinance](https://github.com/ranaroussi/yfinance)）计算ETF的市场价格相对于其净资产价值（NAV）的溢价或折价。

**为什么这很重要：** ETF的市场价格可能会与其底层资产的价值（NAV）出现背离。当你以溢价买入时，你相对于资产是高估的；以折价买入时，你则获得了便宜货。这种背离对于流动性好的美国股票ETF通常很小，但对于债券ETF、国际ETF、杠杆/反向产品以及加密货币ETF可能非常显著——尤其是在市场压力期间。

**重要提示：** 仅供研究和教育目的。非财务建议。yfinance与Yahoo公司无关。

---

## 第1步：确保依赖项可用

**当前环境状态：**

```
!`python3 -c "exec('try:\n import yfinance, pandas, numpy\n print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')\nexcept Exception:\n print(\'DEPS_MISSING\')')"`
```

如果`DEPS_MISSING`，请安装所需的软件包：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance", "pandas", "numpy"])
```

如果已安装，请跳过并继续。

---

## 第2步：路由到正确的子技能

对用户的请求进行分类并跳转到匹配的部分。如果用户询问关于ETF溢价或折价的一般性问题，但没有指定特定的分析类型，则默认到**子技能A：单个ETF快照**。

| 用户请求 | 路由到 | 示例 |
|---|---|---|
| 单个ETF溢价/折价 | **子技能A：单个ETF快照** | "SPY是否处于溢价状态？", "AGG溢价对NAV", "BITO溢价" |
| 比较多个ETF | **子技能B：多ETF比较** | "比较债券ETF折价", "IBIT或BITO哪个溢价更大", "按溢价对这些ETF进行排名" |
| 筛选器 / 查找极端溢价 | **子技能C：溢价筛选器** | "哪些ETF的折价最大", "查找交易低于NAV的ETF", "溢价筛选器" |
| 深入分析并附加背景信息 | **子技能D：溢价深入分析** | "HYG为何处于折价状态", "ARKK溢价是否正常", "带背景信息的ETF溢价分析" |
| 突然溢价飙升 / 做空回补挤压 | **子技能E：溢价飙升分解** | "KWEB今天为何飙升13%"，"该ETF的涨势是否由做空回补挤压驱动", "分解今天的ETF变动", "SOXL的做市商GEX", "溢价收敛需要多长时间" |

### 默认值

| 参数 | 默认值 |
|---|---|
| 数据源 | yfinance `navPrice` 字段 |
| 价格字段 | `regularMarketPrice`（如果失败则回退到`previousClose`） |
| 筛选器范围 | 按类别组织的常见ETF列表（见子技能C） |

---

## 子技能A：单个ETF快照

**目标**：显示一个ETF当前的溢价/折价，并提供关于正常情况的背景信息，并与其他类似ETF进行比较，以显示其相对水平。

### A1：获取和计算

```python
import yfinance as yf

# 按类别组织的同行组——用于自动将目标ETF与其最接近的同行进行比较
CATEGORY_PEERS = {
    "数字资产": ["IBIT", "BITO", "FBTC", "ETHA", "ARKB", "GBTC"],
    "中核债券": ["AGG", "BND", "SCHZ"],
    "高收益债券": ["HYG", "JNK", "USHY"],
    "长期政府债券": ["TLT", "VGLT", "SPTL"],
    "新兴市场债券": ["EMB", "VWOB", "PCY"],
    "大盘成长型": ["QQQ", "VUG", "IWF", "SCHG"],
    "大盘平衡型": ["SPY", "VOO", "IVV", "VTI"],
    "商品聚焦型": ["GLD", "IAU", "SLV", "DBC"],
    "中国区域": ["KWEB", "FXI", "MCHI"],
    "杠杆型股票交易": ["TQQQ", "UPRO", "SOXL", "JNUG"],
    "反向型股票交易": ["SQQQ", "SPXU", "SOXS", "JDST"],
    "衍生品收入": ["JEPI", "JEPQ", "QYLD"],
    "大盘价值型": ["SCHD", "VYM", "DVY", "HDV"],
}

def etf_premium_snapshot(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    # 验证这是一个ETF
    quote_type = info.get("quoteType", "")
    if quote_type != "ETF":
        return {"error": f"{ticker_symbol}不是一个ETF（quoteType={quote_type}）"}

    price = info.get("regularMarketPrice") or info.get("previousClose")
    nav = info.get("navPrice")

    if not price or not nav or nav <= 0:
        return {"error": f"{ticker_symbol}的NAV数据不可用"}

    premium_pct = (price - nav) / nav * 100
    premium_dollar = price - nav

    # 额外背景信息
    result = {
        "ticker": ticker_symbol,
        "名称": info.get("longName") or info.get("shortName", ""),
        "市场价": round(price, 4),
        "NAV": round(nav, 4),
        "溢价/折价百分比": round(premium_pct, 4),
        "溢价/折价金额": round(premium_dollar, 4),
        "状态": "溢价" if premium_pct > 0 else "折价" if premium_pct < 0 else "NAV持平",
        "类别": info.get("category", "N/A"),
        "基金家族": info.get("fundFamily", "N/A"),
        "总资产": info.get("totalAssets"),
        "净费用比率": info.get("netExpenseRatio"),
        "平均成交量": info.get("averageVolume"),
        "买入价": info.get("bid"),
        "卖出价": info.get("ask"),
        "收益率百分比": info.get("yield"),
        "年化收益率": info.get("ytdReturn"),
    }

    # 买卖价差作为背景信息，以判断溢价是否具有意义
    bid = info.get("bid")
    ask = info.get("ask")
    if bid and ask and bid > 0:
        spread_pct = (ask - bid) / ((ask + bid) / 2) * 100
        result["买卖价差百分比"] = round(spread_pct, 4)

    return result
```

### A2：获取同行比较

在计算目标ETF的快照后，根据其`category`查找并获取同一类别中同行（在`CATEGORY_PEERS`中）的溢价数据。这为用户提供即时背景信息，以判断溢价是ETF特有的还是市场普遍存在的。

使用目标的`category`从`CATEGORY_PEERS`中选择，删除目标，并对每个同行运行相同的价格/NAV计算。跳过不可用的NAV行，但报告请求和返回的同行数量，以便可见缺失数据。

将同行比较作为主要快照后的小表格呈现。这有助于用户判断溢价是否仅限于其ETF，还是整个类别都存在——例如，如果所有加密货币ETF溢价约为1.5%，则用户的ETF不是异常值。

### A3：解释结果

使用此框架解释溢价/折价是否具有意义：

| 溢价/折价 | 解释 |
|---|---|
| 在 +/- 0.05% 以内 | 基本上处于NAV——大型、流动性好的ETF正常 |
| +/- 0.05% 到 0.25% | 轻微偏差——常见且通常无操作价值 |
| +/- 0.25% 到 1.0% | 值得注意——应提及。检查买卖价差和类别 |
| +/- 1.0% 到 3.0% | 显著——常见于流动性差、国际或专业ETF |
| 超过 +/- 3.0% | 很大——可能表明压力、流动性差或结构性问题 |

**类别背景信息：**
- **美国大盘股股票**（SPY、QQQ、IVV）：溢价 > 0.10% 不常见
- **债券ETF**（AGG、HYG、LQD、TLT）：在波动期间出现0.5-2%的折价
- **国际/新兴市场**（EEM、VWO、KWEB）：时区差异导致常规0.3-1%的偏差
- **杠杆/反向型**（TQQQ、SQQQ、JNUG）：由于每日重置机制，0.3-1.5%是正常值
- **加密货币**（IBIT、BITO）：1-3%的溢价很常见，尤其是较新的基金
- **商品**（GLD、USO、UNG）：取决于期货的期货溢价/期货贴水

还比较溢价/折价与**买卖价差**：如果溢价小于价差，则它是噪音，不是信号。

---

## 子技能B：多ETF比较

**目标**：并排比较多个ETF的溢价/折价。

### B1：获取和排名

```python
import yfinance as yf
import pandas as pd

def compare_etf_premiums(tickers):
    rows = []
    for sym in tickers:
        try:
            t = yf.Ticker(sym)
            info = t.info
            if info.get("quoteType") != "ETF":
                rows.append({"ticker": sym, "error": "不是ETF"})
                continue
            price = info.get("regularMarketPrice") or info.get("previousClose")
            nav = info.get("navPrice")
            if price and nav and nav > 0:
                prem = (price - nav) / nav * 100
                bid = info.get("bid", 0)
                ask = info.get("ask", 0)
                spread = (ask - bid) / ((ask + bid) / 2) * 100 if bid and ask and bid > 0 else None
                rows.append({
                    "ticker": sym,
                    "名称": info.get("shortName", ""),
                    "价格": round(price, 2),
                    "NAV": round(nav, 2),
                    "溢价百分比": round(prem, 4),
                    "价差百分比": round(spread, 4) if spread else None,
                    "类别": info.get("category", "N/A"),
                    "总资产": info.get("totalAssets"),
                })
            else:
                rows.append({"ticker": sym, "error": "NAV不可用"})
        except Exception as e:
            rows.append({"ticker": sym, "error": str(e)})

    df = pd.DataFrame(rows)
    if "premium_pct" in df.columns:
        df = df.sort_values("premium_pct", ascending=True)
    return df
```

### B2：以排名表格呈现

按溢价/折价排序（最折价优先）。突出显示：
- 哪些ETF处于最深的折价
- 哪些ETF处于最高溢价
- 溢价/折价是否超过买卖价差（如果没有，则是市场微观结构噪音）

---

## 子技能C：溢价筛选器

**目标**：扫描常见ETF集合，查找具有最大溢价或折价的ETF。

### C1：定义集合并扫描

使用`references/etf_premium_reference.md`中按类别组织的集合，或用户自己的列表。对每个符号应用子技能A的计算，保留类别标签，按请求的绝对溢价阈值过滤，并从最深折价到最高溢价排序。保留失败或缺少NAV的计数，而不是将其静默处理为零。

### C2：呈现结果

显示按溢价排序的排名表格（最折价优先）。如果列表很长，按类别分组。指出：
- **前5个最深折价**——潜在的买入机会（或压力迹象）
- **前5个最高溢价**——支付过高的风险
- **类别模式**——所有债券ETF都处于折价吗？所有加密货币ETF都处于溢价吗？

警告说，大型集合可能需要1-2分钟。

---

## 子技能D：溢价深入分析

**目标**：结合溢价/折价数据与附加背景信息，帮助用户理解溢价存在的原因，以及它是否可能持续存在。

### D1：收集综合数据

运行子技能A的快照，然后获取三个月的每日历史数据并添加：

- 年化波动率：`std(daily returns) * sqrt(252)`
- 平均每日美元成交量：`mean(close * volume)`
- 从三个月收盘价高的百分比距离
- AUM、费用比率、收益率、YTD回报和三年贝塔
- 买卖价差百分比以及绝对溢价是否超过该价差

将不可用字段保留为`null`，而不是编造值。时间戳价格和NAV输入，以便用户可以判断比较是否同步。

### D2：解释*原因*

收集数据后，使用此诊断框架解释溢价/折价：

**溢价常见原因：**
- **需求激增**——买家多于授权参与者可以创建的份额（常见于新/热门ETF，如加密货币）
- **时区差异**——国际ETF在底层市场关闭时交易；价格反映预期变动
- **创建机制瓶颈**——当授权参与者面临创建新份额的限制时
- **情绪溢价**——在炒作周期中，散户需求将价格推高于公允价值

**折价常见原因：**
- **流动性压力**——在抛售期间，债券和信贷ETF通常以折价交易，因为底层债券比ETF本身更难定价/交易
- **赎回压力**——大量资金流出但授权参与者响应缓慢
- **NAV陈旧**——官方NAV可能无法反映盘后新闻或事件
- **结构性问题**——基于期货的ETF（USO、UNG）的期货溢价导致持续拖累

**溢价是否可能持续？**
- 对于流动性好的美国股票ETF：不会——套利在几分钟内纠正偏差
- 对于债券ETF在压力期间：折价可能持续数天或数周
- 对于加密货币ETF：溢价倾向于随着基金成熟和AP更活跃而缩小
- 对于国际ETF：由于底层市场每日重置，溢价会重置

---

## 子技能E：溢价飙升分解（做空回补挤压分析）

**目标**：当ETF刚刚经历单日内大幅变动，与其底层资产出现背离时，将变动分解为（1）由NAV驱动的成分和（2）由结构性力量驱动的“超额溢价”——最常见的是期权做市商的做空回补挤压、授权参与者套利失败或情绪激增。然后评估溢价可能需要多长时间收敛。

当用户报告或询问以下内容时，此子技能适用：
- ETF单日内上涨5%+
- ETF与其指定底层资产之间的背离（例如，“MSTR上涨13%，但BTC仅上涨3%”）
- ETF或单个名称中怀疑存在做空回补挤压
- 做市商对冲是否在放大变动

在运行E2之前，请阅读`references/gamma_squeeze_reference.md`，了解完整的GEX公式推导、做市商头寸惯例和工作示例。

### E1：将今天的变动分解为NAV驱动与超额溢价

静态`navPrice`字段仅提供最近一个交易日的NAV。估计今天NAV回报，基于当前持股权重和同日持股回报，然后归一化，计算：

```text
NAV代理回报 = sum(weight_i x return_i) / 覆盖权重
超额溢价回报 = ETF回报 - NAV代理回报
```

报告持股覆盖率和使用的每只持股回报。如果`funds_data.top_holdings`不完整，则优先使用发行方发布的持股或用户提供的权重。

**注意**：对于其底层资产在关闭交易期间交易的国际ETF（例如，亚洲持仓在美国时间），必须使用美国上市的代理（ADRs）或期货。如果两者都不可用，请向用户标记此问题——NAV代理将过时。

### E2：根据期权链计算做市商伽马敞口（GEX）

GEX近似每1%底层资产变动下的做市商对冲敏感性。阅读公式和两种头寸惯例，根据当前现货、行权价、时间、无风险利率和隐含波动率计算合约伽马，然后在整个链条上聚合`OI x gamma x spot^2`。

返回看涨GEX、看跌GEX、SqueezeMetrics风格的净GEX、总对冲压力、看涨/看跌未平仓合约比率、中位数近ATM隐含波动率、分析的到期日以及最高行权价/到期日集中度。明确说明符号惯例；不要从公开未平仓合约中推断实际做市商库存。

解释输出：

- **`net_gex_squeezemetrics_$`高度负** → 做市商做空伽马；他们的对冲买入将放大涨势。经典的做空回补挤压燃料。
- **集中在一个近到期日的行权价上**（例如，在下一个月份的看涨期权中未平仓合约大量集中）→ 挤压脆弱且集中。当该行权价到期或现货价格超过它时，伽马会急剧下降。
- **ATM隐含波动率远高于近期平均水平**（例如，78%对典型的30-40%）→ 市场正在为持续的大幅变动定价；期权溢价衰减本身将在数天内提供收敛压力。
- **看涨/看跌未平仓合约比率 > 2.5** → 看涨头寸集中，与看涨做空回补挤压设置一致。

### E3：比较结构性买入压力与实际成交量

估计上限做市商份额：

```text
隐含做市商驱动美元 = abs(GEX per 1% move) x abs(ETF return in percentage points)
做市商成交量份额 = implied dealer-driven dollars / (close x volume)
```

这是一个粗略估算——它假设在行情变动期间，所有合约的完整伽玛（gamma）都朝单一方向进行了对冲。实际的对冲是分批次进行的，且并非所有交易员都采用完全相同的对冲策略。请将其视为一种上限启发式方法，而非精确数值。在呈现结果时，务必同时列明相关假设。

### E4：评估溢价收敛的时间线

收敛过程体现在三个时间尺度上（详见 `references/gamma_squeeze_reference.md` 中的“收敛时间线”章节）：

| 时间尺度 | 机制 | 需要检查的事项 |
|---|---|---|
| **小时级** | AP（授权参与者）创建/赎回套利 | 标的市场是否开盘？创建单元是否受限？买卖价差是否正在扩大（暗示 AP 在退后）？ |
| **天级** | 期权到期 / 伽玛衰减 | 主要行权价的到期日何时？未平仓合约（OI）是否在向前滚动或平仓？隐含波动率（IV）是否开始压缩？ |
| **周级** | 净流量正常化 | 该 ETF 是否正在接收大额每日资金流入（表明需求超出创建能力）？空头头寸是否正在积累（可能成为进一步挤压的燃料）？ |

对于小时级视角，记录标的市场是否开盘以及创建/赎回是否受到限制。对于天级视角，计算最大伽玛集中点的到期剩余天数，并检查 IV 和 OI 是在衰减还是在滚动。对于周级视角，如有条件，请使用发行人的流量/创建数据；仅凭资产规模（AUM）只是一个粗略的代理指标。

### E5：呈现分解结果

按以下顺序格式化答案：

1. **核心数值**：今日 ETF 的变动、基于 NAV 的代理变动，以及超额溢价（以百分点 pp 表示）。
2. **分解表**：

   | 组成部分 | 贡献度 |
   |---|---|
   | NAV 驱动部分（持仓 × 权重） | +X.X% |
   | 超额溢价（残差部分） | +Y.Y% | |
   | ETF 总变动 | +Z.Z% |

3. **交易员对冲量化**：
   - 净 GEX（采用 SqueezeMetrics 惯例）
   - 当日隐含的交易员购买美元金额 vs 实际成交美元金额
   - 估算的交易员在买盘压力中所占份额
4. **风险指标**：平值（ATM）IV、看涨/看跌期权 OI 比率、前三大行权价/到期日集中度。
5. **收敛展望**：列出小时级/天级/周级各机制及其当前状态。
6. **注意事项**：GEX 估算假设交易员头寸均匀；在隔夜时段，NAV 代理数据是滞后的；这*并非*对未来价格的预测。

---

## 第 3 步：回复用户

### 始终包含
- **ETF 名称及代码**
- **市场价格**和**NAV**，并展示计算过程
- 明确标注**溢价/折价百分比**
- **背景**：这种偏离对该类别的 ETF 而言是否正常？

### 始终添加警示
- 来自 Yahoo Finance 的 NAV 数据反映的是**最近一次官方 NAV**（通常为前一个交易日收盘数据）——它不是实时数据
- 取决于交易所，市场价格可能存在**15 分钟延迟**
- 溢价/折价在交易时段可能迅速变化——这是一个快照，而非实时数据流
- 微小的溢价/折价（小于买卖价差）属于**市场微观结构噪音**，而非真实的错误定价
- 不要仅凭溢价/折价推荐买入或卖出——呈现数据，让用户自行决定

### 格式要求
- 多 ETF 比较时使用 markdown 表格
- 展示公式：`Premium/Discount = (Market Price - NAV) / NAV x 100`
- 在文本中加粗核心数值：“以**0.45% 折价**交易” 或 “以**1.2% 溢价**交易”
- 根据数值大小，将百分比保留至 2-4 位小数

---

## 参考文件

- `references/etf_premium_reference.md` — 详细公式、特定类别基准、常见 ETF 名单，以及驱动溢价的创建/赎回机制背景
- `references/gamma_squeeze_reference.md` — 溢价分解框架、Black-Scholes 伽玛 + GEX 公式（包含 SqueezeMetrics 和净多头客户惯例两种）、收敛时间线框架（小时/天/周）、伽玛挤压与常规上涨的诊断对照表，以及一个实例。请在运行子技能 E *之前*阅读此文件。

阅读参考文件，以获取关于 ETF 溢价/折价机制、历史背景以及伽玛挤压分解方法论的更深入技术细节。
