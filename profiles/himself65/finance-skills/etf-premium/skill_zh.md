# ETF溢价/折价分析技能

使用来自Yahoo Finance的数据（通过[yfinance](https://github.com/ranaroussi/yfinance)）计算ETF的市场价格相对于其净资产价值（NAV）的溢价或折价。

**为什么这很重要**：ETF的市场价格可能会与其基础资产的价值（NAV）出现背离。当你以溢价买入时，你相对于资产来说支付了过高的价格；以折价买入时，你则得到了便宜货。这种背离对于流动性好的美国股票ETF通常很小，但对于债券ETF、国际ETF、杠杆/反向产品以及加密货币ETF来说可能很显著——尤其是在市场压力期间。

**重要提示**：仅供研究和教育目的使用。不是财务建议。yfinance与Yahoo, Inc.没有关联。

---

## 第1步：确保依赖项可用

**当前环境状态**：

```
!`python3 -c "exec('try:\n import yfinance, pandas, numpy\n print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')\nexcept Exception:\n print(\'DEPS_MISSING\')')"`
```

如果`DEPS_MISSING`，则安装所需的软件包：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance", "pandas", "numpy"])
```

如果已安装，则跳过并继续。

---

## 第2步：路由到正确的子技能

对用户的请求进行分类并跳转到匹配的部分。如果用户询问关于ETF溢价或折价的一般问题，但没有指定特定的分析类型，则默认到**子技能A：单个ETF快照**。

| 用户请求 | 路由到 | 示例 |
|---|---|---|
| 单个ETF溢价/折价 | **子技能A：单个ETF快照** | "SPY是否处于溢价状态？", "AGG溢价对NAV", "BITO溢价" |
| 比较多个ETF | **子技能B：多ETF比较** | "比较债券ETF折价", "IBIT或BITO哪个溢价更大", "按溢价对这些ETF进行排名" |
| 筛选器 / 查找极端溢价 | **子技能C：溢价筛选器** | "哪些ETF的折价最大", "查找交易低于NAV的ETF", "溢价筛选器" |
| 深入分析并附加背景信息 | **子技能D：溢价深入分析** | "为什么HYG处于折价状态", "ARKK溢价是否正常", "具有背景信息的ETF溢价分析" |
| 突然溢价飙升 / 做多Gamma挤压 | **子技能E：溢价飙升分解** | "为什么KWEB今天跳涨13%"，"这个ETF的涨势是否由做多Gamma驱动"，"分解今天的ETF变动"，"做市商GEX对SOXL"，"溢价收敛需要多长时间" |

### 默认值

| 参数 | 默认值 |
|---|---|
| 数据源 | yfinance `navPrice` 字段 |
| 价格字段 | `regularMarketPrice`（如果失败则回退到`previousClose`） |
| 筛选器宇宙 | 按类别组织的常见ETF列表（见子技能C） |

---

## 子技能A：单个ETF快照

**目标**：显示一个ETF当前的溢价/折价，并提供关于什么才是正常的背景信息，并加上与类似ETF的同行比较，以显示它如何与同类ETF相比。

### A1：获取和计算

```python
import yfinance as yf

# 按类别组织的同行组——用于自动将目标ETF与其最接近的同行进行比较
CATEGORY_PEERS = {
    "数字资产": ["IBIT", "BITO", "FBTC", "ETHA", "ARKB", "GBTC"],
    "中短期核心债券": ["AGG", "BND", "SCHZ"],
    "高收益债券": ["HYG", "JNK", "USHY"],
    "长期政府债券": ["TLT", "VGLT", "SPTL"],
    "新兴市场债券": ["EMB", "VWOB", "PCY"],
    "大型成长型": ["QQQ", "VUG", "IWF", "SCHG"],
    "大型平衡型": ["SPY", "VOO", "IVV", "VTI"],
    "商品聚焦型": ["GLD", "IAU", "SLV", "DBC"],
    "中国区域": ["KWEB", "FXI", "MCHI"],
    "交易——杠杆股票": ["TQQQ", "UPRO", "SOXL", "JNUG"],
    "交易——反向股票": ["SQQQ", "SPXU", "SOXS", "JDST"],
    "衍生收入": ["JEPI", "JEPQ", "QYLD"],
    "大型价值型": ["SCHD", "VYM", "DVY", "HDV"],
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
        return {"error": f"没有{ticker_symbol}的NAV数据"}

    premium_pct = (price - nav) / nav * 100
    premium_dollar = price - nav

    # 额外背景信息
    result = {
        "ticker": ticker_symbol,
        "name": info.get("longName") or info.get("shortName", ""),
        "市场价格": round(price, 4),
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
        "年化回报率": info.get("ytdReturn"),
    }

    # 买卖价差作为背景信息，以判断溢价是否有意义
    bid = info.get("bid")
    ask = info.get("ask")
    if bid and ask and bid > 0:
        spread_pct = (ask - bid) / ((ask + bid) / 2) * 100
        result["买卖价差百分比"] = round(spread_pct, 4)

    return result
```

### A2：获取同行比较

在计算目标ETF的快照后，查找其`category`并获取同一类别中同行（ETF）的溢价数据。这为用户提供即时背景信息，以判断溢价是ETF特有的还是市场普遍的。

使用目标的`category`从`CATEGORY_PEERS`中选择，删除目标，并对每个同行运行相同的价格/NAV计算。跳过不可用的NAV行，但报告请求和返回的同行数量，以便可见缺失数据。

在主快照后以小表格的形式呈现同行比较。这有助于用户看到溢价是否仅限于他们的ETF，还是整个类别都存在——例如，如果所有加密货币ETF的溢价都在~1.5%，那么用户的ETF就不是异常。

### A3：解释结果

使用这个框架来解释溢价/折价是否有意义：

| 溢价/折价 | 解释 |
|---|---|
| 在 +/- 0.05% 之内 | 基本上处于NAV——对于大型、流动性好的ETF是正常的 |
| +/- 0.05% 到 0.25% | 轻微偏差——很常见，通常不是可操作的 |
| +/- 0.25% 到 1.0% | 值得注意——值得提及。检查买卖价差和类别 |
| +/- 1.0% 到 3.0% | 显著——常见于流动性差、国际或专业ETF |
| 超过 +/- 3.0% | 很大——可能表明压力、流动性差或结构性问题 |

**类别背景信息**：
- **美国大型股票**（SPY、QQQ、IVV）：溢价 > 0.10% 是不寻常的
- **债券ETF**（AGG、HYG、LQD、TLT）：在波动期间，折价 0.5-2% 是常见的
- **国际/新兴市场**（EEM、VWO、KWEB）：时区差异导致定期 0.3-1% 的偏差
- **杠杆/反向**（TQQQ、SQQQ、JNUG）：由于每日重置机制，0.3-1.5% 是正常的
- **加密货币**（IBIT、BITO）：1-3% 的溢价很常见，尤其是对于较新的基金
- **商品**（GLD、USO、UNG）：取决于期货的期货溢价/期货贴水

还比较溢价/折价与**买卖价差**：如果溢价小于价差，则这是噪音，不是信号。

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
                    "name": info.get("shortName", ""),
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

### B2：以排名表格的形式呈现

按溢价/折价排序（最折价在前）。突出显示：
- 哪些ETF处于最深的折价状态
- 哪些处于最高溢价状态
- 溢价/折价是否超过买卖价差（如果没有，则是市场微观结构噪音）

---

## 子技能C：溢价筛选器

**目标**：扫描一个由常见ETF组成的宇宙，以找到具有最大溢价或折价的ETF。

### C1：定义宇宙并扫描

使用`references/etf_premium_reference.md`中按类别组织的宇宙，或用户自己的列表。对每个符号应用子技能A的计算，保留类别标签，按请求的绝对溢价阈值过滤，并从最深折价到最高溢价排序。保留失败或缺少NAV的计数，而不是将其静默地视为零。

### C2：呈现结果

显示按溢价排序的排名表格（最折价在前）。如果列表很长，则按类别分组。指出：
- **最深的5个折价**——潜在的买入机会（或压力迹象）
- **最高的5个溢价**——支付过高的风险
- **类别模式**——所有债券ETF都处于折价状态吗？所有加密货币ETF都处于溢价状态吗？

警告说，大型宇宙可能需要1-2分钟。

---

## 子技能D：溢价深入分析

**目标**：将溢价/折价数据与附加背景信息结合起来，帮助用户理解溢价存在的原因，以及它是否可能持续存在。

### D1：收集全面数据

运行子技能A的快照，然后拉取三个月的每日历史并添加：

- 年化波动率：`std(daily returns) * sqrt(252)`
- 平均每日美元成交量：`mean(close * volume)`
- 从三个月收盘价到当前距离
- AUM、费用比率、收益率、YTD回报和三年贝塔
- 买卖价差百分比以及绝对溢价是否超过该价差

将不可用字段保留为`null`，而不是编造值。为价格和NAV输入时间戳，以便用户可以判断比较是否同步。

### D2：解释“为什么”

收集数据后，使用这个诊断框架来解释溢价/折价：

**溢价的常见原因**：
- **需求激增**——买家多于授权参与者可以创建的份额（常见于新/热门ETF，如加密货币）
- **时区不匹配**——国际ETF在基础市场关闭时交易；价格反映了预期的变动
- **创建机制瓶颈**——当授权参与者面临创建新份额的限制时
- **情绪溢价**——在炒作周期中，散户需求将价格推高到公允价值之上

**折价的常见原因**：
- **流动性压力**——在抛售期间，债券和信贷ETF通常以折价交易，因为基础债券比ETF本身更难定价/交易
- **赎回压力**——大量资金流出，但授权参与者的响应缓慢
- **陈旧的NAV**——官方NAV可能无法反映盘后新闻或事件
- **结构性问题**——基于期货的ETF（USO、UNG）的期货溢价导致持续的压力

**溢价是否可能持续**？
- 对于流动性好的美国股票ETF：不会——套利在几分钟内纠正偏差
- 对于债券ETF在压力期间：折价可能持续数天或数周
- 对于加密货币ETF：溢价往往会随着基金成熟和AP更活跃而缩小
- 对于国际ETF：由于基础市场每日重置，溢价会重置

---

## 子技能E：溢价飙升分解（Gamma挤压分析）

**目标**：当ETF刚刚经历了与基础资产背离的剧烈日内变动时，将变动分解为（1）由NAV驱动的基本成分和（2）由结构性力量驱动的“超额溢价”——最常见的是做市商的Gamma对冲、AP套利破裂或情绪激增。然后评估溢价可能需要多长时间收敛。

当用户报告或询问以下内容时，此子技能是合适的：
- 一个ETF在一个交易日内上涨/下跌5%+
- ETF与其指定基础资产之间的背离（例如，“MSTR跳涨13%，但BTC仅上涨3%”）
- ETF或单个名称中怀疑存在Gamma挤压
- 做市商对冲是否在放大变动

在运行E2之前，请阅读`references/gamma_squeeze_reference.md`，了解GEX公式的完整推导、做市商头寸惯例和示例。

### E1：将今天的变动分解为NAV驱动与超额溢价

静态`navPrice`字段仅提供最近的日终NAV。根据当前持股权重和同会话持股回报估计今天的NAV回报，然后归一化，计算：

```text
NAV代理回报 = sum(weight_i x return_i) / 覆盖权重
超额溢价回报 = ETF回报 - NAV代理回报
```

报告持股覆盖率和每只持股的回报。如果`funds_data.top_holdings`不完整，则优先使用发行人发布的持股或用户提供的权重。

**注意**：对于其基础资产在一个会话中交易的ETF（例如，亚洲资产在美国时间），必须使用其美国上市的代理（ADR）或期货。如果两者都不可用，请向用户报告此问题——NAV代理将过时。

### E2：从期权链计算做市商Gamma敞口（GEX）

GEX近似每1%基础资产变动下的做市商对冲敏感性。阅读公式和两种头寸惯例，在`references/gamma_squeeze_reference.md`中计算当前现货、行权价、时间、无风险利率和隐含波动率下的合约Gamma，然后在整个链条中聚合`OI x gamma x spot^2`。

返回调用GEX、看跌GEX、SqueezeMetrics风格的净GEX、总对冲压力、看涨/看跌未平仓合约比率、中位ATM隐含波动率、分析的到期日以及最高行权价/到期日集中度。明确说明符号惯例；不要从公共未平仓合约中推断实际做市商库存。

解释输出：

- **`net_gex_squeezemetrics_$`高度负** → 做市商做空Gamma；他们的对冲买入将放大反弹。经典的Gamma挤压燃料。
- **集中在单个接近到期日的行权价**（例如，文章中的“6月45美元看涨期权”）→ 挤压脆弱且集中。当该行权价到期或现货价格超过它时，Gamma会急剧下降。
- **ATM隐含波动率远高于近期平均水平**（文章示例：78 vs 典型~30–40）→ 市场正在为持续的大幅变动定价；期权溢价衰减本身将在数天内提供收敛压力。
- **看涨/看跌未平仓合约比率 > 2.5** → 看涨头寸较多，与看涨Gamma挤压设置一致。

### E3：比较结构性买入压力与实际成交量

估计上限做市商份额：

```text
隐含做市商驱动美元 = abs(GEX per 1% move) x abs(ETF return in percentage points)
做市商成交量份额 = implied dealer-driven dollars / (close x volume)
```

这是一个粗略估计——它假设每个合约在单方向上在变动期间进行了全部Gamma对冲。实际对冲是逐步进行的，而且并非所有做市商都相同。将其视为上限启发式，而不是精确数字。始终将其与假设一起呈现。

### E4：评估溢价收敛时间表

文章的三级收敛框架：

| 时间尺度 | 机制 | 检查内容 |
|---|---|---|
| **小时** | AP创建/赎回套利 | 基础市场是否开放？创建单位是否受限？买卖价差是否扩大（表明AP退回）？ |
| **天** | 期权到期 / Gamma衰减 | 主导行权价的到期日是什么时候？未平仓合约是否向前滚动或关闭？隐含波动率是否开始收窄？ |
| **周** | 净流量正常化 | ETF是否每天收到大量流入（表明需求超过创建能力）？卖空兴趣是否增加（潜在的额外挤压燃料）？ |

对于小时视图，记录基础市场是否开放以及创建/赎回是否受限。对于天视图，计算最大Gamma集中度的到期日，并检查隐含波动率和未平仓合约是否正在衰减或滚动。对于周视图，如果可用，则使用发行人流量/创建数据；AUM仅是一个粗略的代理。

### E5：呈现分解

按以下顺序格式化答案：

1. **标题编号**：今天的ETF变动、NAV代理变动和超额溢价（以百分比表示）。
2. **分解表格**：

   | 成分 | 贡献 |
   |---|---|
   | NAV驱动（持股×权重） | +X.X% |
   | 超额溢价（剩余） | +Y.Y% |
   | 总ETF变动 | +Z.Z% |

3. **做市商对冲量化**：
   - 净GEX（SqueezeMetrics惯例）
   - 当天隐含做市商美元买入与实际美元成交量
   - 估计做市商买入压力的份额
4. **风险指标**：ATM隐含波动率、看涨/看跌未平仓合约比率、前3个行权价/到期日集中度。
5. **收敛展望**：列出每个小时/天/周机制的当前状态。
6. **注意事项**：GEX估计假设做市商头寸一致；NAV代理在夜间会话期间过时；这不是对未来价格的预测。

---

## 第3步：响应用户

### 始终包括
- **ETF名称和代码**
- **市场价格**和**NAV**，并显示计算
- **溢价/折价百分比**，并明确标注
- **背景信息**：这种ETF类别是否正常？

### 始终注意
- 来自Yahoo Finance的NAV数据反映**最近的官方NAV**（通常为前一个交易日结束时的NAV）——它不是实时数据
- 市场价格可能有**15分钟的延迟**，具体取决于交易所
- 在交易时段内，溢价/折价可能迅速变化——这是一个快照，不是实时数据流
- 小溢价/折价（小于买卖价差）是**市场微观结构噪音**，不是实际定价错误
- **切勿仅基于溢价/折价建议买卖**——提供数据并让用户自行决定

### 格式化
- 使用markdown表格进行多ETF比较
- 显示公式：`溢价/折价 = (市场价格 - NAV) / NAV x 100`
- 在文本中使用颜色指示器："以**0.45%折价**交易"或"以**1.2%溢价**"

百分比根据幅度四舍五入到2-4位小数
