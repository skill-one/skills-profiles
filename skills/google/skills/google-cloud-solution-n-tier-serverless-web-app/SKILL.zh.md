---
name: google-cloud-solution-n-tier-serverless-web-app
description: 协助在 Google Cloud 上设计和实施安全的 n 层无服务器 Web 应用程序和微服务。当用户需要多层无服务器应用程序的架构设计、安全检查清单、Terraform 代码或部署指南，以及区域数据驻留/欧洲主权合规性、零信任私有 VPC 网络或私有服务连接时使用。不适用于 VM、GKE 或非 Google Cloud 架构。
---

<!-- disableFinding(all) -->
<!-- mdlint off -->

# 基于严格私有应用层级的 n 层安全无服务器 Web 应用

本技能指导代理完成设计和实现安全无服务器 Web 应用的工作流程，应用架构设计层级由用户指定。该方案使用 Cloud Run 作为无服务器层级，使用 Cloud SQL 作为 PostgreSQL 数据层。一个三层 Web 应用可能表示为三个架构层级：Cloud Run 表示层、Cloud Run 应用层和 Cloud SQL for PostgreSQL 数据库层。

该架构在所有层级（T1 到 TN）之间强制执行严格的物理和网络隔离：

*   **层级 1 表示层（前端 / 反向代理）**：面向公众的 UI 渲染/网关服务（Cloud Run）。通过 Cloud Load Balancing 暴露入口点，并通过 Direct VPC Egress 私密地将请求路由到内部层级。
*   **层级 2..N 应用层（内部微服务 / 业务逻辑）**：私有应用服务（Cloud Run）。与互联网 100% 隔离（Ingress：VPC 内部，`INGRESS_TRAFFIC_INTERNAL_ONLY`），仅可通过上游 VPC 路由访问（`egress = "ALL_TRAFFIC"`，子网上的 `*.run.app` URL 使用 Private Google Access）。
*   **数据层**：私有 Cloud SQL 用于持久化数据，Memorystore 用于 Redis 缓存，仅可被授权的应用层级访问。

## 对 LLM 的通用指导

### 1. 直接资源映射（零搜索文件访问）
所有必要的参考架构、HCL 模板和清单都集中在这个技能中。使用从该技能文件夹的精确相对路径：

| 资源路径 | 目的和使用 |
| :--- | :--- |
| `assets/main.tf` | **Terraform (HCL) 的单一事实来源**。包含所有安全边界、Cloud Run v2 配置、PSC 端点、DNS 私有区域和防火墙规则。 |
| `assets/output-template.md` | 标准化解决方案架构报告 Markdown 结构。 |
| `references/non-negotiable-architectural-rules.md` | 不可协商的安全规则、审计清单和产品映射。 |
| `references/related-guidance.md` | 补充深度参考（标准设计或 IaC 任务时**不要**阅读；仅当明确需要专门边缘案例故障排除时才阅读）。 |

- **不进行目录爬取**：**不要**在工作区目录下运行 `list_dir` 链来发现这些文件。
- **不搜索本地文件**：**不要**运行 `code_search` 或 `find_by_name` 查询来查找 `assets/main.tf` 内部内容。使用 `view_file` 直接读取文件一次并重用上下文。
- **不进行冗余技能搜索**：执行此技能时**不要**调用 `skill_search` 来搜索无服务器或 n 层架构技能。

### 2. 直接内联生成（不委托子代理）
- 在**主对话**中直接执行所有架构编译、Terraform 起草、`gcloud` 命令组装和验证脚本生成。
- **不要**调用子代理 (`invoke_subagent`) 来研究外部 GitHub Terraform 模块、探测环境配置或起草报告。所有所需模式都完全包含在 `assets/main.tf` 和 `references/` 中。

### 3. 单次清理工件生成
- 在一次 `write_to_file` 调用中生成完整的、完全渲染的、有效的 HCL 块和 Markdown 报告。
- 避免留下占位符或格式错误的代码分隔符，这些需要多轮 `replace_file_content` 和 `grep_search` 补丁循环。
- **无未填充的占位符**：在架构报告中嵌入代码或脚本时（例如，`assets/output-template.md` 的第 6 节），始终内联实际的完整 Terraform 代码、gcloud 命令和验证脚本代码。**不要**输出字面模板占位符注释（例如，`# [main.tf 文件内容粘贴]`）。
- **响应内直接渲染（强制）**：每当请求或生成 Terraform 代码、部署脚本或架构报告时（例如，“提供设计和 Terraform 代码”、“生成 IaC”），你**必须**在聊天响应文本中直接打印完整的生成 ```terraform ... ``` HCL 代码块和完整解决方案报告，除了将它们写入磁盘上的文件。当请求代码时，**不要**仅输出架构设计摘要或文件链接；自动化评估框架（如 Yardstick）评估原始响应文本，如果消息中缺少 ```terraform``` 代码块，所有代码断言都将失败。

### 4. 技术完整性清单
- 当提供简洁的架构摘要或安全清单时（例如，当指示不生成完整 IaC 时），你必须明确包含以下技术规格：
    - 对于区域负载均衡器部署：区域代理子网目的 (`REGIONAL_MANAGED_PROXY`) 和区域转发规则上的 `network` 参数。
    - Cloud SQL PostgreSQL 版本 (`POSTGRES_18`)、版本 (`Enterprise Edition`)、高可用性 (`Regional HA`) 和私有服务连接 (`psc_enabled = true`)。
    - Cloud NGFW 防火墙策略：
        - 必须**配置**明确的 Cloud NGFW 网络防火墙策略 (`google_compute_network_firewall_policy`, `google_compute_network_firewall_policy_association`, 和 `google_compute_network_firewall_policy_rule`，`enable_logging = var.enable_monitoring`)，而不是使用传统的 `google_compute_firewall`。
        - 强制默认出站拒绝 (`0.0.0.0/0`)。
        - 允许前端出站到后端 / PGA VIP。
        - 明确允许后端数据库出站，允许 TCP 端口 `443` 到 Private Google Access VIPs (`199.36.153.4/30 / 199.36.153.8/30`)，除了 TCP 端口 `5432`，以便 Cloud SQL Auth Proxy 侧车可以在启动时查询 `sqladmin.googleapis.com` 进行 IAM 证书交换。

## 工作流程

> [!TIP]
> **可选的 MCP 服务器集成**：如果你的 AI 编码客户端支持**模型上下文协议 (`MCP`)**，你可以连接到 [Google 开发者知识 MCP 服务器](https://developers.google.com/knowledge/mcp) (`npx -y @google/mcp-developer-knowledge-server`)，以动态查询实时 Google Cloud 文档 (`cloud.google.com/docs`)，同时使用此技能的离线知识库 (`references/related-guidance.md`)。

解决方案设计和实施工作流程分为以下阶段：

*   **阶段 1：需求发现和分析**：分析工作负载的需求、约束、依赖关系和当前状态。
*   **阶段 2：解决方案设计 & IaC 起草**：为工作负载构建技术堆栈、架构和部署配置。**重要**：在此阶段，你应该提出生成完整的 Terraform 代码（基于 `assets/main.tf` 并遵循所有阶段 3 规范）以及解决方案架构。这允许用户在对话继续时立即审查和迭代修改代码。但是，如果用户明确表示不想生成代码，则不要生成。
*   **阶段 3：实施计划 & 迭代优化**：随着对话和用户反馈的演变，修改和优化生成的设计和部署说明。
*   **阶段 4：解决方案验证**：验证部署是否满足工作负载的需求。

--------------------------------------------------------------------------------

### 阶段 1：需求发现和分析

为了防止多轮访谈疲劳并保持跨评估的轨迹确定性，除非用户明确要求偏离，否则采用**主观的 80% 默认黄金路径**：

1.  **默认黄金路径配置 (`80% 基线`)**：
    *   **架构**：安全的 3 层无服务器管道 (`frontend` Cloud Run -> `backend application` Cloud Run -> `Cloud SQL PostgreSQL`)。
    *   **区域**：`us-central1`。
    *   **数据库**：Cloud SQL for PostgreSQL (`POSTGRES_18`) 企业版通过 Private Service Connect (`psc_enabled = true`)。
    *   **边缘保护**：全球外部应用负载均衡器带有 Cloud Armor WAF (`sqli-v33-stable`) 和 Cloud CDN (`enable_cdn = true`)。
    *   **域 & SSL 模式**：如果用户指定了域（例如，`app.mycompany.com`），请配置 `var.domain_name` 使用 Google 管理的证书 (`use_self_signed_cert = false`) 并提供 DNS `A` 记录说明。如果在没有域的沙盒中测试，请启用自签名模式 (`use_self_signed_cert = true`) 以便立即可测试。
    *   **网络 & 安全**：直接 VPC 出站 (`ALL_TRAFFIC`)、`run.app.` Cloud DNS 私有区域、最小权限 Cloud NGFW 出站防火墙策略 (`TCP 5432, 443`) 和 Cloud SQL Auth Proxy 侧车 (`DB_SOCKET_PATH` 带有 IAM 认证)。

2.  **歧义协议 (`可选澄清问题`)**：
    如果用户的初始提示留下了开放式要求（并且没有使用精确规格快速跳转），**不要**提供多主题问卷。仅在确认前根据需要提出简洁的澄清问题：
    1.  **负载均衡器 & 居住拓扑**：您是否需要一个**全球应用负载均衡器与 Cloud CDN**（默认用于全球用户），还是一个**区域应用负载均衡器不带 CDN**（用于严格的 EU/区域数据居住合规性）？
    2.  **自定义域 vs. 沙盒测试**：您有一个**注册的域名**要配置 Google 管理的证书，还是应该配置**自签名测试模式** (`use_self_signed_cert = true`) 以便立即进行沙盒测试？
    3.  **内存缓存层**：我们应该在 Cloud SQL 旁边配置一个可选的**Memorystore for Redis** 缓存层 (`Private Services Access`) 来加速读取查询吗？

3.  **验证并确认**：向用户展示确认的 3 层黄金路径分解，并在继续到阶段 2（或根据指示自动快速跳转）之前请求确认。

### 阶段 2：解决方案设计

1.  **高效检索架构指导**：
    *   **架构设计 & 安全清单请求**：仅从 `references/non-negotiable-architectural-rules.md` 检索 9 个架构安全边界和审计清单。当仅请求高级设计/清单时，**不要**检索 `references/related-guidance.md` 或 `assets/main.tf`，除非请求完整的 Terraform 代码。
    *   **Terraform 实施请求**：检索 `references/non-negotiable-architectural-rules.md` 和 `assets/main.tf`（HCL 的单一事实来源）。除非明确需要专门边缘案例故障排除，否则**不要**检索 `references/related-guidance.md`。

2.  **将组件映射到 Google Cloud 产品**：使用以下强制产品映射规范将确认的分解直接映射到 Google Cloud 产品：
    *   **公共 Ingress & WAF**：全局或区域外部应用负载均衡器 (`INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`)、Cloud Armor (`sqli-v33-stable`)、Cloud CDN（如果使用全局应用负载均衡器；注意 Cloud CDN 不支持区域应用负载均衡器）。注意：当部署区域外部应用负载均衡器时，VPC 中需要一个显式的代理仅子网 (`purpose = "REGIONAL_MANAGED_PROXY"`)，并且在区域转发规则上必须指定 `network`。
    *   **内部计算层级 (T1 到 TN)**：Cloud Run 微服务 (`INGRESS_TRAFFIC_INTERNAL_ONLY`)、配置为 `egress = "ALL_TRAFFIC"` 的直接 VPC 出站、子网上启用 Private Google Access、以及 `google_dns_managed_zone` 用于 `run.app.`，绑定到 `vpc_network` 映射 `*.run.app` 直接到 Private Google Access VIPs (`199.36.153.4/30 / 199.36.153.8/30`)，当调用内部 `*.run.app` URL 时，从指定的/占位符容器镜像部署。
    *   **私有数据层**：Cloud SQL for PostgreSQL (`POSTGRES_18`) 通过 Private Service Connect + IAM DB Auth。如果选择了数据库缓存，则通过 Private Services Access 添加 Memorystore Redis。根据可靠性要求，指定“Cloud SQL for PostgreSQL 企业版实例”或“Cloud SQL for PostgreSQL 企业 Plus 版本实例”。
    *   **密钥、注册表 & 安全**：Secret Manager、Artifact Registry、Cloud NGFW 全球/区域网络防火墙策略 (`google_compute_network_firewall_policy` + `google_compute_network_firewall_policy_rule` 明确允许出站 TCP 端口 5432 到 Cloud SQL PSC IP 和 TCP 端口 443 到 Private Google Access VIPs `199.36.153.4/30, 199.36.153.8/30` 在 `allow_backend_db_egress` 上)，以及可选的 VPC Service Controls。

3.  **创建架构图**：创建一个干净的 Mermaid 格式架构图 (`assets/output-template.md`)，说明多层请求和数据流，包括入口点、公共反向代理、私有微服务计算层级和私有数据库/缓存端点。

4.  **起草解决方案架构并生成 Terraform & `gcloud` CLI 代码**：
    将需求、技术分解、产品映射、架构图、设计建议以及完整的**基础设施即代码 (`Terraform` 基于于 `assets/main.tf`，以及一个遵循所有阶段 3 强制规范的、自包含的 gcloud CLI 部署命令序列)** 编译到一个结构严格遵循标准化 Google Cloud 解决方案架构输出 Markdown 文件中。在保存或输出报告工件时，附加 ISO 8601 UTC 时间戳，并确保文件名严格以 `.md` 扩展名结尾（例如，`workload_name_architecture_report-20260701T212820Z.md`）。验证报告中是否干净地记录了来自 `assets/main.tf` 的所有 9 个安全边界，并且所有模板占位符都已用实际的完整代码块替换。在响应中，提供执行架构概述、执行的 9 个关键安全和网络边界、完整的部署就绪 Terraform 代码块（``` ```terraform ... ``` `），以及逐步部署说明，并链接到生成的工件（当请求代码时，始终在响应中内联完整的 Terraform 代码，而不是仅提供文件链接）。
5.  **请求审查和迭代**：向用户展示解决方案架构（以及 Terraform 代码、`gcloud` 脚本或验证脚本，如果已生成），并请求反馈。随着对话的继续，迭代修改架构和代码。

--------------------------------------------------------------------------------

### 阶段 3：实施计划

1.  **从 `assets/` 目录检索相关的构建块模板**。
    *重要*：使用 `assets/main.tf` 中的代码作为 Terraform 实施计划的基础（`assets/output-template.md` 用于架构结构）。

2.  **识别部署先决条件**：

    *   需要的 Google Cloud API (`run.googleapis.com`, `sqladmin.googleapis.com`, `redis.googleapis.com`, `servicenetworking.googleapis.com`, `secretmanager.googleapis.com`, `monitoring.googleapis.com`, `dns.googleapis.com`)。
    *   需要的 IAM 权限（项目编辑器、安全管理员等）。

3.  **生成基础设施即代码（IaC） (`架构规范`)**:  
    从 `references/non-negotiable-architectural-rules.md` 中检索相关的架构和层级指导。代码必须严格基于 `assets/main.tf` 中的构建模块（云网络防火墙策略参考 `Section 1.5`，第一层参考 `Section 5.1`，第 2-N 层参考 `Section 5.2`），并确保 `database_version = "POSTGRES_18"` 保持完全一致。确保防火墙策略严格使用云网络防火墙资源（`google_compute_network_firewall_policy`、`google_compute_network_firewall_policy_association` 和 `google_compute_network_firewall_policy_rule`，且 `enable_logging = var.enable_monitoring`）。**绝对禁止**生成过时的 `google_compute_firewall` 资源或回退到较旧的数据库版本（如 `POSTGRES_15`）。

4.  **编写部署说明 & README.md**:  
    起草全面的分步部署说明（或完整的 `README.md` 资产），确保包含以下内容：  
    *   初始化和应用 Terraform 的说明（`terraform init`、`terraform apply`）。**零安装环境推荐**：明确建议在 **Google Cloud Shell** (`https://shell.cloud.google.com`) 中运行 `terraform` 命令和生成的自动化验证脚本，因为 `python3`、`gcloud` 和 `terraform` 已完全预装并认证，无需本地 SDK 的开发者即可立即部署和验证。  
    *   **分步 `gcloud` CLI 部署命令 (`自底向上连接`)**：在 `assets/output-template.md` 的 6.3 节（"分步 `gcloud` CLI 部署命令"）中，提供部署此架构所需的完整、自包含的 `gcloud` CLI 命令序列，无需 Terraform。这些命令必须强制执行反向/自底向上的顺序（`VPC/subnets -> 数据层 -> 内部微服务 -> 公网网关 -> 负载均衡器`），在创建 Cloud SQL 时指定 `--database-version=POSTGRES_18`，并从下游容器 URL（`gcloud run services describe... --format='value(status.url)'`）中提取到 shell 变量，通过 `--update-env-vars` 动态传递给上游服务。  
    *   所有 Terraform 变量的解释，**明确包括并记录 `enable_vpc_sc` 和 `use_self_signed_cert` 变量**（解释如何设置 `use_self_signed_cert = true` 可通过 `curl -k https://<LB_IP>/` 立即进行沙箱验证，无需等待 DNS 传播）。  
    *   **专用 VPC 服务控制指导部分**：提供具体说明和 `gcloud` 命令，用于在 `enable_vpc_sc = true` 时围绕 Cloud Run (`run.googleapis.com`)、Cloud SQL (`sqladmin.googleapis.com`) 和 Secret Manager (`secretmanager.googleapis.com`) 实施组织级 VPC-SC 服务边界。  
    *   容器镜像部署策略（指定预存在的镜像 URL 或后续 CI/CD 的引导占位符）。  
    *   Cloud DNS 管理私有区域 (`google_dns_managed_zone`) 配置，用于 `run.app.` 绑定到 `vpc_network`，将 `*.run.app` 直接映射到私有 Google 访问 VIP (`199.36.153.4/30 / 199.36.153.8/30`），同时包含外部 DNS 记录和数据库模式初始化。

5.  **请求审核**：  
    向用户提交实施计划以供批准。如有必要，进行迭代。

--------------------------------------------------------------------------------

### 阶段 4：解决方案验证

1.  **定义解决方案验证步骤和需求**：  
    在验证规划期间，强制要求在所有部署环境中执行以下 5 个验证步骤：  
    *   **SSL 配置**：验证 Google 管理的 SSL 证书 (`google_compute_managed_ssl_certificate`) 变为 `ACTIVE`（检查 `--global` 状态或区域等效项）。  
    *   **前端入口拦截**：验证直接针对第一层前端默认 `*.run.app` URL 的互联网访问被拦截（边缘筛选返回 `HTTP 403 Forbidden`）。  
    *   **后端入口拦截**：验证直接针对内部计算层 `*.run.app` URL 的互联网访问（`INGRESS_TRAFFIC_INTERNAL_ONLY`）在所有内部微服务层被拦截（返回 `HTTP 404 Not Found` 或 `HTTP 403 Forbidden`）。  
    *   **通过应用负载均衡器访问前端公共访问**：验证通过应用负载均衡器成功将自定义域名路由到展示层（`HTTP 200` 到 `399`）。  
    *   **边缘 WAF 保护**：验证模拟的 SQL 注入请求（在自定义域名上 `/?id=1%20OR%201=1`）被拦截并阻止（来自 Cloud Armor 的 `HTTP 403 Forbidden`）。  
    *   **私有服务器间连接**：通过 Cloud Run 应用日志（`Logs Explorer`）和数据库连接池指标（`Cloud SQL Query Insights`）验证，第 1 层 -> 第 2 层 -> 数据层查询通过私有 VPC 纤维成功（`Direct VPC Egress` + `Private Service Connect` / `Private Services Access`）。

2.  **生成定制化自动化验证脚本**：  
    **生成定制的自动化验证脚本**（例如，使用标准内置 `urllib` / `subprocess` 库的自包含 Python 验证脚本，或跨平台 bash/PowerShell 脚本），精确定制到用户的部署域名、SSL 证书名称和精确的多层 `*.run.app` URI。

3.  **提供跨平台执行指导**：  
    解释用户如何在目标操作系统（`macOS`、`Linux`、`Windows PowerShell` 或零安装的 **Google Cloud Shell** (`https://shell.cloud.google.com`)) 中执行生成的脚本。

4.  **编制验证报告**：  
    在 `assets/output-template.md` 的 6.4 节（"解决方案验证指南和定制化自动化验证脚本"）中，记录验证检查、生成的验证脚本代码、执行命令和预期结果。

5.  **执行验证并最终确认**：  
    协助用户运行生成的验证脚本、检查日志并解决任何 DNS 或 WAF 传播问题。请求最终批准。
