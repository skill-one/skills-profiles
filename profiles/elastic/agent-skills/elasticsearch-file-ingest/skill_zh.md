# Elasticsearch 文件摄取

对大型数据文件（NDJSON、CSV、Parquet、Arrow IPC）进行流式摄取和转换，将其导入 Elasticsearch。

## 功能与用例

- **流式处理**：无需耗尽内存即可处理大文件
- **高吞吐量**：在普通硬件上每秒可处理 50k+ 个文档
- **格式**：NDJSON、CSV、Parquet、Arrow IPC
- **转换**：在摄取过程中应用自定义 JavaScript 转换（丰富、拆分、过滤）
- **批量处理**：摄取匹配模式的多個文件（例如，`logs/*.json`）
- **文档拆分**：将一个源文档转换为多个目标

## 前置条件

- **可访问 Elasticsearch 8.x 或 9.x**（本地或远程）
- **安装 Node.js 22+**

## 安装

此技能是自包含的。`scripts/` 文件夹和 `package.json` 位于此技能的目录中。从该目录运行所有命令。在引用位于其他位置的数据文件时使用绝对路径。

在首次使用前，安装依赖项：

```bash
npm install
```

### 环境配置

Elasticsearch 连接完全由用户通过环境变量配置。**切勿将凭证作为命令行参数传递**。如果测试失败，请向用户输出以下设置选项，然后停止。在成功连接测试之前，不要继续进行摄取。

#### 选项 1：Elastic Cloud（推荐用于生产）

```bash
export ELASTICSEARCH_CLOUD_ID="<your-cloud-id>"
export ELASTICSEARCH_API_KEY="<your-api-key>"
```

#### 选项 2：带 API 密钥的直接 URL

```bash
export ELASTICSEARCH_URL="https://elasticsearch:9200"
export ELASTICSEARCH_API_KEY="<your-api-key>"
```

#### 选项 3：基本认证

```bash
export ELASTICSEARCH_URL="https://elasticsearch:9200"
export ELASTICSEARCH_USERNAME="<your-username>"
export ELASTICSEARCH_PASSWORD="<your-password>"
```

#### 选项 4：本地开发

对于本地开发和测试，请参阅
[在本地运行 Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html)
来启动 Elasticsearch 和 Kibana。设置后，导出连接变量（URL 和 API 密钥或凭证），如选项 2 或选项 3 中所示。

#### 可选：跳过 TLS 验证（仅限开发）

```bash
export ELASTICSEARCH_INSECURE="true"
```

## 测试连接

在摄取数据前验证 Elasticsearch 连接：

```bash
node scripts/ingest.js test
```

始终首先运行此命令。如果测试失败，请在继续之前解决连接问题。

## 示例

### 摄取 JSON 文件

```bash
node scripts/ingest.js ingest --file /absolute/path/to/data.json --target my-index
```

### 通过 stdin 流式传输 NDJSON/CSV

```bash
# NDJSON
cat /absolute/path/to/data.ndjson | node scripts/ingest.js ingest --stdin --target my-index

# CSV
cat /absolute/path/to/data.csv | node scripts/ingest.js ingest --stdin --source-format csv --target my-index
```

### 直接摄取 CSV

```bash
node scripts/ingest.js ingest --file /absolute/path/to/users.csv --source-format csv --target users
```

### 直接摄取 Parquet

```bash
node scripts/ingest.js ingest --file /absolute/path/to/users.parquet --source-format parquet --target users
```

### 直接摄取 Arrow IPC

```bash
node scripts/ingest.js ingest --file /absolute/path/to/users.arrow --source-format arrow --target users
```

### 带解析选项的 CSV 摄取

```bash
# csv-options.json
# {
#   "columns": true,
#   "delimiter": ";",
#   "trim": true
# }

node scripts/ingest.js ingest --file /absolute/path/to/users.csv --source-format csv --csv-options csv-options.json --target users
```

### 从 CSV 推断映射/管道

使用 `--infer-mappings` 时，**切勿**与 `--source-format csv` 结合使用。推断会将原始样本发送到 Elasticsearch 的 `_text_structure/find_structure` 端点，该端点返回映射和带有 CSV 处理器的摄取管道。如果也设置了 `--source-format csv`，客户端和服务器端都会解析 CSV，导致空索引。让 `--infer-mappings` 处理所有内容：

```bash
node scripts/ingest.js ingest --file /absolute/path/to/users.csv --infer-mappings --target users
```

### 带选项的映射推断

```bash
# infer-options.json
# {
#   "sampleBytes": 200000,
#   "lines_to_sample": 2000
# }

node scripts/ingest.js ingest --file /absolute/path/to/users.csv --infer-mappings --infer-mappings-options infer-options.json --target users
```

### 带自定义映射的摄取

```bash
node scripts/ingest.js ingest --file /absolute/path/to/data.json --target my-index --mappings mappings.json
```

### 带转换的摄取

```bash
node scripts/ingest.js ingest --file /absolute/path/to/data.json --target my-index --transform transform.js
```

## 命令参考

### 必填选项

```bash
--target <index>         # 目标索引名
```

### 源选项（选择一个）

```bash
--file <path>            # 源文件（支持通配符，例如，logs/*.json）
--stdin                  # 从 stdin 读取 NDJSON/CSV
```

### 索引配置

```bash
--mappings <file.json>          # 映射文件
--infer-mappings                # 从文件/流推断映射/管道（切勿与 --source-format 结合使用）
--infer-mappings-options <file> # 推断选项（JSON 文件）
--delete-index                  # 如果存在则删除目标索引
--pipeline <name>               # 摄取管道名
```

### 处理

```bash
--transform <file.js>    # 转换函数（导出为 default 或 module.exports）
--source-format <fmt>    # 源格式：ndjson|csv|parquet|arrow（默认：ndjson）
--csv-options <file>     # CSV 解析器选项（JSON 文件）
--skip-header            # 跳过第一行（例如，CSV 标头）
```

### 性能

```bash
--buffer-size <kb>       # 缓冲区大小（KB）（默认：5120）
--total-docs <n>         # 总文档数（用于进度条）（文件/流）
--stall-warn-seconds <n> # 停滞警告阈值（默认：30）
--progress-mode <mode>   # 进度输出：auto|line|newline（默认：auto）
--debug-events           # 记录暂停/恢复/停滞事件
--quiet                  # 禁用进度条
```

## 转换函数

转换函数允许您在摄取过程中修改文档。创建一个导出转换函数的 JavaScript 文件：

### 基本转换（transform.js）

```javascript
// ES 模块（默认）
export default function transform(doc) {
  return {
    ...doc,
    full_name: `${doc.first_name} ${doc.last_name}`,
    timestamp: new Date().toISOString(),
  };
}

// 或 CommonJS
module.exports = function transform(doc) {
  return {
    ...doc,
    full_name: `${doc.first_name} ${doc.last_name}`,
  };
};
```

### 跳过文档

返回 `null` 或 `undefined` 以跳过文档：

```javascript
export default function transform(doc) {
  // 跳过无效文档
  if (!doc.email || !doc.email.includes("@")) {
    return null;
  }
  return doc;
}
```

### 拆分文档

返回一个数组，以从源文档创建多个目标文档：

```javascript
export default function transform(doc) {
  // 将推文拆分为多个标签文档
  const hashtags = doc.text.match(/#\w+/g) || [];
  return hashtags.map((tag) => ({
    hashtag: tag,
    tweet_id: doc.id,
    created_at: doc.created_at,
  }));
}
```

## 映射

### 自定义映射（mappings.json）

```json
{
  "properties": {
    "@timestamp": { "type": "date" },
    "message": { "type": "text" },
    "user": {
      "properties": {
        "name": { "type": "keyword" },
        "email": { "type": "keyword" }
      }
    }
  }
}
```

```bash
node scripts/ingest.js ingest --file /absolute/path/to/data.json --target my-index --mappings mappings.json
```

## 边界

- **切勿**回显、打印、记录或以其他方式泄露凭证环境变量的值
  (`$ELASTICSEARCH_API_KEY`, `$ELASTICSEARCH_PASSWORD`, `$ELASTICSEARCH_CLOUD_ID`, 等）。不要运行会暴露密钥值的 shell 命令（例如，`echo $ELASTICSEARCH_API_KEY`, `env | grep KEY`, `printenv`）。导出这些变量并运行内部读取它们的脚本是可以的且安全的——限制是在命令输出中暴露密钥值。验证连接的唯一方式是 `node scripts/ingest.js test`。如果测试失败，请要求用户检查他们的环境配置——不要尝试自行诊断凭证。
- **切勿**在没有明确用户确认的情况下运行破坏性命令（例如，使用 `--delete-index` 标志或删除现有索引和数据）。

## 指南

- **先测试**：始终在摄取数据前运行 `node scripts/ingest.js test`。如果连接失败，请要求用户验证他们的环境配置并重新测试。在测试通过之前，不要尝试摄取。
- **切勿**将 `--infer-mappings` 与 `--source-format` 结合使用。推断会创建一个服务器端摄取管道，该管道处理解析（例如，CSV 处理器）。使用 `--source-format csv` 会导致客户端和服务器端双重解析，导致空索引。单独使用 `--infer-mappings` 进行自动检测，或使用 `--source-format` 与显式 `--mappings` 进行手动控制。
- **使用 `--source-format csv` 与 `--mappings`** 当您希望客户端进行 CSV 解析且字段类型已知时。
- **单独使用 `--infer-mappings`** 当您希望 Elasticsearch 检测格式、推断字段类型并自动创建摄取管道时。

## 不应使用的情况

考虑替代方案用于：

- **重新索引或索引迁移**：使用 `elasticsearch-reindex` 技能复制、迁移或转换现有的 Elasticsearch 索引
- **实时摄取**：使用 [Filebeat](https://www.elastic.co/beats/filebeat) 或
  [Elastic Agent](https://www.elastic.co/guide/en/fleet/current/fleet-overview.html)
- **企业管道**：使用 [Logstash](https://www.elastic.co/products/logstash)
- **内置转换**：使用
  [Elasticsearch Transforms](https://www.elastic.co/guide/en/elasticsearch/reference/current/transforms.html)

## 额外资源

- [常见模式](references/patterns.md) - CSV 加载、批量摄取、丰富等详细示例
- [故障排除](references/troubleshooting.md) - 常见问题的解决方案

## 参考

- [Elasticsearch 映射](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
- [Elasticsearch 查询 DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
