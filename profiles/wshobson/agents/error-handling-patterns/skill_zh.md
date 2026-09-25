# 错误处理模式

通过构建具有强大错误处理策略的应用程序，以优雅地处理故障并提供出色的调试体验，从而构建具有弹性的应用程序。

## 何时使用此技能

- 在新功能中实现错误处理
- 设计具有弹性的 API
- 调试生产问题
- 提高应用程序的可靠性
- 为用户和开发者创建更好的错误消息
- 实现重试和断路器模式
- 处理异步/并发错误
- 构建容错分布式系统

## 核心概念

### 1. 错误处理哲学

**异常与结果类型：**

- **异常**：传统的 try-catch，中断控制流
- **结果类型**：显式的成功/失败，函数式方法
- **错误代码**：C 风格，需要纪律性
- **选项/可能类型**：用于可空值

**何时使用每种方法：**

- 异常：意外错误，异常条件
- 结果类型：预期错误，验证失败
- 恐慌/崩溃：不可恢复的错误，编程错误

### 2. 错误类别

**可恢复错误：**

- 网络超时
- 缺失文件
- 无效用户输入
- API 速率限制

**不可恢复错误：**

- 内存不足
- 栈溢出
- 编程错误（空指针等）

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **快速失败**：早期验证输入，快速失败
2. **保留上下文**：包含堆栈跟踪、元数据、时间戳
3. **有意义的消息**：解释发生了什么以及如何修复
4. **适当记录**：错误 = 记录，预期失败 = 不要滥用日志
5. **在正确的级别处理**：在可以有意义处理的地方捕获
6. **清理资源**：使用 try-finally、上下文管理器、defer
7. **不要吞下错误**：记录或重新抛出，不要无声忽略
8. **类型安全的错误**：在可能的情况下使用类型化的错误

```python
# 良好的错误处理示例
def process_order(order_id: str) -> Order:
    """使用全面的错误处理处理订单。"""
    try:
        # 验证输入
        if not order_id:
            raise ValidationError("需要订单 ID")

        # 获取订单
        order = db.get_order(order_id)
        if not order:
            raise NotFoundError("订单", order_id)

        # 处理支付
        try:
            payment_result = payment_service.charge(order.total)
        except PaymentServiceError as e:
            # 记录并包装外部服务错误
            logger.error(f"订单 {order_id} 支付失败：{e}")
            raise ExternalServiceError(
                f"支付处理失败",
                service="payment_service",
                details={"order_id": order_id, "amount": order.total}
            ) from e

        # 更新订单
        order.status = "completed"
        order.payment_id = payment_result.id
        db.save(order)

        return order

    except ApplicationError:
        # 重新抛出已知的应用程序错误
        raise
    except Exception as e:
        # 记录意外错误
        logger.exception(f"处理订单 {order_id} 时发生意外错误")
        raise ApplicationError(
            "订单处理失败",
            code="INTERNAL_ERROR"
        ) from e
```

## 常见陷阱

- **过于宽泛的捕获**：`except Exception` 隐藏了错误
- **空的捕获块**：无声地吞下错误
- **记录和重新抛出**：创建重复的日志条目
- **未清理**：忘记关闭文件、连接
- **糟糕的错误消息**："发生错误" 没有帮助
- **返回错误代码**：使用异常或 Result 类型
- **忽略异步错误**：未处理的 Promise 拒绝
