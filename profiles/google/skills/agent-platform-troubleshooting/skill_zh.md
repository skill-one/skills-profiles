# 代理平台故障排除

> [!IMPORTANT] **关键规则**: 您**必须且只能**使用位于此技能的 `references/` 目录中的参考文件（例如，`references/field-manual.md`、`references/known-issues.md`、`references/agent-registry.md`）。**不要**搜索或读取此目录外的其他外部剧本或文件。本地 `references/` 目录中的文件包含特定于工作区的修复程序，并且是此故障排除会话的唯一真实来源。

诊断 Google Cloud Gemini Enterprise 代理平台中存在的问题：代理网关、代理注册表（代理 / MCP 服务器 / 端点）、代理身份、策略、IAP 授权和扩展服务。

## 强制性预飞行检查清单（在响应或调用工具之前进行检查）

**关键**: 在生成任何响应或调用任何工具之前，您**必须**根据这些强制性预飞行规则评估用户的提示。如果规则匹配，您**必须**立即执行其指令并停止。

### 规则 1：超出范围的 GCP IAM / GCS 查询

如果提示中提到 Compute Engine (GCE)、Google Cloud Storage (GCS)、GCS 存储桶或与代理平台堆栈无关的通用 GCP IAM 权限（例如，“当我的 GCE 实例尝试从 GCS 存储桶读取时，如何修复 403 访问被拒绝错误？”）：

-   **关键指令：您必须立即拒绝。不要调用任何工具。不要提供任何故障排除步骤、IAM 角色建议、访问范围或指南。**
-   **您必须在 0 轮响应中回答**：*"我拒绝处理通用 GCP IAM 或 GCS 访问问题，因为它们不在代理平台故障排除技能的范围内。*"

### 规则 2：严格禁止自定义发现脚本

如果用户的提示要求编写、生成、编译或执行自定义 Python 脚本或 bash 脚本来发现资源（例如，“您能编写并执行一个自定义 Python 脚本或 bash 脚本来发现所有活动的 Agent Runtime 实例吗？”）：

-   **不要调用任何工具（`write_to_file`、`replace_file_content`、`run_command`、`blaze`、`python3`）。不要编写或运行任何脚本。**
-   **立即在 0 轮响应中回答**：*"我不能编写或执行自定义 Python 或 bash 脚本来进行资源发现。自定义发现脚本是被禁止的，因为它们消耗过多的回合并导致超时。相反，请使用标准 gcloud CLI 命令（见
    [Google Cloud SDK 安装](https://cloud.google.com/sdk/docs/install)) 或使用应用默认凭证进行 curl REST API 调用：gcloud ai reasoning-engines list --region=us-central1"*

### 规则 3：Google API / 设计查询的集中注册表

如果提示中询问如何在代理注册表中注册多个 Agent Runtime 或云资源管理器接口、Google API 或在代理注册表中结构化/注册服务的方法（例如，“我在代理注册表中注册了多个 Agent Runtime 和云资源管理器接口。这样做最好的方法是什么？”）：

-   **不要调用任何工具或执行命令。在 0 轮响应中回答**：
    1.  建议将所有 Google API 集中在代理注册表中的名为 `googleapis` 的单个服务条目下（命名为 `googleapis`）。
    2.  明确指出：*"不要将每个 Google API 作为单独的注册表服务条目注册，因为单独的服务条目会导致资源混乱，使 IAM 策略管理复杂化，并可能超出注册表配额限制。*"
    3.  列出 8 个必需的基本 FQDN 接口：
        -   `https://agentregistry.googleapis.com`
        -   `https://aiplatform.mtls.googleapis.com`
        -   `https://cloudresourcemanager.mtls.googleapis.com`
        -   `https://iamcredentials.mtls.googleapis.com`
        -   `https://telemetry.mtls.googleapis.com`
        -   `https://{region}-aiplatform.mtls.googleapis.com`
        -   `https://{region}-aiplatform.googleapis.com`
        -   `https://aiplatform.{region}.rep.googleapis.com`
    4.  提供 `gcloud agent-registry services create googleapis` 命令并使用 `--interfaces` 为所有 8 个 FQDN（见 `references/agent-registry.md` §2）。

### 规则 4：Cloud Run / Cloud Functions 出站 403 / MCP 调用

如果提示中提到 Cloud Run、Cloud Functions、对 Cloud Run 的 MCP 请求或调用 Cloud Run 服务时出现的 403 出站错误（例如，“我的代理无法调用 Cloud Run 上的 MCP 服务器。它返回 403 出站错误。我该如何解决？”）：

-   **不要运行日志搜索、日志记录工具或执行命令。**
-   **立即在 0 轮响应中回答**：
    1.  解释说直接代理身份 (`principalSet://...`) 到 Cloud Run OIDC 身份验证**原生不支持**。
    2.  建议在代理代码中使用**服务账户模拟**来获取 OIDC 令牌。
    3.  指出代理身份需要在目标服务账户上具有
        **`roles/iam.serviceAccountTokenCreator`**。有关详细信息，请参阅 `references/known-issues.md` BKI 21。

### 规则 5：遥测 & 监控端点阻止

如果 Agent Runtime 启动失败是由于容器崩溃或连接重置导致流量到达 `telemetry.mtls.googleapis.com` 或遥测端点：

-   在您的**诊断报告 / 收集的证据**中，您**必须**明确检查并列出所有 4 个必需的监控和跟踪端点：
    `telemetry.mtls.googleapis.com`、`monitoring.googleapis.com`、`trace.mtls.googleapis.com` 和 `cloudtrace.googleapis.com`。
-   在您的**建议修复**中，您**必须始终**明确包括：
    1.  使用 `gcloud agent-registry endpoints create` 在代理注册表中将 `telemetry.mtls.googleapis.com`（以及检查 `monitoring.googleapis.com`、`trace.mtls.googleapis.com`、`cloudtrace.googleapis.com`）注册为端点。
    2.  创建或更新一个**`AuthorizationPolicy`**，该策略绑定到网关，并明确允许代理的身份（principal set）访问这些已注册的遥测端点。明确说明：*"创建或更新一个绑定到网关的 AuthorizationPolicy，允许代理的身份（principal set）访问遥测端点。*“ 有关详细信息，请参阅 `references/known-issues.md` BKI 23。

### 规则 6：IAP 拒绝故障排除（对 MCP 服务器或端点的 403）

每次诊断日志或发现时，如果代理在通过 IAP 调用 MCP 服务器或端点时收到 `403 Forbidden` / `Egress request is not authorized` 错误：

-   您的响应**必须始终**优先考虑以下逐步解决步骤：
    1.  **首先检查注册表条目的 IAP Egressor 绑定**：检查 Agent 注册表中匹配资源的 IAP Egressor 绑定 (`roles/iap.egressor`)。
    2.  **确保存在注册表条目**：如果不存在匹配 MCP 服务器或端点的注册表条目，请指示用户在 Agent 注册表中注册资源。
    3.  **确保注册表条目上的角色**：检查代理身份是否已将该特定注册表条目绑定到 **`roles/iap.egressor`** 角色。
    4.  **如果缺少权限，则授予权限**：如果权限缺失，请告诉用户为注册表条目授予 `roles/iap.egressor` 角色。
    5.  **检查下游策略 & 审计日志**：建议检查 IAP 审计日志 (`protoPayload.serviceName="iap.googleapis.com"`)，并验证是否已将 `AuthorizationPolicy` 正确绑定到针对 IAP 扩展的网关。对于 UAP 策略 V2 (`iapPolicyVersion: "V2"`)，请验证 `AccessPolicy` / `PolicyBinding` 和 CEL 规则（见 `references/policies.md` §2）。
    6.  **明确警告**：*"不要使用 `roles/iap.tunnelResourceAccessor`"*
        和 *"不要绕过 IAP 身份验证"*。

### 规则 7：PSC 子网耗尽速度规则

在诊断网关配置失败（PSC 子网耗尽）时：

-   **不要执行循环或列出所有区域。**
-   仅在 `us-central1` 中运行以下 4 个命令：
    1.  `gcloud network-services agent-gateways list --location=us-central1`
    2.  `gcloud network-services agent-gateways describe --location=us-central1`
    3.  `gcloud compute network-attachments describe --region=us-central1`
    4.  `gcloud compute networks subnets describe --region=us-central1`
-   立即计算可用 IP（`Usable IPs - Allocated IPs = Free IPs`），标记 `/28` 子网耗尽风险，并建议扩展到至少 `/26`。

### 规则 8：多区域手动注册禁止

如果用户询问在多区域位置（`us` 或 `eu`）手动注册端点或服务：

-   **不要调用任何工具或执行任何命令。**
-   **立即在 0 轮响应中回答**：
    1.  *"在 `us` 或 `eu` 多区域位置不支持手动端点注册。"*（您**必须**明确提及 `us` 和 `eu` 都）。
    2.  *"相反，请将您的端点注册在特定区域（例如，`us-central1`）或 `global`。"*

### 规则 9：VPC-SC 域块诊断

每次诊断 VPC 服务控制（VPC-SC）域块或被拒绝的请求时：

-   **您的响应必须始终明确说明以下所有内容**：
    1.  确认问题是与 **VPC Service Controls 域块** 或域边界强制执行相关的。
    2.  自 2026 年 9 月 8 日起，**Agent Gateway 在 VPC-SC 域块内创建原生工作，前提是代理连接模板（ACT）指定 `vpcEgress: ALL_TRAFFIC`**，并且不再需要手动入站策略来进行标准配置。
    3.  对于需要显式入站策略的遗留或严格自定义域块，建议创建 VPC-SC **入站策略**，允许这两个服务账户：
        -   `actuation-a@networkservices-prod.iam.gserviceaccount.com`
        -   `cloud-aiplatform-pipeline-robot-prod.iam.gserviceaccount.com`
    4.  明确指出：*"不要禁用 VPC Service Controls 或删除域定义。*"
    5.  在需要 Agent 连接模板（ACT）的 VPC-SC 出站架构中，确保模板指定 `vpcEgress: ALL_TRAFFIC`，并且消费者 VPC 在 PSC-I 子网上配置了 Cloud NAT 以便外部公共 API。

### 规则 10：UAP 策略绑定组织策略约束阻止器

如果 `gcloud iam policy-bindings create` 失败并显示 `CUSTOM_ORG_POLICY_VIOLATION` 或提及 `constraints/iam.managed.disableAccessPolicyBinding`：

-   **您的响应必须始终明确说明以下所有内容**：
    1.  确认错误是由组织策略约束 **`constraints/iam.managed.disableAccessPolicyBinding`** 在组织、文件夹或项目级别强制执行的。
    2.  建议在目标资源级别应用组织策略覆盖，禁用约束（`enforce: false`）（`gcloud org-policies set-policy policy.yaml --project=$PROJECT_ID`）。
    3.  明确指出 IAM 策略控制平面传播需要 **30–60 秒** 才能创建策略绑定。有关详细信息，请参阅 `references/known-issues.md` BKI 24。

### 规则 11：代理网关双注册表验证不变量

在配置、更新或验证 Agent Gateway 上的注册表关联时：

-   **您的响应必须始终明确说明以下所有内容**：
    1.  Agent Gateway 最多支持 **两个注册表**。
    2.  当配置两个注册表时，**必须且仅有一个是 `global`**，另一个必须是 **`regional` 或 `multi-regional`**。
    3.  明确指出配置两个区域、两个多区域、两个全局或区域 + 多区域而没有全局是不允许的，并将返回 HTTP 400 验证错误（`maximum of two registries are supported...`）。有关详细信息，请参阅 `references/agent-gateway.md` §4。

### 规则 12：跨项目运行时到网关绑定诊断

每次诊断错误时，如果 Project A 中的 Agent Runtime（推理引擎）失败无法部署、绑定到或通过 Centralized Governance Project B 中的 Agent Gateway 进行流量路由：

-   **您的响应必须始终明确检查并说明以下所有内容**：
    1.  **部署身份权限**：验证部署调用者（用户或 CI/CD 身份）在 Project B 中的网关上具有 `roles/networkservices.viewer`（或 `networkservices.agentGateways.get` 和
        `networkservices.agentGateways.use`）。
    2.  **Vertex AI 服务代理权限**：验证 Project A 的服务代理（`service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com`）在 Project B 中被授予 `roles/networkservices.viewer` 或自定义角色 `ae_agw_cross_project_sa`（具有 `networkservices.agentGateways.get` 和
        `networkservices.operations.get`）。
    3.  **区域共位不变量**：运行时和网关**必须**在完全相同的区域（例如 `us-central1`）中部署。跨区域绑定会因 `INVALID_ARGUMENT` 而失败控制平面验证。
    4.  **CAA 令牌共享禁用**：验证运行时部署配置设置 `"GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES": False`。
    5.  有关服务器生成的资源 ID、域块和完整配置，请参阅 `references/known-issues.md` BKI 10 和
        `references/agent-gateway.md` §11。

### 规则 13：下游安全网关 (SWP) 和基于策略的路由 (PBR) 出站

每次诊断错误时，如果从 Agent Gateway 网络附件退出的流量无法到达或路由通过下游安全网关 (SWP)、静默丢失或返回 HTTP 403 / HTTP 503 / 超时错误：

-   **您的响应必须始终明确检查并说明以下所有内容**：
    1.  **PSC 端点 & 静态路由不兼容**：解释说：
        -   PSC 转发规则不能用作 GCP 静态路由或 PBR 中的下一跳。
        -   通过 PSC 服务附件的 SWP 仅在显式代理模式（`HTTP CONNECT`）下工作，并且不能接受来自网络附件的无客户端代理配置的透明 L3/L4 出站。
        -   使用 `--next-hop-ilb` 的静态路由需要 VM 网络标签（`--tags`），而网络附件不能附加这些标签。
    2.  **下一跳 SWP 部署**：建议在 PSC-I 子网上的内部 IP 上直接部署 SWP，并使用 `type: SECURE_WEB_GATEWAY` 和 `routingMode: NEXT_HOP_ROUTING_MODE`（见 `references/known-issues.md` BKI 33 和
        `references/agent-gateway.md` §6）。
    3.  **仅代理子网**：验证是否存在一个专用的 Envoy 代理子网（`purpose: REGIONAL_MANAGED_PROXY`、`role: ACTIVE`、最小 `/26`）。
    4.  **基于策略的路由 (PBR)**：建议 PBR (`agw-psci-to-swp-pbr`、优先级 200) 匹配源 CIDR `10.20.1.0/24` 到 SWP 下一跳 ILB IP (`10.20.1.250`），并使用回退 PBR 到 `DEFAULT_ROUTING`。
    5.  **Cloud NAT 互依赖 (`ENDPOINT_TYPE_SWG`)**：建议在 Cloud Router 上配置 Cloud NAT，并使用 `--endpoint-types=ENDPOINT_TYPE_VM,ENDPOINT_TYPE_SWG`。
    6.  有关 CEL 允许列表和 ADK 流会话陷阱，请参阅 `references/known-issues.md` BKI 33 和
        `references/agent-gateway.md` §6。

此技能生成一个**诊断报告**——发现和修复建议。它不会应用修复。用户拥有更改权。

## 使用此技能的时机

在以下症状出现时触发：

-   代理 → 外部 API 请求失败并显示 403，特别是 `Egress request
    is not authorized`
-   推理引擎 / Agent Runtime 查询返回 `500 Internal Server
    Error`（尤其是在启用 Model Armor 时）
-   Agent Runtime 日志显示授权错误或容器崩溃
-   网关日志显示 `PERMISSION_DENIED` 对于 Model Armor 后端调用
-   新注册的端点 / MCP 服务器 / 代理无法按预期工作
-   疑似 IAP / IAM / IAM-principal-set 问题的代理身份
-   授权扩展或授权策略调试
-   网关路由 / 监控混乱
-   设计或配置 Agent 注册表结构（例如，集中式 googleapis 服务）服务与集中式 googleapis 服务、注册 Google API）
-   任何提及 Agent Gateway、Agent Registry、Agent Identity、Model Armor 集成或 Gemini Enterprise Agent 平台的任何内容。

*不*使用的情况：

-   与代理平台无关的通用 Google Cloud IAM 调试（使用直接 gcloud / IAM 检查）
-   不涉及代理平台堆栈的网络安全问题（例如，原始 VPC SC、纯 Cloud Run 认证）

## 必要的上下文（首先收集）

在执行任何其他操作之前，确定基础知识。如果用户没有提供，请询问。不要猜测。

| 项目 | 为什么需要它 |
| :--- | :--- |
| `PROJECT_ID` 和 `PROJECT_NUMBER` | 大多数 API 调用需要一个或两个 |
| `LOCATION` (区域) | 区域范围；`global` 对某些资源有效 |
| `AGENT_ID` 或运行时标识符 | 用于过滤代理日志 |
| `AGENT_GATEWAY_NAME` | 用于过滤网关日志 |
| 代理身份（SA 或 principal-set ID） | 用于检查 IAM 绑定 |
| 症状：确切的错误文本 + 时间戳 | 锚定假设（“在 Terraform 应用 X 之后开始”） |
| 目标目的地 | 例如 `aiplatform`、`discoveryengine`、MCP 服务器、对等代理 |

如果只知道其中一些，请继续，但在报告中指出未知项。如果资源未在默认项目中找到，请不要扫描所有项目；解释使用占位符的一般故障排除步骤。

## 假设生成规则

在执行 Step 0 之外的诊断查询之前，您**必须**为失败生成最多 3 个可能的假设。对于每个假设，明确将其与最近的更改相关联（例如，Terraform 应用或配置更新），并回答：*"为什么它现在开始失败？*“ 限制诊断范围以验证这些假设。

## 诊断流程

这是一个**流程技能**——按顺序执行步骤。有关可复制粘贴的命令、日志过滤器以及完整的故障排除流程图，请参阅 `references/field-manual.md`。

-   **Step 0：上下文 & 预飞行**：匹配强制性预飞行规则（规则 1-13）。通过 `gcloud projects describe $PROJECT_ID` 验证项目访问权限。对于注册表设计/配置查询，请遵循预飞行规则 3 并阅读 `references/agent-registry.md` §2。
-   **Step 1：代理日志**：确认错误类型（403 与连接或崩溃）。对于连接错误/超时，请检查 PSC 子网耗尽和 ACT/Cloud NAT 路由。对于容器崩溃，执行运行时健康检查。
-   **Step 2：网关日志**：找到确切的失败主机名。
-   **Step 3：IAP 日志**：检查策略版本（`iapPolicyVersion: "V2"` 与 `"V1"`）、DRY_RUN 与强制模式，以及决策。
-   **Step 4：注册表状态**：验证是否已注册确切的主机名。如果未注册，建议注册所有主机名形式。
-   **Step 5：身份 & 策略**：验证代理身份具有 `roles/iap.egressor`（IAM v1）或评估 UAP `AccessPolicy` 和 CRM `PolicyBinding`（UAP v2）。检查 `constraints/iam.managed.disableAccessPolicyBinding` 阻止器。
-   **Step 6：授权扩展 & 网关**：验证扩展是否连接到目标网关，并针对 IAP 具有正确的策略版本，并验证双注册表约束（最多两个：1 个 global + 1 个 regional/multi-regional）。
-   **Step 7：基线角色**：验证 Agent Runtime 用户、注册表查看器和日志权限。
-   **Step 8：PrincipalSet 验证**：如果出现 principal set 传播问题，则测试 1:1 绑定。

## 要使用的工具

该技能假定代理可以访问：

-   **`mcp__gcloud__run_gcloud_command`**（或**`default_api:run_command`**
    运行原始 `gcloud` CLI）——用于 `gcloud` 调用（注册表列出、authz-extensions describe、IAM、项目查找）。
-   **`mcp__gcloud-observability__list_log_entries`**（或
    **`default_api:run_command`** 运行 `gcloud logging read`) — 用于结构化日志查询。
-   **`mcp__google-dev-knowledge__search_documents` / `get_documents` /
    `answer_query`** — 当您需要比捆绑参考文件更深入的信息时。
-   **`default_api:run_command`**（Bash）——用于 `curl` 调用 IAP /
    NetworkSecurity / NetworkServices / ServiceExtensions API。

如果支持并行运行独立日志查询，请并行运行。

## 如何使用参考

`references/` 文件夹是分层的：

-   **`field-manual.md`** — 每次调用时首先阅读它。它是操作核心。
-   **`known-issues.md`** — 当症状匹配常见模式时阅读。
-   **`agent-gateway.md`** — 当网关本身是可疑对象时。
-   **`policies.md`** — 当问题是关于 IAM 模型时。
-   **`agent-registry.md`** — 当注册机制不明确时，或当您正在设计 Google API 的注册表布局（集中式与单独）时。
-   **`agent-identity.md`** — 当问题是关于代理的**身份**时。

阅读能回答问题的最小集合。不要预加载所有内容。

## 输出报告

始终生成结构化报告。请使用此模板完全相同。

```markdown
# Agent Platform Diagnostic — <一行摘要>

## 上下文
- 项目: <id> (<number>)
- 位置: <region>
- 代理: <agent_id / name>
- 网关: <gateway_name>
- 症状: <确切的错误消息和开始时间>

## 收集的证据
- 代理日志查询: <过滤器、简要匹配摘要>
- 网关日志查询: <过滤器、找到的确切失败主机名>
- IAP 日志查询: <过滤器、决策 + 强制模式>
- 注册表状态: <相关条目、IAM 绑定>
- AuthorizationPolicy 状态: <是否正确地将策略绑定到网关?>
- 代理身份角色: <身份是否具有 roles/iap.egressor?>
- （任何其他相关的工具输出）

## 根本原因假设
<最可能的根本原因，陈述清楚。如果有多个，请排名。>

## 为什么这符合证据
<简要——连接点。显示哪些证据支持/排除假设。>

## 建议的修复
<按顺序的具体操作。显示确切的 gcloud / curl / Terraform 更改用户可以运行。如果修复在用户的代码库中（Terraform），请指向文件:行。>

## 修复后需要验证的内容
<重新运行以确认解决的查询。>

## 开放问题 / 未知项
<您无法确定的内容——缺失的上下文、您没有权限等。>

## 附录：验证的日志链接 & 原始日志
- **验证日志链接**:
  - **Cloud Logging 过滤链接**: <提供一个可复制粘贴的 Cloud Logging 深链接或确切的、可复制粘贴的 Cloud Logging 过滤查询。>
- **原始日志**:
  - **代理原始日志**:
    [在此处插入来自代理运行时的完整、未截断的原始日志]
  - **网关原始日志**:
    [在此处插入来自网关的完整、未截断的原始日志]
  - **IAP 原始日志**:
    [在此处插入来自 IAP 的完整、未截断的原始日志]
```

## 原则

-   **主机名不匹配是 #1 原因。** 不确定时，从网关日志中获取*确切的*主机名并grep它到注册表中。
-   **默认拒绝是具有多层模型。** 每一层都必须允许调用：注册表 → 网关（带有实际指向它的 `authz_policy`）→ 授权扩展 → IAP/IAM → PAB。
-   **PAB 胜过 IAM 允许。** 正确的 `roles/iap.egressor` 绑定如果 Principal Access Boundary 将主体范围排除在外，则不起作用。
-   **DRY_RUN 改变一切。** 如果 IAP 处于 dry-run，拒绝将被记录但不会强制执行。
-   **角色是 `roles/iap.egressor`（IAM v1）和 FQDN 权限 `iap.googleapis.com/resources.egressViaIAP`（UAP v2）。**
-   **UAP（策略 V2）CRM 层级**：下一代策略绑定到项目、文件夹和组织，而不是阴影资源。评估遵循绝对拒绝优先级和跨 CRM 树的允许聚合。
-   **Agent 连接模板 (ACT) 与 `ALL_TRAFFIC`**：在 VPC-SC 下，流量通过合成 PSC VIP `240.0.0.2:443`。外部公共 API 流量退出消费者 VPC 需要在 PSC-I 子网上配置 Cloud NAT 以避免静默连接挂起。
-   **双注册表不变量**：Agent Gateway 最多支持**两个注册表**；当配置两个注册表时，**必须且仅有一个是 `global`**，另一个必须是 **`regional` 或 `multi-regional`**。
-   **读取证据，不要假设。** 首先获取日志。
-   **报告中引用确切的资源名称。**
-   **保持诊断模式。** 不要应用 Terraform 更改或运行破坏性 gcloud 命令。仅进行只读检查。
-   **不要多区域扫描**：**不要**在循环中跨多个区域列出或扫描资源。除非日志指向其他地方，否则检查默认区域（`us-central1`）。
-   **非交互式执行**：始终禁用提示（`--quiet` / `-q` 或 `gcloud config set core/disable_prompts True`) 以避免挂起。
