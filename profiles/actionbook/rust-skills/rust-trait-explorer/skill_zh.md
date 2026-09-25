# Rust 特性探索器

发现特性实现并理解多态设计。

## 使用方法

```
/rust-trait-explorer <特性名|结构体名>
```

**示例：**
- `/rust-trait-explorer Handler` - 查找 Handler 特性的所有实现者
- `/rust-trait-explorer MyStruct` - 查找 MyStruct 实现的所有特性

## LSP 操作

### 跳转到实现

查找特性的所有实现。

```
LSP(
  operation: "goToImplementation",
  filePath: "src/traits.rs",
  line: 10,
  character: 11
)
```

**使用场景：**
- 已知特性名称
- 想查找所有实现者
- 理解多态代码

## 工作流程

### 查找特性实现者

```
用户: "谁实现了 Handler 特性?"
    │
    ▼
[1] 查找特性定义
    LSP(goToDefinition) 或 workspaceSymbol
    │
    ▼
[2] 获取实现
    LSP(goToImplementation)
    │
    ▼
[3] 对每个 impl 获取详情
    LSP(documentSymbol) 用于方法
    │
    ▼
[4] 生成实现映射
```

### 查找类型的特性

```
用户: "MyStruct 实现了哪些特性?"
    │
    ▼
[1] 查找结构体定义
    │
    ▼
[2] 搜索 "impl * for MyStruct"
    Grep 模式匹配
    │
    ▼
[3] 获取每个特性的详情
    │
    ▼
[4] 生成特性列表
```

## 输出格式

### 特性实现者

```
## `Handler` 的实现

**特性定义位置：** src/traits.rs:15

​```rust
pub trait Handler {
    fn handle(&self, request: Request) -> Response;
    fn name(&self) -> &str;
}
​```

### 实现者 (4)

| 类型 | 位置 | 备注 |
|------|------|------|
| AuthHandler | src/handlers/auth.rs:20 | 处理认证 |
| ApiHandler | src/handlers/api.rs:15 | REST API 端点 |
| WebSocketHandler | src/handlers/ws.rs:10 | WebSocket 连接 |
| MockHandler | tests/mocks.rs:5 | 测试模拟 |

### 实现详情

#### AuthHandler
​```rust
impl Handler for AuthHandler {
    fn handle(&self, request: Request) -> Response {
        // 认证逻辑
    }

    fn name(&self) -> &str {
        "auth"
    }
}
​```

#### ApiHandler
​```rust
impl Handler for ApiHandler {
    fn handle(&self, request: Request) -> Response {
        // API 路由逻辑
    }

    fn name(&self) -> &str {
        "api"
    }
}
```
```

### 类型的特性

```
## `User` 实现的特性

**结构体定义位置：** src/models/user.rs:10

### 标准库特性
| 特性 | 派生/手动 | 备注 |
|------|----------|------|
| Debug | #[derive] | 自动生成 |
| Clone | #[derive] | 自动生成 |
| Default | 手动 | 自定义默认值 |
| Display | 手动 | 用户友好输出 |

### Serde 特性
| 特性 | 位置 |
|------|------|
| Serialize | #[derive] |
| Deserialize | #[derive] |

### 项目特性
| 特性 | 位置 | 方法 |
|------|------|------|
| Entity | src/db/entity.rs:30 | id(), created_at() |
| Validatable | src/validation.rs:15 | validate() |

### 实现层次结构

​```
User
├── derive
│   ├── Debug
│   ├── Clone
│   ├── Serialize
│   └── Deserialize
└── impl
    ├── Default (src/models/user.rs:50)
    ├── Display (src/models/user.rs:60)
    ├── Entity (src/models/user.rs:70)
    └── Validatable (src/models/user.rs:85)
​```
```

## 特性层次结构可视化

```
## 特性层次结构

                    ┌─────────────┐
                    │    Error    │ (std)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
      ┌───────▼───────┐ ┌──▼──┐ ┌───────▼───────┐
      │  AppError     │ │ ... │ │  DbError      │
      └───────┬───────┘ └─────┘ └───────┬───────┘
              │                         │
      ┌───────▼───────┐         ┌───────▼───────┐
      │  AuthError     │         │ QueryError    │
      └───────────────┘         └───────────────┘
```

## 分析功能

### 覆盖率检查

```
## 特性实现覆盖率

特性: Handler (3 个必需方法)

| 实现者 | handle() | name() | priority() | 完整 |
|--------|----------|--------|------------|------|
| AuthHandler | ✅ | ✅ | ✅ | 是 |
| ApiHandler | ✅ | ✅ | ❌ default | 是 |
| MockHandler | ✅ | ✅ | ✅ | 是 |
```

### 全局实现

```
## 全局实现

以下全局实现可能适用于您的类型:

| 特性 | 全局实现 | 适用范围 |
|------|----------|----------|
| From<T> | `impl<T> From<T> for T` | 所有类型 |
| Into<U> | `impl<T, U> Into<U> for T where U: From<T>` | 具备 From 的类型 |
| ToString | `impl<T: Display> ToString for T` | 具备 Display 的类型 |
```

## 常见模式

| 用户输入 | 操作 |
|----------|------|
| "谁实现了 X?" | 对特性执行 goToImplementation |
| "Y 实现了哪些特性?" | Grep 搜索 `impl * for Y` |
| "显示特性层次结构" | 递归查找超特性 |
| "X 是否: Send + Sync?" | 检查 std 特性实现 |

## 相关技能

| 场景 | 工具 |
|------|------|
| 跳转到实现 | rust-code-navigator |
| 调用关系 | rust-call-graph |
| 项目结构 | rust-symbol-analyzer |
| 安全重构 | rust-refactor-helper |
