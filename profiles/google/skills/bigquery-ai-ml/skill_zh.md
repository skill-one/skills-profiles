# BigQuery AI & ML

BigQuery 与 Vertex AI 集成，可在 SQL 查询中直接使用内置函数（如 `AI.FORECAST`、`AI.KEY_DRIVERS`、`AI.DETECT_ANOMALIES` 和 `AI.GENERATE`）提供强大的机器学习和生成式 AI 功能。

## 参考目录

-   **函数参考**：

    -   **AI.AGG**：[ai_agg.md](references/ai_agg.md) - 多行语义聚合和汇总。
    -   **AI.CAUSAL_EFFECT**：[ai_causal_effect.md](references/ai_causal_effect.md) - 衡量干预对时间序列的影响。
    -   **AI.CLASSIFY**：[ai_classify.md](references/ai_classify.md) - 文本分类。
    -   **AI.DETECT_ANOMALIES**：[ai_detect_anomalies.md](references/ai_detect_anomalies.md) - 检测异常。
    -   **AI.EVALUATE**：[ai_evaluate.md](references/ai_evaluate.md) - 评估模型。
    -   **AI.FORECAST**：[ai_forecast.md](references/ai_forecast.md) - 时间序列预测。
    -   **AI.GENERATE**：[ai_generate.md](references/ai_generate.md) - 使用 LLM 生成文本。
    -   **AI.GENERATE_EMBEDDING**：[ai_generate_embedding.md](references/ai_generate_embedding.md) - 生成嵌入。
    -   **AI.GENERATE_TABLE**：[ai_generate_table.md](references/ai_generate_table.md) - 表值 AI 生成。
    -   **AI.IF**：[ai_if.md](references/ai_if.md) - 评估语义条件。
    -   **AI.KEY_DRIVERS**：[ai_key_drivers.md](references/ai_key_drivers.md) - 识别关键驱动因素，这是一个 TVF。
    -   **AI.SCORE**：[ai_score.md](references/ai_score.md) - 评分数据。
    -   **AI.SEARCH**：[ai_search.md](references/ai_search.md) - 语义搜索。
    -   **AI.SIMILARITY**：[ai_similarity.md](references/ai_similarity.md) - 语义相似度。
    -   **Remote Models**：[remote_models.md](references/remote_models.md) - 使用远程模型（Vertex AI）。
    -   **CONTRIBUTION_ANALYSIS**：[ml_contribution_analysis.md](references/ml_contribution_analysis.md) - 查找贡献因素、变化的关键驱动因素。需要创建 MODEL 实体。
    -   **ML.CORRELATION**：[ml_correlation.md](references/ml_correlation.md) - 计算列之间的相关性，可选择按维度切片。
    -   **ML.DETECT_CHANGE_POINTS**：[ml_detect_change_points.md](references/ml_detect_change_points.md) - 检测时间序列中的结构断裂或持续变化。
    -   **ML.SEASONALITY**：[ml_seasonality.md](references/ml_seasonality.md) - 从时间序列中提取季节性成分。
    -   **ML.TREND**：[ml_trend.md](references/ml_trend.md) - 从时间序列中提取长期趋势成分。
    -   **VECTOR_SEARCH**：[vector_search.md](references/vector_search.md) - 向量搜索最佳实践。

## 相关技能

-   [BigQuery 基础技能](../bigquery-basics)：SKILL.md 文件，包含核心 BigQuery 概念、资源管理、CLI 和客户端库。
