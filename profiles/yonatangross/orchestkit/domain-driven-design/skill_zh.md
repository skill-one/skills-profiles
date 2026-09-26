# 领域驱动设计战术模式

使用实体、值对象和限界上下文对复杂业务领域进行建模。

## 概述

- 建模复杂的业务逻辑
- 将领域与基础设施分离
- 在子域之间建立清晰的边界
- 使用行为构建丰富的领域模型
- 在代码中实现通用语言

## 构建块概述

```
┌─────────────────────────────────────────────────────────────┐
│                    DDD构建块                               │
├─────────────────────────────────────────────────────────────┤
│  实体           值对象          聚合根         │
│  Order (有ID)   Money (无ID)    [Order]→Items  │
│                                                              │
│  领域服务       仓库           领域事件        │
│  PricingService IOrderRepository OrderSubmitted            │
│                                                              │
│  工厂           规范           模块           │
│  OrderFactory OverdueOrderSpec orders/, payments/          │
└─────────────────────────────────────────────────────────────┘
```

## 快速参考

### 实体（具有身份）

```python
from dataclasses import dataclass, field
from uuid import UUID
from uuid_utils import uuid7

@dataclass
class Order:
    """实体：具有身份、可变状态、生命周期。"""
    id: UUID = field(default_factory=uuid7)
    customer_id: UUID = field(default=None)
    status: str = "draft"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id  # 基于身份的相等性

    def __hash__(self) -> int:
        return hash(self.id)
```

ID生成是一个约定俗成，而不是主观选择：`Read("references/ork-delta.md")`。

### 值对象（不可变）

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # 必须是frozen的！
class Money:
    """值对象：由属性定义，而不是身份。"""
    amount: Decimal
    currency: str

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("不能添加不同货币")
        return Money(self.amount + other.amount, self.currency)
```

规范地址/日期范围样板代码在此不再重述。请参阅下方的上游覆盖表。

## 关键决策

| 决策 | 建议 |
|------|------|
| 实体与VO | 有唯一ID+生命周期？实体。否则VO |
| 实体相等性 | 基于ID，而不是属性 |
| 值对象可变性 | 始终不可变（`frozen=True`） |
| 仓库范围 | 每个聚合根一个 |
| 领域事件 | 在实体中收集，持久化后发布 |
| 上下文边界 | 基于业务能力，而不是技术 |

## 规则快速参考

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| aggregate-boundaries (load `rules/aggregate-boundaries.md`) | 高 | 聚合根设计、通过ID引用、每事务一个 |
| aggregate-invariants (load `rules/aggregate-invariants.md`) | 高 | 业务规则执行、规范模式 |
| aggregate-sizing (load `rules/aggregate-sizing.md`) | 高 | 合适的大小、何时拆分、最终一致性 |

## 不应使用的情况

实体少于5个？完全跳过DDD。仪式成本高于收益。

| 模式 | 面试 | 简报 | MVP | 成长 | 企业 | 更简单的替代方案 |
|------|------|------|-----|------|------|------------------|
| 聚合根 | 过度 | 过度 | 过度 | 选择性 | 适当 | 带验证的普通dataclass |
| 限界上下文 | 过度 | 过度 | 过度 | 边缘 | 适当 | 清晰导入的Python包 |
| CQRS | 过度 | 过度 | 过度 | 过度 | 合理时 | 读写使用单个模型 |
| 值对象 | 过度 | 过度 | 边缘 | 适当 | 必需 | 实体上的类型字段 |
| 领域事件 | 过度 | 过度 | 过度 | 选择性 | 适当 | 服务之间直接方法调用 |
| 仓库模式 | 过度 | 过度 | 边缘 | 适当 | 必需 | 服务层直接ORM查询 |

**经验法则：** DDD会增加约40%的代码开销。只有当领域复杂性确实需要时才值得（5个以上实体且不变式跨越多个对象）。使用DDD的CRUD应用是一个警示信号。

## 反模式（禁止）

```python
# 永远不要有贫血的领域模型（只有数据的类）
@dataclass
class Order:
    id: UUID
    items: list  # 错误 - 没有行为！

# 永远不要将基础设施泄漏到领域
class Order:
    def save(self, session: Session):  # 错误 - 知道数据库！

# 永远不要使用可变的值对象
@dataclass  # 错误 - 缺少frozen=True
class Money:
    amount: Decimal

# 永远不要让仓库返回ORM模型
async def get(self, id: UUID) -> OrderModel:  # 错误 - 返回领域！
```

## 上游覆盖（不再重述）

这些主题是第一方编写的。请直接阅读源代码，而不是在此重新推导；仅保留房屋后果，在`references/ork-delta.md`中。

| 主题 | 源 |
|------|----|
| 实体/值对象dataclass机制：`frozen`、`__post_init__`、继承字段排序、`kw_only` | https://docs.python.org/3/library/dataclasses.html |
| 领域事件定义、延迟派发、处理器连接、提交前与提交后派发 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation |
| 限界上下文、上下文映射、ACL、子域、通用语言、集成模式（共享内核、客户-供应商、一致性、开放主机服务、发布语言） | https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis |
| 反腐败层：它转换什么以及它成本什么 | https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer |
| UUIDv7生成、服务器端和Python中 | https://www.postgresql.org/docs/18/functions-uuid.html 和 https://github.com/aminalaee/uuid-utils |
| 零售金额在最小单位、零小数货币 | https://docs.stripe.com/currencies |
| 发布事件到Redis流（`XADD`字段映射、管道） | https://redis.io/docs/latest/commands/xadd/ |
| 分层架构执行、项目结构验证、测试标准 | 此插件中的`architecture-patterns`技能 |

有两个主题故意保留在此技能中，而不是路由到上游：仓库和单元工作实现，它完全存在于`references/repositories.md`中，以及聚合边界、不变式和大小，它完全存在于`rules/`中。

## 相关技能

- `rules/aggregate-boundaries.md`、`rules/aggregate-invariants.md`、`rules/aggregate-sizing.md` - 聚合设计，在此技能中
- `ork:architecture-patterns` - 分层边界和项目结构验证
- `ork:distributed-systems` - 跨聚合协调
- `ork:database-patterns` - DDD的架构设计

## 参考文献

使用`Read("references/<file>")`按需加载：
| 文件 | 内容 |
|------|------|
| `ork-delta.md` | 房屋规则：UUIDv7、事件排空顺序、ACL边界、源布局 |
| `repositories.md` | 仓库模式、单元工作、SQLAlchemy映射 |

## 能力详情

### 实体
**关键词：** 实体、身份、生命周期、可变、领域对象
**解决：** 通过ID的相等性，以及`references/ork-delta.md`中的房屋UUIDv7 ID规则。dataclass机制路由到上游。

### 值对象
**关键词：** 值对象、不可变、frozen、dataclass、结构化相等性
**解决：** 何时使用VO而不是实体。`frozen=True`语义和继承字段排序路由到上游。

### 领域服务
**关键词：** 领域服务、业务逻辑、跨聚合、无状态
**解决：** 何时使用领域服务，跨越聚合的逻辑

### 仓库
**关键词：** 仓库、持久化、集合、IRepository、协议
**解决：** 实现仓库模式，抽象数据库访问，ORM映射

### 限界上下文
**关键词：** 限界上下文、上下文映射、ACL、子域、通用语言
**解决：** 房屋ACL边界和`references/ork-delta.md`中的上下文优先源布局。上下文映射和集成模式路由到上游。
