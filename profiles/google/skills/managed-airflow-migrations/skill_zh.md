# Apache Airflow 管理服务（原 Cloud Composer）迁移指南

本指南将指导您如何调整现有 Apache Airflow 管理服务（原 Cloud Composer）环境（或本地可用）中的 Airflow DAG 文件，使其与 **Airflow 2.11.1**（MSAA Gen 2 或 3）或 **Airflow 3**（MSAA Gen 3）兼容。

--------------------------------------------------------------------------------

## 第一阶段：发现与下载

在做出任何更改之前，如果明确要求，请下载现有的 DAG 文件。如果明确要求，请检查源环境以确认源版本。有关环境检查和下载文件的详细说明，请参阅
[参考资料/环境检查.md](参考资料/环境检查.md)。

--------------------------------------------------------------------------------

## 第二阶段：目标版本与依赖关系映射

### 2.1 Airflow 2.11.1+ 依赖关系映射

如果迁移到 Airflow 2.11.1（MSAA Gen 2）或 Airflow 3，请使用以下列表跟踪关键依赖关系的版本变化。该列表涵盖了达到 Airflow 2.11.1 所需的更改。在从 Airflow 2（早于 2.11.1）迁移到 Airflow 3 时，请考虑这些更改。

### Composer 2.10.0 (Airflow 2.10.2)

-   **Google 提供者**：`10.26.0`
-   **SSH 提供者**：`3.14.0`
-   **HTTP 提供者**：`4.13.3`
-   **重大变更**：*最旧的完全记录的源的基本线。*

### Composer 2.15.3 (Airflow 2.10.5)

-   **Google 提供者**：`18.0.0`
-   **SSH 提供者**：`4.1.4`
-   **HTTP 提供者**：`5.3.4`
-   **重大变更**：
    -   **SSH 提供者 4.0.0**：移除了 Hook `timeout`；`get_conn()` 上下文管理器。
    -   **HTTP 提供者 5.0.0**：`SimpleHttpOperator` -> `HttpOperator`。
    -   **Google 提供者 11.0.0**：移除了 `BigQueryExecuteQueryOperator`。
    -   **Google 提供者 12.0.0**：移除了遗留数据管道运算符。
    -   **Google 提供者 13.0.0**：移除了 `AutoMLBatchPredictOperator`。
    -   **Google 提供者 17.0.0**：移除了 `BigQueryCreateEmptyTableOperator` 和 `BigQueryCreateExternalTableOperator`；移除了生命科学运算符。
    -   **Google 提供者 18.0.0**：移除了遗留 DV360 运算符。

### Composer 2.16.1 (Airflow 2.10.5)

-   **Google 提供者**：`19.0.0`
-   **SSH 提供者**：`4.1.6`
-   **HTTP 提供者**：`5.5.0`
-   **重大变更**：**Google 提供者 19.0.0**：移除了 AutoML 运算符（使用 Vertex AI）。

### Composer 2.17.0 (目标 Airflow 2.11.1)

-   **Google 提供者**：**`20.0.0`**
-   **SSH 提供者**：**`5.0.0`**
-   **HTTP 提供者**：**`6.0.2`**
-   **重大变更**：
    -   **SSH 提供者 5.0.0**：移除了 `sshtunnel`（原生隧道）。
    -   **HTTP 提供者 6.0.0**：JSON 序列化。
    -   **Google 提供者 20.0.0**：ADLS Gen2 迁移。

### 2.2 Airflow 3 迁移

如果迁移到 Airflow 3（MSAA Gen 3），请注意这是一个主要版本升级，包含重大变更，包括：

*   解耦任务 SDK（导入从 `airflow` 更改为 `airflow.sdk`）。
*   移除直接元数据 DB 访问。
*   将 `Dataset` 重命名为 `Asset`。
*   移除 SubDAGs 和 SLAs。
*   上下文变量可用性变更。

在从 Airflow 2 迁移时（例如，从 Airflow 2.10.2 迁移），请考虑所有适用的变更，并在迁移到 Airflow 2.11.1 后，再应用 Airflow 3 迁移的变更。

--------------------------------------------------------------------------------

## 第三阶段：分析与修复（扫描下载的文件）

在本地工作区的根目录下运行扫描命令（`./migration_workspace`，除非另有说明）。

--------------------------------------------------------------------------------

### 3.1 Airflow 2.11.1 核心 & 依赖关系检查

如果迁移到 Airflow 2.11.1+（迁移到 Airflow 3 的中间步骤），请使用这些扫描。

#### 3.1.1 数据集调度 (Airflow 2.11.0)

*   **变更**：仅当 DAG 处于未暂停状态时，基于数据集调度的 DAG 才会触发事件。
*   **扫描命令**：`grep -rn "Dataset(" ./dags`
*   **修复**：您必须记录这些 DAG 必须保持未暂停以捕获事件，或计划手动触发以进行补录。

#### 3.1.2 描述中的 HTML (Airflow 2.11.0)

*   **变更**：DAG 文档/参数中的原始 HTML 默认情况下会被转义。
*   **扫描命令**：

    ```bash
    grep -rn -E "doc_md.*<|doc_md.*>|description.*<|description.*" ./dags
    ```

*   **修复**：将 HTML 转换为 Markdown，或在目标中设置
    `AIRFLOW__WEBSERVER__ALLOW_RAW_HTML_DESCRIPTIONS=True`。

#### 3.1.3 拆卸任务 (Airflow 2.10.5)

*   **变更**：当 DAG 标记为失败时，拆卸任务始终运行。
*   **扫描命令**：`grep -rn "as_teardown" ./dags`
*   **修复**：确保拆卸任务是幂等的。

#### 3.1.4 Pendulum 3 升级 (Airflow 2.11.0)

*   **变更**：`Period` 重命名为 `Interval`，测试辅助工具已移除。
*   **代码扫描命令**：

    ```bash
    grep -rn -E "pendulum\.Period|pendulum\.period" ./dags
    ```

*   **测试扫描命令**：

    ```bash
    grep -rn -E "\.test\(|set_test_now\(" ./tests 2>/dev/null || true
    ```

*   **修复**：将 `Period` 替换为 `Interval`，将 `period(...)` 替换为 `interval(...)`。

--------------------------------------------------------------------------------

### 3.2 路径 A：Airflow 2.11.1 提供者包扫描

#### 3.2.1 SSH 提供者 (SSH 4.0.0 & 5.0.0)

*   **扫描命令（超时）**：`grep -rn "SSHHook" ./dags | grep "timeout"`
*   **扫描命令（上下文管理器）**：`grep -rn "with SSHHook" ./dags`
*   **扫描命令（隧道属性）**：`grep -rn "\.get_tunnel" ./dags`
*   **修复**：
    *   在 `SSHHook` 中将 `timeout` 替换为 `conn_timeout`。
    *   将 `with hook as conn:` 替换为 `with hook.get_conn() as conn:`。
    *   使用 `get_tunnel()` 作为上下文管理器：`with hook.get_tunnel(...) as
        tunnel:`。

#### 3.2.2 HTTP 提供者 (HTTP 5.0.0 & 6.0.0)

*   **扫描命令**：`grep -rn "SimpleHttpOperator" ./dags`
*   **修复**：将 `SimpleHttpOperator` 替换为 `HttpOperator`。

#### 3.2.3 Google 提供者 (v11 到 v20)

*   **扫描命令（BigQuery 查询）**：

    ```bash
    grep -rn "BigQueryExecuteQueryOperator" ./dags
    ```

    *   *修复*：替换为 `BigQueryInsertJobOperator`（使用 `configuration` 字典）。
*   **扫描命令（BigQuery 表）**：

    ```bash
    grep -rn -E "BigQueryCreateEmptyTableOperator|BigQueryCreateExternalTableOperator" ./dags
    ```

    *   *修复*：替换为 `BigQueryCreateTableOperator`（使用 `table_resource` 字典）。
*   **扫描命令（AutoML）**：

    ```bash
    grep -rn -E "AutoMLTrainModelOperator|AutoMLPredictOperator|AutoMLCreateDatasetOperator|AutoMLBatchPredictOperator" ./dags
    ```

    *   *修复*：迁移到 Vertex AI 运算符。
*   **扫描命令（Dataflow）**：

    ```bash
    grep -rn -E "CreateDataPipelineOperator|RunDataPipelineOperator" ./dags
    ```

    *   *修复*：替换为
        `DataflowCreatePipelineOperator`/`DataflowRunPipelineOperator`。
*   **扫描命令（生命科学）**：

    ```bash
    grep -rn "LifeSciencesRunPipelineOperator" ./dags`
    ```

    *   *修复*：迁移到 Google Cloud Batch 运算符
        (`BatchCreateJobOperator`)。
*   **扫描命令（ADLS 到 GCS）**：`grep -rn "ADLSToGCSOperator" ./dags`
    *   *修复*：确保提供 `file_system_name`。

--------------------------------------------------------------------------------

### 3.3 Airflow 3 迁移检查

迁移到 Airflow 3 时，请使用 [参考资料/airflow-3.md](参考资料/airflow-3.md) 中的说明。

--------------------------------------------------------------------------------

## 第四阶段：部署与验证

*只有在明确要求时才执行部署和验证步骤。*

### 4.1 静态验证（当迁移到 Airflow 3 时）

在应用 Airflow 3 的代码更改后，验证语法正确性。如果在开发环境中可用，请运行静态代码检查：

```bash
ruff check {target_dag_file} --select AIR30
```

在最终确定之前，解决任何报告的弃用警告。如果 ruff 不可用，建议安装一个。

### 4.2 部署到 MSAA

#### 4.2.1 获取目标 GCS 桶路径（仅当请求时）

```bash
gcloud composer environments describe <TARGET_ENV> \
    --location <TARGET_REGION> \
    --format="value(config.dagGcsPrefix)"
```

*预期输出*：`gs://<target-bucket-name>/dags`

### 4.3 上传修改后的 DAG 和桶依赖项（仅当请求时）

*只有在明确要求时才执行此步骤。* 将修改后的 DAG 和任何备份的桶依赖项从您的本地工作区复制到目标 GCS 桶。*如果您跳过了检查步骤，请确保您有正确的 `<target-bucket-name>`。*

1.  **上传 DAG**：

    ```bash
    gcloud storage cp -r ./dags/* gs://<target-bucket-name>/dags/
    ```

2.  **上传其他桶依赖项（如果适用）**：

    ```bash
    gcloud storage cp -r ./migration_workspace/<dependency-folder> gs://<target-bucket-name>/<dependency-folder>
    ```

### 4.4 通过 Airflow CLI 验证 DAG

*只有在明确要求将修改后的 DAG 上传到目标环境（并且上传后）才执行此步骤。*

您可以使用 Airflow CLI 验证您的 DAG 已成功上传、解析并在目标环境中注册。

1.  **列出注册的 DAG**：运行以下命令以列出目标环境中注册的所有 DAG。验证您的迁移的 DAG 是否出现在此列表中。

    ```bash
    gcloud composer environments run <TARGET_ENV> \
        --location <TARGET_REGION> \
        dags list
    ```

2.  **检查导入错误**：如果某些 DAG 缺失在列表中，或者为了确保没有解析问题，请检查导入错误：

    ```bash
    gcloud composer environments run <TARGET_ENV> \
        --location <TARGET_REGION> \
        dags list-import-errors
    ```

    *预期输出*：

    *   如果没有错误，命令将输出 `No data found`。
    *   如果有错误，它将列出文件路径和错误的堆栈跟踪。

*注意：Airflow 调度器解析新文件并使更改反映在这些命令中可能需要几分钟时间。*

### 4.4 在 Cloud Logging 中验证

*只有在明确要求将修改后的 DAG 上传到目标环境（并且上传后）才执行此步骤。* 监控目标环境的 Cloud Logging 以检测任何运行时错误或导入错误。

在 **GCP Cloud Logging 控制台**（或通过 `gcloud logging read`）中运行以下查询：

```query
resource.type="cloud_composer_environment"
resource.labels.environment_name="<TARGET_ENV>"
log_id("airflow-scheduler")
severity>=ERROR
```

--------------------------------------------------------------------------------

## 附录：本地环境验证

如果您希望在部署到目标环境之前在本地验证您的更改，您可以使用 Composer 本地开发 CLI 工具（`composer-dev`）。使用
[参考资料/本地开发环境.md](参考资料/本地开发环境.md) 作为与本地开发环境交互的参考。
