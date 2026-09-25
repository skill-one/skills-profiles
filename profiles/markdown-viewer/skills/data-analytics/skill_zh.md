# 数据分析图表生成器

**快速入门：** 定义数据源 → 声明摄取/ETL图标 → 连接到存储/仓库 → 添加BI/可视化 → 用 ` ```plantuml ` 管理员包围。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码管理员。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `left to right direction` 为数据管道（源 → 摄取 → 转换 → 存储 → 可视化）
- 使用 `mxgraph.aws4.*` 样板语法用于分析、数据库和存储图标
- 默认颜色自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "区域" { ... }` 或 `package "层" { ... }` 用于分组管道阶段
- 有向流使用 `-->`，异步/流式流使用 `..>`（虚线）

**完整样板参考：** 参考 [stencils/README.md](../uml/stencils/README.md) 获取 9500+ 可用图标。

## Mxgraph 样板语法

```
mxgraph.aws4.<icon> "标签" as <别名>
```

### 分析与ETL样板

| 类别 | 样板 | 目的 |
|----------|----------|---------|
| 查询引擎 | `athena`, `athena_data_source_connectors` | S3 数据上的无服务器 SQL |
| ETL | `glue`, `glue_crawlers`, `glue_data_catalog`, `aws_glue_data_quality`, `aws_glue_for_ray` | 数据集成和目录管理 |
| 流式传输 | `kinesis`, `kinesis_data_streams`, `kinesis_data_firehose`, `kinesis_data_analytics`, `kinesis_video_streams` | 实时数据流 |
| MapReduce | `emr`, `emr_engine`, `emr_engine_mapr_m3`, `emr_engine_mapr_m5` | 大数据处理（Spark、Hive） |
| 数据仓库 | `redshift`, `redshift_ra3`, `redshift_streaming_ingestion`, `redshift_ml` | 列式分析仓库 |
| 搜索 | `opensearch_service_data_node`, `opensearch_ingestion`, `cloudsearch` | 全文搜索和日志分析 |
| BI | `quicksight` | 仪表板和可视化 |
| 数据湖 | `lake_formation`, `s3`, `glacier`, `glacier_deep_archive` | 受管理的数据湖存储 |
| 目录 | `datazone_custom_asset_type`, `data_exchange` | 数据治理和共享 |
| 流式 Kafka | `msk`, `msk_connect` | 管理的 Kafka 流 |

### 数据库样板

| 类别 | 样板 | 目的 |
|----------|----------|---------|
| 关系型 | `aurora`, `aurora_instance`, `rds`, `rds_instance`, `rds_mysql_instance`, `rds_postgresql_instance` | 事务型数据库 |
| NoSQL | `dynamodb`, `dynamodb_table`, `dynamodb_global_secondary_index`, `dynamodb_stream` | 键值和文档存储 |
| 图形 | `neptune` | 图形数据库 |
| 内存中 | `elasticache`, `elasticache_for_redis`, `elasticache_for_memcached` | 缓存和会话存储 |
| 文档 | `documentdb`, `documentdb_with_mongodb_compatibility` | 文档数据库 |
| 分类账 | `quantum_ledger_database` | 不可变事务日志 |
| 宽列 | `keyspaces` | Cassandra 兼容 |

### 连接类型

| 语法 | 含义 | 用例 |
|--------|---------|----------|
| `A --> B` | 实线箭头 | 批量数据流 / API 调用 |
| `A ..> B` | 虚线箭头 | 流式传输 / 异步 / CDC |
| `A -- B` | 实线 | 双向同步 |
| `A --> B : "标签"` | 带标签的连接 | 描述数据格式或容量 |

### 快速示例

```plantuml
@startuml
left to right direction
mxgraph.aws4.s3 "数据湖\n(S3)" as s3
mxgraph.aws4.glue "Glue\nETL" as glue
mxgraph.aws4.redshift "Redshift" as rs
mxgraph.aws4.quicksight "QuickSight" as qs

s3 --> glue
glue --> rs
rs --> qs
@enduml
```

## 数据分析架构类型

| 类型 | 目的 | 关键样板 | 示例 |
|------|---------|--------------|---------|
| 数据湖 | 集中化原始数据存储 | `s3`, `lake_formation`, `glue`, `athena` | [data-lake.md](examples/data-lake.md) |
| 实时流式传输 | 事件流处理 | `kinesis`, `msk`, `lambda_function`, `opensearch_service` | [real-time-streaming.md](examples/real-time-streaming.md) |
| 数据仓库 | 星型架构分析 | `redshift`, `glue`, `quicksight` | [data-warehouse.md](examples/data-warehouse.md) |
| ETL 管道 | 提取-转换-加载 | `glue`, `glue_crawlers`, `glue_data_catalog`, `s3` | [etl-pipeline.md](examples/etl-pipeline.md) |
| 日志分析 | 集中化日志 | `kinesis_data_firehose`, `opensearch_service`, `lambda_function` | [log-analytics.md](examples/log-analytics.md) |
| ML 特征存储 | 特征工程管道 | `glue`, `s3`, `athena`, `emr` | [ml-feature-pipeline.md](examples/ml-feature-pipeline.md) |
| CDC 管道 | 数据库变更捕获 | `dynamodb_streams`, `kinesis`, `lambda_function`, `redshift` | [cdc-pipeline.md](examples/cdc-pipeline.md) |
| 多源 BI | 跨数据库报告 | `aurora`, `dynamodb`, `redshift`, `quicksight` | [multi-source-bi.md](examples/multi-source-bi.md) |
