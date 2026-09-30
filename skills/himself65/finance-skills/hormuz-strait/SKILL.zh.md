---
name: hormuz-strait
description: 从霍尔木兹海峡监控面板检查霍尔木兹海峡的实时状态：开放、限制或关闭状态，油轮通行与正常通行对比，搁浅船只，布伦特油价影响，战争风险保险水平，货物吞吐量，油轮运费率，外交发展动态以及全球贸易影响。当用户询问关于霍尔木兹海峡或波斯湾在石油、航运或地缘政治风险背景下的情况时，无论霍尔木兹海峡是否开放、咽喉要道或通行中断、海湾油轮交通、战争风险溢价、中东航运路线或能源供应链风险，均使用此技能。
---

# Hormuz海峡监控技能

从[Hormuz海峡监控](https://hormuzstraitmonitor.com)仪表板API获取Hormuz海峡的实时状态。涵盖航运通行、油价、搁浅船只、保险风险、外交状态、全球贸易影响和危机时间线。

**此技能仅读不写。** 它获取的是公开的仪表板数据——无需认证。

---

## 第1步：获取仪表板数据

使用`curl`获取仪表板API：

```bash
curl -s https://hormuzstraitmonitor.com/api/dashboard
```

解析JSON响应。API返回`{ "success": true, "data": { ... }, "timestamp": "..." }`。

如果`success`为`false`或请求失败，则告知用户监控暂时不可用，并建议直接访问https://hormuzstraitmonitor.com。

---

## 第2步：识别用户需求

将用户的请求与相关数据部分进行匹配。如果用户要求一般状态更新，则呈现所有部分。如果他们询问具体内容，则专注于相关部分。

| 用户请求 | 数据部分 | 关键字段 |
|---|---|---|
| 一般状态 / "Hormuz海峡是否开放？" | `straitStatus` | `status`, `since`, `description` |
| 船运交通 / 通行次数 | `shipCount` | `currentTransits`, `last24h`, `normalDaily`, `percentOfNormal` |
| 油价影响 | `oilPrice` | `brentPrice`, `change24h`, `changePercent24h`, `sparkline` |
| 搁浅 / 停滞船只 | `strandedVessels` | `total`, `tankers`, `bulk`, `other`, `changeToday` |
| 保险 / 战争风险 | `insurance` | `level`, `warRiskPercent`, `normalPercent`, `multiplier` |
| 货物吞吐量 | `throughput` | `todayDWT`, `averageDWT`, `percentOfNormal`, `last7Days` |
| 外交局势 | `diplomacy` | `status`, `headline`, `parties`, `summary` |
| 全球贸易影响 | `globalTradeImpact` | `percentOfWorldOilAtRisk`, `estimatedDailyCostBillions`, `affectedRegions`, `lngImpact`, `alternativeRoutes`, `supplyChainImpact` |
| 危机时间线 / 事件 | `crisisTimeline` | `events[]` with `date`, `type`, `title`, `description` |
| 油轮运费率 / VLCC运费率 | `tankerRates` | `currentRate`, `preCrisisRate`, `changePercent`, `route`, `vesselType`, `trend`, `unit` |
| 最新新闻 | `news` | `title`, `source`, `url`, `publishedAt`, `description` |

---

## 第3步：呈现数据

为金融研究清晰地格式化结果。根据用户请求的内容调整呈现方式。

### 一般状态简报（默认）

当用户要求一般更新时，涵盖这些部分——航运正常运营时每部分一行，在存在活跃中断的地方提供更深入的细节：

1. **海峡状态** — 首先说明当前状态（例如，"开放"、"限制"、"关闭"），持续了多久，以及描述
2. **船运交通** — 当前通行次数，过去24小时计数，以及正常百分比
3. **油价** — 布伦特油价及24小时变化
4. **搁浅船只** — 总数按类型细分，以及今日变化
5. **保险风险** — 风险等级，战争风险溢价百分比，以及与正常的倍数对比
6. **货物吞吐量** — 今日DWT与平均值对比，正常百分比
7. **外交状态** — 当前状态，头条，以及简要概述
8. **全球贸易影响** — 处于风险中的世界石油百分比，估计每日成本，以及最受影响的地区
9. **油轮运费率** — 基准航线上当前VLCC率与危机前基线对比，以及趋势方向

### 格式化指南

- 使用表格呈现结构化数据（船只计数、受影响地区、替代航线）
- 突出异常值——如果`percentOfNormal`低于80%或高于120%，则指出
- 对于`oilPrice.sparkline`，描述趋势（上升、下降、稳定），而不是列出原始数字
- 对于`throughput.last7Days`，描述趋势方向
- 显示`lastUpdated`时间戳，以便用户了解数据新鲜度
- 对于新闻项，包括来源和链接
- 对于危机时间线事件，按时间顺序呈现，并标注事件类型

### 风险评估

根据数据，提供简要的风险评估。`insurance.level`值以大写返回：

| 保险等级 | 解释 |
|---|---|
| `NORMAL` | 无高风险——航运正常运营 |
| `ELEVATED` | 存在部分中断担忧——密切监控 |
| `HIGH` | 显著风险——存在活跃中断或可信威胁 |
| `CRITICAL` | 严重中断——对全球石油供应产生重大影响 |
| `EXTREME` | 实际关闭——战争风险溢价处于数十年高位，大部分商业交通停滞 |

如果海峡状态不是完全开放，则突出：
- 对全球贸易的估计每日成本
- 最受影响的地区及其石油依赖程度
- 可用的替代航线，包括额外的通行天数和成本
- 如适用，LNG影响
- 战略石油储备（SPR）状态（以天计）

---

## 第4步：回复用户

- 首先提供最重要的信息：海峡状态和任何活跃中断
- 包括数据新鲜度（`lastUpdated`时间戳）
- 如果情况升高或更糟，主动包含全球贸易影响概述
- 对于常规的"一切正常"状态，保持回复简洁；对于活跃事件，则扩展内容
- 添加免责声明：数据源自Hormuz海峡监控，可能存在延迟

---

## 参考文件

- `references/api_schema.md` — 完整API响应模式，包含字段描述和数据类型

需要精确的字段名或数据类型详情时，请阅读参考文件。
