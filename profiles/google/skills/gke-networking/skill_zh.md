# GKE 网络配置

本指南涵盖 GKE 集群的网络配置。黄金路径要求使用 Dataplane V2 的私有 VPC 本地集群。

> **MCP 工具:** `get_cluster`, `update_cluster`, `apply_k8s_manifest`, `get_k8s_resource`

## 黄金路径网络默认值

设置                                                              | 黄金路径值                  | Day-0/1 | 备注
-------------------------------------------------------------------- | ---------------------------------- | ------- | -----
`privateClusterConfig.enablePrivateNodes`                            | `true`                             | Day-0   | 节点没有公网 IP
`masterAuthorizedNetworksConfig.privateEndpointEnforcementEnabled`   | `true`                             | Day-0   | 控制平面仅可通过私有端点或 DNS 访问
`controlPlaneEndpointsConfig.dnsEndpointConfig.allowExternalTraffic` | `true`                             | Day-0   | 允许基于 DNS 的 VPC 外部访问
`networkConfig.datapathProvider`                                     | `ADVANCED_DATAPATH` (Dataplane V2) | Day-0   | 基于 eBPF 的内置网络策略
`networkConfig.dnsConfig.clusterDns`                                 | `CLOUD_DNS`                        | Day-0   | 管理式 DNS，比 kube-dns 更可靠
`networkConfig.enableIntraNodeVisibility`                            | `true`                             | Day-1   | VPC 流量日志用于节点内部流量
`ipAllocationPolicy.autoIpamConfig.enabled`                          | `true`                             | Day-0   | 自动 IP 范围管理
`ipAllocationPolicy.createSubnetwork`                                | `true`                             | Day-0   | 自动创建专用子网
`defaultMaxPodsConstraint.maxPodsPerNode`                            | `48`                               | Day-0   | 保守默认值；高密度为 110

## 私有集群访问模式

黄金路径创建私有集群。用户通过以下方式访问：

1.  **DNS 端点（默认）**: `allowExternalTraffic: true` 允许从 VPC 外部通过集群的 DNS 端点访问。无需 VPN。
2.  **私有端点**: 直接从 VPC 内部访问，或通过 Cloud VPN/Interconnect 访问。
3.  **授权网络**: 向 `masterAuthorizedNetworksConfig` 添加特定 CIDR 进行基于 IP 的访问控制。

```bash
# 通过 DNS 端点访问私有集群（黄金路径默认）
gcloud container clusters get-credentials {cluster_name} \
  --region {region} --dns-endpoint \
  --quiet

# 通过私有端点访问（从 VPC 内部）
gcloud container clusters get-credentials {cluster_name} \
  --region {region} --internal-ip \
  --quiet
```

## 带入自己的 VPC/子网

如果客户有现有的网络基础设施：

```bash
gcloud container clusters create-auto {cluster_name} \
  --region {region} \
  --network {vpc_name} \
  --subnetwork {subnet_name} \
  --cluster-secondary-range-name {pod_range} \
  --services-secondary-range-name {svc_range} \
  --enable-private-nodes \
  --enable-master-authorized-networks \
  --quiet
```

> **Day-0 警告**: 创建集群后，VPC、子网和 IP 范围无法更改。

## VPC 本地模式优势

VPC 本地集群使用 GCP 翻译 IP 范围原生路由流量。关键优势包括：

1.  **可扩展性**: 流量在 VPC 内原生路由，无需自定义路由，避免自定义路由限制瓶颈。
2.  **直接 VPC 集成**: 跨 GCP 网络直接资源集成，无需复杂的桥接或路由隧道。
3.  **避免 IP 空耗**: 支持不连续 IP 范围并优化分配，降低子网 IP 范围空耗风险。

## IP 规划

| 资源      | 黄金路径  | 备注                                      |
| ------------- | ------------ | ------------------------------------------ |
| Pod CIDR      | `/17` (自动) | ~32K Pod IP；基于 `maxPodsPerNode` 大小 |
| Service CIDR  | `/20` (自动) | ~4K Service IP                            |
| Node 子网   | 自动创建   | 推荐 /20 以支持扩展                     |
| 每节点最大 Pod | 48           | 每个节点获得一个 /25 Pod 范围；设为 110 |
:               :              : 每节点 /24                           :

**Pod CIDR 规模估算规则**:

-   `maxPodsPerNode=48` -> 每个节点使用 Pod CIDR 的 `/25` (128 IP)
-   `maxPodsPerNode=110` -> 每个节点使用 Pod CIDR 的 `/24` (256 IP)
-   更大的 `maxPodsPerNode` = 更少的节点能容纳在给定 CIDR 内

## 出站流量

-   默认：节点使用 Cloud NAT 进行出站互联网访问（私有节点没有公网 IP），允许私有节点访问互联网而不暴露公网 IP。
-   静态出站 IP：配置 Cloud NAT 手动 IP 分配，以维持一致源 IP 用于外部允许列表或合作伙伴防火墙。
-   限制出站流量：通过自定义路由将流量路由到防火墙设备，根据组织安全策略检查和过滤出站流量。

## 网络策略

Dataplane V2（黄金路径）提供内置网络策略强制执行 — 无需额外插件。按命名空间应用默认拒绝策略，然后允许特定流量。

> 参考的 `gke-workload-security` 技能了解默认拒绝策略，参考 `gke-multitenancy` 技能了解按团队允许策略。
