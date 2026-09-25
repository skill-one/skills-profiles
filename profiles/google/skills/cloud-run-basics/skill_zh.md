# Cloud Run 基础知识

Cloud Run 是一个完全托管的计算平台，用于在 Google 的高可扩展基础设施上运行您的代码、函数或容器。它抽象了基础设施管理，提供三种主要资源类型：

1.  **服务：** 响应发送到唯一且稳定的端点的 HTTP 请求，使用无状态的实例，根据各种关键指标自动扩展，也响应事件和函数。
2.  **作业：** 执行可并行化任务，可手动执行或在计划时间执行，并运行至完成。
3.  **工作池：** 处理始终开启的背景工作负载，例如基于拉取的工作负载，例如 Kafka 消费者、Pub/Sub 拉取队列或 RabbitMQ 消费者。

## 前置条件

1.  启用 Cloud Run 管理员 API 和 Cloud Build API：

    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet
    ```

1.  如果您处于受域限制的组织策略[限制](https://docs.cloud.google.com/organization-policy/restrict-domains.md.txt)下，对您的项目未身份验证的调用，您需要按照[测试私有服务](https://docs.cloud.google.com/run/docs/triggering/https-request.md.txt)下的说明访问您部署的服务。

### 所需角色

您需要以下角色才能部署您的 Cloud Run 资源：

*   在项目中具有 Cloud Run 管理员 (`roles/run.admin`) 角色权限
*   在项目中具有 Cloud Run 源开发者 (`roles/run.sourceDeveloper`) 角色权限
*   在服务标识中具有服务账户用户 (`roles/iam.serviceAccountUser`) 角色权限
*   在项目中具有日志查看器 (`roles/logging.viewer`) 角色权限

Cloud Build 会自动使用 Compute Engine 默认服务账户作为默认 Cloud Build 服务账户来构建您的源代码和 Cloud Run 资源，除非您覆盖此行为。

要让 Cloud Build 构建您的源代码，请授予 Cloud Build 服务账户在您的项目中具有 Cloud Run 构建者 (`roles/run.builder`) 角色权限：

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:SERVICE_ACCOUNT_EMAIL_ADDRESS \
    --role=roles/run.builder \
    --quiet
```

将 `PROJECT_ID` 替换为您的 Google Cloud 项目 ID，将 `SERVICE_ACCOUNT_EMAIL_ADDRESS` 替换为 Cloud Build 服务账户的电子邮件地址。

## 部署 Cloud Run 服务

您可以使用容器镜像或直接从源代码使用单个 Google Cloud CLI 命令将服务部署到 Cloud Run。

> **关键规则：** 任何部署的代码都必须监听 0.0.0.0（而不是 127.0.0.1）并使用注入的 $PORT 环境变量（默认为 8080），否则它将在启动时崩溃。

### 将容器镜像部署到 Cloud Run

Cloud Run 在部署期间导入您的容器镜像。只要该容器镜像被服务修订版使用，Cloud Run 就会保留该容器镜像的副本。当启动新的 Cloud Run 实例时，不会从其容器注册库中拉取容器镜像。

### 支持的容器镜像

您可以直接使用存储在 [Artifact Registry](https://docs.cloud.google.com/artifact-registry/docs/overview.md.txt) 或 [Docker Hub](https://hub.docker.com/) 中的容器镜像。Google 推荐使用 Artifact Registry，因为 Docker Hub 镜像最多会缓存一小时。

您可以使用来自其他公共或私有注册库（例如 JFrog Artifactory、Nexus 或 GitHub Container Registry）的容器镜像，方法是设置一个 [Artifact Registry 远程存储库](https://docs.cloud.google.com/artifact-registry/docs/repositories/remote-repo.md.txt)。

对于部署流行的容器镜像（例如 [Docker 官方镜像](https://docs.docker.com/docker-hub/official_images/) 或 [Docker 赞助的 OSS 镜像](https://docs.docker.com/docker-hub/dsos-program/)），您应该只考虑 [Docker Hub](https://hub.docker.com/)。为了更高的可用性，Google 推荐使用 [Artifact Registry 远程存储库](https://docs.cloud.google.com/artifact-registry/docs/repositories/remote-repo.md.txt) 部署这些 Docker Hub 镜像。

要部署容器镜像，请运行以下命令：

```bash
    gcloud run deploy SERVICE_NAME \
        --image IMAGE_URL \
        --region us-central1 \
        --allow-unauthenticated \
        --quiet
```

将以下内容替换：

*   SERVICE_NAME：您要部署到的服务的名称。服务名称必须不超过 49 个字符，并且必须在每个区域和项目中唯一。如果服务尚不存在，此命令将在部署期间创建该服务。您可以完全省略此参数，但如果省略，您将在运行命令时被提示输入服务名称。
*   IMAGE_URL：对容器镜像的引用，例如 `us-docker.pkg.dev/cloudrun/container/hello:latest`。如果您使用 Artifact Registry，则必须已创建 REPO_NAME 存储库。URL 格式为 `LOCATION-docker.pkg.dev/PROJECT_ID/REPO_NAME/PATH:TAG`。请注意，如果您不提供 `--image` 标志，部署命令将尝试从源代码部署。

### 从源代码部署

您可以通过两种不同的方式从源代码部署服务：

*   使用构建从源代码部署（默认）：此选项使用 Google Cloud 的 buildpacks 和 Cloud Build 自动从您的源代码构建容器镜像，而无需在您的机器上安装 Docker 或设置 buildpacks 或 Cloud Build。默认情况下，Cloud Run 使用 Cloud Build 提供的默认机器类型。

    *   要从源代码部署并启用自动基础镜像更新，请运行以下命令：

         ```bash
         gcloud run deploy SERVICE_NAME --source . \
         --base-image BASE_IMAGE \
         --automatic-updates \
         --quiet
         ```

        Cloud Run 仅支持使用 [Google Cloud 的 buildpacks 基础镜像](https://docs.cloud.google.com/docs/buildpacks/base-images.md.txt) 的自动基础镜像。

        *   要使用 Dockerfile 从源代码部署，请运行以下命令：

         ```bash
          gcloud run deploy SERVICE_NAME --source . --quiet
         ```
            当您提供 Dockerfile 时，Cloud Build 会将其在云端运行，并部署服务。

*   不使用构建从源代码部署（预览）：此选项直接将工件部署到 Cloud Run，绕过 Cloud Build 步骤。这允许快速部署时间。要从源代码不使用构建部署，请运行以下命令：

    ```bash
    gcloud beta run deploy SERVICE_NAME \
     --source APPLICATION_PATH \
     --no-build \
     --base-image=BASE_IMAGE \
     --command=COMMAND \
     --args=ARG \
     --quiet
    ```

    将以下内容替换：

    *   SERVICE_NAME：您的 Cloud Run 服务的名称。
    *   APPLICATION_PATH：您的应用程序在本地文件系统中的位置。
    *   BASE_IMAGE：您要为应用程序使用的 [运行时基础镜像](https://docs.cloud.google.com/run/docs/configuring/services/runtime-base-images.md.txt)。例如，`us-central1-docker.pkg.dev/serverless-runtimes/google-24-full/runtimes/nodejs24`。您也可以使用 OS 仅基础镜像部署预编译的二进制文件，而无需配置额外的语言特定运行时组件，例如 `osonly24`。
    *   COMMAND：容器启动时使用的命令。
    *   ARG：您发送到容器命令的参数。如果您使用多个参数，请在其各自的行上指定每个参数。

    关于从源代码不使用构建部署的示例，请参阅 [从源代码不使用构建部署的示例](https://docs.cloud.google.com/run/docs/deploying-source-code.md.txt)。

## 创建和执行 Cloud Run 作业

要创建新作业，请运行以下命令：

```bash
gcloud run jobs create JOB_NAME --image IMAGE_URL OPTIONS --quiet
```

或者，使用部署命令：

```bash
gcloud run jobs deploy JOB_NAME --image IMAGE_URL OPTIONS --quiet
```

将以下内容替换：

*   JOB_NAME：您要创建的作业的名称。如果您省略此参数，则在运行命令时将提示您输入作业名称。
*   IMAGE_URL：对容器镜像的引用，例如 `us-docker.pkg.dev/cloudrun/container/job:latest`。

*   可选地，用以下任何标志替换 OPTIONS：

    *   `--tasks`：接受大于或等于 1 的整数。默认值为 1；最大值为 10,000。每个任务都会获得环境变量 `CLOUD_RUN_TASK_INDEX`（其值介于 0 和任务数减 1 之间）以及 `CLOUD_RUN_TASK_COUNT`（任务数）。
    *   `--max-retries`：失败任务重试的次数。一旦任何任务超出此限制失败，整个作业将被标记为失败。例如，如果设置为 1，则失败任务将重试一次，总共尝试两次。默认值为 3。接受 0 到 10 的整数。
    *   `--task-timeout`：接受如 "2s" 的持续时间。默认值为 10 分钟；最大值为 168 小时（7 天）。对于使用 GPU 的任务，最大可用超时时间为 1 小时。
    *   `--parallelism`：可以并行执行的最大任务数。默认情况下，任务将尽可能快地并行启动。
    *   --execute-now：如果设置，则立即在作业创建后启动作业执行。相当于调用 `gcloud run jobs create` 后跟 `gcloud run jobs execute`。

    除了上述选项外，您还可以指定更多配置，例如环境变量或内存限制。

有关创建作业时可用选项的完整列表，请参阅 [`gcloud run jobs create`](https://docs.cloud.google.com/sdk/gcloud/reference/run/jobs/create) 命令行文档。

等待作业创建完成。成功完成后，您将看到一条成功消息。

要执行现有作业，请运行以下命令：

```bash
gcloud run jobs execute JOB_NAME --quiet
```

如果您希望命令等待执行完成，请运行以下命令：

```bash
gcloud run jobs execute JOB_NAME --wait --region=REGION --quiet
```

将以下内容替换：

*   JOB_NAME：作业的名称。
*   REGION：资源所在的区域。例如，`europe-west1`。或者，可以设置 `run/region` 属性。

## 部署工作池

您可以使用容器镜像或直接从源代码部署 Cloud Run 工作池。

### 部署容器镜像

您可以指定带有标签的容器镜像（例如 `us-docker.pkg.dev/my-project/container/my-image:latest`）或带有确切摘要的容器镜像（例如 `us-docker.pkg.dev/my-project/container/my-image@sha256:41f34ab970ee...`）。

### 支持的容器镜像

您可以直接使用存储在 [Artifact Registry](https://docs.cloud.google.com/artifact-registry/docs/overview.md.txt) 或 [Docker Hub](https://hub.docker.com/) 中的容器镜像。Google 推荐使用 Artifact Registry，因为 Docker Hub 镜像最多会缓存一小时。

您可以使用来自其他公共或私有注册库（例如 JFrog Artifactory、Nexus 或 GitHub Container Registry）的容器镜像，方法是设置一个 [Artifact Registry 远程存储库](https://docs.cloud.google.com/artifact-registry/docs/repositories/remote-repo.md.txt)。

对于部署流行的容器镜像（例如 [Docker 官方镜像](https://docs.docker.com/docker-hub/official_images/) 或 [Docker 赞助的 OSS 镜像](https://docs.docker.com/docker-hub/dsos-program/)），您应该只考虑 [Docker Hub](https://hub.docker.com/)。为了更高的可用性，Google 推荐使用 [Artifact Registry 远程存储库](https://docs.cloud.google.com/artifact-registry/docs/repositories/remote-repo.md.txt) 部署这些 Docker Hub 镜像。

要部署容器镜像，请运行以下命令：

```bash
gcloud run worker-pools deploy WORKER_POOL_NAME --image IMAGE_URL --quiet
```

将以下内容替换：

*   WORKER_POOL_NAME：您要部署的工作池的名称。如果工作池尚不存在，此命令将在部署期间创建该工作池。您可以完全省略此参数，但如果省略，您将在运行命令时被提示输入工作池名称。

*   IMAGE_URL：包含工作池的容器镜像的引用，例如 `us-docker.pkg.dev/cloudrun/container/worker-pool:latest`。请注意，如果您不提供 `--image` 标志，部署命令将尝试从源代码部署。

等待部署完成。成功完成后，Cloud Run 会显示一条成功消息以及已部署工作池的修订信息。

### 从源代码部署工作池

您可以使用单个 `gcloud run worker-pools` 部署命令和 `--source` 标志直接从源代码部署新的工作池或工作池修订版到 Cloud Run。

如果未提供 `--image` 或 `--source` 标志，部署命令将默认为源部署。

在幕后，此命令使用 [Google Cloud 的 buildpacks](https://docs.cloud.google.com/docs/buildpacks/overview.md.txt) 和 Cloud Build 自动从您的源代码构建容器镜像，而无需在您的机器上安装 Docker 或设置 buildpacks 或 Cloud Build。默认情况下，Cloud Run 使用 Cloud Build 提供的默认机器类型。

要从源代码部署工作池，请运行以下命令：

```bash
gcloud run worker-pools deploy WORKER_POOL_NAME --source . --quiet
```

将 `WORKER_POOL_NAME` 替换为您希望为工作池设置的名称。

### 如果部署失败怎么办：

1.  **IAM/权限错误：** 阅读 [iam-security.md](references/iam-security.md)。
2.  **启动时崩溃 / 健康检查失败：** 立即使用 `gcloud logging read "resource.labels.service_name=SERVICE_NAME" --limit=20` 获取日志，以找到确切的运行时错误。
3.  **原生依赖错误（Node/Python）：** 如果使用 `--no-build`，切换到 `--source .`（Buildpacks）以正确为 Linux 编译原生扩展。

## 参考目录

-   [核心概念](references/core-concepts.md)：服务与作业与工作池、资源模型和服务自动扩展行为。
-   [CLI 使用](references/cli-usage.md)：部署和管理 Cloud Run 的基本 `gcloud run` 命令。
-   [客户端库](references/client-library-usage.md)：使用 Google Cloud 客户端库与 Cloud Run 交互。
-   [MCP 使用](references/mcp-usage.md)：使用 Cloud Run 远程 MCP 服务器。
-   [基础设施即代码](references/iac-usage.md)：服务、作业、工作池和 IAM 绑定的 Terraform 示例。
-   [IAM & 安全](references/iam-security.md)：角色、服务标识和入站/出站控制。
-   [网络最佳实践 & 成本优化](references/networking.md)：成本优化策略、Direct VPC 出站、IP 地址和端口耗尽策略、性能吞吐量调整和 MTU 设置。

*如果您需要在这些参考中找不到的产品信息，请使用开发者知识 MCP 服务器 `search_documents` 工具。*
