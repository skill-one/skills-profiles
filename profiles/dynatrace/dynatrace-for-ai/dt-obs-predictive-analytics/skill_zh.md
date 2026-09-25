# 预测分析技能

使用 DQL 和 Dynatrace 分析器工具预测资源饱和度、检测趋势、分析异常并描述信号行为。

## 分析领域

| 序号 | 领域 | 在以下情况下使用 |
|---|---|-----------|
| 1 | **预测和预测** | 预测未来指标值用于容量规划、成本估算或主动警报 |
| 2 | **检测变化** | 指标 *发生变化* — 查找信号特征何时改变，无论是否跨越了限制 |
| 3 | **检测违规** | 指标 *当前超出范围* — 查找超出或低于可接受范围的实体 |
| 4 | **时间序列特征** | 在进一步分析之前描述信号的季节性、噪声水平和趋势 |

---

## 选择合适的检测工具

**最重要的决定**：你是在问“这个指标 *是否改变*？”还是“这个指标 *当前是否错误*？”？

| 问题 | 工具 | 原因 |
|----------|------|-----|
| “这个指标在过去 N 小时内是否改变？” | `timeseries-novelty-detection` | 检测信号特征何时改变（尖峰、阶跃、趋势开始、可变性变化）而无需已知可接受限制 |
| “哪些服务最近出现尖峰或下降？” | `timeseries-novelty-detection` with `SPIKE` / `CHANGE_IN_VALUES` | 查找发生变化的特定实体和时间戳；对于稳定信号返回空结果 |
| “CPU 何时开始呈上升趋势？” | `timeseries-novelty-detection` with `TREND_IN_VALUES` | 精确确定方向性变化的开始 |
| “哪些主机当前 CPU 超过 90%？” | `static-threshold-analyzer` | 已知固定限制 — 超出时触发警报 | 也可以使用标准 DQL 查询完成，但该工具提供内置违规计数、滑动窗口和警报逻辑 |
| “哪些服务当前负载高于正常水平？” | `adaptive-anomaly-detector` | 从数据中学习正常分布并标记持续阈值违规 |
| “哪些服务当前与其周度模式相比处于高位？” | `seasonal-baseline-anomaly-detector` | 在判断异常之前考虑小时/星期模式 |

### 简单语言中的决策规则

- **使用 `timeseries-novelty-detection`** 当问题包含“改变”、“变化”、“尖峰”、“下降”、“开始”、“何时”或“是否发生任何异常”。该工具回答 *是否* 发生变化以及 *何时*。它不需要预定义阈值。
- **使用异常检测器** (`adaptive`、`seasonal` 或 `static`) 当问题是关于 *持续* 或 *当前* 状态相对于预期范围： “哪些最高”、“谁违规”、“什么超过 X”。这些工具在滑动窗口内计数违规样本 — 它们确认 *多长时间* 事情变差，而不是信号是否改变。

> **陷阱**：在广泛的主机上运行 `adaptive-anomaly-detector` 来回答“哪个服务负载改变？”通常会将每个有任何变化的服务的标记，产生低信噪比结果。首先使用 `timeseries-novelty-detection` 识别负载特征真正改变的实体，然后使用异常检测器测量这些特定信号的严重程度。

## 何时使用此技能

- **容量**： “哪些主机将在未来 30 天内达到 90% CPU？”
- **预测**： “预测未来 7 天的服务请求量”
- **趋势**： “我们的 Kubernetes 节点内存使用量是否在增长？”
- **异常**： “哪些服务当前错误率异常？”
- **基线**： “今天的流量与上周相比如何？”
- **信号配置文件**： “在我设置警报之前，这个指标是否具有季节性或趋势？”

---

## 重要限制

**Dynatrace 预测分析器仅支持单变量预测** — 基于其自身历史值预测一个指标。多变量预测（使用多个指标作为输入）需要外部工具（Python、R、Azure AutoML）。

**工具规则**：使用 Dynatrace 工具进行分析：`timeseries-forecast`、`adaptive-anomaly-detector`、`seasonal-baseline-anomaly-detector`、`static-threshold-analyzer` 和 `timeseries-novelty-detection`。使用 `execute-dql` 进行 DQL 查询。

**结果分析规则**：始终直接从原始工具输出生成和分析结果。内联导出所有数字、趋势和结论。

---

## 结果呈现格式

始终将预测结果以结构化表格呈现：

| 列 | 内容 |
|--------|---------|
| 排名 | 🥇 🥈 🥉 按紧急程度或幅度排序 |
| 信号/实体 | 指标名称和实体或维度 |
| 最后实际值 | 历史序列中最新的非空值 |
| 预测 | 在视野结束时的时间点预测值 |
| 范围 | 在同一视野时间点的下限 – 上限置信带 |
| 趋势 | 从最后实际值到预测的百分比变化：🔴 >+20% / 🟠 +5–20% / 🟢 ±5% 稳定 / 🔵 −5–20% 下降 / ⚫ <−20% 尖峰下降 |
| 操作 | ✅ 无操作 / ⚠️ 监控 / 🔴 立即行动 |

始终在表格后附上 **关键发现** 部分（3–5 个要点，按优先级排序）。

---

## 核心DQL技术

DQL 没有内置的 `forecast` 函数。对于前瞻性预测，使用 `timeseries-forecast`（参见 `references/forecasting-analyzer.md`）。

### 关键DQL规则

1. `timeseries` 返回数组 — 每个时间槽每个实体一个值
2. `arrayLast(arr)` = 最新的值；`arrayFirst(arr)` = 最旧的
3. 增长 = `(arrayLast - arrayFirst) / 时间间隔数量`
4. 在排序前始终 `filter isNotNull(field)` 以避免空排序问题
5. 当除以 `Long` 字段时使用 `toLong()` 以避免类型错误
6. 在 DQL 显示字段中使用 `dt.smartscape.*` 而不是已弃用的 `dt.entity.*`；在 `by:{}` 分组子句中使用 `dt.smartscape.*` 进行实体级查询

---

## 标准查询模式

### 移动平均趋势

```dql
timeseries cpu = avg(dt.host.cpu.usage), from: now()-24h, interval: 1h, by: {dt.smartscape.host}
| fieldsAdd moving_avg = arrayMovingAvg(cpu, 4)
| fieldsAdd current = arrayLast(cpu)
| fieldsAdd trend = arrayLast(cpu) - arrayFirst(cpu)
| filter isNotNull(current)
| sort trend desc
| limit 20
| fields dt.smartscape.host, current, trend, moving_avg
```

### 饱和风险分类

```dql
timeseries cpu = avg(dt.host.cpu.usage), from: now()-7d, interval: 1h, by: {dt.smartscape.host}
| fieldsAdd p95 = arrayPercentile(cpu, 95)
| fieldsAdd saturation_risk = if(p95 > 85, "HIGH", else: if(p95 > 70, "MEDIUM", else: "LOW"))
| filter isNotNull(p95)
| sort p95 desc
| fields dt.smartscape.host, p95, saturation_risk
```

### 饱和预测天数

```dql
timeseries cpu = avg(dt.host.cpu.usage), from: now()-30d, interval: 1d, by: {dt.smartscape.host}
| fieldsAdd current = arrayLast(cpu)
| fieldsAdd daily_growth = (arrayLast(cpu) - arrayFirst(cpu)) / 30
| filter isNotNull(current)
| fieldsAdd days_to_saturation = if(daily_growth > 0, toLong((90 - current) / daily_growth), else: 9999)
| sort days_to_saturation asc
| limit 20
| fields dt.smartscape.host, current, daily_growth, days_to_saturation
```

### 异常评分

```dql
timeseries cpu = avg(dt.host.cpu.usage), from: now()-24h, interval: 1h, by: {dt.smartscape.host}
| fieldsAdd baseline_avg = arrayAvg(cpu)
| fieldsAdd current = arrayLast(cpu)
| fieldsAdd anomaly_score = if(isNotNull(current) and isNotNull(baseline_avg), abs(current - baseline_avg), else: 0)
| sort anomaly_score desc
| limit 20
| fields dt.smartscape.host, current, baseline_avg, anomaly_score
```

### 指标发现

在预测之前，通过关键字发现可用指标：

```dql
metrics from: now() - 1h
| filter contains(metric.key, "cpu")
| summarize count(), by: {metric.key}
| sort `count()` desc
```

---

## 参考指南

- **`references/forecasting-analyzer.md`** — `timeseries-forecast` 工具：
  数据要求、参数参考、时间间隔选择、视野限制、常见陷阱
- **`references/capacity-forecasting.md`** — CPU/内存/磁盘/K8s 饱和预测；
  多资源风险评分；DQL 预测天数模式
- **`references/anomaly-scoring.md`** — `adaptive-anomaly-detector`、`seasonal-baseline-anomaly-detector`、
  `static-threshold-analyzer`；DQL 偏差评分
- **`references/novelty-detection.md`** — `timeseries-novelty-detection` 工具：尖峰、下降、阶跃变化，
  趋势开始、可变性变化；所有新颖类型；参数参考；示例
- **`references/trend-detection.md`** — `timeseries-novelty-detection` 用于趋势开始和变化点；
  周比连接；增长率加速检测

## 相关技能

- **dt-dql-essentials** — DQL 语法、`timeseries` 命令规则、数组函数参考
- **dt-obs-hosts** — 主机和进程指标目录
- **dt-obs-services** — 服务 RED 指标用于服务级趋势分析
- **dt-obs-problems** — Davis AI 问题历史用于异常关联
