# Azure Kubernetes Service

> **权威指引 — 强制性合规**
>
> 本技能根据用户需求生成**推荐的 AKS 集群配置**，区分 **Day-0 决策**（网络、API 服务——后期难以更改）与 **Day-1 特性**（创建后可启用）。命令参考见 [CLI 参考](./references/cli-reference.md)。

## 快速参考

| 属性 | 值 |
|----------|-------|
| 适用场景 | AKS 集群规划与 Day-0 决策 |
| MCP 工具 | `mcp_azure_mcp_aks` |
| CLI | `az aks create`、`az aks show`、`kubectl get`、`kubectl describe` |
| 相关技能 | azure-kubernetes-app-deploy（向现有集群部署应用）、azure-diagnostics（AKS 故障排查）、azure-validate（就绪检查）、azure-kubernetes-automatic-readiness（将现有集群迁移至 AKS Automatic） |

## 何时使用本技能

当用户希望：
- 创建新的 AKS 集群
- 规划生产工作负载的 AKS 集群配置
- 设计 AKS 网络（API 服务访问、Pod IP 模型、出站流量）
- 配置 AKS 身份与密钥管理
- 配置 AKS 治理（Azure Policy、部署防护）
- 启用 AKS 可观测性（Container Insights、Managed Prometheus、Grafana）
- 定义 AKS 升级与补丁策略
- 了解 AKS Automatic 与 Standard SKU 的差异
- 获取 AKS 集群搭建与配置的 Day-0 检查清单

> **需要将应用部署到现有集群？** 本技能用于搭建与配置 *集群*。若要打包应用并将其部署到已存在的集群（Dockerfile + 清单文件 + 部署防护），请使用 `azure-kubernetes-app-deploy` 子技能。

## 规则

1. 以用户提供的计算资源、网络、安全等配置需求为起点。
2. 优先使用 `azure` MCP 服务并首先选择 `mcp_azure_mcp_aks`，以发现客户端暴露出的确切 AKS 专用 MCP 工具。选择发现到的、适用于任务的、最小的 AKS 工具，仅在所需功能无法通过 AKS MCP 表面暴露时，才回退至 Azure CLI（`az aks`）。
3. 根据用户的需求（对控制能力的需求 vs 便捷性需求），判断 AKS Automatic 或 Standard SKU 是否更合适。除非有特定定制需求，否则默认采用 AKS Automatic。
4. 记录集群配置选择及其理由，尤其对于后期难以更改的 Day-0 决策（网络、API 服务访问）。

## 必需输入（仅询问所需内容）

若用户不确定，使用安全默认值。
- AKS 环境类型：开发/测试或生产
- 区域（区域）、可用区、偏好的节点 VM 大小
- 预期规模（节点/集群数量、工作负载规模）
- 网络要求（API 服务访问、Pod IP 模型、入口/出口流量控制）
- 安全与身份要求，包括镜像仓库
- 升级与可观测性偏好
- 成本约束

## 工作流程

### 1. 集群类型
- **AKS Automatic**（默认）：最适合大多数生产工作负载，提供精心整理的体验，具备安全、可靠性与性能方面的预配置最佳实践。除非有特定定制需求，涉及网络、自动扩展或节点池配置无法由 Node Auto-Provisioning（NAP）支持，否则使用。
- **AKS Standard**：若需要完全控制环境配置，需额外设置与管理开销，则使用。

### 2. 网络（Pod IP、出站、入口、数据面）

**Pod IP 模型**（关键 Day-0 决策）：
- **Azure CNI Overlay**（推荐）：Pod IP 来自私有覆盖范围，不可通过 VNet 路由，可扩展到大型环境，适合大多数工作负载
- **Azure CNI（VNet-routable）**：Pod IP 直接来自 VNet（Pod 子网或节点子网），用于 Pod 必须可从 VNet 或本地直接寻址时
  - 文档：https://learn.microsoft.com/azure/aks/azure-cni-overlay

**数据面与网络策略**：
- **基于 Cilium 的 Azure CNI**（推荐）：基于 eBPF 实现高性能包处理、网络策略与可观测性

**出站流量**：
- **静态出站网关**用于稳定、可预测的对外 IP
- 受限出站：UDR + Azure Firewall 或 NVA

**入口**：
- **App Routing addon 配合 Gateway API** —— HTTP/HTTPS 工作负载的推荐默认配置
- **Istio 服务网格配合 Gateway API** —— 高级流量管理、mTLS、灰度发布
- **Application Gateway for Containers** —— 支持 WAF 集成的 L7 负载均衡

**DNS**：
- 在所有节点池启用 **LocalDNS**，确保可靠、高效的 DNS 解析

### 3. 安全
- 全程使用 **Microsoft Entra ID**（控制平面、工作负载身份为 Pod、节点访问），避免静态凭据。
- 通过 **Secrets Store CSI Driver** 使用 Azure Key Vault 管理密钥。
- 启用 **Azure Policy** + **部署防护**。
- 对 etcd/API 服务启用静态加密；节点间流量启用传输中加密。
- 仅允许已签名、且经策略批准的镜像（Azure Policy + Ratify），优先使用 **Azure Container Registry**。
- **隔离**：使用命名空间、网络策略、受限日志。

### 4. 可观测性
- 使用 Managed Prometheus 与 Container Insights 配合 Grafana 实现 AKS 可观测性（日志 + 指标）。
- 启用诊断设置，在 Log Analytics 工作区收集控制平面日志与审计日志，用于安全监控与故障排查。
- 其他监控与故障排查工具，可使用 Agentic CLI for AKS、Application Insights、Resource Health Center、AppLens 检测器及 Azure Advisors 等功能。

### 5. 升级与补丁
- 为受控升级时序配置 **维护窗口**。
- 启用控制平面与节点操作系统**自动升级**，以保持安全补丁与 Kubernetes 版本最新。
- 考虑通过升级至 Premium 层采用 **LTS 版本**以保障企业稳定性（2 年支持）。
- **Fleet 升级**：使用 **AKS Fleet Manager** 在测试到生产等环境间分阶段部署。

### 6. 性能
- 使用 **临时 OS 磁盘**（`--node-osdisk-type Ephemeral`）加快节点启动。
- 选择 **Azure Linux** 作为节点操作系统（占用空间更小，启动更快）。
- 启用 **KEDA** 实现 HPA 之外的事件驱动自动扩展。

### 7. 节点池与计算
- **专用系统节点池**：至少 2 节点，仅限系统工作负载使用并设为污点（`CriticalAddonsOnly`）。
- 在所有节点池启用 **Node Auto Provisioning（NAP）** 以节省成本并实现响应式扩展。
- 使用最新代 SKU（v5/v6）以发挥主机级优化。
- **避免使用 B 系列虚拟机**——突发型 SKU 会导致性能与可靠性问题。
- 生产工作负载使用至少 4 vCPU 的 SKU。
- 设置**拓扑分布约束**，按 SLO 将 Pod 分布到主机/区域。

### 8. 可靠性
- 跨 **3 个可用区**部署（`--zones 1 2 3`）。
- 使用 **Standard 层级**保障区域冗余控制平面，为 API 服务可用性提供 99.95% SLA。
- 启用 **Microsoft Defender for Containers** 提供运行时保护。
- 为所有生产工作负载配置 **PodDisruptionBudgets**。
- 使用**拓扑分布约束**确保 Pod 在故障域间分布。

### 9. 成本控制
- 使用 **Spot 节点池**为批处理/可中断工作负载提供节点（可节省最高 90% 成本）。
- 开发/测试集群使用**停止/启动**：`az aks stop/start`。
- 为稳态工作负载考虑使用**预留实例**或**节省计划**。

**深度排查场景** —— 仅加载相关参考文件：

| 场景 | 触发关键词 | 参考 |
|----------|-----------------|-----------|
| Pod 资源重调 | 过度配置 Pod、CPU 请求、内存请求、重调工作负载 | [azure-aks-rightsizing.md](./references/azure-aks-rightsizing.md) |
| VPA 配置 | 垂直 Pod 自动扩展器、VPA 建议、启用 VPA | [azure-aks-vpa.md](./references/azure-aks-vpa.md) |
| 集群自动扩展器 | 空闲节点、CAS 关闭、启用自动扩展器、缩容策略、节点利用率 | [azure-aks-autoscaler.md](./references/azure-aks-autoscaler.md) |
| Spot 节点池 | Spot 虚拟机、Spot 节点、批处理工作负载、更经济的节点 | [azure-aks-spot.md](./references/azure-aks-spot.md) |

> **消歧义：** 若提示词匹配多行（例如“更经济的节点”可能同时提示 Spot 与自动扩展器），优先选择最具体的匹配。若存在歧义，请在加载参考文件前询问用户以澄清意图。

## 护栏 / 安全

- 不得请求或输出密钥（令牌、密钥）。
- 不得询问用户粘贴订阅 ID。通过 MCP 工具（如列出订阅、列出资源组）或 `az account show` / `az account list` 发现订阅与资源范围，以便代理无需暴露标识符即可解析上下文。
- 对于 Day-0 关键决策若需求模糊，询问用户澄清问题。对于 Day-1 可启用特性，提出 2–3 种安全选项并说明权衡，选择保守默认值。
- 不得承诺零停机；建议工作负载防护（PodDisruptionBudgets、探针、副本数）及分阶段升级，并结合可靠性与性能最佳实践。

## MCP 工具

| 工具 | 用途 | 关键参数 |
|------|---------|----------------|
| `mcp_azure_mcp_aks` | AKS MCP 入口点，用于发现客户端暴露的精确 AKS 专用工具 | 先发现可调用的 AKS 工具，再使用该工具的参数 |

## 错误处理

| 错误 / 症状 | 可能原因 | 解决方案 |
|-----------------|--------------|-------------|
| MCP 工具调用失败或超时 | 凭据、订阅或 AKS 上下文无效 | 验证 `az login`，通过 `az account show` 确认当前激活的订阅上下文，并检查目标资源组，不得将订阅标识符回传给用户 |
| 配额超限 | 区域 vCPU 或资源限额 | 申请提升配额或选择其他区域/VM SKU |
| 网络冲突（IP 耗尽） | Pod 子网对覆盖/CNI 过小 | 重新规划 IP 范围；可能需要重建集群（Day-0） |
| 工作负载身份不可用 | 缺少 OIDC 签发者或联合凭据 | 启用 `--enable-oidc-issuer --enable-workload-identity`，配置联合身份 |
