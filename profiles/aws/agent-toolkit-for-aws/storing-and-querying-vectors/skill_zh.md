# 使用 Amazon S3 Vectors 存储和查询向量

## 概述

Amazon S3 Vectors 是一个经济高效的 AWS 服务，用于大规模存储和查询向量嵌入。它针对长期存储进行了优化，冷查询延迟低于亚秒级，热查询延迟低至 100 毫秒。

## 决策指南

- **每秒数百/数千个持续查询 (QPS)**：不合适的工具。推荐使用 OpenSearch。
- **混合搜索、聚合、分面搜索**：推荐使用 OpenSearch，并将 S3 Vectors 作为存储引擎。有关 OpenSearch 集成，请在 AWS 文档中搜索 `"Using S3 Vectors with OpenSearch Service"`。
- **分层（批量 + 热存储）**：S3 Vectors 用于存储 + OpenSearch Serverless 用于实时处理。参考 `references/limits-and-patterns.md`。
- **经济高效的存储、不频繁的查询、RAG**：S3 Vectors 是理想选择。继续操作。

有关最新指南，请在 AWS 文档中搜索 `"S3 Vectors 最佳实践"`。

## 常见任务

开始前对请求进行分类：

- **简单查询**：现有索引，跳至步骤 6
- **标准**：你必须先列出现有索引，如果相关则建议复用。否则，新建索引 + 存储向量，然后遵循步骤 2-6
- **迁移或多租户**：先阅读 `references/limits-and-patterns.md`，然后遵循步骤 2-6

连接时必须使用 AWS MCP 服务器工具执行命令。如果 AWS MCP 不可用，则退回到 AWS CLI。你必须在使用前向用户解释每个步骤。

### 1. 验证依赖项

**约束条件：**

- 你必须检查 AWS MCP 工具或 AWS CLI 是否可用，如果缺失则通知用户
- 你必须确认目标 AWS 区域

### 2. 创建向量存储桶

你必须与用户确认存储桶名称。名称：3-63 个字符，仅限小写字母、数字、短横线。加密（默认为 SSE-S3 或 SSE-KMS 以符合合规要求）创建后不可更改。

```bash
aws s3vectors create-vector-bucket \
  --vector-bucket-name <BUCKET_NAME>
```

**约束条件：**

- 你必须解释加密创建后无法更改
- 对于 SSE-KMS，KMS 密钥策略必须授予 S3 Vectors 服务主体 `indexing.s3vectors.amazonaws.com` `kms:GenerateDataKey` 和 `kms:Decrypt` 权限。你必须使用完整的 KMS 密钥 ARN（而不是别名）。参考 `references/limits-and-patterns.md` 获取命令示例。

### 3. 创建向量索引

每个参数创建后都**不可更改**。

**预检查清单（必须与用户确认所有内容）：**

1. **维度**（必需，整数 1-4096）-- 必须与嵌入模型输出匹配
2. **距离度量**（必需）-- `cosine` 或 `euclidean`。使用嵌入模型推荐的度量方式；
3. **不可过滤元数据键**（可选，最多 10 个，1-63 个字符）-- 创建时声明或永久丢失。有关 Bedrock Knowledge Bases 集成，请在 AWS 文档中搜索 `"S3 Vectors Bedrock Knowledge Bases 先决条件"` 获取所需的键名。
4. **加密**（可选）-- 继承自存储桶。如果需要，可以按索引覆盖。

```bash
aws s3vectors create-index \
  --vector-bucket-name <BUCKET_NAME> \
  --index-name <INDEX_NAME> \
  --dimension <DIM> \
  --distance-metric <cosine|euclidean> \
  --data-type float32 \
  --metadata-configuration '{"nonFilterableMetadataKeys":["<KEY1>","<KEY2>"]}'
```

如果不需要不可过滤的键，则省略 `--metadata-configuration`。

索引名称：3-63 个字符，小写字母、数字、短横线、点。在存储桶内唯一。可过滤元数据：2 KB 限制。总元数据（可过滤 + 不可过滤的组合）：40 KB。参考 `references/metadata-filtering.md`。

### 4. 生成嵌入（如果需要）

如果用户已有嵌入，则跳至步骤 5（存储）或步骤 6（查询）。

**约束条件：**

- 你必须询问使用哪个嵌入模型（如果未指定）
- 你不得假设默认模型
- 维度必须与步骤 3 匹配
- 你必须使用相同的模型进行存储和查询

使用 Bedrock invoke-model 生成嵌入：

```bash
aws bedrock-runtime invoke-model \
  --model-id <MODEL_ID> \
  --content-type application/json \
  --cli-binary-format raw-in-base64-out \
  --body '{"inputText": "your text"}' \
  invoke-model-output.json
```

对于 CLI v2，你必须使用 `--cli-binary-format raw-in-base64-out`。输出文件是必需的。响应键取决于模型（例如，Titan 的 embedding，Cohere 的 embeddings）。对于 Titan，使用 `json.load(open('invoke-model-output.json'))['embedding']` 解析。在 put-vectors 或 query-vectors 中使用 `embedding` 数组作为 `float32`。对于批量嵌入生成，使用 AWS SDK 或 CLI。

### 5. 存储（put）向量

```bash
aws s3vectors put-vectors \
  --vector-bucket-name <BUCKET_NAME> \
  --index-name <INDEX_NAME> \
  --vectors '[{"key":"<ID>","data":{"float32":[<EMBEDDING>]},"metadata":{"topic":"science"}}]'
```

**约束条件：**

- 每次调用不得超过 500 个向量
- 应批量存储以优化成本
- 对于批量操作，应使用 SDK 而不是 CLI -- 向量负载可能太大无法作为 shell 参数传递
- 必须实现带退避的重试 `429 TooManyRequestsException`
- 参考 `references/limits-and-patterns.md` 获取批量模式

### 6. 查询向量

如果需要生成嵌入（步骤 4），然后查询：

```bash
aws s3vectors query-vectors \
  --vector-bucket-name <BUCKET_NAME> \
  --index-name <INDEX_NAME> \
  --query-vector '{"float32":[<EMBEDDING>]}' \
  --top-k 10 \
  --return-distance
```

可选：添加 `--return-metadata` 和/或 `--filter '{"topic":{"$eq":"science"}}'`（两者都需要 GetVectors 权限）。参考 `references/metadata-filtering.md`。

示例响应体：`{"vectors": [{"key": "id1", "distance": 0.45, "metadata": {"topic": "science"}}, ...], "distanceMetric": "cosine"}`

**约束条件：**

- 使用 `--filter` 或 `--return-metadata` 需要 `s3vectors:QueryVectors` AND `s3vectors:GetVectors` IAM 权限。没有 GetVectors，这些选项将返回 403。

## 故障排除

| 错误 | 原因 | 解决方法 |
|------|------|--------|
| `DimensionMismatch` | 维度不匹配索引 | 使用匹配的模型，或删除/重建索引（与用户确认 -- 销毁所有向量）。 |
| `403 Forbidden` 与 `--filter` 或 `--return-metadata` | 缺少 `s3vectors:GetVectors` | 将 `s3vectors:GetVectors` 添加到 IAM 策略。 |
| 结果少于 `--top-k` | 符合过滤条件的向量较少 | 预期 -- 过滤是内联的。放宽过滤条件。 |
| `429 TooManyRequestsException` | 超出每个索引的速率限制 | 带退避重试。跨索引分片以实现持续吞吐量。搜索 AWS 文档中的 `"S3 Vectors 限制和限制"` 获取当前限制。 |
| `AccessDeniedException` | 缺少 `s3vectors:*` IAM 操作 | S3 Vectors 使用 `s3vectors:*` 命名空间，而不是 `s3:*`。更新 IAM 策略。 |
| `RequestTimeoutException` 或服务不可用 | 请求超时或区域不支持 | 重试请求。有关区域可用性，搜索 AWS 文档中的 `"S3 Vectors 限制和限制"`。 |

## 其他资源

- [limits-and-patterns.md](references/limits-and-patterns.md) -- 多租户模式、批量摄取、SSE-KMS、迁移
- [metadata-filtering.md](references/metadata-filtering.md) -- 过滤运算符、不可过滤的元数据、Bedrock KB 键
