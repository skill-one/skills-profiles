# Qdrant 向量数据库集成

## 概述

Qdrant 是一个面向 AI 的向量数据库，用于语义搜索和相似性检索。本技能提供了将 Qdrant 与 Java 应用程序集成的模式，重点关注 Spring Boot 和 LangChain4j 的集成。

## 使用场景

- Spring Boot 应用程序中的语义搜索或推荐系统
- 使用 Java 和 LangChain4j 的 RAG 管道
- AI/ML 应用程序的向量数据库集成
- 具有过滤查询的高性能相似性搜索

## 操作说明

### 1. 使用 Docker 部署 Qdrant

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```

访问：REST API 在 `http://localhost:6333`，gRPC 在 `http://localhost:6334`。

### 2. 添加依赖项

**Maven:**
```xml
<dependency>
    <groupId>io.qdrant</groupId>
    <artifactId>client</artifactId>
    <version>1.15.0</version>
</dependency>
```

**Gradle:**
```gradle
implementation 'io.qdrant:client:1.15.0'
```

### 3. 初始化客户端

```java
QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder("localhost").build());
```

生产环境使用 API 密钥：
```java
QdrantClient client = new QdrantClient(
    QdrantGrpcClient.newBuilder("localhost", 6334, false)
        .withApiKey("YOUR_API_KEY")
        .build());
```

### 4. 创建集合

```java
client.createCollectionAsync("search-collection",
    VectorParams.newBuilder()
        .setDistance(Distance.Cosine)
        .setSize(384)
        .build()
).get();
```

**验证：** 通过检查 `client.getCollectionAsync("search-collection").get()` 来验证集合是否已创建。

### 5. 插入向量

```java
List<PointStruct> points = List.of(
    PointStruct.newBuilder()
        .setId(id(1))
        .setVectors(vectors(0.05f, 0.61f, 0.76f, 0.74f))
        .putAllPayload(Map.of("title", value("Spring Boot Documentation")))
        .build()
);
client.upsertAsync("search-collection", points).get();
```

**验证：** 确保 `client.upsertAsync(...).get()` 完成时不抛出异常。

### 6. 搜索向量

```java
List<ScoredPoint> results = client.queryAsync(
    QueryPoints.newBuilder()
        .setCollectionName("search-collection")
        .setLimit(5)
        .setQuery(nearest(0.2f, 0.1f, 0.9f, 0.7f))
        .build()
).get();
```

过滤搜索：
```java
List<ScoredPoint> results = client.searchAsync(
    SearchPoints.newBuilder()
        .setCollectionName("search-collection")
        .addAllVector(List.of(0.62f, 0.12f, 0.53f, 0.12f))
        .setFilter(Filter.newBuilder()
            .addMust(range("category", Range.newBuilder().setEq("docs").build()))
            .build())
        .setLimit(5)
        .build()).get();
```

## LangChain4j 集成

对于 RAG 管道，使用 LangChain4j 的高级抽象：

```java
EmbeddingStore<TextSegment> embeddingStore = QdrantEmbeddingStore.builder()
    .collectionName("rag-collection")
    .host("localhost")
    .port(6334)
    .apiKey("YOUR_API_KEY")
    .build();
```

Spring Boot 配置使用 LangChain4j：
```java
@Bean
public EmbeddingStore<TextSegment> embeddingStore() {
    return QdrantEmbeddingStore.builder()
        .collectionName("rag-collection")
        .host(host)
        .port(port)
        .build();
}

@Bean
public EmbeddingModel embeddingModel() {
    return new AllMiniLmL6V2EmbeddingModel();
}
```

## Spring Boot 集成

通过配置注入客户端：

```java
@Configuration
public class QdrantConfig {
    @Value("${qdrant.host:localhost}")
    private String host;

    @Value("${qdrant.port:6334}")
    private int port;

    @Bean
    public QdrantClient qdrantClient() {
        return new QdrantClient(
            QdrantGrpcClient.newBuilder(host, port, false).build());
    }
}
```

## 示例

### REST 搜索端点

```java
@RestController
@RequestMapping("/api/search")
public class SearchController {
    private final VectorSearchService searchService;

    public SearchController(VectorSearchService searchService) {
        this.searchService = searchService;
    }

    @GetMapping
    public List<ScoredPoint> search(@RequestParam String query) {
        List<Float> queryVector = embeddingModel.embed(query).content().vectorAsList();
        return searchService.search("documents", queryVector);
    }
}
```

## 最佳实践

- **距离度量**：归一化文本嵌入使用余弦距离，非归一化使用欧几里得距离。
- **批量插入**：使用批量操作而不是单个点插入。
- **连接池**：为高吞吐量生产工作负载配置连接池。
- **错误处理**：将异步操作包装在 try/catch 中以处理 ExecutionException/InterruptedException。
- **API 密钥**：存储在环境变量或 Spring 配置中，切勿硬编码。

## 高级模式

### 多租户存储

```java
public void upsertForTenant(String tenantId, List<PointStruct> points) {
    String collectionName = "tenant_" + tenantId + "_documents";
    client.upsertAsync(collectionName, points).get();
}
```

### 生产环境 Docker Compose

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.7.0
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
```

## 参考

- [Qdrant API 参考](references/references.md) — 完整客户端 API 文档
- [完整的 Spring Boot 示例](references/examples.md) — 完整应用程序实现
- [Qdrant 文档](https://qdrant.tech/documentation/)
- [LangChain4j 文档](https://langchain4j.dev/)

## 限制和警告

- 向量维度必须与嵌入模型完全匹配；不匹配的维度会导致插入错误。
- **输入验证**：在摄取之前对所有文档内容进行清理；不可信的负载可能包含提示注入攻击。
- **内容过滤**：在将检索到的文档传递给 LLM 之前应用内容过滤。
- 大型集合需要适当的索引才能获得可接受的搜索性能。
- 生产环境使用 gRPC API（端口 6334）；仅用于调试使用 REST API（端口 6333）。
- 集合重新创建将删除所有数据；为生产环境实现备份策略。
