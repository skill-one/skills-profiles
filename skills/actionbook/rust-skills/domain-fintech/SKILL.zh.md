---
name: domain-fintech
description: 在构建金融科技应用程序时使用。关键词：金融科技，交易，小数，货币，金融，金钱，交易，账簿，支付，汇率，精度，四舍五入，会计，金融，交易系统，货币，支付
---

# 金融科技领域

> **第3层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust影响 |
|-------------|-------------------|------------------|
| 审计追踪 | 不可变记录 | Arc<T>，无修改 |
| 精度 | 无浮点数 | rust_decimal |
| 一致性 | 事务边界 | 明确所有权 |
| 合规性 | 完整日志记录 | 结构化追踪 |
| 可复现性 | 确定性执行 | 无竞态条件 |

---

## 关键约束

### 金融精度

```
规则：禁止使用f64处理货币
原因：浮点数会丢失精度
Rust：使用rust_decimal::Decimal
```

### 审计要求

```
规则：所有事务必须不可变且可追踪
原因：监管合规，争议解决
Rust：使用Arc<T>进行共享，事件溯源模式
```

### 一致性

```
规则：资金不能凭空消失或出现
原因：复式记账原则
Rust：具有验证总额的事务类型
```

---

## 向下追踪 ↓

从约束到设计（第2层）：

```
"需要不可变的事务记录"
    ↓ m09-domain：将模型建模为值对象
    ↓ m01-所有权：使用Arc处理共享不可变数据

"需要精确的小数运算"
    ↓ m05类型驱动：为货币/金额创建新类型
    ↓ rust_decimal：使用Decimal类型

"需要事务边界"
    ↓ m12生命周期：使用RAII管理事务作用域
    ↓ m09-domain：聚合边界
```

---

## 关键库

| 目的 | 库 |
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
| 审计日志 | 可追溯性 | 带有trace ID的结构化日志记录 |
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
| 使用f64 | 精度丢失 | rust_decimal |
| 可变事务 | 审计追踪中断 | 不可变 + 事件 |
| 字符串表示金额 | 无验证 | 验证的新类型 |
| 静默溢出 | 资金消失 | 检查型运算 |

---

## 向第1层追踪

| 约束 | 第2层模式 | 第1层实现 |
|------------|-----------------|------------------------|
| 不可变记录 | 事件溯源 | Arc<T>，Clone |
| 事务作用域 | 聚合 | 所有权子对象 |
| 精度 | 值对象 | rust_decimal新类型 |
| 线程安全共享 | 共享不可变 | Arc（非Rc） |

---

## 相关技能

| 当... | 查看 |
|------|-----|
| 值对象设计 | m09-domain |
| 所有权用于不可变 | m01-所有权 |
| 使用Arc进行共享 | m02资源 |
| 错误处理 | m13-domain-error |
