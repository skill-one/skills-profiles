# GKE 基础知识 & 关键注意事项

Google Cloud 上的托管 Kubernetes 平台。默认为 Autopilot 模式，除非明确要求使用 Standard 模式。

## Autopilot 与 Standard 的关键选择规则

* **几乎所有工作负载都默认使用 Autopilot**。
* **仅当以下情况时使用 Standard**：
  * 需要 Custom node OS 内核参数 (`sysctl`)。
  * 需要 Custom node taints 或特定的硬件节点池。
  * DaemonSets 需要 raw `hostPath` 挂载到主机操作系统文件系统。
* 当解释为什么需要 Standard 而不是 Autopilot 时，必须明确引用所有匹配的限制（例如，自定义 sysctls 和自定义 node taints）。
* *对于高级集群架构或复杂的节点池创建规划，请参考 `gke-cluster-creation`。*

## 关键注意事项 & 最佳实践

1. **私有 Autopilot 集群**：
   * 使用 `--enable-private-nodes` 获取私有节点 IP 地址。
   * 使用 `--enable-private-endpoint` 禁止通过公共 IP 访问控制平面。
   * 使用 `--enable-master-authorized-networks` 和 `--master-authorized-networks=CIDR_BLOCK` 限制控制平面访问：
     ```bash
     gcloud container clusters create-auto CLUSTER_NAME --region=REGION \
       --enable-private-nodes \
       --enable-private-endpoint \
       --enable-master-authorized-networks \
       --master-authorized-networks=CIDR_BLOCK
     ```

2. **工作负载身份认证 (IAM 绑定)**：
   * 永远不要在 Pods 中挂载原始 GCP Service Account JSON 密钥。
   * 使用注释 Kubernetes ServiceAccount (`KSA`) 绑定到 Google Service Account (`GSA`)：
     ```yaml
     metadata:
       annotations:
         iam.gke.io/gcp-service-account: GSA_NAME@PROJECT_ID.iam.gserviceaccount.com
     ```

3. **Autopilot 资源请求**：
   * 在 Autopilot 中，CPU 请求必须以 250m（0.25 vCPU）的增量指定。如果请求不匹配的 CPU 请求（例如，300m），则向上舍入到最近的 250m 增量（500m / 0.5 vCPU）。
   * 资源请求等于资源限制。省略 `limits` 以允许 Autopilot 设置与 `requests` 匹配的默认值。

4. **集群凭证**：
   * 在获取凭证时始终明确指定 `--region`（对于区域集群）或 `--zone`（对于区域集群）：
     ```bash
     gcloud container clusters get-credentials CLUSTER_NAME --region=REGION --quiet
     ```

## 参考目录

-   [核心概念](references/core-concepts.md)：架构、集群模式（Autopilot 与 Standard）、网络、扩展和安全模型。

-   [CLI 使用 & 工具参考](references/cli-reference.md)：工具优先级层次（MCP vs gcloud vs kubectl）、`gcloud container` 命令和用户优先级覆盖。

-   [客户端库](references/client-library-usage.md)：Python、Go、Node.js 和 Java 中的官方 Kubernetes 和 Google Cloud 容器客户端库。

-   [MCP 使用](references/mcp-usage.md)：连接和使用 23 个结构化的 GKE MCP 工具进行集群管理、K8s 资源和诊断。

-   [基础设施即代码](references/iac-usage.md)：`google_container_cluster`（Autopilot）的 Terraform 示例、Kubernetes 提供者资源和 YAML 示例。
