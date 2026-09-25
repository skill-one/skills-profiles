# Azure Kubernetes Service

> **权威指导 — 强制合规**
>
> 该技能根据用户需求生成**推荐的 AKS 集群配置**，区分**Day-0 决策**（网络、API 服务器——后期难以更改）与**Day-1 功能**（可创建后启用）。有关命令，请参阅 [CLI 参考](./references/cli-reference.md)。

## 快速参考
| 属性 | 值 |
|----------|-------|
| 最佳用途 | AKS 集群规划及 Day-0 决策 |
| MCP 工具 | `mcp_azure_mcp_aks` |
| CLI | `az aks create`, `az aks show`, `kubectl get`, `kubectl describe` |
| 相关技能 | azure-kubernetes-app-deploy (将应用部署到现有集群), azure-diagnostics (故障排除 AKS), azure-validate (就绪检查), azure-kubernetes-automatic-readiness (将现有集群迁移到 AKS 自动) |

## 何时使用此技能
当用户需要执行以下操作时，请激活此技能：
- 创建新的 AKS 集群
- 规划用于生产工作负载的 AKS 集群配置
- 设计 AKS 网络架构（API 服务器访问、Pod IP 模型、出站流量）
- 设置 AKS 身份和密钥管理
- 配置 AKS 治理（Azure Policy、部署安全保护）
- 启用 AKS 可观测性（容器洞察、托管 Prometheus、Grafana）
- 定义 AKS 升级和补丁策略
- 了解 AKS 自动与标准 SKU 的差异
- 获取 AKS 集群设置和配置的 Day-0 检查清单

> **要将应用部署到现有集群？** 此技能负责创建和配置*集群*。若要将应用容器化并部署到已存在的集群（Dockerfile + 配置清单 + 部署安全保护），请改用 `azure-kubernetes-app-deploy` 子技能。

## 规则
1. 从用户对计算、网络、安全和其他设置的配置需求开始。
2. 使用 `azure` MCP 服务器并首先选择 `mcp_azure_mcp_aks`，以发现客户端暴露的特定于 AKS 的 MCP 工具。选择符合任务的最小 AKS 工具，仅在所需功能未通过 AKS MCP 表面暴露时才回退到 Azure CLI (`az aks`)。
3. 根据用户对控制的需求与便利性的权衡，确定 AKS 自动或标准 SKU 更为合适。除非需要特定自定义，否则默认选择 AKS 自动。
4. 记录集群配置决策及其理由，特别是对于难以后期更改的 Day-0 决策（网络、API 服务器访问）。

## 必需输入（仅询问所需内容）
如果用户不确定，请使用安全默认值。
- AKS 环境类型：开发/测试或生产
- 区域、可用性区域、首选节点 VM 大小
- 预期规模（节点/集群数量、工作负载大小）
- 网络需求（API 服务器访问、Pod IP 模型、入站/出站流量控制）
- 安全和身份需求，包括镜像注册表
- 升级和可观测性偏好
- 成本限制

## 工作流

### 1. 集群类型
- **AKS 自动**（默认）：适用于大多数生产工作负载，提供经过筛选的最佳实践配置，涵盖安全、可靠性和性能。除非您有特定自定义需求（如网络、自动扩展或节点池配置），否则请使用此选项。
- **AKS 标准**：如果您需要完全控制环境配置，则需要额外的开销来设置和管理。

### 2. 网络（Pod IP、出站流量、入站流量、数据平面）

**Pod IP 模型**（关键的 Day-0 决策）：
- **Azure CNI Overlay**（推荐）：Pod IP 来自私有覆盖范围，非 VNet 可路由，可扩展到大型环境，适用于大多数工作负载
- **Azure CNI (VNet 可路由)**：Pod IP 直接来自 VNet（Pod 子网或节点子网），当 Pod 必须从 VNet 或本地环境直接访问时使用
  - 文档：https://learn.microsoft.com/azure/aks/azure-cni-overlay

**数据平面和网络策略**：
- **由 Cilium 驱动的 Azure CNI**（推荐）：基于 eBPF 的高性能数据包处理、网络策略和可观测性

**出站流量**：
- **静态出站网关**：用于稳定、可预测的出站 IP
- 对于受限出站流量：UDR + Azure Firewall 或 NVA

**入站流量**：
- **使用 Gateway API 的 App Routing 插件**——推荐默认用于 HTTP/HTTPS 工作负载
- **使用 Gateway API 的 Istio 服务网格**——用于高级流量管理、mTLS、金丝雀发布
- **容器应用网关**——用于 L7 负载均衡与 WAF 集成

**DNS**：
- 在所有节点池上启用 **LocalDNS** 以实现可靠、高性能的 DNS 解析

### 3. 安全
- 在所有地方使用 **Microsoft Entra ID**（控制平面、Pod 的 Workload Identity、节点访问）。避免静态凭证。
- 通过 **Secrets Store CSI Driver** 使用 Azure Key Vault 存储密钥
- 启用 **Azure Policy** + **部署安全保护**
- 启用 **静态加密**（etcd/API 服务器）；**传输中加密**（节点间）
- 仅允许签名、经策略批准的镜像（Azure Policy + Ratify），优先使用 **Azure 容器注册表**
- **隔离**：使用命名空间、网络策略、范围日志记录

### 4. 可观测性
- 使用 Managed Prometheus 和 Container Insights 配合 Grafana 实现 AKS 可观测性（日志 + 指标）。
- 启用诊断设置，将控制平面日志和审计日志收集到 Log Analytics 工作区，用于安全监控和故障排除。
- 对于其他监控和故障排除工具，使用 Agentic CLI for AKS、Application Insights、资源健康中心、AppLens 检测器和 Azure Advisors 等功能。

### 5. 升级和补丁
- 配置 **维护窗口** 以控制升级时间
- 启用 **自动升级** 以确保控制平面和节点 OS 及时更新安全补丁和 Kubernetes 版本
- 考虑 **LTS 版本** 以实现企业级稳定性（2 年支持），通过将 AKS 环境升级到 Premium 级别
- **集群升级**：使用 **AKS Fleet Manager** 在测试到生产环境中进行分阶段发布

### 6. 性能
- 使用 **临时 OS 磁盘** (`--node-osdisk-type Ephemeral`) 以实现更快的节点启动
- 选择 **Azure Linux** 作为节点 OS（更小的占用空间，更快的启动速度）
- 启用 **KEDA** 以实现 HPA 之外的事件驱动自动扩展

### 7. 节点池和计算
- **专用系统节点池**：至少 2 个节点，仅用于系统工作负载（`CriticalAddonsOnly`）
- 在所有池上启用 **节点自动配置 (NAP)** 以节省成本和响应式扩展
- 使用 **最新代 SKU (v5/v6)** 以实现主机级优化
- **避免 B 系列 VM**——突发型 SKU 会导致性能/可靠性问题
- 使用至少具有 **4 个 vCPU** 的 SKU 以实现生产工作负载
- 设置 **拓扑扩展约束** 以按 SLO 在主机/区域间分配 Pod

### 8. 可靠性
- 在 **3 个可用性区域** (`--zones 1 2 3`) 部署
- 使用 **标准层** 以实现区域冗余控制平面 + API 服务器 99.95% 的可用性
- 启用 **Microsoft Defender for Containers** 以实现运行时保护
- 为所有生产工作负载配置 **PodDisruptionBudgets**
- 使用 **拓扑扩展约束** 以确保 Pod 在故障域间分布

### 9. 成本控制
- 使用 **Spot 节点池** 以实现批处理/可中断工作负载（最高 90% 的节省）
- **停止/启动** 开发/测试集群：`az aks stop/start`
- 考虑 **保留实例** 或 **节省计划** 以实现稳定状态工作负载

**深入场景**——仅加载相关的参考文件：

| 场景 | 触发关键词 | 参考 |
|----------|-----------------|-----------|
| Pod 重新配置 | 过度配置的 Pod、CPU 请求、内存请求、重新配置工作负载 | [azure-aks-rightsizing.md](./references/azure-aks-rightsizing.md) |
| VPA 设置 | 垂直 Pod 自动扩展、VPA 建议、VPA 启用 | [azure-aks-vpa.md](./references/azure-aks-vpa.md) |
| 集群自动扩展 | 空闲节点、CAS 关闭、启用自动扩展、缩减配置、节点利用率 | [azure-aks-autoscaler.md](./references/azure-aks-autoscaler.md) |
| Spot 节点池 | Spot VM、Spot 节点、批处理工作负载、更便宜的节点 | [azure-aks-spot.md](./references/azure-aks-spot.md) |

> **消除歧义**：如果提示词匹配多个行（例如，“更便宜的节点”可能暗示 Spot 和自动扩展），请优先选择最具体的匹配。如果存在歧义，请在加载参考文件前向用户澄清意图。

## 安全约束 / 安全
- 不要请求或输出密钥（令牌、密钥）。
- 不要要求用户粘贴订阅 ID。通过 MCP 工具（例如，列出订阅、列出资源组）或 `az account show` / `az account list` 发现订阅和资源范围，以便代理可以在不暴露标识符的情况下解析上下文。
- 如果 Day-0 关键决策的需求不明确，请向用户提出澄清问题。对于 Day-1 启用的功能，建议 2-3 个安全选项并说明权衡，选择保守的默认值。
- 不要承诺零停机时间；建议工作负载安全措施（PDB、探测器、副本）和分阶段升级，同时遵循可靠性和性能的最佳实践。

## MCP 工具
| 工具 | 目的 | 关键参数 |
|------|---------|----------------|
| `mcp_azure_mcp_aks` | AKS MCP 入口点，用于发现客户端暴露的特定于 AKS 的工具 | 首先发现可调用的 AKS 工具，然后使用该工具的参数 |

## 错误处理
| 错误/症状 | 可能原因 | 补救措施 |
|-----------------|--------------|-------------|
| MCP 工具调用失败或超时 | 无效凭证、订阅或 AKS 上下文 | 验证 `az login`，确认活动订阅上下文与 `az account show`，并检查目标资源组，不要向用户回显订阅标识符 |
| 配额超限 | 区域 vCPU 或资源限制 | 请求配额增加或选择不同区域/VM SKU |
| 网络冲突（IP 耗尽） | Pod 子网太小，无法用于覆盖/CNI | 重新规划 IP 范围；可能需要集群重建（Day-0） |
| Workload Identity 不工作 | 缺少 OIDC 发行人或联合凭证 | 启用 `--enable-oidc-issuer --enable-workload-identity`，配置联合身份 |
