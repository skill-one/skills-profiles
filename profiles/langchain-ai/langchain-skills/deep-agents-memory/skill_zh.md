<概述>
Deep Agents 使用可插拔的后端进行文件操作和内存管理：

**短期（StateBackend）**： 在单个线程内持久化，线程结束时丢失
**长期（StoreBackend）**： 跨线程和会话持久化
**混合（CompositeBackend）**： 将不同路径路由到不同的后端

FilesystemMiddleware 提供工具：`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`
</概述>

<后端选择>

| 使用场景 | 后端 | 原因 |
|----------|---------|-----|
| 临时工作文件 | StateBackend | 默认，无需设置 |
| 本地开发 CLI | FilesystemBackend | 直接磁盘访问 |
| 跨会话内存 | StoreBackend | 跨线程持久化 |
| 混合存储 | CompositeBackend | 混合临时和持久存储 |

</后端选择>

<默认 StateBackend 示例>
<python>
默认 StateBackend 在线程内临时存储文件。

```python
from deepagents import create_deep_agent

agent = create_deep_agent()  # 默认：StateBackend
result = agent.invoke({
    "messages": [{"role": "user", "content": "写入笔记到 /draft.txt"}]
}, config={"configurable": {"thread_id": "thread-1"}})
# /draft.txt 在线程结束时丢失
```
</python>
<typescript>
默认 StateBackend 在线程内临时存储文件。

```typescript
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent();  // 默认：StateBackend
const result = await agent.invoke({
  messages: [{ role: "user", content: "写入笔记到 /draft.txt" }]
}, { configurable: { thread_id: "thread-1" } });
// /draft.txt 在线程结束时丢失
```
</typescript>
</默认 StateBackend 示例>

<混合 CompositeBackend 示例>
<python>
配置 CompositeBackend 将路径路由到不同的存储后端。

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),
    routes={"/memories/": StoreBackend(rt)}
)

agent = create_deep_agent(backend=composite_backend, store=store)

# /draft.txt -> 临时 (StateBackend)
# /memories/user-prefs.txt -> 持久 (StoreBackend)
```
</python>
<typescript>
配置 CompositeBackend 将路径路由到不同的存储后端。

```typescript
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    { "/memories/": new StoreBackend(config) }
  ),
  store
});

// /draft.txt -> 临时 (StateBackend)
// /memories/user-prefs.txt -> 持久 (StoreBackend)
```
</typescript>
</混合 CompositeBackend 示例>

<跨会话内存示例>
<python>
通过 StoreBackend 路由，/memories/ 中的文件跨线程持久化。

```python
# 使用前例中的 CompositeBackend
config1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke({"messages": [{"role": "user", "content": "保存到 /memories/style.txt"}]}, config=config1)

config2 = {"configurable": {"thread_id": "thread-2"}}
agent.invoke({"messages": [{"role": "user", "content": "读取 /memories/style.txt"}]}, config=config2)
# Thread 2 可以读取 Thread 1 保存的文件
```
</python>
<typescript>
通过 StoreBackend 路由，/memories/ 中的文件跨线程持久化。

```typescript
// 使用前例中的 CompositeBackend
const config1 = { configurable: { thread_id: "thread-1" } };
await agent.invoke({ messages: [{ role: "user", content: "保存到 /memories/style.txt" }] }, config1);

const config2 = { configurable: { thread_id: "thread-2" } };
await agent.invoke({ messages: [{ role: "user", content: "读取 /memories/style.txt" }] }, config2);
// Thread 2 可以读取 Thread 1 保存的文件
```
</typescript>
</跨会话内存示例>

<本地开发 FilesystemBackend 示例>
<python>
使用 FilesystemBackend 进行本地开发，具有真实磁盘访问和人工交互。

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),  # 限制访问
    interrupt_on={"write_file": True, "edit_file": True},
    checkpointer=MemorySaver()
)

# Agent 可以读写磁盘上的实际文件
```
</python>
<typescript>
使用 FilesystemBackend 进行本地开发，具有真实磁盘访问和人工交互。

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  interruptOn: { write_file: true, edit_file: true },
  checkpointer: new MemorySaver()
});
```
</typescript>

**安全提示**： 永远不要在 Web 服务器中使用 FilesystemBackend - 使用 StateBackend 或沙盒替代。
</本地开发 FilesystemBackend 示例>

<自定义工具中访问存储>
<python>
在自定义工具中直接访问存储进行长期内存操作。

```python
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

@tool
def get_user_preference(key: str, runtime: ToolRuntime) -> str:
    """从长期存储中获取用户偏好。"""
    store = runtime.store
    result = store.get(("user_prefs",), key)
    return str(result.value) if result else "未找到"

@tool
def save_user_preference(key: str, value: str, runtime: ToolRuntime) -> str:
    """将用户偏好保存到长期存储。"""
    store = runtime.store
    store.put(("user_prefs",), key, {"value": value})
    return f"保存 {key}={value}"

store = InMemoryStore()

agent = create_agent(
    model="gpt-4.1",
    tools=[get_user_preference, save_user_preference],
    store=store
)
```
</python>
</自定义工具中访问存储>

<边界限制>
### Agents 可以配置的内容

- 后端类型和配置
- CompositeBackend 的路由规则
- FilesystemBackend 的根目录
- 文件操作的人工交互

### Agents 不能配置的内容

- 工具名称（ls、read_file、write_file、edit_file、glob、grep）
- 虚拟模式限制外的文件访问
- 无适当后端设置时的跨线程文件访问
</边界限制>

<StoreBackend 需要存储实例修复>
<python>
StoreBackend 需要存储实例。

```python
# 错误
agent = create_deep_agent(backend=lambda rt: StoreBackend(rt))

# 正确
agent = create_deep_agent(backend=lambda rt: StoreBackend(rt), store=InMemoryStore())
```
</python>
<typescript>
StoreBackend 需要存储实例。

```typescript
// 错误
const agent = await createDeepAgent({ backend: (c) => new StoreBackend(c) });

// 正确
const agent = await createDeepAgent({ backend: (c) => new StoreBackend(c), store: new InMemoryStore() });
```
</typescript>
</StoreBackend 需要存储实例修复>

<StateBackend 文件不持久修复>
<python>
StateBackend 文件是线程范围的 - 使用相同 thread_id 或 StoreBackend 进行跨线程访问。

```python
# 错误：thread-2 无法读取 thread-1 的文件
agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "thread-1"}})  # 写入
agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "thread-2"}})  # 文件未找到！
```
</python>
<typescript>
StateBackend 文件是线程范围的 - 使用相同 thread_id 或 StoreBackend 进行跨线程访问。

```typescript
// 错误：thread-2 无法读取 thread-1 的文件
await agent.invoke({ messages: [...] }, { configurable: { thread_id: "thread-1" } });  // 写入
await agent.invoke({ messages: [...] }, { configurable: { thread_id: "thread-2" } });  // 文件未找到！
```
</typescript>
</StateBackend 文件不持久修复>

<持久化路径前缀修复>
<python>
路径必须与 CompositeBackend 路由前缀匹配才能持久化。

```python
# With routes={"/memories/": StoreBackend(rt)}:
agent.invoke(...)  # /prefs.txt -> 临时 (无匹配)
agent.invoke(...)  # /memories/prefs.txt -> 持久 (匹配路由)
```
</python>
<typescript>
路径必须与 CompositeBackend 路由前缀匹配才能持久化。

```typescript
// With routes: { "/memories/": StoreBackend }:
await agent.invoke(...);  // /prefs.txt -> 临时 (无匹配)
await agent.invoke(...);  // /memories/prefs.txt -> 持久 (匹配路由)
```
</typescript>
</持久化路径前缀修复>

<生产环境存储修复>
<python>
使用 PostgresStore 进行生产（InMemoryStore 重启时丢失）。

```python
# 错误                              # 正确
store = InMemoryStore()              store = PostgresStore(connection_string="postgresql://...")
```
</python>
<typescript>
使用 PostgresStore 进行生产（InMemoryStore 重启时丢失）。

```typescript
// 错误                                    // 正确
const store = new InMemoryStore();          const store = new PostgresStore({ connectionString: "..." });
```
</typescript>
</生产环境存储修复>

<FilesystemBackend 需要虚拟模式修复>
<python>
启用 virtual_mode=True 以限制路径访问（防止 ../ 和 ~/ 逃逸）。

```python
backend = FilesystemBackend(root_dir="/project", virtual_mode=True)  # 安全
```
</python>
</FilesystemBackend 需要虚拟模式修复>

<最长前缀匹配修复>
<python>
CompositeBackend 按最长前缀优先匹配。

```python
routes = {"/mem/": StoreBackend(rt), "/mem/temp/": StateBackend(rt)}
# /mem/file.txt -> StoreBackend, /mem/temp/file.txt -> StateBackend (更长的匹配)
```
</python>
</最长前缀匹配修复>
