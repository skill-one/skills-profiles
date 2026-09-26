# Redis 语义缓存

使用 Redis Cloud 的 LangCache 服务对 LLM 响应进行语义缓存。将提示存储为嵌入；后续语义相似的提示将直接返回缓存的响应，而无需重新调用模型。

> LangCache 目前在 Redis Cloud 上处于 **预览** 状态。功能和行为可能会有所变化。

## 何时使用

- 用缓存层封装 LLM 调用（如 OpenAI、Anthropic 等），以降低成本和延迟。
- 缓存 RAG 响答、分类输出或任何确定性 LLM 工作负载。
- 调整语义缓存的精确度/命中率权衡。
- 将一个应用程序的 LLM 工作负载分配到多个缓存实例。

## 1. 缓存旁路流程

LangCache 作为标准缓存旁路模式，适用于任何 LLM 调用之前：

1. 将用户的提示发送到 LangCache 的 `search`。
2. **缓存命中** — 直接返回存储的响应。
3. **缓存未命中** — 调用 LLM，然后 `set` 响应，以便未来相似的提示命中。

```python
from langcache import LangCache
import os

lang_cache = LangCache(
    server_url=f"https://{os.getenv('HOST')}",
    cache_id=os.getenv("CACHE_ID"),
    api_key=os.getenv("API_KEY"),
)

result = lang_cache.search(prompt="What is Redis?", similarity_threshold=0.9)
if result:
    response = result[0]["response"]
else:
    response = llm.generate("What is Redis?")
    lang_cache.set(prompt="What is Redis?", response=response)
```

当无法使用 SDK 时，可通过 REST (`POST /v1/caches/{cacheId}/entries/search` 和 `POST /v1/caches/{cacheId}/entries`) 进行相同操作。

有关完整的 SDK + REST 示例和基于属性的存储，请参阅 [references/langcache-usage.md](references/langcache-usage.md)。

## 2. 调整相似度阈值

阈值控制新提示必须与缓存提示在嵌入余弦距离上多接近才能计为命中。更高 = 更严格的匹配，更少的误报。更低 = 更高的命中率，但返回离题答案的风险更高。

| 阈值 | 行为 | 何时使用 |
|---|---|---|
| 0.95+ | 需要近似完全匹配 | 用户界面答案，错误响应成本高昂 |
| 0.9 | 平衡默认值 | 大多数工作负载 — 从这里开始 |
| 0.8 | 松散的语义匹配 | 内部工具、探索性查询、FAQ 去重 |

```python
# 更严格 — 更少的误报
result = lang_cache.search(prompt="What is Redis?", similarity_threshold=0.95)

# 更宽松 — 更高的命中率
result = lang_cache.search(prompt="What is Redis?", similarity_threshold=0.8)
```

通过观察实际的缓存命中率并抽查返回的答案是否仍然相关来调整。

请参阅 [references/best-practices.md](references/best-practices.md)。

## 3. 按任务类型分离缓存

不同的 LLM 工作负载不应共享一个缓存 — “代码问题”提示与其它代码问题语义上接近，但与密码重置支持查询无关，交叉使用会返回垃圾信息。

```python
support_cache = LangCache(server_url=..., cache_id="support-cache-id", api_key=...)
code_cache    = LangCache(server_url=..., cache_id="code-cache-id",    api_key=...)
```

在 Redis Cloud 中为每个任务创建不同的缓存 ID，并将每个调用路由到正确的缓存。作为更细粒度的替代方案，使用 **自定义属性**（例如 `{"category": "database"}`）存储和搜索，以将任务保持在同一缓存中但通过属性过滤器隔离 — 当相同的提示格式跨越子主题时很有用。

## 参考资料

- [LangCache 文档](https://redis.io/docs/latest/develop/ai/langcache/)
