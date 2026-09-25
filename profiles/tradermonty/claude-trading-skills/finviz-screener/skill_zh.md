# FinViz 筛选器

## 概述

将自然语言股票筛选请求转换为 FinViz 筛选器过滤代码，构建 URL，并在 Chrome 中打开。公共筛选器无需 API 密钥；FINVIZ Elite 会自动检测 `$FINVIZ_API_KEY` 以实现增强功能。

**主要功能：**
- 自然语言 → 过滤代码映射（日语 + 英语）
- 带视图类型和排序顺序选择的 URL 构建
- Elite/公共自动检测（环境变量或显式标志）
- Chrome 优先浏览器打开，带操作系统适配回退
- 严格过滤验证以防止 URL 注入

---

## 何时使用此技能

**显式触发器：**
- "寻找高股息成长型小型股"
- "Find oversold large caps near 52-week lows"
- "希望筛选技术板块的便宜股"
- "筛选有内部人士买入的股票"
- "在 FinViz 上显示突破候选股"
- "Show me high-growth small caps on FinViz"
- "寻找股息收益率 5% 以上且 ROE 15% 以上的股票"

**隐式触发器：**
- 用户使用基本面或技术术语描述股票筛选标准
- 用户提及 FinViz 筛选器或股票过滤
- 用户询问具有特定财务特征的股票

**不适用情况：**
- 深入分析特定股票的基本面（使用 us-stock-analysis）
- 持仓投资组合审查（使用 portfolio-manager）
- 图像上的图表模式分析（使用 technical-analyst）
- 基于盈利的筛选（使用 earnings-trade-analyzer 或 pead-screener）

---

## 工作流程

### 第 1 步：加载过滤参考

读取过滤知识库：

```bash
cat references/finviz_screener_filters.md
```

### 第 2 步：解释用户请求

将用户的自然语言请求映射到 FinViz 过滤代码。使用下表中的常见概念映射表进行快速翻译，并参考完整过滤列表进行精确代码选择。

**注意：** 对于范围标准（例如，"dividend 3-8%"，"P/E between 10 and 20"），使用 `{from}to{to}` 范围语法作为单个过滤标记（例如，`fa_div_3to8`，`fa_pe_10to20`），而不是组合 `_o` 和 `_u` 过滤器。

**常见概念映射：**

| 用户概念（英文） | 用户概念（日文） | 过滤代码 |
|---|---|---|
| 高股息 | 高配当 | `fa_div_o3` 或 `fa_div_o5` |
| 小型股 | 小型株 | `cap_small` |
| 中型股 | 中型株 | `cap_mid` |
| 大型股 | 大型株 | `cap_large` |
| 超大型股 | 超大型株 | `cap_mega` |
| 割安 | 割安 | `fa_pe_u20,fa_pb_u2` |
| 成长股 | 成長株 | `fa_epsqoq_o25,fa_salesqoq_o15` |
| 售卖过剩 | 売られすぎ | `ta_rsi_os30` |
| 购买过剩 | 買われすぎ | `ta_rsi_ob70` |
| 52周高值附近 | 52週高値付近 | `ta_highlow52w_b0to5h` |
| 52周安值附近 | 52週安値付近 | `ta_highlow52w_a0to5l` |
| 突破 | ブレイクアウト | `ta_highlow52w_b0to5h,sh_relvol_o1.5` |
| 技术 | テクノロジー | `sec_technology` |
| 医疗保健 | ヘルスケア | `sec_healthcare` |
| 能源 | エネルギー | `sec_energy` |
| 金融 | 金融 | `sec_financial` |
| 半导体 | 半導体 | `ind_semiconductors` |
| 生物技术 | バイオテク | `ind_biotechnology` |
| 美国股票 | 米国株 | `geo_usa` |
| 黑字 | 黒字 | `fa_pe_profitable` |
| 高 ROE | 高ROE | `fa_roe_o15` 或 `fa_roe_o20` |
| 低负债 | 低負債 | `fa_debteq_u0.5` |
| 内部人士买入 | インサイダー買い | `sh_insidertrans_verypos` |
| 短线挤压 | ショートスクイーズ | `sh_short_o20,sh_relvol_o2` |
| 增配 | 增配 | `fa_divgrowth_3yo10` |
| 深值 | ディープバリュー | `fa_pb_u1,fa_pe_u10` |
| 动量 | モメンタム | `ta_perf_13wup,ta_sma50_pa,ta_sma200_pa` |
| 防御性 | ディフェンシブ | `ta_beta_u0.5` 或 `sec_utilities,sec_consumerdefensive` |
| 高流动性/高成交量 | 高出来高 | `sh_avgvol_o500` 或 `sh_avgvol_o1000` |
| 高值からの押し目 | 高値からの押し目 | `ta_highlow52w_10to30-bhx` |
| 安値圏リバーサル | 安値圏リバーサル | `ta_highlow52w_10to30-alx` |
| 急落後反発 | 急落後反発 | `ta_highlow52w_b20to30h,ta_rsi_os40` |
| AI 主题 | AIテーマ | `--themes "artificialintelligence"` |
| 网络安全主题 | サイバーセキュリティ | `--themes "cybersecurity"` |
| AI + 网络安全 | AI＆サイバーセキュリティ | `--themes "artificialintelligence,cybersecurity"` |
| AI 云子主题 | AIクラウド | `--subthemes "aicloud"` |
| AI 计算子主题 | AI半導体 | `--subthemes "aicompute"` |
| 配当 3-8%（排除陷阱） | 配当3-8%（トラップ除外）| `fa_div_3to8` |
| 中值 P/E | 適正PER帯 | `fa_pe_10to20` |
| EV 割安 | EV割安 | `fa_evebitda_u10` |
| 来週决算 | 来週決算 | `earningsdate_nextweek` |
| 直近 IPO | 直近IPO | `ipodate_thismonth` |
| 目标股价以上 | 目標株価以上 | `targetprice_a20` |
| 最新新闻存在 | 最新ニュースあり | `news_date_today` |
| 機構保有率高 | 高機構保有率 | `sh_instown_o60` |
| 浮动股少 | 浮動株少 | `sh_float_u20` |
| 史上最高值附近 | 史上最高値付近 | `ta_alltime_b0to5h` |
| 高波动性 | 高ボラティリティ | `ta_averagetruerange_o1.5` |

### 第 3 步：展示过滤选择

执行前，以表格形式展示所选过滤条件供用户确认：

```markdown
| 类型 | 值 | 含义 |
|---|---|---|
| 主题 | artificialintelligence | 人工智能 |
| 子主题 | aicloud | AI - 云计算与基础设施 |
| 过滤器 | cap_small | 小型股 ($300M–$2B) |
| 过滤器 | fa_div_o3 | 股息收益率 > 3% |
| 过滤器 | fa_pe_u20 | P/E < 20 |
| 过滤器 | geo_usa | 美国 |

视图：概览 (v=111)
模式：公共 / Elite (自动检测)
```

询问用户是否确认或调整，然后继续。

### 第 4 步：执行脚本

运行筛选器脚本以构建 URL 并打开 Chrome：

```bash
python3 scripts/open_finviz_screener.py \
  --filters "cap_small,fa_div_o3,fa_pe_u20,geo_usa" \
  --view overview

# 仅主题筛选（无需 --filters）
python3 scripts/open_finviz_screener.py \
  --themes "artificialintelligence,cybersecurity" \
  --url-only

# 主题 + 子主题 + 过滤器组合
python3 scripts/open_finviz_screener.py \
  --themes "artificialintelligence" \
  --subthemes "aicloud,aicompute" \
  --filters "cap_midover" \
  --url-only
```

**脚本参数：**
- `--filters` (可选): 逗号分隔的过滤代码。**注意：** `theme_*` 和 `subtheme_*` 标记不在此处使用 — 使用 `--themes` / `--subthemes` 代替。
- `--themes` (可选): 逗号分隔的主题缩写（例如，`artificialintelligence,cybersecurity`）。接受纯缩写或 `theme_` 前缀值。
- `--subthemes` (可选): 逗号分隔的子主题缩写（例如，`aicloud,aicompute`）。接受纯缩写或 `subtheme_` 前缀值。
- `--elite`: 强制 Elite 模式（如果未设置，则从 `$FINVIZ_API_KEY` 自动检测）
- `--view`: 视图类型 — 概览、估值、财务、技术、所有权、表现、自定义
- `--order`: 排序顺序（例如，`-marketcap`，`dividendyield`，`-change`）
- `--url-only`: 仅打印 URL 而不打开浏览器

必须提供至少一个 `--filters`、`--themes` 或 `--subthemes`。

### 第 5 步：报告结果

打开筛选器后，报告：
1. 构建的 URL
2. 使用的 Elite 或公共模式
3. 应用过滤器的摘要
4. 建议的下一步操作（例如，"按股息收益率排序"，"切换到财务视图以查看详细比率"）

---

## 使用配方

从重复使用中提炼出的实际筛选模式。每个配方都包括起始过滤器集、推荐视图和迭代优化的提示。

### 配方 1：高股息成长股（Kanchi 风格）

**目标：** 高收益率 + 股息增长 + 盈利增长，排除收益率陷阱。

```
--filters "fa_div_3to8,fa_sales5years_pos,fa_eps5years_pos,fa_divgrowth_5ypos,fa_payoutratio_u60,geo_usa"
--view financial
```

| 过滤代码 | 目的 |
|---|---|
| `fa_div_3to8` | 收益率 3-8%（限制高收益率陷阱） |
| `fa_sales5years_pos` | 5 年销售增长为正 |
| `fa_eps5years_pos` | 5 年 EPS 增长为正 |
| `fa_divgrowth_5ypos` | 5 年股息增长为正 |
| `fa_payoutratio_u60` | 派息比率 < 60%（可持续性） |
| `geo_usa` | 美国上市股票 |

**迭代优化：** 从宽泛开始使用 `fa_div_o3` → 查看结果 → 添加 `fa_div_3to8` 限制收益率 → 添加 `fa_payoutratio_u60` 排除陷阱 → 切换到 `financial` 视图查看派息和增长率列。

### 配方 2：Minervini 趋势模板 + VCP

**目标：** 处于阶段 2 上升趋势的股票，波动性收缩（VCP 设置）。

```
--filters "ta_sma50_pa,ta_sma200_pa,ta_sma200_sb50,ta_highlow52w_0to25-bhx,ta_perf_26wup,sh_avgvol_o300,cap_midover"
--view technical
```

| 过滤代码 | 目的 |
|---|---|
| `ta_sma50_pa` | 价格高于 50 日 SMA |
| `ta_sma200_pa` | 价格高于 200 日 SMA |
| `ta_sma200_sb50` | 200 日 SMA 低于 50 日 SMA（上升趋势） |
| `ta_highlow52w_0to25-bhx` | 52 周高值的 25% 以内 |
| `ta_perf_26wup` | 26 周正表现 |
| `sh_avgvol_o300` | 平均成交量 > 300K |
| `cap_midover` | 中型股及以上 |

**VCP 收缩过滤器（添加以缩小范围）：** `ta_volatility_wo3,ta_highlow20d_b0to5h,sh_relvol_u1` — 低周波动性，接近 20 日高值，平均成交量低于平均水平（收缩信号）。

### 配方 3：被低估的成长股

**目标：** 基本面强劲的公司近期大幅下跌 — 可能的均值回归候选股。

```
--filters "fa_sales5years_o5,fa_eps5years_o10,fa_roe_o15,fa_salesqoq_pos,fa_epsqoq_pos,ta_perf_13wdown,ta_highlow52w_10to30-bhx,cap_large,sh_avgvol_o200"
--view overview
```

| 过滤代码 | 目的 |
|---|---|
| `fa_sales5years_o5` | 5 年销售增长 > 5% |
| `fa_eps5years_o10` | 5 年 EPS 增长 > 10% |
| `fa_roe_o15` | ROE > 15% |
| `fa_salesqoq_pos` | QoQ 销售增长为正 |
| `fa_epsqoq_pos` | QoQ EPS 增长为正 |
| `ta_perf_13wdown` | 13 周负表现 |
| `ta_highlow52w_10to30-bhx` | 10-30% 低于 52 周高值 |
| `cap_large` | 大型股 |
| `sh_avgvol_o200` | 平均成交量 > 200K |

**查看后：** 切换到 `valuation` 视图检查 P/E 和 P/S 以确定入场吸引力。

### 配方 4：反转股

**目标：** 盈利曾经下降的公司现在显示出复苏 — 底部捕捞结合基本面确认。

```
--filters "fa_eps5years_neg,fa_epsqoq_pos,fa_salesqoq_pos,ta_highlow52w_b30h,ta_perf_13wup,cap_smallover,sh_avgvol_o200"
--view performance
```

| 过滤代码 | 目的 |
|---|---|
| `fa_eps5years_neg` | 5 年 EPS 增长为负（先前下降） |
| `fa_epsqoq_pos` | QoQ EPS 增长为正（复苏） |
| `fa_salesqoq_pos` | QoQ 销售增长为正（复苏） |
| `ta_highlow52w_b30h` | 52 周高值的 30% 以内（不在底部） |
| `ta_perf_13wup` | 13 周正表现 |
| `cap_smallover` | 小型股及以上 |
| `sh_avgvol_o200` | 平均成交量 > 200K |

### 配方 5：动量交易候选股

**目标：** 近 52 周高值的短期动量领导者，成交量增加。

```
--filters "ta_sma50_pa,ta_sma200_pa,ta_highlow52w_b0to3h,ta_perf_4wup,sh_relvol_o1.5,sh_avgvol_o1000,cap_midover"
--view technical
```

| 过滤代码 | 目的 |
|---|---|
| `ta_sma50_pa` | 价格高于 50 日 SMA |
| `ta_sma200_pa` | 价格高于 200 日 SMA |
| `ta_highlow52w_b0to3h` | 52 周高值的 3% 以内 |
| `ta_perf_4wup` | 4 周正表现 |
| `sh_relvol_o1.5` | 相对成交量 > 1.5x |
| `sh_avgvol_o1000` | 平均成交量 > 1M |
| `cap_midover` | 中型股及以上 |

### 配方 6：主题筛选（AI + 子主题深入挖掘）

**目标：** 查找中型股以上专注于云计算基础设施和计算加速的 AI 股票。

```
--themes "artificialintelligence"
--subthemes "aicloud,aicompute"
--filters "cap_midover"
--view overview
```

| 类型 | 值 | 目的 |
|---|---|---|
| 主题 | `artificialintelligence` | AI 主题宇宙 |
| 子主题 | `aicloud` | 云计算与基础设施垂直 |
| 子主题 | `aicompute` | 计算与加速垂直 |
| 过滤器 | `cap_midover` | 中型股及以上 |

**多主题示例：** `--themes "artificialintelligence,cybersecurity"` 选择被标记为任一主题的股票（通过 `|` 分组的 OR 逻辑）。

### 提示：迭代优化模式

筛选最佳实践是作为对话，而不是一次性查询：

1. **从宽泛开始** — 使用 3-4 个核心过滤器获取初始结果集
2. **查看数量** — 如果结果过多（>100），添加收紧过滤器；如果过少（<5），放宽约束
3. **切换视图** — 从 `overview` 开始快速扫描，然后切换到 `financial` 或 `valuation` 进行深度检查
4. **添加技术指标** — 在确认基本面质量后，添加 `ta_` 过滤器以把握入场时机
5. **保存并迭代** — 收藏 URL，然后逐个调整过滤器以了解其影响

---

## 资源

- `references/finviz_screener_filters.md` — 完整过滤代码参考，包含自然语言关键词（包括行业代码示例；完整 142 代码列表在行业代码部分）
- `scripts/open_finviz_screener.py` — URL 构建器和 Chrome 打开器
