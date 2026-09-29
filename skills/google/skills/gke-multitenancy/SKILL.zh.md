---
name: gke-multitenancy
description: 在 GKE 上规划和配置多租户。涵盖命名空间隔离、团队 RBAC 规划、资源配额、LimitRanges、网络隔离和成本分配。在设计和 GKE 多租户、配置 GKE 命名空间、设置资源配额或隔离 GKE 团队时使用。不适用于单租户集群配置或通用部署说明（请使用 gke-basics 或 gke-app-onboarding）。
---

# GKE 多租户

本指南涵盖 GKE 上的企业级多租户模式，包括命名空间隔离、RBAC 规划、资源配额和网络分段。

> **MCP 工具:** `apply_k8s_manifest`, `get_k8s_resource`, `check_k8s_auth`, `describe_k8s_resource`, `delete_k8s_resource`

## 使用场景

- 多个团队共享单个 GKE 集群
- 在单个集群内按环境（开发/预发布/生产）隔离工作负载
- 实施最小权限访问控制
- 跨团队或项目进行成本分摊

## 多租户模型

| 模型                         | 隔离程度    | 复杂度 | 成本           |
| ----------------------------- | ------------ | ---------- | -------------- |
| **每个团队一个命名空间**        | 软（RBAC + | 低        | 最低（共享    |
:                               : 网络策略）      :            : 集群）       :
:                               :              :            :                :
| **每个环境一个命名空间**        | 软         | 低        | 低            |
| **每个团队一个节点池**        | 中等       | 中等     | 中等         |
:                               : （专用计   :            :                :
:                               : 算力）     :            :                :
| **每个团队一个集群**          | 硬（完全   | 高       | 最高        |
:                               : 隔离）   :            :                :

> **推荐路径**: 从每个团队一个命名空间开始以实现成本效益。仅在合规性要求时才升级到更强的隔离。

## 命名空间隔离设置

### 1. 创建命名空间

```bash
kubectl create namespace team-a
kubectl create namespace team-b
kubectl label namespace team-a team=a
kubectl label namespace team-b team=b
```

### 2. RBAC 配置

**原则**: 每个命名空间授予最小权限。永远不要绑定到 `system:authenticated`。

```yaml
# 为团队创建命名空间范围的 Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: team-a-developer
  namespace: team-a
rules:
- apiGroups: ["", "apps", "batch"]
  resources: ["pods", "deployments", "services", "configmaps", "jobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-a-developers
  namespace: team-a
subjects:
- kind: Group
  name: "team-a@example.com"  # Google Group
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: team-a-developer
  apiGroup: rbac.authorization.k8s.io
```

**RBAC 最佳实践**: 使用 Google Groups 进行主体绑定。优先选择命名空间范围的 Roles 而非 ClusterRoles。参考 `gke-platform-security` 技能获取完整的 RBAC 强化指导。

### 3. 资源配额

防止任何单个团队消耗所有集群资源：

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    pods: "50"
    services: "10"
    persistentvolumeclaims: "10"
```

### 4. LimitRange

为每个容器设置默认和最大资源约束：

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: team-a-limits
  namespace: team-a
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "8Gi"
```

> [!IMPORTANT] **强制默认值**: 在 `LimitRange` 中定义 `min` 或 `max` 限制时，你必须同时定义相应的 `default` 和 `defaultRequest` 值。如果你只设置 `min` 或 `max` 而没有默认值，任何没有显式资源请求/限制的 Pod 都会被准入控制器拒绝。

### 5. 网络隔离

按命名空间应用默认拒绝策略（参考 `gke-workload-security` 技能），然后允许团队内部流量：

```yaml
# 允许同命名空间 Pod 通信 + DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: team-a
spec:
  podSelector: {}
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:  # 允许 DNS
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

## 成本分摊

### 用于成本归因的标签

```bash
# 为计费标签命名空间
kubectl label namespace team-a cost-center=engineering
kubectl label namespace team-b cost-center=data-science
```

### GKE 成本分摊

启用 GKE 成本分摊以按命名空间和标签分解成本：

```bash
gcloud container clusters update <CLUSTER_NAME> --region <REGION> \
  --enable-cost-allocation
```

在 Cloud Billing > GKE Cost Allocation 中查看。
