# GKE 集群创建

本指南通过提供一系列最佳实践模板，并指导用户进行模式选择和定制，来帮助创建 Google Kubernetes Engine (GKE) 集群。**黄金路径 Autopilot** 配置是所有新集群的默认配置。

> **MCP 工具:** `list_clusters`, `create_cluster`, `get_cluster`, `list_operations`, `get_operation`

## 工作流程

1.  **发现上下文**: 使用 `list_clusters` 查看现有集群。如果项目未知，请使用 `gcloud config get-value project`。
2.  **收集输入**: `project_id`, `location`（区域或区域），`cluster_name`, 环境类型。如果缺少关键信息，请在采取行动前询问用户。
3.  **选择模式并解释权衡**: 如果用户未指定模板或模式，请提供可用模板（例如 Autopilot、标准区域、GPU 推理、AI 超计算），并解释关键权衡（成本与可用性、Autopilot 与标准节点管理）。
4.  **配置网络**: 自动创建子网（默认）或自带。
5.  **审查黄金路径设置**: 展示默认配置块（`gcloud` 命令或 `create_cluster` JSON 负载），并在创建前与用户确认。
6.  **创建**: 使用 MCP `create_cluster` 工具或 `gcloud` CLI。
7.  **跟踪**: 使用 `get_operation` 监控创建进度。
8.  **验证**: 使用 `get_cluster` 并设置 `readMask="*"` 来确认黄金路径设置已应用。

## 模式选择

| 标准           | Autopilot (黄金路径)   | 标准                  |
| -------------- | --------------------- | --------------------- |
| 节点管理    | Google 管理            | 自我管理              |
| 定价            | 按 Pod 资源付费      | 按节点 (VM) 付费         |
:                : 请求                   :                           :
| 节点定制    | 通过 ComputeClasses    | 完全控制              |
| DaemonSets     | 允许（带             | 完全控制              |
:                : 限制）             :                           :
| GPU/TPU            | 通过             | 通过节点池            |
:                : ComputeClasses            :                           :
| 适用于           | 大多数生产工作负载 | 内核调优、自定义 OS、 |
:                :                           : 特权工作负载      :

> **规则**: 默认使用 Autopilot，除非客户有特定要求 Autopilot 无法满足。

## 最佳实践

在指导用户或生成配置时，请遵循以下 GKE 最佳实践：

### 安全与网络

1.  **私有集群**: 默认使用私有集群（`enablePrivateNodes: true`）和私有控制平面，并限制公共端点（`enable-master-authorized-networks`），以最小化攻击面。
2.  **VPC 本地网络**: 使用 VPC 本地集群（`useIpAliases: true` / `--enable-ip-alias`）以启用别名 IP 范围和 Pod 级防火墙规则。
3.  **工作负载身份**: 优先使用工作负载身份（`workloadPool: <PROJECT_ID>.svc.id.goog`）以安全地授予 GKE 工作负载访问 Google Cloud 服务的权限，而不是静态服务账户密钥。
4.  **Shielded GKE 节点**: 启用 Shielded GKE 节点（`--enable-shielded-nodes`, `--enable-secure-boot`）以防范 Rootkit 和 Bootkit。
5.  **最小权限 (RBAC)**: 实施严格的基于角色的访问控制限制（`scoped-rbs-bindings`）。

### 成本优化

1.  **自动扩展**: 启用集群自动扩展器和水平/垂直 Pod 自动扩展器（`--enable-autoscaling`, `--enable-vertical-pod-autoscaling`）以根据需求调整资源。
2.  **合理配置与 Spot VM**: 选择合适的机器类型和节点数量。考虑使用 Spot VM（`--spot`）为容错、非关键的批处理或推理工作负载。

### 高可用性与可靠性

1.  **区域集群**: 使用区域集群为生产环境，以确保控制平面跨多个区域复制（`--region` 而不是 `--zone`）。*注意：标准区域默认在 3 个区域创建节点。*
2.  **Pod 中断预算**: 建议为应用程序稳定性在节点维护期间设置 Pod 中断预算。
3.  **发布通道**: 订阅发布通道（`REGULAR` 或 `STABLE`）以实现自动、更安全的集群升级。

## 模板

### 1. 黄金路径 Autopilot (生产)

这是默认选项。所有设置与 `../gke-golden-path/assets/golden-path-autopilot.yaml` 匹配。

**通过 gcloud:**

```bash
gcloud container clusters create-auto <CLUSTER_NAME> \
  --region <REGION> \
  --project <PROJECT_ID> \
  --release-channel regular \
  --enable-private-nodes \
  --enable-master-authorized-networks \
  --enable-dns-access \
  --enable-secret-manager \
  --secret-manager-rotation-interval=120s \
  --scoped-rbs-bindings \
  --monitoring=SYSTEM,API_SERVER,SCHEDULER,CONTROLLER_MANAGER,STORAGE,POD,DEPLOYMENT,STATEFULSET,DAEMONSET,HPA,CADVISOR,KUBELET,DCGM \
  --quiet
```

**通过 MCP (`create_cluster`):**

```json
{
  "parent": "projects/<PROJECT_ID>/locations/<REGION>",
  "cluster": {
    "name": "<CLUSTER_NAME>",
    "autopilot": { "enabled": true },
    "privateClusterConfig": { "enablePrivateNodes": true },
    "masterAuthorizedNetworksConfig": {
      "privateEndpointEnforcementEnabled": true
    },
    "releaseChannel": { "channel": "REGULAR" },
    "secretManagerConfig": {
      "enabled": true,
      "rotationConfig": { "enabled": true, "rotationInterval": "120s" }
    },
    "rbacBindingConfig": {
      "enableInsecureBindingSystemAuthenticated": false,
      "enableInsecureBindingSystemUnauthenticated": false
    }
  }
}
```

### 2. Autopilot 开发/测试

为节省成本和简化非生产环境中的访问而放宽了一些黄金路径默认设置。

**通过 gcloud:**

```bash
gcloud container clusters create-auto <CLUSTER_NAME> \
  --region <REGION> \
  --project <PROJECT_ID> \
  --release-channel rapid \
  --quiet
```

**通过 MCP (`create_cluster`):**

```json
{
  "parent": "projects/<PROJECT_ID>/locations/<REGION>",
  "cluster": {
    "name": "<CLUSTER_NAME>",
    "autopilot": { "enabled": true },
    "releaseChannel": { "channel": "RAPID" }
  }
}
```

> **警告**: 这不应用黄金路径安全强化。仅适用于开发/测试。

### 3. 标准区域 (高可用性 / 自定义需求)

当 Autopilot 无法使用时（例如自定义内核调优、特定节点 OS 要求）最佳。默认情况下创建 3 个跨区域的节点。

**通过 gcloud:**

```bash
gcloud container clusters create <CLUSTER_NAME> \
  --region <REGION> \
  --project <PROJECT_ID> \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --disk-type pd-balanced \
  --enable-autoscaling --min-nodes 1 --max-nodes 10 \
  --enable-shielded-nodes --enable-secure-boot \
  --workload-pool=<PROJECT_ID>.svc.id.goog \
  --enable-private-nodes \
  --enable-master-authorized-networks \
  --enable-vertical-pod-autoscaling \
  --enable-dataplane-v2 \
  --release-channel regular \
  --quiet
```

**通过 MCP (`create_cluster`):**

```json
{
  "parent": "projects/<PROJECT_ID>/locations/<REGION>",
  "cluster": {
    "name": "<CLUSTER_NAME>",
    "initialNodeCount": 3,
    "nodeConfig": {
      "machineType": "e2-standard-4",
      "diskType": "pd-balanced",
      "diskSizeGb": 100,
      "oauthScopes": ["https://www.googleapis.com/auth/cloud-platform"],
      "shieldedInstanceConfig": {
        "enableSecureBoot": true,
        "enableIntegrityMonitoring": true
      },
      "workloadMetadataConfig": {
        "mode": "GKE_METADATA"
      }
    },
    "privateClusterConfig": { "enablePrivateNodes": true },
    "releaseChannel": { "channel": "REGULAR" },
    "workloadIdentityConfig": {
      "workloadPool": "<PROJECT_ID>.svc.id.goog"
    }
  }
}
```

### 4. GPU 推理与 AI 工作负载 (L4 / ComputeClass)

适用于：AI/ML 推理、小型模型服务。可通过 Autopilot + ComputeClass 或标准节点池（使用 `g2-standard-4` (`nvidia-l4`））配置。*注意：需要 `g2-standard-4` 配额。*

**Autopilot ComputeClass / GIQ 方法:**

```bash
# 1. 创建黄金路径集群（与模板 1 相同）
gcloud container clusters create-auto <CLUSTER_NAME> \
  --region <REGION> --project <PROJECT_ID> \
  --enable-private-nodes --enable-master-authorized-networks \
  --enable-dns-access --enable-secret-manager --scoped-rbs-bindings \
  --quiet

# 2. 应用 GPU ComputeClass（见 gke-compute-classes.md）
kubectl apply -f gpu-compute-class.yaml

# 3. 或使用 GIQ 进行推理（见 gke-inference.md）
gcloud container ai profiles manifests create \
  --model=gemma-2-9b-it --model-server=vllm --accelerator-type=nvidia-l4 --quiet > inference.yaml
kubectl apply -f inference.yaml
```

**标准节点池方法通过 MCP (`create_cluster`):**

```json
{
  "parent": "projects/<PROJECT_ID>/locations/<REGION>",
  "cluster": {
    "name": "<CLUSTER_NAME>",
    "initialNodeCount": 1,
    "nodeConfig": {
      "machineType": "g2-standard-4",
      "accelerators": [
        {
          "acceleratorCount": "1",
          "acceleratorType": "nvidia-l4"
        }
      ],
      "diskSizeGb": 100,
      "oauthScopes": ["https://www.googleapis.com/auth/cloud-platform"]
    }
  }
}
```

### 5. AI 超计算 (A3 高 GPU / 大型模型服务)

适用于：大规模 LLM / AI 模型训练和超计算推理。*注意：高小时成本和严格的配额要求（`a3-highgpu-8g` / `nvidia-h100-80gb-hbm3`）。*

**通过 gcloud:**

```bash
gcloud container clusters create <CLUSTER_NAME> \
  --region <REGION> \
  --project <PROJECT_ID> \
  --num-nodes 1 \
  --machine-type a3-highgpu-8g \
  --accelerator type=nvidia-h100-80gb-hbm3,count=8 \
  --disk-size 200 \
  --scopes https://www.googleapis.com/auth/cloud-platform \
  --workload-pool=<PROJECT_ID>.svc.id.goog \
  --release-channel regular \
  --quiet
```

**通过 MCP (`create_cluster`):**

```json
{
  "parent": "projects/<PROJECT_ID>/locations/<REGION>",
  "cluster": {
    "name": "<CLUSTER_NAME>",
    "initialNodeCount": 1,
    "nodeConfig": {
      "machineType": "a3-highgpu-8g",
      "accelerators": [
        {
          "acceleratorCount": "8",
          "acceleratorType": "nvidia-h100-80gb-hbm3"
        }
      ],
      "diskSizeGb": 200,
      "oauthScopes": ["https://www.googleapis.com/auth/cloud-platform"]
    }
  }
}
```

## 说明

-   **始终**在上下文中没有 `project_id` 时请求 `project_id`。
-   **始终**请求 `region`（或位置）。
-   **始终**请求一个唯一的 `cluster_name`。
-   **默认**使用黄金路径 Autopilot，除非客户指定其他选项或具有自定义节点/内核/超计算需求。
-   **始终警告**当选择 GKE 标准，强调其偏离黄金路径，并解释增加的运营/管理开销（手动管理节点池、升级和自动扩展）。
-   **解释权衡**当向用户展示模板或模式选择时，如果他们未指定（例如 Autopilot 与标准、成本与可用性）。
-   **展示配置**块（`gcloud` 命令或 JSON 负载），并在调用任何创建工具前请求确认。
-   **警告**关于 Day-0 决策（网络、私有节点），这些决策后期难以更改。
-   **明确警告**关于成本和配额要求，当用户选择 GPU（`g2-standard-4`, `a3-highgpu-8g`）、TPU 或多区域/区域集群（`--region` 默认为 3 个区域）。
-   当使用 MCP `create_cluster` 时，`cluster.name` 参数应该是**短名称**（例如 `my-cluster`），而不是完整资源路径（`projects/<PROJECT_ID>/locations/<REGION>/clusters/<CLUSTER_NAME>`）。`parent` 参数定义作用域（`projects/<PROJECT_ID>/locations/<REGION>`）。
