# Grafana Beyla

> **文档**: https://grafana.com/docs/beyla/latest/

通过 eBPF 实现零代码的 HTTP / gRPC / DB 仪器。发出 OTLP 追踪 + Prometheus 指标。

## 前置条件

- Linux 内核 **5.8+** 并启用 BTF (`ls /sys/kernel/btf/vmlinux` 必须存在)
- root 或 `CAP_SYS_ADMIN` (或 Kubernetes 中的 `privileged: true` + `hostPID: true`)
- x86_64 或 ARM64
- 一个可从 Beyla 访问的 OTLP 接收器 (Tempo, Alloy, OTel Collector)

## 常见工作流程

### 1. 使用 Docker 仪器单个二进制文件

```bash
# 1. 运行 Beyla 对应用端口 (应用必须已经运行，监听在 8080)
docker run --privileged --pid=host \
  -v /sys/kernel/debug:/sys/kernel/debug:ro \
  -e BEYLA_OPEN_PORT=8080 \
  -e BEYLA_PROMETHEUS_PORT=8999 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
  -p 8999:8999 \
  grafana/beyla

# 2. 生成一些流量
curl http://localhost:8080/ ; curl http://localhost:8080/api/users/42

# 3. 验证 Beyla 发出的指标 — 应列出 http_server_request_duration_seconds + 计数器
curl -s http://localhost:8999/metrics | grep -E '^http_(server|client)_request_duration'

# 4. 验证追踪 — 在 Tempo 的 Grafana Explore 中按 service.name 搜索 (默认 = 进程名)
#    或: 查询 Tempo 的搜索 API，查找 service.name="<app>" 的 spans
```

### 2. 部署为集群范围的 DaemonSet

完整的 DaemonSet + RBAC YAML 存在于 [`references/kubernetes.md`](references/kubernetes.md)。应用后：

```bash
# 1. 验证 DaemonSet 展开
kubectl -n monitoring rollout status ds/beyla

# 2. 验证 pod 正在运行，每个节点一个
kubectl -n monitoring get pods -l app=beyla -o wide

# 3. 验证 eBPF 探针已附加 (无提及 BTF 或 "权限被拒绝" 的错误)
kubectl -n monitoring logs ds/beyla --tail=50 | grep -Ei 'error|fail|btf' || echo "clean"

# 4. 验证遥测数据正在流动 — 检查 Tempo/Alloy 接收器是否收到来自集群的 spans
#    或直接抓取一个 pod:
kubectl -n monitoring port-forward ds/beyla 8999:8999 &
curl -s localhost:8999/metrics | head
```

### 3. 通过 Alloy 发送到 Grafana Cloud

```yaml
# beyla-config.yml
otel_traces_export:  { endpoint: http://alloy:4318 }
otel_metrics_export: { endpoint: http://alloy:4318 }
```

```bash
# 验证 Alloy 是否转发 — 检查 Alloy UI (localhost:12345) 中的
# otelcol.receiver.otlp.beyla 组件是否显示接收到的 spans/metrics > 0。
```

完整的 Alloy + Beyla YAML: [`references/config.md`](references/config.md).

## 故障排除

- `failed to load BPF object` → 内核 < 5.8 或 BTF 缺失；检查 `/sys/kernel/btf/vmlinux`
- Tempo 中无 spans，但 Prometheus 指标显示 → 检查 `OTEL_EXPORTER_OTLP_ENDPOINT`、协议 (http vs grpc) 和端口 (4318 http / 4317 grpc)
- HTTP 路由基数爆炸 → 设置 `routes.unmatched: heuristic` 并添加模式 (见 [`references/config.md`](references/config.md))
- Pod 重启时出现 `CrashLoopBackOff` → 可能缺少 `hostPID: true` 或 `privileged: true` / 需要的权限

## 资源

- [Beyla 文档](https://grafana.com/docs/beyla/latest/)
- [Beyla GitHub](https://github.com/grafana/beyla)
- [`references/config.md`](references/config.md) — 完整配置、环境变量、采样器、路由装饰器、生成的指标表、运行时矩阵
- [`references/kubernetes.md`](references/kubernetes.md) — DaemonSet + RBAC + 发现过滤器 + Helm
