# 代理平台调优管理

本技能提供使用 Agent Platform Python SDK 管理 GenAI 调优作业的说明。当用户想要检查调优运行状态、查找活动调优作业或取消运行时间过长的作业时，请使用此技能。

## 安全性与确认级别（关键）

在代表用户执行任何命令之前，您必须根据请求的操作遵守以下安全级别：

1.  **R级别：只读（`list`，`get`）**
    *   **规则**：无需确认。您可以立即执行这些命令以收集用户所需的信息。
2.  **D级别：破坏性与中断性（`cancel`）**
    *   **规则**：这需要**明确的类型确认**。您必须向用户输出一条文本消息，解释这将停止调优过程且任何进度都将丢失，并要求他们输入“我确认”或“是的，取消它”。您必须在执行取消命令之前立即请求此确认。

## 第0阶段：环境设置

**关键**：在运行下方的任何 Python 代码片段之前，您必须确保通过以下步骤正确初始化环境：

1.  **Google Cloud 身份验证**：使用您的 Google Cloud 账户进行身份验证，并为 Agent Platform 访问配置活动应用默认凭证（ADC）：

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **Python 依赖项**：此技能需要 `google-cloud-aiplatform`。**不要**创建虚拟环境——它初始为空且会隐藏环境已提供的包，强制进行冗余安装。探测并仅安装缺失的部分：

    ```bash
    python3 -c "import vertexai" || pip install google-cloud-aiplatform
    ```

3.  **执行**：使用纯 `python3` 运行 Python 代码片段。无需先激活任何环境。

## 工作流决策树

1.  **信息收集**：您有项目 ID 和区域吗？

    *   **否** -> 您**必须**以纯文本形式向用户询问缺失的项目 ID 和区域，或建议他们检查其 gcloud 配置。如果这两个位置都没有此信息，则询问用户提供。不要自行尝试搜索随机区域。
    *   **是** -> 继续步骤 2。

2.  **任务类型**：用户想要做什么？

    *   **查找或列出作业** -> 使用 Python SDK 列出调优作业。（R 级别）
    *   **检查状态 / 检查特定作业** -> 使用 Python SDK 获取调优作业详细信息。（R 级别）
    *   **取消作业** -> 请求确认，然后使用 Python SDK 取消调优作业。（D 级别）

## 使用 Python SDK

> [!NOTE]
>
> **资源验证与缺失项目/作业**：如果执行 Python 代码片段时出现错误（例如 `403 权限被拒绝`，`404 未找到`，`INVALID_ARGUMENT` 或指示虚拟/缺失项目或作业 ID），您**必须**告知用户项目或调优作业不存在或无法访问。您**必须**提示用户提供有效的项目 ID 或作业 ID，并立即停止工具执行以等待其响应。**不要**重试或循环，**不要**假设资源有效，并且在收到用户提供的有效详细信息之前**不要**执行进一步脚本。

### 1. 列出调优作业（R 级别）

如果用户询问“我正在运行哪些调优作业？”或想要查找特定作业 ID：

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
    print(f"名称: {job.name}")
    print(f"基础模型: {job.base_model}")
    print(f"状态: {job.state}")
```

### 2. 获取特定作业的详细信息（R 级别）

如果用户提供调优作业 ID 并询问其状态：

```python
from google.cloud import aiplatform_v1

project_id = "YOUR_PROJECT_ID"
region = "YOUR_REGION"
job_id = "YOUR_JOB_ID"  # 19位 ID
name = f"projects/{project_id}/locations/{region}/tuningJobs/{job_id}"

client = aiplatform_v1.GenAiTuningServiceClient(
    client_options={"api_endpoint": f"{region}-aiplatform.googleapis.com"}
)

job = client.get_tuning_job(name=name)
print(f"名称: {job.name}")
print(f"基础模型: {job.base_model}")
print(f"状态: {job.state}")
print(f"调优模型: {job.tuned_model_display_name}")
```

### 3. 取消作业（D 级别）

如果用户明确要求停止、中止或取消正在运行的调优作业：

**安全检查**：**操作需要在继续之前进行明确的类型确认。** 您必须在生成或提供此脚本之前请求用户的确认，即使他们提供了作业 ID，除非他们明确使用确认性语言（如“是的，我确认，取消调优作业 123456”）。

> [!IMPORTANT]
>
> **在收到用户在新回合中的响应之前，****永远不要**预先提供或执行任何取消代码。您绝不能猜测或假设会获得确认。在单个并行回合中请求确认并提供代码是一种严重的违规行为。

```python
from google.cloud import aiplatform_v1

project_id = "YOUR_PROJECT_ID"
region = "YOUR_REGION"
job_id = "YOUR_JOB_ID"  # 19位 ID
name = f"projects/{project_id}/locations/{region}/tuningJobs/{job_id}"

client = aiplatform_v1.GenAiTuningServiceClient(
    client_options={"api_endpoint": f"{region}-aiplatform.googleapis.com"}
)

client.cancel_tuning_job(name=name)
print(f"成功请求取消 {name}")
```
