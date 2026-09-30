---
name: langchain-dependencies
description: 在使用新项目时或当被询问关于 LangChain、LangGraph、LangSmith 或 Deep Agents 的包版本、安装或依赖管理时，请调用此技能。涵盖所需包、最低版本、环境要求、版本管理最佳实践以及 Python 和 TypeScript 的常见社区工具包。
---

<概述>
LangChain 生态系统由多个专注且独立版本控制的包组成。了解您需要哪些包——以及它们的版本约束——可以防止不兼容问题，并使升级过程可预测。

**关键原则：**
- **LangChain 1.0 是当前的长支持（LTS）版本。** 始终在 1.0+ 上启动新项目。LangChain 0.3 仅用于遗留维护——不要用它来开发新工作。
- **langchain-core** 是共享基础：始终与其他任何包一起显式安装它。
- **langchain-community**（仅限 Python）**不遵循语义版本控制；保守地固定它。**
- **LangGraph 与 Deep Agents：** 根据您的用例选择一种编排方法——它们是替代品，而不是必需的堆栈（见下文[框架选择](#框架选择)）。
- 提供商集成（模型、向量存储、工具）是单独安装的，这样您只会拉入您使用的部分。

</概述>

---

## 环境要求

<环境要求>

| 要求 | Python | TypeScript / Node |
|------|--------|-------------------|
| 运行时最低要求 | **Python 3.10+** | **Node.js 20+** |
| LangChain | **1.0+ (LTS)** | **1.0+ (LTS)** |
| LangSmith SDK | >= 0.3.0 | >= 0.3.0 |

</环境要求>

---

## 框架选择

<框架选择>
选择**一个**代理编排层。您不需要两者都使用。

| 框架 | 使用场景 | 核心额外包 |
|------|----------|------------|
| **LangGraph** | 需要细粒度图控制、自定义工作流、循环或分支 | `langgraph` / `@langchain/langgraph` |
| **Deep Agents** | 想要开箱即用的规划、内存、文件上下文和技能 | `deepagents` (依赖于 LangGraph；作为传递依赖项安装) |

两者都建立在 `langchain` + `langchain-core` + `langsmith` 之上。
</框架选择>

---

## 核心包

<python包>

### Python — 始终需要

| 包 | 角色 | 最低版本 |
|----|------|----------|
| `langchain` | 代理、链、检索 | 1.0 |
| `langchain-core` | 基本类型和接口（同级依赖） | 1.0 |
| `langsmith` | 跟踪、评估、数据集 | 0.3.0 |

### Python — 编排（选择一个）

| 包 | 使用场景 | 最低版本 |
|----|----------|----------|
| `langgraph` | 直接构建自定义图 | 1.0 |
| `deepagents` | 使用 Deep Agents 框架 | 最新 |

### Python — 模型提供者（选择您使用的那个）

| 包 | 提供商 |
|----|--------|
| `langchain-openai` | OpenAI (GPT-4o, o3, …) |
| `langchain-anthropic` | Anthropic (Claude) |
| `langchain-google-genai` | Google (Gemini) |
| `langchain-mistralai` | Mistral |
| `langchain-groq` | Groq (快速推理) |
| `langchain-cohere` | Cohere |
| `langchain-fireworks` | Fireworks AI |
| `langchain-together` | Together AI |
| `langchain-huggingface` | Hugging Face Hub |
| `langchain-ollama` | Ollama (本地模型) |
| `langchain-aws` | AWS Bedrock |
| `langchain-azure-ai` | Azure AI Foundry |

### Python — 常用工具和检索包

这些包具有更严格的兼容性要求——除非您有特定原因，否则请使用最新可用版本。

| 包 | 添加 | 备注 |
|----|------|------|
| `langchain-tavily` | Tavily 网络搜索 (`TavilySearch`) | 专用集成包；优先使用最新版本 |
| `langchain-text-splitters` | 文本分块工具 | 语义版本，保持当前 |
| `langchain-community` | 1000+ 集成（备用） | **不遵循语义版本——固定到次版本系列** |
| `faiss-cpu` | FAISS 向量存储（本地） | 通过 `langchain-community` 提供；使用最新版本 |
| `langchain-chroma` | Chroma 向量存储 | 专用集成包；优先使用最新版本 |
| `langchain-pinecone` | Pinecone 向量存储 | 专用集成包；优先使用最新版本 |
| `langchain-qdrant` | Qdrant 向量存储 | 专用集成包；优先使用最新版本 |
| `langchain-weaviate` | Weaviate 向量存储 | 专用集成包；优先使用最新版本 |
| `langsmith[pytest]` | LangSmith 的 pytest 插件 | 需要 langsmith >= 0.3.4 |

> **langchain-community 稳定性说明：** 此包**不遵循语义版本控制。** 次版本更新可能包含破坏性变更。当存在专用集成包时（例如 `langchain-chroma`、`langchain-tavily`），优先使用它们——它们是独立版本控制的，更稳定。

</python包>

<typescript包>

### TypeScript — 始终需要

| 包 | 角色 | 最低版本 |
|----|------|----------|
| `@langchain/core` | 基本类型和接口（同级依赖） | 1.0 |
| `langchain` | 代理、链、检索 | 1.0 |
| `langsmith` | 跟踪、评估、数据集 | 0.3.0 |

### TypeScript — 编排（选择一个）

| 包 | 使用场景 | 最低版本 |
|----|----------|----------|
| `@langchain/langgraph` | 直接构建自定义图 | 1.0 |
| `deepagents` | 使用 Deep Agents 框架 | 最新 |

### TypeScript — 模型提供者（选择您使用的那个）

| 包 | 提供商 |
|----|--------|
| `@langchain/openai` | OpenAI (GPT-4o, o3, …) |
| `@langchain/anthropic` | Anthropic (Claude) |
| `@langchain/google-genai` | Google (Gemini) |
| `@langchain/mistralai` | Mistral |
| `@langchain/groq` | Groq (快速推理) |
| `@langchain/cohere` | Cohere |
| `@langchain/aws` | AWS Bedrock |
| `@langchain/azure-openai` | Azure OpenAI |
| `@langchain/ollama` | Ollama (本地模型) |

### TypeScript — 常用工具和检索包

| 包 | 添加 | 备注 |
|----|------|------|
| `@langchain/tavily` | Tavily 网络搜索 (`TavilySearch`) | 专用集成包；优先使用最新版本 |
| `@langchain/community` | 广泛的社区集成 | 谨慎使用；优先使用专用包 |
| `@langchain/pinecone` | Pinecone 向量存储 | 专用集成包；优先使用最新版本 |
| `@langchain/qdrant` | Qdrant 向量存储 | 专用集成包；优先使用最新版本 |
| `@langchain/weaviate` | Weaviate 向量存储 | 专用集成包；优先使用最新版本 |

> **`@langchain/core` 必须显式安装** 在 yarn 工作区和多包项目中——它是一个同级依赖项，不会总是自动提升。

</typescript包>

---

## 最小项目模板

<ex-langgraph-python>
<python>
LangGraph 项目的最小依赖集（与提供者无关）。

```
# requirements.txt
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langgraph>=1.0,<2.0
langsmith>=0.3.0

# 添加您的模型提供者，例如：
# langchain-openai
# langchain-anthropic
# langchain-google-genai
```
</python>
</ex-langgraph-python>

<ex-langgraph-typescript>
<typescript>
LangGraph 项目的最小 package.json 依赖（与提供者无关）。

```json
{
  "dependencies": {
    "@langchain/core": "^1.0.0",
    "langchain": "^1.0.0",
    "@langchain/langgraph": "^1.0.0",
    "langsmith": "^0.3.0"
  }
}
```
</typescript>
</ex-langgraph-typescript>

<ex-deepagents-python>
<python>
Deep Agents 项目的最小依赖集（与提供者无关）。

```
# requirements.txt
deepagents            # 内部捆绑 langgraph
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langsmith>=0.3.0

# 添加您的模型提供者，例如：
# langchain-anthropic
# langchain-openai
```
</python>
</ex-deepagents-python>

<ex-deepagents-typescript>
<typescript>
Deep Agents 项目的最小 package.json 依赖（与提供者无关）。

```json
{
  "dependencies": {
    "deepagents": "latest",
    "@langchain/core": "^1.0.0",
    "langchain": "^1.0.0",
    "langsmith": "^0.3.0"
  }
}
```
</typescript>
</ex-deepagents-typescript>

<ex-with-tools-python>
<python>
在 LangGraph 项目中添加 Tavily 搜索和向量存储。

```
# requirements.txt
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langgraph>=1.0,<2.0
langsmith>=0.3.0

# 网络搜索
langchain-tavily          # 使用最新版本；合作伙伴包，语义版本

# 向量存储——选择一个：
langchain-chroma          # 使用最新版本；合作伙伴包，语义版本
# langchain-pinecone      # 使用最新版本；合作伙伴包，语义版本
# langchain-qdrant        # 使用最新版本；合作伙伴包，语义版本

# 文本处理
langchain-text-splitters  # 使用最新版本；语义版本

# 您的模型提供者：
# langchain-openai / langchain-anthropic / 等。
```
</python>
</ex-with-tools-python>

<ex-with-tools-typescript>
<typescript>
在 LangGraph 项目中添加 Tavily 搜索和向量存储。

```json
{
  "dependencies": {
    "@langchain/core": "^1.0.0",
    "langchain": "^1.0.0",
    "@langchain/langgraph": "^1.0.0",
    "langsmith": "^0.3.0",
    "@langchain/tavily": "latest",
    "@langchain/pinecone": "latest"
  }
}
```
</typescript>
</ex-with-tools-typescript>

---

## 版本控制策略与升级策略

<版本控制策略>

| 包组 | 版本控制 | 安全升级策略 |
|------|----------|--------------|
| `langchain`, `langchain-core` | 严格语义版本（1.0 LTS） | 允许次版本：`>=1.0,<2.0` |
| `langgraph` / `@langchain/langgraph` | 严格语义版本（v1 LTS） | 允许次版本：`>=1.0,<2.0` |
| `langsmith` | 严格语义版本 | 允许次版本：`>=0.3.0` |
| 专用集成包（例如 `langchain-tavily`, `langchain-chroma`） | 独立版本控制 | 允许次版本更新；使用最新版本 |
| `langchain-community` | **不遵循语义版本** | 固定精确次版本：`>=0.4.0,<0.5.0` |
| `deepagents` | 跟随项目发布 | 在生产中固定已测试版本 |

**所有语义版本控制包仅在主版本（1.x → 2.x）中发生破坏性变更。** 已弃用的功能在整个 1.x 系列中保持功能，并会发出警告。

**优先使用专用集成包而不是 langchain-community。** 当存在专用包时（例如 `langchain-chroma` 而不是 `langchain-community` 的 Chroma 集成），请使用它——专用包是独立版本控制的，经过更好的测试。

**社区工具包（Tavily、向量存储等）应保持在最新状态** 除非您的项目需要锁定环境。这些包经常与 LangChain/LangGraph 更新一起发布兼容性修复。

</版本控制策略>

---

## 环境变量

<环境变量>
所有键都在运行时从环境中读取。仅设置您实际使用的服务的键。

```bash
# LangSmith（始终推荐用于可观察性）
LANGSMITH_API_KEY=<your-key>
LANGSMITH_PROJECT=<project-name>   # 可选，默认为 "default"

# 模型提供者——设置您使用的那个
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
MISTRAL_API_KEY=<your-key>
GROQ_API_KEY=<your-key>
COHERE_API_KEY=<your-key>
FIREWORKS_API_KEY=<your-key>
TOGETHER_API_KEY=<your-key>
HUGGINGFACEHUB_API_TOKEN=<your-key>

# 常用工具/检索服务
TAVILY_API_KEY=<your-key>          # 用于 Tavily 搜索
PINECONE_API_KEY=<your-key>        # 用于 Pinecone
```
</环境变量>

---

## 常见错误

<fix-legacy-version>
永远不要在 LangChain 0.3 上启动新项目。它仅用于维护，直到 2026 年 12 月。

```
# 错误：遗留，没有新功能，仅安全补丁
langchain>=0.3,<0.4

# 正确：LangChain 1.0 LTS
langchain>=1.0,<2.0
```
</fix-legacy-version>

<fix-community-unpinned>
`langchain-community` 在次版本升级时可能会中断——它不遵循语义版本控制。

```
# 错误：允许次版本升级，可能存在破坏
langchain-community>=0.4

# 正确：固定精确次版本系列
langchain-community>=0.4.0,<0.5.0
```
如果存在等效的专用集成包，请考虑切换（例如 `langchain-chroma` 而不是社区 Chroma 集成）。
</fix-community-unpinned>

<fix-community-tool-outdated>
像 `langchain-tavily` 和向量存储集成的社区工具包会与 LangChain 更新一起发布兼容性修复。使用过时的固定版本可能会导致导入错误或损坏的工具模式。

```
# 有风险：旧版本可能与 LangChain 1.0 不兼容
langchain-tavily==0.0.1

# 更好：允许当前主版本内的最新版本
langchain-tavily>=0.1
```
</fix-community-tool-outdated>

<fix-community-import-deprecated>
许多以前位于 `langchain-community` 中的工具现在有专用包，并具有更新的导入路径。始终优先使用专用包的导入。

```python
# 错误——已弃用的社区导入路径
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import Pinecone

# 正确——使用专用包导入
from langchain_tavily import TavilySearch                  # pip: langchain-tavily (TavilySearchResults 已弃用)
from langchain_community.tools import WikipediaQueryRun  # 尚无专用包
from langchain_chroma import Chroma                       # pip: langchain-chroma
from langchain_pinecone import PineconeVectorStore        # pip: langchain-pinecone
```

要查找任何集成的当前规范导入，请搜索集成目录：
https://python.langchain.com/docs/integrations/tools/

每个条目显示正确的包和导入路径。如果存在专用包，请使用它——社区路径可能仍然工作，但被视为遗留。
</fix-community-import-deprecated>

<fix-core-not-installed>
<typescript>
`@langchain/core` 是一个同级依赖项——它必须在您的 package.json 中，尤其是在多包项目中。

```json
// 错误：缺少 @langchain/core（在 yarn 工作区/严格提升时会导致问题）
{
  "dependencies": {
    "@langchain/langgraph": "^1.0.0"
  }
}

// 正确：始终显式列出 @langchain/core
{
  "dependencies": {
    "@langchain/core": "^1.0.0",
    "@langchain/langgraph": "^1.0.0"
  }
}
```
</typescript>
</fix-core-not-installed>

<fix-python-version>
<python>
Python 3.9 及以下版本不受 LangChain 1.0 支持。

```python
# 安装前验证
import sys
assert sys.version_info >= (3, 10), "Python 3.10+ required for LangChain 1.0"
```
</python>
</fix-python-version>

<fix-node-version>
<typescript>
Node.js 低于 20 版本不受官方支持。

```bash
# 安装前验证
node --version   # 必须是 v20.x 或更高版本
```
</typescript>
</fix-node-version>
