# RAG 架构师

## 核心工作流

1. **需求分析** — 确定检索需求、延迟约束、准确度要求及规模
2. **向量存储设计** — 选择数据库、模式设计、索引策略、分片方法
3. **分块策略** — 文档分割、重叠、语义边界、元数据增强
4. **检索流程** — 嵌入选择、查询转换、混合检索、重新排序
5. **评估与迭代** — 指标追踪、检索调试、持续优化

每一步需验证后再进行下一步（见下文检查点）。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 向量数据库 | `references/vector-databases.md` | 比较 Pinecone、Weaviate、Chroma、pgvector、Qdrant |
| 嵌入模型 | `references/embedding-models.md` | 选择嵌入、微调、维度权衡 |
| 分块策略 | `references/chunking-strategies.md` | 文档分割、重叠、语义分块 |
| 检索优化 | `references/retrieval-optimization.md` | 混合检索、重新排序、查询扩展、过滤 |
| RAG 评估 | `references/rag-evaluation.md` | 指标、评估框架、检索调试 |

## 实现示例

### 1. 分块文档

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 在您的领域数据上评估 chunk_size — 切勿盲目使用 512
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " "],
)

chunks = splitter.create_documents(
    texts=[doc.page_content for doc in raw_docs],
    metadatas=[{"source": doc.metadata["source"], "timestamp": doc.metadata.get("timestamp")} for doc in raw_docs],
)
```

**检查点:** `assert all(c.metadata.get("source") for c in chunks), "缺少来源元数据"`

### 2. 生成嵌入及索引

```python
from openai import OpenAI
import qdrant_client
from qdrant_client.models import VectorParams, Distance, PointStruct

client = OpenAI()
qdrant = qdrant_client.QdrantClient("localhost", port=6333)

# 创建集合
qdrant.recreate_collection(
    collection_name="知识库",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

def embed_chunks(chunks: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    response = client.embeddings.create(input=chunks, model=model)
    return [r.embedding for r in response.data]

# 确定性 ID 的幂等插入及去重
import hashlib, uuid

points = []
for i, chunk in enumerate(chunks):
    doc_id = str(uuid.UUID(hashlib.md5(chunk.page_content.encode()).hexdigest()))
    embedding = embed_chunks([chunk.page_content])[0]
    points.append(PointStruct(id=doc_id, vector=embedding, payload=chunk.metadata))

qdrant.upsert(collection_name="知识库", points=points)
```

**检查点:** `assert qdrant.count("知识库").count == len(set(p.id for p in points)), "去重失败"`

### 3. 混合检索（向量 + BM25）

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, SparseVector
from rank_bm25 import BM25Okapi

def hybrid_search(query: str, tenant_id: str, top_k: int = 20) -> list:
    # 密集检索
    query_embedding = embed_chunks([query])[0]
    tenant_filter = Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])
    dense_results = qdrant.search(
        collection_name="知识库",
        query_vector=query_embedding,
        query_filter=tenant_filter,
        limit=top_k,
    )

    # 稀疏检索（BM25）
    corpus = [r.payload.get("text", "") for r in dense_results]
    bm25 = BM25Okapi([doc.split() for doc in corpus])
    bm25_scores = bm25.get_scores(query.split())

    # 互惠排序融合
    ranked = sorted(
        zip(dense_results, bm25_scores),
        key=lambda x: 0.6 * x[0].score + 0.4 * x[1],
        reverse=True,
    )
    return [r for r, _ in ranked[:top_k]]
```

**检查点:** `assert len(hybrid_search("测试查询", tenant_id="demo")) > 0, "混合检索未返回结果"`

### 4. 重新排序 Top-K 结果

从环境变量或密钥管理器加载提供者 API 密钥；切勿将它们提交到源代码。

```python
import os

import cohere

co = cohere.Client(os.environ["COHERE_API_KEY"])

def rerank(query: str, results: list, top_n: int = 5) -> list:
    docs = [r.payload.get("text", "") for r in results]
    reranked = co.rerank(query=query, documents=docs, top_n=top_n, model="rerank-english-v3.0")
    return [results[r.index] for r in reranked.results]
```

### 5. 检索评估

```python
# 对标记评估集运行 precision@k 和 recall@k
# python evaluate.py --metrics precision@10 recall@10 mrr --collection 知识库

from ragas import evaluate
from ragas.metrics import context_precision, context_recall, faithfulness, answer_relevancy
from datasets import Dataset

eval_dataset = Dataset.from_dict({
    "question": questions,
    "contexts": retrieved_contexts,
    "answer": generated_answers,
    "ground_truth": ground_truth_answers,
})

results = evaluate(eval_dataset, metrics=[context_precision, context_recall, faithfulness, answer_relevancy])
print(results)
```

**检查点:** 在转向 LLM 集成前，目标 `context_precision >= 0.7` 和 `context_recall >= 0.6`。

## 约束条件

### 必须执行
- 在提交前在您的领域数据上评估多个嵌入模型
- 为生产系统实现混合检索（向量 + 关键词）
- 为多租户或特定领域检索添加元数据过滤器
- 测量检索指标（precision@k、recall@k、MRR、NDCG）
- 在将上下文传递给 LLM 前使用重新排序 Top-K 结果
- 实现幂等摄取及去重（确定性 ID）
- 监控检索延迟和质量随时间变化
- 版本嵌入并计划模型迁移

### 切勿执行
- 在未在您的领域数据上评估的情况下使用默认分块大小（512）
- 跳过元数据增强（来源、时间戳、章节）
- 仅凭 LLM 输出质量而忽略检索质量指标
- 未预处理/清理就存储原始文档
- 对于复杂的多领域检索仅使用余弦相似度
- 在未在类似生产数据量上测试的情况下部署
- 忘记处理边缘情况（空结果、格式化错误的文档）
- 将嵌入模型与应用程序代码紧密耦合

## 输出模板

设计 RAG 架构时交付：
1. 系统架构图（摄取 + 检索流程）
2. 向量数据库选择及权衡分析
3. 分块策略（含示例及理由）
4. 检索流程设计（查询 → 结果流）
5. 评估计划（含指标、基准及通过/失败阈值）

[文档](https://jeffallan.github.io/claude-skills/skills/data-ml/rag-architect/)
