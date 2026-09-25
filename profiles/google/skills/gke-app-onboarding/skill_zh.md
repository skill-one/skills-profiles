# GKE 应用入门

本指南提供了首次将应用程序容器化并部署到 GKE 的工作流程。

> **MCP 工具：** `apply_k8s_manifest`, `get_k8s_resource`, `get_k8s_rollout_status`, `get_k8s_logs`, `describe_k8s_resource`

## 工作流程

### 1. 应用评估

在容器化之前，评估应用程序：

-   **语言 & 框架**：确定技术栈
-   **依赖项**：列出所需的库和外部服务
-   **配置**：应用程序如何进行配置？（环境变量、配置文件、密钥）
-   **有状态性**：是否需要持久化存储？（数据库、文件存储）
-   **网络**：端口映射和协议（HTTP、gRPC、TCP）
-   **健康端点**：应用程序是否暴露健康检查端点？

### 2. 容器化

创建容器镜像。对于大多数应用程序，建议使用多阶段构建的 Dockerfile —— 请参阅 [`references/go-example.md`](./references/go-example.md) 中的 Go Dockerfile 示例。

**最佳实践：**

-   使用多阶段构建以保持生产镜像小巧
-   使用 distroless 或最小基础镜像以减少攻击面
-   以非 root 用户运行
-   将日志记录到 `stdout` 和 `stderr` 以便 Cloud Logging 收集

完整的 Node.js 示例提供在 [`assets/`](./assets/) 中：
[`Dockerfile`](./assets/Dockerfile)（非 root `node` 用户）,
[`index.js`](./assets/index.js)（实现 `/healthz` 和 `/readyz` 端点）,
[`package.json`](./assets/package.json), 和
[`deployment.yaml`](./assets/deployment.yaml)（加固的 Deployment 加 ClusterIP Service，探针连接到 `/healthz` 和 `/readyz`）。

对于不希望编写 Dockerfile 的应用程序，您可以使用
[**云原生构建包**](https://buildpacks.io/) 自动检测语言并构建容器镜像：

```bash
pack build <image> --builder gcr.io/buildpacks/builder:latest
```

### 3. 镜像管理

构建并存储容器镜像：

```bash
# 配置 Docker 以使用 Artifact Registry
gcloud auth configure-docker <REGION>-docker.pkg.dev --quiet

# 构建并推送
docker build -t <REGION>-docker.pkg.dev/<PROJECT>/<REPO>/<IMAGE>:<TAG> .
docker push <REGION>-docker.pkg.dev/<PROJECT>/<REPO>/<IMAGE>:<TAG>
```

**漏洞扫描**：在 Artifact Registry 中启用自动扫描以检测基础镜像和依赖项中的问题。

```bash
# 检查扫描结果
gcloud artifacts docker images describe \
  <REGION>-docker.pkg.dev/<PROJECT>/<REPO>/<IMAGE>:<TAG> \
  --show-package-vulnerability \
  --quiet
```

### 4. 配置文件生成

为应用程序生成 Kubernetes 配置文件。基线 Deployment + ClusterIP Service 配置文件（探针、资源请求/限制、2 个副本）在 [`references/go-example.md`](./references/go-example.md) 中。

**配置文件清单：**

-   设置资源请求和限制
-   配置 liveness 和 readiness 探针
-   至少 2 个副本用于生产
-   适当的 Service 类型（内部使用 ClusterIP，外部使用 Gateway API）

请参阅 [`assets/deployment.yaml`](./assets/deployment.yaml) 以获取加固的示例。生产加固的 Pod 配置必须包含所有：`runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, `seccompProfile: {type: RuntimeDefault}`, `automountServiceAccountToken: false`（除非 Pod 需要令牌——如果需要，请说明原因），资源请求，固定摘要的镜像，以及 ClusterIP Service。

该清单是此处生成的任何 Pod 配置的基线。对于超出该清单的配置文件工作——Gateway API 路由、GCS FUSE 和密钥卷挂载、`subPath` 覆盖、Spot VM 目标或 AI/推理服务配置文件——请参阅 `gke-manifest-generation`。

### 5. 部署

```
# MCP（推荐）
apply_k8s_manifest(parent="projects/<PROJECT>/locations/<REGION>/clusters/<CLUSTER>", yamlManifest="<manifest>")

# 验证
get_k8s_rollout_status(parent="...", resourceType="deployment", name="my-app")
get_k8s_resource(parent="...", resourceType="pod", labelSelector="app=my-app")
```

**kubectl 备用方案：**

```bash
kubectl apply -f manifests/
kubectl rollout status deployment/my-app
kubectl get pods -l app=my-app
```

## 金路径入门清单

对于每个首次入门 GKE 的生产应用程序：

1.  **容器安全**：非 root 用户 (`runAsNonRoot: true`)，锁定文件安装，最小化/distroless 基础镜像。
2.  **资源请求**：显式 CPU 和内存请求（GKE Autopilot 的强制要求）。
3.  **健康探针**：配置 liveness (`livenessProbe`) 和 readiness (`readinessProbe`) 探针。
4.  **可靠性与可用性**：至少 2 个副本和 `PodDisruptionBudget` (`minAvailable: 1` 或 `2`)。
5.  **IAM 与工作负载身份**：使用 Workload Identity (`iam.gke.io/gcp-service-account`) 而不是静态服务账户密钥。

## 下一步

应用程序在 GKE 上运行后：

-   配置自动扩展——请参阅 `gke-workload-scaling` 技能
-   设置可观察性——请参阅 `gke-observability` 技能
-   加固安全——请参阅 `gke-workload-security` 技能
-   配置可靠性（PDBs、拓扑分布）——请参阅 `gke-reliability` 技能
