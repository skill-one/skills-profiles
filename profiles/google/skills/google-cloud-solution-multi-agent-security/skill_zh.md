# Agent Gateway多代理安全

## 关键执行规则及原因

*   **Gcloud发布版本追踪**: 命令中必须使用指定的确切发布版本追踪（例如，`gcloud beta network-services agent-gateways`）。省略这些前缀会导致命令失败，因为Agent Gateway功能位于专门的、非默认的命名空间中。
*   **API启用**: 在设置护栏时，必须在API启用列表中包含`modelarmor.googleapis.com`。排除它会导致Model Armor策略和过滤器无法成功附加到网关。
*   **出站验证**: 出站策略验证需要使用Python脚本（[scripts/verify_egress_policies.py](scripts/verify_egress_policies.py)），而不是`curl`。出站网关依赖于运行时SDK生命周期处理和JWT上下文，而标准curl命令无法正确模拟这些。
*   **Model Armor密钥**: 在`model-armor-config.yaml`中，始终包含`piAndJailbreakFilterSettings`和`sdpFilterSettings`（`filterEnforcement: ENFORCE`）。无效或缺失的过滤器会导致部署验证失败，或导致护栏被静默绕过。
*   **子网私有访问**: 任何托管出站网关私有服务连接网络附件的子网都必须在Terraform中启用`private_ip_google_access = true`。禁用此功能会阻止连接到Google管理的端点，导致代理完全路由失败。
*   **直接交付**: 立即提供所请求的架构、配置文件、CLI命令、脚本和图表。不要停留在规划阶段，不要生成计划工件，并且在交付输出之前不要要求用户确认。
*   **无基础设施执行**: 在设计期间，不要尝试对真实云资源运行部署或验证命令（例如`gcloud`、`kubectl`、`terraform`或`curl`）。你正在生成计划配置，而不是执行它们。

> [!IMPORTANT] **即时（JIT）资源加载协议**: 根据需要使用`view_file`检查[assets/](assets/)中的模板文件和[scripts/](scripts/)中的可执行脚本，用于扩展配置、部署脚本和测试套件。

--------------------------------------------------------------------------------

## 快速参考：必需的文件名

当被要求时，始终使用以下确切名称生成文件：

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

## 1. 双入站与出站架构设计（`dual_ingress_egress_architecture_design`）

-   **入站模式**: `CLIENT_TO_AGENT`，由入站控制平面（Agent Gateway、Model Armor）前端。
-   **出站模式**: `AGENT_TO_ANYWHERE`，利用出站控制平面（Agent Gateway、`roles/iap.egressor` CEL策略、Cloud DNS）和出站数据平面（PSC接口、Cloud Run、PSC Google API全局端点），通过Agent Registry & Agent Engine运行时协调。
-   **Mermaid图表**:

    ```mermaid
    graph TD
        Client["外部客户端"] -->|HTTPS / MCP| GLB["全局负载均衡器"]
        GLB --> Ingress["入站Agent Gateway (CLIENT_TO_AGENT)"]
        Ingress --> MA["Model Armor (内容授权)"]
        MA --> Agent["Agent Engine代理 (BillingAgent, SupportAgent, FraudAgent)"]
        Agent --> Egress["出站Agent Gateway (AGENT_TO_ANYWHERE)"]
        Egress --> PSC["私有服务连接网络附件"]
        PSC --> Tools["私有MCP工具后端"]
    ```

--------------------------------------------------------------------------------

## 2. 入站与出站护栏策略配置（`ingress_and_egress_guardrail_policy_config`）

当被要求提供入站与出站护栏策略配置时，你必须生成并创建工作区中的所有必需文件：

-   `agw-ingress-config.yaml`
    ([assets/agw-ingress-config.yaml](assets/agw-ingress-config.yaml)): 声明`governedAccessPath: CLIENT_TO_AGENT`，协议为`HTTP`和`MCP`。
-   `agw-egress-config.yaml`
    ([assets/agw-egress-config.yaml](assets/agw-egress-config.yaml)): 声明`governedAccessPath: AGENT_TO_ANYWHERE`，协议为`MCP`。
-   `agw-authz-extension.yaml`
    ([assets/agw-authz-extension.yaml](assets/agw-authz-extension.yaml)): 配置用于IAP授权的AuthzExtension服务。
-   `agw-authz-policy.yaml`
    ([assets/agw-authz-policy.yaml](assets/agw-authz-policy.yaml)): 配置`AuthzPolicy`动作`ALLOW`，目标为入站和出站网关。
-   `iap-policy.json` ([assets/iap-policy.json](assets/iap-policy.json)): 绑定`roles/iap.egressor`，使用CEL条件检查`iap.googleapis.com/mcp.toolName == 'get_account_balance' &&
    iap.googleapis.com/mcp.tool.isReadOnly == true`。
-   `model-armor-config.yaml`
    ([assets/model-armor-config.yaml](assets/model-armor-config.yaml)): 启用`piAndJailbreakFilterSettings`和`sdpFilterSettings`，`filterEnforcement: ENFORCE`。
-   `sgp-policy.yaml` ([assets/sgp-policy.yaml](assets/sgp-policy.yaml)): 实现自然语言约束，阻止交易> $1000，并清理PII。

--------------------------------------------------------------------------------

## 3. 入站与出站基础设施部署（`ingress_and_egress_infrastructure_deployment`）

检查并提供来自[scripts/deploy_infrastructure.sh](scripts/deploy_infrastructure.sh)的逐步`gcloud` CLI命令：

1.  **启用必需的API**: `compute`、`networkservices`、`networksecurity`、`modelarmor`、`iap`、`agentregistry`、`serviceextensions`和`aiplatform`。
2.  **导入Agent Gateway**: 入站（`agw-ingress-config.yaml`）和出站（`agw-egress-config.yaml`）通过`gcloud alpha network-services agent-gateways import`。
3.  **导入Authz Extension**: `agw-authz-extension.yaml`通过`gcloud beta service-extensions authz-extensions import`。
4.  **导入Authz Policy**: `agw-authz-policy.yaml`通过`gcloud beta network-security authz-policies import`。

--------------------------------------------------------------------------------

## 4. 入站与出站安全验证（`ingress_and_egress_security_validation`）

当验证入站和出站安全时：

1.  **入站403未身份验证测试**: 提供从[scripts/validate_ingress_unauth.sh](scripts/validate_ingress_unauth.sh)复制的验证curl命令，发送未身份验证的POST请求到推理引擎端点，期望HTTP 403禁止。
2.  **Python出站验证脚本（必须使用Python脚本片段，不能使用curl）**: 提供从[scripts/verify_egress_policies.py](scripts/verify_egress_policies.py)的Python验证脚本片段，发送JSON-RPC `tools/call`请求（`get_account_balance`）通过出站网关，验证允许工具的HTTP 200。
3.  **Model Armor测试负载**: 生成`model-armor-payload.json`
    ([assets/model-armor-payload.json](assets/model-armor-payload.json))，包含提示注入/越狱指令。

--------------------------------------------------------------------------------

## 5. 排查入站与出站故障（`troubleshooting_ingress_and_egress_failures`）

-   **入站403（客户端到代理）**:

    -   **根本原因**: 未身份验证的客户端请求或缺失/无效的OAuth 2.0 / IAP身份令牌。
    -   **OAuth配置步骤**:
        1.  在Google Cloud Console中配置OAuth 2.0客户端ID凭证。
        2.  授予客户端身份/服务账户`roles/iap.httpsResourceAccessor`权限。
        3.  与Google OAuth交换凭证以获取OIDC / OAuth ID令牌。
        4.  在`Authorization: Bearer <TOKEN>`标头中传递令牌。
    -   **验证命令**: 提供来自[scripts/verify_ingress_auth.sh](scripts/verify_ingress_auth.sh)的curl命令。

-   **出站403（代理到任何地方）**:

    -   **根本原因**: 代理身份上缺失`roles/iap.egressor` IAM绑定、格式错误的主体ID，或工具元数据上的CEL条件不匹配。
    -   **修复命令**: 提供来自[scripts/fix_egress_iap.sh](scripts/fix_egress_iap.sh)的确切`gcloud`命令。

--------------------------------------------------------------------------------

## 6. 混合VPN连接与出站路由（`hybrid_vpn_connectivity_egress_routing`）

-   **Terraform HCL**: 参考[assets/main.tf](assets/main.tf)中的基线Terraform配置，用于VPC、子网（`private_ip_google_access = true`）、PSC网络附件、Cloud DNS私有转发（用于`aws.internal.`）和HA VPN网关/路由器。
-   **出站网关配置（`agw-egress-config.yaml`）**: 生成配置，声明`governedAccessPath: AGENT_TO_ANYWHERE`，指向PSC网络附件，并在`dnsPeeringConfig`中引用`aws.internal.`（参见[assets/agw-egress-config.yaml](assets/agw-egress-config.yaml)）。
-   **Python SDK部署脚本**: 参考[scripts/hybrid_vpn_agent.py](scripts/hybrid_vpn_agent.py)的完整脚本，初始化Vertex AI，使用`agent_to_anywhere_config`引用出站网关，启用遥测，并使用`types.IdentityType.AGENT_IDENTITY`部署`HybridAgent`。

--------------------------------------------------------------------------------

## 7. 私有出站GKE内部负载均衡器（`private_egress_gke_internal_load_balancer`）

-   通过内部负载均衡器（ILB）在字面IP `10.0.1.50`上暴露GKE内部MCP工具服务器，通过Agent Gateway PSC接口+Cloud DNS私有区域连接。
-   **Cloud DNS记录映射**: 提供来自[scripts/create_gke_dns_record.sh](scripts/create_gke_dns_record.sh)的命令，将私有域映射到GKE的私有ILB IP `10.0.1.50`。
-   **明确TLS警告**: Agent Gateway出站**不原生信任自签名证书或私有企业CA**。你必须使用由受信任的证书颁发机构签名的公开受信任的TLS证书（例如，Let's Encrypt）。

--------------------------------------------------------------------------------

## 8. 治理控制Model Armor SGP（`governance_controls_model_armor_sgp`）

当在入站上配置Model Armor双安全层，并在出站上配置SGP时：

1.  **Model Armor配置**: 生成`model-armor-config.yaml`
    ([assets/model-armor-config.yaml](assets/model-armor-config.yaml))，包含`piAndJailbreakFilterSettings`和`sdpFilterSettings`（`filterEnforcement: ENFORCE`）。
2.  **语义治理策略**: 生成`sgp-policy.yaml`
    ([assets/sgp-policy.yaml](assets/sgp-policy.yaml))，包含阻止交易> $1000的自然语言约束和清理PII。
3.  **Curl PATCH命令**: 提供来自[scripts/enforce_sgp_patch.sh](scripts/enforce_sgp_patch.sh)的curl命令，以更新`authzExtensions`，将`sgpEnforcementMode`设置为`ENFORCE`。

--------------------------------------------------------------------------------

## 9. 多代理Cloud Run出站路由（`multi_agent_cloud_run_egress_routing`）

不要生成计划工件或停留在规划阶段。当配置多代理Cloud Run出站路由时，你必须直接提供并生成所有必需组件：

1.  **出站网关配置（`agw-egress-config-run.yaml`）**: 生成配置，声明`governedAccessPath: AGENT_TO_ANYWHERE`，PSC网络附件，以及`*.run.app`的DNS对等（参见[assets/agw-egress-config-run.yaml](assets/agw-egress-config-run.yaml)）。
2.  **在Agent Registry中注册Cloud Run服务**: 提供来自
    [scripts/register_cloud_run_services.sh](scripts/register_cloud_run_services.sh)的注册命令，注册所有3个Cloud Run服务（`marketing-tool-service`、`sales-tool-service`、`support-tool-service`）到`us-east4` Agent Registry。
3.  **`iap-policy.json`（多代理）**: 生成`iap-policy.json`
    ([assets/iap-policy-multi-agent.json](assets/iap-policy-multi-agent.json))，包含`roles/iap.egressor`下`members`列表中的所有3个`principal://`绑定。
4.  **Python SDK部署脚本**: 参考
    [scripts/multi_agent_cloud_run.py](scripts/multi_agent_cloud_run.py)的完整GenAI SDK部署脚本。

--------------------------------------------------------------------------------

## 10. 高级Model Armor过滤（`advanced_model_armor_filtering`）

对于自定义关键字匹配，配置`userDefinedFilterSettings`（参见[assets/model-armor-advanced.yaml](assets/model-armor-advanced.yaml)）。

--------------------------------------------------------------------------------

## 11. 已知陷阱和注意事项（`known_traps_and_gotchas`）

*   **`network_attachment`是`ForceNew`**: 在初始Terraform应用后启用语义治理策略（SGP）或修改网络附件将强制重建网关资源。如果不小心管理，这可能导致销毁操作期间的依赖死锁。相应地规划基础设施顺序。
*   **Authz Policy限制**: Agent Gateway最多允许**4个自定义授权策略**同时附加。确保你的安全态势在此限制内整合规则。
