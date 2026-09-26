# MiroFish-Offline 技能

> 由 [ara.so](https://ara.so) 开发的技能 — 2026 每日技能集合。

MiroFish-Offline 是一个完全本地的多智能体群智能引擎。给它任何文档（新闻稿、政策草案、财务报告），它都会生成数百个具有独特个性的 AI 智能体，模拟社交媒体上的公众反应——帖子、争论、观点转变——每小时更新一次。无需云 API：Neo4j CE 5.15 处理图内存，Ollama 提供大型语言模型服务。

---

## 架构概述

```
文档输入
     │
     ▼
图构建（通过 Ollama 大型语言模型进行命名实体识别和关系提取）
     │
     ▼
Neo4j 知识图谱（实体、关系、通过 nomic-embed-text 生成的嵌入）
     │
     ▼
环境设置（生成数百个具有个性化和记忆的智能体角色）
     │
     ▼
模拟（智能体在模拟平台上发布帖子、回复、争论、改变观点）
     │
     ▼
报告（ReportAgent 访谈焦点小组、查询图、生成分析报告）
     │
     ▼
交互（与任何单个智能体聊天，完整记忆持久化）
```

**后端**：Flask + Python 3.11  
**前端**：Vue 3 + Node 18  
**图数据库**：Neo4j CE 5.15（bolt 协议）  
**大型语言模型**：Ollama（兼容 OpenAI 的 `/v1` 端点）  
**嵌入**：`nomic-embed-text`（768 维度，通过 Ollama）  
**搜索**：混合——0.7 × 向量相似度 + 0.3 × BM25

---

## 安装

### 选项 A：Docker（推荐）

```bash
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline
cp .env.example .env

# 启动 Neo4j + Ollama + MiroFish 后端 + 前端
docker compose up -d

# 将所需的模型拉取到 Ollama 容器中
docker exec mirofish-ollama ollama pull qwen2.5:32b
docker exec mirofish-ollama ollama pull nomic-embed-text

# 检查所有服务是否健康
docker compose ps
```

打开 `http://localhost:3000`。

### 选项 B：手动安装

**1. Neo4j**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mirofish \
  neo4j:5.15-community
```

**2. Ollama**
```bash
ollama serve &
ollama pull qwen2.5:32b       # 主要大型语言模型（约 20GB，需要 24GB 显存）
ollama pull qwen2.5:14b       # 较轻量级选项（约 10GB 显存）
ollama pull nomic-embed-text  # 嵌入（小，快速）
```

**3. 后端**
```bash
cp .env.example .env
# 编辑 .env（见配置部分）

cd backend
pip install -r requirements.txt
python run.py
# 后端在 http://localhost:5000 上启动
```

**4. 前端**
```bash
cd frontend
npm install
npm run dev
# 前端在 http://localhost:3000 上启动
```

---

## 配置（`.env`）

```bash
# ── 大型语言模型（Ollama 兼容 OpenAI 端点） ──────────────────────────
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:32b

# ── Neo4j ─────────────────────────────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# ── 嵌入（Ollama） ───────────────────────────────────────────────
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434

# ── 可选：用任何 OpenAI 兼容提供者替换 Ollama ─────────
# LLM_API_KEY=$OPENAI_API_KEY
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL_NAME=gpt-4o
```

---

## 核心Python API

### GraphStorage 接口

MiroFish 和图数据库之间的抽象层：

```python
from backend.storage.base import GraphStorage
from backend.storage.neo4j_storage import Neo4jStorage

# 初始化存储（通常通过 Flask app.extensions 完成）
storage = Neo4jStorage(
    uri=os.environ["NEO4J_URI"],
    user=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    embedding_model=os.environ["EMBEDDING_MODEL"],
    embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
    llm_base_url=os.environ["LLM_BASE_URL"],
    llm_api_key=os.environ["LLM_API_KEY"],
    llm_model=os.environ["LLM_MODEL_NAME"],
)
```

### 从文档构建知识图谱

```python
from backend.services.graph_builder import GraphBuilder

builder = GraphBuilder(storage=storage)

# 输入文档字符串
with open("press_release.txt", "r") as f:
    document_text = f.read()

# 提取实体 + 关系，存储在 Neo4j 中
graph_id = builder.build(
    content=document_text,
    title="Q4 财报报告",
    source_type="financial_report",
)

print(f"构建的图谱：{graph_id}")
# 返回用于后续模拟运行的 graph_id
```

### 创建和运行模拟

```python
from backend.services.simulation import SimulationService

sim = SimulationService(storage=storage)

# 从现有图谱创建模拟环境
sim_id = sim.create_environment(
    graph_id=graph_id,
    agent_count=200,           # 生成智能体的数量
    simulation_hours=24,       # 模拟时间跨度
    platform="twitter",        # "twitter" | "reddit" | "weibo"
)

# 运行模拟（阻塞式 — 生产环境使用异步包装器）
result = sim.run(sim_id=sim_id)

print(f"模拟完成。生成的帖子：{result['post_count']}")
print(f"情绪轨迹：{result['sentiment_over_time']}")
```

### 查询模拟结果

```python
from backend.services.report import ReportAgent

report_agent = ReportAgent(storage=storage)

# 生成结构化分析报告
report = report_agent.generate(
    sim_id=sim_id,
    focus_group_size=10,    # 访谈的智能体数量
    include_graph_search=True,
)

print(report["summary"])
print(report["关键叙事"])
print(report["情绪变化"])
print(report["有影响力的智能体"])
```

### 与模拟智能体聊天

```python
from backend.services.agent_chat import AgentChatService

chat = AgentChatService(storage=storage)

# 列出已完成模拟的智能体
agents = chat.list_agents(sim_id=sim_id, limit=10)
agent_id = agents[0]["id"]

print(f"与 {agents[0]['persona']['name']} 聊天")
print(f"个性：{agents[0]['persona']['traits']}")

# 发送消息 — 智能体以角色扮演方式回复，并使用完整记忆
response = chat.send(
    agent_id=agent_id,
    message="你为什么发布了对财报的批评？",
)

print(response["reply"])
# → 智能体使用其个性、观点偏见和帖子历史进行回复
```

### 知识图谱的混合搜索

```python
from backend.services.search import SearchService

search = SearchService(storage=storage)

# 混合搜索：0.7 * 向量相似度 + 0.3 * BM25
results = search.query(
    text="执行董事薪酬争议",
    graph_id=graph_id,
    top_k=5,
    vector_weight=0.7,
    bm25_weight=0.3,
)

for r in results:
    print(r["entity"], r["relationship"], r["score"])
```

### 实现自定义 GraphStorage 后端

```python
from backend.storage.base import GraphStorage
from typing import List, Dict, Any

class MyCustomStorage(GraphStorage):
    """
    通过实现此接口，用任何图数据库替换 Neo4j。
    通过 Flask app.extensions['neo4j_storage'] = MyCustomStorage(...) 注册。
    """

    def store_entity(self, entity: Dict[str, Any]) -> str:
        # 存储实体，返回 entity_id
        raise NotImplementedError

    def store_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Dict[str, Any],
    ) -> str:
        raise NotImplementedError

    def vector_search(
        self, embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def keyword_search(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_agent_memory(self, agent_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def update_agent_memory(
        self, agent_id: str, memory_update: Dict[str, Any]
    ) -> None:
        raise NotImplementedError
```

### Flask 应用集成模式

```python
# backend/app.py — 通过依赖注入如何连接存储
from flask import Flask
from backend.storage.neo4j_storage import Neo4jStorage
import os

def create_app():
    app = Flask(__name__)

    # 单个存储实例，通过 app.extensions 注入到所有地方
    storage = Neo4jStorage(
        uri=os.environ["NEO4J_URI"],
        user=os.environ["NEO4J_USER"],
        password=os.environ["NEO4J_PASSWORD"],
        embedding_model=os.environ["EMBEDDING_MODEL"],
        embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
        llm_base_url=os.environ["LLM_BASE_URL"],
        llm_api_key=os.environ["LLM_API_KEY"],
        llm_model=os.environ["LLM_MODEL_NAME"],
    )
    app.extensions["neo4j_storage"] = storage

    from backend.routes import graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(report_bp)

    return app
```

### 在 Flask 路由中访问存储

```python
from flask import Blueprint, current_app, request, jsonify

simulation_bp = Blueprint("simulation", __name__)

@simulation_bp.route("/api/simulation/run", methods=["POST"])
def run_simulation():
    storage = current_app.extensions["neo4j_storage"]
    data = request.json

    sim = SimulationService(storage=storage)
    sim_id = sim.create_environment(
        graph_id=data["graph_id"],
        agent_count=data.get("agent_count", 200),
        simulation_hours=data.get("simulation_hours", 24),
    )
    result = sim.run(sim_id=sim_id)
    return jsonify(result)
```

---

## REST API 参考

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| `POST` | `/api/graph/build` | 上传文档，构建知识图谱 |
| `GET` | `/api/graph/:id` | 获取图谱实体和关系 |
| `POST` | `/api/simulation/create` | 创建模拟环境 |
| `POST` | `/api/simulation/run` | 执行模拟 |
| `GET` | `/api/simulation/:id/results` | 获取帖子、情绪、指标 |
| `GET` | `/api/simulation/:id/agents` | 列出生成的智能体 |
| `POST` | `/api/report/generate` | 生成 ReportAgent 分析 |
| `POST` | `/api/agent/:id/chat` | 与特定智能体聊天 |
| `GET` | `/api/search` | 混合搜索知识图谱 |

**示例：从文档构建图谱**
```bash
curl -X POST http://localhost:5000/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Acme Corp 宣布 Q4 财报创纪录，CFO 辞职...",
    "title": "Q4 新闻稿",
    "source_type": "press_release"
  }'
# → {"graph_id": "g_abc123", "entities": 47, "relationships": 89}
```

**示例：运行模拟**
```bash
curl -X POST http://localhost:5000/api/simulation/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "g_abc123",
    "agent_count": 150,
    "simulation_hours": 12,
    "platform": "twitter"
  }'
# → {"sim_id": "s_xyz789", "status": "running"}
```

---

## 硬件选择指南

| 用例 | 模型 | 显存 | 内存 |
|----------|-------|------|-----|
| 快速测试 / 开发 | `qwen2.5:7b` | 6 GB | 16 GB |
| 平衡质量 | `qwen2.5:14b` | 10 GB | 16 GB |
| 生产质量 | `qwen2.5:32b` | 24 GB | 32 GB |
| 仅 CPU（慢） | `qwen2.5:7b` | None | 16 GB |

通过编辑 `.env` 切换模型：
```bash
LLM_MODEL_NAME=qwen2.5:14b
```
然后重启后端——无需其他更改。

---

## 常见模式

### PR 危机测试流程

```python
import os
from backend.storage.neo4j_storage import Neo4jStorage
from backend.services.graph_builder import GraphBuilder
from backend.services.simulation import SimulationService
from backend.services.report import ReportAgent

storage = Neo4jStorage(
    uri=os.environ["NEO4J_URI"],
    user=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    embedding_model=os.environ["EMBEDDING_MODEL"],
    embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
    llm_base_url=os.environ["LLM_BASE_URL"],
    llm_api_key=os.environ["LLM_API_KEY"],
    llm_model=os.environ["LLM_MODEL_NAME"],
)

def test_press_release(text: str) -> dict:
    # 1. 构建知识图谱
    builder = GraphBuilder(storage=storage)
    graph_id = builder.build(content=text, title="草稿 PR", source_type="press_release")

    # 2. 模拟公众反应
    sim = SimulationService(storage=storage)
    sim_id = sim.create_environment(graph_id=graph_id, agent_count=300, simulation_hours=48)
    sim.run(sim_id=sim_id)

    # 3. 生成报告
    report = ReportAgent(storage=storage).generate(sim_id=sim_id, focus_group_size=15)

    return {
        "情绪峰值": report["sentiment_over_time"][0],
        "关键叙事": report["key_narratives"],
        "风险评分": report["risk_score"],
        "建议修改": report["recommendations"],
    }

# 使用
with open("draft_announcement.txt") as f:
    result = test_press_release(f.read())

print(f"风险评分：{result['risk_score']}/10")
print(f"顶级叙事：{result['key_narratives'][0]}")
```

### 使用任何 OpenAI 兼容提供者

```bash
# Claude 通过 Anthropic（或任何代理）
LLM_API_KEY=$ANTHROPIC_API_KEY
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL_NAME=claude-3-5-sonnet-20241022

# OpenAI
LLM_API_KEY=$OPENAI_API_KEY
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o

# 本地 LM Studio
LLM_API_KEY=lm-studio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=your-loaded-model
```

---

## 故障排除

### Neo4j 连接被拒绝
```bash
# 检查 Neo4j 是否运行
docker ps | grep neo4j
# 检查 bolt 端口
nc -zv localhost 7687
# 查看 Neo4j 日志
docker logs neo4j --tail 50
```

### Ollama 模型未找到
```bash
# 列出可用模型
ollama list
# 拉取缺失模型
ollama pull qwen2.5:32b
ollama pull nomic-embed-text
# 检查 Ollama 是否正在服务
curl http://localhost:11434/api/tags
```

### 显存不足
```bash
# 在 .env 中切换到较小模型
LLM_MODEL_NAME=qwen2.5:14b   # 或 qwen2.5:7b
# 重启后端
cd backend && python run.py
```

### 嵌入维度不匹配
```bash
# nomic-embed-text 生成 768 维向量
# 如果你切换嵌入模型，删除并重新创建 Neo4j 向量索引：
# 在 Neo4j 浏览器（http://localhost:7474）：
# DROP INDEX entity_embedding IF EXISTS;
# 然后重启 MiroFish — 它会以正确的维度重新创建索引。
```

### Docker Compose：Ollama 容器无法访问 GPU
```yaml
# docker-compose.yml — 添加 GPU 保留：
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### CPU 上模拟缓慢
- 使用 `qwen2.5:7b` 进行更快（质量较低）的推理
- 将 `agent_count` 减少到 50–100 进行测试
- 将 `simulation_hours` 减少到 6–12
- CPU 推理使用 7b 模型：预期 ~5–10 tokens/sec

### 前端无法连接后端
```bash
# 检查 frontend/.env 中的 VITE_API_BASE_URL
VITE_API_BASE_URL=http://localhost:5000

# 验证后端是否运行
curl http://localhost:5000/api/health
```

---

## 项目结构

```
MiroFish-Offline/
├── backend/
│   ├── run.py                    # 入口点
│   ├── app.py                    # Flask 工厂，依赖注入连接
│   ├── storage/
│   │   ├── base.py               # GraphStorage 抽象接口
│   │   └── neo4j_storage.py      # Neo4j 实现
│   ├── services/
│   │   ├── graph_builder.py      # 命名实体识别 + 关系提取
│   │   ├── simulation.py         # 智能体模拟引擎
│   │   ├── report.py             # ReportAgent + 焦点小组
│   │   ├── agent_chat.py         # 每个智能体的聊天接口
│   │   └── search.py             # 混合向量 + BM25 搜索
│   └── routes/
│       ├── graph.py
│       ├── simulation.py
│       └── report.py
├── frontend/                     # Vue 3（完全英文 UI）
├── docker-compose.yml
├── .env.example
└── README.md
```
