# Google Cloud Build 基础知识

## 前置条件

开始之前，请确保满足以下前置条件：

1.  **Google Cloud SDK**: 确保 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) 已安装并配置。
2.  **身份验证**: 身份验证 gcloud CLI：
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **项目 ID**: 了解目标 Google Cloud 项目 ID。设置上下文：
    ```bash
    gcloud config set project <PROJECT_ID>
    ```
4.  **启用 Cloud Build API**: 必须为项目启用 Cloud Build API。
    ```bash
    gcloud services enable cloudbuild.googleapis.com
    ```
5.  **权限**: 确保用户或服务账户具有必要的权限，例如 `roles/cloudbuild.builds.editor` 和 `roles/serviceusage.serviceUsageAdmin`（用于启用 API）。

## 核心概念

Google Cloud Build (GCB) 是一个无服务器平台，在 Google Cloud 上执行您的构建。它将您的源代码转换为可部署的工件，例如 Docker 容器或 Java 归档文件。

| 概念 | 描述 |
| :--- | :--- |
| **`cloudbuild.yaml`** | 必须的配置文件，用于定义构建步骤。它使用 YAML 或 JSON 编写。 |
| **构建步骤** | GCB 执行的一系列操作（步骤）。每个步骤在特定的 Docker 容器（构建器）中运行命令。常见的构建器包括 `gcr.io/cloud-builders/gcloud`、`gcr.io/cloud-builders/docker` 和自定义容器。 |
| **工件** | 构建的输出，通常是推送到 Google Container Registry (GCR) 或 Artifact Registry (AR) 的容器镜像，或其他可部署文件。 |
| **触发器** | 自动化规则，在响应事件时（例如，推送到 Git 仓库、Pub/Sub 消息或手动请求）触发构建。 |

## 导航：查看构建历史记录

Cloud Build 构建历史记录页面是监控过去和正在进行构建状态的中心位置。

1.  **打开 Cloud Console**: 导航到 Google Cloud Console。
2.  **进入 Cloud Build**: 使用搜索栏或导航菜单找到 **Cloud Build**。
3.  **选择构建历史记录**: 在左侧导航栏中，选择 **History**（或使用直接 URL：`https://console.cloud.google.com/cloud-build/builds`）。
4.  **查看构建记录**：
    *   **状态**: 检查状态列 (`SUCCESS`、`FAILURE`、`WORKING`、`QUEUED`)。
    *   **区域**: 使用顶部的区域筛选器查看在特定区域运行的构建（对于区域工作池非常重要）。
    *   **日志**: 点击特定的构建 ID 查看详细日志、执行步骤和构建摘要。这对于调试失败的构建至关重要。

> [!NOTE]
> 如果您是第一次访问此页面，您可能会看到“零状态”体验，它提供运行示例构建或创建第一个触发器的选项（如 [`cb-list-build-zero-state`](references/cb-list-build-zero-state.md) 技能中所述）。请注意，触发器和构建的区域设置在创建后是不可变的，必须谨慎选择。

## 创建基本自动化触发器

此过程定义了一个自动化规则，以便在将代码推送到指定 Git 分支时运行构建。

### 第 1 步：开始创建触发器

1.  导航到 **Cloud Build 触发器** 页面 (`https://console.cloud.google.com/cloud-build/triggers`)。
2.  点击 **创建触发器**。

### 第 2 步：配置触发器设置

1.  **名称**: 提供一个唯一且描述性的名称（例如，`github-main-branch-build`）。
2.  **区域**: 选择触发器配置将存储的区域（例如，`global` 或特定区域端点）。**注意：触发器和构建区域设置在创建后是不可变的，必须谨慎选择。**
3.  **事件**: 选择事件类型。对于自动化 CI/CD，选择 **推送到分支**。
4.  **源**: 选择仓库源：
    *   **仓库**: 连接您的源仓库（GitHub、Bitbucket、Cloud Source Repositories 等）。如有需要，请授权连接。
    *   **仓库名称**: 选择您要链接的特定仓库。
5.  **分支**: 输入分支模式（例如，`^main$` 或 `^develop`）。

### 第 3 步：配置构建设置

1.  **配置**: 选择 **Cloud Build 配置文件 (yaml 或 json)**。
2.  **位置**: 保持默认的 **仓库**，并指定您的构建配置文件路径（例如，`cloudbuild.yaml`）。
    *   *替代方案*：对于非常简单的构建，您可以选择 **内联** 将 YAML 配置直接粘贴到触发器中。
3.  **（可选）服务账户**: 对于生产环境，选择一个具有有限权限的专用服务账户，以实施最小权限原则。

### 第 4 步：保存并测试

1.  点击 **创建**。触发器现在已激活，将在下一个匹配的 Git 推送时自动运行。

> [!TIP]
> `cb-create-trigger` 技能提供了创建所有类型（GitHub、Pub/Sub、Webhook）和配置（内联、Dockerfile、YAML）触发器的详细 `gcloud` 命令。使用该技能进行 CLI 自动化。

## 手动运行现有触发器

有时您需要按需运行触发器，在其正常自动化流程之外（例如，重新构建旧提交或测试新替换项）。

> [!IMPORTANT]
> **替换项不可变性**: 您只能覆盖触发器配置中**已定义**的替换项的值。您无法在运行时引入新的替换项键。

### 选项 A：通过 Cloud Console

1.  导航到 **Cloud Build 触发器** 页面 (`https://console.cloud.google.com/cloud-build/triggers`)。
2.  找到您要运行的触发器。
3.  点击触发器旁边的垂直省略号（⋮）并选择 **运行**。
4.  将出现一个对话框，允许您指定：
    *   **源分支/标签**: 选择要从中构建的特定 Git 引用。
    *   **替换项**: 覆盖任何现有的替换项（例如，将 `_VERSION` 设置为新值）。
5.  点击 **运行触发器**。构建将立即开始，您可以在 **历史记录** 页面上监控其状态。

### 选项 B：通过 gcloud CLI

使用 `gcloud builds triggers run` 命令来调用触发器并可选地覆盖参数。

```bash
# 对 'main' 分支运行触发器
gcloud builds triggers run <TRIGGER_NAME> \
    --region=<REGION> \
    --branch=main

# 运行触发器并覆盖替换项
gcloud builds triggers run <TRIGGER_NAME> \
    --region=<REGION> \
    --branch=main \
    --substitutions=_IMAGE_TAG="20231027-manual"

# 监控启动的构建
# 注意：运行命令会输出构建 ID。使用它来检查状态：
# gcloud builds log <BUILD_ID> --region=<REGION>
```

> [!NOTE]
> `cb-run-trigger` 技能提供了更复杂的调用示例，包括针对特定提交 SHA 运行或使用标签。

## 相关技能

*   [`cb-create-trigger`](references/cb-create-trigger.md): 创建所有触发器类型的详细 CLI 聚焦说明。
*   [`cb-list-build-zero-state`](references/cb-list-build-zero-state.md): Cloud Build 仪表板的高级管理和新用户引导零状态。
*   [`cb-run-trigger`](references/cb-run-trigger.md): 使用各种 `gcloud` 选项手动运行触发器的综合指南。

## 外部资源与文档

*   [Google Cloud Build 文档](https://cloud.google.com/build/docs)
*   [Cloud Build 配置文件架构](https://cloud.google.com/build/docs/build-config-file-schema)
*   [使用触发器自动化构建](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)
*   [gcloud CLI 构建 参考](https://cloud.google.com/sdk/gcloud/reference/builds)
