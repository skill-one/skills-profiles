# GKE 工作负载故障排除技能

使用此技能系统性地诊断和解决在 GKE 集群中部署的应用工作负载的故障。此技能非交互式操作，并强制执行只读诊断边界：它仅**建议**修复措施——无论是 Kubernetes 声明文件/配置补丁还是 Google Cloud 变更（例如 `gcloud` IAM 绑定或节点池重建）——本身从不执行实时变更。

## 🔍 诊断工作流

### 第 0 步：非交互式上下文发现和时间窗口定义

1.  **参数提取**：从用户提示、活动的 `SETTINGS.md` 或活动环境默认值中非交互式地提取所需上下文（`project_id`、`cluster_name`、`cluster_location`、`workload_name`、`workload_namespace`）：

    -   如果省略，则默认将 `workload_namespace` 设置为 `default`。
    -   从活动环境推断缺失的集群参数（`kubectl config current-context` 或 `gcloud config get-value project`）。
    -   优先从提示和环境默认值中非交互式地发现上下文，以确保自主执行流程。

2.  **集群凭证和回退模式**：

    -   尝试凭证获取：`gcloud container clusters get-credentials {cluster_name} --region/--zone {cluster_location}`
    -   **回退/干运行模式**：如果集群无法访问、不存在或实时命令执行失败（例如在沙盒评估、干运行模式或离线分析中）：
        -   限制重试次数，以避免在无法访问的集群场景中资源耗尽和上下文溢出。
        -   立即向人类操作员展示精确的 `kubectl` 诊断命令序列以供运行。
        -   根据报告的症状合成根本原因分析，并输出建议的 GitOps 声明文件修复。

3.  **时间处理和回退**：

    -   **确定问题时间戳 ({issue_time})**：
        -   **提供具体时间**：如果用户提供具体时间戳，则将其用作 `{issue_time}`。
        -   **提供相对时间（例如，“5 分钟前”）**：根据当前系统时间动态计算相应的 UTC 时间戳，并用作 `{issue_time}`。
        -   **未提供时间（默认）**：使用当前系统时间作为 `{issue_time}`。
    -   **窗口计算**：以 `{issue_time}` 为中心，设置一个 1 小时的查询窗口（`start_time` = `{issue_time} - 30m`，`end_time` = `{issue_time} + 30m`）。

--------------------------------------------------------------------------------

### 第 1 步：分析 Pod 状态和条件

检查工作负载的活跃 Pod 状态和控制器状态。

**诊断命令：**

```bash
# 1. 检查部署的实际选择器标签：
kubectl get deployment {workload_name} -n {workload_namespace} -o jsonpath='{.spec.selector.matchLabels}'
# 2. 使用返回的标签查询 Pod，例如：
kubectl get pods -l {selector_labels} -n {workload_namespace}
kubectl get deploy/{workload_name} -n {workload_namespace} -o yaml
```

#### 诊断决策树：

-   **阶段：Pending**：
    -   Pod 无法在任何节点上调度。直接进入 **第 2 步（查询命名空间事件）**。
-   **状态：CrashLoopBackOff / Error**：

    -   容器启动但反复退出；`kubelet` 使用递增的回退延迟（最多五分钟）重新启动它。首先读取终止的 **原因** 和 **退出代码**：

    ```bash
    kubectl describe pod {pod_name} -n {workload_namespace}
    kubectl get pod {pod_name} -n {workload_namespace} -o jsonpath='{.status.containerStatuses[*].lastState.terminated}'
    ```

    -   **原因：OOMKilled（退出代码 137）**：容器的内存限制被达到。进入 **第 3 步（检查日志）→ OOM 分析** 以对容器级与节点级进行分类，然后进入 **第 5 步** 以提出修复建议。
    -   **退出代码 0（成功退出）**：对于长时间运行的 Deployment/StatefulSet 来说不常见——`restartPolicy: Always` 重新启动完成的进程，从而创建循环。常见原因：`command`/`entrypoint` 未启动持久化进程、工作进程在空队列上退出，或缺少/无效的配置（例如未挂载或密钥错误的 `ConfigMap` 卷）使应用干净退出。进入 **第 3 步（检查日志）**。
    -   **退出代码 128**：无效的 `command`/`entrypoint`——可执行路径错误或镜像中不存在。验证声明文件中的容器命令。
    -   **退出代码 1 或其他非零**：应用崩溃——配置错误、缺少/无效的环境变量或配置文件、无法访问的依赖项，或 Google Cloud 调用上的认证失败（检查 Pod 的 IAM / Workload Identity Federation）。直接进入 **第 3 步（检查日志）**。
    -   如果退出代码看起来健康但容器仍在重启，怀疑 **liveness probe 失败**（见第 3 步）。

-   **状态：ImagePullBackOff / ErrImagePull**：

    -   `kubelet` 无法拉取容器镜像。`ImagePullBackOff` 表示它不断重试并使用回退；`ErrImagePull` 是一个通用且不可恢复的拉取错误。相关状态：`InvalidImageName`、`RegistryUnavailable`、`SignatureValidationFailed`、`ImageInspectError`。进入 **第 2 步（查询命名空间事件）** 读取确切的拉取错误消息。

-   **状态：ContainerCreating**：

    -   容器在卷挂载、网络设置或镜像拉取期间被阻塞。直接进入 **第 2 步（查询命名空间事件）**。

--------------------------------------------------------------------------------

### 第 2 步：查询命名空间事件

在 GKE 中查找基础设施、卷、镜像或调度警报。

**诊断命令：**

```bash
kubectl get events -n {workload_namespace} --sort-by='.metadata.creationTimestamp'
# 或查询 Cloud Logging 以获取时间窗口内的历史 GKE 事件：
gcloud logging read "resource.type=\"k8s_cluster\" AND logName=\"projects/{project_id}/logs/events\" AND jsonPayload.involvedObject.namespace=\"{workload_namespace}\"" --start-time="{start_time}" --end-time="{end_time}" --project="{project_id}"
# 或查询时间窗口内的特定镜像拉取失败：
gcloud logging read 'log_id("events") AND resource.type="k8s_pod" AND resource.labels.cluster_name="{cluster_name}" AND jsonPayload.message=~"Failed to pull image"' --project="{project_id}"
```

*注意：获取排序的事件列表并手动检查事件时间戳（CreationTimestamp/LastSeen）以识别在 `{start_time}` 和 `{end_time}` 窗口内发生的故障。*

#### 签名标识符：

-   **`FailedScheduling`**：节点资源耗尽。查找类似 `0/3 nodes are available: 3 Insufficient memory.` 的消息或缺少节点亲和性容忍（例如 Spot VM 污点）。
-   **`FailedMount`**：
    -   缺少 PersistentVolumeClaim (`PVC`)。
    -   缺少 Secret (`Secret "{secret_name}" not found`).
    -   缺少 ConfigMap (`ConfigMap "{configmap_name}" not found`).
-   **`Failed` / `BackOff`（镜像拉取）**：首先读取确切的事件消息（`Failed to pull image "IMAGE": ...`）并根据实际内容进行分类。除非消息确实是权限或认证错误，否则**不要**跳转到 IAM / 节点服务账户调查。

    -   **错误的镜像名称/标签——从这里开始**（`not found`、`manifest unknown`、`InvalidImageName`）：最常见的原因——标签或路径错误，或镜像已被删除，经常由最近的部署更改引入。
        *   确定失败的容器镜像名称和无效的标签。
        *   检查 Git 历史记录以获取最后一个已知工作的镜像标签：`git log -p -S "{image_name}" -- {manifest_file_path}`（或运行 `git log` 在包含声明的文件夹上）。
        *   建议将镜像标签还原到最后一个工作版本（或更正标签）在声明文件补丁中。
    -   **权限/认证错误**（消息包含 `403 Forbidden` / `denied` 或 `401 Unauthorized` / `unauthorized`）：节点无法授权或认证到注册表。仅在消息匹配时才执行以下检查。

        *   **`403 Forbidden`（授权）**——节点池服务账户（或 `imagePullSecret` 的服务账户）缺少注册表读取权限。**建议**通过向用户展示以下命令以供审查和运行来授予它；不要执行它。对于 **Artifact Registry**：

            ```bash
            gcloud artifacts repositories add-iam-policy-binding {repository} \
              --location={repo_location} \
              --member="serviceAccount:{node_service_account_email}" \
              --role="roles/artifactregistry.reader"
            ```

            对于 **Container Registry (`gcr.io`)**，授予对底层存储桶的 `roles/storage.objectViewer`（如果 `gcr.io` 已迁移则为 Artifact Registry 角色）。还检查任何 **VPC Service Controls** 边缘是否允许 Artifact Registry。
        *   **`401 Unauthorized`（认证）**——节点服务账户被禁用或节点缺少所需的 OAuth 范围：

            ```bash
            gcloud container clusters describe {cluster_name} --location={cluster_location} \
              --format="table(nodePools.name,nodePools.config.serviceAccount)"
            gcloud iam service-accounts list \
              --filter="email:{node_service_account_email} AND disabled:true" --project={project_id}
            gcloud compute instances describe {node_name} --zone={node_zone} \
              --format="flattened(serviceAccounts[].scopes)"
            ```

            范围必须包括 `devstorage.read_only` 或 `cloud-platform`（由 `gke-default` 提供）。节点是不可变的，因此**建议**使用 `--scopes="gke-default"` 重新创建节点池，如果范围缺失——将其作为建议命令展示给用户，不要执行。
        *   **私有/自托管注册表**：确保存在有效的 `imagePullSecret` 并由 Deployment 引用。
    -   **其他状态**：`RegistryUnavailable` / `i/o timeout` / DNS `server misbehaving` → 注册表网络路径（DNS、防火墙出站、Google API 连接性）；`exec format error` 或过时的 schema-1 镜像 → 架构/模式不匹配。

--------------------------------------------------------------------------------

### 第 3 步：检查应用日志

从应用运行时提取异常和堆栈跟踪。

**诊断命令：**

```bash
# 检查当前活跃的日志流（处理多容器 Pod）
kubectl logs {pod_name} -n {workload_namespace} --all-containers --tail=100

# 检查先前终止的容器实例的日志（处理多容器 Pod）
kubectl logs {pod_name} -n {workload_namespace} --all-containers -p --tail=100
```

#### 签名标识符：

-   **OOM 分析**：首先确认并分类终止。

    -   **容器级 OOM**（最常见）：`kubectl describe pod` 显示 `Last State: Terminated`、`Reason: OOMKilled`、`Exit Code: 137`。容器超出其 cgroup 内存限制。区分应用内存泄漏/循环（日志和启动命令中无界增长）与基础设施容量不匹配（合法需求超过 `resources.limits.memory`）。
    -   **节点级（系统）OOM**：整个节点内存耗尽；查找被驱逐的 Pod 和节点压力驱逐。所有 Pod 的内存总和超过了节点容量。
    -   **“隐形”OOM（`cgroup v1`）**：子进程被杀死但主进程（PID 1）仍在运行，因此 Kubernetes 从不标记 `OOMKilled`。在 Cloud Logging 中搜索节点日志：

        ```bash
        gcloud logging read 'resource.type="k8s_node" AND resource.labels.cluster_name="{cluster_name}" AND jsonPayload.MESSAGE:("TaskOOM event" OR "ContainerDied")' --project="{project_id}"
        ```

        `TaskOOM` 条目确认了 OOM 杀死；将其容器 ID 与 `ContainerDied` 条目匹配以找到受影响的 Pod。在节点上，`journalctl -k` 区分容器级杀死（`memory cgroup`、`memcg`）和系统级杀死（`Out of memory: Killed process`）。
    -   不要仅依赖采样的内存指标——它们通常错过了触发杀死的峰值。然后进入 **第 5 步** 以提出修复建议（提高限制、修复泄漏或调整节点池大小）。
-   **Liveness Probe 失败（CrashLoop 但无应用错误）**：如果容器重启但其日志显示无崩溃，`kubelet` 可能因 liveness probe 失败（默认 `failureThreshold: 3`）而杀死它。在 Cloud Logging 中确认：

    ```bash
    gcloud logging read 'resource.type="k8s_node" AND log_id("kubelet") AND jsonPayload.MESSAGE:"failed liveness probe, will be restarted" AND resource.labels.cluster_name="{cluster_name}"' --project="{project_id}"
    ```

    常见修复：修正 probe 类型/路径/端口，提高 `initialDelaySeconds` 或 `timeoutSeconds`/`failureThreshold` 以适应慢启动，或减轻导致 probe 超时的 CPU/磁盘 I/O 竞争。保持 probe 命令轻量。
-   **堆栈跟踪/未处理的异常**：查找特定语言的堆栈跟踪（例如 `panic:`、`NullPointerException`、`Traceback (most recent call)`）。这表示应用错误。
-   **出站网络超时**：查找连接超时（例如 `Connection timed out`、`dial tcp: i/o timeout`）。进入 **第 4 步（验证连接性）**。
-   **权限错误（ReadOnlyRootFilesystem）**：查找写入错误（例如 `Read-only file system`、`Permission denied` 当写入 `/tmp` 或 `/var/log`）。建议在声明文件中添加该目录的 `emptyDir` 卷挂载。

--------------------------------------------------------------------------------

### 第 4 步：验证服务连接性和网络策略

解决连接到其他服务的连接中断。

**诊断命令：**

```bash
# 验证目标端点是否活跃
kubectl get endpoints {target_service_name} -n {target_namespace}

# 查询命名空间内的网络策略
kubectl get networkpolicies -n {workload_namespace} -o yaml
```

#### 逻辑和干运行回退：

1.  **实时集群模式**：

    -   如果 `kubectl get endpoints` 返回空列表，目标微服务本身无法调度或启动（排查目标服务）。
    -   如果端点存在但日志显示超时，分析 `NetworkPolicy` 出站阻止以验证是否允许出站流量到目标服务的 IP/端口。

2.  **沙盒/干运行模式**：

    -   如果实时 `kubectl` 查询失败或集群连接不可用，**不要**重试实时集群访问或进入重复连接尝试。
    -   立即检查应用源代码（例如 `worker.py`、`app.go`、DB 连接字符串）或 Deployment 声明文件以识别目标服务主机名（例如 `account-db`）和目标端口（例如 `5432`）。
    -   向用户展示精确的 `kubectl get endpoints` 和 `kubectl get networkpolicies` 命令，并综合所需的 `NetworkPolicy` 出站补丁以允许流量到目标服务和端口。

--------------------------------------------------------------------------------

### 第 5 步：提出 GitOps 修正

遵循 GitOps 边界，**不要直接应用变更**——这包括集群声明文件/配置补丁和任何 Google Cloud 变更（例如 `gcloud` IAM 绑定或节点池重建）。将每个变更作为可审查的建议呈现：声明文件补丁/PR，或用户可运行的命令。

1.  为人类操作员综合根本原因分析（例如 *"payment-api 因退出代码 137 失败，因为其内存限制设置为 256Mi，而实际使用量飙升至 270Mi"*）。
2.  生成修正的 YAML 声明文件补丁（例如提高内存限制、添加缺少的 Secret 挂载，或添加 Spot 节点的容忍）。
3.  检查是否已存在此工作负载/故障的分支或 Pull Request (PR)。如果存在，则更新现有分支/PR 或通知用户，而不是创建重复项。否则，创建分支，提交更改，在 GitHub 上打开 Pull Request (PR)，并结束工作流（不要等待人工合并）。

--------------------------------------------------------------------------------

## 参考

-   [Troubleshoot OOM events](https://docs.cloud.google.com/kubernetes-engine/docs/troubleshooting/oom-events.md.txt)
-   [Troubleshoot image pulls](https://docs.cloud.google.com/kubernetes-engine/docs/troubleshooting/image-pulls.md.txt)
-   [Troubleshoot CrashLoopBackOff events](https://docs.cloud.google.com/kubernetes-engine/docs/troubleshooting/crashloopbackoff-events.md.txt)
-   [Troubleshoot deployed workloads](https://docs.cloud.google.com/kubernetes-engine/docs/troubleshooting/deployed-workloads.md.txt)
-   [Artifact Registry access control with GKE](https://docs.cloud.google.com/artifact-registry/docs/access-control.md.txt#gke)
