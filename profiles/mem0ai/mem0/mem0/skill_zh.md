# Mem0 平台集成

> **技能图谱:** 此技能是 Mem0 技能图谱的一部分:
> - **mem0** (此技能) -- 平台客户端 SDK + 开源 (Python + TypeScript)
> - **[mem0-cli](../mem0-cli/SKILL.md)** ([GitHub](https://github.com/mem0ai/mem0/tree/main/skills/mem0-cli)) -- 命令行界面
> - **[mem0-vercel-ai-sdk](../mem0-vercel-ai-sdk/SKILL.md)** ([GitHub](https://github.com/mem0ai/mem0/tree/main/skills/mem0-vercel-ai-sdk)) -- Vercel AI SDK 提供者

Mem0 是 AI 应用的托管记忆层。它通过 API 存储用户记忆、检索和管理记忆——无需部署基础设施。对于自托管使用，请参阅下方客户端参考中的开源部分。

## 第 1 步：安装和认证

**Python:**
```bash
pip install mem0ai
export MEM0_API_KEY="m0-your-api-key"
```

**TypeScript/JavaScript:**
```bash
npm install mem0ai
export MEM0_API_KEY="m0-your-api-key"
```

在 https://app.mem0.ai/dashboard/api-keys?utm_source=oss&utm_medium=skill-mem0 获取 API 密钥

> **没有 `MEM0_API_KEY`？** 运行 `mem0 init --agent --agent-caller <your-name> --json` (在 `pip install mem0-cli` 或 `npm install -g @mem0/cli` 之后)，替换您的代理身份 (例如 `claude-code`, `cursor`)。如果您忘记传递 `--agent-caller`，在初始化后运行 `mem0 identify <your-name>`。人类稍后可以使用 `mem0 init --email <your-email>` 声明。

## 第 2 步：初始化客户端

**Python:**
```python
from mem0 import MemoryClient
client = MemoryClient(api_key="m0-xxx")
```

**TypeScript:**
```typescript
import MemoryClient from 'mem0ai';
const client = new MemoryClient({ apiKey: 'm0-xxx' });
```

对于异步 Python，使用 `AsyncMemoryClient`。

## 第 3 步：核心操作

每个 Mem0 集成都遵循相同的模式：**检索 → 生成 → 存储**。

### 添加记忆
```python
messages = [
    {"role": "user", "content": "我是素食者，对坚果过敏。"},
    {"role": "assistant", "content": "明白了！我会记住的。"}
]
client.add(messages, user_id="alice")
```

### 搜索记忆
```python
results = client.search("饮食偏好", filters={"user_id": "alice"})
for mem in results.get("results", []):
    print(mem["memory"])
```

### 获取所有记忆
```python
all_memories = client.get_all(filters={"user_id": "alice"})
```

### 更新记忆
```python
client.update("memory-uuid", text="更新: 素食者，对坚果过敏，偏好有机食品")
```

### 删除记忆
```python
client.delete("memory-uuid")
client.delete_all(user_id="alice")  # 删除用户的全部记忆
```

## 常见集成模式

```python
from mem0 import MemoryClient
from openai import OpenAI

mem0 = MemoryClient()
openai = OpenAI()

def chat(user_input: str, user_id: str) -> str:
    # 1. 检索相关记忆
    memories = mem0.search(user_input, filters={"user_id": user_id})
    context = "\n".join([m["memory"] for m in memories.get("results", [])])

    # 2. 带记忆上下文生成响应
    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": f"用户上下文:\n{context}"},
            {"role": "user", "content": user_input},
        ]
    )
    reply = response.choices[0].message.content

    # 3. 存储交互以供未来上下文使用
    mem0.add(
        [{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}],
        user_id=user_id
    )
    return reply
```

## 常见边缘情况

- **搜索结果为空:** 记忆异步处理。在 `add()` 后等待 2-3 秒再搜索。同时请确保 `user_id` 完全匹配 (区分大小写) 并使用 `filters={"user_id": "..."}` 语法。
- **AND 筛选器与 user_id + agent_id 返回空:** 实体单独存储。使用 `OR` 替代，或分别查询。
- **重复记忆:** 不要将 `infer=True` (默认) 和 `infer=False` 混合用于相同数据。坚持使用一种模式。
- **错误导入:** 始终使用 `from mem0 import MemoryClient` (或 `AsyncMemoryClient` 用于异步)。不要使用 `from mem0 import Memory`。
- **v3 默认值:** `top_k=20`, `threshold=0.1`, `rerank=False`。根据您的用例调整。

## v2 兼容性

如果您使用 SDK v2.x，请注意以下差异:
- **实体 ID:** 将 `user_id` 作为顶级关键字参数传递给 `search()`，而不是在 `filters` 内部
- **默认值:** `top_k=100`，无阈值，`rerank=True`
- **图记忆:** 通过 `enable_graph=True` 可用

有关详细信息，请参阅 [迁移指南](https://docs.mem0.ai/migration/oss-v2-to-v3)。

## 实时文档搜索

对于参考资料之外的最新文档，使用文档搜索工具:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/mem0_doc_search.py --query "主题"
python ${CLAUDE_SKILL_DIR}/scripts/mem0_doc_search.py --page "/platform/features/graph-memory"
python ${CLAUDE_SKILL_DIR}/scripts/mem0_doc_search.py --index
```

无需 API 密钥——直接搜索 docs.mem0.ai 文档。

## 客户端 SDK 参考

语言特定的深度参考 (平台 + 开源):

| 语言 | 文件 |
|------|------|
| Python (MemoryClient + AsyncMemoryClient + Memory OSS) | [client/python.md](client/python.md) |
| TypeScript/Node.js (MemoryClient + Memory OSS) | [client/node.md](client/node.md) |
| Python 与 TypeScript 的差异 | [client/differences.md](client/differences.md) |

## 平台参考

按需加载以获取更详细信息:

| 主题 | 文件 |
|------|------|
| 快速入门 (Python, TS, cURL) | [references/quickstart.md](references/quickstart.md) |
| SDK 指南 (所有方法，两种语言) | [references/sdk-guide.md](references/sdk-guide.md) |
| API 参考 (端点，筛选器，对象模式) | [references/api-reference.md](references/api-reference.md) |
| 架构 (管道，生命周期，作用域，性能) | [references/architecture.md](references/architecture.md) |
| 平台功能 (检索，图，分类，MCP 等) | [references/features.md](references/features.md) |
| 框架集成 (LangChain，CrewAI，OpenAI Agents 等) | [references/integration-patterns.md](references/integration-patterns.md) |
| 用例和示例 (带代码的现实模式) | [references/use-cases.md](references/use-cases.md) |

## 相关 Mem0 技能

| 技能 | 何时使用 | 链接 |
|------|--------|------|
| mem0-cli | 命令行操作，脚本，CI/CD，代理工具循环 | [本地](../mem0-cli/SKILL.md) / [GitHub](https://github.com/mem0ai/mem0/tree/main/skills/mem0-cli) |
| mem0-vercel-ai-sdk | 自动记忆的 Vercel AI SDK 提供者 | [本地](../mem0-vercel-ai-sdk/SKILL.md) / [GitHub](https://github.com/mem0ai/mem0/tree/main/skills/mem0-vercel-ai-sdk) |
