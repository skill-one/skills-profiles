# 架构模式

掌握成熟的 Backend 架构模式，包括 Clean Architecture、Hexagonal Architecture 和 Domain-Driven Design，以构建可维护、可测试和可扩展的系统。

**输入：** 需要架构的服务边界或模块。
**输出：** 具有清晰依赖规则、接口定义和测试边界的分层结构。

## 何时使用此技能

- 从零开始设计新的 Backend 服务或微服务
- 重构业务逻辑与 ORM 模型或 HTTP 相关性纠缠在一起的单体应用程序
- 在将系统拆分为服务之前建立限界上下文
- 调试依赖循环，其中基础设施代码渗透到领域层
- 创建可测试的代码库，其中用例测试不需要运行数据库
- 实现领域驱动设计战术模式（聚合、值对象、领域事件）

## 核心概念

### 1. Clean Architecture (Uncle Bob)

**层（依赖向内流动）：**

- **实体 (Entities)**：核心业务模型，不包含框架导入
- **用例 (Use Cases)**：应用业务规则，协调实体
- **接口适配器 (Interface Adapters)**：控制器、呈现器、网关——在用例和外部格式之间进行转换
- **框架与驱动 (Frameworks & Drivers)**：UI、数据库、外部服务——所有这些都位于最外层

**关键原则：**

- 依赖仅指向内部；内部层不知道外部层
- 业务逻辑独立于框架、数据库和交付机制
- 每个层边界都通过抽象接口进行跨越
- 无需 UI、数据库或外部服务即可进行测试

### 2. Hexagonal Architecture (Ports and Adapters)

**组件：**

- **领域核心 (Domain Core)**：业务逻辑位于此处，无框架
- **端口 (Ports)**：定义领域核心如何与外部世界交互的抽象接口（驱动和被驱动）
- **适配器 (Adapters)**：端口的实现（PostgreSQL 适配器、Stripe 适配器、REST 适配器）

**优点：**

- 无需触碰核心即可更换实现（例如，用 DynamoDB 替换 PostgreSQL）
- 在测试中使用内存适配器——无需 Docker
- 技术决策推迟到边缘

### 3. Domain-Driven Design (DDD)

**战略模式：**

- **限界上下文 (Bounded Contexts)**：为单个子域隔离一个连贯的模型；避免在整个系统中共享单个模型
- **上下文映射 (Context Mapping)**：定义上下文如何关联（反腐败层、共享内核、开放主机服务）
- **通用语言 (Ubiquitous Language)**：代码中的每个术语都与领域专家使用的术语匹配

**战术模式：**

- **实体 (Entities)**：具有稳定身份随时间变化的对象
- **值对象 (Value Objects)**：不可变对象通过其属性进行识别（Email、Money、Address）
- **聚合 (Aggregates)**：一致性边界；仅根可以外部访问
- **仓库 (Repositories)**：持久化和重新构建聚合；抽象存储机制
- **领域事件 (Domain Events)**：捕获领域内部发生的事情；用于跨聚合协调

## 详细模式和示例

详细模式文档位于 `references/details.md`。当导航层不足以提供信息时，请阅读该文件。

## 测试 — 内存适配器

正确应用 Clean Architecture 的标志是每个用例都可以在没有真实数据库、没有 Docker 和没有网络的情况下通过纯单元测试：

```python
# tests/unit/test_create_user.py
import asyncio
from typing import Dict, Optional
from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository
from use_cases.create_user import CreateUserUseCase, CreateUserRequest


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._store: Dict[str, User] = {}

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._store.values() if u.email == email), None)

    async def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def delete(self, user_id: str) -> bool:
        return self._store.pop(user_id, None) is not None


async def test_create_user_succeeds():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))

    assert response.success
    assert response.user.email == "alice@example.com"
    assert response.user.id is not None


async def test_duplicate_email_rejected():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))
    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice2"))

    assert not response.success
    assert "already exists" in response.error
```

## 故障排除

### 用例测试需要运行数据库

业务逻辑已经渗透到基础设施层。将所有数据库调用通过 `IRepository` 接口进行封装，并在测试中注入内存实现（参见上述测试部分）。用例构造函数必须接受抽象端口，而不是具体类。

### 层之间的循环导入

一个常见症状是 `ImportError: cannot import name X` 在 `use_cases` 和 `adapters` 之间。这发生在用例导入具体适配器类而不是抽象端口时。强制执行规则：`use_cases/` 仅从 `domain/`（实体和接口）导入。它绝不能从 `adapters/` 或 `infrastructure/` 导入。

### 框架装饰器出现在领域实体中

如果 SQLAlchemy `Column()` 或 Pydantic `Field()` 注解出现在领域实体上，则该实体不再纯净。在 `adapters/repositories/` 中创建一个单独的 ORM 模型，并在仓库的 `_to_entity()` 方法中将映射到/从领域实体。

### 所有逻辑最终都出现在控制器中

当控制器超出 HTTP 解析和响应格式化时，将逻辑提取到用例类中。控制器方法应仅做三件事：解析请求、调用用例、映射响应。

### 值对象在太晚时引发错误

在 `__post_init__`（Python）或构造函数中验证不变性，以便无法构建无效的 `Email` 或 `Money`。这将在边界处暴露不良数据，而不是在业务逻辑深处。

### 上下文跨限界上下文泄露

如果 `Order` 上下文从 `Identity` 上下文导入 `User` 实体，则引入反腐败层。`Order` 上下文应持有自己的轻量级 `CustomerId` 值对象，并且仅通过显式接口调用 `Identity` 上下文。

## 高级模式

有关详细的 DDD 限界上下文映射、完整的多服务项目树、反腐败层实现和洋葱架构比较，请参阅：

- [`references/advanced-patterns.md`](references/advanced-patterns.md)

## 相关技能

- `microservices-patterns` — 在将单体拆分为服务时应用这些架构模式
- `cqrs-implementation` — 使用 Clean Architecture 作为 CQRS 命令/查询分离的结构基础
- `saga-orchestration` — Saga 需要定义良好的聚合边界，而 DDD 战术模式提供这些
- `event-store-design` — 聚合产生的领域事件直接输入事件存储
