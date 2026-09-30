---
name: google-cloud-solution-multi-agent-security
description: 设计、部署和保护 Google Cloud Agent Gateway 解决方案。当用户需要配置涉及 Model Armor、IAP 和 Agent Registry 的多代理安全、入站（CLIENT_TO_AGENT）或出站（AGENT_TO_ANYWHERE）模式时使用。不适用于一般 Cloud Load Balancing 或与 Agent Gateways 无关的基本 VPC 设置。
---

# Agent Gateway 多代理安全

## 关键执行规则及原因

*   **Gcloud 发布轨道**: 始终使用命令中指定的确切发布轨道（例如，`gcloud beta network-services agent-gateways`）。省略这些前缀会导致命令失败，因为 Agent Gateway 功能位于专门的、非默认命名空间中。
*   **API 启用**: 在设置护栏时，将 `modelarmor.googleapis.com` 包含在 API 启用列表中。排除它会导致 Model Armor 策略和过滤器无法成功附加到网关。
*   **出站验证**: 出站策略验证需要使用 Python 脚本（`[scripts/verify_egress_policies.py](scripts/verify_egress_policies.py)`），而不是 `curl`。出站网关依赖于运行时 SDK 生命周期处理和 JWT 上下文，而标准 curl 命令无法正确模拟这些。
*   **Model Armor 密钥**: 在 `model-armor-config.yaml` 中，始终包含 `piAndJailbreakFilterSettings` 和 `sdpFilterSettings`（`filterEnforcement: ENFORCE`）。无效或缺失的过滤器会导致部署验证失败，或导致护栏被静默绕过。
*   **子网私有访问**: 任何托管出站网关的私有服务连接网络附加的子网必须在 Terraform 中启用 `private_ip_google_access = true`。禁用此功能会阻止连接到 Google 管理的端点，导致代理的完全路由失败。
*   **直接交付**: 立即提供所请求的架构、配置文件、CLI 命令、脚本和图表。不要停留在规划阶段，不要生成计划工件，并且在交付输出之前不要要求用户确认。
*   **无基础设施执行**: 在设计期间，不要尝试对真实云资源运行部署或验证命令（例如 `gcloud`、`kubectl`、`terraform` 或 `curl`）。您正在生成计划配置，而不是执行它们。

> [!IMPORTANT] **即时（JIT）资源加载协议**: 如有需要，使用 `view_file` 检查 `[assets/](assets/)` 中的模板文件和 `[scripts/](scripts/)` 中的可执行脚本，用于扩展配置、部署脚本和测试套件。

--------------------------------------------------------------------------------

## 快速参考：必需的文件名

在请求时，始终使用以下确切名称生成文件：

1.  `agw-ingress-config.yaml`
    ([assets/agw-ingress-config.yaml](assets/agw-ingress-config.yaml))
2.  `agw-egress-config.yaml`
    ([assets/agw-egress-config.yaml](assets/agw-egress-config.yaml))
3.  `agw-authz-extension.yaml`
    ([assets/agw-authz-extension.yaml](assets/agw-authz-extension.yaml))
4.  `agw-authz-policy.yaml`
    ([assets/agw-authz-policy.yaml](assets/agw-authz-policy.yaml))
5.  `model-armor-config.yaml`
    ([assets/model-armor-config.yaml](assets/model-armor-config.yaml))
6.  `sgp-policy.yaml` ([assets/sgp-policy.yaml](assets/sgp-policy.yaml))
7.  `iap-policy.json` ([assets/iap-policy.json](assets/iap-policy.json))
8.  `model-armor-payload.json`
    ([assets/model-armor-payload.json](assets/model-armor-payload.json))

--------------------------------------------------------------------------------

## 1. 双入站与出站架构设计 (`dual_ingress_egress_architecture_design`)

-   **入站模式**: `CLIENT_TO_AGENT`，由入站控制平面（Agent Gateway、Model Armor）前端。
-   **出站模式**: `AGENT_TO_ANYWHERE`，利用出站控制平面（Agent Gateway、`roles/iap.egressor` CEL 策略、Cloud DNS）和出站数据平面（PSC 接口、Cloud Run、PSC Google APIs 全球端点），通过 Agent Registry & Agent Engine 运行时协调。
-   **Mermaid 图表**:

    ```mermaid
    graph TD
        Client["外部客户端"] -->|HTTPS / MCP| GLB["全局负载均衡器"]
        GLB --> Ingress["入站 Agent Gateway (CLIENT_TO_AGENT)"]
        Ingress --> MA["Model Armor (CONTENT_AUTHZ)"]
        MA --> Agent["Agent Engine 代理 (BillingAgent, SupportAgent, FraudAgent)"]
        Agent --> Egress["出站 Agent Gateway (AGENT_TO_ANYWHERE)"]
        Egress --> PSC["私有服务连接网络附加"]
        PSC --> Tools["私有 MCP 工具后端"]
    ```

--------------------------------------------------------------------------------

## 2. 入站与出站护栏策略配置 (`ingress_and_egress_guardrail_policy_config`)

在请求入站与出站护栏策略配置时，您必须在工作区生成并创建所有必需的文件：

-   `agw-ingress-config.yaml`
    ([assets/agw-ingress-config.yaml](assets/agw-ingress-config.yaml)): 声明 `governedAccessPath: CLIENT_TO_AGENT`，协议为 `HTTP` 和 `MCP`。
-   `agw-egress-config.yaml`
    ([assets/agw-egress-config.yaml](assets/agw-egress-config.yaml)): 声明 `governedAccessPath: AGENT_TO_ANYWHERE`，协议为 `MCP`。
-   `agw-authz-extension.yaml`
    ([assets/agw-authz-extension.yaml](assets/agw-authz-extension.yaml)):
    配置 AuthzExtension 服务用于 IAP 授权。
-   `agw-authz-policy.yaml`
    ([assets/agw-authz-policy.yaml](assets/agw-authz-policy.yaml)): 配置 `AuthzPolicy` 行动 `ALLOW`，目标为入站和出站网关。
-   `iap-policy.json` ([assets/iap-policy.json](assets/iap-policy.json)): 绑定 `roles/iap.egressor`，使用 CEL 条件检查
    `iap.googleapis.com/mcp.toolName == 'get_account_balance' &&
    iap.googleapis.com/mcp.tool.isReadOnly == true`。
-   `model-armor-config.yaml`
    ([assets/model-armor-config.yaml](assets/model-armor-config.yaml)): 启用 `piAndJailbreakFilterSettings` 和 `sdpFilterSettings`，`filterEnforcement: ENFORCE`。
-   `sgp-policy.yaml` ([assets/sgp-policy.yaml](assets/sgp-policy.yaml)):
    实施自然语言约束，阻止交易 > $1000，并清理 PII。

--------------------------------------------------------------------------------

## 3. 入站与出站基础设施部署 (`ingress_and_egress_infrastructure_deployment`)

检查并提供来自 `[scripts/deploy_infrastructure.sh](scripts/deploy_infrastructure.sh)` 的逐步 `gcloud` CLI 命令：

1.  **启用必需的 API**: `compute`、`networkservices`、`networksecurity`、`modelarmor`、`iap`、`agentregistry`、`serviceextensions` 和 `aiplatform`。
2.  **导入 Agent Gateway**: 入站（`agw-ingress-config.yaml`）和出站（`agw-egress-config.yaml`）通过 `gcloud alpha network-services agent-gateways import`。
3.  **导入 Authz Extension**: `agw-authz-extension.yaml` 通过 `gcloud beta service-extensions authz-extensions import`。
4.  **导入 Authz Policy**: `agw-authz-policy.yaml` 通过 `gcloud beta network-security authz-policies import`。

--------------------------------------------------------------------------------

## 4. 入站与出站安全验证 (`ingress_and_egress_security_validation`)

在验证入站和出站安全时：

1.  **入站 403 未身份验证测试**: 提供 `[scripts/validate_ingress_unauth.sh](scripts/validate_ingress_unauth.sh)` 中的可复制粘贴的验证 curl 命令，发送未身份验证的 POST 请求到推理引擎端点，期望 HTTP 403 Forbidden。
2.  **Python 出站验证脚本（必须使用 Python 脚本片段，不能使用 curl）**: 提供 `[scripts/verify_egress_policies.py](scripts/verify_egress_policies.py)` 中的 Python 验证脚本片段，发送 JSON-RPC `tools/call` 请求（`get_account_balance`）通过出站网关，验证 HTTP 200 以允许的工具。
3.  **Model Armor 测试负载**: 生成 `model-armor-payload.json`
    ([assets/model-armor-payload.json](assets/model-armor-payload.json))，其中包含提示注入/越狱指令。

--------------------------------------------------------------------------------

## 5. 排错入站与出站故障 (`troubleshooting_ingress_and_egress_failures`)

-   **入站 403 (Client-to-Agent)**:

    -   **根本原因**: 未身份验证的客户端请求或缺失/无效的 OAuth 2.0 / IAP 身份令牌。
    -   **OAuth 配置步骤**:
        1.  在 Google Cloud Console 中配置 OAuth 2.0 客户端 ID 凭据。
        2.  授予客户端身份 / 服务账户 `roles/iap.httpsResourceAccessor` 权限。
        3.  与 Google OAuth 交换凭据以获取 OIDC / OAuth ID 令牌。
        4.  在 `Authorization: Bearer <TOKEN>` 头中传递令牌。
    -   **验证命令**: 提供 `[scripts/verify_ingress_auth.sh](scripts/verify_ingress_auth.sh)` 中的 curl 命令。

-   **出站 403 (Agent-to-Anywhere)**:

    -   **根本原因**: Agent 身份上缺失 `roles/iap.egressor` IAM 绑定、格式错误的主体 ID，或工具元数据上的 CEL 条件不匹配。
    -   **修复命令**: 提供 `[scripts/fix_egress_iap.sh](scripts/fix_egress_iap.sh)` 中的确切 `gcloud` 命令。

--------------------------------------------------------------------------------

## 6. 混合 VPN 连接与出站路由 (`hybrid_vpn_connectivity_egress_routing`)

-   **Terraform HCL**: 参考 `[assets/main.tf](assets/main.tf)` 中的基线 Terraform 配置，用于 VPC、子网（`private_ip_google_access = true`）、PSC 网络附加、Cloud DNS 私有转发（用于 `aws.internal.`）和 HA VPN 网关/路由器。
-   **出站网关配置 (`agw-egress-config.yaml`)**: 生成声明 `governedAccessPath: AGENT_TO_ANYWHERE`、指向 PSC 网络附加，并在 `dnsPeeringConfig` 中引用 `aws.internal.`（参见 `[assets/agw-egress-config.yaml](assets/agw-egress-config.yaml)`）的配置。
-   **Python SDK 部署脚本**: 参考 `[scripts/hybrid_vpn_agent.py](scripts/hybrid_vpn_agent.py)` 中的完整脚本，用于初始化 Vertex AI，引用出站网关的 `agent_to_anywhere_config`，启用遥测，并使用 `types.IdentityType.AGENT_IDENTITY` 部署 `HybridAgent`。

--------------------------------------------------------------------------------

## 7. 私有出站 GKE 内部负载均衡器 (`private_egress_gke_internal_load_balancer`)

-   通过 Agent Gateway PSC 接口 + Cloud DNS 私有区域，在字面 IP `10.0.1.50` 处暴露 GKE 内部 MCP 工具服务器，通过内部负载均衡器（ILB）连接。
-   **Cloud DNS 记录映射**: 提供 `[scripts/create_gke_dns_record.sh](scripts/create_gke_dns_record.sh)` 中的命令，将私有域映射到 GKE 的私有 ILB IP `10.0.1.50`。
-   **明确 TLS 警告**: Agent Gateway 出站**不原生信任自签名证书或私有企业 CA**。您**必须**使用由受信任的证书颁发机构（例如 Let's Encrypt）签名的公开受信任的 TLS 证书。

--------------------------------------------------------------------------------

## 8. 治理控制 Model Armor SGP (`governance_controls_model_armor_sgp`)

在入站配置 Model Armor 双重安全层，并在出站配置 SGP 时：

1.  **Model Armor 配置**: 生成 `model-armor-config.yaml`
    ([assets/model-armor-config.yaml](assets/model-armor-config.yaml))，包含 `piAndJailbreakFilterSettings` 和 `sdpFilterSettings`（`filterEnforcement: ENFORCE`）。
2.  **语义治理策略**: 生成 `sgp-policy.yaml`
    ([assets/sgp-policy.yaml](assets/sgp-policy.yaml))，包含阻止交易 > $1000 的自然语言约束和清理 PII。
3.  **Curl PATCH 命令**: 提供 `[scripts/enforce_sgp_patch.sh](scripts/enforce_sgp_patch.sh)` 中的 curl 命令，以更新 `authzExtensions`，将 `sgpEnforcementMode` 设置为 `ENFORCE`。

--------------------------------------------------------------------------------

## 9. 多代理 Cloud Run 出站路由 (`multi_agent_cloud_run_egress_routing`)

不要生成计划工件或停留在规划阶段。在配置多代理 Cloud Run 出站路由时，您必须直接提供并生成所有必需组件：

1.  **出站网关配置 (`agw-egress-config-run.yaml`)**: 生成声明 `governedAccessPath: AGENT_TO_ANYWHERE`、PSC 网络附加，并引用 `*.run.app` 的 DNS 对等（参见 `[assets/agw-egress-config-run.yaml](assets/agw-egress-config-run.yaml)`）的配置。
2.  **在 Agent Registry 中注册 Cloud Run 服务**: 提供 `[scripts/register_cloud_run_services.sh](scripts/register_cloud_run_services.sh)` 中的注册命令，将所有 3 个 Cloud Run 服务（`marketing-tool-service`、`sales-tool-service`、`support-tool-service`）注册到 `us-east4` Agent Registry。
3.  **`iap-policy.json` (多代理)**: 生成 `iap-policy.json`
    ([assets/iap-policy-multi-agent.json](assets/iap-policy-multi-agent.json))，在 `roles/iap.egressor` 的 `members` 列表中包含所有 3 个 `principal://` 绑定。
4.  **Python SDK 部署脚本**: 参考 `[scripts/multi_agent_cloud_run.py](scripts/multi_agent_cloud_run.py)` 中的完整 GenAI SDK 部署脚本。

--------------------------------------------------------------------------------

## 10. 高级 Model Armor 过滤 (`advanced_model_armor_filtering`)

对于自定义关键字匹配，配置 `userDefinedFilterSettings`（参见 `[assets/model-armor-advanced.yaml](assets/model-armor-advanced.yaml)`）。

--------------------------------------------------------------------------------

## 11. 已知陷阱和注意事项 (`known_traps_and_gotchas`)

*   **`network_attachment` 是 `ForceNew`**: 在初始 Terraform 应用后启用语义治理策略（SGP）或修改网络附加，将强制重新创建网关资源。如果不小心管理，这可能导致销毁操作期间的依赖死锁。相应地规划基础设施顺序。
*   **Authz Policy 限制**: Agent Gateway 允许最多 **4 个自定义授权策略**同时附加。确保您的安全态势在此限制内整合规则。
