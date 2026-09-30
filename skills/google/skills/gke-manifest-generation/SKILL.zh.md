---
name: gke-manifest-generation
description: 生成和更新针对 GKE Autopilot 和 GKE Standard 集群优化的安全、生产就绪的 Kubernetes YAML 配置文件。在创建或修改 GKE 部署配置文件、配置容器安全上下文、设置 CPU/内存资源限制、定义就绪/存活/启动探针、挂载密钥和卷、配置 GKE Gateway API 路由、目标 Spot 虚拟机或部署 AI 模型推理工作负载（vLLM、TGI、Gemma）时使用。不应用于实时集群操作、Pod 故障排除（使用 gke-workload-troubleshooting）或集群基础设施配置（使用 gke-cluster-creation）。
---

# GKE 资源清单生成技能

本技能提供指南、工具集成和模板，用于将自然语言描述或应用程序代码变更转换为针对 GKE Autopilot 和 GKE Standard 集群优化的、安全合规且经济高效的 Kubernetes YAML 资源清单。

## 核心规则与验证

在生成或更新 YAML 资源清单时，你必须严格遵循以下规则：

### 1. 命名空间与资源隔离

-   **显式命名空间**：在所有资源（部署、服务、配置映射、密钥、持久卷声明、角色、绑定）的元数据中始终显式声明 `namespace: {namespace}`。映射到你在活动 `SETTINGS.md` 中配置的命名空间。绝不能省略命名空间。
-   **专用 ServiceAccount**：避免使用命名空间的 `default` ServiceAccount。始终为每个微服务创建和引用一个专用的 `ServiceAccount`（例如 `devteam-agent-sa`）。

### 2. GKE 资源调优（Autopilot & Standard）

-   **资源请求与限制**：始终为所有容器指定 CPU 和内存请求和限制。
    -   *GKE Autopilot*：请求直接决定 Pod 的计费；请求和限制必须相等。如果它们不同，Autopilot 将自动将请求扩展到匹配限制，这会显著增加成本。
    -   *GKE Standard*：请求确保稳定调度和装箱；限制防止资源饥饿/噪声邻居问题。
-   **密度默认值**：对于 GKE Standard 上的无状态应用程序或边车，默认使用保守的请求（例如 `requests.cpu: "100m"` 或 `"200m"`，`requests.memory: "256Mi"` 或 `"512Mi"`），并使用可突发限制。为限制使用合理的超配比（例如 2x 到 4x 请求，例如 `limits.cpu: "400m"` 到 `"800m"`，以及 `limits.memory: "512Mi"` 到 `"1Gi"`）。避免过度超配限制（例如 `limits.cpu: "4"` 用于 `100m` 请求），以防止在重调度负载下出现严重的 CPU 限制和延迟下降，特别是在没有保证节点份额的环境中。
-   **用于预发布/开发环境的 Spot VM**：对于非生产工作负载（例如包含 `-test`、`-dev` 或 `-staging` 的命名空间），或者如果用户请求成本优化，自动目标 GKE Spot VM。这需要注入同时针对 Spot VM 的 `nodeSelector` 和相应的容忍 Spot VM 污点：

    ```yaml
    nodeSelector:
      cloud.google.com/gke-spot: "true"
    tolerations:
      - key: "cloud.google.com/gke-spot"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
    ```

    （在 GKE Standard 上，这假设已配置 Spot 节点池）。

### 3. 容器安全加固（Pod 安全标准）

-   **非 root 执行**：始终在 Pod 级别（如果覆盖则容器级别）配置 `securityContext` 以作为非 root 用户运行（例如 `runAsNonRoot: true`，`runAsUser: 10000`，`runAsGroup: 10000`，`fsGroup: 10000`）。这在 GKE Autopilot 上是严格强制的，并且是 GKE Standard 的关键安全基线。
-   **最小权限**：始终设置 `allowPrivilegeEscalation: false` 和 `seccompProfile: {type: RuntimeDefault}`。
-   **只读根文件系统**：设置 `readOnlyRootFilesystem: true` 以防止修改容器镜像文件系统。
    -   *可写目录回退*：如果 `readOnlyRootFilesystem` 已启用，则挂载本地 `emptyDir` 卷到 `/tmp` 或 `/var/run/`，以允许应用程序（如 Java/Nginx）写入临时文件而不会崩溃。
-   **密钥卷挂载**：优先将密钥挂载为只读文件（在 `volumes` 规范中配置 `defaultMode: 0400`），而不是作为环境变量映射，除非应用程序框架仅支持基于环境变量的配置。这可以防止密钥泄露到应用程序日志中。

### 4. 健康检查（强制探针）

-   **存活与就绪探针**：每个部署容器必须定义 `livenessProbe` 和 `readinessProbe`。
    -   **Web/API**：使用 `httpGet` 探针。
    -   **TCP 服务**：使用 `tcpSocket` 探针。
    -   **数据库/缓存**：使用基于命令的 `exec` 探针（例如 `exec.command: ["redis-cli", "ping"]`）。
-   **慢启动应用程序的启动探针**：对于具有慢启动时间的应用程序（例如 Java spring boot、复杂的 Python 脚本、LLM 模型服务器），你必须定义 `startupProbe`。当定义了 `startupProbe` 时，存活和就绪探针将被禁用，直到它成功，以防止 Kubernetes 在启动期间过早杀死 Pod：

    ```yaml
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    ```

-   **合理默认值**：根据启动时间设置 `initialDelaySeconds: 5` 到 `15`（例如 Java 需要比 Go/Nginx 更长的延迟）。

### 5. 服务与 Ingress 路由

-   **内部 ClusterIP**：将所有内部微服务默认设置为 `type: ClusterIP`。除非工作负载明确打算从互联网公开访问，否则永远不要使用 `type: LoadBalancer` 或 `NodePort`。
-   **端口命名**：始终为服务和容器端口分配清晰的标准名称（例如 `name: http-web` 或 `name: grpc-api`），以启用自动协议发现、跟踪和 Web 应用路由。
-   **优先使用 Gateway API**：当从外部公开 API 时，优先使用 GKE Gateway API（`Gateway` 和 `HTTPRoute` 资源）而不是传统的 `Ingress` 对象，以启用高级 L7 路由和安全性功能（例如 Cloud Armor）。

### 6. 卷挂载、StorageClasses & subPath 安全

-   **避免目录覆盖**：当将 `ConfigMap` 或 `Secret` 挂载到包含其他文件的应用程序目录（如 Nginx 公共目录）时，始终使用 `subPath` 仅覆盖特定文件。
    *注意*：使用 `subPath` 卷挂载的容器不会在底层 ConfigMap 或 Secret 修改时自动接收配置更新；必须手动重新启动 Pod 才能获取更改。
-   **StorageClass 选择**：在 PersistentVolumeClaims 中使用正确的 GKE 存储类：
    -   *CSI 驱动集群（Autopilot & 现代标准）*：使用 `standard-rwo`（默认平衡 PD）或 `premium-rwo`（SSD PD）。
    -   *传统标准集群*：如果未配置 `standard-rwo`/`premium-rwo`，则使用 `standard`（默认 PD）或 `premium`（SSD PD）。
    -   *数据库规则*：仅在提示明确要求高 IOPS、低延迟或数据库存储时使用 SSD 存储类（`premium-rwo` 或 `premium`）。

### 7. GKE 上的高可用性

-   **拓扑扩展**：对于具有 >1 个副本的部署，使用 `podAntiAffinity` 或 `topologySpreadConstraints` 并设置 `topologyKey: "kubernetes.io/hostname"` 以将 Pod 分布到 GKE 节点和可用区。
-   **PodDisruptionBudget**：对于具有 >1 个副本的部署，声明 `PodDisruptionBudget` 以保证在自愿的 GKE 节点升级和维护周期期间最小副本可用性。

### 8. 更新与服务器端应用 Reconciliations

-   **稳定的列表键**：在 Kubernetes 服务器端应用（SSA）下，关联列表（如卷、卷挂载、端口和容器定义）中的元素通过其唯一标识符键（通常为 `name`）进行匹配和合并。你必须修改现有列表项的属性时保持 `name` 键稳定。重命名 `name` 键会导致 SSA 创建一个全新的条目，并将旧条目保留为孤儿（而不是修改它）。
-   **最小差异**：仅进行所请求的更改。紧密遵循现有的标签、注解和约定。

--------------------------------------------------------------------------------

## 特殊工作负载：GKE AI/推理服务（vLLM、TGI 等）

对于模型服务工作负载，如果可用，请优先使用优化的工具（如 GKE 推理快速入门）。如果手动生成：

1.  **GPU 请求与分配**：
    -   始终在 `requests` 和 `limits` 中请求 `nvidia.com/gpu`。
    -   添加一个 `nodeSelector` 或节点亲和性，针对所需的 GKE 加速器标签（例如 `cloud.google.com/gke-accelerator: nvidia-l4`）。
2.  **共享内存增强**：
    -   模型服务器需要高共享内存（`/dev/shm`）进行进程间通信。始终声明并挂载一个 `emptyDir` 卷到 `/dev/shm`，并设置 `medium: Memory`。
3.  **权重加载优化**：
    -   使用 GKE GCS Fuse CSI 驱动（`csi.storage.gke.io`）将模型权重目录（如 GCS 桶）挂载为 `readOnly: true`，以实现高效的冷启动。

--------------------------------------------------------------------------------

## 工具与基础指南

在生成清单时，你应该利用以下工具来减少幻觉并优化配置：

1.  **推理工作负载（GKE 推理快速入门 CLI）**：

    -   确保你已经安装了 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)。
    -   对于所有 AI/LLM 推理工作负载（例如模型服务），你必须优先使用 `gcloud` CLI GKE 推理快速入门命令来生成优化的清单，而不是手动编写：

        ```bash
        gcloud container ai profiles manifests create \
          --model={model_name} \
          --model-server={server_name} \
          --accelerator-type={accelerator_type} \
          --output=manifest \
          --output-path={output_file_path}
        ```

    -   *约束*：你必须包含此命令返回的所有资源（部署、服务、PodMonitoring 等），不得过滤。

2.  **基于官方文档（开发者知识 API）**：

    -   对于 GKE 特定功能、API 默认值、清单示例或安全上下文，你必须查询 Google 的开发者知识库以检索官方 GKE 文档：
        -   **`answer_query`**：使用此工具提出直接问题（例如，*"如何在 GKE 中配置 GCS Fuse CSI 驱动"*）。这是用于一般查询的首选工具。
        -   **`search_documents`**：当你没有特定问题时，使用此工具搜索相关的 GKE 指南或示例。
        -   **`get_document`**：当你有特定文档 ID 时，使用此工具获取完整文档内容。

--------------------------------------------------------------------------------

## 参考示例

有关详细、生产就绪的清单模板，请参阅以下参考指南：

-   **[基础加固 Nginx 工作负载](references/basic-workload.md)**：具有专用 ServiceAccount、安全上下文、探针、反亲和性和 PodDisruptionBudget 的生产就绪部署。
-   **[网络策略](references/network-policy.md)**：默认拒绝入站网络策略和针对特定应用程序的选择性入站允许。
-   **[AI/LLM 推理工作负载](references/ai-inference.md)**：GPU 资源分配、Workload Identity、GCS FUSE CSI 驱动挂载、`/dev/shm` 共享内存增强和启动探针。
-   **[GKE Gateway API 路由](references/gateway-api.md)**：使用 GKE L7 Gateway API（`Gateway` 和 `HTTPRoute` 资源）公开工作负载。
