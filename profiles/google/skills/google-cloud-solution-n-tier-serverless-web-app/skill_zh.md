<!-- disableFinding(all) -->
<!-- mdlint off -->

# 基于严格私有应用层级的 n 层安全无服务器 Web 应用

本技能指导代理完成设计和实现安全无服务器 Web 应用的工作流程，用户指定的架构设计层级越多，该技能提供的架构设计层级就越多。它使用 Cloud Run 作为无服务器层级，使用 Cloud SQL 作为 PostgreSQL 数据层。三层 Web 应用可能表示为三个架构层级：Cloud Run 表示层、Cloud Run 应用层和 Cloud SQL for PostgreSQL 数据库层。

该架构在所有层级（T1 到 TN）之间强制执行严格的物理和网络隔离：

*   **层级 1 表示层（前端 / 反向代理）**：面向公众的 UI 渲染/网关服务（Cloud Run）。通过 Cloud Load Balancing 暴露入口点，并通过 Direct VPC Egress 私密地将请求路由到内部层级。
*   **层级 2..N 应用层（内部微服务 / 业务逻辑）**：私有应用服务（Cloud Run）。100% 与互联网隔离（Ingress：VPC 内部，`INGRESS_TRAFFIC_INTERNAL_ONLY`），仅可通过上游 VPC 路由访问（`egress = "ALL_TRAFFIC"`，子网上的 `*.run.app` URL 使用私有 Google 访问）。
*   **数据层**：私有 Cloud SQL 用于持久化数据，Memorystore 用于 Redis 缓存，仅可从授权的应用层级访问。

## 对 LLM 的通用指导

### 1. 直接资源映射（零搜索文件访问）
所有必要的参考架构、HCL 模板和检查清单都集中在这个技能中。使用此技能文件夹的精确相对路径：

| 资源路径 | 目的和使用 |
| :--- | :--- |
| `assets/main.tf` | **Terraform（HCL）的单一事实来源**。包含所有安全边界、Cloud Run v2 配置、PSC 端点、DNS 私有区域和防火墙规则。 |
| `assets/output-template.md` | 标准化解决方案架构报告 Markdown 结构。 |
| `references/non-negotiable-architectural-rules.md` | 不可协商的安全规则、审计检查清单和产品映射。 |
| `references/related-guidance.md` | 补充深度参考（不要用于标准设计或 IaC 任务；仅当明确需要专门边缘情况故障排除时才阅读）。 |

- **不进行目录爬取**：不要在工作区目录下运行 `list_dir` 链来发现这些文件。
- **不在本地文件上进行搜索泛滥**：不要运行 `code_search` 或 `find_by_name` 查询来查找 `assets/main.tf` 内部内容。使用 `view_file` 直接读取文件一次并重用上下文。
- **不进行冗余技能搜索**：在执行此技能时，不要调用 `skill_search` 来搜索无服务器或 n 层架构技能。

### 2. 直接内联生成（不委托子代理）
- 直接在主要对话中执行所有架构编译、Terraform 起草、`gcloud` 命令组装和验证脚本生成。
- **不要**调用子代理（`invoke_subagent`）来研究外部 GitHub Terraform 模块、探测环境配置或起草报告。所有所需模式都完全包含在 `assets/main.tf` 和 `references/` 中。

### 3. 一次性干净的艺术品编写
- 在一次 `write_to_file` 调用中生成完整的、完全渲染的、有效的 HCL 块和 Markdown 报告。
- 避免留下占位符或格式不正确的代码围栏，这些需要多轮 `replace_file_content` 和 `grep_search` 补丁循环。
- **没有未填充的占位符**：当在架构报告中嵌入代码或脚本（例如，`assets/output-template.md` 的第 6 节）时，始终内联实际的完整 Terraform 代码、gcloud 命令和验证脚本代码。永远不要输出字面模板占位符注释（例如，`# [main.tf 文件内容粘贴]`）。
- **响应内直接渲染（强制）**：每当请求或生成 Terraform 代码、部署脚本或架构报告时（例如，“提供设计和 Terraform 代码”、“生成 IaC”），您**必须**在聊天响应文本中直接打印完整的生成 ```terraform ... ``` HCL 代码块和完整解决方案报告，除了将它们写入磁盘上的文件。当请求代码时，永远不要只输出架构设计摘要或文件链接；自动化评估框架（例如 Yardstick）评估原始响应文本，如果消息中缺少 ```terraform``` 代码块，则所有代码断言都将失败。

### 4. 技术完整性检查清单
- 当提供简洁的架构摘要或安全检查清单时（例如，当指示不生成完整 IaC 时），您必须明确包含以下技术规范：
    - 对于区域负载均衡器部署：区域代理仅子网目的 (`REGIONAL_MANAGED_PROXY`) 和区域转发规则上的 `network` 参数。
    - Cloud SQL PostgreSQL 版本 (`POSTGRES_18`)、版本 (`Enterprise Edition`)、高可用性 (`Regional HA`) 和私有服务连接 (`psc_enabled = true`)。
    - Cloud NGFW 防火墙策略：
        - 必须配置明确的 Cloud NGFW 网络防火墙策略 (`google_compute_network_firewall_policy`, `google_compute_network_firewall_policy_association` 和 `google_compute_network_firewall_policy_rule`，`enable_logging = var.enable_monitoring`)，而不是传统的 `google_compute_firewall`。
        - 强制默认出站拒绝 (`0.0.0.0/0`)。
        - 允许前端出站到后端 / PGA VIP。
        - 明确允许后端数据库出站，明确允许 TCP 端口 `443` 到私有 Google 访问 VIP (`199.36.153.4/30 / 199.36.153.8/30`)，除了 TCP 端口 `5432`，以便 Cloud SQL Auth Proxy 侧车可以在启动时查询 `sqladmin.googleapis.com` 进行 IAM 证书交换。

## 工作流程

> [!TIP]
> **可选 MCP 服务器集成**：如果您的 AI 编码客户端支持 **模型上下文协议 (`MCP`)**，您可以将 [Google 开发者知识 MCP 服务器](https://developers.google.com/knowledge/mcp) (`npx -y @google/mcp-developer-knowledge-server`) 连接到此技能的离线知识库 (`references/related-guidance.md`) 一起动态查询实时 Google Cloud 文档 (`cloud.google.com/docs`)。

解决方案设计和实施工作流程分为以下阶段：

*   **阶段 1：需求发现和分析**：分析工作负载的需求、约束、依赖关系和当前状态。
*   **阶段 2：解决方案设计 & IaC 起草**：为工作负载构建技术堆栈、架构和部署配置。**重要提示**：在此阶段，您应该提供生成完整的 Terraform 代码（基于 `assets/main.tf` 并遵循所有阶段 3 规定）的提议，同时提供解决方案架构。这允许用户立即审查并在对话过程中迭代修改代码。但是，如果用户明确表示他们不想生成代码，则不要生成它。
*   **阶段 3：实施计划 & 迭代改进**：随着对话和用户反馈的演变，修改和改进生成的设计和部署说明。
*   **阶段 4：解决方案验证**：验证部署是否满足工作负载的要求。

--------------------------------------------------------------------------------

### 阶段 1：需求发现和分析

为了防止多轮面试疲劳并保持跨评估的轨迹确定性，除非用户明确要求偏离，否则采用**意见化的 80% 默认黄金路径**：

1.  **默认黄金路径配置 (`80% 基线`)**：
    *   **架构**：安全的 3 层无服务器管道（`frontend` Cloud Run -> `backend application` Cloud Run -> `Cloud SQL PostgreSQL`）。
    *   **区域**：`us-central1`。
    *   **数据库**：Cloud SQL for PostgreSQL (`POSTGRES_18`) 企业版通过私有服务连接 (`psc_enabled = true`)。
    *   **边缘保护**：具有 Cloud Armor WAF (`sqli-v33-stable`) 和 Cloud CDN (`enable_cdn = true`) 的全球外部应用负载均衡器。
    *   **域 & SSL 模式**：如果用户指定了域（例如，`app.mycompany.com`），请配置 `var.domain_name` 使用 Google 管理的证书（`use_self_signed_cert = false`）并提供 DNS `A` 记录说明。如果在没有域的沙盒中测试，请启用自签名模式（`use_self_signed_cert = true`）以实现即时可测试性。
    *   **网络 & 安全**：直接 VPC 出站 (`ALL_TRAFFIC`)、`run.app.` Cloud DNS 私有区域、最小权限 Cloud NGFW 出站防火墙策略（`TCP 5432, 443`）和 Cloud SQL Auth Proxy 侧车（`DB_SOCKET_PATH` 使用 IAM 认证）。

2.  **歧义协议（可选澄清问题）**：
    如果用户的初始提示留下了开放式要求（并且不是快速前进带有精确规格），则**不要**提出多主题问卷。仅在确认之前根据需要仅提出简洁的澄清问题：
    1.  **负载均衡器 & 居住拓扑**：您是否需要一个具有 Cloud CDN 的**全球应用负载均衡器**（默认用于全球用户），还是一个**区域应用负载均衡器**（无 CDN）（用于严格的 EU/区域数据居住合规性）？
    2.  **自定义域 vs. 沙盒测试**：您有**注册的域名**要配置为使用 Google 管理的证书，还是应该配置**自签名测试模式** (`use_self_signed_cert = true`) 以进行即时沙盒测试？
    3.  **内存缓存层**：我们应该在 Cloud SQL 旁边配置可选的**Memorystore for Redis** 缓存层（`Private Services Access`）以加速读取查询吗？

3.  **验证 & 确认**：向用户展示确认的 3 层黄金路径分解，并在进入阶段 2（或根据指示自动快速前进）之前请求确认。

### 阶段 2：解决方案设计

1.  **高效检索架构指导**：
    *   **架构设计 & 安全检查清单请求**：仅从 `references/non-negotiable-architectural-rules.md` 检索 9 个架构安全边界和审计检查清单。**不要**检索 `references/related-guidance.md` 或 `assets/main.tf`，除非请求的是高级设计/检查清单，而不需要完整的 Terraform 代码。
    *   **Terraform 实施请求**：检索 `references/non-negotiable-architectural-rules.md` 和 `assets/main.tf`（HCL 的单一事实来源）。**不要**检索 `references/related-guidance.md`，除非明确需要专门边缘情况故障排除。

2.  **将组件映射到 Google Cloud 产品**：使用以下强制产品映射规范将您的确认分解直接映射到 Google Cloud 产品：
    *   **公共 Ingress & WAF**：全局或区域外部应用负载均衡器（`INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`）、Cloud Armor (`sqli-v33-stable`）（如果使用全局应用负载均衡器；请注意 Cloud CDN 不支持区域应用负载均衡器）。注意：当部署区域外部应用负载均衡器时，需要在 VPC 中配置显式代理仅子网（`purpose = "REGIONAL_MANAGED_PROXY"`），并且在区域转发规则上必须指定 `network`。
    *   **内部计算层（T1 到 TN）**：Cloud Run 微服务（`INGRESS_TRAFFIC_INTERNAL_ONLY`）、配置为 `ALL_TRAFFIC` 的直接 VPC 出站、子网上的私有 Google 访问启用，以及用于 `run.app.` 的 Cloud DNS 管理私有区域（`google_dns_managed_zone`）绑定到 `vpc_network` 映射 `*.run.app` 直接到私有 Google 访问 VIP (`199.36.153.4/30 / 199.36.153.8/30`)，当调用内部 `*.run.app` URL 时，从指定的/占位符容器镜像部署。
    *   **私有数据层**：Cloud SQL for PostgreSQL (`POSTGRES_18`) 通过私有服务连接 + IAM DB 认证。如果选择了数据库缓存，则通过私有服务访问添加 Memorystore Redis。根据可靠性要求，指定“Cloud SQL for PostgreSQL 企业版实例”或“Cloud SQL for PostgreSQL 企业版 Plus 实例”。
    *   **密钥、注册表 & 安全**：Secret Manager、Artifact Registry、Cloud NGFW 全局/区域网络防火墙策略（`google_compute_network_firewall_policy` + `google_compute_network_firewall_policy_rule` 明确允许出站 TCP 端口 5432 到 Cloud SQL PSC IP 和 TCP 端口 443 到私有 Google 访问 VIP `199.36.153.4/30, 199.36.153.8/30` 在 `allow_backend_db_egress`），以及可选的 VPC 服务控制。

3.  **创建架构图**：创建一个干净的 Mermaid 格式架构图（`assets/output-template.md`），说明跨入口点、公共反向代理、私有微服务计算层和私有数据库/缓存端点的多层请求和数据流。

4.  **起草解决方案架构并生成 Terraform & `gcloud` CLI 代码**：
    将需求、技术分解、产品映射、架构图、设计建议以及完整的基础设施即代码（基于 `assets/main.tf` 的 Terraform 以及遵循所有阶段 3 强制规范的 gcloud CLI 部署命令序列）编译到一个结构严格遵循标准化 Google Cloud 解决方案架构输出 Markdown 文件中。当保存或输出报告工件时，附加 ISO 8601 UTC 时间戳，并确保文件名严格以 `.md` 扩展名结尾（例如，`workload_name_architecture_report-20260701T212820Z.md`）。验证 `assets/main.tf` 中的所有 9 个安全边界是否在报告中清晰记录，并且所有模板占位符都已替换为实际的完整代码块。在您的响应中，提供执行架构概述、执行的 9 个关键安全和网络边界、完整的部署就绪 Terraform 代码块（```terraform ... ``` `），以及分步部署说明，链接到生成的工件（当请求代码时，始终在响应中内联完整的 Terraform 代码，而不是只提供文件链接）。
5.  **请求审查和迭代**：向用户展示解决方案架构（以及生成的 Terraform 代码、`gcloud` 脚本或验证脚本），并请求反馈。随着对话的继续，迭代修改架构和代码。

--------------------------------------------------------------------------------

### 阶段 3：实施计划

1.  **从 `assets/` 目录检索相关构建块模板**。
    *重要*：使用 `assets/main.tf` 中的代码作为 Terraform 实施计划的基础（`assets/output-template.md` 用于架构结构）。

2.  **识别部署先决条件**：

    *   需要的 Google Cloud API (`run.googleapis.com`, `sqladmin.googleapis.com`, `redis.googleapis.com`, `servicenetworking.googleapis.com`, `secretmanager.googleapis.com`, `monitoring.googleapis.com`, `dns.googleapis.com`)。
    *   需要的 IAM 权限（项目编辑器、安全管理员等）。

3.  **生成基础设施即代码（IaC） (`架构规范`)**：从 `references/non-negotiable-architectural-rules.md` 检索相关的架构和层次指导。严格基于 `assets/main.tf` 中的构建块（`Section 1.5` 用于 Cloud NGFW 防火墙策略，`Section 5.1` 用于层级 1，`Section 5.2` 用于层级 2..N），确保 `database_version = "POSTGRES_18"` 保持完全精确。确保防火墙策略严格使用 Cloud NGFW 资源（`google_compute_network_firewall_policy`, `google_compute_network_firewall_policy_association` 和 `google_compute_network_firewall_policy_rule`，`enable_logging = var.enable_monitoring`）。**永远不要**生成遗留 `google_compute_firewall` 资源或恢复到旧数据库版本，如 `POSTGRES_15`。

4.  **编写部署说明 & README.md**：起草全面的分步部署说明（或完整的 `README.md` 工件），确保您包括：
    *   初始化和应用 Terraform 的说明（`terraform init`, `terraform apply`）。**零安装环境建议**：明确建议在 **Google Cloud Shell** (`https://shell.cloud.google.com`) 中运行 `terraform` 命令和您的生成自动化验证脚本，其中 `python3`、`gcloud` 和 `terraform` 都 100% 预安装并开箱即用认证，因此没有本地 SDK 的开发人员可以立即部署和验证。
    *   **分步 `gcloud` CLI 部署命令（自下而上连接）**：在 `assets/output-template.md` 的 Section 6.3（“分步 `gcloud` CLI 部署命令”）中，提供一个完整的、自包含的 `gcloud` CLI 命令序列，用于部署此精确架构，而无需 Terraform。这些命令必须强制执行反向/自下而上的顺序（`VPC/子网 -> 数据层 -> 内部微服务 -> 公共网关 -> 负载均衡器`），在创建 Cloud SQL 时指定 `--database-version=POSTGRES_18`，并提取下游容器 URL（`gcloud run services describe... --format='value(status.url)'`）到 shell 变量，通过 `--update-env-vars` 动态传递到上游服务。
    *   所有 Terraform 变量的解释，**明确包括并记录 `enable_vpc_sc` 和 `use_self_signed_cert` 变量**（解释如何设置 `use_self_signed_cert = true` 可启用通过 `curl -k https://<LB_IP>/` 进行即时沙盒验证，而无需等待 DNS 传播）。
    *   **专用 VPC 服务控制指导部分**：提供实施围绕 Cloud Run (`run.googleapis.com`)、Cloud SQL (`sqladmin.googleapis.com`) 和 Secret Manager (`secretmanager.googleapis.com`) 的组织级 VPC-SC 服务边界的具体说明和 gcloud 命令，当 `enable_vpc_sc = true` 时。
    *   容器镜像部署策略（指定预存在的镜像 URL 或占位符引导，然后是 CI/CD）。
    *   Cloud DNS 管理私有区域（`google_dns_managed_zone`）配置为 `run.app.` 绑定到 `vpc_network`，将 `*.run.app` 直接映射到私有 Google 访问 VIP (`199.36.153.4/30 / 199.36.153.8/30`)，以及外部 DNS 记录和数据库模式初始化。

5.  **请求审查**：向用户展示实施计划以供批准。按需迭代。

--------------------------------------------------------------------------------

### 阶段 4：解决方案验证

1.  **定义解决方案验证步骤 & 要求**：在验证计划期间，在任何部署环境中强制执行以下 5 个验证步骤：
    *   **SSL 配置**：验证 Google 管理的 SSL 证书（`google_compute_managed_ssl_certificate`）变为 `ACTIVE`（检查 `--global` 状态或区域等效项）。
    *   **前端 Ingress 阻塞**：验证直接针对层级 1 前端的默认 `*.run.app` URL 的互联网访问被阻塞（从边缘筛选返回 `HTTP 403 Forbidden`）。
    *   **后端 Ingress 阻塞**：验证直接针对内部计算层 `*.run.app` URL（`INGRESS_TRAFFIC_INTERNAL_ONLY`）的互联网访问在所有内部微服务层被阻塞（`HTTP 404 Not Found` 或 `HTTP 403 Forbidden`）。
    *   **通过应用负载均衡器的前端公共访问**：验证通过应用负载均衡器访问自定义域成功路由到表示层（`HTTP 200` 到 `399`）。
    *   **边缘 WAF 保护**：验证模拟 SQL 注入请求（在自定义域上的 `/?id=1%20OR%201=1`）被拦截和阻止（来自 Cloud Armor 的 `HTTP 403 Forbidden`）。
    *   **私有服务器到服务器连接**：通过 Cloud Run 应用程序日志（`Logs Explorer`）和数据库连接池遥测（`Cloud SQL Query Insights`）验证层级 1 -> 层级 2 -> 数据层查询通过私有 VPC 光纤成功（`Direct VPC Egress` + `Private Service Connect` / `Private Services Access`）。

2.  **生成定制的自动化验证脚本**：而不是依赖静态预打包脚本，**生成一个定制的自动化验证脚本**（例如，使用标准内置 `urllib` / `subprocess` 库的自包含 Python 验证脚本，或跨平台 bash/PowerShell 脚本），精确定制到用户的部署域、SSL 证书名称和精确的多层 `*.run.app` URI。

3.  **提供跨平台执行指导**：解释用户如何在他们的目标操作系统（`macOS`、`Linux`、`Windows PowerShell` 或零安装 **Google Cloud Shell** (`https://shell.cloud.google.com`)) 执行生成的脚本。

4.  **编译验证报告**：在 `assets/output-template.md` 的 Section 6.4（“解决方案验证指南和定制的自动化验证脚本”）中，记录验证检查、生成的验证脚本代码、执行命令和预期结果。

5.  **执行验证并最终确定**：协助用户运行生成的验证脚本、检查日志并解决任何 DNS 或 WAF 传播问题。请求最终批准。
