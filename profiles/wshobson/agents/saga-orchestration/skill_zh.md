# Saga 编排

管理分布式事务和长时间运行的业务流程的模式，无需两阶段提交。

## 输入和输出

**你提供的内容：**
- 服务边界和所有权（哪个服务拥有哪个步骤）
- 事务要求（哪些步骤必须是原子的，哪些可以是最终一致的）
- 每个步骤的失败模式（暂时性 vs. 永久性，重试策略）
- 每个步骤的 SLA 要求（指导超时配置）
- 现有的事件/消息基础设施（Kafka、RabbitMQ、SQS 等）

**此技能生成的结果：**
- 带有序列步骤、动作命令和补偿命令的 Saga 定义
- 为你选择的模式编排的协调器或编排实现
- 每个参与服务的事务补偿逻辑（幂等性，始终成功）
- 步骤超时配置，带每步骤截止日期
- 监控设置：状态机指标、卡顿 Saga 检测、DLQ 恢复

---

## 使用此技能的场景

- 无需分布式锁协调多服务事务
- 实现部分失败的补偿事务
- 管理长时间运行的业务工作流（分钟到小时）
- 处理分布式系统中需要原子性的失败
- 构建订单履行、审批或预订流程
- 用异步补偿替换脆弱的两阶段提交

---

## 详细部分：核心概念

已移至 `references/details.md`。

## 详细部分：模板

已移至 `references/details.md`。

## 最佳实践

### 应做事项

- **确保每一步都是幂等的** — 命令可能在代理重新连接时被重放
- **仔细设计补偿逻辑** — 它是至关重要的代码路径
- **使用关联 ID** — `saga_id` 必须通过每个事件和日志
- **实现每步骤超时** — 不要无限期等待参与者回复
- **记录状态转换** — 每次变更时记录 `saga_id`、`step_name`、`old_state → new_state`
- **明确测试补偿路径** — 在集成测试中在每个步骤索引处注入失败

### 不应做事项

- **不要假设立即完成** — Saga 是异步的，可能需要几分钟
- **不要跳过补偿测试** — 回滚路径是最难正确实现的
- **不要直接耦合服务** — 使用异步消息，Saga 步骤内绝不能同步调用
- **不要忽略部分失败** — 部分执行的步骤仍需要补偿
- **不要使用全局超时** — 每个步骤具有不同的延迟特性

---

## 故障排除

### Saga 卡在 COMPENSATING 状态

Saga 进入补偿但从未达到 FAILED。这意味着补偿处理程序抛出未处理的异常，并且从未发布 `SagaCompensationCompleted`。向补偿消费者添加死信队列 (DLQ) 处理，并确保每个补偿操作在底层操作已回滚时发布结果事件。

```python
async def handle_release_reservation(self, command: Dict):
    try:
        await self.release_reservation(command["original_result"]["reservation_id"])
    except ReservationNotFoundError:
        pass  # 已释放 — 视为成功
    # 无论结果如何，始终发布完成
    await self.event_publisher.publish("SagaCompensationCompleted", {
        "saga_id": command["saga_id"],
        "step_name": "reserve_inventory"
    })
```

### 重启时重复执行 Saga

如果你的协调器服务在 Saga 中间重启，它可能会重放事件并重新执行已完成的步骤。为每个步骤操作添加幂等性键 — 见上述 **模板 3**。

### 基于编排的 Saga 丢失事件

在基于编排的 Saga 中，如果下游服务在发布时离线，可能会错过事件。使用持久消息代理（Kafka 带复制、RabbitMQ 带持久性）并将当前 Saga 状态存储在专用的 `saga_log` 表中，以便可以从最后一个已知良好的步骤重放。

### 超时在慢但有效的步骤完成前触发

像 `create_shipment` 这样的步骤在高峰负载期间可能需要长达 15 分钟，但你的全局超时是 5 分钟，导致虚假补偿。使步骤超时可按步骤类型配置 — 见 `references/advanced-patterns.md` 中的 `TimeoutSagaOrchestrator` 实现和 `STEP_TIMEOUTS` 字典模式。

### 补偿顺序与执行顺序不匹配

当两个步骤都在检测到失败前完成时，补偿必须在严格的逆序运行，否则会留下不一致的数据状态。验证 `_compensate()` 是否从 `current_step - 1` 遍历到 `0`，并添加一个集成测试，故意在每个步骤索引处失败以确认正确的回滚顺序。

---

## 高级模式

`references/` 目录包含大多数 Saga 不需要的生产级实现：

- **`references/advanced-patterns.md`** — 完整的 `SagaOrchestrator` 抽象基类、带每步骤截止日期的 `TimeoutSagaOrchestrator`、详细的银行转账补偿事务链、Prometheus 仪器、卡顿 Saga PromQL 警报和 DLQ 恢复工作程序。

---

## 相关技能

- `cqrs-implementation` — 与 CQRS 配合使用，在每步骤完成后更新读模型
- `event-store-design` — 将 Saga 事件存储在事件存储中，以实现完整审计跟踪和重放能力
- `workflow-orchestration-patterns` — 基于 Saga 概念构建的高级工作流引擎（Temporal、Conductor）
