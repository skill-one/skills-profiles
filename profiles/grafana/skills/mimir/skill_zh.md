# Grafana Mimir

> **文档**: https://grafana.com/docs/mimir/latest/

水平可扩展、多租户、长期存储 Prometheus + OpenTelemetry 指标。

## 前置条件

- Docker（用于快速启动）或 Kubernetes 集群（用于 Helm）
- 生产用对象存储桶（S3/GCS/Azure）—— 开发用仅限文件系统
- 能够远程写入 Mimir 推送端点的 Prometheus 或 Alloy

## 常见工作流

### 1. 本地部署单体 Mimir

```yaml
# demo.yaml
target: all
multitenancy_enabled: false

blocks_storage:
  backend: filesystem
  bucket_store:
    sync_dir: /tmp/mimir/tsdb-sync
  filesystem:
    dir: /tmp/mimir/data/tsdb
  tsdb:
    dir: /tmp/mimir/tsdb

compactor:
  data_dir: /tmp/mimir/compactor
  sharding_ring:
    kvstore: { store: memberlist }

distributor:
  ring:
    instance_addr: 127.0.0.1
    kvstore: { store: memberlist }

ingester:
  ring:
    instance_addr: 127.0.0.1
    kvstore: { store: memberlist }
    replication_factor: 1

server:
  http_listen_port: 9009
  grpc_listen_port: 9095
  log_level: error
```

```bash
# 1. 运行
docker run --rm -p 9009:9009 -v $(pwd)/demo.yaml:/etc/mimir/demo.yaml \
  grafana/mimir:latest --config.file=/etc/mimir/demo.yaml

# 2. 验证就绪状态（期望 HTTP 200，正文："ready"）
curl -sf http://localhost:9009/ready

# 3. 验证是否正在服务 API
curl -s http://localhost:9009/api/v1/labels | jq '.status'   # → "success"

# 4. 验证自检指标抓取
curl -s http://localhost:9009/metrics | grep -E '^mimir_(distributor|ingester)_' | head
```

### 2. 发送指标 — Prometheus remote_write

```yaml
remote_write:
  - url: http://localhost:9009/api/v1/push
    headers:
      X-Scope-OrgID: tenant1   # 当 multitenancy_enabled: true 时必须
```

```bash
# 验证样本是否已写入
curl -s -H 'X-Scope-OrgID: tenant1' \
  'http://localhost:9009/api/v1/query?query=up' | jq '.data.result | length'
# 期望在 Prometheus 抓取后的约 30 秒内 > 0
```

### 3. 发送指标 — Grafana Alloy

```alloy
prometheus.remote_write "mimir" {
  endpoint {
    url = "http://mimir:9009/api/v1/push"
    headers = { "X-Scope-OrgID" = "tenant1" }
  }
}
```

### 4. Kubernetes 部署（Helm，微服务）

```bash
# 1. 安装
helm repo add grafana https://grafana.github.io/helm-charts
helm install mimir grafana/mimir-distributed --version 6.0.6 -f values.yaml

# 2. 验证所有 Pod 是否处于 Running / Ready 状态
kubectl get pods -n mimir
#   distributor, ingester, querier, query-frontend, store-gateway, compactor, ruler

# 3. 验证网关是否就绪
kubectl port-forward -n mimir svc/mimir-nginx 9009:80 &
curl -sf http://localhost:9009/ready
```

## 多租户

```yaml
multitenancy_enabled: true
# 每个请求必须包含标头:  X-Scope-OrgID: <租户 ID>
```

关于存储后端（S3 / GCS / Azure / 文件系统）请参阅 [`references/storage.md`](references/storage.md)。关于组件角色、环选项、限制和 API 端点转储请参阅 [`references/architecture.md`](references/architecture.md)。

## 故障排除

- `/ready` 返回 503 → ingester 仍在加入环；检查 `mimir_ring_members` 和 ingester 日志
- 推送时出现 `429 Too Many Requests` → 提高 `limits.ingestion_rate` / `ingestion_burst_size`
- 样本已写入但查询返回空结果 → 确认 `X-Scope-OrgID` 在写入和读取之间匹配
- 查询旧数据返回无结果 → 检查压缩器日志并确认 store-gateway 已同步块

## 资源

- [Mimir 文档](https://grafana.com/docs/mimir/latest/)
- [Helm 图表 `mimir-distributed`](https://github.com/grafana/mimir/tree/main/operations/helm/charts/mimir-distributed)
- [架构参考](https://grafana.com/docs/mimir/latest/references/architecture/)
