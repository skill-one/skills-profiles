# Linkerd 模式

Linkerd 服务网格的运维模式 - Kubernetes 中轻量级、以安全为先的服务网格。

## 何时使用此技能

- 设置轻量级服务网格
- 实现自动 mTLS
- 配置金丝雀部署的流量拆分
- 为每条路由设置服务配置文件
- 实现重试和超时
- 多集群服务网格

## 核心概念

### 1. Linkerd 架构

```
┌─────────────────────────────────────────────┐
│                控制平面                 │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ destiny │ │ identity │ │ proxy-inject │ │
│  └─────────┘ └──────────┘ └──────────────┘ │
└─────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────┐
│                 数据平面                   │
│  ┌─────┐    ┌─────┐    ┌─────┐             │
│  │proxy│────│proxy│────│proxy│             │
│  └─────┘    └─────┘    └─────┘             │
│     │           │           │               │
│  ┌──┴──┐    ┌──┴──┐    ┌──┴──┐            │
│  │ app │    │ app │    │ app │            │
│  └─────┘    └─────┘    └─────┘            │
└─────────────────────────────────────────────┘
```

### 2. 关键资源

| 资源                | 目的                              |
| ----------------------- | ------------------------------------ |
| **ServiceProfile**      | 每条路由的指标、重试、超时        |
| **TrafficSplit**        | 金丝雀部署、A/B 测试              |
| **Server**              | 定义服务器端策略                  |
| **ServerAuthorization** | 访问控制策略                      |

## 模板

### 模板 1：网格安装

```bash
# 安装 CLI
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh

# 验证集群
linkerd check --pre

# 安装 CRDs
linkerd install --crds | kubectl apply -f -

# 安装控制平面
linkerd install | kubectl apply -f -

# 验证安装
linkerd check

# 安装 viz 扩展（可选）
linkerd viz install | kubectl apply -f -
```

### 模板 2：注入命名空间

```yaml
# 自动注入命名空间
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
  annotations:
    linkerd.io/inject: enabled
---
# 或注入特定部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    linkerd.io/inject: enabled
spec:
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
```

### 模板 3：带重试的服务配置文件

```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: my-service.my-namespace.svc.cluster.local
  namespace: my-namespace
spec:
  routes:
    - name: GET /api/users
      condition:
        method: GET
        pathRegex: /api/users
      responseClasses:
        - condition:
            status:
              min: 500
              max: 599
          isFailure: true
      isRetryable: true
    - name: POST /api/users
      condition:
        method: POST
        pathRegex: /api/users
      # POST 默认不重试
      isRetryable: false
    - name: GET /api/users/{id}
      condition:
        method: GET
        pathRegex: /api/users/[^/]+
      timeout: 5s
      isRetryable: true
  retryBudget:
    retryRatio: 0.2
    minRetriesPerSecond: 10
    ttl: 10s
```

### 模板 4：流量拆分（金丝雀）

```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: my-service-canary
  namespace: my-namespace
spec:
  service: my-service
  backends:
    - service: my-service-stable
      weight: 900m # 90%
    - service: my-service-canary
      weight: 100m # 10%
```

### 模板 5：服务器授权策略

```yaml
# 定义服务器
apiVersion: policy.linkerd.io/v1beta1
kind: Server
metadata:
  name: my-service-http
  namespace: my-namespace
spec:
  podSelector:
    matchLabels:
      app: my-service
  port: http
  proxyProtocol: HTTP/1
---
# 允许来自特定客户端的流量
apiVersion: policy.linkerd.io/v1beta1
kind: ServerAuthorization
metadata:
  name: allow-frontend
  namespace: my-namespace
spec:
  server:
    name: my-service-http
  client:
    meshTLS:
      serviceAccounts:
        - name: frontend
          namespace: my-namespace
---
# 允许未认证流量（例如来自 ingress）
apiVersion: policy.linkerd.io/v1beta1
kind: ServerAuthorization
metadata:
  name: allow-ingress
  namespace: my-namespace
spec:
  server:
    name: my-service-http
  client:
    unauthenticated: true
    networks:
      - cidr: 10.0.0.0/8
```

### 模板 6：高级路由的 HTTPRoute

```yaml
apiVersion: policy.linkerd.io/v1beta2
kind: HTTPRoute
metadata:
  name: my-route
  namespace: my-namespace
spec:
  parentRefs:
    - name: my-service
      kind: Service
      group: core
      port: 8080
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api/v2
        - headers:
            - name: x-api-version
              value: v2
      backendRefs:
        - name: my-service-v2
          port: 8080
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: my-service-v1
          port: 8080
```

### 模板 7：多集群设置

```bash
# 在每个集群上，使用集群凭证安装
linkerd multicluster install | kubectl apply -f -

# 链接集群
linkerd multicluster link --cluster-name west \
  --api-server-address https://west.example.com:6443 \
  | kubectl apply -f -

# 导出服务到其他集群
kubectl label svc/my-service mirror.linkerd.io/exported=true

# 验证跨集群连通性
linkerd multicluster check
linkerd multicluster gateways
```

## 监控命令

```bash
# 实时流量视图
linkerd viz top deploy/my-app

# 每条路由的指标
linkerd viz routes deploy/my-app

# 检查代理状态
linkerd viz stat deploy -n my-namespace

# 查看服务依赖关系
linkerd viz edges deploy -n my-namespace

# 仪表盘
linkerd viz dashboard
```

## 调试

```bash
# 检查注入状态
linkerd check --proxy -n my-namespace

# 查看代理日志
kubectl logs deploy/my-app -c linkerd-proxy

# 调试 identity/TLS
linkerd identity -n my-namespace

# 抽取流量（实时）
linkerd viz tap deploy/my-app --to deploy/my-backend
```

## 最佳实践

### 应该做

- **到处启用 mTLS** - Linkerd 会自动完成
- **使用 ServiceProfiles** - 获取每条路由的指标和重试
- **设置重试预算** - 防止重试风暴
- **监控黄金指标** - 成功率、延迟、吞吐量

### 不应该做

- **不要跳过检查** - 修改后始终运行 `linkerd check`
- **不要过度配置** - Linkerd 默认值很合理
- **不要忽略 ServiceProfiles** - 它们解锁高级功能
- **不要忘记超时** - 为每条路由设置适当的值
