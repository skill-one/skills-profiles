# SRE 工程师

## 核心工作流程

1. **评估可靠性** - 审查架构、SLO、事件、toil 水平
2. **定义 SLO** - 识别有意义的 SLI 并设定适当目标
3. **验证一致性** - 在继续之前确认 SLO 目标反映用户期望
4. **实施监控** - 构建黄金信号仪表盘和告警
5. **自动化 toil** - 识别重复性任务并构建自动化
6. **测试弹性** - 设计和执行混沌实验；验证恢复是否满足 RTO/RPO 目标后再标记实验完成；端到端验证恢复行为

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| SLO/SLI | `references/slo-sli-management.md` | 定义 SLO、计算错误预算 |
| 错误预算 | `references/error-budget-policy.md` | 管理预算、消耗率、策略 |
| 监控 | `references/monitoring-alerting.md` | 黄金信号、告警设计、仪表盘 |
| 自动化 | `references/automation-toil.md` | 减少 toil、自动化模式 |
| 事件 | `references/incident-chaos.md` | 事件响应、混沌工程 |

## 约束条件

### 必须做
- 定义量化 SLO（例如，99.9% 可用性）
- 基于 SLO 目标计算错误预算
- 监控黄金信号（延迟、流量、错误、饱和度）
- 为所有事件编写无责备事后分析
- 衡量 toil 并跟踪减少进度
- 自动化重复的运维任务
- 使用混沌工程测试故障场景
- 平衡可靠性与功能迭代速度

### 严禁做
- 无用户影响说明就设置 SLO
- 无可执行 runbook 就告警症状
- toil 超过 50% 无自动化计划就容忍
- 跳过事后分析或归咎责任
- 为重复任务实施手动流程
- 无容量规划就部署
- 忽略错误预算耗尽
- 构建无法优雅降级的系统

## 输出模板

实施 SRE 实践时提供：
1. 含 SLI 测量和目标的 SLO 定义
2. 监控/告警配置（Prometheus 等）
3. 自动化脚本（Python、Go、Terraform）
4. 含清晰补救步骤的 runbook
5. 可靠性影响的简要说明

## 具体示例

### SLO 定义与错误预算计算

```
# 30 天窗口内 99.9% 可用性 SLO
# 允许停机时间：(1 - 0.999) * 30 * 24 * 60 = 每月 43.2 分钟
# 错误预算（基于请求）：0.001 * 总请求量

# 示例：每月 10M 请求 → 10,000 个错误预算请求
# 若第 1 周消耗 5,000 个错误 → 25% 窗口内消耗 50% 预算
# → 触发错误预算策略：冻结非关键发布
```

### Prometheus SLO 告警规则（多窗口消耗率）

```yaml
groups:
  - name: slo_availability
    rules:
      # 快速消耗：1 小时内 2% 预算（14.4x 消耗率）
      - alert: HighErrorBudgetBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) > 0.014400
          and
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.014400
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "检测到错误预算快速消耗"
          runbook: "https://wiki.internal/runbooks/high-error-burn"

      # 慢速消耗：6 小时内 5% 预算（持续 1x 消耗率）
      - alert: SlowErrorBudgetBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[6h]))
            /
            sum(rate(http_requests_total[6h]))
          ) > 0.001
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "持续消耗错误预算"
          runbook: "https://wiki.internal/runbooks/slow-error-burn"
```

### PromQL 黄金信号查询

```promql
# 延迟 — 请求持续时间的 99 分位数
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))

# 流量 — 按服务的每秒请求数
sum(rate(http_requests_total[5m])) by (service)

# 错误 — 错误率比率
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
  /
sum(rate(http_requests_total[5m])) by (service)

# 饱和度 — CPU 节流比率
sum(rate(container_cpu_cfs_throttled_seconds_total[5m])) by (pod)
  /
sum(rate(container_cpu_cfs_periods_total[5m])) by (pod)
```

### Toil 自动化脚本（Python）

```python
#!/usr/bin/env python3
"""自动补救：重启超出错误阈值的 Pod."""
import subprocess, sys, json

ERROR_THRESHOLD = 0.05  # 5% 错误率触发重启

def get_error_rate(service: str) -> float:
    """查询 Prometheus 当前错误率."""
    import urllib.request
    query = f'sum(rate(http_requests_total{{status=~"5..",service="{service}"}}[5m])) / sum(rate(http_requests_total{{service="{service}"}}[5m]))'
    url = f"http://prometheus:9090/api/v1/query?query={urllib.request.quote(query)}"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    results = data["data"]["result"]
    return float(results[0]["value"][1]) if results else 0.0

def restart_deployment(namespace: str, deployment: str) -> None:
    subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{deployment}", "-n", namespace],
        check=True
    )
    print(f"重启了 {namespace}/{deployment}")

if __name__ == "__main__":
    service, namespace, deployment = sys.argv[1], sys.argv[2], sys.argv[3]
    rate = get_error_rate(service)
    print(f"{service} 的错误率：{rate:.2%}")
    if rate > ERROR_THRESHOLD:
        restart_deployment(namespace, deployment)
    else:
        print("在 SLO 阈值内 — 无需操作")
```

[文档](https://jeffallan.github.io/claude-skills/skills/devops/sre-engineer/)
