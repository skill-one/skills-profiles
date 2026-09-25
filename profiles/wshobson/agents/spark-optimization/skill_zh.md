# Apache Spark 优化

优化 Apache Spark 作业的生产模式，包括分区策略、内存管理、shuffle 优化和性能调优。

## 何时使用此技能

- 优化缓慢的 Spark 作业
- 调整内存和执行器配置
- 实现高效的分区策略
- 调试 Spark 性能问题
- 扩展 Spark 管道以处理大型数据集
- 减少 shuffle 和数据倾斜

## 核心概念

### 1. Spark 执行模型

```
驱动程序程序
    ↓
作业（由 action 触发）
    ↓
阶段（shuffle 分隔）
    ↓
任务（每个分区一个）
```

### 2. 关键性能因素

| 因素            | 影响                | 解决方案                      |
| -------------- | ------------------- | ----------------------------- |
| **Shuffle**    | 网络I/O、磁盘I/O    | 最小化宽转换                 |
| **数据倾斜**    | 任务执行时间不均    | 添加盐值、广播连接           |
| **序列化**      | CPU开销             | 使用 Kryo、列式格式           |
| **内存**        | GC 压力、溢出       | 调整执行器内存               |
| **分区**        | 并行度               | 合理设置分区大小             |

## 快速入门

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# 创建优化的 Spark 会话
spark = (SparkSession.builder
    .appName("OptimizedJob")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate())

# 使用优化的设置读取数据
df = (spark.read
    .format("parquet")
    .option("mergeSchema", "false")
    .load("s3://bucket/data/"))

# 高效的转换
result = (df
    .filter(F.col("date") >= "2024-01-01")
    .select("id", "amount", "category")
    .groupBy("category")
    .agg(F.sum("amount").alias("total")))

result.write.mode("overwrite").parquet("s3://bucket/output/")
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **启用 AQE** - 自适应查询执行可处理许多问题
- **使用 Parquet/Delta** - 带压缩的列式格式
- **广播小表** - 避免小表连接时的 shuffle
- **监控 Spark UI** - 检查倾斜、溢出、GC
- **合理设置分区** - 每个分区 128MB - 256MB

### 不应该做

- **不要收集大量数据** - 保持数据分布式
- **不要不必要地使用 UDF** - 使用内置函数
- **不要过度缓存** - 内存有限
- **不要忽视数据倾斜** - 它主导作业时间
- **不要用 `.count()` 检查存在性** - 使用 `.take(1)` 或 `.isEmpty()`
