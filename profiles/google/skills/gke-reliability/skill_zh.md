# GKE 可靠性

本指南涵盖 GKE 集群和工作负载的高可用性和可靠性配置。

> **MCP 工具：** `get_cluster`, `get_k8s_resource`, `describe_k8s_resource`,
> `apply_k8s_manifest`, `list_k8s_events`

## 金路径可靠性默认值

| 设置          | 金路径值     | 备注                            |
| ------------- | ------------ | -------------------------------- |
| 集群类型     | 区域 (4 个区域：    | 控制平面跨区域复制             |
:              : us-central1-a/b/c/f)  : 区域                          :
| 升级策略     | SURGE (`maxSurge: 1`) | 带额外容量的滚动升级             |
:              :                   :                              :
| 自动修复     | `true`        | 自动替换不健康的节点            |
:              :                   :                              :
| 自动升级     | `true`        | 节点跟随控制平面版本            |
:              :                   :                              :
| 发布通道     | REGULAR       | 平衡新鲜度和稳定性             |
| 有状态 HA     | 启用         | 有状态工作负载的领导者选举      |
:              :                   :                              :

## 工作流

### 1. 验证集群高可用性

```
# MCP (首选)
get_cluster(name="projects/<PROJECT>/locations/<REGION>/clusters/<CLUSTER>",
  readMask="location,locations,nodePools.locations")

# gcloud 降级方案
gcloud container clusters describe <CLUSTER> --region <REGION> \
  --format="json(location, locations)" \
  --quiet
```

-   如果 `location` 是区域（例如，`us-central1`），则控制平面是区域的
-   如果 `locations` 有多个条目，则节点跨多个区域

### 2. Pod 中断预算 (PDB)

PDB 确保在自愿中断（节点升级、自动缩放缩小）期间保持最低的 Pod 可用性。

**检查现有 PDB：**

```
# MCP (首选)
get_k8s_resource(parent="...", resourceType="poddisruptionbudget")

# kubectl 降级方案
kubectl get pdb --all-namespaces
```

**创建 PDB：**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: default
spec:
  minAvailable: 2       # 或使用 maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

> 每个生产 Deployment（副本数为 2+）都应该有 PDB。

### 3. 健康探针

每个生产容器都应该有存活性和就绪探针。对于启动缓慢的应用，建议使用启动探针。

**检查现有探针：**

```
# MCP (首选)
describe_k8s_resource(parent="...", resourceType="deployment", name="<APP>", namespace="<NS>")

# kubectl 降级方案
kubectl get deployment <APP> -n <NS> -o yaml | grep -E "livenessProbe|readinessProbe|startupProbe"
```

**推荐的探针配置：**

```yaml
spec:
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /readyz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 3
    startupProbe:             # 对于启动缓慢的应用
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 30    # 30 * 5s = 150s 最大启动时间
```

-   **就绪性**：确定 Pod 何时可以接受流量
-   **存活性**：确定何时重启容器
-   **启动**：在应用准备好之前禁用存活性/就绪性（防止过早重启）

### 4. 优雅关闭

确保应用处理 `SIGTERM` 并排空正在进行的请求：

```yaml
spec:
  terminationGracePeriodSeconds: 30    # 默认；对于长连接请求增加
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 5"]  # 允许负载均衡器注销
```

### 5. 拓扑扩展约束

将 Pod 分发到区域和节点，以在故障时存活：

```yaml
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: my-app
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: my-app
```

-   **区域扩展** (`DoNotSchedule`)：硬性要求——Pod 必须在区域间平衡
-   **节点扩展** (`ScheduleAnyway`)：尽力而为——优先分发，但不阻止调度

### 6. 副本

| 工作负载类型        | 最小副本数     | 原因                         |
| ------------------- | -------------- | ---------------------------- |
| 无状态 Web/API    | 2              | 存活单个 Pod/节点故障        |
:                    :              :                          :
| 关键服务          | 3              | 存活区域故障（带区域扩展）    |
:                    :              :                          :
| 有状态（数据库）    | 3（带复制）    | 应用级别的仲裁               |
| 批处理/作业        | 1              | 本质上是暂时的               |

## 最佳实践与生产指南

1.  **生产使用区域集群**：始终使用区域集群以在区域故障时存活。
2.  **所有工作负载使用 PDB**：每个生产工作负载（副本数为 2+）都需要 PodDisruptionBudget (PDB) 以防止自愿中断。
3.  **带显式超时的探针**：每个生产容器都必须定义存活性和就绪探针。**始终显式定义 `initialDelaySeconds`、`periodSeconds` 和 `timeoutSeconds`**。如果您的应用需要更多时间，但始终设置严格的限制以防止挂起连接。
4.  **区域扩展**：使用拓扑扩展约束将 Pod 分发到故障域（区域和节点）。
5.  **优雅关闭**：处理 `SIGTERM` 并设置适当的 `terminationGracePeriodSeconds`，使用 `preStop` 延迟钩子以允许负载均衡器注销。
6.  **维护窗口**：在低流量期间安排升级（参考 `gke-upgrades` 技能）。
