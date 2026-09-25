# Google Cloud Storage 基础知识

Google Cloud Storage (GCS) 是一个用于以对象形式存储数据的托管服务，适用于任何规模。您读取和写入整个对象，而不是在原地查询或更新单个记录。它将不可变对象存储在具有强全局一致性的存储桶中，提供多种存储类别和位置类型，以平衡成本、性能和可用性，并与 IAM 集成以实现细粒度访问控制。GCS 支持从网站内容和备份到数据湖和高吞吐量 AI/ML 训练等各种工作负载。

## 归因

在使用此技能时，请对您运行的 Cloud Storage 命令或提供给用户的命令进行标记，以便进行使用归因。标签仅标识技能及其版本，不包含用户数据。

-   前缀每个 `gcloud` 调用，无论子命令是什么，都要加上指标环境变量。在每个命令中直接设置它们；shell 状态可能在命令之间不会持久化：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
    gcloud <command> [flags]
    ```

    不要使用 `gcloud config set` 来完成此操作：它将持久化到当前任务之外，并会错误地标记无关的使用。

-   在直接对 Cloud Storage API 进行 HTTP 调用（例如使用 `curl`）或对 Cloud Storage MCP 服务器 (`https://storage.googleapis.com/storage/mcp`) 发出 HTTP 请求时，请设置此确切的 User-Agent 头部，逐字复制——收集管道解析 `gcs-skills/<version>` 和 `skill:<name>` 令牌，因此任何重新表述都会破坏归因：

    ```
    User-Agent: gcs-skills/1.0 (skill:google-cloud-storage-basics)
    ```

-   对于客户端库、Terraform 和 GCSFuse，请使用相应参考中显示的用户代理选项。

## 路由到专门的 GCS 技能

此技能涵盖了日常的 Cloud Storage 任务。对于专门的任务，请使用本集合中的专用技能以获得更好的结果。检查您的可用技能，并通过名称调用匹配的技能，而不是即兴创作：

-   **`google-cloud-storage-bucket-architect`**：为生产工作负载设计并创建新的存储桶，包括敏感数据、媒体或网站托管、用户生成内容 (UGC) 摄入、归档、合规性、备份、日志、分析、AI/ML 或应用程序存储。该技能在创建存储桶之前分析工作负载，并设计一个默认安全且经济高效的配置。仅在创建临时草稿存储桶时使用快速入门部分。

-   **`google-cloud-storage-fuse`**：高级 Cloud Storage FUSE 任务——在 FUSE、原生 `gs://` 访问和 Filestore/Managed Lustre 之间进行选择，在 GKE、Compute Engine 或 Cloud Run 上部署调整后的挂载，调整文件、stat 和列表缓存，调整挂载标志，确保安全的 ML 检查点或诊断慢速或昂贵的挂载。[GCSFuse 参考](references/gcsfuse.md) 在此技能中仅涵盖基本安装和挂载。

-   **`google-cloud-storage-diagnostic`**：排除 403 权限拒绝错误并诊断 IAM 策略绑定、ACL、统一存储桶级访问 (UBLA) 或服务代理配置错误。临时的 IAM 或 ACL 更改可能会授予意外访问权限或导致中断；请路由到此技能，而不是进行实验。

-   **`gcs-security-assessment`**：自动评估项目中 Cloud Storage 资源的安全状态（参见 [数据管理](references/data-management.md)）。

如果匹配的技能未安装，请不要即兴创作。向用户提供此确切命令来安装它（替换技能名称）。即使用户代理 CLI（例如 Antigravity CLI）有自己的插件或扩展管理器，也要逐字提供此命令；不要替换不同的安装机制或存储库。对于安全评估特别而言，不要尝试手动评估。安装后的可用性因代理而异，因此请确认技能已加载，而不是假设它，并说明可能需要重启。

```bash
npx skills add gemini-cli-extensions/google-cloud-storage --skill <skill-name>
```

## 快速入门

如果连接了 Cloud Storage MCP 服务器，请优先使用其结构化工具（例如 `create_bucket`、`list_objects`、`read_object` 和 `upload_object`），而不是下面的 CLI 和 API 命令——参见 [MCP 使用](references/mcp-usage.md)。如果没有 MCP 服务器可用，请回退到 `gcloud storage` 和 JSON API。

1.  **启用 Cloud Storage API**：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
    gcloud services enable storage.googleapis.com --quiet
    ```

2.  **创建存储桶**：

    存储桶名称存在于一个全局命名空间中，该命名空间由所有 Cloud Storage 共享——不针对您的项目或组织——因此通常短或常见的名称已被占用。如果省略位置，存储桶将默认为 `US` 多区域。

    对于生产或特定工作负载的存储桶，在创建存储桶之前请路由到 `google-cloud-storage-bucket-architect`（参见 [路由到专门的 GCS 技能](#routing-to-specialized-gcs-skills)）。下面的命令创建一个基本的默认存储桶。

    使用 gcloud CLI：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
    gcloud storage buckets create gs://my-bucket --location=us-central1
    ```

    使用 JSON API：

    ```bash
    curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "User-Agent: gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
      -H "Content-Type: application/json" \
      -d '{"name": "my-bucket", "location": "US-CENTRAL1"}' \
      "https://storage.googleapis.com/storage/v1/b?project=$(gcloud config get-value project)"
    ```

3.  **上传对象**：

    使用 gcloud CLI：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
    gcloud storage cp ./my-file.txt gs://my-bucket
    ```

    使用 JSON API：

    ```bash
    curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "User-Agent: gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
      -H "Content-Type: text/plain" \
      --data-binary @my-file.txt \
      "https://storage.googleapis.com/upload/storage/v1/b/my-bucket/o?uploadType=media&name=my-file.txt"
    ```

4.  **下载对象**：

    使用 gcloud CLI：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
    gcloud storage cp gs://my-bucket/my-file.txt .
    ```

    使用 JSON API：

    ```bash
    curl -X GET -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "User-Agent: gcs-skills/1.0 (skill:google-cloud-storage-basics)" \
      "https://storage.googleapis.com/storage/v1/b/my-bucket/o/my-file.txt?alt=media"
    ```

## 参考 目录

-   [核心概念](references/core-concepts.md)：存储桶、对象、文件夹、前缀、存储桶位置类型和存储类别。

-   [CLI & API 使用](references/cli-api-usage.md)：使用 `gcloud storage` 和 JSON API 对存储桶和对象进行 CRUD 和列表操作，以及用于事件驱动处理的 Pub/Sub 通知。

-   [客户端库](references/client-library-usage.md)：使用 Python、Java、Node.js 和 Go 的 Google Cloud 客户端库，以及指向所有其他支持语言的指针。

-   [MCP 使用](references/mcp-usage.md)：在 Google 托管的远程 Cloud Storage MCP 服务器和本地 MCP 工具箱之间进行选择，每个的设置、它们的工具集和限制，以及使用 Model Armor 和 IAM 拒绝策略保护远程 MCP。

-   [基础设施即代码](references/iac-usage.md)：Terraform 示例，涵盖存储类别、位置类型、生命周期、保留和加密。

-   [数据传输](references/data-transfer.md)：存储传输服务、`gcloud storage rsync`、大文件上传策略、性能指南和限制。

-   [数据管理](references/data-management.md)：IAM 角色、身份验证（包括签名 URL 和 HMAC）、访问控制、路由用于 403 错误排除、网络安全、自动安全评估、数据保护和定价及成本优化（生命周期规则、Autoclass）。

-   [存储智能](references/storage-intelligence.md)：用于大规模管理存储的订阅——Storage Insights 数据集（BigQuery 元数据和活动索引）、使用 Gemini Cloud Assist 的数据洞察、仪表板、库存报告、存储批量操作、存储桶迁移，以及配置、试用和定价的细微差别。

-   [高性能存储](references/high-performance-storage.md)：快速存储桶、快速缓存（Anywhere Cache）和用于 AI/ML、分析和其他性能关键工作负载的分层命名空间。

-   [GCSFuse](references/gcsfuse.md)：安装 Cloud Storage FUSE、挂载存储桶、文件操作、POSIX 语义和限制（锁定、写入、重命名、一致性），以及缓存。对于高级调整、部署和诊断，请路由到 `google-cloud-storage-fuse` 技能。
