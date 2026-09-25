# Kubernetes 专家

## 使用此技能的场景

- 部署工作负载（Deployments、StatefulSets、DaemonSets、Jobs）
- 配置网络（Services、Ingress、NetworkPolicies）
- 管理配置（ConfigMaps、Secrets、环境变量）
- 设置持久化存储（PV、PVC、StorageClasses）
- 创建 Helm 图表用于应用打包
- 排查集群和工作负载问题
- 实施安全最佳实践

## 核心工作流程

1. **分析需求** — 理解工作负载特性、扩展需求、安全要求
2. **设计架构** — 选择工作负载类型、网络模式、存储方案
3. **实现清单** — 创建声明式 YAML，包含正确的资源限制、健康检查
4. **安全配置** — 应用 RBAC、NetworkPolicies、Pod Security Standards、最小权限
5. **验证** — 运行 `kubectl rollout status`、`kubectl get pods -w` 和 `kubectl describe pod <name>` 确认健康状态；如有需要使用 `kubectl rollout undo` 回滚

## 参考资料

根据上下文加载详细指南：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 工作负载 | `references/workloads.md` | Deployments、StatefulSets、DaemonSets、Jobs、CronJobs |
| 网络 | `references/networking.md` | Services、Ingress、NetworkPolicies、DNS |
| 配置 | `references/configuration.md` | ConfigMaps、Secrets、环境变量 |
| 存储 | `references/storage.md` | PV、PVC、StorageClasses、CSI 驱动 |
| Helm 图表 | `references/helm-charts.md` | 图表结构、values、模板、钩子、测试、仓库 |
| 排查问题 | `references/troubleshooting.md` | kubectl debug、日志、事件、常见问题 |
| 自定义 Operator | `references/custom-operators.md` | CRD、Operator SDK、controller-runtime、reconciliation |
| 服务网格 | `references/service-mesh.md` | Istio、Linkerd、流量管理、mTLS、金丝雀发布 |
| GitOps | `references/gitops.md` | ArgoCD、Flux、渐进式交付、sealed secrets |
| 成本优化 | `references/cost-optimization.md` | VPA、HPA 调优、spot 实例、配额、资源适配 |
| 多集群 | `references/multi-cluster.md` | Cluster API、federation、跨集群网络、灾难恢复 |

## 约束条件

### 必须

- 使用声明式 YAML 清单（避免使用命令式 kubectl 命令）
- 为所有容器设置资源请求和限制
- 包含 liveness 和 readiness 探针
- 使用 secrets 存储敏感数据（绝不硬编码凭证）
- 应用最小权限 RBAC 权限
- 实施网络策略进行网络隔离
- 使用命名空间进行逻辑隔离
- 统一标记资源以方便组织
- 在注解中记录配置决策

### 禁止

- 未设置资源限制就部署到生产环境
- 在 ConfigMaps 或普通环境变量中存储 secrets
- 使用默认 ServiceAccount 部署应用 Pod
- 允许无限制网络访问（默认允许所有）
- 无正当理由以 root 用户运行容器
- 跳过健康检查（liveness/readiness probes）
- 使用最新标签部署生产镜像
- 暴露不必要的端口或服务

## 常用 YAML 模式

### 具有资源限制、探针和安全上下文的 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
  labels:
    app: my-app
    version: "1.2.3"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
        version: "1.2.3"
    spec:
      serviceAccountName: my-app-sa   # 绝不使用默认 ServiceAccount
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
        - name: my-app
          image: my-registry/my-app:1.2.3   # 绝不使用 latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          envFrom:
            - secretRef:
                name: my-app-secret   # 从 Secret 获取凭证，而非 ConfigMap
```

### 最小 RBAC（最小权限）

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]   # 只授予所需权限
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: my-namespace
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: my-namespace
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
```

### NetworkPolicy（默认拒绝+显式允许）

```yaml
# 默认拒绝所有入站和出站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: my-namespace
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
---
# 仅允许特定流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-my-app
  namespace: my-namespace
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

## 验证命令

部署后验证健康状态和安全配置：

```bash
# 观察滚动更新完成
kubectl rollout status deployment/my-app -n my-namespace

# 实时查看 Pod 事件以捕获崩溃循环或镜像拉取错误
kubectl get pods -n my-namespace -w

# 检查特定 Pod 的失败原因
kubectl describe pod <pod-name> -n my-namespace

# 查看容器日志
kubectl logs <pod-name> -n my-namespace --previous   # 对崩溃的容器使用 --previous

# 验证资源使用与限制对比
kubectl top pods -n my-namespace

# 审计 ServiceAccount 的 RBAC 权限
kubectl auth can-i --list --as=system:serviceaccount:my-namespace:my-app-sa

# 回滚失败的部署
kubectl rollout undo deployment/my-app -n my-namespace
```

## 输出模板

实施 Kubernetes 资源时需提供：
1. 完整的 YAML 清单，结构正确
2. 如有需要，提供 RBAC 配置（ServiceAccount、Role、RoleBinding）
3. 用于网络隔离的网络策略
4. 简要说明设计决策和安全考虑

[文档](https://jeffallan.github.io/claude-skills/skills/infrastructure/kubernetes-specialist/)
