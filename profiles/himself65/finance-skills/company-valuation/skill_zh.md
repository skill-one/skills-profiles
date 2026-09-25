# 公司估值

通过三种方法进行估值三角测量，然后将它们混合成一个隐含的股价：

1. **DCF** — 5年FCFF预测，按WACC折现，终值。
2. **相对估值** — 应用同行中位数市盈率、EV/收入、EV/EBITDA。
3. **SOTP** — 当存在2个或多个不同的报告部门时，按纯业务同行倍数进行估值。

始终展示WACC × 终值增长率敏感性表格和牛市/基准/熊市情景。

**免责声明**：研究/教育输出。非财务建议。

---

## 第1步：检测流程

检测数据源和运行时依赖项。该技能支持2种方法路径——选择可用的最丰富的一种。

**环境状态：**

```
!`python3 -c "exec('try:\n import yfinance, numpy, pandas\n print(\'YFIN_OK\')\nexcept Exception:\n print(\'YFIN_MISSING\')')"`
```

```
!`python3 -c "exec('try:\n import yfinance as yf\n t=yf.Ticker(\'^TNX\')\n p=t.fast_info.last_price\n print(f\'RF_10Y={p/100:.4f}\')\nexcept Exception:\n print(\'RF_FETCH_FAIL\')')"`
```

**决策树：**

| 条件 | 方法路径 |
|---|---|
| `YFIN_OK` | **路径A**（主要）：yfinance获取财务数据 + 同行倍数 |
| `YFIN_MISSING` | **路径B**：安装yfinance，然后路径A。`python3 -m pip install -q yfinance numpy pandas` |
| `RF_FETCH_FAIL` | 使用默认`rf = 0.045`并在输出中注明过时的无风险利率 |

如果打印了`RF_10Y=`，则使用该值作为第4步d中的`rf`，而不是硬编码的4.5%。

---

## 第2步：选择方法并设置默认值

### 方法适用性

| 公司类型 | DCF | 相对估值 | SOTP | 备用方案 |
|---|---|---|---|---|
| 成熟现金流（CPG、电信、公用事业） | ✅ 主要 | ✅ | ❌ | — |
| 高增长SaaS / 软件 | ✅ 小心使用 | ✅ 主要 | ❌ | 使用EV/收入 + 规则40 |
| 多部门企业集团 | ✅ | ✅ | ✅ 主要 | 查看`references/sotp.md` |
| 银行 / 保险 | ❌ | ✅（市净率、市总资产净值倍率） | ❌ | DDM或超额回报；在输出中注明 |
| 收入前 | ❌ | 仅EV/收入 | ❌ | 标记低置信度 |
| REITs | ❌ | ✅（市现率、市每股自由现金流率） | ❌ | 基于净资产价值 |
| 周期性（能源、半导体、工业） | ✅ 在中周期 | ✅ | 有时 | 通过周期性进行标准化 |

### 默认值表格

以下每个参数在进入第3步之前都必须有值。除非用户覆盖，否则使用这些默认值。

| 参数 | 默认值 | 理由 |
|---|---|---|
| 预测期 | 5年 | 标准显式预测窗口 |
| 终值增长率 `g` | 2.5% | ~ 长期美国GDP |
| 无风险利率 `rf` | 来自第1步的活期10年期美国国债，否则4.5% | 当前资本成本基准 |
| 股权风险溢价 `erp` | 5.5% | Damodaran中位数 |
| Beta | 来自yfinance的`info['beta']` | 市场观察到的杠杆Beta |
| 债务成本 `kd` | `interest_expense / total_debt`，否则5.5% | 有效利率；回退至IG利差 |
| 税率 | 3年有效税率中位数，下限15%，上限30% | 剔除一次性因素 |
| 利润率假设 | 每个比率3年中的中位数 | 平滑周期性噪音 |
| SBC处理 | 软件/SaaS用现金；工业/CPG用非现金 | 行业惯例 |
| 同行数量 | 4-6 | 平衡信号与噪音 |
| 同行倍数 | 中位数（不是平均值） | 对异常值具有鲁棒性 |
| 方法权重（无SOTP） | DCF 50% / 相对估值50% | 等效三角测量 |
| 方法权重（有SOTP） | DCF 40% / 相对估值30% / SOTP 30% | 当适用时SOTP获得权重 |
| 敏感性网格 | WACC ±1% 在0.5%步长 × g从1.5-3.5%在0.5% | 5×5矩阵 |

查看`references/wacc_erp_rates.md`以获取当前无风险利率、ERP表格和行业WACC基准。

---

## 第3步：获取数据

```python
import yfinance as yf
import numpy as np
import pandas as pd

TICKER = "AAPL"  # 替换
t = yf.Ticker(TICKER)

info       = t.info
income_a   = t.income_stmt
cashflow_a = t.cashflow
balance_a  = t.balance_sheet
income_q   = t.quarterly_income_stmt
cashflow_q = t.quarterly_cashflow

earnings_est = t.earnings_estimate
revenue_est  = t.revenue_estimate

price       = info.get("currentPrice") or info.get("regularMarketPrice")
market_cap  = info.get("marketCap")
shares_out  = info.get("sharesOutstanding")
total_debt  = info.get("totalDebt") or 0
cash        = info.get("totalCash") or 0
beta        = info.get("beta") or 1.0
sector      = info.get("sector")
industry    = info.get("industry")
```

关键财务报表行（yfinance标签）：

| 需要 | 行 |
|---|---|
| 收入 | `Total Revenue` |
| EBIT | `Operating Income` |
| 净收入 | `Net Income` |
| D&A | `Depreciation And Amortization`（在现金流量表中） |
| CapEx | `Capital Expenditure`（负值） |
| ΔNWC | `Change In Working Capital`（现金流量表） |
| SBC | `Stock Based Compensation`（现金流量表） |

---

## 第4步：DCF构建

完整方法 + 行业特定调整在`references/dcf.md`中。快速骨架：

```python
# 4a. 收入增长路径——从第1年（共识或历史CAGR）渐变为终值g
hist_cagr = (rev[-1] / rev[0]) ** (1 / (len(rev)-1)) - 1
y1 = float(revenue_est.loc["+1y", "growth"]) if "+1y" in revenue_est.index else hist_cagr
g_terminal = 0.025
growth_path = np.linspace(y1, g_terminal + 0.01, 5)

# 4b. 利润率——3年中的中位数
ebit_margin = float((income_a.loc["Operating Income"] / income_a.loc["Total Revenue"]).iloc[:3].median())
da_pct      = float((cashflow_a.loc["Depreciation And Amortization"] / income_a.loc["Total Revenue"]).iloc[:3].median())
capex_pct   = float((cashflow_a.loc["Capital Expenditure"].abs() / income_a.loc["Total Revenue"]).iloc[:3].median())
nwc_pct     = float((cashflow_a.loc["Change In Working Capital"].abs() / income_a.loc["Total Revenue"]).iloc[:3].median())
tax_rate    = max(0.15, min(0.30, 0.21))  # 使用有效税率（如果可用）

# 4c. 每年FCFF
rev_t = [float(income_a.loc["Total Revenue"].iloc[0])]
fcff  = []
for g in growth_path:
    rev_t.append(rev_t[-1] * (1 + g))
    ebit = rev_t[-1] * ebit_margin
    nopat = ebit * (1 - tax_rate)
    fcff.append(nopat + rev_t[-1]*da_pct - rev_t[-1]*capex_pct - rev_t[-1]*nwc_pct)

# 4d. WACC
rf, erp, kd = 0.045, 0.055, 0.055  # 用第1步的实时值覆盖rf
ke = rf + beta * erp
e_v = market_cap / (market_cap + total_debt)
d_v = 1 - e_v
wacc = e_v*ke + d_v*kd*(1 - tax_rate)

# 4e. 终值——计算两个值，使用中点
tv_gordon = fcff[-1] * (1 + g_terminal) / (wacc - g_terminal)
tv_exit   = (rev_t[-1] * ebit_margin + rev_t[-1] * da_pct) * 15  # 同行中位数EV/EBITDA
tv_base   = 0.5 * (tv_gordon + tv_exit)

# 4f. 桥接至股权
pv_fcff = sum(f / (1+wacc)**(i+1) for i, f in enumerate(fcff))
pv_tv   = tv_base / (1+wacc)**5
ev      = pv_fcff + pv_tv
equity  = ev + cash - total_debt
implied_price_dcf = equity / shares_out
```

**门禁**：（a）如果`wacc <= g_terminal` → 停止，g过于激进；（b）如果`pv_tv / ev > 0.85`或`< 0.45` → 标记并显示两种终值方法；（c）如果`wacc`在`references/wacc_erp_rates.md`中的行业合理性范围内之外 → 注明。

---

## 第5步：相对估值

选择4-6个同行。同行映射和调整规则在`references/relative_valuation.md`中。

```python
PEERS = ["MSFT", "ORCL", "CRM", "NOW", "SAP", "WDAY"]  # 按行业选择
multiples = {}
for p in PEERS:
    pi = yf.Ticker(p).info
    multiples[p] = {
        "pe_fwd": pi.get("forwardPE"),
        "ev_rev": pi.get("enterpriseToRevenue"),
        "ev_ebitda": pi.get("enterpriseToEbitda"),
        "ps": pi.get("priceToSalesTrailing12Months"),
    }
med_pe     = np.nanmedian([v["pe_fwd"] for v in multiples.values()])
med_ev_rev = np.nanmedian([v["ev_rev"] for v in multiples.values()])
med_ev_eb  = np.nanmedian([v["ev_ebitda"] for v in multiples.values()])

eps_ttm    = float(income_q.loc["Diluted EPS"].iloc[:4].sum())
rev_ttm    = float(income_q.loc["Total Revenue"].iloc[:4].sum())
ebitda_ttm = float(income_q.loc["EBIT"].iloc[:4].sum()) + float(cashflow_q.loc["Depreciation And Amortization"].iloc[:4].sum())
net_debt   = total_debt - cash

implied_pe       = med_pe * eps_ttm
implied_ev_rev   = (med_ev_rev * rev_ttm - net_debt) / shares_out
implied_ev_ebit  = (med_ev_eb  * ebitda_ttm - net_debt) / shares_out
implied_price_rel = np.nanmedian([implied_pe, implied_ev_rev, implied_ev_ebit])
```

如果目标公司的增长或利润率特征与同行有实质性差异，则同行中位数±10-30%。始终说明调整和原因。规则40锚定用于SaaS在`references/relative_valuation.md`中。

---

## 第6步：SOTP（仅限多部门）

除非10-K报告存在2个或多个具有不同经济学的运营部门，否则跳过。yfinance不暴露部门数据——用户必须提供或从申报文件中解析。完整方法在`references/sotp.md`中：
- 确定部门 + 每个部门的纯业务同行
- 应用同行中位数EV/EBITDA（或增长部门的EV/收入）
- 减去未分配的 corporate 成本（如果未知，收入上限2-5%）
- 减去净债务、少数股东权益；除以股份数量

SOTP折现 = (SOTP价格 − 市场价格) / SOTP价格。如果>20%，则标记（集团折扣）。

---

## 第7步：三角测量、敏感性、情景

```python
# 混合隐含价格
if sotp_price is None:
    blended = 0.5*implied_price_dcf + 0.5*implied_price_rel
else:
    blended = 0.4*implied_price_dcf + 0.3*implied_price_rel + 0.3*sotp_price

# 5x5敏感性网格
wacc_grid = [wacc + dx for dx in (-0.01, -0.005, 0, 0.005, 0.01)]
g_grid    = [0.015, 0.020, 0.025, 0.030, 0.035]
sens = {}
for w in wacc_grid:
    for g in g_grid:
        tv = fcff[-1]*(1+g)/(w-g)
        pv = sum(f/(1+w)**(i+1) for i,f in enumerate(fcff)) + tv/(1+w)**5
        sens[(w,g)] = (pv + cash - total_debt) / shares_out
```

还生成牛市 / 基准 / 熊市：将收入增长±300bps，EBIT利润率±200bps，WACC ∓100bps，终值g 3.0% / 2.5% / 1.5%。

---

## 第8步：回复用户

按以下顺序输出：

1. **标题结论** — 一句话：混合公允价值，与当前对比，百分比升/降，最乐观/悲观的方法。示例： "AAPL公允价值≈$215（混合），与当前$198 → ~9%升幅；DCF最乐观，达$228。"
2. **快照** — 行业，行业，市值，当前价格，3个月/12个月价格变化，LTM收入增长。
3. **三种方法总结** — 3列表格：方法 | 隐含价格 | 权重 | 简要理由。
4. **DCF构建** — 假设表格（增长路径、利润率、WACC组成部分、终值方法）+ 5年FCFF预测表格 + EV至股权桥接。
5. **同行比较** — 同行表格，包含市盈率前值、EV/收入、EV/EBITDA、毛利率、收入增长；最后一行 = 中位数；标记目标的溢价/折价。
6. **SOTP**（如果适用） — 部门表格 + 调整 + 股权价值。
7. **敏感性矩阵** — WACC × g网格（5×5），基准案例突出显示。
8. **情景** — 牛市 / 基准 / 熊市表格，包含杠杆 + 隐含价格。
9. **关键风险** — 3-5个要点：哪个假设对答案影响最大；什么会打破论点。

### 错误处理

| 缺失 / 边缘情况 | 操作 |
|---|---|
| yfinance返回`None`的Beta | 使用来自`references/wacc_erp_rates.md`的同行默认Beta |
| 负值LTM EBITDA | 跳过EV/EBITDA倍数；依赖EV/收入 + DCF |
| 负值LTM EPS | 跳过市盈率倍数；如果为正，使用预期市盈率，否则跳过 |
| 增长 > WACC在Gordon | 限制`g = wacc − 0.5%`并标记 |
| 历史少于3年 | 使用可用数据；标记数据置信度为"低" |
| 同行数据获取失败 | 从中位数中删除该同行；在输出中注明 |
| 没有SOTP的部门数据 | 跳过第6节；仅进行DCF + 相对估值 |

### 注意事项

- TTM数据滞后实时；同行倍数反映市场情绪（可能超调）
- DCF是垃圾进垃圾出；敏感性比点估计更重要
- yfinance数据非官方；对任何决策都与主要申报文件进行交叉验证
- 非财务建议

---

## 参考文件

- `references/dcf.md` — DCF方法 + 行业特定指导（软件、零售、金融、医疗保健、能源、制造业、CPG、电信、REITs、流媒体）
- `references/relative_valuation.md` — 同行选择、倍数调整规则、规则40、按主题划分的同行集
- `references/sotp.md` — 总和部分方法、集团折扣检测、催化剂
- `references/wacc_erp_rates.md` — 无风险利率、股权风险溢价、行业WACC基准、行业默认Beta
