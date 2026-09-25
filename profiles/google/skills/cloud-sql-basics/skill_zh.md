# Cloud SQL 基础知识

Cloud SQL 是一种完全托管的用于 MySQL、PostgreSQL 和 SQL Server 的关系型数据库服务。它自动化了补丁、更新、备份和副本等耗时任务，同时为您的应用程序提供高性能和可用性。

## 前置条件

确保您拥有创建和管理 Cloud SQL 实例所需的 IAM 权限。**Cloud SQL 管理员** (`roles/cloudsql.admin`) 角色提供对 Cloud SQL 资源的完全访问权限。

## 快速入门 (PostgreSQL)

1.  **启用 API:**
    
    ```bash
    gcloud services enable sqladmin.googleapis.com --quiet
    ```

2.  **创建实例:**
    
    ```bash
    gcloud sql instances create INSTANCE_NAME \
      --database-version=POSTGRES_18 \
      --cpu=2 \
      --memory=7680MiB \
      --region=REGION \
      --quiet
    ```

3.  **为默认用户设置密码:**

    由于这是一个 Cloud SQL for PostgreSQL 实例，默认的管理用户是 `postgres`：
    
    ```bash
    gcloud sql users set-password postgres \
      --instance=INSTANCE_NAME --password=PASSWORD \
      --quiet
    ```

4.  **创建数据库:**
    
    ```bash
    gcloud sql databases create DATABASE_NAME \
      --instance=INSTANCE_NAME \
      --quiet
    ```

5.  **获取实例连接名称:**

    您需要实例连接名称（其格式为 `PROJECT_ID:REGION:INSTANCE_NAME`）才能使用 Cloud SQL Auth Proxy 连接。使用以下命令检索它：
    
    ```bash
    gcloud sql instances describe INSTANCE_NAME \
      --format="value(connectionName)" \
      --quiet
    ```

6.  **连接到实例:**

    Cloud SQL Auth Proxy 必须正在运行才能连接到实例。在另一个终端中，使用连接名称启动代理：
    
    ```bash
    ./cloud-sql-proxy INSTANCE_CONNECTION_NAME
    ```

    代理运行后，在另一个终端中使用 `psql` 连接：
    
    ```bash
    psql "host=127.0.0.1 port=5432 user=postgres dbname=DATABASE_NAME password=PASSWORD sslmode=disable"
    ```

## 参考 目录

-   [核心概念](references/core-concepts.md)：Cloud SQL 版本（企业版 & 企业版 Plus）、实例架构、读池、高可用性 (HA) 和支持的数据库引擎。

-   [CLI 使用](references/cli-usage.md)：用于实例、数据库和用户管理的 `gcloud sql` 命令。

-   [客户端库和连接器](references/client-library-usage.md)：使用 Python、Java、Node.js 和 Go 连接到 Cloud SQL。

-   [MCP 使用](references/mcp-usage.md)：使用 Cloud SQL 远程 MCP 服务器和 Gemini CLI 扩展。

-   [基础设施即代码](references/iac-usage.md)：用于实例、数据库和用户的 Terraform 配置。

-   [IAM 与安全](references/iam-security.md)：预定义角色、SSL/TLS 证书和 Auth Proxy 配置。

-   [灾难恢复与备份](references/dr-backups.md)：备份类型、点时间恢复 (PITR)、副本、读池比较和企业版 Plus 高级灾难恢复。

*如果您需要在这些参考中找不到的产品信息，请使用开发者知识 MCP 服务器 `search_documents` 工具。*
