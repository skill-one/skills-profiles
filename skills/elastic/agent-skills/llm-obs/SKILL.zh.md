---
name: observability-llm-obs
description: 从已导入Elastic的数据中回答关于LLM和代理应用行为的问题：延迟和错误率、令牌和成本利用率、响应质量和安全护栏事件，以及代理调用链的编排。当用户询问关于LLM监控、生成式AI可观察性、令牌消耗或AI成本、模型延迟、提示或安全护栏失败，或代理工具调用链如何执行时使用。
---

# 大语言模型和代理可观察性

使用**实际被导入Elastic的数据**回答关于监控大语言模型（LLM）和代理组件的问题——仅此而已。这项技能回答的四个问题是：LLM性能、成本和令牌利用率、响应质量以及调用链或代理工作流编排。

一个给定的部署通常使用**一个或多个**导入路径：APM/OTLP跟踪，以及/或集成指标和日志。存在哪种路径是一个发现结果，而不是一个假设——永远不要假设两者都存在。对于ES|QL语法、命令和查询模式，使用**elasticsearch-esql**技能。对于不是LLM特定的服务级延迟和错误分派，使用**observability-sre-triage**技能。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过`elastic` CLI执行Elasticsearch操作。如果未安装`[elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户它需要什么。不要猜测凭证，直接调用HTTP API，或尝试其他变通方法。

此技能以HTTP简写形式引用操作（例如，`GET /`，`GET /_cat/indices`，`GET /{index}/_mapping`，`GET /{index}/_settings/index.mode`，`POST /_query`）。本文件末尾的[操作](#operations)表将每个简写映射到等效的`elastic` CLI命令——始终使用CLI而不是直接调用HTTP API。

<!-- end-partial: preamble -->

### 无集群访问的分析

上述CLI检查会阻止**查询集群**——但它不会阻止分析。当用户已经在他们的问题中提供了证据（指标值、计数、状态原因、日志行、警报有效载荷、配置）时，从该证据中推理并给出结论。

当您确实需要用户未提供的数据时，仍然说明您会检查什么以及如何——指定将解决该问题的特定查询、索引和字段——然后请求CLI设置。没有集群的答案会命名检查是有用的；仅要求设置的答案则没有用。

## 要完成的任务

- 在查询任何内容之前，发现部署实际使用的LLM导入路径
- 发现此部署中的真实LLM字段名，因为生成式人工智能（GenAI）属性命名不一致
- 按模型、服务或时间报告LLM延迟、吞吐量和错误率
- 报告令牌利用率，并且只有在真实存在成本字段时才报告成本
- 调查响应质量：失败、超时、完成原因、内容过滤器以及守门人事件
- 重建代理调用链，并在多步骤工作流中找到瓶颈跨度
- 将发现与定义在LLM相关数据上的SLO（服务水平目标）和警报规则相关联

## 输出规范

适用于此技能生成的每个响应。

- **致力于最支持的结论。** 当证据指向一个方向时，请这样说。不要因为显得谨慎而降低信心——对明确证据的保留是一种缺陷，而不是谦逊。
- **在结论中只陈述一次信心。** 不要逐条陈述。
- **不要超出证据进行推测。** 如果没有观察到原因，它不会出现在答案中。说出未知的内容并停止。
- **报告缺失即缺失。** 零行数意味着数据缺失或未收集；它永远不会意味着底层条件是健康的。特别是，**如果不存在成本字段，请说明成本未进行指标化**——不要将令牌计数乘以猜测的每个令牌价格，并将乘积作为成本数字报告。
- **报告实际找到的数字。** 引用查询返回的令牌计数、延迟和错误率。不要将它们四舍五入成模糊的描述，也不要从本技能中的示例中传递一个数字。
- **不要填充。** 不要重述问题，不要叙述运行了哪些查询（除非结果很重要），不要总结总结。
- **以发现结束。** 不要有诸如“要我深入挖掘吗？”之类的结尾提议。可操作的后续行动应属于建议列表，以建议的形式提出，而不是以问题的形式提出。

## 数据存储位置

| 导入路径                  | 索引模式                                                            | 它能回答什么                                                       |
| ------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| OTel / EDOT跟踪通过OTLP     | `traces-*.otel-*`，或通用的 `traces-*`                              | 每个请求的延迟、令牌、模型、完成原因、**以及调用链** |
| Elastic APM代理跟踪        | `traces-apm*`，或通用的 `traces-*`                                  | 每个请求的延迟和结果；如果SDK添加了它们，则包含GenAI属性   |
| APM/OTel指标                | `metrics-apm*`，`metrics-*.otel-*`                                        | 服务级速率和延迟的聚合                                     |
| Elastic LLM集成指标        | `metrics-<integration>.*`（例如 `metrics-aws_bedrock_agentcore.*`) | 聚合令牌计数、调用次数、延迟，有时是成本             |
| Elastic LLM集成日志    | `logs-<integration>.*`                                                    | 提示/响应记录、守门人和内容过滤器事件             |

使用通用的`traces-*`模式来查找跟踪数据，无论是由Elastic APM代理还是OpenTelemetry收集的。仪器化可以来自EDOT、OpenLLMetry、OpenLIT或Langtrace导出到OTLP——所有这些都将LLM和代理跨度放入跟踪数据流中。

**只有跟踪才能重建调用链。** `trace.id`，`span.id`，和`parent.id`是重建代理调用链的唯一方法。集成指标是预先聚合的，无法做到这一点——如果问题是关于编排并且仅存在集成指标，请说明链无法从可用数据中重建。

背景阅读：
[LLM和代理式人工智能可观察性](https://www.elastic.co/docs/solutions/observability/applications/llm-observability)，
[EDOT LLM用例](https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/use-cases/llms)，
[可观察性实验室—LLM可观察性](https://www.elastic.co/observability-labs/blog/tag/llmobs)。

## 流程：确定哪些数据可用

按顺序运行。不要跳到第5步。

1. **验证连接并检测版本。** 调用`GET /`。此决策驱动的是可用的查询语言表面：`build_flavor: "serverless"`意味着所有ES|QL功能（包括`TS`，`TRANGE`和`TBUCKET`）都可用。否则使用`version.number`：在Stack上，`TS`在9.2中是预览版，在9.4中是GA版，而`TRANGE`在9.3.0中是GA版。因此将**Stack 9.4**视为整个时间序列路径的底线，并回退到下面使用`BUCKET(@timestamp, ...)`。做错会导致查询无法解析。

2. **确定哪些导入路径存在。** 此决策是此部署是否有跟踪、集成数据或两者——它决定了哪些问题根本无法回答。使用`GET /_data_stream/<name>`（传递`traces-*`，`metrics-*`，`logs-*`）或使用`GET /_resolve/index/<pattern>`解析模式。查找跟踪数据流、`metrics-apm*`以及任何匹配已知LLM集成数据集的`metrics-*`或`logs-*`。如果两者都没有LLM数据，请说明并停止——不要根据对模型提供者的通用知识回答。

3. **发现真实的LLM字段名。** 此决策是写入ES|QL的确切字段路径，不能猜测。命名在不同的仪器化之间有所不同：`gen_ai.*`与`llm.*`与集成特定名称，并且语义约定本身也已发生变化（较旧的仪器化发出`gen_ai.system`，较新的发出`gen_ai.provider.name`）。使用`GET /_field_caps`并带有字段模式（例如`*gen_ai*`，`*llm*`，`*token*`，`*cost*`），或读取`GET /<index>/_mapping`，然后采样文档以确认值已填充。**属性嵌套因导入路径而异**——OTel原生跟踪数据流将跨度属性暴露为`attributes.<name>`（并且通常作为裸通过`<name>`），而不是`span.attributes.<name>`。在写入查询之前确认哪种形式可以解析。参见[references/genai-fields.md](references/genai-fields.md)以获取属性目录和解析规则。

4. **决定是否存在成本字段。** 成本是**不**OpenTelemetry GenAI规范的一部分。一些仪器化添加了自定义属性，例如`llm.response.cost.usd_estimate`，而一些集成暴露了成本指标，但许多部署都没有。在步骤3中明确查找它。如果不存在，成本问题的答案将是成本未进行指标化——报告令牌计数并命名差距。

5. **为每个问题选择一个一致的数据源。** 当APM跟踪和集成指标都存在时，选择一个并用于整个答案。混合它们会导致重复计算，并为同一数量产生两个不同的数字，因为集成轮询提供者自己的账目，而跟踪记录客户端观察到的内容。按问题类型路由：**跟踪**用于每个请求的分析、调用链以及任何需要跟踪层次结构的内容；**集成指标**用于长时间窗口内聚合的令牌和成本总计。说明答案来自哪个来源。

6. **在相关性合理时检查警报和SLO。** 此决策是降级是否已被知晓并跟踪。使用`GET kbn:/api/alerting/rules/_find`查找规则，使用`GET kbn:/api/observability/slos`查找SLO，然后过滤到针对LLM相关服务或集成指标的那些——步骤3中的字段名告诉您哪些规则是相关的。触发的警报或处于违规或降级状态的SLO是性能降级的证据。请注意，SLO API的`sli.kql.custom`指示器使用KQL而不是ES|QL；这是一个API合同，而不是在其他地方使用KQL的建议。

## 用例和查询模式

使用`POST /_query`编写查询。始终绑定时间范围，当存在时添加`service.name`，并`LIMIT`结果。当只需要趋势而不是在细粒度下扫描宽窗口时，使用粗粒度桶。

| 问题                        | 跟踪路径                                                                                                                                     | 集成路径                                               |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 延迟、吞吐量、错误率 | 根据GenAI操作或模型属性进行过滤；每个桶的`COUNT(*)`，`AVG(span.duration.us)`，以及通过`event.outcome == "failure"`的失败 | 按模型维度请求速率、延迟和错误指标    |
| 令牌和成本                 | 按时间、模型或服务对输入和输出令牌属性求和；如果存在，则添加成本属性                                 | 按时间和模型聚合的令牌和成本指标            |
| 响应质量和安全性     | `event.outcome`，`error.type`，以及完成原因属性；如果捕获且未编辑，则仅捕获提示和响应                 | 守门人块、内容过滤器事件和政策违规 |
| 调用链和编排             | **仅跟踪**——按`trace.id`分组，通过`parent.id`到`span.id`行走，按跨度名称或GenAI操作聚合 | 无法回答——指标是预先聚合的                    |

在跟踪路径上，每个跨度的延迟来自`duration`（纳秒，每个OTel原生跨度填充）或`span.duration.us`（微秒，APM兼容字段，在许多跨度上是`null`——按它排序可能会无声地丢弃最慢的步骤）。在使用它之前确认哪个已填充。最慢的子跨度是瓶颈。按跨度名称或GenAI操作属性聚合显示了工作流中步骤类型的分布——检索、LLM调用、工具使用。

对于集成特定数据流和字段名——OpenAI、Azure OpenAI、Azure AI Foundry、Amazon Bedrock、Bedrock AgentCore、GCP Vertex AI——参见[references/integrations.md](references/integrations.md)。对于包括跟踪层次结构行走和时间序列集成模式的更长的查询，参见[references/esql-recipes.md](references/esql-recipes.md)。

## 示例

下面的字段路径是**说明性的**。在运行任何内容之前，先从步骤3中确认真实路径——此技能自己的方法是先发现字段名，正确的嵌套取决于导入路径。

**“每个模型我们消耗了多少令牌？”**——确认令牌属性存在并解析，然后按模型和时间桶求和。报告返回的总额：

```esql
FROM traces-*
| WHERE @timestamp > NOW() - 24 hours AND attributes.gen_ai.request.model IS NOT NULL
| EVAL in_tok = TO_LONG(attributes.gen_ai.usage.input_tokens),
       out_tok = TO_LONG(attributes.gen_ai.usage.output_tokens)
| STATS input_tokens = SUM(in_tok), output_tokens = SUM(out_tok)
    BY hour = BUCKET(@timestamp, 1 hour), attributes.gen_ai.request.model
| SORT hour
| LIMIT 500
```

**“我们的LLM支出是多少？”**——在查询之前使用`GET /_field_caps`在`*cost*`上查找成本字段。如果不存在，报告令牌利用率并明确说明在此部署中成本未进行指标化；在仪器化层添加成本属性，或启用报告成本的集成是解决方案。不要将令牌乘以一个你假设的价格。

**“哪个模型最慢，它是否失败？”**——一次进行延迟和错误率，按模型分组：

```esql
FROM traces-*
| WHERE @timestamp > NOW() - 24 hours AND attributes.gen_ai.request.model IS NOT NULL
| STATS request_count = COUNT(*),
        failures = COUNT(*) WHERE event.outcome == "failure",
        avg_duration_us = AVG(span.duration.us)
    BY attributes.gen_ai.request.model
| EVAL error_rate = failures::double / request_count
| SORT avg_duration_us DESC
| LIMIT 100
```

**“我们的代理为什么慢？”**——这需要跟踪层次结构，因此它需要跟踪数据。找到包含超过一个LLM或工具跨度的跟踪，按这些跨度中花费的时间排序，然后通过`trace.id`进入最差的跟踪以找到瓶颈跨度。由于`WHERE`限制为LLM跨度，下面的总和是LLM时间，而不是端到端跟踪持续时间——命名列以防止将其误读为墙钟延迟：

```esql
FROM traces-*
| WHERE @timestamp > NOW() - 3 hours AND attributes.gen_ai.operation.name IS NOT NULL
| STATS llm_span_count = COUNT(*), llm_duration_us = SUM(span.duration.us) BY trace.id
| WHERE llm_span_count > 1
| SORT llm_duration_us DESC
| LIMIT 50
```

**“提示是否被阻塞？”**——在跟踪路径上检查完成原因属性和`error.type`，或集成的守门人日志事件。例如，内容过滤器是一种质量信号，而不是传输错误。

**“是否已经对此发出警报？”**——`GET kbn:/api/alerting/rules/_find`和`GET kbn:/api/observability/slos`，过滤到步骤2中确定的LLM相关服务或集成指标。

## 指南

- **仅从导入到 Elastic 的数据中作答。** 不要描述或依赖其他供应商的 UI、控制台或产品。
  如果数据不在 Elastic 中，答案就是不在 Elastic 中。
- **查询前先发现。** 从 `GET /_field_caps`、`GET /<index>/_mapping` 或样本文档中确认数据导入路径（步骤 2）和字段名称（步骤 3）。不要猜测属性路径。
- **每个问题仅使用一个一致的数据源。** 不要在一个答案中混合 APM 追踪和集成指标。
- **成本不在 GenAI 规范中。** 只有当数据中存在成本字段时，成本数值才被视为可用。
- **只有追踪可以重建链路。** 如果问题是关于智能代理编排且仅存在集成指标，应说明链路无法重建，而不是从聚合数据中近似估算。
- **根据版本控制时间序列语法。** 在 Serverless 或 Stack 9.4+ 上使用 `TS` 配合 `TRANGE` 和 `TBUCKET`；低于此版本则回退到使用 `FROM` 配合 `BUCKET(@timestamp, ...)`。别名桶（`BY bucket = TBUCKET(1小时)`）并按别名排序。
- **动态映射的属性可能存在类型冲突。** 在滚动后，标记属性在一个后备索引中可能被映射为 `integer`，在另一个中映射为 `long`，这会导致 ES|QL 拒绝该字段。在聚合前使用 `EVAL` 中的 `TO_LONG(...)` 进行类型转换。
- **不依赖 Kibana UI。** 优先使用 ES|QL 和 Elasticsearch API；仅在 SLO 和告警中使用 Kibana API。不要指示用户打开 Kibana UI。
- 对于 ES|QL 语法和查询模式使用 **elasticsearch-esql** 技能；`[TS 命令参考](https://www.elastic.co/docs/reference/query-languages/esql/commands/ts)` 在 Stack 9.4+ 和 Serverless 上适用，`[FROM 命令参考](https://www.elastic.co/docs/reference/query-languages/esql/commands/from)` 在其他地方适用。

## 操作

| HTTP API (简称)                | `elastic` CLI 命令                                                  |
| ------------------------------- | -------------------------------------------------------------------- |
| `GET /`                        | `elastic es info`                                                    |
| `GET /_data_stream/<name>`      | `elastic es indices get-data-stream --name '<name>'`                 |
| `GET /_resolve/index/<pattern>` | `elastic es indices resolve-index --name '<pattern>'`                |
| `GET /<index>/_mapping`         | `elastic es indices get-mapping --index '<index>'`                   |
| `GET /_field_caps`             | `elastic es field-caps --index '<index>' --fields '<fields>'`        |
| `POST /_query`                 | `elastic es esql query --format tsv --query '<esql>'`                |
| `GET kbn:/api/alerting/rules/_find` | `elastic kb alerting get-alerting-rules-find --filter '<filter>'`    |
| `GET kbn:/api/observability/slos` | `elastic kb slo find-slos-op --space-id '<space>' --kql-query '<kql>'` |
