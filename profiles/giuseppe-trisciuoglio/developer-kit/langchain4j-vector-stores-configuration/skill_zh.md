# LangChain4J 向量存储配置

使用 LangChain4J 为检索增强生成应用配置向量存储。

## 概述

LangChain4J 提供了针对向量存储（PostgreSQL/pgvector、Pinecone、MongoDB Atlas、Milvus、Neo4j）的统一抽象，支持基于构建者的配置、元数据过滤和混合搜索。

## 使用场景

- 为语义搜索和 RAG 应用配置向量存储
- 设置支持元数据过滤和混合搜索的嵌入存储
- 优化向量数据库性能以支持生产 AI 工作负载

## 使用说明

### 基本向量存储设置

为向量操作配置嵌入存储：

```java
@Bean
public EmbeddingStore<TextSegment> embeddingStore() {
    return PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("vectordb")
        .user("username")
        .password("password")
        .table("embeddings")
        .dimension(1536) // OpenAI 嵌入维度
        .createTable(true)
        .useIndex(true)
        .build();
}
```

### 验证流程

遵循此流程确保正确的向量存储设置：

1. **配置**：使用所需的维度和连接参数构建嵌入存储
2. **测试连接**：在导入数据前通过健康检查验证存储连接性
3. **验证维度**：确认嵌入模型维度与存储配置匹配
4. **导入测试数据**：添加一小批测试文档以验证导入功能
5. **运行测试查询**：执行样本语义搜索以确认检索准确性
6. **进入生产环境**：只有所有步骤通过后，才进行完整数据导入

### 配置多个向量存储

为不同用例使用不同的存储：

```java
@Configuration
public class MultiVectorStoreConfiguration {

    @Bean
    @Qualifier("documentsStore")
    public EmbeddingStore<TextSegment> documentsEmbeddingStore() {
        return PgVectorEmbeddingStore.builder()
            .table("document_embeddings")
            .dimension(1536)
            .build();
    }

    @Bean
    @Qualifier("chatHistoryStore")
    public EmbeddingStore<TextSegment> chatHistoryEmbeddingStore() {
        return MongoDbEmbeddingStore.builder()
            .collectionName("chat_embeddings")
            .build();
    }
}
```

### 实现文档导入

使用 EmbeddingStoreIngestor 进行自动化文档处理：

```java
@Bean
public EmbeddingStoreIngestor embeddingStoreIngestor(
        EmbeddingStore<TextSegment> embeddingStore,
        EmbeddingModel embeddingModel) {

    return EmbeddingStoreIngestor.builder()
        .documentSplitter(DocumentSplitters.recursive(
            300,  // maxSegmentSizeInTokens
            20,   // maxOverlapSizeInTokens
            new OpenAiTokenizer(GPT_3_5_TURBO)
        ))
        .embeddingModel(embeddingModel)
        .embeddingStore(embeddingStore)
        .build();
}
```

### 设置元数据过滤

配置基于元数据的过滤功能：

```java
// MongoDB 的元数据字段映射
IndexMapping indexMapping = IndexMapping.builder()
    .dimension(1536)
    .metadataFieldNames(Set.of("category", "source", "created_date", "author"))
    .build();

// 带元数据过滤的搜索
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(queryEmbedding)
    .maxResults(10)
    .filter(and(
        metadataKey("category").isEqualTo("technical_docs"),
        metadataKey("created_date").isGreaterThan(LocalDate.now().minusMonths(6))
    ))
    .build();
```

### 配置生产环境设置

实现连接池和监控：

```java
@Bean
public EmbeddingStore<TextSegment> optimizedPgVectorStore() {
    HikariConfig hikariConfig = new HikariConfig();
    hikariConfig.setJdbcUrl("jdbc:postgresql://localhost:5432/vectordb");
    hikariConfig.setUsername("username");
    hikariConfig.setPassword("password");
    hikariConfig.setMaximumPoolSize(20);
    hikariConfig.setMinimumIdle(5);
    hikariConfig.setConnectionTimeout(30000);

    DataSource dataSource = new HikariDataSource(hikariConfig);

    return PgVectorEmbeddingStore.builder()
        .dataSource(dataSource)
        .table("embeddings")
        .dimension(1536)
        .useIndex(true)
        .build();
}
```

### 实现健康检查

监控向量存储连接性：

```java
@Component
public class VectorStoreHealthIndicator implements HealthIndicator {

    private final EmbeddingStore<TextSegment> embeddingStore;

    @Override
    public Health health() {
        try {
            embeddingStore.search(EmbeddingSearchRequest.builder()
                .queryEmbedding(new Embedding(Collections.nCopies(1536, 0.0f)))
                .maxResults(1)
                .build());

            return Health.up()
                .withDetail("store", embeddingStore.getClass().getSimpleName())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

## 示例

### 基本RAG应用设置

```java
@Configuration
public class SimpleRagConfig {

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return PgVectorEmbeddingStore.builder()
            .host("localhost")
            .database("rag_db")
            .table("documents")
            .dimension(1536)
            .build();
    }

    @Bean
    public ChatLanguageModel chatModel() {
        return OpenAiChatModel.withApiKey(System.getenv("OPENAI_API_KEY"));
    }
}
```

### 语义搜索服务

```java
@Service
public class SemanticSearchService {

    private final EmbeddingStore<TextSegment> store;
    private final EmbeddingModel embeddingModel;

    public List<String> search(String query, int maxResults) {
        Embedding queryEmbedding = embeddingModel.embed(query).content();

        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(maxResults)
            .minScore(0.75)
            .build();

        return store.search(request).matches().stream()
            .map(match -> match.embedded().text())
            .toList();
    }
}
```

### 带监控的生产设置

```java
@Configuration
public class ProductionVectorStoreConfig {

    @Bean
    public EmbeddingStore<TextSegment> vectorStore(
            @Value("${vector.store.host}") String host,
            MeterRegistry meterRegistry) {

        EmbeddingStore<TextSegment> store = PgVectorEmbeddingStore.builder()
            .host(host)
            .database("production_vectors")
            .useIndex(true)
            .indexListSize(200)
            .build();

        return new MonitoredEmbeddingStore<>(store, meterRegistry);
    }
}
```

## 最佳实践

### 选择合适的向量存储

**开发环境：**
- 使用 `InMemoryEmbeddingStore` 进行本地开发和测试
- 快速设置，无外部依赖
- 应用重启时数据会丢失

**生产环境：**
- **PostgreSQL + pgvector**：适用于现有 PostgreSQL 环境
- **Pinecone**：托管服务，适合快速原型开发
- **MongoDB Atlas**：与现有 MongoDB 应用良好集成
- **Milvus/Zilliz**：适用于大规模部署的高性能方案

### 配置适当的索引类型

根据性能需求选择索引类型：

```java
// 高召回需求
.indexType(IndexType.FLAT)  // 精确搜索，较慢但准确

// 平衡性能
.indexType(IndexType.IVF_FLAT)  // 速度和准确性良好平衡

// 高速近似搜索
.indexType(IndexType.HNSW)  // 最快，准确性略低
```

### 优化向量维度

将嵌入维度与您的模型匹配：

```java
// OpenAI text-embedding-3-small
.dimension(1536)

// OpenAI text-embedding-3-large
.dimension(3072)

// Sentence Transformers
.dimension(384)  // all-MiniLM-L6-v2
.dimension(768)  // all-mpnet-base-v2
```

### 实现批量操作

使用批量操作以提高性能：

```java
@Service
public class BatchEmbeddingService {

    private static final int BATCH_SIZE = 100;

    public void addDocumentsBatch(List<Document> documents) {
        for (List<Document> batch : Lists.partition(documents, BATCH_SIZE)) {
            List<TextSegment> segments = batch.stream()
                .map(doc -> TextSegment.from(doc.text(), doc.metadata()))
                .collect(Collectors.toList());

            List<Embedding> embeddings = embeddingModel.embedAll(segments)
                .content();

            embeddingStore.addAll(embeddings, segments);
        }
    }
}
```

### 安全配置

保护敏感配置：

```java
// 使用环境变量
@Value("${vector.store.api.key:#{null}}")
private String apiKey;

// 验证配置
@PostConstruct
public void validateConfiguration() {
    if (StringUtils.isBlank(apiKey)) {
        throw new IllegalStateException("Vector store API key must be configured");
    }
}
```

## 参考

有关全面文档和高级配置，请参阅：

- [API 参考](references/api-reference.md) - 完整 API 文档
- [示例](references/examples.md) - 生产就绪示例

## 限制和警告

- 向量维度必须与嵌入模型匹配；不匹配的维度会导致错误
- 大型向量集合需要适当的索引配置才能获得可接受的搜索性能
- 嵌入生成可能很昂贵；实现批处理和缓存策略
- 不同的向量存储支持不同的距离度量；验证兼容性
- 连接池对生产部署至关重要，以防止连接耗尽
- 元数据过滤功能在向量存储实现之间有所不同
- 向量存储消耗大量内存；在生产中监控资源使用情况
- 在向量存储提供者之间迁移可能需要重新嵌入所有文档
- 批量操作比单文档操作更高效
- 始终在应用启动时验证配置，以便快速失败
