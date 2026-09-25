# 金融科技领域

> **第 3 层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 审计追踪 | 不可变记录 | Arc<T>，无修改 |
| 精度 | 无浮点数 | rust_decimal |
| 一致性 | 事务边界 | 明确的所有权 |
| 合规性 | 完整日志记录 | 结构化追踪 |
| 可复现性 | 确定性执行 | 无竞态条件 |

---

## 关键约束

### 金融精度

```
规则：永远不要使用 f64 表示金钱
原因：浮点数会丢失精度
Rust：使用 rust_decimal::Decimal
```

### 审计要求

```
规则：所有事务必须是不可变且可追踪的
原因：监管合规，争议解决
Rust：使用 Arc<T> 进行共享，事件溯源模式
```

### 一致性

```
规则：金钱不能消失或出现
原因：复式记账原则
Rust：具有验证总金额的事务类型
```

---

## 向下追踪 ↓

从约束到设计（第 2 层）：

```
"需要不可变的事务记录"
    ↓ m09-domain：将模型建模为值对象
    ↓ m01-所有权：使用 Arc 处理共享不可变数据

"需要精确的小数运算"
    ↓ m05-类型驱动：为货币/金额创建新类型
    ↓ rust_decimal：使用 Decimal 类型

"需要事务边界"
    ↓ m12-生命周期：使用 RAII 管理事务作用域
    ↓ m09-domain：聚合边界
```

---

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| 小数运算 | rust_decimal |
| 日期/时间 | chrono, time |
| UUID | uuid |
| 序列化 | serde |
| 验证 | validator |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| 货币新类型 | 类型安全 | `struct Amount(Decimal);` |
| 事务 | 原子操作 | 事件溯源 |
| 审计日志 | 可追溯性 | 带有 trace ID 的结构化日志记录 |
| 分类账 | 复式记账 | 借/贷余额 |

## 代码模式：货币类型

```rust
use rust_decimal::Decimal;

#[derive(Clone, Debug, PartialEq)]
pub struct Amount {
    value: Decimal,
    currency: Currency,
}

impl Amount {
    pub fn new(value: Decimal, currency: Currency) -> Self {
        Self { value, currency }
    }

    pub fn add(&self, other: &Amount) -> Result<Amount, CurrencyMismatch> {
        if self.currency != other.currency {
            return Err(CurrencyMismatch);
        }
        Ok(Amount::new(self.value + other.value, self.currency))
    }
}
```

---

## 常见错误

| 错误 | 领域违规 | 修复 |
|---------|-----------------|-----|
| 使用 f64 | 精度丢失 | rust_decimal |
| 可变事务 | 审计追踪中断 | 不可变 + 事件 |
| 字符串表示金额 | 无验证 | 验证的新类型 |
| 静默溢出 | 金钱消失 | 检查型算术 |

---

## 向第 1 层追踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 不可变记录 | 事件溯源 | Arc<T>，Clone |
| 事务作用域 | 聚合 | 所有权子对象 |
| 精度 | 值对象 | rust_decimal 新类型 |
| 线程安全共享 | 共享不可变 | Arc（非 Rc） |

---

## 相关技能

| 当... | 查看 |
|------|-----|
| 值对象设计 | m09-domain |
| 所有权用于不可变 | m01-所有权 |
| 使用 Arc 进行共享 | m02-资源 |
| 错误处理 | m13-domain-error |
