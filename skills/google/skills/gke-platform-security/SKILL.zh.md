---
name: gke-platform-security
description: 制定、配置和加固平台级 Google Kubernetes Engine (GKE) 集群安全。涵盖集群附加组件（启用密钥管理器）、RBAC 加固（禁用不安全绑定、审计工具）、二进制授权、启用受保护节点、GKE 沙盒集群启用、GKE IAM 角色，以及跨服务认证 IAM 模式。在以下情况下使用：保护集群控制平面、加固 GKE RBAC、启用受保护节点、启用 GKE 沙盒运行时、启用集群级安全附加组件或管理 GKE IAM 角色。不适用于工作负载级安全（工作负载身份、SecretProviderClass、PSS、NetPol、gVisor pod runtimeClassName；请使用 gke-workload-security）。
---

# GKE 平台安全

本指南涵盖 Google Kubernetes Engine (GKE) 的平台级安全加固和集群配置。关于工作负载级安全控制（如 Workload Identity Service Account 绑定、SecretProviderClass 卷挂载、网络策略和 Pod 安全标准），请参考 `gke-workload-security` 技能。

> **MCP 工具：** `gke:get_cluster`, `k8s:check_k8s_auth`, `k8s:get_k8s_resource`, `k8s:apply_k8s_manifest`, `gke:update_cluster`

## 黄金路径安全默认值

设置                                                        | 黄金路径值                       | Day-0/1 | 备注
-------------------------------------------------------------- | --------------------------------------- | ------- | -----
`workloadIdentityConfig.workloadPool`                          | `<PROJECT>.svc.id.goog`                 | Day-0   | 集群 Pod 的工作负载身份联合
`secretManagerConfig.enabled`                                  | `true`                                  | Day-1   | Google Secret Manager 集群插件集成
`secretManagerConfig.rotationConfig`                           | `enabled: true, rotationInterval: 120s` | Day-1   | 集群级别的自动密钥轮换
`rbacBindingConfig.enableInsecureBindingSystemAuthenticated`   | `false`                                 | Day-0   | 阻止旧的 `system:authenticated` 绑定
`rbacBindingConfig.enableInsecureBindingSystemUnauthenticated` | `false`                                 | Day-0   | 阻止旧的 `system:unauthenticated` 绑定
`nodeConfig.shieldedInstanceConfig.enableSecureBoot`           | `true`                                  | Day-0   | 可验证的启动完整性
`nodeConfig.shieldedInstanceConfig.enableIntegrityMonitoring`  | `true`                                  | Day-0   | 运行时完整性检查
`nodeConfig.workloadMetadataConfig.mode`                       | `GKE_METADATA`                          | Day-0   | 阻止旧的元数据 API，强制执行工作负载身份
私有集群 + Dataplane V2 设置                        | 参考的 `gke-networking` 技能          | Day-0   | 私有节点，私有端点强制执行，ADVANCED_DATAPATH

## Secret Manager 插件启用

黄金路径在集群级别启用 Secret Manager 并进行自动密钥轮换。

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

> **注意：** 关于配置 `SecretProviderClass` 声明式文件并在应用程序部署中挂载密钥为卷，请参考 `gke-workload-security` 技能。

## RBAC 加固

黄金路径禁用不安全的旧版 RBAC 绑定，这些绑定向 `system:authenticated` 和 `system:unauthenticated` 组提供广泛访问权限。

```bash
# 验证不安全的绑定是否已禁用
gcloud container clusters describe <CLUSTER_NAME> --region <REGION> \
  --format="yaml(rbacBindingConfig)" \
  --quiet
```

**RBAC 最佳实践：**

-   使用命名空间范围的 Roles 而不是集群范围的 ClusterRoles。
-   绑定到特定的 Groups 或 ServiceAccounts，永远不要绑定到 `system:authenticated` 或 `system:unauthenticated`。
-   通过 MCP 审计权限：`k8s:check_k8s_auth(parent="...", verb="list", resourceType="pods", namespace="...")`（或 `kubectl auth can-i --list --as=<user>`）。
-   通过 MCP 查看绑定：`k8s:get_k8s_resource(parent="...", resourceType="clusterrolebinding")`（或 `kubectl get clusterrolebindings,rolebindings --all-namespaces`）。

> 关于企业级 RBAC 规划，请参考 `gke-multitenancy` 技能和 https://docs.cloud.google.com/kubernetes-engine/docs/best-practices/rbac.md.txt

## 二进制授权

默认情况下黄金路径不启用，但建议在集群中强制执行生产镜像来源：

```bash
# 启用二进制授权
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE \
  --quiet
```

## Shielded Nodes & GKE Sandbox 启用

在集群级别启用可验证节点启动完整性和内核隔离功能：

```bash
# 在现有集群上启用 Shielded Nodes
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-shielded-nodes \
  --quiet

# 在现有集群上启用 GKE Sandbox (gVisor) 运行时
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-gke-sandbox \
  --quiet
```

> **注意：** 要在 gVisor Sandbox 内运行工作负载，请在 Pod 规范中指定 `runtimeClassName: gvisor`，具体请参考 `gke-workload-security` 技能。

## 常见 IAM 角色

GKE 平台和集群访问的五个最常见的预定义 IAM 角色：

| 角色                            | 目的             | 使用时机          |
| ------------------------------- | ------------------- | -------------------- |
| `roles/container.admin`         | 对集群和 Kubernetes 资源完全控制 | 平台团队管理员     |
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
| `roles/container.clusterAdmin`  | 管理集群但不管理 | 集群操作员    |
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
| `roles/container.developer`     | 部署工作负载    | 应用程序          |
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
| `roles/container.viewer`        | 对集群和 Kubernetes 资源只读访问 | 监控、          |
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
:                                 :                     :                  :
| `roles/container.clusterViewer` | 列出和获取集群详情 | 需要集群元数据的 CI/CD 管道 |

> **最小权限原则：** 从 `roles/container.viewer` 或 `roles/container.developer` 开始，并根据需要提升权限。避免在团队之间广泛授予 `roles/container.admin`。

## 服务账户和代理

-   **GKE 服务代理**
    (`service-<PROJECT_NUMBER>@container-engine-robot.iam.gserviceaccount.com`):
    自动创建。代表您管理节点、网络和集群操作。不要删除或修改其权限。
-   **节点服务账户**：默认情况下，节点使用 Compute Engine 默认服务账户。对于生产平台，创建一个具有最小必要权限（`roles/monitoring.metricWriter`, `roles/logging.logWriter`）的 Google Service Account，并在创建节点池时分配它。
-   **工作负载身份**：关于将 Google Service Accounts 绑定到 Kubernetes Service Accounts (`roles/iam.workloadIdentityUser`)，请参考 `gke-workload-security` 技能。

## 跨服务认证模式

用于在通过工作负载身份链接之前授予后端 Google Service Accounts (GSAs) 访问外部 Google Cloud 服务的前端项目级 IAM 策略绑定模式：

```bash
# 授予 GSA 访问 Cloud Storage 对象
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/storage.objectViewer" \
  --quiet

# 授予 GSA 访问 Cloud SQL 数据库
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/cloudsql.client" \
  --quiet

# 授予 GSA 访问 Pub/Sub 订阅
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:<GSA_NAME>@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/pubsub.subscriber" \
  --quiet

## 资源

- [GKE 集群加固指南](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster)
- [GKE RBAC 最佳实践](https://cloud.google.com/kubernetes-engine/docs/best-practices/rbac)
- [GKE Secret Manager 插件](https://cloud.google.com/secret-manager/docs/secret-manager-managed-csi-component)
- [GKE 二进制授权](https://cloud.google.com/binary-authorization/docs/setting-up)
- [Shielded GKE 节点](https://cloud.google.com/kubernetes-engine/docs/how-to/shielded-gke-nodes)
- [GKE Sandbox (gVisor)](https://cloud.google.com/kubernetes-engine/docs/how-to/sandbox-pods)
