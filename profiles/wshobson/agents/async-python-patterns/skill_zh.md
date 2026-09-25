# 异步 Python 模式

使用 asyncio、并发编程模式和 async/await 实现异步 Python 应用的全面指南，用于构建高性能、非阻塞系统。

## 何时使用这项技能

- 构建 async Web API（FastAPI、aiohttp、Sanic）
- 实现并发 I/O 操作（数据库、文件、网络）
- 使用并发请求创建网络爬虫
- 开发实时应用（WebSocket 服务器、聊天系统）
- 同时处理多个独立任务
- 使用异步通信构建微服务
- 优化 I/O 密集型工作负载
- 实现异步后台任务和队列

## 同步与异步决策指南

在采用异步之前，考虑它是否适合您的用例。

| 用例 | 推荐方法 |
|------|---------|
| 许多并发网络/数据库调用 | `asyncio` |
| CPU 密集型计算 | `multiprocessing` 或线程池 |
| 混合 I/O + CPU | 使用 `asyncio.to_thread()` 将 CPU 工作卸载 |
| 简单脚本，少量连接 | 同步（更简单，更容易调试） |
| 高并发 Web API | 异步框架（FastAPI、aiohttp） |

**关键规则**：在调用路径中保持完全同步或完全异步。混合会创建隐藏的阻塞和复杂性。

## 核心概念

### 1. 事件循环

事件循环是 asyncio 的核心，管理和调度异步任务。

**关键特性**：

- 单线程协作式多任务处理
- 调度协程执行
- 处理 I/O 操作而不阻塞
- 管理回调和 Future

### 2. 协程

使用 `async def` 定义的可以暂停和恢复的函数。

**语法**：

```python
async def my_coroutine():
    result = await some_async_operation()
    return result
```

### 3. 任务

在事件循环上并发运行的已调度协程。

### 4. Future

表示异步操作最终结果的低级对象。

### 5. 异步上下文管理器

支持 `async with` 以进行适当清理的资源。

### 6. 异步迭代器

支持 `async for` 以迭代异步数据源的迭代器。

## 快速入门

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Python 3.7+
asyncio.run(main())
```

## 基本模式

### 模式 1：基本 Async/Await

```python
import asyncio

async def fetch_data(url: str) -> dict:
    """异步获取 URL 数据。"""
    await asyncio.sleep(1)  # 模拟 I/O
    return {"url": url, "data": "result"}

async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())
```

### 模式 2：使用 gather() 进行并发执行

```python
import asyncio
from typing import List

async def fetch_user(user_id: int) -> dict:
    """获取用户数据。"""
    await asyncio.sleep(0.5)
    return {"id": user_id, "name": f"User {user_id}"}

async def fetch_all_users(user_ids: List[int]) -> List[dict]:
    """并发获取多个用户。"""
    tasks = [fetch_user(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    user_ids = [1, 2, 3, 4, 5]
    users = await fetch_all_users(user_ids)
    print(f"Fetched {len(users)} users")

asyncio.run(main())
```

### 模式 3：任务创建和管理

```python
import asyncio

async def background_task(name: str, delay: int):
    """长时间运行的背景任务。"""
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} completed")
    return f"Result from {name}"

async def main():
    # 创建任务
    task1 = asyncio.create_task(background_task("Task 1", 2))
    task2 = asyncio.create_task(background_task("Task 2", 1))

    # 执行其他工作
    print("Main: doing other work")
    await asyncio.sleep(0.5)

    # 等待任务
    result1 = await task1
    result2 = await task2

    print(f"Results: {result1}, {result2}")

asyncio.run(main())
```

### 模式 4：异步代码中的错误处理

```python
import asyncio
from typing import List, Optional

async def risky_operation(item_id: int) -> dict:
    """可能失败的操作。"""
    await asyncio.sleep(0.1)
    if item_id % 3 == 0:
        raise ValueError(f"Item {item_id} failed")
    return {"id": item_id, "status": "success"}

async def safe_operation(item_id: int) -> Optional[dict]:
    """带错误处理的包装器。"""
    try:
        return await risky_operation(item_id)
    except ValueError as e:
        print(f"Error: {e}")
        return None

async def process_items(item_ids: List[int]):
    """带错误处理地处理多个项目。"""
    tasks = [safe_operation(iid) for iid in item_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤失败
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    print(f"Success: {len(successful)}, Failed: {len(failed)}")
    return successful

asyncio.run(process_items([1, 2, 3, 4, 5, 6]))
```

### 模式 5：超时处理

```python
import asyncio

async def slow_operation(delay: int) -> str:
    """耗时操作。"""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"

async def with_timeout():
    """带超时地执行操作。"""
    try:
        result = await asyncio.wait_for(slow_operation(5), timeout=2.0)
        print(result)
    except asyncio.TimeoutError:
        print("Operation timed out")

asyncio.run(with_timeout())
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 文件中。当上面的导航摘要不足以满足需求时，请阅读该文件。

## 常见陷阱

### 1. 忘记使用 await

```python
# 错误 - 返回协程对象，不执行
result = async_function()

# 正确
result = await async_function()
```

### 2. 阻塞事件循环

```python
# 错误 - 阻塞事件循环
import time
async def bad():
    time.sleep(1)  # 阻塞！

# 正确
async def good():
    await asyncio.sleep(1)  # 非阻塞
```

### 3. 未处理取消

```python
async def cancelable_task():
    """处理取消的任务。"""
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Task cancelled, cleaning up...")
        # 执行清理
        raise  # 重新抛出以传播取消
```

### 4. 混合同步和异步代码

```python
# 错误 - 不能直接从同步调用异步
def sync_function():
    result = await async_function()  # 语法错误！

# 正确
def sync_function():
    result = asyncio.run(async_function())
```

## 测试异步代码

```python
import asyncio
import pytest

# 使用 pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数。"""
    result = await fetch_data("https://api.example.com")
    assert result is not None

@pytest.mark.asyncio
async def test_with_timeout():
    """带超时测试。"""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(5), timeout=1.0)
```
