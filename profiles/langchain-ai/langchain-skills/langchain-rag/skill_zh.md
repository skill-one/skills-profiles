<概述>
检索增强生成（RAG）通过从外部知识源获取相关上下文来增强大型语言模型（LLM）的响应。

**流程：**
1. **索引**：加载 → 分割 → 嵌入 → 存储
2. **检索**：查询 → 嵌入 → 搜索 → 返回文档
3. **生成**：文档 + 查询 → LLM → 响应

**关键组件：**
- **文档加载器**：从文件、网络、数据库中导入数据
- **文本分割器**：将文档分割成块
- **嵌入**：将文本转换为向量
- **向量存储**：存储和搜索嵌入

<vectorstore-selection>

| 向量存储 | 用例 | 持久化 |
|----------|------|--------|
| **内存中** | 测试 | 仅内存 |
| **FAISS** | 本地、高性能 | 硬盘 |
| **Chroma** | 开发 | 硬盘 |
| **Pinecone** | 生产、托管 | 云端 |

</vectorstore-selection>

---

## 完整 RAG 流程

<ex-basic-rag-setup>
<python>
端到端 RAG 流程：加载文档、分割成块、嵌入、存储、检索并生成响应。

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 1. 加载文档
docs = [
    Document(page_content="LangChain 是一个用于 LLM 应用的框架。", metadata={}),
    Document(page_content="RAG = 检索增强生成。", metadata={}),
]

# 2. 分割文档
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(docs)

# 3. 创建嵌入并存储
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore.from_documents(splits, embeddings)

# 4. 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 5. 在 RAG 中使用
model = ChatOpenAI(model="gpt-4.1")
query = "什么是 RAG？"
relevant_docs = retriever.invoke(query)

context = "\n\n".join([doc.page_content for doc in relevant_docs])
response = model.invoke([
    {"role": "system", "content": f"使用这个上下文：\n\n{context}"},
    {"role": "user", "content": query},
])
```
</python>
<typescript>
端到端 RAG 流程：加载文档、分割成块、嵌入、存储、检索并生成响应。

```typescript
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { Document } from "@langchain/core/documents";

// 1. 加载文档
const docs = [
  new Document({ pageContent: "LangChain 是一个用于 LLM 应用的框架。", metadata: {} }),
  new Document({ pageContent: "RAG = 检索增强生成。", metadata: {} }),
];

// 2. 分割文档
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 500, chunkOverlap: 50 });
const splits = await splitter.splitDocuments(docs);

// 3. 创建嵌入并存储
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorstore = await MemoryVectorStore.fromDocuments(splits, embeddings);

// 4. 创建检索器
const retriever = vectorstore.asRetriever({ k: 4 });

// 5. 在 RAG 中使用
const model = new ChatOpenAI({ model: "gpt-4.1" });
const query = "什么是 RAG？";
const relevantDocs = await retriever.invoke(query);

const context = relevantDocs.map(doc => doc.pageContent).join("\n\n");
const response = await model.invoke([
  { role: "system", content: `使用这个上下文：\n\n${context}` },
  { role: "user", content: query },
]);
```
</typescript>
</ex-basic-rag-setup>

---

## 文档加载器

<ex-loading-pdf>
<python>
加载 PDF 文件并将每一页提取为单独的文档。

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./document.pdf")
docs = loader.load()
print(f"加载了 {len(docs)} 页")
```
</python>
<typescript>
加载 PDF 文件并将每一页提取为单独的文档。

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("./document.pdf");
const docs = await loader.load();
console.log(`加载了 ${docs.length} 页`);
```
</typescript>
</ex-loading-pdf>

<ex-loading-web-pages>
<python>
从网络 URL 获取并解析内容为文档。

```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com")
docs = loader.load()
```
</python>
<typescript>
使用 Cheerio 从网络 URL 获取并解析内容为文档。

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://docs.langchain.com");
const docs = await loader.load();
```
</typescript>
</ex-loading-web-pages>

<ex-loading-directory>
<python>
使用 glob 模式从目录加载所有文本文件。

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# 从目录加载所有文本文件
loader = DirectoryLoader(
    "path/to/documents",
    glob="**/*.txt",  # 文件加载模式
    loader_cls=TextLoader
)
docs = loader.load()
```
</python>
</ex-loading-directory>

---

## 文本分割

<ex-text-splitting>
<python>
使用 RecursiveCharacterTextSplitter 将文档分割成块，可配置大小和重叠。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 每块字符数
    chunk_overlap=200,      # 上下文连续性重叠
    separators=["\n\n", "\n", " ", ""],  # 分割层级
)

splits = splitter.split_documents(docs)
```
</python>
</ex-text-splitting>

---

## 向量存储

<ex-chroma-vectorstore>
<python>
创建一个持久的 Chroma 向量存储并从磁盘重新加载它。

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db",
    collection_name="my-collection",
)

# 加载现有
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(),
    collection_name="my-collection",
)
```
<typescript>
创建一个连接到正在运行的 Chroma 服务器的 Chroma 向量存储。

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorstore = await Chroma.fromDocuments(
  splits,
  new OpenAIEmbeddings(),
  { collectionName: "my-collection", url: "http://localhost:8000" }
);
```
</typescript>
</ex-chroma-vectorstore>

<ex-faiss-vectorstore>
<python>
创建一个 FAISS 向量存储，保存到磁盘，并重新加载它。

```python
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(splits, embeddings)
vectorstore.save_local("./faiss_index")

# 仅加载你创建并完全控制的 FAISS 索引。
# Python FAISS 加载器使用基于 pickle 的元数据，因此永远不要加载
# 下载的、共享的或任何其他不受信任的索引目录。
loaded = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True,
)
```
<typescript>
创建一个 FAISS 向量存储，保存到磁盘，并重新加载它。

```typescript
import { FaissStore } from "@langchain/community/vectorstores/faiss";

const vectorstore = await FaissStore.fromDocuments(splits, embeddings);
await vectorstore.save("./faiss_index");

const loaded = await FaissStore.load("./faiss_index", embeddings);
```
</typescript>
</ex-faiss-vectorstore>

---

## 检索

<ex-similarity-search>
<python>
执行相似度搜索并检索带相关度分数的结果。

```python
# 基本搜索
results = vectorstore.similarity_search(query, k=5)

# 带分数
results_with_score = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results_with_score:
    print(f"分数: {score}, 内容: {doc.page_content}")
```
<typescript>
执行相似度搜索并检索带相关度分数的结果。

```typescript
// 基本搜索
const results = await vectorstore.similaritySearch(query, 5);

// 带分数
const resultsWithScore = await vectorstore.similaritySearchWithScore(query, 5);
for (const [doc, score] of resultsWithScore) {
  console.log(`分数: ${score}, 内容: ${doc.pageContent}`);
}
```
</typescript>
</ex-similarity-search>

<ex-mmr-search>
<python>
使用 MMR（最大边际相关性）平衡搜索结果的相关性和多样性。

```python
# MMR 平衡相关性和多样性
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```
</python>
</ex-mmr-search>

<ex-metadata-filtering>
<python>
为文档添加元数据并按元数据属性过滤搜索结果。

```python
# 创建文档时添加元数据
docs = [
    Document(
        page_content="Python 编程指南",
        metadata={"语言": "python", "主题": "编程"}
    ),
]

# 带过滤搜索
results = vectorstore.similarity_search(
    "编程",
    k=5,
    filter={"语言": "python"}  # 仅 Python 文档
)
```
</python>
</ex-metadata-filtering>

<ex-rag-with-agent>
<python>
创建一个使用 RAG 作为工具来回答问题的代理。

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_docs(query: str) -> str:
    """搜索文档以获取相关信息。"""
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

agent = create_agent(
    model="gpt-4.1",
    tools=[search_docs],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "如何创建一个代理？"}]
})
```
<typescript>
创建一个使用 RAG 作为工具来回答问题的代理。

```typescript
import { createAgent } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const searchDocs = tool(
  async (input) => {
    const docs = await retriever.invoke(input.query);
    return docs.map(d => d.pageContent).join("\n\n");
  },
  {
    name: "search_docs",
    description: "搜索文档以获取相关信息。",
    schema: z.object({ query: z.string() }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchDocs],
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "如何创建一个代理？"}],
});
```
</typescript>
</ex-rag-with-agent>

<boundaries>
### 你可以配置的

- 块大小/重叠
- 嵌入模型
- 结果数量（k）
- 元数据过滤器
- 搜索算法：相似度、MMR

### 你不能配置的

- 嵌入维度（每个模型）
- 在同一存储中混合来自不同模型的嵌入
</boundaries>

<fix-chunk-size>
<python>
块大小 500-1500 通常很好。

```python
# 错误：太小（丢失上下文）或太大（超出限制）
splitter = RecursiveCharacterTextSplitter(chunk_size=50)
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# 正确
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```
</python>
<typescript>
块大小 500-1500 通常很好。

```typescript
// 错误：太小或太大
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 50 });

// 正确
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
```
</typescript>
</fix-chunk-size>

<fix-chunk-overlap>
<python>
使用重叠（块大小的 10-20%）以在边界处保持上下文。

```python
# 错误：无重叠 - 边界处上下文断裂
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# 正确：10-20% 重叠
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```
</python>
</fix-chunk-overlap>

<fix-persist-vectorstore>
<python>
使用持久化向量存储而不是内存存储以避免数据丢失。

```python
# 错误：内存中 - 重启时丢失
vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)

# 正确
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
```
<typescript>
使用持久化向量存储而不是内存存储以避免数据丢失。

```typescript
// 错误：内存中 - 重启时丢失
const vectorstore = await MemoryVectorStore.fromDocuments(docs, embeddings);

// 正确
const vectorstore = await Chroma.fromDocuments(docs, embeddings, { collectionName: "my-collection" });
```
</typescript>
</fix-persist-vectorstore>

<fix-consistent-embeddings>
<python>
使用相同的嵌入模型进行索引和查询。

```python
# 错误：索引和查询使用不同的嵌入 - 兼容性差！
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))
retriever = vectorstore.as_retriever(embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))

# 正确：相同模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()  # 使用相同的嵌入
```
<typescript>
使用相同的嵌入模型进行索引和查询。

```typescript
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorstore = await Chroma.fromDocuments(docs, embeddings);
const retriever = vectorstore.asRetriever();  // 使用相同的嵌入
```
</typescript>
</fix-consistent-embeddings>

<fix-faiss-deserialization>
<python>
仅对受信任的本地索引选择启用 FAISS 反序列化。Python FAISS 索引包括基于 pickle 的元数据，不受信任的 pickle 文件在加载期间可以执行任意代码。

```python
# 错误：加载下载的、共享的、云端托管或第三方控制的
# FAISS 索引，启用危险反序列化。
loaded_store = FAISS.load_local(
    "./untrusted_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True,
)

# 正确：仅在索引目录由你创建且始终处于你控制下时选择启用。
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True,
)
```

如果你无法保证持久化索引的来源，不要使用 `allow_dangerous_deserialization=True` 加载它。从可信源文档重新构建索引，或使用不需要对不受信任文件进行 pickle 反序列化的向量存储/后端。
</python>
</fix-faiss-deserialization>

<fix-dimension-mismatch>
<python>
确保嵌入维度与向量存储索引维度匹配。

```python
# 错误：索引有 1536 维度，但使用 512 维嵌入
pc.create_index(name="idx", dimension=1536, metric="cosine")
vectorstore = PineconeVectorStore.from_documents(
    docs, OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512), index=pc.Index("idx")
)  # 错误：维度不匹配！

# 正确：匹配维度
embeddings = OpenAIEmbeddings()  # 默认 1536
```
</python>
</fix-dimension-mismatch>
