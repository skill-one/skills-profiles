# Rust 异步模式

使用 Tokio 运行时的异步 Rust 编程生产模式，包括任务、通道、流和错误处理。

## 何时使用此技能

- 构建 async Rust 应用程序
- 实现并发网络服务
- 使用 Tokio 进行异步 I/O
- 正确处理异步错误
- 调试异步代码问题
- 优化异步性能

## 核心概念

### 1. 异步执行模型

```
Future (延迟) → poll() → Ready(value) | Pending
                ↑           ↓
              Waker ← 运行时调度
```

### 2. 关键抽象

| 概念    | 目的                                  |
| ------- | ------------------------------------ |
| `Future` | 可能稍后完成的延迟计算               |
| `async fn` | 返回 impl Future 的函数             |
| `await`    | 挂起直到 future 完成               |
| `Task`     | 并发运行的已生成 future             |
| `Runtime`  | 轮询 futures 的执行器               |

## 快速入门

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full"] }
futures = "0.3"
async-trait = "0.1"
anyhow = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
```

```rust
use tokio::time::{sleep, Duration};
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    // 初始化 tracing
    tracing_subscriber::fmt::init();

    // 异步操作
    let result = fetch_data("https://api.example.com").await?;
    println!("Got: {}", result);

    Ok(())
}

async fn fetch_data(url: &str) -> Result<String> {
    // 模拟异步操作
    sleep(Duration::from_millis(100)).await;
    Ok(format!("Data from {}", url))
}
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **使用 `tokio::select!`** - 用于竞态 futures
- **优先使用通道** - 在可能的情况下优于共享状态
- **使用 `JoinSet`** - 用于管理多个任务
- **使用 tracing 仪器化** - 用于调试异步代码
- **处理取消** - 检查 `CancellationToken`

### 不应该做

- **不要阻塞** - 异步中永远不要使用 `std::thread::sleep`
- **不要跨 awaits 持有锁** - 导致死锁
- **不要无限制生成** - 使用信号量进行限制
- **不要忽略错误** - 使用 `?` 或记录进行传播
- **不要忘记 Send 约束** - 对于已生成的 futures
