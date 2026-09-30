---
name: agent-platform-tuning-management
description: 在 Agent 平台上管理 GenAI 调优作业。使用此功能可列出、获取或取消正在进行的模型调优作业。不要用于模型微调（请使用 `agent-platform-tuning`）、将模型部署到端点（请使用 `agent-platform-deploy`）或管理服务端点（请使用 `agent-platform-endpoint-management`）。
---

# 代理平台调优管理

本技能提供使用 Agent 平台 Python SDK 管理 GenAI 调优作业的说明。当用户想要检查调优运行状态、查找活动调优作业或取消运行时间过长的作业时，请使用此技能。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，你必须遵守以下基于请求操作的安全级别：

1.  **R级别：只读（`list`，`get`）**
    *   **规则**：无需确认。你可以立即执行这些命令以收集用户所需的信息。
2.  **D级别：破坏性与中断性（`cancel`）**
    *   **规则**：取消操作是 D 级别的操作，需要**明确的类型确认**（例如 "我确认" 或 "是的，取消它"）。
    *   **干运行确认卡中的必填字段**：在取消调优作业之前，你必须展示一个干运行确认预览，清晰列出：
        *   **目标资源**：完整的调优作业资源名称或 ID（例如 `projects/<PROJECT_ID>/locations/<REGION>/tuningJobs/<JOB_ID>`）。
        *   **命令/脚本**：将要执行的精确取消命令或 Python 代码。
        *   **预期效果**：停止正在进行的调优作业；任何进行中的训练将被中止且无法恢复。
        *   询问用户进行明确确认（例如，"你确认吗？请回复 '我确认' 或 '是的，取消它'。"）。
    *   **同回合限制**：**绝对不要**在展示预览卡的同回合中执行取消操作。必须立即停止并等待用户在新回合中确认。即使用户提供了预先确认（例如 "是的，我确认，取消调优作业..."）或提供了修正的作业 ID，你也必须展示针对该特定作业 ID 的干运行预览，并在单独的新回合中等待确认后才能执行取消。

## 第 0 阶段：环境设置

**关键**：在运行下方的任何 Python 代码片段之前，你必须确保通过以下步骤正确初始化环境：

1.  **Google Cloud 身份验证**：使用你的 Google Cloud 账户进行身份验证，并为 Agent 平台访问配置活动应用默认凭证（ADC）：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **Python 依赖项**：此技能需要 `google-cloud-aiplatform`。**不要**创建虚拟环境——它初始为空，会隐藏环境已提供的包，强制进行冗余安装。探测并仅安装缺失的部分：

    ```bash
    python3 -c "import vertexai" || pip install google-cloud-aiplatform
    ```

3.  **执行**：使用 `python3` 运行 Python 代码片段。无需先激活任何环境。

## 工作流决策树

1.  **信息收集**：你拥有项目 ID 和区域吗？

    *   **否** -> 你**必须**以纯文本形式向用户询问缺失的项目 ID 和区域，或建议他们检查 gcloud 配置。如果两个位置都没有此信息，则询问用户提供。不要自行尝试搜索随机区域。
    *   **是** -> 继续步骤 2。

2.  **任务类型**：用户想要做什么？

    *   **查找或列出作业** -> 使用 Python SDK 列出调优作业。（R 级别）
    *   **检查状态/检查特定作业** -> 使用 Python SDK 获取调优作业详细信息。（R 级别）
    *   **取消作业** -> 请求确认，然后使用 Python SDK 取消调优作业。（D 级别）

## 使用 Python SDK

> [!NOTE]
>
> **资源验证与缺失的项目/作业**：如果执行 Python 代码片段时出现错误（例如 `403 权限被拒绝`，`404 未找到`，`INVALID_ARGUMENT` 或指示虚拟/缺失项目或作业 ID），你必须**立即**告知用户项目或调优作业不存在或无法访问。你必须提示用户提供有效的项目 ID 或作业 ID，并立即停止工具执行以等待其响应。**不要**重试或循环，**不要**假设资源有效，并且在收到用户提供的有效详细信息之前**不要**执行后续脚本。

### 1. 列出调优作业（R 级别）

如果用户询问 "我正在运行哪些调优作业？" 或想要查找特定作业 ID：

```python
from google.cloud import aiplatform_v1

project_id = "YOUR_PROJECT_ID"
region = "YOUR_REGION"
parent = f"projects/{project_id}/locations/{region}"

client = aiplatform_v1.GenAiTuningServiceClient(
    client_options={"api_endpoint": f"{region}-aiplatform.googleapis.com"}
)

jobs = client.list_tuning_jobs(parent=parent)
for job in jobs:
    print(f"Name: {job.name}")
    print(f"Base Model: {job.base_model}")
    print(f"State: {job.state}")
```

### 2. 获取特定作业的详细信息（R 级别）

如果用户提供调优作业 ID 并询问其状态：

```python
from google.cloud import aiplatform_v1

project_id = "YOUR_PROJECT_ID"
region = "YOUR_REGION"
job_id = "YOUR_JOB_ID"  # 19 位 ID
name = f"projects/{project_id}/locations/{region}/tuningJobs/{job_id}"

client = aiplatform_v1.GenAiTuningServiceClient(
    client_options={"api_endpoint": f"{region}-aiplatform.googleapis.com"}
)

job = client.get_tuning_job(name=name)
print(f"Name: {job.name}")
print(f"Base Model: {job.base_model}")
print(f"State: {job.state}")
print(f"Tuning Model: {job.tuned_model_display_name}")
```

### 3. 取消作业（D 级别）

如果用户明确请求停止、中止或取消正在运行的调优作业：

**安全检查**：**操作需要在进行之前进行明确的类型确认。** 你必须展示一个干运行确认卡，列出目标资源、命令/脚本和预期效果，并要求用户输入 "我确认" 或 "是的，取消它"。即使用户提供了确认性语言预先确认或正在提供修正的/新的作业 ID，你也必须展示针对该特定作业 ID 的预览卡，并在单独的新回合中等待其明确批准。

> [!IMPORTANT]
>
> **绝对不要**在收到用户在新回合中的响应之前预先执行任何取消代码或命令。你必须永远不会猜测或假设确认将被给出。在同回合中展示预览卡时执行取消是严重的违规行为。

```python
from google.cloud import aiplatform_v1

project_id = "YOUR_PROJECT_ID"
region = "YOUR_REGION"
job_id = "YOUR_JOB_ID"  # 19 位 ID
name = f"projects/{project_id}/locations/{region}/tuningJobs/{job_id}"

client = aiplatform_v1.GenAiTuningServiceClient(
    client_options={"api_endpoint": f"{region}-aiplatform.googleapis.com"}
)

client.cancel_tuning_job(name=name)
print(f"成功请求取消 {name}")
```
