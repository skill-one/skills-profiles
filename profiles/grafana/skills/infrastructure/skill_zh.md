# Grafana Cloud 基础设施监控

> **文档**: https://grafana.com/docs/grafana-cloud/monitor-infrastructure/

K8s + 主机 + 容器 + 云提供商遥测数据，主要通过 `grafana/k8s-monitoring` Helm 图表或 Alloy。

## 前置条件

- Grafana Cloud 堆栈，包含 Prometheus / Loki / Tempo 端点 + API 密钥（`metrics:write`, `logs:write`, `traces:write`）
- 对于 Kubernetes：一个集群 + `helm` 3.x + 指向该集群的 `kubectl` 上下文
- 对于主机 / Docker：节点上安装 Alloy

## 常见工作流

### 1. 集成 Kubernetes 集群（k8s-monitoring 图表）

```bash
# 1. 创建命名空间 + 密钥
kubectl create namespace monitoring
kubectl create secret generic grafana-cloud-secret \
  -n monitoring --from-literal=api-key=<your-api-key>

# 2. 安装 — values.yaml 参考于 references/k8s-monitoring-values.md
helm repo add grafana https://grafana.github.io/helm-charts && helm repo update
helm install k8s-monitoring grafana/k8s-monitoring \
  --version 4.1.4 -n monitoring -f values.yaml

# 3. 验证所有 Pod 都处于 Running 状态
kubectl get pods -n monitoring
# 期望 alloy-*, kube-state-metrics-*, node-exporter-* 等都 Ready。

# 4. 验证 metrics/logs/traces Alloy 中无错误日志
kubectl -n monitoring logs deploy/k8s-monitoring-alloy-metrics --tail=50 | grep -iE 'error|level=err' || echo "clean"

# 5. 验证遥测数据已到达 Grafana Cloud
#    PromQL 在 metrics 数据源上（应 > 0）:
#      sum(up{cluster="production-us-east"})
#    LogQL 在 Loki 上:
#      sum(count_over_time({cluster="production-us-east"}[5m]))
```

完整的 `values.yaml`、关键 PromQL、仪表板 ID（15520, 1860, 14282…）和告警规则：[`references/k8s-monitoring-values.md`](references/k8s-monitoring-values.md)。

### 2. 监控 Linux 主机

```alloy
# 1. /etc/alloy/config.alloy — 参考于 references/clouds-and-hosts.md 获取完整块
prometheus.exporter.unix "host"  { rootfs_path = "/" }
prometheus.scrape         "node" { targets = prometheus.exporter.unix.host.targets
                                   forward_to = [prometheus.remote_write.cloud.receiver] }
```

```bash
# 2. 重新加载 Alloy 并验证 unix 出口是否已启动
systemctl reload alloy
curl -s http://localhost:12345/api/v0/web/components | jq '.[] | select(.id|contains("prometheus.exporter.unix"))'

# 3. 在 Grafana Cloud 中验证 — 打开 "Node Exporter Full" 仪表板（ID 1860）
#    并从 `instance` 下拉菜单中选择您的主机。
```

### 3. 拉取 AWS / Azure / GCP 指标

配置数据源（完整 YAML 在 [`references/clouds-and-hosts.md`](references/clouds-and-hosts.md)），然后：

```bash
# 1. 配置后，重启 Grafana 以加载文件
# 2. 验证数据源 — Grafana → 连接 → 数据源 → "测试"
#    期望 "成功查询 CloudWatch 指标 API"（或类似）。
# 3. 确认查询 — 探索 → 数据源 → 指标 例如
#    CloudWatch 命名空间 AWS/EC2 指标 CPUUtilization，最近 1h。
```

## 故障排除

- 图表已安装但 Cloud 中无指标 → 检查 `grafana-cloud-secret` `api-key` 值；检查 Alloy 日志中的 `401`
- `kube-state-metrics` Pod Pending → 可能是 RBAC；重新应用图表的 CRDs/CRBs
- Node-exporter Pod CrashLoopBackOff → 通常与主机的 :9100 冲突；更改端口
- CloudWatch "访问被拒绝" → IAM 角色缺少 `cloudwatch:GetMetricData`, `cloudwatch:ListMetrics`

## 资源

- [`grafana/k8s-monitoring` 图表](https://github.com/grafana/k8s-monitoring-helm)
- [监控基础设施文档](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/)
- [CloudWatch 数据源](https://grafana.com/docs/grafana/latest/datasources/aws-cloudwatch/)
- [Azure Monitor 数据源](https://grafana.com/docs/grafana/latest/datasources/azure-monitor/)
- [Google Cloud Monitoring 数据源](https://grafana.com/docs/grafana/latest/datasources/google-cloud-monitoring/)
