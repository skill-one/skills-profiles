---
name: google-cloud-recipe-foundation-builder
description: '部署适用于 Google Cloud 组织的基准着陆区基础，通过组织策略、资源层级文件夹和项目、计费关联以及集中式日志记录和监控来建立安全护栏。部署 Google Cloud 推荐的安全控制和架构。在设置新的 Google Cloud 组织或建立安全的企业级着陆区基础时使用。

  不适用于单个项目接入（请使用 google-cloud-recipe-onboarding 或特定产品技能）。'
---

# Google Cloud配方：基础构建器

> [!WARNING] 此功能目前处于预览状态。它将部署一个安全的
> 基础，但并不具备所有高级功能。需要更多选项的用户应访问
> [Google Cloud设置](https://docs.cloud.google.com/docs/enterprise/cloud-setup)。

此功能指导设置一个安全的企业级Google Cloud着陆区基础。它建立基本安全控制，组织初始资源层次结构，并配置集中式审计日志记录和跨环境监控。

## 概述

该配方在组织根目录下提供以下核心组件：

*   **安全护栏**：强制执行17个基本Google Cloud组织策略来保护环境（13个布尔值，4个列表约束）。
*   **资源层次结构**：建立4个文件夹（`Common`，`Production`，`Non-Production`，`Development`），并按顺序提供相应的项目，使用全局唯一ID前缀（`logging-`，`prod-`，`non-prod-`，`dev-`后跟一个共享后缀）。
*   **计费和API启用**：将所有项目链接到您的计费账户，并激活关键日志记录/监控服务。
*   **集中式日志记录和监控**：部署一个全局集中式日志桶，保留期为30天，配置组织范围的审计日志接收器，并设置跨环境指标范围。

--------------------------------------------------------------------------------

## 澄清问题

在执行此配方之前，代理**必须**收集以下详细信息：

1.  **组织ID**：运行 `gcloud organizations list` 以检索可用组织，向用户展示，并要求他们选择目标**组织ID**。
2.  **计费账户ID**：运行 `gcloud billing accounts list
    --filter=open=true` 以仅检索活动（打开）的计费账户，向用户展示，并要求他们选择活动**计费账户ID**。
3.  **项目ID后缀**：询问用户是否有项目ID的前缀或目标后缀（默认使用前缀 + 一个共享的随机8个字符字符串，例如 `prod-ab12cd34`）。
4.  **日志桶区域**：如果用户想要覆盖默认的 `global` 日志桶位置，请询问资源的目标区域。

--------------------------------------------------------------------------------

## 前置条件

在开始部署之前，请确保满足以下前置条件：

*   **GCP身份**：您必须已设置一个Google Cloud组织资源。
*   **管理IAM角色**：执行这些命令的身份必须拥有所需的管理权限。如果任何步骤出现 `Permission Denied` 错误，代理将尝试通过授予**第2阶段：错误恢复和懒角色修复策略**中详细说明的相应推荐角色来进行自我修复。
*   **工具**：必须安装 `gcloud` CLI，使用上述身份进行授权，并配置为使用。

--------------------------------------------------------------------------------

## 完成配方的步骤

### 第1阶段：预飞行确认

在做出更改之前，识别目标组织并获得明确的用户批准。

1.  **识别和发现组织**：验证目标组织。如果只知道显示名称，请列出组织以找到ID。然后，检索组织元数据以动态计算**目录客户ID**和**域名**：

    ```bash
    # 如果需要，列出以找到ID
    gcloud organizations list

    # 描述组织以检索元数据
    gcloud organizations describe [ORGANIZATION_ID]
    ```

    *计算值：*

    *   **域名** (`[ORG_NAME]` / `[YOUR_DOMAIN]`): 使用输出中的 `displayName` 值（例如，`my-business.com`）。
    *   **客户ID** (`[DIRECTORY_CUSTOMER_ID]`): 使用输出中的 `owner.directoryCustomerId` 值（例如，`C01234567`）。

2.  **展示蓝图摘要**：向用户展示蓝图的准确详细信息，并请求确认继续：

    > **为组织 `[ORG_NAME]` (`[ORGANIZATION_ID]`) 提出的基础部署摘要**
    >
    > *   **安全**：强制执行17个基本组织策略（13个布尔值，4个
    >     列表）。
    > *   **文件夹**：按顺序创建4个文件夹 (`Common`，`Production`，
    >     `Non-Production`，`Development`)。
    > *   **项目**：按顺序创建4个项目，具有唯一ID
    >     (`logging-[SUFFIX]`，`prod-[SUFFIX]`，`non-prod-[SUFFIX]`，
    >     `dev-[SUFFIX]`)。
    > *   **计费**：将所有项目链接到计费账户
    >     `[BILLING_ACCOUNT_ID]`。
    > *   **API**：在中央项目上启用日志记录和监控API。
    > *   **集中式日志记录**：部署 `global` 日志桶
    >     `[ORG_NAME]-logging`（30天保留期），配置组织级接收器
    >     `[ORGANIZATION_ID]-logbucketsink-[RANDOM_HEX]`，并建立跨项目指标范围。
    >
    > 您希望继续此部署吗？（是/否）

> [!IMPORTANT] **暂停执行**，并等待明确的用户批准后再进入第2阶段。如果用户拒绝，则中止操作。

### 第2阶段：错误恢复和懒角色修复策略

为确保在干净的组织中顺利部署，而无需复杂的初始权限检查（这些检查需要配额项目），代理**必须**采用“懒恢复”方法。

不要提前测试权限，代理将尝试执行配方中的每个步骤。如果某个步骤因 `Permission Denied` 错误而失败，代理将尝试通过向部署身份授予相应的推荐管理组角色来进行自我修复，然后重试操作。

> [!IMPORTANT] 当询问关于预部署准备情况、前置条件或要运行的检查时，代理**必须**明确解释着陆区部署采用懒角色修复策略，而不是 upfront 测试，并在其响应中详细说明以下所有内容： 1. 确认它将直接执行部署命令，捕获任何 Permission Denied 错误。 2. 确认它在失败时将尝试通过运行确切的命令 `gcloud organizations add-iam-policy-binding` 或 `gcloud billing accounts add-iam-policy-binding` 来授予整个管理组角色给活动身份，然后重试失败的部署命令。 3. 列出它将尝试授予的核心管理组（组织管理员组、计费管理员组和安全管理组）及其关键角色。 4. 确认如果自我修复授予权限命令失败，它将停止执行并请求手动管理员干预。

#### 修复协议

对于因缺少权限而失败的任何命令：

1.  **识别所需管理员组**：确定负责失败操作的管理员组。有关详细信息，请参阅
    [管理员IAM参考](references/admin-iam.md#core-administrative-groups--roles)。
2.  **尝试自我修复**：将属于该管理员组的**所有**角色依次授予活动经过身份验证的账户。有关详细信息，请参阅
    [管理员IAM修复指南](references/admin-iam.md#remediation) 的可复制粘贴脚本命令：

    *   **对于组织/文件夹级别的失败（组织管理员组或安全管理组）**：依次运行 `gcloud organizations add-iam-policy-binding`。
    *   **对于计费级别的失败（计费管理员组）**：依次运行 `gcloud
        billing accounts add-iam-policy-binding`。

3.  **在修复失败时停止**：

    *   如果授予权限命令成功，立即重试失败的部署命令。
    *   如果任何授予权限命令失败（例如，由于缺少 `setIamPolicy` 管理员权限），**停止执行**并指示用户要求其组织/计费管理员手动授予整个管理员组角色。

#### 阶段特定修复映射

*   **第3阶段：安全护栏（组织策略）**：
    *   如果 `gcloud org-policies set-policy` 失败：尝试在组织级别授予整个
        **组织管理员组**（9个角色）。
*   **第4阶段：资源层次结构（文件夹和项目）**：
    *   如果 `gcloud resource-manager folders create` 或 `gcloud projects create`
        失败：尝试在组织级别授予整个
        **组织管理员组**（9个角色）。
*   **第4阶段：计费链接**：
    *   如果 `gcloud billing projects link` 失败：尝试在计费账户级别授予整个
        **计费管理员组**（3个角色），并确保活动身份在组织级别授予
        **组织管理员组**（其中包含 `roles/billing.user`）。
*   **第5阶段：集中式日志记录和监控**：
    *   如果在组织级别 `gcloud logging sinks create` 失败：尝试授予
        整个 **日志记录/监控管理员组**（2个角色：
        `roles/logging.admin`，`roles/monitoring.admin`）和 **安全管理组**
        （9个角色）在组织级别。

### 第3阶段：安全护栏（组织策略）

在组织根目录下应用17个基本安全控制。

> [!CAUTION] 首先应用 `iam.allowedPolicyMemberDomains` 可能会锁定部署身份，如果它位于不允许的域中。在执行此策略之前，请确保部署身份是安全的。

1.  生成用于17个策略的YAML配置文件。有关布尔值和列表约束的确切YAML模板，请参阅
    [组织策略参考](references/org-policies.md)。
2.  使用 `gcloud org-policies` 工具按顺序应用每个组织策略：

    ```bash
    gcloud org-policies set-policy [POLICY_FILE_NAME].yaml
    ```

### 第4阶段：资源层次结构

#### 1. 文件夹创建

检查目标文件夹是否存在以避免重复。代理必须检查所有4个文件夹：对于任何已存在的文件夹（例如，如果 `Common` 或 `Production` 已存在），代理必须定位并重用它们；对于任何缺失的文件夹（例如，如果 `Non-Production` 或 `Development` 不存在），代理必须按顺序创建它们：

> [!IMPORTANT] 当解释如何处理现有资源（文件夹和项目）以防止重复时，代理**必须**明确命名其余缺失的文件夹（`Non-Production` 和 `Development`），并确认它将按顺序仅创建这些缺失的文件夹和项目。

```bash
# 检查并创建 "Common" 文件夹
gcloud resource-manager folders list --organization=[ORGANIZATION_ID] --filter="display_name=Common"
# 如果不存在：
gcloud resource-manager folders create --display-name="Common" --organization=[ORGANIZATION_ID]

# 检查并创建 "Production" 文件夹
gcloud resource-manager folders list --organization=[ORGANIZATION_ID] --filter="display_name=Production"
# 如果不存在：
gcloud resource-manager folders create --display-name="Production" --organization=[ORGANIZATION_ID]

# 检查并创建 "Non-Production" 文件夹
gcloud resource-manager folders list --organization=[ORGANIZATION_ID] --filter="display_name=Non-Production"
# 如果不存在：
gcloud resource-manager folders create --display-name="Non-Production" --organization=[ORGANIZATION_ID]

# 检查并创建 "Development" 文件夹
gcloud resource-manager folders list --organization=[ORGANIZATION_ID] --filter="display_name=Development"
# 如果不存在：
gcloud resource-manager folders create --display-name="Development" --organization=[ORGANIZATION_ID]
```

#### 2. 项目创建和计费链接

通过匹配显示名称检查目标项目是否已在文件夹中存在。如果不存在，则生成一个共享的8个字符随机后缀（例如，
`ab12cd34`），并按顺序创建项目，立即链接计费并启用API：

```bash
# 检查 "central-logging-monitoring" 项目是否存在于 Common 文件夹
gcloud projects list --filter="parent.id=[COMMON_FOLDER_ID] AND parent.type=folder AND name=central-logging-monitoring"

# 如果不存在：创建，链接计费，并启用API
gcloud projects create logging-[SUFFIX] --name="central-logging-monitoring" --folder=[COMMON_FOLDER_ID]
gcloud billing projects link logging-[SUFFIX] --billing-account=[BILLING_ACCOUNT_ID]
gcloud services enable compute.googleapis.com logging.googleapis.com monitoring.googleapis.com --project=logging-[SUFFIX]

# 检查 "production" 项目是否存在于 Production 文件夹
gcloud projects list --filter="parent.id=[PRODUCTION_FOLDER_ID] AND parent.type=folder AND name=production"

# 如果不存在：创建，链接计费，并启用API
gcloud projects create prod-[SUFFIX] --name="production" --folder=[PRODUCTION_FOLDER_ID]
gcloud billing projects link prod-[SUFFIX] --billing-account=[BILLING_ACCOUNT_ID]
gcloud services enable compute.googleapis.com run.googleapis.com container.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com pubsub.googleapis.com aiplatform.googleapis.com cloudaicompanion.googleapis.com apphub.googleapis.com designcenter.googleapis.com discoveryengine.googleapis.com iam.googleapis.com config.googleapis.com cloudbuild.googleapis.com cloudasset.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com --project=prod-[SUFFIX]

# 检查 "non-production" 项目是否存在于 Non-Production 文件夹
gcloud projects list --filter="parent.id=[NON_PRODUCTION_FOLDER_ID] AND parent.type=folder AND name=non-production"

# 如果不存在：创建，链接计费，并启用API
gcloud projects create non-prod-[SUFFIX] --name="non-production" --folder=[NON_PRODUCTION_FOLDER_ID]
gcloud billing projects link non-prod-[SUFFIX] --billing-account=[BILLING_ACCOUNT_ID]
gcloud services enable compute.googleapis.com run.googleapis.com container.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com pubsub.googleapis.com aiplatform.googleapis.com cloudaicompanion.googleapis.com apphub.googleapis.com designcenter.googleapis.com discoveryengine.googleapis.com iam.googleapis.com config.googleapis.com cloudbuild.googleapis.com cloudasset.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com --project=non-prod-[SUFFIX]

# 检查 "development" 项目是否存在于 Development 文件夹
gcloud projects list --filter="parent.id=[DEVELOPMENT_FOLDER_ID] AND parent.type=folder AND name=development"

# 如果不存在：创建，链接计费，并启用API
gcloud projects create dev-[SUFFIX] --name="development" --folder=[DEVELOPMENT_FOLDER_ID]
gcloud billing projects link dev-[SUFFIX] --billing-account=[BILLING_ACCOUNT_ID]
gcloud services enable compute.googleapis.com run.googleapis.com container.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com pubsub.googleapis.com aiplatform.googleapis.com cloudaicompanion.googleapis.com apphub.googleapis.com designcenter.googleapis.com discoveryengine.googleapis.com iam.googleapis.com config.googleapis.com cloudbuild.googleapis.com cloudasset.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com --project=dev-[SUFFIX]
```

> [!NOTE] **代理并行性选项**：虽然手动运行手册强制执行按顺序执行项目以避免终端竞争条件，但具有多代理编排能力的AI代理可以选择在解析文件夹ID后并行地生成子代理来提供4个项目。

### 第5阶段：集中式日志记录和监控

在 `logging-[SUFFIX]` 项目中配置集中式审计日志记录和跨项目监控范围。

参考
[集中式日志记录和监控参考](references/logging-monitoring.md)
以获取详细的逐步命令，以执行以下操作：

1.  创建中央日志存储桶。
2.  创建组织范围的日志接收器。
3.  为日志接收器授予权要的 IAM 权限。
4.  配置跨项目监控指标范围。

--------------------------------------------------------------------------------

## 验证逻辑与检查清单

根据以下验证检查评估部署情况：

-   [ ] **安全策略**：运行 `gcloud org-policies list
    --organization=[ORGANIZATION_ID]` 并验证所有 17 个目标策略都已强制执行或正确配置。
-   [ ] **资源文件夹**：验证组织根目录下存在 `Common`、`Production`、`Non-Production` 和 `Development` 文件夹。
-   [ ] **计费链接**：运行 `gcloud billing projects list` 并断言所有 4 个新创建的项目都已链接到您的计费账户。
-   [ ] **日志存储桶与保留期**：验证项目 `logging-[SUFFIX]` 中存在日志存储桶 `[ORG_NAME]-logging`，其位于 `global`，并且保留期为恰好 30 天。
-   [ ] **日志接收器路由**：在组织级别运行 `gcloud logging sinks describe` 并确认接收器将云审计日志路由到全局存储桶，并持有标准的 `writerIdentity` 凭证。
-   [ ] **指标范围链接**：运行 `gcloud beta monitoring metrics-scopes
    describe` 并断言 `dev`、`non-prod` 和 `prod` 项目出现在中央 `logging` 项目的监控列表中。

--------------------------------------------------------------------------------

## 链接

*   [Google Cloud 资源层次结构文档](https://cloud.google.com/resource-manager/docs/creating-managing-organization)
*   [Google Cloud 组织策略概述](https://cloud.google.com/resource-manager/docs/organization-policy/overview)
*   [集中式审计日志最佳实践](https://cloud.google.com/architecture/security-foundations/logging-monitoring)
*   [云监控指标范围配置](https://cloud.google.com/monitoring/settings/multiple-projects)
*   [Gcloud Logging 接收器 CLI 参考](https://cloud.google.com/sdk/gcloud/reference/logging/sinks)
*   [Google Cloud 登陆区域指南](https://docs.cloud.google.com/architecture/landing-zones)
*   [Google Cloud 安全基础蓝图](https://docs.cloud.google.com/architecture/blueprints/security-foundations)
