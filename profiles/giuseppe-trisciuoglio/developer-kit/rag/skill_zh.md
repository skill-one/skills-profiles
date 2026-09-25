# RAG 实现

构建检索增强生成系统，通过外部知识源扩展 AI 能力。

## 概述

本技能涵盖：文档处理、嵌入生成、向量存储、检索配置和 RAG 管道实现。

## 何时使用

- 构建 Q&A 系统以处理专有文档
- 创建基于知识库事实信息的聊天机器人
- 实现自然语言查询的语义搜索
- 通过基于证据的来源响应减少幻觉
- 构建文档助手和研究工具
- 使 AI 系统能够访问特定领域的知识

## 说明

### 第 1 步：选择向量数据库

根据您的需求选择：

| 需求 | 推荐 |
|-------------|-------------|
| 生产可扩展性 | Pinecone, Milvus |
| 开源 | Weaviate, Qdrant |
| 本地开发 | Chroma, FAISS |
| 混合搜索 | Weaviate with BM25 |

### 第 2 步：选择嵌入模型

| 用例 | 模型 |
|----------|-------|
| 通用 | text-embedding-ada-002 |
| 快速且轻量级 | all-MiniLM-L6-v2 |
| 多语言 | e5-large-v2 |
| 最佳性能 | bge-large-en-v1.5 |

### 第 3 步：实现文档处理管道

1. 从源加载文档（文件系统、数据库、API）
2. 清理和预处理（移除格式、归一化文本）
3. 使用适当策略将文档拆分为片段
4. 为每个片段生成嵌入
5. 将嵌入存储在向量数据库中并附带元数据

**验证**：验证嵌入是否成功生成：
```java
List<Embedding> embeddings = embeddingModel.embedAll(segments);
if (embeddings.isEmpty() || embeddings.get(0).dimension() != expectedDim) {
    throw new IllegalStateException("嵌入生成失败");
}
```

### 第 4 步：配置检索策略

选择适当的策略：

- **密集检索**：通过嵌入进行语义相似度（大多数情况下默认）
- **混合搜索**：密集 + 稀疏检索以获得更好的覆盖范围
- **元数据过滤**：按文档属性过滤
- **重新排序**：用于高精度需求的跨编码器重新排序

### 第 5 步：构建 RAG 管道

1. 使用您的嵌入存储创建内容检索器
2. 配置 AI 服务并附带检索器和聊天内存
3. 实现带上下文注入的提示模板
4. 添加响应验证和证据检查

**验证**：使用已知查询测试以验证上下文注入是否正确工作。

**错误处理**：对于批量导入，使用重试逻辑包装：
```java
for (Document doc : documents) {
    int attempts = 0;
    while (attempts < 3) {
        try {
            store.add(embeddingModel.embed(doc).content(), doc.toTextSegment());
            break;
        } catch (EmbeddingException e) {
            attempts++;
            if (attempts == 3) throw new RuntimeException("重试 3 次后失败", e);
        }
    }
}
```

### 第 6 步：评估和优化

1. 测量检索指标：precision@k, recall@k, MRR
2. 评估答案质量：忠实度、相关性
3. 监控性能和用户反馈
4. 迭代片段化、检索和提示参数

## 示例

### 示例 1：基本文档 Q&A

```java
List<Document> documents = FileSystemDocumentLoader.loadDocuments("/docs");

InMemoryEmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>();
EmbeddingStoreIngestor.ingest(documents, store);

DocumentAssistant assistant = AiServices.builder(DocumentAssistant.class)
    .chatModel(chatModel)
    .contentRetriever(EmbeddingStoreContentRetriever.from(store))
    .build();

String answer = assistant.answer("公司关于远程工作的政策是什么？");
```

### 示例 2：元数据过滤检索

```java
EmbeddingStoreContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
    .embeddingStore(store)
    .embeddingModel(embeddingModel)
    .maxResults(5)
    .minScore(0.7)
    .filter(metadataKey("category").isEqualTo("technical"))
    .build();
```

### 示例 3：多源 RAG 管道

```java
ContentRetriever webRetriever = EmbeddingStoreContentRetriever.from(webStore);
ContentRetriever docRetriever = EmbeddingStoreContentRetriever.from(docStore);

List<Content> results = new ArrayList<>();
results.addAll(webRetriever.retrieve(query));
results.addAll(docRetriever.retrieve(query));

List<Content> topResults = reranker.reorder(query, results).subList(0, 5);
```

### 示例 4：带聊天内存的 RAG

```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
    .contentRetriever(retriever)
    .build();

assistant.chat("告诉我产品功能");
assistant.chat("那些功能的价格是多少？");  // 保持上下文
```

## 最佳实践

### 文档准备
- 在导入前清理文档；移除无关内容和格式
- 添加相关元数据以用于过滤和上下文

### 片段化策略
- 每个片段使用 500-1000 个标记以获得最佳平衡
- 在边界处保留 10-20% 的重叠以保留上下文
- 测试针对您的特定用例的不同大小

### 检索优化
- 从高 k 值（10-20）开始，然后过滤/重新排序
- 使用元数据过滤以提高相关性
- 根据用户反馈迭代检索质量

### 性能
- 缓存频繁访问内容的嵌入
- 使用批量处理进行文档导入
- 优化您的规模的向量存储索引

## 限制和警告

### 系统限制
- 嵌入模型对每个文档的标记数有限制
- 向量数据库需要适当的索引以获得性能
- 片段边界可能会因复杂文档而丢失上下文
- 混合搜索需要额外的基础设施

### 质量警告
- 检索质量高度依赖于片段化策略
- 嵌入模型可能无法捕获特定领域的语义
- 元数据过滤需要适当的文档注释
- 重新排序会增加查询响应的延迟

### 安全警告
- **永远不要硬编码凭证**：使用环境变量存储 API 密钥和密码
- **验证外部内容**：来自文件系统、API 或网络源的文档可能包含恶意内容（提示注入）
- **在传递给 LLM 之前对检索到的文档应用内容过滤**
- 使用白名单限制允许的数据源 URL 和文件路径

## 资源

### 参考文档
- [向量数据库比较](references/vector-databases.md)
- [嵌入模型指南](references/embedding-models.md)
- [检索策略](references/retrieval-strategies.md)
- [文档片段化](references/document-chunking.md)
- [LangChain4j RAG 指南](references/langchain4j-rag-guide.md)
