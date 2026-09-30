---
name: kibana-anomaly-detection
description: Elastic ML异常检测——调查/RCA、分数解释、作业生命周期故障排除和作业操作。在回答“什么出错了？”、“哪个实体？”/RCA、“分数为什么高/低？”/重新归一化、“数据源停止”/“内存限制”/硬限制，或配置ML异常检测作业时使用。从`.ml-anomalies-*`读取结果，从ML REST API读取作业状态。
---

# Elastic ML 异常检测

专家级 ML 异常检测流程：将属性事件归因于实体，解释分数和模型行为，诊断作业生命周期故障，并管理作业。从 `POST /.ml-anomalies-*/_search`（服务器端安全）读取异常**结果**，从 ML REST API 读取**作业/数据源状态**。当用户在提示中嵌入固定证据（影响者行、作业统计信息）时，直接应用以下判断——不要重新获取已提供的字段。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他解决方案。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。本文件末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

## 模式选择器

| 用户意图                                                                   | 模式                                                                                                   |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| "什么出错了？" / RCA / 跨作业 / 爆炸半径 / 影响者 / 日志类别                 | **调查**                                                                                        |
| "为什么分数高/低？" / 重新归一化 / 模型边界 / 预测                          | **解释**                                                                                            |
| 缺失文档 / 内存限制 / 数据源停止 / 生命周期 / 日历                          | **排错**                                                                                           |
| 创建作业 / 配置数据源 / 开始分析 / 检索结果                               | **管理**                                                                                             |
| 安全框架（攻击链、MITRE、外泄）                                | 调查 + [参考资料/security-anomaly-expert.md](references/security-anomaly-expert.md)           |
| 可观察性/SRE 框架（退化、容量、部署回归）      | 调查 + [参考资料/observability-anomaly-expert.md](references/observability-anomaly-expert.md) |

当问题跨越多个模式时：**调查 → 解释 → 排错**。完成一个模式后再混合逻辑。

> **服务器端注意：** 遗留的 `/_ml/anomaly_detectors/{job_id}/results/*` 端点在服务器端返回 HTTP 410。始终通过 `POST /.ml-anomalies-*/_search` 并使用 `result_type` 过滤器查询 `.ml-anomalies-*`。

## 分数快速参考

- `record_score` 分段：**>75** 严重 · **50–75** 警告 · **25–50** 轻微 · **<25** 信息性
- `multi_bucket_impact ≥ 3` → 持续变化（不是瞬态峰值）
- `initial_record_score >> record_score` → 重新归一化（模型后来看到了更严重的异常）
- `actual << typical` 与 `count`/`low_count`/`low_mean` → 缺失/停机，而不仅仅是低值
- 多个作业的低分数 > 一个高分数 — 综合跨作业信号通常比单个检测器严重性更准确

> 完整分数定义、重新归一化机制和 `anomaly_score_explanation` 组件：
> [参考资料/score-reference.md](references/score-reference.md)。

## 核心概念

通过搜索查询中的 `result_type` 将 `.ml-anomalies-*` 视为分层结果类型：

| `result_type`         | 范围           | 关键字段                                                                               |
| --------------------- | --------------- | ---------------------------------------------------------------------------------------- |
| `bucket`              | 时间窗口     | `anomaly_score`, `initial_anomaly_score`, `timestamp`                                    |
| `record`              | 检测器行    | `record_score`, `initial_record_score`, `actual`, `typical`, `anomaly_score_explanation` |
| `influencer`          | 实体 × 时间窗口 | `influencer_field_name`, `influencer_field_value`, **`influencer_score`**                |
| `model_plot`          | 边界          | `model_lower`, `model_upper`, `actual`                                                   |
| `category_definition` | 日志模式    | `category_id`, `terms`, `regex`, `examples`                                              |

这样读取分数：

- `anomaly_score` / `record_score` = **当前归一化** 值（随着模型看到新的极端值而变化）。
- `initial_anomaly_score` / `initial_record_score` = **不可变快照** 从检测时间。
- **`influencer_score` 在时间窗口内对实体责任进行排名** — 最高分是主要嫌疑人，而不是时间窗口级别的 `anomaly_score`。
- 通过 `partition_field_value` / `by_field_value` / `over_field_value` 映射实体。
- 读取 `multi_bucket_impact` (-5 到 +5) 以区分单时间窗口峰值和持续趋势。

---

## 模式：调查 — RCA

**当：** "什么出错了？"、"哪个实体导致了这个问题？"、跨作业关联、爆炸半径、攻击/级联链。

### 流程

1. **发现作业。** 当作业 ID 未知时，调用 `GET /_ml/anomaly_detectors`。调用 `GET /_ml/anomaly_detectors/{job_id}` 和 `GET /_ml/datafeeds/datafeed-{job_id}` 以了解源索引、实体字段 (`by_field_name`, `over_field_name`, `partition_field_name`) 和 `bucket_span`。决策：识别相关作业组——共享数据源索引或实体字段监控同一系统但角度不同的作业。

2. **确定事件窗口。** 调用 `POST /.ml-anomalies-*/_search` 并使用 `result_type: bucket`、时间范围和可选的最小 `anomaly_score`。决策：固定事件的开始/结束并计算在该窗口内同时触发多少个作业。多个作业同时的低分数通常指示系统级根本原因。

3. **归因于实体（对 RCA 至关重要）。** 对于异常时间戳，调用 `POST /.ml-anomalies-*/_search` 并使用 `result_type: influencer`、作业 ID 和时间窗口。按 **`influencer_score` 降序** 排序。决策：将具有 **最高 `influencer_score`** 的实体命名为可能原因——它按每个实体在该时间窗口中的异常程度进行排名。不要在没有归因责任的情况下仅重述桶 `anomaly_score`。建议下一步深入该实体的记录。

4. **跨作业确认。** 对相关作业 ID 的相同实体值和时间窗口重新查询影响者（或桶记录）。在 **2 个或更多作业** 中异常的实体是主要嫌疑人（资源故障或系统级故障）；单作业实体通常是下游受害者。参见
   [参考资料/协议/investigation.md](references/protocols/investigation.md)。

5. **深入记录。** 调用 `POST /.ml-anomalies-*/_search` 并使用 `result_type: record`、确切作业 ID、实体过滤器 (`partition_field_value`, `by_field_value`) 和低最小 `record_score`（25 或更低）。读取 `multi_bucket_impact ≥ 3` 作为持续行为变化。读取 `actual` 与 `typical` 以确定故障类型（峰值 vs 缺失/停机）。

6. **用源证据确认。** 对嫌疑人实体和时间窗口调用 `POST /{index}/_search` 在数据源索引上。原始源文档是真相——在没有它们的情况下不要关闭 RCA。

7. **综合。** 报告：**根本原因实体 · 受影响的作业 · 时间进展 · 故障类型 · 严重性 · 推荐操作**。工作示例：[参考资料/worked-example.md](references/worked-example.md)。查询模板：[参考资料/investigation-queries.md](references/investigation-queries.md)。

### 规则

1. **对于“哪个实体？”按 `influencer_score` 排序，而不是 `anomaly_score`** — 桶分数是汇总的；影响者分数归因于原因。
2. **多作业实体是主要嫌疑人；单作业实体通常是受害者。**
3. **最早异常时间戳获胜** — 通过跨作业记录时间戳重建时间线。
4. **`multi_bucket_impact ≥ 3` = 持续行为变化**，权重高于瞬态峰值。
5. **使用低分数阈值（25 或更低）进行影响者/记录查询** — 高阈值会遗漏相关实体。
6. **在没有数据源索引的源证据的情况下永远不要关闭 RCA**。

---

## 模式：解释 — 分数 / 模型行为

**当：** "为什么我的分数是 30/90？"、"分数在一夜之间下降"、"重新归一化是什么？"、"为什么没有被检测到？".

### 流程

1. **决定获取 vs 解释。** 如果用户提供了带有 `record_score`、`initial_record_score`、`actual` 和 `typical` 的记录，直接解释。否则加载配置使用 `GET /_ml/anomaly_detectors/{job_id}` 和记录使用 `POST /.ml-anomalies-*/_search` (`result_type: record`)。

2. **始终显示 `initial_record_score` 和 `record_score`。** 间隙是重新归一化的故事。大幅正漂移 (`initial_record_score >> record_score`) 意味着后来更严重的异常将此记录向下重新归一化——这是预期的健康行为，而不是模型损坏。

3. **在猜测之前对模式进行分类。**

   | 模式                                                      | 解释                                                    |
   | ------------------------------------------------------------ | ----------------------------------------------------------------- |
   | `initial_record_score >> record_score`                       | 重新归一化 — 在建议配置更改之前解释                      |
   | `actual << typical` with `low_count`/`count`/`low_mean`      | 缺失/停机异常 — 调查停机，而不是分数调整                |
   | `high_variance_penalty: true` in `anomaly_score_explanation` | 噪声指标 — 宽边界吸收了峰值                     |
   | `incomplete_bucket_penalty: true`                            | 摄取延迟或稀疏桶 — 分数合理降低                      |

   仅引用记录中**存在的** `anomaly_score_explanation` 因素。

4. **量化重新归一化（可选）。** 重新查询按 `timestamp` 排序的记录；计算 `score_drift = initial_record_score - record_score` 并标记大幅漂移。

5. **在需要时添加视觉上下文。** 如果 `model_plot_config.enabled`，查询 `result_type: model_plot` 并比较 `actual` 与 `model_lower`/`model_upper`。对于分类作业，查询 `result_type: category_definition`。

6. **当分数持续看起来错误时检查作业健康。** 调用 `GET /_ml/anomaly_detectors/{job_id}/_stats` — `model_size_stats.memory_status` 的 `hard_limit` 会损坏学习并使分数失效。升级到排错模式。

### `anomaly_score_explanation` 组件

| 组件                        | 影响  | 意思                                                |
| -------------------------------- | ------- | ------------------------------------------------------------ |
| `anomaly_length`                 | ↑ 分数 | 更多的连续异常桶                           |
| `single_bucket_impact`           | ↑ 分数 | 更低的可能性 → 更高影响                            |
| `multi_bucket_impact`            | ↑ 分数 | 持续模式贡献                               |
| `anomaly_characteristics_impact` | ↑ 分数 | 均值变化 vs 方差变化                               |
| `high_variance_penalty`          | ↓ 分数 | 噪声数据 → 宽边界 → 异常不那么令人惊讶           |
| `incomplete_bucket_penalty`      | ↓ 分数 | 桶中的数据比预期少（摄取延迟、稀疏数据） |

### 规则

1. **在诊断配置之前解释重新归一化** — 分数漂移是“分数下降”最常见的原因。
2. **`actual << typical` with count/low_count 是一个缺失异常** — 区分停机与值峰值。
3. **每周季节性需要 ≥3 周的训练数据** — 标记年轻作业作为原因。
4. **检测器函数方向很重要** — 参见
   [参考资料/anomaly-detection-functions.md](references/anomaly-detection-functions.md)。

---

## 模式：排错 — 作业生命周期

**当：** "缺失文档"、"数据源停止"、"**`hard_limit`**"、"结果看起来不对"、"生命周期变化".

### 流程

1. **加载作业和数据源状态。** 调用 `GET /_ml/anomaly_detectors/{job_id}/_stats` 和
   `GET /_ml/datafeeds/datafeed-{job_id}/_stats`。读取 `state`、`data_counts`、**`model_size_stats`** 和数据源 `state`。如果用户嵌入统计 JSON，直接从 `memory_status` 和数据源状态诊断。

2. **首先诊断内存状态（关键）。** 检查 `model_size_stats`:

   | 字段                      | 含义                                                     |
   | -------------------------- | ----------------------------------------------------------- |
   | `memory_status`            | `ok` / `soft_limit` (修剪) / **`hard_limit` (关键)** |
   | `model_bytes`              | 当前内存使用                                         |
   | `model_bytes_memory_limit` | 配置的 `model_memory_limit`                             |

   当 **`memory_status` 是 `hard_limit`** 且 `model_bytes` 等于 `model_bytes_memory_limit` 时，模型达到了内存上限——它停止学习新实体，结果变差或停止。停止的数据源通常是 **症状**，而不是根本原因。**不要仅建议重新启动数据源**——单独这样做并不能清除硬限制。

3. **修复 hard_limit。** 修复方法是**提高 `model_memory_limit`**（通过作业更新）**和/或减小模型大小**
   通过降低基数（更少的 partition/by/over 字段值，分成多个作业）。提高限制需要以下生命周期序列（停止数据源 → 关闭作业 → 更新 → 打开 → 启动）。可选地调用
   `POST /_ml/anomaly_detectors/_estimate_model_memory` 从源基数大小调整新限制。

4. **诊断缺失文档 / 查询时间。** 内存健康后，通过 `GET /_ml/datafeeds/datafeed-{job_id}` 检查数据源 `query_delay` 和
   `delayed_data_check_config`。在 `.ml-annotations-*` 中搜索延迟数据事件。将 `query_delay` 设置为 P95 摄取延迟 + 缓冲（默认 `60s`–`120s`）。

5. **读取作业消息。** 当错误不明确时，搜索 `.ml-notifications-*` 对于作业 ID。

6. **恢复损坏的模型状态。** 当模型在 hard_limit 期间损坏时，调用 `POST /_ml/anomaly_detectors/{job_id}/model_snapshots/{snapshot_id}/_revert`
   恢复到已知良好的快照。

### 配置更改的生命周期（内存限制、query_delay）

按顺序应用——跳过步骤会导致更新被拒绝：

1. `POST /_ml/datafeeds/datafeed-{job_id}/_stop`
2. `POST /_ml/anomaly_detectors/{job_id}/_close`
3. `POST /_ml/anomaly_detectors/{job_id}/_update` (内存限制) 和/或 `POST /_ml/datafeeds/datafeed-{job_id}/_update`
   (query_delay)
4. `POST /_ml/anomaly_detectors/{job_id}/_open`
5. `POST /_ml/datafeeds/datafeed-{job_id}/_start`

在重新启动之前使用 `POST /_ml/datafeeds/datafeed-{job_id}/_preview` 预览更改。

> **`hard_limit` 损坏模型状态** 并导致下游缺失文档假警报。**在修复 `query_delay` 之前修复内存**。完整排错细节：
> [参考资料/troubleshooting-reference.md](references/troubleshooting-reference.md)。

### 规则

1. **`memory_status`中的地面生命周期诊断** — 不要提供通用的“重启它”建议。
2. **在`query_delay`之前修复内存** — 硬限制会使下游诊断失效。
3. **停止数据源 → 关闭作业 → 更新 → 打开 → 启动**，以应对任何内存或数据源配置变更。
4. **不要将删除作业作为硬限制的第一项补救措施** — 提高限制和/或减少基数。

---

## 模式：管理 — 创建/配置作业

**何时使用：** “设置作业”、“创建机器学习检测器”、“监控X随时间变化”。

对于完整的创建/打开/启动生命周期，优先使用`elasticsearch-anomaly-detection`技能。此模式总结了操作顺序和检测器选择：

1. **验证目标索引。** 调用`GET /{index}/_mapping` — 确认存在时间字段和检测器字段。
2. **创建作业。** 调用`PUT /_ml/anomaly_detectors/{job_id}`，包含`analysis_config`（检测器、`bucket_span`、影响因素）和`data_description.time_field`。
3. **创建数据源。** 调用`PUT /_ml/datafeeds/datafeed-{job_id}`，包含`indices`、`query`和`query_delay`。
4. **打开和启动。** 调用`POST /_ml/anomaly_detectors/{job_id}/_open`，然后`POST /_ml/datafeeds/datafeed-{job_id}/_start`。
5. **确认。** 调用`GET /_ml/anomaly_detectors/{job_id}/_stats`和`GET /_ml/datafeeds/datafeed-{job_id}/_stats`。

根据用户意图选择检测器功能 — 参见
[references/anomaly-detection-functions.md](references/anomaly-detection-functions.md)。有效的JSON体：
[references/job-creation-recipes.md](references/job-creation-recipes.md)。

### 规则

1. **在创建数据源之前创建作业。** 在启动数据源之前打开作业。
2. **`query_delay` = P95摄取延迟 + 缓冲**（60秒–120秒为安全默认值）。
3. **`by_field_name` vs `over_field_name`：** `by`将实体与其自身历史比较；`over`将实体与同组比较。
4. **预测需要非人口统计作业** — 具有`over_field_name`的作业无法进行预测。

---

## 示例

**根本原因分析（RCA）：** “某事导致结账延迟激增 — 哪个实体？” → 查询影响因素的桶 → **web-07**具有最高的`influencer_score`（91.5）对比22.0和8.4 → 将web-07命名为可能原因 → 建议深入其记录 — 不要仅以桶`anomaly_score` 88作为答案。

**分数下降：** “分数从90降至55 — 模型是否更改？” → 比较`initial_record_score`与`record_score` → 如果漂移较大，解释重新归一化。

**内存限制：** “作业显示`hard_limit`且数据源停止。” → 诊断
`model_size_stats.memory_status = hard_limit` → 通过关闭/更新/打开生命周期提高`model_memory_limit`和/或减少基数 — **不是**“仅重启数据源”。

**新作业：** “检测每个主机的异常错误率。” → `high_count`与`by_field_name: host.keyword` → 创建/打开/启动序列。

---

## 指南

1. **首先选择模式。** 不要在一个回复中混合RCA逻辑和分数解释逻辑。
2. **对于“哪个实体？”按`influencer_score`排序**，而不是桶`anomaly_score`。
3. **对于生命周期失败先读取`memory_status`**，然后再建议重启数据源。
4. **在`record_score`旁边显示`initial_record_score`** — 差值说明了重新归一化的故事。
5. **在`query_delay`之前修复内存。** 硬限制会使下游诊断失效。
6. **用数据源索引的源证据确认RCA**。

## 操作

| HTTP API（简称）                                                                 | `elastic` CLI命令                                                                                       |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `GET /{index}/_mapping`                                                          | `elastic es indices get-mapping --index '<index>'`                                                  |
| `POST /{index}/_search`                                                          | `elastic es search --index '<index>' --input-file '<search-body.json>'`                             |
| `GET /_ml/anomaly_detectors`                                                     | `elastic es ml get-jobs`                                                                            |
| `GET /_ml/anomaly_detectors/{job_id}`                                            | `elastic es ml get-jobs --job-id '<job_id>'`                                                        |
| `GET /_ml/anomaly_detectors/{job_id}/_stats`                                     | `elastic es ml get-job-stats --job-id '<job_id>'`                                                   |
| `GET /_ml/datafeeds/datafeed-{job_id}`                                           | `elastic es ml get-datafeeds --datafeed-id 'datafeed-<job_id>'`                                     |
| `GET /_ml/datafeeds/datafeed-{job_id}/_stats`                                    | `elastic es ml get-datafeed-stats --datafeed-id 'datafeed-<job_id>'`                                |
| `POST /.ml-anomalies-*/_search`                                                  | `elastic es search --index '.ml-anomalies-*' --input-file '<search-body.json>'`                     |
| `POST /.ml-annotations-*/_search`                                                | `elastic es search --index '.ml-annotations-*' --input-file '<search-body.json>'`                   |
| `POST /.ml-notifications-*/_search`                                              | `elastic es search --index '.ml-notifications-*' --input-file '<search-body.json>'`                 |
| `POST /_ml/anomaly_detectors/_estimate_model_memory`                             | `elastic es ml estimate-model-memory --analysis-config '<json>'`                                    |
| `PUT /_ml/anomaly_detectors/{job_id}`                                            | `elastic es ml put-job --job-id '<job_id>' --input-file '<job-body.json>'`                          |
| `PUT /_ml/datafeeds/datafeed-{job_id}`                                           | `elastic es ml put-datafeed --datafeed-id 'datafeed-<job_id>' --input-file '<datafeed-body.json>'`  |
| `POST /_ml/anomaly_detectors/{job_id}/_open`                                     | `elastic es ml open-job --job-id '<job_id>'`                                                        |
| `POST /_ml/anomaly_detectors/{job_id}/_close`                                    | `elastic es ml close-job --job-id '<job_id>'`                                                       |
| `POST /_ml/anomaly_detectors/{job_id}/_update`                                  | `elastic es ml update-job --job-id '<job_id>' --analysis-limits '<json>'`                           |
| `POST /_ml/datafeeds/datafeed-{job_id}/_update`                                 | `elastic es ml update-datafeed --datafeed-id 'datafeed-<job_id>' --input-file '<update-body.json>'` |
| `POST /_ml/datafeeds/datafeed-{job_id}/_start`                                  | `elastic es ml start-datafeed --datafeed-id 'datafeed-<job_id>'`                                    |
| `POST /_ml/datafeeds/datafeed-{job_id}/_stop`                                   | `elastic es ml stop-datafeed --datafeed-id 'datafeed-<job_id>'`                                     |
| `POST /_ml/datafeeds/datafeed-{job_id}/_preview`                                | `elastic es ml preview-datafeed --datafeed-id 'datafeed-<job_id>'`                                  |
| `POST /_ml/anomaly_detectors/{job_id}/model_snapshots/{snapshot_id}/_revert`     | `elastic es ml revert-model-snapshot --job-id '<job_id>' --snapshot-id '<snapshot_id>'`             |

每种`result_type`的搜索体形状和故障排除查询在
[references/investigation-queries.md](references/investigation-queries.md)和
[references/troubleshooting-reference.md](references/troubleshooting-reference.md)中记录。
