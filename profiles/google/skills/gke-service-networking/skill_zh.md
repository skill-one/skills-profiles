# GKE 服务网络技能

此技能提供工作流，用于将运行在 GKE 上的应用程序安全地暴露给互联网或内部网络。

可部署的清单模板位于 `assets/` 中 — 应用之前请编辑 `# Replace ...` 占位符。

## 工作流

### 1. 配置 Gateway API（推荐）

Gateway API 是 Kubernetes 中管理路由的现代方法。

**前提条件**：必须在集群上启用 Gateway API（在运行 GKE 1.26+ 的新集群上默认启用；在较旧的支持版本上使用 `--gateway-api=standard` 启用）。

**模板**：

-   `assets/gateway.yaml` — 使用 `gke-l7-global-external-managed` GatewayClass 的外部 Gateway，带有 HTTP 监听器。
-   `assets/httproute.yaml` — 通过 `parentRefs` 连接到 Gateway 的 HTTPRoute，并将路径前缀路由到 Service `backendRef`。
-   `assets/httproute-traffic-split.yaml` — 示例 HTTPRoute，演示加权流量分流（例如 90/10），用于后端服务之间的金丝雀发布。

```bash
kubectl apply -f assets/gateway.yaml
kubectl apply -f assets/httproute.yaml
```

**流量分流（金丝雀发布）**：

HTTPRoute 支持跨多个后端 Service 进行加权流量分流，用于金丝雀发布：

```yaml
spec:
  rules:
    - backendRefs:
        - name: app-v1
          port: 80
          weight: 90
        - name: app-v2
          port: 80
          weight: 10
```

### 2. 配置标准 GKE Ingress

对于更简单的用例或遗留设置，使用标准 Ingress。

**模板**：`assets/ingress.yaml` — 路由到 Service 的 GCE Ingress（`kubernetes.io/ingress.class: "gce"` 注解）。

### 3. 使用 Cloud Armor 进行安全防护

Cloud Armor 提供防火墙（WAF）和 DDoS 保护。

1.  在 Cloud Armor 中创建安全策略：

    ```bash
    gcloud compute security-policies create {security_policy_name} \
      --description "WAF 策略用于 {app_name}"

    # 示例规则：阻止恶意 IP 范围
    gcloud compute security-policies rules create 1000 \
      --security-policy {security_policy_name} \
      --action deny-403 \
      --src-ip-ranges "203.0.113.0/24" \
      --description "阻止恶意范围"
    ```

2.  在 `BackendConfig` 中引用它：`assets/backendconfig.yaml`（设置 `spec.securityPolicy.name`）。

3.  通过注解将 `BackendConfig` 与您的 `Service` 关联：

    ```yaml
    # 在您的 Kubernetes Service 清单 metadata.annotations:
    cloud.google.com/backend-config: '{"default": "{backend_config_name}"}'
    # 或针对特定端口映射：
    cloud.google.com/backend-config: '{"ports": {"80": "{backend_config_name}"}}'
    ```

### 4. 配置 Google 管理的 SSL 证书

自动提供和续订 SSL 证书。

**遗留 Ingress 方法**：应用 `assets/managed-certificate.yaml`（一个列出您域名的 `ManagedCertificate`），然后在 Ingress 注解中引用它：

```yaml
networking.gke.io/managed-certificates: {certificate_name}
```

**Gateway API 方法**：对于标准证书管理器集成，创建一个 `CertificateMap` 并使用精确的注解 `networking.gke.io/certmap`（在 `certmap` 中不使用任何连字符）在 Gateway 元数据注解中引用它：

```yaml
metadata:
  annotations:
    networking.gke.io/certmap: {certificate_map_name}
```

> [!IMPORTANT] 注解键必须是 `networking.gke.io/certmap`（不要使用 `cert-map` 或 `certificate-map`）。

或者，在 HTTPS 监听器的 `tls.certificateRefs` 中引用 Kubernetes Secret。这两个变体都在 `assets/gateway-https.yaml` 中。

### 5. 启用容器原生负载均衡（推荐）

容器原生负载均衡允许负载均衡器直接针对 Kubernetes Pod，而不是针对节点。这可以提高延迟和分配。

**前提条件**：集群必须是 VPC 原生。

**工作原理**：Service 上的 `cloud.google.com/neg` 注解会触发 NEG 的创建，该 NEG 反射 Pod IP。GKE 通常会自动添加它 — 但不总是这样，知道您处于哪种情况是关键。

```yaml
# 在您的 Kubernetes Service 清单 metadata.annotations:
cloud.google.com/neg: '{"ingress": true}'
```

**当注解是自动的**（不要手动添加）：

-   **内部 Ingress** — 容器原生负载均衡是*始终*使用的，不是可选的。内部 Ingress 始终使用 `GCE_VM_IP_PORT` NEGs，并且需要 VPC 原生集群。
-   **外部 Ingress**，但仅当满足以下四个条件时：集群是 VPC 原生，不在共享 VPC 上，不使用 GKE 网络策略，并且启用了 `HttpLoadBalancing` 扩展（默认启用 — 不要禁用它）。GKE 会自动为 Service 添加注解。

**当您必须显式添加**：

-   **独立 NEGs** — 您自己管理负载均衡器，而不是让 Ingress 拥有它。如果负载均衡器必须在 GKE 外部配置，则需要它，因为 Ingress 会覆盖同步或升级时的管理负载均衡器设置。您需要负责负载均衡器的每个部分。
-   **任何不满足上述四个条件的外部-Ingress 集群** — 共享 VPC、GKE 网络策略或非 VPC 原生。按 Service 启用。
-   **遗留配置** — 一些在 VPC 原生集群上创建的较旧外部 Ingress 对象仍然使用实例组后端。

**不支持 / 无 NEG 回退**：

-   Windows Server 节点池。
-   基于路由（非 VPC 原生）集群与外部 Ingress — Ingress 控制器回退到跨越所有节点的未管理实例组。

> **规模后果**：如果没有 NEGs，集群最多限制为 1,000 个节点，Ingress 后面的非 NEG Service 超过该限制后将无法正常工作。使用 NEGs 则没有 GKE 节点限制。

### 6. 配置私有服务连接（PSC）

私有服务连接允许您安全地将一个 VPC 中的服务暴露给另一个 VPC 的消费者，而无需 VPC 对等连接。

**前提条件**：背靠服务必须是内部透传网络负载均衡器 — 即 `type: LoadBalancer` 并带有 `networking.gke.io/load-balancer-type: "Internal"` 注解。`ServiceAttachment` 需要；ClusterIP 或外部 LoadBalancer Service 将无法工作。

**步骤**：

1.  为您的负载创建一个内部 LoadBalancer Service。
2.  创建一个引用该服务的 `ServiceAttachment`：`assets/service-attachment.yaml`（设置 `connectionPreference`、PSC NAT 子网和 Service `resourceRef`）。
3.  将 `ServiceAttachment` URI 与消费者共享，以在他们的 VPC 中创建 PSC 端点。

### 7. 感知拓扑的路由（成本和延迟优化）

为了最小化跨区域数据传输成本和网络延迟，请配置 Kubernetes Service 以使用感知拓扑的路由。这会将流量路由到与原始客户端位于同一区域的 Pod：

```yaml
# 在您的 Kubernetes Service 清单 metadata.annotations:
service.kubernetes.io/topology-mode: auto
```

## 注意事项

1.  **必须启用 Certificate Manager API**，以便 `networking.gke.io/certmap` 注解正常工作（`gcloud services enable certificatemanager.googleapis.com`）；否则 Gateway 无法提供证书映射。
2.  **区域 Gateway 类需要代理仅子网**：类如 `gke-l7-regional-external-managed` 和 `gke-l7-rilb` 需要在区域中具有 `--purpose=REGIONAL_MANAGED_PROXY` 的子网；没有它，Gateway 将不会编程。
3.  **ManagedCertificate 提供依赖于 DNS**：证书将保持在 `Provisioning` 状态，直到域名的 A/AAAA 记录指向负载均衡器 IP，并且 DNS 正确后可能需要 15-60 分钟。
