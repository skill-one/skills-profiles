# SLO 实现

用于定义和实现服务级别指标（SLI）、服务级别目标（SLO）和错误预算的框架。

## 目的

使用 SLI、SLO 和错误预算实现可衡量的可靠性目标，以平衡可靠性与创新速度。

## 使用场景

- 定义服务可靠性目标
- 衡量用户感知的可靠性
- 实施错误预算
- 创建基于 SLO 的警报
- 追踪可靠性目标

## SLI/SLO/SLA 层级关系

```
SLA (服务级别协议)
  ↓ 与客户签订的合同
SLO (服务级别目标)
  ↓ 内部可靠性目标
SLI (服务级别指标)
  ↓ 实际测量
```

## 定义 SLI

### 常见 SLI 类型

#### 1. 可用性 SLI

```promql
# 成功请求 / 总请求
sum(rate(http_requests_total{status!~"5.."}[28d]))
/
sum(rate(http_requests_total[28d]))
```

#### 2. 延迟 SLI

```promql
# 低于延迟阈值的请求 / 总请求
sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
/
sum(rate(http_request_duration_seconds_count[28d]))
```

#### 3. 可靠性 SLI

```
# 成功写入 / 总写入
sum(storage_writes_successful_total)
/
sum(storage_writes_total)
```

**参考:** 查看 `references/slo-definitions.md`

## 设置 SLO 目标

### 可用性 SLO 示例

| SLO %  | 每月停机时间 | 每年停机时间 |
| ------ | -------------- | ------------- |
| 99%    | 7.2 小时      | 3.65 天     |
| 99.9%  | 43.2 分钟   | 8.76 小时    |
| 99.95% | 21.6 分钟   | 4.38 小时    |
| 99.99% | 4.32 分钟   | 52.56 分钟   |

### 选择合适的 SLO

**考虑:**

- 用户期望
- 业务需求
- 当前性能
- 可靠性成本
- 竞争对手基准

**示例 SLO:**

```yaml
slos:
  - name: api_availability
    target: 99.9
    window: 28d
    sli: |
      sum(rate(http_requests_total{status!~"5.."}[28d]))
      /
      sum(rate(http_requests_total[28d]))

  - name: api_latency_p95
    target: 99
    window: 28d
    sli: |
      sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
      /
      sum(rate(http_request_duration_seconds_count[28d]))
```

## 错误预算计算

### 错误预算公式

```
错误预算 = 1 - SLO 目标
```

**示例:**

- SLO: 99.9% 可用性
- 错误预算: 0.1% = 每月 43.2 分钟
- 当前错误: 0.05% = 每月 21.6 分钟
- 剩余预算: 50%

### 错误预算策略

```yaml
error_budget_policy:
  - remaining_budget: 100%
    action: 正常开发速度
  - remaining_budget: 50%
    action: 考虑推迟有风险的变化
  - remaining_budget: 10%
    action: 暂停非关键性变化
  - remaining_budget: 0%
    action: 功能冻结，专注于可靠性
```

**参考:** 查看 `references/error-budget.md`

## SLO 实现

### Prometheus 记录规则

```yaml
# SLI 记录规则
groups:
  - name: sli_rules
    interval: 30s
    rules:
      # 可用性 SLI
      - record: sli:http_availability:ratio
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[28d]))
          /
          sum(rate(http_requests_total[28d]))

      # 延迟 SLI (请求 < 500ms)
      - record: sli:http_latency:ratio
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
          /
          sum(rate(http_request_duration_seconds_count[28d]))

  - name: slo_rules
    interval: 5m
    rules:
      # SLO 合规性 (1 = 达到 SLO, 0 = 违反)
      - record: slo:http_availability:compliance
        expr: sli:http_availability:ratio >= bool 0.999

      - record: slo:http_latency:compliance
        expr: sli:http_latency:ratio >= bool 0.99

      # 剩余错误预算 (百分比)
      - record: slo:http_availability:error_budget_remaining
        expr: |
          (sli:http_availability:ratio - 0.999) / (1 - 0.999) * 100

      # 错误预算消耗率
      - record: slo:http_availability:burn_rate_5m
        expr: |
          (1 - (
            sum(rate(http_requests_total{status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          )) / (1 - 0.999)
```

### SLO 警报规则

```yaml
groups:
  - name: slo_alerts
    interval: 1m
    rules:
      # 快速消耗: 14.4x 消耗率, 1 小时窗口
      # 1 小时内消耗 2% 错误预算
      - alert: SLOErrorBudgetBurnFast
        expr: |
          slo:http_availability:burn_rate_1h > 14.4
          and
          slo:http_availability:burn_rate_5m > 14.4
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "检测到快速错误预算消耗"
          description: "错误预算消耗率 {{ $value }}x"

      # 慢速消耗: 6x 消耗率, 6 小时窗口
      # 6 小时内消耗 5% 错误预算
      - alert: SLOErrorBudgetBurnSlow
        expr: |
          slo:http_availability:burn_rate_6h > 6
          and
          slo:http_availability:burn_rate_30m > 6
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "检测到慢速错误预算消耗"
          description: "错误预算消耗率 {{ $value }}x"

      # 错误预算耗尽
      - alert: SLOErrorBudgetExhausted
        expr: slo:http_availability:error_budget_remaining < 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SLO 错误预算耗尽"
          description: "剩余错误预算: {{ $value }}%"
```

## SLO 仪表盘

**Grafana 仪表盘结构:**

```
┌────────────────────────────────────┐
│ SLO 合规性 (当前)                 │
│ ✓ 99.95% (目标: 99.9%)          │
├────────────────────────────────────┤
│ 剩余错误预算: 65%                │
│ ████████░░ 65%                   │
├────────────────────────────────────┤
│ SLI 趋势 (28 天)                 │
│ [时间序列图]                     │
├────────────────────────────────────┤
│ 消耗率分析                       │
│ [按时间窗口的消耗率]             │
└────────────────────────────────────┘
```

**示例查询:**

```promql
# 当前 SLO 合规性
sli:http_availability:ratio * 100

# 剩余错误预算
slo:http_availability:error_budget_remaining

# 当前消耗率下错误预算耗尽的天数
(slo:http_availability:error_budget_remaining / 100)
*
28
/
(1 - sli:http_availability:ratio) * (1 - 0.999)
```

## 其他模式和模板

更详细的模板和实例在 `references/details.md` 中。阅读该文件以获取完整模式库。
