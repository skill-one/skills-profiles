# 使用应用设计中心设计和部署 GCP 基础设施

## 概述

本技能为 Google Cloud Platform (GCP) 上整个基础设施生命周期提供一套规范性、生产级的流程。它用**代理控制的设计和验证循环**取代了自动化的、不透明的 GAD `design_infra` 工具，该循环利用模块化 Terraform 和本地 CLI 验证，然后在与应用设计中心 (ADC) 注册表同步以进行部署和生命周期管理之前进行**左移最佳实践计划扫描**。

始终保持主要云架构师的角色。将本地 Terraform 配置作为真实来源，并在将其导入云注册表之前确保设计完全符合最佳实践。

--------------------------------------------------------------------------------

## 索引

1.  [前提条件：设置和确认](#前提条件-设置和确认)
2.  [阶段 1：本地基础设施设计和验证](#阶段-1-本地基础设施设计和验证)
3.  [阶段 2：左移最佳实践评估和迭代修复](#阶段-2-左移最佳实践评估和迭代修复)
4.  [阶段 3：将 IaC 导入应用设计中心](#阶段-3-将-iac-导入应用设计中心)
5.  [阶段 4：应用部署和监控](#阶段-4-应用部署和监控)
6.  [阶段 5：排查部署失败](#阶段-5-排查部署失败)
7.  [阶段 6：验证和端到端测试](#阶段-6-验证和端到端测试)

--------------------------------------------------------------------------------

## 前提条件：设置和确认

在执行阶段 1 之前，您**必须**执行以下设置步骤：

1.  **确认目标项目和位置**：

    *   明确要求用户确认目标 GCP **项目 ID** 和**位置**（区域）。
    *   如果用户未指定位置，则使用 **`us-central1`** 作为默认值。
    *   验证您的本地环境已设置活动项目：

        ```bash
        gcloud config set project <project_id>
        ```

--------------------------------------------------------------------------------

## 阶段 1：本地基础设施设计和验证

**目标**：将用户需求和代码库特征转换为本地 100% 验证、安全且可编译的 Terraform 配置。

1.  **调用 `design` 技能**：调用并执行为用户的提示定义的 `design` 技能（位于 [design](references/design_guide.md)）。
    *   `design` 技能将自动执行代码库分析、查询目录注册表、规划、HCL 生成和本地 CLI 验证循环（`terraform init`、`validate`、`plan`）在一个专用的临时目录中。
2.  **定位验证后的 HCL**：确定 `design` 技能保存验证后、可编译的 Terraform 文件的临时目录（例如，`scratch/tf_validate_<session_id>/`）。
3.  **验证交接（强制）**：确保 `design` 技能中的本地验证循环在继续之前已成功完成并生成干净的计划。仔细检查 HCL 以验证：
    *   **Secret-Safe 政策**：确认 `terraform.tfvars` 或 HCL 资源块中没有明文凭证、密码或硬编码的密钥。所有敏感输入必须通过 GCP Secret Manager 进行连接。
    *   **State Isolation 政策**：确认 HCL 文件中没有远程后端块（例如，`backend "gcs" {}`）。在验证期间，状态必须保留在临时文件夹中，允许 ADC 处理远程状态注册表。
    *   *修复*：如果发现任何违规行为，请在 HCL 中进行修正，重新运行本地验证，并再次验证。不要继续使用未验证或不安全的代码。
4.  **将 Terraform 计划导出为 JSON（强制）**：在临时目录中，运行以下命令以生成二进制计划并将其转换为干净的 JSON 表示形式：

    ```bash
    terraform plan -out=tfplan && terraform show -json tfplan > tfplan.json
    ```

    验证 `tfplan.json` 文件是否已成功写入您的临时目录。

--------------------------------------------------------------------------------

## 阶段 2：左移最佳实践评估和迭代修复

**目标**：在将其导入云注册表之前，使用原生 ADC 计划评估 API 验证本地计划与安全、成本和可靠性基准的一致性。

1.  **发现 Space ID（强制）**：在运行评估或创建模板之前，您**必须**动态发现目标位置中的活动 ADC Space ID：

    *   **列出 Space**：运行命令：

        ```bash
        gcloud design-center spaces list --project=<project_id> --location=<location>
        ```

    *   **选择 Space**：解析输出以识别活动空间（例如，`test-deploy` 或 `googlespace`）。如果存在多个空间，请要求用户确认。如果不存在空间，请要求用户创建一个：

        ```bash
        gcloud design-center spaces create <space_id> --project=<project_id> --location=<location>
        ```

2.  **通过 gcloud 执行计划评估**：使用发现的 Space ID 和您导出的 `tfplan.json` 文件运行基于计划的评估。直接在终端中执行命令：

    ```bash
    gcloud design-center spaces generate-terraform-assessment-report <space_id> \
        --location=<location> \
        --project=<project_id> \
        --terraform-plan="<scratch_directory_path>/tfplan.json" \
        --format=json
    ```

3.  **分析结果**：以干净的表格格式向用户展示所有结果，详细说明具体的违规行为、资源作用域和相关严重级别。

4.  **本地修复循环**：

    *   **不要**尝试导入或提交不安全的代码。
    *   在临时目录中编辑您的**本地 HCL 文件**以修复报告的违规行为（例如，添加加密密钥、启用 OS Login 或限制 IAM 作用域）。
    *   重新运行阶段 1 本地验证和计划导出：

        ```bash
        terraform validate && terraform plan -out=tfplan && terraform show -json tfplan > tfplan.json
        ```

    *   重新运行步骤 2 中显示的计划评估命令。

5.  **退出标准**：

    *   所有高/关键结果已解决，或记录了可接受的权衡。
    *   最多达到三次（3）迭代尝试。一旦干净或可接受，则继续进行阶段 3。

--------------------------------------------------------------------------------

## 阶段 3：将 IaC 导入应用设计中心

**目标**：将完全验证且符合最佳实践的本地的 HCL 配置与 ADC 云注册表同步，以建立可部署的模板资源。

1.  **验证或创建应用程序模板（强制）**：在导入 HCL 之前，您**必须**确保在发现的 ADC 空间中存在父应用程序模板资源。

    *   **检查存在**：运行 `gcloud design-center spaces application-templates describe <template_id> --space=<space_id> --project=<project_id> --location=<location>` 以检查模板是否存在。
    *   **如果不存在则创建**：如果描述命令返回 `NOT_FOUND` 错误，请首先通过运行以下命令创建模板资源：

        ```bash
        gcloud design-center spaces application-templates create <template_id> --space=<space_id> --project=<project_id> --location=<location> --display-name="<Name>" --description="<Description>"
        ```

2.  **严格的 HCL 解析器约束（关键）**：在调用导入操作之前，确保您的本地 HCL 符合 ADC 注册表的严格摄取规则：

    *   **纯模块策略（不允许资源块）**：ADC 解析器严格**禁止**在导入的 HCL 中包含任何 `resource` 块。只允许 `module`、`variable`、`output` 和 `provider` 块。如果需要资源（例如 Private Service Access 对等连接），但目录中没有为其注册独立的模块，则必须检查它是否作为现有注册模块中的内置配置选项支持（例如，在 `module "vpc"` 中设置 `private_service_access_config`）。
    *   **严格的字符串类型**：ADC 解析器不会执行从布尔值到字符串的隐式类型强制。例如，子网私有访问必须作为字面量字符串声明：`subnet_private_access = "true"`，而不是作为布尔值 `true`。
    *   **不允许 Terraform 块**：解析器严格禁止 `terraform {}` 版本约束块。完全从 `providers.tf` 或 `main.tf` 中省略它。

3.  **导入到 ADC 模板**：一旦确认模板资源存在并且 HCL 符合上述约束，请调用托管的 `application_design_center:manage_application_template` MCP 工具，并使用 `APPLICATION_TEMPLATE_OPERATION_IMPORT_IAC` 操作：

    *   **参数**：

        *   `project`：目标项目 ID。
        *   `location`：GCP 部署区域（例如，`us-central1`）。
        *   `spaceId`：发现的 ADC 空间 ID。
        *   `applicationTemplateId`：您的应用程序模板的唯一名称。
        *   `operation`：`APPLICATION_TEMPLATE_OPERATION_IMPORT_IAC`
        *   `iacModule`：包含文件列表的结构化对象：

            ```json
            {
              "files": [
                { "name": "main.tf", "content": "<content of main.tf>" },
                { "name": "variables.tf", "content": "<content of variables.tf>" },
                { "name": "terraform.tfvars", "content": "<content of terraform.tfvars>" }
              ]
            }
            ```

    *   **弹性和重试（强制）**：

        *   如果 `IMPORT_IAC` 调用由于瞬态错误（例如，`502 Bad Gateway`、`504 Gateway Timeout` 或 `429 Rate Limit`）失败，**不要立即重试**。
        *   使用**带有抖动的指数退避**（例如，等待 2 秒、4 秒、8 秒加上一个随机的秒数分数）。
        *   **重试前验证修订版本**：如果发生超时，首先调用 `gcloud alpha design-center spaces application-templates describe` 检查导入是否在后台实际成功。只有在模板未更新时才重试。

4.  **捕获模板 URI**：成功后，这将在此空间中建立模板资源。使用以下模式构造 `applicationTemplateUri`：
    `projects/{project}/locations/{location}/spaces/{spaceId}/applicationTemplates/{applicationTemplateId}`

--------------------------------------------------------------------------------

## 阶段 4：应用部署和监控

**目标**：将经过验证且符合最佳实践的应用程序模板部署到 GCP 环境。

1.  **部署应用**：调用托管的 `application_design_center:manage_application` MCP 工具，并使用 `APPLICATION_OPERATION_DEPLOY` 操作：
    *   **参数**：
        *   `project`：目标项目 ID。
        *   `location`：目标部署位置。
        *   `spaceId`：目标空间 ID。
        *   `applicationId`：已部署应用程序实例的唯一 ID。
        *   `applicationTemplateUri`：阶段 3 中建立的 URI。
        *   `serviceAccount`：部署服务帐户。
    *   **弹性和重试（强制）**：
        *   如果 `DEPLOY` 操作因瞬态网络或网关错误（例如，`502`、`504`）失败，在重试之前应用**带有抖动的指数退避**。
        *   如果部署 LRO 超时或因状态冲突失败，使用 `gcloud design-center spaces applications describe` 验证应用程序状态，以确认其状态后再重试部署调用，避免并发冲突部署。

2.  **活动 LRO 监控**：
    *   工具返回一个长运行操作 (LRO)。通知用户部署已开始。
    *   **不要休眠**在部署状态轮询期间。每 30-60 秒使用 `gcloud design-center operations describe <operation_name>` 主动轮询 LRO，直到 `done: true`。

3.  **处理结果**：
    *   **成功**：如果 `done` 为 `true` 且没有 `error` 字段，则继续进行阶段 6。
    *   **失败**：如果存在 `error` 字段，请分析错误类型并继续进行阶段 5。

--------------------------------------------------------------------------------

## 阶段 5：排查部署失败

**目标**：使用专门的故障排除技能和已建立的云解决模式，迭代地诊断和修复部署失败。

1.  **迭代云解决模式（关键）**：如果部署因 `REVISION_FAILED` 或 `TERRAFORM` 错误失败，请检查这些常见的资源冲突：

    *   **服务帐户 409 冲突（`alreadyExists`）**：如果部署失败是因为模块生成的服务帐户（例如 `frontend-service-us-central-sa`）已在项目中存在，请通过禁用服务帐户创建并引用现有的服务帐户来修复本地 HCL：

        ```hcl
        create_service_account = false
        service_account        = "<existing_service_account_email>"
        ```

    *   **容器镜像 404 NotFound**：如果部署失败是因为找不到容器镜像，请确认镜像是否存在于您的注册表中。对于测试或 hello-world 部署，利用官方公共 Google hello-world 镜像：
        `us-docker.pkg.dev/cloudrun/container/hello`

2.  **委托给故障排除技能**：如果发生部署失败且不匹配上述模式，请调用并执行专门的 `infra-deployment-debugging` 指南（位于 [infra-deployment-debugging](references/troubleshooting_guide.md)）。

3.  **选择故障排除上下文**：

    *   **对于本地验证错误（阶段 1/2）**：遵循故障排除技能中的**案例 B：原始 Terraform 部署**说明，以隔离语法、编译和计划时验证错误。
    *   **对于云部署失败（阶段 4）**：遵循故障排除技能中的**案例 A：ADC 应用程序部署**说明，以分析 LRO 错误、检索服务日志并诊断云环境问题。

4.  **应用本地优先修复**：

    *   遵循故障排除技能的修复指南来制定修复方案。
    *   **强制**：直接在临时目录中的**本地 HCL 文件**上应用修复，重新运行本地验证，重新导入 HCL，并触发新的部署。
    *   重新运行阶段 1 本地验证和计划导出：

        ```bash
        terraform validate && terraform plan -out=tfplan && terraform show -json tfplan > tfplan.json
        ```

    *   重新运行计划评估（阶段 2），以确保没有引入新的违规行为。

    *   使用 `APPLICATION_TEMPLATE_OPERATION_IMPORT_IAC` 重新导入修正后的 HCL 到 ADC。

    *   使用 `APPLICATION_OPERATION_DEPLOY` 触发新的部署。

5.  **迭代阈值**：重复故障排除、验证、导入和重新部署循环最多五（5）次。如果仍然失败，请向用户报告完整的历史记录和诊断。

--------------------------------------------------------------------------------

## 阶段 6：验证和端到端测试

**目标**：确认已部署的服务是健康的且完全可用的。

1.  **检索已部署资源**：调用托管的 `application_design_center:manage_application` MCP 工具，并使用 `APPLICATION_OPERATION_GET` 操作以检索资源详细信息、公共端点和输出参数。
2.  **健康检查**：验证所有服务是否使用正确的容器镜像 URL，并且其运行时状态是健康的。
3.  **端到端验证**：进行简单的演示测试（例如，检查公共 HTTP 端点或触发干运行事务），以确保端到端功能。向用户展示结果和公共 URL 以完成任务。

## 报告问题

在 [Google 技能问题](https://github.com/google/skills/issues) 中报告此技能的 bug 或改进。
