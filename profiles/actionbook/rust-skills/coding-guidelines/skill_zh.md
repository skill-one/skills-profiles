# Rust 编码规范（50条核心规则）

## 命名（Rust 特有）

| 规则 | 指导方针 |
|------|-----------|
| 无 `get_` 前缀 | `fn name()` 而不是 `fn get_name()` |
| 迭代器惯例 | `iter()` / `iter_mut()` / `into_iter()` |
| 转换命名 | `as_` (廉价借用), `to_` (昂贵转换), `into_` (所有权转移) |
| 静态变量前缀 | `G_CONFIG` 用于 `static`，`const` 无需前缀 |

## 数据类型

| 规则 | 指导方针 |
|------|-----------|
| 使用新类型 | `struct Email(String)` 用于领域语义 |
| 优先使用切片模式 | `if let [first, .., last] = slice` |
| 预分配 | `Vec::with_capacity()`, `String::with_capacity()` |
| 避免滥用 Vec | 对于固定大小使用数组 |

## 字符串

| 规则 | 指导方针 |
|------|-----------|
| 优先使用字节 | `s.bytes()` 而不是 `s.chars()` 当是 ASCII 时 |
| 使用 `Cow<str>` | 当可能修改借用数据时 |
| 使用 `format!` | 而不是使用 `+` 进行字符串连接 |
| 避免嵌套迭代 | 字符串上的 `contains()` 是 O(n*m) |

## 错误处理

| 规则 | 指导方针 |
|------|-----------|
| 使用 `?` 传播 | 而不是 `try!()` 宏 |
| `expect()` 而不是 `unwrap()` | 当值被保证存在时 |
| 断言不变式 | 在函数入口处使用 `assert!` |

## 内存

| 规则 | 指导方针 |
|------|-----------|
| 有意义的生命周期 | `'src`, `'ctx` 而不是仅仅 `'a` |
| 使用 `try_borrow()` for RefCell | 避免恐慌 |
| 使用遮蔽进行转换 | `let x = x.parse()?` |

## 并发

| 规则 | 指导方针 |
|------|-----------|
| 识别锁顺序 | 防止死锁 |
| 原子操作用于基本类型 | 而不是使用 Mutex for bool/usize |
| 小心选择内存顺序 | Relaxed/Acquire/Release/SeqCst |

## 异步

| 规则 | 指导方针 |
|------|-----------|
| CPU 密集型使用同步 | 异步用于 I/O |
| 不要在 `await` 跨越持有锁 | 使用作用域守卫 |

## 宏

| 规则 | 指导方针 |
|------|-----------|
| 非必要避免使用 | 优先使用函数/泛型 |
| 遵循 Rust 语法 | 宏输入应该像 Rust 代码 |

## 已弃用 → 更好

| 已弃用 | 更好 | 自版本 |
|------------|--------|-------|
| `lazy_static!` | `std::sync::OnceLock` | 1.70 |
| `once_cell::Lazy` | `std::sync::LazyLock` | 1.80 |
| `std::sync::mpsc` | `crossbeam::channel` | - |
| `std::sync::Mutex` | `parking_lot::Mutex` | - |
| `failure`/`error-chain` | `thiserror`/`anyhow` | - |
| `try!()` | `?` 操作符 | 2018 |

## 快速参考

```
命名: snake_case (函数/变量), CamelCase (类型), SCREAMING_CASE (常量)
格式化: rustfmt (直接使用)
文档: /// 用于公共项, //! 用于模块文档
Lint: #![warn(clippy::all)]
```

Claude 对 Rust 惯例非常了解。这些是非明显的 Rust 特有规则。
