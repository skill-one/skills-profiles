# Python 弹性设计模式

构建能够优雅处理瞬态故障、网络问题和服务中断的容错 Python 应用程序。弹性设计模式能够在依赖项不可靠时保持系统运行。

## 何时使用此技能

- 为外部服务调用添加重试逻辑
- 为网络操作实现超时
- 构建容错微服务
- 处理速率限制和反向压力
- 创建基础设施装饰器
- 设计断路器

## 核心概念

### 1. 瞬态故障与永久故障

重试瞬态错误（网络超时、临时服务问题）。不要重试永久错误（无效凭证、错误请求）。

### 2. 指数退避

增加重试之间的等待时间，以避免使正在恢复的服务不堪重负。

### 3. 抖动

在退避中添加随机性，以防止当多个客户端同时重试时出现雷鸣群集效应。

### 4. 有界重试

限制尝试次数和总持续时间，以防止无限重试循环。

## 快速入门

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def call_external_service(request: dict) -> dict:
    return httpx.post("https://api.example.com", json=request).json()
```

## 基础模式

### 模式 1：使用 Tenacity 的基本重试

使用 `tenacity` 库实现生产级重试逻辑。对于简单情况，可以考虑内置重试功能或轻量级自定义实现。

```python
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
    retry_if_exception_type,
)

TRANSIENT_ERRORS = (ConnectionError, TimeoutError, OSError)

@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS),
    stop=stop_after_attempt(5) | stop_after_delay(60),
    wait=wait_exponential_jitter(initial=1, max=30),
)
def fetch_data(url: str) -> dict:
    """在瞬态故障时自动重试获取数据。"""
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### 模式 2：仅重试适当的错误

白名单特定的瞬态异常。永远不要重试：

- `ValueError`, `TypeError` - 这些是错误，不是瞬态问题
- `AuthenticationError` - 无效凭证不会变得有效
- HTTP 4xx 错误（除 429 外）- 客户端错误是永久性的

```python
from tenacity import retry, retry_if_exception_type
import httpx

# 定义可重试的错误
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
)

@retry(
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def resilient_api_call(endpoint: str) -> dict:
    """在网络问题发生时重试 API 调用。"""
    return httpx.get(endpoint, timeout=10).json()
```

### 模式 3：HTTP 状态码重试

重试指示瞬态问题的特定 HTTP 状态码。

```python
from tenacity import retry, retry_if_result, stop_after_attempt
import httpx

RETRY_STATUS_CODES = {429, 502, 503, 504}

def should_retry_response(response: httpx.Response) -> bool:
    """检查响应是否指示可重试的错误。"""
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=retry_if_result(should_retry_response),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def http_request(method: str, url: str, **kwargs) -> httpx.Response:
    """在瞬态状态码发生时重试 HTTP 请求。"""
    return httpx.request(method, url, timeout=30, **kwargs)
```

### 模式 4：组合异常和状态码重试

处理网络异常和 HTTP 状态码。

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)
import logging
import httpx

logger = logging.getLogger(__name__)

TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectError,
    httpx.ReadTimeout,
)
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

def is_retryable_response(response: httpx.Response) -> bool:
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=(
        retry_if_exception_type(TRANSIENT_EXCEPTIONS) |
        retry_if_result(is_retryable_response)
    ),
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def robust_http_call(
    method: str,
    url: str,
    **kwargs,
) -> httpx.Response:
    """具有全面重试处理的 HTTP 调用。"""
    return httpx.request(method, url, timeout=30, **kwargs)
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 文件中。当上面的导航摘要不足以满足需求时，请阅读该文件。

## 最佳实践总结

1. **仅重试瞬态错误** - 不要重试错误或身份验证失败
2. **使用指数退避** - 给服务恢复时间
3. **添加抖动** - 防止同步重试的雷鸣群集效应
4. **限制总持续时间** - `stop_after_attempt(5) | stop_after_delay(60)`
5. **记录每次重试** - 静默重试隐藏系统问题
6. **使用装饰器** - 将重试逻辑与业务逻辑分离
7. **注入依赖项** - 使基础设施可测试
8. **到处设置超时** - 每个网络调用都需要超时
9. **优雅失败** - 对于非关键路径返回缓存的默认值
10. **监控重试率** - 高重试率指示潜在问题
