# 特权访问管理器 (PAM)

本技能提供分步指导，用于规划、验证和执行特权访问管理器 (PAM) 权限授予的 CRUD 操作、审批工作流配置、访问提升以及授予权限/拒绝工作流。

## 目录

*   [核心概念](#核心概念)
*   [审批工作流 & 最大请求时长](#审批工作流)
*   [安全性与确认策略](#安全性与确认策略)
*   [规划-验证-执行模式](#规划-验证-执行模式)
*   [模式 1：交互式访问提升](#模式-1)
*   [模式 2：独立权限授予 CRUD](#模式-2)
*   [模式 3：审批者工作流](#模式-3)
*   [支持链接与资源](#支持链接与资源)

## 核心概念 {#核心概念}

特权访问管理器 (PAM) 用按需、有时间限制且经过审计的访问提升来替代永久或环境 IAM 角色分配。PAM 不通过追加永久 IAM 策略绑定，而是使用：

*   **权限授予 (Entitlements):** 定义访问范围、符合条件的请求者和审批者的配置。
*   **授予权限 (Grants):** 针对权限授予创建的短期请求，用于激活权限授予的 IAM 角色。

### 特权访问 (`privilegedAccess`)

权限授予中的 `privilegedAccess` 块定义了将要授予的精确访问范围。访问范围包含三个基本组件：
*   **资源 (Resource):** 授予权限的目标 Google Cloud 资源（项目、文件夹或组织）。
*   **角色设置 (Role Setup):** 要分配的 IAM 角色 (`roleBindings.role`)。
*   **条件 (Condition):** (可选) 限制角色何时或何地生效的 IAM 条件表达式 (`roleBindings.conditionExpression`)。

### 核心工作流

1.  管理员创建权限授予。
2.  请求者可以针对这些权限授予请求授予权限。
3.  如果权限授予配置了审批，则必须由审批者批准请求的授予权限。
4.  完成所有必要的审批步骤后，授予权限将在请求的时间内被激活。
5.  授予权限在请求的时长结束后自动结束，提升的访问权限将被移除。

## 审批工作流 & 最大请求时长 {#审批工作流}

### 审批工作流 (`approvalWorkflow`)

当敏感环境需要在临时访问激活前需要人工审批时，在权限授予 YAML 清单 (`entitlement.yaml`) 中配置 `approvalWorkflow` 块。

```yaml
approvalWorkflow:
  manualApprovals:
    # 可选：要求审批者提供理由字符串
    requireApproverJustification: true
    steps:
    - approvalsNeeded: 1
      approverEmailRecipients:
      - approver@example.com
      approvers:
      - principals:
        - user:db-lead@my-company.com  # 或 group:sre-leads@my-company.com
```

*   **何时包含:** 每当用户提示需要手动审批或审批者（用户或组）时，包含 `approvalWorkflow`。
*   **结果:** 当用户针对具有 `approvalWorkflow` 的权限授予请求授予权限时，授予权限将过渡到 `APPROVAL_AWAITED`。请求者必须等待审批者的决定 (`模式 3`)。

### 最大请求时长 (`maxRequestDuration`)

`maxRequestDuration` 定义请求者在提交授予权限请求时可以请求的最大单次访问提升时长。

*   **灵活配置:** 根据用户的特定请求配置 `maxRequestDuration`（例如 `8 小时` / `28800s`，`1 小时` / `3600s`，`24 小时` / `86400s`）。
*   **默认值:** 如果用户未指定最大请求时长，则默认为 `4 小时` (`14400s`)。
*   **YAML 语法:** 始终将 `maxRequestDuration` 格式化为秒数的字符串，在权限授予 YAML 中（例如 `"14400s"`，`"28800s"`）。

## 安全性与确认策略 {#安全性与确认策略}

严格遵循以下工作流保护措施：

*   **修改/破坏性执行 (创建、更新、删除、批准、拒绝、撤销):** 始终显示计划的调整的纯文本摘要，并提示用户进行明确确认（是/否）。
*   **只读检查 (列出、描述、搜索):** 无需请求确认即可自动运行。
*   **批量 Bash 命令 (减少用户确认):** 主机环境要求用户对每个单独的 shell 工具调用进行批准。为减少确认弹窗，将顺序只读和查找命令组合成一个复合 bash 脚本，在一个工具调用中执行（例如，将项目、文件夹和组织层次结构审计组合为单行执行）。
*   **反循环策略:** 如果命令因明确的可操作错误而失败，可以尝试自我调试并重试。如果错误不明确，立即停止，显示 stderr 输出，并等待用户指示。

## 规划-验证-执行模式 {#规划-验证-执行模式}

对于所有修改操作（模式 1 步骤 3、模式 2 创建、更新、删除、模式 3 批准、拒绝）：

1.  **规划:** 构建建议的参数或读取示例权限授予结构。（对于权限授予创建，加载并使用模板：[assets/entitlement_template.yaml](assets/entitlement_template.yaml)）。
2.  **验证:** 检查目标配置参数（资源名称、角色绑定、时长限制）是否符合公司规则。
3.  **执行:** 显示已验证的计划，获取明确用户确认，并运行 `gcloud` 命令。

--------------------------------------------------------------------------------

## 模式 1：交互式访问提升 {#模式-1}

当用户作为请求者请求临时访问提升时，加载并遵循 [`references/requester.md`](references/requester.md) 中的详细说明。

--------------------------------------------------------------------------------

## 模式 2：独立权限授予 CRUD {#模式-2}

按照以下步骤进行权限授予配置。

### 权限授予管理员所需的权限

*   `roles/privilegedaccessmanager.admin`: 创建、更新和删除权限授予配置所需（`模式 1 步骤 3` 和 `模式 2 CRUD`）。
*   **范围 IAM 管理权限:** 在目标层次结构范围内需要，因为创建权限授予授权了在该范围内未来的角色评估和绑定：
    *   **组织:** `roles/iam.securityAdmin`
    *   **文件夹:** `roles/resourcemanager.folderAdmin`
    *   **项目:** `roles/resourcemanager.projectIamAdmin`
*   `roles/privilegedaccessmanager.viewer`: 列出和描述跨范围的权限授予所需。

*(规则：对于所有以下独立的权限授予 CRUD 命令，使用与权限授予定义位置匹配的标志：传递 `--project=PROJECT_ID`，`--folder=FOLDER_ID` 或 `--organization=ORGANIZATION_ID`)。*

### 1. 创建权限授予

1.  检查 `ENTITLEMENT_ID` 是否存在：

```bash
gcloud pam entitlements describe ENTITLEMENT_ID \
    --location=global \
    --project=PROJECT_ID
```

*   **如果存在:** 停止。询问：*"请求的 PAM 权限授予 `ENTITLEMENT_ID` 已存在。您想查看其详细信息还是更新它？(查看 / 更新 / 退出)"*
*   **如果未找到:** 加载模板 [assets/entitlement_template.yaml](assets/entitlement_template.yaml)。使用连字符分隔的小写字母生成 ID，基于角色名称（例如，`compute-admin` 对应 `roles/compute.admin`）。**注意：**
    *   您可以在 `roleBindings` 下指定多个 IAM 角色。
    *   您也可以为每个角色绑定包含可选的 IAM `conditionExpression`。
    *   不支持遗留基本角色（例如 `roles/viewer`，`roles/editor`，`roles/owner`）。相反，使用它们的 v2 基本角色等效项（例如 `roles/basic.viewer`，`roles/basic.editor`，`roles/basic.owner`）。确保选择有效的预定义、自定义或 v2 基本角色。
*   根据 `maxRequestDuration` 设置用户指定（例如，8 小时为 `"28800s"`，1 小时为 `"3600s"`）。如果用户未指定，默认为 `"14400s"`（4 小时）。如果政策指定或用户请求手动审批，请在 `entitlement.yaml` 中配置 `approvalWorkflow` 块。保留 `requesterJustificationConfig: {unstructured: {}}`。
*   提示：*"您即将创建 PAM 权限授予 `ENTITLEMENT_ID`。您批准此创建吗？(是/否)"*
*   部署：

```bash
gcloud pam entitlements create ENTITLEMENT_ID \
    --location=global \
    --entitlement-file=entitlement.yaml \
    --project=PROJECT_ID
```

### 2. 读取权限授予

自动运行这些读取操作：

列出单个范围内的所有权限授予：

```bash
gcloud pam entitlements list \
    --location=global \
    --project=PROJECT_ID
```

要列出整个资源层次结构中的所有权限授予（项目、祖先文件夹和组织），使用层次结构列出脚本：

```bash
bash scripts/list_entitlements_hierarchy.sh --project=PROJECT_ID
```
*(或传递 `--folder=FOLDER_ID` 或 `--organization=ORGANIZATION_ID`)。*

描述目标权限授予：

```bash
gcloud pam entitlements describe ENTITLEMENT_ID \
    --location=global \
    --project=PROJECT_ID
```

### 3. 更新权限授予

1.  运行 `export` 命令生成当前配置（包括 `etag`）：

    ```bash
    gcloud pam entitlements export ENTITLEMENT_ID \
        --location=global \
        --project=PROJECT_ID > {scratch}/updated_entitlement.yaml
    ```

    如果缺失，提供运行 `list` 或退出的选项。

2.  编辑导出的 `{scratch}/updated_entitlement.yaml` 文件以应用请求的更改（例如，更新 `maxRequestDuration`，`approvalWorkflow` 或 `eligibleUsers`）。不要修改 `etag`。

3.  提示：*"您即将更新 PAM 权限授予 `ENTITLEMENT_ID`。您批准此更新吗？(是/否)"*

4.  执行：

```bash
gcloud pam entitlements update ENTITLEMENT_ID \
    --location=global \
    --entitlement-file={scratch}/updated_entitlement.yaml \
    --project=PROJECT_ID
```

### 4. 删除权限授予

1.  使用 `describe` 验证存在性。如果缺失，提供列表/退出。
2.  **安全检查:** 如果存在打开的授予权限，则无法删除权限授予。在删除之前，搜索任何 `ACTIVE` 或 `SCHEDULED` 授予权限：

    ```bash
    gcloud pam grants list \
        --entitlement=ENTITLEMENT_ID \
        --location=global \
        --project=PROJECT_ID \
        --filter="state:(ACTIVE, SCHEDULED)"
    ```

    如果找到任何打开的授予权限，提示用户授权撤销它们：*"此权限授予上有活跃或计划的授予权限。您授权我撤销它们以便删除权限授予吗？(是/否)"*

    如果是，撤销它们：

    ```bash
    gcloud pam grants revoke GRANT_ID \
        --entitlement=ENTITLEMENT_ID \
        --location=global \
        --project=PROJECT_ID \
        --reason="撤销以删除权限授予"
    ```

3.  提示：*"您即将永久删除 PAM 权限授予 `ENTITLEMENT_ID`。您批准此删除吗？(是/否)"*

4.  执行：

```bash
gcloud pam entitlements delete ENTITLEMENT_ID \
    --location=global \
    --project=PROJECT_ID
```

--------------------------------------------------------------------------------

## 模式 3：审批者工作流 {#模式-3}

当审批者需要审查、批准或拒绝待处理的授予权限请求时，加载并遵循 [`references/approver.md`](references/approver.md) 中的详细说明。

--------------------------------------------------------------------------------

## 支持链接与资源 {#支持链接与资源}

有关与特权访问管理器工作的更多信息，请参阅：

*   [Google Cloud 特权访问管理器概述][pam-overview]
*   [设置 PAM 权限授予][pam-create]
*   [请求和审计 PAM 授予权限][pam-grants]
*   [gcloud SDK pam 参考指南][pam-gcloud]

[pam-overview]: https://cloud.google.com/iam/docs/pam-overview
[pam-create]: https://cloud.google.com/iam/docs/pam-create-entitlements
[pam-grants]: https://cloud.google.com/iam/docs/pam-request-temporary-elevated-access
[pam-gcloud]: https://cloud.google.com/sdk/gcloud/reference/pam
