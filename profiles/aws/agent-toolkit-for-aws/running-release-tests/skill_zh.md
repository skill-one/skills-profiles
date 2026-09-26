# 发布测试

> **AgentSpace 路由（仅 SigV4）：** 如果您的工具列表中存在 `list_agent_spaces`，并且本次会话尚未调用多空间编排技能，请首先调用它以确定要使用的 `agent_space_id`。然后在所有后续工具调用中传递 `agent_space_id`。对于基于令牌的身份验证，这不需要——令牌已经针对一个空间进行了范围限制。

通过 AWS DevOps Agent 的发布测试 Agent 在云端运行自动化发布测试。支持 UI 测试（基于浏览器）和 API 测试（基于 OpenAPI 规范）。使用预先存在的测试配置文件，这些配置文件定义了目标 URL、代理类型、角色和凭证。

**输入是一个测试配置文件**——测试配置文件已经包含目标 URL、代理类型（UI 或 API）、测试角色和凭证。不要直接要求用户提供 URL；URL 定义在测试配置文件中。

## 前置条件

- 从 AWS DevOps Agent 控制台创建的预先存在的测试配置文件（知识项 ID，例如 `ki-12345`）

## 收集测试参数

在开始任何工作流之前，您必须收集以下参数。在得到答复之前，不要继续进行工作创建。

### 第 1 步 — 测试配置文件（必需）

询问用户要使用哪个测试配置文件。测试配置文件已经包含目标 URL、代理类型（UI 或 API）、测试角色和凭证配置——这些不需要单独收集。

**注意：** 预先存在的测试配置文件是前提条件。测试配置文件是使用 AWS DevOps Agent 控制台或 API 创建的，而不是通过此工具创建的。如果用户询问是否可以在此处创建，请告知他们必须已经存在。

### 第 2 步 — 测试需求（可选）

如果用户尚未提及测试重点，请询问：
> "您有特定的测试需求或重点领域吗？如果没有，我将运行全面的探索性测试。"

等待用户的回复。如果他们提供了一个，将其用作 `test_requirement`。如果他们说不或跳过，则不使用它继续进行。

**重要提示：** 在继续进行工作创建之前，您必须等待用户的回复。

## 核心工作流

### 1. 选择 Agent Space

列出可用的代理空间：

```
aws devops-agent list-agent-spaces --region us-east-1
```

向用户展示列表并询问他们想使用哪个代理空间。**在用户选择之前，不要继续进行。** 使用选择的 `agentSpaceId` 作为后续所有调用中的 `SPACE_ID`。

### 2. 检查工具可用性

验证以下工具是否可用：`aws_devops_agent__create_release_testing_job`、`aws_devops_agent__get_task`、`aws_devops_agent__list_journal_records`、`aws_devops_agent__get_release_ui_testing_report`、`aws_devops_agent__get_release_api_testing_report`。这些工具不是延迟加载的——如果它们不在您的工具列表中，则不可用。不要通过 ToolSearch 搜索它们。如果有任何工具缺失，请跳过本节剩余步骤，并使用下面的“后备（aws-mcp）”路径。

### 3. 启动工作

```
aws_devops_agent__create_release_testing_job(
    test_profile_id="ki-12345",
    webhook_event_message="<可选的测试需求>"
)
→ {"taskId": "...", "executionId": "...", "status": "started"}
```

从响应中记录 **taskId** 和 **executionId**。

### 4. 定期轮询状态

每 **30 秒** 调用一次 `aws_devops_agent__get_task(task_id=TASK_ID)`，直到状态转换为 `IN_PROGRESS` 或终端状态。

### 5. 监控直至完成

一旦 `IN_PROGRESS`，在循环中轮询进度：

1. 调用 `aws_devops_agent__list_journal_records(execution_id=EXEC_ID, order="ASC")` 获取新发现。
2. 向用户展示每条记录，并附带友好的进度更新。
3. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
4. 在每次轮询迭代之间**等待 20 秒**。
5. 定期检查 `aws_devops_agent__get_task(task_id=TASK_ID)`——在终端状态（`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`）时停止。

### 6. 展示结果

一旦工作达到终端状态：

- 如果 `COMPLETED`：
  1. 根据测试配置文件的代理类型（UI 或 API）确定报告类型。调用 `aws_devops_agent__get_release_ui_testing_report(execution_id=EXEC_ID)` 用于 UI 配置文件，或调用 `aws_devops_agent__get_release_api_testing_report(execution_id=EXEC_ID)` 用于 API 配置文件。
  2. 将报告内容写入 Markdown 文件：

     ```
     release-testing-report-<YYYY-MM-DD-HHmmss>.md
     ```

  3. 告知用户报告已保存，包括文件路径。
- 如果 `FAILED` 或 `TIMED_OUT`：展示错误信息并建议下一步操作。
- 如果 `CANCELED`：告知用户工作已取消，并且没有报告可用。

## 取消工作

```
aws_devops_agent__cancel_release_testing_job(task_id=TASK_ID)
```

## 错误处理

1. 如果任务状态变为 `FAILED`，停止工作流并报告错误。
2. 如果任务在 5 分钟内未达到 `IN_PROGRESS`，使用 `cancel_release_testing_job` 取消它。
3. 如果任何输出包含 "NoCredentialsError"、"ExpiredTokenException" 或身份验证失败，建议用户刷新凭证或检查令牌。
4. 如果被限流（`429` 或 `ThrottlingException`），在重试前等待 30 秒。重试 3 次后，告知用户。

## 后备（aws-mcp）

如果 `aws-devops-agent` 远程服务器不可用，直接使用 AWS CLI：

告知用户："远程服务器不可用——使用直接 AWS API 后备。"

### 1. 选择 Agent Space

列出可用的代理空间：

```
aws devops-agent list-agent-spaces --region us-east-1
```

向用户展示列表并询问他们想使用哪个代理空间。**在用户选择之前，不要继续进行。** 使用选择的 `agentSpaceId` 作为后续所有调用中的 `SPACE_ID`。

### 2. 启动工作

```
aws devops-agent create-backlog-task \
  --agent-space-id SPACE_ID \
  --task-type RELEASE_TESTING \
  --title '发布测试' \
  --priority MEDIUM \
  --description '{\"testProfileId\": \"<PROFILE_ID>\", \"webhookEventMessage\": \"<REQUIREMENT>\"}' \
  --region us-east-1
```

如果用户提供了测试需求，将其作为 `webhookEventMessage` 包括在内。如果没有，省略该字段或将其留空。

### 3. 定期轮询状态

```
aws devops-agent get-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --region us-east-1
```

每 **30 秒** 轮询一次，直到状态转换为 `IN_PROGRESS` 或终端状态（`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`）。

### 4. 监控直至完成

一旦 `IN_PROGRESS`，在循环中轮询进度：

```
aws devops-agent list-journal-records \
  --agent-space-id SPACE_ID \
  --execution-id EXEC_ID \
  --order ASC \
  --region us-east-1
```

1. 向用户展示每条记录，并附带友好的进度更新。
2. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
3. 在每次轮询迭代之间**等待 20 秒**。
4. 定期检查 `get-backlog-task`——在终端状态（`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`）时停止。

### 5. 展示结果

一旦工作达到终端状态：

- 如果 `COMPLETED`：
  1. 使用适当的记录类型检索报告：
     - **UI 测试**：`--record-type qa_ui_testing_report`
     - **API 测试**：`--record-type qa_api_testing_report`

     ```
     aws devops-agent list-journal-records \
       --agent-space-id SPACE_ID \
       --execution-id EXEC_ID \
       --record-type qa_ui_testing_report \
       --order ASC \
       --region us-east-1
     ```

  2. 将报告内容写入 Markdown 文件：

     ```
     release-testing-report-<YYYY-MM-DD-HHmmss>.md
     ```

  3. 告知用户报告已保存，包括文件路径。
- 如果 `FAILED` 或 `TIMED_OUT`：展示错误信息并建议下一步操作。
- 如果 `CANCELED`：告知用户工作已取消，并且没有报告可用。

#### 取消（后备）

```
aws devops-agent update-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --task-status CANCELED \
  --region us-east-1
```
