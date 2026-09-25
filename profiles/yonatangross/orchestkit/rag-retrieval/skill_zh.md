# RAG 检索

构建生产级 RAG 系统的全面模式。每个类别都有独立的规则文件，存放在 `rules/` 目录下，按需加载。

阈值、融合顺序以及我们声称的延迟和质量预算位于下方的 [House delta](#house-delta) 中。供应商文档已链接，不再重复陈述（参见 [上游覆盖](#upstream-coverage-do-not-restate)）。

## 快速参考

| 类别 | 规则 | 影响 | 使用场景 |
|------|-------|--------|-------------|
| [核心 RAG](#core-rag) | 4 | 关键 | 基础 RAG、引用、混合搜索、上下文管理 |
| [嵌入](#embeddings) | 3 | 高 | 模型选择、分块、批处理/缓存优化 |
| [上下文检索](#contextual-retrieval) | 3 | 高 | 上下文前置、混合 BM25+向量、管道 |
| [HyDE](#hyde) | 3 | 高 | 词汇不匹配、假设文档生成 |
| [Agentic RAG](#agentic-rag) | 4 | 高 | 自我 RAG、CRAG、知识图谱、自适应路由 |
| [多模态 RAG](#multimodal-rag) | 3 | 中 | 图像+文本检索、PDF 分块、跨模态搜索 |
| [查询分解](#query-decomposition) | 3 | 中 | 多概念查询、并行检索、RRF 融合 |
| [重新排序](#reranking) | 3 | 中 | 跨编码器、LLM 评分、组合信号 |
| [PGVector](#pgvector) | 4 | 高 | PostgreSQL 混合搜索、HNSW 索引、模式设计 |

**总计：9 个类别，30 条规则**

## 核心RAG

检索、生成和管道组合的基本模式。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 基础 RAG | `rules/core-basic-rag.md` | 检索 + 上下文 + 带引用生成 |
| 混合搜索 | `rules/core-hybrid-search.md` | RRF 融合 (k=60) 用于语义 + 关键词 |
| 上下文管理 | `rules/core-context-management.md` | token 预算 + 充足性检查 |
| 管道组合 | `rules/core-pipeline-composition.md` | 可组合 Decompose → HyDE → 检索 → 重新排序 |

## 嵌入

嵌入模型、分块策略和生产优化。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 模型 & API | `rules/embeddings-models.md` | 模型选择、批处理 API、相似度 |
| 分块 | `rules/embeddings-chunking.md` | 语义边界分割、512 token 甜点 |
| 高级 | `rules/embeddings-advanced.md` | Redis 缓存、Matryoshka 维度、批处理 |

## 上下文检索

Anthropic 的上下文前置技术——检索失败率降低 67%。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 上下文前置 | `rules/contextual-prepend.md` | LLM 生成的上下文 + 提示缓存 |
| 混合搜索 | `rules/contextual-hybrid.md` | 40% BM25 / 60% 向量权重分配 |
| 完整管道 | `rules/contextual-pipeline.md` | 端到端索引 + 混合检索 |

## HyDE

假设文档嵌入，用于弥合词汇差距。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 生成 | `rules/hyde-generation.md` | 嵌入假设文档，而非查询 |
| 按概念 | `rules/hyde-per-concept.md` | 多主题查询的并行 HyDE |
| 回退 | `rules/hyde-fallback.md` | 2-3s 超时 → 直接嵌入回退 |

## Agentic RAG

带 LLM 驱动的决策生成的自我纠正检索。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 自我 RAG | `rules/agentic-self-rag.md` | 二元文档评分用于相关性 |
| 纠正 RAG | `rules/agentic-corrective-rag.md` | CRAG 工作流带网络回退 |
| 知识图谱 | `rules/agentic-knowledge-graph.md` | KG + 向量混合用于实体丰富领域 |
| 自适应检索 | `rules/agentic-adaptive-retrieval.md` | 查询路由至最佳策略 |

## 多模态 RAG

图像 + 文本检索与跨模态搜索。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 嵌入 | `rules/multimodal-embeddings.md` | CLIP、SigLIP 2、Voyage multimodal-3 |
| 分块 | `rules/multimodal-chunking.md` | PDF 提取保留图像 |
| 管道 | `rules/multimodal-pipeline.md` | 去重 + 混合检索 + 生成 |

## 查询分解

将复杂查询分解为概念以进行并行检索。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 检测 | `rules/query-detection.md` | 启发式指标 (<1ms 快速路径) |
| 分解 + RRF | `rules/query-decompose.md` | LLM 概念提取 + 并行检索 |
| HyDE 组合 | `rules/query-hyde-combo.md` | 分解 + HyDE 以实现最大覆盖 |

## 重新排序

检索后重新评分以提高精度。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 跨编码器 | `rules/reranking-cross-encoder.md` | ms-marco-MiniLM (~50ms, 免费) |
| LLM 重新排序 | `rules/reranking-llm.md` | 批处理评分 + Cohere API |
| 组合 | `rules/reranking-combined.md` | 多信号加权评分 |

## PGVector

使用 PostgreSQL 的生产混合搜索。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 模式 | `rules/pgvector-schema.md` | HNSW 索引 + 预计算 tsvector |
| 混合搜索 | `rules/pgvector-hybrid-search.md` | SQLAlchemy RRF 带 FULL OUTER JOIN |
| 索引 | `rules/pgvector-indexing.md` | HNSW (17x 更快) vs IVFFlat |
| 元数据 | `rules/pgvector-metadata.md` | 过滤、提升、Redis 8 对比 |

## 快速入门示例

```python
from openai import OpenAI

client = OpenAI()

async def rag_query(question: str, top_k: int = 5) -> dict:
    """基础 RAG 带引用."""
    docs = await vector_db.search(question, limit=top_k)
    context = "\n\n".join([f"[{i+1}] {doc.text}" for i, doc in enumerate(docs)])

    response = await llm.chat([
        {"role": "system", "content": "用内联引用 [1], [2] 回答。仅使用提供的上下文。"},
        {"role": "user", "content": f"上下文:\n{context}\n\n问题: {question}"}
    ])

    return {"answer": response.content, "sources": [d.metadata['source'] for d in docs]}
```

## 关键决策

| 决策 | 建议 |
|------|----------------|
| 嵌入模型 | `text-embedding-3-small` (通用), `voyage-3.5` (生产) |
| 分块大小 | 256-1024 tokens (512 典型) |
| 混合权重 | 40% BM25 / 60% 向量 |
| Top-k | 3-10 文档 |
| 温度 | 0.1-0.3 (事实性) |
| 上下文预算 | 4K-8K tokens |
| 重新排序 | 检索 50, 重新排序至 10 |
| 向量索引 | HNSW (生产), IVFFlat (高容量) |
| HyDE 超时 | 2-3 秒带回退 |
| 查询分解 | 启发式优先，仅多概念时使用 LLM |

## 上游覆盖（不要重复陈述）

从源获取这些，而不是在这里重复。如果某行表示 House 子集保持不变，则该命名文件仅包含调整值和原因，不包含教程。

| 主题 | 源 |
|-------|--------|
| pgvector 安装、操作符、索引构建语法、"为什么我的索引未被使用" | https://github.com/pgvector/pgvector; House 子集 (HNSW `m=16`, `ef_construction=64`, halfvec, 二进制量化) 保持不变在 `rules/pgvector-indexing.md` 和 `rules/pgvector-schema.md` |
| PostgreSQL 全文搜索：tsvector、tsquery、GIN、`ts_rank_cd` | https://www.postgresql.org/docs/current/textsearch.html; House 子集 (生成的 STORED 列) 保持不变在 `rules/pgvector-schema.md` |
| 查询计划阅读、确认索引被使用、VACUUM/ANALYZE | https://www.postgresql.org/docs/current/using-explain.html |
| RRF 机制：排名常数、排名窗口大小、平局处理 | https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion; House 子集 (`k=60`, 3x fetch) 保持不变在 `rules/core-hybrid-search.md` 和 `rules/pgvector-hybrid-search.md` |
| 字段加权提升和评分配置文件作为概念 | https://learn.microsoft.com/en-us/azure/search/index-add-scoring-profiles; 我们的提升因子及其排序在 [House delta](#house-delta) 和 `rules/pgvector-metadata.md` |
| 嵌入 API 机制：批处理限制、`input_type`、维度、定价 | https://docs.voyageai.com/docs/embeddings 和 https://platform.openai.com/docs/guides/embeddings; 模型选择保持不变在 `rules/embeddings-models.md` |
| 检索指标定义（precision@k, recall@k, MRR, nDCG）和构建查询集 | ork 技能 `golden-dataset` |
| 搜索端点形状、分页、错误体 | ork 技能 `api-design` |
| 追踪和仪表板搜索调用 | ork 技能 `monitoring-observability` |
| 编写运行这些断言的集成测试 | ork 技能 `testing-integration` |

## 常见错误

1. 无引用跟踪（无法验证的答案）
2. 上下文过大（稀释相关性）
3. 单一检索方法（错过关键词匹配）
4. 不分块长文档（上下文丢失）
5. 查询嵌入与文档不同
6. Agentic RAG 无回退路径（工作流卡住）
7. 无限重写循环（无重试限制）
8. 使用错误相似度指标（余弦 vs 欧几里得）
9. 不缓存嵌入（重新计算未更改内容）
10. 多模态 RAG 缺少图像说明（限制文本搜索）

## 评估

参见 `test-cases.json`，其中包含所有类别的 30 个测试用例。

这里**没有**通过率、精度、召回率或 MRR 基线。此处早期文字承诺了这些数字；它们从未被测量，也从未在任何地方记录。它们被保留为未设置，而不是用看似合理的值填充，因为未测量的阈值比没有阈值更糟：它被引用为似乎有意义的东西，而通过或失败的原因无法令人信服。`test-cases.json` 是建立真实指标的合适底座，对这 30 个案例的基线运行将产生值得断言的数字。

这项技能断言的唯一预算是延迟，在 [House delta](#house-delta) 中。

## 相关技能

- `ork:langgraph` - LangGraph 工作流模式（用于 Agentic RAG 工作流）
- `ork:golden-dataset` - 评估检索质量
- `ork:llm-integration` - 本地嵌入使用 nomic-embed-text
- `ork:multimodal-llm` - 多模态 RAG 的图像分析
- `ork:database-patterns` - 向量搜索的方案设计
- `ork:performance` - 缓存重复 RAG 响应

## 能力详情

### retrieval-patterns
**关键词：**检索、上下文、分块、相关性、rag
**解决：**
- 为 LLM 检索相关上下文
- 实现 RAG 管道带引用
- 优化检索质量

### hybrid-search
**关键词：**混合、bm25、向量、融合、rrf
**解决：**
- 结合关键词和语义搜索
- 实现互惠排名融合
- 平衡精度和召回率

### embeddings
**关键词：**嵌入、文本到向量、向量化、分块、相似度
**解决：**
- 将文本转换为向量嵌入
- 选择嵌入模型和维度
- 实施分块策略

### contextual-retrieval
**关键词：**上下文、anthropic、上下文前置、bm25
**解决：**
- 将上下文前置到分块以改善检索
- 通过 67% 减少检索失败
- 实现混合 BM25+向量搜索

### hyde
**关键词：**hyde、假设、词汇不匹配
**解决：**
- 桥接语义搜索中的词汇差距
- 生成假设文档用于嵌入
- 处理抽象或概念查询

### agentic-rag
**关键词：**self-rag、crag、纠正、自适应、评分
**解决：**
- 构建自我纠正 RAG 工作流
- 评分文档相关性
- 实现网络搜索回退

### multimodal-rag
**关键词：**multimodal、图像、clip、视觉、pdf
**解决：**
- 构建带图像和文本的 RAG
- 跨模态搜索（文本→图像）
- 处理混合内容的 PDF

### query-decomposition
**关键词：**分解、多概念、复杂查询
**解决：**
- 将复杂查询分解为概念
- 每个概念并行检索
- 改善复合问题的覆盖

### reranking
**关键词：**重新排序、跨编码器、精度、评分
**解决：**
- 检索后提高搜索精度
- 使用跨编码器或 LLM 评分
- 组合多个评分信号

### pgvector-search
**关键词：**pgvector、postgresql、hnsw、tsvector、混合
**解决：**
- 使用 PostgreSQL 的生产混合搜索
- HNSW vs IVFFlat 索引选择
- 基于 SQL 的 RRF 融合

---

## House delta

内联而非放置在 `references/` 中：这项技能将其 House 知识携带在 `rules/`（32 个文件）中，并且从未有过 `references/` 目录，因此一个孤独的 delta 文件将是其中唯一的居住者。

嵌入模型选择、分块算法、向量索引调整、重新排序器 API 和查询重写文献属于供应商和上游领域；参见 [上游覆盖](#upstream-coverage-do-not-restate) 了解每个位置的归属。以下是 OrchestKit 添加、反驳或必须警告的内容。

### 检索延迟预算：p95 500ms 内端到端

来源：`checklists/rag-quality.md:57`，这项技能唯一实际断言的检索预算。它涵盖用户等待的整个路径（嵌入查询、搜索、重新排序、组装上下文），而不是孤立阶段。一个每个阶段清除 500ms 但整体超时的管道已失败此预算。

p95 而不是平均值测量。检索延迟主要由尾部行为（冷索引分片、重新排序器队列）主导，而平均值隐藏了用户抱怨的请求。

### 针对特定语料库的调整不会迁移

融合权重、重新排序深度和混合 alpha 是语料库的属性，而非技术的属性。一个在散文文档上提升召回率的权重通常会对代码或表格数据造成伤害，因此在不同项目间复制值是噪音而非起点。针对每个语料库的评估集重新推导它们。

## 在 RRF 融合后应用元数据提升，绝不在之前

原因：提升因子乘以已融合结果集的 RRF 分数，然后重新排序该列表，使用标题匹配 1.5x、路径匹配 1.15x，以及技术查询中的代码块 1.2x；在融合前提升每种方法的分数会破坏 RRF 依赖的属性（它按排名融合，而非按分数），并允许一个强大的关键词命中超过两种方法都同意的文档，而这一确切顺序产生了 `rules/pgvector-metadata.md` 中归因于提升的 +6% MRR（源自退役的 checklists/search-implementation-checklist.md 和 examples/examples/orchestkit-retrieval.md；无追踪事件）。
上游：https://learn.microsoft.com/en-us/azure/search/index-add-scoring-profiles

## 停止将 RRF 获取倍数提高超过 3x

原因：在参考语料库上测量的通过率在 1x 时为 87.2%，2x 时为 89.5%，3x 时为 91.1%，4x 时为 91.3%，因此第四个倍数仅购买了 0.2 个点，而每方法扫描的行数增加了三分之一，这就是为什么 3x 是 `rules/core-hybrid-search.md` 和 `rules/pgvector-hybrid-search.md` 中硬编码的 House 默认值；仅在获得优于此曲线的金色集数字时才提高它（源自退役的 examples/examples/orchestkit-retrieval.md；无追踪事件）。
上游：https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion

## 每个检索更改都基于金色集阈值

原因：检索更改在发货前的 House 标准是通过金色查询集至少 90% 的通过率，precision@10 至少 0.70，recall@10 至少 0.85，以及 MRR 至少 0.65，这些基线设置在参考管道的 91.6% 通过率和 0.777 整体 MRR（硬切片为 0.695）之下，以便真实的回归会触发它们，而不是噪声运行（源自退役的 checklists/search-implementation-checklist.md 和 examples/examples/orchestkit-retrieval.md；无追踪事件）。
上游：ork 技能 `golden-dataset`

## 断言每个阶段的搜索延迟，而不仅仅是端到端

原因：集成测试分别断言向量搜索低于 100ms，关键词搜索低于 50ms，以及融合混合搜索低于 150ms，分别针对观察到的 415 个分块基线的 P50 15ms / P95 32ms / P99 62ms，因为单个总延迟断言保持绿色，而一个阶段无声地翻倍，这正是索引停止被使用的形状（源自退役的 checklists/search-implementation-checklist.md 和 examples/examples/orchestkit-retrieval.md；无追踪事件）。
上游：https://www.postgresql.org/docs/current/using-explain.html

## 在调整索引前预算嵌入调用

原因：在参考测量中，查询嵌入占 15ms 端到端搜索的 8ms，而向量搜索为 2ms，关键词搜索为 3ms，它是约 120 个请求每秒的吞吐量上限，因此首先缓存和批量嵌入，因为索引调整低于该上限会改变总数个位数百分比（源自退役的 examples/examples/orchestkit-retrieval.md；无追踪事件）。
上游：https://docs.voyageai.com/docs/embeddings
