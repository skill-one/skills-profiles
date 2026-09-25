# Kubernetes 基础设施

使用 Dynatrace DQL 监控和分析 Kubernetes 基础设施。查询集群资源、监控工作负载健康状态、分析 Pod 布局、优化成本并评估安全态势。

## 何时使用此技能

- 监控 Kubernetes 集群健康状态和容量
- 分析 Pod 和容器的资源利用率
- 调查 Pod 故障、OOMKills、驱逐或崩溃循环
- 调试降级部署、卡住的滚动更新或节点压力
- 优化 Kubernetes 资源成本
- 评估安全态势和合规性
- 排查工作负载调度和布局问题
- 审计入口路由和网络策略

## 知识库结构

### 核心监控（从这里开始）

1. **集群清单** → `references/cluster-inventory.md` - 集群、命名空间、资源分布
2. **节点监控** - 节点容量、CPU/内存使用率、Pod 密度
3. **Pod 监控** - Pod CPU、内存、生命周期事件
4. **工作负载监控** - Deployment、StatefulSet、DaemonSet 资源

### 高级主题

1. **配置分析** → `references/labels-annotations.md` - 解析 k8s.object、标签、注解
2. **调度与布局** → `references/pod-node-placement.md` - 节点选择器、亲和性、污点、高可用性
3. **成本优化** - 合适的尺寸、浪费检测、效率评分
4. **安全与合规** - 特权容器、安全上下文

## 关键概念

### 实体类型

**工作负载：** `K8S_DEPLOYMENT`、`K8S_STATEFULSET`、`K8S_DAEMONSET`、`K8S_JOB`、`K8S_CRONJOB`、`K8S_HORIZONTALPODAUTOSCALER`
**基础设施：** `K8S_CLUSTER`、`K8S_NAMESPACE`、`K8S_NODE`、`K8S_POD`
**配置：** `K8S_SERVICE`、`K8S_CONFIGMAP`、`K8S_SECRET`、`K8S_PERSISTENTVOLUMECLAIM`、`K8S_PERSISTENTVOLUME`、`K8S_INGRESS`、`K8S_NETWORKPOLICY`

> **注意：** HPA、Job、CronJob 和配置实体类型仅用于清单查询。对于 HPA 缩放分析，请参阅 `references/workload-health.md`；对于 PVC/PV，请参阅 `references/pv-pvc.md`；对于 Ingress/NetworkPolicy，请参阅相应的参考文件。

### 查询类型

**smartscapeNodes** - 查询 K8s 实体（当前状态，无需指定时间范围）：

```dql
smartscapeNodes K8S_POD
| filter k8s.namespace.name == "production"
| fields k8s.cluster.name, k8s.pod.name
```

**timeseries** - 监控指标随时间变化（始终指定 `from:` 范围）：

```dql
timeseries cpu = sum(dt.kubernetes.container.cpu_usage),
  by: {k8s.pod.name, k8s.namespace.name},
  from: now()-1h
| fieldsAdd avg_cpu = arrayAvg(cpu)
```

> `timeseries` 将每个指标作为时间桶数组返回。要在下游 `fieldsAdd` 中将其折叠为标量，请使用 `arrayAvg(series)` 或 `arraySum(series)` — 在 `timeseries {}` 块外对系列字段调用 `avg()` 或 `sum()` 不受支持。

**fetch logs** - 分析日志事件：

```dql
fetch logs
| filter k8s.namespace.name == "production" and loglevel == "ERROR"
```

### 核心字段

- `k8s.cluster.name`, `k8s.namespace.name`, `k8s.pod.name`, `k8s.node.name`
- `k8s.workload.name`, `k8s.workload.kind`, `k8s.container.name`
- `k8s.object` - 深度检查的完整 JSON 配置
- `tags[label]` - 访问标签和注解

**`k8s.workload.kind` 值**（在 DT 中始终为小写 — 不是 K8s API 中的帕斯卡大小写）：
`"deployment"`，`"statefulset"`，`"daemonset"`，`"replicaset"`，`"job"`，`"cronjob"`

**`k8s.object` 可用性：**

| 实体类型 | `k8s.object` 可用？ |
|---|---|
| `K8S_POD` | 是 |
| `K8S_NAMESPACE` | 是 |
| `K8S_NODE` | 是 |
| 工作负载类型 (`K8S_DEPLOYMENT` 等) | 是 |
| `K8S_CLUSTER` | **否** |

### 可用指标

**CPU：** `dt.kubernetes.container.cpu_usage`, `cpu_throttled`, `limits_cpu`, `requests_cpu`
**内存：** `dt.kubernetes.container.memory_working_set`, `limits_memory`, `requests_memory`
**操作：** `dt.kubernetes.container.restarts`, `oom_kills`
**节点：** `dt.kubernetes.node.pods_allocatable`, `cpu_allocatable`, `memory_allocatable`, `dt.kubernetes.pods`

> **请求/限制的聚合规则：** 聚合 `requests_cpu`、`limits_cpu`、`requests_memory` 或 `limits_memory` 时，始终使用 `sum()` — 永远不要使用 `avg()` — `avg()` 返回每个容器的平均值，并会静默地低估多容器 Pod 和多副本工作负载。对于 DaemonSets（每个节点一个 Pod），此错误与集群大小成正比。

### 实体消歧

`K8S_POD` vs `CONTAINER`：这些是 Dynatrace 中的不同实体类型。

- **`K8S_POD`** — 具有嵌套 `k8s.object` JSON、调度状态、条件和 K8s 指标的 K8s 原生实体。使用此技能。
- **`CONTAINER`** — 主机级容器清单（镜像、生命周期、主机分配）。改用 `dt-obs-hosts` 技能。

smartscape 边缘是 `CONTAINER --(is_part_of)--> K8S_POD`。要从 Pod 到达容器，向后遍历：

```dql-template
smartscapeNodes K8S_POD
| filter k8s.namespace.name == "<namespace>"
| traverse edgeTypes: {is_part_of}, targetTypes: {CONTAINER}, direction: backward, fieldsKeep: {id}
| fields k8s.cluster.name, k8s.namespace.name, k8s.pod.name, container.id=id
```

### 服务 → K8S_POD 关联

不存在 `SERVICE` 和 `K8S_POD` 之间的直接 smartscape 边缘。关联键是共享维度 `k8s.workload.name`。有关完整两步模式，请参阅 `references/pod-debugging.md` 中的 [服务 → Pod Drill-Down](references/pod-debugging.md#service--pod-drill-down)。

## 常见工作流

### 1. 集群健康检查

列出所有集群：

```dql
smartscapeNodes K8S_CLUSTER
| fields k8s.cluster.name, k8s.cluster.version, k8s.cluster.distribution
```

检查节点容量：

```dql
timeseries {
  current_pods = avg(dt.kubernetes.pods),
  max_pods = avg(dt.kubernetes.node.pods_allocatable)
}, by: {k8s.node.name, k8s.cluster.name},
from: now()-1h
| fieldsAdd pod_capacity_pct = (arrayAvg(current_pods) / arrayAvg(max_pods)) * 100
| filter pod_capacity_pct > 80
```

识别非 Running 状态的 Pod：

```dql
smartscapeNodes K8S_POD
| parse k8s.object, "JSON:config"
| fieldsAdd phase = config[status][phase]
| filter not(in(phase, {"Running", "Succeeded"}))
| fields k8s.cluster.name, k8s.namespace.name, k8s.pod.name, phase
```

> `Succeeded` 是已完成 Job Pod 的健康终端阶段 — 排除它可以避免误报。如果您想审计已完成的 Job，请调整。

### 2. 资源优化

**Pod 级** — 查找资源利用率低于 30% 的 Pod：

```dql
timeseries {
  cpu_usage = sum(dt.kubernetes.container.cpu_usage),
  cpu_requests = sum(dt.kubernetes.container.requests_cpu)
}, by: {k8s.pod.name, k8s.namespace.name, k8s.cluster.name},
from: now()-7d
| fieldsAdd usage_pct = (arrayAvg(cpu_usage) / arrayAvg(cpu_requests)) * 100
| filter usage_pct < 30 and arrayAvg(cpu_requests) > 0
```

**工作负载级** — 跨所有副本聚合（对于正确的 DaemonSet 会计是必需的）：

```dql
timeseries {
  cpu_usage = sum(dt.kubernetes.container.cpu_usage),
  cpu_requests = sum(dt.kubernetes.container.requests_cpu)
}, by: {k8s.workload.name, k8s.workload.kind, k8s.namespace.name, k8s.cluster.name},
from: now()-7d
| fieldsAdd
    avg_usage = arrayAvg(cpu_usage),
    avg_requests = arrayAvg(cpu_requests)
| fieldsAdd usage_pct = (avg_usage / avg_requests) * 100
| filter usage_pct < 30 and avg_requests > 0
| sort usage_pct asc
```

> 在每个聚合级别都使用 `sum()` 进行 `cpu_usage` 和 `cpu_requests` 的聚合。在 50 个节点上运行的 DaemonSet 具有 50 倍的每个 Pod 请求总量；`avg()` 会报告真实保留容量的 1/50。

识别没有限制的容器：

```dql
smartscapeNodes K8S_POD
| parse k8s.object, "JSON:config"
| expand container = config[spec][containers]
| fieldsAdd
    container_name = container[name],
    cpu_limit = container[resources][limits][cpu],
    memory_limit = container[resources][limits][memory]
| filter isNull(cpu_limit) or isNull(memory_limit)
```

### 3. 排查 Pod 问题

Pod 排查受益于结合 **指标**（timeseries）和 **Kubernetes 事件**（事件流）以获得完整图景。

#### 基于指标的排查

查找有 OOMKills 的 Pod：

```dql
timeseries oom_kills = sum(dt.kubernetes.container.oom_kills),
  by: {k8s.pod.name, k8s.namespace.name, k8s.cluster.name},
  from: now()-1h
| filter arraySum(oom_kills) > 0
| fieldsAdd total_oom_kills = arraySum(oom_kills)
| sort total_oom_kills desc
```

分析 Pod 重启模式：

```dql
timeseries restarts = sum(dt.kubernetes.container.restarts),
  by: {k8s.pod.name, k8s.namespace.name, k8s.cluster.name},
  from: now()-1h
| fieldsAdd total_restarts = arraySum(restarts)
| filter total_restarts > 5
```

#### 基于事件的排查

对于操作事件（Pod 重启、OOM kills、驱逐、调度失败），Kubernetes 事件比指标提供更丰富的上下文，包括事件原因、消息和时间戳。

**何时使用 Kubernetes 事件而不是指标：**
- 用户询问最近的操作事件（“显示我 Pod 重启事件”）
- 用户想要事件详情，如原因和消息
- 用户询问特定时间窗口内的事件（“过去 48 小时”）
- 用户想要将事件与根本原因关联

**Kubernetes 事件** 可通过 `get-events-for-kubernetes-cluster` 工具（一个 Dynatrace MCP 工具）获取。调用时使用 `findAllK8Events: true` 获取所有集群的事件，或使用 `findAllK8Events: false` 并提供 `clusterId`（`k8s.cluster.uid`）或 `kubernetesEntityId`（`dt.entity.kubernetes_cluster`）以限制到单个集群。使用 `history` 设置回溯窗口（例如 `"1h"`、`"24h"`、`"7d"`；最大 `"60d"`）。
**优先使用此工具** 当用户询问 OOM 事件、Pod 重启、驱逐或集群级事件历史时。如果工具不可用，则回退到下面的 `fetch events` DQL 模式。

**重要：** 过滤结果时区分事件类型。Kubernetes 事件涵盖许多类别。当用户询问特定类型的事件时，请按相应方式过滤结果 — 不要报告不相关的事件：

| 用户询问 | 相关事件原因 | 不相关 |
|-----------------|----------------------|-------------|
| Pod 重启 | `BackOff`, `CrashLoopBackOff`, `Killing` | Readiness probe failures, CPU throttling |
| OOM 事件 | `OOMKilling`, `OOMKilled` | Memory pressure warnings |
| 驱逐 | `Evicted`, `Preempting` | Node pressure |
| 调度失败 | `FailedScheduling`, `Unschedulable` | Resource quotas |

**为了获得完整答案**，结合两种方法：
1. 使用 **事件工具** 获取事件详情（发生了什么、何时、为什么）
2. 使用 **timeseries 指标** 显示定量影响（多少重启、随时间的 OOM kill 计数）

#### 通过 DQL 获取 Kubernetes 事件

查询 Pod 重启和操作事件：

```dql
fetch events
| filter event.kind == "K8S_EVENT"
| filter event.type == "Warning"
| fields timestamp, k8s.cluster.name, k8s.namespace.name, k8s.pod.name,
    event.reason, event.message
| sort timestamp desc
| limit 50
```

按特定事件原因过滤：

```dql
fetch events
| filter event.kind == "K8S_EVENT"
| filter in(event.reason, {"OOMKilling", "BackOff", "Evicted", "FailedScheduling"})
| fields timestamp, k8s.cluster.name, k8s.namespace.name, k8s.pod.name,
    event.reason, event.message
| sort timestamp desc
```

**`fetch events` 中的字段名称：** 使用 `event.reason` 和 `event.message` — 不要使用 `dt.kubernetes.event.reason`。`dt.kubernetes.*` 前缀用于 timeseries 指标，而不是事件表。使用错误前缀的查询将返回零结果。

### 4. 安全评估

识别特权容器：

```dql
smartscapeNodes K8S_POD
| parse k8s.object, "JSON:config"
| expand container = config[spec][containers]
| fieldsAdd
    container_name = container[name],
    privileged = container[securityContext][privileged]
| filter privileged == true
```

查找以 root 身份运行的容器：

```dql
smartscapeNodes K8S_POD
| parse k8s.object, "JSON:config"
| expand container = config[spec][containers]
| fieldsAdd
    container_name = container[name],
    run_as_user = container[securityContext][runAsUser],
    run_as_non_root = container[securityContext][runAsNonRoot]
| filter (isNull(run_as_user) or run_as_user == 0) and run_as_non_root != true
```

### 5. 调度分析

验证 Deployment 和 StatefulSet 的 Pod 分布（高可用合规性）：

```dql
smartscapeNodes K8S_POD
| filter in(k8s.workload.kind, {"deployment", "statefulset"})
| summarize pod_count = count(),
            node_count = countDistinct(k8s.node.name),
            by: {k8s.cluster.name, k8s.namespace.name, k8s.workload.name, k8s.workload.kind}
| fieldsAdd ha_compliant = node_count > 1
| filter pod_count >= 2 and not ha_compliant
```

> DaemonSets 是有意排除的 — 每个容器设计为在单个节点上运行，因此单节点布局对它们来说不是高可用性违规。

### 6. DAVIS 问题影响 K8s 实体

查找影响 K8s 实体的活动 DAVIS 问题：

```dql
fetch dt.davis.problems, from:now() - 2h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| filter iAny(startsWith(smartscape.affected_entities[][type], "K8S_"))
| fields display_id, event.name, event.category, affected_entity_ids = smartscape.affected_entities[][id]
```

`smartscape.affected_entities` 是一个记录数组；每个记录具有 `id`、`type` 和 `name`。使用 `[][id]` 获取受影响实体的 Smartscape ID 数组，或在 `expand smartscape.affected_entities` 后使用 `[id]`。如果没有前面的 `expand`，`[id]` 会静默返回 `null`。由于 `filter` 不能接受裸迭代表达式，因此将其包装在 `iAny(...)` 中。

## 最佳实践

### 选择合适的数据源

| 用户问题 | 最佳方法 | 原因 |
|---------------|---------------|-----|
| "显示我 OOM 事件" | 事件工具 + 指标 | 事件提供原因/消息；指标显示趋势 |
| "显示我 Pod 重启事件" | 事件工具 + timeseries 指标 | 事件揭示原因（BackOff、Killing、CrashLoopBackOff）；`dt.kubernetes.container.restarts` 指标提供实际重启计数 |
| "有多少 Pod 重启？" | timeseries 指标 | 随时间变化的定量数据 |
| "我最近的 48 小时内 Pod 发生了什么？" | 事件工具 | 操作事件历史记录，包含上下文 |
| "哪些 Pod 使用最多的 CPU？" | timeseries 指标 | 资源利用率分析 |
| "列出所有集群/命名空间" | smartscapeNodes | 实体发现和清单 |
| "是否有调度失败？" | 事件工具 | 事件原因解释为什么 |
| "哪些工作负载被过度配置？" | timeseries 指标，工作负载级 | 必须使用 `sum()` 进行请求；按 `k8s.workload.name` 分组 |

### 时间范围

- **`smartscapeNodes`** — 无需时间范围；始终返回当前实体状态。
- **`timeseries`** — 始终添加 `from: now()-<窗口>`。默认窗口由系统确定，通常对于趋势分析太短。推荐默认值：
  `now()-1h` 用于最近峰值，`now()-24h` 用于每日模式，`now()-7d` 用于每周趋势。
- **`fetch events`** — 添加 `from:` 是推荐的，以获得可重复的结果；如果没有，则应用系统默认窗口。
- **`fetch dt.davis.problems`** — 使用 `from: now()-2h` 获取活动问题；扩展到 `now()-7d` 以包括最近关闭的问题。

### 查询性能

1. **尽早过滤** - 立即应用集群/命名空间过滤器
2. **使用特定实体类型** - 避免使用通配符
3. **限制结果集** - 使用 `limit` 进行探索
4. **缓存集群列表** - 存储在变量中
5. **除非需要，否则省略 `k8s.object`** - 解析它会显著增加查询成本

### 监控建议

1. 为所有容器设置资源限制
2. 监控 OOMKills 并调整内存限制
3. 跟踪 CPU 节流并调整 CPU 限制
4. 定期检查资源效率（目标 70-80%）
5. 实施安全最佳实践（非 root、只读文件系统）
6. 使用特定镜像标签（避免 :latest）

### 配置标准

1. 使用标签进行组织（应用、环境、团队）
2. 设置资源请求和限制
3. 配置健康检查（liveness/readiness probes）
4. 为所有入口资源使用 TLS
5. 使用注解进行文档记录

## 排查

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 未返回 Pod 数据 | 实体类型错误或缺少集群过滤器 | 使用 `K8S_POD`（不是 `POD`）；添加 `k8s.cluster.name` 过滤器 |
| `k8s.object` 解析错误 | 复杂的 JSON 结构 | 使用 `parse k8s.object, "JSON:config"` 然后访问嵌套字段 |
| Pod 网络指标不可用 | Grail 中不可用 | 使用服务网格指标或主机级网络指标 |
| 大结果集 | 无时间范围或集群过滤器 | 添加时间范围并尽早过滤集群/命名空间 |
| 输出中缺少标签 | 标签访问不正确 | 使用 `tags[label_name]` 访问标签 |
| `k8s.workload.kind` 过滤器返回无结果 | 值为帕斯卡大小写（例如 `"Deployment"`） | 值在 DT 中始终为小写：`"deployment"`，`"statefulset"`，`"daemonset"` |

## 限制

**不可用指标：**

- Pod 网络指标（rx_bytes, tx_bytes）在 Grail 中不可用
- 解决方案：使用服务网格指标或主机级网络指标

**查询注意事项：**

- 最小化结果集大小：如果不需要，则不要包含 `k8s.object` 字段
- 尽可能简化结果集：解析 k8s.object 会增加查询复杂性
- 大型集群可能需要分页或时间范围限制
- 一些 K8s 状态字段异步更新

## 何时加载参考

### 加载 cluster-inventory.md 当：

- 执行集群、命名空间或资源分布分析
- 跨集群审计工作负载计数

→ [references/cluster-inventory.md](references/cluster-inventory.md)

### 加载 labels-annotations.md 当：

- 按标签或注解过滤
- 解析 `k8s.object` 进行详细配置检查

→ [references/labels-annotations.md](references/labels-annotations.md)

### 加载 pod-node-placement.md 当：

- 分析调度约束（亲和性、污点、容忍度）
- 验证高可用性合规性和 Pod 分布

→ [references/pod-node-placement.md](references/pod-node-placement.md)

### 加载 pod-debugging.md 当：

- 调查 Pod 退出代码、崩溃循环或初始化容器故障
- 诊断镜像拉取错误或服务到 Pod 连接问题
- 从服务问题钻取到 Pod 级详情

→ [references/pod-debugging.md](references/pod-debugging.md)

### 加载 workload-health.md 当：

- 调查降级部署或卡住的滚动更新
- 检查节点条件、CPU 节流或 HPA 缩放
- 分析 StatefulSet 排序或 DaemonSet 覆盖范围

→ [references/workload-health.md](references/workload-health.md)

### 加载 pv-pvc.md 当：

- 处理持久存储（PVC/PV 生命周期、遗弃卷）
- 检查 StorageClass 配置

→ [references/pv-pvc.md](references/pv-pvc.md)

### 加载 ingress.md 当：

- 分析入口路由规则或 TLS 证书
- 审计入口控制器配置

→ [references/ingress.md](references/ingress.md)

### 加载 network-policies.md 当：

- 列出或审计网络策略
- 检查命名空间隔离配置

→ [references/network-policies.md](references/network-policies.md)

## 参考

- [cluster-inventory.md](references/cluster-inventory.md) — 集群、命名空间和资源分布分析
- [labels-annotations.md](references/labels-annotations.md) — 标签/注解过滤和 k8s.object 解析
- [pod-node-placement.md](references/pod-node-placement.md) — 调度、亲和性、污点和高可用性模式
- [pod-debugging.md](references/pod-debugging.md) — 退出代码、Pod 条件、初始化容器、镜像拉取错误、日志、服务到 Pod 钻取
- [workload-health.md](references/workload-health.md) — 降级部署、卡住的滚动更新、节点条件、CPU 节流、HPA、StatefulSet 排序
- [pv-pvc.md](references/pv-pvc.md) — PVC/PV 生命周期、阶段参考、遗弃卷、StorageClass
- [ingress.md](references/ingress.md) — 路由规则解析、TLS 审计
- [network-policies.md](references/network-policies.md) — 策略列出、命名空间隔离审计

## 相关技能

- **dt-obs-problems** — 用于与 Kubernetes 集群相关的问题（使用 `dt.smartscape_source.id` 并使用 K8S_ 前缀过滤器）
- **dt-dql-essentials** — 核心 DQL 语法和查询结构
- **dt-obs-hosts** — Kubernetes 节点的主机级指标
