# Python 后台任务与任务队列

将耗时较长或不可靠的工作与请求/响应周期解耦。立即返回给用户，同时后台工作者异步处理繁重的工作。

## 何时使用此技能

- 处理耗时超过几秒钟的任务
- 发送电子邮件、通知或 webhook
- 生成报告或导出数据
- 处理上传或媒体转换
- 与不可靠的外部服务集成
- 构建事件驱动架构

## 核心概念

### 1. 任务队列模式

API 接收请求，将任务入队，立即返回任务 ID。工作者异步处理任务。

### 2. 不可变性

任务可能在失败时被重试。设计为安全地重新执行。

### 3. 任务状态机

任务通过状态转换：待处理 → 运行 → 成功/失败。

### 4. 至少一次交付

大多数队列保证至少一次交付。你的代码必须处理重复项。

## 快速入门

此技能使用 Celery 作为示例，它是一种广泛采用的任务队列。其他选择如 RQ、Dramatiq 和云原生解决方案（AWS SQS、GCP Tasks）同样有效。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

@app.task
def send_email(to: str, subject: str, body: str) -> None:
    # 这将在后台工作者中运行
    email_client.send(to, subject, body)

# 在你的 API 处理程序中
send_email.delay("user@example.com", "欢迎！", "感谢你注册")
```

## 基础模式

### 模式 1：立即返回任务 ID

对于耗时超过几秒钟的操作，返回任务 ID 并异步处理。

```python
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

@dataclass
class Job:
    id: str
    status: JobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict | None = None
    error: str | None = None

# API 端点
async def start_export(request: ExportRequest) -> JobResponse:
    """启动导出任务并返回任务 ID。"""
    job_id = str(uuid4())

    # 持久化任务记录
    await jobs_repo.create(Job(
        id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
    ))

    # 入队任务进行后台处理
    await task_queue.enqueue(
        "export_data",
        job_id=job_id,
        params=request.model_dump(),
    )

    # 立即返回任务 ID
    return JobResponse(
        job_id=job_id,
        status="pending",
        poll_url=f"/jobs/{job_id}",
    )
```

### 模式 2：Celery 任务配置

使用适当的重试和超时设置配置 Celery 任务。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

# 全局配置
app.conf.update(
    task_time_limit=3600,          # 硬限制：1 小时
    task_soft_time_limit=3000,      # 软限制：50 分钟
    task_acks_late=True,            # 完成后确认
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,   # 不要预取太多任务
)

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
)
def process_payment(self, payment_id: str) -> dict:
    """处理支付，在瞬态错误时自动重试。"""
    try:
        result = payment_gateway.charge(payment_id)
        return {"status": "success", "transaction_id": result.id}
    except PaymentDeclinedError as e:
        # 不要重试永久性失败
        return {"status": "declined", "reason": str(e)}
    except TransientError as e:
        # 指数退避重试
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
```

### 模式 3：使任务不可变

工作者可能在崩溃或超时时重试。设计为安全地重新执行。

```python
@app.task(bind=True)
def process_order(self, order_id: str) -> None:
    """不可变地处理订单。"""
    order = orders_repo.get(order_id)

    # 已处理？提前返回
    if order.status == OrderStatus.COMPLETED:
        logger.info("订单已处理", order_id=order_id)
        return

    # 已在处理中？检查是否应继续
    if order.status == OrderStatus.PROCESSING:
        # 使用不可变键以避免重复收费
        pass

    # 使用不可变键处理
    result = payment_provider.charge(
        amount=order.total,
        idempotency_key=f"order-{order_id}",  # 关键！
    )

    orders_repo.update(order_id, status=OrderStatus.COMPLETED)
```

**不可变策略：**

1. **写前检查**：在操作前验证状态
2. **不可变键**：使用唯一令牌与外部服务
3. **插入更新模式**：`INSERT ... ON CONFLICT UPDATE`
4. **去重窗口**：跟踪 N 小时内已处理的 ID

### 模式 4：任务状态管理

持久化任务状态转换以实现可见性和调试。

```python
class JobRepository:
    """管理任务状态的仓库。"""

    async def create(self, job: Job) -> Job:
        """创建新的任务记录。"""
        await self._db.execute(
            """INSERT INTO jobs (id, status, created_at)
               VALUES ($1, $2, $3)""",
            job.id, job.status.value, job.created_at,
        )
        return job

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        **fields,
    ) -> None:
        """更新任务状态并记录时间戳。"""
        updates = {"status": status.value, **fields}

        if status == JobStatus.RUNNING:
            updates["started_at"] = datetime.utcnow()
        elif status in (JobStatus.SUCCEEDED, JobStatus.FAILED):
            updates["completed_at"] = datetime.utcnow()

        await self._db.execute(
            "UPDATE jobs SET status = $1, ... WHERE id = $2",
            updates, job_id,
        )

        logger.info(
            "任务状态更新",
            job_id=job_id,
            status=status.value,
        )
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md`。当上面的导航摘要不足以满足需求时，请阅读该文件。

## 最佳实践总结

1. **立即返回** - 不要因耗时操作而阻塞请求
2. **持久化任务状态** - 启用状态轮询和调试
3. **使任务不可变** - 任何失败时都安全重试
4. **使用不可变键** - 用于外部服务调用
5. **设置超时** - 软硬限制都要设置
6. **实现死信队列** - 捕获永久性失败的任务
7. **记录状态转换** - 跟踪任务状态变化
8. **适当重试** - 瞬态错误使用指数退避
9. **不要重试永久性失败** - 验证错误、无效凭证
10. **监控队列深度** - 警报队列积压增长
