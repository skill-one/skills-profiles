# TPU连接失败和VBAR内存耗尽问题排查

使用此技能系统性地诊断和预防TPU v6e节点上的`vbar_control_agent`段错误和内存耗尽（OOM）错误。

## ⚠️ 前置条件

-   项目必须启用云日志记录。
-   通过`gcloud`或等效工具访问项目和集群。

## 🔍 诊断工作流

### 第0步：上下文获取和时间窗口定义

使用可用的GCP/GKE工具独立收集所需上下文，或使用提供的`{variable}`占位符：

-   `{project_id}`：GCP项目ID（例如，`customer-ai-project-123`）。
-   `{cluster_name}`：GKE集群名称（例如，`tpu-cluster-prod`）。
-   `{node_name}`：节点名称或实例ID（例如，`tpu-node-1`）。
-   `{workload_name}`：工作负载名称/作业集名称（例如，`my-training-job-456`）。
-   `{namespace}`：工作负载命名空间。
-   `{issue_time}`：问题时间戳（例如，`2026-04-14T20:00:00Z`）。

#### 时间处理与执行规则

1.  **窗口计算**：如果提供了问题时间戳`{issue_time}`，计算查询时间窗口为`[{issue_time} - 30m]`到`[{issue_time} + 30m]`。
    -   令`{start_time}` = `{issue_time} - 30m`
    -   令`{end_time}` = `{issue_time} + 30m`
2.  **信息性查询与实时执行**：如果用户请求是信息性的或查询形式（例如，“如何检查...”，“如何确定...”），或者如果实时GCP项目资源无法被主动目标，则直接输出计算的时间窗口、日志名称和云日志记录过滤器模板，而无需尝试实时日志执行命令。

### 第1步：检查`vbar_control_agent`内存耗尽

在串行控制台日志（`serialconsole.googleapis.com%2fserial_port_1_output`）中查找来自`vbar_control_agent`的特定内存耗尽消息。

-   **使用的工具**：`query_logs`（用于实时诊断）
-   **过滤器模板**：

**串行控制台日志（内存耗尽）**：

```sql
logName="projects/{project_id}/logs/serialconsole.googleapis.com%2fserial_port_1_output"
AND labels."compute.googleapis.com/resource_name"="{node_name}"
AND SEARCH(text_payload, "Memory cgroup out of memory: Killed process .* (vbar_control_ag)")
AND timestamp >= "{start_time}"
AND timestamp <= "{end_time}"
```

-   **逻辑**：存在与`vbar_control_agent`相关的`Memory cgroup out of memory`消息。指向`libtpu::tpunetd::VBARControlHelper::MetricsReadFromVBAR`的堆栈跟踪是强烈指示。
-   **自动化**：报告发现后自动进入下一步。
-   **参考**：参见`references/failure_signatures.md`查看示例日志模式。

### 第2步：调查`tpu-device-plugin`指标获取失败 [低风险]

检查`tpu-device-plugin`是否报告指标获取失败。

-   **使用的工具**：`query_logs`
-   **过滤器模板**：

```sql
resource.type="k8s_container"
AND resource.labels.project_id="{project_id}"
AND resource.labels.cluster_name="{cluster_name}"
AND resource.labels.container_name="tpu-device-plugin"
AND severity=ERROR
AND textPayload:"metrics fetch failed for .* deviceID and .* device path with error: checksum didn't match with the metrics data. Corrupt data found"
AND timestamp >= "{start_time}"
AND timestamp <= "{end_time}"
```

-   **逻辑**：指示“metrics fetch failed”且“checksum didn't match”的错误表明vBAR内存损坏。
-   **自动化**：报告发现后自动进入下一步。

### 第3步：检查自定义指标收集使用情况 [低风险]

检查集群配置、工作负载或容器规范，以确定是否部署了自定义TPU指标收集机制。

-   **操作**：检查是否部署了自定义脚本或代理（例如，使用`libtpu.sdk.tpumonitoring`）频繁从`vBAR Control Agent`查询`GetHostMetrics`。
-   **验证命令**：

    -   **Kubectl搜索（检查工作负载环境/规范）**：

    ```bash
    kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"/"}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
    ```

    -   **日志搜索过滤器（`query_logs`）**：

    ```sql
    resource.type="k8s_container"
    AND resource.labels.project_id="{project_id}"
    AND resource.labels.cluster_name="{cluster_name}"
    AND textPayload:"libtpu.sdk.tpumonitoring"
    AND timestamp >= "{start_time}"
    AND timestamp <= "{end_time}"
    ```

-   **逻辑**：确认自定义指标收集有助于确认竞争条件假设。

## 🛠️ 解决方案工作流

### 解决方案1：暂时禁用自定义指标收集 [高风险]

如果识别到自定义指标收集代理，建议禁用它。

-   **操作**：建议禁用自定义指标收集器。
-   **理由**：防止在设备重置期间从vBAR读取，停止崩溃和OOM。

### 解决方案2：等待`vbar_control_agent`弹性更新 [低风险]

建议永久修复将在未来的GKE版本中提供。

-   **操作**：建议在修复可用时升级GKE。
-   **理由**：更新的代理将能够抵抗内存损坏，并优雅地处理来自未绑定vBAR的读取。

## 📋 copypaste清单

-   [ ] 获取上下文并计算`[{start_time}, {end_time}]`窗口。
-   [ ] 使用`query_logs`检查`vbar_control_agent`段错误和OOM。
-   [ ] 使用`query_logs`调查`tpu-device-plugin`失败。
-   [ ] 检查自定义指标收集使用情况。
-   [ ] 如适用，建议禁用自定义指标收集。
-   [ ] 建议等待弹性更新。
