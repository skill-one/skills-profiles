# 领域建模

> **第 2 层：设计选择**

## 核心问题

**这个概念在领域中扮演什么角色？**

在用代码建模之前，先理解：
- 它是实体（身份重要）还是值对象（可互换）？
- 必须维护哪些不变式？
- 聚合的边界在哪里？

---

## 领域概念 → Rust 模式

| 领域概念 | Rust 模式 | 所有权暗示 |
|----------|-----------|-----------|
| 实体 | struct + Id | 拥有，唯一身份 |
| 值对象 | struct + Clone/Copy | 可共享，不可变 |
| 聚合根 | struct 拥有子项 | 明确所有权树 |
| 仓库 | trait | 抽象持久化 |
| 领域事件 | enum | 捕获状态变化 |
| 服务 | impl block / free fn | 状态无关的操作 |

---

## 思考提示

在创建领域类型之前：

1. **这个概念的标识是什么？**
   - 需要唯一标识 → 实体（Id 字段）
   - 可按值互换 → 值对象（Clone/Copy）

2. **必须保持哪些不变式？**
   - 始终有效 → 私有字段 + 验证构造器
   - 转变规则 → 类型状态模式

3. **谁拥有这些数据？**
   - 单一所有者（父项）→ 拥有字段
   - 共享引用 → Arc/Rc
   - 弱引用 → Weak

---

## 向上追溯 ↑

到领域约束（第 3 层）：

```
"如何建模交易？"
    ↑ 询问：哪些领域规则管理交易？
    ↑ 检查：domain-fintech（审计，精度要求）
    ↑ 检查：业务利益相关者（哪些不变式？）
```

| 设计问题 | 追溯到 | 询问 |
|----------|--------|------|
| 实体与值对象 | domain-* | 什么让两个实例“相同”？ |
| 聚合边界 | domain-* | 什么必须一起保持一致性？ |
| 验证规则 | domain-* | 应用哪些业务规则？ |

---

## 向下追溯 ↓

到实现（第 1 层）：

```
"作为实体建模"
    ↓ m01-ownership：拥有，唯一
    ↓ m05-type-driven：Id 用 Newtype

"作为值对象建模"
    ↓ m01-ownership：Clone/Copy 可以
    ↓ m05-type-driven：在构造时验证

"作为聚合建模"
    ↓ m01-ownership：父项拥有子项
    ↓ m02-resource：考虑 Rc 用于聚合内共享
```

---

## 快速参考

| DDD 概念 | Rust 模式 | 示例 |
|----------|-----------|------|
| 值对象 | Newtype | `struct Email(String);` |
| 实体 | 结构 + ID | `struct User { id: UserId, ... }` |
| 聚合 | 模块边界 | `mod order { ... }` |
| 仓库 | Trait | `trait UserRepo { fn find(...) }` |
| 领域事件 | Enum | `enum OrderEvent { Created, ... }` |

## 模式模板

### 值对象

```rust
struct Email(String);

impl Email {
    pub fn new(s: &str) -> Result<Self, ValidationError> {
        validate_email(s)?;
        Ok(Self(s.to_string()))
    }
}
```

### 实体

```rust
struct UserId(Uuid);

struct User {
    id: UserId,
    email: Email,
    // ... 其他字段
}

impl PartialEq for User {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id  // 身份等价
    }
}
```

### 聚合

```rust
mod order {
    pub struct Order {
        id: OrderId,
        items: Vec<OrderItem>,  // 拥有子项
        // ...
    }

    impl Order {
        pub fn add_item(&mut self, item: OrderItem) {
            // 强制聚合不变式
        }
    }
}
```

---

## 常见错误

| 错误 | 为什么不对 | 更好的做法 |
|------|------------|-----------|
| 原始类型痴迷 | 没有类型安全 | Newtype 包装器 |
| 带不变式的公共字段 | 不变式被违反 | 私有 + 访问器 |
| 泄露聚合内部 | 封装被破坏 | 根上的方法 |
| 用字符串表示语义类型 | 没有验证 | 验证的 Newtype |

---

## 相关技能

| 当... | 看到 |
|------|------|
| 类型驱动实现 | m05-type-driven |
| 聚合所有权 | m01-ownership |
| 领域错误处理 | m13-domain-error |
| 特定领域规则 | domain-* |
