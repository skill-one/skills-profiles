---
name: m13-domain-error
description: 在设计领域错误处理时使用。关键词：领域错误，错误分类，恢复策略，重试，后备，领域错误层次结构，面向用户与内部错误，错误代码设计，断路器，优雅降级，弹性，错误上下文，退避，带退避的重试，错误恢复，暂时性错误与永久性错误，领域错误，错误分类，恢复策略，重试，熔断器，优雅降级
---

# 域错误策略

> **第 2 层：设计选择**

## 核心问题

**谁需要处理这个错误，以及他们应该如何恢复？**

在设计错误类型之前：
- 这是面向用户还是内部使用？
- 是否可以恢复？
- 调试需要哪些上下文？

---

## 错误分类

| 错误类型 | 目标受众 | 恢复方式 | 示例 |
|----------|----------|----------|------|
| 面向用户 | 最终用户 | 指导操作 | `InvalidEmail`, `NotFound` |
| 内部使用 | 开发者 | 调试信息 | `DatabaseError`, `ParseError` |
| 系统 | 运维/SRE | 监控/告警 | `ConnectionTimeout`, `RateLimited` |
| 瞬时性 | 自动化 | 重试 | `NetworkError`, `ServiceUnavailable` |
| 永久性 | 人工处理 | 调查 | `ConfigInvalid`, `DataCorrupted` |

---

## 思考提示

在设计错误类型之前：

1. **谁会看到这个错误？**
   - 最终用户 → 友好的消息，可操作
   - 开发者 → 详细信息，可调试
   - 运维 → 结构化，可告警

2. **我们可以恢复吗？**
   - 瞬时性 → 带退避的重试
   - 可降级 → 备用值
   - 永久性 → 快速失败，告警

3. **需要哪些上下文？**
   - 调用链 → `anyhow::Context`
   - 请求 ID → 结构化日志
   - 输入数据 → 错误负载

---

## 向上追溯 ↑

到域约束（第 3 层）：

```
"如何处理支付失败？"
    ↑ 询问：重试的业务规则是什么？
    ↑ 检查：`domain-fintech`（交易要求）
    ↑ 检查：SLA（可用性要求）
```

| 问题 | 追溯到 | 询问 |
|------|--------|------|
| 重试策略 | `domain-*` | 重试的可接受延迟是多少？ |
| 用户体验 | `domain-*` | 用户应该看到什么消息？ |
| 合规性 | `domain-*` | 审计必须记录哪些内容？ |

---

## 向下追溯 ↓

到实现（第 1 层）：

```
"需要类型化的错误"
    ↓ `m06-error-handling`：`thiserror` 用于库
    ↓ `m04-zero-cost`：错误枚举设计

"需要错误上下文"
    ↓ `m06-error-handling`：`anyhow::Context`
    ↓ 日志：带字段的跟踪

"需要重试逻辑"
    ↓ `m07-concurrency`：异步重试模式
    ↓ Crate：`tokio-retry`, `backoff`
```

---

## 快速参考

| 恢复模式 | 适用场景 | 实现 |
|----------|----------|------|
| 重试 | 瞬时性失败 | 指数退避 |
| 备用 | 降级模式 | 缓存/默认值 |
| 电路断路器 | 级联失败 | `failsafe-rs` |
| 超时 | 慢操作 | `tokio::time::timeout` |
| 隔离舱 | 隔离问题 | 独立线程池 |

## 错误层级

```rust
#[derive(thiserror::Error, Debug)]
pub enum AppError {
    // 面向用户
    #[error("无效输入: {0}")]
    Validation(String),

    // 瞬时性（可重试）
    #[error("服务暂时不可用")]
    ServiceUnavailable(#[source] reqwest::Error),

    // 内部使用（记录详情，显示通用消息）
    #[error("内部错误")]
    Internal(#[source] anyhow::Error),
}

impl AppError {
    pub fn is_retryable(&self) -> bool {
        matches!(self, Self::ServiceUnavailable(_))
    }
}
```

## 重试模式

```rust
use tokio_retry::{Retry, strategy::ExponentialBackoff};

async fn with_retry<F, T, E>(f: F) -> Result<T, E>
where
    F: Fn() -> impl Future<Output = Result<T, E>>,
    E: std::fmt::Debug,
{
    let strategy = ExponentialBackoff::from_millis(100)
        .max_delay(Duration::from_secs(10))
        .take(5);

    Retry::spawn(strategy, || f()).await
}
```

---

## 常见错误

| 错误 | 为什么不对 | 更好的做法 |
|------|------------|-----------|
| 所有错误使用同一个类型 | 没有可操作性 | 按受众分类 |
| 对所有错误都重试 | 浪费资源 | 仅对瞬时错误重试 |
| 无限重试 | 可能导致自身宕机 | 最大尝试次数 + 退避 |
| 暴露内部错误 | 安全风险 | 用户友好消息 |
| 没有上下文 | 难以调试 | 处处使用 `.context()` |

---

## 反模式

| 反模式 | 为什么不好 | 更好的做法 |
|--------|------------|-----------|
| 字符串错误 | 没有结构 | `thiserror` 类型 |
| 使用 `panic!` 处理可恢复的错误 | 用户体验差 | 带上下文的 `Result` |
| 忽略错误 | 沉默失败 | 记录或传播 |
| 处处使用 `Box<dyn Error>` | 失去类型信息 | `thiserror` |
| 在正常路径中处理错误 | 性能问题 | 早期验证 |

---

## 相关技能

| 适用场景 | 相关内容 |
|----------|----------|
| 错误处理基础 | `m06-error-handling` |
| 重试实现 | `m07-concurrency` |
| 域建模 | `m09-domain` |
| 面向用户的 API | `domain-*` |
