# GCP 管理的 Airflow DAG 编写指南

本指南将指导您为 Managed Service for Apache Airflow (MSAA；以前称为 Cloud Composer) 环境编写和验证 Apache Airflow DAG。

--------------------------------------------------------------------------------

## 第一阶段：环境发现

在编写任何 DAG 代码之前，如果您愿意提供，您必须了解目标环境的约束（例如 Airflow 版本）和能力。

### 1.1 确定目标环境及访问权限

确定您是否可以直接访问目标管理的 Airflow 环境、本地开发环境，或者您是否正在离线工作（仅更改本地文件而不进行验证）。

*   **如果环境访问可用：** 使用 `gcloud` 检查环境（见第 1.3 节）。
*   **如果离线：** 依赖用户提供的信息。

### 1.2 确定开发环境

确定是否存在本地开发环境。

*   检查是否安装了 `composer-dev` 命令行工具。
*   检查是否有一个带有 `airflow` 的本地 Python 环境。

### 1.3 检查目标环境（如果可用且已请求）

运行以下命令以发现版本约束：

1.  **获取 Airflow/镜像版本：**

    ```bash
    gcloud composer environments describe {env_name} \
        --location {region} \
        --format="value(config.softwareConfig.imageVersion)"
    ```

2.  **获取已安装的软件包（版本）：**

    ```bash
    gcloud composer environments describe {env_name} \
        --location {region} \
        --format="value(config.softwareConfig.pypiPackages)"
    ```

3.  **获取 DAG 的 GCS 存储桶：**

    ```bash
    gcloud composer environments describe {env_name} \
        --location {region} \
        --format="value(config.dagGcsPrefix)"
    ```

--------------------------------------------------------------------------------

## 第二阶段：DAG 编写最佳实践

### 2.1 一般 Airflow 最佳实践

*   **幂等性：** 每个任务都应该具有幂等性。使用相同的输入（例如，执行日期）多次运行它应该产生相同的结果，并且不会重复数据。
*   **避免顶层代码执行：** 不要在 DAG 文件的顶层（任务/操作符之外）执行数据库查询、外部 API 调用或重型计算。此代码在 DAG 解析期间每隔几秒运行一次，并将降低性能。
*   **显式回滚：** 在 DAG 定义中始终设置 `catchup=False`，除非明确需要历史回填。
*   **使用 Airflow 变量/连接：** 不要硬编码凭证或特定环境的配置。使用 `Variable.get()`（如果适用，则使用 `deserialize_json=True`）和 `BaseHook.get_connection()`。通过 Jinja 模板（例如，`{{ var.value.my_var }}`）访问变量，以避免在 DAG 解析期间进行数据库调用。

### 2.2 Airflow 2 与 Airflow 3 兼容性

使用 `managed-airflow-migrations` 技能来导航调整代码以适应特定的目标 Airflow 版本。

--------------------------------------------------------------------------------

## 第三阶段：验证过程

在完成任务之前，您必须验证 DAG。

### 3.1 本地验证（离线/预部署）

#### 3.1.1 静态分析及代码检查

如果可用，请使用 `ruff` 或 `pylint`。

```bash
ruff check path/to/dag.py
```

*   如果目标是 Airflow 3，如果有规则集，请使用 Airflow 3 规则进行检查。

#### 3.1.2 本地开发环境 (`composer-dev`)

如果用户配置了 `composer-dev`：

1.  将 DAG 复制到 DAG 目录的本地目录：

    ```bash
    cp path/to/dag.py $(composer-dev describe {local_env} --format="value(dags_directory)")
    ```

2.  验证解析：

    ```bash
    composer-dev run-airflow-cmd {local_env} dags list-import-errors
    ```

### 3.2 目标环境验证

只有当您有 GCP 访问权限并且有权部署到目标环境时，才执行这些步骤。

### 3.2.1 部署到 GCS

将 DAG 上传到目标环境的 GCS 存储桶：

```bash
gcloud storage cp path/to/dag.py gs://{target_bucket}/dags/
```

### 3.2.2 通过 Airflow CLI 验证

等待 1-2 分钟让调度程序解析文件，然后运行：

1.  **检查导入错误：**

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        dags list-import-errors
    ```

*通过标准：* 输出应该是 "No data found" 或空。

2.  **验证 DAG 是否列出：**

    ```bash
    gcloud composer environments run {env_name} \
        --location {region} \
        dags list | grep {dag_id}
    ```

### 3.2.3 监控 Cloud Logging

在 Cloud Logging 中检查运行时解析错误：

```query
resource.type="cloud_composer_environment"
resource.labels.environment_name="{env_name}"
log_id("airflow-scheduler")
severity>=ERROR
textPayload:"{dag_file_name}"
```

--------------------------------------------------------------------------------

## 完成定义

*   DAG 代码符合目标环境的 Airflow 版本约束。
*   DAG 代码遵循最佳实践（没有顶层执行，如果可能则具有幂等性）。
*   DAG 本地解析没有导入错误。
*   （如果环境可用）DAG 已部署到目标环境，并验证没有导入错误。
