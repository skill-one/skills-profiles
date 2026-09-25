# Grafana 仪表板

创建和管理生产就绪的 Grafana 仪表板，以实现全面的系统可观察性。

## 目的

设计有效的 Grafana 仪表板，用于监控应用程序、基础设施和业务指标。

## 何时使用

- 可视化 Prometheus 指标
- 创建自定义仪表板
- 实施SLO仪表板
- 监控基础设施
- 追踪业务KPI

## 仪表板设计原则

### 1. 信息层级

```
┌─────────────────────────────────────┐
│  关键指标（大数字）               │
├─────────────────────────────────────┤
│  主要趋势（时间序列）             │
├─────────────────────────────────────┤
│  详细指标（表格/热力图）           │
└─────────────────────────────────────┘
```

### 2. RED方法（服务）

- **Rate** - 每秒请求数
- **Errors** - 错误率
- **Duration** - 延迟/响应时间

### 3. USE方法（资源）

- **Utilization** - 资源繁忙的百分比时间
- **Saturation** - 队列长度/等待时间
- **Errors** - 错误计数

## 仪表板结构

### API监控仪表板

```json
{
  "dashboard": {
    "title": "API监控",
    "tags": ["api", "生产"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "title": "请求率",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "错误率%",
        "type": "graph",
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
            "legendFormat": "错误率"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [5], "type": "gt" },
              "operator": { "type": "and" },
              "query": { "params": ["A", "5m", "now"] },
              "type": "query"
            }
          ]
        },
        "gridPos": { "x": 12, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "P95延迟",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 8, "w": 24, "h": 8 }
      }
    ]
  }
}
```

**参考:** 查看 `assets/api-dashboard.json`

## 面板类型

### 1. 统计面板（单个值）

```json
{
  "type": "stat",
  "title": "总请求数",
  "targets": [
    {
      "expr": "sum(http_requests_total)"
    }
  ],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "orientation": "auto",
    "textMode": "auto",
    "colorMode": "value"
  },
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": 0, "color": "green" },
          { "value": 80, "color": "yellow" },
          { "value": 90, "color": "red" }
        ]
      }
    }
  }
}
```

### 2. 时间序列图

```json
{
  "type": "graph",
  "title": "CPU使用率",
  "targets": [
    {
      "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
    }
  ],
  "yaxes": [
    { "format": "percent", "max": 100, "min": 0 },
    { "format": "short" }
  ]
}
```

### 3. 表格面板

```json
{
  "type": "table",
  "title": "服务状态",
  "targets": [
    {
      "expr": "up",
      "format": "table",
      "instant": true
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": { "Time": true },
        "indexByName": {},
        "renameByName": {
          "instance": "实例",
          "job": "服务",
          "Value": "状态"
        }
      }
    }
  ]
}
```

### 4. 热力图

```json
{
  "type": "heatmap",
  "title": "延迟热力图",
  "targets": [
    {
      "expr": "sum(rate(http_request_duration_seconds_bucket[5m])) by (le)",
      "format": "heatmap"
    }
  ],
  "dataFormat": "tsbuckets",
  "yAxis": {
    "format": "s"
  }
}
```

## 变量

### 查询变量

```json
{
  "templating": {
    "list": [
      {
        "name": "namespace",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_pod_info, namespace)",
        "refresh": 1,
        "multi": false
      },
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_service_info{namespace=\"$namespace\"}, service)",
        "refresh": 1,
        "multi": true
      }
    ]
  }
}
```

### 在查询中使用变量

```
sum(rate(http_requests_total{namespace="$namespace", service=~"$service"}[5m]))
```

## 仪表板中的警报

```json
{
  "alert": {
    "name": "高错误率",
    "conditions": [
      {
        "evaluator": {
          "params": [5],
          "type": "gt"
        },
        "operator": { "type": "and" },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "reducer": { "type": "avg" },
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "5m",
    "frequency": "1m",
    "message": "错误率超过5%",
    "noDataState": "no_data",
    "notifications": [{ "uid": "slack-channel" }]
  }
}
```

## 仪表板配置

**dashboards.yml:**

```yaml
apiVersion: 1

providers:
  - name: "default"
    orgId: 1
    folder: "General"
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
```

## 常见仪表板模式

### 基础设施仪表板

**关键面板:**

- 每个节点的CPU利用率
- 每个节点的内存使用情况
- 磁盘I/O
- 网络流量
- 按命名空间划分的Pod数量
- 节点状态

**参考:** 查看 `assets/infrastructure-dashboard.json`

### 数据库仪表板

**关键面板:**

- 每秒查询数
- 连接池使用情况
- 查询延迟（P50、P95、P99）
- 活跃连接
- 数据库大小
- 复制延迟
- 慢查询

**参考:** 查看 `assets/database-dashboard.json`

### 应用程序仪表板

**关键面板:**

- 请求率
- 错误率
- 响应时间（分位数）
- 活跃用户/会话
- 缓存命中率
- 队列长度

## 最佳实践

1. **从模板开始**（Grafana社区仪表板）
2. **为面板和变量使用一致的命名**
3. **在行中分组相关指标**
4. **设置适当的时间范围**（默认：过去6小时）
5. **使用变量以实现灵活性**
6. **为面板添加描述以提供上下文**
7. **正确配置单位**
8. **为颜色设置有意义的阈值**
9. **跨仪表板使用一致的配色方案**
10. **使用不同的时间范围进行测试**

## 仪表板即代码

### Terraform配置

```hcl
resource "grafana_dashboard" "api_monitoring" {
  config_json = file("${path.module}/dashboards/api-monitoring.json")
  folder      = grafana_folder.monitoring.id
}

resource "grafana_folder" "monitoring" {
  title = "生产监控"
}
```

### Ansible配置

```yaml
- name: 部署Grafana仪表板
  copy:
    src: "{{ item }}"
    dest: /etc/grafana/dashboards/
  with_fileglob:
    - "dashboards/*.json"
  notify: restart grafana
```

## 相关技能

- `prometheus-configuration` - 用于指标收集
- `slo-implementation` - 用于SLO仪表板
