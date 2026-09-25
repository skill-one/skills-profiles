# Apache Airflow 管理服务 (原 Cloud Composer) DAG 排错指南

本指南提供有关排错管理 Airflow DAG (DAG 运行和任务实例) 的说明，利用 `gcloud composer`、`gcloud logging` 和 `gcloud storage` 命令获取远程日志和代码。

## 一般规则

1.  提供有关如何排错失败任务的建议。仅提供用户实际可以采取的步骤。所有排错建议都必须基于直接发现。
2.  在排错失败时，遵循以下实践，始终提供可确定的诊断：

    *   **获取相关日志**：始终使用 `gcloud logging read` 获取正在调查的任务的日志；检查日志中的特定错误模式：Python 追踪、API 错误代码（例如，400、403、404、500）或 Airflow 信号（例如，`AirflowTaskTimeout`）。
    *   **获取任务元数据**：在排错任务时，使用以下命令获取任务状态和元数据（执行状态、尝试次数、时间戳和执行详细信息）：

        ```bash
        gcloud composer environments run {env_name} \
            --location {location} \
            tasks states-for-dag-run -- -d {dag_id} -r {run_id}
        ```

        或对于单个任务实例：

        ```bash
        gcloud composer environments run {env_name} \
            --location {location} \
            tasks state -- {dag_id} {task_id} {execution_date}
        ```
    *   **检索并比较 DAG 源代码**：使用 `gcloud storage cp gs://{bucket_name}/dags/{dag_file}.py .` (通过 `gcloud composer environments describe {env_name} --location {location} --format="value(config.dagGcsPrefix)" 找到环境存储桶) 下载远程 DAG 源代码。将代码中的参数（例如，表 ID、磁盘大小、URI 路径）与任务日志中发现的错误消息进行比较。
    *   **解释代码错误和潜在修复方案**：解释代码中的错误（如果实际可见）；建议潜在的修复方案（如果它们很可能有意义）；如有必要，讨论源代码可用性 - 如果某些源代码不可用（例如，从主源代码文件以外的文件导入），请提及（可以提及包名）- 在这种情况下，考虑最可能的触发规则（如果未知）。
    *   **检查环境级错误**：使用 `gcloud logging read` 查询 Cloud Logging，查看是否存在高级环境问题或与失败相关的已知平台错误（见 **已知问题** 下）。你必须返回所有发现的问题。
    *   **识别 DAG 运行中的失败任务**：在排错失败的 DAG 运行时，提及导致失败的特定任务（使用 `tasks states-for-dag-run` 或 Cloud Logging 来识别失败的任务）。提供任务实例名称。如果许多任务失败，请提及哪个任务是关键的（对于成功执行 DAG 运行是必需的 - 查看任务依赖关系和触发规则），并专注于这一个。
    *   **验证代码中的服务配置**：如果日志表明特定服务存在问题（例如，BigQuery、Dataform、Compute Engine），请使用日志详细信息来验证 DAG 源代码中的配置。
    *   **将日志与代码关联**：例如，如果 BigQuery 返回 404，请验证 DAG 源代码中的数据集 ID 或表 ID 是否与现实相符。
    *   **优先考虑已知平台问题**：检查 **已知问题** 下。如果 Cloud Logging 查询返回匹配的平台错误信号，请优先考虑该诊断。

3.  **总结证据（确定性响应）**：你的响应必须具体。避免提供一般性建议，如“检查你的权限。”或“检查日志。”。相反，你应该说“服务账户缺少 X 权限。”

    *   **问题**：陈述具体的根本原因和确切的任务实例 ID。确定它是代码逻辑错误、配置不匹配还是环境超时。
    *   **证据**：**必须**。提供日志 (`textPayload`) 或 DAG 中导致失败的特定代码行的逐字文本。不要总结证据；显示数据。
    *   **建议**：提供可操作的修复方案。如果是代码错误，请提供修正的 Python 片段。如果是资源问题，请指定需要的确切配置更改。

4.  **由编排管道生成的 DAG**：某些 DAG 可能由编排管道生成。与这些 DAG 相关的特殊要求是，需要根据管道 YAML 中定义的逻辑操作来解释失败。

    *   **确定 DAG 是否由编排管道生成**：
        由专用工具部署的编排管道 DAG 在它们的 DAG 运行元数据（包含 JSON 元数据的 `DagRun.note`）中设置了 `bundle_name`、`version_id` 和 `pipeline_name`。所有这些（即由专用工具部署的编排管道 DAG 和手动创建的 DAG）都具有 `op:orchestration_pipeline` 标签设置（DAG 属性，包括标签，可以在 DAG 源代码中验证，或通过 `gcloud composer environments run {env_name} --location {location} dags list` 验证）。
    *   由专用工具部署的编排管道 DAG 还具有以下标签（这些标签中的信息应与上述 DAG 运行属性中的数据一致）：
        *   管道名称 - 标签 `op:pipeline`，例如 `op:pipeline:xyz` 表示名称 `xyz`
        *   包名称 - 标签 `op:bundle`
        *   版本 ID - 标签 `op:version`
    *   **从环境存储桶检索解析的管道 YAML 定义**：
        *   确定 YAML 文件位置：
            1.  使用 `gcloud storage cp gs://{bucket_name}/dags/{dag_file}.py .`（或 `gcloud storage cat gs://{bucket_name}/dags/{dag_file}.py`）从环境存储桶检索 DAG 源代码。
            2.  检查源代码中的 `generate` 或 `generate_dags` 函数调用：
                *   情景 1：找到 `generate` 调用。第一个参数是相对于环境存储桶中 `dags` 文件夹的 YAML 文件路径。
                *   情景 2：找到 `generate_dags` 调用。
                    *   提取第一个参数 - 这是数据文件夹。如果它以 `/home/airflow/gcs/` 开头，请删除此前缀以获得相对于环境存储桶根目录的路径。
                    *   提取 `bundle_name`、`version_id` 和 `pipeline_name`（如上所述）。
                    *   构建路径：
                        `{data_directory}/{bundle_name}/versions/{version_id}/{pipeline_name}.yml`（或 `.yaml`）。
                *   情景 3：如果未找到任何调用，则默认为环境存储桶中的路径：
                    `data/{bundle_name}/versions/{version_id}/{pipeline_name}.yml`（或 `.yaml`）。
            3.  使用 `gcloud storage cp gs://{bucket_name}/{yaml_path} .`（或 `gcloud storage cat gs://{bucket_name}/{yaml_path}`）下载 YAML 文件。
    *   使用任务实例元数据/注释将失败的 Airflow 任务映射回逻辑操作名称（例如，任务 `note` 中的 `op_action_name`）。
    *   如果失败涉及用户资产（如 Python 脚本），请检查它们在操作定义中的路径。如果它们在环境存储桶中，请下载并阅读它们以进行调试 (`gcloud storage cp gs://{bucket_name}/{asset_path} .`)。如果它们在自定义工件存储桶中（见日志/配置中的 GCS URI），请注意它们不能直接读取的限制，但可以根据可用日志进行分析。

5.  你可以假设默认设置的环境变量（它们可以在 DAG 代码中使用，但在自定义环境配置中不可见），例如 `GCS_BUCKET`，是正确的 - 用户无法更改它们。

6.  GCP API 返回的“未找到”（404）错误可能具有误导性。当资源实际上存在，但调用者没有权限访问或查看它时，可能会返回“未找到”错误。如果预期存在资源，建议验证正确的权限。

### 重要约束和说明

*   **首先只读**：**不要**立即尝试修复代码。你必须首先使用日志和远程代码证明根本原因。
*   **不要猜测**：如果日志为空或代码无法找到，请明确说明。始终引用错误消息。
*   **安全**：小心处理密钥。如果日志包含敏感信息（例如，密码），请在分析中对其进行编辑。

### 应用修复 - 仅在明确请求时

当根本原因分析完成且修复方案准备就绪时：

1.  **仓库检查**：如果当前工作区似乎不是管理 Airflow 环境的真相来源：
    *   要求用户**打开正确的仓库**。
    *   或者询问他们是否希望将远程 DAG**下载到当前工作区以应用修复**（警告他们可能存在覆盖风险）。

## 相关 gcloud 命令

### 环境和 DAG 发现

*   **列出 composer 环境**：

    ```bash
    gcloud composer environments list \
        --locations=us-central1 \
        --format="table(name,location,state)"
    ```
*   **描述环境（获取 DAG 存储桶和配置）**：

    ```bash
    gcloud composer environments describe {env_name} \
        --location {region} \
        --format="value(config.dagGcsPrefix)"
    ```
*   **列出 composer DAG**：

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        dags list
    ```
*   **列出 composer DAG 运行**：

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        dags list-runs -- -d {dag_id} --no-backfill
    ```
*   **列出 DAG 运行中的任务实例状态**：

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        tasks states-for-dag-run -- -d {dag_id} -r {run_id}
    ```
*   **获取特定任务实例的状态**：

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        tasks state -- {dag_id} {task_id} {execution_date}
    ```

### 日志检索

*   **获取 DAG / 任务错误日志**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND labels.dag_id="{dag_id}" AND severity>=ERROR' \
        --limit=25 \
        --format="table(timestamp,severity,labels.task_id,textPayload)"
    ```
*   **获取环境失败的任务调度器日志**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND log_id("airflow-scheduler") AND severity>=ERROR' \
        --limit=25 \
        --format="table(timestamp,severity,textPayload)"
    ```

### 代码和资产检索

*   **从 GCS 下载 DAG 代码**：

    ```bash
    gcloud storage cp gs://{bucket_name}/dags/{dag_file}.py .
    ```
*   **从 GCS 下载管道 YAML 定义或脚本**：

    ```bash
    gcloud storage cp gs://{bucket_name}/{path_to_file} .
    ```

## 与 DAG 运行和任务实例相关的已知问题

使用以下查询与 `gcloud logging read` 来识别特定的已知平台失败模式：

### 1. DAG_RUN_TIMEOUT

*   **问题摘要**：由于 DAG 超时，任务实例执行被中断。未完成的任务被标记为“跳过”或失败。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND log_id("airflow-scheduler") AND textPayload=~"Run .* of .* has timed-out"' --limit=10
    ```

### 2. TASK_QUEUED_TIMEOUT

*   **问题摘要**：任务失败，因为它在最大允许队列时间后仍然处于排队状态。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND log_id("airflow-scheduler") AND textPayload=~"Task requeue attempts exceeded max; marking failed"' --limit=10
    ```
*   **修复**：考虑增加工作者资源（CPU、内存、工作者数量）或调整 `[celery]worker_concurrency`。

### 3. TASK_STUCK_IN_QUEUE

*   **问题摘要**：任务达到 DAG 运行超时，因为任务在队列中停留时间过长。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND log_id("airflow-scheduler") AND textPayload=~"Task stuck in queued; will try to requeue"' --limit=10
    ```
*   **修复**：考虑增加超时或减少环境负载。

### 4. BIGQUERY_JOB_FAILED

*   **问题摘要**：由于 BigQuery 管理器中的 BigQuery 操作失败，任务失败。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND (log_id("airflow-worker") OR log_id("airflow-k8s-worker")) AND textPayload:"airflow/providers/google/cloud/operators/bigquery.py" AND textPayload:"Task failed with exception" AND severity=ERROR' --limit=10
    ```
*   **修复**：检查工作者日志中的 BigQuery Job ID (`Job ID: ...`) 以诊断底层查询错误或权限问题。

### 5. DETECTED_ZOMBIE

*   **问题摘要**：执行者由于缺少心跳而撤销了任务实例。任务实例定期发送心跳（默认每 `job_heartbeat_sec`，即 5 秒），如果心跳缺失超过 `scheduler_zombie_task_threshold`（默认 300 秒），则任务被视为僵尸并标记为失败或准备重试。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND log_id("airflow-scheduler") AND (textPayload:"Detected zombie job:" OR textPayload:"Detected a task instance without a heartbeat:")' --limit=10
    ```
*   **修复**：这可能是当工作者过载（CPU/内存饥饿）而无法按时发送心跳，工作者被终止且任务未完成（OOM kill/eviction），或元数据数据库过载时发生的。检查工作者指标并考虑扩展工作者 CPU/内存。

### 6. WORKER_OUT_OF_POD_STORAGE

*   **问题摘要**：任务实例失败，因为工作者正在耗尽 Pod 存储（临时磁盘空间达到上限或由于存储限制 Pod 被驱逐）。
*   **Cloud Logging 查询**：

    ```bash
    gcloud logging read 'resource.type="cloud_composer_environment" AND resource.labels.environment_name="{env_name}" AND (log_id("airflow-worker") OR log_id("airflow-k8s-worker")) AND textPayload:"Pod ephemeral local storage usage exceeds the total limit of containers"' --limit=10
    ```
*   **修复**：根据存储的数据量更新工作者存储配置或清理任务执行期间创建的临时文件。
