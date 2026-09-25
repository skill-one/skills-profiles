# GKE黄金路径配置

黄金路径是生产集群推荐的Autopilot配置。它定义了合理的默认值——当用户请求不同的设置时，应用这些设置并注意相关的权衡。

> **MCP工具：** `get_cluster`、`create_cluster`、`update_cluster`

## 规则

1.  **默认采用黄金路径。** 除非用户另有要求，否则使用黄金路径值。当偏离时，注意权衡，但尊重用户的选择。
2.  **Day-0与Day-1。** 突出标记Day-0决策（网络、私有节点、子网、IP分配）——创建后很难或不可能更改。
3.  **工具偏好：MCP > gcloud > kubectl。** 优先使用MCP，因为它直接与GKE API交互并使用结构化数据，减少了shell语法错误和解析歧义。参见`gke-basics`技能的CLI参考，以获取完整的覆盖矩阵和覆盖选项。如果用户说“使用gcloud”或“使用kubectl”，请尊重本次会话的选择。
4.  **记录决策和理由**，特别是对于Day-0选择和黄金路径偏离。

## 必填输入

如果用户不确定，使用黄金路径默认值。

-   **项目ID**（必填）
-   **区域**（必填，例如`us-central1`）
-   **集群名称**（必填）
-   **环境类型**：开发/测试或生产（默认为生产）
-   **网络**：自带VPC/子网或自动创建（默认：自动创建）
-   **扩展预期**：预期的节点/ Pod数量、工作负载类型
-   **成本限制**：Spot VM容忍度、预算考虑

## 始终应用默认值

默认应用的最佳实践。如果用户请求不同的设置，应用它并简要说明安全或操作上的权衡。

设置                                                            | 黄金路径值
------------------------------------------------------------------ | -----------------
`autopilot.enabled`                                                | `true`
`privateClusterConfig.enablePrivateNodes`                          | `true`
`masterAuthorizedNetworksConfig.privateEndpointEnforcementEnabled` | `true`
`secretManagerConfig.enabled` + `rotationInterval: 120s`           | `true`
`rbacBindingConfig.enableInsecureBinding*`                         | `false`（两者）
`workloadIdentityConfig.workloadPool`                              | 启用
`networkConfig.datapathProvider`                                   | `ADVANCED_DATAPATH`
`networkConfig.dnsConfig.clusterDns`                               | `CLOUD_DNS`
`autoscaling.autoscalingProfile`                                   | `OPTIMIZE_UTILIZATION`
`verticalPodAutoscaling.enabled`                                   | `true`
`monitoringConfig` 组件                                          | SYSTEM_COMPONENTS、STORAGE、POD、DEPLOYMENT、STATEFULSET、DAEMONSET、HPA、JOBSET、CADVISOR、KUBELET、DCGM、APISERVER、SCHEDULER、CONTROLLER_MANAGER
`loggingConfig` 组件                                             | SYSTEM_COMPONENTS、WORKLOADS（默认启用）
`advancedDatapathObservabilityConfig.enableMetrics`                | `true`
`nodeConfig.shieldedInstanceConfig.enableSecureBoot`               | `true`
`nodeConfig.workloadMetadataConfig.mode`                           | `GKE_METADATA`
`nodeConfig.gcfsConfig.enabled` / `gvnic.enabled`                  | `true` / `true`
`addonsConfig.statefulHaConfig.enabled`                            | `true`
存储CSI驱动程序（Filestore、GCS FUSE、Parallelstore）           | 启用
Pod安全标准                                                     | 生产命名空间上的`restricted`

## 客户可配置设置

这些有黄金路径默认值，但客户可以提供有效理由进行偏离。**更改前请询问。**

设置                                  | 默认                             | 为什么偏离
---------------------------------------- | ----------------------------------- | -----------
`dnsEndpointConfig.allowExternalTraffic` | `true`                              | 如果集群仅从VPC内部访问，则限制
`autoIpamConfig` / `createSubnetwork`    | `true` / `true`                     | 客户已有预置VPC/子网
`maxPodsPerNode`                         | `48`                                | `110` 用于高Pod密度（成本更高CIDR空间）
`subnetwork`                             | 自动创建                        | 客户自带现有子网
维护排除窗口            | 配置（NO_MINOR_UPGRADES、1yr） | 客户特定调度
`nodeConfig.bootDisk.diskType`           | `pd-balanced`                       | `pd-ssd` 用于I/O密集型，`pd-standard` 用于成本
`nodeConfig.machineType`                 | `ek-standard-8`（Autopilot）         | 根据工作负载变化；使用ComputeClasses

## 安全防护措施

-   不要请求或输出密钥（令牌、密钥、服务账户JSON）。
-   通过MCP工具或`gcloud config get-value project`发现项目/集群上下文——不要要求用户粘贴项目ID。
-   对于Day-0决策，在继续之前始终询问澄清问题。
-   对于Day-1功能，提出黄金路径默认值并说明权衡，然后让客户确认。
-   不要承诺零停机时间；建议使用PDB、健康探针、副本和分阶段升级。
-   在审计现有集群时，与黄金路径进行比较，并报告偏差的严重性和修复措施。

## 黄金路径配置

参见[golden-path-autopilot.yaml](./assets/golden-path-autopilot.yaml)以获取完整的集群级策略设置。
