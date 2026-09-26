# GKE 节点 NotReady 排错技巧

使用此技巧系统性地诊断一个或多个 GKE 节点报告 `NotReady`（或 `Ready: Unknown`）状态的原因，并提出安全的修复建议。`NotReady` 状态表示节点的 kubelet 没有正确地向控制平面报告，因此 Kubernetes 停止在节点上调度新的 Pod，这可能会降低应用程序的容量并导致停机。

此技巧以 **非交互式** 方式运行，并强制执行 **只读诊断边界**：先收集证据，然后提出供人类应用的修复方案（`kubectl`/`gcloud` 命令或 GitOps 资源清单更改）。**绝对不要** 自动修改集群、排空、删除或重建节点。

> [!IMPORTANT]
> 首先排除 **预期** 的 `NotReady`：新创建、升级、正在修复、隔离或缩小的节点会暂时报告 `NotReady`。只有在预期窗口期过后仍然存在时才将其视为故障。

## 🔍 诊断工作流

### 第 0 步：上下文发现和时间窗口

1.  **参数提取** — 从用户提示、活动的 `SETTINGS.md` 或环境默认值（`kubectl config current-context`、`gcloud config get-value project`）中非交互式地获取 `project_id`、`cluster_name`、`cluster_location` 和 `node_name`。
2.  **凭证与回退** — 尝试执行 `gcloud container clusters get-credentials {cluster_name} --location {cluster_location} --project {project_id}`。如果集群无法访问或命令失败（沙盒/干运行/离线），则向人类展示精确的诊断命令，并从报告的症状继续分析。
3.  **时间窗口** — 确定 `{issue_time}`（显式、相对或当前），并在其周围设置一个 1 小时的时间窗口（`start = issue_time - 30m`、`end = issue_time + 30m`），用于所有日志/指标查询。

--------------------------------------------------------------------------------

### 第 1 步：识别 NotReady 节点并收集初始状态

```bash
# 列出节点并识别 NotReady 状态、节点 IP 和容器运行时版本。
kubectl get nodes -o wide

# 检查受影响节点的 Conditions 和 Events（主要线索）。
kubectl describe node "{node_name}"
```

通过 Cloud Logging（当 kubectl 访问受限或用于历史事件时优先使用）进行等效操作。将其作为 **Logs Explorer 深度链接** 打开 — 将查询 URL 编码并附加项目和第 0 步的时间窗口：
`https://console.cloud.google.com/logs/query;query={URL_ENCODED_QUERY};timeRange={start}%2F{end}?project={project_id}`
（将 `/` 编码为 `%2F`，或使用 `;duration=PT1H` 表示滚动小时）：

```
resource.type="k8s_node"
log_id("events")
resource.labels.node_name="{node_name}"
resource.labels.cluster_name="{cluster_name}"
resource.labels.location="{cluster_location}"
```

**解释 `Conditions` 表：**

- `Ready: False` / `Ready: Unknown` 原因 `KubeletNotReady` / `NodeStatusUnknown`（"Kubelet 停止发布节点状态"）→ kubelet 或运行时问题；继续执行第 2 步。
- `MemoryPressure: True`、`DiskPressure: True`、`PIDPressure: True` → 资源耗尽；转到第 4b 步。
- `NetworkUnavailable: True` → 网络问题/CNI 问题；转到第 4d 步。

--------------------------------------------------------------------------------

### 第 2 步：扫描 kubelet 日志以查找错误特征

使用与第 1 步相同的 `logs/query;query={URL_ENCODED_QUERY};timeRange=...?project=...` 模式，将这些 kubelet 日志作为 **Logs Explorer 深度链接** 打开。

```
resource.type="k8s_node"
resource.labels.node_name="{node_name}"
resource.labels.cluster_name="{cluster_name}"
resource.labels.location="{cluster_location}"
log_id("kubelet")
severity>=WARNING
```

还请查看节点的串行控制台日志（`log_id("serialconsole.googleapis.com/serial_port_1_output")` 或 `resource.type="gce_instance"` 的串行日志），查找与 kubelet 失败相关的内核 `TaskHung`、OOM-killer 或磁盘 I/O 错误。

--------------------------------------------------------------------------------

### 第 3 步：将特征映射到根本原因（决策表）

| kubelet / 事件特征 | 可能的根本原因 | 转到 |
| --- | --- | --- |
| `runtime is down`、`Container runtime not ready`、`/run/containerd/containerd.sock` 上的错误（连接拒绝 / DeadlineExceeded） | 容器运行时（`containerd`）停止或无响应 | 第 4a 步 |
| `Got sys oom event from cadvisor` / 串行日志中的内核 OOM-killer | 系统级（节点级）OOM 杀死关键进程 | 第 4b 步 |
| `PLEG is not healthy` | PLEG 停滞，通常是节点过载（CPU/磁盘） | 第 4c 步 |
| `TaskHung` for `containerd`/`kubelet`、高磁盘延迟 | 磁盘节流 / I/O 不足 | 第 4b 步 |
| `failed to ensure lease`、`leases.coordination.k8s.io ... namespace kube-node-lease ... terminating` | `kube-node-lease` 终止 → NotReady 频繁波动 | 第 4f 步 |
| Kubelet 无法连接到 API 服务器，TLS/拨号超时 | Kubelet ↔ 控制平面连接 | 第 4d 步 |
| `NetworkPluginNotReady`、`cni plugin not initialized`、`NetworkUnavailable` | CNI 插件故障 | 第 4d 步 |
| 节点关键 DaemonSet Pod（CNI、kube-proxy、元数据）被阻止准入 | 准入 webhook 干扰 | 第 4e 步 |
| 仅通用 `NodeNotReady`，无其他特征 | 原因不明确 — 扩展到第 4d 步，然后升级 | 升级 |

--------------------------------------------------------------------------------

### 第 4 步：分支调查

#### 第 4a 步：容器运行时（`containerd`）停止

确认 kubelet 无法与 containerd 通信（上述套接字错误）。检查串行日志中 `containerd` 的重启/崩溃。**修复建议（仅提出，不要执行）：** 重建/修复节点（`kubectl drain` 然后让节点池重新创建它，或 `gcloud container clusters upgrade`/节点自动修复）；如果跨节点复发，则怀疑节点镜像或自定义 DaemonSet 干扰了 containerd。

#### 第 4b 步：资源压力 & OOM

```bash
# 节点可分配资源与使用情况。
kubectl describe node "{node_name}" | sed -n '/Allocated resources/,/Events/p'
```
Cloud Monitoring 指标用于检查（只读）：`kubernetes.io/node/memory/used_bytes`、`kubernetes.io/node/cpu/core_usage_time`、`kubernetes.io/node/ephemeral_storage/used_bytes`。
- **DiskPressure / 磁盘节流**：启动磁盘满或慢 PD → 增加磁盘大小/使用更快 PD 类型；减少镜像/日志更迭。
- **系统 OOM**：节点内存耗尽 → 设置/提高 Pod 内存 `requests`/`limits`，减少超额提交，或使用更大机器类型。区分 **系统 OOM**（节点级，杀死 kubelet/运行时）和 **cgroup OOM**（单个容器）。
- **PIDPressure**：进程过多 → 限制 Pod PIDs / 降低工作负载密度。

#### 第 4c 步：PLEG 不健康

`PLEG is not healthy` 几乎总是表示节点过载（CPU 饱和、磁盘延迟或每个节点 Pod/容器过多），导致运行时无法及时重新列出。与 4b 指标关联。**修复建议：** 降低节点密度，增加 CPU/磁盘余量，或分散工作负载。

#### 第 4d 步：网络

```bash
# 此节点上的节点关键网络 Pod 是否健康？
kubectl get pods -n kube-system -o wide --field-selector spec.nodeName={node_name}
```
- **Kubelet ↔ 控制平面**：到 API 服务器的拨号/TLS 超时 → 检查防火墙规则、Private Google Access、授权网络和路由/NAT 变更。
- **CNI 故障**（`NetworkPluginNotReady`）：CNI DaemonSet（`netd`/`calico`/dataplane）未在节点上运行 → 检查这些 Pod 的日志/事件。

#### 第 4e 步：准入 webhook 干扰

配置错误/失败的验证或修改 webhook，其作用域过广，可能会阻止节点关键系统 Pod 被准入，使节点保持 NotReady。

```bash
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
```
查找拦截 `kube-system` / 节点关键对象的 webhook，其 `failurePolicy: Fail`。**修复建议（提出）：** 将 webhook 的作用域排除 `kube-system`/节点关键命名空间，或设置适当的 `namespaceSelector`。

#### 第 4f 步：`kube-node-lease` 终止波动

如果节点频繁波动 NotReady 并显示 `leases.coordination.k8s.io ... namespace kube-node-lease ... is being terminated`，则 `kube-node-lease` 命名空间被删除/终止。**修复建议（提出）：** 不要删除 `kube-node-lease` 命名空间；如果终止，则识别持有该命名空间的最终化者/执行者并恢复命名空间。

--------------------------------------------------------------------------------

### 第 5 步：修复边界与升级

- 展示 **根本原因 + 证据**（观察到的确切条件、事件、日志行或指标）。提供 **Cloud Logging 深度链接**（以及第 4b 指标的 Cloud Monitoring 链接），以便人类可以直接打开证据。
- 提出供人类应用的修复方案（命令或 GitOps 资源清单更改） — 绝不自动应用、排空、删除或重建节点。
**何时升级（在此处而不是提出更多自助式诊断）：**

当以下任一情况发生时升级：

- 相关日志 **不可用** — 被日志过滤器排除，或超出日志桶的保留期（`_Default` 桶默认为 30 天，因此 30 天前的案例永久删除）；或
- kubelet/事件特征 **不在第 3 步表中**，且分支调查后根本原因 **仍不确定**。

在这种情况下，执行全部三项：

1.  **明确说明限制**（例如，"该日期的 kubelet 日志已超出 30 天的 `_Default` 保留期，并永久删除"）。
2.  **总结已收集的发现**（节点条件、事件、指标，以及 `_Required` 桶中仍然保留的任何 Admin Activity 审计日志，默认保留 400 天）。
3.  **路由到 GKE 支持 / 工程升级，并提供这些发现。** 不要继续提出进一步的自助式调查，并且在证据缺失时 **不要编造诊断结果**。

--------------------------------------------------------------------------------

## 参考

此技巧源自公共 Google Cloud 文档：

- [Troubleshoot nodes with the NotReady status](https://cloud.google.com/kubernetes-engine/docs/troubleshooting/node-notready) — 节点条件以及 kubelet / PLEG / 系统OOM / containerd / `kube-node-lease` / CNI / 准入webhook 的特征及其修复方案。
- [Troubleshoot node registration](https://cloud.google.com/kubernetes-engine/docs/troubleshooting/node-registration) — Node Registration Checker 用于从未完成注册的节点。
- [View GKE logs](https://cloud.google.com/kubernetes-engine/docs/how-to/view-logs) 和 [Cloud Logging routing overview](https://cloud.google.com/logging/docs/routing/overview) — 日志查询（`resource.type="k8s_node"`、`log_id("kubelet")`）和日志桶保留期（`_Default` 30 天，`_Required` 400 天）。
- [Logs Explorer interface](https://cloud.google.com/logging/docs/view/logs-explorer-interface) — 通过 URL 构建和共享查询（上述 `logs/query;query=...` 深度链接格式）。
