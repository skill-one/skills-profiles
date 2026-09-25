# GPT研究员开发技能

GPT研究员是一个基于LLM的自主代理，采用规划器-执行器-发布者模式，通过并行化代理工作来提高速度和可靠性。

## 快速入门

### 基本Python使用

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    researcher = GPTResearcher(
        query="最新的AI发展是什么？",
        report_type="研究报告",  # 或者detailed_report、deep、outline_report
        report_source="网络",            # 或者local、hybrid
    )
    await researcher进行研究()
    report = await researcher撰写报告()
    print(report)

asyncio.run(main())
```

### 运行服务器

```bash
# 后端
python -m uvicorn backend.server.server:app --reload --port 8000

# 前端
cd frontend/nextjs && npm install && npm run dev
```

---

## 关键文件位置

| 需求 | 主要文件 | 关键类 |
|------|--------------|-------------|
| 主协调器 | `gpt_researcher/agent.py` | `GPTResearcher` |
| 研究逻辑 | `gpt_researcher/skills/researcher.py` | `ResearchConductor` |
| 报告撰写 | `gpt_researcher/skills/writer.py` | `ReportGenerator` |
| 所有提示 | `gpt_researcher/prompts.py` | `PromptFamily` |
| 配置 | `gpt_researcher/config/config.py` | `Config` |
| 配置默认值 | `gpt_researcher/config/variables/default.py` | `DEFAULT_CONFIG` |
| API服务器 | `backend/server/app.py` | FastAPI `app` |
| 搜索引擎 | `gpt_researcher/retrievers/` | 各种检索器 |

---

## 架构概述

```
用户查询 → GPTResearcher.__init__()
                │
                ▼
         choose_agent() → (agent_type, role_prompt)
                │
                ▼
         ResearchConductor进行研究()
           ├── plan_research() → 子查询
           ├── 对于每个子查询:
           │     └── _process_sub_query() → 上下文
           └── 汇总上下文
                │
                ▼
         [可选] ImageGenerator.plan_and_generate_images()
                │
                ▼
         ReportGenerator.write_report() → Markdown报告
```

**有关详细架构图**: 查看[references/architecture.md](references/architecture.md)

---

## 核心模式

### 添加新功能（8步模式）

1. **配置** → 添加到`gpt_researcher/config/variables/default.py`
2. **提供者** → 创建在`gpt_researcher/llm_provider/my_feature/`
3. **技能** → 创建在`gpt_researcher/skills/my_feature.py`
4. **代理** → 集成在`gpt_researcher/agent.py`
5. **提示** → 更新`gpt_researcher/prompts.py`
6. **WebSocket** → 通过`stream_output()`发送事件
7. **前端** → 在`useWebSocket.ts`中处理事件
8. **文档** → 创建`docs/docs/gpt-researcher/gptr/my_feature.md`

**有关完整功能添加指南和图像生成案例研究**: 查看[references/adding-features.md](references/adding-features.md)

### 添加新检索器

```python
# 1. 创建: gpt_researcher/retrievers/my_retriever/my_retriever.py
class MyRetriever:
    def __init__(self, query: str, headers: dict = None):
        self.query = query
    
    async def search(self, max_results: int = 10) -> list[dict]:
        # 返回: [{"title": str, "href": str, "body": str}]
        pass

# 2. 在gpt_researcher/actions/retriever.py中注册
case "my_retriever":
    from gpt_researcher.retrievers.my_retriever import MyRetriever
    return MyRetriever

# 3. 在gpt_researcher/retrievers/__init__.py中导出
```

**有关完整检索器文档**: 查看[references/retrievers.md](references/retrievers.md)

---

## 配置

配置键在被访问时**全部小写**:

```python
# 在default.py中: "SMART_LLM": "gpt-4o"
# 访问为: self.cfg.smart_llm  # 全小写！
```

优先级：环境变量 → JSON配置文件 → 默认值

**有关完整配置参考**: 查看[references/config-reference.md](references/config-reference.md)

---

## 常见集成点

### WebSocket流式传输

```python
class WebSocketHandler:
    async def send_json(self, data):
        print(f"[{data['type']}] {data.get('output', '')}")

researcher = GPTResearcher(query="...", websocket=WebSocketHandler())
```

### MCP数据源

```python
researcher = GPTResearcher(
    query="开源AI项目",
    mcp_configs=[{
        "name": "github",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}
    }],
    mcp_strategy="deep",  # 或者"fast"、"disabled"
)
```

**有关MCP集成细节**: 查看[references/mcp.md](references/mcp.md)

### 深度研究模式

```python
researcher = GPTResearcher(
    query="量子计算的全面分析",
    report_type="deep",  # 触发递归树状探索
)
```

**有关深度研究配置**: 查看[references/deep-research.md](references/deep-research.md)

---

## 错误处理

始终在技能中使用优雅降级:

```python
async def execute(self, ...):
    if not self.is_enabled():
        return []  # 不要崩溃
    
    try:
        result = await self.provider.execute(...)
        return result
    except Exception as e:
        await stream_output("logs", "error", f"⚠️ {e}", self.websocket)
        return []  # 优雅降级
```

---

## 关键注意事项

| ❌ 错误 | ✅ 正确 |
|-----------|-----------|
| `config.MY_VAR` | `config.my_var` (全小写) |
| 编辑已安装的pip包 | `pip install -e .` |
| 忘记async/await | 所有研究方法都是异步的 |
| `websocket.send_json()`在None上 | 先检查`if websocket:` |
| 未注册检索器 | 添加到`retriever.py`的match语句 |

---

## 参考文档

| 主题 | 文件 |
|-------|------|
| 系统架构和图表 | [references/architecture.md](references/architecture.md) |
| 核心组件和签名 | [references/components.md](references/components.md) |
| 研究流程和数据流程 | [references/flows.md](references/flows.md) |
| 提示系统 | [references/prompts.md](references/prompts.md) |
| 检索器系统 | [references/retrievers.md](references/retrievers.md) |
| MCP集成 | [references/mcp.md](references/mcp.md) |
| 深度研究模式 | [references/deep-research.md](references/deep-research.md) |
| 多代理系统 | [references/multi-agents.md](references/multi-agents.md) |
| 添加功能指南 | [references/adding-features.md](references/adding-features.md) |
| 高级模式 | [references/advanced-patterns.md](references/advanced-patterns.md) |
| REST & WebSocket API | [references/api-reference.md](references/api-reference.md) |
| 配置变量 | [references/config-reference.md](references/config-reference.md) |
