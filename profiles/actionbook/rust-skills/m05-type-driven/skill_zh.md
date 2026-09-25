# 驱动类型的设计

> **第一层：语言机制**

## 核心问题

**类型系统如何防止无效状态？**

在寻求运行时检查之前：
- 编译器能否捕获此错误？
- 无效状态是否无法表示？
- 类型能否编码不变式？

---

## 错误 → 设计问题

| 模式 | 不要只说 | 而是问 |
|------|----------|--------|
| 原始类型痴迷 | "它只是一个字符串" | 这个值代表什么？ |
| 布尔标志 | "添加一个is_valid标志" | 状态能否是类型？ |
| 处处可选 | "检查None" | 真的有可能缺失吗？ |
| 运行时验证 | "如果无效则返回Err" | 我们能否在构造时验证？ |

---

## 思考提示

在添加运行时验证之前：

1. **类型能否编码约束？**
   - 数字范围 → 有界类型或新类型
   - 有效状态 → 类型状态模式
   - 语义含义 → 新类型

2. **何时可以进行验证？**
   - 在构造时 → 验证新类型
   - 在状态转换时 → 类型状态
   - 仅在运行时 → 带清晰错误的Result

3. **谁需要知道不变式？**
   - 编译器 → 类型级别编码
   - API用户 → 清晰的类型签名
   - 仅在运行时 → 文档说明

---

## 向上追溯 ↑

当类型设计不明确时：

```
"需要验证电子邮件格式"
    ↑ 问：这是一个领域值对象吗？
    ↑ 检查：m09-domain (电子邮件作为值对象)
    ↑ 检查：domain-* (验证要求)
```

| 情况 | 追溯到 | 问题 |
|------|--------|------|
| 创建什么类型 | m09-domain | 领域模型是什么？ |
| 状态机设计 | m09-domain | 有效转换是什么？ |
| 标记特征使用 | m04-zero-cost | 静态还是动态派发？ |

---

## 向下追溯 ↓

从设计到实现：

```
"需要原始类型的类型安全包装器"
    ↓ 新类型：struct UserId(u64);

"需要编译时状态验证"
    ↓ 类型状态：Connection<Connected>

"需要跟踪虚类型参数"
    ↓ PhantomData：PhantomData<T>

"需要能力标记"
    ↓ 标记特征：trait Validated {}

"需要渐进式构造"
    ↓ 构建器：Builder::new().field(x).build()
```

---

## 快速参考

| 模式 | 目的 | 示例 |
|------|------|------|
| 新类型 | 类型安全 | `struct UserId(u64);` |
| 类型状态 | 状态机 | `Connection<Connected>` |
| PhantomData | 变异/生命周期 | `PhantomData<&'a T>` |
| 标记特征 | 能力标志 | `trait Validated {}` |
| 构建器 | 渐进式构造 | `Builder::new().name("x").build()` |
| 封闭特征 | 防止外部实现 | `mod private { pub trait Sealed {} }` |

## 模式示例

### 新类型

```rust
struct Email(String);  // 不仅仅是任何字符串

impl Email {
    pub fn new(s: &str) -> Result<Self, ValidationError> {
        // 验证一次，永远信任
        validate_email(s)?;
        Ok(Self(s.to_string()))
    }
}
```

### 类型状态

```rust
struct Connection<State>(TcpStream, PhantomData<State>);

struct Disconnected;
struct Connected;
struct Authenticated;

impl Connection<Disconnected> {
    fn connect(self) -> Connection<Connected> { ... }
}

impl Connection<Connected> {
    fn authenticate(self) -> Connection<Authenticated> { ... }
}
```

---

## 决策指南

| 需要 | 模式 |
|------|------|
| 原始类型的类型安全 | Newtype |
| 编译时状态验证 | Type State |
| 生命周期/变异标记 | PhantomData |
| 能力标志 | Marker Trait |
| 渐进式构造 | Builder |
| 封闭的实现集 | Sealed Trait |
| 零大小类型标记 | ZST struct |

---

## 反模式

| 反模式 | 为什么不好 | 更好的方式 |
|--------|------------|-----------|
| 用于状态的布尔标志 | 运行时错误 | 类型状态 |
| 用于语义类型的字符串 | 没有类型安全 | 新类型 |
| 用于未初始化的Option | 不明确的不变式 | 构建器 |
| 带不变式的公共字段 | 不变式违例 | 私有 + 验证new() |

---

## 相关技能

| 当... | 查看 |
|------|------|
| 领域建模 | m09-domain |
| 特征设计 | m04-zero-cost |
| 构造器中的错误处理 | m06-error-handling |
| 反模式 | m15-anti-pattern |
