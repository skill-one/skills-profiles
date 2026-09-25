# 调试 Buttercup

## 何时使用

- `crs` 命名空间中的 Pod 处于 CrashLoopBackOff、OOMKilled 或重启状态
- 多个服务同时重启（级联故障）
- Redis 无响应或显示 AOF 警告
- 队列在增长但任务没有进展
- 节点显示 DiskPressure、MemoryPressure 或 PID 压力
- 构建机器人无法连接 Docker 守护进程（DinD 故障）
- 调度器卡住且未推进任务状态
- 健康检查探针意外失败
- 部署的 Helm 值与实际 Pod 配置不匹配

## 何时不应使用

- 部署或升级 Buttercup（使用 Helm 和部署指南）
- 调试 `crs` Kubernetes 命名空间外的故障
- 不涉及故障症状的性能调优

## 命名空间和服务

所有 Pod 都在 `crs` 命名空间中运行。关键服务：

| 层级 | 服务 |
|------|------|
| 基础设施 | redis、dind、litellm、registry-cache |
| 编排 | scheduler、task-server、task-downloader、scratch-cleaner |
| 模糊测试 | build-bot、fuzzer-bot、coverage-bot、tracer-bot、merger-bot |
| 分析 | patcher、seed-gen、program-model、pov-reproducer |
| 界面 | competition-api、ui |

## 筛查工作流

始终从筛查开始。首先运行以下三个命令：

```bash
# 1. Pod 状态 - 查找重启、CrashLoopBackOff、OOMKilled
kubectl get pods -n crs -o wide

# 2. 事件 - 故障的时间线
kubectl get events -n crs --sort-by='.lastTimestamp'

# 3. 仅警告 - 过滤噪音
kubectl get events -n crs --field-selector type=Warning --sort-by='.lastTimestamp'
```

然后缩小范围：

```bash
# 特定 Pod 重启的原因？检查 Last State Reason (OOMKilled、Error、Completed)
kubectl describe pod -n crs <pod-name> | grep -A8 'Last State:'

# 检查实际资源限制与预期
kubectl get pod -n crs <pod-name> -o jsonpath='{.spec.containers[0].resources}'

# 崩溃容器的日志（--previous = 死亡的容器）
kubectl logs -n crs <pod-name> --previous --tail=200

# 当前日志
kubectl logs -n crs <pod-name> --tail=200
```

### 历史问题与持续问题

高重启次数不一定表示问题仍在持续——重启会累积在 Pod 的生命周期中。始终区分：
- `--tail` 显示日志缓冲区的末尾，可能包含旧消息。使用 `--since=300s` 确认问题是否当前正在发生。
- 日志输出中的 `--timestamps` 有助于跨服务关联事件。
- 在 `describe pod` 中检查 `Last State` 时间戳，以查看最近一次崩溃实际发生的时间。

### 级联检测

当许多 Pod 同时重启时，在调查单个 Pod 之前检查共享依赖故障。最常见的级联：Redis 停机 -> 每个服务都得到 `ConnectionError`/`ConnectionRefusedError` -> 大量重启。在多个 `--previous` 日志中查找相同错误——如果它们都显示 `redis.exceptions.ConnectionError`，则调试 Redis，而不是单个服务。

## 日志分析

```bash
# 所有服务的所有副本一次性
kubectl logs -n crs -l app=fuzzer-bot --tail=100 --prefix

# 实时流
kubectl logs -n crs -l app.kubernetes.io.name=redis -f

# 将所有日志收集到磁盘（现有脚本）
bash deployment/collect-logs.sh
```

## 资源压力

```bash
# 每个 Pod 的 CPU/内存
kubectl top pods -n crs

# 节点级别
kubectl top nodes

# 节点状态（磁盘压力、内存压力、PID 压力）
kubectl describe node <node> | grep -A5 Conditions

# Pod 内的磁盘使用情况
kubectl exec -n crs <pod> -- df -h

# 什么在消耗磁盘
kubectl exec -n crs <pod> -- sh -c 'du -sh /corpus/* 2>/dev/null'
kubectl exec -n crs <pod> -- sh -c 'du -sh /scratch/* 2>/dev/null'
```

## Redis 调试

Redis 是骨干。当它停机时，一切都会级联。

```bash
# Redis Pod 状态
kubectl get pods -n crs -l app.kubernetes.io.name=redis

# Redis 日志（AOF 警告、OOM、连接问题）
kubectl logs -n crs -l app.kubernetes.io.name=redis --tail=200

# 连接到 Redis CLI
kubectl exec -n crs <redis-pod> -- redis-cli

# 在 redis-cli 中：键诊断
INFO memory          # used_memory_human, maxmemory
INFO persistence     # aof_enabled, aof_last_bgrewrite_status, aof_delayed_fsync
INFO clients         # connected_clients, blocked_clients
INFO stats           # total_connections_received, rejected_connections
CLIENT LIST          # 查看谁连接了
DBSIZE               # 总键数

# AOF 配置
CONFIG GET appendonly     # AOF 是否启用？
CONFIG GET appendfsync   # fsync 策略：everysec、always 或 no

# /data 挂载的是什么？（磁盘与 tmpfs 对 AOF 性能很重要）
```

```bash
kubectl exec -n crs <redis-pod> -- mount | grep /data
kubectl exec -n crs <redis-pod> -- du -sh /data/
```

### 队列检查

Buttercup 使用 Redis 流和消费者组。队列名称：

| 队列 | 流键 |
|------|------|
| 构建 | fuzzer_build_queue |
| 构建输出 | fuzzer_build_output_queue |
| 故障 | fuzzer_crash_queue |
| 确认的漏洞 | confirmed_vulnerabilities_queue |
| 下载任务 | orchestrator_download_tasks_queue |
| 就绪任务 | tasks_ready_queue |
| 补丁 | patches_queue |
| 索引 | index_queue |
| 索引输出 | index_output_queue |
| 追踪漏洞 | traced_vulnerabilities_queue |
| POV 请求 | pov_reproducer_requests_queue |
| POV 响应 | pov_reproducer_responses_queue |
| 删除任务 | orchestrator_delete_task_queue |

```bash
# 检查流长度（待处理消息）
kubectl exec -n crs <redis-pod> -- redis-cli XLEN fuzzer_build_queue

# 检查消费者组滞后
kubectl exec -n crs <redis-pod> -- redis-cli XINFO GROUPS fuzzer_build_queue

# 检查每个消费者的待处理消息
kubectl exec -n crs <redis-pod> -- redis-cli XPENDING fuzzer_build_queue build_bot_consumers - + 10

# 任务注册表大小
kubectl exec -n crs <redis-pod> -- redis-cli HLEN tasks_registry

# 任务状态计数
kubectl exec -n crs <redis-pod> -- redis-cli SCARD cancelled_tasks
kubectl exec -n crs <redis-pod> -- redis-cli SCARD succeeded_tasks
kubectl exec -n crs <redis-pod> -- redis-cli SCARD errored_tasks
```

消费者组：`build_bot_consumers`、`orchestrator_group`、`patcher_group`、`index_group`、`tracer_bot_group`。

## 健康检查

Pod 将时间戳写入 `/tmp/health_check_alive`。健康检查探针检查文件的新鲜度。

```bash
# 检查健康文件新鲜度
kubectl exec -n crs <pod> -- stat /tmp/health_check_alive
kubectl exec -n crs <pod> -- cat /tmp/health_check_alive
```

如果一个 Pod 在重启循环，健康检查文件可能正在过时，因为主进程被阻塞（例如等待 Redis、卡在 I/O）。

## 远程监控（OpenTelemetry / Signoz）

所有服务都通过 OpenTelemetry 导出跟踪和指标。如果部署了 Signoz（`global.signoz.deployed: true`），请使用其 UI 跨服务进行分布式跟踪。

```bash
# 检查 OTEL 是否配置
kubectl exec -n crs <pod> -- env | grep OTEL

# 验证 Signoz Pod 是否运行（如果部署）
kubectl get pods -n platform -l app.kubernetes.io.name=signoz
```

跟踪特别适用于诊断慢速任务处理、识别管道中的瓶颈服务以及跨调度器 -> 构建机器人 -> 模糊测试机器人链关联事件。

## 卷和存储

```bash
# PVC 状态
kubectl get pvc -n crs

# 检查 corpus tmpfs 是否挂载、其大小和后备类型
kubectl exec -n crs <pod> -- mount | grep corpus_tmpfs
kubectl exec -n crs <pod> -- df -h /corpus_tmpfs 2>/dev/null

# 检查是否设置了 CORPUS_TMPFS_PATH
kubectl exec -n crs <pod> -- env | grep CORPUS

# 完整磁盘布局 - 磁盘与 tmpfs 的区别
kubectl exec -n crs <pod> -- df -h
```

`CORPUS_TMPFS_PATH` 在 `global.volumes.corpusTmpfs.enabled: true` 时设置。这会影响 fuzzer-bot、coverage-bot、seed-gen 和 merger-bot。

### 部署配置验证

当行为不符合预期时，验证 Helm 值是否实际生效：

```bash
# 检查 Pod 的实际资源限制
kubectl get pod -n crs <pod-name> -o jsonpath='{.spec.containers[0].resources}'

# 检查 Pod 的实际卷定义
kubectl get pod -n crs <pod-name> -o jsonpath='{.spec.volumes}'
```

Helm 值模板拼写错误（例如错误的键名）会静默回退到图表默认值。如果部署的资源与值模板不匹配，请检查键名不匹配。

## 服务特定调试

有关每个服务的详细症状、根本原因和修复方法，请参阅 [references/failure-patterns.md](references/failure-patterns.md)。

快速参考：

- **DinD**: `kubectl logs -n crs -l app=dind --tail=100` -- 查找 Docker 守护进程崩溃、存储驱动错误
- **构建机器人**: 检查构建队列深度、DinD 连接性、编译期间的 OOM
- **模糊测试机器人**: corpus 磁盘使用情况、CPU 限制、崩溃队列积压
- **补丁**: LiteLLM 连接性、LLM 超时、补丁队列深度
- **调度器**: 中央大脑 -- `kubectl logs -n crs -l app=scheduler --tail=-1 --prefix | grep "WAIT_PATCH_PASS\|ERROR\|SUBMIT"`

## 诊断脚本

运行自动筛查快照：

```bash
bash {baseDir}/scripts/diagnose.sh
```

传递 `--full` 以还原始日志所有 Pod：

```bash
bash {baseDir}/scripts/diagnose.sh --full
```

这会一次性收集 Pod 状态、事件、资源使用情况、Redis 健康和队列深度。
