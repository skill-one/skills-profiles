# GKE 工作负载安全

本技能提供有关保护 GKE 工作负载的流程和最佳实践。它涵盖了安全审计、身份和访问管理（工作负载身份）、网络安全（网络策略）和节点安全。

## 流程

### 1. 安全审计

使用提供的审计脚本评估您集群的当前安全状况。

**前提条件：**

-   `gcloud` 命令行界面已进行身份验证。
-   已安装 `jq` 命令行 JSON 处理器。

**功能：**

-   检查工作负载身份。
-   验证网络策略是否已启用。
-   检查是否启用 Shielded Nodes。
-   检查是否启用 Binary Authorization。
-   检查私有集群配置。

**命令：**

```bash
scripts/audit_cluster.sh <cluster-name> <region> <project-id>
```

### 2. 配置工作负载身份

工作负载身份允许 Kubernetes Service Accounts (KSAs) 伪装 Google Service Accounts (GSAs)。这是工作负载访问 Google Cloud API 的推荐方法。

**步骤：**

1.  **创建命名空间和 KSA：**

    ```bash
    kubectl create namespace workload-identity-test-ns
    kubectl create serviceaccount <ksa-name> \
        --namespace workload-identity-test-ns
    ```

2.  **将 KSA 绑定到 GSA：**

    ```bash
    gcloud iam service-accounts add-iam-policy-binding <gsa-name>@<project-id>.iam.gserviceaccount.com \
        --role roles/iam.workloadIdentityUser \
        --member "serviceAccount:<project-id>.svc.id.goog[workload-identity-test-ns/<ksa-name>]"
    ```

3.  **为 KSA 添加注释：**

    ```bash
    kubectl annotate serviceaccount <ksa-name> \
        --namespace workload-identity-test-ns \
        iam.gke.io/gcp-service-account=<gsa-name>@<project-id>.iam.gserviceaccount.com
    ```

4.  **验证示例 Pod：** 使用现有资源 `assets/workload-identity-pod.yaml` 测试配置。首先更新文件中的 `<ksa-name>`。

    ```bash
    kubectl apply -f assets/workload-identity-pod.yaml -n workload-identity-test-ns
    ```

### 3. 实施 Network Policies

使用 Network Policies 控制 Pod 之间的流量。默认情况下，允许所有流量。

**启用 Network Policy 强制执行：**

```bash
gcloud container clusters update <cluster-name> \
    --update-addons=NetworkPolicy=ENABLED \
    --region <region>
```

> [!NOTE] 如果您的集群使用 Dataplane V2 (`--enable-dataplane-v2`)，则 Network Policy 强制执行是内置的，此步骤不是必需的（并且可能会失败）。

**应用默认拒绝策略：** 通过默认拒绝所有入站和出站流量来隔离命名空间。

**将 `<target-namespace>` 替换为您要隔离的命名空间。**

```bash
kubectl apply -f assets/default-deny-netpol.yaml -n <target-namespace>
```

### 4. GKE Sandbox (gVisor) Pod 隔离

在沙盒中运行不受信任的工作负载，以实现额外的内核隔离。*(注意：在集群控制平面级别启用 Shielded Nodes (`--enable-shielded-nodes`) 和 GKE Sandbox (`--enable-gke-sandbox`) 是平台级别的操作，涵盖在 `gke-platform-security` 技能中。)*

**运行沙盒 Pod：** 在 Pod 规范中添加 `runtimeClassName: gvisor`：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: app
    image: nginx
```

### 5. Pod 安全标准

使用标签在命名空间上强制执行安全策略。

**强制执行受限配置文件：**

```bash
kubectl label --overwrite ns <namespace> \
    pod-security.kubernetes.io/enforce=restricted \
    pod-security.kubernetes.io/enforce-version=latest
```

> [!NOTE] 使用 `latest` 可以确保您使用与集群当前版本对应的策略。您可以将其固定到特定版本（例如，`v1.30`），以将命名空间锁定到特定发布的策略。

### 6. Secret Manager 集成 (CSI 驱动)

将 Google Cloud Secret Manager 的密钥直接挂载为 Pod 中的卷。

**前提条件**：集群上必须启用 Secret Manager CSI 驱动。

**示例 SecretProviderClass：**

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: my-secret-provider
spec:
  provider: gcp
  parameters:
    secrets: |
      - resourceName: "projects/<project-id>/secrets/my-secret/versions/latest"
        fileName: "my-secret-file"
```

**示例 Pod 规范摘录：**

```yaml
spec:
  containers:
    - name: my-app
      volumeMounts:
        - name: secrets-store-inline
          mountPath: "/mnt/secrets"
          readOnly: true
  volumes:
    - name: secrets-store-inline
      csi:
        driver: secrets-store.csi.k8s.io
        readOnly: true
        volumeAttributes:
          secretProviderClass: "my-secret-provider"
```

### 7. 启用 Network Policy 日志记录

如果使用 GKE Dataplane V2，您可以记录允许和拒绝的连接。

**步骤：**

1.  配置 `NetworkLogging` 自定义资源。

**示例 NetworkLogging 资源清单：**

```yaml
apiVersion: networking.gke.io/v1alpha1
kind: NetworkLogging
metadata:
  name: default
spec:
  cluster:
    allow:
      log: true
      delegate: true
    deny:
      log: true
      delegate: true
```

这将将连接详细信息记录到 Cloud Logging。

## 最佳实践

1.  **最小权限：** 始终使用具有最小 IAM 角色的工作负载身份。避免使用节点默认服务账户。
2.  **网络隔离：** 使用 Network Policies 限制 Pod 之间的通信。启用 Network Policy 日志记录以实现可见性。
3.  **镜像安全：** 使用 Binary Authorization 确保仅部署受信任的镜像。
4.  **密钥管理**：使用 Secret Manager CSI 驱动而不是默认的 Kubernetes 密钥来管理敏感数据。
5.  **Pod 安全**：在所有非系统命名空间上强制执行 `baseline` 或 `restricted` Pod 安全标准。
6.  **策略强制执行**：考虑使用 **Policy Controller**（Gatekeeper）跨集群强制执行自定义安全性和合规性策略。

## 资源

-   [GKE 工作负载身份联合](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
-   [GKE 网络策略](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy)
-   [GKE 中的 Pod 安全标准](https://cloud.google.com/kubernetes-engine/docs/how-to/podsecurityadmission)
-   [Google Secret Manager CSI 驱动](https://cloud.google.com/secret-manager/docs/secret-manager-managed-csi-component)
-   [GKE Dataplane V2 网络日志记录](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy-logging)
