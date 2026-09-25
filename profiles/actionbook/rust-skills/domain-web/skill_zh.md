# Web 域

> **第 3 层：域约束**

## 域约束 → 设计影响

| 域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 无状态 HTTP | 无请求局部全局变量 | 提取器中的状态 |
| 并发 | 处理多个连接 | 异步，Send + Sync |
| 延迟 SLA | 快速响应 | 高效的所有权 |
| 安全性 | 输入验证 | 类型安全的提取器 |
| 可观察性 | 请求跟踪 | tracing + tower 层 |

---

## 关键约束

### 默认异步

```
规则：Web 处理器不得阻塞
原因：阻塞一个任务 = 阻塞多个请求
Rust：async/await，spawn_blocking 用于 CPU 工作
```

### 状态管理

```
规则：共享状态必须是线程安全的
原因：处理器可能在任何线程上运行
Rust：Arc<T>，Arc<RwLock<T>> 用于可变状态
```

### 请求生命周期

```
规则：资源仅存在于请求持续时间
原因：内存管理，无泄漏
Rust：提取器，正确的所有权
```

---

## 向下跟踪 ↓

从约束到设计（第 2 层）：

```
"需要共享应用状态"
    ↓ m07-并发：使用 Arc 进行线程安全共享
    ↓ m02-资源：Arc<RwLock<T>> 用于可变状态

"需要请求验证"
    ↓ m05-类型驱动：验证提取器
    ↓ m06-错误处理：IntoResponse 用于错误

"需要中间件栈"
    ↓ m12-生命周期：Tower 层
    ↓ m04-零成本：基于 trait 的组合
```

---

## 框架比较

| 框架 | 风格 | 适合 |
|-----------|-------|----------|
| axum | 函数式，tower | 现代 API |
| actix-web | 基于演员 | 高性能 |
| warp | 过滤器组合 | 可组合 API |
| rocket | 宏驱动 | 快速开发 |

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| HTTP 服务器 | axum, actix-web |
| HTTP 客户端 | reqwest |
| JSON | serde_json |
| 认证/JWT | jsonwebtoken |
| 会话 | tower-sessions |
| 数据库 | sqlx, diesel |
| 中间件 | tower |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| 提取器 | 请求解析 | `State(db)`，`Json(payload)` |
| 错误响应 | 统一错误 | `impl IntoResponse` |
| 中间件 | 跨切面 | Tower 层 |
| 共享状态 | 应用配置 | `Arc<AppState>` |

## 代码模式：Axum 处理器

```rust
async fn handler(
    State(db): State<Arc<DbPool>>,
    Json(payload): Json<CreateUser>,
) -> Result<Json<User>, AppError> {
    let user = db.create_user(&payload).await?;
    Ok(Json(user))
}

// 错误处理
impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            Self::NotFound => (StatusCode::NOT_FOUND, "Not found"),
            Self::Internal(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Internal error"),
        };
        (status, Json(json!({"error": message}))).into_response()
    }
}
```

---

## 常见错误

| 错误 | 域违规 | 修复 |
|---------|-----------------|-----|
| 处理器中阻塞 | 延迟峰值 | spawn_blocking |
| 状态中使用 Rc | 不是 Send + Sync | 使用 Arc |
| 无验证 | 安全风险 | 类型安全的提取器 |
| 无错误响应 | 差体验 | IntoResponse impl |

---

## 向第 1 层跟踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 异步处理器 | 异步/await | tokio 运行时 |
| 线程安全状态 | 共享状态 | Arc<T>，Arc<RwLock<T>> |
| 请求生命周期 | 提取器 | 通过 From<Request> 的所有权 |
| 中间件 | Tower 层 | 基于 trait 的组合 |

---

## 相关技能

| 当 | 查看 |
|------|-----|
| 异步模式 | m07-并发 |
| 状态管理 | m02-资源 |
| 错误处理 | m06-错误处理 |
| 中间件设计 | m12-生命周期 |
