# Python 资源管理

使用上下文管理器以确定性方式管理资源。数据库连接、文件句柄和网络套接字等资源应在出现异常时可靠地释放。

## 何时使用此技能

- 管理数据库连接和连接池
- 处理文件句柄和 I/O
- 实现自定义上下文管理器
- 构建带状态流式响应
- 处理嵌套资源清理
- 创建异步上下文管理器

## 核心概念

### 1. 上下文管理器

`with` 语句确保资源在出现异常时自动释放。

### 2. 协议方法

同步资源管理使用 `__enter__`/`__exit__`，异步资源管理使用 `__aenter__`/`__aexit__`。

### 3. 无条件清理

`__exit__` 总是会运行，无论是否发生异常。

### 4. 异常处理

从 `__exit__` 返回 `True` 以抑制异常，返回 `False` 以传播异常。

## 快速入门

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.cleanup()

with managed_resource() as r:
    r.do_work()
```

## 基础模式

### 模式 1：基于类的上下文管理器

为复杂资源实现上下文管理器协议。

```python
class DatabaseConnection:
    """带自动清理的数据库连接。"""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: Connection | None = None

    def connect(self) -> None:
        """建立数据库连接。"""
        self._conn = psycopg.connect(self._dsn)

    def close(self) -> None:
        """如果已打开则关闭连接。"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DatabaseConnection":
        """进入上下文：连接并返回 self。"""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """退出上下文：始终关闭连接。"""
        self.close()

# 使用上下文管理器（推荐）
with DatabaseConnection(dsn) as db:
    result = db.execute(query)

# 需要时手动管理
db = DatabaseConnection(dsn)
db.connect()
try:
    result = db.execute(query)
finally:
    db.close()
```

### 模式 2：异步上下文管理器

为异步资源实现异步协议。

```python
class AsyncDatabasePool:
    """异步数据库连接池。"""

    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> "AsyncDatabasePool":
        """创建连接池。"""
        self._pool = await asyncpg.create_pool(
            self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """关闭池中的所有连接。"""
        if self._pool is not None:
            await self._pool.close()

    async def execute(self, query: str, *args) -> list[dict]:
        """使用池连接执行查询。"""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

# 使用
async with AsyncDatabasePool(dsn) as pool:
    users = await pool.execute("SELECT * FROM users WHERE active = $1", True)
```

### 模式 3：使用 @contextmanager 装饰器

使用装饰器简化上下文管理器，适用于简单情况。

```python
from contextlib import contextmanager, asynccontextmanager
import time
import structlog

logger = structlog.get_logger()

@contextmanager
def timed_block(name: str):
    """计时代码块。"""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{name} completed", duration_seconds=round(elapsed, 3))

# 使用
with timed_block("data_processing"):
    process_large_dataset()

@asynccontextmanager
async def database_transaction(conn: AsyncConnection):
    """管理数据库事务。"""
    await conn.execute("BEGIN")
    try:
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise

# 使用
async with database_transaction(conn) as tx:
    await tx.execute("INSERT INTO users ...")
    await tx.execute("INSERT INTO audit_log ...")
```

### 模式 4：无条件资源释放

在 `__exit__` 中始终清理资源，无论是否发生异常。

```python
class FileProcessor:
    """带保证清理的文件处理器。"""

    def __init__(self, path: str) -> None:
        self._path = path
        self._file: IO | None = None
        self._temp_files: list[Path] = []

    def __enter__(self) -> "FileProcessor":
        self._file = open(self._path, "r")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """无条件清理所有资源。"""
        # 关闭主文件
        if self._file is not None:
            self._file.close()

        # 清理任何临时文件
        for temp_file in self._temp_files:
            try:
                temp_file.unlink()
            except OSError:
                pass  # 最佳努力清理

        # 返回 None/False 以传播任何异常
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 文件中。当导航摘要不足以提供信息时，请阅读该文件。

## 最佳实践总结

1. **始终使用上下文管理器** - 对于任何需要清理的资源
2. **无条件清理** - `__exit__` 即使在异常发生时也会运行
3. **不要意外抑制** - 除非有意抑制，否则返回 `False`
4. **使用 @contextmanager** - 对于简单的资源模式
5. **实现两个协议** - 支持使用 `with` 和手动管理
6. **使用 ExitStack** - 用于动态数量的资源
7. **高效累积** - 列表 + join，而不是字符串连接
8. **跟踪指标** - 对于流式传输，首次字节时间很重要
9. **记录行为** - 特别是异常抑制
10. **测试清理路径** - 验证在错误时资源是否被释放
