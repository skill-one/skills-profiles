# 云原生领域

> **第 3 层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 12-Factor | 从环境获取配置 | 基于环境的配置 |
| 可观察性 | 指标 + 跟踪 | tracing + opentelemetry |
| 健康检查 | 活性/就绪检查 | 专用端点 |
| 平稳关闭 | 清洁终止 | 信号处理 |
| 水平扩展 | 无状态设计 | 无本地状态 |
| 容器友好 | 小二进制文件 | 发布优化 |

---

## 关键约束

### 无状态设计

```
规则：无本地持久状态
原因：Pod 可以随时被杀死/重新调度
Rust：外部状态（Redis、DB），无 static mut
```

### 平稳关闭

```
规则：处理 SIGTERM，关闭连接
原因：零停机部署
Rust：tokio::signal + 平稳关闭
```

### 可观察性

```
规则：每个请求都必须可跟踪
原因：调试分布式系统
Rust：tracing spans，opentelemetry 导出
```

---

## 向下跟踪 ↓

从约束到设计（第 2 层）：

```
"需要分布式跟踪"
    ↓ m12-lifecycle：Span 生命周期
    ↓ tracing + opentelemetry

"需要平稳关闭"
    ↓ m07-concurrency：信号处理
    ↓ m12-lifecycle：连接关闭

"需要健康检查"
    ↓ domain-web：HTTP 端点
    ↓ m06-error-handling：健康状态
```

---

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| gRPC | tonic |
| Kubernetes | kube, kube-runtime |
| Docker | bollard |
| 跟踪 | tracing, opentelemetry |
| 指标 | prometheus, metrics |
| 配置 | config, figment |
| 健康 | HTTP 端点 |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| gRPC 服务 | 服务网格 | tonic + tower |
| K8s Operator | 自定义资源 | kube-runtime Controller |
| 可观察性 | 调试 | tracing + OTEL |
| 健康检查 | 编排 | `/health`，`/ready` |
| 配置 | 12-factor | 环境变量 + 密钥 |

## 代码模式：平稳关闭

```rust
use tokio::signal;

async fn run_server() -> anyhow::Result<()> {
    let app = Router::new()
        .route("/health", get(health))
        .route("/ready", get(ready));

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    Ok(())
}

async fn shutdown_signal() {
    signal::ctrl_c().await.expect("failed to listen for ctrl+c");
    tracing::info!("shutdown signal received");
}
```

## 健康检查模式

```rust
async fn health() -> StatusCode {
    StatusCode::OK
}

async fn ready(State(db): State<Arc<DbPool>>) -> StatusCode {
    match db.ping().await {
        Ok(_) => StatusCode::OK,
        Err(_) => StatusCode::SERVICE_UNAVAILABLE,
    }
}
```

---

## 常见错误

| 错误 | 领域违规 | 修复 |
|---------|-----------------|-----|
| 本地文件状态 | 非无状态 | 外部存储 |
| 无 SIGTERM 处理 | 强制杀死 | 平稳关闭 |
| 无跟踪 | 无法调试 | tracing spans |
| 静态配置 | 非 12-factor | 环境变量 |

---

## 向第 1 层跟踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 无状态 | 外部状态 | Arc<Client> 用于外部 |
| 平稳关闭 | 信号处理 | tokio::signal |
| 跟踪 | Span 生命周期 | tracing + OTEL |
| 健康检查 | HTTP 端点 | 专用路由 |

---

## 相关技能

| 当 | 查看 |
|------|-----|
| 异步模式 | m07-concurrency |
| HTTP 端点 | domain-web |
| 错误处理 | m13-domain-error |
| 资源生命周期 | m12-lifecycle |
