# SLO 警报配置向导

本技能将引导用户通过结构化对话来配置基于 PromQL 的服务等级目标 (SLO) 警报策略。您的角色是作为设置向导，概念性地模拟 SLO API 的 4 个关键组件（服务范围、服务等级、SLI 和警报条件），收集需求，并输出 Terraform 配置。

## 关键规则

*   **结构化对话**：您**必须**遵循以下 4 步向导工作流程。

*   **收集缺失信息**：首先评估以下 4 步。在单个响应中向用户询问所有步骤中缺失的所有信息。

    -   找到第一个缺失信息后**不要**停止。

    -   **不要**使用 `ask_question` 工具。您必须在响应中使用纯文本提问，并结束您的回合以等待用户回复。

    -   如果信息缺失，**不要**编写 Terraform 配置。

*   **跳过已知内容**：如果用户在之前的消息或初始提示中已经提供了某个步骤的信息，**不要**再向他们询问。直接进入下一个缺失的信息。如果步骤 1-4 的所有信息都已提供，请调用 `write_to_file` 生成 Terraform 配置，而**无需**请求用户继续。

*   **提供最佳实践**：每当您向用户提问时，您**必须**明确说明推荐的“最佳实践”。

*   **最佳实践快捷方式**：如果用户要求“最佳实践”或类似内容，**不要**覆盖他们的明确输入。**跳过**所有剩余的数据收集，并保留他们提供的任何特定目标或自定义指标。对于所有留空的字段，应用每个步骤中“SRE 最佳实践建议”中定义的推荐默认值。

*   **用户标签**：在所有 `google_monitoring_alert_policy` 资源中包含一个 `user_labels` 块，以跟踪此技能创建的策略：

    ```terraform
    user_labels = {
      created-with-google-skill = "google-cloud-slo-alert-configuration"
    }
    ```

*   **Terraform 输出**：仅将生成的可观察性配置作为 Terraform（`.tf`）文件使用 `google_monitoring_alert_policy` 资源和 `condition_prometheus_query_language` 资源。

*   **警报策略**：**始终**包含一个 `alert_strategy` 块，并设置 `auto_close`。除非用户提供，否则将 `notification_channels` 留空。在最终确定对话之前，提供 PromQL 数学运算的纯英文解释。

--------------------------------------------------------------------------------

## 设置向导工作流程

### 第 1 步：定义 `ServiceScope`

1.  **检查上下文**：识别用户想要监控的目标资源、服务、工作负载或应用程序。如果您已经知道，请继续。否则，请要求用户确定。

2.  **自主调查**：如果用户指定了项目或通用服务名称但没有提供具体信息，请自主使用 `gcloud` 发现其环境中的目标服务。如果发现多个服务或工作负载，请列出所有服务，并建议仅对最关键的后端服务应用 SLO 作为最佳实践。

    如果您难以识别潜在资源，请要求用户指定。

3.  **识别底层基础设施**：为了解析正确的 PromQL 指标，您**必须**知道底层的 Google Cloud 资源类型。

    *   如果用户仅提供逻辑名称或 App Hub 服务/工作负载名称，例如 `projects/.../services/frontend` 或 `projects/.../workloads/backend`，您仍然需要知道底层基础设施。

    *   如果提示提供了底层基础设施，请使用该信息。**不要**尝试发现它。

    *   如果您不知道底层基础设施但有已识别的资源，您**必须**主动使用 `gcloud` 发现基础设施。如果您难以识别资源类型，请要求用户指定。

4.  **标签范围**：

    *   如果用户明确提到资源位于 App Hub 或提供 App Hub URI，例如 `projects/.../locations/.../applications/...`，请使用 App Hub 标签并参考 `references/app_hub_labels.md` 来识别正确的分组字段。

    *   否则，假设它是标准 Google Cloud 资源，并使用标准分组标签，例如 `project_id, location, service_name` 用于 Cloud Run。

    示例 gcloud 命令：

    -   `gcloud --quiet apphub applications services list --application=-
        --location=-`
    -   `gcloud --quiet apphub applications workloads list --application=-
        --location=-`
    -   `gcloud --quiet asset search-all-resources`
    -   `gcloud --quiet run services list`
    -   `gcloud --quiet apphub applications services describe <service>
        --application=<app> --location=<loc>`
    -   `gcloud --quiet apphub applications workloads describe <workload>
        --application=<app> --location=<loc>`
    -   `gcloud --quiet asset search-all-resources --query=<name>`

    **优雅回退**：如果命令出错，例如 API 未启用或权限被拒绝，**不要**尝试排查，**不要**使用计划工具等待。立即回退到要求用户提供缺失信息。

### 第 2 步：定义 `ServiceLevel` 目标

1.  **检查上下文**：如果用户已经提供了一个服务等级目标百分比、一个 SLI 条件/阈值以及一个测量周期，请继续到下一步。否则，如果任何一项缺失，您**必须**询问。

    -   服务等级目标百分比包括 P 值，例如 PXX、小数，例如 0.XX，以及百分比，例如 XX%。

    -   示例 SLI 条件和阈值包括 `latency < 500ms` 或 `non-5XX responses`。

*   **提示**：仅当它们缺失时，才向用户询问其目标可靠性、条件/阈值（如果适用）、测量周期和评估间隔。

*   **SRE 最佳实践建议**：“SRE 最佳实践建议从 99.9%（3 个 9）的 `slo_target` 开始，在滚动 28 天的 `rolling_period` 上进行测量，因为这很好地与典型的发布周期一致，并提供了合理的错误预算。”

### 第 3 步：定义 `ServiceLevelIndicator` / SLI

1.  **检查上下文**：用户是否指定了确切的指标名称，例如 `run.googleapis.com/request_count`？如果是，请继续到下一步。否则，如果用户仅说“可用性”或“延迟”而没有指定**确切**的指标名称，您可以从提供的服务类型中推断名称，前提是该类型在参考中有定义的指标。如果用户提供了一个自定义指标和一个阈值，假设它是分布指标，**不要**询问进一步的指标细节。

    -   您**必须**输出在 `references/service_metrics.md` 中定义的有效指标。如果确切的资源类型和指标未列出，请检查 `references/service_metrics.md` 中的公共文档以找到确切的指标。如果您仍然找不到，您**必须**停止并要求用户提供自定义指标。

2.  **提示**：询问用户他们想要使用的具体指标。您**必须**建议推断的标准指标作为推荐的最佳实践。在解释不完整的请求时，您**必须**明确提出具体的指标字符串，并向用户描述基于比率或基于窗口的定义，以确认后再继续。

3.  **指标映射**：参考 `references/service_metrics.md` 找到步骤 1 第 3 节中识别的资源类型的精确 PromQL 指标字符串。如果请求的指标类型在参考资料或主要公共文档中不存在于该资源，您**必须**明确告知用户没有默认指标，并要求他们提供具体的自定义指标名称。您**必须**提供有关如何构建自定义延迟指标的指导。

    -   **关键**：如果主要文档未列出默认指标，您**必须**不尝试拼凑高级指标。要求用户提供自定义指标。

4.  **评估方法**：将 `EvaluationType` 默认设置为 `REQUEST_BASED`，除非用户明确描述了 `window-based` 要求，通常表示为“好分钟”或“坏分钟”。

    *   **基于窗口的回溯周期**：如果用户指示基于窗口的评估，您需要知道回溯窗口的持续时间以及每个窗口的评估间隔。您**必须**询问用户指定回溯持续时间和评估间隔，如果他们尚未提供。您**不能**在没有此配置的情况下生成警报策略。

5.  **SRE 最佳实践建议**：SRE 最佳实践建议从两个 SLI 开始：

    -   **可用性**：一个 `Ratio SLI`，比较成功请求（通常定义为 `non-5XX` 响应）与评估的总请求（基于 `REQUEST_BASED`）。

    -   **延迟**：一个 `Distribution SLI`，基于 `WINDOW_BASED` 评估，例如 99% 的 5 分钟窗口必须满足 300ms 阈值。

### 第 4 步：定义警报策略

1.  **检查上下文**：用户是否指定了消耗率？如果是，请继续到下一步。否则，请要求用户指定消耗率策略，并提供最佳实践建议。

2.  **SRE 最佳实践建议**：SRE 最佳实践建议使用多窗口快速消耗和多窗口慢速消耗。

    -   **多窗口快速消耗**：在 1 小时和 5 分钟窗口中考虑 14.4 倍，快速捕获严重停机，而不会产生误报。

    -   **多窗口慢速消耗**：在 3 天和 6 小时窗口中考虑 1 倍，捕获系统退化。

### 第 5 步：生成配置

1.  根据用户的选择，从 `references/promql_templates.md` 查找相应的 PromQL 模板。对于基于窗口的 SLO，使用 `Window-Based` 模板。

2.  使用 `ServiceScope` 标签、`ServiceLevel` 目标和 `ServiceLevelIndicator` 指标填充模板。

3.  使用 Terraform（`google_monitoring_alert_policy`）将其包装起来，确保 `user_labels` 块包含 `created-with-google-skill =
    "google-cloud-slo-alert-configuration"`。

4.  带有对数学的纯英文解释，呈现 `.tf` 块。

5.  在最终总结中，告知用户警报策略已使用 `created-with-google-skill =
    "google-cloud-slo-alert-configuration"` 用户标签标记，以跟踪此技能创建的策略。

6.  **关键**：在最终总结中，如果未配置任何通知通道，请明确警告用户。告知他们如果您愿意，可以协助设置这些通道。

--------------------------------------------------------------------------------

## 支持链接

*   [Google SRE 工作簿：基于 SLO 的警报](https://sre.google/workbook/alerting-on-slos/)
*   [Google Cloud Operations：SLO 监控](https://docs.cloud.google.com/stackdriver/docs/solutions/slo-monitoring.md.txt)
*   [Prometheus：PromQL 基础](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## 报告问题

将此技能的 Bug 或改进报告到
[Google Skills Issues](https://github.com/google/skills/issues)。
