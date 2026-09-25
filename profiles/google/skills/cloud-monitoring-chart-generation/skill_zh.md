# 云监控图表生成技能 (`cloud-monitoring-chart-generation`)

将 PromQL 或 ListTimeSeries JSON 请求有效载荷和指标元数据转换为有效的服务器驱动 UI (SDUI) `google.monitoring.dashboard.v1.Widget` Protocol Buffer 文本protos。这些生成的文本protos 设计用于被云监控仪表板 API、gcloud CLI 或声明式仪表板配置管道摄取。

> [!IMPORTANT] **首选 API 与互斥查询**：
> - **API 首选**：始终优先为小部件生成 `ListTimeSeries` (`time_series_filter`) 配置，而不是 PromQL，除非用户明确请求 PromQL 或指标数学严格需要它。
> - **互斥**：小部件数据集 `time_series_query` 必须包含 **要么** `time_series_filter` **要么** `prometheus_query`。你绝不能同时填充同一数据集中的这两个字段。
> - **严格传递**：你必须逐字符精确复制提供的 PromQL 查询或 ListTimeSeries JSON 过滤字符串。在任何情况下都不要凭空捏造、重写或修改查询。

> [!CAUTION] **关键执行与工作目录规则**：
>
> -   **不要更改工作目录**：将你的工作目录保持在你的工作区根目录。不要 `cd` 到技能子目录中。
> -   **无发现或搜索规则**：指标描述符、PromQL 查询、ListTimeSeries JSON 有效载荷、单位和资源类型始终存在于对话上下文中。**永远**不要运行文件或代码库搜索工具，如 grep、find、目录列表或代码库查询，以发现指标元数据或检查仓库结构。
> -   **脚本执行**：直接使用 python3 执行捆绑的 Python 脚本。
> -   **输出生成**：`assemble_widget_proto` 脚本自动生成一个基于 UUID 的唯一文件名，以防止并行执行冲突。它将生成的文件名打印到标准错误中，并强烈前缀为 "Wrote widget textproto to:"。你必须从日志中解析这个确切的前缀，以提取生成的路径并在第 4 步中用于验证。

## 前置条件：环境设置

在你的环境或沙盒中安装所需的依赖项：

```bash
pip install -r scripts/requirements.txt
```

## 遵循工作流管道

```
[ 第 1 步：compute_labels ]  --->  [ 第 2 步：LLM 合成 ]  --->  [ 第 3 步：assemble_widget_proto ]
  生成候选标签         构思语义 PlotSpec       发出经过验证的小部件文本proto
```

### 第 1 步：基线候选合成

使用 python3 运行第 1 步：

```bash
# 对于 PromQL：
python3 scripts/compute_labels.py \
  --metric_display_name "METRIC_DISPLAY_NAME" \
  --resource_type "RESOURCE_TYPE" \
  --metric_unit "UNIT" \
  --promql_query 'PROMQL_QUERY'

# 对于 ListTimeSeries：
python3 scripts/compute_labels.py \
  --metric_display_name "METRIC_DISPLAY_NAME" \
  --resource_type "RESOURCE_TYPE" \
  --metric_unit "UNIT" \
  --filter_string 'metric.type="m"...' \
  --per_series_aligner "ALIGN_RATE" \
  --cross_series_reducer "REDUCE_SUM"
```

### 第 2 步：语义 PlotSpec 预测 (LLM)

审查用户提示、PromQL 或 LTS 查询结构以及第 1 步的基线候选，以构思一个 4 键的 `SemanticPlotSpec` JSON 对象：

1.  **`title`**：将 `titleCandidate` 精炼，确保它简洁、人类可读，并且少于 80 个字符。
2.  **`yAxisLabel`**：将其设置为简洁、人类可读的定量描述符或指标概念，例如 `"利用率"`、`"字节"` 或 `"字节速率"`。不要将单位符号或后缀（如 `"(%)"`、`"(/s)"` 或 `"(By)"`）附加到标签上，因为单位会自动通过 `unitOverride` 渲染。
3.  **`plotType`**：默认为 `LINE`。如果用户请求或用于分布查询，则使用 `STACKED_AREA`。
4.  **`unitOverride`**：将其设置为度量单位统一代码 (UCUM) 单位字符串，通过应用以下相应规则导出：

#### List Time Series (LTS) 单位策略：

-   **信任候选**：对于 List Time Series 流，直接将其设置为第 1 步生成的 `unitOverrideCandidate`。第 1 步数学处理 `ALIGN_RATE`，例如生成 `By/s`，强制 `ALIGN_PERCENT_CHANGE` 为 `%`，并且无条件正确输出原生规范化。

#### PromQL 单位策略 (LLM 手动覆盖)：

因为 PromQL 表达式可以几何组合，例如 `histogram_quantile(..., rate(...))`，依靠你自己的语义推理来控制最终单位：

-   **速率函数 (`rate(...)`, `irate(...)`)**：将累积计数转换为每秒速率。将 `/s` 附加到原始指标单位。例如，原始指标单位为 `By`，使用 `rate(...)` 结果为 `unitOverride: "By/s"`。 -   **例外**：如果 `rate()` 在 `histogram_quantile()` 内部评估，输出是原始桶单位，如 `"s"`，而不是速率。
-   **比率与百分比 (`100 * (A / B)`)**：相同指标单位的比率通常表示百分比，结果为 `unitOverride: "%"`。
-   **规范化**：将 `10^2.%` 规范化为 `"%"`。
-   **保留单位**：对于简单的聚合函数，如 `avg_over_time(...)` 或 `sum by (...)`，保留并输出底层指标单位，不进行修改。

-   **图例模板**：不要配置 `legend_template` 字段。它有意省略，以便云监控前端在运行时动态渲染其多列表图例。

示例 `SemanticPlotSpec`：

```json
{
  "title": "VM CPU 利用率 us-central1-a",
  "yAxisLabel": "利用率",
  "plotType": "LINE",
  "unitOverride": "%"
}
```

### 第 3 步：Protobuf 组装与输出

使用 python3 运行第 3 步以生成并保存小部件文本proto。使用 `--promql_query` 用于 PromQL，或 `--lts_request_json` 用于 ListTimeSeries：

```bash
# 对于 PromQL：
python3 scripts/assemble_widget_proto.py \
  --promql_query 'PROMQL_QUERY' \
  --spec_json 'SEMANTIC_PLOT_SPEC_JSON'

# 对于 ListTimeSeries：
python3 scripts/assemble_widget_proto.py \
  --lts_request_json '{"filter": "...", "aggregation": {...}}' \
  --spec_json 'SEMANTIC_PLOT_SPEC_JSON'
```

> [!IMPORTANT] **强制性文件输出契约**：不要试图猜测或强制输出文件名。脚本将自动生成一个保证唯一的文件名，并将其打印到标准错误中。在标准错误中搜索显式前缀 "Wrote widget textproto to:" 以确定性捕获此文件名，然后将其作为第 4 步验证的目标。

-   **分配文件名反馈**：每当保存输出文件时，脚本会将文件路径记录到标准错误中。阅读你的命令执行日志以获取创建的确切文件名，以便你在第 4 步中验证它。
-   **文本聊天输出**：在响应中用 ```` ```textproto```` 代码块包围生成的 SDUI 小部件文本proto：

```textproto
title: "..."
xy_chart {
  ...
}
```

### 验证并自动重试

> [!CAUTION] **文件验证通过之前不要结束你的回合**：1. **验证工件**：执行第 3 步生成的文件输出验证器脚本：

```bash
    # 对于 PromQL 图表：
    python3 scripts/validate_chart.py --input_file "GENERATED_FILE.textproto" \
       --expected_promql_substring "SOME_IDENTIFYING_SUBSTRING_FROM_QUERY" \
       --expected_unit_override "UNIT_OVERRIDE_CANDIDATE"
    
    # 对于 ListTimeSeries (LTS) 图表：
    python3 scripts/validate_chart.py --input_file "GENERATED_FILE.textproto" \
       --expected_lts_filter_substring "SOME_IDENTIFYING_SUBSTRING_FROM_FILTER" \
       --expected_unit_override "UNIT_OVERRIDE_CANDIDATE"
    
    # ALWAYS provide an identifying substring and the Stage 1 unit override candidate to verify you didn't mutate the data.
    
    # CRITICAL: If you generated multiple charts for multiple metrics, you MUST run this validation script independently for EACH file generated to ensure every chart is correct!
```

2.  **如果缺失或失败则自动重试**：如果 `validate_chart` 报告文件缺失或无效，验证你的脚本参数并立即重新运行第 3 步：

     ```bash
     python3 scripts/assemble_widget_proto.py \
       --promql_query 'PROMQL_QUERY' \
       --spec_json 'SEMANTIC_PLOT_SPEC_JSON'
     # 或使用 --lts_request_json 如果适用
     ```
3.  **验证与重试**：运行 `validate_chart` 以验证生成的 textproto。如果由于模式或语法错误导致验证失败，请更正参数并重试最多 2 次。如果 2 次重试后验证仍然失败，请停止重试，通知用户验证错误，并呈现最佳努力文本proto。
4.  **执行与验证错误**：请注意，`validate_chart.py` 的模式/语法验证错误与 OS 或环境执行限制不同，这些限制在下面的 **优雅沙盒回退** 中处理。

#### 执行优雅沙盒回退

如果由于环境或沙盒限制无法执行 `compute_labels.py`、`assemble_widget_proto.py` 或 `validate_chart.py`，请执行以下操作：

1. 通知用户哪个脚本无法执行以及原因。
2. **直接在你的响应中合成并输出完整的小部件文本proto**，遵循所有格式和单位规则。
3. 提供一个 **"本地验证"** 部分包含独立的 python3 命令，以便用户可以本地运行和验证模式（如果需要）。

## 支持链接

- [仪表板 API](https://docs.cloud.google.com/monitoring/dashboards/api-dashboard)
- [Prometheus 文档](https://prometheus.io/docs/prometheus/latest/querying/)
