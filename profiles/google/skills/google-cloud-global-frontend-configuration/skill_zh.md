# Google Cloud 全球外部应用负载均衡器配置技能

## 目的与代理指导

该技能使代理能够引导用户通过一个结构化的、6步发现流程来设计和部署 Google Cloud 全球外部应用负载均衡器（包括 Cloud CDN、Cloud Armor 和服务扩展）。

**假设与目标环境：**
- 该技能假设它是在可以执行 Google Cloud CLI (`gcloud`) 的环境（如 Gemini CLI、Antigravity 等）中调用的。
- 如果 `gcloud` 不可用或无法访问，该技能无法执行自动资源发现或管理部署操作。在这种情况下，该技能将将其支持限制为引导设计和生成 Terraform HCL 配置。

执行此技能时，代理必须：
- 使用实际的 Google Cloud 产品名称将用户工作负载需求映射到简化的、基于意见的最佳实践配置。
- 逐步披露详细信息，除非用户明确要求自定义，否则隐藏高级复杂性。
- 利用 `references/` 目录中的参考文档执行资源发现、代码生成、操作和漂移检测。

## 6步配置流程

### 第 1 步：基础信息

*   **项目发现：** 参考 `references/resource-discovery.md` 自动检测 Google Cloud 项目 ID。向用户展示发现的该项目 ID。
*   向用户询问其负载均衡器的基础信息：
    *   **名称与描述：** 我们应该如何命名此负载均衡器？
    *   **协议选择：** 他们需要 HTTP、HTTPS 还是两者都需要？
    *   **证书管理：** 他们想使用 Google 管理的证书还是自带现有证书？

### 第 2 步：源配置

帮助用户通过严格顺序的、分步循环定义其后端工作负载。不要一次性询问所有内容。所有步骤都是强制的。

*   **子步骤 A - 源设置：** 询问他们是否有单个源或需要多源支持。等待响应。
*   **子步骤 B - 源类型：** 要求他们从以下选项中选择后端类型：Cloud Storage 存储桶、Compute Engine 管理实例组 (MIGs)、Google Kubernetes Engine (GKE) 集群、Cloud Run 服务或外部/互联网源（IP/FQDN）。等待响应。
*   **子步骤 C - 源定义循环：** 对子步骤 B 中选择的每个源类型，按顺序执行以下循环。等待用户回答一个源后再询问下一个源：
    *   **资源发现：** 对于 Google Cloud 本地源（Cloud Storage、MIGs、GKE、Cloud Run），参考 `references/resource-discovery.md` 获取资源。从 **1. 创建新**、**2. 无** 开始展示列表。对于外部/互联网源，只需询问 FQDN/IP。
    *   **工作负载类型（关键）：** 在他们定义资源后，立即询问正在提供的工作负载类型：
        1.  **静态图像/对象**（静态内容、图像、视频、样式资源）
        2.  **可缓存 API**（只读、公共 API，其中缓存数据是可以接受的）
        3.  **不可缓存 API / 事务**（事务端点、登录、结账、账户更改）
        4.  **动态 Web (SSR)**（动态页面、服务器端渲染应用、自定义动态会话）
*   **子步骤 D - 路由规则：** 一旦所有源都已逐一完全定义，询问流量应如何在这些源之间路由（基于路径、基于头部或基于查询参数）。等待响应。
*   **子步骤 E - 日志记录：** 建立路由后，询问他们是否要启用 Cloud CDN 日志记录，以及如果启用，采样率是多少（0-100%）。等待响应。

### 第 3 步：流量管理与可扩展性

*   提供第 2 步中定义的源和路由规则的简要总结。
*   询问他们是否需要启用高级流量管理设置（如粒度加权负载均衡、流量镜像或 **Cloud Load Balancing 服务扩展**用于自定义 WASM 插件/调用），或者他们想继续使用 **Google Cloud 最佳实践配置**。

### 第 4 步：缓存（Cloud CDN）

根据第 2 步的工作负载类型完全提出“推荐配置”。除非他们拒绝推荐并想进行自定义，否则不要列出高级设置（TTL、缓存键、压缩）。

*   **如果工作负载 = 静态图像/对象：**
    *   缓存模式：缓存所有静态
    *   TTL：客户端（1 天 / 86400 秒）、默认（30 天 / 2592000 秒）、最大（365 天 / 31536000 秒）——平衡静态资产的长期缓存卸载与周期性重新验证。
    *   缓存键：协议 + 主机 + 路径（忽略查询字符串）
    *   压缩：启用（Brotli & Gzip）
    *   负面缓存：启用
    *   允许陈旧服务：启用
*   **如果工作负载 = 可缓存 API：**
    *   缓存模式：使用源头
    *   TTL：由源管理（从配置中省略以防止错误）
    *   缓存键：协议 + 主机 + 路径 + 包含查询字符串
    *   压缩：启用（Gzip）
    *   负面缓存：启用
    *   允许陈旧服务：禁用
*   **如果工作负载 = 不可缓存 API / 事务：**
    *   缓存模式：禁用（CDN 跳过）
*   **如果工作负载 = 动态 Web (SSR)：**
    *   缓存模式：使用源头
    *   TTL：由源管理（从配置中省略以防止错误）
    *   缓存键：协议 + 主机 + 路径
    *   压缩：启用（Brotli & Gzip）
    *   缓存绕过：如果存在会话 Cookie（例如 SESSID、JWT），则绕过缓存

### 第 5 步：安全（Cloud Armor）

根据第 2 步的工作负载类型完全提出“推荐配置”。除非请求，否则隐藏高级保护（Bot 管理、威胁情报、地理屏蔽）。

*   **如果工作负载 = 静态图像/对象：**
    *   速率限制：无（标准边缘行为；Cloud Armor 边缘策略不支持 Cloud Storage 存储桶的速率限制）。
    *   OWASP 保护：禁用
*   **如果工作负载 = 可缓存 API：**
    *   速率限制：每客户端 IP 每分钟 100 个请求（标准基线，以防止 API 滥用和 DDoS，同时适应正常交互使用）。
    *   OWASP 保护：启用（SQLi、XSS、本地文件包含）
*   **如果工作负载 = 不可缓存 API / 事务：**
    *   速率限制：每客户端 IP 每分钟 30 个请求（严格阈值，以保护登录/结账等敏感事务端点免受凭证注入和暴力攻击）。
    *   OWASP 保护：启用（SQLi、XSS、远程命令执行、会话固定）
    *   Bot 管理与威胁情报：启用（阻止恶意 Bot 和已知恶意 IP）
*   **如果工作负载 = 动态 Web (SSR)：**
    *   速率限制：每客户端 IP 每分钟 120 个请求（宽阈值，以适应初始页面加载和 SSR Web 应用中的资产注入的突发请求）。
    *   OWASP 保护：启用（SQLi、XSS、CSRF、Shellshock）
    *   地理屏蔽：可选（限制/允许特定国家访问）

### 第 6 步：审查与部署

*   **配置摘要：** 生成一个完整的、格式化的 markdown 表格，显示第 1 步到第 5 步的所有最终设置，使用 Google Cloud 产品名称。遵循以下精确的模板结构：

    | 组件 | 参数/设置 | 值与理由 |
    | :--- | :--- | :--- |
    | **负载均衡器** | 名称与协议 | `<Name>` (HTTP/HTTPS) |
    | **源** | 后端与工作负载 | `<Backend 1>` (`<Workload Type>`), `<Backend 2>`... |
    | **流量管理** | 路由规则 | `<路径 / 头部规则或默认>` |
    | **Cloud CDN** | 缓存模式与 TTL | `<缓存模式>`，默认 TTL: `<TTL>` |
    | **Cloud Armor** | 速率限制与 OWASP | `<RPM 限制>`，OWASP 规则: `<启用/禁用>` |
    | **服务扩展**| WASM / 调用 | `<启用/禁用或 N/A>` |

*   **下一步操作：** 询问用户选择他们的部署/生成格式（Terraform HCL 或 gcloud CLI Bash 脚本）以及他们的下一步操作：
    1.  **显示代码 / 脚本**（显示 HCL 代码或 gcloud bash 脚本。显示后，提供 **下载** 或 **部署/执行** 的选项）
    2.  **下载文件**（将 `main.tf` 或 `deploy.sh` 保存到本地工作区）
    3.  **部署配置：** 通过 Infrastructure Manager 启动部署或执行 gcloud 脚本。这应使用 `references/managed-deployment.md` 中的部署说明来完成。

---

## 相关文档与支持链接

- [Cloud Load Balancing 概述](https://cloud.google.com/load-balancing/docs/load-balancing-overview)
- [Cloud CDN 文档](https://cloud.google.com/cdn/docs)
- [Cloud Armor 文档](https://cloud.google.com/armor/docs)
- [Cloud Load Balancing 服务扩展](https://cloud.google.com/service-extensions/docs/overview)
- [Infrastructure Manager 概述](https://cloud.google.com/infrastructure-manager/docs)
- [官方 Terraform LB-HTTP 模块](https://registry.terraform.io/modules/GoogleCloudPlatform/lb-http/google/latest)
- [官方 Terraform Cloud Armor 模块](https://registry.terraform.io/modules/GoogleCloudPlatform/cloud-armor/google/latest)
