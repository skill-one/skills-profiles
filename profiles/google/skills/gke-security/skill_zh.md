# GKE 安全

本指南涵盖 GKE 集群的安全配置。黄金路径默认强制执行强化后的安全态势。

> **MCP 工具:** `get_cluster`, `check_k8s_auth`, `get_k8s_resource`,
> `apply_k8s_manifest`, `update_cluster`

## 黄金路径安全默认值

设置                                                        | 黄金路径值                       | Day-0/1 | 备注
-------------------------------------------------------------- | --------------------------------------- | ------- | -----
`workloadIdentityConfig.workloadPool`                          | `<PROJECT>.svc.id.goog`                 | Day-0   | Pod 的工作负载身份联合
`secretManagerConfig.enabled`                                  | `true`                                  | Day-1   | Google Secret Manager 集成
`secretManagerConfig.rotationConfig`                           | `enabled: true, rotationInterval: 120s` | Day-1   | 自动密钥轮换
`rbacBindingConfig.enableInsecureBindingSystemAuthenticated`   | `false`                                 | Day-0   | 阻止旧的 `system:authenticated` 绑定
`rbacBindingConfig.enableInsecureBindingSystemUnauthenticated` | `false`                                 | Day-0   | 阻止旧的 `system:unauthenticated` 绑定
`nodeConfig.shieldedInstanceConfig.enableSecureBoot`           | `true`                                  | Day-0   | 可验证的启动完整性
`nodeConfig.shieldedInstanceConfig.enableIntegrityMonitoring`  | `true`                                  | Day-0   | 运行时完整性检查
`nodeConfig.workloadMetadataConfig.mode`                       | `GKE_METADATA`                          | Day-0   | 阻止旧的元数据 API，强制执行工作负载身份
私有集群 + Dataplane V2 设置                        | 参考 `gke-networking` 技能          | Day-0   | 私有节点，私有端点强制执行，ADVANCED_DATAPATH

## 工作负载身份联合

工作负载身份是 Pod 访问 Google Cloud API 的推荐方式。它消除了对静态服务账户密钥的需求。

### 设置

```bash
# 1. 创建 Google 服务账户 (GSA)
gcloud iam service-accounts create <GSA_NAME> \
  --project <PROJECT_ID> \
  --display-name "Workload Identity SA" \
  --quiet

# 2. 授予 GSA IAM 角色
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "<ROLE>" \
  --quiet

# 3. 创建 Kubernetes 服务账户 (KSA)
kubectl create namespace <NAMESPACE>
kubectl create serviceaccount <KSA_NAME> --namespace <NAMESPACE>

# 4. 将 KSA 绑定到 GSA
gcloud iam service-accounts add-iam-policy-binding \
  <GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:<PROJECT_ID>.svc.id.goog[<NAMESPACE>/<KSA_NAME>]" \
  --quiet

# 5. 为 KSA 添加注解
kubectl annotate serviceaccount <KSA_NAME> \
  --namespace <NAMESPACE> \
  iam.gke.io/gcp-service-account=<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com
```

> 参考 [assets/workload-identity-pod.yaml](./assets/workload-identity-pod.yaml)
> 获取测试 Pod。

### 验证

```bash
kubectl run workload-identity-test \
  --image=gcr.io/google.com/cloudsdktool/cloud-sdk:slim \
  --serviceaccount=<KSA_NAME> --namespace=<NAMESPACE> \
  --rm -it -- gcloud auth list --quiet
```

## Secret Manager 集成

黄金路径启用 Secret Manager 并进行自动轮换。密钥同步到 Kubernetes Secret。

```bash
# 验证集群上是否已启用 Secret Manager
gcloud container clusters describe <CLUSTER_NAME> --region <REGION> \
  --format="value(secretManagerConfig.enabled)" \
  --quiet

# 如果尚未启用（Day-1 变更）
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-secret-manager \
  --secret-manager-rotation-interval=120s \
  --quiet
```

### 通过 CSI 卷挂载密钥（部署示例）

启用 Secret Manager 插件后，工作负载可以使用 Secrets Store CSI 驱动将密钥作为卷挂载。这需要两个步骤：

1.  **定义 `SecretProviderClass`** 以指定从 Secret Manager 获取哪些密钥。
2.  **在 `Deployment` 中挂载卷** 并引用该类。

> [!IMPORTANT] **生产最佳实践**：始终使用生产标准的 **`Deployment`** 资源清单来演示工作负载集成（如 Secret Manager CSI），而不是原始的 `Pod` 资源清单。

#### 第 1 步：创建 SecretProviderClass

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: app-secrets-provider
  namespace: default
spec:
  provider: gke  # 指定 GKE 管理提供者
  parameters:
    secrets: |
      - resourceName: "projects/<PROJECT_ID>/secrets/db-password/versions/latest"
        fileName: "db-password.txt"
```

#### 第 2 步：在 Deployment 中挂载密钥

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
    spec:
      serviceAccountName: secure-ksa  # 必须绑定到具有 Secret Manager Secret Accessor 角色的 GSA
      containers:
      - name: app
        image: <IMAGE>
        volumeMounts:
        - name: secrets-volume
          mountPath: "/var/secrets"
          readOnly: true
      volumes:
      - name: secrets-volume
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "app-secrets-provider"
```

## RBAC 强化

黄金路径默认禁用不安全的旧版 RBAC 绑定，这些绑定授予对 `system:authenticated` 和 `system:unauthenticated` 组的广泛访问权限。

```bash
# 验证不安全绑定是否已禁用
gcloud container clusters describe <CLUSTER_NAME> --region <REGION> \
  --format="yaml(rbacBindingConfig)" \
  --quiet
```

**RBAC 最佳实践：**

-   使用命名空间范围的 Roles 而不是集群范围的 ClusterRoles
-   绑定到特定的 Groups 或 ServiceAccounts，切勿绑定到 `system:authenticated`
-   通过 MCP 审计权限：`check_k8s_auth(parent="...", verb="list",
    resourceType="pods", namespace="...")`（或 `kubectl auth can-i --list
    --as=<user>`)
-   通过 MCP 查看绑定：`get_k8s_resource(parent="...",
    resourceType="clusterrolebinding")`（或 `kubectl get
    clusterrolebindings,rolebindings --all-namespaces`）

> 参考 `gke-multitenancy` 技能进行企业 RBAC 规划和
> https://docs.cloud.google.com/kubernetes-engine/docs/best-practices/rbac.md.txt

## 二进制授权

黄金路径默认不启用，但建议用于生产镜像溯源：

```bash
# 启用 Binary Authorization
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE \
  --quiet
```

## 网络策略

Dataplane V2（黄金路径）提供内置的网络策略强制执行。每个命名空间应用默认拒绝策略：

```
# MCP（首选）
apply_k8s_manifest(parent="...", yamlManifest="<default-deny-netpol.yaml 的内容>")

# kubectl 备用方案
kubectl apply -f ./assets/default-deny-netpol.yaml -n <NAMESPACE>
```

## GKE Sandbox (gVisor)

用于在隔离沙盒中运行不受信任的工作负载：

```bash
# 在集群上启用（标准集群）
gcloud container clusters update <CLUSTER_NAME> --region <REGION> --enable-gke-sandbox --quiet

# 在 Pod 规范中使用
# 添加：runtimeClassName: gvisor
```

## Pod 安全标准（黄金路径）

Pod 安全标准定义了三个限制 Pod 能力的配置文件。**`restricted` 配置文件是生产命名空间的黄金路径默认值**。

| 配置文件      | 级别                 | 用例                           |
| ------------ | --------------------- | ---------------------------------- |
| `privileged` | 无限制          | 系统命名空间 (`kube-system`), |
:              :                       : 基础设施控制器         :
| `baseline`   | 最小限制          | 共享/开发命名空间，正在迁移的旧版应用 |
:              :                       :                           :
| `restricted` | **黄金路径**       | 生产工作负载 -- 阻止     |
:              :                       : 特权提升，主机访问， :
:              :                       : 根                               :

**通过命名空间标签（Pod 安全准入）强制执行：**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

**渐进式推出策略：**

1.  在现有命名空间上使用 `warn` + `audit` 以识别违规行为
2.  修复不符合要求的工作负载（移除 `privileged`，`hostNetwork`，根用户等）
3.  一旦所有工作负载都通过，启用 `enforce`

`restricted` 阻止：以根用户运行，特权提升，主机网络/PID/IPC，主机路径卷，以及大多数能力。黄金路径 `workload-identity-pod.yaml` 已经符合要求。

## 网络策略日志记录（推荐）

使用 Dataplane V2（黄金路径），您可以启用网络策略决策的日志记录。**不是黄金路径默认值** -- 推荐用于安全审计。

```bash
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-network-policy-logging \
  --quiet
```

这将记录允许和拒绝的连接，有助于排查网络策略规则和审计流量。

## 常见 IAM 角色

GKE 最常见的五个预定义 IAM 角色：

| 角色                            | 目的             | 使用场景          |
| ------------------------------- | ------------------- | -------------------- |
| `roles/container.admin`         | 对集群和 Kubernetes 资源进行完全控制 | 平台团队管理员     |
:                                 : 集群管理     :
:                                 : Kubernetes : 资源管理 :
:                                 :            :            :
| `roles/container.clusterAdmin`  | 管理集群但不管理 | 集群操作员    |
:                                 : 项目级 IAM  | 创建/删除集群     :
| `roles/container.developer`     | 部署工作负载    | 应用程序          |
:                                 : (Pod，服务，    | 开发者部署到现有集群 :
:                                 : 部署)        |                  :
| `roles/container.viewer`        | 对集群和 Kubernetes 资源进行只读访问 | 监控，          |
:                                 :            | 审计，或         :
:                                 :            | 只读仪表板         :
:                                 :            |                  :
| `roles/container.clusterViewer` | 列出和获取集群  | 需要集群元数据的 CI/CD 管道 |
:                                 : 细节        |                  :

> **最小权限原则**：从 `roles/container.viewer` 或 `roles/container.developer` 开始，并根据需要升级。避免广泛授予 `roles/container.admin`。

## 服务账户和代理

-   **GKE 服务代理**
    (`service-<PROJECT_NUMBER>@container-engine-robot.iam.gserviceaccount.com`):
    自动创建。代表您管理节点、网络和集群操作。不要删除或修改其权限。
-   **节点服务账户**：默认情况下，节点使用 Compute Engine 默认服务账户。对于生产环境，创建一个具有最小权限的专用 SA，并通过节点池配置分配它。
-   **工作负载身份**：Pod 访问 Google Cloud API 的推荐方式。将 Kubernetes ServiceAccount 映射到 Google IAM ServiceAccount — 参考 [工作负载身份设置](#workload-identity-federation)。

## 跨服务认证模式

授予 GKE 工作负载访问其他 Google Cloud 服务的常见模式：

```bash
# 授予 GKE 工作负载访问 Cloud Storage
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/storage.objectViewer" \
  --quiet

# 授予 GKE 工作负载访问 Cloud SQL
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/cloudsql.client" \
  --quiet

# 授予 GKE 工作负载访问 Pub/Sub
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/pubsub.subscriber" \
  --quiet
```

在所有情况下，GSA 必须通过工作负载身份绑定到 KSA（参考上述设置）。Pod 然后使用 KSA 作为 GSA 进行身份验证。
