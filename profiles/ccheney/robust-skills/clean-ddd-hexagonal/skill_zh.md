# 清洁架构、领域驱动设计（DDD）和六边形架构

使用这些相关的模式来解决具体的领域或依赖问题。这是一种主观的综合，而不是强制性的文件夹布局。用户的明确指示优先于此技能的指南。

## 选择范围

从请求的行为、现有的领域模型和当前的依赖关系开始。除非改变它们是任务的一部分，否则保留项目的语言和架构。简单的 CRUD 可以保持简单；团队规模、实体数量和文件长度并不决定 DDD 是否适用。

| 设计问题 | 相关模式 |
|---|---|
| 哪种语言和一致性规则描述了业务？ | DDD、限界上下文、聚合 |
| 源依赖关系应该指向哪个方向？ | 清洁/洋葱架构 |
| 应用程序如何使用不同的接口或基础设施？ | 六边形端口和适配器 |
| 读取和写入是否需要不同的模型？ | CQRS |
| 必须从事件历史中重建状态吗？ | 事件溯源 |

如果一个业务不变式是未知的，识别具体的缺失规则并继续不依赖于它的工作。不要编造业务行为或要求发现工作坊进行本地修复。

## 保留重要的边界

- 保持领域行为独立于 HTTP、持久化和消息实现。将编排放在应用用例中，将外部 I/O 放在适配器中。
- 将实体身份与值对象相等性分开建模。根据事务不变式和争用选择聚合边界。
- 优先选择包含在聚合内的事务。当需求需要跨聚合的原子性时，明确进行这种权衡，而不是默默地用最终一致性替换它。
- 当提交的数据库更改和外部事件投递必须一起可靠时，使用 outbox。
- 将 CQRS、事件溯源、仓库接口和单独的表示文件夹视为由任务证明的选择。根据项目调整示例命名和目录。

提供请求的模型、补丁或评审，并包含受影响的边界和解释它们的权衡。在适当的级别验证更改的不变式和适配器契约；架构问题不需要实现每个模式。

## 参考文献

加载正在做出的决策的参考，而不是整个集合。

| 任务 | 参考 |
|---|---|
| 层级放置、依赖方向、组合根 | [LAYERS.md](references/LAYERS.md) |
| 限界上下文、通用语言、上下文映射 | [DDD-STRATEGIC.md](references/DDD-STRATEGIC.md) |
| 实体、值对象、聚合、仓库 | [DDD-TACTICAL.md](references/DDD-TACTICAL.md) |
| 端口、驱动/被驱动适配器、替代布局 | [HEXAGONAL.md](references/HEXAGONAL.md) |
| CQRS、事件、outbox、sagas、事件溯源 | [CQRS-EVENTS.md](references/CQRS-EVENTS.md) |
| 领域、集成或架构测试设计 | [TESTING.md](references/TESTING.md) |
| 紧凑模式和放置查找 | [CHEATSHEET.md](references/CHEATSHEET.md) |

主要基础：[DDD](https://www.domainlanguage.com/ddd/blue-book/)、[六边形架构](https://alistair.cockburn.us/hexagonal-architecture/) 和 [清洁架构](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)。
