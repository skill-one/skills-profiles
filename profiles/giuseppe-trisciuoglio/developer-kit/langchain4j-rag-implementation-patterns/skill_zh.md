# LangChain4j RAG 实现模式

## 概述

使用 LangChain4j 实现 RAG 系统：文档摄取管道、嵌入存储和向量搜索，用于聊天式文档和知识增强型 AI 应用。

## 何时使用此技能

- 构建聊天式文档系统或 PDF、文本文件或网页上的文档问答
- 创建可访问公司知识库或外部来源的 AI 助手
- 实现文档库的语义搜索或混合搜索
- 构建具有精选知识和来源归因的特定领域 AI

## 说明

### 初始化 RAG 项目

创建一个包含所需依赖项的新 Spring Boot 项目：

**pom.xml**:
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.8.0</version>
</dependency>
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.8.0</version>
</dependency>
```

### 设置文档摄取

配置文档加载和处理并进行验证：

**验证检查点**：摄取后，验证嵌入数量与片段数量是否匹配，并使用样本查询测试检索。

```java
@Configuration
public class RAGConfiguration {

    @Bean
    public EmbeddingModel embeddingModel() {
        return OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();
    }

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return new InMemoryEmbeddingStore<>();
    }
}
```

创建文档摄取服务：

```java
@Service
@RequiredArgsConstructor
public class DocumentIngestionService {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;

    public void ingestDocument(String filePath, Map<String, Object> metadata) {
        Document document = FileSystemDocumentLoader.loadDocument(filePath);
        document.metadata().putAll(metadata);

        DocumentSplitter splitter = DocumentSplitters.recursive(
            500, 50, new OpenAiTokenCountEstimator("text-embedding-3-small")
        );

        List<TextSegment> segments = splitter.split(document);
        List<Embedding> embeddings = embeddingModel.embedAll(segments).content();
        embeddingStore.addAll(embeddings, segments);

        // 验证：验证嵌入数量与片段是否匹配
        if (embeddings.size() != segments.size()) {
            throw new IllegalStateException("嵌入数量不匹配：预期 " + segments.size() + "，实际得到 " + embeddings.size());
        }
    }

    public boolean validateIngestion(String testQuery) {
        // 验证：使用样本查询测试检索
        Embedding queryEmbedding = embeddingModel.embed(testQuery).content();
        List<EmbeddingMatch<TextSegment>> results = embeddingStore.search(
            EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(1)
                .build()
        ).matches();
        return !results.isEmpty();
    }
}
```

### 配置内容检索

使用过滤设置内容检索：

**验证检查点**：配置后，使用已知查询测试检索以验证嵌入是否可搜索。

```java
@Configuration
public class ContentRetrieverConfiguration {

    @Bean
    public ContentRetriever contentRetriever(
            EmbeddingStore<TextSegment> embeddingStore,
            EmbeddingModel embeddingModel) {

        return EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(5)
            .minScore(0.7)
            .build();
    }
}
```

### 创建支持 RAG 的 AI 服务

定义具有上下文检索的 AI 服务：

```java
interface KnowledgeAssistant {
    @SystemMessage("""
        你是一个知识渊博的助手，可以访问一个全面的知识库。

        回答问题时：
        1. 使用从知识库提供的上下文
        2. 如果信息不在上下文中，请明确说明
        3. 提供准确、有帮助的回复
        4. 在可能的情况下，引用具体来源
        5. 如果上下文不足，请请求澄清
        """)
    String answerQuestion(String question);
}

@Service
@RequiredArgsConstructor
public class KnowledgeService {

    private final KnowledgeAssistant assistant;

    public KnowledgeService(ChatModel chatModel, ContentRetriever contentRetriever) {
        this.assistant = AiServices.builder(KnowledgeAssistant.class)
            .chatModel(chatModel)
            .contentRetriever(contentRetriever)
            .build();
    }

    public String answerQuestion(String question) {
        return assistant.answerQuestion(question);
    }
}
```

## 示例

### 基本文档处理

```java
public class BasicRAGExample {
    public static void main(String[] args) {
        var embeddingStore = new InMemoryEmbeddingStore<TextSegment>();

        var embeddingModel = OpenAiEmbeddingModel.builder()
            .apiKey(System.getenv("OPENAI_API_KEY"))
            .modelName("text-embedding-3-small")
            .build();

        var ingestor = EmbeddingStoreIngestor.builder()
            .embeddingModel(embeddingModel)
            .embeddingStore(embeddingStore)
            .build();

        ingestor.ingest(Document.from("Spring Boot 是一个用于构建 Java 应用的框架，配置最小化。"));

        var retriever = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .build();
    }
}
```

### 多领域助手

```java
interface MultiDomainAssistant {
    @SystemMessage("""
        你是一个具有多领域知识的专业助手：
        - 技术文档
        - 公司政策
        - 产品信息
        - 客户支持指南

        根据问题的类型和可用上下文调整你的回复。
        始终标明信息来源的领域。
        """)
    String answerQuestion(@MemoryId String userId, String question);
}
```

### 分层 RAG

```java
@Service
@RequiredArgsConstructor
public class HierarchicalRAGService {

    private final EmbeddingStore<TextSegment> chunkStore;
    private final EmbeddingStore<TextSegment> summaryStore;
    private final EmbeddingModel embeddingModel;

    public String performHierarchicalRetrieval(String query) {
        List<EmbeddingMatch<TextSegment>> summaryMatches = searchSummaries(query);
        List<TextSegment> relevantChunks = new ArrayList<>();

        for (EmbeddingMatch<TextSegment> summaryMatch : summaryMatches) {
            String documentId = summaryMatch.embedded().metadata().getString("documentId");
            List<EmbeddingMatch<TextSegment>> chunkMatches = searchChunksInDocument(query, documentId);
            chunkMatches.stream()
                .map(EmbeddingMatch::embedded)
                .forEach(relevantChunks::add);
        }

        return generateResponseWithChunks(query, relevantChunks);
    }
}
```

## 最佳实践

### 文档分段

- 对于大多数应用，使用递归分段，每个片段 500-1000 个 token
- 在片段之间保持 20-50 个 token 的重叠以保留上下文
- 分段时考虑文档结构（标题、段落）
- 使用 token 感知的分段器以生成最佳嵌入

### 元数据策略

- 包括丰富的元数据用于过滤和归因：
  - 用户和租户标识符用于多租户
  - 文档类型和分类
  - 创建和修改时间戳
  - 版本和作者信息
  - 机密性和访问级别标签

### 查询处理

- 实现查询预处理和清理
- 考虑查询扩展以改善召回率
- 基于用户上下文动态过滤
- 使用重新排序以改善结果质量

### 性能优化

- 缓存嵌入以供重复查询使用
- 使用批量嵌入生成进行批量操作
- 实现分页以处理大型结果集
- 考虑异步处理以处理长时间运行的操作

## 常见模式

### 简单 RAG 管道

```java
@RequiredArgsConstructor
@Service
public class SimpleRAGPipeline {

    private final EmbeddingModel embeddingModel;
    private final EmbeddingStore<TextSegment> embeddingStore;
    private final ChatModel chatModel;

    public String answerQuestion(String question) {
        Embedding queryEmbedding = embeddingModel.embed(question).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
            .queryEmbedding(queryEmbedding)
            .maxResults(3)
            .build();

        List<TextSegment> segments = embeddingStore.search(request).matches().stream()
            .map(EmbeddingMatch::embedded)
            .collect(Collectors.toList());

        String context = segments.stream()
            .map(TextSegment::text)
            .collect(Collectors.joining("\n\n"));

        return chatModel.generate(context + "\n\n问题: " + question + "\n回答:");
    }
}
```

### 混合搜索（向量 + 关键词）

```java
@Service
@RequiredArgsConstructor
public class HybridSearchService {

    private final EmbeddingStore<TextSegment> vectorStore;
    private final FullTextSearchEngine keywordEngine;
    private final EmbeddingModel embeddingModel;

    public List<Content> hybridSearch(String query, int maxResults) {
        // 向量搜索
        List<Content> vectorResults = performVectorSearch(query, maxResults);

        // 关键词搜索
        List<Content> keywordResults = performKeywordSearch(query, maxResults);

        // 使用 RRF 算法组合并重新排序结果
        return combineResults(vectorResults, keywordResults, maxResults);
    }
}
```

## 故障排除

### 验证失败

**嵌入数量不匹配**：当片段 != 嵌入时抛出。检查分段配置和模型可用性。

**检索结果为空**：调用 `validateIngestion(testQuery)` 以验证嵌入是否可搜索。检查文档是否成功摄取。

**检索分数低**：验证 minScore 阈值（默认 0.7）是否过高。使用已知查询进行测试。

### 常见问题

**检索结果差**
- 检查文档分段大小和重叠设置
- 验证嵌入模型兼容性
- 确保元数据过滤器没有过于严格
- 考虑添加重新排序步骤
- 运行验证以确认嵌入存在

**性能慢**
- 使用缓存嵌入处理频繁查询
- 优化向量存储的数据库索引
- 实现分页以处理大型数据集
- 考虑异步处理以处理批量操作

**内存使用率高**
- 对于大型数据集使用基于磁盘的嵌入存储
- 实现适当的分页和过滤
- 定期清理未使用的嵌入
- 监控和优化分段大小

## 限制和警告

- **嵌入模型成本**：为大型文档集合生成嵌入可能很昂贵；实现缓存和批量处理。
- **向量存储可扩展性**：内存存储仅适用于开发；生产环境使用持久存储（Pinecone、Qdrant、Redis）。
- **分段大小权衡**：较小的分段提高精度但丢失上下文；较大的分段保留上下文但可能引入噪声。
- **过时数据**：缓存的嵌入在源文档更改时过时；实现更新策略。
- **token 限制**：RAG 上下文窗口有限；通常 3-5 个检索片段适合标准模型限制。
- **幻觉风险**：RAG 减少但不会消除幻觉；始终对照来源验证关键回复。
- **延迟**：向量搜索和嵌入生成增加延迟；考虑异步处理以用于实时应用。
- **元数据过滤**：过于严格的过滤器可能返回无结果；实现回退策略。
- **多租户**：确保适当的元数据隔离以防止跨租户数据泄露。

## 参考

- [API 参考](references/references.md) - 完整的 API 文档和接口
- [示例](references/examples.md) - 生产就绪示例和模式
- [官方 LangChain4j 文档](https://docs.langchain4j.dev/)
