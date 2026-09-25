# 代理平台警报配置

## 关键步骤

### 1. 安全与确认层级（关键）

在代表用户执行任何命令或编写配置之前，
你必须严格遵守以下基于请求操作的安全层级：

1.  **层级 R：只读（`check_telemetry.py` / `gather_agent_info.py`）**
    *   **规则**：无需确认。你可以立即执行这些脚本
        来检查遥测状态或收集代理配置详情。
2.  **层级 B：计费与资源创建（`create_online_monitor.py` /
    配置）**
    *   **规则**：**需要明确用户确认**。这些操作会产生额外的计费费用并创建云资源。代理必须始终明确警告用户 Online Monitor（特别提及 **LLM 评估**）和遥测（特别提及 **Cloud Trace/Cloud Logging 导出**）的潜在额外计费成本。你必须停止操作并请求明确批准后再进行配置或提供设置命令。

### 2. 前置条件与依赖项

#### 代理遥测

*   **免责声明**：为了使可靠性、成本、安全和安全警报能够正常工作，底层的代理必须被仪器化以发出 OpenTelemetry (OTel) 指标。如果代理不发出这些指标，警报策略将没有要评估的数据流。

#### Python 环境

在执行此技能中的任何 Python 脚本之前，你必须先在你的环境中安装所需的依赖项。首先运行此命令：

```bash
pip install -r scripts/requirements.txt
```

### 3. 输入假设

*   **明确项目遵循**：你必须仅配置警报、查询遥测或与用户在提示中明确提供的 Google Cloud 项目交互。除非用户明确指示你这样做，否则不要假设或使用环境或历史记录中的其他项目。
*   **顺序文件转换**：如果用户明确要求复制文件然后修改它，你必须按顺序执行这些操作（先复制，然后修改），而不是直接写入最终内容。

### 4. 执行步骤

1.  **强制前置条件执行协议（顺序）**：在生成或写入任何配置之前，你必须按顺序执行以下步骤：
    1.  **步骤 1：简化的发现（强制）**：运行 `gather_agent_info.py` 以自动识别代理运行时、验证遥测、指标范围、关联数据集等。此脚本涵盖了后续步骤中列出的大部分手动验证。
        *   命令：`python3 scripts/gather_agent_info.py --project-id
            {project_id} --agent-name {agent_name}`
        *   **注意**：如果此脚本**失败**、返回**部分数据**或无法提供所需的所有信息，你必须通过运行步骤 2 中列出的手动回退步骤来满足要求，然后执行步骤 3 中的操作。如果步骤 1 成功并提供所有信息，**跳过**到步骤 3（现有策略验证）。
    2.  **步骤 2：指标范围验证（回退）**：仅在步骤 1 无法确定指标范围时运行。
        *   **操作 A（CLI）**：运行 `gcloud beta monitoring metrics-scopes list
            projects/{project_id}`。如果返回了范围项目，你必须将策略部署在那里。
        *   **操作 B（代码扫描）**：搜索 Terraform 配置文件以提取 `google_monitoring_monitored_project` 资源来获取范围项目。
        *   **操作 C（回退）**：如果存在歧义，向用户提问：“您是否使用多项目 Cloud Monitoring 指标范围？如果是，范围项目 ID 是什么？”
    3.  **步骤 3：现有策略验证**：避免重复。
        *   **操作**：扫描目标目录以查看是否已存在针对相同指标的聚合策略（按 `reasoning_engine_id` 或 `gen_ai_agent_name` 分组）。使用 `scan_duplicates.py` 进行验证。
2.  **警报策略类型资源文件**：你必须列出并读取 `references/` 下以 `_alert_policies.md` 结尾的文件，以了解如何根据类型配置警报策略。默认情况下，你必须配置以下所有警报类型，除非用户请求生成明确的警报策略和/或类型。请参考他们的目录以帮助你找到需要阅读的参考部分：

    警报类型      | 参考文件
    :-------------- | :-------------
    **可靠性**     | [reliability_alert_policies.md](references/reliability_alert_policies.md)
    **质量**       | [quality_alert_policies.md](references/quality_alert_policies.md)
    **成本**       | [cost_alert_policies.md](references/cost_alert_policies.md)
    **安全**       | [safety_alert_policies.md](references/safety_alert_policies.md)
    **安全**       | [security_alert_policies.md](references/security_alert_policies.md)

### 5. 输出与格式

*   **始终为目标代理配置支持的警报策略**：
    *   **对于可靠性监控**：你必须配置五个警报策略：
        1.  **延迟**（异常监控）
        2.  **错误率 - 快速燃烧 SLO**（1 小时窗口）
        3.  **错误率 - 慢速燃烧 SLO**（3 天窗口）
        4.  **模型调用错误率**（基于 SQL 的可观察性分析警报）
        5.  **工具调用错误率**（基于 SQL 的可观察性分析警报）
    *   **对于质量监控**：你必须配置三个警报策略（需要 Vertex AI 在线监控器）：
        1.  **最终响应质量**
        2.  **工具使用质量**
        3.  **幻觉**
    *   **对于成本监控**：你必须配置一个成本警报策略：
        1.  **快速 token 燃烧率**（异常监控）
    *   **对于安全监控**：你必须配置一个安全警报策略：
        1.  **高模型装甲安全策略触发率**（基于 SQL 的可观察性分析警报）
    *   **对于安全监控**：你必须配置一个安全警报策略：
        1.  **高 IAM 权限拒绝触发率**（基于 SQL 的可观察性分析警报）
*   **仅限 Terraform**：仅将生成的可观察性配置作为 Terraform（`.tf`）文件（例如 `alerts.tf`、`variables.tf`）写入。
    -   你**仅**需要在被要求部署警报且没有有效 Terraform 安装的情况下安装 Terraform。使用 `condition_sql` 的基于 SQL 的警报需要提供版本 **>= 6.0.0**（或支持该功能的较新 5.x 版本）。
    -   如果你**不**被要求部署警报，则无需安装 Terraform。
*   **动态多资源警报（无单一资源固定）**：你必须不在警报条件中硬编码特定的代理 ID 或资源名称过滤器（例如，
    `{gen_ai_agent_name="{agent_name}"}` 或
    `metric.labels.agent_resource_name="{agent_name}"`），除非用户明确要求（例如，“仅针对此代理”）。在请求中提及特定代理名称或 ID **不构成**明确请求固定/过滤；你必须仍然默认使用动态分组以涵盖所有代理。要动态涵盖项目中的所有活动代理：

    *良好示例（PromQL 分组）*：

    ```promql
    sum(rate(workload_googleapis_com:gen_ai_invoke_agent_duration_count{monitored_resource="generic_node"}[5m])) by (gen_ai_agent_name)
    ```

    *不良示例（PromQL 硬编码过滤器）*：

    ```promql
    sum(rate(workload_googleapis_com:gen_ai_invoke_agent_duration_count{monitored_resource="generic_node", gen_ai_agent_name="support-bot"}[5m]))
    ```

    *   **对于使用 PromQL 的可靠性指标**：始终使用分组聚合。按 `gen_ai_agent_name` 分组（例如，`by
        (gen_ai_agent_name)`）。避免过滤到单个 ID/名称，除非被要求。
    *   **对于使用标准阈值过滤器的质量指标**：完全省略 `agent_resource_name` 过滤器。将条件过滤器配置为仅针对全局项目中的监控资源类型
        (`aiplatform.googleapis.com/OnlineEvaluator`) 和指标类型
        (`aiplatform.googleapis.com/online_evaluator/scores`) 进行目标。

    *良好示例（SQL 分组）*：

    ```sql
    SELECT
      JSON_VALUE(resource.attributes, '$."cloud.resource_id"') as agent_id,
      ...
    FROM ...
    GROUP BY agent_id
    ```

    *不良示例（SQL 硬编码过滤器）*：

    ```sql
    SELECT ...
    FROM ...
    WHERE JSON_VALUE(resource.attributes, '$."cloud.resource_id"') = 'support-bot'
    ```

    *   **对于使用 SQL 的下游调用**：省略针对特定代理名称的 `ENDS_WITH` 过滤器。相反，提取代理标识符（例如，`JSON_VALUE(resource.attributes, '$."cloud.resource_id"')`）并将其添加到 `GROUP BY` 子句中，与模型或工具名称一起使用。
*   **目录推断**：优先使用用户明确提供的路径（如果有）。否则，将配置文件部署到目标 Terraform 或 SRE 文件夹（例如 `monitoring/`、`ops/`、`sre/`）。使用工具定位项目中警报策略或状态指针的位置，而不是盲目写入根目录。
*   **通知通道**：默认情况下，未经用户输入，不要配置任何通知通道。如果用户在提示中明确提供了一个通知通道，请配置警报使用它。如果没有提供通知通道，你必须在你最后的响应中明确询问用户是否希望配置通知通道。**这是一个强制性问题，你必须不能从你的响应中省略它。** **重要**不要对通知通道做出假设。如果你在代码库中搜索通知通道，你必须始终在使用它之前与用户确认。
*   **纯英文响应**：你必须包括对警报作用的纯英文解释。这必须用纯英文解释警报测量什么、算法如何工作以及触发表示什么。

### 6. 输出验证

*   **后台任务清理**：你必须验证你启动的所有后台任务的状态。在完成执行并返回最终响应之前，你必须终止或杀死所有活动或挂起的后台任务（使用 `manage_task` 工具并使用操作 `kill`）。
*   **验证配置**：运行 **配置校验** 工具，以确保所有输出文件都使用正确的语法和结构。有关该工具的详细信息，请参阅下文“工具脚本”部分。

## 工具脚本

使用以下脚本发现代理、收集配置详情、解决重复项并验证配置：

1.  **代理信息收集**：简化发现、环境审计（指标范围、BQ 数据集、通知通道）、表派生（日志和跟踪）以及在线评估器验证。
    *   命令：`python3 scripts/gather_agent_info.py --project-id {project_id}
        --agent-name {agent_name}`
2.  **重复项验证与合并**：验证目标文件夹中的现有警报，以确保更改原地合并而不是追加：
    *   命令：`python3 scripts/scan_duplicates.py {target_tf_dir}
        --engine-var '${var.gen_ai_agent_name}'`
3.  **配置校验**：验证 PromQL 语法、匹配引擎标签和 HCL 结构：
    *   命令：`python3 scripts/lint_syntax.py {path_to_tf_file}`
    *   **自我纠正循环**：如果验证失败（退出非零或输出错误），你必须阅读命令输出，定位包含校验错误的行/文件，分析 PromQL 语法或 Terraform HCL 问题，原地应用调整，并重新运行 `lint_syntax.py` 验证。重复此循环，直到验证脚本成功通过。

## 注意事项与行为纠正

*   **原始错误边界**：解释原始错误计数或绝对失败请求计数边界在流量吞吐量变化时无法扩展。建议使用基于比例的错误率警报。
*   **安全阈值调制端到端验证**：在端到端验证动态指标阈值策略时，不要尝试强制平台错误。相反，使用标准安全边界（Z 分数乘数 > 15）部署警报策略，然后临时将标准偏差 Z 分数限制更改为负值（例如，> -3）以触发/验证“触发”状态，然后再还原。在采取此操作前必须获得确认。
*   **预期脚本失败**：
    *   `scan_duplicates.py` 以代码 1 退出：解析 JSON 输出以查找重复的资源目标。执行原地升级编辑，然后重新检查，直到以 0 通过。
    *   **避免重复发现调用**：如果 `gather_agent_info.py`
        成功返回跟踪或日志表名（或写入变量文件），不要重复调用
        `list_trace_scope_table_names.py` 或 `list_log_scope_table_names.py`。
        这些脚本由 `gather_agent_info.py` 内部运行，仅作为外部回退提供。
    *   **脚本执行失败与自我纠正**：如果实用脚本（如 `gather_agent_info.py`、`check_telemetry.py`、
        `create_online_monitor.py`、`analyze_traffic.py`、
        `list_log_scope_table_names.py` 或 `list_trace_scope_table_names.py`)
        意外失败，你必须阅读并检查 stdout/stderr 日志或错误输出。分析错误消息并尝试动态纠正参数并重试执行，然后再升级或回退到手动计划。参考相关的特定领域参考文件以获取有关特定脚本的详细故障排除步骤。
*   **分布指标对齐约束**：标准 `ALIGN_MEAN` 不能应用于 `DELTA` 分布指标（如 `online_evaluator/scores`）。你必须使用百分位数对齐器（如 `ALIGN_PERCENTILE_50`）将分数分布减少为可比较的数字流。
*   **HCL Heredoc 插值**：在 PromQL 或 SQL 查询中引用 Terraform 变量（定义为字符串）时，你必须使用 ${var.variable_name} 语法。裸引用（如 var.variable_name）将在部署时失败。
*   **避免递归目录操作**：如果你从包含大量文件的存储库根目录运行递归列出或搜索命令（例如 `ls -R`、`find .` 或原始递归 `grep`），这将冻结你的会话。始终针对特定子目录。

## 支持链接

*   [使用在线监控器进行持续评估](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-online)
*   [代理平台质量指标](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/rubric-metric-details)
*   [Google Cloud 警报策略指南](https://docs.cloud.google.com/monitoring/alerts)
*   [Google Cloud Monitoring PromQL 文档](https://docs.cloud.google.com/monitoring/promql)
