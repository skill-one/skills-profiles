# IAM 推荐检索

此技能提供从 Google Cloud 获取 IAM 推荐和见解的说明。它涵盖了验证输入目标范围、使用 MCP 工具、gcloud 命令或直接 API 调用检索推荐，以及处理常见 API 错误。

## 流程

### 1. 验证输入目标

验证输入目标范围。

1.  **检查格式**：检查目标是否匹配以下格式之一：

    *   `organizations/{org_id}`
    *   `folders/{folder_id}`
    *   `projects/{project_id}`

2.  **处理模糊/原始目标**：如果用户仅提供原始 ID（不带前缀）：

    *   **字母开头**：假设它是项目 ID。将其格式化为 `projects/{project_id}` 并继续。
    *   **纯数字**：它是模糊的（可能是组织、文件夹或项目编号）。
        *   询问用户资源类型：> "目标 ID '{provided_id}' 是组织、文件夹还是项目？"
        *   一旦用户指定，相应地格式化目标范围（例如，添加 `organizations/`、`folders/` 或 `projects/`）并继续。
        *   如果用户的响应无效或无法澄清，将其视为错误并继续到 [处理错误](#5-处理错误)（目标不正确）。

3.  **处理项目编号**：如果目标是项目但使用纯数字 ID（项目编号）而不是项目 ID（例如，`projects/123456789`）：

    *   `gcloud` 推荐器命令需要项目 ID。尝试使用 `gcloud projects list
        --filter="projectNumber={project_number}" --format="value(projectId)"`
        将项目编号解析为项目 ID。
    *   如果此解析返回空或因权限错误失败，不要尝试描述项目、搜索代码库或搜索模拟数据。立即返回 [处理错误](#5-处理错误) 中指定的标准化错误 JSON 并停止执行（不要调用任何其他工具）。

4.  **记录验证**：在继续到获取步骤之前，在您的思考/推理中明确说明已验证和格式化的目标范围（例如，`projects/123456789` 或 `organizations/123456789012`）。

### 2. 获取推荐和见解（备用流程）

按顺序尝试以下检索方法。在第一个成功时停止。

**关键**：出错时快速失败（为了避免因相同的授权/权限原因导致冗余 API 调用失败）：如果任何尝试的方法（选项 A 或选项 B）因 API 级错误（例如 `PERMISSION_DENIED`、`UNAUTHENTICATED` 或资源 `NOT_FOUND` / 不存在）或 CLI 验证错误（例如项目编号不允许）而失败，**不要尝试任何其他选项**（包括选项 C 或直接 API/curl 调用）。立即停止，不要调用任何其他工具，并返回“处理错误”部分中指定的标准化错误 JSON。

#### 选项 A：MCP 工具（首选）

如果可用，请使用 MCP 工具。MCP 工具专为在 Google 内部环境中高效、安全地执行而设计，通常与通用 CLI 命令相比提供更简化的身份验证和更好的集成。

如果在您的上下文中提供 IAM 推荐器 MCP 工具：

*   使用 `target` 参数调用该工具。

#### 选项 B：gcloud CLI（首次备用）

如果 MCP 不可用，使用 `run_command` 执行以下命令（相应地替换变量）：

目标                          | 标志
:----------------------------- | :---------------------------------
`projects/{project_id}`        | `--project={project_id}`
`folders/{folder_id}`          | `--folder={folder_id}`
`organizations/{organization_id}` | `--organization={organization_id}`

**要运行的命令**：

```bash
GCLOUD_COMMON_FLAGS="--format=json --location=global \
--filter=stateInfo.state=ACTIVE"

# 1. 获取推荐
gcloud recommender recommendations list \
--recommender=google.iam.policy.Recommender $GCLOUD_COMMON_FLAGS {mapped_flag}

# 2. 获取见解
gcloud recommender insights list --insight-type=google.iam.policy.Insight
$GCLOUD_COMMON_FLAGS {mapped_flag}
```

#### 选项 C：Google Cloud API（最终备用）

仅在 `gcloud` 在环境中物理上不可用时才尝试此选项（例如，`gcloud: 命令未找到`）。API 客户端库需要更多的设置和执行开销，因此仅在缺少 CLI 工具时作为最后的手段使用。如果 `gcloud` 可用但因 API 错误失败，则**不要**使用此选项。

使用辅助脚本（或如果库不可用则直接 API 调用）通过 Google Cloud 推荐器 API 客户端库来：

1.  调用 `list_recommendations`（或 `recommendations.list`）用于
    `google.iam.policy.Recommender`（过滤：`stateInfo.state=ACTIVE`）。
2.  调用 `list_insights`（或 `insights.list`）用于 `google.iam.policy.Insight`
    （过滤：`stateInfo.state=ACTIVE`）。

### 3. 确定输出格式并交付

**关键**：仅在步骤 2 中的检索成功时才继续到此步骤。如果检索失败，跳过此步骤并直接转到 [处理错误](#5-处理错误)。

在展示结果之前，确定所需的输出格式。

**关键**：如果用户的初始提示已经指定了输出格式（例如，“以 JSON 格式返回原始结果”或“以表格形式显示”），则跳过询问并直接进行该格式。

否则，使用下拉菜单询问用户，选项为：

1.  JSON 文件
2.  聊天中的 Markdown 表格

根据选择（无论是预先指定还是由用户选择），交付输出：

#### 选项 A：JSON 文件

1.  将原始结果写入当前工作目录中的文件 `iam_recommendations_<target_id>_<timestamp>.json`
    （其中 `<target_id>` 是清理后的资源标识符，`<timestamp>` 格式化为 `YYYYMMDD_HHMMSS`）。
2.  文件内容必须与 [示例执行](#4-示例执行) 中显示的结构匹配。
3.  向用户回复文件路径。

#### 选项 B：聊天表格

1.  **排序推荐**：将检索到的推荐排序，将服务代理推荐放在列表的末尾。
2.  **格式化表格**：将排序后的推荐格式化为 Markdown 表格。表格应包含关键字段：
    -   **Subtype**：推荐器子类型或见解子类型（例如，指示是否用于资源级角色）。
    -   **Recommended Action**：推荐的摘要。
    -   **Rationale**：理由/证明。
    -   **Associated Insights**：任何链接见解的 ID（来自 `associatedInsights`）。
3.  **限制聊天显示**：在聊天表格中仅显示前 10 个推荐。
4.  **提供完整列表**：将完整的推荐和见解列表保存到 Markdown 文件（例如，
    `iam_recommendations_<target_id>_<timestamp>.md`，其中 `<target_id>` 是清理后的资源标识符，`<timestamp>` 格式化为 `YYYYMMDD_HHMMSS`）并提供链接供用户下载。
5.  **格式化见解表格**：如果有见解，则在 Markdown 文件中的单独表格中格式化它们（如果合适，还可以在聊天中显示摘要，但保持聊天简洁）。表格应包含关键字段：
    -   **Insight ID**：见解标识符 (`INSIGHT_ID`)。
    -   **State**：见解状态 (`INSIGHT_STATE`)。
    -   **Subtype**：见解子类型 (`INSIGHT_SUBTYPE`)。
    -   **Description**：见解描述 (`DESCRIPTION`)。
6.  **不要**在此选项中选择时提供包含原始结果的 JSON 文件。

### 4. 示例执行

*   **输入目标**：projects/my-test-project
*   **映射标志**：--project=my-test-project
*   **操作（选项 B）**：运行 `gcloud recommender recommendations list
    --recommender=google.iam.policy.Recommender --format=json --location=global
    --filter=stateInfo.state=ACTIVE --project=my-test-project`
*   **预期输出结构**：

    ```json
    {
      "raw_results": {
        "recommendations": [
          {
            "name": "projects/my-test-project/locations/global/recommenders/ \
            google.iam.policy.Recommender/recommendations/123",
            "content": { ... }
          }
        ],
        "insights": []
      },
      "error": null
    }
    ```

### 5. 处理错误

**关键**：如果您遇到以下任何错误条件（在验证或获取过程中），**立即停止**。不要尝试调试、切换帐户、搜索代码库或验证资源存在。立即输出指定的 JSON 结构作为您的最终响应，并调用不使用任何其他工具。

如果所有方法都失败，返回：

*   对于不正确的目标：`{"raw_results": null, "error": "指定的目标资源不正确或不存在。"}`
*   对于身份验证问题：`{"raw_results": null, "error": "用户未通过身份验证。请进行身份验证（例如，运行 'gcloud auth login'）。"}`
*   对于权限：`{"raw_results": null, "error": "权限不足。请确保您在目标范围内具有 'roles/recommender.iamViewer'。"}`
*   其他：`{"raw_results": null, "error": "获取失败：{error_details}"}`
    （不要向用户提及 MCP 工具失败）。

## 注意事项

*   **状态过滤**：始终确保您正在过滤 `ACTIVE` 推荐。
*   **位置**：IAM 推荐器的位置始终是全局。
