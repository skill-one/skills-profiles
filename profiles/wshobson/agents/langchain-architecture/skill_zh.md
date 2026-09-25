# LangChain & LangGraph 架构

掌握现代 LangChain 1.x 和 LangGraph，用于构建具有代理、状态管理、记忆和工具集成的复杂 LLM 应用。

## 何时使用此技能

- 构建具有工具访问权限的自主 AI 代理
- 实现复杂的多步骤 LLM 工作流
- 管理对话记忆和状态
- 将 LLM 与外部数据源和 API 集成
- 创建模块化、可重用的 LLM 应用组件
- 实现文档处理管道
- 构建生产级 LLM 应用

## 包结构（LangChain 1.x）

```
langchain (1.2.x)         # 高级编排
langchain-core (1.2.x)    # 核心抽象（消息、提示、工具）
langchain-community       # 第三方集成
langgraph                 # 代理编排和状态管理
langchain-openai          # OpenAI 集成
langchain-anthropic       # Anthropic/Claude 集成
langchain-voyageai        # Voyage AI 嵌入
langchain-pinecone        # Pinecone 向量存储
```

## 核心概念

### 1. LangGraph 代理

LangGraph 是 2026 年构建代理的标准。它提供：

**关键特性：**

- **StateGraph**：使用类型化状态进行显式状态管理
- **持久执行**：代理在失败时保持持久
- **人工参与**：可在任何点检查和修改状态
- **记忆**：跨会话的短期和长期记忆
- **检查点**：保存和恢复代理状态

**代理模式：**

- **ReAct**：使用 `create_react_agent` 的推理 + 行动
- **计划-执行**：分离计划和执行节点
- **多代理**：在专业代理之间进行监督路由
- **工具调用**：使用 Pydantic 模式进行结构化工具调用

### 2. 状态管理

LangGraph 使用 TypedDict 进行显式状态：

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState

# 简单基于消息的状态
class AgentState(MessagesState):
    """扩展 MessagesState 以添加自定义字段。"""
    context: Annotated[list, "检索到的文档"]

# 复杂代理的自定义状态
class CustomState(TypedDict):
    messages: Annotated[list, "对话历史"]
    context: Annotated[dict, "检索到的上下文"]
    current_step: str
    results: list
```

### 3. 记忆系统

现代记忆实现：

- **ConversationBufferMemory**：存储所有消息（短对话）
- **ConversationSummaryMemory**：总结旧消息（长对话）
- **ConversationTokenBufferMemory**：基于令牌的窗口
- **VectorStoreRetrieverMemory**：语义相似度检索
- **LangGraph 检查点**：跨会话的持久状态

### 4. 文档处理

加载、转换和存储文档：

**组件：**

- **文档加载器**：从各种来源加载
- **文本分割器**：智能分割文档
- **向量存储**：存储和检索嵌入
- **检索器**：获取相关文档

### 5. 回调与跟踪

LangSmith 是可观察性的标准：

- 请求/响应日志记录
- 令牌使用跟踪
- 延迟监控
- 错误跟踪
- 跟踪可视化

## 快速入门

### 使用 LangGraph 构建 ReAct 代理

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import ast
import operator

# 初始化 LLM（推荐使用 Claude Sonnet 5）
llm = ChatAnthropic(model="claude-sonnet-5")

# 使用 Pydantic 模式定义工具
@tool
def search_database(query: str) -> str:
    """在内部数据库中搜索信息。"""
    # 你的数据库搜索逻辑
    return f"结果为: {query}"

@tool
def calculate(expression: str) -> str:
    """安全地评估数学表达式。

    支持：+，-，*，/，**，%，括号
    示例：'(2 + 3) * 4' 返回 '20'
    """
    # 使用 ast 进行安全的数学评估
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            return allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return allowed_operators[type(node.op)](operand)
        else:
            raise ValueError(f"不支持的运算: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        return str(_eval(tree.body))
    except Exception as e:
        return f"错误: {e}"

tools = [search_database, calculate]

# 创建检查点以持久化记忆
checkpointer = MemorySaver()

# 创建 ReAct 代理
agent = create_react_agent(
    llm,
    tools,
    checkpointer=checkpointer
)

# 使用线程 ID 运行代理以进行记忆
config = {"configurable": {"thread_id": "user-123"}}
result = await agent.ainvoke(
    {"messages": [("user", "搜索 Python 教程并计算 25 * 4")]},
    config=config
)
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 测试策略

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_tool_selection():
    """测试代理选择正确的工具。"""
    with patch.object(llm, 'ainvoke') as mock_llm:
        mock_llm.return_value = AsyncMock(content="使用 search_database")

        result = await agent.ainvoke({
            "messages": [("user", "搜索文档")]
        })

        # 验证工具是否被调用
        assert "search_database" in str(result)

@pytest.mark.asyncio
async def test_memory_persistence():
    """测试记忆跨调用持久化。"""
    config = {"configurable": {"thread_id": "test-thread"}}

    # 第一条消息
    await agent.ainvoke(
        {"messages": [("user", "记住：代码是 12345")]},
        config
    )

    # 第二条消息应记住
    result = await agent.ainvoke(
        {"messages": [("user", "代码是什么？")]},
        config
    )

    assert "12345" in result["messages"][-1].content
```

## 性能优化

### 1. 使用 Redis 缓存

```python
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
import redis

redis_client = redis.Redis.from_url("redis://localhost:6379")
set_llm_cache(RedisCache(redis_client))
```

### 2. 异步批量处理

```python
import asyncio
from langchain_core.documents import Document

async def process_documents(documents: list[Document]) -> list:
    """并行处理文档。"""
    tasks = [process_single(doc) for doc in documents]
    return await asyncio.gather(*tasks)

async def process_single(doc: Document) -> dict:
    """处理单个文档。"""
    chunks = text_splitter.split_documents([doc])
    embeddings = await embeddings_model.aembed_documents(
        [c.page_content for c in chunks]
    )
    return {"doc_id": doc.metadata.get("id"), "embeddings": embeddings}
```

### 3. 连接池

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# 重用 Pinecone 客户端
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("my-index")

# 使用现有索引创建向量存储
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
```
