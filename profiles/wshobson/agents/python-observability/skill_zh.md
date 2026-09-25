# Python 可观测性

为 Python 应用程序添加结构化日志、指标和跟踪。当生产环境出现问题时，你需要在不部署新代码的情况下回答“是什么、在哪里、为什么”。

## 使用此技能的场景

- 为应用程序添加结构化日志
- 使用 Prometheus 实现指标收集
- 在服务之间设置分布式跟踪
- 在请求链中传递关联 ID
- 调试生产问题
- 构建可观测性仪表板

## 核心概念

### 1. 结构化日志

在生产环境中以 JSON 格式输出日志，并包含一致的字段。机器可读的日志支持强大的查询和警报。对于本地开发，可以考虑人类可读的格式。

### 2. 四大黄金信号

跟踪每个服务边界处的延迟、流量、错误和饱和度。

### 3. 关联 ID

在所有日志和跨度中串联一个唯一的 ID，以实现端到端跟踪。

### 4. 有界基数

保持指标标签值的有界性。无界标签（如用户 ID）会爆炸式增加存储成本。

## 快速入门

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()
logger.info("Request processed", user_id="123", duration_ms=45)
```

## 基础模式

### 模式 1：使用 Structlog 进行结构化日志

配置 Structlog 以输出 JSON 格式并包含一致的字段。

```python
import logging
import structlog

def configure_logging(log_level: str = "INFO") -> None:
    """为应用程序配置结构化日志记录。"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# 在应用程序启动时初始化
configure_logging("INFO")
logger = structlog.get_logger()
```

### 模式 2：一致的日志字段

每个日志条目都应包含用于过滤和关联的标准字段。

```python
import structlog
from contextvars import ContextVar

# 在上下文中存储关联 ID
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

logger = structlog.get_logger()

def process_request(request: Request) -> Response:
    """使用结构化日志记录处理请求。"""
    logger.info(
        "Request received",
        correlation_id=correlation_id.get(),
        method=request.method,
        path=request.path,
        user_id=request.user_id,
    )

    try:
        result = handle_request(request)
        logger.info(
            "Request completed",
            correlation_id=correlation_id.get(),
            status_code=200,
            duration_ms=elapsed,
        )
        return result
    except Exception as e:
        logger.error(
            "Request failed",
            correlation_id=correlation_id.get(),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        raise
```

### 模式 3：语义日志级别

在整个应用程序中一致地使用日志级别。

| 级别 | 目的 | 示例 |
|------|------|------|
| `DEBUG` | 开发诊断 | 变量值、内部状态 |
| `INFO` | 请求生命周期、操作 | 请求开始/结束、任务完成 |
| `WARNING` | 可恢复的异常 | 重试尝试、回退使用 |
| `ERROR` | 需要关注的失败 | 异常、服务不可用 |

```python
# DEBUG：详细的内部信息
logger.debug("Cache lookup", key=cache_key, hit=cache_hit)

# INFO：正常的操作事件
logger.info("Order created", order_id=order.id, total=order.total)

# WARNING：异常但已处理的情况
logger.warning(
    "Rate limit approaching",
    current_rate=950,
    limit=1000,
    reset_seconds=30,
)

# ERROR：需要调查的失败
logger.error(
    "Payment processing failed",
    order_id=order.id,
    error=str(e),
    payment_provider="stripe",
)
```

不要在 `ERROR` 级别记录预期行为。用户输入错误密码是 `INFO`，而不是 `ERROR`。

### 模式 4：关联 ID 传播

在入口处生成一个唯一 ID，并将其串联到所有操作中。

```python
from contextvars import ContextVar
import uuid
import structlog

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def set_correlation_id(cid: str | None = None) -> str:
    """为当前上下文设置关联 ID。"""
    cid = cid or str(uuid.uuid4())
    correlation_id.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid)
    return cid

# FastAPI 中间件示例
from fastapi import Request

async def correlation_middleware(request: Request, call_next):
    """中间件以设置和传播关联 ID。"""
    # 使用传入的头部或生成新的
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    set_correlation_id(cid)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response
```

传播到出站请求：

```python
import httpx

async def call_downstream_service(endpoint: str, data: dict) -> dict:
    """带关联 ID 调用下游服务。"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=data,
            headers={"X-Correlation-ID": correlation_id.get()},
        )
        return response.json()
```

## 详细的工作示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 中。当上面的导航摘要不足以说明时，请阅读该文件。

## 最佳实践总结

1. **使用结构化日志** - 带有一致字段的 JSON 日志
2. **传播关联 ID** - 串联到所有请求和日志中
3. **跟踪四大黄金信号** - 延迟、流量、错误、饱和度
4. **有界标签基数** - 不要将无界值用作指标标签
5. **在适当的级别记录** - 不要用 `ERROR` 发出虚假警报
6. **包含上下文** - 用户 ID、请求 ID、操作名称在日志中
7. **使用上下文管理器** - 一致的计时和错误处理
8. **分离关注点** - 可观测性代码不应污染业务逻辑
9. **测试你的可观测性** - 在集成测试中验证日志和指标
10. **设置警报** - 指标在没有警报的情况下是无用的
