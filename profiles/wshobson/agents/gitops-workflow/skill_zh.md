# GitOps 工作流

使用 ArgoCD 和 Flux 实现自动化 Kubernetes 部署的 GitOps 工作流完整指南。

## 目的

使用 ArgoCD 或 Flux CD，遵循 OpenGitOps 原则，为 Kubernetes 实现声明式、基于 Git 的持续交付。

## 何时使用此技能

- 为 Kubernetes 集群设置 GitOps
- 从 Git 自动化应用部署
- 实施渐进式交付策略
- 管理多集群部署
- 配置自动同步策略
- 在 GitOps 中设置密钥管理

## OpenGitOps 原则

1. **声明式** - 整个系统以声明式方式描述
2. **版本化且不可变** - 期望状态存储在 Git 中
3. **自动拉取** - 软件代理自动拉取期望状态
4. **持续协调** - 代理协调实际状态与期望状态

## ArgoCD 设置

### 1. 安装

```bash
# 创建命名空间
kubectl create namespace argocd

# 安装 ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 获取管理员密码
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**参考:** 详细设置请参阅 `references/argocd-setup.md`

### 2. 仓库结构

```
gitops-repo/
├── apps/
│   ├── production/
│   │   ├── app1/
│   │   │   ├── kustomization.yaml
│   │   │   └── deployment.yaml
│   │   └── app2/
│   └── staging/
├── infrastructure/
│   ├── ingress-nginx/
│   ├── cert-manager/
│   └── monitoring/
└── argocd/
    ├── applications/
    └── projects/
```

### 3. 创建应用

```yaml
# argocd/applications/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: apps/production/my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 4. App of Apps 模式

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: applications
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: argocd/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {}
```

## Flux CD 设置

### 1. 安装

```bash
# 安装 Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# 初始化 Flux
flux bootstrap github \
  --owner=org \
  --repository=gitops-repo \
  --branch=main \
  --path=clusters/production \
  --personal
```

### 2. 创建 GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/my-app
  ref:
    branch: main
```

### 3. 创建 Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./deploy
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
```

## 同步策略

### 自动同步配置

**ArgoCD:**

```yaml
syncPolicy:
  automated:
    prune: true # 删除 Git 中不存在的资源
    selfHeal: true # 协调手动更改
    allowEmpty: false
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

**Flux:**

```yaml
spec:
  interval: 1m
  prune: true
  wait: true
  timeout: 5m
```

**参考:** 请参阅 `references/sync-policies.md`

## 渐进式交付

### 使用 ArgoCD Rollouts 进行金丝雀发布

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: { duration: 1m }
        - setWeight: 50
        - pause: { duration: 2m }
        - setWeight: 100
```

### 蓝绿发布

```yaml
strategy:
  blueGreen:
    activeService: my-app
    previewService: my-app-preview
    autoPromotionEnabled: false
```

## 密钥管理

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/password
```

### Sealed Secrets

```bash
# 加密密钥
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 将 sealed-secret.yaml 提交到 Git
```

## 最佳实践

1. **为不同环境使用单独的仓库或分支**
2. **为 Git 仓库实现 RBAC**
3. **启用同步失败的通知**
4. **为自定义资源使用健康检查**
5. **为生产环境实现审批门禁**
6. **将密钥移出 Git**（使用 External Secrets）
7. **使用 App of Apps 模式进行组织**
8. **为回滚标记发布**
9. **使用警报监控同步状态**
10. **先在 staging 环境测试更改**

## 故障排除

**同步失败:**

```bash
argocd app get my-app
argocd app sync my-app --prune
```

**不同步状态:**

```bash
argocd app diff my-app
argocd app sync my-app --force
```

## 相关技能

- `k8s-manifest-generator` - 用于创建清单
- `helm-chart-scaffolding` - 用于打包应用
