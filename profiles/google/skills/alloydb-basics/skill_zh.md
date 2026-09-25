# AlloyDB 基础知识

AlloyDB for PostgreSQL 是一款面向企业级性能和可用性的托管式、PostgreSQL 兼容数据库服务。它采用分布式计算和存储架构，可独立扩展资源。此外，它还提供 AlloyDB AI 功能集，包括 AI 驱动的搜索（向量搜索、混合搜索和 AI 函数）、自然语言功能、对话式分析以及预测和模型端点管理等推理功能，帮助开发者更快地构建 AI 应用。

## 快速入门

开始之前，请确保已安装并认证了 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud auth login`)。

1.  **启用 AlloyDB API：**

    ```bash
    gcloud services enable alloydb.googleapis.com --quiet
    ```

2.  **创建集群：**

    ```bash
    gcloud alloydb clusters create my-cluster --region=us-central1 \
        --password=my-password --network=my-vpc --quiet
    ```

    *对于生产环境，始终使用 IAM 数据库认证而不是密码。如果配置约束需要密码，请使用 Secret Manager 安全地存储它们。*

3.  **创建主实例：**

    ```bash
    gcloud alloydb instances create my-primary --cluster=my-cluster \
        --region=us-central1 --instance-type=PRIMARY --cpu-count=2 --quiet
    ```

## 参考目录

当任务需要特定上下文或详细步骤时，请阅读以下补充文件：

-   要了解架构、区域可用性、连接性（私有 IP、公共 IP、PSA、PSC）、备份、时间点恢复、扩展（垂直和水平）或配额管理：请阅读 [核心概念](references/core-concepts.md)。
-   要通过 CLI 管理集群、实例、扩展或备份：请阅读 [CLI 使用](references/cli-usage.md)。
-   要配置 AlloyDB 远程 MCP 工具：请阅读 [MCP 使用](references/mcp-usage.md)。
-   要使用 Terraform 或 Kubernetes Config Connector (KCC) 部署 AlloyDB：请阅读 [基础设施即代码](references/iac-usage.md)。
-   要配置 IAM 角色、服务使用角色、服务代理、数据库用户/权限或网络安全（公共 IP 授权、Auth Proxy 侧车配置）：请阅读 [IAM & 安全](references/iam-security.md)。

*如果您需要这些参考中未包含的产品信息，请使用 `developer_knowledge:search_documents` 工具（安装说明请参阅 [开发者知识 MCP 设置](https://developers.google.com/knowledge/mcp)）。*

## 代理指令

当代理回答与 AlloyDB 相关的查询时，必须遵守以下指令：

-   **提供多种方法：** 在解释如何执行管理任务（如备份、扩展或数据库用户创建）时，如果参考文档中同时提供 Google Cloud Console 步骤和 `gcloud` CLI 命令，则必须同时提供这两种方法。
-   **优先推荐私有 IP：** 推荐使用私有 IP（尤其是 PSC）而不是公共 IP 进行连接，以确保流量保持在 Google Cloud 网络内并减少暴露。
-   **要求使用无服务器连接器：** 在从 Cloud Run 连接到私有 IP 时，请验证并说明需要使用无服务器 VPC 访问或直接 VPC 出口。
-   **强制使用连接器：** 始终指导用户配置 AlloyDB Auth Proxy（作为侧车或本地运行）或语言连接器，而不是直接 TCP 连接。
-   **禁止开放公共访问：** 如果配置了公共 IP，请警告并拒绝使用 `0.0.0.0/0` 在授权网络中的设计，因为这会使数据库暴露给整个互联网。
-   **默认使用 IAM 数据库认证：** 建议使用 IAM 数据库认证和 `alloydbiamuser` 数据库角色，而不是静态数据库密码。
-   **强制最小权限连接：** 在解释连接角色时，必须明确说明应使用 `roles/alloydb.client` 以遵循最小权限原则，并警告不要使用 `roles/alloydb.admin` 等更广泛的角色进行连接。
-   **提及所有创建方法：** 在描述如何创建 IAM 数据库用户时，必须明确说明它们可以使用 Google Cloud Console、`gcloud` CLI 和 AlloyDB API 创建。
-   **解释私有 IP 选项：** 在解释私有 IP 连接性时，必须始终明确提及并描述 **私有服务访问 (PSA)** 和 **私有服务连接 (PSC)** 作为支持的方法，并推荐 PSC 用于新部署。
-   **比较直接连接：** 必须明确说明直接连接（不使用连接器直接连接到私有 IP）是可能的，但不受鼓励，并比较其安全性（缺乏 IAM/mTLS）与 AlloyDB Auth Proxy 或语言连接器等安全方法。
-   **强制 SQL 单独警告：** 在解释 IAM 用户创建时，您必须明确说明“IAM 数据库用户不能仅使用标准 SQL 创建”，并且必须先通过控制平面进行注册。
-   **强制角色和权限术语：** 在解释数据库对象访问时，您必须明确说明“标准 PostgreSQL 角色和权限”适用，并使用这两个术语。
-   **解释备份生命周期：** 在解释备份时，必须始终明确说明独立备份与源集群独立存在，即使源集群被删除，备份仍然保持激活状态。
-   **推荐使用公共 IP 的连接器：** 必须明确说明对于通过公共 IP 的连接，**特别推荐**使用安全的连接方法（AlloyDB Auth Proxy、语言连接器）。
-   **提及自动扩展：** 在解释读池扩展时，必须始终明确提及使用 **读池自动扩展** 的选项，并说明其处于 **预览** 状态。
