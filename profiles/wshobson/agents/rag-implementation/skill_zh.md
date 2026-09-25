# RAG 实现

掌握检索增强生成（RAG）技术，以构建使用外部知识库提供准确、可靠响应的大型语言模型（LLM）应用程序。

## 何时使用此技能

- 构建基于专有文档的问答系统
- 创建具有实时、事实性信息的聊天机器人
- 实现基于自然语言查询的语义搜索
- 通过可靠响应减少幻觉现象
- 使 LLM 能够访问特定领域的知识
- 构建文档助手
- 创建带有来源引用的研究工具

## 核心组件

### 1. 向量数据库

**目的**：高效存储和检索文档嵌入

**选项**：

- **Pinecone**：托管式、可扩展、无服务器
- **Weaviate**：开源、混合搜索、GraphQL
- **Milvus**：高性能、本地部署
- **Chroma**：轻量级、易于使用、本地开发
- **Qdrant**：快速、过滤搜索、基于 Rust
- **pgvector**：PostgreSQL 扩展、SQL 集成

### 2. 嵌入

**目的**：将文本转换为数值向量以进行相似度搜索

**模型（2026年）**：

| 模型          | 维度     | 适用场景         |
|--------------|----------|------------------|
| **voyage-3-large** | 1024    | Claude 应用（Anthropic 推荐） |
| **voyage-code-3**  | 1024    | 代码搜索         |
| **text-embedding-3-large** | 3072   | OpenAI 应用，高精度 |
| **text-embedding-3-small** | 1536   | OpenAI 应用，成本效益高 |
| **bge-large-en-v1.5** | 1024    | 开源，本地部署     |
| **multilingual-e5-large** | 1024    | 多语言支持       |

### 3. 检索策略

**方法**：

- **密集检索**：通过嵌入进行语义相似度匹配
- **稀疏检索**：关键词匹配（BM25、TF-IDF）
- **混合搜索**：结合密集+稀疏，加权融合
- **多查询**：生成多个查询变体
- **HyDE**：生成假设性文档以提升检索效果

### 4. 重新排序

**目的**：通过重新排序结果提升检索质量

**方法**：

- **交叉编码器**：基于 BERT 的重新排序（ms-marco-MiniLM）
- **Cohere Rerank**：基于 API 的重新排序
- **最大边际相关性（MMR）**：多样性+相关性
- **基于 LLM**：使用 LLM 评分相关性

## 使用 LangGraph 快速入门

```python
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import TypedDict, Annotated

class RAGState(TypedDict):
    question: str
    context: list[Document]
    answer: str

# 初始化组件
llm = ChatAnthropic(model="claude-sonnet-5")
embeddings = VoyageAIEmbeddings(model="voyage-3-large")
vectorstore = PineconeVectorStore(index_name="docs", embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# RAG 提示
rag_prompt = ChatPromptTemplate.from_template(
    """根据以下上下文回答。如果无法回答，请说明。

    上下文：
    {context}

    问题：{question}

    回答:"""
)

async def retrieve(state: RAGState) -> RAGState:
    """检索相关文档。"""
    docs = await retriever.ainvoke(state["question"])
    return {"context": docs}

async def generate(state: RAGState) -> RAGState:
    """根据上下文生成答案。"""
    context_text = "\n\n".join(doc.page_content for doc in state["context"])
    messages = rag_prompt.format_messages(
        context=context_text,
        question=state["question"]
    )
    response = await llm.ainvoke(messages)
    return {"answer": response.content}

# 构建 RAG 图
builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

rag_chain = builder.compile()

# 使用
result = await rag_chain.ainvoke({"question": "主要功能是什么?"})
print(result["answer"])
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请查阅该文件。
